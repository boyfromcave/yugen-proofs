#!/usr/bin/env python3
"""Linear hand-offs without a dummy variable (docs/zk-system-a-gaps.md, Proposition L).

A value v of committed data is revealed and then used only linearly: as a term of the claim that
heads a masked sumcheck, S = k v + rest (k, rest public). The prover sends vhat = v + b with b one
uniform element of the mask column, and Gt = G + rho k b in place of G; the verifier runs the
round checks from the head rho (k vhat + rest) + Gt.

Model: plain sumcheck, two variables, degree 2, staircase mask, GF(4) and GF(16). A witness is a
pair (v, f) with cube sum of f equal to k v + rest. Exact law of the view (vhat, Gt, s_1, s_2)
over every b and every mask (the mask part as a coset), for all witnesses in a sample with
different v and f: identical, and the honest messages pass the verifier's checks from the stated
head. The mask's final value is not in the view (variant R: it is the gadget's claim).
Controls: no blinder; G sent unshifted (the head check fails).

Run: python3 test_handoff.py
"""
import itertools
import random
import sys
from collections import Counter

from gf import GF
from sumcheck import PLAIN, cube_sum_by_definition, mask_basis, real_view, upoly, view_of
from gaps_common import Canon, emitter

RNG = random.Random(20261123)
N, DEGS, W = 2, [2, 2], [PLAIN, PLAIN]


def rand_poly(F):
    return {e: RNG.randrange(F.q) for e in itertools.product(range(3), repeat=2)}


def passes(F, view, head, r):
    pos, claim = 1, head
    for j, d in enumerate(DEGS):
        s = view[pos:pos + d + 1]
        pos += d + 1
        if s[0] ^ upoly(F, s, 1) != claim:
            return False
        claim = upoly(F, s, r[j])
    return True


def law(F, v, f, k, rho, r, canon, blind=True, shift=True):
    cnt = Counter()
    ok = True
    for b in (range(F.q) if blind else (0,)):
        off = real_view(F, f, {}, N, DEGS, r, W, rho)[:-1]          # variant R: no g(r)
        vhat = v ^ b
        if shift:
            off[0] ^= F.mul(rho, F.mul(k, b))
        rest = cube_sum_by_definition(F, f, N, W) ^ F.mul(k, v)
        ok &= passes(F, off, F.mul(rho, F.mul(k, vhat) ^ rest) ^ off[0], r)
        cnt[(vhat, canon.reduce(off))] += 1
    return cnt, ok


def main():
    emit, lines = emitter()
    good = True
    for F, name in ((GF(2), "GF(4)"), (GF(4), "GF(16)")):
        same = cases = pass_all = ctl_blind = ctl_shift = 0
        basis = mask_basis(F, "stair", N, DEGS)
        for _ in range(40):
            r = [RNG.randrange(F.q) for _ in range(N)]
            rho, k, rest = RNG.randrange(1, F.q), RNG.randrange(1, F.q), RNG.randrange(F.q)
            canon = Canon(F, [view_of(F, g, N, DEGS, r, W)[:-1] for g in basis])
            assert canon.rank == 1 + sum(DEGS)
            wits = []
            for v in range(F.q):
                f = rand_poly(F)
                # adjust the constant so that the cube sum is k v + rest: in characteristic 2 the constant
                # does not move the sum, so move the coefficient of x1 x2 (cube sum 1)
                cur = cube_sum_by_definition(F, f, N, W)
                f[(1, 1)] ^= cur ^ F.mul(k, v) ^ rest
                wits.append((v, f))
            laws = [law(F, v, f, k, rho, r, canon) for v, f in wits]
            cases += 1
            same += all(l[0] == laws[0][0] for l in laws)
            pass_all += all(l[1] for l in laws)
            off = [law(F, v, f, k, rho, r, canon, blind=False)[0] for v, f in wits]
            ctl_blind += any(o != off[0] for o in off)
            ctl_shift += not all(law(F, v, f, k, rho, r, canon, shift=False)[1] for v, f in wits)
        emit(f"{name}: {F.q} witnesses with different v, all blinders and masks: view laws identical in {same} of {cases} "
             f"challenge sets; honest checks pass from the stated head in {pass_all} of {cases}; "
             f"control no blinder: different in {ctl_blind}; control G unshifted: head check fails in {ctl_shift}")
        good &= same == cases and pass_all == cases and ctl_blind == cases and ctl_shift == cases
    emit("RESULT: " + ("PASS" if good else "FAIL"))
    with open("results/handoff.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if good else 1)


if __name__ == "__main__":
    main()
