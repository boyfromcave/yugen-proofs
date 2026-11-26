#!/usr/bin/env python3
"""Exact transcript distributions of the masked sumcheck, real against simulated.

For fixed public data (field, n, degrees, weights, claim S, challenges rho and r) and a fixed
witness polynomial f, the honest prover's view is a function of the mask coefficients only and
the simulator's output is a function of its random tape only. Both are enumerated in full and
compared as exact distributions (integer counts, no sampling). Equality for every (rho, r)
is perfect honest-verifier zero knowledge at that size; the statistical distance is reported
where they differ.

Enumeration uses the fact that the view is affine in the mask coefficients (packed XOR);
`selfcheck` verifies that packed enumeration against the protocol run from the definition (cube
sums of polynomial evaluations), and the simulator's affinity in its tape, before anything is
compared.

Run: python3 test_exact.py            (standard library only)

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
from collections import Counter
from fractions import Fraction

from gf import GF
from sumcheck import (PLAIN, combine, cube_sum_by_definition, eval_poly, mask_basis, padd, pscale,
                      real_adaptive, real_view, round_poly_value_by_definition, round_polys,
                      sim_randomness, simulate, simulate_adaptive, upoly, view_of)

RNG = random.Random(20261118)


def random_poly(F, n, degs):
    return {e: RNG.randrange(F.q) for e in itertools.product(*[range(d + 1) for d in degs])}


def enumerate_affine(F, offset, gens):
    """All offset + sum c_i gens_i as packed ints (a list of q^len(gens) entries)."""
    sums = [F.pack(offset)]
    for gvec in gens:
        tab = [F.pack(F.scale(c, gvec)) for c in range(F.q)]
        sums = [s ^ t for s in sums for t in tab]
    return sums


def real_distribution(F, f, basis, n, degs, r, W, rho):
    zero = {}
    offset = real_view(F, f, zero, n, degs, r, W, rho)
    gens = [view_of(F, b, n, degs, r, W) for b in basis]
    return Counter(enumerate_affine(F, offset, gens)), len(basis)


def sim_distribution(F, n, degs, W, S, rho, r, f_r):
    m = sim_randomness(degs)
    base = simulate(F, n, degs, W, S, rho, r, f_r, [0] * m)
    gens = []
    for i in range(m):
        e = [0] * m
        e[i] = 1
        v = simulate(F, n, degs, W, S, rho, r, f_r, e)
        gens.append([a ^ b for a, b in zip(v, base)])
    return Counter(enumerate_affine(F, base, gens)), m


def distance(F, cr, nr, cs, ns):
    """Statistical distance between count tables with q^nr and q^ns total mass."""
    tr, ts = F.q ** nr, F.q ** ns
    acc = Fraction(0)
    for key in set(cr) | set(cs):
        acc += abs(Fraction(cr.get(key, 0), tr) - Fraction(cs.get(key, 0), ts))
    return acc / 2


def selfcheck(F, n, degs, kind, W):
    """Packed enumeration and the simulator's affinity, against the definitions."""
    basis = mask_basis(F, kind, n, degs, W)
    for _ in range(6):
        f = random_poly(F, n, degs)
        coeffs = [RNG.randrange(F.q) for _ in basis]
        g = combine(F, basis, coeffs)
        r = [RNG.randrange(F.q) for _ in range(n)]
        rho = RNG.randrange(F.q)
        h = padd(pscale(F, rho, f), g)
        v = real_view(F, f, g, n, degs, r, W, rho)
        # the affine form used by the enumeration
        acc = real_view(F, f, {}, n, degs, r, W, rho)
        for c, b in zip(coeffs, basis):
            acc = [x ^ F.mul(c, y) for x, y in zip(acc, view_of(F, b, n, degs, r, W))]
        assert acc == v
        # the definition: G and every round polynomial as cube sums, at every field point
        assert v[0] == cube_sum_by_definition(F, g, n, W)
        pos = 1
        for j in range(n):
            coefs = v[pos:pos + degs[j] + 1]
            pos += degs[j] + 1
            for X in range(F.q):
                assert upoly(F, coefs, X) == round_poly_value_by_definition(F, h, n, r, W, j, X)
        assert v[-1] == eval_poly(F, g, r)
        # the verifier accepts
        S = cube_sum_by_definition(F, f, n, W)
        accepts(F, n, degs, W, S, rho, r, eval_poly(F, f, r), v)
        # simulator: affine in its tape, and accepted by the verifier
        m = sim_randomness(degs)
        f_r = eval_poly(F, f, r)
        base = simulate(F, n, degs, W, S, rho, r, f_r, [0] * m)
        tape = [RNG.randrange(F.q) for _ in range(m)]
        out = simulate(F, n, degs, W, S, rho, r, f_r, tape)
        acc = base[:]
        for i, t in enumerate(tape):
            e = [0] * m
            e[i] = 1
            u = simulate(F, n, degs, W, S, rho, r, f_r, e)
            acc = [x ^ F.mul(t, y ^ z) for x, y, z in zip(acc, u, base)]
        assert acc == out
        accepts(F, n, degs, W, S, rho, r, f_r, out)


def accepts(F, n, degs, W, S, rho, r, f_r, v):
    """The verifier's checks on a view."""
    from sumcheck import lam
    target = F.mul(rho, S) ^ v[0]
    pos = 1
    for j in range(n):
        coefs = v[pos:pos + degs[j] + 1]
        pos += degs[j] + 1
        l = 0
        for e, c in enumerate(coefs):
            l ^= F.mul(c, lam(e, W[j]))
        assert l == target, "round check"
        target = upoly(F, coefs, r[j])
    assert target == F.mul(rho, f_r) ^ v[-1], "final check"


def points(F, n, limit):
    allpts = F.q ** n
    if allpts <= limit:
        return list(itertools.product(range(F.q), repeat=n)), True
    special = [tuple([0] * n), tuple([1] * n), tuple([1] + [0] * (n - 1)), tuple([0] * (n - 1) + [1]),
               tuple([2] * n)]
    pts = set(special)
    while len(pts) < limit:
        pts.add(tuple(RNG.randrange(F.q) for _ in range(n)))
    return sorted(pts), False


def run_case(F, n, d, kind, weights="plain", rlimit=256, nf=2, rhos=None, max_mask=10 ** 6 + 10 ** 5,
             budget=2 * 10 ** 7):
    degs = [d] * n
    rhos = rhos if rhos is not None else [0, 1, 2]
    # bound the work: (number of r) x (mask space) x witnesses x rhos <= budget, at least 8 points
    cost = F.q ** len(mask_basis(F, kind, n, degs, [PLAIN] * n)) * nf * len(rhos)
    rlimit = max(8, min(rlimit, budget // cost))
    rs, exhaustive = points(F, n, rlimit)
    equal = cases = 0
    worst = Fraction(0)
    total_sd = Fraction(0)
    bad_r = set()
    checked = False
    for fi in range(nf):
        f = random_poly(F, n, degs)
        if weights == "plain":
            W = [PLAIN] * n
        elif weights == "eq":
            tau = [RNG.randrange(F.q) for _ in range(n)]
            if fi == 0:
                tau = [0] * n if n < 2 else [0, 1] + [RNG.randrange(F.q) for _ in range(n - 2)]
            W = [(1 ^ t, t) for t in tau]
        else:                                  # arbitrary nonzero weight pairs
            W = []
            for _ in range(n):
                w = (0, 0)
                while w == (0, 0):
                    w = (RNG.randrange(F.q), RNG.randrange(F.q))
                W.append(w)
            if fi == 0:
                W[0] = (RNG.randrange(1, F.q), 0)       # w1 = 0
        basis = mask_basis(F, kind, n, degs, W)
        if F.q ** len(basis) > max_mask:
            return None
        if not checked:
            selfcheck(F, n, degs, kind, W)
            checked = True
        S = cube_sum_by_definition(F, f, n, W)
        for r in rs:
            f_r = eval_poly(F, f, r)
            for rho in rhos:
                cr, nr = real_distribution(F, f, basis, n, degs, r, W, rho)
                cs, ns = sim_distribution(F, n, degs, W, S, rho, r, f_r)
                sd = distance(F, cr, nr, cs, ns)
                cases += 1
                total_sd += sd
                if sd == 0:
                    equal += 1
                else:
                    bad_r.add(r)
                worst = max(worst, sd)
    return dict(field=F.k, n=n, d=d, kind=kind, weights=weights, masks=len(basis), cases=cases, equal=equal,
                worst=worst, mean=total_sd / cases, exhaustive=exhaustive, nr=len(rs), bad_r=bad_r)


def fmt(res):
    ex = "all" if res["exhaustive"] else "sample"
    return (f"GF(2^{res['field']}) n={res['n']} d={res['d']} {res['weights']:7s} {res['kind']:10s} "
            f"coeffs={res['masks']:2d} r:{ex}({res['nr']}) cases={res['cases']:5d} equal={res['equal']:5d} "
            f"maxSD={float(res['worst']):.4f} meanSD={float(res['mean']):.6f}")


def adaptive_case(F, n, d, kind):
    """A deterministic adaptive verifier: challenges are functions of the messages so far."""
    degs = [d] * n
    W = [PLAIN] * n
    basis = mask_basis(F, kind, n, degs, W)
    f = random_poly(F, n, degs)
    S = cube_sum_by_definition(F, f, n, W)
    results = []
    strategies = {
        "hash": (lambda G: F.mul(G, G) ^ 1, lambda j, t: (sum(t) * 7 + j + len(t)) % F.q),
        "aim-at-1": (lambda G: 1, lambda j, t: 1 if (sum(t) + j) % 2 else t[-1]),
    }
    for name, (rho_fn, r_fn) in strategies.items():
        cr = Counter()
        for coeffs in itertools.product(range(F.q), repeat=len(basis)):
            g = combine(F, basis, coeffs)
            cr[real_adaptive(F, f, g, n, degs, W, rho_fn, r_fn)] += 1
        cs = Counter()
        m = sim_randomness(degs)
        for tape in itertools.product(range(F.q), repeat=m):
            cs[simulate_adaptive(F, n, degs, W, S, f, tape, rho_fn, r_fn)] += 1
        sd = distance(F, cr, len(basis), cs, m)
        results.append((name, sd))
    return results


def main():
    ok = True
    lines = []

    def emit(s):
        print(s, flush=True)
        lines.append(s)

    emit("# exact real-vs-simulated transcript distributions (statistical distance, exact rationals)")
    emit("## A. plain sumcheck over {0,1}^n, characteristic 2")
    grid4 = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
    grid16 = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 1)]
    for k, grid in ((2, grid4), (4, grid16)):
        F = GF(k)
        for (n, d) in grid:
            for kind in ("stair", "stair_full", "cfs", "weighted", "libra"):
                big = (F.q ** (n * d + 1)) > 70000
                rlimit = 12 if big else (256 if k == 2 else 64)
                res = run_case(F, n, d, kind, "plain", rlimit=rlimit, nf=1 if big else 2,
                               rhos=[1, 2] if big else [0, 1, 2])
                if res is None:
                    emit(f"GF(2^{k}) n={n} d={d} plain   {kind:10s} skipped (mask space too large to enumerate)")
                    continue
                emit(fmt(res))
                if kind in ("stair", "stair_full", "cfs"):
                    ok &= res["equal"] == res["cases"]
                elif kind == "weighted":
                    # equal exactly when no challenge r_k = 1 with k < n
                    expect_bad = {r for r in res["bad_r"] if 1 in r[:-1]}
                    ok &= res["bad_r"] == expect_bad
                    ok &= res["mean"] <= Fraction(n - 1, F.q) or not res["exhaustive"]
                    emit(f"    weighted: every distinguishable r has some r_k = 1, k < n: {res['bad_r'] == expect_bad};"
                         f" bound (n-1)/|F| = {float(Fraction(n - 1, F.q)):.4f}")
                elif kind == "libra":
                    # the leak: the test must detect it whenever there is something to hide
                    if (n >= 2 and d >= 2) or n >= 3:
                        ok &= res["equal"] < res["cases"]
    emit("## B. eq-weighted sumcheck (weights (1+tau_k, tau_k), reduced round messages)")
    for k, grid in ((2, [(1, 2), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2)]), (4, [(1, 3), (2, 1), (2, 2), (3, 1)])):
        F = GF(k)
        for (n, d) in grid:
            for kind in ("libra", "stair_u"):
                big = (F.q ** (n * d + 1)) > 70000
                res = run_case(F, n, d, kind, "eq", rlimit=12 if big else 64, nf=2, rhos=[1, 2] if big else [0, 1, 2])
                if res is None:
                    emit(f"GF(2^{k}) n={n} d={d} eq      {kind:10s} skipped (mask space too large to enumerate)")
                    continue
                emit(fmt(res))
                ok &= res["equal"] == res["cases"]
    emit("## C. arbitrary nonzero weight pairs, mask with lam_k(u_k) = 1")
    for k, grid in ((2, [(2, 2), (3, 1), (3, 2)]), (4, [(2, 1), (2, 2), (3, 1)])):
        F = GF(k)
        for (n, d) in grid:
            big = (F.q ** (n * d + 1)) > 70000
            res = run_case(F, n, d, "stair_u", "general", rlimit=12 if big else 64, nf=2,
                           rhos=[1, 2] if big else [0, 1, 2])
            if res is None:
                emit(f"GF(2^{k}) n={n} d={d} general stair_u    skipped (mask space too large to enumerate)")
                continue
            emit(fmt(res))
            ok &= res["equal"] == res["cases"]
    emit("## D. deterministic adaptive verifier (challenges chosen from the messages), GF(2^2), from the definition")
    F = GF(2)
    for (n, d) in ((2, 2), (3, 1), (3, 2)):
        for kind in ("stair", "weighted", "libra"):
            for name, sd in adaptive_case(F, n, d, kind):
                emit(f"GF(2^2) n={n} d={d} {kind:9s} strategy={name:9s} SD={float(sd):.4f}")
                if kind == "stair":
                    ok &= sd == 0
    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/exact.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
