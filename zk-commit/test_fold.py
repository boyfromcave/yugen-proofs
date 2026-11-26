"""Lemma F: openings of deterministically folded codewords (FRI-Binius / BaseFold family).

One committed polynomial P_0 with 2^n message coefficients and T uniform coefficients in the
slots [2^n, 2^n + T), evaluated on D_0 = shift + S_0. Oracle i+1 is the fold of oracle i (one
variable per level, challenge gamma_i): P_{i+1}(q(x)) from the pair P_i(x), P_i(x + b_0), with
coefficients c'[j] = (1 + gamma) c[2j] + gamma c[2j+1]. Oracles 0..Lc-1 are committed with pair
leaves; a query opens one pair in each. The final polynomial P_Lc is sent masked:
P* = gt + c P_Lc, with the mask column G opened at the queries' final points.

Checked: the lane identity that makes the model faithful; the rank criterion (the view is
independent of the WHOLE message) holds when T >= Q * 2^Lc on a coset domain; it fails with
fewer random coefficients, on the linear domain when a query meets U, and when the final
polynomial is sent in clear. One instance is enumerated in full.

Sources and provenance (REFERENCES.md). Lemma F (T >= Q * 2^K) is Original (the Ycash developers,
2026) as far as checked. Related: Haböck, Al Kindi, "A note on adding zero-knowledge to STARK", ePrint 2024/1037, Section 2 (each fold halves the randomizer space on a multiplicative domain; no proof without
the mask polynomial, footnote 3).
"""
import itertools
import random
import sys

from ff import GF, Vars, fadd, fscale, lincomb, zk_rank_test, enumerate_view, tv_distance
from additive import Chain


def build(F, n, dim, Lc, T, Q, shift_on, final_mask, gam, bc, queries):
    V = Vars()
    coef = V.new("w", 1 << n) + V.new("enc", T)
    chain = Chain(F, [1 << i for i in range(dim + 1)])
    shift = (1 << dim) if shift_on else 0
    view = []
    pts = [chain.point(j, shift) for j in queries]
    for i in range(Lc):
        b0 = chain.basis[0]
        nxt, q = chain.image()
        for x in pts:
            for xx in (x, x ^ b0):
                view.append(lincomb(F, chain.novel_row(xx, len(coef)), coef))
        g = gam[i]
        folded = [fadd(fscale(F, 1 ^ g, coef[2 * j]), fscale(F, g, coef[2 * j + 1] if 2 * j + 1 < len(coef) else {}))
                  for j in range((len(coef) + 1) // 2)]
        chain, coef, pts = nxt, folded, [q(x) for x in pts]
    if final_mask:
        gt = V.new("bc", len(coef))
        view += [fadd(a, fscale(F, bc, c)) for a, c in zip(gt, coef)]
        for y in pts:
            view.append(lincomb(F, chain.novel_row(y, len(coef)), gt))
    else:
        view += coef
    return view, V, len(coef)


def lane_identity(F, out):
    """P(x) = f0(q(x)) + (x / b_0) f1(q(x)), f_b with coefficients c[b + 2j] in the image basis."""
    rnd = random.Random(7)
    chain = Chain(F, [1 << i for i in range(5)])
    nxt, q = chain.image()
    bad = 0
    for _ in range(200):
        c = [rnd.randrange(F.q) for _ in range(12)]
        x = rnd.randrange(F.q)
        lhs = F.dot(chain.novel_row(x, 12), c)
        nr = nxt.novel_row(q(x), 6)
        rhs = F.dot(nr, c[0::2]) ^ F.mul(F.mul(x, F.inv(chain.basis[0])), F.dot(nr, c[1::2]))
        bad += lhs != rhs
    out(f"lane identity P(x) = f0(q(x)) + (x/b0) f1(q(x)): {200 - bad}/200 random checks hold")
    return bad


def rank_part(F, out):
    rnd = random.Random(11)
    fails = 0
    cases = [
        ("T = Q 2^Lc, coset, masked final", dict(n=3, dim=5, Lc=2, T=8, Q=2, shift_on=True, final_mask=True), True, False),
        ("T = Q 2^Lc, coset, masked final (Q=3, Lc=1)", dict(n=3, dim=5, Lc=1, T=6, Q=3, shift_on=True, final_mask=True), True, False),
        ("T = Q 2^Lc, coset, masked final (Lc=3, Q=1)", dict(n=3, dim=5, Lc=3, T=8, Q=1, shift_on=True, final_mask=True), True, False),
        ("T = (Q-1) 2^Lc: too little randomness", dict(n=3, dim=5, Lc=2, T=4, Q=2, shift_on=True, final_mask=True), False, False),
        ("T = Q 2^(Lc-1): budget of one level less", dict(n=3, dim=5, Lc=3, T=4, Q=1, shift_on=True, final_mask=True), False, False),
        ("linear domain, a query in U", dict(n=3, dim=5, Lc=2, T=8, Q=2, shift_on=False, final_mask=True), False, True),
        ("final polynomial in clear", dict(n=3, dim=5, Lc=2, T=8, Q=2, shift_on=True, final_mask=False), False, False),
    ]
    for name, kw, expect, low in cases:
        good = bad = uni = 0
        for trial in range(120):
            gam = [rnd.randrange(F.q) for _ in range(kw["Lc"])]
            if trial < 4:
                gam = [(trial >> k) & 1 for k in range(kw["Lc"])]
            # queries with distinct final points: distinct classes modulo the fold kernel
            cls = rnd.sample(range(1 << (kw["dim"] - kw["Lc"])), kw["Q"])
            queries = [(c << kw["Lc"]) | rnd.randrange(1 << kw["Lc"]) for c in cls]
            if low:
                queries[0] = rnd.randrange(1 << kw["Lc"])
            view, V, flen = build(F, gam=gam, bc=rnd.randrange(1, F.q), queries=queries, **kw)
            widx = V.indices("w")
            ridx = [i for i in range(V.n) if i not in set(widx)]
            ok, rb, rab = zk_rank_test(F, view, [{i: 1} for i in widx], ridx)
            good += ok
            bad += not ok
            uni += rb == kw["Q"] * (kw["Lc"] + 1) + flen
        verdict = "PASS" if (bad == 0) == expect else "FAIL"
        fails += verdict == "FAIL"
        out(f"{verdict} {name}: hiding {good}, leaking {bad}, rank B at the accepting dimension {uni}/120")
    return fails


def enum_part(out):
    F = GF(4)
    fails = 0
    for name, T, expect in [("T = Q 2^Lc", 2, True), ("T too small", 0, False)]:
        same = diff = 0
        for gam in range(F.q):
            for qi in range(8):
                view, V, _ = build(F, n=1, dim=3, Lc=1, T=T, Q=1, shift_on=True, final_mask=True,
                                   gam=[gam], bc=3, queries=[qi])
                widx = V.indices("w")
                ridx = [i for i in range(V.n) if i not in set(widx)]
                w1 = {widx[0]: 5, widx[1]: 9}
                w2 = {widx[0]: 12, widx[1]: 2}
                d = tv_distance(enumerate_view(F, view, w1, ridx), enumerate_view(F, view, w2, ridx))
                same += d == 0
                diff += d > 0
        ok = (diff == 0) if expect else (diff > 0)
        fails += not ok
        out(f"{'PASS' if ok else 'FAIL'} enumeration GF(16), n=1, one fold, one query, {name}: "
            f"identical {same}, different {diff} (all gamma, all positions, every randomness value)")
    return fails


if __name__ == "__main__":
    lines = []
    out = lambda s: (print(s, flush=True), lines.append(s))
    F = GF(8)
    f = lane_identity(F, out) + rank_part(F, out) + enum_part(out)
    out(f"FAILURES {f}")
    open("results/fold.txt", "w").write("\n".join(lines) + "\n")
    sys.exit(1 if f else 0)
