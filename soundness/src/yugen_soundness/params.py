"""RECORD ONLY (revision 6, 2026-11-19). This module holds the step 0.3 parameter sets and the leanVM cross-checks; it certifies nothing. Its system A query terms use the
NOMINAL rate 2^-r of each level, not the true rate (2^mu + k)/2^(mu + r) that finding W-1 requires
(docs/whir-additive-soundness.md section 6), and its QROM figures use CMS19's constants for CMS19's own
construction, which covers neither transcript as built. The certified rows are revision5.py (condition C,
true rates) with revision6.py (condition Q under Sharp-Grubbs Theorem 6.6 (2) for the spBCS transcript).

Parameter sets for systems A and B, with the statement-size assumptions written out.

Every size assumption here is an estimate for step 0.3; step 0.4 (E1) and 0.5 (E2) replace each one
with a measurement. See docs/framework-selection.md for the derivation of each trace size.
"""

from __future__ import annotations

from copy import deepcopy

from .bounds import Regime
from .compose import FsParams
from .fri import FriConfig
from .whir import BaseFoldConfig, WhirConfig

QROM_TARGET = 100.0

FS_256 = FsParams(digest_bits=256)
FS_384 = FsParams(digest_bits=384)


def leanvm_schedule(num_vars: int, log_inv_rate: int) -> tuple[list[int], list[int]]:
    """leanVM's WHIR ladder (verifier/src/whir.rs derive_config at commit 84780fb4): first fold 6,
    then 4; the rate grows by k_i - 3 after level 0 and k_i - 1 after; stop at <= 5 variables."""
    folds = [6]
    rates = [log_inv_rate]
    remaining = num_vars - 6
    while remaining > 5:
        reduction = 3 if len(folds) == 1 else 1
        rates.append(rates[-1] + folds[-1] - reduction)
        f = min(4, remaining)
        remaining -= f
        folds.append(f)
    return folds, rates


# --- Cross-checks against shipped code and measurements ------------------------------------


def a_leanvm_shipped(regime: Regime) -> WhirConfig:
    """leanVM as shipped: GF(2^128), 256-bit Keccak, rate 1/16, stacked 2^20, its tabulated queries
    [55, 32, 23, 20] and grinds (query 17, fold 7, OOD 15). leanVM's own analysis (doc/leanvm,
    appendix B: affine combiner, CWYZ26) claims 125 round-by-round bits."""
    folds, rates = leanvm_schedule(20, 4)
    return WhirConfig(
        name=f"A leanVM as shipped ({regime.value})",
        field_bits=128, base_bytes=8, ext_bytes=16, num_vars=20,
        log_inv_rates=rates, folds=folds, queries=[55, 32, 23, 20][: len(folds)],
        regime=regime, grind_fold=7, grind_ood=15, grind_query=17, fs=FS_256,
    )


def b_koalabear_measured(which: str) -> FriConfig:
    """The two Plonky3 KoalaBear runs in bench/results (128 Keccak-f, KeccakAir width 2633)."""
    if which == "bench100":
        return FriConfig(
            name="B KoalaBear bench100 (measured 1,428,394 B)",
            field_bits=124, base_bytes=4, ext_bytes=16, log_k=12, log_blowup=1,
            num_constraints=3000, max_constraint_degree=3, widths=[2633, 8 + 16],
            log_arity=1, queries=100, grind_query=16, salt_bytes=36, fs=FS_256,
        )
    return FriConfig(
        name="B KoalaBear q100 (measured 1,809,036 B)",
        field_bits=248, base_bytes=4, ext_bytes=32, log_k=12, log_blowup=4,
        num_constraints=3000, max_constraint_degree=3, widths=[2633, 16 + 64],
        log_arity=3, queries=110, grind_query=24, grind_fold=16, grind_batch=16, salt_bytes=36,
        fs=FS_384,
    )


def b_binary_measured() -> BaseFoldConfig:
    """Plonky3 binary folding run in bench/results: 163 Keccak-f, 2^23 bits = 2^16 GF(2^128)
    elements, rate 1/2, fold 4, 100-bit target (measured 434,434 B; Merkle arity 4 not modelled)."""
    return BaseFoldConfig(
        name="B Plonky3 binary folding (measured 434,434 B)",
        field_bits=128, base_bytes=16, ext_bytes=16, num_vars=16, log_inv_rate=1, fold=4,
        queries=245, fs=FS_256,
    )


# --- Yugen parameter sets at 100 QROM bits ----------------------------------------------------

# Statement-size assumptions (docs/framework-selection.md, "Statement size"):
A_VARS = {"leaf": 24, "bundle": 28, "merge1": 28, "merge2": 26}
B_VARS = {"leaf": 19, "bundle": 28, "merge1": 28, "merge2": 27}
# Non-PCS transcript (zerocheck, Keccak GKR, buses): leanVM measured 91,608 B against a WHIR model of
# 74,422 B for its smallest program, about 17 KB; doubled for 32-byte challenges.
A_EXTRA = {"leaf": 35_000, "bundle": 40_000, "merge1": 40_000, "merge2": 40_000}


def a_yugen(layer: str, regime: Regime) -> WhirConfig:
    """System A for Yugen: leanVM's WHIR ladder with 256-bit challenges (GF(2^256) as an extension
    of leanVM's GF(2^128)), 384-bit Keccak digests in every Merkle tree, salted leaves (ZK), rate 1/16."""
    m = A_VARS[layer]
    folds, rates = leanvm_schedule(m, 4)
    return WhirConfig(
        name=f"A {layer} ({regime.value})",
        field_bits=256, base_bytes=8, ext_bytes=32, num_vars=m,
        log_inv_rates=rates, folds=folds, queries=[1] * len(folds),
        regime=regime, grind_fold=6, grind_ood=6, grind_query=20, salt_bytes=32,
        extra_bytes=A_EXTRA[layer], fs=deepcopy(FS_384),
    )


def b_yugen(layer: str, regime: Regime) -> BaseFoldConfig:
    """System B for Yugen: Plonky3's native binary stack, GF(2^64) values, 256-bit challenges (a
    degree-4 extension of GF(2^64): GF(2^192), the largest at the pin, leaves the unique-decoding
    fold error n/|F| at about 169 bits, short of the 201 a 100-bit QROM target needs), BaseFold-style
    folding PCS (fold 4), 384-bit Keccak digests, salted leaves, rate 1/16."""
    return BaseFoldConfig(
        name=f"B {layer} ({regime.value})",
        field_bits=256, base_bytes=8, ext_bytes=32, num_vars=B_VARS[layer], log_inv_rate=4, fold=4,
        regime=regime, grind_fold=0, grind_query=20, salt_bytes=32, residual_vars=4,
        extra_bytes=20_000, fs=deepcopy(FS_384),
    )


def b_koalabear_yugen_leaf(regime: Regime) -> FriConfig:
    """System B's alternative configuration: KoalaBear octic FRI with a narrow Keccak AIR (assumed
    width 200 main + 160 LogUp aux + 80 quotient/random base columns, height 2^17)."""
    return FriConfig(
        name=f"B-alt KoalaBear leaf ({regime.value})",
        field_bits=248, base_bytes=4, ext_bytes=32, log_k=17, log_blowup=4,
        num_constraints=600, max_constraint_degree=3, widths=[200, 160, 80],
        log_arity=3, grind_query=20, grind_fold=8, grind_batch=8, salt_bytes=36, regime=regime,
        fs=deepcopy(FS_384),
    )
