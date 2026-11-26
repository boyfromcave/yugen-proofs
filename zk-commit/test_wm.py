"""Hiding opening W-M (full mask): exact zero-knowledge test and negative controls.

Construction (docs/zk-hiding-commitment.md section 7a). Oracle 0 holds, in the same leaves, the lanes
of the witness polynomial p (message slots [0, m), then t uniform coefficients at an aligned offset)
and the lanes of a uniform polynomial mk of the same lane length, on a coset domain. Prover sends
G = <mk, W>; verifier sends rho; the UNMODIFIED non-hiding opening is run on h = rho p + mk with
claim rho T + G; a level-0 query opens the rows of p and of mk.

View modelled: G, EVERY coefficient of h (an upper bound on what any non-hiding opening of h can
reveal: its round messages, later oracles, final message and later rows are functions of h and of
public challenges), and the opened level-0 rows of p and mk.

Tests: rank B = rank [A dirs | B] (the view's law does not depend on the witness) and rank B =
lanes * lrow + lanes * Q, the dimension of the set of views consistent with the public claim (the
simulator: h uniform, p's opened rows uniform, mk's rows and G determined). Full enumeration of all
randomness at toy size. Controls: linear domain with an opened row in U_top; one random coefficient
too few; a mask that misses one message slot; no mask.

Sources and provenance (REFERENCES.md). W-M is Adapted from Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields", ePrint 2025/1015, Construction 4.1 and Theorem 4.3 (pad, second uniform polynomial, unmodified opening on
alpha f + f'; the simulator tested here is that theorem's simulator). Changed: WHIR-style interleaved
opening instead of binary BaseFold, shared leaves, aligned pad offset.
"""
import random
import sys

from ff import GF, Vars, fadd, fscale, lincomb, zk_rank_test, enumerate_view, evalf
from additive import Chain

OUT = []


def say(s):
    print(s)
    OUT.append(s)


def build(F, kappa, m, Q, dim, rho, qpos, W, shift=True, t_deficit=0, mask_hole=False, no_mask=False):
    lanes, t = 1 << kappa, Q - t_deficit
    align = 1 << max(Q - 1, 0).bit_length()
    aoff = -(-m // align) * align
    lrow = aoff + t
    ch = Chain(F, [1 << k for k in range(dim + 1)])
    V = Vars()
    wit = V.new("w", lanes * m)
    P = [[{} for _ in range(lrow)] for _ in range(lanes)]
    for idx, f in enumerate(wit):
        P[idx % lanes][idx // lanes] = f
    for b in range(lanes):
        r = V.new("enc", t)
        for s in range(t):
            P[b][aoff + s] = r[s]
    M = [[{} for _ in range(lrow)] for _ in range(lanes)]
    if not no_mask:
        for b in range(lanes):
            mk = V.new("mask", lrow)
            for j in range(lrow):
                M[b][j] = mk[j]
        if mask_hole:
            M[0][0] = {}
    view = []
    g = {}
    for idx in range(lanes * m):
        g = fadd(g, fscale(F, W[idx], M[idx % lanes][idx // lanes]))
    view.append(g)                                                     # G
    for b in range(lanes):
        for j in range(lrow):
            view.append(fadd(fscale(F, rho, P[b][j]), M[b][j]))        # all of h
    for q in qpos:
        nr = ch.novel_row(ch.point(q, (1 << dim) if shift else 0), lrow)
        for b in range(lanes):
            view.append(lincomb(F, nr, P[b]))                          # row of p
            view.append(lincomb(F, nr, M[b]))                          # row of mk
    return view, V, lanes * lrow + lanes * len(set(qpos))


def dirs_for(F, V, W):
    widx = V.indices("w")
    p = next(k for k, w in enumerate(W) if w)
    return [{widx[k]: 1, widx[p]: F.mul(W[k], F.inv(W[p]))} for k in range(len(W)) if k != p]


def rank_case(F, name, rnd, trials, expect, **kw):
    good = 0
    dims = set()
    for _ in range(trials):
        kappa, m, Q, dim = kw["kappa"], kw["m"], kw["Q"], kw["dim"]
        W = [rnd.randrange(1, F.q) for _ in range((1 << kappa) * m)]
        qpos = sorted(rnd.sample(range(1 << dim), Q))
        if kw.get("low_row"):
            qpos[0] = 0
        rho = rnd.randrange(F.q) if not kw.get("rho_nonzero") else rnd.randrange(1, F.q)
        view, V, acc = build(F, kappa, m, Q, dim, rho, qpos, W, **{k: v for k, v in kw.items()
                                                                  if k in ("shift", "t_deficit", "mask_hole", "no_mask")})
        widx = set(V.indices("w"))
        ok, rb, rab = zk_rank_test(F, view, dirs_for(F, V, W), [i for i in range(V.n) if i not in widx])
        if expect:
            good += ok and rb == acc
            dims.add((rb, acc))
        else:
            good += not ok
    say(f"{'ok  ' if good == trials else 'FAIL'} {name}: {good}/{trials}" + (f"  (rank B, dim Acc) = {sorted(dims)}" if expect else "  leak in every tuple"))
    return good == trials


def enum_case(F, name, expect_equal, **kw):
    """Every randomness value, two witnesses with the same claim, every rho and position."""
    equal = total = 0
    W = [1, 3]
    for rho in range(F.q):
        for q in range(1 << kw["dim"]):
            view, V, _ = build(F, 1, 1, 1, kw["dim"], rho, [q], W, **{k: v for k, v in kw.items() if k != "dim"})
            widx = V.indices("w")
            ridx = [i for i in range(V.n) if i not in set(widx)]
            a1, a2 = [0] * V.n, [0] * V.n
            a1[widx[0]], a1[widx[1]] = 3, 0                              # <w, W> = 3 for both
            a2[widx[0]], a2[widx[1]] = 0, 1
            if rho == 0 and not expect_equal:
                continue
            total += 1
            equal += enumerate_view(F, view, a1, ridx) == enumerate_view(F, view, a2, ridx)
    okv = (equal == total) if expect_equal else (equal == 0)
    say(f"{'ok  ' if okv else 'FAIL'} {name}: distributions equal in {equal}/{total} (rho, position) cases")
    return okv


def main():
    rnd = random.Random(20261119)
    F = GF(8)
    res = []
    res.append(rank_case(F, "W-M, 2 lanes, 3 message slots, Q = 3, coset of 16, GF(256)", rnd, 120, True, kappa=1, m=3, Q=3, dim=4))
    res.append(rank_case(F, "W-M, 4 lanes, 4 message slots, Q = 4, coset of 16, GF(256)", rnd, 80, True, kappa=2, m=4, Q=4, dim=4))
    res.append(rank_case(F, "W-M, 4 lanes, 5 message slots, Q = 2, coset of 32, GF(256)", rnd, 60, True, kappa=2, m=5, Q=2, dim=5))
    res.append(rank_case(F, "control: linear domain, an opened row in U_top", rnd, 60, False, kappa=1, m=4, Q=3, dim=4, shift=False, low_row=True, rho_nonzero=True))
    res.append(rank_case(F, "control: one random coefficient too few", rnd, 60, False, kappa=1, m=3, Q=3, dim=4, t_deficit=1, rho_nonzero=True))
    res.append(rank_case(F, "control: mask misses one message slot", rnd, 60, False, kappa=1, m=3, Q=3, dim=4, mask_hole=True, rho_nonzero=True))
    res.append(rank_case(F, "control: no mask", rnd, 60, False, kappa=1, m=3, Q=3, dim=4, no_mask=True, rho_nonzero=True))
    F8 = GF(3)
    res.append(enum_case(F8, "enumeration GF(8): W-M, 2 lanes, 1 slot, Q = 1, coset of 4, all 8^6 tapes", True, dim=2))
    res.append(enum_case(F8, "enumeration GF(8) control: no mask, rho != 0", False, dim=2, no_mask=True))
    fails = res.count(False)
    say(f"FAILURES {fails}")
    with open("results/wm.txt", "w") as f:
        f.write("\n".join(OUT) + "\n")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
