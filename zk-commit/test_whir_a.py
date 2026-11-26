"""System A's composed hiding opening (affine-combiner fold, F-1 layout): completeness, exact
zero-knowledge test of the whole algebraic view, uniformity on the accepting set, negative controls.
Method of test_whir.py: the honest prover runs on affine forms; rank B = rank [A dirs | B] over the
differences of witnesses with the same claim; rank B = dimension of the accepting set.
"""
import random
import sys

from ff import GF, evalf, zk_rank_test
from whir_a import config, prove, verify, free_dimension

OUT = []


def say(s):
    print(s)
    OUT.append(s)


def sample(F, levels, rnd, special=None, low_row=False):
    chal = []
    for lv in levels:
        ab = [(rnd.randrange(F.q), rnd.randrange(F.q)) for _ in range(lv.kappa)]
        if special is not None:
            ab = [special] * lv.kappa
        q = sorted(rnd.sample(range(1 << lv.dim), lv.Q))
        if low_row:
            q[0] = 0
        chal.append({"rho": rnd.randrange(1, F.q), "ab": ab, "qpos": q, "lam": rnd.randrange(1, F.q), "bc": rnd.randrange(1, F.q)})
    return chal


def case(F, name, rnd, trials, expect, wit_rows, kappas, Qs, dims, specials=(), low_row=False, t_deficit=0, shift=True, **kw):
    levels = config(F, wit_rows, kappas, Qs, dims, t_deficit)
    nw = levels[0].lanes * wit_rows
    good = comp = tamper = 0
    seen = set()
    runs = [None] * trials + list(specials)
    for sp in runs:
        W0 = [rnd.randrange(1, F.q) for _ in range(nw)]
        chal = sample(F, levels, rnd, sp, low_row)
        view, V = prove(F, levels, W0, chal, shift=shift, **kw)
        widx = V.indices("w")
        ridx = [i for i in range(V.n) if i not in set(widx)]
        assign = [rnd.randrange(F.q) for _ in range(V.n)]
        claim = F.dot(W0, [assign[i] for i in widx])
        vals = [evalf(F, f, assign) for f in view]
        acc = verify(F, levels, W0, claim, chal, vals, shift=shift)
        bad = vals[:]
        k = rnd.randrange(len(bad))
        bad[k] ^= 1
        comp += acc
        tamper += not verify(F, levels, W0, claim, chal, bad, shift=shift)
        p = 0
        dirs = [{widx[k]: 1, widx[p]: F.mul(W0[k], F.inv(W0[p]))} for k in range(1, nw)]
        ok, rb, rab = zk_rank_test(F, view, dirs, ridx)
        if expect:
            good += ok and rb == free_dimension(levels)
            seen.add((rb, free_dimension(levels)))
        else:
            good += not ok
    n = len(runs)
    lens = "/".join(str(lv.Lf) for lv in levels)
    say(f"{'ok  ' if good == n and (comp == n or kw.get('every_lane')) else 'FAIL'} {name} [folded lanes {lens}]: "
        f"completeness {comp}/{n}, one changed entry rejected {tamper}/{n}; " + (f"zero knowledge and uniformity {good}/{n}, (rank B, dim Acc) = {sorted(seen)}" if expect else f"leak {good}/{n}"))
    return good == n and (comp == n or bool(kw.get("every_lane")))


def main():
    rnd = random.Random(20261119)
    F = GF(8)
    sp = [(0, 0), (1, 0), (0, 1), (1, 1)]
    res = [
        case(F, "one level, fold 1, Q = 2, GF(256)", rnd, 120, True, 2, [1], [2], [4], specials=sp),
        case(F, "one level, fold 2, Q = 2, GF(256)", rnd, 60, True, 1, [2], [2], [5], specials=sp),
        case(F, "two levels, folds 1/1, Q = 2/2, GF(256)", rnd, 60, True, 2, [1, 1], [2, 2], [4, 4], specials=sp),
        case(F, "two levels, folds 2/1, Q = 3/2, GF(256)", rnd, 30, True, 1, [2, 1], [3, 2], [5, 5]),
        case(GF(6), "one level, fold 1, Q = 2, GF(64)", rnd, 80, True, 1, [1], [2], [4]),
        case(F, "control: no mask", rnd, 40, False, 2, [1], [2], [4], mask=False),
        case(F, "control: no base-case mask", rnd, 40, False, 2, [1], [2], [4], bc_mask=False),
        case(F, "control: one random coefficient too few", rnd, 40, False, 2, [1], [2], [4], t_deficit=1),
        case(F, "control: linear domain, an opened row in U_top", rnd, 40, False, 2, [1, 1], [2, 2], [4, 4], shift=False, low_row=True),
    ]
    # offset aligned to t only: the fold's X multiplication moves random coefficients into the aux slots
    levels = config(F, 1, [2, 1], [3, 2], [5, 5], narrow_align=True)
    rej = 0
    for _ in range(30):
        W0 = [rnd.randrange(1, F.q) for _ in range(4)]
        chal = sample(F, levels, rnd)
        view, V = prove(F, levels, W0, chal)
        assign = [rnd.randrange(F.q) for _ in range(V.n)]
        claim = F.dot(W0, [assign[i] for i in V.indices("w")])
        rej += not verify(F, levels, W0, claim, chal, [evalf(F, f, assign) for f in view])
    ok = rej >= 27
    say(f"{'ok  ' if ok else 'FAIL'} control: offset aligned to t instead of t + kappa (fold 2): honest view rejected in {rej}/30 runs (F-7)")
    res.append(ok)
    # the every-lane layout: honest views are rejected (finding F-1)
    levels = config(F, 2, [1], [2], [4])
    rej = 0
    for _ in range(60):
        W0 = [rnd.randrange(1, F.q) for _ in range(4)]
        chal = sample(F, levels, rnd)
        view, V = prove(F, levels, W0, chal, every_lane=True)
        assign = [rnd.randrange(F.q) for _ in range(V.n)]
        claim = F.dot(W0, [assign[i] for i in V.indices("w")])
        rej += not verify(F, levels, W0, claim, chal, [evalf(F, f, assign) for f in view])
    ok = rej >= 55
    say(f"{'ok  ' if ok else 'FAIL'} control: every-lane aux layout: honest view rejected in {rej}/60 runs (F-1)")
    res.append(ok)
    fails = res.count(False)
    say(f"FAILURES {fails}")
    with open("results/whir_a.txt", "w") as f:
        f.write("\n".join(OUT) + "\n")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
