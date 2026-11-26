# System A: the gaps between the checklist and the real prover

Part of Yugen. The team building checklist A1 to A17 in system A (leanVM) listed where
the documents do not cover what the pinned prover does: `yugen-proof-a-zk/docs/zero-knowledge.md`
sections 12 to 14 (instances S1 to S12, matches M-1 to M-4, gaps G-1 to G-5). This document closes
each item with a construction, a paper proof, a reference test with negative controls, the
soundness effect and a checklist entry. The entries are also appended to
`zk-implementation-checklist.md` as A18 to A25.

Status tags: **(P)** proven on paper here or in the documents named; **(C)** checked by exact
computation in `zk-lemma/`, `zk-commit/` or `zk-sound/` (file named with the claim); **(S)** read
in the pinned source or its specification (`yugen-proof-a-zk/vendor/leanMultisig`, file named);
**(M)** from memory, not verified; **(U)** open.

Notation: `K = GF(2^64)`, `F` the 256-bit challenge field, `q = |F|`, `g` the generator of `K*`
the VM counts with. "The lemma document" is `zk-masked-sumcheck.md`, "the commitment document"
`zk-hiding-commitment.md`, "the composition document" `zk-composition.md`.

Provenance (citation audit of 2026-11-19; `../REFERENCES.md` Part 3, O-9 and O-10). Everything
stated in this document is Original (the Ycash developers, 2026) as far as checked: it concerns
the pinned leanVM statement, and the five papers read in the audit contain nothing on the count
root, the bit slices, the dummy variable (A8, A8-T, Proposition D), the linear hand-off
(Proposition L), the Keccak layer chain (M1), the radix-4 bus GKR (M2) or the shared root.
Published ingredients used: "Libra's mask" is the mask of Xie, Zhang, Zhang, Papamanthou, Song,
ePrint 2019/317, Section 4.1, Construction 1, used inside an `eq` factor (Corollary B of
`zk-masked-sumcheck.md`); the multiplier that vanishes on the cube adapts Section 4.2, equation
(7), of the same paper; the base case of section 12 adapts Construction 7.2 of Chiesa, Fenzi,
Weissenberg, ePrint 2026/391. Unread and still marked: Katz's character-sum bound (9.2).

## 0. Results

| Item | Verdict | Section | Reference test |
|---|---|---|---|
| G-1 count root | The proposal hides the root and is sound. Two corrections: the leaf's own value must never be sent (it enters a later head linearly), and the reason given for an `F`-valued leaf is wrong, although an `F`-valued leaf is the convenient choice. No soundness term, no completeness loss | 1 | L `test_count_root.py` |
| G-3 bit slices | Not covered by A8: a slice is `F_2`-linear in the cells. Unmasked, the 64 slices reveal up to `64 x 256` bits. Mask: a block of 256 `K` cells read through a fixed `F_2`-basis of `F`; the ring switch runs unchanged on the enlarged cell set | 2 | L `test_slices.py` |
| G-4 dummy variable on S4 | A8 is confirmed with three corrections: the dummy round must use a weighted functional (the plain sum over `y` is identically 0); its degree is `2 deg C`, which is 4 on S4, not 6 or 7; the same theorem allows a cheaper form (A8-T: multiplier `y`, check `p(0) = claim`, dummy round last, degree `deg C = 2`, the `x` rounds of the prover unchanged) | 3 | L `test_dummy_terminal.py`; D `test_terminal_dummy_sound.py` |
| Reference test M-1 (S5) | Theorem 1' applies with 46 coefficients for the product round. `lam != 0` holds for every challenge with the pinned constants (computed). At `lam = 0` the mask still covers the view, because S5 is the first round of its chain | 4 | K `test_product_round.py` |
| Reference test M-2 (S1) | Lemma 4 holds with four blinders per tree and layer and the combiner inside `Gtilde`. The last layer's children are not column evaluations; the chain ends by a linear hand-off | 5 | L `test_gkr4.py` |
| G-2 read counts | With A8 and A18 in place Z-C1, Z-C2 and Z-C3 are not needed. Drop them | 6 | (argument) |
| G-5 testing | The rank statistic over `K` under one tape, with `d + 2` proofs per witness for a view of `d` words; a translation test for multiplicative pads; no sampling statistic reaches the target distance | 7 | (procedure) |
| Column evaluations (64/64/65) | Closed by blinder cells, checklist item A8, which is not part of W-I. W-I is needed in addition so that proving the cells' relation leaks nothing. Nothing else is needed for that block | 8 | L `test_dummy_terminal.py` |
| W-I base case by a sumcheck; narrow alignment | Sound with `2 n_last / q` added; leaks nothing (both vectors public, `P*` padded in full). The narrow-alignment control is a completeness failure at particular shapes, not a verifier check | 12 | K `test_narrow_align.py` |
| Found while reading | Four more values on the wire that no item names, and M-3 is not Lemma 5 as stated | 9 | L `test_count_root.py` (leaf form) |

Two general statements carry most of the items and are stated once, in section 3: Proposition D
(the one-sided dummy variable) and Proposition L (linear terminals and hand-offs need no dummy
variable).

---

## 1. G-1: the count root

### 1.1 What the verifier sees

(S: `verifier/src/bus.rs::verify_gkr_grand_products`, `verify_bus_balance`;
`doc/leanvm/body/06-bus-interactions.tex`, "The lookup protocol" and "The count product".)

The bus sends two scalars before its GKR: `R`, the one root claimed for both the push tree and the
pull tree, and `R_c`, the root of the count tree. Both are products of leaves (a grand product; no
fraction, no numerator and denominator). The verifier's only check on `R_c` is `R_c != 0`. The
count tree's leaves are the cells of every `cnt*` column on executed rows and 1 elsewhere, so for
an honest prover

    R_c = prod over all reads of (the read's count) = g^(sum over addresses i of 0 + 1 + .. + (A[i] - 1)) ,

with `A[i]` the number of reads of address `i`. It is one element of `K*` (seen as an element of
`F`), and a function of the access histogram, which depends on secret bytes through the range
checks. Anyone recomputes it from a candidate witness: unmasked, it is a distinguisher of
advantage 1 between two witnesses with different histogram sums (C: control "no leaf").

Besides `R_c` the count tree contributes to the view the children of every GKR layer (section 5,
checklist A24) and its leaf claim, which the table sumcheck discharges through the count columns'
evaluations (A8). Those are other blocks with their own pads.

### 1.2 Construction

One leaf of the count tree, at a fixed public position `p` that no block covers (a padding leaf,
which holds 1 today), holds a committed mask `e`:

- `e` is one element of the mask column `A` (four `K` cells read through the basis of `F` over
  `K`), drawn uniformly from `F \ {0}` by the prover (redraw on 0);
- the prover builds the count tree with leaf `p` equal to `e` and publishes `R_c' = R_c e`;
- the verifier's check stays `R_c' != 0`;
- the leaf claim. The verifier reduces the count tree's value at `zeta` to
  `totals[count] = (value) + (public padding terms)` and hands `dot(form_powers, totals)` to the
  table sumcheck as its target. The mask leaf adds `eq(zeta, p) (e + 1)` to the tree's value at
  `zeta`. The verifier adds the public part `form_powers[count] eq(zeta, p)` to the target, and the
  secret part `form_powers[count] eq(zeta, p) e` enters the table sumcheck's `Gtilde` (Proposition
  L, section 3.3): one more weight in a linear claim on column `A` that the gadget already proves.
  **The value of `e` is never sent**, in clear or as an evaluation.

A position `p` exists: every count block has a push block of the same size on the push side, which
also holds the state, memory and bytecode blocks, and the count side is padded to the push side's
depth (S: `06-bus-interactions.tex`, leaf stacks), so the count side has at least one padding leaf.

Variant with a `K` word: `e` uniform in `K*`, stored in one cell. It hides as well (below) but its
value at `zeta` then needs a revealed evaluation with its own cell; the `F`-valued leaf in column
`A` needs neither and is the form to build.

### 1.3 Zero knowledge

**Proposition G1 (P; C).** For every witness, `R_c' = R_c e` is uniform on `F*` and independent
of everything that does not depend on `e`. With the `K`-word variant it is uniform on `K*`.

*Proof.* `R_c != 0` for an honest prover (every count is a power of `g`), and multiplication by a
fixed nonzero element is a bijection of `F*`. For the variant: `R_c` lies in `K*`, because every
count leaf is a cell of a `K`-valued column, and multiplication by it is a bijection of `K*`. ∎

Placement in the pad ledger (composition document 4.1): a new block "count root", pad `e`, law
uniform on `F*`, listed first. `e` then occurs in later blocks only: in the count tree's layer
polynomials (padded by the layer blinders), in `Gtilde` of the table sumcheck (padded by that
sumcheck's mask), in the gadget and in the rows of oracle 0. Lemma T's argument applies with a
group translation in place of an affine one: conditioned on the earlier pads, `R_c e` is uniform
on `F*`. Simulator: sample `R_c'` uniformly from `F*`.

Correction to the implementers' note. They wrote that a `K` word makes the product uniform "only
on a coset of `K*`", so that `e` must be an element of `F`. The coset is `R_c K* = K*` itself,
because `R_c` is in `K*`; a `K` word hides exactly. (It would fail only for a root outside `K*`,
which an honest prover never produces: C, control.) The `F`-valued leaf is preferred for the
reason in 1.2, not for hiding.

C (`zk-lemma/test_count_root.py` part A, `K = GF(4)` in `F = GF(16)`, every `e`): the honest
roots are exactly `K*`; with `e` uniform on `F*` the published value is uniform on `F*` for every
root; with `e` uniform on `K*` it is uniform on `K*`. Controls: no leaf (distance 1); an additive
mask `R_c + e` with `e` nonzero (distance `1/15`: not perfect, and unsound, below); a `K`-word leaf
against a root outside `K*` (distance 1); the leaf also published (distance 1).

### 1.4 Soundness

**Proposition G1-S (P; C).** The memory argument with the mask leaf accepts exactly the
assignments it accepts without it, for every `e != 0`, and accepts nothing for `e = 0`.

*Proof.* The count root has one role (S: Theorem "Lookup correctness" of the specification): its
hypotheses are that the bus balances, that every read's count is nonzero, and that there are fewer
than `2^64 - 1` reads. The count tree proves the second: the product of all count leaves is
nonzero. `F` is a field, so `R_c e != 0` if and only if `R_c != 0` and `e != 0`: a nonzero
published value still forces every count to be nonzero. The leaf is a leaf of the count tree only;
it is in no push and no pull tuple, so balance is the same statement; the number of reads is
unchanged. The GKR proves the product of the leaf vector the committed data defines, whatever
field its entries lie in; `e` is fixed by oracle 0 before every challenge. ∎

No error term is added: the count tree has the same depth and the same rounds. Completeness: the
prover redraws `e` if it is 0 (it chooses `e` before any challenge, so unlike a bus payload it
can avoid the bad value); without the redraw the loss is `1/q`.

What would not be sound: an additive mask (`R_c + e != 0` proves nothing about `R_c`); a leaf the
prover may place or choose after a challenge; a mask multiplied into the root outside the tree
(the published value must be the root the GKR proves).

C (part B; the lookup protocol over `K = GF(4)`, two cells, two reads, all 65,536 assignments of
addresses, counts, values and final counts): 6 assignments are accepted without the leaf; the
accepted set with the leaf equals it for each nonzero `e` and is empty for `e = 0`; no accepted
assignment contains a forged read. Controls: without the nonzero check 308 balanced assignments
contain a forged read (a read with count 0 pulls and pushes the same tuple); the additive mask
accepts forged reads; three reads with counts `1, g, g^2` at a non-entry are accepted with or
without the leaf (the read bound's job, unchanged).

---

## 2. G-3: the 64 bit slices of `q_keccak`

### 2.1 What the verifier learns

(S: `verifier/src/keccak.rs::verify_keccak`, the input opening; `verifier/src/ring_switch.rs`.)

The Keccak reduction ends on `slices[i]`, `i < 64`:

    s_i = sum_u eq(point, u) bit_i(q[u])      in F,

`q[u]` the `K` cells of `q_keccak`, `bit_i` the coordinate on the basis `x^i` of `K`. Two uses:
the input opening's final check `mle(mu, low) <weights, s> = value`, linear in `s`; and the ring
switch, `T = sum_i x^i Phi(s_i)` with `Phi(v) = sum_{k<64} c_k v^(2^k)`, additive and not
`F`-linear, after which one claim `<Phi(eq(point, .)), q> = T` goes to the opening.

Each `s_i` is an `F_2`-linear map of the `i`-th bits of the cells into `F`: up to 256 bits. The 64
slices together are up to `64 x 256 = 16,384` independent `F_2`-linear equations on the committed
Keccak states; the one `K`-linear evaluation `q~(point) = sum_i x^i s_i` is 256 bits. At toy size
(C: `test_slices.py`, 4 cells of `GF(4)` in `GF(16)`): at the 91 of 200 points whose weights have
full `F_2`-rank the two slices take 256 values over the 256 witnesses, so they determine the
witness; the column evaluation takes 16.

Why no existing item covers them: A8 pads a `K`-linear evaluation with a cell that enters the
opening's relation linearly. A slice is not `K`-linear in the cells, and `Phi` is not `F`-linear
in the slice, so "`s_i + Z b_i` with `b_i` a cell" has no linear relation to hand to the opening.
The masking rows of the implementers' layer 2 give each slice 200 uniform bits (25 lanes of 8
permutations), below the 256 needed for a uniform element of `F`, and their weights
`eq(point, u)` carry no rank guarantee (composition document, "Why cells and not blinding rows").

### 2.2 Construction

- **Blinder block.** 256 committed uniform `K` cells `B_j`, `j in {0,1}^8`, in oracle 0. Fixed
  public elements `theta_0 .. theta_7` of `F` whose subset products
  `omega_j = prod_l theta_l^(j_l)` are an `F_2`-basis of `F`: `theta_l = x^(2^l)` for `l < 6`
  (the powers `x^i`, `i < 64`), and the two basis elements of the extension steps of `F` over `K`.
  The blinder of slice `i` is

      b_i = sum_j omega_j bit_i(B_j)      in F.

- **Dummy round.** The input opening's sumcheck chain (the pack rounds, then the slot rounds) gets
  one more round, last, in the one-sided form of Proposition D: the prover sends the polynomial
  `Y -> mle(mu, low) <weights, s + Y b>` (degree 1: one scalar beside the claim), the verifier
  draws `r_y`, the prover sends `shat_i = s_i + r_y b_i`, and the final check is the present one
  on `shat`. With the masked sumcheck of A4 the mask has one more coefficient.
- **Ring switch, unchanged in form.** The verifier computes `T = sum_i x^i Phi(shat_i)` as now.
  The claim handed to the opening is

      sum_u Phi(eq(point, u)) q[u] + sum_j Phi(r_y omega_j) B_j = T ,

  `K`-linear in the committed cells. The second weight has a product form, as `ring_weight` has:
  its multilinear extension at `r'` is `sum_k c_k r_y^(2^k) prod_l (1 + r'_l + r'_l theta_l^(2^k))`.

The identity (P): `Phi` is additive and `Phi(w beta) = Phi(w) beta` for `beta` in `F_2`, so
`Phi(shat_i) = sum_u Phi(eq(point, u)) bit_i(q[u]) + sum_j Phi(r_y omega_j) bit_i(B_j)`; multiply
by `x^i` and sum over `i`, using `cell = sum_i x^i bit_i(cell)`.

### 2.3 Zero knowledge

**Proposition G3 (P; C).** If the cells `B_j` are uniform, independent of everything else, and
`r_y != 0`, the 64 values `shat_i` are uniform on `F^64` and independent, for every witness.

*Proof.* The bits `bit_i(B_j)` are `64 x 256` independent uniform bits. For each `i`,
`b_i = sum_j omega_j bit_i(B_j)` is the element of `F` with coordinates `(bit_i(B_j))_j` on the
basis `omega`: uniform on `F`; different `i` use disjoint bits. Multiplication by `r_y != 0` is a
bijection. ∎

Ledger: block "slices", pad the block `B`, law uniform, excluded event `r_y = 0` (`1/q`). The
cells `B_j` occur elsewhere only as entries of oracle 0 (Lemma E) and inside the dummy round's
message (padded by the sumcheck's mask). The simulator samples `shat` uniformly and computes the
final value of the opening sumcheck and the target `T` from it.

C (`zk-lemma/test_slices.py`): for all 256 witnesses and 6 challenge sets, the map from the 256
blinder blocks to `(shat_0, shat_1)` is a bijection onto `F^2`; the ring-switch identity holds in
12,800 of 12,800 sampled cases; the product form of the weights holds. Controls, each with
different laws for some pair of witnesses: `r_y = 0`; three blinder cells (three bits a slice
against four: support 64 of 256); a weight set of `F_2`-rank 3; one element of `F` shared by the
slices.

### 2.4 Soundness

The blinded slice polynomial `zhat_i(y, u) = z_i(u) + y b_i` is fixed by oracle 0 and public
constants, so the dummy round is a sumcheck round on a fixed polynomial: `+1/q` (degree 1;
Proposition D). The ring switch proves the 64 claims "`shat_i` is the `F`-weighted sum of the
`i`-th bits of the cells `(q, B)` with weights `(eq(point, .), r_y omega)`". Its argument does not
use the shape of the weights (P): with `delta_i` the error of claim `i`, the dense claim's defect
is `sum_i x^i Phi(delta_i) = sum_k c_k D_k`, `D_k = sum_i x^i delta_i^(2^k)`, and `D_k = 0` for all
`k < 64` forces `delta = 0` because the matrix `((x^i)^(2^-k))` is a Moore matrix of a basis of `K`
over `F_2`. So the ring switch's error term is the pinned protocol's own (its value for the
structured coefficients `c_(8p+b) = f_p g_b^(2^(8p))` was not re-derived here), with no addition.

---

## 3. G-4: the dummy variable on the table sumcheck, and two general statements

### 3.1 The sumcheck S4 as it is

(S: `verifier/src/bus.rs::table_sumcheck`, `verifier/src/layout.rs::Form`.)

    target = sum_x F(x),     F(x) = sum_t W_t(x) C_t(columns of table t at x_{< h_t}) ,

a plain sum over the tallest table's cube (`sumcheck(.., 4, [None; n])`: four coefficients a
round, round check `p(0) + p(1) = claim`). `W_t` is the product of the line `1 + e_v + x_v` for
the variables the table owns and of `x_v` for the variables above its height. `C_t` is the batch of
the table's constraints and bus forms, of degree at most 2 in the columns (`Form`: "a polynomial
of degree at most 2"; the round degree 3 is 2 plus the line). After the rounds the prover sends
one evaluation per column of every table (153 at the wallet statement) and the verifier computes
the terminal `sum_t W_t(r) C_t(evaluations)`.

### 3.2 A8 confirmed, with corrections

Blinded columns `chat_i(y, x) = c_i(x) + m(y) b_i`, one cell per column of every table (each
column is evaluated at one point, its table's). The construction of the composition document,
section 3, applies to this batch as it stands: Theorem B's proof uses nothing about `C` beyond its
being a polynomial of the revealed values with public coefficients, and the weights `W_t(x)` do
not involve `y`. Corrections to what the implementers planned:

1. **The dummy round is weighted.** S4 is a plain sum. Summing the dummy variable plainly gives
   `sum_y sum_x Fhat(y, x) = 2 sum_x F(x) = 0` in characteristic 2: the claim is lost (C: cube sum
   0 in 720 of 720 cases, 440 of them with a nonzero target; and an exact game where the plain
   functional on the dummy round accepts a false claim with probability 1,
   `zk-sound/test_terminal_dummy_sound.py`). The dummy round's functional is
   `lam_y(p) = (1 + tau_y) p(0) + tau_y p(1)`, with `tau_y` a challenge or the constant 0; in the
   pinned transcript this is `sumcheck_round_poly` with `eq_factor = Some(tau_y)` for that round.
2. **Degree.** With `m(y) = y(1 + y)` the dummy round's message (reduced form) has degree
   `2 deg C` in `y`: 4 on S4, where `deg C = 2`; 5 if the line `eq(tau_y, y)` is counted, as the
   pinned grinding rule counts it. Not 6 and 7: those are the figures for a batch with cubic
   constraints, which S4 does not have.
3. **The mask** is the family of Theorem 1 for the mixed functionals: plain variables take
   `u = x`, the dummy variable takes `u = 1`. With the dummy variable last this is the present
   staircase mask in `x` with its constant replaced by a full univariate `g_y(y)`:
   `g(x, y) = sum_j ghat_j(x_j) x_{j+1} .. x_n + g_y(y)`, `1 + 3n + d_y` coefficients.

### 3.3 Two general statements

**Proposition D (one-sided dummy variable) (P; C).** Let the dummy variable's functional be
`lam_y(p) = p(0)`. Then the blinded polynomials may be `chat_i(y, x) = c_i(x) + y b_i`
(multiplier `y` in place of `y(1 + y)`), and:

- completeness: `lam_y` applied to the summand gives the unblinded summand, so the claim is the
  original one;
- zero knowledge: Theorem B holds with `Z = r_y`, excluded event `r_y = 0`, probability `1/q`;
- soundness: Lemma 7 of `zk-wi-soundness.md` holds with the dummy round's degree `deg C` in place
  of `2 deg C`;
- the dummy variable may stand anywhere in the round order. Placed **last**, the rounds over `x`
  are those of the unblinded protocol (the prover's code for them is unchanged), and the dummy
  round's polynomial is `P(Y) = sum_t W_t(r) C_t(c(r) + Y b)`, computed from the column
  evaluations and the cells alone; `P(0)` is the incoming claim, so `deg C` coefficients are sent.

*Proof.* Completeness: `chat(0, x) = c(x)`. Zero knowledge: the proof of Theorem B is Lemma T with
two blocks. Block 1, the values `chat_i(r_y, r) = c_i(r) + r_y b_i`, is a bijective image of the
cells when `r_y != 0`. Block 2, the round messages, is uniform on the sequences passing the round
checks by Theorem 1, which holds for arbitrary nonzero functionals per variable and for every
order of the variables; `lam_y = ev_0` is nonzero and `lam_y(1) = 1`, so `u_y = 1`. Soundness: the
polynomial `Fhat(x, y) = sum_t W_t(x) C_t(c(x) + y b)` is fixed by oracle 0 before every challenge
of the component. The protocol is a sumcheck of the claim `lam_x .. lam_y Fhat = target` with a
product of per-variable functionals; a wrong round polynomial survives its challenge with
probability at most (its degree)`/q`, and the last claim is compared with `Fhat(r, r_y)` computed
from the revealed values, which the opening's relation `c_i(r) + r_y b_i = chat_i` forces to be
the committed polynomial's. The cell's content is irrelevant to soundness, as in Lemma 7. ∎

Call the form of the checklist A8 (`m = y(1+y)`, any `tau_y`) and this one **A8-T**. Both are
correct. A8-T is the one to build on S4: two more mask coefficients, two more scalars sent, one
challenge, no change to the prover's `x` rounds.

**Proposition L (linear terminals and hand-offs) (P).** Let a revealed evaluation `v` of
committed data (or of a virtual polynomial the protocol proves) enter the verifier's later
computation only through a linear form: as a term of the claimed value that heads a later masked
sumcheck, or as a term of a masked sumcheck's terminal that is linear in `v`. Then `v` is blinded
with multiplier 1 and no dummy variable: the prover sends `vhat = v + b` with `b` one uniform
element of the mask column `A`, the verifier computes with `vhat`, and the difference, `rho` times
a public multiple of `b`, is added to that sumcheck's `Gtilde` (head) or to its final-value linear
claim (terminal), both of which the gadget proves. If `v` is an evaluation of a committed column,
the opening's relation also contains `v + b = vhat`. `vhat` is uniform; no challenge is excluded;
soundness is that of `Gtilde` (`zk-wi-soundness.md` 6.3): `b` is committed before every
challenge, so the corrected claim is the intended one.

*Proof.* Lemma 5 form 1 of the lemma document for the value, and the shift argument of Lemma 4 for
the head: `rho v + G' = rho vhat + (G' + rho b)`. For a linear terminal:
`s_n(r_n) = rho (k v + rest) + g(r) = rho (k vhat + rest) + (g(r) + rho k b)`, and the bracket is a
linear functional of column `A` with public weights. ∎

C (`zk-lemma/test_handoff.py`, `GF(4)` and `GF(16)`, plain sumcheck of two variables and degree
2, 40 challenge sets each): for witnesses with every value of `v`, the law of
`(vhat, Gtilde, round messages)` over all blinders and masks is identical, and the honest messages
pass the round checks from the head `rho (k vhat + rest) + Gtilde`. Controls: no blinder (laws
differ, 40 of 40); `G` sent unshifted (head check fails, 40 of 40).

A blinder used by Proposition L must lie in column `A` (the gadget proves claims on `A` only). The
opening's relation may address a cell of `A` as it addresses a cell of the blinder column.

### 3.4 Tests

C, zero knowledge (`zk-lemma/test_dummy_terminal.py`). Model of S4: table A with two rows and
columns `a, b`, table B with one row and column `c`, back-loaded
(`F = (1 + e + x) C_A + x C_B`), a quadratic batch and a cubic one, both forms. For fixed
challenges the law of the whole view `(G, round coefficients, mask value, the three blinded
evaluations)` is computed exactly over all 64 or 4,096 blinder triples and all masks (the mask
part as a coset; one case cross-checked by brute force over `4^8` masks: 262,144 distinct views,
equal count tables) and compared between all Boolean witnesses with one target.

| Field | Form | Batch | Round degrees | Multiplier nonzero: identical / different | Multiplier zero: different | Blinder off: different |
|---|---|---|---|---|---|---|
| GF(4) | A8 | quadratic | (4, 3) | 110 / 0 | 80 of 80 | 190 of 190 |
| GF(4) | A8 | cubic | (6, 4) | 94 / 0 | 88 of 88 | 182 of 182 |
| GF(4) | A8-T | quadratic | (3, 2) | 120 / 0 | 52 of 52 | 172 of 172 |
| GF(4) | A8-T | cubic | (4, 3) | 130 / 0 | 44 of 44 | 174 of 174 |
| GF(16) | A8 | quadratic | (4, 3) | 24 / 0 | (no such case drawn) | 24 of 24 |
| GF(16) | A8-T | quadratic | (3, 2) | 22 / 0 | (no such case drawn) | 22 of 22 |

Further controls: a mask one degree short in `y` (rank below `dim V_r`; views differ in 50 of 50
and 94 of 96 cases); the plain functional on `y` (above); the multiplier `y` under `eq(tau, y)`
with `tau != 0` (the sum differs from the target in 523 of 720 cases: the multiplier `y` needs
`lam_y = p(0)`).

C, soundness (`zk-sound/test_terminal_dummy_sound.py`). The A8-T game for the claim "the column is
zero", plain sum with the line inside, dummy round last, ideal commitment: exact value over all
message strategies for every nonzero column, every blinder and every `tau`, `GF(4)` (240 games)
and `GF(8)` (4,032 games). The value does not depend on the blinder; its maximum with
`c(tau) != 0` is `0.6250` and `0.3438`, equal to `1 - (1 - 2/q)(1 - 1/q)`. Controls: plain
functional on the dummy round (value 1); a blinder chosen after the challenges (accepted whenever
`r_y != 0`).

### 3.5 Soundness terms for S4

Mask: `1/q` (already counted for A4). Dummy round: `4/q` (A8; the degree of the reduced
message, `5/q` with the pinned rule that counts the eq line) or `2/q` (A8-T; C: the exact game
value in 3.4 is the bound with the message degrees alone). The relation for
the cells is batched with the other claims by the opening's batching challenge: one more claim in
that batch per revealed evaluation is already counted there; the claim becomes a point claim plus
`r_y` times a cell, so the stacked opening takes a public scalar per claim (the implementers' note
in their A8 row) or, equivalently, one combined weight `sum_i lambda^i eq(point_i, .)` on the
columns plus `r_y lambda^i` on the cells.

---

## 4. Reference test M-1: the Keccak layer chain (S5 to S8)

### 4.1 The chain

(S: `verifier/src/keccak.rs::verify_layer`.) One layer is a claim reduction in three stages:

| Stage | Message | Check | Next claim | Round space, `lam`, `u` |
|---|---|---|---|---|
| S5 | 47 coefficients of `P` | `<functional, P> + iota sum(mu) = claim` | `P(s)` | polynomials of degree at most 46 in `s`; `lam(P) = <functional, P>`; no `u` (first round) |
| S6 | reduced message of degree 2 per pack and segment variable | `(1 + tau) p(0) + tau p(1) = claim` | `p(r)` | Corollary B: `u = 1` |
| S7 | degree 3 per position variable | `p(0) + p(1) = claim` | `p(r)` | Corollary A: `u = X` |
| S8 | `t_0, t_1, t_2` | `at_local (kappa t_0 + (kappa + t_1) t_2) = claim` | `t_0 + beta t_1 + beta^2 t_2` | terminal of degree 2 in the three layer values |

`functional_c = sum of mu_i over the i with bit c of RMFE_PROJECT[i] set`; `mu` are the instance
weights: the eq kernel of four coordinates in the first layer, the sixteen embedding polynomials
`RMFE_EMBED[i]` evaluated at the previous layer's `s` afterwards.

### 4.2 Construction

One claim-level mask per layer (Theorem 1', Lemma S of the commitment document):
`N = 1 + 46 + 2 n_6 + 3 n_7 + d_y` coefficients in column `A`, `n_6` and `n_7` the numbers of S6
and S7 rounds (6 and 11 at the wallet statement: 92 before the dummy round). The prover sends
`Gtilde`, the verifier `rho`, and each message is `rho` times the honest one plus the mask's. The
public term `iota sum(mu)` is multiplied by `rho` with the claim. S8: three blinders per layer and
the dummy round last in the A8-T form: after S7 the prover sends
`P_y(Y) = at_local (kappa (t_0 + Y c_0) + (kappa + t_1 + Y c_1)(t_2 + Y c_2))` (degree 2, two
scalars), the verifier draws `r_y`, the prover sends `that_k = t_k + r_y c_k`, the verifier checks
the terminal on `that`. The next layer's claim is
`t_0 + beta t_1 + beta^2 t_2 = (that_0 + beta that_1 + beta^2 that_2) + r_y (c_0 + beta c_1 + beta^2 c_2)`,
so the next `Gtilde = G' + rho r_y (c_0 + beta c_1 + beta^2 c_2)`: Lemma 4 with three claimed
values and a quadratic combination; the blinder-to-claims map is `r_y` times the identity. After
the last layer the claim goes to the openings (section 2 for the slices, Proposition L for the
output word).

### 4.3 The condition `lam != 0`

**Proposition M1 (P; C).** (a) With the pinned constants, `functional != 0` for every instance
weight vector the verifier can form, for every challenge. (b) Where a round with `lam = 0` is the
first round of its chain, the mask of Theorem 1' still maps bijectively onto the views that pass
the round checks.

*Proof.* (a) `functional = Pi mu` with `Pi` the `47 x 16` binary matrix of `RMFE_PROJECT`. Its
rank over `F_2` is 16 (computed), hence 16 over `F`, so `functional = 0` only if `mu = 0`. In the
first layer `mu` is an eq kernel, whose entries sum to 1. In later layers `mu_i = E_i(s)`; all
sixteen vanish only at a common root of the embedding polynomials, and their greatest common
divisor over `F_2` is 1 (computed), so there is none in any extension field. (b) In Theorem 1' the
mask's first message is `q_1 = g_1 + K_1` (`D_1 = 0`: `u_1` is never used) and
`G = lam_1(g_1) + lam_1(1) K_1`. If `lam_1 = 0` then `G = 0` for every mask, the first check reads
`0 = 0` and constrains nothing, and the passing views are: `G = 0`, `q_1` free in its space, later
rounds as before; the dimension is again `N`. The map is onto: the constant of the target `q_1`
fixes `K_1`, the rest fixes `g_1`, and the induction of Theorem 1 runs from round 2. ∎

So no challenge is excluded for S5 and the hypothesis H1 the implementers asked about holds
always. Had `lam = 0` been possible, zero knowledge would have survived by (b) with a simulator
that sets `Gtilde` to the determined value and samples the first message freely; what a zero
functional damages is the reduction's meaning (all instance weights zero: the next claim is
empty), a soundness matter of the unmasked protocol. A round with `lam = 0` that is not first has
no valid mask (no `u` with `lam(u) = 1`) and the masked messages fail the round checks (C,
control).

C (`zk-commit/test_product_round.py`, GF(2^8)): the pinned constants (rank 16, gcd 1; over every
`s` of `GF(2^8)` the weights and the functional never vanish); the chain at the pinned shape
(S5, 6 eq rounds, 11 plain rounds, `N = 92`; and with the dummy round of 4.2 appended,
`N = 94`) and at two smaller ones: every mask's messages pass
the round checks and the rank is `N` at every challenge vector tried, including all-0 and all-1,
for `lam` random, `lam` from random `mu`, `lam` from the embeddings at a random `s`, and `lam = 0`
(where `G` is identically 0); a reduced chain (degree 6, one eq round, one plain round) at all
49,152 combinations of four `lam`, three `tau` and every challenge vector of `GF(16)`. Controls:
45 coefficients for the product round (rank 59 against 60); `lam = 0` in a second round (round
checks fail).

Soundness: `+1/q` per layer for `rho`; the S5 round keeps its `46/q`; the dummy round adds `2/q`;
`Gtilde` is bound by the gadget.

---

## 5. Reference test M-2: the radix-4 batched bus GKR (S1)

### 5.1 The layer

(S: `verifier/src/bus.rs::verify_gkr_grand_products`.) Three trees (push, pull, count) share
every layer. A step of two levels: combiner `gamma`; claim `sum_t gamma^t v_t(z)`; sumcheck with
the eq factor of `z` removed from each message (five coefficients less one); the prover sends the
four children of each tree at the point; the verifier checks
`claim = sum_t gamma^t prod_b child_t[b]`, draws `y` in `F^2` and sets `v_t(y, x)` to the
multilinear of the four children at `y`. An odd depth starts with one step of one level (two
children: the lemma document's own case).

### 5.2 Construction

    vhat_t(w, b, x) = v_t(b, x) + m(w) c_t(b),    c_t(b) = k_00 + k_10 b_1 + k_01 b_2 + k_11 b_1 b_2 ,

four blinders per tree and layer in column `A`, `w` the dummy variable. The layer's masked
sumcheck runs on `sum_t gamma^t prod_b vhat_t(w, b, x)` with Libra's mask inside the eq factor
(Corollary B). The prover sends the blinded children `Ahat_t[b] = vhat_t(r_w, b, r)`; the verifier
does what it does today with them. With `Z = m(r_w)`:

    v_t(y, r) = (multilinear of Ahat_t at y) + Z c_t(y) ,

and the next layer, with its combiner `gamma'`, has the head
`rho sum_t gamma'^t (multilinear of Ahat_t at y) + Gtilde`,

    Gtilde = G' + rho Z sum_t gamma'^t c_t(y_1, y_2) ,

a linear functional of column `A`, entered in the gadget's list. Forms of the dummy variable: A5
(`m = w(1 + w)` under `eq(z_w, w)`; degree 8 in `w` for the reduced message) or, by Proposition D,
A5-T (`m = w`, `lam_w(p) = p(0)`, degree 4, dummy round last: the `x` rounds are the present
prover's and the dummy round's polynomial is `sum_t gamma^t prod_b (child_t[b] + Y c_t(b))`). The
first layer has no `x` variable: the dummy round alone.

**Top.** The roots are `R` (twice) and the masked count root (section 1); the first head is
`rho (R + gamma R + gamma^2 R_c') + G`.

**Bottom.** The last layer's children are values of the stacked leaf polynomials, not column
evaluations (the implementers' M-2 says A8; this corrects it). They are blinded like every other
layer's, with four blinders per tree. The leaf values at `zeta` then decompose (S:
`verify_bus_balance`): (a) four framework column evaluations (`mem_0`, `mem_1`, the memory's and
the bytecode's final counts) sent in clear today: Proposition L, one blinder each, relation in the
opening; (b) the tables' share, handed to the table sumcheck as its target
`dot(form_powers, totals)`. Every hidden correction is linear in column `A`: the last layer's
`Z c_t(y)`, the four framework blinders through the public fingerprint weights, the count mask
leaf of section 1. So the table sumcheck takes `Gtilde` in place of `G`:

    Gtilde_S4 = G' + rho sum_t form_powers[t] ( Z c_t(y) + sel_t . (weights . framework blinders) + [t = count] eq(zeta, p) e ) .

### 5.3 Statement

**Proposition M2 (P; C).** Under H3 and with every multiplier `Z != 0`, the view of the batched
radix-4 chain (roots, every `Gtilde`, all round messages, all blinded children) is distributed as
the simulator's: children uniform, each layer's messages by the sumcheck simulator with claimed
value `sum_t gamma^t` (previous layer's blinded value at `y`) and final value
`sum_t gamma^t prod_b Ahat_t[b]`.

*Proof.* Lemma 4's proof with two changes. (i) The blinded children of one tree are
`(v_t(b, r))_b + Z M k_t`, `M` the `4 x 4` matrix that evaluates a multilinear in two variables on
the square, which is invertible; so the twelve children of a layer are a bijective image of the
twelve blinders when `Z != 0`. (ii) The summand is the `gamma`-combination of the three products;
conditioned on the blinders it is a fixed polynomial of the layer's degrees and Corollary B
applies; the shift `Gtilde - G'` is the `gamma'`-combination of the three corrections, which is
what turns the head `rho sum_t gamma'^t v_t(y, r) + G'` into the stated one. ∎

Two blinders per tree (the binary form applied to a radix-4 layer) are not enough: the children
then move in a plane of dimension 2 of `F^4` that depends on the witness (C).

C (`zk-lemma/test_gkr4.py`). Part 1, `GF(16)`, three trees of 16 leaves, two reductions, both
forms: every verifier check passes from the stated heads and ends on the stated final value in
36 of 36 honest runs with random blinders and masks; the mask-to-view rank equals `dim V_r` (9 and
17 for A5, 5 and 13 for A5-T) at 12 of 12 challenge vectors; four blinders map onto all `16^4`
children tuples exactly when `Z != 0` (image of size 1 at `r_w in {0, 1}` for A5, at `r_w = 0` for
A5-T). Controls: `Gtilde` without the combiner's powers fails the round check (35 and 31 of 36);
two blinders give an image of 256 of 65,536. Part 2, `GF(4)`, one tree, both forms: the exact
joint law of the two-reduction chain `(G_1, s_1, A_1, Gtilde_2, s_2, A_0)` over all `256 x 256`
blinder pairs and all masks equals the law for a second witness with the same root, and equals the
simulator's law built without the witness, in 4 of 4 challenge sets each. Controls: two blinders
(different in 4 of 4); blinders off (4 of 4). In this test the dummy variable is the first
variable; Theorem 1 holds for every order, and the last position is tested in
`test_dummy_terminal.py`.

Soundness per layer: `1/q` for `rho`; the dummy round `8/q` (A5; `9/q` with the eq line
counted) or `4/q` (A5-T); the layer's other rounds unchanged; every `Gtilde` in the gadget's list (an omitted one is
unsound: `zk-wi-soundness.md` 6.3). The gadget's batching term `(m - 1)/q` grows with the number
`m` of linear claims: one per masked sumcheck and one per `Gtilde`.

---

## 6. G-2: are Z-C1 to Z-C3 still needed?

No. Argument (P, from the pad ledger).

Z-C1 and Z-C2 make every count a product `s_a g^j` with a free uniform seed, so that count cells
are uniform and evaluations of count columns are uniform functionals of them. That serves the
method of the implementers' layer 2, where a revealed value is padded by the uniformity of the
witness cells it reads. The composed simulator of the composition document uses no such pad: in
Theorem C every view block has a pad that is not a witness cell, and the witness may have any
distribution. Where the read counts reach the view:

| Where counts appear | Block and pad | Item |
|---|---|---|
| evaluations of `cnt*` columns, `DEREF` `ptr` and `cnt_target`, in the table sumcheck's terminal (the 22 + 3 of their section 10.2) | blinded evaluations, one cell each | A8 / A8-T |
| the memory's and the bytecode's final counts at the bus point | Proposition L, one blinder each | A22 |
| the count root | the mask leaf | A18 |
| the shared root `R` (counts are coordinates of the pushed and pulled tuples) | section 9.2 | A19 |
| the bus GKR's layer claims | layer blinders | A24 |
| sumcheck messages of S1 and S4 | masks | A4 |
| opened rows of oracle 0 | encoding randomness (Lemma E), whatever the cells hold | A9 |

A cell `g^c` with a small exponent, a pointer `g^address`: neither needs entropy, since no block
relies on it. The leftover-hash question of their section 10.2 (640 bits of pointer entropy) does
not arise. Z-C1 would also change the memory argument and need its own soundness proof (a seeded
count changes the invariant-multiset lemma's setting); dropping it leaves the specification's
theorem untouched. Z-C3 (moving the range checks' cells) only reduced the number of unmasked
claims and has no role once each claim has a cell.

Condition: A18 must be built, because Z-C2 was also the planned mask of `R_c`. With A8, A18, A19
and A22, drop Z-C1, Z-C2 and Z-C3.

---

## 7. G-5: the end-to-end test on real proofs

Setting: two witnesses `w_0, w_1` of **one** public input, `n` proofs of each with fresh prover
randomness, all under one tape of programmed challenges. The view of a part is a vector of `d`
words of `K` (an element of `F` is four words).

**Statistic 1: ranks over `K` (exact for every block whose pad enters linearly).** With `v^a_i`
the `i`-th view of witness `a`:

    D_a = { v^a_i - v^a_1 : i = 2..n },    x = v^1_1 - v^0_1 ,
    (r_0, r_1, r_01) = ( rank D_0, rank D_1, rank [D_0 | D_1 | x] )    over K .

Pass if and only if `r_0 = r_1 = r_01 = d_sim`, the number of free words the simulator samples for
that part. Reading: under a fixed tape the view is `a_0 + A w + B z` (Lemma L), and a map that is
`F`-linear in `F`-valued randomness or `K`-linear in `K`-valued randomness is `K`-linear on words,
so the rank over `K` is exact for both kinds (the implementers' wallet run took ranks over `F`,
which over-counts the image of `K`-valued randomness; use `K`). `r_01 > r_0` proves a leak.
`r_0 < d_sim` means an unpadded direction or too few proofs. `r_0 = r_1 = r_01 = d_sim` gives
`A (w_1 - w_0) in Im B` and `Im B` of the simulator's dimension: identical laws at that tape for
that pair.

How many proofs (P). The `n - 1` differences of one witness are independent and uniform in
`Im B`. They fail to span a space of dimension `d` with probability at most
`(number of hyperplanes) |K|^-(n-1) < |K|^(d - n + 1) / (|K| - 1)`, about `2^(-64 (n - d))`. So
`n = d + 2` proofs per witness give a false "under-rank" with probability below `2^-128`, and a
leak that exists is never missed (the direction `x` is deterministic). For the reported view
sizes: 54 proofs per witness at 52 words, 250 at 248 words; 250 per witness cover every part up to
248 words. A part of `d` words needs `n > d + 1` to mean anything: this is why their bus (542
scalars) and Keccak (1,238 scalars) rows read "not decided" at 200 proofs; once masked, those
parts need `4 x 542 + 2` and `4 x 1,238 + 2` proofs per witness, or the test is run per block.

Conditions that make the statistic meaningful: (a) equal public inputs, else `x` carries the
public difference; (b) a positive control on the same pair: with the masks off, `r_01 > r_0` in
every part, else the pair does not differ where the test looks; (c) values the ledger lists as
determined (`beta`, `B(z)`, mask final values) are removed from the view and checked by
recomputing them from the rest; (d) several tapes, including one with a dummy-variable challenge
in the excluded set, where the test must fail as predicted (negative control).

**Statistic 2: translation test for multiplicative pads** (the count root, and the shared root if
section 9.2's leaf is built). These are not affine in the randomness. Run both witnesses with the
**same** prover randomness under one tape, for two or more seeds: the ratio of the published
values must be the same for every seed **of the proof system at one advice seed** and lie in the
group the pad is uniform on (`F*` trivially for an `F`-valued leaf; `ratio^(2^64 - 1) = 1` for a
`K`-word leaf). Two seeds suffice; the conclusion is exact (a translation of the pad's group
preserves its uniform law). The same paired run checks the affine blocks' difference is constant
across seeds.

Correction (2026-11-19, from the run on real proofs, `yugen-proof-a-zk/docs/zero-knowledge.md`
18.2; P for the argument, C for the observation). The text above first said the ratio is
`R_c(w_1) / R_c(w_0)`, one constant. It is not: the trees' leaves include the advice, the
masking prologue's uniform memory cells and pointers (layer 2), so the product without the mask
leaf is `R_c(w, a)`, a function of the witness **and the advice randomness `a`**, and the ratio
`R_c(w_1, a) / R_c(w_0, a)` moves with `a` (observed: two advice seeds, two different ratios for
both roots; for each advice seed one ratio over three proof seeds). This is not a leak. The root
is `e R_c(w, a)` with `e` uniform on `F*` and drawn from the proof system's seed, apart from `a`
(the mask column's stream; the advice comes from the prologue's seeds, `src/masking.rs`
`Seeds`). For each fixed `a` with `R_c(w, a) != 0`, `e R_c(w, a)` is uniform on `F*` (a
translation of `F*`); so the root's law is uniform on `F*` for every `a` and every witness, and
the mixture over `a` is the same uniform law. What the statistic must check is therefore the
constancy **at fixed advice** (it then shows that the multiplicative pad is the only randomness
in the root), not across advice seeds. Two conditions carry the argument and are now stated:
(i) `e` is independent of the advice: distinct streams of independent seeds (a wallet that
derives both from one seed must use distinct labels, as `Seeds::from_seed` does); (ii) the
joint law of the root with the rest of the view: the bus GKR's values also carry `e` times
partial products of `a` and `w`, so they are not affine in the randomness; the test for them is
the conditional one, with every randomness that enters other than additively held fixed: `a`,
`e`, `e_R`, layer 2's uniform memory cells (drawn from the proof system's seed, leaves of the
trees) and the blinders that enter products (the table sumcheck's cells and the output lanes'
cells, the bus layers' and the Keccak layers' blinders). Holding `a`, `e` and `e_R` alone is not
enough (C: 1,776 of the 1,788 words stay non-affine). With all of them held the view is affine in
what varies, the coefficients do not depend on the held values (checked at three values and both
witnesses), and the rank statistic is exact on the varying words; the held words are each a value
plus its own blinder, or `e` times a product (`zero-knowledge.md` 18.12.2, with what this does not
establish). `R_c(w, a) = 0` happens only when a
leaf's fingerprint is zero (probability at most the leaf count over `q`); the verifier refuses a
zero root (A19), so it is a completeness error, not a leak.

**Statistic 3: sampling tests are regression tests only.** No two-sample statistic on real proofs
supports a claim near the target distance `2^-100`. A two-sample chi-square on a feature with `B`
bins detects a statistical distance `delta` at `z` standard deviations with about
`n = z sqrt(B / 2) / delta^2` proofs per witness (P, normal approximation): 905 proofs for
`delta = 0.25` on one byte (`B = 256`, `z = 5`), 22,600 for `delta = 0.05`. Such a test finds a
forgotten pad; it measures nothing below `delta` of a few percent. The claim of zero knowledge
rests on statistics 1 and 2, on the witness-free simulator through the code (A16), and on the
proofs.

Not testable on real proofs at all: Merkle digests and salts (a random-oracle statement); the
shared root `R` as the implementers mask it today (section 9.2).

Needed from outside this repository: a pair of vectors with equal public inputs (two Falcon
signatures of one digest under one key) from `yugen-falcon`.

---

## 8. The column evaluations that separate two witnesses (64 / 64 / 65)

The implementers' wallet run: with the masked table sumcheck, the 153 column evaluations have rank
64 within each witness and 65 across. From the documents:

1. **What closes it is blinder cells, checklist item A8** (composition document, section 3,
   Theorem B; ledger row 3). Each of the 153 evaluations becomes `c_i(r) + Z b_i` with its own
   uniform cell: for `Z != 0` the 153 values are a bijective image of the cells, hence uniform on
   `F^153` and independent, for every witness. The rank becomes `153 x 4` words within each
   witness and stays there across. On S4 the form to build is A8-T (section 3).
2. **Blinder cells are not part of W-I.** W-I is checklist A9 to A12 (with A1, A2): it hides what
   the opening itself sends and opens. With W-I and without A8 the 153 evaluations are still sent
   in clear before the opening and still separate the witnesses. With A8 and without W-I the
   evaluation block is uniform (the implementers' rank test, which does not read the opening,
   would show it), and the proof still leaks through the non-hiding opening's messages and rows,
   which are functions of the columns and of the cells.
3. **What A8 needs from W-I**: the opening proves the relation `c_i(r) + Z b_i = chat_i` with a
   public right-hand side and reveals nothing else (Theorem W-A), and the cells' other appearance,
   as entries of oracle 0, is covered by the encoding randomness (Lemma E).
4. **Nothing else is needed for this block**, given: one cell per (column, point), never reused
   (the columns of S4 are each read at one point; a column read again elsewhere, such as the
   Keccak table's lanes inside `q_keccak`, has another cell there); the mask of S4 extended to the
   dummy round (section 3.2, item 3); the cells in oracle 0 before every challenge; the excluded
   event `Z = 0` counted (`1/q` for A8-T, `2/q` for A8). The 25 output lanes of the `KECCAK` table
   are among the 153 and are virtual: see 9.1 item 4.

C: `test_dummy_terminal.py`, "blinder off" rows (laws differ in every case) against the blinded
rows (identical in every case).

---

## 9. Found while reading the pinned verifier

### 9.1 Values on the wire that no item names

Each is closed by Proposition L or D; none needs new mathematics.

| # | Value (S: file) | Dependence | Treatment |
|---|---|---|---|
| 1 | `committed` (`keccak.rs::verify_keccak`), the claimed combination of the committed middle states, sent when a batch has more than one segment (two at depth 12) | linear functional of `q_keccak` | It heads two sumchecks linearly (the first layer's claim `committed + last`, and the output opening). Proposition L: one blinder in `A`, two `Gtilde` entries |
| 2 | `word`, the output opening's terminal value (`keccak.rs`) | `K`-linear evaluation of `q_keccak` | The terminal `weights[0] word = value` is linear: Proposition L, the correction joins that sumcheck's final-value claim; relation in the opening |
| 3 | `mem_0`, `mem_1`, the memory's and the bytecode's final counts at `zeta` (`bus.rs`) | column evaluations | They enter `totals` linearly: Proposition L (section 5.2, bottom) |
| 4 | the 25 output lanes of the `KECCAK` table among S4's evaluations | evaluations of virtual columns (no placement) | They enter S4's terminal non-linearly: cells and the dummy round like every column of S4, with the cells in column `A`. They have no relation in the opening; instead the Keccak reduction's first claim `last = eq . <lanes, output>` is linear in them, so its `Gtilde` takes `rho Z eq . <lanes, cells>`. Soundness: the revealed values and the committed cells are fixed before `lanes` is drawn, as the revealed outputs are today |

### 9.2 M-3: the shared root `R`

The implementers match `R` to Lemma 5 form 2: every untouched memory cell contributes the factor
`beta + <weights, (sep, g^a, 1, v_0, v_1)>` to both trees, with `v_0, v_1` uniform `K` words,
68,432 such factors. This is not Lemma 5 as stated: one factor is uniform on an affine plane of
dimension 2 over `K` inside `F` (`2^128` of `2^256` values), not on `F*`, and the product of many
such factors is not exactly uniform on `F*`. It is statistically close under a character-sum
bound (M: Katz's bound `|sum_{t in K} chi(t + theta)| <= (n - 1) sqrt|K|` for `theta` generating
`F` over `K`, `n = 4`, gives a bias of about `2^-30` per factor and `2^(-30 N)` for `N` factors;
not verified, and the generating condition was not checked for the weights in use). The lemma
document claims nothing for it. (U) as built.

Exact replacement, the construction of section 1 on both trees: one padding leaf of the push tree
and one of the pull tree hold the same element `e_R` of column `A`, uniform nonzero; the verifier
adds the check `R != 0`. Then `R' = R e_R` is uniform on `F*` exactly (Proposition G1), the
corrections enter `Gtilde_S4` as in 5.2, and soundness is unchanged: `e_R` is a constant fixed
before the bus challenges, `R' != 0` forces `e_R != 0`, and `e_R Pi_P = e_R Pi_Q` as polynomials
in the fingerprint challenges if and only if `Pi_P = Pi_Q`. The new check costs completeness at
most `2^mu / q` (a leaf `beta + fingerprint` equal to 0). If the push side has no padding leaf (its
blocks fill `2^mu` exactly), the trees gain one level. With this leaf the uniform memory cells of
layer 2 serve no block.

---

## 10. Checklist entries

Appended to `zk-implementation-checklist.md`, system A. Format as there.

| # | Build | Random | Order | Reference |
|---|---|---|---|---|
| A18 | **Count-root mask leaf.** One padding leaf of the count tree, at a fixed public position `p`, holds an element `e` of column `A`, nonzero (redraw on 0). The prover publishes the root of that tree. The verifier's check `!= 0` is unchanged. The verifier adds `form_powers[count] eq(zeta, p)` to the table sumcheck's target; `rho form_powers[count] eq(zeta, p) e` is a term of that sumcheck's `Gtilde`. `e` is never sent | 1 | `e` in oracle 0 before the bus challenges (S); position fixed by the layout (S) | L `test_count_root.py` |
| A19 | **Shared-root mask leaf.** One padding leaf of the push tree and one of the pull tree hold the same element `e_R` of column `A`, nonzero. The verifier checks `R != 0`. Corrections in `Gtilde` of the table sumcheck as A18, with `form_powers[push]`, `form_powers[pull]` | 1 | as A18 | L `test_count_root.py` part A (law); `zk-system-a-gaps.md` 9.2 |
| A20 | **Slice blinder block.** 256 uniform `K` cells `B_j` in oracle 0; `b_i = sum_j omega_j bit_i(B_j)` with `omega` the fixed subset-product basis of `F` over `F_2`. The Keccak input opening ends with a dummy round (A21, degree 1); the prover sends `shat_i = s_i + r_y b_i`; the ring switch runs on `shat` and its claim carries the weights `Phi(r_y omega_j)` on the cells `B_j` | 256 `K` cells | block in oracle 0 before every challenge (S, Z); `shat` before the ring switch's challenges (S) | L `test_slices.py` |
| A21 | **Dummy round, form A8-T** (allowed wherever A8 or A5 asks for a dummy variable). The round is last; its check is `p(0) = claim` (`eq_factor = Some(0)`); multiplier `y`: `chat = c(r) + r_y b`; its polynomial is the terminal evaluated at `evaluations + Y cells`, degree `deg C`, sent without its constant; the mask gains `deg C` coefficients (`g_y`, whose constant is the staircase's `c`). On S4: `deg C = 2`. **A dummy round is never checked as `p(0) + p(1) = claim`.** With `m = y(1 + y)` the degree is `2 deg C` and the functional `(1 + tau) p(0) + tau p(1)` | `deg C` mask coefficients; cells as A8 | cells before the component's challenges (S); the round's message before `r_y` (S) | L `test_dummy_terminal.py`; D `test_terminal_dummy_sound.py` |
| A22 | **Linear hand-offs** (no dummy variable). A revealed value that enters only a later head or a linear terminal is sent as `v + b`, `b` one element of column `A`; the correction is a term of that `Gtilde` or final-value claim; for committed data the opening's relation has `v + b = vhat`. Instances: `mem_0`, `mem_1` and the two final counts at `zeta`; `committed`; the output `word`. The 25 virtual output lanes of `KECCAK` take cells in column `A` under S4's dummy round and a term in the first Keccak layer's `Gtilde` | 1 per value | blinders in oracle 0 (S, Z); every correction in the gadget's list (S) | L `test_handoff.py` |
| A23 | **Keccak layer chain.** One mask per layer over S5 (46 coefficients), S6 (2 a round), S7 (3 a round) and the dummy round (2): `Gtilde`, `rho`, messages `rho` honest + mask; the public `iota` term is multiplied by `rho`. Three blinders per layer on `t_0, t_1, t_2`; next `Gtilde = G' + rho r_y (c_0 + beta c_1 + beta^2 c_2)` | `1 + 46 + 2 n_6 + 3 n_7 + 2` and 3, per layer | as A5 | K `test_product_round.py`; L `test_gkr4.py` (the hand-off), `test_dummy_terminal.py` |
| A24 | **Bus GKR, radix 4, three trees.** Four blinders per tree and layer (two for a one-level step); Libra's mask inside the eq factor; dummy round by A21 (degree 4; 2 for a one-level step); blinded children sent; `Gtilde = G' + rho Z sum_t gamma^t c_t(y)` with the next layer's combiner. The last layer's children are blinded the same way; the table sumcheck's `Gtilde` collects the last layer's corrections, A22's framework blinders and A18, A19 | 12 per two-level layer, plus the layer's mask | as A5 | L `test_gkr4.py` |
| A25 | **End-to-end statistic.** Two witnesses of one public input, one tape: ranks over `K` of the within-witness differences and with the cross difference, `d + 2` proofs per witness for a part of `d` words (250 for 248 words); determined values recomputed; masks-off positive control; excluded-challenge negative control; paired-seed ratio test for A18, A19 | 0 | none | `zk-system-a-gaps.md` section 7 |

Amendments to existing rows: A5's "bottom-layer claims are column evaluations: A8" does not
describe system A's bus (A24, A22). A6 is replaced in system A by A18 and A19 (the bus publishes
two roots, no per-table terminal and no denominator). A8 stands; A21 is its cheaper equivalent.

## 11. Soundness terms added, all in units of `1/q`

| Item | Term | Note |
|---|---|---|
| A18, A19 | 0 | A19 adds completeness loss `2^mu / q` for the check `R != 0` |
| A20 | 1 | dummy round of degree 1; ring switch unchanged |
| A21 on S4 | 2 (A8-T) or 4 (A8) | plus the mask's 1 already in A4; degrees of the reduced messages (the pinned grinding rule counts an eq line as one more) |
| A22 | 0 | bound by the gadget |
| A23 | 1 + 2 per layer | `rho`; the dummy round |
| A24 | 1 + 4 per layer (A5-T), 1 + 8 (A5) | |
| W-I base case (section 12) | `2 n_last` | the relation proved by the unmasked tail sumcheck |
| gadget | `(m - 1) + 1 + l` | `m` linear claims: one per masked sumcheck and one per `Gtilde` |

All are far below the opening's terms at `q = 2^256`; `rounds(c, "A")` should list them so that
A17 stays a statement about the implemented protocol.

## 12. The W-I opening as built: the base-case relation by a sumcheck, and the narrow-alignment control

(Added on the lead's request. S: `yugen-proof-a-zk/docs/zero-knowledge.md` section 15;
`verifier/src/wi.rs::verify_wi`.)

### 12.1 The deviation from A12

A12 has the verifier compute `<P*, W'> = mu + c T` itself. The implementation sends `mu`, draws
`c`, receives `P*` (`lf` scalars), draws the positions, checks the rows against `P*` and the mask
column, and then runs the framework's plain sumcheck (degree 2, `n_last` rounds, no mask) on the
claim `mu + c T`; at the end point `tail` the verifier computes both factors itself:
`weight(tail)` from the challenges and the public claim weights, and the multilinear extension at
`tail` of `P*` padded with zeros to `2^n_last`.

**(a) Soundness: confirmed, with the term `2 n_last / q`.** (P) The sumcheck is run on the product
of two multilinear polynomials that are both fixed before its first challenge: the extension of
the zero-padded `P*` (on the wire before the positions), and the weight, a function of challenges
all drawn earlier (`rho_i`, the fold challenges, `lambda_i`, the positions of the levels below the
last) and of the public stacked claim. Its sum over the cube is `<P*, W'>` exactly: on the indices
at or above `lf` the padded `P*` is 0, whatever the weight's extension is there. The verifier
evaluates both factors at `tail` itself, so no claim is handed on. If `<P*, W'> != mu + c T` the
verifier accepts with probability at most `2 n_last / q` (two per round). The base-case lemma of
`zk-wi-soundness.md` (4.5) uses the relation only as a predicate on values fixed before the last
positions, and `P*` is still bound before them, so its argument is unchanged and the term is added
once. Two conditions, both read in the code and not tested here: the function the verifier
evaluates as `weight` has degree at most 1 in every coordinate of `tail` (each of `Base`, `Mask`
and `Queries` is a product over disjoint coordinates of factors linear in one coordinate, given
that `evaluate_basis` is multilinear), and it agrees with `W'` on the cube indices below `lf`
(their unit test "the truncated row weight is the sum below the bound" is the check of this for
the query weights). The round count for the calculator: `rounds(c, "A")` gets `n_last` rounds of
degree 2 in place of the direct check.

**(b) Zero knowledge: confirmed; the sumcheck needs no mask.** (P) Every message of the tail
sumcheck is a function of `P*`, the weight and the tail challenges. `P*` is sent in full; it is
`gt + c p'` with `gt` uniform on all `lf = lrow + kappa` coefficients of the folded lane, so the
whole of `P*` is padded (ledger row 9), and the zero padding up to `2^n_last` is public. The
weight is public: the verifier recomputes it. So the messages are determined values of the
ledger, as `mu` is, and the simulator computes them from its sampled `P*` by running the same
sumcheck prover. The implementers' rank test agrees (the view has the accepting dimension with the
tail sumcheck counted as determined). Two things to keep true: the prover computes the tail
messages from `P*` as sent (not from a longer internal vector: anything beyond `lf` must be zero),
and `gt` covers every coefficient that `P*` carries (the control "no base-case mask" is the test).
Checklist A4 does not apply to this sumcheck, and instance S12 needs no mask.

### 12.2 The narrow-alignment control

The reference control (`test_whir_a.py`: offset aligned to `2^ceil(log2 t)` in place of
`2^ceil(log2(t + kappa))`, honest view rejected in 30 of 30 runs) is a **completeness failure of
that layout at particular shapes** (finding F-7). It is not a check the verifier makes or can
make: the verifier does not see where the uniform coefficients sit, soundness does not depend on
where a prover puts them, and hiding needs only the alignment to `t` (commitment document 6.2a).
So "accepted at their shapes" is the expected outcome wherever the two layouts coincide or no
coefficient is moved, and the verifier should not be changed.

When it fails (P; C; corrected 2026-11-19). Multiplication by `X` in the novel polynomial basis
(the prover's `pcs/src/xmul.rs`) sends the coefficient at slot `c` to slot `c + 1` and to the
slots `c + 1 - 2^j`, `j = 0 .. r - 1`, where `r` is the number of trailing one bits of `c`; the
lowest is `c + 1 - 2^(r - 1)`. (This section first said "the slot `c` with its trailing one bits
cleared", `c + 1 - 2^r`: one step too low. The real prover's control, run at 17 shapes in
`yugen-proof-a-zk` (`tests/zk_wi.rs`), was refused at 8 and accepted at 9; the old rule predicted
6 of the 9 accepted shapes to fail.) The relation fails when the random content reaches, during
the level's `kappa` fold rounds, a slot below the end of the aux slots (a slot the relation
weighs). With `a = ceil(log2 t)` and the narrow offset `o` a multiple of `2^a`, the content
`o .. o + t - 1` reaches the slot `o + 2^a - 1` (once `t + kappa > 2^a`, or at once when
`t = 2^a`); it has `a + s` trailing ones, `s` the trailing ones of `o / 2^a`, and its lowest image
is `o + 2^a - 2^(a + s - 1)`, below `o` exactly when `s >= 2`: the narrow layout fails when
`o / 2^a` ends in the bits `11`, not, as first written, whenever it is odd. C
(`zk-commit/test_narrow_align.py`): (1) the rule equals the support of this model's own
multiplication by `X` at every slot of a level (124 slots); (2) the eight model shapes, 12 honest
runs each, against the model's verifier: rejected 12 of 12 at the two shapes where a coefficient
reaches a weighed slot (folds 2/1 with `Q = 3/2`; fold 2 with `Q = 3`), accepted 12 of 12 at the
six where none does (the old rule agreed at these eight); (3) the real prover's 17 shapes, as data
(levels and outcome): the prediction is the outcome at all 17, and the old rule is wrong at
exactly 6.

What the implementation's test should assert instead: (i) a unit test that `wi::layout` places
every level's uniform coefficients at a multiple of `2^ceil(log2(t + kappa))`; (ii) the narrow
layout as a completeness control at a shape where the prediction above says it fails, expected
result "the honest proof is refused"; a shape where it is accepted proves nothing either way. At
the design-basis parameters the level with `Q = 128`, fold 3 is such a shape whenever its narrow
offset divided by 128 ends in the bits `11` (`t + kappa = 131` crosses the block; recomputed with
the corrected rule: the first version said "an odd multiple of 128", which includes offsets where
the honest proof is accepted); the levels with `Q = 184`, fold 5 and `Q = 125`, fold 3 have the
same offset under both alignments.

## 13. What was checked, and what was not

Run for this document, all passing (standard library Python, from each directory):
`zk-lemma/test_count_root.py`, `test_dummy_terminal.py`, `test_gkr4.py`, `test_slices.py`,
`test_handoff.py`;
`zk-commit/test_product_round.py`, `test_narrow_align.py`; `zk-sound/test_terminal_dummy_sound.py`. Results in each
directory's `results/`.

Not done:

- No test runs through system A's code; every test is a model. The link is A16 and each row's
  "Reference".
- The ring switch's error term for its structured coefficients was not re-derived (section 2.4).
- The statistical claim for M-3 as built rests on a bound cited from memory (9.2).
- Proposition L is tested for a hand-off into a head (`test_handoff.py`); the linear-terminal case
  is the same identity on the final-value claim and has no separate test.
- The one-level GKR step (odd depth) and chains deeper than two reductions were not enumerated.
- Of the six tables' constraint functions only `Form`'s degree bound and the round's coefficient
  count were read; `deg C = 2` follows from the round degree 3.
- S9's per-instance rounds and S10 were not re-examined; S11 is A9, A10; S12 is section 12.
- Section 12: the degree and the agreement of the verifier's `weight` function were read in the
  code, not tested; the implementers' shapes for the narrow-alignment control were not reproduced.

Claims from memory in this document: Katz's character-sum bound (9.2). Everything else is (P),
(C) or (S) as marked.
