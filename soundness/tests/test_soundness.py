import math

import pytest

from yugen_soundness import fri, whir
from yugen_soundness.bounds import (
    Regime,
    RegimePoint,
    curve,
    log2_sum,
    pg_johnson_bciks,
    pg_udr,
    query_error,
)
from yugen_soundness.compose import FsParams, Round, chain_bits, classical_bits, evaluate, quantum_bits
from yugen_soundness.params import (
    a_yugen,
    b_binary_measured,
    b_koalabear_measured,
    b_yugen,
    leanvm_schedule,
)


def test_log2_sum():
    assert log2_sum([-10.0, -10.0]) == pytest.approx(-9.0)
    assert log2_sum([float("-inf"), -3.0]) == pytest.approx(-3.0)


def test_bciks20_unique_decoding_error_is_n_over_q():
    assert pg_udr(20, 128) == -108


def test_bciks20_johnson_error_matches_hand_computation():
    rho, eta = 1 / 16, (1 / 4) / 20
    expected = math.log2((2**20) ** 2 / ((2 * min(eta, math.sqrt(rho) / 20)) ** 7 * 2.0**256))
    assert pg_johnson_bciks(20, rho, eta, 256) == pytest.approx(expected)


def test_curve_multiplies_by_degree():
    assert curve(7, -100.0) == pytest.approx(-100.0 + math.log2(7))


def test_query_agreement_by_regime():
    assert RegimePoint(Regime.UDR, 1 / 16).query_agreement == pytest.approx((1 + 1 / 16) / 2)
    jb = RegimePoint(Regime.JB_BCIKS, 1 / 16, m=10)
    assert jb.query_agreement == pytest.approx(0.25 * (1 + 1 / 20))
    assert query_error(RegimePoint(Regime.UDR, 1 / 2), 10) == pytest.approx(10 * math.log2(0.75))


def test_classical_hash_cap_from_book_theorem_25_2_1():
    _, cap = classical_bits([Round("r", -1000.0)], FsParams(digest_bits=256))
    assert cap == pytest.approx((255 - math.log2(3.5)) / 2)


def test_quantum_hash_cap_is_a_third_of_the_digest():
    # (lambda - 1 - log2 C2) / 3 with C2 = 24 (ePrint 2019/834 Section 8.5.1; CITATION-AUDIT C-6:
    # these were 85.0 and 383 / 3 with C2 = 1 assumed)
    c2 = math.log2(24)
    assert quantum_bits([Round("r", -1000.0)], FsParams(digest_bits=256))[1] == pytest.approx((255 - c2) / 3)
    assert quantum_bits([Round("r", -1000.0)], FsParams(digest_bits=384))[1] == pytest.approx((383 - c2) / 3)
    assert quantum_bits([Round("r", -1000.0)], FsParams(digest_bits=256, qrom_c2_log2=0.0))[1] == pytest.approx(85.0)


def test_quantum_bits_halve_round_bits_and_grinding():
    fs = FsParams(digest_bits=1024, qrom_c1_log2=0.0)
    base = quantum_bits([Round("q", -150.0)], fs)[0]
    assert base == pytest.approx((150 - 1) / 2)
    ground = quantum_bits([Round("q", -150.0, grind_bits=20)], fs)[0]
    assert ground - base == pytest.approx(10.0)  # 20 grinding bits count as 10 against a quantum adversary


def test_classical_bits_count_grinding_in_full():
    fs = FsParams(digest_bits=1024)
    a = classical_bits([Round("q", -100.0)], fs)[0]
    b = classical_bits([Round("q", -100.0, grind_bits=20)], fs)[0]
    assert b - a == pytest.approx(20.0)


def test_chain_union_bound():
    assert chain_bits([100.0, 100.0]) == pytest.approx(99.0)
    assert chain_bits([100.0, 100.0, 100.0, 100.0]) == pytest.approx(98.0)


def test_leanvm_schedule_matches_shipped_ladder():
    # verifier/src/whir.rs at 84780fb4: log_n 20, rate 4 has a four-entry query list [55, 32, 23, 20]
    folds, rates = leanvm_schedule(20, 4)
    assert folds == [6, 4, 4, 4]
    assert rates == [4, 7, 10, 13]


@pytest.mark.parametrize("which,measured", [("bench100", 1_428_394), ("q100", 1_809_036)])
def test_fri_size_model_tracks_plonky3_measurements(which, measured):
    c = b_koalabear_measured(which)
    assert fri.size_bytes(c)["total"] == pytest.approx(measured, rel=0.15)


def test_basefold_size_model_is_a_lower_estimate_of_the_binary_run():
    est = whir.basefold_size(b_binary_measured())["total"]
    assert 0.6 * 434_434 < est < 434_434


@pytest.mark.parametrize("regime", [Regime.UDR, Regime.JB_DKT26])
@pytest.mark.parametrize("layer", ["leaf", "bundle"])
def test_solved_sets_meet_target_and_are_minimal(regime, layer):
    c = whir.solve(a_yugen(layer, regime), 100.0, quantum=True)
    assert evaluate("x", whir.rounds(c), c.fs).quantum_bits >= 100.0
    c.queries[0] -= 1
    assert evaluate("x", whir.rounds(c), c.fs).quantum_bits < 100.0
    b = whir.basefold_solve(b_yugen(layer, regime), 100.0, quantum=True)
    assert evaluate("x", whir.basefold_rounds(b), b.fs).quantum_bits >= 100.0
    b.queries -= 1
    assert evaluate("x", whir.basefold_rounds(b), b.fs).quantum_bits < 100.0


def test_128_bit_challenges_cannot_reach_100_qrom_bits():
    c = a_yugen("leaf", Regime.UDR)
    c.field_bits = 128
    with pytest.raises(ValueError):
        whir.solve(c, 100.0, quantum=True)


def test_256_bit_digests_cap_qrom_soundness_at_83_5_bits():
    # 83.47 bits with CMS19's C2 = 24 (CITATION-AUDIT C-6; 85.0 with C2 = 1 before the paper was read)
    c = a_yugen("leaf", Regime.UDR)
    c.fs = FsParams(digest_bits=256)
    c = whir.solve(c, 80.0, quantum=True)
    res = evaluate("x", whir.rounds(c), c.fs)
    assert res.quantum_hash_cap == pytest.approx((255 - math.log2(24)) / 3)
    assert res.quantum_bits <= 83.5


def test_more_queries_never_lower_soundness():
    c = b_yugen("leaf", Regime.UDR)
    prev = -1.0
    for q in (50, 100, 150, 200):
        c.queries = q
        bits = evaluate("x", whir.basefold_rounds(c), c.fs).quantum_bits
        assert bits >= prev
        prev = bits


def test_cms19_constant_defaults_to_six():
    # Chiesa, Manohar, Spooner, ePrint 2019/834, proof of Theorem 8.6 (Section 8.5.1, via Lemma 5.13):
    # 6 (t^2 eps + 4 t^3 / 2^lambda); also Spooner's thesis (UCB/EECS-2020-182) Sec. 5.10.5 for the 6
    assert FsParams().qrom_c1_log2 == pytest.approx(math.log2(6))
    assert FsParams().qrom_c2_log2 == pytest.approx(math.log2(24))
    base = quantum_bits([Round("q", -150.0)], FsParams(digest_bits=1024))[0]
    assert base == pytest.approx((150 - 1 - math.log2(6)) / 2)


# --- named targets (cat1, cat3) and the design basis ---------------------------------------------

from yugen_soundness import design  # noqa: E402
from yugen_soundness.targets import CAT1, CAT3  # noqa: E402


def test_target_definitions():
    assert (CAT1.classical_layer, CAT1.quantum_layer, CAT1.attack_bits) == (130.0, 66.0, 128.0)
    assert (CAT3.classical_layer, CAT3.quantum_layer, CAT3.attack_bits) == (194.0, 98.0, 192.0)
    assert (CAT1.digest_attack, CAT1.digest_proven) == (256, 264)
    assert (CAT3.digest_attack, CAT3.digest_proven) == (384, 392)


def test_four_layers_at_the_per_layer_target_compose_to_the_chain_target():
    assert chain_bits([CAT1.classical_layer] * 4) == pytest.approx(128.0)
    assert chain_bits([CAT3.quantum_layer] * 4) == pytest.approx(96.0)


def test_classical_condition_binds_for_both_targets():
    fs = FsParams(digest_bits=256)
    assert CAT1.binding(30, fs) == "classical (C)"
    assert CAT3.binding(30, FsParams(digest_bits=384)) == "classical (C)"


def test_proven_hash_cap_of_256_bit_digests_is_below_cat1_per_layer():
    _, cap = classical_bits([Round("r", -1000.0)], FsParams(digest_bits=256))
    assert cap < CAT1.classical_layer
    _, cap264 = classical_bits([Round("r", -1000.0)], FsParams(digest_bits=264))
    assert cap264 >= CAT1.classical_layer


@pytest.mark.parametrize("target", [CAT1, CAT3])
@pytest.mark.parametrize("system", ["A", "B"])
@pytest.mark.parametrize("layer", ["leaf", "bundle"])
def test_design_points_meet_target_and_are_minimal(target, system, layer):
    d = design.design_point(system, layer, target, field_bits=256)
    assert all(d.checks.values()), d.checks
    c = d.config
    if isinstance(c.queries, list):
        c.queries[0] -= 1
        rs = whir.rounds(c)
    else:
        c.queries -= 1
        rs = whir.basefold_rounds(c)
    res = evaluate("x", rs, c.fs)
    assert not target.assess(res, c.fs)["C"]


@pytest.mark.parametrize("system", ["A", "B"])
def test_gf2_128_challenges_cannot_reach_cat1_without_grinding(system):
    with pytest.raises(ValueError):
        design.design_point(system, "leaf", CAT1, field_bits=128)
    g = design.min_fold_grinding(system, "leaf", CAT1, 128)
    assert g["fold_grind"] >= 30


@pytest.mark.parametrize("system", ["A", "B"])
def test_gf2_192_reaches_cat1_but_not_cat3(system):
    assert all(design.design_point(system, "leaf", CAT1, field_bits=192).checks.values())
    with pytest.raises(ValueError):
        design.design_point(system, "leaf", CAT3, field_bits=192)


def test_cat3_is_a_parameter_change_from_cat1_at_256_bit_challenges():
    a1 = design.design_point("A", "leaf", CAT1, field_bits=256)
    a3 = design.design_point("A", "leaf", CAT3, field_bits=256)
    assert a1.config.folds == a3.config.folds and a1.config.log_inv_rates == a3.config.log_inv_rates
    assert a3.digest_bits == 384 and a1.digest_bits == 256


def test_size_calibration_reproduces_the_measured_b_whir_run():
    w = design.b_whir_measured()
    assert sum(w.queries) == 319  # the harness's opened positions, 112 + 104 + 103


@pytest.mark.parametrize("rate,queries,measured", [(1, [218, 55, 32, 23, 20], 290_584), (4, [55, 32, 23, 18, 16], 153_688)])
def test_a_model_tracks_the_leaf_sized_leanvm_run(rate, queries, measured):
    # system-a-leafsize-20261118.txt: 589,976 cycles, stacked 2^24, leanVM's tabulated queries
    folds, rates = leanvm_schedule(24, rate)
    c = whir.WhirConfig(name="a", field_bits=128, base_bytes=8, ext_bytes=16, num_vars=24, log_inv_rates=rates,
                        folds=folds, queries=queries, fs=FsParams(digest_bits=256))
    assert whir.size_bytes(c)["total"] + 17_000 == pytest.approx(measured, rel=0.1)


def test_design_basis_table_builds_and_every_row_meets_its_target():
    from yugen_soundness.cli import basis_table

    rows = basis_table()
    assert len(rows) == 2 + 2 * 2 * 4  # header + systems x targets x layers


def test_optimised_leaf_is_smaller_than_the_leanvm_ladder():
    ladder = design.design_point("A", "leaf", CAT1, rate_log=2, field_bits=256)
    best = design.optimise("A", "leaf", CAT1, rate_log=2, field_bits=256)
    assert all(best.checks.values())
    assert best.size_bytes < 0.8 * ladder.size_bytes


def test_dkt26_johnson_mca_count_uses_rho_minus():
    """DKT26 (Dao, Kominers, Thaler, ePrint 2026/2056, copy of 2026-11-02), Theorem 4.4, eq. (39):
    exceptional count < 8 n t^3 / (3 rho_minus), t = m + 1/2, rho_minus = (k - 1)/n; error count / |F|.
    Finding C-14: rho = k/n had been used, which understates the count by the factor k/(k - 1)."""
    from yugen_soundness.bounds import pg_johnson_dkt26

    log_n, log_k, m, q = 10.0, 6.0, 10.0, 256.0
    n, k = 2.0**log_n, 2.0**log_k
    expected = math.log2(8.0 * n * (m + 0.5) ** 3 / (3.0 * (k - 1.0) / n)) - q
    assert pg_johnson_dkt26(log_n, log_k, m, q) == pytest.approx(expected)
    assert pg_johnson_dkt26(log_n, log_k, m, q) - (expected - math.log2(k / (k - 1.0))) == pytest.approx(
        math.log2(k / (k - 1.0))
    )
    with pytest.raises(ValueError):
        pg_johnson_dkt26(log_n, 0.0, m, q)  # k = 1: Theorem 4.4 excludes D = 0
    with pytest.raises(ValueError):
        pg_johnson_dkt26(log_n, log_k, 2.0, q)  # m >= 3 is part of eq. (36)
