# Privacy review of the claims beside the proof systems

Part of Yugen. `yugen-proofs`, 2026-11-19. An internal review, not an outside one, of
`docs/what-is-claimed-elsewhere.md` (at `dbe6adc`), privacy first. Read: `yugen-spec` main at `51ab111`
(specification 0.4.2), sections 4, 5, 7, 8, 9, 10, 11.1, 12, 13.1, 17, 18.1; `yugen-review/findings.md`
R-21 to R-26; `yugen-pir/docs/pir-selection.md` (by search). No test, model or check was run. Claims about
papers not in the reference-paper collection (REFERENCES.md) are marked **from memory**. Every finding below is
**Original (the Ycash developers, 2026)**, this document, unless it says it repeats a recorded finding.

## 0. Leaks, first

| # | Finding | Severity |
|---|---|---|
| L-1 | **A request tag is constant per request and public.** `itag_j = trunc_6(PRF_tag(k, LE32(asset)))` (§7.6) depends only on the request secret and asset, so every output paying one request carries the same 6 bytes on chain. Fillers are pseudorandom, so a repeated tag is a near-certain link (chance collision about `N^2 / 2^49` over `N` outputs). Any observer, without `k`, links: (a) two payments by one payer to one request (installments, a re-payment at a different `nf_1`), linking two transfers of that payer's wallet; (b) payments by different payers to one recipient. The specification states that the **holder** of a request sees every payment (§9.1, R-22) but not that **everyone** links them. The public index makes it explicit: the `count` field of §17.1 publishes the number of outputs sharing a tag in a slice. | **MAJOR** |
| L-2 | **Private-retrieval query counts are not fixed in the normative text.** §17.1 lookup reads overflow pages only when the tag's `count > 1`, so the number of queries a wallet sends tells each server, alone, that one of its tags was paid more than once; the number of slices, requests and counters scanned (§9.3 high-water marks, §7.5 `OTAG_GAP`) and the times of sync likewise. R-25's fix ("fixed counts Q and P, real or cover, at times independent of wallet activity", `yugen-review/findings.md`) and `pir-selection.md` §5 (fixed batch with dummy parts, restore only) are not in §17 of 0.4.2 (no "cover" or fixed-count rule found). | **MAJOR** |
| L-3 | **The wallet's own transport keys are not required to be fresh** (§17.7: "a wallet receiving from a host publishes `ek` and `pk_X`"; only `e` and the coins are required fresh). A long-lived wallet key lets a host link every session of one wallet, which undoes the session unlinkability that L-2's fix needs. | MINOR |

Fixes, each buildable without a consensus change except L-1 option (b):

- **L-1.** (a) Specification text, §7.6 and §9.1: "outputs paying one request carry one public tag; any observer links them". Wallet rule: a payer pays a request at most once (re-making a dropped transfer keeps `nf_1` and is not a second payment, §8.4); a second payment to the same payee uses a fresh request; a receiving wallet shows a request as spent after its first applied payment. Vector: `request.json` kind `tag-reuse-links`. (b) Option for the lead architect: bind the tag to the payer's day, `itag_j = trunc_6(PRF_tag(k, LE32(asset) || LE32(a)))` with `a = floor(anchor_height / DAY_BLOCKS)`, which the recipient already scans per slice (§9.3 looks up slices `D − 1` to `D + 7`, so at most 9 tags per request); links then survive only within one day. Changes vectors and the host index, not the statement (the statement does not constrain tags, §7.5).
- **L-2.** New normative §17.8: every sync queries every slice since the last sync with fixed counts `Q` (incoming-tag buckets, overflow pages included, real or cover), `P` (path records) and `M` (mailbox buckets), at times drawn independently of wallet activity; a wallet whose real needs exceed a count spreads them over later syncs; restore uses the fixed-size batch of `pir-selection.md` §5. Model: extend `yugen-models` with a two-wallet indistinguishability check on the query transcript.
- **L-3.** §17.7: a wallet's `ek` and `pk_X` are generated fresh per session and never derived from wallet keys; a host's keys may be long-lived.

## 1. What the public data of a transfer reveal (K-c)

Public inputs P1 to P9 (§11.1) and the on-chain fields (§7.1), with the context of §7.2.

| Item | What it reveals | Verdict |
|---|---|---|
| P1 `anchor_root`, `anchor_slot`, anchor block hash (in P7) | The anchor height, hence the wallet's view of the tip to within 16 blocks; the wallet rule fixes `h_a` from the tip (§8.3), so honest wallets at one tip agree. A wallet whose tip lags is fingerprinted by an older anchor | holds for wallet-rule wallets; NOTE |
| P2 `nf_1`, `nf_2` | Nothing without `nk_d` (PRF, §5.3); dummies `H_nf-dummy(dx)` look alike. An exit reveals `nk_d`, which links every note and spend of that address retroactively (stated, §13.1.2; R-24) | holds under PRF assumption on `PRF_nf`; exit linkage stated |
| P3 `cm_1`, `cm_2` | Nothing if `rcm` is secret (hiding commitment; `spec/request-lemmas.md` L3 covers `cm`, not read here) | holds under assumption (not checked) |
| P4 `fee`, `fee_class`, flag `LEAFFEE` | Fee rung and leaf-or-bundle route. The fee rule (smallest rung cleared in each of the last 10 blocks, §7.9) is deterministic; a wallet off the rule is fingerprinted | holds for rule-following wallets; NOTE |
| P5, P6 `value_balance` (flag `VB`), `tout_hash` over `vout` | **The amount of every deposit and withdrawal**, and the transparent scripts. Inherent to a transparent boundary; amount matching across a deposit and a later withdrawal links them | stated leak by design; NOTE. Fix (wallet rule): offer round-amount deposits and delayed, split withdrawals |
| P7 `m` | Only a hash of the transfer bytes | holds |
| P8 `auth_mode` | A consensus value, the same for every transfer at a height | holds |
| P9 `reg_root` | A chain value | holds |
| `flags` `PKG1`, `PKG2`, `PKG1_MEMO`, `PKG2_MEMO` | How many outputs go to `ONCHAIN` static addresses and whether each carries a memo (package length 1,672 or 2,184); hence recipient type (request, off-chain mailbox or change carry no package). A wallet-type and recipient-type fingerprint | MINOR. Fix (wallet option, no consensus change): a "uniform" wallet rule that always writes two long packages, the extra one to an internal address's `ek_d` |
| `flags` `CANARY*` | Marks canary claims, which are not payments | holds |
| `pkg_bucket` | `b` bits of `H_bkt(ek_d || epoch)` of the recipient: same-epoch linking and known-address testing exactly as SPEC-108 states (§17.4); a published static address is the known-address case | stated leak, bounded by `PKG_BUCKET_FLOOR`; NOTE |
| `otag_j`, `orec_j` | Nothing without `ovk_view`; a reused counter repeats `otag` publicly and links two outputs of one wallet (stated, §7.5). Two devices on one seed reuse counters | MINOR: add a wallet rule that devices sharing a seed use disjoint accounts |
| `itag_j`, `iamt_j` | Request tags: **L-1**. `iamt` is a pad per `(k, asset, nf_1, j)`; two transfers with one `nf_1` and different amounts publish `v XOR v'` (stated, §9.2) | L-1 MAJOR; the XOR case stated |
| 48-byte values (`cm`, roots, `rho`, `nkc_d`) | Length only; no content | holds |
| Counters (`c` of §5.6 and §7.5) | Enter only through PRFs; a host choosing them gets a bounded covert channel (stated, §7.7, SPEC-53) | holds under stated signer rule |

No public input reveals a shielded amount. Linking of two transfers of one wallet: L-1 (request
re-payment), counter reuse, exits (by design), deposit/withdrawal amounts (by design). Status of K-c
after this review: **written, unrefereed** (this table), with L-1 owed.

## 2. ML-KEM recipient anonymity (N-c, N-d)

- **Needed?** Yes. Static addresses are published, so "does this package go to this `ek_d`" is exactly
  the anonymity (ANO-CCA) game; the bucket field already gives away `b` bits on purpose (§17.4), and the
  ciphertext must give away nothing more.
- **Has it?** Not established in the documents. From memory (papers not in the folder, not read):
  Grubbs, Maram and Paterson, "Anonymous, Robust Post-Quantum Public Key Encryption", Eurocrypt 2022
  (ePrint 2021/708), and Maram and Xagawa, "Post-Quantum Anonymity of Kyber", PKC 2023 (ePrint 2022/1696),
  argue ANO-CCA for Kyber-type FO KEMs from Module-LWE, the latter in the QROM. Whether either covers
  FIPS 203 ML-KEM (which changed the key derivation from round-3 Kyber) is to be checked against them.
- **The design around the KEM** adds no recipient-identifying field beyond `pkg_bucket`: the body is
  ChaCha20-Poly1305 output of a fixed length class; `ad` holds `cm_j`, `j`, branch and network, all
  public anyway; coins from `PRF_kem(rsk, …)` are pseudorandom to anyone without `rsk`. Recipient
  robustness is not needed for correctness, because §10.3 rechecks `cm_j`.
- **§17.7 hybrid key**: the recipient is a host, so anonymity is not a goal; confidentiality holds if
  either part holds under the standard hash combiner argument (from memory; not written). L-3 applies.
- **Verdict**: holds under assumption (ANO-CCA of ML-KEM-1024), **gap** in evidence. MINOR.
  **Fix**: add both papers to the folder, check that they cover FIPS 203 Encaps, write a one-page
  reduction (package anonymity ≤ ANO-CCA of ML-KEM + PRF of `PRF_kem` + pseudorandomness of
  ChaCha20-Poly1305 output), and record it in `REFERENCES.md`.

## 3. Private retrieval (P-a)

- **Against one curious server**: holds under the stated assumption that the two hosts do not collude
  and that `G = H_dpf-prg` is a PRG (each server sees one DPF key, pseudorandom by BGI16's construction,
  unread). **Non-collusion, plainly: if the two hosts pool their keys, they learn every index every wallet
  read, now or from logs later.** Logged keys also fall if 256-bit seeds or the §17.7 transport fall.
- **Query pattern**: L-2 (counts, overflow pages, scan lengths, timing) and L-3 (session linking). Not
  covered by DPF privacy at all; network-layer identity (IP address) is not addressed anywhere read: add
  a wallet rule that queries go through an anonymising transport or the leak is stated.
- **Verdict**: holds under non-collusion for content; **leak** for pattern (L-2). BGI16 still unread: owed.

## 4. `sig_d` and Falcon key hiding (K-b)

- Nothing published carries `pk` or a signature: `pk` is never on chain (§4.4), the signature is witness
  only, P7 is a hash. `sig_d` appears only in an exit reveal (§13.1.2), with `rk_d` and `nk_d` of that one
  address; `salt_d` is never published, disclosed (§10.5) or in a viewing key (§4.5).
- So spends of one key are unlinkable given (i) zero knowledge of both proof systems (`what-is-proven.md`,
  not re-checked here) and (ii) `H_sig(0x01 || pk || ·)` behaving as a PRF keyed by the 256-bit secret
  `salt_d` (or a random oracle). (ii) is the unwritten assumption K-b names. A compromised proving device
  sees `pk` and links all addresses of the account (stated, §18.1 (A)).
- **Verdict**: holds under stated assumption once (ii) is written; MINOR. **Fix**: add to
  `statement-theorem.md` a lemma "address unlinkability through `auth_d`, `sig_d`, exit reveals" under
  (ii) and ZK, and name (ii) in §18.

## 5. Remaining items

| Item | Status | Owed |
|---|---|---|
| F-d, B's Falcon gadget, vectors pinned to 0.3 | status not established; MINOR | re-pin `wallet_vectors.rs` to 0.4.2 `51ab111` and an argument document like `falcon-statement.md` |
| F-e, A/B statement equivalence | owed; MAJOR for the "either system proves the same thing" claim of §18.3 | differential test: shared witnesses and the negative vectors through both circuits, plus a short argument |
| N-b, package confidentiality and binding | owed; MINOR | an argument: one key per `(ad, plaintext)` from the coins, so the zero nonce never repeats under one key; IND-CCA from ML-KEM + AEAD; binding to `cm_j` through `ad` and the §10.3 recheck |

## Not checked

Tests, models and vectors were not run. `spec/request-lemmas.md`, `statement-theorem.md`, Appendix A,
§13.3, §15 (bundles: what a host learns from wallets' transfers) and §19 were not read for this review;
the zero-knowledge of either system is taken from `what-is-proven.md`. The two ML-KEM papers and BGI16
are not in the folder and were not read.
