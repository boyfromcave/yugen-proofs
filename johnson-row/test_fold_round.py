r"""Lemma F (docs/binius-johnson-row.md section 5.2): one sumcheck-coupled fold round in the list regime.
The referee's test T-F (docs/johnson-row-referee.md section 6).

Toy: K = GF(256), D = the GF(2)-span of 1, x, x^2, x^3 (16 points), RS[K, D, 2], A = 7. The round is
an index round of Binius64's opening (Blueprint Protocol 7.1 step 4): two rows (f0, f1) on the same
domain are folded as (1 - l) f0 + l f1 = f0 + l (f0 + f1) (characteristic 2). The claim before the
round is <q0, R0> + <q1, R1> = v on the messages of the pair; the prover sends the degree-2 round
polynomial h with h(0) + h(1) = v (the verifier's check) BEFORE l; after l the claim on the folded
word is <msg P, R(l)> = h(l), R(l) = (1 - l) R0 + l R1. This is the constraint Gamma_i of Haboeck,
"Basefold in the List Decoding Regime", ePrint 2024/1571, proof of Lemma 4 (Section 6.1), total
degree 2.

Computed exactly: Lambda (the joint list of (f0, f1) at A); doomed (no member satisfies the claim
before the round); S (the challenges l after which some proximate of the folded word satisfies the
claim); E (the challenges at which some proximate of the folded word is not the fold of a list member
with the same agreement set: DKT26 = Dao, Kominers, Thaler, ePrint 2026/2056, Definition 3.2).

Planted: the rows agree with two codeword pairs y1, y2 on disjoint 7-sets; h is the degree-2
polynomial with phi_{y1}(g_a) = phi_{y1}(g_b) = phi_{y2}(g_c) = 0, phi_y(Z) = <(1 - Z) q0 + Z q1,
R(Z)> - h(Z); v := h(0) + h(1); instances where some member satisfies the claim are skipped.
Acceptance (T-F): every good l outside E is a root of some phi_y; |S \ E| <= 2 |Lambda|; and some
instance attains |S \ E| > |Lambda| (the factor 2, the degree of Gamma, is real).
Original test code (the Ycash developers, 2026).
"""

import random
import unittest

from gf import GF256 as F, interleaved_list

DOM = list(range(16))
N, K_DIM, A = 16, 2, 7


def inner(p, t):
    s = 0
    for c, w in zip(p, t):
        s ^= F.mul(c, w)
    return s


def lin(a, b, z):
    """(1 - z) a + z b = a + z (a + b), coordinatewise."""
    return tuple(x ^ F.mul(z, x ^ y) for x, y in zip(a, b))


def A_of(y, R0, R1, z):
    return inner(lin(y[0], y[1], z), lin(R0, R1, z))


def peval(h, z):
    return h[0] ^ F.mul(z, h[1]) ^ F.mul(F.mul(z, z), h[2])


def quad_through(pts):
    """The polynomial of degree <= 2 through three points (z, value)."""
    return list(F.interpolate([p[0] for p in pts], [p[1] for p in pts]))


def analyse(rows, R0, R1, h):
    lam = interleaved_list(F, DOM, rows, K_DIM, A)
    v = peval(h, 0) ^ peval(h, 1)
    doomed = all(inner(y[0], R0) ^ inner(y[1], R1) != v for y in lam)
    S, E = set(), set()
    for z in range(256):
        folded = [lin(rows[0], rows[1], z)]
        for P, agree in interleaved_list(F, DOM, folded, K_DIM, A).items():
            if inner(P[0], lin(R0, R1, z)) == peval(h, z):
                S.add(z)
            if not any(lin(y[0], y[1], z) == P[0] and a == agree for y, a in lam.items()):
                E.add(z)
    return lam, doomed, S, E


def instance(rng):
    R0 = [rng.randrange(256) for _ in range(K_DIM)]
    R1 = [rng.randrange(256) for _ in range(K_DIM)]
    y1 = (tuple(rng.randrange(256) for _ in range(K_DIM)), tuple(rng.randrange(256) for _ in range(K_DIM)))
    y2 = (tuple(rng.randrange(256) for _ in range(K_DIM)), tuple(rng.randrange(256) for _ in range(K_DIM)))
    ga, gb, gc = rng.sample(range(1, 256), 3)
    h = quad_through([(ga, A_of(y1, R0, R1, ga)), (gb, A_of(y1, R0, R1, gb)), (gc, A_of(y2, R0, R1, gc))])
    perm = rng.sample(range(N), N)
    rows = []
    for j in range(2):
        row = [rng.randrange(256) for _ in range(N)]
        for i in perm[:A]:
            row[i] = F.peval(list(y1[j]), DOM[i])
        for i in perm[A:2 * A]:
            row[i] = F.peval(list(y2[j]), DOM[i])
        rows.append(tuple(row))
    return rows, R0, R1, h, (y1, y2)


class FoldRoundList(unittest.TestCase):
    def test_two_roots_per_list_member(self):
        attained = 0
        for seed in range(1, 7):
            rng = random.Random(seed)
            rows, R0, R1, h, planted = instance(rng)
            lam, doomed, S, E = analyse(rows, R0, R1, h)
            self.assertTrue(set(planted) <= set(lam))
            if not doomed:
                continue
            for z in S - E:
                self.assertTrue(any(A_of(y, R0, R1, z) == peval(h, z) for y in lam), (seed, z))
            self.assertLessEqual(len(S - E), 2 * len(lam))
            if len(S - E) > len(lam):
                attained += 1
        self.assertGreaterEqual(attained, 1)


if __name__ == "__main__":
    unittest.main()
