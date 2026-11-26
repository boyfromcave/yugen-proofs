"""Revision 7 of the calculator (2026-11-19): the NIST security category as a first-class input.

What this module adds (soundness/CHANGELOG.md, revision 7; docs/soundness-method.md section 8.7):

  * REVISION 9: every row of both systems is solved under the counting convention EVERY t (Profile.convention, default
    EVERY_T; see the block "revision 9" below and docs/decision-qrom-counting.md); the book need of revisions 1 to 8
    is available only as T_GE_KQ, whose rows are labelled NON_DEFAULT and never certified. System B's candidates are
    the refereed m = 10 rows of dkt26 (finding R8-8b), not a search over m.

  * The category (1 to 5) is an input. Its requirements are DERIVED here from the text of NIST's call for
    proposals (`NIST`, below), not typed in: the classical bits kappa_C, the QROM bits kappa_Q, the attack bits
    of condition G, the digest length of condition H, and from them the per-round need of a tree of
    MAX_TREE_PROOFS = 20,000 proofs (the union bound of soundness-method.md 8.5b).
  * The digest length, the proof and leaf salt lengths, the challenge field and the proof-internal tree hash are
    inputs (`Profile`). The calculator REFUSES (hard failures, as condition Q already is) a profile whose field is
    too small for the category's algebraic rounds (`FieldTooSmall`), whose digest is shorter than condition H's
    attack rule or too short for the QROM hash term of Sharp-Grubbs Theorem 6.6 (2) (`DigestTooShort`,
    spbcs.ConditionQFailure), whose tree hash claims less collision security than the category or outputs fewer
    bits than the digest (`HashNotAdmissible`), or whose leaf salt is not longer than the digest, a hypothesis of
    Theorem 6.6 (3) (`SaltNotCovered`).
  * Certified rows for both systems at any category (unique decoding, proven bounds, no grinding, true rates,
    spBCS constants): system A's masked leaf rows (row 6, the standalone masked row; row 8, the masked row of a
    tree; mode 0 and mode 1 statements at the stacks the admission rule gives) and node row 9 at every stack
    2^24 to 2^30 and rates 1/2 and 1/4; system B's leaf and node rows at rates 1/8 and 1/16. System B's
    list-decoding rows are CANDIDATE rows only, conditional on DKT26; never certified.
  * The proof-size model per row (opening bytes by digest and salt length; anchored on measured proofs), the
    minimum challenge field per system and category, QROM bits by digest length, zero-knowledge errors by salt.

Source of the category definitions (read 2026-11-19 from the lead architect's copy, call-for-proposals-final-dec-
2016.pdf): NIST, "Submission Requirements and Evaluation Criteria for the Post-Quantum Cryptography Standardization
Process" (December 2016) [NIST-CfP], Section 4.A.5 "Security Strength Categories", pages 15 to 19: the five
requirements (page 16 items 1 to 3, page 17 items 4 and 5), the metrics paragraph and MAXDEPTH (page 17: "Plausible
values for MAXDEPTH range from 2^40 ... through 2^64 ... to no more than 2^96 logical gates"), and the table of
classical and quantum gate counts (page 18), footnotes 4 to 6. FIPS 205 Section 11 (Table 2 and the paragraph
after it) restates the category of each SLH-DSA parameter set and cites the same call.

Provenance: the NIST figures are Published (NIST-CfP 4.A.5, used as is). The conversion of each category into
the conditions C, Q, G, H (the conventions of `derive_target`) and the tree accounting are Original (the Ycash
developers, 2026), REFERENCES.md O-13 and O-38. The bounds the rows are certified under are those of revision 6
(book Theorems 25.2.1 and 31.2.1; BCIKS20 unique decoding; Theorem S0; Sharp and Grubbs, ePrint 2026/2615,
Theorem 6.6 (2) to (4)); the rows themselves are Original (the Ycash developers, 2026), REFERENCES.md O-34.
Every size is an estimate (E) of the model, anchored on the measured proofs named beside the anchors (M).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from . import binius64, current as cu, hashterm as ht, johnson, revision5 as r5, spbcs, whir, wi
from .compose import FsParams, Round
from .shipping import OTHER_ROUNDS, ProofTreeTarget, tree_target
from .targets import SecurityTarget, _digest_proven

PROOFS = 20_000  # MAX_TREE_PROOFS, specification section 2 (SPEC-109)
PROOF_BYTES_MAX = cu.PROOF_LIMIT  # 1.75 MiB = 1,835,008 B, every proof (design basis 2a, decision 5; W1)
POOL_LOG2 = 20.0  # proofs in the pool for the zero-knowledge figure (zk-quantum.md 3.3)
WITNESS_BITS_LOG2 = 24.0  # L of Theorem 6.6 (4) (revision 6)
C1_LOG2 = math.log2(6.0)  # SG26 Theorem 6.6 (2): 6 (t + k_q)^2 eps_k

# --- the NIST text ------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class NistCategory:
    """One security requirement of NIST-CfP 4.A.5, with the gate counts of its reference attack (page 18)."""

    number: int
    reference: str  # the reference primitive as NIST names it
    kind: str  # "key search" (block cipher) or "collision search" (hash function)
    reference_bits: int  # key length, or hash output length
    classical_gates_log2: int  # log2 of NIST's classical gate count for the optimal attack (page 18)
    quantum_gates_maxdepth_log2: int | None  # log2(quantum gates x MAXDEPTH) (page 18); None: no figure given

    @property
    def quote(self) -> str:
        target = (f"key search on a block cipher with a {self.reference_bits}-bit key" if self.kind == "key search"
                  else f"collision search on a {self.reference_bits}-bit hash function")
        return ("Any attack that breaks the relevant security definition must require computational resources "
                f"comparable to or greater than those required for {target} (e.g. {self.reference})")


NIST: dict[int, NistCategory] = {
    1: NistCategory(1, "AES128", "key search", 128, 143, 170),
    2: NistCategory(2, "SHA256/ SHA3-256", "collision search", 256, 146, None),
    3: NistCategory(3, "AES192", "key search", 192, 207, 233),
    4: NistCategory(4, "SHA384/ SHA3-384", "collision search", 384, 210, None),
    5: NistCategory(5, "AES 256", "key search", 256, 272, 298),
}
MAXDEPTH_LOG2 = (40, 64, 96)  # NIST-CfP page 17
SHA3_512_CLASSICAL_GATES_LOG2 = 274  # page 18, the table's last line (no category is defined by it)


def kappa_classical(cat: int) -> float:
    """Condition C's classical bits, in hash-oracle calls (convention C, Original).

    The reference attack's count of reference evaluations: 2^k keys for key search on a k-bit key (the
    attack the gate count prices), 2^(n/2) evaluations for generic collision search on an n-bit hash. NIST
    prices those evaluations in gates: classical_gates_log2 - kappa is 15, 18, 15, 18 and 16 bits for
    categories 1 to 5 (`gates_per_evaluation_log2`). The calculator counts oracle calls, not gates; requiring
    kappa oracle calls equals NIST's gate figure whenever one oracle call costs at least as many gates as one
    evaluation of the reference primitive. A Keccak-f[1600] call is SHA3's core, so by NIST's own figures (18
    bits for a SHA3-256 evaluation against 15 to 16 for AES) the convention is conservative by 2 to 3 bits for
    system A's oracle; for SHA-2 and BLAKE3 compressions the gate count is not in the reference folder (to be
    verified; conservative in the same way if one compression costs at least one AES evaluation)."""
    n = NIST[cat]
    return float(n.reference_bits if n.kind == "key search" else n.reference_bits // 2)


def kappa_quantum(cat: int) -> float:
    """Condition Q's proven QROM bits (convention Q, Original): half of kappa_C. What it proves: the tree's
    QROM bound reaches 1/2 at 2^kappa_Q quantum queries. NIST's quantum budget at categories 3 and 5
    (2^233 / MAXDEPTH and 2^298 / MAXDEPTH gates, at least 2^137 and 2^202 gates) allows more parallel queries
    than that, where the proven bound is vacuous; there the category's quantum half rests on condition G, an
    attack estimate (referee report 3.3, correction F-3). At category 1 with a large MAXDEPTH the bound covers
    the budget.

    A proven QROM bound covers adversaries of any depth. With no depth limit, Grover's search finds a k-bit
    key in about 2^(k/2) sequential evaluations (Zalka's optimality, NIST-CfP footnote 6), so a QROM bound of
    k/2 bits (success at most t / 2^(k/2) for t quantum queries) is the AES-k equivalent at unlimited depth;
    NIST's MAXDEPTH (at most 2^96 gates) only makes the attacker weaker. For the collision categories NIST
    gives no quantum figure; the same halving is applied (a conservative choice of ours)."""
    return kappa_classical(cat) / 2.0


def gates_per_evaluation_log2(cat: int) -> float:
    """log2 of the gates NIST's classical figure implies for one evaluation of the reference primitive."""
    return NIST[cat].classical_gates_log2 - kappa_classical(cat)


def grover_overhead_log2(cat: int) -> float | None:
    """log2 of the (depth x size) product of one reference evaluation that NIST's quantum figure implies:
    2^k x (D x S) / MAXDEPTH gates for parallel Grover under a depth limit (NIST-CfP footnotes 4 and 6; Grassl et
    al. not read). Condition G (attack bits = kappa_C a round) equals NIST's figure at every MAXDEPTH when one
    oracle call's quantum circuit has depth x size at least this. That premise is an ASSUMPTION, unverified
    (referee report security-category-referee.md 1, correction 5; it replaces the AND-count comparison of
    soundness-method.md 8.2)."""
    q = NIST[cat].quantum_gates_maxdepth_log2
    return None if q is None else q - kappa_classical(cat)


def derive_target(cat: int) -> SecurityTarget:
    """The category as the calculator's four conditions (Original, the Ycash developers, 2026):
      C  proven classical bits kappa_C (`kappa_classical`);
      Q  proven QROM bits kappa_Q = kappa_C / 2 (`kappa_quantum`);
      G  attack bits a round = kappa_C (parallel Grover under MAXDEPTH costs 2^e / D oracle calls, as AES key
         search over 2^e keys costs 2^e / D AES calls; Zalka, NIST-CfP footnote 6);
      H  digests of 2 kappa_C bits (attack rule: generic collision search on the digest costs 2^kappa_C calls;
         NIST orders collision search on 256- and 384-bit hashes above key search on 128- and 192-bit keys,
         NIST-CfP page 16 footnote 2, and lists SHA3-384 and SHA3-512 collisions at 2^210 and 2^274 classical
         gates, above AES192's 2^207 and AES 256's 2^272, page 18; NIST precedent: FIPS 204 Section 4 Table 1 sets
         the "collision strength of c~" to 128 / 192 / 256 for ML-DSA's categories 2 / 3 / 5, and Appendix D.1
         records that a 384-bit SHAKE256 output made a category-5 parameter set "only meet category 4"). NIST
         prices collisions in classical gates only (the realistic model); under the BHT model (2^(n/3) queries
         with free quantum memory) the rule would need 576 bits at category 3 (referee report 1, correction 3):
         not used. The proven rule's digest is reported beside it.
    Categories 2 and 4 give the same kappa_C as 1 and 3 in oracle calls, so the same rows."""
    kc = kappa_classical(cat)
    return SecurityTarget(name=f"cat{cat}", nist_category=cat, classical_chain=kc, quantum_chain=kc / 2,
                          attack_bits=kc, digest_attack=int(2 * kc), digest_proven=_digest_proven(kc))


def tree_target_for(cat: int, proofs: int = PROOFS) -> ProofTreeTarget:
    """The per-round need of a tree of `proofs` proofs (union bound, soundness-method.md 8.5b; Original):
    e >= kappa_C + 1 + log2 N + log2(1 + k), k = listed rounds + OTHER_ROUNDS; and Q, G."""
    return tree_target(derive_target(cat), OTHER_ROUNDS, proofs)


def round_need(cat: int, k: int, proofs: int = PROOFS) -> float:
    """Closed form of the book's condition C (NON-DEFAULT since revision 9): kappa_C + 1 + log2 N + log2(1 + k)."""
    return kappa_classical(cat) + 1.0 + math.log2(proofs) + math.log2(1 + k)


# --- revision 9: the counting convention (docs/decision-qrom-counting.md) -------------------------------------
#
# Sharp, Grubbs, ePrint 2026/2615 [SG26], Theorem 6.6 (2) (page 58) bounds the extraction error eps_ex(t) and
# eps^C_ex(t) = (t + k_q)(eps_k + c' (t + k_q) / 2^(8b)) as functions of t, and Definitions H.3 and H.4 (pages 128,
# 129) quantify "for every t and every (t, 0)-adversary" ("for every t in N" in H.4); the paragraph after H.3 says
# the definition "bounds the errors at every query bound". Read from the rendered pages on 2026-11-19 (revision 9),
# agreeing with docs/soundness-rev8-referee.md section 7. The lead architect's ruling (2026-11-19): EVERY t is the
# calculator's only default convention. In the calculator's convention eps(t) <= t / 2^(kappa + 1) for every
# 1 <= t <= 2^kappa (t = 0 is bounded by t = 1: an adversary may always make one more query), the binding t is 1 and a
# round of a proof with k_q verifier hash queries (SG26 Definition I.1) needs, in a tree of N proofs,
#     e >= kappa_C + 1 + log2 N + log2(1 + k_q)                               (EVERY_T, default)
# instead of the book's kappa_C + 1 + log2 N + log2(1 + k), k the rounds (T_GE_KQ, the revision 1 to 8 counts,
# justified for spBCS only by reading condition C for adversaries making at least k_q hash queries: kept behind an
# explicit option, every row printed under it is labelled NON_DEFAULT and never certified). k_q grows with the query
# count, so every row is solved to its least fixed point. Provenance: the bound and the quantifier Published [SG26];
# the per-row fixed point and the tree accounting Original (the Ycash developers, 2026), REFERENCES.md O-13, O-68.

EVERY_T = "every-t"
T_GE_KQ = "t-ge-kq"
CONVENTIONS = (EVERY_T, T_GE_KQ)
NON_DEFAULT = "non-default convention (t >= k_q), not certified"


def check_convention(convention: str) -> str:
    if convention not in CONVENTIONS:
        raise ValueError(f"unknown counting convention {convention!r}; one of {CONVENTIONS}")
    return convention


def every_t_need(cat: int, k_q: int, proofs: int = PROOFS) -> float:
    """Per-round need under EVERY_T: max(C, Q, G) with C = kappa_C + 1 + log2 N + log2(1 + k_q) (SG26 Theorem 6.6 (2),
    ROM part, at t = 1, summed over N proofs), Q = 2 kappa_Q + 1 + log2 6 + log2 N, G = kappa_C."""
    c = kappa_classical(cat) + 1.0 + math.log2(proofs) + math.log2(1 + k_q)
    q = 2.0 * kappa_quantum(cat) + 1.0 + C1_LOG2 + math.log2(proofs)
    return max(c, q, kappa_classical(cat))


@dataclass(frozen=True)
class EveryTTarget(ProofTreeTarget):
    """A tree target whose classical term uses the proof's k_q in place of its rounds (EVERY_T)."""

    k_q: int = 0

    def _cq(self, rounds_count: int, fs: FsParams) -> tuple[float, float]:
        m = math.log2(self.proofs * self.attempts)
        return (self.classical_chain + m + 1.0 + math.log2(1 + self.k_q),
                2.0 * self.quantum_chain + 1.0 + fs.qrom_c1_log2 + m)


def every_t_target(cat: int, k_q: int, proofs: int = PROOFS) -> EveryTTarget:
    b = tree_target_for(cat, proofs)
    return EveryTTarget(name=f"{b.name}-every-t", nist_category=b.nist_category, classical_chain=b.classical_chain,
                        quantum_chain=b.quantum_chain, attack_bits=b.attack_bits, digest_attack=b.digest_attack,
                        digest_proven=b.digest_proven, layers=b.layers, proofs=proofs, attempts=1.0, model="union",
                        other_rounds=b.other_rounds, k_q=k_q)


# --- profiles: digest, salts, field, tree hash ---------------------------------------------------------------


@dataclass(frozen=True)
class TreeHash:
    name: str
    output_bits: int
    collision_bits: int  # the collision security the hash's designers or standard claim
    source: str


TREE_HASHES = {h.name: h for h in (
    TreeHash("Keccak-256", 256, 128, "generic n/2 (from memory; FIPS 202 not in the reference folder)"),
    TreeHash("SHA-256", 256, 128, "generic n/2 (from memory; FIPS 180-4 not in the folder); FIPS 205 Sec. 11.2.2 "
             "replaces it by SHA-512 in its tree functions H and T_l for categories 3 and 5"),
    TreeHash("BLAKE3", 256, 128, "128 bits for every goal and every output length: BLAKE3 specification "
             "(version 20211102173700) Section 4.1 (decision-b-merkle-hash.md H-1.5)"),
    TreeHash("SHA-384", 384, 192, "generic n/2 (from memory; FIPS 180-4 not in the folder)"),
    TreeHash("SHA3-384", 384, 192, "generic n/2, capacity 768 (from memory; FIPS 202 not in the folder)"),
    TreeHash("SHAKE256-384", 384, 192, "min(n/2, c/2 = 256) (from memory; FIPS 202 not in the folder)"),
    TreeHash("SHA-512", 512, 256, "generic n/2 (from memory); FIPS 205 Sec. 11.2.2 uses it for categories 3, 5"),
    TreeHash("SHAKE256-512", 512, 256, "min(n/2, c/2 = 256) (from memory; FIPS 202 not in the folder)"),
)}


@dataclass(frozen=True)
class Profile:
    """The inputs of one parameter set. `privacy_category` sets the hash-query budget t = 2^kappa_Q of the
    zero-knowledge figure (profile M-1: soundness at 3, privacy at 5)."""

    category: int
    digest_bits: int
    proof_salt_bytes: int
    leaf_salt_bytes: int
    field_bits: int
    tree_hash_a: str
    tree_hash_b: str
    privacy_category: int | None = None
    label: str = ""
    convention: str = "every-t"  # revision 9: the QROM/ROM counting convention (EVERY_T default; T_GE_KQ non-default)
    hash_basis: str = "attack-rule"  # revision 10: how the CLASSICAL hash part is judged (hashterm.HASH_BASES)

    @property
    def privacy(self) -> int:
        return self.privacy_category or self.category

    @property
    def digest_bytes(self) -> int:
        return self.digest_bits // 8

    @property
    def name(self) -> str:
        return self.label or f"cat{self.category}"


PROFILES = {
    1: Profile(1, 256, 64, 64, 256, "Keccak-256", "BLAKE3", label="cat1 (as built: D-b salts, SQ-48 BLAKE3)"),
    2: Profile(2, 256, 64, 64, 256, "Keccak-256", "BLAKE3"),
    3: Profile(3, 384, 64, 96, 256, "SHAKE256-384", "SHA-384"),
    4: Profile(4, 384, 64, 96, 256, "SHAKE256-384", "SHA-384"),
    5: Profile(5, 512, 80, 112, 384, "SHAKE256-512", "SHA-512"),
}
# The lead agent's working assumption (decision-security-category.md 6, 7), pending the lead architect's choice:
# category 3 soundness and binding (48-byte digests, the 256-bit field), category 5 privacy (t = 2^128) with the
# category-5 salts.
M1 = Profile(3, 384, 80, 112, 256, "SHAKE256-384", "SHA-384", privacy_category=5, label="M-1 (soundness 3, privacy 5)")
BUILDABLE_FIELDS = (256, 384, 512)  # GF(2^256) built; GF(2^384) cubic over E; GF(2^512) (decision record 3.4)


class CategoryRefusal(ValueError):
    """A profile the calculator refuses for its category (hard failure)."""


class FieldTooSmall(CategoryRefusal):
    pass


class DigestTooShort(CategoryRefusal):
    pass


class HashNotAdmissible(CategoryRefusal):
    pass


class SaltNotCovered(CategoryRefusal):
    pass


class NoAdmittedStack(CategoryRefusal):
    """A masked-leaf shape with no stack at which the hiding layout fits (reported as a refused shape, as
    yugen-proof-a refuses 16 of row 8's 60 shapes at category 1: parameters.md 2.2)."""


def check_profile(p: Profile) -> None:
    """Conditions on the digest and the tree hashes that need no row (H, attack rule; hash admissibility)."""
    t = derive_target(p.category)
    if p.digest_bits < t.digest_attack:
        raise DigestTooShort(f"{p.name}: {p.digest_bits}-bit digests < {t.digest_attack} (condition H, attack rule: "
                             f"collision search on the digest must cost 2^{t.classical_chain:.0f} calls)")
    for sysname, hname in (("A", p.tree_hash_a), ("B", p.tree_hash_b)):
        h = TREE_HASHES[hname]
        if h.collision_bits < t.classical_chain:
            raise HashNotAdmissible(f"{p.name}: system {sysname}'s tree hash {hname} claims {h.collision_bits} bits of "
                                    f"collision security < {t.classical_chain:.0f} ({h.source})")
        if h.output_bits < p.digest_bits:
            raise HashNotAdmissible(f"{p.name}: system {sysname}'s tree hash {hname} outputs {h.output_bits} bits < "
                                    f"the {p.digest_bits}-bit digest")


# --- rows --------------------------------------------------------------------------------------------------------


CERTIFIED = "certified"
FIXED_NEED = "fixed need (passed in), not certified"
NEED_EVERY_T, NEED_BOOK, NEED_FIXED, NEED_UNASSESSED = "every-t", "book", "fixed", "unassessed"
CANDIDATE = ("candidate, rests on DKT26 (Dao, Kominers, Thaler, ePrint 2026/2056), a PREPRINT, and the lemmas of "
             "binius-johnson-row.md; never certified")


@dataclass
class Row:
    system: str
    kind: str  # "leaf" or "node"
    label: str
    stack: int  # log2 committed words (A) or words (B node) / trace (B leaf)
    rate: int  # log2 inverse rate
    queries: tuple[int, ...]
    rounds: int  # listed rounds (A) or challenges (B)
    need: float
    weakest: float  # effective bits of the weakest round
    weakest_name: str
    alg_bits: float  # weakest algebraic round at the field
    alg_name: str
    field_bits: int
    field_min: int  # smallest field (bits) at which every algebraic round meets the need
    size: float  # bytes (E)
    opening: float  # Merkle openings and final codeword, bytes (E)
    route_status: str = ""  # a candidate's label (CANDIDATE ...); "" for a unique-decoding row
    note: str = ""
    extra: dict = field(default_factory=dict)
    # revision 10 (finding R9-2): what the status is COMPUTED from; set by `_stamp`, never a label passed in
    convention: str = EVERY_T
    need_source: str = NEED_UNASSESSED  # NEED_EVERY_T (the row's own k_q), NEED_BOOK (t >= k_q) or NEED_FIXED
    category: int = 1
    digest_bits: int = 256
    hash_basis: str = ht.HASH_ATTACK_RULE
    proofs: int = PROOFS
    kq: ht.KqInput | None = None
    c_prime: int = 0
    c_input: ht.CInput | None = None  # revision 10.1 (R10-6): c' with its provenance

    @property
    def margin(self) -> float:
        return self.weakest - self.need

    @property
    def hash(self) -> ht.HashTerm | None:
        """The hash term of SG26 Theorem 6.6 (2) at this row's c' and k_q (revision 10, finding R9-1)."""
        if self.kq is None or not self.c_prime:
            return None
        return ht.HashTerm(self.c_prime, self.kq.value, self.proofs, self.digest_bits, kappa_classical(self.category),
                           kappa_quantum(self.category))

    @property
    def checks(self) -> dict[str, bool]:
        """Every condition of the label "certified" (revision 10): computed, never passed in; the same function as
        dkt26.Row8.checks (revision 10.1, R10-1)."""
        return certification_checks(convention=self.convention, need_own_kq=self.need_source == NEED_EVERY_T,
                                    unique_decoding=not self.route_status, margin=self.margin, kq=self.kq,
                                    hash_term=self.hash, digest_bits=self.digest_bits, category=self.category,
                                    hash_basis=self.hash_basis)

    @property
    def certified(self) -> bool:
        return all(self.checks.values())

    @property
    def status(self) -> str:
        if self.route_status:
            st = self.route_status
            return f"{NON_DEFAULT}; {st}" if self.convention == T_GE_KQ else st
        if self.convention == T_GE_KQ:
            return NON_DEFAULT
        if self.need_source == NEED_FIXED:
            return FIXED_NEED + ("" if self.margin >= -1e-9 else "; DOES NOT MEET it")
        if self.margin < -1e-9:
            return "DOES NOT MEET the need"
        failing = [k for k, v in self.checks.items() if not v]
        if not failing:
            return CERTIFIED
        if failing == ["k_q guard"]:
            return (f"meets on an estimated k_q by {self.margin:+.4f} bits, under the k_q guard {self.kq.guard:.4f}: "
                    "not certified until task T-1 reports k_q")
        return "not certified: fails " + ", ".join(failing)


def certification_checks(*, convention: str, need_own_kq: bool, unique_decoding: bool, margin: float,
                         kq: ht.KqInput | None, hash_term: ht.HashTerm | None, digest_bits: int, category: int,
                         hash_basis: str) -> dict[str, bool]:
    """The conditions of the label "certified", shared by every row type (category.Row, dkt26.Row8; finding R10-1):
    the every-t convention, the need at the row's own k_q (not passed in, not the book's), unique decoding, the need
    met, the k_q guard, the QROM hash part at kappa_Q, and the classical hash part on the row's basis (condition H's
    attack rule: digest >= 2 kappa_C; proven: the tree's proven classical level >= kappa_C)."""
    if hash_basis not in ht.HASH_BASES:
        raise ValueError(f"hash basis {hash_basis!r}; one of {ht.HASH_BASES}")
    h = hash_term
    hb = digest_bits >= derive_target(category).digest_attack if hash_basis == ht.HASH_ATTACK_RULE \
        else (h is not None and h.classical_margin >= -1e-9)
    return {
        "convention every t": convention == EVERY_T,
        "need at the row's own k_q": need_own_kq,
        "unique decoding (not a candidate)": unique_decoding,
        "meets the need": margin >= -1e-9,
        "k_q guard": kq is not None and margin >= kq.guard - 1e-12,
        "QROM hash part >= kappa_Q": h is not None and h.quantum_margin >= -1e-9,
        f"classical hash part ({hash_basis})": hb,
    }


def certified_label(hash_basis: str) -> str:
    """The positive label, naming the basis it was computed on (R10-1)."""
    return ("certified (every t; classical hash part on condition H's attack rule)" if hash_basis == ht.HASH_ATTACK_RULE
            else "certified (every t; every term proven)")


def _is_query(r: Round) -> bool:
    return r.name.startswith("query") or r.name == "final"


def _alg(rs: list[Round]) -> Round:
    return min((r for r in rs if not _is_query(r)), key=lambda r: r.effective_bits)


def _field_min(rs: list[Round], field_bits: int, need: float) -> int:
    """Smallest field (bits) at which every algebraic round meets `need`: need + log2(largest count n of an
    n / |F| term). Query rounds' t / |F| parts are below 2^-200 and do not bind."""
    worst = max(r.error_log2 + field_bits - 0.0 for r in rs if not _is_query(r))
    return math.ceil(need + worst - 1e-9)


# System A: rows and statements (yugen-proof-a docs/parameters.md 2.2 to 2.4, read 2026-11-19)
A_LEAF_ROWS = (("row 6 (standalone masked)", cu.ROW6, (2,)), ("row 8 (masked in a tree)", r5.ROW8, (2, 1)))
A_MODES = {0: 22, 1: 20}  # trace stacks of the mode-0 and mode-1 wallet statements (parameters.md 2.4, M)
A_STREAM_SCALARS = {("row 6", 0): 6_977, ("row 8", 0): 6_749, ("row 6", 1): 5_021, ("row 8", 1): 4_591}  # 2.4, M
# Measured masked leaves with 64-byte leaf salts, mode 0, rate 1/4 (parameters.md 2.3, M): row 6 at
# 226/157/154/154 (691 opened leaves) 688,180 B; row 8 at 227/161/164/180 (732) 692,504 B.
A_LEAF_ANCHOR = ((226, 157, 154, 154), 688_180)
A_LEAF_CHECK = ((227, 161, 164, 180), 692_504)
# Node: M of 7 S(9) children, 2^27 stack, rate 1/2, row 9 at the list's counts (yugen-proof-a recursion.md 9.10, M)
A_NODE_ANCHOR = 875_309
A_NODE_STACKS = tuple(range(24, 31))
A_NODE_RATES = (1, 2)


def _a_cfg(row: cu.ARow, log_n: int, rate: int, salt: int, p: Profile, queries=None) -> whir.WhirConfig:
    return cu.a_config(row, log_n, rate, salt, queries, field_bits=p.field_bits, digest_bits=p.digest_bits)


def a_leaf_calibration() -> dict:
    """Non-opening bytes of the masked leaf at the 256-bit field: residual = measured - opening model - stream
    scalars x 32 (fitted to row 6's measured proof); the model's error at row 8's measured proof."""
    c = cu.a_config(cu.ROW6, 22, 2, 64, list(A_LEAF_ANCHOR[0]))
    resid = A_LEAF_ANCHOR[1] - wi.size_bytes(c, "A")["total"] - A_STREAM_SCALARS[("row 6", 0)] * 32
    c8 = cu.a_config(r5.ROW8, 22, 2, 64, list(A_LEAF_CHECK[0]))
    model8 = wi.size_bytes(c8, "A")["total"] + A_STREAM_SCALARS[("row 8", 0)] * 32 + resid
    return {"residual": resid, "row 8 error": model8 / A_LEAF_CHECK[1] - 1}


def a_node_calibration() -> float:
    """Non-opening bytes of a node proof at the 256-bit field (fitted to the measured 7 S(9) node)."""
    return A_NODE_ANCHOR - whir.size_bytes(cu.a_config(r5.ROW9, 27, 1, 0))["total"]


def a_leaf_size(c: whir.WhirConfig, rowkey: str, mode: int) -> tuple[float, float]:
    opening = wi.size_bytes(c, "A")["total"]
    return opening + A_STREAM_SCALARS[(rowkey, mode)] * c.ext_bytes + a_leaf_calibration()["residual"], opening


def a_row_counts(c: whir.WhirConfig, rounds: int) -> spbcs.TranscriptCounts:
    """SG26 Definition I.1 quantities for ONE proof of system A (revision 9; as `a_counts`, for one row): N_msg =
    2 (listed rounds + OTHER_ROUNDS), m = 2, q_IOP = the row's opened positions (sum of its query counts, drawn
    queries), l_max = its largest level in positions (cosets). An estimate (E) until the transcript module reports the
    counts (task T-1, docs/decision-qrom-counting.md 7)."""
    l_max = max(c.vars_at(i) - c.folds[i] + c.log_inv_rates[i] for i in range(len(c.folds)))
    return spbcs.TranscriptCounts("A", rounds + OTHER_ROUNDS, rounds + OTHER_ROUNDS, 2, sum(c.queries), l_max,
                                  0.0, 512, 32)


def a_row_kq(c: whir.WhirConfig, rounds: int) -> int:
    return a_row_counts(c, rounds).k_q


A_KQ_SOURCE = "category.a_row_counts (E: N_msg, m, OTHER_ROUNDS; q_IOP and l_max from the shape)"


def a_kq(label: str, stack: int, rate: int, c: whir.WhirConfig, rounds: int) -> ht.KqInput:
    """System A's k_q at config `c` with provenance (revision 10.1, R10-8): a T-1 report for the shape (label, stack,
    rate) is checked against the shape's floor and used at its own counts, or carried as an excess over the estimate
    at other counts; the guard's named errors are 4 OTHER_ROUNDS + q_IOP (R10-7)."""
    est = a_row_kq(c, rounds)
    rep = ht.REPORTED_KQ.get(ht.a_report_key(label, stack, rate))
    est_rep = None
    if rep is not None:
        ht.check_report(rep, rounds, sum(rep.queries), f"system A {label}, 2^{stack}, rate 1/{2 ** rate}")
        import copy

        c2 = copy.deepcopy(c)
        c2.queries = list(rep.queries)
        est_rep = a_row_kq(c2, rounds)
    return ht.resolve_kq(rep, tuple(c.queries), est, est_rep, A_KQ_SOURCE, 4 * OTHER_ROUNDS + sum(c.queries))


def a_c_input(label: str, stack: int, rate: int, c: whir.WhirConfig, rounds: int) -> ht.CInput:
    """System A's c' with provenance (R10-6): reported when a T-1 report for the shape carries N_msg and m (c' does not
    depend on the query counts), else the estimate (E)."""
    rep = ht.REPORTED_KQ.get(ht.a_report_key(label, stack, rate))
    if rep is not None and rep.c_prime is not None:
        return ht.CInput(rep.c_prime, ht.KQ_REPORTED, rep.source)
    return ht.CInput(a_row_counts(c, rounds).c_prime, ht.KQ_ESTIMATED,
                     "N_msg = 2 (listed rounds + OTHER_ROUNDS), m = 2 (E, upper figures)")


def _stamp(r: Row, p: Profile, need_source: str, kq: ht.KqInput | None = None,
           c_input: ht.CInput | None = None) -> Row:
    """Revision 10: record what the row's status is computed from (convention, where its need came from, the
    profile's digest and hash basis, k_q and c' with their provenance). The status is never set by a caller. Revision
    10.1: k_q and c' arrive as inputs with provenance (a_kq, b_kq; R10-6, R10-8); under EVERY_T the need is restated
    at the k_q the row carries."""
    r.convention, r.need_source, r.category = p.convention, need_source, p.category
    r.digest_bits, r.hash_basis = p.digest_bits, p.hash_basis
    if r.system == "A" and "config" in r.extra:
        c = r.extra["config"]
        kq = kq if kq is not None else a_kq(r.label, r.stack, r.rate, c, r.rounds)
        c_input = c_input or a_c_input(r.label, r.stack, r.rate, c, r.rounds)
    if kq is not None:
        r.kq = kq
        r.extra["k_q"] = kq.value
        if need_source == NEED_EVERY_T:
            r.need = every_t_need(p.category, kq.value)
    if c_input is not None:
        r.c_input, r.c_prime = c_input, c_input.value
    return r


def _need(p: Profile, rounds: int, c: whir.WhirConfig) -> float:
    """The need of one system-A proof with config `c` under the profile's convention."""
    if check_convention(p.convention) == EVERY_T:
        return every_t_need(p.category, a_row_kq(c, rounds))
    return tree_target_for(p.category).need_bits(rounds, c.fs)


def _fixed_point(p: Profile, solve_at, book: Row) -> Row:
    """EVERY_T: solve the row against k_q, recompute its own k_q, repeat (starting from the book row, whose k_q is a
    lower bound); a solution is valid when its own k_q is at most the one it was solved at. The valid solution with
    the fewest opened positions is returned, its need restated at its own k_q."""
    def own_kq(r: Row) -> ht.KqInput:
        return a_kq(r.label, r.stack, r.rate, r.extra["config"], r.rounds)

    kq = own_kq(book).value
    seen, best = set(), None
    for _ in range(48):
        if kq in seen:
            break
        seen.add(kq)
        r = solve_at(kq)
        own = own_kq(r)
        if own.value <= kq:
            r.need = every_t_need(p.category, own.value)
            r.extra["k_q"] = own.value
            if r.weakest >= r.need - 1e-9 and (best is None or sum(r.queries) < sum(best.queries)):
                best = r
        kq = own.value
    if best is None:
        raise RuntimeError(f"no fixed point for {book.label}")
    # revision 10.1 (R10-8 (ii)): k_q is the row's own at the chosen counts, a T-1 report included (by shape, not by
    # count), so a report above the estimate RE-SOLVES the row to new counts instead of failing it; the new counts are
    # printed, and the k_q at them is reported only if the report was measured at exactly those counts.
    rep = ht.REPORTED_KQ.get(ht.a_report_key(best.label, best.stack, best.rate))
    if rep is not None and tuple(rep.queries) != tuple(best.queries):
        best.note = ((best.note + "; ") if best.note else "") + (
            f"re-solved at the T-1 report (reported at {tuple(rep.queries)}, k_q {rep.k_q:,})")
    return _stamp(best, p, NEED_EVERY_T, own_kq(best))


def _need_name(t) -> str:
    """Finding R9-5: name the need a refusal compares with. Under EVERY_T the book need (t >= k_q) is solved first, as
    the start of the fixed point; the every-t need is higher, so a refusal at the book need holds a fortiori."""
    if isinstance(t, EveryTTarget):
        return f"every-t need at k_q = {t.k_q:,}"
    return "book need (t >= k_q), solved first; the every-t need is higher, so the refusal holds a fortiori"


def a_leaf(label: str, row: cu.ARow, mode: int, rate: int, p: Profile, max_lift: int = 8) -> Row:
    """The masked leaf (W-I opening, every zero-knowledge round of wi.A_WALLET_ZK) at the least admitted stack at
    or above the mode's trace (the admission rule of parameters.md 2.4, `verifier::zk::admitted_stack_log`); under
    EVERY_T (revision 9) solved to the fixed point of its own k_q."""
    book = _a_leaf_at(label, row, mode, rate, p, tree_target_for(p.category), max_lift)
    if check_convention(p.convention) == T_GE_KQ:
        return _stamp(book, p, NEED_BOOK)
    return _fixed_point(p, lambda kq: _a_leaf_at(label, row, mode, rate, p, every_t_target(p.category, kq), max_lift),
                        book)


def _a_leaf_at(label: str, row: cu.ARow, mode: int, rate: int, p: Profile, t, max_lift: int = 8) -> Row:
    trace = A_MODES[mode]
    rowkey = label.split(" (")[0]
    last = None
    for stack in range(trace, trace + max_lift + 1):
        c = _a_cfg(row, stack, rate, p.leaf_salt_bytes, p, [1] * len(row.schedule(stack, rate)[0]))
        try:
            rs = wi.rounds(c, "A", wi.A_WALLET_ZK)
        except ValueError as e:
            last = str(e)
            continue
        need = t.need_bits(len(rs), c.fs)
        alg = _alg(rs)
        fmin = _field_min(rs, p.field_bits, need)
        if alg.effective_bits < need:
            raise FieldTooSmall(f"{p.name}: system A {label}, mode {mode}, 2^{stack}, rate 1/{2 ** rate}: round {alg.name} "
                                f"gives {alg.effective_bits:.1f} < {need:.2f} bits ({_need_name(t)}) at GF(2^{p.field_bits}); "
                                f"needs {fmin} bits")
        try:
            c = wi.solve(c, "A", t, wi.A_WALLET_ZK)
        except ValueError as e:
            last = str(e)
            continue
        rs = wi.rounds(c, "A", wi.A_WALLET_ZK)
        need = t.need_bits(len(rs), c.fs)
        w = min(rs, key=lambda r: r.effective_bits)
        size, opening = a_leaf_size(c, rowkey, mode)
        return Row("A", "leaf", f"{label}, mode {mode}", stack, rate, tuple(c.queries), len(rs), need, w.effective_bits,
                   w.name, alg.effective_bits, alg.name, p.field_bits, fmin, size, opening,
                   note="" if stack == trace else f"trace 2^{trace}, admitted at 2^{stack}", extra={"config": c})
    raise NoAdmittedStack(f"{p.name}: system A {label}, mode {mode}, rate 1/{2 ** rate}: no admitted stack from 2^{trace} "
                          f"to 2^{trace + max_lift} ({last})")


def a_leaf_counts_meet(row: Row, queries: list[int], p: Profile) -> bool:
    """Whether a leaf row's shape meets its need at `queries` (layout refusals count as failures); under EVERY_T the
    need is taken at the k_q of `queries` (fewer queries: a smaller k_q, a lower need)."""
    rowdef = cu.ROW6 if row.label.startswith("row 6") else r5.ROW8
    c = _a_cfg(rowdef, row.stack, row.rate, p.leaf_salt_bytes, p, list(queries))
    try:
        rs = wi.rounds(c, "A", wi.A_WALLET_ZK)
    except ValueError:
        return False
    return min(r.effective_bits for r in rs) >= _need(p, len(rs), c) - 1e-9


def a_node(log_n: int, rate: int, p: Profile) -> Row:
    """Row 9 (plain WHIR) at the minimal counts that meet the need at the true rates: the rule counts at the need,
    raised until every round meets it, then trimmed (revision5.minimal_counts with the profile's field and digest);
    under EVERY_T (revision 9) solved to the fixed point of its own k_q."""
    book = _a_node_at(log_n, rate, p, tree_target_for(p.category))
    if check_convention(p.convention) == T_GE_KQ:
        return _stamp(book, p, NEED_BOOK)
    return _fixed_point(p, lambda kq: _a_node_at(log_n, rate, p, every_t_target(p.category, kq)), book)


def a_plain_leaf(log_n: int, rate: int, p: Profile) -> Row:
    """Revision 9: system A's row 7 (the plain, not hiding, tree leaf; `yugen-proof-a` `CAT1_TREE_LEAF_QUERIES`) at the
    minimal counts, solved as row 9 is (plain WHIR rounds). Not part of `a_rows` (the masked rows 6 and 8 are the
    leaves of revision 7's tables); printed in the revision 9 tables because the specification's A.1 names its counts."""
    book = _a_node_at(log_n, rate, p, tree_target_for(p.category), r5.ROW7, "leaf", "row 7 (plain leaf)")
    if check_convention(p.convention) == T_GE_KQ:
        return _stamp(book, p, NEED_BOOK)
    return _fixed_point(p, lambda kq: _a_node_at(log_n, rate, p, every_t_target(p.category, kq), r5.ROW7, "leaf",
                                                 "row 7 (plain leaf)"), book)


def _a_node_at(log_n: int, rate: int, p: Profile, t, rowdef: cu.ARow = r5.ROW9, kind: str = "node",
               label: str = "row 9 (node)") -> Row:
    c = _a_cfg(rowdef, log_n, rate, 0, p)
    rs = whir.rounds(c)
    need = t.need_bits(len(rs), c.fs)
    alg = _alg(rs)
    fmin = _field_min(rs, p.field_bits, need)
    if alg.effective_bits < need:
        raise FieldTooSmall(f"{p.name}: system A {label}, 2^{log_n}, rate 1/{2 ** rate}: round {alg.name} gives "
                            f"{alg.effective_bits:.1f} < {need:.2f} bits ({_need_name(t)}) at GF(2^{p.field_bits}); "
                            f"needs {fmin} bits")
    c.queries = r5.rule_counts(c, need)
    for _ in range(64):
        bad = [r for r in whir.rounds(c) if _is_query(r) and r.effective_bits < need]
        if not bad:
            break
        for r in bad:
            c.queries[r5._level_of(r, c)] += 1
    for i in range(len(c.queries)):
        while True:
            c.queries[i] -= 1
            if min(r.effective_bits for r in whir.rounds(c)) < need:
                c.queries[i] += 1
                break
    rs = whir.rounds(c)
    w = min(rs, key=lambda r: r.effective_bits)
    opening = whir.size_bytes(c)["total"]
    size = opening + a_node_calibration() * p.field_bits / 256
    if kind == "leaf":  # row 7: the opening model only (no calibrated non-opening bytes for this row)
        size = opening
    return Row("A", kind, label, log_n, rate, tuple(c.queries), len(rs), need, w.effective_bits, w.name,
               alg.effective_bits, alg.name, p.field_bits, fmin, size, opening, extra={"config": c})


def a_node_counts_meet(row: Row, queries: list[int], p: Profile) -> bool:
    c = _a_cfg(r5.ROW9, row.stack, row.rate, 0, p, list(queries))
    rs = whir.rounds(c)
    return min(r.effective_bits for r in rs) >= _need(p, len(rs), c) - 1e-9


def a_rows(p: Profile, refused: list[str] | None = None) -> list[Row]:
    """Every admitted shape; a masked-leaf shape with no admitted stack is listed in `refused`."""
    out = []
    for label, row, rates in A_LEAF_ROWS:
        for mode in (0, 1):
            for rate in rates:
                try:
                    out.append(a_leaf(label, row, mode, rate, p))
                except NoAdmittedStack as e:
                    if refused is not None:
                        refused.append(str(e))
    for rate in A_NODE_RATES:
        for m in A_NODE_STACKS:
            out.append(a_node(m, rate, p))
    return out


# System B (yugen-proof-b2 docs/parameters.md; binius64.py, johnson.py)
B_RATES = (3, 4)
B_LEAF_VARIANT = binius64.MIXED_T_W1  # the form-T zero-knowledge leaf (`cat1t`)
B_NODE_VARIANT = binius64.ALL256_W1  # node proofs keep the all-256-bit packing (parameters.md 8.3)
B_NODE_SHAPE = binius64.Shape(a=30, b=29, w=30, p=12, v=28, kappa=8)  # a node of 2^30 AND rows (current.b_field_check)
B_NODE_WORDS = 27  # node size model at 2^27 words (as the category study)
B_LEAF_ANCHOR = (3, 184, 32, 583_680)  # form T leaf, rate 1/8, 184 queries, 32-byte salts (parameters.md 8.3, M)
B_TREES = 6  # two round oracles and four fold trees (revision 6)
B_ROUND_ORACLES = (17, 20)  # log2 elements of the leaf's round oracles (revision 6, `B_ROUND_ORACLES`)


def b_fs(p: Profile) -> FsParams:
    return FsParams(digest_bits=p.digest_bits, qrom_c1_log2=C1_LOG2)


def b_need(p: Profile) -> float:
    return binius64.tree_need(derive_target(p.category), [(PROOFS, cu.B_ROW_BUDGET)], b_fs(p))


def b_algebraic(kind: str, rate: int, field_bits: int) -> list[tuple[str, float]]:
    """(name, log2 count) of every algebraic term that bounds the field: johnson.terms (unique decoding; the leaf
    lifted to 2^22 and the node at 2^31 at rate 1/8) and the counted rounds of the leaf shape or of a node of
    2^30 AND rows (binius64.rounds_counted)."""
    rho = 2.0**-rate
    shift = int(round(math.log2(8 * rho)))
    if kind == "leaf":
        jt = johnson.terms("ud", johnson.LOG_E_LEAF - shift, None, rho, field_bits=field_bits)
        rc = binius64.rounds_counted(binius64.leaf_shape(B_LEAF_VARIANT), rate, 1, field_bits)
    else:
        jt = johnson.terms("ud", johnson.LOG_E_NODE - shift, None, rho, mask=False, index_rounds=0, field_bits=field_bits)
        rc = binius64.rounds_counted(B_NODE_SHAPE, rate, 1, field_bits)
    return [(t.name, math.log2(t.count)) for t in jt] + [(r.name, r.error_log2 + field_bits) for r in rc if r.name != "query"]


def _b_leaf_proof(rate: int, q: int, field_bits: int, digest_bits: int, salt: int) -> binius64.B64Proof:
    v = B_LEAF_VARIANT
    pr = binius64.leaf_proof(v, rate, q)
    e = field_bits // 8
    pr.field_bits, pr.ext_bytes, pr.mask_bytes, pr.oracle_bytes = field_bits, e, [e, e], [v.alphabet, e]
    pr.salt_bytes = salt
    pr.fs = FsParams(digest_bits=digest_bits)
    return pr


def b_leaf_opening(rate: int, q: int, field_bits: int, digest_bits: int, salt: int, route_s: bool = True) -> float:
    """Opening bytes of the zero-knowledge leaf; with route S the four fold trees carry the leaf salt too (a
    hypothesis of Theorem 6.6 (3): every leaf of every tree salted; zk-quantum.md 3.1, 5)."""
    pr = _b_leaf_proof(rate, q, field_bits, digest_bits, salt)
    s = binius64.size_model(pr)
    if route_s:
        s += sum(binius64._distinct(2.0**t.depth, q) * salt for t in pr.trees()[len(pr.oracle_logs):])
    return s


def b_leaf_calibration() -> float:
    rate, q, salt, m = B_LEAF_ANCHOR
    return m - b_leaf_opening(rate, q, 256, 256, salt, route_s=False)


def b_node_opening(rate: int, q: int, field_bits: int, digest_bits: int, log_words: int = B_NODE_WORDS) -> float:
    pr = binius64.node_proof(B_NODE_VARIANT, log_words, rate, q)
    pr.field_bits, pr.ext_bytes, pr.oracle_bytes = field_bits, field_bits // 8, [field_bits // 8]
    pr.fs = FsParams(digest_bits=digest_bits)
    return binius64.size_model(binius64.best_arities(pr))


def b_node_calibration() -> float:
    lw, r, q, m = binius64.NODE_ALL256
    pr = binius64.node_proof(binius64.ALL256, lw, r, q)
    pr.arities = binius64.ARITIES
    return m - binius64.size_model(pr)


def b_kq(q: int, rate: int, p: Profile, route: str = "ud", kinds: tuple[str, ...] = ("leaf", "node")) -> ht.KqInput:
    """System B's k_q at q queries with provenance (revision 10.1, R10-8): `b_counts` (E), or a T-1 report per shape
    ("B", kind, rate, route), checked against the shape's floor, used at its own count or carried as an excess at other
    counts. A row covering several kinds (dkt26's leaf + node rows) takes the largest; it is reported only if every
    kind is reported at q. The guard's named error is one more Merkle level, q_IOP (R10-7)."""
    bc = b_counts(q, rate, p, route)
    unit = b_unit(route, rate)
    src = (f"category.b_counts (E: row budget {cu.B_ROW_BUDGET} messages, six trees at a 2^30-row node's depth; "
           f"q_IOP at {padded(q, unit[0])} slots a tree, unit {unit[0]} {unit[1]})")
    outs = []
    for kind in kinds:
        rep = ht.REPORTED_KQ.get(ht.b_report_key(kind, rate, route))
        est_rep = None
        if rep is not None:
            ht.check_report(rep, cu.B_ROW_BUDGET, rep.queries[0] * B_TREES,
                            f"system B {kind}, rate 1/{2 ** rate}, {route}")
            est_rep = b_counts(rep.queries[0], rate, p, route).k_q
        outs.append(ht.resolve_kq(rep, (q,), bc.k_q, est_rep, src, bc.q_iop))
    if all(o.provenance == ht.KQ_REPORTED for o in outs):
        return max(outs, key=lambda o: o.value)
    est = [o for o in outs if o.estimated]
    top = max(outs, key=lambda o: o.value)
    if top.estimated:
        return top
    return ht.KqInput(top.value, ht.KQ_ESTIMATED, top.source + " (another kind estimated)", est[0].named_extra)


def b_c_input(q: int, rate: int, p: Profile, route: str = "ud",
              kinds: tuple[str, ...] = ("leaf", "node")) -> ht.CInput:
    """System B's c' with provenance (R10-6): reported when every kind's T-1 report carries N_msg and m."""
    reps = [ht.REPORTED_KQ.get(ht.b_report_key(k, rate, route)) for k in kinds]
    if reps and all(r is not None and r.c_prime is not None for r in reps):
        return ht.CInput(max(r.c_prime for r in reps), ht.KQ_REPORTED, "; ".join(r.source for r in reps))
    return ht.CInput(b_counts(q, rate, p, route).c_prime, ht.KQ_ESTIMATED,
                     f"N_msg = 2 x row budget {cu.B_ROW_BUDGET}, m = 2 (E, upper figures)")


def b_need_at(p: Profile, q: int, rate: int, route: str = "ud",
              kinds: tuple[str, ...] = ("leaf", "node")) -> tuple[float, int]:
    """(need, k_q) of a system-B proof with q queries under the profile's convention (EVERY_T: SG26 k_q of
    `b_counts`, padded group slots included, or a T-1 report (b_kq); T_GE_KQ: the book need with k = the row
    budget)."""
    kq = b_kq(q, rate, p, route, kinds).value
    if check_convention(p.convention) == T_GE_KQ:
        return b_need(p), kq
    return every_t_need(p.category, kq), kq


def b_fixed_point(p: Profile, rate: int, per: float, route: str = "ud",
                  kinds: tuple[str, ...] = ("leaf", "node")) -> tuple[int, float, int]:
    """Least q with q * per >= need(q) (need non-decreasing in q), iterated from the book count, which is below it
    (k_q > row budget). Returns (q, need, k_q)."""
    q = math.ceil(b_need(p) / per)
    for _ in range(64):
        nd, kq = b_need_at(p, q, rate, route, kinds)
        q2 = math.ceil(nd / per - 1e-12)
        if q2 <= q:
            return q, nd, kq
        q = q2
    raise RuntimeError("no fixed point")


def b_row(kind: str, rate: int, p: Profile, queries: int | None = None) -> Row:
    """System B's unique-decoding row. Its status is computed (revision 10, finding R9-2): certified only under EVERY_T,
    at the need of its own k_q, meeting it with the k_q guard and the hash-term conditions (`Row.checks`); a count
    passed in (`queries`) is evaluated at its own k_q and is certified only if it meets all of them."""
    terms = b_algebraic(kind, rate, p.field_bits)
    name, worst = max(terms, key=lambda x: x[1])
    per = johnson.query_bits(None, 2.0**-rate)
    if queries is not None:
        q = queries
        need, kq = b_need_at(p, q, rate, "ud", (kind,))
    elif check_convention(p.convention) == T_GE_KQ:
        need = b_need(p)
        q = math.ceil(need / per)
        kq = b_kq(q, rate, p, "ud", (kind,)).value
    else:
        q, need, kq = b_fixed_point(p, rate, per, "ud", (kind,))
    alg_bits = p.field_bits - worst
    fmin = math.ceil(need + worst - 1e-9)
    if alg_bits < need:
        raise FieldTooSmall(f"{p.name}: system B {kind}, rate 1/{2 ** rate}: {name} gives {alg_bits:.1f} < {need:.2f} bits "
                            f"at GF(2^{p.field_bits}); needs {fmin} bits")
    return _b_assemble(kind, rate, p, q, q * per, need, kq, alg_bits, name, fmin, "")


def _b_assemble(kind, rate, p, q, qbits, need, kq, alg_bits, name, fmin, route_status, suffix="", route="ud") -> Row:
    if kind == "leaf":
        opening = b_leaf_opening(rate, q, p.field_bits, p.digest_bits, p.leaf_salt_bytes)
        size = opening + b_leaf_calibration() * p.field_bits / 256
        label, stack = "zero-knowledge leaf (form T, route S)", max(B_ROUND_ORACLES)
    else:
        opening = b_node_opening(rate, q, p.field_bits, p.digest_bits)
        size = opening + b_node_calibration() * p.field_bits / 256
        label, stack = f"node, 2^{B_NODE_WORDS} words", B_NODE_WORDS
    weakest = min(qbits, alg_bits)
    r = Row("B", kind, label + suffix, stack, rate, (q,), cu.B_ROW_BUDGET, need, weakest,
            "query" if qbits <= alg_bits else name, alg_bits, name, p.field_bits, fmin, size, opening, route_status,
            extra={"k_q": kq})
    unit, uprov = b_unit(route, rate)
    r.extra["padded"] = padded(q, unit)
    kin = b_kq(q, rate, p, route, (kind,))
    assert kin.value == kq, (kin, kq)
    return _stamp(r, p, NEED_EVERY_T if p.convention == EVERY_T else NEED_BOOK, kin,
                  b_c_input(q, rate, p, route, (kind,)))


def b_rows(p: Profile) -> list[Row]:
    return [b_row(kind, rate, p) for kind in ("leaf", "node") for rate in B_RATES]


CANDIDATE_M = 10  # the refereed Johnson rows (binius-johnson-row.md revision 2; johnson-row-referee-2.md): m = 10 only


def b_candidates(p: Profile) -> list[Row]:
    """System B's list-decoding rows: CANDIDATE only. Revision 9 (finding R8-8b): the refereed m = 10 rows of
    `dkt26` (every term of the DKT26 route, list size by DKT26 (38): 19 at rate 1/8, 31 at 1/16), not a search over m
    (the search always lands on the thinnest margin: the withdrawn 102- and 77-query rows). A row that misses its need
    says so; the status always carries the preprint label."""
    from . import dkt26

    out = []
    for rate in B_RATES:
        for kind in ("leaf", "node"):
            r8 = dkt26.row(f"B {kind}, Johnson m = {CANDIDATE_M}", "dkt", rate, CANDIDATE_M, kinds=(kind,),
                           field_bits=p.field_bits, profile=p)
            k, w = r8.weakest
            alg = min((t for _, t in r8.all_terms), key=lambda t: t.bits)
            fmin = math.ceil(r8.need + p.field_bits - alg.bits - 1e-9)
            st = CANDIDATE if r8.meets else CANDIDATE + "; DOES NOT MEET the need"
            out.append(_b_assemble(kind, rate, p, r8.queries, r8.query_bits, r8.need, r8.extra_kq, alg.bits, alg.name,
                                   fmin, st, f", Johnson m = {CANDIDATE_M} (list {r8.list_size})", "dkt"))
    return out


# --- QROM, classical spBCS need, zero knowledge ---------------------------------------------------------------


def a_counts(rows: list[Row], p: Profile) -> spbcs.TranscriptCounts:
    """SG26 Definition I.1 quantities for system A's worst proof, from the category's own rows (as
    revision6.a_counts, from the rows of this profile)."""
    listed = max(r.rounds for r in rows)
    q_iop = max(sum(r.queries) for r in rows)
    l_max = stream = 0
    n_pos = 0.0
    for r in rows:
        c = r.extra["config"]
        if r.kind == "node":
            for i, q in enumerate(c.queries):
                pos = c.vars_at(i) - c.folds[i] + c.log_inv_rates[i]
                l_max, stream = max(l_max, pos), max(stream, math.ceil(q * pos / 8))
        else:
            n_pos = max(n_pos, sum(2.0 ** (c.vars_at(i) - c.folds[i] + c.log_inv_rates[i]) for i in range(len(c.folds))))
    c0 = rows[0].extra["config"]
    return spbcs.TranscriptCounts("A", listed + OTHER_ROUNDS, listed + OTHER_ROUNDS, 2, q_iop, l_max, math.log2(n_pos),
                                  max((2 ** c0.folds[0]) * c0.base_bytes, 512), max(p.digest_bytes, stream),
                                  source=f"listed rounds {listed} + OTHER_ROUNDS {OTHER_ROUNDS}",
                                  shortest_stream_bytes=p.digest_bytes)


# Revision 10 (Lemma D referee, docs/lemma-d-referee.md finding m-1): system B's in-circuit verifier checks its queries
# in groups of `unit`; when unit does not divide the count the last index is repeated in the unused places, and every
# padded slot verifies an opening in each tree. So the verifier's hash queries count ceil(q / unit) * unit slots a
# tree. Units as built: yugen-proof-b2 docs/parameters.md 15.5, fit table (read at 0f84f74): unit 2 at 192 (rate 1/8,
# leaf and merge slots), 5 at 235 (node, rate 1/4) and at 111 (candidate merge, rate 1/8; the candidate leaf slot
# "2 or 4", the larger unit 5 charged), 4 at 82 (candidate, rate 1/16). Shapes with no recorded grouping (unique
# decoding at 1/16 and 1/2, the Johnson node at 1/4) are charged unit 6, the largest unit the builder has run
# (parameters.md 14.x, "groups of 2 and of 6"): an assumption, marked.
B_QUERY_UNITS = {("ud", 3): (2, "as built"), ("ud", 2): (5, "as built"), ("dkt", 3): (5, "as built"),
                 ("dkt", 4): (4, "as built")}
B_UNIT_ASSUMED = 6


def b_unit(route: str, rate: int) -> tuple[int, str]:
    return B_QUERY_UNITS.get((route, rate), (B_UNIT_ASSUMED, "assumed: no grouping recorded"))


def padded(q: int, unit: int) -> int:
    """Query slots checked by a grouped verifier: q rounded up to a multiple of `unit`."""
    return -(-q // unit) * unit


def b_counts(q: int, rate: int, p: Profile, route: str = "ud") -> spbcs.TranscriptCounts:
    """As revision6.b_counts, at the profile's query count, rate and field. q_IOP must stay the DRAWN QUERIES WITH THE
    PADDED SLOTS INCLUDED (revision 10, Lemma D referee m-1): `padded(q, unit)` a tree, six trees."""
    v = cu.B_ROW_BUDGET
    log_code = max(B_ROUND_ORACLES) + rate
    n_pos = sum(2.0 ** (lg + rate) for lg in B_ROUND_ORACLES)
    depth = log_code
    for a in binius64.ARITIES:
        depth -= a
        n_pos += 2.0**depth
    l_max = 28 + rate  # a node of 2^30 AND rows: 2^28 four-word cells, at the rate
    slots = padded(q, b_unit(route, rate)[0])
    return spbcs.TranscriptCounts("B", v, v, 2, slots * B_TREES, l_max, math.log2(n_pos), 2**4 * (p.field_bits // 8),
                                  max(p.digest_bytes, math.ceil(q * l_max / 8)), source=f"row budget {v}",
                                  shortest_stream_bytes=p.digest_bytes)


def qrom(counts: spbcs.TranscriptCounts, e: float, p: Profile, digest_bytes: int | None = None) -> spbcs.SpbcsTree:
    return spbcs.SpbcsTree(counts, spbcs.FORMS[0], e, PROOFS, digest_bytes or p.digest_bytes, kappa_quantum(p.category))


def qrom_min_digest_bits(counts: spbcs.TranscriptCounts, cat: int) -> int:
    """Smallest whole-byte digest whose QROM hash term alone reaches kappa_Q (Theorem 6.6 (2))."""
    for db in range(16, 129):
        if spbcs.SpbcsTree(counts, spbcs.FORMS[0], 1e9, PROOFS, db, kappa_quantum(cat)).hash >= kappa_quantum(cat):
            return 8 * db
    return -1


@dataclass
class ZkRow:
    system: str
    digest_bytes: int
    proof_salt: int
    leaf_salt: int
    t_log2: float
    one: float
    pool: float
    wi_pool: float
    largest: str
    covered: bool  # b_l > b (Theorem 6.6 (3) hypothesis, Protocol 6.5 step 1(b), Definition I.1)
    pool_classical_t: float  # the same bound at t = 2^kappa_C of the privacy category (the QROM bound read for
    # classical queries: a looser reading, shown for transparency)


def zk_row(counts: spbcs.TranscriptCounts, p: Profile, digest_bytes: int | None = None) -> ZkRow:
    b = digest_bytes or p.digest_bytes
    t = kappa_quantum(p.privacy)
    one = spbcs.eps_zk(counts, t, 0.0, p.proof_salt_bytes, p.leaf_salt_bytes, b)
    pool = spbcs.eps_zk(counts, t, POOL_LOG2, p.proof_salt_bytes, p.leaf_salt_bytes, b)
    terms = {"salt": pool.salt_term, "collision": pool.collision_term, "key": pool.key_term, "leaf": pool.leaf_term}
    wi_ = spbcs.eps_wi_log2(counts, POOL_LOG2, WITNESS_BITS_LOG2, p.proof_salt_bytes, p.leaf_salt_bytes, b)
    pc = spbcs.eps_zk(counts, kappa_classical(p.privacy), POOL_LOG2, p.proof_salt_bytes, p.leaf_salt_bytes, b)
    return ZkRow(counts.system, b, p.proof_salt_bytes, p.leaf_salt_bytes, t, one.total_log2, pool.total_log2, wi_,
                 max(terms, key=terms.get), p.leaf_salt_bytes > b, pc.total_log2)


@dataclass
class Certificate7:
    profile: Profile
    a: list[Row]
    b: list[Row]
    b_candidates: list[Row]
    a_counts: spbcs.TranscriptCounts
    b_counts: spbcs.TranscriptCounts
    a_qrom: spbcs.SpbcsTree
    b_qrom: spbcs.SpbcsTree
    a_zk: ZkRow
    b_zk: ZkRow
    refused: list[str] = field(default_factory=list)

    @property
    def a_e(self) -> float:
        return min(r.weakest for r in self.a)

    @property
    def b_e(self) -> float:
        return min(r.weakest for r in self.b)


def certify(p: Profile, zk_required: bool = True) -> Certificate7:
    """Every row of both systems at the profile, condition Q under Theorem 6.6 (2) as a hard failure, and the
    leaf-salt hypothesis of Theorem 6.6 (3). Raises a CategoryRefusal (or spbcs.ConditionQFailure)."""
    check_profile(p)
    refused: list[str] = []
    a, b = a_rows(p, refused), b_rows(p)
    for r in a + b:
        if r.margin < -1e-9:
            raise CategoryRefusal(f"{p.name}: {r.system} {r.label} misses its need by {-r.margin:.2f} bits")
    ac = a_counts(a, p)
    bmax = max(b, key=lambda r: r.queries[0])
    bc = b_counts(bmax.queries[0], bmax.rate, p)  # the rate-1/8 row (most queries): revision 6's counts at cat1
    aq = spbcs.require(qrom(ac, min(r.weakest for r in a), p), f"{p.name}, system A, spBCS")
    bq = spbcs.require(qrom(bc, min(r.weakest for r in b), p), f"{p.name}, system B, spBCS")
    if zk_required and p.leaf_salt_bytes <= p.digest_bytes:
        raise SaltNotCovered(f"{p.name}: leaf salts of {p.leaf_salt_bytes} B are not longer than the {p.digest_bytes}-byte "
                             "digest: Theorem 6.6 (3) needs b_l > b (its eps_leaf is vacuous otherwise)")
    return Certificate7(p, a, b, b_candidates(p), ac, bc, aq, bq, zk_row(ac, p), zk_row(bc, p), refused)


# --- tables ---------------------------------------------------------------------------------------------------


def _q(r: Row) -> str:
    return ", ".join(map(str, r.queries))


def _p(x: float) -> str:
    return "1 (vacuous)" if x >= 0 else f"2^{x:.1f}"


def _kib(b: float) -> str:
    return f"{b / 1024:,.0f}"


def derivation_table(cats=(1, 2, 3, 4, 5)) -> list[str]:
    out = ["## Derivation of the targets from NIST-CfP Section 4.A.5 (pages 16 to 18)", "",
           "| Category | NIST's requirement (reference attack) | Classical gates (p. 18) | Quantum gates x MAXDEPTH (p. 18) | "
           "kappa_C (oracle calls) | Gates an evaluation implied | Grover overhead implied | kappa_Q | G a round | "
           "Digest, attack rule | Digest, proven rule (book term 3.5 t^2 / 2^lambda, SUPERSEDED) | Digest, proven rule (SG26 hash "
           "term, tree, c' = 2,401) | Book need, A (k = 599; non-default) | Book need, B (k = 600; non-default) |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in cats:
        n, t = NIST[c], derive_target(c)
        sg = ht.digest_for_classical(kappa_classical(c), 2_401, 0, PROOFS)
        g = grover_overhead_log2(c)
        out.append(f"| {c} | {n.kind} on {n.reference} | 2^{n.classical_gates_log2} | "
                   f"{'2^' + str(n.quantum_gates_maxdepth_log2) if n.quantum_gates_maxdepth_log2 else 'not given'} | "
                   f"{kappa_classical(c):.0f} | 2^{gates_per_evaluation_log2(c):.0f} | {'2^%.0f' % g if g is not None else '-'} | "
                   f"{kappa_quantum(c):.0f} | {t.attack_bits:.0f} | {t.digest_attack} | {t.digest_proven} | {sg} | "
                   f"{round_need(c, 87 + OTHER_ROUNDS):.2f} | {round_need(c, cu.B_ROW_BUDGET):.2f} |")
    out += ["", "Revision 9: the last two columns are the book's needs, NON-DEFAULT (t >= k_q). The default need (every t) "
            "is kappa_C + 1 + log2 N + log2(1 + k_q) at each row's own k_q (SG26 Theorem 6.6 (2), Definitions H.3, H.4; "
            "docs/decision-qrom-counting.md): 157.0 to 158.8 bits at category 1, printed with each row.",
            "", "Revision 10 (finding R9-1): the proven digest rule is taken from the hash term of SG26 Theorem 6.6 (2) "
            "itself, c' (t + k_q)^2 / 2^(8b) per proof summed over the tree: 8b >= 2 kappa_C + 1 + log2(N c') (k_q "
            "negligible against 2^kappa_C), whole bytes. The book column (3.5 t^2 / 2^lambda, counted once for the tree: "
            "the source of the former '126.6 proven classical bits' and '264') is kept as a record.",
            "", "Condition Q's per-round need (Theorem 6.6 (2) IOP term, C1 = 6, N = 20,000): "
            + "; ".join(f"cat{c} {2 * kappa_quantum(c) + 1 + C1_LOG2 + math.log2(PROOFS):.2f}" for c in cats)
            + " bits; condition C binds at every category."]
    return out


def _status_cell(r: Row) -> str:
    if r.certified:
        return certified_label(r.hash_basis)
    if r.status == NON_DEFAULT:
        return f"**{NON_DEFAULT}**"
    if not r.route_status:
        return f"**{r.status}**"
    st = "**candidate** (rests on DKT26, a preprint)"
    if "DOES NOT MEET" in r.status:
        st += "; **does not meet the need**"
    if r.status.startswith(NON_DEFAULT):
        st = f"**{NON_DEFAULT}**; " + st
    return st


def _hash_cells(r: Row) -> str:
    h = r.hash
    if h is None:
        return "- | - | -"
    return f"{h.cells()} | {h.digest_needed}"


def rows_table(rows: list[Row], title: str) -> list[str]:
    out = ["", f"### {title}", "",
           "| System | Row | Stack | Rate | Queries | Status | Listed rounds / k | k_q (provenance) | k_q guard | c' | Need | "
           "Weakest round | Margin | Hash term, classical bits, proof / tree | Hash term, QROM bits, proof / tree | "
           "Digest for a proven classical hash part (bits) | "
           "Weakest algebraic (bits) | Field min (bits) | Opening (B, E) | Proof (KiB, E) | Within PROOF_BYTES_MAX |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        st = _status_cell(r)
        kq = r.kq.label() if r.kq else "-"
        guard = f"{r.kq.guard:.4f}" if r.kq else "-"
        cp = r.c_input.label() if r.c_input else f"{r.c_prime:,}"
        out.append(f"| {r.system} | {r.label}{' (' + r.note + ')' if r.note else ''} | 2^{r.stack} | 1/{2 ** r.rate} | {_q(r)} | {st} | "
                   f"{r.rounds} | {kq} | {guard} | {cp} | {r.need:.3f} | {r.weakest_name}: {r.weakest:.3f} | "
                   f"{r.margin:+.4f} | {_hash_cells(r)} | {r.alg_name}: "
                   f"{r.alg_bits:.1f} | {r.field_min} | {r.opening:,.0f} | {_kib(r.size)} | "
                   f"{'yes' if r.size <= PROOF_BYTES_MAX else '**no**'} |")
    return out


def bytes_per_query_table(cert: Certificate7) -> list[str]:
    """Opening bytes divided by opened positions, at digests of 32, 48 and 64 bytes and the leaf salts of each
    category profile (node rows carry no salt); the row's queries and field as certified."""
    p = cert.profile
    salts = (64, 96, 112)
    out = ["", "### Bytes a query (opening bytes / opened positions, E), by digest and leaf salt", "",
           "| System | Row | Rate | Queries | " + " | ".join(f"d = {d} B, salt {s} B" for d in (32, 48, 64) for s in salts) + " |",
           "|---|---|---|---|" + "---|" * 9]
    sel = [r for r in cert.a if r.kind == "leaf" and "mode 0" in r.label] + \
          [r for r in cert.a if r.kind == "node" and r.stack == 27] + cert.b
    for r in sel:
        cells = []
        for d in (32, 48, 64):
            for s in salts:
                if r.system == "A":
                    c = r.extra["config"]
                    c2 = cu.a_config(cu.ROW6 if r.label.startswith("row 6") else (r5.ROW8 if r.kind == "leaf" else r5.ROW9),
                                     r.stack, r.rate, s if r.kind == "leaf" else 0, list(c.queries), p.field_bits, 8 * d)
                    ob = wi.size_bytes(c2, "A")["total"] if r.kind == "leaf" else whir.size_bytes(c2)["total"]
                    npos = sum(c.queries)
                else:
                    q = r.queries[0]
                    ob = b_leaf_opening(r.rate, q, p.field_bits, 8 * d, s) if r.kind == "leaf" else \
                        b_node_opening(r.rate, q, p.field_bits, 8 * d)
                    npos = q * (B_TREES if r.kind == "leaf" else 1 + len(binius64.ARITIES))
                cells.append(f"{ob / npos:,.0f}" if (r.kind == "leaf" or s == salts[0]) else "=")
        out.append(f"| {r.system} | {r.label} | 1/{2 ** r.rate} | {_q(r)} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("Node rows carry no salt (D-c): their cells repeat across salt columns ('='). B's leaf counts route S "
               "(six salted trees).")
    return out


def tables(cats=(1, 3, 5), convention: str = EVERY_T, hash_basis: str = ht.HASH_ATTACK_RULE) -> list[str]:
    """The revision 7 tables (the category as an input), computed under `convention` (revision 9: EVERY_T default) and
    the classical hash basis (revision 10)."""
    check_convention(convention)
    if hash_basis not in ht.HASH_BASES:
        raise ValueError(f"hash basis {hash_basis!r}; one of {ht.HASH_BASES}")
    profiles = {c: replace(PROFILES[c], convention=convention, hash_basis=hash_basis) for c in cats}
    head = ("# Revision 10: the security category as an input, counting convention EVERY t, the SG26 hash term on every "
            f"row, classical hash basis {hash_basis} (generated by `uv run yugen-soundness --rev7`)"
            if convention == EVERY_T else
            f"# {NON_DEFAULT.upper()}: the revision 7 tables at the book need (generated by `uv run yugen-soundness "
            "--rev7 --convention t-ge-kq`)")
    out = [head, "",
           f"Tree of {PROOFS:,} proofs; union bound; no grinding; unique decoding for certified rows; true rates; spBCS "
           "(Sharp-Grubbs, ePrint 2026/2615, Theorem 6.6). Sizes are estimates (E) anchored on measured proofs (M): A's "
           f"masked leaf {A_LEAF_ANCHOR[1]:,} B (row 6, 64-byte salts), A's node {A_NODE_ANCHOR:,} B, B's form-T leaf "
           f"{B_LEAF_ANCHOR[3]:,} B (32-byte salts), B's node {binius64.NODE_ALL256[3]:,} B (2^23 words); non-opening bytes "
           "scale with the field's element size.", ""]
    out += derivation_table()
    for c in cats:
        out += profile_tables(profiles[c])
    if 3 in cats or 5 in cats:
        out += ["", "## Profile M-1 (working assumption: category 3 soundness and binding, category 5 privacy)", ""]
        out += _summary_banner(convention)
        out += zk_table([replace(M1, convention=convention), replace(PROFILES[3], convention=convention),
                         replace(PROFILES[5], convention=convention)])
    out += field_summary(cats, convention, hash_basis)
    out += size_summary(cats, convention, hash_basis)
    out += qrom_digest_table([c for c in cats if c in (3, 5)] or list(cats), convention, hash_basis)
    zf = zk_floor_table(certify(replace(PROFILES[1], convention=convention)))
    return out + zf[:2] + _summary_banner(convention) + zf[2:] + PROVEN_FOOTER


def profile_tables(p: Profile) -> list[str]:
    t = derive_target(p.category)
    banner = ([f"**{NON_DEFAULT.upper()}**: every row below is solved at the book need (t >= k_q reading); none is "
               "certified. The calculator's convention is every t (revision 9)."] if p.convention == T_GE_KQ else [])
    out = [""] + banner + [f"## {p.name}: digest {p.digest_bits} bits, salts {p.proof_salt_bytes} B (proof) / {p.leaf_salt_bytes} B (leaf), "
           f"GF(2^{p.field_bits}), tree hashes {p.tree_hash_a} (A) / {p.tree_hash_b} (B)", ""]
    if p.category in (2, 4):
        out += [f"Category {p.category} gives kappa_C = {t.classical_chain:.0f}, the same as category {p.category - 1}: "
                "its rows are those of category " + str(p.category - 1) + "."]
    try:
        cert = certify(p)
    except (CategoryRefusal, spbcs.ConditionQFailure) as e:
        return out + [f"**Refused**: {e}"]
    out += rows_table(cert.a, "System A (leanVM): masked leaves (W-I, every zero-knowledge round) and node row 9")
    if cert.refused:
        out += ["", "Masked-leaf shapes with no admitted stack (the hiding lane does not fit; not rows): "
                + "; ".join(x.split(": ", 1)[1] for x in cert.refused)]
    out += rows_table(cert.b, "System B (Binius64): unique decoding" + ("" if p.convention == EVERY_T
                                                                          else f", {NON_DEFAULT}"))
    if cert.b_candidates:
        out += rows_table(cert.b_candidates, "System B: list-decoding rows, CANDIDATE only (DKT26 route; never certified)")
    else:
        out += ["", f"System B list-decoding candidates: none meets the need at GF(2^{p.field_bits})."]
    for fb in BUILDABLE_FIELDS:
        if fb > p.field_bits and not any(r.weakest >= r.need - 1e-9 for r in cert.b_candidates):
            cand = b_candidates(replace(p, field_bits=fb))
            if cand:
                out += rows_table(cand, f"System B: list-decoding rows at GF(2^{fb}), CANDIDATE only (DKT26 route; never "
                                        "certified; the certified rows above stay at their field)")
                break
    out += bytes_per_query_table(cert)
    out += ["", "### QROM (Theorem 6.6 (2), N = 20,000, SHAKE256 streams) and condition C under spBCS (finding Q-5, reported)", "",
            "| System | e | k_q | c' | IOP term | Hash term | QROM bits | kappa_Q | Margin | Stream term (log2; at the shortest "
            "stream b + e = b, e = 0: the theorem's b + e, an upper bound on the term until T-1 reports e; R10-9) | "
            "Smallest digest for the hash term (bits) | Classical need, every t, worst proof's k_q (the rows use their own) | "
            "for t >= k_q (non-default) |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, q in ((cert.a_counts, cert.a_qrom), (cert.b_counts, cert.b_qrom)):
        out.append(f"| {k.system} | {q.e:.2f} | {k.k_q:,} | {k.c_prime:,} | {q.iop:.2f} | {q.hash:.2f} | {q.bits:.2f} | "
                   f"{q.quantum_chain:.0f} | {q.margin:+.2f} | {q.stream_term_log2:.0f} | {qrom_min_digest_bits(k, p.category)} | "
                   f"{spbcs.classical_need(k, PROOFS, t.classical_chain):.2f} | "
                   f"{spbcs.classical_need(k, PROOFS, t.classical_chain, True):.2f} |")
    out += hash_term_summary(cert)
    out += tree_qrom_summary(cert)
    out += ["", "### Zero knowledge of leaf proofs (Theorem 6.6 (3), (4); each figure plus Q eps_hvzk, open)", ""]
    out += _zk_lines([(p, cert)])
    a0 = [r for r in cert.a if r.kind == "leaf"]
    out += ["", "Leaf proof sizes (KiB, E): " + "; ".join(f"A {r.label} 1/{2 ** r.rate} {_kib(r.size)}" for r in a0)
            + "; " + "; ".join(f"B {r.label} 1/{2 ** r.rate} {_kib(r.size)}" for r in cert.b if r.kind == "leaf") + "."]
    return out


def hash_term_summary(cert: Certificate7) -> list[str]:
    """Revision 10 (finding R9-1): the hash term of SG26 Theorem 6.6 (2) over the category's rows, and the plain answer
    to 'does the system meet the category once it is counted' in the classical and the quantum measure."""
    p = cert.profile
    kc, kq_ = kappa_classical(p.category), kappa_quantum(p.category)
    banner = ([f"**{NON_DEFAULT.upper()}** (the summary below uses the every-t hash term; the rows above are not "
               "certified)."] if p.convention == T_GE_KQ else [])
    out = ["", "### The hash term of SG26 Theorem 6.6 (2) (revision 10, finding R9-1)", ""] + banner + [
        f"Per proof c' (t + k_q)^2 / 2^{p.digest_bits} (ROM) and 6 c' (t + k_q)^3 / 2^{p.digest_bits} (QROM), summed over "
        f"N = {PROOFS:,} proofs; b = {p.digest_bytes} bytes is the length of every digest the transcript writes (SG26 "
        "Section I.1: challenge-input keys, leaf and node digests, the written-back stream prefix; at category 1 "
        "Keccak-256 keys and trees with SHAKE256 streams in A, SHA-256 keys, BLAKE3 trees and SHAKE256 streams in B; "
        f"this profile's trees: {p.tree_hash_a} (A), {p.tree_hash_b} (B)). Classical: the largest kappa with the tree term <= t / 2^(kappa + 1) for every 1 <= t <= "
        "2^kappa (binding at t = 2^kappa). QROM: the query count at which the tree term reaches 1/2. Revision 10.2: the "
        "tree's classical hash level is Theorem TE' of docs/lemma-tree-extraction.md (the hash part taken once for the "
        f"tree, c'_max (t + N k_q,max)^2 / 2^{p.digest_bits}), {ht.TREE_CONDITIONS}; the per-proof union form is printed "
        "beside it as the comparison and is what the proven-basis check uses (the lower figure).", "",
        "| System | Rows | c' (range) | Classical, proof | Classical, tree, Theorem TE' (" + ht.TREE_CONDITIONS + ") | "
        "Classical, tree, per-proof union (comparison) | kappa_C | Classical shortfall, TE' / union | "
        "Digest for a classical tree at kappa_C, TE' / union (bits) | QROM, proof | QROM, tree | kappa_Q | QROM margin | "
        "Classical hash part judged by | Verdict, classical | Verdict, quantum |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for sysname, rows in (("A", cert.a), ("B", cert.b)):
        hs = [r.hash for r in rows if r.hash is not None]
        if not hs:
            continue
        worst_c = min(hs, key=lambda h: h.classical_tree)
        worst_q = min(hs, key=lambda h: h.quantum_tree)
        cps = sorted({h.c_prime for h in hs})
        te = tree_te_level(hs)
        d_te = next((8 * b for b in range(16, 129) if ht.tree_extraction_level(cps[-1], PROOFS * max(h.k_q for h in hs),
                                                                               8 * b) >= kc - 1e-9), -1)
        h_ok = p.digest_bits >= derive_target(p.category).digest_attack
        vc = ("meets on condition H's attack rule (digest " f"{p.digest_bits} >= {derive_target(p.category).digest_attack}"
              "); NOT as a proven bound" if p.hash_basis == ht.HASH_ATTACK_RULE and h_ok else
              (f"meets (proven basis; tree {ht.TREE_CONDITIONS})" if worst_c.classical_margin >= 0
               else "**does not meet** (proven basis)"))
        vq = (f"meets (tree derived {ht.TREE_CONDITIONS})" if worst_q.quantum_margin >= 0 else "**does not meet**")
        out.append(f"| {sysname} | {len(hs)} | {cps[0]:,} to {cps[-1]:,} | {min(h.classical_proof for h in hs):.2f} | "
                   f"{te:.2f} | {worst_c.classical_tree:.2f} | {kc:.0f} | {kc - te:.2f} / {-worst_c.classical_margin:.2f} | "
                   f"{d_te} / {max(h.digest_needed for h in hs)} | {min(h.quantum_proof for h in hs):.2f} | "
                   f"{worst_q.quantum_tree:.2f} | {kq_:.0f} | {worst_q.quantum_margin:+.2f} | {p.hash_basis} | {vc} | {vq} |")
    return out


def tree_te_level(hs) -> float:
    """Theorem TE' (revision 10.2): the classical hash level of a tree of the system's rows, c'_max over the rows and
    K = N k_q,max (docs/lemma-tree-extraction.md 7 (b))."""
    return ht.tree_extraction_level(max(h.c_prime for h in hs), PROOFS * max(h.k_q for h in hs), hs[0].digest_bits)


def tree_qrom_summary(cert: Certificate7) -> list[str]:
    """Revision 10.2 (docs/tree-extraction-referee.md 3.3, task D): the QROM figures of the tree. The per-proof union
    (the calculator's QROM bits, N = 20,000 in the sum) is what the project CLAIMS; the one-table form of Proposition
    TE-Q' (docs/lemma-tree-extraction.md 9: N does not multiply t^2) is printed beside it with the same label, and the
    term Lemma QC adds, 10 (K - k_q,r) / 2^(8(b+e)), in bits at e = 0 (an upper bound on the term)."""
    p = cert.profile
    out = ["", "### The tree's QROM figures: per-proof union (claimed) and the one-table form of Proposition TE-Q' "
           "(revision 10.2)", "",
           f"Every figure below is derived {ht.TREE_CONDITIONS} (recursion heuristic C2, not a proven QROM theorem; no "
           "unconditional QROM figure exists for a tree whose inner proofs are witnesses), and in addition on SG26 "
           "Theorem I.16 (1) (a preprint), H-BIND and Lemma QC (refereed, pass). The project claims the per-proof union, the lower "
           "figure.", "",
           "| System | e (weakest round) | Per-proof union: IOP / hash / QROM bits (claimed) | One table: IOP / hash / "
           "QROM bits (comparison) | kappa_Q | Lemma QC term, log2 (K = N k_q,max) | Label |",
           "|---|---|---|---|---|---|---|"]
    for sysname, rows, q in (("A", cert.a, cert.a_qrom), ("B", cert.b, cert.b_qrom)):
        hs = [r.hash for r in rows if r.hash is not None]
        if not hs:
            continue
        one = replace(q, proofs=1)
        qc = ht.lemma_qc_log2(PROOFS * max(h.k_q for h in hs), p.digest_bits)
        out.append(f"| {sysname} | {q.e:.2f} | **{q.iop:.2f} / {q.hash:.2f} / {q.bits:.2f}** | {one.iop:.2f} / "
                   f"{one.hash:.2f} / {one.bits:.2f} | {q.quantum_chain:.0f} | {qc:.2f} | {ht.TREE_CONDITIONS} |")
    return out


ZK_HEAD = ["| Profile | System | Digest b (B) | Proof salt b_s (B) | Leaf salt b_l (B) | t | One proof | Pool (2^20) | "
           "Largest term | WI (6.6 (4)), pool | b_l > b (covered) | Pool at t = 2^kappa_C |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]


def _zk_lines(pcs) -> list[str]:
    out = list(ZK_HEAD)
    for p, cert in pcs:
        for z in (cert.a_zk, cert.b_zk):
            out.append(f"| {p.name} | {z.system} | {z.digest_bytes} | {z.proof_salt} | {z.leaf_salt} | 2^{z.t_log2:.0f} | "
                       f"{_p(z.one)} | {_p(z.pool)} | {z.largest} | {_p(z.wi_pool)} | {'yes' if z.covered else '**no**'} | "
                       f"{_p(z.pool_classical_t)} |")
    return out


def zk_table(profiles) -> list[str]:
    pcs = []
    for p in profiles:
        try:
            pcs.append((p, certify(p)))
        except (CategoryRefusal, spbcs.ConditionQFailure) as e:
            pass
    return _zk_lines(pcs)


ZK_TARGETS_LOG2 = (-64.0, -96.0, -128.0)  # pool targets (2^20 proofs), excluding Q eps_hvzk (referee F-4)


def leaf_salt_floor(counts: spbcs.TranscriptCounts, digest_bytes: int, target_log2: float) -> int:
    """Smallest leaf salt (bytes) whose leaf term Q n_pos eps_leaf over the pool is at most 2^target
    (Theorem 6.6 (3); the leaf term does not depend on t or on the category)."""
    for bl in range(digest_bytes + 1, digest_bytes + 129):
        leaf = spbcs.eps_leaf_log2(digest_bytes, bl, counts.leaf_bytes)
        if POOL_LOG2 + counts.n_pos_log2 + leaf <= target_log2:
            return bl
    return -1


def proof_salt_floor(t_log2: float, target_log2: float) -> int:
    """Smallest proof salt b_s (bytes) with 4 Q t / 2^(4 b_s) <= 2^target over the pool (Theorem 6.6 (3))."""
    return math.ceil((2 + POOL_LOG2 + t_log2 - target_log2) / 4)


def zk_floor_table(cert1: Certificate7) -> list[str]:
    out = ["", "## Salt floors from a zero-knowledge target (pool of 2^20 leaf proofs; each figure excludes Q eps_hvzk)", "",
           "Leaf salt floor: the leaf term alone (independent of t). Proof salt floor: the salt term at t = 2^kappa_Q of the "
           "privacy category (t counts hash queries before the last proof; Theorem 6.6 (3)).", "",
           "| Pool target | Leaf salt, b = 32 (A / B) | b = 48 (A / B) | b = 64 (A / B) | Proof salt, t = 2^64 | t = 2^96 | t = 2^128 |",
           "|---|---|---|---|---|---|---|"]
    for tg in ZK_TARGETS_LOG2:
        cells = [f"{leaf_salt_floor(cert1.a_counts, b, tg)} / {leaf_salt_floor(cert1.b_counts, b, tg)}" for b in (32, 48, 64)]
        out.append(f"| 2^{tg:.0f} | " + " | ".join(cells) + " | "
                   + " | ".join(str(proof_salt_floor(t, tg)) for t in (64.0, 96.0, 128.0)) + " |")
    out += ["", "Counts (n_pos, leaf bytes) are category 1's; at larger counts n_pos changes by under one bit (leaf "
            "salt floors move by at most one byte)."]
    return out


def _rows_word(convention: str, hash_basis: str = ht.HASH_ATTACK_RULE) -> str:
    """Finding R9-3: the summaries' word for the rows they summarise ("certified" only under EVERY_T); revision 10.1
    (R10-11): under the proven hash basis the rows are "solved", since that basis certifies no 256-bit row."""
    if convention != EVERY_T:
        return "non-default (t >= k_q), not certified,"
    return "certified" if hash_basis == ht.HASH_ATTACK_RULE else "solved (status per row; proven hash basis)"


# Revision 10.1 (finding R10-2): what "proven" rests on, printed under every table set that says "certified" or
# "proven". Revision 10.2 (docs/tree-extraction-referee.md, task D): the conditions of the tree figures listed one by
# one, each with its status; the tree's classical hash level that of Theorem TE', the QROM figure claimed is the lower.
PROVEN_FOOTER = [
    "", "### What \"proven\" and \"certified\" rest on (revision 10.2; docs/what-is-proven.md)", "",
    "Every figure called proven, and every row labelled certified, rests on the random-oracle model and on the "
    "conditions below, some of them OWED, so in the terms of docs/what-is-proven.md it is conditional; every TREE "
    "figure (classical and quantum) is in addition conditional on the recursion heuristic C2, read as a joint "
    "probability (never a conditional one; equivalence tests do not discharge it), and none is an unconditional "
    "theorem. Conditions: "
    "(1) C2, the recursion heuristic (the event 'a child proof accepted by the in-circuit verifier and rejected by the "
    "native verifier' does not occur; NOT dischargeable by any random-oracle proof; excluded in practice by "
    "in-circuit / native verifier equivalence, a tested engineering property; it enters Theorem TE' at the child's "
    "acceptance and by keeping the node relation oracle-free); "
    "(2) K-A and K-B, OWED: the round-by-round KNOWLEDGE soundness of both IOPs outside the openings; "
    "(3) T-1, OWED from the builders: the transcripts' domain separation across systems (H-DS, injective encodings), "
    "their fit to Sharp-Grubbs Protocol 6.5, and the reported c' and k_q (until then c' and k_q are estimates, "
    "marked E); "
    "(3a) C-4, the level and proof-count binding in node statements: met by design, by search, NOT audited (an audit "
    "owed); "
    "(3b) H-BIND, collision resistance of the concrete statement-digest functions computed inside the node "
    "relations (a standard-model assumption, not an oracle property; it excludes SHAPE-VIOLATION and bounds the "
    "tree's node count); "
    "(4) the modelling assumptions MA-1 (Keccak-256 and SHAKE256 in A, SHA-256 and SHAKE256 in B, as one random oracle "
    "with four disjoint parts) and MA-2' (BLAKE3 derive_key, B's leaves and nodes, as that oracle's leaf and node "
    "parts); "
    "(5) Sharp-Grubbs, ePrint 2026/2615, Theorem 6.6 (2) and Theorem I.16 (1), (2): a PREPRINT; "
    "(6) Theorem TE' (docs/lemma-tree-extraction.md revision 3; revisions 1 and 2 refereed, pass with conditions; "
    "revision 3, with SHAPE-VIOLATION and Lemma TE.3, UNREFEREED); "
    "(7) Lemma QC (the continuation after a database measurement, from Chiesa-Manohar-Spooner, ePrint 2019/834, "
    "Lemma 3.2): refereed, pass (docs/qc-and-status-referee.md); "
    "(8) Theorem D (system B's repeated openings): refereed, pass with conditions. "
    "Candidate (Johnson-regime) rows rest in addition on DKT26 (Dao, Kominers, Thaler, ePrint 2026/2056), a PREPRINT, "
    "and are never certified. "
    f"At category 1 (256-bit digests) the tree's classical hash level is {121.89:.2f} bits (Theorem TE', "
    f"{ht.TREE_CONDITIONS}); the per-proof union form, {114.74:.2f}, is printed beside it and is the figure the "
    "proven-basis check uses; the tables give each profile's figures. The classical hash part is "
    "certified on condition H's attack rule unless the basis printed says proven. The tree's QROM level claimed is "
    "the per-proof union (69.58 A / 70.45 B at category 1); the one-table form (76.72 / 77.60, hash part 80.40) is "
    f"printed beside it, {ht.TREE_CONDITIONS}. The tree figures are for ONE output tree (attempts = 1; R10-10).",
]


def _summary_banner(convention: str) -> list[str]:
    return ([f"**{NON_DEFAULT.upper()}**: the rows summarised below are solved at the book need (t >= k_q); none is "
             "certified."] if convention == T_GE_KQ else [])


def size_summary(cats, convention: str = EVERY_T, hash_basis: str = ht.HASH_ATTACK_RULE) -> list[str]:
    out = ["", "## Proof sizes by category (KiB, E) and the PROOF_BYTES_MAX they need", ""] + _summary_banner(convention) + [
           "| Profile | A leaf, row 6 mode 0 | A leaf, row 8 mode 0 (1/4) | A node 2^27 (1/2; 1/4) | A node 2^30 (1/2; 1/4) | "
           f"B leaf (1/8; 1/16) | B node 2^27 words (1/8; 1/16) | Largest {_rows_word(convention, hash_basis)} proof (B) | "
           "Within 1,835,008 B |",
           "|---|---|---|---|---|---|---|---|---|"]
    profiles = [replace(PROFILES[c], convention=convention) for c in cats]
    if 5 in cats:
        profiles.append(replace(PROFILES[5], field_bits=512, label="cat5 at GF(2^512)", convention=convention))
    for p in profiles:
        try:
            cert = certify(p)
        except (CategoryRefusal, spbcs.ConditionQFailure) as e:
            out.append(f"| {p.name} | refused: {e} |||||||| ")
            continue
        g = lambda sysn, kind, lab, st, rt: next(r for r in (cert.a if sysn == "A" else cert.b)
                                                 if r.kind == kind and r.label.startswith(lab) and r.stack == st and r.rate == rt)
        big = max(cert.a + cert.b, key=lambda r: r.size)
        out.append(f"| {p.name} | {_kib(g('A', 'leaf', 'row 6 (standalone masked), mode 0', 22, 2).size)} | "
                   f"{_kib(g('A', 'leaf', 'row 8 (masked in a tree), mode 0', 22, 2).size)} | "
                   f"{_kib(g('A', 'node', 'row 9', 27, 1).size)}; {_kib(g('A', 'node', 'row 9', 27, 2).size)} | "
                   f"{_kib(g('A', 'node', 'row 9', 30, 1).size)}; {_kib(g('A', 'node', 'row 9', 30, 2).size)} | "
                   f"{_kib(g('B', 'leaf', 'zero', 20, 3).size)}; {_kib(g('B', 'leaf', 'zero', 20, 4).size)} | "
                   f"{_kib(g('B', 'node', 'node', B_NODE_WORDS, 3).size)}; {_kib(g('B', 'node', 'node', B_NODE_WORDS, 4).size)} | "
                   f"{big.size:,.0f} ({big.system} {big.kind} 2^{big.stack} 1/{2 ** big.rate}) | "
                   f"{'yes' if big.size <= PROOF_BYTES_MAX else '**no**'} |")
    return out


def field_summary(cats, convention: str = EVERY_T, hash_basis: str = ht.HASH_ATTACK_RULE) -> list[str]:
    """Minimum challenge field per system and category from the algebraic rounds (every certified shape)."""
    out = ["", f"## Minimum challenge field (bits) from the algebraic rounds, every {_rows_word(convention, hash_basis)} "
           "shape", ""] + \
        _summary_banner(convention) + [
           "| Category | Need (A / B) | A leaf | A node (worst over 2^24..2^30, rates 1/2, 1/4) | A | B leaf | B node | B | "
           "Smallest buildable field |", "|---|---|---|---|---|---|---|---|---|"]
    for c in cats:
        p = replace(PROFILES[c], field_bits=512, convention=convention)  # a field that always serves
        a, b = a_rows(p), b_rows(p)
        al = max(r.field_min for r in a if r.kind == "leaf")
        an = max(r.field_min for r in a if r.kind == "node")
        bl = max(r.field_min for r in b if r.kind == "leaf")
        bn = max(r.field_min for r in b if r.kind == "node")
        best = min(f for f in BUILDABLE_FIELDS if f >= max(al, an, bl, bn))
        out.append(f"| {c} | {min(r.need for r in a):.2f}-{max(r.need for r in a):.2f} / {min(r.need for r in b):.2f}-"
                   f"{max(r.need for r in b):.2f} | {al} | {an} | {max(al, an)} | {bl} | {bn} | {max(bl, bn)} | "
                   f"GF(2^{best}) |")
    return out


def qrom_digest_table(cats, convention: str = EVERY_T, hash_basis: str = ht.HASH_ATTACK_RULE) -> list[str]:
    out = ["", f"## QROM bits by digest length (Theorem 6.6 (2), the category's {_rows_word(convention, hash_basis)} rows' "
           "weakest round)", ""] + _summary_banner(convention) + [
           "| Category | System | Digest (bits) | IOP term | Hash term | QROM bits | kappa_Q | Margin | Verdict |",
           "|---|---|---|---|---|---|---|---|---|"]
    for c in cats:
        p = replace(PROFILES[c], convention=convention)
        a, b = a_rows(p), b_rows(p)
        for sysname, rows in (("A", a), ("B", b)):
            e = min(r.weakest for r in rows)
            for d in (256, 384, 512):
                pp = replace(p, digest_bits=d)
                bm = max(b, key=lambda r: r.queries[0])
                k = a_counts(a, pp) if sysname == "A" else b_counts(bm.queries[0], bm.rate, pp)
                q = qrom(k, e, pp)
                ok = q.meets
                verdict = "meets" if ok else "**refused** (condition Q)"
                if d < derive_target(c).digest_attack:
                    verdict += "; below condition H's attack rule"
                out.append(f"| {c} | {sysname} | {d} | {q.iop:.2f} | {q.hash:.2f} | {q.bits:.2f} | {q.quantum_chain:.0f} | "
                           f"{q.margin:+.2f} | {verdict} |")
    return out
