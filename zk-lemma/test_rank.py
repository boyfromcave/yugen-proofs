#!/usr/bin/env python3
"""Rank tests: the map from mask coefficients to the verifier's view has the rank the proof claims.

Theorem 1 says: for the staircase mask the linear map

    L_r : mask coefficients -> (G, coefficients of p_1..p_n, g(r))

has image exactly V_r, the space of vectors passing the verifier's checks with f = 0, of dimension
1 + sum_j d_j, for EVERY challenge vector r. Containment holds by construction (completeness), so
equality is the statement rank(L_r) = 1 + sum_j d_j. The test computes that rank exactly:
exhaustively over r for small fields, on random and adversarial r (zeros, ones) at the leaf's
sizes (n = 23..27, d = 2..3) over GF(2^8) and GF(2^128).

It also reports the rank for Libra's mask and the weighted mask, and repeats the two-witness test of
yugen-zk-b/experiments/char2_mask_sumcheck.py (difference of two witnesses' unmasked views lies in
the image) for each mask.

Run: python3 test_rank.py

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

from gf import GF
from sumcheck import PLAIN, cube_sum_by_definition, eval_poly, mask_basis, real_view, view_of

RNG = random.Random(20261119)


def image_rank(F, kind, n, degs, r, W):
    basis = mask_basis(F, kind, n, degs, W)
    return F.rank([view_of(F, b, n, degs, r, W) for b in basis]), len(basis)


def two_witness(F, kind, n, d, r, trials=4):
    """Fraction of witness pairs (same S, same f(r)) whose views are identically distributed."""
    degs = [d] * n
    W = [PLAIN] * n
    basis = mask_basis(F, kind, n, degs, W)
    rows = [view_of(F, b, n, degs, r, W) for b in basis]
    rk = F.rank(rows)
    good = 0
    for _ in range(trials):
        exps = list(itertools.product(range(d + 1), repeat=n))
        f1 = {e: RNG.randrange(F.q) for e in exps}
        f2 = {e: RNG.randrange(F.q) for e in exps}
        top, zero = tuple([1] * n), tuple([0] * n)
        f2[top] ^= cube_sum_by_definition(F, f1, n, W) ^ cube_sum_by_definition(F, f2, n, W)
        f2[zero] ^= eval_poly(F, f1, r) ^ eval_poly(F, f2, r)
        assert cube_sum_by_definition(F, f1, n, W) == cube_sum_by_definition(F, f2, n, W)
        assert eval_poly(F, f1, r) == eval_poly(F, f2, r)
        rho = RNG.randrange(1, F.q)
        t1 = real_view(F, f1, {}, n, degs, r, W, rho)
        t2 = real_view(F, f2, {}, n, degs, r, W, rho)
        delta = [a ^ b for a, b in zip(t1, t2)]
        good += F.rank(rows + [delta]) == rk
    return good, trials


def main():
    ok = True
    lines = []

    def emit(s):
        print(s, flush=True)
        lines.append(s)

    emit("# rank of the map mask coefficients -> view; claim for the staircase mask: 1 + n d for every r")
    emit("## A. exhaustive over all r in F^n")
    for k, grid in ((2, [(n, d) for n in (1, 2, 3, 4, 5) for d in (1, 2, 3)]),
                    (4, [(n, d) for n in (1, 2, 3) for d in (1, 2, 3)])):
        F = GF(k)
        for (n, d) in grid:
            degs, W = [d] * n, [PLAIN] * n
            want = 1 + n * d
            row = f"GF(2^{k}) n={n} d={d} want={want:2d} |"
            for kind in ("stair", "stair_full", "weighted", "libra"):
                ranks = {}
                bad_ok = True
                for r in itertools.product(range(F.q), repeat=n):
                    rk, nb = image_rank(F, kind, n, degs, r, W)
                    ranks[rk] = ranks.get(rk, 0) + 1
                    if kind == "weighted":
                        bad_ok &= (rk == want) == (1 not in r[:-1])
                row += f" {kind}({nb}): " + ",".join(f"{a}x{b}" for a, b in sorted(ranks.items())) + " |"
                if kind in ("stair", "stair_full"):
                    ok &= set(ranks) == {want}
                if kind == "weighted":
                    ok &= bad_ok
                if kind == "libra" and n >= 3:
                    ok &= max(ranks) < want
            emit(row)
    emit("   (entries are rank x number of r; weighted: full rank exactly when no r_k = 1 with k < n)")

    emit("## B. mixed degrees per variable, eq weights and arbitrary weights, exhaustive over r, GF(2^2)")
    F = GF(2)
    for degs in ([1, 3, 2], [5, 3], [5, 3, 3], [2, 1, 1, 3]):
        n = len(degs)
        want = 1 + sum(degs)
        got = {image_rank(F, "stair", n, degs, r, [PLAIN] * n)[0] for r in itertools.product(range(F.q), repeat=n)}
        emit(f"plain degs={degs} stair: ranks {sorted(got)} want {want}")
        ok &= got == {want}
        taus = list(itertools.product(range(F.q), repeat=n))
        if n > 3:
            taus = [t for t in taus if RNG.random() < 0.1]
        for tau in taus:
            W = [(1 ^ t, t) for t in tau]
            for kind in ("libra", "stair_u"):
                got = {image_rank(F, kind, n, degs, r, W)[0] for r in itertools.product(range(F.q), repeat=n)}
                ok &= got == {want}
        emit(f"eq    degs={degs} libra and stair_u: rank {want} for {len(taus)} tau and all r: {ok}")
        cnt = 0
        for _ in range(12):
            W = []
            for _ in range(n):
                w = (0, 0)
                while w == (0, 0):
                    w = (RNG.randrange(F.q), RNG.randrange(F.q))
                W.append(w)
            got = {image_rank(F, "stair_u", n, degs, r, W)[0] for r in itertools.product(range(F.q), repeat=n)}
            ok &= got == {want}
            cnt += 1
        emit(f"general weights degs={degs} stair_u: rank {want} for {cnt} random weight vectors and all r: {ok}")

    emit("## C. the leaf's sizes: random and adversarial r")
    for k, sizes, nrand in ((8, [(8, 2), (16, 3), (23, 2), (23, 3), (25, 2), (27, 2), (27, 3)], 12),
                            (128, [(23, 2), (27, 3)], 2)):
        F = GF(k)
        for (n, d) in sizes:
            degs, W = [d] * n, [PLAIN] * n
            want = 1 + n * d
            rs = [[0] * n, [1] * n, [i % 2 for i in range(n)], [1] + [0] * (n - 1)] if k == 8 else [[1] * n]
            rs += [[RNG.randrange(F.q) for _ in range(n)] for _ in range(nrand)]
            got = set()
            for r in rs:
                got.add(image_rank(F, "stair", n, degs, r, W)[0])
            lib = image_rank(F, "libra", n, degs, rs[-1], W)
            emit(f"GF(2^{k}) n={n} d={d} stair: ranks {sorted(got)} over {len(rs)} r, want {want};"
                 f" libra rank {lib[0]} of {lib[1]} coefficients")
            ok &= got == {want}
            ok &= lib[0] < want
    F = GF(8)
    for (n, d) in ((8, 2), (10, 3)):
        degs, W = [d] * n, [PLAIN] * n
        r_good = [RNG.randrange(2, F.q) for _ in range(n)]
        r_bad = r_good[:]
        r_bad[2] = 1
        a, b = image_rank(F, "weighted", n, degs, r_good, W)[0], image_rank(F, "weighted", n, degs, r_bad, W)[0]
        emit(f"GF(2^8) n={n} d={d} weighted: rank {a} (no r_k = 1), rank {b} (r_3 = 1), want {1 + n * d}")
        ok &= a == 1 + n * d and b < a

    emit("## D. two witnesses with equal sum and equal f(r): identically distributed views (GF(2^8), random r)")
    F = GF(8)
    for kind in ("stair", "weighted", "libra"):
        for (n, d) in ((2, 1), (3, 1), (2, 2), (3, 2), (4, 2), (3, 3), (5, 2)):
            good = tot = 0
            for _ in range(10):
                r = [RNG.randrange(2, F.q) for _ in range(n)]
                g, t = two_witness(F, kind, n, d, r)
                good += g
                tot += t
            emit(f"{kind:9s} n={n} d={d}: {good}/{tot}")
            if kind in ("stair", "weighted"):
                ok &= good == tot
            if kind == "libra" and (n >= 3 or d >= 2):
                ok &= good == 0
    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/rank.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
