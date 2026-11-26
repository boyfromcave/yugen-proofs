# Design study: how system B aggregates a bundle tree

Status: study (2026-11-19), for the lead architect. Inputs: `yugen-proof-b2` `185e799`
(`docs/parameters.md` §16.11, §19.1, §20.2–§20.5; `bench/results/kplan-20261120-r.txt`), spec
`yugen-protocol.md` §15.2–§15.3, `design-tree-shape.md`, `tree-shape-referee.md`,
`decision-tree-shape.md`, `yugen-plan-draft/plan-rev7.md` (E2, SQ-42). Read only; nothing built
or run. Marks: M measured, E estimated from M, C counted.

## 1. Size check or real memory?

**Both, in that order.** The `kplan` runs stop at the `stamp::Layout::with_pad` assertion
(`src/stamp.rs:205`, private words; `:208`, rows) with peaks of 4.3–6.1 GB, before any node proof:
the one-merge-shape design pads every node to the level-0 system's stated size, and a merge slot
(5.6–6.7 M AND, it verifies a 2^23–2^24 node at 192/235 queries) is larger than a leaf slot
(~4.2 M AND). So `A` merge slots never fit a system sized for `K0 = A` leaf slots. That is a
sizing failure, not an out-of-memory one. Resizing then meets memory: an arity-4 merge is
22.9 M (1/8) to 27.2 M (1/4) AND plus main, a 2^25 system.

Memory from B's measured scaling (level-0 nodes, `parameters.md` §16.11, M):

| Domain | Peak | Step |
|---|---|---|
| 2^22 (capacity 1) | 5.31 GB | |
| 2^23 (capacity 2) | 6.73 GB | +1.42 |
| 2^24 (capacity 3) | 10.33 GB | +3.60 |

A fixed ~4 GB floor (tables, keys, the vendored crates) plus a part that doubles with the domain,
as the commit-and-fold prover of Diamond–Posen (DP24, ePrint 2024/504, §4–§5: linear-size
codewords of the committed multilinears) implies. Extrapolated (E):

- **2^25** (capacity 4 / arity 4, one shape): ~17–20 GB (§16.11 itself states "about 20 GB").
- **2^26**: ~32–40 GB.

Both fit a **64 GB E2 host** (SQ-42, plan rev7 l. 938): 2^25 three processes, 2^26 one. They do
not fit this laptop's 12 GiB heavy slot, which is a development limit, not a specification one.
Capacity 4 at level 0 alone stays in 2^24 (16.6 M AND, ~10.5–11 GB, E) and is marginal here.

## 2. Options

**(a) Larger nodes on 64 GB hosts, one shape at 2^25.** Pad all B nodes to 2^25; arity 4 and
capacity 4 then fit (4 × 6.7 M + main ≈ 27.7 M < 33.5 M). Open: the fixed point (a merge slot
verifying a 2^25 child grows by about one round, a few %, E) and levels 4–5 never reached
(§20.3 b). Per-node cost about doubles, node count quarters: total core-seconds about level with
§20.2 (14,200–15,570), plus padding waste at level 0 (16.6 M in 33.5 M: ~2x at level 0 unless
level 0 keeps its own 2^24 shape, which is option (a') two shapes, 2^24 leaf node + 2^25 merge).
D-6 ~146 ms at depth 5 (§20.5, E). Development needs a 64 GB machine to test.

**(b) Separate merge shape, arity 2, deeper tree.** Largest merge in 2^24 is arity 2 (§20.3).
With sub-bundles of 4, 4,096 transfers need 1,024 sub-bundles, so depth 10 (2^10) — and the
published tree, which A also proves, becomes 4 / 2 / 10. Carried claims a node at level l = l
(§20.3 c), so the root carries 10: D-6 ≈ 29.4 + 1.5 + 2.6 + 10 × 22.4 ≈ **258 ms** (E), over the
100 ms E2 target. Total claims at N = 1,500 rise (sum over levels of l × nodes) to about 1,500
(C, roughly 2.2x 669), batching cost with it. Soundness: depth enters the tree bound only through
termination (`decision-tree-shape.md` l. 47), but the claim count per root grows, which must sit
inside the row's k_q (open, as §20.3 b). Spec: depth 10, and A pays a deeper tree for B's sake.

**(c) Discharge carried claims at each level (batching per node).** Caps the carried claims at a
constant c, so D-6 ≈ 33.5 + c × 22.4 at any depth (c = 1: ~56 ms) and the merge slot shrinks
(fewer claims in the child's public data). Cost: a batching step inside every merge (§20.2
prices batching at 2.07–3.34 core-seconds a claim; moved into nodes it is paid once per node
rather than at the root). Does not by itself fix arity 4 in 2^24 (the slot is dominated by the
verifier of the child proof, not by claims), so it combines with (a), (b) or (d). Soundness: the
per-level batching adds one batching error term a node (k_q recount, C).

**(d) B proves its own tree; the statement is unchanged.** The published tree and `bstmt`
(§15.3) are fixed; B's recursion need not mirror them. A published merge of arity 4 is proven in B
by a **virtual** binary sub-tree: two arity-2 B nodes that output their children's `D_i` as
public words (no hash), and a top node that checks those four and computes
`H_bundle-node(d || … || Hvar_bundle-kids(D_1 || … || D_4) || …)` as §15.3 l. 3268 states.
Likewise a sub-bundle of 4 can be two capacity-2 virtual nodes. Every B node then stays at arity
2 / capacity 2, inside 2^24 on the separate merge shape §20.3 measured, and inside 12 GiB.
Expressible in §15: the node verifies only B's root proof against `bstmt`; the internal shape is
B's business, as long as the depth, count and proofs cells B proves are those of the published
tree (BC-2..BC-4 are enforced on the published node digests, which the top node computes).
Costs: about 1.5x more B nodes above level 0 (3 per published merge instead of 1); B's depth
doubles above level 0 (5 → 9), so without (c) the root carries ~9 claims (D-6 ~235 ms, E); with
(c) ~56–80 ms. Soundness: B's proof count per tree rises (internal nodes), so B's row must be
certified for its own count, which is larger than `MAX_TREE_PROOFS` (about 1.4x, C); the
statement and A are untouched.

**(e) B non-recursive / reduced role.** B proves only leaves (or only the root over A's list),
the bundle's B evidence being N leaf proofs; or B is demoted to a canary like A's. Kills the
"both systems prove every tree" property §15.2 states and the hybrid soundness argument rests
on; a consensus and security-profile change. Recorded, not recommended.

**(f) Other.** (f1) Rate 1/4 node proofs (smaller merge slot in words but more AND, §20.3; does
not close). (f2) Smaller merge slots via fewer queries (candidate 1/8 row, 111 queries, merge
slot 2^21, §16.11) — a soundness-row decision, not a shape one; with it arity 4 may fit 2^24 on
one shape (4 × ~2.1 M ≈ 8.4 M + main, E) — the cheapest fix if the row is accepted.

## 3. Comparison (N = 1,500; B only; A unchanged at 4 / 4 / 5 unless stated)

| Option | Max transfers | Memory / B node | Prover cost N = 1,500 (core-s) | D-6 (root) | Soundness change | Consensus change | Must be built |
|---|---|---|---|---|---|---|---|
| (a) one shape 2^25, 64 GB hosts | 4,096 | ~17–20 GB (E) | ~15–20k (E; padding at level 0) | ~146 ms (E) | levels 4–5 claims in k_q (open) | none beyond 4/4/5 | 2^25 stamp, 64 GB test host, fixed-point check |
| (a') two shapes 2^24 + 2^25 | 4,096 | ~11 / ~17–20 GB | ~14.2–15.6k (E) | ~146 ms | as (a) | none beyond 4/4/5 | second shape again (pre-§17 form) |
| (b) arity 2, depth 10 | 4,096 | ≤ 10.3 GB (M) | ~16–18k (E; claims ~2.2x) | ~258 ms (E) | more claims per root | depth 10, arity 2 (A too) | spec text, A deeper |
| (c) discharge per level | as host option | +batching slot | +~1–2k moved into nodes (E) | ~56 ms + own (E) | one batching term a node | none | in-node batching circuit |
| **(d) virtual binary B tree** (+c) | 4,096 | ≤ 10.3 GB (M, arity 2 / cap 2) | ~15–17k (E; 1.5x nodes above 0) | ~235 ms; with (c) ~56–80 ms | B certified for its own proof count (~1.4x) | **none** | virtual-node public outputs, top-node hash, (c) |
| (e) reduced role | n/a | leaf only | ~0 bundling | n/a | hybrid argument lost | yes, §15.2 and profile | spec and profile rewrite |
| (f2) 111-query row | 4,096 | ~11 GB (E) | ~7.5k-scale (§16.11, E) | lower (fewer queries) | row change (decision) | none | row certification |

Every B option sits at or above **14k core-seconds** for N = 1,500, against E2's 7,680
core-seconds a minute for *both* systems on eight 64 GB hosts (plan rev7 l. 938; A ~5,700, E).
The shape question does not close E2 for B; only the row (f2) or a cheaper node does.

## 4. Recommendation

**(d) with (c): B proves the published 4 / 4 / 5 tree through a virtual binary tree, discharging
carried claims at each level.** It needs no consensus change, keeps every B node inside the
measured 2^24 / 12 GiB envelope (testable on this laptop), meets D-6 and keeps A's shape.
Pursue (f2) in parallel as the only lever on E2's cost.

What would change it: (1) the lead architect accepts testing on 64 GB hosts — then (a') is
simpler (no virtual nodes, no recount); (2) the 111-query row is certified — then retry one
shape at arity 4 in 2^24 first; (3) the k_q recount for B's larger internal proof count fails
the row — then (a'); (4) in-node batching proves too costly — then (d) alone and record D-6 as
missed (~235 ms).

## References

- DP24: B. Diamond, J. Posen, "Polylogarithmic Proofs for Multilinears over Binary Towers",
  ePrint 2024/504 (`2024-504.pdf` (see REFERENCES.md)), §4–§5 — Published; used for the
  prover-memory scaling argument only.
- Options (c), (d) are Original (the Ycash developers); (a), (b) are the measured design's
  variants.
