# Referee report: `lemma-tree-extraction.md` revision 5 (section 6b)

Document: `docs/lemma-tree-extraction.md` at `ac52f46` (draft). Conditions checked: `tree-extraction-rev4-referee.md`
R4-1 to R4-8. Code: `yugen-proof-b2/wt/s045`, branch `agg`, head `13e0e9d` (read only; nothing built or run).
Referee: independent, adversarial. Date 2026-11-20.

**Verdict: PASS WITH CONDITIONS** (R5-1 to R5-4, section 3). The conditions are editorial / record-keeping; no
mathematical gap found in 6b. Nothing is marked proven: the rows also rest on K-A, K-B, C2 and the unrefereed
revision 3 parts, which this report does not cover.

## 1. The R4 conditions

| Condition | Met? | Check |
|---|---|---|
| R4-1 two passes | yes | 6b (c): pass 1 is TE'/K-B unchanged under "accepts"; pass 2 is top-down induction from the root discharge, the only failure a false input batched into a true output. One fixed `W* = sum_k eq(s,k) W_k` of the four keys pinned by `check_root` (`src/uroot.rs` 165 ff.) and forced equal down the tree by `uniform_head`; child claim and `fW` are public statement words bound before the first `sample` (`pbatch::run`). Sound. |
| R4-2 8,193 | yes | 6b (a); `parameters.md` 24.4 (3) relabelled in `df7e631`. |
| R4-3 drop `2^-106.5` | yes | dropped, with the reason. |
| R4-4 t-linear term, field per build | yes | `t eps_max + (t + K) eps_batch,max` beside TE'; field read from code (below). |
| R4-5 condition 5 built | yes | `bvirt.rs::slot_kind` (60–84) checked: `Published` forces `f` in {0,1} and id key = `KM`/`K0` by `f`; `Internal` `f = 2`, key `KI`; `Internal0` `f = 3`, key `KI0`. With `uniform_head`'s key equalities and `check_root`'s four constants, the kind is fixed by the pinned keys. Tests cited, not re-run (stated). |
| R4-6 constants | yes | `m = 4`, `n + 2 = 74`, 151, `k_q` 40,568. |
| R4-7 4/4/5 a proposal | yes | stated; 16/16/3 stands as spec 0.4.7. |
| R4-8 root discharge in C2 list | yes (listed) | 6b (d). The deployed-key random-point run is still owed; `tests/fold.rs:98` checks `fold::evaluate` against the stacked polynomial on test families only. |

## 2. Arithmetic, field, refusal

- `log2 151 = 7.238`. `151/2^128 = 2^-120.76`; `151/2^256 = 2^-248.76`. Reproduced. `K <= 8,193 x 40,568 = 2^28.31`: reproduced.
- Default combined: `2^-121.89 + 2^-120.76 = 2^-120.22`. Reproduced.
- Quantum form: `(t + K)^2 eps_batch` is the generic search bound for grinding a Fiat-Shamir event of density
  `eps_batch` with `t` quantum queries; caps 60.38 / 124.38 are the classical caps halved, **constant omitted**
  (the doc says "to about 1 bit"). I did not use the [CMS19] constant and so did not re-read it; the quantum caps are
  therefore accepted only as "about". At `cat1t` the margin (124.4 vs the stated 70.45 / 69.58) absorbs any constant
  up to `2^50`, so the conclusion "no stated bound drops" does not depend on it.
- Field from code: `pbatch::run` draws through `IPVerifierChannel<B128>`, `B128 = ChallengeField`
  (`vendor/binius64/crates/field/src/arch/arch_optimal.rs`: `GhashSq256b` under `challenge256`, else `Ghash128b`);
  `Cargo.toml` 58, 61: `cat1 = ["binius-field/challenge256"]`, `cat1t = ["cat1", ...]`; default `["recursion"]`. Confirmed.
- **Fold refused without challenge256 (commit `0613c6c`).** `fold::FOLD_FIELD_OK = size_of::<B128>() == 32`;
  `require_challenge256` is called by `uroot::check_root` (returns Err) and by `Node::build_uniform` (panics whenever
  `uniform.is_some()`), which every uniform constructor (`node.rs` 546, 560, 567, 572) goes through; test
  `tests/fold_field.rs`. No other native discharge path found (`check_root` is the only caller-facing discharge). So
  a fold build is necessarily 256-bit and the 128-bit caps never apply to a built fold. **Revision 5 does not say
  so** (it was written before `0613c6c`): its "Default build: B's bounds would drop" paragraph describes a build that
  can no longer be constructed (R5-1).
- `what-is-proven.md` for `cat1t`: T-e 121.89 / 114.74 and the QROM rows (70.45 for B, 64 target) all sit far above
  the `2^-248.76` per-query term and the ~124.4 quantum cap. **No stated bound drops for `cat1t`.** Confirmed.

## 3. Conditions

1. **R5-1.** In 6b (c), record the built refusal (`fold::require_challenge256`, `check_root`, `build_uniform`,
   `tests/fold_field.rs`, commit `0613c6c`) and recast the default-build row as "not constructible: the fold is
   refused"; keep the 120.76 / ~60.4 figures only as the reason for the refusal.
2. **R5-2.** Label the quantum column's constant: either state the constant of the grinding bound with its source
   (re-read, page cited) or mark the column "constant omitted, order only". The cat1t conclusion stands either way.
3. **R5-3.** `what-is-proven.md` line 64 is stale: it still gives the batching term as "about `2^-107.8`" (the
   withdrawn sum form) and waits "until a referee report on revision 4 is named" (it is named). Restate it with the
   per-query term and the refusal.
4. **R5-4.** R4-8 remains owed in code: run `vfinal`'s random-point check of `check_root` against
   `sum_k eq(s',k) W_k(r')` for the deployed keys and cite the run; until then the root discharge stays an open C2
   obligation.

No paper relied on beyond the document's own citations; [CMS19] (Chiesa, Manohar, Spooner, *Succinct Arguments in
the Quantum Random Oracle Model*, ePrint 2019/834) was not used for any figure here.
