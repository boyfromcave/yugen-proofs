"""Construction W-I (the hiding WHIR-style opening) and the tree composition target.

Round list and error terms: docs/zk-wi-soundness.md section 5 (unique decoding only; every term rests
on BCIKS20 Theorems 4.1 / 1.6, Schwartz-Zippel and unique decoding, all confirmed). Differences from
whir.rounds:

  mask_i    the verifier's rho_i after G_i                               1 / |F|
  fold_i.j  masked round; the aux rows may vary with the lane, so the
            enforced summand has degree 3 (total degree 3 for system A)   3 / |F| + n / |F|
  query_i   true rate (lrow_i [+ k_i for A]) / N_i                        ((1 + rate) / 2)^t + t / |F|
  bc        base-case challenge c (line Gcol + c fold, and the claim)    (N + 1) / |F|
  final     spot check of P* against Gcol + c fold                       ((1 + rate) / 2)^t

Layout per level (zk-hiding-commitment.md 6.1, with finding F-1 for system A): carried slots, for A
k guard slots, the aux slots (1 + 2k eq-fold, 1 + 4k affine combiner; times [F : K] at level 0),
t = queries uniform coefficients at an offset aligned to 2^ceil(log2 t).

Variant "full mask" (W-M, section 8 of the document): the unmodified opening run on rho p + m with a
second committed polynomial m over the challenge field; one extra round (N + 1) / |F|.

Tree target: a block's proof tree holds `proofs` proofs and a forger needs one false proof accepted.
"""

# Provenance (citation audit 2026-11-19): every W-I term below is from zk-wi-soundness.md (Theorem S,
# Lemmas 2 to 7), the Ycash developers' proof from BCIKS20 Theorems 4.1 and 1.6. The published
# round-by-round analysis of the related protocol (Chiesa, Fenzi, Weissenberg, ePrint 2026/391,
# Theorems 6.3, 7.1, 9.8, 10.2; list-decoding regime) is not used by this module.


from __future__ import annotations

import math
from dataclasses import dataclass

from . import whir
from .bounds import Regime, log2_sum
from .compose import FsParams, LayerResult, Round, evaluate
from .targets import SecurityTarget


@dataclass
class Level:
    lanes_log: int
    rows_log: int  # log2 N: domain points = Merkle leaves
    carried: int
    aux: int
    aoff: int
    t: int
    lrow: int
    degree: int  # coefficient count the proximity statement is about (lrow, + k for A's folded lane)

    @property
    def rate(self) -> float:
        return self.degree / 2.0**self.rows_log

    @property
    def n_last(self) -> int:
        """Bits of a folded-lane index, ceil(log2 lf): the tail sumcheck's rounds at the last level."""
        return max(0, (self.degree - 1).bit_length())


def layout(c: whir.WhirConfig, system: str) -> list[Level]:
    out: list[Level] = []
    carried = 2 ** (c.num_vars - c.folds[0])
    for i, k in enumerate(c.folds):
        rows_log = c.vars_at(i) + c.log_inv_rates[i] - k
        per_coeff = (c.ext_bytes // c.base_bytes) if i == 0 else 1
        nmask = (1 + 4 * k if system == "A" else 1 + 2 * k) * per_coeff
        guard = k if system == "A" else 0
        t = c.queries[i]
        # A: the offset is aligned to t + k so that multiplication by X keeps the random slots above it (F-7)
        align = 1 << max(t + guard - 1, 0).bit_length()
        aoff = -(-(carried + guard + nmask) // align) * align
        lrow = aoff + t
        degree = lrow + (k if system == "A" else 0)
        if degree > 2**rows_log:
            raise ValueError(f"{c.name}: level {i} lane length {degree} exceeds the domain")
        out.append(Level(k, rows_log, carried, nmask, aoff, t, lrow, degree))
        if i + 1 < len(c.folds):
            carried = -(-degree // 2 ** c.folds[i + 1])
    return out


@dataclass(frozen=True)
class AZk:
    """System A's zero-knowledge additions outside the opening, as counts of the wallet prover.

    The defaults are the counts of the code with every mask built, as the merge of the zero-knowledge
    branch counted them (revision 6, 2026-11-19: `yugen-proof-a-zk/docs/zero-knowledge.md` section 18.6 and
    `docs/zk-merge-notes.md` section 3, items 2 and 9: the bus trees have depth 21, so **11 bus layers, the
    first a one-level step**; the gadget's list holds **52 linear claims**: 22 bus, 2 table, 24 Keccak, 4
    openings), 12 Keccak layers (one a round), S9 as two masked chains (the output opening, 6 rounds; the
    input opening, 10 rounds and the slice blinder's dummy round of degree 1), column `A` of 2^11 elements.
    With row 6's schedule this is 87 rounds in the list (85 before). `A_WALLET_ZK_R5` keeps the revision-5
    defaults (10 bus layers, 54 claims; section 17.5's reading). The terms per instance are
    `zk-system-a-gaps.md` section 11 and `zk-wi-soundness.md` section 6. `A_WALLET_ZK_E` keeps the
    estimates used before the masks were built (revision 2 and the first revision 3 rows).
    """

    bus_layers: int = 11  # S1: radix-4 bus GKR at depth 21, the first layer a one-level step (zk-merge-notes.md 3, item 2)
    keccak_layers: int = 12  # S5 to S8: one layer a Keccak round at depth 12 (17.1)
    s9_sumchecks: int = 2  # S9: two masked chains, one rho each (17.1, 17.5)
    gadget_log_len: int = 11  # l: column A is 2^11 elements (1,944 at the wallet statement, 17.5)
    dummy_form: str = "A8-T"  # "A8-T" (A21: degree deg C) or "A8" (degree 2 deg C, the eq line counted: + 1)
    claims: int | None = 52  # m as counted at the merge (zk-merge-notes.md 3, item 9); None: one a masked sumcheck and one a Gtilde

    @property
    def masked_sumchecks(self) -> int:
        return 1 + self.s9_sumchecks + self.keccak_layers + self.bus_layers  # S4, S9, one per Keccak layer, one per bus layer

    @property
    def gtilde(self) -> int:
        return self.keccak_layers + self.bus_layers  # one Gtilde per GKR layer (A5, A23, A24)

    @property
    def gadget_claims(self) -> int:
        if self.claims is not None:
            return self.claims
        return self.masked_sumchecks + self.gtilde  # m: one linear claim per masked sumcheck and per Gtilde (gaps 11)


A_WALLET_ZK = AZk()
# Revision 5 defaults (yugen-proof-a-zk zero-knowledge.md 17.5), kept as the record: 10 bus layers, 54 claims.
A_WALLET_ZK_R5 = AZk(bus_layers=10, claims=54)
# The estimates before the fifth pass of yugen-proof-a-zk (upper readings of zero-knowledge.md 11.1).
A_WALLET_ZK_E = AZk(bus_layers=11, keccak_layers=2, s9_sumchecks=3, gadget_log_len=12, claims=None)


def zk_rounds(z: AZk, field_bits: float, grind: float = 0.0) -> list[Round]:
    """The rounds the zero-knowledge construction adds to a system-A proof outside the opening.

    Every entry is a new verifier message, so each is also one more round in k (book Theorem 31.2.1).
    None of them is in `OTHER_ROUNDS` (shipping.py), which counts the unmasked prover's rounds, and
    none is a round of the opening (the W-I opening's own rounds, `mask_i` included, are `rounds`).
    Terms in units of 1/q, q = 2^field_bits:
    """
    fb = field_bits
    t = lambda name, num: Round(name, math.log2(num) - fb, grind)
    s4_dummy, gkr_dummy = (2, 4) if z.dummy_form == "A8-T" else (5, 8)
    out = [
        # A4 on S4: the masked table sumcheck's rho (zk-wi-soundness.md Lemma 6: 1/q). Counted here once;
        # zk-system-a-gaps.md 3.5 says A21's mask term is "already counted for A4".
        t("S4.rho", 1),
        # A21 on S4: the dummy round, form A8-T (gaps 3.5, Proposition D: degree deg C = 2: 2/q); form A8:
        # degree 2 deg C = 4, 5 with the eq line the pinned grinding rule counts (gaps 3.2 item 2).
        t("S4.dummy", s4_dummy),
        # A20: the slice blinder's dummy round, degree 1: +1/q; the ring switch is unchanged (gaps 2.4).
        t("S9.dummy", 1),
    ]
    # A4 on S9: one rho per masked sumcheck of the Keccak openings (Lemma 6: 1/q each).
    out += [t(f"S9.rho{j}", 1) for j in range(z.s9_sumchecks)]
    for j in range(z.keccak_layers):
        # A23: the layer's mask rho (1/q; zk-wi-soundness.md 6.3: Gtilde bound by the gadget, only rho = 0 is bad)
        # and its dummy round of degree 2 (gaps 11: "1 + 2 per layer").
        out += [t(f"keccak{j}.rho", 1), t(f"keccak{j}.dummy", 2)]
    for j in range(z.bus_layers):
        # A24: per bus layer rho (1/q) and the dummy round, degree 4 in form A5-T, 8 in form A5 (gaps 11).
        out += [t(f"bus{j}.rho", 1), t(f"bus{j}.dummy", gkr_dummy)]
    # The linear-claim gadget (A7; zk-wi-soundness.md 6.3, gaps 11 "(m - 1) + 1 + l"): theta batches m
    # claims ((m - 1)/q), c (1/q, beta before c), z (l/q, u before z).
    out += [t("gadget.theta", max(1, z.gadget_claims - 1)), t("gadget.c", 1), t("gadget.z", z.gadget_log_len)]
    # A18, A19 (mask leaves of the count and shared roots) and A22 (linear hand-offs): no term (gaps 11).
    # A19 costs completeness at most 2^mu / q, not soundness. A25 is a test, A26 is the opening's tail (rounds).
    return out


def rounds(c: whir.WhirConfig, system: str, zk: AZk | None = None) -> list[Round]:
    """W-I's rounds (zk-wi-soundness.md Theorem S, section 5.1). For system A also the base case as
    built: the relation <P*, W'> = mu + c T proved by an unmasked degree-2 sumcheck of n_last rounds
    (zk-system-a-gaps.md 12.1 (a), checklist A26: 2 n_last / q, two per round). With `zk`, also the
    proof's zero-knowledge rounds outside the opening (`zk_rounds`, gaps section 11)."""
    assert c.regime is Regime.UDR, "W-I is analysed in the unique-decoding regime only"
    fb = c.field_bits
    out: list[Round] = []
    lv = layout(c, system)
    for i, k in enumerate(c.folds):
        # Lemmas 3, 3A: the level's mask challenge rho_i, 1/q
        out.append(Round(f"mask{i}", -fb, c.grind_fold))
        log_n = c.vars_at(i) + c.log_inv_rates[i]
        for j in range(k):
            # Lemmas 2 / 2A (far: n/q) and 3 / 3A (close: 3/q, total degree 3 for A); charged as (n + 3)/q
            out.append(Round(f"fold{i}.{j}", log2_sum([math.log2(3) - fb, log_n - j - fb]), c.grind_fold))
        # Lemma 4 / Lemma 5: queries at the TRUE rate lf_i / N_i (lrow_i + kappa_i for A)
        q = c.queries[i] * math.log2((1 + lv[i].rate) / 2)
        if i < len(c.folds) - 1:
            out.append(Round(f"query{i}", log2_sum([q, math.log2(c.queries[i]) - fb]), c.grind_query))
        else:
            # Lemma 5: the base-case challenge c, (N + 1)/q
            out.append(Round("bc", math.log2(2.0 ** lv[i].rows_log + 1) - fb, c.grind_fold))
            out.append(Round("final", q, c.grind_query))
            if system == "A":
                # A26 / gaps 12.1 (a): the tail sumcheck on the zero-padded P* and the weight, n_last = ceil(log2 lf)
                # rounds of degree 2. Replaces A12's direct check (no round); not the same event as bc.
                out += [Round(f"tail{j}", 1 - fb, c.grind_fold) for j in range(lv[i].n_last)]
    if zk is not None:
        out += zk_rounds(zk, fb, c.grind_fold)
    return out


def size_bytes(c: whir.WhirConfig, system: str) -> dict[str, float]:
    h = c.fs.digest_bits / 8
    lv = layout(c, system)
    total_q = other = 0.0
    for i, k in enumerate(c.folds):
        elem = c.base_bytes if i == 0 else c.ext_bytes
        t = c.queries[i]
        total_q += t * ((2**k) * elem + c.salt_bytes) + whir._paths(lv[i].rows_log, t, c.cap_height) * h
        other += h + c.ext_bytes + (4 if system == "A" else 3) * k * c.ext_bytes + 8 * 3
    final = (lv[-1].degree + 1 + c.queries[-1]) * c.ext_bytes  # P*, mu, Gcol at the opened rows
    return {"queries": total_q, "rounds": other, "final": final, "extra": c.extra_bytes,
            "total": total_q + other + final + c.extra_bytes}


def _solve(c: whir.WhirConfig, target, rounds_fn) -> whir.WhirConfig:
    for _ in range(200):
        rs = rounds_fn(c)
        need = target.need_bits(len(rs), c.fs)
        weak = [r for r in rs if r.effective_bits < need]
        bad = [r for r in weak if r.name.startswith("query") or r.name == "final"]
        if len(bad) < len(weak):
            r = next(r for r in weak if r not in bad)
            raise ValueError(f"{c.name}: round {r.name} gives {r.effective_bits:.1f} < {need:.1f} bits")
        if not bad:
            return c
        for r in bad:
            i = len(c.folds) - 1 if r.name == "final" else int(r.name[5:])
            c.queries[i] += max(1, int((need - r.effective_bits) / 1.0))
            if c.queries[i] > 2 ** (c.vars_at(i) + c.log_inv_rates[i]):
                # more queries than domain points: the lane's true rate has reached 1, no count works
                raise ValueError(f"{c.name}: round {r.name} cannot reach {need:.1f} bits at any query count")
    raise ValueError(f"{c.name}: no fixed point")


def solve(c: whir.WhirConfig, system: str, target, zk: AZk | None = None) -> whir.WhirConfig:
    """Smallest query counts for which every W-I round meets the target at the true rates (the lane
    length depends on the query count, so this is a fixed point); then trimmed to be minimal."""
    c.queries = [1] * len(c.folds)
    fn = lambda cc: rounds(cc, system, zk)
    _solve(c, target, fn)
    for i in range(len(c.folds)):  # trim overshoot
        while c.queries[i] > 1:
            c.queries[i] -= 1
            rs = fn(c)
            if min(r.effective_bits for r in rs) < target.need_bits(len(rs), c.fs):
                c.queries[i] += 1
                break
    return c


# --- variant W-M: the unmodified opening on rho p + m ---------------------------------------------


def full_mask_rounds(c: whir.WhirConfig) -> list[Round]:
    rs = whir.rounds(c)
    n0 = c.num_vars + c.log_inv_rates[0] - c.folds[0]
    # level 0 opens p's rows too: its t random coefficients per lane raise the level-0 rate
    t = c.queries[0]
    lane = 2 ** (c.num_vars - c.folds[0])
    align = 1 << max(t - 1, 0).bit_length()
    rate0 = (-(-lane // align) * align + t) / 2.0**n0
    q0 = t * math.log2((1 + rate0) / 2)
    name0 = "query0" if len(c.folds) > 1 else "final"
    rs = [Round(r.name, log2_sum([q0, math.log2(t) - c.field_bits]) if r.name == "query0" else (q0 if r.name == name0 else r.error_log2),
                r.grind_bits) for r in rs]
    return [Round("mask", math.log2(2.0**n0 + 1) - c.field_bits, c.grind_fold)] + rs


def full_mask_size(c: whir.WhirConfig) -> dict[str, float]:
    s = whir.size_bytes(c)
    add = c.queries[0] * (2 ** c.folds[0]) * c.ext_bytes + c.ext_bytes  # m's row beside p's row in each opened leaf; G
    return {**s, "mask_rows": add, "total": s["total"] + add}


def full_mask_solve(c: whir.WhirConfig, target) -> whir.WhirConfig:
    c.queries = [1] * len(c.folds)
    _solve(c, target, full_mask_rounds)
    for i in range(len(c.folds)):
        while c.queries[i] > 1:
            c.queries[i] -= 1
            rs = full_mask_rounds(c)
            if min(r.effective_bits for r in rs) < target.need_bits(len(rs), c.fs):
                c.queries[i] += 1
                break
    return c


# --- tree composition ------------------------------------------------------------------------------


@dataclass(frozen=True)
class TreeTarget(SecurityTarget):
    """The target for a whole proof tree: `proofs` proofs (leaves, bundles, merges), any one forged
    proof breaks the tree; `attempts` independent trees the adversary may try in the union model.

    model "union":  every proof is given the whole query budget t and the errors are added:
        eps_tree(t) <= proofs * attempts * eps_proof(t). Per round, with k rounds per proof:
          C  e >= classical_chain + log2(proofs * attempts) + 1 + log2(1 + k)
          Q  e >= 2 * quantum_chain + 1 + log2 6 + log2(proofs * attempts)     (CMS19 summed over proofs)
    model "shared": one budget of t oracle queries for everything the adversary does, all trees it
        tries included (a failed attempt is only queries); the book's (t + k) eps_rbr with k summed
        over the proofs it finally outputs, and CMS19 with a factor `proofs` for guessing which
        proof is the false one:
          C  e >= classical_chain + 1 + log2(1 + proofs * k)
          Q  e >= 2 * quantum_chain + 1 + log2 6 + log2(proofs)
    G (attack estimate) is unchanged in both: a multi-target Grover search over `proofs` statements
    is the same search over one bad set of the oracle's output.
    """

    proofs: int = 1700
    attempts: float = 1.0
    model: str = "union"

    def _cq(self, rounds_count: int, fs: FsParams) -> tuple[float, float]:
        if self.model == "union":
            m = math.log2(self.proofs * self.attempts)
            return (self.classical_chain + m + 1.0 + math.log2(1 + rounds_count * fs.instances),
                    2.0 * self.quantum_chain + 1.0 + fs.qrom_c1_log2 + m)
        return (self.classical_chain + 1.0 + math.log2(1 + self.proofs * rounds_count * fs.instances),
                2.0 * self.quantum_chain + 1.0 + fs.qrom_c1_log2 + math.log2(self.proofs))

    def need_bits(self, rounds_count: int, fs: FsParams) -> float:
        c, q = self._cq(rounds_count, fs)
        return max(c, q, self.attack_bits)

    def binding(self, rounds_count: int, fs: FsParams) -> str:
        c, q = self._cq(rounds_count, fs)
        return "classical (C)" if c >= max(q, self.attack_bits) else ("quantum (Q)" if q >= self.attack_bits else "attack (G)")

    def assess(self, res: LayerResult, fs: FsParams, rule: str = "attack") -> dict[str, bool]:
        e_min = min(r.effective_bits for r in res.rounds)
        c, q = self._cq(len(res.rounds), fs)
        return {"C": e_min >= c - 1e-9, "Q": e_min >= q - 1e-9 and res.quantum_hash_cap >= self.quantum_chain,
                "G": e_min >= self.attack_bits, "H": self.digest_ok(fs.digest_bits, rule)}


def tree_target(base: SecurityTarget, proofs: int = 1700, attempts: float = 1.0, model: str = "union") -> TreeTarget:
    return TreeTarget(name=f"{base.name}-tree", nist_category=base.nist_category, classical_chain=base.classical_chain,
                      quantum_chain=base.quantum_chain, attack_bits=base.attack_bits, digest_attack=base.digest_attack,
                      digest_proven=base.digest_proven, layers=base.layers, proofs=proofs, attempts=attempts, model=model)


def tree_bits_lost(proofs: int, attempts: float, rounds_count: int, model: str) -> float:
    """Classical bits a tree loses against one proof with `rounds_count` rounds."""
    if model == "union":
        return math.log2(proofs * attempts)
    return math.log2(1 + proofs * rounds_count) - math.log2(1 + rounds_count)


def evaluate_wi(c: whir.WhirConfig, system: str) -> LayerResult:
    return evaluate(c.name + " W-I", rounds(c, system), c.fs)
