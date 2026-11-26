# Referee report: the in-circuit verifier of masked row-8 leaf proofs (system A)

Part of Yugen. 2026-11-19. Independent, adversarial review of the guest that verifies a
masked (zero-knowledge) row-8 leaf proof inside a sub-bundle, in `yugen-proof-a` at commit `4862878`
(read only): `guests/e2/j_wi.py`, `h_sub.py`, `g_ring.py`, `c_open.py`, `a_fs.py`, `i_zk.py` and the
assembled `vendor/leanMultisig/guests/lean_ethereum_e2.py`; the native verifier it must match
(`vendor/leanMultisig/crates/verifier/src/{lib,wi,zk,transcript,spbcs,whir,bus}.rs`); the constants
(`crates/aggregation/src/placeholders.rs`, `child.rs`); `src/bundle2.rs`; `tests/guest_masked.rs`,
`tests/bundle2_masked.rs`; `docs/recursion.md` 10.000 and 9.11, `docs/zk-merge-notes.md` 3 and 4; and
the transcript specification `docs/qrom-compilation.md` section 2 of this repository. The reviewer
wrote none of the reviewed code or documents. Nothing but this file was written; the reviewer's
tests ran in a temporary worktree that is removed (their source is Appendix A).

Provenance. Every finding here is **Original (the Ycash developers, 2026)**, first recorded in this
file, unreviewed. The transcript is the spBCS form of Sharp and Grubbs, *Faster and Smaller
Anonymous Credentials from Standardized Signatures*, ePrint 2026/2615, Protocol 6.5 and Section I.1,
**as `qrom-compilation.md` section 2 instantiates and cites it**: the paper itself was not read for
this report, and nothing here is attributed to it beyond what that document states. The hiding
opening W-I is the construction of `docs/zk-hiding-commitment.md` 6.1 and 6.2a as
`verifier/src/wi.rs` implements it; this report checks that the guest equals that native verifier,
not that the construction is sound.

## 0. Verdict

**PASS WITH CONDITIONS.** No soundness defect was found in the guest at `4862878`: every check the
native verifier makes on a masked leaf that I traced is made in the guest on transcript-bound
values, every prover message is absorbed before the challenges that depend on it, and the advice
of the distinct-position walk cannot make a drawn query go unchecked. The conditions are about
what the test suite does not show and about the planned rewrite of the walk.

| Class | Count | Findings |
|---|---|---|
| BLOCKER (soundness) | 0 | none found |
| MAJOR | 2 | M-1: the last rows' check has no test that only it refuses; M-2: the position equality is untested where it alone decides (the last oracle) |
| MINOR | 5 | m-1 build-time guards (the `MUL2` premise, the masking pairing, the 512 bound); m-2 rates 1/2, 1/8, 1/16 not in the suite; m-3 refusal tests do not record the refusing check; m-4 "accepts exactly" is false for the wire (trailing data); m-5 the tree-level refusals are for one leaf only |
| NOTE | 6 | n-1 to n-6 (section 9) |

Conditions: **C-1** add the isolating test of M-1 (a prover control, 10 lines, given in section 8.2;
run here: refused by the guest at the check, accepted by a guest without it). **C-2** add the walk's
advice tests at every oracle, the last included (section 8.2, R2; run here). **C-3** the flag walk
that replaces the strict-increase walk meets conditions W-1 to W-7 of section 4.3 and is reviewed
again before a consensus program is built from it. **C-4** the claim is restated as in m-4.
**C-5** the guards of m-1.

Tests run by the reviewer (section 8.2): five tests, 1 passed each (all assertions held), at the
wallet's shape (`2^18` instructions, stack `2^22`); peak footprint 0.57 to 1.2 GB; no timing is
reported (1-minute load 8 to 11).

## 1. Method

Read: the files above, whole for `j_wi.py`, `h_sub.py`, `a_fs.py`, `c_open.py`, `wi.rs`, `spbcs.rs`,
`transcript.rs`, the `ZK` parts of `g_ring.py`, `lib.rs` (`walk`, `verify_stacked_opening`),
`zk.rs` (`flags`, `unblinded_table`, `admitted_stack_log`, `BlindBlock`, `Region`,
`verify_gadget`), `placeholders.rs` (`zk_placeholders`, `opening_placeholders`), `child.rs`
(`gen_verify_for`, `merkle_hints`), `tests/guest_masked.rs`, `tests/bundle2_masked.rs`; sampled:
`d_bus.py`, `e_tables.py`, `f_keccak.py`, `i_zk.py` (the gadget's weights), `bus.rs`, `keccak.rs`,
`bundle2.rs`, `bundle_sub_e2.py`.

Argument used throughout. A discrepancy between guest and native verifier is one of two kinds.
(a) A formula that differs (a weight, an order, a constant): the honest proof then fails in the
guest with overwhelming probability over the challenges, so the suite's acceptance of real proofs
at a shape is evidence for every formula on that shape. (b) A check that is missing, or made on a
value the prover's advice supplies: no honest run shows it. The review therefore looked for (b):
every `hint_*` call (27 in the parts; the masked row adds `zk_tau_max`, `wi_sorted`, `wi_slot`, the
digits of `wi_below` and the bits of `zk_round_up`), every `assert`, and every place where the
native verifier has a `require`.

The guest's memory is write-once: a second write to a cell is an equality constraint, and a cell
never written holds whatever the prover chooses. Both facts are used below.

## 2. Every native check on a masked leaf, and where the guest makes it

Native lines are of `vendor/leanMultisig/crates/verifier/src/`; guest lines are of the parts in
`guests/e2/` at `4862878`.

| # | Native check | Guest | Same values? |
|---|---|---|---|
| 1 | proof salt is 64 bytes (`transcript.rs:200`) | four cells hinted, `h_sub.py:19-20`; in the header and every stream | yes (shape by construction) |
| 2 | announced values are words (`lib.rs:369-373`) | `h_sub.py:44` (upper cell zero), `g_power_of_word` (52, 55), table rows certified in `verify_tables` | yes |
| 3 | rate in 1..4 (`lib.rs:377`) | `h_sub.py:52-53` | yes |
| 4 | no announced `MUL2` rows when the program has no `MUL2` (`lib.rs:392-395`) | `h_sub.py:97`, unconditional | yes for a program without `MUL2`; see m-1 |
| 5 | layout, mask region, admitted stack size, size window (`lib.rs:405-419`, `zk.rs:93`, `zk.rs:682`) | `h_sub.py:122-128` (`zk_region`, `zk_admit`), `i_zk.py:34-56`; no schedule: `ZK_ADMIT` out of range and `WI_OK` 0 (`j_wi.py:492-495`) | yes; `zk_tau_max` is advice pinned as the largest tau (`h_sub.py:89-94`) and equal to the table sumcheck's (`h_sub.py:179`) |
| 6 | a root's halves have zero upper parts (`lib.rs:166`) | `h_sub.py:106,108`; `j_wi.py:537-538` | yes; tested here (R3) |
| 7 | bus: count root and shared root nonzero (`bus.rs:246-248`) | `d_bus.py:207-210` | yes (suite) |
| 8 | masked bus layers, table sumcheck, Keccak layers and openings: no terminal equality, a linear claim each (`bus.rs:96-107`, `bus.rs:489`, `keccak.rs`) | values `claim + rho terminal` kept for the gadget (`e_tables.py:626-637`, `f_keccak.py:694-711`, `789-797`) | sampled only (section 10) |
| 9 | Keccak product round's check | `f_keccak.py:275-285` | suite (`step_07_08`) |
| 10 | gadget: claims lie on the masks (`zk.rs:757`) | the walk ends at the masks' end, `h_sub.py:227` | yes |
| 11 | gadget: `<u, w> = beta + c value` (`zk.rs:779`) | `h_sub.py:224-229` | yes; the weights are formula (a) |
| 12 | gadget: `norm mle(u, z) = B(z) + c A(z)` (`zk.rs:780`) | `h_sub.py:219-222` | yes |
| 13 | batch: powers of one `lambda`, the blocks' cells (`lib.rs:198-209`) | `h_sub.py:264-289`, `g_ring.py:160-238`, `j_wi.py:29-95`; every block's gap zero by assertion (`placeholders.rs`, "a blind block has a gap") | yes |
| 14 | W-I level: `G`, `rho`, the fold rounds (`wi.rs:237-250`) | `wi_head` (`j_wi.py:101-112`), `opening_round` (`c_open.py:68-98`) | yes |
| 15 | W-I: next root, positions, `lambda`; rows authenticated to the level's root; `claim += lambda^(k+1) fold(row_k)` over the drawn queries (`wi.rs:265-274`, `transcript.rs:321-375`) | `j_wi.py:534-546`, `wi_queries`, `wi_query`, `walk_path`, `verify_merkle_cap`; root equality by the write-once cells `level_roots` (`j_wi.py:542-543`, `557-558`) | yes |
| 16 | W-I base case: `mu`, `c`, `P*`, positions; **`P*(x) = column + c fold(row)` at every drawn row** (`wi.rs:284-309`) | `j_wi.py:553-556`; the check `j_wi.py:211-214` | yes; **untested in isolation: M-1** |
| 17 | tail sumcheck, terminal `W'(tail) mle(P*, tail) = claim` (`wi.rs:315-349`) | `j_wi.py:564-646`, `g_ring.py:237-243` | yes |
| 18 | one opening a distinct position; a second, different opening of a position refused (`transcript.rs:362-369`) | rows are advice; one row a distinct position by `wi_queries` | the guest's form; section 4 |
| 19 | stream and openings wholly consumed (`transcript.rs:403-417`) | **not made** (the stream is advice of fixed capacity) | m-4: no soundness content |
| 20 | no grind under spBCS (`transcript.rs:300-303`) | none drawn | yes |

No native check on a masked leaf was found missing or weaker in the guest but 19.

## 3. Fiat-Shamir

Order of absorption in the guest against the native walk, masked parts (the unmasked parts are the
row-7 guest's):

| Message | Absorbed before | Guest |
|---|---|---|
| header: tag, label, proof salt, `be32(92)`, row, bound IV (the seed), public input | everything | `h_sub.py:23-26`; `SB_ROW` is the row's number, a constant of the program; the seed and `pi` are the caller's |
| announcement, commitment root | the out-of-domain point | `h_sub.py:39-51`, `105-113`, key at 136 |
| slices (the last of 64) | `theta` | `h_sub.py:199-206` |
| `beta` | `c` | `h_sub.py:208-211` |
| the column `u` | `z` | `zk_column`, `i_zk.py:455-486` |
| `A(z)`, `B(z)` | the map challenges and the batching `lambda` (one message) | `h_sub.py:216-217`, `233-248` |
| level `G` | `rho` | `wi_head` |
| fold table (4 scalars) | `alpha`, `beta` | `opening_round` |
| next root | the level's positions and `lambda` (one message) | `opening_message(.., 2, 1)`, `level_positions(.., 1)` |
| `mu` | `c` | `wi_head` (second call) |
| `P*` (`lf` scalars) | the last level's positions | `wi_star`, `level_positions(.., 0)` |
| tail round (2 scalars) | its challenge | `opening_tail_round` |

Block boundaries (`sb_key`'s item count) were checked by hand at `wi_head` (2), `opening_round` (4
then 5), `opening_message` with a root (2), `wi_star` (4, then 8 a block, then `5 + n % 4`),
`opening_tail_round` (3), the gadget (65, 2, the column, 3). The suite's stops compare the guest's
stream position and write-back with the native walk's at every mark, which confirms them at the
tested shapes.

No challenge is derivable from advice. The proof salt is advice by design (it is in the header and
in every stream). A position's windows are advice, range-checked and rebuilt to the squeezed word
(`decode_query_windows`, `assert reconstructed == squeezed_word`); `g^position` for the walk is
rebuilt from the same windows (`wi_position_power`). A root's upper cells are not absorbed (the
item is the digest's two cells) and are asserted zero.

## 4. One path a distinct position (step 3)

### 4.1 The walk as built is sound

`wi_queries` (`j_wi.py:258-317`). Advice: `srt = (g^m, tau_0 .. tau_(m-1))` and `slots = (sigma_k)`.

- `1 <= m <= 512` (`:276`); each `tau_j` in `[0, n - 1]` by the two-sided check (`:281-282`), so
  `positions[tau_j]` and `query_win_ptrs[tau_j]` are cells `level_positions` wrote from the stream.
  An entry's position and its windows are the same drawn query's.
- `g^(p_j - p_(j-1) - 1)` is a power below `16^ceil(depth / 4)` (`:287`, `wi_below`), so positions
  increase strictly (the order of `g` exceeds `2^(depth + 4)`); hence `m <= n`, the loop never reads
  past `srt`, and `recs` is written at entries 1 to `m` only by the loop.
- Entry `j`'s row is hashed, walked by the entry's own windows into the level's cap, and folded
  (`:288`); the record is `(position, g^position, fold)`.
- Every drawn `k`: `sigma_k` in `[0, m - 1]` (`:301-302`), and **`recs[sigma_k].position ==
  positions[k]`** (`:304`). The record read was written by the first loop. So every drawn position
  has an authenticated row, and the fold a query contributes is that row's.
- The sum runs over the drawn order with `lambda^(k + 1)`, duplicates included, as the native
  verifier's (`wi.rs:272-274`); `wi_level_residual` weights the same list.

Attacks tried, each at every oracle of a real proof (R2, section 8.2): two entries swapped; a query
sent to another entry; a query sent one past the last entry and to entry 511; an empty list; an
entry naming query `n` and query 511; **the lowest position not opened at all** (its entry, row and
path left out, its queries sent to the next entry). All refused inside the guest's checks.

### 4.2 Which assertion carries the soundness

The strict increase carries none (agreeing with `docs/recursion.md` 10.000: a position opened twice
is two openings of one authenticated leaf). The position equality `:304` carries all of it, and at
the last oracle it is alone: there a row's check is self-contained and nothing is summed, so
without `:304` a prover opens any `m' < m` positions and sends every query to one of them. Shown
(R2, f): a guest compiled without `:304` **accepts** the proof with the lowest position of the last
oracle unopened; at the other oracles the same guest still refuses, at the terminal, because the
wrong fold enters the claim. This is finding M-2: the suite's test of `:304`
(`step_3_one_path_a_distinct_position`, "a drawn query sent to another position's entry") runs at
the oracle where two positions coincide, which on the suite's proof is oracle 2 of 4 (164 queries,
163 positions; the last oracle's 180 are distinct), where the terminal refuses the edit whether or
not `:304` is there (R5, last line).

### 4.3 The planned drawn-order walk: what it must enforce

For a level with drawn queries `k = 0 .. n - 1` (position `positions[k]`, windows
`query_win_ptrs[k]`, both from the stream), advice a flag `f_k` and, where `f_k` says "as before",
an index `j_k`.

- **W-1.** `f_k` is constrained to two values (a range-checked power of `g` dispatched by `match`,
  or `f (f + 1) = 0`).
- **W-2.** First: the row is hinted, hashed with the leaf tag and salt, walked with **the query's
  own windows** into the level's cap, the cap checked to the level's root, the root the
  transcript's (the write-once equality as today). The record `(positions[k], fold_k)` is written at
  slot `k`; at the last oracle the check `P*(x) = column + c fold` is made here.
- **W-3.** As before: `j_k` is **strictly below `k`**, two-sided, in the exponent (`g^(k - 1) / g^(j_k)`
  a small power, with the loop's own `g^k`; the bound is against `k`, not `n`). Equivalent: `j_k`
  names a query whose flag is "first". Without this the walk is unsound: two queries that name
  each other, both "as before", copy each other's fold cell, both cells are otherwise unwritten,
  and write-once memory accepts any common value, so the prover chooses the fold (below the last
  oracle it forges the level's sum; at the last oracle no row is checked for the pair).
- **W-4.** As before: `positions[j_k] == positions[k]` on the stream's position cells of the same
  level (the whole position; the field encoding is injective on `depth` bits), and the record at
  slot `k` is a copy of slot `j_k`'s. Records are written at every slot, so a chain of "as before"
  ends at a first by induction on `k`.
- **W-5.** The sum stays over all drawn queries in drawn order with `lambda^(k + 1)`, and
  `wi_level_residual` is unchanged.
- **W-6.** No cell of a record is read unless an earlier iteration wrote it (follows from W-3;
  the suite's `unconstrained_reads.is_empty()` shows it for honest advice only, so the argument is
  to be written at the function).
- **W-7.** Tests, at every oracle and at the last in particular: a later query at an earlier
  one's position flagged "as before" naming a query at another position (refused by W-4); naming
  itself and naming a later query (W-3); the first query flagged "as before"; a guest compiled
  without the position equality accepts the edit at the last oracle (the control that the test
  reaches the assertion).

What the rewrite may drop: the order, `g^position`, `wi_below`, `wi_sorted`. A prover may then
open one position twice (two "first" flags); that is sound and concerns the wire format only
(`qrom-compilation.md` 2.4 and A-4: one salted leaf a distinct position), which the guest does not
see. The same conditions apply to the walk planned for `open_stacked` (rows 7 and 9).

## 5. The masks' claims and the hiding opening (steps 10 and 11)

- **Bound to the committed roots.** The mask column `A`, the gadget column `B` and the slice block
  are cells of the stack, committed in the one root read before every challenge
  (`h_sub.py:105-113`); their claims are weights in the one batch opened against that root. The
  last oracle's mask column is one more element of the same leaf as the row's lanes
  (`j_wi.py:195`, `LIG_LEAF_CELLS` includes it), hashed with them and with the salt into the root
  the transcript absorbed before the previous level's positions. A changed column word is refused
  at the path (suite), a wrong column value at the row's check (R5).
- **The same positions.** The lanes and the column are one row at one position; the fold point is
  `positions[k] + COORD_BASIS[depth]`, the native `K(2^log_domain + q)`.
- **Batching randomness after the commitments.** `theta` after the last slice; `c` after `beta`;
  `z` after `u`; the batching `lambda` (with the map challenges) after `A(z)` and `B(z)`; a level's
  `rho` after `G`; a level's `lambda` after the next root, in the positions' message; `c` after
  `mu`; the last positions after `P*`. Section 3.
- **The blocks' powers.** Framework block at power 1, the table block at the first table
  evaluation's power, the output word's at its own, then `A(z)`, `B(z)`, the out-of-domain sample
  (`g_ring.py:160-232` against `lib.rs:483-553`, `614-619`). These are formulas of kind (a).
- **The terminal.** `W' = inner + base * batch` with `base` the product of every `rho` and the zero
  extensions; matches `terminal_weight` (`wi.rs:155-212`) term by term.

**M-1.** The row check of the last oracle is the only thing that ties `P*` to the committed oracle:
the tail sumcheck and the terminal are statements about the public `P*` and `W'` alone
(`wi.rs:19-21`). A prover that sends `P* + delta` with `<delta, W'> = 0` passes both (`W'` on the cube
is fixed before `P*` is sent). The suite has no proof that this check alone refuses: with the two
assertions `j_wi.py:213-214` deleted, every refusal of the suite at the last oracle still holds
(R4: 0 of 13 changes accepted; a changed `mu` or `P*` moves the positions and is refused at the
paths, a changed row word at its leaf hash, a changed tail scalar at the terminal). With the
prover control of section 8.2 the forged proof is refused natively with `WhirFinalQuery`, refused
by the guest at the assertion (assembled guest line 5238), and **accepted by the guest without the
assertion** (R5). The check is present and right; the suite does not hold it in place.

## 6. `MUL2`, and the removal of the row-8 refusal

- The guest refuses announced `MUL2` rows unconditionally (`h_sub.py:97`); the native verifier
  refuses them when the program has no `MUL2` instruction (`lib.rs:392-395`). The guest's mask
  layout is compiled for that case (`placeholders.rs`, `zk_placeholders`: `committed` leaves the
  `MUL2` columns out). For a leaf program **with** a `MUL2` instruction the guest and the native
  verifier are different protocols: the native verifier accepts proofs the guest refuses, and
  nothing the guest accepts is unsound (no soundness argument rests on a blinder cell).
  `Programs::build` does not check the premise (m-1). The two wallet leaf programs have no `MUL2`
  (suite).
- `bundle2::placeholders` now takes row 8 and `CONSENSUS_LEAF_ROWS` lists rows 7 and 8. What a
  consensus program now accepts: a row-8 proof of whatever program the leaf seed names, the seed
  being in the statement. I found nothing accepted that should not be, with three remarks.
  (i) `ZK_STOP` and `SB_TRACE` are 0 in `placeholder_map_for` and no consensus path edits them; a
  nonzero `ZK_STOP` is a guest that returns before the opening (n-2). (ii) `verify` pins
  `params.wallet` and `auth_mode` of the leaf program it is handed, not `params.masking`: the
  unmasked wallet program under row 8 builds, proves and verifies as "consensus" if a node hands
  it in. Sound, not private (m-1). (iii) The merge program's key does not depend on the leaf row
  (`docs/recursion.md` 10.000, the keys table), so the leaf row is bound only through `seed_S` and
  `seed_L` in the statement, which `verify` recomputes from the programs it is handed: which of
  rows 7 and 8 is consensus is the node's choice of `Programs` (n-1).

## 7. Mode 0, mode 1 and the program keys

The sub-bundle program takes the leaf seed (the leaf program's IV bound to the leaf row) as
advice, uses it as the bound IV of every leaf's transcript (`h_sub.py:25`), and publishes it in its
statement (`bundle_sub_e2.py:134`) with the batched claim on the leaf bytecode, which the verifier
evaluates on the leaf program (`bundle2.rs`, `Claims::recompute`). The mode is advice constrained
to a bit, is the mode byte of every leaf's public input and is in `D`
(`bundle_sub_e2.py:104-106`, `82`). `verify` recomputes the three seeds from the programs and the
leaf program it is handed and refuses a leaf program of another mode. So the verified leaf's
program, row and mode are bound in what the parent proves; row 8 changes nothing in this path.
Checked by reading only; `tests/bundle2_mode1.rs` was not read or run (section 10).

## 8. Tests

### 8.1 What the suite refuses, and what it does not

Refused in `tests/guest_masked.rs` (13 tests) and `tests/bundle2_masked.rs` (2): a guest over a
duplex row; salt and row words of a salted leaf; the layout off by one; a zero bus root; a changed
Keccak product coefficient; 22 changed scalars before the ring switch (stop build); some 170
changed stream scalars and 32 changed row words on the whole guest; announced `MUL2` rows (stop
build); the tail's last scalar on a mode-1 leaf; five edits of the walk's advice at one oracle; in
the sub-bundle program a changed tail scalar and a changed mask-column word; a tree verified for
another leaf or another tree.

Not tested (before this report):

1. The last rows' check in isolation (M-1).
2. The position equality at the last oracle, and the walk's advice at the oracles without a
   coincidence (M-2).
3. Rates 1/2, 1/8, 1/16: every proof of both suites is at rate 1/4, and the hiding opening has one
   arm a size and a rate (m-2).
4. Prover-made bad proofs (self-consistent transcript and openings): the suite changes one scalar
   or word of an honest proof, and nearly every such change is refused at a Merkle path because
   the positions move. The fork's own controls (`stable_pcs_e2::wi::Controls`: `linear_domain`,
   `every_lane_aux`, `narrow_alignment`) are not run through the guest.
5. A root's upper cells; the proof salt; the seed; the public input (on the masked guest).
6. The cap's advice (`merkle_cap_active`, `merkle_caps`).
7. A row-7 proof in the row-8 sub-bundle program and the reverse; a mode-0 masked leaf under the
   mode-1 programs (row 8).
8. A sub-bundle of two or more masked leaves in a test (it is in a benchmark), and the refusal of
   a bad second leaf (m-5).
9. Shapes: stack `2^22` and `2^24` at rate 1/4 (mode 0), `2^21` (mode 1); no other admitted size.
10. The cause of a refusal: the acceptance test asserts `is_err()` only (m-3).

### 8.2 Tests written and run by the reviewer

In a worktree at `4862878`, appended to a copy of `tests/guest_masked.rs` (Appendix A); built with
`cargo test -j 3 --release --test referee_masked --no-run`, run one at a time with
`--test-threads=1`, `nice -n 10`. One change outside the test file, in the reviewer's worktree
only: a prover control in `vendor/leanMultisig/crates/stable_prover/pcs/src/wi.rs` (feature
`wi-controls`, tests only):

```rust
// in `Controls`:   pub shift_final_message: bool,
// in `open`, the base case, after `let mut star = ...` and before `ps.add_scalars(&star)`:
if controls().shift_final_message {
    let nz: Vec<usize> = (0..level.lf).filter(|&i| w[i] != F128::ZERO).take(2).collect();
    let (i, j) = (nz[0], nz[1]);
    let (wi, wj) = (w[i], w[j]);
    star[i] += wj;   // <delta, w> = w_j w_i + w_i w_j = 0 in characteristic 2
    star[j] += wi;
}
```

Results (all at the wallet's shape, leaf program `2^18`, stack `2^22`, row 8; "line" is of the
assembled guest):

| Test | What | Result |
|---|---|---|
| R1 | a masked leaf proved at rates 1/2, 1/8, 1/16 (openings 375/169/175/220, 185/157/158/166, 168/155/156/159 rows), verified natively, run whole in the guest; then the tail's last scalar changed | accepted at each rate (1,131,755, 871,056, 849,930 cycles); the change refused at each |
| R2 | the walk's advice, at each of the 4 oracles: a, b, c, c2, d, e, e2, f of section 4.1 (32 runs) | all 32 refused inside the guest: b and f at the position equality (line 5329); c, c2, d, e, e2 at a range check; a at a digest equality of the row's walk, **not** at the increase check (the rows' advice stays in the old order, so the swapped entry meets another position's row first; the suite's "two entries out of order" is the same edit and has the same limit) |
| R2 | f on a guest compiled without the position equality | oracles 0, 1, 2: refused at the terminal; **last oracle: accepted** (928,368 cycles) |
| R3 | the proof salt's last byte; the public input's last byte; the seed's second cell | refused |
| R3 | words 2 and 3 of each half of the commitment root and of the three later roots (16 runs) | native `AnnouncedHighLimb`; guest refused at the zero assertions (lines 5785, 5787, 5562, 5563) |
| R3 | one scalar appended to the stream | native `StreamNotConsumed`; **guest accepted** (m-4) |
| R3 | at each oracle: every cap flag cleared; the cap's node 2 changed | refused (8 runs) |
| R4 | a guest without the last rows' check (lines 5238-5239): the real proof; then `mu`, `P*` first and last, the tail's first and last scalar, and 8 row words of the last oracle changed | the real proof accepted; **all 13 changes still refused** (by the paths, the leaf hash, the terminal): none is the check's alone |
| R5 | the prover control above | native `WhirFinalQuery`; guest **refused at line 5238**; guest without the check **accepted** (925,210 cycles) |
| R5 | prover control `linear_domain` | native `WhirFinalQuery`; guest refused at line 5238; guest without the check refused at the terminal (line 4534) |
| R5 | prover control `every_lane_aux` | native `WhirTerminal`; guest refused at the terminal, with or without the check |
| R5 | no control | accepted by all three |
| R5 | the suite's slot edit at the coinciding oracle (2 of 4), guest without the position equality | refused at the terminal: the suite's test does not reach the assertion |

Peak memory footprint (`/usr/bin/time -l`): R1 1.22 GB, R2 0.58 GB, R3 0.57 GB, R4 0.58 GB,
R5 0.95 GB. Not run by the reviewer: the existing suites, any tree, any other shape.

### 8.3 Tests proposed and not written

- The flag walk's tests, W-7.
- R1 at the other shapes of the suite (`2^24`, mode 1) and one size per rate where the admitted
  size differs from the natural size.
- `narrow_alignment` through the guest; a control that commits a wrong mask column at every
  position (the dual of the control above: `P*` honest, the column shifted).
- Items 7 and 8 of section 8.1 as `bundle2_masked` tests (the two-leaf sub-bundle is 4.9 GB by
  `docs/recursion.md` 10.000: a memory-capped run).
- For m-3: every refusal test asserts the error is not the host's and records the refusing line;
  a table of "check, the test that only it refuses" kept beside the suite.

## 9. Findings

**M-1 (MAJOR, test adequacy of a soundness check).** `guests/e2/j_wi.py:213-214`. No test fails if
the last rows' check is deleted. Attack it guards: `P* + delta`, `<delta, W'> = 0` (section 5; R4, R5).
Fix: the prover control of 8.2 in `stable_prover/pcs/src/wi.rs` with a native test (expects
`WhirFinalQuery`) and a guest test (expects the refusal at the assertion, and acceptance by a guest
compiled without it); `linear_domain` through the guest as a second case.

**M-2 (MAJOR, test adequacy of a soundness check).** `guests/e2/j_wi.py:304`. At the last oracle the
position equality is the only guard against an unopened drawn position; the suite tests it at an
oracle where the terminal refuses too (section 4.2; R2, R5). Fix: R2 in the suite at every oracle,
with the control guest; carried into the flag walk as W-7.

**m-1 (MINOR).** `src/bundle2.rs:194` (`Programs::build`), `:874` (`verify`),
`aggregation/src/placeholders.rs` (`zk_placeholders`, `opening_placeholders`). (a) A leaf row with
masks is built for any leaf program; the guest assumes no `MUL2` instruction. Fix: `build` refuses
unless `zk::flags(leaf_row) == 0 || zk::unblinded_table(leaf bytecode) == Some(OP_MUL2)`. (b) `verify`
does not pin `params.masking` to the leaf row. Fix: refuse unless
`leaf.circuit.params.masking == (zk::flags(programs.leaf_row) != 0)`, or record why the pairing is
free. (c) The walk's bound 512 (`j_wi.py:276,281-282,301-302`) is "above every query count" by
comment. Fix: `assert!(cands.iter().all(|c| c.queries.iter().all(|&q| q <= 512)))` where `WI_*` are
made (largest seen: 375 at rate 1/2). A larger count would cost completeness, not soundness.

**m-2 (MINOR).** Rates 1/2, 1/8, 1/16 are in no test. Run here at one shape: pass (R1). Fix: R1 in the
suite.

**m-3 (MINOR).** `tests/guest_masked.rs:575,581,598` and elsewhere: `is_err()` without the cause.
Most refusals of the acceptance test come from paths at moved positions, and the walk's "two entries out of order" is refused at a row's digest, not at the order check (R2, a). Fix: 8.3, last item.

**m-4 (MINOR, the claim).** "The guest accepts exactly what the native verifier accepts" holds for
the proof read to its natural end, not for the wire: trailing stream scalars (R3), extra opening
phases and a second opening of one position are refused natively (`transcript.rs:403-417`,
`362-369`) and invisible to the guest, whose stream and rows are advice. No soundness content: the
parent proves that a valid proof exists, and binds no proof bytes. Fix: state the claim as "the
guest has an accepting run for (seed, public input) exactly when a proof exists that the native
verifier accepts", in `docs/recursion.md` 10.000 and `zk-merge-notes.md` 4 item 5.

**m-5 (MINOR).** `tests/bundle2_masked.rs`: the tree-level refusals are on a sub-bundle of one leaf.
Fix: 8.3.

**n-1 (NOTE, for the lead architect).** Rows 7 and 8 are both consensus leaf rows and the merge
program's key is the same for both. If consensus requires masked leaves, row 7 leaves
`CONSENSUS_LEAF_ROWS` when row 8 enters, or the leaf row becomes an argument of `verify`.

**n-2 (NOTE).** `ZK_STOP` (early returns: `h_sub.py:98,144,170,180,188,190,230,291,296`;
`j_wi.py:527,559,569`) and `SB_TRACE` are test hooks in the consensus guest's source, off by a
placeholder. Add a test that the consensus programs' placeholder map has both at 0, and that a
program with either nonzero has another key.

**n-3 (NOTE).** `tests/guest_masked.rs:694-695`: the docstring says the coinciding positions are the
last oracle's; on the suite's proof they are oracle 2's.

**n-4 (NOTE).** `inv2(lam)` (`j_wi.py:540`) has no value at `lambda = 0`; the proof is then refused
(probability `2^-256`), as in `open_stacked`.

**n-5 (NOTE, agreement).** `docs/recursion.md` 10.000's recommendation (b), the flag walk, is sound
under W-1 to W-7. The statement there that the strict-increase check "adds nothing to soundness" is
right for that check and must not be read as covering the position equality.

**n-6 (NOTE, process).** A git worktree under `yugen-proof-a/wt/` does not build as it stands: the
vendored crates resolve their workspace root to the outer `yugen-proof-a/Cargo.toml` (which
excludes its own `vendor/` only) and fail on `workspace.package.edition`; the relative
dev-dependencies `../yugen-spec`, `../yugen-falcon` also miss. Building through a symlinked path
outside the repository (with the two siblings linked beside it) works.

## 10. Not checked

- Sharp and Grubbs, ePrint 2026/2615: not read; the transcript was compared with
  `qrom-compilation.md` section 2 and with `verifier/src/spbcs.rs`.
- The soundness of W-I itself, of the masked reductions and of the gadget (`zk-hiding-commitment.md`,
  `zk-wi-soundness.md`, `zk-masked-sumcheck.md`): out of scope; the native verifier is taken as the
  reference.
- Steps 2 to 9 in the guest line by line (`d_bus.py`, `e_tables.py`, `f_keccak.py`, the gadget's
  weights in `i_zk.py:98-435`): sampled (rows 7 to 12 of section 2). They rest on argument (a) of
  section 1 and on the suite's bound-message tests. The hints they use are the row-7 guest's
  except `zk_tau_max`.
- The zkDSL compiler and the VM (write-once memory, range checks, `match`, hint semantics): taken
  from the guest's comments and the errors observed.
- `placeholders.rs` beyond the `ZK_*` and `WI_*` constants; no constant was recomputed.
- The merge program, row 9, `bundle_common_e2.py`, `tests/bundle2_mode1.rs`, `docs/recursion.md`
  9.11 beyond the keys table: section 7 is by reading `bundle_sub_e2.py` and `bundle2::verify`.
- Shapes other than stack `2^22`; the existing suites were not rerun; no tree was proved.
- Commits after `4862878` (the repository's `main` moved to `f5910dc` during the review).

## Appendix A. The reviewer's tests (source; not merged)

Appended to a copy of `tests/guest_masked.rs` at `4862878` (it uses that file's `program`,
`run_as`, `run_edited`, `masked`, `marks_of`, `Masked`, `Streams`, `KBC`, `WALLET_KBC`, `GUEST`,
`MAIN`), with the prover control of section 8.2 in the worktree's
`vendor/leanMultisig/crates/stable_prover/pcs/src/wi.rs`.

```rust
// ======================= the referee's tests (not for merging) =======================

fn program_src(row: &verifier::ParamSet, src: &[(&str, &str)]) -> isa_e2::Program {
    let map = aggregation_e2::parts::placeholder_map_for(row, kbc());
    let mut guest = GUEST.to_string();
    for (from, to) in src {
        assert_eq!(guest.matches(from).count(), 1, "the edit's text is found once: {from}");
        guest = guest.replace(from, to);
    }
    let ast = zkdsl_compiler::parse_with_replacements(&[guest.as_str(), MAIN].concat(), &map).unwrap();
    isa_e2::Program::from(zkdsl_compiler::compile_at(&ast, 0))
}

fn masked_at(rate: usize) -> Result<Masked, String> {
    masked_with(rate, stable_pcs_e2::wi::Controls::default(), true)
}

fn masked_with(rate: usize, controls: stable_pcs_e2::wi::Controls, checked: bool) -> Result<Masked, String> {
    use yugen_proof_a::masking::{self, Seeds};
    let row = &verifier::params::CAT1_TREE_LEAF_SALTED;
    let params = Params { min_log_bytecode: kbc(), ..Params::wallet_masked() };
    let leaf = build(&params, &[]);
    let key = e2::Key::new(&leaf);
    let vectors = spec_vectors::load(spec_vectors::DEFAULT_PATH);
    let v = vectors.iter().find(|v| v.name == "valid-shape-0").unwrap();
    let (public, witness) = (v.public.as_ref().unwrap(), v.witness.as_ref().unwrap());
    let mut raw = wallet_raw(&params, public, witness).unwrap();
    masking::advice(&mut raw, &Seeds { free: [3; 64], pointers: [0x56; 64] });
    let pi = wallet::public_input(&params, public);
    let options = ProveOptions { params: row, retain_codeword: false, zk_seed: Some([0xa6; 64].into()) };
    stable_pcs_e2::wi::set_controls(controls);
    let proved = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| e2::prove_raw_with(&key, &leaf, &raw, &pi, rate, &options)));
    stable_pcs_e2::wi::set_controls(stable_pcs_e2::wi::Controls::default());
    let proof = match proved {
        Ok(Ok((proof, _))) => proof,
        Ok(Err(e)) => return Err(format!("the prover refuses: {e:?}")),
        Err(_) => return Err("the prover panics".into()),
    };
    let summary = if checked {
        verifier_e2::verify_execution_with(row, key.program().bytecode(), &pi, &proof).map_err(|e| format!("native: {e:?}"))?
    } else {
        verifier_e2::replay_unchecked_with(row, key.program().bytecode(), &pi, &proof).map_err(|e| format!("replay: {e:?}"))?
    };
    let marks = marks_of(&key, &pi, &proof);
    Ok(Masked { key, pi, proof, marks, summary })
}

fn flip(proof: &e2::Proof, at: usize, word: usize, bit: u64) -> e2::Proof {
    let mut bad = proof.clone();
    let mut words = bad.stream[at].words();
    words[word] ^= bit;
    bad.stream[at] = verifier_e2::E::from_words(words);
    bad
}

/// R1: the hiding opening's arms of the other rates. Every test of the suite proves at rate 1/4.
#[test]
fn referee_r1_every_rate() {
    KBC.with(|k| k.set(Some(WALLET_KBC)));
    let row = &verifier::params::CAT1_TREE_LEAF_SALTED;
    let whole = program(row, &[]);
    for rate in [1usize, 3, 4] {
        match masked_at(rate) {
            Err(e) => eprintln!("R1 rate {rate}: no native proof ({e})"),
            Ok(m) => {
                let queries: Vec<usize> = m.proof.merkle_openings.iter().map(Vec::len).collect();
                let got = run_as(&whole, row, &m.key, &m.pi, &m.proof, &[], &m.summary);
                eprintln!("R1 rate {rate}: stack 2^{}, {} scalars, openings {queries:?}: guest {:?}", m.summary.stack_log, m.proof.stream.len(), got);
                let bad = flip(&m.proof, m.proof.stream.len() - 1, 0, 1);
                let refused = run_as(&whole, row, &m.key, &m.pi, &bad, &[], &m.summary);
                eprintln!("R1 rate {rate}: the tail's last scalar changed: {:?}", refused.as_ref().map_err(|e| e.chars().take(120).collect::<String>()));
                assert!(got.is_ok(), "rate {rate}: the native verifier accepts and the guest does not");
                assert!(refused.is_err());
            }
        }
    }
    KBC.with(|k| k.set(None));
}

/// R2: the advice of the distinct-position walk, at every oracle.
#[test]
fn referee_r2_walk_advice_every_oracle() {
    use aggregation_e2::parts::count;
    KBC.with(|k| k.set(Some(WALLET_KBC)));
    let m = masked();
    let row = &verifier::params::CAT1_TREE_LEAF_SALTED;
    let whole = program(row, &[]);
    let no_pos = program_src(row, &[("        assert rec[GEN ** 0] == positions[xi]\n", "")]);
    let drawn: Vec<Vec<u64>> = m.proof.merkle_openings.iter().map(|phase| phase.iter().map(|o| o.leaf_index).collect()).collect();
    let distinct: Vec<usize> = drawn.iter().map(|d| verifier_e2::spbcs::distinct(d).len()).collect();
    let hints = aggregation_e2::parts::gen_verify_for(row, kbc(), &m.proof, &m.summary).unwrap();
    let n_rows = hints.iter().filter(|(name, _)| *name == "merkle_leaf_rows").count();
    let n_children = hints.iter().filter(|(name, _)| *name == "merkle_children").count();
    assert_eq!(n_rows, n_children, "every oracle has a path below its cap");
    let try_on = |program: &isa_e2::Program, edit: &dyn Fn(&mut Streams)| run_edited(program, row, &m.key, &m.pi, &m.proof, &[], &m.summary, edit);
    let short = |r: &Result<usize, String>| match r {
        Ok(c) => format!("ACCEPTED ({c} cycles)"),
        Err(e) => format!("refused: {}", e.chars().take(110).collect::<String>()),
    };
    for level in 0..drawn.len() {
        let (n, mcount) = (drawn[level].len(), distinct[level]);
        let before: usize = distinct[..level].iter().sum();
        let sorted_of = move |streams: &mut Streams| -> *mut Vec<F128> { &mut streams.iter_mut().find(|(n, _)| n == "wi_sorted").unwrap().1[level] };
        let slots_of = move |streams: &mut Streams| -> *mut Vec<F128> { &mut streams.iter_mut().find(|(n, _)| n == "wi_slot").unwrap().1[level] };
        let mut cases: Vec<(&str, Box<dyn Fn(&mut Streams)>)> = Vec::new();
        cases.push(("a: two entries swapped", Box::new(move |s: &mut Streams| unsafe { (&mut *sorted_of(s)).swap(1, 2) })));
        cases.push(("b: query 0 sent to another entry", Box::new(move |s: &mut Streams| unsafe {
            let slots = &mut *slots_of(s);
            slots[0] = if slots[0] == count(0) { count(1) } else { count(0) };
        })));
        cases.push(("c: query 0 sent one past the last entry", Box::new(move |s: &mut Streams| unsafe { (&mut *slots_of(s))[0] = count(mcount) })));
        cases.push(("c2: query 0 sent to entry 511", Box::new(move |s: &mut Streams| unsafe { (&mut *slots_of(s))[0] = count(511) })));
        cases.push(("d: an empty list", Box::new(move |s: &mut Streams| unsafe { (&mut *sorted_of(s))[0] = count(0) })));
        cases.push(("e: an entry that names query n", Box::new(move |s: &mut Streams| unsafe { (&mut *sorted_of(s))[1] = count(n) })));
        cases.push(("e2: an entry that names query 511", Box::new(move |s: &mut Streams| unsafe { (&mut *sorted_of(s))[1] = count(511) })));
        // f: the lowest position is not opened at all: its entry, its row and its path are left out, and its
        // queries are sent to the next entry.
        let skip: Box<dyn Fn(&mut Streams)> = Box::new(move |s: &mut Streams| unsafe {
            let sorted = &mut *sorted_of(s);
            sorted[0] = count(mcount - 1);
            sorted.remove(1);
            sorted.push(count(0));
            let slots = &mut *slots_of(s);
            for slot in slots.iter_mut() {
                let j = (0..mcount).find(|&j| *slot == count(j)).unwrap();
                *slot = count(j.saturating_sub(1));
            }
            for name in ["merkle_leaf_rows", "merkle_children"] {
                s.iter_mut().find(|(n, _)| n == name).unwrap().1.remove(before);
            }
        });
        for (name, edit) in &cases {
            let got = try_on(&whole, edit.as_ref());
            eprintln!("R2 oracle {level} ({n} queries, {mcount} positions) {name}: {}", short(&got));
            assert!(got.is_err(), "oracle {level}, {name}");
        }
        let got = try_on(&whole, skip.as_ref());
        eprintln!("R2 oracle {level} f: the lowest position not opened: {}", short(&got));
        assert!(got.is_err(), "oracle {level}: a drawn position goes unopened");
        let got = try_on(&no_pos, skip.as_ref());
        eprintln!("R2 oracle {level} f, the guest WITHOUT the position equality: {}", short(&got));
    }
    KBC.with(|k| k.set(None));
}

/// R3: what the transcript's header binds, the roots' upper cells, the cap's advice.
#[test]
fn referee_r3_header_roots_caps() {
    KBC.with(|k| k.set(Some(WALLET_KBC)));
    let m = masked();
    let row = &verifier::params::CAT1_TREE_LEAF_SALTED;
    let whole = program(row, &[]);
    let short = |r: &Result<usize, String>| match r {
        Ok(c) => format!("ACCEPTED ({c} cycles)"),
        Err(e) => format!("refused: {}", e.chars().take(110).collect::<String>()),
    };
    // the proof salt
    let mut bad = m.proof.clone();
    bad.salt[63] ^= 1;
    let got = run_as(&whole, row, &m.key, &m.pi, &bad, &[], &m.summary);
    eprintln!("R3 the proof salt's last byte: {}", short(&got));
    assert!(got.is_err());
    // the public input
    let mut pi = m.pi;
    pi[31] ^= 1;
    let got = run_as(&whole, row, &m.key, &pi, &m.proof, &[], &m.summary);
    eprintln!("R3 the public input's last byte: {}", short(&got));
    assert!(got.is_err());
    // the seed
    let got = run_edited(&whole, row, &m.key, &m.pi, &m.proof, &[], &m.summary, &|s| {
        let env = &mut s.iter_mut().find(|(n, _)| n == "env").unwrap().1[0];
        env[1] = env[1] + F128::from(1u128 << 100);
    });
    eprintln!("R3 the seed's second cell: {}", short(&got));
    assert!(got.is_err());
    // the guest of row 7 on the row-8 proof (another SB_ROW, no masks): refused
    // a root's upper cell (words 2, 3 of the scalar): not absorbed by the transcript, refused natively
    let n_tables = verifier_e2::layout::N_TABLES;
    let mut roots = vec![("the commitment root, low half".to_string(), 2 + n_tables), ("the commitment root, high half".to_string(), 3 + n_tables)];
    for (i, &(_, at, _)) in m.marks.iter().filter(|(n, ..)| *n == "wi-root").enumerate() {
        roots.push((format!("oracle {}'s root, low half", i + 1), at));
        roots.push((format!("oracle {}'s root, high half", i + 1), at + 1));
    }
    for (name, at) in &roots {
        for word in [2usize, 3] {
            let bad = flip(&m.proof, *at, word, 1 << 7);
            let native = verifier_e2::verify_execution_with(row, m.key.program().bytecode(), &m.pi, &bad);
            let got = run_as(&whole, row, &m.key, &m.pi, &bad, &[], &m.summary);
            eprintln!("R3 {name}, word {word}: native {:?}; guest {}", native.as_ref().map(|_| ()).map_err(|e| format!("{e:?}")), short(&got));
            assert!(native.is_err() && got.is_err(), "{name}, word {word}");
        }
    }
    // trailing scalars: natively refused (StreamNotConsumed); the guest reads a stream of fixed capacity
    let mut longer = m.proof.clone();
    longer.stream.push(verifier_e2::E::from_words([7, 0, 0, 0]));
    let native = verifier_e2::verify_execution_with(row, m.key.program().bytecode(), &m.pi, &longer);
    let got = run_as(&whole, row, &m.key, &m.pi, &longer, &[], &m.summary);
    eprintln!("R3 one scalar after the proof's last: native {:?}; guest {}", native.as_ref().map(|_| ()).map_err(|e| format!("{e:?}")), short(&got));
    // the cap's advice: every active flag of the last oracle cleared; one cap digest changed
    let levels = m.proof.merkle_openings.len();
    for level in 0..levels {
        let got = run_edited(&whole, row, &m.key, &m.pi, &m.proof, &[], &m.summary, &|s| {
            let flags = &mut s.iter_mut().find(|(n, _)| n == "merkle_cap_active").unwrap().1[level];
            flags.iter_mut().for_each(|f| *f = F128::from(0u128));
        });
        eprintln!("R3 oracle {level}: every cap flag cleared: {}", short(&got));
        assert!(got.is_err());
        let got = run_edited(&whole, row, &m.key, &m.pi, &m.proof, &[], &m.summary, &|s| {
            let caps = &mut s.iter_mut().find(|(n, _)| n == "merkle_caps").unwrap().1[level];
            // node 2's digest (a child of the root): cells 4 and 5
            caps[4] = caps[4] + F128::from(1u128);
        });
        eprintln!("R3 oracle {level}: the cap's node 2 changed: {}", short(&got));
        assert!(got.is_err());
    }
    KBC.with(|k| k.set(None));
}

/// R4: the suite's refusals at the last oracle with the guest's check `P*(x) = column + c fold(row)` taken out.
#[test]
fn referee_r4_the_last_rows_check_removed() {
    KBC.with(|k| k.set(Some(WALLET_KBC)));
    let m = masked();
    let row = &verifier::params::CAT1_TREE_LEAF_SALTED;
    let without = program_src(row, &[("        assert e0 == v0\n        assert e1 == v1\n", "")]);
    let short = |r: &Result<usize, String>| match r {
        Ok(c) => format!("ACCEPTED ({c} cycles)"),
        Err(e) => format!("refused: {}", e.chars().take(110).collect::<String>()),
    };
    let got = run_as(&without, row, &m.key, &m.pi, &m.proof, &[], &m.summary);
    eprintln!("R4 the real proof: {}", short(&got));
    assert!(got.is_ok());
    let at = |name: &str| m.marks.iter().find(|(n, ..)| *n == name).unwrap().1;
    let (base_case, tail, end) = (at("wi-base-case"), at("wi-tail"), at("wi-end"));
    let mut accepted = 0;
    for (name, position) in [("mu", base_case), ("P*, first", base_case + 1), ("P*, last", tail - 1), ("the tail's first scalar", tail), ("the tail's last scalar", end - 1)] {
        let got = run_as(&without, row, &m.key, &m.pi, &flip(&m.proof, position, 0, 1), &[], &m.summary);
        eprintln!("R4 {name} changed: {}", short(&got));
        accepted += usize::from(got.is_ok());
    }
    let last = m.proof.merkle_openings.len() - 1;
    let width = m.proof.merkle_openings[last][0].leaf.len();
    let salt = row.leaf_salt_words;
    for opening in [0, m.proof.merkle_openings[last].len() - 1] {
        for word in [0, width - salt - 1, width - salt - 4, width - 1] {
            let mut bad = m.proof.clone();
            bad.merkle_openings[last][opening].leaf[word].0 ^= 1 << 17;
            let got = run_as(&without, row, &m.key, &m.pi, &bad, &[], &m.summary);
            eprintln!("R4 the last oracle's row {opening}, word {word} changed: {}", short(&got));
            accepted += usize::from(got.is_ok());
        }
    }
    eprintln!("R4: {accepted} of 13 changes accepted by the guest without the check (0: no refusal of the suite is the check's alone)");
    KBC.with(|k| k.set(None));
}

/// R5: proofs made by a prover that departs from the protocol (self-consistent transcripts and openings).
#[test]
fn referee_r5_prover_made_bad_proofs() {
    use stable_pcs_e2::wi::Controls;
    use aggregation_e2::parts::count;
    KBC.with(|k| k.set(Some(WALLET_KBC)));
    let row = &verifier::params::CAT1_TREE_LEAF_SALTED;
    let whole = program(row, &[]);
    let without = program_src(row, &[("        assert e0 == v0\n        assert e1 == v1\n", "")]);
    let no_pos = program_src(row, &[("        assert rec[GEN ** 0] == positions[xi]\n", "")]);
    let short = |r: &Result<usize, String>| match r {
        Ok(c) => format!("ACCEPTED ({c} cycles)"),
        Err(e) => format!("refused: {}", e.chars().take(200).collect::<String>()),
    };
    for (name, controls) in [
        ("the final message shifted orthogonally to the weight", Controls { shift_final_message: true, ..Controls::default() }),
        ("the linear domain", Controls { linear_domain: true, ..Controls::default() }),
        ("the fold mask in every lane", Controls { every_lane_aux: true, ..Controls::default() }),
        ("no control", Controls::default()),
    ] {
        let m = masked_with(2, controls, false).unwrap_or_else(|e| panic!("{name}: {e}"));
        let native = verifier_e2::verify_execution_with(row, m.key.program().bytecode(), &m.pi, &m.proof);
        let a = run_as(&whole, row, &m.key, &m.pi, &m.proof, &[], &m.summary);
        let b = run_as(&without, row, &m.key, &m.pi, &m.proof, &[], &m.summary);
        eprintln!("R5 {name}: native {:?}", native.as_ref().map(|_| ()).map_err(|e| format!("{e:?}")));
        eprintln!("R5 {name}: the guest {}", short(&a));
        eprintln!("R5 {name}: the guest without the last rows' check {}", short(&b));
        assert_eq!(native.is_ok(), a.is_ok(), "{name}: the guest and the native verifier differ");
    }
    // The suite's own edit (step_3: a drawn query sent to another position's entry) at the oracle with a
    // coincidence, on the guest without the position equality.
    let m = masked();
    let drawn: Vec<Vec<u64>> = m.proof.merkle_openings.iter().map(|phase| phase.iter().map(|o| o.leaf_index).collect()).collect();
    let level = (0..drawn.len()).find(|&l| verifier_e2::spbcs::distinct(&drawn[l]).len() < drawn[l].len()).unwrap();
    let got = run_edited(&no_pos, row, &m.key, &m.pi, &m.proof, &[], &m.summary, &|s| {
        let slots = &mut s.iter_mut().find(|(n, _)| n == "wi_slot").unwrap().1[level];
        slots[0] = if slots[0] == count(0) { count(1) } else { count(0) };
    });
    eprintln!("R5 the suite's slot edit at oracle {level} (of {}), the guest without the position equality: {}", drawn.len(), short(&got));
    KBC.with(|k| k.set(None));
}
```
