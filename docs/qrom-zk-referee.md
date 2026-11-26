# Referee report: `qrom-compilation.md`, `zk-quantum.md`, `whir-additive-soundness.md`

Part of Yugen. An independent check of the three documents of `CITATION-AUDIT.md` 1d
(C-4, C-7, C-8, C-10 (b)) and of the numbers in `../qrom/test_numbers.py`, written 2026-11-19 by a
reviewer who did not write them. Every "proved" was treated as a claim to break. Provenance of
this report: **Original (the Ycash developers, 2026)** for every finding below; the results it
checks against are cited where used.

Verdict scale: **holds** / **holds under a stated extra hypothesis** / **gap** (the argument is
missing or incomplete, the claim may be true) / **wrong** (the claim or number is false).

## 0. Sources read for this report

Text extracted from the lead architect's copies into a scratch directory outside every repository.

- [CMS19] A. Chiesa, P. Manohar, N. Spooner, "Succinct Arguments in the Quantum Random Oracle Model",
  ePrint 2019/834 (copy dated January 14, 2020): Section 3.3 (definitions, zero knowledge), 3.4,
  4.1 to 4.2 (Lemmas 4.5, 4.9), **5.1 to 5.3 in full (Lemmas 5.7, 5.9, 5.10 with its proof, 5.13,
  Proposition 5.12)**, 7 (Theorem 7.1, **Lemma 7.3 and its proof**, Lemma 7.4, Proposition 7.5),
  8.1 to 8.6 (Definitions 8.1 to 8.5, Theorem 8.6, HExtract, BCSExtract, Lemma 8.8, Claims 8.9,
  8.10, Proposition 8.12, **Lemma 8.13 and its proof**, Section 8.5.2, **Section 8.6**).
- [BCIKS20] E. Ben-Sasson, D. Carmon, Y. Ishai, S. Kopparty, S. Saraf, "Proximity Gaps for
  Reed–Solomon Codes" (copy fetched by an earlier session, not among the lead architect's files):
  Theorem 1.2 (`eps_U = n/q`), Theorem 1.4, Remark 1.5, Theorems 1.6, 1.7.
  *Citation amendment (2026-11-19, `CITATION-AUDIT.md` C-41; text below unchanged):* in the
  folder copy (ePrint 2020/654, revision of July 3, 2021) these are Theorems 1.2, 1.4, Remark 1.2,
  Theorems 1.5 (curves), 1.6 (affine spaces): "Theorem 1.7" below is Theorem 1.6 there, "Remark
  1.5" is Remark 1.2; statements unchanged.
- [WHIR] G. Arnon, A. Chiesa, G. Fenzi, E. Yogev, "WHIR: Reed–Solomon Proximity Testing with
  Super-Fast Verification", ePrint 2024/1586: Lemma 4.10, Corollary 4.11 (statements only).
- [CWYZ26] A. Chiesa, M. Weissenberg, E. Yogev, Z. Zheng, "Affine Combiners for Reed–Solomon
  Proximity Gaps", ePrint 2026/2863 (copy dated November 13, 2026): Section 5, the paragraph
  "Higher-arity interleavings" and Theorem 5.2.
- [SG26] C. Sharp, P. Grubbs, "Faster and Smaller Anonymous Credentials from Standardized
  Signatures" (the GordieHowe system), ePrint 2026/2615: Definition 2.18, Definition 2.20, Section 6
  in full (Definitions 6.1 to 6.3, Protocol 6.5, Theorem 6.6 and the text after it), Appendix I.1
  (Definition I.1, oracle domain, encodings, samplers, Merkle trees), the opening of I.2, Section 8.4.
- [CY] A. Chiesa, E. Yogev, "Building Cryptographic Proofs from Hash Functions" (book, copy fetched
  by an earlier session): Claims 3.4.1, 3.4.2 with proofs, Definition 23.2.1 (IOP
  state-restoration game), Theorem 31.2.1 (statement).
- [BCS16] E. Ben-Sasson, A. Chiesa, N. Spooner, "Interactive Oracle Proofs", ePrint 2016/116: the
  introduction's description of state-restoration attacks (Lemma 3.4 checked only numerically).
- Code read: leanVM verifier at the pin (`yugen-proof-a/vendor/leanMultisig/crates/verifier/src/whir.rs`:
  `derive_config_for`, `verify_whir`; `params.rs`: `level_queries`).

Not read by this reviewer: ePrint 2016-116 beyond the passages named, 2021/1259, 2026/2056,
2026/391, 2023/1071 (no claim under review rests on them in a way this report changes), the proof
bodies of SG26 Appendices I.2 to I.4. Numbers recomputed with an independent script in the
scratch directory (standard library only); the author's `qrom/test_numbers.py` was also run and
exits 0 (FAILURES 0).

---

## 1. `qrom-compilation.md`

### 1.1 Observation 1 (no IOP fits CMS19's construction verbatim; splitting a round loses RBR)

**Verdict: holds, with one overclaim to correct.**

- Part (ii) rested on a recollection of the state-restoration game (marked M). Checked: CY
  Definition 23.2.1 draws `rho_i := rnd_i(x, Pi_1..i, sigma_1..i)` with salts, and Definition 23.2.2
  quantifies over every salt size, so a restoring prover gets fresh randomness by changing a salt;
  Theorem 31.2.1 gives `eps_sr <= (t + k) eps_rbr`. The lower bound `eps' >~ (1 - delta)^(Q/r) / r`
  follows; recomputed: `2^(-152.3/28) / 28 = 2^-10.2`. The M mark can become S (CY Def. 23.2.1,
  Thm. 31.2.1).
- Overclaim: "no transcript that keeps Theorem 8.6 verbatim exists" is false as stated. CMS19's
  construction with `lambda` set to the longest round's need (`h: {0,1}^(2 lambda) -> {0,1}^lambda`
  realised by a truncated XOF, `lambda` of several thousand bits) is Theorem 8.6 verbatim; it is
  excluded only because every digest would then be `lambda` bits. Fix: say "no transcript with
  256-bit digests".

### 1.2 Findings Q-1 and Q-2 (transcripts as built)

**Verdict: hold.** Q-1 (c) is CMS19 Section 8.6 exactly: the BCS16 chain needs the strong
round-by-round property (fill-in of an undefined earlier message) and the proof there is only "nearly
identical" (S, CMS19 p. 46). Q-2's argument (the worst-case database in the instability fixes all
blocks but the last) is correct for iterated expansion.

### 1.3 Lemma X (counter mode costs a factor 2 in quantum queries)

**Verdict: holds.** Compute-add-uncompute is a perfect simulation; `H` on the "exp" domain and `G`
are the same function re-indexed. The resulting pair (`H` off the exp domain, `G` long-output) is one
random oracle with disjoint domain parts, which is what CMS19's compressed oracle needs (Section 3.6,
domain any finite set after an injective encoding).

### 1.4 Theorem Q, form X (A)

**Verdict: holds under stated extra hypotheses, as a proof sketch; the "P" tag is premature.**

What I checked against the lemmas the author did not re-read:

- **Lemmas 5.9, 5.10, 5.13 are generic.** Lemma 5.9 needs only `∅ ∉ P`; the proof of Lemma 5.10
  (Section 5.3) uses only the decomposition of the compressed oracle (Lemma 3.2) and the flip
  probabilities over a uniform `y in {0,1}^n`, for any output length `n` and any finite domain;
  Lemma 5.13 is Lemmas 5.9, 5.10 with Proposition 5.12 (3). Nothing in them uses `n = lambda`, binary
  trees, unsalted leaves or the shape of the chain. So change (a) (one oracle, output `n = max L_j`,
  digests as `lambda`-bit prefixes) is sound, and everything structural moves into the instability
  bound (Lemma 8.13's analogue), as the author says.
- **Lemma 8.13's analogue** (5.2 (b), (c)): the case split of CMS19's proof (Case 1: an extraction
  changes, so `y`'s prefix lies in `S(D) ∪ {z}`; Case 2: the new entry is the round's challenge for
  the extracted prefix, probability `<= eps`) carries over to form X because form X **writes the
  challenge back**: the next link's input contains `rho_j[0..lambda)`, the prefix of the very output
  that is the challenge. A continuation built before the challenge exists must contain a guessed
  prefix, which is the `S(D)` event. Salted, hashed leaves add no pointer components (extraction
  stops at the leaf entry and drops the salt). The pointer count per link input is 2 (chain value,
  root) plus the constant statement digest of link 1, so `|S(D)| <= 2|D|` holds.
- **Constants follow** for binary trees: `6 (t^2 eps + t^2 (2t + 1)/2^lambda + t^3/2^lambda) <=
  6 (t^2 eps + 4 t^3/2^lambda)`; arity `a`: `6 (a + 2)`, as stated in 5.2 (e).
- Extra hypotheses that must be stated in the theorem: (H1) the uniformity of each challenge in its
  space `R_j` given a uniform `L_j`-bit prefix (true for `GF(2^256)` elements and power-of-two
  positions read as `sample_queries` reads them; to be asserted per challenge type, including any
  challenge set whose size is not a power of two); (H2) every IOP round begins with a prover message
  (a verifier-first round needs an empty-message link, which the CMS form must specify); (H3) the
  modelling of Keccak-256 and SHAKE256 as one random oracle on disjoint domains. (H3) is better than
  the document says: SHAKE256's padding appends the suffix bits `1111` before `pad10*1`, so
  `SHAKE256(M)` is the Keccak[c=512] sponge on `M || 1111`, never a byte string, hence disjoint from
  every Keccak-256 input (Original observation, from the FIPS 202 padding rule as recalled, M).
  Idealising the sponge itself in the QROM remains a heuristic (quantum indifferentiability of the
  sponge is, from memory, proven for random-function inner maps, not for a fixed permutation: M).
- What makes this a sketch, not a proof: Lemmas 6.4, 6.5, 8.7, 8.8 and Claims 8.9, 8.10 are
  asserted to "hold with `S(D)` redefined"; HExtract's uniqueness test now compares `lambda`-bit
  prefixes of long outputs, and the knowledge part (Proposition 8.14) is not re-derived. Work that
  closes it: either a written restatement of CMS19 Section 8.5 for form X, or adopting the published
  spBCS form (section 4 below), which removes the need.

### 1.5 Theorem Q, form C (B)

**Verdict: gap.** Form C continues the chain from the link digest `c_j`, **not** from the challenge
(the document says so explicitly: "The chain continues from `c_j`, not from the last expansion
block"). The challenge `G(c_j)` is therefore not an input of the next link: an adversary can build
link `j + 1` (and many continuations) on `c_j` before `G(c_j)` is defined, and later define it. This
is the BCS16 chain of CMS19 Section 8.6 again, the very problem Q-1 (c) identifies for A's duplex.
Change 5.2 (d) treats only the opposite order (a link entry landing on an already-defined `G`
input, `t/2^lambda`). In the reverse order the fill-in of `G(c_j)` makes every continuation's
extracted transcript well formed at once, and the probability over that one value that some
continuation's state goes from 0 to 1 at a **later** round (whose challenge is already fixed in the
worst-case database) is bounded only by the strong round-by-round property of Section 8.6, and a
union over continuations then costs up to a factor `t`. Lemma 8.13's Case 2 does not apply.

This is a gap in the proof, not an attack (a prover that pre-commits candidate continuations has no
more power than one that answers after the challenge), but the constants `C1 = 24`, `C2 = 240` are
unproved. Fix (buildable, no proof-size change): **write the challenge back**:
`c_(j+1) = SHA-256("Yugen/fs/link" || j+1 || rho_j[0] || rt_(j+1) || msg_(j+1))`, with
`rho_j[0] = SHA-256("Yugen/fs/exp" || c_j || 0)` the first expansion block. With Lemma X the pointer
`rho_j[0]` is the prefix of the `G` entry's output, and 5.2 (b) to (d) then go through with the
extra `t/2^lambda` the document already counts. Acceptance: form C's specification and the
`HasherChallenger` change carry the write-back; a test that a changed challenge block changes every
later challenge. Section 4 gives the published form that has this property.

### 1.6 B's leaves and domain separation

**Verdict: gap (small).** Section 4 asserts that "labels are fixed byte strings that no other hash
input of the system can begin with", but form C keeps B's leaves "as built":
`SHA-256(serialised values, salt)` with no tag. Leaf values are prover-chosen field elements, so a
malicious leaf can begin with `"Yugen/fs/link"` and have the length of a link input (96 bytes is
possible), making one oracle point both a leaf and a link entry. CMS19's `Extract`/`HExtract` and
SG26 (Appendix I.1, "four disjoint parts") both rely on disjoint parts. Fix: a one-byte part tag on
B's leaf inputs (the SHA-256 block count of a 96-byte leaf stays 2; of a 128-byte leaf, 3).

### 1.7 Finding Q-3 (B's inner nodes as the raw compression function)

**Verdict: the recommendation is harmless, the reason given is wrong.** Davies–Meyer fixed points
need the attacker to choose the chaining input; with a fixed, domain-separated initial value `IV'`,
`m -> E_m(IV') xor IV'` evaluated at distinct `m` uses distinct keys and is a random function in the
ideal-cipher model (classical reasoning; the quantum ideal-cipher statement is not in hand, M).
Modelling `f(IV', .)` as a random oracle is the same kind of heuristic as modelling SHA-256 on fixed
64-byte inputs. Correct the text; keeping the inner nodes as built is defensible, recorded as a
modelling assumption. Counter-mode SHA-256 on fixed-length, tagged inputs: length extension does not
arise (fixed length, prefix-free by tag); a standard heuristic.

### 1.8 Section 6 numbers

Recomputed independently (`e = 152.343`, `N = 20,000`, `lambda = 256`):

| Constants | `kappa_IOP` | `kappa_hash` | Document | Verdict |
|---|---|---|---|---|
| 6, 24 | 67.235 | 78.709 | 67.24 / 78.71 | holds |
| 24, 240 | 66.235 | 77.602 | 66.24 / 77.60 | holds as arithmetic (constants unproved, 1.5) |
| "`a_V <= t` folded in: 12, 96" | 66.735 | 78.042 | 66.74 / 78.04 | **wrong** |

The third row doubles the quadratic term and quadruples the cubic one. With `t' = t + a_V <= 2t`:
`6 (2t)^2 = 24 t^2` and `24 (2t)^3 = 192 t^3`, so `C1 = 24`, `C2 = 192`: **66.24 / 77.71**. For form C
with `a_V <= t` (`t' <= 3t`): `C1 = 54`, `C2 = 810`: 65.65 / 77.02. Every row still meets 64; the
separate `a_V` estimate of the paragraph below the table is right in substance. The scale is
consistent with the stated target: `kappa_IOP >= 64` iff `e >= 129 + log2 C1 + log2 N` (145.9 for
`C1 = 6`).

### 1.9 Finding Q-4

**Verdict: holds.** Not re-checked beyond the statement of Construction 25.1.1 as quoted.

### Overall, `qrom-compilation.md`

**Gap.** Observation 1, Q-1, Q-2, Lemma X and the form-X arithmetic hold; Theorem Q for form X is a
credible sketch, not a proof; Theorem Q for form C is unproved as specified (no write-back); one
table row is wrong. A published theorem (SG26 Theorem 6.6 (2), section 4) covers a transcript form
that can be adopted for A outright and for B with Lemma X; it should replace Theorem Q as the basis.

---

## 2. `zk-quantum.md`

### 2.1 Lemma M (classical, query-bounded)

**Verdict: holds.** Checked the step most likely to fail: an adversary can test a candidate salt
for an unopened leaf by recomputing the path to the root, but that test is itself a query at the
leaf point, i.e. event `E`; outside `E` the posterior of each unopened salt is uniform on the salts
not yet queried, so the per-query bound is `1/(2^s - t)`, which the stated `2^-s` approximates.
`t N_u / 2^s` at `s = 256`, `t = 2^128`, `N_u = 2^24`: `2^-104` (recomputed).

### 2.2 No statistical statement at `s = sigma = 256`

**Verdict: holds, and it is published.** CY Claim 3.4.1 (lower bound) gives constant expected
distance per leaf; with the witness, a distinguisher holding the whole oracle tests whether a
sibling digest on the copath lies in the image of `H(row, .)` (probability 1 real, about `1 - 1/e`
simulated), so the distance tends to 1 over many leaves. SG26 Section 8.4 states the same (`(1 -
2^-lambda)^(2^lambda)`, close to `1/e`, "statistical zero knowledge does not follow"). Provenance
fix: cite SG26 Section 8.4 for the statement; only the Grover cost is new here.

### 2.3 The Grover attack at about `2^128` queries

**Verdict: holds under a stated extra hypothesis.** It needs every unopened row to be determined by
the witness and the opened rows, i.e. Lemma E's masking dimension equal to the number of opened rows
of that lane. Where a lane has more random coefficients than opened rows, unopened rows are not
determined and the attack weakens. State the hypothesis per oracle. The `0.63^m` repetition and the
`2^128` cost per test are right.

### 2.4 Lemma H

**Verdict: holds.** CY Claim 3.4.2 (read in full) is exactly `E_f[max_x Delta(f(x, U_s), U_sigma)]
<= 2^(-(s - sigma)/2) + sqrt(n) 2^(-s/2)`, `n` the query size in bits; the hybrid over leaves,
conditioning on `H`, is sound and covers rows that depend on `H`. Two corrections: (a) `n_b <= 2^12`
is slightly below A's level-0 leaf query (512-byte row plus the 13-byte label of form X, about
4,200 bits); the effect is under 0.02 bits. (b) Provenance: SG26 Definition I.1's `eps_leaf` is the
same bound (first term with CY 3.4.1's factor `1/2`, second via the same maximal inequality, over
byte strings of length at most `L_leaf`); Lemma H is Published (SG26 Def. I.1 and its derivation
from CY Claims 3.4.1, 3.4.2), not Adapted.

### 2.5 Theorem ZQ and CMS19 Lemma 7.3

**Verdict: holds under stated extra hypotheses; three of them are not met by the deployment.**

- **Lemma 7.3 carries statistical ZK to quantum distinguishers**: checked. Its proof (p. 35) and
  the definition of Section 3.3 compare `(h, pi)` with `(h[mu], pi)` with `h` the whole truth table;
  a quantum distinguisher with superposition access to `h` is a randomised function of the table, so
  the bound transfers. This step holds.
- **(E1) Non-adaptive witness.** CMS19 Section 3.3 fixes `(x, w)` before `h`. The document asserts
  "the wallet chooses its witness independently of the hash function". **Wrong for the recursion
  tree**: a node proof's witness is the inner proofs, which are functions of `h`; and any note
  commitment tree hashed with the same function makes leaf witnesses depend on `h` too. Hybrid 1
  (reprogramming at link inputs) then needs the probability that the witness's generation queried a
  programmed point. Fix: restate ZQ for a witness produced by a `t_w`-query computation before the
  proof, with an extra term `<= t_w k / 2^256` (each link input contains a fresh root that is a
  function of uniform unopened digests), or adopt SG26 Theorem 6.6 (3), which is adaptive by design
  (section 4).
- **(E2) One proof.** ZQ bounds one proof. A wallet publishes many; the error composes at least
  linearly (`Q zeta` by a hybrid, plus cross-proof collisions of programmed points), and SG26's
  Part (3) shows the Q-proof form needs a per-proof salt in every challenge input. Section 3 of the
  document does not say this.
- **(E3) Unsalted trees.** The hypothesis table excuses B's unsalted fold oracles because "the
  simulator produces them in full". Then `zeta_IOP` must be the HVZK error of a view that contains
  those oracles **in full**, not only the queried positions; Hybrid 3 as written uses "challenges and
  query answers". State the stronger view explicitly or salt those trees.
- **HVZK prerequisites.** Section 4 lists them as not established, correctly; but section 3 states
  "`zeta_IOP` ... is below `2^-240`" as if established. Mark it conditional on the open items.

### 2.6 Salt table and costs

Recomputed: per proof `2^-40`, `2^-104`, `2^-136` at 384, 512, 576 bits (`N_u = 2^24`, `n_b = 2^12`);
BCS16 Lemma 3.4 `2^-38`; +32 B per opened leaf: A 728 leaves = 22.75 KiB, B 368 = 11.5 KiB; 576-bit:
28.4 / 14.4 KiB; Keccak-f per leaf 5 and 3 unchanged (also with the 13-byte form-X label: 589 and 333
bytes still 5 and 3 blocks); B 96-byte leaf 2 blocks, 128-byte leaf 3. **All hold.**

### Overall, `zk-quantum.md`

**Holds under stated extra hypotheses**, with one wrong premise (E1) that matters for the recursion
tree, a missing composition across a wallet's proofs (E2), and a provenance correction (Lemma H and
section 2.1 are published in SG26). The recommendation of 512-bit leaf salts is right and is
independently what SG26 uses (`b_l = 2b`); it is not sufficient on its own (section 4 (ii)).

---

## 3. `whir-additive-soundness.md`

### 3.1 Theorem S0 and its use of BCIKS20 Theorem 1.7

**Verdict: holds (as a careful sketch).** Checked:

- BCIKS20 Theorem 1.7 is stated for an affine space `u_0 + span{u_1..u_l}` of words over `F_q` on any
  evaluation set and an RS code `RS[F_q, D, k]`, with `eps_U = n/q` (Theorem 1.2) for
  `delta <= (1 - rho)/2`. The fold `G + alpha F + beta (xF)` with uniform `(alpha, beta)` is uniform on
  the affine space `G + span{F, xF}` (a linear surjection has equal fibres), so the hypothesis "Pr over
  `u in U`" is met. Level 0 words over `K = GF(2^64)` with challenges in `GF(2^256)`: Remark 1.5.
- **At the true rate and distance**: the level radius is `e_i = floor((N_i - d_i)/2)` with `d_i` the
  largest degree bound of the level; for every code `C[D]`, `D <= d_i`, used in Lemma F0,
  `e_i/N_i <= (1 - D/N_i)/2`, so every application is inside Theorem 1.7's unique-decoding range, and
  `N_i - e_i > D` gives Lemma 2A's polynomial identity `x f_1 = f_2`. Valid.
- The interleaved step (a common disagreement set over all lane pairs) is not in BCIKS20; Lemma 2A
  does it by counting (`|Dis| (|Gam| - q) <= e |Gam|`), which I checked and accept.
- WHIR Lemma 4.10 (statement read) needs a proximity generator for a linear code; the
  `(G, F, xF)` generator is one by Theorem 1.7. Lemma 2A already names the common agreement set, so
  the appeal is not needed.
- Lemma C0's two cases give per-position pass probability at most `(N + d - 1)/(2N) < (1 + rho)/2`;
  the `lambda` polynomial has degree `Q_i + 1` (the verifier's `lambda * ood + lambda^2 * sum lambda^q`,
  read in `verify_whir`). Lemma B0: positions drawn after `P*` (read). Holds.

Open, as the document says: the prover-side meaning of the four fold scalars and the lane order.

### 3.2 Finding W-1 (true rate)

**Verdict: holds; the citation should change.** The verifier (read at the pin) accepts any final
lane of `(1 << mu) + fold_count` scalars, and at a non-final level corrects each position by
`novel_eval(high, what) * what[mu]` with `fold_count` high coefficients, on a block of
`2^(mu + level_rate)` points. The code tested is therefore of dimension `2^mu + kappa`, and the
unique-decoding query bound needs `rho = (2^mu + kappa)/2^(mu + r)`. The degree growth is elementary
(`(alpha + beta X) F` raises the degree by one per round) and is read from the verifier code.
CWYZ26 Theorem 5.2, as cited, is a statement about the **equal-degree variant** with a third
challenge `theta` (`f_(2i) + (alpha + beta z)(f_(2i-1) + theta f_(2i))`, inputs of degree at most
`d`, output degree at most `d + r`), not leanVM's combiner; cite it as "consistent with", and the
verifier code as the source.

### 3.3 W-1 numbers

Recomputed with an independent transcription of `derive_config_for` (checked against the pinned
source) and the `ByLevelRate` list (369, 226, 185, 168, 161, 157, 155, 154, ...):

| Row, stack, rate | True-rate weakest | Margin | Document |
|---|---|---|---|
| 7, `2^22`, 1/2 | 152.97 | +0.63 | +0.63 |
| 7, `2^22`, 1/4 | 153.24 | +0.90 | +0.90 |
| 9, `2^24`, 1/2 | 148.02 | -4.35 | -4.35 |
| 9, `2^27`, 1/2 | 148.02 | -4.36 | -4.36 |
| 9, `2^27`, 1/4 | 151.23 | -1.15 | -1.15 |
| 9, `2^25`, `2^26`, `2^28` | as the table | as the table | match |

Fix counts 173 / 163 / 170 / 169 reproduce. **All hold.** The needs (152.343 to 152.375) were taken
from the calculator as constants and were not re-derived here.

### Overall, `whir-additive-soundness.md`

**Holds.** Theorem S0 is a sound unique-decoding argument at the true rate; W-1 is right and its
numbers reproduce; one citation (CWYZ26 Theorem 5.2) supports a different combiner and should be
relabelled.

---

## 4. Sharp–Grubbs (ePrint 2026/2615), Theorem 6.6: a published route

The audit's note that this paper was unused is out of date; C-21 is correct that it is relevant.
What it publishes (SG26 Protocol 6.5, Theorem 6.6, Appendix I.1, all read): **spBCS**. Per verifier
message `i`: a key `u_i = dg(H(ch(label || salt(s) || pre(x) || items(i, l_i))))` whose input lists
**all** items of the past (each prover message's non-oracle part and roots, each earlier verifier
message's written-back digest), then a stream `y_i = H(stream(u_i, s))` of `b + e` bytes, the
challenge `theta_i = sample_i(y_i)` (equal preimage counts), and the **write-back** `dg(y_i)`. One
random oracle with four disjoint input parts (challenge inputs, leaves `leaf(r, v)`, nodes
`node(d, d')`, streams); digests are the first `8b` bits; binary Merkle trees with salted leaves; a
proof salt `s` in every challenge input and stream point. Their implementation models SHA-384 and
cSHAKE256 as that one oracle (I.1, "Hash functions").

### (i) Theorem 6.6 (2): which transcripts it covers, and its loss

- **System A as built (duplex sponge): not covered.** No random-oracle call per challenge input, no
  write-back structure.
- **System B as built: not covered.** Its chain input is the previous digest, not the past's item
  list, and its iterated expansion is not one stream call.
- **CMS form X: not covered verbatim** (chain value instead of the past's items; one call instead of
  key then stream). **Form C: not covered** (no write-back; section 1.5).
- **Covered: a transcript in spBCS form** (Protocol 6.5 with the total order, no merges). For
  soundness the proof salt may be empty (I.1: knowledge soundness "hold[s] at every salt length,
  including 0"). The hypothesis on the IOP is causal round-by-round knowledge soundness, equal to
  CMS19 Definition 8.5 for a total order (SG26 Def. 2.20 and Lemma 2.21 as stated there); Theorem S0
  claims the knowledge form, B's state functions must be checked for it.
- **Bound** (QROM): `eps_ex(t) = 2 sqrt(k_q / 2^(8(b+e))) + 6 (t + k_q)^2 (eps_k + c' (t + k_q) / 2^(8b))`,
  `c' = max(2, c) + n_J + 1`, `c = N_msg max(1, m)`, `k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2 l_max)))`.
  So `C1 = 6` exactly as Theorem Q, and `C2 = 6 c'` (24 only when `c' = 4`; it grows with the
  number of messages because every challenge input carries every past digest).
- **Numbers** at `lambda = 256`, `N = 20,000`, `e = 152.343` (`N_msg` per system to be counted; the
  hash term is never binding):

| Route | `kappa_IOP` | `kappa_hash` at `c' = 2^5 / 2^7 / 2^9` |
|---|---|---|
| A, spBCS form, Keccak-256 + SHAKE256 as one oracle | **67.24** (same as Theorem Q) | 77.71 / 77.04 / 76.38 |
| B, spBCS form with a SHAKE256 stream | 67.24 | as A |
| B, spBCS form with counter-mode SHA-256 stream + Lemma X (`2t`) | 66.24 | 76.71 / 76.04 / 75.38 |

**Recommendation (replaces Theorem Q as the basis).** System A: adopt the spBCS form; Theorem 6.6
(2) then applies **as published**, with the same 67.2 bits. Implementation note (Original,
to be confirmed against I.1's encoding): for the total order the challenge inputs are
prefix-extending (I.1: "For the total order without merges the index ... is not written"), so one
running sponge state is absorbed once and cloned and finalised per challenge; the cost is one
finalisation and one stream squeeze per verifier message, not a re-hash of the past. System B:
either a SHAKE256 stream (published theorem verbatim; adds Keccak to B's circuit) or counter-mode
SHA-256 streams with Lemma X (Adapted: Theorem 6.6 (2) with Lemma X, 66.2 bits; the adaptation is
only the query doubling). Both systems: tag every input part (B's leaves, 1.6); B's inner-node
compression function stays a modelling assumption (1.7). Acceptance: the transcript modules follow
Protocol 6.5 byte for byte (labels, item encodings, write-back), a test vector recomputes every
challenge with an independent hash implementation, and the calculator evaluates `eps_ex` with the
counted `N_msg`, `c'`, `k_q`.

### (ii) Theorem 6.6 (3): 512-bit salts with 256-bit digests

- **Leaf-salt hypothesis: met.** `b = 32`, `b_l = 64 > b`.
  `eps_leaf = (1/2) sqrt(2^(8b)/2^(8 b_l)) + sqrt(ln N_leaf / (2 * 2^(8 b_l))) = 2^-129 + 2^-251`
  (`L_leaf` about 600 bytes), so `n_pos eps_leaf = 2^-105` at `n_pos = 2^24`, against Lemma H's
  `2^-104` (the factor `1/2` is CY 3.4.1's, which CY 3.4.2 drops).
- **Other hypotheses: not met by either CMS form.** Part (3) needs the spBCS transcript **with a
  proof salt of `b_s` bytes in every challenge input and stream point**, and the IOP's HVZK at every
  statement (open, `zk-quantum.md` 4).
- **Its error is of another kind than ZQ's**: everlasting zero knowledge (SG26 Def. 6.2) against
  adversaries with `t` hash queries before the last proof and unbounded afterwards, `Q` adaptively
  chosen proofs:
  `eps_zk(t, Q) = 4 Q t / 2^(4 b_s) + Q(Q - 1)/2^(8 b_s) + Q (eps_key + eps_ov + eps_hvzk + n_pos eps_leaf)`.
  At `t = 2^64`, `Q = 2^20`: `b_s = 32` gives `2^-42` (inadequate), `b_s = 48` gives `2^-106`,
  `b_s = 64` gives `2^-170`; and `Q n_pos eps_leaf = 2^-85`. ZQ's `2^-104` is for **one** proof with
  a non-adaptive witness; for a wallet the comparable figure is about `2^-85` either way.
- Part (4) (unconditional witness indistinguishability, no bound on hash queries at any time,
  adaptive choice) gives `Q (2 n_pos eps_leaf + 2 eps_hvzk + eps_ov + eps_key + sqrt(((L + 1) ln 2 +
  2 ln(L + 1)) / (2 * 2^(8 b_s))))`: at `b_s = 32`, `L = 2^20` bits the salt term is `2^-118.8` per
  proof. It is the right published statement for "recorded transactions against a future quantum
  computer" when witnesses are many and adaptively chosen.

**Recommendation.** Keep 512-bit leaf salts; add a 64-byte proof salt to every challenge input and
stream point (spBCS form); state privacy as SG26 Theorem 6.6 (3) (everlasting ZK, QROM) and 6.6 (4)
(unconditional WI), evaluated per wallet at the agreed `Q`; keep Theorem ZQ only as a single-proof
corollary. Cost: one 64-byte salt per proof, absorbed once per challenge input.

---

## 5. Summary of verdicts

| Claim | Verdict |
|---|---|
| Observation 1 | holds (overclaim "no transcript" to be narrowed; SR game now sourced) |
| Q-1, Q-2 | hold |
| Lemma X | holds |
| Theorem Q, form X | holds under stated extra hypotheses (H1 to H3), as a sketch |
| Theorem Q, form C | **gap**: no write-back; fix by chaining from the first expansion block or spBCS |
| B leaves untagged | gap (small): add a part tag |
| Q-3 reasoning | wrong reason, harmless recommendation |
| Section 6, rows 1, 2 | hold (arithmetic) |
| Section 6, row 3 (`C1 = 12`, `C2 = 96`) | **wrong**: 24, 192, giving 66.24 / 77.71 |
| Lemma M | holds |
| No statistical ZK at 256-bit salts | holds; published in SG26 8.4 |
| Grover attack `2^128` | holds under the hypothesis that unopened rows are determined |
| Lemma H | holds; Published (SG26 Def. I.1), not Adapted |
| Theorem ZQ via CMS19 Lemma 7.3 | holds under extra hypotheses; **non-adaptive witness is false for node proofs**, no multi-proof composition, unsalted trees need a full-view HVZK; `zeta_IOP < 2^-240` unsupported while HVZK is open |
| Salt table, +32 B, KiB, block counts | hold |
| Theorem S0 (BCIKS20 1.7 at true rate) | holds |
| W-1 and 4.36 / 1.15 / 0.63 | hold; CWYZ26 5.2 cited for a different combiner |
| SG26 6.6 (2) | covers the spBCS form: adopt for A (67.2 bits, published), B with Lemma X (66.2) |
| SG26 6.6 (3) with 512-bit salts | leaf hypothesis met (`2^-105`); needs proof salt and spBCS; per wallet about `2^-85` |

Overall: `qrom-compilation.md` **gap** (superseded for A by a published theorem);
`zk-quantum.md` **holds under stated extra hypotheses**, one of them false for recursion;
`whir-additive-soundness.md` **holds**.

## 6. For the plan and the citation audit (not edited here)

- CITATION-AUDIT 1d's C-7 entry quotes `C1 = 24`, `C2 = 240` for B as established: unproved (1.5).
- `REFERENCES.md` should list SG26 Theorem 6.6, Protocol 6.5, Definition I.1 and Section 8.4 against
  `qrom-compilation.md` and `zk-quantum.md`; Lemma H and the `s = sigma` statement move from
  Adapted/Original to Published.
- The privacy claim of the plan should be stated for `Q` proofs per wallet, adaptively chosen.
