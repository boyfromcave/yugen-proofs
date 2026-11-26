# Decision record: the NIST security category of Yugen (1, 3 or 5)

Part of Yugen. Written 2026-11-19 in `yugen-proofs` for the lead architect, who has
said the project should strive for NIST categories 3 to 5. This record states, for categories 1,
3 and 5 (and what 2 and 4 would mean), what every component of a transfer must become, what it
costs in bytes, core-seconds and memory, what is proven, what is not, and which work makes each
level real. It recommends a profile and an order of work.

Figure marks: **M** measured (source cited), **C** counted, **E** estimate (method stated).
Every computed number comes from `category-study/category_study.py`, which uses the calculator
`soundness/` (revision 6) as a library without changing it; its output is
`category-study/output/category-tables.txt` (sections T1 to T8 below refer to its sections 1 to 8).
Regenerate with `cd soundness && uv run python ../category-study/category_study.py`.

Inputs read at: `yugen-spec` 769b37e (specification 0.3.3); `yugen-proof-a` `docs/parameters.md`,
`docs/recursion.md` 9 to 10; `yugen-proof-b2` `docs/parameters.md` 8 to 9; `yugen-falcon`
README and `docs/circuit-notes.md`; the plan (revision 6) sections 0 to 3, 9, 11 and 14.

## 0. Findings first

1. **Today the weakest links are category 1, and there are three of them, not one.** (a) The
   spend authority, Falcon-512 (NIST level I by its designers' parameterisation: the vendored
   `fn-dsa` 0.3.0 source states "degree 512 ('level I security') or 1024 ('level V
   security')", `yugen-falcon/vendor/yugen-fn-dsa-sign/src/lib.rs` lines 29 to 30). (b) Every
   digest whose binding needs collision resistance is 256 bits (specification 3.1: every framed
   hash is "always the first 32 bytes"; the note tree, the note commitment, the bundle list).
   A generic collision on 256 bits costs about `2^128` classical hash calls, which the project
   ranks at category 2 (`soundness-method.md` 8.2, condition H), so these are category 1 to 2,
   never 3. (c) The proof systems' rows are certified for category 1 only, and system B's
   decided Merkle hash, BLAKE3, is claimed by its designers at 128 bits for every security goal
   and every output length (BLAKE3 specification, version 20211102173700, Section 4.1;
   `decision-b-merkle-hash.md` H-1.5; `REFERENCES.md` 1.1e; `CITATION-AUDIT.md` 1f, C-25).
   Note encryption is already category 3 (ML-KEM-768); key derivation, PRF keys and the recovery
   key's preimage (256-bit secrets) are at the key-search level of category 5.
2. **Category 3 is not a parameter-only release, as the plan (section 9) and the design basis
   (section 1) state.** It is a parameter change for the query counts (A: 321/222/219/218 at the
   leaf; B: 261), and the 256-bit challenge field is enough (T2, T3: weakest algebraic rounds
   225 to 234 bits against a need of 216.52). It is new engineering for: 384-bit digests inside
   both proof systems (the A guest's Merkle walk changes cell layout, `yugen-proof-a`
   `recursion.md` 5; B's `check_build` refuses other digests, `yugen-proof-b2` `parameters.md`
   8.4), a third hash for B's trees (SHA-384 or SHA3-384), 48-byte statement digests (a
   specification change: framing, note tree, commitments, bundle list, in both circuits),
   longer leaf salts (64 bytes become vacuous next to 48-byte digests: T5) and Falcon-1024 in
   both circuits.
3. **Category 5 needs a challenge field above 256 bits.** The weakest algebraic round at
   `GF(2^256)` is 232 bits (A's leaf) and 225 bits (both systems' nodes of `2^30`), against a
   need of 280.52: the field must have at least 305 bits for A and 312 for B (T2, T3). That is
   a cubic extension of the 128-bit field (`GF(2^384)`) or a quartic one (`GF(2^512)`) in both
   provers, both guests and the Lean statement. With unique decoding, category 5 node proofs
   exceed `PROOF_BYTES_MAX` (A 2,101 KiB at rate 1/4, B 2,057 to 2,390 KiB, against 1,792 KiB:
   T2, T3, T8). Category 5 inside the current constants needs list-decoding rows, which rest on
   a preprint and on lemmas of ours under review.
4. **Proving cost is the real obstacle, and it is system B's.** At category 1, both systems
   together already need 10,820 to 13,620 core-seconds (E) for N = 1,500 against E2's 7,680:
   12 to 15 hosts, not 8. At category 3 with the certified row and SHA-384: 28,000 to 39,000
   core-seconds, 30 to 41 hosts (E); at category 5: 54,000 to 77,000, 57 to 80 hosts (E).
   System A grows by 1.34 (category 3) and 2.3 to 2.8 (category 5); system B by 3.5 and 7 (T7).
5. **Block capacity collapses at higher categories, and is already below the plan's figure at
   category 1.** Under rule W5 (bundles may use `W - LEAF_RESERVE` = 2,850,000 weight), with
   200-byte transfer records (specification 15.1) and today's root proofs, a block holds about
   6,200 bundled transfers at category 1 (not 9,500; the plan's figure counts block bytes only),
   about 1,970 at category 3 with nodes at rates 1/4 and 1/16, and none at category 5 (T8, E).
   `W` and `LEAF_RESERVE` must rise with the category (section 4.4).
6. **Recommended profile (section 7):** category 3 for the whole transfer as the launch target
   (Falcon-1024, 384-bit digests everywhere, the 256-bit field, 261/321-query rows,
   SHA-384 for B's trees, ML-KEM-768 kept), with **category 5 for long-lived secrets and
   privacy** (ML-KEM-1024, 256-bit PRF keys and seeds, which are already there) and the field
   and the hash interfaces built so that category 5 soundness is a later row. The obstacle that
   decides whether category 3 ships is system B's proving cost.

## 1. Definitions and the rule of the weakest component

### 1.1 What NIST defines: to be verified against the NIST text

The NIST documents are **not** in the reference directory, and this record does not quote them
from memory. The project's existing summary is `soundness-method.md` 8.1 (written 2026-11-18 by
an earlier session that read a primary source; not re-verified here): categories 1, 3 and 5 are
defined by comparison with key search on a block cipher with a 128-, 192- and 256-bit key
(AES-128, AES-192, AES-256), categories 2 and 4 by comparison with collision search on a 256- and
a 384-bit hash (SHA3-256, SHA3-384), quantum attacks are measured as circuit size under a depth
limit MAXDEPTH, and the categories are attack-cost definitions, not proven-security definitions.
**Every statement of this paragraph is to be verified against the NIST text.** Documents the lead
architect should add (section 10): the NIST PQC call for proposals (its security-strength
categories section and the evaluation criteria), FIPS 202, FIPS 203, FIPS 204, FIPS 205, the
FN-DSA (FIPS 206) draft, the Falcon round-3 specification, FIPS 180-4.

### 1.2 How this project turns a category into checkable conditions

Category 1 and 3 are formalised in `soundness-method.md` 8.2 and 8.3 (conditions C, Q, G, H,
calculator `targets.py`). This record extends the same rule to category 5 (**Original, the Ycash
developers, 2026**, by the same pattern; `category_study.py` `CAT5`):

| Target | C: proven classical bits of the tree (book Theorems 25.2.1, 31.2.1) | Q: proven QROM bits (SG26 Theorem 6.6 (2)) | G: attack bits a round (Grover under MAXDEPTH, `soundness-method.md` 8.2) | H: digest bits, attack rule | H: proven rule |
|---|---|---|---|---|---|
| cat1 | 128 | 64 | 128 | 256 (collision `2^128`: the category 2 benchmark) | 264 (book term; 288 under the spBCS term, revision note in 3.5) |
| cat3 | 192 | 96 | 192 | 384 (collision `2^192`: the category 4 benchmark) | 392 |
| cat5 | 256 | 128 | 256 | 512 (collision `2^256` classical, matching AES-256 key search classically) | 520 |

The tree-wide union (`soundness-method.md` 8.5b; **Original**, `REFERENCES.md` O-13): a block's
proof tree has at most `N = MAX_TREE_PROOFS = 20,000` proofs (specification section 2). A round
of every proof must give `e >= kappa_C + 1 + log2 N + log2(1 + k)` bits, `k` the verifier
messages of the proof: 599 for A (87 listed rounds + 512 others), 600 for B (the row budget).
With `log2 20,000 = 14.29`: **152.52, 216.52, 280.52 bits a round** for categories 1, 3, 5 (T1).
Condition Q (`e >= 2 kappa_Q + 1 + log2 6 + log2 N`) needs 145.87, 209.87, 273.87: condition C
binds. No grinding (SQ-39), unique decoding for certified rows.

**Categories 2 and 4.** They are collision benchmarks. For this design they would mean: the
category-1 (or category-3) soundness rows with digests of 256 (or 384) bits and every
collision-dependent digest at that length; the signature and the KEM at level 2 (4) or above.
Falcon has no level-2 or level-4 parameter set (512 is I, 1024 is V), so category 2 or 4 for the
spend authority means Falcon-1024 anyway; nothing in the proof systems is cheaper at 2 than at 3
except the query counts (`kappa_C` between the targets). They are not studied further.

### 1.3 The rule of the weakest component

A transfer is at category `c` only if every part a forger or a decrypter must break is at
category `c` or above: soundness (forging money), spend authority (stealing it), binding
(double-opening a commitment), privacy (decrypting or linking). The parts are listed in
section 2; the weakest link today is listed in finding 1.

## 2. Inventory: every part, its category today, and what 3 and 5 need

Cost model for hashes (stated, not proven; **from memory** where marked): classical collision
`2^(n/2)` calls, classical preimage `2^n`; quantum preimage by Grover `2^(n/2)` sequential calls,
which NIST's depth-limited model compares with AES key search of the same key length
(`soundness-method.md` 8.2, Zalka's optimality, [Zal99] abstract only); quantum collision by
Brassard–Høyer–Tapp about `2^(n/3)` calls with quantum random-access memory (**from memory**,
`REFERENCES.md` 1.3, not in the folder). A sponge of capacity `c` gives at most `c/2` bits of
generic security (**from memory**, FIPS 202, to be verified): SHAKE256 (`c = 512`) supports
outputs of 384 bits at 192-bit collision security and 512 bits at 256-bit collision security.

| Part | Today (source) | Relies on | Category today | Category 3 needs | Category 5 needs |
|---|---|---|---|---|---|
| Spend authority, verified in the wallet proof (C8, C9) | Falcon-512, round 3, padded; pk 897 B, sk 1,281 B, sig 666 B (spec 4; `yugen-falcon`) | NTRU lattice (Falcon) | 1 (level I, `fn-dsa` source comment; Falcon specification to be added) | Falcon-1024 (no level-3 Falcon exists) | Falcon-1024 (level V) |
| Recovery-key mode (mode 1) | `rkh_d = H_rk(rk_d)`, `rk_d` 32 bytes, checked by C10 (spec 4, 11) | preimage of a 256-bit output on a 256-bit secret | key-search level of 5 (Grover `2^128` sequential); multi-target over all published `rkh` loses `log2` of their number | nothing | nothing (or a 48-byte `rk_d` to keep a margin against multi-target search) |
| Note commitment `cm` | `H_cm(...)` framed SHAKE256, 32 bytes (spec 5) | **collision** (an opener of two values inflates) and hiding (`rcm` 32 bytes) | 1 to 2 (collision `2^128`) | 48-byte output | 64-byte output |
| Note tree (4-ary, depth 20) and exit registry (binary, depth 40) | SHA3-256 nodes (spec 6, 12; SPEC-61) | **collision** of node inputs the attacker chooses | 1 to 2 | SHA3-384 or SHAKE256 at 48 bytes: a 4-ary node of 192 B + framing is 2 permutations (rate 104 or 136), 1 today | SHAKE256 at 64 bytes: 256 B + framing, 2 permutations |
| Bundle list commitment, bundle node digests, proof hashes | framed SHAKE256, 32 bytes (spec 15.2, 15.3) | collision (a bundler chooses both lists) | 1 to 2 | 48 bytes | 64 bytes |
| Transfer hash; Falcon message `m` | 32 bytes; `m` 64 bytes (spec 7.2; `circuit-notes.md`) | second preimage against third parties; collision only helps the signer | 5 for second preimage | 48-byte transfer hash (it is signed: keep it at the collision level of the rest) | 64 bytes |
| Nullifier | `PRF_nf(nk_d, rho || cm)`, 32 bytes (spec 5) | PRF security under a 256-bit key; a collision only blocks a note (availability) | 5 (key search) | nothing | nothing |
| Key derivation, seeds | seed 32 to 64 B; every `PRF_expand` output 32 B; Falcon key seed `SHAKE256(...)[0..32]` (spec 4) | PRF / key search on 256-bit keys | 5 | nothing | nothing; a 32-byte seed is the minimum (seed lengths below 32 bytes must stay refused) |
| Note encryption | ML-KEM-768 (FIPS 203 Algorithm 16 as cited by spec 4), `ek` 1,184 B; ChaCha20-Poly1305 with `H_pkg-key(K)` (spec 7.1) | Module-LWE; a 256-bit symmetric key | 3 (plan section 9 table; FIPS 203 to be added) | nothing | ML-KEM-1024: `ek` 1,568 B, ciphertext 1,568 B (**from memory**, FIPS 203 to verify): +384 B a full address, +480 B a package |
| Address scheme | full address carries `ek_d`; short address Bech32m of 34 bytes over `H_addr` (spec 9) | second preimage of `H_addr` | 5 for second preimage | nothing | full addresses grow with ML-KEM-1024 |
| Proof soundness (A and B) | rows certified at 152.52 bits a round, 20,000 proofs (design basis 2a; spec Appendix A) | proven IOP bounds, BCS, spBCS | 1 | 216.52 a round (T1): A 321/222/219/218 at the leaf, B 261 | 280.52 a round: A 415/288/283/282, B 338; a field above 256 bits |
| Challenge field | `GF(2^256)` both systems | algebraic rounds `n / |F|` | serves 1 (needs 177 to 184 bits) | serves 3 (needs 241 to 248 bits) | **does not serve**: needs 305 (A), 312 (B) bits |
| Proof-internal Merkle hash | A: Keccak-256; B: BLAKE3 (SQ-48; the specification still says SHA-256) | collision of tree inputs; QROM hash term | 1 (BLAKE3's claim is 128 bits; SHA-256's collision level likewise) | A: SHAKE256/Keccak at 48 bytes; B: SHA-384 (one SHA-512 compression a 96-byte node) or SHA3-384 | A: SHAKE256 at 64 bytes (a 128-byte node with a one-byte tag is one permutation; with an 8-byte tag, two); B: SHA-512 (compression-function mode, one compression a node) or SHAKE256-512 |
| QROM compilation (SG26 Theorem 6.6 (2)) | 67.32 QROM bits, hash term 75.63 at 32-byte digests (T4) | the bound as published | 1 | 99.32 bits at 48-byte digests (hash term 118.30; a 32-byte digest gives 75.63 < 96) | 131.32 at 64-byte digests (hash term 160.97); the hash term alone needs 416 bits |
| Zero knowledge (SG26 Theorem 6.6 (3), (4)) | 64-byte leaf and proof salts, `2^-87.8` (A) / `2^-85.7` (B) over `2^20` proofs plus `Q eps_hvzk` (open) | `b_l > b` | statistical | leaf salts 96 B: `2^-138.0` (T5) | proof salt 80 B, leaf salts 112 B: `2^-151.8` / `2^-149.7` |
| The wider Ycash system (context, not a recommendation) | the vault upgrade's FN-DSA-512 and SLH-DSA-SHA2-128s (workspace naming) | lattice; hash-based | 1 (both are the 128-bit / level-I parameter sets by name; FIPS 205 and the FN-DSA draft to be added) | — | — |

The last row is a fact about the system-wide weakest link: a coin that enters or leaves Yugen
through a transparent or vault address is protected at category 1 on that side whatever Yugen's
own level. It does not lower Yugen's in-pool level.

## 3. Proof soundness at each category

### 3.1 How the per-round requirement and the union are set

Per round: `e >= kappa_C + 1 + log2 20,000 + log2(1 + k)` (section 1.2). The union is over all
20,000 proofs of one tree (packed or not, the specification's own bound; finding S-11 of the
design basis is closed by `MAX_TREE_PROOFS`), with the collision term counted once and the
multi-block argument of `soundness-method.md` 8.5b. QROM: SG26 Theorem 6.6 (2) per proof, summed
over the 20,000 proofs (`spbcs.SpbcsTree`, **Published** bound, tree accounting **Original**
O-13). Rows are solved by the calculator's own functions (`wi.solve` for A's zero-knowledge leaf,
the rule-then-trim procedure of `revision5.minimal_counts` for A's node row 9, `binius64` and
`johnson.terms` for B).

### 3.2 System A (leanVM, WHIR, unique decoding, true rates), T2

| Target | Field | Leaf queries (ZK leaf, rate 1/4) | Leaf, KiB | Node row 9 at `2^27`, rate 1/2 | Node KiB at 1/2; at 1/4 | Weakest algebraic (leaf; worst node `2^30`) |
|---|---|---|---|---|---|---|
| cat1 | `2^256` | 226, 157, 154, 154 (reproduces the certified row) | 586 (**M**: 600,340 B) | 368, 167 x3, 168 x2, 173 | 855 (**M** 875,309 B); 744 (E) | 232.0; 225.0 |
| cat3 | `2^256` | 321, 222, 219, 218 | 939 (E) | 522, 238 x4, 239, 246 | 1,424; 1,247 (E) | 232.0; 225.0 |
| cat5 | `2^256` | **fails**: the mask round gives 256.0 < 280.5 bits | | fails | | |
| cat5 | `2^384` | 415, 288, 283, 282 | 1,496 (E) | 676, 308 x4, 309, 319 | 2,362; 2,101 (E): **over 1,792** | 360.0; 353.0 |
| cat5 | `2^512` | the same | 1,620 (E) | the same | 2,615; 2,343 (E) | 488.0; 481.0 |

Sizes: measured anchor plus the model's difference (leaf) or times the model's ratio (node);
digests of 384 / 512 bits and field elements of 48 / 64 bytes are in the model.

### 3.3 System B (Binius64, rate 1/8), T3

| Target | Field | Queries (UD, certified form) | Leaf KiB (E; 64-byte salts; route S adds about 46 KiB) | Node KiB, `2^27` words (E) | Weakest algebraic | Johnson candidate (DKT26 route; **not certified**) |
|---|---|---|---|---|---|---|
| cat1 | `2^256` | 184 | 582 (**M** 583,680 B) | 718 | 226.0 | 102 (m = 153): leaf 356, node 447 |
| cat3 | `2^256` | 261 | 970 | 1,183 (1,152 at 1/16) | 226.0 (need 216.52; margin 9.5) | none meets at this field |
| cat3 | `2^384` | 261 | 1,171 | 1,464 | 354.0 | 145 (m = 107): leaf 712, node 896 |
| cat5 | `2^256` | 338 | | | **226.0: fails** | none |
| cat5 | `2^384` | 338 | 1,652 | 2,057 (2,062 at 1/16): **over 1,792** | 354.0 | 188 (m = 92): leaf 1,004, node 1,254 |
| cat5 | `2^512` | 338 | 1,903 | 2,398 | 482.0 | 188: leaf 1,157, node 1,461 |

The calculator's own field check (`current.b_field_check`) gives the field needed: 184, 248 and
312 bits for categories 1, 3, 5. **A larger field buys fewer queries only through the
list-decoding rows**: unique decoding gives at most one bit a query whatever the field.

### 3.4 The challenge field

Category 3: `GF(2^256)` serves both systems with 8.5 to 15.5 bits of margin on the algebraic
rounds; no field change. Category 5: at least 305 (A) and 312 (B) bits. The two candidates:
`GF(2^384)` as a cubic extension of the 128-bit word field `E` (A's `E2 = E[z]/(z^2 + z + c)`
becomes `E3`; B's `GhashSq256b` analogue of degree 3 over GHASH's field), or `GF(2^512)` as a
quadratic extension of the 256-bit field (one more tower step, which keeps every existing
256-bit routine as the base of the new one). The first is smaller (48-byte elements against 64:
leaf 1,496 against 1,620 KiB in A); the second reuses more code. Both are new arithmetic in both
provers, both guests (A: a new `MUL3`-type VM row or several `MUL2` rows a product), the
recursion crates and the Lean statement.

### 3.5 QROM compilation and digest length, T4

Sharp and Grubbs, ePrint 2026/2615, Theorem 6.6 (2) (page 58; **Published**): extraction error
`2 sqrt(k_q / 2^(8(b+e))) + 6 (t + k_q)^2 (eps_k + c' (t + k_q) / 2^(8b))`. With the rows at
their need, both systems reach the QROM target with the same margin (+3.32 bits) at every
category, provided the digest is 48 bytes at category 3 and 64 at category 5. The hash term is
the constraint on the digest: it needs at least 224, 320 and 416 bits for categories 1, 3, 5
(A's counts, `c' = 2,397`). **A 256-bit digest cannot reach category 3 in the QROM (75.63 bits
against 96) under the published theorem.**

Finding Q-5 carries over unchanged (`qrom-compilation.md` 6.2): under SG26's classical bound in
the "every `t`" convention the rows would need 6.3 more bits at every category (T4: 158.8,
223.3, 287.6 against 152.5, 216.5, 280.5); for `t >= k_q` they meet. The decision on Q-5
(task T-6) applies to every category alike.

The proven classical hash term `3.5 t^2 / 2^lambda` leaves 1.4 bits short at the attack-rule
digest at every category (126.6 / 190.6 / 254.6 against 128 / 192 / 256: T1); the proven rule
needs 264 / 392 / 520 bits. SHAKE256 can give 33 / 49 / 65 bytes at no cost in permutations for
the transcript; the Merkle trees would carry one byte more a digest. Recommendation: keep the
attack rule (as at category 1), state it as the basis.

*Revision note (2026-11-19, calculator revision 10; `decision-qrom-counting.md` 7).* The proven classical figures
above come from the book's term `3.5 t^2 / 2^lambda` counted once for the tree. Under the spBCS theorem's own hash
term (Sharp, Grubbs, ePrint 2026/2615, Theorem 6.6 (2): `c' (t + k_q)^2 / 2^(8b)` per proof, `c'` about 2,400) summed
over the 20,000-proof tree, the proven classical level is **114.74 / 178.74 / 242.74** bits at categories 1 / 3 / 5
(not 126.6 / 190.6 / 254.6), and the proven rule needs **288 / 416 / 544** bits (not 264 / 392 / 520). The
recommendation stands: the attack rule is the basis, and the calculator now says so on every certified row.

*Amendment (2026-11-19, calculator revision 10.2, after `docs/tree-extraction-referee.md`; not a rewrite):* every TREE figure in this passage is conditional, not an unconditional theorem. It holds under the recursion heuristic C2 (the event "accepted in-circuit, rejected natively" does not occur; no random-oracle proof can remove it), the owed obligations K-A and K-B (round-by-round knowledge soundness) and T-1 (the transcripts' domain separation and fit to [SG26] Protocol 6.5). Under Theorem TE' (`docs/lemma-tree-extraction.md` revision 2) the classical hash level of the tree is **121.89 bits at category 1** (185.89 / 249.89 at categories 3 / 5), printed with the per-proof union (114.74 / 178.74 / 242.74) beside it as the comparison; the tree's QROM figures are derived under C2, never "proven QROM". Status of every claim: `docs/what-is-proven.md`.

### 3.6 Zero knowledge, T5

SG26 Theorem 6.6 (3) needs leaf salts longer than the digest: the first term of `eps_leaf` is
`2^(-4(b_l - b) - 1)` (SG26 page 58, the paragraph before the theorem). With 48-byte digests,
64-byte leaf salts give `2^-23.8` over `2^20` proofs: **the category 1 salts are vacuous at
category 3**. Proposed rows (pool of `2^20` proofs, `t` = `2^kappa_Q` queries before the last
proof; each plus `Q eps_hvzk`, open):

| Target | Digest | Proof salt | Leaf salt | A, ZK (3) | B, ZK (3) | A, WI (4) |
|---|---|---|---|---|---|---|
| cat1 (D-b) | 32 | 64 | 64 | `2^-87.8` | `2^-85.7` | `2^-86.8` |
| cat3 | 48 | 64 | 96 | `2^-138.0` | `2^-138.0` | `2^-150.8` |
| cat5 | 64 | 80 | 112 | `2^-151.8` | `2^-149.7` | `2^-150.8` |

At category 5 the proof-salt term `4 Q t / 2^(4 b_s)` binds at 64 bytes (`2^-106` at `t =
2^128`); 80 bytes lift it to `2^-170`. Cost: +32 B (cat3) / +48 B (cat5) an opened leaf of a
salted tree, and one more Keccak-f or SHA-512 block where a leaf crosses a block boundary.

### 3.7 Falcon-1024 in the circuits

Constants for `n = 1024` read from `fn-dsa-comm` 0.3.0 (the crate `yugen-falcon` pins):
verifying key 1,793 B (`vrfy_key_size(10) = 1 + 7 x 256`), signing key 2,305 B, signature 1,280
B (`signature_size`), squared-norm bound `beta^2` = 70,265,242 (`mq.rs` `SQBETA[10]`). The
vendored signer already carries `FN_DSA_LOGN_1024` and the same floating-point-free code
(`vendor/yugen-fn-dsa-sign/src/lib.rs` line 72; the determinism argument of `docs/determinism.md`
is per degree and must be re-run at 1024: known-answer vectors on aarch64, x86-64 and wasm32).
Hash-to-point (T6, exact binomial tail): **K = 1,292 draws, 2,584 bytes, 19 SHAKE256
permutations, fills the 19th block exactly, `2^-223`** (1,266 draws give `2^-179`).

In-circuit cost (E): the negacyclic transforms scale by `n log n` (x2.22), every linear part by
2, hash-to-point by 19/10. System B: Falcon alone 72,294 AND rows, one transform 11,344 (**M**,
`yugen-proof-b2` `statement-layout.md`); at `n = 1024` about 150,000 to 155,000, the leaf about
190,000 AND rows: **over the `2^17` committed-word bound, so B's leaf doubles to `2^18`**. System
A: C8 and C9 78,846 of 187,746 cycles (**M**, `yugen-proof-a` `statement-layout.md`); at 1024
about 165,000 to 175,000, the leaf about 275,000 to 285,000 cycles, about 5.1 M committed words:
**a `2^23` stack** (from `2^22`). The pk and signature never go on chain (spec 4), so their sizes
cost only wallet memory. Two Falcon-1024 keys a transfer also double the hash-to-point Keccak
count per spend (19 against 10 permutations).

## 4. Consequences per category

### 4.1 The parameter sets

| | cat1 (built) | cat3 (recommended) | cat5 (unique decoding) | cat5 (Johnson candidate for B) |
|---|---|---|---|---|
| Signature | Falcon-512 | Falcon-1024 | Falcon-1024 | Falcon-1024 |
| Statement digests | 32 B | 48 B | 64 B | 64 B |
| Proof digests / B's tree hash | 32 B / BLAKE3 | 48 B / SHA-384 | 64 B / SHA-512 | 64 B / SHA-512 |
| Challenge field | `2^256` | `2^256` | `2^384` (A, B) | `2^384` |
| Need a round | 152.52 | 216.52 | 280.52 | 280.52 |
| A leaf / node (rate 1/2) queries | 226,157,154,154 / 368,... | 321,222,219,218 / 522,... | 415,288,283,282 / 676,... | as unique decoding |
| B queries (rate 1/8) | 184 | 261 | 338 | 188 (m = 92) |
| Salts (proof / leaf) | 64 / 64 | 64 / 96 | 80 / 112 | 80 / 112 |
| KEM | ML-KEM-768 | ML-KEM-768 (cat3) or 1024 | ML-KEM-1024 | ML-KEM-1024 |

### 4.2 Wallet proofs against E1

E1 (plan 11): A at most 530 KiB, B at most 576 KiB; 10 s on a flagship phone; 512 MB.

| | A leaf | B leaf | Prove (1 M5 thread) | Memory |
|---|---|---|---|---|
| cat1 | 586 KiB (**M**; over E1's 530 already) | 570 KiB (**M**) | A 1.28 s, B 0.79 s (**M**, row 6 masked at `2^256`; form T) | A 596 MiB heap / 897 MiB RSS; B 1,095 MB footprint (**M**; B's native floor after steps a, b 554 MB, `wallet-memory.md` 5) |
| cat3 | 939 KiB (E) | 970 KiB (E), about 1,016 with route S | about the same as cat1 for the opening (more queries, same codewords: design basis 4); **x2 for Falcon-1024's doubled statement** (E): A about 2.6 s, B about 1.6 s | **about x2** with Falcon-1024 (codewords of the `2^23` / `2^18` statement), Merkle digests x1.5 (E) |
| cat5 | 1,496 KiB at `2^384` (E) | 1,652 KiB at `2^384` (E) | as cat3 plus the field: x1.5 (E) | as cat3 plus 1.5 times every extension-field codeword (E) |

E1's size limits cannot hold above category 1; `LEAF_RESERVE` (1,150,000, sized for two proofs
at E1's limits) must become about 1,972,000 at category 3 and about 3,241,000 at category 5 (two
leaf proofs plus 17,456 bytes). The 512 MB memory limit is missed at category 1 already; at
category 3 Falcon-1024 roughly doubles the gap. Phone memory is the second real obstacle after
system B's proving cost.

### 4.3 Node proofs, E2, verification

| | A root (KiB) | B root (KiB) | A core-s, N = 1,500 | B core-s, N = 1,500 | Both: hosts for 60 s | Node verify (4 cores) |
|---|---|---|---|---|---|---|
| cat1, BLAKE3 | 855 (**M**) | 718 (E) | 4,120 (E from **M** nodes) | 6,700 to 9,500 (E) | **12 to 15** | A 34 to 46 ms (**M**, one thread); B about 120 ms at level 3 without D-6 (E) |
| cat1, SHA-256 | 855 | 718 | 4,120 | 13,000 to 18,600 (E) | 18 to 24 | |
| cat3, SHA-384, `2^256` | 1,424 (1/2) / 1,247 (1/4) | 1,183 (1/8) / 1,152 (1/16) | 5,511 (E) | 22,700 to 33,800 (E; 13,500 to 20,000 with D-6) | **30 to 41** (20 to 27 with D-6) | A about 48 to 65 ms (x1.42, E); B over 100 ms without D-6 |
| cat3, B Johnson candidate at `2^384` | as above | 896 | 5,511 | 11,600 to 17,100 (E) | 18 to 24 | |
| cat5, `2^384` A / `2^512` B, SHA-512 | 2,101 at 1/4: **over** | 2,390 at 1/16: **over** | 9,436 (`2^384`) to 11,570 (`2^512`) (E) | 45,000 to 67,000 (E) | **57 to 80** | A about 80 to 130 ms (E) |
| cat5, B Johnson candidate at `2^384` | over | 1,254 | 9,436 | 22,700 to 33,800 (E) | 34 to 46 | |

Method (T7, E): A scales the measured 4,120 core-seconds by the per-child factor
`f = s (q_x / q_1) h + (1 - s) a` with `s = 0.80` the query-proportional share of a verified child
(Keccak-f times the measured 19.8 cycles a modelled Keccak-f, against 520,000 cycles a child,
**M** `recursion.md` 9.10), `h` the Keccak-f an opened position relative to category 1 (1.0 at
`2^256`, 1.25 at `2^384`), `a` the field-arithmetic factor (2.25 for a cubic extension, 3 for a
quartic; E). B scales the category 1 slot (6.5 M AND rows with SHA-256, `parameters.md` 9.2 (c))
by the query ratio and the hash's rows (SHA-384/512 compression estimated at 455 AND rows against
SHA-256's 364 C; SHAKE256 at 600 AND rows a Keccak-f), pads to the next power of two (the slot
cost is a step function, `parameters.md` 9.2 (b)) and uses 5.8 to 8.7 core-seconds a `2^23` slot.
"With D-6" lets the cost follow rows instead of the padded power of two. **The SHA-384 and
SHA3-384 slot rows are being counted by the system B builder; A's list of where a 48- or 64-byte
digest or a field above 256 bits is not a row parameter is being made by the system A builder
(`recursion.md` 10).** Replace these cells when those counts land.

### 4.4 Block weight and capacity, T8

`W` = 4,000,000; bundles may use `W - LEAF_RESERVE` = 2,850,000 (W5); a bundled transfer record is
200 bytes without value balance or on-chain package (spec 15.1, C; tree and anchor table bytes
left out, so these are upper figures).

| Profile | Root proofs A + B (B) | Within `PROOF_BYTES_MAX` | Transfers a block (E) | `W` that keeps cat1's 6,196 transfers |
|---|---|---|---|---|
| cat1 as built | 875,309 + 735,410 | yes | **6,196** (the plan's 9,500 is the block-byte bound alone) | 4,000,000 |
| cat3, nodes at 1/2 and 1/8 | 1,458,510 + 1,211,351 | yes | 901 | about 5,880,000 |
| cat3, nodes at 1/4 and 1/16 | 1,277,031 + 1,179,410 | yes | **1,968** | about 5,670,000 (with `LEAF_RESERVE` 1,972,000) |
| cat5, `2^384` A at 1/4, `2^512` B at 1/16 | 2,151,812 + 2,447,275 | **no** | 0 | about 9,080,000 and `PROOF_BYTES_MAX` of at least 2,450,000 |

With ML-KEM-1024 every on-chain package grows by 480 bytes (E, from memory sizes).

## 5. Feasibility

### 5.1 Category 3

**Built and proven:** the 256-bit challenge field in both systems (A fork change 13; B `cat1`,
`cat1t`); rows as data with `level`, `digest_bits`, `salt_bits` in B's identifier (spec A.2,
`parameters.md` 8.4) and per-shape query counts in A (D1, D4); the soundness bounds (book, SG26
Theorem 6.6, BCIKS20 unique decoding) at any target; ML-KEM-768. **Parameter change only:** query
counts (A 321/222/219/218 leaf, 522/238/... node; B 261), salts (96-byte leaf salts; the salt is
a row field in both). **New engineering (tasks, each with its acceptance test):**

| # | Task | Done when |
|---|---|---|
| K3-1 | Statement digests of 48 bytes: specification 3.1 framing `[0..48]`, `H_cm`, the note tree (SHA3-384 or SHAKE256-384 nodes, 2 permutations a 4-ary node), registry, bundle list and node digests, transfer hash; public inputs of both leaves (`anchor_root`, `nf`, `cm` as 48-byte values) | `yugen-ref` and the vectors regenerated; both wallet statements prove and verify every vector, every negative refused; Keccak-f a spend recounted |
| K3-2 | 384-bit digests inside system A: the guest's digest cells (three cells a digest, `recursion.md` 5), `LeafHasher`, the spBCS kernel's 48-byte items | a cat3 leaf and a node of 7 children prove and verify; the cat1 row still gives identical bytes |
| K3-3 | SHA-384 (SHA-512 compression) for system B's trees, native and in-circuit gadget, `Row::merkle_hash`; 384-bit digests through `check_build` | B's leaf and node at 261 queries prove and verify; slot AND rows counted and recorded |
| K3-4 | Falcon-1024 in both circuits (`n`, `q`, `beta^2` = 70,265,242, K = 1,292, 19 permutations), the 1,793-byte key encoding bound to `auth_d` under a new scheme byte (`sig_d = H_sig(0x02 ...)`, spec 4 SPEC-11 already provides it) | the 128 known-answer vectors at 1024 in both circuits; every Falcon mutation group refused; leaf stack `2^23` (A), `2^18` (B) measured |
| K3-5 | `yugen-falcon` at degree 1024: deterministic key generation and signing, cross-platform determinism re-run | known-answer vectors identical on aarch64, x86-64 (Rosetta) and wasm32-wasip1 |
| K3-6 | Calculator target `cat3` for the tree (`current.target(CAT3, 20,000)`), the rows certified, the salt rows of 3.6 | `uv run yugen-soundness` prints certified cat3 rows; tests that each count less by one fails |
| K3-7 | Consensus constants for cat3: `LEAF_RESERVE`, `LEAF_BYTES_RESERVE`, `W` (section 4.4), E1's size limits | the weight vectors (`bundle_rules.json`) regenerated; a cat3 leaf fits beside a full bundle |

**Lacks a published proof:** nothing at category 3 that is not already open at category 1 (the
recursion heuristic C2, `eps_hvzk` for both systems, the in-circuit-verification step), and the
same review items. **Cannot currently be met:** E2 (system B 22,700 to 33,800 core-seconds with
the certified row: 30 to 41 hosts with A) and E1 (proof sizes and 512 MB). What would make them
meet: (a) more hosts (E2 stated as hosts: about 30 to 41, or 20 to 27 with D-6); (b) B's
list-decoding row at a larger field (145 queries at `2^384`: 18 to 24 hosts with A), which needs
the DKT26 route to be reviewed and our lemmas L-J1 to L-J3 confirmed (`binius-johnson-row.md`);
(c) D-6, K = 7 or 15 and the cap layer at 7 for B (`parameters.md` 9.4: together x0.75 or
better); (d) for E1, A's streamed commitment (R-14) and B's steps L-5a, L-4b to L-4d, d, e
(`wallet-memory.md` 5), and E1's size limits restated per category.

### 5.2 Category 5

Everything of 5.1 at 64-byte digests, plus: **new engineering**: K5-1 the field above 256 bits in
both systems (cubic or quartic extension; A's arithmetic, sponge packing and guest; B's
`binius_field` element type, ring switch over the new field, recursion gadgets), done when a
cat5 leaf and node prove and verify in both systems and the algebraic rounds are recomputed by
the calculator; K5-2 the 80-byte proof salt and 112-byte leaf salts; K5-3 ML-KEM-1024 in the
specification (address and package sizes) and the wallet; K5-4 consensus constants:
`PROOF_BYTES_MAX` of at least 2,450,000 and `W` of about 9,080,000, or list-decoding rows.
**Lacks a published proof:** the list-decoding rows that would keep proofs within the current
limits (DKT26 is a preprint; L-J1 to L-J3 are ours, unreviewed; A has no list-decoding row with a
proven mutual-correlated-agreement bound at these parameters). **Cannot currently be met:** the
proof-size limit and the block weight with unique decoding; E2 by a factor 7 to 10; E1.

## 6. Mixed profiles

**M-1. Secrets and privacy at category 5, consensus soundness at category 3** (recommended).
Privacy must survive "record now, decrypt later": a ciphertext or a proof published today is
attacked with tomorrow's machines, with no way to respond. Soundness only has to hold until the
network can respond: a forgery must be produced before an upgrade, the design has two
independent proof systems that must both accept (plan 0, item 4), canaries that pay whoever
breaks a system first (spec 13), and a miner-signalled pause (plan 0). Limits of the argument: a
forgery that goes unnoticed is not undone by a later pause, so canaries detect only what an
attacker chooses to claim; the two systems share the statement, the specification and Falcon,
so a statement-level or Falcon break defeats both; and a pause halts honest users too. Hence the
parts every proof shares (the signature, the statement digests) belong at the privacy level or
next to it. In this profile: ML-KEM-1024, 256-bit keys and seeds (already there), the everlasting
zero knowledge of 3.6 at category 5 salts (80 / 112 bytes: statistical, cheap), Falcon-1024
(level V: the same scheme serves 3 and 5), 48-byte statement digests, proof rows at category 3.
Weakest link: the proof systems' soundness and the 48-byte digests, at category 3.

**M-2. Category 3 everywhere** (ML-KEM-768, Falcon-1024, 48-byte digests, cat3 rows). Weakest
link: everything at 3, with Falcon at V. Cheaper than M-1 by ML-KEM-768's smaller addresses and
packages (384 and 480 bytes) and 64-byte salts on the proof (not the leaf). Gives up category 5
privacy against an adversary that records ciphertexts.

**M-3. Category 5 for hashes and signatures, category 3 proof soundness.** 64-byte digests
everywhere, Falcon-1024, ML-KEM-1024, rows at 216.52 bits a round on the 256-bit field. Weakest
link: proof soundness at 3. The 64-byte digests cost about 1.3 to 1.5 times the in-circuit
hashing of 48-byte ones (B: a 128-byte SHA-512 node in compression-function mode is one
compression, as a 96-byte one; A: two permutations a 128-byte node with an 8-byte tag, one with a
one-byte tag) and 16 more bytes a digest in every proof; binding then never needs to change again.

**M-4. Category 1 soundness with category 5 privacy** is the cheapest profile that protects
recorded data; it is listed for completeness and is below the lead architect's stated aim.

## 7. Recommendation

**Adopt M-1 as the target: category 3 for the transfer, category 5 for secrets and privacy, with
the field and hash interfaces generic so that category 5 soundness is a later set of rows.**

Reasons: category 3 needs no new field and no unproven mathematics; every soundness statement is
the one already proven for category 1, at more queries. Category 5 privacy costs little (a KEM
parameter set and salt lengths) and is the part that cannot be raised after the fact.
Falcon-1024 is required at category 3 already (there is no level-3 Falcon), and it is level V.

Not recommended: **category 5 everywhere now** (gives up E2 by a factor 7 to 10, needs
`PROOF_BYTES_MAX` and `W` about doubled, a new field in both systems, and, to stay inside the
limits, list-decoding rows without a published proof); **category 3 with BLAKE3 or 32-byte
digests** (not admissible: BLAKE3's claim is 128 bits; a 32-byte digest fails the QROM hash term
at 75.63 against 96); **category 1** (below the stated aim).

What each gives up: M-1 gives up E2 as written (30 to 41 hosts for both systems with the
certified row, E) until B's cost falls, about 4,000 transfers a block of capacity against cat1
unless `W` rises, and E1's sizes. M-2 gives up recorded-ciphertext privacy above 3.

What would change the recommendation: (a) the list-decoding rows confirmed (DKT26 refereed; L-J1
to L-J3 reviewed): category 5 soundness inside 1.75 MiB becomes reachable for B at `2^384` and
B's category 3 cost falls by about half; (b) the SHA-384 slot count landing well above the
estimate: SHA3-384 or more hosts; (c) a proven bound making the 256-bit digest admissible in the
QROM at category 3 (none known); (d) the NIST text read differently from section 1.1 (for
example a per-instance reading that does not need the tree union): every need here falls by
`log2 20,000 = 14.3` bits.

**Order of work** (each a task of section 5 with its done-when test):

1. K3-6: the calculator's cat3 (and cat5) tree targets, certified rows, salt rows; `CAT5` in
   `targets.py` (this record computed it outside the calculator).
2. K3-3 and the B count of SHA-384 against SHA3-384 in circuit; with it, D-6, K = 7 or 15 and
   the cap layer (B's cost is the deciding obstacle).
3. K3-4 and K3-5: Falcon-1024 in `yugen-falcon` and both circuits (the largest change to the
   wallet statement and to E1).
4. K3-1, K3-2: 48-byte statement and proof digests (a specification revision; the scheme byte
   and statement version already provide the mechanism).
5. K5-3: ML-KEM-1024 and the category 5 salts (M-1's privacy half).
6. K3-7: consensus constants for the chosen category, from measured proofs.
7. K5-1 behind a row field: the larger field, so category 5 soundness is a later release.

## 8. Errors in the plan and the specification found here (for the lead)

- Plan section 9 and design basis section 1: "category 3 ... by a release that changes
  parameters only" does not hold (finding 2): statement digests are fixed at 32 bytes by the
  specification, Falcon-512 is category 1, BLAKE3 is category 1, 64-byte leaf salts are vacuous
  with 48-byte digests, and A's guest and B's `check_build` take the digest length as code.
- Plan section 0: "The ceiling set by the 2 MB block is about 9,500 transfers" counts block
  bytes; with W5 and today's root proofs the weight allows about 6,200 (E, section 4.4).
- Plan section 2 and SQ-23 still name Plonky3 for B (the coordinator's inventory; SQ-38 decided
  Binius64); the specification names SHA-256 for B's trees where SQ-48 decided BLAKE3.
- E1's A size limit (530 KiB) is already exceeded by the measured category 1 leaf (600,340 B).

## 9. What the calculator could not express (computed in `category_study.py` from its functions)

A category 5 target (`targets.py` has `cat1`, `cat3`): built as `SecurityTarget(256, 128, 256,
512)`. Fields above 256 bits for A (`current.a_config` fixes 256) and digests other than 256 bits
in the row builders (`FsParams` fixed): the configuration is copied and replaced. B's algebraic
terms at other fields (`johnson.FIELD_BITS` is a module constant): the counts of `johnson.terms`
re-read at the field. Everything else is the calculator's own code.

## 10. Sources and provenance

**Published** (used as is): Sharp, Grubbs, *Faster and Smaller Anonymous Credentials from
Standardized Signatures*, ePrint 2026/2615, Theorem 6.6 (2) to (4), page 58 to 59, and the
`eps_leaf` paragraph before it (read from the text layer, 2026-11-19); O'Connor, Aumasson, Neves,
Wilcox-O'Hearn, *BLAKE3: one function, fast everywhere*, version 20211102173700, Section 4.1, and
Aumasson, Neves, O'Connor, Wilcox, *The BLAKE3 Hashing Framework*, draft-aumasson-blake3-00
(20 July 2024), Section 7 (both in `REFERENCES.md` 1.1e); Chiesa, Yogev, the book's Theorems
25.2.1, 31.2.1; BCIKS20 unique decoding; the Falcon constants of `fn-dsa-comm` 0.3.0 (code, read
here). **Adapted:** none. **Original (the Ycash developers, 2026)**, first in this document and
`category-study/` (commits from `85783d3`, 2026-11-19), unreviewed: the category 5 target and
its digest rule (O-33); the category 3 and 5 rows of A and B, fields and salts (O-34); the cost
and capacity scalings (O-35); the mixed-profile argument M-1 (O-36). Checked before labelling:
`soundness-method.md` 8, `design-basis.md`, `qrom-compilation.md`, SG26 Theorem 6.6, the BLAKE3
sources; none states a category 5 parameter set for these systems.

**Documents the lead architect should add to the reference folder:** the NIST PQC call for
proposals (security-strength categories and evaluation criteria); FIPS 203 (ML-KEM: levels and
sizes of 768 and 1024); FIPS 204 (ML-DSA, for the category definitions it restates); FIPS 205
(SLH-DSA: the category of SHA2-128s); the FN-DSA (FIPS 206) draft; the Falcon round-3
specification (levels of Falcon-512 and -1024); FIPS 202 (SHAKE256 capacity claims); FIPS 180-4
(SHA-384/512 padding and compression); Brassard, Høyer, Tapp on quantum collision search.
