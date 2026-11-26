# The transcript of both systems: spBCS, and Sharp–Grubbs Theorem 6.6 (2)

Part of Yugen. Closes the analysis part of finding C-7 of `CITATION-AUDIT.md`: the
transcript both proof systems adopt, written so that an engineer can implement it, every
hypothesis of the published QROM theorem that covers it checked against each system, the exact
loss, and the resulting QROM bits for a tree of 20,000 proofs. Revision 2 (2026-11-19), after the
independent referee report `qrom-zk-referee.md`. Revision 1 (the "CMS form" with an adapted Theorem
Q) is kept in sections 7 and 8 as the record of the alternatives. Section 2.8 (added the same day)
records the two builders' deviations from section 2 with their byte layouts, checks each against
Theorem 6.6 (2)'s hypotheses, and restates MA-2 as MA-2' for system B's BLAKE3 framing.

**Amendment 2026-11-19 (`zkq-te3-r8-referee.md` M-2, checked against the code; not a rewrite).** The rows of
section 6 that say "not as built" for the transcript (H6) and for B's de-duplicated positions (H7) are **stale**:
both systems carry this section's spBCS transcript natively and in circuit (`yugen-proof-a` `084fbdd`:
`vendor/leanMultisig/crates/verifier/src/spbcs.rs` tags 61-64, header 351-360, `distinct` 400, rows
`TranscriptKind::SpBcs` in `params.rs` 316-317, 335-337, guest `guests/e2/a_fs.py` 214; `yugen-proof-b2` `395da08`:
`vendor/binius64/crates/transcript/src/fiat_shamir/spbcs.rs` 11-19, 45-53, `src/params.rs` 141-147, framing
version 2 with positions de-duplicated, change 34). Findings Q-1 and Q-2 (section 7) are the record of the
transcripts before T-1 and T-2. What differs from the security profile is the **salt length**: both systems build
a 64-byte proof salt (`SALT_BYTES = 64`, A `spbcs.rs` 75, B `spbcs.rs` 53) and 64-byte leaf salts, against profile
Y's 80 B proof salt and 80 B (A) / 96 B (B) leaf salts (`zk-quantum.md` amendment 2.2). The soundness figures of
this document do not depend on salt length beyond `b_l > b`.

Status tags: **(P)** proven here, **(S)** read in a primary source during this work (named),
**(C)** computed (`../soundness`, revision 6, `--rev6`; `../qrom/test_numbers.py`), **(M)** from
memory, **(U)** open.

## 0. Decisions this document writes down

Lead decisions (lead agent, 2026-11-19; open to the lead architect's review):

- **D-a. Transcript form.** Both systems adopt the spBCS transcript of Sharp and Grubbs (Protocol
  6.5): each challenge is hashed from the whole past, its stream is a separate long-output call, and
  the stream's digest is written back into the next challenge input. A published theorem (Theorem
  6.6 (2)) then applies. System A: SHAKE256 streams. System B: **SHAKE256 streams by default** (the
  published theorem as is); counter-mode SHA-256 streams with Lemma X are the documented
  alternative (Adapted), to be chosen only on measured in-circuit cost (section 9, task T-4). The
  "CMS form" of revision 1 is withdrawn as the target: form X is kept as a recorded alternative with
  its three hypotheses (section 7.2); form C is stated as unproved, with the referee's fix (7.3).
- **D-b. Salts.** 512-bit (64-byte) leaf salts on every tree of a leaf proof **and** a 64-byte
  per-proof salt in every challenge input and every stream point (Theorem 6.6 (3)). The per-proof
  salt is in the spBCS specification below; its use is `zk-quantum.md`.
- **D-c. Scope of zero knowledge.** Required of leaf (wallet) proofs only; `zk-quantum.md` 3.4.

## 1. Sources and provenance

Read for this revision (2026-11-19; text extracted from the lead architect's copies into a scratch
directory outside every repository):

- [SG26] C. Sharp, P. Grubbs, "Faster and Smaller Anonymous Credentials from Standardized
  Signatures" (the GordieHowe system), Cryptology ePrint Archive, Paper 2026/2615 (no date on the
  copy): Section 6 in full (6.1: Definitions 6.1 to 6.4; 6.2: the text before Protocol 6.5 and
  Protocol 6.5; 6.3: Theorem 6.6 and the text after it), Definitions 2.16 to 2.20, 2.22 and Lemma 2.21
  (statement), Appendix I.1 in full (Definition I.1, Lemma I.2, the oracle's domain, hash functions,
  challenge inputs, leaves, samplers, Merkle trees, prover and verifier), I.3 (Protocol I.9, Theorem
  I.16 and its proof; Lemmas I.12 to I.15 by statement only), Section 8.4.
- [CMS19] A. Chiesa, P. Manohar, N. Spooner, "Succinct Arguments in the Quantum Random Oracle Model",
  ePrint 2019/834 (copy dated January 14, 2020): read for revision 1 (Sections 3.3, 4.2, 5.1, 6.1 to
  6.3, 7.1, 8.1 to 8.6); used here for Theorem 8.6 and the record of section 8.
- [CY] A. Chiesa, E. Yogev, "Building Cryptographic Proofs from Hash Functions" (version 1.2, March
  25, 2026; a copy fetched by an earlier session, not among the lead architect's files): Construction
  25.1.1, Remarks 25.1.2, 25.1.3, Theorem 25.2.1 (read again for finding Q-5), Definitions 23.2.1,
  23.2.2 and Theorem 31.2.1 (through the referee's reading, `qrom-zk-referee.md` 1.1).
- [BCS16] E. Ben-Sasson, A. Chiesa, N. Spooner, "Interactive Oracle Proofs", ePrint 2016/116: the
  introduction's description of state restoration (used in Observation 1).
- Code read (S): leanVM verifier at the pin (`crates/verifier/src/transcript.rs`, `merkle.rs`,
  `whir.rs`); Binius64 at the pin (`crates/transcript/src/fiat_shamir/hasher_challenger.rs`,
  `crates/iop/src/merkle_tree/scheme.rs`, `crates/hash/src/sha256.rs`).

Provenance of each result:

| Result | Label | Where |
|---|---|---|
| spBCS transcript (Protocol 6.5, Section I.1) | **Published** [SG26] | section 2 instantiates it |
| Theorem 6.6 (2), its quantities (Definition I.1) | **Published** [SG26] | sections 3, 4 |
| The byte-level instantiation for A and B (tags, labels, field order, running state) | **Original (the Ycash developers, 2026)**, as an engineering choice within Section I.1's freedom; the running-state implementation is the referee's note (`qrom-zk-referee.md` 4 (i)) | section 2 |
| Counter-mode streams with Lemma X | **Adapted** (Theorem 6.6 (2) with Lemma X; change: `t -> 2t`) | 2.5, 4 |
| Lemma X | **Original as far as checked** (sources: CMS19 Sections 3, 6 to 8; CY Chapters 15, 18, 25; [BGKTTZ23] Section 3) | 7.1 |
| Observation 1, findings Q-1, Q-2, Q-4 | **Original as far as checked** (same sources) | 7 |
| Finding Q-5 (condition C under the ROM part of Theorem 6.6 (2)) | **Original (the Ycash developers, 2026)** | 6.2 |
| Theorem Q, forms X and C | **Adapted** from CMS19 Theorem 8.6, a proof sketch (X) and unproved (C); record only | 8 |
| The tree accounting (union over the proofs) | **Original**, `REFERENCES.md` O-13 | 5 |
| The byte layouts of 2.8 | **Original (the Ycash developers, 2026)**, the builders' (`yugen-proof-a` §2.5, `yugen-proof-b2` §10.2, §10.4) | 2.8 |
| The hypothesis checks of 2.8, Lemma D, the stream-point length finding | **Original (the Ycash developers, 2026)**, unreviewed (`REFERENCES.md` O-65, O-66) | 2.8 |
| MA-2' | **Original** modelling assumption (`decision-b-merkle-hash.md` H-1.6), supported by [B3] 4.2, 4.3 | 2.8 B-4 |

## 2. The spBCS transcript, as built in each system

### 2.1 What every proof does (SG26 Protocol 6.5, total order, no merges)

Messages are numbered `1 .. N_msg` in protocol order. A prover message `i` has a non-oracle part
`a_i` (field elements the verifier reads in full) and `m_i >= 0` oracle strings, each committed by
its own Merkle tree with root `rt_(i,j)`; its **item** is `W_i = a_i || rt_(i,0) || .. ||
rt_(i, m_i - 1)`. A verifier message `i` is one or more challenges; its **item** is the written-back
digest `dg(y_i)`, the first 32 bytes of its stream. Per proof the prover draws one **proof salt**
`s` of 64 bytes from the system CSPRNG. For verifier message `i`:

1. **Key.** `u_i = H_ch( label || s || pre(x) || item_1 || item_2 || .. )`, the items of every
   message before `i` in order (prover items and written-back digests alike), 32 bytes out.
2. **Stream.** `y_i = H_stream( u_i || s )`, `32 + e_i` bytes, long enough for every challenge of
   message `i`.
3. **Challenges.** `theta_i = sample_i(y_i)`: the message's challenges read in order from a prefix
   of `y_i` (2.4).
4. **Write-back.** `dg(y_i) = y_i[0 .. 32)` is the item of message `i`.

The proof is `pf = (s, (W_i) for prover messages, the salted leaves at the queried positions, their
authentication paths)`. The verifier recomputes every key, stream and challenge from `pf` in the
same order, rejects if a sampler fails, checks every path against its root, and runs the IOP
verifier on the statement, the challenges, the non-oracle parts and the opened values (Protocol 6.5,
step 2). The challenge input of message `i + 1` extends that of message `i` (no index is written
for the total order without merges; SG26 Section I.1, "Challenge inputs"), so prover and verifier
keep **one running hash state** over `label || s || pre(x) || items`, absorb each item once, and for
each key clone the state and finalise the clone: one finalisation per verifier message, never a
re-hash of the past (the referee's implementation note, `qrom-zk-referee.md` 4 (i); for Keccak the
clone pads and permutes, for SHA-256 the clone pads and compresses).

### 2.2 The four oracle parts and their encodings

SG26 Section I.1 requires one random oracle with four parts, injective encodings and disjoint
images: challenge inputs, leaves, internal nodes, stream points. Each input begins with a **part
tag** byte; the two systems use different tags, so no input of one system is an input of the other.

| Part | System A (leanVM) | System B (Binius64) |
|---|---|---|
| Challenge input (key) | `Keccak-256( 0x10 || "Yugen/spBCS/A/v1" || s || pre(x) || items )` | `SHA-256( 0x20 || "Yugen/spBCS/B/v1" || s || pre(x) || items )` |
| Leaf | `Keccak-256( 0x11 || ser(row) || r )` | `SHA-256( 0x21 || ser(values) || r )` (**new tag**, referee 1.6) |
| Internal node | `Keccak-256( 0x12 || left || right )` | the SHA-256 compression function from the domain-separated initial state `IV'`, on `left || right`, as built (no tag; 2.6) |
| Stream point | `SHAKE256( 0x13 || u_i || s )[0 .. 32 + e_i)` | default `SHAKE256( 0x23 || u_i || s )[0 .. 32 + e_i)`; alternative `SHA-256( 0x23 || u_i || s || ctr_be32 )` for `ctr = 0, 1, ..`, concatenated (2.5) |

- `label` is a fixed 16-byte string; `s` is 64 bytes; `pre(x)` is a 4-byte big-endian length
  followed by the statement's bytes (the verifying key or its digest, the circuit identifier, the
  parameter row and shape, and every public input), a prefix-free encoding from which the statement
  is decoded (SG26 I.1: "The statement encoding is prefix-free").
- Items are fixed-length in the fixed schedule of the parameter row: field elements as 32-byte
  strings (A, B: `GF(2^256)`; B's `L = GF(2^128)` values as 16 bytes), roots as 32 bytes, a
  written-back digest as 32 bytes. A message with no oracle has no root in its item. The schedule
  is a function of `pre(x)`, so items need no lengths (SG26 I.1: "uniquely decodable in the fixed
  schedule").
- `r` is the leaf salt: 64 bytes on every tree of a leaf proof (D-b), empty (0 bytes) on node proofs
  (soundness holds at every salt length, including 0: SG26 I.1, first paragraph). The salt sits
  after the row because both systems' trees put it there today; with fixed-length rows the encoding
  is injective either way.
- A part tag on A's internal nodes makes the input 65 bytes: still one Keccak-f[1600] (rate 136). On
  A's leaves it adds one byte: a level-0 leaf (512-byte row, 64-byte salt) stays at 5 Keccak-f, a
  later leaf at 3 (`zk-quantum.md` 4).

### 2.3 Where the proof salt enters

In every challenge input (after the label, before the statement) and in every stream point (after
the key). Nowhere else: leaves and internal nodes carry no proof salt (SG26 Protocol I.4's proof of
zero knowledge relies on exactly this: "they query leaves and internal nodes, which carry no proof
salt", Theorem I.5 step 2). Every proof of both systems carries it, leaf and node alike, so there is
one transcript module per system; for node proofs it costs 64 bytes and changes no theorem.

### 2.4 Challenges per call and samplers

One stream per verifier message, all of the message's challenges read from it in order: a
sumcheck round's challenge; `(alpha, beta)` as bytes `[0, 32)` and `[32, 64)`; a query round's
positions as consecutive fixed-width bit fields (A's `sample_queries` reading, `128 / depth`
positions per 128-bit word, is such a prefix reader); a level's out-of-domain point. Every challenge
set has power-of-two size (`GF(2^256)` as 32-byte strings; positions in `[2^n]` as `n`-bit fields),
so each sampler is a bijection on its prefix, every challenge has the same number of preimages, no
sampler rejects, and `eps_ov = 0` (SG26 Definition I.1 item 2; Section I.1 "Samplers"). A future
challenge set that is not a power of two gets SG26's rejection sampler with the stream excess of
Section 6.3 ("four extra bytes per byte"), and `eps_ov` enters the calculator. The query list
`qry(theta)` is the list of **distinct** positions (SG26 Definition 2.18: "without repetitions");
the proof carries exactly one salted leaf per distinct position (Section I.1, "Prover and
verifier"), which changes A's proof format (today one full path per query, duplicates included).

### 2.5 System B's alternative: counter-mode SHA-256 streams (Adapted)

`y_i = SHA-256(0x23 || u_i || s || 0) || SHA-256(0x23 || u_i || s || 1) || ..`, truncated to
`32 + e_i` bytes (two compressions per block: 101-byte inputs). By Lemma X (section 7.1) an
adversary making `t` quantum queries to SHA-256 is perfectly simulated by one making `2t` queries to
the pair (SHA-256 off the stream part, the long-output stream function), which is the oracle of
Theorem 6.6 (2). So the theorem applies with `t` replaced by `2t` (the verifier's `k_q` unchanged:
it calls the stream function once per message). Cost in bits: 1.00 (section 5). The decision between
the two is task T-4 (section 9).

### 2.6 System B's internal nodes (finding Q-3, corrected)

B's internal node is the SHA-256 compression function on `left || right` from a fixed,
domain-separated initial state `IV'`, with no padding. The node part of SG26's oracle is modelled by
`m -> f(IV', m)`. The reason this is a modelling assumption is **not** Davies–Meyer fixed points
(revision 1's reason was wrong; referee 1.7): fixed points need the attacker to choose the chaining
input, and with `IV'` fixed, `m -> E_m(IV') xor IV'` at distinct `m` uses distinct keys and is a
random function in the ideal-cipher model (classical reasoning; a quantum ideal-cipher statement is
not in hand, M). Modelling `f(IV', .)` as a random oracle on 64-byte inputs, separate from SHA-256
on tagged inputs, is the same kind of heuristic as SG26's own modelling of SHA-384 and cSHAKE256 as
one oracle (Section I.1, "Hash functions"). Kept as built; recorded as modelling assumption MA-2
(section 3). Replacing it by `SHA-256(0x22 || left || right)` costs one more compression per node.

### 2.7 Cost

Proof size: +64 bytes a proof (the proof salt); the leaf salts' bytes are `zk-quantum.md` 4.
Hashing, per verifier message: one key finalisation and one stream call, against one permutation
(A) or one SHA-256 (B) as built; absorption of items at rate 136 (A) or 64 (B) bytes. System A,
upper figure (E): about one more Keccak-f per verifier message, about 600 per verified proof, against
10,670 Keccak-f per leaf verified in a sub-bundle (`recursion.md` 9.10, M): about +5.6 %. System B
with SHAKE256 streams: about 600 to 700 Keccak-f a verified proof in the node circuit (most streams
fit one permutation; the longest, 713 bytes, needs six); the Keccak-f gadget exists in B's framework
(the wallet statement hashes its note tree with SHA3-256, `yugen-proof-b2/docs/statement-layout.md`).
Measured costs are task T-4.

### 2.8 The builders' deviations, for referee review (added 2026-11-19)

Both builders implemented sections 2.1 to 2.6 with deviations they recorded. Each is written
below with the exact byte layout **from the builder's own document** (read-only:
`yugen-proof-a/docs/parameters.md` §2.5 at `4654f15`, unchanged at `0ce1eb9` (checked by `git diff`); `yugen-proof-b2/docs/parameters.md` §10.2
and §10.4 at `b8871ff`), and checked against the hypotheses of Theorem 6.6 (2) as [SG26] states
them: Protocol 6.5 (Section 6.2, p. 57), Theorem 6.6 and the text before it (Section 6.3, pp. 58
to 59; "the samplers, and the encodings of Section I.1 and their decoders run in polynomial
time"), and Section I.1 (pp. 130 to 131: the oracle's domain, hash functions, challenge inputs,
leaves, samplers, Merkle trees, prover and verifier), with Definition 2.18 (p. 13: `qry(theta)` "a
list ... without repetitions"). All read in this pass from the text layer (S). Verdicts are the
Ycash developers' (2026), unreviewed.

**Summary.**

| # | Deviation | Hypotheses of Theorem 6.6 (2) | To re-prove or change |
|---|---|---|---|
| A-1 | Part tags 16 bytes as built (8 bytes under lead decision Q1), value in the first byte | **hold** | nothing for the theorem; spec §3.3's length registry (see below) |
| A-2 | First challenge at stream byte 32; byte 128 to 135 of each output block skipped | **hold** | nothing; H9's longest stream grows by 32 bytes (lowers the stream term) |
| A-3 | Block form of the challenge input (four items a block, Keccak padding in band); six-item header with 24 zero bytes after the row | **hold**: still one Keccak-256 of the whole past, not a chain | nothing new; the decodability argument below to be checked by the referee; the duplex citation is not needed (to be verified) |
| A-4 | One leaf and path per distinct drawn position; two different openings of one position refused | **hold** | nothing |
| B-1 | `pre(x)`'s length covers the identifier only; public words as the first item | **hold**, given that the public-word count is a function of the identifier | nothing |
| B-2 | Index = 4 stream bytes, little-endian, masked to `n` bits | **hold** | nothing; H9's longest stream is 944 bytes (1,504 at 368 queries) |
| B-3 | Repeated query positions not de-duplicated | **do not hold as stated** (Definition 2.18, I.1 "Prover and verifier") | Lemma D below (a reduction, Original) and one of its two closures; or de-duplicate (T-3) |
| B-4 | BLAKE3 `derive_key` framing for leaves and nodes, no tag | **hold under MA-2'** (replaces MA-2 for the BLAKE3 build) | MA-2' is a modelling assumption for the referee |

**A-1. Part tags (system A).** As built a part tag is **cell-wide, 16 bytes: the tag value in the
first byte and fifteen zero bytes**. Lead decision Q1 made it **lane-wide, 8 bytes: the value in
the first byte and seven zero bytes**; the builder kept 16 so that every 32-byte item stays two
whole 16-byte cells of the in-circuit `KECCAK` row, and puts the 8-byte form to the lead.

| Part | Tag bytes as built | Input as built | Length |
|---|---|---|---|
| challenge input | `10 00×15` | the block form (A-3) | multiple blocks |
| leaf | `11 00×15` | `Keccak-256(tag ‖ row words ‖ leaf salt)` | 16 + row + salt |
| internal node | `12 00×15` | `Keccak-256(tag ‖ left ‖ right)` | 80 bytes, one Keccak-f |
| stream point | `13 00×15` | `SHAKE256(tag ‖ key ‖ proof salt)` | 112 bytes, one block |

*Hypotheses.* I.1 requires four injective encodings with disjoint images; the implementation
there begins each input "with a byte naming its part". A fixed 16-byte (or 8-byte) prefix whose
first byte names the part gives disjoint images, and each encoding stays injective (the rest is
section 2.2's injective encoding, salts of fixed length). MA-1 (Keccak-256 and SHAKE256 as one
oracle on disjoint parts) is unchanged. **Holds in both forms.** *Outside the theorem:* the
specification's §3.3 separates the unframed SHAKE256 calls partly by length and lists the stream
points as 97 bytes. As built A's stream point is **112 bytes** (no other unframed SHAKE256 input of
that length; framed calls begin `0x59`), so §3.3 must list 112. In the 8-byte form it would be
**104 bytes, the length of Falcon's hash-to-point input `nonce ‖ m`**, whose first byte is a random
nonce byte, so the two input sets would intersect: Q1's form needs a separation argument by content
that the nonce does not allow. Finding (Original, the Ycash developers, 2026; `REFERENCES.md`
O-65): keep the 16-byte form, or prefix the stream point so that no 104-byte input begins with it.

**A-2. The first challenge at byte 32 (lead decision Q2).** A stream's bytes 0 to 31 are the
written-back digest only; challenges are four-lane field elements read from bytes 32 to 127 of the
first 136-byte output block (three challenges), then bytes `136 j` to `136 j + 127` of block `j`
(four each); lane 16 (bytes 128 to 135) of every output block is skipped.

*Hypotheses.* I.1 "Samplers": the sampler is deterministic, reads a prefix, and every challenge
has the same number of preimages; "the written-back digest `dg(y_i)` is the first 8b bits of the
same stream". A's sampler reads the prefix `y[0 .. 32 + e_i)` and ignores the skipped bytes, so each
challenge has the same number of preimages (the ignored bytes multiply every count by the same
factor), a uniform preimage is drawn by filling the ignored bytes uniformly, `eps_ov = 0`, and the
write-back is still the first 32 bytes. The stream is longer by 32 bytes plus 8 a block; by the
last paragraph of Section 6.3 a longer stream only lowers the `2 sqrt(k_q / 2^(8(b+e)))` term.
**Holds.** H9's longest stream for A becomes the section-4 figure plus these bytes (T-1 reports it).

**A-3. The block form of the challenge input.** An item is 32 bytes. The header is

```
tag (16) ‖ "Yugen/spBCS/A/v1" (16) ‖ s (64) ‖ be32(92) ‖ row (le32) ‖ 0^24 ‖ bound IV (32) ‖ public input (32)
```

192 bytes, six items; `pre(x)` is the last 96 bytes. A block holds at most four items; it is
closed with Keccak's padding (`01`, zeros, `80` at byte 135) when a fifth item arrives and when a
key is taken. The challenge input of a verifier message is every closed block (136 bytes each,
padding bytes included) followed by the open block's items, and the key is Keccak-256 of that
string: one sponge state serves every key (closing a block is one Keccak-f, the key is the state's
first 32 bytes, the state continues). The write-back is the first item of the next block.

*Hypotheses.* I.1 "Challenge inputs" asks for `ch(label ‖ salt(s) ‖ pre(x) ‖ items(i, ℓ_i))` with an
injective `ch`, items "uniquely decodable in the fixed schedule, so a challenge input determines
`(s, x, i, ℓ_i)`", and a polynomial-time left inverse of the statement encoding. (a) *The key is a
Keccak-256 value of a well-defined string.* A sponge that absorbs full 136-byte blocks and then the
padded final block computes Keccak-256 of the concatenation of the full blocks and the final
block's data; the in-band `01 … 80` bytes of closed blocks are ordinary message bytes. So the key
of message `i` is `Keccak-256(S_i)` with `S_i` = closed blocks ‖ open items, and continuing the state
after the key is the sponge absorbing `S_i`'s last block, now padded, as a full block. This is the
sponge definition (from memory, FIPS 202 / the Keccak reference, not in the folder); the
builder's citation of the duplex paper is not needed for it. (b) *Injectivity and decoding.* The
schedule fixes where every key is taken and how many items lie between, as a function of `pre(x)`
(the row); so the padding positions of `S_i` are determined, and stripping them gives back the
byte-continuous string of section 2.1, from which `(s, x, i, ℓ_i)` decode as there; the number of
items, hence `i`, follows from `|S_i|`. The header's zero bytes are fixed. (c) *Disjointness*: `S_i`
begins with the challenge tag. **Holds**; nothing to re-prove. For the referee: the
decodability argument (b) and the reading (a).

*Chain of padded blocks, or one hash of the whole past?* The question is whether the block form is
a hash chain (each key a hash of the previous state and new items, as in BCS16's chain or form C
of section 7.3), which would put it outside Protocol 6.5 and need an extra collision-resistance or
indifferentiability step. It is not. By (a), every key is **one** evaluation of Keccak-256 on the
whole past `S_i`, read from the first block; no intermediate digest is ever an oracle input or an
item, and the state that "continues" is the sponge's internal state, not a 32-byte output fed
back. The block form changes only the encoding `ch`, by inserting fixed bytes at positions the
schedule determines, and Theorem 6.6 (2) allows any injective, polynomial-time-decodable `ch` with
a disjoint image (I.1). So the oracle the theorem idealises is still "Keccak-256 on the challenge
part" (MA-1, unchanged), and no loss is added. What would change this: a key taken from a
truncated or cloned state that is not the result of absorbing `S_i` with Keccak's final padding
(for example a capacity-reduced or re-keyed state), or an intermediate key re-absorbed as an
item in place of the write-back. The builder's tests recompute every key from the padded byte
strings with the `sha3` crate (`tests/spbcs.rs`), which checks (a) on the vectors.

*The duplex citation.* The builder cites Bertoni, Daemen, Peeters, Van Assche, "Duplexing the
sponge" (SAC 2011) from memory for "the state after closing a block is the sponge of the padded
string". That paper is not in the reference folder: **to be verified**. The argument above does
not depend on it: (a) uses only the definition of the Keccak sponge (absorb full blocks, pad the
last; FIPS 202 / the Keccak reference, also from memory, not in the folder), and no duplex
security bound is invoked. The duplexing lemma would be needed only if the key were taken from a
duplex call whose input is not the whole past, which the build does not do.

**A-4. One Merkle path per distinct drawn position.** Also as built in A, and meeting the theorem
(I.1 "Prover and verifier"; Definition 2.18's list without repetitions, after de-duplication of
the drawn list): one salted leaf and one path per **distinct** position on the wire,
a proof holding two different openings of one position refused (I.1 "Prover and verifier", H7);
positions read by `whir::sample_queries` from whole field elements (section 2.4); no grinding.

**B-1. `pre(x)` (system B).** The running input as built:

```
0x20 ‖ "Yugen/spBCS/B/v1" ‖ s (64 bytes) ‖ BE32(len) ‖ StatementId::bytes() ‖ items
```

`len` covers `StatementId::bytes()` only (circuit name, constraint-system digest, mode, row
`row/v4`). The public words (36 at the wallet statement) are the first item, observed before any
commitment or challenge; their number is fixed by the constraint system the identifier's digest
names.

*Hypotheses.* I.1 asks that the statement encoding be prefix-free with a polynomial-time left
inverse on its image. Read `pre'(x) = BE32(len) ‖ id ‖ words`: given the string, the decoder reads
`len`, then `id`, then the number of words `n(id)`, which is a function of `id` (a consensus table
of admitted constraint systems; an unknown `id` maps to 0 and is rejected by the verifier). Two
statements with different `id` differ inside the length-prefixed `id`; with the same `id` they have
the same length; so no encoding is a proper prefix of another. The bytes are those of section 2.1
with the length field not spanning the words. **Holds**, under the stated condition (the count is
a function of the identifier). Section 2.1's form would need the count when the transcript opens
(`SpbcsChallenger::new(.., head, n_tail)` takes it; callers pass 0).

**B-2. Index sampler.** An index into `[2^n]` is four stream bytes read little-endian and masked
to `n` bits; consecutive indices take consecutive 4-byte groups; a field element is its 32
serialised bytes; challenges read from byte 0 (the write-back overlaps the first challenge, as in
[SG26]). Every index has `2^(32 − n)` preimages (`n ≤ 31`, since `l_max = 2^31`): equal counts,
prefix reading, `eps_ov = 0`. A query message's stream is `4 q` bytes; the longest stream of a
wallet proof is 944 bytes at 232 queries, 1,504 at 368 queries of rate 1/2 (M, the builder's
vectors). **Holds**; H9's figure for B becomes 944 (1,504) bytes in place of 713, which lowers the
stream term.

**B-3. Repeated positions are not de-duplicated.** As built the proof carries one leaf and one
path **per query**, repeated positions included, natively and in circuit; each copy is checked
against the root. [SG26] Definition 2.18 makes `qry(theta)` a list without repetitions, and I.1
"Prover and verifier" says the verifier "requires exactly one salted leaf per position". **The
hypotheses do not hold as stated.** Two routes:

- *De-duplicate* (section 2.4 and T-3's second half): the theorem applies as is.
- *Lemma D (reduction; Original, the Ycash developers, 2026, unreviewed; `REFERENCES.md` O-66).*
  Let `V'` be the as-built verifier and `V` the de-duplicating one. (i) If every repeated position's
  copies are byte-equal (leaf and salt), dropping the copies maps an accepting proof for `V'` to an
  accepting proof for `V` on the same statement; the honest prover's `V'`-proof is a deterministic
  function of its `V`-proof, and so is the simulator's. So knowledge soundness transfers with no
  loss (the extractor of `V` is run on the de-duplicated proof), and zero knowledge (6.6 (3), (4))
  transfers with no loss (a repeated leaf is a copy of an opened one). `k_q` already counts every
  query with repetitions (`q_IOP` in section 4), so the constants are unchanged. (ii) If two copies
  of one position differ but both authenticate to the root, the adversary has output two distinct
  inputs of the leaf or node part with equal digests along the two paths: a collision of the
  random oracle. So `eps'(t) ≤ eps_ex(t) + Pr[a t-query adversary outputs a collision]`. The second
  term needs a QROM collision bound for a random function with 256-bit outputs, of order
  `t^3 / 2^256` (Zhandry's bound, **from memory, not in the folder**), which is of the order of
  the theorem's own hash term and below it at the tree's figures (the hash term has 11.6 bits of
  headroom over 64, section 5). **To be written and checked:** (ii) with the collision bound read
  from its paper. A simpler closure that removes (ii): the verifier refuses a proof in which two
  copies of one position differ (system A already does), natively and in circuit; in circuit this
  is a comparison per pair of equal positions, whose cost is for the builder to count.

  **Note (2026-11-19): Lemma D is written in `docs/lemma-d-duplicate-openings.md` (a draft until
  refereed; `REFERENCES.md` O-70).** Part (ii) as sketched above is superseded: unequal copies are a
  digest collision of the extractor's database, which the bad set of [SG26] Lemma I.12 already
  contains and `c'` already charges, so the multi-opening verifier keeps Theorem 6.6 (2) with the
  same constants and no added term (Theorem D there, Adapted from [SG26] Theorem I.16), at the `k_q`
  that counts drawn queries. It covers system A's flag walk and `open_stacked` and system B's
  in-circuit verifier; the Zhandry citation from memory is no longer used.

**B-4. BLAKE3 `derive_key` framing (the BLAKE3 build).** Exactly as built (B's §10.4; contexts 46
ASCII bytes each):

```
C_leaf = "Yugen 2026-11-19 spBCS system B Merkle leaf v1"
C_node = "Yugen 2026-11-19 spBCS system B Merkle node v1"
leaf  = derive_key(C_leaf, ser(values) ‖ salt)     no tag, no length; at most 1,024 bytes (one chunk)
        chaining value K_leaf; every block DERIVE_KEY_MATERIAL; first CHUNK_START; last CHUNK_END | ROOT; counter 0
node  = derive_key(C_node, left ‖ right)            one compression: h = K_node, t = 0, b = 64,
        flags CHUNK_START | CHUNK_END | ROOT | DERIVE_KEY_MATERIAL = 0x4b
K_node = 02e6ff37444ae8befc9ddc0505d3bd40a1b3d9924b45d148905602e214e51cc8
K_leaf = f8f115b975526ca1c5cf5a1196ff0987c98a2f9ac6debfc3c0afc5aa96faf3dc
```

`ser(values)` is each field element's little-endian bytes in order (32 at category 1), the salt's
elements following. No level or position. Challenge inputs stay SHA-256 with tag `0x20`, stream
points SHAKE256 with `0x23`. The SHA-256 build is unchanged (leaf `SHA-256(0x21 ‖ ser(values) ‖
salt)`, node one compression from `IV'`) and keeps MA-2.

*Hypotheses.* I.1 "The oracle's domain": four disjoint parts with injective encodings. The leaf
encoding `(r, v) ↦ ser(v) ‖ r` is injective (the salt has fixed length per tree); the node encoding
is the identity on 64 bytes; leaves and nodes are separated by the context key (different
functions), not by a tag; the challenge and stream parts are other functions. Separation by
function, not by input bytes, is exactly the content of MA-2':

**MA-2' (restated; replaces MA-2 for the BLAKE3 build; from `decision-b-merkle-hash.md` H-1.6).**
The node part of [SG26]'s oracle is modelled by `m ↦ BLAKE3.derive_key(C_node, m)` on 64-byte `m`
(one compression from `K_node` with the flags above), the leaf part by `m ↦
BLAKE3.derive_key(C_leaf, m)` on byte strings of at most 1,024 bytes, the challenge-input part by
`SHA-256` on inputs beginning `0x20`, and the stream part by `SHAKE256` on inputs beginning `0x23`;
the four are modelled as **independent random oracles**, which together form one random oracle on
the disjoint union of their domains, as I.1 requires. Unlike MA-2 it models only values of a mode
the BLAKE3 specification defines, never a bare compression call. Support: the designers'
indifferentiability statements in the ideal-cipher model ([B3] 4.2, 4.3) with the caveat of
`CITATION-AUDIT.md` C-30 (the 7-round keyed permutation has a full-round weak-key distinguisher on
unconstrained inputs, so the premise is restricted to the IV-constrained inputs the mode feeds it).
**Hypotheses hold under MA-2'**; MA-2' itself is for the referee (`decision-b-merkle-hash.md`
§7 item 5).

**Other differences recorded by system B, not hypotheses of Theorem 6.6 (2):** the salt on the
four fold trees of a leaf proof (route S) and its default length (256 bits) bear on zero
knowledge (`zk-quantum.md`), not soundness; at 256-bit salts the salt is the first half of the last
BLAKE3 block, at 512 bits the final block alone (`decision-b-merkle-hash.md` H-1.4).

## 3. Theorem 6.6 (2) and its hypotheses, per system

**Theorem 6.6 (2) [SG26], as stated.** Let IOP be a series–parallel IOP (Definition 2.18) for `R`
with `n_pos` oracle positions, round-by-round knowledge sound with errors at most `eps_k`
(Definition 2.20), and `(Prv, Vrf)` its spBCS transformation (Protocol 6.5) with digests of `b`
bytes and streams of `b + e` bytes. Then `(Prv, Vrf)` is adaptively knowledge sound (Definition
H.3) with oracle simulation error 0 and, in the QROM, extraction error at most

    eps_ex(t) = 2 sqrt( k_q / 2^(8(b+e)) ) + 6 (t + k_q)^2 ( eps_k + c' (t + k_q) / 2^(8b) ),
    c' = max(2, c) + n_J + 1,

and adaptive soundness error at most `eps_ex(t)`; in the ROM `(t + k_q)(eps_k + c'(t + k_q)/2^(8b))`
(Theorem I.16). Here `c = N_msg max(1, m)`, `k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2
max(1, l_max))))` (Definition I.1), `t` the adversary's hash queries, the statement chosen by the
adversary. The extractor is CMS19's database extractor, straight-line.

| # | Hypothesis (where in SG26) | System A | System B |
|---|---|---|---|
| H1 | Public-coin IOP with challenge-determined queries: `qry(theta)` a function of the challenges only, not of the statement (Defs. 2.16, 2.18) | met: positions are read from challenges (`sample_queries`); one IOP per parameter row and shape (stack, rate), which `pre(x)` fixes | met: positions from the query challenge; the fixed `GF(2^8)` zerocheck coordinates are constants, not messages (`yugen-proof-b2/docs/transcript-binding.md`) |
| H2 | Total order (a series–parallel order without merges): `n_B = n_J = 0` | met (one sequential transcript) | met |
| H3 | Round-by-round **knowledge** soundness with errors `eps_k` (Def. 2.20; for the total order equal to CMS19 Def. 8.5 by Lemma 2.21) | the opening: Theorem S0 (`whir-additive-soundness.md`, knowledge form stated there: the state is defined through unique decoding, Berlekamp–Welch extracts) and Theorem S of `zk-wi-soundness.md` (W-I); the rounds outside the opening (sumchecks, bus GKR, Keccak reduction) are counted by `OTHER_ROUNDS` with Schwartz–Zippel errors, their **knowledge** form not written: obligation **K-A** | the state functions of `binius-extension-challenges.md` are soundness state functions; their **knowledge** form (an extractor from the past at each challenge) is not written: obligation **K-B** (referee 4 (i)) |
| H4 | Samplers with equal preimage counts reading a prefix; `eps_ov` (Def. I.1, I.1 "Samplers") | met, `eps_ov = 0` (2.4) | met, `eps_ov = 0` |
| H5 | One random oracle with four disjoint parts and injective encodings (I.1 "The oracle's domain", "Hash functions") | met by the tags of 2.2, under modelling assumption **MA-1**: Keccak-256 and SHAKE256 (same permutation, different padding suffixes) as one oracle, as SG26 models SHA-384 and cSHAKE256 | SHA-256 build: met by the tags of 2.2 (B's leaves need the new tag), under MA-1 for SHA-256 with SHAKE256 and **MA-2**: the node part is the compression function from `IV'` (2.6). BLAKE3 build (as built since change 32): met under **MA-2'** (2.8, B-4), leaves and nodes separated by the `derive_key` context |
| H6 | Challenge inputs list the label, proof salt, statement and every item of the past, with the write-back (Protocol 6.5 step 1(b); I.1 "Challenge inputs") | **met as built** (amendment 2026-11-19; the duplex of Q-1 is the record) | **met as built** (amendment 2026-11-19; the chain of Q-2 is the record) |
| H7 | Merkle commitment of I.1: binary, leaf digest `dg(H(leaf(r, ser(O[q]))))`, node digest `dg(H(node(d, d')))`, compressed paths allowed; the verifier requires exactly one salted leaf per position of `qry(theta)` | binary, full paths: met as built (one leaf a distinct position on the wire; two different openings of one position refused; 2.8) | binary with a decommitted cap checked against the absorbed root: a form of path compression ("does not change the bounds", Section 6.2); **met as built since framing version 2** (positions de-duplicated in the proof, change 34; amendment 2026-11-19; B-3 is the record) |
| H8 | Non-oracle parts read in full and in the challenge inputs (Section 6.2; CY Rem. 25.1.2) | met (items) | met (items) |
| H9 | Digests of `b` bytes, streams of `b + e` bytes, the oracle's output taken at the longest stream, each use a prefix (Section 6.3, last paragraph) | `b = 32`, longest stream 1,154 bytes (a level-0 query round: 369 positions of 25 bits), plus the 32-byte offset and skipped lanes of 2.8 A-2 as built | `b = 32`, longest stream 713 bytes in the model; 944 bytes as built (four bytes an index, 2.8 B-2), 1,504 at 368 queries of rate 1/2 |
| H10 | Adversary class: Definition 6.1 (`t` hash queries; initial state independent of the oracle) | the model | the model |

Every hypothesis is met for both systems **after the transcript change**, except H3's knowledge
form outside the openings (K-A, K-B: written obligations, section 9) and the modelling assumptions
MA-1, MA-2 (MA-2' for B's BLAKE3 build), which are of the kind every random-oracle analysis makes and
which SG26 makes for its own implementation. With the counter-mode alternative, B adds Lemma X
(proved, 7.1). As built (2.8), every deviation keeps the hypotheses except B's repeated positions
(B-3), which need de-duplication or Lemma D.

## 4. The quantities for each system

From each system's message counts (SG26 Definition I.1; `../soundness`, revision 6, `spbcs.py`,
`revision6.a_counts`, `b_counts`; C, estimates (E) until the transcript modules report the counts,
task T-1):

| Quantity | System A | System B |
|---|---|---|
| Verifier messages `|J_V|` | 599: the 87 rounds of the zero-knowledge leaf's list (11 bus layers, 52 claims; the largest list over A's rows) plus `OTHER_ROUNDS` = 512 | 600: the row budget, 600 challenges a proof (`current.B_ROW_BUDGET`) |
| Prover messages `|J_P|` | 599 (one before each verifier message; upper figure) | 600 |
| Oracle strings a message `m` | 2 (upper figure) | 2 |
| `c = N_msg max(1, m)` | 2,396 | 2,400 |
| `c' = max(2, c) + n_J + 1` | **2,397** | **2,401** |
| Hash constant `6 c'` | 14,382 (`2^13.81`) | 14,406 (`2^13.81`) |
| `q_IOP` | 1,552 (the largest sum of query counts over A's rows) | 1,104 (184 queries in each of 6 trees) |
| `l_max` | `2^26` positions | `2^31` positions |
| `k_q` | **45,852** (`2^15.48`) | **38,832** (`2^15.24`) |

## 5. The loss and the QROM bits of the tree

Tree model (`soundness-method.md` 8.5b; O-13): the adversary attacks a tree of `N = 20,000` proofs;
the forgery probability is at most the sum of the `N` per-proof errors; the QROM bits are the
largest `kappa` at which `N * eps_ex(2^kappa)` is at most `1/2`, taken separately for the IOP term
`6 (t + k_q)^2 eps_k` and the hash term `6 c' (t + k_q)^3 / 2^256` (each with `N`), with `k_q`
added to `t` exactly; the stream term `2 sqrt(k_q / 2^(8(b+e)))` does not depend on `t`. `e` is the
effective bits of the weakest round of any proof of the tree (`eps_k = 2^-e`). Results (C, revision
6, `output/revision6-tables.txt`):

| System, form | Provenance | `e` | `C1` | `C2` | IOP term | Hash term | Stream term, tree | **QROM bits** | Margin over 64 |
|---|---|---|---|---|---|---|---|---|---|
| A, spBCS, SHAKE256 | Published | 152.96 | 6 | `6 c'` = 14,382 | 67.54 | 75.63 | `2^-4593` | **67.54** | **+3.54** |
| B, spBCS, SHAKE256 (default) | Published | 152.73 | 6 | 14,406 | 67.43 | 75.63 | `2^-2829` | **67.43** | **+3.43** |
| B, spBCS, counter mode (Lemma X) | Adapted | 152.73 | 24 | `8 x 6 c'` = 115,248 | 66.43 | 74.63 | `2^-2829` | **66.43** | **+2.43** |

The IOP term binds in every row; the hash term carries 11.6 bits of headroom over 64 even though
`c'` is about 2,400 (the referee's `c' = 2^5 .. 2^9` range bracketed it from below). The same holds
in the calculator's "every `t <= 2^kappa`" convention: at `t = 1` the IOP term is
`6 N k_q^2 2^-e = 2^-105` (A), far below `2^-65`. At the document's earlier reference figure
`e = 152.343` the IOP term is 67.24 for both forms with `C1 = 6` (66.24 with Lemma X).

## 6. Corrections, and the classical condition

### 6.1 The corrected table of revision 1 (record)

Revision 1's section 6 table had a wrong row (referee 1.8). Corrected, at `e = 152.343`:

| Constants | `kappa_IOP` | `kappa_hash` | QROM bits |
|---|---|---|---|
| CMS19's own, `C1 = 6`, `C2 = 24` | 67.24 | 78.71 | 67.24 |
| form C as stated, `C1 = 24`, `C2 = 240` (unproved, 7.3) | 66.24 | 77.60 | 66.24 |
| form X with `t' = t + a_V`, `a_V <= t` folded in: **`C1 = 24`, `C2 = 192`** (was "12, 96": wrong) | **66.24** | **77.71** | **66.24** |
| form C with `a_V <= t` folded in (`t' <= 3t`): `C1 = 54`, `C2 = 810` | 65.65 | 77.02 | 65.65 |

`(2t)^2 = 4 t^2` and `(2t)^3 = 8 t^3`: `6 x 4 = 24` and `24 x 8 = 192`. Revision 6 of the calculator
no longer folds `a_V` (or `k_q`) in; it adds `k_q` to `t` exactly.

### 6.2 Finding Q-5: condition C for the spBCS transcript

The calculator's classical condition C rests on the book's Theorems 25.2.1 and 31.2.1, `(t + k)
eps_rbr + 3.5 t^2 / 2^lambda` with `k` the rounds, which are stated for Construction 25.1.1, the
hash chain (S). The book's Remark 25.1.3 describes the variant that derives each challenge from the
whole past (spBCS's shape) and states only that it has "slightly smaller security bounds"; no
theorem is given for it (S). The published classical bound for spBCS is the ROM part of Theorem
6.6 (2): `(t + k_q)(eps_k + c' (t + k_q)/2^256)`. In the calculator's convention (`eps(t) <= t /
2^kappa` for every `t <= 2^kappa`, binding at `t = 1`) the verifier's `k_q` (`2^15.5`) replaces
`1 + k` (`2^9.2`):

| System | Need a round, every `t >= 1` | Need, `t >= k_q` | Certified need (book) | Weakest round | Margin, every `t` | Margin, `t >= k_q` |
|---|---|---|---|---|---|---|
| A | 158.77 | 144.29 | 152.52 | 152.96 | **-5.81** | +8.67 |
| B | 158.53 | 144.29 | 152.52 | 152.73 | **-5.80** | +8.45 |

(C, revision 6.) Finding (Original, the Ycash developers, 2026): the `k_q` at `t = 1` is a feature of
the proof technique (the extractor's database holds the verifier's Merkle queries), not of any
attack, but it is what the published bound says. Buildable fixes, for the lead architect:
(a) read condition C for adversaries making at least `k_q` hash queries (fewer than one
verification's worth of hashing is not a category-1 adversary): every row meets with 8.4 bits or
more and condition C stops binding (condition Q does, at 145.87); or (b) keep "every `t >= 1`" and
solve every row at 158.8 bits a round (calculator revision 7: about 9 more queries a level at rate
1/4, 15 at rate 1/2, 8 for B at rate 1/8; E). Until the decision, the certified rows are certified
under the book's convention as before, and this section records that the spBCS transcript's own
classical theorem needs (a) or (b). The QROM figures above hold in either convention.

**Decided (2026-11-19, the lead architect; `docs/decision-qrom-counting.md`): (b), every `t`.** The quantifier
was checked on the rendered pages of [SG26]: Definition H.3 (p. 128) "for every t and every (t, 0)-adversary",
Definition H.4 (p. 129) "for every t ∈ N"; nothing restricts `t >= k_q`. Calculator revision 9 solves every row at
its **own** `k_q` (not the worst proof's, as the table above does), to its fixed point: system B 184 -> 192,
168 -> 174, Johnson 107 -> 111 and 80 -> 82, node 1/4 225 -> 235 (the built 226 no longer meets) and 165 -> 171;
system A +4 to +15 queries a level (the "about 9 / 15 / 8" estimates above are superseded). Reading (a) is kept only
as the calculator's non-default option, labelled "non-default convention (t >= k_q), not certified". The referee's
Lemma M (`soundness-rev8-referee.md` 7), which would restore the (a) counts for every `t`, is recorded as future
work, unproved. Condition Q under revision 9 (section 5's table, recomputed with the category rows): A 69.58
(e = 157.03), B 70.45 (e = 158.78) against 64. *Amendment (2026-11-19, revision 10.2): these are tree figures, derived under the recursion heuristic C2 and conditional on K-A, K-B and T-1 (`lemma-tree-extraction.md` revision 2, Proposition TE-Q'), not proven QROM theorems; the one-table form gives 76.72 / 77.60, printed beside them; the project claims 69.58 / 70.45. `docs/what-is-proven.md`.*

## 7. Alternatives and the transcripts as built (record)

### 7.1 Observation 1, findings Q-1, Q-2, Lemma X

**Observation 1 (P; narrowed after referee 1.1).** In CMS19's construction every verifier message is
exactly `lambda` bits and the IOP's round-by-round error is measured over a uniform `lambda`-bit
message (Definition 8.4). An IOP round whose challenges need `L > lambda` bits fits only by (i) a
fixed expansion `G` inside the IOP, whose error `Pr_m[state(tr || G(m)) = 1]` no
information-theoretic argument bounds, or (ii) splitting the round into links with empty prover
messages, which loses round-by-round soundness: in the state-restoration game (S: CY Definition
23.2.1 draws `rho_i` afresh with salts, Definition 23.2.2 quantifies over every salt size; Theorem
31.2.1 gives `eps_sr <= (t + k) eps_rbr`) a prover restores to each link until its `Q/r` positions
fall in the agreement set, so `eps' >~ (1 - delta)^(Q/r) / r`: about `2^-10.2` for `r = 28` links of
A's 7,000-bit level (C). Hence **no transcript with 256-bit digests** keeps Theorem 8.6 verbatim for
these IOPs. (CMS19's construction with `lambda` set to the longest round's need, several thousand
bits, is Theorem 8.6 verbatim; it is excluded only because every digest would then be that long.)
spBCS avoids the question: its challenges are long streams and its theorem is stated for them.

**Finding Q-1 (A as built; S, `transcript.rs`).** A duplex sponge over Keccak-f[1600]; every
challenge takes a permutation of its own and is the first four lanes of its output; positions are
read from consecutive challenges. To bring it under a QROM theorem one would need (a) the duplex
idealised as a random oracle on the whole prefix, (b) each 256-bit challenge as a separate entry
(Lemma X), and (c) BCS16's chain, in which a challenge is not an input of the next query, with the
strong round-by-round soundness of CMS19 Section 8.6 and a proof CMS19 only sketches. spBCS removes
(c) by the write-back and (a), (b) up to standard modelling.

**Finding Q-2 (B as built; S, `hasher_challenger.rs`).** The chain keeps each challenge in the
chain, but expansion is iterated (`d_(i+1) = SHA-256(d_i)`); the entry that completes a challenge
vector is its last block, whose probability of making the vector bad is not bounded by `eps` (with
the other blocks good it is the last block's dozen positions, about `2^-6`). No reduction is known
for iterated expansion (U); counter mode has one (Lemma X).

**Lemma X (counter mode is a long-output oracle at a factor 2 in quantum queries) (P).** Let `H` be
a random oracle and `G(c) := (H(exp || c || 0), H(exp || c || 1), ..)`. Any quantum algorithm
making `t` queries to `H` is perfectly simulated by one making at most `2t` queries to the pair (`H`
restricted to inputs not beginning with `exp`, `G`). *Proof.* `G` and `H` on the `exp` domain are
the same random function, re-indexed. A query `|c, i, y> -> |c, i, y + H(exp, c, i)>` is computed
by computing `G(c)` into a fresh register (one `G` query), adding block `i` to `y`, and uncomputing
(a second query). Other queries pass through. ∎ (Referee 1.3: holds; the pair is one random oracle
with disjoint domain parts, which CMS19's compressed oracle and SG26's oracle both allow.) A
classical query costs one.

**Finding Q-4 (the classical construction).** CY Construction 25.1.1 is a hash chain `rho_i :=
f_i(rho_(i-1), rt_i, tau_i)`; spBCS is the "basic variant" of CY Remark 25.1.3 with the non-oracle
parts and write-backs added, for which the book gives no theorem (6.2). The classical guarantee of
the adopted transcript is therefore the ROM part of Theorem 6.6 (2), with finding Q-5.

### 7.2 Form X (recorded alternative for A)

Revision 1's form X: `rho_j = XOF("Yugen/fs/link" || j || rho_(j-1)[0 .. 256) || rt_j || msg_j)[0 ..
L_j)`, leaves and nodes labelled. Theorem Q (section 8) for it is a credible proof sketch with the
referee's three extra hypotheses: **(H1)** each challenge uniform in its space given a uniform
prefix (true for `GF(2^256)` elements and power-of-two positions; to be asserted per challenge
type); **(H2)** every IOP round begins with a prover message (a verifier-first round needs an
empty-message link); **(H3)** Keccak-256 and SHAKE256 modelled as one random oracle on disjoint
domains (SHAKE256's suffix bits keep the domains disjoint; idealising the sponge in the QROM is a
heuristic). What makes it a sketch: Lemmas 6.4, 6.5, 8.7, 8.8, Claims 8.9, 8.10 and Proposition
8.14 are asserted to hold with `S(D)` redefined, not re-derived. Not adopted: spBCS has a published
proof and the same `C1 = 6`.

### 7.3 Form C (unproved; not adopted)

Revision 1's form C chained from the link digest `c_j`, not from the challenge: `c_(j+1) =
SHA-256("Yugen/fs/link" || j+1 || c_j || rt_(j+1) || msg_(j+1))`, `rho_j[i] = SHA-256("Yugen/fs/exp"
|| c_j || i)`. **The constants `C1 = 24`, `C2 = 240` are unproved** (referee 1.5): the challenge
`G(c_j)` is not an input of the next link, so an adversary can build continuations on `c_j` before
`G(c_j)` is defined, the BCS16 chain of CMS19 Section 8.6 again; Lemma 8.13's case 2 does not apply.
The referee's fix, recorded: write the challenge back, `c_(j+1) = SHA-256("Yugen/fs/link" || j+1 ||
rho_j[0] || rt_(j+1) || msg_(j+1))`, with `rho_j[0]` the first expansion block; then 5.2 (b) to (d)
of the record go through. spBCS's write-back is the published form of the same idea.

## 8. Theorem Q (revision 1, record only)

Revision 1 adapted CMS19 Theorem 8.6 to form X (and C) as a list of changes to CMS19 Section 8.5.1:
(a) one oracle with several output lengths, digests as `lambda`-bit prefixes; (b) extraction through
link entries, leaves read as `(row, salt)`; (c) the property `P` and Lemma 8.13 with `S(D)` the
pointer components, `|S(D)| <= 2|D|`; (d) form C's extra `t/2^lambda`; (e) arity `a`: `C2 = 6(a +
2)`. Statement: `( sqrt(6 (t'^2 eps + 4 t'^3 / 2^lambda)) + sqrt(a_V / 2^lambda) )^2`, `t' = t +
a_V`. Status after the referee: a sketch for form X under H1 to H3 (7.2); unproved for form C (7.3).
The full text is in this file's history (commit `b3ec66f` and its successors before revision 2).
Nothing certified rests on it; `soundness/src/yugen_soundness/qrom.py` keeps its constants as a
record.

## 9. Tasks and acceptance

| # | Task | Acceptance |
|---|---|---|
| T-1 | **A's transcript module** (`transcript.rs`) replaced by spBCS as in 2.1 to 2.4 (Keccak-256 keys with the running state, SHAKE256 streams, tags `0x10` to `0x13`, the 64-byte proof salt, write-back, deduplicated positions); the guest's in-circuit verifier the same | a test vector that recomputes every key, stream and challenge of one proof with an independent Keccak implementation; a test that changing any byte of `s`, `pre(x)` or any item changes every later key; a test that the write-back is the stream's first 32 bytes; the module reports `N_msg`, `m`, `q_IOP`, `l_max` and a test asserts them within section 4's figures (else the calculator is re-run with them); the Keccak-f count per verified child reported (M) |
| T-2 | **B's transcript** (`HasherChallenger`) replaced by spBCS with SHAKE256 streams; B's leaf hash gets the tag `0x21`; tags `0x20`, `0x23` | the same tests with an independent SHA-256 and SHAKE256; a test that a leaf input beginning with the challenge-input tag cannot collide with a challenge input (different first byte); the node circuit's transcript gadget updated |
| T-3 | Proof formats carry `s` (64 bytes) and one leaf per distinct position | format tests; proof sizes recorded |
| T-4 | System B's stream: measure the node circuit's cost of SHAKE256 streams against counter-mode SHA-256 streams | the measured AND-row / cycle counts for both; the counter mode is adopted only if it is cheaper, and then the calculator's B row switches to `spbcs.FORMS[1]` (66.43 bits, condition Q still met) |
| T-5 | Obligations K-A, K-B: the knowledge form (an extractor from the past at each challenge, SG26 Definition 2.20) of every round outside the openings, A (sumcheck, bus GKR, Keccak reduction, gadget) and B (`binius-extension-challenges.md` state functions) | a section in `zk-system-a-gaps.md` (A) and in `binius-extension-challenges.md` (B) naming the extractor of each round and checking condition (b) of Definition 2.20 |
| T-6 | Finding Q-5: the lead architect chooses (a) or (b) of 6.2 | the choice recorded in `soundness-method.md` 8.5b; for (b), calculator revision 7 with every row re-solved. **Done 2026-11-19: (b); `soundness-method.md` 8.5b, 8.9; calculator revision 9 (every row re-solved; draft until refereed)** |
| T-7 | External review of this document's instantiation (sections 2 and 3) | signed review sheet item |
| T-8 | System B's repeated positions (2.8 B-3): de-duplicate, or refuse unequal copies of one position natively and in circuit; Lemma D (ii) written with a QROM collision bound read from its paper | a test that a proof with two different openings of one position is refused; or one leaf a distinct position on the wire; Lemma D's text checked by the referee |
| T-9 | Specification §3.3 and A.3 follow 2.8: A's stream point 112 bytes (or a prefix that no 104-byte input carries, if Q1's 8-byte tag is chosen); A's first challenge at byte 32 and the block form; B's `pre(x)`, index sampler and BLAKE3 framing; MA-2' | the spec's separation table lists every unframed SHAKE256 length; vectors of both builders recomputed from the spec's text |

*Revision note (2026-11-19, calculator revision 10).* The `k_q` report that T-1 (A) and T-2 (B) make is specified in `decision-qrom-counting.md` 7.6 (task T-1 for both builder teams: Definition I.1's quantities with `q_IOP` counting every checked record, padded slots included; the hash queries by kind; the derived `k_q` and `c`; a machine-readable line per shape). Until a row's `k_q` is reported, the calculator labels it certified only with the 0.1375-bit guard (7.5 there). The hash term of Theorem 6.6 (2) is now evaluated per row (7.2 there): 114.74 proven classical bits for a 20,000-proof tree, QROM 75.63.

*Amendment (2026-11-19, calculator revision 10.2, after `docs/tree-extraction-referee.md`; not a rewrite):* every TREE figure in this passage is conditional, not an unconditional theorem. It holds under the recursion heuristic C2 (the event "accepted in-circuit, rejected natively" does not occur; no random-oracle proof can remove it), the owed obligations K-A and K-B (round-by-round knowledge soundness) and T-1 (the transcripts' domain separation and fit to [SG26] Protocol 6.5). Under Theorem TE' (`docs/lemma-tree-extraction.md` revision 2) the classical hash level of the tree is **121.89 bits at category 1** (185.89 / 249.89 at categories 3 / 5), printed with the per-proof union (114.74 / 178.74 / 242.74) beside it as the comparison; the tree's QROM figures are derived under C2, never "proven QROM". Status of every claim: `docs/what-is-proven.md`.

## 10. Review sheet

| # | Statement | On paper | Computation | Open |
|---|---|---|---|---|
| 1 | spBCS instantiation for A and B (2.1 to 2.6) | yes | | T-1, T-2 test vectors |
| 2 | Hypotheses of Theorem 6.6 (2), per system (section 3) | yes | | K-A, K-B; MA-1, MA-2 are modelling |
| 3 | Quantities and QROM bits (sections 4, 5) | yes | `soundness/` revision 6 (170 tests) | measured counts (T-1) |
| 4 | Finding Q-5 | yes | revision 6 table; revision 9 (every `t`, per-row `k_q`) | decided (b), 2026-11-19; revision 9 to be refereed |
| 5 | Lemma X; the counter-mode alternative | yes | | |
| 6 | Observation 1, Q-1, Q-2, Q-4 | yes | | |
| 7 | Form X (sketch), form C (unproved), Theorem Q | record | `qrom/test_numbers.py` (corrected row) | not pursued |
| 8 | The builders' deviations (2.8): A-1 to A-3, B-1, B-2, B-4 keep the hypotheses; B-3 does not (Lemma D); MA-2' | yes | builders' vectors (`spbcs-a-v1.txt`; `spbcs-b-*.json` with `check_spbcs.py`) | T-8, T-9; MA-2' for the referee |
