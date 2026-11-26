"""Revision 8: system B's rows with every Johnson-regime term (dkt26.py; CHANGELOG revision 8).

Condition C-3 of docs/johnson-row-referee-2.md (section 7): the terms of docs/binius-johnson-row.md revision 2
reproduce the referee's section 5.1 and 5.2; refusals outside the regime of the cited theorems; the node row at
rate 1/4; the candidate rows always labelled as resting on DKT26, a preprint. Task 4: the calculator and the side
script johnson-row/rowcalc.py agree to the bit on the two candidate rows.

Formulas: Dao, Kominers, Thaler, "Reed-Solomon Codes Beyond Johnson", ePrint 2026/2056 (preprint) [DKT26]
Theorem 4.4 (36) to (39), (33)-(34), Lemma 3.3 (6); Haboeck, ePrint 2024/1571, Lemma 3; Sharp, Grubbs, ePrint
2026/2615, Theorem 6.6 (2), Definition I.1. Original test code (the Ycash developers, 2026)."""

import importlib.util
import math
import pathlib
import sys
from fractions import Fraction

import pytest

from yugen_soundness import cli, dkt26 as K

# Revision 9: the revision 8 rows are computed at the book need; they are pinned here under the NON-DEFAULT convention
# (t >= k_q) as a record. The default (every t) is pinned in test_revision9.py.
ROWS = {r.name: r for r in K.rows(convention=K.T_GE_KQ)}
UD8, J8, J16 = ROWS["B leaf + node, unique decoding, 1/8"], ROWS["B leaf + node, Johnson m = 10, 1/8"], \
    ROWS["B leaf + node, Johnson m = 10, 1/16"]
NODE4, NODE4_BUILT, NODE4_J = ROWS["B node, unique decoding, 1/4"], ROWS["B node, unique decoding, 1/4, as built"], \
    ROWS["B node, Johnson m = 10, 1/4"]


def term(r, kind, prefix):
    ts = [t for k, tt in r.proof_terms if k == kind for t in tt]
    (t,) = [t for t in ts if t.name == prefix] or [t for t in ts if t.name.startswith(prefix)]
    return t


# --- the referee's section 5.1 ------------------------------------------------------------------------------------


def test_need_and_list_sizes():
    assert K.need() == pytest.approx(152.519, abs=5e-4)
    assert (J8.list_size, J16.list_size, NODE4_J.list_size, UD8.list_size) == (19, 31, 10, 1)


@pytest.mark.parametrize("r, piop, ring, batch, mask, mask_c, leaf_fold, leaf_fold_c, node_fold, node_fold_c", [
    (J8, 244.76, 248.75, 250.17, 220.14, 219.41, 221.14, 220.41, 212.14, 211.41),
    (J16, 244.06, 248.05, 249.46, 218.19, 217.41, 219.19, 218.41, 210.19, 209.41),
])
def test_every_term_of_section_5_1(r, piop, ring, batch, mask, mask_c, leaf_fold, leaf_fold_c, node_fold, node_fold_c):
    assert term(r, "leaf", "PIOP").bits == pytest.approx(piop, abs=5e-3)
    assert term(r, "leaf", "ring switch").bits == pytest.approx(ring, abs=5e-3)
    assert term(r, "leaf", "claim batching").bits == pytest.approx(batch, abs=5e-3)
    for name in ("mask fold", "index round 0"):
        t = term(r, "leaf", name)
        assert (round(t.bits, 2), round(t.closed_bits, 2)) == (mask, mask_c)
    t = term(r, "leaf", "X fold 1")
    assert (round(t.bits, 2), round(t.closed_bits, 2)) == (leaf_fold, leaf_fold_c)
    t = term(r, "node", "X fold 1")
    assert (round(t.bits, 2), round(t.closed_bits, 2)) == (node_fold, node_fold_c)
    assert r.weakest == ("node", t)
    assert term(r, "leaf", "terminal sumcheck").bits == pytest.approx(255.0)


def test_query_rounds_and_slack():
    assert (J8.queries, J16.queries) == (107, 80)
    assert J8.query_bits == pytest.approx(152.968, abs=5e-4)
    assert 106 * J8.per_query == pytest.approx(151.539, abs=5e-4)
    assert J16.query_bits == pytest.approx(154.369, abs=5e-4)
    assert 79 * J16.per_query == pytest.approx(152.439, abs=5e-4)
    assert (round(J8.slack, 1), round(J16.slack, 1)) == (59.6, 57.7)
    assert J8.meets and J16.meets


def test_exact_count_and_parameters_at_the_node_line():
    """Referee-1 4.2 / referee-2 4.3, 5: B_jet = 29, B_Z = 294 at m = 10, rate 1/8; 2^43.9 exact, 2^44.6 closed; the
    count needed is below 2^103.48 (binius-johnson-row.md 8.4)."""
    ln = K.line(2**30, 2**27, 10)
    assert (ln.m_thm, ln.b_jet, ln.b_z, ln.list_size) == (10, 29, 294, 19)
    assert ln.lam == Fraction(2**30 - 2**27 + 1, ln.A - 2**27 + 1)
    assert round(ln.count_log2, 1) == 43.9 and round(ln.closed_log2, 1) == 44.6
    assert ln.count < ln.closed  # (39): B_cf < 8 n t^3 / (3 rho_-)
    assert K.tolerated_exceptional_log2(K.need(), 38) == pytest.approx(103.48, abs=5e-3)


def test_exact_count_is_below_the_closed_form_at_every_line_length():
    for rate in (3, 4):
        for ln in range(4 + rate, 32 + rate - 2):
            n = 2**ln
            line = K.line(n, n >> rate, 10)
            assert line.count < line.closed
            assert line.list_size <= (19 if rate == 3 else 31)  # F1': the uniform bound holds at every n


def test_list_bound_38_by_hand():
    n, k = 2**22, 2**19
    A, D = K.agreement(n, k, 10), k - 1
    assert A == math.ceil(1.05 * math.sqrt(1 / 8) * n)
    assert K.line(n, k, 10).list_exact == Fraction(n * (A - D), A * A - n * D)


# --- the node at rate 1/4 (referee-2 5.2) and the cross-check against the documents ------------------------------


def test_node_row_at_rate_one_quarter():
    assert NODE4.queries == 225 and NODE4.status == f"{K.NON_DEFAULT}; unique decoding"
    assert NODE4.query_margin == pytest.approx(0.0472, abs=5e-5)
    assert 224 * NODE4.per_query == pytest.approx(151.888, abs=5e-4)
    assert NODE4_BUILT.queries == 226 and NODE4_BUILT.query_margin == pytest.approx(0.7253, abs=5e-5)
    assert NODE4.weakest[1].bits == pytest.approx(227.0)  # "227 bits or more"
    assert NODE4_J.queries == 165 and NODE4_J.meets and K.DKT26_LABEL in NODE4_J.status


def test_cross_check_with_the_documents():
    """184, 107, 80, 225 (certified or candidate counts) and 226 (built) against binius-johnson-row.md 0.4,
    johnson-row-referee-2.md 5, yugen-proof-b2 parameters.md 14.7: no disagreement."""
    got = {name: (doc, calc, ok) for name, doc, calc, _, ok in K.cross_check(list(ROWS.values()))}
    assert all(ok for _, _, ok in got.values()), got
    assert [doc for doc, _, _ in got.values()] == [184, 107, 80, 225, 226]


def test_each_count_less_by_one_fails():
    for r in (UD8, J8, J16, NODE4, NODE4_J):
        assert (r.queries - 1) * r.per_query < r.need <= r.queries * r.per_query


# --- refusals (C-3: hard, not warnings) --------------------------------------------------------------------------


def test_dimension_one_is_refused_unless_lemma_3_3_is_added():
    sh = K.shape("node", 3, 0)
    with pytest.raises(K.OutsideRegime, match="Lemma 3.3"):
        K.terms("dkt", sh, 10)
    with pytest.raises(K.OutsideRegime):
        K.row("x", "dkt", 3, 10, terminal={"node": 0}, kinds=("node",))
    with pytest.raises(K.OutsideRegime, match="excludes D = 0"):
        K.line(8, 1, 10)
    (t,) = [t for t in K.terms("dkt", sh, 10, dimension_one="lemma33") if "dimension 1" in t.name]
    assert t.count == 14 + 2 * 19  # binius-johnson-row.md 8.2: 14 + 38, 250.3 bits
    assert round(t.bits, 1) == 250.3
    assert K.lemma33_count(8, 3) == 14


def test_the_build_has_no_dimension_one_level():
    """yugen-proof-b2 parameters.md 14.7 (C-4): log_terminal_dim 6 / 4 (leaf), 6 / 5 (node) at rates 1/8 / 1/16."""
    for (kind, rate, route), t in K.TERMINAL_AS_BUILT.items():
        assert t >= 1
        K.terms(route, K.shape(kind, rate, route=route), 10 if route == "dkt" else None)  # no refusal


@pytest.mark.parametrize("call, match", [
    (lambda: K.line(2**20, 2**17, 2), "m = 2"),
    (lambda: K.line(16, 16, 10), "n - 2"),
    (lambda: K.line(16, 15, 10), "a > 1"),
    (lambda: K.terms("haboeck", K.shape("leaf", 3), 10), "not available"),
    (lambda: K.terms("dkt", K.shape("leaf", 3), None), "needs m"),
    (lambda: K.lemma33_count(8, 9), "A <= n"),
])
def test_refusals_outside_the_regime(call, match):
    with pytest.raises(K.OutsideRegime, match=match):
        call()


# --- the label (C-3: never "certified" without "DKT26 ... preprint") ---------------------------------------------


def test_johnson_rows_always_carry_the_preprint_label(monkeypatch):
    for r in K.rows():
        if r.route == "dkt":
            assert K.DKT26_LABEL in r.status and "preprint" in r.status.lower()
            assert "certified" not in r.status.replace("not certified", "")
    monkeypatch.setattr(K, "DKT26_ACCEPTED", True)
    assert "certified" in J8.status and K.DKT26_LABEL in J8.status
    for c in (3, 5):  # rows that miss their need are never called certified
        for r in K.rows(*_cat(c), built=False):
            assert r.meets or "certified" not in r.status


def _cat(c):
    from yugen_soundness import category as C

    p = C.PROFILES[c]
    return C.b_need(p), p.field_bits


@pytest.mark.parametrize("argv", [["--rev8"], ["--rev8", "--category", "3"], ["--rev8", "--category", "5"],
                                  ["--rev7"], ["--category", "1"]])
def test_cli_output_labels_every_johnson_row(argv, capsys):
    cli.main(argv)
    out = capsys.readouterr().out
    for line in out.splitlines():
        if line.startswith("| ") and ("Johnson m =" in line) and ("certified" in line or "candidate" in line):
            assert "preprint" in line.lower(), line


def test_rev8_output_is_regenerated():
    """output/revision8-tables.txt is the CLI's output (regenerate with `uv run yugen-soundness --rev8 --convention
    t-ge-kq`): revision 8's rows, labelled as the non-default convention since revision 9."""
    path = pathlib.Path(__file__).parents[1] / "output" / "revision8-tables.txt"
    from yugen_soundness import category as C

    assert path.read_text().rstrip("\n") == "\n".join(K.tables(convention=K.T_GE_KQ) + C.PROVEN_FOOTER)


# --- condition C-2 (Q-5): the counts under "every t" (referee-2 5.4) ---------------------------------------------


def test_q5_every_t_counts():
    assert [K.every_t_count(r)[0] for r in (J8, J16, UD8, NODE4)] == [111, 82, 192, 235]


# --- task 4: the calculator and johnson-row/rowcalc.py agree to the bit ------------------------------------------


def _rowcalc():
    path = pathlib.Path(__file__).parents[2] / "johnson-row" / "rowcalc.py"
    spec = importlib.util.spec_from_file_location("rowcalc", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rowcalc"] = mod
    spec.loader.exec_module(mod)
    return mod


NAMES = {"PIOP round (worst: skip, 127)": "PIOP", "ring switch (each)": "ring switch",
         "claim batching (alpha / mu)": "claim batching", "mask fold gamma": "mask fold", "index round 0": "index round 0",
         "first X fold": "X fold 1"}


@pytest.mark.parametrize("rho, ours", [(1 / 8, J8), (1 / 16, J16)])
def test_agrees_with_rowcalc_to_the_bit(rho, ours):
    rc = _rowcalc()
    theirs = rc.row("dkt", "cat1", 10, rho)
    assert theirs["queries"] == ours.queries
    assert theirs["per_query"] == ours.per_query and theirs["need"] == ours.need
    assert rc.list_bound(10, rho) == ours.list_size
    for kind in ("leaf", "node"):
        for t in theirs[kind]:
            mine = term(ours, kind, NAMES[t.name])
            mine_bits = mine.closed_bits if mine.closed is not None else mine.bits
            assert abs(mine_bits - t.bits) < 1e-9, (kind, t.name, mine_bits, t.bits)  # the closed form (39), as rowcalc
            assert mine.bits >= t.bits  # the exact count (33) is never weaker
    assert abs(ours.weakest[1].closed_bits - theirs["weakest"].bits) < 1e-9
    assert theirs["meets"] and ours.meets
