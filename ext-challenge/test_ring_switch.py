"""Exact tests of the mixed-field ring switch (docs/binius-extension-challenges.md section 3).

Fields GF(2) < L < K. The witness is bits w(i, y), i < [L:GF(2)], packed as pi(y) = sum_i w(i, y) beta_i
in L. The claim weight b(y) is in K. Two forms of the reduction are tested:

  T  theta(x) = sum_j bit_j(x) eq(r'', j),   j over a GF(2)-basis of K,  r'' in K^(log2 [K:2])
  F  theta(x) = sum_m eq(r'', m) x^(2^m),    m < [L:GF(2)],              r'' in K^(log2 [L:2])

Provenance (REFERENCES.md O-11; CITATION-AUDIT.md C-13). Adapted, not original: form T is ring switching,
Diamond, Posen, "Polylogarithmic Proofs for Multilinears over Binary Towers", ePrint 2024/504, Construction 3.1
and Theorem 3.5 (error kappa / |field| from Schwartz-Zippel on the batching point r''), applied over GF(2) < K
to a packed polynomial whose upper basis coordinates are zero; form F is the Galois-orbit check of Soukhanov's
Hashcaster in the form ePrint 2024/504 gives in Section 1.3, equations (16) to (20), Figure 4, with the orbit
of L and claims and challenges in K. The adaptation to three fields and the exact tests are the Ycash
developers' (2026).

Run: python3 -m unittest -v   (standard library only)
"""

import random
import unittest
from itertools import product

import gf
from gf import F4, F16, PAIRS, dot, eq2, eq_expand, frob, mul


def theta_T(K, e):
    return lambda x: dot(K.bits(x), e)


def theta_F(L, e):
    return lambda x: dot(e, [frob(x, m) for m in range(L.deg)])


def instance(L, K, n, rng):
    w = [[rng.randrange(2) for _ in range(n)] for _ in range(L.deg)]
    pi = [dot([w[i][y] for i in range(L.deg)], L.basis) for y in range(n)]
    b = [rng.choice(K.elems) for _ in range(n)]
    s_hat = [dot(w[i], b) for i in range(L.deg)]
    return w, pi, b, s_hat


def query_holds(L, theta, pi, b, s_hat):
    lhs = dot(pi, [theta(x) for x in b])
    rhs = dot(L.basis, [theta(s) for s in s_hat])
    return lhs == rhs


class Completeness(unittest.TestCase):
    def test_both_forms_all_pairs(self):
        rng = random.Random(1)
        for L, K in PAIRS:
            for _ in range(200):
                w, pi, b, s_hat = instance(L, K, 5, rng)
                self.assertTrue(all(p in L for p in pi))
                eT = eq_expand([rng.choice(K.elems) for _ in range(K.kappa)])
                eF = eq_expand([rng.choice(K.elems) for _ in range(L.kappa)])
                self.assertTrue(query_holds(L, theta_T(K, eT), pi, b, s_hat))
                self.assertTrue(query_holds(L, theta_F(L, eF), pi, b, s_hat))

    def test_message_length_is_the_packing_degree(self):
        # the message has [L:2] elements of K: [L:2] * [K:2] bits, not [K:2]^2
        for L, K in PAIRS:
            _, _, _, s_hat = instance(L, K, 3, random.Random(2))
            self.assertEqual(len(s_hat), L.deg)


def residual_T(L, K, d, e):
    """sum_i beta_i theta(d_i): zero iff a wrong message d + honest passes the query."""
    return dot(L.basis, [dot(K.bits(x), e) for x in d])


def coeffs_T(L, K, d):
    """c_j = sum_i bit_j(d_i) beta_i: the multilinear in r'' whose value is the residual."""
    return [dot([K.bits(x)[j] for x in d], L.basis) for j in range(K.deg)]


def coeffs_F(L, d, powers=None):
    return [dot(L.basis, [frob(x, m) for x in d]) for m in range(L.deg if powers is None else powers)]


class SoundnessExhaustive(unittest.TestCase):
    """L = GF(4), K = GF(16): every wrong message against every challenge."""

    def test_form_T_bound_kappa_over_K(self):
        L, K = F4, F16
        points = [eq_expand(r) for r in product(K.elems, repeat=K.kappa)]
        worst = 0
        for d in product(K.elems, repeat=L.deg):
            if not any(d):
                continue
            zeros = sum(1 for e in points if residual_T(L, K, d, e) == 0)
            worst = max(worst, zeros)
        # Schwartz-Zippel for a nonzero multilinear in kappa_K variables: at most kappa_K |K|^(kappa_K - 1)
        self.assertLessEqual(worst, K.kappa * len(K.elems) ** (K.kappa - 1))
        self.assertGreater(worst, 0)
        self.worst = worst

    def test_form_F_bound_kappa_L_over_K(self):
        L, K = F4, F16
        points = [eq_expand(r) for r in product(K.elems, repeat=L.kappa)]
        worst = 0
        for d in product(K.elems, repeat=L.deg):
            if not any(d):
                continue
            zeros = sum(1 for e in points if dot(L.basis, [dot(e, [frob(x, m) for m in range(L.deg)]) for x in d]) == 0)
            worst = max(worst, zeros)
        self.assertLessEqual(worst, L.kappa * len(K.elems) ** (L.kappa - 1))

    def test_control_challenges_from_the_base_field_are_weaker(self):
        # r'' drawn from L instead of K: some wrong message passes for more than the K-bound's fraction
        L, K = F4, F16
        points = [eq_expand(r) for r in product(L.elems, repeat=K.kappa)]
        worst = max(sum(1 for e in points if residual_T(L, K, d, e) == 0)
                    for d in product(K.elems, repeat=L.deg) if any(d))
        self.assertGreater(worst / len(points), K.kappa / len(K.elems))


class SoundnessStructure(unittest.TestCase):
    """The step the proof rests on, for every pair: a nonzero difference has a nonzero coefficient."""

    def diffs(self, L, K, rng):
        if len(K.elems) ** L.deg <= 70_000:
            return (d for d in product(K.elems, repeat=L.deg) if any(d))
        return (tuple(rng.choice(K.elems) for _ in range(L.deg)) for _ in range(20_000))

    def test_form_T_coefficients(self):
        for L, K in PAIRS:
            for d in self.diffs(L, K, random.Random(3)):
                if any(d):
                    self.assertTrue(any(coeffs_T(L, K, d)))

    def test_form_F_coefficients(self):
        for L, K in PAIRS:
            for d in self.diffs(L, K, random.Random(4)):
                if any(d):
                    self.assertTrue(any(coeffs_F(L, d)))

    def test_moore_matrix_of_the_basis_is_invertible(self):
        # (beta_i^(2^m))_{m, i < [L:2]} has full rank over K: the reason [L:2] Frobenius powers suffice
        for L, K in PAIRS:
            rows = [[frob(b, m) for b in L.basis] for m in range(L.deg)]
            self.assertEqual(rank(rows), L.deg)

    def test_control_T_with_only_the_base_field_columns_is_unsound(self):
        # the pin's functional has [L:2] columns; kept as is under K-valued messages it misses every
        # difference whose K-coordinates outside L's basis are the only nonzero ones
        for L, K in PAIRS:
            y = K.basis[L.deg]  # a basis element of K outside L
            d = (y,) + (0,) * (L.deg - 1)
            c = coeffs_T(L, K, d)
            self.assertTrue(any(c))
            self.assertFalse(any(c[: L.deg]))  # invisible to the truncated functional for every r''

    def test_control_F_with_one_power_fewer_is_unsound(self):
        for L, K in PAIRS:
            # solve sum_i beta_i^(2^m) d_i = 0 for m < [L:2] - 1: a nonzero solution exists (rank deficit)
            rows = [[frob(b, m) for b in L.basis] for m in range(L.deg - 1)]
            self.assertLess(rank(rows), L.deg)
            found = kernel_vector(rows, L.deg)
            self.assertTrue(any(found))
            # c'_m = sum_i beta_i d_i^(2^m) = (sum_i beta_i^(2^-m) d_i)^(2^m): use conjugated rows
            d = kernel_vector([[frob(b, (8 - m) % 8) for b in L.basis] for m in range(L.deg - 1)], L.deg)
            self.assertTrue(any(d))
            self.assertFalse(any(coeffs_F(L, d, powers=L.deg - 1)))
            self.assertTrue(any(coeffs_F(L, d)))


def rank(rows):
    rows = [r[:] for r in rows]
    rk = 0
    for col in range(len(rows[0])):
        piv = next((i for i in range(rk, len(rows)) if rows[i][col]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        iv = gf.inv(rows[rk][col])
        rows[rk] = [mul(iv, x) for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][col]:
                f = rows[i][col]
                rows[i] = [x ^ mul(f, y) for x, y in zip(rows[i], rows[rk])]
        rk += 1
    return rk


def kernel_vector(rows, n):
    """A nonzero v in K^n with rows . v = 0 (rows has rank < n), by reduced row echelon form."""
    rows = [r[:] for r in rows]
    pivots, rk = [], 0
    for col in range(n):
        piv = next((i for i in range(rk, len(rows)) if rows[i][col]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        iv = gf.inv(rows[rk][col])
        rows[rk] = [mul(iv, x) for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][col]:
                f = rows[i][col]
                rows[i] = [x ^ mul(f, y) for x, y in zip(rows[i], rows[rk])]
        pivots.append(col)
        rk += 1
    free = next(c for c in range(n) if c not in pivots)
    v = [0] * n
    v[free] = 1
    for i, pc in enumerate(pivots):
        v[pc] = rows[i][free]
    return tuple(v)


class Operand(unittest.TestCase):
    """The verifier's succinct evaluation of the operand t_rs(rho) = sum_y eq(rho, y) theta(eq(z, y))."""

    def mle(self, theta, rho, z):
        n = len(z)
        acc = 0
        for y in range(2**n):
            ybits = [(y >> k) & 1 for k in range(n)]
            acc ^= mul(eq2(rho, ybits), theta(eq2(z, ybits)))
        return acc

    def test_form_F_is_a_sum_over_frobenius_conjugates_of_the_point(self):
        rng = random.Random(5)
        for L, K in PAIRS:
            for _ in range(40):
                n = 3
                rho = [rng.choice(K.elems) for _ in range(n)]
                z = [rng.choice(K.elems) for _ in range(n)]
                e = eq_expand([rng.choice(K.elems) for _ in range(L.kappa)])
                direct = self.mle(theta_F(L, e), rho, z)
                succinct = dot(e, [eq2(rho, [frob(c, m) for c in z]) for m in range(L.deg)])
                self.assertEqual(direct, succinct)

    def test_form_T_through_the_trace_dual_basis(self):
        # theta_T(x) = sum_m c_m x^(2^m), c_m = sum_j e_j dual_j^(2^m), m < [K:2]
        rng = random.Random(6)
        for L, K in PAIRS:
            dual = dual_basis(K)
            for _ in range(20):
                n = 2
                rho = [rng.choice(K.elems) for _ in range(n)]
                z = [rng.choice(K.elems) for _ in range(n)]
                e = eq_expand([rng.choice(K.elems) for _ in range(K.kappa)])
                c = [dot(e, [frob(g, m) for g in dual]) for m in range(K.deg)]
                direct = self.mle(theta_T(K, e), rho, z)
                succinct = dot(c, [eq2(rho, [frob(x, m) for x in z]) for m in range(K.deg)])
                self.assertEqual(direct, succinct)


def _trace(K, x):
    acc = 0
    for m in range(K.deg):
        acc ^= frob(x, m)
    assert acc in (0, 1)
    return acc


def dual_basis(K):
    """gamma*_j with Tr(gamma*_j gamma_k) = [j = k]."""
    out = []
    for j in range(K.deg):
        cands = [g for g in K.elems if all(_trace(K, mul(g, K.basis[k])) == (1 if k == j else 0) for k in range(K.deg))]
        assert len(cands) == 1
        out.append(cands[0])
    return out


if __name__ == "__main__":
    unittest.main()
