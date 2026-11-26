"""Named security targets: NIST category 1 (`cat1`) and category 3 (`cat3`) equivalence.

The lead architect's target (2026-11-18): the whole suite at NIST category 1, with a parameter path
to category 3. NIST defines the categories by comparison with key search on AES-128 / AES-192
(categories 1 and 3) and collision search on SHA3-256 / SHA3-384 (categories 2 and 4); see
docs/soundness-method.md section 8 for the source and for why each condition below is the right
formalisation.

For one proof layer, a target is met when all of the following hold:

  C  proven classical soundness of the IOP term (book Thms 25.2.1 + 31.2.1, no conjectured
     proximity bound) >= classical_chain + log2(layers): the union bound over `layers` recursion
     layers then leaves >= classical_chain for the composed chain (bounds.RECURSION_UNION);
  Q  proven QROM soundness of the IOP term (CMS19, C1 = 6) >= quantum_chain + log2(layers);
  G  attack cost: every round's effective bits (round bits + full grinding bits) >= attack_bits.
     Under NIST's depth-limited model (MAXDEPTH D, measured in oracle calls) parallel Grover over a
     bad set of density 2^-e needs about 2^e / D oracle calls (Zalka 1999: no better
     parallelisation than splitting the space), exactly as AES key search over 2^e keys needs
     2^e / D AES calls. So e >= 128 is AES-128 equivalence for every D, provided one oracle call
     (at least one Keccak-f[1600]) costs at least one AES-128 evaluation (an estimate, section 8);
  H  digest length: attack rule  lambda >= digest_attack (generic Merkle/transcript collision at
     2^(lambda/2) classical hash calls is at least NIST's category-2 (resp. 4) benchmark, which NIST
     orders above category 1 (resp. 3));
     proven rule  the book's 3.5 t^2 / 2^lambda term itself gives >= classical_chain +
     log2(layers) bits, i.e. lambda >= digest_proven.

C is binding in every configuration computed here; Q and G follow from it (Q because CMS19 halves
the same e, G because e >= C's requirement > attack_bits). They are checked anyway.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .compose import FsParams, LayerResult


@dataclass(frozen=True)
class SecurityTarget:
    name: str
    nist_category: int
    classical_chain: float  # proven classical bits for the composed leaf -> bundle -> merge -> merge chain
    quantum_chain: float  # proven QROM bits for the chain (CMS19)
    attack_bits: float  # per-round effective bits: Grover-under-MAXDEPTH equivalence with AES key search
    digest_attack: int  # digest bits by the attack-cost rule
    digest_proven: int  # digest bits by the proven-bound rule (rounded up to a whole byte)
    layers: int = 4

    @property
    def margin(self) -> float:
        return math.log2(self.layers)

    @property
    def classical_layer(self) -> float:
        return self.classical_chain + self.margin

    @property
    def quantum_layer(self) -> float:
        return self.quantum_chain + self.margin

    def need_bits(self, rounds_count: int, fs: FsParams) -> float:
        """Effective bits (round bits + grind) every round needs for C, Q and G at once."""
        c = self.classical_layer + 1.0 + math.log2(1 + rounds_count * fs.instances)
        q = 2.0 * self.quantum_layer + 1.0 + fs.qrom_c1_log2
        return max(c, q, self.attack_bits)

    def binding(self, rounds_count: int, fs: FsParams) -> str:
        c = self.classical_layer + 1.0 + math.log2(1 + rounds_count * fs.instances)
        q = 2.0 * self.quantum_layer + 1.0 + fs.qrom_c1_log2
        return "classical (C)" if c >= max(q, self.attack_bits) else ("quantum (Q)" if q >= self.attack_bits else "attack (G)")

    def digest_ok(self, digest_bits: int, rule: str = "attack") -> bool:
        return digest_bits >= (self.digest_attack if rule == "attack" else self.digest_proven)

    def assess(self, res: LayerResult, fs: FsParams, rule: str = "attack") -> dict[str, bool]:
        e_min = min(r.effective_bits for r in res.rounds)
        return {
            "C": res.classical_iop_bits >= self.classical_layer - 1e-9,
            "Q": res.quantum_iop_bits >= self.quantum_layer - 1e-9 and res.quantum_hash_cap >= self.quantum_layer,
            "G": e_min >= self.attack_bits,
            "H": self.digest_ok(fs.digest_bits, rule),
        }


def _digest_proven(chain: float, layers: int = 4) -> int:
    """Smallest whole-byte lambda with (lambda - 1 - log2 3.5) / 2 >= chain + log2(layers)."""
    lam = 2.0 * (chain + math.log2(layers)) + 1.0 + math.log2(3.5)
    return 8 * math.ceil(lam / 8)


CAT1 = SecurityTarget(
    name="cat1", nist_category=1, classical_chain=128.0, quantum_chain=64.0, attack_bits=128.0,
    digest_attack=256, digest_proven=_digest_proven(128.0),
)
CAT3 = SecurityTarget(
    name="cat3", nist_category=3, classical_chain=192.0, quantum_chain=96.0, attack_bits=192.0,
    digest_attack=384, digest_proven=_digest_proven(192.0),
)
TARGETS = {"cat1": CAT1, "cat3": CAT3}
