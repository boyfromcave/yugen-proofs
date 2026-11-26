# Referee: Lemma K-A, census A, Lemma RS, Lemma K-B, census B

Part of Yugen. Independent referee, 2026-11-19. Subjects at `yugen-proofs` `72464f2`:
`docs/lemma-k-a.md`, `docs/round-census-a.md` with `soundness/census/a-round-census.json` and
`soundness/src/yugen_soundness/census.py`, `docs/lemma-k-b.md`, `docs/b-round-census.md`. Code read with
`git show HEAD:` in `yugen-proof-a` (HEAD `57cacc2`; the census cites `15b9993`, and between the two only
`merkle.rs` and `transcript.rs` (4 lines) changed in the verifier crate, so the walk read is unchanged). Papers read
from rendered pages with pypdfium2 (`.tools-venv`): [SG26] ePrint 2026/2615 pp. 15–16 (Definition 2.24), p. 58
(Theorem 6.6); [XZZPS19] ePrint 2019/317 pp. 8 and 10.

## Verdicts

| Subject | Verdict |
|---|---|
| Lemma K-A (with Proposition RBR-A) | **PASS WITH CONDITIONS** (M-A1, m-A1, m-A2) |
| Census A | **PASS WITH CONDITIONS** (M-A2 on the row-9 extrapolated rows; m-A3) |
| Lemma RS | **PASS** |
| Lemma K-B | **PASS WITH CONDITIONS** (K-B.2 (R-8) stays an open proof obligation; m-B1, m-B2) |
| Census B | **PASS WITH CONDITIONS** (D-4 unexplained, cannot move a figure; R-8) |

No BLOCKER found.

## Findings

### MAJOR

**M-A1. `State` does not absorb rejection** (`lemma-k-a.md` section 2, "State"; Proposition RBR-A items 2 and 4).
`State = 1` is defined as "`Dec(O_0) != bot` and every pending claim is true". Items 2 and 4 argue "if the check
fails, `V` rejects, a final state 0", but nothing in the definition makes `State` 0 after a failed check: a prover
whose `s_j` fails `s_j(0) + s_j(1) = claim` abandons the false claim, and the next claim `s_j(r_j) = true partial
sum` can be true, so `State` as written can rise to 1 at error up to 1, and (iii) fails for that transcript. The
conclusion survives (such a transcript is rejected), but the state function must say so. **Fix:** define `State = 0`
whenever any verifier check already decidable on `tr|past(i)` (or on `past(i) ∪ {i}`) fails; this is monotone, keeps
(ii) with equality, and makes item 2's and item 4's case split exhaustive. Same one-line change for K-B section 3,
where the deferred inner checks are pending claims (see m-B1).

**M-A2. The row-9 `2^30` (and `2^24`, `2^26`, `2^28`, `2^29`) verdicts rest on an extrapolation that does not hold
as stated** (`round-census-a.md` section 4, rows "E"). The two measured nodes are different programs: 501 is
`node-row9-sub1` (S of one leaf, `2^25`) and 592 the merge of seven (`2^27`). A node's messages outside its opening
are set by its program's bus depth, table and Keccak shape, not by the stack's log; the slope 45.5 per log step is
the effect of the merge's program, so 727 is neither an upper nor a lower bound for a `2^30` node. Use in the project:
the tree's nodes are built at `2^27` (`yugen-proof-a` `docs/recursion.md` table, all `2^27`); no tree shape uses
`2^30`, but row 9's schedule admits every stack `2^16 .. 2^30` (`docs/parameters.md` 2.6, row 9 "60 admitted,
none refused"), so setup accepts the shape. The suggested one-more-query fix is right in method (a query at rate
1/2 adds about 0.415 bits, at 1/4 about 0.678, far above 0.022, and `census.restore` raising each level within the
deficit is the correct rule) but is calibrated to an unsupported count. **Fix:** (1) as the census prefers, measure
`j_v` before a row-9 shape other than `2^25` / `2^27` is used; (2) until then, have row 9's setup refuse (`NoSchedule`)
stacks above `2^27` whose `j_v` is not measured, or bound `j_v` from the program's announced shape with
`census.py`'s walk (it takes bus depth, table rounds and Keccak shape as inputs) at the largest program the node
relation admits, and restore at that bound. Mark the E rows "unknown", not "yes, on the estimate".

### MINOR

**m-A1. The hand-off into the opening should be stated as a conjunction** (`lemma-k-a.md` section 2, attack item
1). Checked: Theorem S's initial doomed condition (`zk-wi-soundness.md` 5.1: "oracle 0 is far or its decoding does
not satisfy `<P, W> = T`") is the negation of K-A's post-`lambda` state, provided "far" is read in `A_{0,0}` at
`e_0` (amendment M-1), as K-A's `Dec` is. One gap of wording: K-A decodes lane by lane, Theorem S measures the
stacked word by rows. Joint proximity (within `e_0` rows) implies every lane decodes to the same `U`, so "not doomed"
implies K-A's `Dec(O_0) != bot` with the same `U`; the converse fails, which only lets `State` fall 1 -> 0 at the
merged ring-switch/`lambda` message, harmless for RBR. **Fix:** write the post-`lambda` state as "K-A's state AND
Theorem S not doomed", and add the one-line implication. Oracles `O_1, ..` enter only through Theorem S's
per-oracle state at their position challenges, as K-A says; I found nothing contrary in `lib.rs`.

**m-A2. Uncommitted layers: correct, should be said with its reason** (attack item (b)). Round-by-round soundness
does not need the claimed values to be committed: the state may be any function of `x`, `Dec(O_0)` and the
transcript ([SG26] Definition 2.24 (a) lets `State` read `U` and the past). The bus trees' layers are deterministic
functions of `O_0`'s columns and of `(weights, beta)`, which are drawn before the GKR (`bus.rs:240-242` precede
`verify_gkr_grand_products`); the Keccak reduction's intermediate states are Keccak's round function applied to the
committed states (a state every 2 rounds, `a-round-census.json`); the masked parts are terms on the mask column of
`O_0` (`bus.rs` comment "values_true[t] = values[t] + ..."). So `Dec(O_0)` defines every layer's true value.
**Fix:** add that sentence and the code citations to section 2 "Claims".

**m-A3. Census table, "Draws" column** (`round-census-a.md` section 3). The rows sum to 515, not the 525 stated.
`census.py:134` draws `y` with `step` coordinates (1 after the odd first layer, 2 after the others), so the row
"`y` + next combiner + `rho`" carries 39 draws, not 30. Messages (412, 445) and errors are unaffected. **Fix:** take
the column from `census.py`'s output and re-add.

**m-B1. K-B's `State` must list the deferred inner checks as pending claims** (`lemma-k-b.md` section 3 item 2).
The step "the inner messages are fixed by the precommit keys before the first challenge" is, as the lemma actually
words it, right: `k_i` is in `Dec(O_pre)` before any challenge and `m_i = c_i - k_i` is a function of the transcript
once `c_i` is sent; the ciphertext is still chosen adaptively, exactly as a clear message would be, so the inner
round-by-round analysis applies to `m_i` at the time `c_i` arrives. But the inner verifier's checks are not run in
clear (`assert_zero` is deferred), so a failed inner check does not reject at once: it must stay as a false pending
claim of the wrapper until the MLE-check. **Fix:** in section 3, "every pending claim" includes each deferred
`assert_zero` equation on the `m_i`; with M-A1's absorbing rule this closes the case.

**m-B2. The state's signature omits the wrapper's later oracles** (`lemma-k-b.md` section 2, Hypotheses). `State(x,
Dec(O_pre), Dec(O_tr), tr)` cannot read the private and mask oracles' decodings that section 3 item 2 needs.
**Fix:** write `State(x, tr)` with the decodings of all oracles in `tr|past(i)` (as Theorem S's per-oracle state
does); the extractor stays `wit(Dec(O_tr))`.

### NOTE

- **N-1. Merge rule against [SG26].** Definition 2.24 (p. 15): a round is a prover message `a_i` followed by one
  uniform challenge `theta_i` in a finite set `C_i`; draws with no prover item between are one `theta_i` in a product
  set. Theorem 6.6 (2) (p. 58) charges `(t + k_q) eps^k` with `eps^k` a bound on every round, so the count enters
  through `k_q`, and a merged round's error is the sum of its sub-draws' errors by sequential conditioning. The
  census's rule is right. I did not read [SG26] Lemma 5.2 (p. 37), which K-B and census B cite.
- **N-2. Citations.** XZZPS19 p. 8 says "complete and sound with eps = d l / |F|" and p. 10 gives the random
  linear combination with two independent coefficients `alpha, beta` and Theorem 1 as `O(d log |C| / |F|)`: as
  quoted. The bus combiner is powers of one challenge, so the error 2 is Schwartz-Zippel on a univariate of degree
  `N_TREES - 1`, not XZZPS19's form; label it Adapted.
- **N-3. Initial claims are `R_leaf`** (attack item (c)): I checked only that `R_leaf` is defined existentially
  over the non-witness stack ("the stack whose carried witness slots are `w` satisfies ..."), which is what makes
  (i) follow; that the verifier's first claims are the whole leanVM constraint system was not checked (upstream's
  arithmetization, as the author says).
- **N-4. K-B 127 vs 131.** Not resolved here; the all-merged bound (232.0 / 225.0 bits) covers every grouping and
  the every-`t` need uses the T-1 `k_q`, so it cannot move a figure. Owed as stated (T-1 per-key trace).
- **N-5. R-8** (lifted oracles) remains a proof obligation; the census says so correctly; the margin does not
  replace a lemma.

## Lemma RS (checked in full)

`GEN = E::new(2, 0)` is `x` in `K = GF(2)[x]/(x^64 + x^4 + x^3 + x + 1)` (`field.rs:121`, `times_x` reduces by
`0x1B`). Computed: `x^(2^64) = x` and `x^(2^32) != x`, so `x` has degree 64 over GF(2) and its 64 conjugates are
distinct: `GEN` generates `GF(2^64)`. `K` sits in the 128-bit field and in `E2 = E[z]/(z^2 + z + c)` (the `e2`
crate, `Cargo.toml` header), so `(.)^(2^-k)` is the automorphism of the challenge field and acts on `K` as
`2^(-k mod 64)`. The proof's steps hold: `A_k = 0` for all `k < 64` gives `sum_i y_k^i d_i = 0` at 64 distinct
`y_k`, a 64 x 64 Vandermonde system, so `d = 0`; some `B_p` is a nonzero linear form in `g` after the inverse
Frobenius (`1/|E|`), then `P` is a nonzero linear form in `f` (`1/|E|`). The code matches the map
(`ring_switch.rs`: 8 `f_p`, 8 `g_b`, `ring_target` with `z_p = x^(2^(64-8p))` computed by `frobenius_8` from `GEN`,
correct only because `GEN` is in `K`). PASS.

## Census A spot-checks against the code

| Row | Code | Census | Agrees |
|---|---|---|---|
| bus fingerprint | `bus.rs:240-242`: grind `round_bits(1 << depth)`, `samples(1 << BUS_BITS)` then `sample()`, no item between | 1 msg, 17 draws, `2^21` | yes |
| bus combiner | `bus.rs:54`: `round_bits(N_TREES - 1)` | error 2 | yes |
| bus `y` | `bus.rs:116-117`: `round_bits(step << last)`, `samples(step)` | `step`, doubled at last | yes (draw column, m-A3) |
| Keccak `s` | `keccak.rs:186`: `round_bits(PRODUCT_BITS - 1)` | 46 | yes |
| Keccak `beta`; segment and lane point | `keccak.rs:239` `round_bits(2)`; `keccak.rs:321` `round_bits(segment_bits + LANE_BITS)` | 2; 6 (+1 public, merged: 7) | yes |
| table `xi` | `lib.rs:447`: `round_bits(n_powers - 1)` | 4 | yes |

## What I did not check

The zero-knowledge rounds' states (`zk-wi-soundness.md` Lemma 6, 6.3; `zk-system-a-gaps.md`); Theorem S itself and
Lemma D; that the bus balance with its count tree is leanVM's memory and bytecode consistency (and so whether the
fingerprint's degree bound `2^mu` covers the pull side with counts); the Keccak reduction's correctness; the 445 /
411 counts beyond the census test's assertion (nothing run); [SG26] Lemma 5.2 and Definition 2.20 (I read 2.24 and
6.6); census B row by row against `yugen-proof-b2` (only its structure and arithmetic were read), `pbatch.rs`,
Lemma P, and the ring switch, skip and shift states (K-B.4); the row-9 query lists of the fix against
`census.restore`.
