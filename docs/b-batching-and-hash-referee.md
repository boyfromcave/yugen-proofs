# Referee report: parallel batching (Lemma P, P-sh) and the transcript hash of system B

Part of Yugen. Independent referee, 2026-11-19. Subject: commit `4fa2cb1`,
`docs/decision-b-parallel-batching.md` and `docs/decision-b-transcript-hash.md` (both drafts),
and, at the lead agent's request, the BLAKE3 Merkle use already in force
(`docs/decision-b-merkle-hash.md`). Builder's side read at `yugen-proof-b2` `0f84f74`
(`src/batch.rs`, `src/node.rs`, `docs/parameters.md` 15.7, the vendored BLAKE3 Merkle gadgets and
`binius_hash::blake3`), read-only.

## 0. Verdicts

| Subject | Verdict |
|---|---|
| Lemma P (and Lemma R, on which the corollary rests) | **PASS**, two minor corrections to the statement (L-1, L-2) |
| The P-sh design as specified in the record (U-1 to U-4) | **PASS WITH CONDITIONS** C-1 to C-8 and tests RT-1 to RT-6 (section 6) |
| The transcript-hash recommendation (keep SHA-256 keys and SHAKE256 streams; (c\*) as the fallback, not (c)) | **PASS WITH CONDITIONS**: the wording of T-3 must be corrected (H-1, MINOR); the recommendation itself stands |
| The existing BLAKE3 Merkle use (`derive_key` leaves and nodes, 32-byte outputs) | **PASS**: not affected by the full-output point (H-3); one citation note |

No BLOCKER and no MAJOR finding. Findings: 7 MINOR, 8 NOTE.

## 1. How the sources were read

- Sharp and Grubbs, "Faster and Smaller Anonymous Credentials from Standardized Signatures",
  ePrint 2026/2615 [SG26]: Definitions 2.23, 2.24, 2.26, Lemma 2.27 (pages 15 to 17), Lemma 5.2
  and its proof (page 37), read from **rendered pages** (the repository's `.tools-venv`,
  `pypdfium2`, images in a scratch directory outside every repository, deleted afterwards).
- O'Connor, Aumasson, Neves, Wilcox-O'Hearn, "BLAKE3: one function, fast everywhere"
  (`blake3-spec.pdf`) [B3]: Sections 2.6 (page 8), 4.1, 4.2 (page 12), 4.3 (pages 12 and 13),
  read from rendered pages.
- The record's paraphrase of Definition 2.24 (a) (i), (ii), of Lemma 2.27 (2)(a) and of Lemma
  5.2 matches the rendered text. Every [B3] passage the hash record quotes in T-2 and T-3 matches
  the rendered text word for word.
- Not read: Theorem 6.6 and Appendix I of [SG26] (taken through `qrom-compilation.md`); the
  papers [B3] cites for bound (2) (Daemen, Mennink, Van Assche; Luykx, Mennink, Neves); the two
  papers the hash record itself marks "from memory".

## 2. Lemma P and Lemma R

### 2.1 Lemma P holds (PASS)

Definition 2.24 (a), rendered: a state function takes the statement, the oracle input, a round
`i` and the transcript of `past(i)` followed by `a_i`, or by `a_i` and `theta_i`; (i) every
full transcript from a false input to a true output has a round where the state is 0 before
the challenge and 1 after it; (ii) at every round, from state 0 after the prover's message, the
challenge makes the state 1 with probability at most `eps_i`.

The record's state for the parallel protocol ("every false group has moved at some round up to
here") is a function of the statement and of the transcript prefix only, so it is a state
function in that sense: **a doomed set is defined for the parallel protocol** (the prefixes at
which some false group has not yet moved). Checked, step by step:

- (i): with all outputs true, each false group has a first move by its own (i); at the largest
  of those rounds the composite state is 0 before the challenge and 1 after. Correct.
- (ii): at a doomed prefix some false group `g0` has not moved; the composite state can become
  1 only if `g0` moves now; `g0`'s own (ii) holds for **every** transcript of `g0`'s past and
  every message, so it holds whatever the other groups sent and however the prover chose
  `g0`'s message from them; the shared challenge is uniform and independent of the prefix.
  Correct. There is no union factor because the event "leave the doomed set" is contained in
  the event "`g0` moves".
- Different groups false in different rounds: a group whose input is true and whose running
  claim the prover later spoils is outside `Bad` and is not constrained by Definition 2.24 (a)
  (its output is then false, which only hurts the prover). A false group that moves and then
  returns to state 0 does not matter either: the composite state is monotone by construction,
  and (i), (ii) ask nothing more. Correct.
- Adaptive choice of where to cheat: every claim element of every group is absorbed before
  `alpha` (`node::batch_all`), so `Bad` is fixed by the statement. The choice of messages after
  earlier shared challenges is covered by (ii)'s quantifier. Under Fiat–Shamir, re-choosing the
  statement is the state-restoration game, bounded through the largest round error, which
  Lemma P leaves unchanged.
- Different lengths: `tau_g` strictly increasing is all the proof uses. End alignment, start
  alignment and any other shape-fixed schedule are covered. A group that has not started
  holds its claim untouched; nothing of another group is ever added to it (section 4).

Exhaustive toy check run for this report (throwaway script, not a test of record): `GF(2^4)`,
two one-variable groups in one shared round, every pair of prover messages, six random
instances, each of "first false", "second false", "both false": at most 2 of the 16 challenges
make every final claim true, which is `2 / |F|`, the larger of the two groups' errors.

### 2.2 Findings on the statement

| # | Class | Finding | Fix |
|---|---|---|---|
| L-1 | MINOR | **A group that sends but takes no challenge is not in the statement.** Lemma P requires every active group's challenge set to be the one set `C`. In P-sh's last round a one-set group sends `s` and takes no `mu`; Definition 2.23 gives every round a challenge. | Add to the statement: a group may take part in a global round with a one-element challenge set (it ignores `theta_j`), with the error its own state function has there. Lemma R gives 0 for that round (from `D_n != 0` the output is false with certainty), so the proof's sentence "if `g0` is not active ... that cannot happen" extends unchanged. |
| L-2 | MINOR | **Rejection is not in the output map.** Lemma R's state "after `mu`" reads "the final check passed and the outgoing claim is true"; Definition 2.24 speaks only of `out(x, tr)` being in the target relation. | State the convention once: a transcript whose final check fails has an output outside the target relation. The same for the one-set case. |
| L-3 | NOTE | Lemma R is correct as coded: `powers(alpha, K)` gives a polynomial of degree at most `K - 1` in `alpha`; `c1 = claim + c2` makes `p(0) + p(1) = claim` an identity in characteristic 2; the true round polynomial has degree at most 2 (a product of two multilinear forms); the final check with prover-supplied `s_o` and the skipped `mu` at one set are as the proof says. | — |
| L-4 | NOTE | **Novelty.** The lemma is short and of the kind commonly used without proof (batched sumchecks sharing their challenges); I did not search the literature beyond what the record lists. "Original as far as checked" is the right label; "Original" without the qualifier would not be. | Keep the qualified label. |
| L-5 | NOTE | Lemma P gives round-by-round **soundness** (Definition 2.24 (a)). What Theorem 6.6 (2) consumes is the node IOP's round-by-round knowledge error after composition; the record defers that to obligation K-B ("no witness of its own"). Not re-derived here. | K-B's text should name Lemma P where it names the batching rounds. |

## 3. The final step and the error terms

- **No random linear combination across groups exists in P-sh**, and none is needed: each
  group keeps its own running claim, makes its own final check and exports its own claim.
  Inside a group the combinations are `alpha` over the `K` claims and `mu` over the sets.
- `alpha`: `(K - 1) / |F|`, `K <= 16` (`bundle::BUNDLE_LEAVES_MAX = 16`, the node's capacity):
  `256 - log2(15) = 252.09` bits. Right, provided the challenge is a uniform element of the
  whole 256-bit field. As built the challenge is 32 stream bytes deserialised as a field
  element; a binary field of `2^256` elements has no invalid pattern, so this is a bijection
  (the 256-bit type's deserialiser was not traced line by line: N-1). In the default 128-bit
  build the same count gives 124.09; the record's rows are category 1 rows and say so.
- A sumcheck round `2 / |F|`: 255.00. `mu`: `(3 - 1) / |F|`: 255.00. Right.
- Sums recomputed from the group shapes (level 0: four groups, one wiring and three wrapper,
  `sum n_g = 173`; each level adds one wiring group of 78 variables):
  P-seq level 3: `15*7 + 2*407 + 2*3 = 925`, 246.15 bits; level 0: 412, 247.31;
  P-sh level 3: `15 + 156 + 2 = 173`, 248.57; P-rlc-pad `alpha` over 112 claims: 249.21;
  P-ind 4, 5, 7 groups: 253.00, 252.68, 252.19 and `alpha` 250.09, 249.29. All as the record has.

## 4. The forging variant (PB-3) and its relatives

**Reproduced on paper.** Running claim `C` true before round `j_h - 1`; group `h` false by
`e`, `delta = beta_h e`. The prover sends `q + delta`, `q` the true round polynomial. In
characteristic 2 `(q + delta)(0) + (q + delta)(1) = q(0) + q(1)`, so the round check passes and
the claim becomes `q(r) + delta`. The verifier adds `beta_h V_h = beta_h T_h + delta`; the two
`delta` cancel and the claim is the true combined partial sum. The attack needs one round
before the join and a coefficient known before that round's message. In odd characteristic the
zero-sum polynomials are multiples of `(1 - 2X)` and `X^2 - X`, whose value at `r` the prover
cannot fix in advance, so the finding is specific to characteristic 2, as stated.

**Reproduced numerically** (throwaway script, `GF(2^8)`, groups of 2 and 1 variables): the
late-join form is forged in 2,000 of 2,000 runs. The same constant shift against P-sh
(separate running claims, shared challenge) passes in 8 of 2,000, consistent with a bound of
`2 / 256` a round.

**P-sh has no relative of it.** The attack's mechanism is: a term fixed before round `j` is
added to a running claim after round `j`'s message. In P-sh as specified:

1. every running claim is initialised once, at `alpha`, from claims absorbed before `alpha`;
2. after that a running claim changes only by its own group's round polynomial at the shared
   challenge;
3. no two running claims are ever added, and no coefficient is fixed before the claims it
   multiplies are absorbed (`alpha` after all claims of all groups; `mu` after all `s_(g,o)`).

A constant added to another group's polynomial therefore makes that group's own claim false,
and Lemma P applies with that group in the false set from then on. These three properties are
conditions C-1 to C-3; the protocol text PB-O1 must state them, since Lemma P's guarantee is
for that text and not for the builder's one sentence.

| # | Class | Finding | Fix |
|---|---|---|---|
| F-1 | MINOR | **A second relative for the later combined form.** If the groups are ever combined (P-rlc-pad) with each group's claims weighted by the same powers `alpha^0 .. alpha^(K-1)`, an error `e` in claim `i` of two groups cancels with probability 1 in characteristic 2. The record's count ("one `alpha` over at most 112 claims") implies distinct powers across all claims but does not say so. | State it in the record's P-rlc-pad row; RT-3 guards it. |
| F-2 | NOTE | The record's padded check ("2 of 200 pass") was not reproduced as described: in my padded run the constant shift fails the first round check outright (the combined claim already contains the false term), so nothing reaches the challenge. The conclusion (padding is sound, a standard sumcheck on one polynomial) is unaffected. | PB-T6 should describe the padded attempt exactly. |
| F-3 | NOTE | "Drawing `beta_h` only when `h` joins would also repair it" is right: the join is then an `alpha`-type round of error `1 / |F|`. Not adopted, not examined further. | — |

## 5. Zero knowledge, Fiat–Shamir order, counts

**Zero knowledge (d).** The question as put (masked round polynomials sharing challenges; one
mask a group) does not arise: the batching sumchecks carry **no mask**, and they run only in
node proofs. Checked: `zk-quantum.md` section 4 (hypothesis N: a node witness is a function of
leaf proofs, child node proofs, public inputs and parameters; zero knowledge is required of
leaf proofs only, D-c); `src/batch.rs` head and `Family::of_wiring` / `of_wrapper_segment`
(every claim is an evaluation of a public bit vector at a point taken from a leaf proof's
transcript, the wrapper-segment claims included: `S_o` is the wrapper's constraint matrix,
`lambda` a transcript element). P-sh adds no input to a node witness, so hypothesis N is
untouched. Condition C-8 keeps it so.

**Fiat–Shamir order (e).** Required order, which the record's U-3 gives for the rounds and
which must be extended to the two ends: all claim elements of all groups, then `alpha`; in each
global round the `(c0, c2)` of every active group in the shape's group order, then `r_j`; all
`s_(g,o)` of all groups, then `mu`. A verifier that draws `r_j` before absorbing any one
group's coefficients is forged with probability 1 in that group (the prover fits its polynomial
to the known challenge); PB-T3 detects it and RT-2 makes it a mutation test.

**Counts (f)**, recomputed from the record's inputs:

| Quantity | Record | Recomputed |
|---|---|---|
| Verifier messages, level 3 | 663 to 326 | `663 - 417 + 80 = 326` |
| `N_msg` | 1,326 to 652 | twice the above |
| `c'` at `m = 2` | 2,653 to 1,305 | `2 N_msg + 1`: the same |
| `k_q` | 39,084 to 37,736 | `2 N_msg + 36,432`: the same; `log2` of the ratio 0.0506 |
| Hash term | +0.34 bits | `log2(2,653 / 1,305) = 1.02` on the term; one third of it, 0.34, in `kappa` (the term is cubic in `t`). Right, but the unit is not stated (P-1) |
| Tree sum | `2^22.36` to `2^22.00` | `16,384 * 183 + 3,616 * 664 = 5,399,296` (22.36); with 327: 4,180,704 (22.00) |

| # | Class | Finding | Fix |
|---|---|---|---|
| P-1 | MINOR | "+0.34 bits" for the hash term is in QROM bits (`kappa`), while the neighbouring rows are bits on the term. | Say "1.02 bits on the term, 0.34 in `kappa`". |
| P-2 | NOTE | `180 + 79 L`, 663, 36,432 and "at most 80 at any level" (which needs every level-0 group to have at most 78 variables) are the builder's figures, not recounted from a compiled circuit here. | PB-T7 and PB-O3 cover it. |
| P-3 | NOTE | The record's section 6, first paragraph (the in-circuit transcript's formal place) is a standing question that P-sh neither opens nor closes; I agree. In the random-oracle model the in-circuit Fiat–Shamir bound depends on the largest round error, which is unchanged. | — |

## 6. Conditions on the builder, and tests

**Conditions (P-sh passes only with all of them):**

- **C-1** One running claim a group, initialised at `alpha` and never touched by another group;
  no sum of running claims or of round polynomials across groups anywhere. Any combined form
  is a different protocol and needs its own record.
- **C-2** `alpha` is drawn after every claim element of every group is absorbed; `mu` after
  every `s_(g,o)` of every group.
- **C-3** In each global round every active group's `c0, c2` are absorbed, in the shape's group
  order, before the one challenge is drawn; the linear coefficient stays implicit
  (`c1 = claim + c2` with the group's **own** claim) or the sum check is made explicitly a group.
- **C-4** The schedule (alignment, which groups are active in which round, whether `mu` is
  drawn) is a function of the node's shape only and is bound by the statement identifier.
- **C-5** Every group takes the whole challenge: one uniform element of the 256-bit field; no
  group reads a truncation, a subfield element or a function of the challenge.
- **C-6** Every group's final check is asserted; a group with one set exports its claim with no
  `mu`, as now.
- **C-7** The inner batching transcript gets its own label or context and the proof format
  version changes (the hash record's O-inner; PB-T5).
- **C-8** The batching step stays out of leaf (wallet) proofs. If a batching sumcheck ever
  enters a zero-knowledge proof, the mask question of (d) must be answered first (task Z-N).

**Tests, in addition to PB-T1 to PB-T8 of the record:**

- **RT-1 (the forging variant is refused).** Against the built verifier, native and in
  circuit: a short group with one false claim, every other claim true; in the global round
  before the short group starts, the prover adds the constant that P-rlc-late would need (for
  every choice of weighting the built protocol could be read as using: 1, `alpha^i`) to a
  longer group's `c0`, and is honest elsewhere. The native run is refused and the circuit is
  unsatisfied. Run for each short group and each longer group.
- **RT-2 (order mutation).** With a `Rules` switch that draws `r_j` before the last group's
  coefficients are absorbed, a prover that fits that group's polynomial to `r_j` forges; with
  the built rules the same prover is refused. The same for `mu` drawn before one group's `s`.
- **RT-3 (cross-group cancellation).** The same error added to claim `i` of two groups is
  refused. (It passes trivially for P-sh; it is the regression guard for F-1.)
- **RT-4 (shapes without `mu`, and `K = 1`).** A node shape in which every group has one set
  draws no `mu` and has `n_max + 1` verifier messages; a group with one claim reduces
  correctly under the shared `alpha`.
- **RT-5 (alignment).** A false claim in the shortest group and in the longest group, with the
  prover cheating only in rounds where the other is not yet active, is refused; the exported
  point of each group is the stated suffix (extends PB-T4).
- **RT-6 (PB-T6 sharpened).** The test of record for PB-3 on a small field states the padded
  attempt exactly (F-2) and includes the equal-powers cancellation of F-1.

## 7. The transcript hash

### 7.1 What [B3] says about extended output and the bound (rendered pages 8, 12, 13)

1. Section 2.6: extended output repeats the root compression with an incrementing counter and
   "uses the full output of the compression function"; outputs of different lengths are not
   domain separated, shorter ones are prefixes of longer ones.
2. Section 4.2: returning 16 words with the feed-forward on the second half only "causes the
   BLAKE3 compression function to no longer be indifferentiable", with an explicit inversion
   for an attacker with access to the cipher who knows the chaining input; and "the truncated
   compression function used in every compression except the root nodes is indifferentiable".
3. Section 4.3: bounds (1) and (2) are introduced by "If only considering 256-bit outputs or
   shorter". Then: "For the full-length output, we do not have a truncated ideal cipher, but
   instead use a feed-forward to prevent inversion. We remark, however, that the truncation
   requirement in [13, Theorem 3] is in place purely to prevent the distinguisher from
   inverting an output; as such, the feed-forward serves the same purpose as truncation, and
   the result still follows as long as the other soundness requirements are in place."
4. Section 4.1: 128-bit security is the target "against (second-)preimage, collision, or
   differentiability attacks", with no restriction on the output length.

So: the designers' **stated bound** is for outputs of at most 256 bits; for longer output they
**claim** that the result still follows, by a remark, with no proof and no restated bound.

| # | Class | Finding | Fix |
|---|---|---|---|
| H-1 | MINOR | **The record's summary words say more than the specification does.** T-3's body quotes the remark correctly. But the options table ("streams: none"), recommendation 3 ("the designers ... give no theorem for the mode"), the decisive reason ("in a way its own security analysis does not cover") and the commit subject ("outside the designers' bound") can be read as "the designers exclude extended output". They do not: they assert the result extends. | Word it everywhere as: "bound (2) is stated for outputs of at most 256 bits; for extended output the designers assert the same result in a remark, without proof ([B3] 4.3); 128-bit differentiability is their stated goal for the function as a whole ([B3] 4.1)". The choice of (c\*) over (c) is then a preference for a stated bound over an unproved remark, at a cost the record puts under 10% of the residue (E). |
| H-2 | NOTE | **A reason for that preference the record can add** (referee's observation, Original as far as checked against [B3] 4.2 and 4.3 only). The remark says the feed-forward prevents inversion; Section 4.2 shows that an attacker who knows the chaining input does invert the 16-word output. In the indifferentiability game the distinguisher computes the tree itself and knows that input. A simulator may still exist (it sees the earlier queries), but the remark's stated reason is not by itself an argument. | Add to T-3, labelled as above. |
| H-3 | NOTE | **The existing Merkle use is inside the stated bound.** Leaves and nodes are `derive_key` values of 32 bytes; the gadgets and the native code return eight words everywhere (`blake3_compress` and `blake3_compress_2x` return `[Wire; 8]`, `binius_hash::blake3::compress` returns `[u32; 8]`); no extended output and no 16-word value is used anywhere in the tree code. A node is one ROOT-flagged compression whose first eight words are taken: as a function this is the truncated compression (no chaining-value feed-forward in that half), and it falls under "256-bit outputs or shorter". The point of T-3 does not reach it. | None needed for the decision. |
| H-4 | NOTE | **Citation precision in `decision-b-merkle-hash.md` section 5 item 3.** It cites [B3] 4.2 for "one truncated compression, which the designers state is indifferentiable". The sentence in 4.2 is about compressions "except the root nodes"; the node of H-1.7 is a root compression. The cover for it is 4.3's "256-bit outputs or shorter" together with 4.2. | Cite both, in that sense. |
| H-5 | MINOR | **(c\*): "bound (2) applies to each" is a modelling step, not a quotation.** Bound (2) is for BLAKE3 as one function. Treating `derive_key` under four contexts (and the trees' two) as independent oracles on disjoint parts is assumption MA-1' / MA-2', as TH-2 already requires; T-4's bullet should say so and not attribute it to [B3]. | Reword T-4's first bullet; TH-2 unchanged. |
| H-6 | NOTE | (c\*) checked: `s || u_i || LE32(c)` is 100 bytes, one chunk of two blocks; the first block's chaining value (flags CHUNK_START and DERIVE_KEY_MATERIAL, the record names only the first) is reusable across a proof by ordinary incremental hashing; each 32-byte stream block is then one compression with CHUNK_END, ROOT, DERIVE_KEY_MATERIAL. It is a value of the defined mode. Two compressions for 64 bytes: 336 rows at 168. | Name both flags. |
| H-7 | NOTE | **Lemma X at 1.00 bit** is consistent with `qrom-compilation.md` section 5 (the counter-mode row is 1.00 below the default in both the IOP term and the hash term: `t -> 2t` is a factor 4 on a term quadratic in `t` and 8 on a cubic one, one bit of `kappa` each). Lemma X's own proof was not re-refereed here (TH-3 stands). | — |
| H-8 | MINOR | T-5's finalisation count (`1 + popcount` of the completed chunks) is right for BLAKE3's tree mode as specified ([B3] 2.4, 2.5: one chunk output, then one parent a stack entry, the last with ROOT). The averages and row totals built on it are estimates on the builder's estimates and were not recomputed. | Keep the (E) marks; TH-6 and test vii replace them. |

### 7.2 The recommendation

Keeping (a) now rests on three things that hold independently of H-1: no number of Theorem 6.6
(2) depends on the hash (T-1); a hash-independent route to D-6 is untried (T-9, which now has
Lemma P behind its batching half); and the recorded policy does not cover a transcript (T-7,
ruling R-1). The recommendation passes. The ranking of (c\*) above (c) passes as a conservative
choice once H-1's wording is in.

## 8. What was not checked

- Theorem 6.6 and Appendix I of [SG26]; obligation K-B; the formal treatment of the in-circuit
  transcript in the tree accounting.
- The builder's counts at their source (180 + 79 L, 663, 36,432, the residue census, D-6
  timings); prover memory with all groups live; nothing was built, run or measured in
  `yugen-proof-b2`.
- The 256-bit field type's deserialiser (N-1), beyond the fact that sampling is a raw
  32-byte read.
- Lemma X's proof; T-2's length-extension search over the schedule; T-6's dependency
  argument; T-8 and T-9's estimates; the cryptanalysis table of `decision-b-merkle-hash.md`;
  H-1.14 (the IV-constrained premise).
- The literature, for prior statements of Lemma P or PB-3.
- No P-sh code exists; every statement about P-sh is about the protocol as the record
  specifies it.

## 9. Provenance

Published, as read from rendered pages: [SG26] Definitions 2.23, 2.24, 2.26, Lemma 2.27, Lemma
5.2; [B3] Sections 2.6, 4.1, 4.2, 4.3. Under review, the Ycash developers' (2026): Lemma P,
Lemma R, findings PB-3, PB-4, T-2 to T-9, option (c\*). New in this report, the Ycash
developers (2026), unreviewed: findings L-1, L-2, F-1, F-2, H-1, H-2, H-5, conditions C-1 to
C-8, tests RT-1 to RT-6 (Original as far as checked; sources consulted: those of section 1).
The two toy checks were throwaway scripts outside every repository and are not tests of
record.
