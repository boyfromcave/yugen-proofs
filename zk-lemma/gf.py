"""GF(2^k) arithmetic, standard library only. Elements are ints in [0, 2^k); addition is XOR."""

MODULI = {
    2: 0x7,                    # x^2 + x + 1
    4: 0x13,                   # x^4 + x + 1
    8: 0x11B,                  # x^8 + x^4 + x^3 + x + 1
    128: (1 << 128) | 0x87,    # x^128 + x^7 + x^2 + x + 1
}


class GF:
    def __init__(self, k):
        self.k = k
        self.q = 1 << k
        self.mod = MODULI[k]
        self.table = None
        if k <= 8:
            self.table = [[self._slow(a, b) for b in range(self.q)] for a in range(self.q)]
            self.invt = [0] * self.q
            for a in range(1, self.q):
                self.invt[a] = self.table[a].index(1)

    def _slow(self, a, b):
        r = 0
        k, mod = self.k, self.mod
        while b:
            if b & 1:
                r ^= a
            a <<= 1
            if a >> k:
                a ^= mod
            b >>= 1
        return r

    def mul(self, a, b):
        if self.table is not None:
            return self.table[a][b]
        return self._slow(a, b)

    def pow(self, a, e):
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a):
        if a == 0:
            raise ZeroDivisionError
        if self.table is not None:
            return self.invt[a]
        return self.pow(a, self.q - 2)

    def rank(self, rows):
        """Rank of a matrix (list of rows) by Gaussian elimination."""
        rows = [row[:] for row in rows]
        rk = 0
        ncols = len(rows[0]) if rows else 0
        for c in range(ncols):
            p = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
            if p is None:
                continue
            rows[rk], rows[p] = rows[p], rows[rk]
            iv = self.inv(rows[rk][c])
            rows[rk] = [self.mul(iv, v) for v in rows[rk]]
            for i in range(len(rows)):
                if i != rk and rows[i][c]:
                    fac = rows[i][c]
                    rows[i] = [v ^ self.mul(fac, w) for v, w in zip(rows[i], rows[rk])]
            rk += 1
        return rk

    def pack(self, vec):
        r = 0
        for i, v in enumerate(vec):
            r |= v << (self.k * i)
        return r

    def scale(self, c, vec):
        return [self.mul(c, v) for v in vec]
