# Yugen proof systems: design basis by NIST security category (1, 3, 5)

Status: the parameter basis the plan cites for proof sizes and verification costs. Written
2026-11-18 in `yugen-proofs`. Decisions recorded: system A is leanVM; system B is Binius64 (revision 3, 2026-11-19; it was
Plonky3's binary stack until then, Appendix A).

Every number is marked **M** (measured on this machine, raw output in `bench/results/`) or **E**
(estimated by `soundness/` from models calibrated against those measurements). Regenerate the
tables with `cd soundness && uv run yugen-soundness --current` (section 2a, the adopted basis),
`--ship` (Appendix A.2), `--basis` (Appendix A.3) and `--design` (section 4); the generated text is kept in `soundness/output/`.

Provenance (citation audit of 2026-11-19): the bounds this basis applies are published and are
listed with their sources in `soundness-method.md` sections 2 and 7 and in `../REFERENCES.md`;
"the book's BCS bound" is Chiesa and Yogev, Theorems 25.2.1 and 31.2.1, whose original form is
Ben-Sasson, Chiesa, Spooner, ePrint 2016/116, Theorem 7.1. The targets, the conditions and the
tree accounting are Original (the Ycash developers, 2026), `REFERENCES.md` O-13. The parameter
choices (no grinding, unique decoding only) are this project's; for comparison, the published
hiding construction ePrint 2026/391 reports its sizes with the Johnson-bound regime and 24
grinding bits at a 100-bit target (its Section 1.3), which are not comparable with the rows here.

## 1. Targets (revision 7: the security category is a parameter)

The lead architect's aim is NIST security categories 3 to 5. The design basis is stated with the
category `c` as a parameter; the calculator derives every condition from the text of NIST's call for
proposals ([CFP] Section 4.A.5, pages 16 to 18; `soundness-method.md` 8.7) and certifies rows at any
category (`uv run yugen-soundness --category c`; categories 1, 3 and 5 in
`soundness/output/revision7-tables.txt`). Definitions, conventions and the line between theorem and
estimate: `soundness-method.md` 8.7 (8.1 to 8.6 for the earlier per-layer form).

**Working assumption (lead agent, pending the lead architect's choice): profile M-1** of
`decision-security-category.md` 6: **category 3 for soundness and binding** (proof rows,
48-byte statement and proof digests, the 256-bit challenge field), **category 5 for privacy and
long-lived secrets** (zero-knowledge salts sized against `t = 2^128`: 80-byte proof salt, 112-byte
leaf salts; ML-KEM-1024 and 256-bit keys outside the proof systems). The referee
(`security-category-referee.md` V15) notes that retrieval (DPF seeds, category 1) and the transport
KEM (category 3) cap M-1's privacy level until they are raised, and that zero knowledge is
statistical, so "category 5 privacy" describes its query budget, not a category.

| Category `c` | `kappa_C`: proven classical bits | `kappa_Q`: proven QROM bits (to `2^kappa_Q` queries) | G: attack bits a round | Need a round, tree of 20,000 proofs (A / B) | Digests, attack rule (proven rule) | Smallest field (worst certified shape) | Admissible tree hashes |
|---|---|---|---|---|---|---|---|
| 1 | 128 | 64 | 128 | 152.52 / 152.52 | 256 (264) | 185 bits: `GF(2^256)` | Keccak-256, SHA-256, BLAKE3, and every longer one |
| 2 | 128 (collision search on a 256-bit hash) | 64 | 128 | as 1 | 256 (264) | as 1 | as 1 |
| 3 | 192 | 96 | 192 | 216.52 / 216.52 | 384 (392) | 249 bits: `GF(2^256)` | SHA-384, SHA3-384, SHAKE256 at 48 B or longer |
| 4 | 192 (collision search on a 384-bit hash) | 96 | 192 | as 3 | 384 (392) | as 3 | as 3 |
| 5 | 256 | 128 | 256 | 280.52 / 280.52 | 512 (520) | 313 bits: `GF(2^384)` | SHA-512, SHAKE256 at 64 B |

**BLAKE3 and SHA-256 are category 1 tree hashes only**: BLAKE3's designers claim 128 bits for every
goal and every output length (BLAKE3 specification, version 20211102173700, Section 4.1;
`decision-b-merkle-hash.md` H-1.5), and SHA-256's generic collision level is 128 bits (from memory;
NIST itself moves SLH-DSA's tree functions `H` and `T_l` from SHA-256 to SHA-512 at categories 3 and
5, FIPS 205 Section 11.2.2). The calculator refuses either as a tree hash above category 2
(`HashNotAdmissible`).

The challenge field `GF(2^256)` serves categories 1 to 4 with 7 or more bits of margin on every
algebraic round; category 5 needs at least 312 bits (313 for nodes of `2^30` at rates 1/4 and
1/16), so `GF(2^384)` (cubic over the 128-bit word field) or `GF(2^512)`. Category 3 is not a
parameter-only release (`decision-security-category.md` finding 2, referee V13): the 48-byte
digests, the tree hash of system B and Falcon-1024 are new engineering.

The former table of this section (per layer, four-layer chain, CMS19, 2026-11-18) is superseded by
the table above:

| Target | Chain, proven classical | Per layer (4 layers, union bound) | Chain, proven QROM (CMS19 Theorem 8.6, C1 = 6, C2 = 24) | Per layer | Attack bits per round (Grover under MAXDEPTH) | Digests, attack rule | Digests, proven rule | Smallest challenge field |
|---|---|---|---|---|---|---|---|---|
| `cat1` | 128 | 130 | 64 | 66 | 128 | 256 | 264 | GF(2^192) |
| `cat3` | 192 | 194 | 96 | 98 | 192 | 384 | 392 | GF(2^256) |

## 2. Design basis

**Section 2a governs** (revision 3, 2026-11-19). Every earlier table is kept in Appendix A as a
record: revision 2 of section 2a (A.2, with system B on Plonky3), the per-layer table of
2026-11-18 and its reading (A.3). Sections 3 to 5 are the record of 2026-11-18; their system B
figures are Plonky3's and are superseded by section 2a.

### 2a. Adopted design basis: category 1 for the tree of specification 0.3, no grinding (2026-11-19, revision 3; system A's leaf row and system B restated in revision 4)

Decisions of the lead architect, which this section implements:

1. The whole tree meets `cat1`: at most 2^14 leaves, sub-bundles of at most 16 leaves, three merge
   levels of arity at most 16. Packed full it has `2^14 + 2^10 + 2^6 + 2^2 + 1` = **17,477
   proofs** (`2^14.09`); the union bound runs over them (`soundness-method.md` 8.5b, 8.5c).
2. No grinding anywhere. 3. Proven bounds only: unique decoding (BCIKS20), the book's BCS bound,
   CMS19. 4. 256-bit digests (attack rule H; finding S-2 of A.2 stands). 5. Every proof at most
   1.75 MiB.
6. System A (leanVM) as built in `yugen-proof-a` / `yugen-proof-a-zk`: the leaf opens with W-I at
   its **true rates** `lf_i / 2^log_domain_i`, with the tail sumcheck of A26 and every
   zero-knowledge round outside the opening in its round list (`wi.rounds(c, "A", wi.A_WALLET_ZK)`,
   section 8.5c of `soundness-method.md`); nodes are plain WHIR.
7. System B is **Binius64** (`yugen-proof-b2`): FRI-Binius / BaseFold under unique decoding,
   SHA-256, its own zero-knowledge mode on the leaf (masked BaseFold and IronSpartan wrapper),
   transparent node proofs. The Plonky3 rows are superseded (A.2, A.3).

Generated by `cd soundness && uv run yugen-soundness --current` (`current.py`, `binius64.py`;
tests `tests/test_current.py`); full output `soundness/output/current-tables.txt`. Every proof
counts 512 rounds outside its listed rounds in `k` (S-1, an upper figure), so a round needs
**152.2 to 152.3 bits** (152.28 for A's leaf, whose list has 68 rounds). **M** marks a measured
input, **E** an estimate; every query count and size below is **E** unless marked.

#### Revision 7 (2026-11-19): rows for categories 1, 3 and 5

Generated by `uv run yugen-soundness --rev7` (`category.py`; tests `tests/test_revision7.py`, each
count less by one fails for every row); output `soundness/output/revision7-tables.txt`; every
number in `soundness/CHANGELOG.md` revision 7. Decisions 2, 3 and 5 above stand at every category
(no grinding, proven bounds with unique decoding for certified rows, every proof at most
1,835,008 B); decision 4 becomes "digests of `2 kappa_C` bits". Tree of 20,000 proofs; spBCS under
Sharp–Grubbs Theorem 6.6. Sizes are estimates (**E**) anchored on measured proofs (**M**: A's masked
leaf 688,180 B, A's node 875,309 B, B's form-T leaf 583,680 B, B's node 538,272 B).

| | Category 1 (as built) | Category 3 (M-1 soundness) | Category 5 |
|---|---|---|---|
| Profile | 32-byte digests; salts 64 / 64 B; `GF(2^256)`; Keccak-256 / BLAKE3 | 48-byte digests; salts 64 / 96 B (M-1: 80 / 112 B); `GF(2^256)`; SHAKE256-384 / SHA-384 | 64-byte digests; salts 80 / 112 B; `GF(2^384)`; SHAKE256-512 / SHA-512 |
| Need a round | 152.52 | 216.52 | 280.52 |
| A leaf, row 6 (standalone masked), mode 0, `2^22`, 1/4 | 226, 157, 154, 154; 672 KiB | 321, 222, 219, 218; 1,055 KiB | 415, 288, 283, 282; 1,750 KiB |
| A leaf, row 6, mode 1, `2^20`, 1/4 | 227, 157, 155; 486 KiB | 323, 223, 219; 753 KiB | 419, 289, 285; 1,254 KiB |
| A leaf, row 8 (masked in a tree), mode 0, 1/4 | 226, 160, 163, 179; 667 KiB | 322, 228, 232, 293; 1,043 KiB | 417, 295, 305, 395; 1,713 KiB |
| A leaf, row 8, mode 1 (admitted stack) | `2^21`: 227, 161, 166, 219 | `2^22`: as mode 0; 976 KiB | `2^22`: as mode 0; 1,612 KiB |
| A leaf, row 8 at rate 1/2 | 374, 168, 174, 219 | **no admitted stack** | **no admitted stack** |
| A node row 9, `2^27`, 1/2 | 368, 167 x3, 168 x2, 173; 853 KiB | 522, 238 x4, 239, 246; 1,427 KiB | 676, 308 x4, 309, 319; 2,368 KiB (**over**) |
| A node row 9, `2^27`, 1/4 | 225, 160 x5, 163; 742 KiB | 320, 227 x5, 231; 1,249 KiB | 414, 294 x4, 295, 299; 2,105 KiB (**over**) |
| A node, largest (`2^30`, 1/2) | 1,023 KiB | 1,751 KiB (41,799 B under the limit) | 2,933 KiB (**over**) |
| B leaf (form T, route S), 1/8 / 1/16 | 184 / 168; 621 / 623 KiB | 261 / 238; 1,066 / 1,045 KiB | 338 / 308; 1,799 / 1,819 KiB (**over**) |
| B node, `2^27` words, 1/8 / 1/16 | 697 / 696 KiB | 1,148 / 1,118 KiB | 1,996 / 2,001 KiB (**over**) |
| B list-decoding rows (**candidate, conditional on DKT26**; never certified) | 102 (1/8), 77 (1/16) | none at `GF(2^256)`; 145 / 109 at `GF(2^384)` | 188 (1/8), 141 (1/16): leaf 1,092 / 940 KiB |
| QROM bits A / B (Theorem 6.6 (2)) | 67.25 / 67.43 (`kappa_Q` 64) | 99.29 / 99.39 (96) | 131.28 / 131.35 (128) |
| Zero knowledge, pool of `2^20` leaf proofs (plus `Q eps_hvzk`, open) | `2^-87.8` / `2^-85.7` | `2^-138.0` (M-1: `2^-170.0`) | `2^-151.8` / `2^-149.7` |

**Findings.** (1) Category 3 meets every condition with every certified proof inside
`PROOF_BYTES_MAX`, the largest (A's node of `2^30` at rate 1/2) by 2.3 % (E): run A's nodes at rate 1/4
(1,544 KiB at `2^30`) to keep a margin. (2) Category 5 with unique decoding does not fit:
B's zero-knowledge leaf (1,799 KiB) and every node except A's `2^24` and `2^25` stacks at rate 1/4 exceed
1,835,008 B; what would make it fit: `PROOF_BYTES_MAX` of at least 3,003,138 B (or 2,683,634 B with A's
nodes at rate 1/4), or B's list-decoding rows once DKT26 and lemmas L-J1 to L-J3 are confirmed (B's
leaf 1,092 KiB, node 1,217 KiB at 1/8). (3) Category 5 needs a field of at least 312 bits for both
systems (313 at rates 1/4 and 1/16); the category study's 305 for A counted the leaf only. (4) Row 8 at
rate 1/2 has no admitted stack at categories 3 and 5: the masked leaf in a tree runs at rate 1/4.
(5) The QROM hash term needs 320 / 416-bit digests at categories 3 / 5 (the attack rule's 384 / 512
satisfy it); a 32-byte digest is refused at category 3, a 48-byte one at 5.

#### Revision 6 (2026-11-19): the spBCS transcript, Sharp–Grubbs Theorem 6.6, corrected zero-knowledge counts

Generated by `uv run yugen-soundness --rev6` (`revision6.py`, `spbcs.py`, `affine.py`; tests
`tests/test_revision6.py`); output `soundness/output/revision6-tables.txt`; every changed number
before and after in `soundness/CHANGELOG.md` (revision 6). Decisions D-a, D-b, D-c of
`qrom-compilation.md` 0 (lead agent; open to the lead architect's review).

**Transcript and condition Q.** Both systems adopt the spBCS transcript of Sharp and Grubbs
(*Faster and Smaller Anonymous Credentials from Standardized Signatures*, ePrint 2026/2615,
Protocol 6.5; specification in `qrom-compilation.md` 2), covered as published by their Theorem
6.6 (2) (Published): `C1 = 6`, hash constant `6 c'`, `c' = max(2, c) + n_J + 1` from the message
counts (A: 599 verifier messages, `c' = 2,397`; B: 600, `c' = 2,401`; estimates until the
transcript modules report them), the verifier's `k_q` added to `t`. Tree of 20,000 proofs,
`lambda = 256`: **A 67.54 QROM bits** (IOP term; hash term 75.63; margin +3.54), **B 67.43**
(+3.43) with SHAKE256 streams (the default), 66.43 (+2.43) with the counter-mode SHA-256
alternative (Lemma X; Adapted). Theorem Q's forms X and C (revision 5) are records: form C's
constants `C1 = 24`, `C2 = 240` are **unproved** (no write-back; referee report 1.5). Condition Q is
a hard failure in `spbcs.require`. **Finding Q-5** (`qrom-compilation.md` 6.2): the published
classical bound of spBCS charges the verifier's `k_q` at `t = 1`; in the calculator's "every `t`"
convention condition C would need 158.8 bits a round (rows miss by 5.8), for `t >= k_q` 144.3 (met
by 8.4 or more). The certified rows stay on the book's convention until the lead architect decides
(task T-6).

**Zero knowledge (leaf proofs only, D-c).** Sharp–Grubbs Theorem 6.6 (3) (everlasting, QROM,
adaptively chosen proofs; Published) with 64-byte leaf salts and a 64-byte proof salt (D-b):
`2^-107.8` (A) and `2^-105.7` (B) a proof, `2^-85.4` over `2^20` proofs of both systems with the
recursion (Theorem ZP of `zk-quantum.md` 3.3; Original as a composition), each plus the IOP's
`eps_hvzk` terms, which are **open** (obligations Z-A1 to Z-B6). Theorem 6.6 (4) (unconditional
witness indistinguishability) `2^-84.4` at the pool. System B's four fold trees must be salted for
the published theorem (route S: +46 KiB a B leaf proof, E). Revision 5's salt figures (Lemma H with
Theorem ZQ: `2^-104` a proof) are records; "`zeta_IOP < 2^-240`" is withdrawn.

**System A's zero-knowledge counts.** `wi.A_WALLET_ZK` corrected to the merged code's 11 bus layers
and 52 claims (87 listed rounds; need 152.517 bits): the leaf row 226 / 157 / 154 / 154 still
meets (+0.44); no count changes.

**leanVM's `eps_aff`** (CWYZ26, ePrint 2026/2863, Theorem 4.10, (4.13); Published), implemented with
leanVM's witness search; Remark 5.3's 125.42 bits reproduced. No certified row changes (every Yugen
row is in unique decoding).

**Records.** `shipping.py`, `design.py`, `params.py`, `qrom.py`, `salts.py` are records that use
nominal rates or superseded constants and certify nothing.

#### Revision 5 (2026-11-19): true rates, the corrected rows, Theorem Q, salt length, B's candidate rows

Generated by `uv run yugen-soundness --rev5 [--salt 512]` (`revision5.py`, `qrom.py`, `salts.py`,
`johnson.py`; tests `tests/test_revision5.py`); output `soundness/output/revision5-tables.txt`;
every changed number before and after in `soundness/CHANGELOG.md`. Tree bound 20,000 proofs, 512
other rounds a proof, no grinding, unique decoding, 256-bit challenges and digests. This block
**governs** where it differs from the revision-3 and revision-4 text below, which is kept as the
record. Rows are those of `yugen-proof-a` `docs/parameters.md` 2 (row 7 plain leaf, row 8 its
salted W-I form, row 9 the node: folds 6, 3; reductions 3, 3; residual bounds `2^7`, `2^7`, `2^5`).

**True-rate rule (finding W-1).** Provenance: Original (the Ycash developers, 2026),
`whir-additive-soundness.md` section 6 with Theorem S0 (Lemmas C0, B0), resting on Published
results: BCIKS20 Theorems 4.1 and 1.6 (proximity, unique decoding) (BCIKS20 numbers follow the folder copy, ePrint 2020/654 revision of July 3, 2021 (`2020-654.pdf` (see REFERENCES.md)); the ECCC TR20-083 copy of May 30, 2020 numbered the affine-space theorem 1.7, the curve theorem 1.6 and the extension-field remark 1.5 (amended 2026-11-19, `CITATION-AUDIT.md` C-41)) and Chiesa, Weissenberg, Yogev,
Zheng, ePrint 2026/2863, Theorem 5.2 (the affine combiner's degree bound `d + r` after `r`
rounds). System A's affine combiner adds one coefficient to the folded lane a fold round, so every
WHIR query round of a plain level is evaluated at the true rate
`rho_i = (2^mu_i + kappa_i) / 2^(mu_i + r_i)` (`mu_i` the variables left after the level's
`kappa_i` folds), not at `2^-r_i`. W-I levels already used the true rates of their layout. At the
153.0-bit list (369, 226, 185, 168, 161, ...) row 9 at rate 1/2 is **4.35 bits short** at `2^24`
(4.36 at `2^27`; final `mu = 3`), 1.72 at `2^25`, 0.39 at `2^26`; at rate 1/4 up to 1.15 short;
row 7 keeps +0.63 (1/2) and +0.90 (1/4) (reproduced independently from the formula, within 0.01
of the document).

**Corrected schedules** (the rule: every query round at 153.0 bits or more at its true rate,
`q_i = ceil(153.0 / -log2((1 + rho_i)/2))`, computable at setup from `mu_i`, `kappa_i`, `r_i`;
equal to the list except at the last one or two levels of rows 7 and 9). Every node shape the tree allows has a stack of `2^24` to
`2^29` (sub-bundles of 1 to 16 leaves, merges of 1 to 16 children, measured up to `2^28`,
`yugen-proof-a` recursion.md 9.10; the calculator checks `2^24` to `2^30`). Provenance: Original
(the Ycash developers, 2026).

| Row | Rate | Counts per level (rule) | Margin over the need | Delta against the list (E) |
|---|---|---|---|---|
| 7 (leaf) | 1/4 | 226, 161, 161, 161 (unchanged) | +0.90 | none |
| 7 | 1/2 | 369, 168, 168, **169** | +0.79 | +325 B; +13 Keccak-f a verified leaf |
| 8 (W-I, 512-bit salts) | 1/4 | **227, 161, 164, 180** (minimal at the need 226, 160, 163, 179) | +0.92 | the list (226, 161, 161, 161) fails by 14.19 bits; 546 KiB |
| 8 | 1/2 | **375, 169, 175, 220** (minimal 374, 168, 174, 219) | +0.68 | the list fails by 30.41; 668 KiB |
| 9 (node), final `mu = 3` (`2^24`, `2^27`) | 1/2 | 369, 168, ..., 168, **169, 174** | +0.77, +0.78 | +1,829 B a node proof; +66 Keccak-f, +1,309 cycles a child verified (E) |
| 9, final `mu = 4` (`2^25`, `2^28`) | 1/2 | 369, 168, ..., **169, 171** | +0.77, +0.78 | +1,012 B; +43 Keccak-f |
| 9, final `mu = 5` (`2^26`, `2^29`) | 1/2 | 369, 168, ..., **170** | +0.76, +0.77 | +522 B; +22 Keccak-f |
| 9 | 1/4 | last level **163 / 162 / 161** at final `mu` 3 / 4 / 5 | +0.72 to +0.88 | +462 / +263 / 0 B |
| zero-knowledge leaf (row 6 schedule, every mask) | 1/4 | 226, 157, 154, 154 (unchanged: W-I) | +0.45 | none |

A full merge of 16 children at the worst node shape: +1,056 Keccak-f and about +21,000 cycles (E),
0.25 % of the about 8.3 million cycles of verifying 16 children (M, recursion.md 9.10). No row
fails the target with the rule; the minimal counts (no margin) are in `revision5-tables.txt`. The
alternative fix (residual bound `2^7` for nodes, `whir-additive-soundness.md` 6, fix 2) is not
needed.

**QROM bits of the tree (Theorem Q; record, superseded by revision 6).** Provenance: Adapted (the Ycash developers, 2026):
`qrom-compilation.md` Theorem Q, from CMS19 (Chiesa, Manohar, Spooner, ePrint 2019/834) Theorem
8.6 and Section 8.5.1 with the changes of its 5.2; tree accounting Original (O-13). **Assumption:
the transcripts are in the CMS form** of `qrom-compilation.md` 4 (form X for A: SHAKE256 link and
expand; form C for B: counter-mode SHA-256); the transcripts as built are outside both theorems
(C-7). Constants: A `C1 = 6`, `C2 = 24` (12 and 96 with the verifier's calls folded in); B
`C1 = 24`, `C2 = 240`. At `N = 20,000`, `lambda = 256`: **A 67.24 (IOP) / 78.71 (hash)** at
`e = 152.343`, 67.54 at the weakest corrected round (margin +3.5 over 64); **B 66.24** at
`e = 152.343`, 66.43 at its weakest round (margin +2.4). Condition Q is now a hard failure in the
calculator (a 192-bit digest under form C, hash term 56.3, is refused). Condition C still binds.

**Salt length: 512 bits** (the lead architect's choice; the error figures of this paragraph are
superseded by revision 6, Lemma H being Published, SG26 Definition I.1). Provenance: Adapted, `zk-quantum.md`
Lemma H and Theorem ZQ (from Chiesa, Yogev, the book's Lemma 17.3.1 and Claim 3.4.2, and CMS19
Lemma 7.3's argument); independently supported by GordieHowe, ePrint 2026/2615, Theorem 6.6 (3)
(C-21). Statistical zero-knowledge error from the salted trees, `N_u = 2^24` unopened leaves a
proof: `2^-104` a proof, `2^-90` for the 2^14 leaf proofs of a tree (384 bits: `2^-40` /
`2^-26`; 576: `2^-136` / `2^-122`; 256 bits as built: no statistical statement). Cost: +32 bytes
an opened leaf (row 8 at 1/4: 732 opened leaves, +23,424 B; B's leaf: +11,776 B); no extra
Keccak-f a leaf in A; B's all-`GF(2^256)` leaf hash goes from 2 to 3 SHA-256 blocks.

**System B.** Certified: **unique decoding, 184 queries at rate 1/8** (weakest algebraic round
226.00 bits). **Candidate rows, under referee review, not certified**: Johnson regime `m = 10`,
107 queries, on the Haböck route (Haböck, ePrint 2024/1571, Theorems 3, 4; weakest 169.34; gap
G-1) and on the DKT26 route (Dao, Kominers, Thaler, ePrint 2026/2056, Theorem 4.4, Corollary 6.6;
weakest 211.41); DKT26 `m = 153`, 102 queries (199.80). They rest on the lemmas L-J1 to L-J3 of
`binius-johnson-row.md` (Original, the Ycash developers, 2026; unreviewed). Category 3: unique
decoding, 261 queries; the Johnson row is refused there.

#### System A

| Layer | Opening | Statement committed | Schedule (row table fields) | Queries per level | Field needed (bits) | Size (KiB) | Under 1.75 MiB |
|---|---|---|---|---|---|---|---|
| leaf | W-I, true rates, every mask built | 2^22 words (**M**) | row 6's: folds 5, 3; reductions 1, 1; residual 2^10; levels 5/3/3/3, rates 2^-2, 2^-6, 2^-8, 2^-10 (nominal) | **226, 157, 154, 154** (revision 4: 20,000 proofs, 85 listed rounds, 152.51 bits) | 177: GF(2^192) | **586** (**M**: 600,340 B at rate 1/4, `yugen-proof-a-zk` zero-knowledge.md 17.4; the model without the masks' scalars gives 520) | yes |
| sub-bundle (16 leaves) | plain | 2^28.11 words (E): 16 x 507,400 cycles (**M**) x 1.12 (query ratio, E) x 31.8 words a cycle (**M**); stack 2^29 | row 9: folds 5, 3; reductions 1, 1; residual 2^9; rate 1/2 | 367, 160, 155, 153, 153, 153 | 183: GF(2^192) | **939** (E; at 2^28: 895) | yes |
| merge 1 to 3 (16 children) | plain | 2^28.07 words (E): 16 x 428,189 cycles (**M**) x 1.12 x 36.6 words a cycle (**M**); stack 2^29 | row 9, rate 1/2 | 367, 160, 155, 153, 153, 153 | 183: GF(2^192) | **939** (E) | yes |

**Revision 4 (system A).** The tree bound is the 20,000 proofs of specification 0.3.2 and the
leaf's zero-knowledge round list is the built one (`wi.A_WALLET_ZK`: 10 bus layers, 12 Keccak
layers, two masked chains in S9, column `A` of 2^11 elements, 54 gadget claims; 85 listed rounds;
revision 6: 11 bus layers and 52 claims as merged, 87 listed rounds, the same counts meet).
The leaf row is **226 / 157 / 154 / 154** (each count less by one fails; the earlier 225 / 156 /
154 / 153 misses by 0.07 to 0.18 bits), as the implementers solved it. The node rows below were
solved for 17,477 proofs: at 20,000 **row 9 at rate 1/2 needs 368 queries at level 0** (152.32 of
152.35 bits with 367); at rate 1/4 its list still meets (finding S-14). The leaf table and the
candidates table below are the 17,477-proof record.

Node size: the plain-WHIR model plus 42,011 B of other transcript, fitted to four measured node
proofs on the 256-bit field (row 5, rate 1/2: 575,188 / 645,676 / 621,676 / 625,604 B, **M**),
error -2.6 % to +4.0 %. At node rate 1/4 the node rows are 862 KiB (queries 225, 156, 154, 153,
153, 153). The node stacks are E: no 16-child node has been built; a sub-bundle of one leaf
commits 2^24 words (**M**).

**The leaf as built (row 6) against the target.** Row 6's counts were solved for 135.58 bits at
the nominal rates. At the true rates and the tree target:

| Level | Fold | Domain | Nominal rate | Folded lane `lf` (built layout) | True rate | Row 6 queries | Bits, true rate | Short of 152.28 by | Queries needed | Bits with them |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 5 | 2^19 | 2^-2 | 131,533 | 0.25088 | 200 | 135.41 | 16.87 | **225** | 152.33 |
| 1 | 3 | 2^20 | 2^-6 | 16,782 | 0.01600 | 139 | 135.82 | 16.46 | **156** | 152.42 |
| 2 | 3 | 2^19 | 2^-8 | 2,444 | 0.00466 | 137 | 136.08 | 16.20 | **154** | 152.96 |
| 3 | 3 | 2^18 | 2^-10 | 651 | 0.00248 (2^-8.65) | 136 | 135.51 | 16.77 | **153** | 152.44 |

Keeping row 6's counts leaves the tree **16.9 bits short** (weakest round 135.41 bits). At the
true rates row 6 also misses its own 135.58-bit design figure by 0.17 bits at level 0 and 0.07 at
level 3. The counts needed at row 6's schedule are exactly the tree list
`CAT1_TREE_UD_QUERIES` read by the nominal level rate, so **the row to paste is row 6's schedule
with `Queries::ByLevelRate(&CAT1_TREE_UD_QUERIES)`**: 225, 156, 154, 153. Each count less by one
fails (tested). The smallest leaf over the schedules the row table can express is folds 5, 3,
reductions 3, 3, residual 2^11 (225, 168, 171; 467 KiB, E), 52 KiB smaller.

**The recursion team's candidates** (`yugen-proof-a` `docs/recursion.md` 9.4, rows 7 to 9; the
tree list by level rate; full table in `current-tables.txt`):

| Candidate | Layer | Meets? | Weakest round | Nearest row that meets |
|---|---|---|---|---|
| row 8: folds 6, 3; reductions 3, 3; residual 2^10 (W-I, 2^22, rate 1/4) | leaf | **no** | final level 150.05 bits (true rate 2^-4.3 against nominal 2^-5); level 0 152.10 | the same schedule with **226, 160, 163** (476 KiB, E): needs per-level counts in the row (the list by level rate cannot give 226 at level 0 and 163 at the last level) |
| row 8 with residual 2^5 (W-I) | leaf | **no, at any count** | final level 21.98 bits: the last lane's true rate is about 0.8 | residual 2^7: 226, 160, 163, 179 (521 KiB, E); residual 2^5 is open to nodes only |
| row 9 (folds 5, 3; reductions 1, 1; residual 2^9) | node | yes, at stacks 2^24 to 2^29, rates 1/2 and 1/4 | level 0 at rate 1/2: 152.32 against 152.17 | |
| row 5 shape, residual 2^5, reductions 3, 3, fold 6, fold 6 with reductions 3, 3, folds 6 and 4 with reductions 3, 3 | node | yes, each at 2^24 and 2^29, rates 1/2 and 1/4 (revision 5: at the true rates, weakest 152.23 to 152.56; the remark "plain WHIR: true rate = nominal" made here before was wrong for system A, finding W-1) | 152.32 to 152.57 (nominal) | |

The node margin is 0.15 bits at rate 1/2: the tree list holds for 17,477 proofs and 512 other
rounds, not for much more (finding S-8).

#### System B (Binius64), revision 4

Rounds counted from the code (`yugen-proof-b2` `docs/parameters.md` 2a.4; calculator
`binius64.k_of`, `rounds_counted`): the wallet leaf has `k` = 182 challenges as built, a node at
most 663 with its batching transcript. Tree bound 20,000 proofs; the row is solved at a budget of
600 challenges a proof on average: **152.52 bits a round** (the counted sum of the largest tree
needs 151.36). Queries 368 / 225 / **184** / 168 at rates 1/2 to 1/16. Field needed 184 bits
(weakest algebraic round at 256 bits: 234.0 leaf, 225.0 for a node of 2^30 rows); GF(2^128) fails
(106.0, 97.0). Rate 1/8 for every layer. `docs/binius-extension-challenges.md` is the analysis of
where each object may live.

| Variant (rate 1/8, wallet leaf zero knowledge, pin layout) | Status | Queries | Wrapper constraints | Symbols: trace / wrapper / mask (B) | Ring-switch message (bits) | Leaf (KiB) | Node, 2^27 words (KiB) | Under 1.75 MiB | Leaf slot: AND rows; BMUL rows (E) |
|---|---|---|---|---|---|---|---|---|---|
| all in GF(2^256), as built (`Level::Cat1`) | **M**: leaf 633,280 B = 618 KiB; node circuit of 2^23 words 538,272 B | **184** | 2^21 | 32 / 32 / 32 | 65,536 | 614 (model; -0.7 %) | 697 (E) | yes | 8.08 M; 3.16 M (implementers: 8.7 M; 3 to 4 M) |
| all in GF(2^256), public transpositions direct (task W-1) | E | **184** | 2^19 | 32 / 32 / 32 | 65,536 | 614 | 697 | yes | 8.08 M; 3.16 M |
| **mixed: trace and first oracle in GF(2^128), challenges in GF(2^256), ring switch form T, W-1** | E; sound with the same round errors (Theorem 1, Lemma 3) | **184** | 2^18 | 16 / 32 / 32 | 32,768 | **568** | 699 | yes | 7.82 M; 3.16 M |
| mixed, ring switch form F | E; Theorem 2 to be reviewed | **184** | 2^17 | 16 / 32 / 32 | 32,768 | **529** | 699 | yes | 7.49 M; 3.16 M |
| mixed, form T, wrapper as is (task A-8 as worded) | E | 184 | 2^21 | 16 / 32 / 32 | 32,768 | 568 | 699 | yes | 7.82 M; 3.16 M |

Sizes: the opening model (Merkle openings with expected path sharing, cap at `ceil(log2 q)`,
terminal codeword) plus non-opening bytes fitted to the measured 256-bit proofs (four leaves,
errors -1.4 % to +1.8 %; one node proof); fold arities past the leaf chosen for size. Slot rows:
the measured pin slot (4.23 M AND, 0.79 M BMUL at 116 queries, **M**) scaled by queries and by
SHA-256 compressions a query; four BMUL rows a field product at 256 bits. Wrapper constraints:
the transposition model of `binius-extension-challenges.md` 5.1, which reproduces the two
measured wrappers. Masks are sampled in GF(2^256) in every mixed row (rule Z of that document:
a base-field mask under an extension challenge reveals the committed oracle). The revision-3
rows (512 other rounds, 17,477 proofs, committed derivation, estimated 256-bit layout) are in
`soundness/output/current-tables.txt` under their own heading.

Revision 5 replaces this candidate by the rows of `binius-johnson-row.md` section 7 (block "Revision 5"
above: 107 queries on the Haböck and on the DKT26 route, candidates under referee review). The
revision-4 text follows as the record.

Candidate, not a row: with 256-bit challenges BCIKS20's proven Johnson-regime gap leaves 168.2
bits at 2^27 elements and rate 1/8, which would allow **107 queries** (80 at rate 1/16). Haböck,
"Basefold in the List Decoding Regime", ePrint 2024/1571, Theorem 6 (read 2026-11-19) proves
round-by-round soundness of row-batched FRI-Binius in that regime with the same query count and a
fold round of 169.3 bits here; Binius64's ring switch, zero-knowledge mask round and lifted
oracles are outside that theorem (`binius-extension-challenges.md` 7 (d); `CITATION-AUDIT.md`
C-11).

#### Findings for the lead architect (revision 3)

- **S-8. Row 6 is 16.9 bits short of the tree target** (it was solved for the four-layer chain).
  Fix: row 6's schedule with the tree list (225, 156, 154, 153): done when the row's query list is
  `CAT1_TREE_UD_QUERIES` and `soundness` accepts the built row (`a_leaf_check(ROW6, queries)`).
  The margin is small everywhere (0.05 to 0.6 bits): the tree list must be re-derived if `k` is
  counted above 512 + the listed rounds, or if the tree may hold more than 17,477 proofs.
- **S-9. Hiding leaves need per-level query counts.** Under W-I the true rate of the last levels
  is up to 2^0.7 above nominal (row 8: 2^-4.3 for 2^-5), so a list by nominal level rate fails
  there. Fix: a `Queries::PerLevel` variant (counts per level of the shape) for hiding rows, or
  the counts computed from `wi::layout` at setup; done when row 8 carries 226, 160, 163 and the
  calculator accepts it. Row 6's schedule needs no change (its counts coincide with the list).
- **S-10. Residual 2^5 is a node-only lever.** Under W-I the lane of a deep last level is mostly
  random coefficients and alignment (true rate about 0.8): no count works. Leaves stop at 2^7 or
  above.
- **S-11. "At most 16" must mean packed nodes.** If a tree may use nodes with one child, the
  same 2^14 leaves give up to 81,920 proofs (+2.2 bits a round): the leaf needs 229, 159, 156,
  156 and row 9's level 0 fails. Fix: a consensus rule that every node but the last of its level
  is full (the specification's tree builder), done when a tree that violates it is refused; or
  the counts re-solved with `current.target(proofs=81_920)`.
- **S-12. B's leaf to 2^256 and to 184 queries is a factor 2 in size** (354 to 700 KiB) and 1.6
  in the verifying slot; the pin's layout (derived wires public) would save 138 KiB a leaf.
- **S-13. Not counted from the code:** `k` for Binius64 (512 assumed, task A-2 of
  `yugen-proof-b2`), the bus-layer and S9 counts in A's zero-knowledge list (`wi.AZk`, E), and
  every 16-child node statement (E).
- **S-14 (revision 4). Row 9 at rate 1/2 is 0.03 bits short at 20,000 proofs.** Fix: 368 queries
  at level 0 (the list `[0, 368, 225, 184, 168, ...]` re-derived with `current.target_bound()`),
  or node rate 1/4, whose list still meets. S-13's first item is closed (`k` counted for
  Binius64); A's bus, Keccak, S9 and gadget counts are now the built ones.
- **S-15 (revision 4). The 256-bit move of system B cost the wallet leaf a factor 4 in its
  wrapper for a reason that is not the field**: 18 of the wrapper's 20 bit transpositions are on
  public values and are constrained although the verifier recomputes them. Fix: task W-1 of
  `binius-extension-challenges.md` (2^21 to 2^19 constraints as built; 2^18 with the mixed field).
- **S-16 (revision 4). No field arrangement moves system B's recursion estimate by more than a
  few per cent**: the leaf slot is 184 queries of hashing. The candidate above (107 queries) is
  the one lever found; its PCS core is proven (ePrint 2024/1571, Theorem 6); the three parts of
  C-11 need their own list-decoding analysis and the external cryptographer's confirmation.


## 3. Measured anchors (M)

All on the Apple M5, one prover thread unless stated, load average below 8 at the time of each run.

| Run | Proof size | Prove | Verify | Peak RSS | Raw output |
|---|---|---|---|---|---|
| A leanVM, 589,976 cycles (128 Keccak compressions + 2^15 squarings; leaf-sized, stacked 2^24 by the model fit), GF(2^128), leanVM's own parameters (125-bit RBR claim), rate 1/2 | 290,584 B | 0.948 s | 2.96 ms | 890 MB | `system-a-leafsize-20261118.txt` |
| same, rate 1/4 | 202,664 B | 1.371 s | 2.31 ms | 1,300 MB | same |
| same, rate 1/8 | 170,628 B | 2.305 s | 2.19 ms | 2,121 MB | same |
| same, rate 1/16 | 153,688 B | 4.284 s | 2.02 ms | 3,631 MB | same |
| B Plonky3 binary, 655 Keccak-f (2^14 rows x 1,625 columns = 2^24.67 bits, leaf-sized), WHIR UD, GF(2^128), harness 100-bit target, rate 1/2 / 1/4 / 1/8 / 1/16 | 314,540 / 279,443 / 269,911 / 272,859 B | 0.151 / 0.163 / 0.203 / 0.273 s | 3 ms | 71 / 90 / 131 / 199 MB | `system-b-binary-engineering-20261118.txt` |
| same, GF(2^64) values with GF(2^192) challenges, rate 1/2 / 1/4 / 1/16 | 425,515 / 404,439 / 408,108 B | 0.730 / 0.728 / 0.916 s | 4 ms | 383 / 428 / 598 MB | same |
| Keccak-f[1600], `keccak` crate 0.1.6, one thread | 7.70 M permutations/s | | | | `system-a-leafsize-20261118.txt` |

Calibration: A's size model gives 290,963 B and 141,614 B for the two ends of the leanVM rate
sweep (+0.1% and -8%; A is not scaled); B's WHIR model is scaled by 1.33 to the 272,859 B run and
B's folding-PCS model by 1.45 to the step 0.3 run (434,434 B). Verify times are the measured
times scaled by the number of Keccak-f a verifier computes (0.83 µs per hash for A, 0.73 µs for B
including field work).

## 4. Rate, grinding and field trades (leaf)

From `soundness/output/design-tables.txt` (leanVM's own fold ladder for A, fold 4 for B; the
optimised schedules of Appendix A.3 are 20 to 35% smaller at every rate):

| Target | System | Rate | Size (KiB, E) | Verify (ms, E) | Prove, 1 M5 thread (s, E) | Peak RSS at GF(2^128) (MB, M) |
|---|---|---|---|---|---|---|
| cat1 | A | 1/2 | 678 | 8.9 | 3.5 | 890 |
| cat1 | A | 1/4 | 602 | 8.1 | 4.8 | 1,300 |
| cat1 | A | 1/8 | 591 | 8.2 | 7.6 | 2,121 |
| cat1 | A | 1/16 | 596 | 8.5 | 13.5 | 3,631 |
| cat1 | B | 1/2 | 540 | 4.9 | 1.6 | 71 |
| cat1 | B | 1/4 | 503 | 4.6 | 1.6 | 90 |
| cat1 | B | 1/8 | 504 | 4.7 | 1.7 | 131 |
| cat1 | B | 1/16 | 514 | 4.9 | 1.9 | 199 |

Prove = measured leaf-sized time at that rate x challenge-field factor + grinding. The factor for
a 256-bit challenge field is an **estimate**: 3 for A (three GF(2^128) products per GF(2^256)
product, applied to the whole prover: an upper estimate) and 5.0 to 7.2 for B (the measured
GF(2^192) factor of 3.4 to 4.8 times 1.5). Size is flat from rate 1/4 to 1/16 under unique
decoding (a query can never give more than one bit there: agreement `(1 + rho)/2 >= 1/2`), while
the prover time and memory roughly double per halving of the rate: **rate 1/4 for the leaf, 1/8
for host layers.** `cat3` scales sizes by about 1.7 and leaves prover times unchanged (same
codewords, more queries).

Query grinding (cat1, rate 1/4, leanVM ladder for A): 0 / 16 / 20 / 24 bits give 694 / 620 /
602 / 583 KiB for A and 579 / 520 / 503 / 488 KiB for B, at 0 / 0.04 / 0.68 / 10.9 s of
grinding on one M5 thread. 20 bits is the knee. Measured in B (folding PCS, 2^14 rows, harness
100-bit target, rate 1/4): pow 0 / 8 / 16 / 20 / 24 gave 357,940 / 341,216 / 315,976 / 305,177 /
296,319 B (M), the same slope as the model (-15% from 0 to 20 bits).

Challenge field at `cat1`: GF(2^128) fails (`docs/soundness-method.md` 8.4; 2^35 to 2^46
Keccak-f of grinding per proof); GF(2^192) reaches `cat1` with 10 to 14% smaller proofs than
GF(2^256) (A leaf 534 against 602 KiB, B leaf 437 against 503 KiB, leanVM ladder) but not `cat3`.

## 5. Proof-size engineering for the leaf

Techniques available at fixed security, with their effect. "M" effects were measured in
`bench/results/system-b-binary-engineering-20261118.txt` (B, 2^14 rows, folding PCS unless noted,
harness 100-bit target) or the leanVM sweeps; "E" effects come from the calculator at `cat1`.

| # | Technique | A (leanVM) | B (Plonky3 binary) | Effect |
|---|---|---|---|---|
| 1 | Larger challenge field only where needed | GF(2^256) as a quadratic extension of leanVM's GF(2^128) for every verifier challenge (fork work) | a degree-4 extension of `Poly64` (upstream has `Poly192` only) | not a size lever: needed for `cat1`/`cat3`; GF(2^192) instead saves 10-14% at `cat1` (E) but blocks the parameter-only path to `cat3` |
| 2 | Rate | runtime parameter (1/2..1/16) | runtime parameter | 1/2 to 1/4: -11% (A), -7% (B) (E); below 1/4 flat; measured at 100-bit harness: B WHIR 314.5 to 279.4 to 269.9 to 272.9 KB (M), A leaf-sized 284 to 198 to 167 to 150 KiB at leanVM's Johnson-regime queries (M) |
| 3 | Fold schedule (first fold, later folds) | constants `INITIAL_FOLDING_FACTOR` 6, `SUBSEQUENT_FOLDING_FACTOR` 4 in `crates/verifier/src/whir.rs` | harness `folding`; WHIR schedule internal | folds of 3 to 4 are optimal; 6 or more costs 70-140% (E). Measured, folding PCS: fold 1/2/3/4/5/6 gave 635/384/343/358/439/681 KB (M) |
| 4 | Final polynomial size (stop folding earlier, send 2^9 to 2^12 coefficients) | `RESIDUAL_MAX_LOG` 5 | WHIR stops at 6 at the pin (inferred from the 319 = 112 + 104 + 103 opened positions) | **the largest lever under unique decoding**: every query round costs about 116 queries regardless of rate, so removing one round (about 100 KiB) for a 32 KiB final polynomial saves 20-35%: A 602 to 443 KiB, B 503 to 325 KiB at rate 1/4 (E) |
| 5 | Query / grinding balance | `QUERY_GRINDING_BITS` constant (17) | `pcs_pow_bits` (folding); WHIR budget | 20 bits: -13 to -15% for 0.5-0.7 s of grinding (E); measured -15% at 20 bits (M); needs F5 for the QROM condition |
| 6 | Merkle arity | binary | 2 or 4 | binary is smaller: arity 4 costs +9% (358 against 329 KB, M) but saves two thirds of prover compressions; leaf proofs use arity 2 |
| 7 | Merkle leaf width (elements per leaf) | one fold coset | `leaf_elements` | the default (one fold coset per leaf) is optimal: 4 / default 16 / 64 / 256 elements gave 359 / 358 / 621 / 1,508 KB (M) |
| 8 | Merkle cap | none | cap 6-7 at the pin | small and negative for proof size at these query counts: cap 0 / 6 / 10 gives 602 / 612 / 702 KiB (A, E); a cap only saves verifier hashing |
| 9 | Path deduplication (multi-opening) | shared upper levels | shared upper levels | already in every figure (the model shares the top `log2 t` levels); worth about 6-7 of 20-25 sibling digests per query |
| 10 | Batching openings across columns | the stacked commitment: one polynomial for all columns | stacked trace commitment | already in every figure; B's alternative of one tree per table would multiply round-0 openings |
| 11 | 256-bit digests (attack rule) instead of 264 (proven rule) | | | -1 to -2% (E) |
| 12 | Compression recursion step (phone or host) | | | **does not shrink the proof at fixed proven security**: a compression layer proving the leaf verifier commits about 2^24-2^25 cells and lands at 512-590 KiB (the merge2 row), more than the optimised leaf. It helps prover memory (phone proves at rate 1/2, host recompresses), not size. Under the unconfirmed Johnson bound a rate-1/8 compression layer gives 199-235 KiB against the rate-1/4 leaf's 232: at most 14%, about what moving the leaf itself to rate 1/8 gives |
| 13 | Sumcheck/fold grinding | `FOLD_GRINDING_BITS` 7 | `sumcheck_pow_bits` | no effect on size at a 256-bit field (algebraic rounds have 150+ bits of slack); 8 bits per round measured: +195 B, same time (M) |

(Section 2a supersedes the grinding and the sizes in this paragraph: no grinding, a
`2^14`-leaf tree, the built statement sizes.) **Recommended leaf configuration (both targets, one code path):** 256-bit challenge field;
rate 1/4; WHIR with first fold 5 and later folds 3 to 4, folding stopped at 10 to 11 variables
(final polynomial of 2^10 to 2^11 coefficients sent in clear); binary Keccak Merkle trees with
one fold coset per leaf, no cap; query grinding 20 bits with the grind-0 set held ready until E3
rules on F5; digests 256 bits (`cat1`) / 384 bits (`cat3`). Every one of these is a parameter in
B's harness except the WHIR stopping point; in A all are compile-time constants and the query
table is hard-coded (`WHIR_QUERIES`), which must become a parameter table for the parameter-only
path. Estimated leaf: A 443 KiB / 7.4 ms verify, B 325 KiB / 2.6 ms at `cat1`; A 751 KiB, B 522
KiB at `cat3`.

## 6. What is not settled

- Every size and verify time here is a model estimate; E1 measures the real leaf, E2 the bundle.
- The statement sizes (A 2^24 cells, B 2^19 elements for the leaf; 2^26 to 2^28 for recursion)
  are the step 0.3 estimates.
- The 256-bit challenge-field prover factors are not measured (neither framework has the field at
  the pin).
- **Prover memory:** leanVM's leaf-sized run needs 0.9 GB at rate 1/2 and 1.3 GB at rate 1/4
  (M), over E1's 512 MB; B needs 90 MB at GF(2^128) and 428 MB on its GF(2^192) path (M) at rate
  1/4. A needs a memory-bounded prover (streamed commitment) before E1, or E1's memory limit
  moves.
- Conditions Q (with grinding) and the hash rule rest on F5 and on NIST's benchmark ordering
  respectively (`soundness-method.md` 8.6).

## Appendix A. Superseded rows

### A.1 Former section 2a: category 1 for a tree of about 1,700 proofs, with 20 bits of query grinding (2026-11-19, first revision)

**Superseded** by section 2a (revision 2): it assumed 1,700 proofs, relied on query grinding
(which counts for condition Q only under the unconfirmed argument F5), used the step 0.3 statement
sizes (A `2^24`, B `2^19`), counted only the openings' rounds in `k`, and modelled B's recursion
with the folding PCS. Kept as the record.

Decisions of the lead architect: the target is `cat1` for a block's whole proof tree of about
1,700 proofs (`soundness-method.md` 8.5a; shared-budget model; about 144 bits per round); system A's
leaf opening is W-I, system B's is W-M (`zk-wi-soundness.md`). Same schedules, field, rates, digests
and query grind (20 bits) as the `cat1` rows above. Every number is **E** (calculator estimate,
`uv run yugen-soundness --wi`, `soundness/output/wi-tables.txt`; B scaled by the measured factor
1.33); nothing in this table is measured.

| System | Layer | Opening | Queries per round (E) | Lane lengths, coefficients (E) | Rates (E) | Size (KiB, E) | Per-proof target, for comparison (KiB, E) |
|---|---|---|---|---|---|---|---|
| A | leaf | W-I | 184, 128, 125, 125 | 524733, 65923, 8448, 1280 (folded lanes) | 0.25021, 0.01572, 0.00403, 0.00122 | **482** | 455 |
| A | bundle, merge1 | not hiding | 150, 125, 125, 125 | `2^22, 2^18, 2^14, 2^10` | `2^-3` at level 0, then `2^-8, 2^-11, 2^-14` | **625** | 589 |
| A | merge2 | not hiding | 150, 126, 125, 125 | folds 5/4/4/4, final `2^9` | `2^-3` at level 0 | **545** | 512 |
| B | leaf | W-M | 183, 127 | `2^14, 2^10`, level-0 lanes of `p` carry 183 more coefficients at offset `2^14`; mask polynomial `m`: `2^19` elements of `F` | `2^-2` (0.2528 for `p`'s level-0 rows), `2^-6` | **524** | 497 |
| B | bundle, merge1 | not hiding | 150 | folding PCS fold 4, final `2^8` | `2^-3` | **904** | 850 |
| B | merge2 | not hiding | 150 | folding PCS fold 4, final `2^11` | `2^-3` | **823** | 779 |

For reference, B with W-I would be 359 KiB (185, 128 queries; lanes 16825, 1280): W-M costs 165 KiB
per B leaf and a second level-0 codeword (64 MiB at rate 1/4) in B's prover, not measured. Grind 0
(no reliance on F5): recursion layers 174, 146, 145, 145 (A; 712 / 619 KiB) and 174 (B; 1,034 /
929 KiB). `cat3` tree-wide rows are not computed yet.

Every row meets conditions C, Q, G and H of its target (asserted when the table is generated). The
proven-digest variant (264/392 bits) adds 1 to 2% to the leaf (`design-tables.txt`, last table).

### A.2 Former section 2a, revision 2: a tree of 64-leaf sub-bundles and two merge levels, system B on Plonky3 (2026-11-19)

**Superseded** by section 2a (revision 3): the tree is now specification 0.3's (16-leaf sub-bundles, three merge levels, 17,477 proofs); system A's leaf is counted at the true W-I rates with every zero-knowledge round; system B is Binius64, so every B row below (Plonky3 W-M leaf, Plonky3 binary WHIR nodes) is obsolete. Kept as the record; findings S-1 to S-7 below still apply where they name system A or the method.

Decisions of the lead architect, which this section implements:

1. The whole bundle tree meets `cat1` for a tree of sub-bundles of at most 64 leaves and two merge
   levels of arity at most 16: 2^14 leaves, 2^8 sub-bundles, 2^4 first merges and one root,
   **16,657 proofs** (`2^14.02`; the calculator counts every proof of the full tree, not 2^14). This
   replaces the 1,700-proof assumption.
2. No grinding anywhere: every query, fold, OOD and batch grind is 0.
3. Proven bounds only: unique-decoding proximity (BCIKS20), the book's BCS bound, CMS19.
4. 256-bit digests (384 for `cat3`).
5. System A's leaf opens with W-I, system B's with W-M (`zk-wi-soundness.md`).
6. Every proof at most 1.75 MiB (1,792 KiB).

The tree model, the security definition and what multi-attempt and multi-block attackers change:
`soundness-method.md` 8.5b. In short: union bound over the 16,657 proofs for one attempt, every
round of a proof counted in `k` (512 rounds outside the openings, an upper figure: finding S-1
below), so a round needs **152.1 bits at `cat1`** and **216.1 at `cat3`**.

Generated by `cd soundness && uv run yugen-soundness --ship` (`soundness/src/yugen_soundness/shipping.py`,
tests `tests/test_shipping.py`); the full output, including the `cat3` rows and the variants, is
`soundness/output/shipping-tables.txt`. **M** marks a measured input, **E** an estimate.
Statement sizes: A's leaf is the built wallet statement (`2^22` words, **M**), B's leaf the built
statement (`2^23.38` bits as `2^18` 64-bit words, plus the `2^18` preprocessed schedule, **M**);
every recursion statement is **E**, from the measured cost of verifying a proof in A's node
(cycles, Keccak-f, words a cycle) and in B's bundle circuit (Keccak-f, witnesses, cells a witness),
times the child count. Every size, query count and cost below is **E**.

##### Shipping rows, `cat1`, leaf rate 1/4, node rate 1/4

| System | Layer | Opening | Statement committed | Queries per round | Folds, final | Challenge field needed (bits) | Size (KiB) | Under 1.75 MiB | Verifier Keccak-f: model / in circuit | Relative prover cost |
|---|---|---|---|---|---|---|---|---|---|---|
| A | leaf | W-I | 2^22 words (M) | 225, 156, 154 | 5/3/3 to 2^11 | 177: GF(2^192) | **449** | yes | 7,915 / 9,351 | 3 |
| A | sub-bundle | plain | 2^29.72 words | 225, 160, 153, 153, 153 | 4/4/4/4/4 to 2^10 | 185: GF(2^192) | **852** | yes | 18,540 / 21,904 | 768 |
| A | merge 1 | plain | 2^28.63 words | 225, 154, 153, 153 | 6/4/4/4 to 2^11 | 184: GF(2^192) | **773** | yes | 14,772 / 17,452 | 384 |
| A | merge 2 | plain | 2^28.37 words | 225, 154, 153, 153 | 6/4/4/4 to 2^11 | 184: GF(2^192) | **773** | yes | 14,772 / 17,452 | 384 |
| B | leaf | W-M, and the preprocessed schedule (plain) | 2^18 + 2^18 words (M) | 226, 160; 225, 160 | 4/3 to 2^11 (both) | 173: GF(2^192) | **834** | yes | 8,627 / 12,501 | 40 |
| B | sub-bundle | plain, one stacked commitment | 2^31.05 + 2^27.86 GF(2^128) cells | 225, 156, 153, 153, 153 | 5/4/4/4/4 to 2^11 | 187: GF(2^192) | **1,472 to 1,919** | only at the low end | 20,581 / 26,360 | 219,546 |
| B | merge 1 | plain, one stacked commitment | 2^29.14 + 2^26.94 cells | 225, 160, 153, 153, 153 | 4/4/4/4/4 to 2^10 | 185: GF(2^192) | **1,342 to 1,790** | yes | 18,765 / 24,255 | 54,886 |
| B | merge 2 | plain, one stacked commitment | 2^29.14 + 2^26.82 cells | 225, 160, 153, 153, 153 | 4/4/4/4/4 to 2^10 | 185: GF(2^192) | **1,342 to 1,790** | yes | 18,765 / 24,255 | 54,886 |

Columns: *rate* is the level-0 rate; later levels follow the WHIR ladder (the rate falls by
`fold - 1` bits a level). *Queries per round* are the solved counts for 152.1 bits a round, minimal
(each count less by one fails; tested). *Challenge field needed* is the smallest field at which
every round of the row, at those queries, meets the target (the `n / |F|` fold terms and the
`t / |F|` combination terms); the sizes are computed on GF(2^256), the field both systems are being
built with, so that `cat3` is a parameter change. *Size* is the calibrated model (calibration
below); for B's nodes it is a range because 458 KB of B's measured layer proofs are not explained
by the opening model (finding S-3): the low end keeps them at their measured size, the high end
doubles them for the 256-bit field. *Verifier Keccak-f*: the model counts the Merkle hashing of
the openings (leaves and deduplicated paths, Keccak-256 rate 136 bytes); *in circuit* is the
calibrated count a parent's circuit performs to verify this proof (A: 1.18 x the model, fitted to
four measured leaf verifications within 2.4%; B: 2,500 fixed + 1.16 x the model, one measured
point). *Relative prover cost*: committed codeword bytes (all committed polynomials, W-M's mask
included) x the 256-bit challenge-field factor (3 for A, 6.7 for B), against the measured leaf
run of the same system at rate 1/4 with 128-bit challenges.

With B's node tables in two commitments, as built at the pin, the B nodes are **2,135 to 2,691
KiB: over the limit** (`shipping-tables.txt`, second table). Proven-rule digests (264 bits)
add 0.7 to 1.8% to every row (A leaf 455, sub-bundle 867, merges 784 KiB).

##### `cat3` (384-bit digests, 216.1 bits a round), same rates

| System | Leaf | Sub-bundle | Merge 1, merge 2 | Field needed | Every proof under 1.75 MiB |
|---|---|---|---|---|---|
| A | 321, 219 queries; 6/4 to 2^12; **717 KiB** | 319, 219, 217, 217; **1,403 KiB** | **1,297 KiB** | 241 to 249 bits: GF(2^256) | **yes** |
| B | 322, 227; 319, 227; **1,147 KiB** | stacked: **2,227 to 2,675 KiB** | stacked: **2,026 to 2,474 KiB** | 237 to 251 bits: GF(2^256) | **no**: leaf yes, every node over (as built: 3,551 to 4,087 KiB) |

##### Leaf rate trade (`cat1`; node rate 1/4)

The leaf is proven on a phone and verified once, inside a sub-bundle; what the sub-bundle pays per
leaf is the in-circuit Keccak-f (and, for A, the cycles that follow from them).

| System | Leaf rate | Queries | Leaf size (KiB) | Verifier Keccak-f of one leaf: model / in circuit | Sub-bundle cost per leaf | Leaf prover cost (relative) |
|---|---|---|---|---|---|---|
| A | 1/2 | 370, 160, 155 | 514 | 9,092 / 10,742 | 498,081 cycles | 1.5 |
| A | **1/4** | 225, 156, 154 | **449** | 7,915 / 9,351 | 454,227 cycles | 3.0 |
| A | 1/8 | 184, 154, 153 | 438 | 7,836 / 9,258 | 451,280 cycles | 6.0 |
| B | 1/2 | 377, 167; 367, 167 | 982 | 10,442 / 14,605 | 14,605 Keccak-f, 5.69 M witnesses | 20 |
| B | **1/4** | 226, 160; 225, 160 | **834** | 8,627 / 12,501 | 12,501 Keccak-f, 4.42 M witnesses | 40 |
| B | 1/8 | 184, 156; 184, 156 | 800 | 8,406 / 12,246 | 12,246 Keccak-f, 4.04 M witnesses | 80 |

Under unique decoding a query gives at most one bit, so only the level-0 round gains from a lower
rate: from 1/4 to 1/8 the leaf shrinks 2 to 4% and its verification 1 to 2%, for twice the
phone's codeword; from 1/4 to 1/2 the leaf grows 14 to 18% and the sub-bundle's cost per leaf 10
to 17%. **Rate 1/4 for the leaf.** `cat3` shows the same shape (A 825 / 717 / 683 KiB; B 1,371 /
1,147 / 1,104 KiB). For nodes, rate 1/2 costs the parent 45% more hashing per merge child for A
(25,342 against 17,452 Keccak-f) and rate 1/8 saves under 3% for twice the codeword: **rate 1/4
for nodes.**

##### Calibration

| Model | Fitted to (M) | Error at the other measured points |
|---|---|---|
| A leaf size: opening model + 9,004 B of other transcript at 128-bit challenges (doubled at 256) | row 1, rate 1/4, 347,704 B | row 1 rate 1/2 (388,652 B) +2.2%; row 3 salted (367,480 B) -0.1%; row 0 rate 1/4 (173,276 B) -6.1%, rate 1/2 (247,420 B) +1.0% |
| A node size: 0.963 x (model + transcript) | mean over three row-4 node proofs | bundle of 1 (539,164 B) +1.2%; bundle of 8 (640,664 B) +1.7%; merge (541,080 B) -2.8% |
| A in-circuit Keccak-f per verified leaf: 1.18 x model | four measured leaf verifications (rows 0, 4; rates 1/2, 1/4) | within 2.4% at each |
| A cycles per verified proof: 88,479 + 17.5 x Keccak-f, x1.8 on the 256-bit field (E, yugen-proof-a `recursion.md` 5) | the same four | within 6.2% |
| B leaf size (WHIR): opening model + 123,064 B of opened values at 128-bit (doubled at 256) | mean over the three WHIR leaf runs (853,779 / 942,419 / 841,715 B) | -0.7%, +0.9%, -0.3% |
| B leaf size, folding PCS (the 793,916 B run) | own fit needs 381,580 B of other transcript | rate 1/2 (991,023 B) -2.5% with its own fit; with the WHIR runs' transcript the folding model is 33% low: it is not used (finding S-4) |
| B node size: opening model + 458,139 B | mean of the two measured layer proofs (1,235,695 / 1,191,423 B) | -1.8%, +1.9% |

No proof at these parameters has been measured: neither framework has the 256-bit challenge field
end to end yet, and none of the recursion statements above has been built at its size.

##### Findings for the lead architect

- **S-1. Every round counts in `k`.** The book's `(t + k) eps_rbr` counts all rounds of the IOP;
  the calculator counted the opening's rounds only. With 512 further rounds per proof (bus GKR,
  table sumcheck, Keccak reduction, ring switch: an upper figure, **E**) a round needs about 4
  bits more (152.1 instead of 148.0). Task: count the non-opening rounds of each built prover and
  record them per system in `shipping.OTHER_ROUNDS`; done when the number is taken from the
  provers' transcripts and the tables are regenerated.
- **S-2. 256-bit digests and proven bounds are 1.4 bits apart.** The book's hash term
  `3.5 t^2 / 2^lambda`, counted once for the tree, caps the proven classical level at 126.6 bits
  with `lambda = 256`. Category 1 holds under the attack rule H (NIST's own ordering of its
  benchmarks); under "proven bounds only" it needs 264-bit digests, which cost 0.7 to 1.8% per
  proof (table above). Decision needed: H by the attack rule, or 264-bit (33-byte) digests.
  *Revision note (2026-11-19, calculator revision 10):* the spBCS transcript's own theorem (Sharp,
  Grubbs, ePrint 2026/2615, Theorem 6.6 (2)) puts the hash term per proof with the factor `c'`
  (about 2,400): summed over a tree of 20,000 proofs the proven classical level is **114.74 bits,
  not 126.6**, and "proven bounds only" needs **288-bit (36-byte) digests, not 264**
  (`decision-qrom-counting.md` 7.2 to 7.4). Category 1 still holds under the attack rule H.
  *Amendment (2026-11-19, calculator revision 10.2, after `docs/tree-extraction-referee.md`; not a rewrite):* every TREE figure in this passage is conditional, not an unconditional theorem. It holds under the recursion heuristic C2 (the event "accepted in-circuit, rejected natively" does not occur; no random-oracle proof can remove it), the owed obligations K-A and K-B (round-by-round knowledge soundness) and T-1 (the transcripts' domain separation and fit to [SG26] Protocol 6.5). Under Theorem TE' (`docs/lemma-tree-extraction.md` revision 2) the classical hash level of the tree is **121.89 bits at category 1** (185.89 / 249.89 at categories 3 / 5), printed with the per-proof union (114.74 / 178.74 / 242.74) beside it as the comparison; the tree's QROM figures are derived under C2, never "proven QROM". Status of every claim: `docs/what-is-proven.md`.
- **S-3. B's nodes exceed 1.75 MiB as built**, and meet it at `cat1` only with one stacked
  commitment and only if the unexplained 458 KB of B's measured layer proofs does not grow with
  the field. Tasks: (a) the node's dense and packed tables in one commitment (Plonky3-recursion's
  mixed commitment holds one dense and one packed table at the pin); (b) a byte breakdown of a B
  layer proof, done when every byte is attributed to an opening, opened values or a sumcheck/GKR
  message and the model reproduces the proof within 3%; (c) for `cat3`, B's nodes need a smaller
  opening (the dense cells are 16 bytes; 64-bit cells, as task F-2 does for the leaf, are expected to halve the
  level-0 rows: not computed): done when `--ship` shows every B node under 1.75 MiB at `cat3`.
- **S-4. The folding-PCS model under-predicts B's folding leaf by about 260 KB**, so the old
  basis's B recursion rows (folding PCS, 850 to 904 KiB) were too low. B's recursion is built on
  WHIR (`yugen-proof-b/docs/recursion.md` section 2), and every B layer here is WHIR.
- **S-5. The recursion statements of this tree shape are large.** A 64-leaf sub-bundle is about
  `2^30` words for A (padded: a 32 GiB level-0 codeword at rate 1/4) and about `2^31` cells for
  B (padded to `2^32` cells of 16 bytes: 64 GiB of table, a 256 GiB codeword): no single commodity host proves it (yugen-proof-a measured 6.9 GB at 8 leaves). The fix
  that keeps the tree's soundness: prove a sub-bundle as bundles of 8 and a merge of 8 (a third
  merge level). The tree then has `2^14 + 2^11 + 2^8 + 2^4 + 1 = 18,705` proofs, `+0.17` bits a
  round, at most one query more a round; the node statements fall to about `2^27` words (A).
  Decision needed: allow the extra level, or keep 64-leaf sub-bundles and set a host memory
  requirement.
- **S-6. B's leaf is dominated by what is not the opening**: 246 KB of opened values (about 9,100
  at 32 bytes) and a second opening for the preprocessed schedule (234 KiB). Levers: fewer
  columns (yugen-proof-b T-3), and the preprocessed schedule batched into the main opening; done
  when `--ship` shows B's leaf with one opening.
- **S-7. GF(2^192) would suffice for `cat1` at every layer** (172 to 188 bits needed) and
  GF(2^256) for `cat3` (236 to 252). B's `cat3` sub-bundle has 4 bits of field margin: a larger
  statement needs a larger field.

### A.3 Former section 2: the per-layer table of 2026-11-18 (system B on Plonky3)

**Superseded** by section 2a. 20 bits of query grinding, step 0.3 statement sizes, four-layer chain, system B on Plonky3.

Both systems, every layer, both targets. Unique decoding (UD) uses confirmed proximity bounds
only; the Johnson column uses DKT26's Johnson-radius MCA bound (P4/P5; ePrint 2026/2056, Theorem
4.4, read 2026-11-19: the bound is proved, the protocol theorems for these codes are not written,
`CITATION-AUDIT.md` C-14, C-15) at the same schedule and is shown only for comparison. Leaf at rate 1/4 (phone prover, memory), recursion layers at rate
1/8 (host). Schedules are the size-optimal ones found by `design.optimise` (first fold 4 to 8,
later folds 3 to 5, folding stops at 5 to 12 variables, the rest sent in clear). Digests 256 bits
(`cat1`) and 384 bits (`cat3`), 32-byte salts on the leaf's opened leaves (zero knowledge), none
in recursion layers (R-9).

"Query grind" 20 bits is counted in full classically (F4) and halved in the QROM (F5, our
argument, unconfirmed; F4 is ethSTARK, ePrint 2021/582, Theorems 6 and 8, read, C-17); the last
column is the set that meets every condition without F5.
"Prover factor" is the committed-codeword ratio times the challenge-field factor, against the
measured leaf-sized run of the same system at the same rate with GF(2^128) challenges (section 3):
A against 2^24 cells, 1.37 s at rate 1/4 and 2.31 s at 1/8; B against 2^18.67 GF(2^64)
elements, 0.163 s at 1/4 and 0.203 s at 1/8, one M5 thread. Grinding is not in the factor
(0.5 to 0.7 s per proof at 20 bits, section 4).

| System | Layer | Target | Field | Rate | Schedule | Queries per round (E) | Query grind | Size UD, proven (KiB, E) | Verify UD (ms, E) | Prover factor (E) | Size Johnson DKT26, unconfirmed (KiB, E) | Grind 0: queries / size (KiB, E) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | leaf | cat1 | 2^256 | 1/4 | WHIR folds 5/3/3/3, final 2^10 | 171, 119, 117, 116 | 20 | 443 | 7.4 | 3 | 232 | 200, 139, 137, 136 / 503 |
| A | bundle | cat1 | 2^256 | 1/8 | WHIR folds 6/4/4/4, final 2^10 | 140, 117, 116, 116 | 20 | 589 | 9.0 | 48 | 235 | 164, 137, 136, 136 / 674 |
| A | merge1 | cat1 | 2^256 | 1/8 | WHIR folds 6/4/4/4, final 2^10 | 140, 117, 116, 116 | 20 | 589 | 9.0 | 48 | 235 | 164, 137, 136, 136 / 674 |
| A | merge2 | cat1 | 2^256 | 1/8 | WHIR folds 5/4/4/4, final 2^9 | 140, 117, 116, 116 | 20 | 512 | 8.1 | 12 | 199 | 164, 138, 136, 136 / 587 |
| A | leaf | cat3 | 2^256 | 1/4 | WHIR folds 5/4/4, final 2^11 | 265, 184, 181 | 20 | 751 | 9.3 | 3 | 403 | 295, 205, 201 / 820 |
| A | bundle | cat3 | 2^256 | 1/8 | WHIR folds 5/4/4/4, final 2^11 | 217, 182, 180, 180 | 20 | 1056 | 14.0 | 48 | 413 | 241, 202, 200, 200 / 1156 |
| A | merge1 | cat3 | 2^256 | 1/8 | WHIR folds 5/4/4/4, final 2^11 | 217, 182, 180, 180 | 20 | 1056 | 14.0 | 48 | 413 | 241, 202, 200, 200 / 1156 |
| A | merge2 | cat3 | 2^256 | 1/8 | WHIR folds 6/4/4, final 2^12 | 217, 181, 180 | 20 | 879 | 10.0 | 12 | 430 | 241, 201, 200 / 953 |
| B | leaf | cat1 | 2^256 | 1/4 | WHIR folds 5/4, final 2^10 | 171, 119 | 20 | 325 | 2.6 | 8 | 210 | 200, 139 / 365 |
| B | bundle | cat1 | 2^256 | 1/8 | folding PCS fold 4, final 2^8 | 140 | 20 | 850 | 7.8 | 3797 | 524 | 164 / 980 |
| B | merge1 | cat1 | 2^256 | 1/8 | folding PCS fold 4, final 2^8 | 140 | 20 | 850 | 7.8 | 3797 | 524 | 164 / 980 |
| B | merge2 | cat1 | 2^256 | 1/8 | folding PCS fold 4, final 2^11 | 140 | 20 | 779 | 6.6 | 1899 | 514 | 164 / 885 |
| B | leaf | cat3 | 2^256 | 1/4 | WHIR folds 5/3, final 2^11 | 265, 184 | 20 | 522 | 3.8 | 8 | 353 | 295, 205 / 563 |
| B | bundle | cat3 | 2^256 | 1/8 | folding PCS fold 4, final 2^12 | 217 | 20 | 1507 | 11.1 | 3797 | 993 | 241 / 1640 |
| B | merge1 | cat3 | 2^256 | 1/8 | folding PCS fold 4, final 2^12 | 217 | 20 | 1507 | 11.1 | 3797 | 993 | 241 / 1640 |
| B | merge2 | cat3 | 2^256 | 1/8 | folding PCS fold 4, final 2^11 | 217 | 20 | 1356 | 10.4 | 1899 | 866 | 241 / 1482 |

#### A.3.1 Reading the table (the record of 2026-11-18)

- **Leaf at `cat1` under proven bounds: about 443 KiB (A) and 325 KiB (B).** The plan's 55 KB
  is not reachable at any target with proven bounds; the unconfirmed Johnson bound would give
  about 210 to 230 KiB.
- **Bundle proofs at `cat1`: 589 KiB (A), 850 KiB (B), inside E2's 1.5 MiB.** At `cat3` B's
  bundle (1,507 KiB with grinding, 1,640 KiB without) sits at or over 1.5 MiB with the folding
  PCS; B's recursion layers on WHIR would give 1,388 / 1,521 KiB (`design-tables.txt`, last
  section), which needs an in-circuit WHIR verifier that Plonky3-recursion does not have at the pin.
- **B's recursion prover factors (about 1,900 to 3,800) are the codeword ratio of an estimated
  2^26 to 2^28-element bundle statement against a 2^18.67-element measured run**, not a
  measured slowdown; E2 measures them. A's factor 48 for a bundle is 16 times the cells at a
  three-times-slower challenge field.
- Statement sizes are the step 0.3 estimates (A leaf 2^24 cells, which the leaf-sized leanVM run
  supports: section 3; B leaf 2^19 elements); E1/E2 replace them.
