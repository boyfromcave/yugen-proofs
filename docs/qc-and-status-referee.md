# Referee report: Lemma QC, Theorem TE' (revision 2) and `what-is-proven.md`

Part of Yugen. `yugen-proofs` at `073832a`. 2026-11-19. Independent referee: did not write
`lemma-tree-extraction.md`, Lemma QC, `tree-extraction-referee.md` or `what-is-proven.md`. Findings are the Ycash
developers' (2026), Original, first recorded here, unreviewed.

**Sources, as read for this report** (page images rendered with pypdfium2 from the lead architect's copies; printed
page numbers):

- [CMS19] A. Chiesa, P. Manohar, N. Spooner, *Succinct Arguments in the Quantum Random Oracle Model*, Cryptology
  ePrint Archive, Paper 2019/834: pages 16 and 17 (Sections 3.5, 3.6, Lemma 3.2, Lemma 3.3; scale 1.8), page 22
  (Definition 5.6, Lemma 5.7, Proposition 5.8, Lemmas 5.9, 5.10, footnote 6; scale 1.6). Appendix A (the proof of
  Lemma 3.2) was **not** read; Lemma 3.2 is used as Published.
- [SG26] C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, Cryptology
  ePrint Archive, Paper 2026/2615 (a preprint): page 142 (Lemma I.15, Theorem I.16 and the first part of its proof;
  scale 1.6). Nothing else of [SG26] was re-read; statements of it quoted in the subject documents are taken as quoted.
- Read-only: `yugen-proof-a` (`guests/bundle_merge_e2.py`, `bundle_sub_e2.py`, `bundle_common_e2.py`,
  `docs/recursion.md` rules BC-1 to BC-5, `docs/parameters.md` 2.5), `yugen-proof-b2` at `543c808` (`src/bundle.rs`,
  `src/params.rs`, `docs/zero-knowledge.md`, `docs/parameters.md`), by search and excerpt, not audited.

## 0. Verdicts

| Subject | Verdict |
|---|---|
| Lemma QC (section 9a) and the coupling of section 9 (ii) | **PASS.** Transcription, both cases, the constant and the additive composition are right. Two wording fixes (Q-2, Q-3), no change to any term. |
| Theorem TE' revision 2 (with TE-X, TE.1 two-sided, TE-Q') | **PASS WITH CONDITIONS** T-1 to T-4 below. The bound is right; one hypothesis is missing (the node count and the termination rest on a concrete-hash digest, T-1), and the reading of "conditional on C2" must be stated as a joint probability (T-2). No figure moves. |
| `what-is-proven.md` as an honest record | **PASS WITH CONDITIONS.** No figure is wrong. Four rows are more optimistic than their evidence (W-1 to W-4, MAJOR); section 6 is resolved in section 4 below. |

No BLOCKER. No query count and no printed figure changes.

## 1. Lemma QC

**Transcription.** The three cases of [CMS19] Lemma 3.2 in section 9a agree with page 17 symbol for symbol, including
`u . ⊥ := 0`, the `2^(-n/2)` on `|D - x>` and the coefficient `1 - (-1)^(u.y) - (-1)^(u.D(x))` with `2^-n`. The
classical query (phase register `H^n|0>`, `O`, `H^n`, measure) is the standard-oracle query of page 16
(`O_h = (I ⊗ H^n) O'_h (I ⊗ H^n)` on answer register 0).

**Case (1), re-derived.** After `O` and `H^n` the state is
`sum_y' |y'> (2^(-n/2)(1 - 2^-n)|D'_y'> + 2^-n |D> - 2^(-3n/2) sum_(y != y') |D'_y>)`; squared norm of each bracket
`2^-n ((1 - 2^-n)^2 + 2^-n + 2^-n - 2^-2n) = 2^-n`. Exactly uniform; recorded with probability `(1 - 2^-n)^2` for every
`y'`. Agrees.

**Case (2), re-derived.** `|delta_u>` is `|phi_u> - (-1)^(u.y_0)|D>`, written on the orthonormal vectors `|D - x>`,
`|D - x + [x -> y]>` (the vector `|D>` is the member `y = y_0`; the document's decomposition handles this correctly
because `delta_u` is expanded on that basis only). `||delta_u||^2 = 2^-n + 2^-2n sum_y c_(u,y)^2`. Exact values: if
`(-1)^(u.y_0) = 1` then `c^2 = 1` for every `y`, total `2 / 2^n`; if it is `-1` then `c` is 1 or 3 on half the `y`
each (`u != 0`), total `6 / 2^n`. So `10 / 2^n` holds with room; the failure probability is at most `||Delta||^2`
because the ideal part maps to `|y_0>|D>` exactly and the projector kills it.

**Numerical check (run for this report, own script, floating point, one cell, `n = 1..5`).** The transcribed map is
an isometry on the cell for every `u`; case (1) is uniform and `(1 - 2^-n)^2` to `1e-12`; the worst failure probability
of case (2) is 0.9375, 0.684, 0.414, 0.228, 0.119, that is `3.8 / 2^n` at `n = 5`, against the bound `10 / 2^n`.

**The coupling (9 (ii)).** After each measurement the database is a basis state in product with the rest, so the
lemma applies again with the same hypotheses; conditioned on no DEVIATION a fresh answer is still uniform (the
recording probability does not depend on the answer) and a recorded one is returned. The errors are conditional
probabilities given the past, so they add: at most `2 / 2^n` for a fresh input, `10 / 2^n` for a recorded one, over
`K - k_q,r` queries. `10 (K - k_q,r) / 2^(8(b+e))`: `log2 10 + 29.77 - 256 = -222.91` (A), `-223.09` (B, `2^29.59`),
`-222.20` at 74,940. Reproduced. The continuation's hash term at `t = 2^64`, `29.77 + 11.23 + 64 - 256 = -151.0`:
reproduced. The capacity is never reached: before the `j`-th continuation query the database has at most
`t + k_q,r + j - 1 < t + K` entries.

**Findings.**

- **Q-1 (NOTE).** The constant 10 is loose (6 analytically, about 3.8 measured). Keep 10; say it is not tight.
- **Q-2 (MINOR), section 9, Proposition TE-Q'.** The event bounded is "FAIL", but `E_T^Q` has a fourth outcome,
  DEVIATION, which is neither a compliant tree nor a C2-VIOLATION. *Fix:* state the left side as
  `Pr[Vrf_r accepts and E_T^Q ends with FAIL or DEVIATION]`; the right side is unchanged (coupling:
  `Pr_Q[FAIL or DEVIATION] <= Pr_L[FAIL] + Pr[DEVIATION]`).
- **Q-3 (MINOR), the capacity remark.** True, but the stated reason ("Lemma 3.2 depends on the capacity only through
  the full case") is half of the argument. [CMS19] Lemmas 5.9, 5.10 (page 22) are stated with one `t` for the query
  count and the database bound (`P_t` projects on `|D| <= t`), so used as black boxes at capacity `t + K` they would
  give `6 T^2 I(B*, T)`, not `6 T_0^2 I(B*, T_0)`. *Fix (one sentence):* the database state of page 16,
  `|D_t> = |x_1, y_1, ..> ⊗ |⊥, 0^n>^(t - |D|)`, embeds capacity `T_0` in capacity `T` by padding; with at most `T_0`
  queries neither oracle is ever applied to a full database, and off the full case the two act identically (Lemma 3.2,
  cases 2 and 3 do not mention `t`), so the state before the measurement is the padded image and the measured
  database has the same distribution. Then Lemma I.15 (2) is applied at capacity `T_0`.
- **Q-4 (NOTE).** [CMS19] Appendix A remains unread; Lemma QC is as sound as Lemma 3.2 as printed.

## 2. Theorem TE' revision 2

**What holds.** Steps (1) to (3) of section 6 are right with the stop at C2-VIOLATION: a FAIL at `v` implies a
recorded accepting native run, hence (Lemma TE.2) the table is in `B*` at that step; the two-sided Lemma TE.1 gives
the per-entry bound in the one direction used, and is the quantity [CMS19] Definition 5.6 asks for. Monotonicity is
no longer used anywhere.

- **T-1 (MAJOR). The node count and the termination rest on an unstated hypothesis; H-BIND is mis-modelled.**
  *Location:* section 3 ("the tree's shape bounds the reached nodes by `N` (the node circuits check the shape)"),
  the statement of Theorem TE' ("at most `N`", `K <= N k_q,max`), section 2 (H-BIND "only for Corollary TE-S",
  "modelled as a further random-oracle part"). *What the builds provide (read, not audited):* both systems put the
  depth, the child count and the proof count in the statement digest
  `H_bundle-node(depth | mode | LE16(count) | content | attr | LE32(proofs))`; a merge has depth `1 + max` of its
  children's and refuses a child of depth 3 (A: `bundle_merge_e2.py`, rules BC-3, BC-4; B: `src/bundle.rs`,
  `depth_bound`, `depth_max`); `proofs = 1 + sum proofs_c`; the bound `MAX_TREE_PROOFS` is checked natively on the
  root's count (`Tree::check`), in no circuit (BC-5). So condition C-4 is met by design in both builds, **through
  the digest only**: a child's depth and count are advice "bound only through the recomputed `D_c`". The extracted
  witness of a child is therefore tied to the cells its parent claimed only if the concrete statement-digest function
  has no collision among the extracted values. Without that, an extracted tree may exceed `N` nodes or fail to
  descend, and `K` is not bounded. Shape alone (depth 3, arity 16) allows 69,905 nodes, which is why the count cell
  matters. That digest is computed **inside the fixed relation** by the concrete hash, so it cannot be "a further
  part of `H`": section 2's own second place of C2 says the relation must not read the oracle. *Fix:* (i) `E_T`
  stops with a third named outcome, **SHAPE-VIOLATION**, when an extracted child's cells contradict its parent's
  (depth not lower, count or proof count different) or when more than `N` nodes are reached; Theorem TE' bounds
  "neither compliant, nor C2-VIOLATION, nor SHAPE-VIOLATION", with `K <= N k_q,max` then unconditional; (ii) H-BIND
  is restated as **collision resistance of the concrete statement-digest functions** (a standard-model assumption on
  SHAKE256 / Keccak-256 at 256 bits, generic cost `2^128` classical; the quantum generic cost is of order `2^85`,
  from memory, not in the folder), which excludes SHAPE-VIOLATION and gives `eps_bind`; the `T^2 / 2^(8b+1)` figure is
  dropped or labelled heuristic; (iii) Proposition TE-Q' and every tree row carry it. No figure moves.
- **T-2 (MINOR). What "outside that event" lets a reader conclude.** Theorem TE' is a true statement about a joint
  probability: `Pr[accepted, no compliant tree] <= bound + Pr[accepted and C2-VIOLATION]`. The last term is not
  bounded by anything, and in the model it is not small: for the **honest** tree (inner proofs made with the concrete
  hash, root against `H`) it is essentially 1. So a reader **may** conclude: the root proof alone is knowledge sound;
  every way of cheating that does not pass through a child the native verifier rejects is bounded; the tree is sound
  to the stated level if the event is empty, which in the deployed system (`H` is the concrete hash) is verifier
  equivalence. A reader **may not** conclude: that a random-oracle proof of the recursion tree exists with a small
  gap; that `Pr[C2-VIOLATION]` is small in the model; that passing equivalence tests "discharges" C2 (they make the
  event empty where there is no theorem, not where the theorem is). Corollary TE-S's "conditional on C2" must be
  displayed as `Pr[a published leaf statement is false and no C2-VIOLATION (and no SHAPE-VIOLATION)] <= ...`, never
  as a conditional probability: the conditioning event can have probability near 0. *Fix:* that display, and the
  three "may not" sentences, in section 6 and on the status page.
- **T-3 (MINOR). Corollary TE-X.** Correct classically as stated (same table, same sum, `K` over all published
  proofs). Two things to say: (a) its content is knowledge soundness of a **batch** of published proofs on one
  table; the children an extracted node witness lists are concrete-hash proofs, are not the published ones and are
  not used, so "tree" adds only the statement binding, which is T-1's assumption again; (b) the quantum version
  ("one verifier with `K` queries before the measurement") is asserted in one sentence in section 9 and in the
  earlier report, with no statement. It is right as far as checked; *fix:* state it: under (K), H-DS and the proof
  of [SG26] Theorem I.16 (1) run with `B*` (Lemmas TE.1, TE.2 in place of I.12, I.14), the error is at most
  `2 sqrt(K / 2^n) + 6 (t + K)^2 (eps_max + c'_max (t + K) / 2^(8b))`. It is the proof of I.16 (1) re-run with a
  joint bad set, not the theorem as a black box; label it "sketched" until written.
- **T-4 (MINOR). H-DS against `qrom-compilation.md` section 2.** *Assumed:* jointly injective encodings over all
  systems on one oracle, and a recorded challenge input decoding to one system. *Provided:* between A and B, a
  different part-tag byte (`0x10..0x13` against `0x20..0x23`), a different 16-byte label and different functions
  (2.2); sufficient. **Within** a system the label is the same for every proof system of the tree (A's rows 6 to 9,
  B's leaf and node), so the system is determined only by `pre(x)`: for A the row number and
  `bind_iv(IV(program))` (2.8 A-3; `yugen-proof-a/docs/parameters.md` 2.5), for B the `StatementId` (circuit name,
  constraint-system digest, mode, row; B-1). That suffices **if** the IV and the constraint-system digest determine
  the program, a concrete-digest binding of the same kind as T-1. Nothing separates levels or proofs in the
  transcript except the statement and the salt; [SG26] needs no more, and the lemma uses the level only for
  termination (T-1). *Fix:* H-DS's sentence "each statement carries its system's verifying-key or circuit digest"
  cites these two fields and names the binding assumption; task T-1 item 10 checks that A's unframed Keccak-256
  statement wrappers (BC-5) and every other in-relation use of Keccak-256 / SHAKE256 cannot produce an input that
  begins with a part tag (not checked here).
- **T-5 (NOTE).** B's node rules have switches (`depth_bound`, `depth_max`: "off: always 1") for negative tests; the
  consensus constraint-system digest must be that of the all-on rule set, pinned in a test.

## 3. `what-is-proven.md`: rows against their evidence

- **W-1 (MAJOR). T-a, T-b, T-d, T-j say "proven" while resting on K-A, K-B, which are owed.** By the page's own
  definition this is "conditional" (S-8, with the same dependence, is so marked). *Fix:* "conditional (the
  implication is proven; K-A, K-B owed; T-1; the statement-digest binding of T-1 above)". After this report the
  Refereed column of T-a, T-b, T-h, T-i reads "`qc-and-status-referee.md`: pass with conditions / pass".
- **W-2 (MAJOR). Z-2, Z-3, Z-4 omit a hypothesis that system B as built does not meet.** `zk-quantum.md` 3.1 and
  5.1: "the published theorem does not apply to B as built, whose four fold trees are unsalted"; the figure
  `2^-105.7` counts those trees as salted. `yugen-proof-b2/docs/parameters.md`: "Not built: salts on the four fold
  trees". *Fix:* add to "Conditional on": route S (fold trees salted, not built) or route F with Z-B6; the spBCS
  transcript with the proof salt (T-1); the category-1 row's 512-bit leaf salts (present: `CAT1_SALT_BITS`; the
  default row is 256 bits, where Z-1 applies); MA-2' for B's BLAKE3 leaves.
- **W-3 (MAJOR). S-1 and S-2 say "knowledge sound, proven".** For Theorem S0 the knowledge form is a three-line
  remark (`whir-additive-soundness.md` section 5, "Knowledge"), against [CMS19] Definition 8.5, not [SG26]
  Definition 2.20 which hypothesis (K) needs; the referee (`qrom-zk-referee.md` 3.1) examined soundness and called
  it "a careful sketch", with the prover-side meaning of the fold scalars and the lane order open. *Fix:* split each
  row: soundness as now; knowledge form "stated, not refereed, to be restated against Definition 2.20", listed under
  K-A.
- **W-4 (MAJOR). S-3 and S-7 say "conditional (the soundness form)", which by the page's definition asserts a
  written proof.** For A the base prover's rounds are an uncounted allowance (`OTHER_ROUNDS = 512`, marked E in
  `rev9-and-lean-referee.md`) and several mask counts are estimates (`soundness-method.md` 8.5c); for B the mask
  round's count is "unconfirmed against the Blueprint" (`binius-extension-challenges.md` R-7). *Fix:* "stated;
  degree bounds by Schwartz–Zippel with about 100 bits of room at 256-bit challenges; round census estimated until
  T-1; not refereed as a whole".
- **W-5 (MINOR).** T-c and section 5's H-BIND row: restate per T-1 (collision resistance of a concrete digest; it also
  carries the node count of T-a).
- **W-6 (MINOR).** The page nowhere says what T-2 above says. Add the "may / may not conclude" sentences under the
  tree table.
- **W-7 (NOTE).** T-1 (the builders' task) is partly delivered for B (`yugen-proof-b2` `543c808`); the page may be
  stale there. S-10's "6 of 20 / 14 / 4 of 4" was not recomputed.
- Rows found to match their evidence: S-4, S-5, S-6, S-8, S-9, T-e, T-f, T-g, T-h, T-i (now refereed), J-1, Z-1,
  Z-5, Z-6, Z-7, Z-8 (Z-5 to Z-7 as "proven in the document", unrefereed).

## 4. Section 6 of the page, resolved

| Item | Referee report | The claim | What leans on it |
|---|---|---|---|
| Theorem S (`zk-wi-soundness.md`) | **none.** `guest-masked-referee.md` declares it out of scope; `rev9-and-lean-referee.md` only re-implements its layout. Indirect: Theorem S0 (the same argument without masks) holds as a sketch | W-I, the masked opening, with its blinding and gadget (Lemma 6, section 6.3), is round-by-round sound and knowledge sound in unique decoding | soundness of **every system-A leaf proof** (row 8 is the one consensus leaf row), and (K) for A's openings |
| A's rounds outside the openings (S-3) | **none** (`zk-system-a-gaps.md` appears in no report) | each added round's error in units of `1/q`; the base rounds as an allowance | soundness of every A proof (large numeric room; the risk is a missing round or a wrong state function); K-A, hence every tree figure |
| B's rounds outside the openings (S-7) | **partial.** `johnson-row-referee.md` and `-2`: ring switch (J1) and Theorem 1's use hold, figures reproduced; Lemma K (knowledge of the opening) holds under its hypotheses. No report on `binius-extension-challenges.md` as a whole | the counted round list of one Binius64 proof | soundness of every B proof; K-B |
| `zk-quantum.md` revision 2 (Z-2, Z-3, Z-4) | **none for revision 2.** `qrom-zk-referee.md` read revision 1, recommended this route (its section 4 (ii)) and computed matching figures (`2^-105` a proof, about `2^-85` a wallet). Theorem ZP (Original) is unread; hypothesis N was looked at in `b-batching-and-hash-referee.md` and `security-profile-referee.md` | everlasting zero knowledge for `Q` proofs ([SG26] 6.6 (3)), the two-system and node composition, witness indistinguishability (6.6 (4)) | the whole privacy statement, which is conditional on `eps_hvzk` in any case |
| `zk-masked-sumcheck.md` | **none** | perfect HVZK of the masked sumcheck in characteristic 2 | `eps_hvzk` of both systems |
| `zk-hiding-commitment.md` | **none** (the guest report takes the construction as given) | W-I hides the committed rows | `eps_hvzk^A` |
| `zk-composition.md` | **none** | a leaf proof's parts compose to HVZK; number withdrawn | it is where `eps_hvzk` (Z-A6) is to come from: until then no privacy figure is complete |
| B's guest, in-circuit / native equivalence | **no report on the guest as a whole.** Partial: `lemma-d-referee.md` (the multi-opening verifier `V'`, pass with conditions), `b-batching-and-hash-referee.md` (the batching step, native and in circuit, pass with conditions) | the in-circuit verifier accepts exactly what the native one does | C2's engineering side for every B tree claim |

**Referee queue, by how much rests on each.** (1) Theorem S; (2) A's rounds outside the openings together with K-A;
(3) B's guest equivalence; (4) B's rounds outside the openings together with K-B; (5) `zk-composition.md` with
`zk-hiding-commitment.md` and `zk-masked-sumcheck.md`, as one read, since together they are `eps_hvzk`;
(6) `zk-quantum.md` revision 2 (published theorem, route already recommended by a referee; Theorem ZP is the new part).

## 5. Claims of the project that are not on the page

The page covers "a witness for the relation exists and is hidden". It does not say that the relation means what the
specification says, nor what the public data hide. Each of the following belongs on a sibling page (statement and
protocol layer), with one line here that states the boundary:

| Claim | Belongs |
|---|---|
| Falcon verification in the leaf statement (both systems accept exactly valid signatures; A / B statement equivalence) | sibling page; it is a soundness dependency of the pool, so a pointer row here |
| The hidden salted key hash (hiding and binding of the key commitment) | sibling page; also a zero-knowledge dependency: Theorem ZP hides the witness, not what the public inputs reveal |
| Note encryption and the ML-KEM binding | sibling page; outside both proof systems |
| The private-retrieval scheme | sibling page (`yugen-pir`); outside both proof systems |
| Turnstile and pause mechanisms | sibling page (consensus rules); a pointer row here, since they are the fallback if a soundness row fails |

## 6. Not checked

[CMS19] Appendix A and the proofs of Lemmas 5.9, 5.10; [SG26] beyond page 142 (Protocol I.9, Lemmas I.10 to I.14,
Definitions I.1, I.13, 2.20 as quoted by the subject); the node circuits beyond search and excerpt (no constraint was
traced; `Tree::check` not read); A's statement wrappers against the part tags; the calculator (not run; figures
checked by hand only where shown); S-10's row counts; Theorems S, ZP and the zero-knowledge documents themselves
(their referee status was established, their content was not refereed); the Johnson-row documents; no test suite
was run. The numerical check of Lemma QC is a scratch script, not committed.
