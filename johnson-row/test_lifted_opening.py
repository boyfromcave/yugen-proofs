r"""Lemma J3 with Lemmas J2, F and K (docs/binius-johnson-row.md sections 4, 5, 7): a lifted toy opening
whose lifted list has a non-lift member. The referee's test T-J3 (docs/johnson-row-referee.md
section 6), in round-by-round form (see the note at the end).

Toy over K = GF(256). Level l: E_l = the GF(2)-span of 1, x, x^2, x^3 (16 points), RS[K, E_l, 2].
Level n: E_n = W(E_l), W(x) = x^2 + x (kernel {0, 1}), 8 points, RS[K, E_n, 1]. Rate 1/8 at both
levels; Johnson thresholds at m = 3: A_l = 7, A_n = 4. Oracle 1 is the level-n word f, read at level
l as Dup(f) = f o W (Binius64 Blueprint 5.3, identity (8), in the subspace-polynomial form of
Haboeck, ePrint 2024/1571, Section 6.2, equation (36)); oracle 2 is a level-l word g; each is
committed with a mask (w_1, w_2). The claim reads only the low block of oracle 1 (lifted operand
T1^up = (t1, 0) on messages in the basis (1, X)): sum <msg c_r, T_r> = s.

Opening (Blueprint Protocol 7.1 shape): mask fold gamma (lerp), index round zeta with a degree-2
round polynomial h_idx, one X fold lambda with h_fold (on a fibre {x0, x0 + 1}: o = H(x0) + H(x0 + 1),
e = H(x0) + x0 o, folded e + lambda (e + o)), then the final constant c' and a query y in E_n.
The X fold ends at message dimension 1, where DKT26 (Dao, Kominers, Thaler, ePrint 2026/2056)
Theorem 4.4 does not apply and Lemma 3.3 does (exceptional count at most C(8, 2) / (A_n - 1) = 9).

Instance: f(y) = c0 + rep(y) (rep(y) the smaller point of the fibre); the non-lift codeword
C(x) = c0 + x agrees with Dup(f) on 8 of 16 points, so (C, o1, g0, o2) is in the lifted joint list,
while f has no codeword of RS[K, E_n, 1] within the level-n Johnson radius.

Checked, all exhaustive in the round's challenge:
1. Lifted list: the width-4 list at level l contains the non-lift member; f's own level-n list is
   empty (Lemma J3: the list must be taken at the lifted level).
2. Extraction (Lemma K with Lemma J3): with the claim true for the non-lift member's low block, the
   extractor that decodes at the lifted level returns a witness; decoding f at level n returns none.
3. Mask round (Lemma J2), claim false for every lifted member, for EVERY s' in K: every good gamma
   outside the exceptional set is a root of phi_y for a lifted member, |S \ E| <= |Lambda4|.
4. Index round (Lemma F), for doomed prefixes and random h_idx: |S \ E| <= 2 |Lambda2|, reached.
5. X fold at dimension 1 (Lemma F with DKT26 Lemma 3.3): |E| <= 9 and |S \ E| <= 2 |Lambda|.
   In the chain of test_3_to_6 the pair list at this step turned out empty (second referee,
   johnson-row-referee-2.md 2.2: vacuous there), so test_5_x_fold_at_dimension_one carries the
   referee's construction (condition C-5): a dimension-1 fold, K = GF(256), n = 8, constant code,
   A = 4, rows (e, o) agreeing with two constant pairs on disjoint 4-sets, h with three planted
   roots, 40 instances; it asserts a non-empty pair list (two members) in doomed instances, every
   good lambda outside E a root of some member's phi_y, |S \ E| <= 2 |Lambda|, |E| <= 9, and
   |S \ E| > |Lambda| in some instance.
6. Query: DEFINITIONAL, not a test of a bound. "lambda not in S implies that the one c' passing
   the final check has fewer than A_n agreements with the folded word" restates the definition of
   S (second referee, 2.2); it is kept as a consistency check of the code. The query bound itself
   is Haboeck Lemma 3 (a query accepts a doomed final state with probability at most
   (A_n - 1) / 8 here), cited, not tested.
Note: the referee's acceptance asks for the accepting (challenge, query) mass under the optimal
prover; that game has about 2^50 nodes here (prover polynomials over K^3), so the test checks the
round-by-round errors the lemmas state, every round exhaustive in its challenge, with every s' in
the mask round and random prover polynomials in the later rounds, and the query bound.
Original test code (the Ycash developers, 2026).
"""

import math
import random
import unittest

from gf import GF256 as F, interleaved_list

E_L = list(range(16))


def W(x):
    return F.mul(x, x) ^ x


E_N = sorted({W(x) for x in E_L})
REP = {y: min(x for x in E_L if W(x) == y) for y in E_N}
A_L = math.ceil((1 + 1 / 6) * math.sqrt(1 / 8) * 16)   # 7
A_N = math.ceil((1 + 1 / 6) * math.sqrt(1 / 8) * 8)    # 4


def inner(p, t):
    s = 0
    for c, w in zip(p, t):
        s ^= F.mul(c, w)
    return s


def lin(a, b, z):
    return tuple(x ^ F.mul(z, x ^ y) for x, y in zip(a, b))


def peval2(h, z):
    return h[0] ^ F.mul(z, h[1]) ^ F.mul(F.mul(z, z), h[2])


def quad_through(pts):
    return list(F.interpolate([p[0] for p in pts], [p[1] for p in pts]))


def enc(p):
    return F.encode(list(p), E_L)


class Instance:
    def __init__(self, seed):
        rng = random.Random(seed)
        self.rng = rng
        self.c0 = rng.randrange(256)
        self.f = {y: self.c0 ^ REP[y] for y in E_N}
        self.F = tuple(self.f[W(x)] for x in E_L)                  # Dup(f)
        self.C = (self.c0, 1)                                       # non-lift level-l codeword
        self.o1, self.g0, self.o2 = (tuple(rng.randrange(256) for _ in range(2)) for _ in range(3))
        self.rows = [self.F, enc(self.o1), enc(self.g0), enc(self.o2)]
        self.T1 = (rng.randrange(1, 256), 0)                        # lifted operand: low block only
        self.T2 = (rng.randrange(256), rng.randrange(256))
        self.lam4 = interleaved_list(F, E_L, self.rows, 2, A_L)

    def claim(self, e):
        return inner(e[0], self.T1) ^ inner(e[2], self.T2)


class LiftedOpening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.I = Instance(3)

    def test_1_lifted_list_has_a_non_lift_member_and_f_is_far(self):
        I = self.I
        star = (I.C, I.o1, I.g0, I.o2)
        self.assertIn(star, I.lam4)
        self.assertEqual(len(I.lam4[star]), 8)
        self.assertTrue(all(enc(I.C)[x] != enc(I.C)[x ^ 1] for x in E_L))     # not of the form c o W
        level_n = [c for c in range(256) if sum(1 for y in E_N if I.f[y] == c) >= A_N]
        self.assertEqual(level_n, [])

    def test_2_extraction_at_the_lifted_level(self):
        I = self.I
        s_true = I.claim((I.C, I.o1, I.g0, I.o2))
        # the extractor: decode oracle 1 at the lifted level (scalar list of Dup(f)) and oracle 2,
        # take the low block of oracle 1's member, test the relation (here: the claim)
        list1 = interleaved_list(F, E_L, [I.F], 2, A_L)
        list2 = interleaved_list(F, E_L, [I.rows[2]], 2, A_L)
        found = [(p1[0][0], p2[0]) for p1 in list1 for p2 in list2
                 if inner((p1[0][0], 0), I.T1) ^ inner(p2[0], I.T2) == s_true]
        self.assertIn((I.c0, I.g0), found)
        # decoding f at level n finds no candidate at all
        self.assertEqual([c for c in range(256) if sum(1 for y in E_N if I.f[y] == c) >= A_N], [])

    def _mask_round_tables(self):
        I = self.I
        tables = []
        for g in range(256):
            G = [lin(I.rows[0], I.rows[1], g), lin(I.rows[2], I.rows[3], g)]
            entries = []
            for P, agree in interleaved_list(F, E_L, G, 2, A_L).items():
                explained = any((lin(e[0], e[1], g), lin(e[2], e[3], g)) == P and a == agree
                                for e, a in I.lam4.items())
                entries.append((inner(P[0], I.T1) ^ inner(P[1], I.T2), explained, P))
            tables.append((G, entries))
        return tables

    def test_3_to_6_round_by_round(self):
        I = self.I
        s = 0
        while any(I.claim(e) == s for e in I.lam4):
            s += 1                                                          # doomed: false for every member
        tables = self._mask_round_tables()
        E_mask = {g for g, (_, ent) in enumerate(tables) if any(not ex for _, ex, _ in ent)}
        doomed_prefixes = []
        # 3. mask round, every s'
        for s2 in range(256):
            S = {g for g, (_, ent) in enumerate(tables)
                 if any(val == (s ^ F.mul(g, s ^ s2)) for val, _, _ in ent)}
            for g in S - E_mask:
                self.assertTrue(any(
                    (I.claim(e) ^ s) ^ F.mul(g, I.claim(e) ^ inner(e[1], I.T1) ^ inner(e[3], I.T2) ^ s ^ s2) == 0
                    for e in I.lam4))
            self.assertLessEqual(len(S - E_mask), len(I.lam4))
            if s2 < 2:
                for g in range(1, 256):
                    if g not in S and g not in E_mask and tables[g][1]:
                        doomed_prefixes.append((s2, g))
                        break
        self.assertGreaterEqual(len(doomed_prefixes), 1)
        # 4. index round on doomed prefixes (random h_idx, h(0) + h(1) = target enforced)
        attained = 0
        for s2, g in doomed_prefixes:
            G, ent = tables[g]
            lam2 = {P: None for _, _, P in ent}
            target = s ^ F.mul(g, s ^ s2)
            Tup = (I.T1, I.T2)
            Afun = lambda P, z: inner(lin(P[0], P[1], z), lin(Tup[0], Tup[1], z))
            per_z = []
            full = interleaved_list(F, E_L, G, 2, A_L)
            for z in range(256):
                H = lin(G[0], G[1], z)
                lst = interleaved_list(F, E_L, [H], 2, A_L)
                exc = any(not any(lin(P[0], P[1], z) == Q[0] and full[P] == a for P in full)
                          for Q, a in lst.items())
                per_z.append((H, lst, exc))
            E_idx = {z for z, (_, _, exc) in enumerate(per_z) if exc}
            members = list(lam2)
            hs = [[self.I.rng.randrange(256) for _ in range(3)] for _ in range(6)]
            for h in hs:
                h[1] ^= peval2(h, 0) ^ peval2(h, 1) ^ target                 # enforce h(0) + h(1) = target
                S = {z for z, (_, lst, _) in enumerate(per_z)
                     if any(inner(Q[0], lin(Tup[0], Tup[1], z)) == peval2(h, z) for Q in lst)}
                for z in S - E_idx:
                    self.assertTrue(any(Afun(P, z) == peval2(h, z) for P in members))
                self.assertLessEqual(len(S - E_idx), 2 * len(members))
                if len(S - E_idx) > len(members):
                    attained += 1
            # 5. X fold at dimension 1 from a doomed index prefix, 6. query
            h = hs[0]
            for z in range(256):
                H, lst, _ = per_z[z]
                tau = lin(Tup[0], Tup[1], z)
                if any(inner(Q[0], tau) == peval2(h, z) for Q in lst):
                    continue
                self._x_fold_and_query(H, tau, peval2(h, z))
                break
        self.assertGreaterEqual(attained, 1)        # the factor 2 of the index round is reached

    def test_5_x_fold_at_dimension_one(self):
        """T-J3 step 5, non-vacuous (condition C-5; johnson-row-referee-2.md 2.2): Lemma F at message
        dimension 1 with a two-member pair list in doomed instances, DKT26 Lemma 3.3's count."""
        rng = random.Random(2056)
        lemma33 = (8 * 7 // 2) // (A_N - 1)                                  # DKT26 Lemma 3.3 (6): 9
        doomed_instances = above_list = 0
        for _ in range(40):
            pts = E_N[:]
            rng.shuffle(pts)
            S1, S2 = set(pts[:4]), set(pts[4:])
            a1, a2 = rng.sample(range(256), 2)
            b1, b2 = rng.sample(range(256), 2)
            e = {y: a1 if y in S1 else a2 for y in E_N}
            o = {y: b1 if y in S1 else b2 for y in E_N}
            tau = (rng.randrange(1, 256), rng.randrange(1, 256))
            tl = lambda lam: tau[0] ^ F.mul(lam, tau[0] ^ tau[1])
            fold = lambda c0, c1, lam: c0 ^ F.mul(lam, c0 ^ c1)
            ga, gb, gc = rng.sample(range(2, 256), 3)
            h = quad_through([(ga, F.mul(fold(a1, b1, ga), tl(ga))), (gb, F.mul(fold(a1, b1, gb), tl(gb))),
                              (gc, F.mul(fold(a2, b2, gc), tl(gc)))])
            h = (h + [0, 0, 0])[:3]
            claim = peval2(h, 0) ^ peval2(h, 1)
            pair_list = []
            for ce in range(256):
                Se = {y for y in E_N if e[y] == ce}
                for co in (range(256) if len(Se) >= A_N else ()):
                    Sj = frozenset(y for y in Se if o[y] == co)
                    if len(Sj) >= A_N:
                        pair_list.append(((ce, co), Sj))
            self.assertEqual(len(pair_list), 2)
            if any(F.mul(ce, tau[0]) ^ F.mul(co, tau[1]) == claim for (ce, co), _ in pair_list):
                continue                                                    # not doomed: skipped
            doomed_instances += 1
            phi = lambda ce, co, lam: F.mul(fold(ce, co, lam), tl(lam)) ^ peval2(h, lam)
            S, E = set(), set()
            for lam in range(256):
                folded = {y: fold(e[y], o[y], lam) for y in E_N}
                for c in set(folded.values()):
                    agree = frozenset(y for y in E_N if folded[y] == c)
                    if len(agree) < A_N:
                        continue
                    if F.mul(c, tl(lam)) == peval2(h, lam):
                        S.add(lam)
                    if not any(fold(ce, co, lam) == c and a == agree for (ce, co), a in pair_list):
                        E.add(lam)
            self.assertLessEqual(len(E), lemma33)
            for lam in S - E:                                               # Lemma F steps 3 to 5
                self.assertTrue(any(phi(ce, co, lam) == 0 for (ce, co), _ in pair_list))
            self.assertLessEqual(len(S - E), 2 * len(pair_list))
            if len(S - E) > len(pair_list):
                above_list += 1
        self.assertGreaterEqual(doomed_instances, 30)
        self.assertGreaterEqual(above_list, 1)                              # the factor 2 is reached at dimension 1

    def _x_fold_and_query(self, H, tau, claim_value):
        o = {y: H[REP[y]] ^ H[REP[y] ^ 1] for y in E_N}
        e = {y: H[REP[y]] ^ F.mul(REP[y], o[y]) for y in E_N}
        pair_list = []
        for ce in range(256):
            Se = {y for y in E_N if e[y] == ce}
            if len(Se) < A_N:
                continue
            for co in range(256):
                Sj = {y for y in Se if o[y] == co}
                if len(Sj) >= A_N:
                    pair_list.append(((ce, co), frozenset(Sj)))
        doomed = all(F.mul(ce, tau[0]) ^ F.mul(co, tau[1]) != claim_value for (ce, co), _ in pair_list)
        self.assertTrue(doomed or pair_list)
        rng = random.Random(9)
        hs = [[rng.randrange(256) for _ in range(3)] for _ in range(4)]
        for h in hs:
            h[1] ^= peval2(h, 0) ^ peval2(h, 1) ^ claim_value
            S, E = set(), set()
            for lam in range(256):
                folded = {y: e[y] ^ F.mul(lam, e[y] ^ o[y]) for y in E_N}
                tl = tau[0] ^ F.mul(lam, tau[0] ^ tau[1])
                for c in range(256):
                    agree = frozenset(y for y in E_N if folded[y] == c)
                    if len(agree) < A_N:
                        continue
                    if F.mul(c, tl) == peval2(h, lam):
                        S.add(lam)
                    if not any((ce ^ F.mul(lam, ce ^ co)) == c and a == agree for (ce, co), a in pair_list):
                        E.add(lam)
                if lam not in S and tl != 0:
                    cprime = F.div(peval2(h, lam), tl)                    # the only c' passing the check
                    self.assertLessEqual(sum(1 for y in E_N if folded[y] == cprime), A_N - 1)
            self.assertLessEqual(len(E), (8 * 7 // 2) // (A_N - 1))      # DKT26 Lemma 3.3
            if doomed:
                self.assertLessEqual(len(S - E), 2 * len(pair_list))


if __name__ == "__main__":
    unittest.main()
