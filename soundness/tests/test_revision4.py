import math

import pytest

from yugen_soundness import binius64 as b64, current as cu, wi
from yugen_soundness.targets import CAT1


# --- system A: the built mask counts and the 20,000-proof row (yugen-proof-a-zk zero-knowledge.md 17.5) ---

def test_a_wallet_zk_is_the_built_counts():
    # Revision 6: the counts of the merge (zk-merge-notes.md 3, items 2 and 9): 11 bus layers, 52 claims.
    z = wi.A_WALLET_ZK
    assert (z.bus_layers, z.keccak_layers, z.s9_sumchecks, z.gadget_log_len, z.gadget_claims) == (11, 12, 2, 11, 52)
    assert len(wi.zk_rounds(z, 256)) == 3 + 2 + 2 * 12 + 2 * 11 + 3
    r5 = wi.A_WALLET_ZK_R5  # the revision-5 defaults (17.5's reading), kept as the record
    assert (r5.bus_layers, r5.gadget_claims) == (10, 54)
    assert len(wi.zk_rounds(r5, 256)) == 3 + 2 + 2 * 12 + 2 * 10 + 3
    e = wi.A_WALLET_ZK_E  # the earlier estimates stay available for the superseded rows
    assert (e.bus_layers, e.keccak_layers, e.s9_sumchecks, e.gadget_log_len, e.gadget_claims) == (11, 2, 3, 12, 30)


def test_a_leaf_row_at_20000_proofs_is_226_157_154_154():
    t = cu.target_bound()
    sol = cu.a_leaf_bound()
    assert len(sol.rounds) == 87  # 85 at the revision-5 defaults
    assert sol.need == pytest.approx(129 + math.log2(20_000) + math.log2(1 + 87 + 512))
    assert list(sol.config.queries) == cu.A_BOUND_QUERIES == [226, 157, 154, 154]
    for i in range(4):
        q = list(cu.A_BOUND_QUERIES)
        q[i] -= 1
        assert not cu.a_leaf_check(cu.ROW6, t, q).meets
    # the fourth pass's counts miss the bound, as 17.5 reports
    assert not cu.a_leaf_check(cu.ROW6, t, [225, 156, 154, 153]).meets
    # the folded lanes of the masked wallet statement (17.4)
    assert [lv.degree for lv in sol.layout] == [131_559, 16_800, 2_461, 669]


def test_a_node_row9_at_rate_half_needs_368_at_20000_proofs():
    t = cu.target_bound()
    assert not cu.a_node_check(cu.ROW9, 24, 1, t).meets
    assert cu.a_node_solve(cu.ROW9, 24, 1, t).config.queries[0] == 368
    assert cu.a_node_check(cu.ROW9, 24, 2, t).meets


# --- system B: the counted round structure (yugen-proof-b2 parameters.md 2a.4) ---

@pytest.mark.parametrize("shape, k", [
    (b64.Shape(a=17, w=17, p=9, v=16, kappa=7), 132),  # wallet leaf, transparent, pin field
    (b64.Shape(a=17, w=17, p=9, v=17, o=1, c=19, zk=True, kappa=7, relations=4), 175),  # zero knowledge, pin field
    (b64.Shape(a=17, w=17, p=8, v=15, kappa=8), 132),  # transparent, 256-bit field
    (b64.Shape(a=17, w=17, p=8, v=19, o=1, c=21, zk=True, kappa=8, relations=4), 182),  # zero knowledge, 256-bit field
    (b64.Shape(a=23, b=20, w=23, p=10, v=21, kappa=8), 198),  # the leaf-verifier slot as one transparent proof
    (b64.Shape(a=30, b=29, w=30, p=12, v=28, kappa=8), 246),  # a node of 2^30 AND rows
])
def test_k_is_the_measured_census(shape, k):
    assert b64.k_of(shape) == k
    assert len(b64.rounds_counted(shape, 3, 184, 256)) == k


def test_variant_shapes_reproduce_the_measured_leaves():
    assert b64.k_of(b64.leaf_shape(b64.PIN128)) == 175
    assert b64.k_of(b64.leaf_shape(b64.ALL256)) == 182
    assert b64.k_of(b64.leaf_shape(b64.MIXED_T_W1)) == 176


def test_skip_round_is_127():
    rs = {r.name: r for r in b64.rounds_counted(b64.leaf_shape(b64.ALL256), 3, 184, 256)}
    assert rs["bitand.skip"].error_log2 == pytest.approx(math.log2(127) - 256)
    assert b64.INNER_SKIP_DEGREE == 127


def test_tree_need_counted_and_at_the_row_budget():
    n = cu.b_need()
    assert n["budget"] == pytest.approx(129 + math.log2(20_000 * 601))
    assert n["budget"] == pytest.approx(152.52, abs=0.005)
    assert n["counted"] < n["budget"]  # 16,384 leaves of k = 182 and 3,616 nodes of k <= 663 fit the budget
    assert n["sum"] <= 20_000 * 601
    # a node at the bound with its batching transcript
    assert 246 + b64.k_batching(3) == cu.B_K_NODE_BOUND


def test_queries_at_the_budget_are_minimal():
    need = cu.b_need()["budget"]
    for rate, q in ((1, 368), (2, 225), (3, 184), (4, 168)):
        assert b64.queries_for(need, rate) == q
        per = -math.log2((1 + 2.0**-rate) / 2)
        assert q * per >= need > (q - 1) * per


def test_field_128_fails_192_and_256_meet():
    need = cu.b_need()["budget"]
    for fb, ok in ((128, False), (192, True), (256, True)):
        c = cu.b_field_check(need, fb)
        assert (c["leaf"][2] and c["node 2^30 rows"][2]) is ok
    assert 176 <= cu.b_field_check(need, 256)["node 2^30 rows"][3] <= 192


def test_every_listed_round_of_the_mixed_leaf_meets_at_184_queries():
    need = cu.b_need()["budget"]
    for v in (b64.ALL256, b64.MIXED_T, b64.MIXED_T_W1, b64.MIXED_F):
        rs = b64.rounds_counted(b64.leaf_shape(v), 3, 184, v.challenge)
        assert min(r.effective_bits for r in rs) >= need
        rs = b64.rounds_counted(b64.leaf_shape(v), 3, 183, v.challenge)
        assert min(r.effective_bits for r in rs) < need
    # the batching transcript's rounds are far below the fold rounds' error
    assert min(r.effective_bits for r in b64.batching_rounds(3)) > 250


# --- the wrapper model and the sizes ---

def test_wrapper_model_reproduces_both_measured_wrappers():
    pin = b64.wrapper_counts(b64.PIN128, 9)
    big = b64.wrapper_counts(b64.ALL256, 8)
    assert abs(pin["private"] - 98_354) < 100 and abs(pin["derived"] - 594_439) < 100
    assert abs(big["private"] - 393_008) < 300 and abs(big["derived"] - 2_105_223) < 300
    assert 2**18 < pin["constraints"] <= 2**19 and 2**20 < big["constraints"] <= 2**21  # measured 2^19, 2^21


def test_mixed_field_alone_does_not_shrink_the_wrapper_but_direct_transposition_does():
    t = b64.wrapper_counts(b64.MIXED_T, 9)
    assert 2**20 < t["constraints"] <= 2**21  # the public-input operand is still in K (x) K
    assert t["private"] * 2 == b64.wrapper_counts(b64.ALL256, 8)["private"]
    assert b64.wrapper_counts(b64.MIXED_T_W1, 9)["constraints"] <= 2**18
    assert b64.wrapper_counts(b64.ALL256_W1, 8)["constraints"] <= 2**19
    assert b64.wrapper_counts(b64.MIXED_F, 9)["constraints"] <= 2**17


def test_size_model_at_256_bits_against_the_measured_proofs():
    c = b64.cal256()
    assert all(abs(e) < 0.02 for e in c["leaf_errors"].values())
    # the pin's proof of the same node circuit, from the 128-bit fit
    lw, r, q, m = b64.NODE_PIN_SAME_CIRCUIT
    assert abs(b64.node_size(b64.PIN128, lw, r, q, (4, 4, 3, 3)) / m - 1) < 0.07


def test_mixed_leaf_is_smaller_than_the_built_256_bit_leaf_and_every_proof_fits():
    q = 184
    sizes = {v.name: b64.leaf_size(v, 3, q) for v in b64.VARIANTS if v.challenge == 256}
    assert sizes[b64.MIXED_T_W1.name] < sizes[b64.ALL256.name]
    assert sizes[b64.MIXED_F.name] < sizes[b64.MIXED_T_W1.name]
    for v in (b64.ALL256, b64.MIXED_T_W1):
        assert b64.node_size(v, 27, 3, q) <= cu.PROOF_LIMIT
    # the leaf-verifier slot: the mixed field moves its AND rows by a few per cent only
    a0, _ = b64.leaf_slot_rows(b64.ALL256, 3, q)
    a1, _ = b64.leaf_slot_rows(b64.MIXED_T_W1, 3, q)
    assert 0.9 < a1 / a0 < 1.0


def test_mask_symbols_of_the_mixed_leaf_are_extension_symbols():
    p = b64.leaf_proof(b64.MIXED_T_W1, 3, 184)
    t0, t1 = p.trees()[:2]
    assert t0.leaf_bytes == 16 + 32 + 32 and t1.leaf_bytes == 32 + 32 + 32


def test_johnson_candidate_numbers():
    need = cu.b_need()["budget"]
    j = b64.johnson_bciks(27, 3, need)
    assert j["queries"] == 107 and j["meets"]
    assert not b64.johnson_bciks(27, 3, need, field_bits=192)["meets"]


def test_revision4_tables_render():
    out = "\n".join(cu.tables())
    assert "revision 4" in out and "226" in out and "mixed, form T" in out
