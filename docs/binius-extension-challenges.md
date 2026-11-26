# System B on Binius64: 128-bit trace and commitments, 256-bit challenges

Part of Yugen. 2026-11-19. Subject: task A-8 of `yugen-proof-b2/docs/parameters.md`
section 2a.5, widened to the whole protocol: keep the trace and the first commitment in
`L = GF(2^128)` (GHASH) and draw every verifier challenge from `K = GF(2^256)` (`GhashSq256b`,
`K = L[Y] / (Y^2 + X Y + X)`).

Marks on every claim:

| Mark | Meaning |
|---|---|
| **S** | read in the vendored source, `yugen-proof-b2/vendor/binius64/crates/`, path given |
| **D** | read in the named document |
| **P** | proved in this document |
| **X** | checked by exact computation in `ext-challenge/` (test named) |
| **M** | measured by the implementers (`parameters.md` 2a) |
| **E** | estimate, method stated |
| **mem** | from memory, not checked against a source |
| **U** | not confirmed |

Read for this document: the Binius64 Blueprint of 2026-11-16 (`yugen-b-eval/upstream/papers/
binius64-spec.txt`) sections 4.8, 4.9, 5.1 to 5.5, 7.2; BCIKS20 (ECCC TR20-083, fetched as PDF and
converted to text locally) Theorems 1.2, 1.4, 1.5, 1.6, 4.1 and Remark 1.2 (BCIKS20 numbers follow the folder copy, ePrint 2020/654 revision of July 3, 2021 (`2020-654.pdf` (see REFERENCES.md)); the ECCC TR20-083 copy of May 30, 2020 numbered the affine-space theorem 1.7, the curve theorem 1.6 and the extension-field remark 1.5 (amended 2026-11-19, `CITATION-AUDIT.md` C-41)); the vendored
`verifier/src/ring_switch.rs`, `verifier/src/reduction.rs` (`verify_public_eval`),
`verifier/src/verify.rs` (the ring switch call), `math/src/tensor_algebra.rs`,
`math/src/multilinear/eq_prefix.rs`, `spartan-verifier/src/wrapper/gadgets.rs`, `circuit_elem.rs`,
`spartan-frontend/src/circuit_builder.rs`, `constraint_system.rs` (wire kinds),
`field/src/fields/ghash_sq.rs` (head); `parameters.md` 2 and 2a; `zero-knowledge.md` of
`yugen-proof-b2`. **Not read when this document was written**: Diamond-Posen ePrint 2024/504
(FRI-Binius; the PDF returned HTTP 403), Haböck ePrint 2024/1571 (both read in the citation audit,
below); **still not read**: ePrint 2023/1784, [HMH] (lifted BaseFold). No vendored code was run.
**Read in the second citation pass of 2026-11-19**: Diamond, Posen, "Polylogarithmic Proofs for
Multilinears over Binary Towers", ePrint 2024/504 (Sections 1.3, 2.6, 2.7, 3.1, 4.3, 5.2; the
copy states no date or venue); Haböck, "Basefold in the List Decoding Regime", ePrint 2024/1571
(Sections 3 to 6; the copy states no date). Findings C-11 to C-13 of `CITATION-AUDIT.md`. **Read in the citation audit of
2026-11-19, after this document was written**: Diamond, "Zero-Knowledge Polynomial Commitment in
Binary Fields", ePrint 2025/1015 (in full); Haböck and Al Kindi, "A note on adding zero-knowledge
to STARK", ePrint 2024/1037 (pages 1 to 16); Ben-Sasson, Chiesa, Spooner, ePrint 2016/116
(Theorems 1.5, 7.1, Remark 1.6); Chiesa, Fenzi, Weissenberg, ePrint 2026/391, revision of
2026-11-16 (Lemma 3.29, Appendix B).

Provenance (`../REFERENCES.md`). Published and used: BCIKS20 Theorem 4.1 and Remark 1.2; the
full-mask opening and its soundness sketch (ePrint 2025/1015, Construction 4.1, Theorems 4.2,
4.3), through the Blueprint; the low-coefficient pad (ePrint 2026/391, Lemma 3.29); ring
switching (ePrint 2024/504, Construction 3.1, Theorem 3.5) and the Galois-orbit variant of
Hashcaster that ePrint 2024/504 presents in its Section 1.3 (equations (16) to (20), Figure 4).
**Adapted** (the Ycash developers, 2026): Theorem 1 (form T) is Construction 3.1 / Theorem 3.5 of
ePrint 2024/504 for `GF(2) < K` (`kappa = 8`) applied to the packed polynomial with its upper 128
basis coordinates zero, the 128 zero columns of the message not sent, and the committed oracle
`L`-valued; Theorem 2 (form F) is the Galois-orbit protocol of its Section 1.3 (the orbit of `L`
over `GF(2)`, length 128) with claims and challenges in the larger field `K` (C-13). Original as
far as checked (sources consulted: ePrint 2024/504, 2024/1571, 2025/1015, 2024/1037, 2026/391):
Lemma 4 (descent), the failure of section 6.1, rule Z and Proposition 6, the wrapper
transposition model. Lemma 3 (restriction) states the setting that Haböck, ePrint 2024/1571,
Section 6.3, already uses (commitments over a field `E`, challenges and the code over `F >= E`,
Theorem 6): Adapted. Neither ePrint 2024/504 nor 2024/1571 treats zero knowledge. Zero-knowledge
ring switching **is** published, in another setting: Sharp and Grubbs, *Faster and Smaller
Anonymous Credentials from Standardized Signatures* (GordieHowe), ePrint 2026/2615, Section 5.5
(read 2026-11-19; its Appendix F, Lemmas F.2, F.4 and Theorem F.6, not read): the Hashcaster-form
twisted sums are masked with committed masks, "subfield masks" packed from `[K : S0]` uniform
entries of a subfield (so uniform in `K`) or "squaring-chain masks" in characteristic 2, perfect
HVZK, round error `1/|K|`, for a Ligero commitment. Lemma 4, rule Z and Proposition 6 remain a
different construction (Binius64's mixed field, the mask round and the wrapper); rule Z's principle
(a mask hiding a `K`-valued message must be uniform in `K`) agrees with its subfield masks
(finding C-21). The counting principle behind 6.1 is Published for evaluation queries: ePrint
2024/1037, Lemma 1 and inequality (1) (an extension-field query to a polynomial randomized over
the base field costs `e` base-field degrees of freedom).

## 0. Result

1. **The mixed-field variant is sound with the same per-round errors as the all-`K` build.** Its
   only new verifier step is the ring switch over `GF(2) < L < K` (Theorem 1, error `8 / |K|`,
   proved here, exhaustively checked on `GF(4) < GF(16)`). Everything after the first oracle is
   the all-`K` protocol run by a prover whose first oracle happens to be `L`-valued, so no new
   proximity theorem is needed; the published statement that covers it directly is BCIKS20
   Theorem 4.1 with Remark 1.2 (read). The row is unchanged: **184 queries at rate 1/8, no
   grinding, 152.52 bits a round**.
2. **The ring-switch message grows with the product of the two degrees, not the square**: 128
   elements of `K`, 32,768 bits (pin 16,384; all-`K` 65,536).
3. **A-8 as worded does not shrink the wrapper.** The wrapper's size is the bit transpositions of
   the tensor algebra. Two are on private values (the two ring-switch messages); `2 p` (18 at the
   pin) are on public values, in the public-input check's operand, and that operand is in
   `K (x) K` whatever the packing field. Model fitted to both measured wrappers (section 5.1):
   the mixed variant alone leaves 1.38 M constraints (2^21, as now). **The fix that matters is
   independent of the field: compute public transpositions directly (task W-1)**: 2^21 to 2^19
   constraints for the all-`K` build, to **2^18** with the mixed field. A second form of the ring
   switch (form F, Theorem 2: Frobenius powers in place of bit decomposition) gives 2^17 and
   removes every transposition.
4. **Masks must be sampled in `K`.** A base-field fold mask under an extension challenge reveals
   the whole committed oracle whenever `gamma` is outside `L` (probability `1 - 2^-128`); a
   base-field one-time-pad key reveals half of each padded message. Fix: fold masks, pad keys,
   and blinding values are uniform in `K` (stored as two `L` slots where the oracle's alphabet is
   `L`); the query pad of an `L`-alphabet oracle stays in `L` (section 6; exact tests with
   controls).
5. **The mixed field repairs the wallet leaf, not the recursion.** Leaf (E): 568 KiB against 614
   (model; 618 KiB measured), wrapper 2^18 against 2^21 constraints. The slot that verifies a leaf
   keeps 97 % of its AND rows: they are 184 queries of SHA-256, and the query count does not
   depend on where the trace lives.
6. **Alternatives**: (a) parallel repetition proves nothing beyond one copy under Fiat-Shamir
   (attack run in `ext-challenge/`); (b) 192 bits suffice numerically but no 192-bit field
   contains GHASH; (c) no step can keep 128-bit challenges; (d) **a candidate worth a decision**:
   in a 256-bit field BCIKS20's *proven* Johnson-regime gap is affordable (168 bits at 2^27
   elements), which would put the row at **107 queries at rate 1/8**. Haböck, ePrint 2024/1571,
   Theorem 6 proves the PCS core (row-batched FRI-Binius, list decoding) with the same count; three
   parts of Binius64 as built are outside it (section 7 (d), finding C-11).

## 1. Where each object lives today

`kappa = log2` of the field degree; a *cell* is the group of trace bits packed in one element.
Pin: `K = L = GF(2^128)`. As built at category 1: everything in `GF(2^256)` (S: VENDOR.md change
16; D: `parameters.md` 2a.1).

| Object | Pin | All-`K` (built) | Evidence |
|---|---|---|---|
| Witness | 64-bit words, i.e. bits `w(i, y)` | same | D: Blueprint 4 |
| Packed trace `pi(y)` | 2 words a cell, `GF(2^128)` | 4 words a cell, `GF(2^256)` | S: `prover/src/prove.rs` `pack_witness` (change 16); D: Blueprint 4.8 |
| Committed codeword alphabet (round oracles) | `GF(2^128)`, 16 B | `GF(2^256)`, 32 B | D: Blueprint 5.2 (`Enc_k : K^(2^k) -> K^|E_k|`); M: 2a.4 item 5 |
| Evaluation domain | a `GF(2)`-subspace spanned by the first basis elements | the same subspace (it lies in `L`: basis elements below 128 are GHASH's) | S: `math/src/binary_subspace.rs` `with_dim`; D: 2a.2 field tests; the inclusion is our reading (U until task T-2's test) |
| Zerocheck / sumcheck challenges and round polynomials (BitAnd, BinMul, shift, public input) | `GF(2^128)` | `GF(2^256)` | D: Blueprint 4.3 to 4.9 |
| Three fixed zerocheck coordinates | constants of `GF(2^8)` | same | D: `parameters.md` 2a.3 |
| Ring-switch message `s_hat` | `2^kappa` = 128 elements of 128 bits | 256 elements of 256 bits | S: `verifier/src/ring_switch.rs:64`; D: Blueprint 4.8 step 1 |
| Ring-switch challenge `r''` | 7 coordinates | 8 | S: `ring_switch.rs:74` |
| Operand `t_rs`, evaluated in the tensor algebra `K (x) K` | 128 x 128 bit matrices | 256 x 256 | S: `ring_switch.rs:115-126`, `math/src/multilinear/eq_prefix.rs:76-103` |
| BaseFold: sumcheck messages, fold challenges, folded and terminal codewords | `GF(2^128)` | `GF(2^256)` | D: Blueprint 5.2 |
| Query openings | first-oracle symbols and fold cosets, 16 B a symbol | 32 B | S: `iop/src/fri/verify.rs` |
| Zero-knowledge wrapper: R1CS field, witness `z_wit`, mask table `g'`, dummy constraints | `GF(2^128)` | `GF(2^256)` | D: Blueprint 6; `zero-knowledge.md` 1.2 M9, M10 |
| One-time-pad keys `z_pre` (in round oracle 0) | one element a padded message | same | D: `zero-knowledge.md` M7, M8 |
| Fold masks `w_r`, one per round oracle, same length | `GF(2^128)` | `GF(2^256)` | D: `zero-knowledge.md` M1, M4 |
| Query pad (`q` coordinates of each round oracle) | `GF(2^128)` | `GF(2^256)` | D: `zero-knowledge.md` M2 |
| Leaf salts | 256 bits | 256 bits | D: `zero-knowledge.md` M1a |
| Digests, transcript | SHA-256 | same | |

## 2. The mixed-field variant

`L = GF(2^128)`, `K = GF(2^256)`, `lambda_L = 128`, `lambda_K = 256`, `kappa_L = 7`,
`kappa_K = 8`. `(beta_i)` is the `GF(2)`-basis of `L`; `(gamma_j)` a `GF(2)`-basis of `K` whose
first 128 elements are the `beta_i` (S: the vendored basis of `GhashSq256b` is `beta_i`, then
`Y beta_i`; `parameters.md` 2a.1 "bit `j` of the four words is coefficient `j`").

| Object | Mixed variant |
|---|---|
| Packed trace `pi(y) = sum_i w(i, y) beta_i` | `L`, 2 words a cell, as at the pin |
| Round oracle 0 (keys, trace, pad) | alphabet `L`, 16 B a symbol |
| Every verifier challenge | `K` |
| Sumcheck and zerocheck messages, folded and terminal codewords | `K` |
| Ring-switch message | 128 elements of `K` (`s_hat_i = sum_y b(y) w(i, y)`, `i < 128`) |
| Ring-switch challenge | form T: `r''` in `K^8`; form F: `r''` in `K^7` |
| Wrapper: R1CS over `K`; round oracle 1 (`z_wit`, `g'`) | alphabet `K`, 32 B |
| Keys and blinding values of round oracle 0 | elements of `K`, each stored as two `L` slots `(p, p')` with value `p + Y p'` (section 6.2) |
| Fold masks `w_r` | `K`, for both round oracles; a leaf of oracle 0 is `(L symbol, K symbol, salt)`: 16 + 32 + 32 B |
| Query pad of oracle 0 | `L` (the opened symbols are `L`-valued); of oracle 1: `K` |

The evaluation domain is unchanged and lies in `L`, so the code of the first oracle is
`RS[L, D, k]` and every later code is `RS[K, D_j, k_j]` with `D_j` in `L`.

## 3. The ring switch over `GF(2) < L < K`

Setting (D: Blueprint 4.8). The shift reduction leaves the claim
`sum_{i, y} a(i) b(y) w(i, y) = t` with `a(i) = eq(r_pack, i)`, `r_pack` in `K^7`,
`b(y) = eq_{<n}(r_rest, y)` in `K`, `t` in `K`; `i` ranges over the 128 bits of a cell and `y`
over the cells. The committed oracle is `pi` in `L^n`.

### 3.1 Form T (the code's form with a rectangular message)

1. The prover sends `s_hat` in `K^128`, `s_hat_i = sum_y b(y) w(i, y)`.
2. The verifier checks `t = sum_i a(i) s_hat_i`.
3. The verifier samples `r''` in `K^8` and sets `e_j = eq(r'', j)`, `j < 256`. Let
   `theta : K -> K` be the `GF(2)`-linear map with `theta(gamma_j) = e_j`.
4. Output: the `K`-linear query `sum_y pi(y) t_rs(y) = s_rs` on `pi`, with
   `t_rs(y) = theta(b(y))` and `s_rs = sum_i beta_i theta(s_hat_i)`.

**Theorem 1 (P).** Form T is complete, and for every `pi` in `L^n`, if the claim is false or
`s_hat` is not the honest vector, then the verifier rejects at step 2 or the output query is
false, except with probability at most `kappa_K / |K| = 8 / 2^256` over `r''`.

*Proof.* Completeness: `theta` is `GF(2)`-linear and the `w(i, y)` are bits, so
`sum_y pi(y) theta(b(y)) = sum_{i, y} w(i, y) beta_i theta(b(y)) = sum_i beta_i theta(sum_y w(i, y) b(y))`.
Soundness: fix `pi`, hence `w` and the honest vector `s*`. If `s_hat = s*` and the claim is
false, step 2 rejects. Otherwise `d = s_hat - s*` is a nonzero vector of `K^128`, and by
completeness the query holds iff `R := sum_i beta_i theta(d_i) = 0`. Write
`d_i = sum_j d_ij gamma_j` with bits `d_ij`. Then `R = sum_j e_j c_j` with
`c_j = sum_i d_ij beta_i` in `L`. The `beta_i` are independent over `GF(2)` and the bit matrix
`(d_ij)` is nonzero, so some `c_j` is nonzero. `R` is the value at `r''` of the multilinear
polynomial in 8 variables with coefficient table `(c_j)`, a nonzero polynomial over `K`:
Schwartz-Zippel gives `8 / |K|`. ∎

The proof never uses the tensor algebra; in its terms the two sides are equal elements of
`L (x) K`, and `(c_j)` are the coordinates of their difference on the `256` columns of `K`.

- **X** `test_ring_switch.Completeness`, `SoundnessExhaustive.test_form_T_bound_kappa_over_K`
  (`GF(4) < GF(16)`: every nonzero `d`, every `r''`; the largest number of passing challenges is
  within `kappa_K |K|^(kappa_K - 1)`), `SoundnessStructure.test_form_T_coefficients` (all three
  field pairs).
- **Control X** `test_control_T_with_only_the_base_field_columns_is_unsound`: keeping the pin's
  128 columns (`r''` of 7 coordinates over `L`'s basis) under `K`-valued messages accepts every
  `d` whose coordinates lie on the columns `Y beta_i`, for every challenge. The functional must
  have 256 columns.
- **Control X** `test_control_challenges_from_the_base_field_are_weaker`.

**Message.** `lambda_L` elements of `K`: `lambda_L lambda_K` bits. With the challenge field
fixed it is linear in the packing degree; against the all-`K` build it is half.

**The operand.** `t_rs(rho) = sum_y eq(rho, y) theta(b(y))` is what the code's `eval_rs_eq`
computes in `TensorAlgebra<B1, K>`, i.e. in `K (x)_GF(2) K`, with 256 x 256 bit transpositions
(S: `ring_switch.rs:115-126`): both `rho` and `r_rest` are in `K`, so this part is the all-`K`
build's and **does not shrink with the packing field**. In code, form T is: the message has
`1 << 7` elements, the point is split at 7, `r''` has `F::LOG_DEGREE = 8` coordinates;
`TensorAlgebra::new` already pads a shorter vector to the degree (S: `tensor_algebra.rs:41`), so
the padded transposition gives exactly the `c_j` of the proof (`L`-valued).

### 3.2 Form F (Frobenius powers)

Steps 1 and 2 as in form T. Step 3: the verifier samples `r''` in `K^7`, `e_m = eq(r'', m)`,
`m < 128`, and uses `theta_F(x) = sum_{m < 128} e_m x^(2^m)`. Step 4 as before with `theta_F`.

**Theorem 2 (P).** Form F is complete and sound with error at most `kappa_L / |K| = 7 / 2^256`.

*Proof.* `theta_F` is `GF(2)`-linear, so completeness is as in Theorem 1. Soundness: the
residual is `R = sum_m e_m c'_m`, `c'_m = sum_i beta_i d_i^(2^m)`. If all `c'_m` vanish, apply
the inverse Frobenius power to each: `sum_i sigma^(-m)(beta_i) d_i = 0` for `m < 128`. As `m`
runs over a full period of the Frobenius of `L`, the rows `(sigma^(-m)(beta_i))_i` form the Moore
matrix of the basis `(beta_i)`, which is invertible because the `beta_i` are independent over
`GF(2)` (mem: Lidl-Niederreiter, Corollary 2.38; ePrint 2024/504, Section 1.3, cites the same fact as Lidl-Niederreiter Lemma 3.51; **X** for the three toy pairs,
`test_moore_matrix_of_the_basis_is_invertible`), so `d = 0`. Hence a nonzero `d` gives a nonzero
multilinear in 7 variables. ∎

- **X** `SoundnessExhaustive.test_form_F_bound_kappa_L_over_K`,
  `SoundnessStructure.test_form_F_coefficients`; **control X**
  `test_control_F_with_one_power_fewer_is_unsound` (127 powers in place of 128 admit a nonzero
  `d` that passes every challenge).

**The operand in form F** is a sum over Frobenius conjugates of the point, with no tensor
algebra: `t_rs(rho) = sum_{m < 128} e_m eq_{<n}(rho, sigma^m(r_rest))`, because
`eq(z, y)^(2^m) = eq(sigma^m(z), y)` for Boolean `y`. **X** `Operand.
test_form_F_is_a_sum_over_frobenius_conjugates_of_the_point`. (Form T has the same shape with
256 terms and coefficients `c_m = sum_j e_j sigma^m(gamma*_j)`, `gamma*` the trace-dual basis:
**X** `test_form_T_through_the_trace_dual_basis`.) Cost: `127 l` squarings and `128 l` products
for `l` cell variables; `s_rs` costs 127 squarings and 128 products a message element.

Form F is a different verifier (another family of functionals) from [DP24, Construction 3.1] as
the Blueprint presents it. It is the Galois-orbit check of Soukhanov's Hashcaster in the improved
form that Diamond and Posen give in ePrint 2024/504, Section 1.3, equations (16) to (20) and
Figure 4 (there over one extension `L / K`, with claims, challenges and sumcheck in `L`; called
"a perfectly correct and sound protocol" there, with no numbered theorem); its invertibility step
is the nonsingularity of the matrix `[sigma^u(beta_v)]`, which that paper cites as Lidl and
Niederreiter, Lemma 3.51 (our "Corollary 2.38" above was from memory and is not checked). What is
ours: the three-field form (orbit of `L`, claims and challenges in `K`) and the error `7 / |K|`.
Form T itself is Construction 3.1 of that paper for `GF(2) < K` applied to a polynomial whose
upper 128 packing coordinates are zero: its Theorem 3.5's proof has the same Schwartz-Zippel step
with error `kappa / |K|`, `kappa = 8` (finding C-13). Form F is proposed as the second step, after
form T, and needs the reviewer's sign-off of Theorem 2.

### 3.3 The public-input check

It runs the same ring switch on the packed public words (S: `reduction.rs:327-383`), so it
packs two words a cell and uses the same form; its sumcheck has `p = 9` rounds as at the pin.
Its operand evaluation `eval_rs_eq(...)` at `reduction.rs:374` is the source of the wrapper's
public transpositions (section 5.1).

## 4. Soundness of the rest

### 4.1 Restriction principle

**Lemma 3 (P).** Let `Pi_K` be the all-`K` protocol and `Pi_mix` the mixed protocol, with the
same verifier after the first oracle is fixed. Any prover of `Pi_mix` is a prover of `Pi_K`
whose first oracle is `L`-valued. Hence every round-by-round error bound of `Pi_K`, for the
rounds after the ring switch (the batching `mu`, the mask fold `gamma`, each fold round, the
query round), holds for `Pi_mix` with the same state function.

*Proof.* A word of `L^N` is a word of `K^N`; the verifier's fold, consistency and final checks
are the same functions of the opened symbols; the state function of a round-by-round analysis
is defined on the transcript and the committed words and does not ask where their symbols
live. A smaller set of prover messages cannot enlarge the set of bad challenges. ∎

So the mixed variant needs no proximity theorem that the all-`K` build does not already rest
on. Two facts make the reduction to the ring switch go through, and one published statement
covers the first fold directly.

**Lemma 4 (descent, P).** Let `D` be a subset of `L`, `u` in `L^D`, and `c` a codeword of
`RS[K, D, k]` agreeing with `u` on at least `k + 1` points. Then `c` is in `RS[L, D, k]`.

*Proof.* The polynomial of degree at most `k` through `k + 1` points of `L x L` has
coefficients in `L` (Lagrange interpolation), and it is the polynomial of `c`. ∎

Within the unique decoding radius agreement is at least `(1 + rho) n / 2 > k + 1`, so the
codeword the extractor decodes from the first oracle is over `L`, its message `pi` is in `L^n`,
and Theorem 1 applies to it. The same holds for the lifted and batched oracles (each is a word
over its own alphabet). **X** `test_code.Descent` (three tests: at the radius, at any agreement
of `k + 1` points, and the control below `k + 1` points).

**Theorem 5 (BCIKS20 Theorem 4.1 over `K`; D, read).** Let `V = RS[F_q, D, k]`, `D` any subset
of `F_q` of size `n`, `delta <= (1 - rho) / 2`, `u_0, u_1 : D -> F_q`. If
`|{z in F_q : Delta(u_0 + z u_1, V) <= delta}| > n` then there are `v_0, v_1` in `V` with
`|{x : (u_0(x), u_1(x)) != (v_0(x), v_1(x))}| <= delta n`. Applied with `F_q = K` and `D` in `L`
it gives the fold's proximity error `n / |K|` for words of any alphabet inside `K`. Remark 1.2
of the same paper states the case in so many words: "One may sample z from a finite extension
field ... the statement above holds with eps_U and eps_J modified by replacing q with q' in the
denominators ... the vectors v_0, v_1 ... belong to RS[F_q, D, k], not just in RS[F_q', D, k]".
**X** on `RS[GF(16), GF(4), 1]`, all 65,536 pairs of base-field words and all 16 challenges:
`test_code.LineOverTheExtension` (no pair without correlated agreement has more than `n = 4`
bad challenges; the correlated codewords are over `GF(4)`; control: with challenges from `GF(4)`
the same bad set is all of the challenge set).

### 4.2 Each step

| Step | In the mixed variant | Error a challenge, units `1 / |K|` | Status |
|---|---|---|---|
| Zerocheck coordinates (BitAnd `a - 3`, BinMul `b`, wrapper `c`, zero extension) | polynomial with `GF(2)` or `L` values on the cube, point in `K` | 1 | Schwartz-Zippel; the three fixed `GF(2^8)` coordinates: `parameters.md` 2a.3's lemma holds for every `F` containing `GF(2^8)` (D) |
| Univariate-skip round | | 127 | Schwartz-Zippel (D: 2a.4) |
| Sumcheck rounds (BitAnd, BinMul 3; shift, public 2; wrapper 3) | messages in `K` | degree | standard; base-field coefficients are a special case |
| Batch coefficients (BitAnd, shift's 4 coordinates, `lambda`) | | at most 10; 1; 2 | Schwartz-Zippel (D: 2a.4) |
| Ring switch, twice (trace, public input) | Theorem 1 or 2 | 1 a coordinate; 8 (T) or 7 (F) jointly | **P**, **X** |
| Opening `mu` (batching relations) | unchanged | relations - 1 | D: Blueprint 7.2 "Soundness" |
| Mask fold `gamma` (leaf) | line `Enc(M) + gamma (Enc(w) + Enc(M))`, `Enc(M)` over `L`, `Enc(w)` over `K` | `n + 1` | Theorem 5 and one root for the mask claim (the method's W-M argument. Published as a proof sketch for the same two events: Diamond, ePrint 2025/1015, Theorem 4.2, which invokes BCIKS20 Theorem 4.1 for the combination and "low probability over alpha" for the claim, with no explicit error; the count `n + 1` is ours. Still U against the Blueprint's own proof) |
| Fold round `j` | first fold takes the `L`-codeword to a `K`-codeword; the fold is affine in the challenge | `n_j + 2` | Theorem 5 per fold (read) and Lemma 3; the terms bound DP24's (ePrint 2024/504, Proposition 4.21: `theta |S^(i+theta)| / |L|` per committed oracle; sumcheck `2 / |L|` a round, proof of Theorem 4.17; read), whose analysis is of whole-protocol soundness; round by round: Haböck, ePrint 2024/1571, Theorems 1 and 6 (list decoding; unique decoding by the paper's remark), C-12 |
| Commitment-index rounds (`o`) | unchanged | `n + 2` | as the fold rounds |
| Query round | first-oracle symbols opened as 16 B, mask symbols 32 B | `((1 + rho) / 2)^q` absolute | the method's Lemma 4 / 5 form; DP24 (ePrint 2024/504) proof of Proposition 4.24 and Section 5.2 equation (42): `(1/2 + 1/(2 * 2^R))^gamma`, read |
| Node batching transcript (`alpha`, rounds, `mu`) | unchanged, in `K` | `K - 1`; 2; 2 | D: 2a.4 |
| Lifted oracles of unequal size | unchanged | | U: [HMH] not read; the same open item as for the pin and the all-`K` build |

No term differs from the all-`K` build's except the ring switch's count of coordinates in form
F. `k` for the wallet leaf: 176 with form T and task W-1 (wrapper 2^18, largest oracle 2^18), 171
with form F; 182 as built (calculator: `binius64.k_of(leaf_shape(v))`).

### 4.3 The row

Target (D: `parameters.md` 2a.2; calculator `current.b_need`): 20,000 proofs, 600 challenges a
proof on average: `e >= 129 + log2(20,000 x 601) = 152.52` bits a round. Counted: 16,384 leaves
of `k = 182` and 3,616 nodes of `k <= 663` sum to `2^22.36` (151.36 bits), inside the budget.

| Rate | Queries | Query round |
|---|---|---|
| 1/2 | 368 | 152.73 |
| 1/4 | 225 | 152.57 |
| **1/8** | **184** | 152.73 |
| 1/16 | 168 | 153.31 |

Weakest algebraic round with `K` challenges: the leaf's commitment-index round, 234.0 bits; the
first fold of a node of 2^30 rows, 225.0 bits. Field needed: 184 bits. No grinding. The row is
the all-`K` build's row; the mixed variant changes no count.

## 5. Cost

### 5.1 What the wrapper's size is made of

The wrapper circuit (R1CS; S: `spartan-frontend`) is the inner verifier's arithmetic. Its large
part is `square_transpose` (S: `spartan-verifier/src/wrapper/gadgets.rs:29-102`): for a
`rows x cols` bit matrix it hints every bit, constrains each by `c^2 = c`, reconstructs each
input and builds each output by products with basis constants. A product or assertion whose
wires are all public allocates derived wires and, for an assertion, still emits a constraint
(S: `circuit_builder.rs:339-386`, and the instance generator's comment "Assertions are enforced
as ordinary public-segment constraints", `circuit_builder.rs:711-714`).

Model (E, fitted): a transposition on private values costs `3 rows cols` constraints and
`3 rows cols` private wires (there are two, the two ring-switch messages); on public values
`rows cols` constraints and `2 rows cols + 2 cols` live derived wires. The public-input check's operand makes two public
transpositions a variable (S: `eq_prefix.rs:92-100`, one `scale_horizontal` on `eq` a variable
when the oracle length is a power of two), `2 p` in all.

| | Private wires | Derived wires | Constraints (padded) |
|---|---|---|---|
| Pin, model: 2 private, 18 public, 128 x 128 | 98,304 | 594,432 | 393,216 (2^19) |
| Pin, measured (M) | 98,354 | 594,439 | 2^19 |
| All-`K`, model: 2 private, 16 public, 256 x 256 | 393,216 | 2,105,344 | 1,441,792 (2^21) |
| All-`K`, measured (M) | 393,008 | 2,105,223 | 2^21 |

The fit is to within 0.06 % on four measured counts (calculator test
`test_wrapper_model_reproduces_both_measured_wrappers`). The split of the constraint count
between its parts is inferred, not read from a run (U): the built code prints only the padded
count.

Consequences (E, calculator `binius64.wrapper_counts`):

| Variant | Private wires (round oracle 1) | Constraints |
|---|---|---|
| Mixed, form T, wrapper as is | 196,608 (2^18) | 1,376,256 (**2^21**: 18 public transpositions of 256 x 256) |
| All-`K` with W-1 | 393,216 (2^19) | 393,216 (2^19) |
| **Mixed, form T, with W-1** | 196,608 (2^18) | 196,608 (**2^18**) |
| Mixed, form F | about 65,600 (2^17) | about 65,600 (2^17) |

**W-1 (direct public transposition).** A transposition whose inputs are all public is a
function of values the verifier computes itself; its hinted bits and assertions constrain
nothing a prover chooses. The builder hook exists (`CircuitBuilder::square_transpose_direct`,
VENDOR.md change 11, used by the recursion crate's instance generator); W-1 implements it for
the three frontend builders when every input wire is public: the constraint builder allocates
`degree` derived wires and no constraint, the instance generator and the witness generator
compute the field's transposition. Sound because derived wires are recomputed by the verifier
(S: `constraint_system.rs:19-22`). It applies to the pin and to the all-`K` build as well.

### 5.2 Sizes and rows (calculator, `yugen-soundness --current`, revision 4)

Rate 1/8; wallet leaf, zero knowledge, pin layout. Opening model fitted to the measured
all-`K` proofs (leaf errors -1.4 % to +1.8 % at four rates).

| Variant | Queries | Wrapper constraints | Symbols: trace / wrapper / mask (B) | Leaf (KiB) | Node, 2^27 words (KiB) | Leaf slot AND rows; BMUL rows (E) |
|---|---|---|---|---|---|---|
| Pin, 96-bit level (M: 283,216 B) | 116 | 2^19 | 16 / 16 / 16 | 280 | 368 | 4.23 M; 0.79 M (M) |
| All-`K` as built (M: 633,280 B) | 184 | 2^21 | 32 / 32 / 32 | 614 | 697 | 8.08 M; 3.16 M |
| All-`K` with W-1 | 184 | 2^19 | 32 / 32 / 32 | 614 | 697 | 8.08 M; 3.16 M |
| Mixed, form T, with W-1 | 184 | 2^18 | 16 / 32 / 32 | **568** | 699 | 7.82 M; 3.16 M |
| Mixed, form F | 184 | 2^17 | 16 / 32 / 32 | **529** | 699 | 7.49 M; 3.16 M |

Slot rows: the pin's measured slot scaled by queries and by SHA-256 compressions a query
(`binius64.hash_blocks`: 103 at the pin, 124 all-`K`, 120 mixed T, 115 mixed F); the
implementers' own estimate for the all-`K` slot is 8.7 M.

### 5.3 Prover and verifier, relative (E)

Rule used: between the two measured builds the wrapper's share of the leaf's prove time, of
its verify time and of its peak memory moves with the padded constraint count (prove, 4
threads: 0.196 s at 2^19 and 0.758 s at 2^21 after subtracting the transparent proof's time;
verify: 136 to 158 ms and 649 to 733 ms; peak 1,274 and 3,829 MB), a factor 3.9 to 4.7 for a
factor 4. Each figure below is that rule applied to the constraint counts of 5.1, to be replaced
by a measurement (tasks T-5, W-1).

| Wallet leaf, rate 1/8 | Pin (M) | All-`K` as built (M) | All-`K` + W-1 (E) | Mixed T + W-1 (E) | Mixed F (E) |
|---|---|---|---|---|---|
| Prove, 4 threads | 0.215 s | 0.799 s | about 0.24 s | about 0.14 s | about 0.09 s |
| Verify, 1 thread | 136 to 158 ms | 649 to 733 ms | about 170 ms | about 90 ms | about 50 ms |
| Peak footprint | 1.27 GB | 3.83 GB | about 1.3 GB | about 0.9 GB | about 0.7 GB |
| Proof | 283 kB | 633 kB | 633 kB | about 582 kB | about 542 kB |

Node prover (transparent proof): all-`K` costs 1.45 times the pin on one circuit (M). Mixed (E,
no measurement): the commitment is the pin's (same symbols, same transform), the sumchecks and
folds are the all-`K` build's on twice as many, half as wide, first-round elements; between
1.3 and 1.6 times the pin. Node proof size is the all-`K` build's (699 against 697 KiB).

Recursion (E): the leaf slot's AND rows fall 3 % (form T) to 7 % (form F) against the all-`K`
build; the 19,300 core-seconds of `parameters.md` 2a.6 move by about that much on their 64 %
leaf share. **The mixed field does not bring recursion inside the allowance.** What does not
change: 184 queries (1.59 times the pin's), 32-byte fold symbols, four BMUL rows a field
product. Final-proof verification: each leaf claim's wrapper evaluation shrinks with the
constraint count (2^21 to 2^18), which is the 85 ms item of 2a.6.

## 6. Zero knowledge under the mixed variant

### 6.1 The failure

The opening folds each committed oracle with its mask: `M^gamma = (1 - gamma) M + gamma w`,
and every later message is a function of `M^gamma` (D: `zero-knowledge.md` M4, M5; Blueprint
Protocol 7.1). With `M` in `L^n`, `w` uniform in `L^n` and `gamma = g_0 + g_1 Y` in `K`:

`M^gamma = (M + g_0 (M + w)) + Y g_1 (M + w)`.

If `g_1 != 0` the `Y`-coordinate gives `M + w` and the other coordinate then gives `M`. A
`K`-valued folded oracle has `2 n` coordinates over `L`; a base-field mask supplies `n`.
The oracle is revealed whenever `gamma` is outside `L`, probability `1 - 2^-128`.

- **Control X** `test_zk_mask.FoldMask.test_control_base_field_mask_reveals_the_whole_oracle`
  (every `M`, every mask, every `gamma` outside `L`: `M` is recovered),
  `test_control_base_field_mask_views_are_disjoint_across_messages` (statistical distance 1),
  `test_base_field_mask_hides_only_when_gamma_falls_in_L`.

The same count applies to every mask whose job is to make a `K`-valued message uniform:

| Mask | Message it hides | Base-field sampling | Evidence |
|---|---|---|---|
| Fold mask `w_r` | `M_r^gamma` in `K^n` | reveals `M_r` | above |
| One-time-pad key | an inner prover message in `K` | reveals the `Y`-coordinate of every padded message | **control X** `OneTimePad.test_control_base_field_key_leaks_a_coordinate` |
| Dummy-constraint operands, `s_pre` blinding (round oracle 0 side) | a `K`-combination `alpha_1 a_1 + alpha_2 a_2` | uniform only if `alpha_2 / alpha_1` is outside `L`; fails with probability about `2^-128`, not `2^-256`, and the product term of finding N3 changes | **X** `Blinding.test_base_field_blinds_are_uniform_iff_the_weights_are_L_independent` |
| Wrapper's mask table `g'`, dummy wires of `z_wit` | messages of the masked check over `K` | not at issue: round oracle 1 has alphabet `K` | |
| Query pad of round oracle 0 | the `q` opened symbols of `Enc(M_0)`, which are `L`-valued | **sufficient**: the opened symbols are `L`-linear functions over `L` | **X** `Pad` (with the placement control) |

### 6.2 The fix

**Rule Z.** Every random value that hides a `K`-valued message is uniform in `K`.

1. Fold masks are sampled in `K^n` for every round oracle. A Merkle leaf of round oracle 0 is
   `(Enc(M_0)[e] in L, Enc(w_0)[e] in K, salt)`.
2. A `K`-valued value stored in round oracle 0 (each one-time-pad key, each dummy wire and
   blinding value of the precommit segment) occupies two `L` slots `(p, p')` and means
   `p + Y p'`. The wrapper and the inner protocol treat the precommit segment as a vector
   `z_pre` in `K^m`; the opening translates a linear query `<z_pre, T>` into the query with
   operand `(T, Y T)` on the `2 m` slots. No constraint is added: `(p, p') -> p + Y p'` is a
   bijection `L^2 -> K`, so the slots are uniform iff the value is.
3. The query pad of round oracle 0 stays `q` coordinates of `L`; round oracle 1 is unchanged
   from the all-`K` build.

**Proposition 6 (P).** With rule Z, the simulator of the Blueprint's 7.2 and 7.3 (D), as
reviewed in `zero-knowledge.md` section 2, applies to the mixed variant with these readings:
(a) `M_r^gamma` is uniform in `K^n` for `gamma != 0` and independent of `M_r`; (b) the `q`
opened symbols of `Enc(M_0)` are uniform in `L^q` given the rest of `M_0`, by the interpolation
argument of `zero-knowledge.md` 2.1 over `L` (the encoder is `L`-linear and the pad sits on
coefficients `0..q`); (c) each opened mask symbol is
`gamma^-1 (Enc(M^gamma)[e] - (1 - gamma) Enc(M)[e])`; (d) the precommit segment is the
all-`K` protocol's `z_pre`, encoded.

*Proof.* (a): `w -> (1 - gamma) M + gamma w` is a bijection of `K^n` for `gamma != 0`. (b):
unchanged argument, over the field `L`, on a word whose symbols are in `L`. (c): symbol-wise
identity. (d): bijection of the encoding. The remaining steps of the simulator do not refer to
the alphabet. ∎

- **X** `FoldMask.test_fix_extension_field_mask_is_perfect_for_every_nonzero_gamma`,
  `test_fix_as_two_base_field_masks`, `test_opened_mask_symbol_is_determined`,
  `OneTimePad.test_fix_key_from_two_base_field_slots`,
  `Blinding.test_fix_extension_blind_needs_one_nonzero_weight`.

Lemma 7.2 (N1) is settled by the citation audit: the statement for a pad on coefficients `0..q`
is Published, ePrint 2026/391 (revision of 2026-11-16), Lemma 3.29, and is the last step of the
proof of Lemma 4.4 of ePrint 2025/1015 (the novel-basis Vandermonde of `X_0..X_{kappa-1}` is
nonsingular); Lemma 4.4 itself treats a **different** layout (pad on coefficients `2^l ..`, domain
disjoint from the message subspace). Over `L` the argument is unchanged.
What Proposition 6 inherits unproven: the `(a, b, c)` distribution
(N3), Fiat-Shamir (N7), exactly as `zero-knowledge.md` section 2.2 lists them for the pin. The
excluded challenges stay `gamma = 0` and the blend challenge 0, each `2^-256`.
Diamond's combination is `alpha f + f'` (mask unscaled), for which Theorem 4.3 of ePrint 2025/1015
gives identical distributions with no excluded challenge; the Blueprint's `(1 - gamma) M + gamma w`
excludes `gamma = 0`. Finding C-5 of `CITATION-AUDIT.md`.

Cost of rule Z against a naive mixed port: 16 more bytes in each opened leaf of round oracle 0
(counted in section 5.2) and twice the key slots (about 1,010 `L` slots for about 505 padded
messages; the precommit segment stays 2^10 to 2^11).

## 7. Alternatives

**(a) Parallel repetition of the 128-bit protocol.** Two independent challenge sets on one
commitment, both must pass. As an interactive proof the error squares: for knowledge error this
is proved for `(k_1, .., k_mu)`-special-sound multi-round protocols by Attema and Fehr, *Parallel
Repetition of (k1, ..., kmu)-Special-Sound Multi-Round Interactive Proofs*, ePrint 2021/1259
(Version 3, September 6, 2023), Theorem 4 (knowledge error `kappa^t` for `t` copies; read
2026-11-19); that the sumcheck and fold rounds here are special-sound in that sense is not shown in
that paper (from memory for the soundness-error form). Under Fiat-Shamir it does not: the bound the method uses is
`(t + k) eps_rbr`, and the round-by-round error of the repeated protocol is still `eps`, because
the two copies can be made consistent in *different* rounds: grind round `i` until copy 1's
challenge is bad (`1 / eps` hash calls), continue copy 1 honestly, then grind a later round for
copy 2. Cost about `2 / eps`, not `1 / eps^2`. **Published**: Block, Garreta, Katz, Thaler, Tiwari,
Zając, ePrint 2023/1071, Appendix C (read 2026-11-19), describes exactly this attack on a `t = 2`
parallel repetition under Fiat-Shamir (grind round 1 until copy 1's challenge lets it cheat, then
round 2 until copy 2's does; the first copy's check holds for every later challenge) and attributes
it to Attema, Fehr, Klooß, *Fiat-Shamir Transformation of Multi-Round Interactive Proofs*, TCC 2022, Part I, LNCS 13747, pp. 113–142 (as cited by ePrint 2023/1071; not supplied, not read) ("This type of attack is introduced and described in [AFK22]"). ePrint 2021/1259,
supplied as the candidate, is Attema and Fehr's interactive repetition paper and does not contain
it (finding C-20). **X** `test_parallel_repetition.StaggeredAttack`:
on a three-round sumcheck, two copies over `GF(16)` are forged with 32 hash calls on average
(200 trials; 256 would be the squared figure) and one copy over `GF(256)` with 289; every forged
transcript passes the verifier. Repetition that does square the error has to force both
challenges into one polynomial identity of the same round, which is drawing the challenge from
the quadratic extension: the variant of this document. **Status: not sound at the target; cost
irrelevant.**

**(b) A 192-bit challenge field.** Numerically sufficient: every algebraic round needs at most
184 bits (calculator: leaf 170.0 and node 161.0 bits at 192; test
`test_field_128_fails_192_and_256_meet`). Algebraically: `GF(2^192)` does not contain
`GF(2^128)`; it contains `GF(2^64)`. A build on it packs one word a cell in `GF(2^64)` (a field
the pin does not have: S, `field/src/fields/` holds GHASH, its square and Rijndael only), draws
challenges from the cubic extension, and must redefine the BMUL constraint, which is a GHASH
product (S: VENDOR.md change 16 note on `constraint.rs`), over a field inside `GF(2^192)`; the
recursion circuits' field arithmetic is BMUL rows. Theorems 1, 2, Lemma 4 and Proposition 6 are
stated for any `L < K` and would cover it. Gains (E): ring-switch message 64 x 192 = 12,288
bits, fold symbols 24 B, a challenge-field product of six 64-bit carry-less products. Drawing
challenges from a 192-bit subset of `GF(2^256)` is sound (the bad set of each round is counted
in elements) and saves nothing. **Status: sound in principle, a new field, a new constraint and
new gadgets; not proposed for this release.**

**(c) 128-bit challenges where the error is not binding.** There is no such step: the bound is
`(t + k) max_r eps_r`, and any round whose challenge has 128 bits has `eps_r >= 2^-128`, 24.5
bits short. Only steps without verifier randomness stay in the small field (the three fixed
zerocheck coordinates, by `parameters.md` 2a.3). **Status: none available.**

**(d) The Johnson regime with BCIKS20's proven bound (new; a candidate).** BCIKS20 Theorem 1.2
(read) gives, for proximity up to `1 - sqrt(rho) - eta`, the error
`(k + 1)^2 / ((2 min(eta, sqrt(rho) / 20))^7 q)`. The method set this regime aside because the
factor costs about 85 bits. In a 256-bit field it is affordable: at rate 1/8, `eta = sqrt(rho) /
20`, a message of 2^27 elements, the fold round keeps **168.2 bits** (2^31: 160.2; rate 1/16:
164.7 and 156.7), above 152.52. A query then gives `-log2(1.05 sqrt(rho))` = 1.43 bits in place
of 0.83: **107 queries at rate 1/8, 80 at rate 1/16**, against 184 and 168 (calculator
`binius64.johnson_bciks`, test `test_johnson_candidate_numbers`; it needs the 256-bit field: at
192 bits it fails). On the leaf slot that is 0.58 of the hashing rows, the lever section 5.3
says the recursion lacks. **Status: the proximity gap is a proven, read statement; the
protocol-level soundness of binary BaseFold (sumcheck interleaved with folding, the list size
in every algebraic term, at most 19 by the Johnson bound as `binius-johnson-row.md` revision 2
derives it (F1'; DKT26 (38) second term), the batched zero-knowledge opening, lifted oracles) in
the list regime is not confirmed here.** Haböck, ePrint 2024/1571 ("Basefold in the List Decoding
Regime"; read 2026-11-19) proves round-by-round soundness of Reed-Solomon BaseFold up to the
Johnson bound (Theorem 1, Section 5), carries it to the additive FFT of binary fields (Section 6.2)
and to row-batched FRI-Binius (Protocol 3, Lemma 5, Theorem 6), with proximity
`theta = 1 - (1 + 1/(2m)) sqrt(rho)`, `m >= 3`. Its errors at this row (`m = 10`, rate 1/8,
`|F| = 2^256`): query `(1 - theta)^s`, 1.43 bits a query, **107 queries** for 152.52 bits (the same
count); fold `1/|F| + eps(C_i, 1, B_i, theta)` of its Theorem 3, 169.3 bits at the first fold of
2^30 points and more at later ones (the BCIKS20 form above gives 168.2); batching (Lemma 1) the same
error with a factor `M`; row batching (Lemma 5) `l_m (d' - 1) / |F|`. What it does **not** cover,
as built (finding C-11): (1) Binius64 reduces to BaseFold by the ring switch of ePrint 2024/504
with eq-weighted (tensor) batching, not by Protocol 3's batching by powers of one challenge;
(2) the zero-knowledge mask round (`gamma` on `M + gamma w`) and the wrapper; (3) the lifted
oracles of unequal size (the commitment-index rounds; [HMH] not available). Each needs its own
list-decoding round error (the list size, at most 19 here by the Johnson bound as
`binius-johnson-row.md` revision 2 derives it, F1', where the Guruswami-Sudan figure
`(m + 1/2)/sqrt(rho)` = 29.70 is valid but looser, multiplies the Schwartz-Zippel and claim terms, which keep more than 90 bits of slack at 256 bits; the mask
round's line term is of a fold round's size, about 169 bits, 17 above the target). Section
6 of that paper is written as an adaptation ("holds verbatim", "we omit certain details") rather
than with full proofs. The lead architect's basis says "unique decoding"; adopting (d) is a change
of that decision, to be taken only after (1) to (3) are written and the reviewer confirms the whole
(review item R-9).

DKT26 (Dao, Kominers, Thaler, ePrint 2026/2056, copy of November 2, 2026; read 2026-11-19,
findings C-14 to C-16) proves line mutual correlated agreement up to the Johnson radius for every
Reed-Solomon code on any evaluation set **in every characteristic** (Theorem 4.4, count
`< 8 n t^3 / (3 rho_minus)`, `t = m + 1/2`), hence for binary additive domains, and extends it to
interleaved codes (Corollary 6.6) and to multilinear (`eq`-weighted, tensor) folds of interleaved
words (Corollary 6.7, error `h` times the line error). At a first fold of `2^30` points over a
message of `2^27` (`m = 10`, `|F| = 2^256`) the line term is **211.4 bits** (169.3 from Haböck's
Theorem 3, 168.2 from BCIKS20); the list size is at most 19 there (its equation (38)). The three
items above are written and proved in `binius-johnson-row.md` (L-J1 to L-J3, on a DKT26 route and
on Haböck's route; `CITATION-AUDIT.md` section 1c), which supersedes the error estimates of this
paragraph; the query count stays 107 on either route.

## 8. The calculator (revision 4)

`soundness/src/yugen_soundness/binius64.py`, `current.py`, `wi.py`; tests
`tests/test_revision4.py` (22 tests; 117 pass in all). `uv run yugen-soundness --current`.

The five corrections of `parameters.md` 2a.4:

1. `k` is counted: `binius64.Shape`, `k_of` (the formula of 2a.4; tests reproduce 132, 175, 132,
   182, 198, 246), `k_batching` for a node's batching transcript, `tree_need` for a tree given
   as groups of (count, `k`); the row is solved at the budget of 600 a proof.
2. `rounds_counted` lists every round of 2a.4's table (`opening.mu`, the commitment-index
   rounds, the wrapper's `2 c + 2`, `batching_rounds`).
3. The skip round is 127, unconditional.
4. The tree is 20,000 proofs (`current.TREE_BOUND`).
5. The leaf layout of the all-`K` build is the measured one (round oracles 2^16 and 2^19 of 32
   bytes, masks 32 bytes); the size model is fitted to the four measured 256-bit leaves and the
   measured node proof (`cal256`).

Added: `Variant` (pin, all-`K`, all-`K` with W-1, mixed T, mixed T with W-1, mixed F) with the
wrapper model of section 5.1, mask symbol sizes, slot rows by hash compressions, and the
candidate (d). The revision-3 functions are kept (the implementers' `soundness/cat1_row.py`
runs unchanged and prints CERTIFIED; run 2026-11-19).

System A (the lead's addition): `wi.A_WALLET_ZK` is now the built counts of
`yugen-proof-a-zk/docs/zero-knowledge.md` 17.5 (10 bus layers, 12 Keccak layers, 2 masked
chains, column `A` 2^11, 54 gadget claims): **85 listed rounds** (the implementers' 88 kept the
tool's larger bus and S9 figures), need 152.51 bits at 20,000 proofs; the solved row is
**226 / 157 / 154 / 154**, each count less by one fails, and the fourth pass's 225 / 156 / 154 /
153 fails (tests `test_a_leaf_row_at_20000_proofs_is_226_157_154_154`). The earlier estimates
remain as `A_WALLET_ZK_E` for the superseded shipping rows. New finding: **row 9 (nodes) at
rate 1/2 misses the 20,000-proof target by 0.03 bits** (level 0: 152.32 of 152.35) and needs
368 queries at level 0; at rate 1/4 it meets.

## 9. Tasks for the implementers

Order: W-1, T-1 to T-6, Z-1 to Z-3, then F-1. Each task is done when its reference test passes
and the named measurement is recorded in `parameters.md`.

| # | Layer and files | Change | Reference test |
|---|---|---|---|
| W-1 | `spartan-frontend/src/circuit_builder.rs` (three builders), `spartan-verifier/src/wrapper/gadgets.rs` | `square_transpose_direct` for the constraint builder, the instance generator and the witness generator when every input wire is public: `degree` derived wires, no hint, no constraint; values by the field's transposition. Pin layout only (with committed derivation the gadget stays) | wire ids agree across the three builders on a circuit with one public and one private transposition; `leafbench` prints at most 2^19 constraints in the `cat1` build and 2^17 in the default build; the vendored `prove_verify.rs` and `zk_statistics` pass; a proof made before the change is refused (the constraint system's digest differs) |
| T-1 | `field/`: `ChallengeField = GhashSq256b`, new `CellField = Ghash128b` in the `cat1` build; `prover/src/prove.rs` `pack_witness` | The trace is packed two words to an element of `Ghash128b` in both builds | `tests/field256.rs` extended: the embedding `Ghash128b -> GhashSq256b` is the identity on the low 128 bits (already tested); packing round trip |
| T-2 | `math/src/ntt`, `iop-prover/src/fri/encode.rs`, `iop/src/fri/` (`common.rs`, `verify.rs`, `fold.rs`), `iop/src/basefold/channel.rs` | Round oracle 0 is encoded over `Ghash128b` on the same subspace; its Merkle leaves hold 16-byte symbols; the first fold takes `L` symbols and a `K` challenge; later oracles as now | the subspace of the `K` build's encoder equals the embedded `L` subspace (assert at setup); a codeword encoded over `L` and embedded equals the `K` encoding of the embedded message; fold consistency on random words; a proof whose first-oracle leaf carries a symbol outside `L` cannot be serialized (16 bytes) |
| T-3 | `verifier/src/ring_switch.rs`, `prover` counterpart, `verifier/src/reduction.rs` (`verify_public_eval`), `verifier/src/verify.rs` | Form T: message of `1 << 7` elements, point split at 7, `r''` of 8 coordinates; `eval_rs_eq` unchanged with `n_pack` counted in two-word cells | port of `ext-challenge/test_ring_switch.py` to the vendored field on random instances (completeness); a message changed in one bit of a `Y beta_i` column is rejected; the census gives `k = 176` for the wallet leaf with W-1 |
| T-4 | `spartan-verifier/src/wrapper/gadgets.rs`, `circuit_elem.rs`, `math/src/tensor_algebra.rs` | Rectangular private transposition, 128 x 256: 128 inputs of `K`, 256 outputs in `L`; hinted bits `128 x 256` | outputs equal the padded square transposition on random inputs; the wrapper's private wires are at most 2^18 and its constraints at most 2^18 with W-1 |
| T-5 | `src/params.rs`, `docs/parameters.md` | Row field "cell field"; the row digest covers it; the wallet leaf measured at the mixed row (size, 1 / 4 / 10 threads, verify, footprint, wasm32) | a proof of the all-`K` row is refused under the mixed row and the reverse; the measured table replaces the estimates of section 5.3 here |
| T-6 | `recursion/` (task A-6 as listed in `parameters.md` 2a.7) | Element on four wires as planned; a first-oracle symbol is two words; the message of a ring switch is 128 elements; transposition network for 128 x 256 | `recursion_end_to_end.rs`, `zk_recursion.rs` pass in the mixed build; `recbench slotmeta` prints the leaf slot's rows |
| Z-1 | `iop-prover/src/fri/encode.rs`, `iop-prover/src/basefold/channel.rs`, `iop/src/basefold/channel.rs`, `iop/src/fri/batch.rs` | The fold mask of every round oracle is sampled in `K`; a leaf of round oracle 0 is `(L symbol, K symbol, salt)` | port of `test_zk_mask.FoldMask`: with the mask type forced to `L` a test recovers the trace words from `M^gamma` (the negative control must fail the build's hiding test); with `K` the statistical test `zk_statistics` passes |
| Z-2 | `spartan-prover/src/wrapper/zk_wrapped_prover_channel.rs`, `spartan-verifier/src/wrapper/zk_wrapped_channel.rs`, `builder_channel.rs`, `spartan-frontend/src/constraint_system.rs` (precommit layout, `BlindingInfo`) | The precommit segment is a vector over `K` stored as two `L` slots a value; linear queries on it take the operand `(T, Y T)`; keys, dummy wires and dummy-constraint operands are uniform in `K` | every ciphertext differs in both coordinates between two prover seeds; a build with one slot a key fails a test that reads the `Y`-coordinate of a padded message; `zk_pad_rank` passes for round oracle 0 over `L` at `q = 184` |
| Z-3 | `docs/zero-knowledge.md` of `yugen-proof-b2` | Section 1 tables restated for the mixed variant (alphabet of each mask), findings F-1 to F-5 re-checked | the review's checklist C1 to C17 filled for the mixed build |
| F-1 | `verifier/src/ring_switch.rs`, prover counterpart, `recursion/src/zk.rs` | Form F after the reviewer accepts Theorem 2: `r''` of 7 coordinates, `theta_F` by squarings, operand as the sum over conjugates; no tensor algebra on the proving path | port of the form-F tests of `test_ring_switch.py`; wrapper at most 2^17 constraints; the control with 127 powers accepts a wrong message |
| C-1 | `yugen-proofs/soundness` (done here) | Revision 4 of the calculator | `uv run pytest` (117 pass) |

Not in this list because they do not depend on the field: D-6, C-4, B-9 of `parameters.md`,
which carry the recursion estimate; and the decision on alternative (d).

## 10. Review sheet for the external cryptographer

| # | Statement | Where | Status |
|---|---|---|---|
| R-1 | Theorem 1: ring switch over `GF(2) < L < K`, form T, error `kappa_K / |K|` | 3.1 | Adapted from ePrint 2024/504 Construction 3.1 / Theorem 3.5 (zero-padded packing over `GF(2) < K`; C-13); exhaustive on `GF(4) < GF(16)`; to review the reduction |
| R-2 | Theorem 2: form F, error `kappa_L / |K|`; uses invertibility of the Moore matrix of a basis | 3.2 | Adapted from the Galois-orbit protocol of ePrint 2024/504 Section 1.3 (Figure 4), which cites the matrix fact as Lidl-Niederreiter Lemma 3.51 (not read here); checked on three toy pairs; exhaustive on `GF(4) < GF(16)`; to review before task F-1 |
| R-3 | Lemma 3: restriction principle (an `L`-valued first oracle is a special case of the all-`K` protocol) | 4.1 | proved here; to review that no verifier check of the all-`K` protocol is dropped in the mixed build (tasks T-2, T-3) |
| R-4 | Lemma 4: descent of the decoded codeword to `L` | 4.1 | proved here; exact test |
| R-5 | BCIKS20 Theorem 4.1 with `F_q = K`, domain in `L`; Remark 1.2 | 4.1 | published; statement read 2026-11-19 in ECCC TR20-083 (Remark 1.5 there); re-read in the folder copy (ePrint 2020/654, July 3, 2021), Theorem 4.1 p. 13, Remark 1.2 p. 4, same statements (amended 2026-11-19, C-41) |
| R-6 | Per-round use of R-5 in binary BaseFold (`(n_j + 2) / |K|` a fold round, `((1 + rho) / 2)^q` for the queries, the commitment-index rounds) | 4.2 | query and fold terms confirmed against ePrint 2024/504 (Propositions 4.21, 4.24, equation (42)); round-by-round form from ePrint 2024/1571 Theorem 1 (unique decoding by its remark); commitment-index rounds in neither (C-12) |
| R-7 | Mask fold round `(n + 1) / |K|` | 4.2 | the method's W-M argument (`zk-wi-soundness.md` 9); the two events are those of the proof sketch of Theorem 4.2, ePrint 2025/1015 (read); unconfirmed against the Blueprint's proof |
| R-8 | Lifted BaseFold for oracles of unequal size | 4.2 | [HMH] not read; unchanged open item |
| R-9 | Alternative (d): binary BaseFold in the Johnson regime; every algebraic term with its list-size factor | 7 (d) | PCS core proven: Haböck, ePrint 2024/1571, Theorem 6 (read; 107 queries reproduced); the ring switch, the mask round and the lifted oracles are outside it (C-11); DKT26 (ePrint 2026/2056, read) supplies line MCA in characteristic 2 (Theorem 4.4) and `eq`-fold MCA (Corollary 6.7) for items (1) and (2) (C-16) |
| R-10 | Proposition 6: zero knowledge of the mixed variant under rule Z | 6.2 | proved here relative to the Blueprint's simulator; inherits N3 and N7 of `zero-knowledge.md`; N1 is settled (ePrint 2026/391 Lemma 3.29) |
| R-11 | Base-field masks under extension challenges leak (the negative result) | 6.1 | proved by the displayed identity; exact test |
| R-12 | Two parallel copies do not square the error under Fiat-Shamir | 7 (a) | attack run on a toy; the attack is published: ePrint 2023/1071 Appendix C (read), attributed there to Attema-Fehr-Klooß, TCC 2022 (not supplied); ePrint 2021/1259 (read) is Attema-Fehr's interactive result, Theorem 4 (C-20). Consistent with ePrint 2016/116 Theorem 1.5 (`s_sr(b) <= binom(b, k+1) s`) and Remark 1.6, which obtains small state-restoration error by `r = Omega((k log b + lambda)/log(1/s))` copies, not by two |
| R-13 | W-1: a transposition of public values needs no constraint | 5.1 | argument from the wire kinds (source read); the wrapper's constraint split is inferred from wire counts, not run |
| R-14 | The fixed `GF(2^8)` zerocheck coordinates under `K` | 4.2 | `parameters.md` 2a.3's lemma (any `F` containing `GF(2^8)`) |
| R-15 | Tree target `129 + log2(sum (1 + k_i))` at 20,000 proofs | 4.3 | the method's union bound (`soundness-method.md` 8.5b), conditional on the recursion heuristic C2 |

## 11. For the lead architect

1. Adopt the mixed variant in form T with W-1 and rule Z (tasks W-1, T-1 to T-6, Z-1 to Z-3)?
   W-1 alone already takes the built all-`K` wrapper from 2^21 to 2^19 constraints with no
   protocol change.
2. Form F (task F-1) after review of Theorem 2?
3. Alternative (d): the PCS core is proven in the list-decoding regime (Haböck, ePrint 2024/1571,
   Theorem 6); decide whether to commission the three missing pieces (finding C-11) and the
   review. It is the only item found here that moves the recursion estimate (107 queries in
   place of 184).
4. `parameters.md` 2a.5 states A-8's acceptance as "the wrapper of the wallet leaf is at most
   2^20 constraints": with the message change alone it stays 2^21 (section 5.1); the acceptance
   is met by W-1.
5. System A: row 9 at rate 1/2 needs 368 queries at level 0 for 20,000 proofs (section 8).
