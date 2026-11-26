# Decision record: the proof-internal Merkle hash of proof system B

Part of Yugen. Decision SQ-48 of the plan (lead agent, 2026-11-19; open to the lead
architect's review). Revision 2 (2026-11-19): obligation H-1 done against the specification
([B3], [B3-ID]: `../REFERENCES.md` 1.1e); sections 4 to 8 corrected, findings H-1.1 to H-1.9 in
section 9, the verdict in section 10, open questions and tasks in section 11. Revision 3
(2026-11-19): obligation H-1 continued against the four cryptanalysis papers the lead architect
supplied ([TMC], [B2], [EFK15], [GKNWW14]: `../REFERENCES.md` 1.1e-bis); findings H-1.10 to
H-1.17 and the margin table in section 9b; sections 5, 6, 7, 9 (H-1.3, H-1.8, H-1.9), 10 and 11
corrected where these papers contradict or refine them. Figure marks: (M) measured, (C) counted from the compiled circuit, (E) estimate.
Source of every figure: `yugen-proof-b2/docs/parameters.md` section 9 at `af0f56d`, unless stated.

## 1. The question

Proof system B (Binius64) commits to its oracles with Merkle trees. A node of the bundle tree
proves that it verified its children, so every Merkle path the verifier checks is hashed again
inside a circuit. Which hash should those trees use?

What the hash is NOT used for: the statement (note commitments, nullifiers, the anchor, the
bundle's list commitment) stays Keccak/SHAKE in both systems, and proof system A's trees stay
Keccak-256. This decision concerns system B's own trees only.

## 2. Why the question matters: where the cost is

In the leaf-verifier circuit at the pin's row, 3.12 M AND rows (C):

| Component | Share |
|---|---|
| Merkle path hashing | 58.8% |
| Leaf hashing | 24.9% |
| Cap layers and the terminal codeword | 9.5% |
| Transcript, wrapper checks, statement | 6.7% |

Hashing is about 92% of the circuit; all field arithmetic together is 23,389 products. The
target E2 (1,500 leaves merged in 60 seconds on eight 16-core hosts, 7,680 core-seconds for both
systems) leaves system B about 3,580 core-seconds once system A's 4,100 are counted.

## 3. Options considered

| Option | Cost in circuit | Effect on N = 1,500 at the certified row (184 queries) | Verdict |
|---|---|---|---|
| **SHA-256** (the pin's hash; FIPS 180-4) | 364 AND rows a compression (C) | 13,000 to 18,600 core-seconds (E) | Kept as a build; not the default |
| **BLAKE3** | 168 AND rows a compression (C); slot 1,378,147 AND rows fused (C); one slot 0.94 core-seconds against 3.00 (M, under load) | 6,700 to 9,500 core-seconds (E) | **Chosen** |
| **Keccak-256** (as in system A and the statement) | about 600 AND rows a Keccak-f (E), one permutation for a two-to-one node: more than SHA-256 | above the SHA-256 figure | Rejected: costlier, and it would put both proof systems on one hash |
| An arithmetization-oriented hash (Poseidon-type, binary-field variants) | far fewer rows | would meet E2 | Rejected: young designs with algebraic structure; the project's rule is that a proof's security rests only on a standard, conservatively analysed hash |
| Keep SHA-256 and cut elsewhere: shared path prefixes; fold arity; leaf rate at unique decoding | at most 5%; within 6%; -0.2% (C) | no material change | Not sufficient alone; the lower cap layer (+2% AND, half the BMUL rows) is adopted as a row field |
| Keep SHA-256 and lower the query count (list-decoding rows: 107, or 80 at rate 1/16) | Merkle rows 6.11 M to 3.77 M or 3.21 M (C) | still above the share with SHA-256 | The rows rest on a preprint (ePrint 2026/2056) and stay candidates (`binius-johnson-row.md`); not a substitute for this decision |
| Raise system B's share of the hosts | none | E2 restated | Not excluded: the measured category 1 figure will be stated as hosts needed; it complements the hash choice |

## 4. The decision

System B's Merkle trees use BLAKE3 at category 1, framed so that leaves and nodes are domain
separated by the mode's own key words and flags (section 9, H-1.7; proposal for the builder and
the referee). The SHA-256 build stays compiling and tested, so the choice is reversible by a row
field; the row's Merkle hash is part of the statement identifier, so proofs of the two builds
cannot be confused.

**As built (`yugen-proof-b2` at `af0f56d`, `vendor/binius64/crates/hash/src/blake3.rs`) the trees
are NOT framed**: a leaf is `blake3::hash(leaf bytes)` and a node is `blake3::hash(left || right)`,
both in the plain `hash` mode with the same flags. Revision 1 of this record said "a framed hash
with domain separation between leaves and nodes"; that described the intent, not the build
(finding H-1.6).

## 5. Why

1. It is the only single change found that moves the certified, unique-decoding row by a factor
   of about two; every other reduction measured or counted is under 6%.
2. Hash diversity. With BLAKE3 in system B and Keccak in system A, the two proof systems of a
   transfer rest on different hash families: an ARX compression function (additions modulo
   `2^32`, rotations, XOR; [B3] Section 2.2) derived from BLAKE2s, and a sponge permutation. A
   structural weakness in one family does not reach both systems. With SHA-256 this was also
   true; with Keccak in both it would not be. (Revision 1 placed BLAKE3 in "the ChaCha/BLAKE
   line"; revision 2 dropped it as unsourced. Revision 3: it is sourced. BLAKE and BLAKE2 "rely
   on a similar core permutation originally used in Bernstein's ChaCha stream cipher" ([B2]
   Section 4.1), and [TMC] Section 4.5 says the same. So the hash diversity holds against the
   Keccak sponge, but BLAKE3 shares its round structure with ChaCha and with BLAKE2.)
3. It keeps the rule that proof security rests on a general-purpose hash, not on an
   arithmetization-oriented one.

## 6. What is given up, stated plainly

1. **A lower claimed level and a thinner margin.** SHA-256 is a NIST standard (FIPS 180-4) with
   over two decades of public cryptanalysis. BLAKE3 is not a NIST standard. Its designers claim
   **128 bits for every security goal**: "128-bit security against (second-)preimage, collision,
   or differentiability attacks" ([B3] Section 4.1); "BLAKE3 with an output of at least 32 bytes
   targets a security level of at least 128 bits for all its security goals" ([B3-ID] Section 7).
   For collisions this is the generic level of a 256-bit output, the same as SHA-256's; for
   preimages and second preimages it is **half** the generic 256 bits (SHA-256's stated preimage
   strength is 256 bits in NIST SP 800-107 Revision 1, cited from memory). Neither BLAKE3 document
   says anything about quantum attackers. The compression function keeps BLAKE2s's round
   function, IV and `G`, with **7 rounds instead of BLAKE2s's 10** ([B3] Section 1 and 2.2; "must
   do exactly 7 rounds", [B3-ID] 3.3), a single repeated message permutation in place of 10
   ([B3] 7.4), the `b` and `d` inputs in place of BLAKE2's `f0`, `f1`, and a 16-word output with
   the feed-forward on the second half only ([B3] 4.2, 7.3). The designers base 7 rounds on the
   cryptanalysis of BLAKE and BLAKE2, their own trail search and Aumasson's *Too much crypto*
   ([B3] 4.4, Tables 4 and 5); none of the cited attacks is on BLAKE3 itself. Four of the cited
   papers were read in revision 3 ([TMC], [B2], [EFK15], [GKNWW14]; section 9b); none analyses
   BLAKE3. How thin the margin is depends on the attack model (margin table, H-1.11). On BLAKE2s's
   **keyed permutation**, with the whole state chosen, results reach 7.5 rounds (boomerang,
   `2^184`, Hao, reported by [TMC] 3.2; not read), and a weak-key distinguisher reaches all
   rounds ([GKNWW14] 3, 7). On its **compression function with the specified IV**, a boomerang
   reaches 5 rounds (conditional estimate, [GKNWW14] 2). On the **hash function**, results on the
   BLAKE2 family reach 3.5 rounds (BLAKE2b, [GKNWW14] 6) and 2.75 rounds for preimages
   (BLAKE2b, [EFK15] 5.3). The 6.75-round pseudo-preimage on BLAKE2s ([EFK15] 5.2, `2^253.8`)
   lets the attacker choose the whole initial state; for BLAKE3's truncated output that model is
   trivial at any round count (H-1.13). With the specified IV, no result in the papers read is
   below the 128-bit claim on BLAKE2s. With a chosen IV, the full 10-round compression function
   of BLAKE2s has collisions in `2^64` ([GKNWW14] 3, Table 1; H-1.11).
   **Obligation H-1** (reading and recording) is done for [B3], [B3-ID] and these four papers.
   What remains is the external cryptographer's judgement of the margin, the papers still unread
   (H-1.16) and a search for analysis published after them (section 11).
2. **Native speed.** SHA-256 has hardware instructions on current phones and servers; a wallet
   proof built with BLAKE3 costs 1.02 to 1.03 core-seconds against the SHA-256 figure (M, under
   load). The bundler's saving in circuit is far larger than this loss.
3. **The security model.** The compilation theorem (Sharp-Grubbs, ePrint 2026/2615, Theorem 6.6)
   treats the hash as a random oracle. Modelling assumption MA-2 of `qrom-compilation.md` was
   written for SHA-256's compression function from a fixed initial value `IV'`, which is not a
   value of SHA-256 as specified. With the framing of H-1.7 every leaf and node digest is a value
   of BLAKE3's defined `derive_key` mode, and MA-2 is replaced by **MA-2'** (H-1.6): the node
   part is BLAKE3 `derive_key` with a fixed context on 64-byte inputs, one truncated compression,
   which the designers state is indifferentiable from a random oracle in the ideal-cipher model
   ([B3] 4.2, citing Luykx, Mennink, Neves) inside a mode they prove sound by Daemen, Mennink,
   Van Assche's Theorem 1 ([B3] 4.3). The ideal-cipher premise is a heuristic. 7- and 7.5-round
   keyed permutations of BLAKE-256 and BLAKE2s have published distinguishers ([B3] Table 4). The
   BLAKE2 keyed permutation, with no constraint on its input state, has a full-round
   distinguisher for a class of weak keys from one chosen plaintext ([GKNWW14] 3, 7 item 1).
   That distinguisher carries over to BLAKE3's 7-round permutation (H-1.14), so the premise can
   hold only on the IV-constrained inputs the mode feeds it.
   **Obligation H-2:** the framing built, MA-2' written into `qrom-compilation.md` 2.2, 2.6 and
   3, then the referee.
4. **Digest and quantum accounting.** The calculator's numbers do not change: 256-bit digests,
   and the hash term depends only on the digest length and the query counts (H-1.2, H-1.3). What
   changes is what stands behind the model: the designers vouch for 128 bits classically and for
   nothing against a quantum attacker, so the QROM hash term (75.63 bits for B) rests on the
   random-oracle heuristic for a 256-bit output with no designer claim above 128 bits (H-1.3).
5. **No category 3 path with BLAKE3.** The claim does not rise with the output length, and
   chaining values are 256 bits, so BLAKE3 cannot serve the 384-bit digests of category 3
   (H-1.5). This was also true of SHA-256; the category 3 row needs a third hash.

## 7. What would reverse the decision

1. A published attack below `2^128` for collisions, preimages or second preimages on 7 rounds of
   BLAKE3's compression function **with the specified IV words in row 3**. Also a distinguisher
   on the 7-round keyed permutation **restricted to inputs of the form the mode feeds it**
   (row 3 = `IV0..IV3`, row 4 = `t, b, d` with defined flag values) that invalidates the
   ideal-cipher premise of MA-2' at the query counts used (`2^128` classical, `2^64` quantum).
   (Revision 3: a distinguisher on the unconstrained permutation does not count here. One
   already exists at every round count, H-1.14, so that condition would be met trivially.)
2. Any published quantum attack on BLAKE3 or reduced-round BLAKE2s below the generic figures
   (`2^85` collisions, `2^128` preimages for a 256-bit output).
3. The external cryptographer's judgement that a 128-bit preimage claim, or the round margin of
   H-1.8, is inadequate for a consensus system whose proofs every node accepts.
4. A list-decoding row surviving review together with enough hosts that SHA-256 fits E2.
5. The referee rejecting MA-2' or the framing of H-1.7 without a fix inside BLAKE3's defined
   modes.

In each case the row field selects SHA-256 (364 AND rows a compression, the fallback already
built and tested) and the certified figure is restated: 13,000 to 18,600 core-seconds at 184
queries (E) against 6,700 to 9,500 with BLAKE3, so at the certified row system B then needs about
3.6 to 5.2 times its 3,580-second share of E2 (1.9 to 2.7 with BLAKE3), and more hosts.

## 8. Provenance

The choice among published hash functions, the framing proposal (H-1.7, Adapted) and findings
H-1.2 to H-1.6 and H-1.9 are the Ycash developers' (2026). SHA-256: FIPS 180-4. BLAKE3: [B3] =
J. O'Connor, J.-P. Aumasson, S. Neves, Z. Wilcox-O'Hearn, *BLAKE3: one function, fast
everywhere*, version 20211102173700; [B3-ID] = J-P. Aumasson (Ed.), S. Neves, J. O'Connor,
Z. Wilcox, *The BLAKE3 Hashing Framework*, Internet-Draft `draft-aumasson-blake3-00`, 20 July
2024 (work in progress; expired 21 January 2025 by its own date). Both read in full from their
text layers (`../REFERENCES.md` 1.1e); every section number below is theirs. Published, as
taken: the security claims, the round count and the changes from BLAKE2s, the modes, flags and
tree (H-1.1, H-1.7's mechanism), the indifferentiability statements ([B3] 4.2, 4.3) and the
cryptanalysis table ([B3] Table 4, H-1.8). Revision 3 read four of the papers [B3] cites
(`../REFERENCES.md` 1.1e-bis): [TMC] = J.-P. Aumasson, *Too Much Crypto*, version
20260706145800 (ePrint 2019/1492); [B2] = J.-P. Aumasson, S. Neves, Z. Wilcox-O'Hearn,
C. Winnerlein, *BLAKE2: simpler, smaller, fast as MD5* (ePrint 2013/322; ACNS 2013 per [B3]);
[EFK15] = T. Espitau, P.-A. Fouque, P. Karpman, *Higher-Order Differential Meet-in-The-Middle
Preimage Attacks on SHA-1 and BLAKE* (ePrint 2015/515, full version of CRYPTO 2015);
[GKNWW14] = J. Guo, P. Karpman, I. Nikolić, L. Wang, S. Wu, *Analysis of BLAKE2* (ePrint
2013/467, full version; shorter version CT-RSA 2014, LNCS 8366). Their results in section 9b are
Published and cited by section and table. The model mapping (H-1.11), the transfer analysis
(H-1.13, H-1.14) and the verdict (H-1.16) are the Ycash developers' (2026), labelled there.
The other cited papers are still unread.

## 9. Findings from the specification (obligation H-1; 2026-11-19)

Each finding: what it affects, and the work that closes it. Figures: (C) counted, (E) estimate.

### H-1.1 The designers' claims (Published; record)

128 bits for collision, preimage, second preimage and differentiability, for every mode and
every output of at least 32 bytes ([B3] 1, 4.1; [B3-ID] 7); the keyed and derive-key modes carry
the same level, the 256-bit key being "an extra defense layer" ([B3] 4.1); the XOF does not raise
it and does not separate output lengths ([B3] 2.6); the hash mode is offered "to instantiate
random oracles in cryptographic protocols" ([B3-ID] 1.1); no quantum statement in either
document. **Affects:** section 6 of this record (corrected above). **Closed** by this revision.

### H-1.2 Classical category 1: the claim equals the level category 1 already rests on (no number changes)

Where the analysis uses the hash classically: the Merkle commitment's binding and extraction and
the transcript are random-oracle statements whose hash term is `3.5 t^2 / 2^256` (book Theorem
25.2.1; `soundness-method.md` 8.2, 8.5b) or, for spBCS, `c' (t + k_q)^2 / 2^256` (Sharp-Grubbs
Theorem I.16); both count collisions and inversions of a 256-bit random oracle together. At
`lambda = 256` the proven classical level is already 126.6 bits, below 128 (`design-basis.md`
finding S-2; *revision note 2026-11-19, calculator revision 10: 114.74 bits under the spBCS term summed over the tree,
`decision-qrom-counting.md` 7.2*) *(Amendment 2026-11-19, revision 10.2: that tree figure is conditional on C2, K-A, K-B and T-1; under Theorem TE' the tree's classical hash level is 121.89; `docs/what-is-proven.md`.)*, and category 1 rests on condition H's attack rule: a generic collision costs
`2^128` calls, NIST's category 2 benchmark, ranked above category 1 (`soundness-method.md` 8.1,
8.2). BLAKE3's claimed collision level is exactly that `2^128`, and a preimage claimed at `2^128`
costs no less than the collision the analysis already concedes, so the 128-bit preimage claim
does not lower the classical level the documents state. The designers' mode bound adds a term
`q / 2^128` ([B3] 4.3, (2)), the same order as the conceded collision term. The calculator's hash
term (digest length and query counts only) is therefore justified classically **at the claimed
level and in the ideal-cipher model**, as it was for SHA-256 under MA-2. NIST category 1 is
defined against AES-128 key search (`soundness-method.md` 8.1): a claim of `2^128` BLAKE3
evaluations meets it if one BLAKE3 compression costs at least one AES-128 evaluation, which is
assumed here as it is for Keccak in 8.2 (not established). **Affects:** nothing in `soundness/`.
**Closes with:** the referee confirming this paragraph (review sheet item for H-2).

### H-1.3 Quantum: the QROM hash term rests on a heuristic the designers do not claim

The QROM hash term `6 c' (t + k_q)^3 / 2^256` (75.63 bits for B, `qrom-compilation.md` 5) and
condition Q model the hash as a quantum-accessible random oracle with 256-bit outputs; the
generic quantum attacks on such an oracle cost about `2^85` (collisions, BHT) and `2^128`
(preimages, Grover), figures from memory (`soundness-method.md` 8.2). The designers claim 128
classical bits and nothing quantum. The heuristic is of the same kind as for SHA-256 (whose
designers also make no quantum claim; NIST's categories 2 and 4 use hash collisions as
benchmarks), but the gap is larger: a dedicated classical preimage attack near `2^128` that
admits a quadratic quantum speed-up would reach the `2^64` target, and BLAKE3's claim does not
exclude one, while SHA-256's 256-bit preimage strength would. No such attack is known in the
documents read. Revision 3 corrects the attribution and the model. The 2.5-round `2^241`
preimage is on the BLAKE-256 **hash function** (Li and Xu, reported by [GKNWW14] Table 1 and
[B2] 4.1; [B3] Table 4 lists it under "c.f."). The papers read give no preimage attack on the
BLAKE2s hash function; for BLAKE2b the hash preimage reaches 2.75 rounds at `2^511` ([EFK15]
Table 7). The 6.75-round `2^253.8` result on BLAKE2s is a pseudo-preimage in which the whole
initial state is free ([EFK15] 5.1 "Terminology", 5.2), and that model is trivial for BLAKE3
(H-1.13). [TMC] 5.2 discusses quantum attacks; on why it does not settle Q-H1, see H-1.17.
**Affects:** the meaning
of B's 67.43 QROM bits (the hash term binds nowhere, 75.63 against the IOP term's 67.43, so no
number changes) and the wording of condition Q for B. **Closes with:** question Q-H1 to the
external cryptographer (section 11); the generic quantum figures sourced (BHT, Grover: to obtain,
`../REFERENCES.md` 1.3).

### H-1.4 Zero knowledge: unchanged as a model statement; the salt goes in its own final block

The leaf hiding of Sharp-Grubbs Theorem 6.6 (3) (`zk-quantum.md` 3) is a QROM statement with
64-byte leaf salts; its Grover figure for salts (`zk-quantum.md` 2.2) is a random-oracle figure
far above any designer claim (`2^256` against 128), as it was for SHA-256: neither function's
designers claim hiding. Nothing BLAKE3-specific changes, with one framing rule: BLAKE3 chains 256
bits between 64-byte blocks ([B3] 2.4), so the 64-byte salt should fill the leaf's **last block
by itself** (the serialized values padded to a whole number of blocks; injective because lengths
are fixed by the row's schedule). The salt's 512 bits then enter one compression together with
the chaining value of the values, never split across a 256-bit chaining value. **Affects:** leaf
encoding (H-1.7). **Closes with:** the builder's test that the salt occupies the final block of
every salted leaf.

### H-1.5 Category 3: BLAKE3 is not admissible; the category 3 row needs a 384-bit hash

Category 3 needs `lambda >= 384` by the attack rule (NIST's category 4 benchmark, collision on a
384-bit hash) and the QROM cap `(lambda - 1 - log2 24)/3 >= 98` (`soundness-method.md` 8.3).
BLAKE3 claims 128 bits whatever the output length ([B3] 4.1; [B3-ID] 7), and structurally every
chaining value is 256 bits ([B3] 2.4, 2.5): a node of two 48-byte children is 96 bytes, two
blocks, so a collision of the 256-bit chaining value after the first block (generic `2^128`)
collides the node whatever the output length. **BLAKE3 with extended output is excluded as a
category 3 digest.** SHA-256 is excluded for the same reason (256-bit output). Constraint on this
decision: **BLAKE3 is a category 1 choice; the category 3 row's Merkle hash for system B is
SHA-384** (FIPS 180-4; a 96-byte node fits one 128-byte block with its padding, one compression
a node; padding rule cited from memory), with **SHA3-384** as the alternative (one Keccak-f a
node at rate 104 bytes, about 600 AND rows (E); it would put both systems on Keccak at category
3). The "parameter-only path to category 3" of `design-basis.md` 1 holds for system B only as a
row-field change that also names a third Merkle hash. **Affects:** `design-basis.md` 1 and 2a
(the category 3 row), the statement identifier. **Closes with:** (a) a SHA-512-family gadget in
the Binius64 circuit, its AND rows a compression counted (C) and checked against FIPS 180-4
vectors; (b) a category 3 row with `merkle_hash = Sha384` in the identifier; (c) a test that a
category 3 row naming BLAKE3 or SHA-256 is refused; (d) `design-basis.md` 1 amended by the lead
agent (not in this task's write set).

### H-1.6 As built, leaves and nodes are not separated; MA-2 is replaced by MA-2'

As built both are plain `blake3::hash` with flags `CHUNK_START | CHUNK_END | ROOT` for any
input of at most 64 bytes ([B3] 2.4). A leaf whose encoding is 64 bytes (the salted round-oracle
leaves at the pin's row are 64 bytes, `yugen-proof-b2/docs/parameters.md` 9.2 (a)) is then the
same oracle input as a node, so hypothesis H5 of `qrom-compilation.md` 3 (one oracle, disjoint
parts) fails for those trees; for leaves of other lengths the parts are disjoint only by length,
which a future row can break. BLAKE3's flags separate chunks from parent nodes **inside one
BLAKE3 evaluation** ([B3] 7.7); two separate evaluations of 64-byte inputs are separated only by
key words or mode flag. The SHA-256 build did not have this defect (its node is a compression
from `IV'`, its leaf a padded hash). **MA-2'** (proposed, for the referee): the node part of
Sharp-Grubbs's oracle is modelled by `m -> derive_key(C_node, m)` on 64-byte `m`, the leaf part by
`derive_key(C_leaf, .)`, both values of BLAKE3's defined mode ([B3] 2.3), and the challenge and
stream parts by SHA-256 and SHAKE256 on their tagged inputs (`qrom-compilation.md` 2.2). Modelled
as independent random oracles, functions on disjoint parts form one random oracle on the union,
so no cross-family assumption beyond independence is needed (elementary; for the referee). The
ideal-model support is [B3] 4.2 and 4.3, with the caveat of section 6.3. Unlike MA-2, MA-2' does
not model a bare compression call. **Affects:** `qrom-compilation.md` 2.2 (the B column's leaf
and node rows), 2.6, 3 (H5); T-2. **Closes with:** H-1.7 built and the tests listed there; MA-2'
written into `qrom-compilation.md` by the lead agent; the referee.

### H-1.7 Proposed framing for system B's trees (proposal for the builder and the referee; Adapted)

Adapted from BLAKE3's `derive_key` mode ([B3] 2.3, 6.2) and the designers' own use of a keyed
hash for domain-separated hashing ([B3] 6.3, stateful hash object: `init(label)` keys the hasher
with `hash(label)`); change: the context names a Merkle part instead of a key-derivation purpose,
and the key material is public.

- Two hardcoded contexts in the format of [B3] 6.2 ("[application] [commit timestamp]
  [purpose]"): `C_leaf = "Yugen 2026-11-19 spBCS system B Merkle leaf v1"` and
  `C_node = "Yugen 2026-11-19 spBCS system B Merkle node v1"`. Their context keys `K_leaf`,
  `K_node` (stage 1 of `derive_key`, flag `DERIVE_KEY_CONTEXT`) are computed once and are
  constants of the verifier and of the circuit.
- **Leaf:** `derive_key(C_leaf, ser(values) || r)`: key words `K_leaf`, flag
  `DERIVE_KEY_MATERIAL` on every compression, 32-byte output; `ser(values)` padded with zeros to
  a whole number of 64-byte blocks so that the 64-byte salt `r` is the final block alone (H-1.4).
  The part tag `0x21` of `qrom-compilation.md` 2.2 is not needed (the context separates) and is
  dropped: at 128 bytes a tag byte would cost a third compression.
- **Node:** `derive_key(C_node, left || right)`: **one compression** with `h = K_node`,
  `m = left || right`, `t = 0`, `b = 64`,
  `d = CHUNK_START | CHUNK_END | ROOT | DERIVE_KEY_MATERIAL` (`0x4b`).
- **Levels and positions:** none. Sharp-Grubbs's node digest `dg(H(node(d, d')))` (Section I.1,
  `qrom-compilation.md` 3, H7) has none, and the fixed schedule fixes every tree's shape. A
  per-tree or per-level context would cost no rows (a constant chaining value) if the referee asks
  for multi-target separation; it is not required by the theorem.
- **Transcript:** unchanged, SHA-256 challenge inputs and SHAKE256 streams with tags `0x20`,
  `0x23` (`qrom-compilation.md` 2.2). BLAKE3 is not proposed for B's transcript.
- **Compressions** ([B3] 2.4, 2.5; C, and checked with a minimal implementation, `../REFERENCES.md`
  1.1e): a 64-byte node, 1 (the builder's 168 AND rows; consistent with the specification's 7
  rounds x 8 `G` x 6 additions = 336 32-bit additions a compression, two compressions packed per
  64-bit row, which is the builder's "336 a pair"); a zero-knowledge round-oracle leaf of 64 bytes
  of symbols with a 64-byte salt (128 bytes), 2 (3 with a tag byte); the pin's 64-byte salted
  leaf, 1; fold cosets of 128 and 256 bytes, 2 and 4; the same salted by route S (192, 320 bytes),
  3 and 5. Every leaf of system B is at most 1,024 bytes, so one chunk and no parent compression.
  The context keys cost no rows (constants) and one compression each natively, once.
- **Inside the specification's defined modes:** all of the above, and the as-built plain `hash`
  (which is defined but gives no separation). **Bare or non-standard uses, excluded:** a single
  `PARENT | ROOT` compression of two arbitrary digests (BLAKE3's internal parent node, defined
  only as part of one BLAKE3 tree); a counter `t` carrying a level or position; flag values other
  than those of [B3] Table 3 in their defined places; altered IV constants ([B3] 7.8: a different
  function); an output longer than 32 bytes read as a stronger digest (H-1.5).
- **Gadget:** `binius_circuits::blake3` already takes a constant key (it pairs the key with
  `KEYED_HASH`, `mod.rs` l. 72 to 106); the builder adds the `DERIVE_KEY_MATERIAL` flag in place
  of `KEYED_HASH`. If that change is refused, `keyed_hash(K_part, .)` with `K_part = hash(label)`
  ([B3] 6.3) is the fallback with the same counts and the gadget as it is.
- **Acceptance** (the builder's tasks): (i) native leaf and node digests equal the `blake3`
  crate's `derive_key` (or `Hasher::new_derive_key`) on the same context and input, by test; (ii)
  a 64-byte leaf encoding and a node on the same 64 bytes give different digests, by test; (iii)
  in-circuit digests equal native ones, and the AND rows a node stay 168 (C); (iv) the salt is the
  final block of every salted leaf; (v) the statement identifier names the framing version (a
  new `row/v4`), and the identifier-binding test covers it.

### H-1.8 The margin at 7 rounds (Published results; revision 2 from [B3] only, checked against four papers in revision 3, H-1.11, H-1.12)

From [B3] Table 4: on BLAKE2s, the keyed permutation is distinguished at 7.5 rounds (boomerang,
`2^184`) and the compression function at 5 rounds (boomerang, about `2^86`), with
pseudo-preimages at 6.75 rounds (about `2^253.8`); on BLAKE-256 (a related design with constants
in `G`), the 7-round keyed permutation is distinguished at `2^44` and its compression function
at 7 rounds at `2^242`. BLAKE3's 7 rounds are therefore within a fraction of a round of the
furthest published results on its predecessors' components. In complexity, revision 2 said only
the BLAKE-256 keyed-permutation boomerang is below `2^128`. **Corrected in revision 3:**
[GKNWW14] adds a 10-round (full) chosen-IV collision on BLAKE2s's compression function in `2^64`
(Table 1, 3) and a full-round weak-key distinguisher on its keyed permutation (3, 7). Li and
Xu's 2.5-round collision on the BLAKE-256 hash function costs `2^112` (reported by [GKNWW14]
Table 1; not read; missing from [B3] Table 4). None of the three applies to BLAKE3 as used here
(H-1.11, H-1.14). The designers argue that the boomerang attacks do not apply, given the IV
constraint on BLAKE3's inputs and the 128-bit target ([B3] 4.4). No cited paper analyses BLAKE3.
For a consensus system, where a hash break lets a forged proof through every node, this is the
weakest point of the decision. Reading the specification does not settle it, and neither do the
four papers read in revision 3 (H-1.16). **Closes with:** the remaining papers of
`../REFERENCES.md` 1.1e-bis obtained and read (rounds, attack type, complexity confirmed on the
typeset pages); a search for cryptanalysis of BLAKE2s and BLAKE3 published after 2015;
question Q-H2 to the external cryptographer.

### H-1.9 Corrections to revision 1 of this record, and to the Internet-Draft

Revision 1 said: "its compression function is that of BLAKE2s with the round count reduced from
10 to 7". **Verified with a correction:** the round count is right ([B3] 1, 2.2, 4.4); the
compression function is not BLAKE2s's with fewer rounds only: the message schedule, the inputs
`b`, `d`, the counter's place and the finalisation also changed ([B3] 4.2, 7.3, 7.4), and its
full output is no longer indifferentiable ([B3] 4.2). "Its designers argue the margin from the
cryptanalysis of BLAKE and BLAKE2": verified ([B3] 4.4), with their own trail search and [3] as
the other two grounds. "A framed hash with domain separation between leaves and nodes": not true
of the build (H-1.6). "The ChaCha/BLAKE line": unsourced in revision 2, dropped; sourced in
revision 3 ([B2] 4.1, [TMC] 4.5) and restored with its consequence (section 5). "Digest and
quantum accounting are unchanged": the numbers are; what supports them is not (H-1.3). The
Internet-Draft has four errors against the paper (`../REFERENCES.md` 1.1e, D-1 to D-4: 16-byte
blocks; `m[15], m[15]` in the last `G`; Appendix B.2 labelled keyed but computed unkeyed; block
length "at least 1"): the build follows [B3] and the `blake3` crate, never the draft's
pseudocode. Also for the lead agent: `yugen-proof-b2/docs/parameters.md` 9.3 (d) still says the
specification is "not in the reference directory" and dates it 2020; the version in hand is
20211102173700.

## 9b. The four cryptanalysis papers (obligation H-1 continued; revision 3, 2026-11-19)

How they were read: `../REFERENCES.md` 1.1e-bis. Text layers, extracted to a temporary directory
outside every repository. Superscripts are flattened in the text layer; [EFK15] prints its
complexities as base-2 logarithms, so its figures are unambiguous. Other exponents are read where
the context fixes them (for example "2^64 for BLAKE2s" from `2^(2w)` with `w = 32`,
[GKNWW14] 3). Each result below is **Published** and cited by section or table. A result one
paper reports from another, unread, paper is marked "reported by".

### H-1.10 What was read, and how independent it is (record)

| Key | Paper (from its own first page) | Read | Independence from BLAKE3's designers |
|---|---|---|---|
| [TMC] | J.-P. Aumasson, *Too Much Crypto*, "Version 20260706145800" | in full (19 pages) | none: the author is a BLAKE3 co-designer. The version read is later than the "Real World Crypto 2020" version [B3] cites. Its addendum of 6 July 2026 calls BLAKE3 "the strongest validation" of its proposal (p. 15) |
| [B2] | J.-P. Aumasson, S. Neves, Z. Wilcox-O'Hearn, C. Winnerlein, *BLAKE2: simpler, smaller, fast as MD5* | in full (16 pages) | none: three of its four authors are BLAKE3 authors |
| [EFK15] | T. Espitau, P.-A. Fouque, P. Karpman, *Higher-Order Differential Meet-in-The-Middle Preimage Attacks on SHA-1 and BLAKE*, full version of the CRYPTO 2015 paper | Sections 1, 2, 3 and 5 in full; Section 4 (SHA-1) for its tables only | third party |
| [GKNWW14] | J. Guo, P. Karpman, I. Nikolić, L. Wang, S. Wu, *Analysis of BLAKE2*, full version ("A shorter version appeared in ... CT-RSA 2014, LNCS 8366, pp. 402–423") | in full, with Appendices A to E (19 pages) | third party |

Of the four, only [EFK15] and [GKNWW14] are independent cryptanalysis. [TMC] and [B2] give the
designers' own reasoning.

### H-1.11 The margin table (Published results; the model mapping is Original as far as checked)

**Models**, as the papers define them. **H** is the hash function: the initial state is fixed and
the attacker chooses the message only ([GKNWW14] 2, "Our Attack Frameworks"). **CF** is the
compression function: the chaining value and counter are free, the IV words are fixed (in
BLAKE2: `v8..v11`, `v14`, `v15`; same place). **FS** is the free state: all 16 words of the
initial state are free and the finalisation is respected. [EFK15] 5.1 ("Terminology") calls
attacks in this model "pseudo-preimage". **CIV** is the chosen-IV model: the IV constants are
chosen ([GKNWW14] 2). **KP** is the keyed permutation as a block cipher: the plaintext (the
state) is chosen and the key (the message) is unknown, possibly with related keys ([GKNWW14] 2,
5). [GKNWW14] 2 says the attacks "drop" in importance going from H towards KP.

**Which model system B's use is in** (Original as far as checked; sources consulted:
[GKNWW14] 2, [EFK15] 5.1, [B3] 2.2, 4.2). A node under the framing of H-1.7 is one compression.
The chaining input `h = K_node`, `t = 0`, `b = 64` and `d = 0x4b` are fixed, and the attacker
chooses only the 512-bit message. That is model H. The later blocks of a multi-block leaf take a
chaining value the attacker reaches only by computing earlier compressions. CF is therefore a
conservative superset for leaves. FS, CIV and KP grant the attacker inputs the mode never grants.

**Rounds reached, by model.** Complexity is in evaluations of the function attacked. "None" means
none in the papers read; it does not mean that none exists.

| Primitive (rounds used) | H | CF (specified IV) | FS / CIV | KP (distinguishers) |
|---|---|---|---|---|
| **BLAKE3 (7)** | none | none | none | none. Only the designers' own trail search: [B3] Table 5 (H: 2 rounds, `>= 2^-185`, rotationally symmetric differences only; CF: 2.5 rounds, `2^-32`; KP: 3.5 rounds, `2^-52`) |
| **BLAKE2s (10)** | none on BLAKE2s. On BLAKE2b (12): differential, 3.5 rounds, `2^480` ([GKNWW14] 6, Appendix D); preimage, 2.75 rounds, `2^511` ([EFK15] 5.3, Table 7) | boomerang, 5 rounds: "could be launched", assuming characteristics "with similar probabilities can be found"; no complexity given ([GKNWW14] 2, p. 4). [B3] gives about `2^86`, which is not in the papers read | FS: pseudo-preimage, 6.75 rounds, `2^253.8` ([EFK15] Tables 1, 6). CIV: collisions on **all 10 rounds**, `2^64`, with `IV0 = IV1 = IV2 = IV3` ([GKNWW14] 3, Table 1) | boomerang, 7.5 rounds, `2^184` (Hao, reported by [TMC] 3.2); rotational with related keys, 7 rounds, about `2^511` against `2^512` ([GKNWW14] 3, Table 1); impossible differential with related keys, 6.5 rounds ([GKNWW14] 5); **all rounds**: a one-query distinguisher for `2^32` weak keys ([GKNWW14] 3, 7 item 1) |
| BLAKE-256 (14) | preimage, 2.5 rounds, `2^241`; collision, 2.5 rounds, `2^112` (Li and Xu, reported by [GKNWW14] Table 1; the preimage also by [B2] 4.1) | boomerang, 7 rounds, `2^242` (Biryukov, Nikolić, Roy, reported by [GKNWW14] Table 1, 2); near-collision, 4 rounds, `2^56` (Aumasson et al., reported by [GKNWW14] Table 1) | FS: pseudo-preimage, 6.75 rounds, `2^253.9` ([EFK15] Tables 1, 6) | boomerang, 8 rounds, `2^232` (reported by [GKNWW14] Table 1); differential, 6 rounds, `2^486` ([GKNWW14] Table 1) or `2^456` ([B2] 4.1, [B3]); impossible differential, 6.5 rounds ([GKNWW14] 5) |
| BLAKE2b (12) | as in the BLAKE2s row | differential, 4.5 rounds, `2^494.5` ([GKNWW14] 6, Appendix C) | FS: 7.5 rounds, `2^510.9` ([EFK15] Table 6; its Table 1 prints 510.3). CIV: partial collisions (208 bits) on all 12 rounds, `2^61`, and a weak class of preimages ([GKNWW14] 4) | boomerang, 8.5 rounds, `2^474` (Hao, reported by [TMC] 3.2); rotational, all 12 rounds, `2^876` against `2^1024` ([GKNWW14] 3) |
| Keccak-f[1600], 24 rounds (SHA3-384, SHAKE256): **as reported in [TMC] 3.4 and 5.1, not an independent survey** | collisions, 5 rounds, practical (SHA3-224, SHA3-256); preimages, 4 rounds (SHA3-224 `2^207`, SHA3-256 `2^239`); on non-standard capacity 160: 6-round collisions about `2^50`, 4-round preimages about `2^54`. Nothing on SHA3-384 or SHAKE256 | — | — | zero-sum distinguishers on 18 rounds, which led the designers to raise the count from 18 to 24 ([TMC] 5.1) |
| SHA-256, 64 steps | **none of the four papers states a round count attacked.** [TMC] 4.5 offers only an opinion: "Cryptanalysts seem to have given up on looking for collision attacks" | — | — | — |
| SHA-512, 80 steps (SHA-384 and SHA-512/t are truncations of it) | **not discussed in any of the four papers** | — | — | — |

**Margin in brief.** BLAKE3 uses 7 rounds. On BLAKE2s, whose round function BLAKE3 shares but
whose schedule and initialisation differ: none in H; 5 in CF (conditional estimate); 6.75 in FS
(meaningless for BLAKE3, H-1.13); all rounds in CIV; 7.5 and all rounds in KP. In the model
system B uses, the furthest result on the whole BLAKE/BLAKE2 family is 3.5 rounds. BLAKE2s
itself uses 10 rounds. Keccak uses 24 against 5 (collisions), 4 (preimages) and 18
(distinguishers), as [TMC] reports it.

**Stated plainly.** (1) None of the four papers analyses BLAKE3; [TMC] mentions it only in its
2026 addendum, as validation. (2) The BLAKE2 results do not cover BLAKE3's changes: the message
schedule (one permutation repeated, [B3] 7.4), row 4 (`t, b, d` with no `IV4..IV7`, [B3] 2.2)
and the finalisation (the truncated output has no feed-forward of the chaining value, [B3] 2.2,
7.3). [GKNWW14] 1: "no universal method nor theory exists that can transitively prove the
security of a symmetric primitive A obtained by modifying a primitive B". (3) Cryptanalysis
after these papers' dates was not searched. The BLAKE2 papers date from 2013 to 2015, and
[TMC]'s 2026 text cites nothing on BLAKE2 later than 2015. (4) The SHA-2 and Keccak rows are as
[TMC] reports them, and SHA-2 is barely covered. For the category 3 alternatives the four papers
give no basis; SHA-384, SHA-512 truncated, SHA3-384 and SHAKE256 need their own sources.

### H-1.12 [B3] Table 4 checked against the papers read (Published; corrections)

| [B3] Table 4 entry | Papers read | Status |
|---|---|---|
| BLAKE-256 c.f., preimage, 2.5 rounds, `2^241` [21] | on the **hash function**: [GKNWW14] Table 1 lists it under "BLAKE-256", not "cf."; [B2] 4.1: "attacks on the BLAKE as hash function" | model corrected (H, not CF) |
| BLAKE-256 and BLAKE2s c.f., pseudo-preimage, 6.75 rounds, `2^253.9`, `2^253.8` [17] | [EFK15] Tables 1, 6, Section 5.2 | confirmed; the model is FS ([EFK15] 5.1) |
| BLAKE2s k.p., boomerang, 7.5 rounds, `2^184` [19] | the same figures, reported by [TMC] 3.2 (citing Hao) | confirmed at second hand; Hao unread |
| BLAKE-256 and BLAKE2s k.p., impossible differential, 6.5 rounds [18] | [GKNWW14] 5, Table 1, related keys | confirmed |
| BLAKE2s k.p., rotational, 4 rounds, `2^489` [18, 20] | [GKNWW14] 3 and Table 1 give **7 rounds** at `2^511` (rotational related keys, against `2^512`). 4 rounds at `2^489` is not in [GKNWW14] | discrepancy; [20] unread; this record uses [GKNWW14]'s 7 rounds |
| BLAKE2s c.f., boomerang, 5 rounds, about `2^86` [10, 18] | [GKNWW14] 2, p. 4: 5 rounds, as a conditional estimate with no complexity | rounds confirmed as an estimate; complexity unverified |
| BLAKE-256 c.f., boomerang, 7 rounds, `2^242` [10] | [GKNWW14] Table 1 and Section 2 agree. [B2] 4.1 describes the same authors' result as "8 rounds of the core permutation of BLAKE-512, with complexity 2^242" and adds "recent work questions the correctness of this result" | secondary sources disagree; Biryukov, Nikolić, Roy unread |
| BLAKE-256 k.p., differential, 6 rounds, `2^456` [16] | [B2] 4.1: `2^456`; [GKNWW14] Table 1: `2^486` | the sources disagree; Dunkelman and Khovratovich unread |
| BLAKE-256 k.p., boomerang, 7 rounds `2^44` and 8 rounds `2^198` [6, 19] | not in the papers read; [GKNWW14] gives 8 rounds at `2^232` | unverified |
| BLAKE-256 c.f., near collision, 4 rounds, `2^56` [4] | [GKNWW14] Table 1: 4 rounds, `2^56` | confirmed at second hand |
| (not in Table 4) | CIV collisions on all 10 rounds of BLAKE2s c.f., `2^64` ([GKNWW14] 3); the all-round weak-key distinguisher on BLAKE2s k.p. ([GKNWW14] 3, 7); a 2.5-round collision on the BLAKE-256 hash, `2^112` (reported, [GKNWW14] Table 1) | added to the margin table |

### H-1.13 Which BLAKE2 results transfer to BLAKE3 (Original as far as checked; sources consulted: [GKNWW14] 2 to 7, [EFK15] 5, [B3] 2.2, 4.2, 4.4, 7.3, 7.4)

(a) **Free-state pseudo-preimages ([EFK15] 5.2) say nothing about BLAKE3.** BLAKE2 feeds the
chaining value forward, `h'_i = h_i xor v_i xor v_(i+8)` ([GKNWW14] 2). So even with the whole
state free, a preimage needs a meet in the middle, which [EFK15] builds. BLAKE3's truncated
output is `v'_i xor v'_(i+8)` with no chaining value ([B3] 2.2, 7.3). With the whole initial
state free, an attacker picks `m` and any final state that gives the target, applies `E^-1`, and
has a pseudo-preimage at any round count. The designers state this inversion for the full output
([B3] 4.2), and [B3] 7.3 says that without the feed-forward "the compression function would be
reversible when the message bytes were known". BLAKE3's preimage resistance therefore rests on
the fixed rows 3 and 4 (`IV0..IV3`; `t, b, d`), which is where the designers place it ([B3] 4.4:
"its input constraints on the compression function (that is, the IV constants)"). [EFK15]'s
6.75 rounds is not a "rounds reached" figure for BLAKE3, and revision 2's comparison "6.75 of 7"
is withdrawn.

(b) **The chosen-IV and weak-IV results ([GKNWW14] 3, 4) need a structured IV.** They need equal
columns (the squeeze attack), IV words that satisfy equation (2) (rotational pairs), or an IV
that is a fixed point. [GKNWW14] 7 item 4 names the guard: the IV words are not structured.
BLAKE3 keeps the same `IV0..IV3` in row 3 ([B3] 2.2, Table 1), so the guard on row 3 is the
same. Row 4 differs. BLAKE3 puts `t0, t1, b, d` there with no IV words. In H-1.7's node all four
are fixed and of low weight (0, 0, 64, `0x4b`), and zero words are rotation-invariant. [GKNWW14]
does not analyse such a row 4. Whether it gives an attacker a foothold is question Q-H2 (b).

(c) **The impossible differentials and differential trails ([GKNWW14] 5, 6) do not transfer as
such, in either direction.** They depend on BLAKE2's ten `sigma` permutations: the analysis
"heavily relies on the good (from an attacker point of view) properties of the different `sigma_r`
message words permutations" ([GKNWW14] 5). BLAKE3 repeats one permutation, chosen for the lowest
3-round trail probability ([B3] 7.4). The designers' own search ([B3] Table 5, with its
footnote 2 caveat) is the only BLAKE3 data.

(d) **What depends on `G` and the round alone does transfer**, because BLAKE3's round function is
BLAKE2s's ([B3] 2.2). The rotational probability, about `2^-9.1` per `G` and `2^-73` per round
([GKNWW14] 3), gives a related-key rotational distinguisher on BLAKE3's unconstrained 7-round
permutation at about `2^511`, against a 512-bit key (inference here). The weak-key property of
H-1.14 also transfers.

### H-1.14 A full-round weak-key property of the keyed permutation; consequence for MA-2' (Original as far as checked)

[GKNWW14] 3 (p. 6) gives a property of BLAKE2's permutation. Take four equal state columns and
equal message words: because `G` has no constants, every round keeps the columns equal. One chosen
plaintext then distinguishes the permutation for `2^w` keys (`2^32` for BLAKE2s), at every round
count. [GKNWW14] 7 item 1 says "this cipher can be fully attacked". BLAKE3's `E` uses the same
`G` and round ([B3] 2.2), and with all message words equal every schedule gives the same words.
So the property holds for BLAKE3's `E` at 7 rounds, and at any count (inference here; not stated
for BLAKE3 in [B3], [B3-ID] or the four papers). `E` is therefore not an ideal cipher on
unconstrained inputs, while [B3] 4.2's indifferentiability statement and MA-2' model it as one.
This is the usual position of a block-cipher-based compression function. The property needs equal
columns, which row 3 (`IV0..IV3`, all distinct) excludes for every input the BLAKE3 mode feeds
`E`, and which the node framing (`K_node`, `t, b, d`) excludes again. **Consequences:** (i)
sections 6.3 and 7 item 1 are reworded (done in this revision). (ii) MA-2' should be stated for
the referee (H-2) as: "the truncated compression function, restricted to inputs with row 3 =
`IV0..IV3` and the fixed row 4 of H-1.7, behaves as a random function". It should not say that
`E` is an ideal cipher. (iii) This feeds question Q-H2 (c).

### H-1.15 *Too Much Crypto*: what it proposes, for which primitives, on what argument (Published; record)

**Proposals** ([TMC] 5.3), with the speed-up it states for each:

| Primitive | Rounds now | Proposed | Name |
|---|---|---|---|
| AES-128, AES-192, AES-256 | 10, 12, 14 | 9, 10, 11 | — |
| BLAKE2b | 12 | 8 | BLAKE2bf |
| BLAKE2s | 10 | **7** | BLAKE2sf |
| ChaCha | 20 | 8 | ChaCha8 |
| SHA-3 | 24 | 10 | KitTen |

It makes **no proposal for SHA-256 or SHA-512** and gives no round count attacked for either.

**Argument.** (1) 128-bit security is sufficient, and `2^128` operations "must remain fantasy"
(Section 2). (2) Attacks on reduced rounds are negative results, and comparing complexities
above about `2^150` "is meaningless from a risk perspective" (Sections 2, 4.1, 4.3.2). (3) It
sets out four statuses for a primitive under attack, Analyzed, Attacked, Wounded and Broken
(Section 4.4). Its counts are those "for which we have strong confidence that the algorithm will
never be wounded, let alone broken", "Based on the previous research and our cryptanalysis
experience" (5.3). That is expert judgement, not a derivation. (4) Attacks plateau after the
differential analysis is done (4.5): "BLAKE2: There was no meaningful progress since the
differential analysis of BLAKE in 2011". (5) Margins should be consistent across families (5.3,
6). It defines the margin as "the gap between the highest round count then reached by
cryptanalysis and the round count specified" (abstract; 5.1). On Keccak it records the 18-to-24
increase after the zero-sum distinguishers and calls 24 "a very high security margin" (5.1). On
BLAKE2 it reports the pseudo-preimages of [EFK15] and Hao's boomerangs, and notes that on the
proper hash function "the best preimage attack applies to no more than 2.75 rounds" (3.2; from
[EFK15], this is BLAKE2b).

**Bearing on SQ-48.** [TMC]'s criterion is "never Wounded". That tolerates the status
"Attacked": an attack below the generic bound that remains impractical (4.4). This record's
reversal criterion (section 7 item 1) is stricter: any attack below `2^128`. [TMC] therefore
supports 7 rounds against practical risk. It does not support the claim that no academic attack
below `2^128` will appear. A consensus system that switches hash on a numerical break (section 7)
carries a risk [TMC] accepts and this record does not. The version read (20260706145800) agrees
with [B3] 4.4's summary ("BLAKE2s and BLAKE2b would be as safe with 7 and 8 rounds"). The 2019
and 2020 text that [B3] cites was not seen.

### H-1.16 Verdict on Q-H2, as far as these sources allow (Original (the Ycash developers, 2026))

**Established.**
1. No source read (six in all: [B3], [B3-ID] and the four papers) analyses BLAKE3 itself.
2. In model H, which describes system B's use (H-1.11), the published attacks on the BLAKE and
   BLAKE2 family reach 2.5 rounds (BLAKE-256: `2^241` preimage and `2^112` collision, reported),
   2.75 rounds (BLAKE2b preimage, `2^511`) and 3.5 rounds (BLAKE2b differential, `2^480`). None
   reaches the BLAKE2s hash. Against 7 rounds, more than half the rounds are unreached. The
   designers' trail search on BLAKE3 agrees in kind ([B3] Table 5).
3. In model CF with the specified IV, the furthest results are 5 of BLAKE2s's 10 rounds
   (boomerang, a conditional estimate) and 7 of BLAKE-256's 14 rounds (boomerang, `2^242`, on a
   function with constants in `G`).
4. Results reach 6.75, 7, 7.5 and all rounds only in models the mode excludes: free state,
   chosen IV and the unconstrained keyed permutation. The free-state model is trivial for BLAKE3
   (H-1.13 (a)).
5. The papers' own judgements. [GKNWW14] 7: BLAKE2 "has a very high security margin against all
   known attacks even after reducing the number of rounds by four", which refers to 10 rounds,
   not 7. [B2] 4.1 expects attacks on `n`-round BLAKE to adapt to `n`-round BLAKE2. [TMC] 5.3
   proposes 7 for BLAKE2s as "never wounded", which is a co-designer's judgement.

**Not established (for the external cryptographer).**
(a) Whether BLAKE3's changes lose or gain rounds against the attacks of [GKNWW14] and the
boomerangs: the single permutation, row 4, and the truncated half without feed-forward. No
third-party analysis read covers them.
(b) Whether a low-weight row 4 (`0, 0, 64, 0x4b` in H-1.7) helps an attacker (H-1.13 (b)).
(c) Whether MA-2', restated as in H-1.14 (ii), is an acceptable heuristic for a consensus system.
(d) Analysis of BLAKE2s after 2015, and of BLAKE3 at all. [TMC]'s 2026 addendum asserts that no
results contradict it but cites none.
(e) The unread papers behind the furthest results: Hao 2014 (7.5 rounds of the keyed
permutation), Biryukov, Nikolić and Roy 2011, Dunkelman and Khovratovich 2011, Li and Xu 2009,
Khovratovich et al. 2015 (`../REFERENCES.md` 1.1e-bis).

**Verdict.** In the model system B uses, the sources read support 7 rounds: the margin there is
more than three rounds out of seven on the predecessors. The thin and negative margins (5, 6.75,
7.5, all rounds) appear only in models the mode excludes, or on BLAKE2s's compression function,
whose schedule differs. With no BLAKE3-specific analysis, Q-H2 stays open, and constraint 4 of
section 10 stands. **Nothing read changes the record's conclusion**: BLAKE3 stands for category 1
with constraints and is not admissible at category 3 or above. The category argument (H-1.5)
rests on the 128-bit claim and the 256-bit chaining value, which the papers do not touch. One
constraint is sharpened: MA-2' as restated in H-1.14 (ii).

### H-1.17 Quantum (Q-H1): what [TMC] 5.2 says, and why it does not close Q-H1 (record; the observation is Original as far as checked)

[TMC] 5.2.1 says Grover's algorithm "is not a reason to add rounds". It cites Valsorda (2026) and
NIST's PQC FAQ, neither read. [TMC] 5.2.2 says dedicated quantum attacks (Simon-type, quantum
slide, hidden shift) mostly need superposition queries to a keyed oracle, the Q2 model, "a much
stronger model than an attacker merely owning a quantum computer". It adds that they "mostly do
not say that AES, ChaCha, BLAKE2, or SHA-3 need more rounds". Observation: for a public, unkeyed
hash in the QROM, superposition access to the hash is the model itself. The Q2 distinction [TMC]
draws for keyed primitives does not separate any cases for system B's hash. No paper read gives
a quantum attack on, or a quantum bound for, a BLAKE-type function. Q-H1 stays open as written,
and H-1.3 is unchanged in substance.

## 10. Verdict: the decision stands, with constraints

The decision **stands, with constraints**; it is not reversed, because the claimed collision
level equals the level category 1 already rests on (H-1.2), no published result reaches BLAKE3
or reaches its predecessors' components at 7 rounds below the claim except a distinguisher on
BLAKE-256's keyed permutation that the designers argue does not apply (H-1.8), and the cost reason
(a factor of about two at the certified row) stands. Stated without softening: BLAKE3's designers
claim 128 bits for preimages where SHA-256 offers 256, claim nothing against quantum attackers,
and rest 7 rounds on a margin of a fraction of a round over the furthest published analyses of
BLAKE2s; for a consensus system that is a real loss of margin, accepted for category 1 only
under these constraints.

**Revision 3**, after the four cryptanalysis papers (H-1.10 to H-1.17). The verdict and the
constraints are unchanged. Three things in the paragraph above are refined. First, "a fraction of
a round over the furthest published analyses" holds in the keyed-permutation, free-state and
chosen-IV models, which the mode excludes; in the hash-function model of system B's use, the
furthest published result on the family is 3.5 rounds (H-1.11, H-1.16). Second, the list of
results below `2^128` is longer than "a distinguisher on BLAKE-256's keyed permutation". It also
holds a full-round chosen-IV collision and a full-round weak-key distinguisher on BLAKE2s's
components ([GKNWW14] 3, 7), neither applicable to the inputs the mode feeds, and a 2.5-round
collision on BLAKE-256 (H-1.8). Third, MA-2' is restated (H-1.14 (ii)) and its review joins
constraint 3. The constraints:

1. **Category 1 only.** The category 3 row's Merkle hash for system B is SHA-384 (or SHA3-384);
   BLAKE3 with extended output is never a category 3 digest (H-1.5).
2. **Framing.** The plain-hash framing as built is not acceptable; system B's trees use the
   `derive_key` framing of H-1.7 (or its `keyed_hash` fallback), with its acceptance tests, before
   any certified figure is quoted for the BLAKE3 row (H-1.6).
3. **Model.** MA-2' replaces MA-2 for the BLAKE3 row, stated for IV-constrained inputs and not
   as an ideal cipher (H-1.14 (ii)). The referee reviews H-1.2, H-1.3, H-1.6, H-1.7 and H-1.14
   (obligation H-2).
4. **External review before activation.** Questions Q-H1 and Q-H2 (section 11) are answered by
   the external cryptographer, and the cited cryptanalysis is read, before Yugen activates with
   the BLAKE3 row; until then the decision stays provisional and the SHA-256 build stays tested.

The alternative, if any condition fails: the SHA-256 row (built; 364 AND rows a compression;
13,000 to 18,600 core-seconds at 184 queries, E) with more hosts or a list-decoding row once
reviewed, at category 1; SHA-384 at category 3 in either case.

## 11. Questions for the external cryptographer, and the remaining tasks

- **Q-H1.** Is a hash whose designers claim 128 bits for preimages and nothing quantum adequate
  when the proof system's QROM analysis models it as a 256-bit random oracle for adversaries of up
  to `2^64` quantum queries and `2^128` classical ones (H-1.3)?
- **Q-H2.** Is BLAKE3's 7-round margin (H-1.8, margin table H-1.11) adequate for a consensus
  system, given the boomerang and pseudo-preimage results on BLAKE-256 and BLAKE2s, and is there
  later analysis of BLAKE3 that changes the picture? Revision 3 splits it into the parts the four
  papers leave open (H-1.16):
  (a) do BLAKE3's single message permutation, its row 4 (`t, b, d` with no IV words) and its
  truncated output without feed-forward lose or gain rounds against the attacks of [GKNWW14] and
  the boomerangs?
  (b) does a fixed, low-weight row 4 (`0, 0, 64, 0x4b` for H-1.7's node) help an attacker
  (H-1.13 (b))?
  (c) is MA-2' as restated in H-1.14 (ii) acceptable, given the full-round weak-key property of
  the unconstrained permutation?
  (d) is there analysis of BLAKE2s after 2015, or of BLAKE3 at all?

| Task | Responsible | Acceptance |
|---|---|---|
| H-2a framing (H-1.7) | system B builder | tests (i) to (v) of H-1.7 pass; AND rows a node 168 (C) |
| H-2b MA-2' | lead agent (`qrom-compilation.md` 2.2, 2.6, 3) | the B column names BLAKE3 `derive_key` leaves and nodes and MA-2'; H5 met |
| H-2c referee | referee | H-1.2, H-1.3, H-1.6, H-1.7, H-1.14 reviewed with a written verdict |
| H-1c papers | lead architect | [TMC], [B2], [EFK15] and [GKNWW14] obtained and read (revision 3, done). Still to obtain: the papers listed as "to obtain" in `../REFERENCES.md` 1.1e-bis. Accepted when each H-1.12 row is confirmed or corrected on the typeset page |
| H-1e literature search | lead architect or a delegated reader | a dated search (ePrint, ToSC, FSE, CRYPTO and EUROCRYPT proceedings) for cryptanalysis of BLAKE2s and BLAKE3 after 2015, its results added to the margin table, or "none found" with the query recorded |
| H-1f category 3 sources | lead architect | sources for reduced-round results on SHA-512 (for SHA-384 and SHA-512 truncated) and on Keccak at capacity 768 or 512 (SHA3-384, SHAKE256). None of the four papers covers them (H-1.11) |
| H-1d external review | lead architect | written answers to Q-H1, Q-H2 |
| C3-hash | system B builder | H-1.5 (a) to (c) |
