"""Two parallel copies of a small-field protocol under Fiat-Shamir do not square the error
(docs/binius-extension-challenges.md section 7, alternative (a)).

Toy: the sumcheck of a multilinear f over n = 3 variables for a false sum. Each round message
carries a free nonce (the role a commitment's salt or any free transcript bits play), so a
prover can resample a round's challenge: the state-restoration game Fiat-Shamir gives.

  protocol P2: two copies over F = GF(16), one hash per round giving both challenges; both must pass.
  protocol PK: one copy over K = GF(256) = F-squared in size.

Interactive soundness error per round: P2 (1/16)^2 = 1/256 (both copies lucky in the same round),
PK 1/256. Under Fiat-Shamir the copies of P2 can be healed in different rounds: about 2 x 16
hash calls against 256.

Sources and provenance (REFERENCES.md). Consistent with Ben-Sasson, Chiesa, Spooner, "Interactive Oracle Proofs", ePrint 2016/116, Theorem 1.5 (state-restoration soundness at most binom(b, k+1) * s) and Remark 1.6 (repetition
reaches small state-restoration error only with many copies). The staggered attack is published:
Block, Garreta, Katz, Thaler, Tiwari, Zajac, "Fiat-Shamir Security of FRI and Related SNARKs",
ePrint 2023/1071, Appendix C (t = 2 parallel repetition: regenerate round-1 challenges until copy 1
cheats, then round-2 challenges until copy 2 does), attributed there to Attema, Fehr, Klooss,
"Fiat-Shamir Transformation of Multi-Round Interactive Proofs", TCC 2022 (not read). The run here
is a toy reproduction by this project, not an original attack.
"""

import hashlib
import unittest

from gf import F16, F256_over_4, mul

N_VARS = 3


def h(field, count, *parts):
    """`count` challenges of `field` from the transcript."""
    d = hashlib.sha256(repr(parts).encode()).digest()
    if len(field.elems) == 16:
        return [field.elems[d[i] & 15] for i in range(count)]
    return [d[i] for i in range(count)]


def partial_sum(f, rs, x0):
    """sum over the remaining Boolean variables of f(rs..., x0, ...), f multilinear by its table."""
    n = N_VARS
    acc = 0
    k = len(rs)
    for tail in range(2 ** (n - k - 1)):
        point = list(rs) + [x0] + [(tail >> j) & 1 for j in range(n - k - 1)]
        acc ^= evaluate(f, point)
    return acc


def evaluate(f, point):
    acc = 0
    for idx, coeff in enumerate(f):  # f in the monomial basis: coefficient of prod_{j in idx} x_j
        term = coeff
        for j in range(N_VARS):
            if (idx >> j) & 1:
                term = mul(term, point[j])
        acc ^= term
    return acc


def line(g0, g1, r):
    return g0 ^ mul(r, g0 ^ g1)


def verify(field, copies, f, claims, proof):
    """proof: per round (nonce, [(g0, g1) per copy]). Returns True iff every copy passes."""
    claims = list(claims)
    rs = [[] for _ in range(copies)]
    transcript = ("stmt", tuple(f), tuple(claims))
    for nonce, msgs in proof:
        for c in range(copies):
            if msgs[c][0] ^ msgs[c][1] != claims[c]:
                return False
        transcript = (transcript, nonce, tuple(msgs))
        ch = h(field, copies, transcript)
        for c in range(copies):
            claims[c] = line(*msgs[c], ch[c])
            rs[c].append(ch[c])
    return all(evaluate(f, rs[c]) == claims[c] for c in range(copies))


def forge(field, copies, f, false_claim):
    """Staggered attack: in each round, heal the first copy that is still false by resampling the nonce."""
    claims = [false_claim] * copies
    rs = [[] for _ in range(copies)]
    healed = [False] * copies
    transcript = ("stmt", tuple(f), tuple(claims))
    proof, calls = [], 0
    for rnd in range(N_VARS):
        true = [(partial_sum(f, rs[c], 0), partial_sum(f, rs[c], 1)) for c in range(copies)]
        msgs = []
        for c in range(copies):
            if healed[c]:
                msgs.append(true[c])
            else:
                g0 = true[c][0]  # keep g(0), shift g(1) to meet the false claim: one root
                msgs.append((g0, claims[c] ^ g0))
        target = next((c for c in range(copies) if not healed[c]), None)
        nonce = 0
        while True:
            t2 = (transcript, nonce, tuple(msgs))
            ch = h(field, copies, t2)
            calls += 1
            if target is None or line(*msgs[target], ch[target]) == line(*true[target], ch[target]):
                break
            nonce += 1
            if nonce > 100_000:
                return None, calls
        if target is not None:
            healed[target] = True
        transcript = t2
        proof.append((nonce, msgs))
        for c in range(copies):
            claims[c] = line(*msgs[c], ch[c])
            rs[c].append(ch[c])
    return (proof if all(healed) else None), calls


class StaggeredAttack(unittest.TestCase):
    def run_many(self, field, copies, trials=200):
        total = 0
        for t in range(trials):
            f = h(field, 8, "poly", t)
            true_sum = partial_sum(f, [], 0) ^ partial_sum(f, [], 1)
            false = true_sum ^ field.elems[1]
            proof, calls = forge(field, copies, f, false)
            self.assertIsNotNone(proof)
            self.assertTrue(verify(field, copies, f, [false] * copies, proof))  # a false sum, accepted
            total += calls
        return total / trials

    def test_two_copies_over_GF16_cost_about_two_times_16_not_256(self):
        mean = self.run_many(F16, 2)
        self.assertLess(mean, 64)
        self.mean = mean

    def test_one_copy_over_GF256_costs_about_256(self):
        mean = self.run_many(F256_over_4, 1)
        self.assertGreater(mean, 150)
        self.assertLess(mean, 400)

    def test_honest_proofs_verify(self):
        for field, copies in ((F16, 2), (F256_over_4, 1)):
            f = h(field, 8, "poly", 0)
            s = partial_sum(f, [], 0) ^ partial_sum(f, [], 1)
            proof, _ = forge(field, copies, f, s)  # a true claim: every copy is healed at once
            # with a true claim the "shifted" message is the true one; the loop exits at nonce 0
            self.assertTrue(verify(field, copies, f, [s] * copies, proof))


if __name__ == "__main__":
    unittest.main()
