"""Numbers of docs/qrom-compilation.md, docs/zk-quantum.md and docs/whir-additive-soundness.md.

Python standard library only; `python3 test_numbers.py` from this directory; exits non-zero on failure.

1. Finding W-1 (whir-additive-soundness.md section 6): query bits of system A's plain rows 7 and 9 at
   the true rate (2^mu + kappa) / 2^(mu + r) against the nominal 2^-r. The needs are the calculator's
   (soundness/, shipping.tree_target(CAT1, proofs=20_000), OTHER_ROUNDS = 512), copied here as
   constants from a read-only run on 2026-11-19; the schedule is verifier/src/whir.rs derive_config_for
   as soundness/src/yugen_soundness/current.py row_schedule transcribes it.
2. QROM bits of a tree of 20,000 proofs at lambda = 256: the record of revision 1 (qrom-compilation.md
   6.1, the constants C1 = 6, C2 = 24 of Chiesa, Manohar, Spooner, ePrint 2019/834, Section 8.5.1, and the
   form-X / form-C constants, with the corrected folded row 24 / 192), and the spBCS figures of revision 2
   (section 5) from Sharp, Grubbs, ePrint 2026/2615, Theorem 6.6 (2) with Definition I.1, recomputed
   independently of soundness/; finding Q-5.
3. Merkle hiding against unbounded distinguishers (zk-quantum.md section 3): the per-leaf bound of
   Chiesa-Yogev, "Building Cryptographic Proofs from Hash Functions", Claim 3.4.2,
   2^(-(s - sigma)/2) + sqrt(n) 2^(-s/2), summed over the unopened leaves.
4. An exact check, at toy sizes, of the two-sided bound of the same book's Claim 3.4.1:
   E_f Delta(f(x, U_s), U_sigma) is at most (1/2) 2^(-(s - sigma)/2) and is a constant when s = sigma.
   The expectation depends only on the multinomial counts of 2^s salts into 2^sigma outputs and is
   computed exactly over all count vectors.
"""

import math
import sys
from fractions import Fraction

FAILURES = []


def check(cond, msg):
    if not cond:
        FAILURES.append(msg)
        print("FAIL", msg)


# ---------------------------------------------------------------- 1. W-1
TREE_LIST = [0, 369, 226, 185, 168, 161, 157, 155, 154, 154, 154]  # params.rs CAT1_TREE_UD_QUERIES
NEED = {22: 152.343, 24: 152.365, 25: 152.365, 26: 152.365, 27: 152.375, 28: 152.375}


def derive(log_n, r0, f0, f, red0, red, resid):
    folds, rates, rem = [f0], [r0], log_n - f0
    while rem > resid:
        rates.append(rates[-1] + folds[-1] - (red0 if len(folds) == 1 else red))
        k = min(f, rem)
        rem -= k
        folds.append(k)
    return folds, rates


def query_bits(q, rho):
    return -q * math.log2((1 + rho) / 2)


def row_bits(log_n, r0, shape):
    folds, rates = derive(log_n, r0, *shape)
    out, m = [], log_n
    for k, r in zip(folds, rates):
        m -= k
        q = TREE_LIST[max(1, min(r, len(TREE_LIST) - 1))]
        out.append((m, k, r, q, query_bits(q, 2.0 ** -r), query_bits(q, (2 ** m + k) / 2 ** (m + r))))
    return out


ROW7 = (6, 3, 3, 3, 7)
ROW9 = (6, 3, 3, 3, 5)
print("W-1: weakest query round, true rate, margin")
results = {}
for name, shape, pairs in (("row 7", ROW7, [(22, 2), (22, 1)]),
                           ("row 9", ROW9, [(n, r) for n in (24, 25, 26, 27, 28) for r in (1, 2)])):
    for log_n, r0 in pairs:
        levels = row_bits(log_n, r0, shape)
        worst = min(l[5] for l in levels)
        nominal = min(l[4] for l in levels)
        margin = worst - NEED[log_n]
        results[(name, log_n, r0)] = margin
        print(f"  {name} 2^{log_n} rate 1/{2 ** r0}: nominal {nominal:.2f} true {worst:.2f} margin {margin:+.2f}")
        check(nominal >= NEED[log_n], f"{name} nominal list should meet the need at 2^{log_n}, 1/{2**r0}")
check(results[("row 7", 22, 1)] > 0.6 and results[("row 7", 22, 2)] > 0.85, "row 7 keeps its margin at true rates")
check(abs(results[("row 9", 24, 1)] + 4.35) < 0.01, "row 9, 2^24, rate 1/2 fails by 4.35 bits")
check(min(results[k] for k in results if k[0] == "row 9") < -4.3, "row 9 fails somewhere by more than 4.3 bits")


def needed(mu, k, r, need):
    return math.ceil(need / -math.log2((1 + (2 ** mu + k) / 2 ** (mu + r)) / 2))


fix = {(mu, r): needed(mu, 3, r, 152.375) for mu in (3, 4, 5, 6) for r in (4, 5)}
print("  last-level counts at the true rate (kappa = 3):", fix)
check(fix[(3, 4)] == 173 and fix[(3, 5)] == 163 and fix[(4, 4)] == 170 and fix[(5, 4)] == 169, "fix counts")
for (mu, r), q in fix.items():  # each count less by one fails
    check(query_bits(q - 1, (2 ** mu + 3) / 2 ** (mu + r)) < 152.375 <= query_bits(q, (2 ** mu + 3) / 2 ** (mu + r)),
          f"minimal count at mu={mu}, r={r}")

# ---------------------------------------------------------------- 2. QROM bits of the tree
LAM, N, E = 256, 20_000, 152.343


def qrom_bits(c1, c2, e=E, lam=LAM, n=N):
    iop = (e - 1 - math.log2(c1) - math.log2(n)) / 2
    hsh = (lam - 1 - math.log2(c2) - math.log2(n)) / 3
    return iop, hsh


print("QROM bits, tree of 20,000 proofs, lambda = 256, e = need of the rows")
# Revision 2 of qrom-compilation.md: the folded row was wrong (12, 96); (2t)^2, (2t)^3 give 24, 192 (referee 1.8).
for label, c1, c2 in (("CMS19 constants", 6, 24), ("form X (record)", 6, 24),
                      ("form C as stated (unproved)", 24, 240), ("form X, t' = t + a, a <= t, folded in", 24, 192),
                      ("form C, a <= t folded in (t' <= 3t)", 54, 810)):
    iop, hsh = qrom_bits(c1, c2)
    print(f"  {label:38s} C1={c1:3d} C2={c2:3d}: IOP {iop:.2f}, hash {hsh:.2f}, min {min(iop, hsh):.2f}")
    check(min(iop, hsh) >= 64, f"{label} meets 64 QROM bits")
iop, hsh = qrom_bits(6, 24)
check(abs(iop - 67.24) < 0.01 and abs(hsh - 78.71) < 0.01, "CMS19 constants: 67.24 / 78.71")
iop, hsh = qrom_bits(24, 192)
check(abs(iop - 66.24) < 0.01 and abs(hsh - 77.71) < 0.01, "folded row corrected: 66.24 / 77.71")
iop, hsh = qrom_bits(54, 810)
check(abs(iop - 65.65) < 0.01 and abs(hsh - 77.02) < 0.01, "form C folded: 65.65 / 77.02")

# spBCS (Sharp-Grubbs, ePrint 2026/2615, Theorem 6.6 (2), Definition I.1), recomputed independently of
# soundness/ from the message counts of qrom-compilation.md section 4, solving N 6 (t + k_q)^2 2^-e = 1/2 and
# N 6 c' (t + k_q)^3 / 2^256 = 1/2 for log2 t by bisection.


def spbcs_bits(e, n_v, m, q_iop, log_lmax, factor=1, n=N, lam=LAM):
    n_msg = 2 * n_v
    c_prime = max(2, n_msg * max(1, m)) + 1
    k_q = 2 * n_msg + q_iop * (2 + log_lmax)

    def solve(f):
        lo, hi = 0.0, 200.0
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) <= -1 else (lo, mid)
        return lo
    T = lambda k: math.log2(factor * 2.0 ** k + k_q)
    iop = solve(lambda k: math.log2(n) + math.log2(6) + 2 * T(k) - e)
    hsh = solve(lambda k: math.log2(n) + math.log2(6 * c_prime) + 3 * T(k) - lam)
    return c_prime, k_q, iop, hsh


print("spBCS, Theorem 6.6 (2), tree of 20,000 proofs")
for label, args, want in (("A, SHAKE256", (152.96, 599, 2, 1552, 26), (2397, 45852, 67.54, 75.63)),
                          ("B, SHAKE256", (152.73, 600, 2, 1104, 31), (2401, 38832, 67.43, 75.63)),
                          ("B, counter mode (Lemma X)", (152.73, 600, 2, 1104, 31, 2), (2401, 38832, 66.43, 74.63))):
    cp, kq, iop, hsh = spbcs_bits(*args)
    print(f"  {label:28s} c' = {cp}, k_q = {kq}, IOP {iop:.2f}, hash {hsh:.2f}")
    check((cp, kq) == want[:2] and abs(iop - want[2]) < 0.006 and abs(hsh - want[3]) < 0.006, f"spBCS {label}")
# finding Q-5: condition C under the ROM part, every t >= 1 (binding at t = 1) and t >= k_q
check(abs(129 + math.log2(N) + math.log2(1 + 45852) - 158.77) < 0.006, "Q-5, A: 158.77")
check(abs(130 + math.log2(N) - 144.29) < 0.006, "Q-5, t >= k_q: 144.29")

# ---------------------------------------------------------------- 3. salts
SIGMA, N_U, N_BITS = 256, 2 ** 24, 2 ** 12
print("Merkle hiding against unbounded distinguishers, all unopened leaves of one proof (N_u = 2^24)")
table = {}
for s in (256, 384, 512, 576, 640):
    per_leaf = 2.0 ** (-(s - SIGMA) / 2) + math.sqrt(N_BITS) * 2.0 ** (-s / 2)
    total = min(1.0, N_U * per_leaf)
    table[s] = math.log2(total)
    print(f"  s = {s}: per leaf 2^{math.log2(per_leaf):.1f}, proof 2^{table[s]:.1f}")
check(table[256] == 0.0, "256-bit salts: vacuous")
check(abs(table[384] + 40) < 0.01 and abs(table[512] + 104) < 0.01 and abs(table[576] + 136) < 0.01, "salt table")
# BCS16 Lemma 3.4 at lambda = 256 (salt 2 lambda = 512): n 2^(-lambda/4 + 2)
check(abs(math.log2(N_U * 2.0 ** (-256 / 4 + 2)) + 38) < 1e-9, "BCS16 Lemma 3.4 at n = 2^24: 2^-38")


# ---------------------------------------------------------------- 4. Claim 3.4.1 exactly at toy size
def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def expected_tv(s, sigma):
    """E over a random function {0,1}^s -> {0,1}^sigma of TV(image of uniform salt, uniform)."""
    n, m = 2 ** s, 2 ** sigma
    total = Fraction(0)
    fact = [math.factorial(i) for i in range(n + 1)]
    for z in compositions(n, m):
        prob = Fraction(fact[n], math.prod(fact[c] for c in z)) / Fraction(m ** n)
        tv = sum(abs(Fraction(c, n) - Fraction(1, m)) for c in z) / 2
        total += prob * tv
    return total


print("Claim 3.4.1, exact, sigma = 1 and 2")
for sigma in (1, 2):
    for s in range(sigma, sigma + 5):
        if 2 ** s > 64:
            continue
        v = expected_tv(s, sigma)
        upper = 0.5 * 2.0 ** (-(s - sigma) / 2)
        print(f"  sigma={sigma} s={s}: E TV = {float(v):.5f}, upper bound {upper:.5f}")
        check(float(v) <= upper + 1e-12, f"upper bound at sigma={sigma}, s={s}")
        if s == sigma:
            check(float(v) >= 0.2, f"s = sigma gives constant distance (sigma={sigma})")

print("FAILURES", len(FAILURES))
sys.exit(1 if FAILURES else 0)
