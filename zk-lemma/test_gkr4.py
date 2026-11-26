#!/usr/bin/env python3
"""Radix-4 batched grand-product GKR with a dummy variable and four blinders per tree and layer.

docs/zk-system-a-gaps.md, section 5 (reference test M-2 for system A's S1, the bus GKR:
`verifier/src/bus.rs::verify_gkr_grand_products`). Trees t = 0..T-1 with 16 leaves v0_t(b, x),
b in {0,1}^2 the child index (low coordinates), x in {0,1}^2;

    v1_t(x) = prod_b v0_t(b, x),     P_t = prod_x v1_t(x)   (the published roots).

Blinded layer polynomials, dummy variable w, multiplier m(w), four blinders per tree and layer:

    vhat_t(w, b, x) = v_t(b, x) + m(w) * c_t(b),   c_t(b) = k00 + k10 b1 + k01 b2 + k11 b1 b2 .

Reduction 1 (roots -> layer 1; no x variable): claim sum_t gam1^t P_t,
    f1(w) = sum_t gam1^t prod_b v1hat_t(w, b), eq-weighted in w, Libra's mask inside the eq factor;
    the prover sends the blinded children A1[t][b] = v1hat_t(r_w, b).
The verifier draws y in F^2: Ahat_t = sum_b eq(y, b) A1[t][b] = v1_t(y) + Z1 c1_t(y).
Reduction 2 (layer 1 -> leaves): claim sum_t gam2^t v1_t(y),
    f2(w, x) = sum_t gam2^t prod_b v0hat_t(w, b, x), eq weights (zw2, y);
    head rho2 * sum_t gam2^t Ahat_t + Gt2,  Gt2 = G2 + rho2 Z1 sum_t gam2^t c1_t(y);
    the prover sends A0[t][b] = v0hat_t(r_w, b, r_x).

Two forms of the dummy variable: "A5" m(w) = w(1 + w) under eq(zw, w) (degree 8 in w);
"A5-T" m(w) = w with zw = 0, that is lam_w(p) = p(0) (degree 4 in w).

Part 1 (GF(16), three trees batched): for random trees, challenges, blinders and masks, the
honest messages pass the verifier's round checks from the stated heads and end on
rho * sum_t gam^t prod_b A[t][b] + g(r); the mask-to-view map has rank dim V_r (Corollary B); the
map blinders -> children of one tree is a bijection of F^4 when Z != 0. Controls: Z = 0; two
blinders per tree; Gt2 without the combiner's powers.
Part 2 (GF(4), one tree, exact joint law): the whole chain's view
    (G1, s1, A1, Gt2, s2, A0)
as an exact count table over all 256 x 256 blinders and all masks (as cosets), equal for witnesses
with the same root, and equal to the simulator's law (A1, A0 uniform, each mask part uniform on
the sequences passing its round checks). Controls: two blinders; blinders off.

Run: python3 test_gkr4.py

Sources and provenance (REFERENCES.md). Adapted from the zero-knowledge GKR of
Xie, Zhang, Zhang, Papamanthou, Song, "Libra: Succinct Zero-Knowledge Proofs with Optimal Prover
Computation", ePrint 2019/317, Section 4.2, equation (7) and Construction 2 (a layer mask
Z(z) * sum_w R(z_1, w) with Z vanishing on the cube). Changed here: one dummy variable with blinder
cells, because the layer claims have a Boolean last coordinate. Original (the Ycash developers, 2026)
as far as checked.
"""
import itertools
import random
import sys
from collections import Counter

from gf import GF
from sumcheck import (eval_poly, lam, mask_basis, padd, pmul, pscale, real_view, round_polys, upoly,
                      view_of, combine)
from gaps_common import Canon, emitter

RNG = random.Random(20261120)
CUBE2 = [(0, 0), (1, 0), (0, 1), (1, 1)]          # b = (b1, b2)


def ml2(F, k, y):
    """k00 + k10 y1 + k01 y2 + k11 y1 y2."""
    return k[0] ^ F.mul(k[1], y[0]) ^ F.mul(k[2], y[1]) ^ F.mul(k[3], F.mul(y[0], y[1]))


def eq2(F, y, b):
    return F.mul(1 ^ y[0] ^ b[0], 1 ^ y[1] ^ b[1])


def mult_poly(n, form):
    w1 = tuple(1 if i == 0 else 0 for i in range(n))
    w2 = tuple(2 if i == 0 else 0 for i in range(n))
    return {w1: 1, w2: 1} if form == "A5" else {w1: 1}


def Zof(F, form, rw):
    return F.mul(rw, 1 ^ rw) if form == "A5" else rw


def layer1(F, v0):
    """v1[x] for x in CUBE2 order, from leaves v0[(b, x)]."""
    out = []
    for x in CUBE2:
        p = 1
        for b in CUBE2:
            p = F.mul(p, v0[(b, x)])
        out.append(p)
    return out


def f1_poly(F, form, v1s, c1s, gam):
    """sum_t gam^t prod_b (v1_t[b] + m(w) c1_t(b)), one variable w."""
    m = mult_poly(1, form)
    tot, gp = {}, 1
    for v1, k in zip(v1s, c1s):
        prod = {(0,): 1}
        for i, b in enumerate(CUBE2):
            fac = padd({(0,): v1[i]}, pscale(F, ml2(F, k, b), m))
            prod = pmul(F, prod, fac)
        tot = padd(tot, pscale(F, gp, prod))
        gp = F.mul(gp, gam)
    return tot


def f2_poly(F, form, v0s, c0s, gam):
    """sum_t gam^t prod_b (v0_t(b, x) + m(w) c0_t(b)), variables (w, x1, x2)."""
    m = mult_poly(3, form)
    tot, gp = {}, 1
    for v0, k in zip(v0s, c0s):
        prod = {(0, 0, 0): 1}
        for b in CUBE2:
            v = [v0[(b, x)] for x in CUBE2]
            leaf = {(0, 0, 0): v[0], (0, 1, 0): v[0] ^ v[1], (0, 0, 1): v[0] ^ v[2],
                    (0, 1, 1): v[0] ^ v[1] ^ v[2] ^ v[3]}
            prod = pmul(F, prod, padd(leaf, pscale(F, ml2(F, k, b), m)))
        tot = padd(tot, pscale(F, gp, prod))
        gp = F.mul(gp, gam)
    return {k: v for k, v in tot.items() if v}


def children1(F, form, v1, k, rw):
    Z = Zof(F, form, rw)
    return [v1[i] ^ F.mul(Z, ml2(F, k, b)) for i, b in enumerate(CUBE2)]


def children0(F, form, v0, k, rw, rx):
    Z = Zof(F, form, rw)
    out = []
    for b in CUBE2:
        v = sum_ml = 0
        for x in CUBE2:
            sum_ml ^= F.mul(eq2(F, rx, x), v0[(b, x)])
        out.append(sum_ml ^ F.mul(Z, ml2(F, k, b)))
    return out


def batch(F, vals, gam):
    tot, gp = 0, 1
    for v in vals:
        tot ^= F.mul(gp, v)
        gp = F.mul(gp, gam)
    return tot


def prod(F, xs):
    p = 1
    for x in xs:
        p = F.mul(p, x)
    return p


def verify_rounds(F, view, head, degs, W, r):
    """The verifier's round checks on (G~, s_1..s_n, .); returns (passes, last claim)."""
    pos, claim = 1, head
    for j, d in enumerate(degs):
        s = view[pos:pos + d + 1]
        pos += d + 1
        if (F.mul(W[j][0], s[0]) ^ F.mul(W[j][1], upoly(F, s, 1))) != claim:
            return False, None
        claim = upoly(F, s, r[j])
    return True, claim


def shapes(form, ch):
    dw = 8 if form == "A5" else 4
    zw1 = ch["zw1"] if form == "A5" else 0
    zw2 = ch["zw2"] if form == "A5" else 0
    y = ch["y"]
    return ([dw], [(1 ^ zw1, zw1)]), ([dw, 4, 4], [(1 ^ zw2, zw2), (1 ^ y[0], y[0]), (1 ^ y[1], y[1])])


def challenges(F, nonzero_Z=True, form="A5"):
    def rw():
        while True:
            v = RNG.randrange(F.q)
            if not nonzero_Z or Zof(F, form, v):
                return v
    return dict(zw1=RNG.randrange(F.q), zw2=RNG.randrange(F.q), y=[RNG.randrange(F.q) for _ in range(2)],
                rw1=rw(), rw2=rw(), rx=[RNG.randrange(F.q) for _ in range(2)],
                gam1=RNG.randrange(1, F.q), gam2=RNG.randrange(1, F.q),
                rho1=RNG.randrange(1, F.q), rho2=RNG.randrange(1, F.q))


def honest_run(F, form, v0s, c1s, c0s, ch, g1c, g2c, bases, batched_shift=True):
    """Runs the chain; returns whether every verifier check passes."""
    (d1, W1), (d2, W2) = shapes(form, ch)
    v1s = [layer1(F, v0) for v0 in v0s]
    roots = [prod(F, v1) for v1 in v1s]
    f1 = f1_poly(F, form, v1s, c1s, ch["gam1"])
    g1 = combine(F, bases[0], g1c)
    view1 = real_view(F, f1, g1, 1, d1, [ch["rw1"]], W1, ch["rho1"])
    ok, claim = verify_rounds(F, view1, F.mul(ch["rho1"], batch(F, roots, ch["gam1"])) ^ view1[0], d1, W1, [ch["rw1"]])
    A1 = [children1(F, form, v1, k, ch["rw1"]) for v1, k in zip(v1s, c1s)]
    ok = ok and claim == F.mul(ch["rho1"], batch(F, [prod(F, a) for a in A1], ch["gam1"])) ^ view1[-1]
    Z1 = Zof(F, form, ch["rw1"])
    y = ch["y"]
    Ahat = [0] * len(v0s)
    for t, a in enumerate(A1):
        for i, b in enumerate(CUBE2):
            Ahat[t] ^= F.mul(eq2(F, y, b), a[i])
    f2 = f2_poly(F, form, v0s, c0s, ch["gam2"])
    g2 = combine(F, bases[1], g2c)
    r2 = [ch["rw2"]] + ch["rx"]
    view2 = real_view(F, f2, g2, 3, d2, r2, W2, ch["rho2"])
    corr = [ml2(F, k, y) for k in c1s]
    shift = F.mul(ch["rho2"], F.mul(Z1, batch(F, corr, ch["gam2"]) if batched_shift else batch(F, corr, 1)))
    Gt2 = view2[0] ^ shift
    ok2, claim2 = verify_rounds(F, view2, F.mul(ch["rho2"], batch(F, Ahat, ch["gam2"])) ^ Gt2, d2, W2, r2)
    A0 = [children0(F, form, v0, k, ch["rw2"], ch["rx"]) for v0, k in zip(v0s, c0s)]
    ok2 = ok2 and claim2 == F.mul(ch["rho2"], batch(F, [prod(F, a) for a in A0], ch["gam2"])) ^ view2[-1]
    return ok, ok2


def rand_tree(F):
    return {(b, x): RNG.randrange(1, F.q) for b in CUBE2 for x in CUBE2}


def part1(emit):
    F = GF(4)
    ok = True
    T = 3
    for form in ("A5", "A5-T"):
        passed = wrong_shift_fail = cases = rank_ok = 0
        for _ in range(12):
            ch = challenges(F, form=form)
            (d1, W1), (d2, W2) = shapes(form, ch)
            bases = [mask_basis(F, "libra", 1, d1, W1), mask_basis(F, "libra", 3, d2, W2)]
            r2 = [ch["rw2"]] + ch["rx"]
            rk1 = Canon(F, [view_of(F, g, 1, d1, [ch["rw1"]], W1) for g in bases[0]]).rank
            rk2 = Canon(F, [view_of(F, g, 3, d2, r2, W2) for g in bases[1]]).rank
            rank_ok += rk1 == 1 + sum(d1) and rk2 == 1 + sum(d2)
            v0s = [rand_tree(F) for _ in range(T)]
            for _ in range(3):
                c1s = [[RNG.randrange(F.q) for _ in range(4)] for _ in range(T)]
                c0s = [[RNG.randrange(F.q) for _ in range(4)] for _ in range(T)]
                g1c = [RNG.randrange(F.q) for _ in bases[0]]
                g2c = [RNG.randrange(F.q) for _ in bases[1]]
                a, b = honest_run(F, form, v0s, c1s, c0s, ch, g1c, g2c, bases)
                passed += a and b
                _, b2 = honest_run(F, form, v0s, c1s, c0s, ch, g1c, g2c, bases, batched_shift=False)
                wrong_shift_fail += not b2
                cases += 1
        (d1, _), (d2, _) = shapes(form, challenges(F, form=form))
        emit(f"GF(16), 3 trees, {form}: degrees {d1} and {d2}: every verifier check passes in {passed} of {cases} runs; "
             f"mask rank = dim V_r ({1 + sum(d1)}, {1 + sum(d2)}) at {rank_ok} of 12 challenge vectors; "
             f"control Gt2 without the combiner's powers: round check fails in {wrong_shift_fail} of {cases}")
        ok &= passed == cases and rank_ok == 12 and wrong_shift_fail > cases // 2
    # blinders -> children of one tree
    for form in ("A5", "A5-T"):
        v1 = [RNG.randrange(F.q) for _ in range(4)]
        res = {}
        for rw in range(F.q):
            img = {tuple(children1(F, form, v1, k, rw)) for k in itertools.product(range(F.q), repeat=4)}
            res.setdefault(len(img), []).append(rw)
        two = {tuple(children1(F, form, v1, (k0, k1, 0, 0), 2)) for k0 in range(F.q) for k1 in range(F.q)}
        emit(f"GF(16), {form}: four blinders -> four children: image size by r_w: "
             + ", ".join(f"{n} at r_w in {v}" for n, v in sorted(res.items()))
             + f"; control, two blinders (c0 + c1 b1): image {len(two)} of {F.q ** 4}")
        bad = [0, 1] if form == "A5" else [0]
        ok &= res.get(1) == bad and res.get(F.q ** 4) == [x for x in range(F.q) if x not in bad] and len(two) == F.q ** 2
    return ok


def joint_law(F, form, v0, ch, canons, nbl, blind=True):
    """Exact law of (A1, coset of (G1, s1, g1(r)), A0, coset of (Gt2, s2, g2(r))) over all blinders."""
    (d1, W1), (d2, W2) = shapes(form, ch)
    v1 = layer1(F, v0)
    r2 = [ch["rw2"]] + ch["rx"]
    Z1 = Zof(F, form, ch["rw1"])
    ks = [k + (0,) * (4 - nbl) for k in itertools.product(range(F.q), repeat=nbl)] if blind else [(0, 0, 0, 0)]
    part1, part2 = [], []
    for k in ks:
        f1 = f1_poly(F, form, [v1], [k], ch["gam1"])
        off = real_view(F, f1, {}, 1, d1, [ch["rw1"]], W1, ch["rho1"])
        part1.append((tuple(children1(F, form, v1, k, ch["rw1"])), canons[0].reduce(off),
                      F.mul(ch["rho2"], F.mul(Z1, ml2(F, k, ch["y"])))))
        f2 = f2_poly(F, form, [v0], [k], ch["gam2"])
        off2 = real_view(F, f2, {}, 3, d2, r2, W2, ch["rho2"])
        part2.append((tuple(children0(F, form, v0, k, ch["rw2"], ch["rx"])), off2))
    cnt = Counter()
    for a1, c1, shift in part1:
        for a0, off2 in part2:
            o = off2[:]
            o[0] ^= shift
            cnt[(a1, c1, a0, canons[1].reduce(o))] += 1
    return cnt


def simulator_law(F, form, root, ch, canons, leaf_claims_free=True):
    """A1, A0 uniform; each mask part the coset of sequences passing its checks: represented by one
    passing sequence, reduced. Built without the witness: from the root and the sampled children."""
    (d1, W1), (d2, W2) = shapes(form, ch)
    r2 = [ch["rw2"]] + ch["rx"]

    def passing(head, final_f, rho, degs, W, r):
        # a particular (G, s, g(r)) with G = 0 passing the checks from head = rho*claim + 0, ending on final
        view, claim = [0], head
        for j, d in enumerate(degs):
            s = [0] * (d + 1)
            piv = 1 if W[j][1] else 0
            s[piv] = F.mul(claim, F.inv(lam(piv, W[j])))
            view += s
            claim = upoly(F, s, r[j])
        view.append(claim ^ F.mul(rho, final_f))
        return view
    cnt = Counter()
    vals = list(itertools.product(range(F.q), repeat=4))
    p1 = {}
    for a1 in vals:
        v = passing(F.mul(ch["rho1"], root), prod(F, a1), ch["rho1"], d1, W1, [ch["rw1"]])
        ahat = 0
        for i, b in enumerate(CUBE2):
            ahat ^= F.mul(eq2(F, ch["y"], b), a1[i])
        p1[a1] = (canons[0].reduce(v), ahat)
    for a1 in vals:
        c1, ahat = p1[a1]
        for a0 in vals:
            v = passing(F.mul(ch["rho2"], ahat), prod(F, a0), ch["rho2"], d2, W2, r2)
            cnt[(a1, c1, a0, canons[1].reduce(v))] += 1
    return cnt


def part2(emit):
    F = GF(2)
    ok = True
    for form in ("A5", "A5-T"):
        eq_w = eq_sim = cases = two_diff = off_diff = 0
        for _ in range(4):
            ch = challenges(F, form=form)
            (d1, W1), (d2, W2) = shapes(form, ch)
            r2 = [ch["rw2"]] + ch["rx"]
            canons = [Canon(F, [view_of(F, g, 1, d1, [ch["rw1"]], W1) for g in mask_basis(F, "libra", 1, d1, W1)]),
                      Canon(F, [view_of(F, g, 3, d2, r2, W2) for g in mask_basis(F, "libra", 3, d2, W2)])]
            # two witnesses with the same root and different layers
            va = rand_tree(F)
            while True:
                vb = rand_tree(F)
                if prod(F, layer1(F, vb)) == prod(F, layer1(F, va)) and layer1(F, vb) != layer1(F, va):
                    break
            la, lb = joint_law(F, form, va, ch, canons, 4), joint_law(F, form, vb, ch, canons, 4)
            sim = simulator_law(F, form, prod(F, layer1(F, va)), ch, canons)
            cases += 1
            eq_w += la == lb
            eq_sim += la == sim
            two_diff += joint_law(F, form, va, ch, canons, 2) != joint_law(F, form, vb, ch, canons, 2)
            off_diff += joint_law(F, form, va, ch, canons, 4, blind=False) != joint_law(F, form, vb, ch, canons, 4, blind=False)
        emit(f"GF(4), one tree, {form}, exact joint law of the two-reduction chain over 256 x 256 blinders and all masks: "
             f"equal for two witnesses of one root in {eq_w} of {cases}; equal to the simulator's law in {eq_sim} of {cases}; "
             f"control two blinders: different in {two_diff} of {cases}; blinders off: different in {off_diff} of {cases}")
        ok &= eq_w == cases and eq_sim == cases and two_diff == cases and off_diff == cases
    return ok


def main():
    emit, lines = emitter()
    emit("# radix-4 batched GKR, dummy variable, four blinders per tree and layer")
    ok = part1(emit)
    ok &= part2(emit)
    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/gkr4.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
