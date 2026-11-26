# System A and System B against the specification's public statements

Current: specification **0.5.1** (`yugen-spec` tag `spec-0.5.1`, `d25a89c`), section 0.5.1 below.
The reviews against 0.5.0 (section 1) and 0.4.8 (section 2) are kept unchanged as history.

## 0.5.1 Review of 2026-11-23 against 0.5.1 (pay per proof, BC-6)

Trees: System A `yugen-proof-a` `f79c8b5` (`docs/recursion.md` "Specification 0.5.1 adopted",
decision S051-1; `src/bundle2.rs:804-886`); System B `yugen-proof-b2` `2b0cb46` (`docs/parameters.md`
§32, `docs/statement-layout.md` §9; `src/bundle.rs:137-166`, `src/bvirt.rs:105-149,296-323`);
bundler `yugen-bundler` `ee63d95` (`crates/bundler-core/src/statement.rs:127-224`,
`docs/decisions.md` C-19). Specification read: SPEC-207 to SPEC-213, §15.2, §15.3 (BC-1 to BC-6).

Vectors: `bundle.json` of both systems is byte-identical to `spec-0.5.1:vectors/bundle.json`
(SHA-256 `fe52d9ba…88d8` all three); B's `hash.json` likewise (`54b8b869…7b13`). Vectors are
yugen-ref's output at the tag, so "equal to the vector" is "equal to yugen-ref".

### 0.5.1.1 Runs (this review, `nice -n 10`, `-j 3`, each repository's own `target/`)

| System | Command | Result |
|---|---|---|
| A | `cargo test --test bundle2 -- the_statement_is_the_specifications the_programs_compute_the_vector_digests the_leaf_binding_vector_is_system_as` | 3 passed, 0 failed. Printed: 17 bundles (51 node digests), 15 differing statements, 24 tree rejections, 8 shapes 4/4/5, 4 canaries natively; the programs compute 33 sub-bundle and 18 merge digests of `bundle.json`; `leaf-binding` base and 8 alterations match |
| B | `cargo test --test bundle_statement --test bc6` | 12 passed (7 + 5), 0 failed. Printed: `WALK 17 bundles, 51 nodes, 33 claimed Internal slots` through internal-0 / top-0 / internal / top; statement-part rows internal-0 4,157, top-0 3,575, internal 2,381, top 7,198 AND |

Not run here: A's proving tests (`a_tree_proves…`, masked, mode 1), B's `uslot` main-circuit walk and
the real-proof chain (cited from §32.4 of B's parameters, not re-run).

### 0.5.1.2 Q1: node digests, `attr`, `bstmt`

**Yes, for all 17 bundle vectors (51 nodes) in both systems.** A: every record cell, `attr`,
digest and `bstmt` natively (`the_statement_is_the_specifications`) and all 51 node digests by
executing the statement programs (`the_programs_compute_the_vector_digests`). B: the same natively
(`the_native_statement_matches_every_bundle_vector_byte_for_byte`) and through the four virtual-tree
statement circuits in modes 0 and 1 (`every_bundle_vector_walks_through_the_internal_and_top_circuits`).
Both compute `attr = H_node-recs(c_A‖c_I1‖c_I2‖c_T)`, id `0x8a`, from script bytes (A
`bundle2.rs:852-886`, B `bundle.rs:137-166`). The 15 `statement-differs` vectors give their own
`bstmt` in both.

### 0.5.1.3 Q2: BC-6 and record substitution

**No substitution is accepted by one system and refused by the other at the published side.**

- Both systems' published proofs (A's one proof, B's Top) are for `bstmt`, whose `attr` is fixed
  by the four cells; the node recomputes every cell from the encoding (§15.3 BC-4/BC-5). Replacing
  any slot's script, exchanging slots, or unclaiming one changes `attr`, hence `bstmt`, so both the
  A proof and the Top proof must be redone. Evidence: the 15 differing statements give distinct
  `bstmt` in both suites; B's `the_differing_statements_do_not_verify_against_the_base_proofs`
  refuses 8 of them on the base Internal proofs and, for `one-slot-unclaimed` and
  `a-and-top-exchanged` (A or T slots only), carries the Internal proofs over while the Top (and
  A) must be re-proved for the new `bstmt`. That is the SPEC-208 property.
- Re-indexing the payee table without changing a script changes no cell in either system (both
  hash scripts, never indices: A `Tree::decode`, B `tree::decode_tree`).
- The asymmetry is on the proven side only, as §15.3 states: B binds `c_I1`, `c_I2` to the
  Internal proofs (`bvirt.rs:141-149`, `bc6_cells`; mutants `each_bc6_rule_is_needed`), A takes
  `attr` as advice (S051-1). An A prover can prove any `attr`, but consensus needs the A and Top
  proofs for one `bstmt`, so an Internal prover's pay rests on System B alone. Accepted by the
  specification ("a break of System B already lets its finder make System B's proofs without
  work"). **Provenance:** the argument is the specification's (Published, §15.3 BC-6); the
  checks above are this review's.

### 0.5.1.4 Q3: decisions D-7 to D-12 at 0.5.1

| Id | Status | Evidence |
|---|---|---|
| D-7 | **Done** (decision); one follow-up open | Flat merge states constant `H_node-recs(0^128)` and is declared non-consensus (B S51-4; `statement-layout.md` §9.4); `KM` is the top node. Mode-1 claimed trees go through internal/top at the statement circuits (`bc6.rs` walk, modes 0 and 1). Open: the mode-1 uniform main-circuit path (B §32.6, the reference prover's finding F-2 (not published); `tests/node_mode1.rs` still runs the flat circuits) |
| D-8 | **Done** at the statement circuits; main circuits mode 0 only | `bc6.rs` walk above (17 bundles, 51 nodes); `uslot` mode-0 walk of 16 bundles, 46 nodes (B §32.4, not re-run here). Real proofs of 3- or 4-input nodes open (B §32.6) |
| D-9 | **Open** (spec text) | §15.3 at `spec-0.5.1` names B-private Internal statements and top-0 (BC-6) but not the lift mode; no note lists lift / internal-0 / top-0 as B-private |
| D-10 | Informational, unchanged | A `bundle_merge_e2.py:117` (`1 ≤ count_c ≤ 4`), B `bvirt.rs:174` (`count_c < 2^16`); no accepted statement differs |
| D-11 | **Partly done** | B now decodes the tree field natively (`src/tree.rs`, S51-6; 24 tree rejections refused). Root-level verify and the 22 non-tree rejections stay the node crate's |
| D-12 | **Done for A, open for B** | A `the_leaf_binding_vector_is_system_as` passed (above); no B test reads `leaf-binding` (grep of `tests/`, `src/`) |
| Shared refusal vectors | **Open** | `spec-0.5.1:vectors/bundle_rules.json` holds node rules only (connect, weight, leaf-size, block-sequence); no in-circuit refusal list; neither system reads `bundle_rules.json` |
| Statement-id name | **Done** | B `uroot::node_name(auth_mode)` (B §32.1 item 6) |

### 0.5.1.5 Q4: the bundler's Internal statement (C-19)

**Match.** A throwaway crate outside every repository (scratch directory, path dependencies on
both crates, nothing written in either) compared `bundler_core::statement::internal_statement`
with `yugen_proof_b2::bvirt::native::commit_leaves` (internal-0, `n = 1, 2`) and `commit_cells`
(internal, `k = 1, 2`, depth 0 mode 0 and depth 4 mode 1, proofs up to 5,461), with cells zero
and two non-zero values: **18 cases, 0 mismatches.** Example: internal-0, `n = 1`, `c = 0`: both
`a4602ba6bd35549636bb60028f5ed413e96945c01683b86ee0bdfe0b767cb751`. By reading, both bodies are
`0x00‖LE16(n)‖lpi_1‖lpi_2‖c` (99 bytes) and `0x01‖LE16(k)‖cells_1‖cells_2‖c` with 71-byte cells
`depth‖LE16(count)‖content‖attr‖LE32(proofs)` (no `auth_mode`), framed `59 67 00 bf`, SHAKE256 to
32 bytes. One difference, no effect on honest input: B zeroes a position at or past `k_I` even if
a cell is passed; the bundler asserts `len ∈ 1..2` and writes only what it is given. C-19's "no
System B vector exists yet" can be closed by a B-side vector of these 18 values. Native function
vs circuit equality is B's `bc6.rs` (`commitments`), run above.

Side finding: `yugen-proof-b2` does not build with `default-features = false` (`phased.rs:245`
uses `crate::fold`, gated on `recursion`). Fix: gate `phased` on `recursion` too, or ungate `fold`.

### 0.5.1.6 Verdict

A and B state the same 0.5.1 statements as yugen-ref for every bundle vector; the BC-6 asymmetry is
proven-side only and by the specification's design; the bundler's C-19 statement equals B's.
Open: D-9 (spec note), D-12 for B, shared in-circuit refusal vectors, B's mode-1 main path, B
real proofs of 3/4-input nodes.

## 1. Review of 2026-11-20 against 0.5.0

Question: for every public statement both systems prove (mode-0 leaf, mode-1 leaf, sub-bundle,
published merge with `merge_rec`, root, and system B's internal arity-2 nodes), are the public
inputs, their order and encoding, the digest committed to, and every refusal rule those of the
specification (§11.1, §15.2, §15.3 BC-1 to BC-5, Appendix A.0 to A.2)? Where they are not, the
"two locks" argument fails for the part that differs.

Trees reviewed (read only; nothing was built or run for this section):

- System A: `yugen-proof-a` main `3f57a75`: `src/bundle2.rs`, `guests/bundle_sub_e2.py`,
  `guests/bundle_merge_e2.py`, `guests/bundle_constants_e2.py`, `src/wallet/v04.rs`, `src/circuit.rs`,
  `tests/bundle2.rs`, `docs/recursion.md` ("Specification 0.5.0 adopted"), vectors `tests/vectors/0.5.0/`.
- System B: `yugen-proof-b2` main `0a666b2`: `src/bundle.rs`, `src/bvirt.rs`, `src/node.rs`,
  `src/uroot.rs`, `src/statement04.rs`, `src/statement04m1.rs`, `tests/bundle_statement.rs`,
  `tests/uslot.rs`, `tests/node_mode1.rs`, `docs/parameters.md` §21 to §31, vectors `vectors/0.5.0/`.

Vectors: `bundle.json` and `bundle_rules.json` of both systems are byte-identical to `spec-0.5.0`
(checked with `cmp`). `statement.json` and `prechecks.json` are unchanged since 0.4.5, so the leaf
vectors of the 0.4.8 review still apply.

### 1.1 Verdict

**Yes for every published statement, with no soundness difference.** For the mode-0 and mode-1 leaf,
the sub-bundle, the published merge with `merge_rec` and the root, the two systems take the same
public inputs in the order and encoding Appendix A fixes for each, commit to the same node digest of
§15.3, and enforce the same refusal rules; no witness or statement was found that one system accepts
and the other refuses. System B's internal and top nodes export exactly the published digest that
system A's single merge program states (§1.3). The 0.4.8 gaps D-1, D-2, D-3 and D-5 are closed and
D-4 is moot (SPEC-206 fixes T1).

What remains is completeness and coverage, not soundness: system B's flat merge circuit still
fixes `attr` to zero (D-7), B's internal/top path is held to the vectors only through its native
function (D-8), and three items are informational (D-9 to D-12). The two-locks argument holds for
every statement 0.5.0 defines, on the condition (D-7) that system B's consensus merge key is the
top node's.

### 1.2 Statement table

| Statement | Spec 0.5.0 | A (`3f57a75`) | B (`0a666b2`) | Agree |
|---|---|---|---|---|
| Leaf, public input | `pi` 345 bytes; `E_A` 372-byte layout, tag `-mode0-v1`/`-mode1-v1`; `E_B` 44 words | `wallet/v04.rs:148-171`; tags `circuit.rs:115,121` | `bundle.rs:68-96` (`pi_bytes`, `pi_words`: `pi[0..296]`, mode word, `pi[297..345]`) | yes; the spec's `leaf-binding` vector (base and 8 alterations) matches both layouts (checked by script for this review, D-12) |
| Leaf, mode byte | P8 in circuit: 0 or 1 | program constant in `E_A` (tag and byte) | `statement04.rs:119` asserts 0; `statement04m1.rs:184` asserts 1 | yes |
| Leaf, mode 1 (C10, C11) | §11 | `wallet/mode1.rs`, `v04.rs` mode 1 | `statement04m1.rs` (parameters §29.2: 7 valid proven, 58 negatives each in its label's group) | yes (0.4.8's D-1 closed) |
| PC-1 per scheme | `auth_mode[scheme] + 2(scheme − 1)` | `bundle2.rs:1263` `leaf_check` (`consensus_p8`); P8 of 2 or 3 refused, no program | per mode byte `M` (parameters §28.1) | yes; neither has a scheme-2 circuit (0.4.8's D-3 closed as a difference) |
| Sub-bundle BC-1 | per leaf: `pi[296] = M`, PC-2, 48-byte values whole, leaf proof for `E_s(pi)` from the same bytes | `bundle_sub_e2.py`: 344 hinted bytes each `< 256` (:23), mode cell is the node's (:115, the `s[18]` cell), PC-2 over all 32 bytes (:79), `lpi` and `E_A` from the same bytes | `bundle.rs:414-455` (PC-1 :432, PC-2 :440, `leaf_pi_digest`); virtual path `bvirt.rs:194` (internal-0, PC-1/PC-2) | yes |
| Sub-bundle BC-2 | `D = H_bundle-node(0, M, LE16(n), Hvar_bundle-list(lpi..), host_rec, LE32(1+n))`, `host_rec` opaque, `1 ≤ n ≤ 4` | `bundle_sub_e2.py:104` (n range), :136-138 | `bundle.rs:447-454`; virtual `bvirt.rs:211` (top-0, `split` canonical) | yes |
| Merge BC-3 | per child: recompute digest from six cells, verify proof for it, `auth_mode_c = M`, `depth_c ≤ 4`, `proofs_c < 2^17` | `bundle_merge_e2.py:115` (depth), :119 (proofs), :120 digest with the node's `mode`, :156 `verify_sub` for it | `bundle.rs:536-551`, `bvirt.rs:125-140` (internal), P1 equality `node.rs:705-710` | yes |
| Merge BC-4 | `D = H_bundle-node(1 + max d_c, M, LE16(k), Hvar_bundle-kids(D_1..D_k), merge_rec, LE32(1 + Σ p_c))`, `merge_rec` opaque, `1 ≤ k ≤ 4` | `bundle_merge_e2.py:48` (k), :164-166 (`merge_rec` hinted, always read) | top node `bvirt.rs:173-189` via `merge_statement_attr` with four witness wires (`node.rs:717-731`) | yes (the top node); see D-7 for the flat merge |
| Merge of one | node gives `merge_rec` = 0 (B1 refuses a record), circuit need not check | not checked in circuit | not in circuit; the witness filler asserts it (`node.rs:928`) | yes (same constraint set) |
| `merge_rec` value | 0 unclaimed, else `H_host-rec(Hvar_host-script(script) ‖ LE16(0))` | `bundle2.rs:860-866` | `bundle.rs:121-132` (B's 0.4.9 form without `LE16(0)` fixed in §31) | yes; both match every `host_rec`/`merge_rec` cell of the 15 bundle vectors |
| Record decoding (node) | share 0 (`Share`); length 0/23/25/35 and exact template (`HostScript`); merge of one no record | `bundle2.rs:1010-1024`, :998 | `bundle.rs:136-166` (`record_ok`; no full tree decoder in B, D-11) | yes; both refuse the 12 record rejections of the vectors |
| Root / BC-5 | node computes `bstmt`; key by `(system, kind, mode)`; transfer and proof totals node-side | `verify_tree` `bundle2.rs:1238`: `check` (transfers, then `Proofs`), depth, kind by depth, keys pinned, mode from consensus | `uroot.rs` `check_root`: root keys `K0/KM/KI/KI0` equal the rule's, claims; `bstmt` supplied by the verifier as the public block | yes |
| System-specific additions to `bstmt` | fixed by consensus or recomputed (BC-5) | seeds and three deferred claims (`statement_merge`, `bundle2.rs:1168`) | key words, kind flags, batched claims in the uniform head | yes |

### 1.3 System B's internal arity-2 nodes against system A's single merge

System A proves a published merge of `k ≤ 4` children with one program. System B proves it with two
internal nodes and a top node (parameters §21, §22; `bvirt.rs`), and a sub-bundle with internal-0 and
top-0 nodes. Checked by reading:

- **Same children, same order.** The top node takes four children's cells as two halves and asserts
  the canonical split `k_L = min(k, 2)`, `k_R = k − k_L` (`bvirt.rs:146-161`); the published hash is
  computed over `[h0c0, h0c1, h1c0, h1c1]` with `Count(k)` (`bvirt.rs:187-188`), so position `i < k`
  of the published list is child `i` in both systems.
- **P2, same wires.** Each internal commitment `E = H_int(1 ‖ LE16(k_I) ‖ cells…)` is recomputed in
  the top node from the same cell wires that enter `H_bundle-node` and compared with the slot's
  public words (`bvirt.rs:176-186`); the right half only when `k_R > 0`.
- **P1, child binding.** Each internal node recomputes each child's digest from its cells under its
  own `auth_mode` constant and asserts the slot's proof is for that digest (`node.rs:705-710`), with
  BC-3's bounds (`bvirt.rs:131-139`); the top repeats the bounds on all four cells
  (`merge_statement_attr`).
- **P3, kinds.** A top node's slots accept kind 2 only, under `KI`; an internal node's accept
  published kinds 0 or 1 under `K0`/`KM` (`bvirt.rs:62-91`, `node.rs:1001-1005`).
- **Mode.** `E` carries no mode byte; the mode is bound because each internal circuit is compiled
  with its mode constant, so `KI` differs per mode, and the root compares `KI` with the consensus
  mode's (`uroot.rs` `check_root`). A mode-0 top over mode-1 internal nodes has no accepted root.
- **Exported digest.** The top's public block is `merge_statement_attr`'s output: depth `1 + max`,
  `LE16(k)`, `Hvar_bundle-kids` over the first `k` digests, `merge_rec` in `attr`, `LE32(1 + Σ)`,
  which is A's `node_digest` call at `bundle_merge_e2.py:166` cell for cell. No internal value
  (`E`, `k_I`, `H_int`) reaches a published digest.

Result: the published digest a B top node exports is the one A's merge program states, for every
`k` from 1 to 4 and every record.

### 1.4 What the 0.5.0 vectors cover and what they do not

Covered (both systems, byte for byte): the native digests of the 15 bundles (every node digest in
preorder, every `host_rec`/`merge_rec`, `bstmt`), the 11 `statement-differs` pairs, the 39 decoding
rejections (12 of them the new record rules), the 8 tree shapes, the 4 recursion canaries. System A
runs its two programs to the vectors' statements (`tests/bundle2.rs:311-390`, `root-claimed` from its
base's children); system B runs its sub-bundle and flat merge circuits to them
(`tests/bundle_statement.rs:269`, :456).

Not covered by any vector, checked here by reading (§1.2, §1.3):

1. In-circuit refusals: PC-1 and PC-2 inside a sub-bundle node, `n` or `k` outside 1 to 4, a child of
   depth 5, a child with `proofs_c ≥ 2^17`. Both suites have their own tests for these (A
   `tests/bundle2.rs:431-443`; B `tests/bundle_statement.rs:537-621`, `tests/shape445.rs`); no vector
   states them, so the two suites are not held to one list.
2. System B's internal, top, internal-0 and top-0 circuits: no vector tree is driven through them
   (D-8).
3. Mode 1 at the node level: 4 vectors carry `auth_mode` 1 (native digests only). A proves mode-1
   trees (`bundle2_mode1`); B's mode-1 node test uses the flat merge only (`tests/node_mode1.rs:445`).
4. The `leaf-binding` vector (`E_A` input and output, `E_B` words, eight alterations): read by
   neither suite (D-12).
5. The node-side totals (`Transfers`, `Proofs` at 20,000): unreachable within 4/4/5 (§15.2); A has
   them in `Tree::check`, B none (node work, D-11).

### 1.5 Differences

Status of the 0.4.8 list (section 2):

| # | 0.4.8 | Status at 0.5.0 |
|---|---|---|
| D-1 | B had no 0.4 mode-1 circuit | **Closed**: `statement04m1.rs`, 65 vectors (B parameters §29.2) |
| D-2 | B's node circuits on the 0.3.2 leaf | **Closed**: 345 bytes, 44 words, per-mode PC-1 (B parameters §28.1, `bundle.rs:33-42`) |
| D-3 | A's PC-1 single-scheme | **Closed**: `bundle2.rs:1263` per scheme; scheme 2 has no program in either system |
| D-4 | T1b in neither | **Moot**: SPEC-206 fixes `TREE_HASH` = T1. A removed T1b; B keeps it behind `build_tree(cfg, t1b)` (`statement04.rs:105`), not consensus |
| D-5 | B had no 0.4 mutation pass | **Closed**: `tests/wallet_mutation_04.rs` (B parameters §29.3) |
| D-6 | 48-byte P1/P3/P9 into A through 32-byte `E_A` | Unchanged, informational (recorded by A.1, §18.3) |

New at 0.5.0:

| # | Difference | A | B | Consequence and fix | Severity |
|---|---|---|---|---|---|
| D-7 | B's **flat** merge circuit (`Statement::Merge`, with lift mode) still fixes `attr` to 32 zero bytes (0.4.9); only the top node reads `merge_rec`. A's one merge program always reads it. | `guests/bundle_merge_e2.py:164-166` | `node.rs:737-750` → `bundle.rs:504-514` (`merge_statement_with` passes `[zero; 4]`) | Not soundness: a zero-`attr` proof proves only an unclaimed digest, which is then the node's. Completeness: a claimed merge cannot be proven by that circuit; B's mode-1 node test runs only it. Fix: give the flat merge the four `merge_rec` witness wires (`merge_statement_attr`), or retire it from the consensus key set and state that `KM` is the top node's for both modes; add a mode-1 top test with a claimed record. | Low (completeness; High if the flat circuit were the consensus `KM`) |
| D-8 | B's virtual-tree circuits are held to the 0.5.0 vectors only through `native::merge_digest_rec`: the tests drive synthetic depth-0 children, mode 0, `k` = 1 to 4 through internal and top (`tests/uslot.rs:465`, :501) and compare with the native function, which `tests/bundle_statement.rs:140` compares with the vectors. | n/a (one program, run to the vectors) | `tests/uslot.rs:465-540` | No vector tree with deeper or mixed-depth children, mode 1, or claimed sub-bundle and merge records together has been driven through internal and top nodes. Fix: a test that walks each `bundle` vector's tree through internal-0/top-0 and internal/top witnesses and compares every exported digest with the vector's. | Low (coverage) |
| D-9 | B has two node kinds the specification does not name: the **lift** mode (re-states a child's digest one level up, `node.rs:16-21`, :747-750) and the internal-0/top-0 pair for sub-bundles; §15.3's last bullet names only internal arity-2 nodes for merges. | none | `node.rs`, `bvirt.rs:194-229` | Sound as read: lift changes no digest, depth and proofs come from cells. Spec text only. Fix: §15.3's bullet (or A.2) lists lift, internal-0 and top-0 as B-private, or B retires lift. | Informational (spec text) |
| D-10 | Bound on a child's `count` cell: A `1 ≤ count_c ≤ 4`; B `count_c < 2^16`. BC-3 requires neither. | `bundle_merge_e2.py:117` | `bundle.rs:547-549`, `bvirt.rs:136-138` | No accepted statement differs: a child's count is bound by its digest, which its own circuit computed in 1..4 in both. | Informational |
| D-11 | B has no tree decoder or root-level `verify` entry (`Transfers`, `Proofs`, depth, kind of root); A has `Tree::decode`/`check`/`verify_tree`. | `bundle2.rs:945-1024`, :1238 | record rules only (`bundle.rs:136`) | Not a statement difference: §15.6 makes these node rules. The node crate must carry them for B. | Informational |
| D-12 | Neither suite reads the `leaf-binding` vector. | — | — | Checked by script for this review: `pi`, `E_A` input and output and `E_B` words of the vector match both layouts as read. Fix: one test each. | Low (coverage) |

Also noted: B's node statement-identifier name is `"bundle/node/mode0"` for every mode
(`uroot.rs:25`); the modes are separated by `cs_digest` (the mode is a circuit constant), so A-3
holds, but the name misleads. Fix: name by mode.

### 1.6 What must change

1. System B: D-7 (record wires in the flat merge, or retire it and name the top as `KM`; mode-1 top
   test with a record).
2. System B: D-8 (vector trees through the virtual-tree circuits).
3. Both: D-12 (`leaf-binding` vector test), and one shared list of in-circuit refusal cases (§1.4
   item 1), ideally as spec vectors.
4. Specification: D-9 (name lift, internal-0 and top-0 as B-private, or B retires lift).

No defect was found in the specification's statement text, and nothing in system A needs to change
for equivalence.

## 2. History: review of 2026-11-20 against 0.4.8


Review of 2026-11-20. Question: do both proof systems accept and refuse exactly the witnesses of the
wallet statement of specification 0.4.8 (`yugen-spec` tag `spec-0.4.8`, `b108428`; §6, §11,
Appendix A.1/A.2; SPEC-133/134/135/139/140/146/147/150)? If they do not, the "two locks" argument
(a forgery must break both systems) does not hold for the part where they differ.

Trees reviewed (read only):

- System A: `yugen-proof-a` main `0cdad2f`: `src/wallet/v04.rs`, `src/wallet/mode1.rs`, `src/lib.rs`
  (`prechecks04`), tests `wallet_vectors_04`, `spec_022`, `wallet1_vectors`, `bundle2`/`bundle2_mode1`
  (precheck tests).
- System B: `yugen-proof-b2` main `185e799`: `src/native04.rs`, `src/statement04.rs`,
  `src/witness04.rs`, `src/cx.rs`, `src/bundle.rs`, `src/node.rs`, `tests/wallet_vectors_04.rs`;
  branch `agg` (`wt/s045`, `8d1517f`) and `mode1` (`55988bb`).

Vectors: both systems carry copies of the 0.4.5 files; `statement.json`, `prechecks.json` and
`statement_t1b.json` are byte-identical at `spec-0.4.5` and `spec-0.4.8` (0.4.8 changed only
`host_index.json`), so the 0.4.5 copies are the 0.4.8 vectors.

### Verdict (0.4.8)

**Mode 0, tree shape T1: yes.** Constraint by constraint the two mode-0 circuits encode the same
statement, and on all 111 mode-0 vectors (13 valid, 97 negative, plus `auth-mode-2`) they give
the same verdict, each negative refused in the constraint group of its label.

**Not yet for the whole statement.** System B has no 0.4 mode-1 circuit and its bundle/node layer is
still on the 0.3.2 leaf (281-byte `pi`, 36 words). Neither system implements T1b. So the two-locks
argument holds today only for **mode-0 leaf proofs under T1**.

### Runs (both `nice -n 19`, 3 threads, private target directories)

| Suite | Result |
|---|---|
| A `wallet_vectors_04` (4 tests) | pass: mode 0 valid 13 / negative 98 (incl. `auth-mode-2`), each negative refused in its label's component; mode 1 valid 7 / negative 58; native check matches 83 + 55 labels |
| A `spec_022` (3) | pass: scheme-1 prechecks accepted 12, refused 7 (5 only by a precheck); 4 scheme-2 entries counted, not judged |
| A `wallet1_vectors` (1) | pass (the 0.3.2 programs no longer build, asserted) |
| A `bundle2::the_prechecks_bind_the_bundle`, `bundle2_mode1::the_mode_1_prechecks_bind_the_bundle` | pass |
| B `wallet_vectors_04` (4) | pass: mode 0 valid 13; negatives refused: constraints 91, decoder 5, precheck 1; prechecks 23/23 incl. scheme 2 |
| B per-vector dump (scratch crate over `statement04`, all 176 vectors) | 13 accept (= the 13 mode-0 valid); every constraint refusal names a group of the vector's label (`DummyBit`→C1, `NfReal`→C4, `Root`/`PathChild`→C5, …); all 20 mode-1 vectors (7 valid) refused at P8: no circuit |
| B dump over `statement_t1b.json` | 33 refused by the decoder (path length), 1 mode-1 at P8; `t1b-valid-shape-3` (two dummies, no path read) accepted; no T1b circuit |

Per-vector comparison, mode 0: no vector is accepted by one system and refused by the other;
decoder refusals coincide (the four `*-v-plus-2^64` C2 vectors and `sig-s2-*` encoding cases have
no encoding in either).

### Component table

| Component | Spec 0.4.8 | A | B | Agree |
|---|---|---|---|---|
| Public-input layout | `pi` 345 bytes, P1..P9 | `E_A` = SHAKE256 over the 372-byte A.1 0.4 layout (P1,P2,P3,P9,P7,P4–6,P8,tag `-v1`), 32-byte public input | 44 words, A.2 order (P1,P2,P3,P4–6,P7,P8,P9) observed raw | yes (each = its A.x layout; A's 32-byte transport is the spec's recorded A-side cost, §A.1) |
| 48-byte comparisons (SPEC-146) | all 48 bytes | 3 cells, every equality on 3 cells; cm/reg_root limbs asserted to spell cells; tests flip byte 47 of `cm_1`/`reg_root` | 6 words, every equality on 6; tests flip byte 47 of P1, byte 32 of P9 | yes |
| C0 / PC-2 | verifier precheck | `prechecks04` (native); bundle: in `leaf_public` | `Public::precheck` (native); bundle: in-circuit (0.3.2 layout) | yes at leaf |
| C1 dummy bits | boolean | range 2 table | `dummy >> 1 = 0` | yes |
| C1 / PC-1 P8 | per scheme (SPEC-150) | single mode, scheme 1 only; mode byte a program constant in `E_A` | `precheck_scheme` per scheme; `auth_mode = 0` asserted in circuit | **differs (scheme 2)**, see D-3 |
| C2 ranges | v, w < 2^64; pos < 2^40; rpos (mode 1) | 64-bit limbs; 20 base-4 digits; 40 bits | 64-bit words; `pos >> 40 = 0` | yes (mode 0) |
| C3 | v=0, nf=H_nf-dummy(dx) | yes | yes | yes |
| C4 | nkc(48), sig, auth, cm(172 B, 48), PRF_nf | yes | yes | yes |
| C5 T1 + selectors (SPEC-147) | digit selectors, one-hot | derived form: digit range < 4, slot table | derived form: two bits of `pos` per level | yes |
| C5 T1b | open (F-2) | absent | absent | both absent |
| C6 | rho = H_rho(nf_1‖j) 48 B, cm 48 B | yes | yes | yes |
| C7 | over integers, < 2^66 | halves + carry digit | 64-bit adds + carry count | yes |
| C8 | h ≤ 12288 | yes (0.3.2 Falcon part) | `HWidth`, `HMax` | yes |
| C9 F2–F5 | | 0.3.2 Falcon part, unchanged | NTT congruence mod q; s1 ∈ [−6144, 10239] by width, the excess unreachable under F5 (6145² > bound) | yes |
| C10, C11 (mode 1) | rkh, exit tag, BE comparison, depth-40 registry | built (`recovery_and_registry`), 7/58 vectors | **absent at 0.4** (0.3.2 `statement1` only, 36 words) | **no**, D-1 |
| Bundle/node leaf layout | 345-byte `pi` (BC-1) | 0.4 leaf in `bundle2` | **281 bytes / 36 words** on main and on `agg` (`src/bundle.rs:32`) | **no**, D-2 |

### Differences

| # | Difference | Consequence | Severity |
|---|---|---|---|
| D-1 | B has no 0.4 mode-1 circuit. | Every mode-1 witness (7 valid vectors) is accepted by A only; mode 1 has one lock. No effect while consensus is mode 0 (PC-1 refuses mode 1), so no launch divergence. | High for the release that enables mode 1 (R-29); blocks the two-locks claim for it |
| D-2 | B's bundle and node circuits (main and `agg`) verify the 0.3.2 leaf: 281-byte `pi`, 36 public words. | B cannot aggregate any 0.4 leaf; its BC-1 enforces PC-1/PC-2 over the old layout. A bundle of 0.4 leaves has one lock (A). | High (blocks the bundle path of system B) |
| D-3 | A's PC-1 is single-scheme (`prechecks04(public, mode)`); B's is per scheme (SPEC-150). | None at launch: scheme `0x02` is refused by consensus (flag bit 9) before the proof. Once scheme 2 is enabled A has no verifier for its 8 entries. | Low now; must be built before scheme 2 |
| D-4 | Neither system implements T1b; neither runs `statement_t1b.json`. | None while T1 stands; if F-2 picks T1b both circuits change and neither has been held to the T1b vectors. | Medium (open decision) |
| D-5 | B has no 0.4 mutation pass (`wallet_mutation.rs` is 0.3.2); A has one for mode 0 and mode 1. | Not a statement difference; B's group coverage at 0.4 rests on the vectors only. | Low |
| D-6 | Binding form of 48-byte P1/P3/P9: B absorbs them whole, A through the 32-byte `E_A`. | Recorded by the spec (A.1, §18.3): an `E_A` collision (2^128 class) fools A only. Not a witness difference. | Informational |

No difference was found in mode 0 under T1: no witness one system accepts and the other refuses,
and no binding difference beyond D-6.

### What neither system checks that the specification requires

- T1b (§6), should F-2 choose it, and its vectors.
- PC-1 for scheme `0x02` inside a system A verifier (B has it natively only; neither has a scheme-2 circuit, which SPEC-139 does not yet require).
- C0 inside the leaf circuit: neither enforces it; allowed (MAY), both rely on PC-2 as the spec says.
- F2's failure branch (fewer than 512 accepted draws): no vector in the spec; neither suite tests it.

### What must change

1. System B: build the 0.4 mode-1 circuit (C10, C11 at 48-byte registry nodes, 44 words, `auth_mode = 1`) and run the 65 mode-1 vectors and `wallet1`-style mutation pass.
2. System B: move `bundle.rs`/`node.rs` (main and `agg`) to the 345-byte `pi` / 44 words, with PC-1 per scheme and PC-2 in-circuit (BC-1).
3. System A: per-scheme PC-1 (`consensus_auth_modes`, SPEC-150) in `prechecks04` and the bundle's leaf check, judging the four scheme-2 entries.
4. Both: after F-2, the chosen shape's circuit and `statement_t1b.json` (or the T1 vectors) in the suite.
5. System B: a 0.4 mutation pass over `statement04` groups.

### Lead agent's decisions on the 0.5.0 findings (2026-11-20)

| Id | Decision | Why | Follow-up |
|---|---|---|---|
| D-7 | Retire B's flat merge circuit as a consensus key; B's top node (internal arity-2 nodes, `design-b-aggregation.md` (d)+(c)) is the published-merge key in both modes | It is the adopted B design and already reads `merge_rec`; adding record wires to a circuit that will not ship is wasted work | B: mark the flat merge non-consensus; drive a mode-1 tree with a claimed record through the internal/top path (closes the mode-1 half of D-8) |
| D-8, D-12 | Accepted as coverage gaps | Low; no accepted statement differs | B: run the 0.5.0 vector trees through the internal/top circuits; both: read the `leaf-binding` vector in a test |
| D-9 | Approved: an informative note in the specification (§15.3) naming B's lift mode and its internal-0 / top-0 pair | Spec text only | Next specification patch |
| D-10, D-11 | Informational; D-11's tree and total checks are node rules, owned by the node crate (plan step 0.17) | — | Node build |
| Shared refusal vectors | Approved: specification vectors for in-circuit refusals (PC-1/PC-2 inside a node, n or k outside 1–4, depth 6, `proofs_c` ≥ 2^17) | One list both systems run removes the remaining read-only checks | Next specification patch |
| Statement-id name | B renames its node statement-ids per mode | Misleading name, no soundness effect | B, with D-7 |
