"""Masked sumcheck over GF(2^k): protocol view, mask families, simulator.

Conventions (docs/zk-masked-sumcheck.md, sections 1 and 3).

A polynomial is a dict {exponent tuple: coefficient}. `degs[j]` bounds the degree in variable j.
`W[j] = (w0, w1)` are the weights of the summation functional of variable j:

    lam_j(q) = w0 * q(0) + w1 * q(1).

The plain sumcheck has W[j] = (1, 1); the eq-weighted (zerocheck) sumcheck with reduced round
messages has W[j] = (1 + tau_j, tau_j). The round message is

    p_j(X) = sum_{b in {0,1}^{n-j}} prod_{k>j} W[k][b_k] * h(r_1..r_{j-1}, X, b),

sent as deg+1 coefficients, and the verifier checks lam_1(p_1) = claim, lam_j(p_j) =
p_{j-1}(r_{j-1}), p_n(r_n) = h(r).

The verifier's view of a masked run is the vector

    (G, coefficients of s_1, ..., coefficients of s_n, g(r))

with s_j the round polynomials of h = rho * f + g and G the mask's (weighted) cube sum.

Sources and provenance (REFERENCES.md). "Libra's mask" a0 + sum_i g_i(x_i) is Published:
Xie, Zhang, Zhang, Papamanthou, Song, "Libra: Succinct Zero-Knowledge Proofs with Optimal Prover
Computation", ePrint 2019/317, Section 4.1, Construction 1 and Theorem 3 (stated over a prime field).
That it fails for a plain sum in characteristic 2 is Published: Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint
2026/391 (revision of 2026-11-16), Section 2.5; the counts computed here are this project's.
The staircase mask and the family M_u (Theorem 1, Corollaries A to C, Theorem 2) are Original (the
Ycash developers, 2026) as far as checked; the published mask for the same problem is Definition 6.1 /
Lemma 6.2 of the second paper, a different family, which these tests do not exercise.
"""
import itertools

PLAIN = (1, 1)


def lam(e, w):
    """lam(x^e) = w0 * 0^e + w1 * 1^e."""
    return (w[0] if e == 0 else 0) ^ w[1]


def upoly(F, c, x):
    r = 0
    for a in reversed(c):
        r = F.mul(r, x) ^ a
    return r


def eval_poly(F, poly, pt):
    r = 0
    for exps, c in poly.items():
        t = c
        for x, e in zip(pt, exps):
            if not t:
                break
            t = F.mul(t, F.pow(x, e))
        r ^= t
    return r


def padd(p, q):
    r = dict(p)
    for k, v in q.items():
        r[k] = r.get(k, 0) ^ v
    return r


def pscale(F, c, p):
    return {k: F.mul(c, v) for k, v in p.items()}


def pmul(F, p, q):
    r = {}
    for k1, v1 in p.items():
        for k2, v2 in q.items():
            k = tuple(a + b for a, b in zip(k1, k2))
            r[k] = r.get(k, 0) ^ F.mul(v1, v2)
    return r


def mono(n, d):
    e = [0] * n
    for i, x in d.items():
        e[i] = x
    return tuple(e)


def round_polys(F, poly, n, degs, r, W):
    """(G, [p_1..p_n]) by the monomial formula."""
    ps = [[0] * (degs[j] + 1) for j in range(n)]
    G = 0
    for exps, c in poly.items():
        if not c:
            continue
        suf = [1] * (n + 1)
        for k in range(n - 1, -1, -1):
            suf[k] = F.mul(suf[k + 1], lam(exps[k], W[k]))
        G ^= F.mul(c, suf[0])
        pre = c
        for j in range(n):
            if not pre:
                break
            ps[j][exps[j]] ^= F.mul(pre, suf[j + 1])
            pre = F.mul(pre, F.pow(r[j], exps[j]))
    return G, ps


def round_poly_value_by_definition(F, poly, n, r, W, j, X):
    """p_{j+1}(X) (0-based j) straight from the definition: a sum over the cube."""
    s = 0
    for b in itertools.product((0, 1), repeat=n - j - 1):
        w = 1
        for k, bk in zip(range(j + 1, n), b):
            w = F.mul(w, W[k][bk])
        if w:
            s ^= F.mul(w, eval_poly(F, poly, list(r[:j]) + [X] + list(b)))
    return s


def cube_sum_by_definition(F, poly, n, W):
    s = 0
    for b in itertools.product((0, 1), repeat=n):
        w = 1
        for k, bk in enumerate(b):
            w = F.mul(w, W[k][bk])
        if w:
            s ^= F.mul(w, eval_poly(F, poly, b))
    return s


def view_of(F, poly, n, degs, r, W):
    """Linear map poly -> (G, round coefficients, poly(r))."""
    G, ps = round_polys(F, poly, n, degs, r, W)
    out = [G]
    for p in ps:
        out += p
    out.append(eval_poly(F, poly, r))
    return out


def real_view(F, f, g, n, degs, r, W, rho):
    """Honest prover's messages for witness polynomial f and mask polynomial g."""
    Gg, pg = round_polys(F, g, n, degs, r, W)
    _, pf = round_polys(F, f, n, degs, r, W)
    out = [Gg]
    for a, b in zip(pf, pg):
        out += [F.mul(rho, x) ^ y for x, y in zip(a, b)]
    out.append(eval_poly(F, g, r))
    return out


def u_poly(F, n, k, w):
    """A polynomial u in x_k of degree <= 1 with lam_k(u) = 1."""
    if w[1]:
        return {mono(n, {k: 1}): F.inv(w[1])}            # x_k / w1
    return {mono(n, {}): F.inv(w[0])}                    # constant 1 / w0  (w1 = 0)


def mask_basis(F, kind, n, degs, W=None):
    """Basis polynomials of a mask family; the mask is a uniform combination of them."""
    W = W or [PLAIN] * n
    one = {mono(n, {}): 1}
    B = []
    if kind == "libra":            # a0 + sum_i g_i(x_i)                      (ePrint 2019/317)
        B.append(one)
        for i in range(n):
            for e in range(degs[i] + 1):
                B.append({mono(n, {i: e}): 1})
    elif kind == "weighted":       # sum_i g_i(x_i) prod_{k != i} (1 + x_k)    (yugen-zk-b experiment)
        for i in range(n):
            cof = one
            for k in range(n):
                if k != i:
                    cof = pmul(F, cof, {mono(n, {}): 1, mono(n, {k: 1}): 1})
            for e in range(degs[i] + 1):
                B.append(pmul(F, {mono(n, {i: e}): 1}, cof))
    elif kind == "stair":          # c + sum_j ghat_j(x_j) prod_{k>j} x_k, ghat_j(0) = 0: n d + 1 coefficients
        B.append(one)
        for j in range(n):
            for e in range(1, degs[j] + 1):
                d = {k: 1 for k in range(j + 1, n)}
                d[j] = e
                B.append({mono(n, d): 1})
    elif kind == "stair_full":     # c + sum_j g_j(x_j) prod_{k>j} x_k: n (d + 1) + 1 coefficients, redundant
        B.append(one)
        for j in range(n):
            for e in range(degs[j] + 1):
                d = {k: 1 for k in range(j + 1, n)}
                d[j] = e
                B.append({mono(n, d): 1})
    elif kind == "stair_u":        # c + sum_j g_j(x_j) prod_{k>j} u_k(x_k), lam_k(u_k) = 1 (general weights)
        B.append(one)
        for j in range(n):
            cof = one
            for k in range(j + 1, n):
                cof = pmul(F, cof, u_poly(F, n, k, W[k]))
            for e in range(degs[j] + 1):
                B.append(pmul(F, {mono(n, {j: e}): 1}, cof))
    elif kind == "cfs":            # every monomial of individual degree <= d: prod (d_j + 1) coefficients
        for exps in itertools.product(*[range(d + 1) for d in degs]):
            B.append({tuple(exps): 1})
    else:
        raise ValueError(kind)
    return B


def combine(F, basis, coeffs):
    g = {}
    for c, b in zip(coeffs, basis):
        if c:
            g = padd(g, pscale(F, c, b))
    return g


def sim_randomness(degs):
    return 1 + sum(degs)


def simulate(F, n, degs, W, S, rho, r, f_r, rnd):
    """The simulator of Theorem 1. Inputs: the public claim S, the challenges, ONE value f(r).

    rnd: 1 + sum(degs) uniform field elements. Output: the same vector as real_view.
    """
    it = iter(rnd)
    G = next(it)
    target = F.mul(rho, S) ^ G
    out = [G]
    for j in range(n):
        w, d = W[j], degs[j]
        piv = 1 if w[1] else 0
        s = [0] * (d + 1)
        acc = 0
        for e in range(d + 1):
            if e == piv:
                continue
            s[e] = next(it)
            acc ^= F.mul(s[e], lam(e, w))
        s[piv] = F.mul(target ^ acc, F.inv(lam(piv, w)))
        out += s
        target = upoly(F, s, r[j])
    out.append(target ^ F.mul(rho, f_r))
    return out


def simulate_adaptive(F, n, degs, W, S, f, rnd, rho_fn, r_fn):
    """Simulator against a deterministic verifier strategy; f is queried once, at r."""
    it = iter(rnd)
    G = next(it)
    rho = rho_fn(G)
    target = F.mul(rho, S) ^ G
    out = [G]
    r = []
    for j in range(n):
        w, d = W[j], degs[j]
        piv = 1 if w[1] else 0
        s = [0] * (d + 1)
        acc = 0
        for e in range(d + 1):
            if e == piv:
                continue
            s[e] = next(it)
            acc ^= F.mul(s[e], lam(e, w))
        s[piv] = F.mul(target ^ acc, F.inv(lam(piv, w)))
        out += s
        r.append(r_fn(j, out))
        target = upoly(F, s, r[j])
    out.append(target ^ F.mul(rho, eval_poly(F, f, r)))      # the single query to f
    return tuple(out), rho, tuple(r)


def real_adaptive(F, f, g, n, degs, W, rho_fn, r_fn):
    """Honest prover against the same deterministic verifier strategy."""
    G = cube_sum_by_definition(F, g, n, W) if n <= 4 else round_polys(F, g, n, degs, [0] * n, W)[0]
    rho = rho_fn(G)
    h = padd(pscale(F, rho, f), g)
    out = [G]
    r = [0] * n
    for j in range(n):
        _, ps = round_polys(F, h, n, degs, r, W)     # p_j depends on r_1..r_{j-1} only
        out += ps[j]
        r[j] = r_fn(j, out)
    out.append(eval_poly(F, g, r))
    return tuple(out), rho, tuple(r)
