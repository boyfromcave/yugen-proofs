#!/usr/bin/env python3
"""Exact test of the linear opening gadget (docs/zk-masked-sumcheck.md, Lemma 3).

Committed: the mask vector a (N entries) followed by pad entries t, as a column A of length 2^l,
and a column B of the same length, uniform. To open the linear claim <a, w> = v:

    prover sends   beta = <B, w>          (w extended by zeros over the pad)
    verifier sends c
    prover sends   u = B + c * A          (the whole vector, in the clear)
    verifier sends z in F^l
    the commitment opens A(z) and B(z)    (multilinear extensions at z)
    verifier checks <u, w> = beta + c v   and   u(z) = B(z) + c A(z).

View for fixed (a, w, c, z): (beta, u, A(z), B(z)). Simulator, given v only: u uniform, A(z)
uniform, beta = <u, w> + c v, B(z) = u(z) + c A(z). The test enumerates all prover randomness
(B and t) and all simulator randomness and compares the distributions exactly, for every c and z.
Claim: equal whenever some pad entry has nonzero weight eq(z, index).

Run: python3 test_gadget.py
"""
import itertools
import random
import sys
from collections import Counter

from gf import GF

RNG = random.Random(20261120)


def eq_weights(F, z):
    w = [1]
    for zi in z:                      # index bit i (little endian) <-> z_i
        w = [F.mul(x, 1 ^ zi) for x in w] + [F.mul(x, zi) for x in w]
    return w


def dot(F, a, b):
    r = 0
    for x, y in zip(a, b):
        r ^= F.mul(x, y)
    return r


def case(F, l, npad, a, w, c, z):
    L = 1 << l
    N = L - npad
    wz = eq_weights(F, z)
    wext = list(w) + [0] * npad
    v = dot(F, a, w)
    real = Counter()
    for t in itertools.product(range(F.q), repeat=npad):
        A = list(a) + list(t)
        Az = dot(F, A, wz)
        cA = [F.mul(c, x) for x in A]
        for B in itertools.product(range(F.q), repeat=L):
            u = tuple(x ^ y for x, y in zip(B, cA))
            real[(dot(F, B, wext), u, Az, dot(F, B, wz))] += 1
    sim = Counter()
    mult = F.q ** (npad - 1)          # the simulator uses L + 1 elements; scale to the same total
    for u in itertools.product(range(F.q), repeat=L):
        uw, uz = dot(F, u, wext), dot(F, u, wz)
        for Az in range(F.q):
            sim[(uw ^ F.mul(c, v), u, Az, uz ^ F.mul(c, Az))] += mult
    pad_weight_nonzero = any(wz[N:])
    return real == sim, pad_weight_nonzero


def main():
    ok = True
    lines = []

    def emit(s):
        print(s, flush=True)
        lines.append(s)

    emit("# linear opening gadget: exact real-vs-simulated view, all prover and simulator randomness")
    for k, l, npad, na in ((2, 2, 1, 6), (2, 2, 2, 4), (2, 3, 1, 1), (4, 1, 1, 6)):
        F = GF(k)
        L = 1 << l
        N = L - npad
        zs = list(itertools.product(range(F.q), repeat=l))
        if k == 2 and l == 3:
            zs = [z for z in zs if RNG.random() < 0.15] + [(1, 1, 1), (0, 1, 1), (2, 3, 1)]
        eq_good = eq_bad = neq_good = neq_bad = 0
        for _ in range(na):
            a = [RNG.randrange(F.q) for _ in range(N)]
            w = [RNG.randrange(F.q) for _ in range(N)]
            for c in range(F.q):
                for z in zs:
                    same, good = case(F, l, npad, a, w, c, z)
                    if good:
                        eq_good += same
                        neq_good += not same
                    else:
                        eq_bad += same
                        neq_bad += not same
        emit(f"GF(2^{k}) length {L} (mask {N}, pad {npad}): pad weight nonzero: equal {eq_good}, different {neq_good};"
             f" pad weight zero: equal {eq_bad}, different {neq_bad}")
        ok &= neq_good == 0 and eq_good > 0
    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/gadget.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
