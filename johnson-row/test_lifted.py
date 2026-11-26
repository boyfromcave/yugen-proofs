"""Lemma J3 (docs/binius-johnson-row.md section 5): lifted oracles of unequal size.

Toy: K = GF(256); level-l domain E_l = GF(2)-span of 1, x, ..., x^4 (32 points); the quadratic
GF(2)-linear map W(x) = x^2 + x (kernel {0, 1}) takes E_l two-to-one onto E_n (16 points). Codes
RS[K, E_n, 2] and RS[K, E_l, 4], both of rate 1/8. The lift of a level-n word f is Dup(f) = f o W
(the codeword-duplication form of the Binius64 Blueprint's Lifted BaseFold, Section 5.3, identity (8)
and Theorem 5.1, there attributed to [HMH] and the Lin-Chung-Han basis; here in the
subspace-polynomial form, which is the same statement for the first projection of an additive FFT,
Haboeck, ePrint 2024/1571, Section 6.2, equation (36)).

Checked:
1. Completeness direction: p o W is a level-l codeword for every level-n codeword p, and agreement
   fractions are preserved: agree(Dup f, p o W) = agree(f, p).
2. Query emulation: a uniform x in E_l gives a uniform W(x) in E_n.
3. The list-regime phenomenon Lemma J3 is built around: a level-l codeword C that is NOT a lift agrees
   with Dup(f) on half of E_l (above the Johnson threshold at m = 3), while f itself is far from
   RS[K, E_n, 2] (best agreement computed exactly). So "Dup(f) is close, hence f is close" is false in
   the list regime; Lemma J3 never uses it: the list is taken at the lifted level, where it is fixed
   once f is committed.
Original test code (the Ycash developers, 2026).
"""

import math
import random
import unittest

from gf import GF256 as F, interleaved_list

E_L = list(range(32))


def W(x: int) -> int:
    return F.mul(x, x) ^ x


E_N = sorted({W(x) for x in E_L})
RHO = 1 / 8


def johnson_A(n: int, m: int = 3) -> int:
    return math.ceil((1 + 1 / (2 * m)) * math.sqrt(RHO) * n)


def agree(a, b) -> int:
    return sum(1 for x, y in zip(a, b) if x == y)


def dup(fvals: dict) -> tuple:
    return tuple(fvals[W(x)] for x in E_L)


class Lifted(unittest.TestCase):
    def test_domains(self):
        self.assertEqual(len(E_N), 16)
        self.assertTrue(all(W(x ^ 1) == W(x) for x in E_L))
        # GF(2)-linearity of W
        self.assertTrue(all(W(a ^ b) == W(a) ^ W(b) for a in E_L for b in E_L))

    def test_lift_is_a_codeword_and_preserves_agreement(self):
        rng = random.Random(3)
        for _ in range(20):
            p = [rng.randrange(256) for _ in range(2)]
            lifted = tuple(F.peval(p, W(x)) for x in E_L)
            # degree of p o W is at most 2 < 4: it interpolates through any 4 of its points
            xs = rng.sample(E_L, 4)
            q = F.interpolate(xs, [lifted[x] for x in xs])
            self.assertEqual(F.encode(q, E_L), lifted)
            self.assertEqual(q[3], 0)
            f = {y: F.peval(p, y) for y in E_N}
            for y in rng.sample(E_N, 5):
                f[y] ^= rng.randrange(1, 256)
            self.assertEqual(agree(dup(f), lifted) / len(E_L), agree(tuple(f[y] for y in E_N),
                                                                     F.encode(p, E_N)) / len(E_N))

    def test_query_emulation_is_uniform(self):
        counts = {}
        for x in E_L:
            counts[W(x)] = counts.get(W(x), 0) + 1
        self.assertEqual(set(counts.values()), {2})

    def test_non_lift_list_element_while_f_is_far(self):
        rng = random.Random(5)
        c0 = [rng.randrange(256) for _ in range(2)]
        C = tuple(F.peval(c0, W(x)) ^ x for x in E_L)          # degree 3 < 4: a level-l codeword
        rep = {y: min(x for x in E_L if W(x) == y) for y in E_N}
        f = {y: F.peval(c0, y) ^ rep[y] for y in E_N}
        a_lift = agree(dup(f), C)
        self.assertEqual(a_lift, 16)                             # one point of every fibre
        self.assertGreaterEqual(a_lift, johnson_A(32))           # 16 >= 14: C is in the lifted list
        self.assertTrue(all(C[x] != C[x ^ 1] for x in E_L))      # C is not of the form c o W
        best = max(len(a) for a in interleaved_list(F, E_N, [tuple(f[y] for y in E_N)], 2, 2).values())
        self.assertLess(best, johnson_A(16))                     # f is outside the level-n Johnson list
        self.assertLess(best / 16, 1 - (1 - RHO) / 2)            # and outside the unique-decoding radius


if __name__ == "__main__":
    unittest.main()
