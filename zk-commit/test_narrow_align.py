"""Finding F-7 by shape: where the narrow alignment (offset a multiple of 2^ceil(log2 t)) breaks completeness.

docs/zk-system-a-gaps.md, section 12.2. The verifier never sees where the uniform coefficients sit, so a
narrow layout is not something it can refuse; it is a layout in which the HONEST relation fails at
some shapes.

Multiplication by X in the novel polynomial basis (the prover's `pcs/src/xmul.rs`: (X h)[c] pulls from
h[c - 1] and, for odd c, from h[c], for even c with t trailing zeros, from h[c + 2^t - 1]) sends the
coefficient at slot s to slot s + 1 and to the slots s + 1 - 2^j for j = 0 .. r - 1, r being the number
of trailing one bits of s. The lowest is s + 1 - 2^(r - 1). (Corrected 2026-11-19: the earlier rule of this
file sent it to s with every trailing one bit cleared, s + 1 - 2^r, one step too low; it mispredicted 6 of
the 17 shapes the real prover was run at. The rule below is checked against this model's own
multiplication by X, which it equals exactly.)

The honest relation fails when the random content, during the level's kappa fold rounds, reaches a slot
below the end of the aux slots (a slot the relation weighs). Checks:
1. the rule is the support of this model's multiplication by X (every slot of a level);
2. the eight model shapes: the prediction against this model's verifier, 12 honest runs each;
3. the 17 shapes of the real prover (yugen-proof-a-zk, tests/zk_wi.rs,
   narrow_alignment_is_refused_where_predicted, run 2026-11-19 at a6079e2 + the levels' print): the levels
   (kappa, end of the aux slots, t) and whether the verifier refused the narrow prover's honest proof; the
   prediction must be the outcome at all 17. The old rule's mispredictions are counted and asserted to be 6.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ff import GF, evalf                                      # noqa: E402
from whir_a import LevelA, config, prove, verify             # noqa: E402
from test_whir_a import sample                                # noqa: E402


def trailing_ones(c):
    return (~c & (c + 1)).bit_length() - 1


def feeds(c):
    """The slots multiplication by X sends the coefficient at slot c to (the prover's xmul.rs)."""
    return {c + 1} | {c + 1 - (1 << j) for j in range(trailing_ones(c))}


def feeds_old(c):
    """The rule this file used before the correction: c + 1 and c with its trailing one bits cleared."""
    return {c + 1, c & (c + 1)}


def reaches_below(start, t, kappa, floor, rule=feeds):
    """Does the content of slots start .. start + t - 1 reach a slot below `floor` within kappa multiplications?"""
    reach = set(range(start, start + t))
    for _ in range(kappa):
        reach |= {s for c in reach for s in rule(c)}
    return min(reach) < floor


def model_fails(lv, rule=feeds):
    return reaches_below(lv.aoff, lv.t, lv.kappa, lv.aux0 + lv.nmask, rule)


# (folds, queries, levels as (kappa, end of the aux slots, t), refused by the real verifier)
REAL = [
    ((2, 1, 7), 7, [(2, 32806, 7), (1, 16419, 7), (1, 8222, 7), (1, 4122, 7), (1, 2074, 7), (1, 1050, 7), (1, 538, 7), (1, 282, 7), (1, 154, 7)], False),
    ((2, 1, 7), 8, [(2, 32806, 8), (1, 16419, 8), (1, 8227, 8), (1, 4131, 8), (1, 2083, 8), (1, 1059, 8), (1, 547, 8), (1, 291, 8), (1, 163, 8)], False),
    ((2, 1, 7), 3, [(2, 32806, 3), (1, 16413, 3), (1, 8216, 3), (1, 4116, 3), (1, 2066, 3), (1, 1042, 3), (1, 530, 3), (1, 274, 3), (1, 146, 3)], False),
    ((2, 1, 7), 5, [(2, 32806, 5), (1, 16414, 5), (1, 8217, 5), (1, 4121, 5), (1, 2073, 5), (1, 1049, 5), (1, 537, 5), (1, 281, 5), (1, 153, 5)], False),
    ((2, 1, 7), 2, [(2, 32806, 2), (1, 16412, 2), (1, 8214, 2), (1, 4116, 2), (1, 2066, 2), (1, 1042, 2), (1, 530, 2), (1, 274, 2), (1, 146, 2)], True),
    ((2, 2, 7), 3, [(2, 32806, 3), (2, 8215, 3), (2, 2067, 3), (2, 531, 3), (2, 147, 3)], False),
    ((2, 2, 7), 7, [(2, 32806, 7), (2, 8218, 7), (2, 2070, 7), (2, 534, 7), (2, 150, 7)], True),
    ((3, 2, 5), 4, [(3, 16439, 4), (2, 4123, 4), (2, 1045, 4), (2, 275, 4), (2, 83, 4), (2, 35, 4)], True),
    ((3, 2, 5), 6, [(3, 16439, 6), (2, 4126, 6), (2, 1045, 6), (2, 275, 6), (2, 83, 6), (2, 35, 6)], True),
    ((3, 2, 5), 7, [(3, 16439, 7), (2, 4126, 7), (2, 1046, 7), (2, 278, 7), (2, 86, 7), (2, 38, 7)], True),
    ((3, 3, 7), 6, [(3, 16439, 6), (3, 2074, 6), (3, 278, 6), (3, 54, 6)], True),
    ((4, 2, 7), 5, [(4, 8264, 5), (2, 2082, 5), (2, 535, 5), (2, 147, 5)], False),
    ((4, 2, 7), 13, [(4, 8264, 13), (2, 2088, 13), (2, 539, 13), (2, 151, 13)], False),
    ((4, 4, 7), 13, [(4, 8264, 13), (4, 541, 13), (4, 57, 13)], False),
    ((5, 3, 10), 6, [(5, 4185, 6), (3, 542, 6)], False),
    ((5, 3, 10), 28, [(5, 4185, 28), (3, 549, 28)], True),
    ((5, 3, 10), 30, [(5, 4185, 30), (3, 549, 30)], True),
]


def real_fails(levels, rule=feeds):
    """The real prover's narrow offset: the aux end rounded up to a multiple of t's next power of two."""
    def narrow(aux_end, t):
        a = 1 << (t - 1).bit_length()
        return -(-aux_end // a) * a
    return any(reaches_below(narrow(end, t), t, kappa, end, rule) for kappa, end, t in levels)


def main():
    rnd = random.Random(20261124)
    F = GF(8)
    lines = []
    say = lambda s: (print(s, flush=True), lines.append(s))
    fails = 0

    # 1. The rule is the model's multiplication by X.
    lv = LevelA(F, 1, 0, 60, 7)
    support = [{j for j, m in enumerate(lv.cols[c]) if m} for c in range(lv.Lf - 1)]
    wrong = [c for c in range(lv.Lf - 1) if support[c] != feeds(c)]
    wrong_old = [c for c in range(lv.Lf - 1) if support[c] != feeds_old(c)]
    ok = not wrong
    fails += not ok
    say(f"{'ok  ' if ok else 'FAIL'} the rule is the support of multiplication by X at all {lv.Lf - 1} slots of a level "
        f"(slots where it differs: {len(wrong)}; the old rule differs at {len(wrong_old)})")

    # 2. The model's shapes against the model's verifier.
    shapes = [(1, [2, 1], [3, 2], [5, 5]), (1, [1], [2], [4]), (2, [1], [2], [4]), (1, [2], [2], [5]),
              (2, [1, 1], [2, 2], [4, 4]), (1, [2], [3], [5]), (3, [1], [3], [5]), (1, [1], [4], [5])]
    for wit, kappas, Qs, dims in shapes:
        try:
            narrow = config(F, wit, kappas, Qs, dims, narrow_align=True)
            wide = config(F, wit, kappas, Qs, dims)
        except AssertionError:
            continue
        predicted = any(model_fails(lv) for lv in narrow)
        rej = 0
        runs = 12
        for _ in range(runs):
            W0 = [rnd.randrange(1, F.q) for _ in range(wit << kappas[0])]
            chal = sample(F, narrow, rnd)
            view, V = prove(F, narrow, W0, chal)
            assign = [rnd.randrange(F.q) for _ in range(V.n)]
            claim = F.dot(W0, [assign[i] for i in V.indices("w")])
            rej += not verify(F, narrow, W0, claim, chal, [evalf(F, f, assign) for f in view])
        same = [a.aoff for a in narrow] == [b.aoff for b in wide]
        ok = (rej == 0) if not predicted else (rej >= runs - 2)
        fails += not ok
        say(f"{'ok  ' if ok else 'FAIL'} model: folds {kappas}, Q {Qs}, witness rows {wit}: offsets narrow {[a.aoff for a in narrow]} "
            f"wide {[b.aoff for b in wide]}{' (same layout)' if same else ''}; a coefficient reaches a weighed slot: "
            f"{predicted}; honest runs rejected {rej}/{runs}")

    # 3. The real prover's 17 shapes.
    old_wrong = 0
    for folds, queries, levels, refused in REAL:
        predicted = real_fails(levels)
        old = real_fails(levels, feeds_old)
        old_wrong += old != refused
        ok = predicted == refused
        fails += not ok
        say(f"{'ok  ' if ok else 'FAIL'} real prover: folds {folds}, {queries} queries: predicted {'refused' if predicted else 'accepted'}, "
            f"{'refused' if refused else 'accepted'}{'' if old == refused else ' (the old rule predicted ' + ('refused' if old else 'accepted') + ')'}")
    ok = old_wrong == 6
    fails += not ok
    say(f"{'ok  ' if ok else 'FAIL'} the old rule mispredicts {old_wrong} of {len(REAL)} real shapes (recorded: 6)")
    say(f"FAILURES {fails}")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "narrow_align.txt"), "w").write("\n".join(lines) + "\n")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
