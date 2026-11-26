"""Additive (subspace) evaluation domains and the novel polynomial basis.

basis b_0..b_{d-1}: F_2-independent field elements. U_i = span(b_0..b_{i-1}).
    W_i(x)    = prod_{u in U_i} (x + u)                     (subspace polynomial, F_2-linear)
    What_i(x) = W_i(x) / W_i(b_i)                           (normalised: What_i(b_i) = 1)
    X_c(x)    = prod_{i : bit i of c is set} What_i(x)      (novel basis; deg X_c = c)
Domain point of index j:  shift + sum_{bit i of j} b_i.  shift = 0 is the linear domain the pinned
stacks use; a shift outside span(b_0..b_{d-1}) gives the coset domain of Lemma E.

Source: the novel polynomial basis and the additive NTT are those of Lin, Chung, Han (FOCS 2014),
used here as described in Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields", ePrint 2025/1015, Section 1.1
("Padding in the novel basis": X_(2^l + j) = What_l * X_j); the original paper was not read.
"""


class Chain:
    def __init__(self, F, basis):
        self.F, self.basis, self.d = F, list(basis), len(basis)
        self.spans = [[0]]
        for b in self.basis:
            self.spans.append(self.spans[-1] + [u ^ b for u in self.spans[-1]])
        assert len(set(self.spans[-1])) == 1 << self.d, "basis is not independent"
        self.norm = [self.W(i, self.basis[i]) for i in range(self.d)]
        self._cache = {}

    def W(self, i, x):
        r = 1
        for u in self.spans[i]:
            r = self.F.mul(r, x ^ u)
        return r

    def What(self, i, x):
        return self.F.mul(self.W(i, x), self.F.inv(self.norm[i]))

    def point(self, j, shift=0):
        return shift ^ self.spans[self.d][j]

    def novel_row(self, x, count):
        """(X_0(x), .., X_{count-1}(x))."""
        key = (x, count)
        if key not in self._cache:
            wh, row = [], [1]
            while len(row) < count:
                i = len(wh)
                wh.append(self.What(i, x))
                row += [self.F.mul(v, wh[i]) for v in row]
            self._cache[key] = row[:count]
        return self._cache[key]

    def image(self):
        """The chain of the folded domain: q(x) = x (x + b_0), basis q(b_1), q(b_2), .."""
        b0 = self.basis[0]
        q = lambda x: self.F.mul(x, x ^ b0)
        return Chain(self.F, [q(b) for b in self.basis[1:]]), q
