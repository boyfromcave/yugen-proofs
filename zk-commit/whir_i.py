"""Hiding WHIR-style opening over additive codes, construction W-I of docs/zk-hiding-commitment.md.

Toy model with exact arithmetic. The honest prover runs on affine forms (ff.py), so its output is
the exact affine map from (witness, randomness) to the verifier's algebraic view. The verifier is
a separate concrete function that sees only the view, the challenges and the public claim.

Objects (level i = 0..L-1):
  P_i     the current polynomial: a table [lane b][slot j] of coefficients. Slots hold, in order,
          the carried coefficients (witness at level 0; the previous level's folded polynomial,
          its excess included, afterwards), the aux rows (one row per mask coefficient of this
          level, the same value in every lane), zeros, and from slot aoff the t fresh uniform
          coefficients of each lane.
  oracle  row y of oracle i is (lane_b(y))_b,  lane_b(y) = sum_j P_i[b][j] X_j(y),  y in D_i.
  W       public weight table of the same shape; the relation carried is  <P, W> = T.
One level:
  1. mask: prover sends G = sum over the cube of the mask g_i; verifier sends rho;
     T <- rho T + G, W <- rho W.
  2. kappa rounds of sumcheck over the lane variables on  sum_j P[b][j] W[b][j] + g_i(b):
     round values at X = 0, 1, 2; check s(0) + s(1) = T; T <- s(gamma).
  3. after the fold the aux slot of mask coefficient m holds exactly that coefficient; its
     weight becomes the mask monomial at gamma. Relation: <P', W'> = T on the folded lane P'.
  4. not the last level: commit oracle i+1 (P' re-laned, new aux rows, fresh randomness);
     out-of-domain answers y = P'(rho_ood); open Q rows of oracle i, v_q = fold of the row;
     T <- T + sum lam^k (answers), W' gains the matching evaluation weights.
  5. last level: a fresh uniform polynomial gt of the folded lane's length was committed as one
     more column G of the last oracle. Prover sends mu = <gt, W'>; verifier sends c; prover
     sends P* = gt + c P'; verifier checks <P*, W'> = mu + c T, opens Q rows and G there and
     checks  P*(y) = G(y) + c * fold(row).

Sources and provenance (REFERENCES.md). W-I adapts Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint
2026/391 (revision of 2026-11-16): masked sumcheck with the mask's final value kept in the relation (Section 6,
Construction 6.4), base case (Construction 7.2), secrets inside the rows of the main oracles (Section
11). Different here and Original (the Ycash developers, 2026) as far as checked: coset domain with an
aligned high-offset pad (Lemma E), the claim-level mask of Theorem 1' instead of the paper's U_sigma,
the out-of-domain budget rule (Lemma O) instead of private zero-evaders (the paper's Lemma 9.4).
"""
import itertools

from ff import Vars, const, fadd, fscale, lincomb, evalf
from additive import Chain

PTS = (0, 1, 2)


class Level:
    def __init__(self, kappa, carried, t, Q, ood, dim):
        self.kappa, self.lanes = kappa, 1 << kappa
        self.carried = carried                     # slots per lane holding carried coefficients
        self.nmask = 1 + 2 * kappa                 # staircase mask, degree 2
        self.aux = list(range(carried, carried + self.nmask))
        m = carried + self.nmask
        align = 1 << max(t - 1, 0).bit_length()
        self.aoff = -(-m // align) * align
        self.t, self.Q, self.ood, self.dim = t, Q, ood, dim
        self.lrow = self.aoff + t
        assert self.lrow <= 1 << dim, "code dimension exceeds the domain"


class Config:
    def __init__(self, F, wit_rows, kappas, Qs, oods, dims, shift=True, t_deficit=0,
                 mask="stair", bc_mask=True):
        self.F, self.shift, self.mask, self.bc_mask = F, shift, mask, bc_mask
        self.levels = []
        carried = wit_rows
        for i, kappa in enumerate(kappas):
            last = i == len(kappas) - 1
            ood = 0 if last else oods[i]
            lv = Level(kappa, carried, Qs[i] + ood - t_deficit, Qs[i], ood, dims[i])
            self.levels.append(lv)
            if not last:
                carried = -(-lv.lrow // (1 << kappas[i + 1]))
        self.chains = [Chain(F, [1 << k for k in range(lv.dim + 1)]) for lv in self.levels]
        self.wit_rows = wit_rows

    def point(self, i, idx):
        lv = self.levels[i]
        return self.chains[i].point(idx, (1 << lv.dim) if self.shift else 0)


# ---------------------------------------------------------------- mask families (degree 2)

def mask_monomials(kind, kappa):
    """Exponent tuples of the mask basis: constant first, then two per variable."""
    mons = [tuple([0] * kappa)]
    for j in range(kappa):
        for e in (1, 2):
            ex = [0] * kappa
            ex[j] = e
            if kind == "stair":
                for k in range(j + 1, kappa):
                    ex[k] = 1
            mons.append(tuple(ex))
    return mons


def mono_val(F, ex, pt):
    r = 1
    for e, x in zip(ex, pt):
        for _ in range(e):
            r = F.mul(r, x)
    return r


def mask_partial(F, mons, prefix, X, kappa):
    """For each monomial: sum over the remaining cube of mono(prefix, X, b)."""
    rest = kappa - len(prefix) - (0 if X is None else 1)
    head = list(prefix) + ([] if X is None else [X])
    out = []
    for ex in mons:
        s = 0
        for b in itertools.product((0, 1), repeat=rest):
            s ^= mono_val(F, ex, head + list(b))
        out.append(s)
    return out


# ---------------------------------------------------------------- shared public computations

def fold_tab(F, tab, x, scale_fn):
    """Bind the lowest lane bit of a table [lane][slot] at x."""
    return [[scale_fn(tab[2 * b][j], tab[2 * b + 1][j], x) for j in range(len(tab[0]))]
            for b in range(len(tab) // 2)]


def mix_const(F):
    return lambda a, b, x: F.mul(1 ^ x, a) ^ F.mul(x, b)


def mix_form(F):
    return lambda a, b, x: fadd(fscale(F, 1 ^ x, a), fscale(F, x, b))


def relane(tab_row, lanes, rows, zero):
    out = [[zero for _ in range(rows)] for _ in range(lanes)]
    for j, v in enumerate(tab_row):
        out[j % lanes][j // lanes] = v
    return out


def eq_weights(F, gam):
    w = [1]
    for g in gam:
        w = [F.mul(v, 1 ^ g) for v in w] + [F.mul(v, g) for v in w]
    return w


# ---------------------------------------------------------------- prover (symbolic)

def prove(cfg, W0, chal):
    """Returns (view, V): view is a list of (label, form); V the variable allocator."""
    F, V = cfg.F, Vars()
    L = len(cfg.levels)
    lv0 = cfg.levels[0]
    wit = V.new("w", lv0.lanes * cfg.wit_rows)                    # index b + lanes * row
    P = [[{} for _ in range(lv0.lrow)] for _ in range(lv0.lanes)]
    W = [[0] * lv0.lrow for _ in range(lv0.lanes)]
    for idx, f in enumerate(wit):
        P[idx % lv0.lanes][idx // lv0.lanes] = f
        W[idx % lv0.lanes][idx // lv0.lanes] = W0[idx]
    view = []
    for i, lv in enumerate(cfg.levels):
        ch, c = cfg.chains[i], chal[i]
        if cfg.mask == "none":
            a = [{} for _ in range(lv.nmask)]
        else:
            a = V.new("mask", lv.nmask)
        for m, row in enumerate(lv.aux):
            for b in range(lv.lanes):
                P[b][row] = a[m]
        rnd = [V.new("enc", lv.t) for _ in range(lv.lanes)]
        for b in range(lv.lanes):
            for s in range(lv.t):
                P[b][lv.aoff + s] = rnd[b][s]
        last = i == L - 1
        if last:
            gt = V.new("bc", lv.lrow) if cfg.bc_mask else [{} for _ in range(lv.lrow)]
        Pfull = [row[:] for row in P]
        mons = mask_monomials("stair" if cfg.mask == "none" else cfg.mask, lv.kappa)
        view.append((f"G{i}", lincomb(F, mask_partial(F, mons, [], None, lv.kappa), a)))
        W = [[F.mul(c["rho"], v) for v in row] for row in W]
        Pt, Wt, gam = P, W, []
        for j in range(lv.kappa):
            for X in PTS:
                PX, WX = fold_tab(F, Pt, X, mix_form(F)), fold_tab(F, Wt, X, mix_const(F))
                s = lincomb(F, mask_partial(F, mons, gam, X, lv.kappa), a)
                for prow, wrow in zip(PX, WX):
                    s = fadd(s, lincomb(F, wrow, prow))
                view.append((f"s{i}.{j}({X})", s))
            g = c["gam"][j]
            gam.append(g)
            Pt, Wt = fold_tab(F, Pt, g, mix_form(F)), fold_tab(F, Wt, g, mix_const(F))
        Pf, Wf = Pt[0], Wt[0][:]
        for m, row in enumerate(lv.aux):
            Wf[row] ^= mono_val(F, mons[m], gam)
        eqw = eq_weights(F, gam)

        def open_rows(positions):
            rows = []
            for q in positions:
                nr = ch.novel_row(cfg.point(i, q), lv.lrow)
                rows.append([lincomb(F, nr, Pfull[b]) for b in range(lv.lanes)])
            return rows
        if not last:
            nx = cfg.levels[i + 1]
            for k, rho in enumerate(c["ood"]):
                view.append((f"ood{i}.{k}", lincomb(F, ch.novel_row(rho, lv.lrow), Pf)))
            for q, row in zip(c["qpos"], open_rows(c["qpos"])):
                for b, f in enumerate(row):
                    view.append((f"row{i}@{q}[{b}]", f))
            for k, rho in enumerate(c["ood"]):
                wv = ch.novel_row(rho, lv.lrow)
                lam = pow_f(F, c["lam"], k + 1)
                Wf = [w ^ F.mul(lam, x) for w, x in zip(Wf, wv)]
            for k, q in enumerate(c["qpos"]):
                wv = ch.novel_row(cfg.point(i, q), lv.lrow)
                lam = pow_f(F, c["lam"], len(c["ood"]) + k + 1)
                Wf = [w ^ F.mul(lam, x) for w, x in zip(Wf, wv)]
            P = relane(Pf, nx.lanes, nx.lrow, {})
            W = relane(Wf, nx.lanes, nx.lrow, 0)
        else:
            view.append(("mu", lincomb(F, Wf, gt)))
            star = [fadd(g_, fscale(F, c["bc"], p)) for g_, p in zip(gt, Pf)]
            for j, f in enumerate(star):
                view.append((f"P*[{j}]", f))
            for q, row in zip(c["qpos"], open_rows(c["qpos"])):
                for b, f in enumerate(row):
                    view.append((f"row{i}@{q}[{b}]", f))
            for q in c["qpos"]:
                nr = ch.novel_row(cfg.point(i, q), lv.lrow)
                view.append((f"Gcol@{q}", lincomb(F, nr, gt)))
    return view, V


def pow_f(F, x, e):
    r = 1
    for _ in range(e):
        r = F.mul(r, x)
    return r


# ---------------------------------------------------------------- verifier (concrete)

def verify(cfg, W0, claim, chal, vals):
    """vals: the view's values in the prover's order. Returns True iff every check passes."""
    F = cfg.F
    it = iter(vals)
    lv0 = cfg.levels[0]
    W = [[0] * lv0.lrow for _ in range(lv0.lanes)]
    for idx, w in enumerate(W0):
        W[idx % lv0.lanes][idx // lv0.lanes] = w
    T, L = claim, len(cfg.levels)
    for i, lv in enumerate(cfg.levels):
        ch, c = cfg.chains[i], chal[i]
        mons = mask_monomials("stair" if cfg.mask == "none" else cfg.mask, lv.kappa)
        G = next(it)
        T = F.mul(c["rho"], T) ^ G
        W = [[F.mul(c["rho"], v) for v in row] for row in W]
        Wt, gam = W, []
        for j in range(lv.kappa):
            s = [next(it) for _ in PTS]
            if s[0] ^ s[1] != T:
                return False
            g = c["gam"][j]
            gam.append(g)
            T = F.interp(PTS, s, g)
            Wt = fold_tab(F, Wt, g, mix_const(F))
        Wf = Wt[0][:]
        for m, row in enumerate(lv.aux):
            Wf[row] ^= mono_val(F, mons[m], gam)
        eqw = eq_weights(F, gam)
        if i < L - 1:
            nx = cfg.levels[i + 1]
            answers, weights = [], []
            for rho in c["ood"]:
                answers.append(next(it))
                weights.append(ch.novel_row(rho, lv.lrow))
            for q in c["qpos"]:
                row = [next(it) for _ in range(lv.lanes)]
                answers.append(F.dot(eqw, row))
                weights.append(ch.novel_row(cfg.point(i, q), lv.lrow))
            for k, (ans, wv) in enumerate(zip(answers, weights)):
                lam = pow_f(F, c["lam"], k + 1)
                T ^= F.mul(lam, ans)
                Wf = [w ^ F.mul(lam, x) for w, x in zip(Wf, wv)]
            W = relane(Wf, nx.lanes, nx.lrow, 0)
        else:
            mu = next(it)
            star = [next(it) for _ in range(lv.lrow)]
            if F.dot(star, Wf) != mu ^ F.mul(c["bc"], T):
                return False
            folds = [F.dot(eqw, [next(it) for _ in range(lv.lanes)]) for _ in c["qpos"]]
            for q, fv in zip(c["qpos"], folds):
                gy = next(it)
                nr = ch.novel_row(cfg.point(i, q), lv.lrow)
                if F.dot(nr, star) != gy ^ F.mul(c["bc"], fv):
                    return False
    return True


def free_dimension(cfg):
    """Dimension of the set of accepting views (for fixed challenges)."""
    d = 0
    for i, lv in enumerate(cfg.levels):
        d += 1 + 2 * lv.kappa + lv.ood + lv.lanes * lv.Q
    return d + cfg.levels[-1].lrow


def sample_challenges(cfg, rnd, special=None):
    F, chal = cfg.F, []
    for i, lv in enumerate(cfg.levels):
        amb = 1 << (lv.dim + 1)
        ood = rnd.sample(range(amb, F.q), lv.ood)
        chal.append({
            "rho": rnd.randrange(1, F.q),
            "gam": [rnd.randrange(F.q) for _ in range(lv.kappa)],
            "ood": ood,
            "qpos": sorted(rnd.sample(range(1 << lv.dim), lv.Q)),
            "lam": rnd.randrange(1, F.q),
            "bc": rnd.randrange(1, F.q),
        })
        if special is not None:
            chal[-1]["gam"] = [special[(i + j) % len(special)] for j in range(lv.kappa)]
    return chal
