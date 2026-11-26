"""Cheating provers against the W-I verifier of ../zk-commit/whir_i.py (docs/zk-wi-soundness.md, section 6).

Every strategy commits its oracles before the challenges that follow them (wi.transcript). For the
one-level instance the acceptance probability is EXACT: every (rho, gamma, c) is enumerated and the
position check is evaluated at every domain point, so the probability over Q independent positions
is (good/N)^Q. For the two-level instance complete challenge tuples are sampled.

Each strategy is compared with the bound the document proves for its case:
    oracles within the unique-decoding radius, j corrupted rows:
        1 - (1 - 1/q) (1 - d/q)^kappa ... (1 - 1/q) (1 - ((lrow - 1 + j)/N)^Q)       d = 2 or 3
    an oracle outside the radius: at most (1 - dist)^Q for the strategy's distance (the n/q term of
    the bound is vacuous at toy field sizes and is not used in a check).
"""
import itertools
import random

from common import GF, Report, solve
from wi import Prover, transcript, verify
from whir_i import Config

R = Report("wi_attacks")


def case_bound(cfg, d, extra_rows=0):
    q, keep = cfg.F.q, 1.0
    L = len(cfg.levels)
    for i, lv in enumerate(cfg.levels):
        N = 1 << lv.dim
        keep *= (1 - 1 / q) * (1 - d / q) ** lv.kappa
        agree = min(1.0, (lv.lrow - 1 + (extra_rows if i == 0 else 0)) / N) ** lv.Q
        if i < L - 1:
            keep *= (1 - agree) * (1 - (lv.Q + lv.ood) / q)
        else:
            keep *= (1 - 1 / q) * (1 - agree)
    return 1 - keep


def exact_one_level(cfg, W0, claim, make):
    F, lv = cfg.F, cfg.levels[0]
    q, N = F.q, 1 << lv.dim
    total, n = 0.0, 0
    for rho in range(q):
        for gam in itertools.product(range(q), repeat=lv.kappa):
            for bc in range(q):
                p = make()
                chal = [{"rho": rho, "gam": list(gam), "ood": [], "qpos": [], "lam": 1, "bc": bc}]
                pre = transcript(cfg, p, chal)
                good = 0
                for y in range(N):
                    good += verify(cfg, W0, claim, [dict(chal[0], qpos=[y])], pre + p.oracle[0][y] + [p.gcol[0][y]])
                total += (good / N) ** lv.Q
                n += 1
    return total / n


def sample_chal(cfg, rnd):
    F, out = cfg.F, []
    for lv in cfg.levels:
        out.append({"rho": rnd.randrange(F.q), "gam": [rnd.randrange(F.q) for _ in range(lv.kappa)], "ood": [],
                    "qpos": [rnd.randrange(1 << lv.dim) for _ in range(lv.Q)], "lam": rnd.randrange(F.q),
                    "bc": rnd.randrange(F.q)})
    return out


def sampled(cfg, W0, claim, make, samples, seed):
    rnd, acc = random.Random(seed), 0
    for _ in range(samples):
        chal = sample_chal(cfg, rnd)
        acc += verify(cfg, W0, claim, chal, transcript(cfg, make(), chal))
    return acc / samples


def sampled_one_level(cfg, W0, claim, make, samples=2500, seed=5):
    """As exact_one_level with (rho, gamma, c) sampled; positions still exact."""
    F, lv = cfg.F, cfg.levels[0]
    q, N = F.q, 1 << lv.dim
    rnd, total = random.Random(seed), 0.0
    for _ in range(samples):
        p = make()
        chal = [{"rho": rnd.randrange(q), "gam": [rnd.randrange(q) for _ in range(lv.kappa)], "ood": [], "qpos": [],
                 "lam": 1, "bc": rnd.randrange(q)}]
        pre = transcript(cfg, p, chal)
        good = sum(verify(cfg, W0, claim, [dict(chal[0], qpos=[y])], pre + p.oracle[0][y] + [p.gcol[0][y]]) for y in range(N))
        total += (good / N) ** lv.Q
    return total / samples


def one_level(k, dim, Q, exact):
    F = GF(k)
    cfg = Config(F, 1, [1], [Q], [0], [dim])
    lv = cfg.levels[0]
    N, q = 1 << lv.dim, F.q
    W0, wit = [3, 5], [7, 9]
    true = F.mul(3, 7) ^ F.mul(5, 9)
    false = true ^ 1
    run = exact_one_level if exact else sampled_one_level
    tol = 0.0 if exact else 0.02
    R.say(f"one level: GF({q}), fold 1, lane length {lv.lrow} (carried 1, aux 3, gap, {lv.t} random) on a coset of {N} points, Q = {Q}; "
          + ("every (rho, gamma, c) and every position enumerated" if exact else
             "2500 sampled (rho, gamma, c), every position enumerated; sampling tolerance 0.02"))
    mk = lambda **kw: (lambda: Prover(cfg, W0, wit, random.Random(7), **kw))
    v = run(cfg, W0, true, mk())
    R.check(abs(v - 1.0) < 1e-12, f"honest prover, true claim: accepted with probability {v:.4f}")
    b2, b3 = case_bound(cfg, 2), case_bound(cfg, 3)
    rows = [
        ("false claim, final-message swap only", mk(claim=false, swap_final=True), b2),
        ("+ G aimed at one rho", mk(claim=false, swap_final=True, target_rho={0: 5}), b2),
        ("+ round message with chosen roots", mk(claim=false, swap_final=True, target_rho={0: 5}, cheat_rounds=True), b2),
        ("+ mu aimed at one c (all gambles)", mk(claim=false, swap_final=True, target_rho={0: 5}, cheat_rounds=True, target_c=3), b2),
        ("all gambles, rho aimed at 0", mk(claim=false, swap_final=True, target_rho={0: 0}, cheat_rounds=True, target_c=0), b2),
        ("all gambles + lane-varying aux rows (cubic round polynomial)",
         mk(claim=false, swap_final=True, target_rho={0: 5}, cheat_rounds=True, target_c=3,
            aux_tables={0: [[1, 2, 3], [4, 6, 9]]}), b3),
    ]
    for label, make, bound in rows:
        v = run(cfg, W0, false, make)
        R.check(v <= bound + 1e-12 + tol, f"{label}: accepted {v:.5f} <= case bound {bound:.5f}")

    # corruption inside the radius: the oracle decodes to P (claim false), the prover plays P'' = P + Z
    e = (N - lv.lrow) // 2
    ch = cfg.chains[0]
    roots = list(range(lv.lrow - 1))
    z0 = solve(F, [ch.novel_row(cfg.point(0, y), lv.lrow) for y in roots] + [[1] + [0] * (lv.lrow - 1)], [0] * (lv.lrow - 1) + [1])
    E = set(range(lv.lrow - 1, lv.lrow - 1 + e))
    zword = [F.dot(ch.novel_row(cfg.point(0, y), lv.lrow), z0) for y in range(N)]

    def corrupt(level, words, gcol):
        for y in range(N):
            if y not in E:
                words[y] = [w ^ zword[y] for w in words[y]]            # everywhere else the oracle is P, not P''
    claim2 = true ^ F.mul(z0[0], 3 ^ 5)
    v = run(cfg, W0, claim2, lambda: Prover(cfg, W0, wit, random.Random(7), delta0=z0, corrupt=corrupt))
    hit = lambda a: 1 - (1 - 1 / q) * (1 - a ** lv.Q)                  # c = 0 erases the fold from the spot check
    pred = hit((lv.lrow - 1 + e) / N)
    R.say(f"radius attack: {e} corrupted rows (the unique-decoding radius), decoded claim false, prover plays the other polynomial: "
          f"accepted {v:.5f}; predicted 1 - (1 - 1/q)(1 - ((lrow-1+e)/N)^Q) = {pred:.5f}; "
          f"document's terms 1/q + ((1+rho)/2)^Q = {1 / q + ((1 + lv.lrow / N) / 2) ** lv.Q:.5f}")
    R.check(abs(v - pred) < 1e-12 + tol and v <= 1 / q + ((1 + lv.lrow / N) / 2) ** lv.Q + tol,
            "radius attack meets its prediction and stays under 1/q + ((1+rho)/2)^Q")

    # outside the radius: half of the rows from one polynomial, half from another
    half = set(range(N // 2))

    def splice(level, words, gcol):
        for y in range(N):
            if y not in half:
                words[y] = [w ^ zword[y] ^ 1 for w in words[y]]
    v = run(cfg, W0, claim2, lambda: Prover(cfg, W0, wit, random.Random(7), delta0=z0, corrupt=splice))
    good = len(half) + sum(1 for y in range(N) if y not in half and zword[y] == 1)
    pred = hit(good / N)
    R.say(f"spliced oracle outside the radius ({good} of {N} rows agree with the polynomial the prover plays): accepted {v:.5f}; "
          f"predicted {pred:.5f}; proven for a word this far: n/q + (1 - dist)^Q with (1 - dist)^Q = {(good / N) ** lv.Q:.5f}")
    R.check(abs(v - pred) < 1e-12 + tol, "spliced oracle: accepted exactly on the agreeing rows, or when c = 0 (inside the n/q term)")

    # Gcol not a codeword: the prover corrupts Gcol on rows where it will need help
    def badg(level, words, gcol):
        for y in range(N // 2):
            gcol[y] ^= 1
    v = run(cfg, W0, false, lambda: Prover(cfg, W0, wit, random.Random(7), claim=false, swap_final=True,
                                                         target_c=3, corrupt=badg))
    R.check(v <= b2 + 1e-12 + tol, f"non-codeword extra column with the gambles: accepted {v:.5f} <= {b2:.5f}")


def two_level():
    F = GF(6)
    cfg = Config(F, 2, [1, 1], [2, 2], [0, 0], [4, 4])
    W0, wit = [3, 5, 2, 7], [7, 9, 4, 1]
    true = 0
    for w, x in zip(W0, wit):
        true ^= F.mul(w, x)
    false = true ^ 1
    l0, l1 = cfg.levels
    R.say(f"two levels: GF(64), folds 1/1, lane lengths {l0.lrow}/{l1.lrow} on cosets of {1 << l0.dim}/{1 << l1.dim} points, Q = 2/2; "
          f"4000 sampled challenge tuples per strategy")
    mk = lambda **kw: (lambda: Prover(cfg, W0, wit, random.Random(11), **kw))
    v = sampled(cfg, W0, true, mk(), 600, 1)
    R.check(v == 1.0, f"honest prover, true claim: accepted {v:.4f} (600 tuples, rho, gamma, lam, c over the whole field)")
    n = 4000
    for d, label, make in [
        (2, "false claim, switch polynomial at the code switch + final swap",
         mk(claim=false, switch={0: True}, swap_final=True)),
        (2, "all gambles (rho at both levels, roots, switch, c, swap)",
         mk(claim=false, switch={0: True}, swap_final=True, target_rho={0: 5, 1: 9}, cheat_rounds=True, target_c=3)),
        (3, "all gambles + lane-varying aux rows at both levels",
         mk(claim=false, switch={0: True}, swap_final=True, target_rho={0: 5, 1: 9}, cheat_rounds=True, target_c=3,
            aux_tables={0: [[1, 2, 3], [4, 6, 9]], 1: [[5, 1, 8], [2, 2, 7]]})),
    ]:
        v = sampled(cfg, W0, false, make, n, 3)
        bound = case_bound(cfg, d)
        tol = 4 * (bound * (1 - bound) / n) ** 0.5
        R.check(v <= bound + tol, f"{label}: accepted {v:.4f} <= case bound {bound:.4f} (+ {tol:.4f} sampling)")


if __name__ == "__main__":
    one_level(4, 3, 2, True)
    one_level(6, 5, 3, False)
    two_level()
    R.close()
