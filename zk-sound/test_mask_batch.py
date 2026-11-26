"""Masked fold batch of W-I with adversarial aux rows: exact game values (docs/zk-wi-soundness.md, Lemma 3).

Model. The oracle is ideal: the prover commits a coefficient table and cannot change it. One level,
kappa lane variables, one witness slot per lane with weight W, and the aux rows of the level's
staircase mask (1 + 2 kappa coefficients). An honest prover writes each mask coefficient into every
lane of its aux row; a cheating prover writes any table. The verifier's relation after the batch
puts the mask's final-value weight on each aux slot of the FOLDED lane, so the summand it enforces is

    H(x) = rho * P(x) W(x) + sum_m A_m(x) mono_m(x)        P, W, A_m multilinear in the lane index

of degree 3 per variable when the aux rows vary with the lane, 2 when they do not. Messages have
degree 2. The claim  sum_b P[b] W[b] = T  is false. Order: table, G, rho, rounds.

Computed: the exact value of the game (the best cheating prover over ALL message strategies), by
dynamic programming, for every aux table (GF(4), kappa = 1), every effective mask (GF(8),
kappa = 1) and a search over tables (GF(8), kappa = 2). Compared with the proven bound
1/q + kappa * 3/q and with the product form 1 - (1 - 1/q)(1 - 3/q)^kappa.
Control: G sent after rho is accepted with probability 1.
"""
import itertools
import random

from common import GF, Report, poly_eval

R = Report("mask_batch")


def pack(vals):
    x = 0
    for i, v in enumerate(vals):
        x |= v << (4 * i)
    return x


def zero_count(x, q, mask1):
    z = (x | (x >> 1) | (x >> 2) | (x >> 3)) & mask1
    return q - z.bit_count()


def messages(F):
    """All degree <= 2 messages, grouped by s(0) + s(1): packed value vectors and plain vectors."""
    by = {c: [] for c in range(F.q)}
    for co in itertools.product(range(F.q), repeat=3):
        vals = [poly_eval(F, co, x) for x in range(F.q)]
        by[vals[0] ^ vals[1]].append((pack(vals), vals))
    return by


def lin(F, a0, a1, x):
    return F.mul(1 ^ x, a0) ^ F.mul(x, a1)


def best_one_round(q, mask1, by, Hpacked, claim):
    return max(zero_count(Hpacked ^ sp, q, mask1) for sp, _ in by[claim])


def kappa1(F, by, exhaustive_tables):
    q = F.q
    mask1 = pack([1] * q)
    P, W = (1, 2), (3, 1)
    S = F.mul(P[0], W[0]) ^ F.mul(P[1], W[1])
    T = S ^ 1
    fvals = [F.mul(lin(F, P[0], P[1], x), lin(F, W[0], W[1], x)) for x in range(q)]

    def value(gvals):
        # V[rho][claim]
        V = []
        for rho in range(q):
            Hp = pack([F.mul(rho, f) ^ g for f, g in zip(fvals, gvals)])
            V.append([best_one_round(q, mask1, by, Hp, c) for c in range(q)])
        return max(sum(V[rho][F.mul(rho, T) ^ G] for rho in range(q)) for G in range(q))  # out of q*q

    best_const = best_any = 0
    if exhaustive_tables:
        for tab in itertools.product(range(q), repeat=6):               # A[b][m], b = lane, m = 1, x, x^2
            A = (tab[0:3], tab[3:6])
            gvals = [0] * q
            for x in range(q):
                acc, xp = 0, 1
                for m in range(3):
                    acc ^= F.mul(lin(F, A[0][m], A[1][m], x), xp)
                    xp = F.mul(xp, x)
                gvals[x] = acc
            v = value(gvals)
            best_any = max(best_any, v)
            if A[0] == A[1]:
                best_const = max(best_const, v)
    else:
        for co in itertools.product(range(q), repeat=4):                # every cubic effective mask
            v = value([poly_eval(F, co, x) for x in range(q)])
            best_any = max(best_any, v)
            if co[3] == 0:
                best_const = max(best_const, v)
    return best_const / q**2, best_any / q**2


def kappa2_search(F, by, tables, seed):
    q = F.q
    mask1 = pack([1] * q)
    rnd = random.Random(seed)
    mons = [(0, 0), (1, 1), (2, 1), (0, 1), (0, 2)]                      # staircase, kappa = 2
    P = [1, 2, 3, 5]
    W = [1, 1, 2, 4]
    S = 0
    for p, w in zip(P, W):
        S ^= F.mul(p, w)
    T = S ^ 1

    def ml(vals, x0, x1):                                               # lane index b = b0 + 2 b1
        lo, hi = lin(F, vals[0], vals[1], x0), lin(F, vals[2], vals[3], x0)
        return lin(F, lo, hi, x1)

    fgrid = [[F.mul(ml(P, x0, x1), ml(W, x0, x1)) for x1 in range(q)] for x0 in range(q)]
    mono = [[[F.mul(F.pow(x0, e0), F.pow(x1, e1)) for x1 in range(q)] for x0 in range(q)] for e0, e1 in mons]

    def value(A):                                                       # A[m][lane]
        ggrid = [[0] * q for _ in range(q)]
        for m in range(5):
            for x0 in range(q):
                for x1 in range(q):
                    ggrid[x0][x1] ^= F.mul(ml(A[m], x0, x1), mono[m][x0][x1])
        V0 = []
        for rho in range(q):
            H = [[F.mul(rho, fgrid[x0][x1]) ^ ggrid[x0][x1] for x1 in range(q)] for x0 in range(q)]
            V1 = [[best_one_round(q, mask1, by, pack(H[g1]), c) for c in range(q)] for g1 in range(q)]
            V0.append([max(sum(V1[g1][vals[g1]] for g1 in range(q)) for _, vals in by[c]) for c in range(q)])
        return max(sum(V0[rho][F.mul(rho, T) ^ G] for rho in range(q)) for G in range(q))

    const = value([[rnd.randrange(q)] * 4 for _ in range(5)])
    best = 0
    for _ in range(tables):
        best = max(best, value([[rnd.randrange(q) for _ in range(4)] for _ in range(5)]))
    # structured: only the top-degree aux rows vary
    for _ in range(tables // 4):
        A = [[rnd.randrange(q)] * 4 for _ in range(5)]
        A[2] = [rnd.randrange(q) for _ in range(4)]
        A[4] = [rnd.randrange(q) for _ in range(4)]
        best = max(best, value(A))
    return const / q**3, best / q**3


def control_G_after_rho(F):
    """If G may depend on rho the prover sets G := (true masked sum) - rho T and is always accepted."""
    q = F.q
    P, W, A = (1, 2), (3, 1), ((1, 2, 3), (1, 2, 3))
    S = F.mul(P[0], W[0]) ^ F.mul(P[1], W[1])
    T = S ^ 1
    acc = 0
    for rho in range(q):
        H = []
        for x in range(q):
            g, xp = 0, 1
            for m in range(3):
                g ^= F.mul(lin(F, A[0][m], A[1][m], x), xp)
                xp = F.mul(xp, x)
            H.append(F.mul(rho, F.mul(lin(F, P[0], P[1], x), lin(F, W[0], W[1], x))) ^ g)
        G = H[0] ^ H[1] ^ F.mul(rho, T)
        claim = F.mul(rho, T) ^ G
        acc += (claim == H[0] ^ H[1])                                   # the honest message then passes every gamma
    return acc / q


def main():
    for k, exhaustive in ((2, True), (3, False)):
        F = GF(k)
        q = F.q
        by = messages(F)
        const, anyv = kappa1(F, by, exhaustive)
        bound, prod = 1 / q + 3 / q, 1 - (1 - 1 / q) * (1 - 3 / q)
        R.say(f"kappa=1 GF({q}) {'every aux table (4^6)' if exhaustive else 'every cubic effective mask (8^4)'}: "
              f"lane-constant aux {const:.4f}, any aux {anyv:.4f}; proven sum bound {bound:.4f}, product form {prod:.4f}")
        R.check(anyv <= min(1.0, prod) + 1e-12, f"GF({q}) kappa=1: exact optimum {anyv:.4f} <= product-form bound {min(1.0, prod):.4f}")
        R.check(abs(const - (1 - (1 - 1 / q) * (1 - 2 / q))) < 1e-12,
                f"GF({q}) kappa=1: lane-constant optimum equals 1 - (1 - 1/q)(1 - 2/q) = {1 - (1 - 1 / q) * (1 - 2 / q):.4f}")
        R.check(anyv >= const, f"GF({q}) kappa=1: lane-varying aux rows gain {anyv - const:+.4f} (the (d+1)/q effect)")
    F = GF(3)
    q = F.q
    const, best = kappa2_search(F, messages(F), tables=160, seed=20261119)
    prod = 1 - (1 - 1 / q) * (1 - 3 / q) ** 2
    R.say(f"kappa=2 GF(8) 200 searched aux tables: lane-constant {const:.4f}, best found {best:.4f}; "
          f"product-form bound {prod:.4f}, sum bound {1 / q + 6 / q:.4f}")
    R.check(best <= prod + 1e-12, f"GF(8) kappa=2: best exact game value {best:.4f} <= {prod:.4f}")
    R.check(abs(const - (1 - (1 - 1 / q) * (1 - 2 / q) ** 2)) < 1e-12,
            f"GF(8) kappa=2: lane-constant optimum equals 1 - (1 - 1/q)(1 - 2/q)^2 = {1 - (1 - 1 / q) * (1 - 2 / q) ** 2:.4f}")
    c = control_G_after_rho(GF(3))
    R.check(c == 1.0, f"control: G sent after rho is accepted with probability {c:.2f} (must be 1: the order matters)")
    R.close()


if __name__ == "__main__":
    main()
