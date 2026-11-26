-- Compose.lean: the check file of docs/arklib-lean-check.md section 3.2, committed as a file (finding L-6 of
-- docs/rev9-and-lean-referee.md). Everything below the separator line is identical to the text in that section.
-- Not part of ArkLib. Part of Yugen; Original (the Ycash developers, 2026), composing Published ArkLib
-- theorems.
--
-- ArkLib: https://github.com/quangvdao/ArkLib, commit 6aa8b6fe8059cecc0e53607ca811a933a0f8e0b7 (unmodified checkout
--   in $YUGEN_ROOT/third-party/arklib).
-- Toolchain: leanprover/lean4:v4.35.0 (ArkLib's lean-toolchain at that commit).
-- Check (from the ArkLib checkout, after its build; docs/arklib-lean-check.md section 2):
--   lake env lean <path>/Compose.lean
-- Expected: exit 0, one deprecation warning for push_neg, and for each of the three theorems
--   'check_...' depends on axioms: [propext, Classical.choice, Quot.sound]
-- The document's warning cites line 65 of the file without this 14-line header (line 79 here).
-- ---------------------------------------------------------------------------------------------------------------
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
