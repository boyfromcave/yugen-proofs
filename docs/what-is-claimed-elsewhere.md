# What is claimed elsewhere: the statement and protocol claims beside the proof systems

Part of Yugen. `yugen-proofs`, 2026-11-19. Sibling of `what-is-proven.md`, written for
`qc-and-status-referee.md` section 5: that page covers "a witness for the relation exists and is hidden"; this page
covers the claims it does not, namely that the relation means what the specification says, what the public data
reveal, and the protocol layer outside both proof systems. It adds no result; every entry points to where the claim is
specified and to the evidence that exists.

**Status words and the rule are those of `what-is-proven.md`**: **proven** only with a written proof, nothing owed,
and a referee report that passed it named in the row; **written, unrefereed**; **conditional**; **stated**; **owed**;
**status not established** (the documents do not let this page say). Two further evidence words, which are never a
status by themselves: **tested** (tests exist and are named; tests do not prove a claim) and **model-checked within
bounds** (exhaustive only within the model's bounds). "Review" below means an internal review of the specification
in `yugen-review/` or a referee report in `yugen-proofs/docs/`; neither is an outside review.

**Repositories as read** (all under `$YUGEN_ROOT/`, read-only for this page, by search and excerpt; no
test or model was run for this page): the specification `yugen-spec` main at `51ab111` (specification 0.4.2;
`spec/yugen-protocol.md`, `spec/statement-theorem.md`, `spec/check_*.py`, `yugen-ref/`, `vectors/`); `yugen-falcon` at
`3cead48`; `yugen-pir` at `2b291af`; `yugen-models` at `07eb594`; `yugen-review` at `e52cb19`; `yugen-proof-a` at
`15b9993`; `yugen-proof-b2` at `047d3b2`. Recorded test and check results below are quoted from the repositories'
own records, with the file named; they were not re-run.

## 1. Falcon-512 verification in the leaf statement

| Part | Claim | Where specified | Evidence | Status |
|---|---|---|---|---|
| F-a | A real spend carries a Falcon-512 signature `(r, s2)` under the key `h` bound to its `auth_d`, checked in coefficient form (checks F1 to F5); the message P7 is computed by the verifier from the transfer bytes, never taken from the prover; a satisfying instance therefore implies a valid signature (Theorem A0), and by Falcon unforgeability no one without the signing key can spend (Corollary A0′) | `yugen-protocol.md` §4.4, §11.1.2, §11.3 (C8, C9), §11.4, §11.5, Appendix A.1, A.2; `statement-theorem.md` §4 | `statement-theorem.md` §4: Theorem A0 and Corollary A0′ on paper, assuming A1 (collision resistance of the framing) and A3 (Falcon unforgeability); the document says "**None of it is machine-checked**" and the Lean formalisation (§6; review requirement R-17) is open. Review: `yugen-review/spec-0.4-review.md` re-ran `spec/check_statement.py` ("17 Falcon coverage" pass) and found that `statement-theorem.md` had not been brought to 0.4 (its M3); no referee report on the theorem | **conditional** on A3 (an assumption on Falcon) and **written, unrefereed** (Theorem A0) |
| F-b | The specification's own reference implementation and independent evaluator accept exactly the specified signatures | as F-a | **tested**: `yugen-falcon` `tests/kat.rs`, `kat1024.rs`, `cross.rs` (the KATs verified under PQClean's C verifier and upstream `fn-dsa`), `cross1024.rs`, `vendor_source.rs`; `yugen-spec` `yugen-ref/tests/falcon_kat.rs` (KATs 0 to 3 through the full statement), `spec/check_statement.py` (an independent evaluator), `vectors/falcon_coverage.json` (16 signatures; F2's failure branch has no vector, its probability being below `2^-178`); `yugen-spec/README.md` records 0.4.2 "(24 files, 88 tests)" passing on three targets on 2026-11-19 | tested; no proof is claimed (status of a proof: owed only if one is asked for) |
| F-c | System A's circuit implements F1 to F5 exactly (in-circuit = specification) | `yugen-proof-a/docs/falcon-statement.md` §1, §3 | `falcon-statement.md` §4: the multiplication's soundness argued ("exact NTT, no soundness error of its own"); §5 tests `tests/kat.rs`, `spec_vectors.rs`, `negative.rs`, `mutation.rs` (18 groups), and `wallet_vectors.rs`; §5 says the tests are "not a test of leanVM's proof soundness"; §6 open: a mutation set over wiring | **stated** (§4 argued for one component; the rest tested); no referee report |
| F-d | System B's circuit implements F1 to F5 exactly | `yugen-proof-b2` (its Falcon gadget) | **tested**: `yugen-proof-b2/tests/falcon.rs` (coverage vectors; every twiddle and packing value against a second definition), `wallet_mutation.rs` (one mutation per constraint group), `wallet_vectors.rs` (its header pins "yugen-spec 8d298f0, specification 0.3": older than the specification at `51ab111`) | **status not established** (no argument document found; vectors pinned to specification 0.3) |
| F-e | A / B statement equivalence: both systems accept exactly the same wallet statements, so that either one proves the same thing (`yugen-protocol.md` §18.3: both verify one signature, Falcon is a shared dependency) | `yugen-protocol.md` §18.3 | none found beyond both systems running the specification's vectors; `falcon-statement.md` §6 item 2: "The same statement checked against system B on a shared witness … this repository has not read `yugen-proof-b`" | **owed** (no document, no differential test) |

Not to be confused with C2 of `what-is-proven.md`: the "in-circuit / native equivalence" there is the recursion
verifier guest, not Falcon.

## 2. The hidden salted key hash `sig_d`

| Part | Claim | Where specified | Evidence | Status |
|---|---|---|---|---|
| K-a | **Binding**: `sig_d = H_sig(0x01 || pk || salt_d)` and `auth_d = H_auth(rkh_d || sig_d)` bind a spend to exactly one key | `yugen-protocol.md` §5.1, §3.2 (registry `0x12`, 32-byte output), §11.3 C4, C8, §18.2 (the binding set) | Theorem A0 (`statement-theorem.md` §4) uses collision resistance of `H_sig` (A1) and the injectivity of the key encoding that C8 provides; negative vector `pk-non-canonical-coefficient`; `vectors/auth.json`; `yugen-proof-a/tests/spec_vectors.rs` checks the in-circuit commitment equals `sig_d` on those vectors. Review: `security-profile-referee.md` §2 table marks the `sig_d` row of the 32-byte digests "agree" | **conditional** on A1 and **written, unrefereed** (Theorem A0) |
| K-b | **Hiding**: `sig_d` hides `pk` behind a per-address 256-bit salt, so addresses and exits are unlinkable (an exit reveals `sig_d`, never `pk`) | `yugen-protocol.md` §5.1 (prose: "`sig_d` hides `pk` behind a per-address salt"), §18.1 goal (A) | no argument found; `statement-theorem.md` and `spec/request-lemmas.md` (its L3 is about `cm`, not `sig_d`) do not state it. Review: `yugen-review/findings.md` R-5 proposed the construction; `security-profile-referee.md` V5: "The choice holds; the label is misframed" (about Falcon-512's level behind the hiding hash, not a hiding proof) | **status not established**: asserted in prose; neither an argument nor the assumption it would rest on (`H_sig` as a PRF or random oracle keyed by the salt) is written |
| K-c | The public inputs reveal nothing beyond what the specification lists | `yugen-protocol.md` §11.3, §18.1 | none: Theorem ZP (`what-is-proven.md` Z-3) hides the witness, not what the public inputs reveal (`qc-and-status-referee.md` section 5) | **status not established** |

## 3. Note encryption: ML-KEM-1024 and the package's binding

| Part | Claim | Where specified | Evidence | Status |
|---|---|---|---|---|
| N-a | Correctness: the package is `ML-KEM-1024.Encaps_internal(ek_d, coins)` with `coins` derived deterministically from the PRF, the key `H_pkg-key(K)`, then ChaCha20-Poly1305 with a zero nonce; the recipient decrypts it | `yugen-protocol.md` §10.1 to §10.3; `spec/decisions.md` SPEC-137 | **tested**: `spec/check_kem_aead.py` (cross-check against kyber-py and OpenSSL ChaCha20-Poly1305); `yugen-ref/tests/acvp_ml_kem.rs` with `tests/data/acvp-ml-kem-1024.json` (the README names a 768 file; the file present is the 1024 one); `vectors/package.json`, `keys.json` (file names only). Review: `spec-0.4-review.md` "Checked and correct": "ML-KEM-1024 sizes and the ek check" | tested; no proof claimed |
| N-b | Confidentiality and binding: `ad = cm_j || j || BRANCH_ID || network` binds the package to its output; since the coins depend on the plaintext and `ad`, a nonce is never reused under one key; the recipient accepts only if the recomputed `cm` equals `cm_j`; a failure is unobservable | `yugen-protocol.md` §10.1, §10.2, §10.4 | no security argument found | **owed** |
| N-c | Recipient anonymity of the package (category 5) | `yugen-protocol.md` §10 (about line 1243: "from memory: Grubbs, Maram, Paterson on the anonymity of Kyber; not in the" folder), "to be verified against FIPS 203" | none; the source is cited from memory in the specification itself | **status not established** |
| N-d | The hybrid X25519 + ML-KEM transport key | `yugen-protocol.md` §17.7 (SPEC-151) | `spec-0.4-review.md` S3 found the combiner "not specified anywhere"; §17.7 was added after it; no argument and no review of §17.7 found | **status not established** |

## 4. Private retrieval (`yugen-pir`)

| Part | Claim | Where specified | Evidence | Status |
|---|---|---|---|---|
| P-a | Hosts serve the tag, path, short-address and mailbox tables by two-server DPF PIR; a host that does not collude with the other learns nothing of what was read; a logged DPF key reveals the read only if its seeds are later broken; 256-bit seeds and a SHAKE256 PRG `G(s)` (0.4) | `yugen-protocol.md` §17.1 to §17.6 (§17.6: SPEC-142), §18.1 (L); `yugen-pir/docs/pir-selection.md` §0 to §8 | no privacy argument found; the specification says BGI16 (the DPF construction) "was not read"; `pir-selection.md` §8, "Claims not confirmed from a primary source"; the 256-bit PRG's cost is unmeasured (task W-4). Review: `security-profile-referee.md` V6 (c) found no PRG at 256 bits (fixed by SPEC-142); `spec-0.4-review.md`: "DPF PRG well-formed at 256 bits", S7 "no vector for the DPF split"; `yugen-review/findings.md` R-21, R-25, R-31 (timing and slots) | **status not established** (the published construction is cited unread; no argument written) |
| P-b | Correctness of retrieval | `pir-selection.md` §3.1 (`dpfpir/`) | `dpfpir/src/main.rs`: a benchmark with a correctness assertion ("wrong record"); no `#[test]` functions; measurements in `bench/results/` | tested by benchmark only |
| P-c | The single-server lattice fallback | `pir-selection.md` §2.2; `yugen-protocol.md` §17 | stated "off" until re-parameterised (its parameters are below ML-KEM-512); `tools/coresvp.py`, `bench/results/coresvp.txt` | not claimed (off) |

## 5. Turnstile, pause and frozen mode (consensus rules)

These rules are the fallback if a soundness row of `what-is-proven.md` fails. The specification states their limit
itself: the caps bound only the **rate** (`K + Kf` a window), and "Nothing here detects such a forger"
(`yugen-protocol.md` §13.3.10).

| Part | Claim | Where specified | Evidence | Status |
|---|---|---|---|---|
| R-a | Turnstile: the node tracks the pool balance `B`; a block taking `B` below 0 is invalid; reorganisations restore the exact state | `yugen-protocol.md` §13.3.2 | **model-checked within bounds**: `yugen-models/models/turnstile.py` (BalanceNonNegative, Conservation, PoolSolventWithoutForgery, ReorgRestoresExactState), `tla/Turnstile.tla` with `Turnstile_*.cfg`; traces `out/turnstile_*.txt`; `docs/findings.md` §"`make check` at 0.4.2 (run 2026-11-19)": exit 0, Python `ALL OK`, "TLC: 130 configurations, `TLC ALL OK`" (log not committed); spec-side `vectors/safety.json`, `yugen-ref` `block.rs` / `safety.rs`, `tools/rule_mutations.py` | **stated**; model-checked within bounds, no proof |
| R-b | Pool conservation (Theorem V′: the pool's balance accounts for every applied transfer) | `statement-theorem.md` (Theorem V, Theorem V′, restated in 0.3.4, SPEC-127) | on paper, "None of it is machine-checked"; `yugen-models/models/ledger.py`, `tla/Ledger.tla` | **written, unrefereed** (model-checked within bounds) |
| R-c | Pause: a miners' signal or a canary starts an expiring pause that voids nothing and stops the maturity clocks; an attacker's pause is bounded | `yugen-protocol.md` §13.3.4, §13.3.7 | **model-checked within bounds**: `models/pauseswitch.py` (SingleClaimNeverFreezes, AttackerPauseBounded, NoSignalRefusedByCanaryCooldown), `models/safety.py`, `tla/PauseSwitch.tla`, `tla/Safety.tla` with their `.cfg` files; traces `out/pause_switch_*`, `out/safety_pause*` | **stated**; model-checked within bounds |
| R-d | Frozen mode: unmatured outputs are voided into claims and paid oldest-first by bucket, without rollback | `yugen-protocol.md` §13.3.8, §13.3.9 | **model-checked within bounds**: `models/safety.py`, `tla/ExitPayout.tla`, `tla/Safety.tla`; traces `out/safety_freeze_*` | **stated**; model-checked within bounds |
| R-e | What these rules give (rate caps, outflow cap, value-cap ratchet, bundle-only halt) | `yugen-protocol.md` §13.3.5, §13.3.6, §13.3.10, §13.3.11 | `models/outflow.py`, `tla/Outflow.tla` and the others above. Review: `security-profile-referee.md` V2, "**Overstated protection.** The caps bound the *rate* … the turnstile only stops at `B = 0`"; `yugen-review/findings.md` R-4 (frozen pro-rata), R-8 (a signal froze the pool; replaced by a pause), R-13 (findings with fixes, not verdicts); `spec-0.4-review.md`: §13.3 "unchanged except one informative paragraph"; no review found of the 0.4.1 and 0.4.2 safety-rule changes | **stated** (as limited by §13.3.10) |

## 6. Status not established (for the lead architect)

1. F-d: system B's Falcon gadget implements F1 to F5 exactly (tests only; vectors pinned to specification 0.3).
2. K-b: hiding of `sig_d` (prose only; no argument, no named assumption).
3. K-c: what the public inputs reveal.
4. N-c: recipient anonymity of the ML-KEM package (source cited from memory in the specification).
5. N-d: the hybrid transport key of §17.7.
6. P-a: privacy of the two-server DPF retrieval (BGI16 cited unread; no argument).

Owed (no document): F-e (A / B statement equivalence), N-b (confidentiality and binding of the package).
