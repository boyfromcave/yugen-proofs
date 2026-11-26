"""Concrete provers for construction W-I (eq-fold), honest and cheating, run against the verifier of
../zk-commit/whir_i.py. Standard library only.

The harness `transcript` enforces the order of the protocol: a prover method receives only the
challenges that precede the message it returns, and every oracle is copied when it is committed, so
a strategy cannot adapt a committed word. Knobs of `Prover` (all default to honest behaviour):

    claim         the public claim T (default: the true value)
    target_rho    level -> rho0: G is chosen so that the masked claim becomes true iff rho = rho0
    cheat_rounds  on a false round claim send the degree-2 message that agrees with the true round
                  polynomial at as many points as its degree allows (2, or 3 when the aux rows make
                  the true polynomial cubic)
    aux_tables    level -> table [lane][m] written into the aux rows instead of a lane-constant mask
    switch        level -> True: when the folded relation is false, commit a different polynomial
                  p'' with <p'', W'> = T that agrees with the true fold on lrow - 1 domain points
    target_c      c0: mu is chosen so that the base-case check holds for the true fold iff c = c0
    swap_final    when the base-case relation is false send a P* that satisfies the linear check and
                  agrees with Gcol + c fold on lrow - 1 domain points
    corrupt       function (level, words, gcol) -> None, applied to a word before it is committed
    delta0        a polynomial (lrow_0 coefficients) added to every lane of the level-0 table
"""
import itertools

from common import solve
from whir_i import PTS, eq_weights, fold_tab, mask_monomials, mix_const, mono_val, pow_f, relane, verify  # noqa: F401


class Prover:
    def __init__(self, cfg, W0, wit, rnd, claim=None, target_rho=None, cheat_rounds=False, aux_tables=None,
                 switch=None, target_c=None, swap_final=False, corrupt=None, delta0=None):
        self.cfg, self.F, self.rnd = cfg, cfg.F, rnd
        self.k = dict(target_rho=target_rho or {}, cheat_rounds=cheat_rounds, aux_tables=aux_tables or {},
                      switch=switch or {}, target_c=target_c, swap_final=swap_final, corrupt=corrupt)
        lv0 = cfg.levels[0]
        self.P = [[0] * lv0.lrow for _ in range(lv0.lanes)]
        self.W = [[0] * lv0.lrow for _ in range(lv0.lanes)]
        for idx, v in enumerate(wit):
            self.P[idx % lv0.lanes][idx // lv0.lanes] = v
            self.W[idx % lv0.lanes][idx // lv0.lanes] = W0[idx]
        if delta0:                                                      # the same polynomial added to every lane
            for b in range(lv0.lanes):
                self.P[b] = [p ^ z for p, z in zip(self.P[b], delta0)]
        self.true0 = self.dot2(self.P, self.W)
        self.T = self.true0 if claim is None else claim
        self.oracle, self.gcol = {}, {}
        self.log = []                                                   # which gambles were taken

    def dot2(self, P, W):
        r = 0
        for p, w in zip(P, W):
            r ^= self.F.dot(p, w)
        return r

    # ---- commitment of oracle i (called with self.P holding the carried coefficients)
    def commit(self, i):
        F, lv, rnd = self.F, self.cfg.levels[i], self.rnd
        tab = self.k["aux_tables"].get(i)
        mask = [rnd.randrange(F.q) for _ in range(lv.nmask)]
        for m, row in enumerate(lv.aux):
            for b in range(lv.lanes):
                self.P[b][row] = tab[b][m] if tab else mask[m]
        for b in range(lv.lanes):
            for s in range(lv.t):
                self.P[b][lv.aoff + s] = rnd.randrange(F.q)
        last = i == len(self.cfg.levels) - 1
        self.gt = [rnd.randrange(F.q) for _ in range(lv.lrow)] if last else None
        ch, words, gcol = self.cfg.chains[i], [], []
        for q in range(1 << lv.dim):
            nr = ch.novel_row(self.cfg.point(i, q), lv.lrow)
            words.append([F.dot(nr, self.P[b]) for b in range(lv.lanes)])
            if last:
                gcol.append(F.dot(nr, self.gt))
        if self.k["corrupt"]:
            self.k["corrupt"](i, words, gcol)
        self.oracle[i], self.gcol[i] = [r[:] for r in words], gcol[:]
        self.mons = mask_monomials("stair", lv.kappa)
        self.Pt, self.Wt, self.gam, self.i = self.P, self.W, [], i

    # ---- the true summand, summed over the remaining cube, with the next variable at X
    def true_round(self, X):
        F, lv = self.F, self.cfg.levels[self.i]
        PX, WX = fold_tab(F, self.Pt, X, mix_const(F)), fold_tab(F, self.Wt, X, mix_const(F))
        rest = lv.kappa - len(self.gam) - 1
        s = 0
        for b, (prow, wrow) in enumerate(zip(PX, WX)):
            s ^= F.dot(prow, wrow)
            pt = self.gam + [X] + [(b >> k) & 1 for k in range(rest)]
            for m, row in enumerate(lv.aux):
                s ^= F.mul(prow[row], mono_val(F, self.mons[m], pt))
        return s

    def send_G(self, i):
        F, lv = self.F, self.cfg.levels[i]
        g = 0
        for b in range(lv.lanes):
            pt = [(b >> k) & 1 for k in range(lv.kappa)]
            for m, row in enumerate(lv.aux):
                g ^= F.mul(self.P[b][row], mono_val(F, self.mons[m], pt))
        S = self.dot2(self.P, self.W)
        self.Gtrue, self.S = g, S
        r0 = self.k["target_rho"].get(i)
        if r0 is not None and S != self.T:
            g ^= F.mul(r0, S ^ self.T)
            self.log.append(f"rho{i}")
        self.G = g
        return g

    def recv_rho(self, i, rho):
        F = self.F
        self.T = F.mul(rho, self.T) ^ self.G
        self.W = [[F.mul(rho, v) for v in row] for row in self.W]
        self.Wt = self.W

    def send_round(self):
        F = self.F
        h = [self.true_round(X) for X in range(min(F.q, 16))]            # true round polynomial on 16 points
        s = [h[0], h[1], h[2]]
        quad = all(F.interp(PTS, s, x) == h[x] for x in range(3, len(h)))
        if quad and h[0] ^ h[1] == self.T:
            return s
        if not self.k["cheat_rounds"]:
            d = self.T ^ h[0] ^ h[1]                                     # keep the sum check, no chosen agreement
            return [h[0] ^ d, h[1], h[2]]
        if not quad:                                                    # cubic truth: agree at three points
            for tri in itertools.combinations(range(2, len(h)), 3):
                vals = [h[x] for x in tri]
                s0, s1 = F.interp(tri, vals, 0), F.interp(tri, vals, 1)
                if s0 ^ s1 == self.T:
                    self.log.append("roots3")
                    return [s0, s1, F.interp(tri, vals, 2)]
        d = self.T ^ h[0] ^ h[1]                                         # quadratic correction with roots a, b
        a, b = 2, 4
        inv = F.inv(1 ^ a ^ b)
        self.log.append("roots2")
        return [h[x] ^ F.mul(d, F.mul(F.mul(x ^ a, x ^ b), inv)) for x in PTS]

    def recv_gamma(self, s, g):
        F = self.F
        self.T = F.interp(PTS, s, g)
        self.gam.append(g)
        self.Pt, self.Wt = fold_tab(F, self.Pt, g, mix_const(F)), fold_tab(F, self.Wt, g, mix_const(F))

    def end_fold(self):
        F, lv = self.F, self.cfg.levels[self.i]
        self.Pf, self.Wf = self.Pt[0][:], self.Wt[0][:]
        for m, row in enumerate(lv.aux):
            self.Wf[row] ^= mono_val(F, self.mons[m], self.gam)

    def vanishing_with(self, i, value, avoid=()):
        """z (lrow coefficients) with <z, Wf> = value and z = 0 on lrow - 1 domain points of level i."""
        F, lv, ch = self.F, self.cfg.levels[i], self.cfg.chains[i]
        pts = [q for q in range(1 << lv.dim) if q not in avoid]
        for start in range(len(pts) - lv.lrow + 2):
            sel = pts[start:start + lv.lrow - 1]
            rows = [ch.novel_row(self.cfg.point(i, q), lv.lrow) for q in sel] + [self.Wf]
            z = solve(F, rows, [0] * (lv.lrow - 1) + [value])
            if z is not None:
                return z
        return None

    def commit_next(self, i):
        F = self.F
        if self.k["switch"].get(i) and F.dot(self.Pf, self.Wf) != self.T:
            z = self.vanishing_with(i, F.dot(self.Pf, self.Wf) ^ self.T)
            if z is not None:
                self.Pf = [p ^ v for p, v in zip(self.Pf, z)]
                self.log.append(f"switch{i}")
        nx = self.cfg.levels[i + 1]
        self.P = relane(self.Pf, nx.lanes, nx.lrow, 0)
        self.Wnext_base = self.Wf
        self.commit(i + 1)

    def answers(self, i, ood, qpos, lam):
        """Out-of-domain answers; then the claim and weight updates the verifier makes."""
        F, lv, ch = self.F, self.cfg.levels[i], self.cfg.chains[i]
        eqw = eq_weights(F, self.gam_prev)
        ans, wts = [], []
        for rho in ood:
            nr = ch.novel_row(rho, lv.lrow)
            ans.append(F.dot(nr, self.Pf_prev))
            wts.append(nr)
        out = ans[:]
        for q in qpos:
            ans.append(F.dot(eqw, self.oracle[i][q]))
            wts.append(ch.novel_row(self.cfg.point(i, q), lv.lrow))
        Wf = self.Wnext_base
        for k, (a, wv) in enumerate(zip(ans, wts)):
            l = pow_f(F, lam, k + 1)
            self.T ^= F.mul(l, a)
            Wf = [w ^ F.mul(l, x) for w, x in zip(Wf, wv)]
        nx = self.cfg.levels[i + 1]
        self.W = relane(Wf, nx.lanes, nx.lrow, 0)
        self.Wt = self.W
        return out

    def send_mu(self):
        F = self.F
        mu = F.dot(self.gt, self.Wf)
        S = F.dot(self.Pf, self.Wf)
        if self.k["target_c"] is not None and S != self.T:
            mu ^= F.mul(self.k["target_c"], S ^ self.T)
            self.log.append("c")
        self.mu = mu
        return mu

    def send_pstar(self, c):
        F, i = self.F, self.i
        star = [g ^ F.mul(c, p) for g, p in zip(self.gt, self.Pf)]
        deficit = F.dot(star, self.Wf) ^ self.mu ^ F.mul(c, self.T)
        if deficit and self.k["swap_final"]:
            z = self.vanishing_with(i, deficit)
            if z is not None:
                star = [s ^ v for s, v in zip(star, z)]
                self.log.append("swap")
        return star


def transcript(cfg, prover, chal):
    """Run the prover against the challenges in protocol order; return the verifier's input list."""
    vals, L = [], len(cfg.levels)
    prover.commit(0)
    for i, lv in enumerate(cfg.levels):
        c = chal[i]
        vals.append(prover.send_G(i))
        prover.recv_rho(i, c["rho"])
        for j in range(lv.kappa):
            s = prover.send_round()
            vals += s
            prover.recv_gamma(s, c["gam"][j])
        prover.end_fold()
        if i < L - 1:
            prover.gam_prev = prover.gam[:]
            prover.commit_next(i)                                       # oracle i+1 fixed before ood, qpos, lam
            prover.Pf_prev = prover.Pf[:]
            vals += prover.answers(i, c["ood"], c["qpos"], c["lam"])
            for q in c["qpos"]:
                vals += prover.oracle[i][q]
        else:
            vals.append(prover.send_mu())
            vals += prover.send_pstar(c["bc"])                           # P* fixed before the positions
            for q in c["qpos"]:
                vals += prover.oracle[i][q]
            for q in c["qpos"]:
                vals.append(prover.gcol[i][q])
    return vals
