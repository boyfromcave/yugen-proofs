# Referee report: SHAPE-VIOLATION, Lemma TE.3 and H-BIND (`lemma-tree-extraction.md` revision 5.2, `b9836a8`)

Independent, adversarial referee. Read only in the code repositories; nothing built or run.
Sources read: `lemma-tree-extraction.md` sections 2 (H-BIND), 3, 6 (Lemma TE.3), 6b (cells through `E`);
spec tag `spec-0.4.8` (`b108428`) §3.2 (0xbf, SPEC-198), §15.2–15.3; System A `yugen-proof-a` `0cdad2f`
(`guests/bundle_merge_e2.py` 1-40, `docs/recursion.md` 202, 246-274, 582, 691, 961); System B
`yugen-proof-b2/wt/s045` branch `agg` at `b6dd2ba` (`src/native.rs` 40, `src/bundle.rs` 29, 96-110, 298-310,
`src/bvirt.rs` 31, 85-130, 178-211).

**Verdict: PASS WITH CONDITIONS** (TE3-1 to TE3-5, section 4). No proof step is wrong; the conditions are about
how `eps_bind` is defined and stated, and about naming the exits that are not collisions.

## 0. What earlier reports cover, and the gap

| Report | Covers of TE.3 / H-BIND |
|---|---|
| `tree-extraction-referee.md` (rev 1) | H-BIND not examined (F-6) |
| `qc-and-status-referee.md` (rev 2) | asked for SHAPE-VIOLATION and H-BIND as collision resistance (T-1); did not referee the text that answers it |
| `zkq-te3-r8-referee.md` | TE.3 as in revision 3: PASS WITH CONDITIONS (M-3: check at the child, hash-chain argument, list `merge_statement`, `Hvar_bundle-kids`; root header case); N-3 |
| `tree-extraction-rev4/5/51-referee.md` | section 6b (shape, kind, fold); `eps_bind` with H_int "stays outside `k_q`" (rev4 2.4) only; each says TE.3 remains unrefereed |

**Gap refereed here:** revision 3.1's M-3 text (step 3's child-side check, TE.3 (a) hash chain, (b) with the
root header), its 6b extension (H_int, cells through `E`), and H-BIND / `eps_bind` (definition, domains, bounds).
M-3 is met as written; not re-litigated.

## 1. Every disagreement: collision, or something else?

Exits from "extracted tree = published statement" that a cheating prover can aim at, by edge:

| Edge / place | Where the two values meet | Exit |
|---|---|---|
| A, merge parent -> merge child | parent: `D_c = H_bundle-node(cells_v)` -> `merge_statement` (Keccak-256, parent's seeds); child: own `D` from `w_c` -> `merge_statement` (own seeds, pinned in its public input) | Keccak or `H_bundle-node` or `Hvar_bundle-kids` collision at the first differing layer. Correct |
| A, merge parent -> sub child (depth 0) | parent rebuilds by the sub program's statement function | as above, provided the parent's choice of program fixes the child's statement function (the verifier and seed it verifies under: H-DS). Correct given H-DS |
| B, top -> published child (K0/KM) | `node_digest` in circuit vs `framed(0x85, ..)` natively | `H_bundle-node` / `Hvar_bundle-kids` collision. Correct |
| B, top -> internal child (KI/KI0) | both witnesses preimages of `E = H_int(OVER_CELLS or OVER_LEAVES || LE16(k) || ..)` | H_int collision, then as above. Correct. `auth_mode` is not in `E` but is a circuit constant, bound by the pinned key (H-DS) |
| Root count | `Tree::check` reads the header; root witness hashes its own count | header-digest collision (listed). Correct |
| Relation does not recompute / range-check a cell | — | **not a collision**: C-4 (unaudited; A's `count_le` mutation, `recursion.md` 691, shows how close this is), `Stream::piece` encoded-bytes caveat |
| Child verified under a foreign key / program | — | **not a collision**: H-DS (and 6b's kind pinning) |
| Inner proof rejected natively | — | C2-VIOLATION |
| Extraction fails | — | FAIL (Theorem TE') |

So: **every disagreement is a collision counted in `eps_bind` or a C2-VIOLATION only under C-4 and H-DS**, which
TE.3 assumes (C-4 explicitly; H-DS implicitly through "the same chain"). That is correct but must be said (TE3-3).
Part (b) (counting along agreeing edges, `<= N + a_m` with the queued-unchecked children) is right.

## 2. Domain separation

- B: every chain hash is `SHAKE256("Yg" 00 id || body)[0..32]` (`native.rs` 40, `sponge::framed`); ids 0x85
  (`BUNDLE_NODE`), the `Hvar` ids (LE64 length prefix), 0xbf (H_int, reserved since spec 0.4.8 SPEC-198,
  `RESERVED_IDS`, checked by `check_vectors.py` 67-68). H_int's two uses are split by a tag byte
  (`OVER_CELLS`/`OVER_LEAVES`) and fixed-length bodies (unoccupied slots zeroed, `k` hashed). `H_bundle-node`'s
  body is a fixed 72 bytes. Separated.
- A: `merge_statement` is **unframed** Keccak-256 of a fixed cell count. Fine for TE.3 (see below), but its
  separation from the oracle's part tags is an open T-1 item (`what-is-proven.md` queue), not settled here.
- For TE.3 itself separation is not needed **if** `eps_bind` counts a collision of the primitive on any two
  inputs: the hash-chain argument then never cares which "function" the colliding inputs belong to. As written,
  `eps_bind` counts "two distinct inputs of **one of these functions**"; a cross-function collision (e.g. a sub
  vs merge statement under Keccak, if layers ever misalign) would fall outside it. The layers do align on every
  edge of section 1 (given H-DS), but the definition should not depend on that (TE3-1). Keccak-256 (pad 0x01)
  and SHAKE256 (pad 0x1F) are different functions; no edge compares across them.

## 3. Collision bounds

- Every digest in the H-BIND chain is **32 bytes** (`H_bundle-node`, `Hvar_*`, H_int, `merge_statement`, B's
  SHA-256 `cs_digest`). The 48-byte outputs (note tree, `rho`, `cm`, spec §3 SPEC-133) are leaf-statement
  *contents*, hashed into 32-byte `Hvar` digests; they are not links of the chain. So the weakest link is 256 bits.
- Classical, generic (random-function heuristic for the concrete function): `Pr <= q(q-1)/2^257`; cost
  `~2^128`. Right. For 48 bytes it would be `2^192`.
- Quantum: `Theta(2^(n/3))` queries — Brassard, Høyer, Tapp, "Quantum cryptanalysis of hash and claw-free
  functions" (LATIN 1998) for the upper bound, Zhandry, "A note on the quantum collision and set equality
  problems" (QIC 2015) for tightness on random functions: `2^85.3` at 256 bits, `2^128` at 384. **Both from
  memory; neither is in the reference-paper collection (REFERENCES.md).** BHT assumes free qRAM; without it the best known is about
  `2^(2n/5)` = `2^102` (Chailloux, Naya-Plasencia, Schrottenloher, ASIACRYPT 2017; from memory). NIST prices
  collisions in classical gates only (call for proposals §4.A.5, `call-for-proposals-final-dec-2016.pdf`
  pp. 16-18, in the folder; as already recorded in `security-category-referee.md` §1 item 3). The document's
  "of order `2^85`" is the conservative BHT figure and is right as such.
- Does `eps_bind` move a figure? Classical: `2^128` > 121.89 (T-e). Quantum: BHT `2^85` > 69.58 / 70.45 (T-g)
  and > 76.72 / 77.60 (T-h). So `eps_bind` does not dominate any printed level, under BHT. It is not stated
  numerically anywhere (TE3-2).
- "Standard-model collision resistance" of an unkeyed function has no non-trivial asymptotic meaning; the document
  correctly states it as an explicit reduction (`eps_bind` is the advantage of the specific `B` built from `A` and
  `E_T`), i.e. the human-ignorance reading. Fine; say so in one line (TE3-4).
- QROM: `B` simulates the compressed oracle and measures; it is a quantum algorithm of about the size of
  `A + E_T^Q`, so `eps_bind` is the quantum advantage at that size. Correct.

## 4. Conditions

1. **TE3-1 (MINOR).** Define `eps_bind` as the collision advantage against the **primitives** (Keccak-256;
   SHAKE256 at 32 bytes on framed inputs; SHA-256 for `cs_digest`), any two distinct inputs, or add one sentence
   proving that on every edge kind (A merge/sub; B K0/KM/KI/KI0; root header) the two chains apply the same function
   at each layer because the parent fixes the child's program/key (H-DS).
2. **TE3-2 (MINOR).** State `eps_bind` numerically: `<= q(q-1)/2^257` classically (generic), `O(q^3/2^256)`
   quantum (BHT, tight per Zhandry), with `q` the hash evaluations of `B`; note that no H-BIND link is 48 bytes;
   and that at the printed levels it dominates nothing. Cite BHT 1998, Zhandry 2015 (and CNS 2017) marked
   "from memory, not in the folder", and [CFP] §4.A.5 for the realistic view.
3. **TE3-3 (MINOR).** In TE.3's statement, name H-DS beside C-4 as a hypothesis, and say once that a
   disagreement not covered by a collision is a C-4 failure (unaudited), an H-DS failure, C2-VIOLATION or FAIL;
   carry the `Stream::piece` caveat into TE.3 (a), not only 6b.
4. **TE3-4 (NOTE).** One line: H-BIND is the explicit-reduction (human-ignorance) form of collision resistance.
5. **TE3-5 (RECORD).** Update section 11's table and the TE.3 row: TE.3 (rev 3.1 + 6b) and H-BIND refereed here,
   pass with conditions TE3-1 to TE3-5. `what-is-proven.md` is **not** updated by this report (not a PASS); its
   tree rows stay conditional on C2, K-A, K-B, T-1, C-4 (unaudited) and H-BIND.
