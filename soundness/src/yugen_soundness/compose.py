"""From per-round errors to bits of security: classical (BCS) and quantum (CMS19), and chains."""

# Sources of the formulas in this module (REFERENCES.md Part 2):
#   classical: Chiesa-Yogev book Theorems 25.2.1 and 31.2.1 (read); original form Ben-Sasson, Chiesa,
#     Spooner, ePrint 2016/116, Theorem 7.1 (read 2026-11-19);
#   quantum: Chiesa, Manohar, Spooner, "Succinct Arguments in the Quantum Random Oracle Model", ePrint
#     2019/834 (copy dated January 14, 2020; read 2026-11-19), Theorem 8.6 (Section 8.4) and its proof,
#     Section 8.5.1: the database game is bounded by 6 (t'^2 eps + 4 t'^3 / 2^lambda) (Lemma 5.13, the
#     lifting lemma, with Lemmas 8.13 and 6.11), and Lemma 4.9 adds sqrt(a / 2^lambda) to the square root,
#     t' = t + a, a = O(q log l) oracle calls of the verifier's expansion. C1 = 6 and C2 = 24 are read off
#     that proof (CITATION-AUDIT C-6); the theorem is for CMS19's own BCS variant (Section 8.2; C-7);
#   the tree accounting and the cat1/cat3 conditions are the Ycash developers' (REFERENCES.md O-13).

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .bounds import NEG_INF, log2_sum


@dataclass(frozen=True)
class Round:
    """One verifier message of the IOP: its round-by-round error before grinding, and its grind."""

    name: str
    error_log2: float  # log2 of the round-by-round error, before any proof of work
    grind_bits: float = 0.0

    @property
    def effective_bits(self) -> float:
        """-log2 of the error per oracle query spent on this round: the round's bits plus its grind."""
        if self.error_log2 == NEG_INF:
            return math.inf
        return -self.error_log2 + self.grind_bits


@dataclass(frozen=True)
class FsParams:
    """Fiat-Shamir / BCS compilation parameters."""

    digest_bits: int = 256  # lambda: Merkle and transcript hash output length
    instances: int = 1  # proofs an adversary must produce at once (adds to the k term)
    # log2 of the constant on t^2 eps_rbr in CMS19: 6, ePrint 2019/834 Section 8.5.1 ("<= 6 (t^2 eps + 4 t^3 /
    # 2^lambda)", from Lemma 5.13, the lifting lemma); also N. Spooner's thesis (UCB/EECS-2020-182, 5.10.5)
    qrom_c1_log2: float = math.log2(6.0)
    # log2 of the constant on t^3 / 2^lambda: 6 * 4 = 24, the same line of ePrint 2019/834 Section 8.5.1.
    # Was 0.0 (C2 = 1, assumed) until the citation audit of 2026-11-19 read the paper: finding C-6 (the QROM
    # hash cap at lambda = 256 moves from 85.0 to 83.5 bits; no check changes). Lemma 4.9's sqrt(a/2^lambda)
    # adds a/2^lambda + 2 sqrt(eps_D a/2^lambda) <= 2^-117 for a < 2^20 at lambda = 256, against a target of
    # at least t/2^98 >= 2^-98 at every t >= 1 (cat3 per layer); not modelled. t' = t + a: for t < a the term is at most
    # 6 a^2 eps_rbr <= 2^(43 - e_min), far below 2^-98 at the e_min >= 152 of every shipping row; not modelled.
    qrom_c2_log2: float = math.log2(24.0)


@dataclass
class LayerResult:
    name: str
    rounds: list[Round]
    classical_bits: float
    quantum_bits: float
    weakest_round: str
    classical_hash_cap: float
    quantum_hash_cap: float
    classical_iop_bits: float = 0.0  # the IOP term alone (no hash-collision cap)
    quantum_iop_bits: float = 0.0
    notes: list[str] = field(default_factory=list)


def classical_bits(rounds: list[Round], fs: FsParams) -> tuple[float, float]:
    """kappa with eps(t) <= t / 2^kappa for every t <= 2^kappa (book Section 28.3.2, average case).

    eps(t) <= (t + k) eps_rbr + 3.5 t^2 / 2^lambda (book Theorems 25.2.1 and 31.2.1), with
    eps_rbr = max over rounds of 2^-(round bits + grind bits). Sufficient conditions:
      (1 + k) eps_rbr <= 2^-(kappa+1)            ->  kappa <= e_min - 1 - log2(1 + k)
      3.5 * 2^kappa / 2^lambda <= 2^-(kappa+1)   ->  kappa <= (lambda - 1 - log2 3.5) / 2
    Returns (kappa, hash cap).
    """
    k = len(rounds) * fs.instances
    e_min = min(r.effective_bits for r in rounds)
    iop = e_min - 1.0 - math.log2(1 + k)
    cap = (fs.digest_bits - 1.0 - math.log2(3.5)) / 2.0
    return min(iop, cap), cap


def quantum_bits(rounds: list[Round], fs: FsParams) -> tuple[float, float]:
    """kappa_Q with eps_Q(t) <= t / 2^kappa_Q for every t <= 2^kappa_Q, from CMS19.

    eps_Q(t) <= C1 t^2 eps_rbr + C2 t^3 / 2^lambda. Sufficient conditions at t = 2^kappa:
      C1 2^kappa eps_rbr <= 2^-(kappa+1)       ->  kappa <= (e_min - 1 - log2 C1) / 2
      C2 2^(2 kappa) / 2^lambda <= 2^-(kappa+1)  ->  kappa <= (lambda - 1 - log2 C2) / 3
    Grinding enters e_min at full value and is therefore halved with it (bounds.GRINDING_QUANTUM).
    Returns (kappa_Q, hash cap).
    """
    e_min = min(r.effective_bits for r in rounds)
    iop = (e_min - 1.0 - fs.qrom_c1_log2) / 2.0
    cap = (fs.digest_bits - 1.0 - fs.qrom_c2_log2) / 3.0
    return min(iop, cap), cap


def evaluate(name: str, rounds: list[Round], fs: FsParams) -> LayerResult:
    c, c_cap = classical_bits(rounds, fs)
    q, q_cap = quantum_bits(rounds, fs)
    weakest = min(rounds, key=lambda r: r.effective_bits)
    e_min = weakest.effective_bits
    k = len(rounds) * fs.instances
    c_iop = e_min - 1.0 - math.log2(1 + k)
    q_iop = (e_min - 1.0 - fs.qrom_c1_log2) / 2.0
    return LayerResult(name, rounds, c, q, weakest.name, c_cap, q_cap, c_iop, q_iop)


def chain_bits(layer_bits: list[float]) -> float:
    """Union bound over recursion layers: eps_chain(t) <= sum eps_i(t) <= t * sum 2^-kappa_i."""
    return -log2_sum([-b for b in layer_bits])


def required_effective_bits(target: float, rounds_count: int, fs: FsParams, quantum: bool) -> float:
    """Per-round effective bits (round bits + grind) needed for `target` bits."""
    if quantum:
        return 2.0 * target + 1.0 + fs.qrom_c1_log2
    return target + 1.0 + math.log2(1 + rounds_count * fs.instances)


def resolve_need(target, rounds_count: int, fs: FsParams, quantum: bool = True) -> float:
    """Per-round effective bits needed: `target` is a float (QROM bits if `quantum`, else classical
    bits, the step 0.6 convention) or a targets.SecurityTarget (cat1, cat3)."""
    if hasattr(target, "need_bits"):
        return target.need_bits(rounds_count, fs)
    return required_effective_bits(float(target), rounds_count, fs, quantum)
