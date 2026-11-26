"""Revisions 8 and 9: system B's opening rows with every error term of the Johnson-regime (DKT26-route) analysis.

REVISION 9 (2026-11-19, the lead architect's ruling on condition C-2): every row's need is taken under the counting
convention EVERY t (Sharp, Grubbs, ePrint 2026/2615, Theorem 6.6 (2) with Definitions H.3, H.4: "for every t and every
(t, 0)-adversary"), kappa_C + 1 + log2 N + log2(1 + k_q) at the row's own k_q, solved to its least fixed point:
192 (unique decoding, 1/8), 111 / 82 (Johnson m = 10, 1/8 / 1/16), 235 (node 1/4, unique decoding), 171 (node 1/4,
Johnson, arithmetic only: R8-3). The revision-8 counts (184 / 107 / 80 / 225 / 165) are kept only behind
convention=T_GE_KQ and labelled NON_DEFAULT. Also: the terminal dimension keyed by row (R8-7), unrecorded shapes at
terminal 0 with Lemma 3.3 and the D-term bound (R8-4), validated m and log_terminal_dim (R8-10, R8-11), no Johnson
row above the unique-decoding threshold (R8-12).

Part of Yugen. Condition C-3 of `docs/johnson-row-referee-2.md` (section 7): the terms of
`docs/binius-johnson-row.md` (revision 2, sections 2.2, 3, 4.1, 5.4, 6, 8) inside the calculator proper,
reproducing the referee's section 5.1, with the proximity-gap parameters and the list size explicit, a
hard refusal outside the regime the cited theorems cover, and the node row at rate 1/4. The side script
`johnson-row/rowcalc.py` computes the same rows with the closed form (39); this module computes the exact
count (33)-(34) and, with `closed=True`, the closed form, which must agree with `rowcalc.py` to the bit
(`tests/test_revision8.py`).

STATUS OF THE ROWS (printed with every row; `Row8.status`):
  * unique decoding (184 queries at rate 1/8; the node at rate 1/4, 225 queries): **certified**; no
    Johnson-regime statement is used.
  * Johnson regime, DKT26 route (107 at rate 1/8, 80 at rate 1/16, m = 10; the node at rate 1/4):
    **CANDIDATE, resting on DKT26, a preprint**. They rest on Q. Dao, S. D. Kominers, J. Thaler,
    "Reed-Solomon Codes Beyond Johnson: Efficient Decoding and Smaller Cryptographic Proofs", Cryptology
    ePrint Archive, Paper 2026/2056 (copy of 2026-11-02, a preprint, not peer reviewed) [DKT26]. The
    label `DKT26_LABEL` is part of every such row's status, also if the lead architect accepts the rows
    (`DKT26_ACCEPTED`): the calculator never prints a Johnson row as certified without it.

SOURCES (each formula also cited at its function):
  [DKT26] Theorem 4.4: parameters (36) m, t; (37) B_jet, B_Z, lambda_agr; list bound (38); exceptional
          count B_cf = E^(1)_ord(D, A, n; B_jet, B_Z) (39), with (33) E_ord and Psi_D, (34) L = D + 1
          (Section 4.2); the closed form B_cf < 8 n t^3 / (3 rho_-) (39), proved in Section B.3;
          hypotheses: any field, distinct points, 1 <= D <= n - 2, a = sqrt(rho_-) + eta_0 <= 1, A = ceil(a n).
          Lemma 3.3 (6): constant codes (message dimension 1), floor(l C(n, 2) / (A - 1)) for A >= 2, list
          size floor(n / A). Lemma 6.5 and Corollary 6.6: the bounds hold for interleaved words of every
          width, error E/q with the challenge uniform in the code's field.
  [ACFY24] G. Arnon, A. Chiesa, G. Fenzi, E. Yogev, "WHIR", ePrint 2024/1586, Lemma 4.10 with
          [BCIKS20] Ben-Sasson, Carmon, Ishai, Kopparty, Saraf (ECCC TR20-083) Theorem 4.1: unique-decoding
          line MCA with n bad challenges on any evaluation set (binius-johnson-row.md 2.2 F2, 6).
  [Hab-LDR] U. Haboeck, "Basefold in the List Decoding Regime", ePrint 2024/1571, Lemma 3: one query
          accepts a doomed final state with probability at most 1 - theta = (1 + 1/(2m)) sqrt(rho)
          (Johnson) or (1 + rho)/2 (unique decoding; also [DP24] Diamond, Posen, ePrint 2024/504,
          Proposition 4.24).
  [SG26]  C. Sharp, P. Grubbs, ePrint 2026/2615, Theorem 6.6 (2) and Definition I.1 (k_q): the per-round
          need of the tree (soundness-method.md 8.5b) and the open convention Q-5 (condition C-2).
  The per-round errors themselves are the lemmas of binius-johnson-row.md revision 2: Lemma U (list
  times per-oracle error), J1 (ring switch, 8 B_list), J2 (mask, N_line + B_list), F (index and X
  folds, N_line + 2 B_list), UD (unique decoding): REFERENCES.md O-17, O-19 (Adapted / Original, the Ycash
  developers, 2026; the second referee: hold). The D-term (yugen-proof-b2 parameters.md 11, terminal check
  by evaluation of the first coset, n_f (2^r - 1) / |K|) is the builder's bound, charged here although the
  second referee shows it is 0 against the analysed protocol (johnson-row-referee-2.md 6.3).

Provenance of this module: code Original (the Ycash developers, 2026); every formula Published at the place
cited; the assembly per round follows binius-johnson-row.md (Adapted / Original as above). Bits are
-log2(error) = field_bits - log2(count of bad challenges).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from math import comb, isqrt

REVISION = 9
FIELD_BITS = 256
TREE_PROOFS = 20_000
BUDGET_K = 600
PIOP_WORST = 127  # univariate-skip round, the largest Schwartz-Zippel count of the PIOP (binius-johnson-row.md 8.1)
KAPPA = 8  # ring-switch coordinates, form T (binius-extension-challenges.md Theorem 1)
J_CLAIMS = 4  # relations batched by the leaf's opening; the batching term is J - 1
LOG_MSG = {"leaf": 19, "node": 28}  # message log2 of the largest common lifted level: CAPS, not the built shapes
# (binius-johnson-row.md 8.1: leaf |E_l| <= 2^22 and node 2^31 at rate 1/8, i.e. 2^19 and 2^28 elements at every
# rate; the build's BR-4 lines open at index bits 21 / 22, finding R8-6). The caps are on the safe side: B_cf grows
# linearly in n at fixed rate and the list bound (38) is uniform in n, so a row computed at the cap holds at every
# smaller line; the slack of the weakest term (57 to 62 bits) covers openings up to about 2^88 points.

# log_terminal_dim as built (yugen-proof-b2 docs/parameters.md 14.7, condition C-4, asserted by the build's
# tests `lift_levels_are_fixed_by_the_circuit_shape` and `recbench qslot`): no committed level of message
# dimension 1. The node at rate 1/4 is not recorded there: 1 is taken (the smallest value Theorem 4.4 covers
# without Lemma 3.3; the weakest term, the first X fold, does not depend on it) and marked in the output.
# Revision 9 (finding R8-7): keyed by (kind, rate, route), since a terminal dimension is a property of a built shape:
# the 184-query unique-decoding build has n_f = 7 (terminal codeword of 1,024 symbols, parameters.md 11.3: 49 = 7 x 7),
# the 107 / 80-query Johnson builds 6 / 4 (leaf) and 6 / 5 (node; a rate-1/16 node of index bits 22 has 4, the larger
# value is charged: the D-term grows with n_f, and the extra fold line at the smaller value is a shorter, stronger line).
# These are the builds at the revision-8 counts; the revision-9 counts have no build yet.
TERMINAL_AS_BUILT = {("leaf", 3, "ud"): 7, ("node", 3, "ud"): 7,
                     ("leaf", 3, "dkt"): 6, ("leaf", 4, "dkt"): 4, ("node", 3, "dkt"): 6, ("node", 4, "dkt"): 5}
# Revision 9 (finding R8-4): an unrecorded shape (the node at rate 1/4) folds down to message dimension 1 with DKT26
# Lemma 3.3's term (the case with the most fold lines, covered by both theorems) and is charged the D-term bound
# log_msg (2^r - 1) (the largest n_f); both are printed.
TERMINAL_ASSUMED = 0

CERTIFIED = ("certified (unique decoding; no Johnson-regime statement used; every t, Sharp-Grubbs ePrint 2026/2615 "
             "Theorem 6.6 (2))")  # the stem; the printed label names the hash basis (`certified_label`, R10-1)
HASH_BASIS_WORDS = {"attack-rule": "classical hash part on condition H's attack rule", "proven": "every term proven"}


def certified_label(hash_basis: str) -> str:
    """Revision 10.1 (R10-1): the positive label always names the basis on which it was computed."""
    return CERTIFIED[:-1] + f"; {HASH_BASIS_WORDS[hash_basis]})"
EVERY_T, T_GE_KQ = "every-t", "t-ge-kq"  # = category.EVERY_T, category.T_GE_KQ (revision 9)
NON_DEFAULT = "non-default convention (t >= k_q), not certified"
FIXED_NEED = "fixed need (passed in), not certified"  # revision 10, finding R9-2
ARITH_ONLY = "arithmetic only: no lemma stated or refereed at this rate, no build"  # finding R8-3 (rate 1/4 Johnson)
DKT26_LABEL = "rests on DKT26 (Dao, Kominers, Thaler, ePrint 2026/2056), a PREPRINT"
DKT26_ACCEPTED = False  # set only by the lead architect's decision after conditions C-1 to C-7


def dkt26_status() -> str:
    """The status of every Johnson-regime row: it always carries DKT26_LABEL."""
    if DKT26_ACCEPTED:
        return f"certified by the lead architect's decision; {DKT26_LABEL}"
    return f"CANDIDATE, not certified; {DKT26_LABEL}"


class OutsideRegime(ValueError):
    """Hard refusal: a row or a line outside the hypotheses of the theorem the term is cited to."""


def need(classical_chain: float = 128.0, proofs: int = TREE_PROOFS, k: int = BUDGET_K) -> float:
    """The book's per-round bits for the tree, c + 1 + log2(N (1 + k)) (soundness-method.md 8.5b; 152.519 at category
    1). NON-DEFAULT since revision 9: for the spBCS transcript it holds only when condition C is read for adversaries
    making at least k_q hash queries (T_GE_KQ). The default need is `every_t_need`."""
    return classical_chain + 1.0 + math.log2(proofs * (1 + k))


def _ceil_sqrt(v: Fraction) -> int:
    """Smallest integer c >= 0 with c^2 >= v (exact)."""
    c = isqrt(v.numerator // v.denominator)
    while c * c < v:
        c += 1
    while c > 0 and (c - 1) ** 2 >= v:
        c -= 1
    return c


def agreement(n: int, k: int, m: int) -> int:
    """A = ceil((1 + 1/(2m)) sqrt(rho) n), rho = k/n, computed exactly: the Johnson threshold of
    binius-johnson-row.md 2.2 (a = (1 + 1/(2m)) sqrt(rho))."""
    return _ceil_sqrt(Fraction(2 * m + 1, 2 * m) ** 2 * k * n)


# --- one line: the proximity-gap parameters of DKT26 Theorem 4.4 ------------------------------------------------


@dataclass(frozen=True)
class Line:
    """One received line on n points for RS[n, k] at our threshold A, with every parameter of DKT26 Theorem 4.4.

    m_thm, t: (36) with eta_0 = A/n - sqrt(rho_-) (the largest a with ceil(a n) = A), so m_thm <= m;
    b_jet, b_z, lam: (37); psi: Psi_D(B_jet) of (33); count: B_cf = E^(1)_ord(D, A, n; B_jet, B_Z) by (33)-(34);
    closed: 8 n t^3 / (3 rho_-) by (39) with t = m + 1/2 (our m, as rowcalc.dkt_count; an upper bound);
    list_exact: n (A - D) / (A^2 - n D) ((38), second term); list_size = min(B_jet, floor(list_exact)) (38)."""

    n: int
    k: int
    m: int
    A: int
    m_thm: int
    t: Fraction
    b_jet: int
    b_z: int
    psi: int
    lam: Fraction
    count: Fraction
    closed: float
    list_exact: Fraction
    list_size: int
    lemma: str = "DKT26 Theorem 4.4 (33)-(34), (39); Lemma 6.5, Corollary 6.6 for width"

    @property
    def D(self) -> int:
        return self.k - 1

    @property
    def count_log2(self) -> float:
        return math.log2(self.count)

    @property
    def lean_count(self) -> Fraction:
        """Revision 10 (finding L-2 of docs/rev9-and-lean-referee.md): ArkLib's `johnsonExceptionCount` at `6aa8b6fe`
        (ArkLib/Data/CodingTheory/HiddenDerivative/Parameters/Johnson/FiniteBounds.lean, read for this revision),
        (2 mu - 1) h + theta (h + mu + 4 D mu h) + (n - D - 1) mu, with mu = johnsonMu = B_jet, h = johnsonH = B_Z,
        theta = johnsonTheta = lambda_agr, at eta = A/n - sqrt(D/n) (johnsonM = m_thm). It is the count of the
        machine-checked statement (docs/arklib-lean-check.md 3.2, `check_F2_johnson_interleaved`): coarser than the
        exact (33)-(34) (4 D mu h in place of h Psi_D), so its bits are a little lower. Published (ArkLib)."""
        mu, h, D = self.b_jet, self.b_z, self.D
        return (2 * mu - 1) * h + self.lam * (h + mu + 4 * D * mu * h) + (self.n - D - 1) * mu

    @property
    def lean_count_log2(self) -> float:
        return math.log2(self.lean_count)

    @property
    def closed_log2(self) -> float:
        return math.log2(self.closed)


def _theorem_m(n: int, D: int, A: int) -> int:
    """(36): m = max(ceil(sqrt(rho_-) / (2 eta_0)), 3) with a = A/n, eta_0 = a - sqrt(rho_-), exactly:
    the smallest c >= 1 with 2 c (a - x) >= x, x = sqrt(D/n), i.e. (2 c a)^2 >= x^2 (1 + 2 c)^2."""
    a, x2 = Fraction(A, n), Fraction(D, n)
    c = 1
    while (2 * c * a) ** 2 < x2 * (1 + 2 * c) ** 2:
        c += 1
    return max(c, 3)


def check_m(m) -> int:
    """Finding R8-10: m must be an integer >= 3 (not a bool, not a float), refused otherwise."""
    if m is None:
        raise OutsideRegime("the Johnson regime needs m")
    if isinstance(m, bool) or not isinstance(m, int):
        raise OutsideRegime(f"m = {m!r}: the Johnson parameter must be an integer >= 3")
    return m


def line(n: int, k: int, m: int) -> Line:
    """The DKT26 Theorem 4.4 line at length n, message dimension k, our Johnson parameter m. Refuses (hard)
    everything outside the theorem's hypotheses and the document's regime."""
    check_m(m)
    if m < 3:
        raise OutsideRegime(f"m = {m} < 3: outside the Johnson regime of binius-johnson-row.md 2.2 (and DKT26 (36) m >= 3)")
    if k < 2:
        raise OutsideRegime(f"message dimension k = {k} (D = 0) at n = {n}: DKT26 Theorem 4.4 excludes D = 0; "
                            "a level of message dimension 1 needs DKT26 Lemma 3.3 (dimension_one='lemma33')")
    D = k - 1
    if D > n - 2:
        raise OutsideRegime(f"D = {D} > n - 2 = {n - 2}: outside DKT26 Theorem 4.4's hypothesis 1 <= D <= n - 2")
    A = agreement(n, k, m)
    if A > n:
        raise OutsideRegime(f"A = {A} > n = {n}: a > 1, outside DKT26 Theorem 4.4 (a = sqrt(rho_-) + eta_0 <= 1)")
    if A <= D or A * A <= n * D:
        raise OutsideRegime(f"A = {A}: not above the Johnson radius (A^2 > n D and A > D needed by (33), (38))")
    m_thm = _theorem_m(n, D, A)
    t = Fraction(2 * m_thm + 1, 2)
    b_jet = _ceil_sqrt(t * t * Fraction(n, D)) - 1  # (37): ceil(t / sqrt(rho_-)) - 1
    tz = t * t * n / (3 * D)
    b_z = -((-tz.numerator) // tz.denominator) - 1  # (37): ceil(t^2 / (3 rho_-)) - 1
    if b_jet < 1:
        raise OutsideRegime(f"B_jet = {b_jet} < 1: outside Lemma 4.3's hypothesis")
    psi = 1 + (2 * D - 1) * (2 * b_jet - 1) + 2 * max(b_jet - 2 * D - 1, 0)  # Psi_D(B), before (33)
    lam = Fraction(n - D, A - D)  # (n - L + 1)/(A - L + 1) at L = D + 1, (34); lambda_agr of (37)
    count = (2 * b_jet - 1) * b_z + lam * (b_jet + b_z * psi) + (n - D - 1) * b_jet  # (33) at l = 1, L = D + 1
    tm = m + 0.5
    closed = 8.0 * n * tm**3 / (3.0 * (k / n - 1.0 / n))  # (39) with our m (rowcalc.dkt_count; rho_- = rho - 1/n)
    lst = Fraction(n * (A - D), A * A - n * D)
    return Line(n, k, m, A, m_thm, t, b_jet, b_z, psi, lam, count, closed, lst, min(b_jet, math.floor(lst)))


def lemma33_count(n: int, A: int, ell: int = 1) -> int:
    """DKT26 Lemma 3.3 (6): a constant code (k = 1) has line exceptional count floor(l C(n, 2) / (A - 1)) for A >= 2
    (l C(n, 2) for A = 1), any field; its list size is floor(n / A)."""
    if not 1 <= A <= n:
        raise OutsideRegime(f"Lemma 3.3 needs 1 <= A <= n (A = {A}, n = {n})")
    return ell * comb(n, 2) if A == 1 else (ell * comb(n, 2)) // (A - 1)


def tolerated_exceptional_log2(need_bits: float, roots_times_list: float, field_bits: int = FIELD_BITS) -> float:
    """log2 of the largest line count E with (E + roots_times_list)/|K| still meeting the need: the qualitative
    requirement of binius-johnson-row.md 8.4 (2^103.48 at category 1 with 2 B_list = 38)."""
    return math.log2(2.0 ** (field_bits - need_bits) - roots_times_list)


# --- the terms of one proof -------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Shape:
    """One proof's opening shape: kind 'leaf' (mask round, one index round, J = 4 claims) or 'node' (one oracle,
    no mask, no index round), log2 inverse rate, message log2 of the largest lifted level, terminal dimension."""

    kind: str
    rate: int
    log_msg: int
    log_terminal_dim: int
    terminal_recorded: bool

    @property
    def log_e(self) -> int:
        return self.log_msg + self.rate

    @property
    def mask(self) -> bool:
        return self.kind == "leaf"

    @property
    def index_rounds(self) -> int:
        return 1 if self.kind == "leaf" else 0


def shape(kind: str, rate: int, log_terminal_dim: int | None = None, route: str = "dkt") -> Shape:
    """The shape of one proof. log_terminal_dim: given, the build's (TERMINAL_AS_BUILT by kind, rate, route), or for
    an unrecorded shape TERMINAL_ASSUMED = 0 (R8-4). Refused outside 0 <= log_terminal_dim <= log_msg (R8-11)."""
    if kind not in LOG_MSG:
        raise ValueError(kind)
    if log_terminal_dim is not None:
        if isinstance(log_terminal_dim, bool) or not isinstance(log_terminal_dim, int) \
                or not 0 <= log_terminal_dim <= LOG_MSG[kind]:
            raise OutsideRegime(f"log_terminal_dim = {log_terminal_dim!r}: outside 0 .. {LOG_MSG[kind]} (the message "
                                f"log2 of the {kind}'s largest level)")
        return Shape(kind, rate, LOG_MSG[kind], log_terminal_dim, True)
    t = TERMINAL_AS_BUILT.get((kind, rate, route))
    return Shape(kind, rate, LOG_MSG[kind], TERMINAL_ASSUMED if t is None else t, t is not None)


@dataclass(frozen=True)
class Term:
    name: str
    count: float  # bad challenges out of |K|
    source: str
    field_bits: int = FIELD_BITS
    closed: float | None = None  # the same term with the closed form (39) in place of (33), Johnson only
    lean: float | None = None  # revision 10 (L-2): the same term with ArkLib's machine-checked count, Johnson only

    @property
    def lean_bits(self) -> float | None:
        return None if self.lean is None else self.field_bits - math.log2(self.lean)

    @property
    def bits(self) -> float:
        return self.field_bits - math.log2(self.count)

    @property
    def closed_bits(self) -> float | None:
        return None if self.closed is None else self.field_bits - math.log2(self.closed)


def _ud_count(n: int) -> int:
    """Unique-decoding line MCA: n bad challenges ([ACFY24] Lemma 4.10 with [BCIKS20] Theorem 4.1; width by
    [DKT26] Lemma 6.5): binius-johnson-row.md 2.2 F2, Lemma UD (6)."""
    return n


def lines_of(sh: Shape, m: int) -> list[tuple[str, int, int]]:
    """(name, n, k) of every line the opening tests: mask and index rounds at the full lifted level, the i-th X fold
    on the half domain n / 2^i at message dimension k / 2^i (binius-johnson-row.md 5.4, Lemma F)."""
    n, k = 2**sh.log_e, 2**sh.log_msg
    out = []
    if sh.mask:
        out.append(("mask fold gamma", n, k))
    out += [(f"index round {j}", n, k) for j in range(sh.index_rounds)]
    for i in range(1, sh.log_msg - sh.log_terminal_dim + 1):
        out.append((f"X fold {i}", n >> i, k >> i))
    return out


def list_size(route: str, sh: Shape, m: int | None) -> int:
    """B_list: 1 in unique decoding; in the Johnson regime the largest list bound (38) over the proof's lines
    (binius-johnson-row.md 2.2 F1': 19 at rate 1/8, 31 at rate 1/16, m = 10)."""
    if route == "ud":
        return 1
    sizes = []
    lines = lines_of(sh, m) or [("whole level", 2**sh.log_e, 2**sh.log_msg)]  # no fold line: the level itself
    for _, n, k in lines:
        if k >= 2:
            sizes.append(line(n, k, m).list_size)
        else:
            sizes.append(n // agreement(n, k, m))  # Lemma 3.3: floor(n / A)
    return max(sizes)


def terms(route: str, sh: Shape, m: int | None = None, field_bits: int = FIELD_BITS,
          dimension_one: str = "refuse") -> list[Term]:
    """Every error term of one proof's rounds (binius-johnson-row.md 8.2; johnson-row-referee-2.md 5.1).

    route: 'ud' (unique decoding) or 'dkt' (Johnson regime, DKT26 route). 'haboeck' is refused: that route is not
    available (binius-johnson-row.md 0.1, gaps G-1, G-3, G-6). dimension_one: a fold whose line has message
    dimension 1 is refused ('refuse') unless DKT26 Lemma 3.3's term is added ('lemma33')."""
    if route == "haboeck":
        raise OutsideRegime("Haboeck's route is not available for system B as built (binius-johnson-row.md 0.1: "
                            "gaps G-1, G-3, G-6); only 'ud' and 'dkt' are computed")
    if route not in ("ud", "dkt"):
        raise ValueError(route)
    if route == "dkt":
        check_m(m)
    if dimension_one not in ("refuse", "lemma33"):
        raise ValueError(dimension_one)
    if not sh.terminal_recorded:
        dimension_one = "lemma33"  # R8-4: an unrecorded shape folds to dimension 1, with Lemma 3.3's term
    lst = list_size(route, sh, m)
    lemma_u = "Lemma U (binius-johnson-row.md 2.3): list size x Schwartz-Zippel"
    out = [Term("PIOP round (worst: skip, 127 B_list)", lst * PIOP_WORST, lemma_u, field_bits),
           Term("ring switch (each, 8 B_list)", lst * KAPPA, "Lemma J1 (3): Theorem 1 x list", field_bits),
           Term(f"claim batching ({J_CLAIMS - 1} B_list)", lst * (J_CLAIMS - 1), lemma_u, field_bits)]
    for name, n, k in lines_of(sh, m):
        roots = 1 if name.startswith("mask") else 2  # J2: one root a member; F: two (degree-2 Gamma)
        lemma = "Lemma J2 (4.1)" if roots == 1 else "Lemma F (5.4)"
        if route == "ud":
            out.append(Term(name, _ud_count(n) + roots * lst,
                            f"{lemma}, unique decoding: n ([ACFY24] Lemma 4.10 + [BCIKS20] Thm 4.1) + {roots}", field_bits))
        elif k >= 2:
            ln = line(n, k, m)
            out.append(Term(name, float(ln.count) + roots * lst,
                            f"{lemma}: DKT26 Thm 4.4 (33)-(34) at n = 2^{n.bit_length() - 1} + {roots} B_list",
                            field_bits, ln.closed + roots * lst, float(ln.lean_count) + roots * lst))
        elif dimension_one == "lemma33":
            c = lemma33_count(n, agreement(n, k, m))
            out.append(Term(name + " (message dimension 1)", c + roots * lst,
                            f"{lemma}: DKT26 Lemma 3.3 (6) + {roots} B_list", field_bits, c + roots * lst))
        else:
            raise OutsideRegime(f"{sh.kind} at rate 1/{2 ** sh.rate}: {name} has message dimension 1 "
                                f"(log_terminal_dim = {sh.log_terminal_dim}); DKT26 Theorem 4.4 excludes D = 0. "
                                "Add DKT26 Lemma 3.3's term (dimension_one='lemma33') or choose log_terminal_dim >= 1")
    if sh.log_terminal_dim >= 1:
        out.append(Term(f"terminal sumcheck round (each of {sh.log_terminal_dim}, degree 2)", 2,
                        "Schwartz-Zippel; levels below the terminal checked against the codeword in the clear (5.4)",
                        field_bits))
    nf = sh.log_terminal_dim if sh.terminal_recorded else sh.log_msg  # R8-4: the bound log_msg (2^r - 1) if unrecorded
    if nf >= 1:
        how = "builder's bound" if sh.terminal_recorded else "bound log_msg (2^r - 1): terminal not recorded"
        out.append(Term(f"D-term, whole proof (n_f (2^r - 1) = {nf} x {2 ** sh.rate - 1}; {how})",
                        nf * (2**sh.rate - 1),
                        "yugen-proof-b2 parameters.md 11 (Schwartz-Zippel); 0 against the analysed protocol, "
                        "johnson-row-referee-2.md 6.3", field_bits))
    return out


def per_query_bits(route: str, m: int | None, rate: int) -> float:
    """One query: Johnson -log2((1 + 1/(2m)) sqrt(rho)), unique decoding -log2((1 + rho)/2) ([Hab-LDR] Lemma 3;
    [DP24] Proposition 4.24)."""
    rho = 2.0**-rate
    if route == "ud":
        return -math.log2((1 + rho) / 2)
    return -math.log2((1 + 1 / (2 * m)) * math.sqrt(rho))


# --- rows -------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Row8:
    name: str
    route: str
    rate: int
    m: int | None
    need: float
    queries: int
    per_query: float
    shapes: tuple[Shape, ...]
    proof_terms: tuple[tuple[str, tuple[Term, ...]], ...]  # (kind, terms) per shape
    field_bits: int = FIELD_BITS
    note: str = ""
    certified_count: int = field(default=0)  # the smallest count meeting the need
    convention: str = EVERY_T
    extra_kq: int = 0  # SG26 Definition I.1 k_q at the row's count (category.b_counts, padded group slots included)
    category: int = 1
    need_fixed: bool = False  # revision 10 (R9-2): the need was passed in (`need_bits`), so the row is never certified
    c_prime: int = 0  # SG26 Theorem 6.6 c' at the row's count (category.b_counts)
    digest_bits: int = 256
    hash_basis: str = "attack-rule"  # revision 10.1 (R10-1): the profile's classical hash basis
    kq_input: object = None  # revision 10.1 (R10-8 (iii)): hashterm.KqInput from category.b_kq (T-1 reports read)
    c_input: object = None  # revision 10.1 (R10-6): hashterm.CInput

    @property
    def kq(self):
        from . import hashterm as ht

        if self.kq_input is not None:
            return self.kq_input
        return ht.KqInput(self.extra_kq, ht.KQ_ESTIMATED, "category.b_counts (E)")

    @property
    def hash(self):
        """The hash term of SG26 Theorem 6.6 (2) at this row (revision 10, R9-1)."""
        from . import category as C, hashterm as ht

        return ht.HashTerm(self.c_prime, self.extra_kq, TREE_PROOFS, self.digest_bits, C.kappa_classical(self.category),
                           C.kappa_quantum(self.category))

    @property
    def margin(self) -> float:
        return min(self.query_margin, self.slack)

    @property
    def checks(self) -> dict[str, bool]:
        """Every condition of the label "certified", computed by the SAME function as category.Row.checks (revision
        10.1, R10-1), on the profile's hash basis; plus the route (unique decoding, or a Johnson row only by the lead
        architect's decision DKT26_ACCEPTED) and the rate-1/4 Johnson row's arithmetic-only status."""
        from . import category as C

        ch = C.certification_checks(convention=self.convention, need_own_kq=not self.need_fixed,
                                    unique_decoding=self.route == "ud" or DKT26_ACCEPTED,
                                    margin=self.margin if self.meets else min(self.margin, -1.0), kq=self.kq,
                                    hash_term=self.hash, digest_bits=self.digest_bits, category=self.category,
                                    hash_basis=self.hash_basis)
        ch["not arithmetic only (R8-3)"] = not self.arithmetic_only
        return ch

    @property
    def certified(self) -> bool:
        """Computed (revision 10, R9-2; revision 10.1, R10-1): all of `checks`."""
        return all(self.checks.values())

    @property
    def arithmetic_only(self) -> bool:
        """R8-3: the Johnson row at rate 1/4 has no lemma stated or refereed at that rate and no build."""
        return self.route == "dkt" and self.rate == 2

    @property
    def status(self) -> str:
        """CERTIFIED only for a unique-decoding row that meets its need under the default convention (every t);
        every Johnson row carries DKT26_LABEL; the rate-1/4 Johnson row ARITH_ONLY; a row under T_GE_KQ NON_DEFAULT."""
        if not self.meets:
            st = "DOES NOT MEET the need" + ("" if self.route == "ud" else f"; {DKT26_LABEL}")
        elif self.need_fixed:
            st = FIXED_NEED + ("" if self.route == "ud" else f"; {DKT26_LABEL}")
        elif self.convention == T_GE_KQ:
            st = "unique decoding" if self.route == "ud" else dkt26_status()
        elif self.route == "ud":
            failing = [k for k, v in self.checks.items() if not v]
            if not failing:
                st = certified_label(self.hash_basis)
            elif failing == ["k_q guard"]:
                st = (f"meets on an estimated k_q by {self.margin:+.4f} bits, under the k_q guard {self.kq.guard:.4f}: "
                      "not certified until task T-1 reports k_q")
            else:
                st = "not certified: fails " + ", ".join(failing)
        else:
            st = dkt26_status()
        if self.arithmetic_only:
            st += f"; {ARITH_ONLY}"
        if self.convention == T_GE_KQ:
            st = f"{NON_DEFAULT}; " + st
        return st

    @property
    def list_size(self) -> int:
        return max(list_size(self.route, sh, self.m) for sh in self.shapes)

    @property
    def query_bits(self) -> float:
        return self.queries * self.per_query

    @property
    def query_margin(self) -> float:
        return self.query_bits - self.need

    @property
    def all_terms(self) -> list[tuple[str, Term]]:
        return [(k, t) for k, ts in self.proof_terms for t in ts]

    @property
    def weakest(self) -> tuple[str, Term]:
        return min(self.all_terms, key=lambda kt: kt[1].bits)

    @property
    def slack(self) -> float:
        """Bits of the weakest algebraic round above the need."""
        return self.weakest[1].bits - self.need

    @property
    def meets(self) -> bool:
        return self.query_bits >= self.need and self.weakest[1].bits >= self.need


def _profile(category: int, profile=None):
    from . import category as C

    return profile if profile is not None else C.PROFILES[category]


def every_t_need(q: int, rate: int, category: int = 1, profile=None, route: str = "ud",
                 kinds: tuple[str, ...] = ("leaf", "node")) -> tuple[float, int]:
    """(need, k_q) at q queries under the default convention (revision 9): kappa_C + 1 + log2 N + log2(1 + k_q), k_q of
    SG26 Definition I.1 for a system-B proof of q queries (category.b_kq: b_counts, six trees, l_max of a 2^30-row
    node, or a T-1 report for the row's kinds; revision 10.1, R10-8 (iii))."""
    from . import category as C

    p = _profile(category, profile)
    kq = C.b_kq(q, rate, p, "dkt" if route == "dkt" else "ud", kinds).value
    return C.every_t_need(p.category, kq), kq


def row(name: str, route: str, rate: int, m: int | None = None, kinds: tuple[str, ...] = ("leaf", "node"),
        need_bits: float | None = None, field_bits: int = FIELD_BITS, queries: int | None = None,
        terminal: dict[str, int] | None = None, dimension_one: str = "refuse", note: str = "",
        convention: str | None = None, category: int | None = None, profile=None,
        hash_basis: str | None = None) -> Row8:
    """One row. Need: `need_bits` if given (fixed); else under EVERY_T (default) the least fixed point q with
    q * per_query >= every_t_need(q); under T_GE_KQ the book need (revision 8's counts, labelled NON_DEFAULT)."""
    if route not in ("ud", "dkt", "haboeck"):
        raise ValueError(route)
    if route == "dkt":
        check_m(m)
        rho = 2.0**-rate
        if (1 + 1 / (2 * m)) * math.sqrt(rho) >= (1 + rho) / 2:  # R8-12: no Johnson row above the UD threshold
            raise OutsideRegime(f"m = {m}, rate 1/{2 ** rate}: the Johnson threshold (1 + 1/(2m)) sqrt(rho) is not below "
                                "the unique-decoding threshold (1 + rho)/2")
    cat = category if category is not None else (profile.category if profile is not None else 1)
    conv = convention or (profile.convention if profile is not None else EVERY_T)
    if conv not in (EVERY_T, T_GE_KQ):
        raise ValueError(conv)
    pq = per_query_bits(route, m, rate) if route != "haboeck" else 0.0
    shapes = tuple(shape(k, rate, (terminal or {}).get(k), "dkt" if route == "dkt" else "ud") for k in kinds)
    pt = tuple((sh.kind, tuple(terms(route, sh, m, field_bits, dimension_one))) for sh in shapes)
    book = need(classical_chain=_kappa(cat)) if cat != 1 or profile is not None else need()
    if need_bits is not None:
        nd, q_min = need_bits, math.ceil(need_bits / pq)
        kq = every_t_need(queries or q_min, rate, cat, profile, route, kinds)[1]
    elif conv == T_GE_KQ:
        nd, q_min = book, math.ceil(book / pq)
        kq = every_t_need(queries or q_min, rate, cat, profile, route, kinds)[1]
    else:
        q = math.ceil(book / pq)
        for _ in range(64):
            nd, kq = every_t_need(q, rate, cat, profile, route, kinds)
            q2 = math.ceil(nd / pq - 1e-12)
            if q2 <= q:
                break
            q = q2
        q_min = q
        if queries is not None:
            nd, kq = every_t_need(queries, rate, cat, profile, route, kinds)
    from . import category as C

    pp = _profile(cat, profile)
    qq = q_min if queries is None else queries
    rt = "dkt" if route == "dkt" else "ud"
    kin = C.b_kq(qq, rate, pp, rt, kinds)
    cin = C.b_c_input(qq, rate, pp, rt, kinds)
    hb = hash_basis or (profile.hash_basis if profile is not None else "attack-rule")
    return Row8(name, route, rate, m, nd, qq, pq, shapes, pt, field_bits, note, q_min,
                conv, kq, cat, need_bits is not None, cin.value, pp.digest_bits, hb, kin, cin)


def _kappa(cat: int) -> float:
    from . import category as C

    return C.kappa_classical(cat)


def rows(need_bits: float | None = None, field_bits: int = FIELD_BITS, built: bool = True,
         convention: str = EVERY_T, category: int = 1, hash_basis: str = "attack-rule") -> list[Row8]:
    """The rows of the referee's condition C-3: the unique-decoding row at rate 1/8, the candidate rows at rates 1/8 and
    1/16 (m = 10), and system B's node at rate 1/4 (unique-decoding count and Johnson count; with `built`, the built
    count 226: a category-1 build figure, left out at other categories)."""
    kw = dict(need_bits=need_bits, field_bits=field_bits, convention=convention, category=category,
              hash_basis=hash_basis)
    out = [
        row("B leaf + node, unique decoding, 1/8", "ud", 3, **kw),
        row("B leaf + node, Johnson m = 10, 1/8", "dkt", 3, 10, **kw),
        row("B leaf + node, Johnson m = 10, 1/16", "dkt", 4, 10, **kw),
        row("B node, unique decoding, 1/4", "ud", 2, kinds=("node",), **kw),
        row("B node, Johnson m = 10, 1/4", "dkt", 2, 10, kinds=("node",), **kw),
    ]
    if built:
        out.insert(4, row("B node, unique decoding, 1/4, as built", "ud", 2, kinds=("node",), queries=226,
                          note="built count (yugen-proof-b2 params::CAT1_QUERIES)", **kw))
    return out


# --- condition C-2 (decided 2026-11-19: every t) -------------------------------------------------------------------


def every_t_count(r: Row8, category: int | None = None) -> tuple[int, int, float]:
    """Query count under EVERY_T (the default since revision 9; qrom-compilation.md 6.2 reading (b);
    johnson-row-referee-2.md 5.4; soundness-rev8-referee.md 7). Returns (count, k_q, need)."""
    cat = r.category if category is None else category
    q = row("x", r.route, r.rate, r.m, kinds=tuple(sh.kind for sh in r.shapes), field_bits=r.field_bits,
            convention=EVERY_T, category=cat)
    return q.certified_count, q.extra_kq, q.need


def book_count(r: Row8, category: int | None = None) -> int:
    """Query count under T_GE_KQ (the revision 1 to 8 counts; NON-DEFAULT)."""
    cat = r.category if category is None else category
    return row("x", r.route, r.rate, r.m, kinds=tuple(sh.kind for sh in r.shapes), field_bits=r.field_bits,
               convention=T_GE_KQ, category=cat).certified_count


# --- cross-check against the documents ---------------------------------------------------------------------------

DOC_FIGURES_REV8 = (  # (row name, figure, source): the revision-8 (T_GE_KQ) figures of the documents
    ("B leaf + node, unique decoding, 1/8", 184, "binius-johnson-row.md 0.4; referee-2 5.3"),
    ("B leaf + node, Johnson m = 10, 1/8", 107, "binius-johnson-row.md 0.4; referee-2 5.1"),
    ("B leaf + node, Johnson m = 10, 1/16", 80, "binius-johnson-row.md 0.4; referee-2 5.1"),
    ("B node, unique decoding, 1/4", 225, "referee-2 0, 5.2 (the count found there under the book need)"),
    ("B node, unique decoding, 1/4, as built", 226, "yugen-proof-b2 parameters.md 14.7 (built)"),
)
DOC_FIGURES = (  # revision 9 (EVERY_T): the referee's section 7 table (soundness-rev8-referee.md), 192/111/82/235/171
    ("B leaf + node, unique decoding, 1/8", 192, "soundness-rev8-referee.md 7 (reading (b))"),
    ("B leaf + node, Johnson m = 10, 1/8", 111, "soundness-rev8-referee.md 7; johnson-row-referee-2.md 5.4"),
    ("B leaf + node, Johnson m = 10, 1/16", 82, "soundness-rev8-referee.md 7; johnson-row-referee-2.md 5.4"),
    ("B node, unique decoding, 1/4", 235, "soundness-rev8-referee.md 7; johnson-row-referee-2.md 5.4"),
    ("B node, Johnson m = 10, 1/4", 171, "soundness-rev8-referee.md 7 (arithmetic only, R8-3)"),
)


def cross_check(rs: list[Row8]) -> list[tuple[str, int, int, str, bool]]:
    """(row, documented count, calculator's figure, source, agree). A certified or candidate count agrees when it is
    the calculator's smallest count meeting the need; a built count agrees when it is the row's count and meets."""
    by = {r.name: r for r in rs}
    figs = DOC_FIGURES_REV8 if rs and rs[0].convention == T_GE_KQ else DOC_FIGURES
    out = []
    for name, fig, src in figs:
        r = by[name]
        if r.note:  # a built count: the row is evaluated at it
            out.append((name, fig, r.queries, src, fig == r.queries and r.meets))
        else:
            out.append((name, fig, r.certified_count, src, fig == r.certified_count))
    return out


# --- tables -----------------------------------------------------------------------------------------------------


def _short(kind: str, t: Term) -> str:
    return f"{kind}: {t.name}"


def tables(category: int | None = None, convention: str = EVERY_T, hash_basis: str = "attack-rule") -> list[str]:
    field_bits, cat = FIELD_BITS, 1
    if category is not None:
        from . import category as C

        field_bits, cat = C.PROFILES[category].field_bits, category
    rs = rows(None, field_bits, built=cat == 1, convention=convention, category=cat, hash_basis=hash_basis)
    conv_line = ("Counting convention: EVERY t (the default; Sharp-Grubbs ePrint 2026/2615 Theorem 6.6 (2) with "
                 "Definitions H.3, H.4; docs/decision-qrom-counting.md): need = kappa_C + 1 + log2 N + log2(1 + k_q) at "
                 "each row's own k_q, solved to its fixed point."
                 if convention == EVERY_T else
                 f"**{NON_DEFAULT.upper()}**: the book need kappa_C + 1 + log2 N + log2(1 + k), k = {BUDGET_K} (the "
                 "revision 1 to 8 counts). Not the calculator's convention; no row below is certified.")
    out = [f"## Revision {REVISION}: system B's rows with every Johnson-regime term (category {cat}, GF(2^{field_bits}))",
           "", conv_line, "", f"Classical hash basis: {hash_basis} (revision 10.1, R10-1: every status below is computed by "
           "category.certification_checks on this basis; under 'proven' no 256-bit row is certified).", "",
           "Every Johnson-regime row " + DKT26_LABEL + "; it is never printed as certified without this label. Unique-decoding rows use no "
           f"Johnson-regime statement. The rate-1/4 Johnson row: {ARITH_ONLY} (finding R8-3).", "",
           "| Row | Status | Queries (smallest meeting) | k_q (provenance; padded group slots counted) | k_q guard | c' | "
           "Need | Query bits | Margin | Hash term, classical bits, proof / tree | Hash term, QROM bits, proof / tree | "
           "List size | Weakest algebraic round | Bits, exact (33) / paper | Bits, Lean-backed (ArkLib 6aa8b6fe, "
           "machine-checked) | Slack | Meets |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        k, w = r.weakest
        lb = f"{w.lean_bits:.2f}" if w.lean is not None else "- (no Johnson term)"
        cpl = r.c_input.label() if r.c_input is not None else f"{r.c_prime:,}"
        out.append(f"| {r.name} | {r.status} | {r.queries} ({r.certified_count}) | {r.kq.label()} | {r.kq.guard:.4f} | "
                   f"{cpl} | {r.need:.3f} | {r.query_bits:.3f} | {r.query_margin:+.4f} | {r.hash.cells()} | "
                   f"{r.list_size} | {_short(k, w)} | {w.bits:.2f} | {lb} | {r.slack:.1f} | {'yes' if r.meets else 'NO'} |")
    out += ["", "Revision 10 (finding L-2): the weakest Johnson term is printed twice. 'Exact (33)' is DKT26's count (33)-(34), "
            "a paper bound no Lean theorem checked here proves; 'Lean-backed' is ArkLib's coarser `johnsonExceptionCount` "
            "(coefficient 4 D mu h), the count of the machine-checked statement `check_F2_johnson_interleaved` "
            "(lean/Compose.lean; docs/arklib-lean-check.md 3.2, 4 (a) (ii)). The formal figure is the Lean-backed one."]
    out += ["", "### Every term, bits (`count` per round out of |K|; Johnson terms: exact count (33), closed form (39) "
            "in parentheses, ArkLib's machine-checked count in brackets)", ""]
    for r in rs:
        if r.note:
            continue
        out += [f"#### {r.name} ({r.status})", "", "| Proof | Term | Bits | Source |", "|---|---|---|---|"]
        for kind, ts in r.proof_terms:
            folds = [t for t in ts if t.name.startswith("X fold ") and t.name != "X fold 1"]
            for t in ts:
                if t in folds:
                    continue
                c = f" ({t.closed_bits:.2f}) [Lean-backed {t.lean_bits:.2f}]" if t.closed is not None else ""
                out.append(f"| {kind} | {t.name} | {t.bits:.2f}{c} | {t.source} |")
            if folds:
                w = min(folds, key=lambda t: t.bits)
                out.append(f"| {kind} | X folds 2 to {len(folds) + 1} (weakest: {w.name}) | {w.bits:.2f} | Lemma F |")
        out.append(f"| tree | query round ({r.queries} x {r.per_query:.4f}) | {r.query_bits:.3f} | [Hab-LDR] Lemma 3 |")
        src = ("SG26 Thm 6.6 (2), every t, k_q = " + f"{r.extra_kq:,}" if r.convention == EVERY_T
               else "soundness-method.md 8.5b (book, non-default)")
        out.append(f"| tree | need a round | {r.need:.3f} | {src} |")
        for sh in r.shapes:
            if not sh.terminal_recorded:
                out.append(f"| {sh.kind} | log_terminal_dim not recorded by the build: {TERMINAL_ASSUMED} taken, with DKT26 "
                           f"Lemma 3.3 at message dimension 1; D-term charged at the bound log_msg (2^r - 1) = "
                           f"{sh.log_msg} x {2 ** sh.rate - 1} | | BR-4 must print it (R8-4) |")
        out.append("")
    out += ["### The proximity-gap parameters of every Johnson line (DKT26 Theorem 4.4, (36) to (39)); lengths are the "
            "caps LOG_MSG (R8-6)", "",
            "| Rate | Line | n | k | A | m (36) | B_jet | B_Z | lambda_agr | log2 B_cf (33) | log2 closed (39) | "
            "list (38), exact | list | log2 tolerated |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    seen = set()
    for r in rs:
        if r.route != "dkt":
            continue
        for sh in r.shapes:
            for name, n, k in lines_of(sh, r.m)[:3 if sh.mask else 1]:
                if (n, k) in seen:
                    continue
                seen.add((n, k))
                ln = line(n, k, r.m)
                tol = tolerated_exceptional_log2(r.need, 2 * r.list_size, field_bits)
                out.append(f"| 1/{2 ** r.rate} | {sh.kind} {name} | 2^{n.bit_length() - 1} | 2^{k.bit_length() - 1} | "
                           f"{ln.A:,} | {ln.m_thm} | {ln.b_jet} | {ln.b_z} | {float(ln.lam):.4f} | {ln.count_log2:.3f} | "
                           f"{ln.closed_log2:.3f} | {float(ln.list_exact):.3f} | {ln.list_size} | {tol:.2f} |")
    out += ["", "### Refusals (hard failures, `OutsideRegime`)", ""]
    for desc, f in (
        ("a fold line of message dimension 1 without Lemma 3.3",
         lambda: terms("dkt", shape("node", 3, 0), 10, field_bits)),
        ("Haboeck's route", lambda: terms("haboeck", shape("leaf", 3), 10, field_bits)),
        ("m = 2", lambda: line(2**20, 2**17, 2)),
        ("m missing", lambda: row("x", "dkt", 3)),
        ("m not an integer", lambda: row("x", "dkt", 3, 10.0)),
        ("D > n - 2", lambda: line(16, 16, 10)),
        ("log_terminal_dim above the message log", lambda: shape("node", 3, 29)),
        ("log_terminal_dim negative", lambda: shape("node", 3, -1)),
        ("a Johnson threshold above the unique-decoding one (m = 1 is refused first; rate 1/2, m = 3)",
         lambda: row("x", "dkt", 1, 3)),
    ):
        try:
            f()
            out.append(f"- {desc}: NOT refused (defect)")
        except OutsideRegime as e:
            out.append(f"- {desc}: refused: {e}")
    t33 = [t for t in terms("dkt", shape("node", 3, 0), 10, field_bits, "lemma33") if "dimension 1" in t.name][0]
    out.append(f"- the same node with DKT26 Lemma 3.3 added: {t33.name}: count {t33.count:.0f}, {t33.bits:.2f} bits")
    out += ["", "### Condition C-2 (decided 2026-11-19: every t): counts under both conventions", "",
            "| Row | Every t (default) | t >= k_q (non-default, not certified) | Added | k_q at the every-t count | "
            "need (every t) |", "|---|---|---|---|---|---|"]
    for r in rs:
        if r.note:
            continue
        q, kq, nb = every_t_count(r, cat)
        b = book_count(r, cat)
        out.append(f"| {r.name}{' (' + ARITH_ONLY + ')' if r.arithmetic_only else ''} | {q} | {b} | {q - b:+d} | "
                   f"{kq:,} | {nb:.3f} |")
    out += ["", "### Cross-check against the documents", "", "| Row | Documented | Calculator | Source | Agree |",
            "|---|---|---|---|---|"]
    by_name = {r.name: r for r in rs}
    if cat == 1:
        for name, fig, calc, src, ok in cross_check(rs):
            tag = f" ({ARITH_ONLY})" if by_name[name].arithmetic_only else ""
            out.append(f"| {name}{tag} | {fig} | {calc} | {src} | {'yes' if ok else 'NO (finding)'} |")
    return out
