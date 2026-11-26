# Soundness of the hiding opening W-I

Part of Yugen. This document proves round-by-round soundness and knowledge soundness of
construction W-I (`zk-hiding-commitment.md` section 6.1) and of the blinding around it
(`zk-composition.md`), in the unique-decoding regime, for both leaf systems; records the search
for a cheating prover in `../zk-sound/`; states what the calculator in `../soundness/` now computes
(W-I, and a whole proof tree); assesses whether both systems should carry the same hiding opening;
and ends with a review sheet.

Status tags, as in the other documents:

| Tag | Meaning |
|---|---|
| **(P)** | proven in this document, pen and paper |
| **(C)** | checked by computation in `zk-sound/` (sizes with the claim) |
| **(S)** | read in a primary source during this work, named with the claim |
| **(M)** | from memory or a secondary description: not verified |
| **(U)** | unproven, open |

Result in one paragraph. In the unique-decoding regime W-I is round-by-round sound with the round
list of section 5: against the non-hiding opening it adds one round of error `1/|F|` per level (the
mask's `rho`), raises each fold round's algebraic term from `2/|F|` to `3/|F|`, adds one round of
error `(N + 1)/|F|` for the base-case challenge, and changes the query terms only through the true
rates `lrow_i / N_i` (P). Every step uses three ingredients: the correlated-agreement theorem of
BCIKS20 inside the unique-decoding radius (Theorems 4.1 and 1.6, read), Schwartz-Zippel, and
uniqueness of decoding. No statement about WHIR, about the affine combiner (CWYZ26) or about
ePrint 2026/391 is used. The coset domain gives the same code word for word, and the dimension of a
Reed-Solomon code need not be a power of two (P, C). Blinder cells, the dummy variable and the
masks outside the opening are committed data, so the sumchecks run on polynomials fixed before
their challenges (P, C). The search found no accepted false claim above the proven bounds: three
component games were solved exactly over all prover strategies and the bounds are met with
equality in several of them (C). One construction defect was found and fixed (F-1: the aux-row
layout does not work for system A's affine combiner as written). The Johnson regime is not
covered (U); the design basis does not use it.

Amendments of 2026-11-19 after `theorem-s-referee.md` (`0a49234`), each dated in place: M-1 (section 5.1:
the state names its admissible code `A_{i,j}`, lane `b` in `C[lrow_i + g_b]`, decoded lane by lane), m-1 (the tail
sumcheck in Lemma 5 and Theorem S's table), m-2 (Lemma 4 (c): `lf_i`), m-3 and M-2 (section 5.2: [SG26]
Definition 2.20 and Lemma 2.21; replaced by Lemma K-A, `lemma-k-a.md`, DRAFT). No bound changes; the calculator
already charged the tail rounds.

---

Provenance (citation audit of 2026-11-19; `../REFERENCES.md`). Published and used: BCIKS20
Theorems 4.1 and 1.7, Schwartz-Zippel. Original (the Ycash developers, 2026): Theorem S and
Lemmas 1 to 7 as a proof for W-I in the unique-decoding regime, finding F-1 and its fix, the
cheating-prover search of section 7, the tree accounting of section 8.3. Lemma 2A is Original as a
proof (unique decoding, no agreement loss, from BCIKS20 Theorem 1.6); the affine combiner it
analyses and the degree asymmetry of its conclusion are Published, CWYZ26 (ePrint 2026/2863)
Section 1.1 (C-19). The protocol proven is
an adaptation of published constructions (ePrint 2026/391 Sections 6, 7, 9, 11; W-M from ePrint
2025/1015 Construction 4.1), as `zk-hiding-commitment.md` states.

## 1. Scope, notation, sources

`F = GF(2^k)` challenge field, `q = |F|`. Level `i` of the opening has `2^kappa_i` lanes, a domain
`D_i = beta_i + S_i` of `N_i` points, lane length `lrow_i` (coefficients in the novel basis
`X_0, X_1, ..`, `deg X_c = c`). `C_i[d]` is the Reed-Solomon code of polynomials of degree below
`d` on `D_i`; `rho_i = lrow_i / N_i`; `e_i = floor((N_i - lrow_i) / 2)` is the unique-decoding
radius in rows, `delta_i = (1 - rho_i)/2`. A row is the tuple of lane values at one point; distances
between interleaved words count rows. "Within the radius" means at most `e_i` rows differ.

| Source | Read? | Used for |
|---|---|---|
| Ben-Sasson, Carmon, Ishai, Kopparty, Saraf, *Proximity Gaps for Reed-Solomon Codes*, ECCC TR20-083 | **read on 2026-11-19** (pages 1 to 22 of the PDF): the code definition (`D` any subset of `F_q`, `k <= n` any integer), Theorems 1.2, 1.4, 1.5, 1.6, Remark 1.2, Theorem 4.1. BCIKS20 numbers follow the folder copy, ePrint 2020/654 revision of July 3, 2021 (`2020-654.pdf` (see REFERENCES.md)); the ECCC TR20-083 copy of May 30, 2020 numbered the affine-space theorem 1.7, the curve theorem 1.6 and the extension-field remark 1.5 (amended 2026-11-19, `docs/CITATION-AUDIT.md` C-41); re-read in the folder copy 2026-11-19: Theorem 1.2 and (1.1) p. 2, Remark 1.2 p. 4, Theorem 1.6 p. 5, Theorem 4.1 p. 13 (printed pages) | Lemmas 2, 2A, 5 |
| Schwartz-Zippel; uniqueness of decoding below half the minimum distance | standard (M for the attribution; both are one-line facts proved where used) | Lemmas 3 to 7 |
| Chiesa, Yogev, *Building Cryptographic Proofs from Hash Functions*: Theorems 25.2.1, 26.1.1, 31.2.1, 31.3.1 | confirmed as statements in `soundness-method.md`; not re-read here | compilation, section 5.3 |
| Pinned leanVM `84780fb4`, `crates/verifier/src/whir.rs` (`verify_whir`, `fold_row`) | read (S) | the affine-combiner round, section 4.3 |
| `zk-commit/whir_i.py` | read (S) | the W-I verifier that is attacked in section 7 |
| WHIR (ePrint 2024/1586) | read 2026-11-19 in the second citation pass (Theorem 5.2, Sections 4.1 to 4.4); not used by the proofs here | Theorem 5.2 is the published round-by-round analysis of plain WHIR for smooth multiplicative domains in unique decoding (mutual correlated agreement: Corollary 4.11); W-I's domains are binary additive cosets, so Theorem S is proven here from BCIKS20 directly (`CITATION-AUDIT.md` C-10) |
| Chiesa, Weissenberg, Yogev, Zheng, *Affine Combiners for Reed–Solomon Proximity Gaps* (CWYZ26), ePrint 2026/2863, copy dated November 13, 2026 | read 2026-11-19 (citation audit, C-19), after this document was written: Sections 1, 4.1, Theorem 4.10, Section 5 (Theorems 5.1, 5.2), Section 6 (Propositions 6.1 to 6.3); **not used** in any proof here | the affine combiner itself (Section 1.1) and the comparison with Lemma 2A after its proof |
| Chiesa, Fenzi, Weissenberg, ePrint 2026/391, revision of 2026-11-16 | read 2026-11-19 (citation audit), after this document was written; **not used** in any proof here. Its Theorems 6.3, 7.1, 9.8 and 10.2 give round-by-round knowledge soundness of the related in-oracle protocol in the list-decoding regime; not compared line by line | |
| Diamond, ePrint 2025/1015 | read in full 2026-11-19; Theorem 4.2 (a proof sketch) is the published soundness argument for the full-mask opening that W-M adapts: proximity gap on `alpha f + f'` (BCIKS20 Theorem 4.1) and one bad `alpha` for the claim | section 9 |

Correction to `soundness-method.md`: correlated agreement over affine spaces is BCIKS20
**Theorem 1.6** (Theorem 1.5 is curves, as that document says; its table does not list 1.6; it does since 2026-11-19).

**BCIKS20 Theorem 4.1 (S), in this document's notation.** `D` a subset of `F_q` with `n` points,
`V` the code of polynomials of degree at most `k'` on `D`, rate `rho = (k' + 1)/n`,
`delta <= (1 - rho)/2`. For words `u0, u1`: if more than `n` values `z` in `F_q` put `u0 + z u1`
within relative distance `delta` of `V`, then every `z` does, and there are `v0, v1` in `V` with
`|{x : (u0(x), u1(x)) != (v0(x), v1(x))}| <= delta n`. **Theorem 1.6 (S).** The same for an affine
space `u0 + span(u1..ul)`: if more than a fraction `n/q` of its elements are within `delta`, there
are `v0..vl` in `V` agreeing with `u0..ul` on a common set of density at least `1 - delta`.
**Remark 1.2 (S):** the challenge may be drawn from an extension field, with that field's size in
the error.

---

## 2. The protocol as modified, and the order of messages

### 2.1 Opening (both families)

Public claim `<p, W> = T` on oracle 0. For level `i = 0..L-1`:

| Step | Prover | Verifier | New in W-I |
|---|---|---|---|
| 0 | oracle `i` is already committed: lanes hold carried slots, aux slots, zeros, `t_i` random slots; the last oracle also holds the column `Gcol` | | coset domain; aux slots; random slots; `Gcol`; salts |
| 1 | `G_i` | `rho_i`; `T <- rho_i T + G_i`, `W <- rho_i W` | yes |
| 2 | `kappa_i` fold rounds: a message, then the challenge | B: `gamma_j`; A: `(alpha_j, beta_j)` | messages carry the mask |
| 3 | | folds `W`; adds the mask's final-value weights on the aux slots of the folded lane | yes |
| 4 (`i < L-1`) | commits oracle `i+1` (the folded lane `p'`, all `lrow_i` coefficients, in its carried slots) | positions `y_1..y_Q` of oracle `i` and `lam` (after the rows are opened or in the same message); `v_q` = fold of row `y_q`; `T <- T + sum lam^q v_q`; `W' <- W' + sum lam^q (X_j(y_q))_j` | the folded lane is not a power of two long; nothing is sent in clear |
| 5 (`i = L-1`) | `mu`; then, after `c`, the padded message `P*` (`lrow_{L-1}` coefficients) | `c`; checks `<P*, W'> = mu + c T`; **then** positions `y_q`; checks `P*(y_q) = Gcol(y_q) + c fold(row y_q)` | replaces the final message in clear |

Family B (Plonky3 binary, FRI-Binius / BaseFold-style fold): a row of `2^kappa` lanes is one coset
of the single codeword (`zk-hiding-commitment.md` 1.1); the row folds by `eq(gamma, .)`, i.e. each
round replaces a lane pair `(u_0, u_1)` by `u_0 + gamma (u_0 + u_1)`. Round message: three values
of a polynomial of degree 2; mask: `1 + 2 kappa` coefficients, each written into every lane of its
aux slot.

Family A (leanVM): each round replaces a lane pair `(F, G)` (lanes `2m`, `2m+1`) by
`G + (alpha + beta X) F`; the coefficient count grows by one per round, so the folded lane has
`lrow_i + kappa_i` coefficients. Round message: four scalars `(u0, w, c0, c1)`, the claim becomes
`u0 + beta c0 + alpha (u0 + claim + alpha w + beta (c0 + c1))` (S). Mask: `1 + 4 kappa`
coefficients. **Layout for A, changed by this document (findings F-1, F-7):** each mask
coefficient is written into the last lane only (the lane that is `G` in every round), `kappa_i`
zero guard slots separate the carried slots from the aux slots, and the random slots start at a
multiple of `2^ceil(log2(t_i + kappa_i))`.

### 2.2 Around the opening (`zk-composition.md` 2.2)

Oracle 0 also holds the blinder column `Bl`, the mask column `A`, the gadget column `B` and the bus
payloads. Every revealed evaluation of committed data is `chat = c(r) + r_y (1 + r_y) b`; every
sumcheck outside the opening runs on `rho f + g` with `g` in column `A`; linear claims on `A` go
through the gadget; all resulting linear claims on oracle 0 are batched with `lambda` into the one
relation `<p, W> = T` that W-I opens.

### 2.3 Order: what must be fixed before which challenge

Each row is a dependency a cheating prover could exploit if the order were different. "Control" is
the test in `zk-sound/` that reverses the order and observes acceptance of a false claim.

| Object | Must be fixed before | Where it is fixed | Holds in the composed protocol? | Control (C) |
|---|---|---|---|---|
| blinder cells `Bl` | the sumcheck challenges of their component (`r_y`, `r`) | oracle 0, step 0 | yes | `test_blinder_sound.py`: late blinder accepted with probability 0.77 at `q = 8` (always when `r_y (1 + r_y) != 0`) |
| sumcheck masks, layer blinders (column `A`) | that sumcheck's `rho` | oracle 0 | yes | |
| `G` of a masked sumcheck | its `rho` | sent before `rho` | yes; **exception** `Gtilde` of a GKR layer is sent after `rho`: sound only because the gadget later proves it equals a fixed linear functional of column `A` (section 6.3) | `test_mask_batch.py`: `G` after `rho` accepted with probability 1 |
| gadget column `B`, `beta` | gadget challenge `c` | oracle 0; `beta` sent before `c` | yes | |
| gadget vector `u` | `z` | sent before `z` | yes | |
| level-`i` mask (aux slots of oracle `i`) | `rho_i` | oracle `i`, committed in step 4 of level `i-1` (or step 0) | yes | as for `G` |
| `G_i` | `rho_i` | step 1 | yes | |
| oracle `i+1` | positions of oracle `i`, `lam` | step 4 | yes | |
| `Gcol`, `mu` | `c` | last oracle; `mu` in step 5 | yes | `test_basecase_sound.py`: `Gcol` after `c` always accepted |
| `P*` | **the last level's positions** | step 5 | yes in `zk-hiding-commitment.md` 6.1 and in `whir_i.py`; it is not listed among the Fiat-Shamir conditions of `zk-composition.md` section 6 | `test_basecase_sound.py`: a position known before `P*` always accepted |
| all revealed evaluations, `A(z)`, `B(z)` | `lambda` (batching) | sent before | yes | |

Acceptance criterion for both implementations: a transcript test per row that fails if the object
is absorbed after the challenge named (extends checklist item 14 of `zk-composition.md`).

---

## 3. Code-level lemmas

**Lemma 1 (coset domain; any dimension) (P; C).** For `beta` in `F` and a subset `S`, the map
`P(x) -> P(x + beta)` is a bijection of the polynomials of degree below `d`, for every integer `d`.
Hence `{(P(y))_{y in beta + S}} = {(P'(s))_{s in S}}`: under the index map `y = beta + s` the code
on the coset **is** the code on `S`, for every `d <= |S|`, power of two or not; minimum distance
`N - d + 1`. The novel-basis functions `X_0..X_{d-1}` have degrees `0..d-1`, so they span the
polynomials of degree below `d` on any domain. Consequences: no proximity statement needs a coset
version, since BCIKS20 is stated for an arbitrary `D` and any `k <= n` (S); the unique-decoding
radius is computed from the true `lrow_i` (family A: `lrow_i + kappa_i`). C
(`results/proximity.txt`, part A): `GF(16)`, `N = 8`, `d = 3, 5, 6`: the three sets of words are
equal and the minimum distance is `N - d + 1`.

Under the folding map `q(x) = x (x + b_0)`, `F_2`-linear with kernel `{0, b_0}` inside `S`, the
image of `beta + S` is the coset `q(beta) + q(S)` with `q(beta)` outside `q(S)`, and the pair
`(P(x), P(x + b_0))` determines `(P_0(q(x)), P_1(q(x)))` by a matrix of determinant 1 at every `x`
(P). So the row/coset equivalence of `zk-hiding-commitment.md` 1.1 holds on cosets.

**Lemma 2 (one fold round keeps a far interleaved word far; eq-fold) (P from Theorem 4.1; C).**
Let `U = (u_b)` be `2m` lanes on `D` (`n` points), `C = C[d]`, `e = floor((n - d)/2)`. For `gamma`
in `F` let `V(gamma)` be the `m` lanes `u_{2c} + gamma (u_{2c} + u_{2c+1})`. If `V(gamma)` is within
`e` rows of `C^m` for more than `n` values of `gamma`, then `U` is within `e` rows of `C^{2m}`, and
for those `gamma` the decoding of `V(gamma)` is the fold of the decoding of `U`.

*Proof.* Let `Gam` be the set of good `gamma`, `|Gam| > n`, and `A_gamma` the rows where
`V(gamma)` equals its nearest codeword tuple `w(gamma)`, `|A_gamma| >= n - e`. Fix a pair `c`. For
every `gamma` in `Gam` the single word `u_{2c} + gamma (u_{2c} + u_{2c+1})` is within `e/n <= delta`
of `C`, so by Theorem 4.1 there are codewords `(a_c, b_c)` equal to `(u_{2c}, u_{2c} + u_{2c+1})`
outside at most `delta n` rows, hence at most `e` rows. `a_c + gamma b_c` and `w_c(gamma)` are both
within `e` rows of the same word, so they are equal (`2e < n - d + 1`). Let `Dis` be the rows where
some pair `c` has `(u_{2c}, u_{2c} + u_{2c+1}) != (a_c, b_c)`. For `y` in `Dis` the value
`(u_{2c} - a_c)(y) + gamma (u_{2c} + u_{2c+1} - b_c)(y)` is a nonzero affine function of `gamma`,
so `y` lies in `A_gamma` for at most one `gamma`. Counting pairs `(gamma, y)`:
`|Gam| (n - e) <= sum |A_gamma| <= (n - |Dis|) |Gam| + |Dis|`, so
`|Dis| <= e |Gam| / (|Gam| - 1) < e + 1` because `|Gam| - 1 >= n > e`. ∎

Round-by-round use: if the interleaved word is not within `e` rows of the code, at most `n` of the
`q` challenges make its fold so: error `n/q`. A level-0 oracle over the subfield `K` is a word over
`F` and the theorem is applied over `F` directly. C (`results/proximity.txt`, part B): every pair
of words up to codewords over `GF(8)`, `n = 4`, `d = 2` on a coset: pairs not jointly within the
radius have at most 4 = `n` good `gamma`; 4,000 sampled lane quadruples: at most 4.

**Lemma 2A (affine combiner) (P from Theorem 1.6; C).** Lane pairs `(F_c, G_c)`; for `(alpha,
beta)` in `F^2` let `V_c = G_c + (alpha + beta x) F_c` (`x` the domain point). If the `m` lanes
`V(alpha, beta)` are within `e` rows of `C[d+1]^m` for more than `n q` pairs, where
`e = floor((n - d - 1)/2)`, then there are `f_c` in `C[d]` and `g_c` in `C[d+1]` equal to
`(F_c, G_c)` outside a common set of at most `e` rows, and the decoding of `V` is
`g_c + (alpha + beta x) f_c`.

*Proof.* For one pair, `{G + alpha F + beta (xF)}` is an affine space of words; by Theorem 1.6 for
`C[d+1]` there are `g, f_1, f_2` in `C[d+1]` equal to `G, F, xF` on a common set `A` of at least
`n - e` rows. On `A`, `x f_1(x) = f_2(x)`; both sides are polynomials of degree at most `d + 1`
and `|A| >= n - e > d + 1`, so `x f_1 = f_2` and `deg f_1 < d`: `f_1` is in `C[d]`. Rows where
some pair disagrees with its `(g_c, f_c)` are fixed by a nonzero polynomial of degree 1 in
`(alpha, beta)`, hence lie in the agreement set of at most `q` of the pairs; the counting of Lemma 2
gives `|Dis| (|Gam| - q) <= e |Gam|`, so `|Dis| <= e` when `|Gam| > q (e + 1)`, which
`|Gam| > n q` implies. ∎

So the affine-combiner round has proximity error `n/q` in the unique-decoding regime **without
CWYZ26**, and it certifies lane `b` only to degree below `d + (number of rounds in which the lane's
path takes the G branch)`: the committed lanes may carry up to `kappa` more coefficients than the
message.

Comparison with CWYZ26 (ePrint 2026/2863, read 2026-11-19; finding C-19 of `CITATION-AUDIT.md`).
The combiner `G + (alpha + beta x) F` and the degree asymmetry of the conclusion (the unscaled word
to the output degree, the scaled one to one less) are CWYZ26's (Section 1.1: `f + (alpha + beta x)
g`, `deg f <= d`, `deg g <= d - 1`, "admissible witnesses"). CWYZ26 proves mutual correlated
agreement with **one coordinate of agreement loss** up to the Johnson radius, over every finite
field and evaluation set: Theorem 1.1, error `4/(eta q) + 2^14 n^2 / (rho^3 eta^10 q^2)` under
`n eta^2 >= 4/rho`, `q >= n`; Theorem 4.10, equation (4.13), the finite form. With **no**
agreement loss, which is the form Lemma 2A proves, its Proposition 6.2 shows that the worst-case
error is at least `(n - A + 1)(q - 1)/q^2`; at the unique-decoding threshold `A = n - e` that is
about `n (1 - rho) / (4 q)`, so Lemma 2A's `n/q` is of the best possible order for that form and is
not contradicted. CWYZ26 does not state the no-loss upper bound; Lemma 2A's proof from BCIKS20
Theorem 1.6 is ours. What CWYZ26 would give here: at A's leaf parameters the loss-one bound is about
`2^-252` against `n/q` (about `2^-228`), at the price of restating Theorem S with one coordinate of
agreement loss per affine round (query terms `(a + 1/n)^t`, CWYZ26 Section 1.1); not adopted, since
no fold round is binding. For the degree excess, CWYZ26's equal-degree variant (Section 5,
`g + (alpha + beta x)(f + theta g)` with one more challenge `theta`; Theorem 5.1, extra error
`l0 / q`; Theorem 5.2, `r` rounds with witnesses of degree at most `d`) is a published alternative
to W-I's excess rule; leanVM as pinned uses the original combiner, so the excess rule stays. These are extra message slots with weight zero in the relation, exactly like W-I's random
slots (section 4.1). C (`results/proximity.txt`, part C): 1,500 sampled `(F, G)` over `GF(8)`,
`n = 4`, `d = 1`: pairs not jointly within the radius have at most 32 = `n q` good `(alpha, beta)`.

---

## 4. Algebraic lemmas

### 4.1 What the relation is about

The verifier's weight table is zero on every slot that is not carried: the aux slots of the current
level (until step 3), the gap, the random slots. A cheating prover may write anything there. The
claim proven is `<P, W> = T` for the **decoded** table `P`, and the extracted witness is the
content of the witness slots of the decoded oracle 0; extra slots are free variables that do not
occur in the claim until the verifier itself gives them a weight (step 3 for aux slots, step 4 for
every slot of the folded lane). So the larger dimension costs rate and nothing else (P).

### 4.2 Masked batch, eq-fold

**Lemma 3 (P; C).** Let the decoded table of oracle `i` be `P[b][j]`, arbitrary on the aux slots,
and let the claim before step 1 be `<P, W> = T`, false. After step 3 the claim
`<p', W'> = T'` for `p' = fold(P, gamma)` is true with probability at most
`1/q + kappa * 3/q` (union over the rounds; `1 - (1 - 1/q)(1 - 3/q)^kappa` exactly), and with
probability at most `1/q + kappa * 2/q` if the aux rows are constant across lanes.

*Proof.* Step 3 fixes the function the batch must end in:

    H(x) = rho * sum_j P^(x)[j] W^(x)[j]  +  sum_m P^(x)[aux_m] mono_m(x) ,

with `P^(x)`, `W^(x)` the multilinear extensions over the lane index (`p' = P^(gamma)`), so
`<p', W'> = H(gamma)`. `H` is a polynomial of degree at most 3 in each variable (2 in the first
term; 1 + 2 in the second), fixed by the committed table and `rho`. `sum_b H(b) = rho <P, W> +
M` with `M = sum_b sum_m P[b][aux_m] mono_m(b)` fixed before `rho`. The verifier's head is
`rho T + G`. `rho (<P, W> - T) = G - M` holds for at most one `rho`: `1/q`. Otherwise the head
differs from the true sum and the rounds are a sumcheck on `H` whose messages have degree 2: in
each round the prover's message differs from the true partial-sum polynomial (their sums differ),
the difference has degree at most 3, and the claim stays false unless the challenge is one of its
at most 3 roots. With lane-constant aux rows the second term has degree 2. ∎

The mask family, its staircase structure and the honest layout play no role: any committed table
defines some `H`. A non-codeword in the aux rows is either within the radius (then `P` is its
decoding) or the oracle is far (Lemma 2).

C (`results/mask_batch.txt`): the game value over all strategies. `GF(4)`, `kappa = 1`, all `4^6`
aux tables: 0.6250. `GF(8)`, `kappa = 1`, all `8^4` cubic effective masks: lane-constant 0.3438 =
`1 - (1 - 1/q)(1 - 2/q)`, lane-varying **0.3750 = 3/q**, bound 0.4531. `GF(8)`, `kappa = 2`, 200
searched tables: lane-constant 0.5078, best found 0.5312, bound 0.6582. The `3/q` term is real: a
prover that varies the top aux rows across lanes gains what the bound says and no more.

### 4.3 Masked batch, affine combiner

**Lemma 3A (P; C for one round).** Same statement with `3/q` per round, challenges `(alpha_j,
beta_j)` uniform in `F^2`.

*Proof.* With `W' = W_F + alpha (W_F + W_G)` the unmasked message is
`q(a, b) = <G + (a + b X) F, W_F + a (W_F + W_G)>`, in `span{1, a, a^2, b, ab}`, and the verifier's
update forces `[1]q + [a]q = claim` (S, read off `verify_whir`; P). The mask's final value is
`sum_j g_j(alpha_j, beta_j) + c` (Theorem 1' with `u = 1`), so step 3 puts weight `e(alpha_j,
beta_j)` on the aux slot of the coefficient of monomial `e` of round `j`. Define
`H(alpha, beta) = rho <p', W'> + sum_m p'[aux_m] omega_m` as a polynomial in all challenges;
`p'` has total degree 1 in each round's pair, `W'` degree 1 in `alpha_j`, `omega_m` degree at most
2 in one pair: `H` has total degree at most 3 in each pair. Extend `lam = [1] + [a]` to all
polynomials in `(a, b)` and let `V_j = lam_{j+1} .. lam_n H`. The verifier's claim after round `j`
is the prover's message at the challenge, and the message `q_{j+1}` satisfies
`lam(q_{j+1}) = claim_j`; if `claim_j != V_j` then `q_{j+1} != V_{j+1}(r_{<=j}, .)`, a nonzero
polynomial of total degree at most 3 in two variables, zero on at most `3q` of the `q^2` pairs.
`V_0 = rho <P, W> + M`: one bad `rho`. ∎

**Finding F-1 (construction defect, fixed).** `zk-hiding-commitment.md` 6.1 writes each mask
coefficient "into every lane of its row", which reproduces the coefficient under the eq-fold
(`sum_b eq(gamma, b) = 1`). Under `G + (alpha + beta X) F` it does not: the folded slot holds
`(1 + alpha) a + beta (X a)`, and multiplication by `X` also pushes the top carried coefficient of
every `F` lane into the first aux slot. An honest A prover built to that layout fails the final
relation. **Fix:** the layout of section 2.1 (last lane only; `kappa_i` guard slots).
C (`results/affine.txt`): 300 honest runs each over `GF(16)`, `kappa = 1` and `2`: every-lane
layout accepted 24 and 17 times, last-lane layout without guard slots 26 and 21, the fixed layout
300 and 300. Soundness does not depend on the layout (Lemma 3A); exact game value of one round over
`GF(8)`, 48 committed tables with arbitrary aux and guard slots: 0.3438 in all, bound 0.4531.
Zero knowledge under the fix (P): the round messages are computed from the mask coefficients, not
from the lanes, so Lemma S is unchanged; the one lane that holds the coefficients is opened only in
rows padded by its own `t_i` random coefficients (Lemma E); the guard slots hold the fold's high
part, which is carried into the next oracle as before. The fix does not touch the eq-fold
construction: `zk-commit/test_code.py`, `test_whir.py`, `test_basecase.py` rerun on 2026-11-19 on a
copy, all `FAILURES 0`. Follow-up of the same day: zero knowledge of A's composed opening with this
layout is now Theorem W-A of `zk-hiding-commitment.md` 6.2a, checked by `zk-commit/test_whir_a.py`
(rank equal to the accepting dimension on five instances, six controls) (C).

### 4.4 Code switch with a lane that is not a power of two long

**Lemma 4 (P).** State before step 4: oracle `i`'s lanes are within `e_i` rows of the code with
decoding `P`, `p' = fold(P)`, and `<p', W'> = T` is false; or the folded word `fold(f_i)` is not
within `e_i` rows of the code. Whatever oracle `i+1` is, the probability over the positions and
`lam` that oracle `i+1` is within its radius with a decoding `u` satisfying the new relation
`<u, W' + sum lam^q X(y_q)> = T + sum lam^q v_q` is at most

    ((1 + rho_i)/2)^{Q_i} + Q_i / q        (rho_i = lrow_i / N_i;  family A: (lrow_i + kappa_i) / N_i).

*Proof.* `u` restricted to the carried slots is a polynomial of degree below `lrow_i`, by the shape
of the weight. The new relation is a polynomial identity in `lam` with constant term
`<u, W'> - T` and coefficients `u(y_q) - v_q`; if it does not hold coefficient by coefficient it
holds for at most `Q_i` values of `lam`. Coefficientwise: (a) `fold(f_i)` far: `u` on `D_i` is a
codeword, so it equals the far word on at most `N_i - e_i - 1` rows, and all `Q_i` positions must
fall there. (b) close and `u = p'`: the constant term is false. (c) close and `u != p'`: `v_q =
p'(y_q)` outside the at most `e_i` corrupted rows, and two distinct polynomials of degree below
`lf_i` (family A, `lf_i = lrow_i + kappa_i`; family B, `lf_i = lrow_i`) agree on at most `lf_i - 1`
points (amended 2026-11-19, `theorem-s-referee.md` m-2; the displayed bound already used `lf_i`): each position passes with probability at most
`(e_i + lf_i - 1)/N_i <= (1 + rho_i)/2`. ∎

Nothing here uses that `lrow_i` is a power of two, or that oracle `i+1` has any relation to `D_i`.
The folded excess is part of `p'` and is tested with it. Under unique decoding there is one
decoding, so no out-of-domain sample is needed; if one is taken for zero-knowledge reasons it joins
the `lam` batch (`(Q_i + o_i)/q`) and restricting it to points outside `span(S, beta)` changes no
bound here.

### 4.5 Base case: the padded final message and the extra column

**Lemma 5 (P; C).** State before `c`: the last oracle's lanes `f` and column `g = Gcol` are
committed, `v = fold(f, gamma)`; either `v` is not within `e` rows of the code, or it is, with
decoding `p'`, and `<p', W'> = T` is false. Then the verifier accepts with probability at most

    (N + 1)/q + ((1 + rho)/2)^Q          (N, rho, Q, e of the last level).

*Proof.* Call `c` *good* if `g + c v` is within `e` rows of the code with decoding `z_c` and
`<z_c, W'> = mu + c T`. If `(g, v)` is jointly within `e` rows of a codeword pair `(g*, p')`, then
`z_c = g* + c p'` and `(<g*, W'> - mu) + c (<p', W'> - T) = 0` has at most one root: `mu` is sent
and `g` committed before `c`. If `(g, v)` is not jointly within the radius, Theorem 4.1 applied to
the line `g + c v` gives at most `N` values of `c` for which `g + c v` is within the radius at all.
So `c` is good with probability at most `max(1, N)/q`. If `c` is not good: either `g + c v` is far
from every codeword, in particular from `P*`, and each position passes with probability at most
`(N - e - 1)/N`; or it decodes to `z_c` with `<z_c, W'> != mu + c T`, so a `P*` that passes the
linear check differs from `z_c` and agrees with `g + c v` on at most `e + lrow - 1` rows. The
positions are drawn after `P*`. ∎

**Amendment (2026-11-19, `theorem-s-referee.md` m-1): the check `<P*, W'> = mu + c T` as built.** For
family A the direct check is a tail sumcheck of `n_last = ceil(log2 lf_{L-1})` rounds of degree 2 on the
zero-padded `P*` and the weight (`zk-system-a-gaps.md` 12.1 (a), checklist A26; `wi.rs` `verify_wi`).
State after the last positions: doomed unless the relation `<P*, W'> = mu + c T` is true for the `P*`
sent; with `P*` fixed and the relation false, each tail round keeps the claim false except with `2/q`
([GKR15] Lemma 2.5, p. 27:21, per-round step of its proof pp. 27:22-23,
`d = 2`; Published; restated in [XZZPS19] p. 8; citation amended 2026-11-19, `citation-check-lfkn-gkr.md` D-1), and the terminal check rejects a false final claim. Lemma 5's bound
becomes `(N + 1)/q + ((1 + rho)/2)^Q + 2 n_last / q`; the calculator has charged the tail rounds since
revision 5 (`wi.rounds`, rows `tail0..`).

Binding of the pad is the statement that `g` and `mu` precede `c` and that `Gcol(y)` is read from
the same leaf as the row: the spot check compares `P*` with a word fixed before `c`. `c = 0` is the
bad challenge of an honest-looking prover (the fold drops out of the check); excluding it buys
nothing, because a prover can aim `mu` at any other value of `c`.

C (`results/basecase_sound.txt`): `GF(8)`, `N = 4`, `lrow = 2`, `Q = 2`, no fold. All `8^4` pairs
`(f, g)` up to codewords, every false claim, 32,515 games, each solved exactly over every `mu` and
every `P*`: codeword pairs 0.1797 = `1/q + (1 - 1/q)((lrow - 1)/N)^Q` exactly; one corrupted row
0.3438 = `1/q + (1 - 1/q)(lrow/N)^Q` exactly; pairs outside the radius 0.3438, against
`N/q + (1 - (e + 1)/N)^Q = 0.75`. The per-case bounds of the proof are attained; no pair exceeds
them.

---

## 5. Theorem

### 5.1 Round-by-round soundness

**State.** After each verifier message the state is *doomed* unless: the current (partially
folded) word of the current oracle is within its radius, with decoding `U`, and the verifier's
current claim equals the true value for `U` (`V_j` of Lemmas 3, 3A during a batch; the relation
between batches); after `c`, unless `c` is good in the sense of Lemma 5. Before any message the
state is doomed if oracle 0 is far or its decoding does not satisfy `<P, W> = T`.

**Amendment M-1 (2026-11-19, `theorem-s-referee.md` M-1): the state names its code.** Lemma 2A
certifies a lane on the `G` branch only to one degree more, so "within its radius" must be read in the
following codes; the paragraph above is to be read with them, and the theorem below holds as stated with
them (the proof is unchanged: Lemma 2A applied pair by pair with each pair's own degree gives the
transition exactly).

- *Admissible code of oracle `i` before its fold rounds*, `A_{i,0}`: the tuple of lanes in which lane `b`
  lies in `C[lrow_i + g_b]`, `g_b` the number of the level's `kappa_i` fold rounds in which lane `b`'s
  path takes the `G` branch (family B, eq-fold: `g_b = 0`). After fold round `j`, `A_{i,j}` is the image
  of `A_{i,j-1}` under the round's combiner: every lane of degree below `lrow_i + j` (at most
  `lf_i = lrow_i + kappa_i` after the last round).
- *Radius*: the uniform `e_i = floor((N_i - lf_i)/2)`. Every lane code above has dimension at most
  `lf_i`, so `e_i` is inside each lane code's unique-decoding radius and **decoding is lane by lane and
  unique** (Berlekamp-Welch per lane, each in its own `C[lrow_i + g_b]`).
- *Doomed* is relative to `A_{i,j}` at radius `e_i`: the current word is not within `e_i` rows of
  `A_{i,j}`, or it is, and the current claim is false for its decoding. Before any message: oracle 0 is
  not within `e_0` of `A_{0,0}`, or its decoding `Dec(O_0)` does not satisfy `<P, W> = T`.
- *Soundness is unaffected as built.* The weight is zero beyond the carried slots
  (`novel_weight_below(.., carried)` in `wi.rs`), and the identity `lambda(q) = <F, W_F> + <G, W_G>` of
  Lemma 3A holds for lanes of any length, so the claim, and the witness the extractor reads, depend only
  on the carried slots: a lane's excess degree carries weight zero.

**Theorem S (P).** In the unique-decoding regime (`delta_i = (1 - rho_i)/2` with the true
`rho_i`), W-I is round-by-round sound: from a doomed state, each verifier message leaves the state
doomed except with the probability below, and a doomed final state is rejected.

| Round (verifier message) | Error | By |
|---|---|---|
| `rho_i` | `1/q` | Lemmas 3, 3A |
| fold round `j` of level `i` | `max(n_i/q, 3/q)`; the calculator charges `(n_i + 3)/q` | far: Lemma 2 (B), 2A (A); close: Lemmas 3, 3A |
| positions of oracle `i` and `lam`, `i < L-1` | `((1 + rho_i)/2)^{Q_i} + (Q_i + o_i)/q` | Lemma 4 |
| `c` | `(N_{L-1} + 1)/q` | Lemma 5 |
| positions of the last oracle | `((1 + rho_{L-1})/2)^{Q_{L-1}}` | Lemma 5 |
| tail sumcheck round `t`, `t < n_last` (family A; amendment m-1) | `2/q` | Lemma 5 amendment (sumcheck, [GKR15] Lemma 2.5; amended 2026-11-19) |

`n_i` is the row count in the proof; the calculator keeps the larger length of the unfolded
codeword, as before. Against the non-hiding opening: `L + 1` more rounds, `3` for `2` in the fold
rounds, the true rates. Proof: the lemmas, in the order of the table; a far state stays far through
a fold round except with `n/q`, a close false state stays false except with `3/q`, and when the
word is close before and after a fold its decoding is the fold of the decoding (Lemmas 2, 2A), so
"claim false for the decoding" is preserved. ∎

Not covered (U): the Johnson regime. There a far word has a list of codewords, each with its own
aux content and its own `H`; the mask and round terms would be multiplied by the list size and
Lemma 5 needs mutual correlated agreement. None of this is written or needed for the design basis,
which is unique decoding.

### 5.2 Knowledge soundness

**Amended 2026-11-19 (`theorem-s-referee.md` M-2, m-3).** The paragraph below (the original text, kept as
the record) does not meet the definition the tree argument needs. The definition is [SG26] (Sharp,
Grubbs, ePrint 2026/2615) **Definition 2.20** (causal round-by-round knowledge soundness, p. 14, read from
the rendered page 2026-11-19): a polynomial-time extractor `E(x, tr|past(i))` and a state function with
(a) every accepted transcript on which `E` fails at every `i` has a challenge where the state moves from
0 to 1, and (b) from state 0, `Pr[State = 1] > eps_i^k` implies that `E` succeeds. Under a total order it
is equivalent to [CMS19] Definition 8.5 with per-round errors ([SG26] **Lemma 2.21**, p. 15). The
replacement of this section is **Lemma K-A** (`lemma-k-a.md`, Original, the Ycash developers, 2026,
DRAFT until refereed): the extractor decodes oracle 0 lane by lane in `A_{0,0}` (M-1) and outputs the
carried witness slots; it is a knowledge extractor with `eps_i^k = eps_i` for every round of the leaf
proof, given the per-round soundness of the rounds outside the opening stated in terms of `Dec(O_0)`
(`round-census-a.md`, `lemma-k-a.md` section 2) and Theorem S as amended. The book's Theorem 31.3.1 is
no longer cited for the definition.

*Original text (record):* The state function is defined through the unique decoding of the committed words, so it is a
knowledge state function: when the initial state is not doomed, the decoding of oracle 0 exists and
its witness slots satisfy the relation. The extractor reads oracle 0 from the prover's random-oracle
queries (the BCS extractor), decodes each lane with Berlekamp-Welch on `D_0` (valid on any domain;
the decoder BCIKS20 section 4.1 describes, S) and outputs the witness slots; salts are part of the
leaf and are discarded. Round-by-round knowledge error = the table of 5.1 (P, given the definition
of round-by-round knowledge soundness in the book, Theorem 31.3.1: statement confirmed in
`soundness-method.md`, definition not re-read here: **(M) for the exact form of the definition**).

### 5.3 Compilation

Unchanged from `soundness-method.md`: Theorems 25.2.1 / 26.1.1 and 31.2.1 / 31.3.1 classically,
CMS19 in the QROM. The new prover messages (`G_i`, `mu`, `P*`) and the new verifier messages
(`rho_i`, `c`) are absorbed and derived like the others; the round count `k` grows by `L + 1`.

---

## 6. Around the opening

**Lemma 6 (masked sumcheck, `rho f + g`) (P).** `g` (column `A` of oracle 0) and `G` are fixed
before `rho`. If `Lam(f) != S`, then `Lam(rho f + g) = rho S + G` for exactly one `rho`, which the
prover may choose by its `G`: error `1/q` whether or not `rho = 0` is excluded (excluding it gives
`1/(q - 1)`). Then the sumcheck on the fixed polynomial `rho f + g`: `d_j/q` per round with
`d_j` the larger of the two degrees. `rho = 0` is the bad challenge of the prover that sends the
honest `G`; it is one instance of the `1/q` term, not an extra attack. C: in
`results/wi_attacks.txt` the strategy that aims `G` at `rho = 0` and the one that aims at
`rho = 5` have the same exact acceptance.

**Lemma 7 (blinder cells) (P; C).** `chat_i(y, x) = c_i(x) + y (1 + y) b_i` with `c_i` and the cell
`b_i` decoded from oracle 0 is a polynomial fixed before every challenge of its component. The
zerocheck over `(y, x)` is a sumcheck on the fixed polynomial
`eq((tau_y, tau), (y, x)) C(chat(y, x))`, which equals `eq(tau, x) C(c(x))` on the cube, so a
doomed state (some `C(c(x)) != 0`) survives `tau` with probability at most `(n_x + 1)/q`, the `y`
round with `(2 deg C + 1)/q`, each `x` round with `(deg C + 1)/q`. The final check uses the
revealed `chat_i`; the opening proves the linear relation `c_i(r) + r_y (1 + r_y) b_i = chat_i` on
the committed vector, with the cell addressed by a fixed position. So the revealed value is the
value at `(r_y, r)` of the committed polynomial `chat_i`, and the check forces
`C(chat(r_y, r))` to be the true final value of the sumcheck. The cell's content is irrelevant to
soundness; at `r_y in {0, 1}` it merely drops out. What would break soundness is a blinder that is
not a committed cell at a fixed position (chosen late, or addressed by a prover-chosen index):
then `chat_i` is free.

C (`results/blinder_sound.txt`): constraint "the column is zero", two rows, dummy variable, ideal
commitment; the exact game value over all message strategies for every nonzero column, every
blinder value and every `tau` (`GF(4)`, 960 games) or six `tau` pairs (`GF(8)`, 3,024 games): for
every column and `tau` the value at any `b` equals the value at `b = 0`; the largest value with
`c(tau) != 0` is 0.5312 = `1 - (1 - 3/q)(1 - 2/q)` at `q = 8`, the bound of the same two rounds
without a blinder.

**6.3 Gadget and GKR layers (P, short).** Gadget (`zk-masked-sumcheck.md` 5.3): `A`, `B` decoded
from oracle 0; `theta`: `(m - 1)/q`; `c`: `1/q` (`beta` before `c`); `z`: `l/q` (`u` before `z`).
GKR layer: `Gtilde` is sent after `rho`, but it is claimed equal to
`<a, omega'> + rho Z (c_0 + alpha c_1)`, a linear functional of the committed `a` with weights
public once `rho`, `alpha`, `r_y` are known, and that claim is among those the gadget proves. Given
the claim, `rho Ahat + Gtilde = rho v + Lam(g')` with `v = Ahat + Z (c_0 + alpha c_1)` fixed before
`rho`, so the only bad `rho` is 0: `1/q`. If the gadget's claim list omitted `Gtilde`, the layer
would be unsound: this is an implementation acceptance criterion (the wire audit, checklist 13).

All of these terms are below `2^-240` at `q = 2^256` and none is the weakest round; the calculator
does not model the components outside the opening (unchanged).

---

## 7. Search for a cheating prover (`zk-sound/`)

Python standard library; `python3 test_*.py` from the directory; each exits non-zero on failure and
writes `results/*.txt`. Run on 2026-11-19: all six exit 0, `FAILURES 0`.

| File | What is attacked | Method | Result |
|---|---|---|---|
| `test_mask_batch.py` | masked batch, adversarial aux rows, `G` aimed at any `rho` | exact game value over all strategies | section 4.2; bounds met, `3/q` attained |
| `test_basecase_sound.py` | padded final message, extra column, any committed words | exact game value, all pairs up to codewords | section 4.5; per-case bounds attained with equality |
| `test_blinder_sound.py` | blinder cells, `r_y in {0,1}` | exact game value, all blinder values | section 6; no gain from any blinder |
| `test_affine.py` | A's round: layout and one-round game | honest runs; exact game value on sampled tables | F-1; bound holds |
| `test_proximity.py` | Lemmas 1, 2, 2A | enumeration and sampling | section 3 |
| `wi.py`, `test_wi_attacks.py` | the whole W-I opening against the verifier of `zk-commit/whir_i.py`; real codes on coset domains, lane lengths 6 to 10 (not powers of two) | strategies with commitments fixed in protocol order; one level: every `(rho, gamma, c)` and every position (`GF(16)`), or 2,500 sampled tuples (`GF(64)`); two levels: 4,000 sampled tuples | below |

Strategies in `test_wi_attacks.py` and their acceptance (one level, `GF(16)`, `N = 8`, `lrow = 6`,
`Q = 2`, exact; "case bound" is `1 - prod(1 - eps_r)` over the rounds of Theorem S for oracles that
are codewords):

| Strategy | Accepted | Bound |
|---|---|---|
| honest, true claim | 1.0000 | |
| false claim; best degree-2 round message; final message that satisfies the linear check and agrees on `lrow - 1` rows | 0.53136 | 0.53136 |
| the same with `G` aimed at `rho = 5` or at `rho = 0`, `mu` aimed at one `c` | 0.53136 | 0.53136 |
| the same with lane-varying aux rows (cubic round polynomial) | 0.53583 | 0.56484 |
| corruption of `e` rows inside the radius, prover plays a second polynomial that agrees with the first on `lrow - 1` rows | 0.58984 = `1 - (1 - 1/q)(1 - ((lrow - 1 + e)/N)^Q)` | `1/q + ((1 + rho)/2)^Q` = 0.82812 |
| oracle spliced from two codewords, outside the radius | 0.29688, exactly the agreeing rows or `c = 0` | `N/q + (1 - dist)^Q` |
| non-codeword extra column with the gambles | 0.07224 | 0.53136 |

Over `GF(64)` (`N = 32`, `lrow = 7`, `Q = 3`) the same strategies give 0.063 to 0.073 against
0.067 to 0.083 (sampled, tolerance 0.02), the radius attack 0.189 against 0.242. Two levels,
`GF(64)`: switching the polynomial at the code switch, all gambles, with and without lane-varying
aux rows: 0.36 to 0.51 against 0.52 to 0.54. No strategy exceeds its bound. The radius attack
shows the query term is not slack: `(lrow - 1 + e)/N` per query is reached, one row short of
`(1 + rho)/2`.

Limits of the search, stated plainly: exact optimality is established only for the three component
games (ideal oracle or no fold, fields of 4 and 8 elements); the whole-protocol runs are specific
strategies, not an optimum; the `n/q` proximity terms are vacuous at these field sizes and are
exercised only through `test_proximity.py`; nothing here runs either system's code.

### Findings

| # | Finding | Fix or action | Zero knowledge |
|---|---|---|---|
| F-1 | A's affine combiner does not reproduce an aux coefficient written into every lane, and its `X` multiplication spills carried coefficients into the aux slots (C) | last lane only, `kappa_i` guard slots (section 2.1); the calculator's layout counts them | argument in 4.3 (P); eq-fold tests rerun green; A's composed opening still (U) |
| F-2 | adversarial aux rows raise a fold round's algebraic term to `3/q`; attained at toy size (C) | accounted in the calculator; no change to the construction | none |
| F-3 | `P*` must be absorbed before the last positions; `Gcol`, `mu` before `c`; `G_i` before `rho_i`; blinder cells before their component's challenges. All hold in the specified order; the first is missing from the Fiat-Shamir conditions of `zk-composition.md` section 6 | add the rows of section 2.3 as transcript tests in both systems | none |
| F-4 | `Gtilde` (GKR) is the one message sent after the challenge it must not depend on; sound only through the gadget's claim list | acceptance criterion: the wire audit shows every `Gtilde` among the gadget's claims | none |
| F-5 | excluding `rho = 0` or `c = 0` has no soundness value | none; do not rely on it | none |
| F-7 | (found while testing F-1's layout in the composed opening) with the random slots at an offset aligned to `t_i` only, A's `X` multiplication moves a random coefficient whose slot index has all low bits set down into the aux slots; honest proofs fail at fold 2 (C: 30/30) | align the offset to `2^ceil(log2(t_i + kappa_i))`; in `whir_a.py` and in `wi.layout` | Theorem W-A holds with it (C) |
| F-6 | `zk-hiding-commitment.md` 1.3 and 6.3 quote later rates `2^-4, 2^-6, 2^-8`; the design basis has `2^-6, 2^-8, 2^-10` (`design.whir_schedule`), so A's last oracle has `2^20` rows, not `2^18`. Its section 8 counts level-0 aux rows without the factor `[F : K]` (4 rows per coefficient over `GF(2^64)`); they still fit under the alignment | corrected in the calculator; the lead may correct the text | none |

---

## 8. Calculator

`soundness/src/yugen_soundness/wi.py`, tests `tests/test_wi.py` (12 new; 56 pass, the 44 existing
ones unchanged). `uv run yugen-soundness --wi [--proofs N] [--attempts A]` prints the tables below
(saved as `soundness/output/wi-tables.txt`). All sizes are estimates (E) of the same model as the
design basis; B's are scaled by the measured factor 1.33.

### 8.1 W-I terms and layout

`wi.rounds` is the table of section 5.1. `wi.layout` computes per level: carried slots, guard slots
(A), aux slots (`1 + 2k` or `1 + 4k`, times `[F : K]` at level 0), `t_i = Q_i`, aligned offset,
`lrow_i`, the degree used for the rate (`lrow_i`, plus `k_i` for A). Query counts and lane lengths
depend on each other; `wi.solve` finds the fixed point and trims it to be minimal. `wi.size_bytes`
adds `G_i`, the longer final message, `mu`, and `Gcol` at the last level's rows (same leaves, no
extra paths).

### 8.2 Category 1, per proof (the design basis's definition: four-layer chain)

| System | Opening | Queries | Lane lengths | Rates | Leaf (KiB, E) |
|---|---|---|---|---|---|
| A | not hiding | 171, 119, 117, 116 | `2^19, 2^16, 2^13, 2^10` | `2^-2, 2^-6, 2^-8, 2^-10` | 443 |
| A | **W-I** | 171, 119, 117, 116 | 524720, 65786, 8440, 1271 | 0.25021, 0.01568, 0.00402, 0.00121 | **455** |
| B | not hiding | 171, 119 | `2^14, 2^10` | `2^-2, 2^-6` | 325 |
| B | **W-I** | 173, 119 | 16813, 1271 | 0.25655, 0.01939 | **341** |
| B | W-M (section 9) | 172, 119 | as not hiding, plus a mask polynomial | `2^-2, 2^-6` | 497 |

W-I costs 12 KiB (A) and 16 KiB (B) and at most two queries; every algebraic round keeps more than
80 bits of slack at a 256-bit field (`(2^26 + 3)/2^256`).

### 8.3 A whole proof tree

A block's tree holds about 1,700 proofs (1,500 leaves, bundles, merges; the lead architect's
figure) and a forger needs one false proof accepted. The design basis charges a union bound over a
chain of four layers (2 bits). The calculator now takes the number of proofs and two models
(`wi.TreeTarget`):

| Model | Statement | Bits needed per round (`k` rounds per proof) |
|---|---|---|
| **union** | every proof is given the whole budget `t` and the errors are added, over `proofs x attempts` proofs | C: `128 + log2(proofs x attempts) + 1 + log2(1 + k)`; Q: `2 x 64 + 1 + log2 6 + log2(proofs x attempts)` |
| **shared budget** | one budget of `t` random-oracle queries for everything the adversary computes, every tree it tries included; it outputs one tree | C: `128 + 1 + log2(1 + proofs x k)` (the book's `(t + k) eps` with `k` summed over the output proofs; our reading of Theorem 31.2.1, (M) for multi-instance use); Q: `2 x 64 + 1 + log2 6 + log2(proofs)` (guessing which proof is false; our argument) |

For one attempt the two agree to 0.1 bit: 1,700 proofs cost **log2(1,700) = 10.7 bits**, i.e.
about 144 bits per round instead of 136. They differ on attempts. In the shared-budget model an
attempt that fails is only oracle queries, which `t` already counts: grinding over many blocks or
many candidate trees costs nothing extra, because the definition `eps(t) <= t / 2^kappa` is already
"success per unit of work". In the union model each further tree adds to the sum:
`attempts = 2^20` costs 20 more bits. The shared-budget model is the one that matches the
adversary (a forger is limited by hash evaluations, not by the number of trees it may consider);
the union model with attempts is shown for a reader who wants per-instance error probabilities
multiplied out.

How such targets are conventionally stated: NIST's categories compare with breaking **one**
instance (key search on one AES-128 key), so a category claim is per instance; multi-target
security is treated as a separate desirable property, and AES-128 itself loses `log2(targets)` bits
against a many-key attacker (M: the call for proposals' wording was not re-read; the single-key
definition is the one quoted in `soundness-method.md` 8.1 from the NIST page). Symmetric designs
that want the tree-wide property state it as a second, stronger claim. Both are given:

| cat1 target | A leaf, W-I | B leaf, W-I | B leaf, W-M | A bundle | B bundle |
|---|---|---|---|---|---|
| per proof (NIST's convention; design basis) | 171, 119, 117, 116: **455 KiB** | 173, 119: **341** | 172, 119: 497 | 140, 117, 116, 116: **589** | 140: **850** |
| whole tree of 1,700 proofs (either model, one attempt; shared budget with any number of attempts) | 184, 128, 125, 125 (126 in round 3 under the union model): **482 KiB** | 185, 128: **359** | 183, 127: 524 | 150, 125, 125, 125: **625** | 150: **904** |
| union model, 1,700 proofs x `2^20` trees | 213, 148, 146, 145: 547 | 215, 149: 408 | 213, 147: 594 | 174, 146, 145, 145: 712 | 174: 1,034 |

The tree-wide target costs 6 % of the leaf and of the bundle. The hash term is not affected by the
number of proofs (`3.5 t^2 / 2^lambda` counts collisions anywhere), so the digest rule of
`soundness-method.md` 8.2 is unchanged, including its 3.4-bit shortfall at 256 bits under the
proven rule. Recommendation: adopt the whole-tree row as the parameter set (`--proofs` as a
recorded parameter), and state the claim as "category 1 for the tree, shared-budget model".

---

## 9. Should both systems carry W-I?

What W-I adds to a system's soundness argument, beyond the non-hiding opening it already has:
Lemma 1 (an identity), section 4.1 (weights), Lemmas 3 / 3A, 4, 5. Each is elementary and each rests
on BCIKS20 Theorem 4.1 or 1.6, which both systems' non-hiding soundness uses anyway. After this
document the common-mode risk is not an unproven theorem; it is (a) an error in these five proofs,
(b) the same misreading of them by two implementations. The two leaves also share the items of
section 6. Against that, the plan's premise is that one soundness flaw must not be fatal, and W-I
changes the opening itself in both.

Two alternatives that share less:

**W-M, full mask (commit-and-prove with a separate masking polynomial).** Commit, in the same
leaves as the witness `p`, a uniform polynomial `m` of the same shape over `F`; the prover sends
`G = <m, W>`, the verifier `rho`, and the **unmodified, non-hiding** opening runs on the virtual
oracle `rho p + m` with claim `rho T + G` (level-0 rows are read as `rho x (p's row) + (m's row)`).
`p` carries `t = Q_0` random coefficients per lane on a coset domain; later oracles and the final
message are those of the non-hiding opening. This is construction F-1 of
`zk-hiding-commitment.md` section 7 applied to the WHIR-style opening.
Soundness (P): if `(f_p, f_m)` is not jointly within the radius, `rho f_p + f_m` is within it for
at most `N` values of `rho` (Theorem 4.1); if it is, with decodings `(p*, m*)`, the non-hiding
opening proves `rho <p*, W> + <m*, W> = rho T + G`, false for all but one `rho`. One added round,
`(N + 1)/q`, and then the opening's own soundness, **untouched**: no aux slots, no base case, no
change of dimension except level 0's `t` coefficients. Zero knowledge (P, the two-line argument of
Theorem BF-1; not tested as a whole): `rho p + m` is uniform and independent of `p`; `p`'s opened
rows are hidden by Lemma E. Cost (E): the mask rows in every level-0 query; B leaf 497 KiB against
341 with W-I (+156 KiB; 524 against 359 tree-wide); the prover commits a second polynomial of
`2^19` elements of `F` (16 MiB of coefficients, 64 MiB as a rate-1/4 codeword). For A the mask
would be `2^24` elements of `F`, 2 GiB as a codeword: not viable on a phone.

**W-S, the mask-oracle layout of the pinned Plonky3** (an implementation of an earlier version of
ePrint 2026/391, with the characteristic-2 replacements of `zk-hiding-commitment.md` 3.4): separate
small mask oracles, power-of-two messages. Soundness status: no analysis of this layout was read;
the paper as published (revision of 2026-11-16) analyses the in-oracle layout, in the
list-decoding regime. The port changes the code's protocol in three places; the replacements
themselves (coset domain, mask
family, out-of-domain rule) are soundness-neutral by Lemma 1 and by the remark after Lemma 3 (any
committed mask), but the mask oracles' spot checks and the base case with several blinds are not
analysed here (U). Cost about +270 KiB on the A leaf (E, from that document). It shares the base
case and the claim-level masks with W-I, so it is less independent than W-M and its soundness is
less established here than W-I's.

**Recommendation.** System A: W-I (the only one of the three that fits a phone prover at A's
statement size). System B: **W-M**. Then the two hiding openings share, for soundness, only Lemma 1
and BCIKS20 Theorem 4.1; A's hiding rests on Lemmas 3A, 4, 5 and B's on one application of the
line theorem in front of an unmodified opening. Cost: 156 KiB on each B leaf (165 KiB tree-wide)
and a second level-0 codeword in B's prover; B's leaf stays below A's plus 10 %. If the lead
architect prefers the smaller proof, the fallback is W-I in both with the review of section 10
completed before release, and W-M kept as a parameter-selectable opening in B; the calculator
prints both. The masks and blinders outside the opening stay common to both systems under either
choice; their soundness is section 6.

Acceptance criteria if W-M is adopted for B: `zk-commit`-style rank test of the W-M view at toy
size; a `zk-sound`-style exact game for the `rho` step; B's size and prover memory measured with
the mask polynomial.

---

## 10. Review sheet for an external cryptographer

**Setting.** `F = GF(2^k)`; Reed-Solomon codes of arbitrary dimension on additive cosets,
interleaved by rows; unique-decoding regime throughout; WHIR-style opening of a linear claim with
fold by `eq` (B) or by `G + (alpha + beta X) F` (A); construction W-I as in section 2.

| # | Statement | On paper | Computation | Open |
|---|---|---|---|---|
| 1 | Lemma 1: the code on `beta + S` is the code on `S`; any dimension | yes | `GF(16)`, `N = 8`, `d = 3, 5, 6`, all words | |
| 2 | Lemma 2: interleaved line correlated agreement inside the radius, error `n/q`, from BCIKS20 Theorem 4.1 | yes | all pairs `GF(8)`, `n = 4`; 4,000 sampled quadruples | |
| 3 | Lemma 2A: the affine combiner with degree raised by one, error `n/q`, from BCIKS20 Theorem 1.6; lanes certified to degree `d +` (G branches) | yes | 1,500 sampled pairs, `GF(8)`, `n = 4` | compared with CWYZ26 (read, C-19): consistent; its Proposition 6.2 shows the order `n/q` is necessary without agreement loss |
| 4 | Lemma 3: masked batch with arbitrary aux rows, `1/q + 3 kappa/q` | yes | exact games: `GF(4)` all tables; `GF(8)` all effective masks (`kappa = 1`), search (`kappa = 2`) | |
| 5 | Lemma 3A: the same for A's round, total degree 3 | yes | exact game, one round, `GF(8)`, 48 tables | more than one round; the prover-side meaning of the four scalars was derived from the verifier only |
| 6 | F-1, F-7: aux layout for A (last lane, guard slots, offset aligned to `t + kappa`); zero knowledge of A's composed opening (Theorem W-A) | yes | 300 honest runs, `kappa = 1, 2`, `GF(16)`; `zk-commit/test_whir_a.py`: rank = accepting dimension, five instances, six controls | alphabet below `F` at level 0 |
| 7 | Lemma 4: code switch for lanes of any length | yes | inside the two-level attack runs only | |
| 8 | Lemma 5: base case with the pad as a column, `(N + 1)/q + ((1 + rho)/2)^Q` | yes | exact games, all committed pairs, `GF(8)`, `N = 4`, no fold | with a fold: strategies only |
| 9 | Theorem S: round-by-round soundness of W-I, unique decoding | yes, from 1 to 8 | strategies against `whir_i.verify`, one and two levels | **Johnson regime (list decoding): not attempted** |
| 10 | Knowledge soundness (5.2) | yes, given the book's definition | none | the exact form of the definition was not re-read |
| 11 | Lemma 6: `rho f + g`, `1/q`; `rho = 0` not special | yes | inside 4 and the attack runs | |
| 12 | Lemma 7: blinder cells bind `c(r)` | yes | exact games `GF(4)`, `GF(8)`, linear constraint, two rows | higher-degree constraints: by the same proof, not computed |
| 13 | 6.3: gadget and `Gtilde` | sketch | none | the gadget is this project's own construction |
| 14 | Order table (2.3) | yes | four reversed-order controls | through-the-code transcript tests in both systems |
| 15 | W-M (B's opening): soundness `(N + 1)/q` + the unmodified opening; zero knowledge (Theorem W-M) | yes | `zk-commit/test_wm.py`: rank and enumeration, four controls | exact game for the `rho` step; measurement of size and prover memory |
| 16 | Tree composition (8.3), shared-budget model | argument | none | the multi-instance reading of the book's Theorem 31.2.1; the QROM factor `proofs` |

Questions to answer:

1. Lemma 2: is the passage from Theorem 4.1 for single lanes to rows correct, in particular the
   identification `w_c(gamma) = a_c + gamma b_c` and the count `|Dis| <= e`?
2. Lemma 2A: is Theorem 1.6 applicable to `{G + alpha F + beta xF}` with the code `C[d+1]`, and is
   the conclusion "`F` in `C[d]`, `G` only in `C[d+1]`" harmless for the relation proven (extra
   coefficients carry weight zero)? CWYZ26 (read, C-19) gives a better error only with one
   coordinate of agreement loss, and the same certified degrees; its Section 5 variant removes the
   excess with one more challenge.
3. Lemma 3 / 3A: the summand `H` is defined by the verifier's own weights on the folded lane. Is
   there any committed content of the aux, gap or random slots, in any lane, for which the batch's
   end claim is not `H` at the challenges?
4. Lemma 4: is the state function well defined across the code switch when oracle `i+1` is
   committed between the last fold challenge and the positions? Does drawing `lam` in the same
   message as the positions (leanVM) rather than after the rows are opened change the bound?
5. Lemma 5: the case split on `(g, v)` jointly within the radius; the claim that a `P*` passing the
   linear check must differ from `z_c`; the role of `c = 0`.
6. Theorem S: is "doomed" a valid round-by-round (knowledge) state function in the sense of the
   book's Definitions behind Theorems 31.2.1 / 31.3.1, with deferred linear checks on committed data
   (gadget, `Gtilde`)?
7. Is unique decoding with the true rates the only place where the non-power-of-two dimension
   enters? (Section 4.1 claims so.)
8. Tree composition: which of the two models is the accepted one for a statement such as "category
   1 for a block's proof tree", and is the QROM term right?
9. The Johnson regime for W-I, should the project ever want it: what replaces Lemmas 3 and 5.

Where to look for an error first: Lemma 2's counting step; the degree bookkeeping of Lemma 3A; case
(c) of Lemma 4 for family A (the folded lane has `lrow + kappa` coefficients); the order rows for
`P*` and `Gtilde`.

---

## 11. What this document changes elsewhere

For the lead (this agent does not edit other documents): `zk-hiding-commitment.md` 6.1 needs the A
layout of F-1; its 6.3 sketch is replaced by sections 3 to 5 here; its 1.3 / 6.3 rates and section
8's A lane lengths (now `2^19 + 432`, `2^16 + 250`, `2^13 + 248`, `2^10 + 247` for the folded
lanes) are corrected by `wi.layout`; `zk-composition.md` section 6 gains the order rows of 2.3 and
checklist item 17 is done by `soundness/`; `soundness-method.md` should cite BCIKS20 Theorem 1.6
for affine spaces and gain the tree target; `design-basis.md` leaf sizes become 455 / 341 KiB per
proof and 482 / 359 KiB tree-wide with W-I (625 / 904 KiB bundles tree-wide). Plan: the union
bound over four layers is replaced by the tree target if the lead adopts section 8.3.
