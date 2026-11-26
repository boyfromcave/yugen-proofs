# Calculator changelog

Every changed number, before and after. Output tables: `output/`. Tests: `uv run pytest`.

## Census of system A beside the estimate (2026-11-19): `census.py`, `--census`; no figure changes

After `docs/theorem-s-referee.md` M-3. New module `census.py` (input `census/a-round-census.json`, test
`tests/test_census.py`, output `output/census-tables.txt`, flag `yugen-soundness --census`): the verifier's messages
walked one by one with their errors (`docs/round-census-a.md`). **No certified figure, count or status changes**:
`OTHER_ROUNDS` stays 512 and `hashterm.REPORTED_KQ` stays empty. Printed beside the estimate: row 8 leaf 445
messages against 599 (k_q 16,820 against 17,436 at 233/166/168/185; margin +0.106 -> +0.158 bits); every row with a
measured or derived census meets its need; row 9 at `2^30` misses on an extrapolated count only (-0.018 / -0.022
bits; restored by one query at the near-binding levels).

## Revision 10.2, footer wording (2026-11-19): aligned with `docs/what-is-proven.md` revision 2

After `docs/qc-and-status-referee.md` and `docs/lemma-tree-extraction.md` revision 3. **No figure, no query count and
no row status changes** (`test_no_query_count_and_no_status_changes` passes against the same 648-row snapshot); only
text: the footer (`category.PROVEN_FOOTER`) no longer says "proven in the random-oracle model" of figures whose
conditions include owed items (it says "conditional" in the status page's terms) and reads C2 as a joint probability
that equivalence tests do not discharge; adds (3a) C-4, met by design, by search, not audited, and (3b) H-BIND as
collision resistance of the concrete statement digests; Theorem TE' at revision 3 (revisions 1 and 2 refereed, pass
with conditions; revision 3 unrefereed); Lemma QC refereed, pass. The tree-QROM table's heading names H-BIND and Lemma
QC (refereed, pass). Docstrings of `hashterm.tree_extraction_level` and `lemma_qc_log2` updated. Outputs regenerated
(the five files of revision 10.2; text lines only). Tests: 465 pass.

## Revision 10.2 (2026-11-19): the tree figures after the referee's report on Lemma TE

After `docs/tree-extraction-referee.md` (F-1 to F-7, conditions C-1 to C-7) and `docs/lemma-tree-extraction.md`
revision 2 (Theorem TE', Proposition TE-Q', Lemma QC). Outputs regenerated: `output/revision10-tables.txt` (no flag),
`revision10-category-tables.txt` (`--rev7`), `revision10-proven-basis-tables.txt` (`--hash-basis proven`),
`revision7-tables.txt` (`--rev7 --convention t-ge-kq`), `revision8-tables.txt` (`--rev8 --convention t-ge-kq`); only
the hash-term summary, the new tree-QROM table and the footer change. Tests: `tests/test_revision10_2.py` (14); 465 in
all. **No query count and no row status changes**: `test_no_query_count_and_no_status_changes` compares every row of
every type, category, convention and hash basis (648 rows) with `tests/data/query_counts_rev10_1.json`, generated at
revision 10.1 (`e6a2d23`) before any change.

| Item | Change | Before | After |
|---|---|---|---|
| Classical tree hash level (task D) | `hashterm.tree_extraction_level` is the level of Theorem TE'; `HashTerm.classical_tree_te`, `classical_margin_te`; `category.tree_te_level` (`c'_max` over the system's rows, `K = N k_q,max`); the summary prints TE' "under C2, K-A, K-B, T-1" with the per-proof union beside it | "Classical, tree" 114.74; shortfall 13.26; digest 288 | "Classical, tree, Theorem TE' (under C2, K-A, K-B, T-1)" **121.89**, union 114.74 beside it; shortfall 6.11 / 13.26; digest 272 / 288 (cat 3: 185.89 / 178.74, 400 / 416; cat 5: 249.89 / 242.74, 528 / 544) |
| Proven-basis check | keeps the union (the lower figure); `HashTerm.classical_tree`, `classical_margin`, `digest_needed` unchanged | - | tested: at every profile's digest both figures are below `kappa_C`, no status depends on the choice |
| Tree QROM (task D) | `category.tree_qrom_summary`: the per-proof union (claimed) beside the one-table form of Proposition TE-Q' | - | A **69.58** (claimed) / 76.72; B **70.45** / 77.60; hash 75.63 / 80.40; label "under C2, K-A, K-B, T-1" |
| Lemma QC term | `hashterm.lemma_qc_log2(K - k_q,r, 8b)` = `log2(10 (K - k_q,r)) - 8(b + e)` at `e = 0` | - | cat 1: -222.91 (A), -223.09 (B; -222.20 at `k_q` 74,940); cat 3 about -350.4; cat 5 about -478.1 |
| Verdict wording | the quantum verdict of the hash-term summary | "meets (proven)" | "meets (tree derived under C2, K-A, K-B, T-1)" |
| Footer (`category.PROVEN_FOOTER`) | lists every condition with its status: C2 (not dischargeable), K-A / K-B (owed), T-1 (H-DS and the fit to Protocol 6.5, owed from the builders), MA-1 / MA-2', [SG26] Theorems 6.6 (2) and I.16 (preprint), Theorem TE' (revision 1 refereed, restatement unrefereed), Lemma QC (unrefereed), Theorem D (refereed), DKT26 for candidate rows (preprint); the classical 121.89 / 114.74 and the QROM 69.58 / 70.45 claimed with 76.72 / 77.60 beside | "(6) the tree reduction by extraction ... (a DRAFT, unrefereed)"; "its proven level is 114.7 bits" | as stated; points to `docs/what-is-proven.md` |

## Revision 10.1 (2026-11-19): the referee's findings on revision 10

**A draft until refereed.** After `docs/rev10-referee.md` (R10-1 to R10-11). Decision record:
`docs/decision-qrom-counting.md` 7 (edited in place) and 7.10; the tree reduction `docs/lemma-tree-extraction.md`
(Theorem TE). Outputs regenerated: `output/revision10-tables.txt` (no flag), `revision10-category-tables.txt` (`--rev7`),
`revision10-proven-basis-tables.txt` (`--hash-basis proven`), `revision7-tables.txt` (`--rev7 --convention t-ge-kq`),
`revision8-tables.txt` (`--rev8 --convention t-ge-kq`). Tests: `tests/test_revision10_1.py` (64); 451 in all. **No query
count changes.**

| Finding | Change | Before | After |
|---|---|---|---|
| R10-1 | `category.certification_checks`, one function for `category.Row` and `dkt26.Row8`; `Row8.hash_basis`, `Row8.checks`; the positive label names the basis (`category.certified_label`, `dkt26.certified_label`); `dkt26.rows/row/tables(..., hash_basis)`; `--rev8 --hash-basis` allowed | `--hash-basis proven`: B leaf + node UD 1/8 and B node UD 1/4 "certified (unique decoding; ...)" | "not certified: fails classical hash part (proven)" |
| R10-2 | `category.PROVEN_FOOTER` printed under the default output, `--rev7`, `--rev8`, `--category` | - | MA-1, MA-2', C2, K-A, K-B, Theorem D, [SG26] a preprint, Lemma TE a draft, `c'` / `k_q` (E); DKT26 for candidates; one tree |
| R10-6 | `hashterm.CInput`; `Row.c_input`, `Row8.c_input`; `c'` printed with `(E)` or `(reported)`; a reported `c'` from `KqReport.n_msg`, `m`, `n_j` | `2,401` | `2,401 (E)` |
| R10-7 | `kq_guard_bits(k_q, fraction, named_extra)` = max(10 %, named errors together); `KqInput.named_extra` = 4 OTHER_ROUNDS + `q_IOP` (A), `q_IOP` (B) | A guards 0.1375 | A guards 0.1375 to 0.2550; A row 7 at 1/4 (margin +0.1920, guard 0.2220) loses "certified"; every other status unchanged |
| R10-8 | `hashterm.KqReport` (k_q, queries, source, n_msg, m, n_j), `REPORTED_KQ` keyed by shape (`a_report_key`, `b_report_key`); `kq_floor`, `check_report`, `ImplausibleReport`; `resolve_kq` (reported at its counts; else estimate + reported excess, guard on); `category.a_kq`, `b_kq`, `a_c_input`, `b_c_input`; `_fixed_point`, `b_fixed_point`, `dkt26.row` re-solve on it | a report keyed by counts; above the estimate `certify` raised; `Row8` ignored reports | refused below the floor; re-solved above the estimate with a note; `Row8` reads reports |
| R10-9 | `TranscriptCounts.shortest_stream_bytes`; `SpbcsTree.stream_bytes_used`; category counts at `b + e = b` | stream term -4,765 (A), -2,953 (B) | -105 (A, B) |
| R10-11 | `_rows_word(convention, hash_basis)` in the summaries | "every certified shape" under `proven` | "every solved (status per row; proven hash basis) shape" |
| R10-2 (lemma) | `hashterm.tree_extraction_level` (comparison only) | - | 121.89 (A and B) under Theorem TE, a draft; the tables keep 114.74 |

## Revision 10 (2026-11-19): the hash term of SG26 Theorem 6.6 (2), "certified" computed, `k_q` with provenance

**A draft until refereed.** After `docs/rev9-and-lean-referee.md` (R9-1 to R9-5, L-2, L-6) and `docs/lemma-d-referee.md`
(m-1). Decision record: `docs/decision-qrom-counting.md` amendment 1 (section 7). Sources read from the rendered page
images (PDFKit, scale 2.2): [SG26] Theorem 6.6 (2) and Section 6.3 (page 58), Definition I.1 (page 130), Section I.1
(page 131); [CFP] Section 4.A.5 (pages 16 to 18, text layer, prose); ArkLib `6aa8b6fe` `FiniteBounds.lean`. Outputs:
`output/revision10-tables.txt` (no flag), `output/revision10-category-tables.txt` (`--rev7`),
`output/revision10-proven-basis-tables.txt` (`--hash-basis proven`); `revision7-tables.txt`, `revision8-tables.txt`
regenerated (non-default convention); `revision9-*.txt` kept as records. Tests: `tests/test_revision10.py` (19); 387 in
all. **No query count changes.**

### 1. The hash term (R9-1; `hashterm.py`)

Per row: `c'`, `k_q` (with provenance), the hash term in bits per proof and over the tree, classical (ROM part, every-t
convention: the tree term at most `t / 2^(kappa_C + 1)` for every `1 <= t <= 2^kappa_C`, binding at the top) and
quantum (QROM part as stated: the tree term reaches 1/2), and the digest a proven classical tree part needs. `b` = 32
bytes, the length of every digest the transcripts write (A: Keccak-256 keys, leaves, nodes, SHAKE256 write-back; B:
SHA-256 keys, BLAKE3 leaves and nodes, SHAKE256 write-back). Category 1:

| Rows | `c'` | Classical, proof / tree | QROM, proof / tree | Digest for proven classical 128 |
|---|---|---|---|---|
| A masked leaves | 2,377 to 2,397 | 121.89 / **114.74** | 80.40 / 75.63 | 288 |
| A nodes `2^24` to `2^30` | 2,157 to 2,189 | 121.95 to 121.96 / 114.81 to 114.82 | 80.45 / 75.68 | 288 |
| B, every row | 2,401 | 121.89 / **114.74** | 80.40 / 75.63 | 288 |

The documented "proven classical 126.6 bits" (book term `3.5 t^2 / 2^lambda`, counted once) is withdrawn; the
derivation table prints the SG26 proven-rule digest (288 / 416 / 544 at categories 1 / 3 / 5) beside the book's
(264 / 392 / 520, superseded). New per-profile section "The hash term of SG26 Theorem 6.6 (2)" with the verdicts:
classical met on condition H's attack rule, not as a proven bound (shortfall 13.26 bits); quantum met, proven
(+11.63 for the hash part; full QROM 69.58 / 70.45 unchanged). `Profile.hash_basis` / `--hash-basis
attack-rule|proven` (default attack-rule, the recorded basis); under `proven` no 256-bit row is certified.

### 2. "Certified" is computed (R9-2)

`Row.status` and `Row.certified` are properties computed from `Row.checks`: every-t convention, the need taken at the
row's own `k_q` (not the book's, not passed in), unique decoding, margin >= 0, the `k_q` guard, the QROM hash part
>= kappa_Q, the classical hash part on the profile's basis. `b_row` has no `status` argument; `b_row("leaf", 3, P,
queries=184)` now reads "DOES NOT MEET the need" (margin -5.80). `dkt26.row(..., need_bits=...)` reads "fixed need
(passed in), not certified". Bare and book rows (`_a_node_at`, `_a_leaf_at`) are never certified.

### 3. `k_q` with provenance and the guard (R9-4)

`hashterm.KqInput` (estimated / transcript-reported), `REPORTED_KQ` (empty until task T-1), guard
`log2(1 + 1.1 k_q) - log2(1 + k_q)` = 0.1375 bits on an estimated `k_q`. Rows that lose "certified" (category 1, margins):
A row 6 mode 1 `2^20` 1/4 (+0.0289); row 8 mode 0 `2^22` 1/4 (+0.1058), 1/2 (+0.0186); row 8 mode 1 `2^22` 1/2
(+0.0186); row 9 at 1/2: `2^24` +0.0011, `2^26` +0.0989, `2^27` +0.0979, `2^28` +0.0456, `2^29` +0.0575, `2^30`
+0.0043; row 9 at 1/4: `2^24` +0.0571, `2^25` +0.0016, `2^28` +0.1109, `2^30` +0.0033; row 7 at 1/2 (+0.0081). Every B
row keeps it (+0.28 to +0.78). Task T-1's text: decision record 7.6.

### 4. Padded group slots in B's `k_q` (Lemma D referee m-1)

`b_counts(q, rate, p, route)`: `q_IOP = ceil(q / unit) x unit x 6` (`B_QUERY_UNITS`, from `yugen-proof-b2` `0f84f74`
`parameters.md` 15.5; 6 assumed where unrecorded). `k_q`: 111 24,378 -> 25,170; 82 19,128 -> 19,536; 171 35,232 ->
35,808; 385 74,010 -> 74,940; 226 (built) 45,792 -> 46,560; 192, 174, 235 unchanged. Needs 157.861 -> 157.907 (111),
157.511 -> 157.542 (82), 158.392 -> 158.416 (171). No count moves.

### 5. Minor findings

R9-3: under `--convention t-ge-kq` the summaries say "non-default (t >= k_q), not certified," in place of "certified",
and the banner precedes every summary (sizes, field, QROM by digest, M-1, salt floors) and the hash-term section; the
cross-check's source reads "the count found there under the book need". R9-5: a field refusal names the need it
compares with (the book need solved first, "the refusal holds a fortiori"). L-2: `dkt26` prints the weakest Johnson
term twice, exact (33) 212.14 / 210.19 / 213.99 and Lean-backed (ArkLib `johnsonExceptionCount`) 212.11 / 210.18 /
213.96 bits. L-6: `lean/Compose.lean` committed (header: ArkLib commit and toolchain), identical to
`docs/arklib-lean-check.md` 3.2; recompiled, same axioms.

## Revision 9 (2026-11-19): the counting convention is EVERY t

The lead architect's ruling on condition C-2 (2026-11-19), following `docs/soundness-rev8-referee.md` section 7.
Decision record: `docs/decision-qrom-counting.md`. Sources: Sharp, Grubbs, *Faster and Smaller Anonymous Credentials
from Standardized Signatures*, ePrint 2026/2615 [SG26], Theorem 6.6 (2) (page 58), Definitions H.3 (page 128) and H.4
(page 129), Definition I.1 (k_q). **Read for this revision from the rendered page images** (pdfium at scale 2), not the
text layer: H.3 asks the bounds "for every t and every (t, 0)-adversary", H.4 "for every t ∈ ℕ and every
(t, 0)-adversary", and the paragraph after H.3 says the definition "bounds the errors at every query bound". The
referee's reading stands; nothing in Theorem 6.6 restricts t to t >= k_q. Flags: `--rev9` (also the output with no
flag), `--convention every-t|t-ge-kq`, `--legacy` (the former no-flag tables, a record). Outputs:
`output/revision9-tables.txt` (no flag), `output/revision9-category-tables.txt` (`--rev7`); `revision7-tables.txt` and
`revision8-tables.txt` regenerated under `--convention t-ge-kq` (labels; R8-7 / R8-4 terms; m = 10 candidates in
place of the searched rows); the other record outputs gain one banner line. Tests: `tests/test_revision9.py` (76);
368 in all.

### 1. The convention

Default (`EVERY_T`, the only certified one): a round of a proof whose verifier makes `k_q` hash queries needs, in a tree
of N = 20,000 proofs, `e >= kappa_C + 1 + log2 N + log2(1 + k_q)` (SG26 Theorem 6.6 (2), ROM part, at `t = 1`; `t = 0`
is bounded by `t = 1`), with `k_q` the row's **own** (system A: `category.a_row_kq`, N_msg from its rounds plus
OTHER_ROUNDS, q_IOP its opened positions, l_max its largest level; system B: `category.b_counts` at its count, six
trees, a 2^30-row node's l_max). `k_q` grows with the queries, so every row is solved to its least fixed point
(`category._fixed_point`, `b_fixed_point`, `dkt26.row`). Non-default (`T_GE_KQ`): the book need
`kappa_C + 1 + log2 N + log2(1 + k)` of revisions 1 to 8 (152.52 at category 1), available only as
`Profile.convention`, `convention=` or `--convention t-ge-kq`; every row it prints carries "non-default convention
(t >= k_q), not certified".

### 2. Every row the project uses, category 1 (old = revision 7 / 8, `t >= k_q`; new = every t)

| Row | Old | New | k_q | Need | Weakest term (bits) | Proof bytes (E) |
|---|---|---|---|---|---|---|
| B leaf + node, unique decoding, 1/8 | 184 | **192** | 40,416 | 158.59 | query 159.37 (algebraic: node X fold 1, 226.00) | leaf 635,909 -> 658,134; node 713,602 -> 737,947 |
| B leaf + node, Johnson m = 10, 1/8 (candidate, DKT26 preprint) | 107 | **111** | 24,378 | 157.86 | query 158.69 (node X fold 1, 212.14) | leaf 403,734 -> 415,692; node 460,314 -> 473,188 |
| B leaf + node, Johnson m = 10, 1/16 (candidate) | 80 | **82** | 19,128 | 157.51 | query 158.23 (node X fold 1, 210.19) | leaf 343,407 -> 350,080; node 394,704 -> 402,024 |
| B leaf + node, unique decoding, 1/16 | 168 | **174** | 37,896 | 158.50 | query 158.78 | leaf 637,473 -> 655,914; node 712,990 -> 733,139 |
| B node, unique decoding, 1/4 | 225 | **235** | 47,520 | 158.82 | query 159.36 (X fold 1, 227.00) | 779,746 -> 806,995 (2^27 words) |
| B node, unique decoding, 1/4, **as built (226)** | meets | **does not meet** (226 < 235) | 45,792 | 158.77 | | |
| B node, Johnson m = 10, 1/4 (candidate; arithmetic only, R8-3) | 165 | **171** | 35,232 | 158.39 | (X fold 1, 213.99) | 611,964 -> 629,042 (2^27 words) |
| A row 6 mode 0, 2^22, 1/4 | 226, 157, 154, 154 | **233, 162, 159, 159** | 18,082 | 157.43 | query0 157.74 | 688,180 -> 702,640 |
| A row 6 mode 1, 2^20, 1/4 | 227, 157, 155 | **234, 161, 159** | 13,456 | 157.00 | query1 157.03 | 497,951 -> 506,975 |
| A row 8 mode 0, 2^22, 1/4 | 226, 160, 163, 179 | **233, 166, 168, 185** | 17,436 | 157.38 | query0 157.48 | 682,787 -> 697,939 |
| A row 8 mode 0 / 1, 2^22, 1/2 | 374, 168, 174, 219 | **386, 174, 180, 228** | 20,788 | 157.63 | query0 157.65 | 807,335 -> 827,271 |
| A row 8 mode 1, 2^21, 1/4 | 227, 161, 166, 219 | **234, 166, 172, 228** | 17,596 | 157.39 | query0 157.65 | 611,122 -> 626,665 |
| A row 9, 2^27, 1/2 | 368, 167 x3, 168, 168, 173 | **382, 174 x4, 175, 180** | 36,564 | 158.45 | query0 158.54 | 873,948 -> 904,856 |
| A row 9, 2^27, 1/4 | 225, 160 x5, 163 | **234, 166 x4, 167, 169** | 33,022 | 158.30 | query4 158.59 | 760,099 -> 785,922 |
| A row 9, 2^30, 1/2 | 368, 167 x3, 168 x3, 173 | **383, 174 x4, 175, 175, 181** | 45,658 | 158.77 | query4 158.77 | 1,047,063 -> 1,085,873 |
| A row 9, 2^30, 1/4 | 225, 160 x6, 163 | **234, 166 x3, 167 x3, 169** | 41,444 | 158.63 | query3 158.63 | 918,699 -> 951,166 |

Also: B unique decoding at rate 1/2, 368 -> **385** (need 159.46, k_q 74,010); A row 7 (the plain tree leaf, 2^22;
new function `category.a_plain_leaf`, printed in the revision 9 tables, not part of `a_rows`): the calculator's
225, 160, 160, 160 at the book need (the build's 153.0-bit rule holds 226, 161, 161, 161) -> **233, 165, 165, 165**
(need 157.31; 448,522 opening bytes, was 435,372), and 368, 167, 167, 168 -> **380, 173, 173, 173** at rate 1/2.
Margins at the new B counts: 192 +0.78, 111 +0.83, 82 +0.72, 235 +0.52 (236: +1.20), 171 +0.57.

Every A node stack 2^24 to 2^30 at both rates is in `output/revision9-category-tables.txt` (+6 to +15 a level; proof
bytes +3.2 % to +3.7 %). Proof bytes are the size model's (E), anchored as in revision 7. A's measured row-8 build
(227, 161, 164, 180; `A_LEAF_CHECK`) is a measurement and does not change; the calculator's own row 8 mode 0 is the
row above. The weakest algebraic rounds do not move (they do not depend on the count); their slack above the need
falls by the rise of the need (B's unique-decoding row at rate 1/8: 73.5 -> 67.4 bits, 226.00 - 158.59).

### 3. Condition Q (QROM, SG26 Theorem 6.6 (2), N = 20,000)

The QROM part already adds `k_q` to `t` exactly; only `e` (the weakest round of any proof of the tree) changes.
Category 1: A 67.25 (revision 7; 67.54 in revision 6's rows) -> **69.58** (e = 157.03, k_q 47,476); B 67.43 ->
**70.45** (e = 158.78, k_q 40,416). Requirement 64: met with +5.58 / +6.45. Categories 3 and 5: A 101.84 / 133.97, B
102.71 / 134.79 (requirements 96 / 128).

### 4. Other categories (reported, not used by the project's rows)

Category 3: A row 6 mode 0 329, 228, 224, 223 (was 321, 222, 219, 218), A node 2^30 at rate 1/2 1,842 KiB, **over
PROOF_BYTES_MAX** (1,835,008 B; it fitted under revision 7); the minimum field for A's 2^30 node at rate 1/4 is exactly
256 bits. B 269 (1/8), 245 (1/16); the m = 10 Johnson node rows miss category 3 at GF(2^256), as before. Category 5:
B 347 / 315, every B proof over PROOF_BYTES_MAX (as in revision 7, which had the B leaf already over).

### 5. Software findings of `docs/soundness-rev8-referee.md`

| Finding | Fix |
|---|---|
| R8-3 | the rate-1/4 Johnson node row carries "arithmetic only: no lemma stated or refereed at this rate, no build" in its status, in the condition C-2 and cross-check tables (`dkt26.ARITH_ONLY`, `Row8.arithmetic_only`) |
| R8-4 | an unrecorded shape takes terminal 0 with DKT26 Lemma 3.3 at message dimension 1 and the D-term bound `log_msg (2^r - 1)` (84 at the node 1/4); printed; 165 / 171 and the weakest 213.99 unchanged |
| R8-5 | `CERTIFIED` now names the convention: "every t, Sharp-Grubbs ePrint 2026/2615 Theorem 6.6 (2)" |
| R8-6 | `LOG_MSG` documented as caps with the monotonicity argument; the parameter table's heading says so |
| R8-7 | `TERMINAL_AS_BUILT` keyed by (kind, rate, route): the 184 row's D-term is 7 x 7 = 49 (250.39 bits), the 107 row's 6 x 7 = 42; rate-1/16 node 5 (the larger of 4 / 5) |
| R8-8 | `--rev5`, `--rev6`, `--design`, `--basis`, `--current`, `--ship`, `--wi`, `--target`, `--legacy` print a RECORD banner first (superseded; book convention, not certified; DKT26 a PREPRINT; Haboeck's route and the 102 / 77 rows withdrawn); the no-flag output is revision 9 |
| R8-8b | `category.b_candidates` returns the refereed m = 10 rows from `dkt26` (list 19 / 31 by DKT26 (38)), never a search over m; a candidate below its need says "DOES NOT MEET" |
| R8-9 | recorded here: DKT26 (36)-(38) were checked on the rendered page by the referee (report section 1), not from the text layer; the same for SG26 H.3 / H.4 in this revision |
| R8-10 | `dkt26.check_m`: a missing, float or bool `m` is refused (`OutsideRegime`) in `row`, `line`, `terms` |
| R8-11 | `dkt26.shape` refuses `log_terminal_dim` outside `0 .. log_msg`; the no-fold shape (equal to `log_msg`) computes |
| R8-12 | `dkt26.row` refuses a Johnson row whose threshold `(1 + 1/(2m)) sqrt(rho)` is not below `(1 + rho)/2` |
| R8-13 | `test_exact_recomputation_at_boundaries`: A, theorem m, B_jet, B_Z with own arithmetic (80-digit decimals, integer ceilings) at (49, 36, 3), (1652, 344, 10) and three row lines |
| R8-14 | `johnson.list_bound` documented as conservative (B_jet >= 29 / 42 >= 19 / 31); the builder's `params.rs` is listed for its maintainers |
| R8-15 | in `johnson-row-referee-2.md`, not this module: listed for the lead |

### Findings

1. The built rate-1/4 node (226 queries, `yugen-proof-b2` `CAT1_QUERIES`) does not meet the default need (235).
2. Every build at the old counts (A's leaves and nodes; B's 184 / 107 / 80) is below its row under every t.
3. Category 3's A node 2^30 at rate 1/2 exceeds PROOF_BYTES_MAX under every t.


## Revision 8 (2026-11-19)

Condition C-3 of `docs/johnson-row-referee-2.md` (section 7). Sources: Dao, Kominers, Thaler, *Reed-Solomon Codes
Beyond Johnson*, ePrint 2026/2056, copy of 2026-11-02, **a preprint** [DKT26]: Theorem 4.4 (36), (37), (38), (39),
Section 4.2 (33), (34) and Psi_D, Section B.2 (the pairwise list bound), B.3 (the closed form), Lemma 3.3 (6), Lemma 6.5,
Corollary 6.6 (all re-read for this revision from the PDF's text layer, 2026-11-19); Haboeck, ePrint 2024/1571, Lemma 3;
Arnon, Chiesa, Fenzi, Yogev, ePrint 2024/1586, Lemma 4.10 with BCIKS20 Theorem 4.1; Sharp, Grubbs, ePrint 2026/2615,
Theorem 6.6 (2), Definition I.1; `docs/binius-johnson-row.md` revision 2 (Lemmas U, J1, J2, F, UD); `yugen-proof-b2`
`docs/parameters.md` 11 (the D-term) and 14.7 (`log_terminal_dim` as built). New module `dkt26.py`; flag `--rev8`
(with `--category N`); output `output/revision8-tables.txt`; tests `tests/test_revision8.py`.

### 1. Every term of the Johnson-regime rows, in the calculator proper

`dkt26.line(n, k, m)` computes, exactly (rationals, exact square-root ceilings), the parameters of DKT26 Theorem 4.4 at
our threshold `A = ceil((1 + 1/(2m)) sqrt(rho) n)`: the theorem's own `m` by (36) (with `eta_0 = A/n - sqrt(rho_-)`), `t`,
`B_jet`, `B_Z`, `lambda_agr` (37), `Psi_D(B_jet)`, the exceptional count `B_cf = E^(1)_ord(D, A, n; B_jet, B_Z)` by
(33)-(34), the closed form (39), and the list bound (38). `dkt26.terms` lists every round of a leaf or node proof:
PIOP (127 `B_list`), ring switch (8 `B_list`), claim batching (3 `B_list`), mask (`B_cf + B_list`), index
(`B_cf + 2 B_list`), **every** `X` fold down to the terminal dimension (`B_cf(n/2^i) + 2 B_list`), the terminal sumcheck
rounds (2), the builder's D-term (`n_f (2^r - 1)`, charged although the referee shows it is 0), and the query round.

| Term (bits) | 107 at 1/8 (exact; closed) | 80 at 1/16 (exact; closed) | Referee-2 5.1 |
|---|---|---|---|
| list size | 19 | 31 | 19 / 31 |
| PIOP / ring switch / batching | 244.76 / 248.75 / 250.17 | 244.06 / 248.05 / 249.46 | same |
| leaf mask, index | 220.14; 219.41 | 218.19; 217.41 | same |
| leaf first `X` fold | 221.14; 220.41 | 219.19; 218.41 | same |
| **node first `X` fold (weakest)** | **212.14**; 211.41 | **210.19**; 209.41 | same |
| terminal sumcheck rounds | 255.00 | 255.00 | same |
| D-term (builder's bound, as built) | 250.61 (6 x 7) | 250.09 leaf (4 x 15), 249.77 node (5 x 15) | 250.39 both (49): see finding 3 |
| query round | 152.968 (106: 151.539) | 154.369 (79: 152.439) | same |
| slack of the weakest algebraic round | 59.6 | 57.7 | same |
| `log2 B_cf` at the node line; closed | 43.86; 44.59 | 45.81; 46.59 | 2^43.9; 2^44.6 |

### 2. Refusals (hard failures, `dkt26.OutsideRegime`), not warnings

A line of message dimension 1 (Theorem 4.4 excludes `D = 0`) unless DKT26 Lemma 3.3's term is added
(`dimension_one="lemma33"`: 14 + 38 = 52, 250.30 bits at `n = 8`, as the document's 8.2); `m < 3`; `D > n - 2`; `A > n`
(`a > 1`); `A^2 <= n D` or `A <= D`; Haboeck's route (not available, document 0.1: G-1, G-3, G-6); a Johnson row
without `m`. The build's terminal dimensions (6 / 4 leaf, 6 / 5 node at 1/8 / 1/16; `parameters.md` 14.7) have no
dimension-1 level; the node at rate 1/4 has none recorded (1 is taken and marked in the output).

### 3. Labels

Every Johnson-regime row's status contains `DKT26_LABEL` ("rests on DKT26 (Dao, Kominers, Thaler, ePrint 2026/2056), a
PREPRINT"), also if `DKT26_ACCEPTED` is set by the lead architect; a row that misses its need is never called
certified. Revision 7's `--category` candidate rows now read "**candidate** (rests on DKT26, a preprint)" and
`category.CANDIDATE` says "a preprint" (label text only; the regenerated `output/revision7-tables.txt` differs from
the previous one in those 8 lines and nowhere else). Revision 5's output is a record and is unchanged.

### 4. Rows and the cross-check against the documents (category 1, need 152.519)

| Row | Status | Count | Margin | Weakest algebraic | Documents |
|---|---|---|---|---|---|
| B leaf + node, unique decoding, 1/8 | certified | 184 | +0.215 | 226.00 | 184: agree |
| B leaf + node, Johnson `m = 10`, 1/8 | candidate, DKT26 preprint | 107 | +0.449 | 212.14 | 107: agree |
| B leaf + node, Johnson `m = 10`, 1/16 | candidate, DKT26 preprint | 80 | +1.850 | 210.19 | 80: agree |
| **B node, unique decoding, 1/4 (new)** | certified | **225** | +0.0472 | 227.00 | 225 (referee-2 5.2): agree |
| B node, unique decoding, 1/4, as built | certified | 226 | +0.7253 | 227.00 | 226 (build): agree, meets |
| **B node, Johnson `m = 10`, 1/4 (new)** | candidate, DKT26 preprint | **165** | +0.867 | 213.99 (list 10) | not in the documents |

Category 3 (`--rev8 --category 3`): unique decoding 261 (1/8), 320 (node 1/4), as the document's 8.3; the `m = 10`
Johnson rows do not meet 216.52 (weakest 212.14 / 210.19 / 213.99) and say so.

Condition C-2 (Q-5, open; `dkt26.every_t_count`): under SG26's classical bound read for every `t`, 107 -> 111,
80 -> 82, 184 -> 192, 225 -> 235 (referee-2 5.4 reproduced), and the new Johnson node at 1/4: 165 -> 171.

### 5. Agreement with `johnson-row/rowcalc.py` (task 4)

`test_agrees_with_rowcalc_to_the_bit`: on the 107 and 80 rows the closed-form terms of `dkt26` equal `rowcalc.row`'s
to within `1e-9` bits for every term of leaf and node, the same query count, per-query bits, need and list size; the
exact count (33) is never weaker than the closed form.

### Findings

1. None of 184, 107, 80, 225, 226 disagrees with the documents.
2. Revision 7's `--category` search for B candidates (`johnson.best_m`, revision-5 list `(m + 1/2)/sqrt(rho)`) still
   offers `m = 153` (102 queries, +0.00) and `m = 38` (77 queries, +0.03) at category 1, rows `binius-johnson-row.md`
   revision 2 withdrew (0.3; 8.2) for their margins. They are labelled candidates; `--rev8` gives the refereed rows.
3. The second referee's 5.1 gives the D-term as 250.39 bits (49) in both columns; with the build's own formula
   `n_f (2^r - 1)` (`parameters.md` 11) and its recorded terminal dimensions it is 250.61 at 1/8 and 250.09 / 249.77
   (leaf / node) at 1/16 (with `n_f = 7`, 1/16 would give 105, 249.29). Not binding anywhere (the referee shows the
   term is 0 against the analysed protocol).
4. The node row at rate 1/4 has no `log_terminal_dim` recorded by the build (BR-4 printed it at 1/8 and 1/16 only).

### Tests

264 -> 292 (`tests/test_revision8.py`: 28). `johnson-row/`: every file passes (T-J3 now 4 tests).

## Revision 7 (2026-11-19)

Sources: NIST, *Submission Requirements and Evaluation Criteria for the Post-Quantum Cryptography Standardization
Process* (call for proposals, December 2016), Section 4.A.5, pages 16 to 18 [CFP]; FIPS 204 Section 4 Table 1 and
Appendix D.1; FIPS 205 Section 11, Table 2, 11.2.2 (all read 2026-11-19, `REFERENCES.md` 1.1f); Sharp, Grubbs, ePrint
2026/2615, Theorem 6.6 (2) to (4) (as revision 6); `docs/decision-security-category.md` and `category-study/` (the
study reproduced, not used); `docs/security-category-referee.md` (its corrections applied, listed in 5). New module
`category.py`; flags `--rev7` and `--category N` (with `--digest-bits`, `--proof-salt`, `--leaf-salt`, `--field-bits`,
`--tree-hash-a`, `--tree-hash-b`, `--privacy-category`); output `output/revision7-tables.txt`; tests
`tests/test_revision7.py`.

### 1. The category as an input, derived from the NIST text

`category.NIST` holds [CFP]'s five requirements and the page-18 gate counts; `derive_target(c)` turns a category into
the conditions C, Q, G, H (conventions stated in `soundness-method.md` 8.7): `kappa_C` = the reference attack's
evaluations (128 / 128 / 192 / 192 / 256 for categories 1 to 5: key bits, or half the hash length), `kappa_Q =
kappa_C / 2`, attack bits `kappa_C`, digests `2 kappa_C`. Derived targets equal revision 6's `cat1` and `cat3` in every
field (test). New: categories 2, 4 (same rows as 1, 3) and 5 (`kappa_C` 256, `kappa_Q` 128, digests 512 / 520).

| Figure | Before (revision 6) | After |
|---|---|---|
| Targets | `cat1`, `cat3` typed in (`targets.py`) | categories 1 to 5 derived from [CFP] 4.A.5 |
| Per-round need, tree of 20,000 proofs, A (k = 599) / B (k = 600) | 152.52 (cat1) | 152.52 / 216.52 / 280.52 for categories 1 / 3 / 5 (2 = 1, 4 = 3) |
| Condition Q's per-round need | 145.87 | 145.87 / 209.87 / 273.87 |
| Gates per reference evaluation implied by [CFP] | not stated | 2^15, 2^18, 2^15, 2^18, 2^16 (categories 1 to 5) |
| (depth x size) per Grover iteration implied by [CFP] | not stated | 2^42, 2^41, 2^42 (categories 1, 3, 5) |

### 2. Inputs and refusals (hard failures)

Field, digest, proof and leaf salts, the tree hash of each system and the privacy category are inputs (`Profile`).
Refused: a field below the category's algebraic rounds (`FieldTooSmall`; example: category 5 at `GF(2^256)`), a digest
below condition H's attack rule (`DigestTooShort`; 256 bits at category 3, 384 at 5) or below the QROM hash term of
Theorem 6.6 (2) (`spbcs.ConditionQFailure`; floor 224 / 320 / 416 bits), a tree hash whose collision claim is below
`kappa_C` or whose output is below the digest (`HashNotAdmissible`; BLAKE3 and SHA-256 at categories 3 and 5,
SHA-384 at 5), leaf salts not longer than the digest (`SaltNotCovered`, Theorem 6.6 (3)'s `b_l > b`). Masked-leaf
shapes with no admitted stack are listed as refused shapes, not rows.

Backward-compatible signature changes (every revision 1 to 6 output regenerated and diffed: unchanged):
`current.a_config(..., field_bits=256, digest_bits=256)`; `johnson.Term.field_bits`, `johnson.terms(...,
field_bits=256)`, `johnson.row(..., field_bits=256)`, `johnson.best_m(..., field_bits=256)`.

### 3. Certified rows at categories 1, 3, 5 (unique decoding, no grinding, true rates, spBCS, 20,000 proofs)

Category 1 reproduces revisions 5 and 6 (tests): the standalone masked leaf 226/157/154/154; row 8's minimal counts
226/160/163/179 (1/4) and 374/168/174/219 (1/2); row 9's minimal counts at every stack and rate; B 184 (1/8), 168
(1/16); B's QROM 67.43 and `k_q` 38,832; B's pool zero-knowledge `2^-85.7`.

| Row | Category 3 (`GF(2^256)`, 48-byte digests, salts 64 / 96 B) | Category 5 (`GF(2^384)`, 64-byte digests, salts 80 / 112 B) |
|---|---|---|
| A row 6, standalone masked, mode 0, `2^22`, 1/4 | 321, 222, 219, 218 (+0.37) | 415, 288, 283, 282 (+0.03) |
| A row 6, mode 1, `2^20`, 1/4 | 323, 223, 219 (+0.12) | 419, 289, 285 (+0.16) |
| A row 8, masked in a tree, mode 0, `2^22`, 1/4 | 322, 228, 232, 293 (+0.35) | 417, 295, 305, 395 (+0.11) |
| A row 8, mode 1 (trace `2^20`), 1/4 | admitted at `2^22` (`2^21` at category 1): as mode 0 | admitted at `2^22`: as mode 0 |
| A row 8, rate 1/2, modes 0 and 1 | **no admitted stack** (`2^20` to `2^30`) | **no admitted stack** |
| A row 9, node `2^27`, 1/2 | 522, 238, 238, 238, 238, 239, 246 | 676, 308, 308, 308, 308, 309, 319 |
| A row 9, node `2^27`, 1/4 | 320, 227, 227, 227, 227, 227, 231 | 414, 294, 294, 294, 294, 295, 299 |
| A row 9, every stack `2^24` to `2^30` | `output/revision7-tables.txt` | the same |
| B leaf and node, 1/8 / 1/16 | 261 / 238 | 338 / 308 |
| B candidates (DKT26 route; **never certified**) | none at `GF(2^256)`; at `GF(2^384)` 145 (m = 107, 1/8), 109 (m = 53, 1/16) | 188 (m = 92, 1/8), 141 (m = 69, 1/16) |

Each count less by one fails, for every row of categories 1, 3 and 5 (`test_each_count_less_by_one_fails`, 68 cases).

### 4. Field, QROM, zero knowledge, sizes

| Figure | Category 1 | Category 3 | Category 5 |
|---|---|---|---|
| Minimum field, A (leaf; worst node) | 177; 185 | 241; 249 | 305; **313** (`2^30`, 1/4; 312 at 1/2) |
| Minimum field, B (leaf; node) | 176; 185 | 240; 249 | 304; 313 (1/16; 312 at 1/8) |
| QROM bits A / B (margin) | 67.25 (+3.25) / 67.43 (+3.43) | 99.29 (+3.29) / 99.39 (+3.39) at 48 B | 131.28 (+3.28) / 131.35 (+3.35) at 64 B |
| QROM at the other digests | | 32 B refused (75.63); 64 B 99.29 / 99.39 | 32 B refused (75.63); 48 B refused (118.30) |
| Zero knowledge, pool `2^20`, A / B (plus `Q eps_hvzk`, open) | `2^-87.8` / `2^-85.7` | `2^-138.0` / `2^-138.0` (salt term) | `2^-151.8` / `2^-149.7` |
| Profile M-1 (48-byte digests, salts 80 / 112 B, `t = 2^128`) | | `2^-170.0` both; WI `2^-214.8` / `2^-212.7` | |
| Largest certified proof (E) | 1,047,063 B | 1,793,209 B (A node `2^30`, 1/2): within 1,835,008 by 41,799 B | 3,003,138 B: **over** |
| Largest with A's nodes at rate 1/4 only (E) | | 1,581,153 B (A node `2^30`, 1/4) | 2,683,634 B (A node `2^30`, 1/4): **over** |

A's QROM figure at category 1 is 67.25 where revision 6 printed 67.54: revision 7 takes `e` from the minimal counts of
every certified row (row 8 at 1/4 has margin +0.02), revision 6 from the 153.0-bit rule rows. No certified figure of
revision 6 changes.

Sizes (E): A's masked leaf is anchored on the measured 688,180 B (row 6, 64-byte salts, after `MUL2`; yugen-proof-a
`parameters.md` 2.3), with the stream scalars (6,977) scaled with the field's element size; row 8's measured
692,504 B is reproduced to -1.0 %. A's node on 875,309 B (recursion.md 9.10), B's leaf on 583,680 B (form T, 32-byte
salts; route S modelled: the four fold trees salted), B's node on 538,272 B (2^23 words); non-opening bytes added,
scaled by the field's element size. Bytes a query by digest (32 / 48 / 64 B) and leaf salt (64 / 96 / 112 B): table in
the output.

Salt floors from a zero-knowledge target (pool of `2^20`, excluding `Q eps_hvzk`; referee F-4): leaf salts 75 / 83 /
91 B at 48-byte digests and 91 / 99 / 107 B at 64-byte digests for `2^-64 / 2^-96 / 2^-128`; proof salts 54 / 62 / 70
B at `t = 2^128`.

### 5. Differences from the category study (`category-study/output/category-tables.txt`) and their causes

| Figure | Study | Revision 7 | Cause |
|---|---|---|---|
| Every query schedule (A leaf, A node, B, B candidates) | as section 3 | identical | (reproduced independently) |
| A's minimum field at category 5 | 305 bits | 312 (rate 1/2), 313 (rate 1/4) | the study took the leaf's `2^24` term; nodes of `2^30` have `2^31` (1/2) and `2^32` (1/4) (referee V7 / F-8 agrees on 312) |
| B's minimum field at category 5 | 312 | 312 (1/8), 313 (1/16) | the study checked rate 1/8 only |
| A leaf, category 3 / 5 (KiB) | 939 / 1,496 | 1,055 / 1,750 | anchor 688,180 B (64-byte salts, after `MUL2`) against 600,340 B; leaf salts 96 / 112 B against 64; at category 5 the stream scalars scale with 48-byte elements |
| B leaf, category 3 / 5 (KiB) | 970 / 1,652 | 1,066 / 1,799 | route S (fold trees salted, required by Theorem 6.6 (3)) and 96 / 112-byte salts; at category 5 the leaf is **over** `PROOF_BYTES_MAX` |
| A node `2^27`, 1/2, category 3 / 5 (KiB) | 1,424 / 2,362 | 1,427 / 2,368 | non-opening bytes added (scaled by element size) instead of a ratio |
| B node `2^27`, 1/8, category 3 / 5 (KiB) | 1,183 / 2,057 | 1,148 / 1,996 | the same, and B's node anchor at 2^23 words added, not scaled by ratio |
| A QROM, category 3 / 5 | 99.32 / 131.32 at the need | 99.29 / 131.28 | `e` the weakest certified round, not the need; `k_q` from the category's own rows |
| Row 8 (masked in a tree) at rate 1/2 | not computed | no admitted stack at categories 3 and 5 | the hiding lane's aligned offset exceeds the domain at the larger counts |
| Mode-1 masked leaf under row 8 | not computed | admitted at `2^22` (categories 3, 5) | the admission rule at the larger counts |

### 6. Referee corrections applied (`docs/security-category-referee.md`)

V7 / F-8 (A's category 5 field: 312, here 312 / 313); 1 (5) / F-2 (condition G's premise is depth x size of the
quantum circuit, an assumption: `category.grover_overhead_log2`); 1 (2) / F-1 (condition H cited to [CFP] page 18 and
[FIPS204] Table 1, D.1; BHT not used); 3.3 / F-3 (condition Q proves security to `2^kappa_Q` queries only; the quantum
half of categories 3 and 5 rests on G); 3.4 / F-4 (salt floors from a zero-knowledge target, printed); 1 (7) (the tree
union goes beyond [CFP]'s per-instance definition; multi-key resistance is "desirable", 4.A.6).

Records unchanged: `output/design-tables.txt` differs from the code's `--design` output by a section that the current
code does not print (B recursion with WHIR); the difference predates revision 7 (HEAD's code prints the same as revision
7's), the file is left as the record.

### Tests

170 -> 264 (`tests/test_revision7.py`: 94 new, of which 68 are the minimality cases (one a row)). `uv run pytest`: 264 passed.

## Revision 6 (2026-11-19)

Sources: Sharp, Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, ePrint 2026/2615
(Protocol 6.5, Theorem 6.6 (2), (3), (4), Definition I.1, Section I.1, Theorems I.5, I.6 with proofs; read
2026-11-19); Chiesa, Weissenberg, Yogev, Zheng, ePrint 2026/2863 (Theorem 4.10, (4.1), (4.5), (4.13), the example
after Theorem 4.10, Remark 5.3); `docs/qrom-zk-referee.md`; lead decisions D-a, D-b, D-c (`docs/qrom-compilation.md`
section 0). Outputs: `output/revision6-tables.txt` (new, `--rev6`), `output/revision5-tables.txt` and
`output/current-tables.txt` regenerated. Every other output (`--ship`, `--wi`, `--basis`, `--design`) diffed: unchanged.

### 1. System A's zero-knowledge defaults: 11 bus layers, 52 claims

`wi.A_WALLET_ZK` was `AZk()` with 10 bus layers and 54 claims (`zero-knowledge.md` 17.5); the merge counted 11
bus layers (depth 21, the first a one-level step) and 52 linear claims (22 bus, 2 table, 24 Keccak, 4 openings):
`yugen-proof-a-zk/docs/zero-knowledge.md` 18.6, `docs/zk-merge-notes.md` 3, items 2 and 9. The revision-5 defaults
are kept as `wi.A_WALLET_ZK_R5`. Before / after:

| Figure | Before | After |
|---|---|---|
| Rounds in the zero-knowledge leaf's list (row 6 schedule, 226/157/154/154) | 85 | 87 |
| Need a round at 20,000 proofs | 152.512 | 152.517 |
| Zero-knowledge leaf, margin of its weakest round (152.96) | +0.45 | +0.44 |
| Row 8 minimal at 1/4 (226, 160, 163, 179), margin | +0.03 | +0.02 |
| Row 8 at the list at 1/2, margin | -30.41 | -30.42 |
| Row 8 at 153.0 bits at 1/2 (375, 169, 175, 220), margin | +0.68 | +0.67 |
| `current` tables: rounds of row 6 / smallest leaf; need at the tree bound | 85 / 82; 152.51 | 87 / 84; 152.52 |

No count changes: 226/157/154/154 still meets (each count less by one fails), and every rule and minimal schedule
of revision 5 is unchanged.

### 2. Condition Q under Sharp-Grubbs Theorem 6.6 (2), spBCS transcript form (new `spbcs.py`, `revision6.py`)

Transcript form as an input: `spbcs.FORMS` = spBCS with a SHAKE256 stream (default, both systems: the published
theorem as is) and spBCS with a counter-mode SHA-256 stream (system B's alternative; Lemma X, `t -> 2t`). The
constants: `C1 = 6`, hash constant `6 c'` with `c' = max(2, c) + n_J + 1`, `c = N_msg max(1, m)`; the verifier's
`k_q` added to `t` exactly. Message counts (estimates until the transcript modules report them): A 599 verifier
messages (87 listed + 512 `OTHER_ROUNDS`), 599 prover messages, `m = 2`: `c' = 2,397`; B 600 + 600, `m = 2`:
`c' = 2,401`. `k_q` = 45,852 (A), 38,832 (B).

| System, form | Before (revision 5, Theorem Q) | After (revision 6, Theorem 6.6 (2)) |
|---|---|---|
| A | form X, `C1 = 6`, `C2 = 24`: IOP 67.54, hash 78.71, **67.54 bits** (+3.54) | spBCS SHAKE256, `C1 = 6`, `6 c' = 14,382`: IOP 67.54, hash 75.63, **67.54 bits** (+3.54) |
| A, `a_V` folded | `C1 = 12`, `C2 = 96`: 67.04 (constants wrong: 24, 192; referee 1.8) | removed (`k_q` is now added to `t` exactly) |
| B | form C, `C1 = 24`, `C2 = 240` (unproved: no write-back): IOP 66.43, hash 77.60, **66.43 bits** (+2.43) | spBCS SHAKE256, `C1 = 6`, `6 c' = 14,406`: IOP 67.43, hash 75.63, **67.43 bits** (+3.43) |
| B, counter mode | | spBCS counter-mode SHA-256 (Lemma X): `C1 = 24`, `C2 = 115,248`: IOP 66.43, hash 74.63, **66.43 bits** (+2.43) |
| Stream term `2 sqrt(k_q / 2^(8(b+e)))` over the tree | not modelled | `2^-4593` (A), `2^-2829` (B) |
| B's QROM condition on a round (IOP term alone) | 147.87 | 145.87 (SHAKE) / 147.87 (counter); condition C binds at 152.52, unchanged |

Condition Q stays a hard failure (`spbcs.require` raises `ConditionQFailure`; example refused: 192-bit digests).
`qrom.py` (Theorem Q) is kept as the record; its form C row is labelled unproved in the tables.

### 2a. Finding Q-5: condition C under the ROM part of Theorem 6.6 (2) (reported, not applied)

New `spbcs.classical_need`, printed in the revision-6 tables. The certified need (152.52) rests on the book's
Theorems 25.2.1 and 31.2.1, `(t + k) eps` with `k` the rounds (599 for A, 600 for B), which are stated for the
hash-chain Construction 25.1.1, not for spBCS. The published classical bound for spBCS is SG26's
`(t + k_q)(eps_k + c' (t + k_q)/2^256)`; in the calculator's convention (every `t <= 2^kappa`, binding at `t = 1`)
it needs 158.77 (A, `k_q` = 45,852) and 158.53 (B) bits a round: the weakest rounds (152.96, 152.73) miss by 5.81
and 5.80. Read for `t >= k_q` (an adversary making at least one verification's queries) it needs 144.29: met with
8.67 and 8.45. No row is changed; the choice of convention (or a revision 7 that solves the rows at 158.8) is the
lead architect's (`docs/qrom-compilation.md` 6.2).

### 3. Zero knowledge under Theorem 6.6 (3), (4): per-proof salt and leaf-salt terms

Before (`salts.py`, Lemma H with Theorem ZQ, one proof, non-adaptive witness): `2^-104` a proof at 512-bit salts
(`N_u = 2^24`) plus `zeta_IOP < 2^-240`. After (`spbcs.eps_zk`, `spbcs.eps_wi_log2`; 64-byte leaf salts, 64-byte
proof salt; `eps_hvzk` open and never filled in; leaf proofs only):

| | A | B |
|---|---|---|
| `n_pos` of a leaf proof (every tree salted) | `2^21.17` | `2^23.25` |
| One proof, `t <= 2^128` | `2^-107.8` + `eps_hvzk` | `2^-105.7` + `eps_hvzk` |
| A wallet, `2^16` proofs | `2^-91.8` + `2^16 eps_hvzk` | `2^-89.7` + ... |
| The pool, `2^20` proofs, `t = 2^64` (also `2^128`) | `2^-87.8` + `2^20 eps_hvzk` | `2^-85.7` + ... |
| The pool with a 48-byte proof salt, `t = 2^64` / `2^128` | `2^-87.8` / `2^-42.0` | `2^-85.7` / `2^-42.0` |
| The pool with a 32-byte proof salt, `t = 2^64` | `2^-42.0` | `2^-42.0` |
| Theorem 6.6 (4), the pool, `L = 2^24` bits | `2^-86.8` + `2^21 eps_hvzk` | `2^-84.7` + ... |
| Leaf salt for `2^-128` at the pool | 76 bytes (`2^-135.8`) | 76 bytes (`2^-133.7`) |

`zeta_IOP < 2^-240` is withdrawn (the IOP-level HVZK items are open, `zk-quantum.md` 5). `salts.py` is kept as the
record (its byte and block counts stay valid).

### 4. leanVM's `eps_aff` (new `affine.py`; audit C-19, R-5)

CWYZ26 Theorem 4.10, (4.13), with (4.1), (4.5) checked in integers and leanVM's `find_witness` search. Reproduced:
Remark 5.3, 125.42 bits (`M = 6`, `l = 6`, `delta = 2^-182.17`); the example after Theorem 4.10, 123.25 bits.
At leanVM as shipped (stack `2^20`, rate 1/16, `q = 2^128`, the calculator's Johnson agreement): levels 0 to 2
`eps_aff` 123.05, 121.27, 119.67 bits (leanVM's round with the claim term 121.46, 119.69, 118.10) against DKT26's
line count 88.41, 88.41, 86.41; level 3: no witness from leanVM's search at that agreement. **No row changes**: no
certified Yugen row is in the Johnson regime (unique decoding, Theorem S0, everywhere).

### 5. Records and citations

`shipping.py`, `design.py`, `params.py`: docstrings now say they are records that use nominal rates and certify
nothing. `qrom.py`, `salts.py`: records superseded by `spbcs.py`. `whir.py`, `revision5.py`: the source of the
degree growth of W-1 is the pinned leanVM verifier; CWYZ26 Theorem 5.2 (a different combiner) is cited only as
consistent. `current.py`: the mask-count line cites 18.6 and the merge notes.

### Tests

153 -> 170 (`tests/test_revision6.py`: 17 new; `tests/test_revision4.py`: the default counts updated to 11/52 with
the revision-5 record asserted). `uv run pytest`: 170 passed.

## Revision 5 (2026-11-19)

Sources: `docs/whir-additive-soundness.md` (Theorem S0, finding W-1, section 6), `docs/qrom-compilation.md`
(Theorem Q, sections 4 to 6), `docs/zk-quantum.md` (Lemma H, Theorem ZQ, section 3), `docs/binius-johnson-row.md`
(section 7), `docs/CITATION-AUDIT.md` (1d: C-4, C-7, C-8, C-10; 1e: C-21). Provenance labels are in each module's
docstring.

### 1. Finding W-1: system A's plain query rounds at the true rate

`whir.WhirConfig.true_rate` (new): level `i`'s query terms at `rho_i = (2^mu_i + k_i) / 2^(mu_i + r_i)`;
`current.a_config` sets it for every system A configuration (rows 6, 7, 9, the node candidates). The W-I
rows (`wi.rounds`) already used the true rates of their layout and do not change. Not changed: the superseded
modules `shipping.py`, `design.py`, `params.py` (records of earlier revisions; nominal rates kept as they were).

Reproduced independently from the formula (`revision5.shape`, `tests/test_revision5.py`), tree of 20,000 proofs,
the 153.0-bit list (369, 226, 185, 168, 161, ... by level rate). Weakest query round, nominal -> true; margin:

| Row, stack, rate | Need | Before (nominal) | After (true) | Margin after |
|---|---|---|---|---|
| 7, 2^22, 1/4 | 152.343 | 153.24 | 153.24 | +0.90 |
| 7, 2^22, 1/2 | 152.343 | 153.15 | 152.97 | +0.63 |
| 9, 2^24, 1/2 | 152.365 | 153.15 | 148.02 | **-4.35** |
| 9, 2^24, 1/4 | 152.365 | 153.24 | 151.23 | -1.14 |
| 9, 2^25, 1/2 / 1/4 | 152.365 | 153.15 / 153.24 | 150.65 / 152.54 | -1.72 / +0.17 |
| 9, 2^26, 1/2 / 1/4 | 152.365 | 153.15 / 153.24 | 151.97 / 153.19 | -0.39 / +0.83 |
| 9, 2^27, 1/2 / 1/4 | 152.375 | 153.15 / 153.24 | 148.02 / 151.23 | **-4.36** / -1.15 |
| 9, 2^28, 1/2 / 1/4 | 152.375 | 153.15 / 153.24 | 150.65 / 152.54 | -1.73 / +0.16 |
| 9, 2^29, 1/2 / 1/4 (new shape) | 152.375 | 153.15 / 153.24 | 151.97 / 153.19 | -0.40 / +0.82 |
| 9, 2^30, 1/2 / 1/4 (new shape, headroom) | 152.386 | 153.15 / 153.24 | 148.02 / 151.23 | -4.37 / -1.16 |

All agree with the document's table to 0.01 bits.

Corrected schedules (the rule: every query round at 153.0 bits or more at the true rate; recommended):

| Row, rate | Before (list) | After (rule) | Margin after | Opening bytes | Keccak-f a verified proof |
|---|---|---|---|---|---|
| 7, 1/4 | 226, 161, 161, 161 | unchanged | +0.90 | 0 | 0 |
| 7, 1/2 | 369, 168, 168, 168 | 369, 168, 168, **169** | +0.79 | +325 | +13 |
| 9, 1/2, last `mu` = 3 (2^24, 2^27, 2^30) | 168 at the last level | **174** (and 169 at `mu` = 6) | +0.76 to +0.78 | +1,829 | +66 |
| 9, 1/2, last `mu` = 4 (2^25, 2^28) | 168 | **171** (and 169 at `mu` = 7) | +0.77, +0.78 | +1,012 | +43 |
| 9, 1/2, last `mu` = 5 (2^26, 2^29) | 168 | **170** | +0.76, +0.77 | +522 | +22 |
| 9, 1/4, last `mu` = 3 / 4 / 5 | 161 | **163** / **162** / 161 | +0.72 to +0.88 | +462 / +263 / 0 | +20 / +11 / 0 |
| 8 (W-I), 1/4 | 226, 161, 161, 161 (fails by 14.19) | **227, 161, 164, 180** (minimal at the need: 226, 160, 163, 179) | +0.92 | | |
| 8 (W-I), 1/2 | 369, 168, 168, 168 (fails by 30.41) | **375, 169, 175, 220** (minimal: 374, 168, 174, 219) | +0.68 | | |
| zero-knowledge leaf, row 6 schedule, 1/4 | 226, 157, 154, 154 | unchanged (W-I: true rates already) | +0.45 | 0 | 0 |

In-circuit cost of the worst node shape (row 9, rate 1/2, final `mu` = 3): +66 Keccak-f and +1,309 cycles (E) a
child verified; a merge of 16 children +1,056 Keccak-f and +20,938 cycles (E), against about 520,000 cycles a
child (M, recursion.md 9.10): +0.25 %.

`output/current-tables.txt` (revision 3/4 candidates table; every row still meets): reductions 3, 3 at 2^24, 1/4,
weakest round query1 152.39 -> final 152.35; at 2^29, 1/4, query1 152.39 -> final 152.31; fold 6 at level 0,
2^24, 1/2, query0 152.32 -> 152.31 and at 1/4 152.57 -> 152.56; fold 6, reductions 3, 3, 2^24, 1/2 query0
152.32 -> final 152.31, 2^24, 1/4 152.57 -> 152.56, 2^29, 1/2 query0 152.32 -> final 152.23; folds 6 and 4,
2^24, 1/2 152.32 -> 152.31, 2^24, 1/4 final 152.51 -> 152.50. The revision-4 node table (`a_bound_tables`, the
old row 9 shape with residual 2^9) is unchanged to two decimals.

### 2. QROM: Theorem Q's constants per system and transcript form

New `qrom.py`. Before: one pair `C1 = 6`, `C2 = 24` (`compose.FsParams`) for every system and no tree figure.
After: form X (system A) `C1 = 6`, `C2 = 6 (a + 2)` = 24; form X with `t' = t + a_V` folded in 12, 96; form C
(system B) 24, 240 (`a` the Merkle arity). Tree of 20,000 proofs, `lambda = 256`:

| System, form | e | IOP term | Hash term | QROM bits | Margin over 64 |
|---|---|---|---|---|---|
| A, form X, at e = 152.343 (document figure) | 152.34 | 67.24 | 78.71 | 67.24 | +3.24 |
| A, form X, weakest corrected round | 152.96 | 67.54 | 78.71 | 67.54 | +3.54 |
| A, form X, `a_V` folded | 152.96 | 67.04 | 78.04 | 67.04 | +3.04 |
| B, form C, at e = 152.343 (document figure) | 152.34 | 66.24 | 77.60 | 66.24 | +2.24 |
| B, form C, weakest round (184 queries) | 152.73 | 66.43 | 77.60 | 66.43 | +2.43 |

Condition Q is a hard failure: `qrom.require` raises `ConditionQFailure`, and `revision5.certify` calls it for
every system (example refused: form C at 192-bit digests, hash term 56.27). System B's per-round need with
`C1 = 24`: 152.52 (unchanged; condition C binds, the QROM condition is 147.87).

### 3. Salt length as an input

New `salts.py`; `--rev5 --salt {256,384,512,576}` (default 512, the lead architect's choice). Per proof
(`N_u = 2^24`): 256 vacuous, 384 `2^-40`, 512 `2^-104`, 576 `2^-136`; per tree (2^14 leaf proofs): vacuous,
`2^-26`, `2^-90`, `2^-122`. Bytes an opened leaf +0 / +16 / +32 / +40; row 8 at 1/4 (732 opened leaves)
+0 / +11,712 / +23,424 / +29,280 B a proof; B leaf (2 x 184 opened) +0 / +5,888 / +11,776 / +14,720 B.
A's leaf Keccak-f unchanged (5 at level 0, 3 later) at every length; B's all-GF(2^256) leaf 2 -> 3 SHA-256
blocks from 512 bits.

### 4. System B: certified and candidate rows

New `johnson.py` (replaces `binius64.johnson_bciks` for revision 5; that function stays as the revision-4
record). Certified: unique decoding, 184 queries at rate 1/8 (weakest algebraic 226.00). Candidate, under
referee review (never certified): Johnson `m = 10` Haböck route 107 (169.34), DKT26 route 107 (211.41),
DKT26 `m = 153` 102 (199.80). Category 3: unique decoding 261; DKT26 `m = 3` refused (216.16). Before: one
candidate line from BCIKS20 Theorem 1.2 (107 queries, fold 168.2 bits at 2^27, rate 1/8).

### Tests

118 -> 153 (`tests/test_revision5.py`: 35 new, each W-1 shape parametrised; the old list fails at rate 1/2 for
every node stack; each minimal count less by one fails).
