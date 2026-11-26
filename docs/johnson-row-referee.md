# Referee report on `binius-johnson-row.md` (L-J1, L-J2, L-J3, Lemma U, Lemma F, Lemma UD, the rows)

Part of Yugen. 2026-11-19. Independent review of `binius-johnson-row.md` at commit
`5f5f677` and its tests in `johnson-row/`. The reviewer did not write the document under review.
Every "proved" there was read as a claim to break. Nothing in the reviewed document or in any other
file was edited. Provenance of the findings below: **Original (the Ycash developers, 2026)**,
review findings, first recorded in this file. Where a finding rests on a paper, the paper is cited.

## 0. Verdicts first

| Claim (section of the reviewed document) | Verdict |
|---|---|
| Lemma U, the list state (2.3) | **Holds.** The union is over a list that is a function of the transcript before the challenge. Prover adaptivity is covered because round-by-round error is a bound for each partial transcript. |
| F1, the list size `B_list = (m + 1/2)/sqrt(rho)` (2.2) | **Holds, and is conservative.** The elementary Johnson bound gives 19.2 at `m = 10` (DKT26 (38), second term; Cauchy–Schwarz). |
| L-J1, ring switch `8 B_list / |K|` (3) | **Holds.** |
| L-J2, mask round, DKT26 route `(N_line + B_list)/|K|` (4.1) | **Holds under an extra hypothesis:** DKT26 Theorem 4.4 and Corollary 6.6 are correct. That paper is an unreviewed preprint. |
| L-J2', mask round, Haböck route (4.2) | **Holds for `R = 1`, which the build never uses**: nodes have no mask, and the leaf has `R = 2`. For the leaf this is a **gap**: G-1, and also G-6 below. |
| "The claim needs no separate term" (0 item 4, 4.1) | **Right on Haböck's route.** On DKT26's route `B_list` roots are a claim term, so the headline of 0 item 4 contradicts its own body (the error is numerically negligible). |
| Is G-1 the only gap on Haböck's route? | **No.** G-3 also applies to Haböck's fold rounds. G-6 (new, below) concerns characteristic 2. Haböck's Section 6 is itself a sketch. G-1 is overstated for the leaf's index round. |
| L-J3, lifting with the list at the lifted level (5.1) | **Holds under H7.** **H8 is mis-stated**: the danger is list binding across separate openings at any level, not "another level". See R-5. |
| Lemma F, fold and index rounds under MCA (5.2) | **Holds under DKT26.** One step is missing (weighted to unweighted, R-3). Levels with message dimension 1 need DKT26 Lemma 3.3, not Theorem 4.4. |
| Lemma UD and the 184 row (6) | **Holds.** It is robust to the WHIR citation, which could not be checked here (R-7). |
| Arithmetic of section 7 (184 / 107 / 102 / 77; 152.52; 216.52) | **Reproduced exactly** by an independent script (section 4). The 102 row clears its target by **0.001 bit**. |
| Round-by-round in the sense of the QROM theorem | **Holds** for CMS19 Definition 8.4 round-by-round *soundness*. The list version of knowledge (G-4) is not written, and a shielded pool needs knowledge (R-9). |
| Tests in `johnson-row/` | **They test something easier than the lemmas.** The list-regime mask tests never contain a nonempty list in a doomed instance, and the Diamond-orientation test is vacuous (section 6). |

**Overall.** The 107-query row at `m = 10` may **not yet be called proven**. What is proven is
narrower: on the **DKT26 route**, the row's round-by-round soundness follows, with the argument
checked here, *from DKT26 Theorem 4.4 and Corollary 6.6 as hypotheses*. The binding term of the row
is the query round (152.97 bits against 152.52). It does not depend on DKT26's constant: the
algebraic rounds keep about 59 bits of slack. So the row needs only the *qualitative* statement:
line MCA with full agreement sets at the Johnson threshold, in characteristic 2, width independent,
with an exceptional count below about `2^103`. **Route: DKT26.** Haböck's route alone is not
available for the leaf until G-1, G-3 and G-6 are closed or F-J2 is built, and F-J2 removes only
G-1. Before the word "proven" is used, do three things: (i) confirm the ArkLib declaration of
DKT26 Theorem 4.4 (every characteristic, full agreement sets, and whether the explicit constant
(39) is formalized) at a pinned revision, and obtain the external review of item 1 of the review
sheet; (ii) close R-3, R-4, R-5 and the R-9 wording; (iii) replace the tests by the ones in
section 6. **Do not adopt the 102 row**: its 0.001-bit margin and its sole dependence on DKT26's
constant (Haböck's route gives 142.25 bits there) make it fragile.

## 1. What was read, and how

Text layers were extracted with `pypdf` (the repository's `.tools-venv`) to a scratch directory
outside every repository. The papers stay in the reference-paper collection (REFERENCES.md).

- Dao, Kominers, Thaler, "Reed–Solomon Codes Beyond Johnson: Efficient Decoding and Smaller
  Cryptographic Proofs", ePrint 2026/2056 (copy dated November 2, 2026; "DKT26"):
  - Sections 3.1 (Definitions 3.1, 3.2, Lemma 3.3) and 4.1 (Lemmas 4.1, 4.2 with proofs);
  - Section 4.2 (Lemma 4.3, statement); Theorem 4.4 with its proof paragraph;
  - Section 6 opening, 6.1 (Lemma 6.2, Corollary 6.3), 6.2 (Corollary 6.4, Lemma 6.5, Corollary 6.6
    with proofs), 6.3 (Corollary 6.7);
  - Appendix A.4 (Lemma A.5) and Appendix B in full: B.1, the proof of Lemma 4.3; B.2, Proposition
    B.1; B.3, the closed constant;
  - Section 1.2 (related work); Appendix H (Lean map); the AI methodology statement.
- Haböck, "Basefold in the List Decoding Regime", ePrint 2024/1571 (undated copy): Theorems 1 to 4,
  Remark 5, Section 5 (languages (20) to (31), Lemmas 1 to 3), Section 6.1 (languages (34), (35),
  Lemma 4 with proof).
- Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint
  2026/391 (copy dated November 16, 2026; "CFW26"): abstract, Definition 3.19, Lemma 3.18,
  Theorem 6.3 (statement only), the beginning of Construction 6.4.
- Diamond, Posen, ePrint 2024/504, and Diamond, ePrint 2025/1015: title pages, plus Theorem 4.2's
  location in 2025/1015. Their content enters only through `binius-extension-challenges.md`
  Theorem 1, whose proof was re-read in that document.
- Binius64 Blueprint (`yugen-b-eval/upstream/papers/binius64-spec.txt`): 5.3, 5.4, 7.2 including
  Protocol 7.1 and its soundness paragraph.
- This repository: `binius-johnson-row.md` (all), `johnson-row/*.py` (all; run),
  `binius-extension-challenges.md` 2 to 4, `soundness-method.md` 8.5b, `qrom-compilation.md` 5 and
  6, `CITATION-AUDIT.md` C-7, C-11, C-12, 1c, C-16, `REFERENCES.md` O-15 to O-19.
- **Not available or not read**: WHIR (ePrint 2024/1586) is not in the reference folder. BCIKS20
  (ECCC TR20-083) is not in the reference folder. BCHKS (DKT26's [BCH+26]) and Zheng's manuscript
  [Zhe26] were not read. The ArkLib sources were not opened.

## 2. The cited theorems against our use

### 2.1 DKT26 Theorem 4.4 (line MCA at Johnson, every characteristic)

**Statement as read.** The hypotheses are: `F` is any field; `alpha_1..alpha_n` are distinct;
`1 <= D <= n - 2`; `rho = (D + 1)/n`; `rho_- = D/n`; `a = sqrt(rho_-) + eta_0 <= 1`;
`A = ceil(a n)`; `m = max(ceil(sqrt(rho_-)/(2 eta_0)), 3)`; `t = m + 1/2`. The conclusions are:

- the list bound (38), `|L_D(y, A)| <= min(B_jet, n(A - D)/(A^2 - nD))`;
- for every `f, g`, a set `E` with `|E| <= B_cf < 8 n t^3 / (3 rho_-)` such that for `z` outside
  `E`, every `P` of degree at most `D` with `|S_z(P)| >= A` is `F_0 + z G_0`, where
  `S_z(P) = S(F_0, G_0)` (equality of full agreement sets);
- if `F` is finite and `z` is uniform in `F`, the probability is at most `B_cf / |F|`.

**Our use.**
- `F = K = GF(2^256)`; the domain is a `GF(2)`-subspace in `L`, hence distinct points of `K`.
- Our threshold `a = (1 + 1/(2m)) sqrt(rho)` is at least `sqrt(rho_-)(1 + 1/(2m))`, so the
  theorem's `m` is at most ours. Checked exactly at `n = 2^12 .. 2^30`: Theorem 4.4's `m` is 10
  when ours is 10; at tiny `n` it is smaller. A higher `A` only shrinks the set of candidates, so
  the same `E` works.
- The challenge is uniform in `K`, the code's field. `L`-valued words are `K`-words
  (`binius-extension-challenges.md` Lemma 3).

**All hypotheses are met.** One exception is noted in R-4: levels with `D = 0`.

**Proof, read as far as needed for characteristic 2.**
- Proposition B.1 (the interpolant) imposes multiplicity through the coefficients of
  `Q(alpha_r + U, Z, f_r + Z g_r + V)`. These are Hasse-type conditions, valid in every
  characteristic.
- Lemma 4.3 (B.1) handles inseparable factors explicitly. A factor `Q_i(Y) = G_i(Y^{s_i})` with
  `s_i = p^nu` is replaced by its Frobenius pullback, which is separable in the message variable.
  The Taylor recurrence then runs to degree `s_i D`, using `(t_0 + xi)^{s_i} = t_0^{s_i} + xi^{s_i}`,
  and the degree loss is absorbed in (103).
- No step that was read assumes odd or large characteristic.
- One external dependency remains inside the proof: the dimension count `N_var > N_eq` (109) is
  cited to BCHKS (full version, Lemma 3.1), which is not in our set. **We checked (109) by exact
  integer arithmetic at our sizes** (section 4.2). It holds, with a ratio of 1.0129 at `m = 10` and
  1.0008 at `m = 153`, and all degree factors are positive.

So, for our instance, the remaining unchecked parts of Theorem 4.4 are Lemmas 4.1 and 4.2, which
were read and found plausible, and Lemma A.5, which was skimmed.

**Status.** DKT26 is a preprint dated 2026-11-02 and has not been peer reviewed. Its methodology
statement says the main results were found and formalized with AI assistance, and its authors take
responsibility. Appendix H's table lists "Zeroth order (Theorem 4.4): every characteristic; positive
Johnson gap: complete finite list and Johnson bound; line MCA with full agreement sets" as
formalized in Lean. The table does not say whether the explicit constant (39) is in the formal
statement. **R-1 below.**

**Robustness, a reviewer's observation.** The 107 row at `m = 10` does not need (39). The weakest
algebraic term would still meet 152.52 bits with any exceptional count below about `2^103` at
`n = 2^30`. That is about 59 bits of slack over (39), and 17 bits even over Haböck's `n^2` count.
What the row needs from DKT26 is the *full-agreement-set* form in characteristic 2. Haböck's
theorems give correlated agreement with a constraint, not that form (section 3.4). The 102 row at
`m = 153` is different: it needs (39) itself, since Haböck's count gives 142.25 bits.

### 2.2 DKT26 Lemma 6.5 and Corollary 6.6 (interleaving)

The proof was read and checked. At each bad `z` choose a witness set; the projections that kill
every coefficient class form a proper subspace `K_z`. At most `q` proper subspaces cover fewer than
`q^s` vectors, so one projection keeps every bad challenge bad for a scalar curve. This is
elementary and correct.

Corollary 6.6 then recovers full sets row by row when `A >= k`. It holds for `C` linear over
`F_q`, with the challenge in the same `F_q`, which is our case. The subset hypothesis of Lemma 6.5
follows from the full-set statement of Theorem 4.4: a bad `z` with set `S` gives `P` with
`S ⊆ S_z(P)`, so outside `E` both rows are in the code on `S`. **The width-independent interleaved
MCA used for the mask round (width `R`) and the index round is valid** under Theorem 4.4.

### 2.3 DKT26 Corollary 6.4 (interleaved lists)

This is an elementary embedding into an extension field. With the Johnson term of (38), itself an
elementary Cauchy–Schwarz count, it gives `|Lambda| <= 19.2` at `m = 10`, at every width.
**Recommendation**: rest `B_list` on this elementary bound, not on the Guruswami–Sudan
`Y`-degree. The document keeps 29.70, which is conservative and costs at most 0.6 bit on
non-binding terms. `binius-extension-challenges.md` was already corrected to 19 in `c594ee6`, and
the two documents now disagree.

### 2.4 Haböck Theorems 2 to 4, Lemmas 1 to 4

**Statements as read.**
- `F` is a finite field of arbitrary characteristic, `C = RS_k[F, D]`, and
  `theta = 1 - sqrt(rho)(1 + 1/(2m))` with `m >= 3`.
- Theorem 3 (weighted subcodes) and Theorem 4 (constraint `Gamma` of total degree 2) have the error
  `eps(C, M, B, theta) = M/|F| * (t/sqrt(rho)) * max(t^6 |D|^2 / (3 rho), 2(B|D| + 1))`.
- Lemma 3 gives the query error `(1 - theta)^s`. Lemma 4 is the fold round with Theorem 4, weight
  denominator `B_i = 2^i`.

The document reproduces this formula correctly (`rowcalc.haboeck_count` matches).

**Our use and the hypotheses.**

(a) The proofs of Theorems 2 to 4 are "as in [BCI+20, Sections 6 and 7]". Section 6 of Haböck's
paper is a sketch ("we omit certain details"; `CITATION-AUDIT.md` C-11). The weighted section of
BCIKS20 is not in our copy (the document's G-3). **G-3 applies to every fold round on Haböck's
route**, not only to a side remark. F-J2 does not remove it. The document's decision 2 ("the leaf
row rests on Haböck's published theorems") is therefore true only in the sense of citing a
published statement whose proof we have not read.

(b) **G-6 (new).** DKT26, Section 4.2, says that, following BCIKS and Zheng, "we also extend the
argument to inseparable factors". Section B.1 then gives the Frobenius pullback. In characteristic
2 a factor of the interpolant can be a polynomial in `Y^2`. Haböck's theorems state "arbitrary
characteristic". Whether the BCIKS20 argument they rest on treats inseparable factors was not
checked: BCIKS20 Section 5.2, Steps 3 to 8, are the steps G-1 already names. **Closes it**: the
same reading as G-1, with this question added; or the DKT26 route.

(c) The doc's G-1 is right for the **mask round** at the leaf. There, the folded word has width
`R = 2` and the constraint is `K`-linear across rows, so the extension-field identification breaks
`K'`-linearity of `Gamma`. G-1 is **overstated for the leaf's index round**: after the mask fold
there are `R = 2` rows, and the one index round folds them into one, so its line `u + zeta v` is a
line of *scalar* words. Haböck's Theorem 4 with `M = 1` applies directly, and its conclusion gives
the joint pair, which is the width-2 list member. G-1 arises for index rounds only when `R > 2`.

## 3. The proof steps

### 3.1 Lemma U

- **The list is fixed before the challenge.** `Lambda(W)` is a function of the committed words,
  all sent before the challenge.
- **The union is legitimate though the list depends on earlier prover messages.** Round-by-round
  error (CMS19 Definition 8.4) is a bound over every partial transcript with a doomed state. For a
  fixed transcript the list is a fixed set of at most `B_list` tuples, so the union bound is
  per-transcript and adaptivity costs nothing.
- **Monotonicity under a new oracle** follows from restriction, given that the PIOP's own state for
  a fixed `y` is round-by-round: a prover's oracle message never raises it. This is the hypothesis
  "St(y, .) with round-by-round error eps".
- **Threshold strictness** (minor). Haböck's (20) and (34) use `d < theta`, while his lemmas
  conclude `>= 1 - theta`. With `A = ceil(a n)` the document's list contains both. The mismatch is
  Haböck's own and harmless.

**Holds.**

### 3.2 L-J1

- The doomed condition is correct. After the check, a member with `s_hat = s*(y)` has its claim
  equal to the passed check, so every member of a doomed state has `s_hat != s*(y)`.
- Theorem 1 of `binius-extension-challenges.md` applies to each member separately.
- "Every list member's trace row is in `L`" **is shown**. The domain lies in `L`; the member's row
  agrees with the committed `L`-valued row on at least `A >= sqrt(rho) n > k` points; Lemma 4 of
  that document does the rest. Degree below `k` needs only `k` points, and Lemma 4 asks for `k + 1`,
  so both are met.
- Precision to add: the descent is row by row for the `M` row of the committed interleaved pair
  `(M_0, omega_0)`. The `omega_0` row is `K`-valued and needs no descent.

**Holds.**

### 3.3 L-J2 on DKT26's route

The algebra checks in both orientations:
- lerp: `y = (F_0, F_0 + G_0)`, constant term `<msg F_0, T> - s`;
- Diamond: `y = (G_0, F_0)`, `Z`-coefficient.

`Exc` depends only on `(u, v)`, which are committed. The roots depend on `s'`, which is sent before
`gamma`. Lifting commutes with `lerp` (Dup is linear), so analysing the mask fold on lifted rows
(H6) equals the Blueprint's fold-then-lift (Protocol 7.1 steps 3 and 4), with conservative lengths.

**Holds under DKT26.** **Relation to published work**: CFW26 Theorem 6.3 states round-by-round
*knowledge* errors of exactly this shape for its zero-knowledge sumcheck over interleaved codes, at
any `delta < delta(C)`:
- `Lambda(C^{≡2^k}, delta) * eps_pil(C, 1, 2)` for the first round;
- `eps_mca(C^{≡2^{k-j}}, delta) + Lambda(C^{≡2^{k-j+1}}, delta) * eps_pil(C, 1, d_s)` for each fold
  round.

Their construction (mask sum, then a combination challenge) differs from Binius64's lerp. But the
document's label for J2, "Original as far as checked", did not consult 2026/391, which is in the
reference folder. **R-8.**

### 3.4 L-J2' on Haböck's route

The proof for `R = 1` is correct. Theorem 4's `Gamma` is affine in `(P, z)`, and the formal
identity at `Z = 0` gives the claim, so no root term appears. But **`R = 1` never occurs in the
build**: the leaf masks `R = 2` round oracles, and nodes are unmasked. On this route the leaf's mask
term rests entirely on G-1, plus G-6.

### 3.5 Lemma F

The replacement of Haböck's Theorem 4 by MCA goes through. One step is missing from the text.

**R-3, the missing line.** Haböck's proximate has *weighted* agreement
`mu*_{i-1}(S) >= 1 - theta`, with `mu*` of density at most 1 (his (29), (30)). MCA needs
*unweighted* `|S| >= A`. The step is `|S| / |D_i| >= mu*_{i-1}(S) >= 1 - theta`, so
`|S| >= ceil((1 - theta)|D_i|) = A`. After MCA, the joint set equals `S`, so the joint weighted
agreement is the same `mu*_{i-1}(S)`. Write this in the proof. It is the reason "the full-set
equality removes the weight denominator".

Two further points about the measure:
- `mu*_{i-1}` is fixed before `lambda_i`. It is built from `f_0..f_{i-1}` and
  `lambda_1..lambda_{i-1}`, and only `mu_i` uses the post-challenge `f_i`, as in Haböck's (30). So
  the list over which the roots are counted, the unweighted column list of
  `(f_{i-1,0}, f_{i-1,1})`, is fixed before the challenge.
- The root count is right: a member not compliant at 0 or at 1 gives a nonzero `Gamma` of degree at
  most 2 in `Z`.

**R-4, levels of dimension 1.** Theorem 4.4 excludes `D = 0`. If any fold level has message
dimension 1, cite DKT26 Lemma 3.3 (constant code, `|E| <= ell C(n, 2)/(A - 1)`), or state that
BaseFold stops at a terminal codeword with `k >= 2`. The numbers are unaffected, since these levels
have tiny `n`.

**Holds under DKT26, with R-3 and R-4.**

### 3.6 L-J3

**The argument.** It is right that no proximity relation between `Dup(f)` and `f` is needed. Every
analysis treats the lifted word as an arbitrary word at level `l`, and the price, errors computed
at the lifted length, is already paid in the rows: `2^22` at the leaf, `2^31` at a node. The claim
operand `T(X_low) eq(0, X_high)` reads only the `X_high = 0` block of *any* level-`l` message. So
the witness is that block whatever list member it comes from, and the list of such blocks has at
most `B_list` elements. The toy counterexample is correct, and it is a fair warning against the
naive argument.

**H7** (the level is fixed by the circuit shape) is true of Binius64 as described. In Blueprint 7.2,
`l_r` is "the least variable count that accommodates the constituents and the pad", and
`l = max_r l_r`. Both are shape functions.

Should H7 ever fail, the fallback of G-5 (open unlifted) is not needed. Let the state be "some
level `l'` in the allowed set and some `y` in `Lambda_{l'}`". That multiplies only the list-factor
terms by the number of possible levels (at most 32, 5 bits). Those terms have more than 85 bits of
slack.

**R-5: H8 is mis-stated.** The cross-proof clause ("no commitment reused across proofs at another
level") misses the real issue. In the list regime a commitment binds a *list*, not a message. Two
separate openings of one commitment, at the same level or not, in one proof or in two, can be
satisfied by **different** list members. Unique decoding cannot do this. The correct hypothesis is
H8': within a proof, every claim on a commitment is discharged by the one batched opening (Protocol
7.1 is a single BaseFold instance, so this holds as built); and no statement of the system relies
on two openings of one commitment denoting the same message.

Blueprint 6 allows a precommitment to be "reused across many statements". The documents read here
show none reused in Yugen: the OTP keys are per proof. The verifier check of G-5 should be extended
to H8'. With H8', each proof's analysis is independent, and the tree union of `soundness-method.md`
8.5b is unaffected.

**Holds under H7 and H8'.**

### 3.7 Lemma UD

`B_list = 1` at `(1 + rho)/2` is correct: two members overlap on at least `2A - n >= k` points.

WHIR Lemma 4.10 and Corollary 4.11 could not be checked: the paper is not in the reference folder.
The row does not depend on them. DKT26 Theorem 4.4 at the unique-decoding agreement (`m = 3`) gives
216.2 bits at the node's first fold, still above 152.52, and the document's direct weighted proof
(end of section 6) is a second route from BCIKS20 Theorem 4.1.

"One bit conservative" is confirmed: full-domain line 225.00 bits against half-domain 226.00.

**Holds.**

## 4. Arithmetic, recomputed independently

### 4.1 The rows

Own script (plain Python floats; formulas taken from the papers, not from `rowcalc.py`; text in
the appendix). All challenges, and hence every term, are over `K = GF(2^256)`.

In the mixed variant the only `L = GF(2^128)` objects are the round-0 codeword alphabet, the packed
trace and the query pad (`binius-extension-challenges.md` 2). No term has a `|L|` denominator: the
ring-switch challenge `r''` is in `K^8`, and every fold, batching and PIOP challenge is in `K`. `L`
enters the proofs only through the descent of L-J1.

| Quantity | Recomputed | Document |
|---|---|---|
| Target `129 + log2(20,000 x 601)` / `193 + ...` | 152.519 / 216.519 | 152.52 / 216.52 |
| QROM per-round need, `C1 = 6` / `C1 = 24` | 145.87 / 147.87 | 145.87 (does not bind) |
| UD: queries, bits; one fewer | 184 -> 152.73; 151.90 | 184 (152.73) |
| `m = 10`: per query; queries | 1.42961; 107 -> 152.968 (106 -> 151.54) | 1.4296; 107 (152.97) |
| `m = 152` / `153`: queries | 103 / 102 -> **152.5199** (need 152.5189) | 103 / 102 (152.53) |
| `m = 3`, category 3: queries | 170 -> 217.19 | 170 (217.19) |
| rate 1/16, `m = 38`: queries; node fold `2^31` line | 77 -> 152.55; 203.78 | 77; 203.8 |
| `B_list` (GS) / Johnson (38), `m = 10` | 29.70 / 19.22 | 29.70 / 19 (in `binius-extension-challenges.md`) |
| PIOP / ring switch / batching, `m = 10` | 244.12 / 248.11 / 249.52 | same |
| DKT26 mask leaf `2^22` / index / leaf fold `2^21` / node fold `2^30` | 219.41 / 219.41 / 220.41 / **211.41** | same |
| Haböck mask `2^22` / leaf fold / node fold | 185.34 / 187.34 / **169.34** | same |
| `m = 153`: DKT26 node fold; Haböck node fold | 199.80; **142.25** (fails) | 199.80; not stated |
| UD: mask / index / node fold / ring switch / PIOP | 234.00 / 234.00 / 226.00 / 253.00 / 249.01 | same |
| Category 3, DKT26 `m = 3`: node fold `2^30` / `2^29` line | 216.16 / 217.16 | same |

The union over rounds and over the tree is inside the target (`soundness-method.md` 8.5b,
condition C: `e >= 129 + log2 N + log2(1 + k)` with `N = 20,000`, `k = 600` on average, both
conservative). Every number of section 7 is reproduced. **Findings:**

- **The 102 row clears its target by 0.001 bit.** Any upward revision of `N`, of `k`, or of the
  QROM constant (Theorem Q form C, `C1 = 24`, does not bind today) can break it.
- **The 102 row rests on DKT26's constant alone.** Haböck's count gives 142.25 bits at the node.
  The document says "DKT26 route only" but does not show the failing figure.

### 4.2 DKT26's interpolant and constant at our sizes

These are exact integer checks.
- **Dimension count.** The count `N_var > N_eq` of (109), the BCHKS dimension estimate the proof
  cites but does not prove, holds at `n = 2^5, 2^8, 2^12, 2^21, 2^22, 2^30` (`m = 10`) and at
  `n = 2^30` (`m = 153`), with every factor `ceil(C_spec) - D j` and `ceil(C_Z) - j` positive.
- **Exceptional count.** The exact `E_ord^(1)` of (33)–(34) is below the closed form (39) at every
  size checked: 212.14 against 211.41 bits at `n = 2^30`.
- **Parameters.** At `m = 10`: `B_jet = 29`, `B_Z = 294`, Johnson list 19.22.

This removes one external dependency of Theorem 4.4 *for our instance*. It does not check the
algebraic-geometry lemmas.

## 5. Round-by-round against the QROM compilation

Theorem Q (`qrom-compilation.md` 5.1, adapted CMS19 Theorem 8.6) needs a CMS19 Definition 8.3
state function, per-round errors under uniform verifier messages in spaces of at least 256 bits,
and (for extraction) Definition 8.5 knowledge.

**Soundness: met.**
- The document's states are of this kind: existential over the list or over Haböck's languages;
  prover messages never raise them (Lemma U, and Haböck's reductions); a doomed final state is
  rejected except with `(1 - theta)^s`.
- Challenges are uniform in `K`, `K^8` and `E_l^s`.
- Efficiency of the state is not required for soundness.

**Two caveats.**
- **R-9: knowledge.** The tree-forgery definition of `soundness-method.md` 8.5b is *soundness* (a
  false leaf statement). For spend statements whose existence part is trivially true (a preimage of
  a key exists), the property a shielded pool needs is knowledge. Theorem Q (2) gives extraction
  from Definition 8.5 round-by-round knowledge. In the list regime that needs an efficient list
  extractor: decode, then test each of at most `B_list` candidates against the relation. Neither it
  nor a knowledge version of Lemmas U, J1, J2 and F is written. The document's G-4 ("none for the
  soundness rows") understates this. CFW26 Theorem 6.3 is a model for the statement: knowledge
  with relaxation, extraction time stated.
- Strong round-by-round soundness (CMS19 Remark 8.2, Appendix B) is not shown. It is needed only for
  the BCS16 chain form, which `qrom-compilation.md` does not adopt.

## 6. The tests

| Test | What it checks | What the lemma claims | Gap |
|---|---|---|---|
| `test_ring_switch_list` | Theorem 1's bound per deviation, exhaustive; then `|union of 3 sets| <= 3 x 32` and "sometimes > 32" | union over a list of codewords fixed before `r''`, with descent of members to `L` | The union step is set arithmetic: true for any three sets. No code, no list, no descent. |
| `test_mask_round` UD planted | `|S| <= |E| + |Lambda4|` with `|Lambda4| = 0` | at most one root per list member outside `Exc` | With an empty list `S ⊆ E` holds by the definition of `E`, so the test is tautological. Run instrumented: Λ4 empty, S = {85}, E = {85, 114} (seed 11). |
| `test_mask_round` list planted (`A = 7`) | same | same, in the list regime | Instrumented run: **Λ4 empty** again, `S ⊆ E` again tautological; doomed is not even asserted. |
| `test_mask_round` Diamond | same | Diamond orientation | Instrumented run: **S = ∅** (the cancellations are planted for lerp): vacuous. |
| `test_mask_round` close, false claim | UD, `|Lambda4| = 1`, `|S \ E| <= 1` | the root step | The only non-trivial check, and only in unique decoding. |
| `test_lifted` | completeness of Dup; uniform emulation; counterexample to the naive argument | L-J3's positive claim | It tests an argument the lemma does not use, not the lemma. |
| `test_rowcalc` | `rowcalc.py`'s outputs | the formulas' correctness | It checks the calculator against itself; section 4 above is the independent check. |

**Tests that would test the claims** (task, with acceptance):

- **T-J2-list.** `K = GF(256)`, `n = 16`, `k = 2`, `A = 7`. Build rows that agree with two distinct
  codeword tuples on disjoint 7-sets, so that `|Lambda4| >= 2`, with a false claim for every
  member. Plant cancellations at chosen `gamma`.
  *Acceptance*: in a doomed instance, every good `gamma` outside `E` is a root of `phi_y` for some
  member `y`, and `|S \ E| <= |Lambda4|`; at least one instance has `|S \ E| >= 2`, so the root term
  is exercised. Do this in both orientations, with the Diamond instance planted for Diamond.
- **T-F.** The same construction for one sumcheck-coupled fold round, with a prover round
  polynomial `h` fixed before `lambda`.
  *Acceptance*: `|S \ E| <= 2 |Lambda|`, and an instance attains more than `|Lambda|`.
- **T-J1-list.** A committed `L`-valued row with two `K`-codeword list members (`GF(4) < GF(16)`
  toy); a check that both members descend to `L`; then the ring switch's bad set is at most
  `|Lambda| kappa |K|^(kappa - 1)`, computed on the members' actual deviations.
- **T-J3.** A lifted toy opening (mask, index, one fold, queries) on a word whose lifted list has a
  non-lift member.
  *Acceptance*: the accepting `(challenge, query)` mass over exhaustive challenges is within the
  sum of the lemma's terms.

## 7. Work that closes each item

| # | Item | Closes it | Fallback |
|---|---|---|---|
| R-1 | DKT26 Theorem 4.4 / Corollary 6.6 are an unreviewed preprint (G-2) | (a) Locate the ArkLib declaration (`ReedSolomon/PaperGuide.lean`, [DA26] revision) for Theorem 4.4 and record its hypotheses: every characteristic, full agreement sets, and whether the bound is (39) or an `O(.)` form. (b) External reviewer signs review item 1. | Haböck's route after R-2 and R-6, or F-J2 for the leaf (107 rows survive; 102 does not) |
| R-2 | G-1 (leaf mask round only; not the index round at `R = 2`) | BCIKS20 full version, Section 5.2 Steps 3 to 8, read for arbitrary subsets `S`; or the DKT26 route | F-J2 |
| R-3 | Lemma F's weighted-to-unweighted step not written | Add the one line of 3.5 to the proof | none needed |
| R-4 | `D = 0` levels outside Theorem 4.4 | Cite DKT26 Lemma 3.3, or state the terminal level has `k >= 2` | none needed |
| R-5 | H8 mis-stated | Replace by H8' (3.6); extend G-5's verifier check | open the shared commitment once and pass its claims to one batched opening |
| R-6 | G-3 and **G-6** on Haböck's route | Read BCIKS20 Sections 5.2 (Steps 3 to 8), 6, 7 for weights and for inseparable factors in characteristic 2 | the DKT26 route |
| R-7 | WHIR Lemma 4.10 / Corollary 4.11 not checkable here | Add 2024/1586 to the reference folder and confirm `err* = n/|F|` for 2 functions | the 184 row stands on DKT26 Theorem 4.4 at `m = 3` (216.2 bits) or on the document's direct weighted argument |
| R-8 | J2's provenance label omits CFW26 (2026/391) Theorem 6.3, whose error has the same MCA-plus-list-times-identity shape | Compare CFW26 Theorem 6.3 with J2 and Lemma F; relabel J2 and F "Adapted, cf. CFW26 Theorem 6.3" or state the difference; update `REFERENCES.md` O-17 and O-19 (the document's author, not this review) | — |
| R-9 | Knowledge in the list regime (G-4) | Write round-by-round knowledge for Lemmas U, J1, J2, F with a list extractor (decode, test each candidate); cite DKT26 Theorem 1.3 for efficient decoding after reading it | — |
| R-10 | Tests | T-J2-list, T-F, T-J1-list, T-J3 (section 6) | — |
| R-11 | Wording | Section 0 item 4: "no claim term" only on Haböck's route; set `B_list` to the elementary Johnson bound (19.2) to agree with `binius-extension-challenges.md`; show 142.25 for Haböck at `m = 153` | — |

**What "proven" may say after R-1, R-3 to R-5 and R-9 to R-11**: "the 107-query row at `m = 10`
is round-by-round sound (and knowledge sound) from DKT26 Theorem 4.4 and Corollary 6.6, whose
statement is formalized in ArkLib at revision X, with no further unproved step". On Haböck's route
alone, the same sentence additionally needs R-2 and R-6, or F-J2 with R-6.

## Appendix: the recomputation script (kept outside the repository; reproduced here)

```python
from math import log2 as L2, sqrt, ceil
rho = 1/8
need = lambda c: c + 1 + L2(20000*601)
qb = lambda m: -L2((1+1/(2*m))*sqrt(rho)) if m else -L2((1+rho)/2)
def queries(m, c): q = ceil(need(c)/qb(m)); return q, q*qb(m), (q-1)*qb(m)
Blist = lambda m: (m+0.5)/sqrt(rho)                                     # GS Y-degree
johnson = lambda m: ((1+1/(2*m))*sqrt(rho)-rho)/(((1+1/(2*m))*sqrt(rho))**2-rho)  # DKT26 (38)
bcf = lambda ln, m: 8*2**ln*(m+0.5)**3/(3*(rho-2**-ln))                 # DKT26 (39)
hab = lambda ln, B, m: (m+0.5)/sqrt(rho)*max((m+0.5)**6/(3*rho)*4**ln, 2*(B*2**ln+1))  # Haböck Thm 3/4
b = lambda cnt: 256 - L2(cnt)
# e.g. b(bcf(30,10)+2*Blist(10)) -> 211.41 ; b(hab(30,2,10)) -> 169.34 ; queries(153,128) -> (102, 152.5199, ...)
```

The exact-integer check of DKT26 (109) and (33)–(34) of section 4.2 follows the definitions of
DKT26 Theorem 4.4 (36)–(37) and Proposition B.1 (109) verbatim, with
`A = ceil((1 + 1/(2m)) sqrt(1/8) n)` and `D = n/8 - 1`.
