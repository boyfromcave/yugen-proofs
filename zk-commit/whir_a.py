"""System A's hiding opening: construction W-I with the affine-combiner fold and the aux layout of
finding F-1 (docs/zk-wi-soundness.md 2.1; docs/zk-hiding-commitment.md 6.1, 6.2a). Toy model, exact.

Fold round (pinned leanVM verifier): lanes 2i (F) and 2i+1 (G) become G + (alpha + beta X) F, the
weights W_F + alpha (W_F + W_G); the prover sends (u0, w, c0, c1) and the claim becomes
u0 + beta c0 + alpha (u0 + claim + alpha w + beta (c0 + c1)).
Lane layout of a level: carried slots; kappa zero guard slots; 1 + 4 kappa aux slots, the mask
coefficients written into the LAST lane only; zeros; t uniform coefficients per lane at an aligned
offset that is a multiple of 2^ceil(log2(t + kappa)). The folded lane has lrow + kappa coefficients and is carried whole into the next oracle.
Mask (Theorem 1', u = 1): coefficients c and g_j = (a, a^2, b, ab) per round; message of round j is
g_j + D_j + K_j; final value sum_j g_j(alpha_j, beta_j) + c.
"""
from ff import Vars, fadd, fscale, lincomb
from additive import Chain

MON = [(1, 0), (2, 0), (0, 1), (1, 1)]


def mono(F, e, a, b):
    return F.mul(F.pow(a, e[0]), F.pow(b, e[1]))


class LevelA:
    def __init__(self, F, kappa, carried, Q, dim, t_deficit=0, narrow_align=False):
        self.kappa, self.lanes, self.carried, self.Q, self.dim = kappa, 1 << kappa, carried, Q, dim
        self.aux0 = carried + kappa
        self.nmask = 1 + 4 * kappa
        t = Q - t_deficit
        # aligned to 2^ceil(log2(t + kappa)): multiplication by X then never moves a random slot below aoff
        align = 1 << max(Q + kappa - 1, 0).bit_length() if not narrow_align else 1 << max(Q - 1, 0).bit_length()
        self.aoff = -(-(self.aux0 + self.nmask) // align) * align
        self.t, self.lrow = t, self.aoff + t
        self.Lf = self.lrow + kappa
        assert self.Lf <= 1 << dim
        self.ch = Chain(F, [1 << k for k in range(dim + 1)])
        pts = list(range(self.Lf))
        rows = [self.ch.novel_row(x, self.Lf) for x in pts]
        inv = invert(F, rows)
        # cols[c][j]: coefficient j of x * X_c
        self.cols = []
        for c in range(self.Lf - 1):
            vals = [F.mul(x, rows[i][c]) for i, x in enumerate(pts)]
            self.cols.append([F.dot(inv[j], vals) for j in range(self.Lf)])


def invert(F, M):
    n = len(M)
    A = [r[:] + [1 if i == j else 0 for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c])
        A[c], A[p] = A[p], A[c]
        iv = F.inv(A[c][c])
        A[c] = [F.mul(iv, v) for v in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [v ^ F.mul(f, w) for v, w in zip(A[i], A[c])]
    return [r[n:] for r in A]


def config(F, wit_rows, kappas, Qs, dims, t_deficit=0, narrow_align=False):
    levels, carried = [], wit_rows
    for i, k in enumerate(kappas):
        lv = LevelA(F, k, carried, Qs[i], dims[i], t_deficit, narrow_align)
        levels.append(lv)
        if i + 1 < len(kappas):
            carried = -(-lv.Lf // (1 << kappas[i + 1]))
    return levels


def times_x(F, lv, v, form):
    out = [{} if form else 0 for _ in range(lv.Lf)]
    for c, a in enumerate(v):
        if a:
            assert c < lv.Lf - 1, "degree overflow"
            for j, m in enumerate(lv.cols[c]):
                if m:
                    out[j] = fadd(out[j], fscale(F, m, a)) if form else out[j] ^ F.mul(a, m)
    return out


def fold_row(F, vals, x, rounds):
    for a, b in rounds:
        aff = a ^ F.mul(b, x)
        vals = [vals[2 * i + 1] ^ F.mul(aff, vals[2 * i]) for i in range(len(vals) // 2)]
    return vals[0]


def point(lv, q, shift=True):
    return lv.ch.point(q, (1 << lv.dim) if shift else 0)


def prove(F, levels, W0, chal, shift=True, mask=True, bc_mask=True, every_lane=False):
    """Symbolic honest prover. Returns (view forms, Vars)."""
    V = Vars()
    lv0 = levels[0]
    wit = V.new("w", lv0.lanes * lv0.carried)
    P = [[{} for _ in range(lv0.Lf)] for _ in range(lv0.lanes)]
    W = [[0] * lv0.Lf for _ in range(lv0.lanes)]
    for idx, f in enumerate(wit):
        P[idx % lv0.lanes][idx // lv0.lanes] = f
        W[idx % lv0.lanes][idx // lv0.lanes] = W0[idx]
    view = []
    for i, lv in enumerate(levels):
        c = chal[i]
        coef = V.new("mask", lv.nmask) if mask else [{} for _ in range(lv.nmask)]
        for m, f in enumerate(coef):
            for b in (range(lv.lanes) if every_lane else [lv.lanes - 1]):
                P[b][lv.aux0 + m] = f
        for b in range(lv.lanes):
            r = V.new("enc", lv.t)
            for s in range(lv.t):
                P[b][lv.aoff + s] = r[s]
        last = i == len(levels) - 1
        Pfull = [row[:] for row in P]
        cst, g = coef[0], [coef[1 + 4 * j:5 + 4 * j] for j in range(lv.kappa)]
        view.append(fadd(cst, *[gj[0] for gj in g]))                    # G
        W = [[F.mul(c["rho"], v) for v in row] for row in W]
        Dj, rounds = {}, []
        for j in range(lv.kappa):
            Kj = fadd(cst, *[gj[0] for gj in g[j + 1:]])
            u0 = w = c0 = c1 = {}
            for k in range(len(P) // 2):
                Fl, Gl, WF, WG = P[2 * k], P[2 * k + 1], W[2 * k], W[2 * k + 1]
                MF = times_x(F, lv, Fl, True)
                u0 = fadd(u0, lincomb(F, WF, Gl))
                w = fadd(w, lincomb(F, [x ^ y for x, y in zip(WF, WG)], Fl))
                c0 = fadd(c0, lincomb(F, WF, MF))
                c1 = fadd(c1, lincomb(F, WG, MF))
            view += [fadd(u0, Dj, Kj), fadd(w, g[j][1]), fadd(c0, g[j][2]), fadd(c1, g[j][3], g[j][2])]
            a, b = c["ab"][j]
            rounds.append((a, b))
            Dj = fadd(Dj, lincomb(F, [mono(F, e, a, b) for e in MON], g[j]))
            Pn, Wn = [], []
            for k in range(len(P) // 2):
                Fl, Gl = P[2 * k], P[2 * k + 1]
                MF = times_x(F, lv, Fl, True)
                Pn.append([fadd(x, fscale(F, a, y), fscale(F, b, z)) for x, y, z in zip(Gl, Fl, MF)])
                Wn.append([wf ^ F.mul(a, wf ^ wg) for wf, wg in zip(W[2 * k], W[2 * k + 1])])
            P, W = Pn, Wn
        Pf, Wf = P[0], W[0][:]
        Wf[lv.aux0] ^= 1
        for j, (a, b) in enumerate(rounds):
            for e in range(4):
                Wf[lv.aux0 + 1 + 4 * j + e] ^= mono(F, MON[e], a, b)
        rows = []
        for q in c["qpos"]:
            nr = lv.ch.novel_row(point(lv, q, shift), lv.Lf)
            rows += [lincomb(F, nr, Pfull[b]) for b in range(lv.lanes)]
        if not last:
            nx = levels[i + 1]
            view += rows
            for k, q in enumerate(c["qpos"]):
                nr = lv.ch.novel_row(point(lv, q, shift), lv.Lf)
                lam = F.pow(c["lam"], k + 1)
                Wf = [x ^ F.mul(lam, y) for x, y in zip(Wf, nr)]
            P = [[{} for _ in range(nx.Lf)] for _ in range(nx.lanes)]
            W = [[0] * nx.Lf for _ in range(nx.lanes)]
            for j in range(lv.Lf):
                P[j % nx.lanes][j // nx.lanes] = Pf[j]
                W[j % nx.lanes][j // nx.lanes] = Wf[j]
        else:
            gt = V.new("bc", lv.Lf) if bc_mask else [{} for _ in range(lv.Lf)]
            view.append(lincomb(F, Wf, gt))                             # mu
            view += [fadd(x, fscale(F, c["bc"], y)) for x, y in zip(gt, Pf)]   # P*
            view += rows
            for q in c["qpos"]:
                view.append(lincomb(F, lv.ch.novel_row(point(lv, q, shift), lv.Lf), gt))
    return view, V


def verify(F, levels, W0, claim, chal, vals, shift=True):
    it = iter(vals)
    lv0 = levels[0]
    W = [[0] * lv0.Lf for _ in range(lv0.lanes)]
    for idx, w in enumerate(W0):
        W[idx % lv0.lanes][idx // lv0.lanes] = w
    T = claim
    for i, lv in enumerate(levels):
        c = chal[i]
        T = F.mul(c["rho"], T) ^ next(it)
        W = [[F.mul(c["rho"], v) for v in row] for row in W]
        rounds = []
        for j in range(lv.kappa):
            u0, w, c0, c1 = (next(it) for _ in range(4))
            a, b = c["ab"][j]
            T = u0 ^ F.mul(b, c0) ^ F.mul(a, u0 ^ T ^ F.mul(a, w) ^ F.mul(b, c0 ^ c1))
            rounds.append((a, b))
            W = [[wf ^ F.mul(a, wf ^ wg) for wf, wg in zip(W[2 * k], W[2 * k + 1])] for k in range(len(W) // 2)]
        Wf = W[0][:]
        Wf[lv.aux0] ^= 1
        for j, (a, b) in enumerate(rounds):
            for e in range(4):
                Wf[lv.aux0 + 1 + 4 * j + e] ^= mono(F, MON[e], a, b)
        if i < len(levels) - 1:
            nx = levels[i + 1]
            for k, q in enumerate(c["qpos"]):
                x = point(lv, q, shift)
                v = fold_row(F, [next(it) for _ in range(lv.lanes)], x, rounds)
                lam = F.pow(c["lam"], k + 1)
                T ^= F.mul(lam, v)
                Wf = [p ^ F.mul(lam, y) for p, y in zip(Wf, lv.ch.novel_row(x, lv.Lf))]
            W = [[0] * nx.Lf for _ in range(nx.lanes)]
            for j in range(lv.Lf):
                W[j % nx.lanes][j // nx.lanes] = Wf[j]
        else:
            mu = next(it)
            star = [next(it) for _ in range(lv.Lf)]
            if F.dot(star, Wf) != mu ^ F.mul(c["bc"], T):
                return False
            folds = [fold_row(F, [next(it) for _ in range(lv.lanes)], point(lv, q, shift), rounds) for q in c["qpos"]]
            for q, fv in zip(c["qpos"], folds):
                if F.dot(lv.ch.novel_row(point(lv, q, shift), lv.Lf), star) != next(it) ^ F.mul(c["bc"], fv):
                    return False
    return True


def free_dimension(levels):
    return sum(1 + 4 * lv.kappa + lv.lanes * lv.Q for lv in levels) + levels[-1].Lf
