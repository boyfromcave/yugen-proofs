# Design study: the bundle tree's shape against what both proof systems can prove

Status: study for a lead decision; nothing decided here. Inputs read at: `yugen-spec` main (0.4.5),
`yugen-proof-a` `494f49d`, `yugen-proof-b2` `ed14384`. Marks: **M** measured in the cited run,
**E** estimated here or in the cited source, **S** stated by the specification.

Papers: none was used. Every figure is from the three repositories cited; the soundness argument
for trees of any shape is the workspace's own `docs/lemma-tree-extraction.md` (Original, the Ycash
developers), which this study does not change.

## 1. The problem

Specification §15.2 (SPEC-73, SPEC-109) admits sub-bundles of 1 to `BUNDLE_LEAVES_MAX` = 16
transfers, merges of 1 to `BUNDLE_ARITY_MAX` = 16 children, depth at most `BUNDLE_DEPTH_MAX` = 3,
at most `BUNDLE_TRANSFERS_MAX` = 16,384 transfers and `MAX_TREE_PROOFS` = 20,000 proofs (S,
`yugen-protocol.md` §15.2, table rows at lines 183 to 187). Both systems must prove every bundle,
and their rows are certified for exactly 20,000 proofs ("a row certified for fewer is not a
consensus row", §15.2). Neither system can prove the trees the shape limits admit.

## 2. What each system can prove now

**System A** (`docs/recursion.md` §10.0000000000, twelfth run). A merge's log heights are a fixed
point in depth, so closure holds at every depth **up to merges of 7 and sub-bundles of 6**; S(7) and
S(8) commit `2^28`, M(7) fills 98.8 % of `2^27`, M(8) and above commit `2^28`, and row 9 refuses
every stack above `2^27` (decision M-A2; the row-9 list asserts `2^28..2^30` refused). (M, from
`bench/results/node-pins-20261119.txt`.) Largest tree at the spec's depth 3: **6 × 7^3 = 2,058
transfers**. Note: before the zero-knowledge padding (H-2 sizing, 80-byte salts) A had proven S(9)
and M(8) inside `2^27` (§9 table, `recursion.md` lines 1152 to 1158); the masking moved the edge.
Nodes at `2^27` take 7.1 to 8.3 GB (M, same table).

**System B** (`docs/parameters.md`). What is proven on the one merge shape (uniform layout, §17.2,
§19.1): **a sub-bundle of one leaf and merges of one child at levels 1, 2, 3** (capacity 1 at every
level, M). Level-0 nodes of capacity 2 and 3 were proven in the earlier grouped layout at 6.73 and
10.33 GB (§16, "Capacity (task F)", M); in the uniform layout no capacity above 1 could even be
planned until the defect fixed in §19.4. Fan-in 8: the level-0 system is `2^25` rows and the merge
system needs 129.8 M words against 66.6 M stated, so **the one merge shape does not close at 8**
(§19.4, M, no proof attempted). The 64 GB one-process bound of §3.4 (K = 5, arity 4, 5 × 4^3 = 320
leaves) predates task B-7 and the 12 GiB memory-cap rule and is superseded by these figures.
So **B proves N = 1 today**; fan-in 4 is the planned shape, not a built one.

**How B's N = 1,500 model maps onto §15.2.** "Capacity 1, 502 slots" (§17.6, §19.1, defined in
§13.6) is a fan-in-4 tree: 375 sub-bundles of 4 (1,500 leaf slots), then merges of 4 in levels of
94, 24, 6, 2, 1 nodes (127 nodes above level 0, 375 + 94 + 24 + 6 + 2 + 1 = 502 child slots, 669
wiring claims = 375 + 2·94 + 3·24 + 4·6 + 5·2). That is **depth 5, two levels more than
`BUNDLE_DEPTH_MAX`**, and its nodes verify 4 children each while the timing is of capacity-1 nodes
("E for capacity 4", §17.6). At depth 3 and fan-in 4 the spec admits at most 4 × 4^3 = 256
transfers; 1,500 needs depth 5 at fan-in 4 (depth 4 gives 1,024).

**Transfers per block and bundles per block** (§16.2, S). The specification fixes no
transfers-per-block figure; the informative capacity is **4,345 bundled transfers** at
`W` = 4,000,000 (232-byte records only; to be restated at revision 9). A transaction holds one
bundle (`yugen-protocol.md` line 887); nothing forbids several bundle
transactions in a block, and W5 limits "the bundle transactions ... together" to `W − LEAF_RESERVE`
= 2,597,000. But each bundle carries its two root proofs (A 875,309 + B 713,602 = 1,588,911 bytes),
so **two bundles do not fit W5**: at `W` = 4 MB a block holds at most one bundle. N = 1,500 is the
E2 target ("1,500 leaves merged in 60 s on eight 16-core hosts", `decision-security-profile.md`
line 372), about 35 % of a full block, not a full block.

## 3. Options

Shape figures: transfers at full shape; proofs = leaves + sub-bundles + merges.

**(a1) Shrink to A's limits, depth 3** (S ≤ 6, M ≤ 7, D 3): 2,058 transfers, 2,458 proofs. Caps a
block at 47 % of 4,345. B still cannot prove it (arity 7 is above its fan-in 8 failure margin and
unbuilt). Rows stay valid (a row certified for 20,000 covers fewer), but `MAX_TREE_PROOFS` 20,000
becomes a dead bound; keeping it keeps the certification unchanged.

**(a2) Shrink to A's limits, raise depth to 4** (S ≤ 6, M ≤ 7, D 4): 14,406 transfers, 17,207
proofs ≤ 20,000: `MAX_TREE_PROOFS` and its certification unchanged, `BUNDLE_TRANSFERS_MAX` may stay
16,384 (shape binds first). Full block reachable. A's closure is depth-invariant, so A needs only
the depth cell and one more node level (no new row). B is unaffected in kind (it fails at 7 anyway).

**(a3) Shrink to the common feasible shape, B's fan-in 4** (S ≤ 4, M ≤ 4, D 5): 4,096 transfers,
5,461 proofs; covers 94 % of a block and is exactly B's modelled N = 1,500 tree. Certification
unchanged. Both systems need depth-5 circuits (the depth cell, BC-2 to BC-4). B's cost of depth:
one more carried wiring claim per level (batching 3.34, 5.35, 6.21 core-s at levels 1 to 3, §19.1)
and final verification grows with the carried claims (151.6 ms at level 3, 100.9 ms of it carried
claims; D-6's 100 ms already missed, depth 5 about 220 ms, E). Still gated on B building fan-in 4
(capacity 4) on the one merge shape.

**(b) Per-system shape limits.** Not available as a consensus rule: one tree, one `bstmt`, both
systems prove it (§15.2, §15.3), so the effective limit is the intersection — this is (a) under
another name. Only meaningful if a system's proof became optional, which breaks the two-system
design.

**(c) Extend the provers.** A: row 9 to `2^28` needs new query schedules and a new `kq-box`
(`recursion.md` §10.0000000000); nodes about 2 × 8.3 = 17 GB (E), above most hosts' heavy slot.
Buys S up to about 12 and M about 15 (E, from the stack law). B: capacity and fan-in above 4 are
blocked by the one merge shape (fan-in 8 does not close, §19.4) and the 12 GiB slot (capacity 7
about 20 GB, E). Neither reaches 16/16; it raises cost and memory and still needs (a) for 16.

**(d) Several bundles per block.** Already legal, but the root pair (1.59 MB) means a second bundle
does not fit W5 at `W` = 4 MB; it needs `W` raised by about 1.6 MB a bundle, or root proofs
pruned/aggregated (not specified). It does not fix the shape gap: each bundle must still be
provable. Privacy: the number of bundles and their sizes partition a block's transfers by
aggregator, a public signal the single-bundle block lacks.

**(e) Pad merges to a fixed arity / uniform shape.** Make every merge arity exactly `a` and every
sub-bundle exactly `s` (dummy children cost proofs). Narrows the tree bytes' information (the shape
is public and today leaks how many hosts and how they merged) and matches B's "one merge shape".
Cost: dummy proofs; proof count for full trees unchanged. Can be combined with (a2)/(a3).

## 4. Comparison

| Option | Max transfers a bundle (block 4,345) | `MAX_TREE_PROOFS` / rows | Memory a node | Prover at N = 1,500 | Consensus change | Privacy |
|---|---|---|---|---|---|---|
| Spec as is (16/16/3) | 16,384 | 20,000, certified | A > 8.3 GB (`2^28`, unproven); B fails | neither can | none | shape public |
| (a1) 6/7/3 | 2,058 (47 %) | dead bound; certification kept | A ≤ 8.3 GB (M) | A ~9,750 core-s (E, `recursion.md` line 2454); B cannot | three constants | same |
| (a2) 6/7/4 | 14,406 (100 %) | 17,207 ≤ 20,000; unchanged | A ≤ 8.3 GB (M) | A as above; B cannot (arity 7) | constants + depth cell 4 | same |
| (a3) 4/4/5 | 4,096 (94 %) | 5,461; unchanged | A < 8.3 GB; B capacity 4 unbuilt (~12 GB, E) | A ~9,750 (E); B 14,200 to 15,240 (M at cap. 1, E cap. 4, §19.1) | constants + depth cell 5 | same |
| (b) per system | intersection | — | — | — | not expressible | — |
| (c) extend A row 9 / B capacity | A ~12/15, B ≤ 4 | new schedules, re-certify A | A ~17 GB, B ~20 GB (E) | higher per node | none, or new A row | same |
| (d) several bundles | one fits at W = 4 MB | per bundle | unchanged | unchanged | `W` or root pruning | bundle count leaks aggregator split |
| (e) fixed arity padding | as chosen | unchanged for full trees | unchanged | + dummy proofs | statement rule | less shape leakage |

## 5. Recommendation

**(a3) as the target shape, with the arity raised toward (a2) when B proves it**: set
`BUNDLE_LEAVES_MAX` = 4, `BUNDLE_ARITY_MAX` = 4, `BUNDLE_DEPTH_MAX` = 5, keep `BUNDLE_TRANSFERS_MAX`
16,384 (inert) and `MAX_TREE_PROOFS` 20,000 (so neither row is re-certified). It is the only shape
both systems are on a path to prove, it is the tree B's N = 1,500 figures already price, it
reaches 94 % of a full block in one bundle (which is all a block can carry, §2), and it keeps A
inside `2^27` with margin. Gate it on B proving a capacity-4 level-0 node and an arity-4 merge on
the one merge shape inside 12 GiB, and on B's depth-5 verification time against D-6. Consider (e)
on top, separately, for shape privacy. Do not pursue (c) for A now; (d) is moot at `W` = 4 MB.

What would change it: B proving fan-in 6 to 7 on the one merge shape (then (a2), 6/7/4, full
block, fewer levels); B failing capacity 4 (then the tree must be shallower in B's terms and the
throughput falls toward 4^k with capacity 2 or 3, or B's role is reconsidered); a larger `W` or
root-proof pruning (then (d) becomes real and per-bundle limits may shrink further); revision-9
proof sizes moving the 4,345 figure materially; A's masking reductions bringing S(8)/M(8) back
inside `2^27`.
