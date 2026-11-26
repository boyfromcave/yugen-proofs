# Round census of system A's leaf (finding M-3)

Part of Yugen. 2026-11-19. Answers MAJOR M-3 of `theorem-s-referee.md` (`0a49234`): the
rounds of a system-A proof outside its opening were charged as one estimated count, `OTHER_ROUNDS = 512`
(`soundness/src/yugen_soundness/shipping.py`), with no per-round error written or charged. This document
lists every challenge the verifier draws for a row-8 leaf proof, in order, with the field it is drawn from,
the error of the round it closes and the source of that error; compares the count with the estimate; and
says, row by row, whether the per-round need is still met. Code: `soundness/src/yugen_soundness/census.py`;
input `soundness/census/a-round-census.json`; test `soundness/tests/test_census.py`; table
`soundness/output/census-tables.txt` (`yugen-soundness --census`). No certified count was changed.

Provenance. The census (the walk, the message-merge rule, the reconciliation with the measured counts) and
Lemma RS (section 2.6) are **Original (the Ycash developers, 2026)**, REFERENCES.md O-85 and O-86,
unreviewed. Each per-round error is labelled in section 2.

## 1. Method

**Verifier read.** `yugen-proof-a` at HEAD `15b9993`, read with `git show` (nothing run there):
`vendor/leanMultisig/crates/verifier/src/lib.rs` (`walk`, `read_ood`, `verify_stacked_opening`), `bus.rs`
(`verify_bus_balance`, `verify_gkr_grand_products`, `table_sumcheck`), `keccak.rs` (`verify_keccak`,
`verify_layer`, `open`), `ring_switch.rs`, `zk.rs` (`verify_gadget`, `flags`), `wi.rs` (`verify_wi`),
`whir.rs` (`verify_whir`, `sample_queries`), `transcript.rs` (`sumcheck`, `sumcheck_round_poly`),
`spbcs.rs` (`challenge`, the counters). The in-circuit verifier of the `e2` build is the same walk (the
`e2` crate is the twin package of this source with the 256-bit field, `lib.rs` header); its counts in
`bench/results/kq-report-20261119.txt` equal the native ones (445, 409), so it is not walked separately.

**What a round is.** Under the spBCS transcript (rows 6 to 9) a verifier message is one stream: a
challenge opens a stream if none is open and every following challenge reads the same stream until the
prover's next item closes it (`spbcs.rs` `challenge`, `item`). So consecutive draws with no prover item
between them are **one** message. Its round-by-round error is at most the sum of its draws' errors (the
draws are sub-steps of one transition; union bound). This merge matters: a masked GKR layer's combiner
and `rho` are one message; a Keccak layer's `beta` and the next layer's `rho` are one; the ring switch's
16 map challenges and the stacked opening's `lambda` are one.

**Field.** Every challenge is drawn in `E`, the row's challenge field: GF(2^256) for rows 6 to 9
(`params.rs`: `challenge_bits: 256`). Query positions are read from challenge words (`sample_queries`).
Below, an error "`a`" means `a / |E| = a / 2^256`.

**Check.** The walk is parameterised by the program's announced shape (bus depth 21, table sumcheck 17
rounds, `KECCAK` table `2^9` steps with a state every 2 rounds, gadget column `2^11`, 52 gadget claims, 2
constraint polynomials; sources in the JSON file). With these figures it gives **445** messages for the
masked row-8 leaf and **411** for the plain row-7 leaf, exactly the counts the built verifier reports for
those shapes (`kq-report-20261119.txt`, `j_v`), two independent configurations (masks on and off, W-I and
plain WHIR) of one parameter set. The test asserts both.

## 2. The errors and their sources

Statements read from rendered pages of the papers in the reference-paper collection (REFERENCES.md) with pypdfium2
(`.tools-venv`), 2026-11-19.

**2.1 Sumcheck rounds.** [XZZPS19] (Xie, Zhang, Zhang, Papamanthou, Song, *Libra*, ePrint 2019/317)
Section 2.3.1, Protocol 1, p. 8: the sumcheck of [LFKN] "is complete and sound with `eps = d l / |F|`",
`d` the variable degree, `l` the rounds. Used round by round (**Published**: [GKR15] proof of Lemma 2.5; `d` per round as the degree of that
round's polynomial; label amended 2026-11-19, `citation-check-lfkn-gkr.md` D-1, was Adapted): from a
false claim, a prover whose round polynomial `s` passes `s(0) + s(1) = claim` sent `s` different from the
true one, both of degree at most `d`, so they agree at a uniform point with probability at most `d/|E|`.
`d` per instance, as the verifier's own grind numerators state it (`round_bits(count - 1 + eq)`): bus GKR
rounds 5 (`eq` times four lines; 3 in the one-level layer, which has no rounds here), bytecode share 2,
table sumcheck 3 (+1: its challenges are also the `KECCAK` table's point coordinates, `bus.rs`
`const` assertion, charged 4), Keccak pack and segment rounds 3 (`eq` times degree 2), bit-position rounds
3, Keccak openings 2, the W-I tail 2. (Amended 2026-11-19, `citation-check-lfkn-gkr.md` D-1.) The per-round form is
the step of [GKR15] (Goldwasser, Kalai, Rothblum, J. ACM 62(4), 2015) Lemma 2.5, p. 27:21, proof
inequality (3), pp. 27:22-23 (any finite field, any `H`); its origin is [LFKN92] Lemma 4, p. 862
(J. ACM 39(4), 1992; permanent protocol, error `r/p` per step). XZZPS19 p. 8 restates it.

**2.2 Out-of-domain point of oracle 0 (`read_ood`, 22 coordinates).** Error **0** in unique decoding.
[ACFY24] (Arnon, Chiesa, Fenzi, Yogev, *WHIR*, ePrint 2024/1586) Lemma 4.25, p. 31: the probability that two
distinct codewords of the list agree at the out-of-domain points is at most `(l^2/2)(2^m/|F|)^s`, `l` the
list size. Under unique decoding (Theorem S's regime) the list has one element, so no pair exists. The
lemma is stated for smooth Reed-Solomon codes; the argument needed here is only "a list of one has no
pair" and holds for any code (**Original**, one line). The OOD value enters as one more stacked claim on
`Dec(O_0)`; a false value makes the claim set false and is caught by the opening.

**2.3 The bus fingerprint (`weights` (16), `beta`; one message).** Error `2^mu`, `mu = 21` the push depth:
**235 bits, the worst round outside the opening.** The push and pull products of
`beta + <weights, tuple>` over `2^mu` tuples each are polynomials of total degree at most `2^mu` in
`(weights, beta)`; distinct multisets of tuples give distinct polynomials (distinct monic linear factors),
so they agree at a uniform point with probability at most `2^mu/|E|` (Schwartz-Zippel). The verifier
states the same bound (`bus.rs`, `bus_grinding_bits`). **Original** as written here (the multiset
fingerprint is classical; no source for it is in the reference folder). Not checked here, and taken from
upstream as the referee's section 6 says: that the bus's balance with its count tree is equivalent to the
memory and bytecode consistency of the execution (leanVM's arithmetization). The bus is a grand-product
argument, **not logup**: no logarithmic-derivative step is in the code, so [Hab22] (logup) is not used.

**2.4 GKR layers (`verify_gkr_grand_products`, 11 layers).** Per layer: the combiner batches the three
trees' claims, degree `N_TREES - 1 = 2` in it (Schwartz-Zippel on a univariate of degree
`N_TREES - 1`, **Adapted** from [XZZPS19] p. 10's two-coefficient combination; amended 2026-11-19,
`citation-check-lfkn-gkr.md` change 4): error 2; the layer's sumcheck rounds
(2.1, error 5 each); `y` reduces the `2^step` claimed children of each tree to their multilinear extension
at `y`: two different child vectors give different multilinear polynomials in `step` variables, which
agree at a uniform `y` with probability at most `step/|E|` (Schwartz-Zippel; **Original** one line);
error `step`, doubled at the last layer, whose `y` are also the zerocheck's first coordinates (the
verifier's own grind numerator, `bus.rs`). (Amended 2026-11-19, `citation-check-lfkn-gkr.md` D-2.) [GKR15] Theorem
3.1, proof in Section 3.3, pp. 27:31-32, charges each layer its sumcheck (`6 m delta/|F|`) plus
the two-to-one claim reduction (`m delta/|F|`, by a line, p. 27:31) and takes the union over
layers; the census follows the same per-layer structure. The combiner by powers and the `y`
reduction are not GKR15's mechanism (Adapted / Original as stated); the product-tree layers are
not GKR15's circuit form (Thaler 2013, not in the folder).

**2.5 Keccak reduction (`verify_keccak`, 12 layers, two openings).** The first message (segment bit and 5
lane bits): the first claim is multilinear in them, error 6. Per layer: `s`, the evaluation point of the
claimed product polynomial of degree `PRODUCT_BITS - 1 = 46`: a wrong polynomial agrees with the true one
at at most 46 points, error 46; the pack and segment rounds and the 11 bit-position rounds (2.1); `beta`,
which combines the three claims `t_0, t_1, t_2` quadratically, error 2. The openings: sumchecks of degree 2
(2.1). All **Original** one-line Schwartz-Zippel arguments over the verifier's own polynomials; the
correctness of the reduction (that the layer identity is Keccak's round function, `RMFE_EMBED`,
`RMFE_PROJECT`) is upstream's and not checked here.

**2.6 Ring switch (16 challenges `f_p`, `g_b`).** **Lemma RS (Original, the Ycash developers, 2026).** Let
`x` generate `K = GF(2^64)` over GF(2) (the verifier's `GEN`) and let the 64 slice claims be off by a
nonzero vector `d` in `E^64`. The verifier's target `sum_i x^i Phi(s_i)`, with `Phi(v) = sum_p f_p
Psi(v)^(2^(8p))`, `Psi(v) = sum_b g_b v^(2^b)` (`ring_switch.rs`), is unchanged by the error with probability
at most `2/|E|`. *Proof.* The change is `P(f, g) = sum_p f_p B_p(g)`, `B_p(g) = sum_b g_b^(2^(8p)) A_(8p+b)`,
`A_k = sum_i x^i d_i^(2^k)`. If every `A_k` (`k < 64`) were 0, then applying the inverse Frobenius,
`sum_i y^i d_i = 0` for the 64 conjugates `y` of `x`, which are distinct; the Vandermonde system forces
`d = 0`. So some `B_p` has a nonzero coefficient, and `B_p(g) = (sum_b g_b A_(8p+b)^(2^(-8p)))^(2^(8p))`
vanishes exactly when a nonzero linear form in `g` does: probability `1/|E|`; given `B_p(g) != 0`, `P` is a
nonzero linear form in `f`: `1/|E|`. ∎ Relation to prior work: the ring switching of [DP24] (Diamond,
Posen, ePrint 2024/504, Construction 3.1, Theorem 3.5) is a different reduction (tensor algebra); this one
is leanVM's own, and no published error for it was found in the folder or the vendored documents. The
weight's correctness (completeness) is upstream's.

**2.7 Batching challenges.** `xi` (table sumcheck): `n_constraints + N_TREES = 5` claims batched by powers,
error 4; `lambda` (stacked opening, same message as the ring switch): at most `MAX_STACKED_CLAIMS = 512`
claims with the gap of the blinder blocks (`lib.rs` refuses more), error at most 511; the public-input
challenge: each memory limb's claim is a line in it, error 1. Schwartz-Zippel on a univariate.

**2.8 Zero-knowledge rounds.** `rho` of every masked instance (1), the dummy rounds (bus 4, table 2, Keccak
layers 2, slices 1) and the gadget's `theta` (51), `c` (1), `z` (11): as the calculator lists them
(`wi.zk_rounds`), proved in `zk-wi-soundness.md` Lemma 6 and section 6.3 and `zk-system-a-gaps.md` 3.5, 11
(not re-refereed here).

**2.9 The opening (33 messages).** Theorem S's table (`zk-wi-soundness.md` 5.1, with the tail rows of
amendment m-1): `rho_i`, the fold rounds (the pair `(alpha, beta)` is one message), the positions with
`lambda`, `c`, the last positions, the tail. These are the 33 rounds `wi.rounds(c, "A")` lists; the query
rounds bind (157.48 bits at row 8, mode 0, rate 1/4).

## 3. The census of a row-8 leaf (mode 0, `2^22`, rate 1/4)

In verifier order; "msgs" verifier messages, "draws" challenges; error per message in units of `1/|E|`.

| Group (code) | Msgs | Draws | Error per message | Bits (worst) | Source |
|---|---|---|---|---|---|
| OOD of oracle 0 (`read_ood`) | 1 | 22 | 0 | - | 2.2 |
| bus fingerprint (`weights`, `beta`) | 1 | 17 | `2^21` | **235.00** | 2.3 |
| bus GKR: combiner + `rho` (first layer) | 1 | 2 | 3 | 254.4 | 2.4, 2.8 |
| bus GKR: `y` + next combiner + `rho` | 10 | 39 | 4 or 5 | 253.7 | 2.4, 2.8 |
| bus GKR: sumcheck rounds | 100 | 100 | 5 | 253.7 | 2.1 |
| bus GKR: dummy rounds (A24) | 11 | 11 | 4 | 254.0 | 2.8 |
| bus GKR: last `y` | 1 | 2 | 4 | 254.0 | 2.4 |
| bytecode share sumcheck | 4 | 4 | 2 | 255.0 | 2.1 |
| table: `xi` + `rho` | 1 | 2 | 5 | 253.7 | 2.7, 2.8 |
| table sumcheck rounds | 17 | 17 | 4 | 254.0 | 2.1 |
| table dummy (A21) | 1 | 1 | 2 | 255.0 | 2.8 |
| public challenge + Keccak segment and lane point | 1 | 7 | 7 | 253.2 | 2.7, 2.5 |
| Keccak: layer-0 `rho`, input-opening `rho` | 2 | 2 | 1 | 256.0 | 2.8 |
| Keccak: `s` (12 layers) | 12 | 12 | 46 | 250.48 | 2.5 |
| Keccak: pack/segment rounds (6 a layer) | 72 | 72 | 3 | 254.4 | 2.1 |
| Keccak: bit-position rounds (11 a layer) | 132 | 132 | 3 | 254.4 | 2.1 |
| Keccak: dummy rounds (12 layers, slices) | 13 | 13 | 2 or 1 | 255.0 | 2.8 |
| Keccak: `beta` + next `rho` | 12 | 24 | 3 | 254.4 | 2.5, 2.8 |
| Keccak: output and input openings | 16 | 16 | 2 | 255.0 | 2.1 |
| gadget `theta`, `c`, `z` | 3 | 13 | 51, 1, 11 | 250.33 | 2.8 |
| ring switch + stacked `lambda` | 1 | 17 | at most 513 | 247.00 | 2.6, 2.7 |
| **outside the opening** | **412** | **525** | sum `2^-235.00` | 235.00 | |
| W-I opening | 33 | 48 | Theorem S | 157.48 | 2.9 |
| **total** | **445** | **573** | | | |

The plain row-7 leaf (no masks, plain WHIR) has 382 messages outside the opening (no `rho`, dummy or
gadget messages; the GKR layers 112, the table 18, Keccak 244) and 29 in it (the folds, an OOD point and
the queries per level, the final queries, the 7-round tail): 411.

## 4. Census against the estimate; every row's need

**Count.** The estimate charges a leaf `87 + 512 = 599` messages (`N_msg = 1,198` with the prover's
messages); the census gives **445** (row 8, mode 0; `N_msg = 890`), 409 (mode 1), 411 (row 7). The unmasked
rounds the estimate stands for are **358** messages (445 less the opening's 33 and the 54 the calculator
lists for the zero-knowledge rounds; after the merges, 30 messages carry only zero-knowledge
challenges). So the estimate is **above** the census for every leaf, by 154 messages (26%). For the node
(row 9) it is **below**: at `2^27` the built verifier counts 592 messages against `31 + 512 = 543`
(finding K-1 of `yugen-proof-a` `docs/parameters.md` 2.2b), 561 outside the listed rounds.

**Errors.** Every round outside the opening has a written error; the worst is the bus fingerprint at 235.00
bits, and all 412 together are below `2^-234.99`. Against a need of about 157.4 bits these rounds have 77
bits of room; they cannot bind. The referee's concern was the count, which sets the need.

**Rows** (category 1, 20,000 proofs, the default convention EVERY t; `output/census-tables.txt`). The
census changes `k_q` by `4 (census - estimate)` (`k_q = 2 N_msg + ...`, `N_msg = 2 x messages`). M:
measured at the shape; D: the measured walk outside the opening plus this shape's opening; E: row 9 at a
stack with no measured proof. The linear extrapolation that filled the E rows is **withdrawn** (revision
2026-11-19, referee M-A2): the two measured nodes are different programs, so no count follows for another
stack.

| Row | Messages est. / census | Margin est. / census (bits) | Meets with the census |
|---|---|---|---|
| row 6, mode 0, `2^22`, 1/4 | 599 / 445 (D) | +0.307 / +0.357 | yes |
| row 6, mode 1, `2^20`, 1/4 | 594 / 404 (D) | +0.029 / +0.113 | yes |
| **row 8, mode 0, `2^22`, 1/4** | 599 / 445 (M) | +0.106 / +0.158 | **yes** |
| **row 8, mode 0, `2^22`, 1/2** | 599 / 445 (D) | +0.019 / +0.062 | **yes** |
| row 8, mode 1, `2^21`, 1/4 | 599 / 409 (M) | +0.258 / +0.321 | yes |
| row 8, mode 1, `2^22`, 1/2 | 599 / 409 (D) | +0.019 / +0.072 | yes |
| row 7, `2^22`, 1/4 | 531 / 411 (M) | +0.192 / +0.234 | yes |
| row 9, `2^25`, 1/2 and 1/4 | 539 / 501 (M, D) | +0.287 / +0.294; +0.002 / +0.010 | yes |
| row 9, `2^27`, 1/2 and 1/4 | 543 / 592 (M, D) | +0.098 / +0.090; +0.289 / +0.281 | yes |
| row 9, `2^24`, `2^26` (both rates) | 539 / not measured (E) | +0.001 to +0.499 / - | unknown |
| row 9, `2^28`, `2^29`, `2^30` (both rates) | 543 to 547 / not measured — refused by the build above `2^27` | +0.003 to +0.146 / - | not admitted |

The referee's figures (margins 0.91 / 0.67 bits) are the book need (`t >= k_q`, non-default) at the
counts 227/161/164/180 and 375/169/175/220. On that convention the census lowers row 8's need from 152.52
to 152.09 bits (`round_need(1, 445)`), so those margins grow by 0.43 bits.

**Row 9 above `2^27` (revised 2026-11-19, referee M-A2).** The first revision gave counts for the E rows
by a line through the two measured nodes (501 at `2^25`, 592 at `2^27`) and found `2^30` missing by 0.018 /
0.022 bits on 727 messages. That count is withdrawn: 501 is `node-row9-sub1` (S of one leaf) and 592 the
merge of seven, two different programs; a node's messages outside its opening are set by its program's bus
depth, table and Keccak shape, not by the stack's log, so 727 bounds nothing in either direction. The rows
`2^28`, `2^29` and `2^30` are now **not measured — refused by the build above `2^27`**: system A's row-9
setup refuses (`NoSchedule`) a stack above `2^27` (the builder is adding that refusal; until it lands, the
schedule's "60 admitted" in `yugen-proof-a` `docs/parameters.md` 2.6 overstates what is certified for row
9 above `2^27`). Every tree node is built at `2^27` (`yugen-proof-a` `docs/recursion.md`), where the measured
count holds by +0.090 bits. `2^24` and `2^26` are unknown until measured. Before any of these shapes is
admitted, `j_v` is measured on a proof of that shape and entered here; if it misses, `census.restore` gives
the fewest added queries (a query adds about 0.415 bits at rate 1/2 and 0.678 at 1/4). The earlier restored
query lists were calibrated to 727 and are withdrawn with it. Rows 6 and 8 need no change: the census only
lowers their need.

The certified counts and statuses are untouched (`OTHER_ROUNDS` stays 512; the calculator's `k_q` guard
and the T-1 reports are the route by which a measured count enters a certified row,
`hashterm.REPORTED_KQ`, which this work does not fill).

## 5. Papers

Used, read from rendered pages in the folder: [XZZPS19] (2019-317) pp. 8 to 10; [ACFY24] (2024-1586) Lemma
4.25, p. 31; [DP24] (2024-504) Construction 3.1 named for comparison only; [SG26] (2026-2615) Definitions
2.20, 2.24, Lemma 2.21, pp. 14 to 16 (for `lemma-k-a.md`). Also used, read from rendered pages (amended 2026-11-19,
`citation-check-lfkn-gkr.md`): [LFKN92] (146585.146605) Lemma 4, p. 862, proof of Theorem 1 pp. 863-864;
[GKR15] (2699436, the journal version; key was [GKR08]) Lemma 2.5 and Figure 2, pp. 27:21-23; Theorem 3.1
and Section 3.3, pp. 27:25, 27:31-32. **Not in the reference-paper collection (REFERENCES.md)** and not
used beyond what is said: [Hab22] logup (not used: the bus is a grand product), BCIKS20 (ePrint 2020/654: Theorem S
rests on it; the referee read a scratch copy; the lead should place it in the folder), leanVM's own
specification (none is vendored; the code is the source).

## 6. What a referee should check first

1. The merge rule (section 1): that the spBCS stream makes consecutive draws one message, so that the
   count of `k_q` is the message count and a merged message's error is the sum.
2. Lemma RS (2.6), in particular that `GEN` generates `GF(2^64)` (its 64 conjugates distinct).
3. The degree of each round against the code (the verifier's grind numerators are the code's own statement).
4. (Withdrawn 2026-11-19, M-A2: the E counts are no longer given.)

## Revision 2026-11-19 (after `knowledge-and-census-referee.md`)

- M-A2: the extrapolated row-9 counts are withdrawn (section 4); rows above `2^27` are "not measured —
  refused by the build above `2^27`", `2^24` / `2^26` unknown. `census.py` returns no count for them and
  `output/census-tables.txt` is regenerated. No certified count changed; measured and derived rows are as
  before.
- m-A3: the "Draws" column (section 3) is taken from `census.py`'s output: the bus `y` row draws 39 (step 1
  after the odd first layer, 2 after the others), the Keccak `beta` row 24. The rows now sum to the 525
  stated; messages and errors are unchanged.
- N-2: the bus combiner is powers of one challenge, so its error 2 (2.4) is Schwartz-Zippel on a univariate
  of degree `N_TREES - 1`, **Adapted** from [XZZPS19] p. 10's two-coefficient form.
