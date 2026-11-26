# Referee report: Theorem S, A's rounds outside the openings, obligation K-A

Part of Yugen. Independent referee, 2026-11-19. Subject: Theorem S of `zk-wi-soundness.md`
(sections 3 to 5) as it applies to system A's masked leaf (rows 6 and 8: W-I over binary additive codes,
the leanVM fork in `yugen-proof-a-zk`), the round census behind rows S-3 / S-7 of `what-is-proven.md`, and
obligation K-A (`qrom-compilation.md` H3, T-5; `lemma-tree-extraction.md` section 2 (K)). Prompted by
`qc-and-status-referee.md` (no referee report existed for Theorem S).

## Verdicts

| Item | Verdict |
|---|---|
| Theorem S (family A, unique decoding) | **holds, pass with corrections** (M-1, m-1 to m-3). Every step checked; no step is wrong; the state function must name its code. |
| Round census for A (rows S-3; the A side of S-7's question) | **incomplete.** The opening's rounds and the rounds the zero-knowledge construction adds are listed with an error and a proof each. The unmasked leanVM rounds are one estimated count (`OTHER_ROUNDS = 512`) with no per-round error (M-3). |
| K-A | **open in the record; closable.** Section 5.2's remark does not meet [SG26] Definition 2.20 (M-2). Lemma K-A below (Original, draft) reduces K-A to S-3 written as round-by-round soundness with states read off the decoded oracle 0, and to Theorem S with M-1 applied. What remains owed is the per-round list of M-3, nothing of a knowledge kind. |
| A payment proof as built | **no concrete soundness gap found** (section 5). |

## 1. Sources checked against rendered pages

Rendered with pypdfium2 (`yugen-proofs/.tools-venv`) and read:

- [BCIKS20] E. Ben-Sasson, D. Carmon, Y. Ishai, S. Kopparty, S. Saraf, *Proximity Gaps for Reed-Solomon
  Codes*, ECCC TR20-083 (ePrint 2020/654): Theorem 1.2 with equation (1.1), `eps_U = n/q` for
  `delta in (0, (1 - rho)/2]` (printed page 3); Theorem 1.7, including the unique-decoding addendum
  (printed page 4, PDF page 5); Theorem 4.1 (printed page 12, PDF page 13); proof of Theorem 1.7
  (Section 6.3, PDF page 27). The code is `RS[F_q, D, k]` for any `D` contained in `F_q` and degree at most `k`.
  `zk-wi-soundness.md` section 1 restates all three correctly, including "any `D`". **Note:** this
  paper is not in the reference-paper collection (REFERENCES.md); the copy read was a scratch download. The lead
  should place it there.
  *Citation amendment (2026-11-19, `CITATION-AUDIT.md` C-41; this record's text above is unchanged):*
  the folder now holds ePrint 2020/654, revision of July 3, 2021. There the statements read above
  are Theorem 1.2 with (1.1), printed page 2 (PDF 3); **Theorem 1.6** (the ECCC copy's 1.7), with
  the unique-decoding addendum, printed page 5 (PDF 6); Theorem 4.1, printed page 13 (PDF 14);
  proof of Theorem 1.6 in Section 6.3, printed page 30 (PDF 31). The statements are the same as
  restated here.
- [WHIR] G. Arnon, A. Chiesa, G. Fenzi, E. Yogev, ePrint 2024/1586: Definition 4.1 (PDF page 21)
  and the overview (page 5) restrict to "smooth" codes, i.e. multiplicative cosets of 2-power order;
  folding is Definition 4.14 (`x -> x^2`); Theorem 5.2 (page 34). Consequently **no WHIR statement applies to
  A's binary additive cosets**, and Theorem S correctly uses none (its section 1 table says so).
  The question "is every WHIR statement valid for binary additive codes" is therefore moot: an
  adaptation was needed, and Theorem S *is* that adaptation, proven from BCIKS20 directly.
- [SG26] C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized
  Signatures*, ePrint 2026/2615: Definition 2.20 (page 14), Lemma 2.21 and Definitions 2.23 and 2.24
  (page 15), Definition 2.24 continued (page 16), Theorem 6.6 (page 58).

Code read (A as built): `yugen-proof-a-zk/vendor/leanMultisig/crates/verifier/src/wi.rs`
(`verify_wi`, `layout`), `whir.rs` (`fold_row`, `novel_eval`), `lib.rs` (`verify_stacked_opening`,
`read_ood`), `params.rs` (each build refuses the other's rows: rows 5 and up are 256-bit only).
Calculator: `soundness/src/yugen_soundness/wi.py`, `shipping.py`, `revision5.py`; run read-only:
row 8 at rate 1/4 gives 227/161/164/180 queries with a weakest round of 153.43 bits against a need of 152.52. At rate 1/2
it gives 375/169/175/220, 153.19 against 152.52. Both have 87 listed rounds plus 512 in `k`.

## 2. Theorem S, step by step (family A)

**What it claims.** In the unique-decoding regime, with the radius taken from the true rate
`lf_i / N_i` (`lf_i = lrow_i + kappa_i` for A), W-I is round-by-round sound. The errors are `1/q` for `rho_i`,
`max(n/q, 3/q)` per fold round, `((1 + rho_i)/2)^Q + Q/q` per query step, `(N + 1)/q` for `c`, and
`((1 + rho)/2)^Q` for the last positions.

**Matches what A runs.** Checked line by line in `verify_wi` against section 2.1 of the document:
- `G` is read before `rho`.
- Each fold round reads four scalars `(u0, w, c0, c1)`, then `alpha` and `beta`, with the update
  `u0 + beta c0 + alpha (u0 + claim + alpha w + beta (c0 + c1))`. This is the polynomial with
  coefficients `[1] = u0`, `[a] = u0 + claim`, `[a^2] = w`, `[b] = c0`, `[ab] = c0 + c1`, so
  `[1] + [a] = claim`, as Lemma 3A uses.
- `fold_row` computes `G + (alpha + beta x) F` with `x` the actual domain point `K(2^log_domain + q)`,
  the same `x` in every round. So Lemma 2A's affine space `G + alpha F + beta (xF)` is literally what is
  checked.
- The next root is read before the positions and `lambda`.
- `mu` is read before `c`, and `P*` before the last positions; `Gcol` is read from the same leaf.
- Challenges are in the 256-bit field `E` and domain points in `K = GF(2^64)`. `RS[E, D, k]` with `D`
  contained in `K` is covered by BCIKS20, which allows any `D`.

**Lemma 1 (coset, any dimension).** Correct. The novel basis has `deg X_c = c`, so the code is
`RS[F, beta + S, d]` for every `d`.

**Lemma 2A (affine combiner).** Correct. The checks:
- Theorem 1.7's hypothesis "fraction > `eps_U = n/q`" over the affine space `u0 + span(u1, u2)` is
  "more than `nq` of the `q^2` pairs". This holds even when `F` and `xF` are dependent, because a
  linear parametrisation pushes the uniform distribution forward to the uniform one.
- From `x f_1 = f_2` on more than `d + 1` points, `f_1` is in `C[d]`.
- Disagreement rows lie in at most `q` agreement sets (a nonzero affine form in `(alpha, beta)`).
- The counting gives `|Dis| <= e` once `|Gam| > q (e + 1)`.

**Lemma 3A (masked batch).** Correct.
- `lambda(q) = <F, W_F> + <G, W_G>` holds for vectors of any length, because `X` only appears with `b`.
- So `V_0 = rho <P, W> + M`, with `M` fixed before `rho`.
- The difference of a degree-2 message and the true degree-3 polynomial is nonzero of total degree at most 3,
  so the error per round is at most `3q / q^2`.

**Lemmas 4 and 5.** Correct. The bounds `(e + lf - 1)/N` and `(N - e - 1)/N` are both below
`(1 + rho)/2`. In Lemma 5 the order is right: `g` and `mu` come before `c`, and `P*` before the positions.

**Mask degree and combination.** The mask has `1 + 4 kappa` coefficients, monomials `1, a, a^2, b, ab`
per round, and is combined as `rho f + g`. The aux content is treated as an arbitrary committed table,
so the proof does not depend on the mask family (as the document says).

**Order of the batching challenges.**
- The stacked `lambda` (`verify_stacked_opening`) is drawn after the stack root and every claimed value.
- Each `rho_i` comes after `G_i`, and after oracle `i`, which holds the level's mask.
- `c` comes after the last oracle, which holds `Gcol` and the lanes `v` derives from, and after `mu`.

The tests `opening_messages_are_bound_and_ordered` exercise these orders.

**MA-1 and MA-2'.** Theorem S is an information-theoretic IOP statement and uses neither. MA-1 (the
transcript hashes as one random oracle) is a modelling assumption of the Ycash developers, of the kind
[SG26] makes for its own hashes. It is neither proved nor conjectured as a theorem. It enters only at
compilation. MA-2' concerns system B's BLAKE3 and does not bear on A.

### Findings on Theorem S

- **M-1 (MAJOR, record): the state function does not name its code.** Location: section 5.1, and
  section 5.2 (decoder). Lemma 2A concludes `F` in `C[d]` and `G` in `C[d + 1]`. Its converse
  therefore certifies an input lane only in a code one degree larger on the `G` branch. The section 3 text
  after Lemma 2A says so, but the state ("within its radius") is stated for `C[lrow]`. Under that reading
  the "far stays far" step fails: a prover may commit lanes of degree up to `lrow + g_b`, where `g_b`
  counts lane `b`'s `G`-branches, and be accepted.
  - *Fix:* define the admissible code `A_{i,0}`: lane `b` in `C[lrow_i + g_b]`, and after round `j` the
    images, with every lane of degree below `lrow_i + j`. Let "doomed" be relative to `A_{i,j}` at the
    uniform radius `e_i = floor((N_i - lf_i)/2)`. This is below each lane code's unique radius, so decoding
    stays lane-wise unique.
  - Lemma 2A applied per pair with that pair's degree gives the transition exactly.
  - The extractor decodes each lane of oracle 0 in its own `C[lrow_0 + g_b]` (Berlekamp-Welch).
  - Soundness is unaffected as built. The weight is zero beyond the carried slots
    (`novel_weight_below(.., carried)`), and the `lambda`-identity above holds for any lengths, so the claim and the
    extracted witness depend only on the carried slots.
- **m-1 (MINOR):** Theorem S's round table (5.1) has the direct check `<P*, W'> = mu + cT`. As built
  (gaps 12.1, A26) this is a tail sumcheck of `n_last` rounds of degree 2. The calculator charges
  `2/q` per round, but Theorem S does not list them.
  - *Fix:* add the rows, with the state "relation false for `P*`" after the positions, to 5.1 and to Lemma 5.
- **m-2 (MINOR):** Lemma 4, proof case (c), says "degree below `lrow_i`". For A it should be `lf_i`. The
  displayed bound is already right.
- **m-3 (MINOR):** section 5.2 rests on "the book, Theorem 31.3.1 (M)". The definition Theorem TE'
  needs is [SG26] Definition 2.20. By Lemma 2.21 (total order, H2) it equals CMS19 Definition 8.5 with
  per-round errors.
  - *Fix:* cite those, and replace 5.2 by Lemma K-A (section 4).
- **NOTE:** the calculator charges the fold round's far term with the unfolded codeword length
  (`2^(log_n - j)`), not `N_i`. This is conservative.

## 3. Rounds outside the openings (A)

| Group | Listed with an error? | Proof or citation |
|---|---|---|
| W-I rounds, tail sumcheck | yes (`wi.rounds`) | Theorem S; gaps 12.1 |
| ZK additions: S4 `rho` and dummy, S9 `rho` and dummy, Keccak and bus `rho` and dummy, gadget `theta`, `c`, `z` (`wi.zk_rounds`) | yes | Lemma 6, section 6.3, gaps 3.5 and 11 (proved there; skimmed here, not refereed) |
| **Unmasked leanVM rounds:** bytecode-share sumcheck (4 rounds), bus fingerprint challenges and the bus GKR's sumcheck rounds (about 253 by the estimate), table sumcheck S4's rounds, Keccak reduction (12 layers), ring-switch map challenges, the stacked-claim `lambda`, the level-0 out-of-domain point (`read_ood`) | **no** | none: counted only in `k` as `OTHER_ROUNDS = 512`, marked an estimate in `shipping.py`. No per-round error is written or charged |

- **M-3 (MAJOR, record):** every unmasked round's error is asserted ("small degree"), never listed.
  The numbers are not at risk: each is a Schwartz-Zippel or fingerprint term. Even `2^30 / 2^256` is
  far below the 152.5-bit need. The count, however, sets the need.
  - Row 8's margins are 0.91 bits (rate 1/4) and 0.67 bits (rate 1/2).
  - So the total `k` (87 + 512) may be short by a factor of about 1.9 or 1.6 before row 8 misses.
  - The estimate (253 + 22 + Keccak + ring switch + batching) is near 512 by its own reading.
  - *Fix:* count `Transcript::sample` / `samples` calls in the `e2` verifier on the wallet statement under row 8.
    Write the per-round table with its degree and source for each group (as `soundness-method.md` 8.5d does for B).
    Replace 512 with the count.
  - *Acceptance:* a test that asserts the count equals the verifier's.
- Rounds whose error is asserted without proof: exactly the unmasked group in the table above.

## 4. K-A

**What TE' needs.** `lemma-tree-extraction.md` section 2 (K) needs [SG26] Definition 2.20 (causal
round-by-round knowledge soundness), and Theorem 6.6 (2) (page 58) needs it with per-round `eps^k`.
That definition asks for:
- a polynomial-time `E(x, tr|past(i))` and a state;
- (a) every accepted transcript on which `E` fails at every `i` has a challenge where the state goes from 0 to 1;
- (b) from state 0, if `Pr[State = 1] > eps_i^k`, then `E` succeeds.

Definition 2.24 (pages 15 and 16) is round-by-round *soundness* of a reduction at a fixed oracle input `U`. It has no
extractor and is not what (K) asks for. It is the right shape for S-3's rounds, with `U = Dec(O_0)`.

**What 5.2 gives.** It gives a state through unique decoding, and an extractor described at the BCS level ("reads oracle 0
from the random-oracle queries"). That is [SG26] Theorem I.16's job, not the IOP's. It covers only the opening's
relation `<p, W> = T`, not the leaf relation (the statement circuit). It does not check (a) or (b), and it decodes in the
wrong code (M-1).

**Lemma K-A (Original (the Ycash developers, 2026), draft, this report; relates to [SG26] Definition 2.20 and Lemma 2.21).**

*Setting.* Let A's leaf IOP have a total order whose first prover message is the oracle `O_0`. Let
`Dec(O_0)` be the lane-wise decoding of `O_0` in `A_{0,0}` within `e_0` (M-1), and `bot` if there is none.

*Hypotheses.* Let `State` be a function of `(x, Dec(O_0), tr)` with:
- (i) at the first challenge, `State = 0` if `Dec(O_0) = bot` or `(x, wit(Dec(O_0)))` is not in `R`, where
  `wit` takes the carried witness slots;
- (ii) a prover message never moves `State` from 0 to 1;
- (iii) from `State = 0`, challenge `i` gives `State = 1` with probability at most `eps_i`;
- (iv) `V` rejects every full transcript with final `State = 0`.

*Conclusion.* Then `E(x, tr|past(i)) := wit(Dec(O_0))`, Berlekamp-Welch per lane and polynomial time, makes the IOP causal
round-by-round knowledge sound with `eps_i^k = eps_i`.

*Proof.*
- `O_0` lies in `past(i)` for every `i`, so `E` is well defined.
- (b): by (iii) the premise `Pr > eps_i` never holds, so (b) holds vacuously.
- (a): let `tr` be accepted with `E` failing at every `i`. Since `E` is constant along the transcript, (i) gives
  `State = 0` at the first challenge, and (iv) gives final `State = 1`.
- In the total order, by (ii), the first rise is at a verifier message `i` with
  `State(x, i, tr|past(i)) = 0` and `State(x, i, tr|past(i) ∪ {i}) = 1`. ∎

*How A meets the hypotheses.* Take `State = 1` iff `O_0` is within `e_0` of `A_{0,0}`, every pending claim of
the outer protocol is true for `Dec(O_0)`, and the opening is not doomed in Theorem S's sense.
- (iv) is Theorem S's "doomed final state is rejected".
- (iii) is Theorem S for the opening and S-3 for the rest.
- (ii) holds because every later oracle and message enters only through claims about `Dec(O_0)` or the opening's
  state, which prover messages cannot make true.
- (i) holds when `R` is stated as "the decoded stack's carried slots satisfy the leaf constraint system". The outer
  protocol's initial claims are that statement.

**What is owed for K-A to close.** M-3's per-round list, with each unmasked round's soundness stated
with a state read off `Dec(O_0)`; Lemma 6 and section 6.3 already phrase theirs so. Also M-1's restatement of Theorem S,
and a referee of Lemma K-A. Nothing of a separate "knowledge" kind remains.

## 5. Is a system-A payment proof sound as built?

I found no concrete gap that lets a false statement verify. Checked:
- The order of every message the opening's proof needs, in `verify_wi`.
- That the fold `verify_wi` checks is the one Lemma 2A analyses.
- That the 128-bit build refuses rows 5 and up.
- That the tail sumcheck is charged.
- That excess-degree lanes (M-1) carry zero weight and change neither the claim nor the witness.
- That the mismatch between the model's and the implementation's multiplication by `X`
  (`zero-knowledge.md` 18.5) affects completeness and layout only. Soundness reads `x` from the verifier.

The residual risks are in the record:
- M-3's count, which could cost up to about 1 bit of need if it is short by 2x.
- The unmasked leanVM protocol's own soundness, taken from upstream and not refereed here.

## 6. Not checked

- Family B (Lemmas 2 and 3; eq-fold).
- Lemmas 6 and 7 and section 6.3 beyond a reading.
- The `zk-sound/` tests (not re-run).
- The prover code.
- The unmasked leanVM rounds' soundness, including the ring switch and the bus fingerprints.
- [SG26] Theorem 6.6's proof and Theorem TE' itself.
- MA-1.
- The Johnson regime.
- The duplicate-position handling for A (Lemma D, refereed elsewhere).
