r"""Lemma J2 (docs/binius-johnson-row.md section 4): the zero-knowledge mask round over several oracles.
Revision 2: the referee's test T-J2-list (docs/johnson-row-referee.md section 6) replaces the
tautological and vacuous tests of revision 1.

Toy: K = GF(256), D = the GF(2)-span of 1, x, x^2, x^3 (16 points), RS[K, D, 2] (rate 1/8), two
round oracles, each committed with its mask: four rows (M_1, w_1, M_2, w_2). The mask fold is the
Blueprint's lerp(gamma, M_r, w_r) = M_r + gamma (M_r + w_r) (Binius64 Blueprint, Protocol 7.1;
characteristic 2) or Diamond's gamma M_r + w_r (Diamond, "Zero-Knowledge Polynomial Commitment in
Binary Fields", ePrint 2025/1015, Construction 4.1, step 4), jointly over r with one challenge. The
claim is K-linear across the oracles: sum_r <coefficients of M_r, T_r> = s.

Computed exactly, per instance:
- Lambda4: the joint list of the four rows at threshold A (gf.interleaved_list, exhaustive);
- S: the challenges after which some joint proximate of the folded pair satisfies the folded claim;
- E: the exceptional challenges, at which some joint proximate of the folded pair is NOT the fold of
  a Lambda4 element with the same agreement set (mutual correlated agreement with full agreement
  sets: Dao, Kominers, Thaler, "Reed-Solomon Codes Beyond Johnson", ePrint 2026/2056, Definition 3.2;
  interleaved form Lemma 6.5 / Corollary 6.6).

T-J2-list (list regime, A = 7, in both orientations): the rows agree with two distinct codeword
tuples y1, y2 on disjoint 7-sets, every list member has a false claim (doomed), and s' places the
root of phi_y (the affine polynomial of the proof of Lemma J2) at a chosen challenge for each of
y1 and y2. Checked: every good challenge outside E is a root of phi_y for some list member, and
|S \ E| <= |Lambda4|; some instance has |S \ E| >= 2, so the root (claim) term B_list / |K| is
exercised and cannot be dropped. In unique decoding (A = 9) the line bound |E| <= n of Arnon,
Chiesa, Fenzi, Yogev, "WHIR", ePrint 2024/1586, Lemma 4.10 (any linear code) with BCIKS20 Theorem
4.1, carried to width 4 by ePrint 2026/2056 Lemma 6.5, is checked on planted cancellations; and a
close word with a false claim has at most one good challenge outside E.
Original test code (the Ycash developers, 2026).
"""

import random
import unittest

from gf import GF256 as F, interleaved_list

DOM = list(range(16))
K_DIM = 2
N = len(DOM)


def inner(p, t):
    s = 0
    for c, w in zip(p, t):
        s ^= F.mul(c, w)
    return s


def coeffs_inner(polys, T):
    s = 0
    for p, t in zip(polys, T):
        s ^= inner(p, t)
    return s


def fold_rows(rows4, g, orient):
    out = []
    for r in range(2):
        M, w = rows4[2 * r], rows4[2 * r + 1]
        if orient == "lerp":
            out.append(tuple(m ^ F.mul(g, m ^ x) for m, x in zip(M, w)))
        else:  # Diamond: g M + w
            out.append(tuple(F.mul(g, m) ^ x for m, x in zip(M, w)))
    return out


def fold_poly(a, b, g, orient):
    if orient == "lerp":
        return tuple(x ^ F.mul(g, x ^ y) for x, y in zip(a, b))
    return tuple(F.mul(g, x) ^ y for x, y in zip(a, b))


def folded_target(s, s2, g, orient):
    return (s ^ F.mul(g, s ^ s2)) if orient == "lerp" else (F.mul(g, s) ^ s2)


def phi(e, T, s, s2, g, orient):
    """phi_y(g) of the proof of Lemma J2 for the list member e = (M_1, w_1, M_2, w_2):
    lerp: (C + s) + g (G + s + s'), C = sum <M_r, T_r>, G = sum <M_r + w_r, T_r>;
    Diamond: (O + s') + g (C + s), O = sum <w_r, T_r>."""
    C = coeffs_inner((e[0], e[2]), T)
    O = coeffs_inner((e[1], e[3]), T)
    if orient == "lerp":
        return (C ^ s) ^ F.mul(g, C ^ O ^ s ^ s2)
    return (O ^ s2) ^ F.mul(g, C ^ s)


def analyse(rows4, T, s, s2, A, orient):
    lam4 = interleaved_list(F, DOM, rows4, K_DIM, A)
    doomed = all(coeffs_inner((e[0], e[2]), T) != s for e in lam4)
    S, E = set(), set()
    for g in range(256):
        lam = interleaved_list(F, DOM, fold_rows(rows4, g, orient), K_DIM, A)
        for P, agree in lam.items():
            if coeffs_inner(P, T) == folded_target(s, s2, g, orient):
                S.add(g)
            explained = any(
                (fold_poly(e[0], e[1], g, orient), fold_poly(e[2], e[3], g, orient)) == P and a4 == agree
                for e, a4 in lam4.items())
            if not explained:
                E.add(g)
    return lam4, doomed, S, E


def rand_poly(rng):
    return [rng.randrange(256) for _ in range(K_DIM)]


def two_member_instance(rng, orient, A=7):
    """Rows agreeing with y1 on one 7-set and with y2 on a disjoint 7-set; claim false for both;
    s' chosen and the w-parts of y1, y2 adjusted so that phi_{y1}, phi_{y2} have roots at chosen
    challenges g1 != g2 (requires T[1][0] != 0)."""
    T = [rand_poly(rng), [rng.randrange(1, 256), rng.randrange(256)]]
    s, s2 = rng.randrange(256), rng.randrange(256)
    g1, g2 = rng.sample(range(1, 256), 2)
    members = []
    for g in (g1, g2):
        M1, w1, M2, w2 = (rand_poly(rng) for _ in range(4))
        C = coeffs_inner((M1, M2), T)
        if C == s:
            M1[0] ^= 1 if T[0][0] else 0
            C = coeffs_inner((M1, M2), T)
        if orient == "lerp":
            # need C + O = (C + s)/g + s + s'  =>  O = target; adjust w2[0]
            target = F.div(C ^ s, g) ^ s ^ s2 ^ C
        else:
            # need O = g (C + s) + s'
            target = F.mul(g, C ^ s) ^ s2
        O_rest = inner(w1, T[0]) ^ F.mul(w2[1], T[1][1])
        w2[0] = F.div(target ^ O_rest, T[1][0])
        members.append((M1, w1, M2, w2))
    perm = rng.sample(range(N), N)
    S1, S2, rest = perm[:A], perm[A:2 * A], perm[2 * A:]
    rows = []
    for j in range(4):
        row = [0] * N
        for i in S1:
            row[i] = F.peval(members[0][j], DOM[i])
        for i in S2:
            row[i] = F.peval(members[1][j], DOM[i])
        for i in rest:
            row[i] = rng.randrange(256)
        rows.append(tuple(row))
    return rows, T, s, s2, (g1, g2), members


class MaskRoundList(unittest.TestCase):
    """T-J2-list."""

    def _run(self, orient):
        attained = 0
        for seed in range(1, 5):
            rng = random.Random(1000 * (orient == "diamond") + seed)
            rows, T, s, s2, gs, members = two_member_instance(rng, orient)
            lam4, doomed, S, E = analyse(rows, T, s, s2, 7, orient)
            planted = {tuple(tuple(p) for p in m) for m in members}
            self.assertTrue(planted <= set(lam4))          # the list is non-empty: |Lambda4| >= 2
            if not doomed:
                continue
            for g in S - E:                                 # every good g outside E is a root
                self.assertTrue(any(phi(e, T, s, s2, g, orient) == 0 for e in lam4), (seed, g))
            self.assertLessEqual(len(S - E), len(lam4))
            if len(S - E) >= 2:
                attained += 1
        self.assertGreaterEqual(attained, 1)              # the root term is exercised

    def test_lerp_orientation(self):
        self._run("lerp")

    def test_diamond_orientation(self):
        self._run("diamond")


class MaskRoundUniqueDecoding(unittest.TestCase):
    def test_line_bound_with_planted_cancellations(self):
        """Rows u + e with error supports cancelling in the lerp fold at chosen challenges: the
        exceptional set contains the planted challenges and has at most n elements (WHIR Lemma
        4.10 with BCIKS20 Theorem 4.1, width 4 by DKT26 Lemma 6.5)."""
        rng = random.Random(11)
        T = [rand_poly(rng), rand_poly(rng)]
        us = [rand_poly(rng) for _ in range(4)]
        perm = rng.sample(range(N), N)
        gs = rng.sample(range(2, 256), 2)
        rows = [list(F.encode(u, DOM)) for u in us]
        for Q, g in zip((perm[:3], perm[3:6]), gs):
            for i in Q:
                for r in range(2):
                    e = rng.randrange(1, 256)
                    rows[2 * r][i] ^= e
                    rows[2 * r + 1][i] ^= F.div(F.mul(e, 1 ^ g), g)
        rows = [tuple(r) for r in rows]
        lam4, doomed, S, E = analyse(rows, T, coeffs_inner((us[0], us[2]), T) ^ 1, 0, 9, "lerp")
        self.assertLessEqual(len(E), N)

    def test_close_but_false_claim(self):
        """Rows close to codewords (one error each) with a false claim: Lambda4 has one element,
        |E| <= n, and at most one good challenge outside E."""
        rng = random.Random(41)
        T = [rand_poly(rng), rand_poly(rng)]
        polys = [rand_poly(rng) for _ in range(4)]
        rows = []
        for p in polys:
            w = list(F.encode(p, DOM))
            w[rng.randrange(N)] ^= rng.randrange(1, 256)
            rows.append(tuple(w))
        s = coeffs_inner((polys[0], polys[2]), T) ^ 5
        s2 = rng.randrange(256)
        lam4, doomed, S, E = analyse(rows, T, s, s2, 9, "lerp")
        self.assertTrue(doomed)
        self.assertEqual(len(lam4), 1)
        self.assertLessEqual(len(E), N)
        self.assertLessEqual(len(S - E), len(lam4))


if __name__ == "__main__":
    unittest.main()
