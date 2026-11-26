"""Revision 10 (2026-11-19): the hash term of Sharp-Grubbs Theorem 6.6 (2), and k_q as an input with provenance.

Source, read from the RENDERED page images (PDFKit, scale 2.2; the text layer drops symbols): C. Sharp, P. Grubbs,
*Faster and Smaller Anonymous Credentials from Standardized Signatures*, Cryptology ePrint Archive, Paper 2026/2615
[SG26] (a preprint; no venue stated):

  * Theorem 6.6 (2), page 58 (Published): extraction error, and adaptive soundness error (Definition H.4),
        eps_ex(t)   = 2 sqrt(k_q / 2^(8(b+e))) + 6 (t + k_q)^2 (eps^k + c' (t + k_q) / 2^(8b))     (QROM)
        eps^C_ex(t) = (t + k_q) (eps^k + c' (t + k_q) / 2^(8b))                                   (ROM)
    with c' = max(2, c) + n_J + 1 (the theorem's preamble), "digests of b bytes" and "streams of b + e bytes";
    Section 6.3 (same page): "In Parts (1), (2), (3) and (5) the adversary makes at most t hash queries".
  * Definition I.1, page 130 (Published): c = N_msg max(1, m), k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2 max(1,
    l_max)))), "the verifier makes at most k_q hash queries: one challenge-input query and one stream query per verifier
    message, one challenge-input query per branch for its final digest, and at most 1 + floor(log2(2 max(1, l_max)))
    Merkle queries per opened position".
  * Section I.1 "Hash functions" and "Merkle trees", page 131 (Published): ONE random oracle H with four disjoint domain
    parts ch, leaf, node, stream; a digest is dg(H(.)), the first 8b bits; the written-back digest dg(y_i) is "the first
    8b bits of the same stream". So b is the length of every digest the protocol writes: challenge-input keys, leaf
    and node digests, and the written-back stream prefix.

OUR FRAMING (docs/qrom-compilation.md 2.2, 2.8 B-4; Original engineering choices, the Ycash developers, 2026):
  system A: keys Keccak-256 (32 B), leaves and nodes Keccak-256 (32 B), streams SHAKE256 with a 32-byte write-back;
            the 16-byte part tags are INPUT framing (domain separation), not digest length;
  system B: keys SHA-256 (32 B), leaves and nodes BLAKE3 derive_key at 32 B output (category-1 row, MA-2'), streams
            SHAKE256 with a 32-byte write-back.
  Every digest part is 32 bytes in both systems, so b = 32 (256 bits) as in the theorem, with no reading needed. With
  parts of unequal length the theorem would not apply as stated; taking b = the SHORTEST digest part would be an
  adaptation (unproved here) and is what `digest_bits` must then be set to.

The tree accounting (Original, the Ycash developers, 2026; REFERENCES.md O-13, O-71): a forged tree of N proofs has a
proof accepted for a false statement, so eps_tree(t) <= sum_v eps_v(t), each proof's term at its own c' and k_q. The
calculator's claim in the ROM is eps_tree(t) <= t / 2^kappa_C for every 1 <= t <= 2^kappa_C, half of it for each term
of the bound (soundness-method.md 8.5b). For the hash half:
    N c' (t + k_q)^2 / 2^(8b) <= t / 2^(kappa + 1)     for every 1 <= t <= 2^kappa.
(t + k_q)^2 / t is convex in t, so the binding t is an end point; for every row here it is t = 2^kappa. The classical
level of the hash part is the largest such kappa; per proof, N = 1. In the QROM the calculator's measure (as
spbcs.SpbcsTree) is the query count at which the term reaches 1/2: N 6 c' (t + k_q)^3 / 2^(8b) = 1/2.

Revision 10.2 (docs/lemma-tree-extraction.md revision 2, after docs/tree-extraction-referee.md): the tree's classical
hash level printed is that of Theorem TE', the hash part taken once for the tree, c'_max (t + K)^2 / 2^(8b) with K the sum
of the tree's k_q (`tree_extraction_level`), conditional on C2, K-A, K-B, T-1 (`TREE_CONDITIONS`); the per-proof union
above is printed beside it and stays the figure the proven-basis check uses. `lemma_qc_log2` is the QROM term Lemma QC
adds.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

KQ_ESTIMATED = "estimated"
KQ_REPORTED = "transcript-reported"
KQ_PROVENANCES = (KQ_ESTIMATED, KQ_REPORTED)

# The k_q guard (finding R9-4; revision 10.1, finding R10-7; Original, the Ycash developers, 2026). A row whose k_q is
# an estimate is labelled certified only if its margin covers the need's rise under a k_q above the estimate by the
# LARGER of two allowances:
#     guard(k_q) = max( log2(1 + 1.1 k_q) - log2(1 + k_q),                 a stated 10 % allowance (revision 10),
#                       log2(1 + k_q + named) - log2(1 + k_q) )             the named errors TOGETHER (revision 10.1),
# with `named` the sum of the estimate's named errors for the row's system (`KqInput.named_extra`):
#   system A: OTHER_ROUNDS twice as large (+2 x 2 x OTHER_ROUNDS = +2,048: two hash queries a message, one prover and
#             one verifier message a round) and one more Merkle level at every opened position (+q_IOP);
#   system B: one more Merkle level at every opened position (+q_IOP, padded slots included); B's message count is its
#             row budget (600 rounds), already an upper figure.
# The 10 % allowance alone covered one named error at a time but not both together (docs/rev10-referee.md R10-7: at
# A row 7 at 1/4 the two together cost 0.222 bits against a margin of 0.192). Taking the larger keeps every row the 10 %
# allowance refused and refuses, in addition, A row 7 at rate 1/4. It is still an allowance, not a bound. What supports
# a small allowance: the Merkle part of the estimate charges EVERY opened position a full path of 1 + floor(log2(2
# l_max)) queries at the LONGEST oracle (SG26 Definition I.1 as stated), an over-count for every oracle shorter than
# l_max and for every path that shares upper levels; the built verifier's count (task T-1) is expected below it there.
# The transcript-reported k_q (task T-1) replaces the estimate and the guard.
KQ_GUARD_FRACTION = 0.10


def kq_guard_bits(k_q: int, fraction: float = KQ_GUARD_FRACTION, named_extra: int = 0) -> float:
    """Bits of need a k_q above the estimate costs under every t: the larger of a `fraction` allowance and the
    named errors together (`named_extra` hash queries), log2(1 + k_q + extra) - log2(1 + k_q)."""
    frac = math.log2(1 + (1 + fraction) * k_q) - math.log2(1 + k_q)
    named = math.log2(1 + k_q + named_extra) - math.log2(1 + k_q)
    return max(frac, named)


@dataclass(frozen=True)
class KqInput:
    """k_q of one proof (SG26 Definition I.1) with its provenance: KQ_ESTIMATED (the calculator's formula on its own
    inputs, marked E) or KQ_REPORTED (the transcript module of the built verifier reports it; task T-1). `named_extra`:
    the estimate's named errors together, in hash queries (the guard; R10-7)."""

    value: int
    provenance: str = KQ_ESTIMATED
    source: str = ""
    named_extra: int = 0

    def __post_init__(self):
        if self.provenance not in KQ_PROVENANCES:
            raise ValueError(f"k_q provenance {self.provenance!r}; one of {KQ_PROVENANCES}")
        if self.value < 0:
            raise ValueError("k_q < 0")

    @property
    def estimated(self) -> bool:
        return self.provenance == KQ_ESTIMATED

    @property
    def guard(self) -> float:
        """The margin a row needs to be certified on this k_q: the guard if estimated, 0 if reported."""
        return kq_guard_bits(self.value, named_extra=self.named_extra) if self.estimated else 0.0

    def label(self) -> str:
        return f"{self.value:,} ({'E' if self.estimated else 'reported'})"


@dataclass(frozen=True)
class CInput:
    """c' of one proof (SG26 Theorem 6.6 preamble, c' = max(2, c) + n_J + 1, c = N_msg max(1, m)) with its provenance
    (finding R10-6): estimated (E: N_msg = 2 (listed rounds + OTHER_ROUNDS) in A, 2 x the row budget in B; m = 2, both
    upper figures) or transcript-reported (task T-1 reports N_msg = |J_V| + |J_P|, m and n_J)."""

    value: int
    provenance: str = KQ_ESTIMATED
    source: str = ""

    @property
    def estimated(self) -> bool:
        return self.provenance == KQ_ESTIMATED

    def label(self) -> str:
        return f"{self.value:,} ({'E' if self.estimated else 'reported'})"


class ImplausibleReport(ValueError):
    """A transcript-reported input below the structural floor the row's own shape implies (finding R10-8 (i))."""


@dataclass(frozen=True)
class KqReport:
    """One line of task T-1 (docs/decision-qrom-counting.md 7.6 item 4) for one proof SHAPE, measured at the query
    counts `queries` it was built at: the reported k_q and, when given, N_msg, m and n_J (the reported c')."""

    k_q: int
    queries: tuple[int, ...]
    source: str
    n_msg: int | None = None
    m: int | None = None
    n_j: int = 0

    @property
    def c_prime(self) -> int | None:
        if self.n_msg is None or self.m is None:
            return None
        return max(2, self.n_msg * max(1, self.m)) + self.n_j + 1


def kq_floor(listed_rounds: int, drawn_positions: int) -> int:
    """The least k_q a verifier of this shape can have (finding R10-8 (i), the referee's floor): each listed round is
    one verifier message after one prover message, each message costs two hash queries (challenge input and stream:
    2 N_msg >= 2 x 2 x listed rounds), and each drawn opened position at least a leaf query and one node query (the
    Merkle factor 1 + floor(log2(2 max(1, l_max))) >= 2)."""
    return 4 * listed_rounds + 2 * drawn_positions


def check_report(rep: KqReport, listed_rounds: int, drawn_positions: int, what: str) -> KqReport:
    """Refuse a report below the structural floors of its shape (R10-8 (i))."""
    floor = kq_floor(listed_rounds, drawn_positions)
    if rep.k_q < floor:
        raise ImplausibleReport(f"{what}: reported k_q {rep.k_q:,} is below the floor {floor:,} its shape implies (4 x "
                                f"{listed_rounds} listed rounds + 2 x {drawn_positions} drawn positions); source "
                                f"{rep.source!r}")
    if rep.n_msg is not None and rep.n_msg < 2 * listed_rounds:
        raise ImplausibleReport(f"{what}: reported N_msg {rep.n_msg:,} is below 2 x {listed_rounds} listed rounds")
    if rep.m is not None and rep.m < 1:
        raise ImplausibleReport(f"{what}: reported m {rep.m} < 1")
    if rep.n_msg is not None and rep.k_q < 2 * rep.n_msg + 2 * drawn_positions:
        raise ImplausibleReport(f"{what}: reported k_q {rep.k_q:,} is below 2 N_msg + 2 x drawn positions = "
                                f"{2 * rep.n_msg + 2 * drawn_positions:,} from its own N_msg")
    return rep


# Transcript-reported inputs (task T-1, docs/decision-qrom-counting.md 7.6), keyed by SHAPE (revision 10.1, R10-8 (ii)):
# system A ("A", row label, stack, rate) (`a_report_key`); system B ("B", kind, rate, route) (`b_report_key`). A report
# carries the query counts it was measured at; a row solved at other counts takes the estimate at its counts plus the
# reported excess over the estimate at the reported counts (provenance estimated, with the guard), so a report above the
# estimate re-solves the row (category._fixed_point, b_fixed_point, dkt26.row) instead of failing it. EMPTY: no built
# verifier reports its counts yet.
REPORTED_KQ: dict[tuple, KqReport] = {}


def a_report_key(label: str, stack: int, rate: int) -> tuple:
    return ("A", label, stack, rate)


def b_report_key(kind: str, rate: int, route: str) -> tuple:
    return ("B", kind, rate, route)


def resolve_kq(report: KqReport | None, queries: tuple[int, ...], estimate: int, estimate_at_report: int | None,
               source: str, named_extra: int) -> KqInput:
    """The row's k_q at `queries`: the report itself when measured at these counts (provenance reported, guard 0);
    else the estimate plus the report's excess over the estimate at the reported counts (estimated, guard on); else the
    estimate."""
    if report is None:
        return KqInput(estimate, KQ_ESTIMATED, source, named_extra)
    if tuple(report.queries) == tuple(queries):
        return KqInput(report.k_q, KQ_REPORTED, report.source)
    excess = max(0, report.k_q - (estimate_at_report if estimate_at_report is not None else estimate))
    return KqInput(estimate + excess, KQ_ESTIMATED,
                   f"{source}; + {excess:,} reported excess at counts {tuple(report.queries)} ({report.source})",
                   named_extra)


def _bisect(ok, lo: float = 0.0, hi: float = 600.0) -> float:
    """Largest kappa in [lo, hi] with ok(kappa) (ok monotone: true below, false above)."""
    for _ in range(200):
        mid = (lo + hi) / 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo


def classical_level(c_prime: int, k_q: int, proofs: int, digest_bits: int) -> float:
    """Largest kappa with N c' (t + k_q)^2 / 2^(8b) <= t / 2^(kappa + 1) for every 1 <= t <= 2^kappa (both end points
    checked; the left side over t is convex)."""
    base = math.log2(proofs * c_prime) - digest_bits

    def ok(k: float) -> bool:
        hi_end = base + 2 * math.log2(2.0**k + k_q) - k <= -(k + 1)
        lo_end = base + 2 * math.log2(1 + k_q) <= -(k + 1)
        return hi_end and lo_end

    return _bisect(ok)


def quantum_level(c_prime: int, k_q: int, proofs: int, digest_bits: int, query_factor: int = 1) -> float:
    """kappa with N 6 c' (f 2^kappa + k_q)^3 / 2^(8b) = 1/2 (the QROM measure of spbcs.SpbcsTree.hash)."""
    base = math.log2(proofs * 6.0 * c_prime) - digest_bits
    return _bisect(lambda k: base + 3 * math.log2(query_factor * 2.0**k + k_q) <= -1.0)


# Revision 10.2 (docs/tree-extraction-referee.md; docs/lemma-tree-extraction.md revision 2): the label every tree
# figure of Theorem TE' and Proposition TE-Q' carries. C2 is the recursion heuristic (the named event C2-VIOLATION,
# not dischargeable by a proof in the ROM); K-A, K-B the owed round-by-round knowledge soundness; T-1 the builders'
# transcript reports (domain separation across systems, H-DS, and the fit to SG26 Protocol 6.5).
TREE_CONDITIONS = "under C2, K-A, K-B, T-1"


def tree_extraction_level(c_prime_max: int, k_sum: int, digest_bits: int) -> float:
    """Theorem TE' (docs/lemma-tree-extraction.md revision 3, section 6; Original, the Ycash developers, 2026;
    revisions 1 and 2 refereed, pass with conditions, revision 3 unrefereed): the classical level of the hash part
    of the tree when the whole tree is extracted from ONE table, c'_max (t + K)^2 / 2^(8b) <= t / 2^(kappa + 1) for
    every 1 <= t <= 2^kappa, K = sum of the tree's k_q. Conditional on C2, K-A, K-B, T-1 (TREE_CONDITIONS). Revision
    10.2 prints it as the tree's classical hash level, with the per-proof union (classical_level with N proofs) beside
    it as the comparison; the proven-basis certification check keeps the union (the lower figure)."""
    return classical_level(c_prime_max, k_sum, 1, digest_bits)


def lemma_qc_log2(k_continuation: int, output_bits: int) -> float:
    """log2 of the term Lemma QC adds to Proposition TE-Q' (docs/lemma-tree-extraction.md 9, 9a; Original, the Ycash
    developers, 2026, found in referee review; refereed, pass: docs/qc-and-status-referee.md): 10 (K - k_q,r) / 2^n, n = 8(b + e) the oracle's output
    bits (here 8b, e = 0, an upper bound on the term), k_continuation = K - k_q,r the child verifiers' queries after
    the database measurement (bounded by N k_q,max)."""
    return math.log2(10 * max(1, k_continuation)) - output_bits


def digest_for_classical(kappa_c: float, c_prime: int, k_q: int, proofs: int) -> int:
    """Smallest whole-byte digest (bits) whose classical hash level of the tree reaches kappa_C."""
    for b in range(16, 129):
        if classical_level(c_prime, k_q, proofs, 8 * b) >= kappa_c - 1e-9:
            return 8 * b
    return -1


@dataclass(frozen=True)
class HashTerm:
    """The hash term of SG26 Theorem 6.6 (2) for one row: per proof (N = 1) and summed over the tree (N proofs),
    classical (ROM part, convention every t) and quantum (QROM part, as stated)."""

    c_prime: int
    k_q: int
    proofs: int
    digest_bits: int
    kappa_c: float
    kappa_q: float

    @property
    def classical_proof(self) -> float:
        return classical_level(self.c_prime, self.k_q, 1, self.digest_bits)

    @property
    def classical_tree(self) -> float:
        return classical_level(self.c_prime, self.k_q, self.proofs, self.digest_bits)

    @property
    def quantum_proof(self) -> float:
        return quantum_level(self.c_prime, self.k_q, 1, self.digest_bits)

    @property
    def quantum_tree(self) -> float:
        return quantum_level(self.c_prime, self.k_q, self.proofs, self.digest_bits)

    @property
    def classical_tree_te(self) -> float:
        """Theorem TE' (revision 10.2): the tree's hash part taken once, c' (t + N k_q)^2 / 2^(8b), at this row's c' and
        k_q for every proof of the tree. Conditional on TREE_CONDITIONS."""
        return tree_extraction_level(self.c_prime, self.proofs * self.k_q, self.digest_bits)

    @property
    def classical_margin_te(self) -> float:
        return self.classical_tree_te - self.kappa_c

    @property
    def classical_margin(self) -> float:
        """Per-proof union tree level minus kappa_C (the proven-basis check; the lower of the two tree figures):
        negative means the classical bound does not reach the category."""
        return self.classical_tree - self.kappa_c

    @property
    def quantum_margin(self) -> float:
        return self.quantum_tree - self.kappa_q

    @property
    def digest_needed(self) -> int:
        """Smallest whole-byte digest at which the proven classical hash part of the tree reaches kappa_C."""
        return digest_for_classical(self.kappa_c, self.c_prime, self.k_q, self.proofs)

    def cells(self) -> str:
        return (f"{self.classical_proof:.2f} / {self.classical_tree:.2f} | {self.quantum_proof:.2f} / "
                f"{self.quantum_tree:.2f}")


# The basis on which the CLASSICAL hash part is judged (Profile.hash_basis):
#   HASH_ATTACK_RULE (default, the project's recorded basis: soundness-method.md 8.5b "category 1 then rests on
#     condition H's attack rule"; decision-security-category.md 3.5 "keep the attack rule ... state it as the basis"):
#     the digest is at least 2 kappa_C bits (generic collision search costs 2^kappa_C calls; NIST's category-2/4
#     benchmarks), and the proven classical level of the hash part is PRINTED, not required;
#   HASH_PROVEN: the proven classical level of the tree's hash part must reach kappa_C (no 256-bit row meets it).
# The QUANTUM hash part is always required proven (condition Q, the full sum of Theorem 6.6 (2)).
HASH_ATTACK_RULE = "attack-rule"
HASH_PROVEN = "proven"
HASH_BASES = (HASH_ATTACK_RULE, HASH_PROVEN)
