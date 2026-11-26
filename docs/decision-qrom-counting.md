# Decision record: the counting convention of the classical tree condition (condition C-2, finding Q-5)

Part of Yugen. `yugen-proofs`. **Revision 1 (2026-11-19); amendment 1 (2026-11-19, section 7,
calculator revision 10: the hash term of the same theorem, `k_q` as an input with provenance, task T-1; a draft until
refereed).** **Amendment 2 (2026-11-19, section 7.11, calculator revision 10.2: the tree figures after `docs/tree-extraction-referee.md`; every tree figure conditional on C2, K-A, K-B, T-1).** Ruling by the lead architect,
2026-11-19. Written by the calculator's author; **a draft until refereed**. Implemented in the soundness
calculator, revision 9 (`soundness/CHANGELOG.md`, revision 9; `soundness/tests/test_revision9.py`).

## 0. The decision

**Every t.** The classical condition of a proof tree is read as [SG26] Theorem 6.6 (2) states it: for
every query bound `t` and every `(t, 0)`-adversary. A round of a proof whose verifier makes `k_q` hash
queries needs, in a tree of `N = 20,000` proofs,

    e >= kappa_C + 1 + log2 N + log2(1 + k_q)        (157.0 to 158.8 bits at category 1, per row)

with `k_q` the row's own (Definition I.1), solved to the row's least fixed point. This is the calculator's
**only default** convention, for both proof systems (A, the WHIR / leanVM fork; B, the Binius64 fork) and every
category. The previous counts (the book need, 152.52 bits a round at category 1) are available only behind an
explicit option (`--convention t-ge-kq`) whose every row reads "non-default convention (t >= k_q), not certified".

**Not adopted now: Lemma M** (section 2.3), which would restore lower counts. It is recorded as possible future
original work, **unproved**.

**Amendment 1 (section 7, calculator revision 10).** The hash term of the same theorem, evaluated per row: the tree's
proven classical level of the hash part is 114.74 bits (A, B), not 126.6; category 1's classical hash part rests on
condition H's attack rule (the recorded basis); the quantum measure is met, proven. `k_q` is an input with provenance;
rows with an estimated `k_q` and a margin under the 0.1375-bit guard are not labelled certified until task T-1 (7.6).

**Amendment 2 (section 7.11, calculator revision 10.2).** The tree reduction is Theorem TE' (`lemma-tree-extraction.md`
revision 2), a theorem of the ROM in which the recursion heuristic C2 is a named event outside the theorem. Every tree
figure of this record, classical and quantum, is **conditional on C2, K-A, K-B and T-1**, and none is an unconditional
theorem; where section 7 says "proven" of a tree figure it is to be read so. The calculator prints the tree's classical
hash level as 121.89 bits (114.74 beside it as the comparison) and the tree's QROM level as 69.58 / 70.45 (claimed;
76.72 / 77.60 beside it). No query count moves.

## 1. The question

Source: C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, Cryptology
ePrint Archive, Paper 2026/2615 [SG26] (the copy in the lead architect's folder; it states no venue). Read for this
record **from the rendered page images** (the text layer can drop symbols; `docs/soundness-rev8-referee.md` R8-9):

- Theorem 6.6 (2), page 58 (Published): if the IOP is round-by-round knowledge sound with errors at most
  `eps_k`, spBCS is adaptively knowledge sound (Definition H.3) with extraction error at most
  `eps^C_ex(t) = (t + k_q)(eps_k + c' (t + k_q) / 2^(8b))` in the ROM (Theorem I.16), and has adaptive
  soundness error at most that (Definition H.4). Section 6.3, same page: "In Parts (1), (2), (3) and (5) the
  adversary makes at most t hash queries".
- Definition H.3, page 128: errors are "functions from N to the nonnegative real numbers" and the extractor
  works "for every t and every (t, 0)-adversary A"; the paragraph after it: the definition "bounds the errors at
  every query bound". Definition H.4, page 129: "for every t ∈ N and every (t, 0)-adversary A".
- Definition I.1 (Published): `k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2 max(1, l_max))))`, almost all of
  it Merkle-path hashes.

Nothing in the theorem restricts `t` to `t >= k_q`. The referee's reading (`docs/soundness-rev8-referee.md`
section 7) is confirmed: reading (a) below is a convention added to the theorem; reading (b) is the theorem.

The calculator states a classical tree claim as `eps(t) <= t / 2^(kappa_C + 1)` for every `1 <= t <= 2^kappa_C`
(`soundness-method.md` 8.5b); `t = 0` is bounded by `t = 1`. Under [SG26]'s bound that claim binds at `t = 1`,
where the verifier's `k_q` (`2^14` to `2^15.6`) replaces the book's `1 + k` (`2^9.2`).

## 2. Options considered

### 2.1 (a) `t >= k_q`: keep the counts of revisions 1 to 8

Read condition C only for adversaries that make at least `k_q` hash queries ("fewer than one verification's
worth of hashing is not a category-1 adversary"; `qrom-compilation.md` 6.2). Then `t + k_q <= 2t` and the book
need (152.52) stands, 8.2 bits above (a)'s own 144.29.

- For: no count changes; no build changes; every built proof stays valid.
- Against: it is not what [SG26] states; it is a restriction of the adversary class that the definitions do not
  make. What it loses is confined to adversaries making fewer hash queries than a per-row threshold (9 to 74
  queries at the rows' present counts, referee report section 7): for them the proved bound is an absolute
  `2^-122.8` or better instead of `t / 2^129`, a shortfall of at most 6.2 bits at `t = 1`. Small, but it is a
  claim the published theorem does not make, and every row labelled "certified" would need the words "book
  convention" beside it.

### 2.2 (b) Every t: re-solve every row (adopted)

- For: the theorem as stated; no lemma of ours in the soundness chain; a row is certified with no convention
  attached.
- Against: more queries, with proof bytes and verifier rows. At category 1, each row at its own `k_q`:

| Row | (a) | (b) | Added | Proof bytes (E, size model) |
|---|---|---|---|---|
| B, unique decoding, rate 1/8 (leaf and node) | 184 | 192 | +8 | +3.4 % to +3.5 % |
| B, Johnson `m = 10`, rate 1/8 (candidate, DKT26 preprint) | 107 | 111 | +4 | +2.8 % to +3.0 % |
| B, Johnson `m = 10`, rate 1/16 (candidate) | 80 | 82 | +2 | +1.9 % |
| B, unique decoding, rate 1/16 | 168 | 174 | +6 | +2.8 % to +2.9 % |
| B node, unique decoding, rate 1/4 | 225 | 235 | +10 | +3.5 % |
| B node, Johnson `m = 10`, rate 1/4 (arithmetic only, R8-3) | 165 | 171 | +6 | +2.8 % |
| A leaves (rows 6, 8; modes 0, 1; rates 1/4, 1/2), each level | | | +4 to +12 | +1.8 % to +2.7 % |
| A node row 9, `2^24` to `2^30`, rates 1/2 and 1/4, each level | | | +6 to +15 | +3.2 % to +3.7 % |

  The referee's figures (192 / 111 / 82 / 235 / 171) are reproduced exactly. Consequences for the builds:
  - the built rate-1/4 node (226 queries) **does not meet** the new need (235);
  - every build at the old counts is below its row (A's leaves and nodes; B's 184 / 107 / 80);
  - **the rate-1/8 Johnson merge slot**: the referee estimated (E, from `yugen-proof-b2` `parameters.md` 14.4)
    that with groups of six 111 queries need 19 groups, 2,058,958 + 64,036 = 2,122,994 AND rows, **about 1.2 %
    over `2^21`**. The builder's later fit table (`yugen-proof-b2` `docs/parameters.md` 15.5, read for this
    record; C, counted at cap 5) has the merge slot at 111 queries in **groups of five: 1,985,497 AND rows, inside
    `2^21` (94.7 %)**, so the merge slot fits after a change of grouping; the **candidate leaf slot at rate 1/8
    does not fit `2^21` at 107 or 111** (2.39 M / 2.46 M) until its residue shrinks (15.5 there). The rate-1/16
    merge slot fits at 82 (1,830,327);
  - the rate-1/4 node: 235 has 0.52 bits of margin (236: 1.20); the builder's rule in 15.5 there (build 235 if it
    has at least 0.3 bits, else 236) gives **235**. System B at rate 1/2: 368 -> 385. System A row 7 (the plain
    tree leaf, `2^22`): the calculator's 225, 160, 160, 160 (the build's 153.0-bit rule holds 226, 161, 161, 161)
    -> 233, 165, 165, 165 at rate 1/4, 380, 173, 173, 173 at rate 1/2;
  - category 3 (reported, not a project row): A's `2^30` node at rate 1/2 grows to 1,841,754 B (E), over
    `PROOF_BYTES_MAX` (1,835,008 B).
  - Condition Q (QROM) improves, since `e` rises and the QROM part already adds `k_q` to `t`: A 67.25 -> 69.58,
    B 67.43 -> 70.45 bits against 64.

### 2.3 (c) Lemma M: keep lower counts by a new lemma (not adopted now; future work)

Proposed by the referee (`docs/soundness-rev8-referee.md` section 7). **Original as far as checked (the Ycash
developers, 2026), a sketch, unproved, unreviewed**; sources consulted for it: [SG26] Section 6 and Appendix I as
listed in the referee report, where no such statement was found. Restated in our words:

> **Lemma M (unproved).** In the random-oracle model a proof is accepted only if every Merkle hash the verifier
> evaluates on an authentication path was queried by the adversary, except with probability at most
> `k_q / 2^(8b)` (an unqueried output is uniform and must equal a value already fixed). So an adversary with
> fewer than `k_min` queries, `k_min` the least number of distinct path hashes of any accepted proof, succeeds
> with probability at most `k_q / 2^(8b)`; for `t >= k_min`, `t + k_q <= t (1 + k_q / k_min)`.

With it the classical need would be `kappa_C + 1 + log2 N + log2(1 + k_q / k_min)` for every `t`. The referee's
illustrative figure (E, one path of 14 hashes in each of 6 trees, `k_min = 84`): 150.4 (107 row), 151.1 (184),
151.4 (225), all under 152.52, so the old counts would hold for every `t`. Not adopted now because:

- it is unproved and unreviewed: the step "an unqueried output must equal a fixed value" needs care with the
  extractor's database and with outputs fixed only later in the adversary's run; the bound must be per accepted
  proof, union-bounded over the tree;
- `k_min` depends on tree depths, cap layers and the tree count of each shape and must be derived per shape;
- the soundness chain would rest on a lemma of ours where a published theorem suffices.

**Task (future work, not scheduled):** write Lemma M with a full proof against [SG26] Definition H.3 and Section
I.1; derive `k_min` per built shape; have it refereed. **Acceptance:** a refereed proof, `k_min` per shape from the
build's tree census, and a calculator option that applies it only when the referee's sign-off is recorded.

## 3. The ruling

The lead architect, 2026-11-19: the convention follows the referee's reading of [SG26] Theorem 6.6, "for every t
and every (t, 0)-adversary". Every t is the only default. Lemma M is not adopted now; it is recorded as possible
future original work that would restore the lower counts, clearly marked unproved.

## 4. What changes

| Where | Change |
|---|---|
| `soundness/` | revision 9: `category.Profile.convention` (default `every-t`), `every_t_need`, per-row `k_q` fixed points for A and B, `dkt26.row(convention=...)`; `--convention t-ge-kq` labelled non-default; 367 tests |
| `qrom-compilation.md` 6.2, 9 (T-6), 10 | Q-5 decided: (b) |
| `soundness-method.md` 8.5b | the convention recorded (T-6's acceptance) |
| `binius-johnson-row.md` 0.4, `decision-security-profile.md` 2.4 | dated revision notes with the new counts |
| Other repositories | listed in the appendix for the lead architect (the calculator's author does not edit them) |

## 5. What would reverse it

- **Lemma M proved and refereed** (section 2.3), with `k_min` per shape bringing each row's need under its old
  count's query bits: the old counts would return for every `t`, under a lemma of ours.
- **A published statement** (in [SG26] or elsewhere) bounding spBCS's extraction error by a function of `t` alone
  for small `t` (for example `t (eps_k + ...)` without the additive `k_q`): the need would fall to it.
- **A change to the transcript** that lowers `k_q` (fewer opened positions, shorter paths, fewer messages): the
  every-t counts fall with it, by `log2` of the ratio.
- Not a reason: the merge slot's 1.2 % overrun or any proof-size cost; those are met by trimming the slot or the
  shapes, not by changing what the theorem is read to say.

## 6. Provenance

**Published, used as is:** [SG26] Theorem 6.6 (2) (p. 58), Section 6.3 (p. 58), Definitions H.3 (p. 128), H.4
(p. 129), I.1 (`k_q`). **Original (the Ycash developers, 2026):** the per-row `k_q` fixed point and the tree
accounting (REFERENCES.md O-13, O-68); finding Q-5 (`qrom-compilation.md` 6.2); the counts of section 2.2
(calculator revision 9, unreviewed); the referee's per-row thresholds and merge-slot estimate
(`soundness-rev8-referee.md` section 7); Lemma M (O-69, the referee's proposal, unproved, not adopted).

## Appendix: places outside this repository that carry a stale count or the old convention (for routing)

Read-only survey, 2026-11-19, at `yugen-spec` (working tree), `yugen-proof-b2` `3a064a5`, `yugen-proof-a` `927cac2`.
New values: `soundness/CHANGELOG.md` revision 9.

| Place | States | Under every `t` |
|---|---|---|
| `yugen-spec/spec/yugen-protocol.md:3922-3925` (A.1) | row 7 226, 161, 161, 161 (1/4), 369, 168, 168, 169 (1/2); row 8 227, 161, 164, 180 (1/4), 375, 169, 175, 220 (1/2); row 9 by shape (369, 168, ...; 163/162/161 at 1/4) | row 7 233, 165 x3 / 380, 173 x3; row 8 (calculator) 233, 166, 168, 185 / 386, 174, 180, 228; row 9 +6 to +15 a level (from the build's re-run) |
| `yugen-spec/spec/yugen-protocol.md:4042-4043` (A.2) | 152.52 bits a round, `round_centibits` 15,252; 184 at 1/8 (368, 225, 168 at 1/2, 1/4, 1/16) | per-row need 158.59 (1/8); 192 at 1/8 (385, 235, 174) |
| `yugen-spec/spec/yugen-protocol.md:4048` | candidate rows "107 or 102 queries" | 111 (82 at 1/16); 102 withdrawn |
| `yugen-spec/spec/yugen-protocol.md:4068-4069` (A.3) | QROM 67.54 (A), 67.43 (B) | 69.58, 70.45 |
| `yugen-spec/spec/yugen-protocol.md:4151` | B's certified row 184 at 1/8 | 192 |
| `yugen-spec/spec/decisions.md:134` (SPEC-125) | 184 at 1/8, 152.52 bits a round | a new decision row (192; the convention) |
| `yugen-proof-b2/src/params.rs:176-178` | `CAT1_QUERIES = [0, 368, 226, 184, 168]` | `[0, 385, 235, 192, 174]` |
| `yugen-proof-b2/src/params.rs:183` | `CAT1_ROUND_CENTIBITS = 15_252` | the row's need (15,859 at 1/8; it differs by rate: 158.50 to 159.46) |
| `yugen-proof-b2/src/params.rs:184-189, 232, 498-506` | `JOHNSON_QUERIES_RATE_8 = 107`, `_16 = 80`; test asserts 107 | 111, 82 |
| `yugen-proof-b2/src/params.rs:110, 250, 493` | list size 29.70 / 42, unlabelled (R8-14) | label "conservative; DKT26 (38) gives 19 / 31" |
| `yugen-proof-b2/src/params.rs:159` | slot counted at 184 queries | 192 |
| `yugen-proof-b2/docs/parameters.md:139-150` (2a.2) | `e >= 152.52`, the row table (368, 225, 184, 168) | every `t`; 385, 235, 192, 174 |
| `yugen-proof-b2/docs/parameters.md:2932-2945` (14.4), `3018` (14.7), `3149-3175` (15.5) | 107 / 80; node built at 226; 15.5 already lists 192 / 111 / 235 or 236 / 82 | confirmed: 192, 111, 82, **235** (0.52 bits), 174 at 1/16 |
| `yugen-proof-b2/docs/parameters.md:2130-2160` (11.3) | D-term 49 at the 184 build | unchanged in form; the build at 192 has its own `n_f` |
| `yugen-proof-a/vendor/leanMultisig/crates/verifier/src/params.rs:230, 246, 252, 261, 271, 277, 481, 514` | the 153.0-bit rule and the tables `CAT1_TREE_LEAF_QUERIES`, `CAT1_TREE_NODE_QUERIES`, `CAT1_TREE_WI_QUERIES` it generates | a per-row need of 157.0 to 158.8 (or one rule at 158.8); every table re-generated |
| `yugen-proof-a/tests/params.rs:172-202` | asserts 153.0 bits and minimality at 153.0 | the new need |
| `yugen-proof-a/bench/soundness/shapes.py:7-14`, `cert.py:7` | the 153.0-bit rule | the calculator's revision 9 (`category.a_leaf`, `a_node`, `a_plain_leaf`) |
| `yugen-proof-a/docs/parameters.md:31-33, 46-47, 75-83` | rows 7 to 9 at 153.0 bits; 226, 161, 161, 161; 227, 161, 164, 180 | as the spec rows above |

History entries (`yugen-spec/spec/CHANGELOG.md:427` and similar) are records and need no change.

## 7. Amendment 1 (2026-11-19): the hash term, `k_q` as an input, task T-1 (calculator revision 10)

Written by the calculator's author after `docs/rev9-and-lean-referee.md` (findings R9-1, R9-2, R9-4) and
`docs/lemma-d-referee.md` (finding m-1). **A draft until refereed.** Sections 0 to 6 stand; this section adds to them.
Nothing here changes a query count, a digest length or any other parameter.

*Revision 10.1 (2026-11-19, after `docs/rev10-referee.md`, findings R10-1 to R10-11): edited in place where the
referee asked for a correction; the list of changes is 7.10. Still a draft until refereed; no query count moves.*

### 7.1 What the theorem says, read from the rendered pages

[SG26] Theorem 6.6 (2) (page 58, read from the page image rendered with PDFKit at scale 2.2; Published): if the IOP
is round-by-round knowledge sound with errors at most `eps^k`, spBCS is adaptively knowledge sound with extraction
error at most

    eps_ex(t)   = 2 sqrt(k_q / 2^(8(b+e))) + 6 (t + k_q)^2 (eps^k + c' (t + k_q) / 2^(8b))     in the QROM,
    eps^C_ex(t) = (t + k_q) (eps^k + c' (t + k_q) / 2^(8b))                                   in the ROM,

and adaptive soundness error at most the same (Definition H.4), with `c' = max(2, c) + n_J + 1` (the theorem's
preamble) for "digests of b bytes" and "streams of b + e bytes". Definition I.1 (page 130): `c = N_msg max(1, m)`, the
digest bound of a challenge input, and `k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2 max(1, l_max))))`, "the
verifier's hash-query bound".

**What `t` is.** Section 6.3 (page 58): "In Parts (1), (2), (3) and (5) the adversary makes at most `t` hash queries".
`t` is the adversary's hash-query budget, and the theorem bounds the error **for every `t`** (Definitions H.3, H.4;
section 1 above). The theorem does not fix a budget. **The project fixes the range of its claim**: classically,
`eps_tree(t) <= t / 2^kappa_C` for every `1 <= t <= 2^kappa_C` (`soundness-method.md` 8.5b; `kappa_C = 128` at
category 1, an adversary of up to `2^128` hash queries), half of it for each term of the bound; in the QROM, the
tree's bound stays below `1/2` up to `t = 2^kappa_Q = 2^64` quantum queries. The IOP term binds at `t = 1` (section
0); the hash term binds at the top of the range, `t = 2^kappa_C`, because `(t + k_q)^2 / t` grows with `t` there
(both end points are checked; `hashterm.classical_level`).

**What `b` is in our framing.** Section I.1 (page 131): one random oracle with four disjoint parts (`ch`, `leaf`,
`node`, `stream`); every digest is "the first 8b bits" of an oracle answer, and "the written-back digest `dg(y_i)` is
the first 8b bits of the same stream". So `b` is the length of every digest the transcript writes: challenge-input
keys, leaf digests, node digests and the written-back stream prefix. In our transcripts (`qrom-compilation.md` 2.2,
2.8): system A, Keccak-256 keys, leaves and nodes, SHAKE256 streams, 32-byte write-back (the 16-byte part **tags**
are input framing, not output length); system B, SHA-256 keys, BLAKE3 `derive_key` leaves and nodes at 32 bytes
(the category-1 row, MA-2'), SHAKE256 streams, 32-byte write-back. **Every part is 32 bytes in both systems, so
`b = 32`** as the theorem states it. A transcript whose parts had different lengths would need `b` = the shortest
(an adaptation, not proved here).

### 7.2 The figures (finding R9-1), every row, category 1, `N = 20,000`

Per row the calculator now prints `c'`, `k_q` with its provenance, and the hash term per proof and over the tree,
classical and quantum (`soundness/output/revision10-tables.txt`, `revision10-category-tables.txt`):

| | `c'` | Classical bits, one proof | Classical bits, tree | Shortfall against 128 | QROM bits, one proof | QROM bits, tree | QROM margin against 64 |
|---|---|---|---|---|---|---|---|
| System A, masked leaves (rows 6, 8) | 2,377 to 2,397 (E) | 121.89 | **114.74** | 13.26 | 80.40 | 75.63 | +11.63 |
| System A, nodes (row 9, `2^24` to `2^30`) | 2,157 to 2,189 (E) | 121.95 to 121.96 | 114.81 to 114.82 | 13.18 to 13.19 | 80.45 | 75.68 | +11.68 |
| System B, every row (192, 174, 235, 385; candidates 111, 82) | 2,401 (E) | 121.89 | **114.74** | 13.26 | 80.40 | 75.63 | +11.63 |

`c'` is an estimate (E; finding R10-6): `N_msg = 2 (listed rounds + 512)` in A and `2 x 600` in B, `m = 2`, both upper
figures not yet confirmed by a built verifier; a factor 2 in `c'` moves the classical figure by 0.5 bit and the quantum
one by 0.33. Every figure of this table is therefore stated "at the estimated `c'`": the classical tree level is **114.7
(at the estimated `c'`)** until task T-1 reports `N_msg` and `m` (the calculator prints `c'` with `(E)` and takes a
reported `c'` from the same report line as `k_q`). "Proven" in this section means proven under the assumptions of 7.3.

Classical: the largest `kappa` with `N c' (t + k_q)^2 / 2^256 <= t / 2^(kappa + 1)` for every `1 <= t <= 2^kappa`;
in closed form (k_q negligible against `2^kappa`) `kappa = (255 - log2(N c')) / 2`. QROM: `N 6 c' (t + k_q)^3 /
2^256 = 1/2`. The full QROM sum of the tree (IOP, hash and stream terms) is unchanged from revision 9: A 69.58, B
70.45 against 64.

**The referee's figures are confirmed.** 114.7 (B) and 114.8 (A) reproduce: the referee's A figure is A's `2^30`
node (`c' = 2,189`, 114.81); A's leaves (`c' = 2,397`) are 114.74. The digest a proven classical 128 needs is
`8b >= 2 kappa_C + 1 + log2(N c') = 257 + 14.29 + 11.23 = 282.5`, so **288 bits (36 bytes)**, not 264; one proof
alone (`N = 1`) would need 272. The tree claim `eps_tree(t) <= t / 2^128` is proved by [SG26] for `t` up to about
`2^101.5`.

**Where 126.6 and 264 came from.** From the hash term of the SNARGs book's BCS theorem (Chiesa, Yogev, Theorem
25.2.1, `3.5 t^2 / 2^lambda`), "taken out once" for the tree (`soundness-method.md` 8.2, 8.5b; `design-basis.md`
finding S-2): `(255 - log2 3.5) / 2 = 126.6` bits, and 264 the least whole-byte `lambda` with `(lambda - 1 - log2 3.5)
/ 2 >= 130` (128 plus 2 for the four-layer chain; `targets._digest_proven`). Two things changed it: (i) the
transcript is spBCS, whose theorem's hash term carries `c'` (the digests in one challenge input plus `n_J + 1`,
`2^11.2` here), not the book's 3.5; (ii) "once for the tree" assumes the collision event is shared by every proof of
the tree, a statement no lemma of ours or of [SG26] makes; under the theorem as stated the term is per proof, `N` times
(`2^14.3`). Together `log2(N c') = 25.52` bits on `2 kappa`; net of the book's `log2 3.5 = 1.81` the change is 23.71 bits
on `2 kappa` and **11.86 bits on `kappa`** (126.60 - 114.74; corrected in revision 10.1, finding R10-5). Revision 9 carried the book's figure next to
[SG26]'s IOP term; revision 10 replaces it.

### 7.3 The plain answer: category 1 for A and for B

**The definition.** [CFP] Section 4.A.5, page 16, item 1 (Published): "Any attack that breaks the relevant security
definition must require computational resources comparable to or greater than those required for key search on a
block cipher with a 128-bit key (e.g. AES128)"; page 17: "In order for a cryptosystem to satisfy one of the above
security requirements, any attack must require computational resources comparable to or greater than the stated
threshold, with respect to all metrics that NIST deems to be potentially relevant to practical security"; page 18:
"Submitted parameter sets meeting the requirements of a higher category will be automatically considered to meet the
requirements of all lower categories". It is an **attack-cost** definition. The project turns it into conditions C,
Q, G, H (`decision-security-category.md` 1.2, table "C: proven classical bits of the tree ... 128; Q: proven QROM bits
... 64; H: digest bits, attack rule 256 (collision `2^128`: the category 2 benchmark); H: proven rule 264"), and its
recorded basis for the hash part is the attack rule: `soundness-method.md` 8.5b, "With `lambda = 256` the proven
classical level is ... 126.6 bits ...; category 1 then rests on condition H's attack rule", and
`decision-security-category.md` 3.5, "Recommendation: keep the attack rule (as at category 1), state it as the basis".

**What "proven" rests on (finding R10-2).** Every figure of this section called proven is proven in the random-oracle
model under: the modelling assumptions MA-1 and MA-2' (the transcript hashes, and B's BLAKE3 `derive_key` leaves and
nodes, as one random oracle with four disjoint parts); the recursion heuristic C2 (an in-circuit verifier treated as the
native verifier against the oracle; no random-oracle proof covers it); the open obligations K-A and K-B (round-by-round
**knowledge** soundness of both IOPs outside the openings, `qrom-compilation.md` H3, T-5); Theorem D of
`lemma-d-duplicate-openings.md` (B's repeated openings; refereed, pass with conditions); [SG26] Theorem 6.6 (2), a
preprint; the tree reduction by extraction, `docs/lemma-tree-extraction.md` Theorem TE (ROM, proved there, a draft until
refereed; its QROM form TE-Q is argued with one step from memory); and `c'`, `k_q` as estimates (E) until task T-1.
Candidate rows rest in addition on DKT26 (a preprint). The figures are for one output tree (`attempts = 1`; R10-10: an
adversary submitting many trees is covered by the same `t` only through the theorem's single-output definition; a
per-output union is not in the figures). The calculator prints the same list under every table (revision 10.1).

*Amendment 2 (2026-11-19, revision 10.2):* the list above is corrected in two items. "Theorem TE (ROM, proved there,
a draft until refereed)" was not a theorem of the ROM as worded: its hypothesis H-C2 is false in the ROM (referee F-1).
It is replaced by Theorem TE' (revision 2 of that document), a true theorem of the ROM with the same bound, which leaves
C2 as the named event "accepted in-circuit, rejected natively". "TE-Q argued with one step from memory" is replaced by
Proposition TE-Q' with Lemma QC (the referee's proof from [CMS19] Lemma 3.2; unrefereed). And: every **tree** figure of
this section rests on C2, which no random-oracle proof can remove, so "proven" for a tree figure means "derived under C2
and the conditions above". The footer of every table (revision 10.2) lists the conditions one by one.

**Quantum measure: both systems meet it, proven (under the assumptions above).** The tree's QROM bound, the theorem's own QROM form with every term,
stays below 1/2 up to `2^69.58` (A) and `2^70.45` (B) quantum queries against `2^64`: margins +5.58 and +6.45 bits.
The hash part alone reaches 75.63 (+11.63). Condition Q needs nothing new. *Amendment 2 (2026-11-19, revision 10.2): "proven" in this heading is withdrawn for the tree: the tree's QROM figures are **derived under the recursion heuristic C2** and conditional on K-A, K-B, T-1, [SG26] Theorem I.16 (1) (a preprint) and Lemma QC (unrefereed); no unconditional QROM figure exists for a tree whose inner proofs are witnesses. The project claims 69.58 / 70.45; the one-table form of Proposition TE-Q' (76.72 / 77.60, hash part 80.40) is printed beside them. The per-proof QROM figures are proven given [SG26] Theorem I.16 (1), K-A, K-B and T-1.*

**Classical measure, as a proven bound: neither system meets it.** With the hash term counted, the tree's proven
classical level is **114.74 bits for A and for B** (A's nodes 114.81), against 128: **a shortfall of 13.26 bits**
(13.18 at A's nodes), at the estimated `c'`. The documents said 126.6 (a shortfall of 1.4); that figure is withdrawn.
Under Lemma TE (`docs/lemma-tree-extraction.md`, a draft) the hash part is taken once for the tree and the level would be
121.89 (6.11 short); the calculator keeps 114.74 until that lemma is refereed. *Amendment 2 (2026-11-19, revision 10.2): the lemma was refereed (pass with conditions) and restated as Theorem TE'; the calculator now prints 121.89 as the tree's classical hash level "under C2, K-A, K-B, T-1", with 114.74 beside it; both are conditional figures, neither is an unconditional theorem.* The IOP half meets
128 at every row (the margins of the row tables), so the shortfall is entirely the hash part.

**Classical measure, as the project's requirement is recorded (C proven for the IOP term, H's attack rule for the
hash part): both systems meet it**, with **0 bits of margin in the digest length** (256 = 2 x 128): a generic
collision on a 256-bit transcript digest (Keccak-256 in A; SHA-256 keys and BLAKE3 `derive_key` leaves and nodes in
B, whose collision resistance at `2^128` rests on the evidence of `decision-b-merkle-hash.md` (MA-2'), a primitive NIST's
benchmark does not name; finding R10-3) costs about `2^128` hash calls, NIST's category-2 benchmark (`2^146` classical gates
against category 1's `2^143`, [CFP] page 18), and a category-2 parameter meets category 1 (page 18). The `N c'`
factor of the bound is an artifact of the proof (a union over proofs and over the digests of a challenge input); a
generic collision search does not get cheaper with it, and inverting one of `N c'` digests costs about `2^230.6`
calls (standard generic reasoning, an attack estimate, not a theorem). **The documented figure is fixed accordingly**:
"proven classical 126.6" becomes "proven classical 114.74 (A, B); category 1 on condition H's attack rule".

The calculator states which basis it applies: `Profile.hash_basis` (default `attack-rule`, the recorded basis) prints
"certified (every t; classical hash part on condition H's attack rule)"; `--hash-basis proven` requires the proven
classical level and certifies no 256-bit row (`soundness/output/revision10-proven-basis-tables.txt`). Revision 10.1
(finding R10-1): this is now true of every table, system B's Johnson-terms table (`dkt26.Row8`) included, whose rows
carry the profile's hash basis and are judged by the same function as every other row (`category.certification_checks`);
every positive label names its basis; `tests/test_revision10_1.py` checks, over every row type, every category, both
conventions and both bases, and over every CLI output, that no row failing a check prints "certified".

### 7.4 Findings and options for the lead architect (nothing is changed)

If the lead architect wants category 1 to be a **proven** classical statement for the whole bound, the options are:

| Option | What changes | Proven classical tree level | Cost (E, size model of the calculator) |
|---|---|---|---|
| (a) Keep the attack-rule basis and say so | the wording only (done in revision 10) | 114.74 | none; every claim of "proven 128 classical bits" must read "proven for the IOP term; hash part on condition H" |
| (b) Wider digest, every part (keys, leaves, nodes, write-back): 36 bytes | A: Keccak-256 has no 36-byte output; SHAKE256 (or Keccak[c=512]) at 36 bytes for keys, leaves and nodes: an 88-byte node input (tag 16 + 2 x 36) stays one Keccak-f, so no permutation is added. B: SHA-256 keys become a truncated SHA-384 / SHA-512 or SHAKE256 at 36 bytes; BLAKE3 leaves and nodes at 36 bytes of XOF output: a 72-byte node input is two BLAKE3 compressions in place of one, so B's Merkle hashing in circuit about doubles at the node | 130.74 (at 288 bits, the least whole-byte digest; 280 bits gives 126.74) | proof bytes: B leaf 658,134 -> 691,895 (+5.1 %), B node `2^27` 737,947 -> 779,400 (+5.6 %); A row 8 leaf 697,939 -> 722,891 (+3.6 %), A node `2^27` 904,856 -> 955,205 (+5.6 %), `2^30` 1,085,873 -> 1,153,110 (+6.2 %); every transcript, every specification digest of the proof layer, both guests and B's slot fits change; no query count changes (the need does not depend on `b`) |
| (c) Per-tree accounting (a new lemma: one collision event of the shared oracle covers every proof of the tree) | Lemma TE (`docs/lemma-tree-extraction.md`, Original, proved there in the ROM, a draft until refereed); the term becomes `c'_max (t + K)^2 / 2^(8b)`, `K <= N k_q` | 121.9 at 256 bits (still 6.1 short); with (b) at **272 bits (34 bytes)** it reaches 128 | the lemma and its referee; with (b) at 34 bytes, about half of (b)'s byte cost |
| (d) A tighter cited bound | a published bound without `c'` | 127.5 at 256 bits for a bound `t^2 / 2^256` taken once a tree (120.36 with the tree sum kept); a bound at the birthday probability itself, `t^2 / 2^257`, gives exactly 128.0 in this convention, and since a collision alone does not forge (`rev10-referee.md` section 4) nothing rules out a proof with no collision term: the cap is a property of the bounds in hand, not of the protocol (corrected in revision 10.1, R10-4) | none in bytes, but it cannot reach 128 at 256 bits alone; combined with (c) it would need 264 bits |
| (e) Fewer proofs a tree | `MAX_TREE_PROOFS` | 0.5 bit for each halving; 121.9 at `N = 1` | cannot reach 128 alone; costs block capacity |

So, **with the published bounds and the lemmas considered here, only a wider digest reaches a proven classical 128**:
288 bits under the theorem as stated, 272 with a per-tree lemma (Lemma TE, if refereed), 264 with a per-tree lemma and
a bound without `c'`. The quantum measure needs none of these.

*Amendment 2 (2026-11-19, revision 10.2):* in row (c) above, "proved there in the ROM, a draft until refereed" is corrected: the per-tree lemma is Theorem TE' (`lemma-tree-extraction.md` revision 2), a theorem of the ROM up to the named event C2-VIOLATION, so the level it gives (121.9 at 256 bits; 128 at 272 bits) is conditional on C2, K-A, K-B and T-1 and is not a proven classical 128 in the unconditional sense; the same holds for every row of this table, since every tree figure rests on C2.

### 7.5 `k_q` as an input with provenance; the guard (finding R9-4)

`k_q` now sets certified counts, and system A's margins are as small as 0.0011 bit. Revision 10 makes `k_q` an input
(`hashterm.KqInput`: value, provenance `estimated` or `transcript-reported`, source), prints it with its provenance
and the margin on every row, and **refuses the label "certified" to a row whose `k_q` is estimated and whose margin is
below the guard**

    guard(k_q) = log2(1 + 1.1 k_q) - log2(1 + k_q)   (0.1375 bits at every category-1 row),

the need's rise if `k_q` is 10 % higher than estimated. Why 10 % (a stated allowance, not a bound): the estimated
parts of A's `k_q` are `N_msg = 2 (listed rounds + OTHER_ROUNDS)` with `OTHER_ROUNDS = 512` and one prover message a
round (E); doubling `OTHER_ROUNDS` adds 2,048 (+4.5 % at `k_q` = 45,658, +15 % at 13,456), and one more Merkle level
at every opened position adds `q_IOP` (+3 % to +4 %); 10 % covers either error alone at most rows. A reported `k_q`
replaces the estimate and the guard is 0.

**Revision 10.1 (finding R10-7): the guard covered ONE named error at a time.** 10 % does not cover the two named errors
together, and not even `OTHER_ROUNDS` doubled alone at the smallest rows (+15.2 % at `k_q` = 13,456; +11.3 %, +11.6 %,
+12.3 % at row 6 mode 0, row 8 mode 1 at 1/4, row 7 at 1/4). A combined guard costs nothing to compute, so it is now
implemented: the guard is the **larger** of the 10 % allowance and the two named errors together,

    guard(k_q) = max( log2(1 + 1.1 k_q) - log2(1 + k_q),  log2(1 + k_q + named) - log2(1 + k_q) ),

`named = 4 OTHER_ROUNDS + q_IOP` in system A (2,048 + the row's opened positions) and `named = q_IOP` (padded slots
included) in system B, whose message count is its row budget, already an upper figure (`hashterm.kq_guard_bits`,
`KqInput.named_extra`). At A's rows the named-errors term is 0.111 to 0.255 bits and the guard 0.1375 to 0.255; at B's rows the 10 % allowance is the larger (one more
Merkle level is +2.6 % to +2.9 %). **One row moves: A row 7 at rate 1/4 loses "certified"** (margin 0.192 against
0.222). Every other row keeps its revision-10 status. What supports a small allowance, and was not said: the Merkle
part of the estimate charges every opened position a full path of `1 + floor(log2(2 l_max))` queries at the longest
oracle of the proof, an over-count for every shorter oracle and every path that shares upper levels; the built count is
expected below the estimate there. It remains an allowance, not a bound, until T-1 reports. Options considered: no guard (rejected: a 0.1 % error breaks A's `2^24`
node); a fixed allowance in A's solve (rejected: it changes counts before T-1 says they are wrong); the guard on the
label (adopted as a proposal for the lead).

**Rows that lose "certified" under the guard (category 1):** system A row 6 mode 1 (`2^20`, 1/4; +0.0289), row 8 mode
0 at 1/4 (+0.1058) and at 1/2 (+0.0186), row 8 mode 1 at 1/2 (+0.0186), row 9 at rate 1/2 for `2^24`, `2^26`, `2^27`,
`2^28`, `2^29`, `2^30` (+0.0011, +0.0989, +0.0979, +0.0456, +0.0575, +0.0043), row 9 at rate 1/4 for `2^24`, `2^25`,
`2^28`, `2^30` (+0.0571, +0.0016, +0.1109, +0.0033), and row 7 at rate 1/2 (+0.0081): **14 of A's 20 rows and row 7
at 1/2**; since revision 10.1 also **row 7 at 1/4** (+0.192 against the combined guard 0.222). They read "meets on an estimated k_q ... not certified until task T-1 reports k_q". Certified: A row 6 mode
0, row 8 mode 1 at 1/4, row 9 `2^25` at 1/2, `2^26`, `2^27`, `2^29` at 1/4, and **every B row** (margins
+0.28 to +0.78); row 7 at 1/4 was certified in revision 10 and is not in revision 10.1. No count changes.

### 7.6 Task T-1 (for both builder teams: `yugen-proof-a`, `yugen-proof-b2`)

**What each built verifier must report, per proof shape and per query count it is built at** (leaf and node, every
rate and stack the calculator certifies; the native verifier and the in-circuit verifier that checks that shape as a
child, each separately):

1. **The quantities of [SG26] Definition I.1**, from the verifier's code path: `|J_V|` (verifier messages) and
   `|J_P|` (prover messages) separately, so `N_msg = |J_V| + |J_P|`; `m` (most oracle strings in one prover
   message); `n_B` and `n_J` (0 without merges); `q_IOP` = **opening records checked**, summed over every oracle of the
   proof, counting padded group slots and duplicate records (Lemma D, D-4); `l_max` = the largest leaf count of any
   oracle's Merkle tree; per oracle its leaf count and cap height; the digest length in bytes of each part (key,
   leaf, node, write-back).
2. **The hash queries the verifier makes on one proof, by kind**, where one query is one evaluation of one domain part
   of the oracle on a whole input (one Keccak-256, SHA-256, SHAKE256 stream point or BLAKE3 `derive_key` call,
   however many permutations or compressions it takes): (a) challenge-input (key) queries, (b) stream queries,
   (c) final-digest queries of merges, (d) leaf queries, (e) internal-node queries including the cap's path to the
   root; each as the **maximum over every proof the verifier accepts for that shape** (from the code path, not one
   sample).
3. **The derived `k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2 max(1, l_max))))` and `c = N_msg max(1, m)`**, with
   tests that assert, on a recorded proof, that the counted calls equal (2) and that (a) + (b) + (c) `<= 2 N_msg + n_B`
   and (d) + (e) `<= q_IOP (1 + floor(log2(2 max(1, l_max))))` (the theorem's hypothesis "the verifier makes at most
   `k_q` hash queries").
4. **Where:** a table in the builder's `docs/parameters.md` and one machine-readable line per shape and count
   (system, shape, stack, rate, query counts, group unit, the numbers of 1 to 3, the commit), which the calculator
   enters in `hashterm.REPORTED_KQ` with provenance `transcript-reported`.

**Acceptance:** for every certified row the calculator's `k_q` is at least the reported one, or the row is re-solved
at the reported `k_q` and any count that moves is reported to the lead; the larger of the native and in-circuit
figures is used; a reported row carries no guard. Until then the rows of 7.5 stay uncertified.

**Additions (revision 10.1, findings R10-9 and R10-6, and hypothesis H-DS of `docs/lemma-tree-extraction.md`).** Items 1
to 4 and the acceptance above are unchanged, so work already started stays valid. Each built verifier reports in
addition, per proof shape and query count, native and in-circuit separately, in the same table and machine-readable line
as item 4:

5. **(Addition) Stream lengths.** For every verifier message `i`: the number of stream bytes the verifier reads
   (`b + e_i`), and the shortest and the longest over the proof. The shortest is the theorem's `b + e` ([SG26] page 59:
   "A longer stream only lowers these terms, so the theorems hold as stated"); the calculator evaluates the stream term
   `2 sqrt(k_q / 2^(8(b+e)))` at it (until reported, at `b + e = b = 32`, `e = 0`, an upper bound on the term).
6. **(Addition) Hash calls outside the four parts.** Every hash evaluation the native verifier, and the in-circuit
   verifier with its host circuit, makes that is not a challenge-input, stream, leaf or node query of the transcript:
   statement digests, verifying-key and constraint-system digests, list digests, the bound IV, public-input hashing,
   and any other. For each: the function, the number of evaluations per proof, its input format, and the domain
   separation that keeps its inputs disjoint from the four parts (the tag or prefix, and why no input of it can equal
   an input of a part).
7. **(Addition) Per message `m_i` and the items of each challenge input.** For every prover message `i`: the number of
   oracle strings it commits (`m_i`), and exactly what it contributes to the next challenge input (the roots only, or
   which further digests: any Merkle cap entry absorbed as an item counts as a digest in `c`). From these, `N_msg`, `m =
   max_i m_i`, `n_J` and `c = N_msg max(1, m)`, so that `c'` is reported with `k_q` (the line's `n_msg`, `m`, `n_j`
   fields; the calculator then prints `c'` as reported in place of `(E)`).
8. **(Addition) No truncated comparison.** A statement, with the code location of every digest comparison in the native
   and the in-circuit verifier (challenge-input keys, leaf and node digests, the written-back digest, root and cap
   checks), that none of them compares fewer than 32 bytes (`b = 32` for every part, 7.1).
9. **(Addition) Sampler evidence.** For every sampler: its challenge set and the number of stream bytes it reads, and
   either the argument that it never rejects (a challenge set of size a power of two read from whole bytes, so
   `eps_ov = 0`) with a test that asserts it on the code path, or its rejection probability if it can reject.
10. **(Addition) Distinct systems on one oracle.** For every proof system whose proofs meet in one tree (A: the leaves of
   rows 6, 8 and 7 and the nodes of row 9; B: the leaf and the node), the protocol label and the statement encoding of
   its challenge inputs, showing that challenge inputs of different systems are distinct and that each statement names
   its circuit (hypothesis H-DS of `lemma-tree-extraction.md`).

**Acceptance of the additions:** the calculator enters a line as `hashterm.KqReport(k_q, queries, source, n_msg, m,
n_j)` keyed by shape (`a_report_key`, `b_report_key`); it refuses a line whose `k_q` is below the shape's floor `4 x`
listed rounds `+ 2 x` drawn positions, or whose `N_msg` is below `2 x` listed rounds (finding R10-8); a reported `k_q`
above the estimate re-solves the row and prints the new count; `c'` is compared and replaced as `k_q` is; the stream
term is printed at the reported shortest stream; items 6, 8, 9 and 10 are checked by the maths team against
`qrom-compilation.md` 2 and `lemma-tree-extraction.md`, and any item that fails is a finding to the lead.

### 7.7 Padded group slots (Lemma D referee, m-1)

System B's in-circuit verifier checks queries in groups of `unit` and repeats the last index in unused places, so it
checks `ceil(q / unit) x unit` records a tree. `category.b_counts` now counts them (units at `yugen-proof-b2`
`0f84f74` `docs/parameters.md` 15.5: 2 at 192, 5 at 235 and 111, 4 at 82; 6 assumed where none is recorded). `k_q`
rises at 111 (24,378 -> 25,170), 82 (19,128 -> 19,536), 171 (35,232 -> 35,808), 385 (74,010 -> 74,940) and the built
226 (45,792 -> 46,560); margins 111 +0.78, 82 +0.69, 171 +0.55, 385 +0.31. **No count moves.**

### 7.8 What would reverse or change this amendment

- A refereed per-tree lemma (7.4 (c)) or a published bound without `c'`: the proven classical level and the digest of
  7.4 change; the attack-rule basis does not.
- The lead architect choosing the proven basis for the hash part: a digest change (7.4 (b)) becomes a requirement.
- T-1's reports: the guard falls away row by row; a reported `k_q` above the estimate re-solves the row.
- A transcript with digest parts of unequal length: `b` must be re-read (7.1).
- A referee's report on `docs/lemma-tree-extraction.md`: if Theorem TE passes, the classical hash part of the tree is
  taken once (121.89 at 256 bits; option (c) of 7.4 at 272 bits reaches 128); if it fails, the tree claim needs another
  reduction, and the black-box one moves every need (+2.3 to +3.9 bits a round; that document, section 8).
  *Amendment 2 (2026-11-19):* the referee's report passed it with conditions; revision 2 applies them (Theorem TE'), and the calculator takes the hash part once (121.89), conditional on C2, K-A, K-B, T-1 (7.11).

### 7.9 Provenance

**Published:** [SG26] Theorem 6.6 (2) and its preamble, Section 6.3 (page 58), Definition I.1 (page 130), Section I.1
(page 131), all read from rendered pages for this amendment; [CFP] Section 4.A.5 pages 16 to 18 (quoted). **Original
(the Ycash developers, 2026), unreviewed:** the per-row evaluation and the tree sum of the hash term, the classical
level in the every-t convention and the digest rule (`REFERENCES.md` O-75); the `k_q` input, its guard and task T-1's
text (O-76); the padded-slot count (O-77; the finding is the Lemma D referee's); the options of 7.4 (the per-tree
lemma of (c) is Lemma TE, `docs/lemma-tree-extraction.md`, Original, a draft until refereed, O-78). Revision 10.1:
the shared certification function, the combined guard, the reported-input floors and re-solve, `c'` with provenance and
the additions to T-1 are Original (the Ycash developers, 2026), unreviewed (O-79).

### 7.10 Revision 10.1: what changed (after `docs/rev10-referee.md`)

| Finding | Change | Figure that moved |
|---|---|---|
| R10-1 (MAJOR) | one certification function for every row type (`category.certification_checks`); `dkt26.Row8` carries the hash basis, its label names it; `--rev8 --hash-basis`; test over every row type, category, convention, basis and CLI output | none; system B's two unique-decoding rows of the Johnson-terms table now read "not certified: fails classical hash part (proven)" under `--hash-basis proven` |
| R10-2 (MAJOR) | 7.3 and the calculator's footer list what "proven" rests on; `docs/lemma-tree-extraction.md` (Theorem TE, ROM, full proof; TE-Q argued) | none in the calculator; under Theorem TE (draft) the hash part of the tree would be 121.89, not 114.74 |
| R10-3 | 7.3 names BLAKE3 | none |
| R10-4 | 7.4 (b) 130.74; (d)'s reason and the closing sentence softened | 128.0 -> 130.74 (a cell) |
| R10-5 | 7.2: 25.52 / 23.71 / 11.86 | 12.7 -> 11.86 (a sentence) |
| R10-6 | `c'` printed with `(E)`; a reported `c'` from the T-1 line; 7.2 states 114.7 at the estimated `c'` | none |
| R10-7 | guard = max(10 %, both named errors together) | A row 7 at 1/4 loses "certified" |
| R10-8 | reports keyed by shape, checked against the shape's floor, re-solve above the estimate; `dkt26.Row8` reads them | none (no report exists) |
| R10-9 | stream term at the shortest stream (`b + e = 32` until reported); T-1 items 5 to 10 added | printed stream term -4,765 / -2,953 -> -105 (A, B) |
| R10-10, R10-11 | one-tree statement in 7.3 and the footer; summaries' headings under the proven basis | none |


### 7.11 Amendment 2, revision 10.2: what changed (after `docs/tree-extraction-referee.md`)

| Finding | Change | Figure that moved |
|---|---|---|
| F-1 (MAJOR), C-1 | Theorem TE restated as Theorem TE' (ROM, true as stated); C2 the named event C2-VIOLATION, entering at two places; what is unconditional (the root; a tree whose every proof is published) and what is conditional (every recursion-tree figure) stated | none in the counts; wording here (7.3, 7.4, 7.8 amended in place with dated notes) |
| F-2 (MINOR), C-2 | Lemma TE.1 two-sided; "in `B*` at some step" | none: the bound is unchanged |
| F-3, C-3 | every tree figure labelled "under C2, K-A, K-B, T-1" in the calculator and here | none |
| F-4, C-5 | `E_T` stops at a rejecting child | none |
| F-7 (MAJOR), C-6 | Lemma QC written into `lemma-tree-extraction.md` section 9a (Original, found in referee review, unrefereed); the corrected `E_T^Q`; the added term `10 (K - k_q,r) / 2^(8(b+e))` printed in bits | the term: -222.91 (A), -223.09 (B) |
| Task D | calculator revision 10.2: the classical tree hash level printed as that of Theorem TE' with the per-proof union beside it; the tree's QROM per-proof union (claimed) with the one-table form beside it; the footer lists every condition with its status | printed classical tree level 114.74 -> **121.89** (114.74 beside it); QROM 69.58 / 70.45 unchanged and claimed, 76.72 / 77.60 printed beside them; **no query count and no row status changes** (`soundness/tests/test_revision10_2.py`) |

Provenance: the restatement, the explicit-tree corollary and Lemma QC are Original (the Ycash developers, 2026), found
in referee review (`REFERENCES.md` O-80, O-81); unrefereed in their revision-2 form.