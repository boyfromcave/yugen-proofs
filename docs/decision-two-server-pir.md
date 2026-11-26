# Decision record D-PIR-3: two-server PIR is Yugen's mode of record (2026-11-24)

Status: **decided** by the lead architect (ruling 17, `yugen-plan` `docs/beta4-yugen-addendum.md`,
"Lead architect's rulings (2026-11-24, third set)"). Scope: the retrieval layer between a wallet and
its hosts (`lightwalletd-dd` mailbox hosts). Nothing here is consensus. Written for review by
outside cryptographers and by readers who are not specialists: plain statement first, precise
statement after.

Sources: `yugen-spec` tag `spec-0.5.2` §17.6-§17.8 and §18.6; the single-server PIR study (not published)
(D-PIR-2, commit `012e269`, "the study"); `yugen-pir` `docs/pir-selection.md` ("the selection",
2026-11-19, with its addendum of 2026-11-24); `lightwalletd-dd` branch `yugen/mailbox`
`yugen/docs/yugen-host.md` ("the host doc").

Labels on every figure: **[them]** measured by a scheme's authors, **[us]** measured on our
machine (results in `yugen-pir` `bench/results/`), **[est]** estimated from those, arithmetic in
the study §3. Provenance: every PIR scheme named is **Published** (cited in the study §2); the
mapping onto Yugen, the operator model and this decision are **Original (the Ycash developers,
2026)**.

## 1. The decision and its context

**Plain.** A Yugen wallet must fetch a few records from a server to learn whether it was paid and
to spend: which outputs carry its tags, the tree path of a note it owns, and the public record
behind a short address it pays. Asking for "record 41,773" in the clear tells the server who the
wallet is dealing with. Private information retrieval (PIR) lets the wallet fetch the record
without the server learning which one. Yugen uses the two-server form: the wallet sends a
scrambled half-question to each of two servers run by different operators; neither half says
anything on its own, and the wallet combines the two answers.

**Decision (ruling 17).** Single-server PIR is not pursued now. Two-server PIR (a distributed point
function, DPF) is the mode of record. The network starts with two or three `lightwalletd-dd`
hosts run by independent operators, every one of which serves the two-server model.

**Why privately, and why on a fixed schedule.** PIR hides *which* record is read, not *how many*
or *when*. So the spec fixes the pattern (§17.8, SPEC-177): every wallet syncs once per 16 blocks
(72 times a day), at one shared phase with a random 0-60 s delay, and every sync sends exactly
4 slot, 8 path and 2 address queries to each host, padded with cover queries that are answered and
checked exactly like real ones. A wallet that was paid, paid twice, or paid nobody sends the same
traffic. Wallet transport keys are fresh every session (§17.7, SPEC-178) so a host cannot link a
wallet's sessions by key. These two rules (fixed cover traffic, no long-lived client keys) are
what decide between PIR schemes; §2 shows why.

Precise: the DPF is BGI16's tree construction (Boyle, Gilboa, Ishai, "Function Secret Sharing";
**not read**, from memory through the selection §3.1, as spec §17.6 states) at 256-bit seeds with a
SHAKE256 length-doubling PRG (`H_dpf-prg`, spec §17.6). Wallet-host transport is hybrid X25519 +
ML-KEM-1024 (§17.7).

## 2. The numbers side by side

Per wallet per day, at full blocks (slot window 10.7 GB, 10^6 used addresses = 3.27 GB, one year of
paths = 0.42 GB; 52.7 GB scanned per sync per host). Source: the study §3 unless stated.

| Mode | Upload / day | Download / day | Host core-s / wallet / day | Post-quantum at shipped parameters | Answers verifiable |
|---|---|---|---|---|---|
| **Two-server DPF (chosen)** | ~1.2 MB, both hosts [est: 14 × 584 B key per host × 72; key size from spec §17.6] | ~5.4 MB, both hosts [est from spec §17.8 sizes] | ~190 per host [est from us: 0.05 core-s/GB at 128-bit seeds, selection §3.1; 256-bit not measured, task W-4] | **yes**: symmetric PRG only; transport ML-KEM-1024 | yes, every answer against committed roots (§17.8 item 3) |
| YPIR (single) | ~1.5-2 GB [est: √N scaling of their 1 GB query, 846 KB, YPIR Table 1 [them]] | ~12 MB [them → est] | ~490 [est from their 7.8 GB/s] | **no**: ring d=2048, q≈2^56, β=354 < 406 [us, selection §2.2] | same root check; no second host to compare |
| Respire / Spiral (single) | ~300-560 MB, client key re-sent each session [us: 3,980 KiB key; them: 7.8 MB] | small | ~7,200 [est from us: 1.9 core-s/GB]; server RAM 17-35× DB [us] | **no** (β=357 Respire, 354 Spiral) [us] | same |
| SimplePIR (single, hint) | ~0.3-1 MB per sync [est] | **>10 GB**: hint ≥121 MB per GB-class DB [them], re-sent every sync because every DB changes every sync | ~190 [est] | **no** at n=1024 (β=326) [us]; yes at n≥1,280 [us], not built | same |
| FrodoPIR / ChalametPIR (single) | >4 GB [est from their 4 MB query] | hint per DB per sync | ~3,000 [est from their 0.8 s/GB] | **yes** (n=1774, β=528) [us] | same |

At today's scale (about ten transfers a block) only the address database is large; YPIR then needs
about 290 MB of upload a day [est], still about 50× the DPF (study §3).

**Reading.** Server compute is not what separates the schemes: the fast single-server schemes are
within 1-3× of the DPF. Wallet traffic is: a single server is paid for with large queries, client
keys or hints, and Yugen multiplies that by 14 queries × 72 syncs on databases that change every
sync, with keys that may not be reused. The only single-server scheme that is post-quantum as
shipped (FrodoPIR) is also the most expensive. Hence ruling 17's "~100-1000× wallet traffic".

**Not measured** (study §7): no single-server run on Yugen-sized data; the DPF at 256-bit seeds
(W-4); YPIR above 1 GB (√N estimate). The paper figures were taken through the selection §2.1 and
not re-read on 2026-11-24.

## 3. The trade-off, stated honestly

**Trust assumption (SPEC-183, §18.6 (A)).** Privacy of *what a wallet reads* holds only if the two
hosts it uses do not pool their halves. This is an assumption, not a guarantee, and **nothing in
the protocol detects collusion**.

**If the two operators collude, they learn** (spec §17.6, §18.6 (A)):
- every index every wallet read from them: which incoming slots (so which outputs paid the
  wallet's requests, SPEC-184), which note paths (so which notes it owns and will spend), which
  short-address records (so whom it is about to pay);
- not only from then on: **from their logs, for every past query** they kept. Logged keys also fall
  later if the 256-bit seeds or the §17.7 transport are ever broken (record-now-break-later);
- combined with the network address, unless the wallet uses an anonymising transport (§18.6 (D)),
  a per-wallet history.

**They do not gain:**
- **no theft**: hosts hold no spending keys; spends are authorised by the wallet's Falcon key and
  proved in zero knowledge, checked by every node;
- **no forgery or false balances**: every answer, real or cover, is checked against the slim
  layer, the completed subtree roots or the pair's address root `aroot_h` (§17.8 item 3); a wrong
  answer is detected and reported, with a reaction that does not depend on whether the query was
  real;
- **no amounts or memos**: packages stay encrypted to the recipient (ML-KEM-1024, §18.6 (B));
- **no consensus power**: hosts are outside consensus; the chain, and anyone's funds, are unaffected.

Collusion is therefore a privacy failure (who received and whom one pays), not a safety failure.

**Availability.** A sync needs two live hosts. With only two hosts, one host down stops private
retrieval for everyone until it returns: funds are safe on chain, but incoming payments are not
seen and paths not fetched, so spending a newly received note waits. A wallet that sees a failed
check moves to "the other host" (§17.8), which presumes a third. Hence two to three hosts at launch,
and three as the target before any user depends on it (§4).

**Centralisation.** Two or three operators are a small set: a natural point for pressure, logging
orders or quiet cooperation, and a barrier to entry if hosting is costly. The DPF keeps host cost
low (~190 core-s per wallet per day at full blocks [est]; much less at today's scale), so the cost
barrier is lower than for any single-server scheme; the governance barrier is the real one and is
addressed in §4.

## 4. Mitigations (tasks with acceptance criteria)

The operator rules below are **Original (the Ycash developers, 2026)**, proposed here; they are not
yet in the spec and need the lead architect's sign-off.

| Task | Acceptance criteria |
|---|---|
| M-1 Independent operators | Each bootstrap host is run by a different legal entity, in a different jurisdiction, on a different hosting provider; operators publish identity, jurisdiction and a no-logging / no-sharing statement; the list is published with the release |
| M-2 Two to three bootstrap hosts, wallet picks any two | Wallets ship the host list and choose two hosts of different operators per session; with three hosts, losing one leaves a working pair (devnet test: kill any one of three, every wallet completes its next sync) |
| M-3 Diversity and rotation | Host list is versioned and replaceable without a node or wallet code change; an operator can be added or removed by a list update; wallets never pair two hosts declaring the same operator or jurisdiction |
| M-4 Transparency | Each host publishes its software version (reproducible `lightwalletd-dd` build), its log-retention setting, and its long-lived §17.7 keys; a wallet refuses a host whose `aroot_h` and roots disagree with the other host's |
| M-5 Shorter logs | Default host configuration does not retain DPF keys after answering (the host doc today logs every request to `D/queries.log`: change to off by default, keep for devnet only) |
| M-6 Anonymising transport option | Wallet supports a network-level anonymiser so collusion does not also give network addresses (§18.6 (D)) |
| M-7 Single-server mode later, without a network upgrade | Retrieval sits between wallet and host, not in consensus. A §17.9 single-server mode (study §5, option B: address and path databases only, re-parameterised to β ≥ 406, its own fixed query counts, per-session keys) can be added by a wallet and host release. Acceptance as in study §5 items 1-4 |

**What would reverse this decision** (any one, measured, not claimed):
1. A single-server scheme at parameters meeting the ML-KEM-512 primal level (β ≥ 406, confirmed by
   the Lattice Estimator's full attack set) whose wallet traffic under the §17.8 schedule is within
   **10×** of the DPF's on Yugen-sized data (the study's benchmarks B1-B5); or a re-parameterised
   YPIR with upload under ~200 KB per sync (study §5 trigger (i)). Then a single-server mode is
   added beside the DPF (M-7), not instead of it, unless trigger 2 also holds.
2. Independent non-colluding operators prove unattainable (fewer than two independent operators
   willing to host). That forces single-server PIR with a lighter fixed schedule (study §5 option C).
3. The fixed cover schedule is relaxed by a later ruling (fewer queries or syncs), which shrinks the
   single-server penalty in proportion.

## 5. Options considered

| Option | For | Against |
|---|---|---|
| **A. Two-server DPF only (chosen, ruling 17)** | kilobytes per sync; post-quantum from symmetric crypto; built (M3 host `yh_addrquery`) and measured | non-collusion assumption; needs ≥ 2 live hosts |
| B. DPF of record plus optional single-server mode for small DBs (study's recommendation) | covers a wallet with one trusted host | needs re-parameterisation and benchmarks; a distinct, distinguishable wallet class; deferred to M-7 |
| C. Single-server only | no collusion assumption | ~100-1000× wallet upload [est]; hint schemes infeasible under per-sync churn; none post-quantum as shipped except FrodoPIR, the most expensive |
| D. No PIR: download whole databases | no trust in hosts | 10.7 GB slot window + 3.27 GB address set per sync at full blocks |
| E. No fixed schedule: query only when needed | single-server becomes affordable | the query pattern reveals when a wallet was paid (finding L-2, undoes SPEC-177) |

Ruling 17 takes A now and keeps B as the path (M-7).

## 6. Anticipated objections and answers

**"A trust assumption is a regression from Zcash."** Zcash light wallets today (lightwalletd
compact blocks) download all outputs and trial-decrypt; they leak timing and network address to
one server but not which outputs are theirs. Yugen does not trial-decrypt (tags and post-quantum
packages make that infeasible at scale), so some retrieval is needed. The choice is between
trusting two operators not to collude, or paying 100-1000× the wallet traffic for a single-server
scheme that, at its published parameters, is not post-quantum. The assumption is stated in the
spec, the failure is privacy only (§3), and M-7 keeps a single-server option open.

**"Two or three operators is centralisation."** Yes, at bootstrap. The DPF keeps hosting cheap,
the host list is replaceable (M-3), and any operator meeting M-1 can join; growth of the operator
set is the remedy, not a different scheme.

**"Collusion cannot be detected, so the guarantee is empty."** It cannot be detected; it can be made
costly and unlikely: different entities and jurisdictions (M-1), no retained keys by default (M-5),
public accountability (M-4), and an anonymising transport so collusion yields indices but not
identities (M-6).

**"Lattice PIR is post-quantum too."** Its assumption is; its shipped parameters are not, by the
measure Yugen uses (β ≥ 406, ML-KEM-512's primal block size): SimplePIR 326, Respire 357,
YPIR/Spiral/InsPIRe ring layer 354 [us, core-SVP, primal only, an upper bound]. Re-parameterising
raises cost further, unmeasured.

## 7. Post-quantum: a hard requirement

**Why.** Retrieval logs are a record-now-break-later target (spec §17.6): whoever keeps today's
queries and later breaks the scheme learns which records each wallet read, for its whole history.
Yugen exists to be post-quantum; a retrieval layer that a future quantum computer unwinds would
reopen exactly the history the shielded pool protects.

**How it decides.** The test is the published or shipped parameters, not the family's assumption:
- DPF: security reduces to a PRF (SHAKE256 at 256-bit seeds), where Grover at most halves the key
  length; post-quantum at the spec's parameters. The transport is hybrid with ML-KEM-1024 (§17.7).
- Single-server lattice PIR: of the schemes surveyed only FrodoPIR meets β ≥ 406 as shipped, and it
  is the most expensive (§2). The others need re-parameterisation that is neither built nor
  measured, and spec §17.6 keeps the lattice fallback **off** until it is.

So the post-quantum requirement and the traffic measurements point the same way. Caveat: our
lattice figures are a primal core-SVP model calibrated on Kyber-512 (selection §2.2), omitting dual
and hybrid attacks; the full Lattice Estimator was not run (it needs Sage).

## Lead architect's rulings on the mitigations (2026-11-24)

- **M-1 not adopted:** the project does not dictate who operates a host or where.
- **M-2 adopted:** two to three bootstrap hosts at launch; wallets pick any two.
- **M-3 adopted in part:** the host list is updatable without a node or wallet code change; no operator or jurisdiction rules are imposed.
- **M-5 adopted:** hosts do not retain DPF keys by default (devnet-only logging).
- **M-6 deferred as an enhancement:** a network anonymiser (Tor, Arti or Nym) is the ideal, not a launch requirement.
- **M-4 adopted:** hosts publish software version (reproducible build), log-retention setting and keys; wallets refuse a host whose roots disagree with the other host's.
- **M-7 adopted:** a single-server mode may be added later without a network upgrade.
- **10x reversal trigger adopted:** revisit this decision if a post-quantum single-server scheme is measured on Yugen-sized data at no more than 10x the two-server wallet traffic.
