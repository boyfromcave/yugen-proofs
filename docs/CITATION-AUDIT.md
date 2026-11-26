# Citation audit of 2026-11-19

Part of Yugen. The documents of this directory were written while the IACR ePrint
server refused PDF downloads; several rested on papers their authors could not read. The lead
architect supplied five papers. This file records what was checked against them, what changed,
and what remains unverified. Bibliographic entries, the reliance table and the list of original
contributions are in `../REFERENCES.md`.

Papers: Ben-Sasson, Chiesa, Spooner, "Interactive Oracle Proofs", ePrint 2016/116 (copy dated
2016-02-10); Xie, Zhang, Zhang, Papamanthou, Song, "Libra: Succinct Zero-Knowledge Proofs with
Optimal Prover Computation", ePrint 2019/317; Haböck, Al Kindi, "A note on adding zero-knowledge
to STARK", ePrint 2024/1037 (revision of 2025-02-20); Diamond, "Zero-Knowledge Polynomial
Commitment in Binary Fields", ePrint 2025/1015; Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs
for Constrained Interleaved Codes", ePrint 2026/391 (**revision of 2026-11-16**).

Second pass, the same day: four further papers, read by the sections listed in `REFERENCES.md`
1.1: Chiesa, Manohar, Spooner, "Succinct Arguments in the Quantum Random Oracle Model", ePrint
2019/834 (copy dated 2020-01-14); Diamond, Posen, "Polylogarithmic Proofs for Multilinears over
Binary Towers", ePrint 2024/504 (undated copy); Haböck, "Basefold in the List Decoding Regime",
ePrint 2024/1571 (undated copy, a revision of the author's earlier preprint); Arnon, Chiesa,
Fenzi, Yogev, "WHIR: Reed–Solomon Proximity Testing with Super-Fast Verification", ePrint
2024/1586 (copy dated 2024-11-21). Findings C-6 to C-13 (section 1b).

How they were read: `REFERENCES.md`, head of Part 1. 2025/1015 in full from the PDF pages; the
others from the PDFs' text layer (the page renderer is not installed), 2024/1037 pages 1 to 16 in
full and the remaining three by the sections listed in `REFERENCES.md` 1.1. Sections not read
are listed there; nothing is attributed to an unread section.

---

## 1. Findings

No statement in the five papers contradicts a construction that is built. Five findings change
what the documents may claim or what should be built next.

### C-1. The characteristic-2 failure of Libra's mask, and a characteristic-free mask, are published

ePrint 2026/391 (revision of 2026-11-16), Section 2.5 (page 20) and Section 1.2: Libra's mask
`s_1(X_1) + .. + s_k(X_k)` leaves the prover's messages unmasked when `char(F) = 2`.
Definition 6.1 and Lemma 6.2 give the mask polynomial
`U_sigma = shat_0 + sum_{e=1}^{d_s-2} shat_e (X_1^e + .. + X_k^e)`,
`shat_e = sum_{i=0}^{k} sigma_{i,e} X_{i+1}..X_k`, with `(k+1)(d_s-1)` coefficients, whose
sumcheck transcript is uniform on the consistent transcripts over every finite ring.

- Consequence: `zk-masked-sumcheck.md` section 2 is **not a new finding** and its section 10 said
  the opposite; both are corrected. The staircase mask (Theorem 1, Corollary A) stays Original as
  far as checked: it is a different family (one univariate polynomial per round times the
  trailing product; `1 + sum_j d_j` coefficients, a bijection; per-round degrees; general round
  functionals, which Theorem 1' and Corollary B need).
- Affected items: A4, B4 (and A23, A24, which use Theorem 1').
- Should ours be replaced by theirs: no. The staircase mask is built, tested exhaustively at toy
  size and uses fewer coefficients; the paper's mask requires masking degree `d_s >= 3` and is
  stated for one uniform degree. Task: the external reviewer compares Theorem 1 / Corollary A
  with Lemma 6.2; acceptance: a written statement that the two transcripts have the same
  distribution for the degree profiles in use, or the difference.

### C-2. Randomness on the lowest coefficients hides on any domain: the coset requirement is avoidable

ePrint 2026/391, Lemma 3.29: `fhat(X) = sum_{j<=t} r_j X^(j-1) + sum_i v_i X^(t+i-1)`, evaluated
on any set of distinct points, is a strong `t`-query zero-knowledge encoding with error 0. In the
novel basis `deg X_c = c`, so the same holds for a pad on novel-basis coefficients `0..t`
(Binius64 does this; `yugen-proof-b2` `tests/zk_pad_rank.rs` checks it at the leaf's size).
Lemma E's statement "hides only if the domain is a coset" is true for the high-offset placement
it studies and is not a property of binary fields.

- Affected items: A1, B1 (coset domains), A9 (lane layout), B9.
- Better construction for binary fields: low placement. It needs no coset, no alignment rule and
  no shifted NTT, and the paper's proof covers it.
- Why it is not adopted here without work: W-I's message keeps slots `[0, m)` so that the
  multilinear claim, the fold and A's affine combiner (multiplication by `X` moves slot `c` to
  `c + 1`, `zk-hiding-commitment.md` 3.2) read the message where the non-hiding code does; a low
  pad shifts the message by `t` slots and changes every linear form (the paper carries this in
  its linear forms `sl`, Lemma 9.7).
- Task: decide per system. For B (W-M) the low placement is a small change (the mask row is
  unaffected); acceptance: `zk-commit/test_code.py` and `test_wm.py` re-run with the pad on slots
  `[0, t)` on a **linear** domain, all sets of `t` rows hidden, controls still failing. For A,
  keep the coset unless the affine-combiner excess rule is re-derived for a low pad. Not run in
  this audit; no construction was changed.

### C-3. The in-oracle layout of W-I is the published layout of 2026/391 Section 11

The revision read puts the masks, the re-encoded folded randomness (auxiliary block) and the
base-case mask inside the rows of the main oracles (Sections 1.2, 9, 11, Construction 11.1) and
sends no mask oracle. `zk-hiding-commitment.md` presented W-I as an alternative to "the layout of
the paper"; that layout (W-S) is the pinned Plonky3 code's, an earlier version.

- Consequence: W-I is **Adapted**, not original as a design. A published security analysis of
  the related protocol exists: HVZK on fresh inputs by composition (Theorem 4.7, not read) and
  round-by-round knowledge soundness in the list-decoding regime (Theorems 6.3, 7.1, 9.8, 10.2).
- Affected items: A9 to A12, A26; the review sheets of `zk-hiding-commitment.md` and
  `zk-wi-soundness.md`.
- Should ours be replaced by theirs: not now. W-I is built for the pinned stacks (leanVM's
  affine combiner has no counterpart in the paper) and proven here under unique decoding, which
  is the design basis. Task for the external review: a line-by-line comparison of W-I with
  Construction 11.1 (differences listed in `REFERENCES.md` O-4); acceptance: each difference
  marked "equivalent", "ours weaker" or "ours needs its own proof", and Sections 4, 8, 9.4 to 9.7
  of the paper read.

### C-4. The Fiat-Shamir zero-knowledge theorem of 2016/116 does not give the error term at our salt size

Theorem 7.1 / Lemma 7.5: honest-verifier statistical zero knowledge of a public-coin IOP gives
statistical zero knowledge of the compiled proof with `z' = z + p(x) 2^(-lambda/4 + 2)`, for the
Merkle tree with privacy of Section 3.2 (salt of `2 lambda` bits, Lemma 3.4, unbounded
distinguisher), in the explicitly-programmable random oracle model. With 256-bit salts under a
256-bit hash the hypothesis on the salt length does not hold and the exponent `lambda/4` would
give about `2^-62` per leaf in any case.

- Consequence: the qualitative statement is verified and cited; the quantitative bound the
  documents use is not this theorem's. It is Lemma M (`q N / 2^s`, a sketch, the argument of
  2026/391 Lemma B.2) and the Chiesa-Yogev book's Theorem 26.2.1.
- Affected items: A2, B2, A13, B12; `zk-composition.md` row 19.
- Fix: no construction change. Task: Lemma M written as a full proof for the tree as built
  (arity, leaf width, salt position) with the book's Theorem 26.2.1 hypotheses checked against
  it; acceptance: the reviewer signs the bound `q N / 2^256` or gives the replacement. The
  quantum bound stays from memory (CMS19 unread).

### C-5. Diamond's combination has no excluded challenge; the pad count depends on symbols opened per query

ePrint 2025/1015, Construction 4.1: the opening runs on `alpha f + f'` with the mask unscaled, and
Theorem 4.3 gives identical real and simulated distributions for every `alpha`. The Blueprint's
`(1 - gamma) M + gamma w` excludes `gamma = 0`. The paper's pad is `kappa = gamma_rep * 2^theta`:
the number of first-oracle symbols the verifier opens, repetitions times coset size.

- Consequence for B on Binius64: (a) the excluded event `gamma = 0` (finding F-3 of
  `yugen-proof-b2/docs/zero-knowledge.md`) disappears if the fold is written `gamma M + w`;
  (b) the pad `q = n_test_queries` is enough only while each query opens one symbol of
  `Enc(M_r)` (true at the pin: `log_batch_size == 1`, one position per leaf); if the batch size
  or the first fold arity is raised the pad must be `q * 2^theta`.
- Affected: the mixed-field tasks T-2 and T-5 (leaf content and row), Proposition 6; B's own W-M
  (B9, B10) already uses `rho p + mk`.
- Fix: (a) optional, a protocol change upstream of our port: not made; (b) a guard: the pad
  length is computed as queries times symbols opened per query. Task for `yugen-proof-b2`;
  acceptance: an assertion in the layout and a test that raises the batch size.

### Smaller corrections

- **Parallel repetition** (`binius-extension-challenges.md` 7 (a), R-12): reworded to "two copies
  do not square the error". 2016/116 Theorem 1.5 and Remark 1.6 show that repetition does reach
  small state-restoration error, with `r = Omega((k log b + lambda)/log(1/s))` copies.
- **Lemma 7.2 of the Blueprint** (N1): the paper it is deferred to, 2025/1015, proves Lemma 4.4
  for a **different layout** (pad on coefficients `2^l ..`, domain disjoint from the message
  subspace). The code's layout (pad on coefficients `0..q`, linear domain) is the last step of
  that proof and is exactly 2026/391 Lemma 3.29. N1 is settled by citation.
- **Salt-free leaves** (2026/391 Appendix B): one extra seed coordinate gives distance
  `T / |F|`; enough at `|F| = 2^256`, not at 128 bits. It confirms F-1 of the B2 review (a
  128-bit mask symbol is not a salt at a 128-bit target) and offers, for the mixed variant whose
  leaves carry a 256-bit mask symbol, a route to drop the 32-byte salt of round oracle 0; that
  needs the analogue of Lemma B.1 for the Blueprint's fold and is not claimed.
- **Extension-field queries to base-field randomness** (2024/1037 Lemma 1, inequality (1)): the
  published form of the counting behind `binius-extension-challenges.md` 6.1.
- **Folding halves the randomizer space** (2024/1037 Section 2): consistent with Lemma F's
  `T >= Q 2^K`; the paper proves the masked route only.


---

## 1b. Second pass: findings C-6 to C-13

The four papers contradict no construction that is built. Two change numbers in the calculator
(C-6, C-9; no shipping row changes), three restrict what may be called a proven bound (C-7, C-8,
C-10), one answers the Johnson-regime question (C-11), two fix citations and labels (C-12, C-13).

### C-6. CMS19's constants are `C1 = 6` and `C2 = 24`; `C2 = 1` had been assumed

- Claimed: F3, `eps_Q(t) <= 6 t^2 eps_rbr + O(t^3 / 2^lambda)`, citing "Lemma 5.13" with the 6
  from Spooner's thesis; `C2 = 1` assumed throughout (`compose.FsParams.qrom_c2_log2 = 0`).
- The paper: Theorem 8.6 (Section 8.4) states `O(t^2 eps + t^3 / 2^lambda)` against attackers
  making at most `t - O(q log l)` queries. Its proof (Section 8.5.1) gives, for the database game,
  `<= t^2 * 6 (I(P | not Pcol, t) + I(Pcol, t)) <= 6 (t^2 eps + 4 t^3 / 2^lambda)` (Lemma 5.13,
  the lifting lemma, with Lemma 8.13: `I < eps + (2t + 1)/2^lambda`, and Lemma 6.11:
  `I(Pcol, t) < t / 2^lambda`), then Lemma 4.9: `sqrt(omega_O) <= sqrt(omega_D) + sqrt(a / 2^lambda)`
  with `a = O(q log l)` the oracle calls of the verifier's expansion (Proposition 8.11). So
  `C1 = 6` is confirmed from the paper itself and **`C2 = 24`**.
- Numbers (before / after): QROM hash cap at `lambda = 256`: 85.0 / 83.5 bits a layer; at 384:
  127.7 / 126.1; the tree's hash condition `lambda >= 193 + log2 N + log2 C2`: 207 / 212 (met by
  256); the step-0.6 record "100 QROM bits needs `lambda >= 301`": 301 / 306. The Lemma 4.9 term
  adds at most `2^-117` for `a < 2^20`, and `t' = t + a` at most `6 a^2 eps_rbr <= 2^(43 - e)`;
  neither is modelled, both are far below every target. **No shipping row and no check changes**:
  condition Q needs 66 (cat1, 256-bit digests: 83.5) or 98 (cat3, 384-bit: 126.1).
- Affected: condition Q and H (`soundness-method.md` 2.1, 8.2, 8.3, 8.5b, 8.6), `design-basis.md`
  section 1 header, `framework-selection.md` 7 and 10 (record text annotated).
- Done: `compose.FsParams.qrom_c2_log2 = log2(24)`; tests `test_quantum_hash_cap_is_a_third_of_the_digest`,
  `test_256_bit_digests_cap_qrom_soundness_at_83_5_bits`, `test_cms19_constant_defaults_to_six` updated
  to the read constants (117 pass).

### C-7. CMS19's theorem is for its own BCS construction, not for the transcripts as built

- Claimed: condition Q (and the "proven bounds only" basis of `design-basis.md` 2a item 3) is a
  QROM theorem for the built proofs.
- The paper: Section 8.2 defines the construction analysed: one oracle `h: {0,1}^(2 lambda) ->
  {0,1}^lambda`; verifier messages `m_j = h(sigma_(j-1), "j")` of `lambda` bits chained by
  `sigma_j = h(m_j, rt_j)`; binary Merkle trees under `h`; no salts in the soundness statement; no
  proof of work. Remark 8.2 and Section 8.6: for the original BCS16 hash chain the IOP must be
  "strongly" round-by-round sound (Appendix B shows the two notions can differ).
- Built: Keccak-256 (A) and SHA-256 (B) sponge transcripts that squeeze many challenges per
  verifier message (226 query positions, 8 ring-switch coordinates), Merkle trees of the arity and
  leaf layout of each stack, salted leaves. The SNARGs book's classical bound (condition C) is
  likewise stated for the book's construction; it was not re-checked in this pass.
- Affected: the word "theorem" for conditions C and Q in `soundness-method.md` 8.3, 8.5b, 8.6;
  the R-1 to R-3 review sheets that cite them.
- Work that closes it: a written reduction for each stack from its transcript to the analysed
  construction: (i) each round's challenges as a deterministic expansion of one `lambda`-bit `m_j`
  by further oracle calls, counted in `a`, with the IOP's round-by-round error unchanged; (ii) the
  Merkle arity and leaf encoding as single oracle calls, with the collision instability
  (Lemma 6.11) recounted; (iii) salts (Lemma 7.3's "straightforward adaptation"); (iv) the strong
  round-by-round property of Section 8.6 where the chain is BCS16's. Acceptance: the external
  cryptographer signs the reduction for both stacks, or the transcript code is changed to the
  analysed form with a test that recomputes its challenges. No numeric change is expected (the
  costs enter `a` and the collision term).

### C-8. CMS19 does not give zero knowledge against quantum distinguishers at the built salt length

- Claimed: `REFERENCES.md` 1.3 listed "zero knowledge against quantum distinguishers" as resting
  on CMS19; `zk-composition.md` 6 and `zk-hiding-commitment.md` 4 give it from memory.
- The paper: Theorem 8.6 (3) and the proof of Lemma 7.3: the classical zero-knowledge guarantee
  is statistical against verifiers unbounded in computation **and in queries**, and therefore
  holds against quantum ones. Our Lemma M (`q N / 2^s`, the form of 2026/391 Lemma B.2) is
  query-bounded, and BCS16's unbounded bound needs `2 lambda`-bit salts with exponent `lambda/4`
  (C-4). So no paper in hand covers the quantum case for 256-bit salts.
- Affected: A2, B2, A13, B12 (as in C-4); `zk-composition.md` 6; `zk-hiding-commitment.md` 4.
- Work that closes it: Lemma M against `q` quantum queries (a one-way-to-hiding or adaptive
  reprogramming argument; the source to be obtained, `REFERENCES.md` 1.3), with the parameter
  check at `q = 2^64`, `N <= 2^21`, `s = 256` (the order `q^2 N / 2^s`, from memory, gives
  `2^-107`). Acceptance: the written lemma with its cited source, and the check. No construction
  change unless the bound requires longer salts.

### C-9. WHIR's fold term is `d* l / |F|` with `d* = 3`; the calculator used 2

- Claimed: `soundness-method.md` 2.3 and `whir.py`: fold step `2 L / q + eps_line(n_i)`, "Theorem
  5.2 as transcribed in Plonky3".
- The paper (2024/1586, Theorem 5.2, Construction 5.1): `eps_fold <= d* l / |F| + err*(C, 2,
  delta)` with `d* = 1 + deg_Z(w) + max_i deg_Xi(w) = 3` for the evaluation constraint `Z eq(z, X)`;
  the other terms match the calculator exactly (OOD `2^m l^2 / (2 |F|)` for one sample, Lemma 4.25
  for `s`; shift `(1 - delta)^t + l (t + 1) / |F|`, the `+1` being the OOD sample; final
  `(1 - delta)^t`; `err*` in unique decoding `(l - 1) n / |F|`, Corollary 4.11, the P1 line value).
- Numbers: `whir.py` now uses 3. System A's leaf (`params.a_yugen`), weakest fold round with its
  grind, unique decoding: 233.999999989 bits before, 233.999999984 after; Johnson (DKT26):
  212.408010230 before, 212.408010229 after (differences below `10^-8` bits). No row changes.

### C-10. WHIR's theorem does not cover the Johnson regime or binary additive codes

- Claimed: `soundness-method.md` P2 "confirmed"; the `johnson-bciks20` regime applied to WHIR; A's
  node rows (plain WHIR) under "proven bounds only".
- The paper: Theorem 5.2 assumes a proximity generator with **mutual** correlated agreement.
  Lemma 4.10 and Corollary 4.11 prove it in unique decoding; up to the Johnson bound it is
  Conjecture 4.12 (1), with exactly BCIKS20's Johnson error. Its codes are smooth: evaluation
  domains are multiplicative cosets (Definition 4.2, Construction 5.1). Haböck (2024/1571,
  Section 6.4) says mutual correlated agreement "can in fact be proven by generalizing the list
  decoder analysis" of BCIKS20 but does not do so; it analyses a WHIR variant (coefficient-order
  folding, kernel `Q_n(z)`, the first round only; Lemmas 6 to 8).
- Consequences: (a) every WHIR row in a Johnson regime rests on a conjecture or on DKT26 (unread);
  the `johnson-dkt26` rows were already marked unconfirmed, the `johnson-bciks20` regime is now
  marked conjectural for WHIR (P2's row). (b) System A's codes are binary additive (leanVM), so
  the unique-decoding term list is applied to codes the theorem does not cover; the numbers do not
  change (BCIKS20 Theorem 4.1 holds for any evaluation set). For A's leaf the W-I proof (Theorem S)
  covers additive cosets; for plain-WHIR nodes no written proof covers them.
- Work that closes (b): Theorem S of `zk-wi-soundness.md` written for the unmasked opening (its
  masks removed, rounds `mask_i`, `bc` dropped), or leanVM's appendix-B theorem checked against
  the node verifier. Acceptance: a proof on binary additive cosets with the terms of `whir.py`,
  signed by the reviewer (E3 item 4).

### C-11. The 107-query Johnson candidate: Haböck proves the PCS core, not the protocol as built

- Claimed: `binius-extension-challenges.md` 7 (d), R-9; `design-basis.md` 2a: 107 queries at rate
  1/8 if a Johnson-regime theorem for binary BaseFold is confirmed.
- The paper (2024/1571): Theorem 1 (Reed-Solomon BaseFold, round-by-round soundness, proximity
  `theta = 1 - (1 + 1/(2m)) sqrt(rho)`, `m >= 3`, proofs in Section 5: Lemma 1 batching, Lemma 2
  folding with the weighted subcode correlated agreement of Theorem 3, Lemma 3 queries
  `(1 - theta)^s`, Section 5.4 skipped commitments); Section 6.2 (additive FFT of binary fields,
  "Theorem 1 with its proof ... holds verbatim"); Section 6.3, Protocol 3 and Theorem 6 (row-batched
  FRI-Binius: commitments over `E`, query field `F >= E`, row batching by powers of one challenge,
  Lemma 5: `l_m (d' - 1) / |F|`). Evaluated at the candidate (`m = 10`, rate 1/8, 2^30 points,
  `|F| = 2^256`): query 1.43 bits, **107 queries** for 152.52 bits (the candidate's count); fold
  `1/|F| + eps(C_i, 1, B_i, theta)`: 169.3 bits at the first fold, more later (BCIKS20's form gave
  168.2); both meet the target. The hypotheses on the field (characteristic 2, `E < F`), the rate
  and `m` are met.
- Not covered, as built: (1) Binius64's ring switch batches the 128 (or 256) rows with `eq(r'', .)`
  weights ([DP24] Construction 3.1), not Protocol 3's powers of one challenge; (2) the
  zero-knowledge mask round (`gamma` on `M + gamma w`) and the wrapper; (3) the lifted oracles of
  unequal size (commitment-index rounds; [HMH] not available). Section 6 of the paper is an
  adaptation sketch ("we omit certain details"), and its Theorems 2 to 4 rest on BCIKS20 Sections
  6 and 7, not read here.
- Work that closes it: three list-decoding round errors, each a union over the list of size
  `l_m = (m + 1/2)/sqrt(rho)` (about 30 here): ring switch `l_m kappa / |K|`; mask round the line
  error of Theorem 2 with `M = 1` plus `l_m / |K|` for the claim; lifted oracles per [HMH] once
  obtained. At 256 bits the ring-switch and claim terms keep more than 90 bits of slack; the mask
  round's line term is of the size of a fold round (about 169 bits, 17 above the target).
  Acceptance: the three lemmas written,
  the calculator's `johnson_bciks` replaced by Haböck's formulas with tests, and the reviewer's
  confirmation (R-9). Adopting the row remains the lead architect's decision (the basis says unique
  decoding).

### C-12. Binius64's query and fold terms are DP24's; DP24 proves whole-protocol soundness, not round-by-round

- Claimed: `soundness-method.md` 8.5c, 8.5d, `binius64.py`, R-6: "the theorem, Diamond-Posen:
  unconfirmed (not read)".
- The paper (2024/504): Construction 4.12 (binary BaseFold), Theorem 4.17 (security in the sense
  of Definition 2.9). Query: the proof of Proposition 4.24, accept with at most
  `(1/2 + 1/(2 * 2^R))^gamma = ((1 + rho)/2)^gamma`; folds: Proposition 4.21, mass of the bad set
  `theta |S^(i+theta)| / |L|` per committed oracle (Diamond-Gruen's tensor gap, Theorem 2.4), at most
  `2^(l+R) / |L|` in all (Proposition 4.23); sumcheck `2 l / |L|` (proof of Theorem 4.17); total in
  Section 5.2, equation (42). Our `(n_j + 2) / q` a round bounds these term by term. DP24 states
  no round-by-round soundness; the round-by-round form is Haböck's Theorem 1 / Theorem 6 (list
  decoding), which the paper says carries over "verbatim" to unique decoding "with the adapted
  soundness errors", without writing them. DP24's security experiment draws the evaluation point
  after the commitment (Definition 2.9).
- Consequence: query and fold terms confirmed; no number changes. Remaining: the unique-decoding
  instance of Haböck's Lemma 2 with its explicit error, and the commitment-index rounds.
- Work: write Lemma 2 for unique decoding (state function from DP24's Definitions 4.18, 4.20; error
  at most `(n_j + 2)/|K|`). Acceptance: reviewer sign-off (R-6).

### C-13. The two forms of the mixed ring switch are adaptations of published protocols

- Claimed: `REFERENCES.md` O-11, "Original as far as checked" for Theorems 1, 2; the Moore-matrix
  fact from memory (Lidl-Niederreiter "Corollary 2.38").
- The paper (2024/504): Construction 3.1 (ring switching) with Theorem 3.5: if the prover's
  `s_hat` is wrong, a nonzero `kappa`-variate multilinear vanishes at `r''` with probability at most
  `kappa / |L|`. Form T is this construction for `GF(2) < K` (`kappa = 8`) on the packed polynomial
  whose upper 128 basis coordinates are zero; the 128 zero columns are not sent and the claim point
  has its eighth packing coordinate 0. Section 1.3, equations (16) to (20) and Figure 4, gives an
  improved form of Soukhanov's Hashcaster that checks the claims on the Galois orbit of the point
  and batches with `eq(r'', .)`: form F is this check for the orbit of `L` with claims and
  challenges in `K`. DP24 calls it "perfectly correct and sound" with no numbered theorem, and
  cites the needed nonsingularity of `[sigma^u(beta_v)]` as Lidl-Niederreiter Lemma 3.51.
- Consequence: O-11 relabelled: Theorems 1 and 2 **Adapted** (changes: three fields, padded
  columns, `L`-valued oracle; the errors `8 / |K|` and `7 / |K|` are the published step with the
  larger field); Lemma 3 Adapted (Haböck Section 6.3's setting). Lemma 4, rule Z, Proposition 6,
  section 6.1 and the transposition model stay Original as far as checked. No construction change.
- Work: the reviewer checks the reduction of form T to Construction 3.1 (R-1) and of form F to the
  Section 1.3 protocol (R-2); the Lidl-Niederreiter lemma to be read (`REFERENCES.md` 1.3).

### 1c. C-11 and C-12 followed up: `binius-johnson-row.md` (2026-11-19)

Papers used beyond those of 1b: Dao, Kominers, Thaler, ePrint 2026/2056 ("DKT26", copy dated
November 2, 2026: Theorem 4.4, Definition 3.2, Corollary 6.4, Lemma 6.5, Corollary 6.6; Lemma 4.3's
proof and Appendix B not read); BCIKS20 (ECCC TR20-083, copy of May 30, 2020: Lemma 5.3, Claim 5.4,
Section 5.2 Steps 1 and 2); WHIR (2024/1586) Lemma 4.10, Corollary 4.11. Entries: `REFERENCES.md`
1.1b; original contributions O-15 to O-19.

- **C-11 (the three parts outside Haböck's Theorem 6).** Written and proved: the ring switch
  (`8 B_list / |K|`, a union over the list fixed before `r''`), the mask round (an interleaved line
  round; `(N_line + B_list)/|K|` with DKT26's line MCA, or Haböck's `eps(C, 1, 1, theta)` for one
  oracle), lifted oracles (the list taken at the lifted level; no refined proximity gap needed; an
  exact toy shows the naive "lifted close implies original close" is false in the list regime).
  The figure "line error plus `l_m / |K|` for the claim" of C-11 is the DKT26-route figure; on
  Haböck's route the claim needs no separate event. **Correction to C-11**: the mask round and the
  index round sit at the full common level (`2^22` points in the leaf), not at the first fold's
  half domain; the node's weakest term (first fold of a `2^31`-point opening) stays 169.34 bits on
  Haböck's route, 211.41 on DKT26's.
- **New gap G-1 (Haböck route only).** Rounds that combine two oracles with one challenge (the
  leaf) need Haböck's Theorem 4 for interleaved words with challenges in the subfield `K` of the
  identifying extension; this rests on BCIKS20's propositions holding for an arbitrary subset of
  challenges (Steps 3 to 8 and the weighted section not read). DKT26 Corollary 6.6 covers the case
  directly. Fallback F-J2 (power batching, Haböck Lemma 1) is a code change with no query cost.
- **C-12.** The unique-decoding round errors are written out (`binius-johnson-row.md` 6): mask
  `(n + 1)/|K|` and index `(n + 2)/|K|` reproduce the calculator; its fold term is one bit
  conservative (the line lives on the half domain). The 184-query row is unchanged.
- **1.3 updated in effect**: DKT26 and CWYZ26 are now read in part (the 1.3 rows for P4 and Lemma 2A
  were not re-checked here); 2023/1071 title page only.
- Rows (category 1, 20,000 proofs, no grinding): 184 (unique decoding), **107** at `m = 10` on
  either route, **102** at `m = 153` on DKT26's; category 3: 261 (unique decoding), the Johnson
  regime short by 0.36 bits at the largest node. Adopting a Johnson row stays the lead architect's
  decision (R-9).


### 1c-R2. `binius-johnson-row.md` revision 2, after the internal referee (2026-11-19)

Read for it (entries in `REFERENCES.md` 1.1b, "Read for revision 2"): DKT26 Lemma 3.3 with proof,
the proof of (38), Section 1.2, Corollary 9.4; CFW26 (2026/391) Theorem 6.3, Lemma 6.6 with proof;
SG26 (2026/2615) Section 5.5, Theorem 6.6, Definitions 2.20, H.3; WHIR (2024/1586, in the folder)
Lemma 4.10, Corollary 4.11, Definition 4.1, Theorem 7.5; CMS19 Definitions 8.3 to 8.5; Haböck
Sections 5.2 and 6.1 again. Corrections to 1c:

- **"107 at `m = 10` on either route" is withdrawn.** The row is proved (round-by-round soundness
  and knowledge) conditional on DKT26 Theorem 4.4, Corollary 6.6 and Lemma 3.3; Haböck's route alone
  is not available (G-1 for the leaf's mask round; G-3 and G-6 for every fold round, nodes
  included). **The 102 row is dropped** (0.001-bit margin; Haböck's count gives 142.25 bits there).
- **"On Haböck's route the claim needs no separate event"** stands, but revision 1's headline
  ("the mask round costs no claim term") was wrong for the DKT26 route, whose error contains the
  claim term `B_list / |K|`.
- **List size**: 19 (the Johnson bound, DKT26 (38) second term, proof read), not 29.70 (valid but
  looser). `binius-extension-challenges.md` 7 (d) already says 19 in its DKT26 paragraph; its
  earlier sentences "list size about 80 in every algebraic term" and "`l_m = (m + 1/2)/sqrt(rho)`,
  about 30" are the looser bounds (the calculator's `m / rho` and Haböck's `l_m`), not wrong as upper
  bounds; for its maintainers to align.
- **WHIR Corollary 4.11 is stated for smooth (multiplicative) domains** (its Definition 4.1); the
  unique-decoding line bound on Binius64's additive domain is WHIR Lemma 4.10 (any linear code) with
  BCIKS20 Theorem 4.1 (any domain). The 1c line "WHIR Lemma 4.10, Corollary 4.11" is corrected to
  that.
- **Provenance**: Lemma J2's error shape and proof pattern, and Lemma F's index rounds entirely, are
  published in CFW26 Lemma 6.6 (MCA event plus a union over the fixed list of a nonzero
  low-degree identity, at any `delta < delta(C)`, with knowledge); O-17 relabelled Adapted, O-19's
  index rounds Published shape. SG26 Section 5.5 (zero-knowledge ring switching for Ligero) concerns
  the ring switch, not the mask fold or the folds: related work for O-16, no relabelling.
- **The qualitative need**: the row needs only line MCA (subset or full-set form, equivalent at
  `A >= k`) at the Johnson threshold in characteristic 2 with count below `2^103.48` up to length
  `2^30`; DKT26 (39) is 59 bits below. DKT26 Section 1.2 names BCHKS (STOC 2026; ePrint 2025/2055,
  Theorem 4.6), Haböck 2025/2110 and Bordage-Chiesa-Guan-Manzur 2025/2051 as Johnson-radius MCA
  results; none is in the folder or read; reading BCHKS Theorem 4.6 is the task that could remove the
  dependence on a preprint (acceptance in `binius-johnson-row.md` 8.4).
- **Knowledge (G-4)**: Lemma K (O-24): round-by-round knowledge (CMS19 Definition 8.5) with the
  soundness errors, extractor = list decoding at the lifted level (DKT26 Corollary 9.4, statement) and
  at most 19 relation checks; compiled by SG26 Theorem 6.6 (2) (spBCS). New build requirement from
  H8' (a commitment binds a list): BR-1 to BR-5 in `binius-johnson-row.md` 5.3.
- Tests: the referee's T-J2-list, T-F, T-J1-list, T-J3 replace the vacuous ones (non-empty lists in
  doomed instances, root terms attained).

### 1d. C-4, C-7, C-8 and C-10 followed up (2026-11-19)

Documents: `qrom-compilation.md`, `zk-quantum.md`, `whir-additive-soundness.md`; numbers in
`qrom/test_numbers.py` (exits 0). Sources beyond 1b: the SNARGs book (Claims 3.4.1, 3.4.2, Chapter
17.3, 18.1, 18.6, Construction 25.1.1, Theorem 26.2.1), CMS19 Sections 3.3, 4, 6, 7, 8 in full,
CWYZ26 Sections 1.1 and 5, Block et al. 2023/1071 Theorem 3.15 (`REFERENCES.md` 1.1c; O-20 to O-23).

- **C-7.** CMS19 Theorem 8.6 cannot apply verbatim to any IOP of either system: its verifier
  messages are `lambda` bits, and splitting a long round into chain links loses round-by-round
  soundness (state-restoration argument). Minimal change: the "CMS form" (one link per prover
  message, challenges expanded from the link; SHAKE256 for A, counter-mode SHA-256 for B), with
  Theorem Q, an adaptation of CMS19's proof (changes listed). Constants: `C1 = 6`, `C2 = 24` for A,
  `24`, `240` for B. Tree of 20,000 proofs at `lambda = 256`: **67.2 QROM bits** (IOP term; hash term
  78.7) with `C1 = 6`, `C2 = 24`; 66.2 for B's constants. As built: A's duplex needs strong
  round-by-round soundness and CMS19 Section 8.6 as a proof (open); B's iterated expansion has no
  known reduction. Decisions: the transcript change in both systems; full or prefix chain value
  (the full one makes the book's classical theorem verbatim); B's inner-node compression function.
  **Correction (2026-11-19, after `qrom-zk-referee.md` 1.5, 1.8):** form C's constants `24`, `240`
  are **not established**: form C continues the chain from the link digest, not from the challenge
  (no write-back), so CMS19 Lemma 8.13's case 2 does not apply and the proof has a gap; the "66.2 for
  B" above is arithmetic on unproved constants. Form X's Theorem Q is a proof sketch under three
  extra hypotheses, not a proof. The "a_V folded" constants of `qrom-compilation.md` revision 1 were
  wrong (24, 192, not 12, 96). **Superseded** (lead decision D-a): both systems adopt the spBCS
  transcript of Sharp and Grubbs (ePrint 2026/2615, Protocol 6.5), covered as published by their
  Theorem 6.6 (2) (`C1 = 6`, hash constant `6 c'` with `c'` about 2,400 from the message counts):
  **67.54 QROM bits for A, 67.43 for B** (66.43 with B's counter-mode alternative and Lemma X),
  `qrom-compilation.md` revision 2, calculator revision 6. New finding Q-5 there (the classical
  bound of spBCS charges the verifier's `k_q` at `t = 1`).
- **C-4, C-8.** Lemma M written in full (`t N_u / 2^s`, `2^-104` at `2^128` queries and `2^24`
  unopened leaves). At `s = 256 = sigma` no statistical statement exists (the book's Claims 3.4.1,
  17.3.3: constant distance), and a witness-holding quantum distinguisher tests a candidate witness
  with about `2^128` queries (Grover over salts). Sourced route: unbounded statistical zero knowledge
  (Lemma H, Theorem ZQ) carried to quantum distinguishers by CMS19 Lemma 7.3's argument; error per
  proof `2^-40` / `2^-104` / `2^-136` at 384 / 512 / 576-bit salts. **Recommended: 512-bit salts**
  (+32 bytes per opened leaf: A about +23 KiB, B about +11.5 KiB; no extra Keccak-f per leaf in A).
  Hypotheses not yet established: the IOP-level HVZK items of both systems (`zk-quantum.md` 4).
  **Update (2026-11-19, `zk-quantum.md` revision 2):** Lemma H and the "no statistical statement at
  `s = sigma`" result are Published (Sharp–Grubbs Definition I.1 and Section 8.4), not Adapted or
  Original; the zero-knowledge statement is now Sharp–Grubbs Theorem 6.6 (3) (everlasting, QROM,
  adaptive, many proofs) with 64-byte leaf salts and a 64-byte proof salt, leaf proofs only: about
  `2^-106` a proof and `2^-85.4` over `2^20` proofs of both systems, plus the IOP's open HVZK terms;
  Theorem ZQ (one proof, non-adaptive witness) is superseded; "`zeta_IOP < 2^-240`" is withdrawn.
- **C-10 (b).** Theorem S0 proves plain WHIR with A's fold over binary additive codes in unique
  decoding (BCIKS20 Theorem 1.6 via Lemma 2A; WHIR Lemma 4.10 for mutual agreement). **New finding
  W-1**: the query terms need the true rate `(2^mu + kappa)/2^(mu + r)` (the affine combiner raises
  the folded lane; the source is the pinned verifier's code, and CWYZ26 Theorem 5.2's `d + r` is for
  the equal-degree combiner, cited only as consistent: corrected after referee 3.2), not the nominal
  rate the calculator and
  `cert.py` use. Row 7 keeps +0.63 bits; **row 9 is short by up to 4.36 bits** (rate 1/2, final
  `mu = 3`) and 1.15 at rate 1/4. Fix: per-level counts at the true rate (173 instead of 168 at the
  last level in the worst shape). Calculator not edited; formula in the document's section 6.

### 1e. Third pass: findings C-14 to C-21 (2026-11-19)

Papers added by the lead architect and read from their text layer (sections in `REFERENCES.md`
1.1d; independent of the follow-ups 1c and 1d, which used parts of DKT26, CWYZ26 and 2023/1071): Dao, Kominers, Thaler, ePrint 2026/2056 (DKT26, copy of 2026-11-02); Ben-Sasson et al.,
*ethSTARK Documentation* Version 1.2, ePrint 2021/582 (July 2023); Block, Garreta, Katz, Thaler,
Tiwari, Zając, ePrint 2023/1071 (copy of 2024-02-15); Chiesa, Weissenberg, Yogev, Zheng, ePrint
2026/2863 (CWYZ26, copy of 2026-11-13). The two unidentified files are **Attema and Fehr**,
*Parallel Repetition of (k1, ..., kmu)-Special-Sound Multi-Round Interactive Proofs*, ePrint
2021/1259 (Version 3, 2023-09-06; Klooß is thanked, not an author), and **Sharp and Grubbs**,
*Faster and Smaller Anonymous Credentials from Standardized Signatures* (the GordieHowe system),
ePrint 2026/2615 (no date on the copy). Nothing built is contradicted. One calculator change
(C-14, under 0.03 bits; no shipping, current, W-I or basis row changes).

### C-14. DKT26's Johnson MCA count is Theorem 4.4 with `rho_minus = (k - 1)/n`; the calculator used `rho`

- Claimed: P4, `8 n (m + 1/2)^3 / (3 rho_minus)`, "Theorem 5.12, App. B.1-B.2" via Plonky3,
  unconfirmed; `bounds.pg_johnson_dkt26` divided by `3 rho` with `rho = k/n`.
- The paper: Theorem 4.4 (any field, any `n` distinct points, every characteristic):
  `m = max(ceil(sqrt(rho_minus)/(2 eta0)), 3)`, `t = m + 1/2`, `A = ceil((sqrt(rho_minus) + eta0) n)`,
  exceptional count `B_cf < 8 n t^3 / (3 rho_minus)`, `rho_minus = D/n = (k-1)/n` (equation (39),
  closed form proved in Section B.3); probability `B_cf / |F|`; full agreement-set line MCA
  (Definition 3.2). Plonky3's numbering is that of an earlier version ([DKT26b] in the copy).
  Hypotheses as used: our agreement `sqrt(rho) (1 + 1/(2m))` is at least `sqrt(rho_minus) +
  sqrt(rho_minus)/(2m)`, so the paper's own `m` is at most ours (an upper bound); `k >= 2` and `m >= 3`
  are now asserted in code.
- Numbers (before / after): leanVM as shipped, Johnson, weakest round fold3.0 (`k = 2^6`):
  91.408010206 / 91.385290130 bits (the table's classical bits 85.7 / 85.6); System A leaf, Johnson,
  weakest fold (fold4.0): 212.408010229 / 212.385290153. All other output of `--ship`, `--current`,
  `--wi`, `--basis`, `--design` unchanged (diffed).
- Done: `bounds.py` (citation, `rho_minus`, guards), test
  `test_dkt26_johnson_mca_count_uses_rho_minus`; `soundness/` 118 passed.

### C-15. Consequences of DKT26 for WHIR (C-10), P5 and power batching

- WHIR Conjecture 4.12 (1) for lines (`Gen(2; alpha) = (1, alpha)`, the fold generator) is
  superseded: DKT26's full agreement-set MCA implies WHIR's Definition 4.9 (any `S` inside the full
  agreement set inherits the witnesses), on any evaluation set, so `err*` holds up to Johnson for
  binary additive codes, with DKT26's error, not the conjectured BCIKS20 form. Not settled by it:
  WHIR Theorem 5.2 is still stated for smooth multiplicative domains (C-10 (b) stands; a written
  round-by-round proof on binary additive domains is now needed in the list regime too, with the
  list sizes of (38)). That proof is the subject of `whir-additive-soundness.md` (another agent's
  file; not checked here).
- P5: DKT26 Theorem 4.4 (38) proves `|L| <= min(B_jet, n (A - D)/(A^2 - n D))` on any domain; the
  calculator's `m / rho` exceeds both (rate 1/16, `m = 10`: 160 against 41 and 31). Confirmed,
  conservative; no change.
- Curves (batching by powers of one challenge; FRI folds of arity above 2): DKT26 asserts the
  extension (end of Section 4.3, Remark 6.1: Lemma 4.3 holds for curves) but gives no closed count
  at order zero; the calculator's `l` times the line count is our extrapolation for MCA (BCIKS20
  Theorem 1.5 is for correlated agreement). Affected: B-alt's FRI rows in the Johnson regime and
  WHIR rows with `batch_count > 1` (none in System A's configurations). Work: Lemma 4.3 with
  Proposition B.1's interpolant for a curve of degree `l`, counted; acceptance: a closed count with
  a test, or the calculator switched to DKT26 Corollary 6.3 (independent coefficients, error
  `E / (q - 1)`), which needs the transcript to draw independent batching challenges.
- The regime label `johnson-dkt26 (UNCONFIRMED)` is kept (outputs unchanged); its meaning is now
  "protocol theorems not written", stated in `soundness-method.md` 2.2.

### C-16. DKT26 and the 107-query row (C-11)

- DKT26 covers characteristic 2 at the Johnson radius: line MCA (Theorem 4.4), interleaved
  (Corollary 6.6), `eq`-weighted multilinear folds of interleaved words (Corollary 6.7, `h` times the
  line error). At `2^30` points, message `2^27`, `m = 10`, `|F| = 2^256`: 211.4 bits per line; list
  at most 19. Query count unchanged (107). The three lemmas of C-11 are written in
  `binius-johnson-row.md` (section 1c). This pass read what that document did not: Section B.2
  (Proposition B.1, whose dimension count is BCHKS's Lemma 3.1, not read) and Section B.3 (the closed
  constant, checked step by step from the text layer), and the end of B.1; this narrows its gap G-2
  to the BCHKS count and the body of Lemma 4.3's proof.

### C-17. ethSTARK: F4 is Theorems 6 and 8; nothing shipping depends on grinding

- Claimed: F4 from "ethSTARK §5", unconfirmed. The paper: Section 6.3, Theorem 6 (proof read): the
  grinded IOP, round `i` with `z_i` extra verifier bits that must be zero, has round-by-round
  soundness `eps_i 2^-z_i`; Section 7.1, Theorem 8: compiled error `T max_i eps_i 2^-z_i + 3 (T^2 +
  1)/2^kappa` (BCS16 Theorem 7.1); classical ROM only. F5 (quantum) remains our argument.
- The ALI round `C L / q` is the form of its Theorem 5 item 1 with Remark 6 (powers of one
  challenge: `(2s - 1) l / |K|`).
- Grinding: `shipping.py` and `current.py` set every grind to 0 (their headers say "no grinding");
  grinding enters only the design-basis columns with 20-bit query grinding, the 100-QROM-bit record
  tables and the leanVM cross-check. Nothing a shipping row claims depends on F4 or F5.

### C-18. Block et al. cover multiplicative FRI only

- Claimed: `soundness-method.md` 5 cited 2023/1071 for FRI knowledge soundness ("abstract read").
  The paper: Theorems 4.1, 4.2 (round-by-round soundness of FRI and batched FRI:
  `max{(m + 1/2)^7 |L0|^2 / (3 rho^(3/2) |F|), (1 - delta)^l}`), Theorem 5.11 (knowledge error the
  same), Corollaries 4.3, 4.4 (Fiat-Shamir: `Q eps_rbr + 3 (Q^2 + 1)/2^kappa`; quantum
  `Theta(Q eps_fs)`, restating CMS19). Hypotheses: `L0` a smooth multiplicative subgroup, binary
  folding, BCIKS20's Johnson error. It covers neither A (binary additive WHIR) nor B on Binius64; for
  B-alt (KoalaBear FRI) only binary folding in the Johnson form. No number rests on it; cited
  exactly. Its Appendix C is the published source of the staggered attack (C-20).

### C-19. CWYZ26 against Lemma 2A and leanVM's `eps_aff`

- Lemma 2A (`zk-wi-soundness.md`): the combiner `G + (alpha + beta x) F` and the degree asymmetry
  of its conclusion are CWYZ26's (Section 1.1). CWYZ26 proves MCA with one coordinate of agreement
  loss up to Johnson, any field and domain (Theorem 1.1: `4/(eta q) + 2^14 n^2/(rho^3 eta^10 q^2)`;
  Theorem 4.10, (4.13)); without agreement loss its Proposition 6.2 gives the lower bound
  `(n - A + 1)(q - 1)/q^2`, so Lemma 2A's `n/q` (unique decoding, no loss) has the right order and is
  not improved by the paper in that form. Lemma 2A's proof (BCIKS20 Theorem 1.6) stays ours;
  relabelled: combiner Published, proof Original (O-7, `REFERENCES.md`). Option (not adopted, no fold
  round binds): loss one at A's leaf gives about `2^-252` against `2^-228`, with Theorem S restated
  for agreement loss. CWYZ26 Section 5 (equal-degree variant with `theta`, Theorems 5.1, 5.2) is a
  published alternative to the excess rule of O-4.
- leanVM's `eps_aff` (appendix B at the pin, read): equation (4.13) with `(m, D, B)` free, as
  CWYZ26's Remark 5.3 itself chooses them; `h` lanes by the packing step of Theorem 5.2's proof
  (5.7); claim binding after Theorem 5.1 without the premix challenge (leanVM's own statement, not
  checked); the agreement loss absorbed by lowering the threshold by one per fold, as Theorem 5.2's
  `A + r`. Work: implement `eps_aff` in `soundness/` with a test reproducing Remark 5.3's 125.42
  bits; R-5 then reduces to the review of leanVM's appendix B theorem.

### C-20. ePrint 2021/1259 is Attema-Fehr's interactive repetition theorem, not the Fiat-Shamir attack

- Claimed: `binius-extension-challenges.md` 7 (a), R-12: interactive repetition squares the error
  (from memory); the staggered attack is Attema-Fehr-Klooß's (from memory).
- The paper: Theorem 4, knowledge error `kappa^t` for the `t`-fold parallel repetition of a
  `(k_1, .., k_mu)`-out-of-`(N_1, .., N_mu)` special-sound protocol (Theorem 5: thresholds). No
  Fiat-Shamir analysis; Section 1.1 only remarks that Fiat-Shamir's loss "is oftentimes exponential
  in the number of rounds". So the interactive half of 7 (a) is now cited (for knowledge error and
  special-sound protocols; that the sumcheck and folds are special-sound is not in this paper).
- The attack itself **is published**: Block et al., ePrint 2023/1071, Appendix C (pages 86, 87, read):
  a `t = 2` parallel repetition under Fiat-Shamir is broken by regenerating round-1 challenges until
  copy 1 cheats, then round-2 challenges until copy 2 does, "introduced and described in [AFK22]" =
  Attema, Fehr, Klooß, *Fiat-Shamir Transformation of Multi-Round Interactive Proofs*, TCC 2022, Part I, LNCS 13747, pp. 113–142 (as cited by ePrint 2023/1071; not supplied, not read). O-12 relabelled **Published** (our run is a toy reproduction).

### C-21. GordieHowe (ePrint 2026/2615): a published QROM theorem near the built transcripts; salts must be twice the digest; zero-knowledge ring switching is published

- C-8 (quantum zero knowledge of salted leaves): Theorem 6.6 (3), everlasting zero knowledge in the
  QROM for spBCS (Protocol 6.5), leaf term per position `1/2 sqrt(2^(8b)/2^(8 b_l)) + sqrt(ln N_leaf
  / (2 * 2^(8 b_l)))` (Definition I.1); Section 8.4: with salts as long as the digest an unopened leaf
  is at expected distance about `1/e` from uniform, so statistical zero knowledge does not follow.
  The built 32-byte salts under 256-bit digests are outside the theorem (term `1/2`): the
  quantum zero-knowledge claim needs longer salts. Section 1d's recommendation of 512-bit salts
  (`zk-quantum.md`, Theorem ZQ via CMS19 Lemma 7.3) is GordieHowe's `b_l = 2b` and is independently
  supported by Theorem 6.6 (3), a second published route (it also needs a per-proof salt in every
  challenge input and the spBCS transcript); acceptance: Theorem 6.6 (3)'s error evaluated for each
  stack at `npos`, `t = 2^64`, or Theorem ZQ's as in 1d.
- C-7 (CMS19 analyses its own construction): Theorem 6.6 (2) is a QROM knowledge-soundness theorem
  for spBCS, which, unlike CMS19's construction, expands several challenges per verifier message from
  one stream, salts leaves and carries non-oracle message parts: `2 sqrt(k_q / 2^(8(b+e))) + 6 (t +
  k_q)^2 (eps_k + c' (t + k_q)/2^(8b))`, `c' = max(2, c) + n_J + 1`, `c` the digests in one
  challenge input. So `C1 = 6` again and the collision constant is `6 c'` (24 when `c' = 4`); at
  `c' = 2^7` the 256-bit hash cap would be 81.8 bits (83.5 now), still above condition Q's 66, and
  126.1 becomes 124.5 at 384 bits (above 98). Not adopted in the calculator (the built transcripts
  are not spBCS); it is a second published target construction beside section 1d's "CMS form", and
  one whose challenge expansion (one stream per verifier message, rejection sampling) is the shape
  section 1d proposes for both systems. **Update (2026-11-19):** adopted (lead decision D-a);
  calculator revision 6 evaluates it with `c'` from the message counts (2,397 for A, 2,401 for B:
  hash term 75.6 bits, never binding).
- O-11: Section 5.5 (Lemmas F.2, F.4, Theorem F.6 not read) publishes zero-knowledge ring switching
  for Ligero (masked twisted sums, subfield masks uniform in `K`, squaring-chain masks in
  characteristic 2, perfect HVZK, `1/|K|` a round). The statement "[Dia25] Section 5 leaves
  zero-knowledge ring switching open" is out of date; Lemma 4, rule Z and Proposition 6 stay
  Original as far as checked with this paper added to the sources (a different construction, the
  same principle as rule Z).


### 1f. The BLAKE3 sources: obligation H-1 of `decision-b-merkle-hash.md` (2026-11-19)

Sources: [B3] (O'Connor, Aumasson, Neves, Wilcox-O'Hearn, *BLAKE3: one function, fast
everywhere*, version 20211102173700) and [B3-ID] (Aumasson (Ed.), Neves, O'Connor, Wilcox,
*The BLAKE3 Hashing Framework*, `draft-aumasson-blake3-00`, 20 July 2024), both supplied by the
lead architect and read in full from their text layers (`REFERENCES.md` 1.1e: how read, the
claims, the cryptanalysis table, the references to obtain).

### C-22. BLAKE3 claims 128 bits for every goal, including preimages; nothing quantum

[B3] 4.1: "128-bit security against (second-)preimage, collision, or differentiability attacks";
[B3-ID] 7: "at least 128 bits" for outputs of at least 32 bytes. Neither text mentions quantum
attackers. Revision 1 of the decision record said the "digest and quantum accounting are
unchanged" without this: the numbers are unchanged (the hash term depends on the digest length
and query counts only), but the QROM hash term now rests on a heuristic above any designer claim
(finding H-1.3), and the classical level is at the claim, not above it (H-1.2). Corrected in the
record's sections 6 and 9.

### C-23. "The compression function of BLAKE2s with the round count reduced from 10 to 7"

Verified for the round count ([B3] 1, 2.2, 4.4; [B3-ID] 3.3); incomplete as a description: the
message schedule (one repeated permutation, [B3] 7.4), the `b`, `d` inputs ([B3] 4.2) and the
finalisation (16-word output, feed-forward on the second half, [B3] 2.2, 7.3) changed, and the
full-output compression function is not indifferentiable ([B3] 4.2). "The ChaCha/BLAKE line" is
not in either source and was removed. Record corrected (H-1.9).

### C-24. "A framed hash with domain separation between leaves and nodes" is not what is built

`yugen-proof-b2` at `af0f56d`, `vendor/binius64/crates/hash/src/blake3.rs`: leaves are
`blake3::Hasher` over the leaf bytes and nodes `blake3::hash(left || right)`, both in the plain
mode; for inputs of at most 64 bytes both carry `CHUNK_START | CHUNK_END | ROOT` ([B3] 2.4). The
mode's flags separate chunks from parents only inside one evaluation ([B3] 7.7). Finding H-1.6,
proposal H-1.7; the record's section 4 now states the build.

### C-25. The category 3 path

`design-basis.md` 1 says category 1 to 3 "changes only queries, fold schedule and digest
length". For system B it also changes the Merkle hash: BLAKE3's claim does not rise with output
length and its chaining values are 256 bits ([B3] 2.4, 4.1), and SHA-256's output is 256 bits.
Finding H-1.5 (SHA-384 or SHA3-384 for B's trees at category 3). `design-basis.md` is not in this
pass's write set: the lead agent amends section 1.

### C-26. Unsourced or memory-based statements left marked

The cryptanalysis of [B3] Table 4 is cited through [B3] only; its exponents were read from a text
layer with flattened superscripts. SHA-256's 256-bit preimage strength (NIST SP 800-107 Revision
1), SHA-384's padding (FIPS 180-4 5.1.2) and the generic quantum figures (BHT, Grover) are from
memory and marked so in the record and in `REFERENCES.md` 1.3. The Internet-Draft's four
discrepancies D-1 to D-4 (`REFERENCES.md` 1.1e) were found here; D-2 and D-3 were checked with a
minimal implementation written from [B3] 2.2 to 2.5 (temporary directory, not committed), which
reproduces [B3-ID] Appendix B.1 and B.2 and the `blake3` crate's vector for "foo".

Tests: no calculator number changes (the hash term depends on digest length and query counts
only), so `soundness/` was not changed and `uv run pytest` was not re-run in this pass.

### 1f, continued: four cryptanalysis papers cited by [B3] (2026-11-19, decision record revision 3)

Sources, supplied by the lead architect and identified from their own first pages
(`REFERENCES.md` 1.1e-bis):
- [TMC], Aumasson, *Too Much Crypto*, version 20260706145800 (ePrint 2019/1492), read in full;
- [B2], Aumasson, Neves, Wilcox-O'Hearn, Winnerlein, *BLAKE2: simpler, smaller, fast as MD5*
  (ePrint 2013/322), read in full;
- [EFK15], Espitau, Fouque, Karpman, full version of their CRYPTO 2015 paper (ePrint 2015/515),
  Sections 1 to 3 and 5;
- [GKNWW14], Guo, Karpman, Nikolić, Wang, Wu, *Analysis of BLAKE2*, full version (ePrint
  2013/467; CT-RSA 2014), read in full.

They are [B3]'s references [3], [5], [17] and [18]. Their text layers were extracted to a
temporary directory outside every repository.

### C-27. [B3] Table 4 against the papers: one model wrong, three disagreements, one figure not found

The BLAKE-256 "c.f. preimage 2.5, `2^241`" is a hash-function preimage ([GKNWW14] Table 1, [B2]
4.1). For "BLAKE2s k.p. rotational 4, `2^489`", [GKNWW14] 3 and Table 1 give 7 rounds at `2^511`.
The "BLAKE2s c.f. boomerang 5, about `2^86`" is a conditional estimate with no complexity in
[GKNWW14] 2. The BLAKE-256 permutation differential is `2^456` in [B2] 4.1 and `2^486` in
[GKNWW14] Table 1. [B2] 4.1 and [GKNWW14] describe the Biryukov-Nikolić-Roy boomerang
differently, and [B2] records a doubt about its correctness. Confirmed: both 6.75-round
pseudo-preimages ([EFK15] Tables 1, 6), the 6.5-round impossible differentials ([GKNWW14] 5),
and the 7.5-round `2^184` boomerang, at second hand ([TMC] 3.2). Not in the papers read: the
BLAKE-256 k.p. boomerangs at `2^44` and `2^198`. The C-26 caveat about flattened exponents is
resolved where [EFK15] (base-2 logarithms) and [GKNWW14] overlap with [B3]. Record: H-1.12.

### C-28. Results below `2^128` that the record had left out

Revision 2 (H-1.8, section 10) said only one result in the cited cryptanalysis is below `2^128`,
the BLAKE-256 keyed-permutation boomerang. [GKNWW14] adds three more:
- chosen-IV collisions on all 10 rounds of BLAKE2s's compression function, `2^64` (Section 3,
  Table 1);
- a full-round weak-key distinguisher on BLAKE2's keyed permutation (Sections 3, 7);
- Li and Xu's 2.5-round collision on the BLAKE-256 hash, `2^112` (reported in Table 1).

None applies to BLAKE3 as used (H-1.13, H-1.14). The record is corrected in 6.1, H-1.8 and 10.

### C-29. The 6.75-round pseudo-preimage is not a margin figure for BLAKE3

Revision 2 compared 7 rounds with "6.75 rounds of BLAKE2s's compression function". [EFK15] 5.1
defines a pseudo-preimage with "complete freedom for the initial 16-word state". BLAKE3's
truncated output has no feed-forward of the chaining value ([B3] 2.2, 7.3). In that model, then,
BLAKE3's compression is inverted in one step at any round count (H-1.13 (a), Original as far as
checked). The comparison is withdrawn from sections 6.1 and 10.

### C-30. MA-2' rested on an ideal cipher that BLAKE2's permutation is not

[GKNWW14] 3 and 7 item 1 show that the unconstrained BLAKE2 permutation is "fully attacked": a
one-query distinguisher for a class of weak keys, at every round count. The property depends
only on `G` and on equal message words, so it carries over to BLAKE3's `E` (inference, H-1.14).
MA-2' is restated for inputs constrained by the IV words, and section 7 item 1 is reworded. As
first written, item 1 was already met by this distinguisher.

### C-31. Smaller corrections

- "The ChaCha/BLAKE line", removed in revision 2 as unsourced, is sourced ([B2] 4.1, [TMC] 4.5)
  and restored (record section 5).
- [TMC]'s criterion for its round counts is "never wounded" (practical risk). That is weaker
  than the record's reversal rule (no attack below `2^128`), and it is now stated (H-1.15).
- [TMC] and [B2] are by BLAKE3's designers. Only [EFK15] and [GKNWW14] are independent (H-1.10).
- The version of [TMC] read (2026) is later than the one [B3] cites (RWC 2020). [B3] 4.4's
  summary of it ("7 and 8 rounds") agrees with the version read.
- [EFK15] is internally inconsistent: Table 6's "e" column, and BLAKE2b at 510.9 in Table 6
  against 510.3 in Table 1. The text and Table 1 are used.
- SHA-256, SHA-512 and Keccak: the four papers give no SHA-2 round counts. The Keccak figures are
  [TMC]'s report, marked so in the margin table. The category 3 alternatives need their own
  sources (task H-1f).

What stays unverified: the papers listed as "to obtain" in `REFERENCES.md` 1.1e-bis (Hao;
Biryukov, Nikolić, Roy; Leurent; Dunkelman, Khovratovich; Li, Xu; Khovratovich et al.; Luykx,
Mennink, Neves; and others). Also unverified: any cryptanalysis after 2015, and BLAKE3-specific
analysis (none in any source read). Figures were read from text layers, not typeset pages. No
test or calculator number depends on this pass.

---

### 1g. The security-profile record, revision 2, and the builders' transcript deviations (2026-11-19)

Scope: `decision-security-profile.md` revision 2 (after `security-profile-referee.md`),
`qrom-compilation.md` 2.8, and two corrections other passes left open. Read: [FIPS204] Appendix D.1
(PDF page 64); [SG26] Definition 2.18, Section 6.2 (Protocol 6.5), Section 6.3 (Theorem 6.6),
Appendix I.1 (`REFERENCES.md` 1.1h).

### C-32. The category-4 label for 48-byte SHAKE256 digests now cites its source

The record's revision 1 labelled 48-byte binding "category 4" with [FIPS204] Table 1 and App. D.1
together; Table 1 gives the collision strength of `c~`, not a rule for other digests. Checked: App.
D.1 states that a collision attack on SHAKE256 with a 384-bit output leaves category-5 parameters
at category 4 (quoted in the record). That sentence is the cited source now; the generic sponge
bound behind it (FIPS 202, capacity 512) stays from memory and is marked "not verified".

### C-33. [SG26]'s Merkle rules exclude repeated positions; system B as built repeats them

Definition 2.18 makes `qry(theta)` a list "without repetitions", and I.1 "Prover and verifier" has
the verifier require "exactly one salted leaf per position". System B carries one opening a query,
repeats included (`yugen-proof-b2` parameters 10.2 item 3). `qrom-compilation.md` 3 (H7) had
"met after deduplication" without saying that the build does not de-duplicate; 2.8 B-3 now says
the hypothesis fails as built and gives Lemma D (Original, O-66). Lemma D (ii) uses a QROM
collision bound that is **from memory** (Zhandry); `REFERENCES.md` 1.1h marks it.

### C-34. The other builder deviations checked against the text, not against `qrom-compilation.md`

Each deviation of 2.8 was checked against the paper's own wording (I.1 "The oracle's domain",
"Hash functions", "Challenge inputs", "Samplers"; Section 6.3's last paragraph on longer streams;
Theorem 6.6's polynomial-time decoders), not against this repository's restatement. Two points
rest on sources not in the folder and are marked: the sponge identity of A-3 (a) (FIPS 202 / the
Keccak reference, from memory; the builder cited the duplex paper from memory too) and MA-2''s
ideal-cipher support ([B3] 4.2, 4.3, read; caveat C-30).

### C-35. Two labels and one figure aligned with what the papers say

- `zk-composition.md`'s provenance paragraph still called the blinder cells and Theorem B
  Original; `REFERENCES.md` O-8 relabelled them Adapted from [SG26] 5.4.2, Lemma 5.8 in the fourth
  pass. The paragraph now says Adapted, with the changes.
- `binius-extension-challenges.md` 7 (d) gave the list size as "about 80" and "about 30";
  `binius-johnson-row.md` revision 2 derives 19 (Johnson bound, DKT26 (38) second term). Both
  sentences now say at most 19, with the Guruswami-Sudan 29.70 named as the looser figure.

### C-36. Claims in the record's revision 2 that stay from memory

FIPS 202 (capacities, the 192-bit claim of SHAKE256-384), FIPS 203 (ML-KEM-1024 sizes and level),
RFC 9861 (TurboSHAKE), the DPF PRG's reduction to AES-256 as a PRF, the Micciancio-Walter measure,
Grubbs-Maram-Paterson (ML-KEM ciphertext anonymity), phone memory limits. Each is marked where used
in the record; none is attributed to a paper in the folder.

### 1h. The calculator's revision 8 (condition C-3 of `johnson-row-referee-2.md`, 2026-11-19)

Scope: `soundness/src/yugen_soundness/dkt26.py`, `soundness/CHANGELOG.md` revision 8, `binius-johnson-row.md` 2.1.
Read: [DKT26] Sections 3.1, 4.2, 4.3, B.1 (end), B.2, B.3, 6.2 (`REFERENCES.md` 1.1b, "Read for the calculator's
revision 8").

### C-37. Every formula of `dkt26.py` checked against the paper's text, not against `rowcalc.py`

(33), (34), `Psi_D`, (36), (37), (38), (39), Lemma 3.3 (6), Lemma 6.5 and Corollary 6.6 are cited in the code at the
equation used and were read in the PDF's text layer for this revision. The text layer drops the ceiling brackets of
(36) and (37); they were taken from Section B.2 (`B_jet = ceil(C_jet) - 1`, `B_Z = ceil(C_Z) - 1`; "the definition
of m gives m eta_0 >= sqrt(rho_-)/2", which holds for a ceiling and not for a floor) and agree with both referees'
`B_jet = 29`, `B_Z = 294`. A typeset-page check of (36), (37) stays owed (as C-14's for (36), (39)).

### C-38. The candidate label says "preprint" wherever a Johnson row is printed

`category.py` (revision 7's `--category` tables) said "candidate (DKT26)"; it now says "rests on DKT26, a preprint",
and every revision 8 row carries the full label. Revision 5's output (`output/revision5-tables.txt`) is a record and
still reads "candidate, under referee review" with "DKT26 route" in the row's name; nothing prints a Johnson row as
certified.

### C-39. One figure of the second referee's 5.1 differs from the formula it cites

The D-term row of `johnson-row-referee-2.md` 5.1 gives 250.39 bits (49) at rate 1/16 as at 1/8; the builder's bound
it cites is `n_f (2^r - 1)`, which at rate 1/16 is 105 for `n_f = 7` (249.29) and 60 / 75 (250.09 / 249.77) at the
build's recorded terminal dimensions. Not binding; recorded in `soundness/CHANGELOG.md` revision 8, finding 3.

### 1i. Sumcheck and GKR against the originals (2026-11-19, `citation-check-lfkn-gkr.md`)

### C-40. The sumcheck and GKR terms match LFKN and GKR; two attributions are corrected

[LFKN92] (J. ACM 39(4), 1992) and [GKR15] (J. ACM 62(4), 2015) were added to the folder and read.
Every per-round sumcheck term `d_j / |E|` is the step of [GKR15] Lemma 2.5's proof (p. 27:21,
inequality (3) pp. 27:22-23; any finite field), originating in [LFKN92] Lemma 4 (p. 862). The
census's per-layer GKR accounting has the structure of [GKR15] Section 3.3 (pp. 27:31-32). No
numerical discrepancy. Textual: LFKN does not state `d l / |F|` (GKR15 Lemma 2.5 does), and
`round-census-a.md` 2.4's "asymptotic only" is superseded. Variants not in either original: `eq`-form
reduced messages, combiner by powers, multilinear `y` reduction, grand-product trees (U-3, U-5, U-6,
U-8 there). Twelve text changes listed for the editing agent; BCIKS20 places listed for re-check.

C-40 applied 2026-11-19: the twelve changes of `citation-check-lfkn-gkr.md` section 4 are in
`round-census-a.md` (5), `lemma-k-a.md` (3), `zk-wi-soundness.md` (2), `what-is-proven.md` (1),
`REFERENCES.md` (1), each marked "amended 2026-11-19".

### 1j. BCIKS20 against the folder copy (2026-11-19)

`2020-654.pdf` (see REFERENCES.md) is ePrint 2020/654, **revision of July 3, 2021** (first
page), 61 pages, printed page = PDF page - 1 (`REFERENCES.md` 1.1k). The documents had cited the
ECCC TR20-083 copy of May 30, 2020 (a scratch download, not in the folder; not re-read here). The
192 citing lines of `citation-check-lfkn-gkr.md` 5 were grouped by statement; each statement was
read in the folder copy (text layer; printed pages 2 and 19 rendered for the formulas).

| Statement as cited | Folder copy | Used as | Verdict |
|---|---|---|---|
| Theorem 1.2, (1.1): `eps_U = n/q` for `delta in (0, (1-rho)/2]` | Theorem 1.2, (1.1), p. 2 | `bounds.py` UD, Theorem S, every UD row | **matches** |
| Theorem 1.2, Johnson case `(k+1)^2 / ((2 min(eta, sqrt(rho)/20))^7 q)` | (1.2), p. 2 (rendered) | `bounds.py` JB, `binius64.johnson_bciks` candidate | **matches** (for correlated agreement; the WHIR mutual-agreement caveat of `soundness-method.md` P2 stands) |
| Theorem 1.4 (lines) | Theorem 1.4, p. 4 | listed as read | matches |
| Remark 1.5 (extension-field challenges; quoted in `binius-extension-challenges.md` 4.1) | **Remark 1.2**, p. 4; the quotation is word for word | Theorem 4.1 / affine theorem with `D` in `K` or `L`, challenges in the extension | number wrong for this copy; statement **matches** |
| Theorem 1.6 (curves, `l eps`) | **Theorem 1.5**, p. 5 (hypothesis `> l eps`) | `bounds.py` CURVE, `fri.py` batch, P3 | number wrong; statement **matches** |
| Theorem 1.7 (affine spaces, UD addendum) on p. 4 | **Theorem 1.6**, p. 5 (PDF 6), with "Furthermore, in the unique decoding regime ... unique maximal `D'`"; proof Section 6.3, p. 30 | Lemma 2A, Theorem S0, Lemma F0 (fraction `> n/q` of `u0 + span(...)`) | number and page wrong; statement **matches** |
| Theorem 4.1 on p. 12 | Theorem 4.1, **p. 13** (PDF 14): `delta <= (1-rho)/2`, `|S| > n` gives `S = F_q` and `v0, v1` with at most `delta |D|` disagreeing positions; `D` any subset of size `n`, `k <= n` (Section 4 preamble) | Theorem S Lemma 2, Theorem 5 of `binius-extension-challenges.md`, mask rounds, `dkt26.py` line MCA, SG26 Lemma 2.14 | page differs; statement **matches**, including "any `D`" |
| Section 4.1 (decoder) | Section 4.1, p. 14, Berlekamp–Welch | `zk-wi-soundness.md` extractor remark | matches |
| Theorems 5.1, 5.2; Lemma 5.3; Claim 5.4 (list size `(m + 1/2)/sqrt(rho)`) | Theorems 5.1, 5.2, p. 17; Lemma 5.3, p. 18; Claim 5.4, (5.6) `D_Y < (m + 1/2)/sqrt(rho)`, p. 19 (rendered) | `johnson.py`, `rowcalc.py` revision-1 list size | matches (the list is bounded by `D_Y`) |
| Proposition 5.5; Section 5.2 Steps 3 to 8; Sections 6, 6.2, 7 | Proposition 5.5, p. 20; Steps 1 to 8 (5.2.1 to 5.2.8) exist; 6.2 proves Theorem 6.2; Section 7 weighted versions | names in [Hab-LDR] and the G-1 / G-3 / G-6 gap text | numbers match; the gap questions themselves were **not** re-derived here |
| "BCIKS conjecture" (correlated agreement up to capacity) | Conjecture 8.4, p. 42 | P7 disproofs | matches |

### C-41. BCIKS20 numbering: three numbers and three pages differ in the folder copy; no statement as used differs

**Published** (the paper); the mapping is read from the two copies' content, not from the ECCC copy
itself (not in the folder: the identification rests on the documents' own descriptions and the
word-for-word quotation of the remark). Fixed in place with dated amendments, 2026-11-19: ECCC
Theorem 1.7 -> **1.6**, Theorem 1.6 -> **1.5**, Remark 1.5 -> **1.2** in `zk-wi-soundness.md`,
`whir-additive-soundness.md`, `soundness-method.md`, `binius-extension-challenges.md`,
`what-is-proven.md`, `design-basis.md`, `binius-johnson-row.md`, this file (lines 451,
508, 557), `REFERENCES.md`, and the code comments and source strings of `soundness/` (`bounds.py`,
`fri.py`, `wi.py`, `revision5.py`, `binius64.py`; 471 tests pass) and `ext-challenge/test_code.py`.
Referee records (`theorem-s-referee.md`, `qrom-zk-referee.md`) keep their text and carry a dated
note with the folder numbers and pages: Theorem 1.2 p. 2 (was cited p. 3), Theorem 1.6 p. 5 (cited
as 1.7, p. 4), Theorem 4.1 p. 13 (cited p. 12), Section 6.3 PDF 31 (cited PDF 27). Not changed:
the generated tables under `soundness/output/` (regenerated output, carries the old strings until
the next run), `CHANGELOG.md` entries, and the other referee records (`johnson-row-referee*.md`,
`security-profile-referee.md`), which cite only Theorem 4.1, 1.2 or sections whose numbers did not
change. **Statement as used versus the paper: no discrepancy found** for any of the eleven
statements in the table.

### C-42. The folder copy treats inseparable factors (G-6) in Appendix C

`binius-johnson-row.md` G-6 and `johnson-row-referee.md` (b) ask whether BCIKS20's list-decoding
argument treats inseparable factors in characteristic 2. The folder copy says, Section 5.2.3, p. 21:
"we will assume for simplicity that Q does not have inseparable irreducible factors ... The general
case, including the possibility of inseparable factors, is very similar, but has more technicalities,
which are discussed in detail in Appendix C" (Appendix C, "The Inseparable Factor Case in the List
Decoding Regime", p. 57). So the source for G-6 on Haböck's route exists in the folder; whether
Appendix C covers the arbitrary-subset use of G-1 / G-3 was **not checked** (Appendix C was not
read beyond its title). For the lead: G-6 can be closed or narrowed by reading Appendix C; the
built rows do not depend on it (they use Theorem 4.1 or the DKT26 route).

## 2. Numbering in the pinned code against the revision read

| Cited in the pinned Plonky3 code | In the revision of 2026-11-16 | Status |
|---|---|---|
| "Construction 6.3" (masked sumcheck) | Construction 6.4, Theorem 6.3 | different mask; the code's sum-of-univariates mask is not in the revision |
| "Lemma 6.4" (divides by two) | no counterpart; Lemma 6.2 inverts nothing | the odd-characteristic condition is the code's |
| "Proposition 3.19" (`f + X^l r`) | Lemma 3.29 (randomness on the low coefficients) | different placement |
| "Lemma 3.26" (fold of randomness) | Claim 2.8, Lemma 3.34 | same statement for the eq-fold |
| "Construction 7.2" (base case) | Construction 7.2 | same |
| "Construction 9.7" (code switch, OOD pad by powers) | Construction 9.9 with private zero-evaders (Lemma 9.4) | different out-of-domain mechanism |

The earlier version was not available. The documents now attribute those six items to the code.

Second pass: the file re-saved by the lead architect at 08:13 on 2026-11-19 is the same revision
(first page dated November 16, 2026; 102 pages; PDF creation date 2026-11-16; Lemma 3.29,
Lemma 6.2, Construction 6.4, Lemma 3.34 and Construction 9.9 at the places read before). The
correspondence above therefore stays as it was; the earlier revision is still needed to establish
it (`REFERENCES.md` 1.3).

Related numbering note: Diamond, ePrint 2025/1015, cites ePrint 2024/504's "Proposition 4.23,
Lemma 4.13, Definition 4.17". In the copy of 2024/504 read, Proposition 4.23 is the bound on the bad
folding events, and 4.13 and 4.17 are Theorems (completeness and security of Construction 4.12):
2025/1015 cites an earlier revision. The documents cite the copy read.

---

## 3. What was checked, per document

| Document | Audit | Changed |
|---|---|---|
| `zk-masked-sumcheck.md` | every statement naming Libra, 2026/391, BCS: sections summary, 1.3, 2, 7.1, 10, 11 | provenance paragraph; Libra's construction and Theorem 3 cited exactly; field assumption stated; literature answer withdrawn and rewritten (C-1); GKR mask cited (Section 4.2, equation (7)) |
| `zk-hiding-commitment.md` | summary, 3.2, 3.4, 4, 6.1, 6.4, 7, 7a, 10, 11 | 3.4 rewritten (four points verified, C-2, C-3); Lemma M's provenance; base case verified against Construction 7.2; W-M marked adapted from 2025/1015; Lemma F related work; sources table |
| `zk-composition.md` | section 6, review rows 10 and 19, status line | the theorem, its four conditions and what it does not give (C-4); provenance |
| `zk-wi-soundness.md` | sources table, section 9 (W-S), summary | sources; W-S no longer called the published layout; provenance |
| `binius-extension-challenges.md` | read list, 4.2 mask row, 6.2, 7 (a), review rows R-7, R-10, R-12 | 2025/1015 cited (Theorems 4.2, 4.3, Lemma 4.4); N1 settled; C-5; repetition reworded; provenance |
| `soundness-method.md` | section 5 (zero knowledge), section 7 rows, 8.5c `mask` row | 2016/116, 2024/1037, 2025/1015, 2026/391 rows; verified statements |
| `framework-selection.md` | candidates table (2024/1037), R-1, section 12 | exact citations |
| `zk-system-a-gaps.md`, `zk-implementation-checklist.md`, `design-basis.md` | every mention of the five papers (Libra's mask; BCS) | one provenance paragraph each |
| Tests and calculator | `zk-lemma/{sumcheck,test_rank,test_leak,test_exact,test_gkr,test_gkr4}.py`, `zk-commit/{additive,test_code,test_basecase,whir_i,test_wm,test_fold,test_blind}.py`, `ext-challenge/{test_zk_mask,test_parallel_repetition}.py`; `soundness/src/yugen_soundness/{bounds,compose,binius64,wi}.py` | citation and provenance in the module docstring (tests) or in comments (calculator; no string that reaches output was changed) |
| `round-census-a.md`, `lemma-k-a.md`, `zk-wi-soundness.md`, `what-is-proven.md` (sumcheck and GKR error terms) | every use of a sumcheck or GKR error against [LFKN92] Lemma 4 and [GKR15] Lemma 2.5, Theorem 3.1, Section 3.3 (C-40) | none here: changes listed in `citation-check-lfkn-gkr.md` 4 for the editing agent |

**Fully audited** (every statement that uses one of the five papers checked): `zk-masked-sumcheck.md`,
`zk-hiding-commitment.md`, `zk-composition.md`, `binius-extension-challenges.md`,
`framework-selection.md`, `soundness-method.md` (for the five papers only).

**Audited by search, not read end to end**: `zk-wi-soundness.md`, `zk-system-a-gaps.md`,
`zk-implementation-checklist.md`, `design-basis.md`. Their mentions of the five papers were found
by searching for the paper numbers, "Libra", "BCS" and "Blueprint" and each was checked; a
statement that relies on one of the papers without naming it would have been missed.

**Second pass** (four papers): `soundness-method.md` (F3, P2, P5, 2.3, 5, 6, 7, 8.2, 8.3, 8.5b,
8.5c, 8.5d, 8.6), `binius-extension-challenges.md` (read list, provenance, 3.2, 4.2, 7 (d), review
rows R-1, R-2, R-6, R-9, section 11), `design-basis.md` (section 1 header, candidate paragraph,
S-16), `framework-selection.md` (section 7 item 2, section 10 item 2), `zk-composition.md` 6,
`zk-hiding-commitment.md` (4, sources), `zk-wi-soundness.md` (sources), `zk-masked-sumcheck.md`
(literature table); `soundness/src/yugen_soundness/{compose,bounds,whir,binius64}.py`,
`soundness/tests/test_soundness.py`, `ext-challenge/test_ring_switch.py`. Found by searching every
file for DP24, FRI-Binius, BaseFold, Haböck, WHIR, CMS19, QROM, ring switch, Johnson,
list-decoding, mutual correlated agreement and the four ePrint numbers.

**1g pass** (2026-11-19): `decision-security-profile.md` revision 2 (every citation of [CFP],
[FIPS204], [FIPS205], [GLS26], [SG26] and every "from memory" mark), `qrom-compilation.md` 2.8 and
its rows in sections 1, 3, 9, 10, `zk-composition.md` provenance paragraph,
`binius-extension-challenges.md` 7 (d), `profile-study/profile_study.py` S6 to S9 (sources named
beside each constant).

**Provenance labels**: given per document in a provenance paragraph and per result in
`REFERENCES.md` Part 3. They are **not** yet attached to each individual lemma, checklist row
and parameter choice inside the ten documents; that pass remains.

---

## 4. What remains unverified

1. Papers not read (full list with the claims that rest on each: `REFERENCES.md` 1.3): [HMH];
   BCIKS20 Sections 6 and 7; a quantum source for Lemma M at salts equal to the digest (GordieHowe,
   2026/2615, covers salts of twice the digest, C-21); Attema-Fehr-Klooß (Fiat-Shamir of multi-round
   proofs; 2021/1259 is a different paper, C-20); BCHKS (full version, Lemma 3.1, behind DKT26's
   Proposition B.1); VEIL 2026/683; Aurora and
   Virgo (cited through 2025/1015); Hashcaster and row-batched FRI-Binius (cited through 2024/504
   and 2024/1571); Lidl-Niederreiter Lemma 3.51; Diamond-Gruen; Katz's bound. (2019/834,
   2024/504, 2024/1571, 2024/1586 were read in the second pass; 2026/2056, 2021/582, 2023/1071,
   2026/2863, 2021/1259 and 2026/2615 in the third, by the sections in `REFERENCES.md` 1.1d.)
2. Sections of the five papers not read: 2026/391 Sections 2.1 to 2.4, 2.6 to 2.8, 4, 5, 6.4,
   7.2, 8, 9.4 to 9.7, 10 (theorem), 12, 13, Appendix A; 2016/116 Sections 4 to 6, 7.1 to 7.3, 8;
   2019/317 Sections 3, 4.3 onward, 5; 2024/1037 Section 5 and Appendix A.
3. Formulas of 2016/116, 2019/317, 2024/1037 and 2026/391 were read from the PDFs' text layer.
   Every formula quoted in the documents was legible there; a reader with the typeset pages
   should confirm Lemma 6.2's proof and Lemma 3.4's proof of 2016/116, which were read in part.
4. The earlier version of 2026/391 that the pinned Plonky3 implements (the re-saved file is the
   same revision as before).
6. Second pass, sections not read: 2019/834 Sections 2, 3, 5.3 (proof of Lemma 5.10), 6.1, 6.2,
   Appendices A, B; 2024/504 Sections 2.1 to 2.5, 3.2, 4.1, 4.2, 4.4, 5.1; 2024/1571 Sections 1,
   2 and the proofs of Section 4.1; 2024/1586 Sections 1 to 3, 4.3, 5.2, 6, 7 (except Theorem
   7.5), 8 and the proof of Theorem 5.2 past its state function. Formulas were read from the text
   layer; Theorem 3 of 2024/1571 (the `max` term) and equation (42) of 2024/504 should be checked
   on the typeset page.
7. Tests after the second pass: `soundness/` 117 passed (after each calculator change);
   `ext-challenge/test_ring_switch.py` 12 passed. Nothing else was re-run (only docstrings changed
   elsewhere).
5. Tests after the changes (only docstrings and comments changed in code): `soundness/` 117
   passed; `ext-challenge/test_zk_mask.py` and `test_parallel_repetition.py` passed;
   `zk-commit/test_code.py`, `test_wm.py`, `test_basecase.py` and `zk-lemma/test_rank.py`,
   `test_leak.py` exited 0; every test file compiles. Not re-run: the other `zk-lemma/`,
   `zk-commit/` and `zk-sound/` scripts and `ext-challenge/test_code.py`, `test_ring_switch.py`
   (their files were either not touched or changed in the docstring only).

8. Third pass (C-14 to C-21): sections not read: DKT26 Sections 2, 3.2 to 3.5, 5, 8, 9, the body of
   Lemma 4.3's proof (B.1 read from its last part), Appendices A, C to H; ethSTARK Sections 1 to 5,
   6.1, 6.2 (except Theorem 5's statement and the bound on `eps_1`); 2023/1071 Sections 2, 3 (except
   Theorem 3.15), 4.2 onward, 5 (except Theorem 5.11's statement), 6, 7; CWYZ26 Sections 2, 3, 4.2 to
   4.4, 7 and the appendix; 2021/1259 Sections 2, 3, 5 and the proofs; 2026/2615 everything except
   Sections 5.5, 6.1 to 6.3, 8.4, Table 3 and Definition I.1 (Appendix F not read). Formulas from the
   text layer; DKT26 (36), (39) and CWYZ26 (1.1), (4.13) should be checked on the typeset page.
   Tests: `soundness/` 118 passed after the C-14 change; `ext-challenge/test_parallel_repetition.py`
   3 passed after its docstring change; nothing else touched.
