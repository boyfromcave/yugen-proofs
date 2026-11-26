"""Revision 5 of the calculator (2026-11-19): true rates on system A's plain rows (finding W-1), Theorem Q's
QROM constants per system, the salt length as an input, and system B's list-decoding candidate rows.

Rows (yugen-proof-a docs/parameters.md section 2 and 2.1, read 2026-11-19; params.rs as that table cites it):
  row 7  the plain leaf: folds 6, 3; reductions 3, 3; residual bound 2^7; queries by level rate from the
         153.0-bit list CAT1_TREE_UD_QUERIES = 369, 226, 185, 168, 161, 157, 155, 154, 154, 154 (r = 1 .. 10)
  row 8  row 7's schedule with the hiding opening W-I and salts (the wallet's zero-knowledge leaf)
  row 9  the node: folds 6, 3; reductions 3, 3; residual bound 2^5; the same list; rate 1/2 (1/4 checked)
  ZK     the zero-knowledge wallet leaf of yugen-proof-a-zk at row 6's schedule with every mask built,
         queries 226 / 157 / 154 / 154 (zero-knowledge.md 17.5; current.A_BOUND_QUERIES)

Finding W-1 (docs/whir-additive-soundness.md section 6, Theorem S0 with Lemmas C0 and B0): the query terms of
level i are taken at the true rate rho_i = (2^mu_i + k_i) / 2^(mu_i + r_i), mu_i the variables left after the
level's k_i folds (whir.WhirConfig.true_rate). W-I rows already used the true rates of their layout (wi.layout).

Node shapes the tree allows (sub-bundles of at most 16 leaves, merges of arity at most 16, three merge levels):
the stack of a node is what varies, and with it the last level's mu. Measured (yugen-proof-a docs/recursion.md
9.10, M): S(1) 14.09 M words (2^24), S(2) 2^25, S(4) 2^26, S(9) 117.70 M (2^27), S(16) 217.58 M (2^28, run
only); M(1) 2^24, M(7 S(9)) 131.60 M (2^27), M(8 S(9)) 145.23 M (2^28). A merge of 16 children of 2^28 stacks is
not measured; at the measured 18.2 to 20.8 M words a child it is under 2^29 (E). The calculator checks every
stack 2^24 to 2^30 (2^30 as headroom) at node rates 1/2 and 1/4: every shape of the tree is one of them.

Two corrected schedules are computed for each shape:
  rule    every query round at 153.0 bits or more at its TRUE rate: q_i = ceil(153.0 / -log2((1 + rho_i)/2)),
          the list's own derivation (parameters.md 2.1) with rho_i true; computable at setup from mu_i, k_i,
          r_i; it equals the list wherever mu_i is large. The recommended rule (margin 0.6 bits or more).
  minimal the smallest per-level counts that meet the shape's need (no margin), for comparison.

Every number is an estimate (E) of the model unless marked M. Provenance: the W-1 finding and Theorem S0 are
Original (the Ycash developers, 2026; whir-additive-soundness.md), resting on BCIKS20 Theorems 4.1, 1.6 and
the pinned leanVM verifier's code for the degree growth (CWYZ26, ePrint 2026/2863, Theorem 5.2 is for the
equal-degree combiner and is only consistent with it; revision 6); the schedules, the cost model and this module are Original (the Ycash
developers, 2026).
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass

from . import binius64, current as cu, johnson, qrom, salts, whir, wi
from .compose import FsParams, Round
from .targets import CAT1, CAT3

TREE_LIST_153 = (0, 369, 226, 185, 168, 161, 157, 155, 154, 154, 154)  # params.rs CAT1_TREE_UD_QUERIES
LIST_BITS = 153.0
ROW7 = cu.ARow("row 7 (leaf, plain: folds 6, 3; reductions 3, 3; residual 2^7)", 6, 3, 3, 3, 7, TREE_LIST_153)
ROW8 = cu.ARow("row 8 (row 7 salted, W-I)", 6, 3, 3, 3, 7, TREE_LIST_153)
ROW9 = cu.ARow("row 9 (node: folds 6, 3; reductions 3, 3; residual 2^5)", 6, 3, 3, 3, 5, TREE_LIST_153)
ZK_QUERIES = (226, 157, 154, 154)
LEAF_SHAPES = ((22, 2), (22, 1))  # the wallet's 2^22 stack (M), rate 1/4 (built) and 1/2
NODE_STACKS = tuple(range(24, 31))
NODE_RATES = (1, 2)
NODE_RATE_ADOPTED = 1
TREE_PROOFS = 20_000
SALT_BITS = salts.LEAD_CHOICE

# Measured in-circuit cost of one verified child (yugen-proof-a docs/recursion.md 9.10, reading 1; M):
LEAF_VERIFY = (380_600, 10_670)  # cycles, Keccak-f per row-7 leaf verified in a sub-bundle (2^22, rate 1/4)
CHILD_VERIFY = (520_000, 21_000)  # cycles, Keccak-f per 2^27 child verified in a merge (rate 1/2)

B_FS = FsParams(digest_bits=256, qrom_c1_log2=qrom.FORMS["B"].c1_log2, qrom_c2_log2=qrom.FORMS["B"].c2_log2)


def target():
    return cu.target(proofs=TREE_PROOFS)


@dataclass(frozen=True)
class FloorTarget:
    """A fixed per-round floor (the 153.0-bit rule) in the interface wi.solve uses."""

    bits: float

    def need_bits(self, rounds_count: int, fs) -> float:
        return self.bits


# --- per-level detail --------------------------------------------------------------------------------


@dataclass(frozen=True)
class LevelInfo:
    level: int
    fold: int
    mu: int
    r: int
    true_rate: float
    queries: int
    nominal_bits: float
    true_bits: float


def levels(c: whir.WhirConfig) -> list[LevelInfo]:
    out = []
    for i, (k, r, q) in enumerate(zip(c.folds, c.log_inv_rates, c.queries)):
        mu = c.vars_at(i) - k
        rho = (2.0**mu + k) / 2.0 ** (mu + r)
        out.append(LevelInfo(i, k, mu, r, rho, q, -q * math.log2((1 + 2.0**-r) / 2), -q * math.log2((1 + rho) / 2)))
    return out


def rule_count(rho: float, bits: float = LIST_BITS) -> int:
    return math.ceil(bits / -math.log2((1 + rho) / 2))


def rule_counts(c: whir.WhirConfig, bits: float = LIST_BITS) -> list[int]:
    return [rule_count(lv.true_rate, bits) for lv in levels(c)]


def _query_rounds(rs: list[Round]) -> list[Round]:
    return [r for r in rs if r.name.startswith("query") or r.name == "final"]


def _level_of(r: Round, c: whir.WhirConfig) -> int:
    return len(c.folds) - 1 if r.name == "final" else int(r.name[5:])


def minimal_counts(row: cu.ARow, log_n: int, rate: int, t=None) -> list[int]:
    """Smallest per-level counts at the true rates for which every round meets the shape's need."""
    t = t or target()
    c = cu.a_config(row, log_n, rate, 0)
    need = t.need_bits(len(whir.rounds(c)), c.fs)
    c.queries = rule_counts(c, need)
    for _ in range(64):
        bad = [r for r in _query_rounds(whir.rounds(c)) if r.effective_bits < need]
        if not bad:
            break
        for r in bad:
            c.queries[_level_of(r, c)] += 1
    for i in range(len(c.queries)):
        while True:
            c.queries[i] -= 1
            if min(r.effective_bits for r in whir.rounds(c)) < need:
                c.queries[i] += 1
                break
    return list(c.queries)


# --- in-circuit cost by count ------------------------------------------------------------------------


def keccak_per_query(c: whir.WhirConfig, i: int, salt_bits: int = 0) -> int:
    """Keccak-f of one opened position at level i (upper figure: full authentication path, no sharing):
    the leaf (2^k lanes of 8-byte K words at level 0, 32-byte E2 scalars after) plus the salt, rate 136;
    one permutation per 64-byte node of a path over 2^(m_i - k_i + r_i) leaves."""
    k = c.folds[i]
    leaf = (2**k) * (c.base_bytes if i == 0 else c.ext_bytes)
    path = c.vars_at(i) - k + c.log_inv_rates[i]
    return (salts.keccak_perms(leaf, salt_bits) if salt_bits else (leaf + 1 + 135) // 136) + path


def keccak_total(c: whir.WhirConfig, salt_bits: int = 0) -> int:
    return sum(q * keccak_per_query(c, i, salt_bits) for i, q in enumerate(c.queries))


def opening_bytes(c: whir.WhirConfig) -> float:
    return whir.size_bytes(c)["total"]


@dataclass
class Shape:
    """One shape of a plain row: the list's counts, the rule's and the minimal ones, with margins."""

    row: cu.ARow
    log_n: int
    rate: int
    need: float
    rounds: int
    folds: list[int]
    rates: list[int]
    mus: list[int]
    list_q: list[int]
    list_weakest: float
    rule_q: list[int]
    rule_weakest: float
    min_q: list[int]
    min_weakest: float
    bytes_rule: float
    bytes_min: float
    keccak_rule: int
    keccak_min: int

    @property
    def list_margin(self) -> float:
        return self.list_weakest - self.need

    @property
    def rule_margin(self) -> float:
        return self.rule_weakest - self.need

    @property
    def min_margin(self) -> float:
        return self.min_weakest - self.need


def _weakest(row, log_n, rate, q) -> float:
    c = cu.a_config(row, log_n, rate, 0, list(q))
    return min(r.effective_bits for r in whir.rounds(c))


def shape(row: cu.ARow, log_n: int, rate: int, t=None) -> Shape:
    t = t or target()
    c = cu.a_config(row, log_n, rate, 0)
    rs = whir.rounds(c)
    need = t.need_bits(len(rs), c.fs)
    lv = levels(c)
    rq = rule_counts(c)
    mq = minimal_counts(row, log_n, rate, t)
    cr = cu.a_config(row, log_n, rate, 0, rq)
    cm = cu.a_config(row, log_n, rate, 0, mq)
    return Shape(row, log_n, rate, need, len(rs), list(c.folds), list(c.log_inv_rates), [l.mu for l in lv],
                 list(c.queries), min(r.effective_bits for r in rs), rq, _weakest(row, log_n, rate, rq), mq,
                 _weakest(row, log_n, rate, mq), opening_bytes(cr) - opening_bytes(c), opening_bytes(cm) - opening_bytes(c),
                 keccak_total(cr) - keccak_total(c), keccak_total(cm) - keccak_total(c))


def node_shapes(t=None) -> list[Shape]:
    return [shape(ROW9, m, r, t) for m in NODE_STACKS for r in NODE_RATES]


def leaf_shapes(t=None) -> list[Shape]:
    return [shape(ROW7, m, r, t) for m, r in LEAF_SHAPES]


def rule_table(kappa: int = 3, rates=(1, 2, 4, 5), mus=range(3, 12)) -> dict[tuple[int, int], int]:
    """The rule's count by (level rate r, mu) for kappa folds; the list's count is the limit mu -> inf."""
    return {(r, mu): rule_count((2.0**mu + kappa) / 2.0 ** (mu + r)) for r in rates for mu in mus}


def cycles_per_keccak(child: str) -> float:
    """Measured cycles per verified child over the model's Keccak-f of that child at the list's counts (E)."""
    if child == "leaf":
        c = cu.a_config(ROW7, 22, 2, 0)
        return LEAF_VERIFY[0] / keccak_total(c)
    c = cu.a_config(ROW9, 27, 1, 0)
    return CHILD_VERIFY[0] / keccak_total(c)


# --- W-I rows (row 8, the zero-knowledge leaf) ----------------------------------------------------------


@dataclass
class WiRow:
    label: str
    rate: int
    queries: list[int]
    need: float
    weakest: float
    rounds: int
    size: float
    true_rates: list[float]

    @property
    def margin(self) -> float:
        return self.weakest - self.need

    @property
    def meets(self) -> bool:
        return self.margin >= -1e-9


def wi_row(label: str, row: cu.ARow, rate: int, queries, salt_bytes: int = SALT_BITS // 8, t=None) -> WiRow:
    t = t or target()
    c = cu.a_config(row, cu.A_LEAF_VARS, rate, salt_bytes, list(queries))
    rs = wi.rounds(c, "A", wi.A_WALLET_ZK)
    lv = wi.layout(c, "A")
    return WiRow(label, rate, list(queries), t.need_bits(len(rs), c.fs), min(r.effective_bits for r in rs), len(rs),
                 wi.size_bytes(c, "A")["total"] + cu.a_extra_leaf(), [l.rate for l in lv])


def wi_solve(row: cu.ARow, rate: int, floor: float | None = None) -> list[int]:
    """Row 8's per-level counts: minimal at the need, or with every query round at `floor` bits."""
    tt = target() if floor is None else FloorTarget(floor)
    c = wi.solve(cu.a_config(row, cu.A_LEAF_VARS, rate, SALT_BITS // 8), "A", tt, wi.A_WALLET_ZK)
    return list(c.queries)


# --- QROM and B ----------------------------------------------------------------------------------------


def b_rows(need: float) -> list[johnson.BRow]:
    return [johnson.row("ud", need), johnson.row("haboeck", need, 10), johnson.row("dkt", need, 10),
            johnson.row("dkt", need, 153)]


def b_need() -> float:
    """System B's per-round need at the row budget (600 challenges a proof), with Theorem Q's form-C C1 = 24."""
    return binius64.tree_need(CAT1, [(TREE_PROOFS, cu.B_ROW_BUDGET)], B_FS)


@dataclass
class Certificate:
    a_e: float  # weakest round over system A's corrected rows (rule schedules, row 8 at the floor, ZK row)
    b_e: float
    a: qrom.TreeQrom
    a_folded: qrom.TreeQrom
    b: qrom.TreeQrom


def certify() -> Certificate:
    """Every corrected row of the tree meets condition C; condition Q is checked with Theorem Q's constants
    and raises qrom.ConditionQFailure if it fails."""
    t = target()
    es = []
    for s in leaf_shapes(t) + node_shapes(t):
        if s.rule_margin < -1e-9:
            raise ValueError(f"{s.row.name} 2^{s.log_n} 1/{2 ** s.rate}: the rule schedule misses by {-s.rule_margin:.2f}")
        es.append(s.rule_weakest)
    for rate in (2, 1):
        w = wi_row("row 8", ROW8, rate, wi_solve(ROW8, rate, LIST_BITS), t=t)
        if not w.meets:
            raise ValueError(f"row 8 at 1/{2 ** rate} misses")
        es.append(w.weakest)
    z = wi_row("ZK", cu.ROW6, cu.A_LEAF_RATE, ZK_QUERIES, t=t)
    if not z.meets:
        raise ValueError("the zero-knowledge leaf at 226/157/154/154 misses")
    es.append(z.weakest)
    a_e = min(es)
    b = johnson.row("ud", b_need())
    b_e = min(b.query_bits, b.weakest.bits)
    return Certificate(a_e, b_e,
                       qrom.require(qrom.tree_qrom(qrom.FORMS["A"], a_e, 256, TREE_PROOFS), "system A, form X"),
                       qrom.require(qrom.tree_qrom(qrom.FORMS["A, a_V folded"], a_e, 256, TREE_PROOFS), "system A, form X, a_V"),
                       qrom.require(qrom.tree_qrom(qrom.FORMS["B"], b_e, 256, TREE_PROOFS), "system B, form C"))


# --- tables --------------------------------------------------------------------------------------------


def _l(xs) -> str:
    return ", ".join(str(x) for x in xs)


def tables(salt_bits: int = SALT_BITS) -> list[str]:
    if salt_bits not in salts.SALT_CHOICES:
        raise ValueError(f"salt length {salt_bits} not in {salts.SALT_CHOICES}")
    t = target()
    sb = salt_bits // 8
    out = [f"Revision 5. Tree bound {TREE_PROOFS:,} proofs, {cu.OTHER_ROUNDS} rounds outside each proof's listed rounds in k, "
           "no grinding, unique decoding, GF(2^256) challenges, 256-bit digests. Finding W-1: system A's plain query rounds "
           "at the true rate (2^mu + k)/2^(mu + r).", ""]
    # W-1 reproduction
    out += ["## W-1: rows 7 and 9 at the list's counts, nominal against true rate", "",
            "| Row | Stack, rate | Levels: mu | Level rates r | List counts | Need | Weakest, nominal | Weakest, true | Margin, true |",
            "|---|---|---|---|---|---|---|---|---|"]
    shapes = leaf_shapes(t) + node_shapes(t)
    for s in shapes:
        c = cu.a_config(s.row, s.log_n, s.rate, 0)
        nom = min(l.nominal_bits for l in levels(c))
        out.append(f"| {s.row.name.split(' (')[0]} | 2^{s.log_n}, 1/{2 ** s.rate} | {_l(s.mus)} | {_l(s.rates)} | {_l(s.list_q)} "
                   f"| {s.need:.3f} | {nom:.2f} | {s.list_weakest:.2f} | {'**' if s.list_margin < 0 else ''}{s.list_margin:+.2f}"
                   f"{'**' if s.list_margin < 0 else ''} |")
    # corrected schedules
    cpk_leaf, cpk_child = cycles_per_keccak("leaf"), cycles_per_keccak("node")
    out += ["", f"## Corrected schedules: the rule (every query round >= {LIST_BITS} bits at the true rate) and the minimal counts", "",
            "Deltas against the list's counts: opening bytes a proof; Keccak-f of verifying one such proof in its parent "
            "(full paths, upper figure); cycles (E) = Keccak-f x measured cycles per modelled Keccak-f "
            f"({cpk_leaf:.1f} for a leaf, {cpk_child:.1f} for a node child; recursion.md 9.10).", "",
            "| Row | Stack, rate | Rule counts | Margin | Bytes | Keccak-f | Cycles (E) | Minimal counts | Margin | Bytes | Keccak-f |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in shapes:
        cpk = cpk_leaf if s.row is ROW7 else cpk_child
        out.append(f"| {s.row.name.split(' (')[0]} | 2^{s.log_n}, 1/{2 ** s.rate} | {_l(s.rule_q)} | {s.rule_margin:+.2f} "
                   f"| {s.bytes_rule:+,.0f} | {s.keccak_rule:+,} | {s.keccak_rule * cpk:+,.0f} | {_l(s.min_q)} | {s.min_margin:+.2f} "
                   f"| {s.bytes_min:+,.0f} | {s.keccak_min:+,} |")
    adopted = [s for s in shapes if s.row is ROW9 and s.rate == NODE_RATE_ADOPTED]
    worst = max(adopted, key=lambda s: s.keccak_rule)
    out += ["", f"Node row 9 at rate 1/2, worst shape (2^{worst.log_n}): {worst.bytes_rule:+,.0f} B a node proof, "
            f"{worst.keccak_rule:+,} Keccak-f and {worst.keccak_rule * cpk_child:+,.0f} cycles (E) per child verified, "
            f"x 16 children = {16 * worst.keccak_rule:+,} Keccak-f, {16 * worst.keccak_rule * cpk_child:+,.0f} cycles (E) a full merge."]
    tab = rule_table()
    out += ["", "Rule counts by level rate r and mu (k = 3 folds; the list's count is the limit):", "",
            "| r | list | " + " | ".join(f"mu = {mu}" for mu in range(3, 12)) + " |",
            "|---|---|" + "---|" * 9]
    for r in (1, 2, 4, 5):
        out.append(f"| {r} | {TREE_LIST_153[r]} | " + " | ".join(str(tab[(r, mu)]) for mu in range(3, 12)) + " |")
    # W-I rows
    out += ["", f"## W-I rows (true rates of the hiding layout; salts {salt_bits} bits, the size includes them)", "",
            "| Row | Rate | Counts | Need | Weakest | Margin | Size KiB (E) | True rates |", "|---|---|---|---|---|---|---|---|"]
    wrows = []
    for rate in (2, 1):
        old = wi_row("row 8 at the list", ROW8, rate, [ROW8.queries[min(r, 10)] for r in ROW8.schedule(22, rate)[1]], sb, t=t)
        mn = wi_row("row 8 minimal", ROW8, rate, wi_solve(ROW8, rate), sb, t=t)
        fl = wi_row(f"row 8 at {LIST_BITS} bits", ROW8, rate, wi_solve(ROW8, rate, LIST_BITS), sb, t=t)
        wrows += [old, mn, fl]
    wrows.append(wi_row("zero-knowledge leaf (row 6 schedule)", cu.ROW6, 2, ZK_QUERIES, sb, t=t))
    for w in wrows:
        out.append(f"| {w.label} | 1/{2 ** w.rate} | {_l(w.queries)} | {w.need:.3f} | {w.weakest:.2f} | "
                   f"{'**' if not w.meets else ''}{w.margin:+.2f}{'**' if not w.meets else ''} | {w.size / 1024:,.0f} | "
                   + ", ".join(f"2^{math.log2(x):.2f}" for x in w.true_rates) + " |")
    # QROM
    cert = certify()
    out += ["", f"## QROM bits of the tree (Theorem Q, N = {TREE_PROOFS:,}, lambda = 256; condition Q: >= 64, hard failure)", "",
            "| System, form | C1 | C2 | e (bits) | IOP term | Hash term | QROM bits | Margin over 64 |", "|---|---|---|---|---|---|---|---|"]
    rows_q = [("A, form X (weakest corrected round)", cert.a), ("A, form X, a_V folded in", cert.a_folded),
              ("B, form C (weakest round, 184 queries)", cert.b)]
    for e_doc, form, lab in ((152.343, qrom.FORMS["A"], "A, form X, at e = 152.343 (qrom-compilation.md 6)"),
                             (152.343, qrom.FORMS["B"], "B, form C, at e = 152.343 (qrom-compilation.md 6)")):
        rows_q.append((lab, qrom.require(qrom.tree_qrom(form, e_doc, 256, TREE_PROOFS))))
    for lab, q in rows_q:
        out.append(f"| {lab} | {q.form.c1:g} | {q.form.c2:g} | {q.e:.2f} | {q.iop:.2f} | {q.hash:.2f} | {q.bits:.2f} | {q.margin:+.2f} |")
    out += ["", "Conditional on the CMS-form transcripts (qrom-compilation.md 4: form X for A, form C for B); the transcripts as "
            "built are outside Theorem 8.6 and Theorem Q (C-7). With 192-bit digests form C would fail condition Q "
            f"(hash term {qrom.tree_qrom(qrom.FORMS['B'], cert.b_e, 192, TREE_PROOFS).hash:.2f}): the calculator refuses such a row."]
    # salts
    out += ["", "## Salt length (Theorem ZQ with Lemma H; N_u = 2^24 unopened salted leaves a proof, n_b <= 2^12)", "",
            "| Salt (bits) | Per leaf | Per proof | Per tree (2^14 leaf proofs) | Over all 20,000 proofs | Bytes an opened leaf (added) "
            "| Row 8 at 1/4: opened leaves, bytes added a proof | B leaf (2 x 184 opened): bytes added | A leaf Keccak-f (level 0 / later) | B leaf SHA-256 blocks (mixed / all-256) |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    r8 = wi_solve(ROW8, 2, LIST_BITS)
    for s in salts.SALT_CHOICES:
        sr = salts.salt_row(s)
        fmt = lambda x: "1 (vacuous)" if x >= 0 else f"2^{x:.0f}"
        out.append(f"| {s}{' (lead)' if s == salts.LEAD_CHOICE else ''}{' (selected)' if s == salt_bits else ''}{' (built)' if s == salts.BUILT_SALT_BITS else ''} "
                   f"| {fmt(sr.per_leaf_log2)} | {fmt(sr.per_proof_log2)} | {fmt(sr.per_tree_log2)} | {fmt(sr.per_tree_all_log2)} "
                   f"| {sr.bytes_per_opened_leaf} ({sr.added_bytes_per_opened_leaf:+}) | {sum(r8)}, {salts.proof_bytes_added(s, sum(r8)):+,} "
                   f"| {salts.proof_bytes_added(s, 2 * 184):+,} | {salts.keccak_perms(512, s)} / {salts.keccak_perms(256, s)} "
                   f"| {salts.sha256_blocks(32, s)} / {salts.sha256_blocks(64, s)} |")
    out += ["", "Form C (system B) adds k^2 / 2^257 (k chain links, below 2^-237 at k <= 600) and zeta_IOP < 2^-240 a proof: "
            "neither changes a figure above. Per-tree figures are a union over the proofs."]
    # B
    bn = b_need()
    out += ["", f"## System B rows (rate 1/8, |K| = 2^256, need {bn:.2f} bits a round at the 600-challenge budget, Theorem Q's C1 = 24)", "",
            "| Row | Status | Queries | Query bits | Weakest algebraic term | Bits | Meets |", "|---|---|---|---|---|---|---|"]
    for r in b_rows(bn):
        out.append(f"| {r.label} | **{r.status}** | {r.queries} | {r.query_bits:.2f} | {r.weakest.name} | {r.weakest.bits:.2f} | "
                   f"{'yes' if r.meets else 'no'} |")
    n3 = binius64.tree_need(CAT3, [(TREE_PROOFS, cu.B_ROW_BUDGET)], B_FS)
    u3, d3 = johnson.row("ud", n3), johnson.row("dkt", n3, 3)
    out += ["", f"Category 3 ({n3:.2f} bits): unique decoding {u3.queries} queries (weakest {u3.weakest.bits:.2f}, "
            f"{'meets' if u3.meets else 'fails'}); Johnson DKT26 m = 3 {d3.queries} queries, weakest {d3.weakest.bits:.2f}: "
            f"{'meets' if d3.meets else 'refused'}. Candidate rows are never reported as certified."]
    return out
