# Lemma K-A: round-by-round knowledge soundness of system A (DRAFT, revision 2026-11-19)

Part of Yugen. Maths team, 2026-11-19. Obligation K-A of `what-is-proven.md` (hypothesis (K) of
`lemma-tree-extraction.md` revision 3, section 2; `qrom-compilation.md` H3, T-5), completing the draft Lemma K-A
of `theorem-s-referee.md` section 4. **Original (the Ycash developers, 2026), DRAFT until refereed**; REFERENCES.md
O-87. Code: `yugen-proof-a` HEAD `15b9993`. Rounds and errors: `round-census-a.md`; sumcheck and GKR terms checked against [LFKN92], [GKR15] (`citation-check-lfkn-gkr.md`, 2026-11-19). Theorem S as amended
2026-11-19 (`zk-wi-soundness.md` 5.1, amendments M-1, m-1, m-2).

## 1. What is needed

(K) asks that each IOP of the tree be causal round-by-round knowledge sound in the sense of [SG26] **Definition
2.20** (C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, ePrint
2026/2615, p. 14, read from the rendered page 2026-11-19): a polynomial-time extractor `E(x, tr|past(i))` and a state
function `State(x, i, tr|past(i))` (and on `past(i) ∪ {i}`) such that for every statement `x`

- (a) every full transcript that `V` accepts with `(x, E(x, tr|past(i))) not in R` for every `i in J_V` has some `i`
  with `State(x, i, tr|past(i)) = 0` and `State(x, i, tr|past(i) ∪ {i}) = 1`;
- (b) for every `i` and every transcript of `past(i)` with `State = 0`, `Pr[State(x, i, tr||theta_i) = 1] >
  eps_i^k(x)` implies `(x, E(x, tr)) in R`.

Under a total order this is [CMS19] Definition 8.5 with per-round errors ([SG26] **Lemma 2.21**, p. 15). A's leaf
IOP is run with the total order of its messages (one transcript, `lib.rs` `walk`), so either form serves. The
relation, as the tree lemma uses it: `R_leaf` = `{(x, w)}`: the stack whose carried witness slots are `w`
satisfies the leaf constraint system for `x` (the leanVM program's bus balance, table constraints, Keccak rows and
the public-input binding), the masks being free.

## 2. The rounds as round-by-round soundness in terms of `Dec(O_0)`

**Setting.** `O_0` is the first prover oracle: the stack (trace columns, then the mask region, `lib.rs` "the mask
column and the gadget column follow the trace's columns in the stack (oracle 0), so they are committed before every
challenge"). It is received before the first challenge (the root is read before `read_ood` draws `z`). `Dec(O_0)` is
its lane-by-lane unique decoding in the admissible code `A_{0,0}` within `e_0 = floor((N_0 - lf_0)/2)` (amendment
M-1), or `bot`. `wit(U)` is the carried witness slots of `U`.

**Claims.** At every point of the walk the verifier holds a finite list of *pending claims*. Outside the opening each
is an equation between a value the verifier computed from the transcript and a function of `Dec(O_0)` and public
data: an evaluation of a committed column's multilinear extension at a point, a sum over the hypercube of a
polynomial in such extensions (a sumcheck claim), a GKR layer value of the bus trees or of the Keccak reduction
(the trees' layers and the reduction's intermediate states are functions of the committed columns and of the
challenges drawn before them, so they are functions of `Dec(O_0)` and the past), a linear claim on the mask region.
*Why claims on uncommitted layers are sound* (revision 2026-11-19, m-A2): round-by-round soundness does not need a
claimed value to be committed, only that its true value is fixed by what `State` may read, and [SG26] Definition 2.24
(a) lets `State` read `x`, `Dec(O_0)` and the past. The bus trees' layers are deterministic functions of `O_0`'s
columns and of `(weights, beta)`, which are drawn before the GKR (`bus.rs:240-242` precede
`verify_gkr_grand_products`); the Keccak reduction's intermediate states are Keccak's round function applied to the
committed states (a state every 2 rounds, `soundness/census/a-round-census.json`); the masked parts are terms on the
mask column of `O_0` (`bus.rs`, "values_true[t] = values[t] + .."). So `Dec(O_0)` defines every layer's true
value.
The initial list at the first challenge is `R_leaf`'s constraint system for `Dec(O_0)`. After the ring switch and
`lambda` the list is the single opening claim `<Dec(O_0), W> = T`, Theorem S's starting relation.

**State** (revised 2026-11-19, referee M-A1). `State = 1` iff `Dec(O_0) != bot`, **no verifier check decidable so
far has failed**, every pending claim is true for `Dec(O_0)`, and, inside the opening, the state of Theorem S
(amended) is not doomed. **The pending claims, the checks and the opening's state are updated only at verifier
messages**: the update at message `i` reads the prover messages sent since message `i - 1` (round polynomials,
claimed values, oracles `O_{j+1}`, `mu`, `P*`) together with `theta_i`, and runs every verifier check that those
messages (with the past) decide, such as `s_j(0) + s_j(1) = claim` or a terminal check. *Absorbing rule:* once any
such check has failed, `State = 0` at that update and at every later point, whatever the later claims are. (Without
the rule a prover that fails a check drops the false claim, the next claim can be true, and `State` could rise to 1
at error up to 1.) Hence `State(x, i', tr|past(i')) = State(x, i, tr|past(i) ∪ {i})` for consecutive verifier
messages `i < i'`. From `Dec(O_0)` through the ring switch the post-`lambda` state is **K-A's state AND Theorem S
not doomed** (m-A1): Theorem S's initial doomed condition (`zk-wi-soundness.md` 5.1, "far" read in `A_{0,0}` at
`e_0`, amendment M-1) is the negation of the post-`lambda` claim; joint proximity of the stacked word (within `e_0`
rows) implies that every lane decodes to the same `U`, so "Theorem S not doomed" implies `Dec(O_0) != bot` with the
same `U`. The converse fails, which only lets `State` fall from 1 to 0 at the merged ring-switch/`lambda` message,
harmless for (iii).

**Proposition RBR-A (Original (the Ycash developers, 2026), DRAFT).** For every verifier message `i` of a row-8 (or
row-6) leaf proof and every transcript of `past(i)` with `State = 0`,
`Pr_{theta_i}[State(x, i, tr||theta_i) = 1] <= eps_i`, where `eps_i` is the error of message `i` in
`round-census-a.md` section 3 (outside the opening) and in Theorem S's table (in the opening; amended).

*Proof, by the kind of message.* If `Dec(O_0) = bot`, no message outside the opening changes that, so `State` stays
0 there (error 0); in the opening a far oracle 0 is Theorem S's doomed start. Otherwise some pending claim `C` is
false for `U = Dec(O_0)`, and `theta_i` must make every new claim true:
1. *OOD point* (`z`): no claim is reduced; `C` stays pending and false (error 0; `round-census-a.md` 2.2). The OOD
   value sent after `z` is a new claim on `U`, true or false; it changes no false claim into a true one.
2. *Sumcheck round* (bus GKR, bytecode share, table, Keccak, openings, tail): `C` is "`s_{j-1}(r_{j-1})` equals the
   true partial sum at `U`". If the message `s_j` fails `s_j(0) + s_j(1) = claim` (or the `eq`-form check), the
   update at `r_j` runs that check, and by the absorbing rule `State` is 0 whatever `r_j` is (error 0). Otherwise `s_j` differs from the true round polynomial for `U`, and
   the new claim is true only if `r_j` is a root of their difference: `d_j/|E|` (2.1; [GKR15]
   Lemma 2.5, proof step (3); for the `eq`-form check, valid because the full round polynomial is
   determined by the message and the claim, Original; citation amended 2026-11-19).
3. *Batching challenge* (bus-tree combiner, `xi`, Keccak `beta`, gadget `theta`, stacked `lambda`): the new claim is a
   polynomial in the challenge whose coefficients are the old claims' errors; one false claim makes it nonzero of
   degree at most `n - 1` (2.4, 2.5, 2.7).
4. *Line to a point* (bus `y`, Keccak `s`, segment and lane point, public challenge): the claimed vector of values
   differs from the true one for `U` (else the terminal check that fixed it has failed, and `State` is 0 at this
   update by the absorbing rule, error 0); their extensions
   differ as polynomials of degree at most `deg` in the challenge, which is a root with probability at most
   `deg/|E|` (2.4, 2.5, 2.7) (GKR15 reduces two claims by a line, p. 27:31; the
   multilinear-extension form here is Schwartz-Zippel, Original; amended 2026-11-19).
5. *Fingerprint* (`weights`, `beta`): `C` is "the push and pull multisets of `U`'s tuples are equal"; false, the two
   fingerprint products differ as polynomials of degree at most `2^mu`, and the new claim (equal products) is true
   with probability at most `2^mu/|E|` (2.3).
6. *Ring switch* (`f`, `g`): Lemma RS (2.6), `2/|E|`; merged with `lambda` (3.), at most `513/|E|`.
7. *Zero-knowledge challenges* (`rho`, dummy rounds, gadget `c`, `z`): `zk-wi-soundness.md` Lemma 6 and section
   6.3, whose states are already pending claims on the trace and mask region of `U` (masked head `rho f + g`,
   `Gtilde` and the final values as linear claims on the mask column, discharged by the gadget into two point
   claims on `U`).
8. *Opening* (`rho_i`, folds, positions, `c`, last positions, tail): Theorem S as amended (M-1: decoding in
   `A_{i,j}`; m-1: the tail rounds).

A message that merges several draws (`round-census-a.md` 1) is the composition of their sub-steps; its error is at
most the sum. ∎

## 3. Lemma K-A

**Setting.** A's leaf IOP with the total order of its messages; `O_0` the first prover message; `Dec`, `wit` as in
section 2.

**Hypotheses.** A function `State` of `(x, i, tr|past(i))` (and of `past(i) ∪ {i}`) such that
- (i) at the first verifier message `i_1`, `State(x, i_1, tr|past(i_1)) = 0` if `Dec(O_0) = bot` or
  `(x, wit(Dec(O_0))) not in R_leaf`;
- (ii) for consecutive verifier messages `i < i'`, `State(x, i', tr|past(i')) = 0` whenever
  `State(x, i, tr|past(i) ∪ {i}) = 0` (a prover message never moves `State` from 0 to 1);
- (iii) for every verifier message `i` and every transcript of `past(i)` with `State = 0`,
  `Pr_{theta_i}[State(x, i, tr||theta_i) = 1] <= eps_i`;
- (iv) `V` rejects every full transcript whose last verifier message `i_L` has `State(x, i_L, tr|past(i_L) ∪
  {i_L}) = 0`.

**Conclusion.** With `E(x, tr|past(i)) := wit(Dec(O_0))` (Berlekamp-Welch on each lane of `O_0` in its own code
`C[lrow_0 + g_b]` over `D_0`, polynomial time in the oracle's length; `bot` if a lane does not decode), the IOP is
causal round-by-round knowledge sound with `eps_i^k = eps_i` in the sense of [SG26] Definition 2.20.

**Proof.**
- *Well defined and causal.* `O_0` precedes `i_1`, so `O_0` is in `past(i)` for every verifier message `i`; `E` reads
  only `O_0` and is the same function at every `i`.
- *(b).* Let `tr` be a transcript of `past(i)` with `State = 0`. By (iii) the probability that `State` becomes 1 is at
  most `eps_i = eps_i^k`, so the premise of (b) is false and (b) holds.
- *(a).* Let `tr` be a full transcript that `V` accepts and on which `E` fails at every `i`. `E` is constant along
  `tr`, so `(x, wit(Dec(O_0))) not in R_leaf` or `Dec(O_0) = bot`; by (i), `State(x, i_1, tr|past(i_1)) = 0`. Since
  `V` accepts, (iv) gives `State(x, i_L, tr|past(i_L) ∪ {i_L}) = 1`. Write `s_k^- = State(x, i_k, tr|past(i_k))` and
  `s_k^+ = State(x, i_k, tr|past(i_k) ∪ {i_k})` for the verifier messages `i_1 < .. < i_L`. By (ii), `s_k^+ = 0`
  implies `s_{k+1}^- = 0`. The sequence `s_1^-, s_1^+, s_2^-, .., s_L^+` starts at 0 and ends at 1, and never rises
  from a `+` entry to the next `-` entry; so some `k` has `s_k^- = 0` and `s_k^+ = 1`, which is (a) at `i = i_k`. ∎

**How A meets the hypotheses.** With `State` of section 2:
- (i) by definition: at `i_1` the pending claims are `R_leaf`'s constraint system for `Dec(O_0)`;
- (ii) by construction: `State` changes only at verifier messages (with equality, which is more than (ii) asks; the
  absorbing rule keeps this, since a check is run in the update of the verifier message that follows the prover
  message deciding it);
- (iii) is Proposition RBR-A, with `eps_i` the census errors (`round-census-a.md` 3) and Theorem S's;
- (iv): after the last message the pending state is Theorem S's final state; a doomed final state is rejected
  (Theorem S; Lemma 5 with the tail of amendment m-1); a transcript with a failed check is rejected by that check,
  which is what the absorbing rule records.

So K-A holds with `eps_i^k = eps_i`: the knowledge errors are the soundness errors of the census and of Theorem S.
The largest is a query round of the opening (157.48 bits at row 8, mode 0, rate 1/4); every round outside the
opening is at most `2^-235`.

## 4. Status, and what a referee should attack first

DRAFT, unrefereed. In order:

1. **The hand-off into the opening.** Section 2's `State` reads claims on `Dec(O_0)` until `lambda` and Theorem S's
   per-oracle state afterwards. Check that Theorem S's initial doomed condition is exactly "`State = 0` after
   `lambda`" (oracle 0 far from `A_{0,0}`, or `<Dec(O_0), W> != T`), with `W` the batched weight including the
   blinder blocks' cells, and that oracles `O_1, ..` enter `State` only at the position challenges (Lemma 4).
2. **Claims on uncommitted layers.** Proposition RBR-A treats the bus trees' inner layers and the Keccak reduction's
   intermediate states as functions of `Dec(O_0)` and the past challenges. Check that every such claim is fixed
   before the challenge that reduces it (the fingerprint challenges precede the GKR; the Keccak instance point is the
   table sumcheck's).
3. **The initial claims are `R_leaf`.** That `R_leaf`, as the constraint system the verifier's first claims express,
   is what the wallet statement means (the program's correctness, leanVM's arithmetization of memory and bytecode by
   the bus with its count tree) is upstream's and outside K-A; a referee should confirm only that the verifier's
   first claims are that system and not less.
4. **Lemma RS** (`round-census-a.md` 2.6), in particular that `GEN` generates `GF(2^64)`.
5. **Merged messages.** That the union bound inside a merged spBCS message is legitimate for (iii) (the message is
   one challenge `theta_i` drawn uniformly from a product set).
6. **The zero-knowledge rounds' states** (`zk-wi-soundness.md` Lemma 6, 6.3; `zk-system-a-gaps.md` 3.5, 11),
   skimmed, not refereed, by `theorem-s-referee.md`: they must be phrased as pending claims on `Dec(O_0)`'s mask
   region, as section 2 item 7 assumes.
7. **Duplicate positions** (Lemma D, `lemma-d-duplicate-openings.md`): that the position challenges' state
   transitions in Theorem S are unaffected by repeated positions (refereed elsewhere).

## 5. Revision 2026-11-19 (after `knowledge-and-census-referee.md`: PASS WITH CONDITIONS)

- **M-A1** (absorbing state): `State` is 0 once any check already decidable has failed (section 2, "State"). Each
  step re-checked against the fixed definition: (i) unchanged (no check is decided before `i_1`); (ii) still holds
  with equality, because checks are run in the update of the next verifier message; (iii) items 1, 3, 5, 6, 7 and 8
  are unchanged (they never used rejection), items 2 and 4 now end "`State` is 0 by the absorbing rule, error 0"
  in place of "`V` rejects", which makes their case split exhaustive; (iv) unchanged, with one clause added; the
  proof of the lemma (well defined, (a), (b)) is unchanged. **No step needed more than the definition change** and
  the rewording of items 2 and 4.
- **m-A1**: the post-`lambda` state is "K-A's state AND Theorem S not doomed", with the one-line implication
  (section 2).
- **m-A2**: why claims on uncommitted GKR and Keccak layers are sound, with the code citations (section 2,
  "Claims").
- Status: refereed (pass with conditions), conditions applied here, pending the referee's re-read.
