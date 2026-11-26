"""WHIR over a multilinear (stacked) commitment: system A (leanVM) and WHIR-shaped binary PCSs.

Per round i, with m_i variables, fold k_i, log inverse rate r_i, t_i queries, s OOD samples:
  fold_i.j  sumcheck round j of the fold    3 L / |F|  +  eps_line(n_i)           (k_i of them)
  ood_i     out-of-domain sample (Johnson)   L^2 / 2 * (2^m_i / |F|)^s
  query_i   shift queries + combination      (1 - delta_i)^t_i + (t_i + s) L / |F|
  final     last round's queries             (1 - delta_M)^t_M

Source: Arnon, Chiesa, Fenzi, Yogev, "WHIR: Reed-Solomon Proximity Testing with Super-Fast
Verification", ePrint 2024/1586 (copy dated November 21, 2024; read 2026-11-19), Theorem 5.2:
eps_fold <= d* l / |F| + err*(C, 2, delta), d* = 1 + deg_Z(w) + max_i deg_Xi(w) = 3 for an evaluation
constraint Z eq(z, X) (Construction 5.1); eps_out <= 2^m_i l^2 / (2 |F|) for one sample (Lemma 4.25 for
s samples: l^2 / 2 (2^m / |F|)^s); eps_shift <= (1 - delta)^t + l (t + 1) / |F|; eps_fin <= (1 - delta)^t.
The fold term was 2 L / |F| (Plonky3 p3-security whir/mod.rs) until the citation audit (finding C-9;
at 256-bit fields the change is below 10^-7 bits). err* is the mutual-correlated-agreement error: proven
in unique decoding (Lemma 4.10, Corollary 4.11: (l - 1) n / |F| for a line), a CONJECTURE up to the
Johnson bound (Conjecture 4.12); the paper restricts to smooth multiplicative domains (Definition 4.2), so
for System A's binary additive codes the term list is applied, not proven (finding C-10).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .bounds import NEG_INF, Regime, RegimePoint, log2_sum, query_error
from .compose import FsParams, Round, resolve_need


@dataclass
class WhirConfig:
    name: str
    field_bits: float
    base_bytes: int  # bytes per committed element at round 0
    ext_bytes: int
    num_vars: int  # m_0
    log_inv_rates: list[int]  # r_i per round
    folds: list[int]  # k_i per round
    queries: list[int]  # t_i per round
    ood_samples: int = 1
    batch_count: int = 1  # polynomials batched into round 0 (stacked commitment: 1)
    regime: Regime = Regime.UDR
    johnson_m: float = 10.0
    grind_fold: float = 0.0
    grind_ood: float = 0.0
    grind_query: float = 0.0
    grind_batch: float = 0.0
    salt_bytes: int = 0
    cap_height: int = 0
    extra_bytes: int = 0  # non-PCS transcript (zerocheck, GKR, lookups) not modelled here
    fs: FsParams = field(default_factory=FsParams)
    # Finding W-1 (docs/whir-additive-soundness.md section 6, Lemmas C0 and B0; revision 5): system A's
    # affine combiner adds one coefficient to the folded lane a fold round, so level i's code has
    # 2^mu_i + k_i coefficients on 2^(mu_i + r_i) rows (mu_i = m_i - k_i), and its query terms are taken
    # at that TRUE rate, not at the nominal 2^-r_i. Source of the degree growth: the pinned leanVM verifier
    # (crates/verifier/src/whir.rs: the final lane has (1 << mu) + fold_count scalars, each non-final level
    # corrects a position by novel_eval(high, what) * what[mu] with fold_count high coefficients); the growth
    # (alpha + beta X) F raising the degree by one a round is elementary. Chiesa, Weissenberg, Yogev, Zheng,
    # ePrint 2026/2863, Theorem 5.2 states d + r for a DIFFERENT combiner (the equal-degree variant (5.1) with a
    # third challenge theta) and is cited only as consistent with it (referee report 3.2, revision 6).
    true_rate: bool = False

    def rate(self, i: int) -> float:
        """The rate the level-i query terms use: nominal 2^-r_i, or (with `true_rate`) the true rate."""
        if not self.true_rate:
            return 2.0 ** -self.log_inv_rates[i]
        mu = self.vars_at(i) - self.folds[i]
        return (2.0 ** mu + self.folds[i]) / 2.0 ** (mu + self.log_inv_rates[i])

    def point(self, i: int) -> RegimePoint:
        return RegimePoint(self.regime, self.rate(i), self.johnson_m)

    def vars_at(self, i: int) -> int:
        return self.num_vars - sum(self.folds[:i])


def rounds(c: WhirConfig) -> list[Round]:
    out: list[Round] = []
    M = len(c.folds)
    for i in range(M):
        p = c.point(i)
        L = p.list_size_log2
        m = c.vars_at(i)
        log_n = m + c.log_inv_rates[i]
        if i == 0 and c.batch_count > 1:
            out.append(Round("batch", math.log2(c.batch_count - 1) + p.line_error(log_n, m, c.field_bits), c.grind_batch))
        if c.regime is not Regime.UDR:
            ood = 2 * L - 1 + c.ood_samples * (m - c.field_bits)
            out.append(Round(f"ood{i}", ood, c.grind_ood))
        for j in range(c.folds[i]):
            # d* = 3 (WHIR Theorem 5.2; was 2 before finding C-9)
            e = log2_sum([math.log2(3.0) + L - c.field_bits, p.line_error(log_n - j, m - j, c.field_bits)])
            out.append(Round(f"fold{i}.{j}", e, c.grind_fold))
        q = query_error(p, c.queries[i])
        if i < M - 1:
            comb = math.log2(c.queries[i] + c.ood_samples) + L - c.field_bits
            out.append(Round(f"query{i}", log2_sum([q, comb]), c.grind_query))
        else:
            out.append(Round("final", q, c.grind_query))
    return out


def _paths(log_leaves: float, queries: int, cap: int) -> float:
    distinct = max(0.0, log_leaves - max(cap, math.log2(max(1, queries))))
    return queries * distinct + 2**cap


def size_bytes(c: WhirConfig) -> dict[str, float]:
    h = c.fs.digest_bits / 8
    total_q = 0.0
    other = 0.0
    for i, k in enumerate(c.folds):
        m = c.vars_at(i)
        elem = c.base_bytes if i == 0 else c.ext_bytes
        t = c.queries[i]
        log_leaves = m + c.log_inv_rates[i] - k
        total_q += t * ((2**k) * elem + c.salt_bytes) + _paths(log_leaves, t, c.cap_height) * h
        other += h + c.ood_samples * c.ext_bytes + 3 * k * c.ext_bytes + 8 * 3
    final = (2 ** c.vars_at(len(c.folds))) * c.ext_bytes
    return {"queries": total_q, "rounds": other, "final": final, "extra": c.extra_bytes,
            "total": total_q + other + final + c.extra_bytes}


def solve(c: WhirConfig, target, quantum: bool = True) -> WhirConfig:
    """Smallest query count per round meeting `target`. Algebraic rounds must meet it with their grind."""
    need = resolve_need(target, len(rounds(c)), c.fs, quantum)
    for i in range(len(c.folds)):
        per_query = -math.log2(c.point(i).query_agreement)
        c.queries[i] = max(1, math.ceil((need - c.grind_query) / per_query))
    for _ in range(64):  # the combination term grows with t; step until every query round holds
        weak = [r for r in rounds(c) if r.effective_bits < need]
        bad_q = [r for r in weak if r.name.startswith("query") or r.name == "final"]
        if not bad_q:
            break
        for r in bad_q:
            i = len(c.folds) - 1 if r.name == "final" else int(r.name[5:])
            c.queries[i] += 1
    for r in rounds(c):
        if r.effective_bits < need:
            raise ValueError(f"{c.name}: round {r.name} gives {r.effective_bits:.1f} < {need:.1f} bits")
    return c


@dataclass
class BaseFoldConfig:
    """BaseFold / FRI-Binius: a multilinear codeword folded k variables per round at constant rate,
    the same query positions followed through every layer, one query round at the end."""

    name: str
    field_bits: float
    base_bytes: int
    ext_bytes: int
    num_vars: int
    log_inv_rate: int
    fold: int
    queries: int = 100
    regime: Regime = Regime.UDR
    johnson_m: float = 10.0
    grind_fold: float = 0.0
    grind_query: float = 0.0
    salt_bytes: int = 0
    cap_height: int = 0
    residual_vars: int = 0
    extra_bytes: int = 0
    fs: FsParams = field(default_factory=FsParams)

    @property
    def point(self) -> RegimePoint:
        return RegimePoint(self.regime, 2.0 ** -self.log_inv_rate, self.johnson_m)

    @property
    def layers(self) -> int:
        return max(1, math.ceil((self.num_vars - self.residual_vars) / self.fold))


def basefold_rounds(c: BaseFoldConfig) -> list[Round]:
    p = c.point
    L = p.list_size_log2
    out = []
    for j in range(c.num_vars - c.residual_vars):
        m = c.num_vars - j
        e = log2_sum([1 + L - c.field_bits, p.line_error(m + c.log_inv_rate, m, c.field_bits)])
        out.append(Round(f"fold.{j}", e, c.grind_fold))
    out.append(Round("query", query_error(p, c.queries), c.grind_query))
    return out


def basefold_size(c: BaseFoldConfig) -> dict[str, float]:
    h = c.fs.digest_bits / 8
    q = 0.0
    for i in range(c.layers):
        m = c.num_vars - i * c.fold
        elem = c.base_bytes if i == 0 else c.ext_bytes
        q += c.queries * ((2**c.fold) * elem + c.salt_bytes) + _paths(m + c.log_inv_rate - c.fold, c.queries, c.cap_height) * h
    other = c.layers * h + 3 * (c.num_vars - c.residual_vars) * c.ext_bytes + 16
    final = (2**c.residual_vars) * c.ext_bytes
    return {"queries": q, "rounds": other, "final": final, "extra": c.extra_bytes,
            "total": q + other + final + c.extra_bytes}


def basefold_solve(c: BaseFoldConfig, target, quantum: bool = True) -> BaseFoldConfig:
    rs = basefold_rounds(c)
    need = resolve_need(target, len(rs), c.fs, quantum)
    for r in rs:
        if r.name != "query" and r.effective_bits < need:
            raise ValueError(f"{c.name}: round {r.name} gives {r.effective_bits:.1f} < {need:.1f} bits")
    c.queries = max(1, math.ceil((need - c.grind_query) / -math.log2(c.point.query_agreement)))
    return c


def check(c: WhirConfig) -> float:
    """Smallest effective bits over rounds (diagnostic)."""
    rs = rounds(c)
    return min((r.effective_bits for r in rs if r.error_log2 != NEG_INF), default=math.inf)
