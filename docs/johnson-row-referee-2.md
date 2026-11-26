# Second referee report on `binius-johnson-row.md` revision 2 (the 107-query and 80-query rows)

Part of Yugen. 2026-11-19. Independent review of `binius-johnson-row.md` revision 2
(commit `8e95120` of this repository), of the first referee's report `johnson-row-referee.md`, of
`johnson-row/` and of the build `yugen-proof-b2` at `cfdffc2` (read only; its uncommitted work
in progress, VENDOR change 41, is noted where it matters). The lead architect has ruled that the
cheaper row ships once internal referees pass it, with no outside review, so this report is
written as the last check. The reviewer did not write the reviewed document or the build.
Nothing but this file was written. Provenance of every finding here: **Original (the Ycash
developers, 2026)**, review findings first recorded in this file, unreviewed; where a finding
rests on a paper, the paper and the place are cited.

## 0. Verdicts

| Item | Verdict |
|---|---|
| **107 queries at rate 1/8 (`m = 10`)** | **PASS WITH CONDITIONS** C-1 to C-6 (section 7) |
| **80 queries at rate 1/16 (`m = 10`)** | **PASS WITH CONDITIONS** C-1 to C-6 and C-7 |
| Node row, unique decoding, rate 1/4 | **225 is the certified count** (+0.0472 bits) under the book convention and the 20,000 x 601 budget; 226 is not required. Under convention (b) of finding Q-5 it is 235 (C-2) |
| D-pre (`pre(x)` length over the identifier only) | **PASS** (extra error 0; condition C-6 (a)) |
| D-idx (indices as 4 masked bytes) | **PASS** (extra error 0) |
| D-term (terminal check by evaluation of the first coset) | **PASS** (extra error 0 against the analysed protocol; at most `7/2^256` against the pin's check; the builder's `49/2^256` is a valid looser bound; conditions C-6 (b), (c)) |

**What the 107 row rests on, exactly.** (1) DKT26 Theorem 4.4 with Corollary 6.6 (and Lemma 3.3,
which the build does not reach): only qualitatively, a full-agreement-set line MCA at the Johnson
threshold in characteristic 2 on an arbitrary evaluation set with exceptional count below
`2^103.48` at `n = 2^30`; the theorem gives `2^43.9` (exact count) to `2^44.6` (closed form), 59.6
bits of slack. I read the proof chain of Theorem 4.4 for the line case (section 4) and found no
gap; its one external count I verified by exact arithmetic at every line length the rows use; the
Lean formalization the paper cites is sorry-free at source level over the whole import closure
of the needed theorems (not compiled: C-1). (2) Haböck's measure framework and query lemma
(shared with the 184 row). (3) Lemmas U, J1, J2, J3, F, K of the reviewed document (all hold;
one wording error in Lemma F, no change to any number). (4) The build properties H7, H8' (BR-1 to
BR-5: evidenced in the build). (5) The query round, the binding term: 152.968 bits against 152.519,
+0.449 bits. (6) The classical-convention decision Q-5, which is open for every row, the 184 row
included.

**What changes if DKT26 Theorem 4.4 were false** (section 4.5): the 107 and 80 rows lose the
bound on every mask, index and fold round of every proof; the 184 row is not affected.

## 1. What was read and run

Papers, text layers extracted with `pypdf` to a scratch directory outside every repository and
deleted afterwards; the PDFs stay in the reference-paper collection (REFERENCES.md):

- Q. Dao, S. D. Kominers, J. Thaler, *Reed–Solomon Codes Beyond Johnson: Efficient Decoding and
  Smaller Cryptographic Proofs*, ePrint 2026/2056, copy dated November 2, 2026, preprint ("DKT26"):
  Section 3.1 (Definitions 3.1, 3.2, **Lemma 3.3 with proof**); Section 4 in full (**Lemma 4.1 with
  proof, Lemma 4.2 with proof, Lemma 4.3 statement and its explanation, Theorem 4.4 with its proof
  paragraph**); Section 6.2 (Corollary 6.4, **Lemma 6.5 with proof**, Corollary 6.6 with proof);
  Corollary 9.4 (statement and proof paragraph); Appendix A.3, A.4 (**Lemmas A.4, A.5 with
  proofs**); Appendix B in full (**B.1 the proof of Lemma 4.3, B.2 Proposition B.1 with proof and
  the list bound, B.3 the closed constant**); Appendix H (Lean map); the AI methodology statement;
  bibliography entries [BCH+26], [BCI+23], [Zhe26], [Jo26a], [Hei83], [Ful98], [GS99], [The26],
  [DKSS13], [DA26]. Lemma A.3 (regular Taylor chart) was read as a statement only.
- C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*,
  ePrint 2026/2615 ("SG26"): Definitions 2.11 to 2.13, Lemmas 2.14, 2.15 with their proofs
  (Appendix A), Definitions 2.18, 2.20, Lemma 2.21 and its proof, Protocol 6.5, Theorem 6.6
  (statement, all parts), Section I.1 ("Hash functions", "Challenge inputs", "Leaves",
  "Samplers", "Merkle trees", "Prover and verifier").
- A. Chiesa, G. Fenzi, M. Weissenberg (first page), *Zero-Knowledge IOPPs for Constrained
  Interleaved Codes*, ePrint 2026/391 ("CFW26"): Lemma 6.6 with the first part of its proof; the
  implementation paragraph citing [BCHKS25].
- U. Haböck, *Basefold in the List Decoding Regime*, ePrint 2024/1571: Lemma 3 with proof, Section
  5.4.
- B. E. Diamond, J. Posen, *Polylogarithmic Proofs for Multilinears over Binary Towers*, ePrint
  2024/504, and G. Arnon et al., *WHIR: Reed–Solomon Proximity Testing with Super-Fast
  Verification*, ePrint 2024/1586: searched for Johnson-regime MCA statements (none beyond WHIR's
  Conjecture 4.12 and its Johnson list bound, Theorem 4.3).
- ArkLib (the Lean library DKT26 cites as [DA26]), `github.com/quangvdao/ArkLib`, revision
  `6aa8b6fe` (the one DKT26 names), downloaded read-only to the scratch directory and deleted:
  `ArkLib/Data/CodingTheory/ReedSolomon/PaperGuide.lean`,
  `.../MutualCorrelatedAgreement/Johnson/Agreement.lean` (theorem
  `exists_johnson_line_exactCorrelatedPair`), `.../HiddenDerivative/Parameters/Johnson/FiniteBounds.lean`
  (definitions), `.../MutualCorrelatedAgreement/ExtensionDescent.lean` (`HasExactCorrelatedPair`),
  `.../Interleaved/PowerAgreement.lean` (`uniformExactInterleavedPowerAgreement_of_scalar`), and a
  scan of the import closure (section 4.3).

This repository: `binius-johnson-row.md` (all), `johnson-row-referee.md` (all), `johnson-row/*.py`
(all, run, and instrumented from a scratch script), `CITATION-AUDIT.md` C-11 to C-16, 1c, 1c-R2,
C-33, C-34, `qrom-compilation.md` sections 2, 3, 4, 5, 6.2, `soundness-method.md` 8.5b and 8.5
(condition C), `soundness/` revision 7 (`spbcs.py`, `revision6.b_counts`) used as a library.
The build: `docs/parameters.md` 2a.2, 8.4, 8.5, 9.6, 10.2, 10.2.1, 11.1 to 11.4, 12.5, 13.9, 13.10;
`VENDOR.md` rows 29, 34, 35, 36; `vendor/binius64/crates/iop/src/fri/verify.rs`
(`verify`, `check_terminal_entries`, `fold_terminal`, `evaluate_first_coset`) and the test
`iop-prover/src/fri/tests.rs::the_first_coset_determines_every_symbol_of_a_codeword`;
`src/params.rs` (`Level::Cat1Johnson`).

Run: every file of `johnson-row/` (all pass); the instrumentation of section 2.2; my own
recomputation script (outside the repository; its method is section 5, independent of
`rowcalc.py` except that `soundness/`'s `spbcs.SpbcsTree` evaluates SG26 Theorem 6.6 (2)); a
scratch test of a dimension-1 fold round. Not run: any Lean build; any build or test of
`yugen-proof-b2`.

## 2. The lemmas

### 2.1 Verdicts

| Lemma | Verdict | Step at fault, correction |
|---|---|---|
| F1' (list size 19 at rate 1/8; 31 at rate 1/16) | **Holds** | Pairwise Johnson count (DKT26 (38), proof in B.2, read): it needs only that two distinct codeword tuples agree on at most `D` common columns. Recomputed at every `n = 2^4 .. 2^31` (rate 1/8) and `2^5 .. 2^32` (rate 1/16) |
| U (list state) | **Holds** | — |
| J1 (ring switch, `8 B_list / |K|`) | **Holds** | — |
| J2 (mask round, `(N_line + B_list)/|K|`, both orientations) | **Holds under F2** | The build uses Diamond's orientation (VENDOR change 25), which the lemma covers |
| J3 (lifted oracles) | **Holds under H7 and H8'**; both are met by the build as committed (section 6.4) | — |
| F (index and `X` folds) | **Holds under F2** (and DKT26 Lemma 3.3 at a level of message dimension 1, which the build does not reach at the terminal dimension 2^7) | **W-1, wording**: step 5 says "every `y` in `Lambda_i` has `phi_y` nonzero". Only the members with weighted agreement `mu*_{i-1}(S(y)) >= 1 - theta` are forced nonzero by step 4; a member of low weighted agreement may have `phi_y = 0`. It is never the explaining member of step 3 (that one has weighted agreement at least `1 - theta`), so the count is unchanged: the good `lambda` outside `Exc` are roots of the nonzero `phi_y` of the explaining members, at most `2 |Lambda_i|`. Correct the sentence; no number changes. Virtual folds and arities above 1: Haböck Section 5.4 (read: "carried over without any changes", virtual commitments) is exactly the reading of review item 4; holds |
| UD (the 184 row) | **Holds** | A second source for the line bound `N_line(n) = n` on any evaluation set is now in the folder: SG26 Lemma 2.14 (2), proved in its Appendix A from BCIKS20 Theorem 4.1 (exceptional set: at most `n` challenges, or at most `e_U` accidental ones), at threshold `n - e_U`, which is our `(n + k)/2` |
| K (round-by-round knowledge, list extractor) | **Holds under F2, H7, H8'** and the spBCS hypotheses of `qrom-compilation.md` 3 | See 2.3 |
| Remark Q | **Holds** | — |

### 2.2 The tests (R-10): non-vacuous now?

Instrumented from a scratch script (the repository's tests unchanged):

| Test | Instances | Measured | Verdict |
|---|---|---|---|
| T-J2-list, lerp | 4 | every instance doomed, `|Lambda4| = 2`, `|E| <= 1`, `|S \ E| = 2` | non-vacuous |
| T-J2-list, Diamond | 4 | every instance doomed, `|Lambda4| = 2`, `|E| = 0`, `|S \ E| = 2` | non-vacuous |
| T-F | 6 | every instance doomed, `|Lambda| = 2`, `|E| = 17` or 18, `|S \ E| = 4 = 2 |Lambda|` | non-vacuous |
| T-J1-list | 150 draws | union above 32 in some instance (asserted) | non-vacuous |
| T-J3, steps 1 to 4 | 1 instance, every `s'` | non-lift member present; extraction succeeds at the lifted level only; index round reaches `|S \ E| > |Lambda2|` | non-vacuous |
| **T-J3, step 5** (`X` fold at dimension 1) | 2 calls | **the pair list is empty in both, `S` is empty, `|E| = 1`**: the check `|S \ E| <= 2 |list|` holds by the definition of `E` | **vacuous** (the referee-1 defect, at this step) |
| **T-J3, step 6** (query) | — | "`lambda` not in `S` implies the passing `c'` has fewer than `A_n` agreements" restates the definition of `S` | **tautological** |

The section 11 claim "an `X` fold that ends at message dimension 1 (Lemma 3.3's count `<= 9`
checked)" is literally true but exercises neither the list nor the root count. A scratch check
written for this report (dimension-1 fold, `K = GF(256)`, `n = 8`, constant code, `A = 4`, rows
`(e, o)` agreeing with two constant pairs on disjoint 4-sets, `h` with three planted roots): 40
of 40 instances doomed with `|Lambda| = 2`, `|S \ E| > |Lambda|` in all 40, `|E| <= 1` against
Lemma 3.3's 9. So Lemma F at dimension 1 holds non-vacuously; the repository's test should carry
such an instance (condition C-5). Not blocking for the build (it does not reach dimension 1).

### 2.3 Lemma K, checked against SG26

- SG26 Definition 2.20 with Lemma 2.21 (read, with proof): under the total order the causal
  definition is CMS19 Definition 8.5 with per-round errors. Lemma K's state (0 up to and
  including the first commitment, then `St_Lambda`) satisfies CMS19's conditions: 0 on the empty
  transcript, never raised by a prover message (Lemma U), a full transcript with state 0 rejected
  except with the query round's error.
- First round: if no member's low block is a witness, every member is doomed and Lemma U gives
  `B_list eps_0`; contrapositive gives extraction from a complete list at the lifted level. Later
  rounds: the condition of Definition 8.5 is vacuous because the per-member analyses bound the
  reduced claims whatever the truth of `x`. Correct.
- SG26's extractor hands the IOP extractor oracle strings recovered from the query database, with
  unrecovered positions at default values (Section I.1, "Leaves"); Lemma K's extractor list-decodes
  whatever string it is given, so it needs no property of the string. Polynomial time: one list
  decoding of length at most `2^22` (`2^23` at rate 1/16) and at most 19 (31) relation checks; the
  decoder exists in every characteristic (DKT26 Corollary 9.4, statement and proof paragraph read;
  the Guruswami–Sudan decoder, from memory).
- `kappa_i = eps_i`: the largest is the query round. SG26 Theorem 6.6 (2) then applies with `eps_k`
  equal to it (section 5.3).

Out of the reviewed document's scope and not specific to the row: knowledge of a leaf witness from
a root proof needs the per-level online extractors composed through the in-circuit verifications
(the recursion heuristic C2 of `soundness-method.md` 2.4); it is the same for 184 and 107.

## 3. The first referee's report: every item

| Referee item | Answered by | New gap? |
|---|---|---|
| Lemma U holds; F1 conservative; J1 holds | no change needed; `B_list = 19` adopted; the `omega` row's descent precision added (3) | no |
| J2 holds under DKT26 (R-1) | status stated (0.1), qualitative need isolated (8.4) | R-1 (a) (ArkLib) and (b) (external review) were **not** done; this report does (a) at source level (4.3) and stands in for (b) as the lead architect ruled; compile check is C-1 |
| J2' only `R = 1` | declared, route withdrawn (0.3, 4.2) | no |
| "No claim term" headline | retracted (0.3) | no |
| G-1 overstated, G-3, G-6 (R-2, R-6) | narrowed and recorded (4.3, 10); route declared unavailable | no |
| H8 mis-stated (R-5) | H8' adopted, J3 re-proved, BR-1 to BR-5 (5.1, 5.3) | no; the build meets them (6.4) |
| R-3 weighted to unweighted | written (5.4 step 2); checked here | **W-1** (step 5 wording, introduced with the rewrite; no number moves) |
| R-4 dimension-1 levels | Lemma 3.3 cited; build terminal at dimension 2^7 | test still vacuous at that step (2.2) |
| R-7 WHIR | Lemma 4.10 read; Corollary 4.11 not cited for the domain | no; SG26 Lemma 2.14 (2) is a second in-folder source |
| R-8 CFW26 | compared and relabelled (9); I read Lemma 6.6 and the description is right | no |
| R-9 knowledge | Lemma K (7) | no (2.3) |
| R-10 tests | four replacements | **T-J3 steps 5, 6 vacuous** (2.2) |
| R-11 wording, 102 row | done; 102 row dropped | no |

One cosmetic inconsistency outside the document: the build's `Level::Cat1Johnson` still carries
the list size `(m + 1/2)/sqrt(rho) = 29.70` (`src/params.rs`, parameters 8.4). It is a valid
upper bound and only makes the build's own check more conservative; C-3 aligns it.

## 4. DKT26

### 4.1 What the row needs from it

For every line `u + z v` of interleaved words of any width on an evaluation set of `n <= 2^30`
points (rate 1/8; `2^31` at rate 1/16) in characteristic 2 with message dimension `k >= 2`: a set of
at most `2^103.48` challenges outside which every degree-`< k` polynomial agreeing with the
combination on at least `A = ceil((1 + 1/20) sqrt(rho) n)` positions is `F_0 + z G_0` with
`S_z(P) = S(F_0, G_0)`. Equivalently (Remark Q) the subset form. This is Theorem 4.4 (scalar) plus
Lemma 6.5 / Corollary 6.6 (width). Lemma 3.3 is needed only at a level of message dimension 1.

### 4.2 My reading of the proof of Theorem 4.4 (line case, order zero)

The proof is: Proposition B.1 (interpolant) -> Lemma 4.3 (proved in B.1) -> Lemma 4.2 (with
Lemma 4.1) -> the count (33), (39) (B.3). Step by step, for `F = GF(2^256)`, distinct points of a
`GF(2)`-subspace, `D = n/8 - 1 >= 1`:

1. **Interpolant (Proposition B.1).** Conditions: the coefficient of `U^a V^b` (`a + b < m`) in
   `Q(alpha_r + U, Z, f_r + Z g_r + V)` vanishes as a polynomial in `Z`. These are Hasse-type
   conditions obtained by substitution, valid in characteristic 2. Equation count: the
   `V^b`-coefficient of `Y^j Z^e` after the substitution has `Z`-degree at most `j - b + e <
   C_Z - b`, so at most `ceil(C_Z) - b` scalar equations per `(r, a, b)`: (109) is right. **The one
   external result, `N_var > N_eq` (BCHKS full version Lemma 3.1), I verified by exact integer
   arithmetic at the theorem's own `m` (computed from our `A`) for every line length the rows use:
   rate 1/8, `n = 2^4 .. 2^31` (28 lengths, ratio at least 1.01287); rate 1/16, `n = 2^5 .. 2^32`
   (28 lengths, ratio at least 1.00745); every factor positive; and the soundness condition
   `C_spec <= m A` holds at each.** So for our instance the theorem uses no unverified count.
   Primitive normalization (division by the `Z`-content) keeps the constraints because `F[Z]` is a
   domain. Vanishing (108): `mA` roots counted with multiplicity against degree below `C_spec <=
   mA`. Holds.
2. **Lemma 4.3 (B.1), the characteristic-2 step.** Content `C(X, Z)` removed (at most `h_C`
   challenges). For an irreducible factor `Q_i(X, Z, Y) = G_i(X, Z, Y^{s_i})`, `s_i = 2^nu` maximal:
   applying the inverse Frobenius to the coefficients is a ring automorphism of `F[T, W, U]` (`F`
   finite, hence perfect), so `G~_i` is irreducible, separable in `U` (the exponents are those of
   `G_i`, and `d/dU G_i != 0` by maximality), and `G~_i^{s_i} = Q_i(T^{s_i}, W^{s_i}, U)` (95): I
   checked this coefficientwise. Then `Q_i(X, z, P(X)) = 0` gives `G~_i(T, w, P(T^{s_i})) = 0` for the
   unique `w` with `w^{s_i} = z` (Frobenius is injective). Gauss's lemma and separability give a
   nonzero resultant of degree at most `(2b_i - 1) h_i` (Sylvester matrix count, checked); off its
   roots the separant is nonzero and Hensel lifting at a transcendental center reconstructs
   `P((t_0 + xi)^{s_i}) = sum_r P^[r](x_0) xi^{s_i r}` (101; `(t_0 + xi)^{s_i} = t_0^{s_i} + xi^{s_i}` in
   characteristic 2) with the separant as the only divisor: no integer is inverted, so no
   characteristic condition. The degree bookkeeping (100), (102), (103): I re-derived
   `h_i beta_i + b_i alpha_i = l j_i + h_i (1 + (2 s_i D - 1)(2 b_i - 1))` and identity (103)
   algebraically. Lemma A.3's coefficient degree bounds were taken as stated (not re-derived).
3. **Lemma A.5 at `d = 0`** (the only case Theorem 4.4 uses) bounds the degree of the image of a
   plane curve of bidegree `(h_i, b_i)` under a map of bidegree `(alpha_i, beta_i)` by
   `h_i beta_i + b_i alpha_i`: this is the bihomogeneous Bézout count on `P^1 x P^1` (classical; from
   memory, not re-read); the paper's Hilbert-function proof (read) gives the same leading term.
   Lemma A.4: Chevalley plus refined Bézout (read; standard).
4. **Lemmas 4.1, 4.2** (read with proofs): the incidence bound is an induction on components with
   refined Bézout [Hei83, Ful98]; a one-dimensional component in at least `L >= k` agreement
   hyperplanes is a witness graph (any `k` evaluation equations determine the witnesses); every
   other curve contributes at most `deg C (n - L + 1)/(A - L + 1)` points; graphs are counted on the
   transcendental fibre (at most `B_jet` of them); accidental agreements on a graph are roots of a
   nonzero affine polynomial in `z`. Outside `E` every candidate lies on a counted graph with no
   accidental agreement, hence the full-set equality, and the witnesses are over `F` by
   interpolation on `>= k` common positions. I found no step that uses odd or large characteristic.
5. **Lemma 6.5** (read, proof checked): `q` proper subspaces cover fewer than `q^s` vectors, one
   projection keeps every bad challenge bad. **Lemma 3.3** (read, proof checked): collision
   counting.

**My conclusion.** I believe Theorem 4.4, Corollary 6.6 and Lemma 3.3 for binary additive
Reed–Solomon codes at our parameters. What I did not re-derive: Lemma A.3's degree bounds, the
refined Bézout inequality and Chevalley's theorem (classical, cited by the paper), and the general
`d` of Lemma A.5. A degree bound wrong by any polynomial factor would not matter (59.6 bits of
slack); only a qualitative failure of the conclusion would.

**External results Theorem 4.4's proof uses** (as cited by DKT26): Guruswami–Sudan interpolation
[GS99]; the BCHKS order-zero symbolic interpolant and its dimension estimate [BCH+26, full version,
Lemma 3.1] (the count verified here at our sizes); the solution-tracking approach of BCIKS
[BCI+23] and Zheng's incidence and persistent-line arguments [Zhe26] (followed, not cited as
lemmas); the refined Bézout inequality [Hei83, Ful98]; Chevalley's theorem [The26]; Hasse
derivatives [DKSS13]; Gauss's lemma and resultants (textbook). Corollary 6.6 adds Jo's projection
idea [Jo26a] (re-proved as Lemma 6.5) and Corollary 6.4's packing ([ABF26, Lemma 2.21], only
injectivity used).

### 4.3 The Lean formalization (R-1 (a), source level)

DKT26 Appendix H points to `ReedSolomon/PaperGuide.lean` at ArkLib revision `6aa8b6fe`. At that
revision the guide maps Theorem 4.4's MCA part to `exists_johnson_line_exactCorrelatedPair`. Its
statement (read): any `Field F`, any embedding `domain : Fin n ↪ F`, `1 <= D <= n - 2`, `eta > 0`,
`johnsonAgreement n D eta * n <= A <= n`; there is a `Finset` of challenges of cardinality at most
`johnsonExceptionCount n D A eta` such that every `z` outside it and every `P` of degree below
`D + 1` with at least `A` agreements has `HasExactCorrelatedPair` (a pair of degree-`< D + 1`
polynomials with `P = F_0 + z G_0` and **equality** of the full agreement set with the common one).
No characteristic hypothesis, no domain structure: exactly F2's scalar form. The formal count uses
the coarser coefficient `1 + 4 D mu` in place of `Psi_D`: at our sizes 212.11 bits at `n = 2^30`
(rate 1/8) and 210.18 at `2^31` (rate 1/16), against 212.14 and 210.19 for (33), so the formal
statement alone meets the need. Interleaving: `uniformExactInterleavedPowerAgreement_of_scalar`;
constant codes: `uniformExactPowerAgreement_constantCode`; list: `closePolynomialSet_finite_and_
ncard_le_pairwiseJohnson`. **Scan**: the import closure of those four theorems and of the Johnson
parameter file (227 modules of the repository) contains no `sorry`, `admit`, `axiom`,
`native_decide`, `implemented_by`, `opaque` or `@[extern]` outside comments (three hits, all the
word "admit" in prose). The repository has 13 files with `sorry`, none in that closure. **Not
done**: compiling it and printing the axioms (C-1); a source scan does not exclude a statement
that fails to elaborate.

### 4.4 Does the needed statement follow from anything else in the folder?

No. SG26 Lemma 2.14 (1) and Lemma 2.15 restate it with DKT26's proof (their Appendix A cites DKT26
for the transfer step), so they are not independent. CFW26 takes `eps_mca` as a parameter and its
implementation cites [BCHKS25] without restating it. WHIR states Johnson-regime MCA only as
Conjecture 4.12. Haböck 2024/1571 proves weighted correlated agreement with a constraint, not the
full-set MCA, and its route has gaps G-1, G-3, G-6. DP24 is unique-decoding only. The independent
sources DKT26 Section 1.2 names (BCHKS, ePrint 2025/2055; Haböck, ePrint 2025/2110; Bordage,
Chiesa, Guan, Manzur, ePrint 2025/2051) are not in the folder and were not read.

### 4.5 The risk in plain terms

If Theorem 4.4 (or Corollary 6.6) were false in characteristic 2 in the strong sense that matters
(no subexponential exceptional count at the Johnson threshold), then in the 107 and 80 rows the
leaf's mask round and index round and every `X` fold of every proof, leaf and node, would have no
proven bound. An attacker who can construct a committed word far from the code (no list member
satisfying the claim) for which a sizeable fraction of fold challenges yields a close, unexplained
codeword would pass those rounds by grinding the Fiat–Shamir challenge, and could then pass the
query round from a folded word that is close. The outcome is an accepted leaf proof of a false
statement or one from which no witness can be extracted: a spend or a mint without a note and key,
that is, undetectable inflation of the shielded pool. To matter against the row's target the count
must exceed `2^103.48` at `n = 2^30`, about `q^0.4`; a bug that only worsened the polynomial count
would not. **The 184 row is not affected**: it uses no Johnson-regime statement (BCIKS20 Theorem
4.1, peer reviewed, via WHIR Lemma 4.10 or SG26 Lemma 2.14 (2); width by DKT26 Lemma 6.5, an
elementary lemma checked here and in the first report). The rows share Haböck's framework, Lemmas
U, J1, J3, K, the spBCS compilation and the build.

## 5. The rows, recomputed

Method: my own script. Exact `A = ceil((1 + 1/(2m)) sqrt(rho) n)` with 80-digit decimals; the
exceptional count from DKT26 (33)–(34) with the theorem's own `m`, `B_jet`, `B_Z` computed exactly
from our `A` (and the closed form (39) beside it); list sizes from (38); Lemma 3.3 for `D = 0`; all
challenges in `K = GF(2^256)`; per-round bits `256 - log2(count)`. Inputs as the document's 8.1:
leaf `|E_l| = 2^22` (rate 1/8; `2^23` at 1/16), node `2^31` (`2^32`), PIOP worst 127, form T ring
switch 8, `J = 4`.

### 5.1 Every error term (bits)

| Term | 107 @ 1/8 | 80 @ 1/16 |
|---|---|---|
| list size `B_list` | 19 | 31 |
| PIOP round (127 `B_list`) | 244.76 | 244.06 |
| ring switch (8 `B_list`) | 248.75 | 248.05 |
| claim batching (3 `B_list`) | 250.17 | 249.46 |
| leaf mask fold (`E + B_list`) | 220.14 (closed form 219.41) | 218.19 (217.41) |
| leaf index round (`E + 2 B_list`) | 220.14 (219.41) | 218.19 (217.41) |
| leaf first `X` fold | 221.14 (220.41) | 219.19 (218.41) |
| **node first `X` fold** | **212.14** (211.41) | **210.19** (209.41) |
| sumcheck rounds of the terminal folds (degree 2) | 255.00 | 255.00 |
| D-term, the whole proof (builder's bound) | 250.39 (0 by section 6.3) | 250.39 |
| query round | **152.968** (106: 151.539) | **154.369** (79: 152.439) |
| need a round (book, `N = 20,000`, `k = 600`) | 152.519 | 152.519 |
| slack of the weakest algebraic round | 59.6 | 57.7 |

All agree with the document's 8.2 to the second decimal (it quotes the closed form).

### 5.2 The node row at rate 1/4 (unique decoding)

Per query `-log2(5/8) = 0.678072`: 224 queries 151.888 (−0.631), **225 queries 152.566
(+0.0472)**, 226 queries 153.244. **225 is the certified count.** Its margin is against the
budgeted sum `20,000 x 601 = 1.202 x 10^7`; 225 holds up to `1.242 x 10^7` (3.3% more). The build's
count of the largest tree, `5.53 x 10^6` (parameters 2a.2), leaves 1.12 bits more. The query bound
is `((1 + rho)/2)^s` with the threshold `n - e_U = (n + k)/2` (Haböck Lemma 3; SG26 Definition
2.11). The algebraic rounds of such a node are at 227 bits or more. The margin is a budget margin,
not a proof gap: 226 is needed only if the tree bound or the challenge budget grows, or under
Q-5's convention (b), where the count is 235 (5.4).

### 5.3 The tree and the QROM compilation (256-bit digests)

| Row | Book union `N (1 + k) 2^-e` | Union of the actual per-round errors | SG26 6.6 (2): `k_q` | IOP term | Hash term | Stream term (tree) | **QROM bits** (margin over 64) |
|---|---|---|---|---|---|---|---|
| 184 @ 1/8 | `2^-129.21` | — | 38,832 | 67.43 | 75.63 | `2^-2829` | 67.43 (+3.43) |
| 107 @ 1/8 | `2^-129.45` | `2^-138.68` | 23,586 | 67.55 | 75.63 | `2^-2829` | **67.55 (+3.55)** |
| 80 @ 1/16 | `2^-130.85` | `2^-140.08` | 18,720 (`l_max = 2^32`) | 68.25 | 75.63 | `2^-2830` | **68.25 (+4.25)** |
| node 225 @ 1/4 | `2^-129.05` | — | — | — | — | — | (not a separate row of the calculator; C-3) |

`c' = 2,401`, `b = 32` bytes, `N = 20,000`, SHAKE256 streams, via `spbcs.SpbcsTree`. Counting the
terminal vector's 1,024 positions as opened positions in `q_IOP` (it is sent in full and checked
against its root) raises `k_q` to 57,378 (107) and changes no figure above to two decimals.

### 5.4 The open convention Q-5 (`qrom-compilation.md` 6.2), for every row

The certified need 152.52 uses the book's theorem for the hash chain. Under SG26's own classical
bound read "for every `t >= 1`" the need is `129 + log2 N + log2(1 + k_q)` and the counts become:
**107 -> 111**, **80 -> 82**, 184 -> 192, node rate 1/4 225 -> 235. Read "for `t >= k_q`", every row
stands and condition Q (145.87) binds. This is decision T-6, open for the 184 row as much as for
107; it is condition C-2, not a reason to prefer one row.

## 6. The build

### 6.1 D-pre

As built the running input is `0x20 || label || s || BE32(len(id)) || id || public words (first
item) || items`, the word count fixed by `cs_digest` inside `id`. SG26 Section I.1 asks for a
prefix-free statement encoding with a polynomial-time left inverse on its image and for statement
digests to be part of `x`; `BE32(len) || id || words` is such an encoding when the count is a
function of `id` (decode `len`, `id`, look up the count, read the words). Every challenge input
still contains the whole statement before any item, because the words are absorbed before the
first challenge. **Hypotheses of Theorem 6.6 (2) hold; extra error 0.** The one thing the argument
uses that the code must guarantee: the verifier refuses a public-word vector whose length is not
the count `cs_digest` fixes (C-6 (a)).

### 6.2 D-idx

`index = LE32(y[4j .. 4j + 4)) AND (2^n - 1)`: each of the `2^n` values has exactly `2^(32 - n)`
preimages, the sampler reads a prefix, a uniform preimage is drawn by filling the masked bits, so
SG26's sampler conditions (Section I.1, "Samplers") hold with `eps_ov = 0`. The write-back is the
first 32 bytes of the same stream, which SG26 states for its own samplers; nothing forbids the
overlap. Longer streams only lower the stream term (Section 6.3). **Extra error 0.** At rate 1/16 a
node codeword has `2^32` positions, so `n = 32`: still within the four bytes (the `qrom-compilation.md`
2.8 B-2 sentence "`n <= 31`" holds only for rates up to 1/8).

### 6.3 D-term

The pin compares each fully reduced query with `c[index]` of the terminal vector `c` (bound by its
root before the `n_f` final challenges) and checks that every coset of `c` folds to one value. The
build compares with `P_0(x_index)`, `P_0` the polynomial the first coset interpolates, computed by
`evaluate_first_coset`, which reads only the first `2^{n_f}` symbols (its argument is that slice;
code read). The repetition check is unchanged.

- **Does the evaluation check accept what the lookup refuses? Yes, in one event only**: `c` is not
  a codeword of the terminal code, every coset nevertheless folds to the same value at the final
  challenges, and some reduced query equals `Enc(P_0)[index]` but not `c[index]`. For a fixed `c`
  the repetition check passes with a non-codeword with probability at most `n_f / |K| = 7/2^256`
  (one coset `i` with `P_i != P_0` suffices; Schwartz–Zippel on the multilinear folds). The
  builder's `n_f (2^r - 1)/|K| = 49/2^256` is a valid looser union bound. The converse event (lookup
  accepts, evaluation refuses) has the same probability.
- **Soundness: no extra term against the protocol the lemmas analyse.** Let `V_send` be the verifier
  that receives the terminal message `P_0` in the clear before the final challenges and compares the
  reduced queries with the codeword `Enc(P_0)`. The built verifier accepts only if `V_send` accepts:
  coset 0's fold is `P_0`'s fold, which the repetition check equates with the final value, and the
  query comparison is identical. So acceptance as built is contained in `V_send`'s, transcript by
  transcript, and every round-by-round soundness and knowledge state function for `V_send` serves
  the build with the same errors. `V_send` is exactly what the analysis assumes: Haböck's Lemma 3
  (read) treats a terminal `f_n` outside the code as "always detected", and the reviewed document's
  5.4 says the levels below the terminal are "checked exactly against the codeword sent in the
  clear". It is the pin's lookup that needed the `n_f / |K|` term to fit that analysis; the
  evaluation makes the compared terminal a codeword by construction.
- **Compilation**: only the verifier's decision predicate changes; messages, challenges and query
  sets are the same, so H1 to H10 of `qrom-compilation.md` 3 are unaffected.
- What the argument needs from the code: `evaluate_first_coset` equals the codeword symbol for
  every first coset. It is `K`-linear in the coset (code read), and the build tests it at every
  position of six shapes including dimension `2^7` at rate 1/8, on one random codeword each, in the
  pin's 128-bit field (C-6 (b)).

### 6.4 BR-1 to BR-5 and de-duplication

| Requirement | Evidence in the build (as committed) | Verdict |
|---|---|---|
| BR-1 one opening per proof over every commitment | `tests/opening_once.rs` (transparent leaf, zero-knowledge leaf); node proofs asserted by `lverify` (11.4 item 5) | met |
| BR-2 every claim in that opening | (b) tested; (a) code search recorded (9.6): `verify_batch_zk_basefold` private, called only from `finish` | met |
| BR-3 no commitment across proofs | test: a replaced first root refused; precommit committed afresh per proof (8.5) | met |
| BR-4 levels from the shape | test: lift levels, arities, terminal dimension equal across set-ups and witnesses | met |
| BR-5 recursion | leaf slot `the_recorded_leaf_verifier_opens_once`; merge slots asserted by `lslot` | met |
| De-duplicated positions (SG26 Definition 2.18) | change 34: native prover and verifier carry one leaf a distinct position, an old-format tape refused; the circuit keeps one opening a query, the filler repeats the first occurrence | met natively; in circuit two copies of one position are each checked against the root, so differing copies would be a hash collision (Lemma D (ii) of `qrom-compilation.md` 2.8), negligible and not specific to the row |

All of this was evidenced at the 184 row; it is structural and does not depend on the query count,
but the `johnson` build has not run it (C-4). The uncommitted query-group path (VENDOR change 41, in
the working tree, not in `cfdffc2`) hands every group `terminate_codeword[..2^{n_f}]` from the one
received vector; when it lands it must keep BR-1, BR-5 and that single binding (C-6 (c)).

## 7. Conditions (each a task with a check)

- **C-1 (Lean compile, R-1 (a)).** Build ArkLib at `6aa8b6fe` with its pinned toolchain
  (`leanprover/lean4:v4.35.0`) and print the axioms of `exists_johnson_line_exactCorrelatedPair`,
  `uniformExactInterleavedPowerAgreement_of_scalar`, `uniformExactPowerAgreement_constantCode` and
  `closePolynomialSet_finite_and_ncard_le_pairwiseJohnson`. Acceptance: the build succeeds and each
  reports only `propext`, `Classical.choice`, `Quot.sound`. If this cannot be run, the row ships on
  this report's reading and source scan alone, and that is recorded as the basis.
- **C-2 (Q-5, all rows).** The lead architect decides T-6. Acceptance: under the book or the
  "`t >= k_q`" convention, 107 / 80 / 225 stand; under "every `t`", the shipped counts are 111 / 82 /
  235 (and 192 for the unique-decoding leaf row), checked by the calculator.
- **C-3 (calculator).** The calculator's maintainers implements the DKT26-route terms (document 8.4) with
  tests reproducing section 5.1 of this report: 107 and 80 queries; list 19 and 31; weakest
  212.14 / 210.19 bits with the exact count (211.41 / 209.41 closed); a refusal when a committed level
  has message dimension 1 unless Lemma 3.3's term is added; the node row at rate 1/4 (225, +0.047).
  The builder's `Level::Cat1Johnson` takes the list size from the same source (19 at 1/8, 31 at
  1/16) or keeps 29.70 as an explicit conservative value.
- **C-4 (build, the row's own configuration).** In the `johnson` build: `tests/opening_once.rs`
  passes; the BR-1 and BR-5 assertions of `lverify` / `lslot` pass on one node level; BR-4 prints
  `log_terminal_dim >= 1` for the leaf and node shapes at 107 (80) queries (so no committed level
  has `D = 0`).
- **C-5 (this repository's tests and text).** T-J3 step 5 gets a dimension-1 fold with a non-empty
  pair list in a doomed instance (the construction of 2.2), asserting `|S \ E| > |list|` in some
  instance; step 6 is described as definitional; Lemma F step 5 is reworded per W-1.
- **C-6 (deviations).** (a) A test that a proof whose public-word vector is one word longer or
  shorter than `cs_digest` fixes is refused (D-pre). (b) `the_first_coset_determines_every_symbol_of_a_codeword`
  also runs in the 256-bit field of `cat1t`, and a second test shows that `evaluate_first_coset` on a
  random non-codeword terminal vector equals the symbol of the codeword interpolating its first
  coset and is unchanged when cosets other than the first are altered (D-term). (c) When change 41
  lands: every query group receives the first coset of the one terminal vector checked against its
  root, and BR-1 / BR-5 are rerun.
- **C-7 (80 at rate 1/16 only).** The rate-1/16 index sampler is tested at `n = 32` (a node codeword
  of `2^32` positions; D-idx); the leaf and node of the row are built and verified once at 80
  queries (sizes and slot fit were not computed by the document; they are engineering, not
  soundness, but the row is not shipped untested).

## 8. Citations and provenance

Every paper result used here is cited at its place in sections 1 to 6. Published, used as is:
DKT26 Theorem 4.4, Lemma 3.3, Lemma 6.5, Corollary 6.6, Corollary 9.4, Proposition B.1, Lemmas 4.1
to 4.3, A.4, A.5; SG26 Definitions 2.11, 2.18, 2.20, Lemmas 2.14, 2.21, Theorem 6.6 (2), Section I.1;
CFW26 Lemma 6.6; Haböck Lemma 3 and Section 5.4; ArkLib's Lean statements at `6aa8b6fe`.
Original (the Ycash developers, 2026), this report: W-1; the vacuity of T-J3 steps 5, 6 and the
dimension-1 scratch check; the exact verification of DKT26 (109) and of the soundness condition at
every line length of both rows; the source scan of ArkLib's import closure; the inclusion argument
for D-term (acceptance contained in that of the terminal-in-the-clear verifier, hence no extra
term), with the `n_f/|K|` bound for the pin's form; the observation that SG26 Lemma 2.14 (2) is a
second in-folder source for the unique-decoding line bound; the Q-5 counts 111 / 82 / 192 / 235;
the tree and QROM figures of section 5 (formulas Published, computation ours). Sources consulted
before labelling them original: the papers listed in section 1. From memory and marked so: the
Guruswami–Sudan decoder's running time, the bihomogeneous Bézout count. For `REFERENCES.md`
(its maintainers, not this review): rows for the findings above, and DKT26's [DA26] ArkLib revision as
the formal source of Theorem 4.4's statement.
