"""leanVM's `eps_aff`: the MCA error of the affine combiner by Chiesa, Weissenberg, Yogev, Zheng, Theorem 4.10.

Revision 6 (2026-11-19; CITATION-AUDIT C-19, design-basis R-5). Source, read from the lead architect's copy
(dated November 13, 2026): A. Chiesa, M. Weissenberg, E. Yogev, Z. Zheng, "Affine Combiners for Reed-Solomon
Proximity Gaps", Cryptology ePrint Archive, Paper 2026/2863 [CWYZ26]: definitions (4.1) (m, D, M), the
interpolation inequality (4.5), the threshold B (Section 4.3: B := ceil((sqrt(rho) + eta/2) n) - 1 in the proof
of Theorem 1.1; free in Theorem 4.10 as Remark 5.3 uses it), Theorem 4.10 with bound (4.13), the example after
it (n = 2^15, rho = 1/2048, eta = 0.05, q = 2^128: 2^-123.25) and Remark 5.3 (n = 2^20, d = 2^18, eta = 0.05,
A = 576717, q = 2^128, m = 3, D = 49, M = 6, B = 567980: about 125.42 bits).

Provenance: the bound is **Published** (CWYZ26 Theorem 4.10, (4.13)), implemented as stated:

    eps_aff <= floor( n (B - d - 1) / (B^2 - n (d + 1)) ) max{q, C(n, 2)} / q^2
               + ( D^2 + 4 d^2 M^2 D^3 (n / (A - B))^2 ) / q^2,

under the hypotheses M >= 1, (4.5), and B^2 > n (d + 1); d is the degree bound (rho n), A the agreement
threshold ceil((sqrt(rho) + eta) n), the agreement loss one coordinate. The parameter search over (m, D, B)
(`best`) follows leanVM's `find_witness` at the pin (Remark 5.3 leaves the choice to the user).
What leanVM's appendix B derives from this bound (the claim binding, the h lanes, the threshold lowered by one
per fold) is leanVM's own statement and is not checked here (R-5).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def _sums(j: int) -> tuple[int, int, int]:
    return j + 1, j * (j + 1) // 2, j * (j + 1) * (2 * j + 1) // 6


def interpolation_ok(n: int, d: int, A: int, m: int, D: int) -> tuple[bool, int]:
    """(4.1) and (4.5), exactly (integers): M = min(D, floor((m A - D - 1)/d)) >= 1 and
    sum_{j<=M} (mA - D - dj)(D - j + 1) > n sum_{s<=min(m-1,M)} (m - s)(D - s + 1); closed forms as leanVM's
    `interpolation_holds` (power sums)."""
    if m * A - D - 1 < 0:
        return False, 0
    M = min(D, (m * A - D - 1) // d)
    if M < 1:
        return False, M
    c, e = m * A - D, D + 1
    s0, s1, s2 = _sums(M)
    unknowns = c * e * s0 + d * s2 - (c + d * e) * s1
    t0, t1, t2 = _sums(min(m - 1, M))
    equations = n * (m * e * t0 + t2 - (m + e) * t1)
    return unknowns > equations, M


def johnson_list(n: int, agree: int, inter: int) -> int | None:
    """CWYZ26 Lemma 3.2 (Johnson): floor(n (agree - inter) / (agree^2 - n inter)); None below the radius."""
    den = agree * agree - n * inter
    if den <= 0 or agree < inter:
        return None
    return n * (agree - inter) // den


@dataclass(frozen=True)
class AffBound:
    n: int
    d: int
    A: int
    q_log2: float
    m: int
    D: int
    M: int
    B: int
    list_term: int  # floor(n (B - d - 1) / (B^2 - n (d + 1)))
    delta_log2: float

    @property
    def log2(self) -> float:
        q = 2.0**self.q_log2
        first = self.list_term * max(q, self.n * (self.n - 1) / 2) / q / q
        return math.log2(first + 2.0**self.delta_log2)

    @property
    def bits(self) -> float:
        return -self.log2

    def round_log2(self) -> float:
        """leanVM's fold-round error for (alpha, beta): eps_aff + 2 ell(A - 1, d) / q (its `combiner_within`,
        the claim binding of CWYZ26 (5.5) with l_0 the Johnson list at A - 1 against d)."""
        ell = johnson_list(self.n, self.A - 1, self.d) or 0
        return math.log2(2.0**self.log2 + 2 * ell * 2.0**-self.q_log2)


def eps_aff(n: int, d: int, A: int, q_log2: float, m: int, D: int, B: int) -> AffBound:
    """CWYZ26 Theorem 4.10, bound (4.13); raises ValueError when a hypothesis fails."""
    ok, M = interpolation_ok(n, d, A, m, D)
    if not ok:
        raise ValueError(f"interpolation inequality (4.5) or M >= 1 fails at m = {m}, D = {D} (M = {M})")
    if not (B * B > n * (d + 1)) or not (d + 1 < B < A) or A > n:
        raise ValueError(f"B = {B}: need B^2 > n (d + 1), d + 1 < B < A <= n")
    ell = johnson_list(n, B, d + 1)
    num = D * D + 4.0 * d * d * M * M * D**3 * (n / (A - B)) ** 2
    return AffBound(n, d, A, q_log2, m, D, M, B, ell, math.log2(num) - 2 * q_log2)


def threshold(n: int, rho: float, eta: float) -> int:
    return math.ceil((math.sqrt(rho) + eta) * n)


def _smallest_d(n: int, d: int, A: int, m: int) -> int | None:
    """For multiplicity m, the smallest D satisfying (4.5) (leanVM's `smallest_big_d`: past the saturation of M,
    a ternary search for the peak of unknowns/equations, then a bisection on the exact test)."""
    lo, hi = max((m * A - 1) // d, 1), m * A // 2
    if lo >= hi:
        return None

    def ratio(D: int) -> float:
        M = min(D, (m * A - D - 1) // d)
        if M < 1:
            return 0.0
        c, e = m * A - D, D + 1
        s0, s1, s2 = _sums(M)
        t0, t1, t2 = _sums(min(m - 1, M))
        return (c * e * s0 + d * s2 - (c + d * e) * s1) / (n * (m * e * t0 + t2 - (m + e) * t1))

    x, y = lo, hi
    while y - x > 3:
        x1, y1 = x + (y - x) // 3, y - (y - x) // 3
        if ratio(x1) < ratio(y1):
            x = x1 + 1
        else:
            y = y1
    peak = next((D for D in range(x, y + 1) if interpolation_ok(n, d, A, m, D)[0]), None)
    if peak is None:
        return None
    x, y = lo, peak
    while x < y:
        mid = (x + y) // 2
        if interpolation_ok(n, d, A, m, mid)[0]:
            y = mid
        else:
            x = mid + 1
    return x


def best(n: int, d: int, A: int, q_log2: float, max_m: int = 1 << 16) -> AffBound | None:
    """leanVM's `find_witness` (crates/experimental_prover/pcs/src/whir_config/affine_mca.rs at the pin): the
    smallest feasible m (doubling, then bisection), its smallest D, then B = A - 2^i minimising (4.13)."""
    gap = A * A - n * d
    if gap <= 0:
        return None
    lo = max(n * d // gap, 1)
    hi = lo
    while _smallest_d(n, d, A, hi) is None:
        lo, hi = hi + 1, hi * 2
        if hi > max_m:
            return None
    while lo < hi:
        mid = (lo + hi) // 2
        if _smallest_d(n, d, A, mid) is not None:
            hi = mid
        else:
            lo = mid + 1
    m, D = hi, _smallest_d(n, d, A, hi)
    out = None
    for i in range(128):
        B = A - (1 << i)
        if B <= d + 1 or johnson_list(n, B, d + 1) is None:
            break
        try:
            b = eps_aff(n, d, A, q_log2, m, D, B)
        except ValueError:
            continue
        if out is None or b.log2 < out.log2:
            out = b
    return out
