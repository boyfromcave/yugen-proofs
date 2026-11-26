"""Revision 10.1: the referee's findings on revision 10 (docs/rev10-referee.md).

R10-1: no row of any type prints "certified" while any of its checks fails, under every flag combination (convention,
hash basis, category), in the row objects and in every CLI output; the positive label names its basis. R10-2: the
footer of what "proven" rests on is printed. R10-6: c' with provenance and a reported path. R10-7: the combined guard.
R10-8: reported inputs below the shape's floor are refused; a report above the estimate re-solves the row; dkt26.Row8
reads the reports. R10-9: the stream term at the shortest stream. Lemma TE's comparison figure (draft).

Source: C. Sharp, P. Grubbs, ePrint 2026/2615 [SG26], Theorem 6.6 (2) (page 58), the remark on stream lengths (page
59), Definition I.1 (page 130), Theorem I.16 (2) (page 142), read from the rendered pages.
"""

import dataclasses
import itertools
import math
import re

import pytest

from yugen_soundness import category as C
from yugen_soundness import cli, dkt26 as K, hashterm as ht

CONVENTIONS = (C.EVERY_T, C.T_GE_KQ)
BASES = ht.HASH_BASES
CATS = (1, 2, 3, 4, 5)

# A POSITIVE "certified": the word at the start of a status (a table cell, a parenthesised heading status, or the
# whole status string), not "not certified", "never certified", "uncertified", "for certified rows".
POSITIVE = re.compile(r"(?:^|\|\s|\(|\*\*)certified\b")


def positive(text: str) -> bool:
    return bool(POSITIVE.search(text))


def _all_rows(cat: int, conv: str, basis: str):
    """Every row type the calculator builds at one flag combination: category.Row (A masked leaves, A nodes, A row 7,
    B unique-decoding rows, B candidates) and dkt26.Row8 (unique decoding, Johnson, arithmetic-only, built count,
    fixed need)."""
    p = dataclasses.replace(C.PROFILES[cat], convention=conv, hash_basis=basis)
    out = []
    try:
        cert = C.certify(p)
        out += cert.a + cert.b + cert.b_candidates
    except (C.CategoryRefusal, C.spbcs.ConditionQFailure):
        out += C.a_rows(p) + C.b_rows(p)
    if cat == 1:
        out += [C.a_plain_leaf(22, r, p) for r in (2, 1)]
        out.append(C.b_row("leaf", 3, p, queries=184))
    fb = p.field_bits
    out += K.rows(None, fb, built=cat == 1, convention=conv, category=cat, hash_basis=basis)
    out.append(K.row("fixed", "ud", 3, None, need_bits=152.52, category=cat, hash_basis=basis))
    return out


@pytest.mark.parametrize("cat,conv,basis", list(itertools.product(CATS, CONVENTIONS, BASES)))
def test_no_row_failing_a_check_prints_certified(cat, conv, basis):
    rows = _all_rows(cat, conv, basis)
    kinds = {type(r).__name__ for r in rows}
    assert kinds == {"Row", "Row8"}
    for r in rows:
        assert r.certified == all(r.checks.values())
        st = r.status
        cell = C._status_cell(r) if isinstance(r, C.Row) else st
        if not r.certified:
            assert not positive(st) and not positive(cell), (cat, conv, basis, st)
        else:
            assert conv == C.EVERY_T
            # the positive label names the basis it was computed on (R10-1)
            words = "attack rule" if basis == ht.HASH_ATTACK_RULE else "every term proven"
            assert words in cell, cell
        if basis == ht.HASH_PROVEN and r.digest_bits < 288:
            assert not r.certified


CLI_ARGV = ([[]] + [["--rev7"], ["--rev8"], ["--rev9"], ["--rev10"]]
            + [["--category", str(c)] for c in CATS] + [["--rev8", "--category", str(c)] for c in (3, 5)])


@pytest.mark.parametrize("argv,conv", list(itertools.product(CLI_ARGV, CONVENTIONS)))
def test_cli_under_proven_prints_no_positive_certified(argv, conv, capsys):
    cli.main(argv + ["--hash-basis", "proven", "--convention", conv])
    out = capsys.readouterr().out
    bad = [ln for ln in out.splitlines() if positive(ln)]
    assert not bad, bad[:3]
    assert "What \"proven\" and \"certified\" rest on" in out  # R10-2 footer


@pytest.mark.parametrize("argv", CLI_ARGV)
def test_cli_under_attack_rule_labels_name_the_basis(argv, capsys):
    cli.main(argv)
    out = capsys.readouterr().out
    for ln in out.splitlines():
        if positive(ln) and ln.startswith("|"):
            assert "attack rule" in ln, ln
    assert "MA-1" in out and "C2" in out and "K-A" in out and "lemma-tree-extraction.md" in out


def test_proven_basis_output_file_has_no_positive_certified():
    from pathlib import Path

    text = (Path(__file__).parents[1] / "output" / "revision10-proven-basis-tables.txt").read_text()
    assert not [ln for ln in text.splitlines() if positive(ln)]
    assert text.rstrip("\n") == "\n".join(cli.rev9_tables("every-t", "proven"))


# --- R10-6: c' with provenance --------------------------------------------------------------------------------------


def test_c_prime_is_marked_estimated_and_can_be_reported(monkeypatch):
    p = C.PROFILES[1]
    r = C.b_row("leaf", 3, p)
    assert r.c_input.estimated and r.c_input.label() == "2,401 (E)"
    line = C.rows_table([r], "t")[-1]
    assert "| 2,401 (E) |" in line
    a = C.a_node(27, 2, p)
    assert a.c_input.estimated and a.c_prime == 2_173
    key = ht.b_report_key("leaf", 3, "ud")
    monkeypatch.setitem(ht.REPORTED_KQ, key, ht.KqReport(40_416, (192,), "T-1 test line", n_msg=1_200, m=1))
    r2 = C.b_row("leaf", 3, p)
    assert r2.c_input.provenance == ht.KQ_REPORTED and r2.c_prime == max(2, 1_200 * 1) + 1
    assert r2.hash.classical_tree > r.hash.classical_tree  # a smaller c' raises the hash term's level


# --- R10-7: the combined guard -----------------------------------------------------------------------------------------


def test_guard_is_the_larger_of_the_allowance_and_the_named_errors():
    assert ht.kq_guard_bits(45_658) == pytest.approx(math.log2(1.1), abs=1e-4)
    k, q = 16_684, 728  # A row 7 at 1/4
    g = ht.kq_guard_bits(k, named_extra=4 * 512 + q)
    assert g == pytest.approx(math.log2(1 + k + 2_048 + q) - math.log2(1 + k)) and round(g, 3) == 0.222
    r7 = C.a_plain_leaf(22, 2, C.PROFILES[1])
    assert r7.kq.named_extra == 4 * 512 + sum(r7.queries) and r7.kq.guard == pytest.approx(g)
    # B: one more Merkle level (q_IOP, padded slots) is below the 10 % allowance at every row
    for r in C.certify(C.PROFILES[1]).b:
        assert r.kq.guard == pytest.approx(math.log2(1.1), abs=1e-3) and r.certified


# --- R10-8: reported inputs ----------------------------------------------------------------------------------------------


def test_reported_k_q_below_the_floor_is_refused(monkeypatch):
    p = C.PROFILES[1]
    r = next(x for x in C.certify(p).a if x.label.startswith("row 6") and x.stack == 20)
    monkeypatch.setitem(ht.REPORTED_KQ, ht.a_report_key(r.label, r.stack, r.rate),
                        ht.KqReport(1, r.queries, "implausible"))
    with pytest.raises(ht.ImplausibleReport):
        C.certify(p)
    floor = ht.kq_floor(r.rounds, sum(r.queries))
    monkeypatch.setitem(ht.REPORTED_KQ, ht.a_report_key(r.label, r.stack, r.rate),
                        ht.KqReport(floor - 1, r.queries, "one below the floor"))
    with pytest.raises(ht.ImplausibleReport):
        C.certify(p)
    monkeypatch.setitem(ht.REPORTED_KQ, ht.b_report_key("node", 3, "ud"), ht.KqReport(10, (192,), "B, implausible"))
    monkeypatch.delitem(ht.REPORTED_KQ, ht.a_report_key(r.label, r.stack, r.rate))
    with pytest.raises(ht.ImplausibleReport):
        C.b_row("node", 3, p)
    with pytest.raises(ht.ImplausibleReport):
        K.rows()
    monkeypatch.setitem(ht.REPORTED_KQ, ht.b_report_key("node", 3, "ud"),
                        ht.KqReport(40_416, (192,), "B, N_msg too small", n_msg=100, m=2))
    with pytest.raises(ht.ImplausibleReport):
        C.b_row("node", 3, p)


def test_report_above_the_estimate_resolves_and_prints_the_new_count(monkeypatch):
    p = C.PROFILES[1]
    base = C.certify(p)
    r = next(x for x in base.a if x.label.startswith("row 6") and x.stack == 20)
    monkeypatch.setitem(ht.REPORTED_KQ, ht.a_report_key(r.label, r.stack, r.rate),
                        ht.KqReport(r.kq.value * 4, r.queries, "four times the estimate"))
    cert = C.certify(p)  # no CategoryRefusal: the row is re-solved
    r2 = next(x for x in cert.a if x.label == r.label and x.stack == r.stack and x.rate == r.rate)
    assert sum(r2.queries) > sum(r.queries) and r2.margin >= 0 and r2.need > r.need + 1.9
    text = "\n".join(C.rows_table(cert.a, "t"))
    assert "re-solved at the T-1 report" in text and ", ".join(map(str, r2.queries)) in text
    # B: the same through b_fixed_point
    b = next(x for x in base.b if x.kind == "leaf" and x.rate == 3)
    monkeypatch.setitem(ht.REPORTED_KQ, ht.b_report_key("leaf", 3, "ud"),
                        ht.KqReport(b.kq.value * 8, (192,), "eight times the estimate"))
    b2 = C.b_row("leaf", 3, p)
    assert b2.queries[0] > 192 and b2.margin >= 0 and b2.kq.estimated


def test_dkt26_rows_read_reports(monkeypatch):
    rs = {r.name: r for r in K.rows()}
    r = rs["B leaf + node, unique decoding, 1/8"]
    assert r.kq.estimated and r.certified
    for kind in ("leaf", "node"):
        monkeypatch.setitem(ht.REPORTED_KQ, ht.b_report_key(kind, 3, "ud"), ht.KqReport(r.extra_kq, (192,), "T-1"))
    r2 = {x.name: x for x in K.rows()}["B leaf + node, unique decoding, 1/8"]
    assert r2.kq.provenance == ht.KQ_REPORTED and r2.kq.guard == 0 and r2.certified
    # only one kind reported: the row's k_q stays estimated (the guard stays on)
    monkeypatch.delitem(ht.REPORTED_KQ, ht.b_report_key("node", 3, "ud"))
    r3 = {x.name: x for x in K.rows()}["B leaf + node, unique decoding, 1/8"]
    assert r3.kq.estimated
    # a report above the estimate re-solves dkt26's row too
    monkeypatch.setitem(ht.REPORTED_KQ, ht.b_report_key("leaf", 3, "ud"),
                        ht.KqReport(r.extra_kq * 8, (192,), "eight times"))
    r4 = {x.name: x for x in K.rows()}["B leaf + node, unique decoding, 1/8"]
    assert r4.queries > 192 and r4.meets


# --- R10-9: the stream term at the shortest stream --------------------------------------------------------------------


def test_stream_term_at_the_shortest_stream():
    cert = C.certify(C.PROFILES[1])
    for q in (cert.a_qrom, cert.b_qrom):
        assert q.stream_bytes_used == 32
        assert -106.0 < q.stream_term_log2 < -104.0  # N 2 sqrt(k_q / 2^256): about 2^-105 (the referee's figure)
        assert q.meets
    assert cert.b_counts.stream_bytes > 32  # the longest stream, the revision 10 reading, is still recorded


# --- Lemma TE (draft): the comparison figure -----------------------------------------------------------------------


def test_tree_extraction_hash_level_draft():
    """docs/lemma-tree-extraction.md, Corollary TE-2: one table for the whole tree gives c'_max (t + K)^2 / 2^256 with
    K = sum of the tree's k_q (at most N k_q,max = 20,000 x 74,940 < 2^30.5); the classical level is the per-proof
    one, 121.89, against the per-proof sum's 114.74 that the calculator keeps until the lemma is refereed."""
    lvl = ht.tree_extraction_level(2_401, 20_000 * 74_940, 256)
    assert round(lvl, 2) == 121.89
    assert round(ht.classical_level(2_401, 40_416, 20_000, 256), 2) == 114.74
