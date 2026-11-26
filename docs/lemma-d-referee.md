# Referee report: Lemma D (duplicate openings under spBCS)

Part of Yugen. `yugen-proofs`. 2026-11-19. Independent referee's report on
`docs/lemma-d-duplicate-openings.md` revision 1 (commit `37c58d3`).

## 0. Verdict

**PASS WITH CONDITIONS.** Theorem D is correct as stated: the extra term for uncompared duplicate
openings is 0 bits in the ROM and the QROM, at every `t`, provided `k_q` counts every opening
record the verifier checks.

**Must either system add the write-once position table or any comparison of openings? No.**

No BLOCKER and no MAJOR finding. Four MINOR findings (conditions C-1 to C-4, all edits to
documents or to one count in the calculator; none changes a verifier) and notes.

## 1. Method

- **Sources read from rendered pages.** The page renderer exists in this repository
  (`.tools-venv`, `pypdfium2`); pages were rendered to images in a scratch directory outside every
  repository and read as images, not from the text layer. Read this way:
  [SG26] C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized
  Signatures*, ePrint 2026/2615, pages 13 (Definitions 2.17, 2.18), 57 and 58 (Protocol 6.5,
  Theorem 6.6), 130 and 131 (Section I.1, Definition I.1), 137 and 138 (Protocol I.9), 140 to 143
  (Lemmas I.12, I.14, I.15, Definition I.13, Theorem I.16 and its proof);
  [CMS19] A. Chiesa, P. Manohar, N. Spooner, *Succinct Arguments in the Quantum Random Oracle
  Model*, ePrint 2019/834, pages 20 (Definitions 4.6 to 4.8, Lemma 4.9), 22 (Definition 5.6, Lemmas
  5.7, 5.9, 5.10, footnote 6), 33 (Lemmas 6.10, 6.11).
- **Code read, read-only, at committed heads** (both working trees carry another agent's
  uncommitted edits, which were not read): `yugen-proof-a` at `b467aa8`
  (`guests/e2/j_wi.py` `wi_query`, `wi_queries`, `wi_level_queries` and their call sites;
  `guests/e2/c_open.py` `verify_merkle_cap`, `walk_window`, `level_positions`, the
  `opening_query` call sites; the generated `vendor/leanMultisig/guests/lean_ethereum_e2.py`
  `decode_query_windows`, `walk_path`); `yugen-proof-b2` at `0f84f74` (`src/groups.rs`,
  `src/stamp.rs` `Link` / `Layout::with_shared`; `vendor/binius64/crates/recursion/src/channel.rs`
  `recv_salted_merkle_commitment`, `recv_openings`, `recv_openings_deferred`, `defer_queries`,
  `sample_bits`; `.../recursion/src/merkle.rs` `verify_layer`, `verify_opening`,
  `verify_opening_2x`, `fold_to_root`; `vendor/binius64/crates/iop/src/fri/verify.rs` `verify`,
  `verify_queries`, `reduce_all`; `.../fri/batch.rs` `open_queries`, `reduce_queries`;
  `.../iop/src/merkle_channel.rs` native `recv_openings`).
- **Numbers recomputed** independently (section 6).
- No test was run and nothing was built.

## 2. Attack 1: the bad set (does it contain every digest collision?)

Rendered [SG26] Lemma I.12 (page 140): "Let B be the set of databases db with a *digest
collision*, two distinct recorded inputs whose answers have the same digest, or with a *knowledge
failure* ...". The oracle is one function on four disjoint parts (Section I.1, page 131) and
`dg(y)` is the first `8b` bits of the answer (Protocol 6.5, Notation, page 57). The definition has
no restriction on the kind of the two inputs: leaf against leaf (different salts are different
inputs), leaf against node, node against challenge input, stream point against anything, inputs of
different oracles, rounds or proofs. The proof charges it without restriction too: the event `F`
includes "`dg(y)` equals the digest of a recorded answer of db", any recorded answer, which is the
`T / 2^(8b)` share, the `+ 1` of `c'`; the closing paragraph says "T bounds collisions" and names
[CMS19] Lemma 6.11, which on its rendered page 33 is `I(P_col, t) < t / 2^lambda` for the plain
collision property. **The draft's claim is right.**

Under our framing:

- *Tags, salts.* The collision of Proposition D.2 is between the two walks' inputs at the same
  height, so both are leaf inputs or both are node inputs: the same part, the same function, in
  every build (Keccak tags in A; SHA-256 leaf and `IV'` compression in B; the two BLAKE3
  `derive_key` contexts). Part separation is not even used by D.2; it is used by the extractor
  (MA-1, MA-2, MA-2', unchanged and not refereed here).
- *Caps.* Both systems fold a cap pairwise with ordinary node hashes (A: `verify_merkle_cap`,
  80-byte node inputs; B: `fold_to_root`). No oracle input carries more than two child digests,
  so the count "at most `max(2, c)` digests" in the proof of Lemma I.12 stands. See finding m-2 for
  the lazily hashed cap of A.
- *A tree of 20,000 proofs.* One database for the whole execution; `B` contains a collision
  between inputs of different proofs. The tree accounting sums per-proof errors that each contain
  the collision share, which over-counts and is safe.
- *Digest length.* A's digest is two 128-bit cells and its root item two cells with the other two
  asserted zero; B's is 32 bytes. `b = 32` for both.

## 3. Attack 2: arguing from the verifier's queries after the output

The paper's own proof does exactly this. Protocol I.9 step 4 (page 138) appends the verifier's
queries after the adversary's output and step 5 measures the database after them; the proof of
Theorem I.16 (pages 142 to 143) works in the simulated oracle game, in which the measured database
agrees with the output tuple (the paper says why it uses that game: "Lemma I.14 needs the
algorithm's actual output"), and Lemma I.14 reasons classically about that database: "Since db has
no digest collision, each recorded digest has a unique preimage. So the leaf at every position that
pf opens is the opened leaf." The draft's step 5 inserts its change at that sentence and nowhere
else. Checked for a hidden use of "one leaf a position":

- The extracted string `tr` is defined from the database alone ("the leaf that the database
  extractor reconstructs from db, or the default"; Protocol I.9 step 6: "a missing or ambiguous
  preimage leaves the leaf undefined"). It does not read the proof's openings, so two records
  cannot make it ambiguous.
- Lemma I.12 does not read the proof. Lemma I.15 needs only the number `k` of oracle inputs of a
  tuple and that the empty database is outside `B`.
- `k_q` (Definition I.1, page 130: "at most `1 + floor(log2(2 max(1, l_max)))` Merkle queries per
  opened position") enters only as that `k`. With one path a record the count is per record
  (finding m-1).
- Definition I.13's second condition names "the verifier"; with `V'` it is a different set of
  tuples of the same form. Nothing else in Section I.3 refers to it.

No hidden use found. The adapted step is legitimate where the draft puts it.

## 4. Attack 3: one value in one check, another in another

Outside `B`, every record authenticated at leaf `q` of a tree with root `rt` has the leaf input
the extractor reconstructs at `q`, so all the values the decision reads at that leaf are one
value. An attack needs a record that is used without being authenticated at the drawn position,
or a value that enters the decision from somewhere other than an authenticated record. Tried
against the code:

- **System A, flag walk** (`wi_queries`). A first-flagged query hints its row once; the same row
  cells are hashed (`keccak_cells`), walked (`walk_path` by `query_win_ptrs[k]`) and folded at
  `x = positions[k] + COORD_BASIS[depth]`; at the last level the check `P*(x) = column + c fold`
  is on the same cells. Position cell and windows of query `k` are written together by
  `decode_query_windows` from one stream word whose windows must rebuild the word, so the path's
  order bits are the position's bits, cap bits included. "As before" requires `0 <= j < k` in the
  exponent, mark 1 on record `j`, `positions[j] == positions[k]` (whole cells, the level's own
  array), and copies the fold. The fold depends on the row, the position and level-wide values
  only; the windows enter the walk only. Records are per level, so a position of one level cannot
  be served by another level's record. Two first flags at one position are two authenticated
  records: equal outside `B`. **No split is possible.**
- **System A, `open_stacked`**: one row a drawn query, each with its own windows and position
  (`opening_query` call sites). Same conclusion.
- **System B** (section 5): each query's leaf feeds its own fold, its own coset select and its own
  terminal check from the same wires that are hashed. Two different drawn indices that share a
  leaf of a later round tree (the common case after the fold shifts) carry two records of that
  leaf, uncompared: equal outside `B`.

The attack fails in both systems for the reason the draft gives.

## 5. Attack 6: system B's in-circuit verifier, audited (D-2)

At `0f84f74`:

- The root is an input digest absorbed by the challenger (`recv_salted_merkle_commitment`).
- The index is drawn in circuit and masked by a gate (`sample_bits`); each tree uses
  `index >> shift` (`open_queries`: `log_lift`; `reduce_queries`: the coset size; `reduce_all`
  shifts by the arity each round).
- `verify_opening` / `verify_opening_2x`: the leaf wires are hashed; at level `k` the pair is
  ordered by bit `k` of **that query's own index wire**; the digest reached must equal the layer
  entry selected by **that index's** upper bits (`multi_wire_multiplex`); `verify_layer` folds the
  layer to `commitment.root`.
- With query groups (`defer_queries`, `GroupedSlot::new`): the residue asserts a fresh wire equal
  to each drawn index; `Link` makes that private word of the residue *be* inout word `j` of group
  `g` (index substitution in `Layout`, not a copied value); the cap layers are shared words that
  are the residue's layer wires, which the residue folds to the absorbed root
  (`recv_openings_deferred`). A link list with a repeated residue word is refused by assertion.

**Each slot's path is walked by its own drawn index into the absorbed root. D-2 holds for B.**
The native verifier carries one opening a distinct position (`first_occurrences`): [SG26]'s `V`.

## 6. Attacks 4 and 5

**Zero knowledge.** "A repeated record reuses the same salt" is honest-prover behaviour; nothing
enforces it directly. It does not need enforcing: zero knowledge is a statement about the honest
prover, whose multi-opening advice is a deterministic function of its de-duplicated proof
(Proposition D.Z is correct), and both wire formats are de-duplicated. For a cheating prover, a
different salt at the same position is a different leaf input and falls under Proposition D.2.
No finding.

**Numbers.** Recomputed: collision term `N 6 T^3 / 2^256 = 1/2` at `log2 T = 79.376`; at
`T = 2^64` it is `2^-47.13`; hash term 75.63344 (A, `c' = 2,397`) and 75.63264 (B, 2,401); with
`c' + 1`, 75.63324 and 75.63243; loss 0.00020 bits; classical `t = 1`: `2^-210.74`, `2^-211.22`.
All agree with the draft's table (79.38, `2^-47.1`, 0.0002). The figures are in `T = t + k_q`.

## 7. Findings

| # | Class | Finding | Fix (buildable) |
|---|---|---|---|
| m-1 | MINOR | **D-4 is not met literally by B's query groups.** `defer_queries` pads the index list to a multiple of the group's `unit` by repeating the last index, and every padded slot verifies an opening in each tree. So `V'` checks up to `unit - 1` records more than drawn queries per tree, and `k'_q` exceeds the calculator's `k_q` by at most `(unit - 1) x trees x (1 + path)` hash queries when `unit` does not divide the query count (192, 174, 111, 82 with groups of five). Soundness of Theorem D is untouched (it is stated in `k'_q`); only the sentence `k'_q <= k_q` fails. Under the "every t" convention the query counts are solved at each row's `k_q`, so the count must be right. | Restate D-4 as "`k'_q` counts every record checked"; in the calculator take `q_iop` for an in-circuit B row as the query count rounded up to the group unit (or fix the unit to divide the count); re-run the affected rows. |
| m-2 | MINOR | **D-2's cap clause is under-stated for A.** A's cap is hashed lazily: `verify_merkle_cap` hashes only flagged nodes, so an unflagged node's hinted digest is unconstrained. Proposition D.2's "the cap's own hashes to the root are common to both walks" needs every cap entry a walk lands on to be linked to the root by hashes the verifier evaluates. It is, as built: `walk_path` writes flag 1 at the parent of the reached entry, an unflagged node pins its children's flags to 0, the root is always hashed, and all records of a level use the one hinted cap. | Add that sentence to D-2 and the cap argument to section 3 of the draft; no code change. |
| m-3 | MINOR | **"Position" must be said to be the Merkle leaf index of each tree.** In B a leaf holds a coset and each tree sees the drawn index shifted; distinct drawn indices routinely share a leaf of a later tree. Sections 1 and 3 of the draft speak of `p_j = p_k` as if repetition came only from repeated draws. The proof covers the general case (it is per record and per tree) but D-3 and the notation should say so. | Reword section 1 and D-3: per tree, position = leaf index after that tree's shift. |
| m-4 | MINOR | **Source note and B's audit line are stale.** The draft says the renderer is not installed and that B's D-2 is "taken from documents, not audited". | Replace by: formulas compared with the rendered pages (this report, section 1), no discrepancy found; B's D-2 audited at `0f84f74` (section 5). B's builder still records the one line in `yugen-proof-b2/docs/parameters.md`, with the padded slots of m-1. |
| n-1 | NOTE | Every formula the draft quotes matches the rendered pages: Lemma I.12's bound, Theorem I.16 (1) and (2), Lemma I.15 (1) and (2), Definition I.1's `k_q` (floor brackets present), `c'`, [CMS19] Lemmas 4.9, 5.7, 5.9, 5.10, 6.11. The text-layer defect did not corrupt anything used. |
| n-2 | NOTE | Recursion: Theorem D bounds an adversary that outputs the advice. Inside a tree nobody runs the inner verifier's hash queries in the real game; the extraction of inner advice and the appended queries of 20,000 inner verifiers belong to the tree accounting (`soundness-method.md` 8.5b, O-13). This is the same for a de-duplicating in-circuit verifier, so it gives no reason for a table; it is not settled by this lemma. |
| n-3 | NOTE | Theorem I.17 (weak online simulation extractability) is not re-proved for `V'`; page 143 shows it uses the same Lemma I.14 plus one collision case. Not used by present claims. |
| n-4 | NOTE | Theorem D is not machine-checked; [SG26]'s statements are reported as machine-checked by its authors. Keep the label "Adapted, reviewed by the referee, not machine-checked" in `REFERENCES.md` O-70. |

## 8. Not checked

- The modelling assumptions MA-1, MA-2, MA-2', obligations K-A and K-B, and whether [SG26]'s
  extractor "adapted to" our tree shapes is written anywhere as an algorithm.
- [SG26]'s own proofs beyond the pages listed (Lemmas I.10, I.11, Definition H.3 to Lemma H.5 were
  not re-read), and its machine-checked development.
- The uncommitted edits in `yugen-proof-a` and `yugen-proof-b2`; B's `merkle-blake3` leaf gadget
  (the climb and the layer check are shared code and were read); A's `open_stacked` beyond its
  call sites; both native verifiers beyond B's `recv_openings`.
- The tests W-7 were not run; no test was run.
- The count of the terminal codeword's tree and of caps inside `k_q` (same for `V` and `V'`).
- Recursion in the QROM (n-2).
