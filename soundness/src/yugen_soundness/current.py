"""Revision 3 of the design basis (2026-11-19): the rows being built, at category 1 for the tree of
specification 0.3, no grinding, unique decoding, proven bounds only.

The tree: at most 2^14 leaves, sub-bundles of at most 16 leaves, three merge levels of arity at most
16. Packed full (every node but the last of its level full) it has 2^14 + 2^10 + 2^6 + 2^2 + 1 =
17,477 proofs (`TREE.proofs`); the union bound runs over them (soundness-method.md 8.5b).

System A (leanVM, yugen-proof-a / yugen-proof-a-zk):
  * leaf: the hiding opening W-I as built (yugen-proof-a-zk docs/zero-knowledge.md section 15,
    vendor/leanMultisig/crates/verifier/src/wi.rs `layout`), at the TRUE rates lf_i / 2^log_domain_i,
    with the tail sumcheck (A26) and every zero-knowledge round outside the opening (wi.zk_rounds);
  * the schedule is the row table's (crates/verifier/src/params.rs `derive_config_for`): first fold,
    later folds, the two domain reductions, the residual bound; `row_schedule` reproduces it;
  * nodes: plain WHIR (not hiding, R-9), the node row's schedule.
System B (Binius64, yugen-proof-b2): `binius64.py`.

Every number here is an estimate (E) unless it is one of the measured constants (M) named below.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field

from . import binius64, whir, wi
from .bounds import Regime
from .compose import FsParams, Round
from .shipping import OTHER_ROUNDS, ProofTreeTarget, tree_target
from .targets import CAT1, SecurityTarget

# --- the tree ------------------------------------------------------------------------------------


@dataclass(frozen=True)
class TreeShape:
    leaves: int
    per_sub: int
    merge_arity: int
    merge_levels: int

    def level_counts(self) -> list[int]:
        """Proofs per level, every node but the last of its level full."""
        counts = [self.leaves, -(-self.leaves // self.per_sub)]
        for _ in range(self.merge_levels):
            counts.append(-(-counts[-1] // self.merge_arity))
        return counts

    @property
    def proofs(self) -> int:
        return sum(self.level_counts())

    @property
    def proofs_any_packing(self) -> int:
        """Proofs of the largest tree when nodes may have a single child: every leaf on its own path."""
        return self.leaves * (2 + self.merge_levels)


TREE = TreeShape(leaves=2**14, per_sub=16, merge_arity=16, merge_levels=3)
LAYERS = ["leaf", "sub-bundle", "merge 1", "merge 2", "merge 3"]


def target(base: SecurityTarget = CAT1, proofs: int | None = None) -> ProofTreeTarget:
    return tree_target(base, OTHER_ROUNDS, TREE.proofs if proofs is None else proofs)


# --- system A: schedules as the row table builds them --------------------------------------------


def row_schedule(log_n: int, log_inv_rate: int, first: int, fold: int, red0: int, red1: int,
                 residual: int) -> tuple[list[int], list[int]]:
    """`derive_config_for` (verifier/src/whir.rs): first fold `first`, then `fold`; the log inverse rate
    grows by (previous fold - reduction), the reduction `red0` after level 0 and `red1` after; folding
    stops once at most `residual` variables remain."""
    folds, rates = [first], [log_inv_rate]
    remaining = log_n - first
    while remaining > residual:
        red = red0 if len(folds) == 1 else red1
        rates.append(rates[-1] + folds[-1] - red)
        f = min(fold, remaining)
        remaining -= f
        folds.append(f)
    return folds, rates


# Query lists by level rate (verifier/src/params.rs, S): row 5/6 (135.58 bits) and rows 7 to 9 (152.3 bits).
CAT1_UD_QUERIES = [0, 327, 200, 164, 149, 142, 139, 138, 137, 136, 136]
CAT1_TREE_UD_QUERIES = [0, 367, 225, 184, 167, 160, 156, 155, 154, 153, 153]


@dataclass(frozen=True)
class ARow:
    """A row of the parameter table as `ParamSet` holds it."""

    name: str
    first: int
    fold: int
    red0: int
    red1: int
    residual: int
    queries: tuple[int, ...] = tuple(CAT1_TREE_UD_QUERIES)  # by level rate

    def schedule(self, log_n: int, rate: int):
        return row_schedule(log_n, rate, self.first, self.fold, self.red0, self.red1, self.residual)


ROW6 = ARow("row 6 (built: folds 5, 3; reductions 1, 1; residual 2^10; 135.58-bit list)", 5, 3, 1, 1, 10, tuple(CAT1_UD_QUERIES))
ROW8 = ARow("row 8 (leaf: folds 6, 3; reductions 3, 3; residual 2^10)", 6, 3, 3, 3, 10)
ROW8_R5 = ARow("row 8 with residual 2^5", 6, 3, 3, 3, 5)
ROW9 = ARow("row 9 (node: folds 5, 3; reductions 1, 1; residual 2^9)", 5, 3, 1, 1, 9)
# The other candidates of yugen-proof-a docs/recursion.md 9.4 (row 5's table, here with the tree list).
NODE_CANDIDATES = [
    ARow("row 5 shape (folds 5, 3; reductions 1, 1; residual 2^10)", 5, 3, 1, 1, 10),
    ARow("residual 2^5", 5, 3, 1, 1, 5),
    ARow("reductions 3, 3", 5, 3, 3, 3, 10),
    ARow("fold 6 at level 0", 6, 3, 1, 1, 10),
    ARow("fold 6, reductions 3, 3", 6, 3, 3, 3, 10),
    ARow("fold 6 and 4, reductions 3, 3", 6, 4, 3, 3, 10),
    ROW9,
]

A_LEAF_VARS = 22  # the wallet statement's stack, 2^22 words (M: yugen-proof-a docs/measurements.md)
A_LEAF_RATE = 2  # 1/4 (row 6's wallet runs)
FS256 = FsParams(digest_bits=256)

# Measured proofs on the 256-bit field (M):
#  the row-6 wallet leaf with the hiding opening, masked table sumcheck and gadget: 483,256 B, queries
#  200/139/137/136 (yugen-proof-a-zk docs/zero-knowledge.md 15.4);
A_ROW6_WI_BYTES = 483_256
#  node proofs at rate 1/2 under row 5's schedule (yugen-proof-a docs/recursion.md 9.7): (stack, residual, bytes)
A_NODE_ANCHORS = [(24, 10, 575_188), (25, 10, 645_676), (25, 10, 621_676), (24, 9, 625_604)]
# Node statement (M, recursion.md 9.7): a sub-bundle of one leaf 516,999 cycles and 16,449,536 words;
# 507,400 cycles per further leaf; a merge of a merge at residual 2^9 428,189 cycles per child and
# 15,695,872 words at 428,510 cycles.
A_LEAF_VERIFY_CYCLES = 507_400
A_SUB_FIXED_CYCLES = 516_999 - 507_400
A_SUB_WORDS_PER_CYCLE = 16_449_536 / 516_999
A_CHILD_VERIFY_CYCLES = 428_189
A_MERGE_WORDS_PER_CYCLE = 15_695_872 / 428_510


def a_config(row: ARow, log_n: int, rate: int, salt: int, queries: list[int] | None = None,
             field_bits: int = 256, digest_bits: int = 256) -> whir.WhirConfig:
    """Revision 7: the challenge field (`field_bits`, elements of field_bits / 8 bytes past level 0) and the
    digest length are inputs; the defaults are the 256-bit field and 256-bit digests of revisions 3 to 6."""
    folds, rates = row.schedule(log_n, rate)
    q = queries or [row.queries[min(r, len(row.queries) - 1)] for r in rates]
    fs = copy.deepcopy(FS256) if digest_bits == 256 else FsParams(digest_bits=digest_bits)
    # Revision 5: system A's plain levels at the true rate (finding W-1); the W-I leaf (wi.layout) had it already.
    return whir.WhirConfig(row.name, field_bits, 8, field_bits // 8, log_n, rates, folds, list(q), regime=Regime.UDR,
                           salt_bytes=salt, fs=fs, true_rate=True)


def a_leaf_rounds(c: whir.WhirConfig) -> list[Round]:
    return wi.rounds(c, "A", wi.A_WALLET_ZK)


def a_extra_leaf() -> float:
    """Non-opening bytes of the zero-knowledge leaf at 256 bits, fitted to the measured row-6 proof."""
    return A_ROW6_WI_BYTES - wi.size_bytes(a_config(ROW6, A_LEAF_VARS, A_LEAF_RATE, 32), "A")["total"]


def a_extra_node() -> tuple[float, dict]:
    """Non-opening bytes of a node proof at 256 bits (mean over the measured node proofs), and the
    model's error at each."""
    def model(m, res):
        r = ARow("row 5", 5, 3, 1, 1, res, tuple(CAT1_UD_QUERIES))
        return whir.size_bytes(a_config(r, m, 1, 0))["total"]
    x = sum(b - model(m, res) for m, res, b in A_NODE_ANCHORS) / len(A_NODE_ANCHORS)
    return x, {f"2^{m} stack, residual 2^{res}, {b:,} B": (model(m, res) + x) / b - 1 for m, res, b in A_NODE_ANCHORS}


@dataclass
class ALeafCheck:
    row: ARow
    config: whir.WhirConfig
    layout: list
    rounds: list[Round]
    need: float
    size: float

    @property
    def query_bits(self) -> list[float]:
        return [r.effective_bits for r in self.rounds if r.name.startswith("query") or r.name == "final"]

    @property
    def meets(self) -> bool:
        return min(r.effective_bits for r in self.rounds) >= self.need - 1e-9

    @property
    def shortfall(self) -> float:
        return max(0.0, self.need - min(r.effective_bits for r in self.rounds))


def a_leaf_check(row: ARow, t=None, queries: list[int] | None = None, log_n: int = A_LEAF_VARS,
                 rate: int = A_LEAF_RATE) -> ALeafCheck:
    """A W-I leaf at the row's counts (or `queries`), against the tree target, at the true rates."""
    t = t or target()
    c = a_config(row, log_n, rate, 32, queries)
    lv = wi.layout(c, "A")
    rs = a_leaf_rounds(c)
    return ALeafCheck(row, c, lv, rs, t.need_bits(len(rs), c.fs), wi.size_bytes(c, "A")["total"] + a_extra_leaf())


def a_leaf_solve(row: ARow, t=None, log_n: int = A_LEAF_VARS, rate: int = A_LEAF_RATE) -> ALeafCheck:
    """The smallest per-level counts at the row's schedule that meet the target at the true rates."""
    t = t or target()
    c = wi.solve(a_config(row, log_n, rate, 32), "A", t, wi.A_WALLET_ZK)
    return a_leaf_check(row, t, list(c.queries), log_n, rate)


def nominal_bits(c: whir.WhirConfig) -> list[float]:
    """What each query round would give at the nominal rates 2^-r_i (the non-hiding opening's)."""
    return [-q * math.log2((1 + 2.0 ** -r) / 2) for q, r in zip(c.queries, c.log_inv_rates)]


def a_leaf_best(t=None, rate: int = A_LEAF_RATE) -> ALeafCheck:
    """Smallest leaf over schedules the row table can express (first fold 4 to 8, later folds 3 to 5,
    reductions 1 to the fold, residual 5 to 12)."""
    t = t or target()
    best = None
    for first in range(4, 9):
        for fold in range(3, 6):
            for red0 in sorted({1, 3, first}):
                for red1 in sorted({1, 3, fold}):
                    if red0 > first or red1 > fold:
                        continue
                    for residual in range(5, 13):
                        row = ARow(f"folds {first}, {fold}; reductions {red0}, {red1}; residual 2^{residual}",
                                   first, fold, red0, red1, residual)
                        try:
                            ch = a_leaf_solve(row, t, rate=rate)
                        except ValueError:
                            continue
                        if best is None or ch.size < best.size:
                            best = ch
    return best


@dataclass
class ANodeCheck:
    row: ARow
    log_n: int
    rate: int
    config: whir.WhirConfig
    rounds: list[Round]
    need: float
    size: float

    @property
    def meets(self) -> bool:
        return min(r.effective_bits for r in self.rounds) >= self.need - 1e-9

    @property
    def weakest(self) -> Round:
        return min(self.rounds, key=lambda r: r.effective_bits)


def a_node_check(row: ARow, log_n: int, rate: int, t=None, queries: list[int] | None = None) -> ANodeCheck:
    t = t or target()
    c = a_config(row, log_n, rate, 0, queries)
    rs = whir.rounds(c)
    return ANodeCheck(row, log_n, rate, c, rs, t.need_bits(len(rs), c.fs), whir.size_bytes(c)["total"] + a_extra_node()[0])


def a_node_solve(row: ARow, log_n: int, rate: int, t=None) -> ANodeCheck:
    t = t or target()
    folds, _ = row.schedule(log_n, rate)
    c = whir.solve(a_config(row, log_n, rate, 0, [1] * len(folds)), t)
    return a_node_check(row, log_n, rate, t, list(c.queries))


def a_node_stacks(leaf: ALeafCheck, node: ARow, node_rate: int = 1) -> dict[str, float]:
    """Committed words of a full-arity node (E): measured cycles per verified child scaled by the
    query sums of the child's row against the row the cycles were measured at."""
    leaf_ratio = sum(leaf.config.queries) / sum(a_config(ROW6, A_LEAF_VARS, A_LEAF_RATE, 32).queries)
    sub = (A_SUB_FIXED_CYCLES + TREE.per_sub * A_LEAF_VERIFY_CYCLES * leaf_ratio) * A_SUB_WORDS_PER_CYCLE
    row5 = ARow("row 5 r9", 5, 3, 1, 1, 9, tuple(CAT1_UD_QUERIES))
    child_ratio = sum(a_config(node, 24, node_rate, 0).queries) / sum(a_config(row5, 24, node_rate, 0).queries)
    merge = TREE.merge_arity * A_CHILD_VERIFY_CYCLES * child_ratio * A_MERGE_WORDS_PER_CYCLE
    return {"sub-bundle": sub, "merge": merge}


# --- tables ----------------------------------------------------------------------------------------


def _kib(b: float) -> str:
    return f"{b / 1024:,.0f}"


def a_leaf_table(ch: ALeafCheck, label: str) -> list[str]:
    nb = nominal_bits(ch.config)
    out = [f"**{label}**: {ch.row.name}; stack 2^{ch.config.num_vars}, rate 1/{2 ** ch.config.log_inv_rates[0]}; "
           f"{len(ch.rounds)} rounds in the proof's list, {OTHER_ROUNDS} more outside it; need {ch.need:.2f} bits a round; "
           f"size {_kib(ch.size)} KiB (E); {'meets' if ch.meets else f'**short by {ch.shortfall:.2f} bits**'}", "",
           "| Level | Fold | Domain (rows) | Nominal rate | Folded lane lf | True rate | Queries | Bits at the nominal rate | Bits at the true rate |",
           "|---|---|---|---|---|---|---|---|---|"]
    qb = ch.query_bits
    for i, (k, lv) in enumerate(zip(ch.config.folds, ch.layout)):
        out.append(f"| {i} | {k} | 2^{lv.rows_log} | 2^-{ch.config.log_inv_rates[i]} | {lv.degree:,} | {lv.rate:.5f} (2^{math.log2(lv.rate):.2f}) "
                   f"| {ch.config.queries[i]} | {nb[i]:.2f} | {qb[i]:.2f} |")
    return out


def tables() -> list[str]:
    t = target()
    out = [f"Tree: {TREE.leaves:,} leaves, sub-bundles of {TREE.per_sub}, {TREE.merge_levels} merge levels of arity "
           f"{TREE.merge_arity}: levels {TREE.level_counts()}, {TREE.proofs:,} proofs (2^{math.log2(TREE.proofs):.3f}); "
           f"union bound, one attempt; {OTHER_ROUNDS} rounds outside each proof's listed rounds in k; no grinding; "
           f"unique decoding; GF(2^256) challenges; 256-bit digests.", ""]
    # A: row 6 as built and the true-rate rows
    built = a_leaf_check(ROW6, t)
    out += ["## System A leaf (W-I, true rates)", ""] + a_leaf_table(built, "Row 6 as built (nominal-rate counts)") + [""]
    sol = a_leaf_solve(ROW6, t)
    out += a_leaf_table(sol, "Row 6's schedule, counts solved at the true rates (the row to paste)") + [""]
    out += [f"Paste: `initial_folding_factor: {ROW6.first}, subsequent_folding_factor: {ROW6.fold}, "
            f"rs_domain_initial_reduction: {ROW6.red0}, rs_domain_subsequent_reduction: {ROW6.red1}, residual_max_log: "
            f"{ROW6.residual}`, queries per level {list(sol.config.queries)} (the tree list `[0, 367, 225, 184, 167, 160, 156, 155, "
            f"154, 153, 153]` by level rate gives {[CAT1_TREE_UD_QUERIES[min(r, 10)] for r in sol.config.log_inv_rates]}).", ""]
    best = a_leaf_best(t)
    out += a_leaf_table(best, "Smallest leaf over the row table's schedules") + [""]
    # A: recursion team's candidates
    out += ["## System A candidates of yugen-proof-a docs/recursion.md 9.4 and rows 7 to 9", "",
            "| Candidate | Layer | Stack, rate | Folds; level rates | Queries (row's list) | Need | Weakest round (bits) | Meets | Nearest row that meets: queries | Size KiB (E) |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for row in (ROW8, ROW8_R5):
        need = "-"
        try:
            ch = a_leaf_check(row, t)
            weak = min(ch.rounds, key=lambda r: r.effective_bits)
            res = f"{weak.name}: {weak.effective_bits:.2f}"
            meets = "yes" if ch.meets else "no"
            folds, rates = ch.config.folds, ch.config.log_inv_rates
            q = ch.config.queries
            need = f"{ch.need:.2f}"
        except ValueError as e:
            folds, rates = row.schedule(A_LEAF_VARS, A_LEAF_RATE)
            res, meets, q = f"layout refused: {e}", "no", [row.queries[min(r, 10)] for r in rates]
        try:
            s = a_leaf_solve(row, t)
            near = f"{list(s.config.queries)}; {_kib(s.size)} KiB"
        except ValueError:
            near = _a_leaf_nearest_residual(row, t)
        out.append(f"| {row.name}, W-I | leaf | 2^{A_LEAF_VARS}, 1/{2 ** A_LEAF_RATE} | {folds}; {rates} | {q} | {need} "
                   f"| {res} | {meets} | {near} | |")
    for row in NODE_CANDIDATES:
        for m in (24, 29):
            for rate in (1, 2):
                ch = a_node_check(row, m, rate, t)
                w = ch.weakest
                near = "" if ch.meets else str(a_node_solve(row, m, rate, t).config.queries)
                out.append(f"| {row.name} | node | 2^{m}, 1/{2 ** rate} | {ch.config.folds}; {ch.config.log_inv_rates} | {ch.config.queries} "
                           f"| {ch.need:.2f} | {w.name}: {w.effective_bits:.2f} | {'yes' if ch.meets else 'no'} | {near} | {_kib(ch.size)} |")
    stacks = a_node_stacks(sol, ROW9)
    out += ["", f"Full-arity node statements (E): sub-bundle of {TREE.per_sub} leaves 2^{math.log2(stacks['sub-bundle']):.2f} words, "
            f"merge of {TREE.merge_arity} 2^{math.log2(stacks['merge']):.2f} words (stack 2^{math.ceil(math.log2(max(stacks.values())))})."]
    x, errs = a_extra_node()
    out += ["", f"Calibration: leaf non-opening bytes {a_extra_leaf():,.0f} B (fitted to the measured row-6 W-I proof, "
            f"{A_ROW6_WI_BYTES:,} B); node non-opening bytes {x:,.0f} B, errors " + "; ".join(f"{k} {v:+.1%}" for k, v in errs.items())]
    # B
    out += [""] + a_bound_tables()
    out += ["", "## System B (Binius64), revision 4: counted rounds, 20,000 proofs, the field variants", ""] + b_tables_r4()
    out += ["", "## System B (Binius64), revision 3 model (superseded: 512 other rounds, 17,477 proofs, estimated layout)", ""] + b_tables(t)
    return out


def _a_leaf_nearest_residual(row: ARow, t) -> str:
    for res in range(row.residual + 1, 14):
        r2 = ARow(f"{row.name} -> residual 2^{res}", row.first, row.fold, row.red0, row.red1, res)
        try:
            s = a_leaf_solve(r2, t)
            return f"no count reaches the target; nearest: residual 2^{res}, {list(s.config.queries)}; {_kib(s.size)} KiB"
        except ValueError:
            continue
    return "none up to residual 2^13"


# --- system B rows -----------------------------------------------------------------------------------

B_LEAF_RATES = (1, 2, 3, 4)
B_NODE_RATE = {"sub-bundle": 1, "merge 1": 3, "merge 2": 3, "merge 3": 3}


def b_rows(t=None, leaf_rate: int = 3, node_rates: dict | None = None, layout: str = "committed") -> list[binius64.B64Row]:
    t = t or target()
    node_rates = node_rates or B_NODE_RATE
    rows = [binius64.leaf_row(t, leaf_rate, layout)]
    for layer in LAYERS[1:]:
        n = TREE.per_sub if layer == "sub-bundle" else TREE.merge_arity
        rows.append(binius64.node_row(layer, t, node_rates[layer], n, rows[-1]))
    return rows


def _b_table(rows) -> list[str]:
    out = ["| Layer | Rate | Statement committed | Queries | Fold arities; terminal | Need (bits) | Field needed (bits) | Size KiB (E) "
           "| Under 1.75 MiB | Rows of the slot verifying it in its parent (E) |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r.layer} | 1/{2 ** r.rate} | {r.statement} | {r.proof.queries} | {'/'.join(map(str, r.proof.arities))}; "
                   f"{r.proof.terminal:,} | {r.need:.2f} | {r.field_min}: GF(2^256) | {_kib(r.size)} "
                   f"| {'yes' if r.size <= PROOF_LIMIT else '**no**'} | {r.child_rows / 1e6:,.1f} M |")
    return out


PROOF_LIMIT = int(1.75 * 2**20)


def b_tables(t) -> list[str]:
    c = binius64.cal()
    out = ["Sub-bundles at rate 1/2, merges at 1/8 (the pin's cheaper choices, parameters.md 3.3):", ""]
    out += _b_table(b_rows(t)) + ["", "Every node at rate 1/8:", ""]
    out += _b_table(b_rows(t, node_rates={k: 3 for k in B_NODE_RATE}))
    out += ["", "Leaf rate trade (zero-knowledge leaf, committed derivation; pin layout in brackets):", "",
            "| Leaf rate | Queries | Leaf KiB (E) | Slot rows in the sub-bundle (E) |", "|---|---|---|---|"]
    for rate in B_LEAF_RATES:
        a = binius64.leaf_row(t, rate, "committed")
        b = binius64.leaf_row(t, rate, "pin")
        out.append(f"| 1/{2 ** rate} | {a.proof.queries} | {_kib(a.size)} ({_kib(b.size)}) | {a.child_rows / 1e6:,.1f} M ({b.child_rows / 1e6:,.1f} M) |")
    out += ["", "Calibration (128-bit, measured proofs; doubled `other` at 256 bits): " + "; ".join(
        f"{k} {v:,.0f} B" for k, v in c.items() if not k.endswith("errors")) + "; errors " + "; ".join(
        f"{k}: " + ", ".join(f"{a} {b:+.1%}" for a, b in v.items()) for k, v in c.items() if k.endswith("errors"))]
    return out


# --- revision 4 (2026-11-19): the tree bound of specification 0.3.2 and the counted rounds ----------------

TREE_BOUND = 20_000  # MAX_TREE_PROOFS of specification 0.3.2 (yugen-proof-b2 src/params.rs; yugen-proof-a-zk 17.5)
A_ROW6_MASKED_BYTES = 600_340  # M: row 6, every mask, rate 1/4, counts 226/157/154/154 (yugen-proof-a-zk zero-knowledge.md 17.4)
A_BOUND_QUERIES = [226, 157, 154, 154]  # params::CAT1_WI_QUERIES at the wallet shape (17.5)


def target_bound() -> ProofTreeTarget:
    return target(proofs=TREE_BOUND)


def a_leaf_bound() -> ALeafCheck:
    """Row 6's schedule solved at the true rates for 20,000 proofs with the built mask counts."""
    return a_leaf_solve(ROW6, target_bound())


def a_bound_tables() -> list[str]:
    t = target_bound()
    sol = a_leaf_bound()
    built = a_leaf_check(ROW6, t, A_BOUND_QUERIES)
    z = wi.A_WALLET_ZK
    out = [f"## System A at the tree bound of specification 0.3.2 ({TREE_BOUND:,} proofs)", "",
           f"Mask counts of the code (yugen-proof-a-zk zero-knowledge.md 18.6, zk-merge-notes.md 3; revision 6): {z.bus_layers} bus layers, {z.keccak_layers} Keccak layers, "
           f"{z.s9_sumchecks} masked chains in S9, column A 2^{z.gadget_log_len}, {z.gadget_claims} gadget claims: "
           f"{len(sol.rounds)} listed rounds (the implementers' run used the tool's larger bus and S9 counts: 88).", ""]
    out += a_leaf_table(sol, "Row 6's schedule solved at 20,000 proofs") + [""]
    out += [f"Built counts {A_BOUND_QUERIES}: {'meet' if built.meets else 'do NOT meet'} (weakest round "
            f"{min(r.effective_bits for r in built.rounds):.2f} of {built.need:.2f} bits); solved counts {list(sol.config.queries)}; "
            f"each built count less by one: {['meets' if a_leaf_check(ROW6, t, [q - (i == j) for j, q in enumerate(A_BOUND_QUERIES)]).meets else 'fails' for i in range(4)]}.",
            f"Measured masked proof at these counts: {A_ROW6_MASKED_BYTES:,} B = {_kib(A_ROW6_MASKED_BYTES)} KiB (M).", "",
            "Node rows at 20,000 proofs (plain WHIR, row 9):", "",
            "| Stack, rate | Row 9's list | Weakest round | Need | Meets | Solved counts |", "|---|---|---|---|---|---|"]
    for m in (24, 29):
        for rate in (1, 2):
            ch = a_node_check(ROW9, m, rate, t)
            s2 = a_node_solve(ROW9, m, rate, t)
            out.append(f"| 2^{m}, 1/{2 ** rate} | {ch.config.queries} | {ch.weakest.name}: {ch.weakest.effective_bits:.2f} | {ch.need:.2f} "
                       f"| {'yes' if ch.meets else '**no**'} | {list(s2.config.queries)} |")
    return out


B_K_NODE_BOUND = 663  # every node: 246 (a node of 2^30 AND rows) + 417 (batching, level 3) (parameters.md 2a.4)
B_ROW_BUDGET = 600  # the row's budget: challenges a proof on average (parameters.md 2a.2)
B_LEAVES = 2**14


def b_need(variant=None) -> dict:
    """Bits a round for system B: from the counted challenges of the largest tree, and at the row's budget."""
    v = variant or binius64.ALL256
    k_leaf = binius64.k_of(binius64.leaf_shape(v))
    groups = [(B_LEAVES, k_leaf), (TREE_BOUND - B_LEAVES, B_K_NODE_BOUND)]
    return {"k_leaf": k_leaf, "counted": binius64.tree_need(CAT1, groups),
            "budget": binius64.tree_need(CAT1, [(TREE_BOUND, B_ROW_BUDGET)]),
            "sum": sum(n * (1 + k) for n, k in groups)}


def b_field_check(need: float, field_bits: int) -> dict:
    """The weakest algebraic round of the measured leaf and of the largest node, at a challenge field."""
    out = {}
    for name, sh in (("leaf", binius64.leaf_shape(binius64.ALL256)),
                     ("node 2^30 rows", binius64.Shape(a=30, b=29, w=30, p=12, v=28, kappa=8))):
        rs = [r for r in binius64.rounds_counted(sh, 3, 184, field_bits) if r.name != "query"]
        worst = min(rs, key=lambda r: r.effective_bits)
        out[name] = (worst.name, worst.effective_bits, worst.effective_bits >= need,
                     math.ceil(need + worst.error_log2 + field_bits))
    return out


def b_tables_r4() -> list[str]:
    n = b_need()
    need = n["budget"]
    out = [f"Tree bound {TREE_BOUND:,} proofs. Counted challenges (parameters.md 2a.4): leaf k = {n['k_leaf']}, every node "
           f"k <= {B_K_NODE_BOUND}; largest tree sum of (1 + k) = {n['sum']:,} = 2^{math.log2(n['sum']):.2f}: {n['counted']:.2f} bits a "
           f"round. Row budget {B_ROW_BUDGET} challenges a proof on average: **{need:.2f} bits a round** (the row is solved at the budget).",
           "", "| Rate | Bits a query | Queries | Query round reaches |", "|---|---|---|---|"]
    for rate in B_LEAF_RATES:
        q = binius64.queries_for(need, rate)
        per = -math.log2((1 + 2.0**-rate) / 2)
        out.append(f"| 1/{2 ** rate} | {per:.4f} | {q} | {q * per:.2f} |")
    out += ["", "| Challenge field | Leaf: weakest algebraic round (bits) | Node of 2^30 rows: weakest (bits) | Meets | Field needed (bits) |",
            "|---|---|---|---|---|"]
    for fb in (128, 192, 256):
        c = b_field_check(need, fb)
        out.append(f"| 2^{fb} | {c['leaf'][0]}: {c['leaf'][1]:.1f} | {c['node 2^30 rows'][0]}: {c['node 2^30 rows'][1]:.1f} "
                   f"| {'yes' if c['leaf'][2] and c['node 2^30 rows'][2] else '**no**'} | {max(c['leaf'][3], c['node 2^30 rows'][3])} |")
    out += ["", "Rate 1/8, zero-knowledge wallet leaf (pin layout) and nodes, by where the objects live "
            "(docs/binius-extension-challenges.md). M: measured build; E: estimate.", "",
            "| Variant | Status | Queries | Leaf k | Wrapper constraints (log2 padded) | Wrapper private wires (log2) | Trace / wrapper / mask symbol (B) "
            "| Ring-switch message (bits) | Leaf KiB | Node KiB (2^27 words) | Leaf slot: AND rows, BMUL rows (E) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in binius64.VARIANTS:
        q = 116 if v.challenge == 128 else binius64.queries_for(need, 3)
        sh = binius64.leaf_shape(v)
        w = binius64.wrapper_counts(v, sh.p)
        a, bm = binius64.leaf_slot_rows(v, 3, q)
        out.append(f"| {v.name} | {v.status} | {q}{' (96-bit level)' if v.challenge == 128 else ''} | {binius64.k_of(sh)} | {w['constraints']:,} (2^{v.leaf_c}) "
                   f"| {w['private']:,} (2^{v.leaf_oracles[1]}) | {v.alphabet} / {v.wrapper_alphabet} / {v.mask} | {v.rs_rows * v.challenge:,} "
                   f"| {_kib(binius64.leaf_size(v, 3, q))} | {_kib(binius64.node_size(v, 27, 3, q))} | {a / 1e6:.2f} M, {bm / 1e6:.2f} M |")
    c = binius64.cal256()
    out += ["", f"Calibration at 256 bits: non-opening bytes leaf {c['leaf']:,.0f}, node {c['node']:,.0f} (fitted to the measured all-GF(2^256) "
            "proofs); leaf errors " + ", ".join(f"{k} {e:+.1%}" for k, e in c["leaf_errors"].items()) + ".", "",
            "Candidate, NOT a row (protocol theorem unconfirmed): the Johnson regime with BCIKS20's proven proximity gap, eta = sqrt(rho)/20:", "",
            "| Message (log2) | Rate | Queries | Bits a query | Fold round (bits) | Meets |", "|---|---|---|---|---|---|"]
    for lm in (20, 27, 31):
        for rate in (3, 4):
            j = binius64.johnson_bciks(lm, rate, need)
            out.append(f"| {lm} | 1/{2 ** rate} | {j['queries']} | {j['bits_per_query']:.3f} | {j['fold_bits']:.1f} | {'yes' if j['meets'] else 'no'} |")
    return out
