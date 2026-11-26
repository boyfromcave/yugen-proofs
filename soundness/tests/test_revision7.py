"""Revision 7: the security category as an input (category.py; CHANGELOG revision 7).

Sources: NIST, Submission Requirements and Evaluation Criteria for the Post-Quantum Cryptography Standardization
Process (December 2016), Section 4.A.5, pages 16 to 18 (the five requirements and the gate-count table); the bounds
of revision 6 (book Theorems 25.2.1, 31.2.1; BCIKS20 unique decoding; Sharp-Grubbs ePrint 2026/2615 Theorem 6.6).
The category conventions and rows are Original (the Ycash developers, 2026)."""

import dataclasses
import math

import pytest

from yugen_soundness import category as C, cli, current as cu, revision5 as r5, revision6 as r6, spbcs
from yugen_soundness.targets import CAT1, CAT3

# Revision 9: these tests pin the revision 7 rows, which are computed at the book need: they run under the
# NON-DEFAULT convention (t >= k_q) as a record. The default (every t) is pinned in test_revision9.py.
P7 = {c: dataclasses.replace(p, convention=C.T_GE_KQ) for c, p in C.PROFILES.items()}
M1_7 = dataclasses.replace(C.M1, convention=C.T_GE_KQ)
CERTS = {c: C.certify(P7[c]) for c in (1, 3, 5)}


# --- the derivation from the NIST text ----------------------------------------------------------------------


@pytest.mark.parametrize("cat,base", [(1, CAT1), (3, CAT3)])
def test_derived_targets_equal_the_revision6_targets(cat, base):
    t = C.derive_target(cat)
    for f in ("classical_chain", "quantum_chain", "attack_bits", "digest_attack", "digest_proven"):
        assert getattr(t, f) == getattr(base, f)


def test_category5_and_the_collision_categories():
    t5 = C.derive_target(5)
    assert (t5.classical_chain, t5.quantum_chain, t5.attack_bits, t5.digest_attack, t5.digest_proven) == (256, 128, 256, 512, 520)
    assert C.kappa_classical(2) == C.kappa_classical(1) and C.kappa_classical(4) == C.kappa_classical(3)


def test_gate_figures_of_the_call_for_proposals():
    # page 18: 2^143, 2^146, 2^207, 2^210, 2^272 classical gates; 2^170, 2^233, 2^298 / MAXDEPTH quantum
    assert [C.gates_per_evaluation_log2(c) for c in range(1, 6)] == [15, 18, 15, 18, 16]
    assert [C.grover_overhead_log2(c) for c in (1, 3, 5)] == [42, 41, 42]
    assert C.grover_overhead_log2(2) is None and C.grover_overhead_log2(4) is None
    assert C.SHA3_512_CLASSICAL_GATES_LOG2 > C.NIST[5].classical_gates_log2  # the 512-bit digest rule's anchor


@pytest.mark.parametrize("cat,need", [(1, 152.52), (3, 216.52), (5, 280.52)])
def test_round_need_closed_form_and_tree_target_agree(cat, need):
    from yugen_soundness.compose import FsParams
    closed = C.round_need(cat, 87 + C.OTHER_ROUNDS)
    tt = C.tree_target_for(cat).need_bits(87, FsParams(digest_bits=P7[cat].digest_bits))
    assert closed == pytest.approx(tt, abs=1e-9)
    assert round(closed, 2) == need


def test_collision_categories_give_the_same_rows():
    for lo, hi in ((1, 2), (3, 4)):
        a, b = C.a_rows(P7[lo]), C.a_rows(P7[hi])
        assert [r.queries for r in a] == [r.queries for r in b]
        assert [r.queries for r in C.b_rows(P7[lo])] == [r.queries for r in C.b_rows(P7[hi])]


# --- category 1 reproduces revisions 5 and 6 -------------------------------------------------------------


def _row(cert, system, label, stack, rate):
    rows = cert.a if system == "A" else cert.b
    return next(r for r in rows if r.label.startswith(label) and r.stack == stack and r.rate == rate)


def test_category1_rows_reproduce_revision6():
    c = CERTS[1]
    assert _row(c, "A", "row 6 (standalone masked), mode 0", 22, 2).queries == tuple(r5.ZK_QUERIES)
    assert list(_row(c, "A", "row 8 (masked in a tree), mode 0", 22, 2).queries) == r5.wi_solve(r5.ROW8, 2)
    assert list(_row(c, "A", "row 8 (masked in a tree), mode 0", 22, 1).queries) == r5.wi_solve(r5.ROW8, 1)
    for m in C.A_NODE_STACKS:
        for rate in C.A_NODE_RATES:
            assert list(_row(c, "A", "row 9", m, rate).queries) == r5.minimal_counts(r5.ROW9, m, rate)
    assert [r.queries[0] for r in c.b if r.kind == "leaf"] == [184, 168]
    assert c.b_qrom.bits == pytest.approx(r6.certify().b.bits, abs=1e-9)
    assert c.b_counts.k_q == r6.b_counts().k_q
    assert c.b_zk.pool == pytest.approx(spbcs.eps_zk(r6.b_counts(), 64.0, 20.0).total_log2, abs=1e-9)
    assert c.a_zk.pool == pytest.approx(-87.83, abs=0.01)


def test_size_anchors_are_reproduced():
    p = P7[1]
    row6 = _row(CERTS[1], "A", "row 6 (standalone masked), mode 0", 22, 2)
    assert row6.size == pytest.approx(C.A_LEAF_ANCHOR[1], abs=0.5)
    assert abs(C.a_leaf_calibration()["row 8 error"]) < 0.02  # row 8's measured 692,504 B within 2 %
    rate, q, salt, m = C.B_LEAF_ANCHOR
    assert C.b_leaf_opening(rate, q, 256, 256, salt, route_s=False) + C.b_leaf_calibration() == pytest.approx(m, abs=0.5)
    from yugen_soundness import whir
    assert whir.size_bytes(cu.a_config(r5.ROW9, 27, 1, 0))["total"] + C.a_node_calibration() == pytest.approx(C.A_NODE_ANCHOR)
    assert p.digest_bits == 256


# --- the category study's schedules, reproduced independently --------------------------------------------


def test_study_schedules_category3():
    c = CERTS[3]
    assert _row(c, "A", "row 6 (standalone masked), mode 0", 22, 2).queries == (321, 222, 219, 218)
    assert _row(c, "A", "row 9", 27, 1).queries == (522, 238, 238, 238, 238, 239, 246)
    assert _row(c, "A", "row 9", 27, 2).queries == (320, 227, 227, 227, 227, 227, 231)
    assert [r.queries[0] for r in c.b] == [261, 238, 261, 238]


def test_study_schedules_category5():
    c = CERTS[5]
    assert _row(c, "A", "row 6 (standalone masked), mode 0", 22, 2).queries == (415, 288, 283, 282)
    assert _row(c, "A", "row 9", 27, 1).queries == (676, 308, 308, 308, 308, 309, 319)
    assert [r.queries[0] for r in c.b] == [338, 308, 338, 308]


def test_candidates_are_never_certified():
    """Revision 9 (finding R8-8b): the candidates are the refereed m = 10 rows, not a search over m (which returned the
    withdrawn 102 / 77-query rows at 0.00 / 0.03 bits of margin, and m = 107, 53, 92 at larger fields)."""
    c1 = CERTS[1].b_candidates
    assert [r.queries[0] for r in c1] == [107, 107, 80, 80]
    assert all("Johnson m = 10" in r.label for r in c1)
    assert [r.label.split("(list ")[1].rstrip(")") for r in c1] == ["19", "19", "31", "31"]
    c3 = C.b_candidates(P7[3])  # m = 10's node rows (212.14 / 210.19 bits) miss category 3's need: listed, and say so
    assert [r.kind for r in c3 if "DOES NOT MEET" in r.status] == ["node", "node"]
    assert all(("DOES NOT MEET" in r.status) == (r.margin < 0) for r in c3)
    for r in c1 + c3 + CERTS[5].b_candidates:
        assert not r.certified and "DKT26" in r.status and "PREPRINT" in r.status and C.NON_DEFAULT in r.status


# --- every count is minimal ------------------------------------------------------------------------------


def _all_rows():
    for cat, cert in CERTS.items():
        for r in cert.a + cert.b:
            yield pytest.param(cat, r, id=f"cat{cat}-{r.system}-{r.label[:24]}-2^{r.stack}-1/{2 ** r.rate}")


@pytest.mark.parametrize("cat,row", list(_all_rows()))
def test_each_count_less_by_one_fails(cat, row):
    p = P7[cat]
    assert row.margin >= -1e-9 and row.status == C.NON_DEFAULT and not row.certified
    for i in range(len(row.queries)):
        q = list(row.queries)
        q[i] -= 1
        if row.system == "A" and row.kind == "leaf":
            assert not C.a_leaf_counts_meet(row, q, p)
        elif row.system == "A":
            assert not C.a_node_counts_meet(row, q, p)
        else:
            from yugen_soundness import johnson
            assert q[0] * johnson.query_bits(None, 2.0**-row.rate) < row.need


# --- refusals (hard failures) ------------------------------------------------------------------------------


def test_refuses_a_short_digest():
    with pytest.raises(C.DigestTooShort):
        C.certify(dataclasses.replace(P7[3], digest_bits=256))
    with pytest.raises(C.DigestTooShort):
        C.certify(dataclasses.replace(P7[5], digest_bits=384))


def test_refuses_a_digest_too_short_for_the_qrom_hash_term():
    # condition H alone would admit 384 bits at a hypothetical 'category 5 with a 384-bit attack rule'; Theorem 6.6 (2)
    # does not: the hash term at 48-byte digests is 118.30 < 128.
    c = CERTS[5]
    q = C.qrom(c.a_counts, c.a_e, P7[5], digest_bytes=48)
    assert q.hash == pytest.approx(118.30, abs=0.01)
    with pytest.raises(spbcs.ConditionQFailure):
        spbcs.require(q)
    assert C.qrom_min_digest_bits(c.a_counts, 5) == 416 and C.qrom_min_digest_bits(CERTS[3].a_counts, 3) == 320


def test_refuses_a_field_too_small():
    with pytest.raises(C.FieldTooSmall):
        C.certify(dataclasses.replace(P7[5], field_bits=256))
    C.certify(dataclasses.replace(P7[3], field_bits=384))  # a larger field is admitted


@pytest.mark.parametrize("h", ["BLAKE3", "SHA-256"])
def test_category1_tree_hashes_are_refused_at_category3(h):
    with pytest.raises(C.HashNotAdmissible):
        C.certify(dataclasses.replace(P7[3], tree_hash_b=h))
    with pytest.raises(C.HashNotAdmissible):
        C.certify(dataclasses.replace(P7[5], tree_hash_b="SHA-384"))


def test_refuses_leaf_salts_not_longer_than_the_digest():
    with pytest.raises(C.SaltNotCovered):
        C.certify(dataclasses.replace(P7[3], leaf_salt_bytes=48))


# --- field, QROM, zero knowledge -----------------------------------------------------------------------------


def test_minimum_fields():
    def fmin(cat, system):
        p = dataclasses.replace(P7[cat], field_bits=512)
        rows = C.a_rows(p) if system == "A" else C.b_rows(p)
        return max(r.field_min for r in rows)
    assert [fmin(c, "A") for c in (1, 3, 5)] == [185, 249, 313]
    assert [fmin(c, "B") for c in (1, 3, 5)] == [185, 249, 313]
    # the study's 305 for A is the leaf's figure; nodes of 2^30 at rate 1/4 need 313
    a5 = C.a_rows(dataclasses.replace(P7[5], field_bits=512))
    assert max(r.field_min for r in a5 if r.kind == "leaf") == 305


def test_qrom_margins():
    for cat, kq in ((1, 64), (3, 96), (5, 128)):
        c = CERTS[cat]
        assert c.a_qrom.bits >= kq and c.b_qrom.bits >= kq
        assert 3.2 < c.a_qrom.margin < 3.4


def test_zero_knowledge_rows():
    m1 = C.certify(M1_7)
    assert m1.a_zk.pool == pytest.approx(-170.0, abs=0.05) and m1.a_zk.covered
    assert CERTS[3].a_zk.pool == pytest.approx(-138.0, abs=0.05)
    assert CERTS[5].a_zk.pool == pytest.approx(-151.83, abs=0.01)


def test_size_limit_at_category5():
    c = CERTS[5]
    over = [r for r in c.a + c.b if r.size > C.PROOF_BYTES_MAX]
    assert any(r.system == "B" and r.kind == "leaf" for r in over)
    assert all(r.size <= C.PROOF_BYTES_MAX for r in CERTS[3].a + CERTS[3].b)


def test_cli_category_flag(capsys):
    cli.main(["--category", "3", "--convention", "t-ge-kq"])
    out = capsys.readouterr().out
    assert C.NON_DEFAULT.upper() in out
    assert "321, 222, 219, 218" in out and "| 3 | key search on AES192 |" in out
    cli.main(["--category", "3", "--digest-bits", "256", "--convention", "t-ge-kq"])
    assert "**Refused**" in capsys.readouterr().out


def test_salt_floors_from_a_zero_knowledge_target():
    # referee report security-category-referee.md 3.4 (R6): 83 / 91 B at 48-byte digests for 2^-96 / 2^-128
    k = CERTS[1].a_counts
    assert [C.leaf_salt_floor(k, 48, t) for t in (-64.0, -96.0, -128.0)] == [75, 83, 91]
    assert C.leaf_salt_floor(k, 64, -128.0) == 107
    assert C.proof_salt_floor(128.0, -128.0) == 70 and C.proof_salt_floor(96.0, -128.0) == 62


def test_largest_proof_by_category():
    big = {c: max(CERTS[c].a + CERTS[c].b, key=lambda r: r.size) for c in (1, 3, 5)}
    assert big[3].size <= C.PROOF_BYTES_MAX < big[5].size
    assert (big[5].system, big[5].kind, big[5].stack, big[5].rate) == ("A", "node", 30, 1)
