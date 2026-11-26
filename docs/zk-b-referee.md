# Referee: Theorem C-B, Lemma DC and the rank term of Theorem C

Part of Yugen. Independent second read of `zk-composition.md` section 5.2 (Theorem C-B,
Sim-B, ledger M1 to M12, Lemma DC, Corollary DC) and section 4.2a (the `GF(2^64)`-rank term of
Theorem C), at `yugen-proofs` `a6f044c`, against `yugen-proof-b2` HEAD `7cae341` (read with
`git show HEAD:`) and the rendered CFW26 paper (pypdfium2). Context: `hvzk-referee.md`. Referee
date 2026-11-19. Marks: **(R)** reasoned here; **(S)** read in source, file named; **(P)** read in
the rendered paper, page named; **(C)** computed here; **(N)** not checked.

Verdicts: **Lemma DC (with Corollary DC): PASS WITH CONDITIONS. Theorem C-B / Sim-B: PASS WITH
CONDITIONS. The rank term: FAIL as a proven bound (a buildable fix is given, F-4).**

## 1. Lemma DC and Corollary DC

**Lemma DC, line by line (R).** The bijection `(a_2, b_2) -> (u, v)` for fixed `(a_1, b_1)` is
right (`alpha_2 != 0`). Expanding `alpha_2 a_2 b_2 = (u + alpha_1 a_1)(v + alpha_1 b_1)/alpha_2`
gives exactly `c_1 a_1 b_1 + (alpha_1/alpha_2)(a_1 v + b_1 u) + uv/alpha_2` with
`c_1 = alpha_1 (alpha_1 + alpha_2)/alpha_2`. Completing the product with `s = u/(alpha_1 +
alpha_2)`, `t = v/(alpha_1 + alpha_2)` is right in characteristic 2. The law of `Y = xy` for
independent uniform `x, y` and the distance `1/2 ((Q-1)/Q^2 + (Q-1)/Q^2) = (Q-1)/Q^2` check. The distance is constant in `(u, v)`, so the joint distance equals it: the
"exactly" is earned. The remark on `alpha_1 = alpha_2` (third coordinate `a_1 v + b_1 u + uv/alpha`,
uniform unless `u = v = 0`) is right.

**Corollary DC (R, S).** The decomposition `N = (P + W, l(P))` matches the code:
`precommit_claim = <precommit_packed, fold(M_A + lambda M_B + lambda^2 M_C)^T eq(r_x)>`
(`spartan-prover/src/lib.rs` lines 297-302) and `private_claim = batched_sum - public_eval -
precommit_claim` (line 304); `(a_eval, b_eval, c_eval)` are the MLE evaluations at `r_x` sent after
the zerocheck (`prove_mulcheck`). The coupling and the data-processing step are sound; `l` has
coefficient 1 on `x_A` for every `lambda`. The bound `2 delta` is loose but correct.

**(H-DC) against the code (S).** Holds by construction: `add_blinding_constraints`
(`spartan-verifier/src/constraint_system.rs` lines 46-66) appends, per segment, `a * b = c` with each
operand a single wire of coefficient 1 at indices `n_circuit + n_dummy_wires + 3i..+3`, which no
circuit constraint can name; padding rows are `one * one = one`. The prover fills them with
`a, b` uniform and `c = a b` (`pack_and_blind_witness`, lines 514-520).

**Excluded events (R).** Per `alpha_i`: `eq(r_x, j)` vanishes iff some `r_k` hits one value,
`<= n_x/|K|`, four times; the two differences are nonzero multilinear of degree `<= n_x`, two times;
total `6 n_x/|K|`. Complete for the Corollary's hypotheses. Arithmetic of `eps_B` checks
(`192 * 2^-256 = 2^-248.42`).

**The test (C).** Re-run: `zk-lemma/test_dummy_constraints.py` with the tools venv, all four lines
PASS, exit 0, 38 s, output identical to `results/dummy_constraints.txt`. Part 1 tests the Lemma's
actual claim (TV equality, every admissible pair, GF(16)); part 2 tests the Corollary's claim
(`<=`), at GF(4) only.

## 2. Findings

**F-1 MINOR (Corollary DC, (H-DC) citation).** The cited lines 302-315 are a `#[test]`
(`every_committed_segment_masks_its_revealed_evaluations`) on a toy shape that asserts only that the
dummy-constraint wires *appear* in the relation, not "exactly once, coefficient 1, no other row".
Fix: cite `add_blinding_constraints` (lines 46-66) as the construction that makes (H-DC) true, and
make SB-3 assert exclusivity and coefficient 1 on the padded wallet system.

**F-2 MINOR (test strength).** Part 2's bound `2 delta = 3/8` at GF(4) is far above the observed
`561/8192` and the Lemma's own `delta = 3/16`; a broken Corollary with distance up to `3/8` would
pass. The `alpha_1 = alpha_2` case is printed, not asserted; no control has `alpha_i = 0`; the
"first two coordinates uniform" clause is not checked separately. Fix: in part 2 also assert
`worst <= delta + delta` exactly as computed by the coupling and record the GF(4) worst value as a
regression constant; add controls `alpha_i = 0` (must exceed `delta`) and `alpha_1 = alpha_2` (must
differ from the formula); assert uniformity of `(u, v)` in part 1. Not a weakness in the claim.

**F-3 MINOR (Theorem C-B, `n_x` unread).** Read here (S): `bench/results/cat1-20261119.txt`,
`leafbench-cat1`, "mul constraints 2097152 (log 21)", and `log_mul_constraints =
checked_log_2(mul_constraints.len())` is `n_x`. So `n_x = 21` at the shipping category-1 wrapper
(other builds 2^17 to 2^19, VENDOR.md changes 21, 24, 27). The document's guess `n_x <= 20` from the
wire count is wrong (constraints, not wires) but `n_x <= 32` holds: `eps_B <= 2^-255 + 126 *
2^-256 = 2^-249`. Fix: replace the U/M paragraph with this reading; SB-3 prints it.

**F-4 MAJOR (rank term of Theorem C, section 4.2a).** The uniform-weight model is not justified:
the columns of the `8 x c` matrix are the `K`-coordinates of `eq(z, cell)` (and of the gadget's
weight), which are tensor-structured functions of one `z`, not independent uniform entries; a union
bound over functionals needs, per functional, `Pr_z[Tr(beta_1 w_1(cell) + beta_2 w_2(cell)) = 0
for all cells]`, and no such bound is given. Worse, if the two revealed values use the same point
and the same per-cell weighting, the matrix has rank `<= 4` identically and the leak is certain;
whether they do was not read here (A's code, N). The 72-cell assertion does not repair this: it is a
margin under the same unproven model. Correct term: owed. **Buildable fix (preferred): make it a
public-coin restart, error 0.** The matrix is a public function of `z` and the layout; the prover
computes its `K`-rank after `z` is drawn and restarts (as for blend 0 and `gamma = 0`) if it is
below 8; the term leaves `eps_hvzk^A` and enters only the restart count of the soundness ledger,
where `Pr[restart]` is measured. Also required: a test that the matrix is not rank-deficient
identically at the built shape (sample `z`, compute rank, expect 8), which rules out the same-weight
case. Alternative: prove a bound by a Schwartz-Zippel argument on an `8 x 8` minor written as a
polynomial in `z` (the `K`-coordinates bring in Frobenius powers, degree up to `|K|^3` per entry, so
the naive per-minor bound is only about `8 n/|K|`); not recommended.

**F-5 NOTE (CFW26 Lemma 3.29, Adapted) (P, p. 38).** The paper's statement and proof are for the
monomial-coefficient encoding; the proof separates the first `s <= t` coefficients and uses
injectivity of evaluation of degree `< s` polynomials at `s` distinct points (Lemma 3.9). The
adaptation holds because the novel basis has `deg X_j = j`, so for every `s` the prefix
`X_0..X_(s-1)` spans the polynomials of degree `< s`; the document states only "span the same space
of degree below `q`", which is the `s = t` case. Fix: add the one line "for every `s <= q`, `X_0 ..
X_(s-1)` span degree `< s` (degree-triangular), so the proof of Lemma 3.29 runs unchanged". I
checked (S, `iop/src/basefold/layout.rs`) that the pad is the top `pad_len` coordinates of `M_r`
relabeled by bit reversal onto coefficients `0..q`, and `zk_pad_len = q` at `ZK_LOG_BATCH_SIZE =
1`. With that line the adaptation is proved.

**F-6 NOTE (Sim-B ordering).** Corollary DC is stated for fixed `r_x`, while the zerocheck messages
that produce `r_x` depend on the dummy operands. This is sound in the HVZK setting (all challenges
fixed first, Lemma T order: block 2 then block 3, and the Theorem 6.3 simulator needs only the
final value), but the proof should say that the challenges are fixed before the dummies are drawn.

## 3. Ledger rows against code

Checked (S): M10, M11, N8 (prover lib, as above); (H-DC); M2/M3/M6 pad placement and size
(`layout.rs`); `n_x`. Taken from the B review without reading the code here (N): M1/M1a (salt sizes
per row), M4/M5 (Diamond opening, `w_r`, `gamma` restart), M7/M8 (one-key-per-value, C11, and the
inner target relation), M9/M12 (`zk_mlecheck`, Libra mask size, blend restart), the wiring claim
(1.3). Not checked: the Blueprint's Theorem 6.3 and Diamond's Theorem 4.3 themselves; SB-1 to SB-5
(not built).
