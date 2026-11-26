"""Primitive error bounds, each tagged with its source and whether the source was confirmed.

Every function returns log2 of an error probability (a negative number, or -inf) unless its name
says otherwise. Working in log2 keeps 2^-200-sized terms exact in floating point.

Source status (see docs/soundness-method.md, "Sources"):

  CONFIRMED   the statement was read in the primary source during step 0.6.
  UNCONFIRMED transcribed from a secondary source (named) or from memory; the external
              cryptographer's E3 review must check it before any parameter set relies on it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

NEG_INF = float("-inf")


def log2_sum(terms: list[float]) -> float:
    """log2(sum 2^x) for a list of log2 values."""
    finite = [t for t in terms if t != NEG_INF]
    if not finite:
        return NEG_INF
    top = max(finite)
    return top + math.log2(sum(2.0 ** (t - top) for t in finite))


class Status(Enum):
    CONFIRMED = "confirmed"
    UNCONFIRMED = "unconfirmed"


@dataclass(frozen=True)
class Source:
    ref: str
    status: Status


# --- Reed-Solomon proximity gaps ------------------------------------------------------------

BCIKS20_UD = Source(
    "BCIKS20, ePrint 2020/654 (revision of July 3, 2021), Theorem 1.2, eq. (1.1), unique-decoding case: eps_U = n/q", Status.CONFIRMED
)
BCIKS20_JB = Source(
    "BCIKS20, ePrint 2020/654 (revision of July 3, 2021), Theorem 1.2, eq. (1.2), Johnson case: eps_J = (k+1)^2 / ((2 min(eta, sqrt(rho)/20))^7 q)",
    Status.CONFIRMED,
)
BCIKS20_CURVE = Source(
    "BCIKS20, ePrint 2020/654 (revision of July 3, 2021), Theorem 1.5: a degree-l curve has error l * eps", Status.CONFIRMED
)
# Dao, Kominers, Thaler, "Reed-Solomon Codes Beyond Johnson: Efficient Decoding and Smaller
# Cryptographic Proofs", ePrint 2026/2056 (copy dated November 2, 2026), read 2026-11-19:
# Theorem 4.4 (quantitative Johnson MCA in every characteristic, any n distinct evaluation points),
# equation (39): exceptional count B_cf < 8 n t^3 / (3 rho_minus), t = m + 1/2,
# m = max(ceil(sqrt(rho_minus) / (2 eta0)), 3), rho_minus = D/n = (k - 1)/n, agreement
# sqrt(rho_minus) + eta0; closed form proved in its Section B.3; probability B_cf / |F|.
# Plonky3's "Theorem 5.12 / App. B.1-B.2" is the numbering of an earlier version (DKT26b, cited
# by the copy read). Finding C-14: the calculator used rho in place of rho_minus until 2026-11-19.
DKT26_LINE = Source(
    "DKT26, ePrint 2026/2056 (2026-11-02), Theorem 4.4, eq. (39) and Section B.3: line MCA (full agreement "
    "sets) exceptional count < 8 n (m+1/2)^3 / (3 rho_minus), rho_minus = (k-1)/n, every characteristic, "
    "any evaluation set",
    Status.CONFIRMED,
)
# The list size used is 1/(2 eta sqrt(rho)) = m / rho (WHIR, ePrint 2024/1586, Theorem 4.3). DKT26
# Theorem 4.4, eq. (38), proves |L| <= min(B_jet, n (A - D)/(A^2 - n D)), B_jet = ceil(t/sqrt(rho_minus)) - 1,
# for every field and evaluation set (Proposition B.1 and the pairwise Johnson argument after it); at
# the calculator's agreement both are below m / rho, so the figure used is an upper bound (C-15).
JOHNSON_LIST = Source(
    "Johnson list size L <= 1/(2 eta sqrt(rho)) at radius 1 - sqrt(rho) - eta: WHIR ePrint 2024/1586 Theorem 4.3; "
    "dominates DKT26 ePrint 2026/2056 Theorem 4.4 eq. (38), which proves the list bound on any evaluation set",
    Status.CONFIRMED,
)


def pg_udr(log_n: float, field_bits: float) -> float:
    """Proximity-gap error for a line below the unique-decoding radius: n / |F| (BCIKS20 Thm 1.2)."""
    return log_n - field_bits


def pg_johnson_bciks(log_k1: float, rho: float, eta: float, field_bits: float) -> float:
    """Proximity-gap error for a line up to the Johnson radius (BCIKS20 Thm 1.2, Johnson case).

    log_k1 is log2(k+1), the code dimension (message length); rho the rate; eta = 1 - sqrt(rho) - delta.
    """
    denom = (2.0 * min(eta, math.sqrt(rho) / 20.0)) ** 7
    return 2.0 * log_k1 - math.log2(denom) - field_bits


def pg_johnson_dkt26(log_n: float, log_k: float, m: float, field_bits: float) -> float:
    """Line MCA error at the Johnson radius: DKT26 (ePrint 2026/2056) Theorem 4.4, eq. (39).

    8 n (m + 1/2)^3 / (3 rho_minus q) with rho_minus = (k - 1)/n (finding C-14: rho was used before).
    The calculator's agreement sqrt(rho) (1 + 1/(2m)) exceeds DKT26's sqrt(rho_minus) + eta0 at the
    same m, so DKT26's own m at that agreement is at most m and the count is an upper bound.
    Hypotheses: 2 <= k <= n - 1 (Theorem 4.4: 1 <= D <= n - 2); m >= 3.
    """
    k = 2.0 ** log_k
    n = 2.0 ** log_n
    if not (2.0 <= k <= n - 1.0) or m < 3.0:
        raise ValueError("DKT26 Theorem 4.4 needs 2 <= k <= n - 1 and m >= 3")
    rho_minus = (k - 1.0) / n
    return math.log2(8.0) + log_n + 3.0 * math.log2(m + 0.5) - math.log2(3.0 * rho_minus) - field_bits


def curve(l: int, eps_log2: float) -> float:
    """Degree-l curve (batching by powers of one challenge): l * eps (BCIKS20 Thm 1.5)."""
    if l <= 0:
        return NEG_INF
    return math.log2(l) + eps_log2


# --- Decoding regimes ------------------------------------------------------------------------


class Regime(Enum):
    UDR = "unique-decoding"
    JB_BCIKS = "johnson-bciks20"
    JB_DKT26 = "johnson-dkt26 (UNCONFIRMED)"


@dataclass(frozen=True)
class RegimePoint:
    """The proximity parameter a protocol runs at, for a code of rate rho."""

    regime: Regime
    rho: float
    m: float = 10.0  # Johnson slack: eta = sqrt(rho) / (2m)

    @property
    def eta(self) -> float:
        if self.regime is Regime.UDR:
            return 0.0
        return math.sqrt(self.rho) / (2.0 * self.m)

    @property
    def delta(self) -> float:
        if self.regime is Regime.UDR:
            return (1.0 - self.rho) / 2.0
        return 1.0 - math.sqrt(self.rho) - self.eta

    @property
    def query_agreement(self) -> float:
        """alpha = 1 - delta: the probability one query misses a delta-far word."""
        return 1.0 - self.delta

    @property
    def list_size_log2(self) -> float:
        if self.regime is Regime.UDR:
            return 0.0
        return -math.log2(2.0 * self.eta * math.sqrt(self.rho))

    def line_error(self, log_n: float, log_k1: float, field_bits: float) -> float:
        if self.regime is Regime.UDR:
            return pg_udr(log_n, field_bits)
        if self.regime is Regime.JB_BCIKS:
            return pg_johnson_bciks(log_k1, self.rho, self.eta, field_bits)
        return pg_johnson_dkt26(log_n, log_k1, self.m, field_bits)

    def sources(self) -> list[Source]:
        if self.regime is Regime.UDR:
            return [BCIKS20_UD, BCIKS20_CURVE]
        if self.regime is Regime.JB_BCIKS:
            return [BCIKS20_JB, BCIKS20_CURVE, JOHNSON_LIST]
        return [DKT26_LINE, BCIKS20_CURVE, JOHNSON_LIST]


def query_error(point: RegimePoint, queries: int) -> float:
    """log2(alpha^t): a query round against a delta-far word."""
    return queries * math.log2(point.query_agreement)


# --- Fiat-Shamir / BCS compilation ------------------------------------------------------------

# The original statement of the classical compilation bound is Ben-Sasson, Chiesa, Spooner,
# "Interactive Oracle Proofs", ePrint 2016/116, Theorem 7.1: s' = sbar_sr(x, m) + 3 (m^2 + 1) 2^-lambda
# (read 2026-11-19); the calculator uses the later form of the Chiesa-Yogev book cited below.
BCS_CLASSICAL = Source(
    "Chiesa-Yogev, Building Cryptographic Proofs from Hash Functions (snargsbook.org), Theorem 25.2.1: "
    "eps_ARG(t) <= eps_sr(t) + 3.5 t^2 / 2^lambda; Theorem 31.2.1: eps_sr(t) <= (t + k) eps_rbr; "
    "Section 28.3.2 for the average-case bits-of-security definition",
    Status.CONFIRMED,
)
BCS_QROM = Source(
    "Chiesa-Manohar-Spooner, ePrint 2019/834 (copy of 2020-01-14), Theorem 8.6: BCS on a round-by-round "
    "sound IOP has soundness O(t^2 eps_rbr + t^3 / 2^lambda) against t quantum queries; its proof (Section "
    "8.5.1) gives 6 (t^2 eps_rbr + 4 t^3 / 2^lambda) for the database game, so C1 = 6, C2 = 24 (read "
    "2026-11-19). Unconfirmed for the transcripts as built: the theorem is for the paper's own BCS variant "
    "(Section 8.2, Remark 8.2), not for a sponge transcript squeezing many challenges (CITATION-AUDIT C-7)",
    Status.UNCONFIRMED,
)
GRINDING_CLASSICAL = Source(
    "Proof of work of g bits before a challenge multiplies that round's error by 2^-g against a classical "
    "query-bounded adversary (ethSTARK, ePrint 2021/582 Section 5; not fetched)",
    Status.UNCONFIRMED,
)
GRINDING_QUANTUM = Source(
    "Against a quantum adversary the round's bad set has density eps * 2^-g in the oracle's output, so the "
    "CMS19 t^2 term halves the grinding bits along with the round's own bits. Our argument; relies on "
    "the optimality of Grover search (Bennett-Bernstein-Brassard-Vazirani 1997; not fetched)",
    Status.UNCONFIRMED,
)
RECURSION_UNION = Source(
    "Recursive composition: the chain's error is at most the sum of the layers' errors at the same query "
    "budget (union bound). Conditional on the heuristic that Keccak evaluated inside a circuit behaves as "
    "the random oracle the inner proof assumed; no proof in the ROM covers that step",
    Status.UNCONFIRMED,
)
