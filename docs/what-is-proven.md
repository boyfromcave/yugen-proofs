# What is proven: every soundness and zero-knowledge claim, with its status

Part of Yugen. `yugen-proofs`, 2026-11-19, at calculator revision 10.2. This page is what the plan and the
specification cite. It states each claim the project makes for system A (leanVM, WHIR over binary additive codes),
system B (Binius64) and the proof tree, with its figure (category 1 unless stated), its status and where its proof is.
It adds no result; every entry points to the document that carries it. Provenance labels are in those documents and in
`REFERENCES.md` Part 3. **Revision 2 (2026-11-19)** applies `qc-and-status-referee.md` (findings W-1 to W-7, its
sections 4 and 5) and the dated correction below. **Revision 3 (2026-11-19)** records the referee reports
`theorem-s-referee.md`, `knowledge-and-census-referee.md`, `zk-referee.md`, `pbatch-code-referee.md` and
`guest-merge-referee.md` in the rows they affect, and the referee queue (section 6) as it now stands.

**Status words.** **Proven**: a written proof exists, under the named modelling assumptions only, nothing it rests on
is owed, **and a referee report that passed it is named in the row's Refereed column**. **Written, unrefereed**: a
written proof exists and nothing it rests on is owed, but no referee report has passed it. **Conditional**: a written
proof of the implication exists, but the claim also rests on something unproven or owed (named). **Stated**: the
claim and its argument are written down, but part of it is an estimate or a sketch (named), not a written proof.
**Owed**: no written proof yet; the obligation is listed in section 5. **Status not established**: the documents do
not let this page say. "Refereed" means an internal referee report in `docs/` with its verdict; no claim has had an
outside review.

**The rule (revision 2, `qc-and-status-referee.md`).** A row may say "proven" only if a referee report is named in the
row. A row whose proof has not been refereed says "written, unrefereed" or weaker, however complete the proof looks.

**Correction, 2026-11-19 (`zk-referee.md`, at `7e79cef`).** `qc-and-status-referee.md` finding W-2 asked this page to
state that system B's fold trees are unsalted as built, quoting `zk-quantum.md` section 5 and
`yugen-proof-b2/docs/parameters.md` ("Not built: salts on the four fold trees"). Both were out of date: `yugen-proof-b2`
commit `7de8da0` (2026-11-19 11:59, `VENDOR.md` change 35, "route S"), an ancestor of that repository's head, salts
every fold-round tree and both round oracles (512-bit salts at category 1). The zero-knowledge referee withdrew the
finding (`zk-referee.md` section 1, R-1) and the lead architect confirmed it. Rows Z-2 to Z-4 below state route S as
built; `zk-quantum.md` carries a dated amendment (revision 2.1). `qc-and-status-referee.md` is left as written.

**Two facts behind every row.** (1) Every hash-based figure is in the random-oracle model (ROM, classical) or the
quantum random-oracle model (QROM), with the transcript hashes modelled as one random oracle: **MA-1** (Keccak-256 and
SHAKE256 in A, SHA-256 and SHAKE256 in B) and **MA-2'** (B's BLAKE3 `derive_key` leaves and nodes). (2) The compiler
theorem is C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, ePrint
2026/2615 [SG26], Theorem 6.6 and Appendix I, **a preprint** (Published, used as stated).

**What this page covers, and what it does not.** This page covers "a witness for the relation exists and is hidden".
It does not say that the relation means what the specification says (Falcon verification, the key commitment), nor
what the public data reveal, nor the protocol layer (note encryption, private retrieval, the turnstile and pause
rules). Those claims are on the sibling page `what-is-claimed-elsewhere.md`, with their status by the same rule; the
boundary rows are in section 7.

## 1. Soundness of one proof

| # | Claim | Figure | Status | Conditional on | Proof | Refereed |
|---|---|---|---|---|---|---|
| S-1 | A's opening rounds (plain WHIR, binary additive codes, unique decoding) are round-by-round sound (Theorem S0) | each certified row's weakest round meets its need, 157.0 to 158.8 bits | proven (soundness) | BCIKS20 Theorem 1.6 (Published) | `whir-additive-soundness.md` 5 | `qrom-zk-referee.md` 3.1: holds (a careful sketch) |
| S-1k | The same rounds are round-by-round **knowledge** sound | `eps_i^k = eps_i` | **conditional** (on the re-read of K-A's revision) | Lemma K-A: the extractor is decoding of oracle 0, against [SG26] Definition 2.20 | `lemma-k-a.md` 3 (revision 2026-11-19) | `knowledge-and-census-referee.md`: K-A pass with conditions (M-A1, m-A1, m-A2), applied in `lemma-k-a.md` revision 2026-11-19, pending a re-read |
| S-2 | A's masked-leaf opening W-I is round-by-round sound, unique decoding (Theorem S) | as S-1 for rows 6, 8 | proven (soundness), corrections applied | BCIKS20 Theorems 4.1, 1.6 (numbering of the ePrint 2020/654 revision of July 3, 2021; 1.7 in ECCC TR20-083; amended 2026-11-19, `CITATION-AUDIT.md` C-41) | `zk-wi-soundness.md` 5 with the dated amendments M-1, m-1 to m-3 | `theorem-s-referee.md`: **holds, pass with corrections** (M-1, m-1 to m-3), applied in `zk-wi-soundness.md` (`72464f2`) |
| S-2k | W-I is round-by-round **knowledge** sound | `eps_i^k = eps_i` | **conditional** (as S-1k) | Lemma K-A with Theorem S (hand-off: "K-A's state AND Theorem S not doomed", m-A1) | `lemma-k-a.md` 2, 3 | as S-1k |
| S-3 | A's rounds outside the openings (sumcheck, bus GKR, Keccak reduction, gadget) have the stated soundness errors | row 8: 412 messages outside the opening, worst `2^-235.00` (bus fingerprint); census 445 (row 8), 411 (row 7), equal to the built verifier's counts | **conditional** (on the re-read of the census revision) | the census per message (`round-census-a.md`); row 9 counted only where measured (`2^25`, `2^27`): the extrapolated counts are withdrawn and row 9 above `2^27` is "not measured — refused by the build above `2^27`" (M-A2); `OTHER_ROUNDS = 512` stays the certified count; the zero-knowledge rounds' states (`zk-wi-soundness.md` Lemma 6, 6.3) not refereed; knowledge form: K-A | `round-census-a.md`; `soundness/census/`; `zk-system-a-gaps.md` 11; sumcheck rounds: [GKR15] Lemma 2.5 (per-round step); GKR layers: [GKR15] Section 3.3 structure; other draws: Schwartz-Zippel (amended 2026-11-19, `citation-check-lfkn-gkr.md`) | `knowledge-and-census-referee.md`: census A **pass with conditions** (M-A2, m-A3), applied in `round-census-a.md` revision 2026-11-19, pending a re-read; `theorem-s-referee.md` M-3 (the census was its request) |
| S-3a | Lemma RS: A's ring switch has error `2/|E|` (`GEN` generates `GF(2^64)`) | `2/|E|`; with `lambda`, at most `513/|E|` (247.00 bits) | proven | - | `round-census-a.md` 2.6 | `knowledge-and-census-referee.md`: **pass** (checked in full, `x^(2^64) = x`, `x^(2^32) != x` computed) |
| S-4 | B's unique-decoding opening (rows 192, 174, 235, 385 queries) is round-by-round sound (Lemma UD) | as S-1 | proven | WHIR Lemma 4.10, BCIKS20 Theorem 4.1, DKT26 Lemma 6.5 (elementary, read) | `binius-johnson-row.md` 6 | `johnson-row-referee.md`: holds |
| S-5 | B's repeated openings of one position add nothing (Theorem D) | 0 bits | proven | conditions D-1 to D-5 on the verifier | `lemma-d-duplicate-openings.md` 4 | `lemma-d-referee.md`: pass with conditions |
| S-6 | B's batching reduction composes with the larger per-round error (Lemmas P, R) | in B's round list | proven | - | `decision-b-parallel-batching.md` | `b-batching-and-hash-referee.md`: pass (L-1, L-2 corrections) |
| S-7 | B's rounds outside the openings: soundness errors stated | in B's round list | **stated** | degree bounds by Schwartz–Zippel with about 100 bits of room at 256-bit challenges; **the round census is an estimate, not a written proof**: the mask round's count is "unconfirmed against the Blueprint" (`binius-extension-challenges.md` R-7), until T-1; knowledge form: Lemma K-B (conditional on R-8, K-B.2) | `binius-extension-challenges.md`; `b-round-census.md`; `lemma-k-b.md` | partial: `johnson-row-referee.md` and `-2` (ring switch J1, Lemma K hold); census B: `knowledge-and-census-referee.md`, **pass with conditions** (D-4 unexplained, cannot move a figure; R-8 open); Lemma K-B: same report, **pass with conditions** (K-B.2 / R-8 open; m-B1, m-B2 and M-A1 applied in `lemma-k-b.md` revision 2026-11-19, pending a re-read) |
| S-8 | One proof is adaptively knowledge sound in the ROM ([SG26] Theorem 6.6 (2), Theorem I.16 (2)) | hash part 121.89 bits a proof; IOP part from S-1 to S-7 | conditional | K-A, K-B (written and refereed, pass with conditions applied, re-read pending; K-B also R-8); T-1; MA-1, MA-2'; [SG26] a preprint | [SG26] pages 58, 142 to 143 (Published) | the application: `rev10-referee.md`, pass (figures reproduced) |
| S-9 | One proof is adaptively knowledge sound in the QROM ([SG26] Theorem I.16 (1)) | IOP 76.72 (A) / 77.60 (B), hash 80.40 bits against 64 | conditional | as S-8 | [SG26] page 142 (Published) | as S-8 |
| S-10 | Every certified category-1 row meets the classical need for every `t` (every-t convention) | A: 6 of 20 rows certified, 14 meet only under the `k_q` guard until T-1 reports; B: 4 of 4 | conditional | S-1 to S-9; `c'`, `k_q` estimates until T-1 (partly delivered for B, `yugen-proof-b2` `543c808`; this page not yet updated from it) | `soundness/` revision 10.2; `decision-qrom-counting.md` 0, 7 | revision 10: `rev10-referee.md`, pass with conditions; revisions 10.1, 10.2: no. The counts "6 of 20 / 14 / 4 of 4" were not recomputed by `qc-and-status-referee.md` (W-7) |

## 2. The proof tree (20,000 proofs; one output tree)

Every tree row rests on `lemma-tree-extraction.md` **revision 3** (unrefereed; *revision 5.1, 2026-11-20, draft, section 6b: revision 4 refereed in `tree-extraction-rev4-referee.md` (pass with conditions R4-1 to R4-8, applied in revision 5); revision 5 refereed in `tree-extraction-rev5-referee.md` (`cabb19c`, pass with conditions R5-1 to R5-4, applied in revision 5.1, not re-refereed). Shape 4/4/5 with stop `N + 4`, B's internal nodes (bound 8,191, stop 8,193), H_int in H-BIND, the fold's two passes conditioned on the root discharge, and a per-query batching term `(t + K) eps_batch,max`, `eps_batch,max = 151 / |F_c|` (about `2^-248.76` a query at `GF(2^256)`; revision 4's `2^-107.8` sum is withdrawn). The fold is refused without `challenge256` (`yugen-proof-b2` `0613c6c`), so B's tree figures exist only for the 256-bit challenge build; no stated bound drops for `cat1t`. The root discharge's random-point check ran in `vfinal` (revision 5.1, 6b (d)); its C2 equivalence obligation stays open. Revision 5.2 (`b9836a8`) applies R51-1 to R51-3 and is refereed **PASS** for section 6b (`tree-extraction-rev51-referee.md`, section 4): the 4/4/5 shape, B's internal nodes, H_int and the fold's argument are refereed implications. The rows stay **conditional** (K-A, K-B, C2 including the root discharge's equivalence, H-BIND), and revision 3's SHAPE-VIOLATION / TE.3 was refereed in `te3-referee.md` (pass with conditions TE3-1 to TE3-5, applied in revision 5.3); the tree rows stay conditional on C2, K-A, K-B, T-1, C-4 and H-BIND*; revision 2 refereed in
`qc-and-status-referee.md`, pass with conditions T-1 to T-4, which revision 3 applies). Every tree row is conditional
on K-A and K-B (written and refereed 2026-11-19, pass with conditions, conditions applied, re-read pending; K-B also
on R-8), on **H-BIND**, now the collision resistance of the concrete statement-digest functions (a
standard-model assumption; it excludes SHAPE-VIOLATION, Lemma TE.3), and on condition **C-4** (depth and proof count
bound through the statement digest): **met by design, by search, not audited** (an audit owed, section 5).

| # | Claim | Figure | Status | Conditional on | Proof | Refereed |
|---|---|---|---|---|---|---|
| T-a | The tree extractor ends, for every accepted root, with a compliant tree of witnesses, the named event C2-VIOLATION or the named event SHAPE-VIOLATION, except with probability `t eps_max + sum_v |J_V,v| eps_v + c'_max (t + K)^2 / 2^(8b)` (Theorem TE'); SHAPE-VIOLATION has probability at most `eps_bind` (Lemma TE.3) | the bound | **conditional** (the implication is proven; K-A, K-B owed) | K-A, K-B; T-1 (H-DS); H-BIND (the statement-digest binding of `qc-and-status-referee.md` T-1); C-4 as built; [SG26] | `lemma-tree-extraction.md` 3, 6 | revision 1: `tree-extraction-referee.md`, pass with conditions; revision 2: `qc-and-status-referee.md`, pass with conditions; revision 3.1 + 6b (SHAPE-VIOLATION, Lemma TE.3, H-BIND): `te3-referee.md` (`1056ea6`), pass with conditions TE3-1 to TE3-5, applied in revision 5.3 (not re-refereed; row stays conditional on C2, K-A, K-B, T-1, C-4 (unaudited) and H-BIND); section 6b (4/4/5, B internal nodes, fold terms) at revision 5.2: `tree-extraction-rev51-referee.md`, **pass** (implication refereed; row stays conditional) |
| T-b | A tree whose every proof is published and verified natively is knowledge sound (Corollary TE-X): knowledge soundness of a batch of published proofs on one table | the bound of T-a | **conditional** (the implication is proven; K-A, K-B owed); **no C2** | as T-a | `lemma-tree-extraction.md` 6 | revision 2: `qc-and-status-referee.md` T-3, correct classically; quantum form Corollary TE-X-Q **sketched** (section 9), unrefereed |
| T-c | The chain's recursion tree (root proof published, inner proofs witnesses): `Pr[some published leaf statement is false and no C2-VIOLATION]` is at most the bound of T-a plus `eps_bind` (Corollary TE-S) | the bound of T-a plus `eps_bind` | **conditional** | **C2** (as the joint probability above, never as a conditional probability); K-A, K-B; T-1; H-BIND (collision resistance of the concrete statement digests, which also carries the node count of T-a; `qc-and-status-referee.md` T-1, W-5); C-4 as built | `lemma-tree-extraction.md` 7 | H-BIND restated per `qc-and-status-referee.md` T-1; revision 3 unrefereed; H_int and B's root-discharge conditioning at revision 5.2: `tree-extraction-rev51-referee.md`, **pass** (row stays conditional on C2) |
| T-d | No query count moves: the certified needs give the IOP part of T-a at every `t` (Corollary TE-F (a)) | 0 bits | **conditional** (the arithmetic is proven; K-A, K-B owed) | as T-a; for A, `guest-merge-referee.md` K-1' (prover-chosen `N_msg`) and K-2' (calls above `k_q` on the wire path), MAJOR, open | `lemma-tree-extraction.md` 7 | arithmetic: `tree-extraction-referee.md` F-5, reproduced |
| T-e | Classical hash part of the tree | **121.89 bits** (Theorem TE'); 114.74 printed beside it (per-proof union) and used by the proven-basis check | **conditional** | C2, K-A, K-B, T-1, H-BIND | `lemma-tree-extraction.md` 7 (b); calculator 10.2 | figures reproduced (`tree-extraction-referee.md` F-5); restatement: `qc-and-status-referee.md`, no figure moves |
| T-f | Category 1's classical hash part | digest 256 bits = 2 x 128; generic collision `2^128` | attack-cost basis (condition H), not a theorem | the attack rule (`decision-security-category.md` 3.5) | `decision-qrom-counting.md` 7.3 | `rev10-referee.md`: the ruling's factual basis stands |
| T-g | Tree QROM level, **claimed** (per-proof union) | **69.58 (A) / 70.45 (B)** against 64; hash part 75.63 | **conditional** (derived under C2; not a proven QROM figure) | C2, K-A, K-B, T-1, H-BIND; [SG26] Theorem I.16 (1) (preprint); [CMS19] Lemmas 5.9, 5.10 | `qrom-compilation.md` 5; calculator | arithmetic: `rev10-referee.md`, pass |
| T-h | Tree QROM level, one-table form (Proposition TE-Q', bounding FAIL or DEVIATION; printed beside T-g, not claimed) | 76.72 / 77.60; hash 80.40 | **conditional** | as T-g, and Lemma QC | `lemma-tree-extraction.md` 9 | revision 1 (TE-Q): pass with conditions; revision 2 (TE-Q'): `qc-and-status-referee.md`, pass with conditions (Q-2, Q-3 applied in revision 3) |
| T-i | Lemma QC: a classical query after a database measurement is lazy sampling up to `10 / 2^n` | term `log2` -222.91 (A), -223.09 (B) | proven (from [CMS19] Lemma 3.2, whose Appendix A proof was not read) | - | `lemma-tree-extraction.md` 9a | `qc-and-status-referee.md` section 1: **pass** (both cases re-derived, numerical check) |
| T-j | Black-box composition (Corollary TE-bb) | +2.3 to +3.9 bits a round if used | **conditional** (the implication is proven; K-A, K-B owed); **not used** | as T-a | `lemma-tree-extraction.md` 8 | arithmetic confirmed (`tree-extraction-referee.md` section 2) |

No unconditional QROM figure exists for a tree whose inner proofs are witnesses; C2 cannot be removed by any
random-oracle proof (`tree-extraction-referee.md` 1.1).

**How to read "conditional on C2"** (`qc-and-status-referee.md` T-2, W-6; `lemma-tree-extraction.md` 6). Every tree
statement is a **joint** probability, `Pr[bad outcome and no C2-VIOLATION] <= ...`, never a conditional one: the event
C2-VIOLATION is bounded by nothing, and in the model it is not small (for the honest tree, inner proofs made with the
concrete hash and the root checked against the oracle, it is essentially 1). A reader **may** conclude: the root
proof alone is knowledge sound; every way of cheating that does not pass through a child the native verifier rejects
is bounded; the tree is sound to the stated level if C2-VIOLATION is empty, which in the deployed system is
in-circuit / native verifier equivalence. A reader **may not** conclude: that a random-oracle proof of the recursion
tree exists with a small gap; that `Pr[C2-VIOLATION]` is small in the model; or that passing equivalence tests
**discharges** C2 (they make the event empty in the deployed system, where there is no theorem, not in the model,
where the theorem is).

## 3. Candidate rows (system B, Johnson regime; never certified)

| # | Claim | Figure | Status | Conditional on | Proof | Refereed |
|---|---|---|---|---|---|---|
| J-1 | B's 107 / 80-query rows (111 / 82 under every `t`) are round-by-round sound and knowledge sound on the DKT26 route (Lemmas F1', U, J1, J2, J3, F, UD, K) | query round 152.97 against 152.52 bits (book need) | **conditional** | DKT26 Theorem 4.4, Corollary 6.6, Lemma 3.3 (ePrint 2026/2056, a preprint); build properties H7, H8' | `binius-johnson-row.md` 2 to 7 | `johnson-row-referee.md`; `johnson-row-referee-2.md`, pass with conditions C-1 to C-7 |

## 4. Zero knowledge (leaf proofs only; decision D-c: node proofs carry no secret)

Salting as built (`zk-referee.md` section 1): **A**: every tree of the masked leaf (rows 6, 8) salted with 8 words
(64 bytes), salts and masks from the caller's `zk_seed` through SHAKE256 (A's generator finding S-1 of
`yugen-proof-a/docs/parameters.md`, computational; the wallet must draw the seed itself, `zk-referee.md` R-4);
**B**: route S built (`yugen-proof-b2` `7de8da0`, change 35): the witness and mask round oracles and every fold-round
tree salted at 512 bits at category 1; the terminal codeword is sent in full (part of `eps_hvzk^B`). Node proofs are
transparent and carry no secret (hypothesis N).

| # | Claim | Figure | Status | Conditional on | Proof | Refereed |
|---|---|---|---|---|---|---|
| Z-1 | No statistical zero knowledge at salts as long as the digest | - | proven (Published, [SG26] 8.4) | - | `zk-quantum.md` 2.1 | `qrom-zk-referee.md` 2: holds |
| Z-2 | One leaf proof is everlasting zero knowledge against quantum distinguishers ([SG26] Theorem 6.6 (3)) | *amended 2026-11-19 (`zk-quantum.md` 2.2):* at profile Y (80 / 96 / 80 B salts), `Q = 2^37`, `t = 2^128`: A **`2^-134.8`** + `2^37 eps_hvzk^A`, B **`2^-153.0`** + `2^37 eps_hvzk^B`; **as built (64 B salts on both)** A `2^-70.8`, B `2^-68.7`, below the target; record (64 B, one proof): A `2^-107.8`, B `2^-105.7` | **conditional** | *2026-11-19:* the spBCS transcript is **built** in both systems (`zkq-te3-r8-referee.md` M-2 was stale; file:lines in `zk-quantum.md` 2.2 item 1); the as-built figure reaches the profile only with A's 80 B leaf and proof salts and B's 96 B leaf and 80 B proof salts (task Z-1'); MA-0 for ZP; `Q eps_hvzk` open (HVZK referee running). Earlier conditions: A: every tree salted (64 bytes, built), A's generator finding S-1, `eps_hvzk^A` **owed** (Z-A); B: route S built (salted witness, mask and fold trees, `7de8da0`), `eps_hvzk^B` **owed** (Z-B); both: the HVZK documents not yet refereed; the spBCS transcript with the 64-byte proof salt (T-1); the category-1 row's 512-bit leaf salts (present: `CAT1_SALT_BITS`; the default row is 256 bits, where Z-1 applies); MA-1, and MA-2' for B's BLAKE3 leaves | `zk-quantum.md` 3.1, 3.2 (revision 2.1) | route assessed in `qrom-zk-referee.md` 4; salting as built: `zk-referee.md` section 1; the application in revision 2: none; referee engaged 2026-11-19 (queue item 6) |
| Z-3 | The published record (both systems, the pool, node proofs) is simulated without witnesses (Theorem ZP) | *amended 2026-11-19:* profile Y, `Q = 2^37`, `t = 2^128`: **`2^-134.8`** + `2^37 (eps_hvzk^A + eps_hvzk^B)`; as built (64 B salts) `2^-68.4`; record: `2^-85.4` at `Q = 2^20`, 64 B | **conditional** | Z-2; hypothesis N (node witnesses are functions of public data; confirmed against both builders' documents by `zk-referee.md`, not re-derived from the node circuits) | `zk-quantum.md` 3.3 | none (Theorem ZP is new and unread); referee engaged 2026-11-19 (queue item 6) |
| Z-4 | Unconditional witness indistinguishability, no query bound ([SG26] Theorem 6.6 (4)) | *amended 2026-11-19:* profile Y, `Q = 2^37`, `L = 2^24`: **`2^-133.8`** + `2^38 (eps_hvzk^A + eps_hvzk^B)`; as built `2^-67.4`; record: `2^-84.4` at `Q = 2^20` | **conditional** | as Z-2: salting built on both systems; `eps_hvzk^A`, `eps_hvzk^B` owed (Z-A, Z-B), HVZK documents not yet refereed | `zk-quantum.md` 3.4 | none for revision 2; referee engaged 2026-11-19 (queue item 6) |
| Z-5 | Masked sumcheck in characteristic 2 is perfect HVZK (staircase mask; Theorems 1, 2; Corollaries A, B) | exact | written, unrefereed; tests `zk-lemma/` | - | `zk-masked-sumcheck.md` 3, 4 | none; referee engaged 2026-11-19 (queue item 5) |
| Z-6 | W-I hides the committed rows (zero-knowledge encoding on an additive domain; salted leaves) | per `zk-hiding-commitment.md` 8 | written, unrefereed; tests `zk-commit/` | Lemma E's domain condition | `zk-hiding-commitment.md` 3, 6.2 | none (read for coverage only by `zk-referee.md`; R-6: worked examples restated at the current counts); referee engaged 2026-11-19 (queue item 5) |
| Z-7 | A leaf proof's components compose to HVZK with error `zeta_IOP` (Theorem C, pad ledger) | no number claimed (withdrawn) | **owed** as a number | Z-A6 | `zk-composition.md` 4.2 | none; referee engaged 2026-11-19 (queue item 5) |
| Z-8 | Classical query-bounded salt lemma (Lemma M) | - | proven (Adapted) | - | `zk-quantum.md` 1 | `qrom-zk-referee.md` 2: holds |

## 5. Open obligations (what is owed, one line each)

| Obligation | What is owed |
|---|---|
| C2 | Not dischargeable by proof, and not discharged by tests. What is owed instead: in-circuit / native verifier equivalence of every guest, which empties the event in the deployed system (A: `guest-masked-referee.md`, `guest-pstar-referee.md`, pass with conditions; A's merge of seven: `guest-merge-referee.md`, sound, M-1 and M-2 open; B's guest: no report on the guest as a whole, partial in `lemma-d-referee.md`, `b-batching-and-hash-referee.md` and `pbatch-code-referee.md` (P-sh code **pass**, its in-circuit equivalence pass, vendored channel not read); referee queue item 3). *Revision 4 (`lemma-tree-extraction.md` 6b (d)):* five new B guests owe equivalence: internal, top, internal-0, top-0 node circuits and the fold's in-circuit batching verifier; none built as one place yet, no report |
| K-A | Written (`lemma-k-a.md`), refereed (`knowledge-and-census-referee.md`, pass with conditions M-A1, m-A1, m-A2; applied 2026-11-19). Owed: the re-read of the revision; the zero-knowledge rounds' states (`zk-wi-soundness.md` Lemma 6, 6.3) refereed as pending claims; row 9's `j_v` measured before a stack other than `2^25` / `2^27` is admitted |
| K-B | Written (`lemma-k-b.md`), refereed (same report, pass with conditions; M-A1, m-B1, m-B2 applied 2026-11-19). Owed: the re-read; K-B.2 (R-8, lifted oracles), K-B.3 (TE' wording), K-B.4, K-B.5 |
| T-1 | From the builders: each shape's `k_q`, `c'` (`N_msg`, `m`, `n_J`) reported by the transcript module (partly delivered for B, `yugen-proof-b2` `543c808`); the round census of S-3 and S-7 confirmed; domain separation across systems (H-DS, injective encodings, items 7.6 (g) and 10, including A's unframed Keccak-256 statement wrappers against the part tags); the transcripts' fit to [SG26] Protocol 6.5; `decision-qrom-counting.md` 7.6 |
| C-4 audit | Level and proof-count binding (`lemma-tree-extraction.md` 3): **met by design, by search, not audited** (`qc-and-status-referee.md` T-1). Owed: an audit of both node circuits (`yugen-proof-a` `guests/bundle_merge_e2.py`, `bundle_sub_e2.py`, rules BC-3 to BC-5; `yugen-proof-b2` `src/bundle.rs`), of the native `Tree::check` on the root's proof count, and a test pinning B's consensus constraint-system digest to the all-on rule set (`depth_bound`, `depth_max` have "off" switches; T-5) |
| H-BIND | Collision resistance of the concrete statement-digest functions computed inside the fixed relations (`H_bundle-node`, A's bound IV, B's constraint-system digest, the chain's leaf-statement digests): a standard-model assumption, generic cost `2^128` classical at 256 bits, of order `2^85` quantum (from memory, no source in the folder); it excludes SHAPE-VIOLATION and carries the node count of T-a. Replaces the oracle figure `T^2 / 2^(8b + 1)`, dropped |
| MA-1 | A modelling assumption, not provable: Keccak-256 / SHAKE256 (A) and SHA-256 / SHAKE256 (B) as one random oracle with four disjoint parts; owed: the encodings' injectivity checked in the transcripts (T-1) |
| MA-2' | A modelling assumption, not provable: BLAKE3 `derive_key` as the oracle's leaf and node parts on IV-constrained inputs; owed: the framing as built (obligation H-2, `decision-b-merkle-hash.md`) |
| Z-A | `eps_hvzk^A`: Z-A1 sumchecks matched to the mask lemma; Z-A2 wire audit; Z-A3 the shared root's statistical claim; Z-A4 the GKR fraction layers; Z-A5 the simulator through the code; Z-A6 the number (`zk-quantum.md` 5.2). *Amended 2026-11-19 (`zk-b-referee.md` F-4, MAJOR):* the H-2 rank term of Theorem C (`zk-composition.md` §4.2a) is **not proven** — under investigation in system A's build (rank check after `z`, restart below 8); no figure is claimed for it, and `eps_hvzk^A <= 2^-246.5` holds only once that restart is built and tested |
| Z-B | `eps_hvzk^B`: Z-B1 the wrapper's view; Z-B2 the pad-count guard; Z-B3 the event `gamma = 0`; Z-B4 the ring switch in the pad ledger; Z-B5 the statistical form of each step (Z-B6 not needed: route S built); a test that every fold-round commitment is the salted hash (`zk-referee.md` R-3) *Amended 2026-11-19:* the ledger for B as built (Binius64 zero-knowledge mode) is `zk-composition.md` §5.2 (Theorem C-B, Sim-B, rows M1–M12; Lemma DC and Corollary DC, Original, draft until refereed: `eps_B < 2^-248.4` for `n_x ≤ 32`; *2026-11-19, `zk-b-referee.md` F-3:* `n_x = 21` at the category-1 wrapper, `eps_B ≤ 2^-249`; second referee `zk-b-referee.md`: Lemma DC and Theorem C-B pass with conditions, F-1, F-2, F-3, F-5, F-6 applied); referee `hvzk-referee.md` (pass with conditions H-1, H-3, applied in `c73ff53`, pending a re-read); simulator tests SB-1 to SB-5 owed by system B. |
| U, J1, J2, J3, F, K (candidate rows) | Proven in `binius-johnson-row.md` and found to hold by both referees; owed: DKT26 Theorem 4.4 / Corollary 6.6 / Lemma 3.3 themselves (a preprint; or BCHKS, not read, in its place), the ArkLib Lean build (referee-2 C-1), the calculator and test conditions C-3, C-5, the build checks C-4, C-6, C-7, and for J3 the build properties H7, H8' |
| `lemma-tree-extraction.md` revision 3 | A referee's report on SHAPE-VIOLATION and Lemma TE.3, H-BIND as restated, the joint-probability reading, Corollary TE-X-Q (sketched) |
| `lemma-tree-extraction.md` revision 5 | A fresh referee's report on section 6b as revised: the two-pass fold argument, the per-query batching term and its quantum form ([CMS19] constant not re-read), the per-build challenge field; owed elsewhere: `yugen-proof-b2` parameters 24.4 (3) relabel (R4-2), vfinal's root-discharge random-point check run (R4-8), spec adoption of 4/4/5 (R4-7). **Refereed: `tree-extraction-rev5-referee.md`, pass with conditions R5-1 to R5-4** (record the built challenge256 refusal; quantum constant labelled; line 64 restated; R4-8 run); revision 5.1: `tree-extraction-rev51-referee.md`, pass with conditions R51-1 to R51-3; **revision 5.2 (`b9836a8`): PASS** (same report, section 4). Done for section 6b; owed elsewhere: parameters 24.4 (3) relabel (R4-2), spec adoption of 4/4/5 (R4-7) |
| R-8 | The lifted-oracle proximity statement for B (`b-round-census.md` 5; K-B.2): **Lemma LF** (`lemma-k-b.md` 3a, 2026-11-19; Original, refereed-in-review: written by the referee of `zkq-te3-r8-referee.md`, not yet independently read). Owed: an independent read; **m-5**, B's direct encoding test (lift of the small-domain encoding equals the large code's encoding of the embedded message, at every `L` the rows use) |
| Z-1' | Salts at profile Y as built: A leaf and proof salts 80 B (an agent is moving A now; A's head `084fbdd` has 64 B), B leaf salts 768 bits and proof salt 80 B (B's head `395da08` has 512 bits and 64 B) (`zk-quantum.md` 7) |
| A-row0 | A's row 0 descriptor binds nothing beyond the program IV (`lemma-tree-extraction.md` N-3): no gap as built (tree rows 6 to 9); fix: bind row 0's fields or refuse it in tree programs, with a test |

## 6. Referee queue (revised 2026-11-19, revision 3)

**Refereed now** (report, verdict):

| Item | Report | Verdict |
|---|---|---|
| Theorem S (`zk-wi-soundness.md`) | `theorem-s-referee.md` | holds, pass with corrections (M-1, m-1 to m-3), applied |
| Lemma K-A, census A | `knowledge-and-census-referee.md` | pass with conditions (M-A1, M-A2, m-A1 to m-A3), applied 2026-11-19; re-read pending |
| Lemma RS | `knowledge-and-census-referee.md` | pass |
| Lemma K-B, census B | `knowledge-and-census-referee.md` | pass with conditions (m-B1, m-B2, M-A1 applied; R-8, D-4 open); re-read pending |
| Salting as built (A and B) | `zk-referee.md` | complete on both systems; audit finding W-2 withdrawn |
| P-sh code (B's parallel node batching) | `pbatch-code-referee.md` | pass; in-circuit equivalence pass |
| A's merge of seven, `zk_mle`, R-1, the `k_q` findings | `guest-merge-referee.md` | sound; M-1, M-2 and the MAJORs K-1', K-2' open |
| `lemma-tree-extraction.md` revision 4, section 6b (4/4/5, B internal nodes, fold terms) | `tree-extraction-rev4-referee.md` | pass with conditions R4-1 to R4-8; applied in revision 5 (draft, unrefereed; two-pass fold argument, per-query batching term `(t + K) 151 / |F_c|`: negligible at the 256-bit challenge field (`cat1`/`cat1t`), caps B at 120.76 classical / about 60.4 quantum bits at the default `GF(2^128)` build); rows stay **not proven** |
| `zk-quantum.md` rev 2/2.1 (Theorem 6.6 (3), (4), ZP), Lemma TE.3, Corollary TE-X-Q, R-8 | `zkq-te3-r8-referee.md` | ZK: pass with conditions (M-1 applied in 2.2; M-2 **stale**, the transcript is built); TE.3: pass with conditions (M-3 applied in 3.1); TE-X-Q: pass as a sketch; R-8: Lemma LF, conditional on m-5 |

**What remains**, by how much rests on each:

| # | Item | What leans on it |
|---|---|---|
| 1 | The three HVZK documents' simulators (`zk-composition.md`, `zk-hiding-commitment.md`, `zk-masked-sumcheck.md`; `zk-referee.md` read them for coverage only) | `eps_hvzk` of both systems: no privacy figure is complete until then |
| 2 | `zk-quantum.md` revision 2.2 and `lemma-tree-extraction.md` revision 3.1: the re-read of the `zkq-te3-r8-referee.md` fixes (M-1 figures at the profile, M-2 transcript built, M-3 shape check at the child, MA-0) | the privacy statement; every tree row |
| 3 | Lemma LF (R-8, K-B.2): an independent read of the referee's proof; m-5 test from B | K-B at the commitment-index round, hence every B tree figure |
| 4 | Corollary TE-X-Q's owed parts (i) to (iii) (`zkq-te3-r8-referee.md` section 2) | the quantum batch form of the tree |
| 5 | A / B statement equivalence (`what-is-claimed-elsewhere.md`) | that both systems prove the same leaf statement |
| - | Re-reads of this revision's K-A, K-B and census A changes; B's guest as a whole (C2) | K-A, K-B; C2 for B |

## 7. Boundary: claims on the sibling page `what-is-claimed-elsewhere.md`

| Claim | Why it touches this page |
|---|---|
| Falcon-512 verification in the leaf statement; A / B statement equivalence | a soundness dependency of the pool: a leaf proof proves the statement, and the statement must accept exactly valid signatures |
| The hidden salted key hash `sig_d` (hiding and binding) | binding is a soundness dependency (one key per address); hiding is a zero-knowledge dependency: Theorem ZP hides the witness, not what the public inputs reveal |
| ML-KEM-1024 note encryption and its binding to the output | outside both proof systems |
| The private-retrieval scheme (two-server DPF) | outside both proof systems |
| Turnstile, pause and frozen mode | consensus rules; the fallback if a soundness row of this page fails |
