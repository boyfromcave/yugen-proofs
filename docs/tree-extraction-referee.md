# Referee report: `lemma-tree-extraction.md` (Theorem TE, Proposition TE-Q)

Part of Yugen. `yugen-proofs` at `2a00109`. 2026-11-19. Independent referee; subject: revision 1 of
`docs/lemma-tree-extraction.md` (Original, unrefereed) and the tree figures that rest on it.

**Sources, as read for this report** (page images rendered with pypdfium2, scale 1.6; printed page numbers):

- [SG26] C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, ePrint
  2026/2615 (preprint): pages 137 to 144 (Protocol I.9, Lemmas I.10, I.11, I.12 with proof, Definition I.13, Lemma
  I.14 with proof, Lemma I.15, Theorem I.16 with proof, Theorem I.17 statement).
- [CMS19] A. Chiesa, P. Manohar, N. Spooner, *Succinct Arguments in the Quantum Random Oracle Model*, ePrint
  2019/834: pages 16, 17 (Sections 3.5, 3.6, Lemma 3.2, Lemma 3.3), 20 (Definitions 4.6 to 4.8, Lemma 4.9), 22
  (Definition 5.6, Lemma 5.7, Lemmas 5.9, 5.10 statements, footnote 6).
- The impossibility and heuristic status of recursion in the random-oracle model (section 1.1) is cited **from memory
  only** (Chiesa, Ojha, Spooner, *Fractal*; Chiesa, Liu, on relativized probabilistic proofs; Chen, Chiesa, Spooner, on
  SNARGs in relativized worlds; Hall-Andersen, Nielsen, on IVC in the ROM). None was consulted; none is in the folder
  as far as checked by file name.

## 0. Verdicts

| Subject | Verdict |
|---|---|
| Classical Theorem TE | **PASS WITH CONDITIONS** (C-1 to C-5). The bound and the one-table composition are right; the statement is not a theorem of the ROM as worded (F-1), and one proof step is false as written but repairable with no change to the bound (F-2). |
| Quantum claim (Proposition TE-Q) | **PASS WITH CONDITIONS** (C-1 to C-7). The "step from memory" is false as worded and true in a corrected form, proved in section 3 from [CMS19] Lemma 3.2. The proof in section 3 is itself unrefereed. |
| Black-box figures (+2.3 to +3.9, +14.29) | Arithmetic confirmed; the black-box route is not needed. |
| Calculator at 121.89 | May move after C-1, C-2 are applied to the lemma document, with the label of D below. |

**No query count must change.** Nothing found here raises a per-round need.

**What may honestly be said today.**

- (i) Classical: "Under the recursion heuristic C2, round-by-round knowledge soundness of every round (K-A, K-B, owed)
  and the transcript checks of T-1, an accepted root of a 20,000-proof tree is unsound with probability at most
  `t eps_max + sum |J_V| eps_v + c'(t + K)^2 / 2^256` (IOP part 128 bits; hash part 121.89 proven, 128 on the attack
  rule); without C2 the theorem covers the root proof, or a tree whose every proof is published, and nothing below."
- (ii) Quantum: "Under the same conditions, [SG26] Theorem I.16 (1) and the continuation lemma of this report, the
  tree's QROM level is at least 69.58 / 70.45 bits (76.7 / 77.6 in the one-table form) against 64; this is a derived
  figure conditional on C2, not an unconditional QROM theorem, and no unconditional QROM figure exists for a tree
  whose inner proofs are witnesses."

## 1. Classical Theorem TE (task A)

### 1.1 F-1 (MAJOR): H-C2 is false in the model, so TE as stated is vacuous; C2 enters at two points, not one

`R_sigma` is fixed and evaluates the concrete hash `h` in the circuit; the native verifier queries the oracle `H`.
H-C2 says every witness's child proofs are accepted **against `H`**. In the ROM this is false with probability
essentially 1: take an honest tree whose inner proofs are made with `h` and whose root is made with `H`. The root is
accepted, `E_T` extracts `w_r`, the child verifier run against `H` rejects (its challenges are fresh), the database
algorithm finds no challenge input for `x_c`, and `E_T` records FAIL with probability 1. So in the ROM the conclusion
of TE is false without H-C2 and the theorem is vacuous with it (a false hypothesis). The document says H-C2 "cannot
hold as mathematics"; it must then not say "Proved here, with a full proof" of a ROM theorem.

The two ways to make the model consistent both fail, and this is the standard gap (from memory, see sources):
(a) fixed relation with `h`: H-C2 false, as above; (b) oracle relation `R^H` (hash gates are oracle gates): H-C2 holds
by definition, but then no IOP for `R^H` exists for a random `H`, hypothesis (K) is unavailable, and Lemma TE.1's
independence of `theta_i` from the relation fails (the document's own remark after TE.1). So C2 is used twice: for the
child's acceptance (section 6 step (1)) **and** for keeping (K) and TE.1 on a relation that does not read `H`. Section
10 item 1 ("at one point only") is to be corrected.

**Fix (buildable, C-1).** State what is actually proved, which is a true theorem of the ROM:

> **Theorem TE'** (ROM; under (K), H-DS). Let `E_T` be as in section 3, stopping with the outcome **C2-VIOLATION at
> `c`** when a child verifier it runs rejects. For every `(t, 0)`-adversary, the probability that the root is accepted
> and `E_T` ends with neither a compliant tree of witnesses nor a C2-VIOLATION is at most
> `t eps_max + sum_v |J_V,v| eps_v + c'_max (t + K)^2 / 2^(8b)`.

Its proof is sections 4 to 6 with "by H-C2" deleted and F-2 repaired. C2 is then one named event, "a proof accepted by
the in-circuit verifier (concrete hash) is rejected by the native verifier", outside the theorem. In the deployed
system both verifiers compute the same function, so the event is excluded by in-circuit / native verifier equivalence
(a testable engineering property); the heuristic is the usual one, that a bound proved for a random `H` describes the
concrete hash, here applied to a statement that itself contains the hash. TE is **conditional on C2 in this form**,
and no proof in the ROM can remove it.

**What is unconditional.** If every proof of the tree is published and verified natively, TE' needs no C2: the same
table, the same bound, `t` shared. This "explicit tree" theorem is the rigorous core.

### 1.2 Answers to the questions put

- *Is `E_T` well defined; where do child proofs come from.* Yes: from the witness the database algorithm extracts for
  the parent ([SG26] Protocol I.9 step 6), a deterministic function of the table. The extracted witness satisfies the
  fixed node relation, so the **in-circuit** verifier accepts the child; that the **native** verifier does is C2.
  "Running the child verifier" is a native run against the lazily sampled oracle, recorded in the shared table.
- *Does the in-circuit verifier query the same oracle.* No. It computes the hash as constraints. Nothing in TE models
  an oracle queried inside a circuit; this is exactly C2 (1.1).
- *Depth, fan-in.* The bound depends on them only through `N` and `K`. Termination needs the level (or remaining
  depth) bound in each statement so that an extracted node cannot list a child of its own level (C-4; not checked in
  the circuits).
- *Two systems, one oracle.* H-DS is needed and sufficient for TE.1 as adapted: one recorded challenge input must
  decode to one system. Modelling distinct concrete hash functions as disjoint parts of one oracle is sound (it only
  adds cross-function collisions to the bad set). Whether the transcripts give injective cross-system encodings is
  T-1 item 10: **not checked here**.
- *Is `t` shared.* Yes, correctly. Each of the adversary's entries fixes at most one challenge of one statement of one
  system (TE.1, by the write-back as in [SG26] Lemma I.12), so the IOP part is `t eps_max`, not `N t eps`. This is the
  adaptive-statement property [SG26] Theorem I.16 already has, extended to many statements.
- *Each term.* `t eps_max`: right. `sum_v |J_V,v| eps_v`: right, only a stream query fixes a challenge, a sharpening
  of [SG26]'s `k_q eps`; it relies on [SG26] Definition I.1's count of stream queries, **not re-read**, and on the
  count for system B's `V'`. `c'_max (t + K)^2 / 2^(8b)`: right, at most `T` entries each with `Pr[F] <= c'_max T /
  2^(8b)`.

### 1.3 F-2 (MINOR, proof step false as written): `B*` is not monotone

Lemma TE.1 claims monotonicity because "a reconstructed transcript can be changed by a later entry only through a
second preimage". Protocol I.9 step 6 (page 138): "A missing or ambiguous preimage leaves the leaf undefined, and it
decodes to the default." A later entry that supplies a **missing first** preimage of a digest carried by a recorded
input changes a reconstructed transcript without any collision, and the knowledge failure may disappear. Section 6
uses monotonicity twice. **Fix:** state TE.1 as [SG26] states I.12, as the two-sided instability (outside `F`
membership does not change except by the one new knowledge failure; the event above lies in `F`), and replace
"the final table is in `B*`" by "the table is in `B*` at some step": `Pr[exists j: db_j in B*] <= sum_j Pr[db_(j-1)
not in B*, db_j in B*]`, the same sum. The bound is unchanged. The two-sided form is also what Lemma I.15 (2) needs in
the QROM ([CMS19] Definition 5.6).

### 1.4 Other findings

- **F-3 (MAJOR, known, open): (K) is owed.** Extraction needs round-by-round **knowledge** soundness of every round of
  both systems; soundness errors do not suffice for a tree whose inner proofs are witnesses. K-A and K-B are open
  obligations; until discharged every tree figure is conditional on them (C-3).
- **F-4 (MINOR):** `E_T` step 3 does not test the child verifier's verdict; add the stop of TE' (C-5).
- **F-5 (NOTE):** Corollary TE-F (a) checked: at `t = 1` it needs `N (1 + k_min) >= 1 + k_max`, true; for larger `t`
  the left side grows with slope below 1. Corollary TE-F (b): `(255 - log2 c'_max) / 2` = 121.886 (2,397), 121.885
  (2,401); per-proof sum `(255 - log2(N c')) / 2` = 114.741. Reproduced by hand.
- **F-6 (NOTE):** TE-S needs H-BIND and the statement-digest modelling (MA-1); not examined.

## 2. Black-box composition (task C)

Corollary TE-bb's reduction is valid classically (the ancestors' database algorithms make no oracle queries). Checked:
`log2(1 + N k / (1 + k))` = 14.288 at `k` = 74,940; `log2 5` = 2.32 for a leaf under four ancestors of equal `k_q`
(system B, rate 1/8). The figures 2.40 and 3.29 to 3.87 are consistent with the stated `k_q` range (13,456 to 74,940)
but were **not recomputed row by row**. The black-box form is not needed: TE' holds with the one-table bound, so the
per-round need stays `kappa_C + 1 + log2 N + log2(1 + k_q)` and **no query count moves**. I agree the black-box route
does not exist in the QROM. If C2 were instead taken in the standard-model form (the concrete-hash argument is a
knowledge-sound SNARK, composed level by level), the black-box cost, with extractor running time in place of query
counts, would return; the project's recorded C2 is the oracle form, and this report keeps it.

## 3. Quantum (task B)

### 3.1 What a QROM version needs

(a) the pre-measurement part exactly as [SG26] Theorem I.16 (1) for `A` followed by the root verifier (compressed
oracle, Lemmas I.10, I.11, one database measurement, Lemma I.15 with `B*`); (b) the two-sided instability of `B*`
(F-2); (c) a statement of how the compressed oracle answers the extractor's **classical** queries after the database
has been measured; (d) the classical per-entry argument for those queries; (e) C2 as in TE'. No joint measurement and
no commutation argument is needed: after the one measurement everything `E_T^Q` does is classical, and its queries act
on the oracle register only, so `A`'s output and register `Z` are untouched (Lemma I.11).

### 3.2 F-7 (MAJOR, closed here): the step from memory

Step (ii) as written ("one inside returns the recorded answer", "is recorded") is **false exactly** and true up to
`O(2^-n)` per query, `n = 8(b + e)` the oracle's output bits. Proof from [CMS19] Lemma 3.2 (page 17; Published,
attributed there to Zhandry and proved in their Appendix A, not re-read):

**Lemma QC (continuation after a database measurement).** *Provenance: Original as far as checked (the Ycash
developers, 2026; sources consulted: [CMS19] Sections 3.5, 3.6, 4; [SG26] Appendix I), derived from [CMS19] Lemma
3.2.* Let the database register be in a basis state `|D>` with `|D|` below the capacity. A classical query on `x`
(phase register `H^n|0>`, compressed phase oracle, `H^n`, measure) satisfies:

1. if `D(x) = ⊥`: the answer `y` is **exactly** uniform and independent of every other register; measuring the
   database afterwards gives `D + [x -> y]` with probability `(1 - 2^-n)^2`;
2. if `D(x) = y_0`: with probability at least `1 - 10 / 2^n` the answer is `y_0` and the database is unchanged.

*Proof.* (1) By Lemma 3.2 (first and second cases) the state after the query is `sum_y' |y'> (2^(-n/2) |D + y'> +
2^-n |D> - 2^(-3n/2) sum_y |D + y>)`; the squared norm of each bracket is `2^-n ((1 - 2^-n)^2 + 2^-n + 2^-n - 2^-2n)
= 2^-n`, and the weight on `|D + y'>` is `2^-n (1 - 2^-n)^2`. `|D>` is a basis state, hence in product with the rest.
(2) By the third case, for each `u != 0` the image differs from `(-1)^(u.y_0) |D>` by a vector of squared norm at most
`2^-n + 9 / 2^n`; the ideal state gives `y_0` with certainty. ∎ Checked numerically for `n = 1..5` on one cell (the
transcribed map is unitary; uniformity exact; `(1 - 2^-n)^2` exact; (2) holds with room).

**Corrected `E_T^Q`:** compressed oracle of capacity `t + K`; after the first measurement, measure the database after
each of the extractor's queries; stop with outcome DEVIATION if a re-queried point does not return its recorded answer
or a fresh answer is not recorded. By Lemma QC, `Pr[DEVIATION] <= 10 (K - k_q,r) / 2^(8(b+e))` (about `2^-222`).
Outside DEVIATION the continuation is lazy sampling extending `db_0` with exactly uniform, independent answers, and
section 6's argument (as repaired) applies. TE-Q's bound stands with this one added, negligible term:

    2 sqrt(k_q,r / 2^n) + 6 T_0^2 (eps_max + c'_max T_0 / 2^(8b)) + sum_(v != r) |J_V,v| eps_v
        + (K - k_q,r) c'_max T / 2^(8b) + 10 (K - k_q,r) / 2^n          (cubic in t, constant 6; N does not multiply t^2)

### 3.3 Which quantum tree figures are proven

- **Proven, given [SG26] Theorem I.16 (1), (K) and T-1:** the per-proof QROM figures; and a tree whose every proof is
  published (one verifier with `K` queries before the measurement; no continuation, no C2).
- **Conditional:** every QROM figure of the recursion tree (69.58 / 70.45; the one-table 76.72 / 77.60; hash part
  80.40, all reproduced by hand from `e_min` 157.03 and `c'`), on: **C2** (not dischargeable); **K-A, K-B** (owed);
  **H-DS and the transcripts' fit to Protocol 6.5** (T-1); **[SG26] Theorem I.16 (1)**, a preprint whose proof was
  read but not re-derived; **Lemma QC and the corrected `E_T^Q`**, unrefereed (C-6); [CMS19] Lemmas 5.9, 5.10 as
  black boxes.
- The sentence "without (ii) there is no proven QROM figure for the tree" is superseded: (ii) is closed in the
  corrected form, and what remains is C2, which was always there.

## 4. The calculator (task D)

121.89 is the correct hash level of TE'. 114.74 has no better foundation (the per-proof sum also needs an extraction
argument for inner proofs) and is only more conservative. **Recommendation:** after C-1 and C-2 are applied to the
lemma document, print 121.89 as the tree's classical hash level "under C2, K-A, K-B, T-1", keep 114.74 as the
per-proof-sum comparison, and derive `K` from the T-1 reports. Neither reaches 128; the attack-rule basis is unchanged.

## 5. Conditions

- **C-1** Restate as TE' (F-1); remove "Proved ... full proof" for a ROM theorem under H-C2; say C2 enters twice.
- **C-2** Replace monotonicity by two-sided instability and "in `B*` at some step" (F-2).
- **C-3** Every tree figure carries "conditional on K-A, K-B" until they are discharged (F-3).
- **C-4** Check in both node circuits that the level is bound in the statement, and H-DS in the transcripts (T-1 item 10).
- **C-5** `E_T` stops at a rejecting child (F-4).
- **C-6** Replace section 9 by the corrected `E_T^Q`, Lemma QC and the bound of 3.2; have Lemma QC refereed.
- **C-7** Wording everywhere: the tree's quantum figures are "derived under the recursion heuristic", not "proven QROM".

## 6. Not checked

[SG26] Definitions I.1, 2.20, 6.1, H.3, H.4, Section I.1, Lemma H.5, Theorem I.17's proof; [CMS19] Appendix A and the
proofs of Lemmas 5.9, 5.10; [Zha18]; Theorem D; the node circuits and transcripts of either system (shape, level
binding, domain separation, in-circuit / native equivalence); K-A, K-B; H-BIND; the calculator beyond
`hashterm.classical_level`, `quantum_level`, `tree_extraction_level` (read, not run); no test suite was run.
