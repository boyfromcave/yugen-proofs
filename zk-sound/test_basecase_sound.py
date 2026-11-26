"""Base case of W-I (padded final message checked against the extra column): exact game values.

Game (docs/zk-wi-soundness.md, Lemma 5), with no fold so that every committed word can be enumerated:
    prover commits two words on D: f (the lane) and g (the extra column Gcol);     public: W, T
    prover sends mu;  verifier sends c;  prover sends P* (k coefficients);
    verifier checks <P*, W> = mu + c T, draws Q positions y and checks P*(y) = g(y) + c f(y).
Code: Reed-Solomon, k = 2 coefficients in the novel basis, on the coset D = 4 + {0,1,2,3} of GF(8)
(n = 4, unique-decoding radius e = 1 position). Q = 2 positions, uniform and independent.

Every pair (f, g) is enumerated up to translation by codewords (which the prover can absorb into
mu and P*, so it does not change the game): 8^4 syndrome pairs. For each pair and each claim T that
is false (pair jointly within the radius: T differs from <decoded f, W>) or for every T (pair not
jointly within the radius), the exact value of the game is computed: the best mu, and for each c the
best P*, over ALL of them.

Proven bounds checked:
    jointly close:      1/q + (1 - 1/q) ((k - 1 + j)/n)^Q        j = number of rows where (f, g) is off its decoding
    not jointly close:  n/q + (1 - (e + 1)/n)^Q
Controls (the order of messages): positions known before P*; Gcol chosen after c.
"""
import itertools

from common import GF, Chain, Report

R = Report("basecase_sound")
F = GF(3)
q, n, k, Q, e = F.q, 4, 2, 2, 1
CH = Chain(F, [1, 2])
D = [CH.point(j, 4) for j in range(n)]
ROWS = [CH.novel_row(y, k) for y in D]                                  # evaluation functionals
W = (1, 3)
POLYS = list(itertools.product(range(q), repeat=k))
WORD = {p: tuple(F.dot(ROWS[y], p) for y in range(n)) for p in POLYS}
LIN = {p: F.dot(W, p) for p in POLYS}
WORD_INV = {w: p for p, w in WORD.items()}


def decode_on(word, A):
    """The polynomial through word on the first two positions of A, if it matches word on all of A."""
    for p in POLYS:
        if all(WORD[p][y] == word[y] for y in A):
            return p
    return None


def joint(f, g):
    """(j, u, v): the fewest rows where (f, g) differs from a pair of codewords, and that pair."""
    for size in (4, 3):
        for A in itertools.combinations(range(n), size):
            u, v = decode_on(f, A), decode_on(g, A)
            if u is not None and v is not None:
                return n - size, u, v
    return 2, None, None


def game_value(f, g, T):
    """max over mu of (1/q) sum_c max over P* with <P*, W> = mu + c T of (good/n)^Q; returned times q n^Q."""
    best = [[0] * q for _ in range(q)]                                  # best[c][target] = max good count
    for c in range(q):
        w = [g[y] ^ F.mul(c, f[y]) for y in range(n)]
        row = best[c]
        for p in POLYS:
            good = sum(1 for y in range(n) if WORD[p][y] == w[y])
            if good > row[LIN[p]]:
                row[LIN[p]] = good
    return max(sum(best[c][mu ^ F.mul(c, T)] ** Q for c in range(q)) for mu in range(q))


def main():
    reps = [(0, 0, a, b) for a in range(q) for b in range(q)]            # syndrome representatives
    worst = {"close": (0.0, None), "far": (0.0, None)}
    by_j = {}
    count = 0
    for f in reps:
        for g in reps:
            j, u, v = joint(f, g)
            if j <= e:
                S = LIN[u]
                Ts = [T for T in range(q) if T != S]
                kind = "close"
            else:
                Ts, kind = list(range(q)), "far"
            for T in Ts:
                val = game_value(f, g, T) / (q * n**Q)
                count += 1
                by_j[j] = max(by_j.get(j, 0.0), val)
                if val > worst[kind][0]:
                    worst[kind] = (val, (f, g, T))
    R.say(f"GF(8), n = 4, k = 2, Q = 2: {len(reps) ** 2} committed pairs, {count} (pair, false claim) games, each solved exactly")
    for j in sorted(by_j):
        R.say(f"  joint distance {j}: largest game value {by_j[j]:.4f}")
    b_close = {j: 1 / q + (1 - 1 / q) * ((k - 1 + j) / n) ** Q for j in (0, 1)}
    b_far = n / q + (1 - (e + 1) / n) ** Q
    R.check(by_j[0] <= b_close[0] + 1e-12, f"codeword pairs: optimum {by_j[0]:.4f} <= 1/q + (1-1/q)((k-1)/n)^Q = {b_close[0]:.4f}")
    R.check(by_j[1] <= b_close[1] + 1e-12, f"pairs with one corrupted row: optimum {by_j[1]:.4f} <= 1/q + (1-1/q)(k/n)^Q = {b_close[1]:.4f}")
    R.check(by_j[2] <= b_far + 1e-12, f"pairs outside the radius: optimum {by_j[2]:.4f} <= n/q + (1-(e+1)/n)^Q = {b_far:.4f}")
    doc = 1 / q + n / q + ((1 + k / n) / 2) ** Q
    R.check(max(by_j.values()) <= doc, f"all pairs: optimum {max(by_j.values()):.4f} <= document bound (n+1)/q + ((1+rho)/2)^Q = {doc:.4f}")
    R.say(f"  worst close pair (f, g, T) = {worst['close'][1]}, worst far pair = {worst['far'][1]}")

    # control 1: one position known before P* (Q = 1): is there always an accepted P*?
    acc = tot = 0
    for f in reps[::5]:
        for g in reps[::7]:
            j, u, v = joint(f, g)
            T = (LIN[u] ^ 1) if u is not None else 0
            for c in range(q):
                for y in range(n):
                    tot += 1
                    target = g[y] ^ F.mul(c, f[y])
                    acc += any(WORD[p][y] == target and LIN[p] == F.mul(c, T) for p in POLYS)   # mu = 0
    R.check(acc == tot, f"control: position drawn before P* (Q = 1): accepted in {acc}/{tot} cases (must be all: the order matters)")
    # control 2: Gcol chosen after c: g := P* - c f for any P* with the linear check
    acc = tot = 0
    for f in reps[::5]:
        for c in range(q):
            tot += 1
            p = next(p for p in POLYS if LIN[p] == F.mul(c, 1))          # T = 1, mu = 0
            g = [WORD[p][y] ^ F.mul(c, f[y]) for y in range(n)]
            acc += all(WORD[p][y] == g[y] ^ F.mul(c, f[y]) for y in range(n))
    R.check(acc == tot, f"control: Gcol chosen after c: accepted in {acc}/{tot} cases (must be all: the order matters)")
    R.close()


if __name__ == "__main__":
    main()
