# Lemma K-B: round-by-round knowledge soundness of system B (DRAFT, revision 2026-11-19)

Part of Yugen. Maths team, 2026-11-19. Obligation K-B of `what-is-proven.md` (hypothesis (K) of
`lemma-tree-extraction.md` revision 3, section 2; `qrom-compilation.md` H3, T-5). Written in the manner of the
draft Lemma K-A (`theorem-s-referee.md` section 4). **Original (the Ycash developers, 2026), DRAFT until refereed.**
Code: `yugen-proof-b2` `1f67267`. Rounds and errors: `b-round-census.md`.

## 1. What Theorem TE' needs from B

(K) asks that each IOP of the tree be causal round-by-round knowledge sound in the sense of [SG26] Definition 2.20
(C. Sharp, P. Grubbs, ePrint 2026/2615, page 14): a polynomial-time extractor `E` and a state function `State`, both
reading only the past of a challenge, such that (a) every accepted transcript on which `E` fails at every challenge
has a challenge where `State` rises from 0 to 1, and (b) from `State = 0` the rise has probability at most
`eps_i^k`, or else `E` succeeds. TE' then charges `t eps_max + sum_v |J_V,v| eps_v`; the calculator's `e` of a B row
is used as `-log2 eps_max`. So K-B is: **for the leaf relation `R_leaf` and the node relation `R_node`, B's IOP has
causal round-by-round knowledge errors no larger than the per-message soundness errors of the census**, so that the
row's `e` (the query round, 159.37 / 159.35 bits) is a knowledge error.

The relations (as the tree lemma uses them): `R_leaf` = "the hidden words of the trace satisfy the leaf constraint
system with the stated public words"; `R_node` = "the trace satisfies the node's main circuit and its slots", where
a slot's satisfaction includes the in-circuit verifier's acceptance of a child with its wiring claim **deferred**
and the batching step's final checks; the deferred claims leave the node as public claim words.

## 2. Lemma K-B

**Setting.** B's IOP for one proof has the total order of its messages (series order; [SG26] Definition 2.18).
Its oracles, in order (`spartan-verifier/src/wrapper/zk_wrapped_channel.rs:68-110`; `verifier/src/verify.rs:236`):
for the leaf, `O_pre` (the wrapper's precommit: the one-time keys of the inner prover messages), `O_tr` (the trace),
then the wrapper's private and mask oracles; for a node, `O_tr` only. Both `O_pre` and `O_tr` are received before
the first challenge (`verify.rs:236` precedes `reduce_constraints`, the first `sample`). Let `Dec(O)` be unique
decoding of `O` within the radius the opening's analysis uses (S-4, Lemma UD; for `O_tr` in `L = GF(2^128)` under
form T, Lemma 4 of `binius-extension-challenges.md` 4.1 places the decoded codeword over `L`), and `bot` if none.
Write `wit(Dec(O_tr))` for the hidden trace words, and for the leaf `m_i = c_i - k_i` for the decrypted inner prover
message whose ciphertext `c_i` is in the transcript and whose key `k_i` is the `i`-th precommit word of
`Dec(O_pre)`.

**Hypotheses.** A function `State(x, tr)` (revised 2026-11-19, m-B2), which reads the decodings of all oracles in
`tr|past(i)` (`Dec(O_pre)`, `Dec(O_tr)` and, once received, the wrapper's private and mask oracles, as Theorem S's
per-oracle state does), with:
- (i) at the first challenge, `State = 0` if a decoding is `bot` or `(x, wit(Dec(O_tr))) not in R`;
- (ii) a prover message never moves `State` from 0 to 1;
- (iii) from `State = 0`, the message `i` gives `State = 1` with probability at most `eps_i`, the census error of
  message `i` (`b-round-census.md` 2.1, 2.2);
- (iv) `V` rejects every full transcript with final `State = 0`.

**Conclusion.** `E(x, tr|past(i)) := wit(Dec(O_tr))` (Berlekamp-Welch per column, as [Dia25] Theorem 4.2's
extractor and DP24 Algorithm 1; polynomial time) makes B's IOP causal round-by-round knowledge sound with
`eps_i^k = eps_i`.

**Proof.** As Lemma K-A, word for word. `O_tr` is in `past(i)` for every challenge `i`, so `E` is well defined and
constant along a transcript. (b): by (iii) the premise `Pr > eps_i` never holds. (a): if `E` fails at every `i`,
(i) gives `State = 0` at the first challenge and (iv) final `State = 1`; by (ii) the first rise is at a verifier
message. ∎

## 3. How B meets the hypotheses

Take (revised 2026-11-19, M-A1, m-B1) `State = 1` iff `Dec(O_pre)` and `Dec(O_tr)` exist, **no verifier check
decidable so far has failed** (absorbing rule, as in Lemma K-A section 2: once a check run in the clear fails,
`State = 0` from then on), every pending claim of the outer protocol is true for the decoded words **and the
decrypted messages `m_i`**, and the opening is not doomed in S-4's sense. **The pending claims include each deferred
inner check**: every `assert_zero` equation that the wrapper defers on the `m_i` (`zk_wrapped_channel.rs`
`recv_one`, `assert_zero`) joins the list when its `c_i` arrives and stays there, true or false, until the wrapper's
MLE-check discharges it. A failed inner check therefore does not reject at once; it is a false pending claim, so
`State = 0` until the MLE-check, whose own error is in (iii).

1. **(i)** The initial pending claims are "the trace's AND, MUL, shift and public constraints hold" (`verify.rs`,
   the reductions' inputs), i.e. `(x, wit(Dec(O_tr))) in R_leaf` (resp. the node's main constraint system). For a
   node this makes `R_node` as stated in section 1, deferred claims included.
2. **(ii)** Every later oracle and message enters only through claims about the decoded words or the opening's
   state. For the leaf the key step is that the inner prover's messages are fixed by `Dec(O_pre)` and the
   ciphertexts: `m_i = c_i - k_i` is a function of the transcript once `O_pre` is in it, which it is before the
   first challenge. The ciphertext is still chosen adaptively, exactly as a clear message would be, so each inner
   reduction's round-by-round analysis applies to `m_i` at the time `c_i` arrives, although the inner verifier's
   checks are deferred into the wrapper's constraints (`zk_wrapped_channel.rs` `recv_one`, `assert_zero`): they are
   pending claims (above), so the inner analysis's "the check fails" case is "a false pending claim stays". The wrapper's own private and mask oracles are chosen after the inner challenges; they enter
   through the wrapper's claims (MLE-check, `lambda`, the oracle relations) whose truth the state tracks.
3. **(iii)** The census, per message, with merged challenges summed by [SG26] Lemma 5.2 (page 37). Each part's
   state is the one its cited bound is proved with: sumcheck and MLE-check rounds (the textbook state "the running
   claim is true"); the zerocheck points (2a.3 Lemma); the skip round; the ring switch (Theorem 1 of
   `binius-extension-challenges.md`, a state "the switched claim is true", refereed J1); the wrapper's blend
   (`zk-wi-soundness.md` Lemma 6); `mu`, `gamma`, the index and fold rounds and the query round (S-4, Lemma UD,
   whose states are read off the decoded oracle, as Lemma K-A requires).
4. **(iv)** The final checks: the wrapper's `assert_zero` of every deferred inner check, its MLE-check final, the
   opening's final fold value and query consistency. A doomed opening state is rejected except at the query round's
   error, which is in (iii).

**The node's batching transcript** (`pbatch.rs`) is not a part of B's IOP: its challenges come from the in-circuit
challenger over witness words, so for B's IOP they are witness, and `R_node` holds or fails with them fixed. What
the tree needs from them is that a compliant node whose children's deferred claims are false is unlikely; that is
Lemma R / Lemma P (errors at most `2^-249` a message) applied to the in-circuit transcript **as a hash-based
transcript under the one oracle**, i.e. under C2 and H-DS. TE' must name these rounds: either as further rounds of
the node's `J_V` (59 / 70 messages, T-1 `node-main-inner-*`, counted in `K` by their hash queries 236 / 280), or as a
separate reduction the extractor `E_T` runs at each node. Either way the cost is at most `70 N 2^-249`, negligible;
the wording is owed (K-B.3 below).

## 3a. Lemma LF: lifted oracles of unequal size (K-B.2, R-8)

**Provenance: Original (the Ycash developers, 2026), refereed-in-review.** Written by a referee, not by this
document's author: `zkq-te3-r8-referee.md` section 3 (commit `3cfd252`, 2026-11-19), reproduced here in substance
and **not yet independently read** by a second person. It relates to Ben-Sasson, Carmon, Ishai, Kopparty, Saraf,
*Proximity Gaps for Reed-Solomon Codes* ([BCIKS20], ePrint 2020/654, folder copy), Theorem 4.1 (correlated agreement
on lines, unique-decoding regime), which it lets the census apply to lifted words; the Gao-Mateer basis is as built
(`yugen-proof-b2` vendored binius64 `math/src/ntt/domain_context.rs` 170-193).

**Setting (as built).** A round oracle of message dimension `d - L` is encoded at rate `rho` over the prefix domain
`S_s = span(beta_0..beta_(k-1))` (`iop-prover/src/fri/encode.rs` 53-66) and committed at that size; the verifier
reads it as `Lift(c)[i] = c[i >> L]` over `S_b = span(beta_0..beta_(k+L-1))` (`iop/src/fri/batch.rs` 94-100); the
commitment-index rounds fold `lo + alpha (lo + hi)` of lifted words (`iop-prover/src/basefold/index_rounds.rs`);
FRI runs on `RS_b = RS[S_b, 2^d]`. Basis: `beta_0 = 1`, `beta_(i-1) = beta_i^2 + beta_i`; points `x_i = sum_j i_j
beta_j`; `q(X) = X^2 + X`, `W = q^L`, `RS_s = RS[S_s, 2^(d-L)]`.

**Lemma LF.** (1) `Lift(c) = c o W` on `S_b`, and `Lift` maps `RS_s` into `RS_b`. (2) `Lift` preserves relative
distance exactly. (3) For every word `u` on `S_s` and every `delta < (1 - rho)/2`: `Delta(Lift(u), RS_b) <= delta`
iff `Delta(u, RS_s) <= delta`, and the unique codeword of `RS_b` within `delta` of `Lift(u)` is `Lift(v)`, `v` the
one of `u`. The same holds for interleaved words with one agreement set.

*Proof (the referee's).* (1) `q` is `F_2`-linear, `q(beta_0) = 0`, `q(beta_i) = beta_(i-1)`, so `W(x_i) =
x_(i >> L)`; degree `< 2^(d-L)` composed with `W` gives degree `< 2^d`; `S_s = W(S_b)`. (2) Each point of `S_s` has
`2^L` preimages. (3) "If" by (1), (2). "Only if": let `w in RS_b` with polynomial `P` be within `delta` of
`Lift(u)`. For `a in U = ker W = span(beta_0..beta_(L-1))`, translation by `a` fixes `S_b`, `Lift(u)` and `RS_b`, so
`P(X + a)` is also within `delta`; unique decoding gives `P(X + a) = P(X)` on `S_b`, hence as polynomials (degree
`< 2^d < |S_b|`). Expand `P = sum_j r_j(X) W^j`, `deg r_j < 2^L`; each `r_j` is `U`-invariant, so `r_j - r_j(0)` has
`2^L` roots and degree `< 2^L`: `r_j` is constant. So `P = R(W)`, `deg R < 2^(d-L)`, `w = Lift(v)`, and
`Delta(u, v) = Delta(Lift(u), w)` by (2). Interleaved: row by row with one agreement set. ∎

*Consequence for K-B (iii) and the census.* [BCIKS20] Theorem 4.1 applied in `RS_b` to the lifted words gives
codewords on a common agreement set; by (3) each is the lift of an `RS_s` codeword of the committed word at the same
distance, and queries uniform on `S_b` are uniform on `S_s` after `>> L`. So the charge `(n + 2)/|K|` per
commitment-index round with `n` the largest codeword stands, and R-8 **moves no figure** in B's unique-decoding
regime. Outside unique decoding (the list regime, not used by B) nothing is claimed.

**Condition m-5 (owed by system B).** The sumcheck side needs the message of `Lift(Enc_s(g))` under `RS_b`'s
encoding to be `G↑` as `index_rounds.rs` defines it (novel basis: `X_j^(s) o W = X_(j << L)`). Honest lifted proofs
verify (vendored `iop/src/fri/common.rs` 724-937), which is evidence, not proof. **Task:** a direct encoding test in
`yugen-proof-b2`: encode a random small message on `S_s`, lift by `>> L`, and compare with `RS_b`'s encoding of the
embedded message, at every `L` the rows use. Until it passes, Lemma LF closes K-B.2 **conditionally on m-5**.

## 4. Status: what is owed for K-B to close

| | Item | Kind |
|---|---|---|
| K-B.1 | Refereed 2026-11-19 (`knowledge-and-census-referee.md`, pass with conditions M-A1, m-B1, m-B2, applied here); the re-read of this revision | review |
| K-B.2 | The lifted-oracle proximity statement (R-8; `b-round-census.md` 5): (iii) at the commitment-index round rests on it | **Lemma LF** (section 3a; Original, refereed-in-review: written by the referee of `zkq-te3-r8-referee.md`, not yet independently read); conditional on **m-5**, the direct encoding test owed by system B |
| K-B.3 | Theorem TE' to name the node's in-circuit batching rounds (section 3, last paragraph) | wording in `lemma-tree-extraction.md` |
| K-B.4 | The states of the ring switch, the univariate skip and the shift reduction written out against the code (I checked call sites and degrees only) | proof text from the cited statements |
| K-B.5 | The 127-versus-131 message grouping (`b-round-census.md` D-4) | count from T-1; cannot move a figure |

Nothing of a separate "knowledge" kind remains beyond these: as for K-A, the extractor is decoding of the first
oracle, and the knowledge errors are the soundness errors of the census.

## 5. Provenance

Lemma K-B: **Original (the Ycash developers, 2026)**, the same argument as Lemma K-A (`theorem-s-referee.md` 4,
Original, draft) transposed to B; new here: the two-oracle setting and step 2 (decryption by the precommit keys
under the zero-knowledge wrapper). Uses [SG26] Definition 2.20, Lemma 5.2 (Published, pages 14, 37), the
Berlekamp-Welch extractor of Diamond, ePrint 2025/1015, Theorem 4.2 (proof sketch, page 5) and Diamond-Posen,
ePrint 2024/504 (Algorithm 1 as [Dia25] cites it; not re-read). Sources consulted before the label: those, and
[SG26] Lemma 2.21 and Appendix A (page 96, the equivalence with [CMS19] Definition 8.5); none states a lemma for an
encrypted-message wrapper.

## 6. Revision 2026-11-19 (after `knowledge-and-census-referee.md`: PASS WITH CONDITIONS)

- **M-A1**: the absorbing rule added to `State` (section 3). **m-B1**: the deferred `assert_zero` equations on the
  `m_i` are listed as pending claims. **m-B2**: `State(x, tr)` reads the decodings of every oracle in the past.
- Each step re-checked: the proof of section 2 is unchanged (it is Lemma K-A's, whose re-check found no step needing
  more than the definition change); section 3 (i) unchanged; (ii) unchanged in substance, step 2 now says that a
  failing deferred inner check is a false pending claim rather than a rejection; (iii) unchanged (the MLE-check's
  error already covers discharging false deferred claims); (iv) unchanged. No step needed more than the definition
  change and m-B1's listing.
- Open as before: K-B.2 (R-8, lifted oracles), K-B.3, K-B.4, K-B.5.
- *Addendum 2026-11-19 (`zkq-te3-r8-referee.md` R-8):* K-B.2 has a proof, Lemma LF (section 3a), written by that
  referee; status **refereed-in-review** (not yet independently read), conditional on m-5 (B's direct encoding
  test). No figure moves.
