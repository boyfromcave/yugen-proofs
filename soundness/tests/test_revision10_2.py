"""Revision 10.2: the tree figures after docs/tree-extraction-referee.md (Theorem TE', Proposition TE-Q', Lemma QC).

The classical tree hash level is that of Theorem TE' (121.89 at category 1), labelled "under C2, K-A, K-B, T-1", with the
per-proof union (114.74) beside it; the QROM figures claimed stay the per-proof union (69.58 / 70.45), the one-table
form (76.72 / 77.60, hash 80.40) is printed beside them; the Lemma QC term is printed in bits; the footer lists every
condition. NO QUERY COUNT AND NO STATUS CHANGES: every row of every type, category, convention and hash basis is
pinned against tests/data/query_counts_rev10_1.json, generated from revision 10.1 (commit e6a2d23) before any
revision 10.2 change.

Sources: docs/lemma-tree-extraction.md revision 2 (sections 6, 7, 9, 9a); C. Sharp, P. Grubbs, ePrint 2026/2615
[SG26], Theorem I.16 (page 142); A. Chiesa, P. Manohar, N. Spooner, ePrint 2019/834 [CMS19], Lemma 3.2 (page 17).
"""

import dataclasses
import itertools
import json
from pathlib import Path

import pytest

from yugen_soundness import category as C
from yugen_soundness import cli, dkt26 as K, hashterm as ht

DATA = Path(__file__).parent / "data" / "query_counts_rev10_1.json"


def _snapshot():
    out = {}
    for cat, conv, basis in itertools.product((1, 2, 3, 4, 5), (C.EVERY_T, C.T_GE_KQ), ht.HASH_BASES):
        p = dataclasses.replace(C.PROFILES[cat], convention=conv, hash_basis=basis)
        rows = []
        try:
            cert = C.certify(p)
            rows += cert.a + cert.b + cert.b_candidates
        except (C.CategoryRefusal, C.spbcs.ConditionQFailure):
            rows += C.a_rows(p) + C.b_rows(p)
        if cat == 1:
            rows += [C.a_plain_leaf(22, r, p) for r in (2, 1)]
        rows += K.rows(None, p.field_bits, built=cat == 1, convention=conv, category=cat, hash_basis=basis)
        ent = []
        for r in rows:
            q = r.queries if isinstance(r.queries, tuple) else (r.queries,)
            ent.append([type(r).__name__, getattr(r, "system", "B"), getattr(r, "kind", ""),
                        getattr(r, "label", None) or f"{r.name}|{r.route}|{r.m}", getattr(r, "stack", 0), r.rate,
                        list(q), r.status])
        out[f"{cat}|{conv}|{basis}"] = ent
    return out


def test_no_query_count_and_no_status_changes():
    """Every row's query counts and status are those of revision 10.1 (the snapshot), at every flag combination."""
    pinned = json.loads(DATA.read_text())
    now = json.loads(json.dumps(_snapshot()))
    assert set(now) == set(pinned)
    for key in pinned:
        assert len(now[key]) == len(pinned[key]), key
        for a, b in zip(now[key], pinned[key]):
            assert a == b, (key, a, b)


def _cert1():
    return C.certify(C.PROFILES[1])


def test_classical_tree_level_is_te_prime_with_the_union_beside_it():
    cert = _cert1()
    for rows, want_cp in ((cert.a, 2_397), (cert.b, 2_401)):
        hs = [r.hash for r in rows if r.hash is not None]
        assert max(h.c_prime for h in hs) == want_cp
        assert round(C.tree_te_level(hs), 2) == 121.89
        assert round(min(h.classical_tree for h in hs), 2) == 114.74
    # B at the largest k_q the calculator prints (74,940): the same level (K is negligible against 2^121)
    assert round(ht.tree_extraction_level(2_401, 20_000 * 74_940, 256), 2) == 121.89
    text = "\n".join(C.hash_term_summary(cert))
    assert "Classical, tree, Theorem TE' (under C2, K-A, K-B, T-1)" in text
    assert "| 121.89 | 114.74 | 128 | 6.11 / 13.26 | 272 / 288 |" in text


def test_proven_basis_check_does_not_depend_on_te_or_union():
    """The proven-basis check keeps the union (the lower figure); at every profile's digest both figures are below
    kappa_C, so no row's status would differ under Theorem TE'."""
    for cat in (1, 2, 3, 4, 5):
        p = C.PROFILES[cat]
        for r in C.a_rows(p) + C.b_rows(p):
            h = r.hash
            if h is None:
                continue
            assert h.classical_tree <= h.classical_tree_te
            assert (h.classical_margin >= 0) == (h.classical_margin_te >= 0), (cat, r.label)


def test_quantum_figures_claimed_and_one_table():
    cert = _cert1()
    one = {s: dataclasses.replace(q, proofs=1) for s, q in (("A", cert.a_qrom), ("B", cert.b_qrom))}
    assert (round(cert.a_qrom.bits, 2), round(cert.b_qrom.bits, 2)) == (69.58, 70.45)
    assert (round(one["A"].iop, 2), round(one["B"].iop, 2)) == (76.72, 77.60)
    assert round(one["A"].hash, 2) == round(one["B"].hash, 2) == 80.40
    text = "\n".join(C.tree_qrom_summary(cert))
    assert "| A | 157.03 | **69.58 / 75.63 / 69.58** | 76.72 / 80.40 / 76.72 | 64 |" in text
    assert "| B | 158.78 | **70.45 / 75.63 / 70.45** | 77.60 / 80.40 / 77.60 | 64 |" in text
    assert "The project claims the per-proof union, the lower figure." in text
    assert text.count(ht.TREE_CONDITIONS) >= 3


def test_lemma_qc_term_is_negligible_in_bits():
    cert = _cert1()
    ka = 20_000 * max(r.hash.k_q for r in cert.a if r.hash)
    kb = 20_000 * max(r.hash.k_q for r in cert.b if r.hash)
    assert round(ht.lemma_qc_log2(ka, 256), 2) == -222.91
    assert round(ht.lemma_qc_log2(kb, 256), 2) == -223.09
    assert round(ht.lemma_qc_log2(20_000 * 74_940, 256), 2) == -222.20
    # even at k_q = 2^17 a proof, above every k_q the calculator prints, the term stays below 2^-220
    assert ht.lemma_qc_log2(20_000 * 2**17, 256) < -220
    # and below the continuation's hash term at t = 2^64 by more than 70 bits (docs/lemma-tree-extraction.md 9a)
    cont_hash = __import__("math").log2(ka * 2_397 * (2**64 + ka)) - 256
    assert ht.lemma_qc_log2(ka, 256) < cont_hash - 70


FOOTER_TERMS = ("C2", "NOT dischargeable", "K-A and K-B, OWED", "T-1, OWED from the builders", "H-DS",
                "Protocol 6.5", "MA-1", "MA-2'", "Theorem I.16 (1), (2): a PREPRINT", "Theorem TE'",
                "Lemma QC", "UNREFEREED", "Theorem D", "refereed, pass with conditions", "DKT26", "121.89", "114.74",
                "69.58 A / 70.45 B", "76.72 / 77.60, hash part 80.40", ht.TREE_CONDITIONS)


def test_footer_lists_every_condition():
    text = "\n".join(C.PROVEN_FOOTER)
    for term in FOOTER_TERMS:
        assert term in text, term
    assert "none is an unconditional theorem" in text


@pytest.mark.parametrize("argv", [[], ["--rev7"], ["--rev8"], ["--category", "1"], ["--category", "3"],
                                  ["--hash-basis", "proven"], ["--rev8", "--convention", "t-ge-kq"]])
def test_every_cli_table_set_ends_with_the_footer(argv, capsys):
    cli.main(argv)
    out = capsys.readouterr().out
    assert out.rstrip("\n").endswith(C.PROVEN_FOOTER[-1])
    for term in FOOTER_TERMS:
        assert term in out, (argv, term)


def test_no_tree_figure_is_called_proven_qrom():
    out = "\n".join(C.tables((1,)))
    assert "meets (proven)" not in out
    assert "meets (tree derived under C2, K-A, K-B, T-1)" in out
