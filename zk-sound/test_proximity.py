"""The code-level facts the W-I soundness proof uses, checked exactly at toy size
(docs/zk-wi-soundness.md, section 3).

A. Coset domain, any dimension: the Reed-Solomon code of degree < k on beta + S equals, word for
   word under y = beta + s, the code on S; the novel-basis functions X_0..X_{k-1} span it; minimum
   distance n - k + 1 (k = 3, 5, 6: not powers of two).
B. Correlated agreement on a line inside the unique-decoding radius (BCIKS20 Theorem 4.1), on a
   coset domain: every pair of words (up to codewords) over GF(8), n = 4, k = 2, e = 1. If more than
   n values of gamma put u0 + gamma u1 within e of the code, the pair is jointly within e.
   Lemma 2 (interleaved): the same for two lane pairs folded with one gamma, sampled.
C. The affine combiner G + (alpha + beta x) F with the degree raised by one, sampled: if more than
   n q pairs (alpha, beta) put the word within e of RS[k + 1], then F is within e of RS[k] and G of
   RS[k + 1] on a common set of rows.
"""
import itertools
import random

from common import GF, Chain, Report, poly_eval

R = Report("proximity")


def part_a():
    F = GF(4)
    ch = Chain(F, [1, 2, 4, 8])
    S = [ch.point(j) for j in range(8)]
    for k in (3, 5, 6):
        D = [8 ^ s for s in S]
        mono_coset, mono_lin, novel = set(), set(), set()
        minw = len(D)
        for co in itertools.product(range(F.q), repeat=k):
            w = tuple(poly_eval(F, co, y) for y in D)
            mono_coset.add(w)
            mono_lin.add(tuple(poly_eval(F, co, s) for s in S))
            if any(co):
                minw = min(minw, sum(1 for v in w if v))
        rows = [ch.novel_row(y, k) for y in D]
        for co in itertools.product(range(F.q), repeat=k):
            novel.add(tuple(F.dot(r, co) for r in rows))
        R.check(mono_coset == mono_lin == novel and minw == len(D) - k + 1,
                f"A: GF(16), n = 8, k = {k}: coset code = linear-domain code = novel-basis span ({len(novel)} words), minimum distance {minw}")


def part_b():
    F = GF(3)
    q, n, k, e = F.q, 4, 2, 1
    ch = Chain(F, [1, 2])
    rows = [ch.novel_row(ch.point(j, 4), k) for j in range(n)]
    code = [tuple(F.dot(r, p) for r in rows) for p in itertools.product(range(q), repeat=k)]
    dist = {}
    for w in itertools.product(range(q), repeat=n):
        dist[w] = min(sum(1 for a, b in zip(w, c) if a != b) for c in code)

    def joint(words):
        """Fewest rows where the words differ from codewords simultaneously."""
        best = n
        for size in (4, 3):
            for A in itertools.combinations(range(n), size):
                if all(any(all(w[y] == c[y] for y in A) for c in code) for w in words):
                    return n - size
        return 2
    reps = [(0, 0, a, b) for a in range(q) for b in range(q)]
    worst = bad = 0
    for u0 in reps:
        for u1 in reps:
            cnt = sum(1 for g in range(q) if dist[tuple(a ^ F.mul(g, b) for a, b in zip(u0, u1))] <= e)
            j = joint([u0, u1])
            if j > e:
                worst = max(worst, cnt)
            if cnt > n and (j > e or cnt != q):
                bad += 1
    R.check(bad == 0 and worst <= n, f"B: all {len(reps) ** 2} pairs: pairs not jointly within the radius have at most {worst} good gamma (theorem: at most n = {n})")
    rnd = random.Random(1)
    worst = bad = 0
    for trial in range(4000):
        if trial % 2:
            us = [tuple(rnd.randrange(q) for _ in range(n)) for _ in range(4)]
        else:                                                            # near-codewords: the hard cases
            us = []
            for _ in range(4):
                w = list(rnd.choice(code))
                w[rnd.randrange(n)] ^= rnd.randrange(q)
                us.append(tuple(w))
        cnt = 0
        for g in range(q):
            v0 = tuple(a ^ F.mul(g, b) for a, b in zip(us[0], us[1]))
            v1 = tuple(a ^ F.mul(g, b) for a, b in zip(us[2], us[3]))
            cnt += joint([v0, v1]) <= e
        j = joint(us)
        if j > e:
            worst = max(worst, cnt)
        if cnt > n and j > e:
            bad += 1
    R.check(bad == 0, f"B: Lemma 2, 4000 sampled lane quadruples: not jointly within the radius => at most {worst} good gamma (<= n = {n})")


def part_c():
    F = GF(3)
    q, n, k, e = F.q, 4, 1, 1
    ch = Chain(F, [1, 2])
    D = [ch.point(j, 4) for j in range(n)]
    code1 = [tuple(poly_eval(F, co, y) for y in D) for co in itertools.product(range(q), repeat=k)]
    code2 = [tuple(poly_eval(F, co, y) for y in D) for co in itertools.product(range(q), repeat=k + 1)]
    dist2 = {w: min(sum(1 for a, b in zip(w, c) if a != b) for c in code2) for w in itertools.product(range(q), repeat=n)}
    rnd = random.Random(2)
    worst = bad = 0
    for trial in range(1500):
        Fw = list(rnd.choice(code1)) if trial % 3 else [rnd.randrange(q) for _ in range(n)]
        Gw = list(rnd.choice(code2)) if trial % 2 else [rnd.randrange(q) for _ in range(n)]
        for w in (Fw, Gw):
            if rnd.random() < 0.7:
                w[rnd.randrange(n)] ^= rnd.randrange(q)
        cnt = 0
        for a in range(q):
            for b in range(q):
                cnt += dist2[tuple(g ^ F.mul(a ^ F.mul(b, y), f) for g, f, y in zip(Gw, Fw, D))] <= e
        ok = False
        for A in itertools.combinations(range(n), n - e):
            if any(all(Fw[y] == c[y] for y in A) for c in code1) and any(all(Gw[y] == c[y] for y in A) for c in code2):
                ok = True
        if not ok:
            worst = max(worst, cnt)
        if cnt > n * q and not ok:
            bad += 1
    R.check(bad == 0, f"C: 1500 sampled (F, G): not jointly within the radius => at most {worst} good (alpha, beta) (<= n q = {n * q})")


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    R.close()
