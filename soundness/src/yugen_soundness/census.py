"""Round census of system A (finding M-3 of docs/theorem-s-referee.md; docs/round-census-a.md).

The calculator charges the rounds of an A proof outside its opening as one estimated count, `shipping.OTHER_ROUNDS =
512`, with no per-round error. This module replaces the estimate by a census, WITHOUT changing any certified count:

* `leaf_messages` walks the verifier of `yugen-proof-a` (HEAD 15b9993, `vendor/leanMultisig/crates/verifier/src`,
  read, not run) message by message for a leaf proof: every challenge it draws, in order, what it is for, the field
  it is drawn from (always the row's challenge field E, GF(2^256) for rows 6 to 9) and the numerator of the
  round-by-round error of the message it closes (error = numerator / |E|). Under the spBCS transcript a verifier
  message is a maximal run of challenges with no prover item between them (`verifier::spbcs::SpBcs::challenge` opens
  one stream a message), so consecutive draws are one message and their errors add (union bound inside the message).
* the walk's message count is checked against the counts the built verifier reports (`census/a-round-census.json`,
  from yugen-proof-a `bench/results/kq-report-20261119.txt`): 445 for the masked row-8 leaf, 411 for the plain row-7
  leaf, both reproduced exactly from one set of program parameters.
* `rows` prints, beside the calculator's estimate, each A row's need with the census count in place of 87 + 512.

Provenance. The per-round errors are cited per message in `leaf_messages` (sources in docs/round-census-a.md). The
census itself (the walk, the merge rule and the reconciliation with the measured counts) is Original (the Ycash
developers, 2026), REFERENCES.md O-85. Nothing here is used by a certified row: `shipping.OTHER_ROUNDS` is unchanged.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from . import category as C
from . import revision5 as r5
from . import whir, wi
from .shipping import OTHER_ROUNDS

DATA = Path(__file__).resolve().parents[2] / "census" / "a-round-census.json"

# verifier constants (yugen-proof-a verifier/src): BUS_BITS (layout.rs), N_TREES (bus.rs), PACK_BITS, LANE_BITS,
# LOCAL_BITS, PRODUCT_BITS (keccak.rs), ROUNDS (hash.rs), STATE_LANES, RING_MAP_WIDTH (ring_switch.rs),
# MAX_STACKED_CLAIMS (lib.rs), TABLE_TERMINAL_DEGREE, KECCAK_TERMINAL_DEGREE (zk.rs)
BUS_BITS, N_TREES, PACK_BITS, LANE_BITS, LOCAL_BITS, PRODUCT_BITS = 4, 3, 4, 5, 11, 47
KECCAK_ROUNDS, STATE_LANES, RING_MAP_WIDTH, MAX_STACKED_CLAIMS = 24, 25, 8, 512


def load() -> dict:
    return json.loads(DATA.read_text())


@dataclass
class Message:
    """One verifier message: the challenges it draws (purpose, count), the error numerator over |E| (sum over its
    challenges), the group it belongs to, whether a challenge of it was added by the zero-knowledge construction, and
    the source of each term."""

    group: str
    draws: list[tuple[str, int]] = field(default_factory=list)
    numerator: float = 0.0
    zk: bool = False
    sources: list[str] = field(default_factory=list)
    bits: float | None = None  # set for opening rounds, whose error is not a numerator over |E| (query rounds)

    def error_bits(self, field_bits: int) -> float:
        if self.bits is not None:
            return self.bits
        return math.inf if self.numerator == 0 else field_bits - math.log2(self.numerator)


class _Walk:
    """Event stream of a verifier walk: `item()` for a prover item (closes the open message), `draw(..)` for a
    challenge (opens a message or joins the open one)."""

    def __init__(self) -> None:
        self.messages: list[Message] = []
        self.open = False

    def item(self) -> None:
        self.open = False

    def draw(self, group: str, purpose: str, count: int, numerator: float, source: str, zk: bool = False,
             bits: float | None = None) -> None:
        if not self.open:
            self.messages.append(Message(group))
            self.open = True
        m = self.messages[-1]
        m.draws.append((purpose, count))
        m.numerator += numerator
        m.zk = m.zk or zk
        m.sources.append(source)
        if bits is not None:
            m.bits = bits if m.bits is None else min(m.bits, bits)
        if m.group != group:
            m.group = f"{m.group}+{group}"


SZ = "Schwartz-Zippel (one line, docs/round-census-a.md 2)"
SC = "sumcheck round: XZZPS19 (ePrint 2019/317) Section 2.3.1, p. 8, eps = d l / |F|, per round d / |F| (Adapted)"


def leaf_messages(prog: dict, masked: bool, opening: list, plain_whir: whir.WhirConfig | None = None,
                  stack_log: int = 22) -> list[Message]:
    """The verifier messages of one leaf proof, in order (lib.rs `walk`). `opening` is the W-I round list
    (`wi.rounds(c, "A")`, no zero-knowledge rounds) when `masked`; for the plain leaf pass `plain_whir`."""
    w = _Walk()
    d, t_rounds = prog["bus_depth"], prog["table_rounds"]
    ls, kd = prog["keccak_log_steps"], prog["keccak_depth"]
    segments = KECCAK_ROUNDS // kd
    seg_bits = math.ceil(math.log2(segments)) if segments > 1 else 0
    pack_bits = ls - PACK_BITS
    slot_bits = math.ceil(math.log2(STATE_LANES * segments))
    # 1] announced sizes; 2] the root of oracle 0, then its out-of-domain point (read_ood): error 0 in unique decoding
    w.item()
    w.item()
    w.draw("ood", "z (OOD point, stack variables)", stack_log, 0,
           "OOD: unique decoding, one decoding, no list: error 0 (ACFY24 Lemma 4.24's term with list size 1; 2.2)")
    w.item()  # the OOD value
    # 3] bus: the fingerprint (weights, beta), then the batched GKR (bus.rs verify_bus_balance)
    w.draw("bus-fingerprint", "weights (tuple slots) and beta", (1 << BUS_BITS) + 1, 2 ** d,
           "grand-product fingerprint: degree 2^mu in (weights, beta), " + SZ)
    w.item(); w.item()  # the shared root and the count root
    steps = [1] * (d % 2) + [2] * (d // 2)
    point = 0
    for k, step in enumerate(steps):
        w.draw("bus-gkr", f"combiner (layer {k})", 1, N_TREES - 1, "GKR claim batching, powers of one challenge, degree N_TREES - 1: " + SZ + " (Adapted from XZZPS19 p. 10)")
        if masked:
            w.draw("bus-gkr", f"rho (layer {k}, A24)", 1, 1, "Lemma 6, zk-wi-soundness.md (1/q)", zk=True)
        w.item()  # Gtilde (masked) or nothing; the first round polynomial follows
        for _ in range(point):
            w.item()
            w.draw("bus-gkr", f"sumcheck round (layer {k})", 1, (1 << step) + 1,
                   "GKR layer round, eq times 2^step lines: " + SC)
        if masked:
            w.item()
            w.draw("bus-gkr", f"r_w dummy (layer {k}, A24)", 1, 4, "zk-system-a-gaps.md 11 (form A5-T, 4/q)", zk=True)
        w.item()  # the children of the three trees
        last = k == len(steps) - 1
        w.draw("bus-gkr", f"y (layer {k})", step, step * (2 if last else 1),
               "line to a point: the children's multilinear in `step` variables, " + SZ
               + ("; the last y is also zeta's first coordinates (bus.rs: degree doubled)" if last else ""))
        point += step
    # framework values, then the bytecode share's sumcheck (BUS_BITS rounds, degree 2)
    w.item()
    for _ in range(BUS_BITS):
        w.item()
        w.draw("bytecode", "bytecode-share sumcheck round", 1, 2, SC)
    w.item()  # the bytecode value
    # 4] table sumcheck: xi (n_constraints + N_TREES powers), masked head rho, rounds of degree 3, dummy round
    w.draw("table", "xi (constraint and tree powers)", 1, prog["n_constraints"] + N_TREES - 1,
           "batching n_powers claims with powers of xi: " + SZ)
    if masked:
        w.draw("table", "rho (S4, A4)", 1, 1, "Lemma 6 (1/q)", zk=True)
        w.item()  # Gtilde
    for _ in range(t_rounds):
        w.item()
        w.draw("table", "table sumcheck round", 1, 4, SC + " (degree 3, plus 1: the challenge is also a KECCAK point "
               "coordinate, bus.rs)")
    if masked:
        w.item()
        w.draw("table", "r_y dummy (S4, A21)", 1, 2, "zk-system-a-gaps.md 3.5 (2/q)", zk=True)
    w.item()  # the column evaluations
    # 5] the public input: one line in the challenge
    w.draw("public", "public-input challenge", 1, 1, "a line in one variable: " + SZ)
    # 6] Keccak reduction (keccak.rs verify_keccak): segment and lane point, then the layers, then the two openings
    w.draw("keccak", "segment and lane point", seg_bits + LANE_BITS, seg_bits + LANE_BITS,
           "the first claim is multilinear in segment and lane bits: " + SZ)
    if segments > 1:
        w.item()  # committed
    for layer in range(kd):
        if masked:
            w.draw("keccak", f"rho (layer {layer}, A23)", 1, 1, "Lemma 6; zk-wi-soundness.md 6.3 (1/q)", zk=True)
            w.item()  # Gtilde
        w.item()  # the product polynomial
        w.draw("keccak", f"s (product polynomial, layer {layer})", 1, PRODUCT_BITS - 1,
               "a univariate of degree PRODUCT_BITS - 1 = 46 at a random point: " + SZ)
        for _ in range(pack_bits + seg_bits):
            w.item()
            w.draw("keccak", f"pack/segment round (layer {layer})", 1, 3, SC + " (eq times degree 2)")
        for _ in range(LOCAL_BITS):
            w.item()
            w.draw("keccak", f"bit-position round (layer {layer})", 1, 3, SC + " (degree 3)")
        if masked:
            w.item()
            w.draw("keccak", f"r_y dummy (layer {layer}, A23)", 1, 2, "zk-system-a-gaps.md 11 (2/q)", zk=True)
        w.item()  # t[0..3]
        w.draw("keccak", f"beta (layer {layer})", 1, 2, "three claims combined, quadratic in beta: " + SZ)
    if segments > 1:  # the committed outputs' opening
        if masked:
            w.draw("keccak", "rho (output opening, A4 on S9)", 1, 1, "Lemma 6 (1/q)", zk=True)
            w.item()
        for _ in range(slot_bits):
            w.item()
            w.draw("keccak", "output-opening round", 1, 2, SC + " (degree 2)")
        w.item()  # the word
    if masked:
        w.draw("keccak", "rho (input opening, A4 on S9)", 1, 1, "Lemma 6 (1/q)", zk=True)
        w.item()
    for _ in range(PACK_BITS + slot_bits):
        w.item()
        w.draw("keccak", "input-opening round", 1, 2, SC + " (degree 2)")
    if masked:
        w.item()
        w.draw("keccak", "r_y dummy (slices, A20)", 1, 1, "zk-system-a-gaps.md 2.4 (degree 1)", zk=True)
    w.item()  # the 64 slices
    # the linear-claim gadget (zk.rs verify_gadget)
    if masked:
        w.draw("gadget", "theta (batching the mask claims)", 1, prog["gadget_claims"] - 1,
               "zk-wi-soundness.md 6.3 ((m - 1)/q)", zk=True)
        w.item()  # beta
        w.draw("gadget", "c", 1, 1, "zk-wi-soundness.md 6.3 (1/q)", zk=True)
        w.item()  # u
        w.draw("gadget", "z", prog["gadget_log_len"], prog["gadget_log_len"], "zk-wi-soundness.md 6.3 (l/q)", zk=True)
        w.item()  # A(z), B(z)
    # 7] ring switch (16 map challenges) and, in the same message, the stacked opening's lambda
    w.draw("ring-batch", "ring-switch map (f_p, g_b)", 2 * RING_MAP_WIDTH, 2,
           "ring switch: two nonzero linear forms, Original (docs/round-census-a.md 2.6)")
    w.draw("ring-batch", "stacked lambda", 1, MAX_STACKED_CLAIMS - 1,
           "batching at most MAX_STACKED_CLAIMS = 512 claims with powers of lambda: " + SZ)
    # 8] the opening
    if masked:
        for r in opening:  # each W-I round is preceded by a prover item (G, the round table, a root, mu, P*, ...)
            w.item()
            w.draw("opening", r.name, 2 if r.name.startswith("fold") else 1, 0,
                   "Theorem S (zk-wi-soundness.md 5.1)", bits=r.effective_bits)
    else:
        c = plain_whir
        ws = {r.name: r.effective_bits for r in whir.rounds(c)}
        levels = len(c.folds)
        for i, k in enumerate(c.folds):
            for j in range(k):
                w.item()
                w.draw("opening", f"fold{i}.{j}", 2, 0, "WHIR fold (calculator whir.rounds)", bits=ws[f"fold{i}.{j}"])
            w.item()
            if i < levels - 1:
                w.draw("opening", f"ood{i}", c.vars_at(i + 1), 0, "OOD, unique decoding: error 0")
                w.item()
                w.draw("opening", f"query{i} and lambda", 1, 0, "WHIR query round (calculator)", bits=ws[f"query{i}"])
            else:
                w.draw("opening", "final queries", 1, 0, "WHIR final round (calculator)", bits=ws["final"])
                for _ in range(c.vars_at(i) - k):
                    w.item()
                    w.draw("opening", "tail round", 1, 2, SC + " (degree 2)")
    return w.messages


def plain_whir_messages(c: whir.WhirConfig) -> int:
    """A plain WHIR opening's verifier messages (whir.rs verify_whir): the fold rounds, per non-final level its OOD
    point and its queries with lambda, the final queries and the tail sumcheck. The calculator's `whir.rounds` lists the
    folds and queries only (no OOD, no tail)."""
    last = len(c.folds) - 1
    return sum(c.folds) + 2 * last + 1 + (c.vars_at(last) - c.folds[last])


# --- the census against the estimate -----------------------------------------------------------------------------


def wallet_leaf(masked: bool = True, p: C.Profile | None = None) -> list[Message]:
    """The census of the mode-0 wallet leaf at 2^22, rate 1/4: row 8 (masked) or row 7 (plain)."""
    p = p or C.PROFILES[1]
    prog = load()["programs"]["wallet-mode0"]
    if masked:
        row = next(r for r in C.a_rows(p) if r.label.startswith("row 8") and r.stack == 22 and r.rate == 2)
        return leaf_messages(prog, True, wi.rounds(row.extra["config"], "A"))
    row = C.a_plain_leaf(22, 2, p)
    return leaf_messages(prog, False, [], row.extra["config"])


def summary(ms: list[Message], field_bits: int = 256) -> dict:
    groups: dict[str, int] = {}
    for m in ms:
        groups[m.group] = groups.get(m.group, 0) + 1
    outside = [m for m in ms if m.group != "opening"]
    worst = min(outside, key=lambda m: m.error_bits(field_bits))
    return {"messages": len(ms), "outside_opening": len(outside), "opening": len(ms) - len(outside),
            "challenges": sum(n for m in ms for _, n in m.draws),
            "challenges_outside": sum(n for m in outside for _, n in m.draws), "groups": groups,
            "worst_outside": (worst.group, worst.draws[0][0], worst.error_bits(field_bits)),
            "sum_outside_log2": math.log2(sum(m.numerator for m in outside)) - field_bits}


def _measured(row: str, mode: int, stack: int, rate: int) -> dict | None:
    for m in load()["measured"]:
        if m["row"] == row and m["mode"] == mode and m["stack"] == stack and m["rate"] == rate:
            return m
    return None


def census_messages(r: C.Row) -> tuple[int, str]:
    """The census message count of a row's shape and its provenance: measured (M), derived from a measured program
    (D: the program's walk outside the opening plus the opening's own messages at this shape) or not measured (None:
    row 9 at a stack with no proof measured; E below 2^27, R above it, where the build refuses the shape)."""
    label, stack, rate = r.label.split(", mode")[0], r.stack, r.rate
    mode = int(r.label.split("mode ")[1][0]) if "mode" in r.label else 0
    c = r.extra["config"]
    m = _measured(label, mode, stack, rate)
    if label.startswith("row 9"):
        if m is not None:
            return m["j_v"], "M"
        outside = {s: _measured("row 9 (node)", 0, s, 1)["j_v"] - plain_whir_messages(C._a_cfg(r5.ROW9, s, 1, 0,
                                                                                               C.PROFILES[1]))
                   for s in (25, 27)}
        if stack in outside:  # the same node program at another rate: its walk outside the opening is the measured one
            return outside[stack] + plain_whir_messages(c), "D"
        # No count otherwise (referee M-A2, 2026-11-19): the two measured nodes are different programs, so the
        # former linear extrapolation in the stack's log bounds nothing. Above 2^27 the build refuses the shape.
        return None, ("R" if stack > 27 else "E")
    if label.startswith("row 7"):
        n = len(leaf_messages(load()["programs"]["wallet-mode0"], False, [], c, stack))
        return n, ("M" if m is not None and m["j_v"] == n else "D")
    opening = len(wi.rounds(c, "A"))
    if mode == 0:
        prog = load()["programs"]["wallet-mode0"]
        n = len(leaf_messages(prog, True, wi.rounds(c, "A"), stack_log=stack))
        return n, ("M" if m is not None and m["j_v"] == n else "D")
    # mode 1: the walk outside the opening is the measured count less the measured shape's opening
    ref = _measured("row 8 (masked in a tree)", 1, 21, 2)
    ref_c = C._a_cfg(r5.ROW8, 21, 2, C.PROFILES[1].leaf_salt_bytes, C.PROFILES[1], ref["queries"])
    outside = ref["j_v"] - len(wi.rounds(ref_c, "A"))
    n = outside + opening
    return n, ("M" if m is not None and m["j_v"] == n else "D")


@dataclass
class CensusRow:
    row: C.Row
    est_messages: int
    messages: int | None
    provenance: str
    kq_est: int
    kq: int | None
    need_est: float
    need: float | None
    book_need_est: float
    book_need: float | None

    @property
    def margin_est(self) -> float:
        return self.row.weakest - self.need_est

    @property
    def margin(self) -> float | None:
        return None if self.need is None else self.row.weakest - self.need

    @property
    def tolerance(self) -> int:
        """Messages the row's census may exceed the estimate by before the every-t need passes its weakest round."""
        slack = (1 + self.kq_est) * (2 ** self.margin_est - 1)
        return int(slack // 4)  # k_q = 2 N_msg + ..., N_msg = 2 x messages (J_V + J_P)


def census_row(r: C.Row, cat: int = 1) -> CensusRow:
    est = r.rounds + OTHER_ROUNDS
    n, prov = census_messages(r)
    kq_est = C.a_row_kq(r.extra["config"], r.rounds)
    if n is None:  # not measured: no census count, no need (M-A2)
        return CensusRow(r, est, None, prov, kq_est, None, C.every_t_need(cat, kq_est), None,
                         C.round_need(cat, est), None)
    kq = kq_est + 4 * (n - est)  # k_q = 2 N_msg + n_B + q_IOP (..), N_msg = 2 x messages
    return CensusRow(r, est, n, prov, kq_est, kq, C.every_t_need(cat, kq_est), C.every_t_need(cat, kq),
                     C.round_need(cat, est), C.round_need(cat, n))


def rows(p: C.Profile | None = None) -> list[CensusRow]:
    p = p or C.PROFILES[1]
    out = [census_row(r, p.category) for r in C.a_rows(p)]
    out.append(census_row(C.a_plain_leaf(22, 2, p), p.category))
    return out


def restore(cr: CensusRow, p: C.Profile | None = None) -> tuple[int, ...] | None:
    """For a row that misses with the census: the fewest added queries (one at a time on the weakest query round)
    that restore it at the census k_q (each added query raises k_q too). None if it meets already."""
    if cr.margin is None or cr.margin >= 0:
        return None
    p = p or C.PROFILES[1]
    r = cr.row
    c = r.extra["config"]
    q = list(r.queries)
    for _ in range(16):
        rs = whir.rounds(c) if r.kind == "node" or r.label.startswith("row 7") else wi.rounds(c, "A", wi.A_WALLET_ZK)
        weak = min((x for x in rs if x.name.startswith("query") or x.name == "final"), key=lambda x: x.effective_bits)
        i = len(q) - 1 if weak.name == "final" else int(weak.name[5:])
        q[i] += 1
        c = C._a_cfg(r5.ROW9 if r.kind == "node" else (r5.ROW7 if r.label.startswith("row 7") else r5.ROW8),
                     r.stack, r.rate, 0 if r.kind == "node" else p.leaf_salt_bytes, p, q)
        rs = whir.rounds(c) if r.kind == "node" or r.label.startswith("row 7") else wi.rounds(c, "A", wi.A_WALLET_ZK)
        kq = C.a_row_kq(c, r.rounds) + 4 * (cr.messages - cr.est_messages)
        if min(x.effective_bits for x in rs) >= C.every_t_need(p.category, kq):
            return tuple(q)
    return None


def tables(p: C.Profile | None = None) -> list[str]:
    s = summary(wallet_leaf(True))
    out = ["## Round census of system A beside the estimate (finding M-3; docs/round-census-a.md)", "",
           f"Row 8, mode 0, 2^22, rate 1/4 (the walk of the built verifier): {s['messages']} verifier messages "
           f"({s['opening']} in the opening, {s['outside_opening']} outside it), {s['challenges']} challenges drawn; "
           f"the calculator's estimate is 87 listed + OTHER_ROUNDS {OTHER_ROUNDS} = {87 + OTHER_ROUNDS}. Weakest message "
           f"outside the opening: {s['worst_outside'][0]} ({s['worst_outside'][1]}), {s['worst_outside'][2]:.2f} bits; all "
           f"of them together 2^{s['sum_outside_log2']:.2f}.", "",
           "Census provenance: M measured (the built verifier's j_v at this shape), D derived (the measured walk outside "
           "the opening plus this shape's opening). Row 9 at an unmeasured stack has no census count (referee M-A2: the "
           "two measured nodes are different programs, so no extrapolation holds): 'not measured' below 2^27, 'not "
           "measured — refused by the build above 2^27' above it. Needs under the default convention (every t, at the row's k_q); the "
           "book need (t >= k_q, non-default) beside it. Certified counts and statuses are unchanged.", "",
           "| Row | Stack | Rate | Counts | Messages: estimate / census | k_q: estimate / census | Need: estimate / census "
           "| Weakest | Margin: estimate / census | Tolerance (messages over the estimate) | Book need: estimate / census |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for cr in rows(p):
        r = cr.row
        if cr.messages is None:
            what = "not measured — refused by the build above 2^27" if cr.provenance == "R" else "not measured"
            out.append(f"| {r.label} | 2^{r.stack} | 1/{2 ** r.rate} | {', '.join(map(str, r.queries))} | "
                       f"{cr.est_messages} / {what} | {cr.kq_est:,} / - | {cr.need_est:.4f} / - | {r.weakest:.4f} | "
                       f"{cr.margin_est:+.4f} / - | {cr.tolerance:+,} | {cr.book_need_est:.2f} / - |")
            continue
        out.append(f"| {r.label} | 2^{r.stack} | 1/{2 ** r.rate} | {', '.join(map(str, r.queries))} | {cr.est_messages} / "
                   f"{cr.messages} ({cr.provenance}) | {cr.kq_est:,} / {cr.kq:,} | {cr.need_est:.4f} / {cr.need:.4f} | "
                   f"{r.weakest:.4f} | {cr.margin_est:+.4f} / {cr.margin:+.4f}{'' if cr.margin >= 0 else ' MISSES'} | "
                   f"{cr.tolerance:+,} | {cr.book_need_est:.2f} / {cr.book_need:.2f} |")
        fix = restore(cr, p)
        if fix is not None:
            out.append(f"| | | | restored at {', '.join(map(str, fix))} | | | | | | | |")
    return out
