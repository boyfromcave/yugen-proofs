# Referee: the code of P-sh (system B, parallel-round node batching) at yugen-proof-b2 `3f1f081`

Scope: `src/pbatch.rs` (whole file), `src/node.rs` 392-420 (`batch_parallel`, `group_inputs`),
540-550 (circuit build), 700-735 (witness replay), `docs/parameters.md` 17.3 and 17.10.
Design reference: `docs/b-batching-and-hash-referee.md` (Lemma P, C-1..C-8, RT-1..RT-6).
Read from `git show 3f1f081:<path>`. No test was run by the referee; test results are the builder's
(`bench/results/tests-20261120-p.txt`), not re-verified.

## 1. Conditions in the code

| | Verdict | Evidence (src/pbatch.rs) |
|---|---|---|
| C-1 | met | running claims `claims[g]` built per group at 239-251; only write is 285, indexed by the group's own `g`; `c1 = claims[g] + c2` (284). No expression combines two groups. Final check per group, 309-334. |
| C-2 | met | label 223-225, then every bound element 229-232, then `alpha` 237. All `s_o` absorbed 296-303 before `mu` 338-342 (built rules). |
| C-3 | met | in each round, loop 263-271 observes every active group's `c0, c2` before `sample` 273; prover gets `current: None`. |
| C-4 | met | `Schedule::of` reads shapes only (102-109); schedule and claim counts hashed into the label (147-167). |
| C-5 | met | one `r` folded and pushed for every active group, 280-287. Point = last `n_g` challenges (`start`, 112-114; assert 310). |
| C-6 | met | `assert_zero` per group at 333, before `mu` is drawn (338). One-set group exports `[1]`, its `s`, no `mu` (348-349). |
| C-7 | met on the builder's reading, accepted (section 2) | |
| C-8 | met as far as read | `pbatch::run` is reached from `node.rs` only (`git grep pbatch` at `3f1f081`). |

End alignment: a group not yet active absorbs nothing and its running claim stays at its
round-0 value (fixed after `alpha`, its claim elements bound before `alpha`). This is the
end-aligned statement of Lemma P (late start, own running claim, no padding); the excluded
PB-3 form (adding a late group into a common claim) is not expressible here.

Manipulations tried (on paper):
- draw `r_j` before a group's coefficients: the `draw_before_last_group` switch; RT-2 reports forged under the switch, refused under built rules. Caught.
- `mu` before last `s_o`: `mu_before_last_finals`; RT-2. Caught.
- `alpha` before some bound element: no switch exists; only `pbt3` (changing a bound element changes the transcript) bears on it. A reorder in code would not be caught by a forging test. MINOR-2.
- summing two groups' claims (PB-3): RT-1 / RT-6 forge it in the toy and refuse the built code. Caught.
- same error in two groups cancelling: RT-3. Caught.

## 2. C-7 reading: accepted

A P-sh node and a sequential node are different constraint systems (different transcript
operations, different row counts, `pbt5_pbt7`), so their key digests differ, and the key digest
enters the statement identifier. A proof under one key cannot verify under the other key; the
builder's `recbench ucross` reports exactly that on real level-3 roots (not re-run). The in-circuit
label (`VERSION`, schedule, counts) additionally separates inner transcripts. Leaf identifiers
need not move: leaves do not contain the step (C-8). Caveat: MINOR-1.

## 3. In-circuit equivalence: same protocol, by construction

The circuit (`node.rs` 542-549, `Binius64BuilderChannel`), the witness replay (`run_native` over
`WitnessFillerChannel`, 727-731) and the native reference all call the one function
`pbatch::run` with `Rules::default()`; only the channel and the message/finals closures differ.
Order, absorption, `alpha`, `mu` and the final `assert_zero`s are therefore the same code path.
The label is a compile-time constant in the circuit (observed, then asserted equal to the
constant). Not checked: that `Binius64BuilderChannel::observe_one` makes the prover values
private witness wires bound into the in-circuit sponge (vendored code, not read here).

## 4. G-3 justification: accepted

The child proof is private witness of the slot, the recorded verifier reads a fixed-length tape,
and nothing hashes the raw proof bytes into a public value. Trailing bytes therefore cannot
change what the circuit accepts or exports; the statement proven is identical with or without
them, and extraction reads the consumed prefix only. The native `finalize` refusal is a
canonical-encoding rule (non-malleability of the byte string), not a soundness condition of the
proven statement. Acceptance holds only while no digest of the child proof's bytes is ever
made public or bound to an identifier; if that changes, G-3 must be built (NOTE-1).

## Findings

- **BLOCKER:** none. **MAJOR:** none.
- **MINOR-1** `src/node.rs:494` `build_sequential` is public library code. A verifier or chain
  configured with a sequential node key accepts sequential proofs; C-7 then rests on
  configuration. Fix: put `build_sequential` behind `#[cfg(any(test, feature = "differential"))]`.
- **MINOR-2** `src/pbatch.rs:75-83` no mutation switch for C-2's first half (`alpha` before the
  last bound element) or for C-6 (final checks after `mu`). Fix: add `alpha_before_last_bind`
  and a forging test as in RT-2.
- **MINOR-3** `src/pbatch.rs:75-83, 170-179` `Rules` and `Ask::current` are a public API that can
  hand the prover the current challenge. Fix: gate the mutating fields under `cfg(test)` or a
  test feature, so a production build cannot construct them.
- **NOTE-1** G-3: record in `docs/parameters.md` 17.10 the condition under which the
  justification fails (child proof bytes hashed into anything public).
- **NOTE-2** `src/pbatch.rs:165` the non-recursion build `unreachable!`s in `label`; harmless, a
  compile-time gate would be cleaner.

## Verdicts

- P-sh code: **PASS** (minor fixes above).
- C-7 reading (key digest as format version): **ACCEPTED**, with MINOR-1.
- In-circuit equivalence of P-sh: **PASS** (one code path), vendored channel not read.
- G-3 justification: **ACCEPTED**, conditional per NOTE-1.

Not checked: tests not run; vendored channel internals; prover-side variable order vs claim point
order (relied on `pbt1`); `group_claims` / flag weighting in `node.rs`; zero-group handling soundness
beyond its being prover-only.
