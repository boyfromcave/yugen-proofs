# Zero-knowledge sumcheck in characteristic 2: the mask lemma

Part of Yugen. This document states and proves the lemma on which the zero knowledge
of the sumchecks of both proof systems rests, in the binary fields GF(2^k) both systems use, and
records what was checked by exhaustive computation in `../zk-lemma/`.

Status tags used on every claim:

| Tag | Meaning |
|---|---|
| **(P)** | proven in this document, pen and paper |
| **(C)** | checked by exact computation in `zk-lemma/` (sizes stated with the claim) |
| **(S)** | read in a primary source, named with the claim |
| **(M)** | from memory, or read only in an abstract or a secondary description: not verified |
| **(U)** | unproven, open |

Result in one paragraph. Libra's mask `a0 + sum_i g_i(x_i)` does not hide a sumcheck over
`{0,1}^n` in characteristic 2 (P, C). The **staircase mask**

    g(x) = c + sum_{j=1..n} ghat_j(x_j) * x_{j+1} * x_{j+2} * ... * x_n ,   ghat_j(0) = 0, deg ghat_j <= d_j

with `1 + sum_j d_j` uniform coefficients makes the sumcheck perfectly zero-knowledge for every
challenge vector, with no excluded challenge and no condition on the field size (P, C). The
weighted mask of `yugen-zk-b` is correct only outside the event "some `r_k = 1`" and is
superseded. For a sumcheck weighted by `eq(tau, x)` (a zerocheck with reduced round messages),
Libra's mask is perfect in every characteristic (P, C). All three facts are one theorem
(Theorem 1): a mask term for round `j` needs a cofactor whose sum over the remaining cube is 1,
and the constant cofactor 1 sums to `2^(n-j)`, which is 0 here.

Provenance (citation audit of 2026-11-19; full entries in `../REFERENCES.md`). **Published:** the
masked sumcheck with a full random polynomial (Chiesa, Forbes, Spooner, "A Zero Knowledge
Sumcheck and its Applications", ePrint 2017/305, Section 2.3); the small mask
`a0 + sum_i g_i(x_i)` (Xie, Zhang, Zhang, Papamanthou, Song, "Libra: Succinct Zero-Knowledge
Proofs with Optimal Prover Computation", ePrint 2019/317, Section 4.1, Construction 1 and
Theorem 3); **the failure of that mask for a plain sum in characteristic 2** (Chiesa, Fenzi,
Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint 2026/391, revision
of 2026-11-16, Section 2.5, page 20, and Section 1.2), together with a mask that is uniform on
the consistent transcripts over every finite field and ring (the same paper, Definition 6.1 and
Lemma 6.2). This document was written on 2026-11-19 before that revision could be read; its
section 2 found the failure independently, and it is **not** a new finding. **Original (the
Ycash developers, 2026), as far as checked:** the staircase family and the general family `M_u`
with Theorem 1 and Corollaries A to C (a different family from the paper's `U_sigma`: one
univariate polynomial per round times the trailing product, `1 + sum_j d_j` coefficients, a
bijection, per-round degrees, general round functionals; the paper's has `(k+1)(d_s - 1)`
coefficients and is a surjection), Theorem 2, the opening gadget (section 5), the GKR layer
construction (section 7, **adapted** from Libra's Section 4.2) and Lemma 5. Which of the two
masks to build is finding C-1 of `CITATION-AUDIT.md`.

---

## 1. The problem

### 1.1 Sumcheck variant

`F = GF(2^k)`, `q = |F|`. `n >= 1` variables. Degree bounds `d_1..d_n >= 1`; `F[x]_{<=d}` is the
space of polynomials of degree at most `d_j` in `x_j`. (The multilinear case is `d_j = 1`; the
systems use `d_j = 2` for a product of two multilinears and `d_j = 3` with a third factor.)

Each variable `j` has a **summation functional** `lam_j`, a nonzero linear functional on
univariate polynomials of degree at most `d_j`:

    plain sum over {0,1}:          lam_j(p) = p(0) + p(1)
    eq-weighted (zerocheck):       lam_j(p) = (1 + tau_j) p(0) + tau_j p(1)        tau in F^n public
    general two-point weights:     lam_j(p) = w_j(0) p(0) + w_j(1) p(1),  (w_j(0), w_j(1)) != (0,0)

The total is `Lam(f) = lam_1 lam_2 ... lam_n f = sum_{x in {0,1}^n} prod_j w_j(x_j) f(x)`. The
claim is `Lam(f) = S`.

Round message `j`, for challenges `r_1..r_{j-1}`:

    p_j^f(X) = lam_{j+1} ... lam_n  f(r_1, .., r_{j-1}, X, x_{j+1}, .., x_n)        degree <= d_j

Verifier checks: `lam_1(p_1) = S`; `lam_j(p_j) = p_{j-1}(r_{j-1})` for `j >= 2`; finally
`p_n(r_n) = f(r)`.

Notes on encodings. (a) In the plain case `p_j` is the standard round polynomial. In the
eq-weighted case the standard round polynomial is `eq(tau_<j, r_<j) * eq(tau_j, X) * p_j(X)`; it
is a function of `p_j` and public values, so zero knowledge of the reduced form implies zero
knowledge of the standard form. (b) `p_j` may be sent as `d_j + 1` coefficients, as values at
`d_j + 1` distinct points (needs `q >= d_j + 1`), or with one coefficient dropped and recovered
from the check: these are invertible affine images of each other given the public data, so every
statement below holds for each. The proofs and the tests use coefficients. (c) In characteristic
2 the plain functional kills constants: `lam(1) = 0`, `lam(X^e) = 1` for `e >= 1`. So the check
`p(0) + p(1) = t` says "the non-constant coefficients sum to `t`" and leaves the constant
coefficient free.

Not covered by this section's variant: a first round over a larger domain ("univariate skip").
Theorem 1 is stated for arbitrary nonzero functionals `lam_j` and covers it on paper (remark
3.6); it was not tested.

### 1.2 Masked protocol

A **mask family** `M` is a linear space of polynomials in `F[x]_{<=d}` with a fixed basis; "a
uniform mask" is a uniform combination of the basis.

    0. The prover holds f. It samples g uniform in M, independent of everything else, and
       commits to g (section 5 says what the commitment must provide).
    1. Prover sends G = Lam(g).
    2. Verifier sends rho in F  (F \ {0} if the soundness analysis wants it; zero knowledge holds for every rho).
    3. Sumcheck on h = rho f + g with claim rho S + G: messages s_1..s_n, challenges r_1..r_n.
    4. Final check s_n(r_n) = rho f(r) + g(r), in one of two forms:
         variant O  the verifier obtains g(r) from the mask commitment and f(r) from the
                    witness commitment;
         variant R  the claim "rho f(r) + g(r) = s_n(r_n)" is handed to a downstream reduction
                    that proves it without revealing f(r) or g(r) separately.

View of the verifier, as far as this lemma is concerned:

    variant O:  (G, rho, s_1, r_1, ..., s_n, r_n, g(r))        with f(r) known to the verifier
    variant R:  (G, rho, s_1, r_1, ..., s_n, r_n)

What is **not** in this view and is handled elsewhere: the commitment to `g` and its opening
(section 5), the opening of `f(r)` and the question whether `f(r)` itself may be known (the
column-evaluation blinding, `yugen-zk-b` item Z-3), the witness commitment's queries (Z-1, Z-6).

Soundness (P, standard argument, not the subject here): `g` is fixed before `rho`; if
`Lam(f) != S` then `Lam(rho f + g) = rho S + G` holds for at most one `rho`, so the masked
protocol adds `1/q` to the sumcheck's `sum_j d_j / q`.

### 1.3 Zero-knowledge definition

**Definition (perfect zero knowledge with one query).** The masked protocol is perfect
zero-knowledge with one query if there is an efficient simulator `Sim` such that for every `f`
and every deterministic verifier strategy `V*` (which maps the messages so far to the next
challenge), the output of `Sim`, given `S`, the code of `V*`, and oracle access to `f` that it
uses **once, at the point `r`** fixed by the run, is distributed identically to the view of
`V*` in a real run with a uniform mask. In variant R the simulator makes **no** query to `f`.

The honest-verifier case is the special case of constant strategies: for every fixed
`(rho, r)` the distribution of the prover's messages equals that of `Sim(S, rho, r, f(r))`.
Both systems are compiled by Fiat-Shamir, where honest-verifier zero knowledge is what the
compilation uses (Published: Ben-Sasson, Chiesa, Spooner, "Interactive Oracle Proofs", ePrint
2016/116, Theorem 7.1 and Lemma 7.5: an honest-verifier statistical zero-knowledge public-coin
IOP compiles, with the Merkle tree with privacy of its Section 3.2, to a statistical
zero-knowledge non-interactive proof in the explicitly-programmable random oracle model;
`zk-composition.md` section 6 has the conditions and the error term).

"Perfect" means equality of distributions. Where a construction has excluded challenges, the
statement is statistical with distance at most the probability of the excluded event.

---

## 2. Why Libra's mask fails in characteristic 2

Libra's mask (Published: ePrint 2019/317, Section 4.1, Construction 1 step 1, read
2026-11-19): `g(x) = a0 + g_1(x_1) + .. + g_l(x_l)`, `g_i(x_i) = a_{i,1} x_i + .. + a_{i,d} x_i^d`,
all coefficients uniform, `1 + l d` in total; the verifier's `rho` is drawn from `F*` and the
sumcheck runs on `f + rho g`. The paper's Theorem 3 (zero knowledge) states no condition on the
characteristic; its proof asserts that the view imposes `l d + 1` independent linear
constraints on the coefficients and that these are matched by the mask's `l d + 1`
coefficients, without proving the independence. The paper's field is a prime field throughout
(Protocol 2: "Let F be a prime field"; Constructions 3 and 4; a 254-bit prime in the
implementation), so characteristic 2 is outside its setting and what follows does not
contradict it. The failure in characteristic 2 is stated in ePrint 2026/391 (revision of
2026-11-16), Section 2.5: the partial sums of that mask over the hypercube "vanish in all but
the last two rounds". The computation below was made here before that text was read and agrees
with it; the exact counts are this project's. Below `deg g_i <= d_i`.

Plain sum, any field. Summing over the `n - j` remaining cube variables multiplies everything
that does not depend on them by `2^(n-j)`:

    p_j^g(X) = 2^(n-j) * ( a0 + sum_{i<j} g_i(r_i) + g_j(X) )  +  2^(n-j-1) * sum_{i>j} ( g_i(0) + g_i(1) )
    G        = 2^n a0 + 2^(n-1) sum_i ( g_i(0) + g_i(1) )

In odd characteristic `2^(n-j)` is invertible and `g_j` masks round `j`. In characteristic 2
(P; C in `results/rank.txt`, `results/leak.txt`):

    G = 0                                  (n >= 2)
    p_j^g = 0                              for j <= n - 2
    p_{n-1}^g = g_n(0) + g_n(1)            a constant
    p_n^g(X) = a0 + sum_{i<n} g_i(r_i) + g_n(X)

So rounds `1 .. n-2` are sent in the clear (times the public `rho`), round `n-1` is masked in its
constant coefficient only, and only the last round is masked. The image of the map "mask
coefficients -> view" has dimension `d + 1` for every `n >= 2`, where `1 + n d` is needed (C:
rank 3 of 82 coefficients at `n = 27, d = 2`; rank 4 of 109 at `n = 27, d = 3`).

**Worked example.** `n = 3`, `d = 2`, any `GF(2^k)`. Take

    f  = x1 x2 x3            f' = x1^2 x2 x3

They agree on the whole cube (`x1^2 = x1` there), so `S = 1` for both and no statement about
cube values separates them. Their first round polynomials differ:

    p_1^f(X) = sum_{b2,b3} X b2 b3 = X            p_1^{f'}(X) = X^2

With Libra's mask, `G = 0` and `s_1 = rho * p_1 + 0`: the verifier reads `rho X` or `rho X^2`
and tells the witnesses apart with certainty after one message. With the staircase mask of
section 3, `s_1 = rho p_1 + ghat_1(X) + (a_21 + a_22)`: its three coefficients are uniform
subject to `(coefficient of X) + (coefficient of X^2) = rho + G`, the same law for both
witnesses.

In general the verifier reads from each unmasked round the coefficient vector of `p_j^f`:
`d_j` field elements per round that are linear functionals of the witness (one linear relation
is the public check). For multilinear `f` (`d = 1`) that is one element per round: the mask
fails for `d = 1` as well once `n >= 3` (C: `results/leak.txt`, `n = 3, d = 1`: 28 of 40
witness pairs with equal `S` and equal `f(r)` are told apart over GF(4); the earlier experiment
only ran `d = 1` at `n = 2`, where nothing beyond `(S, f(r))` is exposed).

Why "weights" repair it: a term `g_j(x_j) * U(x_{j+1}, .., x_n)` contributes
`g_j(X) * (lam_{j+1} .. lam_n U)` to round `j`. Libra uses `U = 1`, whose cube sum is `2^(n-j)`.
Any `U` whose cube sum is 1 works; `U = x_{j+1} ... x_n` is the simplest, since
`lam(x) = 0 + 1 = 1`.

---

## 3. The mask theorem

### 3.1 Statement

Fix nonzero functionals `lam_j` on `F[X]_{<=d_j}` (section 1.1; the proof uses nothing else
about them). For each `k = 2..n` fix a polynomial `u_k(X)` of degree at most `d_k` with

    lam_k(u_k) = 1 .                                                             (H-u)

Such `u_k` exists because `lam_k != 0`. Define the mask family

    M_u = { g(x) = c + sum_{j=1..n} g_j(x_j) * prod_{k>j} u_k(x_k) :  c in F,  g_j in F[X]_{<=d_j} }

parametrised by `N = 1 + sum_j (d_j + 1)` coefficients. For a challenge vector `r` let

    V_r = { (G, p_1, .., p_n) :  lam_1(p_1) = G,   lam_j(p_j) = p_{j-1}(r_{j-1}) for j = 2..n }

the space of "mask views that pass the round checks". Each condition fixes `lam_j(p_j)`, and
`lam_j != 0`, so `dim V_r = 1 + sum_j d_j`. Let `P_r(g) = (Lam(g), p_1^g, .., p_n^g)`;
`P_r(g)` lies in `V_r` for every polynomial `g` (completeness of the sumcheck).

**Theorem 1 (P).** For every `r in F^n`, the linear map `P_r : F^N -> V_r` (coefficients of a
mask in `M_u` to its view) is surjective, and every fibre has exactly `q^n` elements. Hence for
a uniform mask, `P_r(g)` is uniform on `V_r`, for every `r`. Moreover `g(r) = p_n^g(r_n)`.

No hypothesis on `q`, on the characteristic, or on `r`.

### 3.2 Proof

**Lemma 1 (round polynomials of the mask) (P).** With

    D_1 = 0,   D_{j+1} = g_j(r_j) + u_j(r_j) D_j          (u_1 := any polynomial; it is multiplied by D_1 = 0)
    K_n = c,   K_j = lam_{j+1}(g_{j+1}) + lam_{j+1}(1) K_{j+1}

one has, for every `j`,

    p_j^g(X) = g_j(X) + D_j u_j(X) + K_j ,          Lam(g) = lam_1(g_1) + lam_1(1) K_1 .

*Proof.* For a product `t(x) = prod_k t_k(x_k)` the definition gives
`p_j^t(X) = prod_{k<j} t_k(r_k) * t_j(X) * prod_{k>j} lam_k(t_k)`. Apply it to each term of `g`.
Term `i < j`: factors `g_i(r_i) prod_{i<k<j} u_k(r_k)`, then `u_j(X)`, then
`prod_{k>j} lam_k(u_k) = 1` by (H-u). Their sum over `i < j` is `D_j u_j(X)`, with
`D_j = sum_{i<j} g_i(r_i) prod_{i<k<j} u_k(r_k)`, which satisfies the stated recursion. Term
`i = j`: `g_j(X)`. Term `i > j`: `prod_{j<k<i} lam_k(1) * lam_i(g_i) * 1`, a constant; the term
`c` gives `c prod_{k>j} lam_k(1)`. The constants add up to `K_j`, which satisfies the stated
recursion. The formula for `Lam(g)` is the same computation with no free variable. ∎

*Proof of Theorem 1.* Fix `r` and a target `(G, p_1, .., p_n) in V_r`. Choose any
`kappa = (kappa_1, .., kappa_n) in F^n`. Define, for `j = 1, 2, .., n` in this order,

    g_j := p_j - D_j u_j - kappa_j          (D_j computed from g_1..g_{j-1} by Lemma 1's recursion)
    c   := kappa_n .

Claim: `K_j = kappa_j` for all `j`. Downward induction. `K_n = c = kappa_n`. For `j < n`:

    lam_{j+1}(g_{j+1}) = lam_{j+1}(p_{j+1}) - D_{j+1} lam_{j+1}(u_{j+1}) - kappa_{j+1} lam_{j+1}(1)
                       = p_j(r_j) - D_{j+1} - kappa_{j+1} lam_{j+1}(1)                    (target in V_r; H-u)
                       = [ g_j(r_j) + D_j u_j(r_j) + kappa_j ] - [ g_j(r_j) + u_j(r_j) D_j ] - kappa_{j+1} lam_{j+1}(1)
                       = kappa_j - kappa_{j+1} lam_{j+1}(1)

so `K_j = lam_{j+1}(g_{j+1}) + lam_{j+1}(1) K_{j+1} = kappa_j - lam_{j+1}(1) (kappa_{j+1} - K_{j+1}) = kappa_j`.

By Lemma 1, `p_j^g = g_j + D_j u_j + K_j = g_j + D_j u_j + kappa_j = p_j`, and
`Lam(g) = lam_1(g_1) + lam_1(1) K_1 = lam_1(p_1) - lam_1(1) kappa_1 + lam_1(1) kappa_1 = G`
(using `D_1 = 0` and the target's first condition). So every target has at least `q^n`
preimages, one for each `kappa` (different `kappa` give different `c` or different `g_j`).
Counting: `q^N = q^(1 + sum (d_j + 1)) = |V_r| * q^n`, so every fibre has exactly `q^n` elements
and `P_r` is onto. A linear map with equal fibres sends the uniform distribution to the uniform
distribution on its image. Finally `p_n^g(X) = g(r_1, .., r_{n-1}, X)` by definition (no
variables remain), so `g(r) = p_n^g(r_n)`. ∎

(The signs are written for any characteristic; in characteristic 2 they are all `+`.)

### 3.3 Corollary A: the staircase mask (plain sum, characteristic 2)

Plain functional, characteristic 2: `lam(1) = 0`, `lam(X) = 1`. Take `u_k = x_k`. The family is

    g(x) = c + sum_j g_j(x_j) x_{j+1} ... x_n .

Its parametrisation is redundant: the constant coefficient of `g_j` (`j < n`) multiplies the
monomial `x_{j+1} ... x_n`, which is also the linear term of `g_{j+1}` times `x_{j+2} .. x_n`; the
constant of `g_n` duplicates `c`. Dropping the constants leaves the **staircase mask**

    M_stair = { c + sum_{j=1..n} ghat_j(x_j) x_{j+1} ... x_n :  ghat_j(X) = a_{j,1} X + .. + a_{j,d_j} X^{d_j} }

with `N = 1 + sum_j d_j` coefficients, the same set of polynomials. `dim V_r = N`, so:

**Corollary A (P; C).** For every `r`, `P_r : F^N -> V_r` is a **bijection** on the staircase
mask. Explicitly, with `gam_j = a_{j,1} + .. + a_{j,d_j}` and `gam_{n+1} := c`:

    G = gam_1
    p_j^g(X) = ghat_j(X) + D_j X + gam_{j+1} ,      D_1 = 0,  D_{j+1} = ghat_j(r_j) + r_j D_j
    g(r) = p_n^g(r_n)

The constant coefficient of round `j` is masked by the next round's coefficient sum (and the
last by `c`); the other coefficients by `ghat_j`. The prover computes all mask round
polynomials in `O(sum_j d_j)` field operations.

Computation (C): rank `1 + n d` for **every** `r in F^n` over GF(4) (`n <= 5`, `d <= 3`) and
GF(16) (`n <= 3`, `d <= 3`), and for mixed degrees; rank `1 + n d` at `n in {8, 16, 23, 25, 27}`,
`d in {2, 3}` over GF(2^8) for 12 random and 4 adversarial `r` (all zeros, all ones, alternating,
`(1,0,..,0)`), and at `(23, 2)`, `(27, 3)` over GF(2^128) (`results/rank.txt`).

The multilinear case: `d = 1` gives `g = c + sum_j a_j x_j x_{j+1} ... x_n`, `n + 1` coefficients.

### 3.4 Corollary B: Libra's mask is perfect for an eq-weighted sumcheck

For `lam_j(p) = (1 + tau_j) p(0) + tau_j p(1)`: `lam_j(1) = 1` for every `tau_j`, including
`tau_j in {0, 1}`. Take `u_k = 1`. Then `M_u = { c + sum_j g_j(x_j) }` is Libra's mask.

**Corollary B (P; C).** In a sumcheck of `sum_x eq(tau, x) * ( rho C(x) + g(x) )` with reduced
round messages, Libra's mask gives `P_r` onto `V_r` for every `tau` and every `r`, in every
characteristic. (C: rank for all `tau` and all `r` over GF(4) at several degree profiles;
exact distributions over GF(4) and GF(16), `results/exact.txt` part B.)

The mask must sit **inside** the eq factor: the summand is `eq(tau, x) (rho C(x) + g(x))` and
the final check is `p_n(r_n) = rho C(r) + g(r)` on the reduced message. A mask added outside the
eq factor is a plain-sum mask and needs Corollary A.

### 3.5 Corollary C: other masks

- **Odd characteristic, plain sum** (P): `lam(1) = 2`, take `u_k = 1/2`: the family is
  `c + sum_j 2^(-(n-j)) g_j(x_j)`, Libra's mask up to rescaling each `g_j`. Theorem 1 recovers
  the odd-characteristic lemma, and it shows exactly where characteristic 2 breaks it:
  `lam(1) = 0` forbids a constant `u_k`.
- **Full random polynomial** (P; C at toy sizes): all `prod_j (d_j + 1)` monomials, the mask of
  [BCFGRS16]/[CFS17] (S, section 10). It contains `M_stair`, so `P_r` is onto. It costs
  `(d + 1)^n` coefficients: `3^27` at the leaf's size. Not usable; listed for completeness.
- **Weighted mask of `yugen-zk-b`**, `g = sum_i g_i(x_i) prod_{k != i} (1 + x_k)` (P; C). Its
  cofactor is a suffix `prod_{k>i} (1 + x_k)` (fine: `lam(1 + x) = 1`) times a prefix
  `prod_{k<i} (1 + x_k)`, which the challenges turn into the scalar `E_i = prod_{k<i} (1 + r_k)`.
  One finds `p_j^g(X) = E_j g_j(X) + (1 + X) * const_j`. If no `r_k = 1` for `k < n`, every
  `E_j != 0` and `P_r` is onto `V_r`; if `r_k = 1` for some `k < n`, then `E_j = 0` for all
  `j > k` and those rounds are `(1 + X) * const`: unmasked. C: over GF(4) and GF(16), for every
  `r`, full rank **exactly** when no `r_k = 1` with `k < n` (`results/rank.txt` part A). It is
  statistically zero-knowledge with distance at most `(n - 1)/q` for an honest verifier, and
  not zero-knowledge against a verifier who may choose `r_k = 1`. The staircase mask has no
  excluded challenge and `n - 1` fewer coefficients; it replaces the weighted mask.

### 3.6 Remark: other summation domains (P, not tested)

The proof of Theorem 1 uses only that each `lam_j` is a nonzero linear functional on
`F[X]_{<=d_j}` and that the total sum factors as `lam_1 .. lam_n`. It therefore holds verbatim
when variable `j` is summed over any set `H_j` with weights, `lam_j(p) = sum_{a in H_j} w_j(a) p(a)`,
provided `lam_j` is not identically zero on degree `<= d_j`. That hypothesis is not automatic in
characteristic 2: for the unweighted sum over an `F_2`-subspace `H` of dimension `s`, the power
sums `sum_{a in H} a^e` vanish for `e < 2^s - 1` and not for `e = 2^s - 1` (M as a theorem; C for
four subspaces of dimension 2 and 3 in GF(16) and GF(256)), so the unweighted functional is zero
unless `d_j >= 2^s - 1`. A univariate-skip round must be checked against this before the theorem is
applied to it.

---

## 4. Zero knowledge of the masked sumcheck

Call a mask family **round-complete** if `P_r` maps the uniform mask to the uniform distribution
on `V_r` for every `r in F^n`. By Theorem 1: `M_u`, the staircase mask, Libra's mask under eq
weights, the full random polynomial.

### 4.1 Simulator

    Sim (variant O), for a deterministic verifier strategy V*, given S and one query to f:
      1. G  <- uniform in F.              rho := V*(G).            t := rho S + G.
      2. for j = 1..n:
           s_j <- uniform in { s in F[X]_{<=d_j} : lam_j(s) = t }         (an affine space of dimension d_j)
           r_j := V*(G, s_1, .., s_j).    t := s_j(r_j).
      3. query v := f(r_1, .., r_n).     output (G, rho, s_1, r_1, .., s_n, r_n,  g(r) := t - rho v).

    Variant R: the same without step 3's query and without the last entry.

It uses `1 + sum_j d_j` uniform field elements. Sampling `s_j` in the plain characteristic-2
case: choose the constant coefficient and the coefficients of degree `2..d_j` uniformly, set the
coefficient of `X` so that the non-constant coefficients sum to `t`. Code:
`zk-lemma/sumcheck.py`, `simulate` and `simulate_adaptive`.

### 4.2 Theorem

**Theorem 2 (P; C).** Let `M` be round-complete. Then the masked sumcheck with the mask
commitment replaced by an ideal functionality that reveals only `G` and (variant O) `g(r)` is
perfect zero-knowledge with one query (variant O) or with no query (variant R), against every
verifier strategy, for every field size, every `f in F[x]_{<=d}` and every `rho` including 0.

*Proof.* Fix `f` and a deterministic `V*`. Call a sequence
`T = (G, rho, s_1, r_1, .., s_n, r_n)` *consistent* if its challenges are those `V*` computes
from its messages, and *accepting* if `lam_1(s_1) = rho S + G` and
`lam_j(s_j) = s_{j-1}(r_{j-1})` for `j >= 2`.

Real run. The view is a function of the mask `g`. Fix a consistent `T` and let `r` be its
challenge vector. By induction on the rounds, the real run with mask `g` produces `T` if and
only if `Lam(g) = G` and `rho p_j^f + p_j^g = s_j` for all `j`, where `p_j^f`, `p_j^g` are
computed with `T`'s challenges; that is, iff

    P_r(g) = ( G, s_1 - rho p_1^f, .., s_n - rho p_n^f ) .                           (*)

The vector `(S, p_1^f, .., p_n^f)` satisfies the round checks with head `S` (completeness of the
plain sumcheck for `f`), so the right side of (*) lies in `V_r` if and only if `T` is
accepting. By round-completeness, `Pr_g[(*)] = q^(-(1 + sum d_j))` if `T` is accepting and `0`
otherwise. So the real view is uniform on the set of consistent accepting sequences, and its
last entry is `g(r) = p_n^g(r_n) = s_n(r_n) - rho f(r)`.

Simulated run. `Sim` outputs only consistent accepting sequences, and outputs each with
probability `q^(-1) * prod_j q^(-d_j)`: `G` is uniform, and given the past, `s_j` is uniform on
an affine space of dimension `d_j`. Its last entry is `s_n(r_n) - rho f(r)`.

The two distributions are equal. ∎

**Corollary (statistical version) (P).** If `P_r` maps the uniform mask to uniform on `V_r`
only for `r` outside a set `B`, the honest-verifier view is within statistical distance
`Pr_r[r in B]` of the simulator's. For the weighted mask `B = { r : r_k = 1 for some k < n }`
and the bound is `(n - 1)/q`.

Computation (C), `results/exact.txt`: for fixed `(f, rho, r)` **every** mask and **every**
simulator tape is enumerated and the two distributions compared as exact count tables.

| Field | `(n, d)` | challenge vectors | result for the staircase mask |
|---|---|---|---|
| GF(4) | `n = 1,2` with `d = 1,2,3`; `(3,1)`, `(3,2)` | all `r in F^n`, `rho in {0, 1, 2}`, 2 witnesses | equal in every case |
| GF(4) | `(3,3)` | 9 `r` (5 adversarial), `rho in {1,2}` | equal in every case |
| GF(16) | `(1,1)`, `(1,2)`, `(1,3)` | all `r` | equal in every case |
| GF(16) | `(2,1)`, `(2,2)`, `(3,1)` | 64, 9 and 50 `r` | equal in every case |

The same holds for the redundant staircase family, the full random polynomial, Libra's mask and
the general-weight family under eq weights and under arbitrary weight pairs (parts B, C), and
for two deterministic adaptive verifier strategies over GF(4), one of which steers challenges
to 1 (part D, run from the definition, cube sums of polynomial evaluations). The packed
enumeration is checked against the definition and against the verifier's acceptance before any
comparison (`selfcheck`).

Negative controls (C): the same harness reports distance up to `0.996` for Libra's mask and a
positive distance for the weighted mask exactly at challenge vectors with some `r_k = 1`,
`k < n`; `results/leak.txt` compares two witnesses with equal `S` and equal `f(r)` directly and
separates them under Libra's mask (all pairs at `(2,3)`, `(3,2)` over GF(4)) and never under the
staircase mask.

### 4.3 Hypotheses, all of them

| # | Hypothesis | Used for |
|---|---|---|
| H1 | `d_j >= 1`; each `lam_j` nonzero on degree `<= d_j` | `dim V_r`, existence of `u_k` |
| H2 | the mask is uniform in a round-complete family, with the degree bounds of the summand (`deg_j g <= d_j`, and the staircase needs degree 1 in later variables, which `d_j >= 1` gives) | Theorem 1 |
| H3 | the mask is independent of the witness, of the witness commitment's randomness, of every blinding row or pad, and of every other mask; one fresh mask per sumcheck instance | the probability in (*) |
| H4 | the verifier learns about `g` only `G`, the round messages, and (variant O) `g(r)`: the commitment and its opening reveal no other function of the mask coefficients | section 5 |
| H5 | (variant O) the simulator may be given `f(r)`: either `f(r)` is public by design or the layer above makes it simulatable | section 5.4 |
| H6 | `g` is committed before `rho` | soundness only |

No hypothesis on `q` for zero knowledge. Field size enters soundness (`(1 + sum d_j)/q`) and
the excluded events of sections 5, 7, 8.

Reusing one mask in two sumchecks breaks H3: the difference of the two views cancels the mask.

---

## 5. The final evaluation and the commitment to the mask

### 5.1 How much of the mask the verifier learns

The view contains `1 + sum_j d_j` independent linear functionals of the mask's coefficient
vector (the image `V_r`). For the staircase mask that is **all of it**: the map is a bijection,
the mask is a one-time pad with no slack. `g(r)` is not a further functional (`g(r) = p_n^g(r_n)`).

**Proposition 3 (P).** For the staircase mask, every linear functional `ell` of the mask
coefficients equals `<mu, P_r(g)>` for some `mu`. Hence an additional value `ell(g)` given to
the verifier equals `<mu, (G, s)> - rho <mu', (p_1^f, .., p_n^f)>`: it reveals the linear
functional `<mu', p^f>` of the unmasked round polynomials of the witness, unless `mu' = 0` on
the differences of admissible witnesses. `ell = Lam` (value `G`) and `ell = ev_r` (value `g(r)`,
when `f(r)` is known) are the only harmless directions.

Consequence: the opening of `g(r)` must reveal **nothing** about the mask coefficients beyond
`g(r)`. Extra coefficients in `g` cannot pay for a leaky opening, because every nonzero
polynomial added to `g` shows up in the round messages (`p_n^g = 0` for all `r` forces `g = 0`).
The slack has to live in the commitment layer.

### 5.2 What the commitment must provide

| # | Requirement | Reason |
|---|---|---|
| C1 | binding before `rho` | H6 |
| C2 | hiding: the commitment string and every query answered on it are simulatable without the mask | H4 |
| C3 | an evaluation (or linear-functional) opening that is itself zero-knowledge: it reveals `g(r)` and nothing else | Proposition 3 |

Three ways to meet C3, in increasing reliance on other components:

1. **Variant R (residual hand-off).** Never open `g(r)`. The claim
   `rho f(r) + g(r) = s_n(r_n)` goes to the polynomial commitment's own zero-knowledge
   evaluation reduction as one claim on the pair (witness oracle, mask oracle). This is how the
   pinned prime-field code ends a masked batch (S: `sumcheck/src/zk/verifier.rs`, "Residual
   claim `target = h_k(gamma_k)`, fed to the downstream committed-sumcheck reduction"). The
   sumcheck simulator then needs no query to `f`. Zero knowledge of the downstream reduction in
   characteristic 2 is (U) here; it is `yugen-zk-b` items Z-1 and Z-6.
2. **Linear opening gadget (section 5.3).** The mask coefficients sit in a committed column;
   the gadget turns any linear claim on them into two evaluation claims at a random point, both
   uniform. It needs from the commitment only what the witness columns already need:
   multilinear evaluations at a random point that reveal nothing but the values.
3. **A second, small commitment scheme** for the pads (the Longfellow route named in
   `yugen-zk-b`; that it runs over GF(2^128) is (M)). Not analysed here.

### 5.3 Linear opening gadget

All masks of a proof (and the layer blinders of section 7) are concatenated into one vector
`a in F^N`. Every value the verifier needs from them is a linear functional with public
weights: `g(r) = <a, W(r)>` (for the staircase mask `W(r)` has entries `1` and
`r_j^e r_{j+1} .. r_n`), `G = <a, omega>`, and the claims of section 7. Batch the `m` claims
`<a, w_i> = v_i` with a random `theta`: `w = sum theta^i w_i`, `v = sum theta^i v_i`.

    Committed, with the witness, before any challenge:
        column A = (a, t)   length L = 2^l,   t = pad of L - N >= 1 uniform elements
        column B            length L,         uniform
    1. Prover sends beta = <B, w>.            (w extended by zeros over the pad)
    2. Verifier sends c in F.
    3. Prover sends the whole vector u = B + c A.
    4. Verifier sends z in F^l.
    5. The commitment opens the multilinear evaluations A(z) and B(z).
    6. Verifier checks   <u, w> = beta + c v    and    u(z) = B(z) + c A(z).

**Lemma 3 (P; C).** Fix `a, w, c, z`. If some pad position `i` has `eq(z, i) != 0`, the view
`(beta, u, A(z), B(z))` is distributed identically to the output of

    Sim(v):  u <- uniform in F^L;  alpha <- uniform in F;  output ( <u, w> + c v,  u,  alpha,  u(z) + c alpha ).

*Proof.* For fixed `t`, `B -> u = B + c (a, t)` is a bijection, so `u` is uniform and
independent of `t`. `A(z) = sum_{i<N} a_i eq(z, i) + sum_pad t_i eq(z, i)` is uniform over the
choice of `t` when some pad weight is nonzero, and independent of `u`. So `(u, A(z))` is uniform
on `F^(L+1)`. The other two entries are functions of it: `beta = <B, w> = <u, w> + c <a, w> =
<u, w> + c v` (the pad has weight 0 in `w`), and `B(z) = u(z) + c A(z)`. ∎

With one pad element at the all-ones index, the excluded event is `z_1 z_2 .. z_l = 0`,
probability at most `l/q` (P). Soundness (P, sketch): if `u != B + c A` the check at `z` fails
except with probability `l/q` (Schwartz-Zippel, multilinear); otherwise
`<u, w> - beta - c v = (<B, w> - beta) + c (<a, w> - v)` vanishes for at most one `c` unless
`<a, w> = v`; batching adds `(m - 1)/q`.

Composition with Theorem 2 (P): `B` and `t` are fresh and independent (H3), and Lemma 3's
simulator needs only `v`, which is a function of the sumcheck views. So the joint view
(sumcheck views, gadget view) is simulated by running the two simulators in sequence.

Computation (C), `results/gadget.txt`: all prover randomness and all simulator randomness
enumerated over GF(4) (lengths 4 and 8, one or two pad elements) and GF(16) (length 2), every
`c` and every `z` (a sample of `z` at length 8): equal in all 1,876 cases with a nonzero pad
weight, different in all 356 cases with zero pad weight.

What Lemma 3 leaves to the commitment (U here): the evaluation proofs for `A(z)` and `B(z)` and
the code-symbol queries on the two columns must be simulatable. `A(z)` and `B(z)` are already
uniform given the rest of the view, so the two columns ask of the commitment exactly what a
blinded witness column asks. The gadget is this document's own construction, in the family of
the linear tests of Ligero-type arguments (M); it has not been reviewed.

### 5.4 The value `f(r)`

Theorem 2's simulator is handed `f(r)`. Whether that is acceptable is decided outside the
lemma: (a) in a zerocheck, `f(r) = C(column evaluations at r)`, and the column evaluations are
made uniform by blinding rows (`yugen-zk-b` Z-3); the simulator samples them and computes
`f(r)`; (b) in a commitment fold round, `f(r)` is the next round's claim; variant R keeps it
unopened. This document proves neither (a) nor (b).

---

## 6. Cost

Field element: 16 bytes (GF(2^128)). Staircase mask, uniform degree `d`.

| `n` | `d` | mask coefficients `1 + n d` | weighted mask `n (d + 1)` | full random `(d+1)^n` |
|---|---|---|---|---|
| 23 | 2 | 47 | 69 | 9.4e10 |
| 23 | 3 | 70 | 92 | 7.0e13 |
| 25 | 2 | 51 | 75 | 8.5e11 |
| 25 | 3 | 76 | 100 | 1.1e15 |
| 27 | 2 | 55 | 81 | 7.6e12 |
| 27 | 3 | 82 | 108 | 1.8e16 |

Extra proof data per masked sumcheck:

| Item | Elements | Note |
|---|---|---|
| `G` | 1 | |
| round messages | 0 | still `d` coefficients per round; the dropped coefficient is still recovered from the check |
| `g(r)` | 0 | computed by the verifier as `s_n(r_n) - rho f(r)` and added to the linear claims |
| variant R total | 1 | 16 bytes, plus whatever the downstream reduction costs |

Extra proof data per proof for the linear opening gadget (shared by all masks; `N` = total mask
and blinder coefficients): `beta` (1), `u` (`N + 1`), `A(z)`, `B(z)` (2): `N + 4` elements.

| One sumcheck of | `G` + gadget, elements | bytes |
|---|---|---|
| `n = 23, d = 2` | 1 + 51 = 52 | 832 |
| `n = 23, d = 3` | 75 | 1,200 |
| `n = 25, d = 2` | 56 | 896 |
| `n = 25, d = 3` | 81 | 1,296 |
| `n = 27, d = 2` | 60 | 960 |
| `n = 27, d = 3` | 87 | 1,392 |

Not counted: the commitment's own cost for two more evaluation claims at one more point `z`
(it depends on the commitment's batching and is not derived here).

Extra commitment: two columns of `L = 2^ceil(log2(N + 1))` field elements (128 elements each
for one sumcheck at these sizes), placed in the witness commitment; no extra Merkle root if they
share a table. Prover work: `O(n d)` field operations per sumcheck for the mask's round
polynomials (Corollary A's recursion), `O(L)` for the gadget. Soundness: `+ 1/q` per masked
sumcheck, `+ (l + m)/q` for the gadget.

---

## 7. GKR layer reductions

### 7.1 What leaks

A layered product or fraction argument proves, layer by layer,

    v_{i+1}(z) = sum_x eq(z, x) * v_i(x, 0) * v_i(x, 1)                 (product tree)

(and the analogous pair of identities for numerators and denominators). Each reduction leaks
(1) its sumcheck round polynomials and (2) the **layer claims** `v_i(r, 0)`, `v_i(r, 1)`, sent
so that the verifier can finish the sumcheck and form the next claim `v_i(r, alpha)`. The
layers are functions of the witness. Theorem 2 removes (1). For (2) the claims must be blinded
and the final check must still be computable from the blinded claims; a product of blinded
values is not a blinded product, so the blinding goes into the summand itself (the idea of
Libra's zero-knowledge GKR: Published, ePrint 2019/317, Section 4.2, equation (7):
`Vdot_i(z) = Vtilde_i(z) + Z_i(z) sum_{w in {0,1}} R_i(z_1, w)` with `Z_i(z) = prod_k z_k (1 - z_k)`
and `R_i` a random bivariate polynomial of variable degree 2, committed with a zero-knowledge
polynomial commitment and opened at two points per layer; Construction 2, Theorem 4. Read
2026-11-19. The construction of 7.2 is **adapted** from it: what changes is stated next).

Libra's multiplier `Z(x) = prod_k x_k (1 - x_k)` over all variables does not fit as is: the
claims here are at points `(r, 0)` and `(r, 1)` with a Boolean last coordinate, where a
multiplier containing that coordinate vanishes, and the top layers have no `x` variable at all.

### 7.2 Construction

Give every layer one extra **dummy variable** `y`, on which the true layer does not depend, and
two blinding constants per claimed polynomial:

    vhat_i(y, x, b) = v_i(x, b) + y (1 + y) * ( c_{i,0} + c_{i,1} b )

`vhat_i = v_i` whenever `y in {0, 1}`; `vhat_i` is linear in `b`; its degree in `y` is 2. The
constants `c_{i,0}, c_{i,1}` are uniform, part of the mask vector `a` of section 5.3, committed
before any challenge.

Reduction from a claim on `v_{i+1}(z)` to layer `i` (`z_y` a fresh verifier challenge):

    v_{i+1}(z) = sum_{y in {0,1}} sum_x  eq((z_y, z), (y, x)) * vhat_i(y, x, 0) * vhat_i(y, x, 1)       (**)

True because the summand is evaluated at Boolean `y` only and `sum_y eq(z_y, y) = 1`. The
summand has degree 5 in `y` and 3 in each `x_k` (4 and 2 with reduced eq messages). Run the
masked sumcheck of section 1.2 on (**) with a staircase mask of degrees `(5, 3, .., 3)`
(`1 + 5 + 3 m` coefficients for `m` variables `x`), or Libra's mask with reduced messages
(Corollary B).

At the end, with challenges `(r_y, r)`, the prover sends the **blinded claims**

    A_0 = vhat_i(r_y, r, 0),     A_1 = vhat_i(r_y, r, 1)

and the verifier finishes the sumcheck with `f(r_y, r) = eq(..) A_0 A_1`, computed from the
blinded claims alone. It samples `alpha` and forms `Ahat = (1 + alpha) A_0 + alpha A_1`. With
`Z = r_y (1 + r_y)`:

    v_i(r, alpha) = Ahat + Z * ( c_{i,0} + alpha c_{i,1} )

The verifier never learns the right-hand correction. The next reduction's masked claim is

    Lam(rho f' + g') = rho * v_i(r, alpha) + G' = rho * Ahat + Gtilde ,     Gtilde := G' + rho Z ( c_{i,0} + alpha c_{i,1} )

so the prover sends `Gtilde` **in place of** `G'` (after `rho`), and "`Gtilde` equals this
linear functional of the committed mask vector" joins the linear claims proved by the gadget.
Soundness is unchanged (P, sketch): `a` is committed first, so `G'` and the correction are
determined before `rho`; if the linear claim holds, the sum claim is the intended one.

The top of the tree is the same reduction with no `x` variable (the dummy variable alone); the
bottom layer is the committed columns themselves, with no blinder: its claims are column
evaluations at `(r, 0)` and `(r, 1)`, which the column blinding must cover (two evaluation
points per column for this purpose).

A fraction layer (numerator and denominator) uses the same construction with four blinded
claims and four constants per layer.

### 7.3 Simulator and proof

    Sim, given the public output of the tree and the leaf claims L_0, L_1:
      for each layer from the top:   A_0, A_1 <- uniform;
                                     (Gtilde, s) <- the sumcheck simulator of section 4.1 with claimed
                                     value [output, or the previous layer's Ahat] and final value
                                     eq(..) A_0 A_1   (for the last reduction: eq(..) L_0 L_1).

**Lemma 4 (P; C at one size).** Fix the witness and all challenges, with `r_y notin {0, 1}`
in every reduction. Under H3 (all masks and blinders uniform and independent), the view of the
chain is distributed identically to `Sim`'s output.

*Proof.* The blinders enter the view in two ways. (i) The blinded claims: `(A_0, A_1) =
(v_i(r,0), v_i(r,1)) + Z (c_{i,0}, c_{i,0} + c_{i,1})`, a bijective affine image of
`(c_{i,0}, c_{i,1})` since `Z != 0`; so the pairs are uniform and independent across layers.
(ii) The summands `f_i` (through `vhat_i`) and the shifts `Gtilde - G'`. Condition on all
blinders. Then each summand `f_i` is a fixed polynomial of the right degrees, the masks are
still uniform and independent, and by Theorem 1 the pair `(G'_i, P_r(g_i))` is uniform on
`V_r`; hence `(Gtilde_i, s^(i)) = (G'_i + shift_i, rho p^{f_i} + p^{g_i})` is uniform on the set
of sequences that pass the round checks with head `rho Ahat_{i+1} + Gtilde_i` (the shift is
exactly what turns the head `rho v + G'` into `rho Ahat + Gtilde`). That set depends on the
blinders only through the `A`'s. So, given the `A`'s, each reduction's messages are uniform on
a set fixed by the `A`'s and public data, independently across reductions: the law `Sim`
samples. The mask values `g_i(r)` are determined by the view. ∎

For an honest verifier the excluded event has probability at most `2/q` per reduction.

Computation (C), `results/gkr.txt`: a two-reduction chain (4 leaves) over GF(4): for 67
(witness, challenge) cases with `Z != 0`, over all 16 blinders, all `4^6` masks of the first
reduction and all `4^5` of the second: the blinder-to-claims map is a bijection and each
reduction's distribution equals the simulator's (together: equality of the joint
distributions). With `r_y in {0, 1}` the layer claims are published unblinded in all 77 cases
(the excluded event is real). With the blinder off, witnesses with equal output and equal leaf
claims have different published layer claims (40 of 40 pairs).

### 7.4 What remains unproven for GKR

- (U) Fraction (logarithmic-derivative) layers: the construction is stated; no test was run.
- (U) Deeper chains and wider layers were not enumerated; Lemma 4's proof covers them.
- (U) The leaf claims: uniformity of two evaluations per column needs the column-blinding rank
  bound (`yugen-zk-b` T-3).
- (U) The optimised layer sumchecks of the pinned stacks (batched layers, packed round
  messages, univariate skip) are not the textbook reduction (**); each must be matched to
  section 1.1's form before the lemma is applied.
- Alternative that needs none of this: commit the product-tree layers as columns and prove the
  layer relation in the zerocheck (`yugen-proof-b/docs/zero-knowledge.md` Z-4 names it). Then
  only Theorem 2 and the column blinding are used. The cost is the committed layers.

---

## 8. Published cross-table sums (bus terminals)

Each table `t = 1..T` publishes a terminal `sigma_t` (its bus sum or product); the verifier
checks `sum_t sigma_t = 0` or `prod_t sigma_t = 1`. Each `sigma_t` alone is a function of the
witness that anyone can recompute from a candidate witness.

**Lemma 5 (P; C).** Let `e_1 .. e_{T-1}` be uniform and independent of the witness, `e_0 = e_T`
neutral.

1. Additive: `sigmahat_t = sigma_t + e_t + e_{t-1}` (`e_0 = e_T = 0`). The vector `sigmahat`
   is uniform on the hyperplane `{ sum = 0 }`, for every `sigma` with sum 0.
2. Multiplicative: `sigmahat_t = sigma_t e_t / e_{t-1}`, `e_t` uniform nonzero, `e_0 = e_T = 1`.
   For nonzero `sigma` with product 1, `sigmahat` is uniform on the nonzero points of
   `{ prod = 1 }`.
3. Message form (logarithmic-derivative bus): `e_t = 1/(gamma + m_t)` with `m_t` uniform,
   conditioned on `m_t != gamma`. Then `e_t` is uniform on `F \ {0}` and `sigmahat` is within
   statistical distance `(T - 1)/q` of uniform on the hyperplane.

*Proof.* (1) `(e_1..e_{T-1}) -> (sigmahat_1..sigmahat_{T-1})` is a triangular bijection of
`F^(T-1)`; the last coordinate is fixed by the sum. (2) The same with the group `F \ {0}`.
(3) Each `e_t` is at distance `1/q` from uniform on `F`. ∎

The simulator outputs a uniform point of the hyperplane (or of the product-one variety). C,
`results/bus.txt`: exact distance 0 for forms 1 and 2 over GF(4) (`T <= 4`), GF(16) (`T <= 3`),
GF(256) (`T = 2`); form 3 at distance `1/4`, `0.4375`, `0.578` (GF(4), `T = 2, 3, 4`),
`1/16`, `0.121` (GF(16)), `1/256` (GF(256)), each within `(T - 1)/q`.

How the mask reaches the terminals:

- **Form 3 and form 2 by a bus message.** Neighbouring tables `t` and `t + 1` exchange one
  extra bus message with a uniform payload `m_t` held in a committed cell. In a
  logarithmic-derivative bus it adds `1/(gamma + m_t)` to one terminal and removes it from the
  other (form 3); in a grand-product bus it multiplies one by `(gamma + m_t)` and divides the
  other (form 2, conditioned on `gamma + m_t != 0`). Nothing in the protocol changes; it is one
  row per table pair. The event `m_t = gamma` (probability `1/q` per message) makes a term
  undefined: the prover cannot avoid it since `m_t` is committed before `gamma`; it is a
  completeness loss of `(T - 1)/q` and is counted in the statistical distance. This is the
  construction `yugen-zk-b` section 3.4 applied in its prototype; Lemma 5 is its proof at the
  level of the terminals.
- **Fraction terminals.** If the table publishes numerator and denominator `(P_t, Q_t)` with
  `sigma_t = P_t / Q_t`, the denominator `Q_t` (a product over the table's rows) is a second
  witness-dependent value, and the `T - 1` neighbour messages cannot hide `2T` values. Add one
  **self-cancelling pair** per table: the table sends and receives the same uniform payload
  `m'_t`. In characteristic 2 the two fractions cancel in `sigma_t`, and `Q_t` is multiplied by
  `(gamma + m'_t)^2`; squaring is a bijection of `GF(2^k)`, so `Qhat_t` is uniform on
  `F \ {0}` and independent of everything else (P). C: joint distribution of all terminals and
  all denominators equals (message-masked terminals, independent uniform nonzero denominators)
  exactly, GF(4) and GF(16), `T = 2, 3`.
- **Form 1 by a linear claim.** Where the terminal enters the protocol linearly (as the claimed
  value of a sumcheck or GKR output), `sigma_t = sigmahat_t + e_t + e_{t-1}` is handled like
  section 7's correction: the `e_t` are entries of the mask vector and the shift goes into
  `Gtilde`. Distance 0, no completeness loss.

What remains unproven (U): Lemma 5 is about the terminals alone. That the payload cells `m_t`
are otherwise invisible (their column evaluations and commitment queries) is the column
blinding and the hiding commitment; that the rest of each table's bus argument (the layer
claims below the terminal) is simulatable is section 7; the exact published values of each
pinned stack's bus (which of sum, product, numerator, denominator, per-bus or per-table) must
be read from the code and matched to one of the three forms.

---

## 9. Work items and acceptance criteria

| # | Task | Passes when |
|---|---|---|
| W-1 | Replace the weighted mask by the staircase mask in the plain sumchecks of both systems (commitment folds, ring switch); Libra's mask or the staircase mask inside the eq factor for zerochecks with reduced messages | For each sumcheck: the degree profile `d_j` is written down; the mask's round polynomials follow Corollary A's recursion; a unit test reproduces `zk-lemma`'s exact comparison at `n <= 3` on GF(4) or GF(16) through the system's own prover code path |
| W-2 | One fresh mask per sumcheck instance, sampled independently of the witness and of all blinding rows (H3) | A test fails if two instances share mask coefficients; code review of the sampling site |
| W-3 | Mask commitment: variant R, or the linear opening gadget with columns `A` (masks, blinders, pad) and `B` | Variant R: the downstream reduction's simulator test covers the pair (witness, mask). Gadget: `test_gadget.py`'s comparison reproduced through the system's code at toy size; the verifier checks both equations of step 6 |
| W-4 | GKR layers: dummy variable, two blinders per claimed polynomial, `Gtilde` in place of `G`, or the committed-layer alternative | `test_gkr.py`'s comparison reproduced at toy size through the system's code; negative controls (blinder off, `r_y in {0,1}`) fail as in `results/gkr.txt` |
| W-5 | Bus terminals: one mask message per neighbouring table pair; one self-cancelling pair per table where denominators are published | The fourth distinguisher of `yugen-zk-b` T-5 (recompute per-table terminals from a candidate witness) has advantage 0; the list of published bus values per stack is recorded |
| W-6 | Match every sumcheck in both stacks to section 1.1 (domain, weights, message encoding, univariate skip) | A table per stack: sumcheck, `lam_j`, `d_j`, mask used, which corollary applies; any sumcheck that does not fit is listed as open |
| W-7 | External review (E3) of the review sheet, section 11 | The reviewer signs Theorems 1 and 2, Lemmas 3 to 5, or returns a counterexample |

`zk-lemma/` contents: `gf.py` (fields), `sumcheck.py` (protocol, mask families, simulator),
`test_exact.py`, `test_leak.py`, `test_rank.py`, `test_gadget.py`, `test_gkr.py`, `test_bus.py`;
results in `zk-lemma/results/`. Standard library only: `python3 test_*.py` from the directory;
each exits non-zero on failure. (`.venv` there holds `pypdf`, used once to read a paper; no test
needs it.)

---

## 10. Literature: what was read and what was not

| Source | Read? | What it gives |
|---|---|---|
| Chiesa, Forbes, Spooner, "A Zero Knowledge Sumcheck and its Applications" (ePrint 2017/305), arXiv 1704.02086v1 | **body read** (S) | The [BCFGRS16] masked sumcheck, section 2.3: prover sends the evaluation table of a random polynomial `R` "of individual degree at most d", sends `z = sum R`, verifier sends `rho in F*`, sumcheck on `rho F + R`, verifier queries `R` at `c` and outputs the claim `F(c) = (b - R(c))/rho`; "if the verifier makes no queries to R, then the prover's messages are identically distributed to the sumcheck protocol applied to a uniformly random polynomial". Sum over `H^m` for any subset `H` of any finite field: no characteristic hypothesis; the mask is the full random polynomial (exponential size). Theorem 6.4: strong perfect zero knowledge with a single query to `F`. The only remark on characteristic found: a multilinear commitment example "not hiding (in fields of characteristic different than 2)" (section 2.2) and Corollary A.3 for odd prime fields. It does not discuss small masks |
| Xie, Zhang, Zhang, Papamanthou, Song, "Libra: Succinct Zero-Knowledge Proofs with Optimal Prover Computation" (ePrint 2019/317) | **read 2026-11-19** (citation audit; Sections 2.3, 2.4, 4.1, 4.2) | Construction 1: mask `a0 + sum_i g_i(x_i)` with `1 + l d` coefficients, `rho` in `F*`, sumcheck on `f + rho g`, the mask committed with a zero-knowledge polynomial delegation and opened at `r`; Theorem 3 (no characteristic hypothesis stated; independence of the constraints asserted, not proven); the paper's field is a prime field (Protocol 2, Constructions 3, 4). Section 4.2, equation (7): the GKR layer mask `Z_i(z) sum_w R_i(z_1, w)` |
| Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes" (ePrint 2026/391), **revision of 2026-11-16** | **read 2026-11-19** (citation audit; Sections 1.2 to 1.4, 2.5, 3.3.1, 6.1 to 6.3, 7, 9.1 to 9.3, 10.1, 11, Appendix B) | Section 2.5 states that Libra's mask fails when `char(F) = 2`. Definition 6.1 and Lemma 6.2: the mask polynomial `U_sigma = shat_0 + sum_{e=1}^{d_s-2} shat_e * (X_1^e + .. + X_k^e)`, `shat_e = sum_{i=0}^k sigma_{i,e} X_{i+1}..X_k`, `(k+1)(d_s - 1)` coefficients, whose sumcheck transcript is uniform on the consistent transcripts over every finite ring; the proof inverts nothing (each check determines the linear coefficient). Construction 6.4 and Theorem 6.3: the masked sumcheck with `d_s >= 3`, the mask being coordinates of the input oracle's encoding randomness and its final value kept in the output relation (the residual form, variant R here). The paper's implementation is over `GF(2^256)` (Section 1.3) |
| The pinned Plonky3 checkout, `sumcheck/src/zk/mod.rs` (module documentation of its implementation of 2026/391 Construction 6.3) | **read** (S, as a description of the paper by its implementers) | Round polynomial `h_j = 2^(k-j) s_j(X) + 2^(k-j) sum_{l<j} s_l(gamma_l) + 2^(k-j-1) sum_{l>j} (s_l(0) + s_l(1)) + eps * plain_j(X)`: Libra's sum-of-univariates mask with the powers of two of section 2. "Field constraints (Lemma 6.4): Base field characteristic must not be 2". The masked batch ends in a residual claim passed downstream (variant R). So the one construction the pinned code has is stated for odd characteristic only (S). **This is an earlier version of the paper than the one read**: the revision of 2026-11-16 has no Lemma 6.4 that divides by two, its sumcheck is Construction 6.4 with the mask of Definition 6.1, and it covers characteristic 2 |
| Frigo, shelat, "Anonymous credentials from ECDSA" (ePrint 2024/2010) | abstract only | Sumcheck and Ligero; the abstract names neither the field nor the padding. That it pads the sumcheck transcript over GF(2^128) is (M) |
| Gur, O'Connor, Spooner, "Perfect Zero-Knowledge PCPs for #P" (arXiv 2403.11941) | abstract only | A masked sumcheck PCP with "antisymmetric structure within the hypercube"; no statement on characteristic in the abstract |
| Binius (2023/1784), Binius64 repository and documentation | not read (search returned descriptions only; no zero-knowledge note found) | Nothing usable |
| Diamond, Posen, "Polylogarithmic Proofs for Multilinears over Binary Towers" (ePrint 2024/504) | read 2026-11-19 (second citation pass): Sections 1.3, 2.6, 2.7, 3.1, 4.3, 5.2 | No zero-knowledge treatment; its sumchecks (ring switching, binary BaseFold) are unmasked |
| Chiesa, Yogev, "Building Cryptographic Proofs from Hash Functions" (local text extraction, another agent's download) | searched for "zero-knowledge sumcheck", "masking polynomial", "characteristic 2": no match | Nothing found |
| Hyrax (2017/1132), Virgo (2019/1482), Spartan (2019/550) | not fetched | (M): Hyrax and Spartan hide sumcheck messages with homomorphic commitments, Virgo follows Libra's masks over an extension of a Mersenne prime field; none is a binary-field construction |

**Answer to the literature question (corrected by the citation audit of 2026-11-19).** The
question is answered in the literature: ePrint 2026/391, revision of 2026-11-16, states Libra's
failure in characteristic 2 (Section 2.5) and gives a mask with `O(k d_s)` coefficients that is
uniform on the consistent transcripts over every finite field and ring (Definition 6.1,
Lemma 6.2). The pinned Plonky3 code implements an earlier version that excludes characteristic
2. The full-random-polynomial mask of [BCFGRS16]/[CFS17] is characteristic-free and exponential.
Theorem 1 and Corollary A are a different mask family for the same problem (section summary,
"Provenance"); they are Original as far as checked (sources consulted: ePrint 2019/317 Section
4.1, ePrint 2017/305 Section 2.3, ePrint 2026/391 Sections 2.5 and 6, ePrint 2025/1015), are
elementary, and are unreviewed until W-7. The earlier text of this paragraph, which said that no
source notes Libra's failure, was written before the paper could be read and is withdrawn.

---

## 11. Review sheet for an external cryptographer

**Setting.** `F = GF(2^k)`. Polynomials in `n` variables, degree `<= d_j` in `x_j`, `d_j >= 1`.
Summation functionals `lam_j` (nonzero linear functionals on univariate polynomials of degree
`<= d_j`); `Lam = lam_1 .. lam_n`. Plain sum: `lam(p) = p(0) + p(1)`; eq-weighted:
`lam_j(p) = (1 + tau_j) p(0) + tau_j p(1)`. Round message
`p_j^f(X) = lam_{j+1} .. lam_n f(r_<j, X, .)`. `V_r` = vectors `(G, p_1..p_n)` with
`lam_1(p_1) = G`, `lam_j(p_j) = p_{j-1}(r_{j-1})`; `dim V_r = 1 + sum d_j`.
Masked protocol: prover commits `g`, sends `G = Lam(g)`; verifier sends `rho`; sumcheck on
`rho f + g` with claim `rho S + G`; end: `s_n(r_n) = rho f(r) + g(r)`.

**Statements.**

- **Theorem 1.** Let `u_k`, `k = 2..n`, have degree `<= d_k` and `lam_k(u_k) = 1`. For
  `g = c + sum_j g_j(x_j) prod_{k>j} u_k(x_k)` with `c` and all coefficients of the `g_j`
  uniform, and for **every** `r in F^n`: `(Lam(g), p_1^g, .., p_n^g)` is uniform on `V_r`.
- **Corollary A (staircase mask).** Plain sum, characteristic 2, `u_k = x_k`:
  `g = c + sum_j ghat_j(x_j) x_{j+1} .. x_n`, `ghat_j(0) = 0`, has `1 + sum d_j` coefficients and
  the map to `V_r` is a bijection for every `r`.
- **Corollary B.** Under eq weights, `u_k = 1`: Libra's mask `c + sum_j g_j(x_j)` satisfies
  Theorem 1 for every `tau`, `r`, in any characteristic.
- **Failure of Libra's mask.** Plain sum, characteristic 2: `G = 0`, `p_j^g = 0` for
  `j <= n - 2`, `p_{n-1}^g` constant; the image has dimension `d + 1`.
- **Theorem 2.** With a mask as in Theorem 1 and an ideal mask commitment revealing only `G`
  and `g(r)`: for every `f`, every verifier strategy, every `rho`, the view equals the output
  of the simulator of section 4.1, which is given `S` and makes one query `f(r)` (none if the
  final claim is handed on unopened). Perfect; no condition on `|F|`.
- **Proposition 3.** The staircase mask has no slack: any further linear functional of the
  mask given to the verifier reveals a linear functional of the witness's unmasked round
  polynomials.
- **Lemma 3 (linear opening gadget).** Columns `A = (a, pad)`, `B` uniform; messages
  `beta = <B, w>`, challenge `c`, `u = B + c A` in clear, challenge `z`, openings `A(z)`, `B(z)`.
  If a pad position has nonzero weight at `z`, the view is simulatable from `v = <a, w>` alone.
- **Lemma 4 (GKR layer).** With `vhat_i(y, x, b) = v_i(x, b) + y(1 + y)(c_{i,0} + c_{i,1} b)`,
  masked layer sumchecks, blinded claims `A_0, A_1`, and `Gtilde` in place of `G`: for
  challenges with every `r_y notin {0,1}`, the chain's view is simulatable from the tree's
  output and the leaf claims.
- **Lemma 5 (bus terminals).** Telescoping additive or multiplicative masks make the published
  per-table terminals uniform on the variety the public check defines; the message form is
  within `(T - 1)/|F|`; a self-cancelling pair per table makes a published denominator uniform.

**Proven on paper here:** all of the above (sections 3, 4, 5.1, 5.3, 7.3, 8), plus the
generalisation of Theorem 1 to arbitrary nonzero functionals (other summation domains). The
proofs are elementary linear algebra; the place to look for an error is Lemma 1's recursion and
the induction `K_j = kappa_j` in section 3.2, and the conditioning step in Lemma 4.

**Verified by exhaustive or exact computation:**

| Claim | Method | Sizes |
|---|---|---|
| Theorem 2 with the staircase mask | all masks against all simulator tapes, exact count tables | GF(4): `n <= 2, d <= 3` and `(3,1)`, `(3,2)` for all `r`; `(3,3)` for 9 `r`. GF(16): `n = 1, d <= 3` all `r`; `(2,1)`, `(2,2)`, `(3,1)` on samples of `r` |
| Theorem 2 against adaptive verifiers | same, protocol run from the definition | GF(4): `(2,2)`, `(3,1)`, `(3,2)`, two strategies |
| Theorem 1, Corollary A | exact rank of mask-to-view map | all `r`: GF(4) `n <= 5, d <= 3`; GF(16) `n <= 3, d <= 3`. Random and adversarial `r`: GF(2^8) `n in {8,16,23,25,27}`, `d in {2,3}`; GF(2^128) `(23,2)`, `(27,3)` |
| Corollary B, general weights | rank for all `tau` and `r`; exact distributions | GF(4) rank, several degree profiles; distributions: GF(4) at `n <= 3`, GF(16) at `(1,3)`, `(2,1)` |
| Libra's failure, the weighted mask's excluded event | rank; exact two-witness distance | as above; weighted mask full rank exactly when no `r_k = 1`, `k < n`, for all `r` over GF(4), GF(16) |
| Lemma 3 | all prover and simulator randomness | GF(4) lengths 4, 8; GF(16) length 2 |
| Lemma 4 | all blinders and masks, per-part equality plus bijection | GF(4), 4 leaves, two reductions, 67 cases |
| Lemma 5 | all mask randomness | GF(4), GF(16), GF(256), `T <= 4` |

**Not covered:**

1. The commitment to the mask and its opening proof: hiding of the committed columns, the
   evaluation proofs for `A(z)`, `B(z)`, and variant R's downstream reduction, in characteristic 2.
2. Whether `f(r)` may be given to the simulator: column-evaluation blinding and its rank bound.
3. The composed simulator of a whole proof, and the Fiat-Shamir compilation.
4. The optimised sumchecks of the pinned stacks (univariate skip, batched or packed round
   messages): each must be matched to the form of section 1.1; section 3.6 states the hypothesis
   to check for other summation domains and was not tested.
5. Fraction (logarithmic-derivative) GKR layers: stated, not tested. GKR chains beyond two
   reductions: proven, not enumerated.
6. Which bus values each stack publishes; the invisibility of the mask payload cells.
7. Libra's paper and ePrint 2026/391 (revision of 2026-11-16) were read in the citation audit of
   2026-11-19 and sections 1.3, 2, 7.1 and 10 corrected; the reviewer is asked to compare
   Theorem 1 / Corollary A with Lemma 6.2 of ePrint 2026/391 (finding C-1 of `CITATION-AUDIT.md`).
8. Soundness is argued only in sketches; the soundness calculator was not updated with the
   mask terms (`1/q` per masked sumcheck, `(l + m)/q` for the gadget, the completeness loss of
   the bus messages).
