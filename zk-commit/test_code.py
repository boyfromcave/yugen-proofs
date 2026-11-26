"""Lemma E: the zero-knowledge encoding over an additive domain, exact condition.

Interleaved code: `lanes` polynomials, each with coefficients (novel basis)
    slots [0, m)            message
    slots [aoff, aoff + t)  uniform randomness          (aoff >= m, zeros in between)
evaluated on  D = shift + span(b_0..b_{dim-1}).  A leaf is one row: all lanes at one point.

Checked:
  1. rank criterion for EVERY set Q of at most t rows: coset domain -> independent of the message;
     linear domain (shift 0) -> independent exactly when Q avoids U_top = zeros of X_aoff;
     every set of t + 1 rows leaks.
  2. full enumeration of the randomness (small field): the distribution of the opened rows of two
     messages is identical exactly when the rank criterion says so for their difference (this
     also validates the rank criterion against brute force); in every structurally hiding case
     (at most t rows, none in U_top) it is identical.
  3. the alignment condition on aoff (observation).

Sources and provenance (REFERENCES.md). Sufficiency for a pad at offset 2^l on a domain disjoint from
the message subspace is Published: Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields", ePrint 2025/1015, Lemma 4.4.
Necessity, other aligned offsets and interleaved lanes (Lemma E in full) are Original (the Ycash
developers, 2026) as far as checked. The published alternative, randomness on the LOWEST coefficients,
hides on any domain: Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint
2026/391 (revision of 2026-11-16), Lemma 3.29; it is not what this file tests.
"""
import itertools
import sys

from ff import GF, Vars, lincomb, zk_rank_test, enumerate_view, tv_distance
from additive import Chain


def build(F, dim, lanes, m, aoff, t, shift_on):
    ch = Chain(F, [1 << i for i in range(dim + 1)])
    V = Vars()
    msg = [V.new("w", m) for _ in range(lanes)]
    rnd = [V.new("z", t) for _ in range(lanes)]
    shift = (1 << dim) if shift_on else 0
    rows = []
    for j in range(1 << dim):
        x = ch.point(j, shift)
        nr = ch.novel_row(x, aoff + t)
        rows.append([lincomb(F, nr[:m] + nr[aoff:aoff + t], msg[b] + rnd[b]) for b in range(lanes)])
    return ch, V, rows


def top_zero_set(aoff):
    """Row indices j (linear domain) with X_aoff = 0: U_top, top = highest set bit of aoff."""
    return set(range(1 << (aoff.bit_length() - 1)))


def rank_part(out):
    fails = 0
    for (k, dim, lanes, m, aoff, t) in [(4, 3, 1, 2, 2, 2), (4, 3, 2, 4, 4, 3), (8, 4, 2, 4, 4, 3),
                                        (8, 4, 4, 5, 8, 3), (8, 4, 1, 6, 8, 4), (8, 5, 2, 7, 8, 2)]:
        F = GF(k)
        for shift_on in (True, False):
            ch, V, rows = build(F, dim, lanes, m, aoff, t, shift_on)
            dirs = [{i: 1} for i in V.indices("w")]
            zidx = V.indices("z")
            n = 1 << dim
            bad_expected = bad_seen = good = 0
            U = top_zero_set(aoff)
            for size in range(1, t + 1):
                for Q in itertools.combinations(range(n), size):
                    view = [f for j in Q for f in rows[j]]
                    ok, _, _ = zk_rank_test(F, view, dirs, zidx)
                    expect = True if shift_on else not (set(Q) & U)
                    if ok != expect:
                        fails += 1
                    good += ok
                    bad_seen += (not ok)
                    bad_expected += (not expect)
            over = 0
            sets = list(itertools.combinations(range(n), t + 1))
            for Q in sets[:400]:
                view = [f for j in Q for f in rows[j]]
                ok, _, _ = zk_rank_test(F, view, dirs, zidx)
                over += (not ok)
            if over != min(len(sets), 400):
                fails += 1
            out(f"GF(2^{k}) |D|={n} lanes={lanes} m={m} aoff={aoff} t={t} "
                f"{'coset ' if shift_on else 'linear'}: sets<=t hiding {good}, leaking {bad_seen} "
                f"(predicted {bad_expected}); sets of t+1 leaking {over}/{min(len(sets), 400)}")
    return fails


def enum_part(out):
    fails = 0
    F = GF(3)
    for (dim, lanes, m, aoff, t) in [(2, 1, 2, 2, 1), (2, 2, 2, 2, 1), (2, 1, 2, 2, 2)]:
        for shift_on in (True, False):
            ch, V, rows = build(F, dim, lanes, m, aoff, t, shift_on)
            widx, zidx = V.indices("w"), V.indices("z")
            w1 = {i: (3 * i + 1) % F.q for i in widx}
            w2 = {i: (5 * i + 2) % F.q for i in widx}
            U = top_zero_set(aoff)
            same = diff = wrong = 0
            for size in range(1, t + 2):
                for Q in itertools.combinations(range(1 << dim), size):
                    view = [f for j in Q for f in rows[j]]
                    d = tv_distance(enumerate_view(F, view, w1, zidx), enumerate_view(F, view, w2, zidx))
                    # prediction for THIS pair of messages: the rank criterion on their difference
                    dvec = {i: w1[i] ^ w2[i] for i in widx}
                    expect_same, _, _ = zk_rank_test(F, view, [dvec], zidx)
                    structural = size <= t and (shift_on or not (set(Q) & U))
                    assert expect_same or not structural      # structural hiding implies equality
                    same += d == 0
                    diff += d > 0
                    wrong += (d == 0) != expect_same
            fails += wrong
            out(f"enumeration GF(8) |D|={1 << dim} lanes={lanes} m={m} t={t} "
                f"{'coset ' if shift_on else 'linear'}: identical {same}, different {diff}, "
                f"against prediction {wrong}")
    return fails


def alignment_part(out):
    """Randomness at an offset that is not a multiple of 2^ceil(log2 t): is some set of t rows bad?"""
    F = GF(8)
    for (dim, m, aoff, t) in [(4, 3, 3, 2), (4, 5, 5, 3), (4, 6, 6, 4), (4, 4, 4, 4), (4, 6, 8, 4)]:
        ch, V, rows = build(F, dim, 1, m, aoff, t, True)
        dirs = [{i: 1} for i in V.indices("w")]
        zidx = V.indices("z")
        bad = tot = 0
        for Q in itertools.combinations(range(1 << dim), t):
            ok, _, _ = zk_rank_test(F, [rows[j][0] for j in Q], dirs, zidx)
            bad += not ok
            tot += 1
        al = aoff % (1 << (t - 1).bit_length()) == 0
        out(f"alignment GF(2^8) coset |D|=16 m={m} aoff={aoff} t={t} "
            f"({'aligned' if al else 'not aligned'}): leaking sets of t rows {bad}/{tot}")
    return 0


if __name__ == "__main__":
    lines = []
    out = lambda s: (print(s), lines.append(s))
    f = rank_part(out) + enum_part(out) + alignment_part(out)
    out(f"FAILURES {f}")
    open("results/code.txt", "w").write("\n".join(lines) + "\n")
    sys.exit(1 if f else 0)
