"""GF(2^k) arithmetic, sparse affine forms, exact linear algebra. Standard library only.

A field element is an int in [0, 2^k); addition is XOR. An *affine form* is a dict
{variable index: coefficient} with key -1 for the constant term: the symbolic value of a prover
quantity as a function of the secret variables (witness and prover randomness). Every protocol in
this directory is linear in the secrets once the verifier's challenges are fixed, so running the
honest prover on forms yields the exact affine map  view = a0 + A w + B z.
"""
import itertools
from collections import Counter

MODULI = {2: 0x7, 3: 0xB, 4: 0x13, 6: 0x43, 8: 0x11B}


class GF:
    def __init__(self, k):
        self.k, self.q, mod = k, 1 << k, MODULI[k]

        def slow(a, b):
            r = 0
            while b:
                if b & 1:
                    r ^= a
                a <<= 1
                if a >> k:
                    a ^= mod
                b >>= 1
            return r
        self.table = [[slow(a, b) for b in range(self.q)] for a in range(self.q)]
        self.invt = [0] + [self.table[a].index(1) for a in range(1, self.q)]

    def mul(self, a, b):
        return self.table[a][b]

    def pow(self, a, e):
        r = 1
        for _ in range(e):
            r = self.table[r][a]
        return r

    def inv(self, a):
        if a == 0:
            raise ZeroDivisionError
        return self.invt[a]

    def dot(self, u, v):
        r = 0
        for a, b in zip(u, v):
            r ^= self.table[a][b]
        return r

    def rank(self, rows):
        rows = [r[:] for r in rows if any(r)]
        rk, T = 0, self.table
        ncols = len(rows[0]) if rows else 0
        for c in range(ncols):
            p = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
            if p is None:
                continue
            rows[rk], rows[p] = rows[p], rows[rk]
            iv = T[self.invt[rows[rk][c]]]
            piv = rows[rk] = [iv[v] for v in rows[rk]]
            for i in range(len(rows)):
                if i != rk and rows[i][c]:
                    fac = T[rows[i][c]]
                    rows[i] = [v ^ fac[w] for v, w in zip(rows[i], piv)]
            rk += 1
            if rk == len(rows):
                break
        return rk

    def interp(self, xs, ys, x):
        """Value at x of the polynomial through (xs, ys). ys may be field elements."""
        r = 0
        for i, xi in enumerate(xs):
            num = den = 1
            for j, xj in enumerate(xs):
                if j != i:
                    num = self.mul(num, x ^ xj)
                    den = self.mul(den, xi ^ xj)
            r ^= self.mul(ys[i], self.mul(num, self.inv(den)))
        return r


# ---------------------------------------------------------------- affine forms

class Vars:
    """Allocator of secret variables, in named groups."""

    def __init__(self):
        self.n = 0
        self.groups = {}

    def new(self, name, count):
        idx = list(range(self.n, self.n + count))
        self.n += count
        self.groups.setdefault(name, []).extend(idx)
        return [{i: 1} for i in idx]

    def indices(self, *names):
        return [i for nm in names for i in self.groups.get(nm, [])]


def const(c):
    return {-1: c} if c else {}


def fadd(*forms):
    r = {}
    for f in forms:
        for k, v in f.items():
            x = r.get(k, 0) ^ v
            if x:
                r[k] = x
            else:
                r.pop(k, None)
    return r


def fscale(F, c, f):
    if c == 0:
        return {}
    row = F.table[c]
    return {k: row[v] for k, v in f.items()}


def lincomb(F, coeffs, forms):
    r = {}
    for c, f in zip(coeffs, forms):
        if c and f:
            row = F.table[c]
            for k, v in f.items():
                x = r.get(k, 0) ^ row[v]
                if x:
                    r[k] = x
                else:
                    r.pop(k, None)
    return r


def evalf(F, form, assign):
    r = form.get(-1, 0)
    for k, v in form.items():
        if k >= 0:
            r ^= F.table[v][assign[k]]
    return r


def columns(forms, idx):
    """Matrix (list of rows) of the forms restricted to the variables idx."""
    return [[f.get(i, 0) for i in idx] for f in forms]


# ---------------------------------------------------------------- exact tests on affine views

def zk_rank_test(F, view, wit_dirs, rand_idx):
    """Exact criterion for 'the view's distribution is the same for all witnesses in the class'.

    view: list of forms. wit_dirs: list of witness difference vectors, each a dict {var: coeff}
    (a basis of the differences of admissible witnesses). rand_idx: the randomness variables.
    For uniform randomness z the view is uniform on the coset  a0 + A w + Im(B); two witnesses give
    the same coset iff A (w - w') lies in Im(B). Returns (ok, rank B, rank [A dirs | B]).
    """
    B = columns(view, rand_idx)                      # rows = view entries
    Bt = [list(c) for c in zip(*B)] if B and B[0] else []
    rb = F.rank(Bt)
    extra = []
    for d in wit_dirs:
        extra.append([lincomb_val(F, f, d) for f in view])
    rab = F.rank(Bt + extra)
    return rab == rb, rb, rab


def lincomb_val(F, form, d):
    r = 0
    for k, v in d.items():
        c = form.get(k, 0)
        if c:
            r ^= F.table[c][v]
    return r


def enumerate_view(F, view, assign_w, rand_idx):
    """Exact distribution of the view over all values of the randomness variables: a Counter."""
    base = [evalf(F, {k: v for k, v in f.items() if k not in set(rand_idx)}, assign_w) for f in view]
    cols = [[f.get(i, 0) for f in view] for i in rand_idx]
    T = F.table
    cnt = Counter()
    for z in itertools.product(range(F.q), repeat=len(rand_idx)):
        v = base[:]
        for zi, col in zip(z, cols):
            if zi:
                row = T[zi]
                v = [a ^ row[c] for a, c in zip(v, col)]
        cnt[tuple(v)] += 1
    return cnt


def tv_distance(c1, c2):
    n1, n2 = sum(c1.values()), sum(c2.values())
    keys = set(c1) | set(c2)
    return sum(abs(c1.get(k, 0) / n1 - c2.get(k, 0) / n2) for k in keys) / 2
