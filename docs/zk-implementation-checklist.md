# Zero-knowledge implementation checklists

Part of Yugen. Two checklists, one per leaf proof system. Each stands alone: a team
builds from its own list and does not need the other. Decisions behind them (lead architect,
2026-11-19): system A's hiding opening is **W-I**, system B's is **W-M**; the parameter set is
category 1 for a whole proof tree of about 1,700 proofs.

How to read an item. **Build**: what the prover and verifier do. **Random**: uniform values the
prover draws for it, per proof, from a cryptographic generator seeded with fresh entropy; a value is
used for one purpose only. **Order**: the transcript constraint; "X before Y" means X is absorbed
into the Fiat-Shamir state before challenge Y is derived. Violating an order row marked (S) breaks
soundness, (Z) breaks zero knowledge. **Reference**: the test in `zk-lemma/` (L), `zk-commit/` (K)
or `zk-sound/` (D) that states the property in a toy model; the implementation must reproduce it
through its own prover and verifier at toy size (same statement, same negative controls), and the
release is blocked while any item lacks its reproduction. Proofs: `zk-masked-sumcheck.md`,
`zk-hiding-commitment.md`, `zk-composition.md`, `zk-wi-soundness.md`.

Common notation: `F` the 256-bit challenge field, `K = GF(2^64)` the committed alphabet;
`Z = r_y (1 + r_y)` for a dummy-variable challenge `r_y`; a *lane* is one coefficient vector of an
interleaved oracle, a *row* the lanes' values at one domain point (one Merkle leaf).

---

Provenance of the items (citation audit of 2026-11-19; full entries in `../REFERENCES.md`).
"Libra's mask" (A4, A24, B4): Xie, Zhang, Zhang, Papamanthou, Song, ePrint 2019/317, Section 4.1,
Construction 1; used here only inside an `eq` factor, where it is perfect in characteristic 2
(Corollary B, Original as far as checked); for a plain sum it fails in characteristic 2
(Published: Chiesa, Fenzi, Weissenberg, ePrint 2026/391, revision of 2026-11-16, Section 2.5).
Staircase mask (A4, B4): Original as far as checked; the published alternative is the mask of
ePrint 2026/391, Definition 6.1 and Lemma 6.2. Salted leaves: Ben-Sasson, Chiesa, Spooner, ePrint
2016/116, Section 3.2. W-I: adapts ePrint 2026/391, Sections 6, 7, 9 and 11 (its base case is
Construction 7.2). W-M: adapts Diamond, ePrint 2025/1015, Construction 4.1. Blinder cells, dummy
variables (A8, A8-T), the count-root, bit-slice and bus items: Original as far as checked.
Fiat-Shamir: ePrint 2016/116, Theorem 7.1 and Lemma 7.5 (honest-verifier zero knowledge of a
public-coin IOP, salted trees, explicitly-programmable random oracle).

## System A (leanVM): staircase masks, GKR, bus, blinder cells, W-I

Parameters (estimates, `soundness/output/wi-tables.txt`, shared-budget tree target): rate 1/4,
folds 5/3/3/3, queries 184/128/125/125, folded lane lengths 524733 / 65923 / 8448 / 1280, leaf
about 482 KiB.

| # | Build | Random | Order | Reference |
|---|---|---|---|---|
| A1 | **Coset domains.** Every committed oracle is evaluated on `beta_i + S_i` with `beta_i` outside `S_i`; query points, row folds and evaluation weights use the shifted points. | 0 | none | K `test_code.py` (linear domain leaks exactly on `U_top`); D `test_proximity.py` part A |
| A2 | **Salted leaves.** Leaf digest = hash(32-byte salt, row); the salt is opened with the row. Every tree of the leaf proof. | 32 bytes per leaf | salts are independent of all other randomness (Z) | hash-level; `zk-hiding-commitment.md` Lemma M |
| A3 | **Oracle 0 content**, beside the trace: blinder column (A8), mask column `A` with at least one pad element and gadget column `B` (A7), bus payloads (A6), and the level-0 lane layout of A9. | as listed per item | oracle 0's root before every challenge (S, Z) | D `test_blinder_sound.py` and `test_mask_batch.py` controls |
| A4 | **Masked sumcheck** (zerocheck and every other sumcheck outside the opening): prover sends `G = Lam(g)`; verifier sends `rho`; sumcheck on `rho f + g`; the mask `g` is a staircase mask (plain sum) or Libra's mask inside the eq factor (reduced messages); its coefficients are in column `A`. The verifier computes the mask's final value from the last message and the revealed evaluations and adds the linear claim on `A` to the gadget's list. | `1 + sum_j d_j` per sumcheck (`d_j` the round degrees) | mask in oracle 0; `G` before `rho` (S); one fresh mask per sumcheck (Z) | L `test_exact.py`, `test_rank.py`, `test_leak.py`; D `test_mask_batch.py` (order control) |
| A5 | **GKR chain (Keccak-f).** Each layer gets a dummy variable `y` and two blinders per claimed polynomial: `vhat(y, x, b) = v(x, b) + y (1 + y)(c_0 + c_1 b)`; the prover sends the blinded claims; the next layer's head is `rho Ahat + Gtilde` with `Gtilde` sent in place of `G`. **Every `Gtilde` is entered in the gadget's claim list** as the linear functional `G' + rho Z (c_0 + alpha c_1)` of column `A`. Bottom-layer claims are column evaluations: A8. | 2 per layer polynomial, in column `A`, plus the layer sumcheck's mask (A4) | blinders in oracle 0 (S, Z); `Gtilde` is sent after `rho` and is bound only by the gadget (S) | L `test_gkr.py`; `zk-wi-soundness.md` 6.3 |
| A6 | **Bus terminals.** One uniform mask payload per neighbouring table pair, one self-cancelling pair per table that publishes a denominator, inside the tables' own rows. | `T - 1` (+ `T`) payloads | payloads in oracle 0, before the bus challenges (S, Z) | L `test_bus.py` |
| A7 | **Linear-claim gadget.** Columns `A = (masks and blinders, pad)` and `B` uniform of the same length. After all claims on `A` are known: `theta` batches them; prover sends `beta = <B, w>`; verifier `c`; prover sends the vector `u = B + c A`; verifier `z`; prover reveals `A(z)`, `B(z)` (blinded evaluations of oracle 0, proven by the opening); checks `<u, w> = beta + c v` and `u(z) = B(z) + c A(z)`. | `len(A)` for `B`; at least 1 pad | all claimed values before `theta`; `beta` before `c`; `u` before `z` (S) | L `test_gadget.py` |
| A8 | **Blinder cells.** Every sumcheck that ends in evaluations of committed data has a dummy variable `y`; every revealed evaluation is `chat = c(r) + Z b` with its own cell `b` at a fixed position of the blinder column; one cell per (column, point). The cell is an `F` element stored as four `K` cells. The opening's relation contains `c(r) + Z b = chat` for each. | 1 `F` element per revealed evaluation | cells in oracle 0 before the component's challenges (S); never chosen or addressed after a challenge (S) | K `test_blind.py` part B; D `test_blinder_sound.py` |
| A9 | **W-I lane layout**, every level `i`: carried slots (witness, or the previous folded lane, whole); `kappa_i` zero guard slots; `1 + 4 kappa_i` aux slots holding this level's fold mask **in the last lane only** (at level 0 each coefficient takes four `K` rows); zeros; `t_i = Q_i` uniform coefficients per lane at an offset that is a multiple of `2^ceil(log2(t_i + kappa_i))`. Reject parameters whose lane exceeds the domain. The last oracle has one more column `Gcol`: the codeword of a uniform polynomial `gt` of the folded lane's length. | per level: `1 + 4 kappa_i`; `lanes x t_i`; last level: `lrow + kappa` for `gt` | oracle `i` (with its mask) before `rho_i` (S); `Gcol` before `c` (S) | K `test_whir_a.py` (layout controls: every-lane aux rows and narrow alignment are rejected); D `test_affine.py` |
| A10 | **W-I fold batch**, per level: prover sends `G_i`; verifier `rho_i`; claim `rho_i T + G_i`, weights times `rho_i`; `kappa_i` affine-combiner rounds whose four scalars are `rho_i` times the unmasked scalars plus the mask's message; after the batch the verifier adds the mask's final-value weights (`1` for the constant, the monomial `a, a^2, b, ab` at `(alpha_j, beta_j)` for round `j`) on the aux slots of the folded lane. | (A9) | `G_i` before `rho_i` (S) | K `test_whir_a.py`, `test_blind.py` part A; D `test_affine.py`, `test_mask_batch.py` |
| A11 | **W-I code switch**, levels below the last: commit oracle `i+1` holding the whole folded lane (no high part in clear); open `Q_i` rows of oracle `i`; fold each row as the lanes were folded; add the values with powers of `lam` to the claim and the evaluation weights over all `lrow_i + kappa_i` coefficients to the weight. No out-of-domain sample under unique decoding. | 0 | oracle `i+1` before the positions and `lam` (S); at most `t_i` distinct rows opened per oracle (Z) | K `test_whir_a.py` (two-level cases); D `test_wi_attacks.py` (the eq-fold model of the same step) |
| A12 | **W-I base case**, last level, in place of the final message and the final sumcheck: prover sends `mu = <gt, W'>`; verifier `c`; prover sends `P* = gt + c p'`; verifier checks `<P*, W'> = mu + c T`, then draws the positions, opens rows with `Gcol` and checks `P*(y) = Gcol(y) + c fold(row y)`. | (A9) | `mu` before `c`; **`P*` before the last positions** (S) | K `test_whir_a.py` (control: no base-case mask); D `test_basecase_sound.py` (order controls) |
| A13 | **Transcript.** Every prover message, the public input and the parameter table absorbed before the next challenge; separate domain tags per use; grinding nonce and challenges from separate oracle outputs; one test per Order row above that fails when the order is reversed. | 0 | all rows above | D controls in `test_mask_batch.py`, `test_basecase_sound.py`, `test_blinder_sound.py` |
| A14 | **Generator.** All randomness of A2 to A12 from one cryptographic generator with fresh entropy per proof; a test fails if two items read the same stream position. | seed | none | code review; unit test on stream offsets |
| A15 | **Wire audit.** List every value sent and every leaf opened; each is in the pad ledger of `zk-composition.md` 4.1 as padded or determined; every `Gtilde` appears in the gadget's list. | 0 | none | review |
| A16 | **Through-the-code simulator.** A witness-free simulator in A's code produces accepting proofs under programmed challenges; at toy size the rank comparison of K `test_whir_a.py` is reproduced through A's prover. | 0 | none | K `test_whir_a.py` as the model |
| A17 | **Soundness accounting.** The round list of `soundness/src/yugen_soundness/wi.py` (`rounds(c, "A")`) with the implemented parameters meets the tree target. | 0 | none | `soundness/tests/test_wi.py` |

### System A: additions from the gap review (`zk-system-a-gaps.md`)

The implementers' inventory of the pinned prover (`yugen-proof-a-zk/docs/zero-knowledge.md`
sections 11 to 14) named values and reductions that A1 to A17 do not cover. Each row below has its
construction, proof and soundness term in `zk-system-a-gaps.md`. Amendments to the rows above:
A5's "bottom-layer claims are column evaluations: A8" does not describe system A's bus (the last
layer's children are blinded like every layer's: A24, A22); A6 is replaced in system A by A18 and
A19 (the bus publishes two roots, no per-table terminal and no denominator); A8 stands and A21 is
its cheaper equivalent; the read-count protocol change Z-C1 to Z-C3 of the implementers' document
is not needed once A8, A18, A19 and A22 are built.

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
| A26 | **Base-case relation by a sumcheck** (allowed form of A12). `mu`, `c`, `P*`, positions and rows as A12; the relation `<P*, W'> = mu + c T` is then proved by an unmasked plain sumcheck of degree 2 on the zero-padded `P*` and the weight's multilinear, both evaluated by the verifier at the end point. The prover computes its messages from `P*` as sent | 0 | `P*` before the positions and before the sumcheck's challenges (S) | `zk-system-a-gaps.md` 12.1; K `test_whir_a.py` control "no base-case mask"; `test_narrow_align.py` for the layout control |

---

## System B (Plonky3 binary): staircase masks, GKR, bus, blinder cells, W-M

Parameters (estimates, `soundness/output/wi-tables.txt`, shared-budget tree target): rate 1/4,
folds 5/4, queries 183/127, leaf about 524 KiB; mask polynomial of `2^19` elements of `F`.

| # | Build | Random | Order | Reference |
|---|---|---|---|---|
| B1 | **Coset domain for oracle 0.** Oracle 0 is evaluated on `beta + S` with `beta` outside `S`; query points and row folds use the shifted points. Later oracles are those of the non-hiding opening. | 0 | none | K `test_code.py` (linear domain leaks exactly on `U_top`), `test_wm.py` (control); D `test_proximity.py` part A |
| B2 | **Salted leaves** on oracle 0: leaf digest = hash(32-byte salt, row of `p`, row of `mk`); the salt is opened with the leaf. | 32 bytes per leaf | salts are independent of all other randomness (Z) | hash-level; `zk-hiding-commitment.md` Lemma M |
| B3 | **Oracle 0 content**, beside the trace: blinder column (B8), mask column `A` with at least one pad element and gadget column `B` (B7), bus payloads (B6), `p`'s encoding randomness and the mask polynomial `mk` (B9). | as listed per item | oracle 0's root before every challenge (S, Z) | D `test_blinder_sound.py` and `test_mask_batch.py` controls |
| B4 | **Masked sumcheck** (zerocheck, ring switch, stacked-layout reductions; every sumcheck outside the opening): prover sends `G = Lam(g)`; verifier sends `rho`; sumcheck on `rho f + g`; `g` is a staircase mask (plain sum) or Libra's mask inside the eq factor (reduced messages); coefficients in column `A`. The verifier computes the mask's final value and adds the linear claim on `A` to the gadget's list. Libra's mask on a plain sum is not allowed in characteristic 2. | `1 + sum_j d_j` per sumcheck | mask in oracle 0; `G` before `rho` (S); one fresh mask per sumcheck (Z) | L `test_exact.py`, `test_rank.py`, `test_leak.py`; D `test_mask_batch.py` (order control) |
| B5 | **Layered arguments (grand-product bus layers).** Each layer gets a dummy variable `y` and two blinders per claimed polynomial (four for a fraction layer): `vhat(y, x, b) = v(x, b) + y (1 + y)(c_0 + c_1 b)`; blinded claims are sent; the next layer's head is `rho Ahat + Gtilde`. **Every `Gtilde` is entered in the gadget's claim list** as the linear functional `G' + rho Z (c_0 + alpha c_1)` of column `A`. Bottom-layer claims are column evaluations: B8. | 2 (or 4) per layer polynomial, in column `A`, plus the layer sumcheck's mask (B4) | blinders in oracle 0 (S, Z); `Gtilde` is sent after `rho` and is bound only by the gadget (S) | L `test_gkr.py`; `zk-wi-soundness.md` 6.3 |
| B6 | **Bus terminals.** One uniform mask payload per neighbouring table pair for the per-table products, one self-cancelling pair per table that publishes a denominator, inside the tables' own rows. | `T - 1` (+ `T`) payloads | payloads in oracle 0, before the bus challenges (S, Z) | L `test_bus.py` |
| B7 | **Linear-claim gadget.** Columns `A = (masks and blinders, pad)` and `B` uniform of the same length. After all claims on `A` are known: `theta` batches them; prover sends `beta = <B, w>`; verifier `c`; prover sends the vector `u = B + c A`; verifier `z`; prover reveals `A(z)`, `B(z)` (blinded evaluations of oracle 0, proven by the opening); checks `<u, w> = beta + c v` and `u(z) = B(z) + c A(z)`. | `len(A)` for `B`; at least 1 pad | all claimed values before `theta`; `beta` before `c`; `u` before `z` (S) | L `test_gadget.py` |
| B8 | **Blinder cells.** Every sumcheck that ends in evaluations of committed data has a dummy variable `y`; every revealed evaluation is `chat = c(r) + Z b` with its own cell `b` at a fixed position of the blinder column; one cell per (column, point). For bit columns the cell is an `F` element stored as four `K` words, read through the basis of `F` over `K`. The opening's relation contains `c(r) + Z b = chat` for each. Blinding rows appended to a column are not a substitute. | 1 `F` element per revealed evaluation | cells in oracle 0 before the component's challenges (S); never chosen or addressed after a challenge (S) | K `test_blind.py` part B; D `test_blinder_sound.py` |
| B9 | **W-M commitment.** Each lane of the witness polynomial `p` carries, above its message slots, `t = Q_0` uniform coefficients at an offset that is a multiple of `2^ceil(log2 t)`; reject parameters whose lane exceeds the domain. In the same leaves, the lanes of a mask polynomial `mk`: uniform in `F` on **every** slot of the same lane length (message slots and random slots alike). | `lanes x Q_0` in `K`; `lanes x lrow` in `F` for `mk` (`2^19 + 32 x 183` elements at the design basis) | `p` and `mk` in oracle 0 before `rho` (S) | K `test_wm.py` (controls: one coefficient too few, mask missing a slot, no mask) |
| B10 | **W-M opening.** Prover sends `G = <mk, W>` (`W` the batched weight of the claim `<p, W> = T`); verifier sends `rho`; the **unmodified non-hiding opening** is run on `h = rho p + mk` with claim `rho T + G`. A level-0 query opens the row of `p` and the row of `mk` from one leaf and uses `rho x (p's row) + (mk's row)`. No mask, no aux rows, no random coefficients and no salts are added to any later oracle, round message or final message. | 0 | `G` before `rho` (S); at most `Q_0` distinct level-0 rows opened (Z) | K `test_wm.py`; `zk-wi-soundness.md` section 9 (one added round, `(N_0 + 1)/|F|`) |
| B11 | **Non-hiding opening unchanged.** The opening invoked by B10 is byte-for-byte the verifier used for B's non-hiding proofs apart from reading level-0 rows as the combination; a test proves a non-hiding statement and a hiding one through the same opening code. | 0 | as the non-hiding opening | B's existing opening tests |
| B12 | **Transcript.** Every prover message, the public input and the parameter table absorbed before the next challenge; separate domain tags per use; grinding nonce and challenges from separate oracle outputs; one test per Order row above that fails when the order is reversed. | 0 | all rows above | D controls in `test_mask_batch.py`, `test_blinder_sound.py` |
| B13 | **Generator.** All randomness of B2 to B9 from one cryptographic generator with fresh entropy per proof; a test fails if two items read the same stream position. | seed | none | code review; unit test on stream offsets |
| B14 | **Wire audit.** List every value sent and every leaf opened; each is padded or determined: values computed from `h` (padded by `mk`), level-0 rows of `p` (padded by its random coefficients), and the ledger rows 1 to 6 of `zk-composition.md` 4.1; every `Gtilde` appears in the gadget's list; the ring switch and stacked-layout reductions are listed with their round spaces and masks. | 0 | none | review |
| B15 | **Through-the-code simulator.** A witness-free simulator in B's code: sample `h`, run the non-hiding opening on it, sample `p`'s opened rows, derive `mk`'s rows and `G`; it produces accepting proofs under programmed challenges; at toy size the rank and enumeration comparisons of K `test_wm.py` are reproduced through B's prover. | 0 | none | K `test_wm.py` as the model |
| B16 | **Soundness accounting.** The round list of `soundness/src/yugen_soundness/wi.py` (`full_mask_rounds`) with the implemented parameters meets the tree target; proof size and prover memory with `mk` are measured (the 524 KiB figure is an estimate). | 0 | none | `soundness/tests/test_wi.py` |

---

## What neither list covers

- Recursion layers publish nothing secret and stay non-hiding.
- Fraction (logarithmic-derivative) layers: construction stated in `zk-masked-sumcheck.md`, not
  tested; a system that uses them needs its own reference test first.
- Univariate-skip or otherwise optimised round messages must be matched to the masked form before
  A4 / B4 apply (`zk-masked-sumcheck.md` work item W-6). System A's are matched: the Keccak
  product round (A23), the radix-4 batched bus layer (A24), the fold rounds (A9, A10).
- Not tested in the toy models: a level-0 alphabet smaller than `F` inside W-I (A9, A10); an exact
  soundness game for W-M's `rho` step.
