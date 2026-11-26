"""Revision 10: the hash term of Sharp-Grubbs Theorem 6.6 (2) (R9-1), the computed status (R9-2), k_q with provenance
and its guard (R9-4), padded group slots in system B's k_q (Lemma D referee m-1), the summaries' wording (R9-3), the
refusal's need (R9-5), the Lean-backed count (L-2) and Compose.lean as a file (L-6).

Source: C. Sharp, P. Grubbs, ePrint 2026/2615 [SG26], Theorem 6.6 (2) (page 58), Definition I.1 (page 130), Section
I.1 (page 131), read from the rendered pages. Findings: docs/rev9-and-lean-referee.md; docs/lemma-d-referee.md.
"""

import dataclasses
import math
import pathlib

import pytest

from yugen_soundness import category as C
from yugen_soundness import cli, dkt26 as K, hashterm as ht

P1 = C.PROFILES[1]
CERT = C.certify(P1)
ROOT = pathlib.Path(__file__).parents[2]


# --- R9-1: the hash term ---------------------------------------------------------------------------------------------


def _closed_classical(cp, proofs, bits=256):
    """k_q << 2^kappa: N c' 2^(2 kappa) / 2^b = 2^-1  =>  kappa = (b - 1 - log2(N c')) / 2."""
    return (bits - 1 - math.log2(proofs * cp)) / 2


def test_hash_term_of_system_b_row_192():
    r = next(x for x in CERT.b if x.kind == "leaf" and x.rate == 3)
    h = r.hash
    assert (r.c_prime, r.kq.value) == (2_401, 40_416)  # c' = 2 N_msg + 1 = 2 x 1,200 + 1 (m = 2, n_J = 0)
    assert h.classical_tree == pytest.approx(_closed_classical(2_401, 20_000), abs=1e-6)
    assert round(h.classical_tree, 2) == 114.74 and round(h.classical_proof, 2) == 121.89
    assert round(h.quantum_tree, 2) == 75.63 and round(h.quantum_proof, 2) == 80.40
    assert h.digest_needed == 288  # 2 x 128 + 1 + log2(20,000 x 2,401) = 282.5 -> 36 bytes
    assert ht.digest_for_classical(128.0, 2_401, 40_416, 20_000) == 288


def test_hash_term_is_below_kappa_c_at_every_row_and_quantum_meets():
    for r in CERT.a + CERT.b:
        h = r.hash
        assert 114.7 < h.classical_tree < 114.9 and h.classical_margin < -13.0  # proven classical: 13.2 to 13.3 short
        assert h.classical_proof < 128.0  # even one proof (N = 1) is short: c' (t + k_q)^2 / 2^256 at t = 2^128
        assert h.quantum_tree > 75.6 and h.quantum_margin > 11.0
        assert h.digest_needed == 288


def test_the_book_figures_are_the_superseded_ones():
    """126.6 = (255 - log2 3.5) / 2 (the book's 3.5 t^2 / 2^lambda, counted once); 264 = its proven-rule digest."""
    assert (255 - math.log2(3.5)) / 2 == pytest.approx(126.59, abs=0.01)
    assert C.derive_target(1).digest_proven == 264
    assert ht.digest_for_classical(128.0, 2_401, 0, 20_000) == 288


def test_classical_level_checks_both_end_points():
    # with a huge k_q the t = 1 end binds: N c' (1 + k_q)^2 / 2^b <= 2^-(kappa + 1)
    lvl = ht.classical_level(2, 2**100, 1, 256)
    assert lvl == pytest.approx(256 - 1 - 200 - 1, abs=1e-3)


def test_hash_basis_proven_certifies_nothing_at_256_bits():
    p = dataclasses.replace(P1, hash_basis=ht.HASH_PROVEN)
    c = C.certify(p)
    assert not any(r.certified for r in c.a + c.b)
    assert all("classical hash part (proven)" in r.status for r in c.b)
    # at a 288-bit digest the proven classical hash part reaches 128 bits
    r = c.b[0]
    r288 = dataclasses.replace(r, digest_bits=288)
    assert r288.hash.classical_tree >= 128.0


def test_every_row_prints_the_hash_term():
    out = "\n".join(cli.rev9_tables())
    for line in out.splitlines():
        if (line.startswith("| A | row") or line.startswith("| B | ")) and " (E) | " in line:
            assert " / 114." in line and " / 75." in line
    assert "### The hash term of SG26 Theorem 6.6 (2) (revision 10, finding R9-1)" in out
    for r in K.rows():
        assert r.hash.digest_needed == 288 and 114.7 < r.hash.classical_tree < 114.8


# --- R9-2: "certified" is computed --------------------------------------------------------------------------------------


def test_dkt26_fixed_need_is_never_certified():
    r = K.row("x", "ud", 3, None, need_bits=152.52)
    assert r.queries == 184 and not r.certified and r.status == K.FIXED_NEED
    assert "certified (unique" not in r.status


def test_b_row_with_old_count_does_not_meet():
    r = C.b_row("leaf", 3, P1, queries=184)
    assert r.margin == pytest.approx(-5.80, abs=0.01) and not r.certified
    assert r.status == "DOES NOT MEET the need"
    line = C.rows_table([r], "t")[-1]
    assert "certified" not in line and "DOES NOT MEET" in line
    with pytest.raises(TypeError):
        C.b_row("leaf", 3, P1, queries=192, status=C.CERTIFIED)  # no label can be passed in


def test_book_rows_and_bare_rows_are_not_certified():
    book = C._a_node_at(27, 1, P1, C.tree_target_for(1))
    assert not book.certified and book.need_source == C.NEED_UNASSESSED
    c = book.extra["config"]
    stamped = C._stamp(book, P1, C.NEED_BOOK)
    assert not stamped.certified and "need at the row's own k_q" in stamped.status
    leaf = C._a_leaf_at("row 6 (standalone masked)", C.cu.ROW6, 0, 2, P1, C.tree_target_for(1))
    assert not leaf.certified and c is not None


def test_certified_is_exactly_the_checks():
    for r in CERT.a + CERT.b + CERT.b_candidates:
        assert r.certified == all(r.checks.values())
        assert r.certified == (r.status == C.CERTIFIED)
    assert not any(r.certified for r in CERT.b_candidates)


# --- R9-4: k_q with provenance, the guard ---------------------------------------------------------------------------------


def test_guard_value():
    assert ht.kq_guard_bits(18_082) == pytest.approx(math.log2(1.1), abs=1e-4)
    assert ht.KqInput(100, ht.KQ_REPORTED).guard == 0.0
    with pytest.raises(ValueError):
        ht.KqInput(100, "guessed")


LOSE = {  # (label prefix, stack, rate): margin (bits), all below the guard 0.1375 on an estimated k_q
    ("row 6 (standalone masked), mode 1", 20, 2): 0.0289, ("row 8 (masked in a tree), mode 0", 22, 2): 0.1058,
    ("row 8 (masked in a tree), mode 0", 22, 1): 0.0186, ("row 8 (masked in a tree), mode 1", 22, 1): 0.0186,
    ("row 9", 24, 1): 0.0011, ("row 9", 26, 1): 0.0989, ("row 9", 27, 1): 0.0979, ("row 9", 28, 1): 0.0456,
    ("row 9", 29, 1): 0.0575, ("row 9", 30, 1): 0.0043, ("row 9", 24, 2): 0.0571, ("row 9", 25, 2): 0.0016,
    ("row 9", 28, 2): 0.1109, ("row 9", 30, 2): 0.0033,
}


def test_rows_that_lose_certified_under_the_guard():
    """Revision 10's list, unchanged by revision 10.1 except A row 7 at 1/4, which the combined guard (R10-7) adds."""
    lost = {(r.label.split(" (trace")[0] if r.label.startswith("row 8") else r.label, r.stack, r.rate): r
            for r in CERT.a if not r.certified}
    got = {}
    for (lab, st, rt), r in lost.items():
        key = next(k for k in LOSE if lab.startswith(k[0]) and (st, rt) == k[1:])
        got[key] = round(r.margin, 4)
        assert r.kq.estimated and 0 <= r.margin < r.kq.guard and "until task T-1" in r.status
    assert got == LOSE
    assert sum(r.certified for r in CERT.a) == 6 and all(r.certified for r in CERT.b)
    r7 = {rt: C.a_plain_leaf(22, rt, P1) for rt in (1, 2)}
    assert not r7[1].certified and not r7[2].certified  # revision 10.1: row 7 at 1/4 under the combined guard
    assert round(r7[2].margin, 3) == 0.192 and round(r7[2].kq.guard, 3) == 0.222


def test_a_reported_k_q_replaces_the_estimate(monkeypatch):
    r = next(x for x in CERT.a if x.label.startswith("row 9") and (x.stack, x.rate) == (24, 1))
    key = ht.a_report_key(r.label, r.stack, r.rate)
    monkeypatch.setitem(ht.REPORTED_KQ, key, ht.KqReport(r.kq.value, r.queries, "test vector"))
    r2 = C.a_node(24, 1, P1)
    assert r2.kq.provenance == ht.KQ_REPORTED and r2.kq.guard == 0 and r2.certified and r2.queries == r.queries
    # revision 10.1 (R10-8 (ii)): a report ABOVE the estimate re-solves the row to new counts; nothing aborts
    monkeypatch.setitem(ht.REPORTED_KQ, key, ht.KqReport(r.kq.value + 1_000, r.queries, "test vector, larger"))
    r3 = C.a_node(24, 1, P1)
    assert r3.need > r.need and r3.margin >= 0 and sum(r3.queries) > sum(r.queries)
    assert r3.kq.estimated and "reported excess" in r3.kq.source and "re-solved at the T-1 report" in r3.note


# --- Lemma D referee m-1: padded group slots ------------------------------------------------------------------------


def test_b_q_iop_counts_padded_slots():
    assert C.padded(111, 5) == 115 and C.padded(82, 4) == 84 and C.padded(192, 2) == 192 and C.padded(235, 5) == 235
    assert C.b_counts(111, 3, P1, "dkt").q_iop == 115 * 6
    assert C.b_counts(82, 4, P1, "dkt").q_iop == 84 * 6
    assert C.b_counts(192, 3, P1).q_iop == 192 * 6
    assert C.b_unit("ud", 4) == (6, "assumed: no grouping recorded")


def test_no_count_moves_with_padding():
    rs = {r.name: r for r in K.rows()}
    assert [rs[n].queries for n in ("B leaf + node, unique decoding, 1/8", "B leaf + node, Johnson m = 10, 1/8",
                                     "B leaf + node, Johnson m = 10, 1/16", "B node, unique decoding, 1/4",
                                     "B node, Johnson m = 10, 1/4")] == [192, 111, 82, 235, 171]
    assert C.b_row("node", 1, P1).queries == (385,) and C.b_row("leaf", 4, P1).queries == (174,)


# --- R9-3, R9-5, L-2, L-6 -----------------------------------------------------------------------------------------------------


def test_non_default_summaries_do_not_say_certified():
    out = C.tables((1,), C.T_GE_KQ)
    text = "\n".join(out)
    for phrase in ("every certified shape", "Largest certified proof", "certified rows' weakest round"):
        assert phrase not in text
    assert text.count(C.NON_DEFAULT.upper()) >= 5


def test_field_refusal_names_its_need():
    p = dataclasses.replace(C.PROFILES[3], field_bits=128)
    with pytest.raises(C.FieldTooSmall) as e:
        C.a_leaf("row 6 (standalone masked)", C.cu.ROW6, 0, 2, p)
    assert "book need (t >= k_q), solved first" in str(e.value)


def test_lean_backed_count_beside_the_exact_one():
    rs = {r.name: r for r in K.rows()}
    for name, exact, lean in (("B leaf + node, Johnson m = 10, 1/8", 212.14, 212.11),
                              ("B leaf + node, Johnson m = 10, 1/16", 210.19, 210.18)):
        w = rs[name].weakest[1]
        assert (round(w.bits, 2), round(w.lean_bits, 2)) == (exact, lean)
    text = "\n".join(K.tables())
    assert "Lean-backed" in text and "212.11" in text and "212.14" in text


def test_compose_lean_is_the_documented_text():
    doc = (ROOT / "docs" / "arklib-lean-check.md").read_text()
    start = doc.index("### 3.2 Compositions the analysis uses (`Compose.lean`)")
    b = doc.index("```lean\n", start) + len("```lean\n")
    body = doc[b:doc.index("```\n", b)]
    f = (ROOT / "lean" / "Compose.lean").read_text()
    head, sep, rest = f.partition("import ")
    assert "6aa8b6fe8059cecc0e53607ca811a933a0f8e0b7" in head and "leanprover/lean4:v4.35.0" in head
    assert sep + rest == body
