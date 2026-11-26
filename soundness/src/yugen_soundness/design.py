"""RECORD ONLY (revision 6, 2026-11-19). This module is the record of the first design-basis tables; it certifies nothing. Its system A query terms use the
NOMINAL rate 2^-r of each level, not the true rate (2^mu + k)/2^(mu + r) that finding W-1 requires
(docs/whir-additive-soundness.md section 6), and its QROM figures use CMS19's constants for CMS19's own
construction, which covers neither transcript as built. The certified rows are revision5.py (condition C,
true rates) with revision6.py (condition Q under Sharp-Grubbs Theorem 6.6 (2) for the spBCS transcript).

Design basis: parameter sets for systems A and B at the named targets cat1 and cat3.

Every number this module returns is an ESTIMATE from the models in fri.py / whir.py, calibrated
against the measured runs in bench/results/ (the calibration constants below name their run).
Soundness figures are computed from the bounds in bounds.py; the regime decides whether they rest
on confirmed bounds only (Regime.UDR) or on the unconfirmed Johnson-regime transcription
(Regime.JB_DKT26).

Statement-size assumptions (docs/framework-selection.md section 6, estimates until E1/E2):
  A (leanVM): committed variables leaf 24, bundle 28, merge1 28, merge2 26 (GF(2^64) cells);
  B (Plonky3 binary): leaf 19, bundle 28, merge1 28, merge2 27 (GF(2^64) elements).
Layers: the leaf is hiding (32-byte salts on opened leaves); recursion layers are not (R-9).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import whir
from .bounds import Regime
from .compose import FsParams, LayerResult, evaluate
from .params import A_VARS, B_VARS, leanvm_schedule
from .targets import SecurityTarget

LAYERS = ["leaf", "bundle", "merge1", "merge2"]

# Plonky3's binary WHIR at the pin stops folding with 6 variables left: its measured 2^18-variable
# run opens 319 = 112 + 104 + 103 positions, three query rounds at rates 1/16, 1/128, 1/1024.
B_RESIDUAL = 6

# --- calibration constants (measured; see bench/results/) -----------------------------------------

# Single-thread Keccak-f[1600] permutations per second on the Apple M5 (bench/keccak-rate, 7.70 M/s measured at load 5,
# bench/results/system-a-leafsize-20261118.txt). Grinding g bits costs 2^g permutations on average.
KECCAK_F_PER_S = 7.7e6

# Verifier milliseconds per Keccak-f the verifier performs, per system: measured verify time divided
# by the hash count the model gives for the same configuration.
#  A: leanVM shipped, rate 1/16, 128 compressions: 1.59 ms (system-a-20261118-2238.txt)
#  B: Plonky3 binary WHIR UD, 2^14 rows, rate 1/16, 319 positions: 3 ms (system-b-binary-engineering-20261118.txt)
VERIFY_MS_MEASURED = {"A": 1.59, "B": 3.0}


@dataclass
class DesignPoint:
    system: str
    layer: str
    target: str
    regime: Regime
    rate_log: int
    field_bits: int
    digest_bits: int
    grind_query: int
    config: object
    result: LayerResult
    checks: dict[str, bool]
    size_bytes: float
    verify_hashes: float
    verify_ms: float
    grind_perms: float  # expected Keccak-f the prover spends grinding, per proof
    notes: list[str] = field(default_factory=list)

    @property
    def queries(self):
        return self.config.queries


def _keccak_rate_bytes(digest_bits: int) -> int:
    """Keccak sponge rate for capacity 2 * digest: 136 bytes for 256-bit, 104 for 384-bit, 128 for 264-bit."""
    return (1600 - 2 * digest_bits) // 8


def whir_verify_hashes(c: whir.WhirConfig) -> float:
    rate = _keccak_rate_bytes(c.fs.digest_bits)
    h = c.fs.digest_bits / 8
    total = 0.0
    for i, k in enumerate(c.folds):
        m = c.vars_at(i)
        elem = c.base_bytes if i == 0 else c.ext_bytes
        t = c.queries[i]
        leaf_bytes = (2**k) * elem + c.salt_bytes
        log_leaves = m + c.log_inv_rates[i] - k
        nodes = whir._paths(log_leaves, t, c.cap_height)
        total += t * math.ceil(leaf_bytes / rate) + nodes * math.ceil(2 * h / rate)
    return total


def basefold_verify_hashes(c: whir.BaseFoldConfig) -> float:
    rate = _keccak_rate_bytes(c.fs.digest_bits)
    h = c.fs.digest_bits / 8
    total = 0.0
    for i in range(c.layers):
        m = c.num_vars - i * c.fold
        elem = c.base_bytes if i == 0 else c.ext_bytes
        leaf_bytes = (2**c.fold) * elem + c.salt_bytes
        nodes = whir._paths(m + c.log_inv_rate - c.fold, c.queries, c.cap_height)
        total += c.queries * math.ceil(leaf_bytes / rate) + nodes * math.ceil(2 * h / rate)
    return total


# Measured proof sizes the B models are scaled to. A's model is not scaled: at m = 24 with leanVM's
# tabulated queries plus 17 KB of non-commitment transcript it gives 290,963 B against the measured
# 290,584 B (rate 1/2) and 141,614 B against 153,688 B (rate 1/16) for the leaf-sized leanVM run
# (system-a-leafsize-20261118.txt, 589,976 cycles).
#  B WHIR leaf model:    272,859 B, 2^14 rows, rate 1/16 (system-b-binary-engineering-20261118.txt)
#  B folding PCS model:  434,434 B, 2^12 rows, rate 1/2 (system-b-binary-20261118-2244.txt)
B_WHIR_MEASURED_BYTES = 272_859
B_FOLD_MEASURED_BYTES = 434_434


def size_calibration() -> dict[str, float]:
    from .params import b_binary_measured

    w = b_whir_measured()
    w.extra_bytes = 10_000
    return {
        "B-whir": B_WHIR_MEASURED_BYTES / whir.size_bytes(w)["total"],
        "B-fold": B_FOLD_MEASURED_BYTES / whir.basefold_size(b_binary_measured())["total"],
    }


def _calibration_ms_per_hash() -> dict[str, float]:
    from .params import a_leanvm_shipped

    a = a_leanvm_shipped(Regime.UDR)
    b = b_whir_measured()
    return {
        "A": VERIFY_MS_MEASURED["A"] / whir_verify_hashes(a),
        "B": VERIFY_MS_MEASURED["B"] / whir_verify_hashes(b),
    }


def whir_schedule(num_vars: int, log_inv_rate: int, first: int, fold: int, residual: int = 5):
    """Generic WHIR ladder: first fold `first`, then `fold`; the rate grows by k - 1 per round."""
    folds = [min(first, num_vars)]
    rates = [log_inv_rate]
    remaining = num_vars - folds[0]
    while remaining > residual:
        rates.append(rates[-1] + folds[-1] - 1)
        f = min(fold, remaining)
        remaining -= f
        folds.append(f)
    return folds, rates


def b_whir_measured() -> whir.WhirConfig:
    """Plonky3 binary WHIR UD, 2^14 rows x 1,625 bits = 2^24.67 bits packed into 2^18 GF(2^128)
    elements, rate 1/16, fold 4, 319 opened positions (measured 272,859 B, verify 3 ms). The per-round
    split of the 319 positions is not printed by the harness; the split below is this model's
    solution at the harness's 102-bit classical term target."""
    folds, rates = whir_schedule(18, 4, 4, 4, residual=B_RESIDUAL)
    c = whir.WhirConfig(
        name="B Plonky3 binary WHIR UD 2^14 rows (measured 272,859 B)",
        field_bits=128, base_bytes=16, ext_bytes=16, num_vars=18, log_inv_rates=rates, folds=folds,
        queries=[1] * len(folds), regime=Regime.UDR, cap_height=6, fs=FsParams(digest_bits=256, qrom_c1_log2=0.0),
    )
    # harness accounting: per-term 102 classical bits, no log2(1+k) charge
    for i in range(len(folds)):
        c.queries[i] = math.ceil(102 / -math.log2(c.point(i).query_agreement))
    return c


# --- configurations ----------------------------------------------------------------------------


def _fs(digest_bits: int) -> FsParams:
    return FsParams(digest_bits=digest_bits)


def a_config(layer: str, regime: Regime, rate_log: int, field_bits: int, digest_bits: int,
             grind_query: int, grind_fold: int = 0) -> whir.WhirConfig:
    """System A (leanVM): its WHIR ladder (fold 6 then 4, leanvm_schedule) at the given rate, a
    challenge field of `field_bits` (GF(2^128) at the pin; 192 = cubic over GF(2^64), 256 = quadratic
    over GF(2^128)), committed GF(2^64) cells, salted leaves for the leaf layer. The non-commitment
    transcript (zerocheck, Keccak GKR, buses: measured about 17 KB at 16-byte challenges) is scaled
    with the challenge size."""
    m = A_VARS[layer]
    folds, rates = leanvm_schedule(m, rate_log)
    ext = field_bits // 8
    return whir.WhirConfig(
        name=f"A {layer}", field_bits=field_bits, base_bytes=8, ext_bytes=ext, num_vars=m,
        log_inv_rates=rates, folds=folds, queries=[1] * len(folds), regime=regime,
        grind_fold=grind_fold, grind_ood=grind_fold, grind_query=grind_query,
        salt_bytes=32 if layer == "leaf" else 0, extra_bytes=int(17_500 * ext / 16), fs=_fs(digest_bits),
    )


def b_config(layer: str, regime: Regime, rate_log: int, field_bits: int, digest_bits: int,
             grind_query: int, grind_fold: int = 0, recursion_pcs: str = "folding"):
    """System B (Plonky3 binary stack). Leaf: the hiding WHIR commitment (fold 4 per round, rate
    +3 per round), GF(2^64) values, salted leaves. Recursion layers: the folding (BaseFold-style)
    PCS, fold 4, residual 4 variables. Non-PCS transcript (zerocheck, buses) 10 KB at 16-byte
    challenges, scaled with the challenge size."""
    m = B_VARS[layer]
    ext = field_bits // 8
    if layer == "leaf" or recursion_pcs == "whir":
        folds, rates = whir_schedule(m, rate_log, 4, 4, residual=B_RESIDUAL)
        return whir.WhirConfig(
            name=f"B {layer} (WHIR)", field_bits=field_bits, base_bytes=8, ext_bytes=ext, num_vars=m,
            log_inv_rates=rates, folds=folds, queries=[1] * len(folds), regime=regime,
            grind_fold=grind_fold, grind_ood=grind_fold, grind_query=grind_query,
            salt_bytes=32 if layer == "leaf" else 0, extra_bytes=int(10_000 * ext / 16), fs=_fs(digest_bits),
        )
    return whir.BaseFoldConfig(
        name=f"B {layer} (folding)", field_bits=field_bits, base_bytes=8, ext_bytes=ext, num_vars=m,
        log_inv_rate=rate_log, fold=4, regime=regime, grind_fold=grind_fold, grind_query=grind_query,
        residual_vars=4, extra_bytes=int(10_000 * ext / 16), fs=_fs(digest_bits),
    )


def _rounds(c):
    return whir.rounds(c) if isinstance(c, whir.WhirConfig) else whir.basefold_rounds(c)


def _grinding_events(c) -> tuple[int, int]:
    """(number of query grinds, number of fold/OOD grinds) per proof."""
    rs = _rounds(c)
    q = sum(1 for r in rs if r.name.startswith("query") or r.name == "final")
    f = sum(1 for r in rs if not (r.name.startswith("query") or r.name == "final"))
    return q, f


def design_point(system: str, layer: str, target: SecurityTarget, regime: Regime = Regime.UDR,
                 rate_log: int = 4, field_bits: int = 256, digest_bits: int | None = None,
                 grind_query: int = 20, digest_rule: str = "attack", grind_fold: int = 0) -> DesignPoint:
    digest = digest_bits or (target.digest_attack if digest_rule == "attack" else target.digest_proven)
    build = a_config if system == "A" else b_config
    c = build(layer, regime, rate_log, field_bits, digest, grind_query, grind_fold)
    if isinstance(c, whir.WhirConfig):
        c = whir.solve(c, target)
        size = whir.size_bytes(c)["total"] * (size_calibration()["B-whir"] if system == "B" else 1.0)
        hashes = whir_verify_hashes(c)
    else:
        c = whir.basefold_solve(c, target)
        size = whir.basefold_size(c)["total"] * size_calibration()["B-fold"]
        hashes = basefold_verify_hashes(c)
    res = evaluate(c.name, _rounds(c), c.fs)
    nq, nf = _grinding_events(c)
    grind = nq * 2.0**c.grind_query + (nf * 2.0**c.grind_fold if c.grind_fold else 0.0)
    ms = _calibration_ms_per_hash()[system] * hashes
    return DesignPoint(system, layer, target.name, regime, rate_log, field_bits, digest, c.grind_query, c, res,
                       target.assess(res, c.fs, digest_rule), size, hashes, ms, grind)


def min_fold_grinding(system: str, layer: str, target: SecurityTarget, field_bits: int,
                      rate_log: int = 4, regime: Regime = Regime.UDR, digest_bits: int = 256) -> dict:
    """For a challenge field too small for `target`, the grinding every algebraic round (fold, OOD,
    batch) and every query round's combination term needs, and the prover's expected grinding work."""
    build = a_config if system == "A" else b_config
    c = build(layer, regime, rate_log, field_bits, digest_bits, 0, 0)
    rs = _rounds(c)
    from .compose import resolve_need

    need = resolve_need(target, len(rs), c.fs)
    alg = [r for r in rs if not (r.name.startswith("query") or r.name == "final")]
    g_fold = max(0, math.ceil(need - min(r.effective_bits for r in alg)))
    g_query = 0
    if isinstance(c, whir.WhirConfig):
        # the combination term (t + s) L / |F| of each non-final query round, at t about 200
        comb = [math.log2(200 + c.ood_samples) + c.point(i).list_size_log2 - c.field_bits for i in range(len(c.folds) - 1)]
        if comb:
            g_query = max(0, math.ceil(need + max(comb)))
    work = len(alg) * 2.0**g_fold + (len(c.folds) if isinstance(c, whir.WhirConfig) else 1) * 2.0**g_query
    return {"need": need, "algebraic_rounds": len(alg), "fold_grind": g_fold, "query_grind_min": g_query,
            "grind_perms": work, "grind_seconds_m5": work / KECCAK_F_PER_S,
            "weakest_algebraic_bits": min(r.effective_bits for r in alg)}


# --- prover-time model for the leaf (estimates, 1 M5 thread) -------------------------------------

# Measured leaf-sized proving time at GF(2^128) challenges, by log inverse rate, 1 thread:
#  A: leanVM, 589,976 cycles (system-a-leafsize-20261118.txt)
#  B: Plonky3 binary WHIR UD, 2^14 rows x 1,625 columns (system-b-binary-engineering-20261118.txt)
PROVE_S_MEASURED = {
    "A": {1: 0.948, 2: 1.371, 3: 2.305, 4: 4.284},
    "B": {1: 0.151, 2: 0.163, 3: 0.203, 4: 0.273},
}
# Peak memory of the same runs, bytes.
RSS_MEASURED = {
    "A": {1: 889_815_040, 2: 1_299_759_104, 3: 2_121_482_240, 4: 3_631_349_760},
    "B": {1: 71_417_856, 2: 89_571_328, 3: 130_629_632, 4: 199_147_520},
}
# Prover-time factor for a larger challenge field, against the GF(2^128) path at the same rate.
#  B, GF(2^192) (GF(2^64) values): MEASURED 0.730/0.151, 0.728/0.163, 0.916/0.273 at rates 1/2, 1/4, 1/16
#  (rate 1/8 interpolated); every other entry is an ESTIMATE: GF(2^256) as a quadratic extension of
#  GF(2^128) costs three GF(2^128) products per product (Karatsuba), applied to the share of the prover
#  that works in the challenge field (taken as all of it: an upper estimate).
FIELD_FACTOR = {
    ("A", 128): {r: 1.0 for r in range(1, 5)},
    ("A", 192): {r: 2.0 for r in range(1, 5)},
    ("A", 256): {r: 3.0 for r in range(1, 5)},
    ("B", 128): {r: 1.0 for r in range(1, 5)},
    ("B", 192): {1: 4.83, 2: 4.47, 3: 3.9, 4: 3.36},
    ("B", 256): {1: 7.2, 2: 6.7, 3: 5.9, 4: 5.0},
}


def leaf_prove_seconds(d: DesignPoint) -> float:
    """Estimated single-thread leaf proving time: measured leaf-sized run at the same rate, times the
    challenge-field factor, plus the expected grinding work."""
    base = PROVE_S_MEASURED[d.system][d.rate_log] * FIELD_FACTOR[(d.system, d.field_bits)][d.rate_log]
    return base + d.grind_perms / KECCAK_F_PER_S


# --- shape optimisation (proof-size engineering) -------------------------------------------------


def _with_shape(c, first: int, k: int, residual: int):
    if isinstance(c, whir.WhirConfig):
        folds, rates = whir_schedule(c.num_vars, c.log_inv_rates[0], first, k, residual)
        c.folds, c.log_inv_rates, c.queries = folds, rates, [1] * len(folds)
    else:
        c.fold, c.residual_vars = k, residual
    return c


def shaped_point(system: str, layer: str, target: SecurityTarget, regime: Regime, rate_log: int,
                 field_bits: int, first: int, k: int, residual: int, grind_query: int = 20,
                 digest_rule: str = "attack", recursion_pcs: str = "folding") -> DesignPoint:
    """design_point with an explicit fold schedule: WHIR first fold `first`, later folds `k`, folding
    stops at `residual` variables (sent in clear); for B's folding PCS, fold `k` and residual."""
    digest = target.digest_attack if digest_rule == "attack" else target.digest_proven
    if system == "A":
        base = a_config(layer, regime, rate_log, field_bits, digest, grind_query)
    else:
        base = b_config(layer, regime, rate_log, field_bits, digest, grind_query, recursion_pcs=recursion_pcs)
    c = _with_shape(base, first, k, residual)
    if isinstance(c, whir.WhirConfig):
        c = whir.solve(c, target)
        size = whir.size_bytes(c)["total"] * (size_calibration()["B-whir"] if system == "B" else 1.0)
        hashes = whir_verify_hashes(c)
    else:
        c = whir.basefold_solve(c, target)
        size = whir.basefold_size(c)["total"] * size_calibration()["B-fold"]
        hashes = basefold_verify_hashes(c)
    res = evaluate(c.name, _rounds(c), c.fs)
    nq, _ = _grinding_events(c)
    d = DesignPoint(system, layer, target.name, regime, rate_log, field_bits, digest, c.grind_query, c, res,
                    target.assess(res, c.fs, digest_rule), size, hashes, _calibration_ms_per_hash()[system] * hashes,
                    nq * 2.0**c.grind_query)
    d.notes.append(f"shape first={first} k={k} residual={residual}")
    return d


def optimise(system: str, layer: str, target: SecurityTarget, regime: Regime = Regime.UDR, rate_log: int = 2,
             field_bits: int = 256, grind_query: int = 20, shape_of: DesignPoint | None = None,
             recursion_pcs: str = "folding") -> DesignPoint:
    """Smallest proof over fold schedules (first fold 4..8, later folds 3..5, residual 5..12 variables).
    With `shape_of`, reuse that point's schedule (to show one schedule at another target or regime)."""
    if shape_of is not None:
        first, k, residual = (int(x.split("=")[1]) for x in shape_of.notes[-1].split()[1:])
        return shaped_point(system, layer, target, regime, rate_log, field_bits, first, k, residual, grind_query,
                            recursion_pcs=recursion_pcs)
    best = None
    is_whir = system == "A" or layer == "leaf" or recursion_pcs == "whir"
    for first in (range(4, 9) if is_whir else [0]):
        for k in range(3, 6) if is_whir else range(2, 6):
            for residual in range(5, 13) if is_whir else range(4, 13):
                try:
                    d = shaped_point(system, layer, target, regime, rate_log, field_bits, first, k, residual, grind_query,
                                     recursion_pcs=recursion_pcs)
                except ValueError:
                    continue
                if best is None or d.size_bytes < best.size_bytes:
                    best = d
    return best


def prover_factor(d: DesignPoint) -> float:
    """Prover cost relative to the measured leaf-sized run of the same system at the same rate with
    GF(2^128) challenges: committed-size ratio times the challenge-field factor (grinding excluded).
    A measured run commits 2^24 GF(2^64) cells; B's commits 2^24.67 bits = 2^18.67 GF(2^64) elements."""
    measured_log = 24.0 if d.system == "A" else 18.67
    return 2.0 ** (d.config.num_vars - measured_log) * FIELD_FACTOR[(d.system, d.field_bits)][d.rate_log]
