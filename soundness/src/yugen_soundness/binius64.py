"""System B on Binius64: FRI-Binius / BaseFold under unique decoding, SHA-256, GF(2^128) at the pin.

Read (read-only) from `yugen-proof-b2`: `docs/parameters.md` (sections 1 to 3: what is built, the
target, the leaf verifier and the bundle circuits, all measurements used below) and
`docs/zero-knowledge.md` (section 1: the two zero-knowledge round oracles, the pad of `q`
coordinates, the mask claim and its challenge `gamma`, the wrapper's masked check).

Round list of one proof (one verifier message each), errors in units of q = |F|:

  inner      the inner protocol's worst algebraic round: the univariate-skip round of the AND
             check, degree at most 127 (parameters.md 2a.4)                             127 / q
  wrapper    (zero-knowledge leaf only) IronSpartan's blend challenge of the masked
             multilinear-extension check (zero-knowledge.md M9)                      1 / q
  mask       (zero-knowledge leaf only) gamma of the batched opening's mask claim, the
             line M + gamma w (zero-knowledge.md M4)                                 (n + 1) / q
  fold.j     one BaseFold round per folded variable: sumcheck degree 2 and the fold's
             proximity                                                                (n_j + 2) / q
  query      gamma test queries at the code's rate, followed through every layer     ((1 + rho) / 2)^gamma

Every other round of the proof (AND / MUL checks, shift reduction, public input, ring switch,
the wrapper's sumcheck rounds) has error at most a small degree over q; they count in k through
`shipping.OTHER_ROUNDS` (512, the upper figure parameters.md section 2 uses too), not one by one.

Sources and status (docs/soundness-method.md, "Sources"):

  query     ((1 + rho) / 2)^gamma: the code computes exactly this count (S: iop/src/fri/common.rs:456-460,
            `ceil(96 / -log2((1 + rho) / 2))`); the bound is Diamond-Posen, "Polylogarithmic Proofs for
            Multilinears over Binary Towers", ePrint 2024/504, proof of Proposition 4.24 and Section 5.2
            equation (42): accept with at most (1/2 + 1/(2 * 2^R))^gamma (read 2026-11-19; unique
            decoding). The same bound is our Lemma 4 / Lemma 5 for W-I (zk-wi-soundness.md, P).
  fold      n_j / q per folded variable: an upper bound of DP24's per-oracle bad-event mass
            theta |S^(i+theta)| / |L| (Proposition 4.21, from Diamond-Gruen's tensor gap, its Theorem 2.4)
            and of its sumcheck term 2 / |L| per round (proof of Theorem 4.17): CONFIRMED as terms. DP24
            proves soundness of the whole protocol (Definition 2.9), not round-by-round soundness; the
            round-by-round form is Haboeck, "Basefold in the List Decoding Regime", ePrint 2024/1571,
            Theorems 1 and 6 (Sections 5, 6.2, 6.3; written for the list-decoding regime, said there to
            carry over "verbatim" to unique decoding): CITATION-AUDIT C-12.
  mask      (n + 1) / q: BCIKS20 Theorem 4.1 on the line M + gamma w, and one root for the mask claim;
            the argument of W-M (zk-wi-soundness.md section 9, P) applies word for word to the
            Blueprint's Protocol 7.1 as built: our argument, UNCONFIRMED against the Blueprint's proof.
  wrapper   1 / q: zk-wi-soundness.md Lemma 6 (P) for a mask fixed before its blend challenge.
  inner     d / q for a round polynomial of degree d: Schwartz-Zippel (standard). The fixed GF(2^8)
            zerocheck coordinates add no term only if every caller's constraint values are in GF(2)
            (parameters.md task A-3, open): UNCONFIRMED.
"""

# Citation audit 2026-11-19, for the round list in the docstring above:
#   mask  (n + 1) / q: the same two events as the proof sketch of Theorem 4.2 in Diamond, "Zero-Knowledge
#         Polynomial Commitment in Binary Fields", ePrint 2025/1015 (read): BCIKS20 Theorem 4.1 on the
#         combination and one bad challenge for the claim. The paper states no explicit error; the count
#         is ours. Still unconfirmed against the Blueprint's own proof.
#   query, fold: Diamond-Posen, ePrint 2024/504 (read 2026-11-19): see the docstring; C-12.
#   pad:  q opened symbols uniform for a pad on coefficients 0..q: Chiesa, Fenzi, Weissenberg, ePrint
#         2026/391 (revision of 2026-11-16), Lemma 3.29.


from __future__ import annotations

import math
from dataclasses import dataclass, field

from .bounds import log2_sum
from .compose import FsParams, Round

# Fold arities of the opening as built (S: parameters.md 3.2, "[4, 4, 3, 3]", chosen for proof size).
ARITIES = (4, 4, 3, 3)
FOLDED = sum(ARITIES)  # 14 variables; the terminal codeword has 2^(L - 14) elements
INNER_SKIP_DEGREE = 127  # 64 coefficients sent, degree under 128; unconditional (parameters.md 2a.3, A-3 closed)


@dataclass
class Tree:
    """One Merkle tree a query opens: `depth` levels, `leaf_bytes` per opened leaf."""

    depth: int
    leaf_bytes: int


@dataclass
class B64Proof:
    """One Binius64 proof: its committed round oracles and the batched BaseFold opening.

    zk:   the leaf proof: round oracle 0 (pad segment and inner trace) and round oracle 1 (the
          wrapper's private segment and mask table), each committed as the interleaving of Enc(M_r)
          and Enc(w_r) with a 256-bit salt per leaf (zero-knowledge.md M1, M1a); then four fold
          trees (arities 4, 4, 3, 3) and the terminal codeword.
    plain: a node proof (transparent): one oracle whose commitment tree holds the first fold's 16
          elements per leaf (S: bench output "FRI plain: oracles 3 index_bits 15" for the 2^16-element
          wallet trace at rate 1/8), then three fold trees (4, 3, 3) and the terminal codeword.
    """

    name: str
    zk: bool
    oracle_logs: list[int]  # log2 of each round oracle's length in GF(2^128) elements (largest last)
    log_inv_rate: int
    field_bits: int = 256
    queries: int = 1
    oracle_bytes: list[int] = field(default_factory=lambda: [16, 16])  # bytes per symbol of each round oracle
    ext_bytes: int = 32  # folded codewords and the terminal codeword are in the challenge field
    salt_bytes: int = 32
    mask_bytes: list[int] | None = None  # bytes per symbol of each round oracle's mask; None: the oracle's own
    fs: FsParams = field(default_factory=lambda: FsParams(digest_bits=256))
    arities: tuple[int, ...] = ARITIES  # as built; `best_arities` chooses them for size at other shapes

    @property
    def rho(self) -> float:
        return 2.0 ** -self.log_inv_rate

    @property
    def log_codeword(self) -> int:
        return max(self.oracle_logs) + self.log_inv_rate

    def trees(self) -> list[Tree]:
        L = self.log_codeword
        out = []
        if self.zk:
            masks = self.mask_bytes or self.oracle_bytes
            for lg, b, mb in zip(self.oracle_logs, self.oracle_bytes, masks):
                out.append(Tree(lg + self.log_inv_rate, b + mb + self.salt_bytes))
            depth = L
            for a in self.arities:
                depth -= a
                out.append(Tree(depth, (2**a) * self.ext_bytes))
        else:
            b = self.oracle_bytes[0]
            depth = L - self.arities[0]
            out.append(Tree(depth, (2 ** self.arities[0]) * b))
            for a in self.arities[1:]:
                depth -= a
                out.append(Tree(depth, (2**a) * self.ext_bytes))
        return out

    @property
    def terminal(self) -> int:
        return 2 ** max(0, self.log_codeword - sum(self.arities))


def rounds(p: B64Proof) -> list[Round]:
    fb = p.field_bits
    out = [Round("inner.skip", math.log2(INNER_SKIP_DEGREE) - fb)]
    if p.zk:
        out.append(Round("wrapper.blend", -fb))
        out.append(Round("mask", math.log2(2.0**p.log_codeword + 1) - fb))
    m = max(p.oracle_logs)  # variables of the largest oracle, folded one per round
    for j in range(m):
        out.append(Round(f"fold.{j}", log2_sum([1 - fb, p.log_codeword - j - fb])))
    out.append(Round("query", p.queries * math.log2((1 + p.rho) / 2)))
    return out


def solve(p: B64Proof, target) -> B64Proof:
    """Smallest query count meeting `target` (a TreeTarget-like object with need_bits); every algebraic
    round must meet it at the field size, else ValueError."""
    rs = rounds(p)
    need = target.need_bits(len(rs), p.fs)
    for r in rs:
        if r.name != "query" and r.effective_bits < need:
            raise ValueError(f"{p.name}: round {r.name} gives {r.effective_bits:.1f} < {need:.1f} bits")
    p.queries = math.ceil(need / -math.log2((1 + p.rho) / 2))
    return p


def min_field_bits(p: B64Proof, target) -> int:
    """Smallest challenge field at which every algebraic round of `p` meets the target."""
    rs = rounds(p)
    need = target.need_bits(len(rs), p.fs)
    worst = max(r.error_log2 + p.field_bits for r in rs if r.name != "query")
    return math.ceil(need + worst)


def best_arities(p: B64Proof) -> B64Proof:
    """Fold arities of 4 then 3 (the built pattern), as many of each as give the smallest proof; the
    terminal codeword keeps at least the rate's 2^r symbols. Arities are a prover-side configuration
    of the opening (S: chosen for proof size at the pin); they do not change any soundness term."""
    best, best_size = p, math.inf
    for a4 in range(0, 9):
        for a3 in range(0, 9):
            ar = (4,) * a4 + (3,) * a3
            if not ar or sum(ar) > max(p.oracle_logs):
                continue
            p.arities = ar
            s = size_model(p)
            if s < best_size:
                best, best_size = ar, s
    p.arities = best
    return p


def _distinct(n_nodes: float, q: int) -> float:
    """Expected number of distinct nodes among q uniform picks of n_nodes."""
    if n_nodes <= 0:
        return 0.0
    return n_nodes * (1.0 - (1.0 - 1.0 / n_nodes) ** q)


def tree_bytes(t: Tree, q: int, digest_bytes: int) -> float:
    """Expected bytes of q openings of one tree with a cap at depth ceil(log2 q) (S: parameters.md 3.2,
    "the native rule ceil(log2 q)"): the distinct leaves, the sibling digests below the cap, the cap."""
    cap = min(t.depth, math.ceil(math.log2(max(q, 1))))
    leaves = _distinct(2.0**t.depth, q)
    sib = 0.0
    for lvl in range(t.depth, cap, -1):  # nodes at level lvl have parents at lvl - 1
        u = _distinct(2.0**lvl, q)
        par = _distinct(2.0 ** (lvl - 1), q)
        sib += max(0.0, 2 * par - u)
    return leaves * t.leaf_bytes + sib * digest_bytes + (2**cap) * digest_bytes


def size_model(p: B64Proof) -> float:
    """Merkle openings, caps and the terminal codeword (bytes); everything else is `other`."""
    h = p.fs.digest_bits // 8
    return sum(tree_bytes(t, p.queries, h) for t in p.trees()) + p.terminal * p.ext_bytes


# --- measured anchors (M), yugen-proof-b2 docs/parameters.md -------------------------------------

# The zero-knowledge wallet leaf, committed derivation (section 3.2): round oracle 0 2^17 elements,
# round oracle 1 (wrapper private segment, 2^20 constraints) 2^20; GF(2^128); (log inverse rate,
# queries at the pin's 96 bits, proof bytes).
LEAF_ZK_COMMITTED = [(1, 232, 534_736), (3, 116, 354_288)]
LEAF_ORACLES_COMMITTED = [17, 20]
# The pin's layout (derived wires public): both round oracles 2^17.
LEAF_ZK_PIN = [(1, 232, 409_136), (3, 116, 283_216)]
LEAF_ORACLES_PIN = [17, 17]
# Transparent node proofs (section 3.3; heavy-20261119-b.txt): (log2 elements of the oracle,
# log inverse rate, queries, proof bytes). Rows of the circuit: K = 1 5,479,552 (2^23 words, 2^22
# GF(2^128) elements); K = 2 and 3 10.96 M and 16.43 M (2^24 words); merge A = 1 4.14 M rows, 4,206,205 words (2^23).
NODE_ANCHORS = [(22, 3, 116, 275_488), (22, 1, 232, 406_176), (23, 1, 232, 444_208), (23, 1, 232, 444_256),
                (22, 3, 116, 275_488)]
# Rows of the circuit that verifies one zero-knowledge leaf (rate 1/8, 116 queries; 3.2), and of a
# merge slot over a child at rate 1/8 (116 queries) and 1/2 (232 queries) (3.3). 95 % of the AND rows
# are SHA-256 in Merkle checks: rows are taken proportional to the child's query count (E).
LEAF_SLOT_ROWS = (5_477_612, 116)
MERGE_SLOT_ROWS = {3: (4_141_026, 116), 1: (6_551_994, 232)}
WORDS_PER_ROW = 5_542_996 / 5_479_552  # committed 64-bit words per row (K = 1: const + inout + witness + internal)


def _leaf(rate: int, q: int, layout: str = "committed", field_bits: int = 128) -> B64Proof:
    logs = LEAF_ORACLES_COMMITTED if layout == "committed" else LEAF_ORACLES_PIN
    e = field_bits // 8
    # at 256 bits the wrapper witness (round oracle 1) is in the extension (parameters.md task A-4)
    ob = [16, 16] if field_bits == 128 else [16, e]
    return B64Proof("B leaf", True, list(logs), rate, field_bits, q, ob, e)


def _node(m: int, rate: int, q: int, field_bits: int = 128) -> B64Proof:
    return B64Proof("B node", False, [m], rate, field_bits, q, [16], field_bits // 8)


def calibration() -> dict:
    """Additive `other` bytes (sumcheck messages, claims, public words) at 128-bit challenges, fitted
    as the mean residual of the model at the measured points; and the error at each point."""
    out = {}
    for label, pts, logs_layout in (("leaf_committed", LEAF_ZK_COMMITTED, "committed"), ("leaf_pin", LEAF_ZK_PIN, "pin")):
        res = [m - size_model(_leaf(r, q, logs_layout)) for r, q, m in pts]
        x = sum(res) / len(res)
        out[label] = x
        out[label + "_errors"] = {f"rate 1/{2 ** r}": (size_model(_leaf(r, q, logs_layout)) + x) / m - 1 for r, q, m in pts}
    res = [b - size_model(_node(m, r, q)) for m, r, q, b in NODE_ANCHORS]
    x = sum(res) / len(res)
    out["node"] = x
    out["node_errors"] = {f"2^{m} elements, rate 1/{2 ** r}": (size_model(_node(m, r, q)) + x) / b - 1 for m, r, q, b in NODE_ANCHORS}
    return out


_CAL: dict | None = None


def cal() -> dict:
    global _CAL
    if _CAL is None:
        _CAL = calibration()
    return _CAL


@dataclass
class B64Row:
    layer: str
    rate: int
    proof: B64Proof
    statement: str
    need: float
    field_min: int
    size: float  # bytes (E): model + other x (field_bits / 128)
    child_rows: float  # rows of one slot that verifies this proof in its parent (E)
    rounds_count: int


def _depths(p: B64Proof) -> int:
    return sum(t.depth for t in p.trees())


def slot_rows(child: B64Proof) -> float:
    """Rows of the circuit slot that verifies `child` (E): a measured slot scaled by queries and by
    the summed depth of the trees each query walks (95 % of the rows are SHA-256 in Merkle checks)."""
    if child.zk:
        rows, q = LEAF_SLOT_ROWS
        anchor = _leaf(3, q)
    else:
        rate = 3 if child.log_inv_rate >= 3 else 1
        rows, q = MERGE_SLOT_ROWS[rate]
        anchor = _node(22, rate, q)
    return rows * (child.queries / q) * (_depths(child) / _depths(anchor))


def leaf_row(target, rate: int, layout: str = "committed") -> B64Row:
    p = solve(_leaf(rate, 1, layout, 256), target)  # the built arities 4, 4, 3, 3 (terminal 2^(L - 14))
    other = cal()["leaf_" + layout] * 2  # sumcheck messages and claims double with the field (E)
    rows = slot_rows(p)
    rs = rounds(p)
    return B64Row("leaf", rate, p, f"2^{LEAF_ORACLES_COMMITTED[0] if layout == 'committed' else 17} + "
                  f"2^{max(p.oracle_logs)} elements (M)", target.need_bits(len(rs), p.fs), min_field_bits(p, target),
                  size_model(p) + other, rows, len(rs))


def node_row(layer: str, target, rate: int, children: int, child: B64Row) -> B64Row:
    """A sub-bundle (children = leaves) or a merge (children = node proofs) at full arity."""
    rows = children * child.child_rows
    words = rows * WORDS_PER_ROW
    m = max(1, math.ceil(math.log2(words))) - 1  # two 64-bit words per GF(2^128) element
    p = best_arities(solve(_node(m, rate, 1, 256), target))
    rs = rounds(p)
    other = cal()["node"] * 2
    return B64Row(layer, rate, p, f"{rows / 1e6:,.0f} M rows: 2^{m} elements (E)", target.need_bits(len(rs), p.fs),
                  min_field_bits(p, target), size_model(p) + other, slot_rows(p), len(rs))


# =====================================================================================================
# Revision 4 (2026-11-19): the round structure counted from the code, and the mixed-field variant
# =====================================================================================================
#
# Sources: yugen-proof-b2 docs/parameters.md section 2a.4 (the census of sampled challenges on real
# proofs and the five corrections to this file) and docs/binius-extension-challenges.md (the
# mixed-field variant: trace and first-oracle alphabet in L = GF(2^128), every challenge in
# K = GF(2^256)). Every error below is in units of 1 / |K|, K the CHALLENGE field; the alphabet of
# a committed oracle enters sizes only (BCIKS20 Theorem 4.1 over K with the domain in L, Remark 1.2).


@dataclass(frozen=True)
class Shape:
    """One proof's shape in the symbols of parameters.md 2a.4 (all log2)."""

    a: int  # padded AND rows
    w: int  # hidden-segment words
    p: int  # public-segment elements
    v: int  # variables of the opening (largest round oracle)
    b: int = 0  # padded BMUL rows (0: none)
    z: int = 0  # padded ZERO rows
    o: int = 0  # ceil(log2(round commitments))
    c: int = 0  # wrapper multiplication constraints (zero-knowledge leaf only)
    zk: bool = False
    kappa: int = 8  # coordinates of each ring-switch challenge r'' (7 at the pin, 8 with 256-bit challenges, 7 in form F)
    relations: int = 1  # relations batched by the opening's mu (4 for the zero-knowledge leaf)

    @property
    def n_star(self) -> int:
        return max(self.a, self.b)


def k_of(sh: Shape) -> int:
    """Verifier challenges of one proof, the query round included (parameters.md 2a.4):
    k = (2 n* - 1) + 2 b + max(0, z - n*) + (41 + w) + (kappa + p) + kappa + (1 + [zk] + o + v) + [zk](2 c + 2) + 1."""
    n = sh.n_star
    return ((sh.a - 3) + 2 + n) + 2 * sh.b + max(0, sh.z - n) + (41 + sh.w) + (sh.kappa + sh.p) + sh.kappa \
        + (1 + int(sh.zk) + sh.o + sh.v) + (2 * sh.c + 2 if sh.zk else 0) + 1


def rounds_counted(sh: Shape, log_inv_rate: int, queries: int, field_bits: int) -> list[Round]:
    """Every verifier message of one proof with its round-by-round error (parameters.md 2a.4 table).
    `len(rounds_counted(sh, ...)) == k_of(sh)`."""
    fb = field_bits
    t = lambda name, num: Round(name, math.log2(num) - fb)
    n = sh.n_star
    out: list[Round] = []
    out += [t(f"binmul.zc{i}", 1) for i in range(sh.b)] + [t(f"binmul.sc{i}", 3) for i in range(sh.b)]
    out += [t(f"bitand.zc{i}", 1) for i in range(sh.a - 3)]  # three coordinates are fixed (2a.3: no term)
    out += [t("bitand.skip", INNER_SKIP_DEGREE), t("bitand.batch", 10)]
    out += [t(f"bitand.sc{i}", 3) for i in range(n)]
    out += [t(f"zero.ext{i}", 1) for i in range(max(0, sh.z - n))]
    out += [t(f"shift.batch{i}", 1) for i in range(4)] + [t(f"shift.sc{i}", 2) for i in range(37 + sh.w)]
    out += [t(f"public.rs{i}", 1) for i in range(sh.kappa)] + [t(f"public.sc{i}", 2) for i in range(sh.p)]
    out += [t(f"ringswitch.{i}", 1) for i in range(sh.kappa)]
    if sh.zk:
        out += [t(f"wrapper.zc{i}", 1) for i in range(sh.c)] + [t("wrapper.blend", 1)]
        out += [t(f"wrapper.sc{i}", 3) for i in range(sh.c)] + [t("wrapper.lambda", 2)]
    L = sh.v + log_inv_rate
    out.append(t("opening.mu", max(1, sh.relations - 1)))
    if sh.zk:
        out.append(t("opening.gamma", 2.0**L + 1))
    out += [t(f"opening.idx{i}", 2.0**L + 2) for i in range(sh.o)]
    out += [t(f"fold.{j}", 2.0 ** (L - j) + 2) for j in range(sh.v)]
    out.append(Round("query", queries * math.log2((1 + 2.0**-log_inv_rate) / 2)))
    assert len(out) == k_of(sh)
    return out


def k_batching(level: int, field_bits: int = 256) -> int:
    """Challenges of a node's in-circuit batching transcript (parameters.md 2a.4, C-3): level 0 four
    shapes with 161 sumcheck rounds (168 challenges, M at the pin's field; about 12 more for the larger
    wrapper shapes at 256 bits), each level above one wiring shape of at most 78 variables (79)."""
    return 168 + (12 if field_bits > 128 else 0) + 79 * level


def batching_rounds(level: int, field_bits: int = 256, claims: int = 16) -> list[Round]:
    """The batching transcript's rounds: per shape alpha ((K - 1)/|F|), n sumcheck rounds (2), mu (2).
    Only the count and the largest term matter; the rounds are listed as sumcheck rounds of error 2
    and one alpha per shape."""
    k = k_batching(level, field_bits)
    shapes = 4 + level
    return [Round(f"batch.alpha{i}", math.log2(max(1, claims - 1)) - field_bits) for i in range(shapes)] + \
        [Round(f"batch.sc{i}", 1 - field_bits) for i in range(k - shapes)]


def tree_need(base, groups: list[tuple[int, float]], fs: FsParams | None = None) -> float:
    """Bits every round must reach for a tree whose proofs are `groups` = [(count, k)]: the union
    bound sum_i (1 + k_i) 2^-e <= 2^-(kappa + 1) (parameters.md 2a.2; soundness-method.md 8.5b), and the
    QROM condition 2 kappa_Q + 1 + log2 6 + log2 N."""
    fs = fs or FsParams(digest_bits=256)
    total = sum(n * (1 + k) for n, k in groups)
    proofs = sum(n for n, _ in groups)
    c = base.classical_chain + 1.0 + math.log2(total)
    q = 2.0 * base.quantum_chain + 1.0 + fs.qrom_c1_log2 + math.log2(proofs)
    return max(c, q, base.attack_bits)


def queries_for(need: float, log_inv_rate: int) -> int:
    return math.ceil(need / -math.log2((1 + 2.0**-log_inv_rate) / 2))


# --- variants ------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Variant:
    """Where each object lives. `challenge`: bits of the challenge field; `alphabet`: bytes of a
    symbol of the trace oracle; `wrapper_alphabet`, `mask`: bytes of a symbol of the wrapper's oracle
    and of every fold mask; `cell_words`: 64-bit words packed in one trace element."""

    name: str
    challenge: int
    alphabet: int
    wrapper_alphabet: int
    mask: int
    cell_words: int
    rs_rows: int  # elements of one ring-switch message
    kappa: int  # coordinates of r''
    leaf_oracles: tuple[int, int]  # log2 of the wallet leaf's two round oracles (pin layout)
    leaf_c: int  # log2 wrapper constraints of the wallet leaf
    status: str  # M measured, E estimated


# The wallet leaf's wrapper (pin layout, derived wires public). Measured (M, parameters.md 2a.5):
# GF(2^128): 2^19 constraints, 98,354 private wires (2^17), 594,439 derived; GF(2^256): 2^21, 393,008
# (2^19), 2,105,223. Model fitted to both (docs/binius-extension-challenges.md 5.3): a transposition of a
# rows x cols bit matrix on private values costs 3 rows cols constraints and private wires; on public
# values (the public-input check's operand, 2 p of them) rows cols constraints and 2 rows cols derived
# wires. 18 x (2 x 128^2 + 256) = 594,432 and 16 x (2 x 256^2 + 512) = 2,105,344 against the measured
# derived counts; 6 x 128^2 = 98,304 and 6 x 256^2 = 393,216 against the measured private counts.
PIN128 = Variant("pin: all in GF(2^128)", 128, 16, 16, 16, 2, 128, 7, (17, 17), 19, "M")
ALL256 = Variant("all in GF(2^256) (as built, cat1)", 256, 32, 32, 32, 4, 256, 8, (16, 19), 21, "M")
ALL256_W1 = Variant("all in GF(2^256), public transpositions direct (W-1)", 256, 32, 32, 32, 4, 256, 8, (16, 19), 19, "E")
MIXED_T = Variant("mixed, ring switch form T, wrapper as is", 256, 16, 32, 32, 2, 128, 8, (17, 18), 21, "E")
MIXED_T_W1 = Variant("mixed, form T, public transpositions direct (W-1)", 256, 16, 32, 32, 2, 128, 8, (17, 18), 18, "E")
MIXED_F = Variant("mixed, ring switch form F", 256, 16, 32, 32, 2, 128, 7, (17, 17), 17, "E")
VARIANTS = (PIN128, ALL256, ALL256_W1, MIXED_T, MIXED_T_W1, MIXED_F)


def wrapper_counts(v: Variant, p_public: int) -> dict:
    """Constraints and private wires of the wallet leaf's wrapper from the transposition model (E; the
    two measured variants are reproduced, see the comment above)."""
    kb = v.challenge  # columns: GF(2)-coordinates of a challenge-field element
    if v is MIXED_F:
        private = 2 * v.rs_rows * (2 * 128)  # per message element: 127 squarings, 128 products, 1 constant product
        return {"constraints": private, "private": private, "derived": 0}
    private = 2 * 3 * v.rs_rows * kb
    direct = v in (ALL256_W1, MIXED_T_W1)
    public = 0 if direct else 2 * p_public * (kb * kb + 2 * kb)
    return {"constraints": private + (0 if direct else 2 * p_public * kb * kb), "private": private,
            "derived": 0 if direct else 2 * p_public * (2 * kb * kb + 2 * kb), "public_constraints": public}


def leaf_shape(v: Variant) -> Shape:
    """The wallet leaf (zero knowledge): a = 17, w = 17 (M); p = 9 with two-word cells, 8 with four."""
    return Shape(a=17, w=17, p=9 if v.cell_words == 2 else 8, v=max(v.leaf_oracles), o=1, c=v.leaf_c, zk=True,
                 kappa=v.kappa, relations=4)


def node_shape(log_and_rows: int, v: Variant, log_bmul: int | None = None, p: int = 10) -> Shape:
    """A transparent node circuit of 2^log_and_rows AND rows (the slot circuit: a = 23, b = 20, w = 23,
    p = 10, v = 21 with four-word cells; parameters.md 2a.4)."""
    b = log_and_rows - 3 if log_bmul is None else log_bmul
    words = log_and_rows  # hidden words about one a row (M: 5,542,996 words for 5,479,552 rows)
    return Shape(a=log_and_rows, b=b, w=words, p=p, v=words - (1 if v.cell_words == 2 else 2), kappa=v.kappa)


def leaf_proof(v: Variant, rate: int, queries: int) -> B64Proof:
    e = v.challenge // 8
    return B64Proof(f"B leaf, {v.name}", True, list(v.leaf_oracles), rate, v.challenge, queries,
                    [v.alphabet, v.wrapper_alphabet], e, 32, mask_bytes=[v.mask, v.mask])


def node_proof(v: Variant, log_words: int, rate: int, queries: int) -> B64Proof:
    m = log_words - (1 if v.cell_words == 2 else 2)
    return B64Proof(f"B node, {v.name}", False, [m], rate, v.challenge, queries, [v.alphabet], v.challenge // 8)


# Measured proofs of the 256-bit build (M, parameters.md 2a.5): the wallet leaf, pin layout,
# (log inverse rate, queries, bytes); and the slot circuit (2^23 words) as one transparent proof.
LEAF_ALL256 = [(1, 368, 928_416), (2, 225, 685_248), (3, 184, 633_280), (4, 168, 638_688)]
NODE_ALL256 = (23, 3, 184, 538_272)
NODE_PIN_SAME_CIRCUIT = (23, 3, 116, 275_536)


def cal256() -> dict:
    """Non-opening bytes at 256-bit challenges, fitted to the measured proofs of the all-GF(2^256)
    build (mean residual of the opening model), and the model's error at each point."""
    res = [m - size_model(leaf_proof(ALL256, r, q)) for r, q, m in LEAF_ALL256]
    leaf = sum(res) / len(res)
    lw, r, q, m = NODE_ALL256
    pn = node_proof(ALL256, lw, r, q)
    pn.arities = ARITIES
    node = m - size_model(pn)
    return {"leaf": leaf, "node": node,
            "leaf_errors": {f"rate 1/{2 ** r}": (size_model(leaf_proof(ALL256, r, q)) + leaf) / m - 1 for r, q, m in LEAF_ALL256}}


def other_bytes(v: Variant, leaf: bool) -> float:
    """Non-opening bytes (E). At 128 bits: the fit to the pin's proofs. At 256 bits: the fit to the
    measured all-GF(2^256) proofs, with each ring-switch message at its own length (`rs_rows`
    elements of 32 bytes; 256 in the measured build)."""
    if v.challenge == 128:
        return cal()["leaf_pin" if leaf else "node"]
    c = cal256()
    n_rs = 2 if leaf else 1
    return c["leaf" if leaf else "node"] - n_rs * (256 - v.rs_rows) * 32


def leaf_size(v: Variant, rate: int, queries: int) -> float:
    return size_model(leaf_proof(v, rate, queries)) + other_bytes(v, True)


def node_size(v: Variant, log_words: int, rate: int, queries: int, arities=None) -> float:
    p = node_proof(v, log_words, rate, queries)
    p = best_arities(p) if arities is None else p
    if arities is not None:
        p.arities = arities
    return size_model(p) + other_bytes(v, False)


def hash_blocks(p: B64Proof) -> float:
    """SHA-256 compressions one query costs a verifier (E): per tree, the path (one a level) and the
    opened leaf (64-byte blocks with padding). The in-circuit verifier's AND rows follow this count
    (95 % of them are Merkle checks, parameters.md 3.2)."""
    return sum(t.depth + math.ceil((t.leaf_bytes + 9) / 64) for t in p.trees())


# The leaf-verifier slot at the pin row (M, parameters.md 2a.6): 4.23 M AND rows, 0.79 M BMUL rows,
# 116 queries, pin layout.
LEAF_SLOT_PIN = (4_230_000, 790_000, 116)


def leaf_slot_rows(v: Variant, rate: int, queries: int) -> tuple[float, float]:
    """(AND rows, BMUL rows) of the slot that verifies a leaf (E): AND rows by queries and hash
    compressions a query against the pin row; BMUL rows times 4 for a 256-bit challenge field (one
    product of GhashSq256b is 4 BMUL rows, parameters.md 2a.7)."""
    and_pin, bmul_pin, q_pin = LEAF_SLOT_PIN
    ref = hash_blocks(leaf_proof(PIN128, 3, q_pin)) * q_pin
    return and_pin * hash_blocks(leaf_proof(v, rate, queries)) * queries / ref, bmul_pin * (4 if v.challenge > 128 else 1)


# --- alternative (d): the Johnson regime with the proven BCIKS20 bound -----------------------------------

def johnson_bciks(log_msg: int, log_inv_rate: int, need: float, field_bits: int = 256, m: float = 10.0) -> dict:
    """Queries and the fold round's bits at proximity 1 - sqrt(rho) - eta, eta = sqrt(rho) / (2 m), with
    BCIKS20 Theorem 1.2's Johnson-case error (k + 1)^2 / ((2 min(eta, sqrt(rho)/20))^7 q) (confirmed as a
    statement). Haboeck, ePrint 2024/1571, Theorem 6 (row-batched FRI-Binius, round-by-round, list
    decoding, theta = 1 - (1 + 1/(2m)) sqrt(rho)) gives the same query count (query error (1 - theta)^s)
    and a fold error (Theorem 3) about one bit smaller than this one at m = 10; it does not cover
    Binius64's eq-batched ring switch, its zero-knowledge mask round or lifted oracles of unequal size
    (CITATION-AUDIT C-11): a candidate, not a row."""
    rho = 2.0**-log_inv_rate
    eta = math.sqrt(rho) / (2.0 * m)
    per_query = -math.log2(math.sqrt(rho) + eta)
    from .bounds import pg_johnson_bciks
    fold_bits = -pg_johnson_bciks(float(log_msg), rho, eta, field_bits)
    return {"queries": math.ceil(need / per_query), "bits_per_query": per_query, "fold_bits": fold_bits,
            "list_log2": -math.log2(2.0 * eta * math.sqrt(rho)), "meets": fold_bits >= need}
