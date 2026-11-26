"""Blinder cells with a dummy variable: does the revealed value still bind c(r)? Exact game values.

Statement (docs/zk-wi-soundness.md, Lemma 7). Column c with two rows, blinder cell b, both committed
before any challenge (ideal commitment: the final opening is exact). Constraint C(c) = c, i.e. the
claim "c is the zero column". Zerocheck with the dummy variable y:

    sum_{y, x in {0,1}} eq(tau_y, y) eq(tau, x) chat(y, x) = 0,     chat(y, x) = c(x) + y (1 + y) b.

Round y: message of degree <= 3; round x: degree <= 2; the prover reveals v = chat(r_y, r), which the
opening forces to equal c(r) + r_y (1 + r_y) b; final check s_2(r) = eq(tau_y, r_y) eq(tau, r) v.

Computed, for every nonzero column c and every b (GF(4): every tau; GF(8): six tau pairs): the exact
value of the game over ALL message strategies. Checked: (1) the value never exceeds the bound for
the plain zerocheck of the same degrees; (2) for every column and tau its maximum over b equals its value at b = 0 (the
blinder gives a cheating prover nothing, whether or not r_y falls in {0, 1}, where it vanishes).
Control: a blinder that is not committed (chosen after the challenges) is accepted whenever
r_y (1 + r_y) != 0.
"""
import itertools

from common import GF, Report, poly_eval

R = Report("blinder_sound")


def pack(vals):
    x = 0
    for i, v in enumerate(vals):
        x |= v << (4 * i)
    return x


def run(F, taus):
    q = F.q
    mask1 = pack([1] * q)

    def zeros(x):
        z = (x | (x >> 1) | (x >> 2) | (x >> 3)) & mask1
        return q - z.bit_count()

    msg2 = {c: [] for c in range(q)}                                    # degree <= 2, grouped by s(0)+s(1)
    for co in itertools.product(range(q), repeat=3):
        vals = [poly_eval(F, co, x) for x in range(q)]
        msg2[vals[0] ^ vals[1]].append(pack(vals))
    msg1 = []                                                           # degree <= 3 with s(0) + s(1) = 0
    for co in itertools.product(range(q), repeat=4):
        vals = [poly_eval(F, co, x) for x in range(q)]
        if vals[0] == vals[1]:
            msg1.append(vals)
    msg1 = [list(v) for v in {tuple(v) for v in msg1}]

    eq = lambda t, x: 1 ^ t ^ x
    worst_nondeg = spread = 0.0
    games = 0
    for c0, c1 in itertools.product(range(q), repeat=2):
        if (c0, c1) == (0, 0):
            continue
        for ty, t in taus:
            true_sum = F.mul(1 ^ t, c0) ^ F.mul(t, c1)                  # = c(tau): the claim is false iff nonzero
            vals = []
            for b in range(q):
                best2 = []
                for ry in range(q):
                    Z = F.mul(ry, 1 ^ ry)
                    phi = [F.mul(F.mul(eq(ty, ry), eq(t, r)), F.mul(1 ^ r, c0) ^ F.mul(r, c1) ^ F.mul(Z, b)) for r in range(q)]
                    pp = pack(phi)
                    best2.append([max(zeros(pp ^ s) for s in msg2[cl]) for cl in range(q)])
                vals.append(max(sum(best2[ry][s1[ry]] for ry in range(q)) for s1 in msg1) / (q * q))
                games += 1
            spread = max(spread, max(vals) - vals[0])
            if true_sum:
                worst_nondeg = max(worst_nondeg, max(vals))
            else:
                assert min(vals) == 1.0                                 # tau hit a root of c: the claim is true
    return worst_nondeg, spread, games


def control_late_blinder(F):
    """The prover claims the zero column although c != 0, sends the all-zero messages, reveals v = 0
    and then picks b := c(r) / (r_y (1 + r_y)). Accepted iff that is possible."""
    q = F.q
    acc = tot = 0
    for c0, c1 in ((1, 0), (2, 3), (1, 1)):
        for ry in range(q):
            for r in range(q):
                tot += 1
                Z = F.mul(ry, 1 ^ ry)
                cr = F.mul(1 ^ r, c0) ^ F.mul(r, c1)
                acc += (Z != 0) or (cr == 0)
    return acc / tot


def main():
    for k, taus in ((2, None), (3, [(2, 3), (5, 1), (7, 7), (0, 4), (6, 2), (3, 0)])):
        F = GF(k)
        q = F.q
        full = taus is None
        if full:
            taus = list(itertools.product(range(q), repeat=2))
        worst, spread, games = run(F, taus)
        bound = 1 - (1 - 3 / q) * (1 - 2 / q)
        R.say(f"GF({q}), {'every' if full else 'six'} tau, every nonzero column and every b ({games} games solved exactly): "
              f"largest value with c(tau) != 0: {worst:.4f}; largest gain of any b over b = 0: {spread:+.4f}")
        R.check(spread <= 1e-12, f"GF({q}): for every column and tau, no committed blinder value beats b = 0")
        R.check(worst <= bound + 1e-12, f"GF({q}): value {worst:.4f} <= 1 - (1 - 3/q)(1 - 2/q) = {bound:.4f} (the two rounds' bound without a blinder)")
    c = control_late_blinder(GF(3))
    R.say(f"control: blinder chosen after the challenges: accepted with probability {c:.4f} for a false column")
    R.check(c >= 1 - 2 / 8, "control: an uncommitted blinder breaks soundness (accepted whenever r_y (1 + r_y) != 0)")
    R.close()


if __name__ == "__main__":
    main()
