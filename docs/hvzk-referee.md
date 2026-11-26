# Referee: honest-verifier zero knowledge of both proof systems

Part of Yugen. First full read of the simulators in `zk-composition.md`,
`zk-hiding-commitment.md` and `zk-masked-sumcheck.md`, checked against the code at the heads
`yugen-proof-a` `57cacc2`, `yugen-proof-a-zk` `3ec10ab`, `yugen-proof-b2` `710f63e` (read with
`git show HEAD:`), and against the rendered papers in the reference-paper collection (REFERENCES.md) (pypdfium2).
Referee date 2026-11-19. Marks: **(R)** reasoned here; **(S)** read in source, file named;
**(P)** read in the rendered paper, page named; **(N)** not checked.

Verdicts: **HVZK of A: PASS WITH CONDITIONS. HVZK of B: PASS WITH CONDITIONS. Composition: PASS.**

---

## 1. System A (leanVM, opening W-I)

### 1.1 Claim and simulator

Claim (`zk-composition.md` Theorem C): at fixed challenges outside the excluded events, the
algebraic view of a leaf proof equals the output of a witness-free simulator that samples every
padded block uniformly in protocol order and computes the determined values; Merkle trees are
built over the simulated opened leaves with uniform digests elsewhere (Lemma M). The simulator
is built in code (`verifier::zk::sim`, `tests/zk_view.rs::simulate`, `yugen-proof-a-zk`
`docs/zero-knowledge.md` 18.1): 45 scalars and 616 row words determined, the rest drawn.

### 1.2 Per message, against the code

| Message | Pad and count (code) | Check |
|---|---|---|
| Masked sumcheck rounds (table sumcheck, Keccak layers, bus GKR, inputs/outputs) | Libra's mask inside the `eq` factor (Corollary B) or staircase; one mask per instance in column `A`; dummy round per A8-T | Theorem 1 (R: proof re-derived; Lemma 1 recursion, the `q^n` fibre count and the `kappa` construction are correct; Corollary B needs `lam(1) = 1`, true in characteristic 2 for every `tau`). The mask is a bijection onto `V_r` (staircase) or a surjection (Libra form), so the mask is exactly used up by `G` and the rounds; `g(r)` is determined. Any further functional of the mask must come with its own pad: the gadget (`B`, 2,048 elements, consumed by `u`) and the pad elements of `A` (below) |
| Blinded evaluations `chat` | one `F` cell per (column, point), A8 | Theorem B (R: correct; one block, translation by `Z b`, `Z != 0`) |
| Out-of-domain value (level 0) | **not** the encoding randomness: it is `mle(stack, z)` of the message (S: `pcs/src/stack_open.rs` l. 107-108; `verifier/src/lib.rs::read_ood`). Its pad is a spare element of column `A` (S: `verifier/src/zk.rs` `Region::with_slices`: "two pad elements at least: one for the gadget's `A(z)`, one for the commitment's out-of-domain sample") | holds, see finding H-2 for the error term |
| Opened rows, level `i` | `t_i = queries_i` uniform coefficients a lane at an offset aligned to `(t_i + kappa_i).next_power_of_two()` (S: `verifier/src/wi.rs::layout`, `t: queries`; prover `pcs/src/wi.rs::secrets`, `extras`); coset domain (S: `encode`, `base = cosets`) | At row 8 (`params.rs` l. 289-295, wallet shape `[234,166,169,186]`): revealed per lane at level `i` = distinct positions `<= Q_i = t_i`. No out-of-domain sample at levels 1 to 3 (S: `verify_wi` reads none), so `o_i = 0` and Lemma O's `t = Q + o` is met with equality. Lemma E applies (aligned offset, coset) |
| Fold rounds and `G_i` | `1 + 4 kappa_i` coefficients a level in the last lane (S: `layout`, `mask_weights`) | Theorem 1' with round space `span{1, a, a^2, b, ab}`: 4 scalars a round sent, `1 + 4 kappa` coefficients: bijection (R, matches the count) |
| Base case `mu`, `P*` | `gt`, `lf` uniform elements (S: `base_case_mask`); `mu` and the tail sumcheck determined | `P*` is `lf` scalars padded by `lf` uniform elements (R) |
| Mask column at the last level's opened rows | determined (616 words) | by the verifier's check (S: `verify_wi`, `fix_leaf`) |
| Salts and sibling digests | 64-byte leaf salts (S: `SaltSource`, `leaf_salt_words`); uniform digests elsewhere | Lemma M; the quantum statement is Z-2's, not this report's |
| Duplicate positions, first/duplicate flags | functions of public coins | no information (R; agrees with `zk-referee.md` R-5) |
| GKR / Keccak / bus outside the opening | bus roots `e R(w, a)` with mask leaf `e`; each layer's children blinded (A24); Keccak layers A23 with `Gtilde` determined; count root A18; slices A20 | Every wire value is classified masked, determined, public or hash by the test `every_value_on_the_wire_is_a_hash_public_determined_or_masked` (18.4). No witness-dependent value was found unmasked. The 1,788 non-affine words (products of a mask leaf or memory cell with witness) are argued by the conditional statistic (18.12.2) |

### 1.3 `eps_hvzk^A`

Excluded events (each `O(1)/|F|`, `|F| = 2^256`): dummy challenge `r_y = 0` per sumcheck with a
dummy round (about 30), bus payload events (`T - 1`), the gadget's pad weight (`log2 len A`).
Under 300 events: `eps_hvzk^A <= 2^-247` on paper (R), plus H-2's term (negligible at the built
pad count, `<= 2^-6000` with 104 pad elements; up to about `2^-62` if a shape left only two).
Target (`decision-security-profile.md` §2.1): `2^-128` over `Q = 2^37` proofs, so
`eps_hvzk <= 2^-165` is needed: **met on paper**, under the conditions of section 5.

---

## 2. System B (Binius64 zero-knowledge mode, `yugen-proof-b2`)

### 2.1 Claim and simulator

**The built system is not the one `zk-composition.md` describes** (finding H-1). B as built is
Binius64's own mode (`yugen-proof-b2/docs/zero-knowledge.md`): the inner protocol's messages are
one-time padded by keys `z_pre` committed in round oracle 0; IronSpartan proves the inner verifier
accepts; one batched BaseFold opening on `M^gamma = w + gamma M` (Diamond's orientation since
VENDOR change 25), each round oracle with a pad of `q 2^(log_batch_size - 1)` coordinates placed
on novel-basis coefficients `0..q` of a linear domain. The simulator is the three-layer one of the
Binius64 Blueprint 7.3 (pads uniform; IronSpartan's masked check simulated by its Theorem 6.3;
the opening simulated by sampling `M^gamma` and the opened symbols of `Enc(M)`). **No simulator is
built in code** (F-5 (b) open).

### 2.2 Per message

| Message | Pad and count | Check |
|---|---|---|
| Inner messages (sumcheck rounds, claims, layer claims) and the inner query target | one key each, never reused (S per the B review M7, M8, C11) | uniform; the key vector is then consumed except for the precommit contribution `s_pre`, which is one more linear functional of the keys and rests on the segment's dummy constraints (M10, M11): **N3 unproven** (H-3) |
| Wrapper constraint sumcheck | Libra mask in the `eq` form, `n(d+1)` coefficients (surjection) | Corollary B of the lemma document applies (R); blend challenge 0 excluded and the prover restarts (change 5): conditioning on a public-coin event, no leak |
| Wrapper products `(a, b, c)` | two dummy constraints per segment | N3: the sketch gives distance about `1/|K|` per segment (R, not written) |
| Opened symbols of `Enc(M_r)` | pad `q = n_queries` = 192 at rate 1/8 (S: `src/params.rs` l. 189 `CAT1_QUERIES`; pad reads the same `n_test_queries`; `check_zk_pad` refuses a shorter pad). A query opens one symbol of `Enc(M_r)` per round oracle; positions de-duplicated (change 34) | distinct revealed `<= 192 = pad`: CFW26 Lemma 3.29 (P, ePrint 2026/391 p. 38) gives error 0 for `X_0..X_(q-1)` on distinct points. The rank test at leaf size ran at `q = 116` and 232 only (B review 2.1), not at 192; the argument does not depend on `q` |
| Opened symbols of `Enc(w_r)` | determined from `Enc(M^gamma)` and `Enc(M)` | Diamond Theorem 4.3 simulator (P, ePrint 2025/1015 p. 5-6) |
| Fold rounds, folded codewords, terminal | functions of `M^gamma`, uniform for every `gamma` | Diamond Construction 4.1 orientation (P) |
| Salts | 512-bit leaf salts on round oracles and fold trees under route S (`7de8da0`) | Lemma M |
| Wiring claim | public function of challenges | argued (B review 1.3, N6) |

### 2.3 `eps_hvzk^B`

On paper: two N3 events at about `2^-255` each; nothing else (pad error 0, mask fold error 0,
blend 0 excluded by restart). `eps_hvzk^B <= 2^-253` (R), **conditional on N3 and N8 being written
and on the Blueprint's Theorem 6.3 / Lemma D.1** (an upstream design document, not a refereed
paper; read by the B team, **not read by this referee**). Meets the `2^-165` requirement on
paper.

---

## 3. Composition (leaf proofs inside the bundle)

Node proofs are made by the host from data it holds: leaf proofs (published on the audit feed),
child node proofs and public records (S: `yugen-proof-a` `docs/recursion.md` BC-1 to BC-3: every
node advice cell is a leaf's public value, a child's count/content/attribution or proof bytes).
The host never holds a leaf witness, so a node proof and its public inputs are functions of
public data and of the host's own randomness: by data processing they reveal nothing about a
leaf witness beyond the leaf proof. B's recursion layers are non-hiding for the same reason.
**PASS.** (Hypothesis N was read against both builders' documents, as `zk-referee.md` did; the
node circuits were not re-derived.)

---

## 4. Citations checked against the rendered papers

| Citation | Page | Result |
|---|---|---|
| Ben-Sasson, Chiesa, Spooner, ePrint 2016/116, Theorem 7.1 (third bullet) and Lemma 7.5 | pp. 27, 32 | as quoted: public-coin, `z`-statistical HVZK, `z' = z + p 2^(-lambda/4+2)`, explicitly-programmable RO |
| Chiesa, Fenzi, Weissenberg, ePrint 2026/391, Lemma 3.29 | p. 38 | as used in B: low random coefficients, strong `t`-query ZK encoding, error 0 |
| Diamond, ePrint 2025/1015, Lemma 4.4 | p. 6 | as described: high coefficients over `S^(0)` disjoint from `<beta_0..beta_(l-1)>`; last step the Vandermonde of `X_0..X_(kappa-1)`. Lemma E is a correct generalisation (aligned offset, coset) |
| Sharp, Grubbs, ePrint 2026/2615, Lemma 5.8 (3) | p. 44 | pads among the oracle-input elements, HVZK error 0 w.r.t. the uniform simulator: consistent with "adapted" for blinder cells |
| Libra 2019/317 Section 4.1; CFW26 Definition 6.1 / Lemma 6.2, Section 2.5; SG26 Theorem 6.6 | | (N) not rendered by this referee |

---

## 5. Findings

**H-1 MAJOR (documents; no leak).** `zk-composition.md` §1 and §5 describe system B as "Plonky3
binary" with W-M on a coset domain, a ledger of blinder cells, staircase masks and a grand-product
bus. The built B (`yugen-proof-b2`) is Binius64's mode (one-time-pad keys, IronSpartan wrapper,
low-coefficient pad on a linear domain, BaseFold). Theorem C therefore does not cover B, and
`eps_hvzk^B` rests on `yugen-proof-b2/docs/zero-knowledge.md` and the Blueprint, not on the three
documents. *Fix:* replace §5's B paragraph and the B column of §1 with the built construction
(rows M1 to M12 of the B review as the ledger), name Lemma 3.29 of 2026/391 as the encoding lemma
in place of Lemma E for B, and point `what-is-proven.md` Z-B at it. Done when the B ledger names a
pad for every row of the B wire list.

**H-2 MINOR (A; error term missing).** The level-0 out-of-domain value is `mle(stack, z)` over
`K = GF(2^64)` cells; its pad (a spare `F` element of `A`, four `K` cells) is read through
`F`-valued weights `eq(z, cell)`, so independence of the out-of-domain value and the gadget's
`A(z)` is a `K`-rank condition, failing with probability of order `|K|^-(c - 7)` for `c` spare
cells, not `1/|F|`. With exactly two spare elements this is about `2^-62`. Theorem C's excluded
events list only `F`-events, and the joint statistic covering both (the stream before the opening,
16,428 words) is not decided. *Attack:* none at the built shape (104 spare elements). *Fix:* add
the event to Theorem C's table with the bound, and assert in `Region::with_slices` at least
`8 + 64` spare cells (or 18 elements); test: a shape with `masks + 2 = 2^k` is refused or padded.

**H-3 MAJOR (B; unproven step).** N3 (the dummy-constraint blinding of `(a, b, c)` and of `s_pre`,
which is the only pad left for the extra functional on the keys) and N8 are sketches; no
simulator through the code (F-5 (b)); the bit statistic ran at rate 1/2, 96 proofs. *Fix:* write
N3 as a lemma (the distribution of `al1 a1 b1 + al2 a2 b2` given the two linear shares) and check
it by enumeration over GF(16) in the `zk-lemma/` style; build the opening simulator of F-5 (b);
rerun `zk_pad_rank` at `q = 192`.

**H-4 MAJOR (A; evidence at an old row).** The through-the-code evidence (simulator acceptance,
ranks, wire audit) is at row 6 (226/157/154/154) on a superseded proof format; the joint parts
"stream before the opening", "opening" and "whole view" are not decided (18.12.6). Theorem C
plus the code reading in 1.2 give the claim at row 8; the code was not re-tested there. *Fix:*
rerun `zk_view` (simulator acceptance, wire audit, `determined_values`) at row 8 on the current
format, then the decomposition of 18.12.3 (`S` at 16,430 views, `M_OO` at 24,998 of one witness).

**H-5 MINOR.** `zk-composition.md` §4.2 "below `2^-240`" and the review sheet row 18 should
state the count of events at the built shapes (A: about 30 dummy rounds, 11 bus layers, 52
gadget claims) and H-2's term. §4.3 "(U) W-6" is closed for A by `yugen-proof-a-zk` 18.1/18.4 and
should say so.

**H-6 NOTE.** A's announced sizes are public; the leaf program is straight-line
(`yugen-proof-a/docs/falcon-statement.md` l. 221, `statement-layout.md` l. 195,
`wallet1_vectors` asserts one cycle count), so they are constants of the statement. Item (b) of
18.1 is closed by that, not by the ZK tests.

**H-7 NOTE.** Timing (rejection loops, restart on a zero blend challenge, grinding) is outside
HVZK and not covered by any document here.

## 6. For the lead architect

There is no reason found to believe that a payment proof as built reveals anything about the
payment beyond its public inputs: every value on A's wire has a named pad or is determined, and
B's pads cover every opened symbol (192 distinct positions against 192 pad coefficients). The
claim is **not yet proven to the standard of the other rows**: for A the whole-view check at the
current row is outstanding (H-4); for B the documents of record describe a different system and
one blinding step is a sketch (H-1, H-3).

## 7. Not checked

The Binius64 Blueprint (Theorem 6.3, Lemma D.1, 7.2, 7.3); Lemma 1' and Theorem W's proofs line
by line (read for structure, matched by count); the GKR fraction layers (Lemma 4, A24) and the
bus Lemma 5 proofs; the Fiat-Shamir and QROM steps (Z-2's referee); Libra, CFW26 Definition 6.1
and SG26 Theorem 6.6 in rendered form; node circuits (hypothesis N); no code was run.
