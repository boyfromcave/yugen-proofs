# Citation check: sumcheck and GKR error terms against LFKN and GKR (2026-11-19)

Part of Yugen. Scope: every place in `docs/` where a sumcheck or GKR soundness error
is *used* (search: sumcheck, GKR, LFKN, Libra, 2019/317, XZZPS), checked against the two original
papers the lead architect added to the reference-paper collection (REFERENCES.md). Both were read with pypdfium2
(`.tools-venv`): text layer of every page, and the rendered page for LFKN Lemma 4 (the text layer
garbles its fraction). This document edits no other file except new rows in `REFERENCES.md` and
`docs/CITATION-AUDIT.md`; section 4 lists the changes the other documents should get.

## 1. The two papers: what they state

**[LFKN92]** C. Lund, L. Fortnow, H. Karloff, N. Nisan, *Algebraic Methods for Interactive Proof
Systems*, J. ACM 39(4):859-868, 1992 (file `146585.146605.pdf`, 10 pages).

- It does **not** state the general multivariate sumcheck protocol or an error `d l / |F|`. Its
  protocol is for the permanent of a 0-1 matrix over `Z_p` (Section 3, Theorem 1, p. 861).
- **Lemma 4, p. 862** (read on the rendered page): `C`, `D` are `r x r` over `Z_p`, `g` of degree at
  most `r` with `g(0) != per(C)` or `g(1) != per(D)`; for uniform `a`,
  `Pr[per(C + a(D - C)) = g(a)] <= r/p`. Proof (pp. 862-863): two distinct polynomials of degree at
  most `r` agree on at most `r` points. This is the per-round step of every sumcheck analysis:
  a wrong univariate message survives a uniform challenge with probability at most `deg / |F|`.
- **Proof of Theorem 1, part (2), pp. 863-864**: union over fewer than `N^2` iterations, each
  "Pat succeeds in iteration m" with probability at most `N/p`, total `N^3/p`. The iteration
  analysis is a union bound over first-violation rounds, i.e. a per-round form.
- Section 4, p. 865: arithmetization of formulas (Babai-Fortnow, Shamir) "using a protocol similar
  to that of Section 3": the generic sum over a cube is attributed there, not stated.

**[GKR15]** S. Goldwasser, Y. T. Kalai, G. N. Rothblum, *Delegating Computation: Interactive
Proofs for Muggles*, J. ACM 62(4), Article 27, August 2015 (file `2699436.pdf`, 64 pages; the
journal version of STOC 2008).

- **Section 2.5, Lemma 2.5, p. 27:21** (protocol in **Figure 2, p. 27:22**, credited to Lund et al.
  1992 and Shamir 1992): `F` any finite field, `H` any subset, `f : F^m -> F` of degree at most `d`
  in each variable, `d < |F|`. Soundness: if the sum over `H^m` is not `beta`, every prover is
  accepted with probability at most `m d / |F|`.
- **Proof of Lemma 2.5, pp. 27:22-27:23**: reverse induction (3)
  `Pr[S | A_j and ... and A_m] >= s - (m - j + 1) d / |F|`, each step charging `d / |F|` for the
  round in which the prover's `g_j` first differs from the true one. **The per-round form
  `d / |F|` is this proof's step, stated in the original.**
- **Theorem 3.1, p. 27:25**: the bare-bones (layered circuit) protocol, soundness `1/100`.
  **Proof, Section 3.3, pp. 27:31-27:32**: per phase (layer) `i`, the sumcheck costs
  `3m * 2 delta / |F| <= 6 m delta / |F|` and the reduction of two claims to one costs
  `m (|H| - 1) / |F| <= m delta / |F|`, total `7 m delta / |F|` per layer, union over `d` layers:
  `s <= 7 m d delta / |F|`. **This is the per-layer GKR term in the original.**
- **Two claims to one, p. 27:31, steps (1) to (4)**: a *line* `gamma` through the two points; the
  prover sends `V_i o gamma` (degree `m (|H| - 1)`), the verifier picks `t`. Not a random linear
  combination.
- Field: Section 3.1 (p. 27:26) takes `H` an extension field of `GF[2]` and `F` an extension of
  `H`; Lemma 2.5 holds for any finite field. **Binary extension fields are inside the original.**

## 2. Every use in `docs/`, checked

| # | Place | Error used | Original statement | Verdict |
|---|---|---|---|---|
| U-1 | `round-census-a.md` 2.1 (cites XZZPS19 p. 8 restating LFKN) | per sumcheck round `d/|E|`, `d` per instance (2 to 5) | [GKR15] Lemma 2.5, p. 27:21; per-round step: proof, inequality (3), pp. 27:22-23; [LFKN92] Lemma 4, p. 862 (the same step for the permanent) | **Matches**; it is the original's proof step, not an adaptation. Label can move from Adapted to Published ([GKR15] proof of Lemma 2.5). XZZPS19's `d l` is GKR15's `m d`. |
| U-2 | `round-census-a.md` 2.1, `d` taken as the degree of the round polynomial (`eq` times lines) | `d_j/|E|` | Lemma 2.5's `d` is the degree in each variable of `f`; the proof uses only that each `g_j` has degree at most `d` | **Valid consequence**: with `f = eq * prod`, `d_j` = degree of `f` in `x_j`. Rounds of different degree within one instance: the induction runs with `d_j` per step (one line). |
| U-3 | `lemma-k-a.md` proof item 2, "or the `eq`-form check" (reduced messages) | `d_j/|E|` | Not in either original (Figure 2 sends the full `g_j`) | **Variant, not stated**: valid when the verifier reconstructs the full degree-`d_j` polynomial from the message and the claim (then step (3) applies verbatim). Neither Libra nor any paper in the folder states it in this form; keep as Original (one line) in K-A. |
| U-4 | `lemma-k-a.md` 1-3 (round-by-round knowledge soundness) | `eps_i` per round | [GKR15] and [LFKN92] prove whole-protocol soundness by a union over first-violation rounds; they define no state function | **Valid consequence**: the doomed-state argument of K-A is the event `A_j` of GKR15's induction; the RBR definition stays [SG26] Definition 2.20. |
| U-5 | `round-census-a.md` 2.4, combiner by powers of one challenge, error `N_TREES - 1 = 2` | Schwartz-Zippel, univariate | [GKR15] reduces two claims by a line (p. 27:31), not by a combination; XZZPS19 p. 10 uses two independent coefficients (credited to CFS17) | **Not in either original**; Adapted as the referee's N-2 says. Correct as a one-line Schwartz-Zippel bound. |
| U-6 | `round-census-a.md` 2.4, `y` reducing `2^step` children to their multilinear extension, error `step/|E|` | Schwartz-Zippel, `step` variables | [GKR15] p. 27:31: line restriction, error `m (|H| - 1)/|F|`; with `H = {0,1}` this is `m/|F|`, the same size as `step/|E|` | **Different mechanism, same size**; Original (one line) stays. |
| U-7 | `round-census-a.md` 2.4, "[XZZPS19] Theorem 1 gives only `O(d log |C| / |F|)`; [GKR08] not in the folder" | per-layer sum: combiner + rounds + `y` | [GKR15] Section 3.3, pp. 27:31-32: per layer `6 m delta/|F| + m delta/|F|`, union over layers | **Matches in structure**: per-layer term = the layer's sumcheck rounds plus the claim reduction, union over layers. The sentence that only an asymptotic statement is available is now wrong: GKR15 gives the explicit `7 m d delta / |F|`. |
| U-8 | Product (grand-product) layers, radix 4, three trees, `eq`-weighted layer sumcheck (bus GKR) | per-round | [GKR15] uses `add`/`mult` wiring predicates over a layered arithmetic circuit | **Variant, not stated in GKR15**: the product-tree specialisation (Thaler, CRYPTO 2013, not in the folder) is what is built. Libra (XZZPS19 Section 2.3.2/3) does not state it either. Soundness per round follows from Lemma 2.5's proof as U-1/U-2; the layer construction itself stays cited to leanVM's code. |
| U-9 | `zk-wi-soundness.md` 6 (Lemma 5 amendment m-1, line ~370) and the table row ~432 | tail sumcheck, `2/q` per round | as U-1 | **Matches**; cite [GKR15] Lemma 2.5 (proof). |
| U-10 | Characteristic 2 / binary tower `E` | all of the above | [GKR15] Section 3.1 uses extensions of `GF[2]`; Lemma 2.5 any `F` | **Covered** by the original. (Libra's Section 2.3 says "Let F be a prime field"; that restriction is Libra's, not the sumcheck's.) |
| U-11 | `what-is-proven.md` S-3 "degree bounds by Schwartz-Zippel" | — | — | No source named; add [GKR15] Lemma 2.5 for the sumcheck rounds. |
| U-12 | `knowledge-and-census-referee.md` N-2 | quotes XZZPS19 p. 8, p. 10 | — | A referee record: no change; its N-2 (combiner Adapted) agrees with U-5. |

Uses that name sumcheck/GKR but use no error term (masks, zero knowledge, framework choice,
GKR blinders in `zk-masked-sumcheck.md`, `zk-composition.md`, `zk-system-a-gaps.md`,
`zk-implementation-checklist.md`, `framework-selection.md`, `design-basis.md`, `soundness-method.md`)
were not changed by this check; their Libra citations are about the mask (XZZPS19 Section 4), which
LFKN and GKR do not cover.

**Discrepancies found: none numerical.** Two textual ones: (D-1) the chain "the sumcheck of [LFKN]
is sound with `d l / |F|`" attributes to LFKN a form LFKN does not state; the form is GKR15
Lemma 2.5 (which credits LFKN and Shamir). (D-2) `round-census-a.md` 2.4 says only asymptotic GKR
soundness is available; GKR15 Section 3.3 gives the explicit per-layer term.

## 3. Variants the project uses that the originals do not state

1. Reduced (`eq`-form) round messages (U-3): Original, one line.
2. Combining claims by powers of one challenge (U-5): Adapted (Schwartz-Zippel).
3. Multilinear-extension reduction of `2^step` children at `y` (U-6): Original, one line; GKR15 uses
   a line.
4. Grand-product trees with radix 4 and three batched trees (U-8): not in GKR15 or XZZPS19; the
   standard source (Thaler 2013) is not in the folder.
5. Merged messages (several draws in one message, `round-census-a.md` 1): sum of sub-step errors
   by sequential conditioning, as GKR15's union over events; not stated as such in either.

## 4. Change list for the editing agent (not applied here)

1. `round-census-a.md` 2.1, last sentence: old "[LFKN] (Lund, Fortnow, Karloff, Nisan) is not in
   the reference folder; the statement used is XZZPS19's restatement." -> new "The per-round form is
   the step of [GKR15] (Goldwasser, Kalai, Rothblum, J. ACM 62(4), 2015) Lemma 2.5, p. 27:21, proof
   inequality (3), pp. 27:22-23 (any finite field, any `H`); its origin is [LFKN92] Lemma 4, p. 862
   (J. ACM 39(4), 1992; permanent protocol, error `r/p` per step). XZZPS19 p. 8 restates it."
2. `round-census-a.md` 2.1, label: old "(**Adapted**: the per-round form)" -> new "(**Published**:
   [GKR15] proof of Lemma 2.5; `d` per round as the degree of that round's polynomial)".
3. `round-census-a.md` 2.4, last two sentences: old "[XZZPS19] Theorem 1, p. 10, gives the GKR
   protocol's soundness only as `O(d log |C| / |F|)`; the per-round terms above are what is charged.
   [GKR08] (Goldwasser, Kalai, Rothblum) is not in the reference folder." -> new "[GKR15] Theorem
   3.1, proof in Section 3.3, pp. 27:31-32, charges each layer its sumcheck (`6 m delta/|F|`) plus
   the two-to-one claim reduction (`m delta/|F|`, by a line, p. 27:31) and takes the union over
   layers; the census follows the same per-layer structure. The combiner by powers and the `y`
   reduction are not GKR15's mechanism (Adapted / Original as stated); the product-tree layers are
   not GKR15's circuit form (Thaler 2013, not in the folder)."
4. `round-census-a.md` 2.4, the combiner citation: old "([XZZPS19] p. 10, ... credited to [CFS17],
   its reference [24]): error 2" -> new "(Schwartz-Zippel on a univariate of degree
   `N_TREES - 1`, **Adapted** from [XZZPS19] p. 10's two-coefficient combination): error 2".
5. `round-census-a.md` 5 (Papers): move [LFKN] and [GKR08] from "Not in the folder" to "Used, read
   from rendered pages": "[LFKN92] (146585.146605) Lemma 4, p. 862, proof of Theorem 1 pp. 863-864;
   [GKR15] (2699436) Lemma 2.5 and Figure 2, pp. 27:21-23; Theorem 3.1 and Section 3.3,
   pp. 27:25, 27:31-32"; rename the key [GKR08] -> [GKR15] (journal version).
6. `lemma-k-a.md` proof item 2, end: old "`d_j/|E|` (2.1)." -> new "`d_j/|E|` (2.1; [GKR15]
   Lemma 2.5, proof step (3); for the `eq`-form check, valid because the full round polynomial is
   determined by the message and the claim, Original)."
7. `lemma-k-a.md` proof item 4: append "(GKR15 reduces two claims by a line, p. 27:31; the
   multilinear-extension form here is Schwartz-Zippel, Original)".
8. `lemma-k-a.md`, the source line (line 6 area, "Rounds and errors: `round-census-a.md`"): add
   "sumcheck and GKR terms checked against [LFKN92], [GKR15] (`citation-check-lfkn-gkr.md`)".
9. `zk-wi-soundness.md` 6, Lemma 5 amendment (around line 370): old "([XZZPS19], ePrint 2019/317,
   Section 2.3.1, p. 8: sumcheck error `d l / |F|`, here per round, `d = 2`; Adapted to the
   per-round form)" -> new "([GKR15] Lemma 2.5, p. 27:21, per-round step of its proof pp. 27:22-23,
   `d = 2`; Published; restated in [XZZPS19] p. 8)". Not on this agent's do-not-edit list, but left
   for the editing agent so that the K-A/census wording is changed in one pass.
10. `zk-wi-soundness.md` table row "tail sumcheck round `t`" (around line 432): old "Lemma 5
    amendment (sumcheck, XZZPS19 p. 8)" -> new "Lemma 5 amendment (sumcheck, [GKR15] Lemma 2.5)".
11. `what-is-proven.md` S-3, source column: old "degree bounds by Schwartz-Zippel ..." -> new
    "sumcheck rounds: [GKR15] Lemma 2.5 (per-round step); GKR layers: [GKR15] Section 3.3 structure;
    other draws: Schwartz-Zippel ...".
12. `REFERENCES.md` Part 2, the existing rows for `round-census-a.md` 2.1 and 2.4 (now superseded by
    the rows this check added below them): change "(restating [LFKN], not in the folder)" to
    "(restating [LFKN92]/[GKR15], see next rows)" and, in the 2.4 row, "Theorem 1, p. 10
    (asymptotic soundness only)" to "(explicit per-layer form: [GKR15] Section 3.3)". Left to the
    lead (rows of other agents are not edited here).

Twelve changes in five files (`round-census-a.md` 5, `lemma-k-a.md` 3, `zk-wi-soundness.md` 2,
`what-is-proven.md` 1, `REFERENCES.md` 1).

## 5. BCIKS20 (ePrint 2020/654, ECCC TR20-083): every citing place, for a re-check

Not in the reference-paper collection (REFERENCES.md) at the time of this check (placed there later the same day and checked: `CITATION-AUDIT.md` 1j, C-41, C-42). The documents cite a copy fetched from ECCC (May 30, 2020;
`REFERENCES.md` 1.2). Theorem S rests on Theorems 4.1 and 1.7 (and Remark 1.5); also cited:
Theorems 1.2, 1.4, 1.6, 5.1, 5.2, Lemma 5.3, Claim 5.4, Proposition 5.5, Sections 5.2, 6, 7.
Places (file, number of lines, line numbers at `HEAD` of this check; generated by
`grep -nE 'BCIKS|2020/654|TR20-083'`):

- `-sound/test_proximity.py` (1): lines 7
- `FERENCES.md` (13): lines 116, 151, 689, 708, 753, 756, 772, 847, 884, 890, 896, 911, 916
- `cs/CITATION-AUDIT.md` (14): lines 246, 249, 255, 274, 281, 336, 352, 388, 451, 497, 507, 546, 557, 898
- `cs/b-round-census.md` (2): lines 71, 163
- `cs/binius-extension-challenges.md` (10): lines 22, 42, 75, 102, 291, 314, 559, 579, 601, 670
- `cs/binius-johnson-row.md` (13): lines 38, 61, 84, 90, 131, 190, 256, 407, 602, 850, 855, 911, 913
- `cs/decision-security-category.md` (2): lines 356, 497
- `cs/decision-security-profile.md` (2): lines 329, 348
- `cs/design-basis.md` (4): lines 82, 194, 348, 541
- `cs/framework-selection.md` (1): lines 241
- `cs/johnson-row-referee-2.md` (3): lines 107, 248, 298
- `cs/johnson-row-referee.md` (9): lines 70, 71, 168, 173, 176, 177, 315, 433, 437
- `cs/lemma-k-b.md` (1): lines 101
- `cs/qrom-zk-referee.md` (5): lines 22, 281, 285, 294, 444
- `cs/round-census-a.md` (1): lines 231
- `cs/security-profile-referee.md` (2): lines 47, 129
- `cs/soundness-method.md` (16): lines 69, 70, 71, 72, 76, 86, 119, 294, 297, 337, 665, 698, 708, 714, 732, 831
- `cs/theorem-s-referee.md` (4): lines 22, 23, 35, 66
- `cs/what-is-proven.md` (3): lines 46, 48, 51
- `cs/whir-additive-soundness.md` (8): lines 16, 30, 41, 57, 58, 84, 207, 287
- `cs/zk-hiding-commitment.md` (3): lines 311, 572, 797
- `cs/zk-wi-soundness.md` (16): lines 25, 44, 48, 65, 70, 73, 75, 78, 160, 225, 466, 655, 695, 718, 719, 772
- `hnson-row/rowcalc.py` (1): lines 56
- `hnson-row/test_mask_round.py` (2): lines 26, 178
- `t-challenge/test_code.py` (1): lines 57
- `undness/CHANGELOG.md` (2): lines 239, 635
- `undness/output/current-tables.txt` (1): lines 129
- `undness/output/revision10-proven-basis-tables.txt` (5): lines 187, 188, 189, 196, 256
- `undness/output/revision10-tables.txt` (5): lines 187, 188, 189, 196, 256
- `undness/output/revision8-tables.txt` (5): lines 29, 30, 31, 38, 98
- `undness/output/revision9-tables.txt` (5): lines 163, 164, 165, 172, 232
- `undness/src/yugen_soundness/binius64.py` (5): lines 38, 49, 336, 570, 574
- `undness/src/yugen_soundness/bounds.py` (15): lines 44, 45, 47, 48, 51, 52, 80, 85, 110, 121, 159, 165, 166, 167, 168
- `undness/src/yugen_soundness/category.py` (1): lines 40
- `undness/src/yugen_soundness/current.py` (1): lines 525
- `undness/src/yugen_soundness/dkt26.py` (3): lines 39, 332, 393
- `undness/src/yugen_soundness/fri.py` (1): lines 6
- `undness/src/yugen_soundness/johnson.py` (1): lines 17
- `undness/src/yugen_soundness/revision5.py` (1): lines 30
- `undness/src/yugen_soundness/wi.py` (2): lines 4, 25
- `undness/tests/test_revision7.py` (1): lines 5
- `undness/tests/test_soundness.py` (1): lines 46

Priority for the re-check when the PDF arrives: Theorem 4.1 and Theorem 1.7 as used by Theorem S
(`zk-wi-soundness.md`, `whir-additive-soundness.md`, `theorem-s-referee.md`, `qrom-zk-referee.md`),
Theorem 1.2's two error forms (`soundness/src/yugen_soundness/bounds.py`), and the Section 5.2/6/7
gaps G-1, G-3, G-6 (`binius-johnson-row.md`, `johnson-row-referee.md`).
