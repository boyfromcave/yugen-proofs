# System B in the Johnson regime: the lemmas for the 107-query row, with knowledge soundness

Part of Yugen. 2026-11-19, **revision 2** (answers the referee report
`johnson-row-referee.md`; revision 1 is commit `5cec7e5`). Subject: finding C-11 of
`CITATION-AUDIT.md` (the 107-query candidate of `binius-extension-challenges.md` 7 (d) rests on
Haböck's Theorem 6, which does not cover three parts of Binius64 as built), finding C-12 (the
unique-decoding round errors of the 184-query row), and the referee's items R-1 to R-11. This
document writes the lemmas (Lemma U, L-J1 ring switch, L-J2 mask round, L-J3 lifted oracles,
Lemma F fold and index rounds, Lemma K knowledge), the unique-decoding errors, and the resulting
rows. The calculator in `../soundness/` implements section 8.4 since its revision 8
(`soundness/src/yugen_soundness/dkt26.py`, condition C-3 of `johnson-row-referee-2.md`), with
DKT26's exact count (33)-(34) beside the closed form (39) that `../johnson-row/rowcalc.py` uses; the
two agree to the bit on the closed form (`soundness/tests/test_revision8.py`).

**Revision 2.1** (2026-11-19, conditions C-3 and C-5 of the second referee): Lemma F step 5 reworded
(W-1, no number changes); T-J3 step 5 made non-vacuous and step 6 described as definitional
(section 11); the calculator's revision 8 (above). Nothing else changed.

## 0. Status, result, retractions

### 0.1 Status of the row

**The 107-query row at `m = 10` is proved round-by-round sound and round-by-round knowledge sound
on the DKT26 route, conditional on three statements of Dao, Kominers, Thaler, ePrint 2026/2056
(copy of 2026-11-02, a preprint, not peer reviewed; "DKT26"): Theorem 4.4 (line mutual correlated
agreement with full agreement sets at the Johnson threshold, every characteristic, any evaluation
set), Corollary 6.6 (its interleaved form, width independent) and Lemma 3.3 (the same for message
dimension 1).** Lemma 6.5 and Lemma 3.3 have elementary proofs that were read and checked (the
referee checked Lemma 6.5 too); Theorem 4.4's proof rests on algebraic-geometry lemmas (4.1 to 4.3,
A.5) that were not checked line by line here, and on a dimension count of Ben-Sasson, Carmon,
Haböck, Kopparty, Saraf (BCHKS, full version Lemma 3.1, not read) that the referee verified by exact
arithmetic at our sizes only. The other ingredients are proved in this document or are published
statements whose proofs were read (section 1).

**The row is NOT available on Haböck's route alone** (ePrint 2024/1571 without DKT26): for the
leaf, the mask round needs gap G-1 (Theorem 4 for interleaved words with challenges in a subfield);
every fold round on that route rests on Haböck's weighted Theorem 3/4, whose proof refers to a
section of the BCIKS20 full version not available here (G-3) and whose treatment of inseparable
factors in characteristic 2 is unchecked (G-6). This applies to nodes too (their fold rounds use
Theorem 4). Fallback F-J2 removes G-1 only.

What the row needs from DKT26 is qualitative (section 7.4): **line MCA with full agreement sets
(equivalently, WHIR's subset form) at agreement `ceil((1 + 1/(2m)) sqrt(rho) n)`, in
characteristic 2, on an arbitrary evaluation set, with exceptional count below `2^103.48` at
every line length up to `2^30`.** DKT26's explicit count (39) is 59 bits below that. Three other
works prove Johnson-radius MCA according to DKT26 Section 1.2 (not read here, not in the reference
folder): BCHKS (STOC 2026, peer reviewed; full version ePrint 2025/2055, Theorem 4.6, "every
characteristic"), Haböck ePrint 2025/2110 and Bordage, Chiesa, Guan, Manzur ePrint 2025/2051. Any of
them, once read and found to state the property above, removes the dependence on DKT26.

### 0.2 Proved here (P), with dependencies

| Lemma | Statement (round-by-round error, count of bad challenges out of `|K|`) | Depends on |
|---|---|---|
| F1' (2.2) | list size `B_list <= 19` at `m = 10`, every width, every evaluation set | the Johnson bound, DKT26 (38) second term (proof read) |
| U (2.3) | a round analysed per fixed oracle has error `B_list` times its per-oracle error; commitments cannot un-doom | F1' |
| J1 (3) | ring switch: `8 B_list` | U; Theorem 1 of `binius-extension-challenges.md` |
| J2 (4.1) | mask round: `N_line(n) + B_list` (the claim term `B_list` included) | F2 = DKT26 Theorem 4.4 + Corollary 6.6 |
| J3 (5.1) | lifted oracles: every statement holds for the lifted words' lists, under H7 and **H8'** | H7, H8' (build requirements BR-1 to BR-5, section 5.3) |
| F (5.4) | index round and `X` fold: `N_line(n_i) + 2 B_list`, written with the weighted-to-unweighted step; message dimension 1 by DKT26 Lemma 3.3 | F2; Lemma 3.3; Haböck's measure framework (Section 5.2, read) |
| UD (6) | the 184-query row's terms, round by round | WHIR Lemma 4.10 (now read) with BCIKS20 Theorem 4.1; DKT26 Lemma 6.5 |
| K (7) | round-by-round knowledge (CMS19 Definition 8.5, per round) with the same errors; extractor: list-decode the first oracle at its lifted level, test at most 19 candidates | U, J1, J2, J3, F; polynomial-time list decoding (DKT26 Corollary 9.4, statement read) |

Compiled: Sharp, Grubbs, ePrint 2026/2615 ("SG26"), Theorem 6.6 (2) turns round-by-round
knowledge into online (straight-line) knowledge soundness in the QROM for the spBCS transcript
(Protocol 6.5), the form `../soundness/` revision 6 already adopts for condition Q.

### 0.3 Retracted or corrected (revision 1 → revision 2)

| Revision 1 said | Now | Referee item |
|---|---|---|
| "All three lemmas are proved" | proved conditional on DKT26 Theorem 4.4, Corollary 6.6, Lemma 3.3 (0.1) | R-1, overall verdict |
| "A second, independent route" (Haböck) proves the row with one reading check (G-1) | **withdrawn**: Haböck's route is not available for the row; G-1, G-3, G-6 are open, and L-J2' covers only `R = 1`, which the build never uses | 2.4, 3.4 |
| "The mask round costs no claim term ... the claim needs no separate event" | **withdrawn for the DKT26 route**: the mask round's error contains the claim term `B_list / |K|` (one root of `phi_y` per list member); "no root term" holds only on Haböck's route (L-J2') | R-11, 0 item 4 |
| The 102-query row (`m = 153`, DKT26 route) | **dropped**: 0.001-bit margin, and it needs DKT26's constant (39) itself (Haböck's count gives 142.25 bits there) | R-11, 4.1 |
| `B_list = (m + 1/2)/sqrt(rho) = 29.70` | `B_list = 19` (Johnson bound): 29.70 was valid but looser; `binius-extension-challenges.md` 7 (d) already had 19 | R-11, 2.3 |
| H8 (one level per commitment, no reuse "at another level") | **H8'** (a commitment binds a list, not a message): one batched opening per commitment per proof; nothing relies on two openings of one commitment denoting the same message | R-5 |
| G-4: knowledge "none needed for the soundness rows" | Lemma K proves round-by-round knowledge with a list extractor (section 7) | R-9 |
| Lemma F proof skipped the weighted-to-unweighted step; Theorem 4.4 used at every level | the step is written (5.4, step 2); levels of message dimension 1 use DKT26 Lemma 3.3 | R-3, R-4 |
| Decision 2: F-J2 makes "the leaf row rest on Haböck's published theorems" | F-J2 removes G-1 only; G-3 and G-6 stay | 2.4 (a) |
| G-1 applies to the leaf's index round | G-1 applies to the leaf's **mask** round only; the index round at `R = 2` is a line of scalar words (still subject to G-3, G-6 on Haböck's route) | 2.4 (c) |
| J2 "Original as far as checked" (2026/391 not consulted) | **Adapted**: the error shape and proof pattern are published in Chiesa, Fenzi, Weissenberg, ePrint 2026/391, Lemma 6.6 (= Theorem 6.3's RBR errors); Lemma F's index rounds are that lemma's sumcheck rounds (section 9) | R-8 |
| Tests in `johnson-row/` (tautological mask tests, vacuous Diamond test, set-arithmetic union test) | replaced by the referee's T-J2-list, T-F, T-J1-list, T-J3, each with a non-empty list in a doomed instance (section 11) | R-10 |
| WHIR "Lemma 4.10 / Corollary 4.11 (D)" | Lemma 4.10 now read in ePrint 2024/1586 (any linear code); Corollary 4.11 is stated for WHIR's smooth domains, so for our domain the line bound is Lemma 4.10 with BCIKS20 Theorem 4.1 (any domain) | R-7 |

### 0.4 Rows (category 1: 20,000 proofs, no grinding, 256-bit digests, `|K| = 2^256`, target 152.52 bits a round)

| Row | Queries | Weakest algebraic round (bits) | Leaf / node KiB (E) | Leaf slot AND rows (E) | Rests on |
|---|---|---|---|---|---|
| unique decoding, rate 1/8 (as now) | 184 (152.73) | 226.00 (node, first fold) | 568 / 699 | 7.82 M | WHIR Lemma 4.10 + BCIKS20 Theorem 4.1; DKT26 Lemma 6.5 for width |
| **Johnson, `m = 10`, rate 1/8, DKT26 route** | **107** (152.97) | **211.41** (node, first fold) | 362 / 449 | 4.55 M | DKT26 Theorem 4.4, Corollary 6.6, Lemma 3.3 (qualitatively: count `< 2^103.48`) |
| Johnson, `m = 10`, rate 1/16, DKT26 route | 80 (154.37) | 209.41 | not computed here | not computed here | the same; twice the encoding work |

**Revision note (2026-11-19, calculator revision 9; `docs/decision-qrom-counting.md`).** The table above is at the
book need 152.52, which the lead architect's ruling on condition C-2 makes non-default ("t >= k_q", not certified).
Under the default convention (every `t`, [SG26] Theorem 6.6 (2) at each row's own `k_q`): unique decoding at rate
1/8 **192** (need 158.59), Johnson `m = 10` at rate 1/8 **111** (157.86) and at rate 1/16 **82** (157.51); the node
at rate 1/4 **235** in unique decoding and **171** in the Johnson regime (arithmetic only: no lemma here is stated or
refereed at rate 1/4 and no build has that shape, `soundness-rev8-referee.md` R8-3). The weakest algebraic rounds
are unchanged (226.00 / 212.14 / 210.19 exact count); the list sizes are unchanged (19 / 31 / 10); the tolerated
count of 8.4 falls with the need. The referee estimated that 111 queries put the rate-1/8 Johnson merge slot about
1.2 % over `2^21` AND rows (E, groups of six); the builder's count (`yugen-proof-b2` `parameters.md` 15.5) fits it
in `2^21` with groups of five (1,985,497), while the candidate leaf slot fits `2^21` at neither 107 nor 111. The text
below is unchanged.

Category 3 (target 216.52): unique decoding, **261 queries** at rate 1/8 (weakest 226.00). The
Johnson regime does not reach category 3 in `GF(2^256)`: DKT26 at `m = 3` leaves the node's first
fold at 216.16 bits (0.36 short; 170 queries if no opening exceeds `2^30` codeword points).

**Build requirement from H8'** (section 5.3): every commitment of a proof is opened by exactly
one batched BaseFold opening of that proof, into which every claim on it is batched; no statement
relies on two openings of one commitment, within a proof or across proofs, denoting one message.
Binius64 as vendored meets it by construction (`BaseFoldVerifierChannel::finish(self)` consumes the
channel and runs the single combined opening); BR-1 to BR-5 make it checkable in code.

---

## 1. Scope, sources, marks

**Read for revision 1** (text layer extracted to a temporary directory outside every repository;
the papers stay in the reference-paper collection (REFERENCES.md)):

- Haböck, "Basefold in the List Decoding Regime", ePrint 2024/1571 (undated copy): Sections 2.2,
  3 (Protocols 1, 2, Theorem 1), 4 (Propositions 1, 2, Theorems 2, 3, 4, Remark 5), 5 (Lemmas 1 to
  3, Section 5.4), 6.1 (Lemma 4), 6.2, 6.3 (Protocol 3, Lemma 5 with its proof, Theorem 6).
- Diamond, Posen, "Polylogarithmic Proofs for Multilinears over Binary Towers", ePrint 2024/504:
  Definitions 2.8 to 2.10, Construction 3.1, Theorems 3.2 and 3.5 with proofs.
- Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields", ePrint 2025/1015: Construction
  4.1, Theorems 4.2 (sketch) and 4.3.
- Ben-Sasson, Carmon, Ishai, Kopparty, Saraf, "Proximity Gaps for Reed-Solomon Codes", ECCC
  TR20-083 (copy of May 30, 2020; "BCIKS20"): Theorems 1.2, 1.4, 1.5 (1.6 in that copy; numbers amended 2026-11-19 to the folder copy, ePrint 2020/654 revision of July 3, 2021, C-41), 4.1, 5.1, 5.2, Section 5.1
  (Lemma 5.3), Section 5.2 Steps 1 and 2 (Claim 5.4), Section 7.2. No weighted section in this copy.
- DKT26: abstract, Theorem 1.1, Definition 3.2, Section 4.3 (Theorem 4.4 and its proof paragraph),
  Section 6.2 (Corollary 6.4, Lemma 6.5, Corollary 6.6, with proofs).
- Binius64 Blueprint of 2026-11-16 (`yugen-b-eval/upstream/papers/binius64-spec.txt`): Sections
  5.2, 5.3 (Theorem 5.1, identity (8)), 5.4, 5.5, 7.1, 7.2 (Protocol 7.1 and its soundness paragraph).
- This repository: `binius-extension-challenges.md`, `CITATION-AUDIT.md` 1b, `REFERENCES.md`,
  `soundness-method.md` 8.5b, 8.5d, `design-basis.md` 1, `zk-wi-soundness.md` 9;
  `yugen-proof-b2/docs/zero-knowledge.md` 1.2; the calculator `binius64.py`, `current.py`.

**Read for revision 2** (the same way):

- `johnson-row-referee.md` (all); `CITATION-AUDIT.md` 1e (C-14 to C-21);
  `binius-extension-challenges.md` 3.1, 4.1, 7 (d); `qrom-compilation.md` 5;
  `../soundness/CHANGELOG.md` revision 6 (spBCS and SG26 Theorem 6.6 (2) for condition Q).
- DKT26, further: Section 1.1 (the knowledge-soundness paragraph), Theorem 1.3 (informal), Section
  1.2 (related work on correlated agreement and MCA), Section 3.1 (Definitions 3.1, 3.2, **Lemma 3.3
  with its proof**), the end of Section B.2 (the proof of the list bound (38)), Theorem 9.3 and
  Corollary 9.4 (statements: deterministic complete list decoding above Johnson in every
  characteristic). The bibliography entries [BCH+26], [Hab25], [BCGM25], [Jo26a].
- Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint
  2026/391 (copy of 2026-11-16; "CFW26"): Definitions 3.3, 3.4 (round-by-round knowledge with
  relaxation, after [BCFW25]), Definitions 3.16, 3.17, Lemma 3.18 (statement), Definition 3.19
  (MCA error), Section 6.2 (Theorem 6.3, Construction 6.4), Section 6.4 (Lemma 6.6 with its proof).
- Sharp, Grubbs, "Faster and Smaller Anonymous Credentials from Standardized Signatures"
  (GordieHowe), ePrint 2026/2615 ("SG26"): Definition 2.20, Lemma 2.21 (statement), Section 5.5
  (5.5.1, 5.5.2, Table 1; Lemma 5.10 statement), Theorem 6.6 (statement), Definition H.3. Appendix
  F (Lemmas F.2, F.4, Theorem F.6) and Appendix I were not read.
- Arnon, Chiesa, Fenzi, Yogev, "WHIR", ePrint 2024/1586 (copy of 2024-11-21; "ACFY24", in the
  folder; the referee did not find it): Definition 4.1 (the restriction to smooth domains), Theorem
  4.8 (statement), Definition 4.9, Lemma 4.10 (statement and the first part of its proof),
  Corollary 4.11, Theorem 7.5 (statement).
- Chiesa, Manohar, Spooner, ePrint 2019/834 ("CMS19"): Definitions 8.3 to 8.5, Theorem 8.6, the
  start of Section 8.5.2.
- Haböck 2024/1571, again: Section 5.2 (measures (29), (30), language (31), Lemma 2 with proof),
  Section 6.1 ((33) to (35), Lemma 4 with proof).
- `yugen-proof-b2`: `docs/transcript-binding.md`, `VENDOR.md`; in
  `vendor/binius64/crates/`: `iop/src/basefold/channel.rs` (`recv_oracle`, `finish`,
  `verify_batch_zk_basefold`), `iop/src/fri/common.rs` (`log_terminal_dim`, `log_lift`), and the
  callers of `finish` (`verifier/src/verify.rs:510`, `verifier/src/zk_config.rs:317`,
  `spartan-verifier/src/lib.rs:402`, `spartan-verifier/src/wrapper/zk_wrapped_channel.rs:204`).

**Marks**: **P** proved here; **D** read in the named source; **X** checked by exact computation in
`johnson-row/` (test named); **E** estimate (calculator model); **U** not confirmed.

**Provenance** (labels per result; `REFERENCES.md` Part 3 rows O-15 to O-19 and O-24; the
comparison behind the labels is section 9):

| Result | Label |
|---|---|
| F1' (list size 19) | **Published**: the Johnson bound, DKT26 Theorem 4.4 (38) second term, proof in Section B.2; width transfer DKT26 Corollary 6.4 |
| Lemma U (list state) | **Adapted** from the union over a fixed list in Haböck, proof of Lemma 5, and CFW26, proof of Lemma 6.6 (the same step, published); the general per-round form is ours |
| Lemma J1 | **Adapted**: Theorem 1 of `binius-extension-challenges.md` (itself adapted from DP24 Construction 3.1 / Theorem 3.5) with Lemma U |
| Lemma J2 (DKT26 route) | **Adapted**: the error shape (an MCA term plus the list size times the root count of a nonzero low-degree identity) and the proof pattern are CFW26 Lemma 6.6's; the round (Binius64's lerp mask fold of interleaved witness and mask rows, both orientations, the claim carried by the explained member) is not in CFW26 and is ours |
| Lemma J2' (Haböck route, `R = 1`) | **Adapted** from Haböck Theorem 4 (unused by the build) |
| Lemma J3 (lifting at the lifted level) and the counterexample | **Original as far as checked** (sources: 2024/1571, 2025/1015, 2024/504, 2024/1586, 2026/2056, 2026/391, 2026/2615 sections read, the Blueprint; [HMH] not available) |
| H8' and BR-1 to BR-5 | H8' is the referee's statement (R-5); the build requirements are ours |
| Lemma F, index rounds | **Published shape**: CFW26 Lemma 6.6's sumcheck rounds (rows of an interleaved word folded by a sumcheck challenge, error `eps_mca + Lambda eps_pil(C, 1, d_s)`); ours instantiates it for Binius64's index rounds with DKT26 as the MCA input |
| Lemma F, `X` folds | **Adapted** from Haböck Lemma 4 (Section 6.1): Theorem 4 replaced by DKT26 Theorem 4.4 / Corollary 6.6 / Lemma 3.3, the weighted-to-unweighted step written |
| Lemma UD | **Adapted**: Haböck's chain of Sections 5 / 6.1 with WHIR Lemma 4.10 + BCIKS20 Theorem 4.1 as the line statement, DKT26 Lemma 6.5 for width |
| Lemma K (knowledge) | **Adapted**: extraction by list decoding the committed words is WHIR Theorem 7.5's (extraction time `et_RS`) and, by DKT26 Section 1.1, that of FRI [BGKTTZ23] and STIR; the knowledge state function with its initial state set to 0 follows CMS19 Definitions 8.3, 8.5; ours: its application to system B with the lifted list |
| The rows of section 8 | **Original** (parameter choice), terms from the cited statements |

---

## 2. Setting and the list state

### 2.1 The protocol as built, in rounds

`K = GF(2^256)` (every challenge), `L = GF(2^128)` (the trace in the mixed variant), rate `rho = 1/8`.
Binius64 as built (Blueprint 4, 5.5, 6, 7; `binius-extension-challenges.md` 1, 4.2):

1. **Commitments.** Round oracles `M_r`, `r < R` (leaf: `R = 2`, the trace oracle and the wrapper
   oracle; node: `R = 1`), each the merge of its constituents (Blueprint 7.2 "Round merging"); for
   the zero-knowledge leaf each is committed interleaved with a mask `omega_r` of the same length.
   Oracle `r` has level `l_r` (codeword `Enc_{l_r}(M_r)` on `E_{l_r}`, `|E_{l_r}| = 2^{l_r} / rho`).
2. **PIOP rounds.** Zerocheck, sumcheck, univariate skip, batching, shift, public-input check, the
   wrapper's IronSpartan rounds: each a challenge whose bad set, for a fixed oracle message, has
   at most `d_i |K|^{-1}`-mass by Schwartz-Zippel (`binius-extension-challenges.md` 4.2 table).
3. **Ring switch** (form T), twice (trace, public input): `r''` in `K^8`.
4. **Opening** (Protocol 7.1): claim batching `alpha` over `J` claims (with `mu`); the mask claim
   `s'`; the mask fold `gamma`; BaseFold on the concatenation `G(X, Z)` of the ZeroPadMSB lifts of
   the folded oracles to the common level `l = max l_r`: `o = ceil(log2 R)` index rounds (fold over
   `Z`, i.e. over rows of the interleaved word) then `l` folds over `X`, each a sumcheck round of
   degree 2 coupled with a fold (committed or virtual; the vendored FRI parameters fold several
   variables per committed oracle, `fri/common.rs` `fold_arities`, each variable still its own
   sumcheck round); the terminal codeword of dimension `2^log_terminal_dim` in the clear
   (`fri/common.rs:137`, chosen by `optimal_for_batch`); queries.

### 2.2 Notation, the list bound, the line statement

`C_l = RS[K, E_l, 2^l]`. For a tuple of words `W = (w_1, ..., w_s)` over `E_l` (an interleaved word,
width `s`) and `A = ceil(a |E_l|)`, the **joint list** `Lambda(W)` is the set of codeword tuples in
`C_l^s` that agree with all rows on a common set of at least `A` positions. Thresholds: Johnson
`a = (1 + 1/(2m)) sqrt(rho)`, `m >= 3`; unique decoding `a = (1 + rho)/2`. `t = m + 1/2`. The degree
bound is `D = k - 1`.

**F1' (list bound; D, P for the uniformity in `n`).** `|Lambda(W)| <= B_list` with
`B_list = floor((a - rho)/(a^2 - rho))` in the Johnson regime (`19` at `m = 10`, `rho = 1/8`; `6` at
`m = 3`) and `1` in unique decoding. Source: DKT26 Theorem 4.4, bound (38), second term
`n (A - D)/(A^2 - n D)`, whose proof (end of Section B.2, read) is the pairwise Cauchy-Schwarz count:
`L` candidates with `A`-sets whose pairwise intersections have at most `D` points satisfy
`L^2 A^2 / n <= L A + L (L - 1) D`. It needs only that two distinct candidates agree on at most `D`
common positions, which holds for codeword tuples of any width (they differ in some row), so it
holds for interleaved words directly (also DKT26 Corollary 6.4). *Uniformity (P)*: `n (A - D)/(A^2 - n D)`
is decreasing in `A` (its derivative has the sign of `-(A - D)^2 - D (n - D)`) and increasing in `D`
(sign of `A (n - A)`), so with `A >= a n` and `D < rho n` it is below `(a - rho)/(a^2 - rho)` at every
`n`. **X** `test_rowcalc.test_list_size_is_the_johnson_bound_19` (every `n = 2^4 .. 2^31`).
Revision 1 used the Guruswami-Sudan `Y`-degree `(m + 1/2)/sqrt(rho) = 29.70`: valid, looser.

**F2 (line MCA with full agreement sets; D).** For a line `u + z v` of interleaved words of any
width over `E` (`|E| = n`), there is a set `Exc` of challenges, `|Exc| <= N_line(n)`, depending only
on the line, such that for `z` outside `Exc` every codeword tuple `P` with `|S_z(P)| >= A` is
`F_0 + z G_0` with `(F_0, G_0)` a codeword pair and `S_z(P)` equal to the common agreement set of
`(F_0, G_0)` with `(u, v)`.

- Johnson, message dimension `k >= 2`: `N_line(n) = B_cf < 8 n t^3 / (3 rho_-)`, `rho_- = D/n`:
  DKT26 Theorem 4.4 (scalar; hypotheses `1 <= D <= n - 2`, distinct points, any field, the theorem's
  own `m` at most ours, so the count with our `t` is an upper bound: C-14 and the referee's 2.1),
  Lemma 6.5 and Corollary 6.6 (width independent, challenge uniform in the code's field, `A >= k`).
- Johnson or unique decoding, message dimension `k = 1` (constant code): `N_line(n) <=
  floor(C(n, 2)/(A - 1))` (`A >= 2`): DKT26 Lemma 3.3 (proof read: two positions with different
  coefficient tuples collide at at most one challenge of a line, and a bad constant at a challenge
  needs at least `A - 1` collision pairs, disjoint across constants), then Corollary 6.6 for width.
- Unique decoding: `N_line(n) = n`: WHIR Lemma 4.10 (D, any linear code: a proximity generator
  has MCA up to `min(1 - delta_C / 2, B)` with the same error) with BCIKS20 Theorem 4.1 as the
  proximity generator on any evaluation set (D; `binius-extension-challenges.md` Theorem 5). WHIR's
  Corollary 4.11 states the same for its smooth domains only (Definition 4.1 restricts the paper to
  smooth `L`), so it is not cited for our domain. Width: DKT26 Lemma 6.5.

**Remark Q (the subset form suffices; P).** WHIR's Definition 4.9 and CFW26's Definition 3.19 state
MCA in a subset form: outside the bad challenges, if `u + z v` agrees with a codeword on a set `S`
of size at least `A`, then `u` and `v` each agree with codewords on `S`. Applied to `S = S_z(P)`,
with `A >= k` (so codewords are determined by `S`), it gives `q_0, q_1` with `(u, v) = (q_0, q_1)` on
`S` and `P = q_0 + z q_1` there, hence everywhere; and the common agreement set `S(q_0, q_1)`
contains `S` and is contained in `S_z(P)` (where both rows agree, the combination agrees). So the
subset form at threshold `A >= k` **is** F2's full-agreement-set form, as DKT26 notes at the start
of Section 6. Every proof below uses only F2, so any source of the subset form serves.

The binary additive code of Binius64 is a Reed-Solomon code on a `GF(2)`-subspace (Haböck 6.2), so
F1' and F2 apply: no hypothesis restricts the characteristic or the domain. The challenge is uniform
in `K`, the code's field, also for the `L`-valued first oracle (`binius-extension-challenges.md`
Lemma 3).

### 2.3 The list state

**Lemma U (P).** Let a round with challenge `c` follow commitments `W` (all oracles committed so
far, lifted to the common level, section 5). Suppose that for every fixed tuple of codewords `y`
the round has a state function `St(y, .)` with round-by-round error `eps` (the PIOP's own
analysis with `y` as the oracles). Define `St_Lambda(tau) = 1` ("not doomed") iff some `y` in
`Lambda(W)` has `St(y, tau) = 1`. Then `St_Lambda` has round-by-round error at most
`|Lambda(W)| eps <= B_list eps`; a prover message that commits a further oracle `W'` cannot turn a
doomed `St_Lambda` into a non-doomed one.

*Proof.* `Lambda(W)` is a function of the committed words, fixed before `c`. If `St_Lambda` is
doomed before `c`, every `y` in the list is doomed, and `c` makes some `y` non-doomed with
probability at most `|Lambda| eps` by the union bound. For a new oracle: a member of
`Lambda(W, W')` restricts to a member of `Lambda(W)`, so a non-doomed state after the message gives
a non-doomed state before it. ∎

The referee confirmed (3.1) that the union is per partial transcript, so prover adaptivity costs
nothing (CMS19 Definition 8.4 bounds each doomed partial transcript). Threshold strictness:
Haböck's (20), (34) use `d < theta` while his lemmas conclude `>= 1 - theta`; with `A = ceil(a n)`
the list contains both, so the mismatch is harmless. The opening's states are Haböck's languages
(25), (31), (35) with "`theta`-close" read as "in `Lambda`". **Where the list size enters**: as a
factor on every round analysed per fixed oracle (PIOP rounds, ring switch, claim batching), and as
the root count per list element in the rounds analysed by F2 (sections 4, 5). It does not enter the
query round.

---

## 3. L-J1: the eq-weighted ring switch in the list regime

**Hypotheses.** H1: form T as in `binius-extension-challenges.md` 3.1 (`GF(2) < L < K`, packing
basis `beta_i` of `L`, `K`-basis `gamma_j` extending it, `r''` in `K^8`). H2: the oracle `pi` read by
the claim is the low block of the trace oracle's row in a list member (section 5); the claim's point
is drawn after the commitment. H3: the list `Lambda` is fixed before `r''`.

**Descent in the list regime (P).** Every list member's trace row is `L`-valued: its agreement with
the `L`-valued committed row is at least `A >= sqrt(rho) n > k` points, so Lemma 4 of
`binius-extension-challenges.md` applies (interpolation over `L` through `k + 1` points of `E`
inside `L`). The descent is row by row and concerns the `M` row of a committed pair `(M_0, omega_0)`;
the mask row `omega_0` is `K`-valued and needs none (referee 3.2). Hence every member has bits
`w_y(i, .)`.

**State function.** Before `s_hat`: not doomed iff some `y` in `Lambda` satisfies the claim. After
`s_hat` and the check `t = sum_i a(i) s_hat_i`: not doomed iff some `y` satisfies the claim and
`s_hat = s*(y)`. After `r''`: not doomed iff some `y` satisfies the output query
`sum_y pi_y(y) t_rs(y) = s_rs` (and every query collected before).

**Lemma J1 (P).** Under H1 to H3 the ring switch has round-by-round error at most
`B_list kappa_K / |K| = 8 B_list / |K|` (at `m = 10`: 248.75 bits; unique decoding 253.00 bits).

*Proof.* If the state after the check is doomed, every `y` in `Lambda` has `s_hat != s*(y)`. For each
such `y`, Theorem 1 of `binius-extension-challenges.md` (the residual `sum_j e_j c_j` is a nonzero
8-variate multilinear over `K` at `r''`; Schwartz-Zippel; DP24's step in the proof of Theorem 3.5)
bounds the probability that `y`'s output query holds by `8 / |K|`. Lemma U gives the union. The
prover message `s_hat` cannot un-doom: the check fixes it. ∎

**X** `johnson-row/test_ring_switch_list.py` (T-J1-list): descent exhaustive over all 65,536
codewords of `RS[GF(256), GF(16), 2]` for an `L`-valued row with two list members; then, in
`GF(2) < GF(4) < GF(16)`, a committed `L`-valued row whose list over `K` has two members, both
descending to `L`, a claim false for both, and for 134 prover messages the set of `r''` at which some
member's output query holds, computed from the output query itself: at most 32 per member, at most
64 in all, and up to 60 (the factor `B_list` is real).

---

## 4. L-J2: the zero-knowledge mask round in the list regime

### 4.1 Statement and proof (DKT26 route)

**Hypotheses.** H4: after claim batching the claim is `sum_r <M_r, T_r> = s` (merged oracles, lifted
operands `T_r`, Blueprint Protocol 7.1 step 1), each `M_r` committed interleaved with `omega_r` (any
words: soundness does not use how the masks are sampled). H5: the prover sends `s'` before `gamma`.
H6: lifted level fixed in advance (section 5). Orientation: Blueprint `lerp(gamma, M, omega) =
M + gamma (M + omega)` (characteristic 2) with target `s + gamma (s + s')`; Diamond (ePrint
2025/1015, Construction 4.1 step 4) `gamma M + omega` with target `gamma s + s'`.

**State.** Before `gamma`: not doomed iff some `(c^M_r, c^omega_r)_r` in `Lambda((U_r, V_r)_r)`
(width `2R`; `U_r, V_r` the lifted rows) has `sum_r <msg(c^M_r), T_r> = s`. After: not doomed iff
some `(p_r)_r` in `Lambda((G_r^gamma)_r)` (width `R`) satisfies the folded claim, which is Haböck's
language (9)/(34) for the folded tuple: the mask round's output is the hypothesis of the next round.

**Lemma J2 (P, using F1', F2).** The mask round has round-by-round error at most
`(N_line(|E_l|) + B_list) / |K|`, in both orientations. **The term `B_list / |K|` is the claim term**:
one root per list member.

*Proof.* Lerp: the folded tuple is the line `u + gamma v`, `u = (U_r)_r`, `v = (U_r + V_r)_r`.
Diamond: `u = (V_r)_r`, `v = (U_r)_r`. Let `Exc` be F2's exceptional set of this line (width `R`); it
depends only on committed words. Fix `gamma` outside `Exc` with a non-doomed state after the fold:
there is `P` in `Lambda(G^gamma)` satisfying the folded claim. By F2, `P = F_0 + gamma G_0` with
`(F_0, G_0)` agreeing with `(u, v)` on `S_gamma(P)`. Then `y = (F_0, F_0 + G_0)` (lerp) or
`y = (G_0, F_0)` (Diamond) is in `Lambda((U, V))` with the same agreement set, and `msg` is
`K`-linear, so the folded claim reads `phi_y(gamma) = 0` with

- lerp: `phi_y(Z) = (sum <msg F_0, T> + s) + Z (sum <msg G_0, T> + s + s')`,
- Diamond: `phi_y(Z) = (sum <msg F_0, T> + s') + Z (sum <msg G_0, T> + s)`.

Doomed before means `sum_r <msg c^M_r, T_r> != s` for every list member: the constant term (lerp) or
the `Z`-coefficient (Diamond) of `phi_y` is nonzero, so `phi_y` has at most one root, fixed before
`gamma` (`s'` is). The good `gamma` lie in `Exc` or among at most `|Lambda((U,V))| <= B_list`
roots. ∎

Values: leaf `|E_l| = 2^22`, `m = 10`: 219.41 bits; unique decoding `(2^22 + 1)/|K|`: 234.00 bits.
The mask round is only in the zero-knowledge leaf. The referee checked the algebra in both
orientations and that analysing the fold on lifted rows equals the Blueprint's fold-then-lift
(Dup is linear; referee 3.3).

**Excluded challenges.** For soundness none: the bad set is `Exc` and at most `B_list` roots. For
zero knowledge the lerp orientation excludes `gamma = 0` and Diamond's none (C-5; Diamond Theorem 4.3,
D); the vendored prover stops on `gamma = 0` (`VENDOR.md` change 5).

**X** `johnson-row/test_mask_round.py` (T-J2-list): `K = GF(256)`, 16 points, `k = 2`, `A = 7`; rows
agreeing with two codeword tuples on disjoint 7-sets, a false claim for every list member, `s'` and
the mask parts chosen so that `phi_{y1}`, `phi_{y2}` have roots at chosen challenges. In every
doomed instance every good `gamma` outside `Exc` is a root of some `phi_y` and `|S \ Exc| <=
|Lambda|`; `|S \ Exc| = 2` is attained in both orientations (the claim term is exercised). Unique
decoding: `|Exc| <= n` with planted cancellations, and a close word with a false claim has at most
one good challenge outside `Exc`.

### 4.2 Haböck's route (not available for the build)

**Lemma J2' (P for `R = 1`).** With one oracle the mask round has round-by-round error at most
`eps(C_l, 1, 1, theta)` of Haböck's Theorem 4 (unweighted, Remark 5), with no root term (the
identity in `Z` given by Theorem 4 carries the claim at `Z = 0`, lerp, or in the `Z`-coefficient,
Diamond). *Proof* as in revision 1 (the referee confirmed it, 3.4).

**`R = 1` never occurs in the build** (the leaf masks `R = 2` round oracles; nodes are unmasked), so
on this route the leaf's mask round rests on G-1 and G-6, and on G-3 through Theorem 4's proof.

### 4.3 Gap G-1 (Haböck route only; the leaf's mask round only)

For `R >= 2`, Lemma J2' needs Theorem 4 for the interleaved code `C_l^R` with the challenge in `K`
and a constraint `K`-linear across rows. Identifying `C_l^R` with a Reed-Solomon code over a
degree-`R` extension `K'` (Haböck, proof of Lemma 5) makes the challenges range over the subfield
`K` and the constraint not `K'`-linear. **G-1**: BCIKS20's Propositions 5.5 and Section 6.2
(Haböck's Propositions 1, 2) and the weighted step of "[BCI+20, Section 7]" hold for an arbitrary
subset `S` of the field. The leaf's **index round** is not affected: after the mask fold the `R = 2`
rows are folded into one by a line of scalar words, where Theorem 4 with `M = 1` applies directly
(referee 2.4 (c)); G-1 would arise for index rounds only if `R > 2`. **Fallback F-J2**: batch the
leaf's `2R` rows by powers of one challenge (Haböck Protocol 2 step 0, Lemma 1 with `M = 2R - 1`, D);
it removes G-1, not G-3 or G-6.

---

## 5. L-J3: lifted oracles, H8' and what the build must do

### 5.1 Lifting

Blueprint 5.3: a smaller oracle's codeword is read at the common level `l` as
`Dup_{l - n}(Enc_n(pi))`, with completeness from identity (8), `Enc_l(ZeroPadMSB(pi)) =
Dup(Enc_n(pi))` (Theorem 5.1, D); the Blueprint defers soundness to [HMH] (not available).

**Hypotheses.**

- **H7**: the level `l` at which each oracle is opened is a public function of the statement's
  shape, fixed before the first commitment.
- **H8'** (replaces revision 1's H8; the referee's statement, R-5): **a commitment binds a list,
  not a message.** (a) Within a proof, every claim on a commitment is discharged by the one batched
  opening of that proof, which covers every commitment of the proof; (b) no statement of the system
  relies on two openings of one commitment (in one proof or in two) denoting the same message.

Why H8' and not H8: in the list regime two separate openings of one commitment, at the same level
or not, can be satisfied by **different** members of its list. No consistency check on query
answers detects this: both members agree with the one committed word on the queried points they
use, and the answers are that word's values. Only batching the claims into one opening forces one
member to satisfy all of them (the claim-batching round, Lemma U: `B_list (J - 1)/|K|`).

**Lemma J3 (P).** Under H7 and H8', define every round's state on the lifted words `Dup(f_r)` (in
`K^{E_l}`) and their joint list at level `l`. Then every statement of sections 2 to 4, 5.4, 7 and
Haböck's Lemmas 1 to 4 (with Section 5.4) holds for the lifted words with the same errors; the
initial state is fixed when the `f_r` are committed; and every claim on a commitment is a claim on
one and the same list member, the one the batched opening's state selects. No statement relating
the proximity of `Dup(f)` to that of `f` is used.

*Proof.* (i) The verifier's emulated access (a query at `e` in `E_l` answered from `f` at the image
index, Blueprint 5.3) is by definition oracle access to the word `Dup(f)`. (ii) The cited analyses
treat each committed word as an arbitrary function from the domain to the field: Haböck's languages
(25), (31), (35), Lemmas 1 to 4 and Lemma 3's query count use only the values of the words at the
domain points and the uniform choice of query points; Lemmas U, J1, J2, F, K use the list of the
committed tuple. Uniform `e` in `E_l` is the query distribution of those analyses. (iii) By H7 the
level, hence `Dup(f)` and its list, is a function of the commitment and the shape alone. (iv) By
H8' (a) all claims on all commitments of the proof enter one claim-batching round followed by one
opening; the state before that round is "some member `y` of the joint list of all commitments
satisfies every claim", and Lemma U bounds the probability of passing the batching round from a
state where each member fails some claim. So a single member answers for every claim of the
proof. By H8' (b) no conclusion outside the proof is drawn from a second opening, so no second
member can be needed. (v) The claim operands are lifted, `T^(up)(X_low, X_high) = T(X_low)
eq(0, X_high)` (Blueprint (7)), so a claim on a member reads only its low block, a full message of
the original length; the witness is that block, whichever codeword of `C_l` the member is. ∎

If H7 failed, the fallback is not an unlifted opening: let the state be "some level `l'` in the
allowed set and some `y` in `Lambda_{l'}`"; only the list-factor terms grow, by the number of
levels (at most 32, 5 bits), and they keep more than 85 bits of slack (referee 3.6).

**Why the lift-level list is necessary (X).** `johnson-row/test_lifted.py` (revision 1, kept): a
level-`l` codeword that is not a lift agrees with `Dup(f)` on half the points while `f` is outside its
own Johnson list. `johnson-row/test_lifted_opening.py` (T-J3, new): in a lifted toy opening the
lifted joint list has two non-lift members while `f` has no level-`n` candidate; the extractor of
Lemma K succeeds at the lifted level and a level-`n` decoder finds nothing.

### 5.2 H7 in the build

`l_r` is "the least variable count that accommodates the constituents and the pad" and `l = max_r
l_r` (Blueprint 7.2): shape functions (referee 3.6). In the vendored code the lift of oracle `index`
is `fri_params.input_oracles()[index].log_lift` (`iop/src/basefold/channel.rs:116-119`), with the
FRI parameters precomputed from the schedule's oracle specs (`optimal_for_batch`,
`iop/src/fri/common.rs:191`).

### 5.3 Build requirements on `yugen-proof-b2` (from H7 and H8')

Paths are under `yugen-proof-b2/vendor/binius64/crates/`. Each requirement has a check an engineer
can run.

| # | Requirement | As vendored | Check (acceptance) |
|---|---|---|---|
| BR-1 | **One opening per proof covering every commitment.** Every round-oracle commitment received by a proof's verifier is opened in exactly one batched BaseFold opening of that proof | `BaseFoldVerifierChannel::finish(self)` (`iop/src/basefold/channel.rs:158`) consumes the channel and calls `verify_batch_zk_basefold` once over all `oracle_commitments`; `assert!(n_remaining == 0)` (line 160) refuses an unfinished schedule. Callers: `verifier/src/verify.rs:510`, `verifier/src/zk_config.rs:317`, `spartan-verifier/src/lib.rs:402`; the zero-knowledge wrapper forwards to the inner channel's `finish` (`spartan-verifier/src/wrapper/zk_wrapped_channel.rs:204`) | a test-only counter in `verify_batch_zk_basefold`: verifying one transparent leaf proof, one zero-knowledge leaf proof and one node proof each increments it exactly once, and the slice it receives has as many commitments as `recv_oracle` calls of that proof |
| BR-2 | **Every claim on a committed oracle goes into that opening.** No claim on a round oracle is checked outside the queued relations | claims are queued by `verify_multi_oracle_relation` and processed in `finish` (`channel.rs:150-155`); when no relation is queued, `finish` opens nothing (`channel.rs:174`) | (a) no call path outside `iop/src/basefold/` and `iop/src/fri/` decommits a round-oracle commitment (code search, recorded in the review); (b) a test that every oracle index received by a leaf and a node verifier appears in at least one queued relation, so no commitment of a proof is left unopened |
| BR-3 | **No commitment shared across proofs.** Every commitment a verifier uses is read from that proof's own tape; no API takes a round-oracle root from outside the proof | the trace and pad roots are read from the tape before the first challenge (`docs/transcript-binding.md`, rows "Witness (trace) commitment" and "pad (precommit) oracle"); the pad oracle is committed per proof at construction | a test: a leaf proof whose pad or trace root is replaced by another valid proof's root is refused; a review note that no Yugen statement compares commitment roots of two proofs (cross-proof relations are expressed through public inputs only) |
| BR-4 | **Levels from the shape (H7).** `log_lift` of every oracle is computed by the verifier from the constraint system, never read from the proof | `channel.rs:116-119`, `fri/common.rs:191` | a unit test: two different witnesses for one circuit give identical `FRIParams` (same `log_lift` vector, same `log_terminal_dim`) on the verifier side, computed before the proof is read |
| BR-5 | **Recursion keeps BR-1 to BR-4.** The in-circuit verifier of a leaf proof performs one opening per verified proof, over that proof's commitments | `recursion/src/zk.rs` (one recorded zero-knowledge verification per slot, `VENDOR.md` change 12) | the BR-1 counter, or an equivalent gate census, on the recursion circuit: one opening per slot |

If a future change needs two openings of one commitment (for example a precommitment reused
across statements, Blueprint 6), the requirement is to batch both openings' claims into one opening
with a fresh challenge; a second, separate opening is not sound in the list regime under the
analysis here, and a unique-decoding parameter for one of the two openings does not repair it (a
unique-decoding member and a Johnson-radius member can both agree with the committed word).

### 5.4 The index rounds and the fold rounds: Lemma F

The concatenation `G(X, Z)` (Blueprint 5.4 step 2, Protocol 7.1 step 4) is an interleaved word of
`R` rows over `E_l`; BaseFold binds `Z` first, so each index round folds pairs of rows with `zeta_j`,
a sumcheck round of degree 2. The `X` folds fold the even and odd parts of the additive FFT (Haböck
6.2, equation (36): `p(X) = p_e(W(X)) + X p_o(W(X))` with `W` the first subspace polynomial; the
fold map `pi : D_{i-1} -> D_i` is two-to-one).

**Setting (Haböck Section 5.2, read).** Round `i` has the consistency measure `mu_i` on `D_i` with
density `delta_i` in `[0, 1]` ((29), (30)); `mu*_{i-1}` is the projection of `mu_{i-1}` onto `D_i`,
`mu*_{i-1}(B) = mu_{i-1}(pi^{-1}(B))`, again of density at most 1. `mu*_{i-1}` is built from
`f_0, ..., f_{i-1}` and `lambda_1, ..., lambda_{i-1}`, so it is fixed before `lambda_i` (only `mu_i`
uses the post-challenge `f_i`, (30)). The state before round `i` is Haböck's language (35):
some `p_{i-1}` with `agree_{mu_{i-1}}(f_{i-1}, p_{i-1}) >= 1 - theta` that is sumcheck compliant.
Sumcheck compliance of `p_i` after the round is `Gamma_i(p_i, lambda_i) = 0`, `Gamma_i(p, z) =
<P, R(lambda_1, ..., lambda_{i-1}, z, .)> - q_{i-1}(z)` (Haböck, proof of Lemma 4), of total degree 2.

**Lemma F (P, using F1', F2).** A sumcheck-coupled fold round (an index round over rows, or an `X`
fold over even and odd parts on the half domain `D_i`) has round-by-round error at most
`(N_line(n_i) + 2 B_list) / |K|`, `n_i` the length of the words on the line (`|E_l|` for index
rounds, `|D_i| = |E_l| / 2^i` for the `i`-th `X` fold). At a level of message dimension 1,
`N_line(n_i) = floor(C(n_i, 2)/(A_i - 1))` (DKT26 Lemma 3.3).

*Proof.* Write the pair as `(f_{i-1,0}, f_{i-1,1})` (two rows, or the even and odd parts) and the line
`u + lambda v`, `u = f_{i-1,0}`, `v = f_{i-1,0} + f_{i-1,1}` (characteristic 2), so that the fold is
`(1 - lambda) f_{i-1,0} + lambda f_{i-1,1}`. Let `Exc` be F2's exceptional set of this line at
threshold `A_i = ceil((1 - theta) |D_i|)`; it depends only on `f_{i-1}`. Let `Lambda_i` be the
unweighted joint list of `(f_{i-1,0}, f_{i-1,1})` at `A_i`; it is fixed before `lambda_i` and has at
most `B_list` members (F1').

1. *A post-challenge proximate.* Suppose the state after `lambda = lambda_i` is not doomed: there
   are a prover answer `(f_i, q_i)` and a compliant `p_i` with `agree_{mu_i}(f_i, p_i) >= 1 - theta`.
   Let `A'` be the subset of `{f_i = p_i}` where `delta_i > 0`; there the last fold check holds, so the
   combination `(1 - lambda) f_{i-1,0} + lambda f_{i-1,1}` equals `p_i` on `A'`, and
   `mu*_{i-1}(A') = mu_i(A') = mu_i({f_i = p_i}) >= 1 - theta` (Haböck, proof of Lemma 2; for a
   virtual fold `delta_i = delta*_{i-1}` and the same holds).
2. *Weighted to unweighted (R-3).* `mu*_{i-1}` has density at most 1, so
   `|A'| / |D_i| >= mu*_{i-1}(A') >= 1 - theta`, hence `|A'| >= ceil((1 - theta) |D_i|) = A_i`. So the
   full agreement set `S = S_lambda(p_i)` of `p_i` with the combination has at least `A_i` points.
3. *MCA.* For `lambda` outside `Exc`, F2 gives `(q_0, q_1)` with `p_i = (1 - lambda) q_0 + lambda q_1`
   and `S(q_0, q_1) = S`: `(q_0, q_1)` is in `Lambda_i`, with the same agreement set. Its weighted
   joint agreement is `mu*_{i-1}(S) >= mu*_{i-1}(A') >= 1 - theta` (`A'` is inside `S`): this is why
   the full-set equality removes Haböck's weight denominator `B_i`.
4. *Back to the previous state.* Over `pi^{-1}(S)` (index round: `S` itself) `f_{i-1}` agrees with
   `p_{i-1} = q_0(W(X)) + X q_1(W(X))` (index round: the row pair), and
   `agree_{mu_{i-1}}(f_{i-1}, p_{i-1}) >= mu_{i-1}(pi^{-1}(S)) = mu*_{i-1}(S) >= 1 - theta`. If
   `phi_y(Z) = Gamma_i((1 - Z) q_0 + Z q_1, Z)` were identically zero, then `Gamma_i(q_0, 0) =
   Gamma_i(q_1, 1) = 0`, and `p_{i-1}` would be compliant (Haböck's computation at the end of the
   proof of Lemma 4), so the state before the round would not be doomed.
5. *Count.* So if the state before is doomed, every member `y` of `Lambda_i` whose weighted joint
   agreement `mu*_{i-1}(S(y))` is at least `1 - theta` has `phi_y` nonzero (step 4); a member of lower
   weighted agreement may have `phi_y = 0`, but it is never the explaining member of step 3, whose
   weighted agreement is at least `1 - theta`. Each `phi_y` has degree at most 2 and is fixed before
   `lambda` (`q_{i-1}` is sent before it). A good `lambda` outside `Exc` has an explaining member `y`,
   and `phi_y(lambda) = Gamma_i(p_i, lambda) = 0` with `phi_y` nonzero; so the good `lambda` lie in `Exc`
   or among the roots of the nonzero `phi_y` of the members that can explain, at most
   `2 |Lambda_i| <= 2 B_list` of them. ∎ (Wording corrected in revision 2.1, second referee W-1; no
   number changes.)

**Levels of message dimension 1 (R-4).** DKT26 Theorem 4.4 needs `D >= 1`. If the vendored
parameters choose `log_terminal_dim = 0` (`fri/common.rs:137`), the last committed fold reaches
message dimension 1 and Lemma 3.3 gives its exceptional count (at that level `n_i = 1/rho = 8`,
`A_i = 3` at `m = 10`: 14 challenges); if `log_terminal_dim >= 1`, the folds below the terminal
codeword are checked exactly against the codeword sent in the clear and need no proximity step.
Either way the numbers are unaffected.

**X** `johnson-row/test_fold_round.py` (T-F): an index round on `GF(256)`, 16 points, `A = 7`, rows
agreeing with two codeword pairs on disjoint 7-sets, a round polynomial `h` fixed before `lambda`
with three planted roots, every member's claim false: every good `lambda` outside `Exc` is a root of
some `phi_y`, `|S \ Exc| <= 2 |Lambda|`, and `|S \ Exc| = 4 = 2 |Lambda|` is attained.
`johnson-row/test_lifted_opening.py` (T-J3) runs the index round and an `X` fold that ends at
message dimension 1 inside a lifted opening; in that chain the fold's pair list is empty, so the
step is vacuous there (second referee 2.2). Revision 2.1 adds `test_5_x_fold_at_dimension_one`
(condition C-5): a fold at message dimension 1 (`n = 8`, constant code, `A = 4`) with two pair-list
members in a doomed instance and three planted roots; run: 40 of 40 instances doomed, `|E| = 1`
against Lemma 3.3's 9, `|S \ Exc| = 3` or `4 > |Lambda| = 2` in all 40, every good `lambda`
outside `Exc` a root of a member's `phi_y`.

Haböck's route for the same rounds: `eps(C_i, 1, B_i, theta)` (Lemma 4, D), subject to G-3 and G-6
(section 10).

---

## 6. Unique decoding, written out (C-12)

Take `a = (1 + rho)/2`, so `B_list = 1`. The states are Haböck's languages with "the unique close
codeword" (2024/1571 Sections 5, 6.1; "carries over verbatim to the unique decoding regime, with the
adapted soundness errors", Section 3 after (9); D).

**Lemma UD (P).** In the unique-decoding regime the round-by-round errors of system B as built are:

| Round | Error | Proof |
|---|---|---|
| PIOP round with Schwartz-Zippel count `d_i` | `d_i / |K|` | Lemma U with `B_list = 1` |
| Ring switch (each) | `8 / |K|` (form T), `7 / |K|` (form F) | Lemma J1 (Theorems 1, 2 of `binius-extension-challenges.md`) |
| Claim batching `alpha`, `mu` | `(J - 1) / |K|` | Schwartz-Zippel, Lemma U |
| Mask fold `gamma` (leaf) | `(|E_l| + 1) / |K|` | Lemma J2 with `N_line(n) = n` |
| Index round `j` | `(|E_l| + 2) / |K|` | Lemma F |
| `X` fold `i` (`i = 1..l`) | `(|E_l| / 2^i + 2) / |K|` | Lemma F |
| Query phase, `s` queries | `((1 + rho) / 2)^s` | Haböck Lemma 3 at `theta = (1 - rho)/2`; DP24 Proposition 4.24 gives the same base |

`N_line(n) = n`: WHIR Lemma 4.10 (read: any linear code; the error of the proximity generator
carries over) with BCIKS20 Theorem 4.1 (any evaluation set; `binius-extension-challenges.md`
Theorem 5, D); width by DKT26 Lemma 6.5. The referee's robustness note stands: DKT26 Theorem 4.4 at
`m = 3` gives the same rounds 216.2 bits, and the direct weighted argument of revision 1 (kept in git
history, commit `5cec7e5`, section 6) is a third route. Against the calculator
(`binius64.rounds_counted`): mask `n + 1` and index `n + 2` are reproduced exactly; the calculator's
fold term is on the full domain, ours on the half domain, so the calculator is one bit conservative
(225.00 against 226.00 at a node of `2^31` points; confirmed by the referee). **The 184-query row is
unchanged and has a complete round-by-round source.**

---

## 7. Knowledge soundness in the list regime (G-4, R-9)

A shielded pool needs knowledge: the statement "a preimage of a key exists" is true for every key,
so soundness says nothing; the spend must be extractable.

### 7.1 The notion and the compile theorem

**Definition (CMS19 Definition 8.5, D; per-round errors as in SG26 Definition 2.20, D).** An IOP for
`R` has round-by-round knowledge errors `(kappa_i)` if there are a polynomial-time extractor `E` and a
state function `St` (CMS19 Definition 8.3: 0 on the empty transcript, never raised by a prover
message, 0 on a full transcript only if the verifier rejects) such that for every statement `x`,
round `i` and partial transcript `tr` with the verifier to move and `St(x, tr) = 0`: if
`Pr_c[St(x, tr || c) = 1] > kappa_i` then `(x, E(x, tr)) in R`. SG26 Lemma 2.21 states that under a
total order of messages this is equivalent to its Definition 2.20 (D, statement).

**Compile theorem used: SG26 Theorem 6.6 (2) (D, statement).** If a series-parallel IOP (SG26
Definition 2.18; a public-coin IOP with a total order is one) is round-by-round knowledge sound with
errors at most `eps_k`, its spBCS transformation (SG26 Protocol 6.5) is adaptively knowledge sound
(SG26 Definition H.3: an **online** extractor that answers the adversary's oracle queries and outputs
a witness, no rewinding) with oracle simulation error 0 and extraction error, in the QROM,
`2 sqrt(k_q / 2^(8 (b + e))) + 6 (t + k_q)^2 (eps_k + c' (t + k_q) / 2^(8 b))`. Hypotheses: the IOP's
extractor, the samplers and encodings run in polynomial time; the build uses spBCS (per-message
challenge streams with write-back, salted leaves; `../soundness/` revision 6 already evaluates
condition Q with this theorem for both systems). The alternative is CMS19 Theorem 8.6 (2)
(extraction probability `Omega(mu - t^2 k - t^3 / 2^lambda)`, CMS19's own BCS construction; for the
built transcripts through `qrom-compilation.md` Theorem Q (2), adapted, unreviewed).

### 7.2 Lemma K

**Lemma K (P, using Lemmas U, J1, J2, J3, F).** Under H7, H8' and F2, system B as built (sections 2
to 5) has round-by-round knowledge errors equal to its round-by-round soundness errors of sections 3
to 6 and 8 (`kappa_i = eps_i` for every round; the largest is the query round, `(1 - theta)^s`),
with the extractor

> `E(x, tr)`: from the first committed round oracle in `tr` (the trace oracle with its pad
> constituents), take the trace row `M_0` lifted to its level `l` (H7). Compute the complete list of
> codewords of `C_l` agreeing with `Dup(M_0)` on at least `A` points (DKT26 Corollary 9.4:
> deterministic, `O~(n log |K|)` bit operations above the Johnson radius in every characteristic;
> statement read, proof not read; the Guruswami-Sudan decoder is a second, classical choice, cited
> from memory). For each member (at most `B_list = 19`), read its low block (section 5.1 (v)),
> unpack the trace bits (descent, section 3) and evaluate the relation; output the first block that
> satisfies it, else `⊥`.

*Proof.* **State function.** `St^K(x, tr) = 0` for the empty transcript and for every transcript
that ends with, or before, the first commitment (so `St^K = 0` at the first point where the verifier
moves); afterwards `St^K = St_Lambda` of Lemma U, with the per-member states of the PIOP and the
opening as in sections 3 to 5, the final state being the verifier's decision after the queries.
Definition 8.3 holds: empty transcript 0; prover messages do not raise `St_Lambda` (Lemma U) and
the commitment message keeps 0 by definition; a full transcript with `St^K = 0` comes from a doomed
state before the query round, rejected except with `(1 - theta)^s` (Haböck Lemma 3), which is that
round's error.

**Rounds after the first.** If `St^K(x, tr) = 0` at a later round, then `St_Lambda(tr) = 0`, and by
the soundness analysis (Lemmas U, J1, J2, F, the query round) `Pr_c[St^K(x, tr || c) = 1] <= eps_i`
for **every** `x`, whether or not some member's block is a witness: those analyses bound the
reduced claims of the members, not the truth of the statement. So the condition of the definition
is vacuous there with `kappa_i = eps_i`.

**The first round.** Let `tr` end with the first commitment, `St^K(x, tr) = 0` by definition. The
first PIOP round's per-member state before its challenge is "the member's low block `w_y` satisfies
the PIOP's statement for `x`", which for the IOP for `R` is `(x, w_y) in R`. If no member's block is
a witness, every member is doomed and Lemma U gives `Pr_c[St^K = 1] <= B_list eps_0 = eps_0'`, the
first round's soundness error. Contrapositive: if `Pr_c[St^K(x, tr || c) = 1] > eps_0'`, some member
`y` of the joint list of the first round oracle has `(x, w_y) in R`. Its `M_0` row is in the scalar
list of `Dup(M_0)` (a joint member restricts to a member of each row's list), which `E` computes
completely, and `E` tests every member: `E(x, tr)` is a witness. `E` runs in polynomial time: one
list decoding of length `|E_l| <= 2^22` (leaf) and at most 19 relation checks.

**Lemma J3 is where the lifted level matters.** The list `E` decodes is the lifted word's list; T-J3
shows that a decoder at the oracle's own level can return nothing while the lifted list has members.
**H8'** makes the extracted block answer for every claim of the proof (5.1 (iv)). ∎

**Knowledge error and the rows.** `kappa_i = eps_i`, so the knowledge rows are the soundness rows of
section 8, and condition Q of `../soundness/` (revision 6, SG26 Theorem 6.6 (2) with `eps_k` the
largest per-round error) is unchanged by the regime: the largest per-round error is the query round
in both the 184-query row (`2^-152.73`) and the 107-query row (`2^-152.97`).

**How the list size enters knowledge.** Only through the per-round errors (a factor `B_list` on the
rounds analysed per fixed oracle, `B_list` or `2 B_list` roots in the line rounds) and the extractor's
running time (at most 19 candidates). There is no relaxation of the relation (unlike CFW26's relaxed
relations): the extracted block is an exact witness.

**What is not proved, exactly.** (1) F2 itself (DKT26, section 0.1). (2) The decoder's running
time: polynomial-time complete list decoding above Johnson in characteristic 2 is stated by DKT26
Corollary 9.4 (statement read) and is classical (Guruswami-Sudan, from memory, not re-read); only
polynomial time is needed. (3) SG26 Theorem 6.6 (2) applies to spBCS: the built transcripts must be
the spBCS form (the calculator's revision 6 assumes it; `yugen-proof-b2` must build it). (4) The
first PIOP round's per-member state equals `(x, w_y) in R`: true for an IOP for `R` whose oracle is
the witness's encoding; for Binius64 the relation is satisfaction of the constraint system by the
committed trace with the public words of `x` (`transcript-binding.md`), so the extracted trace
contains the spend witness. **Fallback that needs no DKT26**: the 184-query unique-decoding row with
the same Lemma K at `B_list = 1` (the extractor decodes uniquely); it costs 77 queries (568 against
362 KiB at the leaf, 7.82 M against 4.55 M leaf-slot AND rows) and still needs (2) to (4).

**A second extractor (noted, not used).** CFW26 Lemma 6.6 extracts straight-line from the
post-challenge witness: the pre-fold codewords are recovered by erasure correction on the folded
member's agreement set, with no list decoding (its Definition 3.4, after [BCFW25]). With F2's equal
agreement sets the same works here round by round; it is not needed because SG26 Theorem 6.6 (2)
takes CMS19-style extractors.

---

## 8. Rows and error tables

### 8.1 Inputs

Target per round: `e >= c + 1 + log2(20,000 x 601)`, `c = 128` (category 1) or `192` (category 3):
**152.52** and **216.52** bits (`soundness-method.md` 8.5b, 8.5d). Largest common level: leaf
`|E_l| <= 2^22`, node `|E_l| = 2^31` (a node of `2^30` AND rows, the calculator's largest opening).
Leaf: `R = 2`, one index round, mask round, `J = 4`. Node: one oracle, no mask. PIOP worst count 127
(univariate skip). No grinding; 256-bit digests (category 1).

### 8.2 Category 1 (`johnson-row/rowcalc.py`; bits = `256 - log2(count)`)

| Term | Formula (count of bad challenges) | UD | Johnson `m = 10`, DKT26 route |
|---|---|---|---|
| list size `B_list` | F1' | 1 | **19** |
| PIOP round (worst, skip) | `127 B_list` | 249.01 | 244.76 |
| ring switch (each) | `8 B_list` | 253.00 | 248.75 |
| claim batching | `3 B_list` | 254.42 | 250.17 |
| mask fold (leaf, `2^22`) | UD `n + 1`; DKT `B_cf(n) + B_list` | 234.00 | 219.41 |
| index round (leaf, `2^22`) | UD `n + 2`; DKT `B_cf(n) + 2 B_list` | 234.00 | 219.41 |
| first `X` fold, leaf (`2^21`) | UD `n/2 + 2`; DKT `B_cf(n/2) + 2 B_list` | 235.00 | 220.41 |
| first `X` fold, node (`2^30`) | as above | **226.00** | **211.41** |
| fold at message dimension 1 (if reached) | Lemma 3.3: `C(8, 2)/(A - 1) + 2 B_list` | (UD: 8 + 2) | 14 + 38: 250.3 |
| query, per query | UD `-log2((1 + rho)/2)`; Johnson `-log2((1 + 1/(2m)) sqrt(rho))` | 0.8301 | 1.4296 |
| queries for 152.52 | | **184** (152.73) | **107** (152.97) |

`B_cf(n) = 8 n t^3 / (3 rho_-)`, `rho_- = rho - 1/n` (DKT26 (39); the exact `E^(1)_ord` is smaller:
212.14 against 211.41 bits at `2^30`, referee 4.2). Each count less by one fails its target
(`test_each_count_less_by_one_fails`). For reference, Haböck's counts (not an available route):
mask/index 185.34, leaf fold 187.34, node fold 169.34.

Sizes (calculator `binius64.leaf_size`, `node_size`, `leaf_slot_rows`, mixed form T with W-1, E;
unchanged from revision 1, they depend on the query count only):

| Queries (rate) | Leaf KiB | Node KiB (`2^27` words) | Leaf slot AND rows |
|---|---|---|---|
| 184 (1/8) | 568 | 699 | 7.82 M |
| 107 (1/8) | 362 | 449 | 4.55 M |

Rate 1/16, DKT26 route, `m = 10`: 80 queries (154.37 bits), weakest 209.41 (node first fold at
`2^31`); sizes not computed here; twice the encoding and Merkle work (E). Revision 1's 77-query row
at `m = 38` had a 0.03-bit margin and is not kept.

### 8.3 Category 3 (384-bit digests; sizes not computed here)

| Row | Queries | Weakest | Meets 216.52 |
|---|---|---|---|
| UD, rate 1/8 | **261** (216.65) | 226.00 (node fold) | yes |
| UD, rate 1/4 | 320 | | yes |
| Johnson DKT26, `m = 3`, rate 1/8 | 170 (217.19) | 216.16 (node fold, `2^30`-point line) | **no**, by 0.36 bits; yes if every opening is at most `2^30` codeword points |

### 8.4 What the row needs from DKT26, and for the calculator

**Slack.** The binding term is the query round (152.97 against 152.52). The weakest algebraic round
is the node's first fold, `(N_line(2^30) + 2 B_list)/|K|`; it meets 152.52 bits for every
`N_line(2^30) <= 2^103.48` (`rowcalc.tolerated_exceptional_log2`); DKT26 (39) gives `2^44.6`, 58.9
bits below. The leaf's mask and index rounds need the same at `2^22`. So the row needs from DKT26
only the **qualitative** statement of section 0.1 (full-agreement-set, equivalently subset, line MCA
at the Johnson threshold, characteristic 2, any evaluation set, width independent, count below
`2^103.48` up to length `2^30`), and for levels of dimension 1 the elementary Lemma 3.3. Haböck's
correlated agreement (with a constraint, Theorems 3, 4) is not that form; even its `n^2`-type count
would fit (17 bits of slack), so on Haböck's route the obstruction is the proofs (G-1, G-3, G-6), not
the numbers. **Other sources of the qualitative statement** (identified through DKT26 Section 1.2,
not read, none in the reference folder): BCHKS, *On proximity gaps of Reed-Solomon codes*, STOC 2026,
pp. 1157-1167, full version ePrint 2025/2055, Theorem 4.6 (MCA above Johnson, `O(n/(q eta^5))`, every
characteristic, per DKT26); Haböck, *A note on mutual correlated agreement for Reed-Solomon codes*,
ePrint 2025/2110; Bordage, Chiesa, Guan, Manzur, *All polynomial generators preserve distance with
mutual correlated agreement*, ePrint 2025/2051. Task (closes G-2 without DKT26): the lead architect
adds BCHKS's full version to the reference folder; acceptance: its Theorem 4.6 is read and states
line MCA in the subset or full-set form at agreement `sqrt(rho_-) + eta_0`, for every characteristic
and any evaluation set, with a count that, evaluated at `n = 2^30`, `rho = 1/8`, `eta_0 = sqrt(rho)/20`,
is below `2^103.48`.

**For the calculator's next revision** (done in revision 8, `soundness/src/yugen_soundness/dkt26.py`;
it keeps `johnson.py` as the revision-5 record). Replace `binius64.johnson_bciks` by `rowcalc.terms` with
regime `"dkt"`: per round `count / |K|` with the formulas of 8.2; `B_list` = F1' multiplies every PIOP,
ring-switch and batching term; fold terms use the line length of the half domain; add the mask and
index terms at the full domain; keep the query term per regime. Acceptance: the calculator's tests
reproduce `johnson-row/test_rowcalc.py` (184 and 107 at category 1, 261 at category 3; weakest
226.00 and 211.41; list size 19; the category 3 Johnson row refused).

---

## 9. Provenance: what was compared

**CFW26 Theorem 6.3 / Lemma 6.6 (read: statement, construction, full proof of Lemma 6.6).**
Construction 6.4 is an IOR from an interleaved code `C^{≡2^k}` with a linear claim: the prover sends a
mask sum `mu~` (the sum of the sumcheck mask polynomial `U_{sigma,m}` of its Definition 6.1), the
verifier sends a combination challenge `epsilon`, then `k` sumcheck rounds fold the `2^k` rows of the
interleaved word with challenges `gamma_j` (the folded oracle is virtual). Lemma 6.6 bounds the
round-by-round **knowledge** errors at every `delta < delta(C)` (list regime included):
`Lambda(C^{≡2^k}, delta) eps_pil(C, 1, 2)` for `epsilon`, and
`eps_mca(C^{≡2^{k-j}}, delta) + Lambda(C^{≡2^{k-j+1}}, delta) eps_pil(C, 1, d_s)` for round `j`; the proof
(read) is: the MCA event (subset form, Definition 3.19), then a union over the fixed list of
pre-fold codewords of the event that a nonzero polynomial of degree below `d_s` vanishes at the
challenge; the extractor recovers pre-fold codewords by erasure correction on the agreement set.

- **Lemma F, index rounds**: the same round (rows of an interleaved word folded by a sumcheck
  challenge, degree-2 round polynomial, `d_s - 1 = 2` roots) and the same error and proof. Relabelled
  **Published shape (CFW26 Lemma 6.6)**, our instance with DKT26 as the MCA input.
- **Lemma F, `X` folds**: not in Construction 6.4 (which folds rows only; domain folding is
  elsewhere in CFW26, by code switching). Kept **Adapted** from Haböck Lemma 4.
- **Lemma J2**: the same shape (MCA term plus list size times one root) and proof pattern, but a
  different round. CFW26's mask enters the **sum** (the mask polynomial, then the `epsilon`
  combination of claims, a round with **no** MCA term because no words are combined); Binius64's mask
  is a committed **row** folded into the witness row by `gamma` (an MCA term, because words are
  combined, plus one root per member from the folded claim). Relabelled **Adapted (pattern of CFW26
  Lemma 6.6)**; the round itself is ours.
- **Lemma U**: CFW26's "there are at most `Lambda` witnesses ... independently of `epsilon` ... a
  union bound" is the same step. Kept **Adapted**, with CFW26 added as a published instance.
- **Lemma K**: CFW26 proves knowledge with a straight-line erasure-correction extractor (section
  7.2, last paragraph); our extractor list-decodes (WHIR Theorem 7.5's pattern). Different extractor,
  same statement type.

**SG26 Section 5.5 (read: 5.5.1, 5.5.2, Table 1; Appendix F not read).** Zero-knowledge ring
switching for a Ligero commitment: the Hashcaster form (twisted sums with Frobenius powers), each
twisted sum masked by a committed mask (subfield masks, or squaring-chain masks in characteristic
2), with "perfect soundness and HVZK" (Table 1; the `1/|K|` per combination challenge is Theorem F.6,
not read). Compared with this document: it concerns the **ring switch** (section 3), not the
opening's mask fold (J2) or the folds (F). It is not a list-regime analysis (Ligero's own soundness,
not read here), and its form is form F's family (Frobenius twisted sums), not form T. So **no
relabelling of J2 or F**; for Lemma J1 it is related work (a published zero-knowledge ring switch;
J1 treats soundness of the unmasked form T over a list). O-11 already records SG26 5.5 for rule Z.

**SG26 Theorem 6.6 (2), Definition 2.20, Definition H.3**: used as the compile theorem (section 7.1).

**WHIR Theorem 7.5 (statement)**: knowledge compilation of a polynomial IOP with list decoding
(`et_RS`), MCA and list-decodability hypotheses; Lemma K's extractor follows its pattern.

---

## 10. Gaps, fallbacks, decisions

| # | What is not proved, exactly | Closes it | Fallback and its cost |
|---|---|---|---|
| G-1 | Haböck route, leaf **mask** round only: Theorem 4 for interleaved words with challenges in the subfield `K` (4.3) | BCIKS20 full version Sections 5.2 (Steps 3 to 8), 6.2, 7 read for arbitrary subsets; or the DKT26 route | F-J2 (power batching of the leaf's rows), removes G-1 only |
| G-2 | DKT26 Theorem 4.4 and Corollary 6.6 are a preprint (2026-11-02); Theorem 4.4's algebraic-geometry lemmas not checked line by line here; its dimension count cites BCHKS Lemma 3.1 (checked numerically at our sizes by the referee) | (a) the ArkLib declaration of Theorem 4.4 at a pinned revision, with its hypotheses (every characteristic, full agreement sets, whether (39) or an `O(.)` form); (b) the external reviewer signs review item 1; (c) or BCHKS Theorem 4.6 read and found to give the qualitative statement (8.4) | the 184-query unique-decoding row (no DKT26) |
| G-3 | Haböck's weighted Theorems 3, 4 rest on "[BCI+20, Section 7]" of a full version not available; this affects **every** fold round on Haböck's route | read it | the DKT26 route |
| G-4 | **closed by Lemma K** (section 7) up to: polynomial-time decoding (DKT26 Corollary 9.4, statement read); spBCS built (SG26 Theorem 6.6 (2)); the first round's state is the relation | the spBCS build in `yugen-proof-b2`; review item 2 | the 184 row with Lemma K at `B_list = 1` |
| G-5 | H7 and H8' are properties of the build | BR-1 to BR-5 (section 5.3) implemented and their checks passing | if two openings of one commitment are ever needed: batch them into one opening |
| G-6 | Haböck route: whether BCIKS20's argument treats inseparable factors (factors in `Y^2`) in characteristic 2 (DKT26 does, Section B.1, Frobenius pullback) | the reading of G-1 with this question added | the DKT26 route |

**Decisions for the lead architect.**

1. Category 1 row: keep 184 (unique decoding, complete source, knowledge by Lemma K at `B_list = 1`),
   or adopt **107 at `m = 10` on the DKT26 route** once G-2 is closed by (a) and (b), or by (c). The
   102-query row is withdrawn. The 107 row halves the leaf slot's hashing rows (7.82 M to 4.55 M) and
   shrinks the leaf from 568 to 362 KiB.
2. Before either adoption: BR-1 to BR-5 in `yugen-proof-b2` (they also protect the 184 row's
   knowledge claim, since Lemma K uses H8' in both regimes) and the spBCS transcript.
3. F-J2 is not recommended as a hedge for the 107 row: it removes G-1 only.
4. Category 3: unique decoding, 261 queries at rate 1/8; or cap every opening at `2^30` codeword
   points and take 170 on the DKT26 route.

---

## 11. Tests

`johnson-row/` (plain `python3`, no dependencies; run each file directly, e.g.
`cd johnson-row && python3 test_fold_round.py`). Run on 2026-11-19, all passing:

| File | Tests | Time | What makes it non-vacuous |
|---|---|---|---|
| `test_mask_round.py` | T-J2-list (lerp, Diamond); unique-decoding line bound; close word with false claim | 3.2 s | two list members, false claims, `|S \ Exc| = 2` attained in each orientation |
| `test_fold_round.py` | T-F | 1.7 s | two list members, `|S \ Exc| = 4 = 2 |Lambda|` attained |
| `test_ring_switch_list.py` | basis; Theorem 1 exhaustive; descent exhaustive over the code; T-J1-list | 0.9 s | members computed over `K`, descent checked; union up to 60 > 32 from the members' actual output queries |
| `test_lifted_opening.py` | T-J3: lifted list, extraction, mask (every `s'`), index, `X` fold to dimension 1, query; step 5 at dimension 1 with a two-member pair list (revision 2.1, C-5) | 0.8 s | two non-lift members; `f` has no level-`n` candidate; index round reaches `2 |Lambda|`; step 5: `|S \ Exc| > |Lambda|` in 40 of 40 doomed instances. Step 6 (query) is **definitional**: it restates the definition of `S` (second referee 2.2) and is kept as a consistency check; the query bound is Haböck's Lemma 3, cited, not tested |
| `test_lifted.py` | revision 1's completeness, emulation and counterexample tests | < 0.1 s | the counterexample to the naive argument |
| `test_rowcalc.py` | 11, including an independent recomputation from the papers' formulas | < 0.1 s | — |

Revision 1's tautological tests (unique-decoding and list "planted" with an empty list), the vacuous
Diamond test (no good challenge) and the set-arithmetic union test were removed.

Deviation from the referee's acceptance for T-J3: it asks for the accepting mass under the optimal
prover over exhaustive challenges; that game has about `2^50` nodes in the toy (prover round
polynomials range over `K^3`), so T-J3 checks the round-by-round errors the lemmas state, each round
exhaustive in its challenge (the mask round for every `s'`), with random prover polynomials in the
later rounds, plus the query bound. At toy sizes the exceptional sets are computed exactly, not
bounded by DKT26's count (which exceeds `|K|` there); Lemma 3.3's count is checked. Not tested:
anything at real sizes; the Blueprint's code; BR-1 to BR-5 (they are tasks on `yugen-proof-b2`).

---

## 12. Review sheet for an external cryptographer (claims in order of risk)

| # | Claim | Where | Status | Questions for the reviewer (the referee's residual doubts included) |
|---|---|---|---|---|
| 1 | F2: line MCA with full agreement sets at the Johnson threshold, count `< 8 n t^3 / (3 rho_-)` (only `< 2^103.48` needed), characteristic 2, `GF(2)`-subspace domain, interleaved by Lemma 6.5 / Corollary 6.6 | 2.2, 8.4 | D (statement; Lemma 6.5, 3.3 proofs read); Theorem 4.4's Lemmas 4.1, 4.2 read by the referee and found plausible, A.5 skimmed, (109) checked numerically at our sizes only | Is DKT26 Theorem 4.4 correct in characteristic 2, including the Frobenius pullback of inseparable factors (B.1)? Does the ArkLib statement cover every characteristic and full agreement sets, and is (39) formalized? Does BCHKS Theorem 4.6 give the same qualitative statement independently? |
| 2 | Lemma K: round-by-round knowledge with the list extractor; SG26 Theorem 6.6 (2) applies | 7 | P; compile theorem D (statement) | Is setting the state to 0 through the first commitment compatible with SG26 Definition 2.20 (a) for the series-parallel order of the leaf (two commitments)? Is the first round's per-member state exactly `(x, w_y) in R` for Binius64's constraint system with the pad constituents? |
| 3 | Lemma J3 with H8': a commitment binds a list; one batched opening per proof makes one member answer for every claim | 5.1, 5.3 | P; BR-1 to BR-5 are tasks | Does every Yugen statement satisfy H8' (b), including recursion, where a node's circuit verifies leaf openings? Is there any planned precommitment reuse (Blueprint 6)? |
| 4 | Lemma F: weighted-to-unweighted step, measure fixed before the challenge, two roots per member; Lemma 3.3 at dimension 1; virtual folds and higher arities as per-variable rounds | 5.4 | P; X (T-F, T-J3) | Is `delta_i = delta*_{i-1}` the right reading of Haböck's measure for virtual (uncommitted) folds and fold arities above 1? |
| 5 | Lemma J2: `(N_line + B_list)/|K|`, both orientations; output is Haböck's language | 4.1 | P; X (T-J2-list) | — |
| 6 | Remark Q: the subset form of MCA at `A >= k` is the full-set form | 2.2 | P | — |
| 7 | Lemma U: list state, adaptivity | 2.3 | P (referee: holds) | — |
| 8 | Lemma J1 and the descent | 3 | P; X (T-J1-list) | — |
| 9 | F1': `B_list = 19` at every `n` | 2.2 | D + P; X | — |
| 10 | Lemma UD and the 184 row | 6 | P from WHIR Lemma 4.10 (read) + BCIKS20 Theorem 4.1 (D), DKT26 Lemma 6.5 (D) | — |
| 11 | The numbers of section 8 | 8 | X `test_rowcalc.py` (with an independent recomputation) | Inputs `|E_l| <= 2^22` leaf, `2^31` node, 600 challenges a proof: do they bound the built tree? |
| 12 | Haböck route gaps G-1, G-3, G-6 | 4.3, 10 | U | Do BCIKS20's Section 5.2 Steps 3 to 8, 6.2 and 7 hold for arbitrary subsets `S` and treat inseparable factors in characteristic 2? (Only if the DKT26 route fails.) |

Strong round-by-round soundness (CMS19 Remark 8.2) is not shown; SG26 Theorem 6.6 (2) does not need
it, and the BCS16 chain form that would is not adopted (referee 5).

---

## 13. Response to the referee (`johnson-row-referee.md` section 7)

| Item | Done |
|---|---|
| R-1 (DKT26 a preprint) | status stated (0.1); the qualitative need isolated (8.4) and three alternative sources named, with a reading task for BCHKS; ArkLib check and external review stay open (G-2) |
| R-2 (G-1) | narrowed to the leaf's mask round (4.3); the route is declared not available |
| R-3 (weighted to unweighted) | written, Lemma F step 2 |
| R-4 (`D = 0` levels) | Lemma 3.3 in F2 and Lemma F; when the build reaches dimension 1 (5.4) |
| R-5 (H8) | H8' adopted, Lemma J3 re-proved, BR-1 to BR-5 (5.3) |
| R-6 (G-3, G-6) | recorded in section 10; they make Haböck's route unavailable |
| R-7 (WHIR) | WHIR is in the folder: Lemma 4.10 read; Corollary 4.11 not cited for our domain |
| R-8 (CFW26) | compared, section 9; O-17, O-19 relabelled; GordieHowe 5.5 compared too |
| R-9 (knowledge) | Lemma K, section 7 |
| R-10 (tests) | T-J2-list, T-F, T-J1-list, T-J3; vacuous tests removed (11) |
| R-11 (wording, list size, 142.25) | section 0.3; `B_list = 19`; the 102 row dropped with its 142.25-bit Haböck figure (`test_rowcalc.test_withdrawn_102_row_is_fragile`) |
