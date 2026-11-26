# Referee report: the flag walk, the shared stages of `P*`, and row 8 as the one consensus leaf row (system A)

Part of Yugen. 2026-11-19. Independent, adversarial review of three changes to the
in-circuit verifier ("guest") of masked row-8 leaf proofs in `yugen-proof-a` since the last referee
read (`docs/guest-masked-referee.md`, at `4862878`), at commit `b8b85af` (read only):

1. the drawn-order walk with one flag a query (`guests/e2/j_wi.py`, `wi_queries`);
2. the shared stages of `P*` at the last level's rows (`wi_star_classes` and its callers; `WI_CUT`,
   `placeholders.rs::wi_star_cut`);
3. row 8 as the sole consensus leaf row (`src/bundle2.rs`) and the every-`t` query counts
   (`verifier/src/params.rs`).

Also re-checked: the earlier report's m-4 as restated, and its notes n-2 and n-3.

The reviewer wrote none of the reviewed code or documents. Nothing but this file was written. The
reviewer's tests ran in a git worktree of `yugen-proof-a` at `b8b85af` (`wt/referee-pstar`), which is
removed; their source is Appendix A. Line numbers are of the files at `b8b85af`
(`git show b8b85af:<path>`); "guest line" is a line of the assembled guest
`vendor/leanMultisig/guests/lean_ethereum_e2.py`, which was reassembled from its parts in the worktree
and found identical to the committed file.

Provenance. Every finding and every argument of this report is **Original (the Ycash developers,
2026)**, first recorded in this file, unreviewed. Theorem D and its conditions D-1 to D-5 are those of
`docs/lemma-d-duplicate-openings.md` (Original, the Ycash developers, 2026; refereed in
`docs/lemma-d-referee.md`); this report checks the code against the conditions and does not re-prove
the theorem. The property of the subspace polynomials used in section 3.2 is the standard one of the
novel polynomial basis; it is **proved here from the recurrence the code uses**, and no paper was read
for it (the builder names, from memory, Lin, Chung and Han, "Novel Polynomial Basis and Its Application
to Reed-Solomon Erasure Codes", FOCS 2014; that paper is not in the reference folder, was not read by
the reviewer either, and nothing here is attributed to it). The transcript is the spBCS form of Sharp
and Grubbs, ePrint 2026/2615, as `docs/qrom-compilation.md` section 2 cites it; the paper was not read
for this report.

## 0. Verdicts

| Subject | Verdict | Conditions |
|---|---|---|
| 1. The flag walk | **PASS** | none for soundness; the claim of m-4 gains one clause (finding W-a) |
| 2. The shared stages of `P*` | **PASS WITH CONDITIONS** | P-1: a static assertion in the guest that the cut is the path's depth below the cap; P-2: the controls of section 3.5 and an every-candidate check enter the suite |
| 3. Row 8 alone; the counts | **PASS WITH CONDITIONS** | R-1: `verify` binds the leaf key to the leaf circuit it checks, and the consensus keys are pinned in a test |

| Class | Count | Findings |
|---|---|---|
| BLOCKER | 0 | no attack found on any of the three subjects |
| MAJOR | 0 | |
| MINOR | 4 | P-1, P-2, R-1, W-a |
| NOTE | 8 | P-3, P-4, R-2, R-3, R-4, R-5, n-2 (open), n-3 (open, now also stale) |

No path was found by which a query's check uses a value computed for another position, by which a
drawn query goes unchecked, or by which a node that calls `bundle2::verify_tree` with the consensus
leaf program accepts a tree holding an unmasked leaf or a leaf of another program or row.

## 1. Method

Read whole at `b8b85af`: `guests/e2/j_wi.py`; in the assembled guest `decode_query_windows`,
`query_window`, `query_window_split`, `assert_window`, `walk_path`, `verify_merkle_cap`,
`level_positions`, the head of `novel_eval`, `exponent_tables`' window table; the diff
`4862878..b8b85af` of `placeholders.rs`, `child.rs`, `whir.rs`, `stable_prover/pcs/src/wi.rs`,
`params.rs`, `assemble.py`, `src/e2.rs`; `src/bundle2.rs` lines 36 to 340, 810 to 1000;
`guests/bundle_sub_e2.py` `main`; the seed and statement lines of `guests/bundle_merge_e2.py`;
`tests/guest_masked.rs` lines 736 to 1180; `bench/soundness/cert.py`, the head of `shapes.py`;
`docs/recursion.md` 10.00000 and the table of 10.0000; `docs/lemma-d-duplicate-openings.md` section 3.

The two kinds of discrepancy of the earlier report (its section 1) are used again: (a) a wrong
formula, which the honest proof shows at the shapes that are run; (b) a check missing or made on a
value the prover supplies, which no honest run shows. For subject 2 a third kind matters and was
looked for: (c) **a read of a cell nothing wrote**. The guest's memory is write-once and a cell never
written holds what the prover chooses, so a table indexed past its end is a value of the prover's.

Run (section 6): two tests of the reviewer and two of the builder's, at the wallet's shape.

## 2. Subject 1: the flag walk (`wi_queries`, `j_wi.py:305-365`)

Advice: one cell a drawn query, `refs[k]` (`wi_first`, `:331`); and, for a query whose cell is zero,
its row (`merkle_leaf_rows`), its path (`merkle_children`) and the level's cap and cap flags. Derived
from the transcript: `positions[k]` and the query's windows (`level_positions`,
`decode_query_windows`: windows are hinted, each range-checked to its width, disjoint, covering the
`depth` bits exactly, and rebuilt to the squeezed word, so they are a function of the stream).

### 2.1 W-1 to W-7 in the code

| # | Where | Finding |
|---|---|---|
| W-1 | `:339-341` | Met. `if ref != 0` splits the cell; in the second arm `log(ref) < 512` makes it `g^j`, `j < 512`. A cell that is neither is refused (run: guest lines 5367, 5368). |
| W-2 | `:349`, `wi_query` `:264-274`, `:295-296`; `wi_level_queries` `:371-376`; `wi_open` `:583-584`, `:590-591`, `:611-612` | Met. The row is hinted, hashed under `SB_TAG_LEAF` with its salt, walked by `query_win_ptrs[xi]`, the query's own windows, into the level's one cap; the cap's root is written into `level_roots[lvl]`, which already holds the transcript's root (the commitment root, or the item `sent` absorbed before this level's positions were drawn): a write-once equality. At the last level the check `P*(x) = column + c fold(row)` is in this arm. |
| W-3 | `:340-341`, `:343` | Met. `g^(k-1-j)` is a power below 512 with the loop's own `xi = g^k`, so `0 <= j <= k - 1` (the order of `g` is `2^64 - 1`; at `k = 0` no `j` passes). The named record's mark must be 1, so a chain has length one. Two queries cannot name each other. |
| W-4 | `:344-347` | Met. `positions[ref] == positions[xi]`: whole cells, both written by `level_positions` for this level (indices below the count; `squeezes` covers the count, `placeholders.rs:725`). The record is `(0, fold of record j)`. Every query writes its record in either arm. |
| W-5 | `:353-357`, `:592-594`; `wi_level_residual` `:443-524` | Met. `h <- (h + v_k) / lam` over every drawn query in drawn order, scaled by `lam^(n+1)`: `sum_k lam^(k+1) v_k`, duplicates included, as `wi.rs`. `wi_level_residual` is unchanged in the diff. |
| W-6 | `:341` stands before `:342-343` | Met by W-3: record `j < k` was written whole by iteration `j`. |
| W-7 | `tests/guest_masked.rs:871`, `:942`, `:1098` | Met, and run here: `walk_advice_at_every_oracle` passes; 8 refusals an oracle, each at the named line; the unopened position is refused at the position equality at all four oracles, and the guest without the equality accepts it at the last oracle alone (741,931 cycles) and refuses it at the terminal at the other three. |

### 2.2 D-1 to D-5 in the code

- **D-1.** No transcript code changed in the diff of `j_wi.py` (`wi_head`, `wi_star`, the calls of
  `opening_round`, `opening_message`, `level_positions` are as at `4862878`). Met as before.
- **D-2.** A first-flagged query's record is authenticated at `p_k`: W-2. The cap is lazily hashed
  (`verify_merkle_cap`): `walk_path` writes flag 1 at the parent of the cap entry it reaches
  (`flags[2^(cap_depth-1) + q]`), an unflagged internal node pins its children's flags to 0, the root
  is always hashed; so every reached entry is joined to the root by hashes the guest evaluates. Read
  again at `b8b85af`; unchanged.
- **D-3.** The symbol of query `k` is its own record's, or that of a query `j < k` marked first with
  `positions[j] == positions[k]`, whole cells of one level (the encoding `K(p)` is injective on `depth`
  bits). Met. **This is whole-position equality, not class equality** (section 3.4, test P2).
- **D-4.** A query takes exactly one arm: at most one record a drawn query. Met.
- **D-5.** Below the last level the record holds the fold `(d0, d1)`, a function of the row,
  `x = positions[k] + COORD_BASIS[depth]` and the level's fold challenges. At the last level the
  decision of a first query is `P*(x) = column + c fold(row)`: a function of the decoded leaf, the
  position, `c`, the fold challenges and `P*`, a non-oracle message; with the shared stages the left
  side is still a function of `P*` and the position alone (section 3). A duplicate takes no decision
  of its own, which D-3 allows. Met.

### 2.3 Finding

**W-a (MINOR, the claim; the earlier m-4 as restated).** `docs/recursion.md` 10.000 and
`docs/zk-merge-notes.md` 4 item 5 now say: "the guest has an accepting run for (seed, public input)
exactly when a proof exists that the native verifier accepts". The trailing-scalar part is settled:
right, with no soundness content. With the flag walk the word "exactly" needs one clause. "If": holds
(a native proof gives the host's advice). "Only if": a guest run may open one position twice with two
"first" flags and two **different** rows; if both authenticate, the run accepts and no single native
proof need exist. Two different leaf inputs or paths authenticated at one position of one root are a
collision of the leaf or node hash, so the direction holds except with a collision in hand: this is
exactly Theorem D (Proposition D.2), not an identity. Under the strict walk of `4862878` the claim was
exact. Fix: "... exactly when a proof exists that the native verifier accepts, the 'only if' direction
up to a collision of the tree's hash (`lemma-d-duplicate-openings.md`, Theorem D)", in both places.
There is still no test in the suite for the trailing scalar (the earlier report's R3 line); a
four-line test would record it.

## 3. Subject 2: the shared stages of `P*`

### 3.1 What is computed

`P*` is `lf` scalars of the stream, absorbed before the last level's positions are drawn
(`wi_star`, then `level_positions`, `j_wi.py:602-603`), copied into `2^n_bits` values, zero past
`lf` (`:144-153`). A last-level row at position `p` has `x = K(2^depth + p)` and the check needs
`P*(x) = sum_c star[c] prod_(i in c) What_i(x)`.

`wi_star_classes` (`:212-240`) builds, before any row is read, `T_cut`: for each class
`c in [0, 2^(depth - cut))` the `2^cut` values of `P*` with the variables `n_bits - 1` down to `cut`
folded at `What_v(K(2^depth + c' 2^(v+1)))` for the first child and that plus one for the second
(`wi_star_pair`, `:185-201`). A row then evaluates the `cut` low variables at its own `x` on the entry
of its class (`wi_query`, `:290-293`).

### 3.2 Why the staged value is `P*(x)`

Claim: for `v < depth`, `What_v(K(2^depth + p))` depends on `p >> v` alone, and setting bit `v` of `p`
adds one. Proof from the recurrence the guest and the native verifier use (`W_0(y) = y`,
`W_(i+1)(y) = W_i(y) (W_i(y) + W_i(beta_i))`, `beta_i = COORD_BASIS[i]`, `What_i = W_i / W_i(beta_i)`):
by induction `W_i` is additive over `F_2` with kernel `V_i = span(beta_0 .. beta_(i-1))`. Indeed if
`W_i` is additive with kernel `V_i` and `beta_i` is outside it, then
`W_(i+1) = W_i^2 + W_i(beta_i) W_i` is additive (a square and a scalar multiple of an additive map),
vanishes on `V_i` and at `beta_i`, hence on `V_(i+1)`, and has degree `2^(i+1) = |V_(i+1)|`. So
`W_v(K(2^depth + p)) = W_v(K(2^depth + ((p >> v) << v)))`, the low `v` bits of `p` being a vector of
`V_v`, and `W_v(y + beta_v) = W_v(y) + W_v(beta_v)`. The constants `WI_ROOTS`, `WI_ROOT_INVS` are the
ones the unshared evaluation (`wi_star_at`) already used. The builder's native test
(`whir.rs:438`) checks the same statement and the staged evaluation against `novel_eval` at every
position for five shapes; it was read, not run.

### 3.3 Advice and derived values in the shared computation

| Value | Source | Advice? |
|---|---|---|
| `star` (P*) | the stream, absorbed before the positions | bound message |
| A stage's class point `bits * COORD_BASIS[v+1] + COORD_BASIS[depth]` | `bits = tabs[g^c']`, `c'` the loop index; `tabs` is the window table the guest itself writes (`g_squares[WIN_TAB_AT + n] = n`, 2,048 entries) | no |
| `WI_ROOTS`, `WI_ROOT_INVS`, `WI_CUT`, `WI_STAR`, `n_bits`, `depth` | constants of the program (its key) | no |
| The row's class `cls = g^bit (g^q)^2` (`:291-292`) | the query's cap child bit window and cap index window: hinted, range-checked to 1 and `cap_depth - 1` bits, parts of the exact, disjoint cover of the position's `depth` bits that is rebuilt to the squeezed word; the same two cells `walk_path` sends this row's digest to the cap with | pinned to the transcript |
| The row's `x` | `positions[xi] + COORD_BASIS[depth]`, the same query's position | pinned |
| The row, its path, the cap | advice, authenticated (W-2) | advice, checked |
| `refs[k]` | advice, W-1 to W-4 | advice, checked |

Nothing in the stages is advice. The one thing a prover touches is the pair of windows, and those are
a function of the squeezed word.

### 3.4 The attacks asked about

- **A wrong sharing key / a value computed for a different position.** The key is `p >> cut` with
  `cut = depth - cap_depth`: the cap child bit is bit `depth - cap_depth` of `p` and the cap index the
  bits above it (`decode_query_windows`, offsets `path` and `path + 1`). `WI_CUT` is computed as
  `depth - cap` from the same `OpeningShape::cap_depth` that gives `LIG_CAP_DEPTH`
  (`placeholders.rs:714`, `:887`, `:1031`, `:1234-1240`), and the layout's `log_domain` is asserted
  equal to `LIG_TREE_DEPTH` (`:1013`). So the entry a row reads is its own class's. See P-1.
- **Advice-chosen grouping.** There is none: the classes are all `2^cap_depth` values of the loop
  index, computed whether or not a query falls in them.
- **A stage keyed on fewer bits than it depends on.** Stage `v`'s entry for class `c = p >> v` uses
  `What_u` at the class point for `u >= v` only, each a function of `p >> u`, which `c` determines
  (3.2). `v <= n_bits - 1 <= depth - 1` by `wi_star_cut`'s guard `n_bits <= depth`, so the coset bit
  `2^depth` is never a kernel vector. The top stage has `2^(depth - n_bits)` parents, all reading
  `P*` itself (`top`), which is right: above `n_bits` there is no variable to fold.
- **A read of an unwritten cell (kind c).** `cls < 2^cap_depth` by the two range checks; the table
  has `2^(depth - cut) = 2^cap_depth` classes of `2^cut` values, every one written by the last stage;
  a row reads `2^cut` values from `cls * 2^cut`. Stage reads: parent `c' < n_par`, values `m` and
  `m + half` inside the parent's `2 half`; the top stage reads `star` below `2^n_bits`, all written
  (`wi_star` writes zero past `lf`). `tabs[g^c']` with `c' < 2^(cap_depth - 1) <= 2^7`. No read
  outside written cells, **given `cut = depth - cap_depth`, `cut < n_bits <= depth` and
  `2^(n_bits-1) < WI_STAR <= 2^n_bits`**, which are `wi_star_cut`'s guards and the assertion at
  `placeholders.rs:1026`.
- **The order of queries.** The table is complete before the walk and no query writes to it.
- **Duplicates under the flag walk.** A query flagged "as before" evaluates nothing and reads no
  table entry; it is covered by a first query at the **same position** (D-3), whose check used that
  position's class and `x`. Two positions of one class are not confused: test P2 (section 6) flags a
  query "as query j before" with `j` at another position of the same class and leaves its row out;
  the guest refuses at the position equality, and the control guest without that line accepts. On
  the suite's proof the last oracle has 186 queries at 181 positions in 63 of the 64 classes, so the
  honest run already exercises duplicates together with the sharing.
- **A check skipped for some query.** The asserted equality (`:295-296`) is unchanged and is reached
  by every first-flagged query of the last level; the M-1 control (`shift_final_message`) is refused
  at that line with the stages (the builder's test, not re-run here).

No attack was constructed. The argument is complete for every candidate provided the three
build-time facts in bold hold, which is finding P-1.

### 3.5 The control guests: what each would catch, and what none covers

Each control is the guest with one line changed, run on the honest proof; all eight were run here
and each refuses at the last rows' check (guest line 5323).

| Control | Mistake it stands for |
|---|---|
| Builder 1: class without the cap child bit | a sharing key of too few bits (`p >> (cut+1)` used as `p >> cut`) |
| Builder 2: second child folded at the first child's `What` | a stage keyed on fewer bits than it depends on (bit `v` ignored), at every stage |
| Builder 3: class entry at half its stride | the row's address into the table |
| Builder 4: a stage reading its parent at the child's stride | a stage's address into its parent |
| Referee a: class point one bit low (`COORD_BASIS[v]`) | a stage evaluating `What_v` at another class's point |
| Referee b: the top stage's live count 1 | the zero tail of `P*` taken longer than it is |
| Referee c: the stages stop one variable early | the table's cut and the row's cut disagreeing |
| Referee d: the top stage reading a parent entry | the top stage reading past `P*` (kind c) |

Not covered by any control, and why that is or is not a gap:

1. **A check made on advice.** There is none in the sharing (3.3), so there is nothing for a
   prover-side control to reach beyond M-1's.
2. **Candidates other than the wallet's.** The controls run at `2^22`, rate 1/4 only. Of the row's 48
   candidates 32 have `WI_CUT = 6` (printed from the placeholder map, section 6); the suite runs an
   honest proof through a sharing arm at four of them at most (`2^22` at 1/4 and 1/2, `2^21`, `2^24`).
   The other arms are compiled into the consensus program and never run. Finding P-2.
3. **A wrong `WI_CUT` for a candidate.** An honest run of that candidate would show it; a candidate
   that is never run would not, and the case `WI_CUT > depth - cap_depth` is kind (c). Finding P-1.
4. The one class of 64 the suite's proof does not hit. No content: the stages are one loop.

### 3.6 Findings

**P-1 (MINOR, a soundness-relevant invariant held by another file).** `guests/e2/j_wi.py:288-293`,
`:606-609`; `placeholders.rs:1234-1240`. `wi_query` takes the class from the windows at
`depth - cap_depth` and the table's layout from the parameter `cut`; nothing in the guest says they
are the same number. They are, by `wi_star_cut`. If a later edit of the cost rule or of the cap rule
made `WI_CUT[cand]` larger than `depth - cap_depth` for some candidate, a row of that candidate would
read past the table: cells nothing wrote, values of the prover's choice, and the last rows' check
would bind nothing (the M-1 attack: any `P*` consistent with the terminal). No test would show it
unless that candidate is run. Fix, in the guest, where the zkDSL already uses the pattern
(`assert_window`'s last arm): in `wi_query`'s shared arm
`if const(cut != depth - cap_depth): assert 0 == 1`, and in `wi_star_classes`
`if const((cut // nbits) + (nbits // (depth + 1)) != 0): assert 0 == 1` (cut < nbits <= depth); or
drop the parameter, compute `depth - cap_depth` in `wi_query`, and keep `WI_CUT` as a flag. With the
assertion the compiled program is unchanged for a correct table.

**P-2 (MINOR, tests).** `tests/guest_masked.rs:998`. (i) The controls a to d of 3.5 are not in the
suite (source: Appendix A). (ii) No test visits every candidate. Fix: a unit test beside
`wi_star_cut` that, for every candidate of rows 8 (and any later masked row), asserts
`cut == 0 || (cut == depth - cap_depth && cut < n_bits && n_bits <= depth && padded > 2^(n_bits-1)
&& padded <= 2^n_bits && cap_depth <= 8)`; and the builder's native test
(`whir.rs:438`) extended to the three `(depth, n_bits, padded)` triples the candidates actually have
(last-level depth 11, 12, 13 with `n_bits = 9`, `padded` 448 and 512), of which it has `(12, 9, 448)`
and `(12, 9, 512)`.

**P-3 (NOTE).** `the_shared_stages_...` asserts the shared and unshared guests both accept the honest
proof; it does not run the M-1 control on the unshared guest and the shared guest side by side. The
separate test covers the shared guest, which is the consensus one. No action needed.

**P-4 (NOTE, citation).** The source paper of the novel polynomial basis is not in the reference
folder; the builder marks it "from memory, not read" in `whir.rs:422-437`. The property used needs
no source (3.2). `yugen-proof-a/REFERENCES.md` should carry the entry as "named from memory, not
read, nothing rests on it" until the paper is supplied.

## 4. Subject 3: row 8 as the sole consensus leaf row; the counts

### 4.1 What binds the leaf's row and program in what the parent proves

- The sub-bundle program takes the leaf seed as advice (`bundle_sub_e2.py:101`), uses it as the bound
  IV of every leaf's transcript (`h_sub.py`: the header absorbs the label, the proof salt, `SB_ROW`,
  the seed and the public input), and publishes it in its statement with the batched claim on the
  leaf bytecode (`:134`). `SB_ROW`, `ZK`, the query counts and `WI_CUT` are constants of the program,
  hence of its key.
- `bundle2::verify` (`src/bundle2.rs:948`) refuses programs that are not `Programs::build`'s over
  `CONSENSUS_LEAF_ROWS = [row 8]` (`:146`), then recomputes: `seed_L = bind_iv(row 8, leaf IV)`
  (`:326-333`; `ParamSet::descriptor`, `params.rs:396`, puts every field of the row and every count of
  its table under the IV), `seed_S`, `seed_M` under row 9, each deferred claim on its bytecode
  (`:816-826`), the statement, and verifies under row 9.
- The merge program rebuilds each child's statement from its own three seeds
  (`bundle_merge_e2.py:127`, `:139`), which are the ones in its own statement (`:183`).

So a tree accepted by `verify_tree` has, at every sub-bundle, leaf proofs that the row-8 in-circuit
verifier accepted under `seed_L` of the leaf program the node handed in. A proof made under row 7
has another header and another seed; a sub-bundle program compiled for row 7 has another key, which
`seed_S` in the statement excludes. That the refusals of a row-7 leaf at sub-bundle and merge level
are "host-level (no witness)" is the right description and is sufficient: the in-guest refusal of a
hand-made witness is the row-8 guest's soundness, and no separate in-guest "is this row 7" check
could exist. One inherent limit, for the record: a verifier cannot make a prover draw its masks at
random; row 8 guarantees the masked protocol was followed, not that a wallet which wants to leak its
own witness cannot.

No path through `verify` / `verify_tree` with the consensus leaf program was found.

### 4.2 The query counts

One source of truth: the statics of `params.rs` (`CAT1_TREE_WI_QUERIES`, `:293`). Readers:
`ParamSet::level_queries` (`:384`) → `whir.rs:77` (`derive_config_for`) → the native verifier and
prover; the same config → `child.rs:21` (`whir_levels_for`) → `placeholders.rs:682`, `:878`
(`LIG_QUERIES`), with the hiding layout's counts asserted equal (`:1013`) and at most 512 (`:1015`);
`ParamSet::descriptor` → the bound IV → `seed_L`. The guest's counts cannot differ from the native
verifier's without a different table, and a different table is a different seed and a different
sub-bundle key. Checked here: the wallet candidate's `LIG_QUERIES` in the placeholder map reads
`234, 166, 169, 186` (section 6).

The certified shapes: `bench/soundness/cert.py` parses the built tables out of `params.rs`. The
reviewer compared the tables at `b8b85af` with the committed output
`bench/results/soundness-rows-every-t-20261119.txt` shape by shape: 223 shapes with counts, 0
mismatches, every one PASS, row 8's least margin +0.202 bits. `cert.py` and `shapes.py` were not
re-run and the calculator was not re-derived.

### 4.3 Findings

**R-1 (MINOR, host interface; the one path found).** `src/bundle2.rs:43-46`, `:218-232`, `:968-976`,
`:982-995`; `src/e2.rs:28`. `LeafProgram` is a pair of public fields `(circuit, key)` that nothing
ties together. `verify_checked` reads its three checks from `leaf.circuit.params` (`wallet`,
`auth_mode`, `masking`); `seed_L` and the leaf claim come from `leaf.key`. Failing input:
`LeafProgram { circuit: &the masked wallet circuit, key: &Key::of_program_for_tests(P') }` for any
`MUL2`-free program `P'` (that constructor is public since this change): every check passes on the
circuit, and `verify_tree` accepts a tree of proofs of `P'` as a consensus tree. Likewise the other
fields of `Params` (`fault`, `beta2`, `pi_tag`, `commit_prefix`, `h2p_blocks`) are not compared: a
circuit built with `fault: Some(..)` is "the wallet program of mode 0" to `verify`. No network party
can use this: it is the node's own argument. It is the answer to "what binds the leaf program": today,
the caller. Not run (it needs a tree proved over `P'`); by reading. Fix: (i) `verify` computes the key
from the circuit, or `LeafProgram` gets private fields and one constructor that does;
(ii) `verify_checked` compares `leaf.circuit.params` with the canonical parameters of the mode
(`min_log_bytecode` aside); (iii) a test pins `seed_L` (both modes), `seed_S` and `seed_M` of the
consensus programs as constants, so that any change of the leaf program, the guest, the rows or a
count shows as a changed key in review; (iv) `of_program_for_tests` behind `cfg(test)` or a feature.

**R-2 (NOTE).** `src/bundle2.rs:169-186`. `Programs::sub`, `merge`, `leaf_row`, `node_row` are public
fields and `standing` is private: `let mut p = Programs::build(..)?; p.sub = edited;` keeps
`Standing::Consensus`. Fix: private fields with accessors.

**R-3 (NOTE).** `src/bundle.rs:446`. The earlier bundle layer's `verify` is public, takes any row and
unmasked leaves, and its documentation speaks of consensus. Since row 7 was taken off the consensus
list for being unmasked, that module should say it is not a consensus path (as
`build_unmasked_for_tests` does) or be gated.

**R-4 (NOTE, the counts' certification).** The rule of row 8 is recomputed by no Rust test (the unit
test at `params.rs:531` covers rows 7 and 9); it is held by `cert.py`, run by hand, whose committed
output does not name the table it read. Fix: the output file records the SHA-256 of `params.rs` (or
of the four tables), and a test asserts it; or `cert.py` runs in the suite's queue.

**R-5 (NOTE).** `the_consensus_programs_take_no_unmasked_row_7_leaf` was read in the builder's
description only (10.00000 task B), not in source, and not run.

## 5. The earlier report's m-4, n-2, n-3

- **m-4.** Restated correctly as to trailing data. One clause missing after the flag walk: W-a.
- **n-2 (open).** `ZK_STOP` and `SB_TRACE` are 0 in `placeholder_map_for` unconditionally
  (`placeholders.rs:749`, `:310`; no environment variable reads them; printed as 0 in section 6), and
  `bundle2::placeholders` does not override them. There is still no test that the consensus programs'
  map has both at 0 and that a nonzero value is another key. The guest has 18 lines that mention
  them. Stays a NOTE.
- **n-3 (open, and stale).** `tests/guest_masked.rs:1088`: "the last oracle's domain is `2^12` points
  for 180 queries". The count is 186 since the every-`t` tables, and on the suite's proof both oracle
  2 (169 queries, 168 positions) and the last (186, 181) have coinciding positions; the test takes
  the first such oracle, which is oracle 2.

## 6. Tests run by the reviewer

Worktree at `b8b85af`, test file a copy of `tests/guest_masked.rs` with Appendix A appended;
`cargo test -j 3 --release --test referee_pstar --no-run`, then one test at a time,
`--test-threads=1`, `nice -n 10`, `RAYON_NUM_THREADS=3`. 1-minute load 10 to 20: **no timing is
reported.** Peak memory footprint 0.57 to 0.58 GB a test (`/usr/bin/time -l`).

| Test | What | Result |
|---|---|---|
| P1 | the placeholder map at the wallet's shape | `ZK_STOP` 0, `SB_TRACE` 0; `WI_CUT` over the 48 candidates: 32 at 6, 16 at 0; `WI_N` of every last level 9; the wallet candidate's counts 234, 166, 169, 186 |
| P1 | the honest proof, the consensus guest | accepted, 742,312 cycles (the builder's figure); last oracle 186 queries, 181 positions, 63 classes of 64 |
| P1 | controls a, b, c, d of section 3.5 | each refuses the honest proof at guest line 5323, the last rows' check |
| P2 | last oracle: query 185 (position 126) flagged "as query 13 before" (position 107, the same class 1), its row and path left out | the guest refuses at guest line 5372, the position equality; the guest without that line **accepts** (741,931 cycles) |
| builder's `the_shared_stages_of_the_final_message_decide_and_agree_with_the_rows_alone` | | passes: 742,312 against 863,879 cycles; the four controls refuse at the last rows' check |
| builder's `walk_advice_at_every_oracle` | | passes: as in W-7 above |

## 7. Not checked

- The zkDSL compiler and the VM: `if x != 0` on a cell, `log(x) < B`, division by a cell, write-once
  memory, `mul_range`, `HeapBuf` sizes. Taken from the comments, the errors observed and the tests.
- The native test `whir.rs:438` and every suite other than the two tests named: not run. No tree, no
  sub-bundle, no merge was proved or verified. `bundle2_masked`, `bundle2`, `bundle2_mode1`: not run.
- Candidates other than the wallet's (`2^22`, rate 1/4) in any run of the reviewer's.
- `cert.py`, `shapes.py`, the calculator and the need `129 + log2 N + log2(1 + k_q)`: not re-run, not
  re-derived; the 0.2-bit reserve's adequacy is the calculator's referee's subject
  (`docs/rev10-referee.md`). Whether row 8's rounds outside the opening are those of the wallet
  statement at every shape (`wi.A_WALLET_ZK` in `cert.py`) was not examined.
- `guests/bundle_merge_e2.py` and `bundle_common_e2.py` beyond the seed and statement lines;
  `Tree::check`, the proof-count recurrence, PC-1 and PC-2.
- Theorem D itself, the soundness of W-I, of the masked reductions and of the gadget; Sharp and
  Grubbs, ePrint 2026/2615 (not read).
- The parts of the guest outside `j_wi.py` were not re-read except the functions listed in section 1;
  `git diff 4862878 b8b85af` shows no change to them (`guests/e2`: `j_wi.py` and `assemble.py` only).
- Finding R-1's failing input was not executed.

## Appendix A. The reviewer's tests (source; not merged)

Appended to a copy of `tests/guest_masked.rs` at `b8b85af` (it uses that file's `program`,
`program_src`, `run_as`, `run_edited`, `run_counting`, `masked`, `site`, `def_at`, `line_of`,
`outcome`, `Streams`, `KBC`, `WALLET_KBC`, `WALK_POSITION`, `LAST_ROWS`).

```rust
/// P1: controls of the shared stages the builder's four do not have. Each is one part of the sharing wrong; the
/// honest proof must be refused (by the last rows' check).
#[test]
fn referee_p1_more_controls_of_the_shared_stages() {
    KBC.with(|k| k.set(Some(WALLET_KBC)));
    let m = masked();
    let row = &verifier::params::CAT1_TREE_LEAF_SALTED;
    let map = aggregation_e2::parts::placeholder_map_for(row, kbc());
    for name in ["ZK_STOP_PLACEHOLDER", "SB_TRACE_PLACEHOLDER", "WI_CUT_PLACEHOLDER", "WI_STAR_PLACEHOLDER", "WI_LF_PLACEHOLDER", "LIG_QUERIES_PLACEHOLDER", "LIG_TREE_DEPTH_PLACEHOLDER", "LIG_CAP_DEPTH_PLACEHOLDER", "WI_N_PLACEHOLDER"] {
        eprintln!("P1 map {name} = {}", map.get(name).map_or("<none>".to_string(), |v| v.chars().take(400).collect()));
    }
    let drawn: Vec<Vec<u64>> = m.proof.merkle_openings.iter().map(|phase| phase.iter().map(|o| o.leaf_index).collect()).collect();
    let last = drawn.len() - 1;
    let classes: std::collections::BTreeSet<u64> = drawn[last].iter().map(|p| p >> 6).collect();
    let distinct = verifier_e2::spbcs::distinct(&drawn[last]).len();
    eprintln!("P1 last oracle: {} queries, {distinct} distinct positions, {} classes hit of 64, max position {}", drawn[last].len(), classes.len(), drawn[last].iter().max().unwrap());
    let honest = run_as(&program(row, &[]), row, &m.key, &m.pi, &m.proof, &[], &m.summary).expect("honest");
    eprintln!("P1 honest: {honest} cycles");
    let controls: [(&str, &str, &str); 4] = [
        ("a: a stage's class point one bit low", "    chain = bits * COORD_BASIS[v + 1] + COORD_BASIS[depth]\n", "    chain = bits * COORD_BASIS[v] + COORD_BASIS[depth]\n"),
        ("b: the top stage's live count 1", "            live = const(n - half)\n", "            live = const(1)\n"),
        ("c: the stages stop one variable early", "    for i in unroll(0, nbits - cut):\n", "    for i in unroll(0, nbits - cut - 1):\n"),
        ("d: the top stage reads a parent entry past P*", "        src = wi_star_stage(src, tabs, v, depth, half, live, n_par, 1 // (i + 1))\n", "        src = wi_star_stage(src, tabs, v, depth, half, live, n_par, 0)\n"),
    ];
    for (name, from, to) in controls {
        let control = program_src(row, &[(from, to)]);
        let got = run_counting(&control, row, &m.key, &m.pi, &m.proof, &[], &m.summary, &|_| ());
        match &got {
            Ok((cycles, unconstrained)) => eprintln!("P1 {name}: RAN TO THE END ({cycles} cycles), {unconstrained} cells read before written"),
            Err(e) => eprintln!("P1 {name}: refused at line {} in `{}` (last rows' check at {}): {}", site(e), def_at(site(e)), line_of(LAST_ROWS), e.chars().take(120).collect::<String>()),
        }
    }
    KBC.with(|k| k.set(None));
}

/// P2: the flag walk against the sharing. At the last oracle, a query flagged "as query j before" where j is at
/// ANOTHER position of the SAME class (the same shared-stage entry), its own row left out: refused at the position
/// equality (whole positions are compared, not classes); the guest without the equality accepts.
#[test]
fn referee_p2_a_duplicate_flag_within_one_class() {
    use aggregation_e2::parts::count;
    KBC.with(|k| k.set(Some(WALLET_KBC)));
    let m = masked();
    let row = &verifier::params::CAT1_TREE_LEAF_SALTED;
    let whole = program(row, &[]);
    let no_position = program_src(row, &[(WALK_POSITION, "")]);
    let drawn: Vec<Vec<u64>> = m.proof.merkle_openings.iter().map(|phase| phase.iter().map(|o| o.leaf_index).collect()).collect();
    let distinct: Vec<usize> = drawn.iter().map(|d| verifier_e2::spbcs::distinct(d).len()).collect();
    let level = drawn.len() - 1;
    let n = drawn[level].len();
    let is_first = |q: usize| !drawn[level][..q].contains(&drawn[level][q]);
    let (k, j) = (0..n)
        .rev()
        .filter(|&k| is_first(k))
        .find_map(|k| (0..k).find(|&j| is_first(j) && drawn[level][j] != drawn[level][k] && drawn[level][j] >> 6 == drawn[level][k] >> 6).map(|j| (k, j)))
        .expect("two first queries of one class");
    eprintln!("P2 last oracle: query {k} at {} and query {j} at {}: class {}", drawn[level][k], drawn[level][j], drawn[level][k] >> 6);
    let row_at = distinct[..level].iter().sum::<usize>() + (0..k).filter(|&q| is_first(q)).count();
    let unopened = move |s: &mut Streams| {
        s.iter_mut().find(|(n, _)| n == "wi_first").unwrap().1[level][k] = count(j);
        for name in ["merkle_leaf_rows", "merkle_children"] {
            s.iter_mut().find(|(n, _)| n == name).unwrap().1.remove(row_at);
        }
    };
    let a = run_edited(&whole, row, &m.key, &m.pi, &m.proof, &[], &m.summary, &unopened);
    let b = run_edited(&no_position, row, &m.key, &m.pi, &m.proof, &[], &m.summary, &unopened);
    eprintln!("P2 the guest: {}", outcome(&a));
    eprintln!("P2 the guest without the position equality: {}", outcome(&b));
    let err = a.expect_err("same-class duplicate flag");
    assert_eq!(site(&err), line_of(WALK_POSITION));
    assert!(b.is_ok());
    KBC.with(|k| k.set(None));
}
```
