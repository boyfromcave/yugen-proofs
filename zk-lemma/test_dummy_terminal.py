#!/usr/bin/env python3
"""Blinder cells on a batched, back-loaded table sumcheck with a plain sum (system A's S4).

docs/zk-system-a-gaps.md, section 3 (gap G-4). Model of `verifier/src/bus.rs::table_sumcheck`:

    target = sum_x F(x),   F(x) = sum_t W_t(x) * C_t(columns of table t at x)

over the tallest table's cube; a table of height below a variable is multiplied by that variable
(the "waiting challenge"), a table that owns the variable by the line eq(e, x) = 1 + e + x. The eq
line is inside the summand: the sum is plain (round check p(0) + p(1) = claim). Toy instance: table
A with two rows (one variable x) and columns a, b; table B with one row and column c;

    F(x) = (1 + e + x) * C_A(a(x), b(x)) + x * C_B(c)

    quadratic batch:  C_A = xi0 a(1 + a) + xi1 b(1 + a) + xi2 a b,   C_B = xi3 c(1 + c) + xi2 c
    cubic batch:      C_A = xi0 a(1 + a) + xi1 b(1 + a) + xi2 a b (1 + b) + xi2 a b,  same C_B

Blinded columns chat(y, x) = col(x) + m(y) * cell, one cell per revealed evaluation (three). Two
forms of the dummy variable y, both instances of Theorem 1 with general functionals:

    A8   m(y) = y(1 + y), lam_y(p) = (1 + tau) p(0) + tau p(1), y first; degree 2 deg C in y
    A8-T m(y) = y,        lam_y(p) = p(0),                      y last;  degree   deg C in y

The view: (G, round coefficients, mask value at the point, the three blinded evaluations). For
fixed challenges it is enumerated exactly over every blinder and every mask (the mask part as an
affine coset, `gaps_common.Canon`; one case is cross-checked against brute-force enumeration) and
compared between all witnesses with the same public target.

Negative controls: blinder off; multiplier zero at the challenge; the plain functional
p(0) + p(1) on y (the cube sum over (y, x) is 0, not the target); a mask whose y-degree is one
short; lam_y = p(0) with the multiplier y(1+y) replaced by y but y summed with weight on y = 1.

Run: python3 test_dummy_terminal.py
"""
import itertools
import random
import sys
from collections import Counter

from gf import GF
from sumcheck import (PLAIN, cube_sum_by_definition, eval_poly, mask_basis, padd, pmul, pscale,
                      real_view, round_polys, view_of)
from test_exact import enumerate_affine
from gaps_common import Canon, emitter, tv

RNG = random.Random(20261119)


def const(n, v):
    return {tuple([0] * n): v} if v else {}

def var(n, i, e=1):
    return {tuple(e if k == i else 0 for k in range(n)): 1}

def add(*ps):
    r = {}
    for p in ps:
        r = padd(r, p)
    return {k: v for k, v in r.items() if v}


def summand(F, form, cubic, wit, cells, e, xi):
    """F^(y, x) as a polynomial; variable order (y, x) for A8, (x, y) for A8-T."""
    a0, a1, b0, b1, c = wit
    yi, xi_ = (0, 1) if form == "A8" else (1, 0)
    n = 2
    X, Y = var(n, xi_), var(n, yi)
    one = const(n, 1)
    m = add(Y, var(n, yi, 2)) if form == "A8" else Y                     # multiplier m(y)
    col = lambda v0, v1, cell: add(const(n, v0), pscale(F, v0 ^ v1, X), pscale(F, cell, m))
    A, B, Cc = col(a0, a1, cells[0]), col(b0, b1, cells[1]), add(const(n, c), pscale(F, cells[2], m))
    mul = lambda p, q: pmul(F, p, q)
    CA = add(pscale(F, xi[0], mul(A, add(one, A))), pscale(F, xi[1], mul(B, add(one, A))), pscale(F, xi[2], mul(A, B)))
    if cubic:
        CA = add(CA, pscale(F, xi[2], mul(mul(A, B), add(one, B))))
    CB = add(pscale(F, xi[3], mul(Cc, add(one, Cc))), pscale(F, xi[2], Cc))
    line = add(const(n, 1 ^ e), X)
    return add(mul(line, CA), mul(X, CB))


def shape(form, cubic, tau):
    dC = 3 if cubic else 2
    if form == "A8":
        return [2 * dC, dC + 1], [(1 ^ tau, tau), PLAIN]                 # (y, x)
    return [dC + 1, dC], [PLAIN, (1, 0)]                                 # (x, y), lam_y = ev_0


def chat_values(F, form, wit, cells, r):
    a0, a1, b0, b1, c = wit
    ry, rx = (r[0], r[1]) if form == "A8" else (r[1], r[0])
    Z = F.mul(ry, 1 ^ ry) if form == "A8" else ry
    ev = lambda v0, v1: v0 ^ F.mul(v0 ^ v1, rx)
    return (ev(a0, a1) ^ F.mul(Z, cells[0]), ev(b0, b1) ^ F.mul(Z, cells[1]), c ^ F.mul(Z, cells[2])), Z


def target_of(F, wit, e, xi, cubic):
    f = summand(F, "A8-T", cubic, wit, (0, 0, 0), e, xi)
    return cube_sum_by_definition(F, f, 2, [PLAIN, (1, 0)])


def distribution(F, form, cubic, wit, e, xi, tau, r, rho, canon, degs, W, blinder=True):
    """Exact law of the view as a count table over all blinders; the mask part as its coset."""
    cnt = Counter()
    for cells in (itertools.product(range(F.q), repeat=3) if blinder else [(0, 0, 0)]):
        f = summand(F, form, cubic, wit, cells, e, xi)
        off = real_view(F, f, {}, 2, degs, r, W, rho)
        ch, _ = chat_values(F, form, wit, cells, r)
        cnt[(ch, canon.reduce(off))] += 1
    return cnt


def witnesses(F, e, xi, cubic):
    """Boolean witnesses satisfying the constraints (a Boolean, b = 0 where a = 0, c Boolean), by target."""
    groups = {}
    for wit in itertools.product((0, 1), repeat=5):
        a0, a1, b0, b1, c = wit
        if (b0 and not a0) or (b1 and not a1):
            continue
        groups.setdefault(target_of(F, wit, e, xi, cubic), []).append(wit)
    return [g for g in groups.values() if len(g) > 1]


def run(F, form, cubic, emit, cases, basis_kind="stair_u", short=False, plain_y=False):
    same = diff = same_z0 = diff_z0 = off_same = off_diff = 0
    ranks_ok = True
    for _ in range(cases):
        e, tau = RNG.randrange(F.q), RNG.randrange(F.q)
        xi = [RNG.randrange(1, F.q) for _ in range(4)]
        r = [RNG.randrange(F.q) for _ in range(2)]
        rho = RNG.randrange(1, F.q)
        degs, W = shape(form, cubic, tau)
        mdegs = degs[:]
        if short:
            mdegs[0 if form == "A8" else 1] -= 1                          # mask one degree short in y
        basis = mask_basis(F, basis_kind, 2, mdegs, W)
        gens = [view_of(F, g, 2, degs, r, W) for g in basis]
        canon = Canon(F, gens)
        ranks_ok &= canon.rank == 1 + sum(degs)
        Z = chat_values(F, form, (0,) * 5, (0, 0, 0), r)[1]
        for group in witnesses(F, e, xi, cubic):
            d = [distribution(F, form, cubic, w, e, xi, tau, r, rho, canon, degs, W) for w in group]
            eq = all(x == d[0] for x in d[1:])
            if Z:
                same += eq
                diff += not eq
            else:
                same_z0 += eq
                diff_z0 += not eq
            d = [distribution(F, form, cubic, w, e, xi, tau, r, rho, canon, degs, W, blinder=False) for w in group]
            eq = all(x == d[0] for x in d[1:])
            off_same += eq
            off_diff += not eq
    return dict(same=same, diff=diff, same_z0=same_z0, diff_z0=diff_z0, off_same=off_same, off_diff=off_diff,
                ranks_ok=ranks_ok)


def brute_force_check(F, emit):
    """One case by brute force: every mask and every blinder, no coset reduction."""
    form, cubic = "A8-T", False
    e, tau, xi, r, rho = 2, 0, [1, 2, 3, 1], [3, 2], 2
    degs, W = shape(form, cubic, tau)
    basis = mask_basis(F, "stair_u", 2, degs, W)
    gens = [view_of(F, g, 2, degs, r, W) for g in basis]
    group = max(witnesses(F, e, xi, cubic), key=len)[:3]
    tables = []
    for wit in group:
        cnt = Counter()
        for cells in itertools.product(range(F.q), repeat=3):
            f = summand(F, form, cubic, wit, cells, e, xi)
            off = real_view(F, f, {}, 2, degs, r, W, rho)
            ch, _ = chat_values(F, form, wit, cells, r)
            tag = F.pack(list(ch)) << (F.k * len(off))
            for v in enumerate_affine(F, off, gens):
                cnt[tag | v] += 1
        tables.append(cnt)
    ok = all(t == tables[0] for t in tables[1:])
    emit(f"brute force (A8-T, quadratic, GF(4), {len(group)} witnesses, all 64 blinders x 4^{len(basis)} masks each): "
         f"count tables {'equal' if ok else 'DIFFERENT'}, {len(tables[0])} distinct views")
    return ok


def main():
    emit, lines = emitter()
    ok = True
    F4, F16 = GF(2), GF(4)
    emit("# blinder cells on the batched table sumcheck (S4 model): exact view laws, all blinders, all masks")
    for F, name, cases in ((F4, "GF(4)", 60), (F16, "GF(16)", 6)):
        for form in ("A8", "A8-T"):
            for cubic in (False, True):
                if F is F16 and cubic:
                    continue
                res = run(F, form, cubic, emit, cases)
                degs, _ = shape(form, cubic, 0)
                good = res["diff"] == 0 and res["same"] > 0 and res["ranks_ok"]
                # blinder off: the evaluations are published; multiplier zero: same
                ctl = res["off_diff"] > 0 and (res["diff_z0"] > 0 or res["same_z0"] + res["diff_z0"] == 0)
                ok &= good and ctl
                emit(f"{name} {form:4} {'cubic' if cubic else 'quadratic'} batch, round degrees {degs}: "
                     f"multiplier nonzero: identical {res['same']}, different {res['diff']} (witness groups x challenges); "
                     f"multiplier zero: identical {res['same_z0']}, different {res['diff_z0']}; "
                     f"blinder off: identical {res['off_same']}, different {res['off_diff']}; "
                     f"mask rank = dim V_r: {res['ranks_ok']}")
    ok &= brute_force_check(F4, emit)

    # control: mask one degree short in y
    for form in ("A8", "A8-T"):
        res = run(F4, form, False, emit, 40, short=True)
        bad = res["diff"] > 0 and not res["ranks_ok"]
        ok &= bad
        emit(f"control, {form}: mask one degree short in y: rank below dim V_r, views differ in {res['diff']} "
             f"of {res['same'] + res['diff']} cases")

    # control: plain functional on the dummy variable: the cube sum over (y, x) is 0 for every witness
    zero = tot = nonzero_target = 0
    for _ in range(40):
        e = RNG.randrange(4)
        xi = [RNG.randrange(1, 4) for _ in range(4)]
        for group in witnesses(F4, e, xi, False):
            for wit in group:
                cells = [RNG.randrange(4) for _ in range(3)]
                f = summand(F4, "A8", False, wit, cells, e, xi)
                s = cube_sum_by_definition(F4, f, 2, [PLAIN, PLAIN])
                t = target_of(F4, wit, e, xi, False)
                tot += 1
                zero += s == 0
                nonzero_target += t != 0
    ok &= zero == tot and nonzero_target > 0
    emit(f"control: plain sum p(0) + p(1) on the dummy variable: cube sum is 0 in {zero} of {tot} cases "
         f"({nonzero_target} of them have a nonzero target): the dummy round must be weighted")

    # control: multiplier y with a functional that puts weight on y = 1: the claim is no longer the target
    wrong = tot = 0
    for _ in range(40):
        e, tau = RNG.randrange(4), RNG.randrange(1, 4)
        xi = [RNG.randrange(1, 4) for _ in range(4)]
        for group in witnesses(F4, e, xi, False):
            for wit in group:
                cells = [RNG.randrange(1, 4) for _ in range(3)]
                f = summand(F4, "A8-T", False, wit, cells, e, xi)
                s = cube_sum_by_definition(F4, f, 2, [PLAIN, (1 ^ tau, tau)])
                tot += 1
                wrong += s != target_of(F4, wit, e, xi, False)
    ok &= wrong > 0
    emit(f"control: multiplier y under eq(tau, y) with tau != 0: the sum differs from the target in {wrong} of {tot} "
         f"cases: the multiplier y needs lam_y = p(0)")

    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/dummy_terminal.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
