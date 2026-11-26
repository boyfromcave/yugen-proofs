"""Helpers shared by the system-A gap tests (docs/zk-system-a-gaps.md). Standard library only.

Exact comparison of affine-coset distributions. For fixed challenges the masked part of a view is
    offset(witness, blinders) + L * mask,        mask uniform,
with L the same for every witness and blinder. Its law is uniform on the coset offset + Im L, so
two laws are equal iff the cosets are equal. `Canon` reduces a vector modulo Im L to a canonical
representative; a whole view distribution is then the exact count table of
    (values outside the mask's part, canonical representative).
"""
from collections import Counter


class Canon:
    def __init__(self, F, gens):
        self.F = F
        rows = [g[:] for g in gens if any(g)]
        piv = []
        rk = 0
        ncols = len(gens[0]) if gens else 0
        for c in range(ncols):
            p = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
            if p is None:
                continue
            rows[rk], rows[p] = rows[p], rows[rk]
            iv = F.inv(rows[rk][c])
            rows[rk] = [F.mul(iv, v) for v in rows[rk]]
            for i in range(len(rows)):
                if i != rk and rows[i][c]:
                    fac = rows[i][c]
                    rows[i] = [v ^ F.mul(fac, w) for v, w in zip(rows[i], rows[rk])]
            piv.append(c)
            rk += 1
        self.rows, self.piv, self.rank = rows[:rk], piv, rk

    def reduce(self, vec):
        v = vec[:]
        for row, c in zip(self.rows, self.piv):
            if v[c]:
                fac = v[c]
                v = [a ^ self.F.mul(fac, b) for a, b in zip(v, row)]
        return tuple(v)


def tv(c1, c2):
    """Statistical distance of two count tables (each normalised by its own total)."""
    from fractions import Fraction
    n1, n2 = sum(c1.values()), sum(c2.values())
    return sum(abs(Fraction(c1.get(k, 0), n1) - Fraction(c2.get(k, 0), n2)) for k in set(c1) | set(c2)) / 2


def emitter():
    lines = []

    def emit(s):
        print(s, flush=True)
        lines.append(s)
    return emit, lines
