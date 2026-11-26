# Referee: System B carried-claim fold (parameters §24.1–24.2, option (c))

Tree: `yugen-proof-b2/wt/s045`, branch `agg`, head `03d5c6c`. Files: `docs/parameters.md:4604-4653`,
`src/fold.rs`, `tests/fold.rs`, `src/pbatch.rs`, `src/node.rs`. Tests not re-run (read-only review).
Papers: none used. The pattern is a deferred-claim (accumulation) step; no accumulation paper is in
the reference-paper collection (REFERENCES.md), so none is cited here, and the "folklore" provenance in §24.1 stands
as written.

**Verdict: PASS WITH CONDITIONS.** The algebra is right; the soundness argument is not yet in the
circuit that will carry it, and the tests overstate what is refused in circuit.

## 1. Stacking

- Identity: `stacked` (`src/fold.rs:49-58`) places kind `k` at index `i | k<<n`, which is the MLE of
  the concatenation; `evaluate` (`:92-103`) is `sum_k eq(s,k) W_k(r)` with `eq` in char 2
  (`1 + s_b` = `1 - s_b`). Exact at Boolean `s`. Correct.
- Same shape: `stacked` asserts equal `n_vars` and one set (`:54`); the node side relies on
  `Uniform::n_wiring` being one value for all four kinds (the fixed point in `vplan`, §24.3). That
  fixed point is **not run** (§24.3), so "same n for all four, padding included" is asserted, not
  shown on the real systems. Condition 1.
- Selector binding: `selector` (`:61-63`) is correct **only if** the indicators are 0/1, exclusive
  and sum to 1. With free indicators the prover chooses any `s in F^2`, and `W*(r,s) = v` is one
  linear condition in `s_0` (for fixed `s_1`), generally solvable: a false own claim `W_f(r) = v`
  becomes a **true** `W*` claim at a non-Boolean `s`, and the fold then discharges correctly. This is
  a full break of the own-claim check unless the indicators are constrained.
  - `src/node.rs:600-603` already makes the four indicators as `select(icmp_eq(f, k), 1, 0)` from the
    child's kind word `f`: Boolean and one-hot by construction. Good, **if** the fold uses exactly
    these wires and `f` is bound to the child's key/digest (P3, `b-internal-node-referee.md`
    condition 5).
  - The fold is not yet wired into `NodeMain` (§24.1 "Not done"; `node.rs:294-301` still has four
    places). In `tests/fold.rs:191` the indicators are **unconstrained private witnesses**.
- Another kind's slice: natively refused by the honest prover (`tests/fold.rs:93,149-151`); with
  bound one-hot indicators the claim lands on `W_g` and is refused at the final discharge except
  with batching error. Sound once condition 2 holds.

## 2. Batching carried + own as one group

- Ordering: `pbatch::run` binds every claim element, flags and indicators before `alpha`
  (`src/pbatch.rs:250-269`, C-2), round messages absorbed before each challenge (C-3), final
  check `assert_zero` (C-6). The test's `bind_of` (`tests/fold.rs:65-73`) includes the indicators
  and flags. Fiat–Shamir order is correct.
- Error per node: `(m - 1)/|F|` for the `alpha` powers (`m = 2 x slots` claims) plus `2(n+2)/|F|`
  for the sumcheck (degree 2 a round) — about `2^-120` at `n = 70`, 16 slots. Previously four groups
  of `n`; the union is smaller, not larger.
- Depth: a false claim stays false through a node except with that error; errors add over the nodes
  the tree reaches (`<= N + 16`, `lemma-tree-extraction.md:368`). Linear in node count, not
  compounding per level. It is **not in `k_q`** (it is a statistical, not a query, term) and §24.2
  does not state where it is counted. Condition 3.
- Semantics change: a node's circuit no longer checks its children's wiring; it defers it. The
  node relation is now "accepts **and** its carried `W*` claim is true", discharged only at the
  final verifier. The tree-extraction lemma treats each node's relation as self-contained.
  Condition 4.
- Flags: `group_claims` (`fold.rs:80-84`) scales weights and value by `flag`; any nonzero flag is
  equivalent, flag 0 drops the claim (`tests/fold.rs:152-159` documents it). Soundness needs the
  flag fixed by the kind rules (internal-0 child only). Condition 2.

## 3. `k_q`

- `Schedule::verifier_messages = 1 + n_max + mu` (`pbatch.rs:150-152`); one group of `n+2`, one set,
  no `mu`: `+2` messages a node is the whole change in verifier messages. The schedule label
  changes (group count 4 -> 1), bound in the key digest (C-4); no query count change.
- Certify the **conservative** row (40,564, margin +0.7787): it covers the in-node transcript
  whether or not `t1-hash-queries.md`'s exclusion is accepted, and costs 0.005 bits. All three rows
  are figures for the projected one-place `NodeMain`, not measured on it (four-place form still
  built). Condition 5.

## 4. Tests

- The "refusals" (native and "in circuit") are **honest-prover failures**: `run_native` computes
  the true sums, so a false claim makes the final `assert_zero` fail
  (`pbatch.rs:444-498`), and `Circuit::satisfied` returns `false` on that `Err`
  (`tests/fold.rs:225-230`) **before** the constraint system is checked. A cheating prover supplies
  `s_o` equal to the running claim and the recorded step is satisfied, exporting a false `W*` claim;
  by design only the final discharge refuses it. So: no test shows a constraint-level refusal, and
  none should be expected for false values; the test names should say so.
- Forged selector in circuit: not exercised — indicators are free witnesses (`:191`), and the
  "false kind" case uses one-hot indicators of another kind, refused again by the honest prover.
  A non-Boolean forged selector (the attack in section 1) is untested. Condition 6.
- Missing: an adversarial end-to-end test (false child claim, prover-chosen messages, circuit
  satisfied, root `fold::holds` false).

## 5. Interactions

- `b-internal-node-referee.md` conditions 4-5 (KI0, keys asserted parent-to-child, foreign KI
  refused): the fold's soundness now depends on them, because the kind word `f` that makes the
  selector must be the child's real kind. KI0 exists as kind 3 here (`fold.rs:42`), consistent with
  condition 4.
- `lemma-tree-extraction.md`: SHAPE-VIOLATION and the node count are unaffected; the per-node
  relation and the union term change (condition 4).

## Conditions

1. Run the `vplan` fixed point and show one `n_wiring` for all four kinds on the real systems, with
   the padding rule stated (zero rows of `W_k` beyond its own wiring).
2. When the fold enters `NodeMain`: the selector made from the `icmp_eq` indicators of
   `node.rs:600-603` (no new witness wires), `f` bound to the child's key per P3 / internal-node
   condition 5, and the carried flag fixed by the kind rules (0 only for an internal-0 child).
3. State the per-node batching error `((m-1) + 2(n+2))/2^128` and its sum over `<= N + 16` nodes in
   §24.2 and in the theorem's statistical term.
4. Amend `lemma-tree-extraction.md`: node relation = verifier accepts and carried `W*` claim true;
   extraction is conditioned on the root discharge; add the deferred-claim union term.
5. Certify the conservative `k_q` 40,564 (+0.7787), and re-measure it on the built one-place
   `NodeMain`.
6. Tests: a non-Boolean / non-one-hot selector forged in the node circuit is unsatisfiable; an
   adversarial fold that satisfies the step with a false child claim and is refused by the root
   discharge; rename the honest-prover "refusals".
