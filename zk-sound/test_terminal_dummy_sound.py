"""The one-sided dummy variable (form A8-T): does the revealed value still bind c(r)? Exact game values.

Statement (docs/zk-system-a-gaps.md, Proposition D). Column c with two rows and a blinder cell b,
both committed before any challenge (ideal commitment: the final opening is exact). Claim: "c is
the zero column", as system A's table sumcheck states it, a plain sum with the eq line inside:

    sum_x eq(tau, x) chat(x, 0) = 0,      chat(x, y) = c(x) + y b      (multiplier y, lam_y(p) = p(0)).

Round x: message s1 of degree <= 2 with s1(0) + s1(1) = 0; challenge r.
Round y (last): message s2 of degree <= 1 with s2(0) = s1(r); challenge r_y.
The prover reveals v, which the opening forces to equal c(r) + r_y b; final check
s2(r_y) = eq(tau, r) v.

Computed for every nonzero column, every b and every tau: the exact value of the game over ALL
message strategies. Checked: (1) for every column and tau the value does not depend on b; (2) the
largest value with c(tau) != 0 equals 1 - (1 - 2/q)(1 - 1/q), the bound of the two rounds.
Controls: a blinder chosen after the challenges; the dummy round checked with the plain functional
s2(0) + s2(1) = s1(r) (then a false claim is accepted with probability 1).
"""
import itertools

from common import GF, Report, poly_eval

R = Report("terminal_dummy_sound")


def game(F, c0, c1, b, tau, plain_y=False):
    q = F.q
    col = lambda r: F.mul(1 ^ r, c0) ^ F.mul(r, c1)
    eq = lambda r: 1 ^ tau ^ r
    # best second-round success for each (r, claimed value a = s1(r))
    best2 = [[0] * q for _ in range(q)]
    lines = [(k0, k1) for k0 in range(q) for k1 in range(q)]
    for r in range(q):
        target = [F.mul(eq(r), col(r) ^ F.mul(ry, b)) for ry in range(q)]
        for k0, k1 in lines:
            vals = [k0 ^ F.mul(k1, ry) for ry in range(q)]
            head = (vals[0] ^ vals[1]) if plain_y else vals[0]
            hits = sum(v == t for v, t in zip(vals, target))
            best2[r][head] = max(best2[r][head], hits)
    best = 0
    for co in itertools.product(range(q), repeat=3):
        vals = [poly_eval(F, co, x) for x in range(q)]
        if vals[0] ^ vals[1]:
            continue
        best = max(best, sum(best2[r][vals[r]] for r in range(q)))
    return best / (q * q)


def main():
    for k in (2, 3):
        F = GF(k)
        q = F.q
        worst = spread = 0.0
        games = 0
        for c0, c1 in itertools.product(range(q), repeat=2):
            if (c0, c1) == (0, 0):
                continue
            for tau in range(q):
                vals = [game(F, c0, c1, b, tau) for b in range(q)]
                games += q
                spread = max(spread, max(vals) - min(vals))
                if F.mul(1 ^ tau, c0) ^ F.mul(tau, c1):
                    worst = max(worst, max(vals))
        bound = 1 - (1 - 2 / q) * (1 - 1 / q)
        R.say(f"GF({q}), every tau, every nonzero column and every b ({games} games solved exactly): largest value with "
              f"c(tau) != 0: {worst:.4f}; largest difference between two blinder values: {spread:.4f}")
        R.check(spread <= 1e-12, f"GF({q}): the game value does not depend on the committed blinder")
        R.check(abs(worst - bound) <= 1e-12, f"GF({q}): value {worst:.4f} = 1 - (1 - 2/q)(1 - 1/q) = {bound:.4f}")
    F = GF(3)
    v = max(game(F, 1, 0, 3, 5, plain_y=True), game(F, 2, 3, 0, 1, plain_y=True))
    R.say(f"control: dummy round checked as a plain sum: value {v:.4f} for a false column")
    R.check(v == 1.0, "control: the plain functional on the dummy round accepts a false claim always")
    # blinder chosen late: all-zero messages, v = 0, b := c(r) / r_y
    acc = tot = 0
    for c0, c1 in ((1, 0), (2, 3), (1, 1)):
        for ry in range(F.q):
            for r in range(F.q):
                tot += 1
                acc += (ry != 0) or ((F.mul(1 ^ r, c0) ^ F.mul(r, c1)) == 0)
    R.say(f"control: blinder chosen after the challenges: accepted with probability {acc / tot:.4f} for a false column")
    R.check(acc / tot >= 1 - 1 / 8, "control: an uncommitted blinder breaks soundness (accepted whenever r_y != 0)")
    R.close()


if __name__ == "__main__":
    main()
