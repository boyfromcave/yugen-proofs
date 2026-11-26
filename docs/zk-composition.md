# Zero knowledge of a whole leaf proof: composition and Fiat-Shamir

Part of Yugen. This document composes the masked sumcheck (`zk-masked-sumcheck.md`,
"the lemma document") and the hiding opening (`zk-hiding-commitment.md`, "the commitment
document") into a simulator for a complete leaf proof of each system, states the Fiat-Shamir
step, and ends with an implementation checklist and a review sheet.

Status tags: **(P)** proven on paper here or in the two documents named; **(C)** checked by exact
computation in `zk-lemma/` or `zk-commit/`; **(S)** read in a primary source; **(M)** from
memory, not verified; **(U)** open.

Provenance (citation audit of 2026-11-19; `../REFERENCES.md`). Published and used: the
compilation theorem of section 6 (ePrint 2016/116, Theorem 7.1, Lemma 7.5). Adapted: the layer
blinding from Libra (ePrint 2019/317, Section 4.2, equation (7)); **blinder cells and Theorem B**
(relabelled 2026-11-19, `../REFERENCES.md` O-8, fourth pass), from Sharp and Grubbs, ePrint
2026/2615, Section 5.4.2, Lemma 5.8 (a uniform pad held in the oracle input masks each sent
element, and a linear claim on the pads is handed to the commitment); changes here: one committed
cell per revealed evaluation instead of one pad per sent element, multiplied by the public factor
`Z = r_y (1 + r_y)` of a dummy variable so that the pad rides the existing sumcheck claim, and no
committed products of pads. Original (the Ycash developers, 2026) as far as checked: the pad
ledger and Theorem C. A published
composition theorem for honest-verifier zero-knowledge reductions that accounts for later
queries to earlier oracles exists (ePrint 2026/391, revision of 2026-11-16, Theorem 4.7 with
Definitions 4.3, 4.5, 4.9, 4.10); it was **not read**, and Theorem C was not compared with it.

**Scope after the HVZK referee (`hvzk-referee.md`, `8d3516a`, finding H-1; revised 2026-11-19).**
Theorem C (section 4) covers **system A only**. System B as built (`yugen-proof-b2`) is not the
"Plonky3 binary" stack with opening W-M that earlier revisions of this document described: it is
Binius64's own zero-knowledge mode (one-time-pad keys, an IronSpartan wrapper, a low-coefficient
pad on a linear domain, one batched BaseFold opening). It is covered by **Theorem C-B** (section
5.2), whose ledger is rows M1 to M12 of the B review (`yugen-proof-b2/docs/zero-knowledge.md`
section 1.2). Provenance for B: the pad encoding lemma is **Adapted** from Chiesa, Fenzi,
Weissenberg, *Zero-Knowledge IOPPs for Constrained Interleaved Codes*, ePrint 2026/391 (revision
of 2026-11-16), Lemma 3.29 (p. 38; changes: the novel basis `X_0..X_(q-1)` in place of the
monomials `X^0..X^(q-1)`, which span the same space of polynomials of degree below `q`;
*amended 2026-11-19, `zk-b-referee.md` F-5:* `deg X_j = j`, so every prefix `X_0..X_(s-1)`, `s <= q`,
spans the polynomials of degree below `s` (degree-triangular), and the proof of Lemma 3.29, which
separates the first `s` coefficients, runs unchanged); the
opening simulator is **Published**: Diamond, *Zero-Knowledge Polynomial Commitment in Binary
Fields*, ePrint 2025/1015, Construction 4.1 and Theorem 4.3 (pp. 5-6); the masked
multilinear-extension check is the Binius64 Blueprint's Theorem 6.3 (an upstream design document,
not a refereed paper; read by the B team, not by this document's authors); Lemma DC and Corollary
DC (the dummy-constraint blinding, N3 and N8 of the B review) are **Original (the Ycash
developers, 2026), draft until refereed**, first written here.

Result in one paragraph. A leaf proof is a sequence of components, each of which reveals only
(a) values padded by randomness that is fresh, independent and used for that one purpose, and
(b) values the verifier's own equations determine from (a). Given that, the whole algebraic view
is simulated by sampling each padded block uniformly in protocol order and computing the
determined values (Lemma T of the commitment document) (P). The one evaluation `f(r)` that the
sumcheck simulator needs is made simulatable by **blinder cells**: every revealed evaluation of
committed data is `chat = c(r) + Z b` with a dedicated uniform committed cell `b` and a public
nonzero `Z` from a dummy variable, so the simulator samples `chat` and computes `f(r)` from it,
and the opening proves one linear relation with a public target (P; C at toy size). The
interactive protocol is honest-verifier zero-knowledge with a statistical error that is a sum of
excluded-challenge events of size `O(1)/|F|` each; the non-interactive proof is zero-knowledge in
the programmable random-oracle model by the standard argument for public-coin protocols with
salted Merkle commitments (M for the cited theorem; the conditions are listed in section 6).

---

## 1. Components of a leaf proof

Both systems have the same skeleton. The names in the right column are the system-specific
instances; matching each to the abstract form is work item W-6 of the lemma document and is not
done here.

| # | Component | System A (leanVM) | System B (Binius64 zero-knowledge mode, as built; section 5.2) |
|---|---|---|---|
| 1 | witness commitment | one stacked polynomial of `GF(2^64)` cells | round oracle 0: the inner trace `pi` and the key vector `z_pre` merged, each round oracle committed next to a uniform mask `w_r` of equal length (M1), with a pad on coefficients `0..q` (M2) |
| 2 | constraint sumcheck (zerocheck) | VM transition constraints | inner Binius64 protocol, every message one-time padded (M7, M8); IronSpartan's masked check of `a b - c` over the wrapper's R1CS (M9) |
| 3 | layered arguments (GKR) | Keccak-f by GKR | inside the inner protocol, padded by keys (M7) |
| 4 | cross-table values | bus terminals | wrapper products `(a, b, c)` and `s_pre`, blinded by dummy constraints (M10, M11; Lemma DC) |
| 5 | auxiliary reductions | stacking / claim batching | the wiring claim (public, B review 1.3), the mask evaluation `g(r)` (determined, M12) |
| 6 | opening | WHIR with the affine combiner, hiding by W-I | one batched ZK BaseFold on `M^gamma = w + gamma M` on a linear domain (M4 to M6) |

(S for the row labels: framework selection, section 3; the pinned verifiers' module lists. The
prover-side details of rows 2 to 5 in either stack were not read for this document.)

---

## 2. What is committed, and the order of messages

### 2.1 The first oracle

Besides the trace, oracle 0 of the hiding opening (construction W-I) holds, as ordinary message
entries:

| Region | Content | Size |
|---|---|---|
| blinder column `Bl` | one uniform `F`-element per revealed evaluation of committed data (section 3) | number of revealed evaluations, times `[F : K]` alphabet cells |
| mask column `A` | all sumcheck masks of components 2, 3, 5 (staircase or Libra-in-eq coefficients), the GKR layer blinders, and at least one pad element | `N` = total coefficients, padded to a power of two with at least one pad |
| gadget column `B` | uniform, same length as `A` (lemma document 5.3) | same |
| bus mask payloads | one uniform payload per neighbouring table pair, one self-cancelling pair per table that publishes a denominator; inside the tables' own rows | `T - 1` (+ `T`) |
| opening aux rows | the fold-batch mask of level 0 | `1 + 2 kappa_0` or `1 + 4 kappa_0` rows |
| encoding randomness | `t_0 = Q_0 + o_0` per lane, at an aligned offset | `2^kappa_0 t_0` |

Later oracles hold their own aux rows and encoding randomness; the last one holds the base-case
mask column (commitment document 6.1). All leaves of all trees are salted.

### 2.2 Order

    0. root of oracle 0
    1. zerocheck:        tau;  G_z;  rho_z;  masked rounds over (y, x) with challenges (r_y, r);
                         blinded column evaluations chat_i(r_y, r)
    2. buses:            bus challenges;  per-table terminals (masked by the payloads)
    3. GKR chains:       per layer: Gtilde (in place of G), rho, masked rounds, blinded layer claims;
                         at the bottom layer the blinded claims are blinded column evaluations
    4. other reductions: each as a masked sumcheck ending in blinded evaluations
    5. opening gadget:   theta (batching of the linear claims on A);  beta;  c;  u = B + c A;  z;
                         the evaluations A(z), B(z)
    6. batching:         lambda;  one relation  <p, W> = T  over oracle 0 with public T
    7. hiding opening W-I (commitment document 6.1), ending in the base case

Every prover message is absorbed before the next challenge is drawn. The masks, blinders,
payloads, `B` and the pads are fixed by step 0, before any challenge: this is what soundness of
the masked sumchecks needs (H6 of the lemma document), and it is why the opening's own masks,
whose final-value weights depend on challenges drawn in step 7, are handled inside the opening
(aux rows) and not by the gadget of step 5.

---

## 3. The value handed to the sumcheck simulator: blinder cells

The simulator of the masked sumcheck (lemma document Theorem 2, variant O) is given `f(r)`. In a
zerocheck `f(r) = C(c_1(r), .., c_m(r))` and the column evaluations are sent to the verifier.

**Construction.** Add one dummy variable `y` to the sumcheck. For each committed column `c_i`
whose evaluation the component reveals, with blinder cell `b_i`:

    chat_i(y, x) = c_i(x) + y (1 + y) b_i .

`chat_i = c_i` at `y in {0, 1}`, so every identity over the cube is unchanged:
`sum_{y, x} eq((tau_y, tau), (y, x)) C(chat(y, x)) = sum_x eq(tau, x) C(c(x))`. The sumcheck has
one more round, of degree `2 deg C` in `y` (the mask families of the lemma document take any
degree profile). At the end the prover sends `chat_i(r_y, r)`; with `Z = r_y (1 + r_y)` the
claim on committed data is

    c_i(r) + Z b_i = chat_i(r_y, r) ,

linear in the committed vector, with a public right-hand side. A column evaluated at several
points (current row, next row; `(r, 0)` and `(r, 1)` under a GKR chain) has one cell per point.
The bottom layer of a GKR chain is the same construction: lemma document 7.2 with the two layer
blinders taken from `Bl`.

**Theorem B (P; C).** If the cells are uniform, independent of everything else, each used in one
revealed value, and `Z != 0`, the revealed values `chat_i` are uniform and independent, and the
view (masked round messages, `chat`) of the sumcheck equals the output of: sample every `chat_i`
uniformly, run the simulator of Theorem 2 with `f(r) := C(chat)` (times the eq factor in the
unreduced form). The excluded event `r_y in {0, 1}` has probability `2/|F|`.

*Proof.* Lemma T with two blocks. Block 1: the values `chat_i = c_i(r) + Z b_i`, pad `b`, space
everything (`Z != 0`). Block 2: the round messages; the summand `C(chat(y, x))` depends on `b`
(earlier pad) and on the witness, the mask is the block's own pad, and by Theorem 1 the messages
are uniform on the sequences that pass the round checks and end in `rho C(chat(r_y, r)) + g(r)`;
that space is a function of block 1 and public data. ∎

Computation (C, `zk-commit/results/blind.txt`, part B): booleanity constraint `C(c) = c (1 + c)`,
one Boolean column of two rows, eq-weighted zerocheck over `(y, x)` with Libra's mask inside the
eq factor, GF(4), three `tau`, all `r`, `rho in {1, 2}`: over every mask (`4^7`) and every
blinder, the view's distribution is the same for all four Boolean columns in all 48 cases with
`r_y` outside `{0, 1}`; it differs in all 48 cases with `r_y in {0, 1}` and in all 96 cases with
the blinder off.

**Why cells and not blinding rows.** Appending uniform rows to a column makes its evaluation
`c(r) + sum_s eq(r, x_s) row_s` uniform only if the weights `eq(r, x_s)` span the challenge field
over the column's alphabet. For bit columns and `F = GF(2^256)` that needs 256 weights that are
`F_2`-independent; 256 uniform elements of `GF(2^256)` are independent with probability about
0.29 (M: the limit of `prod (1 - 2^-i)`), so each evaluation would need 256 rows plus a
statistical margin, for every column and point, and a rank bound over the challenge
(`yugen-zk-b` T-3). A cell is a field element used once: no rank condition, the same number of
random bits. The cells are addressed in the opening by a structured weight: with batching
challenge `lambda`, the relation carries `Z * <Bl, (lambda^i)_i>`, whose multilinear weight is a
product formula.

---

## 4. The composed simulator

### 4.1 Pad ledger

Each row is one view block. "Determined" entries are computed by the verifier's equations.

| # | View block | Pad (uniform, independent, used once) | Law of the block | Reference |
|---|---|---|---|---|
| 1 | bus terminals | bus mask payloads | uniform on the variety the public bus check defines; statistical `(T - 1)/|F|` in the message form | lemma document Lemma 5 |
| 2 | published denominators | self-cancelling payloads | uniform nonzero | Lemma 5 |
| 3 | blinded evaluations `chat` of every component | blinder cells | uniform; needs `Z != 0` per dummy variable | Theorem B |
| 4 | blinded GKR layer claims | layer blinders (in `A`) | uniform; needs `Z != 0` per reduction | lemma document Lemma 4 |
| 5 | round messages and `G` / `Gtilde` of every masked sumcheck | that sumcheck's mask (in `A`) | uniform on the sequences passing the round checks; final mask value determined | lemma document Theorems 1, 2; Corollary B for eq-weighted |
| 6 | gadget: `u`, `A(z)`; determined: `beta`, `B(z)` | `B`, the pad of `A` | uniform; needs a pad weight nonzero at `z` | lemma document Lemma 3 |
| 7 | opening, per level: `G_i`, fold-round messages | aux-row mask of level `i` | uniform on the passing sequences | commitment document Lemma S |
| 8 | opening, per level: out-of-domain answers, opened rows | encoding randomness `r_i` | uniform | commitment document Lemmas E, O |
| 9 | base case: `P*`; determined: `mu`, mask column at the opened rows | `gt` | uniform | commitment document Theorem W |
| 10 | Merkle roots, salts, sibling digests | salts | simulated from opened leaves only | commitment document Lemma M |

### 4.2 Theorem

**Theorem C (system A; P, given the per-block statements).** Fix all challenges of the interactive protocol
of section 2.2 outside the excluded events (below). Suppose every pad of the ledger is uniform,
independent of the witness and of every other pad, and enters no view block listed above its own
row. Then the algebraic view (blocks 1 to 9) is distributed as the output of

    Sim(public input, challenges):
      1. terminals: a uniform point of the bus variety; denominators uniform nonzero.
      2. for every component, in protocol order:
           blinded evaluations and blinded layer claims  <- uniform;
           round messages  <- the sumcheck simulator (lemma document 4.1, 7.3), with the claimed
           value taken from the public input or from earlier simulated values, and the final value
           computed from the blinded evaluations;  the mask's final value is determined.
      3. gadget: u uniform, A(z) uniform; beta := <u, w> + c v, B(z) := u(z) + c A(z), with v the
         batched mask values determined in step 2.
      4. T := the batched right-hand sides (blinded evaluations, A(z), B(z)): public.
      5. opening: the simulator of Theorem W on the claim (W, T).

and the full view is obtained by building the Merkle trees over the simulated opened leaves and
uniform digests elsewhere (Lemma M). The simulator uses no witness.

*Proof.* Lemma T with the blocks ordered 1, 2, 3, 4, 5, 6, 7/8 per level, 9. For each block the
ledger names the pad and the cited statement gives `Im B_i` equal to the direction space of the
block's affine set, for every value of the earlier randomness. It remains to check that no pad
occurs in an earlier block: payloads occur in the trace rows, hence in every later block, not
earlier; cells occur in blocks 3 (own), 5 (through the summand), 8 (as entries of oracle 0); the
masks and layer blinders in `A` occur in 4, 5 (own), 6, 8; `B` in 6 (own), 8; aux masks in 7
(own), 8, 9; `r_i` in 8 (own), later levels' 7 and 8, and 9; `gt` in 9 only. The affine set of each
block is a function of earlier blocks and public data: the heads of the sumchecks are public
inputs or earlier blinded claims; the opening's target `T` is a function of blocks 3 and 6. ∎

Excluded events for an honest verifier, each added to the statistical distance:

| Event | Probability | Where |
|---|---|---|
| a dummy-variable challenge in `{0, 1}` | `2/|F|` per sumcheck with blinded evaluations or layer claims | Theorem B, Lemma 4 |
| a bus payload equal to the bus challenge | `1/|F|` per payload | Lemma 5 |
| the gadget's pad weight zero at `z` | at most `log2(len A)/|F|` | Lemma 3 |
| an out-of-domain point inside the ambient subspace | 0 if the verifier samples outside it | Theorem W |
| **(H-2)** the shared pad of the level-0 out-of-domain value and of `A(z)` fails to have full `K`-rank | **not proven** (amended 2026-11-19, `zk-b-referee.md` F-4): under investigation in system A's build (rank check after `z`, restart below 8); the uniform-model figure below is withdrawn as a bound | section 4.2a |

**4.2a The `GF(2^64)`-rank term (finding H-2; R, draft until refereed).** *Amended 2026-11-19
(`zk-b-referee.md` F-4, MAJOR): this term is **not proven** — under investigation in system A's
build (rank check after `z`, restart below 8).* The weights are `K`-coordinates of `eq(z, cell)`,
tensor-structured functions of one point `z`, not independent uniform entries, so the union bound
below does not apply; if both revealed values use the same point and per-cell weighting the rank
is at most 4 identically. The fix to be built: the prover computes the matrix's `K`-rank after `z`
is drawn and restarts if it is below 8 (a public-coin restart, error 0 in `eps_hvzk^A`, counted in
the soundness ledger's restarts), with a test that samples `z` at the built shape and expects rank
8. The text below is the withdrawn uniform-model reasoning, kept as a record. System A's level-0
out-of-domain value is `mle(stack, z)` over `K = GF(2^64)` cells and its pad is the spare part of
column `A`, which is also the pad of the gadget's `A(z)` (row 6). Both revealed values lie in
`F = GF(2^256)`, a `K`-space of dimension 4, so together they are a `K`-linear image of the spare
cells in `K^8`, read through the `F`-valued weights `eq(z, cell)`. They are jointly uniform, given
everything earlier, exactly when that `8 x c` matrix over `K` has rank 8; otherwise a `K`-linear
functional of the two values is a function of the witness. This is a `K`-event, not an `F`-event.
Bound: for a uniform `8 x c` matrix over `K`, `Pr[rank < 8] <= sum_(i=0..7) |K|^(i-c) <=
|K|^(8-c) / (|K| - 1)` (union over the nonzero functionals of `K^8`, counted by the rank of the
row they kill). The weights are structured, not uniform; the uniform model is the referee's (R)
and is not proven for `eq` weights. **At the built shape** (104 spare elements of `F` in `A`, `c =
416` cells), under the unproven uniform model only: `|K|^(8-c)/(|K|-1)` (the referee's `<= 2^-6000` is a weaker bound of
the same term). With exactly two spare elements (`c = 8`): `~2^-64`, which fails the target.
**Minimum spare-cell count for `eps_rank < 2^-165`:** `64 (c - 7) >= 166` gives `c >= 10` cells, that
is **3 spare `F`-elements (12 cells)**. Because the uniform model is not proven for the structured
weights, the build asserts the referee's margin: **`Region::with_slices` must refuse (or pad) a
layout with fewer than 18 spare elements (72 cells = 8 + 64) in `A`**, and a test must show that a
shape with `masks + 2 = 2^k` is refused or padded. Responsible for the assertion: system A's builder
(`yugen-proof-a-zk`); not built at the time of writing (U).

**Event counts at the built shapes (finding H-5).** System A, wallet statement, row 8
(counts from the referee's reading of `yugen-proof-a-zk`; the soundness tool counts slightly more,
`yugen-proof-a-zk` A17: 11 bus layers against 10, gadget `2^12` against `2^10`; the larger counts
are used):

| Event | Count | Each | Sum |
|---|---|---|---|
| dummy-variable challenge in `{0, 1}` | about 30 dummy rounds | `2/|F|` | `60/|F|` |
| bus layers (payload or layer dummy events) | 11 | `2/|F|` (bound) | `22/|F|` |
| gadget pad weight zero at `z`, counted once per claim on `A` | 52 claims | `log2(len A)/|F| = 12/|F|` | `624/|F|` |
| out-of-domain point in the ambient subspace | 0 (rejection sampled) | 0 | 0 |
| **total `F`-events** | | | `706/|F| < 2^-246.5` |
| H-2 rank term | 1 | | **not proven** (F-4; rank check after `z`, restart below 8, under investigation) |

So, *if the rank term is closed by the restart (F-4, not proven yet)*, `eps_hvzk^A <= 2^-246.5` (R), below the `2^-240` stated before and below the `2^-165` the
security profile needs (`decision-security-profile.md` 2.1). For system B see Theorem C-B
(section 5.2).

### 4.3 What the composition does not cover

- Matching each sumcheck of each pinned stack to the form of the lemma document (W-6): **closed
  for system A** by `yugen-proof-a-zk` `docs/zero-knowledge.md` 18.1 and 18.4 (the per-sumcheck
  table and the wire audit `every_value_on_the_wire_is_a_hash_public_determined_or_masked`;
  `hvzk-referee.md` H-5). For system B W-6 does not apply in this form: B's ledger is rows M1 to
  M12 (section 5.2).
- (U) Values a stack publishes that are not in the ledger. A value is safe only if it is in a
  block with its own pad or is determined by the verifier's equations; the list of everything on
  the wire must be produced from the code and checked against the ledger (checklist item 12).
- (U) Fraction (logarithmic-derivative) layers: construction stated in the lemma document, not
  tested.
- The simulator is for an honest verifier. Malicious-verifier zero knowledge of the interactive
  protocol is not claimed and is not needed for the Fiat-Shamir proof.

---

## 5. Per family

### 5.1 System A

**System A (opening: W-I).** Each mask coefficient sits in the last lane only, above `kappa` guard slots
(soundness document F-1; zero knowledge: commitment document 6.2a). Fold rounds use the affine combiner: masks by Theorem 1' with the round space
`span{1, a, a^2, b, ab}`, `lam(q) = [1]q + [a]q`, `u = 1`: `1 + 4 kappa` coefficients per batch
(C for the mask; (U) inside the composed opening). The high part of each level is not sent; it is
carried into the next oracle (commitment document 3.2, 6.1). The final sumcheck over the low part
is replaced by the base case. Keccak-f by GKR: lemma document section 7 per layer, bottom-layer
claims through blinder cells. Out-of-domain samples, if the schedule keeps them: budget
`t = Q + o`, points outside the ambient subspace.

### 5.2 System B as built: Theorem C-B

Revised 2026-11-19 after `hvzk-referee.md` (H-1, H-3). Earlier revisions of this paragraph
described B as a Plonky3 binary stack with opening W-M; that is not what `yugen-proof-b2` builds,
and nothing of W-M is used below. Marks as in the header; source facts are the B review's
(`yugen-proof-b2/docs/zero-knowledge.md`, "the B review"), read at `yugen-proof-b2` `395da08` with
`git show HEAD:` (the vendored files named below were read there too).

#### 5.2.1 Setting

`K` is the challenge field of the build: `GF(2^256) = GHASH[Y]/(Y^2 + XY + X)` in the shipping
category-1 builds (`src/params.rs`, `FieldId::GhashSq256`; every mask, key, dummy operand, pad and
salt is sampled in `K`, B review 8.1), `GF(2^128)` at the pin. `q = n_test_queries = 192` at rate
1/8 (`src/params.rs`, `CAT1_QUERIES`). Two zero-knowledge round oracles: `M_0` holds the inner
trace `pi` and the key vector `z_pre` (IronSpartan's precommit segment), `M_1` holds the private
segment `z_wit` and the mask table `g'`; each carries `q 2^(log_batch_size - 1)` pad coordinates on
novel-basis coefficients `0..q` (`check_zk_pad`). Each committed segment ends with `q + 1` plain
dummy wires and **two dummy multiplication constraints** with wires `(a_i, b_i, a_i b_i)`, `a_i,
b_i` uniform (`spartan-frontend/src/constraint_system.rs` `BlindingInfo`,
`spartan-prover/src/lib.rs` `pack_and_blind_witness`, `spartan-verifier/src/constraint_system.rs`
`add_blinding_constraints`; S).

#### 5.2.2 Pad ledger (rows M1 to M12 of the B review)

| Row | View block | Pad (uniform, independent, used once) | Law of the block | Reference |
|---|---|---|---|---|
| M7 | inner prover messages (sumcheck rounds, claims, layer claims), each sent as `m + k` | one key `k` of `z_pre` each, never reused (C11) | uniform on `K^N`, exactly | one-time pad |
| M8 | inner query target `c = s + k` | its own key | uniform; the opening receives `<pi, t> + <z_pre, e_k> = c` | one-time pad |
| (1.3) | wiring claim | none: public function of the constraint system and the challenges | determined | B review 1.3 (N6) |
| M10, M11 | wrapper products `(a, b, c)` and the precommit contribution `s_pre` | the two dummy constraints of each committed segment | within `2 delta` of uniform on `K^4`, `delta = (|K| - 1)/|K|^2` | **Corollary DC** (5.2.3) |
| (N8) | private target `s_wit = (a + lambda b + lambda^2 c) - public_eval - s_pre` | none | determined | `spartan-prover/src/lib.rs` (`private_claim`) |
| M9 | masked check of `a b - c`: mask claim, round messages | mask table `g'` (Libra form, `n(d+1)` coefficients, N4) | the Blueprint's Theorem 6.3 simulator, given the final value `eq(r_mc, r_x)(a b - c)` from the row above; blend 0 excluded by restart (change 5) | Blueprint 6.3.2, appendix D; Libra ePrint 2019/317 Section 4.1 (B review N4) |
| M12 | mask evaluation `g(r)` | none | determined by the messages and the final value | B review M12 |
| M4 | opening mask claim `s'` | `w_r` | uniform; `gamma = 0` excluded by restart (change 5) | Diamond 2025/1015 Construction 4.1 |
| M5 | sumcheck rounds, folded codewords, terminal of the opening | `w_r` (through `M_r^gamma`) | functions of `M_r^gamma`, uniform subject to the batched relation | Diamond Theorem 4.3 (pp. 5-6) |
| M2, M3, M6 | opened symbols of `Enc(M_r)` (at most `q` distinct positions a round oracle, de-duplicated, change 34); symbols of `Enc(w_r)` | pad on coefficients `0..q` of `M_r` | `Enc(M_r)` symbols uniform, error 0; `Enc(w_r)` symbols determined from `Enc(M_r^gamma)` and `Enc(M_r)` | CFW26 Lemma 3.29 (p. 38), adapted to the novel basis; B review 2.1 |
| M1, M1a | round-oracle roots, leaf salts, sibling digests | 256-bit (default row) or 512-bit (category-1 row) leaf salts | simulated from the opened leaves | Lemma M |

Every row of the B review's wire list (its section 1.3 and rows M1 to M12) has a named pad or is
determined or public: the H-1 acceptance criterion.

#### 5.2.3 The dummy-constraint blinding (N3, N8; Original, the Ycash developers, 2026; draft until refereed)

Related prior work: the Blueprint's section 6.4 states that the dummy operands make `(a, b, c)`
"uniform subject to `a b = c`" without proof (D, as reported by the B review 2.2; not read here);
the upstream comment (`constraint_system.rs`, `N_DUMMY_CONSTRAINTS`) claims "statistically close to
uniform" for two constraints. The sketch is the B review's N3. What follows is new here.

**Lemma DC.** Let `K` be a finite field of characteristic 2, `|K| = Q`, and `alpha_1, alpha_2` in `K`
nonzero and distinct. Let `a_1, b_1, a_2, b_2` be uniform and independent in `K`, and

    X = (alpha_1 a_1 + alpha_2 a_2,  alpha_1 b_1 + alpha_2 b_2,  alpha_1 a_1 b_1 + alpha_2 a_2 b_2) .

Then the first two coordinates of `X` are uniform on `K^2`, and `TV(X, U(K^3)) = (Q - 1)/Q^2`
exactly.

*Proof.* Write `u, v` for the first two coordinates. For fixed `(a_1, b_1)` the map `(a_2, b_2) ->
(u, v)` is a bijection (`alpha_2 != 0`), so `(u, v)` is uniform and, given `(u, v)`, the pair
`(a_1, b_1)` is still uniform and independent. Substituting `a_2 = (u + alpha_1 a_1)/alpha_2`,
`b_2 = (v + alpha_1 b_1)/alpha_2`:

    X_C = c_1 a_1 b_1 + (alpha_1/alpha_2)(a_1 v + b_1 u) + u v/alpha_2 ,
    c_1 = alpha_1 + alpha_1^2/alpha_2 = alpha_1 (alpha_1 + alpha_2)/alpha_2 ,

and `c_1 != 0` because `alpha_1 != 0` and `alpha_1 != alpha_2`. With `s = u/(alpha_1 + alpha_2)` and
`t = v/(alpha_1 + alpha_2)`, `c_1 s = (alpha_1/alpha_2) u` and `c_1 t = (alpha_1/alpha_2) v`, so

    X_C = c_1 (a_1 + s)(b_1 + t) + d(u, v)

with `d` a function of `(u, v)` alone. Given `(u, v)`, `(a_1 + s, b_1 + t)` is uniform on `K^2`, so
`X_C = c_1 Y + d` with `Y` the product of two independent uniform elements of `K`. `Y = 0` with
probability `(2Q - 1)/Q^2` and `Y = y` with probability `(Q - 1)/Q^2` for each `y != 0`. The map
`Y -> c_1 Y + d` is a bijection of `K`, so the conditional distance of `X_C` from uniform is that of
`Y`: `1/2 ((2Q - 1)/Q^2 - 1/Q + (Q - 1)(1/Q - (Q - 1)/Q^2)) = (Q - 1)/Q^2`. It is the same for every
`(u, v)`, and `(u, v)` is exactly uniform, so `TV(X, U(K^3)) = (Q - 1)/Q^2`. ∎

The hypotheses are necessary as stated: with one dummy constraint `alpha X_C = X_A X_B`, so the
three values satisfy a public quadratic relation (distance `1 - 1/Q`, the upstream comment's
reason for two); with `alpha_1 = alpha_2` the formula changes (the third coordinate is then
uniform unless `u = v = 0`).

**Corollary DC (N3, N8).** Let the constraint point `r_x` and the operand batching challenge
`lambda` be fixed, and let `alpha_1, alpha_2` (precommit segment) and `alpha_3, alpha_4` (private
segment) be the values `eq(r_x, j_i)` at the four dummy-constraint indices `j_i`. Assume
**(H-DC)**: each dummy operand wire occurs in exactly one constraint, as the operand named, with
coefficient 1, and in no other row of the wiring matrices (the verifier's padded system asserts the
construction, `add_blinding_constraints`, `spartan-verifier/src/constraint_system.rs` lines 46-66, S;
*amended 2026-11-19, `zk-b-referee.md` F-1:* the earlier citation, lines 302-315, is a test on a toy
shape that checks only that the dummy wires appear; test SB-3 must assert on the padded wallet
system that each dummy wire appears exactly once, with coefficient 1, in no other row); the dummy operands are
uniform and independent of everything else in the proof except the oracles that store them. If
`alpha_i != 0` for all `i`, `alpha_1 != alpha_2` and `alpha_3 != alpha_4`, then for every witness,
every key vector and every value of the other randomness, the revealed vector

    V = (a_eval, b_eval, c_eval, s_pre)

satisfies `TV(V, U(K^4)) <= 2 delta`, `delta = (|K| - 1)/|K|^2`. The private target `s_wit` is then
determined (N8).

*Proof.* `V = R + N`, where `R` collects the public, real-wire and key contributions (fixed once
everything except the dummy operands is fixed) and, by (H-DC),

    N = (P_A + W_A, P_B + W_B, P_C + W_C, P_A + lambda P_B + lambda^2 P_C) ,

with `P` the precommit segment's dummy share and `W` the private segment's, each of the form `X` of
Lemma DC and independent of each other and of `R`. A shift is a bijection, so `TV(V, U) = TV(N, U)`.
Let `N* = (U_3, l(P))` with `U_3` uniform on `K^3` independent of `P` and `l(x) = x_A + lambda x_B +
lambda^2 x_C`. Coupling `W` with `U_3` optimally, `TV(N, N*) <= TV(W, U_3) = delta`. The map `l` is
linear and onto `K` (coefficient 1 on `x_A`), so `TV(l(P), U(K)) <= TV(P, U(K^3)) = delta`, hence
`TV(N*, U(K^4)) <= delta`. Adding, `TV(N, U(K^4)) <= 2 delta`. Finally `s_wit` is computed from
`V`, `lambda` and the public evaluation (`spartan-prover/src/lib.rs`, `private_claim`).
*Ordering (amended 2026-11-19, `zk-b-referee.md` F-6):* all challenges, `r_x` and `lambda` among
them, are fixed before the dummy operands are drawn; this is the HVZK setting (Lemma T order,
block 2 before block 3), and the Blueprint's Theorem 6.3 simulator needs only the final value. ∎

*Excluded events.* `eq(r_x, j) = prod_k` (`r_k` or `1 + r_k`) vanishes only if some coordinate of
the uniform `r_x` takes one value: probability `<= n_x/|K|` for each of the four `alpha_i`, `n_x =
log2` of the padded constraint count. `eq(r_x, j_1) + eq(r_x, j_2)` is a nonzero multilinear
polynomial of degree `<= n_x` for `j_1 != j_2`: probability `<= n_x/|K|` by Schwartz-Zippel, twice.
Total `6 n_x/|K|`.

*Computation (C).* `zk-lemma/test_dummy_constraints.py` (results `zk-lemma/results/dummy_constraints.txt`):
over GF(16), every `alpha_1 != alpha_2` nonzero, all `16^4` operand tuples: `TV = 15/256 = (Q -
1)/Q^2` exactly; over GF(4), every admissible `(alpha_1..alpha_4)` and every `lambda`, all `4^8`
operand tuples: worst joint distance `561/8192 <= 2 delta = 3/8`. Controls: one dummy constraint
(distance `15/16`); a precommit segment without dummies (`s_pre` unmasked, distance `3/4`).
*Amended 2026-11-19 (`zk-b-referee.md` F-2), re-run, all lines PASS, exit 0:* part 1 also asserts
`(u, v)` uniform and asserts (no longer prints) that `alpha_1 = alpha_2` is off the formula; part 2
asserts each coupling step, `TV(N, N*) <= delta` and `TV(l(P), U) <= delta` (`delta = 3/16`), for
every admissible case, and pins the worst value `561/8192` as a regression constant; asserted
controls: `alpha_i = 0` gives `405/2048 > delta`; `alpha_1 = alpha_2, alpha_3 = alpha_4` gives
`285/4096`, above the admissible worst case.

#### 5.2.4 Theorem C-B (P given the cited statements; Original composition, draft until refereed)

**Theorem C-B.** Fix all challenges of B's interactive protocol outside the excluded events (the
six `alpha` events of 5.2.3; blend 0 and `gamma = 0` do not occur because the prover restarts,
change 5, a public-coin event). Suppose the keys, dummy operands, mask table, opening masks, pads
and salts are uniform and independent, each used as the ledger says, (H-DC) holds, and at most `q`
distinct positions of each `Enc(M_r)` are opened. Then the algebraic view of a B leaf proof is
within `2 delta` of the output of

    Sim-B(public input, challenges):
      1. inner layer: every padded inner message and the inner query target <- uniform in K;
         the wiring claim := its public function of the constraint system and the challenges.
      2. wrapper values: (a_eval, b_eval, c_eval, s_pre) <- uniform in K^4;
         s_wit := (a + lambda b + lambda^2 c) - public_eval - s_pre.
      3. masked check: the Blueprint's Theorem 6.3 simulator on the zerocheck of a b - c, claim 0,
         final value eq(r_mc, r_x)(a b - c) from step 2; g(r) is determined.
      4. opening: the relations (precommit: target s_pre and the inner-target relation c;
         private: s_wit; mask table: g(r)) are now public; s' <- uniform; for each round oracle
         M_r^gamma <- uniform subject to the batched relation with target s' + gamma s;
         the opened symbols of Enc(M_r) <- uniform (distinct positions); the symbols of Enc(w_r)
         := gamma^-1 (Enc(M_r^gamma) - (1 - gamma) Enc(M_r)) at those positions; fold rounds,
         folded codewords and terminal computed from M_r^gamma.
      5. Merkle trees: salted leaves over the simulated opened leaves, uniform digests elsewhere.

The simulator uses no witness.

*Proof.* Lemma T (commitment document) with four blocks in this order: (1) keys, (2) dummy
operands, (3) the mask table `g'`, (4) the opening masks `w_r` and pads. Each pad enters no earlier
block: keys enter block 1 (own), block 2 (through `R`), block 4 (oracle entries); dummy operands
enter block 2 (own), block 3 (through the summand), block 4; `g'` enters blocks 3 (own) and 4;
`w_r` and the pads enter block 4 only. Given the earlier blocks, block 1 is exactly uniform (one
key a value, C11); block 2 is within `2 delta` of uniform (Corollary DC); block 3 follows the
Blueprint's Theorem 6.3 exactly for a nonzero blend; block 4 follows Diamond's Theorem 4.3 for
`gamma != 0` with the pad step by CFW26 Lemma 3.29 (error 0). The targets of block 4 are functions
of blocks 1 to 3. ∎

**`eps_hvzk^B` at the built shape (H-5 for B).** `eps_hvzk^B <= 2 delta + 6 n_x/|K| < 2^-255 + 6 n_x
2^-256`. *Amended 2026-11-19 (`zk-b-referee.md` F-3):* `n_x = 21` at the shipping category-1
wrapper (S: `yugen-proof-b2` `bench/results/cat1-20261119.txt`, `leafbench-cat1`, "mul constraints
2097152 (log 21)"; `n_x = log_mul_constraints`); the earlier guess `n_x <= 20` counted wires, not
constraints. So `eps_hvzk^B <= 2^-255 + 126 * 2^-256 < 2^-249`; SB-3 prints `n_x`. The
referee's `2^-253` omitted the `alpha` events. Conditional on the Blueprint's Theorem 6.3 / Lemma
D.1 (not refereed here) and on the refereeing of Lemma DC.

#### 5.2.5 Test specification for system B's builder (F-5 (b))

To be built in `yugen-proof-b2` (`tests/zk_simulator.rs`); each item is done when its acceptance
criterion passes in the shipping category-1 build.

| # | Test | Acceptance criterion |
|---|---|---|
| SB-1 | `simulate_b_leaf(public_input, seed)` implementing Sim-B steps 1 to 5, in a module that cannot name the witness type, writes a proof whose Fiat-Shamir challenges are replaced by values drawn from `seed` (a programmed transcript the test verifier replays) | the unmodified verifier, run with the same programmed transcript, accepts, at the toy statement and at the wallet leaf; the simulator's crate graph has no dependency on witness generation |
| SB-2 | determined-value replay: take a real proof, keep only its padded values (the samples of steps 1, 2, `s'`, the opened `Enc(M_r)` symbols, `M_r^gamma`), recompute every other value with Sim-B's equations | byte-equal to the real proof for every determined value (`s_wit`, `g(r)`, the `Enc(w_r)` symbols, folds, terminal, wiring claim); every transcript value is tagged with a ledger row of 5.2.2 and none is untagged |
| SB-3 | Lemma DC hypotheses through the code: (H-DC) asserted on the padded wallet constraint system: each dummy wire appears exactly once, with coefficient 1, in no other row (amended 2026-11-19, `zk-b-referee.md` F-1); at the drawn `r_x` the four `alpha_i` are nonzero and `alpha_1 != alpha_2`, `alpha_3 != alpha_4`; `n_x` printed | assertions hold at both shapes; control: with the precommit segment's dummy constraints removed, a witness-holding distinguisher recomputes `s_pre` exactly and the test reports the leak |
| SB-4 | `zk_pad_rank` rerun at `q = 192`, rate 1/8, both round oracles | rank 192 of 192 at `0..q` and at the random position sets; rank 0 without the relabeling |
| SB-5 | key and dummy freshness: two proofs of one witness | no key, dummy operand, pad or salt value repeats across or within proofs (stream offsets distinct) |

In one line: **SB: a witness-free `simulate_b_leaf` whose programmed-transcript proof the real
verifier accepts, plus a byte-equal replay of every determined value from a real proof's padded
values, the Lemma DC hypotheses asserted at the drawn `r_x`, and `zk_pad_rank` at `q = 192`.**

The two leaves share the characteristic and the idea of a pad on the lowest coefficients of the
encoding, but not the opening construction (A: WHIR with W-I; B: BaseFold with Diamond's mask) nor
the sumcheck masks (A: staircase and Libra-in-eq; B: the Blueprint's masked check and one-time-pad
keys). The common-mode statement of earlier revisions (`yugen-zk-b` section 7) applied to the
design in which B used W-M; for B as built only the characteristic and the encoding-lemma idea are
shared.

---

## 6. Fiat-Shamir

The interactive protocol is public-coin. The non-interactive proof derives every challenge by
hashing the transcript so far (Keccak-256 in both systems).

**Statement used (Published; verified against the paper on 2026-11-19).** Ben-Sasson, Chiesa,
Spooner, "Interactive Oracle Proofs", ePrint 2016/116 (copy dated 2016-02-10), Theorem 7.1,
third bullet, proven as Lemma 7.5: if a public-coin IOP has `z`-statistical honest-verifier
zero knowledge, the compiled non-interactive random-oracle proof has `z'`-statistical zero
knowledge with `z'(x, lambda) = z(x) + p(x) 2^(-lambda/4 + 2)`, `p` the proof length. The
conditions the paper actually requires:

1. the IOP is **public-coin** and its zero knowledge is **honest-verifier and statistical** (a
   simulator for the honest verifier's view: query answers and verifier randomness);
2. every oracle is committed with the **Merkle tree with privacy** of its Section 3.2: leaf
   `rho(v_i || r_i)` with `r_i` uniform of `2 lambda` bits for a `lambda`-bit oracle, revealed with
   the opening (Definition 3.3, Lemma 3.4: privacy `n 2^(-lambda/4 + 2)`, against an unbounded
   distinguisher);
3. zero knowledge is in the **explicitly-programmable random oracle model** (Section 2.3,
   Remarks 1.4 and 2.2): the simulator outputs the points it programs and the distinguisher
   queries the programmed oracle. Zero knowledge with a non-programmable oracle is impossible
   for non-trivial languages (Appendix C);
4. the result is malicious-verifier zero knowledge of the non-interactive proof; no rewinding.

What the paper does **not** give, and what this section rests on instead: (a) its bound is for
`2 lambda`-bit salts and an unbounded distinguisher, with exponent `lambda/4`; with 256-bit
salts and a 256-bit hash the bound used here is the query-bounded one of Lemma M
(`zk-hiding-commitment.md` 4; the form of ePrint 2026/391 Lemma B.2) and of the Chiesa-Yogev
book's Theorem 26.2.1 (`soundness-method.md` section 5), not Lemma 7.5's; (b) the paper says
nothing about quantum distinguishers; (c) direct (non-oracle) messages are covered because they
are oracles read in full. That salting is necessary is Published: Diamond, ePrint 2025/1015,
Section 4.1. The proof idea, which follows the simulator in the proof of Lemma 7.5 (P as a
sketch):

    NIZK-Sim(public input):
      1. sample all challenges as the honest verifier would; run Sim of Theorem C;
      2. build the salted trees over the simulated opened leaves (uniform digests elsewhere);
      3. program the random oracle so that each transcript prefix hashes to the sampled challenge.

Programming fails only if a prefix was queried before; every prefix contains a Merkle root over
salted leaves or a uniform field element, so the failure probability is at most
`q * R / 2^256`-order for `q` oracle queries and `R` rounds. Total distance: (Theorem C's
excluded events) + (Lemma M per tree) + (programming failures).

**Conditions, each a checklist item.**

1. Every prover message (roots, field elements, grinding nonces) and the full public input and
   parameter table are absorbed before the challenge that follows them. Soundness depends on five
   instances in particular (`zk-wi-soundness.md` section 2.3, each with a reversed-order control):
   oracle 0 (blinder cells, masks, `B`) before every challenge; each `G` before its `rho`;
   `Gcol` and `mu` before the base-case challenge `c`; **the padded final message `P*` before the
   last level's query positions**; each new oracle before the positions of the previous one. One
   message is sent after the challenge it must not depend on: a GKR layer's `Gtilde` (after
   `rho`). It is sound only because **every `Gtilde` is in the gadget's claim list** as a linear
   functional of column `A`; an implementation that omits one is unsound.
2. Each challenge is a fresh oracle output on the whole prefix, with domain separation between
   uses; a challenge that the hiding argument restricts (out-of-domain points outside the ambient
   subspace) is obtained by rejection sampling from that output.
3. Query positions are derived the same way; the randomness budget counts distinct rows, so
   repeated positions need no special treatment.
4. Grinding: the prover searches a nonce `s` with `H(prefix, s)` below a target; the challenges
   that follow hash `(prefix, s)` under a separate domain tag. The simulator runs the same search
   against its lazily sampled oracle (the prefix is fresh, so the distribution of `s` is the
   honest one) and programs only the challenge outputs. If one hash output serves both as the
   grinding test and as the challenge, the simulator must sample challenges conditioned on the
   test; separate outputs avoid that.
5. Salts on every tree whose unopened leaves depend on a secret; salts are independent of the
   pads.
6. All pads of the ledger come from a cryptographic generator seeded with fresh entropy for each
   proof. Two proofs that reuse a pad with different challenges reveal the difference of the
   padded values.

Quantum adversaries: zero knowledge by oracle reprogramming also holds against quantum queries,
with a larger loss, by the adaptive-reprogramming bounds of Unruh and of Grilo, Hövelmanns,
Hülsing and Majenz (M; not fetched). Chiesa, Manohar, Spooner, ePrint 2019/834 (read 2026-11-19),
Theorem 8.6 (3) with the argument of Lemma 7.3, gives statistical zero knowledge in the QROM only
from a classical guarantee against distinguishers unbounded in queries; Lemma M's bound is
query-bounded, so the quantum statement for 256-bit salts is not covered by that paper
(`CITATION-AUDIT.md` C-8). A published quantum statement for a closely related transformation
now exists: GordieHowe, ePrint 2026/2615 (read 2026-11-19), Theorem 6.6 (3), everlasting zero
knowledge in the QROM for its spBCS, proved by one-way-to-hiding steps per proof (its Section 6.3,
citing Ambainis, Hamburg, Unruh), with leaf salts twice the digest length; at the built salt length
(equal to the digest) its leaf term is 1/2 and gives nothing (C-21; `zk-hiding-commitment.md` 4).
Statistical zero knowledge of the interactive protocol does
not depend on the adversary's computing power.

Not covered: side channels of the prover (timing of the rejection and grinding loops, memory),
and the knowledge-soundness side of the compilation (`docs/soundness-method.md`).

---

## 7. Implementation checklist

For a sumcheck-based prover over `GF(2^k)` with Merkle commitments to additive Reed-Solomon
codewords. "Random" counts uniform field elements of the challenge field `F` unless stated.
Reference tests are files in `zk-lemma/` (L) or `zk-commit/` (K).

| # | Add | Random | Reference test |
|---|---|---|---|
| 1 | Evaluate every committed oracle on a coset `beta + S` with `beta` outside `S` (shifted additive NTT); the verifier's query points and evaluation weights use the shifted points | 0 | K `test_code.py` (linear domain leaks exactly on `U_top`) |
| 2 | Per oracle and lane: `t = Q + o` uniform coefficients at an offset that is a multiple of `2^ceil(log2 t)` and at or above the message length; reject parameters with lane length above the domain size; recompute queries at the true rate | `lanes * t` per oracle, in the oracle's alphabet | K `test_code.py` (budget, alignment), `test_whir.py` control "one coefficient too few" |
| 3 | Salt every leaf of every tree of the leaf proof with 32 fresh bytes; open the salt with the leaf | 32 bytes per leaf | (hash-level; no algebraic test) |
| 4 | Fold batches of the opening: one claim-level mask per batch, its coefficients written into every lane of their aux rows of that level's oracle; prover sends `G_i`, verifier answers `rho_i`; after the batch the verifier adds the mask's final-value weights on the aux slots | `1 + 2 kappa` per batch (plain degree 2), `1 + 4 kappa` (affine combiner) | K `test_whir.py`; K `test_blind.py` part A for the round space; L `test_exact.py` |
| 5 | Never send a folded polynomial's coefficients: carry the excess (folded randomness, high part) into the next oracle as message slots | 0 | K `test_whir.py` (three-level case) |
| 6 | Base case: commit a uniform polynomial `gt` of the last folded lane's length as one more column of the last oracle; send `mu`; after `c` send `P* = gt + c p'`; verifier checks the relation and, at the last query round's rows, `P*(y) = Gcol(y) + c fold(row)` | lane length of the last level | K `test_basecase.py` (enumerated), `test_whir.py` control "no base-case mask" |
| 7 | Out-of-domain points: sample outside `span(S, beta)`, pairwise distinct | 0 (covered by item 2) | K `test_whir.py` (cases with 1 and 2 points) |
| 8 | Zerocheck and every other sumcheck outside the opening: staircase mask (plain sum) or Libra's mask inside the eq factor (reduced messages); one fresh mask per instance; coefficients in the mask column `A` | `1 + sum_j d_j` per sumcheck | L `test_exact.py`, `test_rank.py`, `test_leak.py` |
| 9 | Dummy variable and blinder cells: every revealed evaluation of committed data is `c(r) + r_y (1 + r_y) b` with its own cell `b` in the blinder column; the relation handed to the opening includes the cells | 1 per revealed evaluation | K `test_blind.py` part B |
| 10 | GKR chains: dummy variable, two blinders per claimed layer polynomial (four for fraction layers), `Gtilde` in place of `G`; bottom-layer claims by item 9 | 2 (or 4) per layer, plus the layer sumcheck's mask | L `test_gkr.py` |
| 11 | Bus terminals: one mask message per neighbouring table pair; one self-cancelling pair per table that publishes a denominator | `T - 1` (+ `T`) payloads | L `test_bus.py` |
| 12 | Linear claims on the mask column: gadget columns `A` (with pad) and `B`; messages `beta`, `u`; evaluations `A(z)`, `B(z)` join the opening's relation | `len(A)` for `B`, at least 1 pad | L `test_gadget.py` |
| 13 | Wire audit: list every value the prover sends and every leaf it opens; each must appear in the pad ledger (section 4.1) as padded or determined; a value outside the ledger blocks release | 0 | review; `yugen-zk-b` T-5 distinguishers as regression |
| 14 | Transcript: conditions 1 to 4 of section 6; separate oracle outputs for grinding and challenges | 0 | transcript unit tests of each system |
| 15 | Generator: all pads and salts from a cryptographic generator with fresh entropy per proof; a test fails if two components draw the same stream position | seed | code review; unit test on stream offsets |
| 16 | Through-the-code simulator test: a witness-free simulator in each system's code produces accepting proofs under programmed challenges; at toy size the exact comparison of K `test_whir.py` is reproduced through the system's prover; at leaf size the statistical test T-4 of `yugen-zk-b` | 0 | K `test_whir.py` as the model |
| 17 | Soundness accounting: `+1/|F|` per masked batch, `(d + 1)/|F|` per round with inline masks, the gadget's `(l + m)/|F|`, the bus messages' completeness loss, the true rates of item 2 | 0 | `soundness/` rerun (not done here) |

---

## 8. Review sheet for an external cryptographer

**Setting.** `F = GF(2^k)`. Additive Reed-Solomon codes in the novel basis `X_c = prod What_i`
over `D = beta + S`; `U_i = span(b_0..b_{i-1})` is the zero set of `What_i`. Interleaved oracles:
a leaf is a row of lanes; fold of a row by `eq(., gamma)` or by the affine combiner. Salted
Keccak Merkle trees. Honest-verifier zero knowledge of the interactive protocol; Fiat-Shamir in
the random-oracle model.

| # | Statement | Proven on paper | Exact computation | Open |
|---|---|---|---|---|
| 1 | **Mask theorem** (lemma document Theorem 1, Corollaries A, B): staircase mask, plain sum, characteristic 2; Libra's mask under eq weights | yes | all `r`: GF(4) `n <= 5`, GF(16) `n <= 3`, `d <= 3`; sampled `r` to `n = 27` | |
| 2 | **Masked sumcheck is perfect zero-knowledge with one query** (lemma document Theorem 2) | yes | all masks against all simulator tapes, GF(4) `n <= 3`, GF(16) `n <= 3` (sizes in the lemma document) | optimised round messages of the pinned stacks |
| 3 | **Theorem 1'**: claim-level masks for abstract round spaces; instance for the affine-combiner round | yes (same proof) | rank `1 + 4n` for all challenge vectors, GF(4) `n <= 2`; sampled, GF(256) `n <= 14` | prover-side reading of the affine round |
| 4 | **Lemma E**: `t` aligned random coefficients per lane hide any `t` rows iff the domain avoids `U_top`; the linear domain leaks on a `rate` fraction of rows | yes | every row set, six shapes, GF(16), GF(256); enumeration GF(8) | |
| 5 | **Lemma O**: out-of-domain answers under the budget `t = Q + o` | yes | inside statement 8's instances | |
| 6 | **Lemma S**: masked claim reduction with residual hand-off | yes | inside statement 8's instances | |
| 7 | **Lemma F**: deterministic folds need `T >= Q 2^K` | yes | rank, GF(256) `n = 3`, three shapes, four controls; enumeration GF(16) | |
| 8 | **Theorem W**: the hiding opening W-I has an algebraic view uniform on the accepting set | yes (Lemma T) | `rank B = dim Acc` on five instances (GF(16), GF(64), GF(256); up to 16 witness and 52 randomness variables); full enumeration with no fold, GF(8) | affine-combiner fold in the composed opening; alphabet below `F` |
| 9 | **Soundness of W-I** | sketch only | none | **open: non-power-of-two lane dimension, coset domain, aux rows, base-case column** |
| 10 | Variant W-S (separate mask oracles, layout of the pinned Plonky3 code, an earlier version of ePrint 2026/391) in characteristic 2 | by the same ledger, not written out | components only | whole protocol; the paper as published (revision of 2026-11-16, read) uses the in-oracle layout, so no published analysis of W-S was read |
| 11 | **Theorem BF-1** (full-mask folding opening) | yes | none | |
| 12 | Theorem BF-2 (budgeted folding opening) | fold-phase view only | Lemma F's tests | mask-oracle part |
| 13 | **Lemma M**: salted leaves hide unopened leaves, `q N / 2^s` | sketch | none | quantum bound |
| 14 | Linear opening gadget (lemma document Lemma 3) | yes | all randomness, GF(4), GF(16) | |
| 15 | GKR layer blinding (lemma document Lemma 4) | yes | GF(4), two reductions | fraction layers, deeper chains |
| 16 | Bus terminals (lemma document Lemma 5) | yes | GF(4), GF(16), GF(256), `T <= 4` | which values each stack publishes |
| 17 | **Theorem B**: blinder cells with a dummy variable | yes | enumeration GF(4), booleanity constraint | |
| 18 | **Theorem C** (system A): composed simulator from the pad ledger; events at the built shape: 706 `F`-events, `< 2^-246.5`, plus the H-2 rank term, **not proven** (F-4: under investigation in system A's build, rank check after `z`, restart below 8; section 4.2a) | yes, given 1 to 17 | none for the composition as a whole | whole-view check at row 8 (`hvzk-referee.md` H-4); the 18-element assertion (H-2) |
| 18b | **Theorem C-B** (system B as built): three-layer simulator over ledger M1 to M12 | yes, given the Blueprint's Theorem 6.3, Diamond Theorem 4.3, CFW26 Lemma 3.29 and Lemma DC | Lemma DC: GF(16) one segment, GF(4) joint (`zk-lemma/test_dummy_constraints.py`) | simulator test SB-1 to SB-5 (section 5.2.5) not built (F-5 (b)); `zk_pad_rank` at `q = 192` |
| 18c | **Lemma DC / Corollary DC**: two dummy constraints a segment blind `(a, b, c)` and `s_pre` | yes (draft, Original) | exact, as 18b | refereeing |
| 19 | Fiat-Shamir compilation to non-interactive zero knowledge in the random-oracle model | sketch; theorem verified: ePrint 2016/116 Theorem 7.1 / Lemma 7.5 | none | the error term used is Lemma M's, not Lemma 7.5's (section 6); QROM statement |

Where to look for an error first: the dependence table in the proof of Theorem W (does any pad
enter an earlier block?); the claim that the aux slots have weight zero until the batch ends;
the alignment argument of Lemma E; the intersection step in the proof of Lemma F; the reading of
the affine-combiner round from the verifier alone.

Every exact test is a statement about the model in `zk-commit/` and `zk-lemma/`, not about the
two provers' code; checklist item 16 is the link.
