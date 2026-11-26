"""GF(2^8) = GF(2)[x] / (x^8 + x^4 + x^3 + x + 1) with its subfields GF(4) and GF(16).

Exact arithmetic for the toy tests of docs/binius-extension-challenges.md. An element is an int
0..255; addition is XOR. A subfield is the set of fixed points of a power of the Frobenius map,
so GF(4) < GF(16) < GF(256) are literal subsets and a "base-field" value is an "extension" value
without conversion, as GHASH sits inside GhashSq256b in the vendored code.
"""

from itertools import product

_EXP = [0] * 510
_LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x ^= (_x << 1) ^ (0x11B if _x & 0x80 else 0)  # multiply by the generator 3 = x + 1
    _x &= 0xFF
for _i in range(255, 510):
    _EXP[_i] = _EXP[_i - 255]


def mul(a, b):
    return 0 if a == 0 or b == 0 else _EXP[_LOG[a] + _LOG[b]]


def inv(a):
    assert a != 0
    return _EXP[255 - _LOG[a]]


def frob(a, m=1):
    """a^(2^m)."""
    for _ in range(m):
        a = mul(a, a)
    return a


def dot(xs, ys):
    acc = 0
    for x, y in zip(xs, ys):
        acc ^= mul(x, y)
    return acc


class Field:
    """The subfield of GF(256) with 2^deg elements, with a GF(2)-basis that extends `sub`'s."""

    def __init__(self, deg, sub=None):
        assert deg in (1, 2, 4, 8)
        self.deg = deg
        self.kappa = deg.bit_length() - 1
        self.elems = [a for a in range(256) if frob(a, deg) == a]
        assert len(self.elems) == 2**deg
        basis = list(sub.basis) if sub else []
        span = {0}
        for b in basis:
            span |= {s ^ b for s in span}
        for a in self.elems:
            if a not in span:
                basis.append(a)
                span |= {s ^ a for s in span}
        assert len(basis) == deg and span == set(self.elems)
        self.basis = basis
        self.coords = {}
        for bits in product((0, 1), repeat=deg):
            v = 0
            for bit, b in zip(bits, basis):
                if bit:
                    v ^= b
            self.coords[v] = bits

    def bits(self, a):
        """Coordinates of `a` in the basis (a tuple of 0/1)."""
        return self.coords[a]

    def __contains__(self, a):
        return a in self.coords


F4 = Field(2)
F16 = Field(4, F4)
F256_over_4 = Field(8, F16)  # basis extends GF(16)'s, which extends GF(4)'s
PAIRS = [(F4, F16), (F4, F256_over_4), (F16, F256_over_4)]  # (L, K): packing field, challenge field


def eq_point(r, j):
    """eq(r, j) for the bit string of the integer j, low bit first; char 2: r if bit else 1 + r."""
    acc = 1
    for k, rk in enumerate(r):
        acc = mul(acc, rk if (j >> k) & 1 else 1 ^ rk)
    return acc


def eq_expand(r):
    return [eq_point(r, j) for j in range(2 ** len(r))]


def eq2(x, y):
    """The multilinear eq(x, y) = prod (x_k y_k + (1 + x_k)(1 + y_k)), which in characteristic 2
    is prod (1 + x_k + y_k)."""
    acc = 1
    for a, b in zip(x, y):
        acc = mul(acc, 1 ^ a ^ b)
    return acc
