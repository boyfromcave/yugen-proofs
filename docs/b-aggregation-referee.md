# Referee report on `design-b-aggregation.md` (System B aggregation of the bundle tree)

Part of Yugen. 2026-11-19. Independent, adversarial review of `docs/design-b-aggregation.md`
at `3eb878b` (unchanged at `cedeac0`). Read only: `yugen-proof-b2` `185e799` (`docs/parameters.md`,
`bench/results/kplan-20261120-r.txt`), spec `yugen-protocol.md` §15.2–§15.3, `decision-tree-shape.md`,
`tree-shape-referee.md`, `lemma-tree-extraction.md`, `what-is-proven.md`, `johnson-row-referee-2.md`,
`yugen-plan-draft/plan-rev7.md`. Nothing built or run. Findings are Original (the Ycash developers, 2026),
unreviewed.

## Verdict

**PASS WITH CONDITIONS** (section 7). (d) is a sound direction and needs no change to `bstmt` or its cells, but
the study (i) misstates the proof-count issue (it is not above `MAX_TREE_PROOFS`; the lemma's *node-count
argument* is what breaks), (ii) under-prices (d) if level 0 is virtualised too, (iii) omits a wall-clock
problem that doubled depth creates for E2's 60 s, and (iv) understates how badly E2 is missed.

## 1. Digest pass-through: soundness, lemma, `k_q`

**Swap / reorder / forge.** A top node verifies internal proofs `P_L`, `P_R` for public words
`(cells_1, cells_2)`, `(cells_3, cells_4)` and hashes `D_1..D_4` in L-then-R order. Choosing which proof is
left is the same freedom a published merge prover has (it picks child order); `bstmt` records the order chosen,
so reordering is not an attack. Forging a passed word means a B proof accepted for a false statement: a
soundness break of B, covered by (K)/C2 like any child. **This holds only if all of the following are built**
(none is stated in the study, §2 (d)):

- (P1) The internal node recomputes each `D_i` from the child's six cells and verifies the child against that
  `D_i` (BC-3, spec `yugen-protocol.md:3293-3301`), and exports the **cells**, not a bare `D_i` beside unbound
  cells. If it exports `D_i` and the top reads `depth_c`, `proofs_c`, `auth_mode_c` from separate unbound words,
  the top can be fed a false `proofs` sum: `MAX_TREE_PROOFS` bypass and a false count in the lemma.
- (P2) The top node's hash input and its verifier slots' public input are the **same wires** (as §17.2's slot
  binds the child transcript on wires, `parameters.md:3708-3712`), no copy.
- (P3) A third node kind: an internal proof must be refused in a published-child slot and vice versa. Today's
  kinds are `f = 0/1` via key digest (`parameters.md:3706-3717`); without a distinct kind a level-0/merge proof
  whose public word is a digest could be read as two passed cell blocks, or the reverse.
- (P4) Published merges with `k < 4` (and sub-bundles `n < 4`): the top writes `LE16(k)` of the real children,
  not 2 or 4; padding/one-child internal nodes refused or fixed by shape.

**Tree-extraction lemma.** The lemma bounds reached nodes by the root's `proofs` cell: `E_T` stops before an
`(N+1)`-th node, `K <= (N + 16) k_q,max` (`lemma-tree-extraction.md:20`, `:227-228`, `:368`), and termination
by the depth cell strictly decreasing (`:231`, `:254`). B's internal nodes carry **neither cell**: they are
not counted by `proofs` and have no depth. So the lemma as written does not cover B's internal tree; it must be
restated (count B nodes as `<= 3 x` published internal nodes + leaves, kind-fixed; termination by kind then
published depth). The C2 count is unchanged in form (one event per child acceptance) but B gains two new
guests (internal node, top node) whose in-circuit/native equivalence is owed (`what-is-proven.md:128`).

**`k_q` and re-certification.** The study says B's count is "larger than `MAX_TREE_PROOFS` (about 1.4x)"
(§2 (d), §3 table). **Wrong.** Rows are certified for `N = MAX_TREE_PROOFS = 20,000` (spec `:187`, `:3218`);
the 4/4/5 shape admits at most **5,461** published proofs (`decision-tree-shape.md:48`). Counted (C): with
sub-bundles and merges both virtualised (2 internal + 1 top each), B proves at most
`4,096 + 3 x 1,024 + 3 x 341 = 8,191` = **1.50x 5,461, 0.41x N**; at N = 1,500 transfers, 3,006 against
2,002. Per-proof `k_q` is unchanged unless (c) adds rounds (section 3). So **no re-certification is needed
provided** the restated lemma bounds B's reached nodes by shape (<= 8,191 + overshoot) and not by
`1.5 x N` (= 30,000, which *would* exceed the certified 20,000).

## 2. "No consensus change"

True for the statement: `bstmt`, the six cells and BC-2/BC-4's digests are computed as §15.3 states
(`:3270-3276`). Not true in two narrower senses:

- **Spec text.** BC-1/BC-3 are normative MUSTs on "a sub-bundle circuit" / "a merge circuit" (`:3284-3301`):
  a merge circuit "verifies the child's proof ... for that digest". B's top node verifies internal proofs whose
  statements are not digests. BC-5 (`:3309-3316`) already lets a system add key identifiers; the text must be
  amended to say BC-1..BC-4 bind the *system's proof of the published node*, however composed. A spec edit,
  not a rule change.
- **Node verification constants.** The node checks B's root against B's keys and B's public layout
  (`K0 | KM | f0 | fM | ... claims`, `parameters.md:3703-3716`); (d) adds keys/kinds and (c) changes the
  root's carried-claim words. These are consensus constants of B's verifier. Since B's keys are not frozen
  (P0), this is not an *additional* change, but "none" should read "none to the statement; B's verifier
  constants as for any B redesign".

Depth, count and proofs cells do not depend on B's internal shape, given P1–P4.

## 3. Option (c): in-node discharge

- **Cost.** Today batching is priced at 2.07–3.34 core-s a claim, 669 claims, 1,360–2,200 (E;
  `parameters.md:4111-4113`, `:4287-4291`). In-node it is paid per node over its own carried claims; at
  c = 1 each node discharges ~1–2 claims, so the total is roughly level (~1–2k) plus a fixed in-circuit
  batching verifier per node (not costed; the merge slot grows by the claims' public data, the study's
  "+batching slot"). The figure "+~1–2k moved into nodes" is plausible (E), unmeasured.
- **Soundness.** Each node gains a batching sub-protocol (P-sh in circuit): one random-linear-combination /
  sumcheck error per node, about `deg x rounds / 2^256`, ~2^-240 a node; union over 8,191 nodes still ~2^-227:
  negligible. What it does cost: the new rounds raise the node row's `k_q` (192 queries sit at +0.78 bits,
  `parameters.md:3367`; `log2(1+k_q)` absorbs at most ~+70 % `k_q` before 192 fails), so the calculator must be
  re-run (T-1), and the in-circuit batching verifier is another C2 guest. Not a re-certification unless the
  recount crosses the margin.
- D-6 with (c): 29.4 + 1.5 + 2.6 + 22.4 c ≈ 56 ms at c = 1 (`parameters.md:4314-4318`) assumes the top
  node's own wiring equals today's merge's; it has two slots plus the batching verifier. E, not M.

## 4. Memory, cost and D-6 figures

- Memory: 5.31 / 6.73 / 10.33 GB at 2^22–2^24 (`parameters.md:3629-3631`) are M. Steps 1.42, 3.60 grow
  ~2.5x, not 2x; a floor + doubling fit gives 2^25 ≈ 17.5–19.3 GB and 2^26 ≈ 32–42 GB. "17–20 GB" and
  "32–40 GB" are fair (E). "2^25 three processes on 64 GB" is tight (3 x 20 = 60 GB, no OS headroom): say two
  to three.
- "≤ 10.3 GB (M, arity 2 / cap 2)" in the (d) row: 10.33 GB is a capacity-3 level-0 node. An arity-2 merge
  (11.2–13.3 M AND, `parameters.md:4280-4281`) is arithmetic, never planned or built; its footprint is **E**.
  A top node with two internal-proof slots plus hash and (c) is also unbuilt.
- (d) cost "~15–17k": the N = 1,500 model is per slot (1,500 leaf slots, 501 child slots,
  `parameters.md:4101-4113`). (d) on merges adds 2 slots per published merge (~127 merges, ~+254 slots,
  ~+1.4k core-s). If sub-bundles of 4 are also virtualised (as §2 (d) proposes to stay inside cap 2), add
  375 tops x 2 slots ≈ +750 slots, ~+4.2k. So **~15.6k (merges only) to ~20k (both)**, plus per-node
  fixed costs (keys, main witness) for ~1,000 more nodes. The study's range holds only if level 0 stays at
  capacity 4 in 2^24 (unbuilt, ~10.5–11 GB, E).
- D-6: 146 ms depth 5 (E from 100.8 ms M, `:4314-4318`); 235 ms for 9 claims follows the same law; 258 ms for
  (b) likewise. Arithmetic checks.
- **Omitted: wall clock.** E2 is 60 s (`plan-rev7.md:1317`). Each B level is a sequential proof of ~6–12 s
  (`parameters.md:4103-4108`, single-run, threads-vs-cores not separated). Published 4/4/5 is ~6 sequential
  B levels (~36–72 s); (d) gives ~9 merge levels, ~10–11 with virtual level 0 (~60–130 s). More hosts do not
  shorten it. (d) may miss E2 on latency regardless of core-seconds.

## 5. E2, plainly

E2: 1,500 transfers per system, merged in 60 s on at most eight 16-core hosts, **both systems together**
(`plan-rev7.md:938`, `:1317`; SQ-42 decided `:1476`, mirrored in the ideation plan). Budget 8 x 16 x 60 =
7,680 core-s. A ≈ 5,700 (E, `:934`); B ≥ 14,200 (M-based, `parameters.md:4113`), (d) 15.6–20k.

- Total **≈ 19.9k–25.7k core-s against 7,680: E2 is missed by 2.6x to 3.4x**, i.e. 21–27 hosts, not 8.
- B alone is 1.8–2.6x the *whole* budget; against what A leaves (~1,980) B is **7–10x over**.
- A alone uses 74 % of the joint budget, so even a free B leaves almost no slack.
- No aggregation option fixes this (the study is right that shape does not close E2), and (d) makes it
  slightly worse. The plan text is stale: it still prices B at ~100,000 and "12 to 13 times over"
  (`plan-rev7.md:42`, `:354`, `:935`, `:1178`); E2 also says "no deeper than leaf, bundle and two merges"
  (`:1317`), which 4/4/5 (depth 5) already contradicts.

## 6. Option (f2), the 111-query row

- Status: `m = 10`, rate 1/8, 111 queries, `k_q` 24,378, need 157.861, margin **+0.83 bits**
  (`parameters.md:3368`), above the certified 192-query row's +0.78. The 107-query predecessor passed
  `johnson-row-referee-2.md` with conditions C-1..C-6; the lead architect ruled it ships once internal
  referees pass (`johnson-row-referee-2.md:5-7`). The re-derived 111 count (calculator revision 9) has not
  been re-refereed.
- What blocks it: the **leaf slot**, not the merge slot. Merge slots fit 2^21 (C); the leaf slot fits 2^21
  only in the Frobenius-form wrapper as a single circuit, ~90 ms final verification, or the row moves to 1/16
  (`parameters.md:3623-3624`, `:3645-3647`). Nothing at 111 queries is built or timed; ~7,500 core-s is E.
- Security cost: **no loss in the bit margin** (+0.83 vs +0.78). The cost is in the basis: unique decoding
  (elementary) is replaced by list decoding at the Johnson radius resting on DKT26 Theorem 4.4 / Cor. 6.6 /
  Lemma 3.3 (a 2026 result, checked internally only), list size 19 entering every round's error
  (`binius-johnson-row.md:690`, `:729`), and C-1..C-6 still open. It is also not enough for E2: 7.5k + 5.7k =
  13.2k, still 1.7x.

## 7. Conditions

1. Correct §2 (d) and the §3 table: B's internal count is ≤ 8,191 (1.5x the 5,461 shape bound, 0.41x
   `MAX_TREE_PROOFS`); state that no re-certification is needed *given* condition 2.
2. Restate `lemma-tree-extraction.md` for B's internal tree: node bound by shape and kind (not by the
   `proofs` cell, which does not count internal nodes), termination through kind then published depth; add the
   internal and top nodes (and, with (c), the in-circuit batching verifier) to C2's owed guests.
3. Specify P1–P4 (cells recomputed and exported, same wires, a third node kind, `k < 4` handling) and add
   refusal tests: swapped internal proofs across slots, internal proof in a published slot and reverse, a
   passed `proofs`/`depth` cell inconsistent with its `D_i`.
4. Amend spec BC-1/BC-3 wording (and BC-5) to allow a system's internal composition; reword "no consensus
   change" as in section 2.
5. Re-price (d): per slot, with and without virtual level 0 (~15.6k–20k), and mark arity-2 memory as E until
   built.
6. Estimate and then measure B's critical-path wall time at (d)'s depth against E2's 60 s.
7. (c): re-run the calculator for the node row's new `k_q` (T-1) before adopting; measure the top node's own
   wiring for the D-6 claim.
8. State E2 plainly in the study and the plan: missed by 2.6–3.4x in total (B 7–10x over A's remainder);
   update the stale ~100,000 / 12–13x B figures and the depth-3 wording of E2.
9. (f2): have the 111-query count re-refereed (or confirm referee-2 carries over), close C-1..C-6, and decide the
   leaf-slot route (Frobenius single circuit at ~90 ms vs rate 1/16) before calling it "the cheapest fix";
   record that it does not close E2 either.
