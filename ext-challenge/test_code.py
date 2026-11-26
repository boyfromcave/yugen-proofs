"""Exact tests of a base-field Reed-Solomon word under extension-field challenges
(docs/binius-extension-challenges.md section 4).

Code: K = GF(16), evaluation domain D = L = GF(4) (n = 4), polynomials of degree <= 1 (rate 1/2).
Unique decoding radius (1 - rho) / 2 = 1/4: one error. Every word, every challenge.
"""

import unittest
from itertools import product

from gf import F4, F16, mul

L, K = F4, F16
D = L.elems
N = len(D)
CODE = {tuple(a ^ mul(b, x) for x in D): (a, b) for a in K.elems for b in K.elems}  # RS[K, D, 1]
CODE_L = {c for c, (a, b) in CODE.items() if a in L and b in L}  # RS[L, D, 1]


def dist(u, v):
    return sum(1 for a, b in zip(u, v) if a != b)


NEAR = {}  # every word of K^4 within distance 1 of the code -> its codeword
for c in CODE:
    NEAR[c] = c
    for i in range(N):
        for a in K.elems:
            if a != c[i]:
                NEAR[c[:i] + (a,) + c[i + 1:]] = c


class Descent(unittest.TestCase):
    def test_a_base_field_word_decodes_to_a_base_field_codeword(self):
        # within the unique decoding radius the K-codeword nearest an L-valued word is L-valued
        seen = 0
        for u in product(L.elems, repeat=N):
            c = NEAR.get(u)
            if c is not None:
                seen += 1
                self.assertIn(c, CODE_L)
        self.assertGreater(seen, len(CODE_L))

    def test_any_agreement_of_dimension_many_points_descends(self):
        # stronger than needed: agreement on k + 1 = 2 points already forces base-field coefficients
        for u in product(L.elems, repeat=N):
            for c in CODE:
                if N - dist(u, c) >= 2:
                    self.assertIn(c, CODE_L)

    def test_control_below_dimension_many_points_it_need_not(self):
        hit = any(N - dist(u, c) == 1 and c not in CODE_L for u in product(L.elems, repeat=N) for c in CODE)
        self.assertTrue(hit)


class LineOverTheExtension(unittest.TestCase):
    """BCIKS20 Theorem 4.1 with Remark 1.2 on this instance: u0, u1 over L, z over K."""

    @classmethod
    def setUpClass(cls):
        cls.max_bad_K = 0  # largest |S| over pairs without correlated agreement
        cls.max_bad_L = 0  # largest |S n L| over the same pairs
        cls.violations = 0
        cls.descent_fail = 0
        words = list(product(L.elems, repeat=N))
        for u0 in words:
            for u1 in words:
                S = [z for z in K.elems if tuple(a ^ mul(z, b) for a, b in zip(u0, u1)) in NEAR]
                # correlated agreement: v0, v1 in the code agreeing with u0, u1 on a common set of >= 3 points
                corr = False
                c0, c1 = NEAR.get(u0), NEAR.get(u1)
                if c0 is not None and c1 is not None:
                    bad = {i for i in range(N) if u0[i] != c0[i] or u1[i] != c1[i]}
                    if len(bad) <= 1:
                        corr = True
                        if c0 not in CODE_L or c1 not in CODE_L:
                            cls.descent_fail += 1
                if corr:
                    if len(S) != len(K.elems):
                        cls.violations += 1
                else:
                    cls.max_bad_K = max(cls.max_bad_K, len(S))
                    cls.max_bad_L = max(cls.max_bad_L, sum(1 for z in S if z in L))
                    if len(S) > N:
                        cls.violations += 1

    def test_theorem_4_1_holds_with_the_bound_n_over_K(self):
        self.assertEqual(self.violations, 0)
        self.assertLessEqual(self.max_bad_K, N)
        self.assertGreater(self.max_bad_K, 0)

    def test_the_correlated_codewords_are_over_the_base_field(self):
        self.assertEqual(self.descent_fail, 0)

    def test_control_base_field_challenges_reject_less(self):
        # the same bad challenges, drawn from L only: a larger fraction of L than of K
        self.assertGreater(self.max_bad_L / len(L.elems), self.max_bad_K / len(K.elems))


if __name__ == "__main__":
    unittest.main()
