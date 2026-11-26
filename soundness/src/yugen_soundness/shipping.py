"""RECORD ONLY (revision 6, 2026-11-19). This module is the record of design-basis.md Appendix A.2; it certifies nothing. Its system A query terms use the
NOMINAL rate 2^-r of each level, not the true rate (2^mu + k)/2^(mu + r) that finding W-1 requires
(docs/whir-additive-soundness.md section 6), and its QROM figures use CMS19's constants for CMS19's own
construction, which covers neither transcript as built. The certified rows are revision5.py (condition C,
true rates) with revision6.py (condition Q under Sharp-Grubbs Theorem 6.6 (2) for the spBCS transcript).

Shipping rows: category 1 (and 3) for a whole proof tree of up to 2^14 leaves, no grinding.

SUPERSEDED (revision 3, 2026-11-19) by current.py: the tree of specification 0.3 (16-leaf
sub-bundles, three merge levels), system B on Binius64 (binius64.py). Kept as the record of
design-basis.md Appendix A.2; its system B rows are Plonky3's and obsolete.

The lead architect's design basis of 2026-11-19 (second revision):

  1. the whole bundle tree meets the target for a tree of sub-bundles of at most 64 leaves and two
     merge levels of arity at most 16: 2^14 leaves, 2^8 sub-bundles, 2^4 first merges, one root,
     16,657 proofs (`TREE_PROOFS`); union bound over those proofs for one attempt;
  2. no grinding anywhere (every grind 0);
  3. proven bounds only: unique-decoding proximity (Regime.UDR), the book's BCS bound, CMS19;
  4. 256-bit digests (384 for cat3, the attack rule of condition H);
  5. system A's leaf opens with W-I (wi.rounds, "A"), system B's with W-M (wi.full_mask_rounds);
  6. every proof at most 1.75 MiB.

Every proof is counted with all its rounds: `OTHER_ROUNDS` stands for the rounds outside the
polynomial commitment opening (zerocheck / table sumcheck, the bus GKR, the Keccak reduction, ring
switch, batching), which the book's (t + k) eps_rbr bound counts in k like any other round. The
calculator before this module counted the opening's rounds only.

Everything this module returns is an ESTIMATE (E) except the constants marked MEASURED (M), which
are read from the raw files named beside them. Calibration constants and their fit errors are
returned by `calibration()`.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field

from . import design, whir, wi
from .bounds import Regime
from .compose import FsParams, Round, evaluate
from .params import leanvm_schedule
from .targets import CAT1, CAT3, SecurityTarget

# --- the tree ------------------------------------------------------------------------------------

LEAVES_PER_SUB = 64
MERGE_ARITY = 16
TREE_LEAVES = LEAVES_PER_SUB * MERGE_ARITY * MERGE_ARITY  # 2^14
TREE_PROOFS = TREE_LEAVES + MERGE_ARITY * MERGE_ARITY + MERGE_ARITY + 1  # 16,657 = 2^14.02
LAYERS = ["leaf", "sub-bundle", "merge1", "merge2"]
CHILDREN = {"sub-bundle": LEAVES_PER_SUB, "merge1": MERGE_ARITY, "merge2": MERGE_ARITY}

# Rounds of a proof outside its PCS opening(s), counted in k (E, an upper figure): leanVM's bus GKR
# over product trees of depth about 22 is about 253 sumcheck rounds, plus the table sumcheck (22),
# the Keccak reduction, ring switch and batching; B's zerocheck plus its bus GKR is of the same order.
OTHER_ROUNDS = 512

PROOF_LIMIT_BYTES = int(1.75 * 2**20)

# --- built statements (M) ----------------------------------------------------------------------------

# A: the mode-0 wallet statement, 3,463,392 committed GF(2^64) words, a 2^22 stack
#    (yugen-proof-a/docs/measurements.md, bench/results/wallet-20261118.txt).
A_LEAF_VARS = 22
# B: 10,889,102 committed bits = 2^23.38 bits = 2^17.38 GF(2^64) words, a 2^18 stack with 64-bit
#    values (task F-2); the preprocessed schedule, 2,048 x 65 + 8,192 x 7 = 190,464 elements, a
#    second 2^18 commitment (yugen-proof-b/docs/statement-layout.md sections 1 and 5).
B_LEAF_VARS = 18
B_PRE_VARS = 18

# --- measured anchors (M) ------------------------------------------------------------------------------

# A, wallet statement, codeword dropped, 128-bit challenges (yugen-proof-a/bench/results/fork-20261119.txt,
# docs/parameters.md): (row, log inverse rate, salt bytes, proof bytes)
A_ANCHORS = [(1, 2, 0, 347_704), (1, 1, 0, 388_652), (3, 2, 32, 367_480), (0, 2, 0, 173_276), (0, 1, 0, 247_420)]
# A, bundle nodes at row 4 (row 1's queries, residual 2^5), 128-bit (yugen-proof-a/docs/recursion.md section 6):
# (label, log inverse rate, cycles, proof bytes)
A_NODE_ANCHORS = [("bundle of 1, rate 1/2", 1, 329_440, 539_164), ("bundle of 8, rate 1/4", 2, 2_239_683, 640_664),
                  ("merge of two bundles of 4, rate 1/4", 2, 676_373, 541_080)]
# A: in-circuit Keccak-f per verified leaf (row, log inverse rate, Keccak-f, cycles), same section.
A_VERIFY_ANCHORS = [(0, 1, 5_932, 205_118), (0, 2, 3_996, 150_000), (4, 1, 12_980, 320_000), (4, 2, 11_400, 280_000)]
A_WORDS_PER_CYCLE = 30.5  # committed words per node cycle, row-0 bundles of 1 to 8 and the merge: 30.1 to 31.6 (M)
A_NODE_FIXED_CYCLES = 9_800  # (M)
# The 256-bit challenge field multiplies a verification's cycles by about 1.8 (E, yugen-proof-a recursion.md 5).
A_E2_CYCLE_FACTOR = 1.8

# B, the wallet leaf, 128-bit, harness level 100, unique decoding, no grind (yugen-proof-b bench/results):
B_FOLD_ANCHORS = [(2, 793_916), (1, 991_023)]  # folding PCS, fold 3 (wallet-20261119-0005.txt)
B_WHIR_ANCHORS = [(2, 853_779), (1, 942_419), (3, 841_715)]  # WHIR, three openings (docs/recursion.md 4.2)
B_NODE_ANCHORS = [1_235_695, 1_191_423]  # one-leaf bundle / layer proof, rate 1/2, level 100 (bundle-20261119.txt, recursion.md 4.3)
B_VERIFY_FIXED = 2_500  # Keccak-f per verified proof outside the query paths (M, recursion.md 4.2)
B_VERIFY_ANCHOR = 19_634  # Keccak-f per verified leaf, V-1 + rate 1/4, binary trees (M)
B_WITNESS_FIXED = 680_000  # witnesses per verified proof outside the queries (M)
B_WITNESS_PER_QUERY = 2_300  # (M, rate 1/2, binary trees)
B_DENSE_PER_WITNESS = 8_716_320 / 1_110_696  # dense GF(2^128) cells per witness (M, bundle-20261119.txt)
B_BITS_PER_KECCAK = 2**17 * 1625 / 5461  # packed Keccak table bits per permutation (M)
B_E2_WITNESS_FACTOR = 1.8  # 256-bit challenge arithmetic in the circuit (E, A's factor reused)

# Prover's challenge-field factor at 256 bits against the 128-bit path (design.FIELD_FACTOR; E).
FIELD_FACTOR_256 = {"A": 3.0, "B": 6.7}
# The measured leaf codewords the relative prover cost is taken against: A 2^22 words of 8 bytes,
# B 2^24 bits, both at rate 1/4 (M runs above).
MEASURED_LEAF_CODEWORD = {"A": 2**22 * 8 * 4, "B": 2**24 / 8 * 4}

FS = {b: FsParams(digest_bits=b) for b in (256, 264, 384, 392)}


# --- the target ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class ProofTreeTarget(wi.TreeTarget):
    """wi.TreeTarget whose k also counts the proof's rounds outside the opening being solved."""

    other_rounds: int = 0

    def _cq(self, rounds_count: int, fs: FsParams) -> tuple[float, float]:
        return super()._cq(rounds_count + self.other_rounds, fs)


def tree_target(base: SecurityTarget, other_rounds: int = OTHER_ROUNDS, proofs: int = TREE_PROOFS) -> ProofTreeTarget:
    return ProofTreeTarget(name=f"{base.name}-tree", nist_category=base.nist_category,
                           classical_chain=base.classical_chain, quantum_chain=base.quantum_chain,
                           attack_bits=base.attack_bits, digest_attack=base.digest_attack,
                           digest_proven=base.digest_proven, layers=base.layers, proofs=proofs,
                           attempts=1.0, model="union", other_rounds=other_rounds)


def proven_hash_cap(digest_bits: int) -> float:
    """Proven classical bits the book's hash term 3.5 t^2 / 2^lambda allows (counted once for the
    whole tree: a collision anywhere among the adversary's t queries)."""
    return (digest_bits - 1.0 - math.log2(3.5)) / 2.0


# --- calibration -----------------------------------------------------------------------------------

_T128 = [0, 327, 200, 164, 149, 142, 139, 138, 137, 136, 136, 136, 136, 136, 136, 136]
_SHIPPED_Q = {1: [218, 55, 32, 23], 2: [109, 44, 28, 21]}  # leanVM's table at a 2^22 stack


def _a_row(row: int, rate: int, salt: int, num_vars: int = A_LEAF_VARS, residual: int = 10) -> whir.WhirConfig:
    fs = FS[256]
    if row == 0:
        folds, rates = leanvm_schedule(num_vars, rate)
        return whir.WhirConfig("A row 0", 128, 8, 16, num_vars, rates, folds, list(_SHIPPED_Q[rate]),
                               regime=Regime.UDR, salt_bytes=salt, fs=fs)
    folds, rates = design.whir_schedule(num_vars, rate, 5, 3, residual)
    return whir.WhirConfig(f"A row {row}", 128, 8, 16, num_vars, rates, folds, [_T128[min(r, 15)] for r in rates],
                           regime=Regime.UDR, ood_samples=0, salt_bytes=salt, fs=fs)


def _b_whir_open(m: int, rate: int, elem: int = 16, first: int = 4) -> whir.WhirConfig:
    """An opening of Plonky3's binary WHIR at the pin: fold 4, stop at 6 variables, the harness's
    query count for 102 bits a round (as design.b_whir_measured)."""
    folds, rates = design.whir_schedule(m, rate, first, 4, residual=design.B_RESIDUAL)
    c = whir.WhirConfig("B open", 128, elem, 16, m, rates, folds, [1] * len(folds), regime=Regime.UDR, fs=FS[256])
    for i in range(len(folds)):
        c.queries[i] = math.ceil(102 / -math.log2(c.point(i).query_agreement))
    return c


def _a_model(row, rate, salt):
    return whir.size_bytes(_a_row(row, rate, salt))["total"]


def _b_whir_model(rate):  # dense field-element tables (2^23), packed NT (2^16), preprocessed (2^18)
    return sum(whir.size_bytes(_b_whir_open(m, rate))["total"] for m in (23, 16, 18))


def _b_fold_model(rate):
    q = math.ceil(100 / -math.log2((1 + 2.0**-rate) / 2))
    return sum(whir.basefold_size(whir.BaseFoldConfig("B fold", 128, 16, 16, m, rate, 3, queries=q, fs=FS[256]))["total"]
               for m in (17, 18))


def _b_node_model():
    return sum(whir.size_bytes(_b_whir_open(m, 1))["total"] for m in (24, 21))


def _a_node_model(rate, cycles):
    m = math.ceil(math.log2(A_WORDS_PER_CYCLE * cycles))
    return whir.size_bytes(_a_row(4, rate, 0, m, residual=5))["total"]


def _linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return a, my - a * mx


def _a_verify_model(row, rate):
    """Merkle hashing of a leaf proof as the guest does it (16-byte cells: level-0 words count 16 bytes)."""
    if row == 0:
        folds, rates = leanvm_schedule(A_LEAF_VARS, rate)
        q = list(_SHIPPED_Q[rate])
    else:
        folds, rates = design.whir_schedule(A_LEAF_VARS, rate, 5, 3, 5)
        q = [_T128[min(r, 15)] for r in rates]
    c = whir.WhirConfig("A verify", 128, 16, 16, A_LEAF_VARS, rates, folds, q, regime=Regime.UDR, fs=FS[256])
    return design.whir_verify_hashes(c)


def calibration() -> dict:
    """Every calibration constant, with the measured point it was fitted to and the error at the others."""
    out: dict = {}
    # A leaf: an additive non-PCS transcript fitted to row 1 at rate 1/4 (the shipping rate).
    xa = A_ANCHORS[0][3] - _a_model(1, 2, 0)
    out["A_extra_128"] = xa
    out["A_leaf_errors"] = {f"row {r}, rate 1/{2**q}, salt {s}": (_a_model(r, q, s) + xa) / m - 1 for r, q, s, m in A_ANCHORS}
    # A nodes: multiplicative factor on (model + xa), mean over the row-4 node runs.
    ratios = [m / (_a_node_model(q, cyc) + xa) for _, q, cyc, m in A_NODE_ANCHORS]
    fa = sum(ratios) / len(ratios)
    out["A_node_factor"] = fa
    out["A_node_errors"] = {lab: fa * (_a_node_model(q, cyc) + xa) / m - 1 for lab, q, cyc, m in A_NODE_ANCHORS}
    # A verifier hashing: in-circuit Keccak-f = factor x model (16-byte cells), least squares through the origin.
    xs = [_a_verify_model(r, q) for r, q, _, _ in A_VERIFY_ANCHORS]
    ys = [k for _, _, k, _ in A_VERIFY_ANCHORS]
    ka = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
    out["A_hash_factor"] = ka
    out["A_hash_errors"] = {f"row {r}, rate 1/{2**q}": ka * x / y - 1 for (r, q, _, _), x, y in zip(A_VERIFY_ANCHORS, xs, ys)}
    # A cycles per verified proof = c0 + c1 x in-circuit Keccak-f (least squares, 128-bit field).
    c1, c0 = _linfit(ys, [c for *_, c in A_VERIFY_ANCHORS])
    out["A_cycles"] = (c0, c1)
    out["A_cycles_errors"] = {f"row {r}, rate 1/{2**q}": (c0 + c1 * k) / c - 1 for r, q, k, c in A_VERIFY_ANCHORS}
    # B leaf: additive non-PCS transcript fitted to the three WHIR runs (mean), checked on each.
    xb = sum(m - _b_whir_model(q) for q, m in B_WHIR_ANCHORS) / len(B_WHIR_ANCHORS)
    out["B_extra_128"] = xb
    out["B_leaf_errors"] = {f"WHIR, rate 1/{2**q}": (_b_whir_model(q) + xb) / m - 1 for q, m in B_WHIR_ANCHORS}
    xf = B_FOLD_ANCHORS[0][1] - _b_fold_model(2)
    out["B_fold_extra_128"] = xf
    out["B_fold_errors"] = {
        **{f"folding, rate 1/{2**q}, own fit": (_b_fold_model(q) + xf) / m - 1 for q, m in B_FOLD_ANCHORS},
        **{f"folding, rate 1/{2**q}, with the WHIR runs' transcript": (_b_fold_model(q) + xb) / m - 1 for q, m in B_FOLD_ANCHORS},
    }
    # B nodes: additive, mean over the two layer proofs.
    xn = sum(m - _b_node_model() for m in B_NODE_ANCHORS) / len(B_NODE_ANCHORS)
    out["B_node_extra_128"] = xn
    out["B_node_errors"] = {f"layer proof {m} B": (_b_node_model() + xn) / m - 1 for m in B_NODE_ANCHORS}
    # B verifier hashing: fixed + factor x model, at the one measured WHIR leaf point.
    hb = sum(design.whir_verify_hashes(_b_whir_open(m, 2)) for m in (23, 16, 18))
    out["B_hash_factor"] = (B_VERIFY_ANCHOR - B_VERIFY_FIXED) / hb
    return out


_CAL: dict | None = None


def cal() -> dict:
    global _CAL
    if _CAL is None:
        _CAL = calibration()
    return _CAL


# --- configurations ------------------------------------------------------------------------------


def _whir(name, m, rate, first, k, residual, base, ext, salt, digest) -> whir.WhirConfig:
    folds, rates = design.whir_schedule(m, rate, first, k, residual)
    return whir.WhirConfig(name, ext * 8, base, ext, m, rates, folds, [1] * len(folds), regime=Regime.UDR,
                           salt_bytes=salt, fs=copy.deepcopy(FS[digest]))


@dataclass
class Opening:
    """One solved PCS opening of a proof."""

    label: str
    config: whir.WhirConfig
    kind: str  # "W-I A", "W-M", "plain"
    size: float  # model bytes, uncalibrated
    rounds: list[Round]


def _solve_opening(label, c, kind, target) -> Opening:
    if kind == "W-I A":
        # the leaf's whole round list: W-I with the tail sumcheck, and the zero-knowledge rounds outside the
        # opening (wi.zk_rounds: zk-system-a-gaps.md section 11), each one more round in k
        c = wi.solve(c, "A", target, wi.A_WALLET_ZK_E)
        rs, size = wi.rounds(c, "A", wi.A_WALLET_ZK_E), wi.size_bytes(c, "A")["total"]
    elif kind == "W-M":
        c = wi.full_mask_solve(c, target)
        rs, size = wi.full_mask_rounds(c), wi.full_mask_size(c)["total"]
    else:
        c = whir.solve(c, target)
        rs, size = whir.rounds(c), whir.size_bytes(c)["total"]
    return Opening(label, c, kind, size, rs)


def _rounds_fn(kind):
    if kind == "W-I A":
        return lambda c: wi.rounds(c, "A", wi.A_WALLET_ZK_E)
    if kind == "W-M":
        return wi.full_mask_rounds
    return whir.rounds


def min_field_bits(op: Opening, target) -> int:
    """Smallest challenge field (bits) at which every round of this opening, at its solved query
    counts, meets the target: the algebraic rounds' n / |F| terms and the query rounds' t / |F| term."""
    fn = _rounds_fn(op.kind)
    for b in range(64, 1025):
        c = copy.deepcopy(op.config)
        c.field_bits = b
        rs = fn(c)
        if min(r.effective_bits for r in rs) >= target.need_bits(len(rs), c.fs) - 1e-9:
            return b
    raise ValueError("no field up to 1024 bits")


@dataclass
class ShipRow:
    system: str
    layer: str
    target: str
    rate_log: int
    statement: str  # committed size, as words
    num_vars: list[int]
    openings: list[Opening]
    size: float  # calibrated bytes (E)
    size_high: float  # the upper end where the calibration leaves a range (B nodes), else = size
    verify_hashes_model: float  # Keccak-f of the openings' Merkle hashing, native verifier (E, exact for the model)
    verify_hashes_circuit: float  # in-circuit Keccak-f to verify this proof, calibrated (E)
    prover_rel: float  # codeword bytes x challenge-field factor, against the measured leaf (E)
    field_min: int
    need: float
    checks: dict = field(default_factory=dict)
    child_cost: dict = field(default_factory=dict)

    @property
    def queries(self) -> list[list[int]]:
        return [o.config.queries for o in self.openings]

    def schedule(self) -> str:
        parts = []
        for o in self.openings:
            c = o.config
            parts.append(f"{'/'.join(map(str, c.folds))} to 2^{c.vars_at(len(c.folds))}")
        return "; ".join(parts)


def _hashes(op: Opening) -> float:
    c = op.config
    h = design.whir_verify_hashes(c)
    if op.kind == "W-M":  # the mask polynomial's row sits in the same level-0 leaf: longer leaves
        rate = design._keccak_rate_bytes(c.fs.digest_bits)
        k0 = c.folds[0]
        before = math.ceil(((2**k0) * c.base_bytes + c.salt_bytes) / rate)
        after = math.ceil(((2**k0) * (c.base_bytes + c.ext_bytes) + c.salt_bytes) / rate)
        h += c.queries[0] * (after - before)
    return h


def _circuit_hashes(system: str, ops: list[Opening]) -> tuple[float, float]:
    model = sum(_hashes(o) for o in ops)
    if system == "A":
        return model, cal()["A_hash_factor"] * model
    return model, B_VERIFY_FIXED + cal()["B_hash_factor"] * model


def _verify_cost(system: str, row: "ShipRow") -> dict:
    """What verifying one proof of this row costs inside its parent (E)."""
    k = row.verify_hashes_circuit
    if system == "A":
        c0, c1 = cal()["A_cycles"]
        cycles = A_E2_CYCLE_FACTOR * (c0 + c1 * k)
        return {"cycles": cycles, "keccak": k, "words": A_WORDS_PER_CYCLE * cycles}
    q = sum(sum(o.config.queries) for o in row.openings)
    w = B_E2_WITNESS_FACTOR * (B_WITNESS_FIXED + B_WITNESS_PER_QUERY * q)
    return {"keccak": k, "witnesses": w, "dense_cells": B_DENSE_PER_WITNESS * w, "packed_bits": B_BITS_PER_KECCAK * k}


def _optimise(build, kinds, target, other_rounds_of, ranges) -> list[Opening]:
    """Smallest total size over fold schedules; `build(first, k, residual)` gives the configs."""
    best, best_size = None, math.inf
    for first in ranges[0]:
        for k in ranges[1]:
            for residual in ranges[2]:
                try:
                    cs = build(first, k, residual)
                    ops = []
                    counts = [len(_rounds_fn(kd)(x)) for x, kd in zip(cs, kinds)]
                    for i, (c, kind) in enumerate(zip(cs, kinds)):
                        other = OTHER_ROUNDS + sum(counts) - counts[i]
                        t = ProofTreeTarget(**{**target.__dict__, "other_rounds": other})
                        ops.append(_solve_opening(c.name, c, kind, t))
                except ValueError:
                    continue
                s = sum(o.size for o in ops)
                if s < best_size:
                    best, best_size = ops, s
    return best


SHAPES = (range(4, 9), range(3, 6), range(5, 13))


def _target_for(op: Opening, base: ProofTreeTarget, others: list[Opening]) -> ProofTreeTarget:
    other = OTHER_ROUNDS + sum(len(o.rounds) for o in others if o is not op)
    return ProofTreeTarget(**{**base.__dict__, "other_rounds": other})


def _finish(system, layer, target, base_target, rate, statement, ops, extra_bytes, factor, extra_high=None) -> ShipRow:
    pcs = sum(o.size for o in ops)
    size = factor * (pcs + extra_bytes)
    size_high = factor * (pcs + (extra_high if extra_high is not None else extra_bytes))
    hm, hc = _circuit_hashes(system, ops)
    fmin = max(min_field_bits(o, _target_for(o, base_target, ops)) for o in ops)
    need = max(_target_for(o, base_target, ops).need_bits(len(o.rounds), o.config.fs) for o in ops)
    codeword = 0.0
    for o in ops:
        c = o.config
        codeword += 2.0 ** (c.num_vars + c.log_inv_rates[0]) * (c.base_bytes + (c.ext_bytes if o.kind == "W-M" else 0))
    prover = codeword / MEASURED_LEAF_CODEWORD[system] * FIELD_FACTOR_256[system]
    checks = {}
    for o in ops:
        t = _target_for(o, base_target, ops)
        res = evaluate(o.label, o.rounds, o.config.fs)
        for kk, v in t.assess(res, o.config.fs).items():
            checks[kk] = checks.get(kk, True) and v
    row = ShipRow(system, layer, target.name, rate, statement, [o.config.num_vars for o in ops], ops, size, size_high,
                  hm, hc, prover, fmin, need, checks)
    row.child_cost = _verify_cost(system, row)
    return row


def leaf_row(system: str, target: SecurityTarget, rate: int, digest: int | None = None) -> ShipRow:
    t = tree_target(target)
    digest = digest or target.digest_attack
    if system == "A":
        build = lambda f, k, r: [_whir("A leaf W-I", A_LEAF_VARS, rate, f, k, r, 8, 32, 32, digest)]
        ops = _optimise(build, ["W-I A"], t, None, SHAPES)
        return _finish("A", "leaf", target, t, rate, f"2^{A_LEAF_VARS} words (M)", ops, 2 * cal()["A_extra_128"], 1.0)
    build = lambda f, k, r: [_whir("B leaf W-M", B_LEAF_VARS, rate, f, k, r, 8, 32, 32, digest),
                             _whir("B preprocessed", B_PRE_VARS, rate, f, k, r, 8, 32, 0, digest)]
    ops = _optimise(build, ["W-M", "plain"], t, None, SHAPES)
    return _finish("B", "leaf", target, t, rate, f"2^{B_LEAF_VARS} + 2^{B_PRE_VARS} preprocessed words (M)", ops,
                   2 * cal()["B_extra_128"], 1.0)


def node_row(system: str, layer: str, target: SecurityTarget, rate: int, child: ShipRow, stacked: bool = False,
             digest: int | None = None) -> ShipRow:
    t = tree_target(target)
    digest = digest or target.digest_attack
    n = CHILDREN[layer]
    cost = child.child_cost
    if system == "A":
        words = n * cost["words"] + A_WORDS_PER_CYCLE * A_NODE_FIXED_CYCLES
        m = math.ceil(math.log2(words))
        build = lambda f, k, r: [_whir(f"A {layer}", m, rate, f, k, r, 8, 32, 0, digest)]
        ops = _optimise(build, ["plain"], t, None, SHAPES)
        return _finish("A", layer, target, t, rate, f"2^{math.log2(words):.2f} words (E)", ops, 2 * cal()["A_extra_128"],
                       cal()["A_node_factor"])
    dense = n * cost["dense_cells"]
    packed = n * cost["packed_bits"] / 128
    md, mp = math.ceil(math.log2(dense)), math.ceil(math.log2(packed))
    if stacked:  # one commitment for the dense and the packed tables (as system A stacks its tables)
        ms = math.ceil(math.log2(dense + packed))
        build = lambda f, k, r: [_whir(f"B {layer} stacked", ms, rate, f, k, r, 16, 32, 0, digest)]
        ops = _optimise(build, ["plain"], t, None, SHAPES)
    else:
        build = lambda f, k, r: [_whir(f"B {layer} dense", md, rate, f, k, r, 16, 32, 0, digest),
                                 _whir(f"B {layer} packed", mp, rate, f, k, r, 16, 32, 0, digest)]
        ops = _optimise(build, ["plain", "plain"], t, None, SHAPES)
    xn = cal()["B_node_extra_128"]
    return _finish("B", layer, target, t, rate, f"2^{math.log2(dense):.2f} + 2^{math.log2(packed):.2f} GF(2^128) (E)",
                   ops, xn, 1.0, extra_high=2 * xn)


def tree_rows(system: str, target: SecurityTarget, leaf_rate: int = 2, node_rate: int = 2,
              stacked: bool = False, digest: int | None = None) -> list[ShipRow]:
    rows = [leaf_row(system, target, leaf_rate, digest)]
    for layer in LAYERS[1:]:
        rows.append(node_row(system, layer, target, node_rate, rows[-1], stacked, digest))
    return rows


# --- tables ------------------------------------------------------------------------------------------

SHIP_LEAF_RATE = 2  # 1/4: the phone prover's memory; 1/8 saves 2 % of size and doubles the codeword
SHIP_NODE_RATE = 2  # 1/4: 1/2 costs the parent 9 to 45 % more hashing per child, 1/8 doubles the codeword


def _std_field(bits: int) -> str:
    for b in (128, 192, 256, 320, 384):
        if bits <= b:
            return f"GF(2^{b})"
    return f"GF(2^{bits})+"


def _q(row: ShipRow) -> str:
    return "; ".join(", ".join(map(str, q)) for q in row.queries)


def _kib(row: ShipRow) -> str:
    if row.size_high > row.size + 1:
        return f"{row.size / 1024:,.0f} to {row.size_high / 1024:,.0f}"
    return f"{row.size / 1024:,.0f}"


def _fits(row: ShipRow) -> str:
    lo, hi = row.size <= PROOF_LIMIT_BYTES, row.size_high <= PROOF_LIMIT_BYTES
    return "yes" if hi else ("only at the low end" if lo else "**no**")


def _opening(system: str, layer: str, stacked: bool) -> str:
    if layer == "leaf":
        return "W-I" if system == "A" else "W-M + preprocessed (plain)"
    if system == "B":
        return "plain, one stacked commitment" if stacked else "plain, dense + packed (two)"
    return "plain"


HEAD = ("| System | Layer | Opening | Rate | Statement committed | Queries per round (E) | Folds, final | Field needed (bits, E) "
        "| Bits per round needed | Size KiB (E) | Under 1.75 MiB | Verifier Keccak-f: model / in circuit (E) "
        "| Relative prover cost (E) |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def _line(r: ShipRow, stacked: bool) -> str:
    assert all(r.checks.values()), (r.system, r.layer, r.checks)
    return (f"| {r.system} | {r.layer} | {_opening(r.system, r.layer, stacked)} | 1/{2 ** r.rate_log} | {r.statement} "
            f"| {_q(r)} | {r.schedule()} | {r.field_min}: {_std_field(r.field_min)} | {r.need:.1f} | {_kib(r)} | {_fits(r)} "
            f"| {r.verify_hashes_model:,.0f} / {r.verify_hashes_circuit:,.0f} | {r.prover_rel:,.0f} |")


def tables() -> list[str]:
    c = cal()
    out = [f"Tree: {LEAVES_PER_SUB} leaves a sub-bundle, merges of {MERGE_ARITY}, two merge levels: {TREE_LEAVES:,} leaves, "
           f"{TREE_PROOFS:,} proofs (2^{math.log2(TREE_PROOFS):.2f}); union bound over the proofs, one attempt; "
           f"{OTHER_ROUNDS} rounds outside the openings counted in k; no grinding; unique decoding; "
           f"challenge field GF(2^256) for the sizes.", ""]
    for target in (CAT1, CAT3):
        for stacked_b in (True, False):
            label = "B nodes with one stacked commitment (shipping)" if stacked_b else "B nodes as built (two commitments)"
            out += [f"### {target.name}, whole tree, leaf rate 1/{2 ** SHIP_LEAF_RATE}, node rate 1/{2 ** SHIP_NODE_RATE}; {label}", "", HEAD]
            for system in ("AB" if stacked_b else "B"):
                for r in tree_rows(system, target, SHIP_LEAF_RATE, SHIP_NODE_RATE, stacked=stacked_b and system == "B"):
                    out.append(_line(r, stacked_b))
            out.append("")
    out += ["### Leaf rate trade (node rate 1/4, B nodes stacked): the leaf, and what 64 of them cost the sub-bundle", "",
            "| Target | System | Leaf rate | Leaf queries | Leaf size KiB | Verifier Keccak-f of one leaf: model / in circuit "
            "| Cost of verifying one leaf in the sub-bundle | Leaf relative prover cost | Sub-bundle statement | Sub-bundle size KiB |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for target in (CAT1, CAT3):
        for system in "AB":
            for lr in (1, 2, 3):
                rows = tree_rows(system, target, lr, SHIP_NODE_RATE, stacked=system == "B")
                leaf, sub = rows[0], rows[1]
                cc = leaf.child_cost
                cost = (f"{cc['cycles']:,.0f} cycles, {cc['words']:,.0f} words" if system == "A"
                        else f"{cc['keccak']:,.0f} Keccak-f, {cc['witnesses']:,.0f} witnesses")
                out.append(f"| {target.name} | {system} | 1/{2 ** lr} | {_q(leaf)} | {leaf.size / 1024:,.0f} "
                           f"| {leaf.verify_hashes_model:,.0f} / {leaf.verify_hashes_circuit:,.0f} | {cost} | {leaf.prover_rel:,.1f} "
                           f"| {sub.statement} | {_kib(sub)} |")
    out += ["", "### Node rate trade, cat1 (leaf 1/4): node size and what the parent pays per child", "",
            "| System | Node rate | Sub-bundle KiB | Merge KiB | In-circuit Keccak-f to verify a merge child | Merge relative prover cost |",
            "|---|---|---|---|---|---|"]
    for system in "AB":
        for nr in (1, 2, 3):
            rows = tree_rows(system, CAT1, SHIP_LEAF_RATE, nr, stacked=system == "B")
            out.append(f"| {system} | 1/{2 ** nr} | {_kib(rows[1])} | {_kib(rows[2])} | {rows[2].verify_hashes_circuit:,.0f} "
                       f"| {rows[2].prover_rel:,.0f} |")
    out += ["", "### Proven-rule digests (264 bits), cat1, shipping rates", "",
            "| System | Layer | Size KiB at 256-bit digests | at 264-bit digests |", "|---|---|---|---|"]
    for system in "AB":
        a = tree_rows(system, CAT1, SHIP_LEAF_RATE, SHIP_NODE_RATE, stacked=system == "B")
        b = tree_rows(system, CAT1, SHIP_LEAF_RATE, SHIP_NODE_RATE, stacked=system == "B", digest=264)
        for x, y in zip(a, b):
            out.append(f"| {system} | {x.layer} | {_kib(x)} | {_kib(y)} |")
    out += ["", "### Calibration (fit point; error of the model at every measured point)", "",
            "| Quantity | Constant | Errors |", "|---|---|---|"]
    fmt = lambda d: "; ".join(f"{k} {v:+.1%}" for k, v in d.items())
    out.append(f"| A leaf size | non-PCS transcript {c['A_extra_128']:,.0f} B at 128-bit (x2 at 256) | {fmt(c['A_leaf_errors'])} |")
    out.append(f"| A node size | x{c['A_node_factor']:.3f} on model + transcript | {fmt(c['A_node_errors'])} |")
    out.append(f"| A in-circuit Keccak-f per verified leaf | x{c['A_hash_factor']:.3f} on the model (16-byte cells) | {fmt(c['A_hash_errors'])} |")
    c0, c1 = c["A_cycles"]
    out.append(f"| A cycles per verified proof | {c0:,.0f} + {c1:.2f} x Keccak-f; x{A_E2_CYCLE_FACTOR} at 256 bits (E) | {fmt(c['A_cycles_errors'])} |")
    out.append(f"| B leaf size (WHIR) | non-PCS transcript {c['B_extra_128']:,.0f} B at 128-bit (x2 at 256) | {fmt(c['B_leaf_errors'])} |")
    out.append(f"| B leaf size (folding PCS, 793,916 B) | own fit: transcript {c['B_fold_extra_128']:,.0f} B | {fmt(c['B_fold_errors'])} |")
    out.append(f"| B node size | non-PCS {c['B_node_extra_128']:,.0f} B at 128-bit (low end x1, high end x2 at 256) | {fmt(c['B_node_errors'])} |")
    out.append(f"| B in-circuit Keccak-f per verified proof | {B_VERIFY_FIXED:,} + x{c['B_hash_factor']:.3f} on the model | fitted to the one measured point (19,634) |")
    return out
