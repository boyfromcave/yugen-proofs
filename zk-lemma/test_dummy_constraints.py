#!/usr/bin/env python3
"""Dummy-constraint blinding of the wrapper products (a, b, c) and of s_pre (system B, N3/N8).

docs/zk-composition.md section 5.2, Lemma DC and Corollary DC (Original, the Ycash developers,
2026; draft until refereed; hvzk-referee.md H-3). Model of IronSpartan's blinding at the B pin
(`spartan-frontend/src/constraint_system.rs` BlindingInfo, `spartan-prover/src/lib.rs`
pack_and_blind_witness, `spartan-verifier/src/constraint_system.rs` add_blinding_constraints):
each committed segment carries two dummy multiplication constraints with wires (a_i, b_i, a_i b_i),
a_i, b_i uniform; at the constraint point r_x they contribute alpha_i (a_i, b_i, a_i b_i) to the
operand evaluations, alpha_i = eq(r_x, j_i).

Part 1 (GF(16) = GF(2^4), every alpha1 != alpha2, both nonzero): the share X of one segment is enumerated
over all (a1, b1, a2, b2); its total-variation distance from uniform on K^3 equals (q-1)/q^2.
Part 2 (GF(4) = GF(2^2), every alpha1..alpha4 nonzero with alpha1 != alpha2, alpha3 != alpha4, every
lambda): the revealed noise N = (P + W, P_A + lam P_B + lam^2 P_C) is enumerated over all 8 dummy
operands; TV(N, uniform on K^4) <= 2 (q-1)/q^2.
Controls: one dummy constraint a segment (far from uniform); alpha1 = alpha2 is reported
(distance not the formula); the precommit segment without dummies (s_pre a constant).

Amended 2026-11-19 (zk-b-referee.md F-2): part 1 also asserts that the first two coordinates
(u, v) are uniform and that alpha1 = alpha2 does NOT give the formula (assertion, not a print);
part 2 asserts each step of the coupling separately, TV(N, N*) <= delta and TV(N*, U) <= delta,
with N* = (U_3, l(P)), and pins the GF(4) worst value 561/8192 as a regression constant; new
controls: alpha_i = 0 (distance must exceed delta) and alpha1 = alpha2 in part 2 (distance must
differ from the admissible worst case). The challenges (alpha, lambda) are fixed before the dummy
operands are enumerated (F-6).

Run: python3 test_dummy_constraints.py
"""
import itertools
import sys
from collections import Counter
from fractions import Fraction

from gf import GF


def tv_from_uniform(counter, total, support):
    seen = sum(abs(Fraction(c, total) - Fraction(1, support)) for c in counter.values())
    unseen = (support - len(counter)) * Fraction(1, support)
    return (seen + unseen) / 2


def share(f, al, ops):
    A = B = C = 0
    for a_, (a, b) in zip(al, ops):
        A ^= f.mul(a_, a)
        B ^= f.mul(a_, b)
        C ^= f.mul(a_, f.mul(a, b))
    return A, B, C


def part1():
    f = GF(4)
    q = f.q
    bound = Fraction(q - 1, q * q)
    els = range(q)
    ok = True
    for al1 in range(1, q):
        for al2 in range(1, q):
            cnt = Counter()
            uv = Counter()
            for a1, b1, a2, b2 in itertools.product(els, repeat=4):
                X = share(f, (al1, al2), ((a1, b1), (a2, b2)))
                cnt[X] += 1
                uv[X[:2]] += 1
            tv = tv_from_uniform(cnt, q ** 4, q ** 3)
            if al1 != al2 and tv != bound:
                ok = False
                print("FAIL part1", al1, al2, tv)
            if al1 == al2 and tv == bound:
                ok = False
                print("FAIL part1 control: alpha1 = alpha2 gave the formula", al1)
            if tv_from_uniform(uv, q ** 4, q ** 2) != 0:
                ok = False
                print("FAIL part1: (u, v) not uniform", al1, al2)
    print(f"part1 GF(16): every alpha1 != alpha2 nonzero: TV = (q-1)/q^2 = {bound}, (u, v) uniform, alpha1 = alpha2 off the formula: {'PASS' if ok else 'FAIL'}")
    # control: one constraint
    cnt = Counter()
    for a1, b1 in itertools.product(els, repeat=2):
        cnt[share(f, (1,), ((a1, b1),))] += 1
    tv1 = tv_from_uniform(cnt, q ** 2, q ** 3)
    c1 = tv1 >= Fraction(1, 2)
    print(f"control one dummy constraint: TV = {tv1} (far from uniform): {'PASS' if c1 else 'FAIL'}")
    return ok and c1


WORST_GF4 = Fraction(561, 8192)  # regression constant (results/dummy_constraints.txt, 2026-11-19)


def joint(f, al, lam):
    """(N, N*) counts for fixed challenges; the dummy operands are enumerated after (F-6)."""
    q = f.q
    els = range(q)
    l2 = f.mul(lam, lam)
    cnt = Counter()
    lp = Counter()
    for ops in itertools.product(els, repeat=8):
        P = share(f, al[:2], ((ops[0], ops[1]), (ops[2], ops[3])))
        W = share(f, al[2:], ((ops[4], ops[5]), (ops[6], ops[7])))
        s = P[0] ^ f.mul(lam, P[1]) ^ f.mul(l2, P[2])
        cnt[(P[0] ^ W[0], P[1] ^ W[1], P[2] ^ W[2], s)] += 1
        lp[s] += 1
    return cnt, lp


def tv_n_nstar(cnt, lp, q):
    """TV(N, N*), N* = (U_3 uniform on K^3, l(P)); N* has mass lp[s]/q^8 / q^3 on (x, s)."""
    tot = q ** 8
    d = Fraction(0)
    for x in itertools.product(range(q), repeat=4):
        d += abs(Fraction(cnt.get(x, 0), tot) - Fraction(lp.get(x[3], 0), tot * q ** 3))
    return d / 2


def part2():
    f = GF(2)
    q = f.q
    els = range(q)
    delta = Fraction(q - 1, q * q)
    bound = 2 * delta
    ok = True
    worst = Fraction(0)
    for al in itertools.product(range(1, q), repeat=4):
        if al[0] == al[1] or al[2] == al[3]:
            continue
        for lam in els:
            cnt, lp = joint(f, al, lam)
            tv = tv_from_uniform(cnt, q ** 8, q ** 4)
            step1 = tv_n_nstar(cnt, lp, q)
            step2 = tv_from_uniform(lp, q ** 8, q)  # TV(N*, U) = TV(l(P), U(K))
            worst = max(worst, tv)
            if tv > bound or step1 > delta or step2 > delta:
                ok = False
                print("FAIL part2", al, lam, tv, step1, step2)
    if worst != WORST_GF4:
        ok = False
        print("FAIL part2 regression: worst", worst, "expected", WORST_GF4)
    print(f"part2 GF(4): joint (A, B, C, s_pre) noise, worst TV = {worst} (= {WORST_GF4}) <= 2(q-1)/q^2 = {bound}; "
          f"each coupling step <= delta = {delta}: {'PASS' if ok else 'FAIL'}")
    # control: alpha_i = 0 (one segment loses a dummy constraint) must exceed delta
    c0 = True
    for al in ((1, 2, 0, 1), (0, 1, 1, 2)):
        cnt, _ = joint(f, al, 1)
        tz = tv_from_uniform(cnt, q ** 8, q ** 4)
        if not tz > delta:
            c0 = False
        print(f"control alpha = {al}: TV = {tz} > delta = {delta}: {'PASS' if tz > delta else 'FAIL'}")
    # control: alpha1 = alpha2 (and alpha3 = alpha4) must be off the admissible worst case
    cnt, _ = joint(f, (1, 1, 2, 2), 1)
    te = tv_from_uniform(cnt, q ** 8, q ** 4)
    ce = te > WORST_GF4
    print(f"control alpha1 = alpha2, alpha3 = alpha4: TV = {te} > {WORST_GF4}: {'PASS' if ce else 'FAIL'}")
    ok = ok and c0 and ce
    # control: precommit segment without dummies -> s_pre carries the real share unmasked
    cnt = Counter()
    for ops in itertools.product(els, repeat=4):
        W = share(f, (1, 2), ((ops[0], ops[1]), (ops[2], ops[3])))
        cnt[(W[0], W[1], W[2], 0)] += 1
    tvc = tv_from_uniform(cnt, q ** 4, q ** 4)
    c = tvc >= Fraction(1, 2)
    print(f"control no precommit dummies: TV = {tvc} (s_pre unmasked): {'PASS' if c else 'FAIL'}")
    return ok and c


if __name__ == "__main__":
    r = part1() and part2()
    sys.exit(0 if r else 1)
