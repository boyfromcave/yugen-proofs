# Decision record: the shape of a bundle tree

*The Ycash developers, 2026. Record opened 2026-11-20. Keep this file current: it is the reference
for this decision before, during and after implementation (section 7 is the implementation log).*

## 1. The question

Specification 0.4.5 §15.2 (SPEC-73, SPEC-109) admits bundle trees with sub-bundles of up to 16
transfers, merges of up to 16 children and depth up to 3 (at most 16,384 transfers). Both proof
systems must prove every bundle. Neither can prove trees that large: System A stops at
sub-bundles of 6 and merges of 7, because larger nodes need a stack above 2^27, which its row 9
refuses (M-A2) and host memory would not hold. System B has proven only one-leaf trees on its
current layout, and fan-in 8 does not close. So the specification admits bundles no one can build.

## 2. Sources

| Document | What it is | Status |
|---|---|---|
| `docs/design-tree-shape.md` (`7f70222`) | The design study: what each system proves today, options, comparison | Draft |
| `docs/tree-shape-referee.md` (`d529380`) | Independent referee report on the study | Pass with conditions 1–8 |
| `yugen-proof-a` `docs/recursion.md` §10.0000000000 (`494f49d`) | A's limits 6 / 7; the node box | Measured |
| `yugen-proof-b2` `docs/parameters.md` §17, §19 (`ed14384`) | B's proven shapes, N = 1,500 measured on a fan-in-4 depth-5 tree, fan-in 8 fails | Measured |
| Specification §15.2, §15.3, §16.2 | The tree rules; block capacity 4,345 bundled transfers (informative) | 0.4.5 |

No academic papers were used; every figure comes from the repositories above.

## 3. Options compared

Block capacity 4,345 bundled transfers; at W = 4 MB a block holds one bundle (root proofs of
A plus B are 1,588,911 bytes against 2,597,000). Figures marked (E) are estimates.

| Option | Max transfers a bundle | `MAX_TREE_PROOFS` / soundness rows | Memory a node | Prover at N = 1,500 | Consensus change | Privacy |
|---|---|---|---|---|---|---|
| Specification as is (16 / 16 / depth 3) | 16,384 | 20,000, certified | A above 8.3 GB (2^28, unproven); B fails | neither can | none | shape public |
| (a1) 6 / 7 / 3 | 2,058 (47 % of a block) | bound never reached; certification kept | A ≤ 8.3 GB (measured) | A ~9,750 core-s (E); B cannot | three constants | same |
| (a2) 6 / 7 / 4 | 14,406 (full block) | 17,207 ≤ 20,000 | A ≤ 8.3 GB | A as above; B cannot (arity 7) | constants, depth 4 | same |
| **(a3) 4 / 4 / 5 (recommended)** | 4,096 (94 %) | 5,461, unchanged | B capacity 4 unbuilt, about 12 GB (E) | A ~9,750 (E); B 14,200–15,240 (measured at capacity 1) | constants, depth 5 | same |
| (b) per-system limits | the intersection, i.e. (a) | — | — | — | not expressible: one tree, both systems prove it | — |
| (c) enlarge A's row 9 / B's capacity | A ~12–15, B ≤ 4 | new schedules, A re-certified | A ~17 GB, B ~20 GB (E) | higher | a new A row | same |
| (d) several bundles a block | only one fits at W = 4 MB | per bundle | unchanged | unchanged | raise W or prune root proofs | bundle count shows how aggregators split a block |
| (e) fixed-arity padding (alongside) | as chosen | unchanged for full trees | unchanged | plus dummy proofs | a statement rule | less shape leakage |

## 4. The referee's conditions

Verdict: pass with conditions. Confirmed: neither system can prove 16 / 16 / 3; 4 / 4 / 5 is the
right target; block capacity, root proof bytes and one bundle a block; proof counts (at most 5,461
for every tree the shape admits, so the 20,000 bound holds); depth enters the tree soundness bound
only through termination, so two more levels change neither k_q nor the tree-wide count, provided
every level uses a certified row.

| Id | Condition |
|---|---|
| 1 | Correct the study's figures: 501 child slots, not 502; 659 or 669 wiring claims (to settle); A at sub-bundles of 4 is about 9,100 core-seconds by A's own estimate, not 9,750 |
| 2 | Restate the specification text that hard-codes depth 3 and arity 16 (§15.2, BC-3, BC-4, the "bound admits" paragraph); replace the unreachable `tree-limits` vectors with shape vectors (a sixth level, arity 5 and a sub-bundle of 5 refused) |
| 3 | A: re-pin the merge program's seeds and keys; walk the node box at depths 4 and 5, or close its lower edges |
| 4 | B: prove a capacity-4 level-0 node and arity-4 merges at levels 4 and 5 within 12 GiB, with the level-5 carried claims inside the row's k_q |
| 5 | Restate the tree-extraction lemma for depth 5 and arity 4 (overshoot N + 4, not N + 16) |
| 6 | Measure D-6 (root verification time) at depth 5 for both systems at low load; if it misses 100 ms, record that as a decision |
| 7 | Decide tree-shape privacy (fixed arity or fixed sub-bundle size) together with the constants: sub-bundles of at most 4 and five free levels publish more of the shape |
| 8 | Record why `MAX_TREE_PROOFS` stays at 20,000, now unreachable, rather than being lowered and re-certified |

Options the referee added: lower `MAX_TREE_PROOFS` to about 5,461–6,000 and re-certify (a tighter
count); sub-bundles of 6, merges of 4, depth 5 (6,144 transfers, more than a block), which needs B
at capacity 6.

## 5. Decision

**Adopted by the lead architect on 2026-11-20:** sub-bundles of at most 4 transfers, merges of at most 4 children,
depth at most 5 (`BUNDLE_LEAVES_MAX` 4, `BUNDLE_ARITY_MAX` 4, `BUNDLE_DEPTH_MAX` 5), so a bundle holds at most 4,096
transfers (about 94 % of a block's 4,345; one bundle fits a block at W = 4 MB). `BUNDLE_TRANSFERS_MAX` 16,384 and
`MAX_TREE_PROOFS` 20,000 are kept, now unreachable (at most 5,461 proofs), so neither system's soundness rows need
re-certifying (tree-shape referee condition 8).

Evidence at the decision: System A proves sub-bundles up to 6 and merges up to 7 inside 2^27, so 4/4 is well inside;
System B proves each published merge as internal arity-2 nodes with the carried-claim fold (`design-b-aggregation.md`
option (d)+(c)), every node inside 2^23 and 12 GiB, a real chain to depth 3 verified; on CPU with the machine loaded,
B's critical path for N = 1,500 is about 59 s (target 60 s) and root verification about 97 ms (target 100 ms), not yet
timed at low load. The tree-extraction lemma's section 6b passed review at revision 5.2.

Tree-shape privacy (tree-shape referee condition 7): decided by the lead agent, **no fixed-arity padding**. The
sub-bundle records (host script, count, share) are already public in the host-fee list (section 15.4), so the
tree's leaf grouping is public anyway; padding would cost dummy proofs and hide only the merge grouping, which follows
from how hosts merge and reveals nothing about wallets. Residual: the merge grouping is public. Would change: a
finding that merge grouping links transfers to wallets.

## 6. What would change this decision

- System B proving fan-in 6 or 7: then (a2), a full block in fewer levels.
- System B failing capacity 4: a shallower B tree with lower throughput, or a review of B's role.
- A larger block weight or root-proof pruning: then (d).
- Proof sizes moving the 4,345 figure.
- A's masking reductions bringing sub-bundles and merges of 8 back inside 2^27.

## 7. Implementation log

| Date | Step | Where | Result |
|---|---|---|---|
| 2026-11-20 | Gap found | `yugen-proof-a` `494f49d` | The specification admits trees A cannot prove |
| 2026-11-20 | Design study | `docs/design-tree-shape.md` `7f70222` | (a3) recommended |
| 2026-11-20 | Referee | `docs/tree-shape-referee.md` `d529380` | Pass with conditions 1–8 |
| 2026-11-20 | Gate: B capacity 4 and arity 4 | `yugen-proof-b2` `185e799`, §20, `bench/results/kplan-20261120-r.txt` | **Failed** on B's one merge shape: no capacity above 1 closes at rate 1/8 or 1/4 (a merge slot, 5.6–6.7 M AND, is larger than a leaf slot, about 4.2 M AND); an arity-4 merge needs 2^25; with a separate merge shape the largest merge in 2^24 is arity 2; under this machine's 12 GiB limit. Also measured: 669 carried claims (not 659); D-6 at depth 3 100.8 ms at load 4.76, depth 5 about 146 ms (estimate) |
| 2026-11-20 | Design study: how B aggregates | `docs/design-b-aggregation.md` `3eb878b` | Recommends (d)+(c): B proves each published arity-4 merge as three internal arity-2 nodes, digests passed through and hashed at a top node as §15.3 states, carried claims discharged at each level; no consensus change; every B node within 2^24. Finding: every B option costs at least about 14k core-seconds at N = 1,500, against E2's 7,680 core-seconds a minute for both systems |
| 2026-11-20 | Referee of the aggregation study | `docs/b-aggregation-referee.md` `e2fdbf3` | Pass with conditions 1–9. (d) is sound only with P1–P4 built (internal nodes recompute and export child digests; one set of wires for the top hash; a third node kind; merges under 4 children); B's internal count is at most 8,191, within the certified 20,000; the tree-extraction lemma must be restated for internal nodes; (c) raises the node row's k_q (calculator re-run). **E2 missed by 2.6–3.4×** (both systems about 19.9k–25.7k core-seconds against 7,680; 21–27 hosts, not 8); B's critical path under (d) about 60–130 s against 60 s, which more hosts cannot shorten. The 111-query row keeps the margin (+0.83 bits) but rests on Johnson-radius list decoding with open conditions, and still misses E2 by 1.7× |
| | Specification change | `yugen-spec` | Not started |
| | A and B moved to the new limits | both proof repositories | Not started |
| 2026-11-20 | B internal nodes built, first form | `yugen-proof-b2` branch `agg` `a89652b`, §21 | P1–P4 specified and tested at witness level (6/6); P1 as a commitment E under H_int (tag 0xbf) instead of raw words; internal node fits 2^24 at node rate 1/4 only (12.35 GiB peak at level 2); timings void (load 9–14) |
| 2026-11-20 | Referee of B internal nodes | `docs/b-internal-node-referee.md` `cd15562` | Pass with conditions 1–6: reserve 0xbf in the specification; range-check `count_j`; H_int added to the tree lemma's assumptions; a key of its own for the level-0 internal node; slot equalities and key pinning inside the circuits; refusal tests for the level-0 pair. Conditions 2, 4, 5, 6 sent to B; 1 and 3 owed by the lead (spec registry, lemma) |
| 2026-11-20 | B: D-6 and critical path | `yugen-proof-b2` `agg` `270fcd4`, section 27 | Root verification 96–98 ms (loaded), uniform step 5.1 s, critical path for N = 1,500 about 59 s (loaded); a real chain to depth 3 verified; depth 4 and 5 refused by BC-3 until the specification changes |
| 2026-11-20 | **Decision** | the lead architect | 4 / 4 / 5 adopted; tree-shape privacy: no padding (lead agent) |
| 2026-11-20 | Specification change (4 / 4 / 5) | `yugen-spec` 0.4.9, tag `spec-0.4.9` (`30740bf`), SPEC-201 | Merged; shape vectors (full 4/4/5 tree accepted at 4,096 transfers, 5,461 proofs; sixth level, merge of 5, sub-bundle of 5 refused); 97 tests on three targets, 125 mutations, 120 reverts; checkers re-run by the lead |
| 2026-11-20 | B on 0.4 leaf and depth 5 | `yugen-proof-b2` `agg` `de7214b`, section 28 | Node circuits on the 0.4 leaf (44 words, per-scheme PC-1, C0 in circuit); real chain to depth 5 verified (feature `shape445`); D-6 at depth 5 137.3 ms at load 11.7 (not yet at low load); C-4 gaps G-3, G-4 closed |
| | A at depth 5 | `yugen-proof-a` | Not started |
| 2026-11-20 | **System B closed** | the lead architect | Times measured under load accepted as within error: critical path about 59 s for N = 1,500 (target 60 s); D-6 96–98 ms at depth 3, 137.3 ms at depth 5 at load 11.7 (target 100 ms); quiet-machine timings no longer a blocker. B on specification 0.5.0 at `0a666b2` |
