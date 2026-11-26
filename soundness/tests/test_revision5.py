"""Revision 5: finding W-1 (true rates on system A's plain rows), Theorem Q's QROM constants, the salt length,
system B's certified and candidate rows. Sources in the docstrings of revision5.py, qrom.py, salts.py,
johnson.py. Original test code (the Ycash developers, 2026)."""

import math

import pytest

from yugen_soundness import cli, current as cu, johnson, qrom, revision5 as r5, salts, whir


# --- W-1: reproduced from the formula -----------------------------------------------------------------

def _margin(row, log_n, rate, queries=None):
    t = r5.target()
    c = cu.a_config(row, log_n, rate, 0, queries)
    rs = whir.rounds(c)
    return min(r.effective_bits for r in rs) - t.need_bits(len(rs), c.fs)


def test_true_rate_is_the_folded_lane_over_the_domain():
    c = cu.a_config(r5.ROW9, 24, 1, 0)
    assert c.true_rate
    last = len(c.folds) - 1
    assert c.vars_at(last) - c.folds[last] == 3
    assert c.rate(last) == pytest.approx((2**3 + 3) / 2 ** (3 + 4))
    c.true_rate = False
    assert c.rate(last) == 2.0**-4


@pytest.mark.parametrize("log_n,rate,margin", [(24, 1, -4.35), (24, 2, -1.14), (25, 1, -1.72), (25, 2, 0.17),
                                               (26, 1, -0.39), (26, 2, 0.83), (27, 1, -4.36), (27, 2, -1.15),
                                               (28, 1, -1.73), (28, 2, 0.16)])
def test_row9_shortfalls_reproduce_whir_additive_section6(log_n, rate, margin):
    assert _margin(r5.ROW9, log_n, rate) == pytest.approx(margin, abs=0.006)


def test_row7_keeps_its_margin():
    assert _margin(r5.ROW7, 22, 1) == pytest.approx(0.63, abs=0.006)
    assert _margin(r5.ROW7, 22, 2) == pytest.approx(0.90, abs=0.006)


# --- regression: the old schedule fails, the corrected one passes --------------------------------------

@pytest.mark.parametrize("log_n", r5.NODE_STACKS)
def test_row9_old_list_fails_at_rate_half_and_rule_passes(log_n):
    t = r5.target()
    assert not cu.a_node_check(r5.ROW9, log_n, 1, t).meets  # the list by nominal level rate: fails at true rates
    s = r5.shape(r5.ROW9, log_n, 1, t)
    assert s.rule_margin >= 0.7 and s.min_margin >= 0
    assert cu.a_node_check(r5.ROW9, log_n, 1, t, s.rule_q).meets


def test_every_node_and_leaf_shape_meets_with_the_rule():
    for s in r5.leaf_shapes() + r5.node_shapes():
        assert s.rule_margin >= 0.7, (s.log_n, s.rate)
        assert all(q >= l for q, l in zip(s.rule_q, s.list_q))  # the rule never lowers a list count
        assert s.min_margin >= 0


def test_minimal_counts_each_less_by_one_fails():
    for log_n, rate in ((24, 1), (27, 2), (25, 1)):
        s = r5.shape(r5.ROW9, log_n, rate)
        for i in range(len(s.min_q)):
            q = list(s.min_q)
            q[i] -= 1
            assert _margin(r5.ROW9, log_n, rate, q) < 0


def test_last_level_counts_of_the_document():
    # whir-additive-soundness.md 6, fix 1: at the need 152.375, mu = 3: 173 (r = 4), 163 (r = 5); mu = 4: 170; mu = 5: 169
    need = 152.375
    assert [r5.rule_count((2**mu + 3) / 2 ** (mu + r), need) for mu, r in ((3, 4), (3, 5), (4, 4), (5, 4))] == [173, 163, 170, 169]
    tab = r5.rule_table()
    assert (tab[(4, 3)], tab[(5, 3)], tab[(4, 4)], tab[(4, 5)]) == (174, 163, 171, 170)
    assert r5.shape(r5.ROW9, 24, 1).min_q[-1] == 173
    assert r5.shape(r5.ROW9, 24, 1).rule_q == [369, 168, 168, 168, 169, 174]


def test_row9_old_last_level_count_fails_with_rule_elsewhere():
    q = r5.shape(r5.ROW9, 27, 1).rule_q
    q[-1] = 168  # the list's count at the last level
    assert _margin(r5.ROW9, 27, 1, q) < -4


def test_cost_deltas_are_positive_and_small():
    s = r5.shape(r5.ROW9, 24, 1)
    assert 0 < s.bytes_rule < 2_000 and 0 < s.keccak_rule < 100
    assert r5.shape(r5.ROW7, 22, 2).keccak_rule == 0


# --- W-I rows -----------------------------------------------------------------------------------------

def test_row8_needs_per_level_counts():
    t = r5.target()
    old = r5.wi_row("old", r5.ROW8, 2, [226, 161, 161, 161], t=t)
    assert not old.meets and old.margin < -14
    assert r5.wi_solve(r5.ROW8, 2) == [226, 160, 163, 179]
    floor = r5.wi_solve(r5.ROW8, 2, r5.LIST_BITS)
    assert floor == [227, 161, 164, 180]
    assert r5.wi_row("floor", r5.ROW8, 2, floor, t=t).margin >= 0.9


def test_zero_knowledge_row_unaffected_by_w1():
    z = r5.wi_row("zk", cu.ROW6, 2, r5.ZK_QUERIES)
    assert z.meets and z.margin == pytest.approx(0.45, abs=0.01)


# --- Theorem Q -----------------------------------------------------------------------------------------

def test_theorem_q_constants_per_form():
    f = qrom.FORMS
    assert (f["A"].c1, f["A"].c2) == (6, 24)
    assert (f["A, a_V folded"].c1, f["A, a_V folded"].c2) == (12, 96)
    assert (f["B"].c1, f["B"].c2) == (24, 240)
    assert qrom.form_x(4).c2 == 36 and qrom.form_c(4).c2 == 336


def test_qrom_bits_of_the_document():
    a = qrom.tree_qrom(qrom.FORMS["A"], 152.343)
    b = qrom.tree_qrom(qrom.FORMS["B"], 152.343)
    assert (round(a.iop, 2), round(a.hash, 2)) == (67.24, 78.71)
    assert (round(b.iop, 2), round(b.hash, 2)) == (66.24, 77.60)


def test_condition_q_is_a_hard_failure():
    with pytest.raises(qrom.ConditionQFailure):
        qrom.require(qrom.tree_qrom(qrom.FORMS["B"], 152.73, digest_bits=192))
    with pytest.raises(qrom.ConditionQFailure):
        qrom.require(qrom.tree_qrom(qrom.FORMS["A"], 140.0))
    cert = r5.certify()
    assert cert.a.margin > 3 and cert.b.margin > 2 and cert.a_folded.margin > 2.5


def test_b_need_unchanged_by_c1_24():
    assert r5.b_need() == pytest.approx(cu.b_need()["budget"])


# --- salts ---------------------------------------------------------------------------------------------

def test_salt_errors_and_bytes():
    rows = {s: salts.salt_row(s) for s in salts.SALT_CHOICES}
    assert rows[256].per_proof_log2 == 0.0 and not rows[256].statistical
    assert [round(rows[s].per_proof_log2) for s in (384, 512, 576)] == [-40, -104, -136]
    assert round(rows[512].per_tree_log2) == -90
    assert rows[512].added_bytes_per_opened_leaf == 32 and rows[576].added_bytes_per_opened_leaf == 40
    assert [salts.keccak_perms(512, s) for s in salts.SALT_CHOICES] == [5] * 4
    assert [salts.keccak_perms(256, s) for s in salts.SALT_CHOICES] == [3] * 4
    assert salts.sha256_blocks(64, 256) == 2 and salts.sha256_blocks(64, 512) == 3


def test_salt_is_an_input():
    with pytest.raises(ValueError):
        r5.tables(300)
    assert any("576 (selected)" in line for line in r5.tables(576))


# --- system B ------------------------------------------------------------------------------------------

def test_b_rows_reproduce_binius_johnson_row():
    need = r5.b_need()
    ud, hab, dkt, dkt153 = r5.b_rows(need)
    assert (ud.queries, hab.queries, dkt.queries, dkt153.queries) == (184, 107, 107, 102)
    assert [round(r.weakest.bits, 2) for r in (ud, hab, dkt, dkt153)] == [226.00, 169.34, 211.41, 199.80]
    assert ud.status == johnson.CERTIFIED
    assert all(r.status == johnson.CANDIDATE for r in (hab, dkt, dkt153))
    assert johnson.best_m(need).m == 153 and johnson.row("dkt", need, 152).queries == 103
    for r in (ud, hab, dkt153):
        assert (r.queries - 1) * r.per_query < need


def test_b_category3():
    from yugen_soundness import binius64
    from yugen_soundness.targets import CAT3
    n3 = binius64.tree_need(CAT3, [(20_000, 600)], r5.B_FS)
    assert johnson.row("ud", n3).queries == 261 and johnson.row("ud", n3).meets
    d3 = johnson.row("dkt", n3, 3)
    assert not d3.meets and round(d3.weakest.bits, 2) == 216.16


def test_cli_rev5_labels_candidates(capsys):
    cli.main(["--rev5"])
    out = capsys.readouterr().out
    assert "candidate, under referee review" in out
    for line in out.splitlines():
        if "Johnson" in line and line.startswith("|"):
            assert "certified" not in line.replace("candidate", "")
