# Referee report: private tag filtering, option (v) "slim slice"

Part of Yugen. Subject: `docs/design-private-tag-filtering.md` at `d53ea58` (draft),
read against `yugen-spec` 0.4.4 (`8359075`): SPEC-176, SPEC-177, §7.6, §9.1 to §9.3, §17.1, §17.8.
Papers checked from rendered text (pypdfium2, `.tools-venv`): [BLMG21] `2021-089.pdf` pp. 14, 19,
20; [LT21] `2021-1256.pdf` pp. 47, 52 to 54, 57. The referee's own claims below are Original
(the Ycash developers, 2026), unreviewed.

## Verdicts

| Item | Verdict |
|---|---|
| Option (v), privacy | PASS WITH CONDITIONS (M-1, M-3, m-1) |
| Option (v), correctness | PASS WITH CONDITIONS (M-2, m-2, m-3) |
| Rejection of (ii) to (iv) | PASS (two MINOR corrections, m-4, m-5) |

## 1. Unlinkability

- `nf_1` is already public in the transfer and, at 0.4.4, in every slot (§17.1). `n_j` is a public
  function of public data, so publishing it adds no information about payer or recipient. Fillers
  get an `n_j` too, so `n_j` does not separate request outputs from fillers. Confirmed.
- `itag_j` under `k` with input `LE32(asset) || n_j`: outputs to one request are unrelated to a
  non-holder unless two `n_j` collide. Honest collision: about `2^-65` per pair; over a full-block
  day (1.99 × 10^7 outputs) about 5 × 10^-6 pairs a day chain-wide, and only a collision *within one
  request's payments* links anything. Grinding does not help an outsider: forcing a collision with a
  victim's `n_j` is a 64-bit second preimage, and the only party who gains from linking two
  payments to one request already holds `k`. Confirmed.
- Re-made transfers sharing `nf_1` share `n_j` and `itag`, exactly as they share `nf_1` today; only
  one is applied and only applied outputs are in slices (§7.8). No new linkage; §9.1's stated
  residual stands. Confirmed.

## 2. Findings

**M-1 (MAJOR) The DPF domain of the slot query is unspecified, and either choice is wrong as
written.** If the database is one day's slice, the wallet tells the host which day it was paid
(covers cannot hide a real query's day unless covers name days by the same distribution). If it is
every slot since activation, host cost grows without bound (at full blocks 435 GB after a year:
about 22 core-s per query at 0.05 core-s/GB, not 0.06). *Fix:* one fixed database per sync: the
concatenation of the slices in the scan window `D − 1 … D + 7` relative to the sync's day (nine
slices, the window §9.3 already scans), indexed by global position; real and cover queries draw an
index in that one database; slots older than the window are fetched only by restore (M-3).
Cost at full blocks: about 10.7 GB per evaluation, about 0.54 core-s per query per host; state it
in §17.8's cost paragraph and in task W-4.

**M-2 (MAJOR) A holder of `k` can exhaust the slot-query budget; "DoS only" is right but the DoS is
new and remote.** Today a false match costs the holder one local commitment check. Under (v) a
payer, or anyone a shared request was shown to, can post outputs whose `itag` matches under `k`
(it computes `n_j` itself) with a wrong `cm`; each costs the victim one of `SYNC_SLOT_QUERIES`.
A flood above `72 × SYNC_SLOT_QUERIES` a day delays every genuine payment of the wallet without
bound (carry-over). No fake is ever credited: `cm` is recomputed and a path to a committed root is
required (§9.3, §7.8, R-7), so acceptance of a fake stays impossible. *Fix:* the carry queue is
fair across requests (round-robin by request, oldest first within one), so a flood through one
request delays only that request; a request whose pending matches exceed a wallet bound (say
`4 × SYNC_SLOT_QUERIES`) is shown to the user as flooded; add a `host_index.json` `sync-queries`
case "flooded request does not delay another". The flood costs the attacker fees per output.

**M-3 (MAJOR) Restore is not specified.** §17.8 item 4 requires that what a host sees is "a restore
of a chain of a given length, the same for every wallet". Fetching a restore's matches through
fixed slot queries makes restore length depend on the number of payments, and over the
whole-history domain (M-1). *Fix:* restore downloads the full 60-byte slots whole (as at 0.4.4);
only live sync uses the slim layer. State it in item 4.

**m-1 (MINOR) The match count is hidden only while matches fit the count.** With a fixed count and
carry-over the host sees the same transcript (no leak to the host); the residual is behavioural:
a carried payment's path query, and so the user's ability to spend it, comes syncs later, which a
counterparty who paid several times can observe as delayed spending. *Fix:* state it in §18.6 next
to the path-query carry; extend the owed models check of §17.8 to "paid `SYNC_SLOT_QUERIES + 1`
times".

**m-2 (MINOR) Host misbehaviour and the slim layer.** A host can serve a wrong `n_j` or `itag` in
the slim layer and so hide a payment; today it can drop a slot as well, so this is not worse, but
it is undetected. *Fix:* the wallet checks `n_j = trunc_8(H_nonce(nf_1 || j))` and the position on
every fetched slot (a mismatch is a host fault: report and use the other host), and compares a
hash of each completed slim slice between the two hosts (both serve the same public bytes).

**m-3 (MINOR) The bandwidth claim omits the query traffic.** Arithmetic checked: 14 × 23,040 =
322,560 B (323 KB); 17,240 × 1,152 × 14 ≈ 278 MB; 60/14 = 4.29; the 10-byte variant's 46 false
matches a day is right. But each slot query uploads a DPF key per host (about 584 B at the path
domain, §17.8; somewhat less over a 2^28 domain). At `SYNC_SLOT_QUERIES` = 4: 4 × 2 × 584 × 72 ≈
336 KB a day up plus 4 × 2 × 60 × 72 ≈ 35 KB down, which exceeds the slim slice itself at ten
transfers a block. Net saving there is about 1.38 MB to 0.69 MB (2×), at full blocks still 4.3×.
*Fix:* restate the table rows with query traffic and fix `SYNC_SLOT_QUERIES` before the claim.

**m-4 (MINOR, rejection of (iv)) Clue capacity understated.** The clue is per output: a two-output
232-byte transfer gains 1,912 bytes, so capacity falls to about one ninth, not one fifth. Does not
change the verdict.

**m-5 (MINOR, rejection of (iv)) Attribution.** "Nearly doubles" in [LT21] §12 (p. 57) refers to
Zcash transactions with the 133 kB clue key in addresses as text; cite the table value (clue 956 B,
Table 3, p. 53) for the clue itself.

**N-1 (NOTE) Rejections confirmed against the papers.** FMD2: DA-CCA under DLOG and Gap-DH in the
ROM ([BLMG21] Theorem 13, p. 14), so quantum-broken, retroactively given published keys; Lewis's
attacks and Table 3's trivial-attribution growth as `p` falls (pp. 19, 20) are reported as the note
says; Test 0.548 ms gives 12.6 s / 3.0 h as stated. OMR: PVW at 120 bits and BFV over 128 by the
classical estimator ([LT21] §10.1, p. 52), clue 956 B, clue key 133 kB, detection key 129 MB,
0.145 / 0.155 s per message on one thread (Table 3); 33.4 core-days per wallet per day at full
blocks checked; DoS soundness on Conjecture 8.4 (p. 47). (ii) is correctly rejected for detection.

**N-2 (NOTE)** The task brief cites the note's "O-93"; no such identifier is in `d53ea58`. The
DoS-only claim is in §4.1 and §5; M-2 addresses it.
