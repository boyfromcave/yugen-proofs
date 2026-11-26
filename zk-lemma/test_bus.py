#!/usr/bin/env python3
"""Exact distributions of masked per-table bus terminals (docs/zk-masked-sumcheck.md, section 8).

T tables publish terminals sigma_1..sigma_T whose total is fixed by the bus check (sum 0 for a
logarithmic-derivative bus, product 1 for a grand-product bus). Each sigma_t alone is a function
of the witness.

  additive mask        sigma^_t = sigma_t + e_t + e_{t-1},  e_0 = e_T = 0, e_1..e_{T-1} uniform
  multiplicative mask  sigma^_t = sigma_t * e_t / e_{t-1},  e_0 = e_T = 1, e_t uniform nonzero
  message mask (LogUp) sigma^_t = sigma_t + 1/(gamma + m_t) + 1/(gamma + m_{t-1}), m_t uniform:
                       the form a bus message between neighbouring tables produces

The test enumerates the mask randomness and compares with the simulator's distribution (uniform
on the hyperplane, resp. on the nonzero points of the product-one variety), exactly.

Run: python3 test_bus.py
"""
import itertools
import random
import sys
from collections import Counter
from fractions import Fraction

from gf import GF

RNG = random.Random(20261121)


def sd(c1, c2):
    t1, t2 = sum(c1.values()), sum(c2.values())
    return sum(abs(Fraction(c1.get(k, 0), t1) - Fraction(c2.get(k, 0), t2)) for k in set(c1) | set(c2)) / 2


def main():
    ok = True
    lines = []

    def emit(s):
        print(s, flush=True)
        lines.append(s)

    emit("# masked bus terminals: exact statistical distance to the witness-free simulator")
    for k, Ts in ((2, (2, 3, 4)), (4, (2, 3)), (8, (2,))):
        F = GF(k)
        for T in Ts:
            worst_add = worst_mul = worst_msg = Fraction(0)
            for _ in range(6):
                # additive: any sigma with xor-sum 0
                sig = [RNG.randrange(F.q) for _ in range(T - 1)]
                last = 0
                for s in sig:
                    last ^= s
                sig.append(last)
                real = Counter()
                for e in itertools.product(range(F.q), repeat=T - 1):
                    ee = (0,) + e + (0,)
                    real[tuple(sig[t] ^ ee[t + 1] ^ ee[t] for t in range(T))] += 1
                sim = Counter()
                for free in itertools.product(range(F.q), repeat=T - 1):
                    last = 0
                    for s in free:
                        last ^= s
                    sim[free + (last,)] += 1
                worst_add = max(worst_add, sd(real, sim))
                # message mask: delta_t = 1/(gamma + m_t), runs with gamma + m_t = 0 abort
                gamma = RNG.randrange(F.q)
                realm = Counter()
                for m in itertools.product(range(F.q), repeat=T - 1):
                    if any(x == gamma for x in m):
                        continue
                    ee = (0,) + tuple(F.inv(gamma ^ x) for x in m) + (0,)
                    realm[tuple(sig[t] ^ ee[t + 1] ^ ee[t] for t in range(T))] += 1
                worst_msg = max(worst_msg, sd(realm, sim))
                # multiplicative: nonzero sigma with product 1
                sg = [RNG.randrange(1, F.q) for _ in range(T - 1)]
                p = 1
                for s in sg:
                    p = F.mul(p, s)
                sg.append(F.inv(p))
                realp = Counter()
                for e in itertools.product(range(1, F.q), repeat=T - 1):
                    ee = (1,) + e + (1,)
                    realp[tuple(F.mul(sg[t], F.mul(ee[t + 1], F.inv(ee[t]))) for t in range(T))] += 1
                simp = Counter()
                for free in itertools.product(range(1, F.q), repeat=T - 1):
                    p = 1
                    for s in free:
                        p = F.mul(p, s)
                    simp[free + (F.inv(p),)] += 1
                worst_mul = max(worst_mul, sd(realp, simp))
            bound = Fraction(T - 1, F.q)
            emit(f"GF(2^{k}) T={T}: additive SD={worst_add}  multiplicative SD={worst_mul}  "
                 f"message SD={float(worst_msg):.5f} (bound (T-1)/|F| = {float(bound):.5f})")
            ok &= worst_add == 0 and worst_mul == 0 and worst_msg <= bound and worst_msg > 0
    emit("# fractional bus (sigma_t = P_t / Q_t, both published): messages between neighbours plus one")
    emit("# self-cancelling pair per table; conditional on no zero denominator")
    for k, Ts in ((2, (2, 3)), (4, (2, 3))):
        F = GF(k)
        for T in Ts:
            worst = Fraction(0)
            for _ in range(3):
                sig = [RNG.randrange(F.q) for _ in range(T - 1)]
                last = 0
                for s in sig:
                    last ^= s
                sig.append(last)
                Q = [RNG.randrange(1, F.q) for _ in range(T)]
                real = Counter()
                # x_t = 1/(gamma + m_t) for the neighbour messages, y_t = gamma + m'_t for the internal pair
                for x in itertools.product(range(1, F.q), repeat=T - 1):
                    xx = (0,) + x + (0,)
                    sh = tuple(sig[t] ^ xx[t + 1] ^ xx[t] for t in range(T))
                    base = []
                    for t in range(T):
                        q_ = Q[t]
                        for v in (xx[t], xx[t + 1]):
                            if v:
                                q_ = F.mul(q_, F.inv(v))          # denominator factor gamma + m = 1/x
                        base.append(q_)
                    for y in itertools.product(range(1, F.q), repeat=T):
                        real[sh + tuple(F.mul(base[t], F.mul(y[t], y[t])) for t in range(T))] += 1
                sim = Counter()
                for x in itertools.product(range(1, F.q), repeat=T - 1):
                    xx = (0,) + x + (0,)
                    sh = tuple(sig[t] ^ xx[t + 1] ^ xx[t] for t in range(T))
                    for qh in itertools.product(range(1, F.q), repeat=T):
                        sim[sh + qh] += 1
                worst = max(worst, sd(real, sim))
            emit(f"GF(2^{k}) T={T}: (terminals, denominators) against (message-masked terminals, uniform nonzero"
                 f" denominators): SD={worst}")
            ok &= worst == 0
    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/bus.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
