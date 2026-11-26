# Referee: K-1' node boxes (System A, yugen-proof-a dc9f5f3)

Independent, adversarial read. Read-only; nothing built. Citations are at `dc9f5f3`.

## Verdict: PASS WITH CONDITIONS

The box bounds what a cheating prover can get accepted, and the walk is exhaustive over the
committed boxes. The box itself is measured, not derived, so its upper edge carries a liveness
risk. Its lower edge buys no soundness. Both should be fixed before the box is called final.

## 1. Does the box bound every announced size that feeds the message count?

Yes, for accepted proofs.
- The announcement is `log_memory`, the seven `table_rows` and `log_inv_rate`
  (`vendor/leanMultisig/crates/verifier/src/lib.rs:405-416`). The rate is pinned to 1/2 natively
  (`src/bundle2.rs:219`) and in circuit (`guests/e2/h_sub.py:74`). The row is pinned by
  `consensus_rows` (`src/bundle2.rs:237`) and the bytecode by the programs. The stack, the round
  count (`lib.rs:423`, the largest table log) and `admitted_stack_log` are all computed from
  those values. Nothing that feeds the message count is left free.
- Exact row counts are not boxed, only their `log2_ceil` heights (`layout.rs:744-748`). The claim
  that the control flow depends only on the heights is asserted (`lib.rs:312-316`) and checked
  empirically against real proofs (`tests/kq_report.rs`); it is not proved. Exact `rows` reach
  `BusBlock` (`layout.rs:757`) and the padding values (`bus.rs:348-358`), but only as values. The
  one branch on an exact value is `rows == 0` for the unblinded table (`lib.rs:430`). That branch
  can only refuse, and it does not apply to node programs, which use MUL2.
- Native ordering: `node_tables_admitted` runs after the full `verify_execution_with` /
  `replay_unchecked_with` (`src/bundle2.rs:1237-1238`, `1564-1565`). This does not break
  soundness, because every accepted proof is in the box. It does mean the native verifier does
  unbounded work on an out-of-box announcement before it refuses: a cheap DoS.
- In circuit, the check `log(ratio) < 8` (`h_sub.py:69-73`) is a correct range check, given that
  the logs are certified in `verify_tables` (stated at `h_sub.py:64`; I did not re-audit that).

## 2. Is the walk exhaustive, and does its maximum feed k_q?

Yes.
- The walk is an odometer over the whole box (`tests/kq_max.rs:166-196`), and the walk counts
  match the box volumes exactly:
  - mode 0 S: 3·4·3·3·4·3·4·3 = 15552
  - M: 4^8 = 65536
  - mode 1 S placeholder: 4^6·5^2 = 102400
- `skipped=0` everywhere. The 35 refusals are walks the verifier itself refuses, on the same code
  path.
- The committed mode 1 S box (`src/bundle2.rs:193`) is a subset of the walked placeholder, so its
  maxima bound the committed box. The file should still be regenerated on the committed box
  (condition 4).
- The maximum is kept per stack and taken over S and M. The stack-2^27 maximum, 1184 (M), feeds
  `kq-need` (`kq-box-20261119.txt`): k_q = 2·1184 + 34440 = 36808 against the calculator's
  36612. The larger value is the one used, and it gives the +0.239 margin. Consistent.
- The walk is tied to the live code only through `CONSENSUS_NODE_BOXES`. Nothing fails when the
  box or the programs change, because the test is `#[ignore]`.

## 3. Liveness

Real risk, at the upper edge.
- The box is "least and most over the honest runs measured" (`src/bundle2.rs:184-186`): counts
  1 to 6 or 8, children of the least and the most size, and depth up to 3 only.
- No closure argument shows that the merge of the largest admissible children, at the largest
  arity, still lands inside the merge box. An honest depth-4 tree, an unmeasured mix, or a merge
  of maximal children is refused if it does not.
- The leaf side is already pinned (`ZK_PIN`, `src/bundle2.rs:177`). Host-script length cannot
  move node sizes unless it moves the leaf, and the leaf pin refuses that first. That is an
  existing leaf-pin liveness item, not a box item.
- How to derive the box (formula):
  - Upper bound. Compute M_max = tables(merge of a_max children, each at the box's own maximum),
    and S_max = tables(sub of the largest admitted count). Require M_max ≤ box.hi. That makes the
    box a fixed point, and closure follows by induction over depth. This assumes, and should test,
    that the table rows are monotone in the child's announced heights and in the arity.
  - Lower bound. The lower bound serves no soundness purpose: k_q is a maximum. Set it to the
    layout floors (`layout.rs:661`) or to the smallest legal child, or drop it.

## 4. Box vs per-arity pin

The deviation is sound and better. A per-arity point pin is wrong on the evidence: a merge of two
S(1) children commits 2^25 and a merge of two S(6) children 2^26 (`node-pins` lines). Soundness
needs an upper bound on announcements, and a box gives exactly that. The decision should be
amended to "box, derived by the closure formula", not reverted.

## Conditions

1. Derive the box's upper edge from the closure formula in section 3, with a test that the
   maximal merge of maximal children stays in the merge box at the largest arity the tree builder
   can emit. Also bound that arity and the depth explicitly, or show that they need no bound.
2. Lower the lower edges to the layout floors (or drop them), then re-walk.
3. Move the native box check to right after `build_layout` in the walk, before any further
   transcript work, so that an out-of-box proof is refused cheaply. Keep the post-hoc check as
   well.
4. Re-run `every_announcement_a_node_box_admits_walked` on the committed boxes and make it
   un-ignored, or add a CI check that the `CONSENSUS_NODE_BOXES` hash matches the box the walk
   used.
5. Turn the "control flow depends only on log heights" claim into a check. For example, walk one
   rows value at each end of every height interval (2^(h-1)+1 and 2^h), or show that `rows` is
   used only as a value.
6. Record the box as the amendment to the per-arity decision, with this report as its review
   (`src/bundle2.rs:189` still says "unreviewed").
