# Referee report on the security-category decision record

Part of Yugen. Written 2026-11-19 in `yugen-proofs` as an independent referee
report on `docs/decision-security-category.md` (commit `e2cebb6`, with `category-study/` at the
same commit). The referee did not write the record. Findings are attributed to the Ycash
developers (2026) and are unreviewed.

**Recomputation.** The referee's own script is `category-study/referee/referee_check.py`. It
derives the needs, system B's query counts, the field sizes, the QROM digest floor, the salt
floor and the block capacity from closed forms. It uses the calculator (revision 6, unchanged)
only to read system A's round list and to test that each of A's counts is minimal. To run it:
`cd soundness && uv run python ../category-study/referee/referee_check.py`. Its sections are
cited below as R1 to R8.

**Sources read for this report.** These are in the reference-paper collection (REFERENCES.md) and were read from
their text layer.

- NIST, *Submission Requirements and Evaluation Criteria for the Post-Quantum Cryptography
  Standardization Process* (call for proposals, December 2016), §4.A.5, pp. 15–19, and §4.A.6.
  Cited below as [CFP].
- NIST FIPS 204, §4 Table 1, §5.4 footnote 6, Appendix D.1. Cited as [FIPS204].
- NIST FIPS 205, §10.2 footnote 18, §11 with Table 2 and the text after it, §11.2.2. Cited as
  [FIPS205].
- Prorock, Steele, Tschofenig, *FN-DSA for JOSE and COSE*, draft-ietf-cose-falcon-05
  (1 November 2026), §1 Table 1. Cited as [COSE-FN].
- Günther, Lyubashevsky, Schmidt, *FALCON with message recovery, a specification*, Cryptology
  ePrint Archive 2026/420, abstract and §1 (pp. 1–2). Cited as [GLS26]. This is the file the
  coordinator listed as unidentified. It bears on the study in one way only: it states that
  Falcon-512 and Falcon-1024 are at "NIST levels 1 and 5" (abstract) and at "128 and 256-bit
  security levels" (§1). Its message-recovery mode is of no use here, because Yugen's signature
  never goes on chain.
- Sharp, Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, ePrint
  2026/2615, §6.3 and Theorem 6.6, pp. 58–59. Cited as [SG26].

FIPS 202, FIPS 203 and the FN-DSA standard (FIPS 206) are still not in the folder. Statements
that rest on them are marked **from memory**.

Verdict scale: **holds**; **holds under a stated hypothesis**; **unsupported** (the record's
evidence does not carry the claim); **wrong**.

---

## 0. Verdicts first

| # | Claim of the record | Verdict |
|---|---|---|
| V1 | Category definitions (§1.1), cost model (§2) | **Holds**, now verified against [CFP] §4.A.5. Two corrections (§1 below): a 256-bit collision-resistant digest is category **2** by definition, not "1 to 2"; NIST gives collision costs in classical gates only, so the record's BHT figure is not used by NIST |
| V2 | Signature levels: Falcon-512 is I, Falcon-1024 is V; SLH-DSA-SHA2-128s is 1 | **Holds** ([GLS26] abstract; [FIPS205] §11 Table 2). The sizes are confirmed by [COSE-FN] Table 1 |
| V3 | "Falcon-1024 is required at category 3" | **Holds only under the hypothesis "pk is public"**. In Yugen `pk` is never published (spec §4.4, §5.1), so the record omits an option that the lead architect must weigh (§2.2) |
| V4 | Weakest-link inventory (§2) | **Incomplete.** It misses private retrieval (DPF with 128-bit seeds: category 1), the transport KEM (ML-KEM-768: category 3) and lattice PIR parameters below category 1. The nullifier row misses the collision dependence through `nkc_d` (§2) |
| V5 | Needs of 152.52 / 216.52 / 280.52 bits a round | **Holds** (R1), as the project's tree-wide proven rule. It is stricter than NIST's per-instance definition (§3.1) |
| V6 | Query schedules: A 321/222/219/218 and 415/288/283/282, B 261 and 338 | **Holds** (R2, R4: every count is minimal) |
| V7 | The 2^256 field suffices at 3; category 5 needs 305 (A) / 312 (B) bits | **Holds, except A's 305 is wrong: A needs 312 too.** A's 2^30 nodes have the same 2^31 term as B (R3) |
| V8 | QROM: 384-bit digests at 3 and 512 at 5 by the bound itself | **Holds** by Theorem 6.6 (2): the floor is 320 / 416 bits (R5). **"Proven category 3 in the QROM" is overstated**: the proof covers 2^96 queries; NIST's category 3 quantum budget is larger (§3.3) |
| V9 | 64-byte leaf salts "vacuous" at 48-byte digests; 96 bytes needed | **Wrong word, unsupported figure.** The bound is 2^-23.8: useless, but not vacuous. No zero-knowledge target is defined, so no length is "needed": 83 B meets 2^-96 and 91 B meets 2^-128 (R6) |
| V10 | Capacity: 6,196 a block at category 1 against the plan's 9,500 | **The record misreads the plan.** The plan calls 9,500 the block-byte ceiling, gives about 5,600 at the launch weight, and says the ceiling needs `W` ≥ 4.82 MB (plan §5). Both figures are estimates on different inputs (§4.3) |
| V11 | Category 3 capacity of about 1,970 | **Wrong**: the record's own `LEAF_RESERVE` for category 3 leaves room for no bundle at `W` = 4,000,000 (R7) |
| V12 | Hosts for E2 (12–15 / 30–41 / 57–80) | **Estimates on an inconsistent baseline.** B's category 3 and 5 figures are scaled from a formula that gives 11 % less than `parameters.md` at category 1. Corrected category 3: 25,600–36,800 B core-seconds, 33 to 44 hosts (R8) |
| V13 | "Category 3 is not parameter-only" | **Holds** (§5.1). The list is complete except for the privacy side (DPF seeds, transport KEM) and W4 |
| V14 | Category 5 needs a field above 256 bits; list decoding is the only way inside the size limits | **The field claim holds and does not depend on the tree union.** The list-decoding claim is **unsupported as "only"**: raising `PROOF_BYTES_MAX` and `W` is the other way, and the record lists it itself (§5.2) |
| V15 | M-1: privacy and long-lived secrets at category 5 | **Overstated.** With DPF seeds and the transport KEM unchanged, retrieval privacy is category 1 and transport privacy category 3. Zero knowledge is statistical (no category applies), and its HVZK term is open (§6) |
| V16 | §8 plan and specification errors | Items 1, 3 and 4 **confirmed**; item 2 **refuted as stated** (§7) |
| V17 | Category 1 measured state is consistent | **No.** Today's measured leaf proofs (1,184,020 B) plus 17,456 B of transaction exceed `LEAF_RESERVE` (1,150,000), so rule W4 refuses a measured category 1 leaf transfer (R7). The record does not say so |

**Overall.** The lead architect can rely on the record's **soundness arithmetic**: the needs,
the query counts, the field threshold and the QROM digest lengths. The lead architect should
**not** rely on its capacity and host figures without the corrections below. Nor should the
lead architect rely on its claim that M-1 delivers "category 5 privacy". The recommendation is
argued under a bias towards category 3 or above, which the record's brief asked for. §8 gives a
feasibility comparison of the profiles and the referee's opinion.

---

## 1. Definitions and cost model, against the NIST text (V1, V2)

**What [CFP] §4.A.5 says** (pp. 16–18; quotations marked). Categories 1, 3 and 5 are key search
on a block cipher with a 128-, 192- or 256-bit key. Categories 2 and 4 are "collision search on
a 256-bit hash function (e.g. SHA256/ SHA3-256)" and on a 384-bit one (SHA384/SHA3-384). An
attack must cost at least the threshold "with respect to all metrics that NIST deems to be
potentially relevant". MAXDEPTH is suggested from 2^40 through 2^64 to "no more than 2^96"
logical gates.

The table on p. 18 gives these costs:

| Primitive | Quantum cost | Classical cost |
|---|---|---|
| AES-128 | 2^170/MAXDEPTH | 2^143 |
| SHA3-256 collision | none given | 2^146 |
| AES-192 | 2^233/MAXDEPTH | 2^207 |
| SHA3-384 collision | none given | 2^210 |
| AES-256 | 2^298/MAXDEPTH | 2^272 |
| SHA3-512 collision | none given | 2^274 |

Footnote 2 orders the five categories. Footnote 6 cites Zalka for parallel Grover. The record's
§1.1 summary, taken from `soundness-method.md` 8.1, matches this text. It names SHA3-256 and
SHA3-384 where NIST names "SHA256/SHA3-256" and "SHA384/SHA3-384".

**Corrections.**

1. **A 256-bit digest whose role needs collision resistance is category 2 by definition, not "1
   to 2"** (record finding 1(b), inventory rows). Category 2 *is* collision search on a 256-bit
   hash. The open question is whether 256-bit collisions reach category 3, and they do not:
   2^146 < 2^207 classical gates.
2. **The rule "384 bits at 3, 512 at 5" is confirmed by NIST's own numbers and by a NIST
   precedent.** SHA3-384 collision (2^210) ≥ AES-192 (2^207), and SHA3-512 collision (2^274) ≥
   AES-256 (2^272) ([CFP] p. 18). [FIPS204] §4 Table 1 sets the "collision strength of c̃" λ to
   128 / 192 / 256 for categories 2 / 3 / 5. Appendix D.1 records that a 384-bit SHAKE256 output
   "would make it so that parameters targeting NIST security strength category 5 could only meet
   category 4". These two citations should replace the record's "from memory" basis for H.
3. **Quantum collision search: NIST takes the realistic view.** [CFP] gives collision costs in
   classical gates only. The record's §2 BHT figure (2^(n/3)) appears in its cost model but is
   applied nowhere, so the record is consistent with NIST. It should say so. Under the
   conservative BHT view (query count with free quantum memory), a 384-bit digest would give
   about 2^128 queries. Then 48-byte digests would not be category 3, and the H rule would need
   576 bits at category 3.
4. **Preimage-only components may stay at 256 bits even at category 5.** NIST does this itself
   in SLH-DSA: [FIPS205] §11.2.2 instantiates `F` and `PRF` with SHA-256 truncated to `n` = 32
   bytes in the category 5 sets. This supports the record's rows for the address hash, the
   second-preimage role of the transfer hash, and the PRFs.
5. **Grover model, condition G.** The record compares one Fiat–Shamir oracle call with one AES
   evaluation by AND count (`soundness-method.md` 8.2, from memory). Under a depth limit, the
   cost of parallel Grover scales with (oracle depth × oracle size) / MAXDEPTH. NIST's 2^170 for
   AES-128 is 2^128 × 2^42 on that product (Grassl et al., cited in [CFP] footnote 4, not read).
   The correct premise is therefore "Keccak-f's quantum circuit has depth × size at least AES's".
   This is plausible: Keccak-f is the larger circuit. It is **unverified**.
   *Work*: cite a Keccak quantum-circuit cost, or state the premise as an assumption.
6. **Signature levels (V2).** Falcon-512 is level I and Falcon-1024 level V ([GLS26] abstract and
   §1). FN-DSA-512 / 1024 sizes are 666 / 897 / 1,281 and 1,280 / 1,793 / 2,305 bytes
   ([COSE-FN] Table 1), which confirms the record's §3.7. SLH-DSA-*-128s is category 1
   ([FIPS205] §11 Table 2 and the text after it). ML-DSA-44 / 65 / 87 are 2 / 3 / 5 ([FIPS204]
   §4 Table 1). ML-KEM-768 at 3 and ML-KEM-1024 at 5, with sizes 1,568 / 1,568 bytes, remain
   **from memory** (FIPS 203 not supplied).
7. **[CFP] §4.A.6 lists multi-key resistance as desirable, not required.** The record's tree
   union over 20,000 proofs therefore goes beyond the definition. That is acceptable, but the
   record should say so (its §7 (d) says it only as a possible "reading").

[CFP] p. 18 also says: "NIST recommends that submitters primarily focus on parameters meeting
the requirements for categories 1, 2 and/or 3, since these are likely to provide sufficient
security for the foreseeable future", with a parameter set above 3 "to hedge". This bears on
the lead architect's choice and is missing from the record.

---

## 2. Weakest-link inventory (V3, V4)

### 2.1 Components missed or misclassified

| Component | Today | Category | The record | Correction |
|---|---|---|---|---|
| **Private retrieval, two-server DPF** (plan step 0.8; `yugen-pir/docs/pir-selection.md` table "Two-server DPF, AES-256 Hirose PRG, 128-bit seeds") | 128-bit seeds | **1** (that document says so itself) | missing | A server that logs DPF keys and later searches the 128-bit seed space learns which bucket, tag or tree path a wallet read. Retrieval privacy is therefore record-now-break-later at category 1. *Fix*: DPF with λ = 256 seeds. Each correction word doubles, so keys grow about 2×, still a few KB a lookup. *Done when*: `yugen-pir` runs the BGI16 DPF at λ = 256 and re-measures E5 |
| **Single-server lattice PIR** (same document, p. "Consequence") | shipped parameters estimate below ML-KEM-512 | below 1 | missing | Re-parameterise before use (that document already says so). For category 5 privacy, choose parameters against the category 5 lattice estimate |
| **Transport** (plan §6: "hybrid key exchange (X25519 with ML-KEM-768), including the oblivious-HTTP layer") | ML-KEM-768 | 3 | missing | Recorded wallet-to-host traffic is category 3. *Fix*: ML-KEM-1024 in the hybrid for M-1 |
| **Nullifier, double-spend side** (spec §4.3, §5.3) | `nkc_d = H_nkc(nk_d)` is 32 bytes and sits in the note | 2 (collision) | row says "5, nothing" | A holder who finds two `nk_d` with one `nkc_d` (a collision on his own address) can spend his own note twice. Both proof systems accept, because both statements are true. The nullifier's integrity therefore rests on collision resistance of `H_nkc`, which K3-1's 48-byte framing does cover. The inventory row should say "collision through `nkc_d`" |
| **Address commitment** `auth_d`, `sig_d` (spec §5.1) | 32 bytes | 5 against third parties (second preimage), 2 for the owner | not listed | Same pattern as above: the owner's collision gains nothing, because he owns the note. List it for completeness |
| **Short address** `H_addr` (spec §12.2) | 32 bytes | 5 (second preimage); 2 for the owner | "5" | An owner collision gives two full addresses behind one short address (payment deniability). This is minor, and K3-1 covers it |
| **Exit tags, registry** (spec §13.1) | `exit-tag` over `nkc_d ‖ rk_d`; SHA3-256 registry | hiding 5; registry collision 2 | registry listed, tags not | Correct as far as listed. Tags hide by preimage (5) |
| **Canaries** (spec §13.2) | detection, not a primitive | n/a | used as an argument in §6 | See §6 and §8 |
| **Multi-target key search** over all users' 256-bit keys | — | 5 minus log2(users) classically | not discussed | At 2^30 users, about 2^226 classical; still ≥ AES-192. Note it under [CFP] §4.A.6 |

Every other row of the record's §2 table checks against spec §3 to §7: framing, the note tree
and registry, commitments, bundle digests, key derivation, note encryption and AEAD keys.

### 2.2 Spend authority: the hidden-key alternative the record omits (V3)

`pk` is never placed on chain, exported or shown (spec §4.4). It sits behind
`sig_d = H_sig(0x01 ‖ pk ‖ salt_d)` with a secret 32-byte `salt_d` (spec §5.1). The exit
reveals `sig_d`, never `pk` (R-5). A third party who wants to forge a spend under Falcon-512
must therefore first obtain `pk`. That takes a leak (a wallet or signing-device compromise) or
a second preimage of `H_sig` / `H_auth` (category 5). The plan's §9 table says this
("The public key is never revealed"). The record drops it and calls Falcon-512 the category 1
weakest link outright.

**Verdict.** Falcon-1024 is required at category 3 only under the NIST convention that the
verification key is public. Under Yugen's construction, with a secret `pk`, Falcon-512 is a
second factor behind a category 5 hash, until `pk` leaks.

**Correction.** State both readings. Under the first, Falcon-1024 (K3-4, K3-5) is required.
Under the second, Falcon-512 is kept and K3-4 / K3-5 become an upgrade by scheme byte `0x02`
(spec §5.1) when the lead architect wants it. That upgrade needs new addresses.

**Cost of the choice.** The record estimates about 2× prove time and memory in the wallet
statement (§3.7). This is the single largest wallet cost in M-1.

---

## 3. Soundness arithmetic (V5 to V8)

### 3.1 Needs (R1)

`e ≥ κ + 1 + log2 N + log2(1 + k)` gives 152.517 / 216.517 / 280.517 bits for A (k = 599) and
152.519 / 216.519 / 280.519 for B (k = 600). Condition Q gives 145.87 / 209.87 / 273.87, so
condition C binds. **Holds**, as derived in `soundness-method.md` 8.5b. The per-instance reading
(one proof, no union) is 138.2 / 202.2 / 266.2, which is the record's 14.3-bit remark. That
reading is closer to [CFP]'s wording (one key; multi-key only "desirable", §4.A.6).

### 3.2 Queries and fields (R2, R3, R4)

- **B.** Unique decoding gives 183.74 → 184 (cat 1), 260.84 → 261 (cat 3) and 337.94 → 338
  (cat 5) at rate 1/8, and 168 / 238 / 308 at rate 1/16.
- **A.** Re-solved from the calculator's round list: 226/157/154/154 (cat 1), 321/222/219/218
  (cat 3), 415/288/283/282 (cat 5, field 2^384). Lowering any count by one fails the need. The
  first count is close to the closed form at rate 1/4 (224.9 / 319.3 / 413.7); the rest comes
  from the zero-knowledge leaf's extra terms. **Holds.**
- **Field.** The largest algebraic error term is n/|F| with n = 2^31 (nodes of 2^30, both
  systems). That gives 183.5 / 247.5 / 311.5 bits, so GF(2^256) leaves +8.5 bits at category 3
  and −55.5 at category 5. **A's category 5 figure "305" counts only the leaf (2^24) and is
  wrong: A needs 312 as well** (the record's own table T2, worst node 225.0). This makes no
  difference to the choice of 2^384.
- **Category 5 needs a field above 256 bits on every reading.** Even one proof with no union
  needs 266.2 > 256 bits. As an attack: grinding the weakest round costs about 2^225 hash calls,
  below AES-256's 2^256 calls. The claim holds independently of the tree union.

### 3.3 QROM digests (R5) and what Q proves (V8)

Theorem 6.6 (2) ([SG26] p. 58) contains the hash term `6 (t + k_q)^2 · c'(t + k_q)/2^(8b)`.
Summed over 20,000 proofs and set to 1/2 at `t = 2^κ_Q`, it needs
8b ≥ 3κ_Q + log2(12 c' N). With c' = 2,397 (A) or 2,401 (B), that is 221.1 / 317.1 / 413.1
bits, so **224 / 320 / 416**. At 48 B the term gives 118.3 QROM bits (≥ 96); at 64 B it gives
161.0 (≥ 128). **Holds by the bound itself, not by analogy.** The record's "a 32-byte digest
cannot reach 96" also holds (75.6).

**Overstatement.** Condition Q's "96 QROM bits" means the bound reaches 1/2 at 2^96 total
queries (`spbcs.SpbcsTree.iop`). NIST's category 3 quantum budget is 2^233/MAXDEPTH gates
([CFP] p. 18): 2^137 gates even at MAXDEPTH = 2^96. With a Keccak circuit of 2^17 to 2^22
gates (from memory), that is about 2^115 to 2^120 parallel oracle queries. The proven QROM
bound is vacuous there. At category 3, the quantum side of the claim therefore rests on G, the
attack estimate (parallel Grover, Zalka), not on a theorem. The same holds at category 5. At
category 1 with large MAXDEPTH the theorem does cover the budget: 2^74 gates, about 2^57
queries.

*Correction*: label the quantum half of categories 3 and 5 "attack estimate (G); proven QROM
security to 2^96 / 2^128 queries".

The Q-5 finding (6.3 bits under SG26's ROM bound in the "every t" convention) carries over, as
the record says.

### 3.4 Salts (V9)

[SG26] p. 58 states the first term of ε_leaf as `2^(-4(b_l - b) - 1)`, with "each byte of leaf
salt beyond the digest divid[ing] both terms by 2^4". It also says that in Part (3), `t` counts
only the queries *before the last proof query*. The record's use of everlasting zero knowledge
is therefore right: queries made after the proofs are published do not count.

With b = 48 and b_l = 64, the pool bound is 2^-23.8. That is useless, but **not vacuous**
(vacuous means ≥ 1, which happens at b = 64, b_l ≤ 72). **No zero-knowledge target per category
is defined anywhere.** The leaf term does not depend on `t` or on the category. Pool targets
give these floors (R6):

| Pool target | Leaf salt with 48-byte digests | Leaf salt with 64-byte digests |
|---|---|---|
| 2^-64 | 75 B | 91 B |
| 2^-96 | 83 B | 99 B |
| 2^-128 | 91 B | 107 B |

So "96 bytes are needed" is a choice: 96 B gives 2^-138 (the proof-salt term binds). The choice
is cheap, so keep it, but state the target.

*Work*: add a zero-knowledge target (for example "pool advantage ≤ 2^-128 at every category,
excluding Q·ε_hvzk") to `soundness-method.md` and derive salts from it.

---

## 4. Sizes, costs and capacity (V10 to V12, V17)

### 4.1 What is measured

| Figure | Kind |
|---|---|
| A leaf 600,340 B; A node 875,309 B; B leaf 583,680 B (measured) | measured (M) |
| B node 538,272 B at 2^23 words | measured |
| B root at 2^27 words, 735,410 B | **estimate**. The record's §4.4 calls it "as built", but B's category 1 recursion "does not yet compile" (plan §0 step 0.5) |
| Prove times 1.28 s / 0.79 s | one M5 thread, not a phone. Phone measurements are "Not started" (plan step 0.15) |

Every category 3 and 5 size is the measured anchor times a model ratio. This is defensible for
openings. It is unvalidated for the Falcon-1024 statement (no layout counted).

### 4.2 Falcon-1024 scaling

The constants hold ([COSE-FN]; β² from `fn-dsa-comm`, read by the record). The transform
factor n log n gives (1024·10)/(512·9) = 2.22. The hash-to-point draw count is K = 1,292,
which fills 19 blocks and gives 2^-223; K = 1,266 suffices for 2^-179 (T6, recomputed). The
in-circuit totals are an estimate built from one measured transform count (B) and one measured
cycle count (A); no NTT-free check was considered.

*Work*: count the Falcon-1024 rows in both circuits (K3-4) before using the 2× figures.

### 4.3 Capacity (V10, V11)

Spec §16.2: weight is block bytes plus proof bytes, W5 limits bundles to `W − LEAF_RESERVE`.

- **Category 1.** The record gets 6,196 = (2,850,000 − 1,610,719)/200. The plan (§5 table)
  gets about 5,600, using 1,787,904 B of estimated proofs, 210.5 B a transfer and a leaf
  actually present. It calls 9,500 the block-byte ceiling and says that needs `W` ≥ 4.82 MB.
  With the record's proofs and the plan's 210.5 B allowance: 5,887. **The record misreads the
  plan; the two estimates differ by their inputs, and neither is wrong.** The record also leaves
  out the tree and anchor-table bytes.
- **Category 3.** The record's 1,968 keeps `LEAF_RESERVE` at 1,150,000. Its own §4.2 says
  `LEAF_RESERVE` must become about 1,972,000. Then W5 gives 4,000,000 − 1,972,000 = 2,028,000
  of weight against 2,456,441 B of root proofs: **no bundle fits; capacity 0** (R7). Category 3
  needs `W` of at least about 4.43 MB for an empty bundle, and about 5.67 MB for 6,196
  transfers. The record's last column has the second figure; its headline "1,970" is wrong.
- **W4 today (V17).** The measured category 1 leaves (600,340 + 583,680 B) plus 17,456 B of
  transaction weigh 1,201,476 B, which is over `LEAF_RESERVE` = 1,150,000. A measured category 1
  leaf transfer is invalid under W4. *Fix*: shrink the leaves to E1 (A's R-14 streamed
  commitment, B's mixed form), or raise `LEAF_RESERVE` to at least 1,202,000. Either way, every
  capacity figure falls by the difference: about 260 transfers.

### 4.4 Hosts (V12)

For system B, the script applies its own formula (1,504·s + 435 + 416·s) at category 3 and 5,
but substitutes `parameters.md`'s 13,000–18,600 at category 1. The formula gives 11,571–17,139
there, which is 8 to 12 % low. Rescaled from `parameters.md`, B at category 3 with SHA-384 costs
25,600–36,800 core-seconds. **Both systems together: 31,100–42,300, so 33 to 44 hosts (not 30
to 41).** Category 5 rises in proportion. A's 4,120 rests on a model of measured nodes. The plan
shows an earlier 15,000 estimate for A (plan step 0.10), so A's figure also carries model risk.

---

## 5. Feasibility claims (V13, V14)

### 5.1 Category 3 is not parameter-only (V13)

This holds. The specification fixes 32-byte outputs (§3.1) and B's tree hash is BLAKE3 (128-bit
claim, `decision-b-merkle-hash.md` H-1.5). Both force code changes. The record's list is
correctly sorted between "parameter" (query counts, salts) and "new engineering" (K3-1 to K3-7).

Missing from the list:

- **K3-8**: retrieval and transport at the chosen privacy level (§2.1). This is only for M-1;
  it is not required for "category 3 throughout", whose transport is already category 3.
- The W4 / `LEAF_RESERVE` repair of §4.3.

Mislisted: K3-4 / K3-5 are required only under the public-key reading (§2.2).

### 5.2 Category 5 (V14)

**The new field is new engineering, not new mathematics.** A cubic extension of a binary field
`E` of 128 bits is a field for any irreducible cubic over `E`. Additive NTTs and the sumcheck and
fold bounds the calculator uses are field-generic.

One caveat for B. DP24 ring switching (ePrint 2024/504, Section 3 to 4, as read in
`REFERENCES.md` 1.1) packs into a field whose degree over its subfield is a power of two. A
384-bit challenge field must therefore stay an extension *above* the 128-bit packing field, as
the 256-bit variant does (`binius-extension-challenges.md`). It cannot be a packing field. The
record's "degree 3 over GHASH's field" is consistent with this. The masking lemma of that
document (masks sampled in the extension) must be re-checked at degree 3.

**List decoding is not "the only way" inside the size limits.** The other way is to change the
limits: `PROOF_BYTES_MAX` ≥ 2,450,000 and `W` ≈ 9.1 MB, which the record states in K5-4. A
third way is node rates. At rate 1/16, B's node is 2,062 KiB at 2^384 (still over 1,792), so
rates alone do not suffice. Unique-decoding category 5 does not fit the current constants. That
is the correct statement.

---

## 6. The recommendation M-1 (V15)

**The asymmetry argument is sound in its core.** A soundness break must be used live, against
a network that can pause, re-parameterise and shut the turnstiles. A privacy break works on
records retroactively, and nothing can be done afterwards.

Its limits are those the record gives:

- A forgery that is not noticed is not undone.
- Canaries detect only an attacker who chooses to claim.
- Shared statement-level parts defeat both proof systems.

To these, add that **binding (commitment and tree collisions) is shared by both systems.** An
attacker who finds a collision in `H_cm` or `H_nkc` makes a *true* statement that both systems
prove. The two-system design gives no protection there. Only the outflow caps and the value-cap
ratchet (spec §13.3.5, §13.3.6) bound the damage.

**Is anything in the privacy path bounded by a category 3 component in M-1?**

| Privacy path | M-1 as written | Level |
|---|---|---|
| Note packages (ML-KEM-1024, ChaCha20 key from `H_pkg-key`) | 5 | 5 (FIPS 203 from memory) |
| Commitment hiding (`rcm` 32 B), nullifier PRF, tags, address diversification | 256-bit keys | 5 |
| Zero knowledge of the proofs | statistical, everlasting ([SG26] Thm 6.6 (3)) | no category applies; Q·ε_hvzk **open** in both systems |
| Private retrieval (DPF) | 128-bit seeds | **1** |
| Transport (X25519 + ML-KEM-768) | unchanged | **3** |
| Single-server lattice PIR (if used) | below ML-KEM-512 | **below 1** |

The 48-byte digests and the 256-bit field bound soundness and binding, not privacy. The zero
knowledge's leaf term depends on digest length only through `b_l − b`, which the salts handle.

**So "category 5 privacy" is an overstatement until K3-8 is done.** The honest labels are:

| Profile | Soundness | Binding | Spend | Privacy |
|---|---|---|---|---|
| M-1 as written | 3, quantum half by attack estimate | 4 (48-byte collisions) | 5 (Falcon-1024) | 5 for packages and keys; 3 for transport; 1 for DPF retrieval; zero knowledge statistical with HVZK open |
| M-1 with K3-8 | 3 | 4 | 5 | 5, with HVZK open |
| M-2 | 3 | 4 | 5 | 3; DPF 1 unless fixed |
| M-3 | 3 | 5 | 5 | 5 with K3-8 |

---

## 7. The record's §8 list (V16)

1. **Plan §9 / design basis §1 "parameters only"**: **confirmed.** The plan's §9 still says
   "a release that changes parameters only". The specification fixes 32-byte outputs (§3.1).
   BLAKE3's claim is 128 bits. The salt and digest coupling is real (at the wording of V9).
2. **Plan §0 "9,500"**: **refuted as stated.** Plan §0 calls 9,500 "the ceiling set by the 2 MB
   block", which is accurate. Plan §5 gives about 5,600 at the launch weight and `W` ≥ 4.82 MB
   for the ceiling. The defect is presentation only: §0 omits the weight figure.
3. **Plonky3 / SHA-256 naming**: **confirmed.** The plan's §2 glossary (system B "on Plonky3's
   binary stack"), its framework table and SQ-23 still say Plonky3. The specification's A.2 /
   A.3 name SHA-256 for B's Merkle hashing, while SQ-48 decided BLAKE3 (provisionally).
4. **E1's A limit**: **confirmed.** 600,340 B > 530 KiB (542,720 B). Add V17: W4 is violated by
   today's measured leaves.

---

## 8. Feasibility of the profiles

### 8.1 The limits used

These are the plan's limits (E1, E2, spec §2, §16.2):

- wallet proof on a phone in 10 s or less, within 512 MB, each leaf proof at most 530 KiB (A)
  and 576 KiB (B);
- proofs at most 1.75 MiB, block weight 4 MB;
- 1,500 leaves merged in 60 s on 8 hosts of 16 cores;
- transfers per block.

**No phone measurement exists** (plan step 0.15 not started). Times are M5 single-thread
figures; phone factors are not known.

### 8.2 The profiles

**P1. Category 1 throughout** (as built). Falcon-512, 32-byte digests, BLAKE3 for B, ML-KEM-768,
DPF λ = 128.

- *Meets today*: proof size limit; B's leaf size.
- *Meets with named engineering*:
  - A's leaf size and W4 (R-14 streamed commitment, or `LEAF_RESERVE` ≥ 1,202,000);
  - memory below 512 MB (A: R-14; B: `wallet-memory.md` steps L-5a, L-4b to L-4d, d, e;
    measured today at 897 MiB / 1,095 MB);
  - E2 (12 to 15 hosts estimated; with D-6, K = 7 or 15 and the cap layer, the record's 5.1
    (c) gives about ×0.75, which is still about 9 to 11 hosts);
  - capacity about 5,900 to 6,200, less the W4 repair.
- *Cannot meet*: nothing identified.
- *Proven*: rows at 152.52 bits from published bounds. *Unreviewed*: the tree accounting
  (O-13), the recursion heuristic C2, ε_hvzk, BLAKE3's cryptanalysis (H-1).
- *What an attacker gains*:
  - **Forgery** needs a bad challenge in *both* systems. Classically that is about 2^129 hash
    calls each; quantum, about 2^129/D oracle calls each under depth D. Consequence: counterfeit
    YEC in the pool, extractable only through the outflow caps and the ratchet. Canaries pay a
    claimant; the pause stops further damage.
  - **Collisions** on 256-bit statement digests (2^128 classical calls, category 2) give a
    double-opened note: inflation that **both** systems accept. Bounded only by the caps.
  - **Falcon-512** needs a leaked `pk`. The gain is theft from that one user.
  - **Privacy**: ML-KEM-768 packages and transport are category 3 against record-now-decrypt-
    later. DPF retrieval is category 1, so a logging host links wallets to their reads.

**P2. Category 1 soundness with category 5 privacy and long-lived secrets** (the record's M-4,
completed). P1 plus ML-KEM-1024 (+384 B a full address, +480 B a package), DPF at λ = 256,
ML-KEM-1024 in the transport, and leaf salts by the zero-knowledge target.

- *Limits*: as P1. Package and address growth and about 2× DPF key size are within E5's margins
  by the record's figures; E5 must be re-measured.
- *Proven*: as P1, plus FIPS 203's claim (from memory).
- *What an attacker gains*: as P1 for soundness and binding. Privacy is closed against
  recording, except for ε_hvzk, which is open.

**P3. M-1** (the record's recommendation).

- *Meets with engineering*: proof size limit (nodes at 1/4 and 1/16).
- *Cannot meet with the current constants*:
  - E1 size (939 / 970 KiB estimated);
  - E1 memory (about 2× P1 with Falcon-1024; prove time about 2× P1);
  - capacity: **0 at `W` = 4 MB**. It needs `W` ≥ 5.67 MB for P1's capacity.
- *E2*: 33 to 44 hosts (corrected), or 18 to 24 with B's Johnson row, which is unreviewed
  (DKT26 preprint, L-J1 to L-J3).
- *Proven*: the same theorems at more queries. The quantum half is an attack estimate (§3.3).
- *What an attacker gains*: forgery at about 2^193 per system classical. Binding at 48-byte
  collisions (2^192, category 4). Privacy: see §6, which needs K3-8.

**P4. Category 3 throughout** (M-2): as P3, without ML-KEM-1024 and with the transport kept at
category 3.

**P5. Category 5 throughout.**

- *Cannot meet*: `PROOF_BYTES_MAX` (unique decoding); E2 at 57 to 80 hosts or more; W4; E1.
- *Needs*: a new field in both systems; `W` ≈ 9.1 MB; or list-decoding rows (unreviewed).
- *Proven only* with the rows that exceed the limits.

**P6 (the referee's). Shared parts above per-system parts.**

- **Per-system parts at category 1.** These are the parts the two-system design protects: rows
  at 152.52 bits, the proof-internal hash (A Keccak, B BLAKE3), the 256-bit field.
- **Shared, statement-level parts one level higher.** These are the parts it does not protect:
  binding digests stay 32 bytes, which is **category 2** by [CFP]'s own definition, already
  above the rows.
- **Falcon-512, with `pk` secret** (§2.2); scheme byte `0x02` reserved for Falcon-1024.
- **P2's privacy set**: ML-KEM-1024, DPF λ = 256, ML-KEM-1024 transport, salts from a stated
  zero-knowledge target.
- **Every row parameter kept generic**: digest length, field, salts and query counts as row
  fields (spec A.2 already carries `level`, `digest_bits`, `salt_bits`). Category 3 soundness is
  then a later release once E2 allows it. That release changes K3-1 to K3-3 and needs the
  specification change of K3-1.

*Limits*: as P2. *Claims*: soundness category 1 in each of two independent systems, binding
category 2, spend category 1 behind a category 5 hiding hash, privacy category 5 (HVZK open).
*What an attacker gains*: as P1 for soundness. Binding requires a 2^128-classical collision
search per attempt on a shared digest, which the caps bound.

### 8.3 The referee's opinion

**This is the referee's opinion, not a finding.** P6 (equivalently P2 with the hidden-key reading
of Falcon) is the most favourable feasible profile today, for three reasons.

1. It is the only profile whose phone, block and host limits are reachable with engineering
   already named. P3 and P4 cannot fit a bundle at `W` = 4 MB, and cannot meet E1 on memory
   with Falcon-1024.
2. It spends on the one argument the record gets right: privacy is retroactive. It closes the
   three privacy gaps the record missed (DPF, transport, lattice PIR) at a small cost.
3. It keeps category 3 soundness one release away, behind row fields. That is the
   "parameter-only" path the plan wanted, made true by building K3-1 to K3-3's interfaces
   without switching them on.

The record's bias shows in three places:

- it does not price P2 / P6;
- it treats Falcon-1024 as unconditional;
- it reports category 3 capacity as 1,970 instead of 0.

What would change this opinion:

- E2 met at category 3 by measured B recursion (SHA-384 slot counts, D-6, the Johnson row
  reviewed);
- a phone measurement of a Falcon-1024 leaf within 512 MB;
- the lead architect reading the public-key convention as binding for the spend authority.

---

## 9. Work that closes the findings

| Task | Done when |
|---|---|
| F-1 Cite [CFP] §4.A.5 and [FIPS204] Table 1 / D.1 for conditions G and H; remove "from memory" there; state the realistic collision model | `soundness-method.md` 8.1 and the record §1.1 cite pages; BHT stated as not used |
| F-2 State the Keccak-versus-AES premise for G as depth × size | the premise is cited or labelled an assumption in `soundness-method.md` 8.2 |
| F-3 Relabel the quantum half of categories 3 and 5 as an attack estimate; proven QROM to 2^κ_Q queries | record §1.2 and §3.5 reworded |
| F-4 Define a zero-knowledge target; derive leaf salts (83 / 91 B at 48-byte digests for 2^-96 / 2^-128) | the calculator prints the salt row from the target |
| F-5 Add DPF, transport, lattice PIR, `nkc_d` / `auth_d` / `H_addr` owner collisions to the inventory | the record's §2 lists them with levels |
| F-6 Fix W4: shrink the leaves or set `LEAF_RESERVE` ≥ 1,202,000; recompute capacity at every category with the category's `LEAF_RESERVE` | `bundle_rules.json` vectors regenerated; capacity table shows 0 at category 3 for `W` = 4 MB |
| F-7 Rebase B's host scaling on `parameters.md`'s category 1 figure | the record's T7 gives 33 to 44 hosts at category 3, or replaced by the B builder's slot counts |
| F-8 A's category 5 field need: 312 bits | the record's §0 and §3.4 corrected |
| F-9 Price P2 / P6 and the hidden-key reading of Falcon in the record | §6 and §7 of the record carry both |
| F-10 Plan §0 wording | add "about 5,600 at the launch weight" beside 9,500 (lead's plan; reported here) |

## 10. Provenance

- **Published, used as is**: [CFP] §4.A.5–4.A.6; [FIPS204] §4 Table 1, §5.4 footnote 6,
  Appendix D.1; [FIPS205] §10.2 footnote 18, §11 Table 2 and text, §11.2.2; [COSE-FN] Table 1;
  [GLS26] abstract, §1; [SG26] §6.3, Theorem 6.6 (2)–(4), pp. 58–59. BGI16 DPF and Hirose PRG
  are as described in `yugen-pir/docs/pir-selection.md` (not re-read here). DP24 ring switching
  is as recorded in `REFERENCES.md` 1.1 (not re-read here).
- **Original (the Ycash developers, 2026), unreviewed, first in this document**:
  - the hidden-key reading of the spend authority's level (§2.2; it restates the plan's §9
    remark);
  - the shared-versus-per-system level rule and profile P6 (§8.2);
  - the observation that binding collisions bypass the two-system defence (§6);
  - the W4 violation (§4.3);
  - the category 3 zero-capacity result under the record's own `LEAF_RESERVE` (§4.3);
  - the DPF and transport privacy ceilings (§2.1);
  - the gap between the QROM query bound and NIST's quantum budget (§3.3).

  Checked against [CFP], [FIPS204], [FIPS205], [SG26] and the record. None of these states
  them for this design. These rows belong in `REFERENCES.md` Part 3. The referee was told to
  edit no other file, so the lead should add them.
