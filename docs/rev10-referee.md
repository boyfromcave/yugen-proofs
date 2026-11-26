# Referee report: soundness calculator revision 10 and `decision-qrom-counting.md` section 7

Date: 2026-11-19. Subject: `soundness/` at `40676be` (387 tests) and `docs/decision-qrom-counting.md` section 7
(amendment 1), the first evaluation of the hash term of C. Sharp, P. Grubbs, *Faster and Smaller Anonymous
Credentials from Standardized Signatures*, Cryptology ePrint Archive, Paper 2026/2615 [SG26] (a preprint),
Theorem 6.6 (2) and Definition I.1. The lead architect's ruling SQ-54 (digests stay 256-bit; category 1 claimed on
attack cost with the proven bounds stated beside it) rests on this material.

## 0. Verdicts

| Subject | Verdict |
|---|---|
| The hash-term figures (121.89 / 114.74, A nodes 121.96 / 114.81, quantum 80.40 / 75.63, overall 69.58 / 70.45, 13.26 short, 288 bits) | **PASS**. Every figure reproduced by an independent script from the rendered theorem. Condition: mark `c'` as an estimate (R10-6). |
| The summary statement the lead architect ruled on | **PASS WITH CONDITIONS. The ruling's factual basis stands**: the numbers are right, no attack cheaper than a digest collision was found, and a collision alone does not forge. Conditions: the word "proven" carries its assumptions (R10-2); the claim names BLAKE3 (R10-3). |
| Revision 10 as software | **PASS WITH CONDITIONS**. One path prints "certified" for rows that fail the selected check (R10-1, to be fixed before the output is cited); R10-7 to R10-9 before T-1's values are entered. |

## 1. What was done

- [SG26] pages 57, 58, 59, 130, 131 rendered with pypdfium2 at scale 2.0 and read as images (Protocol 6.5, Section
  6.3, Theorem 6.6 parts (2) to (5), Definition I.1, Section I.1).
- Own script (bisection on the stated inequalities, three test points in `t`, no code shared with `hashterm.py`):
  per-proof and tree levels, classical and quantum, at each `(c', k_q)` of the rows; the options of 7.4; the full
  QROM sum of every row from the row's own weakest round; the guard list.
- `pytest` run: 387 passed. CLI outputs regenerated and compared byte for byte with `output/revision10-tables.txt`,
  `revision10-category-tables.txt` (`--rev7`) and `revision10-proven-basis-tables.txt`: identical.
- A sweep of `category.certify` over categories 1 to 5, both conventions, both hash bases, comparing every printed
  status cell with `Row.checks`; `dkt26.tables` on the same grid; injected values in `hashterm.REPORTED_KQ`.

## 2. Item 1: the theorem and `b`

**The forms (Published, [SG26] Theorem 6.6 (2), page 58, rendered).** ROM: `eps^C_ex(t) = (t + k_q)(eps^k +
c'(t + k_q) / 2^(8b))`, so the hash term is **quadratic**, `c'(t + k_q)^2 / 2^(8b)`. QROM: `eps_ex(t) = 2 sqrt(k_q /
2^(8(b+e))) + 6 (t + k_q)^2 (eps^k + c'(t + k_q) / 2^(8b))`, so the hash term is **cubic with constant 6**,
`6 c'(t + k_q)^3 / 2^(8b)`. They are different expressions and the calculator uses each in its place
(`hashterm.classical_level`, `quantum_level`). `c' = max(2, c) + n_J + 1` (preamble), `c = N_msg max(1, m)`,
`k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2 max(1, l_max))))` (Definition I.1, page 130). `t` is the adversary's
hash-query bound (Section 6.3). Section 7.1 of the record quotes all of this correctly.

**`b`.** Protocol 6.5 (page 57): the oracle's range is `{0,1}^(8(b+e))`, `dg(y)` is the first `8b` bits, the key is
`u_i = dg(H(ch(..)))`; Section I.1 (page 131): leaf and node digests are `dg(H(..))` and the written-back digest
is the first `8b` bits of the stream. So `b` is the one length of keys, leaf digests, node digests and the
write-back. Against `qrom-compilation.md` 2.1, 2.2 and 2.8: A's key, leaf, node are Keccak-256 (32 bytes), the
write-back is stream bytes 0 to 31; B's key is SHA-256, leaves and nodes BLAKE3 `derive_key` at 32 bytes, the
write-back 32 bytes; roots are absorbed as 32-byte items; B's cap is checked against the absorbed root (H7), so no
cap entry is a challenge-input digest. A's 16-byte tags are input prefixes (stream point 16 + 32 + 64 = 112 bytes,
node 16 + 64 = 80), not outputs. B's 16-byte `GF(2^128)` values are field elements, not digests. **`b = 32` holds
for every role the documents list.** Not verified in the builders' code (section 8).

Notes. (i) Statement digests (verifying-key or constraint-system digests, the bound IV, list digests) are part of
`x` and outside the theorem ([SG26] I.1: "the verifier reads them from pre(x) without recomputing them"); where the
tree's statements bind children through such a digest, each adds a collision term of order `t^2 / 2^257`, which is
below `N c' t^2 / 2^256` by 26 bits and moves no figure, but it is not in the 114.74 and should be named. (ii)
SHA-256 keys over an extending input have the length-extension property; in the soundness game every input is
public, so no attack follows, and [SG26] models SHA-2 the same way; it is part of MA-1's content, not a new term.

## 3. Item 2: the figures

| Quantity | Record | Recomputed |
|---|---|---|
| Classical, one proof / tree, `c'` = 2,397 (A leaves) | 121.89 / 114.74 | 121.886 / 114.743 |
| `c'` = 2,401 (B) | 121.89 / 114.74 | 121.885 / 114.741 |
| `c'` = 2,157 and 2,189 (A nodes) | 121.95 to 121.96 / 114.81 to 114.82 | 121.963, 121.952 / 114.819, 114.808 |
| QROM hash part, one proof / tree | 80.40 / 75.63 | 80.396 / 75.633 |
| Full QROM sum of the tree (all three terms) | A 69.58, B 70.45 | worst A row (row 6 mode 1, `e` = 157.03) 69.58; worst B row (`e` = 158.78) 70.45 |
| Digest for a proven 128 | 282.5, so 288 | 282.51; 280 bits gives 126.74, 288 gives 130.74 |
| Range of the proven `t / 2^128` claim | `t` up to `2^101.5` | `2^101.49` |
| 126.6 (book term, once a tree) | `(255 - log2 3.5) / 2` | 126.60 |

**Composition over the tree.** Summing the per-proof bound over the `N` proofs, each at the adversary's full `t`,
is the right (conservative) union: the adversary's queries are shared, and charging every proof the whole budget
over-counts. The verifier's own queries are inside each proof's `(t + k_q)`. No further factor is needed for the
in-circuit verifier **provided** the composition is done by extraction (R10-2): [SG26]'s extractor is the
straight-line database extractor (page 59), so extracting a child proof from an accepted parent adds no rewinding
and at most the verifier's `k_q` queries per extracted proof, at most `N k_q = 2^29.7` in all, negligible against
`2^64` and `2^114`.

**Consistency of the quantum measure.** The quantum figure is "the tree's bound reaches 1/2 at `2^kappa` queries";
the classical one is "`eps(t) <= t / 2^kappa` for every `t`", which at the top of its range is the same event
(bound = 1/2 for each half). `2^64` is applied to the whole sum, not per term. Consistent. (NOTE: the
`t`-independent stream term is evaluated by the calculator at the longest stream; see R10-9.)

## 4. Item 3: is "category 1 on attack cost, 114.74 proven" honest

**A collision does not forge.** What one digest collision (about `2^128` calls classically; about `2^85` quantum
queries by the generic collision algorithm, and the theorem's own QROM hash part stays below 1/2 up to `2^80.4` per
proof, `2^75.6` for the tree, all above `2^64`) gives a prover:

- at a leaf or node: one position, or one subtree, that opens two ways, so one commitment stands for two oracles
  and the prover picks one **after** the round's challenge: the round's error at most doubles;
- at a key: two transcripts sharing one challenge; every later key hashes the whole past and differs again.

A forgery needs the choice to be about `1 / eps` wide (about `2^157`), not 2. So the collision is a necessary
event of the proof technique (the extractor's bad set), not a sufficient attack. The claim "no known attack is
cheaper than a digest collision" is true and conservative.

**The best attack found.** Fiat–Shamir grinding of the weakest round: one stream evaluation per attempt, success
`eps` per attempt, so about `2^157.0` hash calls (system A, row 6 mode 1) to `2^158.8` (B); at `2^128` calls its
success probability is about `2^-29`. Quantum: amplitude amplification over the same search, about `2^78.5`
iterations, above `2^64` and consistent with the proven 69.58 (which carries `N` and the constant 6). Checked and
found no cheaper: multi-target over the 20,000 proofs and the positions (an attempt's success does not rise with
the number of targets; collision search does not get cheaper with `N c'`); second preimages on honest digests
(`2^256 / N c' = 2^230.5`, and they forge nothing for a false statement); salt and tag effects (salts give the
freedom to make a collision meaningful, already assumed above; tags are fixed prefixes). No attack below `2^128`
calls on the compiled protocol was found.

**So:** "classical: met on attack cost; proven bound 114.74 bits, 13.26 short" is an honest summary, with two
corrections of wording (R10-2, R10-3). "Proven 114.74" means: under the theorem, the tree's forgery probability is
at most `t / 2^114.74` for every `t` up to `2^114.74`, and at most `t / 2^128` only for `t` up to `2^101.5`.

## 5. Items 4 to 6

**Options (7.4).** (a) correct. (b) 288 bits is the least whole-byte digest (280 gives 126.74); the level reached
is **130.74**, not "128.0" (R10-4). (c) per-tree term: 121.89 at 256 bits, 125.89 at 264, **129.89 at 272**:
correct. (d) 127.5 at 256 bits for a bound `t^2 / 2^256` taken once a tree: correct as arithmetic; with the tree
sum kept it is 120.36; the reason given is too strong (R10-4). (e) 0.5 bit a halving, 121.89 at `N = 1`: correct.
Proof-byte costs of (b): not checked.

**The guard (7.5).** `log2(1.1) = 0.1375` reproduced. The list reproduced: 14 of A's 20 rows and row 7 at 1/2 are
not certified; A row 6 mode 0, row 8 mode 1 at 1/4, row 9 `2^25` at 1/2, `2^26`, `2^27`, `2^29` at 1/4, row 7 at
1/4 and every B row are. Defensibility: R10-7. T-1's list: R10-9.

**"Certified is computed" (7.3, R9-2).** `category.Row` holds on the whole grid (no status cell says certified
with a failing check). One path fails: R10-1.

## 6. Findings

| # | Class | Location | Finding | Fix |
|---|---|---|---|---|
| R10-1 | **MAJOR** | `cli.rev9_tables` (calls `dkt26.tables(None, convention)` without the basis); `dkt26.Row8.certified`, `Row8.status`, `dkt26.CERTIFIED`; `output/revision10-proven-basis-tables.txt` lines 158, 161, 169, 238; record 7.3 last paragraph | `yugen-soundness --hash-basis proven` prints "certified (unique decoding; ... every t ...)" for system B's two unique-decoding rows (192 at 1/8, 235 at 1/4) while their classical hash part is 114.74 against 128, the check that basis selects. The record's sentence "certifies no 256-bit row" is false for the committed file. `Row8` has no `hash_basis`, and its label never states the basis even under the default. | Give `Row8` the profile's `hash_basis`; compute `certified` from the same checks as `category.Row` (one shared function); print the basis in the label; pass `hash_basis` through `dkt26.tables` and allow `--rev8 --hash-basis`; a test that greps every CLI output under `proven` for a positive "certified". Regenerate the output file. |
| R10-2 | **MAJOR** | record 7.3 ("both systems meet it, proven"), 7.9; `soundness-method.md` 8.5b "Reduction to the proofs"; plan row SQ-54 | "Proven" is stated without its conditions. The figures are theorems only given: (i) the random-oracle modelling MA-1, MA-2' ; (ii) the recursion heuristic C2 (an in-circuit verifier evaluates a hash function, not the oracle; no random-oracle proof covers it); (iii) round-by-round **knowledge** soundness of both IOPs, whose written form is still owed (K-A, K-B, `qrom-compilation.md` 3, H3); (iv) Lemma D for B's repeated openings (refereed, pass with conditions); (v) [SG26] being a preprint; (vi) `c'`, `k_q` estimated. Further, 8.5b's walk-down argues through "a true statement has an accepted child proof": that is existence, and soundness bounds only proofs the adversary outputs. An attacker publishes the root proof alone, so the tree sum needs **extraction** down the tree, which uses (iii). | Wording, wherever the figures appear (record 7.3, the specification, SQ-54): "proven in the random-oracle model under assumptions MA-1, MA-2', C2 and obligations K-A, K-B (open)". Rewrite 8.5b's reduction as a lemma by straight-line extraction: `eps_tree(t) <= sum_v eps_ex,v(t + N k_q)`, Adapted from [SG26] Theorem 6.6 (2) and its extractor ([CMS19] Theorem 8.6 as cited on page 59); no figure moves (`N k_q = 2^29.7`). Close K-A, K-B. |
| R10-3 | MINOR | plan row SQ-54; record 7.3 | The claim names "a collision in SHA-256 or Keccak-256". System B's leaf and node digests are BLAKE3 `derive_key` (7-round compression, one compression a node). The attack-cost claim for B rests on BLAKE3's collision resistance at `2^128` as well, a primitive NIST's category-2 benchmark does not name. | Name it: "a collision in a transcript digest (Keccak-256; SHA-256 and BLAKE3 in system B)", with the BLAKE3 evidence of `decision-b-merkle-hash.md`. For the lead agent (plan file). |
| R10-4 | MINOR | record 7.4 rows (b), (d) and the closing sentence | (b) the level at 288 bits is 130.74, not 128.0. (d) "any bound of the form `t^2 / 2^256` caps a 256-bit digest below 128 (birthday)": a bound at the birthday probability itself, `t^2 / 2^257`, gives exactly 128.0 in the record's own convention, and since a collision does not forge (section 4) nothing rules out a proof without a collision term. "Only a wider digest reaches a proven 128" is true of the bounds in hand, not a fact about the protocol. | Correct the cell; reword to "with the published bounds and the lemmas considered here". The ruling is unaffected (it keeps 256 bits). |
| R10-5 | MINOR | record 7.2, last paragraph | "Together 25.4 bits on `2 kappa`, 12.7 bits on `kappa`": `log2(N c') = 25.52`; net of the book's `log2 3.5 = 1.81` the change is 23.71 bits on `2 kappa` and **11.86** on `kappa` (126.60 - 114.74). | Replace the two numbers. |
| R10-6 | MINOR | record 7.2 table, SQ-54; `spbcs.TranscriptCounts` | `c'` is an estimate (`N_msg = 2 (rounds + 512)`, `m = 2`, both "upper figures" not yet confirmed by a built verifier), printed without (E). A factor 2 in `c'` is 0.5 classical bit and 0.33 quantum bit. The calculator has an input with provenance for `k_q` only. | Print `c'` with (E); add a reported `c` (with `N_msg`, `m`) beside `REPORTED_KQ`; T-1's acceptance compares `c'` as well as `k_q`. State 114.74 as "114.7 (at the estimated `c'`)" until then. |
| R10-7 | MINOR | record 7.5; `hashterm.KQ_GUARD_FRACTION` | 10 % does not cover the record's own example at the small rows: `OTHER_ROUNDS` doubled is +15.2 % at `k_q` = 13,456 and +11.3 %, +11.6 %, +12.3 % at three rows that are certified today (row 6 mode 0, row 8 mode 1 at 1/4, row 7 at 1/4; their margins 0.307, 0.258, 0.192 still cover it: 0.154, 0.159, 0.167). With one more Merkle level as well, row 7 at 1/4 fails (0.215 against 0.192). The Merkle part of the estimate (every position charged at `l_max`) is an over-count, which is the real support for a small guard and is not said. | Either state the guard per row in absolute terms, `log2(1 + k_q + 4 OTHER_ROUNDS + q_IOP) - log2(1 + k_q)` (covers both named errors together), or keep 10 % and record that row 7 at 1/4 is certified only against one error at a time. Add the over-count remark. |
| R10-8 | MINOR | `hashterm.kq_input`, `REPORTED_KQ`; `category.certify`; `dkt26.Row8.kq` | (i) A reported `k_q` is accepted with no plausibility check: entering 1 certifies A row 6 mode 1 at a need of 145.87. (ii) A reported value above the estimate does not re-solve the row as 7.6 promises: `certify` raises `CategoryRefusal` for the whole table (fail-closed, but not the stated behaviour), and a re-solved row would change its query tuple and lose its key. (iii) `Row8` never reads `REPORTED_KQ`. | Refuse a reported `k_q` below the floor the row's own shape implies (`2 x 2 x` listed rounds `+ 2 q_IOP`); key reports by shape, not by count, or re-solve to a fixed point; read reports in `Row8`; tests for all three. |
| R10-9 | MINOR | record 7.6 (task T-1); `spbcs.SpbcsTree.stream_term_log2` | T-1 omits: (a) the **shortest and longest stream** of each verifier message. [SG26] page 59: "A longer stream only lowers these terms, so the theorems hold as stated", so the theorem's `b + e` is the shortest stream, while the calculator evaluates `2 sqrt(k_q / 2^(8(b+e)))` at the longest (printed -4765, -2953). At B's shortest stream (32 bytes, `e = 0`) the tree's term is `2^-105`: no figure moves, but the printed value is not the theorem's. (b) Hash calls the verifier and its host circuit make **outside the four parts** (statement, verifying-key and list digests, public-input hashing), with their domain separation from the four parts. (c) Per message `m_i` and what each item contributes to a challenge input (roots only; any cap entry absorbed as an item counts in `c`). (d) A statement that no comparison anywhere uses fewer than 32 digest bytes. (e) Evidence that no sampler rejects (`eps_ov = 0`). Present and sufficient: padded slots, duplicates, the cap's path to the root, the maximum over accepted proofs, native and in-circuit separately. | Add (a) to (e) to T-1's item 1 and 2; evaluate the stream term at the shortest stream. |
| R10-10 | NOTE | record 7.2, `soundness-method.md` 8.5a | The tree figures are for one output tree (`attempts = 1`). An adversary submitting many trees is covered by the same `t` only through the theorem's single-output definition; a per-output union is not in the figures. Recorded before; restate beside the figures. | Wording. |
| R10-11 | NOTE | `category.field_summary`, QROM-by-digest tables under `--hash-basis proven` | Headings say "every certified shape", "the category's certified rows" where that basis certifies none. | Use `_rows_word`'s approach there. |

## 7. Answers in one place

1. ROM and QROM hash terms differ (quadratic; cubic with constant 6); both are evaluated correctly; `b = 32` for
   every documented role in both systems.
2. All figures reproduce. The tree sum is the right composition given extraction; `t` is shared and charged in
   full to every proof; `2^64` is applied consistently.
3. Honest, with R10-2 and R10-3. Best attack found: grinding the weakest round, about `2^157` hash calls
   classically, about `2^78.5` quantum iterations; a digest collision (`2^128`; `2^85` quantum) is cheaper but does
   not forge.
4. Ceilings correct except the cell "128.0" (130.74) and the reason given for (d).
5. 10 % is an allowance that holds for one named error at a time; the uncertified list is right; T-1 needs five
   additions.
6. One path prints "certified" for failing rows (R10-1).

## 8. Not checked

- The builders' code: digest lengths, tags, cap handling and the query counts were taken from
  `qrom-compilation.md` 2 and 3, not from `yugen-proof-a` or `yugen-proof-b2` sources.
- [SG26]'s proofs (Lemma I.12, Theorem I.16) were not re-derived; the theorem is used as stated. Definitions H.3,
  H.4 were not re-read.
- The rounds' errors (`e`, the weakest round of each row) and the listed round counts were taken from the
  calculator; only the hash term, the need formula and the QROM sum were recomputed.
- The proof-byte costs of option (b); the Lean files; the NIST call-for-proposals quotations (not re-read from
  rendered pages in this pass); the BLAKE3 cryptanalysis behind MA-2'.
- Categories 2 to 5 were exercised for the status logic only, not for their figures.

## 9. Provenance

**Published:** [SG26] Protocol 6.5, Theorem 6.6 (2), Section 6.3, Definition I.1, Section I.1 (pages 57 to 59, 130,
131, rendered), used as stated. **Original (the Ycash developers, 2026), this report:** findings R10-1 to R10-11;
the analysis of what a digest collision gives a prover (section 4), standard generic reasoning and an attack
estimate, not a theorem; the extraction form of the tree lemma proposed in R10-2 (Adapted from [SG26] Theorem 6.6
(2); unproved here).
