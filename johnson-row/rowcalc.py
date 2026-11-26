"""Error terms of system B's opening rows in the unique-decoding and Johnson regimes.

Part of `docs/binius-johnson-row.md` section 7 (Yugen). Standalone: the calculator in
`../soundness/` is not changed; these formulas are for its next revision. Original code (the Ycash
developers, 2026); the formulas are cited per function.

Bits are -log2(error). All logs base 2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

FIELD_BITS = 256
TREE_PROOFS = 20_000
BUDGET_K = 600  # challenges a proof on average (parameters.md 2a.2)
# Largest committed codeword length (common lifted level) a proof of the tree opens, log2:
LOG_E_LEAF = 22   # wallet leaf, rate 1/8: largest round oracle 2^19 as built (2^18 mixed): 2^22 bounds both
LOG_E_NODE = 31   # node of 2^30 AND rows: opening of 2^28 elements at rate 1/8 (calculator: fold.0 = 225 bits)
J_CLAIMS = 4      # relations batched by the opening (leaf); the batching term is (J - 1)
PIOP_WORST = 127  # univariate-skip round, the largest Schwartz-Zippel count of the PIOP rounds
KAPPA = 8         # ring-switch coordinates (form T)


def need(classical_chain: float) -> float:
    """Every round's bits for the tree: classical_chain + 1 + log2(proofs x (1 + k))
    (soundness-method.md 8.5b; calculator binius64.tree_need at the row budget)."""
    return classical_chain + 1.0 + math.log2(TREE_PROOFS * (1 + BUDGET_K))


NEED = {"cat1": need(128.0), "cat3": need(192.0)}


def bits(count: float) -> float:
    return FIELD_BITS - math.log2(count)


# --- the list size ---------------------------------------------------------------------------------

def list_bound(m: int, rho: float) -> int:
    """List size at agreement a = (1 + 1/(2m)) sqrt(rho), every width, every evaluation set:
    the classical pairwise (Johnson) bound n (A - D) / (A^2 - n D), DKT26 ePrint 2026/2056
    Theorem 4.4 bound (38), second term (proof read: Section B.2, Cauchy-Schwarz over the A-sets of
    the candidates, pairwise intersections at most D), transferred to interleaved words by
    Corollary 6.4 (or directly: two distinct codeword tuples agree on at most D common columns).
    It is decreasing in A and increasing in D, so with A >= a n and D < rho n it is at most
    (a - rho) / (a^2 - rho) at every n; the list size is an integer, hence the floor.
    m = 10, rho = 1/8: 19 (19.22). Revision 2 of the document; revision 1 used the
    Guruswami-Sudan Y-degree (m + 1/2)/sqrt(rho) = 29.70, valid but looser."""
    a = (1 + 1 / (2 * m)) * math.sqrt(rho)
    return math.floor((a - rho) / (a * a - rho))


def gs_list_bound(m: int, rho: float) -> float:
    """Revision 1's bound, kept for comparison: (m + 1/2)/sqrt(rho) (BCIKS20 Lemma 5.3, Claim 5.4;
    Haboeck ePrint 2024/1571 l_m)."""
    return (m + 0.5) / math.sqrt(rho)


def lemma33_count(n: int, A: int, ell: int = 1) -> int:
    """Exceptional count for a level of message dimension 1 (constant code), DKT26 Lemma 3.3 (6):
    ell C(n, 2) / (A - 1) for A >= 2 (proof read). Theorem 4.4 excludes D = 0."""
    pairs = n * (n - 1) // 2
    return ell * pairs if A == 1 else (ell * pairs) // (A - 1)


def query_bits(m: int | None, rho: float) -> float:
    """One query: Johnson (1 - theta) = (1 + 1/(2m)) sqrt(rho) (Haboeck Lemma 3); unique decoding
    (1 + rho)/2 (DP24 Proposition 4.24)."""
    if m is None:
        return -math.log2((1 + rho) / 2)
    return -math.log2((1 + 1 / (2 * m)) * math.sqrt(rho))


# --- proximity terms (counts of bad challenges; divide by |K|) ---------------------------------------

def haboeck_count(log_n: float, B: float, m: int, rho: float, M: int = 1) -> float:
    """eps(C, M, B, theta) |F| of Haboeck ePrint 2024/1571 Theorem 3 / Theorem 4:
    M (m + 1/2)/sqrt(rho) max( (m + 1/2)^6 / (3 rho) |D|^2, 2 (B |D| + 1) )."""
    n = 2.0 ** log_n
    t = m + 0.5
    return M * t / math.sqrt(rho) * max(t ** 6 / (3 * rho) * n * n, 2 * (B * n + 1))


def dkt_count(log_n: float, m: int, rho: float) -> float:
    """Exceptional count of line MCA at the Johnson threshold, DKT26 ePrint 2026/2056 Theorem 4.4,
    bound (39): B_cf < 8 n t^3 / (3 rho_-), t = m + 1/2, rho_- = D / n = rho - 1/n (degree bound
    D = rho n - 1). Width-independent for interleaved words (Lemma 6.5, Corollary 6.6)."""
    n = 2.0 ** log_n
    rho_minus = rho - 1.0 / n
    t = m + 0.5
    return 8.0 * n * t ** 3 / (3.0 * rho_minus)


@dataclass
class Term:
    name: str
    count: float  # bad challenges (out of |K|)
    source: str

    @property
    def bits(self) -> float:
        return bits(self.count)


def terms(regime: str, log_e: int, m: int | None = None, rho: float = 1 / 8, mask: bool = True,
          index_rounds: int = 1) -> list[Term]:
    """Every distinct error term of one proof's rounds. regime: 'ud', 'haboeck', 'dkt'."""
    out: list[Term] = []
    lst = 1.0 if regime == "ud" else list_bound(m, rho)
    out.append(Term("PIOP round (worst: skip, 127)", lst * PIOP_WORST, "Schwartz-Zippel x list (Lemma U)"))
    out.append(Term("ring switch (each)", lst * KAPPA, "Theorem 1 x list (Lemma J1)"))
    out.append(Term("claim batching (alpha / mu)", lst * (J_CLAIMS - 1), "Schwartz-Zippel x list (Lemma U)"))
    first_fold_log = log_e - 1  # the line of the first X fold lives on the half domain
    if regime == "ud":
        if mask:
            out.append(Term("mask fold gamma", 2.0 ** log_e + 1, "line MCA n (WHIR Cor. 4.11) + 1 root"))
        for j in range(index_rounds):
            out.append(Term(f"index round {j}", 2.0 ** log_e + 2, "line MCA n + 2 roots"))
        out.append(Term("first X fold", 2.0 ** first_fold_log + 2, "line MCA n/2 + 2 roots"))
    elif regime == "haboeck":
        if mask:
            out.append(Term("mask fold gamma", haboeck_count(log_e, 1, m, rho), "Haboeck Thm 4, B = 1 (Lemma J2)"))
        for j in range(index_rounds):
            out.append(Term(f"index round {j}", haboeck_count(log_e, 1, m, rho), "Haboeck Thm 4, B = 1"))
        out.append(Term("first X fold", haboeck_count(first_fold_log, 2, m, rho), "Haboeck Lemma 4 (Thm 4), B = 2"))
    elif regime == "dkt":
        if mask:
            out.append(Term("mask fold gamma", dkt_count(log_e, m, rho) + 1 * lst, "DKT26 Thm 4.4 + 1 root a list element"))
        for j in range(index_rounds):
            out.append(Term(f"index round {j}", dkt_count(log_e, m, rho) + 2 * lst, "DKT26 Thm 4.4 + 2 roots a list element"))
        out.append(Term("first X fold", dkt_count(first_fold_log, m, rho) + 2 * lst, "DKT26 Thm 4.4 + 2 roots a list element"))
    else:
        raise ValueError(regime)
    return out


def row(regime: str, target: str, m: int | None = None, rho: float = 1 / 8) -> dict:
    """Queries and the weakest algebraic term over the tree (leaf with mask and one index round;
    node without mask, one oracle)."""
    nd = NEED[target]
    qb = query_bits(None if regime == "ud" else m, rho)
    q = math.ceil(nd / qb)
    shift = int(round(math.log2(8 * rho)))  # the same messages at another rate: codewords 1/rho long
    leaf = terms(regime, LOG_E_LEAF - shift, m, rho)
    node = terms(regime, LOG_E_NODE - shift, m, rho,
                 mask=False, index_rounds=0)
    weakest = min(leaf + node, key=lambda t: t.bits)
    return {"regime": regime, "target": target, "m": m, "rho": rho, "need": nd, "queries": q,
            "query_bits": q * qb, "per_query": qb, "leaf": leaf, "node": node,
            "weakest": weakest, "meets": weakest.bits >= nd and q * qb >= nd}


def best_m(target: str, regime: str = "dkt", rho: float = 1 / 8, m_max: int = 2000) -> dict | None:
    """Smallest query count over m >= 3 whose every term meets the target; ties to the smallest m."""
    best = None
    for m in range(3, m_max + 1):
        r = row(regime, target, m, rho)
        if r["meets"] and (best is None or r["queries"] < best["queries"]):
            best = r
    return best


def tolerated_exceptional_log2(target: str, roots_times_list: float) -> float:
    """log2 of the largest line exceptional count E such that (E + roots_times_list)/|K| still meets
    the per-round target: the qualitative-MCA requirement of section 7.4 (any proof of line MCA with
    full agreement sets, or equivalently the subset form, whose count at the opening's line lengths
    is below this suffices for the row)."""
    return math.log2(2.0 ** (FIELD_BITS - NEED[target]) - roots_times_list)


if __name__ == "__main__":
    for args in (("ud", "cat1", None), ("dkt", "cat1", 10), ("haboeck", "cat1", 10),
                 ("ud", "cat3", None), ("dkt", "cat3", 3), ("haboeck", "cat3", 3)):
        r = row(*args)
        print(f"{r['regime']:8} {r['target']} m={r['m']} need {r['need']:.2f} queries {r['queries']} "
              f"({r['query_bits']:.2f} bits) weakest {r['weakest'].name}: {r['weakest'].bits:.2f} meets {r['meets']}")
        for t in r["leaf"]:
            print(f"    leaf {t.name:32} {t.bits:8.2f}")
        for t in r["node"]:
            print(f"    node {t.name:32} {t.bits:8.2f}")
    print("B_list m=10:", list_bound(10, 1 / 8), "GS:", round(gs_list_bound(10, 1 / 8), 2))
    print("tolerated exceptional count, cat1, log2:", round(tolerated_exceptional_log2("cat1", 2 * list_bound(10, 1 / 8)), 2))
    r16 = row("dkt", "cat1", 10, 1 / 16)
    print("rate 1/16 m=10 DKT:", r16["queries"], round(r16["query_bits"], 2), round(r16["weakest"].bits, 2), r16["meets"])
    print("Lemma 3.3 count at a k = 1 level (n = 8, A = 3):", lemma33_count(8, 3))
