# Private tag filtering for payment requests: FMD, OMR, PIR and a slim slice

Part of Yugen. **Status: draft for refereeing**, unreviewed. Read against specification
0.4.4 (`yugen-spec` `main`): SPEC-176 and SPEC-177 in `spec/decisions.md`; §7.6, §9.1 to §9.3,
§17.1, §17.6 and §17.8 of `spec/yugen-protocol.md`.

The question (the lead architect): SPEC-176 made request tags per payment,
`itag_j = trunc_6(PRF_tag(k, LE32(asset) || nf_1 || j))`, so only a request holder links payments.
The price is that every wallet downloads every incoming slice whole (60 bytes per applied output:
about 1.38 MB a day at ten transfers a block, about 1.19 GB a day at full blocks, §17.1) and scans
it (§9.3). Can a tag the statement proves well-formed, testable by the host under a key that does
not tell it which outputs are the wallet's, cut the download, and can it be built before the
wallet circuits freeze?

Short answer (section 6): neither FMD nor OMR is ready for Yugen, and neither needs a circuit
change. A different change, also with no circuit change, removes most of the bandwidth now:
the **slim slice** of section 5 (14 bytes per output instead of 60, with the matched slots
fetched by the existing DPF). FMD and OMR stay later options; section 6.3 says what would change
that.

## 1. Sources and how they were read

Both papers were read from their text layer, extracted with pypdfium2 (the `yugen-proofs`
`.tools-venv`) to the session's scratch directory, outside every repository. Titles and authors
are taken from each first page.

- **[BLMG21]** Gabrielle Beck, Julia Len, Ian Miers, Matthew Green. *Fuzzy Message Detection.*
  Cryptology ePrint Archive, Paper 2021/089 (file `2021-089.pdf`, 38 pages; no venue stated in the
  copy). Read: §1 to §2 (pp. 1 to 3), the definitions (pp. 7 to 9, Theorem 5), §5.2 Figure 3 and
  Theorems 12, 13 (p. 14), §5.3 (p. 14), §7 Tables 1 to 3 and the evaluation text (pp. 18 to 20,
  including "Lewis's Attacks"), §8 and §9 (p. 22).
- **[LT21]** Zeyu Liu, Eran Tromer. *Oblivious Message Retrieval.* Cryptology ePrint Archive,
  Paper 2021/1256, the revision dated April 14, 2022 on its first page (file `2021-1256.pdf`,
  66 pages; no venue stated in the copy). Read: abstract and §1.1 (pp. 1, 6), §2 with Tables 1, 2
  (pp. 7 to 9), §3 overview (pp. 11 to 13), §7.1, §7.2 (pp. 30, 31), Theorem 8.3 and
  Conjecture 8.4 (pp. 47, 48), §10 with Tables 3, 4 (pp. 52 to 54), §11 detection cost and
  latency (pp. 56, 57), §12 limitations (pp. 57, 58).
- Yugen context, read: `yugen-spec` as above; `yugen-pir` `docs/pir-selection.md` table 1 and
  §3.1 (DPF host cost, measured there).

Not read (marked wherever used): ZIP-307 and Zcash trial decryption (cited by [LT21] Table 3 as
[GH18]); Lewis's FMD analysis [Sar21a, Sar21b] (known here only through [BLMG21] p. 19); PVW08
and BFV (only as [LT21] §5.2, §5.3, §7 describe them); any lattice FMD paper (section 3.1).

## 2. The two papers

### 2.1 Fuzzy Message Detection [BLMG21]

**Construction.** A recipient has a key pair; a sender attaches a **flag** made with `Flag(pk)`;
`Extract(sk, p)` gives a **detection key** `dsk` for a false-positive rate `p`; `Test(dsk, flag)`
returns 1 on every flag to `pk` and on a flag to anyone else with probability about `p` ([BLMG21]
§2, p. 3; the syntax on p. 7). The efficient restricted scheme FMD2 ([BLMG21] Figure 3, p. 14) is
hashed ElGamal per bit: `sk = (x_1..x_γ)`, `pk = (g, h_i = g^{x_i})`; a flag is
`(u = g^r, y, c_1..c_γ)` with `c_i = H(u || h_i^r || w) XOR 1` and a chameleon-hash value `y`
for CCA security; `dsk` for `p = 2^-n` is `(x_1..x_n)`, and `Test` recomputes the first `n` bits.
FracFMD (§6, Theorem 15) supports fractional `p` with garbled circuits.

**Security model.** Correctness, fuzziness (false positives at rate `p`), and **detection
ambiguity** (DA-CPA/DA-CCA): a server holding `dsk` cannot tell true from false positives
([BLMG21] §2, p. 3; Theorem 5 for key privacy). FMD2 is DA-CCA secure for `P = {2^-s}` under
discrete log and Gap-DH in the random-oracle model ([BLMG21] Theorem 13, p. 14). The paper does
not try to hide `p` from the server (p. 3).

**Costs** ([BLMG21] Tables 1, 2, pp. 18, 19; p. 3). FMD2: flag 68 bytes, Flag 1.927 ms, Test
0.548 ms at `p` about 3 %, `γ` up to 24. FracFMD: flags of 318,530 bytes (`8` bits of
precision) to 1,230,914 bytes (`24` bits).

**Privacy versus bandwidth, and weaknesses the paper states.** The anonymity is a decoy set: a
server sees about `pN` flagged items out of `N` ("dynamic k-anonymity", p. 2; [LT21] p. 7 calls it
pN-msg-anonymity). Larger `p` hides better and costs more download. [BLMG21] §7 p. 19 reports
Lewis's independent analysis: privacy depends on parameters; **differential attacks** (a server
that learns some messages are for one recipient narrows the recipient), **statistical attacks**
(whether a recipient received anything in a period) and an attack that **uncovers recipients of a
subset of messages at low `p`**; the paper's suggested mitigations are hiding sender metadata
(anonymous networks) and having some users download everything. Table 3 (p. 20) bounds the
probability of a "trivial attribution" (a message flagged for one recipient only) in a
300,000-transaction, 400,000-recipient day: about `4 × 10^-82` a day at `p = 5 × 10^-4` but
rising steeply as `p` falls ("As p decreases, the probability of a trivial attribution increases
drastically"). §5.3 (p. 14): detection keys cannot be revoked and `p` cannot be changed without
new keys. §8 (p. 22): FMD "natively provides only probabilistic privacy guarantees".

### 2.2 Oblivious Message Retrieval [LT21]

**Construction.** Senders attach a **clue**; a recipient gives a **detector** a detection key and
a bound `k̄` on its pertinent messages; the detector computes, under homomorphic encryption, a
**digest** from which the recipient decodes the pertinent payloads ([LT21] §3, pp. 11 to 13;
Definition 4.1 ff., pp. 14 to 16). Practical schemes ([LT21] §7): clues are PVW encryptions of
zero (a Regev-style LWE scheme; §7.1, p. 30); the detection key holds a BFV public key, BFV
evaluation keys and the PVW secret key under BFV; the detector decrypts every clue
homomorphically (inner product, division, rounding, §7.2 p. 31), forms an encrypted
pertinency vector, and packs pertinent payloads by a homomorphically encoded **sparse random
linear code** (SRLC) that the recipient solves (§3.3, pp. 12, 13; §6.2). OMRp1 (§7.3) has a digest
linear in `N` but dense; OMRp2 (§7.4) is compact (quasilinear in `k̄`, polylogarithmic in `N`).

**Security model.** Privacy and full key unlinkability hold "even if everyone but the recipient
is adversarial and colluding" ([LT21] abstract; Table 1, p. 7), under Ring-LWE. Soundness and
completeness assume an honest detector (§12, p. 57). DoS resistance (a malicious sender making
clues that match others) needs **Conjecture 8.4** ("Regev05 is snake-eye resistant", p. 48; used
in Theorem 8.3, p. 47) or zk-SNARKs; privacy does not (p. 47).

**Costs** ([LT21] §10, Tables 3, 4, pp. 52 to 54; parameters N = 500,000, `k̄` = 50, payload 612 B,
PVW `n` = 450, `q` = 65537, `w` = 16000, `ℓ` = 4 at 120 bits by the LWE estimator; BFV `D = 2^15`,
`log Q` = 790). Clue **956 bytes**; clue key (the recipient's public key, needed by senders)
**133 KB**; detection key **129 MB**; detector time OMRp1 0.145 s/msg on one thread, 0.065 s/msg on
4 threads; digest OMRp1 1.13 B/msg (about 9 bits), OMRp2 9.03 B/msg at that `N` and under 1 bit/msg
above `N = 8 × 10^6`; OMRp1 digest 549 KB at N = 500,000 (the packing minimum: `N` is rounded up
to multiples of 500,000, p. 54), recipient decode about 20 ms. Streaming ("subscribe and
finalize", §11 p. 57) moves most work before the recipient arrives; it is still per recipient.
§12 lists the clue and clue-key size, the detection cost and the detection-key size as open
limitations.

## 3. Post-quantum status

### 3.1 FMD

FMD2 rests on discrete log and Gap-DH ([BLMG21] Theorem 13): **broken by a quantum attacker**,
and retroactively: with `x_i = log h_i` from a published key, anyone can test every flag ever
posted against every published key and attribute every payment. Under Yugen's
record-now-break-later threat this is disqualifying for FMD2 as built.

FMD1 ([BLMG21] Figure 2, Theorems 10, 11, p. 13) is generic over a **uniformly ambiguous bit
PKE**. A lattice PKE with that property would give a post-quantum FMD in principle; [BLMG21] does
not give one, and [LT21] Table 1 lists FMD1/FMD2 only under "PKE". From memory, not read: later
papers propose lattice-based FMD variants; none is in the reference folder and none is relied on
here. No hash-based FMD is known to this document: a hash-only flag that a third party can test
under a delegated key while keeping detection ambiguity needs public-key structure (Original
observation, unreviewed; not a theorem).

### 3.2 OMR

Privacy is proven under **Ring-LWE** ([LT21] §1.1, p. 6: "Security is thus plausibly
postquantum"; Table 1), PVW's IND-CPA and key privacy under LWE (§7.1, p. 31, citing
[PVW08, Lemma 7.4], not read). Two cautions for Yugen: the stated security levels are 120 bits
(PVW) and over 128 bits (BFV) **by the classical LWE estimator** ([LT21] §10.1, p. 52), below the
level-5 target the rest of Yugen uses (compare `yugen-pir` `pir-selection.md` "Consequence", which
found the same gap for single-server lattice PIR); a level-5 re-parameterisation enlarges clues
and keys and is not in the paper. DoS resistance rests on the new Conjecture 8.4.

## 4. Fit with Yugen

### 4.1 What the statement would prove, and whether it must

For OMR the payment statement would prove `clue = PVW.Enc(pk_clue, 0^ℓ)` under the recipient's
clue key, bound to the output's commitment. PVW encryption at [LT21]'s parameters multiplies a
`w = 16000` short vector by the `n × w` (450 × 16000) seeded matrix and by the `ℓ × w` key part:
about **7.3 million** mod-`q` multiply-adds, plus expanding the matrix from its seed (about 15 MB of
SHAKE output, about **112,000 Keccak-f** at the 136-byte rate) and absorbing the 133 KB key into the
address commitment (about 1,000 Keccak-f). Against system A (about 742K cycles per masked leaf,
about 9 % slack, so some 67K cycles) and system B (leaf slot near `2^22`) this is two orders of
magnitude over. Estimate from the algorithm of [LT21] §5.2, §7.1 (Adapted: the count is ours).

For FMD2 the statement would prove `γ` exponentiations and hashes in a prime-order group:
non-native group arithmetic in a hash-based system, and quantum-broken anyway.

**But the proof is not needed for privacy.** [LT21] Table 1 and p. 47: privacy holds against
malicious senders; only DoS soundness needs Conjecture 8.4 or a SNARK. In Yugen a malformed clue
hurts the payer's own payment (the recipient misses it, as if it were not sent) or adds false
positives for others (DoS). So OMR or FMD can be added **with no circuit change**: the clue rides
in the transfer bytes, which the transfer hash binds (§7.6 treats `itag` the same way). Original
observation (the Ycash developers, 2026), unreviewed.

### 4.2 Bytes, server work, download, what the host learns

Figures per wallet per day; `N` = 23,040 outputs (ten transfers a block) or 19.9 million (full
blocks), from §17.1.

| | Extra bytes per output | Server per wallet per day | Wallet download per day | Host learns |
|---|---|---|---|---|
| Status quo (SPEC-176) | 0 (60-byte slot in the host index) | serve the slice | 1.38 MB / 1.19 GB | nothing beyond §17.8's schedule |
| FMD2, `p = 2^-8` | 68 on chain (flag) | `N` Tests at 0.548 ms: 13 s / 3.0 h of core time | `pN` slots: 5.4 KB / 4.7 MB (plus true positives) | the candidate set; pN-anonymity, Lewis's attacks; quantum: everything, retroactively |
| OMRp1 | 956 on chain (clue); 133 KB clue key in each address | 0.145 core-s × `N`: 56 core-min / **33 core-days** | ≥ 549 KB (packing minimum) / about 22 MB | nothing about content; a long-lived 129 MB detection key links the wallet's sessions |
| OMRp2 | as OMRp1 | 0.155 core-s × `N`: about 60 core-min / 36 core-days | 9 B/msg at small `N` (207 KB) / under 2.5 MB | as OMRp1 |

Consequences. The 956-byte clue is about four times a 232-byte transfer: at full blocks it cuts
capacity to roughly a fifth (Adapted from [LT21] §12, which says it "nearly doubles" a Zcash
transaction). The 129 MB detection key either stays with a host for weeks, which links all of a
wallet's syncs to one key and undoes SPEC-178's fresh-per-session keys, or is re-sent each sync:
72 syncs a day (1,152 blocks / 16) × 129 MB = 9.3 GB a day upload, worse than the status quo. At
full blocks the server bill is per wallet and linear in `N`: 33 core-days per wallet per day is not
operable. FMD's candidate set grows by the wallet's true payments, so its download size reveals
activity unless padded to a fixed size, which §17.8 item 2 would require.

### 4.3 Can PIR/DPF over the slice do it without a circuit change?

**Not by itself.** The two-host DPF (§17.6) retrieves a record at an index the wallet chooses.
Under SPEC-176 the wallet cannot compute the index of its payment: the tag depends on the payer's
`nf_1`, which the wallet learns only from the slot. Any scheme that makes the index predictable
(a small nonce set, a per-day key) is one of SPEC-176's rejected options (a′), (a″), (b), (b′).
Benefit of DPF alone: **zero** for detection. What DPF does do well is fetch a few known slots
cheaply once detection has happened elsewhere: one query over a 1.19 GB slice is about 0.06
core-seconds a host (scaled from `pir-selection.md` table 1, 0.076 core-s at 1.46 GB, about
0.05 core-s/GB, measured there at 128-bit seeds; the 256-bit PRG of §17.6 is not yet re-measured,
task W-4).

## 5. A hybrid: the slim slice (Original, the Ycash developers, 2026)

The scan in §9.3 needs, per slot, only the 6-byte tag and the PRF input that varies per output.
Today that input is `nf_1 || j` (33 bytes), so a wallet that only scans must still download the
tag, `nf_1` and `j`; the remaining 21 bytes (`count`, position, `iamt`, padding) are needed only
for a match. Change the PRF input to a short public digest of `nf_1 || j`:

```
n_j    = trunc_8( H_nonce( nf_1 || j ) )                       public: anyone can compute it from the transfer
itag_j = trunc_6( PRF_tag( k, LE32(asset) || n_j ) )
iamt_j, rcm, rho_j: unchanged (still keyed by nf_1 || j)
```

and serve two layers per slice:

1. **slim slice**, downloaded whole by every wallet (§17.8 item 2 unchanged in form):
   `itag_j(6) || n_j(8)` per applied output in position order, **14 bytes**; position is implied
   by order;
2. **full slots** (§17.1's 60 bytes), never downloaded whole; a wallet fetches the slot at each
   matched position by the two-host DPF under a new fixed count `SYNC_SLOT_QUERIES` per sync, real
   or cover, carried over like path queries (§17.8 item 3). Alternatively the path record could
   carry the slots of its 64-leaf group so that the existing path query fetches both (larger
   records; not costed).

Properties.
- **No circuit change**: the statement does not constrain `itag` (§7.6); `rcm`, `cm`, `iamt` are
  untouched. Changes are in §7.6 (`itag` input), §9.3 (scan over `n_j`), §17.1 (two layers),
  §17.8 (one more fixed query count), §2 (one parameter), the vectors `tags`, `request`,
  `host_index` and the transfers that pay requests.
- **Post-quantum**: hash and PRF only, as today; the DPF keeps SPEC-183's non-collusion
  assumption, which the design already makes for path records.
- **Privacy**: the same as SPEC-176. Payments to one request carry tags under distinct `n_j`;
  two payments share a tag only if their `n_j` collide (probability about `2^-64` a pair). The
  host sees one fixed-size download and a fixed number of DPF queries per sync, whatever was
  matched.
- **Bandwidth**: 14 B per output: **323 KB a day** at ten transfers a block, **279 MB a day** at
  full blocks (a factor 4.3 below 60 B). A 10-byte variant (`itag` 4, `n_j` 6) gives 230 KB / 199 MB,
  but raises false matches to `S × R / 2^32` per slice (about 46 a day at full blocks with
  `R = 10`), each spending a fixed slot query: the 6-byte tag is kept.
- **Wallet compute**: unchanged, `S × R` Keccak-f a slice (§9.3).
- **Host cost**: `SYNC_SLOT_QUERIES` DPF evaluations a sync of each wallet, about 0.06 core-s each
  at full blocks.
- **Latency**: a found payment needs its slot (this sync's slot query) before its path query; with
  the slot fetched in the same sync as the slim slice, the path query follows at the next sync.

Prior work checked: [BLMG21] and [LT21] (their "full scan" baseline downloads the whole relevant
part of each message; neither splits a scan layer from a retrieval layer this way); Zcash's
compact blocks (from memory, ZIP-307 not read) also download a trimmed per-output record for
trial decryption, so splitting a small scan record from the full record is long-standing practice.
The specific use (a public short digest as the PRF input so the scan layer is 14 bytes, with
retrieval by DPF under fixed counts) is **Original as far as checked** (sources consulted: the two
papers, `yugen-spec` 0.4.4 SPEC-176 options, `pir-selection.md`).

The slim slice does not change the asymptotics: at full blocks a light wallet still downloads
279 MB a day. Only detection delegated to a host (FMD, OMR) removes the linear term.

## 6. Options and recommendation

### 6.1 Options

| Option | Post-quantum | Circuit change | Host learns | Wallet bandwidth/day (10 tx/block; full) | Server cost/wallet/day (full) | Literature | Original |
|---|---|---|---|---|---|---|---|
| (i) SPEC-176 status quo | yes (hash) | no | nothing beyond schedule | 1.38 MB; 1.19 GB | serving bytes | trial scanning: long practice | SPEC-176 as specified |
| (ii) DPF/PIR over the slice | yes (hash; two hosts non-colluding) | no | nothing (non-collusion) | no saving: the index is unknown | — | BGI16 (not read) | — |
| (iii) FMD | **no** for FMD2 (DDH, retroactive); lattice FMD1 possible in principle, no instance in these papers | no (needed only for DoS) | pN-anonymity set; Lewis's attacks; size leaks activity unless padded | 5.4 KB; 4.7 MB at `p = 2^-8` (+68 B flag on chain) | about 3 core-h | published 2021, weaknesses published | none |
| (iv) OMR (OMRp1/p2) | assumption: Ring-LWE, at classical-estimator 120/128 bits, not level 5 | no for privacy; DoS needs Conj. 8.4 or a SNARK (in-circuit: about 7.3M field ops + 112K Keccak-f, infeasible) | nothing about content; sessions linked by the 129 MB key | ≥ 549 KB; about 2.5 to 22 MB (+956 B clue on chain, 133 KB addresses, 129 MB key upload) | 33 to 36 core-days | published 2021/22, prototype; open problems stated in §12 | the no-circuit observation (4.1) |
| (v) slim slice + DPF slot fetch | yes (hash; DPF non-collusion as today) | **no** | same as (i) | **323 KB; 279 MB** | `SYNC_SLOT_QUERIES` × 0.06 core-s per sync | parts published; combination new | the slim slice (section 5) |
| (vi) slim slice later + OMR as an optional service | assumption as (iv) for the opt-in | no | as (iv) for opt-in wallets | as (v), or as (iv) | as (iv) | — | the layering |

### 6.2 Recommendation (draft for refereeing)

1. **Adopt (v), the slim slice, before the wallet circuits freeze.** It needs no circuit change,
   keeps SPEC-176's privacy and the post-quantum basis, and cuts the daily download by a factor
   4.3. It is spec and wallet work only, so it does not block on the circuits; but it changes the
   `itag` derivation, which fixes transfer bytes and test vectors, so it should land before
   those vectors are frozen.
   **First concrete step:** a specification change proposal against 0.4.4 (§7.6 `n_j` and the new
   `itag` input with a new `H_nonce` identifier in §3.2; §17.1 two layers; §17.8 item 3
   `SYNC_SLOT_QUERIES`; §9.3 scan), with vectors `tags`, `request`, `host_index` regenerated and a
   test that two payments to one request with distinct `nf_1` give unrelated `(itag, n_j)`.
   Acceptance: `check_vectors.py` passes; the scan in the reference wallet finds every payment of
   the `request` vectors from the slim layer alone and fetches exactly `SYNC_SLOT_QUERIES` slots
   per sync whatever it matched.
2. **FMD: not yet.** No post-quantum instance in the supplied papers; FMD2 is retroactively broken
   by a quantum attacker; its anonymity at practical `p` is weak by the paper's own account.
   What would change it: a refereed lattice FMD with ambiguity proven at level 5, and a padded
   fixed-size candidate download compatible with §17.8.
3. **OMR: not yet.** It is the only option with full obliviousness and a sublinear download, but at
   Yugen's full-block load the detector cost (33 core-days per wallet per day), the 956-byte clue
   (capacity), the 129 MB long-lived detection key (session linkage against SPEC-178) and the
   below-level-5 parameters rule it out as a default. What would change it: level-5 parameters with
   measured clue and key sizes; detector cost amortised across recipients or hardware-accelerated
   by orders of magnitude ([LT21] §12 names both as open); a key-rerandomisation that keeps
   sessions unlinkable. Because the clue needs no circuit change (4.1), OMR can be added later as
   an optional transfer field and an opt-in host service without touching the frozen circuits;
   the circuit freeze does not foreclose it. Reserving the field now is not recommended: its
   size depends on the level-5 parameters, which are unknown.

### 6.3 Decision record

- **Options considered:** (i) to (vi) above.
- **Trade-offs:** (v) keeps linear bandwidth but at 23 % of today's; (iii) and (iv) remove the
  linear term at the cost of quantum security (iii) or of server cost, clue size and key size (iv).
- **Reason for the draft choice:** (v) is the only option that cuts bandwidth while keeping every
  property SPEC-176 and SPEC-177 established, with no circuit change.
- **What would reverse it:** a referee finding that `n_j` creates linkage SPEC-176 did not have
  (for example, a reuse of `n_j` across transfers that the `nf_1` uniqueness argument misses); a
  measured DPF slot-query cost at 256-bit seeds that makes the fixed slot count unaffordable
  (task W-4); or OMR meeting the conditions of 6.2 item 3, after which (vi) becomes the target.

## 7. What could not be verified

- PVW08, BFV, BGI16, ZIP-307 and Lewis's analyses were not read; statements about them are via
  the two papers or from memory, as marked.
- No lattice FMD paper was read; its existence is from memory.
- No benchmark was run; all server figures are the papers' (2021/22 hardware) or
  `pir-selection.md`'s measurements, scaled linearly.
- The in-circuit counts in 4.1 are estimates from the algorithm description, not a circuit.
- [LT21]'s security levels are by the classical LWE estimator; no level-5 parameters were derived.
