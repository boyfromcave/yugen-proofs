# Plain WHIR over binary additive codes: round-by-round soundness of system A's node and leaf rows

Part of Yugen. Closes finding C-10 (b) of `CITATION-AUDIT.md` for the unique-decoding
regime: a written proof of round-by-round soundness of the opening that system A's plain rows run
(leanVM's WHIR with the affine-combiner fold, binary additive Reed–Solomon codes, unique decoding),
with each error term and its source. It is Theorem S of `zk-wi-soundness.md` with the masks removed
and with the plain opening's own code switch (high part in clear, one out-of-domain claim) and base
case (full folded lane in clear, then a sumcheck). One step changes a number: the query terms must
use the **true** rate of the folded lane, which the affine combiner raises; with it, **row 9 fails
the tree target by up to 4.36 bits** and row 7 keeps 0.63 bits of margin (section 6).

Status tags as in the other documents: **(P)** proven here, **(S)** read in a primary source named
with the claim, **(C)** checked by computation (`../qrom/test_numbers.py`), **(M)** from memory,
**(U)** open.

Provenance. Published and used: BCIKS20 Theorems 4.1 and 1.6 and Remark 1.2 (read for (BCIKS20 numbers follow the folder copy, ePrint 2020/654 revision of July 3, 2021 (`2020-654.pdf` (see REFERENCES.md)); the ECCC TR20-083 copy of May 30, 2020 numbered the affine-space theorem 1.7, the curve theorem 1.6 and the extension-field remark 1.5 (amended 2026-11-19, `CITATION-AUDIT.md` C-41))
`zk-wi-soundness.md`; restated in its section 1); WHIR (Arnon, Chiesa, Fenzi, Yogev, ePrint
2024/1586, copy dated November 21, 2024), Lemma 4.10 (unique decoding turns any proximity generator
into one with mutual correlated agreement, for **any** linear code) and Theorem 5.2 / Construction
5.1 as the template of the round list; Chiesa, Weissenberg, Yogev, Zheng, "Affine Combiners for
Reed–Solomon Proximity Gaps", ePrint 2026/2863 (copy dated November 13, 2026; CWYZ26), Section 1.1
(definition of the affine combiner and its degree asymmetry) and Section 6 (worst-case MCA error
`Omega(n/q)` without agreement loss); its Section 5 (Theorem 5.2, the interleaved rounds of the
**equal-degree** combiner (5.1) with a third challenge `theta`) is a different combiner and is cited
only as consistent with the degree growth used here (corrected 2026-11-19 after the referee report
`qrom-zk-referee.md` 3.2; the source of the degree growth is the pinned verifier's code, section 6). Adapted: Theorem S0 below is Theorem S of
`zk-wi-soundness.md` (Original, the Ycash developers, 2026) with its mask rounds removed and the
plain code switch and base case of leanVM (read in the pinned verifier, `crates/verifier/src/whir.rs`,
`verify_whir`, `sample_queries`, `lib.rs` `read_ood`; S). Original (the Ycash developers, 2026), as
far as checked against WHIR Sections 4 and 5, CWYZ26 Sections 1, 5, 6 and BCIKS20 Section 1:
the state function with per-lane degree bounds (section 3), Lemma C0 (code switch with the high
part in clear) and Lemma B0 (base case), and finding W-1 (true rates on the plain rows).

---

## 1. Why WHIR's theorem is not enough, and what replaces each hypothesis

WHIR Theorem 5.2 assumes (i) smooth codes: multiplicative cosets of power-of-two order and
power-of-two degree (Definitions 4.1, 4.2, S); (ii) a proximity generator with mutual correlated
agreement (Definition 4.9) for its fold `Fold(f, alpha)` (Definition 4.14), proven in unique
decoding by Lemma 4.10 with Theorem 4.8 (BCIKS20) and conjectured beyond (Conjecture 4.12); (iii)
its own fold, out-of-domain sampling and shift queries (Construction 5.1).

System A differs in each: (i) evaluation domains are `F_2`-linear subspaces `S` of `K = GF(2^64)`
(`x = K(query)`), codes are evaluations of the novel basis (`zk-hiding-commitment.md` 1.1), the
folded lane has `2^mu + kappa` coefficients, not a power of two; (ii) the fold is the affine
combiner `G + (alpha + beta X) F` on lane pairs of a row (leaf = row of `2^kappa` lanes at one
point), not WHIR's `Fold`; (iii) a non-final level commits the low `2^mu` coefficients of the
folded lane, sends its `kappa` high coefficients in clear, reads one out-of-domain multilinear
claim, then draws query positions and `lambda` in one message; the final level sends the whole
folded lane and closes with a degree-3 sumcheck over the low part (S, `verify_whir`).

What replaces each hypothesis:

| WHIR hypothesis | Replacement for A | Source |
|---|---|---|
| smooth domain | none needed: BCIKS20 Theorems 4.1 and 1.6 hold for every evaluation set `D` of `n` distinct points and every degree `k <= n` | BCIKS20 Section 1 (S, via `zk-wi-soundness.md` 1) |
| MCA for `Fold` in unique decoding (Corollary 4.11) | affine-combiner correlated agreement inside the unique-decoding radius, error `n/q`: `zk-wi-soundness.md` Lemma 2A from BCIKS20 Theorem 1.6. Mutual agreement is automatic there: WHIR Lemma 4.10's proof uses only linearity and `delta < delta_C / 2`, both true for additive codes; Lemma 2A's conclusion already names the common agreement set | Lemma 2A (P, `zk-wi-soundness.md`); WHIR Lemma 4.10 (S) |
| power-of-two degree | Lemma 1 of `zk-wi-soundness.md` (any dimension); degree bounds tracked per lane (section 3) | (P) |
| WHIR's shift and OOD rounds | Lemma C0 (section 4) | (P) |
| WHIR's final round | Lemma B0 (section 5) | (P) |

CWYZ26 (read 2026-11-19 for this document) is the published analysis of exactly this combiner:
`w = f + (alpha + beta x) g` with `deg f <= d`, `deg g <= d - 1`, over arbitrary evaluation domains
in every finite field (Section 1.1, Theorem 1.1). Two of its statements fix what can be claimed
here. (a) Without agreement loss the worst-case MCA error of the affine combiner is `Omega(n/q)`
(Section 6): Lemma 2A's `n/q` is of the right order for the exact-agreement statement used below,
and CWYZ26's `O(1/q + n^2/q^2)` needs one coordinate of agreement loss per round and the
Johnson-regime parameters, which this document does not use. (b) Its Theorem 5.2 (interleaved
rounds) recovers witnesses whose fold has degree bound `d + r` after `r` rounds, but for the
equal-degree combiner `f_(2i) + (alpha + beta z)(f_(2i-1) + theta f_(2i))` with inputs of degree at
most `d` (Section 5, (5.1)), not for leanVM's `G + (alpha + beta x) F`. It is **consistent with**,
not the source of, the degree growth that section 6 charges to the query terms; that growth is read
from the pinned verifier (section 6) and is elementary: `(alpha + beta X) F` raises the degree by one
a round.

## 2. Setting and notation

`F = GF(2^256)` (`E2`), `q = |F|`. Level `i`: oracle `i` is an interleaved word of `2^kappa_i`
lanes on a domain `D_i` (an `F_2`-subspace of `K`, `N_i = 2^(mu_i + r_i)` points), `mu_i` the
number of variables left after the level's `kappa_i` folds, `r_i` the level's log inverse rate as
`derive_config_for` sets it. An honest lane has `L_i = 2^mu_i` coefficients in the novel basis. A
row is the tuple of lane values at one point; distances count rows. Level 0 holds `K`-words; the
proximity statements are applied over `F` (BCIKS20 Remark 1.2: a word over a subfield is a word
over `F`; S).

`C[d]` is the code of polynomials with fewer than `d` coefficients (degree below `d`) on the
current domain. For a lane index `b in {0,1}^kappa` let `g(b)` be the number of fold rounds in
which lane `b` is the `G` member of its pair (CWYZ26's `f`, the member with the larger degree
bound). Define the level's **start code** `C_i = prod_b C[L_i + g(b)]` and after `j` folds the code
`C_{i,j} = prod_{b'} C[L_i + j + g_{>j}(b')]` on the remaining lanes. Every lane of `C_{i,j}` has
degree bound at most `d_i := L_i + kappa_i`; the folded lane after the level has `d_i`
coefficients (S: `next_scalars((1 << mu) + fold_count)`). The radius used throughout level `i` is

    e_i = floor((N_i - d_i) / 2),        true rate rho_i = d_i / N_i = (2^mu_i + kappa_i) / 2^(mu_i + r_i).

Any two codewords of any `C_{i,j}` differ in at least `N_i - d_i + 1 > 2 e_i` rows, so decoding
within `e_i` rows is unique at every round of the level.

Fold round `j` of level `i`: the prover sends `(u0, w, c0, c1)`; the verifier samples `alpha`,
`beta` (two independent uniform elements of `F`) and sets
`claim' = u0 + beta c0 + alpha (u0 + claim + alpha w + beta (c0 + c1))` (S). The honest message is
`q(a, b) = <G + (a + b X) F, W_F + a (W_F + W_G)>`, of total degree 2 in `(a, b)`, in
`span{1, a, a^2, b, ab}`, with `[1]q + [a]q = <(F, G), (W_F, W_G)>` (P, `zk-wi-soundness.md` 4.3,
unmasked).

The verifier's weight is zero on every coefficient slot above the honest ones (the high part enters
only the query checks), so a claim `<P, W> = T` about a decoded table `P` concerns its honest slots;
extra coefficients a cheating prover adds by the degree growth have weight zero
(`zk-wi-soundness.md` 4.1, P).

## 3. State function

After each verifier message the state is **doomed** unless:

- during the folds of level `i` (after `j` folds): the current word `U_{i,j}` is within `e_i` rows
  of `C_{i,j}`, and with its unique decoding `P_{i,j}` the current claim equals the true value
  `V_j(r_{<=j})` of the sumcheck polynomial of Lemma F0;
- between the last fold of level `i < L-1` and its positions: the folded word `fold_i` (a function on
  `D_i`, row `y` mapped to `fold_row(row_y, y)`) is within `e_i` rows of `C[d_i]`, and its decoding
  `p'` satisfies `<p', W'> = T` (the claim after the folds);
- after the positions and `lambda` of level `i`: the start condition of level `i + 1` for oracle
  `i + 1` and the new claim (the first item at `j = 0`);
- at the last level, after the positions: every opened row folds to `P*`'s value at its point and
  `<P*_low, W'> = T` (the sumcheck claim of the tail is true for the sent lane); during the tail
  sumcheck, the standard sumcheck state (claim equals the true partial sum).

Before any message the state is doomed if oracle 0 is not within `e_0` rows of `C_0` or its decoding
violates `<P, W> = T`. A prover message never changes a doomed state into a non-doomed one: the
committed oracle and earlier claims are fixed, and a later commitment is judged only after the
next verifier message (Definition 8.3 of CMS19, ePrint 2019/834, and the book's definition behind
Theorem 31.2.1 ask exactly this; S for CMS19 Definition 8.3).

## 4. Lemmas

**Lemma F0 (one fold round) (P).** From a doomed state during level `i`, the probability over
`(alpha, beta)` that the state after the round is not doomed is at most `max(N_i / q, 2 / q)`.

*Proof.* Case far: `U_{i,j}` not within `e_i` rows of `C_{i,j}`. The pairs `(F_c, G_c)` of lanes
have degree bounds `(D - 1, D)` for `D = L_i + j + 1 + g_{>j+1}(c)`. If the folded word is within
`e_i` rows of `C_{i,j+1}` for more than `N_i q` of the `q^2` pairs, `zk-wi-soundness.md` Lemma 2A
(applied per pair with the common radius `e_i <= floor((N_i - D)/2)`, then its row count) gives
`f_c in C[D - 1]`, `g_c in C[D]` agreeing with `(F_c, G_c)` outside a common set of at most `e_i`
rows: `U_{i,j}` was within `e_i` rows of `C_{i,j}`, a contradiction. So at most `N_i / q` of the
challenges leave the far case. Case close and false: the fold of the rows equals the fold of the
decoding outside the same at most `e_i` rows, so the new decoding is the fold of the old one
(uniqueness). Extend the operator `lam(q) = [1]q + [a]q` and let
`H = <p'(alpha_1, beta_1, .., alpha_k, beta_k), W'(alpha_1, .., alpha_k)>` with `p'` the fold of
the decoding; `H` has total degree at most 2 in each pair (`p'` degree 1, `W'` degree 1 in `alpha`).
`V_j = lam_{j+1} .. lam_k H`. If `claim_j != V_j(r_{<=j})`, any message `q'` with `lam(q') = claim_j`
differs from `V_{j+1}(r_{<=j}, ., .)`; the difference is a nonzero polynomial of total degree at
most 2 in `(a, b)`, zero on at most `2q` of the `q^2` pairs (Schwartz–Zippel). ∎

The masked version (`zk-wi-soundness.md` Lemma 3A) has degree 3 per pair; without masks it is 2.
The calculator's fold term `(3 + n)/q` (WHIR's `d* = 3`, finding C-9) is an upper bound of both.

**Lemma O0 (the out-of-domain point) (P).** The out-of-domain point `z` (in `F^mu`) of a non-final
level is a verifier message whose drawing changes no state: the state between the folds and the
positions does not mention `z`, and the prover's answer joins the `lambda` batch. Error 0. (Under
unique decoding the sample is not needed for soundness; its claim is one more linear constraint.)

**Lemma C0 (code switch with the high part in clear) (P).** Before the positions of level
`i < L-1`, let the state be doomed: `fold_i` is not within `e_i` rows of `C[d_i]`, or it is, with
decoding `p'`, and `<p', W'> != T`. Oracle `i + 1`, the high part `h` (`kappa_i` scalars) and the
out-of-domain answer `v_z` are fixed. Then the probability over the `Q_i` positions (independent,
uniform in `D_i`: S, `sample_queries`, bits of fresh challenges, `N_i` a power of two) and
`lambda` that the state after is not doomed is at most

    ((1 + rho_i) / 2)^Q_i + (Q_i + 1) / q,        rho_i = (2^mu_i + kappa_i) / N_i.

*Proof.* Suppose oracle `i + 1` is within `e_{i+1}` rows of `C_{i+1}` with decoding whose honest
slots form `u` (`2^mu_i` coefficients; other slots have weight zero, section 2). The new claim is
the identity in `lambda`

    (<u, W'_low> - T) + lambda (u(z) - v_z) + sum_q lambda^(q+2) (u(y_q) + What_mu(y_q) h(y_q) - v_q) = 0,

`v_q = fold_row(row_q, y_q)`, `u(z)` the multilinear evaluation (S: the glued claims of
`verify_whir`). If some coefficient is nonzero it holds for at most `Q_i + 1` values of `lambda`.
Otherwise `<u, W'_low> = T` and the polynomial `P' = u + What_mu * h` (coefficients `(u, h)`,
`d_i` of them; S: the correction `novel_eval(high, what) * what[mu]`) satisfies `P'(y_q) = v_q`
at every position and `<P', W'> = T`. Far case: `P' in C[d_i]` agrees with `fold_i` on at most
`N_i - e_i - 1` rows, and every position falls there. Close case: `P' = p'` contradicts
`<p', W'> != T`; `P' != p'` agrees with `p'` on at most `d_i - 1` points, so a position passes only
in the at most `e_i` corrupted rows or those points. In both cases a position passes with
probability at most `(e_i + d_i - 1)/N_i <= (1 + rho_i)/2` or `(N_i - e_i - 1)/N_i <= (1 + rho_i)/2`. ∎

**Lemma B0 (base case: full folded lane, then a sumcheck) (P).** At the last level the prover sends
`P*` (`d_{L-1}` coefficients) before the positions. From a doomed state (fold far, or close with
decoding `p'` and `<p', W'> != T`), the positions make the state non-doomed with probability at
most `((1 + rho_{L-1}) / 2)^Q_{L-1}`; each round of the tail sumcheck (degree at most 3 accepted)
with probability at most `3/q`; a doomed final state is rejected by the terminal check.

*Proof.* Far: `P*` is a codeword of `C[d]`, as in Lemma C0. Close: if `P* = p'` the claim is false
for `P*` and the state stays doomed whatever the positions; if `P* != p'` each position passes with
probability at most `(e + d - 1)/N`. The positions are drawn after `P*` (S). The tail is a sumcheck
on the fixed multilinear `P*_low` with public weights: Schwartz–Zippel per round. ∎

## 5. Theorem

**Theorem S0 (P).** In the unique-decoding regime with the true rates of section 2, leanVM's plain
WHIR opening over binary additive codes (rows 7 and 9 of `yugen-proof-a` `docs/parameters.md` 2.1,
and any row of the same verifier) is round-by-round sound with the state function of section 3 and
the errors

| Verifier message | Error | By |
|---|---|---|
| fold round `j` of level `i` (`alpha`, `beta`) | `max(N_i, 2) / q` (calculator: `(3 + n)/q` with `n >= N_i`) | Lemma F0; BCIKS20 Theorem 1.6 via Lemma 2A |
| out-of-domain point of level `i < L-1` | 0 | Lemma O0 |
| positions and `lambda` of level `i < L-1` | `((1 + rho_i)/2)^Q_i + (Q_i + 1)/q`, `rho_i = (2^mu_i + kappa_i)/N_i` | Lemma C0 |
| positions of the last level | `((1 + rho_{L-1})/2)^Q_{L-1}` | Lemma B0 |
| tail sumcheck, each of `mu_{L-1}` rounds | `3/q` | Lemma B0 |

and a doomed final state is rejected. *Proof:* the lemmas in protocol order; the initial state is
doomed for a false claim on oracle 0 (or a far oracle 0). The batching of evaluation claims into
the initial weight `W` precedes the opening and is counted among the rounds outside it
(`soundness-method.md` 8.5b, `OTHER_ROUNDS`). ∎

**Knowledge.** The state function is defined through unique decoding of committed words, so it is a
knowledge state function in the sense of CMS19 Definition 8.5 (S): when the initial state is not
doomed the decoding of oracle 0 (Berlekamp–Welch on `D_0`, valid on any domain) is a witness. Round-by-round
knowledge error = the table above (P). Row 8 (the hiding leaf, W-I) is covered by Theorem S of
`zk-wi-soundness.md`, whose query terms already use the true rates `wi.layout` computes.

What is not covered (U): the Johnson regime. For lines over arbitrary evaluation sets in every
characteristic, Johnson-regime MCA is now stated by Dao, Kominers, Thaler, "Reed–Solomon Codes
Beyond Johnson", ePrint 2026/2056 (copy dated November 2, 2026), Theorem 4.4 (statement located on
2026-11-19, proof not read); for the affine combiner near Johnson, CWYZ26 Theorem 1.1 and Section 5
(with one coordinate of agreement loss). Neither is used by any row; the design basis is unique
decoding.

## 6. Finding W-1: the plain rows' query terms must use the true rate

The calculator (`whir.rounds`, `current.a_node_check`) and `yugen-proof-a`'s certification
(`bench/soundness/cert.py`) evaluate the query terms at the nominal rate `2^-r_i`. Lemma C0 and
Lemma B0 need `rho_i = (2^mu_i + kappa_i)/2^(mu_i + r_i)`: the affine combiner raises the folded
lane by one coefficient a round. Source (S): the pinned verifier, `crates/verifier/src/whir.rs`: the
final lane is accepted with `(1 << mu) + fold_count` scalars, and at a non-final level each position
is corrected by `novel_eval(high, what) * what[mu]` with `fold_count` high coefficients on a block of
`2^(mu + level_rate)` points, so the code tested at level `i` has dimension `2^mu_i + kappa_i`; the
growth itself is elementary (`(alpha + beta X) F` has degree one more than `F`). CWYZ26 Theorem 5.2
states `d + r` for a different (equal-degree) combiner and is consistent with it, nothing more. The design basis's remark "plain WHIR: true rate = nominal"
does not hold for system A. The factor `1 + kappa 2^-mu` matters only where `mu` is small: the last
level, and for residual `2^5` the level before it.

Re-evaluated with the tree need of the calculator (`shipping.tree_target(CAT1, proofs=20_000)`,
`OTHER_ROUNDS = 512`, read only) and the query list of the rows (`CAT1_TREE_UD_QUERIES`,
`params.rs`: 369, 226, 185, 168, 161, ... by level rate), C (`../qrom/test_numbers.py`; the
calculator was not edited):

| Row, stack, rate | Need (bits) | Weakest query round, nominal | Weakest, true rate | Margin, true rate |
|---|---|---|---|---|
| 7 (leaf, folds 6, 3; reductions 3, 3; residual `2^7`), `2^22`, 1/4 | 152.343 | 153.24 | 153.24 (level 0; last level 153.69) | **+0.90** |
| 7, `2^22`, 1/2 | 152.343 | 153.15 | 152.97 (last level, `mu = 7`) | **+0.63** |
| 9 (node, folds 6, 3; reductions 3, 3; residual `2^5`), `2^24`, 1/2 | 152.365 | 153.15 | **148.02** (last level, `mu = 3`) | **-4.35** |
| 9, `2^24`, 1/4 | 152.365 | 153.24 | 151.23 (`mu = 3`) | -1.14 |
| 9, `2^25`, 1/2 / 1/4 | 152.365 | | 150.65 / 152.54 (`mu = 4`) | -1.72 / +0.17 |
| 9, `2^26`, 1/2 / 1/4 | 152.365 | | 151.97 / 153.19 (`mu = 5`) | -0.39 / +0.83 |
| 9, `2^27`, 1/2 / 1/4 | 152.375 | | 148.02 / 151.23 (`mu = 3`) | -4.36 / -1.15 |
| 9, `2^28`, 1/2 / 1/4 | 152.375 | | 150.65 / 152.54 (`mu = 4`) | -1.73 / +0.16 |

Row 8 (W-I) is unaffected: its counts were solved at the true rates of the hiding layout.

Fixes, either suffices (the choice is the lead architect's):

1. **Per-level counts at the true rate** (the `Queries::PerLevel` variant of `design-basis.md`
   S-9, or counts computed at setup from `mu_i`, `kappa_i`, `r_i`). At the last level of row 9:
   `mu = 3`: 173 queries at rate `2^-4` (list: 168), 163 at `2^-5` (161); `mu = 4`: 170 / 161;
   `mu = 5`: 169 / 161; `mu >= 6`: the list's counts. Cost: at most five more queries on the
   smallest tree of a node proof. Acceptance: `cert.py` (or the calculator) evaluates
   `rho_i = (2^mu_i + kappa_i)/2^(mu_i + r_i)` and every shape of row 9 passes; a test that
   decreases each last-level count by one fails.
2. **Residual bound with `mu_final >= 7`** for the node row (the leaf row already has it): the list's
   counts then hold with at least 0.6 bits of margin (C, row 7's last level). This changes the
   recursion team's node sweep (`recursion.md` 9.10) and is not recommended over fix 1.

For the calculator (a later revision; not edited here): in `whir.rounds`, replace
`query_error(p, c.queries[i])` by the same error at rate `(2^(m_i - k_i) + k_i) / 2^(m_i - k_i + r_i)`
for system A's configurations (`zk-wi-soundness.md`'s `wi.layout` already does this for W-I), and
in `a_node_check` / `a_leaf_check` pass the post-fold variable count. The unique-decoding radius
used by the fold terms is unaffected at 256 bits (fold rounds keep 74 bits or more over the need).

## 7. Review sheet

| # | Statement | On paper | Computation | Open |
|---|---|---|---|---|
| 1 | Per-lane degree bounds and one radius per level (section 2) | yes | | |
| 2 | Lemma F0: far case by Lemma 2A (BCIKS20 Theorem 1.6), close case total degree 2 | yes | Lemma 2A's toy checks (`zk-sound/test_proximity.py`) | the prover-side meaning of the four scalars is read from the verifier only (as in Lemma 3A) |
| 3 | Lemma C0: code switch with the high part in clear and one OOD claim | yes | none | |
| 4 | Lemma B0: full lane, positions after it, degree-3 tail | yes | none | |
| 5 | Finding W-1 (true rates) | yes | `../qrom/test_numbers.py` | the fix (per-level counts) and its certification |
| 6 | Mutual correlated agreement is not needed beyond Lemma 2A's common agreement set in unique decoding | yes (WHIR Lemma 4.10's argument) | | |

Questions for the external reviewer: whether the state function of section 3 is a valid
round-by-round state function across the code switch when oracle `i + 1`, the high part and the OOD
answer are all fixed before the positions; whether the degree bookkeeping `L_i + j + g_{>j}(b')`
of Lemma F0 matches the verifier's lane order (`eq_kernel` order, level 0 reversed; S); and whether
CWYZ26's agreement-loss version should replace Lemma 2A if the project ever leaves unique decoding.
