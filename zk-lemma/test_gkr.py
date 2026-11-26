#!/usr/bin/env python3
"""Exact test of the masked GKR layer reduction (docs/zk-masked-sumcheck.md, section 7).

Instance: a product tree with 4 leaves. v0(x, b) is the leaf layer (multilinear), v1(b) =
v0(b, 0) * v0(b, 1), output P = v1(0) * v1(1) (public).

Blinded layer polynomial (dummy variable y, two blinding constants c0, c1 per layer):

    v1^(y, b) = v1(b) + y (1 + y) (c0 + c1 b)            equal to v1 for y in {0, 1}

Reduction 1 (output -> layer 1), a masked sumcheck in the one variable y:
    P = sum_y F1(y),  F1 = eq(zy1, y) v1^(y, 0) v1^(y, 1)                (degree 5)
    view: G1, s1, then the blinded claims A0 = v1^(ry, 0), A1 = v1^(ry, 1).
The verifier picks alpha; A^ = (1 + alpha) A0 + alpha A1 = v1(alpha) + Z (c0 + alpha c1),
Z = ry (1 + ry).
Reduction 2 (layer 1 -> leaves), a masked sumcheck in (y, x):
    v1(alpha) = sum_{y,x} F2,  F2 = eq(zy2, y) eq(alpha, x) v0(x, 0) v0(x, 1)   (degrees 1, 3)
    the prover sends G2~ = G2 + rho2 Z (c0 + alpha c1) in place of G2; the verifier checks
    lam(s_y) = rho2 A^ + G2~. The leaf claims L0 = v0(rx, 0), L1 = v0(rx, 1) end the chain
    (in the full system they are evaluations of blinded committed columns; here the simulator
    is given them).

Simulator, given P, L0, L1 and the challenges: A0, A1 uniform; (G1, s1) by the sumcheck
simulator with claim P and final value eq * A0 * A1; (G2~, s_y, s_x) by the sumcheck simulator
with claim A^ and final value eq * eq * L0 * L1.

Exactness. For fixed witness and challenges the real view is a function of (c, g1, g2) with the
three parts independent and uniform. The test checks, for every c in F^2:
  - c -> (A0, A1) is a bijection of F^2 (when Z != 0);
  - the distribution of (G1, s1, g1(ry)) over all g1 equals the simulator's for A = A(c);
  - the distribution of (G2~, s_y, s_x, g2(r')) over all g2 equals the simulator's for A = A(c).
Together these are equality of the joint distributions. Negative controls: Z = 0, and blinder off.

Run: python3 test_gkr.py

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

from gf import GF
from sumcheck import PLAIN, eval_poly, mask_basis, pmul, pscale, padd
from test_exact import real_distribution, sim_distribution

RNG = random.Random(20261122)


def eq1(n, var, z):
    """eq(z, x_var) = (1 + z) + x_var in characteristic 2."""
    e0 = tuple([0] * n)
    e1 = tuple(1 if i == var else 0 for i in range(n))
    return {e0: 1 ^ z, e1: 1}


def instance(F, v0, c, ch):
    """Polynomials and blinded claims for leaves v0[(x, b)], blinder c, challenges ch."""
    zy1, rho1, ry, alpha, zy2, rho2, ry2, rx = ch
    v1 = [F.mul(v0[(b, 0)], v0[(b, 1)]) for b in (0, 1)]
    P = F.mul(v1[0], v1[1])
    # reduction 1, one variable y
    blind = [c[0], c[0] ^ c[1]]                                   # c0 + c1 b for b = 0, 1
    vh = [{(0,): v1[b], (1,): blind[b], (2,): blind[b]} for b in (0, 1)]
    F1 = pmul(F, eq1(1, 0, zy1), pmul(F, vh[0], vh[1]))
    A = [eval_poly(F, vh[b], [ry]) for b in (0, 1)]
    Z = F.mul(ry, 1 ^ ry)
    # reduction 2, variables (y, x)
    leaf = [{(0, 0): v0[(0, b)], (0, 1): v0[(0, b)] ^ v0[(1, b)]} for b in (0, 1)]   # v0(x, b)
    F2 = pmul(F, pmul(F, eq1(2, 0, zy2), eq1(2, 1, alpha)), pmul(F, leaf[0], leaf[1]))
    L = [eval_poly(F, leaf[b], [0, rx]) for b in (0, 1)]
    shift = F.mul(rho2, F.mul(Z, c[0] ^ F.mul(alpha, c[1])))      # G2~ = G2 + shift
    return dict(P=P, F1=F1, F2=F2, A=A, Z=Z, L=L, shift=shift, v1=v1)


def check(F, v0, ch, blinder=True):
    zy1, rho1, ry, alpha, zy2, rho2, ry2, rx = ch
    b1 = mask_basis(F, "stair", 1, [5])
    b2 = mask_basis(F, "stair", 2, [1, 3])
    images = set()
    parts_equal = True
    cs = list(itertools.product(range(F.q), repeat=2)) if blinder else [(0, 0)]
    for c in cs:
        I = instance(F, v0, c, ch)
        A0, A1 = I["A"]
        images.add((A0, A1))
        # part 1
        real1, n1 = real_distribution(F, I["F1"], b1, 1, [5], [ry], [PLAIN], rho1)
        f_r1 = F.mul(1 ^ zy1 ^ ry, F.mul(A0, A1))                 # eq(zy1, ry) A0 A1, from the view
        sim1, m1 = sim_distribution(F, 1, [5], [PLAIN], I["P"], rho1, [ry], f_r1)
        parts_equal &= n1 == m1 and real1 == sim1
        # part 2
        real2, n2 = real_distribution(F, I["F2"], b2, 2, [1, 3], [ry2, rx], [PLAIN] * 2, rho2)
        real2 = {key ^ I["shift"]: cnt for key, cnt in real2.items()}     # entry 0 is G2 -> G2~
        Ahat = F.mul(1 ^ alpha, A0) ^ F.mul(alpha, A1)
        f_r2 = F.mul(F.mul(1 ^ zy2 ^ ry2, 1 ^ alpha ^ rx), F.mul(I["L"][0], I["L"][1]))
        sim2, m2 = sim_distribution(F, 2, [1, 3], [PLAIN] * 2, Ahat, rho2, [ry2, rx], f_r2)
        parts_equal &= n2 == m2 and real2 == dict(sim2)
    return parts_equal, len(images), I


def main():
    ok = True
    lines = []

    def emit(s):
        print(s, flush=True)
        lines.append(s)

    F = GF(2)
    emit("# masked GKR layer chain, GF(2^2), exact")
    good = bad = 0
    zero_Z_leaks = zero_Z = 0
    for _ in range(6):
        v0 = {(x, b): RNG.randrange(F.q) for x in (0, 1) for b in (0, 1)}
        for _ in range(24):
            ch = [RNG.randrange(F.q) for _ in range(8)]
            if ch[2] in (0, 1):                 # Z = 0: the excluded event, counted separately
                eqp, nimg, _ = check(F, v0, ch)
                zero_Z += 1
                zero_Z_leaks += nimg == 1
                continue
            eqp, nimg, _ = check(F, v0, ch)
            if eqp and nimg == F.q ** 2:
                good += 1
            else:
                bad += 1
    emit(f"blinded chain, Z != 0: joint distribution equal to the simulator's in {good} of {good + bad} "
         f"(witness, challenge) cases, each over all 16 blinders and all 4^6 + 4^5 mask polynomials")
    emit(f"excluded event ry in {{0,1}} (Z = 0): {zero_Z_leaks} of {zero_Z} cases publish v1(0), v1(1) unblinded")
    ok &= bad == 0 and good > 0 and zero_Z_leaks == zero_Z
    # negative control: without the blinder two witnesses with the same public data are told apart
    told = tot = 0
    for _ in range(200):
        ch = [RNG.randrange(F.q) for _ in range(8)]
        va = {(x, b): RNG.randrange(1, F.q) for x in (0, 1) for b in (0, 1)}
        vb = dict(va)
        # swap the two halves' roles: same P; keep leaf claims by brute search for a second witness
        cands = []
        for vals in itertools.product(range(F.q), repeat=4):
            vb = dict(zip(sorted(va), vals))
            Ia, Ib = instance(F, va, (0, 0), ch), instance(F, vb, (0, 0), ch)
            if Ia["P"] == Ib["P"] and Ia["L"] == Ib["L"] and Ia["v1"] != Ib["v1"]:
                cands.append(vb)
        if not cands:
            continue
        vb = cands[0]
        tot += 1
        told += instance(F, va, (0, 0), ch)["A"] != instance(F, vb, (0, 0), ch)["A"]
        if tot >= 40:
            break
    emit(f"blinder off: {told} of {tot} witness pairs with equal P and equal leaf claims have different layer claims")
    ok &= told == tot and tot > 0
    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/gkr.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
