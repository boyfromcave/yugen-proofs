# Decision record (DRAFT): the Fiat–Shamir transcript hash of proof system B

Part of Yugen. **Draft, unrefereed**: a recommendation of the maths team to the lead
agent, 2026-11-19. Nothing here is decided; items R-1 to R-3 of section 11 need the lead
architect. The decision number is the lead agent's to assign. Format and standard follow
`decision-b-merkle-hash.md` (SQ-48). Figure marks: (M) measured, (C) counted from a compiled
circuit, (E) estimate; every (M) and (C) figure is system B's own, from
`yugen-proof-b2/docs/parameters.md` at `09a7b4e` (sections 7.6, 10.2, 10.3, 15.1, 15.6, 15.7).
Nothing was re-measured. Estimates marked "(E, here)" are this record's arithmetic on those
figures and are for the B team to replace by counts.

## 1. The question

Every proof of system B derives its challenges with the spBCS transcript of
`qrom-compilation.md` section 2 (Published: Sharp and Grubbs, ePrint 2026/2615 [SG26], Protocol
6.5 and Section I.1): a 32-byte **key** `u_i = H_ch(whole past)` for each verifier message and a
**stream** `y_i = H_stream(u_i, s)` of `32 + e_i` bytes from which the challenges are read, the
first 32 bytes written back. As built, `H_ch` is SHA-256 (FIPS 180-4) and `H_stream` is SHAKE256
(FIPS 202). A node of the bundle tree recomputes this transcript in circuit for every proof it
verifies. Which functions should `H_ch` and `H_stream` be?

Not in question: the statement (Keccak/SHAKE in both systems), system A's transcript and trees
(Keccak-256, SHAKE256), system B's Merkle trees (BLAKE3 `derive_key`, SQ-48, provisional).

## 2. Why the question is asked: goal D-6

D-6 (the plan's E2: "Node verification 100 ms or less per proof") is not met. System B's figures
at `09a7b4e`:

| Final verification of a level-3 root, four cores | Figure |
|---|---|
| As built (four grouped shapes) | about 390 to 420 ms (E from M) |
| With one merge shape | about 180 ms (E from M) |
| The same with BLAKE3 keys and streams | about 90 to 100 ms (E) |
| The same with the nested evaluator at the plain shape's rate, hash unchanged | 90 to 120 ms (E; 15.6: "either alone leaves it at 90 to 120") |
| Both | about 50 to 60 ms (E) |

The level-1 residue is 527,611 AND rows (C). Its transcript is 292,656 rows of SHA-256 (about
800 compressions: absorption, 152 write-backs, 152 key finalisations) and 91,275 rows of
Keccak-f (152 stream permutations of 600), together 73% (C, census 15.1). A main circuit is
nearly all transcript.

## 3. Options considered

| | Option | Residue, B's figure | Residue, corrected (E, here; T-5) | D-6, B's figure | Published theorem behind the random-oracle modelling of each part | Functions B's soundness rests on | Shared with system A |
|---|---|---|---|---|---|---|---|
| (a) | SHA-256 keys, SHAKE256 streams (built) | 527,611 (C) | same | about 180 ms; 90 to 120 with the evaluator repaired | keys: none (Merkle–Damgård on nested inputs, T-2); streams: the sponge's (not in the folder, T-3) | BLAKE3, SHA-256, Keccak-f | Keccak-f |
| (b) | BLAKE3 keys, SHAKE256 streams | about 370,000 (E) | 413,000 to 440,000 | not given | keys: [B3] 4.3, bound (2), ideal-cipher model; streams as (a) | BLAKE3, Keccak-f | Keccak-f |
| (c) | BLAKE3 keys, BLAKE3 XOF streams (B's recommendation) | about 305,000 (E) | 350,000 to 405,000 (by framing) | 90 to 100 ms | keys as (b); **streams: none** ([B3] 4.2, 4.3: T-3) | BLAKE3 | none |
| (c*) | BLAKE3 keys, BLAKE3 counter-mode streams of 32-byte outputs, salt-first framing (this record's variant; T-4) | — | 380,000 to 405,000 | not given; within about 10% of (c) | keys and streams: [B3] 4.3, bound (2); Lemma X costs 1.00 QROM bit | BLAKE3 | none |
| (d) | Keep (a), restate D-6 at about 200 ms | 527,611 | same | met at about 180 ms | as (a) | as (a) | Keccak-f |

Also considered and not listed: Keccak-256 keys (one Keccak-f per 136 bytes at 600 rows:
costlier than SHA-256, and both systems fully on Keccak); an arithmetization-oriented hash
(excluded by the project's rule, `decision-b-merkle-hash.md` section 3); counter-mode SHA-256
streams (measured costlier than SHAKE256, B's 10.3: 1,478 against 1,337 rows a message).

## 4. Recommendation

1. **Keep (a) now.** Do not change the transcript hash to reach D-6 before the two
   hash-independent reductions are built and measured: the batching rounds of
   `decision-b-parallel-batching.md` and the repair of the nested evaluator's rate (B's 15.6).
   By B's own estimates these two bring a level-3 root to about 60 to 95 ms with the hash
   unchanged (E, here, from B's E: 90 to 120 ms with the evaluator repaired, less the 22% to
   32% of terms that main's batching transcript loses; T-9). Not established; to be measured.
2. **If D-6 is still missed after both, the hash change to prepare is (c\*), not (c).** (c\*)
   keeps every BLAKE3 call inside the designers' indifferentiability statement and inside a
   mode the specification defines. It needs the lead architect's ruling R-1 and obligations
   TH-1 to TH-6 first.
3. **Reject (c) as proposed** (BLAKE3 XOF streams). Every stream is at least 64 bytes, and
   BLAKE3's extended output is made of full 16-word compression outputs, for which the
   designers state that the compression function is not indifferentiable and give no theorem
   for the mode (T-3). The saving of (c) over (c\*) is under 10% of the residue (E, here).
4. **Reject (b)**: it removes SHA-256 from system B but keeps the one primitive both systems
   share (Keccak-f), for about half the gain.
5. **(d) is the interim position, and costs no security.** Until item 1 is measured, D-6 is
   reported as missed at about 180 ms with one merge shape; what 200 ms costs a node is in T-8.
   Whether E2's 100 ms is restated is the lead architect's (R-3; SQ-50 (1) already says E2 is
   restated from measurement).

**The decisive reason.** D-6 is a performance target. Missing it at 180 ms costs a node about
0.1 s more per block, inside the plan's 1-second verification cap. Options (b), (c) and (c\*)
instead move the Fiat–Shamir step of a consensus proof, which is where the bundle's statement
is bound to the proof, onto a function whose designers claim 128 bits, say nothing about
quantum attackers, and use 7 rounds; (c) further uses it in a way its own security analysis
does not cover. Security comes first, and a route to D-6 that does not touch the hash exists
and is not yet tried.

## 5. Why, in order of weight

1. **The theorem is indifferent to the hash; the support for the modelling is not.** T-1 to T-4.
2. **A cheaper route to D-6 is untried.** T-9.
3. **B's cost estimate for the change is optimistic.** T-5: the straight ratio 168/364 omits
   the tree mode's key finalisations and assumes one compression a stream.
4. **Independence cuts both ways** (T-6): (c) and (c\*) are the only options in which no hash
   primitive is shared between the two proof systems, and that is a real gain; they are also
   the only options in which system B's soundness has no FIPS function in it at all.
5. **The hash policy as recorded does not cover it** (T-7).

## 6. What is given up by keeping (a)

1. D-6 stays unmet until the batching and evaluator work lands; if that work reaches only 100
   to 120 ms, the choice between (c\*) and a restated D-6 returns.
2. The shared exposure of both systems to Keccak-f stays (system B's streams are SHAKE256). A
   failure of Keccak-f as a random function would reach system A wholly and system B's
   challenge streams. This is the one argument for (c\*) that is about security and not cost;
   it is put to the lead architect in R-2.
3. The key hash stays a Merkle–Damgård function on nested inputs, which no indifferentiability
   theorem covers (T-2). [SG26] does the same with SHA-384.

## 7. What would reverse the recommendation

Towards (c\*):
1. D-6 measured above 100 ms on a level-3 root after the parallel batching rounds and the
   evaluator repair, together with the lead architect declining to restate D-6.
2. The lead architect ruling (R-2) that independence of the two systems' hash primitives
   outweighs a FIPS function in system B's transcript.
3. In both cases only after R-1, TH-1 to TH-6, and with `decision-b-merkle-hash.md`'s
   constraints (category 1 only, external or internal referee answers to Q-H1 and Q-H2)
   extended to the transcript.

Towards (c) with XOF streams: a published indifferentiability theorem (or a refereed proof of
our own) for BLAKE3's extended output beyond 256 bits. None is in hand.

Away from BLAKE3 altogether (trees included): the reversal conditions of
`decision-b-merkle-hash.md` section 7.

## 8. Provenance

Published, as taken: the spBCS transcript and Theorem 6.6 (2) with its Section I.1 ([SG26]);
BLAKE3's modes, flags, extended output and security statements ([B3] = O'Connor, Aumasson,
Neves, Wilcox-O'Hearn, *BLAKE3: one function, fast everywhere*, version 20211102173700,
Sections 2.3 to 2.6, 4.1 to 4.4, 7.3, 7.7; read for this record from the text layer of the
lead architect's copy, the passages quoted below checked there); the cryptanalysis table of
`decision-b-merkle-hash.md` 9b (its sources, not re-read here). Adapted: option (c\*) (from
[B3]'s `derive_key` mode and Lemma X of `qrom-compilation.md` 7.1; changes in T-4). Original
(the Ycash developers, 2026), as far as checked against [SG26] Section I.1, [B3] and
`qrom-compilation.md`: findings T-2 (the nested-input observation for SHA-256 keys), T-3 (the
consequence of [B3] 4.2 and 4.3 for spBCS streams), T-5 (the cost corrections), T-6 (the
dependency table), T-7, T-9, O-inner. Cited from memory, not in the reference folder, not read:
Coron, Dodis, Malinaud, Puniya, "Merkle–Damgård Revisited", CRYPTO 2005; Bertoni, Daemen,
Peeters, Van Assche, "On the Indifferentiability of the Sponge Construction", EUROCRYPT 2008.
Each use below is marked.

## 9. Findings

### T-1 Theorem 6.6 (2) carries over for any hash; no number changes (Published; record)

The theorem is a statement in the (quantum) random-oracle model about one oracle with four
disjoint parts ([SG26] I.1, "The oracle's domain"). The hash enters in exactly three places:
hypothesis H5 (which functions are modelled as that oracle), the digest length `b` and the
stream excess `e` (`qrom-compilation.md` section 3). [SG26] itself instantiates the oracle with
two unrelated functions and models them as one: "We model both functions as the one random
oracle H, with these input sets as its disjoint domain parts" (I.1, "Hash functions", p. 131;
SHA-2 for challenge inputs, leaves and nodes, cSHAKE256 for streams). So for every option:

- `b = 32` and the longest stream are unchanged, hence `k_q`, `c'`, the hash term (75.63 bits
  in the revision 6 table, `qrom-compilation.md` section 5) and the QROM bits (70.45 for B at
  calculator revision 9) are unchanged, except (c\*)'s Lemma X factor (T-4).
- Domain separation, salt framing and the write-back are requirements on encodings (injective,
  disjoint images, the proof salt in every challenge input and stream point), which any of the
  functions can meet (TH-2).
- What changes is the modelling assumption: MA-1 ("SHA-256 on tagged inputs and SHAKE256 on
  tagged inputs are parts of one random oracle") becomes a statement about BLAKE3. The rest of
  this section is about how well each such statement is supported.

### T-2 Keys: BLAKE3's hash is inside its designers' theorem; SHA-256 on nested inputs is inside none (Original as far as checked)

The challenge input of message `i + 1` extends that of message `i` (`qrom-compilation.md` 2.1),
so the set of key inputs of one proof is a chain of prefixes: it is not prefix-free.

- **SHA-256.** A Merkle–Damgård hash with length padding is differentiable from a random oracle
  by length extension, and is indifferentiable for prefix-free encodings (Coron et al., from
  memory, not read). The key inputs are not prefix-free, so no indifferentiability theorem
  covers MA-1's SHA-256 part. Length extension gives no attack found here: from `u_i` one can
  compute SHA-256 of `input_i || padding || X`, but every input and the proof salt are public
  to whoever holds the proof, and the bytes that follow `input_i` in a real challenge input
  are the 32-byte write-back, not a padding block. This is the same heuristic [SG26] makes for
  SHA-384. It is recorded because revisions 1 and 2 of `qrom-compilation.md` discuss length
  extension only for fixed-length tagged inputs (`qrom-zk-referee.md` 1.7).
- **BLAKE3, 32-byte output.** The designers give a differentiability bound for "256-bit outputs
  or shorter" ([B3] 4.3, equation (2), by Theorem 1 of Daemen, Mennink, Van Assche with the
  truncated compression function's indifferentiability from Luykx, Mennink, Neves; neither
  cited paper read), in the ideal-cipher model. Length extension is excluded by the ROOT flag:
  "Subtree-freeness ensures that generalized length-extension attacks, like the ones that
  plagued Merkle-Damgård, cannot happen" ([B3] 4.3); "The ROOT flag ... separates the final
  block from all other blocks in a root chunk, both of which prevent length extension" ([B3]
  7.7). A long transcript is hashed in BLAKE3's tree mode (1,024-byte chunks, parent nodes),
  which bound (2) covers.
- **Weighing.** In kind, BLAKE3's key hash has the better-founded ideal-model statement. In
  level, bound (2) carries the term `q / 2^128`, the same order as the whole classical target
  (`eps_tree(t) <= t / 2^128`): composed literally it halves the classical budget (one bit),
  and it is a classical bound in the ideal-cipher model whose premise holds only on the
  IV-constrained inputs the mode feeds the permutation (`decision-b-merkle-hash.md` H-1.14).
  SHA-256 has no theorem and no known structural weakness in this use, a FIPS status, and a
  256-bit preimage level. Neither function's designers say anything about quantum attackers.

### T-3 Streams: BLAKE3's extended output is outside its designers' theorem (Original as far as checked; the cited statements are Published)

[B3] 2.6: extended output repeats the root compression with an incrementing counter and "uses
the full output of the compression function"; each 16-word output is 64 bytes. [B3] 4.2: the
16-word finalisation "causes the BLAKE3 compression function to no longer be indifferentiable,
unlike its predecessor", with the explicit inversion that shows it. [B3] 4.3 states bound (2)
"If only considering 256-bit outputs or shorter", and for longer output only remarks that "the
feed-forward serves the same purpose as truncation, and the result still follows as long as
the other soundness requirements are in place": a remark, with no theorem and no bound.

Every spBCS stream is at least 64 bytes (32 written back and at least one 32-byte challenge),
and the longest are 944 bytes as built and 1,504 at 368 queries (`qrom-compilation.md` H9). So
under (c) **every challenge of every proof** comes from the part of BLAKE3 the designers'
analysis does not cover, and hypothesis H9 ("the oracle's output taken at the longest stream")
would rest on a new modelling assumption with nothing published behind it. No attack follows
from differentiability by itself, and none is claimed here. The finding is that the proof
route "ideal compression function, then indifferentiable mode, then Theorem 6.6 (2)" exists
for BLAKE3 outputs of at most 32 bytes and does not exist for its extended output.

SHAKE256, by comparison: a sponge with capacity 512 bits, specified in FIPS 202; the sponge's
indifferentiability from a random oracle for a random permutation is a published theorem
(Bertoni et al., from memory, not read), for any output length. Its quantum counterpart is a
heuristic in both cases (`qrom-zk-referee.md` 1.4).

Also from [B3] 2.6: "BLAKE3 does not domain separate outputs of different lengths. Shorter
outputs are prefixes of longer ones." This matches spBCS's requirement that each use reads a
prefix of one long output, and is harmless here; it would be harmful if a 32-byte key and a
stream were ever taken from the same input (TH-2 forbids it).

### T-4 Option (c\*): counter-mode streams of truncated outputs, salt first (Adapted)

Adapted from [B3]'s `derive_key` mode (2.3, 6.2; as `decision-b-merkle-hash.md` H-1.7 uses it
for leaves and nodes) and from the counter-mode alternative of `qrom-compilation.md` 2.5 with
Lemma X (7.1). Changes: BLAKE3 in place of SHA-256; the proof salt first; contexts in place of
tag bytes.

```
C_key    = "Yugen 2026-11-19 spBCS system B transcript key v1"
C_stream = "Yugen 2026-11-19 spBCS system B transcript stream v1"
u_i      = derive_key(C_key,    s || pre(x) || items before message i)          32 bytes
y_i      = B_0 || B_1 || ..,   B_c = derive_key(C_stream, s || u_i || LE32(c))  32 bytes each
```

- **Inside the theorem and the specification.** Every value is a 32-byte output of a defined
  BLAKE3 mode: bound (2) applies to each, and nothing uses the 16-word output.
- **Salt framing.** `s` is 64 bytes and is the first block of both inputs, alone. In a stream
  point the block `s` is compressed once per proof (flag CHUNK_START) and its chaining value is
  reused; each 32 bytes of stream is then **one** compression of the 36 bytes `u_i || LE32(c)`
  (flags CHUNK_END, ROOT, DERIVE_KEY_MATERIAL). The whole input is 100 bytes, one chunk. This
  is ordinary incremental hashing of a defined input, not a bare compression call. The
  encoding `(u, s, c) -> s || u || LE32(c)` is injective at fixed lengths, which is all
  [SG26] I.1 asks of `stream(u, s)`. Where the 512-bit salt enters a stream point it passes
  through one 256-bit chaining value; `zk-quantum.md` 2.2's salt-search figure is to be
  re-read for this (TH-4), as H-1.4 did for leaves.
- **Lemma X.** Its proof uses only that the counter-mode function and the hash on its domain
  part are the same random function re-indexed (`qrom-compilation.md` 7.1); it does not use
  SHA-256. With the stream part a separate `derive_key` context, an adversary making `t`
  quantum queries is simulated with at most `2t` queries to the long-output oracle, so Theorem
  6.6 (2) applies with `t -> 2t`: **1.00 bit** off the QROM figure (70.45 to 69.45 at revision
  9, against 64), nothing at `t = 1` classically. To be confirmed by the referee (TH-3).
- **Cost** (E, here): a verifier message with one challenge reads 64 bytes, two compressions,
  336 AND rows, against one Keccak-f of 600 (C) today and 168 for (c) with the same salt-first
  framing. A query message of 192 indices reads 768 bytes: 24 compressions against 12 for (c)
  and 6 Keccak-f today.

### T-5 The cost of the change: two corrections to B's estimate (E, here; for the B team to count)

B's 370,000 for (b) is `527,611 - 292,656 + 292,656 x 168/364`, a straight ratio. Two things
that ratio does not hold:

1. **Key finalisation in tree mode.** spBCS takes a key from a clone of the running state for
   every verifier message. For SHA-256 the clone pads and compresses: one or two compressions.
   For BLAKE3 the clone finishes the current chunk (one compression) and merges the stack of
   subtree chaining values (one parent compression each, the last with ROOT): `1 + popcount`
   of the number of completed chunks. At 32 to 42 KB absorbed (from B's "about 800
   compressions" less the finalisations) that averages about 3.5 compressions a key: about 530
   for 152 keys, against 150 to 300 for SHA-256. Absorption is 500 to 650 compressions plus 31
   to 41 parents. Total about 1,060 to 1,220 BLAKE3 compressions, 178,000 to 205,000 rows,
   against B's 135,000: **(b) is about 413,000 to 440,000**, not 370,000. The stack shape at
   every key is fixed by the row's schedule, so no data-dependent selection is needed.
2. **Streams.** B's 305,000 for (c) takes one compression a stream (152). With the built
   framing `0x23 || u || s` (97 bytes, two blocks, the first depending on `u`) an extended
   output costs one compression plus one per 64 bytes: at least two a stream. One a 64 bytes is
   reached only with the salt-first framing of T-4.

Result: (c) is 350,000 (salt first) to 405,000 (framing as built); (c\*) is 380,000 to 405,000.
Against 527,611 that is a cut of 23% to 34%, not 42%. B's D-6 figure for (c), 90 to 100 ms,
assumed 305,000; at the corrected counts and the same rate it is nearer 100 to 115 ms (E from
E, weak): **(c) alone does not safely meet D-6 either.**

### T-6 What each system rests on, and what a break of BLAKE3 breaks (Original as far as checked)

| Function | System A | System B, (a) built | (b) | (c), (c\*) |
|---|---|---|---|---|
| Keccak-f[1600] | trees, keys, streams | streams (SHAKE256) | streams | — |
| SHA-256 | — | keys | — | — |
| BLAKE3 | — | trees | trees, keys | trees, keys, streams |

A transfer needs both systems' proofs to verify (the plan, section 4: "both must verify"), so a
forgery needs both systems broken.

- **System B's soundness already rests on BLAKE3**, since SQ-48: a collision in the node or
  leaf hash breaks the Merkle commitment's binding and with it extraction. So does its hiding
  for leaf proofs: the salted leaf digests on opened paths hide unopened values only if the
  leaf hash does (`zk-quantum.md` 3). Moving the transcript to BLAKE3 does **not** change which
  system a BLAKE3 break reaches, and it is not "hiding only": in every option a BLAKE3 break is
  a soundness break of system B and leaves system A standing.
- **What (b), (c), (c\*) add** is the kind of weakness that suffices. Today a break must produce
  collisions in a 64-byte-input, 32-byte-output `derive_key` call or defeat a salted leaf.
  With BLAKE3 keys and streams, any non-random behaviour that lets a prover steer challenges
  faster than search also suffices, over long inputs in tree mode (keys) and, under (c), over
  the uncovered extended output. Fiat–Shamir asks more of a hash than collision resistance.
- **What (c), (c\*) remove.** Today system B's soundness needs three functions to hold; under
  (c) one. And today Keccak-f is in both systems: a failure of Keccak-f as a random function
  reaches all of system A and system B's streams together. Under (c) and (c\*) the two proof
  systems share no hash primitive inside their proofs. (The statement is Keccak in both by
  design; that is outside this record.)
- **Net.** "Concentration" is the wrong picture within system B (fewer functions must hold,
  one of them is asked for more). Across the two systems (c\*) improves independence. The cost
  is that system B's proof layer would contain no FIPS function, and would rest entirely on a
  function with the margins of `decision-b-merkle-hash.md` 9b: 7 rounds; on the predecessors,
  in the hash-function model, attacks reach 2.5 to 3.5 rounds; no third-party analysis of
  BLAKE3 itself in the sources read; a 128-bit claim for every goal against SHA-256's 256-bit
  preimage level; nothing on quantum attackers. For ChaCha, whose permutation the BLAKE family
  derives from, the best result reported in Aumasson's *Too Much Crypto* (ePrint 2019/1492,
  Section 3.3, a co-designer's survey) is a key recovery on 7 of 20 rounds; this record did not
  read its sources.

### T-7 The hash policy does not, as recorded, cover the transcript

The lead architect's ruling as the plan records it (SQ-50 (4)): "FIPS-standard hashes for
binding digests; BLAKE3 only inside system B's proof trees." The brief for this record words
it "FIPS for binding, BLAKE3 inside proofs". Under the recorded text a transcript is not a
proof tree, so (b), (c) and (c\*) are outside the ruling. Under the wider wording the question
is whether the key hash is "binding". It is not consensus-visible: no key or stream is
published, every node recomputes them. But it is binding in function: the key hash is the only
place where the statement (`pre(x)`, with the bundle's public inputs) and every Merkle root
are tied to the challenges, and so to the proof. A collision between two challenge inputs is
a statement or commitment substitution. This record's reading: the transcript falls on the
"binding" side of the policy's intent, and **an explicit ruling is needed (R-1)** before any
BLAKE3 transcript is built as a default.

### T-8 What a 200 ms root verification costs a node (E, here; from the plan's figures)

From the plan (sections 5, 7 and 8): one bundle per block at launch; 75-second blocks, 1,152 a
day; "the worst block verifies in 1 second on a four-core reference machine"; system A
verifies in 7 to 15 ms a proof.

| Quantity | At 100 ms | At 200 ms |
|---|---|---|
| System B root, per block | 0.1 s | 0.2 s |
| Share of the 75 s block interval | 0.13% | 0.27% |
| Worst block at launch (one bundle pair and one leaf pair; B's zero-knowledge leaf 117 to 119 ms, M at the 96-bit level) | about 0.25 s | about 0.35 s |
| Against the 1 s verification cap | inside | inside |
| Initial sync, verification of bundle roots, per day of chain | about 115 s | about 230 s |
| Block relay, if a node verifies before it forwards | — | about 0.1 s more a hop; the plan's condition for raising `W` is block-plus-proof propagation of 1.5 s or less at the 95th percentile (section 7) |
| Mempool: a relayed bundle refused or accepted | 0.1 s | 0.2 s of four cores each |

The per-hop relay term is the one that matters and the one to measure (it depends on whether
the node lines forward a block before or after proof verification). The others are small.

### T-9 D-6 without a hash change (E, here, from B's estimates; not established)

B's 15.6: with one merge shape and the evaluator at the plain rate, hash unchanged, 90 to 120
ms. Main is 8.6 M of a level-1 node's 23.1 M terms and "nearly all" transcript; the batching
change of `decision-b-parallel-batching.md` cuts main's transcript by about 2.4 to 3 times
with shared challenges and by the number of groups with one combined round polynomial (that
record, section 7): 22% to 32% of the node's terms, taking all of main as batching
transcript, which overstates it by the rows that absorb the claims. Applied to 90 to 120 ms:
about 60 to 95 ms. A level-3 root has seven groups and 417 batching rounds, so it gains more than level 1.
These are estimates on estimates. The acceptance test is a timed level-3 root (TH-6).

### T-10 Margins at the output lengths the transcript uses (record; generic figures from memory as in `soundness-method.md` 8.2)

| Use in the transcript | What an attack must do | Generic cost, 256-bit random oracle | SHA-256 / SHAKE256 | BLAKE3 |
|---|---|---|---|---|
| Key `u_i`, 32 bytes | two different pasts with one key (the `c'` term of Theorem 6.6 (2)) | `2^128` classical; about `2^85` quantum (collision search) | designers' collision level 128 bits (FIPS 180-4 with SP 800-107, from memory) | claimed 128 bits ([B3] 4.1): equal |
| Key, as a target | a past hashing to a given key | `2^256`; `2^128` quantum (Grover) | 256 bits (from memory) | claimed 128 bits: **half**, and at the quantum budget `2^64` only if no dedicated attack near `2^128` admits a quadratic speed-up (`decision-b-merkle-hash.md` H-1.3) |
| Stream `y_i` | a prover message whose stream gives a challenge in a bad set of probability `eps_k` (about `2^-158.8` at category 1) | `2^158.8` classical, `2^79.4` quantum: the IOP term, which binds | SHAKE256: capacity 512, 256-bit level (FIPS 202, from memory) | no claim above `2^128` for any output length ([B3] 4.1, 2.6); nothing quantum |

No number of the calculator changes with the hash (T-1): the adversary budgets are `2^128`
classical and `2^64` quantum, and a 128-bit claim meets the first. What changes is that for
BLAKE3 the figures above `2^128` and every quantum figure are random-oracle figures with no
designer statement behind them, as `decision-b-merkle-hash.md` H-1.2 and H-1.3 found for the
trees; a transcript on BLAKE3 extends that position from the commitment to the challenges.
Reduced-round results: `decision-b-merkle-hash.md` 9b (H-1.11) is the table; nothing was added
to it here.

### O-inner The node's batching transcript uses the default challenger (observation; for the referee)

`src/node.rs` opens main's batching transcript with `StdChallenger::default()`, which is
`SpbcsChallenger::new(.., [0; 64], &[], 0)` (`vendor/binius64/crates/transcript/src/
fiat_shamir/spbcs.rs`): a zero salt, an empty statement, and the same tag and label as the
outer proofs. Its inputs differ from every outer challenge input only by the length field
(zero against a non-empty identifier). Soundness does not need a salt, and the claims are the
first items, so no defect is asserted. Whatever the hash, this inner transcript should carry
its own label (or context) and the node circuit's identifier, so that it is a separate part
of the oracle by construction and not by a length field (TH-2, test iv). No rows: constants.

## 10. Proof obligations, tests, and what a referee should attack first

**Obligations if (c\*) is ever built** (none arises from keeping (a)):

| # | Obligation | Responsible | Acceptance |
|---|---|---|---|
| TH-1 | R-1 ruled | lead architect | the ruling recorded in the plan (SQ-50 (4) amended or confirmed) |
| TH-2 | MA-1 restated as MA-1' for BLAKE3 keys and streams in `qrom-compilation.md` 2.2, 2.8, 3 (H5, H9): four `derive_key` contexts, all outputs 32 bytes, the premise restricted to IV-constrained inputs as H-1.14 (ii) | lead agent | the B column names the four contexts; H5 and H9 met; the inner batching transcript has its own |
| TH-3 | Lemma X re-read for a `derive_key` stream context; the 1.00 bit entered in the calculator's row | referee; calculator maintainers | written verdict; revision note |
| TH-4 | Zero knowledge: Theorem 6.6 (3)'s salt terms re-read with the salt-first framing (512 bits through a 256-bit chaining value in stream points) | maths team, then referee | `zk-quantum.md` 2.2 amended or confirmed |
| TH-5 | Category: BLAKE3 keys are category 1 only (`decision-b-merkle-hash.md` H-1.5 applies to 32-byte keys as to digests); the category 3 row names a 384-bit key hash | lead agent | a category 3 row naming BLAKE3 for the transcript is refused by test |
| TH-6 | D-6 timed on a level-3 root, load under 8, before and after | system B | the figure, with the residue counted (C), replaces T-5 and T-9 |

**Tests the B team must add** (for (c\*); i, iv and v apply to (a) as built as well):

i. Known answers: every key and stream of one transparent and one zero-knowledge proof
   recomputed by an independent BLAKE3 (`vectors/check_spbcs.py` extended, with the
   compression function written from the specification as for 10.4).
ii. Each `B_c` equals the `blake3` crate's `derive_key` on `s || u || LE32(c)`; a stream is
   never taken with the extended-output reader (a test that fails if `finalize_xof` is used).
iii. In-circuit keys and streams equal native ones on mixed scripts, including a transcript
   that crosses 1, 2, 3 and 4 chunk boundaries and a key taken exactly at a chunk boundary
   and one byte either side.
iv. Separation: the same bytes under the four contexts and under the inner batching
   transcript's give five different outputs; a key is never the first 32 bytes of any stream.
v. Binding: a change of any byte of the salt, the statement or an item changes every later
   key and no earlier one (the existing `tests/transcript_binding.rs`, in every build,
   including the `johnson` build in which it was not run at `09a7b4e`).
vi. The row's `stream` and transcript-hash fields are in the statement identifier, and a
   proof made under one is refused under the other.
vii. Count (C): AND rows a key finalisation at stack depths 0 to 6, and a stream message of 1
   and of 192 challenges.

**What a referee should attack first:**

1. T-3. Is the reading of [B3] 4.2 and 4.3 right, that no stated result covers extended
   output? If a proof for the full-output mode exists in the literature after 2021, (c)
   reopens and (c\*)'s Lemma X bit is unnecessary.
2. T-5. The finalisation count (`1 + popcount`) and whether a different, still
   theorem-conforming arrangement of the challenge input avoids it. If the correction is
   wrong, B's 305,000 stands and T-9's comparison shifts towards the hash change.
3. T-6's claim that a BLAKE3 break already breaks system B's soundness today, and its
   converse: is there a weakness that would leave 64-byte `derive_key` collisions hard but
   break Fiat–Shamir over tree-mode inputs? (Then (c\*) adds real exposure beyond SQ-48.)
4. T-2. Is there an attack, not only a missing theorem, from length extension on nested
   SHA-256 challenge inputs, for instance through a prover message chosen to equal a padding
   block at a position where the schedule allows it? This record found none and did not
   search the schedule exhaustively.
5. T-4's salt-first reuse of the first block's chaining value: is it a value of the defined
   mode in the sense of H-1.7's exclusions?

## 11. For the lead architect

- **R-1.** Does "BLAKE3 inside proofs" (recorded: "only inside system B's proof trees") extend
  to system B's Fiat–Shamir transcript? This record reads the transcript as binding in
  function and recommends that it stay FIPS unless R-2 is answered for independence.
- **R-2.** Is removing the shared Keccak-f between the two proof systems worth a system B with
  no FIPS function in its proof layer? This is the security argument for (c\*); cost is not.
- **R-3.** If the hash-independent work leaves a level-3 root between 100 and 200 ms: restate
  E2's verification figure, or accept (c\*)?
