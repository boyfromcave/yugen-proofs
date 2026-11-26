# Referee report: zk-quantum.md revision 2 (Theorem 6.6 (3), (4), Theorem ZP), Lemma TE.3 and Corollary TE-X-Q, and R-8

Part of Yugen. Independent referee, 2026-11-19, against `yugen-proofs` head `a18d4f6`. Code read
read-only: `yugen-proof-a` (vendored leanMultisig `crates/verifier/src/params.rs`, `guests/bundle_merge_e2.py`),
`yugen-proof-b2` (`src/prove.rs`, `src/stamp.rs`, `src/uroot.rs`, `src/bundle.rs`, vendored binius64
`iop/src/fri/{batch,common}.rs`, `iop/src/basefold/{layout,channel}.rs`, `iop-prover/src/fri/encode.rs`,
`iop-prover/src/basefold/index_rounds.rs`, `math/src/ntt/domain_context.rs`). Source: [SG26] ePrint 2026/2615,
rendered with pypdfium2: Section 6.2 and Protocol 6.5 (p. 57), Section 6.3 and Theorem 6.6 (pp. 58-59), Definition
H.6 (p. 129), Section I.1 with Definition I.1 (pp. 130-131), Protocol I.4 and Theorem I.5 (p. 133). No test was run.

## Verdicts

| Item | Verdict |
|---|---|
| 1. `zk-quantum.md` rev 2/2.1: Theorem 6.6 (3), (4) applied; Theorem ZP | **PASS WITH CONDITIONS** (M-1, M-2; `eps_hvzk` open as the document says) |
| 2a. Lemma TE.3 | **PASS WITH CONDITIONS** (M-3) |
| 2b. Corollary TE-X-Q | **PASS as a sketch** (correctly labelled; what is owed listed in section 2) |
| 3. R-8 | **Proven here in the regime B uses (Lemma LF, Original, draft)**, conditional on one identity evidenced by completeness and owed a direct test (m-5). It cannot affect soundness beyond the census charge. |

## 1. Theorem 6.6 (3), (4) and Theorem ZP

**Checked against the rendered theorem.** The quoted bounds of Theorem 6.6 (3) (QROM and ROM) and (4) are verbatim
(p. 59). Definition I.1's `eps_leaf = (1/2) sqrt(2^(8b)/2^(8 b_l)) + sqrt(ln N_leaf / (2 * 2^(8 b_l)))`, `N_leaf`
the byte strings of length at most `L_leaf`, is copied correctly; `q_S = 2 n_pos + N_msg + n_B` (the document drops
`n_B`, zero without merges: NOTE). Definition H.6 is adaptive and multi-theorem as stated. Protocol I.4 "assigns only
stream points, one per verifier message" (p. 133): Theorem ZP's separation argument (A's simulator touches only tag
`0x13` inputs, B's only `0x23`) holds. Hybrids 1 and 2 of ZP are right: the reductions are `(t', Q)`-adversaries of
Definition 6.1 with `t'` as stated; B and node proofs computed after the last proof query are uncounted, as the
definition allows. Arithmetic re-done: `eps_leaf(64 B) = 2^-129.0`; `n_pos eps_leaf` = `2^-107.8` (A), `2^-105.75`
(B); `eps_key = 2^-236.5`; sums `2^-105.4`, `2^-89.4`, `2^-85.4`; `4Qt/2^256 = 2^-169.9` at `t = 2^64.1`. All agree.

**Hypotheses as built.** Salting (per-leaf, independent, `b_l > b`): met by both systems (A 8 words; B 512 bits on
both round oracles and every fold tree, route S, `7de8da0`; not re-read here). De-duplicated positions: Section I.1
requires exactly one salted leaf per position; `qrom-compilation.md` 2 specifies it. Not met as built: the
series-parallel transcript with proof salt and write-back (T-1, T-2, `qrom-compilation.md` H6 "not as built").
`eps_hvzk`: open (Z-A1..Z-B5).

**The quantum ZK bound at the project's parameters** (`decision-security-profile.md` 2.1: target `2^-128` over
`Q = 2^37` leaf proofs, excluding `Q eps_hvzk`; leaf salts A 80 B, B 96 B, proof salt 80 B), `t = 2^128`:

| | A (`b_l = 80`) | B (`b_l = 96`) | ZP |
|---|---|---|---|
| `Q n_pos eps_leaf` | `2^(37+21.17-193) = 2^-134.8` | `2^(37+23.25-257) = 2^-196.7` | |
| `4Qt / 2^(4 b_s)`, `b_s = 80` | `2^-153` | `2^-153` | |
| `Q eps_key` | `2^-199.5` | `2^-199.5` | |
| `eps_zk(2^128, 2^37)` | **`2^-134.8`** + `2^37 eps_hvzk^A` | **`2^-153.0`** + `2^37 eps_hvzk^B` | **`2^-134.8`** + `2^37 (eps_hvzk^A + eps_hvzk^B)` |
| `eps_wi` (Thm 6.6 (4), `L = 2^24`) | `2^-133.8` + `2^38 eps_hvzk^A` | `2^-195.7` + ... | **`2^-133.8`** + `2^38 (...)` |

**Meets the target** (`2^-128`) in both forms, excluding the `eps_hvzk` terms, which no document yet bounds. At
the document's own parameters (64/64/64 B, `Q = 2^20`) it does **not** (`2^-85.4`).

### Findings

- **M-1 (MAJOR), `zk-quantum.md` 0 (D-b), 3.2, 3.3, 3.4, 7.** Every figure is at 64-byte salts and `Q = 2^20`, which
  the security profile has withdrawn ("`Q` corrected from `POOL_LOG2 = 20`, which Theorem 6.6 (3) does not permit for
  a permanent record"); the pool figure `2^-85.4` fails the privacy target. *Fix:* a dated amendment restating D-b as
  the profile's 80 / 96 / 80 B, the tables at `Q = 2^37`, `t = 2^128` as above, and Z-1's acceptance at those
  lengths; keep the 64-byte rows as record.
- **M-2 (MAJOR, condition), 3.1 table row 1.** The theorem needs the spBCS transcript; as built neither system has it
  (T-1, T-2). The table says so; the summary and `what-is-proven.md` must not present Theorem 6.6 (3) as applying to
  the built code. *Fix:* state "applies after T-1 / T-2" in the status line and the review sheet item 4.
- **m-1 (MINOR), 3.1.** `L_leaf = 512` is not the maximum leaf encoding: A's level-0 leaf is 16-byte tag + 512-byte
  row; B's BLAKE3 leaf framing allows up to 1,024 bytes (`qrom-compilation.md` B-4). The second term of `eps_leaf`
  moves from `2^-250.8` to about `2^-250.3` at 64 B (negligible at any salt length). *Fix:* use the largest leaf.
- **m-2 (MINOR), 3.3 Theorem ZP.** The two systems use different functions (Keccak-256/SHAKE256; SHA-256/BLAKE3).
  ZP needs all of them modelled as **one** random oracle with disjoint parts (or independent oracles); MA-1 and MA-2
  are stated per system. *Fix:* add the joint assumption (MA-0) to the hypotheses of ZP.
- **N-1 (NOTE).** `q_S` omits `n_B`; harmless without merges, which the transcripts may use (I.1). State it.
- **N-2 (NOTE).** "Everlasting" bounds only queries before the **last** proof. For a record growing for 50 years
  that is the adversary's whole budget until then; `t = 2^128` is the right reading, and 3.4 (no query bound) is
  the fallback. Say so in 3.3.

## 2. Lemma TE.3 and Corollary TE-X-Q

**The digest functions.** A: `bind_iv` (`params.rs` 460) is `Keccak("leanvm-params-v1" || program IV ||
descriptor())`, with `descriptor()` every row field including `leaf_salt_words` and the query table, **except row 0,
which returns the program IV unbound**; the node's public input is `merge_statement`, `keccak_cells(seeds ||
D || three deferred claims)` (`bundle_merge_e2.py`), over `D = H_bundle-node(d | mode | LE16(k) |
Hvar_bundle-kids(D_1..D_k) | 0^32 | LE32(proofs))`. B: `StatementId` (circuit name, `cs_digest` = SHA-256 of the
serialized constraint system, zk flags, `Row`), for stamped systems `key_digest` / `key_digest_padded` (SHA-256 over
label, slot and main digests, `K`, pad), nodes via `uroot::statement_id(key, rate)`; `H_bundle-node` as `framed(id::
BUNDLE_NODE, ..)` natively and `node_digest` in-circuit (`bundle.rs` 96, 298). The document names the right families.

**TE.3's proof, part (a).** The step "the shape cells of `x_c` contradict those `w_v` claims" assumes `x_c` exposes
its cells. It does not: in A, `x_c`'s public input is the `merge_statement` hash, and `D_c` sits two hash layers
below it; in B the node's public words carry `D_c`, not its preimage. The cells of `c` become available only from
`w_c`, after `c` is extracted. **M-3 (MAJOR), section 3 step 3 and Lemma TE.3 (a).** *Fix (buildable, no new
assumption):* move the shape check to the processing of `c`: after `w_c` is extracted and `(x_c, w_c) in R`,
compare the cells `w_c` hashes into its own statement with those `w_v` claimed; if they differ while both yield the
public input `x_c` names, the two preimage chains (`H_bundle-node`, then for A `merge_statement`; and
`Hvar_bundle-kids` one level up) differ and have equal outputs, so the first layer at which they differ is a
collision (hash-chain argument). List `merge_statement`'s Keccak and `Hvar_bundle-kids` in H-BIND. The node count
then reaches at most `N + 16` before the stop (a node is queued before its cells are checked): `K <= (N + 16)
k_q,max`, which moves no figure. Part (b) is right: with agreeing cells the proof counts add and the root's is at
most `N`. One more case belongs in (b): the root's count is checked by `Tree::check` on the header the chain holds,
a third preimage of the root's digest; a disagreement there is the same collision.
- **N-3 (NOTE).** A's row 0 binds nothing beyond the program IV; H-DS for any tree node under row 0 rests on the
  program IV alone. Rows 6-9 are the tree's, so no gap as built; record it.

**Corollary TE-X-Q: what is proven and what is a sketch.** Proven (given [SG26] Theorem I.16 (1) as published):
the per-proof QROM figures; the form of the bound (`2 sqrt(K/2^n)` and `6 (t+K)^2 (eps_max + c'_max (t+K)/2^(8b))`
match I.16 (1) with `k_q` replaced by `K`); that no continuation after the measurement occurs when every proof is
published and verified first, so no Lemma QC term and no C2; that SHAPE-VIOLATION is separately `eps_bind` (with M-3
applied, the collision finder measures the compressed oracle, runs the database algorithms and outputs a collision of
a concrete function; correct). **Sketch (owed):** (i) the joint bad set `B*` of Lemma TE.1 stated as a database
property with the per-query flip bound that [CMS19] Lemmas 5.9, 5.10 (via [SG26] Lemma I.15) consume, across nodes
of two systems on one database; (ii) Lemma TE.2 for the database measured once, i.e. that each node's database
algorithm applied to the one measured database extracts as in the single-proof proof; (iii) the instability count
with `T = t + K` in place of `t + k_q`. Label correct; no figure rests on it alone.

## 3. R-8: lifted oracles of unequal size

**The obligation, from the code.** A round oracle of message dimension `d - L` is encoded at rate `rho` over the
Gao-Mateer prefix domain `S_s = span(beta_0..beta_(k-1))` (`encode.rs` 53-66) and committed at that size. The
verifier reads it as the virtual word `Lift(c)[i] = c[i >> L]` over `S_b = span(beta_0..beta_(k+L-1))` (`batch.rs`
94-100), and the commitment-index rounds fold `lo + alpha (lo + hi)` of lifted words (`index_rounds.rs`), then
FRI runs on `RS_b = RS[S_b, 2^d]`. The census charges `(n + 2)/|K|` per index round with `n = |S_b|` (BCIKS20
Theorem 4.1 on lines, unique decoding: query bound `((1 + rho)/2)^192`, `b-round-census.md` row 131). Owed: that a
correlated agreement in `RS_b` for lifted words yields codewords of `RS_s` for the committed words at the same
distance.

**Lemma LF (Original, the Ycash developers, 2026; draft).** Let the basis be Gao-Mateer (`beta_0 = 1`,
`beta_(i-1) = beta_i^2 + beta_i`; `domain_context.rs` 170-193) and points indexed `x_i = sum_j i_j beta_j`. Let
`q(X) = X^2 + X`, `W = q^L`. Then: (1) `Lift(c) = c o W` on `S_b`, and `Lift` maps `RS_s = RS[S_s, 2^(d-L)]`
into `RS_b`. (2) `Lift` preserves relative distance exactly. (3) For every word `u` on `S_s` and every
`delta < (1 - rho)/2`: `Delta(Lift(u), RS_b) <= delta` iff `Delta(u, RS_s) <= delta`, and the unique codeword of
`RS_b` within `delta` of `Lift(u)` is `Lift(v)`, `v` the one of `u`. The same holds for interleaved words.

*Proof.* (1) `q` is `F_2`-linear with `q(beta_0) = 0`, `q(beta_i) = beta_(i-1)`, so `q^L(x_i) = x_(i >> L)`; `p` of
degree `< 2^(d-L)` gives `p o W` of degree `< 2^d`; `S_s = W(S_b)`. (2) each position of `S_s` has `2^L` preimages.
(3) "If": by (1), (2). "Only if": let `w in RS_b`, polynomial `P`, with `Delta(Lift(u), w) <= delta`. For `a in U =
ker W = span(beta_0..beta_(L-1))`, translation by `a` maps `S_b` to itself, fixes `Lift(u)` (`W(x + a) = W(x)`) and
maps `RS_b` to itself, so `w_a(x) = P(x + a)` is also within `delta`; unique decoding gives `w_a = w`. Then `P(X + a)
- P(X)` has degree `< 2^d < |S_b|` and vanishes on `S_b`, so `P(X + a) = P(X)` for all `a in U`. Write `P = sum_j
r_j(X) W^j`, `deg r_j < 2^L` (unique `W`-adic expansion); `W` is `U`-invariant, so each `r_j` is, and a polynomial of
degree `< |U|` taking one value on `U`'s cosets' points `X, X + a` is constant (`r_j - r_j(0)` has `2^L` roots on
`U`). So `P = R(W)`, `deg R < 2^(d-L)`, `w = Lift(v)` with `v = R` on `S_s`, and `Delta(u, v) = Delta(Lift(u), w)` by
(2). Interleaved: apply to each row, with one agreement set. ∎

*Consequence.* BCIKS20 Theorem 4.1 applied in `RS_b` to the lifted words (arbitrary words of `S_b`, so the theorem
applies as stated) gives codewords on a common agreement set; by (3) each is the lift of an `RS_s` codeword of the
committed word, at the same distance. Queries uniform on `S_b` are uniform on `S_s` after `>> L`. So the charge
`(n + 2)/|K|` with `n` the largest codeword is justified and **R-8 cannot move a figure** in B's unique-decoding
regime. Outside unique decoding (list regime, not used by B) Lemma LF (3) is not claimed.

- **m-5 (MINOR, the condition).** The sumcheck side needs the message of `Lift(Enc_s(g))` under `RS_b`'s encoding to
  be `G↑` as `index_rounds.rs` defines it (novel basis: `X_j^(s) o W = X_(j << L)`, which follows from `W_i = q^i`
  in the Gao-Mateer basis). Honest lifted proofs verify (`common.rs` 724-937 exercise lifting), which is evidence,
  not proof. *Fix:* a test that encodes a random small message, lifts by `>> L`, and compares with `RS_b`'s encoding
  of the embedded message, at every `L` the rows use; and Lemma LF written into `lemma-k-b.md` K-B.2.

## Not checked

The HVZK documents (another referee). Route S's code (`7de8da0`) beyond the citations. Whether T-1, T-2, Z-1 are
built. `n_pos` values (taken from `soundness` revision 6). [SG26] Theorem I.16 (1)'s proof and Lemmas I.12-I.15.
The novel-basis identity of m-5 at the bit level, and the B index-to-point convention beyond the code comments
(`encode.rs` "prefix of the longer's"). C-4 (node circuits' shape checks). No test or calculator run.
