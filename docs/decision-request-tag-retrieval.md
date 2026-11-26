# Decision record: how a wallet finds payments to its requests

*The Ycash developers, 2026. Record opened 2026-11-20. Keep this file current: it is the reference
for this decision before, during and after implementation (section 7 is the implementation log).*

## 1. The question

Specification 0.4.4 (SPEC-176) gave every payment to a payment request its own tag, so that no one
but the request's holder can link two payments to the same request. The price was bandwidth: every
wallet downloads each day's whole incoming slice (60 bytes per output) and checks it itself, about
1.38 MB a day at ten transfers a block and about 1.19 GB a day at full blocks. The lead architect
asked for a design study of the alternatives, "to see if this would be feasible to implement sooner
rather than later".

## 2. Sources

| Document | What it is | Status |
|---|---|---|
| `docs/design-private-tag-filtering.md` (`d53ea58`) | The design study: both papers summarised, post-quantum status, fit with the design, options, the slim slice | Draft, refereed |
| `docs/slim-slice-referee.md` (`f7ca82e`) | Independent referee report on the study and on option (v) | Pass with conditions |
| [BLMG21] Beck, Len, Miers, Green, "Fuzzy Message Detection", ePrint 2021/089 (folder: `2021-089.pdf`) | Option (iii) | Published |
| [LT21] Liu, Tromer, "Oblivious Message Retrieval", ePrint 2021/1256, revision of 2022-04-14 (folder: `2021-1256.pdf`) | Option (iv) | Published |
| Specification `yugen-spec`, SPEC-176, SPEC-177 (0.4.4); the decision taking option (v) (0.4.5, in preparation) | The rules | — |

## 3. Options compared

Figures from the design study, with the referee's corrections applied (marked *). Download is per
wallet per day at ten transfers a block / at full blocks.

| Option | Quantum-safe | Changes what proofs prove | What the host learns | Wallet traffic per day | Server cost (full blocks) | Verdict |
|---|---|---|---|---|---|---|
| (i) Status quo, SPEC-176: download every 60-byte slot | yes (hashes) | no | nothing beyond the fixed sync schedule | 1.38 MB / 1.19 GB | serving the bytes | works; heavy for phones at full blocks |
| (ii) Two-host private retrieval (DPF) over today's slice | yes (hashes; hosts must not collude) | no | nothing, if the hosts do not collude | no saving | — | does not work: the wallet cannot compute where its payment sits, because the tag depends on the payer's `nf_1` |
| (iii) Fuzzy message detection [BLMG21] | **no**: FMD2 rests on discrete-log / Gap-DH (Theorem 13) and breaks retroactively; no post-quantum instance in the paper | no (a proof would only stop denial of service) | a decoy set of size about `p·N`; the paper reports Lewis's attacks on the anonymity | 5.4 KB / 4.7 MB at `p = 2^-8` | about 3 hours of core time per wallet | rejected: not quantum-safe, and the host learns a candidate set |
| (iv) Oblivious message retrieval [LT21] | an assumption: Ring-LWE, about 120/128 bits by the classical estimator, below our top level | no for privacy; stopping denial of service in circuit would take about 7.3M field operations plus 112K Keccak-f (infeasible) | nothing about content; a long-lived 129 MB detection key links a wallet's sessions | at least 549 KB / 2.5–22 MB | about 33 core-days per wallet per day | rejected for now: server cost, key size, below the security target; could be offered later as an opt-in service |
| **(v) Slim slice (adopted)**: download only `itag` and a public digest `n_j` per output (14 bytes), fetch matched slots by DPF at a fixed count | yes (hashes; hosts must not collude, as today) | **no** | the same as (i) | download 323 KB / 279 MB; with the DPF key upload the saving is about 2× at light load and about 4.3× at full blocks* | a fixed number of DPF evaluations per sync over a nine-slice window* | adopted, with the referee's conditions |
| (vi) Slim slice now, OMR later as an opt-in service | as (iv) for wallets that opt in | no | as (iv) for those wallets | as (v), or as (iv) | as (iv) | kept open for later |

How the slim slice works, in one paragraph: each payment's tag is computed from the request key and
a short public digest, `n_j = trunc_8(H(nf_1 || j))`. The digest is made from values that are public
already, so it links nothing. Every wallet downloads 14 bytes per output, recomputes tags for its own
requests, and fetches only the matching payments through the two-host private retrieval it already
uses, always making the same number of fetches per sync so the count reveals nothing. The slim
slice is original work of the Ycash developers as far as the study could check; its parts (trial
scanning, two-host DPF retrieval) are published.

## 4. The referee's conditions (all adopted)

| Id | Severity | Finding | Fix taken into the specification |
|---|---|---|---|
| M-1 | major | The domain the slot fetches query was unspecified: a per-day slice tells the host which day a wallet was paid; the whole history grows without bound | Every sync queries one fixed nine-slice window |
| M-2 | major | Anyone holding a request key can flood matching tags with wrong commitments and use up the fixed fetch count (a new remote denial of service; a fake payment is still never credited) | A carry queue serving requests in turn, flagging of a flooded request, a test vector |
| M-3 | major | Restore was unspecified | Restore keeps downloading the full 60-byte slots |
| m-1 | minor | Carry-over hides the match count but delays spending of a carried payment | The delay is stated |
| m-2 | minor | The wallet should check `n_j` on every fetched slot and compare slim-slice hashes across the two hosts | Adopted |
| m-3 | minor | The DPF key upload was left out of the bandwidth figures | Restated: about 2× saving at light load, about 4.3× at full blocks |
| m-4, m-5 | minor | OMR capacity falls to about 1/9, not 1/5; a citation in the study points at the wrong passage of [LT21] | Corrected in the study |

Verified by the referee: unlinkability (an 8-byte digest collision has odds of about 2^-65 per pair
and only links anything inside one request's payments); a fake payment can never be credited (the
commitment is recomputed and a membership path is required); the reasons for rejecting (ii)–(iv)
match the papers. Not verified: the supporting papers the study did not read (PVW08, BFV, BGI16,
ZIP-307, Lewis's analyses); server figures are scaled from the papers, not measured.

## 5. Decision

Adopt option (v), the slim slice, with all the referee's conditions, in specification 0.4.5.
Decided by the lead agent on 2026-11-20 after the study and its referee, following the lead
architect's request to study the alternative; open to the lead architect's review.

## 6. What would change this decision

- Load at which 14 bytes per output a day is still beyond light wallets: then offer (vi), an opt-in
  oblivious retrieval service, which needs no change to what the proofs prove.
- A post-quantum fuzzy message detection with an anonymity analysis that survives Lewis's attacks.
- A break of the two-host non-collusion assumption in practice (it already underlies private
  retrieval in the design).
- Measured server cost of the fixed fetch schedule far above the scaled figures.

## 7. Implementation log

Add a dated line for each step: specification version, code commits, measurements, reviews.

| Date | Step | Where | Result |
|---|---|---|---|
| 2026-11-20 | Design study | `docs/design-private-tag-filtering.md` `d53ea58` | Options compared; (v) recommended |
| 2026-11-20 | Referee | `docs/slim-slice-referee.md` `f7ca82e` | Pass with conditions M-1..M-3, m-1..m-5 |
| 2026-11-20 | Specification change | `yugen-spec` 0.4.5, tag `spec-0.4.5` (`228b2f5`), SPEC-184 to SPEC-191 | Merged; all conditions applied; 357 KB down + 336 KB up a day at ten transfers a block (1.99×), 278 MB + 336 KB at full blocks (4.28×); host about 0.54 core-s per slot query at full blocks, scaled from a 128-bit-seed figure (to re-measure at 256-bit seeds); no circuit change |
| 2026-11-20 | Models check of the fixed fetch schedule and the carry queue | `yugen-models` `9f14368` | P-1, P-3, P-4, P-5 closed; P-2 open by stated assumption (anonymising transport is a MUST); overflow and flood transcripts identical to the host. New: S-1 medium (an active host corrupting a share learns from the wallet's reaction whether a request payment was pending; fix: check every answer, react identically), S-2 low (partial restore after a flood marks the wallet; fix: full restore only), S-3 text (a flood delays others up to ceil(R/3) syncs) |
| 2026-11-20 | Specification change for S-1 to S-3 | `yugen-spec` 0.4.6, tag `spec-0.4.6` (`905eca7`), SPEC-192 to SPEC-195 | Merged: every answer checked, one reaction at a fixed time (a cover address answer can be checked only for format, so a real address answer failing decryption alone is retried silently, not reported); recovery by full restore only (about 1.19 GB a day at full blocks, for a flooded wallet only); the flooded request takes one slot in each round of the turn, others wait at most ceil(R/3) syncs; the backlog warning at expiry < wait; no circuit change; 95 tests on three targets, 113 mutations, 109 reverts; checkers re-run by the lead |
| 2026-11-20 | Models re-check at 0.4.6 | `yugen-models` `c43e6e4` | S-1, S-2, S-3 and the expiry wording closed; full model check passes (133 TLC configurations, 177 vectors). New: S-5 low (a host colluding with the payee corrupts a real address answer, the silent retry stalls the payment, and the stall tells it this session is the payer), S-6 text (the flood can take up to ceil(4/(R+1)) slots a sync) |
| 2026-11-20 | Specification change for S-5, S-6 | `yugen-spec` 0.4.7, tag `spec-0.4.7` (`8ed62a2`), SPEC-196 to SPEC-198 | Merged: address records an append-only table under a per-sync root that both hosts publish; every address answer (3,270 bytes, +802) carries its path and is checked like a slot answer, so the exception is gone; residual: a corrupted real answer still delays that payment one sync (one bit per corruption, each costing the host a fault report and the wallet's switch), stated in §18.6 (D); about 231 KB a day more per wallet; flood text corrected; 0xbf reserved for System B; no circuit change; 96 tests on three targets, 117 mutations, 113 reverts; checkers re-run by the lead |
| 2026-11-20 | Models re-check at 0.4.7 | `yugen-models` `e61804a` | S-5 and S-6 closed; the address table adds no distinguisher; full model check passes. New text gaps: S-7 minor (a wallet back after several missed periods cannot rebuild the locator chain), S-8 low (no answer passes while the table is empty, a fault storm for every wallet alike) |
| 2026-11-20 | Specification change for S-7, S-8 | `yugen-spec` 0.4.8, tag `spec-0.4.8` (`b108428`), SPEC-199, SPEC-200 | Merged: a catch-up sync gets the count at every missed boundary from both hosts (8 bytes a boundary for the pair, 576 a missed day); cover address indices drawn from the filled table, no address queries while it is empty; no circuit change; 97 tests on three targets, 121 mutations, 117 reverts; checkers re-run by the lead |
| 2026-11-20 | Models re-check at 0.4.8 | `yugen-models` `3674cf3` | S-7 and S-8 closed; no new findings; full model check passes (133 TLC runs, 177 vectors, 504-point sweep). **The sync-privacy model is closed at 0.4.8** (P-2 stays open by its stated transport assumption) |
| | Wallet implementation | wallet code | Not started |
| | Measured bandwidth and server cost | — | Not measured |
