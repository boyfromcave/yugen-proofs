# Zero knowledge against quantum distinguishers: salts, Sharp–Grubbs Theorem 6.6 (3), and the record

Part of Yugen. Closes the analysis part of findings C-4 and C-8 of `CITATION-AUDIT.md`.
Recorded transactions must stay private against a future quantum computer, so the zero-knowledge
statement must hold against quantum distinguishers that keep querying the hash function after the
proofs are published. Revision 2 (2026-11-19), after the independent referee report
`qrom-zk-referee.md`: the statement now rests on a published theorem (Sharp–Grubbs Theorem 6.6 (3),
everlasting zero knowledge in the QROM for many adaptively chosen proofs), with Theorem 6.6 (4)
(unconditional witness indistinguishability) as the fallback without a query bound; the
composition over a wallet's proofs, the pool, the two systems and the recursion is written as
Theorem ZP; the scope of zero knowledge is leaf proofs (lead decision D-c).

**Amendment 2026-11-19 (revision 2.1; `zk-referee.md` R-1, at `7e79cef`).** Section 5 of revision 2 and the table of
section 3.1 said that system B's four fold trees are unsalted as built. That was **out of date when written**:
`yugen-proof-b2` commit `7de8da0` (2026-11-19 11:59, `VENDOR.md` change 35, "route S"), an ancestor of that
repository's head, salts **every fold-round tree and both round oracles** with the round salt length (512 bits at
category 1, `CAT1_SALT_BITS`; `iop/src/basefold/compiler.rs` 95-102, `iop-prover/src/fri/fold.rs` 298-316, verifier
`iop/src/fri/fold.rs` 169, 235, as `zk-referee.md` section 1 cites them). Route S is **built**; the published theorem's
salting hypothesis is met by B as built, as it is by A (every tree of the masked leaf salted with 8 words, 64 bytes).
B's terminal codeword is sent in full and has no tree; it belongs to `eps_hvzk^B`, not to salting. Sections 3.1 and 5
are rewritten accordingly below; no figure changes (the figure `2^-105.7` already counted the fold trees as salted).
Privacy still rests on `eps_hvzk^A` and `eps_hvzk^B`, **owed** (section 5.2), whose documents are not yet refereed.
`yugen-proof-b2/docs/parameters.md` lines 1941-1943 ("Not built: salts on the four fold trees") are stale (a builder's
fix, `zk-referee.md` R-2), and no B test yet asserts that the fold-tree digests are the salted hash (R-3).

**Amendment 2026-11-19 (revision 2.2; `zkq-te3-r8-referee.md` M-1, M-2, m-1, m-2, N-1, N-2, at `3cfd252`; not a
rewrite, the revision 2 figures below are kept as the record).**

1. **The transcript is built (M-2 was stale).** Both systems carry the spBCS transcript of Section 2 of
   `qrom-compilation.md`, natively and in circuit, read at `yugen-proof-a` `084fbdd` and `yugen-proof-b2` `395da08`
   (`git show HEAD:`): **A** `vendor/leanMultisig/crates/verifier/src/spbcs.rs` (tags `0x10`..`0x13` at lines
   61-64, header `tag || label || s || pre(x)` 351-360, stream `SHAKE256(0x13 || u || s)` 285-300, `distinct` 400,
   leaf and node digests 405-417), rows of `TranscriptKind::SpBcs` in `params.rs` 316-317 and 335-337, the
   in-circuit verifier `guests/e2/a_fs.py` 214-215, `c_open.py`, `h_sub.py`, test vector `tests/spbcs.rs` with
   `tests/vectors/spbcs-a-v1.txt`; **B** `vendor/binius64/crates/transcript/src/fiat_shamir/spbcs.rs` (tags `0x20`,
   `0x21`, `0x23` at 45-49, label `Yugen/spBCS/B/v1`, SHA-256 running key, SHAKE256 stream, 11-19), `src/params.rs`
   141-147 (framing version 2: positions de-duplicated in the proof, change 34), `src/prove.rs` 5-8, the node
   circuit's `.spbcs_message` gadget (census in `bench/results/census-after-20261119-n.txt`), vectors
   `tests/spbcs_vectors.rs`. Hypothesis row 1 of 3.1 is **met as built in form**; T-1 and T-2's transcript part is
   built. What is **not** at the profile is the salt lengths (item 2).
2. **Salt lengths as built against profile Y** (`decision-security-profile.md` 2.1: leaf A 80 B, leaf B 96 B, proof
   80 B). A: proof salt `SALT_BYTES = 64` (`spbcs.rs` 75), leaf salts `leaf_salt_words: 8` = 64 B (`params.rs` 226,
   335). B: proof salt `SALT_BYTES = 64` (`spbcs.rs` 53), leaf salts `CAT1_SALT_BITS = 512` = 64 B (`src/params.rs`
   156; allowed lengths `merkle_tree/mod.rs` 32: 256, 384, 512, 576, 768 bits, so **96 B = 768 bits is allowed but
   not selected**). Neither system is at profile Y as built; an agent is moving A to 80 B (not yet in A's head).
3. **The figures at the profile (M-1), recomputed (C, this amendment, a direct evaluation of the formula of 3.1;
   `n_pos` A `2^21.17`, B `2^23.25`, `eps_key = 2^-236.5`, `b = 32`, `L_leaf = 1,024` bytes per m-1), `Q = 2^37`
   leaf proofs, `t = 2^128`, `eps_hvzk` excluded:**

   | Salts (leaf A / leaf B / proof) | `eps_zk^A` | `eps_zk^B` | Theorem ZP | WI (6.6 (4), `L = 2^24`), A / B / both |
   |---|---|---|---|---|
   | **profile Y, 80 / 96 / 80 B** | **`2^-134.8`** | **`2^-153.0`** | **`2^-134.8`** + `2^37 (eps_hvzk^A + eps_hvzk^B)` | `2^-133.8` / `2^-195.7` / **`2^-133.8`** + `2^38 (...)` |
   | **as built, 64 / 64 / 64 B** | `2^-70.8` | `2^-68.7` | **`2^-68.4`** | `2^-69.8` / `2^-67.7` / `2^-67.4` |
   | A at 80 B, B as built | `2^-89.0` | `2^-68.7` | `2^-68.7` | `2^-133.8` / `2^-67.7` |

   The referee's figures (A `2^-134.8`, B `2^-153.0`, ZP `2^-134.8`, WI `2^-133.8`) are **confirmed**. At the
   profile the target `2^-128` is met, excluding `Q eps_hvzk`; **as built it is not** (`2^-68.4`): the as-built
   privacy figure depends on the salts actually built, and reaches the profile only when A's leaf and proof salts
   are 80 B and B's leaf salts 96 B (768 bits) and proof salt 80 B. At the profile the leading terms are A's leaf
   term and the proof-salt term `4 Q t / 2^(4 b_s) = 2^-153`. `Q eps_hvzk` is **still open** (the HVZK referee is
   running); no figure here bounds it.
4. **D-b restated** as the profile's 80 / 96 / 80 B (64 B is the record of revision 2).
5. **m-1.** `L_leaf` is the largest leaf encoding: 1,024 bytes (B's BLAKE3 framing, `qrom-compilation.md` B-4; A's
   level-0 leaf is 16 + 512 bytes plus salt). The second term of `eps_leaf` is `2^-250.3` at 64 B and `2^-314.3` at
   80 B: negligible at every length.
6. **m-2 (MA-0).** Theorem ZP needs one joint oracle assumption: **MA-0**: Keccak-256, SHAKE256 (A), SHA-256,
   SHAKE256, BLAKE3 `derive_key` (B) are modelled as **one** random oracle whose parts are disjoint by tag or
   function (A's `0x10`..`0x13`, B's `0x20`..`0x23` and the BLAKE3 contexts), equivalently independent oracles.
   MA-1 and MA-2' are its per-system restrictions. Added to ZP's hypotheses (3.3).
7. **N-1.** `q_S = 2 n_pos + N_msg + n_B`; `n_B = 0` without merges, which the transcripts as built do not use.
8. **N-2.** "Everlasting" bounds only the queries before the last proof; for a record growing for decades that is
   the adversary's whole budget until then, so `t = 2^128` is the reading used, and 3.4 (no query bound) is the
   fallback.

Status tags: **(P)** proven here, **(S)** read in a primary source (named), **(C)** computed
(`../soundness` revision 6, `--rev6`; `../qrom/test_numbers.py`), **(M)** from memory, **(U)** open.

## 0. Decisions and sources

Lead decisions (lead agent, 2026-11-19; open to the lead architect's review):
**D-b** (restated by amendment 2.2: profile Y, leaf A 80 B, leaf B 96 B, proof 80 B; the revision-2 text follows as record): 64-byte (512-bit) leaf salts on every tree of a leaf proof and a 64-byte proof salt in every
challenge input and stream point (the spBCS specification, `qrom-compilation.md` 2.3).
**D-c**: zero knowledge is required of leaf (wallet) proofs only (section 4).

Sources (read 2026-11-19; text extracted to a scratch directory outside every repository):

- [SG26] C. Sharp, P. Grubbs, "Faster and Smaller Anonymous Credentials from Standardized
  Signatures", Cryptology ePrint Archive, Paper 2026/2615: Section 6.1 (Definitions 6.1, 6.2, 6.3),
  6.2, Protocol 6.5, Theorem 6.6 (3), (4) and the text after it (p. 60); Definition H.6; Definition
  2.22; Appendix I.1 (Definition I.1, Lemma I.2, the leaf-term paragraph, the oracle's domain);
  **Section I.2 in full, with the proof bodies**: Theorem I.3 and its proof, Protocol I.4, Theorem I.5
  and its proof (hybrids, the two one-way-to-hiding steps, step 3's four terms), Theorem I.6 with
  Lemmas I.7, I.8 and their proofs; Section 8.4 (p. 77).
- [CMS19] Chiesa, Manohar, Spooner, ePrint 2019/834: Section 3.3, Lemma 7.3 and its proof (read for
  revision 1; used for the record, section 6).
- [CY] Chiesa, Yogev, "Building Cryptographic Proofs from Hash Functions" (version 1.2, March 25,
  2026; a copy fetched by an earlier session): Claims 3.4.1, 3.4.2, Lemma 17.3.1, Claims 17.3.2,
  17.3.3, Remark 18.6.2, Theorem 26.2.1 (read for revision 1).
- [BCS16] Ben-Sasson, Chiesa, Spooner, ePrint 2016/116: Definition 3.3, Lemma 3.4 and its proof.
- [D25] Diamond, ePrint 2025/1015: Section 4.1 (salts are necessary); Construction 4.1 and the
  simulator of Theorem 4.3 (steps 1 to 6, read for section 5).
- Code and project documents (S): leanVM `crates/verifier/src/params.rs` (`leaf_salt_words`),
  Binius64 `crates/iop/src/merkle_tree/mod.rs` (`LEAF_SALT_BITS = 256`); `yugen-proof-a/docs/recursion.md`
  (statement and witness of the sub-bundle and merge programs, BC-1, the salted-leaves row of its
  open items); `yugen-proof-b/docs/recursion.md` (statement / witness table);
  `yugen-proof-b2/docs/statement-layout.md`; the plan's data table (where each object lives).

Provenance:

| Result | Label |
|---|---|
| No statistical zero knowledge at salts as long as the digest (section 2.1) | **Published**: SG26 Section 8.4 (p. 77), "the expected statistical distance of an unopened leaf from uniform ... is `(1 - 2^-lambda)^(2^lambda)`, close to `1/e`, so statistical zero knowledge does not follow"; CY Claim 3.4.1 (both sides) |
| Lemma H, the per-leaf hiding term of a salted tree (section 3.1) | **Published**: SG26 Definition I.1, `eps_leaf` (its first term is CY Claim 3.4.1's bound, its second follows CY Claim 3.4.2's proof with McDiarmid and Lemma I.2; SG26 I.1, p. 130), applied per leaf in the proof of Theorem I.5 step 3 and Lemma I.7 (1). Revision 1 labelled it Adapted: corrected |
| Theorem 6.6 (3), (4) | **Published** (SG26), used as stated |
| Lemma M (classical, query-bounded; section 1) | **Adapted** from CY Lemma 17.3.1, Claim 17.3.2, Remark 18.6.2 (changes: any tree shape, the salt's position, one event for all leaves) |
| Grover cost of the 256-bit-salt attack (section 2.2) | **Original as far as checked** (necessity of salts: D25 Section 4.1; the `1/e` distance: SG26 8.4) |
| Theorem ZP (composition over the pool, the two systems and the recursion; section 3.3) | **Original (the Ycash developers, 2026)** as a composition; its parts are Theorem 6.6 (3) per system and two hybrids; the hybrid technique is SG26's own (proof of Theorem I.5, step 2 (ii): assignments applied on top of the oracle) |
| The node-witness check (section 4) | **Original** |
| Theorem ZQ (record, section 6) | **Adapted** from CY Theorem 26.2.1 and CMS19 Lemma 7.3; superseded |

---

## 1. Lemma M, classical, in full (unchanged; referee 2.1: holds)

**Setting.** A commitment tree as built in either system: leaves `l_y = H(enc(row_y, tau_y))`, `enc`
injective, the salt `tau_y` uniform in `{0,1}^s` and independent of everything else; inner nodes any
fixed function of their children's digests computed with `H`; root `rt`. An opening reveals, for the
opened set `I`, the rows, the salts and the copath digests. `U = [n] \ I`, `N_u = |U|`; `H` a random
oracle with `sigma`-bit output.

**Simulator.** `SimTree(I, (row_y)_(y in I))`: salts and digests of opened leaves computed with `H`;
`l_y` uniform for `y in U`; inner nodes recomputed (CY Remark 18.6.2).

**Lemma M (P).** For every `t`-query classical algorithm that chooses the rows (with oracle access),
receives the real or simulated (root, opening) and keeps querying, the statistical distance of its
outputs is at most `t N_u / 2^s + N_u^2 / 2^(s+1)`.

*Proof.* Condition on distinct salts (second term). Let `E` be the event that the algorithm queries
`H` at some `enc(row_y, tau_y)`, `y in U`. Outside `E` the `N_u` digests are uniform and independent
of the view except through the root and copaths, and the joint distribution is the simulated one.
A query hits a given unopened leaf with probability at most `2^-s` before the salts are drawn and,
outside `E` so far, after (CY Claim 17.3.2's two-phase argument; testing a candidate salt by
recomputing the path is itself a query at the leaf point, i.e. `E`; referee 2.1); a union bound
gives `Pr[E] <= t N_u / 2^s` (more exactly `1/(2^s - t)` a query). ∎ At `s = 256`, `t = 2^128`,
`N_u = 2^24`: `2^-104` (C).

## 2. Salts as long as the digest (256 bits) under a 256-bit hash

### 2.1 No statistical statement (Published)

SG26 Section 8.4 (p. 77, S): for digests and salts of `lambda` bits the expected statistical distance
of an unopened leaf from uniform, over the oracle, is `(1 - 2^-lambda)^(2^lambda)`, close to `1/e`,
"so statistical zero knowledge does not follow"; GordieHowe therefore uses leaf salts of twice the
digest. The same follows from CY Claim 3.4.1's two-sided bound (S). In SG26's terms: `eps_leaf` at
`b_l = b` has first term `1/2` a leaf, and `n_pos eps_leaf` is vacuous. Exact toy check of Claim
3.4.1 (C, `qrom/test_numbers.py` section 4): 0.25 and 0.316 at `s = sigma = 1, 2`. BCS16's Lemma
3.4 (`n 2^(-lambda/4 + 2)` for `2 lambda`-bit salts): `2^-38` at `n = 2^24`, not used.

### 2.2 A quantum attack at about `2^128` queries (Original as far as checked)

A zero-knowledge distinguisher holds the witness. **Hypothesis (stated per oracle, referee 2.3):**
every unopened row of the oracle is determined by the witness and the opened rows, i.e. the lane's
masking dimension equals its number of opened rows (Lemma E of `zk-hiding-commitment.md`: the `t_i`
random coefficients are in bijection with the `t_i` opened rows). Where a lane has more random
coefficients than opened rows, unopened rows are not determined and the attack weakens. Under the
hypothesis the distinguisher computes an unopened row for a candidate witness and runs Grover's
search for `tau` with `H(enc(row_y, tau)) = l_y`: about `(pi/4) 2^(s/2)` queries if the candidate is
right; for a wrong candidate a preimage of that form exists with probability about `1 - 1/e` a leaf,
so the test repeats on further leaves (`0.63^m` after `m`). At `s = 256` a recorded proof is
protected only by about `2^128` quantum oracle evaluations per tested candidate witness, a
category-1-like attack cost and no proof; low-entropy candidates (an amount, a recipient from a
short list) are what an observer would test. D25 Section 4.1 shows salts are necessary; the
Grover cost of the salted tree is the step added here.

### 2.3 A query-bounded quantum lemma for 256-bit salts: not pursued

From memory (M), one-way-to-hiding would give an advantage of order `q sqrt(N_u / 2^s)`: `2^-52` at
`q = 2^64`. Section 2.2 shows it cannot be much better; it is not pursued.

## 3. The zero-knowledge theorem: Sharp–Grubbs Theorem 6.6 (3)

### 3.1 The statement and its hypotheses, per system

**Theorem 6.6 (3) [SG26], as stated (S).** If the honest prover of the IOP is honest-verifier zero
knowledge with error at most `eps_hvzk` at every statement (Definition 2.22: the verifier's view is
`(x, theta, (a_i), qry(theta), ans)`, the challenges, the non-oracle messages and the answers **at
the queried positions only**), then the spBCS transformation is everlasting zero knowledge
(Definition 6.2) with respect to the simulator of Protocol I.4, with error at most

    eps_zk(t, Q) = 4 Q t / 2^(4 b_s) + Q (Q - 1) / 2^(8 b_s) + Q ( eps_key + eps_ov + eps_hvzk + n_pos eps_leaf )

in the QROM, against adversaries that make at most `Q` proof queries, each a pair `(x, w)` chosen
**adaptively** after their hash queries and earlier proofs (Definition H.6: "The notion is adaptive
and multi-theorem"), at most `t` hash queries before the last proof query and any number after it
(Definition 6.2). Here `eps_leaf = (1/2) sqrt(2^(8b)/2^(8 b_l)) + sqrt(ln N_leaf / (2 * 2^(8 b_l)))`
(Definition I.1; **Lemma H**), `eps_key = C(N_msg, 2) 2^(-8b)`, `n_pos` the oracle positions of the
proof.

| Hypothesis (where in SG26) | System A (leanVM, leaf) | System B (Binius64, leaf) |
|---|---|---|
| spBCS transcript (Protocol 6.5) with the proof salt `s` in every challenge input and stream point (Section 6.2; the proof of Theorem I.5 uses that leaves and nodes carry no proof salt and every other input carries exactly one) | **built** (amendment 2.2 item 1: `spbcs.rs`, tags `0x10`..`0x13`, distinct positions); proof salt 64 B as built, 80 B at the profile | **built** (amendment 2.2 item 1: tags `0x20`, `0x21`, `0x23`, framing v2 de-duplicated); proof salt 64 B as built, 80 B at the profile |
| Every leaf of every tree salted, `b_l > b`, salts independent and uniform per leaf (Protocol 6.5 step 1(b); Definition I.1; Lemma I.7 (1) uses a fresh honest salt per position) | every tree of the leaf is a W-I oracle with `leaf_salt_words` salt words: set to 8 words (64 bytes) | the two round oracles and every fold-round tree salted at 512 bits (`CAT1_SALT_BITS`), **route S built** (`yugen-proof-b2` `7de8da0`, change 35; amendment 2026-11-19, section 5); the terminal codeword is sent in full, no tree |
| HVZK of the IOP with error `eps_hvzk` at every statement (Definition 2.22) | **open**: obligations Z-A1 to Z-A6 (section 5) | **open**: Z-B1 to Z-B6 |
| Samplers succeed (`eps_ov`) | `eps_ov = 0` (`qrom-compilation.md` 2.4) | `eps_ov = 0` |
| Proof salt `b_s` bytes, digests `b` bytes | `b_s = 64`, `b = 32` | as A |
| Proof salts and leaf salts fresh per proof from the system CSPRNG | checklist item 6 of `zk-composition.md` | as A |

### 3.2 The error of one proof

With `b = 32`, `b_l = 64`, `L_leaf = 512` bytes: `eps_leaf = 2^-129 + 2^-250.8 = 2^-129.0`
(SG26 Section 6.3: the first term is `2^(-4(b_l - b) - 1)`; each further byte of leaf salt divides
the term by `2^4`). `eps_key = 2^-236.5` (A, `N_msg = 1,198`), `eps_ov = 0`. `n_pos` (every position
of every tree of a leaf proof, E, `soundness` revision 6): A `2^21.17`, B `2^23.25` (the round oracles
`2^17` and `2^20` elements at rate 1/8 and the four fold trees, salted). Per proof (`Q = 1`), for every
`t <= 2^128` (C):

| | System A | System B |
|---|---|---|
| `eps_zk(t, 1)` | `2^-107.8` + `eps_hvzk^A` | `2^-105.7` + `eps_hvzk^B` |
| Largest term | `n_pos eps_leaf` | `n_pos eps_leaf` |

### 3.3 Many proofs: a wallet, the pool, both systems and the recursion

Theorem 6.6 (3) is already a statement about `Q` adaptively chosen proofs sharing one oracle, so the
composition over a wallet's proofs and over every proof of the pool is the theorem itself, evaluated
at `Q`. What it does not cover is that each transfer carries **two** leaf proofs (one per system,
both on the same statement and witness) and that bundlers publish **node proofs** computed from
leaf proofs. Theorem ZP covers both.

**Theorem ZP (privacy of the published record) (P; Original as a composition).** Let an adversary
choose, adaptively and up to `Q` times, a statement and witness `(x_j, w_j)` of the wallet relation;
let the record contain, for each `j`, a system-A leaf proof and a system-B leaf proof of `x_j` from
`w_j`, and any node proofs computed by provers whose witnesses are functions of leaf proofs, earlier
node proofs, public inputs and public parameters only (hypothesis **N**), with `q_N` hash queries in
all before the last leaf proof. Let `q_A`, `q_B` bound the hash queries of one honest leaf prover of
each system and `q_S^A` those of system A's simulator per proof (`2 n_pos + N_msg`, Definition
I.1). Then for every adversary with `t` hash queries before the last proof and any number after it,
the record is simulated without any `w_j` (system A's and B's simulators of Protocol I.4, node proofs
computed honestly from the simulated leaf proofs) within

    eps_ZP  <=  eps_zk^A( t + Q q_B + q_N , Q )  +  eps_zk^B( t + Q q_S^A + q_N , Q ),

each term Theorem 6.6 (3) for that system.

*Proof.* Hybrid 0 is the real record. Hybrid 1 replaces every system-A leaf proof by the system-A
simulator's proof and its assignments. A distinguisher between hybrids 0 and 1 gives an adversary
`R_1` against system A's experiment of Definition H.6: `R_1` runs the adversary, sends each `(x_j,
w_j)` as a proof query, computes the system-B proof itself with `Prv_B(x_j, w_j)` (it knows `w_j`,
which the adversary chose), computes every node proof itself (hypothesis N: from the record and
public data), and passes the adversary's hash queries to the current oracle. System A's simulator
reprograms only system-A stream points (tag `0x13`), which no system-B input and no node input can
equal (`qrom-compilation.md` 2.2), so `R_1`'s B proofs and node proofs are distributed as in the
hybrid it emulates. `R_1` makes at most `t + Q q_B + q_N` hash queries before its last proof query
and any number after, and at most `Q` proof queries; its advantage is the distinguisher's, so the
difference is at most `eps_zk^A(t + Q q_B + q_N, Q)` (Theorem 6.6 (3)). Hybrid 2 replaces every
system-B leaf proof by system B's simulator's. `R_2` runs system A's simulator itself and applies its
assignments on top of its oracle, a query to `O[Reprog]` being one query to `O` (the step SG26 uses
in the proof of Theorem I.5, step 2 (ii), with Lemma I.10), and computes node proofs from the
simulated A proofs and the B proofs it receives; its hash queries before the last proof query are at
most `t + Q q_S^A + q_N`; the difference is at most `eps_zk^B(t + Q q_S^A + q_N, Q)`. Hybrid 2 is the
simulated record: no `w_j` is used (node witnesses are functions of the simulated leaf proofs and
public data by N). ∎

*Hypothesis added (amendment 2.2, m-2):* **MA-0**, one random oracle over every hash function of both systems with
disjoint parts (A's tags `0x10`..`0x13`; B's `0x20`..`0x23` and the BLAKE3 contexts). The separation step of
hybrid 1 ("no system-B input can equal a `0x13` input") is a statement about that one oracle.

**Numbers (record of revision 2; superseded by amendment 2.2 item 3; C, revision 6; `b_s = b_l = 64` bytes, `eps_hvzk` excluded, `eps_ov = 0`).** The
`t`-terms: with `q_A, q_B, q_S^A <= 2^26` (a leaf prover hashes every leaf and node of its trees once;
E), `Q = 2^20` and `q_N <= 2^60` (E), the effective `t` stays below `2^64.1`, and `4 Q t / 2^256 <=
2^-169.9`; the salt-collision term is `2^-472`. So the leaf term leads:

| | One proof | A wallet, `Q = 2^16` | The pool, `Q = 2^20`, `t = 2^64` (also `2^128`) |
|---|---|---|---|
| System A, `eps_zk^A` | `2^-107.8` | `2^-91.8` | `2^-87.8` |
| System B, `eps_zk^B` | `2^-105.7` | `2^-89.7` | `2^-85.7` |
| Theorem ZP (both) | `2^-105.4` | `2^-89.4` | **`2^-85.4`** + `2^20 (eps_hvzk^A + eps_hvzk^B)` |

The proof salt: the referee's figure for the salt term at the pool, `t = 2^64`, `Q = 2^20`: `2^-42`
at 32 bytes, `2^-106` at 48 bytes, **`2^-170` at 64 bytes** (C; `4 Q t / 2^(4 b_s)`). 64 bytes keep
the salt term below `2^-100` up to `Q t = 2^154`, so an adversary with `2^128` queries before the
last proof changes nothing; at 48 bytes it would be `2^-42` there. The leaf salt sets the pool
figure: 72-byte leaf salts give `2^-119.8` (A) and `2^-117.7` (B), 76 bytes `2^-135.8` and
`2^-133.7` (C): each byte divides it by 16, at 1 byte an opened leaf. The choice of the pool target
(`2^-85` at 64 bytes, or `2^-128` at 76) is the lead architect's; D-b's 64 bytes are what is
specified here.

### 3.4 Unconditional witness indistinguishability: Theorem 6.6 (4) (fallback)

**Theorem 6.6 (4) [SG26] (S).** Under the hypotheses of 3.1, the spBCS transformation is
unconditionally witness indistinguishable (Definition 6.3: `Q` triples `(x_j, w_(j,0), w_(j,1))`
chosen adaptively as functions of the whole oracle and earlier proofs, total encoding length at most
`L` bits) with error at most

    eps_wi(Q, L) = Q ( 2 n_pos eps_leaf + 2 eps_hvzk + eps_ov + eps_key + sqrt( ((L + 1) ln 2 + 2 ln(L + 1)) / (2 * 2^(8 b_s)) ) ).

No bound on hash queries at any time: this is the statement for "recorded transactions against a
future quantum computer" when the adversary's query count before the proofs cannot be bounded
(SG26 p. 60: "Part (4) therefore does not follow from Part (3)"). At the pool (`Q = 2^20`, `L = 2^24`
bits, upper figure) (C): A `2^-86.8` + `2^21 eps_hvzk^A`, B `2^-84.7` + `2^21 eps_hvzk^B`; the salt
term is `2^-244.8` a proof. The two systems compose by the triangle inequality as in Theorem ZP
(each hybrid switches one system's witness; node proofs by hypothesis N), giving `2^-84.4` +
`2^21 (eps_hvzk^A + eps_hvzk^B)`.

### 3.5 Where the non-adaptive premise went

Revision 1's Theorem ZQ fixed the witness before the oracle (CMS19 Section 3.3) and asserted that
"the wallet chooses its witness independently of the hash function". The referee showed this false
for node proofs (their witnesses are leaf proofs, functions of `H`) and doubtful for leaves (a note
tree hashed with the same function makes leaf witnesses depend on `H`; referee 2.5 (E1)). Both are
now outside the premise: Theorem 6.6 (3) lets the adversary choose `(x, w)` after its hash queries,
so a leaf witness may depend on `H` arbitrarily (the queries made to produce it count in `t`), and
node proofs need no zero knowledge (D-c, section 4); Theorem ZP's hypothesis N is what replaces the
premise for them.

## 4. Scope (D-c): zero knowledge of leaf proofs only; nothing secret in a node witness

Leaf (wallet) proofs must be zero knowledge. Node proofs (sub-bundle, merge, the root; both
systems) need not be: their witnesses are leaf proofs and child node proofs, which the bundler
receives and which bundlers publish anyway (wallet proofs to the audit feed for days, node proofs
in the sidecar; the plan's data table), and which are themselves zero-knowledge objects. Theorem ZP
needs only hypothesis N: **every node witness is a function of leaf proofs, child node proofs,
public inputs and public parameters.** Checked against the built node programs (S):

| Node witness item | System A (`yugen-proof-a/docs/recursion.md`) | System B (`yugen-proof-b/docs/recursion.md`; spec 0.3.2 statement) | Secret? |
|---|---|---|---|
| Leaf proofs | the leaf proof verified under `leaf_seed` (`verify_sub`) | "per leaf: ... its proof" | no: published to the audit feed; zero knowledge by Theorem 6.6 (3) |
| Leaf public inputs | the 280 bytes of `pi` other than the mode, as advice, range checked (BC-1) | "per leaf: its 20 public words" | no: nullifiers, commitments, anchor, fee, value balances, mode, registry root: in the block |
| Hints | in-circuit verification advice "read off the proof as it was made" | "two hint words" (the inverse used for PC-2, `nf_1 != nf_2`, computed from the public nullifiers) | no: functions of the proof and public inputs |
| Child node proofs and digests | the child's proof, its digests, depth, count, attribution records | "per child: its digest `D_j` and its proof" | no: sidecar and public statement |
| Seeds | `seed`, `leaf_seed`: the programs' Fiat–Shamir IVs bound to the parameter row | (verifying keys, fixed per circuit) | no: verifying keys |
| Attribution records, shares | host records in the statement (`attr`) | host-fee ranges over the public order | no: public in the bundle header |

**Finding: nothing secret enters a node witness** in either system as built. `recursion.md`
already records the consequence for salts ("The node's own proof need not be salted: its witness is
leaf proofs, which the audit feed publishes"). The check must be repeated whenever a node program
gains an input: task Z-N (section 7). Leaf salts and the proof salt are therefore required on leaf
proofs only; node proofs carry an empty leaf salt (soundness holds at every salt length) and, for a
single transcript module, the 64-byte proof salt.

## 5. System B's fold trees (route S built, change 35), and the open HVZK obligations

### 5.1 What the IOP's zero knowledge must cover

Theorem 6.6 (3) as published uses HVZK over the **queried positions** (Definition 2.22) and handles
every unopened position through its salted leaf: the simulator gives each unopened position a
uniform digest (Protocol I.4, step 2), and the cost is `n_pos eps_leaf` (Theorem I.5, step 3). An
unsalted tree has `eps_leaf >= 1/2` a leaf, so the published theorem needs every tree salted.
**As built (amendment 2026-11-19):** route S, below, is built in `yugen-proof-b2` at `7de8da0` (`VENDOR.md` change
35): every fold-round tree and both round oracles carry 512-bit salts at category 1, fresh per leaf from the leaf
prover's OS-seeded generator (`src/prove.rs` 188, as `zk-referee.md` section 1 cites it). Revision 2 of this section
said B's fold trees were unsalted as built; that was out of date (`zk-referee.md` R-1). The two routes, as they were
weighed:

- **Route S (published theorem as is; recommended).** Salt B's four fold trees with 64-byte salts,
  like every other tree of the leaf. Cost (E): 4 x 184 opened fold leaves x 64 bytes = **+47,104
  bytes (46 KiB) a B leaf proof**; a fold leaf of arity 4 (16 elements of 32 bytes = 512 bytes) grows
  from 9 to 10 SHA-256 blocks (`512 + 1 + 64 + 9` bytes), for the prover (`2^19.1` fold leaves) and
  per opened fold leaf in the node circuit. Then HVZK over the queried positions suffices, and
  `n_pos` counts the fold positions (it does already: `2^23.25`).
- **Route F (Adapted, record).** Keep the fold trees unsalted and prove the stronger HVZK in which
  the verifier's view contains the fold oracles **in full**. D25's simulator for Construction 4.1
  computes the fold oracles honestly, in full, from its simulated combined word `f''` (Theorem 4.3,
  simulator step 5, S), and the real `t'' = alpha t + t'` is uniform subject to the same linear
  condition as the simulated one, so the full fold oracles are identically distributed (P, for the
  BaseFold opening alone; the wrapper and the ring switch must be added). Theorem I.5's step 3 is
  then adapted: the unsalted trees are built from the simulator's full strings, their positions are
  removed from `n_pos`, and the HVZK error is that of the full view. This is an adaptation of the
  proof of a published theorem (Adapted: change to Protocol I.4 step 2 and Theorem I.5 step 3), not
  the theorem itself; it saves the 46 KiB.

The briefing's rule (a published theorem is preferred to an adapted proof wherever one applies)
selected route S, and route S is built (`7de8da0`); route F and obligation Z-B6 remain only as a record. Route S's
cost as built is recorded in `yugen-proof-b2/docs/parameters.md` 11.3 (the estimate above is not re-checked here).

### 5.2 Open obligations: `eps_hvzk` of each leaf IOP

Revision 1 stated "`zeta_IOP` (the excluded challenges of `zk-composition.md` 4.2) is below
`2^-240`". **Withdrawn**: no IOP-level honest-verifier zero-knowledge statement of either leaf is
established, so no value of `eps_hvzk` is claimed, and every figure of section 3 is stated with
`eps_hvzk` added and not filled in. The obligations, each with what discharges it:

| # | System A (leanVM leaf, W-I) | Discharged by |
|---|---|---|
| Z-A1 | Every pinned sumcheck matched to the lemma form of the masked sumcheck (W-6) | `zk-masked-sumcheck.md` W-6 section, per sumcheck; reference tests in `zk-lemma/` |
| Z-A2 | Wire audit: every value the prover sends in the pad ledger as padded or determined (checklist 12, 13), including SG26 Definition 2.22's non-oracle messages | `yugen-proof-a-zk` `tests/zk_view.rs` wire audit, rerun on the merged branch with the spBCS transcript |
| Z-A3 | M-3's statistical claim (the shared root; Katz's bound, M) | `zk-system-a-gaps.md` 9.2 with the bound sourced, or the shared root replaced |
| Z-A4 | Fraction layers of the bus GKR (untested) | a rank test in `zk-lemma/` on the fraction layer, as for the product layers |
| Z-A5 | The witness-free simulator through the system's own code (checklist A16) | `yugen-proof-a-zk` simulator test: proofs from the simulator verify, and a two-witness statistic on the final proof shows no distinguisher |
| Z-A6 | `eps_hvzk^A` as a number: the sum of the excluded-challenge events of `zk-composition.md` 4.2, each measured, at the rows' sizes | `zk-composition.md` 4.2 restated with the measure of each event; the calculator's `spbcs.eps_zk` then filled in |

| # | System B (Binius64 leaf, own zero-knowledge mode) | Discharged by |
|---|---|---|
| Z-B1 | The wrapper (IronSpartan) view as a whole | `yugen-proof-b2/docs/zero-knowledge.md`, a section on the wrapper's view with its simulator |
| Z-B2 | The pad-count guard of C-5 | `binius-extension-challenges.md` C-5 item, with a test that a short pad count is refused |
| Z-B3 | The excluded event `gamma = 0` (F-3) | its probability stated (`1/|K|`) in `yugen-proof-b2/docs/zero-knowledge.md` |
| Z-B4 | The ring switch's place in the pad ledger | `zk-composition.md` 5, with SG26 Section 5.5 (published zero-knowledge ring switching) compared |
| Z-B5 | The statistical (not only computational) form of each step (D25 Section 4.1 claims computational zero knowledge after salting) | per step in `yugen-proof-b2/docs/zero-knowledge.md`; the witness-free simulator test (checklist B15) |
| Z-B6 | Only for route F (not taken: route S built, `7de8da0`): HVZK with the fold oracles in full, for the whole leaf (BaseFold opening, wrapper, ring switch) | a section in `yugen-proof-b2/docs/zero-knowledge.md` extending D25 Theorem 4.3's step 5 to the full view |

## 6. Record: Theorem ZQ of revision 1 (superseded)

Revision 1 proved, for **one** proof with a witness fixed before the oracle (CMS19 Section 3.3), in
the CMS form, `zeta <= zeta_IOP + sum over salted trees N_u (2^(-(s - 256)/2) + sqrt(n_b) 2^(-s/2)) +
k^2/2^257`, carried to quantum distinguishers by CMS19 Lemma 7.3's argument (referee 2.5: this step
holds). It is kept only as a single-proof corollary in that definition: its premises (non-adaptive
witness, CMS form, `zeta_IOP` below `2^-240`) are respectively false for node proofs, withdrawn, and
unestablished, and it does not compose over a wallet's proofs (referee 2.5 (E2)). The salt table of
revision 1 (per proof `2^-40`, `2^-104`, `2^-136` at 384, 512, 576 bits) remains correct arithmetic
of Lemma H (C; `qrom/test_numbers.py` section 3).

## 7. Salt costs and tasks

**Costs (E).** Leaf salts 64 bytes: +32 bytes an opened leaf against the built 32. System A row 8 at
rate 1/4 (227, 161, 164, 180: 732 opened leaves): +23,424 bytes. System B round oracles (2 x 184
opened): +11,776 bytes; with route S also +47,104 bytes for the fold trees. Proof salt: +64 bytes a
proof. Hashing with the part tag: A's level-0 leaf (512-byte row, 64-byte salt, tag) 5 Keccak-f, a
later leaf 3, unchanged; B's mixed round-oracle leaf (16 + 32 + 64 + 1 bytes) 2 SHA-256 blocks, the
all-`GF(2^256)` leaf (32 + 32 + 64 + 1) 3 blocks, a fold leaf 10 blocks (route S). Salt generation:
from the system CSPRNG, +32 bytes a committed leaf (A about `2^21` leaves, B about `2^23`); a keyed
expansion of one seed per tree would keep memory flat but makes Lemma H hold only against
distinguishers that do not break the PRF, so the CSPRNG stays.

| # | Task | Acceptance |
|---|---|---|
| Z-1' | (amendment 2.2) Salts at profile Y: A leaf and proof salts 80 B (`leaf_salt_words = 10`, `SALT_BYTES = 80`); B leaf salts 768 bits (96 B) on every salted tree of the category-1 rows and proof salt 80 B | a test that a proof with the old 64-byte salts is refused by the new rows; the spBCS test vectors re-recorded; sizes updated; then amendment 2.2's profile row is the as-built figure |
| Z-1 | Leaf salts 64 bytes: A `leaf_salt_words = 8` on every tree of rows 3, 6, 8 and every salted row; B `LEAF_SALT_BITS = 512` | a test that a proof with 32-byte salts is refused by the new rows; leaf-size assertions and proof sizes updated; in-circuit leaf hash block counts as above |
| Z-2 | Route S for B: salt the fold trees | **built** (`yugen-proof-b2` `7de8da0`, change 35); open: a test that every fold-round commitment is the salted hash and the terminal is unsalted (`zk-referee.md` R-3), and the stale line of B's `parameters.md` struck (R-2) |
| Z-3 | The spBCS transcript with the 64-byte proof salt | **built in both systems** (amendment 2.2 item 1); the 80-byte proof salt is Z-1' |
| Z-4 | The open obligations Z-A1 to Z-A6, Z-B1 to Z-B5 (Z-B6 only for route F) | each closed in the document named, with its statistical error stated; then `eps_hvzk` filled in and Theorem ZP evaluated in full |
| Z-N | Hypothesis N rechecked whenever a node program gains an input | the table of section 4 updated in the same change |
| Z-R | External review of sections 3 to 5 | signed review sheet items |

## 8. Review sheet

| # | Statement | On paper | Computation | Open |
|---|---|---|---|---|
| 1 | Lemma M | yes | | |
| 2 | No statistical statement at `s = sigma` (SG26 8.4; CY 3.4.1) | sourced | toy exact expectation | |
| 3 | Grover attack at `2^128` per candidate, under the stated hypothesis | yes | | |
| 4 | Hypotheses of Theorem 6.6 (3), per system (3.1) | yes | | HVZK (5.2); salts at profile Y (Z-1'); the transcript is built (amendment 2.2) |
| 5 | Errors per proof, wallet, pool (3.2, 3.3); at the profile (amendment 2.2 item 3) | yes | `soundness` revision 6; amendment 2.2 by direct evaluation | `eps_hvzk` |
| 6 | Theorem ZP (two systems, node proofs) | yes | | review |
| 7 | Theorem 6.6 (4) fallback | sourced | revision 6 | `eps_hvzk` |
| 8 | Node witnesses hold nothing secret (section 4) | checked against the built programs | | Z-N |
| 9 | Route S / route F for B's fold trees | yes | sizes (E) | the lead architect's choice if route F |
