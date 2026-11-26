"""Revision 6: the spBCS transcript form and the errors of Sharp and Grubbs' Theorem 6.6.

Source (read 2026-11-19 from the lead architect's copy): C. Sharp, P. Grubbs, "Faster and Smaller
Anonymous Credentials from Standardized Signatures" (the GordieHowe system), Cryptology ePrint
Archive, Paper 2026/2615 [SG26]: Protocol 6.5 (spBCS), Theorem 6.6 parts (2), (3), (4), Definition
I.1 (the quantities c, c', k_q, q_S, eps_ov, eps_key, eps_leaf), Section I.1 (oracle domain,
challenge inputs, samplers, Merkle trees), Theorems I.5, I.6 and their proofs (Section I.2).

Provenance: every formula below is **Published** (SG26, at the place named beside it), used as is.
The counter-mode stream (system B's documented alternative) is **Adapted**: Theorem 6.6 (2) with
Lemma X of docs/qrom-compilation.md (the Ycash developers, 2026), whose only change is that the
adversary's t quantum queries become 2t. The tree accounting (union over the N proofs of a tree;
the bits are the query count at which the tree term reaches 1/2) is **Original (the Ycash
developers, 2026)**, REFERENCES.md O-13.

Knowledge soundness, QROM (Theorem 6.6 (2)):

    eps_ex(t) = 2 sqrt(k_q / 2^(8(b+e))) + 6 (t + k_q)^2 (eps_k + c' (t + k_q) / 2^(8b)),
    c' = max(2, c) + n_J + 1,  c = N_msg max(1, m),
    k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2 max(1, l_max)))).

Everlasting zero knowledge, QROM (Theorem 6.6 (3)), Q adaptively chosen proofs, t hash queries
before the last proof and unbounded after:

    eps_zk(t, Q) = 4 Q t / 2^(4 b_s) + Q (Q - 1) / 2^(8 b_s) + Q (eps_key + eps_ov + eps_hvzk + n_pos eps_leaf),
    eps_leaf = (1/2) sqrt(2^(8b) / 2^(8 b_l)) + sqrt(ln N_leaf / (2 * 2^(8 b_l))),
    eps_key = C(N_msg, 2) 2^(-8b).

Unconditional witness indistinguishability (Theorem 6.6 (4)), no bound on hash queries:

    eps_wi(Q, L) = Q (2 n_pos eps_leaf + 2 eps_hvzk + eps_ov + eps_key
                      + sqrt(((L + 1) ln 2 + 2 ln(L + 1)) / (2 * 2^(8 b_s)))).

eps_hvzk (the IOP's honest-verifier zero-knowledge error, SG26 Definition 2.22) is not established
for either system (zk-quantum.md section 5); every zero-knowledge figure is reported as
"figure + Q eps_hvzk" (or + 2 Q eps_hvzk), never with eps_hvzk filled in.

Message counts (TranscriptCounts): the verifier messages of a proof are its round list (the rounds
the soundness calculator counts in k) plus OTHER_ROUNDS (shipping.py); one prover message before
each verifier message (an upper figure: consecutive prover parts merge into one item); m = 2 oracle
strings a prover message (upper figure). These are estimates (E) until the transcript modules report
the counts (qrom-compilation.md section 7, acceptance).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

DIGEST_BYTES = 32  # b: 256-bit digests in both systems
PROOF_SALT_BYTES = 64  # b_s: lead decision D-b (qrom-compilation.md 4.3, zk-quantum.md 3)
LEAF_SALT_BYTES = 64  # b_l: 512-bit leaf salts (zk-quantum.md 3)
FORMS = ("spBCS, SHAKE256 stream", "spBCS, counter-mode SHA-256 stream (Lemma X)")


@dataclass(frozen=True)
class TranscriptCounts:
    """The quantities of SG26 Definition I.1 for one proof system's worst proof."""

    system: str
    verifier_messages: int  # |J_V|
    prover_messages: int  # |J_P|
    oracles_per_message: int  # m
    q_iop: int  # opened positions of one proof over all its oracles: DRAWN QUERIES, PADDED SLOTS INCLUDED (a grouped
    # verifier that repeats an index in unused slots checks those openings too; docs/lemma-d-referee.md m-1, revision 10)
    log2_l_max: int  # log2 of the longest oracle string (positions)
    n_pos_log2: float  # log2 of all oracle positions of a leaf proof (salted trees)
    leaf_bytes: int  # L_leaf: largest leaf encoding (bytes, without the salt)
    stream_bytes: int  # b + e: the longest stream
    n_branches: int = 0  # n_B (no merges: total order)
    n_j: int = 0  # n_J (no merges)
    source: str = ""
    shortest_stream_bytes: int | None = None  # revision 10.1 (R10-9): b + e of the theorem is the SHORTEST stream
    # (SG26 page 59: "A longer stream only lowers these terms"); None keeps the revision 6 to 10 reading (longest)

    @property
    def n_msg(self) -> int:
        return self.verifier_messages + self.prover_messages

    @property
    def c(self) -> int:
        """Digests in one challenge input (SG26 Definition I.1 item 1)."""
        return self.n_msg * max(1, self.oracles_per_message)

    @property
    def c_prime(self) -> int:
        """c' = max(2, c) + n_J + 1 (SG26 Theorem 6.6, preamble)."""
        return max(2, self.c) + self.n_j + 1

    @property
    def k_q(self) -> int:
        """The verifier's hash queries (SG26 Definition I.1 item 1)."""
        return 2 * self.n_msg + self.n_branches + self.q_iop * (1 + (1 + self.log2_l_max))

    @property
    def q_s(self) -> int:
        """The simulator's hash queries per proof: 2 n_pos + N_msg + n_B (Definition I.1)."""
        return int(2 * 2.0 ** self.n_pos_log2) + self.n_msg + self.n_branches


# --- knowledge soundness, Theorem 6.6 (2), tree of N proofs ------------------------------------------------


def _solve(f, lo: float = 0.0, hi: float = 200.0) -> float:
    """Largest kappa in [lo, hi] with f(kappa) <= log2(1/2) = -1 (f increasing), by bisection."""
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) <= -1.0:
            lo = mid
        else:
            hi = mid
    return lo


@dataclass(frozen=True)
class SpbcsTree:
    """QROM bits of a tree of N proofs under Theorem 6.6 (2), one transcript form."""

    counts: TranscriptCounts
    form: str
    e: float  # effective bits of the weakest round (eps_k = 2^-e)
    proofs: int = 20_000
    digest_bytes: int = DIGEST_BYTES
    quantum_chain: float = 64.0

    @property
    def query_factor(self) -> int:
        """Lemma X: a counter-mode stream doubles the adversary's quantum queries."""
        return 2 if "counter" in self.form else 1

    def _t(self, kappa: float) -> float:
        return self.query_factor * 2.0**kappa + self.counts.k_q

    @property
    def iop(self) -> float:
        """kappa with N 6 (t' + k_q)^2 eps_k = 1/2."""
        n = math.log2(self.proofs)
        return _solve(lambda k: n + math.log2(6.0) + 2 * math.log2(self._t(k)) - self.e)

    @property
    def hash(self) -> float:
        """kappa with N 6 c' (t' + k_q)^3 / 2^(8b) = 1/2."""
        n = math.log2(self.proofs)
        return _solve(lambda k: n + math.log2(6.0 * self.counts.c_prime) + 3 * math.log2(self._t(k))
                      - 8 * self.digest_bytes)

    @property
    def stream_bytes_used(self) -> int:
        """The b + e the stream term is evaluated at: the shortest stream when the counts give it (revision 10.1,
        R10-9; the theorem's b + e), else the longest (the record revisions)."""
        sh = self.counts.shortest_stream_bytes
        return sh if sh is not None else self.counts.stream_bytes

    @property
    def stream_term_log2(self) -> float:
        """log2 of N 2 sqrt(k_q / 2^(8(b+e))), independent of t."""
        return (math.log2(self.proofs) + 1 + (math.log2(self.counts.k_q) - 8 * self.stream_bytes_used) / 2)

    @property
    def c1(self) -> float:
        return 6.0 * self.query_factor**2

    @property
    def c2(self) -> float:
        return 6.0 * self.counts.c_prime * self.query_factor**3

    @property
    def bits(self) -> float:
        return min(self.iop, self.hash)

    @property
    def margin(self) -> float:
        return self.bits - self.quantum_chain

    @property
    def meets(self) -> bool:
        return self.margin >= -1e-9 and self.stream_term_log2 < -1.0

    def need_e(self) -> float:
        """Effective bits a round needs for the IOP term alone to meet the chain's QROM target."""
        return 2.0 * (self.quantum_chain + math.log2(self.query_factor)) + 1.0 + math.log2(6.0) + math.log2(self.proofs)


def classical_need(counts: TranscriptCounts, proofs: int = 20_000, classical_chain: float = 128.0,
                   from_k_q: bool = False) -> float:
    """Effective bits a round needs for condition C under the ROM part of Theorem 6.6 (2),
    eps^C_ex(t) = (t + k_q)(eps_k + c' (t + k_q) / 2^(8b)), summed over the N proofs of a tree, in the calculator's
    convention eps(t) <= t / 2^(kappa + 1) for every t <= 2^kappa (soundness-method.md 8.5b). The binding t is 1:
    N (1 + k_q) 2^-e <= 2^-(kappa + 1). With `from_k_q` the convention is read for t >= k_q only (t + k_q <= 2 t):
    N 2 t 2^-e <= t 2^-(kappa + 1). Finding Q-5 of docs/qrom-compilation.md (Original, the Ycash developers, 2026)."""
    n = math.log2(proofs)
    if from_k_q:
        return classical_chain + 2.0 + n
    return classical_chain + 1.0 + n + math.log2(1 + counts.k_q)


class ConditionQFailure(ValueError):
    """Condition Q (QROM bits of the tree >= the chain's target) does not hold under Theorem 6.6 (2)."""


def require(q: SpbcsTree, label: str = "") -> SpbcsTree:
    if not q.meets:
        raise ConditionQFailure(
            f"{label or q.counts.system}: condition Q fails under SG26 Theorem 6.6 (2), {q.form}: "
            f"{q.bits:.2f} QROM bits (IOP {q.iop:.2f}, hash {q.hash:.2f}) < {q.quantum_chain:.0f}; e = {q.e:.2f}, "
            f"c' = {q.counts.c_prime}, k_q = {q.counts.k_q}, N = {q.proofs:,}")
    return q


# --- zero knowledge, Theorem 6.6 (3) and (4) ------------------------------------------------------------


def ln_n_leaf(leaf_bytes: int) -> float:
    """ln of N_leaf = sum_{j=0}^{L_leaf} 256^j (Definition I.1), computed in closed form."""
    L = leaf_bytes
    return L * math.log(256.0) + math.log((256.0 - 256.0**-L) / 255.0)


def eps_leaf_log2(digest_bytes: int = DIGEST_BYTES, leaf_salt_bytes: int = LEAF_SALT_BYTES,
                  leaf_bytes: int = 512) -> float:
    """log2 of eps_leaf (Definition I.1); 0 (vacuous) when the first term is at least 1."""
    t1 = 0.5 * 2.0 ** (4 * digest_bytes - 4 * leaf_salt_bytes)
    t2 = math.sqrt(ln_n_leaf(leaf_bytes) / 2.0) * 2.0 ** (-4 * leaf_salt_bytes)
    return min(0.0, math.log2(t1 + t2))


def eps_key_log2(n_msg: int, digest_bytes: int = DIGEST_BYTES) -> float:
    return math.log2(n_msg * (n_msg - 1) / 2) - 8 * digest_bytes


def _lsum(xs: list[float]) -> float:
    top = max(xs)
    return top + math.log2(sum(2.0 ** (x - top) for x in xs))


@dataclass(frozen=True)
class ZkError:
    """Theorem 6.6 (3) at (t, Q), with every term in log2; eps_hvzk is reported separately."""

    t_log2: float
    q_log2: float
    salt_term: float  # 4 Q t / 2^(4 b_s)
    collision_term: float  # Q (Q - 1) / 2^(8 b_s)
    key_term: float  # Q eps_key
    leaf_term: float  # Q n_pos eps_leaf

    @property
    def total_log2(self) -> float:
        """log2 of eps_zk(t, Q) - Q eps_hvzk (eps_ov = 0: every challenge set is a power of two)."""
        return min(0.0, _lsum([self.salt_term, self.collision_term, self.key_term, self.leaf_term]))


def eps_zk(counts: TranscriptCounts, t_log2: float, q_log2: float, proof_salt_bytes: int = PROOF_SALT_BYTES,
           leaf_salt_bytes: int = LEAF_SALT_BYTES, digest_bytes: int = DIGEST_BYTES) -> ZkError:
    q = 2.0**q_log2
    coll = (q_log2 + math.log2(q - 1) if q > 1 else -math.inf) - 8 * proof_salt_bytes
    leaf = eps_leaf_log2(digest_bytes, leaf_salt_bytes, counts.leaf_bytes)
    return ZkError(t_log2, q_log2, 2 + q_log2 + t_log2 - 4 * proof_salt_bytes,
                   coll if q > 1 else -1e9, q_log2 + eps_key_log2(counts.n_msg, digest_bytes),
                   q_log2 + counts.n_pos_log2 + leaf if leaf < 0 else 0.0)


def eps_wi_log2(counts: TranscriptCounts, q_log2: float, l_bits_log2: float,
                proof_salt_bytes: int = PROOF_SALT_BYTES, leaf_salt_bytes: int = LEAF_SALT_BYTES,
                digest_bytes: int = DIGEST_BYTES) -> float:
    """log2 of eps_wi(Q, L) - 2 Q eps_hvzk (Theorem 6.6 (4)), L = 2^l_bits_log2 bits of statement and witnesses."""
    L = 2.0**l_bits_log2
    leaf = eps_leaf_log2(digest_bytes, leaf_salt_bytes, counts.leaf_bytes)
    salt = 0.5 * (math.log2(((L + 1) * math.log(2) + 2 * math.log(L + 1)) / 2.0) - 8 * proof_salt_bytes)
    return min(0.0, q_log2 + _lsum([1 + counts.n_pos_log2 + leaf, eps_key_log2(counts.n_msg, digest_bytes), salt]))
