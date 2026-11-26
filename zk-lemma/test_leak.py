#!/usr/bin/env python3
"""Leak detection, exact: two witnesses with the same public data, compared view against view.

A mask family can differ from the simulator of Theorem 2 for a harmless reason (Libra's mask in
characteristic 2 always has G = 0, which reveals nothing). The meaningful negative control is
witness dependence: take f1, f2 with the same claimed sum S and the same f(r), enumerate every
mask, and compare the two view distributions exactly. Distance 0 for every pair means the view
depends on the witness only through (S, f(r)); distance > 0 is a distinguisher.

Run: python3 test_leak.py

Sources and provenance (REFERENCES.md). "Libra's mask" a0 + sum_i g_i(x_i) is Published:
Xie, Zhang, Zhang, Papamanthou, Song, "Libra: Succinct Zero-Knowledge Proofs with Optimal Prover
Computation", ePrint 2019/317, Section 4.1, Construction 1 and Theorem 3 (stated over a prime field).
That it fails for a plain sum in characteristic 2 is Published: Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint
2026/391 (revision of 2026-11-16), Section 2.5; the counts computed here are this project's.
The staircase mask and the family M_u (Theorem 1, Corollaries A to C, Theorem 2) are Original (the
Ycash developers, 2026) as far as checked; the published mask for the same problem is Definition 6.1 /
Lemma 6.2 of the second paper, a different family, which these tests do not exercise.
"""
import itertools
import random
import sys
from fractions import Fraction

from gf import GF
from sumcheck import PLAIN, cube_sum_by_definition, eval_poly, mask_basis
from test_exact import distance, random_poly, real_distribution

RNG = random.Random(20261123)


def pair(F, n, d, r, W):
    degs = [d] * n
    f1, f2 = random_poly(F, n, degs), random_poly(F, n, degs)
    top, zero = tuple([1] * n), tuple([0] * n)
    f2[top] ^= cube_sum_by_definition(F, f1, n, W) ^ cube_sum_by_definition(F, f2, n, W)
    f2[zero] ^= eval_poly(F, f1, r) ^ eval_poly(F, f2, r)
    assert cube_sum_by_definition(F, f1, n, W) == cube_sum_by_definition(F, f2, n, W)
    assert eval_poly(F, f1, r) == eval_poly(F, f2, r)
    return f1, f2


def main():
    ok = True
    lines = []

    def emit(s):
        print(s, flush=True)
        lines.append(s)

    emit("# exact distance between the views of two witnesses with equal S and equal f(r) (plain sumcheck)")
    for k, grid in ((2, [(2, 1), (2, 2), (2, 3), (3, 1), (3, 2)]), (4, [(2, 1), (2, 2), (3, 1)])):
        F = GF(k)
        for (n, d) in grid:
            degs, W = [d] * n, [PLAIN] * n
            for kind in ("stair", "weighted", "libra"):
                basis = mask_basis(F, kind, n, degs, W)
                if F.q ** len(basis) > 1100000:
                    emit(f"GF(2^{k}) n={n} d={d} {kind:9s} skipped (mask space too large to enumerate)")
                    continue
                per = max(1, min(40, 4 * 10 ** 6 // F.q ** len(basis)))
                zero = pos = 0
                worst = Fraction(0)
                bad_has_one = True
                for _ in range(per):
                    r = [RNG.randrange(F.q) for _ in range(n)]
                    f1, f2 = pair(F, n, d, r, W)
                    rho = RNG.randrange(1, F.q)
                    c1, n1 = real_distribution(F, f1, basis, n, degs, r, W, rho)
                    c2, n2 = real_distribution(F, f2, basis, n, degs, r, W, rho)
                    sd = distance(F, c1, n1, c2, n2)
                    worst = max(worst, sd)
                    if sd == 0:
                        zero += 1
                    else:
                        pos += 1
                        bad_has_one &= 1 in r[:-1]
                emit(f"GF(2^{k}) n={n} d={d} {kind:9s} coeffs={len(basis):2d} pairs={per:3d} identical={zero:3d} "
                     f"distinguishable={pos:3d} maxSD={float(worst):.4f}")
                if kind == "stair":
                    ok &= pos == 0
                if kind == "weighted":
                    ok &= bad_has_one
                if kind == "libra" and (n >= 3 or d >= 2):
                    ok &= pos > 0
                if kind == "libra" and n == 2 and d == 1:
                    ok &= pos == 0          # nothing beyond (S, f(r)) to hide at this size
    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/leak.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
