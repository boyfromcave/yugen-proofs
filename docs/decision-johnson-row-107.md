# Decision record: adopt the 107-query Johnson-regime row (rate 1/8, `m = 10`) for System B, and a 2^22 shape for merge kinds?

Part of Yugen. `yugen-proofs`. Revision 1, 2026-11-23. **For the lead architect's ruling; nothing
here is decided and no spec or code was changed.** Figures carry a label: **M** measured (built and run),
**C** counted (circuit census or exact arithmetic), **E** estimated. Citations carry provenance labels
(Published / Adapted / Original (the Ycash developers)).

## 0. In plain language

System B (the Binius64 fork) checks each proof by opening its committed codewords at random places. Today
the soundness argument is the classical "unique decoding" one, which is peer reviewed and needs **184**
openings (192 under the counting convention the lead architect ruled on 2026-11-19). A newer argument, valid
up to the "Johnson radius", lets each opening count for more, so **107** openings (111 under the ruled
convention) give the same security. That cuts proof size and verifier work by about 40 %, and makes the
merge verifier fit in half the circuit (2^21 instead of 2^22 AND rows).

The catch: the newer argument rests on one paper (Dao, Kominers, Thaler, ePrint 2026/2056, "DKT26") that is
**a preprint, not peer reviewed**. Its key theorem was read by two of our referees and is machine-checked in
Lean (we compiled it), but nobody outside this project has reviewed our use of it. If the theorem were
wrong, a 107-query proof would keep only about **89 bits** a round (about 59 bits over the 20,000-proof
tree), against 152 to 158 needed: forging a proof would then be expensive but within reach of a
well-funded attacker, and a forged leaf proof means undetected inflation of the shielded pool.

Note on the counts: the title says 107; under the ruled "every t" convention (`decision-qrom-counting.md`)
the rows to ship are **111** (Johnson) and **192** (unique decoding). Both are given below.

## 1. What changes

| Item | Unique decoding, rate 1/8 | Johnson `m = 10`, rate 1/8 | Label, source |
|---|---|---|---|
| Queries, book convention (need 152.52) | 184 (152.73 bits) | 107 (152.97 bits) | C, `binius-johnson-row.md` 0.4 |
| Queries, ruled "every t" convention | 192 (159.37 vs need 158.59) | 111 (158.69 vs need 157.86) | C, `yugen-proof-b2/docs/parameters.md` 16.1 (calculator revision 9) |
| Weakest algebraic round | 226.00 bits | 211.41 closed form / 212.14 DKT26 exact / 212.11 Lean count | C, `binius-johnson-row.md` 0.4; `arklib-lean-check.md` L-2 |
| Leaf / node proof size | 568 / 699 KiB | 362 / 449 KiB | E, `binius-johnson-row.md` 0.4, 751 |
| Level-0 node proof (K = 1) | — | 364,960 bytes at 107 | M, `parameters.md` 14.4 |
| Leaf verifier slot, AND rows | 7.82 M (184, E); 3,816,030 at 192, groups of two (M, replayed), pads to 2^22 | 2,106,406 at 107 single circuit (M); 2,158,112 at 111, best cap (C); pads to **2^22** (60,960 over 2^21) | `binius-johnson-row.md` 0.4; `parameters.md` 14.4, 16.7 |
| Merge slot, AND rows | 3,080,123 at 192, groups of five (C); 3,664,903 groups of two (M); **2^22** | 2,058,958 at 107, groups of six (M, replayed); 1,985,497 at 111, groups of five (C, not recounted); **2^21** | `parameters.md` 14.4, 16.7 |
| Rests on | BCIKS20 Theorem 4.1 (peer reviewed) | DKT26 Theorem 4.4, Corollary 6.6, Lemma 3.3 (preprint) | section 2 |

Shape: with the Johnson row the merge slot halves (2^22 to 2^21) but the rate-1/8 leaf slot does not (it
stays 2^22 unless the Frobenius-form wrapper lands, about 2,054,000 at cap 5, E, `parameters.md` 16.7). The
"2^22 shape for merge kinds" of the title is read here as: keep every merge kind padded to the same 2^22
shape as the leaf slot rather than trimming to 2^21, and spend the room on **one merge shape** that reads
both child kinds (lead decision (d), not built; `parameters.md` 14.6; final verifier about 110 to 135 ms
against 330 ms, E, 14.5). This interpretation is the lead agent's; correct it if another was meant.

## 2. The security claim

**Unique-decoding row (184 / 192).** Per-query error `(1 + rho)/2 = 9/16`; algebraic rounds by WHIR Lemma 4.10
(any linear code) with BCIKS20 Theorem 4.1 (any evaluation set), width by DKT26 Lemma 6.5 (elementary, proof
read by builder and both referees). Second in-folder source for the line bound: SG26 Lemma 2.14 (2)
(`johnson-row-referee-2.md` 2.1). No Johnson-regime statement used.

**Johnson row (107 / 111).** Per-query error `a = (1 + 1/(2m)) sqrt(rho) = 0.3712` at `m = 10`; list size 19.
Mask, index and fold rounds need line mutual correlated agreement with full agreement sets at the Johnson
threshold, characteristic 2, arbitrary evaluation set, exceptional count below `2^103.48` at `n = 2^30`. DKT26
gives `2^43.9` to `2^44.6`: 59.6 bits of slack, so the row uses the theorem only qualitatively
(`johnson-row-referee-2.md` 0).

**Citations (Published unless stated).**

- **DKT26**: Q. Dao, S. D. Kominers, J. Thaler, *Reed–Solomon Codes Beyond Johnson: Efficient Decoding and
  Smaller Cryptographic Proofs*, IACR ePrint 2026/2056, copy dated 2026-11-02. **Preprint, not peer
  reviewed** (the ArkLib merge commit names an `rs-beyond-johnson-stoc-submission` branch: submitted, not
  accepted as far as recorded). Used: Theorem 4.4 (line MCA at Johnson, bound (38)/(39)), Corollary 6.6
  (interleaved, width independent), Lemma 3.3 (message dimension 1), Lemma 6.5 (width), Corollary 6.4,
  Corollary 9.4 (list decoding, statement), Proposition B.1. PDF in the folder:
  `2026-2056.pdf` (see REFERENCES.md). Read by the builder (`binius-johnson-row.md` 1: Theorem 4.4
  statement and proof paragraph; Lemmas 3.3, 6.5 proofs; Theorem 4.4's lemmas 4.1 to 4.3, A.5 **not checked**
  line by line) and by the second referee (`johnson-row-referee-2.md` 1: Section 4 in full with proofs,
  Appendix B, Lemmas A.4, A.5; no gap found; BCHKS's dimension count (109) verified by exact arithmetic at our
  sizes only). **Machine check**: ArkLib `6aa8b6fe`, Lean 4.35.0, four theorems compiled, axioms only
  `propext`, `Classical.choice`, `Quot.sound` (`arklib-lean-check.md`, C-1). This record's author did not
  re-read the PDF.
- **WHIR**: G. Arnon, A. Chiesa, G. Fenzi, E. Yogev, *WHIR: Reed–Solomon Proximity Testing with Super-Fast
  Verification*, ePrint 2024/1586 (copy 2024-11-21), Lemma 4.10 (unique-decoding proximity generator, any
  linear code). Peer reviewed per the documents (not verified here). Read by the builder after referee R-7.
  Corollary 4.11 is for smooth domains and is **not** cited for our additive domain (CITATION-AUDIT 1c).
- **BCIKS20**: E. Ben-Sasson, D. Carmon, Y. Ishai, S. Kopparty, S. Saraf, *Proximity Gaps for Reed–Solomon
  Codes*, ePrint 2020/654 (folder copy, revision of 2021-07-03, `2020-654.pdf`; FOCS 2020, peer reviewed, from
  memory), Theorem 4.1 (any evaluation domain) and Theorem 1.2 (1.1), checked against the folder copy
  (CITATION-AUDIT 1j). Earlier documents cited the ECCC TR20-083 copy, not in the folder.
- Haböck, *Basefold in the List Decoding Regime*, ePrint 2024/1571 (framework and query lemma, shared by both
  rows); CFW26 = Chiesa, Fenzi, Weissenberg, ePrint 2026/391, Lemma 6.6 (shape of Lemmas J2, F: Adapted);
  SG26 = Sharp, Grubbs, ePrint 2026/2615, Theorem 6.6 (2) (the counting convention).
- Lemmas U, J1, J2, J3, F, K and the rows: Adapted / Original (the Ycash developers, 2026),
  `binius-johnson-row.md` provenance table.

## 3. The second referee's conditions (`johnson-row-referee-2.md` 7)

| Condition | Met today? | Evidence | What remains |
|---|---|---|---|
| C-1 Lean compile of the four ArkLib theorems | **met** | `arklib-lean-check.md`; `lean/Compose.lean` recompiled 2026-11-19 | nothing (ArkLib build deleted to save disk; re-clone to recheck, handoff 2026-11-23) |
| C-2 counting convention Q-5 | **met (ruled)**: "every t" | `decision-qrom-counting.md` | ship **111**, not 107; the 107 builds are records only |
| C-3 calculator DKT26 terms | **met** | calculator revision 8 (`soundness/.../dkt26.py`, `test_revision8.py`); revision 9 rows cross-checked (`parameters.md` 16.1) | nothing |
| C-4 build properties in the `johnson` build | **met** at 107 and 80 | `parameters.md` 14.7 | rerun at **111** (identifiers changed with revision 9; `target/j8` no longer verifies) |
| C-5 tests and text here | **met** | `binius-johnson-row.md` revision 2.1 | nothing |
| C-6 (a)-(c) deviations D-pre, D-term, change 41 | **met** | `parameters.md` 14.7, `tests/referee_conditions.rs` | rerun with the 111 build |
| C-7 (rate 1/16, 80 queries only) | **met** at 80 | `parameters.md` 14.7 | not needed for the rate-1/8 row; 82 under the ruling |

All conditions are met at the counts they named; the rerun at 111 is the one open engineering item.

## 4. External review still outstanding

Referee 1 (R-1 (b)) asked an **external reviewer** to sign review item 1 (DKT26 Theorem 4.4 / Corollary 6.6
as used). The lead architect ruled that the second, internal referee stands in for it
(`johnson-row-referee-2.md` 3, R-1 row). So formally nothing is open; in substance no one outside the Ycash
developers has checked (i) DKT26 itself, or (ii) our application (Lemmas J2, F, K to Binius64 as built).
What would satisfy it, any one of:

1. a cryptographer outside the project signs a review of Lemmas J2, F, K against DKT26 4.4 / 6.6 and the build;
2. DKT26 accepted at a peer-reviewed venue, plus (1) for our application;
3. one of the independent Johnson-radius MCA proofs DKT26 Section 1.2 names (BCHKS ePrint 2025/2055 Theorem 4.6;
   Haböck 2025/2110; Bordage, Chiesa, Guan, Manzur 2025/2051), read and found to state the qualitative property
   of section 2 (none is in the folder, none read).

The Lean check covers the theorem's statement and proof, not that the statement is the one our lemmas need
(the referee and `arklib-lean-check.md` 4 compared them by hand).

## 5. Options

| Option | Gain | Rests on | Work needed | Reversed by |
|---|---|---|---|---|
| **A** stay at 184 (192) | none; status quo | BCIKS20 Thm 4.1, peer reviewed | none beyond current plan | a measured need for smaller proofs or slots that 192 cannot meet |
| **B** 107 (111) for every System B kind | ~40 % smaller proofs (E); merge slot 2^21 (C); leaf slot stays 2^22 at 1/8 | DKT26 4.4, 6.6, 3.3 (preprint) + Lemmas J2, F, K | spec version bump (row in statement ids), new verifying keys for every level, new vectors, A/B equivalence over the new tree, C-4/C-6 rerun at 111, miner/prover re-base (prover jobs re-timed), mixed slot shapes (leaf 2^22, merge 2^21) | a flaw in DKT26 4.4 / 6.6 or in Lemmas J2/F; an external review that does not sign |
| **C** as B, merge kinds held at a 2^22 shape | B's proof-size gain; one slot size everywhere; room for **one merge shape** for both child kinds (final verifier ~110-135 ms vs ~330 ms, E) | as B | all of B, plus the one-merge-shape work of `parameters.md` 14.6 (shared constant table, flags, `tests/node_main.rs` with mixed children); gives up B's 2^21 merge saving | as B; or the one-merge-shape build failing its acceptance |
| **D** ship 192 at launch, 111 as a later upgrade | launch on peer-reviewed footing; the gain later | A now; DKT26 + external review later | A's work now; later: a new spec version and keys accepted beside the old (verifier accepts both statement ids for a transition), vectors, A/B equivalence, miner re-base; keep the `johnson` build green meanwhile | DKT26 refuted (then stay on A); or a launch requirement that 192 cannot meet |

## 6. Failure mode if the Johnson-regime bound is wrong

If DKT26 Theorem 4.4 / Corollary 6.6 failed in the strong sense (exceptional count above `2^103.48`), the
mask, index and fold rounds of the 107/111 rows lose their Johnson bound (`johnson-row-referee-2.md` 4.5). What
remains is the unique-decoding analysis (Lemma UD, which does not depend on the query count): fold rounds stay
near 226 bits, and the query round falls to the unique-decoding per-query error.

Formula (Published: Haböck 2024/1571 query lemma with the unique-decoding agreement `a = (1 + rho)/2`, as
`binius-johnson-row.md` 2.1 and 6 use it; arithmetic Original):

    bits(t) = -t log2((1 + rho)/2),  rho = 1/8:  -log2(9/16) = 0.8301 bits a query

    t = 107:  88.82 bits        t = 111:  92.14 bits        (check: t = 184 gives 152.73, as the table)

Against the tree (need `kappa + 1 + log2 20,000 + log2(1 + k_q)`, the ruled convention; 14.29 + 14.57 at
`k_q = 24,378`): about **59 bits** classical at 107 and **62 bits** at 111 for the whole 20,000-proof tree,
against 128 targeted (C, from the formula; the 107 figure uses 111's `k_q`, E).

What an attacker could do: grind Fiat–Shamir query challenges, about `2^89` to `2^92` hash evaluations per
forged proof (fewer against a full tree), to have a far-from-code committed word pass. A forged leaf proof
is a spend or mint without note and key: undetectable inflation of the shielded pool. Quantum (Grover) search
roughly halves the exponent. The 184/192 row is unaffected by this failure.

## 7. Recommendation (the lead agent's)

**Option D**: ship 192 queries at launch on all System B kinds (2^22 shapes, as built and certified), and
carry 111 as a prepared upgrade, adopted when section 4's external review is signed.

Reasons: (1) every referee condition is met, but the theorem is a three-week-old preprint and the fallback
(about 59 tree bits) is a pool-inflation risk, not a degradation; (2) 192 already fits every slot in 2^22 (M/C),
so the Johnson row buys size and verifier time, not feasibility, except the merge slot halving; (3) the final
verifier gain the plan needs (D-6) comes mainly from one merge shape and the residue cut, which work at 192
too; (4) D keeps the `johnson` build and its tests green, so the upgrade is a spec version and new keys, not
new research. If launch size or prover throughput measurements show 192 cannot meet the 1,500-payment
target, **C** is preferred over B (one shape everywhere) and needs the external review before activation.

Reversed by: an external sign-off before launch (then C at launch), or a peer-reviewed acceptance of DKT26
plus that sign-off.

## Ruling (lead architect, 2026-11-23)

**Option D, at 192 only.** System B ships the unique-decoding row (192 queries, rate 1/8). The
Johnson-regime row (111 queries) is not built into the launch release: no second key set, no
disabled switch, no value-capped lane. It may be proposed again as a later network upgrade after a
review of DKT26 and of its use here by someone outside the project. Coexistence of both rows with
a choice per prover was considered and not adopted: soundness is a property of what the verifier
accepts, so the pool is as strong as the weakest accepted row.
