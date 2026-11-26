# References and provenance

Part of Yugen. This file has three parts: the bibliography (what each source is and
how much of it was read), the reliance table (which document and section rests on which result
of which source), and the list of original contributions of the Ycash developers.

Provenance labels used here and in every document of `docs/`:

- **Published**: taken as is from the cited source.
- **Adapted**: built on the cited source; the change is stated.
- **Original (the Ycash developers, 2026)**: devised in this project; the related prior work and
  what was checked before the label was given are stated. "Original as far as checked" means
  that prior publication cannot be ruled out; the sources consulted are listed.

How the five supplied papers were read (2026-11-19, citation audit): the PDF files in the lead
architect's reference directory. 2025/1015 was read in full, page by page. For the other four
the page renderer was not available on this machine, so the text layer of each PDF was extracted
locally to a temporary directory outside every repository and read from there: 2024/1037
pages 1 to 16 in full; 2016/116, 2019/317 and 2026/391 by the sections named in each entry.
Formulas in those three were read from the text layer, not from the typeset page; a statement
whose formula could not be read reliably from the text layer is not quoted here.

Second pass (2026-11-19, the same day): the lead architect added four papers, 2019/834, 2024/504,
2024/1571 and 2024/1586, and re-saved 2026/391. All five were read from their text layer, extracted
locally to a temporary directory outside every repository, by the sections named in each entry.
The re-saved 2026/391 is the same revision as before (first page dated November 16, 2026, 102
pages; Lemma 3.29, Construction 6.4, Lemma 6.2, Construction 9.9 at the same places), so the
numbering of the earlier version cited by the pinned Plonky3 code still cannot be established.
Findings C-6 to C-13 of `docs/CITATION-AUDIT.md` come from this pass.

---

## Part 1. Bibliography

### 1.1 The supplied papers (five on 2026-11-19 morning, four more the same day)

**[BCS16]** Eli Ben-Sasson, Alessandro Chiesa, Nicholas Spooner. *Interactive Oracle Proofs.*
Cryptology ePrint Archive, Paper 2016/116. The copy read is dated February 10, 2016 (48 pages);
it states no venue. (The conference version is cited by [Dia25] as TCC 2016, LNCS 9986,
pp. 31-60; its section numbers differ: [Dia25] cites the salted variant as "[BCS16, § 3.2]",
which is also Section 3.2 "Privacy" in the copy read.)
Read: abstract; Sections 1.3.2 and 1.3.3 (Theorems 1.2 and 1.5, Remarks 1.3, 1.4, 1.6);
Section 1.4 (the paragraph "Preserving zero knowledge"); Section 2.3 (zero knowledge in the
explicitly-programmable random oracle model, Remark 2.2); Section 3.2 (Definition 3.3,
Lemma 3.4 and the first half of its proof); Theorem 7.1; Section 7.4 (Lemma 7.5 and its proof);
the statement of Appendix C. Not read: Sections 4 to 6, 7.1 to 7.3, 8.

**[XZZPS19]** Tiancheng Xie, Jiaheng Zhang, Yupeng Zhang, Charalampos Papamanthou, Dawn Song.
*Libra: Succinct Zero-Knowledge Proofs with Optimal Prover Computation.* Cryptology ePrint
Archive, Paper 2019/317 (38 pages). The copy read states neither a date nor a venue.
Read: abstract, Section 1 (contributions); Section 2.3 (Protocol 2, "Let F be a prime field");
Section 2.4 (Definition 4); Section 4.1 in full (Construction 1, Theorem 3 and its proof);
Section 4.2 (equations (7) to (9), Construction 2 steps 1 to 5(e), Theorem 4 and the start of
its proof; the rank condition `2 c^2 - 1 != 0 mod p` on page 25); the headers of
Constructions 3 and 4 and of Theorem 6. Not read: Section 3 (the linear-time prover),
Section 4.3 onward in detail, Section 5.

**[HK25]** Ulrich Haböck, Al Kindi. *A note on adding zero-knowledge to STARK.* Cryptology
ePrint Archive, Paper 2024/1037. The copy read is the revision dated February 20, 2025
(21 pages); no venue stated.
Read: pages 1 to 16 in full (Sections 1 to 4: Protocols 1 to 3, Lemmas 1 to 5, Theorems 4, 6,
7, Remarks 1 to 5, footnote 3). Not read: Section 5 and Appendix A (permutation arguments).

**[Dia25]** Benjamin E. Diamond. *Zero-Knowledge Polynomial Commitment in Binary Fields.*
Cryptology ePrint Archive, Paper 2025/1015 (10 pages). The copy read states neither a date nor
a venue. Read in full.

**[CFW26]** Alessandro Chiesa, Giacomo Fenzi, Guy Weissenberg. *Zero-Knowledge IOPPs for
Constrained Interleaved Codes.* Cryptology ePrint Archive, Paper 2026/391. **The copy read is
the revision dated November 16, 2026** (102 pages); no venue stated. Its numbering differs from
the numbering cited in the pinned Plonky3 code (`fe5e46d7`), which implements an earlier
version: the code's "Construction 6.3", "Lemma 6.4", "Proposition 3.19", "Lemma 3.26" and
"Construction 9.7" do not exist under those numbers in the copy read (see
`docs/CITATION-AUDIT.md` section 2 for the correspondence that could be established). The
earlier version was not available and nothing is attributed to it.
Read: abstract; Sections 1.2, 1.3, 1.4; Section 2.5 (Definitions 2.6, 2.7, Claim 2.8,
Construction 2.9, Lemmas 2.10, 2.11, "Comparisons"); Section 3.3.1 (Definitions 3.21, 3.23,
3.25, 3.27, Claims 3.22, 3.24, 3.26, Lemmas 3.28, 3.29, Theorem 3.30); Section 6.1 to 6.3
(Definition 6.1, Lemma 6.2 with proof, Theorem 6.3, Construction 6.4, Lemma 6.5 and the first
half of its proof); Section 7 (Theorem 7.1, Construction 7.2, Lemma 7.3 with proof);
Sections 9.1 to 9.3 (Lemmas 9.1, 9.4, 9.5, 9.7, Definitions 9.2, 9.3, 9.6) and the statement of
Theorem 9.8 with Construction 9.9 steps 1 to 4; Section 10.1; Section 11 (layout, the mask
polynomial, the last stage, "Security", "Communication", "Reed-Solomon codes", "Merkle
commitments"); Appendix B (Lemmas B.1, B.2 with proofs, "Application"). Not read: Sections 2.1
to 2.4, 2.6 to 2.8, 3.1, 3.2, 4, 5, 6.4, 7.2, 8, 9.4 to 9.7, 10 (theorem), 12, 13, Appendix A.

**[CMS19]** Alessandro Chiesa, Peter Manohar, Nicholas Spooner. *Succinct Arguments in the
Quantum Random Oracle Model.* Cryptology ePrint Archive, Paper 2019/834. The copy read is dated
January 14, 2020 (56 pages, with an appendix by James Hulett); it states no venue (the documents'
earlier "TCC 2019" is from memory). Read: abstract; Section 1.2 (Theorems 1 to 3, informal);
Section 4.2 (Definition 4.8, Lemma 4.9); Sections 5.1 and 5.2 (statements of Lemmas 5.9, 5.10;
Lemma 5.13, the lifting lemma, with proof); Section 6.3 (Lemmas 6.10, 6.11, the end of the proof of Theorem 6.1, tightness);
Section 7 (Theorem 7.1, Lemma 7.3 with proof, Lemma 7.4); Section 8 in full (Definitions 8.1,
8.3 to 8.5, Remark 8.2, Theorem 8.6, Propositions 8.11, 8.12, Lemmas 8.7, 8.8, 8.13, Section
8.5.1, 8.5.2, 8.6). Not read: Sections 2, 3, 5.3 (the proof of Lemma 5.10), 6.1, 6.2, Appendices
A and B.

**[DP24]** Benjamin E. Diamond, Jim Posen. *Polylogarithmic Proofs for Multilinears over Binary
Towers.* Cryptology ePrint Archive, Paper 2024/504 (50 pages). The copy read states neither a date
nor a venue. Read: abstract; Section 1.1 (in part), 1.3 (the Hashcaster comparison, equations (14) to
(21), Figure 4, and the efficiency comparison), 1.5; 2.6 (Theorems 2.3, 2.4); 2.7 (Definitions 2.8 to 2.10); 3.1
(Construction 3.1, Theorems 3.2, 3.5 with proof); 4.3 (Construction 4.12, Lemma 4.14, Theorem
4.17 with proof: Definitions 4.18, 4.20, Lemma 4.19, Propositions 4.21 to 4.24, Lemmas 4.25,
4.26, Remark 4.27); 5.2 (concrete soundness, equation (42)). Not read: Sections 2.1 to 2.5, 3.2,
4.1, 4.2, 4.4, 5.1 and the rest of 5.2. Its numbering differs from the one [Dia25] cites: [Dia25]
names DP24's "Proposition 4.23, Lemma 4.13, Definition 4.17"; in this copy Proposition 4.23 is the
bound on the bad folding events, and 4.13 and 4.17 are Theorems (completeness and security of
Construction 4.12). [Dia25] cites an earlier revision.

**[Hab-LDR]** Ulrich Haböck. *Basefold in the List Decoding Regime.* Cryptology ePrint Archive,
Paper 2024/1571 (39 pages). The copy read states no date or venue; it says it is a revision of the
author's earlier preprint that recasts the analysis as round-by-round soundness and adds WHIR.
Read: abstract; Sections 3 (Protocols 1, 2, Theorem 1, the soundness sketch), 4 (statements of
Theorems 2, 3, 4, Remark 5, Section 4.2), 5 (Lemmas 1, 2, 3 with proofs, Section 5.4), 6.1 (Lemma
4), 6.2, 6.3 (Protocol 3, Lemma 5 with proof, Theorem 6), 6.4 (Protocol 4, Lemmas 6, 7, 8). Not
read: Sections 1, 2, the proofs of Section 4.1 (Propositions 1, 2 are BCIKS20's Proposition 5.5
and Section 6.2, not read there either).

**[ACFY24]** Gal Arnon, Alessandro Chiesa, Giacomo Fenzi, Eylon Yogev. *WHIR: Reed–Solomon
Proximity Testing with Super-Fast Verification.* Cryptology ePrint Archive, Paper 2024/1586. The
copy read is dated November 21, 2024 (83 pages); no venue stated. Read: abstract; Sections 4.1
(Definitions 4.1, 4.2, Theorem 4.3, Lemma 4.4), 4.2 (Theorem 4.8, Definition 4.9, Lemma 4.10 with
proof, Corollary 4.11, Conjecture 4.12, Lemma 4.13 statement), 4.4 (Lemmas 4.24, 4.25),
Construction 5.1, Theorem 5.2 and the start of its proof (the state function), the statement of
Theorem 7.5. Not read: Sections 1 to 3, 4.3, the rest of 5.1, 5.2, 6, 7 (except Theorem 7.5), 8.

### 1.1b Read for `docs/binius-johnson-row.md` (2026-11-19, papers added by the lead architect that afternoon)

Text layer extracted locally to a temporary directory outside every repository, as above.

**[DKT26]** Quang Dao, Scott Duke Kominers, Justin Thaler. *Reed-Solomon Codes Beyond Johnson:
Efficient Decoding and Smaller Cryptographic Proofs.* Cryptology ePrint Archive, Paper 2026/2056.
The copy read is dated November 2, 2026; no venue stated. Read: abstract; Theorem 1.1 (statement);
Definition 3.2 (line MCA with full agreement sets); Section 4.3, Theorem 4.4 (statement, bounds (38)
list and (39) exceptional count `B_cf < 8 n t^3 / (3 rho_-)`, in every characteristic, any distinct
evaluation points) and its short proof paragraph; Section 6.2: Corollary 6.4 (interleaved lists, with
proof), Lemma 6.5 (interleaving preserves polynomial-family MCA, with proof), Corollary 6.6
(interleaved MCA, width independent, with proof). Not read: Lemma 4.3's proof, Appendix B, Sections
2, 3.3 onward, 5, 7 to 9. (Section 1.3 below listed DKT26 for P4; that claim was not re-checked
here.)

**[CWYZ26]** Alessandro Chiesa, Guy Weissenberg, Eylon Yogev, Kai Zhe Zheng. *Affine Combiners for
Reed-Solomon Proximity Gaps.* Cryptology ePrint Archive, Paper 2026/2863. The copy read is dated
November 13, 2026. Read for this document: abstract only (affine combiners `f + (alpha + beta x) g`;
scalar combiners have worst-case MCA error `Omega(n/q)` at the Johnson threshold). Nothing in
`binius-johnson-row.md` rests on it.

Title pages only, nothing used: Block, Garreta, Katz, Thaler, Tiwari, Zając, *Fiat-Shamir Security
of FRI and Related SNARKs*, ePrint 2023/1071 (copy dated February 15, 2024); Sharp, Grubbs, *Faster
and Smaller Anonymous Credentials from Standardized Signatures*, ePrint 2026/2615. Also read for that
document: [BCIKS20] (ECCC TR20-083, copy of May 30, 2020) Theorems 1.2, 1.4, 1.5 (1.6 in that copy; numbers amended 2026-11-19 to the folder copy, ePrint 2020/654 revision of July 3, 2021, C-41), 4.1, 5.1, 5.2,
Lemma 5.3, Section 5.2 Steps 1 and 2 (Claim 5.4), Section 7.2; this copy has no weighted section.

**Read for revision 2 of `docs/binius-johnson-row.md`** (2026-11-19, answering
`docs/johnson-row-referee.md`; text layers extracted to a scratch directory outside every
repository): [DKT26] further: Section 1.1 (knowledge soundness by list decoding), Theorem 1.3
(informal), Section 1.2 (related work: [BCH+26], [Hab25], [BCGM25], [Jo26a]), Section 3.1
(Definitions 3.1, 3.2, **Lemma 3.3 with its proof**), the end of Section B.2 (proof of the list bound
(38)), Theorem 9.3 and Corollary 9.4 (statements: deterministic complete list decoding above Johnson
in every characteristic). [CFW26]: Definitions 3.3, 3.4, 3.16, 3.17, 3.19, Lemma 3.18 (statement),
Theorem 6.3, Construction 6.4, **Lemma 6.6 with its proof**. [SG26]: Definition 2.20, Lemma 2.21
(statement), Section 5.5 (5.5.1, 5.5.2, Table 1, Lemma 5.10 statement), Theorem 6.6 (statement),
Definition H.3; Appendices F and I not read. [ACFY24]: Definition 4.1 (restriction to smooth
domains), Theorem 4.8 (statement), Definition 4.9, Lemma 4.10 (statement and first part of the
proof), Corollary 4.11, Theorem 7.5 (statement). [CMS19]: Definitions 8.3 to 8.5, Theorem 8.6, start
of Section 8.5.2. [Hab-LDR]: Section 5.2 ((29) to (31), Lemma 2 with proof), Section 6.1 ((33) to
(35), Lemma 4 with proof).

**Read for the calculator's revision 8** (`soundness/src/yugen_soundness/dkt26.py`, condition C-3 of
`docs/johnson-row-referee-2.md`; 2026-11-19; text layer extracted to the session's scratch directory
outside every repository and deleted afterwards): [DKT26] Section 3.1 (equations (2) to (5),
Definitions 3.1, 3.2, **Lemma 3.3 statement with (6)**: constants, list `floor(n / A)`, count
`floor(l C(n, 2)/(A - 1))`); Section 4.2 (definitions of `Psi_D`, **(33)**, **(34)**, Lemma 4.3
statement with (35) and the explanation of its three terms); Section 4.3 (**Theorem 4.4 statement
with (36) to (39)** and its proof paragraph, the remark on `D = 0`); end of Section B.1 ((103) to
(105)); Section B.2 (Proposition B.1 with proof, the thresholds `C_spec`, `C_jet`, `C_Z` and
`B_jet = ceil(C_jet) - 1`, `B_Z = ceil(C_Z) - 1`, (109), the list bound (38)); **Section B.3** (the
closed form (39)); Section 6.2 (Lemma 6.5 with proof, Corollary 6.6 statement and proof). The
brackets of (36) and (37), lost in the text layer, were taken from B.2's
`B_jet = ceil(C_jet) - 1`, `B_Z = ceil(C_Z) - 1` and checked against the referees' `B_jet = 29`,
`B_Z = 294` at `m = 10`, rate 1/8; (36)'s `m = max(ceil(sqrt(rho_-) / (2 eta_0)), 3)` follows from
B.2's "the definition of m gives m eta_0 >= sqrt(rho_-)/2" (a typeset-page check is still owed, as
for C-14's (36), (39)).

### 1.1c Read for `docs/qrom-compilation.md`, `docs/zk-quantum.md`, `docs/whir-additive-soundness.md` (2026-11-19)

Text layer extracted locally to a temporary directory outside every repository.

- [CMS19], further sections: 3.3 (zero knowledge in the QROM: `(h, pi)` against `(h[mu], pi)`, `h`
  the whole function), 4 (Definitions 4.1, 4.6 to 4.8, Lemma 4.9: oracles `{0,1}^m -> {0,1}^n` of any
  sizes), 5.1 (Definitions 5.1, 5.2), 6.1 to 6.3 (Merkle trees with the symbols as leaves, `Expand`,
  `Extract`, Lemmas 6.4, 6.5, Definition 6.3), 7 (Theorem 7.1, Lemmas 7.3, 7.4), 8.1 to 8.6 in full
  (Definitions 8.1 to 8.5, Theorem 8.6, Propositions 8.11, 8.12, Lemmas 8.7, 8.8, 8.13, Claims 8.9,
  8.10, Section 8.5.2, Section 8.6). Not read: the proofs of Lemmas 5.9, 5.10, 5.13; Appendices.
- [CY-book] (version 1.2 dated March 25, 2026, CC BY-SA 4.0; a copy fetched by an earlier session,
  not among the lead architect's files), further sections: Claims 3.4.1, 3.4.2 with proofs; Lemma
  17.3.1, Claims 17.3.2, 17.3.3; Section 18.1 (Merkle scheme, Remarks 18.1.3 to 18.1.8); Lemmas
  18.6.1, 18.6.3, Remark 18.6.2, Constructions 18.6.4, 18.6.5, Remark 18.6.9; Construction 25.1.1;
  Theorem 26.2.1 with Construction 26.2.2 and the proof's hybrids.
- [BCS16], further: Definition 3.3, Lemma 3.4 with its proof (Facts 1, 2), Theorem 7.1 statement.
- [ACFY24], further: Definitions 4.5 to 4.7, Theorem 4.8 (statement); the rest as in 1.1.
- [CWYZ26], further: Sections 1.1 (definition of the affine combiner and of its MCA error with
  agreement loss; Theorem 1.1; the leanVM remark), 5 (equal-degree combiner (5.1), linear
  constraints, Theorem 5.1 statement, Theorem 5.2 with its proof: `r` interleaved rounds give degree
  bound `d + r`), and Section 6's claims as stated in the abstract (worst-case `Omega(n/q)` without
  agreement loss). Not read: Sections 2 to 4 (the proof of Theorem 1.1), 6, 7, Appendix A.
- [BGKTTZ23] Alexander R. Block, Albert Garreta, Jonathan Katz, Justin Thaler, Pratyush Ranjan Tiwari,
  Michał Zając. *Fiat-Shamir Security of FRI and Related SNARKs.* Cryptology ePrint Archive, Paper
  2023/1071 (copy dated February 15, 2024). Read: Theorem 3.15 (their restatement of the BCS,
  CMS19, COS20 guarantees for `H: {0,1}^* -> {0,1}^kappa`), Appendix A.4 (end-to-end caveat). Used
  as a secondary statement only.
- [DKT26]: Theorem 4.4 statement re-read (any field, any distinct evaluation points); cited in
  `whir-additive-soundness.md` 5 for what is not used.
- Attema, Fehr, ePrint 2021/1259: title page; not used here. Sharp, Grubbs, ePrint 2026/2615: used from
  revision 2 of `qrom-compilation.md` and `zk-quantum.md` (2026-11-19); sections read in 1.1d.

### 1.1d Third pass: the six papers added on 2026-11-19 afternoon (citation audit, findings C-14 to C-21)

Text layer extracted locally (pypdf) to a temporary directory outside every repository; authors,
titles and dates taken from each paper's first page. Formulas read from the text layer.

**[DKT26]** (entry in 1.1b). Further read in this pass: Sections 1, 1.1, 1.2 (Tables 1, 2), 3.1
(Definitions 3.1, 3.2, Lemma 3.3), 4.2 (Lemma 4.3 statement and the paragraph after it), 4.3
(Theorem 4.4 with its proof paragraph), 6 in full (Remark 6.1, Lemma 6.2 with proof, Corollaries
6.3, 6.4, 6.6, 6.7 with proofs, Lemma 6.5), 7.1, 7.2, Appendix B: end of B.1, B.2 (Proposition B.1
with proof), B.3 (closed constants); the AI methodology statement. Not read: Sections 2, 3.2 to 3.5,
5, 8, 9, 10, the body of B.1, Appendices A, C to H. Plonky3's "Theorem 5.12, App. B.1–B.2" is the
numbering of an earlier version, cited in the copy as [DKT26b]. The copy states that its bounds are
formalized in Lean (ArkLib); not checked here.

**[ethSTARK]** Eli Ben-Sasson, Dan Brownstein, Dan Carmon, Lior Goldberg, David Levit, Dori Medini,
Alon Shtaierman, Eylon Yogev. *ethSTARK Documentation – Version 1.2.* Cryptology ePrint Archive,
Paper 2021/582. The copy is dated July 2023 (52 pages); StarkWare Industries. Read: contents,
Theorem 5 (statement) and the bound on `eps_1` with Remark 6, Section 6.3 (Theorem 6 with proof),
Section 7.1 (Theorems 7, 8, Claim 1, Corollary 3, Section 7.1.1). Not read: Sections 1 to 5, the rest
of 6.1, 6.2.

**[BGKTTZ23]** (entry in 1.1c). Further read in this pass: abstract; Theorem 3.15; Section 4.1
(Theorems 4.1, 4.2, Corollaries 4.3, 4.4, Remark 4.5); Theorem 5.11 (statement and the start of its
proof); the related-work paragraph on Fiat-Shamir (Section 1); Appendix C (the less sound variant of
OPlonky and the attack of [AFK22] on parallel repetition). Not read: Sections 2, 3 except 3.15, 4.2
onward, 5 except 5.11, 6, 7, the other appendices.

**[CWYZ26]** (entry in 1.1b). Further read in this pass: Sections 1.1, 1.2, 2 (first page), 4.1
(equation (4.1), Lemma 4.2 with the start of its proof), Theorem 4.10 (equation (4.13)) and the
example after it, Section 5 (Theorems 5.1, 5.2 with proofs, Remark 5.3), Section 6 (Propositions 6.1,
6.2 with proofs, 6.3 statement and start of proof). Not read: Sections 3, 4.2 to 4.4, 7, Appendix A.
Fourth pass (calculator revision 6, `soundness/affine.py`): Section 4.1 again ((4.1), Lemma 4.2 and its
proof through (4.5)), the definition `B := ceil((sqrt(rho) + eta/2) n) - 1` in the proof of Theorem 1.1,
Theorem 4.10 with (4.13), the example after it, Remark 5.3; both worked examples reproduced (123.25 and
125.42 bits).

**[AF21]** Thomas Attema, Serge Fehr. *Parallel Repetition of (k1, ..., kmu)-Special-Sound
Multi-Round Interactive Proofs.* Cryptology ePrint Archive, Paper 2021/1259. The copy is "Version 3 -
September 6, 2023"; no venue stated on the pages read. (Not the Attema-Fehr-Klooß paper; Klooß is
thanked in the acknowledgements.) Read: abstract, Sections 1.1 to 1.3, Theorem 4, the opening of
Section 5. Not read: Sections 2, 3, 4 (proofs), 5 (Theorem 5 and proofs).

**[SG26]** Chad Sharp, Paul Grubbs. *Faster and Smaller Anonymous Credentials from Standardized
Signatures* (the GordieHowe system). Cryptology ePrint Archive, Paper 2026/2615 (the copy states no
date or venue). **Fifth pass (2026-11-19, calculator revision 9, `decision-qrom-counting.md`)**: Theorem 6.6 (2)
and Section 6.3 (page 58), Definitions H.2, H.3 and the text after it (page 128), Definition H.4, Lemma H.5 (page
129), read **from rendered page images** (the quantifier "for every t and every (t, 0)-adversary"). Read: abstract; contents; Section 5.5 (5.5.1, 5.5.2, Lemma 5.10 statement, Table 1,
Definition 5.11); Sections 6.1 (Definitions 6.1 to 6.3), 6.2 (Protocol 6.5), 6.3 (Theorem 6.6 and the
text after it); Table 3; Section 8.4; Definition I.1. **Fourth pass (2026-11-19, for revision 2 of
`qrom-compilation.md` and `zk-quantum.md` and calculator revision 6)**: Section 6 in full again
(Definitions 6.1 to 6.4, the text of 6.2, Protocol 6.5, Theorem 6.6 parts (1) to (5) and pp. 59 to 60);
Definitions 2.16 to 2.20, 2.22, Lemma 2.21 (statement); Definition H.6; Section 5.4.2 (Lemma 5.8) and
5.4.3 (Lemma 5.9) for the comparison with O-8 and O-10; Appendix I.1 in full (Definition I.1, Lemma
I.2, the oracle's domain, hash functions, challenge inputs, leaves, samplers, Merkle trees, prover and
verifier); **Appendix I.2 in full with the proof bodies** (Theorem I.3 and proof, Protocol I.4,
Theorem I.5 and its proof, Theorem I.6 with Lemmas I.7, I.8 and their proofs); Appendix I.3: Protocol
I.9 and Theorem I.16 with its proof (Lemmas I.10 to I.15 by the statements quoted in those proofs
only). What was taken from each: Theorem 6.6 (2) with Definition I.1 for condition Q of both systems
(`qrom-compilation.md` 3 to 5; `soundness/spbcs.py`); Protocol 6.5 and Section I.1 for the
transcript specification (`qrom-compilation.md` 2); Theorem 6.6 (3), (4), Definition I.1's
`eps_leaf`, Section 8.4 and the hybrid step of Theorem I.5's proof (step 2 (ii)) for
`zk-quantum.md` 2.1, 3; Theorem I.16's ROM part for finding Q-5. Not read: Sections 1 to 5 except
the parts named, 7, 9; Appendices A to H except H.6; Appendix F (Lemmas F.2, F.4, Theorem F.6);
Lemmas I.10 to I.15 in full; Appendix I.4; Appendix J.

### 1.1e The BLAKE3 sources (obligation H-1 of `docs/decision-b-merkle-hash.md`, 2026-11-19)

Supplied by the lead architect in the reference directory: `blake3-spec.pdf` (from the
BLAKE3-team/BLAKE3-specs repository) and `draft-aumasson-blake3-00.html`. How read: the page
renderer was not available, so the PDF's text layer (31 pages) was extracted locally with `pypdf`
and the HTML stripped to text, both into a temporary directory outside every repository; both were
read **in full**. Superscripts are flattened in the PDF's text layer: the exponents of Table 4 and
of bound (2) below are this project's reading of the flattened text (for example "244" read as
`2^44`) and should be confirmed on the typeset page. Authors, titles, dates and versions are taken
from the documents themselves.

**[B3]** Jack O'Connor, Jean-Philippe Aumasson, Samuel Neves, Zooko Wilcox-O'Hearn, *BLAKE3: one
function, fast everywhere*, specification paper, "Version 20211102173700" (first page),
https://blake3.io. (The Internet-Draft cites this document as "[BLAKE3] ... January 2020"; the
version read here is the one dated 2021-11-02 on its first page.)

**[B3-ID]** J-P. Aumasson (Ed.), S. Neves, J. O'Connor, Z. Wilcox, *The BLAKE3 Hashing Framework*,
Internet-Draft `draft-aumasson-blake3-00`, Internet Engineering Task Force, published 20 July
2024, expires 21 January 2025, intended status Informational. An Internet-Draft is "work in
progress" (its own Status of This Memo) and this revision has expired by its own date; whether a
later revision exists was not checked. Where [B3-ID] and [B3] differ, [B3] and the reference code
govern (discrepancies D-1 to D-4 below).

**Security claims, verbatim where quoted.**

| Claim | Where | Text |
|---|---|---|
| Overall level | [B3] Section 1, p. 3 | "BLAKE3 has the same 128-bit security level and 256-bit default output size as BLAKE2s." |
| Every goal at 128 bits | [B3] Section 4.1 | "BLAKE3 targets 128-bit security for all of its security goals. That is, 128-bit security against (second-)preimage, collision, or differentiability attacks." Rationale referred to [B3] reference [3], Section 2 (Aumasson, *Too much crypto*; not read here) |
| Output length | [B3-ID] Section 7 | "BLAKE3 with an output of at least 32 bytes targets a security level of at least 128 bits for all its security goals." |
| Collision resistance | [B3] 4.1 | 128 bits (the generic birthday level of a 256-bit output). No higher level is claimed for longer outputs |
| Preimage and second preimage | [B3] 4.1 | 128 bits, **not** the 256 bits generic for a 256-bit output |
| Keyed mode (`keyed_hash`) | [B3] 4.1, 6.1; [B3-ID] 1.1 | PRF and MAC use; the claim is the same 128-bit level; "The key length is nevertheless 256 bits, as an extra defense layer against weakly chosen keys, key material leaks, and potentially multi-target attacks" ([B3] 4.1) |
| Key derivation (`derive_key`) | [B3] 2.3, 6.2, 7.8; [B3-ID] 1.1 | KDF use; the context string "should be hardcoded, globally unique, and application-specific" and must not hold variable data ([B3] 6.2); no separate level stated, so the 128-bit level of 4.1 applies |
| Extendable output (XOF) | [B3] 2.6; [B3-ID] 4.3, 5.4 | outputs of any length; "in contrast to BLAKE2 and BLAKE2X, BLAKE3 does not domain separate outputs of different lengths. Shorter outputs are prefixes of longer ones" ([B3] 2.6). No level above 128 bits is claimed for any output length |
| Random-oracle use | [B3-ID] 1.1 | the hash mode "can be used whenever a preimage- or collision-resistant hash function is needed, and to instantiate random oracles in cryptographic protocols" |
| Quantum attackers | neither document | **no statement**: the word "quantum" does not occur in either text (searched) |
| Indifferentiability of the compression function | [B3] 4.2 | the full 16-word output "causes the BLAKE3 compression function to no longer be indifferentiable, unlike its predecessor" (cites [22], Luykx, Mennink, Neves); "the truncated compression function used in every compression except the root nodes is indifferentiable" (proof "very similar" to [22]) |
| Indifferentiability of the mode | [B3] 4.3 | the mode meets the conditions of Daemen, Mennink, Van Assche ([13]): subtree-freeness (the ROOT flag), radical-decodability, message-completeness; for outputs of 256 bits or fewer, by [13] Theorem 1 with [22], the differentiability advantage of a distinguisher of total complexity `q` is bounded by `C(q,2)/2^256 + C(q,2)/2^512 + C(q,2)/2^256 + q/2^128` (equation (2), read from the text layer; the last two terms are attributed to the truncated compression function [22]). For the full-length output the feed-forward is argued to serve the purpose of truncation (no theorem stated). All of this is in the ideal-cipher / ideal-compression-function model |

**The compression function** ([B3] 2.2, 4.2; [B3-ID] 3). Inputs: chaining value `h0..h7` (256
bits), message block `m0..m15` (512 bits), 64-bit counter `t`, block length `b`, flags `d`. State
`v0..v15` = `h0..h7`, `IV0..IV3`, `t0, t1, b, d`; the IV constants are BLAKE2s's (= SHA-256's,
[B3-ID] 2.3). **7 rounds** ("The compression function applies a 7-round keyed permutation",
[B3] 2.2; "must do exactly 7 rounds", [B3-ID] 3.3); "The round function is the same as in
BLAKE2s": `G` on the four columns, then the four diagonals, each `G` with additions modulo `2^32`,
XOR and rotations by 16, 12, 8, 7. Changes from BLAKE2s stated by the designers: rounds **7
instead of 10** ([B3] Section 1: "Fewer rounds in the BLAKE2s-based compression function (7
instead of 10)"; "BLAKE3 reduces the number of rounds in the compression function from 10 to 7");
the message schedule is **one fixed permutation** applied after each round, replacing BLAKE2's 10
distinct permutations ([B3] 2.2 Table 2, 7.4; chosen among 12 candidates for the lowest 3-round
differential trail probability, `2^-21` against `2^-13`); BLAKE2's `f0`, `f1` flags replaced by the
`b` and `d` inputs ([B3] 4.2); finalisation returns 16 words, `h'_i = v'_i xor v'_(i+8)` and
`h'_(i+8) = v'_(i+8) xor h_i`, so the feed-forward is applied to the second half only ([B3] 2.2,
4.2, 7.3); the output is truncated to 8 words for chaining values ([B3] 2.2).

**Modes, flags, tree, counter** ([B3] 2.1, 2.3 to 2.6, 7.5 to 7.7; [B3-ID] 2.5, 4).
Flags (Table 3; [B3-ID] 2.5): `CHUNK_START` 1, `CHUNK_END` 2, `PARENT` 4, `ROOT` 8, `KEYED_HASH`
16, `DERIVE_KEY_CONTEXT` 32, `DERIVE_KEY_MATERIAL` 64; `d` is their sum. Modes ([B3] 2.3):
`hash` (key words = IV, no mode flag), `keyed_hash` (key words = the 256-bit key, `KEYED_HASH` on
every compression), `derive_key` (stage 1: the context string hashed from the IV with
`DERIVE_KEY_CONTEXT` on every compression; stage 2: the key material hashed with the first 8
output words of stage 1 as key words and `DERIVE_KEY_MATERIAL` on every compression). Tree
([B3] 2.1, 2.4, 2.5): input split into 1,024-byte chunks, each a sequence of 64-byte blocks
chained through the truncated output, the last block zero-padded with `b` its true length; first
block `CHUNK_START`, last block `CHUNK_END`, a single-block chunk both; a chunk that is the whole
input sets `ROOT` on its last block; otherwise chunks are leaves of a binary tree ("left subtrees
are full", "left subtrees are big") whose parent nodes are **one compression each**, key words as
chaining input, message = left child's CV || right child's CV, `t = 0`, `b = 64`, `PARENT` (and
`ROOT` at the root). Counter: the chunk index for every block of a chunk, 0 for parents, and
incremented over repeated root compressions for extendable output ([B3] 2.4 to 2.6, 7.5: "not
strictly necessary for security"). **Domain separation the mode itself gives** ([B3] 7.7):
"The ROOT and CHUNK_START domain flags are strictly necessary for security" (ROOT separates the
root from all other nodes and the final block of a root chunk from all other blocks: length
extension; CHUNK_START "separates chunks from parent nodes" and a caller-provided IV or key from
CVs computed inside a chunk: collisions); PARENT and CHUNK_END are "not strictly necessary" and
included to be conservative. So inside one BLAKE3 evaluation chunks and parent nodes are
separated; **two separate BLAKE3 evaluations of 64-byte inputs** (an application's leaf and an
application's node) carry identical flags (`CHUNK_START | CHUNK_END | ROOT`) and are separated only
by their key words and mode flag. [B3] 7.8 adds that a related algorithm should change the IV
constants (as SHA-512/256 does); that would no longer be BLAKE3.

**Compressions per input** (follows from [B3] 2.4, 2.5; checked with a minimal implementation
written from [B3] 2.2 to 2.5 in a temporary directory, which reproduces [B3-ID] Appendix B.1 and
B.2 and the `blake3` crate's test vector for "foo", `blake3-1.8.7/src/test.rs`
`test_hex_encoding_decoding`): an input of `1 <= L <= 1024` bytes costs `ceil(L / 64)`
compressions (64 bytes: one, with `d = CHUNK_START | CHUNK_END | ROOT` plus the mode flag; 65 to
128: two; 1,025: 18, that is 17 block compressions and one parent). [B3-ID] B.1 shows the
4-byte input "IETF" as one compression with flags `0x0b`; B.2 shows a two-chunk root parent as
one compression with flags `0x0c`.

**Discrepancies of [B3-ID] against [B3]** (found here; the draft's own vectors are unaffected):
D-1, Section 1.2 says a chunk is "16 consecutive 16-byte blocks" (64-byte blocks in its Section 4.1
and in [B3] 2.4). D-2, the pseudocode of Section 3.3 calls the last `G` of a round with
`m[15], m[15]`; [B3] 2.2 (`G_i` takes `m_(2i)`, `m_(2i+1)`) and the reference code
(`portable.rs`, `schedule[14], schedule[15]`) use `m14, m15`; the draft's two examples cannot
detect this (their message words 14 and 15 coincide in every round), and on a general block the
two readings differ (checked). D-3, Appendix B.2 is titled "keyed_hash mode" but its trace starts
from the IV with flags `0x01`, `0x02`, `0x0c` (no `KEYED_HASH`); its value is the plain `hash` of
the input (reproduced), not a keyed hash. D-4, Section 3.1 says the block length is "at least 1",
while [B3] 2.4 allows the empty input (one empty block).

**Cryptanalysis the designers rely on, cited by the specification and NOT read here.** [B3] 4.4:
"The round reduction from 10 to 7 rounds is based on existent cryptanalysis, along with novel
research. High confidence in the security of 7 rounds follows from cryptanalysis efforts over 10
years, first on BLAKE [4, 6, 10, 16, 21, 25, 26] and then on BLAKE2 [17-19]." Table 4 of [B3]
(k.p. = keyed permutation, c.f. = compression function; complexities read from the text layer):

| Primitive | Type | Rounds | Complexity | [B3] ref. |
|---|---|---|---|---|
| BLAKE-256 k.p. | boomerang | 7 | `2^44` | [6], [19] |
| BLAKE-256 k.p. | boomerang | 8 | `2^198` | [19] |
| BLAKE-256 k.p. | differential | 4 | `2^192` | [16] |
| BLAKE-256 k.p. | differential | 6 | `2^456` | [16] |
| BLAKE-256 k.p. | impossible differential | 6.5 | not given | [18] |
| BLAKE-256 c.f. | boomerang | 7 | `2^242` | [10] |
| BLAKE-256 c.f. | near collision (152 of 256 bits) | 4 | `2^21` | [25] |
| BLAKE-256 c.f. | near collision (232 of 256 bits) | 4 | `2^56` | [4] |
| BLAKE-256 c.f. | preimage | 2.5 | `2^241` | [21] |
| BLAKE-256 c.f. | pseudo-preimage | 6.75 | `2^253.9` | [17] |
| BLAKE2s k.p. | boomerang | 7.5 | `2^184` | [19] |
| BLAKE2s k.p. | impossible differential | 6.5 | not given | [18] |
| BLAKE2s k.p. | rotational | 4 | `2^489` | [18], [20] |
| BLAKE2s c.f. | boomerang | 5 | about `2^86` | [10], [18] |
| BLAKE2s c.f. | pseudo-preimage | 6.75 | `2^253.8` | [17] |

The designers' own trail search ([B3] Table 5, "Best differential trail probabilities ...
respecting their constraints on inputs to the keyed permutation") gives, for BLAKE3, `2^-52` for
3.5 rounds of the keyed permutation and `2^-32` for 2.5 rounds of the compression function; their
footnote 2 says the search is "Optimal under certain assumptions, which are not entirely correct,
cf. [23]". Their argument for 7 rounds against the boomerang results: "such attacks do not present
a threat to BLAKE3, considering its input constraints on the compression function (that is, the IV
constants), plus the 128-bit security target"; and [3] "pleads in favor of reduced round values,
arguing that BLAKE2s and BLAKE2b would be as safe with 7 and 8 rounds, respectively." **No entry of
Table 4 is an analysis of BLAKE3 itself**; the newest cited work is from 2015. Cryptanalysis of
BLAKE3 published after the specification's version is not covered by these two documents and was
not searched.

Full references as printed in [B3] (pp. 28 to 31), to be obtained by the lead architect:

- [3] Jean-Philippe Aumasson. Too much crypto. In Real World Crypto, 2020. ePrint 2019/1492. (Rationale for the 128-bit target, Section 2, and for 7 rounds.)
- [4] J.-P. Aumasson, J. Guo, S. Knellwolf, K. Matusiewicz, W. Meier. Differential and invertibility properties of BLAKE. FSE 2010, LNCS 6147, pp. 318–332, Springer 2010. doi:10.1007/978-3-642-13858-4_18.
- [5] J.-P. Aumasson, S. Neves, Z. Wilcox-O'Hearn, C. Winnerlein. BLAKE2: simpler, smaller, fast as MD5. ACNS 2013, LNCS 7954, pp. 119–135, Springer 2013. doi:10.1007/978-3-642-38980-1_8. (BLAKE2s's 10 rounds and its claims.)
- [6] D. Bai, H. Yu, G. Wang, X. Wang. Improved boomerang attacks on round-reduced SM3 and keyed permutation of BLAKE-256. IET Information Security 9(3):167–178, 2015. doi:10.1049/iet-ifs.2013.0380.
- [10] A. Biryukov, I. Nikolic, A. Roy. Boomerang attacks on BLAKE-32. FSE 2011, LNCS 6733, pp. 218–237, Springer 2011. doi:10.1007/978-3-642-21702-9_13.
- [16] O. Dunkelman, D. Khovratovich. Iterative differentials, symmetries, and message modification in BLAKE-256. ECRYPT2 Hash Workshop, 2011.
- [17] T. Espitau, P.-A. Fouque, P. Karpman. Higher-order differential meet-in-the-middle preimage attacks on SHA-1 and BLAKE. CRYPTO 2015, Part I, LNCS 9215, pp. 683–701, Springer 2015. doi:10.1007/978-3-662-47989-6_33.
- [18] J. Guo, P. Karpman, I. Nikolic, L. Wang, S. Wu. Analysis of BLAKE2. CT-RSA 2014, LNCS 8366, pp. 402–423, Springer 2014. doi:10.1007/978-3-319-04852-9_21.
- [19] Y. Hao. The boomerang attacks on BLAKE and BLAKE2. Inscrypt 2014, LNCS 8957, pp. 286–310, Springer 2014. doi:10.1007/978-3-319-16745-9_16.
- [20] D. Khovratovich, I. Nikolic, J. Pieprzyk, P. Sokolowski, R. Steinfeld. Rotational cryptanalysis of ARX revisited. FSE 2015, LNCS 9054, pp. 519–536, Springer 2015. doi:10.1007/978-3-662-48116-5_25.
- [21] J. Li, L. Xu. Attacks on round-reduced BLAKE. ePrint 2009/238.
- [23] N. Mouha, B. Preneel. Towards finding optimal differential characteristics for ARX: Application to Salsa20. ePrint 2013/328. (Limits of the designers' trail search.)
- [25] B. Su, W. Wu, S. Wu, L. Dong. Near-collisions on the reduced-round compression functions of Skein and BLAKE. CANS 2010, LNCS 6467, pp. 124–139, Springer 2010. doi:10.1007/978-3-642-17619-7_10.
- [26] J. Vidali, P. Nose, E. Pasalic. Collisions for variants of the BLAKE hash function. Inf. Process. Lett. 110(14-15):585–590, 2010. doi:10.1016/j.ipl.2010.05.007. (Cited in 4.4's list; not in Table 4.)

Mode and compression-function security, cited by [B3] 4.2, 4.3 (the basis of modelling
assumption MA-2' of the decision record; not read here):

- [7] G. Bertoni, J. Daemen, M. Peeters, G. Van Assche. Sufficient conditions for sound tree and sequential hashing modes. Int. J. Inf. Sec. 13(4):335–353, 2014. doi:10.1007/s10207-013-0220-y.
- [11] W. Choi, B. Lee, J. Lee. Indifferentiability of truncated random permutations. ASIACRYPT 2019, Part I, LNCS 11921, pp. 175–195, Springer 2019. doi:10.1007/978-3-030-34578-5_7.
- [12] J. Daemen, T. Dusenge, G. Van Assche. Sufficient conditions for sound hashing using a truncated permutation. ePrint 2011/459.
- [13] J. Daemen, B. Mennink, G. Van Assche. Sound hashing modes of arbitrary functions, permutations, and block ciphers. IACR Trans. Symmetric Cryptol. 2018(4):197–228. (Theorem 1 is the mode bound of [B3] 4.3.)
- [14] Y. Dodis, L. Reyzin, R. L. Rivest, E. Shen. Indifferentiability of permutation-based compression functions and tree-based modes of operation, with applications to MD6. FSE 2009, LNCS 5665, pp. 104–121, Springer 2009. doi:10.1007/978-3-642-03317-9_7.
- [22] A. Luykx, B. Mennink, S. Neves. Security analysis of BLAKE2's modes of operation. IACR Trans. Symmetric Cryptol. 2016(1):158–176. doi:10.13154/tosc.v2016.i1.158-176. (Indifferentiability of the truncated compression function.)

What `docs/decision-b-merkle-hash.md` takes from [B3] and [B3-ID]: the claims, the round count and
the changes from BLAKE2s, the flags and modes, the compressions per input, the mode's own domain
separation, and the cited cryptanalysis (its sections 6 to 9, findings H-1.1 to H-1.9).

**Table 4 above after revision 3** (1.1e-bis; `decision-b-merkle-hash.md` H-1.12). The rows stay
as [B3] prints them; the papers read change them as follows. The BLAKE-256 "c.f. preimage 2.5,
`2^241`" is a **hash-function** preimage ([GKNWW14] Table 1, [B2] 4.1). The two 6.75-round
pseudo-preimages are confirmed ([EFK15] Tables 1, 6) in the free-state model. The BLAKE2s k.p.
boomerang 7.5/`2^184` is confirmed at second hand ([TMC] 3.2). The 6.5-round impossible
differentials are confirmed ([GKNWW14] 5). The BLAKE2s k.p. rotational "4, `2^489`" is not in
[GKNWW14], which gives 7 rounds at `2^511` (Section 3, Table 1). The BLAKE2s c.f. boomerang
"5, about `2^86`" is confirmed for the rounds only, as a conditional estimate without complexity
([GKNWW14] 2). The BLAKE-256 k.p. differential "6, `2^456`" is `2^456` in [B2] 4.1 and `2^486` in
[GKNWW14] Table 1. The BLAKE-256 c.f. boomerang "7, `2^242`" agrees with [GKNWW14]; [B2] 4.1
describes it differently, and its correctness was questioned. The BLAKE-256 k.p. boomerangs
`2^44` and `2^198` are not in the papers read. The exponents read from the flattened text layer
agree with [EFK15], which prints base-2 logarithms, and with [TMC] and [GKNWW14] wherever they
overlap.

### 1.1e-bis Cryptanalysis cited by the BLAKE3 specification: four papers read (H-1 continued, 2026-11-19)

Supplied by the lead architect in the reference directory as `2019-1492.pdf`, `2013-322.pdf`,
`2015-515.pdf` and `2013-467.pdf` (the file names are ePrint numbers). How read: the page
renderer was not available, so the text layer of each PDF was extracted with `pypdf` into a
temporary directory outside every repository and read there. No file was copied into a
repository. Authors, titles, versions and venues are taken from the papers' own pages; where a
venue is not on the page, the source of the venue is named. Each paper is the one [B3] cites as
[3], [5], [17] and [18] (identified from the title and authors on its first page, against [B3]'s
reference list). Superscripts are flattened in the text layers. [EFK15] prints complexities as
base-2 logarithms; elsewhere the exponents were read from the context (for example
`2^(2w) = 2^64` for `w = 32`, [GKNWW14] 3).

**[TMC]** Jean-Philippe Aumasson, *Too Much Crypto*, "Version 20260706145800" (first page). The
file is ePrint 2019/1492 by its name and as [B3] [3] cites it ("In Real World Crypto, 2020"); no
venue is printed on the version read. **Read in full** (19 pages, Sections 1 to 6, the addenda
of 24 May 2021 and 6 July 2026, references). This is a later revision than the one [B3] cites;
the earlier text was not seen. The author is a BLAKE3 co-designer.
- Section 2: 128-bit security is "often acknowledged as sufficient"; "a 2^128-operations attack
  must remain fantasy"; comparing complexities above about `2^150` "is meaningless from a risk
  perspective". This is the rationale [B3] 4.1 points to for its 128-bit target.
- Section 3.2 (BLAKE2): BLAKE2b uses 12 rounds and BLAKE2s 10. Pseudo-preimages reach 7.5 rounds
  of BLAKE2b (`2^510.3`) and 6.75 rounds of BLAKE2s (`2^253.8`) [27 = EFK15], and "do not use the
  initial value defined in the specification"; "On the proper hash function, the best preimage
  attack applies to no more than 2.75 rounds". Boomerang distinguishers reach 8.5 rounds of
  BLAKE2b's keyed permutation (`2^474`) and 7.5 of BLAKE2s's (`2^184`) [36 = Hao]: "such
  distinguishers don't have much to do with the security of the hash function".
- Section 3.4 (SHA-3; reported, with its sources [34] Guo, Liao, Liu, Liu, Qiao, Song, ePrint
  2019/147 and [41] Li, Sun, EUROCRYPT 2019): practical collisions on 5-round SHA3-224 and
  SHA3-256; 4-round preimages on SHA3-224 (`2^207`) and SHA3-256 (`2^239`); on non-standard
  capacity 160, 6-round collisions (about `2^50`) and 4-round preimages (about `2^54`).
  KangarooTwelve uses 12 rounds. Nothing on SHA3-384 or SHAKE256.
- Section 4.4: four statuses, Analyzed, Attacked, Wounded and Broken. Section 4.5: on BLAKE2,
  "no meaningful progress since the differential analysis of BLAKE in 2011", and "BLAKE's and
  BLAKE2's internals are based on ChaCha's permutation". On SHA-256, only the opinion
  "Cryptanalysts seem to have given up on looking for collision attacks". **SHA-512 is not
  discussed.**
- Section 5.1: the margin is "the difference between the number of rounds known to be
  insufficient and the number of rounds specified"; Keccak was raised from 18 to 24 rounds after
  the zero-sum distinguishers on 18. Section 5.2: quantum (see `decision-b-merkle-hash.md`
  H-1.17).
- **Section 5.3, the proposals:** AES 9/10/11 (from 10/12/14); BLAKE2b 8 (from 12); **BLAKE2s 7
  (from 10)**; ChaCha 8 (from 20); SHA-3 10 (from 24). The criterion is "never be wounded, let
  alone broken", on "previous research and our cryptanalysis experience". There is no proposal
  for SHA-2.
- Addendum of 6 July 2026: BLAKE3 is "the strongest validation" ("its compression function
  reduces BLAKE2s' 10 rounds to 7"). The addendum is not independent evidence.

**[B2]** Jean-Philippe Aumasson, Samuel Neves, Zooko Wilcox-O'Hearn, Christian Winnerlein,
*BLAKE2: simpler, smaller, fast as MD5*. The file is ePrint 2013/322 by its name; no venue is
printed on the pages read. [B3] [5] and [GKNWW14] ref. 4 give ACNS 2013, LNCS 7954,
pp. 119–135, and [GKNWW14] ref. 5 names a "version 2013.01.29" at blake2.net. **Read in full**
(16 pages).
- Section 2.1: BLAKE2b uses 12 rounds and BLAKE2s 10, against BLAKE's 16 and 14; "it is unlikely
  that 16 and 14 rounds are meaningfully more secure than 12 and 10 rounds".
- Section 2.4: the initialisation `v8..v11 = IV0..IV3`, `v12..v15 = t0^IV4, t1^IV5, f0^IV6,
  f1^IV7`; no constants in `G`.
- Section 4: fewer rounds "does not imply lower security (it does imply a lower security
  margin)". Section 4.1: the core permutation comes from ChaCha. On the BLAKE hash function, the
  best attacks are 2.5-round preimages (`2^241` BLAKE-256, `2^481` BLAKE-512; Li and Xu). On
  components: a 6-round permutation distinguisher on BLAKE-256 (`2^456`, Dunkelman and
  Khovratovich) and an "8 rounds of the core permutation of BLAKE-512, with complexity 2^242"
  boomerang (Biryukov, Nikolić, Roy), whose correctness "recent work questions" (Leurent). "We
  expect attacks on reduced BLAKE with n rounds to adapt to BLAKE2 with n rounds".
- Section 4.2: the best collision-like results are near-collisions on 4 reordered rounds of the
  compression function.

**[EFK15]** Thomas Espitau, Pierre-Alain Fouque, Pierre Karpman, *Higher-Order Differential
Meet-in-The-Middle Preimage Attacks on SHA-1 and BLAKE*, "the full version of the article to
appear in the proceedings of CRYPTO 2015" (first page); ePrint 2015/515 by the file name.
[B3] [17] gives CRYPTO 2015, Part I, LNCS 9215, pp. 683–701. **Read**: Sections 1, 2, 3 and 5
in full, with Tables 1, 6 and 7; Section 4 (SHA-1) for its tables only.
- Table 1 (complexities as base-2 logarithms): BLAKE-512 preimage, 2.75 rounds, 510.3;
  BLAKE2b preimage, 2.75 rounds, 511; BLAKE-256 c.f. pseudo-preimage, 6.75 rounds, 253.9;
  BLAKE-512 c.f. pseudo-preimage, 7.5 rounds, 510.3; **BLAKE2s c.f. pseudo-preimage, 6.75
  rounds, 253.8**; BLAKE2b c.f. pseudo-preimage, 7.5 rounds, 510.3, and a weak class on all 12
  rounds (from [GKNWW14]).
- Section 5.1, "Terminology": a "pseudo-preimage on the compression function" "bypasses this
  initialization and requires complete freedom for the initial 16-word state, yet that does
  respect the finalization". This is the free-state model of `decision-b-merkle-hash.md` H-1.11.
- Section 5.2, Table 6: rounds 0.75 to 7.5 for BLAKE2s and BLAKE-256. Table 6's caption and its
  "e" column (7) do not match the text (end at round 7.5); the 6.75 of Table 1 and the text are
  used here. BLAKE2b is listed at 510.9 in Table 6 and 510.3 in Table 1.
- Section 5.3, Table 7: hash-function preimages on BLAKE-512 and BLAKE2b only (2.75 rounds).
  There is no hash-function preimage on BLAKE2s.

**[GKNWW14]** Jian Guo, Pierre Karpman, Ivica Nikolić, Lei Wang, Shuang Wu, *Analysis of BLAKE2*,
full version; the first page states "A shorter version appeared in J. Benaloh (Ed.): CT-RSA 2014,
LNCS 8366, pp. 402–423"; ePrint 2013/467 by the file name. **Read in full** (19 pages, Sections 1
to 7 and Appendices A to E).
- Section 2, "Our Attack Frameworks": the hash-function, compression-function, chosen-IV and
  permutation (block-cipher) models (the H, CF, CIV and KP of H-1.11). The importance of an
  attack "drops as one goes from the framework of hash functions to the one of permutations".
  Section 2, p. 4: the boomerangs on BLAKE's compression function do not extend trivially to
  BLAKE2, because six state words are fixed. With characteristics of similar probability, 5
  rounds (2 + 3) of BLAKE2s and 5.5 of BLAKE2b.
- Table 1 (its own results and those it reports): on BLAKE2s, the permutation has an impossible
  differential on 6.5 rounds and a rotational distinguisher on 7 rounds at `2^511`; the c.f. has
  **chosen-IV collisions on all 10 rounds at `2^64`**. On BLAKE-256 (reported), the hash has
  2.5-round collisions at `2^112` and preimages at `2^241` (Li and Xu); the c.f. has a 7-round
  boomerang at `2^242` and a 4-round near-collision at `2^56`; the permutation has an 8-round
  boomerang at `2^232` and a 6-round differential at `2^486`.
- Section 3: the rotational probability is about `2^-9.1` per `G` and `2^-73` per round. The
  internal-differential (squeeze) property gives a one-query distinguisher of the permutation for
  `2^w` keys at any round count, and c.f. collisions in `2^(2w)` if all inputs could be chosen.
  "In BLAKE2 the initialization once again prohibits this type of trivial attacks as
  IV0 ≠ IV1 ≠ IV2 ≠ IV3".
- Section 4: chosen-IV partial collisions (208 bits, `2^61`) and a weak class of preimages on all
  12 rounds of BLAKE2b; not applicable with the specified IV.
- Section 5: a 6.5-round impossible differential, with related keys, for BLAKE-256, BLAKE-512,
  BLAKE2s and BLAKE2b. It "heavily relies on" the ten `sigma_r` permutations.
- Section 6 (BLAKE2b; "applies to BLAKE2s as well, but the number of attacked rounds is
  lower"): c.f. differential on 4.5 rounds (`2^-494.5`), hash on 3.5 rounds (`2^480`),
  permutation on 5.5 rounds (`2^-928`).
- Section 7, Table 2 and conclusion: the absence of constants in `G` lets the keyed permutation
  "be fully attacked"; the compression function's security is "highly dependent on the right
  choice of IV". The tweaks taken together do not significantly change the hash or compression
  function's security, and BLAKE2 "has a very high security margin against all known attacks
  even after reducing the number of rounds by four". Section 1: "no universal method nor theory
  exists that can transitively prove the security of a symmetric primitive A obtained by
  modifying a primitive B".

**None of the four analyses BLAKE3.** Cryptanalysis published after them was not searched
(`decision-b-merkle-hash.md` section 11, task H-1e).

**Still to obtain** (claims of the margin table that rest on them; from [B3]'s list and the
papers above):

| Source | Rests on it |
|---|---|
| Y. Hao, *The boomerang attacks on BLAKE and BLAKE2*, Inscrypt 2014, LNCS 8957 ([B3] [19], [TMC] [36]) | the furthest keyed-permutation results: BLAKE2s 7.5 rounds, `2^184`; BLAKE2b 8.5 rounds, `2^474`; BLAKE-256 7 and 8 rounds, `2^44`, `2^198` |
| A. Biryukov, I. Nikolić, A. Roy, *Boomerang attacks on BLAKE-32*, FSE 2011, LNCS 6733 ([B3] [10]) | the 7-round BLAKE-256 c.f. boomerang `2^242`; the disagreement between [B2] 4.1 and [GKNWW14] about it |
| G. Leurent, *ARXtools: A toolkit for ARX analysis*, Third SHA-3 Candidate Conference, 2012 (as cited by [B2] ref. 22) | the doubt [B2] 4.1 records about Biryukov, Nikolić, Roy |
| O. Dunkelman, D. Khovratovich, ECRYPT2 Hash Workshop 2011 ([B3] [16]) | the 6-round BLAKE-256 permutation differential, `2^456` or `2^486` |
| J. Li, L. Xu, ePrint 2009/238 ([B3] [21]) | BLAKE-256 hash: 2.5-round preimage `2^241`, collision `2^112` |
| D. Khovratovich, I. Nikolić, J. Pieprzyk, P. Sokolowski, R. Steinfeld, FSE 2015 ([B3] [20]) | [B3]'s "rotational 4, `2^489`" on BLAKE2s |
| J.-P. Aumasson et al., FSE 2010 ([B3] [4]); B. Su et al., CANS 2010 ([B3] [25]); D. Bai et al., IET 2015 ([B3] [6]) | the near-collisions and the `2^44` boomerang |
| A. Luykx, B. Mennink, S. Neves, ToSC 2016(1) ([B3] [22]) | the indifferentiability of the truncated compression function in the ideal-cipher model (MA-2', H-1.14) |
| reduced-round cryptanalysis of SHA-512 and of Keccak at capacity 768 and 512 (none at hand) | the category 3 alternatives SHA-384, SHA-512 truncated, SHA3-384 and SHAKE256 (task H-1f) |

What `docs/decision-b-merkle-hash.md` takes from these four: revision 3, section 9b (H-1.10 to
H-1.17), and the corrections in sections 5, 6.1, 6.3, 7, 8, H-1.3, H-1.8, H-1.9, 10 and 11.

### 1.1f The NIST documents (calculator revision 7, 2026-11-19)

Supplied by the lead architect in the reference directory on 2026-11-19. Read from the PDF text
layer (extracted locally with `pypdf` into a temporary directory outside every repository); the
sections named below were read in full. Titles and dates are taken from the documents.

**[CFP]** National Institute of Standards and Technology, *Submission Requirements and Evaluation
Criteria for the Post-Quantum Cryptography Standardization Process*, call for proposals, December
2016 (`call-for-proposals-final-dec-2016.pdf`). Read: Section 4.A.5 "Security Strength
Categories" (pages 15 to 19: the five requirements, page 16 items 1 to 3 and page 17 items 4 and
5; footnote 2, the ordering; the metrics paragraph and MAXDEPTH, 2^40 to "no more than 2^96"
logical gates, page 17; the table of classical and quantum gate counts, page 18; footnotes 4 to
6, Grassl et al. and Zalka); Section 4.A.4 (signatures, `2^64` chosen messages); Section 4.A.6
(multi-key resistance "desirable").

**[FIPS204]** National Institute of Standards and Technology, *Module-Lattice-Based Digital
Signature Standard*, FIPS 204 (`NIST.FIPS.204.pdf`). Read: Section 4, Table 1 (the "collision
strength of c~" 128 / 192 / 256 and the claimed categories 2 / 3 / 5) and the paragraphs after
it; Appendix D.1 (a 384-bit SHAKE256 output made category-5 parameters "only meet category 4").

**[FIPS205]** National Institute of Standards and Technology, *Stateless Hash-Based Digital
Signature Standard*, FIPS 205 (`NIST.FIPS.205.pdf`). Read: Section 11, Table 2 and the text after
it (categories 1 / 3 / 5 for `n` = 16 / 24 / 32, claimed against the call for proposals);
Section 11.2.1 and 11.2.2 (the SHA2 instantiations: for categories 3 and 5, `H_msg`, `PRF_msg`,
`H` and `T_l` use SHA-512 while `F` and `PRF` keep SHA-256 truncated to `n` bytes).

### 1.1g Read for `docs/decision-security-profile.md` (2026-11-19)

From the reference directory, text layer. [CFP], [FIPS204] and [FIPS205] as in 1.1f (re-read: [CFP]
pages 16 to 19 including the recommendation on page 18 to focus on categories 1 to 3 and hedge
above 3; [FIPS204] Table 1 and Appendix D.1; [FIPS205] Section 11.2.2).

**[COSE-FN]** M. Prorock, O. Steele, H. Tschofenig, *FN-DSA for JOSE and COSE*, Internet-Draft
draft-ietf-cose-falcon-05, 1 November 2026 (`draft-ietf-cose-falcon-05.txt`). Read: Section 1,
Table 1 (FN-DSA-512: signature 666, public key 897, private key 1,281 bytes; FN-DSA-1024: 1,280,
1,793, 2,305), Section 3 opening.

**[GLS26]** F. Günther, V. Lyubashevsky, R. Schmidt, *FALCON with message recovery, a
specification*, Cryptology ePrint Archive, Paper 2026/420 (`2026-420.pdf`). Read: abstract
(Falcon-512 and Falcon-1024 at "NIST levels 1 and 5"); Section 1 and 1.1 (pages 1 to 2: "128 and
256-bit security levels", the parameters `lambda`, `gamma`); Algorithms 1 to 4 (pages 3 to 4);
Lemma 1 and its proof (pages 3 to 5).

Still not in the folder (claims stay "from memory"): FIPS 202, FIPS 203 (ML-KEM sizes and levels),
FIPS 206 / the Falcon specification, FIPS 180-4, Brassard-Hoyer-Tapp, RFC 9861 (TurboSHAKE).

### 1.1h Read for revision 2 of `docs/decision-security-profile.md` and `docs/qrom-compilation.md` 2.8 (2026-11-19)

From the reference directory, text layer, no new paper. **[FIPS204] Appendix D.1** (PDF page 64)
re-read and quoted in the record: a collision attack on SHAKE256 with a 384-bit output leaves
category-5 parameters at category 4; this is now the cited source of the record's category-4
label for 48-byte SHAKE256 digests (FIPS 202's capacity claim stays from memory, not verified).
**[SG26]** re-read for the builders' deviations: Definition 2.18 (page 13, `qry(theta)` "without
repetitions"), Section 6.2 with Protocol 6.5 (pages 56 to 57), Section 6.3 with Theorem 6.6 and the
text before and after it (pages 58 to 59), Appendix I.1 in full (pages 130 to 131: Definition I.1,
the oracle's domain, hash functions, challenge inputs, leaves, samplers, Merkle trees, prover and
verifier). Additionally from memory, marked where used: the Micciancio-Walter bit-security
measure, Grubbs-Maram-Paterson on ML-KEM anonymity, Zhandry's QROM collision bound (Lemma D (ii)
of `qrom-compilation.md` 2.8 rests on it until read), the sponge definition of FIPS 202 / the
Keccak reference (2.8 A-3 (a)).

### 1.1i Read for `docs/decision-b-transcript-hash.md` and `docs/decision-b-parallel-batching.md` (2026-11-19)

From the reference directory, text layer (extracted with `pypdf` to a temporary directory outside
every repository), no new paper. **[SG26]**: Definition 2.17 (series–parallel order), Definition
2.18, Definitions 2.19, 2.20 and the text after it, Lemma 2.21, Definition 2.24 (a), (b),
Definitions 2.25 (item 4), 2.26, Lemma 2.27 with its closing sentence (pages 14 to 17); Lemma 5.2
with its proof (page 37); the paragraph on the round errors of a GKR layer (page 45); Appendix I.1
"The oracle's domain", "Hash functions", "Challenge inputs", "Samplers" again (page 131). **[B3]**:
Sections 2.6, 4.1, 4.2, 4.3, 7.3 and 7.7 re-read for the passages quoted. **[TMC]** Section 3.3
(ChaCha) only. Searched without reading further, for "sumcheck" with "parallel", "shared" or "same
challenge": [CMS19], [DP24], [Hab-LDR], [ACFY24], [CFW26], [BGKTTZ23], [AF21]; nothing used from
them. From memory, marked where used: Coron, Dodis, Malinaud, Puniya (CRYPTO 2005); Bertoni,
Daemen, Peeters, Van Assche (EUROCRYPT 2008); the collision and preimage levels of SHA-256 and
SHAKE256 in NIST's documents.

### 1.1j The original sumcheck and GKR papers (2026-11-19, `docs/citation-check-lfkn-gkr.md`)

**[LFKN92]** Carsten Lund, Lance Fortnow, Howard Karloff, Noam Nisan. *Algebraic Methods for
Interactive Proof Systems.* Journal of the ACM 39(4):859-868, October 1992 (file
`146585.146605.pdf`, 10 pages). Read: all pages (text layer via pypdfium2; Lemma 4 on the rendered
page). Used: Lemma 4, p. 862 (two distinct polynomials of degree at most `r` over `Z_p` agree at a
uniform point with probability at most `r/p`), the per-step argument of every sumcheck analysis;
proof of Theorem 1 (2), pp. 863-864 (union over iterations, `N^3/p`). It states the permanent
protocol only, not the general sumcheck or a `d l / |F|` bound (Section 4, p. 865, attributes the
formula version to Babai-Fortnow and Shamir).

**[GKR15]** Shafi Goldwasser, Yael Tauman Kalai, Guy N. Rothblum. *Delegating Computation:
Interactive Proofs for Muggles.* Journal of the ACM 62(4), Article 27, August 2015, 64 pages
(file `2699436.pdf`; journal version of STOC 2008). Read: Sections 1.1, 2.5, 3 (3.1 to 3.3) from
the text layer via pypdfium2. Used: Lemma 2.5, p. 27:21, with Figure 2, p. 27:22 (sumcheck over any
finite field and any `H`, soundness `m d / |F|`) and its proof, inequality (3), pp. 27:22-23 (the
per-round `d / |F|`); Theorem 3.1, p. 27:25, and its proof in Section 3.3, pp. 27:31-32 (per layer
`6 m delta / |F|` for the sumcheck plus `m delta / |F|` for the line reduction of two claims,
p. 27:31; union over layers). Section 3.1 works over extensions of `GF[2]`. Not read: Sections 4 to
8.

### 1.1k BCIKS20, the folder copy (2026-11-19, `docs/CITATION-AUDIT.md` 1j)

**[BCIKS20]** Eli Ben-Sasson, Dan Carmon, Yuval Ishai, Swastik Kopparty, Shubhangi Saraf. *Proximity
Gaps for Reed–Solomon Codes.* Cryptology ePrint Archive, Paper 2020/654, the revision dated **July 3,
2021** on its first page (file `2020-654.pdf`, 61 pages; printed page = PDF page - 1). No venue is
stated in the copy. This revision is not the ECCC TR20-083 copy of May 30, 2020 that the documents
first read: it numbers remarks separately, so the affine-space theorem is **1.6** (ECCC 1.7), the
curve theorem **1.5** (ECCC 1.6), the extension-field remark **1.2** (ECCC 1.5); it adds an
acknowledgment of a corrected Polishchuk–Spielman citation (p. 6) and Appendix C (the inseparable
factor case, p. 57). Read from the text layer via pypdfium2, printed pages 2 and 19 also rendered:
Sections 1 (Definition 1.1, Theorem 1.2 with (1.1) and (1.2), p. 2; Remark 1.1, Corollary 1.3, p. 3;
Theorem 1.4 and Remark 1.2, p. 4; Theorems 1.5, 1.6, p. 5), 4 (Theorem 4.1, p. 13; Section 4.1, the
Berlekamp–Welch decoder, p. 14), 5 (Theorems 5.1, 5.2, p. 17; Lemma 5.3, p. 18; Section 5.2 with Steps
1 to 8, Claim 5.4 and (5.5), (5.6), p. 19; Proposition 5.5, p. 20; the inseparable-factor caveat,
p. 21), 6 (statements, Section 6.3 p. 30), 7 (statements), Conjecture 8.4 (p. 42), Appendix C (title
only). Used: Theorem 1.2 ((1.1) unique decoding `n/q`; (1.2) Johnson
`(k+1)^2 / ((2 min(eta, sqrt(rho)/20))^7 q)`), Theorem 1.5 (curves, `l eps`), Theorem 1.6 (affine
spaces, with the unique-decoding addendum), Remark 1.2 (challenges from an extension field),
Theorem 4.1 (lines, `|S| > n`, any `D`), Lemma 5.3 and Claim 5.4 (list size `< (m + 1/2)/sqrt(rho)`).
Files: as listed in `docs/citation-check-lfkn-gkr.md` 5.

### 1.2 Other sources the documents rely on (read by the documents' authors)

| Key | Source | What was read |
|---|---|---|
| [BCIKS20] | E. Ben-Sasson, D. Carmon, Y. Ishai, S. Kopparty, S. Saraf, *Proximity Gaps for Reed-Solomon Codes*, ECCC TR20-083 (ePrint 2020/654) | PDF fetched and converted to text: Theorems 1.2, 1.4, 1.6, 1.7, 4.1, Remark 1.5 (ECCC copy of May 30, 2020). **Superseded 2026-11-19**: the folder copy is the entry in 1.1k; numbers in the documents now follow it (C-41) |
| [CY-book] | A. Chiesa, E. Yogev, *Building Cryptographic Proofs from Hash Functions* (snargsbook.org) | Theorems 25.2.1, 26.2.1, 31.2.1 (local text extraction) |
| [Spo20] | N. Spooner, *Succinct Non-Interactive Arguments for Arithmetic Circuits*, PhD thesis, UC Berkeley, UCB/EECS-2020-182 | Section 5.10, 5.10.5 (the constant 6 of the lifting lemma) |
| [CFS17] | A. Chiesa, M. Forbes, N. Spooner, *A Zero Knowledge Sumcheck and its Applications*, ePrint 2017/305, arXiv 1704.02086v1 | body; Section 2.3 used |
| [Blueprint] | The Binius64 Blueprint of 2026-11-16 (`yugen-b-eval/upstream/papers/binius64-spec.txt`) | Sections 4.8, 4.9, 5.1 to 5.5, 6.3, 6.4, 7.2, 7.3, appendix D |
| [Zal99] | C. Zalka, *Grover's quantum searching algorithm is optimal*, Phys. Rev. A 60 (1999) | abstract |
| code | Plonky3 at `fe5e46d7` and `0d803737` (`whir/src/pcs/zk/`, `sumcheck/src/zk/`, `zk-codes/`, `binary-pcs/`, `binary-dft/`, `p3-security/`); leanVM at `84780fb4` (`crates/verifier/src/whir.rs`); Binius64 at `32ede490e8b6` (files listed in `binius-extension-challenges.md` and in `yugen-proof-b2/docs/zero-knowledge.md`) | source files as listed in each document's source table |

### 1.3 Sources cited but not read: claims that rest on them stay marked

To be obtained by the lead architect. Each line says exactly which claim waits for it. The four
papers of the second pass (2019/834, 2024/504, 2024/1571, 2024/1586) left this list; what they did
not settle is in `docs/CITATION-AUDIT.md` C-7, C-8, C-10, C-11. The third pass (2026-11-19, 1.1d)
removed DKT26, ethSTARK, 2023/1071 and CWYZ26 (`CITATION-AUDIT.md` C-14 to C-19); what they leave
open: P4 times `l` for curves (C-15), F5 (ours), WHIR on binary additive domains (C-10 (b)).

| Source | Claims that rest on it | Where |
|---|---|---|
| [HMH] (lifted BaseFold) | oracles of unequal size; the commitment-index rounds (neither [DP24] nor [Hab-LDR] covers them) | `binius-extension-challenges.md` R-8, 7 (d) |
| BCIKS20, Sections 6 and 7 (the proofs behind [Hab-LDR] Theorems 2 to 4: Proposition 5.5, Section 6.2, weighted correlated agreement) | the list-decoding errors of [Hab-LDR] (C-11) and the unique-decoding form of its Lemma 2 (C-12) | `binius-extension-challenges.md` 7 (d) |
| Attema, Fehr, Klooß, *Fiat-Shamir Transformation of Multi-Round Interactive Proofs*, TCC 2022, Part I, LNCS 13747, pp. 113–142 (as cited by ePrint 2023/1071; not supplied, not read); **not** ePrint 2021/1259 (C-20) | the general statement of the staggered attack; the attack itself is now cited to [BGKTTZ23] Appendix C (read) | `binius-extension-challenges.md` 7 (a), R-12 |
| A source for zero knowledge of salted Merkle trees against quantum, query-bounded distinguishers at salts as long as the digest (one-way-to-hiding or adaptive reprogramming: Unruh; Grilo, Hövelmanns, Hülsing, Majenz). For salts of twice the digest [SG26] Theorem 6.6 (3) is a published quantum statement (C-21) | the quantum form of Lemma M at the built 256-bit salts (C-8) | `zk-hiding-commitment.md` 4; `zk-composition.md` 6 |
| BCHKS (Ben-Sasson, Carmon, Haböck, Kopparty, Saraf; full version, Lemma 3.1, as cited by [DKT26] Proposition B.1) | the interpolant dimension count behind DKT26 Theorem 4.4 (P4, P5) | `soundness-method.md` P4; `binius-johnson-row.md` 0.1, 10 (G-2) |
| BCHKS, *On proximity gaps of Reed-Solomon codes*, STOC 2026, pp. 1157-1167, full version ePrint 2025/2055, **Theorem 4.6** (MCA above Johnson, every characteristic, as described by [DKT26] Section 1.2); Haböck, *A note on mutual correlated agreement for Reed-Solomon codes*, ePrint 2025/2110; Bordage, Chiesa, Guan, Manzur, ePrint 2025/2051 (all as cited by [DKT26]; not read) | candidate independent sources of the qualitative MCA statement the 107-query row needs; nothing rests on them yet (task: read BCHKS Theorem 4.6, acceptance in `binius-johnson-row.md` 8.4) | `binius-johnson-row.md` 0.1, 8.4 |
| V. Guruswami, M. Sudan, list decoding of Reed-Solomon codes (1999; cited from memory, as [GS99] in [DKT26]) | a second polynomial-time decoder for Lemma K's extractor (the first is [DKT26] Corollary 9.4, statement read) | `binius-johnson-row.md` 7.2 |
| [Dia24b] (row-batched FRI-Binius, cited by [Hab-LDR] Protocol 3) and S. Soukhanov, Hashcaster ([Sou24], cited by [DP24] Section 1.3) | cited through [Hab-LDR] and [DP24] only | `binius-extension-challenges.md` 3.2, 7 (d) |
| R. Lidl, H. Niederreiter, *Finite Fields* (Lemma 3.51, as cited by [DP24] Section 1.3) | invertibility of the Moore-type matrix in Theorem 2 (checked here on toy pairs only) | `binius-extension-challenges.md` 3.2 |
| Diamond, Gruen ([DG25], cited by [DP24] Theorem 2.4) | the tensor proximity gap behind [DP24] Proposition 4.21 | `soundness-method.md` 8.5c |
| VEIL [DHRR26], ePrint 2026/683 (cited in [CFW26] Section 1.4 as the one-time-pad wrapping approach) | whether the Binius64 wrapper follows it; nothing here rests on it | `yugen-proof-b2` |
| E. Ben-Sasson et al., *Aurora*, EUROCRYPT 2019; Zhang, Xie, Zhang, Song, *Virgo*, S&P 2020 | [Dia25] attributes its two techniques to them (Aurora Section 5, 5.1; Virgo Protocol 2); cited here through [Dia25] only | `zk-hiding-commitment.md` 7, 7a |
| N. Katz, character-sum bound | M-3 as built (shared root): statistical closeness | `zk-system-a-gaps.md` 9.2 |
| Crites, Stewart 2025/2046; Diamond, Gruen 2025/2010 | P7 (what is disproved) | `soundness-method.md` P7 |
| Frigo, shelat 2024/2010; Gur, O'Connor, Spooner arXiv 2403.11941; Hyrax, Virgo, Spartan | literature survey rows only | `zk-masked-sumcheck.md` 10 |
| The earlier revision of 2026/391 implemented by the pinned Plonky3 | the code's numbering ("Construction 6.3", "Lemma 6.4", "Proposition 3.19", "Lemma 3.26", "Construction 9.7") | `CITATION-AUDIT.md` section 2 |
| The cryptanalysis and mode-security papers cited by [B3] (references [3], [4], [5], [6], [7], [10], [11], [12], [13], [14], [16] to [23], [25], [26]; full list in 1.1e) | the margin argument for 7 rounds (finding H-1.8) and the ideal-model basis of MA-2' (H-1.6); the exponents of [B3] Table 4 as read from the text layer | `decision-b-merkle-hash.md` 6, 9 |
| Cryptanalysis of BLAKE3 itself published after [B3]'s version 20211102 (not searched) | whether any result reaches 7 rounds of BLAKE3's compression function or keyed permutation (H-1.8) | `decision-b-merkle-hash.md` 9 |
| NIST SP 800-107 Revision 1 (security strengths of SHA-2: preimage 256 bits, collision 128 bits for SHA-256; **from memory**, not read) and FIPS 180-4 Section 5.1.2 (SHA-384 padding: 1,024-bit blocks, 128-bit length field; from memory) | the comparison of claimed preimage levels (H-1.3) and the one-compression SHA-384 node at category 3 (H-1.5) | `decision-b-merkle-hash.md` 9 |
| Brassard, Høyer, Tapp, quantum collision search (BHT), and Grover, quantum search (both **from memory**, as already in `soundness-method.md` 8.2) | the generic quantum figures `2^85` (collisions) and `2^128` (preimages) for a 256-bit output (H-1.3) | `decision-b-merkle-hash.md` 9 |

---

### 1.1l Read for `docs/design-private-tag-filtering.md` (2026-11-19)

**[BLMG21]** Gabrielle Beck, Julia Len, Ian Miers, Matthew Green. *Fuzzy Message Detection.* Cryptology
ePrint Archive, Paper 2021/089 (file `2021-089.pdf`, 38 pages; no venue stated in the copy). Text layer
via pypdfium2: §1, §2, definitions pp. 7 to 9 (Theorem 5), Figure 3 and Theorems 12, 13 (p. 14), §5.3,
Tables 1 to 3 and pp. 18 to 20 (Lewis's attacks), §8, §9.

**[LT21]** Zeyu Liu, Eran Tromer. *Oblivious Message Retrieval.* Cryptology ePrint Archive, Paper
2021/1256, revision of April 14, 2022 (file `2021-1256.pdf`, 66 pages; no venue stated). Text layer via
pypdfium2: abstract, §1.1, §2 Tables 1, 2, §3, §7.1, §7.2, Theorem 8.3, Conjecture 8.4, §10 Tables 3, 4,
§11, §12.

### 1.1m Cited in `docs/privacy-elsewhere-review.md` (anonymity of the KEM)

- [GMP22] Paul Grubbs, Varun Maram, Kenneth G. Paterson, "Anonymous, Robust Post-Quantum Public Key
  Encryption", Cryptology ePrint Archive, Paper 2021/708 (Eurocrypt 2022). **Published**; cited for
  ANO-CCA of the Fujisaki-Okamoto KEMs, as `yugen-spec` `REFERENCES.md` [GMP22] records.
- [MX23] Varun Maram, Keita Xagawa, "Post-Quantum Anonymity of Kyber", Cryptology ePrint Archive,
  Paper 2022/1696 (PKC 2023). **Published**; cited for the anonymity of ML-KEM, as `yugen-spec`
  `REFERENCES.md` [MX23] records.

## Part 2. Reliance table: document and section, result, source

| Document, section | Statement | Source and exact location | Label |
|---|---|---|---|
| `zk-masked-sumcheck.md` 1.2 | masked sumcheck: send `G`, verifier sends `rho`, sumcheck on a combination of `f` and a random `g` | [CFS17] Section 2.3 (full random `g`); [XZZPS19] Section 4.1, Construction 1 (small `g`, sumcheck on `f + rho g`, `rho` in `F*`) | Adapted: here `rho f + g`, so no challenge is excluded for zero knowledge; residual hand-off (variant R) |
| `zk-masked-sumcheck.md` 2 | the mask `a0 + sum_i g_i(x_i)`, `g_i` without constant term, `1 + l d` coefficients | [XZZPS19] Section 4.1, Construction 1 step 1; Theorem 3 | Published (the mask). Its paper works over a prime field (Protocol 2, Constructions 3, 4; a 254-bit prime field in the implementation, page 27); Theorem 3 states no condition on the characteristic and its proof asserts, without proof, that the `l d + 1` constraints are independent |
| `zk-masked-sumcheck.md` 2 | that mask does not hide a plain sum over `{0,1}^n` in characteristic 2 | [CFW26] Section 2.5, page 20 ("whenever char(F) = 2 the partial sums of that polynomial over the hypercube vanish in all but the last two rounds") and Section 1.2 | **Published** in [CFW26] (revision of 2026-11-16). Found here independently on 2026-11-19 before that text was read; the exact leak counts and the `d = 1`, `n >= 3` case are computations of this project |
| `zk-masked-sumcheck.md` 3, Theorem 1, Corollary A | a mask with `O(n d)` coefficients that is perfect over every finite field | [CFW26] Definition 6.1, Lemma 6.2 (mask polynomial `U_sigma`, uniform on consistent transcripts over every finite ring) | Related published result; ours is a different family: see Part 3, O-1 |
| `zk-masked-sumcheck.md` 3.4, Corollary B | Libra's mask is perfect under `eq` weights with reduced messages | [XZZPS19] Construction 1 for the mask | Original as far as checked (O-2) |
| `zk-masked-sumcheck.md` 7 | GKR layer blinding by a multiplier that vanishes on the cube | [XZZPS19] Section 4.2, equation (7): `Vdot_i(z) = Vtilde_i(z) + Z_i(z) sum_w R_i(z_1, w)`, `Z(z) = prod z_i (1 - z_i)`, `R_i` bivariate of degree 2; Construction 2 | Adapted: one dummy variable `y` with multiplier `y(1+y)` and blinder cells, because the claims here have a Boolean last coordinate (O-8) |
| `zk-hiding-commitment.md` 3, Lemma E (sufficiency) | uniform coefficients above the message hide `t` opened points when the domain is disjoint from the subspace on which the basis polynomial of the first random slot vanishes | [Dia25] Lemma 4.4 (pad at `2^l .. 2^l + kappa - 1`, domain `S^(0)` disjoint from `<beta_0..beta_{l-1}>`); Section 1.1 "Padding in the novel basis" | Published for that offset; Adapted: any aligned offset, interleaved lanes, the necessity direction and the count of leaking rows are O-3 |
| `zk-hiding-commitment.md` 3 (alternative) | randomness on the lowest coefficients hides `t` distinct points on **any** domain | [CFW26] Lemma 3.29 (error 0, "strong", any strong sampling set); the same placement in Binius64 (`layout.rs`) | Published; not what W-I uses: see CITATION-AUDIT finding C-2 |
| `zk-hiding-commitment.md` 3.2 | fold then encode equals encode then fold, with folded randomness | [CFW26] Claim 2.8 (informal), Lemma 3.34 | Published for the eq-fold; the affine-combiner excess rule is Original (O-4) |
| `zk-hiding-commitment.md` 3.3, Lemma O | out-of-domain answers hidden by the budget `t >= Q + o` | related: [CFW26] Section 9.2, Lemma 9.4 (private zero-evaders: `r_ood >= t_ood` dedicated pad coordinates and a random matrix) | Original as far as checked (O-3); [CFW26]'s route differs and is characteristic-free |
| `zk-hiding-commitment.md` 4, Lemma M | salted leaves: unopened digests replaced by uniform strings, advantage `q N / 2^s` | [BCS16] Section 3.2, Definition 3.3, Lemma 3.4 (salt of `2 lambda` bits, statistical privacy `n 2^(-lambda/4 + 2)` against unbounded distinguishers); [CFW26] Lemma B.2 (the same hybrid for query-bounded adversaries: `T 2^-kappa`) | Adapted: the query-bounded form with a salt of `s` bits; the argument is that of [CFW26] Lemma B.2 with the salt as the unpredictable part |
| `zk-hiding-commitment.md` 5, Theorem 1' | claim-level masks for abstract round spaces | none found | Original as far as checked (O-5) |
| `zk-hiding-commitment.md` 6.1, base case | fresh mask, mask-side claim, challenge, reveal `mask + c * secret`, target check and spot checks | [CFW26] Construction 7.2, Theorem 7.1, Lemma 7.3 (perfect HVZK; errors `eps_mca + Lambda eps_pil`, `(1 - delta)^t`) | Adapted: the mask is a column of the last oracle; [CFW26] Section 11 does the same ("the final oracle has one additional masking row") |
| `zk-hiding-commitment.md` 6.1, layout of W-I | masks and re-encoded randomness inside the rows of the main oracles | [CFW26] Section 11 (main block, auxiliary block, mask, seed; Construction 11.1), Section 1.2 second bullet | The published layout of the 2026-11-16 revision; W-I was built from the earlier layout as implemented in Plonky3 and arrives at the same idea. What differs is O-4 |
| `zk-hiding-commitment.md` 6.4, W-S | separate mask oracles | the pinned Plonky3 code only (an earlier version of [CFW26], not available) | Published as code; not in the copy of [CFW26] read |
| `zk-hiding-commitment.md` 7, Lemma F | no re-randomisation: `T >= Q 2^K` | related: [HK25] Section 2, page 5 (each fold halves the randomizer space; the group structure matters, footnote 3); [Dia25] Section 4.2 ("Avenues for improvement") | Original as far as checked (O-6) |
| `zk-hiding-commitment.md` 7a, W-M and Theorem W-M | pad the witness polynomial, commit a uniform polynomial of the same length, run the unmodified opening on the combination; simulator samples the combination and back-fills the mask's opened values | [Dia25] Construction 4.1, Theorem 4.3 and its simulator (steps 1 to 6), Lemmas 4.5 to 4.7; [Dia25] attributes the technique to Aurora Section 5.1 and Virgo Protocol 2 | **Adapted** from [Dia25]: the opening is the WHIR-style interleaved opening of section 1.3 instead of binary BaseFold; both polynomials share leaves; the pad sits at an aligned offset; `rho p + mk` is [Dia25]'s `alpha f + f'` |
| `zk-composition.md` 6; `zk-masked-sumcheck.md` 1.3 | honest-verifier zero knowledge of a public-coin IOP gives zero knowledge of the compiled non-interactive argument | [BCS16] Theorem 7.1 third bullet and Lemma 7.5: `z' = z + p(x) 2^(-lambda/4 + 2)`, statistical, explicitly-programmable random oracle (Section 2.3, Remarks 1.4, 2.2), Merkle tree with privacy of Section 3.2; restated in [CFW26] Section 1.4 and [Dia25] Section 4.1 | Published (qualitative). The quantitative bound used by the method is [CY-book] Theorem 26.2.1, not [BCS16]'s |
| `zk-composition.md` 6 | the standard (unsalted) compilation is not zero-knowledge when the distinguisher inherits the oracle | [Dia25] Section 4.1 (the recomputed-root attack) | Published |
| `zk-wi-soundness.md` | W-I soundness in the unique-decoding regime | [BCIKS20] Theorems 4.1, 1.6 | Original proof from published proximity gaps (O-7). A published analysis of the corresponding protocol, in the list-decoding regime, is [CFW26] Theorems 6.3, 7.1, 9.8/9.12, 10.2 (not used) |
| `binius-extension-challenges.md` 6.1; `ext-challenge/test_zk_mask.py` | a mask sampled in the base field does not hide a value combined with an extension-field challenge | related: [HK25] Lemma 1 and inequality (1) (each extension-field query to a base-field randomized polynomial counts as `e` base-field queries) | Original as far as checked for the fold-challenge form (O-11); the counting principle is Published |
| `binius-extension-challenges.md` 6.2 (b); `yugen-proof-b2` Lemma 7.2 | `q` opened symbols are uniform when the pad fills coefficients `0..q` | [CFW26] Lemma 3.29 (exactly this statement, monomial basis, any domain); the last paragraph of the proof of [Dia25] Lemma 4.4 (the novel-basis Vandermonde of `X_0..X_{kappa-1}` is nonsingular) | Published |
| `binius-extension-challenges.md` 4.2, mask fold round; `soundness-method.md` 8.5c row `mask`; `binius64.py` | mask round error `(n + 1)/q`: proximity gap on the combination, one root for the claim | [Dia25] Theorem 4.2 (proof sketch): the same two events, [BCIKS20] Theorem 4.1 for the combination and "low probability over alpha" for the claim; no explicit error stated | Published as a sketch; the explicit count is ours |
| `binius-extension-challenges.md` 7 (a) | two parallel copies do not square the error under Fiat-Shamir (the interactive half: [AF21] Theorem 4, C-20) | [BCS16] Theorem 1.5 (`s_sr(b) <= binom(b, k+1) s`) and Remark 1.6 (repetition does reach small state-restoration error, with `r = Omega((k log b + lambda) / log(1/s))` copies) | The attack run is ours (O-12); the general statement is from memory (Attema-Fehr-Klooß, unread) |
| `soundness-method.md` section 5; `framework-selection.md` 3 | Plonky3's `HidingFriPcs` masking bounds | [HK25] Section 4.2 (Lagrange decomposition), inequalities (16), (17), Lemma 5; the mask `R` of Protocol 2 and Lemma 2 (decoupling) | Published; verified |
| `soundness/` calculator | classical compilation `eps_sr(t) + 3.5 t^2 / 2^lambda`, `eps_sr <= (t + k) eps_rbr` | [CY-book] Theorems 25.2.1, 31.2.1; the original statement is [BCS16] Theorem 7.1: `s' = sbar_sr(x, m) + 3 (m^2 + 1) 2^-lambda` | Published |
| `soundness-method.md` F3, 8.2, 8.3 (condition Q), 8.5b; `compose.py` | quantum compilation `6 t^2 eps_rbr + 24 t^3 / 2^lambda` (plus Lemma 4.9's `sqrt(a / 2^lambda)`, `t' = t + O(q log l)`) | [CMS19] Theorem 8.6 (Section 8.4), constants from its proof, Section 8.5.1 (Lemma 5.13 with Lemmas 8.13, 6.11; Lemma 4.9; Proposition 8.11) | Published; for [CMS19]'s own BCS construction (Section 8.2, Remark 8.2); the built transcripts' fit is open (C-7) |
| `zk-composition.md` 6; `zk-hiding-commitment.md` 4 | zero knowledge against quantum distinguishers | [CMS19] Theorem 8.6 (3), Lemma 7.3: classical statistical zero knowledge against query-unbounded distinguishers carries over | Published for that hypothesis; not met by Lemma M (query-bounded): C-8 |
| `soundness-method.md` 2.3; `whir.py` | WHIR round list: fold `3 l / |F| + err*`, OOD `l^2 / 2 (2^m / |F|)^s`, shift `(1 - delta)^t + l (t + s) / |F|`, final `(1 - delta)^t` | [ACFY24] Theorem 5.2 (one OOD sample; Lemma 4.25 for `s`), Construction 5.1 (`d* = 3`); `err*` in unique decoding: Lemma 4.10, Corollary 4.11 | Published for smooth multiplicative domains in unique decoding; applied to System A's binary additive codes (C-10); up to Johnson `err*` is [ACFY24] Conjecture 4.12 |
| `soundness-method.md` P5 | Johnson list size `1 / (2 eta sqrt(rho))` | [ACFY24] Theorem 4.3 (stated without proof), Lemma 4.4 (interleaved) | Published (as stated there) |
| `soundness-method.md` 8.5c, 8.5d; `binius64.py`; `binius-extension-challenges.md` 4.2 | Binius64's query round `((1 + rho)/2)^gamma` and fold rounds `(n_j + 2) / q` | [DP24] proof of Proposition 4.24 and Section 5.2 equation (42) (query); Proposition 4.21, 4.23 and the sumcheck term in the proof of Theorem 4.17 (fold); round by round: [Hab-LDR] Theorem 1 with Sections 5.4, 6.2, 6.3 (Theorem 6) | Published (terms); the round-by-round form in unique decoding rests on [Hab-LDR]'s remark that its analysis "carries over verbatim" (C-12) |
| `binius-extension-challenges.md` 3.1, Theorem 1 | ring switch, form T, error `kappa_K / |K|` | [DP24] Construction 3.1, Theorem 3.5 (Schwartz-Zippel on `r''`, `kappa / |L|`) | Adapted: over `GF(2) < K` with the upper 128 packing coordinates zero, the zero columns not sent, an `L`-valued oracle (C-13) |
| `binius-extension-challenges.md` 3.2, Theorem 2 | ring switch, form F (Frobenius powers), error `kappa_L / |K|` | [DP24] Section 1.3, equations (16) to (20), Figure 4 (the Galois-orbit check of Hashcaster, improved there); the matrix fact as [DP24]'s citation of Lidl-Niederreiter Lemma 3.51 | Adapted: the orbit of `L`, claims and challenges in `K` (C-13) |
| `binius-extension-challenges.md` 4.1, Lemma 3 | commitments in a subfield, challenges and code over the larger field | [Hab-LDR] Section 6.3 (alphabet `E`, query field `F >= E`, Theorem 6 with the code over `F`) | Adapted (the setting is published; the restriction argument is ours) |
| `binius-extension-challenges.md` 7 (d); `design-basis.md` 2a; `binius64.johnson_bciks` | 107 queries at rate 1/8 in the list-decoding regime | [Hab-LDR] Theorem 6 (row-batched FRI-Binius), Lemma 3 (query `(1 - theta)^s`), Theorem 3 (fold error) | Published for the PCS core; the ring switch, the mask round and lifted oracles are not covered (C-11) |

| `binius-johnson-row.md` 2.2 F1' (revision 2) | list size at most `floor((a - rho)/(a^2 - rho))` = 19 at `m = 10`, every width and evaluation set | [DKT26] Theorem 4.4 bound (38) second term, proof at the end of Section B.2 (read); Corollary 6.4 | Published (uniformity in `n` ours, P) |
| `binius-johnson-row.md` 0.1, 2.2 F2, 4.1, 5.4, 7, 8 | line MCA with full agreement sets at the Johnson threshold, exceptional count `< 8 n t^3 / (3 rho_-)` (only `< 2^103.48` needed, 8.4), interleaved and width independent; message dimension 1 | [DKT26] Theorem 4.4 (39), Definitions 3.1, 3.2, Lemma 6.5, Corollary 6.6, **Lemma 3.3** (proof read) | Published (preprint of 2026-11-02; Theorem 4.4's algebraic-geometry lemmas not checked here): the row is proved **conditional** on it |
| `binius-johnson-row.md` 2.2 F2, 6 | line MCA in unique decoding, error `n / |F|` | [ACFY24] Lemma 4.10 (any linear code; read) with [BCIKS20] Theorem 4.1 (any domain); [ACFY24] Corollary 4.11 is for smooth domains and is not cited for ours; width by [DKT26] Lemma 6.5 | Published |
| `binius-johnson-row.md` 4.2, 4.3, 10 (Haböck route) | weighted subcode / non-linear correlated agreement `eps(C, M, B, theta)` | [Hab-LDR] Theorems 3, 4, Remark 5, Lemma 1 (fallback F-J2), Lemma 4 | Published; **not an available route for the row** (revision 2): G-1 (leaf mask round), G-3, G-6 |
| `binius-johnson-row.md` 3 | eq-weighted ring switch per candidate `kappa / |K|` | [DP24] Construction 3.1, proof of Theorem 3.5, through `binius-extension-challenges.md` Theorem 1 | Adapted (O-11) |
| `binius-johnson-row.md` 5.1 | lifted codeword = duplicated codeword (completeness) | Binius64 Blueprint 5.3, Theorem 5.1, identity (8) (unpublished, read locally) | Published there |
| `binius-johnson-row.md` 5.4 (Lemma F) | measures `mu_i`, `mu*_{i-1}`, language (35), sumcheck compliance `Gamma_i`, the fold-round proof | [Hab-LDR] Section 5.2 ((29), (30), (31), Lemma 2) and Section 6.1 ((35), Lemma 4) | Adapted (MCA in place of Theorem 4; the weighted-to-unweighted step written) |
| `binius-johnson-row.md` 5.4, 9 (index rounds), 4.1 (shape) | fold of the rows of an interleaved word by a sumcheck challenge: RBR knowledge error `eps_mca + Lambda eps_pil(C, 1, d_s)` at any `delta < delta(C)` | [CFW26] Theorem 6.3, Construction 6.4, Lemma 6.6 (proof read) | Published (index rounds); the pattern of Lemma J2 |
| `binius-johnson-row.md` 7 (Lemma K) | round-by-round knowledge (state function, extractor), per-round errors; equivalence under a total order | [CMS19] Definitions 8.3, 8.5; [SG26] Definition 2.20, Lemma 2.21 | Published (definitions) |
| `binius-johnson-row.md` 7.1 | online knowledge soundness in the QROM of the spBCS transformation from round-by-round knowledge | [SG26] Theorem 6.6 (2), Protocol 6.5, Definition H.3 (statements read); alternative [CMS19] Theorem 8.6 (2) | Published; needs the spBCS transcript in the build |
| `binius-johnson-row.md` 7.2 | extraction by list decoding the committed words; polynomial-time complete list decoding above Johnson in every characteristic | [ACFY24] Theorem 7.5 (statement); [DKT26] Section 1.1, Corollary 9.4 (statement) | Adapted (Lemma K, O-24) |

| `qrom-compilation.md` 2 (revision 2) | the spBCS transcript: key from the whole past with the proof salt, stream per verifier message, write-back of the stream's digest, four disjoint oracle parts, samplers, salted binary Merkle trees | [SG26] Protocol 6.5, Section 6.2, Appendix I.1 | Published; the byte-level instantiation for A and B is ours (O-27) |
| `qrom-compilation.md` 3 to 5; `soundness/spbcs.py`, `revision6.py` | QROM (and ROM) adaptive knowledge soundness of spBCS: `2 sqrt(k_q/2^(8(b+e))) + 6 (t + k_q)^2 (eps_k + c' (t + k_q)/2^(8b))`, `c' = max(2, c) + n_J + 1`, `k_q` of Definition I.1 | [SG26] Theorem 6.6 (2), Theorem I.16, Definition I.1, Definitions 2.18, 2.20, Lemma 2.21 | Published (used as is for both systems; with Lemma X for B's counter-mode alternative: Adapted) |
| `qrom-compilation.md` 6.2 (Q-5) | the book gives a theorem only for the hash-chain construction; the whole-past variant has "slightly smaller security bounds", no theorem | [CY-book] Remark 25.1.3, Theorem 25.2.1 | Published (the remark); the consequence for condition C is O-29 |
| `qrom-compilation.md` 7, 8 (record) | QROM soundness of BCS from round-by-round soundness, constants 6 and 24; the database and lifting machinery for oracles of any input and output size | [CMS19] Theorem 8.6, Section 8.5.1 (Lemmas 8.13, 6.11, 5.13, 4.9), Section 4 | Published; adapted to the CMS form as Theorem Q (O-20, record: form X a sketch, form C unproved) |
| `qrom-compilation.md` 7.1 (Observation 1), Q-4 | the BCS construction with one oracle per round whose output is the round's randomness, chained on the previous challenge, salted leaves; the state-restoration game with fresh salts | [CY-book] Construction 25.1.1, Section 18.1, Definitions 23.2.1, 23.2.2, Theorem 31.2.1 | Published |
| `zk-quantum.md` 1 | query-bounded hiding of a salted commitment, two-phase argument | [CY-book] Lemma 17.3.1 (`t < infinity`), Claim 17.3.2 | Adapted (Lemma M, O-22) |
| `zk-quantum.md` 2.1 | salts as long as the digest: expected distance of an unopened leaf about `1/e`, no statistical zero knowledge | [SG26] Section 8.4 (p. 77); [CY-book] Claim 3.4.1 | **Published** (relabelled 2026-11-19, referee 2.2) |
| `zk-quantum.md` 3.1 (Lemma H) | per-leaf hiding term `eps_leaf = (1/2) sqrt(2^(8b)/2^(8 b_l)) + sqrt(ln N_leaf / (2 * 2^(8 b_l)))`, summed over the positions | [SG26] Definition I.1 (from [CY-book] Claims 3.4.1, 3.4.2), proof of Theorem I.5 step 3, Lemma I.7 (1) | **Published** (relabelled from Adapted, referee 2.4) |
| `zk-quantum.md` 3.1 to 3.4; `soundness/spbcs.py` | everlasting zero knowledge of spBCS in the QROM for `Q` adaptively chosen proofs; unconditional witness indistinguishability | [SG26] Theorem 6.6 (3), (4), Theorems I.5, I.6 with proofs, Definitions 6.2, 6.3, H.6, 2.22 | Published, used as stated |
| `zk-quantum.md` 3.3 (Theorem ZP) | applying a simulator's assignments on top of the oracle in a reduction | [SG26] proof of Theorem I.5, step 2 (ii), with Lemma I.10 | Published technique; the composition is O-28 |
| `zk-quantum.md` 5.1 (route F) | the zero-knowledge BaseFold simulator computes the fold oracles in full from its simulated word | [Dia25] Theorem 4.3, simulator steps 1 to 6 | Published; the full-view use is Adapted (route F, record) |
| `zk-quantum.md` 6 (record) | statistical zero knowledge against query-unbounded distinguishers carries to quantum ones; definition with the whole oracle | [CMS19] Section 3.3, Lemma 7.3 and its proof | Published (Theorem ZQ, superseded) |
| `zk-quantum.md` 2.1 | `n 2^(-lambda/4 + 2)` privacy for `2 lambda`-bit salts | [BCS16] Lemma 3.4 | Published (weaker than [CY-book]; not used) |
| `whir-additive-soundness.md` 1, 4 | unique decoding turns any proximity generator into one with mutual correlated agreement, any linear code | [ACFY24] Lemma 4.10 with proof | Published |
| `whir-additive-soundness.md` 1, 6 | the affine combiner, its degree asymmetry, `Omega(n/q)` worst case without agreement loss | [CWYZ26] Section 1.1, Section 6 | Published |
| `whir-additive-soundness.md` 1, 6 (W-1) | the degree growth of leanVM's combiner (one coefficient a round) | the pinned leanVM verifier (`crates/verifier/src/whir.rs`); [CWYZ26] Theorem 5.2 states `d + r` for the equal-degree combiner (5.1) only | source: the code; CWYZ26 cited as consistent, not as the source (corrected 2026-11-19, referee 3.2) |

| `soundness-method.md` P4; `bounds.pg_johnson_dkt26`; `binius-extension-challenges.md` 7 (d) | line MCA (full agreement sets) up to Johnson, count `< 8 n (m + 1/2)^3 / (3 rho_minus)`, `rho_minus = (k-1)/n`, any field, any evaluation set | [DKT26] Theorem 4.4, equations (36) to (39), Section B.3; Definition 3.2 | Published (C-14; the calculator's `rho` corrected to `rho_minus`) |
| `soundness-method.md` P5 | Johnson list size on any domain | [DKT26] Theorem 4.4, equation (38), Proposition B.1; the calculator's `m / rho` exceeds it | Published (C-15) |
| `soundness-method.md` 2.2 (P2 note), C-15 | WHIR Conjecture 4.12 (1) for lines holds up to Johnson, with DKT26's error | [DKT26] Theorem 4.4 with Definition 3.2, read against [ACFY24] Definition 4.9 | Published (the implication is one line, ours) |
| `binius-extension-challenges.md` 7 (d) | `eq`-weighted (tensor) folds of interleaved words, error `h` times the line count | [DKT26] Corollary 6.7 (after [BCGM25] Lemma 4.4, Corollary 8.6, not read), Corollary 6.6 | Published |
| `soundness-method.md` F4; `compose.py` grinding | a `z`-bit proof of work multiplies the round error by `2^-z`; compiled bound `T max eps_i 2^-z_i + 3 (T^2+1)/2^kappa` | [ethSTARK] Section 6.3, Theorem 6; Section 7.1, Theorem 8 | Published (classical ROM; C-17) |
| `soundness-method.md` 2.3, ALI row | constraint combination `C L / q` | [ethSTARK] Theorem 5 item 1 and Remark 6 | Published (form) |
| `soundness-method.md` 5 | round-by-round (knowledge) soundness of FRI and its Fiat-Shamir compilation | [BGKTTZ23] Theorems 4.1, 4.2, 5.11, Corollaries 4.3, 4.4 (smooth multiplicative `L0`, binary folding) | Published; covers neither A nor B on Binius64 (C-18) |
| `zk-wi-soundness.md` Lemma 2A | the affine combiner `G + (alpha + beta x) F` with the degree asymmetry | [CWYZ26] Section 1.1; the no-loss lower bound Proposition 6.2 | combiner Published; the proof of Lemma 2A Original (O-7; C-19) |
| `soundness-method.md` 2.3 (leanVM), `framework-selection.md` R-5 | leanVM's `eps_aff` | [CWYZ26] Theorem 4.10, equation (4.13), Remark 5.3; Theorem 5.2 (packing, (5.7)) | Published; transcription checked (C-19); **implemented** in `soundness/affine.py` (revision 6) with leanVM's witness search, Remark 5.3 (125.42 bits) and the example after Theorem 4.10 (123.25) reproduced; a cross-check column only |
| `binius-extension-challenges.md` 7 (a) | interactive parallel repetition reduces the knowledge error to `kappa^t` | [AF21] Theorem 4 (special-sound multi-round protocols) | Published (C-20) |
| `binius-extension-challenges.md` 7 (a); `ext-challenge/test_parallel_repetition.py` | the staggered attack on two parallel copies under Fiat-Shamir | [BGKTTZ23] Appendix C (attributed there to Attema-Fehr-Klooß, TCC 2022) | Published (O-12) |
| `binius-extension-challenges.md` provenance; `REFERENCES.md` O-11 | zero-knowledge ring switching (masked twisted sums; subfield and squaring-chain masks) | [SG26] Section 5.5, Table 1 | Published, other setting (Ligero); related work for O-11 (C-21) |
| `zk-hiding-commitment.md` 4; `zk-composition.md` 6 | QROM everlasting zero knowledge of a salted BCS variant; salts as long as the digest give no statistical guarantee | [SG26] Theorem 6.6 (3), Definition I.1, Section 8.4 | Published for spBCS with salts of about twice the digest; not met by the built 32-byte salts (C-21) |

| `decision-b-merkle-hash.md` 6.1, 9 H-1.1 | BLAKE3's security claims: 128 bits for collision, (second) preimage and differentiability, every mode, outputs of at least 32 bytes; no quantum statement | [B3] Sections 1, 4.1, 2.6; [B3-ID] Sections 1.1, 7 | Published |
| `decision-b-merkle-hash.md` 6.1, 9 H-1.9 | 7 rounds instead of BLAKE2s's 10; changed schedule, inputs `b`, `d`, finalisation | [B3] Sections 1, 2.2, 4.2, 7.3, 7.4; [B3-ID] 3.3 | Published |
| `decision-b-merkle-hash.md` 6.3, 9 H-1.6 (MA-2') | the truncated compression function is indifferentiable; the mode is sound with bound (2) | [B3] 4.2 (citing Luykx, Mennink, Neves), 4.3 (citing Daemen, Mennink, Van Assche, Theorem 1); neither cited paper read | Published (as stated by [B3]); MA-2' itself is a modelling assumption of this project (O-31) |
| `decision-b-merkle-hash.md` 9 H-1.7 | modes, flags, key words, chunk and parent compressions; context strings hardcoded and application-specific; keyed hashing with `hash(label)` for domain separation | [B3] 2.3 to 2.5, Table 3, 6.2, 6.3, 7.7; [B3-ID] 2.5, 4.1, 4.2, Appendix B | Published mechanism; the framing is Adapted (O-32) |
| `decision-b-merkle-hash.md` 6.1, 9 H-1.8 | reduced-round results on BLAKE-256 and BLAKE2s (rounds, type, complexity) | [B3] 4.4, Tables 4, 5; since revision 3, checked against [EFK15] Tables 1, 6, 7, [GKNWW14] Tables 1, 2 and Sections 2 to 7, [B2] 4.1, [TMC] 3.2 (1.1e-bis); the other cited papers are not read | Published; the results only [B3] states are marked so in H-1.12 |
| `decision-b-merkle-hash.md` 9b H-1.11, H-1.12 | the margin table: rounds attacked by model, for BLAKE2s, BLAKE-256 and BLAKE2b; Keccak and SHA-2 as [TMC] reports them | [GKNWW14] 2 (models), 3 to 7, Tables 1, 2, Appendices C, D; [EFK15] 5.1 to 5.3, Tables 1, 6, 7; [B2] 2.1, 4.1, 4.2; [TMC] 3.2, 3.4, 4.5, 5.1 | Published (results); the mapping of system B's use to model H is Original (O-37) |
| `decision-b-merkle-hash.md` 9b H-1.13, H-1.14 | no feed-forward makes free-state pseudo-preimages trivial; the guard on row 3; the full-round weak-key property of the permutation | [GKNWW14] 2, 3, 5, 7; [EFK15] 5.1, 5.2; [B3] 2.2, 4.2, 4.4, 7.3, 7.4 | Published facts; their transfer to BLAKE3 is Original (O-37) |
| `decision-b-merkle-hash.md` 9b H-1.15, H-1.17; 5 item 2 | *Too Much Crypto*'s proposals, criterion and quantum remarks; the ChaCha lineage | [TMC] 2, 4.4, 4.5, 5.1 to 5.3, addendum; [B2] 4.1 | Published |
| `decision-security-category.md` 3.5; `category-study/category_study.py` `qrom_tables` | QROM extraction error of spBCS, evaluated at 48- and 64-byte digests and 96 / 128 QROM bits over 20,000 proofs | [SG26] Theorem 6.6 (2), page 58 (read from the text layer 2026-11-19) | Published (the bound); tree accounting Original (O-13); the category rows O-34 |
| `decision-security-category.md` 3.6; `category_study.py` `zk_tables` | leaf salts must exceed the digest: first term of `eps_leaf` is `2^(-4(b_l - b) - 1)`; proposed salts 96 B (cat3), 80 / 112 B (cat5) | [SG26] Theorem 6.6 (3), (4) and the paragraph before the theorem, page 58 to 59; Definition I.1 | Published (the bounds); the salt rows Original (O-34) |
| `decision-security-category.md` 0, 2, 4.1 | BLAKE3 is admissible at category 1 only (128-bit claim for every goal and output length) | [B3] Section 4.1; [B3-ID] Section 7; as recorded in `decision-b-merkle-hash.md` H-1.5 and `CITATION-AUDIT.md` 1f C-25 | Published (the claim); its consequence O-31 |
| `decision-security-category.md` 0, 2, 3.7 | Falcon degree 512 is level I and 1024 level V; Falcon-1024 key, signature sizes and norm bound | `fn-dsa` 0.3.0 source comment (`yugen-falcon/vendor/yugen-fn-dsa-sign/src/lib.rs` 29 to 30); `fn-dsa-comm` 0.3.0 `vrfy_key_size`, `sign_key_size`, `signature_size`, `mq.rs` `SQBETA[10]` = 70,265,242 | Published as code (T. Pornin); the Falcon specification and the FN-DSA draft are not in the folder (1.3) |
| `decision-security-category.md` 1.1, 2 | the NIST category definitions; ML-KEM-768 at category 3; ML-KEM-1024 sizes; SLH-DSA-SHA2-128s at category 1; SHAKE256 capacity claims; BHT collision cost | NIST PQC call for proposals, FIPS 202, 203, 205, the FN-DSA draft, BHT: **not in the folder, not read** (1.3); stated as "to be verified" or "from memory" | not verified |
| `soundness/src/yugen_soundness/category.py` (`NIST`, `kappa_classical`, `kappa_quantum`, `derive_target`); `soundness-method.md` 8.7 | the five categories, their reference attacks and gate counts; MAXDEPTH range; ordering of the categories | [CFP] Section 4.A.5, pages 16 to 18 and footnotes 2, 4 to 6 | Published (the figures, used as is); the conversion into conditions C, Q, G, H is Original (O-38) |
| `category.py` `derive_target` (condition H); `soundness-method.md` 8.7 | digests of 384 / 512 bits for categories 3 / 5 (collision strength) | [CFP] page 18 (SHA3-384 2^210, SHA3-512 2^274 classical gates against AES192 2^207, AES 256 2^272); [FIPS204] Section 4 Table 1 (collision strength of c~ 128 / 192 / 256 at categories 2 / 3 / 5) and Appendix D.1 | Published (NIST's figures and precedent); the rule as a calculator condition Original (O-38) |
| `category.py` `TREE_HASHES`; `design-basis.md` 1 | SHA-256 is replaced by SHA-512 in tree functions at categories 3 and 5 by NIST's own instantiation | [FIPS205] Section 11.2.2 (`H`, `T_l` with SHA-512; `F`, `PRF` with SHA-256) | Published (the instantiation); the reason (collision role of tree nodes) is this project's reading, NIST states none |
| `category.py` `zk_row`, `leaf_salt_floor`, `proof_salt_floor`; `soundness-method.md` 8.7 | zero-knowledge errors at categories 3 and 5 and the salt floors from a pool target | Sharp, Grubbs, ePrint 2026/2615, Theorem 6.6 (3), (4) and the `eps_leaf` paragraph before it (page 58), Definition I.1 | Published (the bounds); the targets and floors Original (O-40), following referee F-4 (`security-category-referee.md` 3.4) |
| `decision-security-profile.md` 1, 4 | the five categories, their gate figures, MAXDEPTH, the ordering, the recommendation to focus on 1 to 3 and hedge above 3, multi-key resistance desirable | [CFP] Section 4.A.5 pages 16 to 19, 4.A.6 | Published |
| `decision-security-profile.md` 2.2 | 384-bit collision strength as the category 3 / 4 rule for collision-dependent digests | [FIPS204] Section 4 Table 1, Appendix D.1; [CFP] page 18 | Published (precedent); the binding classification is Original (O-50) |
| `decision-security-profile.md` 2.1, 2.3 | 256-bit preimage-only functions at category 5 | [FIPS205] Section 11.2.2 | Published (precedent) |
| `decision-security-profile.md` 2.3 | Falcon-512 / 1024 at NIST levels 1 / 5; key and signature sizes | [GLS26] abstract, Section 1; [COSE-FN] Table 1 | Published |
| `decision-security-profile.md` 3.3 | message recovery: signing, verification, reduction to Falcon | [GLS26] Algorithms 3, 4, Lemma 1 | Published; its assessment for a signature verified inside a proof is Original (O-55) |
| `decision-security-profile.md` 2.1, 2.4; `profile-study/profile_study.py` | zero-knowledge and QROM figures, rows and sizes of profile Y | [SG26] Theorem 6.6 (2) to (4) through `soundness/` revision 7 (not re-read) | Published bound; the work-over-advantage reading is Original (O-52) |
| `decision-security-profile.md` 2.1 | ML-KEM-768 / 1024 levels and sizes; SHAKE256 and SHA3 capacity; quantum collision search with quantum memory | FIPS 203, FIPS 202, Brassard-Hoyer-Tapp: **not in the folder, from memory** | not verified |
| `decision-security-profile.md` (revision 2) 1.3, 2.2 | a 384-bit SHAKE256 output is the category-4 case for collisions | [FIPS204] Appendix D.1, page 64 (quoted); [CFP] page 17 | Published (precedent); FIPS 202's generic bound from memory |
| `decision-security-profile.md` (revision 2) 1.1 | the two-hour MAXDEPTH extrapolation (about 2^142 gates) | [CFP] page 18 AES-128 formula, read below its stated range | Adapted (change: the depth only; first in `security-profile-referee.md` 1.2) |
| `decision-security-profile.md` (revision 2) 2.1 | proof-salt and leaf terms at the lifetime count `Q = 2^37` | [SG26] Theorem 6.6 (3), (4) through `spbcs.eps_leaf_log2` (`profile_study.py` S7) | Published bound; `Q` and the floors are Original (O-64) |
| `decision-security-profile.md` (revision 2) 2.1 | DPF PRG for 256-bit seeds: AES-256 keyed by the seed in counter mode; security by AES-256 as a PRF | standard construction, **from memory** (no source in the folder) | not verified; W-4 measures it |
| `qrom-compilation.md` 2.8 | the encodings, samplers and Merkle rules the theorem assumes; repeated positions excluded | [SG26] Definition 2.18 (page 13), Protocol 6.5 (page 57), Theorem 6.6 (pages 58 to 59), Section I.1 (pages 130 to 131) | Published (read); the per-deviation checks and Lemma D are Original (O-66) |
| `qrom-compilation.md` 2.8 B-4 (MA-2') | BLAKE3 `derive_key` as a random oracle on each part | [B3] 2.3, 4.2, 4.3 | Published support for a modelling assumption that is Original (`decision-b-merkle-hash.md` H-1.6) |
| `soundness/.../dkt26.py` `line` (revision 8) | exceptional count of line MCA at our Johnson threshold, exact: `E^(1)_ord(D, A, n; B_jet, B_Z) = (2 B_jet - 1) B_Z + lambda_agr (B_jet + B_Z Psi_D(B_jet)) + (n - D - 1) B_jet`, with the theorem's own `m`, `B_jet`, `B_Z` from our `A` | [DKT26] Theorem 4.4 (36), (37), (39) first part; Section 4.2 (33), (34), `Psi_D`; hypotheses `1 <= D <= n - 2`, `a <= 1` | Published (preprint), used as is; the choice `eta_0 = A/n - sqrt(rho_-)` is ours (the largest `a` with `ceil(a n) = A`) |
| `soundness/.../dkt26.py` `line` (revision 8) | closed form `8 n t^3 / (3 rho_-)`; list size `min(B_jet, floor(n (A - D)/(A^2 - n D)))` | [DKT26] (39) with Section B.3; (38) with the end of Section B.2 | Published (preprint) |
| `soundness/.../dkt26.py` `lemma33_count`, `terms(dimension_one="lemma33")` | a fold line of message dimension 1: `floor(C(n, 2)/(A - 1))` | [DKT26] Lemma 3.3 (6) | Published (preprint) |
| `soundness/.../dkt26.py` `terms` | width independence of every line term | [DKT26] Lemma 6.5, Corollary 6.6 | Published (preprint) |
| `soundness/.../dkt26.py` `terms` (unique decoding) | `n` bad challenges per line on any evaluation set | [ACFY24] Lemma 4.10 with [BCIKS20] Theorem 4.1; width [DKT26] Lemma 6.5 | Published |
| `soundness/.../dkt26.py` `per_query_bits` | one query accepts a doomed state with probability `(1 + 1/(2m)) sqrt(rho)` (Johnson) or `(1 + rho)/2` | [Hab-LDR] Lemma 3; [DP24] Proposition 4.24 | Published |
| `soundness/.../dkt26.py` `every_t_count` (C-2) | the need `c + 1 + log2 N + log2(1 + k_q)` under Q-5's convention (b) | [SG26] Theorem 6.6 (2), Definition I.1 (via `spbcs.classical_need`) | Published bound; the convention decided 2026-11-19 (every `t`, revision 9) |
| `soundness/.../category.py` `every_t_need`, `EveryTTarget`, `a_row_kq`, `_fixed_point`, `b_fixed_point`; `dkt26.py` `row`, `every_t_need` (revision 9); `decision-qrom-counting.md`; `soundness-method.md` 8.9 | the classical need of every row for every `t`: `kappa_C + 1 + log2 N + log2(1 + k_q)` at the row's own `k_q` | [SG26] Theorem 6.6 (2) (p. 58), Definitions H.3 (p. 128), H.4 (p. 129), I.1 | Published bound and quantifier; the per-row fixed point Original (O-68) |
| `soundness/.../hashterm.py` (revision 10, R9-1); `category.Row.hash`, `hash_term_summary`; `dkt26.Row8.hash` | the hash term `c' (t + k_q)^2 / 2^(8b)` (ROM) and `6 c' (t + k_q)^3 / 2^(8b)` (QROM) of the extraction error, per proof; `c' = max(2, c) + n_J + 1`; adversaries of at most `t` hash queries | [SG26] Theorem 6.6 (2) and its preamble, Section 6.3 (page 58); Definition I.1 (page 130); Section I.1 "The oracle's domain", "Hash functions", "Merkle trees" (page 131: one oracle, a digest is the first `8b` bits, the written-back digest the stream's first `8b` bits), all read from the RENDERED pages (PDFKit, scale 2.2) for revision 10 | Published; the tree sum, the every-t level and the digest rule Original (O-75) |
| `soundness/.../hashterm.py` `HASH_ATTACK_RULE`; `decision-qrom-counting.md` 7 | category 1 is an attack-cost requirement ("Any attack that breaks the relevant security definition must require computational resources comparable to or greater than those required for key search on a block cipher with a 128-bit key (e.g. AES128)"); a parameter set meeting a higher category meets every lower one | [CFP] Section 4.A.5, pages 16 to 18 (item 1; "Submitted parameter sets meeting the requirements of a higher category will be automatically considered to meet the requirements of all lower categories", page 18), re-read for revision 10 from the text layer (prose only) | Published |
| `soundness/.../dkt26.py` `Line.lean_count`, `Term.lean` (revision 10, L-2) | ArkLib's exception count `(2 mu - 1) h + theta (h + mu + 4 D mu h) + (n - D - 1) mu` | ArkLib `6aa8b6fe`, `ArkLib/Data/CodingTheory/HiddenDerivative/Parameters/Johnson/FiniteBounds.lean`, `johnsonExceptionCount` (read for revision 10); the statement that uses it: `lean/Compose.lean`, `check_F2_johnson_interleaved` (compiled 2026-11-19, axioms `propext`, `Classical.choice`, `Quot.sound`) | Published (ArkLib; machine-checked) |
| `qrom-compilation.md` 2.8 B-3 (Lemma D (ii)) | QROM collision bound of order `t^3 / 2^n` | Zhandry, **from memory, not in the folder** | not verified |
| `lemma-d-duplicate-openings.md` 4, 5 | the bad set with digest collisions and its instability; extraction outside it; lifting; the collision game | [SG26] Lemma I.12 (page 140), Lemma I.14 (page 141), Lemma I.15 and Theorem I.16 (pages 141 to 143), Protocol I.9 (pages 137 to 138), Definition I.13 (page 141); [CMS19] Lemma 4.9 (page 20), Lemma 5.7 (page 22), Lemma 6.11 (page 33), Section 2.3 (page 11); [BCS16] Section 6 (page 25), Lemma 3.2 (pages 14 to 15) | Published (read, text layer); Theorem D Adapted (the verifier's opening rule), O-70; replaces the row above |
| `lemma-tree-extraction.md` 3 to 9 (Theorem TE, Lemmas TE.1, TE.2, Corollaries TE-S, TE-F, TE-bb, Proposition TE-Q) | the ROM extractor answers by lazy sampling and applies the database algorithm to the table of the adversary's and the verifier's queries (Theorem I.16 (2)); the bad set and its instability (Lemma I.12); extraction outside it (Lemma I.14); the classical union bound over the table's entries; Definitions H.3, H.4, 6.1; the encoding of challenge inputs and statement digests in `pre(x)` (Section I.1) | [SG26] pages 53, 58, 59, 128, 129, 131, 137, 138, 140 to 144, **read from rendered pages** (pypdfium2, scale 2.0) | Published (used as stated; Lemma I.12 Adapted to several systems on one table, Lemma TE.1); revision 2: the compressed-oracle continuation is Lemma QC (section 9a), derived from [CMS19] Lemma 3.2 (printed page 17, **read from the rendered page**, pypdfium2 scale 1.8; Published there, attributed to Zhandry, proved in [CMS19] Appendix A, which was not read); [SG26] page 142 (the capacity remark in the proof of Theorem I.16 (1)) re-read rendered |
| `decision-b-parallel-batching.md` 5 (Lemma R, Lemma P, P-ind) | a reduction, its state function and round-by-round soundness errors; parallel composition with independent challenges keeps each reduction's errors; merged consecutive verifier messages have the sum of the errors; a degree-2 sumcheck round has error `2/\|K\|` | [SG26] Definition 2.24 (a) (pp. 15 to 16), Definitions 2.25, 2.26, Lemma 2.27 (2)(a) (p. 17), Lemma 5.2 (p. 37), Section 5 (p. 45); text layer | Published (the definitions and the two lemmas); Lemma R Adapted; Lemma P Original (O-71) |
| `decision-b-parallel-batching.md` 4, 5 (P-rlc-pad) | batching by one coefficient over equal-length sumchecks; padding a shorter sumcheck with `eq(0, .)` on extra variables | code of the pinned Binius64: `crates/ip/src/sumcheck/batch.rs` (`batch_verify`), `crates/ip-prover/src/sumcheck/padded.rs` (doc comments) | cited as code; no paper attributed |
| `decision-b-transcript-hash.md` 9 (T-1) | the oracle of Theorem 6.6 (2) may be instantiated by different functions on disjoint parts | [SG26] Appendix I.1, "The oracle's domain", "Hash functions" (p. 131) | Published |
| `decision-b-transcript-hash.md` 9 (T-2, T-3) | extended output uses the full 16-word compression output; the full-output compression function is not indifferentiable; bound (2) is for outputs of 256 bits or fewer; ROOT prevents length extension | [B3] 2.6; 4.2; 4.3 (equation (2) and the paragraph after it); 4.3 "Subtree-freeness", 7.7 | Published; the consequence for spBCS streams is ours (O-74) |
| `decision-b-transcript-hash.md` 9 (T-2, T-3) | Merkle–Damgård is indifferentiable only for prefix-free encodings; the sponge is indifferentiable for a random permutation | Coron, Dodis, Malinaud, Puniya, CRYPTO 2005; Bertoni, Daemen, Peeters, Van Assche, EUROCRYPT 2008: **from memory, not in the folder** | not verified |
| `decision-b-transcript-hash.md` 9 (T-6) | best reported result on ChaCha: key recovery on 7 of 20 rounds | [TMC] Section 3.3 (a co-designer's survey; its sources not read) | Published, at second hand |
| `round-census-a.md` 2.1; `zk-wi-soundness.md` Lemma 5 amendment (m-1) | sumcheck soundness `d l / |F|`, used per round (`d / |F|`) | [XZZPS19] Section 2.3.1, Protocol 1, p. 8 (restating [LFKN92]/[GKR15], see next rows; amended 2026-11-19) | Adapted (per-round form) |
| `round-census-a.md` 2.4 | GKR claims combined by a random linear combination | [XZZPS19] Section 2.3.2, p. 10 ("Combining two claims: random linear combination", credited there to [CFS17]); (explicit per-layer form: [GKR15] Section 3.3; amended 2026-11-19) | Published (the technique); per-round terms Original |
| `round-census-a.md` 2.1; `lemma-k-a.md` proof item 2; `zk-wi-soundness.md` Lemma 5 amendment (m-1) | sumcheck error per round `d_j / |E|` | [GKR15] Lemma 2.5, p. 27:21, proof inequality (3), pp. 27:22-23; origin [LFKN92] Lemma 4, p. 862 | Published (any finite field, so binary extensions); `eq`-form reduced messages Original (one line) |
| `round-census-a.md` 2.4 | per-layer GKR error = layer sumcheck + claim reduction, union over layers | [GKR15] Theorem 3.1, proof Section 3.3, pp. 27:31-32 (`7 m delta / |F|` per layer; two claims by a line, p. 27:31) | Published (structure); combiner by powers Adapted; `y` multilinear reduction Original; product-tree layers not in [GKR15] |
| `round-census-a.md` 2.2 | out-of-domain sample: collision probability `(l^2/2)(2^m/|F|)^s` over a list of size `l`; zero for `l = 1` | [ACFY24] Lemma 4.25 (and Lemma 4.24), p. 31, rendered page | Published (smooth codes); the `l = 1` case for any code Original (one line) |
| `zk-wi-soundness.md` 5.2 (amended); `lemma-k-a.md` 1, 3 | causal round-by-round knowledge soundness; equivalence with [CMS19] Definition 8.5 under a total order; security of a reduction | [SG26] Definition 2.20 (p. 14), Lemma 2.21 (p. 15), Definition 2.24 (pp. 15, 16), rendered pages | Published (definitions); Lemma K-A Original (O-87) |

---
| `design-private-tag-filtering.md` 2.1, 3.1, 4.2 | FMD syntax, FMD2, DA-CCA under DLOG/Gap-DH, costs, Lewis's attacks | [BLMG21] §2, Figure 3, Theorem 13, Tables 1 to 3, p. 19 | Published |
| `design-private-tag-filtering.md` 2.2, 3.2, 4.1, 4.2 | OMR, PVW clues, BFV detection, Ring-LWE privacy, Conjecture 8.4, costs | [LT21] §3, §7.1, §7.2, Theorem 8.3, Conjecture 8.4, §10 Tables 3, 4, §12 | Published; in-circuit counts Adapted (ours) |

## Part 3. Original contributions (the Ycash developers, 2026)

All are **unreviewed**. "First commit" is in this repository (`yugen-proofs`, branch `main`).
"Checked against" lists what was consulted before the label was given; none of the unread
sources of section 1.3 was consulted.

| # | Name | Statement in one line | Document, section | First commit, date | Support | Label and what was checked |
|---|---|---|---|---|---|---|
| O-1 | Staircase mask; Theorem 1, Corollary A, Theorem 2 | `g = c + sum_j ghat_j(x_j) x_{j+1}..x_n`, `ghat_j(0) = 0`, with `1 + sum_j d_j` coefficients maps bijectively onto the consistent mask views for every challenge vector over every field; general family `M_u` with any cofactor of functional value 1 | `zk-masked-sumcheck.md` 3, 4 | `ecd8b52`, `a36a3fa`, 2026-11-19 | proof in the document; `zk-lemma/test_rank.py`, `test_exact.py`, `test_leak.py` | **Original as far as checked.** Closest prior work: [CFW26] Definition 6.1, Lemma 6.2 (revision of 2026-11-16), which solves the same problem with `U_sigma = shat_0 + sum_e shat_e * pow_e`, `shat_e = sum_i sigma_{i,e} X_{i+1}..X_k`: also a staircase of trailing products, `(k+1)(d_s - 1)` coefficients, a surjection, masks shared with the rows' encoding randomness. Ours has one univariate polynomial per round times the trailing product, `1 + sum d_j` coefficients (the dimension of the view space, a bijection), per-round degrees, and general round functionals. The problem and the trailing-product idea are published; the family, the bijection and the functional form are ours. Checked: [XZZPS19] 4.1; [CFS17] 2.3; [CFW26] 2.5, 6; [Dia25] |
| O-2 | Corollary B | Libra's mask is perfect, in every characteristic, for a sumcheck weighted by `eq(tau, x)` with reduced round messages | `zk-masked-sumcheck.md` 3.4 | `a36a3fa`, 2026-11-19 | proof; `test_rank.py`, `test_exact.py` | Original as far as checked ([XZZPS19] 4.1; [CFW26] 2.5, 6: neither states it). Binius64 uses this form (`ip/src/libra.rs`), and its Blueprint's Theorem 6.3 proves the masked eq-weighted check, so the fact is in use upstream; the Blueprint is unpublished material read locally |
| O-3 | Lemma E in full; Lemma O | exact condition for a high-offset pad on an additive domain: hides `t` rows iff the domain avoids the zero set of the first random slot's basis polynomial and the offset is aligned; the count of leaking rows on a linear domain; out-of-domain budget `t >= Q + o` | `zk-hiding-commitment.md` 3 | `e25a3e5`, `3b22f2d`, 2026-11-19 | proof; `zk-commit/test_code.py`, `test_whir.py` | Sufficiency at offset `2^l`: **Published**, [Dia25] Lemma 4.4. Original as far as checked: necessity, alignment for other offsets, interleaved lanes, Lemma O. Checked: [Dia25]; [CFW26] 3.3.1, 9.2; [HK25] |
| O-4 | W-I as specified for the two pinned stacks | hiding WHIR-style opening on a coset domain with aligned high-offset randomness, one claim-level mask per fold batch, aux rows (F-1 layout), padded final message on an extra column; Theorems W, W-A (affine combiner), the excess rule, narrow alignment | `zk-hiding-commitment.md` 6; `zk-wi-soundness.md` 4.3 (F-1); `zk-system-a-gaps.md` 12 | `e25a3e5`, `3b22f2d`, `9cefa12`, `e16b1b5`, 2026-11-19 | proofs; `zk-commit/test_whir.py`, `test_whir_a.py`, `test_basecase.py`, `test_fold.py`, `test_narrow_align.py` | **Adapted**, not original as a design: the in-oracle layout, the base case and the masked sumcheck with a claim kept in the relation are [CFW26] Sections 6, 7, 9, 11. Ours: the high-offset placement on a coset (against [CFW26]'s low placement), the claim-level mask of O-5 in place of `U_sigma`, the budget rule of Lemma O in place of private zero-evaders, the affine-combiner variant for leanVM, finding F-1 and its fix |
| O-5 | Theorem 1', Lemma S, Lemma T, Lemma L | mask theorem for abstract round spaces `(P_j, lam_j, u_j)`; masked reduction with residual hand-off; triangular-pad method for affine views | `zk-hiding-commitment.md` 2, 5 | `66f2c5e`, `3b22f2d`, 2026-11-19 | proofs; `zk-commit/test_blind.py`, `test_product_round.py` | Original as far as checked ([CFW26] 6; [XZZPS19] 4.1; [CFS17]) |
| O-6 | Lemma F | folding without re-randomisation: `T >= Q 2^K` uniform coefficients, aligned, is sufficient, and fewer leak at the tested sizes | `zk-hiding-commitment.md` 7 | `66f2c5e`, `3b22f2d`, 2026-11-19 | proof; `zk-commit/test_fold.py` | Original as far as checked. Related: [HK25] Section 2 (halving per fold, multiplicative setting, not proven there without the mask, footnote 3); [Dia25] Section 4.2 |
| O-7 | Soundness of W-I, Theorem S; Lemmas 1 to 7; finding F-1 | round-by-round soundness in the unique-decoding regime with the round list of section 5; the aux-layout defect and its fix | `zk-wi-soundness.md` | `2c108dc`, `9cefa12`, 2026-11-19 | proofs; `zk-sound/` | Original proof from [BCIKS20] Theorems 4.1, 1.6. Published analyses of related protocols: [CFW26] (hiding, list decoding; not compared line by line); [ACFY24] Theorem 5.2 (plain WHIR, round by round, unique decoding, smooth multiplicative domains: the same round structure and terms without masks); [Hab-LDR] Lemmas 6 to 8 (a WHIR variant, first round, list decoding). Checked 2026-11-19: none treats masks or binary additive cosets, so Theorem S stays ours; its unmasked case is the theorem system A's plain-WHIR nodes need (C-10). Third pass (C-19): Lemma 2A checked against [CWYZ26] (Sections 1.1, 4, 5, 6): the affine combiner and the degree asymmetry of the conclusion are **Published** there; CWYZ26 proves MCA with one coordinate of agreement loss, not the no-loss `n/q` bound, and its Proposition 6.2 shows that order is necessary without loss; Lemma 2A's proof (BCIKS20 Theorem 1.6) stays Original as far as checked |
| O-8 | Blinder cells, Theorem B; pad ledger, Theorem C; GKR layer construction, Lemma 4; Lemma 5 (published cross-table sums); linear opening gadget, Lemma 3; Proposition 3 | composition of a whole leaf proof's zero knowledge | `zk-composition.md`; `zk-masked-sumcheck.md` 5, 7, 8 | `a36a3fa`, `f5946ae`, 2026-11-19 | proofs; `zk-lemma/test_gkr.py`, `test_bus.py`, `test_gadget.py`, `zk-commit/test_blind.py` | Adapted from [XZZPS19] Section 4.2 for the idea of a vanishing multiplier. **Blinder cells: Adapted** (relabelled 2026-11-19, fourth pass) from [SG26] Section 5.4.2, Lemma 5.8 (pads in the oracle input masking each sent element, a linear claim on the pads handed to the commitment; after [Fs24] Section 2.3); changes: one cell per revealed evaluation, multiplied by a dummy-variable factor. The ledger and the composed simulator stay Original as far as checked. Published composition theorems for HVZK reductions: [CFW26] Theorem 4.7, [SG26] Theorem 5.3 (neither read) |
| O-9 | Count-root mask (Propositions G1, G1-S); bit-slice mask (Proposition G3); shared-root M-3 analysis | one free leaf hides the count root with exhaustive memory-argument soundness; a block of cells read through a fixed `F_2` basis hides 64 bit-slice evaluations; the shared root as built is only statistically close | `zk-system-a-gaps.md` 1, 2, 9.2 | `1c153f0`, `73d178b`, `ee8d651`, 2026-11-19 | proofs; `zk-lemma/test_count_root.py`, `test_slices.py` | Original as far as checked (specific to the pinned leanVM statement; the five papers contain nothing on these). M-3 rests on a bound cited from memory (Katz) |
| O-10 | A8-T; Proposition D (one-sided dummy variable); Proposition L (linear terminals and hand-offs); Propositions M1, M2 | dummy variable with multiplier `y`, check `p(0) = claim`, dummy round last; a revealed value handed linearly into a masked head stays hidden | `zk-system-a-gaps.md` 3, 4, 5 | `5ea7100`, `ee8d651`, `80888d4`, `a465e08`, `065bb52`, 2026-11-19 | proofs; `zk-lemma/test_dummy_terminal.py`, `test_handoff.py`, `test_gkr4.py`, `zk-sound/test_terminal_dummy_sound.py` | Original as far as checked; related: [XZZPS19] equation (7) (multiplier vanishing on the cube); [SG26] Sections 5.4.2, 5.4.3 (pads per sent element and per-layer linear claims on pads; no dummy variable), compared in the fourth pass |
| O-11 | Lemma 4 (descent), rule Z and Proposition 6, the failure of section 6.1, wrapper transposition model; the three-field adaptation of the ring switch (Theorems 1, 2) and of the restriction setting (Lemma 3) | Binius64 with trace and commitments over `L = GF(2^128)` and challenges in `K = GF(2^256)`: two sound forms of the ring switch; every random value hiding a `K`-valued message must be uniform in `K` | `binius-extension-challenges.md` 3, 4, 6 | `b5476c6`, `b842b98`, 2026-11-19 | proofs; `ext-challenge/test_ring_switch.py`, `test_code.py`, `test_zk_mask.py` | **Relabelled 2026-11-19 (C-13).** Theorem 1 (form T): **Adapted** from [DP24] Construction 3.1 / Theorem 3.5 (zero-padded packing over `GF(2) < K`, same Schwartz-Zippel step). Theorem 2 (form F): **Adapted** from the Galois-orbit check in [DP24] Section 1.3, Figure 4 (Hashcaster, improved by DP24; no numbered theorem there). Lemma 3: **Adapted**, the setting of [Hab-LDR] Section 6.3. Original as far as checked: Lemma 4, section 6.1, rule Z, Proposition 6, the transposition model (sources consulted: [DP24] Sections 1.3, 2.6, 2.7, 3.1, 4.3, 5.2; [Hab-LDR] Sections 3 to 6; [Dia25]; [HK25]; [CFW26]; none treats zero knowledge with mixed fields; [Dia25] Section 5 leaves zero-knowledge ring switching open). Third pass (C-21): zero-knowledge ring switching **is** published in [SG26] Section 5.5 (Hashcaster form, masked twisted sums, subfield masks uniform in `K`, squaring-chain masks, perfect HVZK; for a Ligero commitment; its Appendix F not read). Lemma 4, rule Z, Proposition 6 and section 6.1 are a different construction for Binius64's mixed field and keep "Original as far as checked" with [SG26] added to the sources; rule Z's principle agrees with [SG26]'s subfield masks |
| O-12 | Staggered attack on two parallel copies | two copies of a multi-round protocol are forged under Fiat-Shamir at about `2 / eps` hash calls | `binius-extension-challenges.md` 7 (a) | `b5476c6`, 2026-11-19 | `ext-challenge/test_parallel_repetition.py` | **Published** (relabelled 2026-11-19, C-20): [BGKTTZ23] Appendix C describes the attack on a `t = 2` parallel repetition under Fiat-Shamir and attributes it to Attema, Fehr, Klooß, TCC 2022 (not supplied). The toy run is ours. [AF21] (ePrint 2021/1259) proves the interactive statement only (Theorem 4) |
| O-13 | Tree-wide soundness accounting; conditions C, Q, G, H; argument F5 | tree forgery as a union over all proofs of a tree with every round counted; category 1/3 targets as four conditions; grinding bits halve under quantum search | `soundness-method.md` 3, 8, 8.5b; `zk-wi-soundness.md` 8.3; `soundness/` | `0ce0a7c`, `196019d` (2026-11-18); `eca6825`, `af350fa` (2026-11-19) | calculator and its 117 tests | Original as far as checked as an accounting; it applies published bounds ([CY-book], [BCIKS20], [CMS19] Theorem 8.6 with the constants of its Section 8.5.1, read 2026-11-19: `C2 = 24`, finding C-6). [CMS19] bounds one instance and does not treat proof of work: the union over the tree and F5 stay ours. F5 is an unreviewed argument |
| O-14 | Corollary B's failure statement for the weighted mask of `yugen-zk-b`; negative controls | the earlier weighted mask is correct only outside "some `r_k = 1`" | `zk-masked-sumcheck.md` summary, 3.5 | `a36a3fa`, 2026-11-19 | `test_rank.py` | Original (a defect finding in this project's own earlier work) |
| O-15 | Lemma U (list state) | every round analysed per fixed oracle has error `B_list` times its per-oracle error; committing further oracles cannot un-doom | `binius-johnson-row.md` 2.3 | `5cec7e5`, 2026-11-19 | proof; referee: holds (`johnson-row-referee.md` 3.1) | **Adapted** from the union over a fixed list in [Hab-LDR] proof of Lemma 5; the same step is published in [CFW26] proof of Lemma 6.6 (compared in revision 2, section 9); the general per-round form is ours; reviewed by the internal referee |
| O-16 | Lemma J1 | ring switch in the list regime: `8 B_list / |K|`; list members descend to `L` | `binius-johnson-row.md` 3 | `5cec7e5`, 2026-11-19 | proof; `johnson-row/test_ring_switch_list.py` (T-J1-list, revision 2) | **Adapted** (O-11's Theorem 1 with Lemma U). Related, compared in revision 2 section 9: [SG26] Section 5.5 (zero-knowledge ring switching for Ligero, Hashcaster form, masked twisted sums; not a list-regime analysis, not form T): label kept; referee: holds |
| O-17 | Lemmas J2, J2' | the mask round is an interleaved line round; error `(N_line + B_list)/|K|` on the DKT26 route, **including the claim term `B_list`** (revision 1's "no separate claim event" withdrawn); `eps(C, 1, 1, theta)` on Haböck's route for one oracle only (unused by the build) | `binius-johnson-row.md` 4 | `5cec7e5`; revision 2 `binius-johnson-row.md` revision 2, `f58faa8`, 2026-11-19 | proofs; `johnson-row/test_mask_round.py` (T-J2-list, revision 2) | J2: **Adapted** (relabelled in revision 2, referee R-8): the error shape (MCA term plus list size times the roots of a nonzero low-degree identity) and the proof pattern are [CFW26] Lemma 6.6's; the round (Binius64's lerp mask fold of committed witness and mask rows, both orientations, claim carried by the explained member) is not in [CFW26] (its mask enters the sum, then an `epsilon` combination with no MCA term) and is ours. Compared: [CFW26] Theorem 6.3, Construction 6.4, Lemma 6.6 with proof; [SG26] Section 5.5 (unrelated round). J2': **Adapted** from [Hab-LDR] Theorem 4; referee: holds under DKT26 |
| O-18 | Lemma J3 with H8'; the counterexample; build requirements BR-1 to BR-5 | list taken at the lifted level suffices for soundness and knowledge of lifted oracles under H7 and H8' (a commitment binds a list: one batched opening per proof, nothing relies on two openings denoting one message); in the list regime a lifted word can have non-lift list members while the original is far from its code; BR-1 to BR-5 make H7, H8' checkable in `yugen-proof-b2` | `binius-johnson-row.md` 5.1 to 5.3 | `5cec7e5`; revision 2 `binius-johnson-row.md` revision 2, `f58faa8`, 2026-11-19 | proof; `johnson-row/test_lifted.py`, `test_lifted_opening.py` (T-J3) | **Original as far as checked** (sources: [Hab-LDR], [Dia25], [DP24], [ACFY24], [DKT26], [CFW26], [SG26] sections read, the Blueprint; [HMH] not read, so prior publication cannot be ruled out). H8' is the internal referee's restatement (R-5); BR-1 to BR-5 ours; referee: holds under H7, H8' |
| O-19 | Lemma F, Lemma UD, the rows | index rounds and `X` folds under MCA, error `(N_line(n_i) + 2 B_list)/|K|` without weights (weighted-to-unweighted step written in revision 2; message dimension 1 by [DKT26] Lemma 3.3); unique-decoding round errors of system B; rows 107 (category 1, Johnson, DKT26 route, `B_list = 19`) and 261 (category 3, unique decoding); revision 1's 102 row withdrawn | `binius-johnson-row.md` 5.4, 6, 8 | `5cec7e5`; revision 2 `binius-johnson-row.md` revision 2, `f58faa8`, 2026-11-19 | proofs; `johnson-row/rowcalc.py`, `test_rowcalc.py`, `test_fold_round.py` (T-F) | Lemma F, **index rounds: Published shape** ([CFW26] Lemma 6.6's sumcheck rounds: rows of an interleaved word folded by a sumcheck challenge, same error and proof; ours instantiates it with [DKT26] as the MCA input); **`X` folds: Adapted** from [Hab-LDR] Lemma 4 (Theorem 4 replaced by [DKT26] Theorem 4.4 / Corollary 6.6 / Lemma 3.3); UD: **Adapted** from [Hab-LDR] Sections 5, 6.1 with [ACFY24] Lemma 4.10 + [BCIKS20] Theorem 4.1; rows: Original (parameter choice); referee: holds under DKT26 with R-3, R-4 (now written) |
| O-20 | Theorem Q; the CMS form (X, C); Observation 1 | the BCS chain with one link per prover message and challenges expanded from the link is QROM-sound with CMS19's constants (form X) or `C1 = 24`, `C2 = 240` (form C); no `lambda`-bit-message transcript fits these IOPs | `qrom-compilation.md` 3 to 5 | `b3ec66f`, `5d995b7`, 2026-11-19 | proof as changes to [CMS19] 8.5.1; `qrom/test_numbers.py` | **Adapted** from [CMS19] Theorem 8.6 (changes: long verifier messages from a long-output oracle, hashed salted leaves, arity, clear messages); form X is [CY-book] Construction 25.1.1's shape with a `lambda`-bit chain value. Observation 1 Original as far as checked ([CMS19] 8, [CY-book] 15, 25, [BGKTTZ23] 3). **Reviewed 2026-11-19 (`qrom-zk-referee.md` 1): superseded as the basis by [SG26] Theorem 6.6 (2) (lead decision D-a); now a record.** Form X: a credible sketch under three extra hypotheses; **form C: unproved** (no write-back; its constants 24, 240 are not established); the "a_V folded" constants were wrong (24, 192, not 12, 96); Observation 1 narrowed to "no transcript with 256-bit digests", its state-restoration step now sourced ([CY-book] Definition 23.2.1, Theorem 31.2.1) |
| O-21 | Lemma X; findings Q-1 to Q-4 | counter-mode expansion costs a factor 2 in quantum queries; A's duplex needs strong RBR (CMS19 8.6), B's iterated expansion has no reduction | `qrom-compilation.md` 3, 4, 7 | `b3ec66f`, 2026-11-19 | proof | Original as far as checked (same sources). Reviewed (referee 1.2, 1.3): Lemma X, Q-1, Q-2 hold; Q-3's reason was wrong (Davies–Meyer fixed points need control of the chaining input; corrected in `qrom-compilation.md` 2.6, the recommendation stands as modelling assumption MA-2); Lemma X is used for B's counter-mode alternative to spBCS |
| O-22 | Lemma M (full), Lemma H, Theorem ZQ; the Grover attack on 256-bit salts | salted Merkle hiding `t N_u / 2^s`; unbounded hiding summed over a proof; quantum zero knowledge of the CMS form at `zeta_IOP + sum N_u 2^(-(s-256)/2)`; a witness-holding distinguisher breaks 256-bit-salt hiding with about `2^128` quantum queries | `zk-quantum.md` 1 to 3 | `21f16e0`, 2026-11-19 | proofs; `qrom/test_numbers.py` (salt table, exact toy check of [CY-book] Claim 3.4.1) | **Relabelled 2026-11-19 (referee 2.2, 2.4).** Lemma H: **Published**, [SG26] Definition I.1 (`eps_leaf`, derived there from [CY-book] Claims 3.4.1, 3.4.2) and its use per leaf in the proof of Theorem I.5. "No statistical zero knowledge at salts as long as the digest": **Published**, [SG26] Section 8.4 and [CY-book] Claim 3.4.1. Lemma M: **Adapted** from [CY-book] Lemma 17.3.1, Claim 17.3.2, Remark 18.6.2 (reviewed: holds). Theorem ZQ: Adapted from [CY-book] Theorem 26.2.1 and [CMS19] Lemma 7.3; **superseded** by [SG26] Theorem 6.6 (3) (its non-adaptive premise is false for node proofs; no multi-proof composition). The attack: necessity of salts [Dia25] 4.1; the `2^128` Grover cost is **Original as far as checked** ([SG26] 8.4 checked: it states the gap "gives no attack ... by an adversary with a bounded number of hash queries" and gives no quantum attack), under the hypothesis that unopened rows are determined (referee 2.3) |
| O-23 | Theorem S0; Lemmas F0, O0, C0, B0; finding W-1 | round-by-round soundness of leanVM's plain WHIR over binary additive codes in unique decoding; the query terms need the true rate `(2^mu + kappa)/2^(mu + r)`, row 9 is 4.36 bits short at rate 1/2 | `whir-additive-soundness.md` | `3dc548a`, 2026-11-19 | proofs; `qrom/test_numbers.py` | **Adapted** from Theorem S (O-7) without masks; template [ACFY24] Theorem 5.2; the degree growth is read from the pinned verifier's code ([CWYZ26] Theorem 5.2 is for the equal-degree combiner and is only consistent with it; corrected 2026-11-19, referee 3.2); W-1 Original as far as checked ([ACFY24] 4, 5; [CWYZ26] 1, 5). Reviewed (referee 3): holds, numbers reproduce |
| O-24 | Lemma K | round-by-round knowledge of system B as built (CMS19 Definition 8.5, per-round errors) with errors equal to the round-by-round soundness errors, in both regimes; extractor: complete list decoding of the first oracle at its lifted level, test of at most `B_list` low blocks against the relation; compiled by [SG26] Theorem 6.6 (2) | `binius-johnson-row.md` 7 | revision 2 `binius-johnson-row.md` revision 2, `f58faa8`, 2026-11-19 | proof; `johnson-row/test_lifted_opening.py` (extraction at the lifted level, toy) | **Adapted**: extraction by list decoding is [ACFY24] Theorem 7.5's pattern (and FRI's, [BGKTTZ23], per [DKT26] Section 1.1); the state function set to 0 through the first commitment follows [CMS19] Definitions 8.3, 8.5; [CFW26] Lemma 6.6 proves knowledge for its sumcheck rounds with an erasure-correction extractor (a different extractor). Ours: its application to system B with the lifted list (Lemma J3) and H8'; unreviewed |
| O-25 | The true-rate schedule rule | every query round of system A at 153.0 bits or more at its TRUE rate: `q_i = ceil(153.0 / -log2((1 + rho_i)/2))`, `rho_i = (2^mu_i + kappa_i)/2^(mu_i + r_i)`, computable at setup from the shape; equals the published list wherever `mu_i` is large; corrected schedules of rows 7 to 9 | `soundness/` revision 5 (`revision5.rule_count`, `rule_counts`, CHANGELOG revision 5 section 1); `design-basis.md` 2a | `30e0f17`, 2026-11-19 | `soundness/tests/test_revision5.py` (each count less by one fails; the old list fails at rate 1/2 for every node stack) | **Original as far as checked** (sources consulted: [ACFY24] Sections 4, 5 (query counts from the nominal rate of smooth codes; no combiner growth); [CWYZ26] Sections 1, 5 (the growth, no query rule); [ethSTARK] Section 6.3; leanVM's `params.rs` and `derive_config_for` (the nominal-rate list it derives from)). It is the list's own derivation (`parameters.md` 2.1) with the rate corrected, a parameter rule rather than a theorem; unreviewed |
| O-26 | Cost model of the true-rate schedules | opening bytes of a proof (`whir.size_bytes`), Keccak-f to verify one child in its parent (full paths, no sharing, `revision5.keccak_per_query`), cycles as Keccak-f times the measured cycles per modelled Keccak-f (`recursion.md` 9.10) | `soundness/` revision 5 (`revision5.keccak_total`, `cycles_per_keccak`); CHANGELOG revision 5 section 1 | `30e0f17`, 2026-11-19 | the revision-5 tables; measured anchors (M) | **Original as far as checked** (sources consulted: the papers of 1.1 to 1.1d as read; none models the in-circuit cost of a recursive verifier per opened position); an engineering estimate (E), not a result; unreviewed |
| O-27 | spBCS instantiation for systems A and B; the message-count model | byte-level encodings within [SG26] Section I.1's freedom: part tags `0x10`..`0x13` (A) and `0x20`..`0x23` (B), labels, the proof salt's place, items without lengths in the fixed schedule, deduplicated positions, B's leaf tag, the running hash state per challenge; `N_V` = listed rounds + `OTHER_ROUNDS`, one prover message before each, `m = 2` | `qrom-compilation.md` 2, 4; `soundness/revision6.py` | `471909e`, `cf4d0f9`, 2026-11-19 | `soundness/tests/test_revision6.py`; `qrom/test_numbers.py` | **Original (the Ycash developers, 2026)** as an engineering instantiation of a Published construction ([SG26] Protocol 6.5, I.1; the running-state note is the referee's, `qrom-zk-referee.md` 4 (i)); unreviewed |
| O-28 | Theorem ZP (privacy of the published record) | the record (both systems' leaf proofs for `Q` adaptively chosen transfers, and node proofs whose witnesses hold nothing secret) is simulated within `eps_zk^A(t + Q q_B + q_N, Q) + eps_zk^B(t + Q q_S^A + q_N, Q)`; `2^-85.4` at the pool (`Q = 2^20`) plus the `eps_hvzk` terms; the node-witness check (nothing secret in either system's node witness) | `zk-quantum.md` 3.3, 4 | `7c322f8`, 2026-11-19 | proof (two hybrids); numbers `soundness/` revision 6 | **Original as far as checked** as a composition (sources consulted: [SG26] 6, I.2 (its theorems are per argument system; the hybrid technique of applying assignments on top of the oracle is theirs, Theorem I.5 step 2 (ii)); [CMS19] 7; [CY-book] 26); unreviewed |
| O-29 | Finding Q-5 | for the spBCS transcript the published classical bound ([SG26] Theorem 6.6 (2), ROM) charges the verifier's `k_q` at `t = 1`: condition C needs 158.8 bits a round in the "every `t`" convention (rows miss by 5.8), 144.3 for `t >= k_q` | `qrom-compilation.md` 6.2; `soundness/spbcs.classical_need` | `856c9ea`, 2026-11-19 | `test_finding_q5_classical_need_under_the_rom_part` | **Original (the Ycash developers, 2026)**: a consequence of [SG26] Theorem I.16 (2) and [CY-book] Remark 25.1.3 (no theorem for the whole-past variant); decision pending (T-6); unreviewed |
| O-30 | Route F for B's unsalted fold trees | Theorem 6.6 (3)'s proof adapted to trees the IOP simulator outputs in full (positions removed from `n_pos`, HVZK of the full view) | `zk-quantum.md` 5.1 | `7c322f8`, 2026-11-19 | argument; D25 Theorem 4.3 simulator step 5 for the BaseFold opening | **Adapted** from [SG26] Protocol I.4 step 2 and Theorem I.5 step 3 (change: unsalted trees built from full simulated strings); not adopted (route S, the published theorem, is recommended); unreviewed |
| O-31 | Findings H-1.2 to H-1.6 and MA-2' | BLAKE3's claimed 128 bits equal the classical level category 1 rests on (no number changes); the QROM hash term rests on a heuristic the designers do not claim; BLAKE3 (and SHA-256) are inadmissible at category 3, which needs SHA-384 or SHA3-384 for B's trees; as built, B's BLAKE3 leaves and nodes are not separated (H5 fails for 64-byte leaf encodings); MA-2' models leaves and nodes as BLAKE3 `derive_key` values | `decision-b-merkle-hash.md` 9 | revision 2 of that document, 2026-11-19 | argument from [B3] 2.4, 4.1, 4.3, 7.7 and `soundness-method.md` 8; build read at `yugen-proof-b2` `af0f56d` | **Original (the Ycash developers, 2026)** as consequences for this project of Published claims ([B3], [B3-ID]); sources consulted: [B3], [B3-ID], [SG26] I.1; unreviewed |
| O-32 | Framing of system B's Merkle leaves and nodes with BLAKE3 | `derive_key(C_leaf, ser(values) || r)` with the salt as the final block alone, `derive_key(C_node, left || right)` as one compression (`d = 0x4b`); no levels, positions or tags; transcript unchanged; compressions per leaf and node | `decision-b-merkle-hash.md` 9 H-1.7 | revision 2 of that document, 2026-11-19 | compression counts checked with a minimal implementation against [B3-ID] Appendix B and the `blake3` crate's vector; not built | **Adapted** from [B3] 2.3, 6.2 (derive_key, context strings) and 6.3 (keyed hashing with `hash(label)` for domain separation); change: contexts name Merkle parts, the material is public; a proposal for the builder and the referee; unreviewed |
| O-33 | Category 5 target | `cat5` as conditions C 256, Q 128, G 256, H 512 (attack rule) / 520 (proven rule), by the pattern of `soundness-method.md` 8.3 | `decision-security-category.md` 1.2 | `85783d3`, 2026-11-19 | `category_study.py` `CAT5`; per-round need 280.52 for 20,000 proofs | **Original (the Ycash developers, 2026)** as far as checked (sources consulted: `soundness-method.md` 8, [SG26] Theorem 6.6, [B3]); the NIST text is not in the folder; unreviewed |
| O-34 | Category 3 and 5 rows of systems A and B | A: 321/222/219/218 (leaf), 522/238/... (node) at `2^256`; 415/288/283/282, 676/308/... at `2^384`; B: 261 and 338 queries; fields needed 241/248 (cat3) and 305/312 (cat5) bits; 48 / 64-byte digests for the QROM hash term; salts 96 B and 80 / 112 B | `decision-security-category.md` 3 | `85783d3` to `a5efff1`, 2026-11-19 | the calculator's functions (`wi.solve`, the trim of `revision5.minimal_counts`, `binius64`, `johnson.terms`, `spbcs`); cat1 reproduces the certified rows | **Original (the Ycash developers, 2026)**: the rows; the bounds Published ([CY-book], [BCIKS20], [SG26]); unreviewed |
| O-35 | Cost and capacity scalings by category | A's per-child factor `s (q_x/q_1) h + (1 - s) a` with `s = 0.80`; B's slot rows by queries and hash, padded; capacity under W5 with 200-byte records; `W` and `LEAF_RESERVE` per category | `decision-security-category.md` 4.3, 4.4 | `85783d3`, 2026-11-19 | measured anchors of `yugen-proof-a` `recursion.md` 9.10 and `yugen-proof-b2` `parameters.md` 9; estimates | **Original (the Ycash developers, 2026)**; estimates only; unreviewed |
| O-36 | Profile M-1 | secrets and privacy at category 5, proof soundness at category 3, with the shared parts (Falcon, statement digests) at or near the privacy level; argument from two systems, canaries and the pause, with its limits | `decision-security-category.md` 6, 7 | this document, 2026-11-19 | argument | **Original (the Ycash developers, 2026)** as far as checked (sources consulted: the plan 0, the specification 13); unreviewed |
| O-37 | Findings H-1.11 (model mapping), H-1.13, H-1.14, H-1.16, H-1.17 | system B's BLAKE3 nodes and leaves are in the hash-function model (fixed state, chosen message), where attacks on the BLAKE/BLAKE2 family reach 3.5 rounds; [EFK15]'s free-state pseudo-preimages are trivial for BLAKE3's truncated output (no chaining-value feed-forward), so they are no margin figure for it; the full-round weak-key property of BLAKE2's permutation ([GKNWW14] 3) carries over to BLAKE3's `E`, so MA-2' is restated for IV-constrained inputs, not as an ideal cipher; verdict on Q-H2 (open, conclusion unchanged); [TMC]'s Q2 argument does not separate cases for a public hash in the QROM | `decision-b-merkle-hash.md` 9b | `8c31f13` (revision 3 of that document), 2026-11-19 | argument from the cited sections; no test | **Original as far as checked** (sources consulted: [GKNWW14] in full, [EFK15] 1 to 3 and 5, [B2] in full, [TMC] in full, [B3], [B3-ID]; none states these points for BLAKE3; [B3] 4.2 and 7.3 state the inversion for the full output and the role of the feed-forward, which H-1.13 (a) applies to the free-state model); unreviewed |
| O-38 | Category derivation from the NIST text (calculator revision 7) | each category as conditions C (kappa_C = key bits, or half the hash length for collision categories, in oracle calls), Q (kappa_Q = kappa_C / 2), G (attack bits kappa_C a round, premise: an oracle call's quantum depth x size at least the reference primitive's), H (2 kappa_C-bit digests); categories 2 and 4 coincide with 1 and 3 in oracle calls | `soundness-method.md` 8.7; `soundness/src/yugen_soundness/category.py` | revision 7 of the calculator, 2026-11-19 (this commit series) | `tests/test_revision7.py` (derived targets equal revision 6's `cat1`, `cat3`; NIST's gate figures; needs 152.52 / 216.52 / 280.52) | **Original (the Ycash developers, 2026)** as conventions applying [CFP] 4.A.5 (Published figures); checked against [CFP], [FIPS204] Table 1 and D.1, [FIPS205] 11, `security-category-referee.md` 1 and 3; extends O-13 and O-33; unreviewed |
| O-39 | Revision 7 rows and findings | certified rows of both systems at any category with field, digest, salt and tree hash as inputs and hard refusals; findings: system A needs a 312-bit field at category 5 for nodes of `2^30` at rate 1/2 and 313 at rate 1/4 (B the same at 1/8 and 1/16); row 8 (masked in a tree) has no admitted stack at rate 1/2 at categories 3 and 5; at category 5 B's zero-knowledge leaf (1,799 KiB, E) and most nodes exceed `PROOF_BYTES_MAX`; the largest category 3 proof (A node `2^30`, rate 1/2) is 41,799 B under it (E) | `soundness/CHANGELOG.md` revision 7; `design-basis.md` 2a; `soundness-method.md` 8.7 | revision 7, 2026-11-19 | `tests/test_revision7.py` (each count less by one fails, every row of categories 1, 3, 5) | **Original (the Ycash developers, 2026)**: the rows (parameter choices) and findings; the bounds Published ([CY-book], [BCIKS20], [SG26]); the category 3 / 5 schedules reproduce O-34 independently; unreviewed |
| O-40 | Zero-knowledge target and salt floors | a pool target (`2^-64`, `2^-96`, `2^-128` over `2^20` leaf proofs, excluding `Q eps_hvzk`) gives the leaf salt from the leaf term alone (75 / 83 / 91 B at 48-byte digests, 91 / 99 / 107 B at 64) and the proof salt from `4 Q t / 2^(4 b_s)` at `t = 2^kappa_Q` | `soundness-method.md` 8.7; `category.py` | revision 7, 2026-11-19 | `tests/test_revision7.py::test_salt_floors_from_a_zero_knowledge_target` (agrees with the referee's R6) | **Original (the Ycash developers, 2026)** as an application of [SG26] Theorem 6.6 (3); proposed by the referee (`security-category-referee.md` 3.4, F-4); unreviewed |
| O-41 | Hidden-key reading of the spend authority's level (**superseded by O-61**, 2026-11-19) | with `pk` never published and hidden in `sig_d = H_sig(0x01 || pk || salt_d)`, Falcon-512 is a level-1 second factor behind a level-5 hiding hash until `pk` leaks; Falcon-1024 is required only under the public-key convention | `security-category-referee.md` 2.2 (restates the plan's section 9 remark) | `44e300d`, 2026-11-19 | argument; spec 4.4, 5.1, 13.1.2 | **Original (the Ycash developers, 2026)**; checked against [CFP], [FIPS204], [FIPS205], [GLS26]; unreviewed; used and extended in `decision-security-profile.md` 2.3. The referee of that record (`security-profile-referee.md` 3.1) showed the "1 behind 5" label misframed: correct is O-61 |
| O-42 | Shared-versus-per-system level rule; profile P6 | parts the two-system design protects (rows, proof-internal hash, field) at category 1, shared statement-level parts one level higher, privacy at 5, every row parameter generic | `security-category-referee.md` 8.2, 8.3 | `44e300d`, 2026-11-19 | `referee_check.py` R7 (capacity) | **Original**; unreviewed; tested in `decision-security-profile.md` 5 (O2) |
| O-43 | Binding collisions bypass the two-system defence | a collision in `H_cm` or `H_nkc` makes a true statement that both systems prove; only the outflow caps and the ratchet bound it | `security-category-referee.md` 6 | `44e300d`, 2026-11-19 | argument | **Original**; unreviewed |
| O-44 | The W4 violation | measured category-1 leaves (600,340 + 583,680 B) plus 17,456 B exceed `LEAF_RESERVE` = 1,150,000 | `security-category-referee.md` 4.3 | `44e300d`, 2026-11-19 | `referee_check.py` R7 | **Original**; confirmed and enlarged in `decision-security-profile.md` 0 item 2 (O-53) |
| O-45 | Category 3 capacity is zero at `W` = 4 MB | with the category's own `LEAF_RESERVE` (about 1,972,000 B, now about 2,200,000 under revision 7) W5 leaves less weight than the root proofs | `security-category-referee.md` 4.3 | `44e300d`, 2026-11-19 | `referee_check.py` R7; `profile_study.py` S4 | **Original**; unreviewed |
| O-46 | Privacy ceilings of retrieval and transport | two-server DPF with 128-bit seeds is category 1, the single-server lattice PIR below 1, the hybrid transport with ML-KEM-768 category 3; record-now-break-later applies to all three | `security-category-referee.md` 2.1, 6 | `44e300d`, 2026-11-19 | argument; `yugen-pir/docs/pir-selection.md` | **Original**; unreviewed |
| O-47 | Gap between the proven QROM query bound and NIST's quantum budget | condition Q's `2^96` (`2^128`) queries cover less than [CFP]'s category 3 (5) budget at any MAXDEPTH; the quantum half of categories 3 and 5 rests on the attack estimate G | `security-category-referee.md` 3.3 | `44e300d`, 2026-11-19 | arithmetic on [CFP] page 18 | **Original**; unreviewed; adopted in `soundness-method.md` 8.7 (revision 7) |
| O-48 | The referee's recomputation | closed forms independent of `category_study.py`: per-round needs (R1), B's unique-decoding counts (R2), field bits by the largest algebraic term, correcting A's category-5 need to 312 bits (R3), minimality of each of A's counts by the calculator's round list (R4), the QROM digest floor `8b >= 3 kappa_Q + log2(12 c' N)` (R5), leaf-salt floors from a pool target (R6), capacity under W5 with the category's reserve and W4 (R7), B's host rescaling (R8) | `category-study/referee/referee_check.py`; `security-category-referee.md` R1 to R8 | `44e300d`, 2026-11-19 | the script's own output; agreement with revision 7 (`tests/test_revision7.py`, salt floors) | **Original (the Ycash developers, 2026)** as derivations from [CFP], [SG26] Theorem 6.6 and the calculator; unreviewed |
| O-49 | Per-goal security profile Y | privacy and retrieval at 5, binding at 4 (48-byte collision-dependent digests), Falcon-512 hidden with Falcon-1024 ready and recovery mode as hedge, soundness at 1 in each of two systems with generic rows; options O1 to O6 priced against E1, E2, W1 to W5 | `decision-security-profile.md` 0, 2 to 6 | this commit series from `8fe8093`, 2026-11-19 | `profile-study/profile_study.py` S1 to S5 | **Original (the Ycash developers, 2026)**; extends O-36, O-42; unreviewed |
| O-50 | Binding classification and the 48-byte set | which of the specification's digests need collision resistance (`cm`, `nkc`, tree leaf and nodes, registry, `leaf-pi`, bundle digests, `bstmt`) and which need only second preimage or owner-only collisions; cost by count (A +40 Keccak-f; B +24,000 AND rows, `2^17` to `2^18`) | `decision-security-profile.md` 2.2 | as O-49 | `profile_study.py` S3 | **Original**; extends O-43 and the referee's 2.1; unreviewed. **Corrected in revision 2** (`a642cd9`): `rho` and the transfer hash added (O-57, O-58), the statement layer moved to 32 bytes as window-bound (O-62) |
| O-51 | Anchor-window bound on soundness attacks | all public inputs, `anchor_root` included, enter every transcript before the first challenge, and an anchor is valid for at most 96 blocks: a Fiat-Shamir forgery must be found inside that window in both systems; binding searches have no window | `decision-security-profile.md` 1 | as O-49 | argument (spec 8.1, A-3) | **Original**; unreviewed. **False as specification 0.3.4 stands** (O-56: `E_20`, the first root and quiet stretches are predictable); holds only with fix F-1, as revision 2 (`a642cd9`) 1.1 states |
| O-52 | Work-over-advantage reading of the proof-salt term | the term `4 Q t / 2^(4 b_s)` of [SG26] Theorem 6.6 (3) gives `t / eps >= 2^(4 b_s - 22)` independent of `t`: 2^298 at 80 bytes; floors 70 B (category 5), 54 B (category 3); explains revision 7's `2^-42` column | `decision-security-profile.md` 2.1 | as O-49 | `profile_study.py` S2 | **Original** as an application of [SG26]; unreviewed. **`Q` corrected** to the lifetime count in revision 2 (O-64): floors 74 / 78 B |
| O-53 | W4 magnitude and the `LEAF_RESERVE` rule | with A's row 8 leaf (692,504 B) the breach is 143,640 B, 202,520 B with B's 512-bit salts and route S; `LEAF_RESERVE` derived from the certified leaf rows | `decision-security-profile.md` 0 item 2, 7 W-1 | as O-49 | `profile_study.py` S1, S4 | **Original**; extends O-44; unreviewed. Revision 2: the reserve from measured leaves plus counted deltas, 1,389,000 to 1,403,000 B (`profile_study.py` S6) |
| O-54 | Tree arity count at 48 bytes; rejected tree alternatives | no arity from 2 to 16 is below 40 Keccak-f a path at 48-byte nodes; TurboSHAKE256 nodes (cost of today in B) and chain-entropy leaves (time-bounded search, no category change) evaluated and not chosen | `decision-security-profile.md` 2.2 | as O-49 | counting | **Original as far as checked** (sources consulted: [CFP], the specification); unreviewed |
| O-55 | Message recovery for a signature verified inside a proof | [GLS26]'s mode saves no byte when signature and key are witness and the message is a verifier-computed public input, and its verification costs at least F2 to F5 | `decision-security-profile.md` 3.3 | as O-49 | argument on [GLS26] Algorithms 3, 4 | **Original**; unreviewed |
| O-56 | Predictable statements and fix F-1 (R-1) | below activation the anchor root is the constant `E_20`, the first post-activation root is a constant, and quiet stretches repeat the root, so a forgery can be precomputed offline; F-1 binds the block hash at the anchor height into the transfer hash (hence P7) and refuses anchors below activation | `security-profile-referee.md` 1.1, 1.3; adopted in `decision-security-profile.md` revision 2, 1.1, task F-1 | `483b99d` (referee), `a642cd9` (adopted), 2026-11-19 | argument against spec 0.3.4 §6 l. 614, §8.1 l. 822, A.3 (lines checked in revision 2) | **Original (the Ycash developers, 2026)** as far as checked ([CFP]; [SG26] Theorem 6.6 and Section 6.1 discuss statement freshness only as a property of their extraction notion, not the freshness of a chain anchor); relates to SPEC-19; unreviewed |
| O-57 | Faerie gold through `H_rho` (R-2) | for a dummy first spend `dx` is free witness, so an offline `H_rho` collision gives two identical commitments to one recipient with one nullifier; fixes: `rho` at 48 bytes and the rule that a commitment equal to an earlier applied one is never credited | `security-profile-referee.md` 2.3; adopted in `decision-security-profile.md` revision 2, 2.2 | `483b99d`, `a642cd9`, 2026-11-19 | argument against spec §5.4 l. 543, C3.i | **Original as far as checked** (the attack class is known from Zcash's design, from memory, not in the folder; its route through `H_rho` and free dummy witnesses is new here); unreviewed |
| O-58 | Transfer-hash collisions under split custody (R-3) | the online host chooses the bytes an offline signer cannot check and builds the broadcast transfer, so a transfer-hash collision is host-chosen; the transfer hash goes to 48 bytes | as O-57, 2.2 | as O-57 | argument against spec §4.4, §7.3, §7.7 | **Original** as far as checked ([CFP], [GLS26]); unreviewed |
| O-59 | The DPF PRG at 256-bit seeds is unspecified (R-4) | the built crate (`dpf-fss` 0.6.1) fixes 128-bit seeds under a fixed-key AES-256 Hirose PRG; λ = 256 needs a named PRG (revision 2 names AES-256 keyed by the seed in counter mode, ChaCha20 as the measured alternative) and a re-measured E5 | `security-profile-referee.md` 4; `decision-security-profile.md` revision 2, 2.1, W-4 | as O-57 | reading of `yugen-pir/docs/pir-selection.md` | **Original** (finding); the PRG named is a standard construction, from memory; unreviewed |
| O-60 | Seed entropy caps every derived level (R-5) | a seed is "32 to 64 bytes" by length, not entropy; a 12-word mnemonic makes every derived key category 1; rule: at least 256 bits, 12-word mnemonics refused | `security-profile-referee.md` 4; `decision-security-profile.md` revision 2, 2.1, W-2 | as O-57 | argument from [CFP]'s category definitions | **Original** as far as checked ([CFP]); unreviewed |
| O-61 | Split-custody reading of spend authority; `0x02` readiness list | Falcon-512's level is 5 against everyone outside the wallet's devices (the spend needs 256-bit secrets no viewing key holds) and 1 against a compromised proving device (offline key recovery, every address of the account); scheme `0x02` needs six specification items (registry, key path, scheme on the wire, bundles, migration, circuits) | `security-profile-referee.md` 3.1, 3.3; `decision-security-profile.md` revision 2, 2.3 | as O-57 | argument against spec §3.2, §4.4, §4.5, §11.1.1, §11.2, SPEC-5 | **Original**; supersedes O-41; unreviewed |
| O-62 | Window-bound statement layer; system A's 32-byte public input | `lpi`, the bundle digests and `bstmt` hash fresh public inputs (after F-1), so their collisions are online like soundness and 32 bytes suffice; system A binds them through 32 bytes anyway (256 public bits) | `security-profile-referee.md` 2.3; `decision-security-profile.md` revision 2, 2.2 | as O-57 | argument against spec A.1 l. 3007, §15.3 | **Original**; unreviewed. Revision 2 classes A's `E_A(pi)` as a per-system part (a collision fools A only), not a shared one |
| O-63 | Tree-hash variants by committed words; A's layout risk | B's 2^17 limit binds on committed words as well as AND rows: TurboSHAKE256 nodes keep B at 2^17 by about 148 words, Keccak-f at capacity 384 ternary needs about 7,000 freed words, the FIPS 4-ary node goes to 2^18; a 4-ary 48-byte node straddles A's 16-byte cells across the block boundary unless aligned | `security-profile-referee.md` 5; `profile_study.py` S9; `decision-security-profile.md` revision 2, 3.5 | `483b99d`, `d5a8108`, 2026-11-19 | counts from `yugen-proof-b2` parameters.md 10.4 and statement-layout.md 1 (C), the word rule (E) | **Original**; unreviewed; F-2 counts in circuit |
| O-64 | Lifetime proof count in the zero-knowledge target | Theorem 6.6 (3) counts every proof the adversary sees: at Y's capacity 2^22.3 leaf proofs a day, 2^36.4 in fifty years; at `Q = 2^37` the floors are leaf 79 B (A), 79 B (B), proof salt 74 B (2^256) / 78 B (2^272) | `security-profile-referee.md` 4; `profile_study.py` S7; `decision-security-profile.md` revision 2, 2.1 | `483b99d`, `d5a8108`, 2026-11-19 | `spbcs.eps_leaf_log2` (calculator unchanged) | **Original** as an application of [SG26] Theorem 6.6 (3); corrects O-40's and O-52's `Q = 2^20`; unreviewed |
| O-65 | Binary framed SHAKE256-384 note-tree node (T1b); the 8-byte-tag length clash | a binary node `Yg 00 id l ‖ 0^11 ‖ c0 ‖ c1` (112 bytes) is one permutation a level, 40 a path as the 4-ary two-block form, with both children whole 16-byte cells in system A, no extra sibling bytes and separation by `id`; with Q1's 8-byte part tags A's spBCS stream point would be 104 bytes, the length of Falcon's hash-to-point input whose first byte is random, so the length separation of spec §3.3 fails (the as-built 16-byte tag gives 112 bytes) | `decision-security-profile.md` revision 2, 3.5; `profile_study.py` S9; `qrom-compilation.md` 2.8 A-1 | `eda3813`, `a642cd9`, `e41de26`, 2026-11-19 | counting; spec §3.1, §3.3 | **Original as far as checked** (sources consulted: the specification §3.1, §3.3, §6; [CFP]; `yugen-proof-a` parameters §2.5); unreviewed |
| O-66 | The builders' spBCS deviations against Theorem 6.6 (2); Lemma D | A's 16-byte tags, first challenge at byte 32 and block form, B's `pre(x)` length, 4-byte masked indices and BLAKE3 `derive_key` framing (under MA-2') keep the theorem's hypotheses; B's repeated positions do not, and Lemma D reduces them to the de-duplicated protocol plus a collision event (or none, with an equality check) | `qrom-compilation.md` 2.8 | `e41de26`, 2026-11-19 | argument against [SG26] Definition 2.18, Protocol 6.5, Theorem 6.6, Section I.1 (read); the builders' vectors | **Original (the Ycash developers, 2026)**; Lemma D (ii) rests on a QROM collision bound from memory (Zhandry), to be read; unreviewed |
| O-67 | Calculator revision 8: system B's Johnson-regime rows term by term | every per-round term of the 107 / 80 rows and of system B's node at rate 1/4 (unique decoding 225, Johnson `m = 10` 165; 171 under Q-5 (b)), with DKT26's exact count evaluated at our threshold and hard refusals outside the theorems' hypotheses; the T-J3 step-5 test at message dimension 1 (the second referee's construction) | `soundness/src/yugen_soundness/dkt26.py`; `soundness/CHANGELOG.md` revision 8; `binius-johnson-row.md` 2.1 (5.4, 11) | `727efbf`, `d8682d7`, 2026-11-19 | `soundness/tests/test_revision8.py` (28 tests, among them the bit-for-bit agreement with `johnson-row/rowcalc.py`); `johnson-row/test_lifted_opening.py` | **Original (the Ycash developers, 2026)** as an application: the formulas are [DKT26]'s (Theorem 4.4, Lemma 3.3, Lemma 6.5, Corollary 6.6), [Hab-LDR] Lemma 3's, [ACFY24] Lemma 4.10's and [SG26]'s, the round assembly is `binius-johnson-row.md`'s (O-17, O-19); the step-5 construction is the second referee's (`johnson-row-referee-2.md` 2.2). Sources consulted: those papers' sections listed in 1.1b. Unreviewed |
| O-68 | Calculator revision 9: every row of both systems under "every t" | the classical tree need taken at `t = 1` with each proof's own `k_q` ([SG26] Theorem 6.6 (2) read for every `t`), each row solved to its least fixed point: B 192 / 111 / 82 / 174 / 235 / 171 (were 184 / 107 / 80 / 168 / 225 / 165), A +4 to +15 queries a level, QROM 69.58 / 70.45; the book need only as a labelled non-default option | `soundness/src/yugen_soundness/category.py`, `dkt26.py`, `cli.py`; `soundness/CHANGELOG.md` revision 9; `decision-qrom-counting.md`; `soundness-method.md` 8.9 | revision 9 commit, 2026-11-19 | `soundness/tests/test_revision9.py` (76 tests: the counts, the minimality of every count at its own need, the labels, the refusals, an exact recomputation of DKT26 (36), (37) at the referee's boundary cases) | **Original (the Ycash developers, 2026)** as an application of [SG26] Theorem 6.6 (2) and Definition I.1; the counts reproduce `soundness-rev8-referee.md` section 7. Sources consulted: [SG26] Section 6.3, Appendices H, I.1. Unreviewed (draft until refereed) |
| O-69 | Lemma M (proposal, NOT adopted, UNPROVED) | an accepted proof forces the adversary to have queried every Merkle-path hash the verifier evaluates, except with probability `k_q / 2^(8b)`; so for `t >= k_min` the need would be `kappa_C + 1 + log2 N + log2(1 + k_q / k_min)`, restoring the book counts for every `t` | `soundness-rev8-referee.md` section 7 (first statement); `decision-qrom-counting.md` 2.3 | `b8f30bc`, 2026-11-19 | none: a sketch; `k_min` per shape not derived | **Original as far as checked (the Ycash developers, 2026; the referee's proposal)**; sources consulted: [SG26] Section 6 and Appendix I (no such statement found); unproved, unreviewed; recorded as possible future work by the lead architect's ruling |
| O-70 | Lemma D written: duplicate openings under spBCS (Propositions D.1, D.2, D.Z; Theorem D, Adapted; Corollary D-bb) | a verifier that checks several openings of one position against one root without comparing them (conditions D-1 to D-5; system A's flag walk under W-1 to W-7, A's `open_stacked`, B's in-circuit verifier) keeps the bounds of [SG26] Theorem 6.6 (2) with the same constants at the `k_q` that counts drawn queries: unequal copies are a digest collision of the database, already in the bad set of [SG26] Lemma I.12 (the `+ 1` of `c'`); extra term 0 bits; the black-box form costs 0.0002 bits of the hash term | `docs/lemma-d-duplicate-openings.md` | this commit, 2026-11-19 | proof against [SG26] Protocol I.9, Definition I.13, Lemmas I.12, I.14, I.15, Theorem I.16 and [CMS19] Lemmas 4.9, 5.7, 6.11 (read from the text layer); no test (a proof) | Theorem D **Adapted** from [SG26] Theorem I.16; the propositions and conditions **Original (the Ycash developers, 2026)**; supersedes O-66's Lemma D (ii) and its from-memory Zhandry citation; **refereed, pass with conditions (docs/lemma-d-referee.md)**; conditions m-1 to m-4 applied 2026-11-19 (D-4 counts every checked record, padded slots included; the calculator counts them since revision 10) |
| O-71 | Lemma P: shared-challenge parallel composition of reductions (DRAFT) | reductions with round-by-round soundness errors, run in aligned rounds with ONE challenge a round used by all of them, compose to a reduction whose error at a round is the largest of the active reductions' errors (no factor for the number of reductions) | `decision-b-parallel-batching.md` 5 | this commit, 2026-11-19 | proof in the record; no test of record yet (PB-T8 asks system B for an exhaustive toy check) | **Original as far as checked**, unreviewed. Checked against: [SG26] Definition 2.24, Lemma 2.27 (2) (parallel composition with independent challenges), Lemma 5.2 (merged verifier messages, product challenge set, sum of errors); [AF21] abstract, 1.1 to 1.3, Theorem 4; the text layers of [CMS19], [DP24], [Hab-LDR], [ACFY24], [CFW26] searched for a shared-challenge or parallel sumcheck statement, none found |
| O-72 | Lemma R: the state function of system B's batching reduction as coded | `batch::reduce` has round-by-round soundness errors `(K - 1)/\|F\|` at `alpha`, `2/\|F\|` a round, `(n_sets - 1)/\|F\|` at `mu`, in the sense of [SG26] Definition 2.24 (a) | `decision-b-parallel-batching.md` 5 | this commit, 2026-11-19 | proof in the record; system B's `tests/batch.rs` (theirs) | **Adapted** from the textbook sumcheck analysis ([SG26] Section 5, p. 45, states the degree-2 round error); ours: the state function for the code's `alpha` step, implicit linear coefficient, prover-supplied finals and `mu`. Unreviewed |
| O-73 | Finding PB-3: late joining with fixed coefficients is unsound in characteristic 2 | a batched sumcheck in which a shorter instance's weighted claim is added to the running claim when it starts, with coefficients fixed at the start, is forged with probability 1 over a field of characteristic 2 (a constant added to the previous round polynomial is invisible to `p(0) + p(1)`); `eq(0, .)` padding, or drawing the coefficient at the join, repairs it | `decision-b-parallel-batching.md` 5 | this commit, 2026-11-19 | a throwaway toy run over `GF(2^8)` (200 of 200 forged; padded form 2 of 200), not a test of record; PB-T6 asks for one | **Original as far as checked** (same sources as O-71, and the pinned Binius64 `ip/src/sumcheck/batch.rs`, `ip-prover/src/sumcheck/padded.rs`, which pad). No built code is affected: the form is excluded before anyone builds it. Unreviewed |
| O-74 | Findings T-2, T-3, T-5, T-6 on system B's transcript hash; option (c*) | SHA-256 keys on nested (not prefix-free) challenge inputs are inside no indifferentiability theorem; BLAKE3's extended output is outside its designers' bound (2), so XOF streams would rest on a new modelling assumption; the in-circuit cost of BLAKE3 keys must count tree-mode finalisations (`1 + popcount` compressions a key); which hash failures break which proof system; (c*): BLAKE3 `derive_key` keys with counter-mode 32-byte stream blocks, salt first, under Lemma X | `decision-b-transcript-hash.md` 3, 9 | this commit, 2026-11-19 | arithmetic on system B's counts (E); no test | **Original as far as checked** (T-2, T-3's consequence, T-5, T-6) against [SG26] I.1, [B3] 2.3 to 2.6, 4.1 to 4.3, 7.3, 7.7 and `qrom-compilation.md`; (c*) **Adapted** from [B3]'s `derive_key` and Lemma X. Rests in part on two results cited from memory (Coron et al. 2005; Bertoni et al. 2008), not read. Unreviewed |
| O-75 | Calculator revision 10: the hash term of [SG26] Theorem 6.6 (2) evaluated per row, per proof and over the tree | in the calculator's convention (tree term at most `t / 2^(kappa_C + 1)` for every `1 <= t <= 2^kappa_C`) the hash part of a tree of 20,000 proofs proves 114.74 classical bits (A 114.74 to 114.82, B 114.74; one proof 121.89 to 121.96), not the 126.6 of the book term; a proven classical 128 needs 288-bit digests (`8b >= 2 kappa_C + 1 + log2(N c')`); QROM 75.63 tree / 80.40 proof against 64; the status is computed from checks (R9-2) and the classical hash part is judged on condition H's attack rule by default (`--hash-basis proven` certifies no 256-bit row) | `soundness/src/yugen_soundness/hashterm.py`, `category.py`, `dkt26.py`; `soundness/CHANGELOG.md` revision 10; `decision-qrom-counting.md` 7 | revision 10 commit `e93e57c`, 2026-11-19 | `soundness/tests/test_revision10.py` (closed form, both end points, every row printed, basis proven) | **Original (the Ycash developers, 2026)** as an application of [SG26] Theorem 6.6 (2); confirms `rev9-and-lean-referee.md` R9-1 (114.8 / 114.7; 288 bits). Sources consulted: [SG26] pages 58, 130, 131. Unreviewed (draft until refereed) |
| O-76 | `k_q` as an input with provenance, and the 10 % guard (R9-4); task T-1's report | a row whose `k_q` is the calculator's estimate is certified only if its margin is at least `log2(1 + 1.1 k_q) - log2(1 + k_q)` (0.1375 bits); a transcript-reported `k_q` replaces the estimate (guard 0). At category 1 14 of system A's 20 rows and A row 7 at rate 1/2 are not certified until T-1; every B row keeps its label | `soundness/src/yugen_soundness/hashterm.py`, `category.py`; `decision-qrom-counting.md` 7.3, 7.4 | `e93e57c`, 2026-11-19 | `soundness/tests/test_revision10.py` (the list of rows, a reported `k_q` replacing the estimate) | **Original (the Ycash developers, 2026)**, an engineering rule; the 10 % is a stated allowance, not a bound. Unreviewed |
| O-77 | Padded group slots in system B's `k_q` (Lemma D referee m-1, implemented) | `q_IOP` = query count rounded up to the group unit, in each of six trees (units 2 / 5 / 5 / 4 as built at 192 / 235 / 111 / 82; 6 assumed where no grouping is recorded); `k_q` rises at 111 (24,378 -> 25,170), 82 (19,128 -> 19,536), 171 (35,232 -> 35,808), 385 (74,010 -> 74,940), 226 built (45,792 -> 46,560); no count moves | `soundness/src/yugen_soundness/category.py` `b_counts`, `padded`, `B_QUERY_UNITS` | `e93e57c`, 2026-11-19 | `soundness/tests/test_revision10.py` | the finding is the referee's (`lemma-d-referee.md` m-1); the count **Original (the Ycash developers, 2026)**; units read at `yugen-proof-b2` `0f84f74` `docs/parameters.md` 15.5. Unreviewed |
| O-78 | Lemma TE: knowledge soundness of a proof tree by one straight-line extractor on one table | in the ROM, under (K) round-by-round knowledge soundness of every system (K-A, K-B open), H-DS (one oracle, injective encodings across systems) and H-C2 (the recursion heuristic as a hypothesis on witnesses of a fixed node relation), the extractor that runs the root verifier and then [SG26]'s database algorithm and the child verifiers node by node on one table fails for an accepted root with probability at most `t eps_max + sum_v |J_V,v| eps_v + c'_max (t + K)^2 / 2^(8b)`, `K` = sum of the tree's `k_q`; consequences: no certified count moves; the hash part is taken once for the tree (121.89 classical bits at 256-bit digests, against 114.74 for the per-proof sum); the black-box composition costs +2.3 to +3.9 bits a round on the path (+14.29 in the form `sum_v eps_ex,v(t + N k_q)`); QROM form TE-Q argued, one step from memory | `docs/lemma-tree-extraction.md` | `f414811`, 2026-11-19 | full proof in the document (ROM); `soundness/tests/test_revision10_1.py::test_tree_extraction_hash_level_draft` (the 121.89 figure) | **Original as far as checked** (sources consulted: [SG26] Theorems I.16, I.17, Lemmas I.12, I.14, I.15, Protocol I.9; [CMS19] only as [SG26] cites it; recursive-proof extraction in the wider literature known from memory only, not consulted); Lemma TE.1 **Adapted** from [SG26] Lemma I.12. Revision 1 refereed 2026-11-19 (`docs/tree-extraction-referee.md`: pass with conditions; H-C2 false in the ROM, `B*` not monotone); superseded by O-80 |
| O-79 | Calculator revision 10.1 (after `rev10-referee.md`): one certification function for every row type with the hash basis named in every positive label; the combined `k_q` guard; T-1 reports keyed by shape, refused below the shape's floor, re-solving above the estimate; `c'` with provenance; the stream term at the shortest stream; task T-1 items 5 to 10 | guard = max(10 %, `log2(1 + k_q + named) - log2(1 + k_q)`), `named` = 4 OTHER_ROUNDS + `q_IOP` (A), `q_IOP` (B): A row 7 at 1/4 loses "certified"; floor `4 x` listed rounds `+ 2 x` drawn positions; no query count moves | `soundness/src/yugen_soundness/hashterm.py`, `category.py`, `dkt26.py`, `cli.py`, `spbcs.py`; `decision-qrom-counting.md` 7.2 to 7.10; `soundness/CHANGELOG.md` revision 10.1 | `7607ba1`, 2026-11-19 | `soundness/tests/test_revision10_1.py` (every row type x category x convention x basis; every CLI output; floors; re-solve; `c'`; stream term) | **Original (the Ycash developers, 2026)**, engineering rules; the findings are the referee's (R10-1 to R10-11). Unreviewed |
| O-80 | Theorem TE' and Corollary TE-X; C2 as the named event C2-VIOLATION entering at two places; calculator revision 10.2 | in the ROM, under (K) and H-DS only, the tree extractor that stops at a child its native verifier rejects ends, for every accepted root, with a compliant tree or C2-VIOLATION except with probability at most `t eps_max + sum_v |J_V,v| eps_v + c'_max (t + K)^2 / 2^(8b)` (Lemma TE.1 two-sided); a tree whose every proof is published needs no C2 (TE-X); C2 enters at child acceptance and by keeping the node relation oracle-free; the calculator prints the classical tree hash level 121.89 "under C2, K-A, K-B, T-1" (114.74 beside it) and the QROM 69.58 / 70.45 claimed (76.72 / 77.60 beside it); no query count or status moves | `docs/lemma-tree-extraction.md` revision 2, sections 2, 3, 4, 6, 7; `soundness/src/yugen_soundness/hashterm.py`, `category.py`; `soundness/CHANGELOG.md` revision 10.2 | `44b751d`, `5d7fa81`, 2026-11-19 | full proof in the document; `soundness/tests/test_revision10_2.py` (648 rows pinned against revision 10.1; figures; footer) | **Original (the Ycash developers, 2026), found in referee review** (the restatement, the stop and the two places of C2 are the referee's conditions C-1 to C-5); sources consulted as O-78. Revision 2 **unrefereed** |
| O-81 | Lemma QC: a classical query after a database measurement of the compressed oracle | with the database in a basis state `|D>` below capacity: a fresh `x` gets an exactly uniform answer independent of every other register, and the database then measures `D + [x -> y]` with probability `(1 - 2^-n)^2`; a recorded `x` returns `D(x)` with the database unchanged except with probability at most `10 / 2^n`; hence Proposition TE-Q' with the added term `10 (K - k_q,r) / 2^(8(b+e))`, `log2` -222.91 (A) / -223.09 (B) at category 1 | `docs/lemma-tree-extraction.md` revision 2, section 9a (proof in full), section 9 (the corrected `E_T^Q`); first stated and proved in `docs/tree-extraction-referee.md` 3.2 | `e6a2d23` (referee report), `44b751d` (written into the lemma document), 2026-11-19 | proof in the document; the referee's numerical check for `n = 1..5` (not rerun); `hashterm.lemma_qc_log2`, `tests/test_revision10_2.py::test_lemma_qc_term_is_negligible_in_bits` | **Original as far as checked (the Ycash developers, 2026), found in referee review**; derived from [CMS19] Lemma 3.2 (Published, attributed there to Zhandry); sources consulted: [CMS19] Sections 3.5, 3.6, 4 and page 17, [SG26] Appendix I. **Unrefereed** |
| O-82 | System B round census (leaf 192 at 1/8, node 235 at 1/4) | every challenge of B's native verifier located in the code with its per-message error; weakest algebraic message 234.0 / 226.0 bits, all algebraic challenges merged 232.0 / 225.0 bits, query round 159.37 / 159.35 against needs 158.59 / 158.82: every B row meets its per-round need; discrepancies D-1 to D-4, none binding; R-8 owed | `docs/b-round-census.md` | this commit, 2026-11-19 | code reading at `yugen-proof-b2` `1f67267`; calculator run read-only | **Original (the Ycash developers, 2026)**; uses [SG26] Definition 2.20 and Lemma 5.2, [DP24] Propositions 4.21, 4.24, [Dia25] Theorem 4.2. Unreviewed |
| O-83 | Lemma K-B (draft) | B's IOP is causal round-by-round knowledge sound with the census errors, extractor = unique decoding of the trace oracle; the leaf's inner messages are fixed by the precommit keys before the first challenge | `docs/lemma-k-b.md` | this commit, 2026-11-19 | proof in the document; owed K-B.1 to K-B.5 | **Original (the Ycash developers, 2026)**, transposes Lemma K-A (`theorem-s-referee.md` 4); sources consulted: [SG26] Definitions 2.18, 2.20, Lemmas 2.21, 5.2, Appendix A. **Unrefereed** |
| O-84 | Review of B's guest against its native verifier | channel-by-channel equivalence; findings G-1 (root verifier and merge slot only in an example), G-2, G-3; refusal tests RT-B1 to RT-B9 | `docs/b-guest-equivalence-review.md` | this commit, 2026-11-19 | code reading only | **Original (the Ycash developers, 2026)**, review. Unreviewed |
| O-85 | System A round census (row-8 leaf 445 messages, row-7 leaf 411) | every challenge of A's verifier (`yugen-proof-a` 15b9993) in order with its field and per-message error; spBCS merge rule (consecutive draws one message); reproduces the built verifier's counts for the masked and the plain leaf; weakest message outside the opening 235.00 bits (bus fingerprint); estimate 599 above the census for every leaf, below it for row 9 at `2^27` (592) | `docs/round-census-a.md`; `soundness/src/yugen_soundness/census.py`, `soundness/census/a-round-census.json` | this commit, 2026-11-19 | `soundness/tests/test_census.py` (counts equal the measured `j_v`) | **Original (the Ycash developers, 2026)**, unreviewed. Per-round errors cited: [XZZPS19] Section 2.3.1 p. 8 (sumcheck), p. 10 (claim batching, from [CFS17]); [ACFY24] Lemma 4.25 p. 31 (OOD, list size 1) |
| O-86 | Lemma RS (the ring switch's error) | 64 slice claims off by a nonzero vector survive leanVM's Frobenius-map ring switch with probability at most `2/|E|` when `x` generates `GF(2^64)` | `docs/round-census-a.md` 2.6 | this commit, 2026-11-19 | proof (Vandermonde over the conjugates of `x`, two linear forms) | **Original as far as checked** (sources consulted: [DP24] Construction 3.1, Theorem 3.5, a different ring switching; the vendored leanMultisig documents state no error) |
| O-87 | Lemma K-A and Proposition RBR-A (draft) | A's leaf IOP is causal round-by-round knowledge sound ([SG26] Definition 2.20) with `eps_i^k = eps_i` (census and Theorem S), extractor = lane-by-lane unique decoding of oracle 0 in `A_{0,0}`; the rounds outside the opening as round-by-round soundness with the state read off `Dec(O_0)` | `docs/lemma-k-a.md` | this commit, 2026-11-19 | proof | **Original (the Ycash developers, 2026)**, DRAFT, unrefereed; completes the draft of `theorem-s-referee.md` section 4; [SG26] Definitions 2.20, 2.24, Lemma 2.21 read from rendered pages 14 to 16 |
| O-88 | Lemma LF (lifted oracles of unequal size) | in the Gao-Mateer basis `Lift(c) = c o (X^2 + X)^L` maps `RS_s` into `RS_b`, preserves relative distance, and every `RS_b` codeword within unique-decoding distance of a lifted word is the lift of the small word's codeword, so [BCIKS20] Theorem 4.1 on lifted words yields codewords of the committed codes | `lemma-k-b.md` 3a; `b-round-census.md` 5 | `bc18d26`, 2026-11-19 (written in `zkq-te3-r8-referee.md` section 3, `3cfd252`) | proof; condition m-5 (B's direct encoding test, not built) | Original (the Ycash developers, 2026), written by a referee, **refereed-in-review** (not yet independently read); relates to [BCIKS20] Theorem 4.1 (Published, applied as stated) |
| O-89 | Lemma DC and Corollary DC (dummy-constraint blinding, B's N3/N8) | two dummy multiplication constraints `(a_i, b_i, a_i b_i)` at distinct nonzero weights `alpha_1 != alpha_2` give a share at distance exactly `(|K|-1)/|K|^2` from uniform on `K^3`; with one such pair per segment, `(a_eval, b_eval, c_eval, s_pre)` is within `2(|K|-1)/|K|^2` of uniform on `K^4`; excluded events `6 n_x/|K|` | `docs/zk-composition.md` 5.2.3; `zk-lemma/test_dummy_constraints.py` | this commit, 2026-11-19 | proof; exact enumeration GF(16), GF(4) | **Original (the Ycash developers, 2026)**, DRAFT until refereed; relates to the Binius64 Blueprint 6.4 (stated without proof; not read here) and to the upstream comment in `spartan-frontend/src/constraint_system.rs` |
| O-90 | Theorem C-B (composed simulator of system B as built) | Sim-B: keys, dummy-blinded wrapper values, the Blueprint's masked-check simulator, Diamond's opening simulator with the pad step of [CFW26] Lemma 3.29 (adapted to the novel basis); `eps_hvzk^B <= 2(|K|-1)/|K|^2 + 6 n_x/|K|`; test specification SB-1 to SB-5 | `docs/zk-composition.md` 5.2 | this commit, 2026-11-19 | proof given the cited statements | **Original (the Ycash developers, 2026)** as a composition, DRAFT until refereed; components Published (Diamond ePrint 2025/1015 Theorem 4.3), Adapted ([CFW26] Lemma 3.29), upstream design document (Blueprint Theorem 6.3) |
| O-91 | The `K`-rank term of A's shared out-of-domain / `A(z)` pad (H-2) | `eps_rank(c) <= |K|^(8-c)/(|K|-1)` for `c` spare `GF(2^64)` cells under a uniform-weight model; `c >= 10` keeps it below `2^-165`; the build asserts 72 cells | `docs/zk-composition.md` 4.2a | this commit, 2026-11-19 | bound under a stated model (R); the `eq`-weight case not proven | **Original (the Ycash developers, 2026)**, from `hvzk-referee.md` H-2 |

Not original, although first derived here without the source (now cited as Published or
Adapted): the failure of Libra's mask for a plain sum in characteristic 2 ([CFW26] Section 2.5);
hiding by low-coefficient randomness on any domain ([CFW26] Lemma 3.29); the full-mask opening W-M
([Dia25] Construction 4.1); the base case ([CFW26] Construction 7.2); the query-bounded
salted-leaf bound ([CFW26] Lemma B.2); the two forms of the ring switch ([DP24] Construction 3.1
and Section 1.3; second pass, C-13).

Second-pass check of the other rows (2026-11-19): [DP24], [Hab-LDR] and [ACFY24] contain no
zero-knowledge construction (each was searched for "zero-knowledge" and "mask": only bibliography
entries; the sections listed in Part 1 were read), and [CMS19] treats zero knowledge only through
an honest-verifier zero-knowledge PCP or IOP (Lemma 7.3, Theorem 8.6 (3)). So O-1 to O-6, O-8 to
O-10, O-12 and O-14 keep their labels; O-7, O-11 and O-13 are updated above.

Third-pass check (2026-11-19, C-14 to C-21; papers [DKT26], [ethSTARK], [BGKTTZ23], [CWYZ26], [AF21],
[SG26], sections in 1.1d): each was searched for "mask", "zero-knowledge", "affine", "salt",
"parallel repetition" and "grinding"; the hits were read in the five smaller papers; in [SG26]
(over 300 hits for "mask") Sections 5.4.2, 5.5, 6 and 8.4 were read, not every hit. Relabelled:
O-7 (Lemma 2A's combiner Published in [CWYZ26]); O-11 (related published zero-knowledge ring
switching in [SG26]; label kept); **O-12 Published** ([BGKTTZ23] Appendix C). Related work found
for O-8 and O-10, not yet compared: [SG26] Section 5.4.2 masks every element the prover sends by a
pad held in the oracle input (credited there to Frigo and shelat, ePrint 2024/2010, Section 2.3)
and makes the final check linear with committed products of terminal pads; O-8's pad ledger and
O-10's linear terminals may be instances of that technique. Their labels stay "Original as far as
checked" until that comparison is written. O-13: its F5 is not in [ethSTARK] (classical
only) or [SG26] (no proof of work); kept. O-4's excess rule: [CWYZ26] Section 5 solves the same
degree excess differently (an extra challenge `theta`); kept as Original as far as checked, with
[CWYZ26] Section 5 added to its related work. O-1 to O-3, O-5, O-6, O-8 to O-10, O-14 to O-23:
none of the six papers contains them (by the search above); labels kept.

Fourth pass (2026-11-19): the comparison with [SG26] Sections 5.4.2 (Lemma 5.8) and 5.4.3 (Lemma 5.9)
is written. **O-8, blinder cells: relabelled Adapted.** [SG26] masks every element the prover sends,
including each terminal claim, by a uniform pad held in the oracle input (after [Fs24] Section 2.3,
not read) and hands the commitment one linear claim on the stored values and the pads, with
committed products of terminal pads for the non-linear final check (Lemma 5.8 (3): perfect HVZK with
the uniform simulator). A blinder cell is the same idea for one revealed evaluation, `chat = c(r) +
Z b` with a committed uniform cell `b` and a linear relation with a public target handed to the
opening; changes here: the cell is multiplied by a public `Z` from a dummy variable (`r_y (1 + r_y)`)
so the pad rides the existing sumcheck claim, one cell per revealed evaluation instead of one pad per
sent element, no product elements. **O-8, pad ledger and Theorem C (the composed simulator): kept
Original as far as checked**; [SG26] composes its reductions through its Theorem 5.3 (not read) and
[CFW26] Theorem 4.7 (not read), so a published composition theorem may cover Theorem C; that check
stays open. **O-10: kept Original as far as checked.** [SG26] has no dummy variable (it pads each
sent element); A8-T and Proposition D are not there. Proposition L (a revealed value handed linearly
into a masked head stays hidden) shares its principle with [SG26] 5.4.3's per-layer linear claims on
the pads of a layer and the previous one; the statement as proved here (a hand-off into a masked
sumcheck head with the staircase mask) is not in the sections read. [SG26] is added to the related
work of both rows.
| O-92 | Slim slice | request tags keyed by a public 8-byte digest `n_j` of `nf_1 || j`, so the scan layer is 14 B per output and matched slots are fetched by DPF under a fixed count; no circuit change | `design-private-tag-filtering.md` 5 | this commit, 2026-11-19 | none (design only) | Original as far as checked ([BLMG21], [LT21], `yugen-spec` 0.4.4 SPEC-176, `pir-selection.md`); trimmed scan records as such are long practice (Zcash compact blocks, from memory) |
| O-93 | Clue needs no circuit proof | FMD/OMR clues can ride in transfer bytes bound by the transfer hash; privacy needs no well-formedness proof ([LT21] Table 1, p. 47) | `design-private-tag-filtering.md` 4.1 | this commit, 2026-11-19 | argument only | Original as an observation for Yugen; rests on [LT21] p. 47 |

### 1.1h Read for the single-server PIR study (not published) (2026-11-24; titles and authors from the ePrint pages, figures via yugen-pir pir-selection.md §2.1)

- Henzinger, Hong, Corrigan-Gibbs, Meiklejohn, Vaikuntanathan. One Server for the Price of Two: Simple and Fast Single-Server PIR. ePrint 2022/949 (USENIX Security 2023).
- Li, Micciancio, Raykova, Schultz-Wu. Hintless Single-Server Private Information Retrieval. ePrint 2023/1733.
- Menon, Wu. YPIR: High-Throughput Single-Server PIR with Silent Preprocessing. ePrint 2024/270 (USENIX Security 2024), Tables 1, 5.
- Menon, Wu. Spiral: Fast, High-Rate Single-Server PIR via FHE Composition. ePrint 2022/368.
- Burton, Menon, Wu. Respire: High-Rate PIR for Databases with Small Records. ePrint 2024/1165, Table 1.
- Akhavan Mahdavi, Patel, Seo, Yeo. InsPIRe: Communication-Efficient PIR with Server-side Preprocessing. ePrint 2025/1352, Table 4.
- Davidson, Pestana, Celi. FrodoPIR: Simple, Scalable, Single-Server PIR. ePrint 2022/981 (PoPETs 2023), Table 6.
- Celi, Davidson. Call Me By My Name: Simple, Practical PIR for Keyword Queries. ePrint 2024/092 (costs not confirmed).
- de Castro, Lee. VeriSimplePIR: Verifiability in SimplePIR at No Online Cost for Honest Servers. ePrint 2024/341 (abstract only).
- valargroup/spendability-pir@9fb7844 (2026-11-21), README and docs/enhance/architecture.md.

Original (the Ycash developers, 2026): the mapping of these schemes onto the §17.8 fixed schedule and decision D-PIR-2 (option B), in the single-server PIR study (not published) §3, §5; unreviewed.
