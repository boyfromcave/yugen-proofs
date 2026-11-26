# Referee report: `lemma-tree-extraction.md` revision 5.1 (section 6b)

Date 2026-11-20. Object: `lemma-tree-extraction.md` at `af56689` (revision 5.1), against `tree-extraction-rev5-referee.md`
(`cabb19c`). Code read (read-only): `yugen-proof-b2/wt/s045`, branch `agg`, head `8d1517f`.

**Verdict: PASS WITH CONDITIONS** (R51-1 to R51-3, section 3). R5-1 to R5-3 are met; R5-4 is met in substance, but the
text cites an unversioned log and a root-discharge path that the code has since added to (`cc6a794`). Editorial only;
no figure moves. `what-is-proven.md` is **not** updated (its rule needs a PASS; the rows stay "not proven").

## 1. The four conditions

| Item | Met? | Check |
|---|---|---|
| R5-1 | yes | 6b (c) records `fold::require_challenge256` (`0613c6c`), its enforcement in `build_uniform` (`src/node.rs` 578, confirmed at `8d1517f`) and `uroot::check_root`, `tests/fold_field.rs`; the default row is "not constructible", 120.76 / ~60.4 kept only as the reason. The summary paragraph is restated to match. |
| R5-2 | yes | Quantum column header and the note say "order only, constant not stated, [CMS19] not re-read"; the `cat1t` conclusion is stated as independent of the constant. |
| R5-3 | yes | `what-is-proven.md` line 64 now gives the per-query term `(t + K) 151/|F_c|` (~`2^-248.76` at `GF(2^256)`), withdraws `2^-107.8`, names both reports and the refusal, keeps the rows "not proven". |
| R5-4 | in substance | The check ran: `bench/results/v-tree-pad23-chain4-vfinal.txt` (versioned in `99f646a`, copy of log lines 100-106: `VFINAL W* = sum_k eq(s, k) W_k at a random point; 81052349 terms`, root verified, refusals) and `bench/results/v-tree-vfinal-20261120T0947Z.txt` (head `cc6a794`, log sha256 `6cc60b9c...6c9f`, same line plus `VFINAL stacked W* evaluator = the discharge at a random point`). Code `examples/recbench.rs` 2459-2470: `assert_eq!(star.evaluate(point), fold::evaluate(point, [four kinds]))`, `StdRng` seed 24, one point; confirmed. But revision 5.1 cites only `target/logs/...chain4.log` at `13e0e9d` (not versioned), not the versioned records (R51-1). |

## 2. Regression check (diff `cabb19c..af56689`)

Only the revision note, 6b (c) table and bullets, 6b (d) root-discharge paragraph, the summary, and
`what-is-proven.md` line 64 changed (27+/12-). No other statement, figure or condition moved. The C2 list is
unchanged (six obligations; the root discharge still listed as owed). Two drifts:

- **Root discharge (cc6a794).** `uroot::check_root` now has two paths (`src/uroot.rs` 191-194): with
  `RootRule::folded_wiring` set, the folded claim is checked by one `phased::Stacked` evaluator
  (`weights.len() == 1 && weights[0] * star(point) == value`); otherwise `fold::holds` over the four kinds as before.
  The lemma names the discharge as `uroot::check_root` / `fold::evaluate` only. The 0947Z record shows the stacked
  evaluator equals the discharge at the same random point, so the statement remains true of the code as run, but the
  C2 obligation must name both evaluators (R51-2). The extra `weights.len() == 1` requirement only narrows acceptance;
  no soundness consequence.
- **Line citation.** `uroot.rs` "line 166" is now 170 (`require_challenge256()?`); cite by commit (R51-3).

## 3. Conditions

1. **R51-1.** In 6b (d), cite the versioned records `bench/results/v-tree-pad23-chain4-vfinal.txt` (`99f646a`) and
   `bench/results/v-tree-vfinal-20261120T0947Z.txt` (`8d1517f`, run at `cc6a794`) in place of, or beside, the
   `target/` log; drop the "not versioned" caveat accordingly. Keep "one fixed-seed point, a test, not a proof".
2. **R51-2.** In 6b (d) and the C2 list, name the root discharge as `check_root` with either evaluator
   (`fold::evaluate` over the four kinds, or `phased::Stacked` via `RootRule::folded_wiring`, `cc6a794`); the C2
   equivalence obligation covers the one the deployed verifier sets.
3. **R51-3.** Pin the `src/uroot.rs` / `src/node.rs` line citations to a commit (`0613c6c` or `8d1517f`).

No paper relied on; [CMS19] not used for any figure here.

## 4. Revision 5.2 (`b9836a8`)

Diff `d31ce64..b9836a8`: `lemma-tree-extraction.md` only, 17+/5-, all in the revision note and 6b (b) to (d).
- **R51-1 met:** 6b (d) cites both `bench/results` records with commits (`99f646a`; `8d1517f`, run at `cc6a794`).
  The leftover "the log sits under `target/`, not versioned" is now true only of the raw log; harmless.
- **R51-2 met:** 6b (c) and the C2 list name `check_root` by either evaluator (`fold::evaluate`; `phased::Stacked`
  via `RootRule::folded_wiring`, single weight), both owing the test.
- **R51-3 met:** 6b citations pinned to `13e0e9d`; confirmed `uroot.rs` 166 and `node.rs` 578 at `13e0e9d`,
  `uroot.rs` 170 at `8d1517f`.
- Nothing else changed; no figure moved.

**Verdict on revision 5.2, section 6b: PASS.** The tree rows stay **conditional** (K-A, K-B, C2 including the root
discharge's equivalence, H-BIND); revision 3's SHAPE-VIOLATION / Lemma TE.3 remains unrefereed. `what-is-proven.md`
updated accordingly (line 64, T-a and T-c Refereed columns, queue row).
