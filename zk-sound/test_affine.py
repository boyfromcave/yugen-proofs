"""System A's fold round (affine combiner  P' = G + (alpha + beta X) F) with a claim-level mask in aux
slots: layout (completeness) and exact game values (docs/zk-wi-soundness.md, sections 4.3 and 7).

The round is read from the pinned leanVM verifier (crates/verifier/src/whir.rs, verify_whir and
fold_row): lanes 2i (F) and 2i + 1 (G); weights fold as W' = W_F + alpha (W_F + W_G); the prover
sends (u0, w, c0, c1) and the claim becomes
    u0 + beta c0 + alpha (u0 + claim + alpha w + beta (c0 + c1)).
Multiplication by X acts on novel-basis coefficients and moves a coefficient up by at most one slot.

Part 1 (layout). The mask of Theorem 1' (zk-hiding-commitment.md section 5) has final value
sum_j g_j(alpha_j, beta_j) + c. Its coefficients must sit in the folded lane with coefficient 1.
Tested layouts: (a) each coefficient in every lane of its aux slot, as W-I writes it for the
eq-fold; (b) in the all-G lane only, aux slots directly above the carried slots; (c) in the all-G
lane only, with kappa empty guard slots between the carried slots and the aux slots.
Part 2 (soundness). One round, ideal oracle, any committed table (aux and guard slots arbitrary in
both lanes), false claim: the exact value of the game over all (G, message) strategies, against
1 - (1 - 1/q)(1 - 3/q): the true final claim has total degree 3 in (alpha, beta).
"""
import itertools
import random

from common import GF, Chain, Report, solve

R = Report("affine")
MON = [(1, 0), (2, 0), (0, 1), (1, 1)]                                  # a, a^2, b, ab


def times_x_matrix(F, ch, L):
    """cols[c] = novel-basis coefficients (length L) of x * X_c, for c < L - 1."""
    pts = list(range(L))
    rows = [ch.novel_row(x, L) for x in pts]
    cols = []
    for c in range(L - 1):
        cols.append(solve(F, rows, [F.mul(x, ch.novel_row(x, L)[c]) for x in pts]))
    return cols


def times_x(F, cols, v):
    out = [0] * len(v)
    for c, a in enumerate(v):
        if a:
            assert c < len(cols), "degree overflow"
            out = [o ^ F.mul(a, m) for o, m in zip(out, cols[c])]
    return out


def mono(F, e, a, b):
    return F.mul(F.pow(a, e[0]), F.pow(b, e[1]))


def fold(F, cols, P, W, a, b):
    Pn, Wn = [], []
    for i in range(len(P) // 2):
        Fl, Gl = P[2 * i], P[2 * i + 1]
        MF = times_x(F, cols, Fl)
        Pn.append([g ^ F.mul(a, f) ^ F.mul(b, m) for g, f, m in zip(Gl, Fl, MF)])
        Wn.append([wf ^ F.mul(a, wf ^ wg) for wf, wg in zip(W[2 * i], W[2 * i + 1])])
    return Pn, Wn


def scalars(F, cols, P, W):
    u0 = w = c0 = c1 = 0
    for i in range(len(P) // 2):
        Fl, Gl, WF, WG = P[2 * i], P[2 * i + 1], W[2 * i], W[2 * i + 1]
        MF = times_x(F, cols, Fl)
        u0 ^= F.dot(Gl, WF)
        w ^= F.dot(Fl, [x ^ y for x, y in zip(WF, WG)])
        c0 ^= F.dot(MF, WF)
        c1 ^= F.dot(MF, WG)
    return u0, w, c0, c1


def layout_run(F, ch, kappa, layout, rnd, trials):
    """Honest masked batch; returns the number of challenge vectors on which <p', W'> = claim."""
    carried, n = 2, 1 + 4 * kappa
    guard = kappa if layout == "c" else 0
    L = carried + guard + n + kappa
    cols = times_x_matrix(F, ch, L)
    aux0 = carried + guard
    lanes, q = 1 << kappa, F.q
    ok = 0
    for _ in range(trials):
        P = [[rnd.randrange(q) if j < carried else 0 for j in range(L)] for _ in range(lanes)]
        W = [[rnd.randrange(q) if j < carried else 0 for j in range(L)] for _ in range(lanes)]
        g = [[rnd.randrange(q) for _ in range(4)] for _ in range(kappa)]
        cst = rnd.randrange(q)
        coef = [cst] + [x for gj in g for x in gj]
        for m, v in enumerate(coef):
            for b in (range(lanes) if layout == "a" else [lanes - 1]):
                P[b][aux0 + m] = v
        T = 0
        for p, w in zip(P, W):
            T ^= F.dot(p, w)
        G = cst
        for gj in g:
            G ^= gj[0]                                                  # lam(g_j) = [a] g_j
        rho = rnd.randrange(q)
        claim = F.mul(rho, T) ^ G
        W = [[F.mul(rho, x) for x in row] for row in W]
        Dj, ch_all = 0, []
        for j in range(kappa):
            Kj = cst
            for gj in g[j + 1:]:
                Kj ^= gj[0]
            u0, w, c0, c1 = scalars(F, cols, P, W)
            k0, k2, k3, k4 = Dj ^ Kj, g[j][1], g[j][2], g[j][3]          # the mask's message  g_j + D_j + K_j
            u0, w, c0, c1 = u0 ^ k0, w ^ k2, c0 ^ k3, c1 ^ k4 ^ k3
            a, b = rnd.randrange(q), rnd.randrange(q)
            claim = u0 ^ F.mul(b, c0) ^ F.mul(a, u0 ^ claim ^ F.mul(a, w) ^ F.mul(b, c0 ^ c1))
            Dj ^= sum_mono(F, g[j], a, b)
            P, W = fold(F, cols, P, W, a, b)
            ch_all.append((a, b))
        Wf = W[0][:]
        Wf[aux0] ^= 1
        for j, (a, b) in enumerate(ch_all):
            for e in range(4):
                Wf[aux0 + 1 + 4 * j + e] ^= mono(F, MON[e], a, b)
        ok += F.dot(P[0], Wf) == claim
    return ok


def sum_mono(F, gj, a, b):
    r = 0
    for e in range(4):
        r ^= F.mul(gj[e], mono(F, MON[e], a, b))
    return r


def pack(vals):
    x = 0
    for i, v in enumerate(vals):
        x |= v << (4 * i)
    return x


def game_values(F, ch, tables, seed):
    q = F.q
    carried, guard, n = 1, 1, 5
    L = carried + guard + n + 1
    aux0 = carried + guard
    cols = times_x_matrix(F, ch, L)
    rnd = random.Random(seed)
    npts = q * q
    mask1 = pack([1] * npts)
    pts = [(a, b) for a in range(q) for b in range(q)]
    basis = [pack([mono(F, e, a, b) for a, b in pts]) for e in [(0, 0)] + MON]   # 1, a, a^2, b, ab as value vectors
    scal = [[pack([F.mul(s, (v >> (4 * i)) & 15) for i in range(npts)]) for s in range(q)] for v in basis]
    # all messages k0 + k1 a + k2 a^2 + k3 b + k4 ab grouped by k0 + k1
    msgs = {c: [] for c in range(q)}
    for k in itertools.product(range(q), repeat=5):
        msgs[k[0] ^ k[1]].append(scal[0][k[0]] ^ scal[1][k[1]] ^ scal[2][k[2]] ^ scal[3][k[3]] ^ scal[4][k[4]])

    def zeros(x):
        z = (x | (x >> 1) | (x >> 2) | (x >> 3)) & mask1
        return npts - z.bit_count()

    def value(P, W, T):
        V = []
        for rho in range(q):
            Wr = [[F.mul(rho, x) for x in row] for row in W]
            H = []
            for a, b in pts:
                Pn, Wn = fold(F, cols, P, Wr, a, b)
                Wf = Wn[0][:]
                Wf[aux0] ^= 1
                for e in range(4):
                    Wf[aux0 + 1 + e] ^= mono(F, MON[e], a, b)
                H.append(F.dot(Pn[0], Wf))
            Hp = pack(H)
            V.append([max(zeros(Hp ^ m) for m in msgs[c]) for c in range(q)])
        return max(sum(V[rho][F.mul(rho, T) ^ G] for rho in range(q)) for G in range(q)) / (q * npts)

    Wt = [[3] + [0] * (L - 1), [5] + [0] * (L - 1)]
    out = {}
    for kind in ("honest layout (c)", "aux in every lane", "random aux and guard slots"):
        best = 0.0
        for _ in range(tables if kind.startswith("random") else max(2, tables // 6)):
            P = [[0] * L, [0] * L]
            P[0][0], P[1][0] = rnd.randrange(q), rnd.randrange(q)
            coef = [rnd.randrange(q) for _ in range(n)]
            for m, v in enumerate(coef):
                if kind.startswith("honest"):
                    P[1][aux0 + m] = v
                elif kind.startswith("aux in"):
                    P[0][aux0 + m] = P[1][aux0 + m] = v
                else:
                    P[0][aux0 + m], P[1][aux0 + m] = rnd.randrange(q), rnd.randrange(q)
            if kind.startswith("random"):
                P[0][1], P[1][1] = rnd.randrange(q), rnd.randrange(q)
            S = F.mul(P[0][0], 3) ^ F.mul(P[1][0], 5)
            best = max(best, value(P, Wt, S ^ 1))
        out[kind] = best
    return out


def main():
    rnd = random.Random(20261119)
    F = GF(4)
    for kappa in (1, 2):
        ch = Chain(F, [1, 2, 4, 8])
        res = {lay: layout_run(F, ch, kappa, lay, rnd, 300) for lay in "abc"}
        R.say(f"layout, GF(16), kappa = {kappa}, 300 honest runs each: accepted (a) every lane {res['a']}, "
              f"(b) all-G lane, no guard {res['b']}, (c) all-G lane with kappa guard slots {res['c']}")
        R.check(res["c"] == 300, f"kappa = {kappa}: layout (c) is complete (the folded aux slot holds the coefficient)")
        R.check(res["a"] < 300 and res["b"] < 300, f"kappa = {kappa}: layouts (a) and (b) are not complete (finding F-1)")
    F = GF(3)
    q = F.q
    vals = game_values(F, Chain(F, [1, 2, 4]), tables=36, seed=3)
    b2, b3 = 1 - (1 - 1 / q) * (1 - 2 / q), 1 - (1 - 1 / q) * (1 - 3 / q)
    for kind, v in vals.items():
        R.say(f"one affine round, GF(8), exact game value, {kind}: {v:.4f}")
    R.check(vals["honest layout (c)"] <= b2 + 1e-12, f"honest layout: {vals['honest layout (c)']:.4f} <= 1 - (1-1/q)(1-2/q) = {b2:.4f}")
    R.check(max(vals.values()) <= b3 + 1e-12, f"any committed table: {max(vals.values()):.4f} <= 1 - (1-1/q)(1-3/q) = {b3:.4f}")
    R.close()


if __name__ == "__main__":
    main()
