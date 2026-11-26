#!/usr/bin/env python3
"""Bit-slice evaluations of a packed column, and their blinding (docs/zk-system-a-gaps.md, section 2).

System A's Keccak reduction ends on 64 scalars, the "slices" of the committed column q_keccak:

    s_i = sum_u eq(point, u) * bit_i(q[u]),   i < 64,   q[u] in K = GF(2^64), s_i in F.

They are F_2-linear, not K-linear, in the committed cells. The ring switch turns the 64 claims into
one K-linear claim: with Phi(v) = sum_k c_k v^(2^k) and q[u] = sum_i x^i bit_i(q[u]),

    sum_i x^i Phi(s_i) = sum_u Phi(eq(point, u)) q[u] .

Construction G-3: a block of [F : F_2] committed uniform K-cells B_j and a fixed F_2-basis
(omega_j) of F; slice i has the blinder b_i = sum_j omega_j bit_i(B_j), an element of F, and the
prover reveals shat_i = s_i + Z b_i (Z the public nonzero multiplier of the dummy variable). The
ring switch runs unchanged on the cells (q, B) with the weights (eq(point, .), Z omega):

    sum_i x^i Phi(shat_i) = sum_u Phi(eq(point, u)) q[u] + sum_j Phi(Z omega_j) B_j .

Toy model: K = GF(4) = {0, 1, 6, 7} inside F = GF(16), K-basis {1, x} with x = 6 (two slices),
four cells of q, four blinder cells, omega = {1, 6, 2, 12} = {theta0^a theta1^b}, theta = (6, 2).

  1. unblinded: F_2-rank of (bits of q) -> slices against that of the column evaluation;
  2. blinded: for every witness, B -> (shat_0, shat_1) is a bijection of K^4 onto F^2 (exact,
     all 256 blinder blocks, all 256 witnesses);
  3. the ring-switch identity above, all witnesses and blinder blocks at sampled challenges;
  controls: Z = 0; three blinder cells; a dependent weight set; one F element shared by the slices.

Run: python3 test_slices.py
"""
import itertools
import random
import sys
from collections import Counter

from gf import GF
from gaps_common import emitter

RNG = random.Random(20261121)
F = GF(4)
KEL = [0, 1, 6, 7]
X = 6
BITS = {0: (0, 0), 1: (1, 0), 6: (0, 1), 7: (1, 1)}       # k = bit_0 + bit_1 * x
OMEGA = [1, 6, 2, F.mul(6, 2)]                             # subset products of theta = (6, 2)


def f2_rank(vals):
    v = list(vals)
    r = 0
    while v:
        p = v.pop()
        if not p:
            continue
        r += 1
        hb = p.bit_length() - 1
        v = [a ^ p if a >> hb & 1 else a for a in v]
    return r


def eq_weights(p):
    return [F.mul(1 ^ p[0] ^ u0, 1 ^ p[1] ^ u1) for u1 in (0, 1) for u0 in (0, 1)]


def slices(w, cells):
    return [_dot_bits(w, cells, i) for i in (0, 1)]


def _dot_bits(w, cells, i):
    s = 0
    for wu, c in zip(w, cells):
        if BITS[c][i]:
            s ^= wu
    return s


def phi(c, v):
    return F.mul(c[0], v) ^ F.mul(c[1], F.mul(v, v))


def main():
    emit, lines = emitter()
    ok = True
    emit("# bit slices of a packed column: K = GF(4) in F = GF(16), two slices, four cells")
    emit(f"F_2-rank of the blinder basis omega = {OMEGA}: {f2_rank(OMEGA)} of 4")
    ok &= f2_rank(OMEGA) == 4
    wits = list(itertools.product(KEL, repeat=4))
    blocks = list(itertools.product(KEL, repeat=4))

    # 1. what the unblinded slices reveal
    hist = Counter()
    for _ in range(200):
        p = [RNG.randrange(16) for _ in range(2)]
        w = eq_weights(p)
        n_slice = len({tuple(slices(w, q)) for q in wits})
        n_eval = len({slices(w, q)[0] ^ F.mul(X, slices(w, q)[1]) for q in wits})
        hist[(f2_rank(w), n_slice, n_eval)] += 1
    for (rk, ns, ne), c in sorted(hist.items()):
        emit(f"unblinded, {c} points with F_2-rank {rk} of the weights: the slices take {ns} values over the 256 "
             f"witnesses (2 x {rk} bits), the column evaluation {ne}")
    ok &= all(ns == 4 ** rk and ne <= 16 for (rk, ns, ne) in hist)

    # 2. blinded: bijection for every witness
    bij = tot = 0
    for _ in range(6):
        p = [RNG.randrange(16) for _ in range(2)]
        Z = RNG.randrange(1, 16)
        w = eq_weights(p)
        zw = [F.mul(Z, o) for o in OMEGA]
        pads = [tuple(slices(zw, B)) for B in blocks]
        full = len(set(pads)) == 256
        for q in wits:
            s = slices(w, q)
            tot += 1
            bij += full and len({(s[0] ^ a, s[1] ^ b) for a, b in pads}) == 256
    emit(f"blinded, Z != 0: B -> (shat_0, shat_1) is a bijection of K^4 onto F^2 for {bij} of {tot} (witness, challenge) "
         f"cases: the two slices are uniform and independent")
    ok &= bij == tot

    # 3. ring-switch identity on the cells (q, B)
    good = tot = 0
    for _ in range(8):
        p = [RNG.randrange(16) for _ in range(2)]
        Z = RNG.randrange(1, 16)
        c = [RNG.randrange(16) for _ in range(2)]
        w = eq_weights(p)
        zw = [F.mul(Z, o) for o in OMEGA]
        pw, pz = [phi(c, a) for a in w], [phi(c, a) for a in zw]
        for q in RNG.sample(wits, 40):
            for B in RNG.sample(blocks, 40):
                sh = [a ^ b for a, b in zip(slices(w, q), slices(zw, B))]
                lhs = phi(c, sh[0]) ^ F.mul(X, phi(c, sh[1]))
                rhs = 0
                for a, cell in zip(pw + pz, list(q) + list(B)):
                    rhs ^= F.mul(a, cell)
                tot += 1
                good += lhs == rhs
    emit(f"ring switch on the blinded slices: sum_i x^i Phi(shat_i) = <Phi(eq), q> + <Phi(Z omega), B> in {good} of {tot} cases")
    ok &= good == tot
    # the tensor form of the weight: Phi(Z omega_j) = sum_k c_k Z^(2^k) prod_l (theta_l^(2^k))^(j_l)
    tens = True
    for _ in range(50):
        Z, c = RNG.randrange(16), [RNG.randrange(16) for _ in range(2)]
        for j, (j0, j1) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
            v = 0
            for k in (0, 1):
                t = F.mul(c[k], F.pow(Z, 1 << k))
                if j0:
                    t = F.mul(t, F.pow(6, 1 << k))
                if j1:
                    t = F.mul(t, F.pow(2, 1 << k))
                v ^= t
            tens &= v == phi(c, F.mul(Z, OMEGA[j]))
    emit(f"product form of the blinder weights: {tens}")
    ok &= tens

    # controls
    p, w = [5, 9], eq_weights([5, 9])
    def law(q, zw, blocks_):
        s = slices(w, q)
        return Counter((s[0] ^ a, s[1] ^ b) for a, b in (tuple(slices(zw, B)) for B in blocks_))
    qa, qb = wits[27], wits[200]
    assert slices(w, qa) != slices(w, qb)
    c0 = law(qa, [0] * 4, blocks) != law(qb, [0] * 4, blocks)
    emit(f"control, Z = 0: laws of two witnesses differ: {c0}")
    three = [OMEGA[0], OMEGA[1], OMEGA[2]]
    b3 = list(itertools.product(KEL, repeat=3))
    l3 = law(qa, three, b3)
    emit(f"control, three blinder cells (3 bits a slice against 4): support {len(l3)} of 256; "
         f"some witness pair has different laws: {any(law(q, three, b3) != l3 for q in wits)}")
    dep = [1, 6, 7, 2]
    ld = law(qa, dep, blocks)
    emit(f"control, dependent weights {dep} (F_2-rank {f2_rank(dep)}): support {len(ld)} of 256; "
         f"some witness pair has different laws: {any(law(q, dep, blocks) != ld for q in wits)}")
    def law_shared(q):
        s = slices(w, q)
        return Counter((s[0] ^ b, s[1] ^ b) for b in range(16))
    cs = any(law_shared(q) != law_shared(qa) for q in wits)
    emit(f"control, one element of F shared by both slices: some witness pair has different laws: {cs}")
    ok &= c0 and len(l3) < 256 and len(ld) < 256 and cs
    ok &= any(law(q, three, b3) != l3 for q in wits) and any(law(q, dep, blocks) != ld for q in wits)

    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/slices.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
