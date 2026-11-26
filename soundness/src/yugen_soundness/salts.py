"""RECORD ONLY (revision 6, 2026-11-19): superseded by spbcs.py (Sharp, Grubbs, ePrint 2026/2615, Theorem 6.6 (3)
and (4), with a 64-byte proof salt and 64-byte leaf salts; docs/zk-quantum.md section 3). Lemma H below is that
paper's Definition I.1 leaf term (Published, not Adapted), and zeta_IOP < 2^-240 is withdrawn as a claim: the
IOP-level honest-verifier zero knowledge of both systems is open (zk-quantum.md section 5). The byte and block
counts below stay valid.

Salt length: the statistical zero-knowledge error of salted Merkle trees, per proof and per tree.

Revision 5 (2026-11-19). docs/zk-quantum.md section 3: Lemma H (Adapted from Chiesa, Yogev, "Building
Cryptographic Proofs from Hash Functions", Lemma 17.3.1 at t = infinity, Claim 3.4.2, Remark 18.6.2)
bounds the statistical distance of the salted trees of one proof by

    sum over unopened leaves  2^(-(s - sigma)/2) + sqrt(n_b) 2^(-s/2)

(s salt bits, sigma = 256 digest bits, n_b <= 2^12 bits of leaf content), and Theorem ZQ (Adapted;
CMS19 Lemma 7.3's argument) carries it to quantum distinguishers with any number of queries:
zeta <= zeta_IOP + Lemma H + k^2 / 2^257 (the last term for form C only). zeta_IOP < 2^-240
(zk-composition.md 4.2). Independent published support for s = 2 sigma: GordieHowe, ePrint 2026/2615,
Theorem 6.6 (3) and Section 8.4 (CITATION-AUDIT C-21; not used for the numbers here).

At s = 256 = sigma no statistical statement exists (CY Claim 3.4.1 lower bound; zk-quantum.md 2.1):
the error is reported as 1 (vacuous).

The tree: only leaf proofs hide (node proofs are not zero knowledge), so the per-tree figure sums
over the at most 2^14 leaves; the figure over all 20,000 proofs is printed beside it as an upper one.
Bytes: a salt of s bits is s / 8 bytes in each opened leaf; the built salt is 32 bytes.
Provenance of this module's accounting (per tree, bytes): Original (the Ycash developers, 2026).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

SALT_CHOICES = (256, 384, 512, 576)
LEAD_CHOICE = 512  # the lead architect's choice (2026-11-19), zk-quantum.md section 5
BUILT_SALT_BITS = 256
SIGMA = 256  # digest bits
N_U = 2**24  # unopened salted leaves of one proof, upper figure over every salted tree (zk-quantum.md 3)
N_B = 2**12  # bits of leaf content, upper figure
ZETA_IOP_LOG2 = -240.0  # upper figure (zk-composition.md 4.2)
TREE_LEAVES = 2**14
TREE_PROOFS = 20_000


def per_leaf_log2(s: int, sigma: int = SIGMA, n_b: int = N_B) -> float:
    """log2 of CY Claim 3.4.2's bound for one unopened leaf (0 = vacuous at s <= sigma)."""
    if s <= sigma:
        return 0.0
    return min(0.0, math.log2(2.0 ** (-(s - sigma) / 2) + math.sqrt(n_b) * 2.0 ** (-s / 2)))


@dataclass(frozen=True)
class SaltRow:
    salt_bits: int
    per_leaf_log2: float
    per_proof_log2: float
    per_tree_log2: float  # over the leaf proofs
    per_tree_all_log2: float  # over every proof of the tree (upper)
    bytes_per_opened_leaf: int
    added_bytes_per_opened_leaf: int

    @property
    def statistical(self) -> bool:
        return self.per_proof_log2 < 0.0


def _cap(x: float) -> float:
    return min(0.0, x)


def salt_row(s: int, n_u: int = N_U, form_c_links: int | None = None) -> SaltRow:
    """The error of Theorem ZQ at salt length `s` (bits). `form_c_links`: k chain links of a form-C
    transcript (system B), adding k^2 / 2^257."""
    leaf = per_leaf_log2(s)
    terms = [ZETA_IOP_LOG2, leaf + math.log2(n_u)]
    if form_c_links:
        terms.append(2 * math.log2(form_c_links) - 257)
    top = max(terms)
    proof = _cap(top + math.log2(sum(2.0 ** (t - top) for t in terms))) if leaf < 0 else 0.0
    return SaltRow(s, leaf, proof, _cap(proof + math.log2(TREE_LEAVES)), _cap(proof + math.log2(TREE_PROOFS)),
                   s // 8, (s - BUILT_SALT_BITS) // 8)


def proof_bytes_added(s: int, opened_leaves: int) -> int:
    """Bytes a proof gains against the built 32-byte salts, for `opened_leaves` opened salted leaves."""
    return opened_leaves * (s - BUILT_SALT_BITS) // 8


def keccak_perms(leaf_bytes: int, s: int) -> int:
    """Keccak-256 permutations to hash a leaf of `leaf_bytes` plus an s-bit salt (rate 136, pad10*1)."""
    return (leaf_bytes + s // 8 + 1 + 135) // 136


def sha256_blocks(leaf_bytes: int, s: int) -> int:
    """SHA-256 compressions for a leaf of `leaf_bytes` plus an s-bit salt (64-byte blocks, 9 bytes of padding)."""
    return (leaf_bytes + s // 8 + 9 + 63) // 64
