"""The round census of system A (finding M-3 of docs/theorem-s-referee.md; docs/round-census-a.md).

The census walks the built verifier message by message (census.leaf_messages) and must give the counts the built
verifier reports (census/a-round-census.json, from yugen-proof-a bench/results/kq-report-20261119.txt). It is
printed beside the estimate OTHER_ROUNDS and changes no certified count."""

from yugen_soundness import census as K
from yugen_soundness.shipping import OTHER_ROUNDS


def _measured(row, mode, stack, rate):
    return next(m["j_v"] for m in K.load()["measured"]
                if (m["row"], m["mode"], m["stack"], m["rate"]) == (row, mode, stack, rate))


def test_row8_leaf_census_is_the_built_verifiers_count():
    s = K.summary(K.wallet_leaf(masked=True))
    assert s["messages"] == 445 == _measured("row 8 (masked in a tree)", 0, 22, 2)
    assert (s["opening"], s["outside_opening"]) == (33, 412)
    assert s["groups"] == {"ood": 1, "bus-fingerprint": 1, "bus-gkr": 123, "bytecode": 4, "table": 19,
                           "public+keccak": 1, "keccak": 259, "gadget": 3, "ring-batch": 1, "opening": 33}
    assert s["challenges"] == 573


def test_row7_plain_leaf_census_is_the_built_verifiers_count():
    """The same program parameters, no masks, plain WHIR: a second, independent check of the parameters."""
    s = K.summary(K.wallet_leaf(masked=False))
    assert s["messages"] == 411 == _measured("row 7 (plain leaf)", 0, 22, 2)
    assert (s["opening"], s["outside_opening"]) == (29, 382)


def test_every_round_outside_the_opening_has_an_error_and_a_source():
    ms = [m for m in K.wallet_leaf(masked=True) if m.group != "opening"]
    assert all(m.sources for m in ms)
    bits = [m.error_bits(256) for m in ms]
    assert min(bits) == 235.0  # the bus fingerprint, 2^21 / 2^256
    assert sorted(bits)[1] >= 246.9  # next: the ring switch with the stacked lambda, 513 / 2^256
    assert K.summary(ms)["sum_outside_log2"] < -234.9


def test_census_beside_the_estimate_and_the_estimate_unchanged():
    assert OTHER_ROUNDS == 512  # certified counts are not moved by the census
    rows = {(cr.row.label, cr.row.stack, cr.row.rate): cr for cr in K.rows()}
    r8 = rows[("row 8 (masked in a tree), mode 0", 22, 2)]
    assert (r8.est_messages, r8.messages, r8.provenance) == (599, 445, "M")
    assert r8.kq_est - r8.kq == 4 * (599 - 445)
    assert rows[("row 8 (masked in a tree), mode 1", 21, 2)].messages == 409
    node27 = rows[("row 9 (node)", 27, 1)]
    assert (node27.messages, node27.provenance) == (592, "M") and node27.messages > node27.est_messages


def test_rows_with_a_measured_or_derived_census_meet_their_need():
    out = K.rows()
    for cr in out:
        if cr.provenance in ("M", "D"):
            assert cr.messages is not None and cr.margin >= 0, cr.row.label
    assert all(cr.margin is None or cr.margin >= 0 for cr in out)


def test_unmeasured_row9_counts_are_withdrawn():
    """Referee M-A2: the two measured nodes are different programs; no extrapolated count is given, and the shapes
    above 2^27 are marked refused by the build."""
    out = [cr for cr in K.rows() if cr.messages is None]
    assert {(cr.row.stack, cr.provenance) for cr in out} == {(24, "E"), (26, "E"), (28, "R"), (29, "R"), (30, "R")}
    assert all(cr.row.label.startswith("row 9") and K.restore(cr) is None for cr in out)
    text = "\n".join(K.tables())
    assert "727" not in text and text.count("not measured — refused by the build above 2^27 |") == 6
