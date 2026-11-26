import copy
import math

import pytest

from yugen_soundness import binius64, current as cu, wi, whir
from yugen_soundness.compose import FsParams
from yugen_soundness.shipping import OTHER_ROUNDS
from yugen_soundness.targets import CAT1


def test_tree_of_specification_0_3():
    assert cu.TREE.level_counts() == [2**14, 2**10, 2**6, 2**2, 1]
    assert cu.TREE.proofs == 17_477
    assert cu.TREE.proofs_any_packing == 5 * 2**14
    t = cu.target()
    fs = FsParams(digest_bits=256)
    assert t.need_bits(20, fs) == pytest.approx(128 + 1 + math.log2(17_477) + math.log2(1 + 20 + OTHER_ROUNDS))


@pytest.mark.parametrize("row, log_n, rate, folds, rates", [
    (cu.ROW6, 22, 2, [5, 3, 3, 3], [2, 6, 8, 10]),
    (cu.ROW8, 22, 2, [6, 3, 3], [2, 5, 5]),
    (cu.ROW9, 24, 1, [5, 3, 3, 3, 3], [1, 5, 7, 9, 11]),  # recursion.md 9.7: 24 - 5 - 3 - 3 - 3 - 3 = 7
])
def test_row_schedule_is_derive_config_for(row, log_n, rate, folds, rates):
    assert row.schedule(log_n, rate) == (folds, rates)


def test_layout_reproduces_the_built_lane_lengths():
    # yugen-proof-a-zk zero-knowledge.md 15.1: the unit test of wi::layout reproduces 524,733 / 65,923 / 8,448 / 1,280
    c = cu.a_config(cu.ROW6, 24, 2, 32, [184, 128, 125, 125])
    assert [lv.degree for lv in wi.layout(c, "A")] == [524_733, 65_923, 8_448, 1_280]


def test_zk_rounds_carry_the_terms_of_the_gaps_document():
    z = wi.A_WALLET_ZK
    rs = {r.name: r.error_log2 + 256 for r in wi.zk_rounds(z, 256)}
    assert rs["S4.rho"] == 0 and rs["S4.dummy"] == pytest.approx(1)  # 1/q (A4) and 2/q (A21, A8-T)
    assert rs["S9.dummy"] == 0  # A20: +1/q
    assert rs["keccak0.dummy"] == pytest.approx(1) and rs["bus0.dummy"] == pytest.approx(2)  # A23 2/q, A24 4/q
    assert rs["gadget.theta"] == pytest.approx(math.log2(z.gadget_claims - 1))
    assert rs["gadget.z"] == pytest.approx(math.log2(z.gadget_log_len))
    assert len(rs) == 3 + z.s9_sumchecks + 2 * z.keccak_layers + 2 * z.bus_layers + 3
    a8 = {r.name: r.error_log2 + 256 for r in wi.zk_rounds(cu.wi.AZk(dummy_form="A8"), 256)}
    assert a8["bus0.dummy"] == pytest.approx(3) and a8["S4.dummy"] == pytest.approx(math.log2(5))


def test_tail_sumcheck_replaces_the_direct_check():
    c = cu.a_config(cu.ROW6, 22, 2, 32)
    lv = wi.layout(c, "A")
    rs = wi.rounds(c, "A")
    tail = [r for r in rs if r.name.startswith("tail")]
    assert len(tail) == math.ceil(math.log2(lv[-1].degree)) and all(r.error_log2 == 1 - 256 for r in tail)
    assert "bc" in {r.name for r in rs}
    assert len(wi.rounds(c, "B")) == len(rs) - len(tail)  # system B's W-I keeps the direct check
    full = wi.rounds(c, "A", wi.A_WALLET_ZK)
    assert len(full) == len(rs) + len(wi.zk_rounds(wi.A_WALLET_ZK, 256))


def test_row6_as_built_is_short_of_the_tree_target_at_the_true_rates():
    built = cu.a_leaf_check(cu.ROW6)
    assert not built.meets and 16 < built.shortfall < 18
    # at the true rates even the row's own 135.58-bit design target is missed by level 0
    assert min(built.query_bits) < 135.58 < min(cu.nominal_bits(built.config))


def test_solved_leaf_meets_is_minimal_and_equals_the_tree_list():
    t = cu.target()
    sol = cu.a_leaf_solve(cu.ROW6, t)
    assert sol.meets
    assert list(sol.config.queries) == [cu.CAT1_TREE_UD_QUERIES[r] for r in sol.config.log_inv_rates]
    for i in range(len(sol.config.queries)):
        q = list(sol.config.queries)
        q[i] -= 1
        assert not cu.a_leaf_check(cu.ROW6, t, q).meets


def test_row8_under_wi_fails_and_its_nearest_row_meets():
    t = cu.target()
    ch = cu.a_leaf_check(cu.ROW8, t)
    assert not ch.meets
    assert cu.a_leaf_solve(cu.ROW8, t).meets
    with pytest.raises(ValueError):  # residual 2^5 under W-I: the last lane's true rate leaves no count that works
        cu.a_leaf_solve(cu.ROW8_R5, t)


@pytest.mark.parametrize("row", cu.NODE_CANDIDATES)
def test_node_candidates_meet_the_tree_target(row):
    for m in (24, 29):
        for rate in (1, 2):
            assert cu.a_node_check(row, m, rate).meets


def test_node_size_calibration():
    x, errs = cu.a_extra_node()
    assert all(abs(e) < 0.05 for e in errs.values())


def test_binius64_query_count_and_field():
    t = cu.target()
    for rate, q in ((1, 367), (2, 225), (3, 184), (4, 167)):
        p = binius64.solve(binius64._leaf(rate, 1, "committed", 256), t)
        assert p.queries == q
        rs = binius64.rounds(p)
        need = t.need_bits(len(rs), p.fs)
        assert min(r.effective_bits for r in rs) >= need
        p.queries -= 1
        assert min(r.effective_bits for r in binius64.rounds(p)) < need
    p = binius64._leaf(3, 184, "committed", 256)
    assert 128 < binius64.min_field_bits(p, t) <= 192
    with pytest.raises(ValueError):  # GF(2^128), the pin's field, cannot reach the target at any query count
        binius64.solve(binius64._leaf(3, 1, "committed", 128), t)


def test_binius64_round_lists():
    zk = {r.name for r in binius64.rounds(binius64._leaf(3, 184, "committed", 256))}
    plain = {r.name for r in binius64.rounds(binius64._node(22, 3, 184, 256))}
    assert {"mask", "wrapper.blend", "query", "inner.skip"} <= zk
    assert "mask" not in plain and "wrapper.blend" not in plain


def test_binius64_calibration_and_rows_under_the_limit():
    c = binius64.cal()
    assert all(abs(e) < 0.03 for e in c["leaf_committed_errors"].values())
    assert all(abs(e) < 0.07 for e in c["node_errors"].values())
    rows = cu.b_rows(node_rates={k: 3 for k in cu.B_NODE_RATE})
    assert all(r.size <= cu.PROOF_LIMIT for r in rows)
    assert all(r.field_min <= 192 for r in rows)


def test_current_tables_render():
    out = "\n".join(cu.tables())
    assert "17,477 proofs" in out and "Binius64" in out
