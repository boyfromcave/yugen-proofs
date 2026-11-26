# Referee report: soundness calculator revision 9 and the ArkLib compose statements

Part of Yugen. `yugen-proofs`, at `a214558`. 2026-11-19. Independent referee; the subjects are
`soundness/` revision 9 with `docs/decision-qrom-counting.md`, and `docs/arklib-lean-check.md` with its `Compose.lean`.

Sources read for this report, from rendered page images (PDFKit, scale 2.2), not the text layer:

- C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, Cryptology ePrint
  Archive, Paper 2026/2615 [SG26] (no venue stated): Theorem 6.6 (2) and Section 6.3 (p. 58), Definitions H.3 (p. 128)
  and H.4, Lemma H.5 (p. 129); Definition I.1 (p. 130) from the text layer.
- Q. Dao, S. D. Kominers, J. Thaler, *Reed-Solomon Codes Beyond Johnson: Efficient Decoding and Smaller Cryptographic
  Proofs*, Cryptology ePrint Archive, Paper 2026/2056 [DKT26] (a preprint): Theorem 4.4 with (36) to (39) (p. 29),
  Corollary 6.4, Lemma 6.5 (p. 37), Corollaries 6.6, 6.7 (p. 38).
- ArkLib at `6aa8b6fe` (the checkout in `third-party/arklib`, unmodified before and after).

Provenance of this report: the recomputation, the findings and the two unfolded Lean restatements are **Original (the
Ycash developers, 2026)**, first here, unreviewed. Every bound used is **Published** at the place named.

## 0. Verdicts

| Subject | Verdict |
|---|---|
| (i) Revision 9 counts, system B | **PASS WITH CONDITIONS** (R9-1, R9-2, R9-4) |
| (ii) Revision 9 counts, system A | **PASS WITH CONDITIONS** (R9-1, R9-4: margins down to 0.001 bit on an estimated `k_q`) |
| (iii) The Lean compose statements | **PASS** (minor: L-2, L-3, L-6) |
| (iv) Candidate rows 111 and 82 | **Not yet "certified".** The coding-theory statements they need are now machine-checked, which is stronger than "rests on a preprint"; what stands in the way is listed in section 3.4 |

Every count named in the task reproduces exactly from a script that imports nothing from the calculator (section 1.2).
No BLOCKER was found.

## 1. Subject 1: revision 9

### 1.1 (a) The per-round need, derived from the paper before the code was read

[SG26] Theorem 6.6 (2), ROM part (Published): `eps^C_ex(t) = (t + k_q)(eps^k + c'(t + k_q)/2^(8b))`, an adaptive
soundness error by Definition H.4 "for every t ∈ N and every (t, 0)-adversary" (and Lemma H.5, with oracle simulation
error 0). `eps^k` is a bound on every round's error, so the factor `(t + k_q)` multiplies one round's error, not the
sum over rounds.

Tree of `N` proofs: a forged tree has a node whose proof is accepted for a false statement
(`soundness-method.md` 8.5b); the tree adversary, restricted to that node, is a `(t, 0)`-adversary against that
proof, so `eps_tree(t) <= sum_v (t + k_q,v)(eps_v + c'_v (t + k_q,v)/2^(8b))`. The project's claim is
`eps_tree(t) <= t/2^kappa_C` for `1 <= t <= 2^kappa_C`, half of it for the IOP term:
`N (t + k_q) eps <= t / 2^(kappa_C + 1)`. `(t + k_q)/t` is largest at `t = 1`, so

    e >= kappa_C + 1 + log2 N + log2(1 + k_q)      = 143.288 + log2(1 + k_q) at category 1, N = 20,000.

This is the calculator's formula. Answers to the questions put:

- **Why the need differs per row.** Only through `k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2 l_max)))`
  (Definition I.1): the row's opened positions and largest tree. `k_q` grows with the query count, so each row is a
  fixed point; iterating upward from a count below it reaches the least one. Each proof at its own `k_q` is correct
  for the union: every summand is at most `2^-(kappa_C+1)/N`.
- **Double-counted: nothing.** The verifier's `k_q` enters once per proof; `log2 N` once; the round count does not
  enter (it did in the book's `1 + k`).
- **Salt terms.** The ROM extraction error has none (Section I.1: knowledge soundness holds "at every salt length,
  including 0"). The QROM part's stream term `2 sqrt(k_q / 2^(8(b+e)))` is computed and negligible.
- **De-duplicated positions.** `q_IOP` is charged without de-duplication (an upper bound, Definition I.1 "at most
  `q_IOP` queries"), and the query round's error uses all `q` independent samples. Consistent.
- **Missed: the hash term of the same bound** (finding R9-1 below).
- **Load-bearing estimate:** `k_q` (finding R9-4).

### 1.2 (b) Independent recomputation

Script (referee's scratch, not committed; Python, no import from `yugen_soundness`): the need above; Definition I.1's
`k_q` with the project's inputs (B: `N_msg = 1,200`, six trees, `l_max = 2^(28 + r)`; A: `N_msg = 2 (rounds + 512)`,
`l_max` the largest level); B's per-query bits `-log2((1 + rho)/2)` and, in the Johnson regime, `-log2(A/n)` with
`A = ceil((1 + 1/(2m)) sqrt(rho) n)` in exact integers; A's level schedule, true rates `(2^mu + k)/2^(mu + r)` and,
for the masked leaves, the hiding layout. Least counts found by stepping up, then trimming.

| Row | Claimed | Recomputed | `k_q` | Need | Margin (bits) |
|---|---|---|---|---|---|
| B unique decoding 1/8 | 192 | 192 | 40,416 | 158.590 | +0.784 (191 short by 0.039) |
| B Johnson `m = 10` 1/8 | 111 | 111 | 24,378 | 157.861 | +0.826 |
| B Johnson `m = 10` 1/16 | 82 | 82 | 19,128 | 157.511 | +0.717 |
| B node 1/4 | 235 | 235 | 47,520 | 158.824 | +0.523 (234 short by 0.149) |
| B 1/16 | 174 | 174 | 37,896 | 158.498 | +0.284 |
| B 1/2 | 385 | 385 | 74,010 | 159.463 | +0.326 |
| B Johnson node 1/4 (arithmetic only) | 171 | 171 | 35,232 | 158.392 | +0.571 |
| A row 8, `2^22`, 1/4 | 233, 166, 168, 185 | same | 17,436 | 157.378 | +0.105 |
| A row 7, `2^22`, 1/4 | 233, 165, 165, 165 | same | 16,684 | 157.314 | +0.192 |
| A row 6 mode 0, `2^22`, 1/4 | 233, 162, 159, 159 | same | 18,082 | 157.430 | +0.307 |

Also reproduced: row 6 mode 1 (234, 161, 159), row 8 at 1/2 (386, 174, 180, 228) and at `2^21` (234, 166, 172, 228),
row 7 at 1/2 (380, 173, 173, 173), all fourteen row-9 node stacks `2^24` to `2^30` at both rates, and categories 3
and 5 (B 269 / 245, 347 / 315; A node `2^30` 538, 245 x5, 246, 254 at category 3). Limits of independence: the masked
leaves' layout was re-implemented from the description in `wi.py`'s header, not derived from `zk-wi-soundness.md`;
the number of listed rounds (87, 82, 19, 27 to 35) was counted from the round lists.

### 1.3 (c) Tree QROM bits

Computed by the theorem's formula, not a shortcut: `spbcs.SpbcsTree` solves `N 6 (t + k_q)^2 eps^k = 1/2` and
`N 6 c' (t + k_q)^3 / 2^(8b) = 1/2` with `k_q` added exactly, and checks the stream term separately. The referee's
solve of the **full sum** `N eps_ex(t) = 1/2` gives A 69.579, B 70.454: the same to three decimals (the hash and
stream terms are negligible). NOTE R9-6: "69.58 bits" is the query count at which the tree bound reaches 1/2; at
`t = 2^64` the bound is `2^-12.2` (A), `2^-13.9` (B). The claim in the form `eps(t) <= t/2^65` is the separate need
145.87 bits a round, which every row exceeds. With system B's documented counter-mode alternative (Lemma X) B is 69.45.

### 1.4 Findings

**R9-1 (MAJOR; `docs/decision-qrom-counting.md` 0 and 2.2, `soundness-method.md` 8.9, `category.derivation_table`).**
Revision 9 takes the `eps^k` term from [SG26] "as stated" but leaves the hash term to the book's `3.5 t^2/2^lambda`,
"taken out once" for the tree. The theorem as stated carries `c'(t + k_q)^2/2^(8b)` **per proof**. Summed over the
tree, in the calculator's own convention (`N c' t / 2^256 <= 2^-(kappa+1)` at `t = 2^kappa`), the proven classical
level of the hash part is **114.8 bits (A, `c'` = 2,189), 114.7 (B, `c'` = 2,401)**, not the documented 126.6; the
digest the proven rule needs is `2 kappa_C + 1 + log2(N c')` = 282.5, so 288 bits, not the printed 264. The tree claim
`eps_tree(t) <= t/2^128` is therefore proved by [SG26] only up to about `t = 2^101`. No query count changes (the
classical level already rests on condition H's attack rule), but "certified (every t)" reads as more than is proved.
Fix: evaluate and print the [SG26] hash term per profile beside "Digest, proven rule"; state in 8.9 and in the decision
record that every t is certified for the IOP term and that the hash part rests on condition H; or prove that the
collision event can be shared across the tree and label that lemma Original.

**R9-2 (MAJOR; `dkt26.row`, `category.b_row`).** Two library paths print old-convention counts as certified (no
command-line flag reaches them):
`dkt26.row("x", "ud", 3, None, need_bits=152.52)` returns 184 queries with status "certified (unique decoding; ...;
every t, Sharp-Grubbs ...)"; `category.b_row("leaf", 3, PROFILES[1], queries=184)` returns status "certified", and
`rows_table` prints "certified (every t)" beside margin -5.80. The private `_a_node_at` / `_a_leaf_at` return the book
row with the default status "certified". Fix: a row is certified only if the convention is every t, the need was not
overridden and the row meets it; otherwise "fixed need, not certified" or "DOES NOT MEET"; make `Row.status` default
to a non-certified value; one test per path.

**R9-3 (MINOR; `category.tables`, `dkt26.tables` under `--convention t-ge-kq`).** No row table prints a certified
status under the flag, and each category block has the banner. But the summaries still say "every certified shape",
"Largest certified proof", "the category's certified rows' weakest round", and the cross-check row
"B node, unique decoding, 1/4 | 225 | 225 | ... (certified count)"; the sections after the category blocks (M-1,
field minimum, sizes, QROM by digest, salt floors) are covered only by the title line. Fix: switch those words on the
convention and repeat the banner before each summary.

**R9-4 (MAJOR for A, MINOR for B; `category.a_row_kq`, `b_counts`).** `k_q` was an estimate (E) that fed only the QROM
figure, where it is negligible. It now sets certified counts. System A's rows have margins of +0.0011 (`2^24`, 1/2),
+0.0016 (`2^25`, 1/4), +0.003 and +0.004 (`2^30`), +0.02 (row 8, 1/2), +0.03 (row 6 mode 1): a `k_q` 0.1 % higher
breaks the first. The inputs look like upper figures (B's leaf is charged six paths of depth 31 against built depths
20, 21, 18, 15, 12, 10, `yugen-proof-b2` `parameters.md` 8.3), but nothing proves `k_q >=` the built verifier's count
for A (`OTHER_ROUNDS = 512`, `m = 2`, one prover message a round are marked E). Fix: make task T-1 a condition of the
label (the transcript modules report `N_msg`, `n_B`, `q_IOP`, `l_max`; a test asserts the calculator's `k_q` is at
least the reported one), and until then either print "certified given k_q (E)" or solve A with a stated allowance.

**R9-5 (MINOR; `category._a_leaf_at`).** Under every t a field refusal prints the book need
("fold0.0 gives 104.0 < 216.51 bits" at category 3), because the book row is solved first. The refusal fires
correctly. Fix: solve the every-t row first, or name the convention in the message.

**R9-7 (NOTE; (f), the D-term).** Checked: revision 8's output at `b8f30bc` printed `6 x 7` for the 184 row; revision
9 prints `7 x 7 = 49`, 250.39 bits, which is the builder's `49 / 2^256` (`yugen-proof-b2` `parameters.md` 11.3); the
107 row keeps `6 x 7`. The 192 / 111 / 82 rows reuse the terminal dimensions of the 184 / 107 / 80 builds (the module
says no build exists at the new counts); the term is 90 bits above the need either way.

**R9-8 (NOTE).** [SG26] is itself an ePrint with no venue. Every "certified (every t)" row of both systems rests on
it; the label names it, and it should be read as a dependence on a preprint as the DKT26 label is.

### 1.5 (d), (e)

(d) Command line: `--convention t-ge-kq` alone and with `--rev7`, `--rev8`, `--rev9`, `--category 1`, `--category 3`,
`--rev8 --category 3` was run; every row with a status reads "non-default convention (t >= k_q), not certified"; with
a record flag the option is refused. Remaining leaks: R9-2 (library), R9-3 (summary wording).

(e) Categories 2 and 4 equal 1 and 3. Category 3: A's `2^30` node at rate 1/2 is 538, 245 x5, 246, 254 (recomputed)
and prints 1,799 KiB with "no" under PROOF_BYTES_MAX (1,835,008 B): **confirmed** as printed (the size model itself
was not re-derived). Refusals fired: category 3 with 256-bit digests, with a 128-bit field, with 32-byte leaf salts;
category 5 at GF(2^256); `dkt26.row` with `m` = 2, None, 10.0, True, and Haböck's route. The Johnson candidates at
category 3 print "does not meet the need".

## 2. Subject 2: the Lean compose statements

### 2.1 What was run

`Compose.lean` was extracted from the document and compiled against the built library
(`lake env lean`, Lean 4.35.0, no rebuild, the checkout untouched): exit 0, the three theorems depend on
`propext`, `Classical.choice`, `Quot.sound` only. The file contains no `sorry`, `native_decide`, `decide`, `axiom`,
`implemented_by` or `extern`; `open Classical` supplies decidability instances only. A `native_decide` anywhere in
the closure would show as `Lean.ofReduceBool`; it does not.

To test what the statements mean, the referee added to a scratch copy two restatements with **every ArkLib
definition unfolded** and proved them from the author's theorems (compiled, same three axioms):

- `ref_F1_unfolded`: for `domain : Fin n ↪ F`, any finite `κ`, `D + 1 <= A`, `n D < A A`, and any finite set `T` of
  arrays `c : Fin n → κ → F` such that every row `j` is `i ↦ p.eval (domain i)` for some `p` of degree `< D + 1` and
  `A <= #{i | ∀ j, c i j = received i j}`: `T.card <= n (A - D) / (A A - n D)`.
- `ref_F2_unfolded`: under `1 <= D <= n - 2`, `0 < eta`, `(sqrt(D/n) + eta) n <= A <= n`, for arrays `u, v`:
  `∃ bad : Finset F, bad.card <= ⌊johnsonExceptionCount n D A eta⌋₊ ∧ ∀ z ∉ bad, ∀ Q : κ → F[X]` with every
  `deg Q j < D + 1`, if `A <= #{i | ∀ j, (Q j)(domain i) = u i j + z v i j}` then `∃ P0 P1` of degree `< D + 1` with
  `Q j = P0 j + C z * P1 j` for every `j` and
  `{i | ∀ j, (Q j)(domain i) = u i j + z v i j} = {i | ∀ j, (P0 j)(domain i) = u i j ∧ (P1 j)(domain i) = v i j}`.
- `ref_instance_rate8`: the real-number hypotheses hold at `n = 2^30`, `D = 2^27 - 1`, `A = 398,606,316` with
  `eta = A/n - sqrt(D/n) > 0` (compiled).

### 2.2 Are these the statements the analysis needs

Compared with `binius-johnson-row.md` 2.2 (F1', F2) and [DKT26] Theorem 4.4, (38), Corollaries 6.4, 6.6, Lemma 3.3.

| Point | Finding |
|---|---|
| Agreement | joint, in columns (all rows at one position), with the **full** agreement set and set equality: F2's form, and stronger than the subset form |
| Interleaving | any finite row type, including the coset widths and the mask pairing; the count does not depend on it |
| Exceptional set | chosen after the pair `(u, v)`, before `z` and before the candidate `Q`: the order Lemma F and J2 use |
| List (F1') | every finite family is bounded, so the list is; rows are polynomial evaluations on an arbitrary injective domain; no field restriction (characteristic 2 and `GF(2^256)` included) |
| Hypotheses not stronger than system B's | exact integers and 80-digit decimals at every level `n = 2^(r+1) .. 2^32`, rates 1/8, 1/16, 1/4, `D = rho n - 1`, `A = ceil(1.05 sqrt(rho) n)`: `1 <= D <= n - 2`, `A <= n`, `D + 1 <= A`, `n D < A^2`, `eta > 0` hold at every level; `johnsonM = 10` at every level |
| Conclusions not weaker | list quantity 19 (1/8), 31 (1/16), 10 (1/4) at every level; Lean count `2^43.89` at the `2^30` line (rate 1/8) and `2^45.82` at the `2^31` line (rate 1/16): the document's figures, 212.11 / 210.18 bits with `2 B_list` |
| Vacuity | none: the hypotheses are instantiated (above), the count is 212 bits below `|K|`, and close candidates exist |
| Challenge field | `z` ranges over `F`, the code's field; system B's challenges are uniform in `K`, over which the code is taken |
| Universe | `F, κ : Type`: no effect |

**L-2 (MINOR; `arklib-lean-check.md` 4 (a) (ii), `soundness/CHANGELOG.md` revision 9 table).** The machine-checked
count is ArkLib's coarser one (coefficient `4 D mu h`): 212.11 / 210.18 bits. The calculator prints 212.14 / 210.19
from [DKT26] (33)-(34), which no Lean theorem checked here proves. The difference is 0.03 bit against 54 bits of
slack. Fix: print the Lean-backed figure beside the exact one and say which is formal.

**L-3 (MINOR).** F1''s uniformity in `n` is on paper only. The referee evaluated the Lean quantity at every level
(above); a test should pin that table.

**L-6 (MINOR).** `Compose.lean` exists only as text inside the document. Fix: commit it (with the two unfolded
restatements, if the lead wants them) under `lean/` with the one-line command and the expected axiom output.

**L-7 (NOTE).** `check_F2_constant_interleaved` gives `C(n, 2) / max(A - 1, 1)` at message dimension 1 for `A >= 1`:
[DKT26] Lemma 3.3's count. It matters only for a shape folded to dimension 1 (the unrecorded rate-1/4 node); the
recorded builds stop at dimension `2^4` or more.

### 2.3 What remains paper-only in the candidate rows' argument, and its weight

| Step | Status | Weight |
|---|---|---|
| Line MCA at the Johnson threshold, its interleaved form, the list bound, dimension 1 | **machine-checked** (ArkLib `6aa8b6fe` + `Compose.lean`); statement compared with the paper and unfolded | was the heaviest; now rests on the Lean kernel, Mathlib and the statement comparison of 2.2 |
| Binius64's code is Reed-Solomon on a `GF(2)`-subspace, and each index / mask / `X` fold round is a line `u + z v` of interleaved words on the folded domain (cosets as rows) | paper (Haböck 2024/1571 Section 6.2, Lemma F) | **high**: it is where the protocol meets the theorem |
| Lemma U, J1 (ring switch, `8 B_list`), J2 (mask round), J3 (lifted oracles; H7, H8'; BR-1 to BR-5) | paper, Original, refereed twice inside the project | **high** |
| Lemma F's weighted-to-unweighted step; composition across fold levels ([DKT26] Corollary 6.7; ArkLib's `tensorFoldBad_card_le` not checked) | paper | medium |
| Lemma K (round-by-round **knowledge**, list extractor, polynomial-time list decoding from [DKT26] Corollary 9.4, statement only) | paper | **high**: [SG26] Theorem 6.6 (2) asks round-by-round knowledge soundness |
| Query round `(A/n)^q`, list size not entering it | paper | medium |
| [SG26] Theorem 6.6 (2) and the transcript as built being spBCS (`qrom-compilation.md` 2.8) | Published preprint; deviations paper | high |
| `k_q` (E), the hash term (R9-1), the in-circuit oracle heuristic C2 | estimate / heuristic | as in section 1 |
| F1' uniformity in `n` | paper; numerically closed here | low |

### 2.4 (iv) May 111 and 82 be called certified with a stated dependence on a preprint

The dependence on [DKT26] has changed in kind: the three statements the rows use are machine-checked, with clean
axioms, and their unfolded meaning is the analysis's F1' and F2. That part no longer needs the words "rests on a
preprint's proof". In the referee's judgement the rows may be called **"certified, conditional on stated
dependences"** once the following are done, and not before:

1. The label names all three dependences: ArkLib `6aa8b6fe` with `Compose.lean` (machine-checked statements of
   [DKT26]); this project's Lemmas U, J1, J2, J3, F, K (Original, refereed only inside the project); [SG26] (a preprint).
2. R9-1 and R9-4 are closed (the hash term stated; `k_q` reported by the transcript module).
3. Conditions C-4, C-6 and C-7 of `johnson-row-referee-2.md` are met **at 111 and 82**: no build at these counts was
   seen by this referee, and the decision record says the rate-1/8 candidate leaf slot does not fit `2^21`.
4. The lead architect's decision (`dkt26.DKT26_ACCEPTED`) is recorded.

The rate-1/4 Johnson node (171) stays arithmetic only.

## 3. Not checked

The Johnson rows' algebraic terms (taken from the revision 8 referee); the proof-size model and its anchors; every
zero-knowledge figure; system A's fold and out-of-domain terms; the masked layout against the build; whether `k_q`
bounds the built verifiers' hash counts; [SG26]'s proof and whether the transcripts as built are spBCS; the proofs of
Lemmas U, J1 to J3, F, K; ArkLib's proofs beyond kernel acceptance of the prebuilt library (no rebuild; the `.olean`
files were trusted); the builders' repositories and their tests; the other repositories' stale counts listed in the
decision record's appendix.
