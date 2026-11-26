# Decision record (DRAFT): the node's batching sumchecks in parallel rounds (system B)

Part of Yugen. **Draft, unrefereed**: a recommendation of the maths team to the lead
agent, 2026-11-19. Lemma P, Lemma R and finding PB-3 are this project's own and are drafts
until a referee has passed them. The decision number is the lead agent's to assign. Format and
standard follow `decision-b-merkle-hash.md`. Figure marks: (M) measured, (C) counted, (E)
estimate; (M) and (C) figures are system B's, from `yugen-proof-b2/docs/parameters.md` at
`09a7b4e` (sections 2a.4, 3.6.2, 10.3, 13.2, 15.6, 15.7) and its code (`src/batch.rs`,
`src/node.rs`, `vendor/binius64/crates/ip/src/sumcheck/batch.rs`,
`crates/ip-prover/src/sumcheck/padded.rs`). Nothing was re-measured.

## 1. The question

The main circuit of a bundle node reduces the deferred claims of the proofs it verified to one
claim per shape, by one sumcheck per shape, one after the other, on one in-circuit Fiat–Shamir
transcript. System B proposes to run these sumchecks in parallel rounds, with one verifier
message a round for all of them (its 15.7 item 2). Is that sound, at what error, and what does
it do to the transcript's compilation and to zero knowledge?

## 2. What is built (read from the code)

`batch::reduce` (one group `g`: `K_g` claims `T(z_i; u_i) = v_i` on one family of `n_sets` bit
vectors over `n_g` variables):

| Step | Prover sends | Verifier draws | Error if the state is false before it |
|---|---|---|---|
| 0 | — (every claim element of every group is already absorbed, `node::batch_all`) | `alpha` | `(K_g - 1) / \|F\|` |
| `j = 1 .. n_g` | `c0, c2` of the round polynomial (`c1 = claim + c2`, so `p(0) + p(1) = claim` holds by construction in characteristic 2) | `r_j` | `2 / \|F\|` |
| `n_g + 1` | `s_o = S~_o(r)` for each set; the verifier checks `claim = sum_i alpha^i eq(z_i, r) sum_o u_(i,o) s_o` | `mu` (only if `n_sets > 1`) | `(n_sets - 1) / \|F\|` |

Output: the one claim `T(r; [1, mu, ..]) = sum_o mu^o s_o`. `node::batch_all` runs `reduce`
for the groups in order on one channel. Level 0 has four groups; each level above adds one
wiring group of at most 78 variables. Verifier messages of the batching transcript at the
256-bit field: `180 + 79 L` at level `L` (the calculator's `k_batching`; B's 2a.4), so 417 at
level 3. `F` is the channel's field, `GF(2^256)` at category 1.

## 3. What is proposed, and what the proposal leaves open

B's text, whole: "Batching sumchecks of a node in parallel rounds (one verifier message a
round for all claim groups, in place of one a round a group): main's transcript falls about
fivefold at level 0. A change of our own batching step (`src/batch.rs`); the error is the
union over the groups, a round." No protocol text or code exists yet. Four points are not
fixed by that sentence; this record fixes them so that a definite protocol is analysed, and
the B team confirms or corrects them (obligation PB-O1):

- **U-1 Alignment.** Groups have different `n_g`. Taken here: **end-aligned**. With
  `n_max = max n_g`, group `g` runs its round `j` in global round `n_max - n_g + j`, so all
  groups finish together. (Start alignment is covered by Lemma P as well.)
- **U-2 `alpha` and `mu`.** Taken here: one `alpha` for all groups (global round 0) and one
  `mu` for all groups that need one (global round `n_max + 1`).
- **U-3 Absorption.** In each global round the prover's message is the tuple of `(c0, c2)` of
  every active group in the fixed group order; all of it is absorbed before the challenge.
- **U-4 Separate or combined round polynomials.** Taken here: **separate** (each group keeps
  its own running claim and its own `(c0, c2)`). Combined forms are section 4's other options.

**Protocol P-sh** (shared challenges; the proposal as read here). Global round 0: `alpha`.
Global round `j = 1 .. n_max`: the prover sends `(c0, c2)` for each group with
`n_max - n_g < j`; the verifier draws one `r_j`; each active group updates its own claim with
`r_j`. Then the prover sends every group's `s_(g,o)`; the verifier makes each group's final
check and draws one `mu`. Group `g`'s reduced claim is at the point
`(r_(n_max - n_g + 1), .., r_(n_max))`: a suffix of the shared challenge vector. Verifier
messages: `n_max + 2`, at most 80 at any level.

## 4. Options considered

| | Form | Verifier messages, level `L` | Error a round | Rests on | Verdict |
|---|---|---|---|---|---|
| P-seq | As built | `180 + 79 L` | `2 / \|F\|`; `alpha`: `(K - 1) / \|F\|` | Lemma R | Baseline |
| **P-sh** | Shared challenge, separate round polynomials | `n_max + 2 <= 80` | **the same: the largest over the active groups, no union factor** | Lemma R, **Lemma P (Original, draft)** | **Recommended** |
| P-ind | Independent challenges for the groups, carried in one verifier message | `n_max + 2` | sum over the active groups: at most `2 G / \|F\|` | [SG26] Lemma 2.27 (2)(a) and Lemma 5.2 (Published), with a linearisation step of ours | Fallback if Lemma P is refused; streams of `32 (1 + G)` bytes, a second Keccak-f a round from four groups up |
| P-rlc-pad | One combined round polynomial; short groups padded with `eq(0, .)` on leading variables | `n_max + 2` | `2 / \|F\|`; `alpha`: `(sum_g K_g - 1) / \|F\|` | the standard sumcheck on one polynomial; the form the pinned library implements for its own sumchecks (`batch_verify`, `PaddedProver`) | Sound; the larger saving (section 7); a second step, with its own record |
| P-rlc-late | One combined round polynomial; a short group's weighted claim added to the running claim when it starts, coefficients fixed at round 0 | `n_max + 2` | **unsound in characteristic 2: forged with probability 1** | finding PB-3 | **Excluded** |

## 5. Soundness

Definitions used: a reduction, its state function and its round-by-round soundness errors are
those of Sharp and Grubbs, ePrint 2026/2615 [SG26], Definition 2.24 (a), conditions (i) and
(ii) (p. 15 to 16; read from the text layer for this record). A state is 0 while the prover
has not yet been lucky; (i) says that from a false input every transcript with a true output
has a round at which the state moves from 0 to 1; (ii) bounds the probability of that move at
each round by the round's error.

### Lemma R (the built reduction; Adapted)

Adapted from the textbook sumcheck analysis; the per-round figure for a degree-2 round
polynomial is as [SG26] states it for its own layers ("Each sumcheck round of a layer has
error 2/|K|, the error of a sumcheck round with a polynomial of degree 2", Section 5, p. 45).
What is ours: the state function for `reduce` as coded (the `alpha` step, the implicit linear
coefficient, the final check against prover-supplied `s_o`, the `mu` step).

**Statement.** `reduce` for one group is a reduction from "every incoming claim is true" to
"the outgoing claim is true" with round-by-round soundness errors `(K - 1) / |F|` at `alpha`,
`2 / |F|` at each `r_j` and `(n_sets - 1) / |F|` at `mu`.

**Proof.** Write `t_i = T(z_i; u_i)` for the true values, `F_alpha(x) = sum_o S_o(x) E_o(x)`
with `E_o(x) = sum_i alpha^i u_(i,o) eq(z_i, x)` (multilinear in `x`; `F_alpha` has degree at
most 2 in each variable), `P(r_1 .. r_j) = sum over x in {0,1}^(n - j) of F_alpha(r_1 .. r_j, x)`,
`C_j` the verifier's running claim after round `j` and `D_j = C_j - P(r_1 .. r_j)`.
State: 0 before `alpha` (the input is false); after `alpha` and after each `r_j`, the state is
1 if and only if `D_j = 0`; before a challenge it equals the state after the previous one;
after `mu` it is 1 if and only if the final check passed and the outgoing claim is true.

(i) The state starts at 0. If the outgoing claim is true the state ends at 1, so it moves at
some round.

(ii) At `alpha`: `D_0 = sum_i alpha^i (v_i - t_i)`, a nonzero polynomial in `alpha` of degree
at most `K - 1`; it vanishes with probability at most `(K - 1) / |F|`. At `r_j` with
`D_(j-1) != 0`: the prover's `p_j` has `p_j(0) + p_j(1) = C_(j-1)` and the true
`q_j(X) = P(r_1 .. r_(j-1), X)` has `q_j(0) + q_j(1) = P(r_1 .. r_(j-1))`, so `p_j - q_j` sums
to `D_(j-1) != 0` over `{0, 1}` and is a nonzero polynomial of degree at most 2;
`D_j = (p_j - q_j)(r_j)` vanishes with probability at most `2 / |F|`. At `mu` with
`D_n != 0`: if the final check passes, `sum_o s_o E_o(r) = C_n != sum_o S~_o(r) E_o(r)`, so
`s_o != S~_o(r)` for some `o`, and `sum_o mu^o (s_o - S~_o(r))` is a nonzero polynomial in
`mu` of degree at most `n_sets - 1`. With one set there is no `mu` and the outgoing claim is
false with certainty. ∎

### Lemma P (shared-challenge parallel composition; Original, draft)

Original (the Ycash developers, 2026) as far as checked. Sources consulted: [SG26] Section 2.6
(Definitions 2.24 to 2.26, Lemma 2.27) and Lemma 5.2; Attema and Fehr, ePrint 2021/1259
(abstract, Sections 1.1 to 1.3, Theorem 4); the text layers of ePrint 2019/834, 2024/504,
2024/1571, 2024/1586 and 2026/391 searched for a shared-challenge or parallel sumcheck
statement, none found. [SG26] Lemma 2.27 (2) is the parallel composition with **independent**
challenges (the rounds of the two reductions are unordered and each keeps its own challenge);
Lemma 5.2 merges consecutive verifier messages into one whose challenge set is the **product**,
at the sum of the errors. Neither covers one challenge used by several reductions at once.
First appears: this section.

**Statement.** Let `Pi_1 .. Pi_G` be reductions (from `R_g` to `R'_g`) with round-by-round
soundness errors `eps_(g,i)` by state functions `State_g` ([SG26] Definition 2.24 (a)), all of
whose challenge sets are one set `C`. Let `tau_g` be strictly increasing maps from the rounds
of `Pi_g` to global rounds `0 .. N - 1`. Define `Pi_sh`: in global round `j` the prover sends
the messages of all groups `g` with `j = tau_g(i)` for some `i`, the verifier sends **one**
uniform `theta_j` in `C`, and each such group takes `theta_j` as the challenge of its round
`i`; the output is the tuple of the groups' outputs. Then `Pi_sh` is a reduction from the
conjunction of the `R_g` to the conjunction of the `R'_g` with round-by-round soundness errors

    eps_j = max over the groups g active in global round j of eps_(g, tau_g^-1(j)).

**Proof.** Fix a statement and oracle input. Let `Bad` be the set of groups whose input is
false. If `Bad` is empty, (i) is vacuous; let the state be 0 everywhere. Otherwise say that
group `g` *moves* at global round `j = tau_g(i)` of a transcript if `State_g` is 0 on `g`'s
own past followed by its round-`i` message and 1 once `theta_j` is appended. Define the state
of `Pi_sh` at global round `j`: before `theta_j`, it is 1 if and only if every group of `Bad`
has moved at some round strictly before `j`; after `theta_j`, if and only if every group of
`Bad` has moved at some round up to and including `j`.

(i) Take a full transcript with every output true. For each `g` in `Bad`, condition (i) for
`Pi_g` gives a round at which `g` moves; let `j_g` be the first such global round and `j*` the
largest `j_g`. Before `theta_(j*)` the group attaining `j*` has not moved, so the state is 0;
after it every group of `Bad` has moved, so the state is 1.

(ii) Take a global round `j` and a transcript of its past and its prover message at which the
state is 0. Then some `g0` in `Bad` has not moved before `j`. The state after `theta_j` is 1
only if `g0` moves at `j`. If `g0` is not active at `j`, or `State_g0` is already 1 before
`theta_j`, that cannot happen. Otherwise `State_g0` is 0 on `g0`'s past and message, `theta_j`
is uniform in `C`, and condition (ii) for `Pi_g0` (which holds for every transcript of `g0`'s
past, whatever the other groups sent) bounds the probability by `eps_(g0, i) <= eps_j`. ∎

**Remarks.** (1) Leaving the false state needs every false group to be rescued by the same
challenge; the bound uses only that one of them must be, which is why there is no factor `G`.
B's "union over the groups" is an upper bound on this and is not needed. (2) The lemma does
not claim that cheating in several groups at once is harder than in one (no `eps^G`). The
staggered attack on parallel repetitions under Fiat–Shamir (`REFERENCES.md` O-12) is against
such a claim and has no bearing on the bound above. (3) The lemma needs one challenge set for
all groups in a round; in P-sh every challenge is one element of `GF(2^256)`. (4) The groups'
outgoing points share coordinates. A level above treats incoming claims as arbitrary claims
bound in its transcript (Lemma R holds for any points, equal ones included), so no
independence of points is used anywhere.

**Corollary (P-sh).** With Lemma R for each group and the alignment of section 3, P-sh has
errors `(K_max - 1) / |F|` at `alpha`, `2 / |F|` at each `r_j`, `(n_sets,max - 1) / |F|` at
`mu`: the same per-round errors as P-seq, over `n_max + 2` rounds in place of `180 + 79 L`.

### P-ind by published lemmas (Adapted)

Compose the `G` reductions in parallel ([SG26] Definition 2.26 (2)): by Lemma 2.27 (2)(a) the
composition has each group's own errors at each group's own rounds. Order the messages so
that in each global round all active groups' prover messages precede their verifier messages
(a refinement of the partial order; each state function reads only its own group's past, so
conditions (i) and (ii) are unchanged: this step is ours). The verifier messages of one global
round are then consecutive with no prover message between them, and Lemma 5.2 merges them
into one message "with error" the sum, at most `2 G / |F|`.

### PB-3 Finding: late joining with fixed coefficients is unsound in characteristic 2 (Original as far as checked)

Sources consulted: as for Lemma P, and the pinned library's `batch.rs` and `padded.rs`, which
avoid the problem by padding. First appears: this section.

**Protocol P-rlc-late.** Coefficients `beta_g` fixed at round 0. One running claim `C`,
initially the sum of `beta_g V_g` over the groups active in global round 1. When a shorter
group `h` starts at global round `j_h > 1`, the verifier adds `beta_h V_h` to `C`. Each round
one polynomial `p_j` with `p_j(0) + p_j(1) = C`.

**Attack.** Let `h` be a group with `j_h >= 2` and a false claim, `delta = beta_h (V_h - T_h)
!= 0`, every other claim true. In global round `j_h - 1` the prover sends the true round
polynomial plus the constant `delta`. In characteristic 2 a constant contributes
`delta + delta = 0` to `p(0) + p(1)`, so the round is accepted, and the running claim is now
the true partial sum plus `delta`. At `j_h` the verifier adds `beta_h V_h = beta_h T_h + delta`:
the two `delta` cancel and the running claim is the true combined partial sum. The prover is
honest from there and every later check passes. The false claim of `h` is reduced to true
claims with probability 1.

Checked on a toy instance over `GF(2^8)` (two groups of 2 and 1 variables, 200 random
instances, 200 forged; with `eq(0, .)` padding the same shift is caught, 2 of 200 pass
against an expected `200 / 256`); the script was a throwaway outside every repository and is
not a test of record (PB-T6 asks for one).

**Why padding is sound.** With group `h` replaced by `eq(0, x_pad) F_h(x)` on all `n_max`
variables, the batch is one sumcheck of one polynomial of degree at most 2 in each variable
from round 1, whose sum over the cube is the combined true sum (`eq(0, .)` sums to 1), and
Lemma R's argument applies with every claim in the running claim from the start. Front
padding without the `eq` factor fails for a different reason: it multiplies a group's sum by
`2^(pad) = 0`. Drawing `beta_h` only when `h` joins would also repair it (the constant the
prover needs is then unknown when it must be sent), at one more challenge a join.

### Error terms in bits, category 1 rows (`|F| = 2^256`; `K <= 16`; three sets at most)

| Term | P-seq (built) | P-sh (Lemma P) | P-ind, or B's union reading | P-rlc-pad |
|---|---|---|---|---|
| A sumcheck round | 255.00 | 255.00 | 253.00 (4 groups), 252.68 (5), 252.19 (7) | 255.00 |
| `alpha` | 252.09 | 252.09 | 250.09 to 249.29 | 249.21 (one `alpha` over at most 112 claims) |
| `mu` | 255.00 | 255.00 | 253.00 to 252.19 | 255.00 |
| Weakest round | 252.09 | 252.09 | 249.29 | 249.21 |
| All batching rounds of a level-3 node, summed | 246.15 | 248.57 | 246.15 (the same sum as P-seq) | 247.93 |
| All batching rounds of a level-0 node, summed | 247.31 | at least 248.57 | 247.31 | at least 248.21 |

Against the need: a category 1 row needs about 158.8 bits a round (system B's weakest round at
calculator revision 9, `e = 158.78`, `qrom-compilation.md` 6.2). Every form has at least 90
bits to spare a round. **No batching round is, or becomes, a binding term**; the batching
rounds matter to the calculator only through their number.

## 6. Effect on the compilation (spBCS), and on zero knowledge

**What kind of transcript this is.** The batching transcript is a second, in-circuit
Fiat–Shamir transcript of an interactive proof with no oracles (`SpbcsChallenger`, the same
key, stream and write-back as the outer transcript). Its challenges are functions of the
node's witness, and the documents count its rounds in the node's own (`parameters.md` 2a.4;
`soundness-method.md` 8.5b). That convention is unchanged; whether it is the right formal
treatment of an in-circuit transcript is not a question this proposal opens or closes.

**Hypotheses of Theorem 6.6 (2)** (`qrom-compilation.md` section 3) under P-sh: H1 (public
coin) and H2 (total order, `n_B = n_J = 0`) hold: P-sh is a sequence of global rounds, not a
series–parallel order, despite the name. H3 holds with the errors of the corollary (the
batching step has no witness of its own; obligation K-B is unchanged). H4 and H9 are
unchanged: every verifier message is still one 32-byte challenge from a 64-byte stream. H6 and
H8 hold if every active group's coefficients are absorbed before the challenge, in an order
fixed by the node's shape (U-3; test PB-T3); items stay fixed-length in a schedule that is a
function of the statement, because which groups are active in which round is fixed by the
shape. P-ind differs in H9 only: streams of `32 (1 + G)` bytes.

**Quantities** (level-3 node, the worst case; verifier messages 663 as built, 326 with P-sh):

| Quantity | Built | P-sh | Effect |
|---|---|---|---|
| Batching verifier messages | 417 | at most 80 | |
| `N_msg` of the node (both senders) | at most 1,326 | at most 652 | |
| `c' = N_msg max(1, m) + 1`, `m = 2` | 2,653 | 1,305 | hash term of the QROM bound: +0.34 bits (it does not bind) |
| `k_q = 2 N_msg + q_IOP (1 + floor(log2(2 l_max)))`, the second term 36,432 at 184 queries | 39,084 | 37,736 | 0.05 bits on `(t + k_q)` at `t = 1` |
| Tree sum `sum (1 + k_i)` of the largest tree (2^14 leaves at 182, 3,616 nodes at their maximum) | `2^22.36` | `2^22.00` | 0.37 bits on the classical union bound |
| `eps_k` of the node (its weakest round) | a query or fold round, about `2^-158.8` | the same | none |

The QROM bound `6 (t + k_q)^2 (eps_k + c' (t + k_q) / 2^256)` depends on the number of rounds
only through `k_q` and `c'`; both fall, by the amounts above. (E, here: arithmetic on the
documents' counts; the calculator's `k_batching` and `batching_rounds` rows are to be restated
and re-run, PB-O3. No row's query count is expected to move; that is for the calculator to
confirm, not asserted.)

**Zero knowledge: not affected.** (1) Zero knowledge is required of leaf proofs only (lead
decision D-c, `zk-quantum.md`); a node proof has no masking to disturb. (2) The batching step
handles no secret: every claim is "an evaluation of a fixed, public, sparse 0/1 object at a
point the transcript chose" (`src/batch.rs`, head), so its values are functions of public bit
vectors and of challenges. (3) The batching sumcheck has no masks; the mask-independence
conditions of [SG26] Lemma 2.27 (c) are not in play. (4) P-sh changes how the points `r` are
derived, not what is revealed: the same claims are absorbed and the same kind of claim is
exported. For the referee: confirm (2) for the wrapper-segment claims of a zero-knowledge
leaf (`Family::of_wrapper_segment`) against `zk-composition.md`.

## 7. Cost (E, here, from B's measured rows; for the B team to count)

From B's 10.3 (M): a verifier message of one 32-byte challenge costs 1,337 AND rows (key
finalisation, one Keccak-f, write-back); a SHA-256 compression is 364, and two 32-byte
coefficients are one block.

| Per global round with `G` active groups | Rows | `G = 4` | `G = 7` |
|---|---|---|---|
| P-seq: `G` messages, each with its two coefficients | `G (1,337 + 364)` | 6,804 | 11,907 |
| P-sh: one message, `2 G` coefficients | `1,337 + 364 G` | 2,793 (2.4 times fewer) | 3,885 (3.1) |
| P-rlc-pad: one message, two coefficients | `1,337 + 364` | 1,701 (4.0) | 1,701 (7.0) |

**Finding PB-4.** By these figures P-sh cuts main's transcript by about 2.4 at four groups of
equal length and less when lengths differ; "about fivefold" is the ratio of verifier messages
or of P-rlc-pad, not of P-sh's rows, because every group's coefficients are still absorbed.
The B team should count (C) both forms before the saving is quoted.

**Prover memory.** In P-seq the group provers run one after the other. In P-sh and P-rlc-pad
every group's prover is live at once, because round `j`'s challenge depends on all groups'
round-`j` messages. B's 13.2 gives 3.7 GiB peak for four claims on one wiring shape; the sum
over the groups of a level-3 node must stay inside the machine limits. To be measured (PB-O4).

## 8. Recommendation

**Adopt P-sh**, with U-1 to U-4 as fixed in section 3, once Lemma P and Lemma R have passed a
referee. Decisive reason: by Lemma P the per-round error is unchanged (the largest over the
groups, 252.09 bits at the weakest round, more than 90 bits above the need), the transcript
stays a total order under Theorem 6.6 (2) with fewer rounds, and nothing zero-knowledge is
touched; the change is confined to our own `src/batch.rs` and `src/node.rs`.

**Then count P-rlc-pad** (one combined round polynomial with `eq(0, .)` padding, the pinned
library's own form) as a second step in a record of its own: it is where the fivefold saving
is, and its only new term is `alpha` over all claims (249.21 bits).

**Never P-rlc-late** (PB-3).

## 9. What is given up

1. A published lemma for the composition: P-sh rests on Lemma P, ours and unrefereed. P-ind
   avoids that at `2 G / |F|` a round and a longer stream.
2. Independent points: the groups' outgoing points share coordinates. Nothing uses their
   independence (remark 4), but any future argument that does must not assume it.
3. Prover memory headroom (section 7).
4. A change of the proof format: node proofs made before and after are not interchangeable,
   so the row or framing version in the statement identifier must change (PB-T5).

## 10. What would reverse it

1. The referee refusing Lemma P or Lemma R: then P-ind, or P-seq as built.
2. A count (C) showing P-sh saves less than the prover-memory cost is worth, with P-rlc-pad
   counted better: then go straight to P-rlc-pad under its own record.
3. A formal treatment of in-circuit transcripts (section 6, first paragraph) that needs the
   groups' transcripts to be separable.
4. A challenge set that is not the same for all groups in a round (for example a group over
   another field): Lemma P does not apply; use P-ind for that round.

## 11. Obligations, tests, and what a referee should attack first

| # | Obligation | Responsible | Acceptance |
|---|---|---|---|
| PB-O1 | U-1 to U-4 confirmed or corrected; the protocol text of P-sh written in `parameters.md` | system B | the text; any difference from section 3 returned to the maths team |
| PB-O2 | Lemma R and Lemma P refereed | referee | written verdict on each proof step and on remark 4 |
| PB-O3 | `k_batching` restated as `n_max + 2` a node and `batching_rounds` as section 5's corollary; tree rows re-run | calculator maintainers | revision note; the rows' query counts stated unchanged or changed |
| PB-O4 | Prover peak footprint with all groups live, level 0 and a merge level | system B | figure under the memory cap, or the scaling evidence |
| PB-O5 | `REFERENCES.md` Part 3 rows for Lemma R, Lemma P, PB-3 | maths team | done with this record (O-71 to O-73; O-74 for the transcript record) |

**Tests the B team must add:**

- PB-T1. The existing reductions in the new form: 1, 2, 5 and 16 true claims in each of 1 to 7
  groups of different `n_g` reduce to true claims (native, witness replay, circuit).
- PB-T2. One false claim in any one group, and one in each of two groups, is refused (native
  run and unsatisfied circuit), for every position of the false group in the group order and
  for the shortest and the longest group.
- PB-T3. Binding: changing any one coefficient of any one group in round `j` changes `r_j` and
  every later challenge and no earlier one; `alpha` changes with any claim element of any
  group.
- PB-T4. Each group's reduced point is the stated suffix of the shared challenges, and the
  reduced claims equal those of P-seq run with those challenges forced (differential test
  against `reduce`).
- PB-T5. A node proof in the old form is refused by the new verifier and conversely; the
  statement identifier differs.
- PB-T6. A test of record for PB-3 on a small field: the late-join form is forged, the padded
  form is not. It guards any later move to a combined round polynomial.
- PB-T7. Count (C): main's AND rows and verifier messages at levels 0 to 3, before and after.
- PB-T8. An exhaustive check of Lemma P's bound on a toy field (two groups, `GF(2^4)`,
  every prover strategy of bounded form): the measured escape probability a round is at most
  the larger of the two groups' errors.

**What a referee should attack first:**

1. Lemma P, condition (ii): is `State_g0`'s bound really independent of what the other
   groups' messages and the shared past contain? The proof uses that Definition 2.24 (a)(ii)
   quantifies over every transcript of the group's own past.
2. Lemma P, condition (i), with end alignment: groups that have not started yet have a fixed
   false claim across several global rounds. Is there any cross-group cancellation of the
   kind in PB-3? (In P-sh the running claims are never added together, which is why not; the
   referee should confirm it from the protocol text of PB-O1, not from this sentence.)
3. Lemma R's last step, as coded: the final check uses prover-supplied `s_o`, and `mu` is
   skipped for one set.
4. PB-3: reproduce the attack; then try it against P-rlc-pad and against the pinned library's
   `batch_verify` with `PaddedProver`.
5. Section 6's first paragraph: the in-circuit transcript's place in the tree accounting.
   Shared challenges make more of a node's soundness ride on single hash outputs; with the
   random-oracle modelling that is immaterial, and a referee should say whether it agrees.

## 12. Provenance

Published, as taken: Definition 2.24 (a), Definitions 2.25 and 2.26, Lemma 2.27, Lemma 5.2 and
the degree-2 round error of Sharp and Grubbs, "Faster and Smaller Anonymous Credentials from
Standardized Signatures", ePrint 2026/2615; Theorem 6.6 (2) and Definition I.1 of the same
paper through `qrom-compilation.md`. The phased prover's source is as B's 13.2 states it (Xie,
Zhang, Zhang, Papamanthou, Song, ePrint 2019/317); it is not used here. Code read: the files
named at the top; the pinned library's batched and padded sumcheck are cited as code, with no
paper attributed. Adapted: Lemma R; P-ind's linearisation. Original (the Ycash developers,
2026) as far as checked, with the sources consulted named in place: Lemma P, finding PB-3,
finding PB-4, the choices U-1 to U-4. System B's proposal itself (parallel rounds) is the B
team's (`parameters.md` 15.7 item 2).
