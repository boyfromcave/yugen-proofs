"""Hiding WHIR-style opening (construction W-I): completeness, exact zero-knowledge test of the
whole algebraic view, and negative controls.

For each challenge tuple the honest prover is run on affine forms; then
  * completeness: the forms are evaluated on random secrets and the concrete verifier accepts;
    a view with one entry changed is rejected or was not checked (reported);
  * zero knowledge (exact): rank B = rank [A dirs | B], where dirs spans the differences of
    witnesses with the same public claim <f, W0>: the view's distribution is then the same for
    all of them;
  * uniformity: rank B equals the dimension of the set of accepting views, so the view is
    uniform on that set (the simulator samples it without the witness).
Negative controls: linear domain with a row in U, one randomness coefficient too few, no
sumcheck mask, Libra's mask, no base-case mask.
"""
import random
import sys

from ff import GF, evalf, zk_rank_test
from whir_i import Config, prove, verify, free_dimension, sample_challenges


def claim_dirs(V, W0):
    widx = V.indices("w")
    p = next(k for k, w in enumerate(W0) if w)
    return widx, p


def run_case(F, name, kw, trials, rnd, out, expect_zk=True, force_low_row=False, specials=()):
    cfg = Config(F, **kw)
    nw = cfg.levels[0].lanes * cfg.wit_rows
    zk_ok = zk_bad = uni_ok = comp_ok = 0
    rb_seen = set()
    tuples = [None] * trials + list(specials)
    for sp in tuples:
        W0 = [rnd.randrange(1, F.q) for _ in range(nw)]
        chal = sample_challenges(cfg, rnd, sp)
        if force_low_row:
            chal[0]["qpos"][0] = 0
            chal[0]["qpos"] = sorted(set(chal[0]["qpos"]))
            if len(chal[0]["qpos"]) < cfg.levels[0].Q:
                continue
        view, V = prove(cfg, W0, chal)
        forms = [f for _, f in view]
        widx = V.indices("w")
        ridx = [i for i in range(V.n) if i not in set(widx)]
        # completeness
        assign = [rnd.randrange(F.q) for _ in range(V.n)]
        claim = F.dot(W0, [assign[i] for i in widx])
        vals = [evalf(F, f, assign) for f in forms]
        acc = verify(cfg, W0, claim, chal, vals)
        comp_ok += acc
        # differences of witnesses with the same claim: kernel of W0
        p = next(k for k, w in enumerate(W0) if w)
        dirs = []
        for k in range(nw):
            if k != p:
                dirs.append({widx[k]: 1, widx[p]: F.mul(W0[k], F.inv(W0[p]))})
        ok, rb, rab = zk_rank_test(F, forms, dirs, ridx)
        zk_ok += ok
        zk_bad += not ok
        rb_seen.add(rb)
        uni_ok += rb == free_dimension(cfg)
    n = zk_ok + zk_bad
    verdict = "PASS" if (zk_bad == 0) == expect_zk and (not expect_zk or (uni_ok == n and comp_ok == n)) else "FAIL"
    if not expect_zk and zk_bad == 0:
        verdict = "FAIL"
    out(f"{verdict} {name}: tuples {n}, verifier accepts {comp_ok}, hiding {zk_ok}, leaking {zk_bad}, "
        f"uniform on accepting set {uni_ok}, rank B {sorted(rb_seen)}, accepting dimension {free_dimension(cfg)}, "
        f"secrets w={nw} z={len(ridx)}, view entries {len(forms)}")
    return verdict == "FAIL"


def tamper_check(F, kw, rnd, out):
    """Every view entry is bound by some check: changing one entry makes the verifier reject."""
    cfg = Config(F, **kw)
    nw = cfg.levels[0].lanes * cfg.wit_rows
    W0 = [rnd.randrange(1, F.q) for _ in range(nw)]
    chal = sample_challenges(cfg, rnd)
    view, V = prove(cfg, W0, chal)
    assign = [rnd.randrange(F.q) for _ in range(V.n)]
    claim = F.dot(W0, [assign[i] for i in V.indices("w")])
    vals = [evalf(F, f, assign) for _, f in view]
    assert verify(cfg, W0, claim, chal, vals)
    rej = 0
    for k in range(len(vals)):
        v2 = vals[:]
        v2[k] ^= 1
        rej += not verify(cfg, W0, claim, chal, v2)
    out(f"tamper: {rej}/{len(vals)} single-entry changes rejected; wrong claim rejected: "
        f"{not verify(cfg, W0, claim ^ 1, chal, vals)}")
    return 0 if rej == len(vals) else 1


if __name__ == "__main__":
    lines = []
    out = lambda s: (print(s, flush=True), lines.append(s))
    rnd = random.Random(20261119)
    F8, F6, F4 = GF(8), GF(6), GF(4)
    two = dict(wit_rows=2, kappas=[2, 1], Qs=[2, 2], oods=[1], dims=[4, 4])
    three = dict(wit_rows=2, kappas=[1, 1, 1], Qs=[2, 1, 2], oods=[1, 1], dims=[4, 4, 4])
    one = dict(wit_rows=1, kappas=[1], Qs=[1], oods=[], dims=[3])
    big = dict(wit_rows=4, kappas=[2, 2], Qs=[3, 2], oods=[2], dims=[5, 5])
    adv = [(0,), (1,), (0, 1), (1, 0), (1, 1), (0, 0)]
    fails = 0
    fails += run_case(F8, "two levels (folds 2,1), GF(2^8)", two, 150, rnd, out, specials=adv)
    fails += run_case(F8, "three levels (folds 1,1,1), GF(2^8)", three, 100, rnd, out, specials=adv)
    fails += run_case(F8, "two levels (folds 2,2), 3+2 queries, 2 OOD, GF(2^8)", big, 40, rnd, out, specials=adv)
    fails += run_case(F4, "one level (fold 1), GF(2^4)", one, 200, rnd, out, specials=adv)
    fails += run_case(F6, "two levels, GF(2^6)", dict(wit_rows=1, kappas=[1, 1], Qs=[1, 1], oods=[1], dims=[3, 3]),
                      150, rnd, out, specials=adv)
    fails += tamper_check(F8, two, rnd, out)
    out("negative controls (each must leak):")
    fails += run_case(F8, "linear domain, a row inside U", dict(two, shift=False), 60, rnd, out,
                      expect_zk=False, force_low_row=True)
    fails += run_case(F8, "one randomness coefficient too few", dict(two, t_deficit=1), 60, rnd, out, expect_zk=False)
    fails += run_case(F8, "no sumcheck mask", dict(two, mask="none"), 60, rnd, out, expect_zk=False)
    fails += run_case(F8, "Libra's mask in a 2-round batch", dict(two, mask="libra"), 60, rnd, out, expect_zk=False)
    fails += run_case(F8, "no base-case mask", dict(two, bc_mask=False), 60, rnd, out, expect_zk=False)
    out(f"FAILURES {fails}")
    open("results/whir.txt", "w").write("\n".join(lines) + "\n")
    sys.exit(1 if fails else 0)
