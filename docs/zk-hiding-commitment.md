# Hiding commitments and hiding openings over binary additive codes

Part of Yugen. This document states the polynomial commitment and opening protocols
of the two leaf proof systems at the level the zero-knowledge argument needs, constructs their
hiding versions in characteristic 2, proves honest-verifier zero knowledge of the algebraic view,
and records what was checked by exact computation in `../zk-commit/`. The masked sumcheck is
`zk-masked-sumcheck.md` (cited as "the lemma document"); the whole leaf proof and the
Fiat-Shamir step are `zk-composition.md`.

Status tags, as in the lemma document:

| Tag | Meaning |
|---|---|
| **(P)** | proven in this document, pen and paper |
| **(C)** | checked by exact computation in `zk-commit/` (sizes stated with the claim) |
| **(S)** | read in a primary source, named with the claim |
| **(M)** | from memory, or read only in an abstract or a secondary description: not verified |
| **(U)** | unproven, open |

Result in one paragraph. A Reed-Solomon code over an additive (subspace) domain with `t` uniform
coefficients appended to each lane hides any `t` opened rows **only if the evaluation domain is a
coset that avoids the zero set of the randomness' basis polynomial**; on the linear subspace the
pinned stacks use, every opened row inside that zero set (a fraction equal to the rate) is a
function of the witness alone (P, C). With a coset domain, salted leaves, one claim-level mask
per fold batch, a randomness budget of (queries + out-of-domain samples) per lane and per oracle,
and a one-time-padded final message checked on one extra committed column, the WHIR-style opening
is perfect honest-verifier zero-knowledge in its algebraic view: the view is uniform on the set of
accepting views (P; C on five toy instances, all with rank equal to the accepting dimension, and
one instance enumerated in full). In this construction (W-I) every auxiliary secret rides inside
the main oracles, so the hiding costs about 12 to 15 KiB on the leaf instead of the several small
mask oracles of the layout the pinned prime-field code implements. For codewords folded without
re-randomisation (FRI-Binius, BaseFold) the exact budget is `T >= Q * 2^K` uniform coefficients,
`K` the total fold depth of the committed oracles (P, C). Section 3.4 compares the construction
with ePrint 2026/391 as published (revision of 2026-11-16, read in the citation audit): the
dependences on odd characteristic and on a multiplicative domain that this document found are
properties of the pinned Plonky3 code, which implements an earlier version; the paper as
published covers binary fields, and its layout is the in-oracle layout of W-I (section 3.4).
is proven in the unique-decoding regime in `zk-wi-soundness.md` ("the soundness document"), which
also corrects the aux layout for system A (finding F-1, section 6.1 below). Decision of the lead
architect (2026-11-19): **system A uses W-I; system B uses W-M** (section 7, the unmodified opening
on `rho p + m`), so that the two hiding openings are independent for soundness.

Provenance (citation audit of 2026-11-19; `../REFERENCES.md`). Published and used: the salted
Merkle tree (ePrint 2016/116, Section 3.2); the base case (ePrint 2026/391, Construction 7.2);
the hiding of a high-offset pad on a disjoint coset (ePrint 2025/1015, Lemma 4.4). Adapted: W-M
from ePrint 2025/1015, Construction 4.1; W-I's in-oracle layout coincides with ePrint 2026/391,
Section 11. Original (the Ycash developers, 2026) as far as checked: Lemma E beyond Lemma 4.4
(necessity, alignment, lanes), Lemma O, Lemmas L and T, Theorem 1', Lemma S, Lemma F, Theorems W
and W-A as proofs for the two pinned stacks. Each is labelled where it is stated or in
`REFERENCES.md` Part 3.

---

## 1. The protocols in question

### 1.1 Additive domains and the novel basis

`F = GF(2^k)` is the challenge field; the committed alphabet `K` is `F` or a subfield (B commits
bits packed into `GF(2^64)` words, A commits `GF(2^64)` cells; S: `binary-pcs/src/whir/domain.rs`,
leanVM `crates/verifier/src/whir.rs`). Fix `F_2`-independent `b_0, b_1, ..` in `K`
(Cantor basis in B, powers of `x` in A; S, same files). `U_i = span(b_0..b_{i-1})`.

    W_i(x)    = prod_{u in U_i} (x + u)          F_2-linear, degree 2^i, zero set U_i
    What_i(x) = W_i(x) / W_i(b_i)
    X_c(x)    = prod_{i : bit i of c set} What_i(x)        novel basis, deg X_c = c

A polynomial with coefficient vector `p` is `P(x) = sum_c p_c X_c(x)`. Its value at `x` is the
multilinear extension of `p` at the point `(What_0(x), What_1(x), ..)` (S: `query_point` in
`binary-pcs/src/whir/domain.rs`; leanVM `novel_eval`). The domain of size `N = 2^l` is
`S_l = U_l`, indexed by `j -> sum_{bit i of j} b_i`: **a linear subspace, containing 0, whose
first `2^mu` points are `U_mu`** (S, both stacks; B's fold module states `domain_point(0) = 0`
implicitly through `W_1(domain_point(i)) = domain_point(i >> 1)`).

Folding identity (S: `binary-pcs/src/fold.rs` module text; C: `test_fold.py`, 200 random
checks): with `q(x) = x (x + b_0)`,

    P(x) = P_0(q(x)) + (x / b_0) P_1(q(x)),     P_b has coefficients p_{b + 2j} in the novel basis of q(S)

so the pair `(P(x), P(x + b_0))` and the pair `(P_0(y), P_1(y))`, `y = q(x)`, determine each other
by a public invertible map. Iterating: a coset of size `2^kappa` of a codeword is equivalent to
one **row** of the `2^kappa`-interleaved code whose **lanes** are the polynomials `P_b`,
`b in {0,1}^kappa`, with coefficients `p_{b + 2^kappa j}`. Both presentations are used below; all
statements are made for rows of lanes.

### 1.2 Commitment

Message `p in K^(2^n)` (the stacked witness). Oracle: `2^kappa` lanes of `M = 2^(n - kappa)`
coefficients each, evaluated on a domain of `N = M / rate` points. Leaf `y` holds the row
`(lane_b(y))_b`. The commitment is the root of a binary Keccak Merkle tree over the leaves. No
salt, no randomness in either pinned binary stack (S for B: `docs/architecture.md` and the
framework selection; S for A: none in `crates/verifier`).

### 1.3 WHIR-style opening (the leaf of both systems)

Claim: `<p, W> = v` for a public weight `W` (batched evaluation claims). Levels `i = 0..L-1`;
level `i` has an oracle with `2^kappa_i` lanes and performs `kappa_i` fold rounds.

Generic form (S: `whir/src/pcs/prover/mod.rs`, `whir/src/pcs/zk/mod.rs` of the pinned Plonky3,
which B instantiates with `BinaryWhirDomain`; prefix-interleaved oracles, fold of a row by
`eq(., gamma)`):

    level i:
      kappa_i sumcheck rounds on  sum_b sum_j p[b][j] W[b][j]  over the lane index b:
          prover sends the round polynomial (degree 2), verifier sends gamma.
          After the batch:  p' = sum_b eq(gamma, b) p[b][.],  W' likewise,  claim <p', W'> = T.
      not the last level:
          prover commits oracle i+1: the lanes of p' at a lower rate;
          verifier sends out-of-domain points (none under unique decoding), prover answers p'(rho);
          verifier opens Q_i rows of oracle i; each row folds to p'(y_q) = sum_b eq(gamma, b) row[b];
          the answers are added to the claim with powers of a batching challenge, and the
          evaluation weights (X_j(rho))_j, (X_j(y_q))_j to W'.
      last level:
          prover sends p' in clear (2^9 to 2^12 coefficients in the design basis);
          verifier opens Q rows of the last oracle, checks each fold against p', and checks
          <p', W'> = T.

System A's variant (S: leanVM `crates/verifier/src/whir.rs`, `verify_whir`): a fold round sends
four scalars `(u0, w, c0, c1)`, the verifier draws `(alpha, beta)` and sets
`claim' = u0 + beta c0 + alpha (u0 + claim + alpha w + beta (c0 + c1))`; lanes fold in pairs by
the affine combiner `G + (alpha + beta X) F`, which raises the degree by one per round. A
non-final level commits the folded lane's low `2^mu` coefficients, **sends the `kappa` high
coefficients in clear**, reads one out-of-domain claim, and opens rows, each "folded as the lanes
were and corrected by the high part". The final level sends the whole folded lane
(`2^mu + kappa` coefficients) and closes with a degree-3 sumcheck over the low part. Domains are
linear subspaces (`x = K(query)`).

Schedules (design basis, category 1, rate 1/4 at level 0; later rates from
`design.whir_schedule`: the rate exponent grows by `k - 1` per level): A `n = 24`, folds 5/3/3/3,
rates `2^-2, 2^-6, 2^-8, 2^-10`, queries 171/119/117/116, final `2^10`; B `n = 19`, folds 5/4,
rates `2^-2, 2^-6`, queries 171/119, final `2^10` (per-proof target; the tree-wide design basis is
in `design-basis.md` section 2a).

**Amendment 2026-11-19 (`zk-referee.md` R-6).** The schedules above are the old design-basis examples, kept because
the worked examples of sections 1.3 and 8 use them. The rows as built now have **A: queries 234/166/169/186** and
**B: 184 to 192 queries at rate 1/8 on BaseFold** (FRI-Binius / BaseFold folding, section 1.4, not WHIR `n = 19` with
folds 5/4); B's leaf hides with the full-length mask `omega` of D25 Construction 4.1 and salts every tree as built
(`yugen-proof-b2` `7de8da0`, `zk-quantum.md` amendment of 2026-11-19). The hiding statements do not depend on the
example counts: A's code sizes its randomness `t = Q` per level from the row (`yugen-proof-a` `verifier/src/wi.rs`
64-85, as `zk-referee.md` R-6 cites it), so coverage holds at the raised counts by construction. Section 8 is
restated at A's current counts where the figure is a direct function of them. Under unique decoding no out-of-domain samples are taken (S:
`whir/src/parameters/whir.rs`, "UniqueDecoding needs no out-of-domain samples"); leanVM at its own
(Johnson) parameters reads one per commitment.

### 1.4 Folding opening (FRI-Binius / BaseFold; B's recursion layers)

(S: `binary-pcs/src/pcs.rs`, `fold.rs`.) One committed codeword of `P` on `S_l`. A sumcheck on
`sum_x p(x) W(x)` over all `n` variables runs "in lockstep" with the codeword: after each round's
challenge `gamma` the codeword is folded, `fold(P)(q(x)) = (1 + gamma) P_0 + gamma P_1`, i.e.
coefficients `p'_j = (1 + gamma) p_{2j} + gamma p_{2j+1}`. Every `k` rounds the folded codeword is
committed. The last codeword (a constant, or a short polynomial) is sent in clear. Each of `Q`
queries opens one coset in every committed oracle along its path and checks the folds and the
final message. **The folded oracles are deterministic functions of the first codeword and the
challenges: no fresh randomness can enter them.**

### 1.5 What the verifier sees, and from which secrets

| View element | Function of |
|---|---|
| Merkle roots, sibling digests | every leaf (hash) |
| sumcheck / fold-round messages | linear in the current polynomial, given the challenges |
| out-of-domain answers | linear in the folded polynomial |
| opened rows | linear in the lanes of that oracle |
| high part (A), final message | linear in the folded polynomial: `2^10` or more functionals of the witness |

Every algebraic element is an `F`-linear function of the witness once the challenges are fixed.
Hiding therefore reduces to linear algebra over `F` (section 2) plus the hash (section 4).

---

## 2. Method: affine views

**Lemma L (affine views) (P).** Fix the verifier's challenges `chi`. Suppose the algebraic view is
`view = a0(chi) + A(chi) w + B(chi) z` with `w` the witness and `z` the prover's randomness,
uniform. Then the view is uniform on the coset `a0 + A w + Im B`. Two witnesses have identically
distributed views if and only if `A (w - w') in Im B`. If moreover `Im B` is the whole direction
space of the affine set `Acc(chi)` of views the verifier accepts, the view is uniform on
`Acc(chi)` for every witness with the public claim, and a simulator samples `Acc(chi)` uniformly.

*Proof.* A linear map sends the uniform distribution to the uniform distribution on its image;
cosets of `Im B` are equal or disjoint. Honest views are accepted, so the coset lies in `Acc`. ∎

**Lemma T (triangular pads) (P).** Let the view be blocks `v_1..v_m` and the randomness be
independent uniform blocks `z_1..z_m` with

    v_i = Phi_i(w, z_1, .., z_{i-1}; chi) + B_i(chi) z_i ,

`Phi_i` arbitrary, and suppose that for every `w` and `z` the block `v_i` lies in an affine space
`c_i(v_1..v_{i-1}; chi) + I_i(chi)` with `I_i = Im B_i`, where `c_i` is a public function. Then
the view is distributed as: `v_i` uniform on `c_i(v_{<i}; chi) + I_i`, for `i = 1..m` in turn. In
particular it does not depend on `w`, and the sequential sampler is a simulator.

*Proof.* Induction on `i`. Condition on `z_{<i}`; this fixes `v_{<i}` and `Phi_i`. Then
`v_i = Phi_i + B_i z_i` is uniform on the coset `Phi_i + I_i`, which contains `v_i` and therefore
equals `c_i(v_{<i}) + I_i`. The conditional law depends on `z_{<i}` only through `v_{<i}`. ∎

`z_i` may appear in later blocks (inside `Phi_j`, `j > i`); it must not appear in earlier ones.
The order is a proof device and need not be the order of the protocol. Every zero-knowledge proof
below is a table that assigns to each view block its pad `z_i` and its space `c_i + I_i`.

Tests use Lemma L directly: the honest prover is run on affine forms (`zk-commit/ff.py`), which
yields `A` and `B` exactly; the test compares `rank B` with `rank [A dirs | B]` and with
`dim Acc`. `test_code.py`, `test_fold.py` and `test_basecase.py` also enumerate every randomness
value and compare count tables; the two methods agree in every case (C).

---

## 3. The zero-knowledge encoding on an additive domain

### 3.1 Statement

Each lane has coefficient slots

    [0, m)             message (anything linear in the witness and in other randomness)
    [aoff, aoff + t)   t fresh uniform coefficients          aoff >= m, zeros in between

with `aoff` **aligned**: a multiple of `2^ceil(log2 t)`. The lane is evaluated on
`D = beta + S_l`. Let `top` be the highest set bit of `aoff`.

**Lemma E (P; C).** Let `Q` be a set of rows.

1. If `D` does not meet `U_top` and `|Q| <= t`, the opened rows `(lane_b(y))_{b, y in Q}` are
   uniform in `F^(lanes x |Q|)` (in `K` if message and randomness are in `K`) and independent of
   the message.
2. If `y in Q` lies in `U_top`, row `y` equals the message polynomials at `y`: a function of the
   message alone, whatever `t` is.
3. If `|Q| > t` the rows are not independent of the message (when `m >= 1`).

`D cap U_top` is empty exactly when `beta` is outside `S_l` (for `aoff < 2^l`). On the linear
domain (`beta = 0`), `U_top` is the first `2^top` rows: for `aoff = M = 2^mu` that is a fraction
`rate` of all rows.

*Proof.* For `s < t <= 2^a` and `aoff` a multiple of `2^a`, the bits of `s` and of `aoff` are
disjoint, so `X_{aoff + s} = X_aoff * X_s`. The randomness contributes
`X_aoff(y) * R_b(y)`, `R_b = sum_s r_{b,s} X_s`, a uniform polynomial of degree below `t` (the
`X_s`, `s < t`, are a triangular basis of that space). `X_aoff(y) = prod What_i(y)` over the bits
of `aoff`, zero iff `y in U_top`. (1) For `|Q| <= t` distinct points outside `U_top`, evaluation
of `R_b` at `Q` is onto `F^|Q|` and each value is scaled by a nonzero constant; lanes are
independent. Apply Lemma L. (2) `X_aoff(y) = 0`. (3) `t` coefficients cannot make `t + 1` values
uniform, and the message part at `t + 1` points has rank `min(m + t, t + 1) > t` together with
the randomness. ∎

Computation (C, `results/code.txt`): for six shapes over GF(16) and GF(256) (`|D| = 8, 16, 32`,
1 to 4 lanes, `t = 2..4`), **every** set of at most `t` rows: coset domain, hiding in all 4,564
sets; linear domain, leaking in exactly the sets that meet `U_top` (3,677 predicted, 3,677
found); sets of `t + 1` rows leak in all 3,452 tried. Enumeration over GF(8): for every set of
rows and two messages, the distributions are equal exactly when the rank criterion says so.
Alignment: with `aoff = 6`, `t = 4` (not aligned) 4 of 1,820 sets of 4 rows leak on a coset
domain; aligned offsets leak in none.

### 3.2 Folding preserves the structure

Fold of a row by `eq(., gamma)`: `sum_b eq(gamma, b) lane_b(y)` is the value at `y` of the
polynomial with coefficients `sum_b eq(gamma, b) p[b][.]`: message `Fold(msg)` in `[0, m)`,
**excess** `e = Fold(r, gamma)` in `[aoff, aoff + t)` (P. Published for the eq-fold: Chiesa, Fenzi,
Weissenberg, ePrint 2026/391, revision of 2026-11-16, Claim 2.8 and Lemma 3.34, "encode then fold
equals fold then encode" with folded randomness; the pinned `whir/src/pcs/zk/committer.rs` cites
it as "Lemma 3.26" of an earlier version, a number that is a different statement in the revision
read). The verifier computes the fold
from the opened row, so a folded value is not a further functional of the secrets.

For A's affine combiner `G + (alpha + beta X) F` (P, from the multiplication rule quoted in the
pinned tests, `X X_c = sum_{j<t} A_j X_(c with bits below j cleared) + A_t X_(c+1)`; not tested):
multiplication by `X` maps slot `c` to slots at most `c + 1` and never moves a slot at or above
`aoff` below `aoff` while `aoff + t + kappa <= 2 aoff`. So the folded lane is: message part in
`[0, m + kappa)`, excess in `[aoff, aoff + t + kappa)`. The alignment must leave `kappa` free
slots above the randomness.

### 3.3 Out-of-domain samples

An out-of-domain answer on the folded polynomial `P'` of oracle `i` is one more evaluation of
`P'`, at `rho`. **Lemma O (P; C inside `test_whir.py`).** If `t_i >= Q_i + o_i` and the `o_i`
out-of-domain points are pairwise distinct and outside the ambient subspace `span(S_l, beta)`,
the `Q_i` opened rows and the `o_i` answers are jointly uniform. *Proof.* The functionals on
`r_i` are `e_b (x) ev(y_q)` (rows) and `eq(gamma) (x) ev(rho_k)` (answers); `eq(gamma, .)` is
never the zero vector (its entries sum to 1), the `Q_i + o_i` points are distinct with
`X_aoff != 0`, and `t_i >= Q_i + o_i` makes their evaluation functionals independent. ∎ No
separate pad is needed: the budget rule is `t = queries + out-of-domain samples`.

### 3.4 The construction of 2026/391 as published, against the pinned code and against W-I

Corrected by the citation audit of 2026-11-19. Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs
for Constrained Interleaved Codes", ePrint 2026/391, was read in its revision of 2026-11-16. The
pinned Plonky3 (`whir/src/pcs/zk/`, `sumcheck/src/zk/`, `zk-codes/`) implements an **earlier
version** with other numbering; that version was not available, and the four dependences below
are properties of the code (S), not of the paper as published. For each, what the published
paper does:

| # | Place in the pinned code (S) | Dependence in the code | The paper as published (revision of 2026-11-16) | What W-I does, and provenance |
|---|---|---|---|---|
| 1 | Masked sumcheck (`sumcheck/src/zk/transcript.rs`: "Lemma 6.4 divides by two when it inverts the endpoint identity"; returns `EvenCharacteristic` when `F::TWO == 0`) | odd characteristic, explicitly | **No such dependence.** Section 2.5 states that Libra's mask fails when `char(F) = 2` and Definition 6.1 / Lemma 6.2 give a mask polynomial whose transcript is uniform on the consistent transcripts over every finite ring; the proof inverts nothing. Construction 6.4, Theorem 6.3 (`d_s >= 3`) | claim-level mask, Theorem 1' (Original as far as checked, `REFERENCES.md` O-5); the paper's `U_sigma` is the published alternative |
| 2 | Zero-knowledge Reed-Solomon encoding (`zk-codes/src/reed_solomon.rs`, cited there as Proposition 3.19): `p = f + X^l r` on a multiplicative subgroup | implicit: `x^l != 0` at every domain point; on an additive subspace the analogue `X_l(x) = What_mu(x)` vanishes on `U_mu` | **Randomness on the lowest coefficients.** Lemma 3.29: `fhat(X) = sum_{j<=t} r_j X^(j-1) + sum_i v_i X^(t+i-1)` on any set of distinct points is a strong `t`-query zero-knowledge encoding with error 0 (the map from `r` to `t` values is a Vandermonde bijection). No condition on the domain: a linear subspace works | coset domain `beta + S` and aligned high offset, Lemma E (sufficiency at offset `2^l` is Published: Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields", ePrint 2025/1015, Lemma 4.4; the rest is O-3). **The low placement removes the coset requirement**: finding C-2 of `CITATION-AUDIT.md` |
| 3 | Out-of-domain pad (`whir/src/pcs/zk/code_switch.rs`, cited there as Construction 9.7: "OOD points pairwise distinct and nonzero"; the pad continues the power run `rho^(l+s)`) | the pad's weight is nonzero for `rho != 0` | **Private zero-evaders.** Definition 9.2, Lemma 9.4: `r_ood >= t_ood` dedicated pad coordinates and an independent random matrix whose columns span make the answers perfectly private over every finite field, at zero-evading error `max(eps_zero, 1/(|F|^t - 1))` (Lemma 9.5); Construction 9.9 | budget rule of Lemma O with `rho` outside the ambient subspace (Original as far as checked, O-3) |
| 4 | Every type bound `TwoAdicField`, `TwoAdicSubgroupDft` in `whir/src/pcs/zk/` | structural (multiplicative domains) | **None.** The paper is code-agnostic; its own implementation uses Reed-Solomon codes over `GF(2^256)` (Section 1.3), and Lemma 3.29 needs only distinct evaluation points | additive NTT and `WhirDomain` as the non-hiding binary path already does |

So the paper as published neither excludes binary fields nor needs any of the four
replacements; this document built the replacements because only the code could be read. Further
points of the published paper that bear on this document:

- **Layout.** Section 11 (Construction 11.1) puts everything inside the rows of the main oracles:
  each row is a main block, an auxiliary block (the re-encoded folded randomness of the previous
  stage), a mask of two coordinates and a seed; the base-case mask is one more row of the last
  oracle; no mask oracle is sent. This is the layout of W-I (section 6.1). W-I was derived here
  from the earlier, separate-oracle layout (W-S, section 6.4) and is therefore **not new as a
  layout**; what differs from the paper is listed in `REFERENCES.md` O-4.
- **Salts.** Appendix B: with one more seed coordinate than queries, an unopened column keeps
  one field element of entropy (Lemma B.1) and the leaves need no salt, at distance `T / |F|` for
  `T` oracle queries (Lemma B.2). For `|F| = 2^256` that is enough; for the 128-bit and smaller
  alphabets of the leaves here it is not, so section 4's salts stay.
- **Soundness.** The paper proves round-by-round knowledge soundness in the list-decoding regime
  (Theorems 6.3, 7.1, 9.8, 10.2); `zk-wi-soundness.md` proves W-I in the unique-decoding regime
  from BCIKS20 alone. The two were not compared line by line.

Not read in the paper: Sections 4, 5, 8, 9.4 to 9.7, 12, 13 and Appendix A.

---

## 4. Salted leaves

Leaf digest `H(sigma_y || row_y)` with an independent uniform salt `sigma_y` of `s` bits per
leaf; opening a leaf reveals its salt.

**Lemma M (P as a sketch, classical random-oracle model).** Replace the digest of every unopened
leaf by an independent uniform string and compute the tree from those. An adversary making `q`
oracle queries distinguishes the two trees with advantage at most `q * N / 2^s`, `N` the number
of unopened leaves. *Sketch.* The two experiments differ only if the adversary queries `H` on
`sigma_y || .` for the salt of an unopened leaf; each query hits one of `N` uniform unknown salts
with probability at most `N / 2^s`. ∎ With `s = 256`, `N <= 2^21`, `q = 2^128`: `2^-107`. Against
quantum queries the bound is of the order `q^2 N / 2^s` (M, no source read). Chiesa, Manohar,
Spooner, ePrint 2019/834 (read 2026-11-19), do not supply it: their Lemma 7.3 and Theorem 8.6 (3)
carry zero knowledge to the QROM by a classical bound that holds against distinguishers unbounded
in queries, and Lemma M is query-bounded (`CITATION-AUDIT.md` C-8). GordieHowe (Sharp, Grubbs, *Faster and Smaller Anonymous Credentials from Standardized
Signatures*, ePrint 2026/2615, read 2026-11-19, finding C-21) supplies a quantum statement for a
related construction and settles the question of salt length: its Theorem 6.6 (3) gives
"everlasting" zero knowledge in the QROM (queries bounded only before the last proof, unbounded
after; Definition 6.2) for its transformation spBCS (Protocol 6.5: a fresh proof salt in every
challenge input, leaf salts of `b_l` bytes), with per-position leaf term (Definition I.1)
`1/2 sqrt(2^(8b) / 2^(8 b_l)) + sqrt(ln N_leaf / (2 * 2^(8 b_l)))` for `b`-byte digests; its
Section 8.4 notes that with salts as long as the digest the expected distance of an unopened leaf
from uniform is about `1/e`. So with the built 32-byte salts under 256-bit digests that theorem
gives nothing, and Lemma M (query-bounded) is the only statement available; salts of `2b` bytes
(64 with 256-bit digests, as GordieHowe uses) plus a proof salt would bring the built trees under
its theorem, if the transcript is also brought to spBCS form (C-7).

Provenance. The salted tree is Published: Ben-Sasson, Chiesa, Spooner, "Interactive Oracle
Proofs", ePrint 2016/116, Section 3.2 (leaf `rho(v_i || r_i)`, `r_i` uniform of `2 lambda` bits;
Definition 3.3, Lemma 3.4: statistical privacy `n 2^(-lambda/4 + 2)` against an **unbounded**
distinguisher, proven for one-bit leaves). Lemma M is **Adapted**: the query-bounded form for a
salt of `s` bits. The same hybrid argument, with the unpredictable part of the leaf in place of
the salt, is Lemma B.2 of ePrint 2026/391 (revision of 2026-11-16), bound `T 2^-kappa`. Lemma 3.4
as stated does not apply to a 256-bit salt under a 256-bit hash (it needs `2 lambda`), and its
`lambda/4` exponent is not the figure used here; the figure used is Lemma M's, which is a sketch
and is unreviewed. That the salt is necessary, not only sufficient, is Published: Diamond,
ePrint 2025/1015, Section 4.1 (a distinguisher that holds the witness recomputes the root of an
unsalted tree).

Consequences: the simulator needs the content of opened leaves only; internal-node siblings on
opened paths are digests of subtrees of unopened leaves and are simulated by the same
replacement. Salts are needed on **every** tree whose unopened leaves depend on a secret: all
oracles of section 6. The design basis already counts 32-byte salts on the leaf's opened leaves.

---

## 5. Claim-level masks

The lemma document masks a sumcheck by adding a mask polynomial to the summand. The fold rounds
of the two openings are claim reductions whose messages are not always univariate round
polynomials (A's four scalars). The mask theorem is restated at the level of claims.

**Setting.** Rounds `j = 1..n`. Round `j` has a challenge set `Omega_j`, a finite-dimensional
space `P_j` of functions `Omega_j -> F` containing the constants, and a linear functional `lam_j`
on `P_j`. The (unmasked) reduction sends `q_j in P_j`, the verifier checks
`lam_j(q_j) = claim_{j-1}` and sets `claim_j = q_j(r_j)`. Fix `u_j in P_j` with `lam_j(u_j) = 1`.
A mask is `(c, g_1..g_n)`, `c in F`, `g_j in P_j`; its messages are

    q_j^g = g_j + D_j u_j + K_j ,    D_1 = 0,  D_{j+1} = g_j(r_j) + u_j(r_j) D_j ,
    K_n = c,  K_j = lam_{j+1}(g_{j+1}) + lam_{j+1}(1) K_{j+1},   G = lam_1(g_1) + lam_1(1) K_1 ,

its final value is `q_n^g(r_n)`, a linear function of the mask coefficients with public weights.

**Theorem 1' (P; C).** For every challenge vector: `lam_1(q_1^g) = G` and
`lam_{j+1}(q_{j+1}^g) = q_j^g(r_j)` (the mask's messages pass the round checks), and the map from
a uniform mask to `(G, q_1^g..q_n^g)` is onto the space `V_r` of sequences passing the round
checks, with all fibres of equal size. `dim V_r = 1 + sum_j (dim P_j - 1)`; dropping the constant
of each `g_j` makes the map a bijection.

*Proof.* The first claim: `lam_{j+1}(q_{j+1}^g) = lam(g_{j+1}) + D_{j+1} + lam(1) K_{j+1} =
K_j + D_{j+1} = q_j^g(r_j)`. The second is the proof of Theorem 1 of the lemma document verbatim
(choose `kappa in F^n`, set `g_j := p_j - D_j u_j - kappa_j`, `c := kappa_n`, show
`K_j = kappa_j` by downward induction); it uses only linearity of `lam_j` and `lam_j(u_j) = 1`. ∎

Instances:

| Round | `P_j` | `lam_j` | `u_j` | Mask coefficients per round |
|---|---|---|---|---|
| plain sumcheck round, degree `d` (eq-fold of the generic WHIR, FRI-Binius) | polynomials of degree `<= d` in `X` | `p(0) + p(1)` | `X` | `d`: this is the staircase mask |
| eq-weighted round, reduced message | same | `(1 + tau) p(0) + tau p(1)` | `1` | `d`: Libra's mask |
| A's affine-combiner round | `span{1, a, a^2, b, a b}` in the challenge `(a, b)`; `q = u0 + a (u0 + claim) + a^2 w + b c0 + a b (c0 + c1)` | `[1] q + [a] q` (so that `lam(q) = claim`) | `1` (since `lam(1) = 1`) | 4 |

The third row is read off the claim update in the pinned verifier (S: `verify_whir`); the
prover-side meaning of the four scalars was not read. C (`results/blind.txt`): the mask's views
pass the round checks and have rank `1 + 4n` for all `16^n` challenge vectors over GF(4)
(`n = 1, 2`) and for random and all-0/1 vectors over GF(256) (`n = 3, 5, 14`); the plain space
has rank `1 + n d` for all challenge vectors over GF(4) (`n = 3`, `d = 2, 3`); with the invalid
`u = 1` in the plain space the views fail the round checks except at `r_1 = r_2 = 0`.

**Lemma S (masked reduction with residual hand-off) (P).** Run a claim reduction as: prover
sends `G`; verifier sends `rho`; the claim becomes `rho * claim + G`; each message is
`rho q_j^f + q_j^g`; the final claim `rho * (final claim of f) + q_n^g(r_n)` is handed on. If the
mask is uniform, independent of everything else, and used once, then for fixed challenges the
messages are uniform on the set of sequences passing the round checks from the public head
`rho * claim + G`, whatever `q^f` is. *Proof.* `q^f` passes the checks from head `claim` by
completeness; add Theorem 1'. ∎ Soundness: the mask is committed before `rho`; `+1/|F|` per
masked batch (P, as in the lemma document section 1.2).

---

## 6. The hiding WHIR-style opening

### 6.1 Construction W-I (inline)

Everything secret rides inside the main oracles; there is no separate mask oracle.

**Layout of oracle `i`** (lane = coefficient slots):

    [0, c_i)                 carried: the witness (i = 0) or the lanes of the previous level's
                             folded polynomial, its excess included (c_{i+1} = ceil(lrow_i / 2^kappa_{i+1}))
    [c_i, c_i + n_i)         aux rows: the n_i mask coefficients of this level's fold batch.
                             eq-fold: each written into EVERY lane of its row.
                             Affine combiner (system A): each written into the LAST lane only (the
                             lane that is G in every round), zero in the other lanes, and the aux
                             rows start kappa_i slots higher: [c_i, c_i + kappa_i) are zero GUARD
                             slots that receive the fold's high part (soundness document, F-1)
    [aoff_i, aoff_i + t_i)   t_i = Q_i + o_i fresh uniform coefficients per lane; aoff_i aligned
    lrow_i = aoff_i + t_i    coefficient length of a lane; domain D_i = beta_i + S, beta_i outside S

`n_i = 1 + 2 kappa_i` for the eq-fold (degree 2), `1 + 4 kappa_i` for A's affine combiner. At
level 0 with alphabet `K` a mask coefficient in `F` takes `[F : K]` aux rows, one per coordinate.
Leaves are salted. The last oracle carries **one more column** `Gcol`: the codeword on `D_{L-1}`
of a fresh uniform polynomial `gt` of `lrow_{L-1}` coefficients.

**Opening** of the public claim `<p, W> = T` (weights zero outside the carried slots):

    level i = 0..L-1:
      1. prover sends G_i (the mask's sum);  verifier sends rho_i;  T <- rho_i T + G_i,  W <- rho_i W
      2. kappa_i masked fold rounds (Lemma S): messages rho_i q^f + q^g, challenges gamma;
         T <- the final claim
      3. fold: p' = sum_b eq(gamma, b) lanes. The aux slot of mask coefficient m now holds exactly
         that coefficient (sum_b eq(gamma, b) = 1); its weight becomes the mask's final-value
         weight at gamma. The relation is  <p', W'> = T  on the folded lane p' (lrow_i coefficients).
      4. not the last level:
           prover commits oracle i+1 (layout above, salted);
           verifier sends o_i out-of-domain points outside the ambient subspace; prover answers p'(rho);
           verifier opens Q_i rows of oracle i (salts, paths); v_q = fold of row q;
           verifier sends lam;  T <- T + sum_k lam^k (answers),  W' gains lam^k (X_j(point_k))_j
      5. last level (base case):
           prover sends mu = <gt, W'>;  verifier sends c;  prover sends P* = gt + c p';
           verifier checks <P*, W'> = mu + c T;
           verifier opens Q_{L-1} rows of the last oracle, with Gcol at the same rows, and checks
           P*(y) = Gcol(y) + c * fold(row y)   for each.

The base case **adapts** Construction 7.2 of ePrint 2026/391 (revision of 2026-11-16; verified
against the paper on 2026-11-19: the prover sends a fresh mask codeword `g = Enc(g, r')` and
`mu~ = <sl(st), g>`, receives `gamma`, discloses `f* = g + f gamma` and `r* = r' + r gamma`; the
verifier checks `<sl(st), f*> = mu~ + mu gamma` and `Enc(f*, r*)[Q] = g[Q] + y[Q] gamma` at `t`
uniform points; Theorem 7.1 and Lemma 7.3: perfect honest-verifier zero knowledge, round-by-round
errors `eps_mca + Lambda eps_pil` and `(1 - delta)^t`). What changes here: one secret, and the
mask is committed as a column of the last oracle, as the paper's own Section 11 does ("the final
oracle has one additional masking row").
each level is not sent: it stays in `p'` and is carried into the next oracle, and the final
degree-3 sumcheck is replaced by the base case.

### 6.2 Zero knowledge

**Theorem W (P; C).** Fix the challenges, with out-of-domain points distinct and outside the
ambient subspaces and the opened rows of each oracle distinct. If all randomness (per oracle:
`t_i >= Q_i + o_i` coefficients per lane; per level: one mask; `gt`) is uniform and independent,
the algebraic view of W-I is uniform on the set of accepting views. It is simulated from the
public claim alone:

    Sim:  for each level:  G_i uniform; each fold-round message uniform subject to its round check;
                           out-of-domain answers uniform; opened rows uniform;
          P* uniform;  mu := <P*, W'> - c T;  Gcol(y) := P*(y) - c * fold(row y).

*Proof.* Lemma T with the blocks, in this order:

| Block | Pad | Space | Why `Im B` is the whole space |
|---|---|---|---|
| level `i`: `G_i`, fold-round messages | mask of level `i` | sequences passing the round checks from the head, which is a function of earlier blocks | Lemma S |
| level `i`: out-of-domain answers, opened rows of oracle `i` | `r_i` | everything | Lemmas E, O |
| `P*`, `mu`, `Gcol` at the opened rows | `gt` | graph of the two check equations over a free `P*` | `P* = gt + c p'` is a bijection in `gt` |

Order: level 0 messages, level 0 rows, level 1 messages, .., last rows, base case. Dependences:
the fold messages of level `i` depend on the witness, on `r_{<i}` and masks `<= i` (the weight is
zero on the randomness slots and on the aux rows of oracle `i` until step 3); rows of oracle `i`
depend on masks `<= i`, `r_{<i}` and `r_i`; the base case on everything and `gt`. Each pad is
absent from all earlier blocks. The determined entries (`mu`, `Gcol(y)`) satisfy the verifier's
equations in every honest run. ∎

Statistical version: an honest verifier's challenges violate the hypotheses only by repeated
query positions (the budget counts distinct rows, so repetition only helps) or out-of-domain
points inside the ambient subspace; sampling `rho` outside it (as soundness already requires
`rho` outside the domain) makes the statement perfect.

Computation (C, `results/whir.txt`, `results/basecase.txt`). The prover of `whir_i.py` runs on
affine forms; a separate concrete verifier accepts every honest view and rejects each of 39
single-entry changes.

| Instance | Field | Challenge tuples | Result |
|---|---|---|---|
| two levels, folds (2, 1), 2 + 2 queries, 1 out-of-domain point, 8 witness and 36 randomness variables | GF(2^8) | 150 random, 6 with all fold challenges in {0, 1} | `rank B = rank [A | B] = 33 = dim Acc` in all 156 |
| three levels, folds (1, 1, 1) | GF(2^8) | 106 | same, 33 |
| two levels, folds (2, 2), 3 + 2 queries, 2 out-of-domain points | GF(2^8) | 46 | same, 46 |
| one level, fold 1 | GF(2^4) | 206 | same, 10 |
| two levels | GF(2^6) | 156 | same, 18 |
| no fold, full opening, **every** randomness value (`8^6` tapes), two witness pairs, 12 challenge settings | GF(2^3) | 24 cases | count tables identical in all 24 |

Negative controls (each must leak, each does, in every tuple): linear domain with an opened row
in `U_top` (60/60; enumeration: 12 of 24, exactly the rows in `U_top`); one randomness
coefficient too few (60/60); no sumcheck mask (60/60); Libra's mask in a two-round batch (60/60);
no base-case mask (60/60; enumeration 24/24); no encoding randomness (enumeration 24/24).

Not tested: alphabet `K` smaller than `F` at level 0; sizes beyond the table.

### 6.2a System A: the affine-combiner fold inside the composed opening (P; C)

Layout (soundness document F-1 and F-7): per lane, carried slots `[0, c_i)`; `kappa_i` zero guard
slots; `1 + 4 kappa_i` aux slots, the mask coefficients in the **last lane only**; zeros; `t_i`
uniform coefficients at an offset that is a multiple of `2^ceil(log2(t_i + kappa_i))`. The folded
lane has `lrow_i + kappa_i` coefficients and is carried whole. The stronger alignment is needed for
completeness, not for hiding: `X X_c` has components on `c + 1` and on `c` with its trailing one
bits cleared, so with an offset aligned to `t_i` only, a random slot whose low bits are all ones is
moved below the offset, into the aux slots, and the honest final relation fails (C: 30 of 30 honest
runs rejected at fold 2).

**Theorem W-A (P; C).** With this layout, under the hypotheses of Theorem W, the algebraic view of
W-I with the affine-combiner fold is uniform on the set of accepting views; the simulator is the
one of Theorem W with four uniform scalars per fold round.

*Proof.* Lemma T with the blocks of Theorem W. Fold-round block: the messages are
`rho q^f + q^g` with `q^g` the mask's messages of Theorem 1' (round space `span{1, a, a^2, b, ab}`,
`u = 1`), computed from the mask coefficients; Lemma S gives uniformity on the sequences passing
the round checks. Row block: Lemma E for each lane of oracle `i` (the commitment is made before
any fold, so the affine combiner plays no role in it); the last lane's aux content is message for
this purpose. Base case: `P* = gt + c p'` with `gt` of `lrow + kappa` coefficients. Dependences:
the mask of level `i` enters the rows of oracle `i` (last lane) and everything later, not the
earlier blocks; where the fold moves the excess is irrelevant, because the folded lane is never
revealed except through later rows (padded by later randomness) and `P*` (padded by `gt`). ∎

C (`zk-commit/whir_a.py`, `test_whir_a.py`, `results/whir_a.txt`): symbolic prover and concrete
verifier for the affine-combiner opening. `rank B = rank [A | B] = dim Acc` in every challenge
tuple of: one level fold 1 (GF(256), 124 tuples including all-0/1 challenges, rank 20; GF(64), 80);
one level fold 2 (64 tuples, rank 33); two levels folds 1/1 (64, rank 33); two levels folds 2/1 with
3 + 2 queries (30, rank 53). Controls, each leaking in every tuple: no mask; no base-case mask; one
random coefficient too few; linear domain with a row in `U_top`. Layout controls, honest view
rejected: every-lane aux rows (60/60), offset aligned to `t` only (30/30).

### 6.3 Soundness of W-I (sketch; superseded)

Superseded by `zk-wi-soundness.md` sections 3 to 5 (proof, unique-decoding regime) and its
calculator tables; the rates quoted below were wrong (A's last oracle has `2^20` rows, B's `2^16`)
and the query counts are those of `soundness/output/wi-tables.txt`. Kept as the record.

- Masked batches: Lemma S, `+1/|F|` each. A cheating prover may write different values into the
  lanes of an aux row; the "mask" is then the polynomial `sum_m row_m(x) phi_m(x)` (`row_m` the
  multilinear extension of the row over the lane index, `phi_m` the mask's basis function), still
  fixed before `rho_i`, of degree one higher per variable; the sumcheck's soundness error grows
  from `d/|F|` to `(d + 1)/|F|` per round and nothing else changes (P, sketch).
- Each oracle is the plain interleaved Reed-Solomon code of its lanes with `lrow_i` coefficients
  per lane: W-I is the non-hiding WHIR opening applied to polynomials whose coefficient count is
  not a power of two (`c_i + n_i + ..` instead of `2^mu`), on a coset domain, at rate
  `lrow_i / N_i`. Proximity-gap statements for Reed-Solomon codes hold for arbitrary evaluation
  sets and dimensions (M: BCIKS20; `docs/soundness-method.md` lists what is confirmed). The
  round-by-round analysis of the code switch for such dimensions is **not** written here (U).
- The last query round is the base case's spot check (positions drawn after `P*`); the base
  case's soundness is that of Construction 7.2 with one secret (M).
- Rates: A's last oracle goes from `2^10 / 2^18` to `1268 / 2^18`; under the per-query rule
  `(1 + rate) / 2` that moves 116 queries to 117 (E). B's last oracle from `1024 / 2^14` to
  `1274 / 2^14`: 119 to 122 (E). The soundness calculator must be rerun with the true rates.

### 6.4 Variant W-S (separate mask oracles; the layout of the pinned prime-field code)

Provenance: W-S is the layout of the pinned Plonky3 code, an implementation of an earlier
version of ePrint 2026/391. The revision of 2026-11-16 does not use separate mask oracles
(Section 11); nothing below is attributed to the paper.

The pinned implementation keeps each new oracle's message a power of two and moves every other
secret into small mask oracles: one for the sumcheck masks, one per code-switching round holding
`(Fold(r_i, gamma) || pad)`, and in the base case one fresh blind per mask oracle, each
spot-checked at `t_zk` positions (S: `whir/src/pcs/zk/config.rs`, `base_case/mod.rs`). Ported to
characteristic 2 it needs the replacements of section 3.4 and nothing else; its zero-knowledge
proof is Lemma T with two more kinds of block (mask-oracle spot values, padded by that oracle's
own encoding randomness, Lemma E with `t_zk`; mask reveals, padded by the blinds). It was not
tested here as a whole (U); its components are the ones tested. No soundness analysis of this
layout was read (the published paper analyses the in-oracle layout). Cost: section 8.

---

## 7. Folding openings without re-randomisation

Provenance: Lemma F is Original (the Ycash developers, 2026) as far as checked. Related published
statements: Haböck and Al Kindi, ePrint 2024/1037, Section 2 (page 5 and footnote 3): each FRI
fold halves the randomizer space on a multiplicative domain, which is why their Protocol 2 adds
a full mask polynomial `R` (Lemma 2); they report no proof for the route without the mask.
Diamond, ePrint 2025/1015, Section 4.2, discusses delaying the mask and concludes that the
sumcheck of BaseFold prevents it. Lemma F concerns the opened leaves only; the sumcheck messages
of a folding opening need the masks of section 5 or the full mask of 7a.

**Lemma F (P; C).** Commit `P_0` with message in `[0, 2^n)` and `T` uniform coefficients in
`[2^n, 2^n + T)`, on a coset domain. Let oracles `0..Lc-1` be committed (oracle `i` after `K_i`
fold bits in total), with `K = K_Lc` the fold depth of the final polynomial `P_Lc`, and let `Q`
query paths be opened. If `T >= Q * 2^K` (and `2^(n-K)` is a multiple of `2^ceil(log2 (T / 2^K))`,
so that the folded randomness stays aligned), the opened leaves of all oracles are uniform on the
set of leaf tuples consistent under folding, independent of the message, and the final
polynomial's randomness part keeps `T / 2^K >= Q` uniform coefficients. With fewer coefficients and `Q` paths
with distinct final points the leaves are not independent of the message (C at the tested sizes;
the proof below shows where the rank is lost).

*Proof.* Write `R` for the randomness as a tensor over (fold bits, final slot). The folded
randomness at level `i` is `R_i`, with `t_i = T / 2^(K_i)` coefficients. A leaf of oracle `i` is
the row of lanes at one point `y` of the next domain: functionals `e_b (x) ev_{i+1}(y)` on
`R_i`. Let `E_i` be the span of all functionals revealed at levels `>= i`, as functionals on
`R_i`, and `V_{i+1}` the span of `ev_{i+1}(y_q)` over the paths. Then
`E_i = F^(lanes) (x) V_{i+1} + eq(gamma_i) (x) E_{i+1}` and `V_{i+1}` is contained in `E_{i+1}`
(the next leaf contains the fold of this one). Since `eq(gamma, .) != 0`, the intersection of the
two summands is `eq(gamma_i) (x) V_{i+1}`, so the only relations among the opened values are the
fold relations, provided `dim V_{i+1} =` the number of distinct points, which holds iff
`t_{i+1} >=` that number (Lemma E on the coset image domain; `q` maps `beta` outside `S` to a
point outside `q(S)`). `t_{i+1} >= Q` for all `i < Lc` is `T >= Q 2^K`. The message part of the
view satisfies the same fold relations, so Lemma L applies. ∎

Computation (C, `results/fold.txt`), GF(2^8), `n = 3`, 120 challenge and query choices per case
(4 with all fold challenges in {0,1}): hiding with `rank B` equal to the accepting dimension for
`(Lc, Q, T) = (2, 2, 8), (1, 3, 6), (3, 1, 8)`; leaking in all 120 for `T = (Q - 1) 2^Lc`, for the
budget of one level less, for the linear domain with a query in `U`, and for a final polynomial
sent in clear. Enumeration over GF(16) (`n = 1`, one fold, one query, all `gamma`, all positions,
all `16^4` tapes): identical in 128 of 128 cases with `T = 2`, different in 128 of 128 with `T = 0`.

**Construction F-2 (budgeted).** Lemma F's encoding; the lockstep sumcheck masked by one
staircase mask over all its rounds (lemma document Corollary A); the final polynomial sent as
`P* = gt + c P_Lc` with a fresh mask codeword `Gcol` committed on the final domain before the
first challenge and opened at the queries' final points; the mask's final value and `mu` proved
as in the base case, with the staircase coefficients in a small mask oracle or in the linear
opening gadget (lemma document 5.3). **Theorem BF-2 (P for the view of Lemma F plus `P*`, C;
(U) for the mask-oracle part).** The fold-phase view (opened leaves, `P*`, `Gcol` values) is
uniform on its accepting set.

**Construction F-1 (full mask).** Commit a second uniform polynomial `m` of the full size over
`F` beside `p`; prover sends `G = <m, W>`; verifier sends `rho`; the **unmodified** folding
opening runs on `h = rho p + m` with claim `rho v + G`, the first oracle of `h` being read as
`rho * (p's leaf) + (m's leaf)`; `p` is encoded with `T >= Q * 2^(k_0)` (one level only: only
oracle 0 of `p` is opened). **Theorem BF-1 (P).** Perfect honest-verifier zero knowledge: `h` is
uniform and independent of `(p, r)`; the simulator samples `h`, runs the honest opening on it,
samples `p`'s opened leaves uniformly (Lemma E) and sets `m`'s leaves to `h - rho p` there.
Not tested (the proof is two lines). Cost: a second commitment of the witness' size over the
challenge field, and `m`'s leaves in every query.

B's recursion layers, the only users of the folding opening in the design basis, publish no
secret (framework selection R-9) and need neither.

### 7a. Construction W-M: the full mask in front of the WHIR-style opening (system B's opening)

Decided for system B on 2026-11-19. It is construction F-1 applied to the opening of section 1.3.

Provenance: **Adapted** from Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields",
ePrint 2025/1015, Construction 4.1 and Theorem 4.3 (read in full, 2026-11-19): pad the committed
polynomial with random high coefficients on a domain disjoint from the message subspace, commit a
second uniform polynomial of the same length, send its claim, receive a challenge, and run the
unmodified opening on the combination `alpha f + f'`; the simulator samples the combination,
runs the opening honestly on it, samples the opened values of `f` uniformly (Lemma 4.4) and
back-fills those of `f'`. Diamond attributes the two techniques to Aurora (Section 5, 5.1) and
Virgo (Protocol 2). W-M's `rho p + mk` is that combination and Theorem W-M's simulator is that
simulator. What changes: the opening is the WHIR-style interleaved opening of section 1.3 instead
of binary BaseFold (Diamond-Posen, Construction 4.11); both polynomials share leaves; the pad is
`t = Q_0` coefficients per lane at an aligned offset (Lemma E) instead of `kappa = gamma 2^theta`
at offset `2^l`. Diamond's construction doubles the message space to `2^(l+1)` to hold the pad
(its Section 4.2: about four times the prover cost); the rate consequence for W-M is in section 8
and in `zk-wi-soundness.md` 9. Like Diamond's, W-M has no excluded challenge.

    oracle 0, one leaf per domain point of D_0 = beta + S (beta outside S), salted:
        the row of p's lanes:  message slots [0, m), t = Q_0 uniform coefficients per lane at an
                               aligned offset (section 3.1), alphabet K
        the row of mk's lanes: a uniform polynomial of the same lane length, every slot, alphabet F
    1. prover sends G = <mk, W>;  verifier sends rho
    2. the UNMODIFIED non-hiding opening on h = rho p + mk with claim rho T + G:
       a level-0 query opens both rows and uses rho * (p's row) + (mk's row);
       later oracles, round messages and the final message are those of the non-hiding protocol.

**Theorem W-M (P; C).** If `mk` is uniform on all `lanes x lrow` slots and independent, `p`'s
random coefficients are uniform, and the level-0 positions are at most `t` distinct rows, the view
is simulated without the witness: sample `h` uniformly and run the honest non-hiding opening on it
with claim `<h, W>`; set `G := <h, W> - rho T`; sample `p`'s opened rows uniformly; set `mk`'s
rows to `h`'s rows minus `rho` times `p`'s.

*Proof.* Lemma T with two blocks. Block 1: everything the opening computes from `h`; pad `mk`
(`h = rho p + mk` is a bijection in `mk`), space everything, with `G` determined by
`<h, W> = rho T + G`. Block 2: `p`'s opened rows; pad: `p`'s encoding randomness, Lemma E; `mk`'s
rows are determined. `mk` is absent from no earlier block; `p`'s randomness enters block 1 only
inside `h`, which is already uniform given it. ∎ No mask on any sumcheck of the opening, no base
case, no randomness in later oracles: the opening's code is the non-hiding code.

Soundness: one added round, `(N_0 + 1)/|F|` (soundness document section 9). The mask must cover
every slot, including `p`'s random slots; `mk` over a proper subfield or with a missing slot leaks.

C (`zk-commit/test_wm.py`, `results/wm.txt`). View modelled: `G`, **every coefficient of `h`** (an
upper bound on any non-hiding opening's view), the opened rows of `p` and `mk`. `rank B =
rank [A | B] = dim Acc` in all of: 2 lanes x 3 slots, `Q = 3` (120 tuples, rank 20); 4 lanes x 4,
`Q = 4` (80, rank 48); 4 lanes x 5, `Q = 2`, 32 points (60, rank 40), GF(256). Enumeration of all
`8^6` randomness values over GF(8), two witnesses, every `rho` and position: identical in 32 of 32
cases. Controls, each leaking in every tuple: linear domain with a row in `U_top`; one random
coefficient too few; mask missing one message slot; no mask (also by enumeration, 28 of 28).

---

## 8. Randomness and proof size at the category 1 design basis

All figures (E): counted from the schedules of section 1.3 with 32-byte field elements and
digests; not measured.

**W-I, system A leaf** (`n = 24`, folds 5/3/3/3, queries 171/119/117/116, unique decoding, no
out-of-domain samples). Lane lengths: `2^19 + 427`, `2^16 + 247`, `2^13 + 245`, `2^10 + 244`
(alignment 256, 128, 128, 128; each excess is the level's query count plus its alignment).

*At the current counts (amendment 2026-11-19, `zk-referee.md` R-6; A queries 234/166/169/186, E, computed from the
counts only):* lane lengths `2^19 + 490`, `2^16 + 294`, `2^13 + 297`, `2^10 + 314`; encoding randomness, oracle 0,
32 x 234 = 7,488 elements of `GF(2^64)`, 59,904 bytes; oracles 1 to 3, 8 x (166 + 169 + 186) = 4,168 elements of
`F`, 133,376 bytes. The remaining rows of the table below (fold-batch masks, `gt`, the proof overhead and its
percentage) are at the old counts and were **not recomputed**.

| Item (old counts) | Count | Bytes |
|---|---|---|
| encoding randomness, oracle 0 | 32 lanes x 171, in `GF(2^64)` | 43,776 of randomness |
| encoding randomness, oracles 1 to 3 | 8 x (119 + 117 + 116) = 2,816 in `F` | 90,112 of randomness |
| fold-batch masks | 11 + 7 + 7 + 7 = 32 (eq-fold) or 21 + 13 + 13 + 13 = 60 (affine combiner) | up to 1,920 of randomness |
| base-case mask `gt` | 1,268 | 40,576 of randomness |
| proof: `G_i` | 4 | 128 |
| proof: longer final message (`P*`, 1,268 instead of 1,024 elements) | +244 | 7,808 |
| proof: `mu`; `Gcol` at 116 (to 117) rows | 1 + 117 | 3,776 |
| proof: one more row in the last round (rate) | 1 row of 8 lanes with salt and path | about 500 |
| proof: salts | 523 opened leaves x 32 | already in the design basis |
| **proof overhead** | | **about 12 KiB on 443 KiB (2.8 %)** |

Prover: lane polynomials grow by under 0.1 % at level 0; one extra column of `2^18` rows on the
smallest oracle; about 175 KB of generator output per proof.

**W-I, system B leaf** (superseded layout, record: B as built is BaseFold at rate 1/8 with 184 to 192 queries and
D25 Construction 4.1's mask, see the amendment in section 1.3; its overhead is in `yugen-proof-b2/docs/parameters.md`
11.3, not restated here) (`n = 19`, folds 5/4, queries 171/119): lane lengths `2^14 + 427` and
`2^10 + 250`; final message `+250` elements (8.0 KiB), `Gcol` at 122 rows (3.9 KiB), 3 more rows
in the last round (about 2.3 KiB): **about 14 KiB on 325 KiB (4.4 %)**.

**W-S for comparison** (A leaf): 4 mask oracles and a blind group, each a tree of about `2^11`
leaves opened at `t_zk` = about 197 positions (130 bits plus the union over the mask oracles at
`(1 + 1/4)/2` per query, no grinding): about 234 KiB of openings and 38 KiB of reveals, **about
270 KiB (61 %)**. This is the reason W-I is the recommended layout.

**Out-of-domain samples** (Johnson-regime variants only): `t_i` grows by `o_i` per lane; no proof
bytes.

**Folding family.** F-2: `T = Q * 2^K`; for `n = 24`, `Q = 171`, final `2^10`: `T = 2^21.4`, 17 %
of the message (the rate rises from 0.25 to 0.29, and the query count with it). F-1: a second
full commitment over `F`.

---

## 9. Tests

`zk-commit/`, Python standard library, `python3 test_*.py` from the directory; each exits
non-zero on failure and writes `results/*.txt`.

| File | Statement | Method |
|---|---|---|
| `ff.py`, `additive.py` | fields, affine forms, rank and enumeration helpers; subspace polynomials, novel basis, image chain | |
| `test_code.py` | Lemma E, alignment | rank for every row set; enumeration over GF(8) |
| `whir_i.py`, `test_whir.py` | Theorem W, Lemmas O, S | symbolic prover, concrete verifier, rank against accepting dimension, five negative controls |
| `test_basecase.py` | Theorem W with no fold | enumeration of `8^6` tapes; agreement of enumeration and rank |
| `test_fold.py` | folding identity, Lemma F | rank; enumeration over GF(16) |
| `test_blind.py` | Theorem 1' (three round spaces); evaluation blinding (`zk-composition.md` section 3) | rank for all challenge vectors; enumeration over GF(4) |
| `whir_a.py`, `test_whir_a.py` | Theorem W-A (section 6.2a): system A's composed opening | symbolic prover, concrete verifier, rank against accepting dimension, four leak controls, two layout controls |
| `test_wm.py` | Theorem W-M (section 7a): system B's opening | rank against accepting dimension; enumeration over GF(8); four controls |

Run on 2026-11-19: all five test files exit 0 (`FAILURES 0` in each result file). Run times on
the M5: under 2 s, except `test_fold.py` 26 s, `test_basecase.py` 50 s, `test_blind.py` 89 s.

---

## 10. Sources

| Source | Read? | Used for |
|---|---|---|
| Pinned Plonky3 `fe5e46d7`: `whir/src/pcs/zk/{mod,config,code_switch,committer}.rs`, `base_case/{mod,prover}.rs` (documentation and the budget derivation), `zk-codes/src/{encoding,reed_solomon}.rs`, `sumcheck/src/zk/transcript.rs` (`validate`), `whir/src/domain.rs`, `binary-pcs/src/{pcs,fold}.rs` module text, `binary-pcs/src/whir/domain.rs`, `binary-dft/src/traits.rs` | read (S) | sections 1, 3.4, 6.1, 6.4 |
| Pinned leanVM `84780fb4`: `crates/verifier/src/whir.rs` (constants, `verify_whir`, `fold_row`, test comments) | read (S) | sections 1.3, 3.2, 5 |
| Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint 2026/391, revision of 2026-11-16 | **read 2026-11-19** (citation audit): Sections 1.2 to 1.4, 2.5, 3.3.1, 6.1 to 6.3, 7, 9.1 to 9.3, 10.1, 11, Appendix B. The pinned code cites an earlier version's numbering | sections 3.2, 3.4, 4, 6.1, 6.4 |
| Ben-Sasson, Chiesa, Spooner, "Interactive Oracle Proofs", ePrint 2016/116 (copy dated 2016-02-10) | **read 2026-11-19**: Theorems 1.2, 7.1, Lemmas 3.4, 7.5, Sections 2.3, 3.2 | section 4, `zk-composition.md` 6 |
| Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields", ePrint 2025/1015 | **read in full 2026-11-19** | sections 3 (Lemma E), 4, 7a |
| Haböck, Al Kindi, "A note on adding zero-knowledge to STARK", ePrint 2024/1037 (revision of 2025-02-20) | **read 2026-11-19**, pages 1 to 16 | section 7 (related: each fold halves the randomizer space, Section 2, page 5) |
| Diamond, Posen, "Polylogarithmic Proofs for Multilinears over Binary Towers" (ePrint 2024/504); Arnon, Chiesa, Fenzi, Yogev, "WHIR" (ePrint 2024/1586) | read 2026-11-19 in the second citation pass (sections in `../REFERENCES.md`); neither treats zero knowledge; this document's descriptions of the two openings (1.3, 1.4) are from the code (S) and agree with DP24 Construction 4.12 (the coefficient fold of 1.4 is its Lemma 4.14, `(1 - r) a_2j + r a_2j+1`) and WHIR Construction 5.1 | 1.3, 1.4 |
| BCIKS20 | read by other documents (`soundness-method.md`) | (M) where named |

---

## 11. Open

1. Soundness of W-I: done for unique decoding (`zk-wi-soundness.md`); open for the Johnson regime.
2. System A: the affine-combiner fold inside the composed opening (the excess rule of section
   3.2 and the meaning of the four scalars were derived from the verifier only); a level-0
   alphabet smaller than `F`.
3. W-S as a whole, and Theorem BF-2's mask-oracle part: not tested.
4. Lemma M is a sketch; the quantum bound is from memory (no source read).
5. ePrint 2026/391 was read (section 3.4). Open: a line-by-line comparison of W-I with its
   Construction 11.1, and the choice between the high-offset coset placement and the paper's low
   placement (findings C-2 and C-3 of `CITATION-AUDIT.md`).
6. Done: `soundness/src/yugen_soundness/wi.py`, `uv run yugen-soundness --wi`.
