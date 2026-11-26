# Referee: design study "tree shape" (`docs/design-tree-shape.md`, 7f70222)

Independent read-only referee, 2026-11-19. Inputs: `yugen-spec` main 0.4.5, `yugen-proof-a/docs/recursion.md`,
`yugen-proof-b2/docs/parameters.md`, `docs/lemma-tree-extraction.md`.

**Verdict: PASS WITH CONDITIONS.** The diagnosis (neither system proves 16/16/3) and the choice of (a3) 4/4/5 hold.
Several figures are mis-sourced or slightly wrong, and depth 5 changes more consensus text and pinned keys than the
study says.

## 1. Figures

| Figure | Check | Source |
|---|---|---|
| A closes up to S 6 / M 7; S(7), S(8) commit `2^28`; M(7) 98.8 % of `2^27` | correct | `recursion.md:1353-1358` |
| Section label "§10.0000000000" | garbled; it is §10, "Stop note", twelfth run | `recursion.md` heading above line 1354 |
| B proves capacity 1 at levels 0 to 3; fan-in 8 does not close (129.8 M against 66.6 M words) | correct | `parameters.md:4086-4093`, `4140-4157` |
| 502-slot tree = fan-in 4, depth 5 (375 sub-bundles; 94, 24, 6, 2, 1 merges) | shape correct (5 merge levels = depth 5). **Slot sum wrong**: child slots are 375+94+24+6+2 = 501, the root is no child. **Wiring claims**: the study gives 669 (its own sum is right); B says 659 (`parameters.md:4105`). One of the two is wrong, to be reconciled | `parameters.md:3830`, `4105` |
| 4,345 transfers a block, W = 4 MB; roots A 875,309 + B 713,602 | correct (S, informative) | `yugen-protocol.md:3567-3570`; A `recursion.md:1158` |
| Two bundles do not fit W5 | correct: 2 × 1,588,911 > 2,597,000 | `yugen-protocol.md:3525` |
| 94 % | 4,096 / 4,345 = 94.3 %, correct | |
| Proofs: (a1) 2,458, (a2) 17,207, (a3) 5,461 | correct | |
| A "~9,750 core-s at 4/4/5" | **mis-attributed**. 9,750 is a per-leaf cycle scaling that ignores shape (`recursion.md:2452-2454`). A's own figure for sub-bundles of 4 is "about 9,100, a tree one level deeper" (`recursion.md:2458-2459`), and A says the node sizes "do not carry over" (`2460`). Neither is measured at 4/4/5 | |
| B 14,200 to 15,240 core-s | M at capacity 1, rate 1/8, depth 3 node timings; **not** capacity 4 and not levels 4 and 5 | `parameters.md:4100-4114` |
| B depth-5 verification ~220 ms | E by the study; the depth-3 figure 151.6 ms is itself held open (load) | `parameters.md:4093-4097` |

## 2. Does depth 5 break anything?

- **Proof count.** At 4/4/5 every admitted tree has ≤ 4^5 = 1,024 sub-bundles of ≤ 4 leaves and ≤ 341 merges, so
  ≤ 4,096 + 1,024 + 341 = 5,461 proofs. Small sub-bundles give fewer proofs (S = 1: 2,389). Merges of 1 add at most
  one proof a level and are bounded by depth. So every tree has ≤ 20,000 proofs. **But** `MAX_TREE_PROOFS` and
  `BUNDLE_TRANSFERS_MAX` become unreachable. The `tree-limits` vectors (20,000 accepted, 20,001 refused;
  `yugen-protocol.md:3210-3212`) can no longer be built inside the shape, and the informative paragraph "What the
  bound admits" (`3203-3212`) is false at 4/4/5.
- **Statement cells (§15.3).** The `depth` cell is 1 byte, `count` is LE16 and `proofs` is LE32, so all three fit.
  The normative text hard-codes depth 3. BC-3 says `depth_c ≤ 2`, "1, 2 or 3", "a fourth merge level has no
  satisfying assignment" (`yugen-protocol.md:3299-3302`); line 3267 says "d (1, 2 or 3)"; BC-3's `k ≤ 16` and the
  `proofs_c < 2^17` rationale ("at most 69,905") are at `3299-3304`; §15.2 has "merge 1, merge 2, merge 3"
  (`3193-3194`). All of these must be restated, and the arity bound in BC-3 must become 4.
- **Circuits BC-2 to BC-4.** A pins its consensus seeds, `seed_M` among them (`recursion.md:1648`), and its merge
  program contains the depth bound (`recursion.md:134`, a test that a fourth level has no execution). Changing the
  bound changes the merge program, so the seeds and keys must be re-pinned. B's merge circuit verifies each child
  "against the verifying key of its level" (`parameters.md:495`) and has a carried wiring claim per level. Levels 4
  and 5 are new slots and keys, and their merge systems grow with the carried claims. Whether B's one merge shape
  still closes at level 5 is not shown.
- **Soundness tree bound.** The lemma bounds the reached nodes by `N` (at most `N + 16`, the 16 being the arity
  overshoot) and `K ≤ N k_q,max` (`lemma-tree-extraction.md:20`, `269`, `368`). It uses depth only for termination
  (`158-159`). Two more levels therefore change neither the tree-wide count nor `k_q`, provided each level's node
  proof uses an already-certified row: no extra heuristic C2 application per level. The overshoot falls from 16 to
  4, which is harmless. The lemma's text still states depth 3 / arity 16 (`102`, `249`, `256`), and B's carried
  claims across more levels must be confirmed to be inside the certified row's `k_q` (deferred claims are checked
  in the circuit, not by a new round). Lemma text update: required, not a re-derivation.
- **D-6.** B already misses 100 ms at depth 3 (107.6 to 151.6 ms, `parameters.md:3812`, `4095`). Depth 5 makes it
  worse. A's root verification time at depth 5 is not addressed by the study.

## 3. A at arity 4 / sub-bundles of 4 and the node box

A's boxes were walked over S(1..8) and M(1..7) at depths 1 to 3 (`recursion.md:1413`, `1420`), and the box's lower
edges are still open (condition 2: "lower edges to the layout floors ... changes the merge program and so the
seeds", `recursion.md:1361-1364`). S(1) and M(1) are already legal today, so arity 4 adds no shape below the
current floor. Depths 4 and 5 were never walked, though. Heights are a fixed point in depth (`1354`), which makes
it plausible but not measured that M(k) at depth 4 or 5 over S(1) children stays inside the box. Row 9 / `2^27` is
not at risk (S(4), M(4) are well below the S(6) / M(7) edge).

## 4. Missing options and risks

1. **Privacy (missed).** Sub-bundles of ≤ 4 mean each host record (§15.4) and each sub-bundle's anonymity set
   covers ≤ 4 transfers instead of 8 to 16, and five levels with free arity 1..4 publish a richer shape. This is an
   argument for (e) fixed-arity padding; make that a companion decision, not "consider separately".
2. Option: 4/4/5 **with** `MAX_TREE_PROOFS` lowered to a bound that is actually reachable (5,461 or 6,000). This
   would need re-certification and yields a tighter `N` (better soundness margin). The study does not weigh it.
3. Option: S 6 / M 4 / D 5 (A's sub-bundle edge, B's arity): 6,144 transfers (a full block), if B's level 0 can take
   capacity 6. Not considered.
4. Risk: B has never proven capacity > 1 on the one merge shape (the planning defect was fixed only in
   `parameters.md:4142-4146`). The whole recommendation rests on an unbuilt B node.

## Conditions

1. Correct the record: 501 child slots; reconcile 669 against B's 659 wiring claims; replace A's "~9,750 at 4/4/5"
   with "9,750 shape-free leaf scaling; ~9,100 at S(4), E" and the cite `recursion.md:2452-2460`; fix the section
   label.
2. The spec change must restate BC-3 / BC-4 (`depth_c ≤ 4`, depth 1..5, `k ≤ 4`, the `2^17` rationale), §15.2's
   depth sentence, line 3267, and the "What the bound admits" paragraph. It must also replace the `tree-limits`
   vectors with depth-5 / arity-4 shape vectors (a sixth level refused, arity 5 refused, S(5) refused).
3. A: re-pin the consensus seeds and keys for the depth-5 merge program; walk the node box at depths 4 and 5 (or
   close condition 2's lower edges) before the row is consensus.
4. B: prove a capacity-4 level-0 node and an arity-4 merge at levels 4 and 5 on the one merge shape within 12 GiB,
   and show that the carried wiring claims at level 5 stay inside the certified row's `k_q`.
5. Update `lemma-tree-extraction.md`'s stated shape (depth 3 / arity 16 at lines 102, 249, 256; the `N + 16`
   overshoot) to 5 / 4. State explicitly that depth enters only termination.
6. D-6 at depth 5 measured for both systems (load < 5) before the shape is fixed. If it misses 100 ms, record that
   as a decision, not a footnote.
7. Decide shape privacy (option (e) or a fixed sub-bundle size) together with the constants, and record the drop
   in the sub-bundle anonymity set.
8. Record why `MAX_TREE_PROOFS` stays at 20,000 (unreachable) rather than being lowered and re-certified.
