"""Shared helpers for the soundness searches of construction W-I (docs/zk-wi-soundness.md).

Standard library only. Field arithmetic, additive domains and the W-I verifier are imported from
../zk-commit (read-only): the verifier attacked here is the one whose zero knowledge was tested.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zk-commit"))

from ff import GF  # noqa: E402
from additive import Chain  # noqa: E402


class Report:
    def __init__(self, name):
        self.name, self.lines, self.failures = name, [], 0

    def say(self, s=""):
        print(s)
        self.lines.append(s)

    def check(self, ok, label):
        if not ok:
            self.failures += 1
        self.say(("ok    " if ok else "FAIL  ") + label)

    def close(self):
        self.say(f"FAILURES {self.failures}")
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, self.name + ".txt"), "w") as f:
            f.write("\n".join(self.lines) + "\n")
        sys.exit(1 if self.failures else 0)


def poly_eval(F, coeffs, x):
    """Monomial-basis evaluation, coeffs[i] is the coefficient of X^i."""
    r = 0
    for c in reversed(coeffs):
        r = F.mul(r, x) ^ c
    return r


def solve(F, rows, rhs):
    """One solution x of rows * x = rhs over F (free variables set to 0), or None."""
    m, n = len(rows), len(rows[0]) if rows else 0
    A = [r[:] + [b] for r, b in zip(rows, rhs)]
    piv, rk = [], 0
    for c in range(n):
        p = next((i for i in range(rk, m) if A[i][c]), None)
        if p is None:
            continue
        A[rk], A[p] = A[p], A[rk]
        iv = F.inv(A[rk][c])
        A[rk] = [F.mul(iv, v) for v in A[rk]]
        for i in range(m):
            if i != rk and A[i][c]:
                f = A[i][c]
                A[i] = [v ^ F.mul(f, w) for v, w in zip(A[i], A[rk])]
        piv.append(c)
        rk += 1
        if rk == m:
            break
    if any(A[i][n] for i in range(rk, m)):
        return None
    x = [0] * n
    for i, c in enumerate(piv):
        x[c] = A[i][n]
    return x


def all_tuples(q, n):
    return itertools.product(range(q), repeat=n)
