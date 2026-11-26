"""Full enumeration of a complete hiding commit-and-open at toy size (no folding).

Construction W-I with zero fold rounds over GF(8): witness f in F^2, one mask constant, one
encoding-randomness coefficient, a 4-coefficient base-case mask; coset domain of 4 points; one
opened row. The verifier's whole algebraic view (G, mu, P*, the opened row, the mask column at
the row) is enumerated over EVERY value of the prover's randomness (8^6 tapes) for witnesses
with the same public claim, and the count tables are compared. The rank criterion is evaluated
on the same instances; the two methods must agree in every case.

Sources and provenance (REFERENCES.md). The base case adapts Construction 7.2 of
Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint
2026/391 (revision of 2026-11-16) (Theorem 7.1, Lemma 7.3: perfect honest-verifier zero knowledge); changed here: the mask is a
column of the last oracle (as in that paper's Section 11). The rest of W-I: see whir_i.py.
"""
import sys

from ff import GF, evalf, zk_rank_test, enumerate_view, tv_distance
from whir_i import Config, prove, verify


def case(F, kw, rho, bc, pos, W0, pairs):
    cfg = Config(F, **kw)
    chal = [{"rho": rho, "gam": [], "ood": [], "qpos": [pos], "lam": 1, "bc": bc}]
    view, V = prove(cfg, W0, chal)
    forms = [f for _, f in view]
    widx = V.indices("w")
    ridx = [i for i in range(V.n) if i not in set(widx)]
    res = []
    for w1, w2 in pairs:
        a1 = {widx[0]: w1[0], widx[1]: w1[1]}
        a2 = {widx[0]: w2[0], widx[1]: w2[1]}
        assert F.dot(W0, w1) == F.dot(W0, w2)
        d = tv_distance(enumerate_view(F, forms, a1, ridx), enumerate_view(F, forms, a2, ridx))
        ok, _, _ = zk_rank_test(F, forms, [{widx[0]: w1[0] ^ w2[0], widx[1]: w1[1] ^ w2[1]}], ridx)
        res.append((d, ok))
        # completeness on one tape
        full = [0] * V.n
        full[widx[0]], full[widx[1]] = w1
        for k, i in enumerate(ridx):
            full[i] = (3 * k + 5) % F.q
        assert verify(cfg, W0, F.dot(W0, w1), chal, [evalf(F, f, full) for f in forms])
    return res, len(ridx)


if __name__ == "__main__":
    lines = []
    out = lambda s: (print(s, flush=True), lines.append(s))
    F = GF(3)
    W0 = [3, 5]
    # pairs of witnesses with equal <f, W0>: f2 = f1 + s * (5, 3)
    pairs = [((1, 2), (1 ^ 5, 2 ^ 3)), ((0, 0), (F.mul(6, 5), F.mul(6, 3)))]
    base = dict(wit_rows=2, kappas=[0], Qs=[1], oods=[], dims=[2])
    fails = 0
    for name, kw, expect in [("hiding construction", base, True),
                             ("no base-case mask", dict(base, bc_mask=False), False),
                             ("no encoding randomness", dict(base, t_deficit=1), False),
                             ("linear domain", dict(base, shift=False), None)]:
        same = diff = disagree = cases = 0
        nz = None
        for pos in range(4):
            for bc in (1, 2, 6):
                res, nz = case(F, kw, rho=3, bc=bc, pos=pos, W0=W0, pairs=pairs)
                for d, ok in res:
                    cases += 1
                    same += d == 0
                    diff += d > 0
                    disagree += (d == 0) != ok
        if expect is True:
            good = diff == 0
        elif expect is False:
            good = diff == cases
        else:
            good = 0 < diff < cases            # linear domain: leaks exactly at rows inside U
        good = good and disagree == 0
        fails += not good
        out(f"{'PASS' if good else 'FAIL'} {name}: {cases} cases, {F.q}^{nz} tapes each; identical {same}, "
            f"different {diff}; enumeration and rank criterion disagree in {disagree}")
    out(f"FAILURES {fails}")
    open("results/basecase.txt", "w").write("\n".join(lines) + "\n")
    sys.exit(1 if fails else 0)
