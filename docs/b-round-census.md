# System B: the round census of a payment (leaf) proof and of a node proof

Part of Yugen. Maths team, 2026-11-19. Answers referee-queue item 4 of `what-is-proven.md` (row S-7)
for the rounds, and supplies the per-round list that obligation K-B needs (`lemma-k-b.md`). **Status: DRAFT,
unrefereed.** Code read at `yugen-proof-b2` `HEAD` = `1f67267` (read-only, by `git show HEAD:<path>`); build
`cat1t,blake3` (challenge field `K = GF(2^256)`, `binius_verifier::config::B128 = ChallengeField`,
`vendor/binius64/crates/verifier/src/config.rs:12-14`). Calculator read at this repository's `HEAD` (`a622179`),
revision 10.2, run read-only.

## 0. Result

| | Leaf, 192 queries, rate 1/8 | Node, 235 queries, rate 1/4 |
|---|---|---|
| Field elements drawn (algebraic challenges) | **181** (measured, `parameters.md` 2a.4; `cat1-20261119.txt`) | **246** for the calculator's bounding node of `2^30` AND rows (formula of 2a.4); the as-built node is smaller |
| Verifier messages (`|J_V|`) | 127 (T-1, `t1-kq-20261120-p.txt`) | 143 (T-1, by formula) |
| In-circuit batching transcript of the node (P-sh) | none | 59 (level 0) / 70 (merge) verifier messages (T-1 `node-main-inner-*`) |
| Weakest algebraic **message** | `gamma` and the commitment-index round, `(2^22 + 2) / |K|`: **234.0 bits** | first fold round, `(2^30 + 2) / |K|`: **226.0 bits** |
| All algebraic challenges of the proof merged into ONE message (worst grouping) | **232.0 bits** | **225.0 bits** |
| Query round | `192 x 0.830075` = **159.37 bits** | `235 x 0.678072` = **159.35 bits** |
| Per-round need (calculator, every-`t`, `k_q` estimated) | 158.59 (`k_q` 40,416 E) | 158.82 (`k_q` 47,520 E) |
| Per-round need at the T-1 reported `k_q` | 158.02 (27,188, native) / 158.02 (27,232, in-circuit) | 158.05 (27,689, by formula) |

**Every B row meets its per-round need with the census.** The binding round is the query round, already the
calculator's binding round (margins +0.78 and +0.52 bits at the estimated `k_q`, +1.35 and +1.30 at the reported
one). Every algebraic round has at least 66 bits to spare, and so does the worst conceivable grouping of them, so
no grouping question of section 3 can move a row. **B does not have system A's gap** (`theorem-s-referee.md` M-3):
the calculator lists B's non-opening rounds one by one with an error each (`binius64.rounds_counted`, from the
builders' census `parameters.md` 2a.4), and under the every-`t` convention the need depends on `k_q`, not on the
number of rounds. No query count changes; no fix to a certified count is needed.

What the census adds to the record: four discrepancies between the calculator's list and the code, none binding
(section 4), one open proof obligation that the margin does not discharge (lifted oracles, R-8; section 5), and
one item the tree lemma must name (the node's in-circuit batching rounds; section 2.3, `lemma-k-b.md` 3).

## 1. Method

Every `sample`, `sample_many` and `sample_bits` on the native verifier's path was located by
`git grep -n "sample" HEAD -- vendor/binius64/crates/{verifier,iop,ip,spartan-verifier}/src src`, and each call
site read. The order of calls is the order of `IOPVerifier::verify` (`verifier/src/verify.rs:200-330`), the
wrapper (`verifier/src/zk_config.rs:261-326`, `spartan-verifier/src/lib.rs:235-300, 407-440`) and the opening
(`iop/src/basefold/channel.rs:220-260`, `opening.rs:57-99`, `fri/verify.rs:194-240`). Counts were checked against
the builders' measurement (`bench/results/cat1-20261119.txt`, phase lines; `parameters.md` 2a.4, table
"Measured"). Errors are stated for a verifier message, the unit of [SG26] Definition 2.20 (C. Sharp, P. Grubbs,
*Faster and Smaller Anonymous Credentials from Standardized Signatures*, ePrint 2026/2615, page 14): where one
message carries several challenges, the error is the sum over them, by [SG26] **Lemma 5.2 (Merged verifier
messages)**, page 37 (Published; read on the rendered page).

Notation: `|K| = 2^256`; "bits" means `-log2` of the error; `d / |K|` for a univariate round polynomial of degree
`d` (Schwartz-Zippel, standard); a point of `m` coordinates drawn in one message for an `eq`-weighted
multilinear claim costs `m / |K|` (Schwartz-Zippel on a multilinear polynomial of total degree at most `m`).

## 2. The census

### 2.1 Payment proof (zero-knowledge leaf), as built: `a = 17`, `w = 17`, `p = 8`, `kappa = 8`, `c = 21`, `v = 19`, `o = 1`, 4 relations, codeword `2^22` at rate 1/8

| # | Part | Source (code) | Challenges in the message | Error of the message (units `1/|K|`) | Bits | Basis |
|---|---|---|---|---|---|---|
| 1 | BitAnd zerocheck point | `verify.rs:556-563` | `a - 3 = 14` coordinates, one `sample_many` (three are the fixed `GF(2^8)` constants) | 14 | 252.19 | `parameters.md` 2a.3 Lemma (Original, the Ycash developers; its proof read: correct, needs `f` bit-valued on the cube, which 2a.3 shows for every committed trace) |
| 2 | Univariate skip `z`, then the rerand batch coefficient | `bitand.rs` `verify_univariate_skip` (64 coefficients received, `z` sampled); `rerand.rs` -> `sumcheck/batch.rs:48` (no prover message between) | 2 | 127 + (sums - 1) = 127 (leaf: one sum, no BinMul) | 249.01 | degree < 128 on the 128-point skip domain (64 forced zero); batch: Schwartz-Zippel in the coefficient; merged by [SG26] Lemma 5.2 |
| 3-19 | BitAnd sumcheck rounds | `sumcheck/verify.rs:52`, `SUMCHECK_DEGREE = 3` (`rerand.rs`) | 1 each, 17 messages | 3 | 254.42 | textbook sumcheck round (degree 2 prime factor times the indicator) |
| 20 | Shift operand batch | `shift/verify.rs:156` | `ceil(log2 13) = 4` coordinates | 4 | 254.00 | multilinear batching of 13 claims, total degree 4 |
| 21-74 | Shift sumcheck | `shift/verify.rs:175`, degree 2, `SHIFT_LOG_VARS + log_word_count` = 36 + 18 rounds | 1 each, 54 messages | 2 | 255.00 | sumcheck |
| 75 | Public input: ring switch `r''` | `ring_switch.rs:85` (`sample_many(LOG_DEGREE)` after `recv_many`) | 8 | 8 | 253.00 | ring switch, `kappa / |K|`: Theorem 1 of `binius-extension-challenges.md` 3.1 (Adapted from Diamond-Posen, ePrint 2024/504, Construction 3.1, Theorem 3.5); found to hold by `johnson-row-referee.md` (J1) |
| 76-83 | Public input sumcheck | `reduction.rs:399`, degree 2 | 1 each, 8 | 2 | 255.00 | sumcheck |
| 84 | Ring switch of the trace claim | `verify.rs:305-308` -> `ring_switch.rs:85` | 8 | 8 | 253.00 | as row 75 |
| 85 | Wrapper mulcheck point | `spartan-verifier/src/lib.rs:418` (`sample_many(log_mul_constraints)`), after the outer private and mask oracles | `c = 21` | 21 | 251.61 | zerocheck by MLE-check, Schwartz-Zippel |
| 86 | Wrapper blend challenge | `ip/src/mlecheck.rs:97` (after `recv_one` of the mask evaluation) | 1 | 1 | 256.00 | `zk-wi-soundness.md` Lemma 6 (Original, the Ycash developers): a mask fixed before its blend challenge |
| 87-107 | Wrapper MLE-check rounds | `mlecheck.rs:65`, degree 2 | 1 each, 21 | 2 (the calculator charges 3) | 255.00 | sumcheck |
| 108 | Wrapper operand batch `lambda` | `spartan-verifier/src/lib.rs:278`, after `recv_array` of `a, b, c` | 1 | 2 | 255.00 | Schwartz-Zippel, degree 2 in `lambda` |
| 109 | Opening relation batch `mu` | `basefold/channel.rs:242` | 1 | relations - 1 = 3 | 254.42 | Diamond-Posen ePrint 2024/504 / the Blueprint 7.2, as `binius-extension-challenges.md` 4.2 cites (not re-read here) |
| 110 | Mask fold `gamma` | `basefold/channel.rs:254` (after `recv_one` of `s'`) | 1 | `2^22 + 1` | 234.00 | BCIKS20 Theorem 4.1 on the line `s' + gamma s` and one root for the mask claim: Diamond, *Zero-Knowledge Polynomial Commitment in Binary Fields*, ePrint 2025/1015, Theorem 4.2, proof sketch (page 5, read on the rendered page; no explicit error there); the count `n + 1` is ours (`binius-extension-challenges.md` R-7). **Not binding**: even `n^2 / |K|` would leave 212 bits |
| 111 | Commitment-index round | `basefold/opening.rs:75-78` (`recv_many(2)`, `sample`) | 1 | `2^22 + 2` | 234.00 | as the fold rounds; `binius-extension-challenges.md` R-6 (C-12) |
| 112-130 | Fold rounds `j = 0..18` | `opening.rs:75-78` | 1 each, 19 | `2^(22-j) + 2` | 234.00 up to 252.9 | per round `n_j / |K|` bounds Diamond-Posen ePrint 2024/504 Proposition 4.21 (`theta |S^(i+theta)| / |L|` per committed oracle, read on the rendered page 40) and the sumcheck term `2 / |K|`; round-by-round form: Haböck, ePrint 2024/1571, Theorems 1 and 6 (C-12, as cited by the calculator) |
| 131 | Query indices | `fri/verify.rs:211` (192 x `sample_bits(index_bits)`) | 192 indices | `((1 + 1/8) / 2)^192` absolute | **159.37** | unique-decoding query bound, DP24 proof of Proposition 4.24 and equation (42); S-4 (Lemma UD), refereed (`johnson-row-referee.md`) |

Totals: 181 field elements (14 + 2 + 17 + 4 + 54 + 8 + 8 + 8 + 21 + 1 + 21 + 1 + 1 + 1 + 1 + 19 = 181: matches the
measured phases 33 / 58 / 16 / 8 / 44 / 2 / 20) and the query message. My grouping by "no prover message between"
gives 131 messages; T-1 reports 127 keys (section 4, D-4).

Sum of every algebraic error of the proof: `2 (2^22 + 2) + sum_j (2^(22-j) + 2) + (small terms < 2^10)` `<= 2^24`,
so **232.0 bits** even if every algebraic challenge were one message ([SG26] Lemma 5.2).

### 2.2 Node proof (transparent), 235 queries, rate 1/4: the calculator's bounding shape `a = 30`, `b = 29`, `w = 30`, `p = 12`, `v = 28`, `kappa = 8`

The node proof is the same verifier without the wrapper, the mask and the commitment-index rounds, with the BinMul
reduction present (`protocols/binmul.rs:78-113`) and one relation (`mu` error 0).

| Part | Challenges | Error of the message | Bits |
|---|---|---|---|
| BinMul zerocheck point (`binmul.rs:78`, one `sample_many`) | 29 | 29 | 251.14 |
| BinMul MLE-check rounds (`mlecheck.rs:65`, degree 2; calculator 3) | 29 messages | 2 | 255.00 |
| BitAnd zerocheck point | 27 | 27 | 251.25 |
| Skip `z` + batch coefficient (sums: the AND claim and the BinMul operand claims, at most 11) | 2 | 127 + 10 | 248.90 |
| BitAnd sumcheck | 30 messages | 3 | 254.42 |
| Zero extension (`reduction.rs:300`) | `max(0, z - n*) = 0` | | |
| Shift batch; shift sumcheck | 4; 67 messages | 4; 2 | 254.00; 255.00 |
| Public ring switch; public sumcheck | 8; 12 messages | 8; 2 | 253.00; 255.00 |
| Trace ring switch | 8 | 8 | 253.00 |
| Opening `mu` | one relation | 0 | |
| Fold rounds `j = 0..27` | 28 messages | `2^(30-j) + 2` | 226.00 and up |
| Query indices | 235 | `(5/8)^235` | **159.35** |

The bounding shape is larger than any built node (the node row's size model is `2^27` words; T-1 counts 143
messages on the recorded chain). The sum of every algebraic error is below `2^31`: **225.0 bits**.

### 2.3 The node's in-circuit batching transcript (`src/pbatch.rs`, protocol P-sh)

These challenges are drawn by the in-circuit challenger of the node's main circuit, from the slots' claim elements;
they are not challenges of the node's B proof, but rounds of a reduction inside the node relation (section 2.3 of
`lemma-k-b.md`). Read in `pbatch.rs:225-360`:

| Message | Challenges | Error | Bits | Basis |
|---|---|---|---|---|
| after the label and every claim element (C-2, C-7) | `alpha`, shared by all groups | `(K_max - 1) / |F|`, `K_max` the largest group's claim count | at least 249 (`K_max <= 2^7`) | Lemma R and Lemma P of `decision-b-parallel-batching.md` 5 (Lemma P Original, the Ycash developers, refereed PASS: `b-batching-and-hash-referee.md` 2.1) |
| global round `j = 1..n_max`, after every active group's `c0, c2` (C-3) | one `r_j` | `2 / |F|` (Lemma P: the max over the active groups, no factor `G`) | 255.00 | Lemma P, Lemma R |
| after every group's `s_o` and final check (C-2, C-6) | `mu` if a group has several sets | `(n_sets,max - 1) / |F|` | 255.00 | Lemma R |

The code matches P-sh as fixed in the decision record: end alignment (`Schedule::start`), one `alpha`, separate
running claims (no addition of two groups' claims, so PB-3 does not arise), `c1 = claim + c2` from the group's own
claim, every group's final check asserted before `mu`, the label binding the schedule and version (`label`,
`pbatch.rs:150-175`). The channel's field is `B128 = ChallengeField`, the 256-bit field under `cat1t`, so Lemma P's
"one challenge set" holds. Messages: 59 (level 0) and 70 (merge) by T-1.

## 3. The calculator against the census

`category.b_algebraic` (used by every B row) takes `johnson.terms` (the opening) and `binius64.rounds_counted` (the
rest) for `binius64.leaf_shape(MIXED_T_W1)` and `B_NODE_SHAPE`, and refuses a row whose weakest algebraic term is
below the need. It charges every challenge element as its own round. Against the census:

| Row | Calculator's weakest algebraic | Census, weakest message | Census, all merged | Need (E) | Query round | Meets |
|---|---|---|---|---|---|---|
| B leaf, 1/8, 192 (certified) | index round 0: 234.0 | 234.0 | 232.0 | 158.59 | 159.37 | **yes** (+0.78) |
| B leaf, 1/16, 174 (certified) | index round 0: 233.0 | 233.0 | 231.0 | 158.50 | 158.78 | yes (+0.28) |
| B node, 1/8, 192 (certified) | fold.0: 225.0 | 225.0 (at `2^30` rows, rate 1/8: `2^31`) | 224.0 | 158.59 | 159.37 | yes |
| B node, 1/4, 235 | fold.0: 226.0 | 226.0 | 225.0 | 158.82 | 159.35 | **yes** (+0.52) |

The per-element charge understates a merged message's error (rows 1, 85 and the node's two zerocheck points by
`log2 14` to `log2 29`, at most 4.9 bits), but the merged figure is still above 248 bits for every non-opening
message, and the opening messages are single challenges. So the calculator's per-round check is right in its
conclusion and needs no change to certify; section 4 lists what its round list should say.

## 4. Discrepancies (none binding; for the calculator's maintainers)

| | Calculator | Code | Effect |
|---|---|---|---|
| D-1 | wrapper `c = 18` (`MIXED_T_W1`, task W-1, E) | `c = 21` as built at 256 bits (measured 44 wrapper elements = `2 c + 2`) | `k` 176 vs 181 elements; no error term changes (each 255 to 256 bits) |
| D-2 | public sumcheck `p = 9` | `p = 8` (measured 16 = 8 + 8) | one element fewer in the code |
| D-3 | wrapper and BinMul sumcheck rounds charged degree 3 | MLE-check rounds of degree 2 (`mlecheck.rs`; `binmul.rs:85`, `lib.rs:425`) | calculator conservative by `log2 1.5` |
| D-4 | one round per element | several elements per message (rows 1, 2, 20, 75, 84, 85; BinMul point); 131 messages by my grouping, **127 keys reported by T-1** | errors to be summed per message ([SG26] Lemma 5.2); worst 21 / `|K|`. The difference of 4 between my grouping and T-1's key count is **not explained** here; it cannot move any figure (the all-merged bound of section 2 covers every grouping). Owed: T-1's per-message trace (which samples share a key) to close it |

Under the every-`t` convention the number of rounds does not enter the need (`category.every_t_need` uses `k_q`);
under the book convention it enters through the 600-challenge budget, which the leaf (182) and the node (246 plus
up to 70 batching messages under P-sh; 417 under the sequential form) are inside.

## 5. What the margin does not discharge

- **Lifted oracles of unequal size (R-8).** The leaf's opening batches round oracles of `2^17`-ish and `2^20`-ish
  elements by "lift and repeat" (`iop-prover/src/basefold/index_rounds.rs`, head comment; `iop/src/basefold/layout.rs`)
  and folds across commitments in the commitment-index round. The per-round charge `(n + 2) / |K|` with `n` the
  largest codeword is ours and rests on a proximity statement for the lifted words that no source in the folder
  states for this construction ([HMH] not read; `binius-extension-challenges.md` R-8). With 75 bits of margin any
  polynomial loss is absorbed, but the statement is a **proof obligation, not a figure**: owed a lemma that a
  lifted-and-repeated word far from its code stays far after the commitment-index fold (the same form as BCIKS20
  Theorem 4.1 on the line of the two lifted words). Smallest fix: prove it for the "repeat" embedding, where a
  repeated message is a message of the larger code (Lemma 4 of `binius-extension-challenges.md` 4.1 is the model).
  *Addendum 2026-11-19:* proven in B's unique-decoding regime by **Lemma LF** (`lemma-k-b.md` section 3a; Original
  (the Ycash developers, 2026), written by the referee of `zkq-te3-r8-referee.md` section 3, **refereed-in-review**,
  not yet independently read): `Lift = c o (X^2 + X)^L` in the Gao-Mateer basis maps `RS_s` into `RS_b`, preserves
  distance, and every codeword of `RS_b` within unique-decoding distance of a lifted word is a lift. The charge
  `(n + 2)/|K|` stands; no figure moves. Condition **m-5**: system B owes a direct encoding test (encode a random
  message on the small domain, lift by `>> L`, compare with the large code's encoding of the embedded message, at
  every `L` the rows use).
- **The ring switch, the univariate skip and the shift reduction** are taken from the builders' reading and the
  cited papers; I checked call sites and degrees, not the reductions' completeness or their state functions.
- **The query round** is S-4's, refereed; Lemma D's conditions (repeated indices) are `lemma-d-referee.md`'s.

## 6. Provenance

Published: [SG26] Definition 2.20 and Lemma 5.2 (pages 14, 37); Diamond-Posen ePrint 2024/504 Proposition 4.21
(page 40), proof of Proposition 4.24 (page 42); Diamond ePrint 2025/1015 Theorem 4.2 (page 5); Schwartz-Zippel and
the sumcheck round bound (standard). Adapted: the ring switch over `GF(2) < L < K` (`binius-extension-challenges.md`
Theorem 1, from DP24 Construction 3.1 / Theorem 3.5). Original (the Ycash developers, 2026), first here: this
census (per-message errors from the code at `1f67267`, the all-merged bound, the comparison with the calculator,
D-1 to D-4); the per-round errors it reuses that are ours carry their own labels (2a.3 Lemma, Lemma 6, Lemmas P
and R, the mask count `n + 1`). Sources consulted before labelling: the papers above and `REFERENCES.md` entries
[SG26], [DP24], [Dia25], [Hab-LDR]; none gives a census of this verifier.
