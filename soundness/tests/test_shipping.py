import copy
import math

import pytest

from yugen_soundness import shipping as sh
from yugen_soundness import whir, wi
from yugen_soundness.compose import FsParams
from yugen_soundness.targets import CAT1, CAT3


@pytest.fixture(scope="module")
def ship():
    return {(t.name, s): sh.tree_rows(s, t, sh.SHIP_LEAF_RATE, sh.SHIP_NODE_RATE, stacked=s == "B")
            for t in (CAT1, CAT3) for s in "AB"}


def test_tree_shape_counts_every_proof():
    assert sh.TREE_LEAVES == 2**14
    assert sh.TREE_PROOFS == 2**14 + 2**8 + 2**4 + 1


def test_tree_target_is_the_union_over_the_proofs_with_all_rounds_in_k():
    fs = FsParams(digest_bits=256)
    t = sh.tree_target(CAT1)
    k = 20
    c = 128 + 1 + math.log2(sh.TREE_PROOFS) + math.log2(1 + k + sh.OTHER_ROUNDS)
    q = 2 * 64 + 1 + math.log2(6) + math.log2(sh.TREE_PROOFS)
    assert t.need_bits(k, fs) == pytest.approx(max(c, q))
    plain = wi.tree_target(CAT1, sh.TREE_PROOFS, 1.0, "union")
    assert t.need_bits(k, fs) == pytest.approx(plain.need_bits(k + sh.OTHER_ROUNDS, fs))


@pytest.mark.parametrize("target", ["cat1", "cat3"])
@pytest.mark.parametrize("system", ["A", "B"])
def test_shipping_rows_meet_every_condition_with_no_grinding(ship, target, system):
    for row in ship[(target, system)]:
        assert all(row.checks.values()), (row.layer, row.checks)
        for o in row.openings:
            assert all(r.grind_bits == 0 for r in o.rounds)
            assert o.config.grind_query == 0 and o.config.grind_fold == 0


@pytest.mark.parametrize("system", ["A", "B"])
def test_leaf_openings_are_minimal(ship, system):
    leaf = ship[("cat1", system)][0]
    for o in leaf.openings:
        fn = sh._rounds_fn(o.kind)
        others = [x for x in leaf.openings if x is not o]
        t = sh._target_for(o, sh.tree_target(CAT1), leaf.openings)
        assert len(others) + 1 == len(leaf.openings)
        for i in range(len(o.config.queries)):
            d = copy.deepcopy(o.config)
            d.queries[i] -= 1
            rs = fn(d)
            assert min(r.effective_bits for r in rs) < t.need_bits(len(rs), d.fs)


def test_leaf_openings_are_the_decided_ones(ship):
    assert [o.kind for o in ship[("cat1", "A")][0].openings] == ["W-I A"]
    assert [o.kind for o in ship[("cat1", "B")][0].openings] == ["W-M", "plain"]
    assert ship[("cat1", "A")][0].num_vars == [22] and ship[("cat1", "B")][0].num_vars == [18, 18]


def test_system_a_fits_the_limit_at_cat1_and_cat3(ship):
    for t in ("cat1", "cat3"):
        assert all(r.size_high <= sh.PROOF_LIMIT_BYTES for r in ship[(t, "A")])


def test_system_b_nodes_as_built_exceed_the_limit_and_stacked_fits_only_low_at_cat1(ship):
    rows = sh.tree_rows("B", CAT1, sh.SHIP_LEAF_RATE, sh.SHIP_NODE_RATE, stacked=False)
    assert rows[0].size <= sh.PROOF_LIMIT_BYTES
    assert all(r.size > sh.PROOF_LIMIT_BYTES for r in rows[1:])
    stacked = ship[("cat1", "B")]
    assert all(r.size <= sh.PROOF_LIMIT_BYTES for r in stacked)
    assert stacked[1].size_high > sh.PROOF_LIMIT_BYTES
    assert all(r.size > sh.PROOF_LIMIT_BYTES for r in ship[("cat3", "B")][1:])


def test_challenge_field_needed(ship):
    for s in "AB":
        assert all(r.field_min <= 192 for r in ship[("cat1", s)])
        assert all(192 < r.field_min <= 256 for r in ship[("cat3", s)])
    # one bit less and some round of the opening fails
    leaf = ship[("cat1", "A")][0]
    o = leaf.openings[0]
    d = copy.deepcopy(o.config)
    d.field_bits = leaf.field_min - 1
    rs = wi.rounds(d, "A")
    t = sh._target_for(o, sh.tree_target(CAT1), leaf.openings)
    assert min(r.effective_bits for r in rs) < t.need_bits(len(rs), d.fs)


def test_calibration_errors_are_small_where_the_model_is_used():
    c = sh.calibration()
    assert all(abs(e) < 0.07 for e in c["A_leaf_errors"].values())
    assert all(abs(e) < 0.03 for e in c["A_node_errors"].values())
    assert all(abs(e) < 0.03 for e in c["A_hash_errors"].values())
    assert all(abs(e) < 0.07 for e in c["A_cycles_errors"].values())
    assert all(abs(e) < 0.01 for e in c["B_leaf_errors"].values())
    assert all(abs(e) < 0.02 for e in c["B_node_errors"].values())
    # the folding-PCS model does not explain the folding leaf with the WHIR runs' transcript
    assert c["B_fold_extra_128"] > 3 * c["B_extra_128"]


def test_leaf_rate_trade_size_falls_and_prover_cost_doubles():
    a = [sh.leaf_row("A", CAT1, r) for r in (1, 2, 3)]
    assert a[0].size > a[1].size > a[2].size
    assert a[0].verify_hashes_model > a[1].verify_hashes_model > a[2].verify_hashes_model
    assert a[1].prover_rel == pytest.approx(2 * a[0].prover_rel) and a[2].prover_rel == pytest.approx(2 * a[1].prover_rel)


def test_proven_hash_cap_is_short_of_128_at_256_bit_digests():
    assert sh.proven_hash_cap(256) == pytest.approx(126.6, abs=0.05)
    assert sh.proven_hash_cap(264) >= 128


def test_solver_refuses_a_lane_that_cannot_reach_the_target():
    c = sh._whir("B leaf", 6, 1, 4, 3, 5, 8, 32, 32, 256)
    with pytest.raises(ValueError):
        wi.full_mask_solve(c, sh.tree_target(CAT3))


def test_tables_render():
    out = "\n".join(sh.tables())
    assert "16,657 proofs" in out and "Calibration" in out
