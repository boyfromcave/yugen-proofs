# C-4 audit: the node relations recompute and range-check every child cell

Condition C-4 of `lemma-tree-extraction.md` (§3, Lemma TE.3; `te3-referee.md`). Audited 2026-11-20 against
`yugen-spec` tag `spec-0.4.8`, §15.2, §15.3, BC-1 to BC-5. Static reading of the circuits and their mutation
tests; no test was run.

- System A: `yugen-proof-a` main `0cdad2f` (`guests/bundle_merge_e2.py`, `bundle_sub_e2.py`,
  `bundle_common_e2.py`, `bundle_constants_e2.py`; mutants in `tests/bundle2.rs`).
- System B: `yugen-proof-b2/wt/s045` branch `agg` `d28b108` (`src/bundle.rs`, `src/bvirt.rs`, `src/node.rs`,
  `src/sponge.rs`; mutants in `tests/bundle_statement.rs`, `tests/node_mode1.rs`).

## Verdict

**C-4 met with conditions.** Every cell of §15.3 is recomputed in circuit from the child's words, every
range BC-3 names is checked, the depth bound, depth recurrence and proof-count recurrence are in circuit in
both systems, and nearly every load-bearing check has a mutation test that removes it and is caught. The
conditions are three missing mutation tests (G-1 to G-3) and one missing pin (G-4); no missing constraint
was found.

## System A (merge `bundle_merge_e2.py`, sub-bundle `bundle_sub_e2.py`)

The cells live in the exponent of `g` (depth, count, proofs) or as two digest cells (content, attr); the
child's digest is `node_digest` over them (`bundle_common_e2.py:92`), the proof is verified for that digest
(`verify_sub`, merge 156), so nothing is taken from the proof (BC-5).

| Cell / rule | In circuit | Range check | Mutant |
|---|---|---|---|
| child depth | merge 114, into `node_digest` 120 via `tabs[dc_g]` | `log(dc_g) < MAX_DEPTH` (115): `depth_c <= 2` | yes, "depth bound" (`bundle2.rs:931`) |
| own depth `1 + max` | `max_tab` 93-100, step 157, written 163 | from the table, domain 0..2 | yes, "depth increment" |
| child mode | `node_digest(..., mode, ...)` 120: the node's own `mode`, never advice | `mode*(mode+1)=0` (63) | mode range: none (acknowledged, `recursion.md` §9.2) |
| child count | `cc[1]`, `tabs[kc_g]` 120 | `log(kc_g/GEN) < SUB_MAX` (117): 1..16 | **none** (G-2) |
| own count `k` | `tabs[n_children_g]` 163; list `match` over 1..16 (162) | `log(selk) < MAX_RECURSIONS` (48) | **none** (G-1) |
| child content, attr | `cc[2..5]` into `node_digest`, `split_limbs` | limbs bound by `split_limbs` | covered by "publish"/recompute only |
| own content (kids list) | `framed_list(parts, k, FRAME_KIDS)` 162 | — | "publish" |
| own attr | constants `0, 0` (163) | — | "publish" |
| child proofs | `count_le(pc_g)` 120, bytes range-checked and product-checked (`bundle_common_e2.py:69-89`) | `log(pc_g) < 2^17` (119) | yes, all four: range, byte range, `count_le` product, child-count binding (`every_constraint_on_the_proof_count_is_live`, 1082) |
| own proofs `1 + sum` | `psum` 89, 121, `count_le` 163 | sum < `2^21 + 1` | yes: start, constant, per-child step |
| sub-bundle `n`, proofs `1 + n` | sub 104, 138 (`tabs[n_leaves_g * GEN]`), depth constant 0 | `log(sel) < SUB_MAX` (104) | `1 + n` yes; `n` range **none** (G-1) |
| sub host_rec | hinted, opaque (136) | none needed (BC-2: opaque) | — |
| PC-1, leaf byte range | sub 23, tail | yes | yes |

## System B (`bundle.rs::merge_statement_with` 399, `bvirt.rs`, `node.rs`)

`node_digest` (`bundle.rs:300`) hashes `depth`, `count`, `proofs` with `Stream::piece` (`sponge.rs:48`),
which **does not truncate**: high bits of a wire shift into the following bytes. So each small cell needs its
own range check for the cells-to-digest map to be injective; that is what each check below provides.

| Cell / rule | In circuit | Range check | Mutant |
|---|---|---|---|
| child depth | `bundle.rs:418-422`, `bvirt.rs:125-126` | in {0,1,2} | yes, `depth_bound` (`bundle_statement.rs:543`) |
| own depth `1 + max` | `bundle.rs:434-441` | from masks | yes, `depth_max` (552) |
| child mode | constant `auth_mode` in `node_digest` (431) | constant | structural, none needed |
| child count | `cells.count` (431) | `count_c < 2^16`, `bundle.rs:429`, `bvirt.rs:128` (internal-node condition 2) | **none: unconditional, no `Rules` switch** (G-3) |
| own count `k` | `Count::with_rules` (407, 212-233): 1..capacity | yes | yes, `count_range` (498), `occupancy` (530); both on the sub-bundle circuit, shared code |
| child content, attr | 64-bit words, `s.words` | full words, no range needed | via `child_binding` (`node_mode1.rs:415`) |
| own content | `list_digest(BUNDLE_KIDS, occupied)` 442 | — | `occupancy` (sub only) |
| own attr | zeros (444) | — | — |
| child proofs | `cells.proofs` (431) | `< 2^17` (426), `bvirt.rs:127` | yes, `proofs_bound` (560) |
| own proofs `1 + sum` | `iadd` masked by occupancy (430) | no carry below `2^21` | yes, `proofs_sum` (570) |
| sub-bundle proofs `1 + n` | `bundle.rs:366-372` | via `Count` | none of its own (low; `count_range` exercises it) |
| `bvirt` commitments | `commit_cells` (87) reads the same wires `merge_statement` range-checks (`top_statement` 173) | inherited | — |

`each_statement_rule_is_needed` asserts the caught list is exactly
`pc1, pc2, count_range, occupancy, depth_bound, depth_max, proofs_bound, proofs_sum` (`bundle_statement.rs:576`).

## Gaps

| # | Sys | Gap | Severity | Test that closes it |
|---|---|---|---|---|
| G-3 | B | `count_c < 2^16` (`bundle.rs:429`, `bvirt.rs:128`) has no switch and no mutant. Without it `count = c + 2^16 x` shifts `x` into the content lane, so two cell tuples give one digest: an extracted child's cells would not be unique, exactly the C-4 failure mode. | medium | add `Rules::count_bits`; a mutant with it off accepts a child whose `count` has bit 16 set and whose `content` is adjusted to the same digest; add `"count_bits"` to the caught list; same for `internal_statement` |
| G-1 | A | No mutant removes `log(selk) < MAX_RECURSIONS` (merge 48) or `log(sel) < SUB_MAX` (sub 104). The `match` over `range(0, 16)` probably refuses `k > 16` too, so the check may be doubly held; untested either way. | low | mutants dropping each assert, cheat `k = 17` (statement-only programs); expect the program to stop at the assert and record whether the mutant stops in `match` |
| G-2 | A | No mutant for the child-count range (merge 117). Redundant under BC-5 (the child's own circuit fixed it, bound by the digest), but the table read `tabs[kc_g]` out of range is the same aliasing the `count_le` byte-range mutant showed. | low | mutant dropping 117, cheat a child with `kc_g = g^300` whose table read aliases a valid pattern; program stops at 117 |
| G-4 | B | No test pins that the consensus node constraint systems (`NodeMain::build`, `node.rs:537, 560-572`) are built with `Rules::default()` (all on), e.g. that the published `cs_digest` equals the all-on build and differs from each single-rule-off build (`qc-and-status-referee.md` T-5, task T-1). Today it holds by reading the code. | low | test: for each `Rules` field, `build_with(rule off).cs_digest != build().cs_digest == pinned consensus digest` |
| — | A | mode-range assertion: no mutant (acknowledged). | info | statement-only cheat with `mode = 2` |
| — | B | merge-circuit `count_range`/`occupancy` mutants run on the sub-bundle circuit only (shared `Count`). | info | repeat both on `merge_circuit` |

Not gaps: neither system re-checks `count_c <= 16` (B) or a child's host record; BC-5 binds them through the
child's digest, which the child's own circuit computed. `MAX_TREE_PROOFS` is native only (`Tree::check`),
as BC-5 permits.
