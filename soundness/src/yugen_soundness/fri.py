"""A univariate STARK with DEEP-FRI (system B's KoalaBear configuration, and FRI-shaped binary PCSs).

Round structure (one verifier message each):
  ali      random combination of the C constraints            C * L / |F|          (UNCONFIRMED form)
  deep     out-of-domain point                                L^2 * D * k / |F|    (UNCONFIRMED form)
  batch    powers-batching of the W opened (column, point)    (W - 1) * eps_line(n) (BCIKS20 Thm 1.2, 1.5)
  fold_i   folding by arity 2^a, one round per fold            (2^a - 1) * eps_line(n_i)
  query    s queries                                           alpha^s
The `ali` and `deep` terms are far from binding at the field sizes used here (they sit near
|F| / (C D k)); their exact constants are listed as unconfirmed in docs/soundness-method.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .bounds import Regime, RegimePoint, curve, query_error
from .compose import FsParams, Round, resolve_need


@dataclass
class FriConfig:
    name: str
    field_bits: float  # challenge (extension) field size in bits
    base_bytes: int  # bytes per committed base-field element
    ext_bytes: int  # bytes per challenge-field element
    log_k: int  # log2 of the trace height (polynomial degree bound)
    log_blowup: int
    num_constraints: int
    max_constraint_degree: int
    widths: list[int]  # committed matrices' widths, in base-field elements (main, aux, quotient, ...)
    opening_points: int = 2
    log_arity: int = 3
    log_final: int = 0
    queries: int = 100
    regime: Regime = Regime.UDR
    johnson_m: float = 10.0
    grind_ali: float = 0.0
    grind_deep: float = 0.0
    grind_batch: float = 0.0
    grind_fold: float = 0.0
    grind_query: float = 0.0
    salt_bytes: int = 0  # per opened Merkle leaf (hiding commitments)
    cap_height: int = 0
    extra_bytes: int = 0  # anything outside the PCS not modelled here
    fs: FsParams = field(default_factory=FsParams)

    @property
    def rho(self) -> float:
        return 2.0 ** -self.log_blowup

    @property
    def point(self) -> RegimePoint:
        return RegimePoint(self.regime, self.rho, self.johnson_m)

    @property
    def fold_rounds(self) -> int:
        return max(0, math.ceil((self.log_k - self.log_final) / self.log_arity))


def rounds(c: FriConfig) -> list[Round]:
    p = c.point
    L = p.list_size_log2
    out = [
        Round("ali", math.log2(max(1, c.num_constraints)) + L - c.field_bits, c.grind_ali),
        Round("deep", 2 * L + math.log2(c.max_constraint_degree) + c.log_k - c.field_bits, c.grind_deep),
    ]
    n_open = sum(1 for _ in c.widths)  # one tree per matrix
    total_cols = sum(c.widths) * c.opening_points
    log_n = c.log_k + c.log_blowup
    out.append(Round("batch", curve(total_cols - 1, p.line_error(log_n, c.log_k, c.field_bits)), c.grind_batch))
    for i in range(c.fold_rounds):
        lk = c.log_k - i * c.log_arity
        ln = lk + c.log_blowup
        out.append(Round(f"fold{i}", curve(2**c.log_arity - 1, p.line_error(ln, lk, c.field_bits)), c.grind_fold))
    out.append(Round("query", query_error(p, c.queries), c.grind_query))
    del n_open
    return out


def _paths(log_leaves: float, queries: int, cap: int) -> float:
    """Sibling digests for `queries` openings of a binary tree with 2^log_leaves leaves (deduplicated
    estimate: the top log2(queries) levels are shared)."""
    distinct = max(0.0, log_leaves - max(cap, math.log2(max(1, queries))))
    return queries * distinct + 2**cap


def size_bytes(c: FriConfig) -> dict[str, float]:
    h = c.fs.digest_bits / 8
    log_n = c.log_k + c.log_blowup
    s = c.queries
    trace = 0.0
    for w in c.widths:
        trace += s * (w * c.base_bytes + c.salt_bytes) + _paths(log_n, s, c.cap_height) * h
    fri = 0.0
    for i in range(c.fold_rounds):
        ln = log_n - i * c.log_arity
        fri += s * ((2**c.log_arity) * c.ext_bytes + c.salt_bytes) + _paths(ln - c.log_arity, s, c.cap_height) * h
    fixed = (
        (len(c.widths) + c.fold_rounds) * h
        + sum(c.widths) * c.opening_points * c.ext_bytes
        + (2**c.log_final) * c.ext_bytes
        + 8 * 5
        + c.extra_bytes
    )
    return {"trace_openings": trace, "fri_layers": fri, "fixed": fixed, "total": trace + fri + fixed}


def solve(c: FriConfig, target, quantum: bool = True) -> FriConfig:
    """Smallest query count meeting `target`; raises if an algebraic round cannot meet it with its grind."""
    rs = rounds(c)
    need = resolve_need(target, len(rs), c.fs, quantum)
    for r in rs:
        if r.name != "query" and r.effective_bits < need:
            raise ValueError(f"{c.name}: round {r.name} gives {r.effective_bits:.1f} < {need:.1f} bits")
    per_query = -math.log2(c.point.query_agreement)
    c.queries = max(1, math.ceil((need - c.grind_query) / per_query))
    return c
