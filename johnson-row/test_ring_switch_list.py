r"""Lemma J1 (docs/binius-johnson-row.md section 3): the ring switch under a list of candidate oracles.
Revision 2: the referee's test T-J1-list (docs/johnson-row-referee.md section 6) replaces revision 1's
union test, which was set arithmetic on random sets.

Form T of `docs/binius-extension-challenges.md` 3.1 (adapted from Diamond, Posen, "Polylogarithmic
Proofs for Multilinears over Binary Towers", ePrint 2024/504, Construction 3.1 and the
Schwartz-Zippel step of the proof of Theorem 3.5): for one candidate the bad set of r'' has at most
kappa_K |K|^(kappa_K - 1) points (Theorem 1). Lemma J1 is the union over the list of the committed
L-valued row, fixed before r'' is drawn (the union step adapted from Haboeck, "Basefold in the List
Decoding Regime", ePrint 2024/1571, proof of Lemma 5).

Checked:
1. Theorem 1 per deviation, exhaustive (GF(2) < L = GF(4) < K = GF(16), every r'' in K^2).
2. Descent in the list regime, exhaustive over the whole code: L = GF(16) inside K = GF(256), domain
   D = L, RS[K, D, 2], an L-valued row agreeing with two L-lines on disjoint 7-sets: of all 65,536
   K-codewords exactly the two planted ones agree on >= 7 points, and both have coefficients in L
   (Lemma 4 of `binius-extension-challenges.md`).
3. T-J1-list: a committed L-valued row (GF(4) < GF(16), D = L, RS[K, D, 1], agreement 2) whose list
   over K has two members, both descending to L; a claim false for both; for each prover message
   s_hat passing the check, the set of r'' at which SOME member's output query holds is computed from
   the protocol's own output query (not from the residual formula): at most |Lambda| kappa
   |K|^(kappa - 1) = 64, at most 32 per member, and above 32 for some instance (the factor
   |Lambda| is real). Completeness of the output query is checked for an honest member.
Original test code (the Ycash developers, 2026).
"""

import itertools
import random
import unittest

from gf import GF16 as F, GF256

BETA = [1, 6]            # GF(2)-basis of L = GF(4) inside GF(16)
GAMMA = [1, 6, 2, 12]    # GF(2)-basis of K extending BETA (rank 4 checked below)
KAPPA = 2                # log2 [K : GF(2)]


def bits_in_gamma(v: int) -> list[int]:
    """Coordinates of v in GAMMA (solve by brute force over the 16 combinations)."""
    for c in itertools.product((0, 1), repeat=4):
        s = 0
        for b, g in zip(c, GAMMA):
            if b:
                s ^= g
        if s == v:
            return list(c)
    raise AssertionError


def eq_weights(r: tuple[int, int]) -> list[int]:
    """e_j = eq(r'', j) for j < 4, bit 0 of j first; in characteristic 2, eq(r, b) = prod (1 + r_i + b_i)."""
    out = []
    for j in range(4):
        e = 1
        for i in range(KAPPA):
            bit = (j >> i) & 1
            e = F.mul(e, 1 ^ r[i] ^ bit)
        out.append(e)
    return out


def residual(d: list[int], r) -> int:
    """R = sum_i beta_i theta(d_i), theta(gamma_j) = e_j (proof of Theorem 1)."""
    e = eq_weights(r)
    total = 0
    for i, di in enumerate(d):
        th = 0
        for bit, ej in zip(bits_in_gamma(di), e):
            if bit:
                th ^= ej
        total ^= F.mul(BETA[i], th)
    return total


ALL_R = list(itertools.product(range(16), repeat=KAPPA))
BAD_ONE = KAPPA * 16 ** (KAPPA - 1)  # Schwartz-Zippel count kappa |K|^(kappa-1) = 32 of 256


def bad_set(d):
    return {r for r in ALL_R if residual(d, r) == 0}


class RingSwitchList(unittest.TestCase):
    def test_basis_extends(self):
        self.assertEqual(sorted(tuple(bits_in_gamma(v)) for v in range(16)),
                         sorted(itertools.product((0, 1), repeat=4)))
        L = {0, 1, 6, 7}
        self.assertTrue(all(F.mul(a, b) in L and (a ^ b) in L for a in L for b in L))

    def test_single_candidate_theorem_1(self):
        """Every nonzero deviation d in K^2 (255 of them): at most 32 bad r''."""
        worst = 0
        for d in itertools.product(range(16), repeat=2):
            if d == (0, 0):
                continue
            worst = max(worst, len(bad_set(list(d))))
        self.assertLessEqual(worst, BAD_ONE)

    def test_descent_in_the_list_regime_exhaustive_over_K(self):
        K = GF256
        L = [x for x in range(256) if K.pow(x, 16) == x]
        self.assertEqual(len(L), 16)
        rng = random.Random(7)
        lines = [[rng.choice(L), rng.choice(L)] for _ in range(2)]
        perm = rng.sample(range(16), 16)
        row = [rng.choice(L) for _ in range(16)]
        for i in perm[:7]:
            row[i] = K.peval(lines[0], L[i])
        for i in perm[7:14]:
            row[i] = K.peval(lines[1], L[i])
        members = []
        for c0 in range(256):
            for c1 in range(256):
                if sum(1 for i in range(16) if K.peval([c0, c1], L[i]) == row[i]) >= 7:
                    members.append((c0, c1))
        self.assertEqual(sorted(members), sorted(tuple(p) for p in lines))
        self.assertTrue(all(c in L for m in members for c in m))

    def test_T_J1_list_on_the_members_actual_deviations(self):
        L = [0, 1, 6, 7]                       # GF(4) inside GF(16); D = L, the code RS[K, D, 1]
        rng = random.Random(1)
        exceeded = 0
        for _ in range(150):
            a_, b_ = rng.sample(L[1:], 2)
            row = (a_, a_, b_, b_)
            lam = [c for c in range(16) if sum(1 for u in row if u == c) >= 2]   # list over K
            self.assertEqual(sorted(lam), sorted((a_, b_)))
            self.assertTrue(all(c in L for c in lam))                         # descent (Lemma 4)
            r_pack, b0 = rng.randrange(16), rng.randrange(1, 16)
            apk = [1 ^ r_pack, r_pack]                                        # eq(r_pack, i)
            w = {c: bits_in_gamma(c)[:2] for c in lam}                        # bits on BETA = (1, 6)
            for c in lam:
                self.assertEqual(c, (BETA[0] if w[c][0] else 0) ^ (BETA[1] if w[c][1] else 0))
            honest = {c: [F.mul(b0, w[c][i]) for i in range(2)] for c in lam}
            claim_true = {c: F.mul(apk[0], honest[c][0]) ^ F.mul(apk[1], honest[c][1]) for c in lam}
            t = rng.randrange(16)
            if t in claim_true.values() or apk[0] == 0:
                continue                                                      # want a false claim for both
            s1 = rng.randrange(16)
            s0 = F.div(t ^ F.mul(apk[1], s1), apk[0])                         # s_hat passes the check
            s_hat = [s0, s1]
            union, per = set(), {}
            for r in ALL_R:
                e = eq_weights(r)
                theta = lambda v: _theta(v, e)
                s_rs = F.mul(BETA[0], theta(s_hat[0])) ^ F.mul(BETA[1], theta(s_hat[1]))
                for c in lam:
                    if F.mul(c, theta(b0)) == s_rs:                           # member c's output query
                        union.add(r)
                        per[c] = per.get(c, 0) + 1
                    if r == ALL_R[0]:
                        s_rs_h = F.mul(BETA[0], theta(honest[c][0])) ^ F.mul(BETA[1], theta(honest[c][1]))
                        self.assertEqual(F.mul(c, theta(b0)), s_rs_h)          # completeness
            self.assertTrue(all(v <= BAD_ONE for v in per.values()))
            self.assertLessEqual(len(union), len(lam) * BAD_ONE)
            if len(union) > BAD_ONE:
                exceeded += 1
        self.assertGreater(exceeded, 0)


def _theta(v, e):
    out = 0
    for bit, ej in zip(bits_in_gamma(v), e):
        if bit:
            out ^= ej
    return out


if __name__ == "__main__":
    unittest.main()
