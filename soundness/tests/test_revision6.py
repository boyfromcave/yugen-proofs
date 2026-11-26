"""Revision 6: spBCS (Sharp-Grubbs, ePrint 2026/2615, Theorem 6.6 and Definition I.1), the corrected system A
zero-knowledge counts, and leanVM's eps_aff (Chiesa-Weissenberg-Yogev-Zheng, ePrint 2026/2863, Theorem 4.10)."""

import math

import pytest

from yugen_soundness import affine, qrom, revision6 as r6, spbcs, wi


# --- CWYZ26 Theorem 4.10, (4.13) ------------------------------------------------------------------------

def test_eps_aff_reproduces_remark_5_3():
    b = affine.eps_aff(2**20, 2**18, 576_717, 128, 3, 49, 567_980)
    assert b.M == 6 and b.list_term == 6  # "M = 6", "l <= 6"
    assert b.delta_log2 < -182  # "delta < 2^-182"
    assert b.bits == pytest.approx(125.42, abs=0.005)  # "approximately 125.42 bits"
    # leanVM's round: eps_aff + 2 l(A - 1, d)/q with l = 5 ("l_0 <= 5"): 16 / q and a fraction
    assert affine.johnson_list(2**20, 576_716, 2**18) == 5
    assert -b.round_log2() == pytest.approx(124.0, abs=0.01)


def test_eps_aff_reproduces_the_example_after_theorem_4_10():
    n, rho = 2**15, 1 / 2048
    assert affine.threshold(n, rho, 0.05) == 2363  # "A = 2363"
    assert math.ceil((math.sqrt(rho) + 0.025) * n) - 1 == 1543  # "B = 1543" (B := ceil((sqrt rho + eta/2) n) - 1)
    b = affine.eps_aff(n, 16, 2363, 128, 1, 28, 1543)
    assert b.bits == pytest.approx(123.25, abs=0.01)  # "~ 2^-123.25"


def test_eps_aff_refuses_failed_hypotheses():
    with pytest.raises(ValueError):
        affine.eps_aff(2**20, 2**18, 576_717, 128, 3, 49, 2**19)  # B^2 <= n (d + 1)
    with pytest.raises(ValueError):
        affine.eps_aff(2**20, 2**18, 576_717, 128, 1, 2, 567_980)  # (4.5) fails


def test_eps_aff_search_does_at_least_as_well_as_the_paper():
    b = affine.best(2**20, 2**18, 576_717, 128)
    assert b is not None and b.bits >= 125.415


def test_no_certified_row_uses_eps_aff():
    rows = r6.leanvm_eps_aff()
    assert rows[0].bound is not None and rows[0].bound.bits > rows[0].dkt26_bits


# --- SG26 Theorem 6.6 (2) ---------------------------------------------------------------------------------

def _counts(**kw):
    base = dict(system="T", verifier_messages=10, prover_messages=10, oracles_per_message=1, q_iop=100,
                log2_l_max=10, n_pos_log2=20.0, leaf_bytes=512, stream_bytes=64)
    base.update(kw)
    return spbcs.TranscriptCounts(**base)


def test_definition_i1_quantities():
    k = _counts()
    assert k.c == 20 and k.c_prime == 21  # c = N_msg max(1, m); c' = max(2, c) + n_J + 1
    assert k.k_q == 2 * 20 + 100 * (1 + 11)  # 2 N_msg + n_B + q_IOP (1 + floor(log2(2 l_max)))
    assert _counts(verifier_messages=1, prover_messages=0).c_prime == 3  # max(2, 1) + 1


def test_tree_terms_match_the_closed_forms_when_k_q_is_negligible():
    k = _counts()
    q = spbcs.SpbcsTree(k, spbcs.FORMS[0], 152.0, 20_000)
    n = math.log2(20_000)
    assert q.iop == pytest.approx((152.0 - 1 - math.log2(6) - n) / 2, abs=1e-6)
    assert q.hash == pytest.approx((256 - 1 - math.log2(6 * 21) - n) / 3, abs=1e-6)


def test_lemma_x_costs_exactly_one_bit_of_the_iop_term():
    k = _counts()
    a = spbcs.SpbcsTree(k, spbcs.FORMS[0], 152.0)
    b = spbcs.SpbcsTree(k, spbcs.FORMS[1], 152.0)
    assert a.iop - b.iop == pytest.approx(1.0, abs=1e-6)
    assert b.c1 == 24 and b.c2 == 6 * 21 * 8


def test_condition_q_is_a_hard_failure():
    k = r6.b_counts()
    with pytest.raises(spbcs.ConditionQFailure):
        spbcs.require(spbcs.SpbcsTree(k, spbcs.FORMS[0], 152.73, 20_000, digest_bytes=24))  # 192-bit digests
    with pytest.raises(spbcs.ConditionQFailure):
        spbcs.require(spbcs.SpbcsTree(k, spbcs.FORMS[0], 140.0, 20_000))  # a weak round


def test_revision6_certificate():
    c = r6.certify()
    assert c.a.counts.verifier_messages == 87 + 512
    assert c.b.counts.verifier_messages == 600
    assert c.a.bits == pytest.approx(67.54, abs=0.01) and c.a.hash == pytest.approx(75.63, abs=0.01)
    assert c.b.bits == pytest.approx(67.43, abs=0.01)
    assert c.b_counter.bits == pytest.approx(66.43, abs=0.01)
    for q in (c.a, c.b, c.b_counter):
        assert q.meets and q.iop < q.hash  # the IOP term binds, as in revision 5
    # the record: Theorem Q's form X gives the same IOP term as spBCS for A (C1 = 6 in both)
    assert qrom.tree_qrom(qrom.FORMS["A"], c.a_e).iop == pytest.approx(c.a.iop, abs=1e-6)


# --- SG26 Theorem 6.6 (3), (4) ------------------------------------------------------------------------------

def test_leaf_term():
    # b_l = 2b: 2^(-4(b_l - b) - 1) plus a negligible second term (Section 6.3: "2^(-4(b_l - b) - 1)")
    assert spbcs.eps_leaf_log2(32, 64, 512) == pytest.approx(-129.0, abs=1e-6)
    # salts as long as the digest: 1/2 a leaf, vacuous over a proof's leaves (SG26 Section 8.4: about 1/e)
    assert spbcs.eps_leaf_log2(32, 32, 512) == pytest.approx(-1.0, abs=1e-9)
    assert spbcs.eps_zk(r6.a_counts(), 64.0, 0.0, leaf_salt_bytes=32).total_log2 == 0.0
    # each byte of leaf salt beyond the digest divides the term by 2^4
    assert spbcs.eps_leaf_log2(32, 65, 512) - spbcs.eps_leaf_log2(32, 64, 512) == pytest.approx(-4.0, abs=1e-6)


def test_salt_terms_reproduce_the_referees_figures():
    k = r6.a_counts()
    for bs, want in ((32, -42.0), (48, -106.0), (64, -170.0)):
        z = spbcs.eps_zk(k, 64.0, 20.0, proof_salt_bytes=bs)
        assert z.salt_term == pytest.approx(want, abs=1e-9)


def test_zk_at_the_pool_is_led_by_the_leaf_term_with_64_byte_salts():
    for k in (r6.a_counts(), r6.b_counts()):
        z = spbcs.eps_zk(k, 64.0, 20.0)
        assert z.leaf_term == max(z.salt_term, z.collision_term, z.key_term, z.leaf_term)
        assert z.total_log2 < -85.0
        assert spbcs.eps_zk(k, 128.0, 20.0).total_log2 == pytest.approx(z.total_log2, abs=1e-4)  # robust in t


def test_unconditional_wi():
    k = r6.a_counts()
    w = spbcs.eps_wi_log2(k, 20.0, 24.0)
    leaf = 20.0 + 1 + k.n_pos_log2 + spbcs.eps_leaf_log2(leaf_bytes=k.leaf_bytes)
    assert w == pytest.approx(leaf, abs=0.01)  # 2 Q n_pos eps_leaf dominates


# --- corrected defaults -----------------------------------------------------------------------------------------

def test_system_a_defaults_are_11_bus_layers_and_52_claims():
    z = wi.A_WALLET_ZK
    assert (z.bus_layers, z.gadget_claims) == (11, 52)
    assert r6.a_counts().verifier_messages - 512 == 87


def test_tables_print():
    out = "\n".join(r6.tables())
    assert "Theorem 6.6 (2)" in out and "125.42" in out


def test_finding_q5_classical_need_under_the_rom_part():
    k = r6.a_counts()
    assert spbcs.classical_need(k) == pytest.approx(129 + math.log2(20_000) + math.log2(1 + k.k_q))
    assert spbcs.classical_need(k, from_k_q=True) == pytest.approx(130 + math.log2(20_000))
    # every t >= 1 is not met by the certified rows; t >= k_q is, with margin
    c = r6.certify()
    assert c.a_e < spbcs.classical_need(k) and c.a_e > spbcs.classical_need(k, from_k_q=True) + 8
