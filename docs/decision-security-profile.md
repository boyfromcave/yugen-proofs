# Decision record: Yugen's security profile (one level per security goal)

Part of Yugen. `yugen-proofs`, SQ-49. **Revision 2 (2026-11-19)**, after the independent
referee report `docs/security-profile-referee.md` (verdicts V1 to V8, read in full). Revision 1
(commit `cb0e173`) chose profile Y; the referee advised "adopt Y with the corrections of its
section 7". **Decision (lead agent, 2026-11-19; open to the lead architect's review): profile Y is
adopted with the referee's corrections.** This revision is the single statement of that decision:
where revision 1 and the referee differ, this text says which holds and why, and revision 1 is
superseded wherever it is not repeated here.

**Revision note (2026-11-19, after revision 2; not a rewrite).** The lead architect ruled on condition C-2 / Q-5:
the classical tree condition is read for **every `t`** ([SG26] Theorem 6.6 (2) with Definitions H.3, H.4;
`docs/decision-qrom-counting.md`). The soundness calculator's revision 9 re-solves every row at its own `k_q`. The
level-1 figures of §2.4 below change as follows (the text of §2.4 is left as written, at the revision-7 counts):
need 152.52 -> 157.0 to 158.8 bits a round; A row 8 at rate 1/4 226, 160, 163, 179 -> **233, 166, 168, 185**;
B at rate 1/8 184 -> **192**; weakest 152.37 / 152.73 -> 157.03 (A) / 158.78 (B); QROM 67.25 / 67.43 -> **69.58 /
70.45** against 64; B's root (node, 2^27 words, rate 1/8) 713,602 -> 737,947 B (E); A's and B's leaves +1.8 % to
+3.5 % (E). "Q-5 open" in §2.4 and §9 item 8 now reads "Q-5 decided: every `t`". Profile Y and the choice of
level 1 are unchanged: the costs are a few percent of proof bytes; the built rate-1/4 node (226 queries) must move
to 235 (`yugen-proof-b2`), and every build at the old counts is below its row until it is rebuilt.

**Revision note (2026-11-19, calculator revision 10; not a rewrite).** (S) proof soundness at level 1 in each system,
re-checked with the hash term of [SG26] Theorem 6.6 (2) counted (`docs/decision-qrom-counting.md` 7): **quantum
measure met, proven** (tree QROM 69.58 / 70.45 against 64; the hash part 75.63); **classical measure met on condition
H's attack rule** (256-bit digests, collision `2^128`: NIST's category-2 benchmark), **not as a proven bound**: the
hash part of a 20,000-proof tree proves 114.74 bits, a shortfall of 13.26 against 128 (the documents said 126.6). A
proven 128 would need 288-bit digests (+3.6 % to +6.2 % proof bytes, E). Options are listed for the lead architect in
7.4 there; nothing is changed. Separately, 14 of system A's 20 level-1 rows lose the label "certified" until their
`k_q` is reported by the transcript module (task T-1; guard 0.1375 bits); system B's rows keep it.

*Amendment (2026-11-19, calculator revision 10.2, after `docs/tree-extraction-referee.md`; not a rewrite):* every TREE figure in this passage is conditional, not an unconditional theorem. It holds under the recursion heuristic C2 (the event "accepted in-circuit, rejected natively" does not occur; no random-oracle proof can remove it), the owed obligations K-A and K-B (round-by-round knowledge soundness) and T-1 (the transcripts' domain separation and fit to [SG26] Protocol 6.5). Under Theorem TE' (`docs/lemma-tree-extraction.md` revision 2) the classical hash level of the tree is **121.89 bits at category 1** (185.89 / 249.89 at categories 3 / 5), printed with the per-proof union (114.74 / 178.74 / 242.74) beside it as the comparison; the tree's QROM figures are derived under C2, never "proven QROM". Status of every claim: `docs/what-is-proven.md`. In particular "quantum measure met, proven" above reads: the tree's QROM figures 69.58 / 70.45 (claimed; one-table form 76.72 / 77.60) are derived under C2, K-A, K-B and T-1; the per-proof QROM figures are proven given [SG26] Theorem I.16 (1), K-A, K-B and T-1.

Figure marks: **M** measured (source named), **C** counted (from a circuit, a layout or a
specification), **E** estimate (method stated). Computed figures are in
`profile-study/output/profile-tables.txt`, produced by `profile-study/profile_study.py` with the
calculator `soundness/` at **revision 7** as an unchanged library: sections S1 to S5 as in revision 1,
**S6 to S9 added for this revision** (commits `d5a8108`, `eda3813`). Run: `cd soundness && uv run
python ../profile-study/profile_study.py`.

Inputs read for revision 2: the referee report in full; revision 1 and its study; `yugen-spec`
`c9e38a3` (specification **0.3.4**: §3.3, §5.4 l. 543, §6 l. 614, §7.3, §8.1 l. 822, §11.2 C3.i,
A.1 l. 3007, A.3, checked where this record restates a referee finding); `yugen-proof-b2`
`b8871ff` `docs/parameters.md` §8.3, §10.2 to §10.4, `docs/statement-layout.md` §1 and task L-1,
`docs/wallet-memory.md` §4; `yugen-proof-a` `4654f15` `docs/parameters.md` §2.5. Revision 1's
inputs as listed there (commit `cb0e173`).

Sources in the reference-paper collection (REFERENCES.md) (text layer):

- **[CFP]** NIST, *Submission Requirements and Evaluation Criteria for the Post-Quantum
  Cryptography Standardization Process* (December 2016), §4.A.5 pp. 16 to 19 (categories,
  footnote 2, MAXDEPTH 2^40 "in a year" to 2^96, the gate table of p. 18), §4.A.6.
- **[FIPS204]** NIST FIPS 204, §4 Table 1 and **Appendix D.1 (PDF p. 64), re-read for this
  revision**: "a collision attack against SHAKE256 with a 384-bit output would make it so that
  parameters targeting NIST security strength category 5 could only meet category 4" (quoted).
- **[FIPS205]** FIPS 205, §11 Table 2, §11.2.2.
- **[COSE-FN]** Prorock, Steele, Tschofenig, draft-ietf-cose-falcon-05, §1 Table 1.
- **[GLS26]** Günther, Lyubashevsky, Schmidt, *FALCON with message recovery, a specification*,
  ePrint 2026/420: abstract, §1, §1.1, Algorithms 1 to 4, Lemma 1.
- **[SG26]** Sharp, Grubbs, *Faster and Smaller Anonymous Credentials from Standardized
  Signatures*, ePrint 2026/2615: Theorem 6.6 (2) to (4), through the calculator; Section 6.2,
  6.3 and Appendix I.1 re-read for `qrom-compilation.md` §2.8 in this pass.

**Not in the folder, marked "from memory" wherever used:** FIPS 202 (SHAKE256 / SHA3 capacities
and security claims: **not verified**), FIPS 203 (ML-KEM sizes and levels), FIPS 206 / the Falcon
specification, FIPS 180-4, RFC 9861 (TurboSHAKE), Brassard–Høyer–Tapp, Grubbs–Maram–Paterson
(ML-KEM anonymity), the Micciancio–Walter bit-security measure, phone and browser memory limits.

---

## 0. The decision, findings first

### 0.1 Profile Y as adopted

| Goal | Level (honest NIST label) | Mechanism | Main cost |
|---|---|---|---|
| (P) privacy, long-lived secrets | **5**, conditional on a seed of at least 256 bits of entropy (§2.1, R-5) and, for zero knowledge, on `ε_hvzk` (open in both systems) | ML-KEM-1024 (packages, addresses, hybrid transport); DPF with 256-bit seeds under a **named** PRG (W-4); seed-entropy rule; leaf salts 80 B (A) / 96 B (B), proof salt 80 B, from a `2^-128` target over the **lifetime** proof count `Q = 2^37` | +480 B a package, +384 B a full address, +41% mailbox bytes, DPF keys about 2× (E5 to be re-measured with the named PRG) |
| (B) binding | **4** for the offline set (collision search on a 384-bit SHAKE256 output: the category-4 case of [FIPS204] App. D.1) | 48-byte outputs for `cm`, `nkc_d`, the note-tree leaf and nodes, `anchor_root`, the exit registry, **`rho`**, **the transfer hash**; the duplicate-commitment wallet rule; the window-bound statement layer (`lpi`, bundle digests, `bstmt`, system A's 32-byte public input) **stays 32 bytes** | B's wallet statement at `2^18`; +32 B a transfer record; capacity 4,345 to 4,405 a block at 4 MB (S6) |
| (A) spend authorisation | **5 against everyone outside the wallet's own devices; 1 against a compromised proving device** (split custody); recovery mode 5 (hash only) | Falcon-512 with the key hidden in `sig_d`; scheme `0x02` (Falcon-1024) **reserved with the six readiness items of §2.3 in the specification** | none now; a later release costs A's wallet stack `2^22` → `2^23` |
| (S) proof soundness | **1** in each of two independent systems; generic forgery confined to the anchor window **after F-1** | rows of revision 7; Keccak-256 (A) and BLAKE3 (B) proof trees; `GF(2^256)`; **F-1: the block hash at the anchor height in the transfer hash, anchors below activation refused** | F-1 is a consensus rule (no circuit change); E2 at 12 to 15 hosts (10 to 11 after B's named reductions) |
| (L) liveness, abuse | as (P) | DPF λ = 256 with the named PRG; X25519 + ML-KEM-1024; lattice PIR off | as (P) |

Note-tree hash (a one-way door, §3.5): **default FIPS SHAKE256 with a 384-bit output**; its
shape (4-ary two-block T1, or binary framed one-block T1b) is fixed by task F-2's counts; a
non-FIPS sponge (TurboSHAKE256 T2, or Keccak-f[1600] at capacity 384 T3) only if F-2 shows the
FIPS form cannot meet the phone memory limit, and then as a recorded exception.

### 0.2 Findings

1. **Statements are not always fresh (V1, R-1).** Revision 1 said every soundness forgery must be
   found inside the 96-block anchor window. As specification 0.3.4 stands that is false: below
   activation the root is the constant `E_20` (spec §6 l. 614), the anchor rule `h_a mod 16 = 0,
   1 ≤ h − h_a ≤ 96` (§8.1 l. 822) does not mention activation, the first post-activation root is
   a constant, and the root does not change in any stretch without applied outputs (a pause, a
   quiet network). A forgery against such a root can be computed offline as soon as a release
   fixes the activation height and branch ID. **Fix F-1, adopted:** the hash of block `h_a`
   enters the transfer hash of every non-canary transfer (hence P7 `m`, absorbed before any
   challenge in both systems), and anchor heights below the activation height are refused. Only
   with F-1 does the window argument hold, and the 32-byte statement layer (item 3) depends on it.
2. **A break is rate-limited, not bounded (V2).** The outflow caps limit what leaves the pool
   **a window** (`K`), not in total: a forger who breaks soundness in both systems, or finds a
   binding collision, and claims no canary drains the pool at `K` a window until a release
   freezes it; nothing detects it automatically. What separates (S) from (B) is **online versus
   offline** (a fresh statement forces the search after the block exists, F-1; a binding
   collision can be prepared for years) and **repairable versus not** (a soundness row is raised
   by a release; a binding digest is fixed in every note already made).
3. **Binding set corrected (V4).** Added: `rho` at 48 bytes **and** the wallet and host rule
   "a commitment equal to an earlier applied commitment is never credited" (R-2, Faerie gold
   through `H_rho` over a free dummy `dx`); the transfer hash at 48 bytes (R-3, host-chosen
   collisions under split custody). Moved to 32 bytes, labelled window-bound: `lpi`,
   `bundle-list`, `bundle-kids`, `bundle-node`, `bstmt` (their inputs start from fresh public
   inputs once F-1 holds) and system A's `E_A(pi)` and Keccak-256 statement wrappers, which are 32
   bytes regardless (spec A.1 l. 3007: "256 public bits").
4. **Spend authority relabelled (V5).** Falcon-512's level matters only against a device that holds
   `pk` and the other spend secrets (a compromised prover in split custody), and there it is
   level 1 with no window, for every address of the account. "Scheme `0x02` reserved" needs six
   specification items before launch (§2.3).
5. **Privacy gaps closed (V6).** A seed-entropy rule (≥ 256 bits: 24 words or 32 random bytes); a
   named PRG for the DPF at 256-bit seeds; `ε_hvzk` stated as open in both systems; salt floors at
   the lifetime proof count `Q = 2^37`: leaf 79 B (A), 79 B (B), proof salt 74 B (against 2^256)
   or 78 B (against [CFP]'s 2^272 gates). The chosen 80 / 96 / 80 B stand (S7).
6. **Feasibility restated (V7; S6, S8, S9).** `LEAF_RESERVE` from measured leaves plus counted
   deltas is 1,389,000 B; with the larger of measured and calculator on each side 1,403,000 B,
   which is the provisional value until W-3 measures Y's leaves (capacity 4,345 transfers a block
   at `W` = 4 MB). B's wallet memory at `2^18` after the named reduction steps is about **2×**
   E1's 512 MB (956 to 965 MB, E), not 4×. The TurboSHAKE256 fallback keeps B at `2^17` by about
   148 committed words only (S9). System A's node layout must keep every 16-byte cell inside one
   block (T1 needs an aligned layout; T1b has none to fix).
7. **Tree-hash variants priced (V8, S9; task F-2 counts them in circuit).** Per transfer in B:
   T1 and T1b 48,000 AND rows of tree hashing (B at `2^18`), T2 24,000 (stays `2^17`, 148 words
   free), T3 31,200 (`2^18` unless L-1 frees about 7,000 words). A block weight of 4.18 MB
   (4,172,711 to 4,186,711 B) restores revision 1's 5,150 transfers under Y; it is an option for
   the lead architect, not taken here.
8. **Unchanged from revision 1:** category-3 soundness does not fit (no bundle at 4 MB, 33 to 45
   hosts); W4 is broken by today's measured leaves (1,293,640 B against 1,150,000) and W-1
   repairs it; message recovery ([GLS26]) does not help Yugen; Falcon-1024 stays a later release
   because it doubles A's wallet prover for split custody only.

### 0.3 Revision 1 against the referee: what changed where

| Verdict | Applied in | Disagreement |
|---|---|---|
| V1 anchor window; R-1; F-1 | §1.1, §2.4, task F-1 | none |
| V2 gain of a break | §1.2, §4 | none |
| V3 shared parts | §2.4 | one: system A's 32-byte public input is a per-system part (a collision there fools A only, as the referee's own §2.3 says), so it is listed with A's own parts, not among the shared ones |
| V4 binding set, label | §2.2 | none on substance; `rho` takes both fixes (48 bytes and the wallet rule), since W-2 opens the spec anyway and B is at `2^18` under Y regardless, which is the referee's own condition for (b) |
| V5 Falcon label, `0x02` | §2.3 | none |
| V6 privacy | §2.1 | none; the PRG is named here (AES-256 keyed by the seed), to be confirmed by W-4's measurement |
| V7 feasibility | §3.3, §3.4, §3.5 | minor: B at `2^18` after steps a and b is 956 to 965 MB by the same proportion (S8), the referee's 1.0 to 1.2 GB; both are about 2× |
| V8 alternatives | §3.5, §5 | none; one variant added (T1b, the binary framed node) |

---

## 1. Method

The goals are taken separately because they fail differently:

| Goal | What a break gives | When the attack can be prepared | Who can respond |
|---|---|---|---|
| (P) privacy | reading or linking recorded data | any time after publication ("record now, break later") | nobody: the data is out |
| (B) binding | inflation or a double spend that **both** systems prove (the statement is true) | **offline**, for any time before the colliding note is inserted | the caps rate-limit outflow (`K` a window); nothing detects it; **not repairable** for notes already made |
| (A) spend authorisation | theft from one account | needs the spend secrets; against a compromised prover, offline key recovery from `pk` | the victim, by moving funds to a new account; the network, by recovery mode |
| (S) soundness | a false statement accepted: counterfeit | **online after F-1**: after block `h_a` exists, in both systems; before F-1 offline for `E_20` and quiet stretches | canaries (only if the forger claims), the pause, a release that freezes and re-parameterises; **repairable** going forward |
| (L) liveness, abuse | linking reads; denial of service | when recorded, or live | as (P) for recorded reads |

### 1.1 Freshness of statements (corrected; V1, R-1, F-1)

Every proof absorbs the verifying key, the circuit identifier and all public inputs before its
first challenge (spec §11.1, A-3, A.3), so a Fiat–Shamir forgery cannot start its challenge search
before the statement is fixed. Revision 1 then assumed the statement is unknown until a recent
block. As specification 0.3.4 stands it is not (the referee's §1.1 table, checked against the
spec lines cited in §0.2): P1 `anchor_root` repeats whenever no output was applied, is `E_20`
below activation and a computable constant just after it; P2 to P6 are the prover's choice
(dummy `dx` is free witness, spec C3.i); P7 `m` is fresh exactly when the root is; P8, P9 are
constants or change rarely; the proof salt is the prover's.

**F-1 (adopted).** `transfer_hash = H_transfer(... || LE32(anchor_height) || anchor_root ||
anchor_block_hash || ...)` (376-byte body, per the referee's layout) for every transfer without a
canary flag; anchor heights below the activation height are refused. P7 is computed from it by
the verifier and absorbed before any challenge in both systems and both modes, so every
non-canary statement is unpredictable until block `h_a` is mined, including in quiet stretches.
No circuit changes (P7 is already a 64-byte public input; nothing in circuit reads the transfer
hash). Canary claims keep constant roots and no block hash, so they stay the cheapest generic
target and the incentive points at firing them. The miner of `h_a` learns it one block early,
inside the window. A hardware signer cannot check the block hash, as it cannot check the anchor
root today (spec §7.7). **Provenance:** Original (the Ycash developers, 2026; first in
`security-profile-referee.md` §1.3; `REFERENCES.md` O-56), relates to SPEC-19's anchor binding;
unreviewed.

**With F-1**, the cost of a *generic* forgery inside the 7,200-s window: classical 2^128 calls is
2^115.2 calls a second (C); quantum, [CFP] p. 17 sets MAXDEPTH at 2^40 for "a year", two hours is
2^27.9 of that, and [CFP] p. 18's AES-128 formula (2^170 / MAXDEPTH) read at that depth gives about
2^142 gates (E: an extrapolation below the range NIST lists; Adapted from [CFP], change: the depth
only). It does nothing against a non-generic break (a soundness bug), which needs no window; that
is what the second system and the canaries are for.

### 1.2 What a break gains (corrected; V2)

Counterfeit notes are indistinguishable from honest ones. Withdrawals are limited to `K` a window
(spec §13.3.5); maturing outputs are voided only in frozen mode, entered by a canary, by a
single-system claim while the other system's break stands, or by a release (§13.3.8). A forger
who breaks both systems (or holds a binding collision) and claims nothing fires none of these: it
drains the pool balance, up to `RATCHET_CMAX`, at `K` a window, until people notice unusual
withdrawals, miners signal a pause and a release freezes the pool. The turnstile stops only at
`B = 0`. So both (S) and (B) breaks are "the whole pool, at most `K` a window, until a release
freezes it"; the incentive constraints R1 to R3 hold for one window at the provisional values
(spec §13.3.1). The difference between the goals is when the attack can be prepared and whether
the damage can be repaired (table above), and that is why binding is placed higher.

### 1.3 Labels

Levels are NIST's per goal ([CFP] §4.A.5): categories 1, 3, 5 are key search on AES-128/192/256
(2^143 / 2^207 / 2^272 classical gates, 2^170 / 2^233 / 2^298 divided by MAXDEPTH quantum, p. 18);
categories 2 and 4 are collision search on 256- and 384-bit hashes (2^146, 2^210 classical; no
quantum figure for collisions). "Category 4" for a 384-bit SHAKE256 output is NIST's own reading
([FIPS204] App. D.1, quoted above). Category 2 has no meaning for soundness: a forgery is a search
problem that Grover speeds up, so the soundness levels are 1, 3, 5. No headline category is given
to the profile.

---

## 2. Goal by goal

### 2.1 (P) Privacy and long-lived secrets

| Component | Level in Y | Mechanism | Cost | Proven / conjectured |
|---|---|---|---|---|
| Note packages, full addresses (spec §4.3, §10, §12.1) | 5 | ML-KEM-1024, ChaCha20-Poly1305 under `H_pkg-key` | ek 1,568 B, ct 1,568 B, dk 3,168 B (from memory); package 1,658 / 2,170 B; mailbox entry 1,656 B (S5) | Module-LWE at level 5 (FIPS 203, from memory); ciphertext anonymity (Grubbs–Maram–Paterson, from memory: to be read when added) |
| Transport (plan §6) | 5 | X25519 + ML-KEM-1024 | +384 B and +480 B a handshake (from memory) | as above |
| Private retrieval, two-server DPF | 5 **with the PRG named** | λ = 256 seeds. **PRG (named here, R-4):** length-doubling by AES-256 keyed with the 256-bit seed in counter mode, `G(s) = AES-256_s(0) ‖ AES-256_s(1) ‖ AES-256_s(2) ‖ AES-256_s(3) ‖ AES-256_s(4)` cut to two child seeds and two control bits; ChaCha20 keyed with the seed is the measured alternative | key about 584 B (E); tag lookups about 28.6 KB a day against E5's 50 KB (S5, E); server PRG work **not established** (a key schedule a node; the 128-bit crate `dpf-fss` 0.6.1 uses a fixed-key AES-256 Hirose PRG): W-4 measures it | PRG security of AES-256 as a pseudorandom function (standard reasoning, from memory; category 5 by [CFP]'s AES-256 benchmark); the DPF construction as published (BGI16 via `pir-selection.md`, not re-read) |
| Single-server lattice PIR fallback | off | until re-parameterised against the level-5 lattice estimate | none | — |
| Keys, PRFs, `nk_d`, `salt_d`, `rk_d`, nullifier PRF, tags (spec §4) | 5 **if the seed has ≥ 256 bits of entropy** | 256-bit secrets, framed SHAKE256; **seed-entropy rule (R-5):** the seed carries at least 256 bits of entropy (a 24-word mnemonic or 32 random bytes); wallets refuse to generate a shorter one and refuse 12-word mnemonics on import | 0 | key search ([FIPS205] §11.2.2 keeps 256-bit `F`, `PRF` at category 5); with a 128-bit seed every derived key is category 1 ([CFP]'s definition) |
| Zero knowledge of leaf proofs | statistical, **conditional on `ε_hvzk`** (open in both systems; obligations Z-A1 to Z-B6 of spec A.3) | target `2^-128` over **`Q = 2^37`** leaf proofs (50 years at Y's capacity: 2^22.3 a day, 2^34.1 in ten years, 2^36.4 in fifty, S7, C), excluding `Q ε_hvzk`: floors A 79 B, B 79 B, proof salt 74 / 78 B; **chosen A 80 B, B 96 B, proof salt 80 B** | A leaf +11,648 B, B leaf +32,002 B (E, revision 7) | [SG26] Theorem 6.6 (3), (4) (Published); `Q` corrected from the calculator's `POOL_LOG2 = 20` (`category.py` l. 52), which Theorem 6.6 (3) does not permit for a permanent record |
| Outgoing and incoming tags (8 and 6 bytes) | 5 | keys of 256 bits; truncation gives false positives only | 0 | |

**The salt-term reading.** The proof-salt term of [SG26] Theorem 6.6 (3) is `4 Q t / 2^(4 b_s)`,
so its work over advantage is `t / ε = 2^(4 b_s − 2 − log2 Q)`, independent of `t`: at 80 bytes
and `Q = 2^37`, 2^281, above AES-256's 2^256 and [CFP]'s 2^272 gates. Reading work over advantage
for a distinguishing game is conservative against the Micciancio–Walter measure, which divides by
the square of the advantage (from memory). Margins at `Q = 2^37` (S7): A's leaf salt 1 byte, B's
17 bytes, the proof salt 2 bytes against 2^272. Theorem 6.6 (4) (no query bound) gives
`2^-150.8` (A) / `2^-148.7` (B) at `2^20` (S2) and stays below `2^-128` at `2^37`.

**Where privacy is not covered:** `ε_hvzk` of both systems; timing and network metadata (plan
§9); the wider Ycash system's transparent and vault addresses (FN-DSA-512, SLH-DSA-SHA2-128s,
category 1 by name, [FIPS205] §11 Table 2) bound any coin that crosses them.

### 2.2 (B) Binding of the statement

**Label and its source.** A collision on a 384-bit output costs 2^192 calls generically, the
category-4 benchmark ([CFP] p. 17: "collision search on a 384-bit hash function"; 2^210 classical
gates, p. 18). That a **SHAKE256** output of 384 bits is exactly the category-4 case is NIST's own
reading in [FIPS204] Appendix D.1 (p. 64, quoted in the sources above; re-read for this
revision). The generic sponge bound (SHAKE256's capacity 512, `min(d/2, 256)` collision claim) is
**from memory (FIPS 202, not in the folder, not verified)**; App. D.1 is consistent only with the
capacity not lowering the 192-bit bound. No binding digest uses Keccak-256 (that is system A's
proof-internal hash and wrapper, which is soundness). A Keccak sponge with capacity 384 also gives
192 bits generically (from memory), so 48-byte binding does not by itself require a FIPS function;
the FIPS default is a choice (§3.5).

**The set (Original classification, the Ycash developers, 2026; revision 1's O-50 corrected by the
referee's §2.3; unreviewed):**

| Digest | Length in Y | Why |
|---|---|---|
| `cm`, `nkc_d`, note-tree leaf and nodes, `anchor_root` | **48** | offline: both inputs chosen by the attacker, no fresh value. A collision is inflation or a double spend that both systems prove |
| `reg-leaf`, `reg-node`, `reg_root` | **48** (mode 1) | offline: an attacker grinds `rk_d` until its tags are adjacent and controls those range leaves; a single collision `(lo, hi) = (0…01, ff…fe)` is a universal false non-membership. Mode 0 unaffected |
| `rho` (`H_rho`) | **48**, plus the credit-once rule | R-2: `rho_j = H_rho(nf_1 ‖ j)` (spec §5.4); for a dummy first spend `nf_1 = H_nf-dummy(dx)` with `dx` free witness (spec C3.i), so an offline search for `dx ≠ dx'` with equal `rho` gives two identical commitments to one victim at two positions with one nullifier; a recipient crediting both loses one. 48 bytes put the search at category 4; the rule "**a commitment equal to an earlier applied commitment is never credited**" (wallet and host, normative) closes it completely, since only the recipient is harmed. Cost (the referee's count, to be confirmed in W-3): one permutation either way for `rho`, `cm` stays two permutations, `nf` stays one, about 8 committed words in B |
| transfer hash (`H_transfer`) | **48** | R-3: under split custody the online host chooses the bytes the offline signer cannot check (anchor root and height, and after F-1 the block hash) and builds the transfer it broadcasts; a collision between a transfer the signer accepts and one paying the host is host-chosen. Falcon's nonce salts the hash of `m`, which is a function of the colliding transfer hash, so it does not help. No circuit cost (computed by nodes and signers; `m` stays 64 bytes); `yugen-falcon`'s `message_digest` input goes from 64 to 80 bytes and its vectors are regenerated |
| `lpi`, `bundle-list`, `bundle-kids`, `bundle-node`, `bstmt` | **32**, labelled **window-bound** | every input starts from fresh public inputs (`pi` begins with `anchor_root`; with F-1 `m` is fresh), so a collision must be found after the transfers exist, like a soundness forgery. **Depends on F-1.** Consistent with system A, which binds them through a 32-byte value anyway |
| system A's `E_A(pi)` (SHAKE256 to 32 bytes) and its Keccak-256 statement wrappers (spec A.1) | **32** (forced) | leanVM proofs carry 256 public bits (spec A.1 l. 3007). Window-bound like the row above; a collision fools A only (B absorbs the 36 words of `pi` directly, A.2), so the pair still covers it |
| `nf`, `auth_d`, `sig_d`, `rid`, `rcm`, short address, `proof_hash`, `exit`, `exit-tag`, `tout_hash`, `dep_sighash` | 32 | second-preimage cases, the owner's own collisions, or digests that carry the transfer hash (the referee's check, §2.3, agreed) |

**Cost in the wallet circuits (S3, S9):** the tree is the cost. A +40 Keccak-f a transfer (stays
`2^22`, words not counted: task P-2); B +24,000 AND rows (600 a Keccak-f, C):
112,710 → 136,710 > 131,072, so B's leaf goes to `2^18` under any FIPS tree. Transfer record
200 → 232 B; anchor-table entry 65 → 97 B; `pi` 281 → 345 B (still 3 Keccak-f for `H_leaf-pi`).

**Choice: level 4 for the offline set.** It is the goal whose weak level cannot be repaired by a
later parameter release, and the two-system design gives it no protection.

### 2.3 (A) Spend authorisation (relabelled; V5)

A real spend's witness is `h` (the key), `nk_i`, `rho_i`, `rcm_i`, `pos_i`, the path, `salt_i`,
`rkh_i`, and in mode 0 the signature (spec §11.2); `auth_d = H_auth(rkh_d ‖ H_sig(0x01 ‖ pk ‖
salt_d))`; `salt_d` comes from `saltm` and `rkh_d` from `rkm`, neither in any viewing key (§4.5).

| Attacker | Needs beyond what it has | Barrier | Level |
|---|---|---|---|
| Outsider, or a full-viewing-key holder, even with a leaked `pk` and a Falcon break | `salt_d`, `rkh_d` (256-bit secrets); outsiders also `nk_d` | preimage / PRF key search | **5** (key search on 256-bit secrets; with the seed rule of §2.1) |
| A compromised proving device (the online half of a hardware wallet, a delegated prover) | the Falcon signing key only | Falcon-512 key recovery from `pk` (offline, no window, permanent, every address of the account: one key per account, SPEC-5) or forgery | **1** ([GLS26] §1) |
| The signing device itself | nothing | — | — |

**Label: "5 against everyone outside the wallet's devices; 1 against a compromised proving
device."** The threat Falcon's level answers is split custody. A wallet that suspects its prover
moves funds to a new account (a new `falcon_seed` path). A per-address-group key is a wallet-level
option at no circuit cost (each address commits to its own `pk`; a transfer's two spends must
share one). **Provenance:** the split-custody reading is Original (the Ycash developers, 2026;
`security-profile-referee.md` §3.1, O-61), superseding O-41's "1 behind 5"; unreviewed.

**Falcon-1024 stays a later release:** it makes A's wallet prover `2^23` (E) while A at `2^22`
already measures 622 to 894 MiB (M, plan step 0.10) against 512 MB; in Y its marginal cost in B is
nil (B is at `2^18` anyway). The lead architect's choice is split-custody security against A's
wallet memory; this record keeps Falcon-512 at launch.

**What "scheme `0x02` reserved" must contain in specification 0.4** (none is in 0.3.4; each so that
`0x02` is a release and not a redesign):

1. **Registry:** an identifier `sig-1024` with body 1,826 B (`1 + 1,793 + 32`); `0x12 sig` has a
   fixed 930-byte body today (§3.2).
2. **Key path:** a `falcon_seed` derivation with the scheme in the path (`0x04` derives one key per
   account today).
3. **Scheme on the wire:** a reserved flag bit of §7.1 (bits 9 to 15) or a statement version names
   the scheme; A-4's identifiers gain a scheme dimension (the verifier picks a leaf circuit by P8
   only, §11.1.1).
4. **Bundles:** BC-1 verifies each leaf "against the leaf verification key of mode M"; either a
   per-leaf key choice among consensus keys or single-scheme bundles, decided before the recursion
   slots are built.
5. **Migration:** after a switch the `0x01` circuit stays live (two anonymity sets) until a
   migration deadline, after which unmigrated notes leave by mode 1 or the hash-only exit. Revision
   1's "one switch at a height, as mode 1 is" does not work: mode 1 can switch because every
   address already has `rk_d`; a `0x01` note opens only under its Falcon-512 key.
6. **Circuits counted and tested:** the 128 known-answer vectors at 1024 (`yugen-falcon` `da7988f`)
   prove in both test builds (task A-1).

### 2.4 (S) Proof soundness, per system and for the pair

| Level | Rows (revision 7, tree of 20,000, no grinding, unique decoding) | Leaf / node sizes | E2 hosts (E) | Proven / conjectured |
|---|---|---|---|---|
| **1** (chosen) | 152.52 bits a round; A row 8: 226, 160, 163, 179 at 1/4; B: 184 at 1/8; weakest 152.37 (A) / 152.73 (B); QROM 67.25 / 67.43 against 64 | A leaf 704,152 (M + delta), B leaf 666,112 to 679,687 (S6); A root 875,309 (M), B root 713,602 (E) | 12 to 15; 10 to 11 after B's D-6, K = 7 or 15 and the cap layer | classical bound proven (book Theorems 25.2.1, 31.2.1, BCIKS20 unique decoding; tree accounting O-13, unreviewed); QROM bound [SG26] 6.6 (2) to 2^64 queries, for the transcripts as specified (the builders' deviations: `qrom-compilation.md` §2.8); the quantum half beyond that is the Grover estimate G; Q-5 open |
| 3 | 216.52 a round | leaves about 1,043 to 1,066 KiB; nodes 1,118 to 1,249 KiB | 33 to 45 | same theorems; QROM to 2^96 only |
| 5 | 280.52; `GF(2^384)` at least | nodes 2.0 to 2.3 MiB: W1 fails | 57 to 82 | needs a new field in both systems |

**What the pair buys: one bit against a generic attacker** (about 2^129 for both forgeries on one
statement), and independence against a non-generic failure of one system: a soundness error in its
proof or implementation, a conjecture failing, a structural attack on its Merkle hash (Keccak-256 in
A, BLAKE3 in B), an arithmetic flaw of its field construction, a collision in its own statement
digest (system A's 32-byte `E_A(pi)` is such a per-system part: it fools A only).

**What the pair does not cover, because it is shared (complete list, V3):**

1. the statement and its binding digests (§2.2), including the transfer hash and P7;
2. the specification itself;
3. Falcon (one signature scheme behind both circuits);
4. the compilation argument: both rest on [SG26] Theorem 6.6, on **one calculator** and **one
   tree-accounting argument** (O-13) that certify both rows;
5. the Fiat–Shamir stream function (SHAKE256 in both spBCS transcripts), so a structural break of
   Keccak's pseudorandomness reaches both;
6. **Reed–Solomon unique-decoding proximity** (BCIKS20) under both soundness proofs;
7. the generic `n / |F|` terms of a 256-bit field (different constructions, same size);
8. **the bundle statement digests of spec §15.3** (`lpi`, `bundle-list`, `bundle-kids`,
   `bundle-node`, `bstmt`), common to both systems' bundle proofs.

The canaries detect only a forger who chooses to claim; after F-1 a generic forger with bounded
parallelism finds a canary (constant roots, offline-precomputable by design) cheaper than a real
mint, so the incentive points at firing it.

**Choice: level 1 per system, generic rows, with F-1.** Category 3 rows are a release once E2 and
the block weight allow them (§6.4).

### 2.5 (L) Liveness and abuse

DPF seeds and transport are in (P). Denial of service is bounded by fees and block rules, not by a
category.

---

## 3. Options priced

### 3.1 The real-world limits

E1 (plan §11): A leaf ≤ 530 KiB, B leaf ≤ 576 KiB, 10 s on a flagship phone, 512 MB a prover. Node
proofs ≤ 1,835,008 B (W1). Block: W2 to W5 with `W` = 4,000,000. E2: 1,500 leaves merged in 60 s on
8 hosts of 16 cores. **No phone measurement exists** (plan step 0.15 not started); prove times are
one Apple M5 thread.

### 3.2 The options (S4, unchanged from revision 1; E unless marked)

| Option | Leaf pair (B) | `LEAF_RESERVE` | Roots A + B | W1 | Record | Transfers at 4 MB | `W` for 6,000 | E2 hosts | Wallet stacks |
|---|---|---|---|---|---|---|---|---|---|
| O1 category 1 as built | 682,787 + 635,909 | 1,337,000 | 875,309 + 713,602 | yes | 200 | 5,370 | 4.13 MB | 12 to 15 (10 to 11) | A `2^22`, B `2^17` |
| O2 referee P6 | 694,435 + 667,911 | 1,381,000 | same | yes | 200 | 5,150 | 4.17 MB | same | same |
| **O3a = Y** | 694,435 + 679,687 (calculator) | 1,393,000 (calculator; **1,389,000 to 1,403,000 corrected, §3.3**) | same | yes | 232 | 4,388 (**4,345 to 4,405**) | 4.37 MB | same | A `2^22`, **B `2^18`** |
| O3b O2 + Falcon-1024 | 701,699 + 679,687 | 1,400,000 | same | yes | 200 | 5,055 | 4.19 MB | same | A `2^23`, B `2^18` |
| O3c O2 + both | 701,699 + 679,687 | 1,400,000 | same | yes | 232 | 4,358 | 4.38 MB | same | A `2^23`, B `2^18` |
| O4 the study's M-1 | 1,092,578 + 1,125,569 | 2,237,000 | 1,278,504 + 1,144,436 | yes | 232 | **0** | 6.05 MB | 33 to 45 | A `2^23`, B `2^18` |
| O5 category 3 throughout | 1,075,378 + 1,103,465 | 2,197,000 | same as O4 | yes | 232 | **0** | 6.01 MB | 33 to 45 | A `2^23`, B `2^18` |
| O6 category 5 throughout | 1,761,111 + 1,854,208 | 3,634,000 | 2,155,687 + 2,043,737 | **no** | 264 | 0 | 9.42 MB and W1 | 57 to 82 | A `2^23`, B `2^18` |

Feasibility as in revision 1: O1 to O3c fit with named engineering (W-1, E1 memory steps, E2
reductions); O4 and O5 fail W5 at 4 MB; O6 fails W1.

### 3.3 `LEAF_RESERVE` and capacity, corrected (S6; V7)

The calculator puts A's row-8 leaf 9,717 B under the measured one, and B's 13,575 B over a
measured-plus-deltas figure:

| Leaf | Calculator (E) | Measured plus counted deltas |
|---|---|---|
| A, row 8, 80-byte leaf salt, `2^22` | 694,435 | **704,152** = 692,504 (M, `yugen-proof-a` parameters §2.3) + 11,648 (salt 64 → 80 B, E) |
| B, form T, 96-byte salt, route S, `2^18` | 679,687 | **666,112** = 583,680 (M, `yugen-proof-b2` §8.3) + 23,552 (salt, C) + 47,104 (route S, spec figure) + 11,776 (one level, E) |

| Basis | `LEAF_RESERVE` | Transfers a block at 4 MB | `W` for 5,150 | `W` for 6,000 |
|---|---|---|---|---|
| calculator on both sides (revision 1) | 1,393,000 | 4,388 | 4,176,711 | 4,373,911 |
| measured plus deltas on both sides | 1,389,000 | 4,405 | 4,172,711 | 4,369,911 |
| **the larger on each side (provisional value)** | **1,403,000** | **4,345** | 4,186,711 | 4,383,911 |

`LEAF_BYTES_RESERVE` with two long ML-KEM-1024 packages is 18,416 B. The provisional value takes
the larger figure on each side so that no valid Y leaf pair is refused before Y's leaves are
measured; W-1 replaces it by the value derived from W-3's measured leaves.

### 3.4 B's wallet memory at `2^18` (S8; V7)

The measured category-1 form-T leaf peaks at 1,095 to 1,106 MB for the whole process (M,
`yugen-proof-b2` §8.3). At the pin, steps a and b took 1,270.5 MB to 554.4 MB
(`wallet-memory.md` §4, dev run). At `2^18` by the same proportion: **956 to 965 MB, about 1.9×
E1's 512 MB** (E); the referee's 1.0 to 1.2 GB is the same order. Revision 1's "about 4×" was the
unreduced process doubled (2,190 to 2,212 MB). wasm32 linear memory never shrinks
(`wallet-memory.md` §5). A at `2^22` (622 to 894 MiB, M) misses E1 too: Y doubles B's share of the
memory problem, it does not create it. Whether 1 to 2 GB is feasible on a phone is not known
(no device figure; plan step 0.15 not started; foreground limits of several GB on flagships are
from memory): task W-7 moves the device measurement ahead of the spec freeze.

### 3.5 The note-tree hash: variants priced (S9; V8; one-way door)

Every note ever made hashes under the tree function, so it is fixed once. Counts per transfer
(two spends), B's rows from `yugen-proof-b2` `docs/parameters.md` §10.4 (C: Keccak-f 600, SHA-512
compression 920; BLAKE3 168 to 192, SHA-256 364, Keccak-256 600 for 32-byte digests); a
Keccak-p[1600,12] at half a Keccak-f and one committed word a row of a permutation (E, the
referee's rule), plus the sibling words over today's 1,920 path bytes:

| Variant | Standard | Depth | Perm. a level | Tree AND rows (B) | B AND rows | B committed words (E) | B stack | Path bytes a spend | A |
|---|---|---|---|---|---|---|---|---|---|
| T0 as built: SHA3-256, 4-ary, 32 B (category 2) | FIPS 202 | 20 | 1 | 24,000 | 112,710 | 130,684 (C) | `2^17` | 1,920 | 24 cycles a level (M) |
| **T1** SHAKE256-384 (or SHA3-384), 4-ary, 197-byte node | FIPS 202 | 20 | 2 | 48,000 | 136,710 | 154,924 | `2^18` | 2,880 | two KECCAK rows a level; **needs an aligned two-block layout** (a 16-byte cell straddles the 136-byte boundary otherwise, about 1,000 cycles a level unaligned against A's 39,600-cycle headroom) and §3.3's separation redone |
| **T1b** SHAKE256-384, binary, framed node `Yg 00 id l ‖ 0^11 ‖ c0 ‖ c1` (16-byte frame first, 112 bytes) | FIPS 202 | 40 | 1 | 48,000 | 136,710 | 154,684 | `2^18` | 1,920 | one KECCAK row a level; both children whole cells (bytes 16, 64); separated as a framed call by its `id` |
| T1c SHA-384, binary | FIPS 180-4 | 40 | 1 | 73,600 | 162,310 | 180,284 | `2^18` | 1,920 | no SHA-512 precompile in leanVM: VM change |
| T2 TurboSHAKE256, 4-ary, two Keccak-p[1600,12] | RFC 9861 (from memory), not FIPS | 20 | 2 | 24,000 | 112,710 | 130,924 (148 free) | `2^17` by a hair; safe only after L-1 | 2,880 | needs a 12-round precompile (VM change) |
| T3 Keccak-f[1600], capacity 384 (rate 152), ternary, 149-byte node | not FIPS | 26 | 1 | 31,200 | 119,910 | 138,028 | `2^18` unless L-1 frees about 7,000 words (its target is 4,000) | 2,496 | one KECCAK row a level; no VM change |

Functions that cannot serve 48-byte binding: BLAKE3 and SHA-256 (32-byte outputs, BLAKE3 claims 128
bits at any length: `decision-b-merkle-hash.md` H-1.5), Keccak-256 (32 bytes); SHA-512 gives 64.
The B figures leave out the other 48-byte digests of the statement (`cm`, `nkc`, `rho`, the public
words): F-2 counts them.

**Default (lead agent, 2026-11-19): FIPS-standard SHAKE256 with a 384-bit output.** The shape is
F-2's choice between T1 and T1b; this record recommends counting **T1b first**: the same 40
Keccak-f a path as T1, no alignment layout to invent in A, no extra sibling bytes (path and exit
reveal stay 1,920 B, which also keeps PIR path records at today's size), and the framed form gives
the separation of §3.3 by the `id` byte, which a SHAKE256 node needs anyway (§3.3's current
argument separates tree nodes from SHAKE256 calls by the SHA3 padding domain, which a SHAKE256 node
no longer has). **A non-FIPS sponge (T2 or T3) only if F-2's counts and B's measured `2^18`
footprint show that the FIPS form cannot meet the phone memory limit, and then as a recorded
exception** with its own review item. T1b is Original as far as checked (the Ycash developers,
2026; O-65; sources consulted: the specification §3.1, §3.3, §6, [CFP]); unreviewed.

### 3.6 Block weight as an option (V8)

`W` = 4,172,711 to 4,186,711 B restores 5,150 transfers under Y (+4.3 to 4.7 %); 6,000 need
4,369,911 to 4,383,911 B. At one block per 75 s that is about 4.8 against 4.6 GB a day of block
data before pruning (C, the referee's figure); whether proofs may be pruned after validation is not
stated in the specification and decides what a node operator pays. The lead architect's call; not
taken in this record.

### 3.7 Falcon with message recovery ([GLS26]): not adopted

As revision 1 §3.3: the signature and `pk` are witness and `m` is a verifier-computed public input,
so nothing on chain is saved, and Algorithm 4's verification costs at least what F2 to F5 cost now.

---

## 4. Attacker's gain at the weaker level, and honest labels

| Goal | Weaker level | What the attacker needs | What it gains | Detectable? |
|---|---|---|---|---|
| (P) | ML-KEM-768 (3) | a level-3 lattice break, any time later, on recorded packages | every recorded note's amount, memo, sender link | never |
| (P) | DPF λ = 128 (1); a 128-bit seed (1) | a logging host plus a 2^128 search later; or a 2^128 search on the seed | which tags and records a wallet read; every key of the wallet | never |
| (B) | 32-byte digests (2) | a 2^128-call collision search, **offline, unbounded time** | counterfeit or a double spend proven by both systems: the whole pool, at most `K` a window, until a release freezes it; not repairable for existing notes | no |
| (A) | Falcon-512 under split custody (1) | a compromised proving device, then offline key recovery from `pk` | every address of that account | by the victim |
| (S) | category-1 rows | 2^128-call forgeries in **both** systems, each inside the 2-hour window after block `h_a` (**with F-1**) | the whole pool, at most `K` a window, until a release freezes it | only if it claims a canary |

| Option | (P) | (B) | (A) | (S) | (L) |
|---|---|---|---|---|---|
| O1 | packages 3; DPF 1; ZK statistical | 2 | 5 outside / 1 split custody | 1 per system | 1 |
| O2 | 5 (conditional); ZK statistical | 2 | 5 / 1 | 1 per system | 5 |
| **Y** | **5, conditional on the seed rule and `ε_hvzk`** | **4 (offline set); statement layer 32, window-bound** | **5 / 1; recovery 5** | **1 per system, window-bound after F-1** | **5** |
| O3c | 5 | 4 | 5 / 5 | 1 per system | 5 |
| O4 to O6 | 5 or 3 | 4 or 5 | 5 | 3 or 5 (do not fit) | 3 to 5 |

---

## 5. Why Y beats each alternative

- **O1 (as built):** Y adds (P) at 5 and (B) at 4. (P) costs bytes only and can never be repaired.
  (B) costs B's doubling and about 15 % capacity; the alternative is a pool migration.
- **O2 (32-byte binding):** the rows are defended by a second system, a window (after F-1) and a
  repairing release; binding has none of the three. O2 remains the fallback if B at `2^18` cannot
  meet E1 even with a non-FIPS exception.
- **O3b / O3c (Falcon-1024):** double A's wallet prover for split custody only.
- **O4, O5, O6:** no bundle fits a 4 MB block; E2 needs 33 to 82 hosts; O6 fails W1.
- **40-byte digests:** a ternary SHAKE256 node of 40-byte children is one permutation (125 bytes),
  but 320-bit collisions cost about 2^160 calls, between categories 2 and 3; 48 bytes is the
  smallest output above category 3.
- **48 bytes for the statement layer too** (revision 1): costs bundle-circuit permutations and buys
  nothing in A (32-byte public input); with F-1 the layer is window-bound. Not taken.
- **A cheaper in-circuit hash for B's statement:** none; both systems prove one statement over the
  same functions, and BLAKE3 targets 128 bits at every output length.
- **"Category 2" soundness:** no such level for a search problem (§1.3).

## 6. The choice

### 6.1 Profile Y, parameters

(P) ML-KEM-1024 (packages, addresses, transport); DPF λ = 256 with the AES-256 counter-mode PRG of
§2.1 (or ChaCha20 if W-4 measures it cheaper); lattice PIR off; seed ≥ 256 bits of entropy; ZK target
`2^-128` over `Q = 2^37` leaf proofs excluding `Q ε_hvzk`: A leaf salt 80 B, B leaf salt 96 B,
proof salt 80 B. (B) 48-byte outputs for `cm`, `nkc`, `leaf`, `node`, `anchor_root`, `reg-leaf`,
`reg-node`, `rho`, `H_transfer`; 32 bytes for `leaf-pi`, `bundle-list`, `bundle-kids`,
`bundle-node`, `bstmt` and every other identifier; note tree under SHAKE256-384 (shape by F-2); the
duplicate-commitment rule. (A) Falcon-512 scheme `0x01`; `0x02` reserved with the six items of
§2.3. (S) category-1 rows of revision 7; Keccak-256 (A), BLAKE3 (B) proof trees; `GF(2^256)`; F-1.

### 6.2 What is given up

- Soundness at category 3; the proven QROM bound reaches 2^64 queries only.
- Falcon at level 5 against a compromised proving device (split custody).
- B's wallet leaf at `2^17`: it doubles (about 2× prove time and memory, E); B's E1 memory gap is
  about 2× after the named steps.
- 15 % of capacity at 4 MB (4,345 to 4,405 against 5,150 transfers) and 41 % more mailbox bytes.
- F-1 makes every non-canary transfer depend on one more consensus value (the block hash at `h_a`),
  which a hardware signer cannot check.
- 48-byte binding of the bundle statement layer (it is 32 and window-bound).
- The plan's single-category story: the profile is labelled per goal.

### 6.3 What stays generic

As revision 1: query counts, rate, salt lengths, proof-internal digest length, Merkle hash,
challenge field and cap layer stay row parameters (bound into the statement identifier); A's guest
digest cells and B's `DIGEST_WORDS = 4` and 32-byte spBCS keys are still constants (task S-1). The
offline binding set is already at 48 bytes, so a soundness raise touches no note, address or tree.

### 6.4 The later releases

1. **(A) Falcon-1024** under the six items of §2.3; cost A `2^23`.
2. **(S) category 3:** rows 322/228/232/293 (A), 261 (B), 48-byte proof digests, SHAKE256-384 proof
   trees, leaf salts ≥ 91 B (96 B), `LEAF_RESERVE` about 2.24 MB, `W` about 6.05 MB, 33 to 45
   hosts, or B's list-decoding row once reviewed.
3. **(S) category 5:** a 384-bit field in both systems.

### 6.5 What would change the choice

- B at `2^18` measured over E1 on devices after the memory steps (W-7): a non-FIPS tree (T2 after
  L-1, or T3) as a recorded exception, or O2.
- Wallets that must delegate proving, or split custody becoming the norm: Falcon-1024 at launch.
- E2 met at category 3 on measured recursion and `W` raised on measured propagation: category-3
  soundness at launch.
- F-1 refused by the lead architect: then the statement layer goes back to 48 bytes and (S)'s
  window argument is withdrawn (the canaries and the pair remain).
- FIPS 202 or 203 read with different figures; structural cryptanalysis of Keccak or BLAKE3; the
  external review rejecting the split-custody reading, the binding set or F-1.

---

## 7. Work list (ordered; each with its done-when test)

| # | Task | Done when |
|---|---|---|
| **F-1** | **Fresh statements.** Spec 0.4: `anchor_block_hash` in the transfer hash of every non-canary transfer (376-byte body); no anchor height below the activation height; `yugen-ref` and vectors regenerated | a vector shows a transfer anchored at `E_20` (below activation) refused; two transfers equal except the block hash have different `m`; canary vectors unchanged; both systems' transcript-binding tests pass with the new `m` |
| **W-1** | **`LEAF_RESERVE` from the rows**, provisional 1,403,000 B (§3.3), then derived from measured leaves plus counted deltas; `LEAF_PROOF_FEE` follows; E1's size limits restated from the certified rows | a script in `profile-study/` prints the value from measured A and B leaves; `bundle_rules.json` regenerated; a test accepts a leaf transfer built from the largest measured pair and refuses one byte more |
| **F-2** | **Tree hash counted before spec 0.4 fixes it:** B's AND rows and committed words, A's cycles and KECCAK-table words (task P-2), for T1 (with an aligned two-block layout), T1b, and, as the exception path, T2 and T3; B's prover footprint at `2^18` with the current circuit padded to `2^18` (through the heavy slot) | a table of the variants' counts in both systems and B's `2^18` peak footprint (M); the lead architect fixes the shape under the SHAKE256-384 default, or records the exception with its reason |
| **W-2** | **Spec 0.4 binding set** as §2.2 and §6.1: the offline set at 48 bytes with F-2's tree; `rho` at 48 and the duplicate-commitment rule; transfer hash 48 (and `yugen-falcon`'s 80-byte `message_digest` input); the statement layer at 32 with its reason; §3.3's separation redone for the new node calls and for the builders' spBCS inputs (A's stream point is 112 bytes as built, not 97: `qrom-compilation.md` §2.8); the seed-entropy rule; the six `0x02` items | `yugen-ref` regenerates every vector; a test refuses a 32-byte value wherever 48 is registered; a duplicate-`cm` vector shows the second note not credited; the separation argument covers every call class at the new lengths; a wallet test refuses a 12-word mnemonic |
| **W-3** | Both wallet circuits on W-2 | every statement vector proves and verifies in A and B; A's stack with the KECCAK-table words counted; B's stack, leaf size and footprint measured; W-1 re-derived from them |
| **W-4** | Privacy at 5: ML-KEM-1024 in spec §4.3, §7.1, §10, §12.1 and the wallet; the hybrid transport; the DPF at 256-bit seeds with the named PRG; lattice PIR off | ML-KEM-1024 known-answer tests (after FIPS 203 is added and read); the DPF built with AES-256 counter mode and with ChaCha20, both keyed by the seed, E5 re-measured (≤ 50 KB a day idle) and the cheaper one recorded |
| **W-5** | Salts from the target at `Q = 2^37` | the calculator prints the floors at `Q = 2^37` (79 / 79 / 78 B against 2^272); the rows carry 80 / 96 / 80 B; `soundness-method.md` states the lifetime `Q` |
| **W-7** | Devices (plan step 0.15) **ahead of the spec freeze** | A `2^22` and B at the chosen stack measured on a flagship, a mid-range Android phone and the web build; peak ≤ 512 MB or the figure reported with §6.5 |
| W-6 | B's E2 reductions (D-6, K = 7 or 15, cap layer at 7); A's N-7 | N = 1,500 measured in both systems at category 1; hosts stated |
| S-1 | Proof-internal digest length, tree hash and field as run-time row parameters | a category-3 row of each system proves and verifies in a test build; category-1 bytes unchanged |
| A-1 | Falcon-1024 counted in both circuits (scheme `0x02`), not enabled | the 128 known-answer vectors at 1024 prove in both test builds; rows and stacks recorded |
| X-1 | External review (§9) | the reviewer's verdict on items 1 to 6 recorded |

First, in order: **F-1, W-1, F-2, W-2, W-3, W-4, W-5, W-7.**

## 8. Corrections to the plan and the specification (reported, not edited)

Plan (lead agent's file):
- §9 "category 1 for the whole suite ... parameters only": profile Y with per-goal levels; a
  soundness raise is a release only after S-1.
- §9 ML-KEM-768 → ML-KEM-1024; "metadata fetched by PIR ... post-quantum protected" is false while
  DPF seeds are 128 bits; hash collisions "256-bit outputs" → the offline binding set at 48 bytes.
- §14 SQ-49: "Falcon-512 behind its hidden, salted key hash" carries the split-custody
  qualification (§2.3); "the turnstile and caps bound" a forgery reads "rate-limit" (§1.2).
- §5, §8: capacity at the launch weight about 4,350 to 4,400 for Y (S6); §11 E1 size thresholds
  restated from the rows (W-1).

Specification 0.3.4:
- §2 `LEAF_RESERVE` 1,150,000 is below every measured pair.
- §3.1 "the output is always the first 32 bytes": per identifier (W-2). §3.2: `sig` body fixed at
  930, no identifier for a 1,793-byte key (§2.3 item 1).
- §3.3: the spBCS stream points are listed as 97 bytes for both systems; system A's are 112 bytes as
  built (16-byte tag). With the 8-byte tag of A's lead decision Q1 they would be 104 bytes, the
  length of Falcon's hash-to-point input, whose first byte is a random nonce byte: the length
  separation of §3.3 would fail (`qrom-compilation.md` §2.8).
- §4.1: no seed-entropy rule (R-5). §5.4 l. 543: "`rho_j` is unique" holds only to `H_rho`'s
  collision resistance (R-2). §8.1: no lower bound at activation (R-1).
- §4.3, §7.1, §12.1 ML-KEM-1024 sizes; A.2 names SHA-256 for B's trees (SQ-48 decided BLAKE3);
  A-9 / A-10 salts 80 / 96 / 80 B.

## 9. Review sheet for the external cryptographer (highest risk first; the referee's residual doubts included)

1. **F-1 and freshness (§1.1).** Is every non-canary statement unpredictable until block `h_a`
   once the block hash is in the transfer hash, in both systems and both modes? Residual doubts:
   the miner of `h_a` knows it one block early; canary roots are constant by design; P7 in mode 1
   (spec §11.1.2 says it is supplied there too).
2. **The binding set (§2.2).** Every collision-dependent digest in the 48-byte set? Is the
   window-bound classification of the statement layer sound given F-1, and is system A's 32-byte
   public input acceptable as a per-system window-bound digest? Is the duplicate-commitment rule
   complete (only the recipient is harmed)?
3. **Split-custody reading of Falcon-512 (§2.3)** and the six `0x02` items; the per-address-group
   key option.
4. **What the pair buys (§2.4):** the eight shared parts; any other common dependency.
5. **The note-tree hash (§3.5):** SHAKE256-384's 192-bit collision claim (FIPS 202 from memory;
   [FIPS204] App. D.1 read); the separation of a framed binary node (T1b) from every other SHAKE256
   call; T2's margin of about 148 committed words; T3's non-FIPS sponge if ever taken.
6. **Zero knowledge (§2.1):** the work-over-advantage reading at `Q = 2^37`; `ε_hvzk` of both
   systems (open); the DPF PRG; the seed rule; ML-KEM ciphertext anonymity (from memory).
7. **The builders' spBCS deviations** (`qrom-compilation.md` §2.8): B's repeated positions; MA-2'.
8. **The category-1 rows:** tree accounting O-13, Q-5's convention, the QROM reach; the MAXDEPTH
   extrapolation of §1.1 (E, below NIST's stated range).
9. **Sizes from memory:** ML-KEM-1024, FIPS 202 capacities, TurboSHAKE; the DPF key size at
   λ = 256.
10. **W-1's derivation of `LEAF_RESERVE`** and B's memory estimate at `2^18` (S8, E).

## 10. Provenance

**Published, used as is:** [CFP] §4.A.5 pp. 16 to 19, §4.A.6; [FIPS204] §4 Table 1, App. D.1 (p.
64, re-read and quoted); [FIPS205] §11 Table 2, §11.2.2; [COSE-FN] §1 Table 1; [GLS26] abstract,
§1, §1.1, Algorithms 1 to 4, Lemma 1; [SG26] Theorem 6.6 (2) to (4) through the calculator; the
Falcon-1024 constants through `yugen-falcon`; measured figures of `yugen-proof-a` and
`yugen-proof-b2` as cited. **Adapted:** the MAXDEPTH extrapolation to a two-hour window (§1.1; [CFP]
p. 18's AES-128 formula below its stated range; change: the depth only; first in the referee's
§1.2). **Original (the Ycash developers, 2026), unreviewed:** from revision 1, the per-goal method
and profile Y (O-49), the binding classification (O-50, **corrected** here), the anchor-window
argument (O-51, **holds only with F-1**), the work-over-advantage reading (O-52, **`Q` corrected**),
the W4 magnitude and reserve rule (O-53, **reserve corrected**), the tree-arity count (O-54), the
message-recovery assessment (O-55); from the referee report, adopted here: R-1 and F-1 (O-56), R-2
(O-57), R-3 (O-58), R-4 (O-59), R-5 (O-60), the split-custody reading and the `0x02` readiness list
(O-61), the window-bound statement layer and A's 32-byte public input (O-62), the tree-variant
counts and A's layout risk (O-63), the lifetime proof count and salt floors (O-64); new in this
revision: the binary framed SHAKE256-384 node T1b and the 8-byte-tag length clash (O-65). Checked
before labelling: [CFP], [FIPS204], [FIPS205], [GLS26], [SG26] Sections 6 and I.1, the referee
report, specification 0.3.4; none states these for this design. The Faerie-gold attack class is
known from Zcash's design (from memory, not in the folder); only its route through `H_rho` and free
dummy witnesses is new here.
