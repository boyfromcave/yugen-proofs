"""RECORD ONLY (revision 6, 2026-11-19): superseded by spbcs.py and revision6.py. The transcript form is now
spBCS (Sharp, Grubbs, ePrint 2026/2615, Protocol 6.5) and condition Q is evaluated with their Theorem 6.6 (2),
a published theorem (lead decision D-a, docs/qrom-compilation.md). Theorem Q's form X stays a recorded
alternative (a proof sketch, referee report 1.4); form C's constants C1 = 24, C2 = 240 are UNPROVED (form C has no
write-back of the challenge, referee report 1.5), and the "a_V folded" constants of this module (12, 96) were
wrong (24, 192; referee report 1.8). Nothing here certifies a row.

QROM bits of a proof tree under Theorem Q, with the constants per system and per transcript form.

Revision 5 (2026-11-19). Replaces the single constant pair of `compose.FsParams` (C1 = 6, C2 = 24) for
the tree statements by the constants of Theorem Q of docs/qrom-compilation.md (section 5.1, with 5.2
(d) and (e) for form C and for arity), which adapts Chiesa, Manohar, Spooner, "Succinct Arguments in
the Quantum Random Oracle Model", ePrint 2019/834 (copy dated January 14, 2020), Theorem 8.6 and its
proof in Section 8.5.1 ("<= 6 (t^2 eps + 4 t^3 / 2^lambda)", C1 = 6, C2 = 24; read 2026-11-19).

Provenance: the constants for CMS19's own construction are Published (CMS19 Section 8.5.1). The
constants of forms X and C are Adapted (Theorem Q, the Ycash developers, 2026: qrom-compilation.md
5.2, changes listed there; under review, review-sheet item 4). The tree accounting (union over the
N proofs, both terms at most t / 2^(kappa + 1)) is Original (the Ycash developers, 2026),
REFERENCES.md O-13; qrom-compilation.md section 6.

Tree bound, with e the effective bits of the weakest round of any proof of the tree:

    kappa_IOP  = (e - 1 - log2 C1 - log2 N) / 2,      kappa_hash = (lambda - 1 - log2 C2 - log2 N) / 3.

Condition Q (targets.py, soundness-method.md 8.3) is min(kappa_IOP, kappa_hash) >= quantum_chain
(64 bits at category 1). Failing it raises `ConditionQFailure`: no table is printed for a row that
fails it.

Every figure is conditional on the transcript being in the CMS form of qrom-compilation.md section
4 (form X for system A, form C for system B): neither system's transcript as built is covered by
Theorem 8.6 or by Theorem Q (section 3 of that document; CITATION-AUDIT C-7).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class QromForm:
    """Theorem Q's constants for one transcript form."""

    name: str
    c1: float
    c2: float
    source: str

    @property
    def c1_log2(self) -> float:
        return math.log2(self.c1)

    @property
    def c2_log2(self) -> float:
        return math.log2(self.c2)


def form_x(arity: int = 2, fold_av: bool = False) -> QromForm:
    """Form X (extendable output, one chain link a prover message; system A). C1 = 6; C2 = 6 (a + 2)
    for inner nodes of arity a (qrom-compilation.md 5.2 (e): 24 for binary trees). With the verifier's
    own calls folded in (t' = t + a_V, a_V <= t: (t + a)^2 <= 2 (t^2 + a^2), (t + a)^3 <= 4 (t^3 + a^3))
    the constants double and quadruple: 12 and 96 at a = 2 (section 6, third row)."""
    c1, c2 = 6.0, 6.0 * (arity + 2)
    if fold_av:
        c1, c2 = 2 * c1, 4 * c2
    tag = ", t' = t + a_V folded in" if fold_av else ""
    return QromForm(f"form X, arity {arity}{tag}", c1, c2,
                    "Theorem Q (qrom-compilation.md 5.1, 5.2 (e)); CMS19 Section 8.5.1 for 6 and 4")


def form_c(arity: int = 2) -> QromForm:
    """Form C (counter-mode expansion; system B). Lemma X doubles the queries (t' = 2 t): C1 = 6 x 4 =
    24; 5.2 (d) turns CMS19's 4 into 5 and arity a into a + 3: C2 = 6 (a + 3) x 8 = 240 at a = 2."""
    return QromForm(f"form C, arity {arity}", 6.0 * 4, 6.0 * (arity + 3) * 8,
                    "Theorem Q (qrom-compilation.md 5.1, 5.2 (d), (e), Lemma X); CMS19 Section 8.5.1")


CMS19 = QromForm("CMS19's own construction", 6.0, 24.0, "CMS19 Section 8.5.1 (Published)")
FORMS = {
    "A": form_x(2),
    "A, a_V folded": form_x(2, fold_av=True),
    "B": form_c(2),
}


class ConditionQFailure(ValueError):
    """Condition Q (proven QROM bits of the tree >= the chain's QROM target) does not hold."""


@dataclass(frozen=True)
class TreeQrom:
    form: QromForm
    e: float
    digest_bits: int
    proofs: int
    quantum_chain: float

    @property
    def iop(self) -> float:
        return (self.e - 1.0 - self.form.c1_log2 - math.log2(self.proofs)) / 2.0

    @property
    def hash(self) -> float:
        return (self.digest_bits - 1.0 - self.form.c2_log2 - math.log2(self.proofs)) / 3.0

    @property
    def bits(self) -> float:
        return min(self.iop, self.hash)

    @property
    def margin(self) -> float:
        return self.bits - self.quantum_chain

    @property
    def meets(self) -> bool:
        return self.margin >= -1e-9

    def need_e(self) -> float:
        """Effective bits a round needs for the IOP term alone to meet the chain's QROM target."""
        return 2.0 * self.quantum_chain + 1.0 + self.form.c1_log2 + math.log2(self.proofs)


def tree_qrom(form: QromForm, e: float, digest_bits: int = 256, proofs: int = 20_000,
              quantum_chain: float = 64.0) -> TreeQrom:
    return TreeQrom(form, e, digest_bits, proofs, quantum_chain)


def require(q: TreeQrom, label: str = "") -> TreeQrom:
    """Hard failure: raise unless condition Q holds."""
    if not q.meets:
        raise ConditionQFailure(
            f"{label or q.form.name}: condition Q fails: {q.bits:.2f} QROM bits of the tree (IOP {q.iop:.2f}, "
            f"hash {q.hash:.2f}) < {q.quantum_chain:.0f}; e = {q.e:.2f}, lambda = {q.digest_bits}, N = {q.proofs:,}, "
            f"C1 = {q.form.c1:g}, C2 = {q.form.c2:g}")
    return q
