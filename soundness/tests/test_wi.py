import copy
import math

import pytest

from yugen_soundness import design, whir, wi
from yugen_soundness.bounds import Regime
from yugen_soundness.compose import FsParams
from yugen_soundness.targets import CAT1


def leaf(system):
    folds, rates = design.whir_schedule(24 if system == "A" else 19, 2, 5, 3 if system == "A" else 4, 10)
    return whir.WhirConfig(name=f"{system} leaf", field_bits=256, base_bytes=8, ext_bytes=32, num_vars=24 if system == "A" else 19,
                           log_inv_rates=rates, folds=folds, queries=[1] * len(folds), regime=Regime.UDR, grind_query=20,
                           salt_bytes=32, fs=FsParams(digest_bits=256))


def test_layout_matches_the_hand_count_of_the_hiding_document():
    # zk-hiding-commitment.md section 8, eq-fold masks: 2^19 + 427, 2^16 + 247, 2^13 + 245, 2^10 + 244
    c = leaf("A")
    c.queries = [171, 119, 117, 116]
    lv = wi.layout(c, "B")
    assert [l.lrow for l in lv] == [2**19 + 427, 2**16 + 247, 2**13 + 245, 2**10 + 244]
    # system A: the folded lane is k coefficients longer (affine combiner), guard slots fit under the alignment
    la = wi.layout(c, "A")
    assert [l.degree - l.lrow for l in la] == c.folds
    assert la[0].lrow == 2**19 + 427


def test_level0_aux_rows_count_the_alphabet_degree():
    c = leaf("B")
    c.queries = [171, 119]
    assert wi.layout(c, "B")[0].aux == (1 + 2 * 5) * 4  # a mask coefficient in GF(2^256) takes four GF(2^64) rows


def test_round_list_has_the_new_rounds_and_terms():
    c = leaf("B")
    c.queries = [171, 119]
    rs = {r.name: r for r in wi.rounds(c, "B")}
    assert {"mask0", "mask1", "bc", "final", "query0"} <= set(rs)
    assert rs["mask0"].error_log2 == -256
    n0 = 19 + 2
    assert rs["fold0.0"].error_log2 == pytest.approx(math.log2(2**n0 + 3) - 256)
    assert rs["bc"].error_log2 == pytest.approx(math.log2(2**16 + 1) - 256)
    lv = wi.layout(c, "B")
    assert rs["final"].error_log2 == pytest.approx(119 * math.log2((1 + lv[1].rate) / 2))
    assert len(wi.rounds(c, "B")) == len(whir.rounds(c)) + 3  # two mask rounds and the base-case challenge


@pytest.mark.parametrize("system", ["A", "B"])
def test_solved_wi_sets_meet_cat1_and_are_minimal(system):
    c = wi.solve(leaf(system), system, CAT1)
    rs = wi.rounds(c, system)
    need = CAT1.need_bits(len(rs), c.fs)
    assert min(r.effective_bits for r in rs) >= need
    assert all(CAT1.assess(wi.evaluate_wi(c, system), c.fs).values())
    for i in range(len(c.queries)):
        d = copy.deepcopy(c)
        d.queries[i] -= 1
        assert min(r.effective_bits for r in wi.rounds(d, system)) < need


@pytest.mark.parametrize("system", ["A", "B"])
def test_wi_costs_a_few_percent_of_the_leaf(system):
    plain = whir.solve(leaf(system), CAT1)
    c = wi.solve(leaf(system), system, CAT1)
    a, b = whir.size_bytes(plain)["total"], wi.size_bytes(c, system)["total"]
    assert a < b < 1.08 * a
    assert sum(c.queries) - sum(plain.queries) <= 4


def test_lane_longer_than_the_domain_is_rejected():
    c = leaf("B")
    c.log_inv_rates = [0, 0]
    c.queries = [171, 119]
    with pytest.raises(ValueError):
        wi.layout(c, "B")


def test_full_mask_variant_adds_one_round_and_the_mask_rows():
    c = wi.full_mask_solve(leaf("B"), CAT1)
    assert len(wi.full_mask_rounds(c)) == len(whir.rounds(c)) + 1
    s = wi.full_mask_size(c)
    assert s["mask_rows"] == c.queries[0] * 32 * 32 + 32
    assert s["total"] > wi.size_bytes(wi.solve(leaf("B"), "B", CAT1), "B")["total"]


def test_tree_target_union_model_costs_log2_proofs():
    t = wi.tree_target(CAT1, 1700, 1.0, "union")
    fs = FsParams(digest_bits=256)
    assert t.need_bits(30, fs) - (128 + 1 + math.log2(31)) == pytest.approx(math.log2(1700))
    assert wi.tree_bits_lost(1700, 1.0, 30, "union") == pytest.approx(10.73, abs=0.01)
    t20 = wi.tree_target(CAT1, 1700, 2.0**20, "union")
    assert t20.need_bits(30, fs) - t.need_bits(30, fs) == pytest.approx(20.0)


def test_tree_target_shared_budget_is_within_a_bit_of_the_union_and_ignores_attempts():
    fs = FsParams(digest_bits=256)
    u = wi.tree_target(CAT1, 1700, 1.0, "union").need_bits(30, fs)
    s = wi.tree_target(CAT1, 1700, 1.0, "shared").need_bits(30, fs)
    assert 0 <= u - s < 0.1
    assert wi.tree_target(CAT1, 1700, 2.0**20, "shared").need_bits(30, fs) == s
    assert wi.tree_target(CAT1, 1, 1.0, "shared").need_bits(30, fs) == pytest.approx(128 + 1 + math.log2(31))


def test_tree_parameter_sets_meet_the_tree_target():
    t = wi.tree_target(CAT1, 1700, 1.0, "union")
    for system in "AB":
        c = wi.solve(leaf(system), system, t)
        res = wi.evaluate_wi(c, system)
        assert all(t.assess(res, c.fs).values())
        per_proof = wi.solve(leaf(system), system, CAT1)
        assert sum(c.queries) > sum(per_proof.queries)
        assert not all(t.assess(wi.evaluate_wi(per_proof, system), per_proof.fs).values())
