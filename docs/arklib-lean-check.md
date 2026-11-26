# ArkLib Lean check of the Johnson-regime statements (condition C-1)

Condition C-1 of `johnson-row-referee-2.md` (section 7, R-1 (a)): build ArkLib at the revision
DKT26 names and print the axioms of the four declarations system B's 107-query (rate 1/8) and
80-query (rate 1/16) rows rest on. Run on 2026-11-19 on this machine.

**Result: C-1 met.** The build succeeds and each of the four theorems depends only on `propext`,
`Classical.choice` and `Quot.sound`. The statements say what the analysis uses, with the
differences listed in section 4. None of them weakens the row. Two of the analysis's steps had
no single ArkLib declaration: the Johnson line theorem composed with the width transfer, and
the joint-list bound for interleaved words. Both were stated and proved here in a separate check
file against the built library (section 3.2). They compile, and their axioms are the same three.

**Revision note (2026-11-19, after `docs/rev9-and-lean-referee.md`; not a rewrite).** L-6: the check file of section
3.2 is now committed as `lean/Compose.lean`, the text identical to section 3.2 below a header naming ArkLib
`6aa8b6fe8059cecc0e53607ca811a933a0f8e0b7` and `leanprover/lean4:v4.35.0`; recompiled 2026-11-19 from the
committed file (`lake env lean`, exit 0, the same three axioms for each theorem; the warning's line is 79 there, 65
here); a test (`soundness/tests/test_revision10.py`) asserts the identity. L-2: the calculator prints the
machine-checked count (ArkLib's `johnsonExceptionCount`, coefficient `4 D mu h`: **212.11 / 210.18** bits) beside
DKT26's exact (33)-(34) (**212.14 / 210.19**, paper only), each labelled; the formal figure is the Lean-backed one.

Source: Q. Dao, S. D. Kominers, J. Thaler, *Reed–Solomon Codes Beyond Johnson: Efficient Decoding
and Smaller Cryptographic Proofs*, IACR ePrint 2026/2056, version of November 2, 2026 (preprint;
"DKT26"). Their reference [DA26] (Q. Dao and ArkLib contributors, *ArkLib: Reed–Solomon capacity
and correlated agreement in Lean*, `https://github.com/quangvdao/ArkLib`, "Revision 6aa8b6fe,
November 2, 2026") and their Appendix H ("start with `ReedSolomon/PaperGuide.lean`") give the
revision and the entry point checked here. Provenance: the four theorems and their proofs are
**Published** (ArkLib at `6aa8b6fe`). The three composition statements in `Compose.lean` and
their proofs, and the comparison in section 4, are **Original (the Ycash developers, 2026)**,
first in this document. They only assemble published ArkLib declarations, and DKT26 Corollaries 6.4
and 6.6 state the same compositions on paper.

## 1. Versions

| Item | Value |
|---|---|
| ArkLib | `https://github.com/quangvdao/ArkLib`, commit `6aa8b6fe8059cecc0e53607ca811a933a0f8e0b7` (merge commit of 2026-11-02, "Merge remote-tracking branch 'origin/main' into rs-beyond-johnson-stoc-submission"), detached HEAD, working tree unmodified (`git status` empty after the build) |
| `lean-toolchain` at that commit | `leanprover/lean4:v4.35.0`, the same as the referee's expectation (no difference) |
| Lean | `Lean (version 4.35.0, arm64-apple-darwin24.6.0, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)`; Lake `5.0.0-src+eb6cafb` |
| elan | 4.4.0 (`3cc76985a`, 2026-11-18). The installer `elan-init.sh` came over HTTPS from `raw.githubusercontent.com/leanprover/elan/master` (SHA-256 `a620ff1641616222c8d37c54845492004bb84d6877cdbc944dd65c1aa685bf53`) and fetched its binary from `github.com/leanprover/elan/releases` |
| Mathlib | `56a005855ea17e0b0958f73ec801ae140b0a1679` (from `lake-manifest.json`, and the same as the checked-out `.lake/packages/mathlib` HEAD). Prebuilt from `cache.mathlib.org` (9031 files) |
| Other pinned dependencies (manifest = checkout) | CompPoly `06686e4c70939af82203af21516f8ab8a21a8051`, VCVio `aae1c9cbd6c00311091d691b74f2d0032d76d9bd`, cslib `5b56df99362532c46e1175381fbbdd755bd56030`, PolyFun `4181c82238142d9b73403fbf4c4b13e1a801e400`, batteries `66e469188fe07963e5cf666c7d4433f45b8131c5`, aesop `4a174c490d8707121c4a9290800489f105d85e07` (full list in ArkLib's `lake-manifest.json` at the commit) |

## 2. Commands (exact)

```sh
# elan, no shell-profile change, no default toolchain
curl --proto '=https' --tlsv1.2 -sSfL -o elan-init.sh https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh
sh elan-init.sh -y --no-modify-path --default-toolchain none
export PATH=$HOME/.elan/bin:$PATH        # explicit in every command; nothing added to profiles

# ArkLib, read-only upstream checkout outside every Yugen repository
mkdir -p $YUGEN_ROOT/third-party
cd $YUGEN_ROOT/third-party
git clone --filter=blob:none https://github.com/quangvdao/ArkLib.git arklib
cd arklib && git checkout 6aa8b6fe
elan toolchain install leanprover/lean4:v4.35.0   # = lean-toolchain

# dependencies + Mathlib's prebuilt cache (no Mathlib build from source)
lake exe cache get

# only the four modules and their import closure, not all of ArkLib
# (run niced, untimed: nice -n 10 <script>)
lake build \
  ArkLib.Data.CodingTheory.ReedSolomon.MutualCorrelatedAgreement.Johnson.Agreement \
  ArkLib.Data.CodingTheory.ReedSolomon.Interleaved.PowerAgreement \
  ArkLib.Data.CodingTheory.ReedSolomon.PowerAgreement.ConstantCode \
  ArkLib.Data.CodingTheory.ReedSolomon.ListDecodability.PairwiseJohnson
#   -> "Build completed successfully (3907 jobs)."; no error, no "declaration uses `sorry`" warning in the log

# axioms (check files kept outside the ArkLib tree; sources in 3.1 and 3.2)
lake env lean AxiomCheck.lean
lake env lean Compose.lean
```

The build compiled 230 ArkLib modules and 87 modules of ArkLib's own dependencies (CompPoly,
VCVio, cslib, PolyFun and their `ToMathlib` parts; CompPoly's prebuilt release could not be
fetched, so those were built from source). Mathlib came from the cache. The run was untimed under
the heavy slot (load was 17 when it started), so no timings are reported. Its peak resident memory
was 2.4 GB (the heavy slot's sample of the whole process group), well under the 6 GB per-process
limit. Nothing from the downloaded tree was run except the Lean/Lake build and Mathlib's `cache`
executable that `lake exe cache get` builds.

## 3. Axiom output (verbatim)

### 3.1 The four theorems (`AxiomCheck.lean`)

```lean
import ArkLib.Data.CodingTheory.ReedSolomon.MutualCorrelatedAgreement.Johnson.Agreement
import ArkLib.Data.CodingTheory.ReedSolomon.Interleaved.PowerAgreement
import ArkLib.Data.CodingTheory.ReedSolomon.PowerAgreement.ConstantCode
import ArkLib.Data.CodingTheory.ReedSolomon.ListDecodability.PairwiseJohnson

#check @ReedSolomon.exists_johnson_line_exactCorrelatedPair
#print axioms ReedSolomon.exists_johnson_line_exactCorrelatedPair
#check @ReedSolomon.uniformExactInterleavedPowerAgreement_of_scalar
#print axioms ReedSolomon.uniformExactInterleavedPowerAgreement_of_scalar
#check @ReedSolomon.uniformExactPowerAgreement_constantCode
#print axioms ReedSolomon.uniformExactPowerAgreement_constantCode
#check @ReedSolomon.closePolynomialSet_finite_and_ncard_le_pairwiseJohnson
#print axioms ReedSolomon.closePolynomialSet_finite_and_ncard_le_pairwiseJohnson

-- supporting declarations the comparison relies on
#print axioms ReedSolomon.HiddenDerivative.johnsonExceptionCount_lt_closed
#print axioms ReedSolomon.powerAgreement_one_of_exactCorrelatedPair
#print axioms Code.finset_card_le_pairwiseJohnson

-- control: the same command must report sorryAx for a declaration that uses sorry
theorem control_uses_sorry : (1 : ℕ) = 2 := by sorry
#print axioms control_uses_sorry
```

Output (`lake env lean AxiomCheck.lean`, exit 0), verbatim:

```
@ReedSolomon.exists_johnson_line_exactCorrelatedPair : ∀ {F : Type u_1} [inst : Field F] {n D A : ℕ} {eta : ℝ}
  (domain : Fin n ↪ F) (f g : Fin n → F),
  1 ≤ D →
    D ≤ n - 2 →
      0 < eta →
        ReedSolomon.HiddenDerivative.johnsonAgreement n D eta * ↑n ≤ ↑A →
          A ≤ n →
            ∃ exceptional,
              ↑exceptional.card ≤ ReedSolomon.HiddenDerivative.johnsonExceptionCount n D A eta ∧
                ∀ z ∉ exceptional,
                  ∀ (P : Polynomial F),
                    P.degree < ↑D + 1 →
                      A ≤ (ReedSolomon.polynomialAgreementSet domain (fun i => f i + z * g i) P).card →
                        ReedSolomon.HasExactCorrelatedPair domain f g (RingHom.id F) (D + 1) z P
'ReedSolomon.exists_johnson_line_exactCorrelatedPair' depends on axioms: [propext, Classical.choice, Quot.sound]
@ReedSolomon.uniformExactInterleavedPowerAgreement_of_scalar : ∀ {F : Type} {ι : Type u_1} {κ : Type u_2}
  [inst : Field F] [inst_1 : Fintype ι] [inst_2 : Fintype κ] [inst_3 : DecidableEq F] {ℓ : ℕ} (domain : ι ↪ F)
  {k L e : ℕ},
  (∀ (w : Fin (ℓ + 1) → ι → F), ReedSolomon.UniformExactPowerAgreement domain w k L e) →
    k ≤ L → ∀ (values : Fin (ℓ + 1) → ι → κ → F), ReedSolomon.UniformExactInterleavedPowerAgreement domain values k L e
'ReedSolomon.uniformExactInterleavedPowerAgreement_of_scalar' depends on axioms: [propext, Classical.choice, Quot.sound]
@ReedSolomon.uniformExactPowerAgreement_constantCode : ∀ {F : Type u_1} {ι : Type u_2} [inst : Field F]
  [inst_1 : Fintype ι] [inst_2 : DecidableEq F] {ℓ : ℕ} (domain : ι ↪ F) (w : Fin (ℓ + 1) → ι → F) (A : ℕ),
  ReedSolomon.UniformExactPowerAgreement domain w 1 A (ℓ * (Fintype.card ι).choose 2 / max (A - 1) 1)
'ReedSolomon.uniformExactPowerAgreement_constantCode' depends on axioms: [propext, Classical.choice, Quot.sound]
@ReedSolomon.closePolynomialSet_finite_and_ncard_le_pairwiseJohnson : ∀ {F : Type u_1} [inst : Field F] {n D A : ℕ}
  (domain : Fin n ↪ F) (received : Fin n → F),
  D + 1 ≤ A →
    n * D < A * A →
      (ReedSolomon.closePolynomialSet domain received (D + 1) A).Finite ∧
        (ReedSolomon.closePolynomialSet domain received (D + 1) A).ncard ≤ Code.pairwiseJohnsonListBound n D A
'ReedSolomon.closePolynomialSet_finite_and_ncard_le_pairwiseJohnson' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ReedSolomon.HiddenDerivative.johnsonExceptionCount_lt_closed' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ReedSolomon.powerAgreement_one_of_exactCorrelatedPair' depends on axioms: [propext, Classical.choice, Quot.sound]
'Code.finset_card_le_pairwiseJohnson' depends on axioms: [propext, Classical.choice, Quot.sound]
AxiomCheck.lean:21:8: warning: declaration uses `sorry`
'control_uses_sorry' depends on axioms: [sorryAx]
```

Each of the four theorems (and the three supporting declarations) reports exactly
`[propext, Classical.choice, Quot.sound]`. The control line shows that the same command does
report `sorryAx` for a declaration that uses `sorry`. `#print axioms` follows the whole
transitive closure of constants, including Mathlib's and the dependencies', so this rules out
`sorry` and any added axiom behind the four statements. It does not cover `implemented_by` or
`@[extern]` tricks that do not appear as axioms. The referee's source scan (`johnson-row-referee-2.md`
4.3) found none in the import closure.

### 3.2 Compositions the analysis uses (`Compose.lean`)

```lean
import ArkLib.Data.CodingTheory.ReedSolomon.MutualCorrelatedAgreement.Johnson.Agreement
import ArkLib.Data.CodingTheory.ReedSolomon.MutualCorrelatedAgreement.PowerToLine
import ArkLib.Data.CodingTheory.ReedSolomon.Interleaved.PowerAgreement
import ArkLib.Data.CodingTheory.ReedSolomon.PowerAgreement.ConstantCode
import ArkLib.Data.CodingTheory.ReedSolomon.ListDecodability.PairwiseJohnson

/-! Check file (not part of ArkLib): composes the four upstream theorems into the three
statements the analysis uses (interleaved line MCA in the Johnson regime, interleaved
constant-code line MCA, interleaved joint-list bound). -/

open Polynomial ReedSolomon HiddenDerivative

open Classical in
/-- F2, Johnson, k = D + 1 >= 2, any width: Theorem 4.4 (line) composed with Corollary 6.6. -/
theorem check_F2_johnson_interleaved
    {F : Type} [Field F] {n D A : ℕ} {eta : ℝ} {κ : Type} [Fintype κ]
    (domain : Fin n ↪ F) (hD : 1 ≤ D) (hDn : D ≤ n - 2) (heta : 0 < eta)
    (hthreshold : johnsonAgreement n D eta * n ≤ A) (hAn : A ≤ n)
    (values : Fin 2 → Fin n → κ → F) :
    UniformExactInterleavedPowerAgreement domain values (D + 1) A
      ⌊johnsonExceptionCount n D A eta⌋₊ := by
  refine uniformExactInterleavedPowerAgreement_of_scalar domain (fun w ↦ ?_)
    (johnson_degree_succ_le_agreement hD (by omega) heta hthreshold) values
  obtain ⟨ex, hcard, hgood⟩ :=
    exists_johnson_line_exactCorrelatedPair domain (w 0) (w 1) hD hDn heta hthreshold hAn
  refine ⟨ex, Nat.le_floor hcard, fun z hz Q hQ hL ↦ ?_⟩
  have hw : w = ![w 0, w 1] := by
    funext t
    fin_cases t <;> rfl
  have hword : powerBatchedWord w z = fun i ↦ w 0 i + z * w 1 i := by
    funext i
    simp [powerBatchedWord, Fin.sum_univ_two]
  have hQ' : Q.degree < (D : WithBot ℕ) + 1 := by exact_mod_cast hQ
  have h := hgood z hz Q hQ' (by rwa [hword] at hL)
  have h2 := powerAgreement_one_of_exactCorrelatedPair domain (w 0) (w 1) (RingHom.id F) z Q h
  rwa [← hw] at h2

open Classical in
/-- F2, message dimension 1, any width: Lemma 3.3 (line, ℓ = 1) composed with Corollary 6.6. -/
theorem check_F2_constant_interleaved
    {F : Type} [Field F] {n A : ℕ} {κ : Type} [Fintype κ]
    (domain : Fin n ↪ F) (hA : 1 ≤ A) (values : Fin 2 → Fin n → κ → F) :
    UniformExactInterleavedPowerAgreement domain values 1 A
      (1 * (Fintype.card (Fin n)).choose 2 / max (A - 1) 1) :=
  uniformExactInterleavedPowerAgreement_of_scalar domain
    (fun w ↦ uniformExactPowerAgreement_constantCode domain w A) hA values

open Classical in
/-- F1', any width: the joint list of an interleaved received word has at most
`⌊n (A - D) / (A² - n D)⌋` members (pairwise Johnson count applied to the interleaved code). -/
theorem check_F1_interleaved_list
    {F : Type} [Field F] {n D A : ℕ} {κ : Type} [Fintype κ]
    (domain : Fin n ↪ F) (received : Fin n → κ → F)
    (hDA : D + 1 ≤ A) (hpositive : n * D < A * A)
    (T : Finset (Fin n → κ → F))
    (hT : ∀ c ∈ T, (∀ j, (fun i ↦ c i j) ∈ code domain (D + 1)) ∧ A ≤ Code.agree c received) :
    T.card ≤ Code.pairwiseJohnsonListBound n D A := by
  have h := Code.finset_card_le_pairwiseJohnson
    {c : Fin n → κ → F | ∀ j, (fun i ↦ c i j) ∈ code domain (D + 1)} received D A (by omega)
    (by simpa using hpositive) ?_ T hT
  · simpa using h
  intro c hc c' hc' hne
  obtain ⟨j, hj⟩ : ∃ j, (fun i ↦ c i j) ≠ (fun i ↦ c' i j) := by
    by_contra hall
    push_neg at hall
    apply hne
    funext i j
    exact congrFun (hall j) i
  have hlt := agree_lt_of_mem_code (hc j) (hc' j) hj
  have hle : Code.agree c c' ≤ Code.agree (fun i ↦ c i j) (fun i ↦ c' i j) := by
    unfold Code.agree
    apply Finset.card_le_card
    intro i hi
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hi ⊢
    rw [hi]
  omega

#print axioms check_F2_johnson_interleaved
#print axioms check_F2_constant_interleaved
#print axioms check_F1_interleaved_list
```

Output (`lake env lean Compose.lean`, exit 0), verbatim apart from the file path. The one warning
is a deprecation notice for the `push_neg` tactic in this check file, not in ArkLib:

```
Compose.lean:65:4: warning: `push_neg` has been deprecated. Prefer using `push Not` instead.
If you'd rather continue using `push_neg` in your project, you can implement it as follows:
```
open Lean.Parser.Tactic in
macro "push_neg" cfg:optConfig loc:(location)? : tactic =>
  `(tactic| push $cfg:optConfig Not $[$loc]?)
```
'check_F2_johnson_interleaved' depends on axioms: [propext, Classical.choice, Quot.sound]
'check_F2_constant_interleaved' depends on axioms: [propext, Classical.choice, Quot.sound]
'check_F1_interleaved_list' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## 4. Do the Lean statements say what the analysis uses?

Compared with `binius-johnson-row.md` 2.2 (F1', F2), 8.4, and with DKT26 Theorem 4.4 (p. 29–30),
Lemma 3.3 (p. 16), Lemma 6.5 and Corollary 6.6 (p. 37–38), all read in the paper for this check.

**(a) `exists_johnson_line_exactCorrelatedPair` vs DKT26 Theorem 4.4 (MCA part) and F2 (Johnson,
`k >= 2`).** The two match on every point the analysis needs:
- the field is any `Field F`, so characteristic 2 and the 256-bit field `K` are included;
- the evaluation points are any injective `domain : Fin n ↪ F`, so a `GF(2)`-subspace domain is
  included;
- the hypotheses are `1 <= D <= n - 2`, `eta > 0` and `(sqrt(D/n) + eta) n <= A <= n`;
- the set is chosen once for the line (after `f, g`, before `z` and `P`);
- the conclusion is the full-agreement-set form: degree-`<= D` `F_0, G_0` with `P = F_0 + z G_0`
  and agreement set **equal** to the common one (`HasExactCorrelatedPair`).

`johnsonM`, `johnsonMu` and `johnsonH` are DKT26's `m`, `B_jet` and `B_Z` of (36)–(37), with
`rho_- = D/n`. Differences:
- (i) DKT26 fixes `A = ceil(a n)` with `a <= 1`, while Lean allows any integer `A` in the range. That
  is more general and covers the analysis's `A = ceil(a n)`.
- (ii) The count. Lean's `johnsonExceptionCount` is the raw count with coefficient `4 D mu h`, not
  DKT26's exact `E^(1)_ord` (33)–(34). This is the coarser count the referee noted. It is still
  an upper bound for the exceptional set, which is all the row needs.
- (iii) The closed bound `B_cf < 8 n t^3 / (3 rho_-)` (DKT26 (39), the form F2 quotes) is
  `HiddenDerivative.johnsonExceptionCount_lt_closed`, axioms clean (3.1).
- (iv) Lean takes `eta` as the free parameter, and the analysis takes `m = 10` and
  `a = (1 + 1/(2m)) sqrt(rho)`, `rho = (D+1)/n`. With `eta = A/n - sqrt(D/n)`, Lean's `johnsonM`
  evaluates to `10` at both rows, so the formal count is the analysis's case.

At the row sizes, the formula of `johnsonExceptionCount` was evaluated (Python, 60-digit decimals,
scratch script; the formula as in `FiniteBounds.lean` lines 86–108):

| `n`, rate | `D` | `A` | `m`, `mu`, `h` | log2 Lean count | log2 closed (39) | node-fold bits `256 - log2(N + 2 B_list)` |
|---|---|---|---|---|---|---|
| `2^30`, 1/8 | 134217727 | 398606316 | 10, 29, 294 | 43.89 | 44.59 | 212.11 |
| `2^31`, 1/16 | 134217727 | 563714458 | 10, 42, 588 | 45.82 | 46.59 | 210.18 |
| `2^22`, 1/8 (leaf) | 524287 | 1557056 | 10, 29, 294 | 35.89 | 36.59 | 220.11 |

All of these are far below the `2^103.48` the row tolerates (8.4). The bits agree with the referee's
212.11 / 210.18 (`johnson-row-referee-2.md` 4.3).

**(b) `uniformExactInterleavedPowerAgreement_of_scalar` vs DKT26 Lemma 6.5 / Corollary 6.6.**
Same conclusion: one exceptional set of the scalar size `e` for every width; polynomial witnesses
of degree `< k` for every row; equality of the full common column-agreement sets; the hypothesis
`k <= L` is DKT26's `A >= k`. Lean is more general than the paper in two ways. It holds over any
field: the paper's Lemma 6.5 is stated over `F_q` and uses a counting argument there. It also
allows any finite row type, including an empty one. Lean adds one restriction, `F : Type` (universe
0), which does not matter here. The theorem is conditional: its hypothesis must hold for **every**
scalar tuple `w`, as in DKT26. ArkLib has no declaration that discharges that hypothesis with the
Johnson theorem, and the two statements are in different forms: a correlated pair with a real
count against power agreement with a natural count. `check_F2_johnson_interleaved` closes that
gap. It combines (a) with `powerAgreement_one_of_exactCorrelatedPair` and `Nat.le_floor`, and
gives F2 for interleaved lines of any width with count `floor(johnsonExceptionCount)`. It compiled
with clean axioms. This is the statement F2 actually uses.

**(c) `uniformExactPowerAgreement_constantCode` vs DKT26 Lemma 3.3 and F2 (`k = 1`).** Exact
match. For `ℓ + 1` received words (curve degree `ℓ`) the count is
`ℓ * C(n, 2) / max(A - 1, 1)`, which is both cases of DKT26 (6). It holds over any field, with the
full common-witness property. The analysis's line case `ℓ = 1` is
`N_line = floor(C(n, 2)/(A - 1))`. Lean omits Lemma 3.3's first sentence (at most `floor(n/A)`
constants per challenge), which the analysis does not use. The width step ("then Corollary 6.6")
is `check_F2_constant_interleaved`, which compiled with clean axioms.

**(d) `closePolynomialSet_finite_and_ncard_le_pairwiseJohnson` vs DKT26 (38) and F1'.** It gives
the second term of (38), `floor(n (A - D)/(A^2 - n D))`, under `D + 1 <= A` and `n D < A^2`, over
any field. The analysis uses only that term. Finding (no effect on the numbers): the theorem is for
**one** received word, while F1' bounds the joint list of an **interleaved** word. ArkLib's generic
`Code.finset_card_le_pairwiseJohnson` covers any code whose distinct codewords agree on at most
`D` positions, and `check_F1_interleaved_list` applies it to the interleaved code. Its proof is the
analysis's own argument: two distinct tuples differ in a row, so they agree on at most `D` columns.
It compiled with clean axioms. Not formalized: F1''s uniformity step (the bound decreases in `A`
and increases in `D`, so it is below `floor((a - rho)/(a^2 - rho))` for every `n`). At the row sizes
the Lean quantity itself is 19 (rate 1/8) and 31 (rate 1/16), the analysis's `B_list` (table above).

**Outside the scope of these theorems** (not formalized, and not claimed by C-1): Haböck's measure
framework and Lemma F's weighted-to-unweighted step, the fold composition across levels (DKT26
Corollary 6.7 has a Lean form, `TensorMCA.tensorFoldBad_card_le`, not checked here), the
probability and Fiat–Shamir accounting, and the uniform-challenge argument. C-1 covers only the
coding-theory statements.

## 5. Disk use and removal

| Path | Size | What |
|---|---|---|
| `$YUGEN_ROOT/third-party/arklib` | 8.5 GB in `.lake` (Mathlib packages 6.8 GB, ArkLib build 0.4 GB), 8.6 GB in all | ArkLib checkout, dependencies, build |
| `$YUGEN_ROOT/third-party/logs` | small | build and axiom logs of this run |
| `~/.elan` | 2.8 GB | elan and the `v4.35.0` toolchain |
| `~/.cache/mathlib` | 0.45 GB | Mathlib's cache download area, created by `lake exe cache get` |

About 11.9 GB in total. No shell profile was changed, nothing runs in the background, and no Yugen
repository contains any of it. To remove it all:

```sh
rm -rf $YUGEN_ROOT/third-party/arklib $YUGEN_ROOT/third-party/logs
rmdir $YUGEN_ROOT/third-party
rm -rf ~/.elan ~/.cache/mathlib
```

To re-run the check without rebuilding, keep the tree and run the two `lake env lean` commands of
section 2 with the check sources of section 3.
