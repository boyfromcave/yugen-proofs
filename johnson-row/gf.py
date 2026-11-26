"""Small binary fields and Reed-Solomon helpers for the johnson-row tests (Yugen).

Part of `docs/binius-johnson-row.md`. Original code (the Ycash developers, 2026); textbook field
arithmetic only, no published construction is implemented here.

Elements of GF(2^m) are integers whose bits are the coefficients in the polynomial basis.
"""

from __future__ import annotations

import itertools


class GF:
    def __init__(self, m: int, modulus: int):
        self.m, self.mod, self.q = m, modulus, 1 << m
        self.exp, self.log = [0] * (2 * self.q), [0] * self.q
        x = 1
        for i in range(self.q - 1):
            self.exp[i] = x
            self.log[x] = i
            x = self._mul_slow(x, 2) if self._is_primitive_two() else None
        for i in range(self.q - 1, 2 * self.q):
            self.exp[i] = self.exp[i - (self.q - 1)]

    def _is_primitive_two(self) -> bool:
        return True  # moduli below are primitive: x generates the multiplicative group

    def _mul_slow(self, a: int, b: int) -> int:
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a & self.q:
                a ^= self.mod
        return r

    def mul(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        return self.exp[self.log[a] + self.log[b]]

    def inv(self, a: int) -> int:
        assert a != 0
        return self.exp[(self.q - 1) - self.log[a]]

    def div(self, a: int, b: int) -> int:
        return self.mul(a, self.inv(b))

    def pow(self, a: int, e: int) -> int:
        r = 1
        for _ in range(e):
            r = self.mul(r, a)
        return r

    # --- polynomials (coefficient lists, low degree first) -----------------------------------

    def peval(self, p: list[int], x: int) -> int:
        r = 0
        for c in reversed(p):
            r = self.mul(r, x) ^ c
        return r

    def interpolate(self, xs: list[int], ys: list[int]) -> list[int]:
        """Lagrange interpolation: the polynomial of degree < len(xs) through the points."""
        k = len(xs)
        out = [0] * k
        for i in range(k):
            num, den = [1], 1
            for j in range(k):
                if j == i:
                    continue
                num = [0] + num  # multiply by (X - x_j) = (X + x_j)
                for t in range(len(num) - 1):
                    num[t] ^= self.mul(num[t + 1], xs[j])
                den = self.mul(den, xs[i] ^ xs[j])
            s = self.div(ys[i], den)
            for t in range(k):
                out[t] ^= self.mul(num[t], s)
        return out

    def encode(self, p: list[int], dom: list[int]) -> tuple[int, ...]:
        return tuple(self.peval(p, x) for x in dom)


GF16 = GF(4, 0b10011)          # x^4 + x + 1
GF256 = GF(8, 0b100011101)     # x^8 + x^4 + x^3 + x^2 + 1 (primitive)


def interleaved_list(F: GF, dom: list[int], rows: list[tuple[int, ...]], k: int, A: int):
    """Exact joint list of an interleaved word: every tuple of codewords of RS[F, dom, k] (degree < k)
    that agrees with all rows on a common set of at least A >= k positions. Every such tuple
    interpolates all rows on some k-subset of that common set, so enumerating k-subsets is exhaustive.
    Returns a dict {tuple of coefficient tuples: frozenset agreement set}."""
    assert A >= k
    out = {}
    n = len(dom)
    for sub in itertools.combinations(range(n), k):
        xs = [dom[i] for i in sub]
        polys = tuple(tuple(F.interpolate(xs, [r[i] for i in sub])) for r in rows)
        if polys in out:
            continue
        agree = frozenset(i for i in range(n)
                          if all(F.peval(list(p), dom[i]) == r[i] for p, r in zip(polys, rows)))
        if len(agree) >= A:
            out[polys] = agree
    return out
