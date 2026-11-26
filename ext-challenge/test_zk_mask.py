"""Exact tests: which masks must be sampled in the challenge field
(docs/binius-extension-challenges.md section 6). L = GF(4), K = GF(16); every case enumerated.

The opening's mask fold is M^gamma = (1 - gamma) M + gamma w with gamma in K. M is over L.

Sources and provenance (REFERENCES.md). The mask fold is the Blueprint's form of the full-mask opening
of Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields", ePrint 2025/1015, Construction 4.1 (there: alpha f + f', no
excluded challenge). The principle that an extension-field query to a base-field randomized object
costs e base-field degrees of freedom is Published for evaluation queries: Haböck, Al Kindi, "A note on adding zero-knowledge to STARK", ePrint 2024/1037, Lemma 1. The failure for a fold challenge, rule Z and its tests are Original (the Ycash developers,
2026) as far as checked. The pad on coefficients 0..q: Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint
2026/391 (revision of 2026-11-16), Lemma 3.29.
"""

import unittest
from collections import Counter
from itertools import product

from gf import F4, F16, inv, mul

L, K = F4, F16
Y = K.basis[L.deg]  # K = L + Y L
N = 2  # message length of the toy oracle


def fold(M, w, g):
    return tuple(mul(1 ^ g, m) ^ mul(g, x) for m, x in zip(M, w))


def split(x):
    """x = a + Y b with a, b in L."""
    for a in L.elems:
        for b in L.elems:
            if a ^ mul(Y, b) == x:
                return a, b
    raise AssertionError


def views(M, masks, g):
    return Counter(fold(M, w, g) for w in masks)


MSGS = list(product(L.elems, repeat=N))
MASKS_L = list(product(L.elems, repeat=N))
MASKS_K = list(product(K.elems, repeat=N))


class FoldMask(unittest.TestCase):
    def test_control_base_field_mask_reveals_the_whole_oracle(self):
        # gamma outside L: the folded oracle determines M, for every M and every mask
        for g in K.elems:
            if g in L:
                continue
            g0, g1 = split(g)
            for M in MSGS:
                for w in MASKS_L:
                    v = fold(M, w, g)
                    # M^gamma = (M + g0 (M + w)) + Y g1 (M + w): read M + w off the Y-coordinate
                    rec = []
                    for x in v:
                        a, b = split(x)
                        mw = mul(inv(g1), b)
                        rec.append(a ^ mul(g0, mw))
                    self.assertEqual(tuple(rec), M)

    def test_control_base_field_mask_views_are_disjoint_across_messages(self):
        g = Y
        supports = [set(views(M, MASKS_L, g)) for M in MSGS]
        for i in range(len(supports)):
            for j in range(i):
                self.assertFalse(supports[i] & supports[j])  # statistical distance 1

    def test_base_field_mask_hides_only_when_gamma_falls_in_L(self):
        ok = [g for g in K.elems if g and len({frozenset(views(M, MASKS_L, g).items()) for M in MSGS}) == 1]
        self.assertEqual(set(ok), set(L.elems) - {0})  # probability (|L| - 1) / |K| over gamma

    def test_fix_extension_field_mask_is_perfect_for_every_nonzero_gamma(self):
        uniform = Counter({v: 1 for v in MASKS_K})
        for g in K.elems:
            if g == 0:
                continue
            for M in MSGS:
                self.assertEqual(views(M, MASKS_K, g), uniform)

    def test_fix_as_two_base_field_masks(self):
        # w = w1 + Y w2 with w1, w2 uniform over L^N is the uniform mask over K^N
        got = Counter(tuple(a ^ mul(Y, b) for a, b in zip(w1, w2)) for w1 in MASKS_L for w2 in MASKS_L)
        self.assertEqual(got, Counter({v: 1 for v in MASKS_K}))

    def test_opened_mask_symbol_is_determined(self):
        # Enc(w)[e] = gamma^-1 (Enc(M^gamma)[e] - (1 - gamma) Enc(M)[e]): symbol-wise, any linear code
        for g in K.elems:
            if g == 0:
                continue
            for m in L.elems:
                for w in K.elems:
                    v = mul(1 ^ g, m) ^ mul(g, w)
                    self.assertEqual(mul(inv(g), v ^ mul(1 ^ g, m)), w)


class OneTimePad(unittest.TestCase):
    def test_control_base_field_key_leaks_a_coordinate(self):
        for m in K.elems:
            cts = {m ^ k for k in L.elems}
            self.assertEqual({split(c)[1] for c in cts}, {split(m)[1]})  # the Y-coordinate of every ciphertext

    def test_fix_key_from_two_base_field_slots(self):
        for m in K.elems:
            cts = Counter(m ^ p ^ mul(Y, q) for p in L.elems for q in L.elems)
            self.assertEqual(cts, Counter({c: 1 for c in K.elems}))


class Blinding(unittest.TestCase):
    """A K-valued revealed combination alpha1 a1 + alpha2 a2 of two blinding values."""

    def test_base_field_blinds_are_uniform_iff_the_weights_are_L_independent(self):
        bad = 0
        for a1w in K.elems:
            for a2w in K.elems:
                img = Counter(mul(a1w, x) ^ mul(a2w, y) for x in L.elems for y in L.elems)
                uniform = len(img) == len(K.elems)
                indep = a1w != 0 and a2w != 0 and mul(a2w, inv(a1w)) not in L
                self.assertEqual(uniform, indep)
                bad += not uniform
        # failure probability over the weights: about 1/|L|, not 1/|K|
        self.assertEqual(bad, len(K.elems) + (len(K.elems) - 1) * len(L.elems))

    def test_fix_extension_blind_needs_one_nonzero_weight(self):
        for a1w in K.elems:
            for a2w in K.elems:
                img = Counter(mul(a1w, x) ^ mul(a2w, y) for x in K.elems for y in K.elems)
                self.assertEqual(len(img) == len(K.elems), bool(a1w or a2w))


class Pad(unittest.TestCase):
    """The pad of a base-field oracle stays in the base field: opened symbols are L-valued."""

    def test_pad_on_the_low_coefficient_hides_an_opened_symbol(self):
        # codeword of (pad, secret): f(x) = pad + secret x on D = L; one opened position
        for e in L.elems:
            for secret in L.elems:
                self.assertEqual(Counter(pad ^ mul(secret, e) for pad in L.elems), Counter({c: 1 for c in L.elems}))

    def test_control_pad_on_the_high_coefficient_fails_at_zero(self):
        self.assertEqual({secret ^ mul(pad, 0) for pad in L.elems for secret in [L.elems[1]]}, {L.elems[1]})


if __name__ == "__main__":
    unittest.main()
