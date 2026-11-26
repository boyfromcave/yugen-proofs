# Referee report on the security-profile decision record (profile Y)

Part of Yugen. Written 2026-11-19 in `yugen-proofs` as an independent referee report
on `docs/decision-security-profile.md` (commit `cb0e173`, `profile-study/` at `8fe8093`; the
repository at `d201c90`). The referee did not write the record. Every finding below is attributed
to the Ycash developers (2026) and is unreviewed.

**Inputs read at these heads.** `yugen-proofs` `d201c90`: the record, `profile-study/`
(script and `output/profile-tables.txt`), `decision-security-category.md`,
`security-category-referee.md`, `qrom-compilation.md`, `zk-quantum.md` §3, `soundness/`
revision 7 (`category.py`, `spbcs.py`, used as a library, unchanged). `yugen-spec` `148a474`
(specification **0.3.4**): §2, §3.1 to §3.3, §4, §5, §6, §7.1 to §7.9, §8, §11.1, §11.2, §11.5,
§12, §13.1.4, §13.2, §13.3.1, §13.3.5 to §13.3.8, §15.2, §15.3, §15.5, Appendix A.0 to A.3;
`spec/decisions.md` (SPEC-1, 3, 5, 17, 19, 21, 28). `yugen-proof-a` `4654f15`: `docs/parameters.md`
§2, `docs/statement-layout.md` §3, §9.2. `yugen-proof-b2` `4101b45`: `docs/statement-layout.md`
§1, §7, §8; `docs/wallet-memory.md` §1 to §5; `docs/parameters.md` §2a.5, §8.1 to §8.4,
§9.3 to §9.7. `yugen-pir` `2b291af`: `docs/pir-selection.md` (the DPF rows). `yugen-falcon`:
`docs/circuit-notes.md`, Falcon-1024 section. The plan (revision 6): §11 (E1), §14 (SQ-45,
SQ-49), the execution-status rows 0.4, 0.10, 0.11, 0.15.

**Sources in the reference-paper collection (REFERENCES.md) read for this report (text layer).**

- **[CFP]** NIST, *Submission Requirements and Evaluation Criteria for the Post-Quantum
  Cryptography Standardization Process* (December 2016), §4.A.5 pp. 16 to 19: the five
  categories, footnote 2 (the categories are assumed ordered by practical security), the
  MAXDEPTH range from 2^40 ("in a year") to 2^96, the gate table of p. 18.
- **[FIPS204]** NIST FIPS 204, §4 Table 1 ("collision strength of c̃" 128 / 192 / 256 for
  categories 2 / 3 / 5) and Appendix D.1 ("a collision attack against SHAKE256 with a 384-bit
  output would make it so that parameters targeting NIST security strength category 5 could only
  meet category 4", quoted).

**From memory, not in the folder, marked where used:** FIPS 202 (capacities and security claims
of SHAKE256, SHA3-256, SHA3-384), FIPS 203 (ML-KEM sizes and levels), RFC 9861 (TurboSHAKE),
Brassard–Høyer–Tapp quantum collision search, the Keccak team's multi-rate padding argument,
Grubbs–Maram–Paterson on the anonymity of Kyber/ML-KEM ciphertexts, the Micciancio–Walter
bit-security definition, phone and browser memory limits. Figures are marked **M** measured
(source named), **C** counted, **E** estimate (method stated).

---

## 0. Verdicts first

| # | Claim of the record | Verdict |
|---|---|---|
| V1 | Soundness forgeries "must finish inside the 96-block anchor window, in both systems" (§1, O-51) | **Wrong as the specification stands; right in structure.** Every proof absorbs the statement before its first challenge (spec §11.1, A-3, A.3), so a forgery cannot precede its statement. But the statement is not always fresh: anchors below the activation height have the constant root `E_20`; the first post-activation root is a constant computable from the specification; and in any stretch without applied outputs (a pause, a frozen-mode attempt, a quiet network) the root does not change, so its "window" is as long as the quiet stretch. A forgery against `E_20` can be computed offline from the day the release publishes the activation height and branch ID (both enter `m`), and spent in the first 96 blocks after activation. Fix F-1 (§1.3): bind the hash of block `h_a` into the transfer hash, hence into P7 |
| V2 | What a category-1 break gains: counterfeit "withdrawn up to the caps", answered by canaries and the pause | **Overstated protection.** The caps bound the *rate* (`K` a window), not the total: a forger who has broken both systems and does not fire a canary drains the pool balance `B` at `K` a window until a release freezes it; nothing detects it automatically (the turnstile only stops at `B = 0`). The same holds for a binding collision. The incentive constraints R1 to R3 hold for one window only at the provisional values (spec §13.3.1). The asymmetry between (S) and (B) is therefore online versus offline and repairable versus not, not "bounded versus unbounded" |
| V3 | "The pair adds one bit, not a category" | **Holds** for a generic attacker. The list of shared parts is incomplete: add Reed–Solomon unique-decoding proximity (BCIKS20) under both soundness proofs, the one calculator and tree accounting (O-13), the statement-binding digests of §15.3, and system A's 256-bit public input (A.1) |
| V4 | The 48-byte binding set (§2.2, O-50) and its label "category 4" | **Label holds; the set is wrong in three ways.** (a) Missing: `rho` (a collision of `H_rho` over attacker-chosen dummy `dx` gives two identical commitments to one recipient, a Faerie-gold loss), and the transfer hash under split custody (an online host builds the transfer an offline signer signs). (b) Over-included by the record's own logic: `lpi`, `bundle-list`, `bundle-kids`, `bundle-node`, `bstmt` all hash fresh public inputs (anchor root first), so their collisions are online like soundness. (c) Inconsistent with system A, whose proofs carry a 32-byte public input (spec A.1: "256 public bits"): a 48-byte `bstmt` does not raise A's binding of it. The capacity argument holds: no binding digest uses Keccak-256, and SHAKE256 truncated to 384 bits is the category-4 case NIST itself names ([FIPS204] App. D.1); the generic sponge bound (capacity 512) is from memory (FIPS 202) |
| V5 | Falcon-512 "level 1 behind a level-5 hiding hash"; Falcon-1024 ready as scheme `0x02` | **The choice holds; the label is misframed and "ready" is not yet true.** Against anyone outside the wallet, a spend already needs `salt_d`, `rk_d` (via `rkh_d`) and `nk_d`, 256-bit secrets no viewing key holds, so Falcon's level does not matter there. Against a compromised proving device (the normal configuration of a hardware wallet with an online phone or desktop prover) Falcon-512 is the only barrier, and key recovery from `pk` is an offline attack with no window, for every address of the account (one key per account, SPEC-5). Scheme `0x02` needs registry, identifier, recursion and migration rules that are not in the specification (§3.3) |
| V6 | Privacy at category 5 (§2.1) | **Holds for the components listed, with three gaps.** (a) No seed-entropy rule: a 12-word mnemonic (128 bits) caps every derived key at category 1 by key search. (b) `ε_hvzk` is open in both systems (the record says so; the label must stay conditional). (c) The DPF at λ = 256 has no specified PRG: the crate built (`dpf-fss` 0.6.1) fixes 128-bit seeds. The salt arithmetic holds; the pool size `Q = 2^20` undercounts lifetime proofs by about 15 bits (2^34 in ten years at Y's capacity); at the true `Q` the floors are 74 B (against 2^256) and 78 B (against [CFP]'s 2^272 gates), and the chosen 80 / 96 / 80 B still meet the `2^-128` target |
| V7 | Feasibility figures (W4, reserve, capacity, hosts, B's memory) | **Arithmetic reproduces** (1,293,640; 1,352,520; 1,392,538 → 1,393,000; 5,150 → 4,388; 12 to 15 and 10 to 11 hosts). Three corrections: the reserve mixes a calculator A leaf (9,717 B under the measured one) with a calculator B leaf (about 13,600 B over a measured-plus-deltas figure); B's "about 4×" is against the unreduced 1.1 GB process and is about 2× after the named steps (E); the TurboSHAKE256 fallback was counted on AND rows only, and system A's node layout at 48 bytes can cross `2^22` if a cell straddles the block boundary (§5) |
| V8 | Alternatives (§3, §5) | **Not all priced.** The tree hash is a one-way door with three buildable variants (FIPS 4-ary two-block, TurboSHAKE256 4-ary, Keccak-f[1600] at capacity 384 ternary) whose B committed words decide whether B stays at `2^17`; a weight `W` of 4.18 MB restores 5,150 transfers under Y. "Category 2 soundness" has no meaning for a search problem |

**Overall: adopt profile Y with the corrections of §7**, the first of which (F-1, a fresh
value in every non-canary statement) is a consensus change that the record's own case for
category-1 soundness depends on.

---

## 1. Point 1: soundness at category 1 against binding at category 4

### 1.1 What in a proof's statement is fresh

| Public input (spec §11.1) | Fresh? |
|---|---|
| P1 `anchor_root` | Only if a note was appended since the last root. Roots repeat across grid heights (spec §7.3 says so: "even when two grid heights have the same root"). Below activation the root is `E_20` (spec §6, SPEC-17), a constant. After the activation block, if it carries no transfer, the root is the tree holding only `cm*` (spec §13.2), a constant |
| P2 `nf_1`, `nf_2`; P3 `cm_1`, `cm_2`; P4 to P6 | Chosen by the prover; a forger chooses them freely (dummy `dx` is unconstrained witness, spec §11.2) |
| P7 `m` | A function of the transfer hash, which covers `anchor_height` (a predictable integer) and `anchor_root` (spec §7.3); fresh exactly when the root is |
| P8 `auth_mode` | Consensus constant |
| P9 `reg_root` | Changes only with exit commits |
| Proof salt `s` (A.3) | Prover-chosen: no freshness |

The spBCS prefix `u_1 = H_ch(tag || label || s || pre(x))` (spec A.3) puts the statement before
the first challenge, so a generic Fiat–Shamir forgery (grinding challenges round by round) cannot
start before the statement is fixed: the first prover oracle may be computed early, but every
challenge depends on `x`. That part of the record holds. What fails is the premise that `x` is
unknown until a recent block.

**Finding R-1 (Original, the Ycash developers, 2026; unreviewed).** The anchor rule (spec §8.1:
`h_a mod 16 = 0`, `1 ≤ h − h_a ≤ 96`) does not refer to activation, so in the first blocks after
activation a transfer may anchor at a pre-activation grid height with root `E_20`. A real spend
cannot have a path to `E_20`, but a forged proof can claim one, and its whole statement except the
prover's own choices is known once the release fixes the activation height and `BRANCH_ID`
(the anchor height and the branch enter `m`), months before activation. A forger with years of offline work enters the pool with
counterfeit notes in its first 96 blocks; the turnstile lets them out only as honest deposits
arrive (`B = CANARY_VALUE` at activation, spec §13.3.2), so the counterfeit waits and drains
later. The same holds, for a shorter but unbounded time, for the post-activation root `R_0` and
for every root during a stretch with no applied output: during a pause (spec §13.3.7) no transfer
is applied, so the root at the pause's start is the root at every grid height of the pause and
for 96 blocks after it, and the pause is renewable. Sources consulted for novelty: [CFP],
[SG26] Theorem 6.6 as used in `qrom-compilation.md`; neither discusses statement freshness.

### 1.2 Cost and gain of a category-1 soundness break

**Cost, generic.** Each system's rows give 152.52 bits a round over a tree of 20,000 proofs
(revision 7). A forgery in both systems is two independent searches on one statement, about one
bit more than one: the record's "one bit" holds. With a fresh statement (after F-1):

- classical: 2^128 hash calls inside 7,200 s is 2^115.2 calls a second (C), beyond any machine;
- quantum: [CFP] p. 17 sets MAXDEPTH at 2^40 gates for "a year"; two hours is 2^27.9 of that
  (C). Read through [CFP] p. 18's formula for AES-128 (2^170 / MAXDEPTH), a Grover search
  confined to that depth costs about 2^142 quantum gates. This is an extrapolation below the
  range NIST lists (its footnote 5 warns the formula may misstate small depths), labelled E.

So with a fresh statement the window raises the real cost of a *generic* forgery well above
category 1's quantum figure. It does nothing against a non-generic break (a soundness bug, an
implementation error): such a break is cheap and needs no window. That case is what the second
system and the canaries are for.

**Gain.** Counterfeit notes inside the pool are indistinguishable from honest ones. Withdrawals
are limited to `K` a window (12.5 % of the value cap a day at the provisional values, of which a
quarter immediate; spec §13.3.5); maturing outputs are voided only if frozen mode is entered.
Frozen mode is entered by a canary, by a single-system claim while the other system's break
stands, or by a release (spec §13.3.8). A forger who breaks both systems and claims nothing
fires none of these, so the bound of §13.3.5 has no end height: it drains `B` (the whole pool,
up to `RATCHET_CMAX` = 1,344,000 YEC) in about `1000 / OUTFLOW_CAP_PERMILLE` = 8 windows of
pool-sized withdrawals once the cap is full, unless people notice unusual withdrawals and miners
signal a pause (80 % of 288 coinbases) and a release freezes the pool. The record's "withdrawn up
to the caps" (§4 table) must read "the whole pool, at most `K` a window, until a release
freezes it". The same is true of a binding collision; the two goals differ in *when* the attack
can be prepared and whether it can be repaired, which is the record's real argument and holds.

**Canaries and the pair.** The canaries detect only a forger who chooses to claim. A canary
claim's roots `root*`, `root_A`, `root_B` and the recursion canary's `m` are constants, so canary
forgeries are offline-precomputable by design. After F-1 that is an advantage: a generic forger
with bounded parallelism finds the canary cheaper than a real mint and the incentive points at
firing. Before F-1 it is not, because `E_20` offers the same offline property with the whole pool
as the prize. Shared parts not on the record's list (§2.4): both soundness proofs rest on
unique-decoding proximity of Reed–Solomon codes (BCIKS20, as cited in the record's table); one
calculator and one tree-accounting argument (O-13) certify both rows; the bundle digests of §15.3
are common to both systems' bundle proofs.

### 1.3 The fix (F-1)

Add the hash of block `h_a` to the transfer hash: `transfer_hash = H_transfer(... ||
LE32(anchor_height) || anchor_root || anchor_block_hash || ...)`, 376 bytes, for every transfer
without a canary flag. P7 is computed from it by the verifier and absorbed before any challenge
in both systems and both modes (spec §11.1.2 says P7 is supplied in mode 1 too), so every
non-canary statement becomes unpredictable until block `h_a` is mined, quiet stretches and
pre-activation anchors included. No circuit changes (P7 is a 64-byte public input already;
nothing in-circuit reads the transfer hash). Canary claims keep their constant roots without the
block hash, so they stay the cheapest generic target. Also refuse anchor heights below the
activation height (one node rule). The miner of block `h_a` learns it one block early; that is
inside the window. A hardware signer cannot check the block hash, exactly as it cannot check the
anchor root today (spec §7.7). Provenance: Original (the Ycash developers, 2026), relates to the
anchor binding of SPEC-19; unreviewed.

---

## 2. Point 2: the binding set and its label

### 2.1 The label

[CFP] p. 17 defines category 4 as "collision search on a 384-bit hash function (e.g. SHA384/
SHA3-384)" (quoted). [FIPS204] App. D.1 treats a collision on **SHAKE256 with a 384-bit output**
as exactly the category-4 case. So "category 4" is the right label for a collision-dependent
digest of 384 bits computed with SHAKE256, and for SHA3-384. NIST gives collision costs in
classical gates only (2^210 for SHA3-384, p. 18).

### 2.2 The sponge capacity

No digest of the binding set is computed with Keccak-256: the framed calls are SHAKE256 (spec
§3.1), the tree nodes SHA3-256 today and SHA3-384 or SHAKE256 in Y. Keccak-256 is system A's
proof-internal hash and wrapper (A.1), which is soundness, not statement binding. From memory
(FIPS 202): SHAKE256 has capacity 512 and claims collision resistance `min(d/2, 256)` bits for a
`d`-bit output, so 192 bits at `d` = 384; SHA3-384 has capacity 768 and 192-bit collision
resistance; a generic inner-state collision of a capacity-512 sponge costs 2^256 classically and,
by BHT-type search, about 2^(512/3) ≈ 2^171 quantum queries (from memory), both above the output
collision. What cannot be verified here without FIPS 202: the capacity values and the security
claim table themselves. What can: [FIPS204] App. D.1 shows NIST treating SHAKE256-384 collisions
as category 4, which is only consistent with the capacity not lowering the 192-bit bound.

One caveat the record does not draw: a Keccak-based sponge with capacity 384 (rate 152) also
gives a 192-bit generic collision bound (capacity/2, from memory), so 48-byte binding does not by
itself require a FIPS function; it is a choice (§6.1).

### 2.3 The set itself

| Digest | Record | Referee | Reason |
|---|---|---|---|
| `cm`, `nkc_d`, note-tree leaf and nodes, `anchor_root` | 48 | **48** | offline: both inputs chosen by the attacker, no fresh value |
| `reg-leaf`, `reg-node`, `reg_root` | 48 (mode 1) | **48** | offline: an attacker grinds `rk_d` until its tags are adjacent and controls those range leaves; a single collision `(lo, hi) = (0…01, ff…fe)` is a universal false non-membership. Free in mode 0 (the 101-byte node stays one permutation) |
| `rho` | 32 ("unique by `nf_1`") | **add, or a wallet rule** | Finding R-2 below |
| transfer hash (`H_transfer`) | 32 ("the signer's own transfer twice") | **48, or keep 32 under F-1** | Finding R-3 below |
| `lpi`, `bundle-list`, `bundle-kids`, `bundle-node`, `bstmt` | 48 | **32 suffices; 48 is harmless** | every input starts from fresh public inputs (`pi` begins with `anchor_root`; after F-1, `m` is fresh too), so a collision must be found after the transfers exist, like a soundness forgery. The record classes them as offline. Keeping 48 costs a few permutations in bundle circuits only |
| system A's `E_A(pi)` (SHAKE256 to 32 bytes) and its Keccak-256 statement wrappers (A.1) | not listed | **list them; 32 is forced by leanVM's 256-bit public input** | a 48-byte `bstmt` is bound into system A's proofs through a 32-byte value, so the 48 bytes buy nothing in A. Window-bound like the row above, and a collision there fools A only (B absorbs the 36 words of `pi` directly, A.2) |
| `nf`, `auth_d`, `sig_d`, `rid`, `rcm`, short address, `proof_hash`, `exit`, `exit-tag`, `tout_hash`, `dep_sighash` | 32 | **32** | agree; checked: an `exit-tag` or `auth_d` collision is the owner's own; a nullifier collision needs a second preimage of an unknown target; `tout_hash` and `dep_sighash` are second-preimage cases or carry the transfer hash |

**Finding R-2 (Faerie gold through `rho`; Original, the Ycash developers, 2026; unreviewed).**
`rho_j = H_rho(nf_1 || j)` (spec §5.4). For a dummy first spend `nf_1 = H_nf-dummy(dx)` with `dx`
free witness (spec §11.2; the derivation of §5.6 is a wallet rule the circuit does not check).
An attacker searches offline for `dx ≠ dx'` with `H_rho(H_nf-dummy(dx) || j) = H_rho(H_nf-dummy(dx')
|| j)`: 2^128 at 32 bytes. Two transfers to one victim address with the same `v`, the same `rcm`
(unconstrained, spec §5.5) and that `rho` produce identical `cm` at two tree positions and one
nullifier (`nf = PRF_nf(nk_d, rho || cm)` has no position). A recipient that credits both (an
exchange crediting deposits) loses one. The spec's sentence "`rho_j` is unique, so the nullifier
of every note is unique" assumes collision resistance it does not have at the level claimed.
Fixes: (a) a normative wallet and host rule, "a commitment equal to an earlier applied commitment
is never credited" (no circuit change; complete, since only the recipient is harmed); or (b) `rho`
at 48 bytes (one permutation either way; `cm` stays two permutations at 176 bytes; `nf` stays one
at 132 bytes; about 8 more committed words in B). Recommended: (a) now, (b) only if W-2 is open
anyway and B has the words.

**Finding R-3 (the transfer hash under split custody; Original, the Ycash developers, 2026;
unreviewed).** The specification designs for an offline signer that recomputes the transfer from
what it displays and signs `m` (spec §4.4 rule 1, §7.7). The bytes it cannot check (anchor root
and height, and after F-1 the block hash) are chosen by the online host, which also builds the
transfer it will broadcast. A collision between a transfer the signer accepts and one paying the
host is a host-chosen collision, which the record's row "the signer's own transfer twice:
nothing" misses. Falcon's own nonce does not help: it salts the hash of `m`, and `m` is a
function of the colliding transfer hash. Today it is bounded by the anchor window (the broadcast
transfer needs a fresh root); after F-1 by the block hash as well. 48 bytes cost nothing in any
circuit (the transfer hash is computed by nodes and signers only; `m` stays 64 bytes); it changes
`yugen-falcon`'s `message_digest` input from 64 to 80 bytes and its vectors. Recommended: 48 bytes,
so split-custody signing does not rest on the window argument.

---

## 3. Point 3: Falcon-512 behind a hidden key

### 3.1 Who holds what

The record's table (§2.3) is right about `pk`. It misses what else a spend needs. The witness of a
real spend is `h` (the key), `nk_i`, `rho_i`, `rcm_i`, `pos_i`, the path, `salt_i`, `rkh_i`, and in
mode 0 the signature (spec §11.2); `auth_d = H_auth(rkh_d || H_sig(0x01 || pk || salt_d))`.
`salt_d` comes from `saltm` and `rkh_d` from `rkm`, neither in any viewing key (spec §4.5). So:

| Attacker | Needs beyond what it has | Barrier | Level |
|---|---|---|---|
| Outsider, or a full-viewing-key holder, with a leaked `pk` and a Falcon break | `salt_d` (a 256-bit PRF output), `rkh_d`; outsiders also `nk_d` | preimage / PRF key search | 5 (key search on 256-bit secrets; [CFP] category 5 by analogy with AES-256) |
| A compromised proving device (the online half of a hardware wallet, a delegated prover) | the Falcon signing key only | Falcon-512 key recovery from `pk` (offline, unbounded time, permanent) or forgery | 1 ([GLS26] §1 via the record) |
| The signing device itself | nothing | — | — |

So the honest label is "**5 against everyone outside the wallet's devices; 1 against a
compromised proving device**", not "1 behind 5". The difference matters: the threat Falcon's level
answers is exactly split custody, and for it the attack is offline and covers every address of the
account, since one Falcon key serves the whole account (SPEC-5) and a transfer opens both spends
under one `h` (spec §11.2). A `pk` leaked years later exposes funds only together with the other
witness secrets, which that same device holds. A wallet that suspects its prover moves funds to a
new account (a new `falcon_seed` path); the specification has no per-address-group key, which
would be a wallet-level option at no circuit cost (each address commits to its own `pk`; a
transfer's two spends must share one).

### 3.2 Is leaving Falcon-1024 out consistent with the brief

Yes, on the figures: Falcon-1024 makes A's wallet prover `2^23` (E, S3) while A at `2^22` is
already 622 to 894 MiB (M) against 512 MB, and the protection applies to split custody only. In
Y its marginal cost in B is nil (B is at `2^18` anyway, S3), so the cost is A's alone. The
lead architect should see it as a choice between split-custody security and A's wallet memory.

### 3.3 What "reserved as `0x02`" must already contain at launch

Not in specification 0.3.4, each needed so that `0x02` is a release and not a redesign:

1. **Registry.** `0x12 sig` has a fixed body of 930 bytes (`1 + 897 + 32`). A 1,793-byte key
   needs its own identifier (`sig-1024`, body 1,826) reserved now.
2. **Key path.** `falcon_seed` (`0x04`) derives one key per account; a 1024 key needs a path with
   the scheme in it.
3. **Scheme on the wire.** The verifier picks a leaf circuit by P8 only (§11.1.1). A transfer
   must name its scheme (a reserved flag bit of §7.1, bits 9 to 15) or carry a statement version,
   and A-4's identifiers gain a scheme dimension.
4. **Bundles.** BC-1 verifies each leaf "against the leaf verification key of mode M"; a
   sub-bundle holding both schemes needs a per-leaf key choice among consensus keys, or bundles
   are single-scheme. Decide now; the recursion slots are built against it.
5. **Migration.** The record's "one switch at a height, as mode 1 is" does not work: mode 1 can
   switch because every address already has `rk_d`; a note at a `0x01` address can be opened only
   under its Falcon-512 key, so after any switch the `0x01` circuit must stay live (two anonymity
   sets) until a migration deadline, after which unmigrated notes leave by mode 1 or the hash-only
   exit. That rule belongs in the specification before launch.
6. **Circuits counted and tested** (the record's A-1): the 128 known-answer vectors at 1024 in
   both test builds.

---

## 4. Point 4: privacy at category 5

| Component on the record-now path | Level | Note |
|---|---|---|
| Packages and addresses: ML-KEM-1024 (from memory, FIPS 203) with ChaCha20-Poly1305 under a 32-byte `H_pkg-key` | 5 | ciphertext anonymity of ML-KEM (that a ciphertext does not reveal its recipient) is from memory (Grubbs–Maram–Paterson); to be checked against the paper when added |
| Transport X25519 + ML-KEM-1024 | 5 | |
| Retrieval: DPF at λ = 256 | 5 **once a PRG is specified** | Finding R-4 |
| Keys, PRFs, `nk_d`, `salt_d`, `rk_d`, nullifier PRF, tags | 5 **if the seed has 256 bits of entropy** | Finding R-5 |
| Zero knowledge of both leaves | statistical, conditional | `ε_hvzk` open in both systems; the record states it. Node proofs are not hiding and need not be (hypothesis N, `zk-quantum.md` 3.3) |
| Proof-internal hashes (Keccak-256, BLAKE3) and the 256-bit field | not on the path | hiding comes from salts, not from output length or field size; Theorem 6.6 (3) and (4) as in the record |
| Outgoing and incoming tags (8 and 6 bytes) | 5 | truncation gives false positives only; the keys are 256-bit |

**Finding R-4 (Original, the Ycash developers, 2026; unreviewed).** `pir-selection.md` records
the DPF as built: `dpf-fss` 0.6.1, "AES-256 Hirose PRG, 128-bit seeds". "λ = 256" is not a
setting of that crate. W-4 must name the length-doubling PRG for 256-bit seeds and its
assumption, for example AES-256 keyed by the seed in counter mode (security reduces to AES-256 as
a pseudorandom function: category 5 by definition) or ChaCha20 keyed by the seed, and E5 must be
measured with it: re-keying a cipher at every tree node costs more than the fixed-key 128-bit
design, so the record's "server PRG work about 2×" is not established.

**Finding R-5 (Original, the Ycash developers, 2026; unreviewed).** The seed is "a byte string of
32 to 64 bytes" (spec §4.1, SPEC-3). Length is not entropy: a seed made from a 12-word mnemonic
carries 128 bits, and every key derived from it, the ML-KEM decapsulation keys and the spend
secrets included, is then found by a 2^128 search: category 1 by [CFP]'s own definition, for
privacy and for spend authority alike. Fix: a normative rule that the seed carries at least 256
bits of entropy (24 words, or 32 random bytes), with a wallet test that refuses to generate
less.

**The salt argument.** The arithmetic reproduces: the proof-salt term of Theorem 6.6 (3) is
`4 Q t / 2^(4 b_s)`, so `t / ε = 2^(4 b_s − 2 − log Q)`, independent of `t`. Reading work over
advantage for a distinguishing game is conservative (the Micciancio–Walter measure for decision
games, from memory, divides by the square of the advantage). The correction is `Q`:
`POOL_LOG2 = 20` (calculator `category.py` line 52) is called "the pool", but Theorem 6.6 (3)
counts every proof the adversary sees, and the record is permanent. At Y's 4,388 transfers a
75-second block, one system makes 2^22.3 leaf proofs a day, 2^34.1 in ten years, 2^36.4 in fifty
(C). With the calculator's own functions (`spbcs.eps_leaf_log2`, run here, unchanged):

| | `Q = 2^20` | `Q = 2^35` | `Q = 2^37` |
|---|---|---|---|
| A leaf salt floor for `2^-128` | 75 B | 78 B | 79 B |
| B leaf salt floor for `2^-128` | 75 B | 79 B | 79 B |
| A leaf term at 80 B | 2^-151.8 | 2^-136.8 | 2^-134.8 |
| Proof salt: `t / ε` at 80 B | 2^298 | 2^283 | 2^281 |
| Proof-salt floor against 2^256 / against 2^272 gates | 70 / 74 B | 74 / 78 B | 74 / 78 B |

So "70 bytes are the floor" becomes 74 B (78 B against [CFP]'s gate count for AES-256), and the
chosen salts (A 80, B 96, proof 80) stand with less margin than stated (A's leaf: 1 byte at
`Q = 2^37`). No parameter changes; W-5 should write the target with `Q = 2^37`.

---

## 5. Point 5: feasibility

**Recomputed (C, from the record's inputs).** W4: 692,504 + 583,680 + 17,456 = 1,293,640;
692,504 + 642,560 + 17,456 = 1,352,520. Y's reserve: 694,435 + 679,687 + 17,456 + 960 =
1,392,538, rounded 1,393,000. Capacity at `W` = 4,000,000: (4,000,000 − 1,393,000 − 875,309 −
713,602) / 232 = 4,388; O2: 5,150. Of the 762-transfer drop, 60 come from the reserve and 702
from the 32 more record bytes. `W` for 5,150 under Y: 4,176,711. Hosts: (4,120 + 6,700 to 9,500)
/ 960 = 12 to 15; with B's reductions (4,600 to 6,200) 10 to 11. All reproduce.

**The reserve's inputs disagree with the measurements.** The calculator puts A's row-8 leaf at
64-byte salts at 682,787 B; it measures 692,504 B (9,717 under). B's measured form-T leaf plus
deltas (583,680 + 23,552 for a 96-byte salt + 47,104 route S + 11,776 for the `2^18` level =
666,112 B) is about 13,600 under the calculator's 679,687 B. The measured-based reserve is
1,389,000 to 1,403,000 depending on which side is taken. W-1's rule (derive it from the certified
rows) is right; the immediate value must use measured leaves plus counted deltas, not the
calculator alone.

**B's memory.** The measured category-1 form-T leaf peaks at 1,095 to 1,106 MB for the whole
process (`yugen-proof-b2` parameters.md §8.3, M). At the pin, the wallet-memory steps a and b took
1,270 MB to 554 MB (`wallet-memory.md` §4, dev run, not through the gate). The record's "about 4×
of 512 MB" is the unreduced process doubled; after steps a and b, B at `2^18` is about 1.0 to
1.2 GB (E: the same proportion), about 2×, and wasm32 linear memory never shrinks
(`wallet-memory.md` §5). Is a 1 to 2 GB prover feasible on a phone? Natively on a current flagship,
probably (foreground limits of several GB, from memory, unverified on devices); on a 4 GB
mid-range phone and in a browser tab, doubtful. Plan step 0.15 (devices) has not started, so no
device figure exists for either system. Note that A at `2^22` (622 to 894 MiB, M) misses E1 too:
Y does not create the memory problem, it doubles B's share of it.

**The fallbacks.** (a) The TurboSHAKE256 node (record §2.2 (i)) was counted on AND rows only. B's
binding limit at `2^17` is two-sided: 131,072 AND rows and 131,072 committed words, and committed
words are the tight one (130,684 used, 388 free; `statement-layout.md` §1). By a count (E: one
committed word per AND row of a permutation; 48-byte siblings add about 244 witness words for two
spends):

| Tree variant at 48 bytes | B AND rows | B committed words | B stack | A |
|---|---|---|---|---|
| T1: SHA3-384 or SHAKE256, 4-ary, two Keccak-f a level (the record) | 136,710 | about 154,900 | `2^18` | two blocks a level; see the layout risk below |
| T2: TurboSHAKE256, 4-ary, two Keccak-p[1600,12] a level | about 112,710 | about 130,930 (about 140 free) | `2^17`, with no margin until L-1 | needs a 12-round precompile (a VM change); RFC 9861 from memory |
| T3: Keccak-f[1600] at capacity 384 (rate 152), ternary, depth 26: `3 × 48 + 5 = 149` bytes, one permutation a level | about 119,900 | about 138,000 | `2^18` unless L-1 frees about 7,000 words (its target is 4,000) | no VM change: the precompile is the permutation; 26 aligned levels |

So the record's claim that T2 keeps B at `2^17` holds only by about 140 words (E) and needs L-1
before it is safe; T3 is the only variant that touches neither FIPS 202's output functions nor
A's VM, and it is not a FIPS function either. (b) Returning to 32-byte binding (O2) is a real
fallback but gives up the one goal the record rightly ranks as irreparable.

**A's layout risk (not in the record).** A's node routine is 24 cycles a level because every
child is whole 16-byte cells inside one block (spec §3.1: the old framing straddling lanes cost
about 1,060 cycles a level). A 4-ary node of 48-byte children with a 136-byte rate (8.5 cells) or
a 104-byte rate (6.5 cells) puts a cell across the block boundary unless the layout pads. A's
headroom under `2^22` is 730,912 words, about 39,600 cycles at 18.45 words a cycle (C); 40 levels
at about 1,000 cycles each would use it all. Spec 0.4 must fix an aligned two-block layout (for
example `c0 || c1 || frame and zeros to byte 136 || c2 || c3`, so the second block starts with
`c2`), and §3.3's separation argument must be redone for it, since the separation of tree-node
calls currently rests on SHA3-256 and SHAKE256 sharing capacity 512 (a SHA3-384 node is another
sponge; the multi-rate padding argument for that is from memory).

---

## 6. Point 6: alternatives the record did not price

1. **Tree hash variants T1 to T3** (§5): priced above by count. Which one fixes the tree is a
   one-way decision (every note ever made hashes under it); it should follow the B count and a
   B `2^18` memory measurement, not precede them.
2. **40-byte digests.** A ternary node of 40-byte children is 125 bytes, one SHAKE256 permutation,
   depth 26, FIPS: +12 Keccak-f a transfer, record +16 B. But 320-bit collisions cost about
   2^160 calls, roughly 2^178 classical gates by [CFP]'s SHA3 scaling (2^146 gates for 2^128
   calls), which is above category 2 and below category 3 (2^207). No FIPS one-permutation tree
   reaches category 3; 48 bytes is the smallest output above 3. The record's 48 is right.
3. **48 bytes only for the offline set** (cm, `nkc`, the note tree, `rho` if chosen, the registry)
   and 32 for the window-bound statement layer: same wallet circuits, smaller bundle digests,
   consistent with system A's 32-byte public input. Recommended (§2.3).
4. **A cheaper in-circuit hash for B's statement.** Not available: both systems prove one
   statement over the same hash functions, and BLAKE3 (B's proof-internal hash) targets 128-bit
   security for every output length, so it cannot carry category-4 binding.
5. **"Category 2" soundness rows.** Category 2 is defined by collision search; a soundness forgery
   is a search problem that Grover speeds up, so no row corresponds to it. The next level is 3
   (216.52 bits a round), priced by the record and infeasible at `W` = 4 MB.
6. **`W` as a consensus parameter.** 4,176,711 bytes restore 5,150 transfers under Y (+4.4 %);
   6,000 need 4,373,911. At one block per 75 s that is 4.81 against 4.61 GB a day of block data
   (C), before pruning; whether proofs may be pruned after validation is not stated in the
   specification and decides what a node operator pays. The lead architect's call; the record
   should show it as an option, not only as "15 % of capacity".

---

## 7. Verdict and the profile the referee would choose

**Adopt Y with these corrections.**

| Goal | Level | Change from the record |
|---|---|---|
| (P) | 5, conditional on `ε_hvzk` and on a ≥ 256-bit seed | add the seed-entropy rule (R-5); specify the DPF PRG (R-4); `Q = 2^37` in the target |
| (B) | 4 for the offline set | add `rho` or the duplicate-commitment wallet rule (R-2); transfer hash at 48 (R-3); statement layer (`lpi`, bundle digests, `bstmt`) may stay 32 and is labelled window-bound, with system A's 32-byte public input recorded; tree hash chosen after the T1/T2/T3 count |
| (A) | 5 outside the wallet's devices; 1 against a compromised prover | relabel; put the six `0x02` items of §3.3 in the specification |
| (S) | 1 per system; generic forgery confined to the anchor window **after F-1** | F-1 (block hash in the transfer hash; no anchor below activation); add the shared parts of §1.2 |
| (L) | as (P) | — |

Why not the alternatives: O2 leaves binding at 2 for the life of every note; O3c doubles A's
prover for split custody only; O4 to O6 fail W5 or W1 (the record's own figures, reproduced).
Y's weakest point is not cryptographic but B's wallet memory at `2^18`; the profile is adopted
on the condition that the tree hash is not frozen before that is measured.

---

## 8. Corrected first tasks (in order)

| # | Task | Done when |
|---|---|---|
| F-1 | **Fresh statements.** Spec 0.4: `anchor_block_hash` in the transfer hash of every non-canary transfer (376 bytes); no anchor height below the activation height; `yugen-ref` and vectors regenerated | a vector shows a transfer anchored at `E_20` refused; two transfers equal except the block hash have different `m`; canary vectors unchanged; both systems' transcript-binding tests pass with the new `m` |
| W-1 | **`LEAF_RESERVE` from the rows** (the record's task), with measured leaves plus counted deltas | the script prints the value from measured A and B leaves; one byte over is refused, the largest measured pair accepted |
| F-2 | **Tree hash decided by count before spec 0.4 fixes it.** Count B's AND rows and committed words, and A's cycles and KECCAK-table words (task P-2), for T1 (with an aligned two-block layout), T2 and T3; measure B's prover footprint at `2^18` with the current circuit padded to `2^18` | a table with the three variants' counts in both systems and B's `2^18` peak footprint (M, through the heavy slot); the lead architect chooses one |
| W-2 | **Spec 0.4 binding set** as corrected in §2.3: the offline set at 48 bytes with the chosen node hash and an aligned layout; `rho` rule (R-2); transfer hash 48 (R-3); the statement layer's length stated with its reason; §3.3 separation redone; seed-entropy rule (R-5); the six `0x02` items of §3.3 | `yugen-ref` regenerates every vector; a test refuses a 32-byte value wherever 48 is registered; a duplicate-`cm` vector shows the second note not credited; the separation argument covers every call class at the new lengths |
| W-3 | Both wallet circuits on W-2 | every statement vector proves and verifies in A and B; A's stack recorded with the KECCAK-table words counted; B's stack and footprint measured |
| W-4 | Privacy at 5, with the DPF PRG named | known-answer tests for ML-KEM-1024 after FIPS 203 is added and read; the DPF at 256-bit seeds built with a named PRG, E5 re-measured |
| W-5 | Salts from the target at `Q = 2^37` | the calculator prints the floors at `Q = 2^37`; the rows carry 80 / 96 / 80 B |
| W-7 | Devices (plan 0.15) moved ahead of the spec freeze | A `2^22` and B at the chosen stack measured on a flagship, a mid-range Android phone and the web build |

## 9. Corrections to the plan and the specification (reported, not edited)

- Specification 0.3.4 §5.4: "`rho_j` is unique" holds only to the collision resistance of
  `H_rho` (R-2). §8.1: no lower bound at activation (R-1). §4.1: no entropy rule (R-5). §3.2:
  `sig` body fixed at 930, no identifier for a 1,793-byte key (§3.3).
- Plan §14 SQ-49 text: "Falcon-512 behind its hidden, salted key hash" should carry the split-
  custody qualification of §3.1; "the turnstile and caps bound" a forgery should read "rate-limit".
- The record (§10) lists its Original contributions O-49 to O-55; the findings R-1 to R-5 and the
  variant count of §5 here are new and need rows in `REFERENCES.md` "Original contributions"
  (this report does not edit that file, by instruction).

## 10. Provenance

**Published, used as is:** [CFP] §4.A.5 pp. 16 to 18 (category definitions, MAXDEPTH, gate
table); [FIPS204] §4 Table 1 and App. D.1; [SG26] Theorem 6.6 (3), (4) through the calculator
revision 7 and `zk-quantum.md`, not re-read. **Adapted:** the MAXDEPTH extrapolation to a
two-hour window (§1.2: [CFP] p. 18's AES-128 formula applied below its stated range; changes:
the depth only). **Original (the Ycash developers, 2026), first in this report, unreviewed:**
R-1 (predictable statements: `E_20`, the first root, quiet stretches) and fix F-1; R-2
(Faerie gold through `H_rho` over free dummy `dx`); R-3 (host-chosen transfer-hash collisions
under split custody); R-4 (the DPF PRG at 256-bit seeds is unspecified); R-5 (seed entropy caps
the category); the split-custody reading of spend authority (§3.1) and the `0x02` readiness list
(§3.3); the window-bound classification of the statement layer and system A's 32-byte public
input (§2.3); the B committed-word count of tree variants T1 to T3 and A's layout risk (§5);
the restated pool size and salt floors (§4). Checked before labelling: [CFP], [FIPS204], the
record, the study, the earlier referee report, specification 0.3.4 and its decisions; none
states these for this design. The Faerie-gold attack class itself is known from Zcash's design
(from memory; not in the folder): what is new here is only its route through `H_rho` and free
dummy witnesses in Yugen.
