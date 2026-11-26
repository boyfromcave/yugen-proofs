"""System B's opening rows in unique decoding (certified) and in the Johnson regime (CANDIDATE rows).

Revision 5 (2026-11-19): replaces `binius64.johnson_bciks` (kept as the revision-4 record) by the three
routes of docs/binius-johnson-row.md section 7 (formulas of its table 7.2; the standalone computation is
`johnson-row/rowcalc.py`, which this module follows term for term). Per round, a count of bad challenges
out of |K| = 2^256; the list size B_list multiplies every PIOP, ring-switch and batching term; the first
X fold lives on the half domain; the mask and index rounds at the full domain; the query term per regime.

Only the unique-decoding row (184 queries at rate 1/8) is CERTIFIED. The Johnson rows are
CANDIDATE rows, under referee review: they rest on Dao, Kominers, Thaler, "Reed-Solomon Codes Beyond
Johnson", ePrint 2026/2056 (Theorem 4.4, eq. (39), Lemma 6.5, Corollary 6.6; DKT26 route) or on Haboeck,
"Basefold in the List Decoding Regime", ePrint 2024/1571 (Theorems 3, 4; Haboeck route, with gap G-1 for
the leaf's two-oracle rounds), and on the three lemmas L-J1 to L-J3 of binius-johnson-row.md
(Original, the Ycash developers, 2026; unreviewed). They are never reported as certified.

Sources of each formula (binius-johnson-row.md 7.2):
  list size    (m + 1/2) / sqrt(rho), conservative (dkt26.py's DKT26 (38) gives 19 / 31): BCIKS20 (ECCC TR20-083) Lemma 5.3, Claim 5.4; DKT26 Theorem 4.4 (B_jet)
  DKT26 count  B_cf(n) = 8 n (m + 1/2)^3 / (3 rho_-), rho_- = rho - 1/n: DKT26 Theorem 4.4, bound (39)
  Haboeck      eps(C, M, B, theta) |K| = M (t / sqrt(rho)) max(t^6 / (3 rho) |D|^2, 2 (B |D| + 1)), t = m + 1/2:
               Haboeck Theorems 3, 4
  query        unique decoding (1 + rho)/2: Diamond, Posen, ePrint 2024/504, Proposition 4.24, eq. (42);
               Johnson (1 + 1/(2m)) sqrt(rho): Haboeck Lemma 3
"""

from __future__ import annotations

import math
from dataclasses import dataclass

FIELD_BITS = 256
LOG_E_LEAF = 22  # largest common lifted level of the wallet leaf at rate 1/8 (binius-johnson-row.md 7.1)
LOG_E_NODE = 31  # a node of 2^30 AND rows at rate 1/8
J_CLAIMS = 4
PIOP_WORST = 127
KAPPA = 8
CANDIDATE = "candidate, under referee review"
CERTIFIED = "certified"


def list_bound(m: int, rho: float) -> float:
    """(m + 1/2) / sqrt(rho): CONSERVATIVE (finding R8-8b / R8-14, revision 9). It is at least DKT26's B_jet (first term
    of Theorem 4.4 (38): 29 at rate 1/8, 42 at rate 1/16, m = 10), which is at least the Johnson value of (38)'s second
    term that dkt26.py uses (19 and 31). The builder's `Row::list_size` (29.70 / 42) is this bound."""
    return (m + 0.5) / math.sqrt(rho)


def query_bits(m: int | None, rho: float) -> float:
    if m is None:
        return -math.log2((1 + rho) / 2)
    return -math.log2((1 + 1 / (2 * m)) * math.sqrt(rho))


def haboeck_count(log_n: float, B: float, m: int, rho: float, M: int = 1) -> float:
    n = 2.0 ** log_n
    t = m + 0.5
    return M * t / math.sqrt(rho) * max(t ** 6 / (3 * rho) * n * n, 2 * (B * n + 1))


def dkt_count(log_n: float, m: int, rho: float) -> float:
    n = 2.0 ** log_n
    t = m + 0.5
    return 8.0 * n * t ** 3 / (3.0 * (rho - 1.0 / n))


@dataclass(frozen=True)
class Term:
    name: str
    count: float
    field_bits: int = FIELD_BITS  # revision 7: the challenge field is an input (default 256, as before)

    @property
    def bits(self) -> float:
        return self.field_bits - math.log2(self.count)


def terms(route: str, log_e: int, m: int | None, rho: float, mask: bool = True, index_rounds: int = 1,
          field_bits: int = FIELD_BITS) -> list[Term]:
    """route: 'ud' (unique decoding), 'haboeck', 'dkt'. `field_bits`: the challenge field (revision 7)."""
    lst = 1.0 if route == "ud" else list_bound(m, rho)
    out = [Term("PIOP round (worst: skip, 127)", lst * PIOP_WORST, field_bits), Term("ring switch (each)", lst * KAPPA, field_bits),
           Term("claim batching", lst * (J_CLAIMS - 1), field_bits)]
    half = log_e - 1  # the line of the first X fold lives on the half domain
    if route == "ud":  # line MCA n (WHIR Cor. 4.11) plus the roots of the claim
        mask_c, index_c, fold_c = 2.0 ** log_e + 1, 2.0 ** log_e + 2, 2.0 ** half + 2
    elif route == "dkt":  # DKT26 Theorem 4.4 plus one or two roots a list element
        mask_c = dkt_count(log_e, m, rho) + lst
        index_c = dkt_count(log_e, m, rho) + 2 * lst
        fold_c = dkt_count(half, m, rho) + 2 * lst
    elif route == "haboeck":  # Haboeck Theorem 4 with B = 1, and B = 2 for the first fold
        mask_c = index_c = haboeck_count(log_e, 1, m, rho)
        fold_c = haboeck_count(half, 2, m, rho)
    else:
        raise ValueError(route)
    if mask:
        out.append(Term("mask fold gamma", mask_c, field_bits))
    out += [Term(f"index round {j}", index_c, field_bits) for j in range(index_rounds)]
    out.append(Term("first X fold", fold_c, field_bits))
    return out


@dataclass(frozen=True)
class BRow:
    route: str
    m: int | None
    rho: float
    need: float
    queries: int
    per_query: float
    weakest: Term
    status: str

    @property
    def query_bits(self) -> float:
        return self.queries * self.per_query

    @property
    def meets(self) -> bool:
        return self.weakest.bits >= self.need and self.query_bits >= self.need

    @property
    def label(self) -> str:
        if self.route == "ud":
            return "unique decoding"
        return f"Johnson, m = {self.m}, {'DKT26' if self.route == 'dkt' else 'Haboeck'} route"


def row(route: str, need: float, m: int | None = None, rho: float = 1 / 8, field_bits: int = FIELD_BITS) -> BRow:
    qb = query_bits(None if route == "ud" else m, rho)
    q = math.ceil(need / qb)
    shift = int(round(math.log2(8 * rho)))
    leaf = terms(route, LOG_E_LEAF - shift, m, rho, field_bits=field_bits)
    node = terms(route, LOG_E_NODE - shift, m, rho, mask=False, index_rounds=0, field_bits=field_bits)
    weakest = min(leaf + node, key=lambda t: t.bits)
    return BRow(route, m, rho, need, q, qb, weakest, CERTIFIED if route == "ud" else CANDIDATE)


def best_m(need: float, route: str = "dkt", rho: float = 1 / 8, m_max: int = 2000,
           field_bits: int = FIELD_BITS) -> BRow | None:
    best = None
    for m in range(3, m_max + 1):
        r = row(route, need, m, rho, field_bits)
        if r.meets and (best is None or r.queries < best.queries):
            best = r
    return best
