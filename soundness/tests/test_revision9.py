"""Revision 9: the counting convention EVERY t as the calculator's only default (CHANGELOG revision 9;
docs/decision-qrom-counting.md), and the software findings R8-3, R8-4, R8-7, R8-8, R8-10, R8-11, R8-12, R8-13 of
docs/soundness-rev8-referee.md.

Sources: Sharp, Grubbs, ePrint 2026/2615 [SG26], Theorem 6.6 (2) (page 58), Definitions H.3, H.4 (pages 128, 129),
Definition I.1 (k_q); Dao, Kominers, Thaler, ePrint 2026/2056 (a preprint) [DKT26], Theorem 4.4 (36) to (38).
Original test code (the Ycash developers, 2026)."""

import dataclasses
import math
from decimal import Decimal, getcontext
from fractions import Fraction

import pytest

from yugen_soundness import category as C, cli, dkt26 as K

ROWS = {r.name: r for r in K.rows()}
OLD = {r.name: r for r in K.rows(convention=K.T_GE_KQ)}
CERT1 = C.certify(C.PROFILES[1])
CERT1_OLD = C.certify(dataclasses.replace(C.PROFILES[1], convention=C.T_GE_KQ))


# --- the convention -------------------------------------------------------------------------------------------


def test_every_t_is_the_default_everywhere():
    assert C.PROFILES[1].convention == C.EVERY_T and all(p.convention == C.EVERY_T for p in C.PROFILES.values())
    assert C.M1.convention == C.EVERY_T
    assert all(r.convention == K.EVERY_T for r in ROWS.values())
    assert (K.EVERY_T, K.T_GE_KQ, K.NON_DEFAULT) == (C.EVERY_T, C.T_GE_KQ, C.NON_DEFAULT)
    with pytest.raises(ValueError):
        C.certify(dataclasses.replace(C.PROFILES[1], convention="t >= 1"))


def test_every_t_need_closed_form():
    """kappa_C + 1 + log2 N + log2(1 + k_q): SG26 Theorem 6.6 (2) ROM part at t = 1, N = 20,000 proofs."""
    for cat, kq in ((1, 40_416), (3, 55_662), (5, 71_106)):
        assert C.every_t_need(cat, kq) == pytest.approx(C.kappa_classical(cat) + 1 + math.log2(20_000) + math.log2(1 + kq))
    assert C.every_t_need(1, 40_416) == pytest.approx(158.590, abs=5e-4)


# --- system B: the referee's section 7 counts --------------------------------------------------------------------

B_NEW = {"B leaf + node, unique decoding, 1/8": (184, 192), "B leaf + node, Johnson m = 10, 1/8": (107, 111),
         "B leaf + node, Johnson m = 10, 1/16": (80, 82), "B node, unique decoding, 1/4": (225, 235),
         "B node, Johnson m = 10, 1/4": (165, 171)}


@pytest.mark.parametrize("name", list(B_NEW))
def test_system_b_counts(name):
    old, new = B_NEW[name]
    r = ROWS[name]
    assert (OLD[name].queries, r.queries, r.certified_count) == (old, new, new)
    assert r.meets and (r.queries - 1) * r.per_query < r.need <= r.queries * r.per_query
    # the need is taken at the row's own k_q (C.b_counts at its count), the least fixed point
    nd, kq = K.every_t_need(r.queries, r.rate, route=r.route)
    assert (r.need, r.extra_kq) == (nd, kq)
    nd1, _ = K.every_t_need(r.queries - 1, r.rate, route=r.route)
    assert (r.queries - 1) * r.per_query < nd1
    assert K.every_t_count(r)[0] == new and K.book_count(r) == old


def test_system_b_needs_and_weakest_terms():
    got = {n: (round(r.need, 3), r.extra_kq, round(r.weakest[1].bits, 2)) for n, r in ROWS.items()}
    assert got["B leaf + node, unique decoding, 1/8"] == (158.590, 40_416, 226.0)
    # revision 10 (Lemma D referee m-1): k_q counts the padded group slots (111 -> 115 slots a tree at unit 5, 82 -> 84
    # at unit 4, 171 -> 174 at the assumed unit 6); revision 9 had 24,378 / 19,128 / 35,232; no count moves
    assert got["B leaf + node, Johnson m = 10, 1/8"] == (157.907, 25_170, 212.14)
    assert got["B leaf + node, Johnson m = 10, 1/16"] == (157.542, 19_536, 210.19)
    assert got["B node, unique decoding, 1/4"] == (158.824, 47_520, 227.0)
    assert got["B node, Johnson m = 10, 1/4"] == (158.416, 35_808, 213.99)


def test_the_built_rate_quarter_node_no_longer_meets():
    """226 queries (yugen-proof-b2 params::CAT1_QUERIES) meet the book need but not every t (235 needed)."""
    built = ROWS["B node, unique decoding, 1/4, as built"]
    assert built.queries == 226 and not built.meets and built.status.startswith("DOES NOT MEET")
    assert OLD["B node, unique decoding, 1/4, as built"].meets


def test_cross_check_against_the_referee():
    got = K.cross_check(list(ROWS.values()))
    assert [(fig, calc, ok) for _, fig, calc, _, ok in got] == [(192, 192, True), (111, 111, True), (82, 82, True),
                                                                (235, 235, True), (171, 171, True)]


# --- category rows of both systems at category 1 -----------------------------------------------------------------

A_NEW = {  # (label prefix, stack, rate): (revision 7 / t >= k_q, revision 9 / every t)
    ("row 6 (standalone masked), mode 0", 22, 2): ((226, 157, 154, 154), (233, 162, 159, 159)),
    ("row 6 (standalone masked), mode 1", 20, 2): ((227, 157, 155), (234, 161, 159)),
    ("row 8 (masked in a tree), mode 0", 22, 2): ((226, 160, 163, 179), (233, 166, 168, 185)),
    ("row 8 (masked in a tree), mode 0", 22, 1): ((374, 168, 174, 219), (386, 174, 180, 228)),
    ("row 8 (masked in a tree), mode 1", 21, 2): ((227, 161, 166, 219), (234, 166, 172, 228)),
    ("row 9", 27, 1): ((368, 167, 167, 167, 168, 168, 173), (382, 174, 174, 174, 174, 175, 180)),
    ("row 9", 27, 2): ((225, 160, 160, 160, 160, 160, 163), (234, 166, 166, 166, 166, 167, 169)),
    ("row 9", 30, 1): ((368, 167, 167, 167, 168, 168, 168, 173), (383, 174, 174, 174, 174, 175, 175, 181)),
    ("row 9", 30, 2): ((225, 160, 160, 160, 160, 160, 160, 163), (234, 166, 166, 166, 167, 167, 167, 169)),
}


def _find(rows, label, stack, rate):
    return next(r for r in rows if r.label.startswith(label) and r.stack == stack and r.rate == rate)


@pytest.mark.parametrize("key", list(A_NEW))
def test_system_a_counts(key):
    old, new = A_NEW[key]
    assert _find(CERT1_OLD.a, *key).queries == old
    r = _find(CERT1.a, *key)
    assert r.queries == new and r.margin >= -1e-9
    # revision 10 (R9-4): certified only with the k_q guard on an estimated k_q
    assert r.certified == (r.margin >= r.kq.guard) and r.kq.estimated
    assert r.extra["k_q"] == C.a_row_kq(r.extra["config"], r.rounds)
    assert r.need == pytest.approx(C.every_t_need(1, r.extra["k_q"]))


def test_system_a_row7_plain_leaf():
    """Row 7 (the plain tree leaf, 2^22): the calculator's book counts 225, 160, 160, 160 (yugen-proof-a holds 226,
    161, 161, 161 under its 153.0-bit rule) become 233, 165, 165, 165; at rate 1/2 380, 173, 173, 173."""
    old = dataclasses.replace(C.PROFILES[1], convention=C.T_GE_KQ)
    assert C.a_plain_leaf(22, 2, old).queries == (225, 160, 160, 160)
    for rate, q in ((2, (233, 165, 165, 165)), (1, (380, 173, 173, 173))):
        r = C.a_plain_leaf(22, rate, C.PROFILES[1])
        assert r.queries == q and r.margin >= -1e-9 and r.certified == (r.margin >= r.kq.guard)
        for i in range(len(q)):
            fewer = list(q)
            fewer[i] -= 1
            c = C._a_cfg(C.r5.ROW7, 22, rate, 0, C.PROFILES[1], fewer)
            rs = C.whir.rounds(c)
            assert min(x.effective_bits for x in rs) < C._need(C.PROFILES[1], len(rs), c) - 1e-9


def test_system_b_category_rows():
    assert [r.queries[0] for r in CERT1.b] == [192, 174, 192, 174]
    assert [r.queries[0] for r in CERT1_OLD.b] == [184, 168, 184, 168]
    assert [r.queries[0] for r in CERT1.b_candidates] == [111, 111, 82, 82]
    assert all(r.certified for r in CERT1.b)  # revision 10: every B row clears the k_q guard; A rows: test_revision10


def _rows9():
    for r in CERT1.a + CERT1.b:
        yield pytest.param(r, id=f"{r.system}-{r.label[:24]}-2^{r.stack}-1/{2 ** r.rate}")


@pytest.mark.parametrize("row", list(_rows9()))
def test_each_count_less_by_one_fails_every_t(row):
    p = C.PROFILES[1]
    for i in range(len(row.queries)):
        q = list(row.queries)
        q[i] -= 1
        if row.system == "A" and row.kind == "leaf":
            assert not C.a_leaf_counts_meet(row, q, p)
        elif row.system == "A":
            assert not C.a_node_counts_meet(row, q, p)
        else:
            nd, _ = C.b_need_at(p, q[0], row.rate)
            from yugen_soundness import johnson
            assert q[0] * johnson.query_bits(None, 2.0**-row.rate) < nd


def test_qrom_bits_of_the_tree():
    """Condition Q (SG26 Theorem 6.6 (2), QROM part, N = 20,000): revision 7's 67.25 (A) / 67.43 (B) become 69.58 /
    70.45 with the larger counts (the QROM part already adds k_q to t exactly; only e changes)."""
    assert (round(CERT1_OLD.a_qrom.bits, 2), round(CERT1_OLD.b_qrom.bits, 2)) == (67.25, 67.43)
    assert (round(CERT1.a_qrom.bits, 2), round(CERT1.b_qrom.bits, 2)) == (69.58, 70.45)
    assert CERT1.a_qrom.bits >= 64 and CERT1.b_qrom.bits >= 64


# --- the non-default convention: only behind the flag, always labelled --------------------------------------------


def test_non_default_rows_are_labelled_and_never_certified():
    for r in OLD.values():
        assert r.status.startswith(K.NON_DEFAULT) and "certified (unique" not in r.status
    for r in CERT1_OLD.a + CERT1_OLD.b + CERT1_OLD.b_candidates:
        assert not r.certified and C.NON_DEFAULT in r.status


@pytest.mark.parametrize("argv", [["--rev8", "--convention", "t-ge-kq"], ["--rev7", "--convention", "t-ge-kq"],
                                  ["--category", "1", "--convention", "t-ge-kq"], ["--convention", "t-ge-kq"]])
def test_cli_non_default_output_is_labelled(argv, capsys):
    cli.main(argv)
    out = capsys.readouterr().out
    assert K.NON_DEFAULT.upper() in out or K.NON_DEFAULT in out
    for line in out.splitlines():
        if line.startswith("| ") and ("| certified" in line or "certified (unique" in line):
            assert "non-default convention" in line, line


def test_cli_convention_flag_only_where_it_applies():
    with pytest.raises(SystemExit):
        cli.main(["--rev5", "--convention", "t-ge-kq"])


def test_cli_default_is_revision9(capsys):
    cli.main([])
    out = capsys.readouterr().out
    assert out.startswith("# Revision 10") and "| 192 | 184 | +8 |" in out and K.NON_DEFAULT not in out  # rev 10 default


# --- R8-8: record flags and withdrawn rows ------------------------------------------------------------------------


@pytest.mark.parametrize("argv", [["--rev5"], ["--design"], ["--basis"], ["--legacy"], ["--rev6"]])
def test_record_flags_carry_the_banner(argv, capsys):
    cli.main(argv)
    out = capsys.readouterr().out
    first = out.splitlines()[0]
    assert first.startswith("RECORD (superseded by revision 9") and "PREPRINT" in first and "withdrawn" in first


def test_withdrawn_rows_are_not_offered(capsys):
    cli.main(["--rev7"])
    out = capsys.readouterr().out
    assert "m = 153" not in out and "m = 38" not in out and "m = 107" not in out
    assert "Johnson m = 10 (list 19)" in out and "Johnson m = 10 (list 31)" in out


# --- R8-3: the rate-1/4 Johnson node is arithmetic only -----------------------------------------------------------


def test_rate_quarter_johnson_row_is_arithmetic_only(capsys):
    r = ROWS["B node, Johnson m = 10, 1/4"]
    assert K.ARITH_ONLY in r.status and K.DKT26_LABEL in r.status
    assert all(K.ARITH_ONLY not in x.status for x in ROWS.values() if x is not r)
    cli.main(["--rev8"])
    for line in capsys.readouterr().out.splitlines():
        if line.startswith("| B node, Johnson m = 10, 1/4 |") or line.startswith("#### B node, Johnson m = 10, 1/4"):
            assert "arithmetic only" in line, line


# --- R8-7, R8-4: the D-term and the terminal dimension ------------------------------------------------------------


def _term(r, kind, prefix):
    return next(t for k, ts in r.proof_terms if k == kind for t in ts if t.name.startswith(prefix))


def test_d_term_keyed_by_row():
    assert _term(ROWS["B leaf + node, unique decoding, 1/8"], "leaf", "D-term").count == 49  # 7 x 7 (the 184 build)
    assert _term(ROWS["B leaf + node, Johnson m = 10, 1/8"], "leaf", "D-term").count == 42  # 6 x 7 (the 107 build)
    assert _term(ROWS["B leaf + node, Johnson m = 10, 1/16"], "node", "D-term").count == 75  # 5 x 15
    assert round(_term(ROWS["B leaf + node, unique decoding, 1/8"], "leaf", "D-term").bits, 2) == 250.39


def test_unrecorded_shape_folds_to_dimension_one_with_lemma_3_3():
    r = ROWS["B node, Johnson m = 10, 1/4"]
    (sh,) = r.shapes
    assert (sh.log_terminal_dim, sh.terminal_recorded) == (0, False)
    assert any("message dimension 1" in t.name for _, t in r.all_terms)
    assert _term(r, "node", "D-term").count == 28 * 3  # the bound log_msg (2^r - 1)
    assert r.queries == 171 and round(r.weakest[1].bits, 2) == 213.99  # nothing binds differently (R8-4)


# --- R8-10, R8-11, R8-12: refusals --------------------------------------------------------------------------------


@pytest.mark.parametrize("call", [
    lambda: K.row("x", "dkt", 3),  # m missing
    lambda: K.row("x", "dkt", 3, 10.0),  # not an integer
    lambda: K.row("x", "dkt", 3, True),  # a bool
    lambda: K.line(64, 8, 10.5),
    lambda: K.shape("node", 3, 29),  # above log_msg
    lambda: K.shape("leaf", 3, -1),
    lambda: K.shape("leaf", 3, 2.0),
    lambda: K.row("x", "dkt", 1, 3),  # Johnson threshold 0.825 >= unique-decoding 0.75
])
def test_refusals_r8_10_to_12(call):
    with pytest.raises(K.OutsideRegime):
        call()


def test_no_fold_shape_is_computed_not_crashing():
    """R8-11: log_terminal_dim equal to the message log is a shape with no fold line; it computes (Johnson list from
    the level itself) instead of raising ValueError."""
    for route, m in (("ud", None), ("dkt", 10)):
        r = K.row("x", route, 3, m, kinds=("node",), terminal={"node": K.LOG_MSG["node"]})
        assert not any(t.name.startswith("X fold") for _, t in r.all_terms)
        assert r.list_size == (1 if route == "ud" else 19)


# --- R8-13: an exact recomputation with its own arithmetic, at the referee's boundary cases -----------------------


def _own_line(n, k, m):
    """A, theorem m, B_jet, B_Z by DKT26 (36), (37), in 80-digit decimals with exact integer checks at the ceilings."""
    getcontext().prec = 80
    A = 1
    while (2 * m) ** 2 * A * A < (2 * m + 1) ** 2 * k * n:  # A = ceil((1 + 1/(2m)) sqrt(k/n) n)
        A += 1
    D = k - 1
    x = (Decimal(D) / n).sqrt()
    eta0 = Decimal(A) / n - x
    q = x / (2 * eta0)
    mt = max(int(q) + (0 if q == int(q) else 1), 3)
    t = Fraction(2 * mt + 1, 2)
    jet = t * t * n / D  # B_jet = ceil(sqrt(jet)) - 1
    r = math.isqrt(jet.numerator // jet.denominator)
    while r * r < jet:
        r += 1
    tz = t * t * n / (3 * D)
    return A, mt, r - 1, math.ceil(tz) - 1, tz


@pytest.mark.parametrize("n, k, m", [(49, 36, 3), (1652, 344, 10), (2**22, 2**19, 10), (2**23, 2**19, 10), (8, 2, 10)])
def test_exact_recomputation_at_boundaries(n, k, m):
    A, mt, b_jet, b_z, tz = _own_line(n, k, m)
    ln = K.line(n, k, m)
    assert (ln.A, ln.m_thm, ln.b_jet, ln.b_z) == (A, mt, b_jet, b_z)
    if (n, k, m) == (49, 36, 3):
        assert A == n  # a n = 49 exactly
    if (n, k, m) == (1652, 344, 10):
        assert tz == 177 and b_z == 176  # t^2 / (3 rho_-) an exact integer
