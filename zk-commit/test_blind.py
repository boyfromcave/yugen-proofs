"""Two exact tests for the composition (docs/zk-composition.md).

Part A. Theorem 1' (claim-level masks for abstract round spaces). Round j has a challenge set, a
space P_j of functions of the challenge with a basis that starts with the constant 1, a nonzero
functional lam_j, and u_j in P_j with lam_j(u_j) = 1. The mask (c, g_1..g_n) has the view
    q_j = g_j + D_j u_j + K_j,   D_{j+1} = g_j(r_j) + u_j(r_j) D_j,   K_n = c,
    K_j = lam_{j+1}(g_{j+1}) + lam_{j+1}(1) K_{j+1},   G = lam_1(g_1) + lam_1(1) K_1.
Every mask's view must pass the round checks, and the rank of (mask coefficients -> (G, q_1..q_n))
must be 1 + sum_j (dim P_j - 1) = the dimension of the space of passing views, for EVERY
challenge vector. Instances: the affine-combiner fold round of the pinned leanVM verifier
(P = span{1, a, a^2, b, ab}, lam(q) = [1]q + [a]q, u = 1), the plain degree-2 and degree-3
sumcheck round (lam(p) = p(0) + p(1), u = X), and the invalid choice u = 1 for the plain round.

Part B. Evaluation blinding with a dummy variable. Column c(x) with Boolean values, constraint
C(c) = c (1 + c); blinded column chat(y, x) = c(x) + y (1 + y) b with one uniform blinder cell b.
Zerocheck over (y, x) with eq weights and Libra's mask inside the eq factor (zk-lemma code).
View: (G, round coefficients, mask value at r, chat(r)). Enumerated over every mask and every
blinder for all four Boolean columns: identical when r_y is not 0 or 1; different with the
blinder off or r_y in {0, 1}.

Provenance (REFERENCES.md): Theorem 1' and the blinder cells are Original (the Ycash developers, 2026)
as far as checked; no published statement is reproduced in this file.
"""
import itertools
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zk-lemma"))
import sumcheck as sc          # noqa: E402  (zk-lemma, read only)
from ff import GF, tv_distance  # noqa: E402


# ---------------------------------------------------------------- part A

class Space:
    """basis: list of functions(challenge) -> field element, basis[0] = constant 1.
    lam: list of lam(basis[i]). u: coefficient vector with lam(u) = 1."""

    def __init__(self, F, basis, lam, u):
        self.F, self.basis, self.lam, self.u = F, basis, lam, u
        self.dim = len(basis)

    def ev(self, coef, r):
        return self.F.dot(coef, [b(r) for b in self.basis])

    def lam_of(self, coef):
        return self.F.dot(coef, self.lam)


def affine_space(F):
    m = F.mul
    basis = [lambda r: 1, lambda r: r[0], lambda r: m(r[0], r[0]), lambda r: r[1], lambda r: m(r[0], r[1])]
    return Space(F, basis, [1, 1, 0, 0, 0], [1, 0, 0, 0, 0])


def plain_space(F, d, u_const=False):
    def power(e):
        def f(r):
            v = 1
            for _ in range(e):
                v = F.mul(v, r)
            return v
        return f
    basis = [power(e) for e in range(d + 1)]
    lam = [0] + [1] * d                       # p(0) + p(1) in characteristic 2
    u = [1] + [0] * d if u_const else [0, 1] + [0] * (d - 1)
    return Space(F, basis, lam, u)


def mask_view(F, spaces, coef, r):
    """coef = [c] + g_1 (dim_1 - 1 entries, constant dropped) + ..  ->  [G] + q_1 + .. + q_n."""
    n = len(spaces)
    g, pos = [], 1
    for sp in spaces:
        g.append([0] + coef[pos:pos + sp.dim - 1])
        pos += sp.dim - 1
    K = [0] * (n + 1)
    K[n] = coef[0]
    for j in range(n - 1, 0, -1):
        K[j] = spaces[j].lam_of(g[j]) ^ F.mul(spaces[j].lam[0], K[j + 1])
    G = spaces[0].lam_of(g[0]) ^ F.mul(spaces[0].lam[0], K[1])
    out, D = [G], 0
    for j, sp in enumerate(spaces):
        q = [a ^ F.mul(D, b) for a, b in zip(g[j], sp.u)]
        q[0] ^= K[j + 1]
        out += q
        D = sp.ev(g[j], r[j]) ^ F.mul(sp.ev(sp.u, r[j]), D)
    return out


def consistent(F, spaces, view, r):
    """The round checks: lam_1(q_1) = G, lam_{j+1}(q_{j+1}) = q_j(r_j)."""
    pos, prev = 1, view[0]
    for j, sp in enumerate(spaces):
        q = view[pos:pos + sp.dim]
        pos += sp.dim
        if sp.lam_of(q) != prev:
            return False
        prev = sp.ev(q, r[j])
    return True


def rank_at(F, spaces, r):
    """(rank, N) if every basis mask's view passes the round checks, else (-1, N)."""
    N = 1 + sum(sp.dim - 1 for sp in spaces)
    rows = []
    for i in range(N):
        e = [0] * N
        e[i] = 1
        rows.append(mask_view(F, spaces, e, r))
        if not consistent(F, spaces, rows[-1], r):
            return -1, N
    return F.rank(rows), N


def part_a(out):
    fails = 0
    rnd = random.Random(3)
    F2, F8 = GF(2), GF(8)
    for n in (1, 2):
        sp = [affine_space(F2)] * n
        pairs = list(itertools.product(range(4), repeat=2))
        full = tot = 0
        for r in itertools.product(pairs, repeat=n):
            rk, N = rank_at(F2, sp, r)
            full += rk == N
            tot += 1
        fails += full != tot
        out(f"affine-combiner space, GF(4), {n} round(s): full rank {1 + 4 * n} at {full}/{tot} challenge vectors (all)")
    for n in (3, 5, 14):
        sp = [affine_space(F8)] * n
        full = 0
        trials = [[(rnd.randrange(256), rnd.randrange(256)) for _ in range(n)] for _ in range(20)]
        trials += [[(a, b)] * n for a in (0, 1) for b in (0, 1)]
        for r in trials:
            rk, N = rank_at(F8, sp, r)
            full += rk == N
        fails += full != len(trials)
        out(f"affine-combiner space, GF(2^8), {n} rounds: full rank {1 + 4 * n} at {full}/{len(trials)} challenge vectors")
    for d in (2, 3):
        sp = [plain_space(F2, d)] * 3
        full = tot = 0
        for r in itertools.product(range(4), repeat=3):
            rk, N = rank_at(F2, sp, r)
            full += rk == N
            tot += 1
        fails += full != tot
        out(f"plain round space degree {d}, u = X, GF(4), 3 rounds: full rank {1 + 3 * d} at {full}/{tot} (all)")
    sp = [plain_space(F2, 2, u_const=True)] * 3
    full = sum(rank_at(F2, sp, r)[0] == 7 for r in itertools.product(range(4), repeat=3))
    fails += full == 64          # u = 1 is valid only where the u-term has coefficient 0 (r_1 = r_2 = 0)
    out(f"control: plain round space with u = 1 (lam(u) = 0): views pass the round checks at {full}/64 (only r_1 = r_2 = 0)")
    return fails


# ---------------------------------------------------------------- part B

def chat_poly(F, c0, c1, b):
    """chat(y, x) = c0 + (c0 + c1) x + (y + y^2) b, variables (y, x)."""
    p = {(0, 0): c0, (0, 1): c0 ^ c1, (1, 0): b, (2, 0): b}
    return {k: v for k, v in p.items() if v}


def part_b(out):
    F = GF(2)
    n, degs = 2, [4, 2]
    one = {(0, 0): 1}
    basis = [one] + [{(e, 0): 1} for e in range(1, 5)] + [{(0, e): 1} for e in (1, 2)]   # Libra, no redundancy
    fails = 0
    for label, blinder_on in (("blinder on", True), ("blinder off", False)):
        same = diff = same_bad = diff_bad = 0
        for tau in ((2, 3), (1, 2), (0, 3)):
            W = [(1 ^ t, t) for t in tau]
            for r in itertools.product(range(4), repeat=2):
                for rho in (1, 2):
                    gviews = [sc.view_of(F, g, n, degs, r, W) for g in basis]
                    dists = []
                    for c0, c1 in itertools.product((0, 1), repeat=2):
                        cnt = Counter()
                        for b in (range(4) if blinder_on else (0,)):
                            ch = chat_poly(F, c0, c1, b)
                            f = sc.padd(ch, sc.pmul(F, ch, ch))            # C(chat) = chat + chat^2
                            assert sc.cube_sum_by_definition(F, f, n, W) == 0
                            _, pf = sc.round_polys(F, f, n, degs, r, W)
                            fpart = [0] + [F.mul(rho, v) for p in pf for v in p] + [0]
                            chr_ = sc.eval_poly(F, ch, r)
                            for coef in itertools.product(range(4), repeat=len(basis)):
                                v = fpart[:]
                                for cf, gv in zip(coef, gviews):
                                    if cf:
                                        v = [a ^ F.mul(cf, x) for a, x in zip(v, gv)]
                                cnt[tuple(v) + (chr_,)] += 1
                        dists.append(cnt)
                    d = max(tv_distance(dists[0], x) for x in dists[1:])
                    Z = F.mul(r[0], r[0] ^ 1)
                    if Z and blinder_on:
                        same += d == 0
                        diff += d > 0
                    else:
                        same_bad += d == 0
                        diff_bad += d > 0
        if blinder_on:
            ok = diff == 0 and diff_bad > 0
            out(f"{'PASS' if ok else 'FAIL'} {label}: r_y not in {{0,1}}: identical {same}, different {diff}; "
                f"r_y in {{0,1}} (excluded event): identical {same_bad}, different {diff_bad}")
        else:
            ok = diff_bad > 0 and same_bad == 0
            out(f"{'PASS' if ok else 'FAIL'} {label}: identical {same_bad}, different {diff_bad}")
        fails += not ok
    return fails


if __name__ == "__main__":
    lines = []
    out = lambda s: (print(s, flush=True), lines.append(s))
    f = part_a(out) + part_b(out)
    out(f"FAILURES {f}")
    open("results/blind.txt", "w").write("\n".join(lines) + "\n")
    sys.exit(1 if f else 0)
