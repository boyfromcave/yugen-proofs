"""Theorem 1' on system A's Keccak layer chain (docs/zk-system-a-gaps.md, section 4; reference test M-1).

One layer of `verifier/src/keccak.rs::verify_layer` is a claim reduction with three kinds of round:

  S5  one round. Message: the 47 coefficients of the product polynomial P(s), degree <= 46. Check
      <functional, P> = claim (+ a public term); next claim P(s). Round space: polynomials of
      degree <= 46 in the challenge s; lam(P) = <functional, P>;
      functional_c = sum of mu_i over the i with bit c of RMFE_PROJECT[i] set.
  S6  eq-weighted rounds, reduced message of degree 2: lam(p) = (1 + tau) p(0) + tau p(1), u = 1.
  S7  plain rounds of degree 3: lam(p) = p(0) + p(1), u = X.

Mask: one claim-level mask for the chain, 1 + 46 + 2 n6 + 3 n7 coefficients. S5 is the first round
of its chain, so no u is used for it (D_1 = 0).

Checked: every mask's messages pass the round checks and the mask-to-view map has rank
N = 1 + 46 + 2 n6 + 3 n7 = dim V_r, at the pinned shape (n6 = 6, n7 = 11, N = 92) and smaller ones;
for lam random, for lam built from the pinned RMFE_PROJECT with random mu and with mu the
embeddings at a random s; and for lam = 0 (rank N as well: G is identically 0 and the first
message is free). The pinned constants: RMFE_PROJECT has F_2-rank 16 and the sixteen RMFE_EMBED
polynomials have gcd 1, so lam != 0 for every instance-weight vector the verifier can produce.
Controls: a mask of 45 coefficients for the product round; lam = 0 in a round that is not first.
"""
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ff import GF                                                   # noqa: E402
from test_blind import Space, consistent, mask_view, plain_space    # noqa: E402

RMFE_EMBED = [0x40c50b, 0x7f79f2, 0x4b4e0a, 0x72740c, 0x5357da, 0x1d1c9e, 0x04be6e, 0x785246, 0x097cdc,
              0x109e7e, 0x1f1454, 0x213cfc, 0x4cfcc8, 0x775770, 0x187386, 0x818a16]
RMFE_PROJECT = [0x1, 0x7fffffffffff, 0x274e9d3a74e9, 0x1d3a74e9d3a7, 0x65cb972e5cb9, 0x5cb972e5cb97,
                0x6690aec7cd21, 0x5d8f9a42bb1f, 0x73485763e690, 0x3750967c6ea1, 0x12cf8dd4259f,
                0x1ba84b3e3750, 0x0ad0c9f715a1, 0x064fb8ad0c9f, 0x456864fb8ad0, 0x400000000000]
PRODUCT_BITS = 47


def power(F, e):
    def f(r):
        v = 1
        for _ in range(e):
            v = F.mul(v, r)
        return v
    return f


def product_space(F, lam, deg=PRODUCT_BITS - 1):
    basis = [power(F, e) for e in range(deg + 1)]
    u = [0] * (deg + 1)
    i = next((k for k, v in enumerate(lam) if v), None)
    if i is not None:
        u[i] = F.inv(lam[i])
    return Space(F, basis, list(lam), u)


def eq_space(F, tau, d=2):
    basis = [power(F, e) for e in range(d + 1)]
    return Space(F, basis, [1] + [tau] * d, [1] + [0] * d)          # lam(1) = 1, lam(X^e) = tau


def functional(F, mu):
    out = []
    for c in range(PRODUCT_BITS):
        v = 0
        for i in range(16):
            if RMFE_PROJECT[i] >> c & 1:
                v ^= mu[i]
        out.append(v)
    return out


def embed_at(F, s):
    pw = [1]
    for _ in range(23):
        pw.append(F.mul(pw[-1], s))
    out = []
    for e in RMFE_EMBED:
        v = 0
        for b in range(24):
            if e >> b & 1:
                v ^= pw[b]
        out.append(v)
    return out


def views(F, spaces, r, drop=()):
    N = 1 + sum(sp.dim - 1 for sp in spaces)
    rows, good = [], True
    for i in range(N):
        if i in drop:
            continue
        e = [0] * N
        e[i] = 1
        rows.append(mask_view(F, spaces, e, r))
        good &= consistent(F, spaces, rows[-1], r)
    return rows, N, good


def f2_rank(vals):
    v, r = list(vals), 0
    while v:
        p = v.pop()
        if p:
            r += 1
            hb = p.bit_length() - 1
            v = [a ^ p if a >> hb & 1 else a for a in v]
    return r


def pgcd(a, b):
    while b:
        while a and a.bit_length() >= b.bit_length():
            a ^= b << (a.bit_length() - b.bit_length())
        a, b = b, a
    return a


def main():
    lines = []
    out = lambda s: (print(s, flush=True), lines.append(s))
    fails = 0
    rnd = random.Random(7)

    # the pinned constants
    g = 0
    for e in RMFE_EMBED:
        g = pgcd(max(g, e), min(g, e)) if g else e
    rp, re_ = f2_rank(RMFE_PROJECT), f2_rank(RMFE_EMBED)
    out(f"pinned constants: F_2-rank of RMFE_PROJECT {rp} of 16, of RMFE_EMBED {re_} of 16, gcd of the sixteen "
        f"embedding polynomials = {g:#x}")
    fails += rp != 16 or g != 1
    F8 = GF(8)
    zero_mu = sum(not any(embed_at(F8, s)) for s in range(256))
    zero_fn = sum(not any(functional(F8, embed_at(F8, s))) for s in range(256))
    out(f"GF(2^8), every s: instance weights all zero at {zero_mu} points, functional zero at {zero_fn} points")
    fails += zero_mu != 0 or zero_fn != 0

    def chain(F, lam, n6, n7, taus, dummy=False):
        sp = [product_space(F, lam)] + [eq_space(F, t) for t in taus[:n6]] + [plain_space(F, 3)] * n7
        return sp + ([eq_space(F, 0, 2)] if dummy else [])     # the one-sided dummy round: lam(p) = p(0), degree 2

    def challenges(F, n):
        return [rnd.randrange(F.q) for _ in range(n)]

    for n6, n7, trials in ((6, 11, 6), (2, 3, 12), (0, 0, 12)):
        N = 1 + 46 + 2 * n6 + 3 * n7
        for label in ("random lam", "lam from random mu", "lam from mu = embeddings at a random s", "lam = 0"):
            full = cons = 0
            g_zero = True
            for t in range(trials):
                if label == "random lam":
                    lam = [rnd.randrange(256) for _ in range(PRODUCT_BITS)]
                elif label == "lam from random mu":
                    lam = functional(F8, [rnd.randrange(256) for _ in range(16)])
                elif label == "lam = 0":
                    lam = [0] * PRODUCT_BITS
                else:
                    lam = functional(F8, embed_at(F8, rnd.randrange(256)))
                taus = challenges(F8, n6)
                r = challenges(F8, 1 + n6 + n7)
                if t == 0:
                    r = [0] * len(r)
                if t == 1:
                    r = [1] * len(r)
                    taus = [1] * n6
                rows, NN, good = views(F8, chain(F8, lam, n6, n7, taus), r)
                assert NN == N
                cons += good
                full += F8.rank(rows) == N
                g_zero &= all(row[0] == 0 for row in rows)
            ok = full == trials and cons == trials and (label != "lam = 0" or g_zero)
            fails += not ok
            extra = "; G identically 0" if label == "lam = 0" and g_zero else ""
            out(f"{'PASS' if ok else 'FAIL'} chain S5 + {n6} eq rounds + {n7} plain rounds, {label}: checks pass "
                f"{cons}/{trials}, rank {N} = dim V_r at {full}/{trials} challenge vectors{extra}")

    # the pinned shape with the dummy round of the layer's terminal appended (lam(p) = p(0), degree 2, u = 1)
    full = 0
    for t in range(6):
        lam = functional(F8, embed_at(F8, rnd.randrange(256)))
        taus, r = challenges(F8, 6), challenges(F8, 1 + 6 + 11 + 1)
        if t == 0:
            r[-1] = 0
        rows, N, good = views(F8, chain(F8, lam, 6, 11, taus, dummy=True), r)
        full += good and N == 94 and F8.rank(rows) == N
    out(f"{'PASS' if full == 6 else 'FAIL'} chain S5 + 6 eq rounds + 11 plain rounds + one-sided dummy round: rank 94 = dim V_r "
        f"at {full}/6 challenge vectors")
    fails += full != 6

    # exhaustive challenges at a reduced size: product round of degree 6, one eq round, one plain round, GF(16)
    F4 = GF(4)
    full = tot = 0
    for lam in ([1, 0, 0, 0, 0, 0, 0], [0, 3, 0, 9, 0, 0, 1], [5, 5, 5, 5, 5, 5, 5], [0] * 7):
        for tau in (0, 1, 7):
            for r in itertools.product(range(16), repeat=3):
                spaces = [product_space(F4, lam, 6), eq_space(F4, tau), plain_space(F4, 3)]
                rows, N, good = views(F4, spaces, r)
                tot += 1
                full += good and F4.rank(rows) == N
    out(f"{'PASS' if full == tot else 'FAIL'} reduced size (degree 6, one eq round, one plain round), GF(16), four lam "
        f"(one zero), three tau: rank 12 at {full}/{tot} (all challenge vectors)")
    fails += full != tot

    # control: one mask coefficient too few in the product round
    lam = functional(F8, [rnd.randrange(256) for _ in range(16)])
    taus, r = challenges(F8, 2), challenges(F8, 6)
    rows, N, _ = views(F8, chain(F8, lam, 2, 3, taus), r, drop=(46,))
    rk = F8.rank(rows)
    out(f"control: mask of 45 coefficients for the product round: rank {rk} against dim V_r = {N}")
    fails += rk != N - 1
    # control: a product round with lam = 0 that is not the first round of its chain
    spaces = [eq_space(F8, taus[0])] + chain(F8, [0] * PRODUCT_BITS, 0, 0, [])
    r = challenges(F8, 2)
    rows, N, good = views(F8, spaces, r)
    out(f"control: product round with lam = 0 placed second: the mask's messages pass the round checks: {good}")
    fails += good

    out(f"FAILURES {fails}")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "product_round.txt"), "w").write("\n".join(lines) + "\n")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
