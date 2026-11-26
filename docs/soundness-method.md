# Yugen step 0.6: soundness method

This document explains how `soundness/` turns a proof system's parameters into classical and
quantum (QROM) bits of soundness per layer and for the leaf, bundle and merge chain, so that an
external cryptographer can check every step. It states each formula, its source, and whether the
source was read during this step (**confirmed**) or not (**unconfirmed**). The E3 review (plan
§11) is asked to confirm or replace every unconfirmed item before any parameter set relies on it.

Run: `cd soundness && uv run yugen-soundness [--target cat1|cat3|BITS] [--design] [--basis]`;
tests: `uv run pytest`. The tool has no dependencies beyond Python 3.11; `pytest` is a
development dependency.

**The security target is NIST category 1 for the whole suite, with a parameter path to
category 3** (the lead architect's decision of 2026-11-18, replacing the "100 QROM bits" wording
of plan SQ-8/SQ-22). Section 8 defines the named targets `cat1` and `cat3` the calculator
implements and says which parts are proven theorems and which are attack-cost estimates.
Sections 1 to 7 describe the machinery (written for step 0.6 at the 100-QROM-bit target; the
tables in section 4 are kept as the record of that target). The parameter sets the plan cites
are in `docs/design-basis.md`.

## 1. What is computed

For one proof system instance (one layer), the tool builds the list of verifier messages of the
underlying IOP (rounds), assigns each round its round-by-round (RBR) soundness error `eps_r` and
its proof-of-work (grinding) bits `g_r`, and compiles:

- classical bits `kappa_C` of the non-interactive argument (BCS transformation, Keccak as a
  random oracle with output length `lambda`);
- quantum bits `kappa_Q` against an adversary making quantum queries to the random oracle;
- for a chain of layers (leaf, bundle, merge 1, merge 2), the chain's bits.

It also estimates proof size per layer, and it solves for the smallest query counts that meet a
target.

**Bits of security.** Average-case, as in the SNARGs book §28.3.2 (Chiesa–Yogev): `kappa` bits
means that for every query budget `t <= 2^kappa`, the success probability `eps(t) <= t / 2^kappa`.
The same definition is used for the quantum case with `t` quantum queries.

## 2. Formulas and sources

### 2.1 From the IOP to the argument

| # | Statement | Source | Status |
|---|---|---|---|
| F1 | `eps_ARG(t) <= eps_sr(t) + 3.5 t^2 / 2^lambda` (with the book's mild condition on `t`) | SNARGs book, Theorem 25.2.1 (and the same form for knowledge soundness, Theorem 26.1.1, straightline case) | confirmed |
| F2 | `eps_sr(t) <= (t + k) eps_rbr`, `k` the number of rounds, `eps_rbr` the largest round error | SNARGs book, Theorem 31.2.1 (knowledge: Theorem 31.3.1) | confirmed |
| F3 | Against `t` quantum queries, BCS on an RBR-sound IOP has error `6 (t'^2 eps_rbr + 4 t'^3 / 2^lambda)` in the database game, `t' = t + a`, `a = O(q log l)` the verifier's oracle calls, plus Lemma 4.9's `sqrt(a / 2^lambda)` added to the square root; so `C1 = 6`, `C2 = 24` | Chiesa, Manohar, Spooner, *Succinct Arguments in the Quantum Random Oracle Model*, ePrint 2019/834 (copy dated January 14, 2020; read 2026-11-19): Theorem 8.6 (Section 8.4) states `O(t^2 eps + t^3 / 2^lambda)`; the constants are in its proof, Section 8.5.1 (Lemma 5.13, the lifting lemma, with Lemmas 8.13, 6.11 and 4.9). The 6 also in N. Spooner's thesis, UCB/EECS-2020-182, §5.10.5 | `C1 = 6` confirmed; `C2 = 24` confirmed (was 1, assumed: CITATION-AUDIT C-6); the theorem is for the paper's own BCS variant (Section 8.2): its use for the transcripts as built is unconfirmed (C-7) |
| F4 | A `g`-bit proof of work before a challenge multiplies that round's error per oracle query by `2^-g` (classical) | Ben-Sasson, Brownstein, Carmon, Goldberg, Levit, Medini, Shtaierman, Yogev, *ethSTARK Documentation*, Version 1.2 (July 2023), ePrint 2021/582, read 2026-11-19: Section 6.3, Theorem 6 (the grinded IOP, in which round `i` carries `z_i` extra verifier bits that must be zero, has round-by-round soundness `eps_i 2^-z_i`) and Section 7.1, Theorem 8 (BCS16 Theorem 7.1 applied: `T max_i eps_i 2^-z_i + 3 (T^2 + 1) / 2^kappa`); classical ROM only. Plonky3 `p3-security` `grinding.rs` uses the same accounting | confirmed for the classical ROM (C-17; the earlier citation "§5" was wrong). **No shipping row uses grinding** (`shipping.py`, `current.py`: every grind 0); F4 enters only the design alternatives with 20-bit query grinding and the leanVM cross-check |
| F5 | Quantumly, the round's bad set (bad challenge and valid nonce) has density `eps_r 2^-g` in the oracle's output, so F3 applies with `eps_r 2^-g`: grinding bits are halved together with the round's bits | Our argument; relies on the optimality of Grover search (Bennett–Bernstein–Brassard–Vazirani, 1997) | unconfirmed |

Derived conditions, implemented in `compose.py`. With `e_r = -log2 eps_r + g_r` and
`e_min = min_r e_r`:

- classical, from F1 and F2: `(1 + k) 2^-e_min <= 2^-(kappa+1)` and
  `3.5 * 2^kappa / 2^lambda <= 2^-(kappa+1)`, so
  `kappa_C = min(e_min - 1 - log2(1 + k), (lambda - 1 - log2 3.5) / 2)`;
- quantum, from F3 and F5 at `t = 2^kappa`:
  `kappa_Q = min((e_min - 1 - log2 C1) / 2, (lambda - 1 - log2 C2) / 3)`.

Consequences: 100 QROM bits needs `e_min >= 201` in every round, and `lambda >= 306`
(`lambda = 256` caps `kappa_Q` at 83.5; `lambda = 384` at 126.1). With `C2 = 1`, as assumed before
CMS19 was read (C-6), these were 301, 85.0 and 127.7. When an adversary must produce
`N` proofs together (a bundle), `k` becomes `N k` in the classical term (parameter `instances`).

### 2.2 Proximity gaps and decoding regimes

| # | Statement | Source | Status |
|---|---|---|---|
| P1 | Lines (affine spaces) in `F^n` have a `(delta, eps)` proximity gap for RS codes of rate `rho`: below unique decoding, `eps_U = n / q` | BCIKS20, Theorem 1.2, read in ECCC TR20-083 (= ePrint 2020/654) | confirmed |
| P2 | Up to Johnson, `delta in ((1-rho)/2, 1 - sqrt(rho))`, `eta = 1 - sqrt(rho) - delta`: `eps_J = (k+1)^2 / ((2 min(eta, sqrt(rho)/20))^7 q)` | BCIKS20, Theorem 1.2 | confirmed for correlated agreement. **WHIR needs mutual correlated agreement**, which WHIR (ePrint 2024/1586) proves only in unique decoding (Lemma 4.10, Corollary 4.11) and states up to Johnson with this error as Conjecture 4.12 (1): for WHIR rows P2 is a conjecture (C-10). For lines (WHIR's fold generator `(1, alpha)`), mutual correlated agreement up to Johnson is now proved with a different, smaller error by DKT26 Theorem 4.4 (P4; C-15). For BaseFold the published Johnson-regime analysis is Haböck, ePrint 2024/1571, Theorem 3 (subcode correlated agreement), a different error form (C-11) |
| P3 | Curves of degree `l` (batching by powers of one challenge): error `l * eps` | BCIKS20, Theorem 1.5 | confirmed |
| P3a | Correlated agreement over affine spaces `u0 + span(u1..ul)`, same `eps` as P1/P2; lines inside the unique-decoding radius with the explicit count `|S| > n` | BCIKS20, Theorem 1.6 and Theorem 4.1 (read 2026-11-19; used by `zk-wi-soundness.md` for the eq-fold and the affine combiner) | confirmed |
| P4 | Line mutual-correlated-agreement count at the Johnson radius: `8 n (m + 1/2)^3 / (3 rho_minus)`, `rho_minus = (k - 1)/n`, `eps = that / q` | Q. Dao, S. D. Kominers, J. Thaler, *Reed–Solomon Codes Beyond Johnson: Efficient Decoding and Smaller Cryptographic Proofs*, ePrint 2026/2056 (copy dated November 2, 2026), read 2026-11-19: Theorem 4.4 ("Quantitative Johnson MCA in every characteristic"), equations (36) to (39): `m = max(ceil(sqrt(rho_minus)/(2 eta0)), 3)`, `t = m + 1/2`, agreement `A = ceil((sqrt(rho_minus) + eta0) n)`, exceptional count `< 8 n t^3 / (3 rho_minus)`, probability that count over `|F|`; any field, any `n` distinct evaluation points (Section 3.1: "We assume no multiplicative or additive structure of the evaluation set"); full agreement-set line MCA (Definition 3.2), which implies WHIR's Definition 4.9 for lines. Proof: Lemma 4.3 (Section B.1), Proposition B.1 (whose dimension count is cited to BCHKS, full version, Lemma 3.1, not read), Section B.3. Plonky3's "Theorem 5.12, App. B.1–B.2" is the numbering of an earlier version the copy cites as [DKT26b] | confirmed (statement and proof outline read; C-14). The calculator used `rho = k/n` until 2026-11-19 (C-14: under 0.03 bits). Curves of degree above one (batching by powers of one challenge, FRI folds of arity above 2) have no closed-form count at order zero in the paper (end of Section 4.3, Remark 6.1): for those rows P4 times `l` is our extrapolation (C-15) |
| P5 | Johnson list size `L <= 1 / (2 eta sqrt(rho))` at radius `1 - sqrt(rho) - eta` | WHIR, ePrint 2024/1586, Theorem 4.3 ("Johnson bound"), stated there without proof; Lemma 4.4 extends it to interleaved codes. Proved, for every field and evaluation set, in DKT26 (ePrint 2026/2056) Theorem 4.4, equation (38): `|L| <= min(B_jet, n (A - D)/(A^2 - n D))`, `B_jet = ceil(t / sqrt(rho_minus)) - 1` (Proposition B.1 and the pairwise argument after it); interleaved lists: its Corollary 6.4. Haböck, ePrint 2024/1571, uses the Guruswami-Sudan bound `(m + 1/2)/sqrt(rho)` at `1 - (1 + 1/(2m)) sqrt(rho)` (Lemma 5) | confirmed (C-15): the value used, `m / rho` at `eta = sqrt(rho)/(2m)`, is above both terms of (38) (at rate 1/16, `m = 10`: 160 against 41 and about 31), so the calculator's figure is an upper bound |
| P6 | A query against a `delta`-far word passes with probability at most `1 - delta`; `t` independent queries `(1 - delta)^t` | definition of distance; the tool uses `delta = (1-rho)/2` (unique decoding) or `1 - sqrt(rho)(1 + 1/(2m))` (Johnson, `m = 10`) | definition |
| P7 | Disproofs: correlated agreement up to capacity (BCIKS conjecture), WHIR's mutual correlated agreement up to capacity, DEEP-FRI list decoding up to capacity | Crites–Stewart, ePrint 2025/2046 (abstract read); Diamond–Gruen ePrint 2025/2010 (cited by the plan, not read) | confirmed for 2025/2046's abstract |

The tool implements three regimes: `unique-decoding` (P1, P3, P6: every bound confirmed),
`johnson-bciks20` (P2, P3, P5, P6) and `johnson-dkt26` (P4, P3, P5, P6, marked UNCONFIRMED in all
output). No capacity-regime (conjectured) bound is implemented, by design. Since DKT26 was read
(2026-11-19, C-14, C-15) the UNCONFIRMED mark no longer refers to P4 or P5, which are proved; it
stays because the protocol-level theorems the rows need are not written for these codes: WHIR's
Theorem 5.2 on binary additive domains (C-10 (b)), batching by powers of one challenge at order
zero (C-15), and for Binius64 the three items of C-11.

At the field sizes Yugen needs, P2 (BCIKS20 Johnson) is too weak to be useful: its `(k+1)^2 /
(sqrt(rho)/10)^7` factor costs about 85 bits at `k = 2^24`, `rho = 1/16`. That is why the tables
show unique decoding (confirmed, larger proofs) beside DKT26 (proximity bound proved; protocol
theorems for the rows not yet written; smaller proofs).

### 2.3 Round structure of each protocol

**FRI-based STARK** (`fri.py`; system B's KoalaBear configuration). Rounds:

| Round | Error | Status |
|---|---|---|
| constraint combination (ALI) | `C L / q` | the form of ethSTARK (ePrint 2021/582, Version 1.2) Theorem 5 item 1 with its Remark 6 (one challenge, powers: `(2s - 1) l / |K|`), read 2026-11-19; never binding here |
| out-of-domain point (DEEP) | `L^2 D k / q` | form unconfirmed (STIR Lemma 4.5 shape via Plonky3); never binding here |
| batching of the `W` opened (column, point) pairs by powers | `(W - 1) eps_line(n)` | P1/P2/P4 with P3 |
| fold `i` with arity `2^a` | `(2^a - 1) eps_line(n_i)` | P3 |
| queries | `(1 - delta)^t` | P6 |

**WHIR** (`whir.py`; system A). Round `i` has `m_i` variables, fold `k_i`, log inverse rate
`r_i`, `t_i` queries and `s` out-of-domain samples. Rounds: `k_i` fold steps each with
`3L/q + eps_line(n_i)`; in the Johnson regime an out-of-domain round `L^2/2 (2^m_i / q)^s`; a
query round `(1 - delta_i)^t_i + (t_i + s) L / q`; and the final round `(1 - delta_M)^t_M`. This
is WHIR (Arnon, Chiesa, Fenzi, Yogev, *WHIR: Reed–Solomon Proximity Testing with Super-Fast
Verification*, ePrint 2024/1586, copy dated November 21, 2024), Theorem 5.2, **read and checked
term by term on 2026-11-19**: `eps_fold <= d* l / |F| + err*(C, 2, delta)` with
`d* = 1 + deg_Z(w) + max deg_Xi(w) = 3` for an evaluation constraint (Construction 5.1; the
calculator used Plonky3's 2 until finding C-9, a change below 10^-7 bits); `eps_out <= 2^m l^2 /
(2 |F|)` for one sample (Lemma 4.25 for `s`); `eps_shift <= (1 - delta)^t + l (t + 1) / |F|`;
`eps_fin <= (1 - delta)^t`. Two hypotheses of the theorem are not met by every row (finding C-10):
`err*` is a **mutual** correlated agreement error, proven in unique decoding (Corollary 4.11:
`(l - 1) n / |F|`, the P1 value for a line) and only conjectured up to Johnson (Conjecture 4.12);
and the codes are **smooth multiplicative** cosets (Definition 4.2), while system A's codes are
binary additive. The unique-decoding rows of A therefore rest on the term list applied to additive
codes, not on the theorem as stated: for the leaf's W-I opening the proof is ours (Theorem S of
`zk-wi-soundness.md`, binary additive cosets, from BCIKS20 Theorem 4.1, which holds for any
evaluation set); for plain-WHIR nodes it is the same proof without masks, still to be written out
(C-10's task).

leanVM's own RBR theorem (its `doc/leanvm/body/b-polynomial-commitment-scheme.tex`, read at the
pin) has the same round list with different constants: batching `(J0 - 1) L0 / |E|`; fold
`eps_aff(n, d, a) + 2 L / |E|` with the affine-combiner MCA error of CWYZ26 (Chiesa, Weissenberg,
Yogev, Zheng, *Affine Combiners for Reed–Solomon Proximity Gaps*, ePrint 2026/2863, copy dated
November 13, 2026, read 2026-11-19: Theorem 4.10, equation (4.13)); OOD `binom(L, 2) nv / |E|`;
query `((a - 1)/n)^t + (J - 1) L / |E|`; tail rounds `2 / |E|`. Checked against the paper (C-19):
leanVM's `eps_aff` (its Definition "Affine MCA error") is equation (4.13) with the interpolation
parameters `(m, D)` and the intermediate threshold `B` left free, as CWYZ26 itself does in Remark
5.3; its `h`-lane form is the packing step of the proof of CWYZ26 Theorem 5.2 (equation (5.7));
CWYZ26 holds over every finite field and every evaluation set, so leanVM's binary additive domains
are covered; the guarantee carries one coordinate of agreement loss per fold, which leanVM absorbs
by lowering its threshold by one per fold round (`a^(i,j-1) = a^(i,j) - 1`), as CWYZ26 Theorem 5.2
does with `A + r`. The tool does not implement `eps_aff` (risk R-5 in `framework-selection.md`; the
formula is now confirmed, the implementation is the remaining task).

**BaseFold-style folding PCS** (`whir.py`, `BaseFoldConfig`; system B's binary configuration).
One fold step per variable with `2L/q + eps_line(n_j)`, the same query positions followed through
every layer, one query round `(1 - delta)^t` at the end. In unique decoding these terms bound those
of Diamond and Posen, *Polylogarithmic Proofs for Multilinears over Binary Towers*, ePrint 2024/504
(read 2026-11-19): sumcheck `2 / |L|` a round and fold `theta |S^(i+theta)| / |L|` per committed
oracle (Proposition 4.21, from the tensor proximity gap of its Theorem 2.4), query
`(1/2 + 1/(2 * 2^R))^gamma` (proof of Proposition 4.24; equation (42)). DP24 proves soundness of
the whole protocol, not round-by-round soundness; the round-by-round statement is Haböck, *Basefold
in the List Decoding Regime*, ePrint 2024/1571, Theorem 1 (Section 5) with Sections 5.4, 6.2 and
6.3 (Theorem 6), written for the list-decoding regime and said there to carry over "verbatim" to
unique decoding (C-12).

### 2.4 Recursion

| # | Statement | Status |
|---|---|---|
| C1 | For a chain of layers verified recursively, `eps_chain(t) <= sum_i eps_i(t)`, so `kappa_chain = -log2 sum_i 2^-kappa_i` | union bound; our argument |
| C2 | C1 holds only under the heuristic that Keccak, evaluated inside the recursion circuit, behaves as the random oracle the inner proof was analyzed with. No ROM proof covers this step (it is the "recursion rests partly on heuristics" risk of plan §9) | unconfirmed by nature; the leaf audit feed (plan §9) is the mitigation |
| C3 | Many leaves in one bundle add no factor beyond the `N k` term of F2, because the query budget `t` already counts every query the adversary makes for every leaf | our argument |

Four layers at 100 bits each give 98.0 chain bits; each layer should target 102.

## 3. Proof-size model

Sizes are estimates for choosing parameters, not specifications. Merkle openings are counted
with the top `log2 t` levels shared among `t` queries: `t (log2 N - cap - log2 t) + 2^cap`
sibling digests per tree. FRI: per query, every committed matrix's row (width x element bytes,
plus a salt) and one leaf of `2^a` extension elements per fold layer. WHIR and BaseFold: per
query and round, `2^k_i` elements; plus roots, sumcheck polynomials (3 coefficients per variable),
out-of-domain answers, the final polynomial and proof-of-work nonces. A fixed `extra_bytes`
stands for transcript parts outside the commitment (zerocheck, GKR, buses).

Calibration against the measurements in `bench/results/` (tests in `tests/test_soundness.py`):

| Run | Measured | Model | Note |
|---|---|---|---|
| Plonky3 KoalaBear, 128 Keccak-f, rate 1/2, 100 queries | 1,428,394 B | 1,302 KiB (1,333,000 B) | -7% |
| Plonky3 KoalaBear, 128 Keccak-f, rate 1/16, 110 queries, octic, 384-bit digests | 1,809,036 B | 1,614 KiB (1,653,000 B) | -9% |
| Plonky3 binary folding, 163 Keccak-f, rate 1/2 | 434,434 B | 293 KiB (300,000 B) | -31%: 4-ary Merkle and the zerocheck transcript are not modelled |
| leanVM, 128 Keccak compressions, rate 1/16 | 91,608 B | 74,422 B for the WHIR part | the 17 KB difference is used as leanVM's non-commitment transcript |

The calculator also reproduces the classical accounting of Plonky3's own `p3-security` crate in
shape: its regression test reports 57 proven unique-decoding bits for 100 queries at rate 1/2 with
a 16-bit grind; this tool gives 52.4 for a comparable configuration, the difference being the
`log2(1 + k)` term of F2, which `p3-security` does not charge.

## 4. Results

Output of `uv run yugen-soundness` (target 100 QROM bits per layer) as produced in step 0.6,
with `C1 = 1`; this target is superseded by `cat1`/`cat3` (section 8). Since then the default
is `C1 = 6` (F3) and the Merkle path count uses `max(cap, log2 t)` shared levels instead of
subtracting both (a correction that changes only configurations with a cap, none below), so a
rerun with `--target 100` differs by under a bit and a few queries. "Unique-decoding" uses only
confirmed bounds; "johnson-dkt26" depends on P4 and P5.

### Cross-checks against shipped parameters and measurements

| Configuration | Queries | Classical bits | QROM bits | Weakest round | Size estimate (KiB) |
|---|---|---|---|---|---|
| A leanVM as shipped (unique-decoding) | [55, 32, 23, 20] | 31.5 | 18.0 | final | 95 |
| A leanVM as shipped (johnson-dkt26 (UNCONFIRMED)) | [55, 32, 23, 20] | 85.7 (85.6 after C-14) | 45.2 | fold3.0 | 95 |
| B KoalaBear bench100 (measured 1,428,394 B) | 100 | 52.4 | 28.3 | query | 1302 |
| B KoalaBear q100 (measured 1,809,036 B) | 110 | 120.2 | 61.7 | query | 1614 |
| B Plonky3 binary folding (measured 434,434 B) | 245 | 96.5 | 50.3 | query | 293 |

### System A, unique-decoding, target 100 QROM bits

| Configuration | Queries | Classical bits | QROM bits | Weakest round | Size estimate (KiB) |
|---|---|---|---|---|---|
| A leaf (unique-decoding) | [199, 184, 182, 182, 182] | 190.6 | 100.3 | query0 | 1075 |
| A bundle (unique-decoding) | [199, 184, 182, 182, 182, 182] | 190.6 | 100.3 | query0 | 1466 |
| A merge1 (unique-decoding) | [199, 184, 182, 182, 182, 182] | 190.6 | 100.3 | query0 | 1466 |
| A merge2 (unique-decoding) | [199, 184, 182, 182, 182] | 190.6 | 100.3 | query0 | 1167 |
| chain leaf to merge2 | | | 98.3 | union bound | |

### System A, johnson-dkt26 (UNCONFIRMED), target 100 QROM bits

| Configuration | Queries | Classical bits | QROM bits | Weakest round | Size estimate (KiB) |
|---|---|---|---|---|---|
| A leaf (johnson-dkt26 (UNCONFIRMED)) | [94, 53, 37, 29, 23] | 190.6 | 100.2 | query0 | 328 |
| A bundle (johnson-dkt26 (UNCONFIRMED)) | [94, 53, 37, 29, 23, 20] | 190.6 | 100.2 | query0 | 404 |
| A merge1 (johnson-dkt26 (UNCONFIRMED)) | [94, 53, 37, 29, 23, 20] | 190.6 | 100.2 | query0 | 404 |
| A merge2 (johnson-dkt26 (UNCONFIRMED)) | [94, 53, 37, 29, 23] | 190.6 | 100.2 | query0 | 355 |
| chain leaf to merge2 | | | 98.2 | union bound | |

### System B, unique-decoding, target 100 QROM bits

| Configuration | Queries | Classical bits | QROM bits | Weakest round | Size estimate (KiB) |
|---|---|---|---|---|---|
| B leaf (unique-decoding) | 199 | 190.6 | 100.3 | query | 576 |
| B bundle (unique-decoding) | 199 | 190.6 | 100.3 | query | 1163 |
| B merge1 (unique-decoding) | 199 | 190.6 | 100.3 | query | 1163 |
| B merge2 (unique-decoding) | 199 | 190.6 | 100.3 | query | 1112 |
| chain leaf to merge2 | | | 98.3 | union bound | |

### System B, johnson-dkt26 (UNCONFIRMED), target 100 QROM bits

| Configuration | Queries | Classical bits | QROM bits | Weakest round | Size estimate (KiB) |
|---|---|---|---|---|---|
| B leaf (johnson-dkt26 (UNCONFIRMED)) | 94 | 190.6 | 100.2 | query | 300 |
| B bundle (johnson-dkt26 (UNCONFIRMED)) | 94 | 190.6 | 100.2 | query | 590 |
| B merge1 (johnson-dkt26 (UNCONFIRMED)) | 94 | 190.6 | 100.2 | query | 590 |
| B merge2 (johnson-dkt26 (UNCONFIRMED)) | 94 | 190.6 | 100.2 | query | 563 |
| chain leaf to merge2 | | | 98.2 | union bound | |

### System B alternative (KoalaBear FRI, narrow Keccak AIR), leaf, target 100 QROM bits

| Configuration | Queries | Classical bits | QROM bits | Weakest round | Size estimate (KiB) |
|---|---|---|---|---|---|
| B-alt KoalaBear leaf (unique-decoding) | 199 | 190.6 | 100.3 | query | 1325 |
| B-alt KoalaBear leaf (johnson-dkt26 (UNCONFIRMED)) | 94 | 190.6 | 100.2 | query | 674 |

Reading the cross-checks: under the bounds implemented here, leanVM's shipped parameters (which
claim 125 RBR bits through the affine-combiner bound) give 31.5 classical bits with unique
decoding and 85.7 with DKT26 (85.6 after C-14). The gap is entirely in which proximity bound is
accepted: leanVM's own bound is CWYZ26's (read 2026-11-19, C-19), which the tool does not
implement; R-5 now asks for that implementation and for the review of leanVM's appendix B
theorem.

The same tables at 64 QROM bits (the plan's 128-bit classical level) are produced by
`uv run yugen-soundness --target 64`: the Johnson-regime leaf is about 218 KiB for A and 198 KiB
for B.

### Parameter sets meeting 100 QROM bits

All at rate 1/16, 256-bit challenge field, 384-bit Keccak digests inside the proof, 32-byte salts
on every opened leaf, query grinding 20 bits (counted as 10 against a quantum adversary).

| System, regime | Queries per round | Other grinding | Leaf size | Bundle size |
|---|---|---|---|---|
| A (WHIR, leanVM ladder: folds 6, 4, 4, ...; rate +3 then +3 per round), unique decoding | 199, 184, 182, 182, 182 | fold 6, OOD 6 | about 1,075 KiB | about 1,466 KiB |
| A, Johnson (DKT26, unconfirmed) | 94, 53, 37, 29, 23 | fold 6, OOD 6 | about 333 KiB | about 423 KiB |
| B (BaseFold, fold 4), unique decoding | 199 | none | about 576 KiB (model under-estimates by about 30%) | about 1,163 KiB |
| B, Johnson (DKT26, unconfirmed) | 94 | none | about 300 KiB | about 590 KiB |
| B-alt (KoalaBear octic FRI, arity 8, narrow Keccak AIR), unique decoding | 199 | fold 8, batch 8 | about 1,325 KiB | not modelled |
| B-alt, Johnson (DKT26, unconfirmed) | 94 | fold 8, batch 8 | about 674 KiB | not modelled |

The measured `q100` KoalaBear run (110 queries, octic, 384-bit digests, rate 1/16, grinds
24/16/16) gives 61.7 QROM bits under unique decoding in this tool: the measured configuration was
built before the calculator, and 199 queries are needed at that rate under confirmed bounds.

## 5. What this method does not cover

- The statement's own soundness (missing constraints): addressed by the single constraint list,
  coverage and mutation tests (plan §9), not by this tool.
- Knowledge soundness and simulation-extractability: F1 and F2 have knowledge-soundness
  counterparts in the same book (Theorems 26.1.1 and 31.3.1, confirmed as statements); RBR
  knowledge soundness: WHIR, ePrint 2024/1586, Theorem 5.2 (round-by-round soundness of the IOPP)
  and Theorem 7.5 (round-by-round knowledge soundness of the compiled polynomial IOP, under the same
  mutual-correlated-agreement hypothesis), statements read 2026-11-19, proofs not checked; FRI:
  Block, Garreta, Katz, Thaler, Tiwari, Zając, *Fiat-Shamir Security of FRI and Related SNARKs*,
  ePrint 2023/1071 (copy dated February 15, 2024), read 2026-11-19 (C-18): Theorems 4.1, 4.2
  (round-by-round soundness of FRI and batched FRI, `max{(m + 1/2)^7 |L0|^2 / (3 rho^(3/2) |F|),
  (1 - delta)^l}`, `delta < 1 - sqrt(rho) - eta`, `eta < sqrt(rho)/(2m)`, `m >= 3`), Theorem 5.11
  (the round-by-round knowledge error equals it), Corollaries 4.3, 4.4 (compiled: `Q eps_rbr +
  3 (Q^2 + 1)/2^kappa` classically, `Theta(Q eps_fs)` quantumly, restating CMS19). Hypotheses:
  `L0` a smooth multiplicative subgroup, binary folding (its Algorithm 1), the BCIKS20 Johnson error
  only. So it covers neither System A (WHIR on binary additive domains) nor System B on Binius64
  (binary BaseFold); for B-alt (KoalaBear FRI, multiplicative) it covers the binary-fold case in the
  Johnson-form error, not arity 8 and not the unique-decoding terms the tool uses (BCIKS20 Theorem
  1.2 with P3). Nothing numeric rests on it.
  Simulation-extractability (plan §4) needs its own review (Chiesa–Fenzi, TCC 2024, cited by the
  plan from memory).
- Zero knowledge: the BCS zero-knowledge bound `zeta_ARG <= zeta_IOP + sum_i zeta_MT,i + t / 2^s_FS`
  is the SNARGs book's Theorem 26.2.1 (confirmed). The original statement, read in the citation
  audit of 2026-11-19, is Ben-Sasson, Chiesa, Spooner, "Interactive Oracle Proofs", ePrint
  2016/116, Theorem 7.1 / Lemma 7.5: `z' = z + p(x) 2^(-lambda/4 + 2)`, statistical, for `2 lambda`-bit
  salts, in the explicitly-programmable random oracle model; the tool uses the book's form. The
  IOP's own HVZK is not computed by the tool. Its sources are now read: Chiesa, Fenzi,
  Weissenberg, ePrint 2026/391, revision of 2026-11-16 (perfect HVZK on fresh inputs for the
  Reed-Solomon instantiation, Section 10.1 and Section 11 "Security"); Haböck and Al Kindi,
  ePrint 2024/1037, Section 4.2 (Lagrange decomposition: `n_F + n_D <= h_p` and
  `2 (e n_F + n_D) <= h <= |H|`, inequalities (16), (17), Lemma 5; the batch mask `R` of
  Protocol 2, Lemma 2), which is what Plonky3's hiding FRI cites.
- Hash collisions on chain (plan §9 table): separate from proof soundness.

## 6. Checklist for the external cryptographer (E3)

1. Confirm F3's constants (CMS19 Section 8.5.1: `C1 = 6`, `C2 = 24`, read in the citation audit)
   and that Theorem 8.6 covers the transcripts as built (finding C-7), and the formalisation of the
   targets in section 8 (conditions C, Q, G, H).
2. Confirm F5 (grinding under quantum adversaries); F4 is ethSTARK Theorems 6 and 8 (read,
   classical ROM, C-17). F5 matters only with grinding: with 20-bit query grinding, condition Q of
   `cat1` holds only if grinding counts in the QROM (section 8.4); the shipping rows use none.
3. P4 and P5 are DKT26 Theorem 4.4 (read, C-14, C-15): confirm the proof (it rests on BCHKS's
   interpolant dimension count, not read here); check leanVM's appendix B theorem against CWYZ26
   Theorem 4.10 (the transcription was checked, C-19), which the tool does not implement.
4. The WHIR round list was checked against ePrint 2024/1586 Theorem 5.2 (C-9); confirm a theorem
   for WHIR on binary additive codes (C-10). The BaseFold round list was checked against ePrint
   2024/504 and 2024/1571 (C-12); confirm that Haböck's round-by-round analysis carries over to
   unique decoding with the errors used here.
5. Confirm C1 to C3 for recursion, and the heuristic C2 is acceptable for a capped pool (plan §9).
6. Check the parameter sets in section 4 by recomputation.

## 7. Sources

| Source | Where read | Status |
|---|---|---|
| A. Chiesa, E. Yogev, *Building Cryptographic Proofs from Hash Functions*, https://snargsbook.org (PDF from the book's GitHub repository, 2026 build) | Theorems 25.2.1, 26.1.1, 26.2.1, 31.2.1, 31.3.1, §28.3.2 | confirmed |
| E. Ben-Sasson, D. Carmon, Y. Ishai, S. Kopparty, S. Saraf, *Proximity Gaps for Reed–Solomon Codes*, ECCC TR20-083 (ePrint 2020/654) | Theorems 1.2, 1.4, 1.5, 1.6, 4.1, Remark 1.2 (BCIKS20 numbers follow the folder copy, ePrint 2020/654 revision of July 3, 2021 (`2020-654.pdf` (see REFERENCES.md)); the ECCC TR20-083 copy of May 30, 2020 numbered the affine-space theorem 1.7, the curve theorem 1.6 and the extension-field remark 1.5 (amended 2026-11-19, `CITATION-AUDIT.md` C-41)) | confirmed |
| A. Chiesa, P. Manohar, N. Spooner, *Succinct Arguments in the Quantum Random Oracle Model*, ePrint 2019/834 (copy dated January 14, 2020; the copy states no venue) | read 2026-11-19: Sections 1.2, 4.2 (Lemma 4.9), 5 (Lemmas 5.9, 5.10, 5.13), 6.3 (Lemmas 6.10, 6.11), 7.1 (Lemma 7.3), 8 in full | confirmed: Theorem 8.6, `C1 = 6`, `C2 = 24` (C-6); hypotheses C-7, C-8 |
| N. Spooner, *Succinct Non-Interactive Arguments for Arithmetic Circuits*, PhD thesis, UC Berkeley, Technical Report UCB/EECS-2020-182, https://www2.eecs.berkeley.edu/Pubs/TechRpts/2020/EECS-2020-182.pdf | §5.10 (BCS in the QROM: "adaptive knowledge error O(t^2 kappa_rbr + t^3 2^-lambda) in the QROM"; §5.10.5: "<= 6 t^2 kappa_rbr + O(t^3 2^-lambda)" by CMS19 Lemma 5.13) | confirmed (read) |
| NIST, *Post-Quantum Cryptography: Security (Evaluation Criteria)*, https://csrc.nist.gov/projects/post-quantum-cryptography/post-quantum-cryptography-standardization/evaluation-criteria/security-(evaluation-criteria) | categories 1 to 5, MAXDEPTH, the gate-count table | confirmed (read 2026-11-18) |
| C. Zalka, *Grover's quantum searching algorithm is optimal*, Phys. Rev. A 60 (1999), arXiv quant-ph/9711070 | abstract: "quantum searching cannot be parallelized better than by assigning different parts of the search space to independent quantum computers" | confirmed (abstract) |
| Bünz, Chen and Guan (authors as a search result gave them), *It Takes Two: Proofs of Work for Fiat–Shamir*, ePrint 2026 (number not recorded) | search-result summary only | not read; relevant to F4/F5 |
| G. Arnon, A. Chiesa, G. Fenzi, E. Yogev, *WHIR: Reed–Solomon Proximity Testing with Super-Fast Verification*, ePrint 2024/1586 (copy dated November 21, 2024) | read 2026-11-19: Sections 4.1 to 4.4 (Theorem 4.3, Theorem 4.8, Definition 4.9, Lemma 4.10, Corollary 4.11, Conjecture 4.12, Lemma 4.25), Construction 5.1, Theorem 5.2, statement of Theorem 7.5 | confirmed (term list, C-9); Johnson regime and additive codes not covered (C-10) |
| B. E. Diamond, J. Posen, *Polylogarithmic Proofs for Multilinears over Binary Towers*, ePrint 2024/504 (the copy states no date or venue) | read 2026-11-19: Sections 1.3 (ring switching, Hashcaster), 2.6, 2.7, 3.1 (Construction 3.1, Theorem 3.5), 4.3 (Construction 4.12, Theorem 4.17 with Propositions 4.21 to 4.24), 5.2 (equation (42)) | confirmed: B's query and fold terms (C-12); ring switching (C-13) |
| U. Haböck, *Basefold in the List Decoding Regime*, ePrint 2024/1571 (the copy states no date; a revision of the author's earlier preprint) | read 2026-11-19: Sections 3, 4 (Theorems 2, 3, 4), 5 (Lemmas 1 to 3, 5.4), 6.1 to 6.4 (Lemmas 4 to 8, Theorem 6) | confirmed as statements (proofs read for Lemmas 1 to 3, 5, 6 to 8); C-11, C-12 |
| Q. Dao, S. D. Kominers, J. Thaler, *Reed–Solomon Codes Beyond Johnson: Efficient Decoding and Smaller Cryptographic Proofs*, ePrint 2026/2056 (copy dated November 2, 2026) | read 2026-11-19: Sections 1, 3.1, 4.2, 4.3 (Lemma 4.3, Theorem 4.4), 6 (Lemma 6.2, Corollaries 6.3, 6.4, 6.6, 6.7, Remark 6.1), 7.1, 7.2, Appendix B (B.1 end, B.2, B.3) | confirmed: P4, P5 (C-14, C-15) |
| E. Crites, A. Stewart, *On Reed–Solomon Proximity Gaps Conjectures*, ePrint 2025/2046 | abstract page | confirmed (what is disproved) |
| A. Chiesa, G. Fenzi, G. Weissenberg, *Zero-Knowledge IOPPs for Constrained Interleaved Codes*, ePrint 2026/391, revision of 2026-11-16 | read 2026-11-19 (sections listed in `REFERENCES.md`) | confirmed (construction; its parameters use the Johnson-bound MCA result and 24 grinding bits at a 100-bit target, Section 1.3, which this method does not use) |
| E. Ben-Sasson, A. Chiesa, N. Spooner, *Interactive Oracle Proofs*, ePrint 2016/116 (copy of 2016-02-10) | read 2026-11-19: Theorems 1.2, 1.5, 7.1, Lemmas 3.4, 7.5 | confirmed: soundness `sbar_sr(x, m) + 3 (m^2 + 1) 2^-lambda` (Theorem 7.1), of which the book's `3.5 t^2 / 2^lambda` is the later form; zero knowledge as above |
| U. Haböck, Al Kindi, *A note on adding zero-knowledge to STARK*, ePrint 2024/1037 (revision of 2025-02-20) | read 2026-11-19, pages 1 to 16 | confirmed (Section 4.2 bounds) |
| B. E. Diamond, *Zero-Knowledge Polynomial Commitment in Binary Fields*, ePrint 2025/1015 | read in full 2026-11-19 | confirmed (Construction 4.1; Theorem 4.2 is a proof sketch without an explicit error) |
| A. R. Block, A. Garreta, J. Katz, J. Thaler, P. R. Tiwari, M. Zając, *Fiat-Shamir Security of FRI and Related SNARKs*, ePrint 2023/1071 (copy dated February 15, 2024) | read 2026-11-19: Sections 1, 3.4 (Theorem 3.15), 4.1 (Theorems 4.1, 4.2, Corollaries 4.3, 4.4), statement of Theorem 5.11 | confirmed as statements (C-18); covers multiplicative FRI only |
| E. Ben-Sasson, D. Brownstein, D. Carmon, L. Goldberg, D. Levit, D. Medini, A. Shtaierman, E. Yogev, *ethSTARK Documentation*, Version 1.2 (July 2023), ePrint 2021/582 | read 2026-11-19: Theorem 5 and the bound on `eps_1` (Remark 6), Section 6.3 (Theorem 6 with proof), Section 7.1 (Theorems 7, 8, Corollary 3, 7.1.1) | confirmed: F4 (classical), the ALI form (C-17) |
| A. Chiesa, G. Weissenberg, E. Yogev, K. Z. Zheng, *Affine Combiners for Reed–Solomon Proximity Gaps* (CWYZ26), ePrint 2026/2863 (copy dated November 13, 2026) | read 2026-11-19: Sections 1, 4.1 (Lemma 4.2, equation (4.1)), Theorem 4.10, Section 5 (Theorems 5.1, 5.2, Remark 5.3), Section 6 (Propositions 6.1 to 6.3) | confirmed: leanVM's `eps_aff` (C-19); not implemented |
| Plonky3 `p3-security` (https://github.com/Plonky3/Plonky3, `security/src`, commit `0d803737`) | read in full where cited | secondary source |
| leanVM appendix B (https://github.com/leanEthereum/leanMultisig, `doc/leanvm`, commit `84780fb4`) | read | secondary source |

## 8. Named targets: NIST category 1 (`cat1`) and category 3 (`cat3`)

Implemented in `soundness/src/yugen_soundness/targets.py`; tests in `tests/test_soundness.py`.

### 8.1 What NIST defines (primary source, read 2026-11-18)

*Revision 7 (2026-11-19): verified against the call for proposals itself, [CFP] Section 4.A.5,
pages 16 to 18 (`REFERENCES.md` 1.1f); the summary below matches it, except that NIST names
"SHA256/ SHA3-256" and "SHA384/ SHA3-384" as the references of categories 2 and 4. Section 8.7
derives every category's conditions from that text, and corrects 8.2's gate comparison for G.*

NIST's evaluation criteria define the categories by comparison: category 1, "any attack that
breaks the relevant security definition must require computational resources comparable to or
greater than those required for key search on a block cipher with a 128-bit key (e.g. AES128)";
category 2, collision search on a 256-bit hash (SHA3-256); category 3, key search on a 192-bit
key (AES192); category 4, collision search on a 384-bit hash. NIST measures quantum attacks in
circuit size under a depth limit MAXDEPTH (plausibly 2^40 to 2^96 logical gates) and gives
AES-128 key search as 2^170/MAXDEPTH quantum gates or 2^143 classical gates, SHA3-256 collision
as 2^146 classical gates, AES-192 as 2^233/MAXDEPTH quantum or 2^207 classical, SHA3-384
collision as 2^210 classical. Higher categories are ordered above lower ones. The categories are
**attack-cost** definitions, not proven-security definitions.

### 8.2 The lead architect's definition, and where it needs correcting

The task defined `cat1` per proof layer as (i) at least 128 classical bits from proven bounds,
(ii) the best quantum attack on Fiat–Shamir costs at least 2^64 sequential oracle evaluations
after counting grinding at half its bits, (iii) 256-bit Keccak digests, (iv) the four-layer chain
still meets (i) and (ii). Checked against the source and the QROM literature:

- **(i) is sound and is the binding condition**, with one correction: the BCS bound has two
  terms, the IOP term and the hash term `3.5 t^2 / 2^lambda` (SNARGs book Thm 25.2.1). With
  `lambda = 256` the hash term caps proven classical soundness at `(255 - log2 3.5) / 2 = 126.6`
  bits per layer, under 128 and under the 130 the chain needs. Proven 130 bits per layer needs
  `lambda >= 263`, i.e. 264-bit (33-byte) digests. So (i) and (iii) as written are inconsistent
  by 3.4 bits. The calculator offers both rules (8.3, condition H).
  *Revision note (2026-11-19, revision 10, 8.10):* for the spBCS transcript the hash term is [SG26]
  Theorem 6.6 (2)'s `c' (t + k_q)^2 / 2^(8b)` per proof; summed over the tree it caps the proven classical
  level at 114.74 bits, and a proven 128 needs 288-bit digests.
  *Amendment (2026-11-19, calculator revision 10.2, after `docs/tree-extraction-referee.md`; not a rewrite):* every TREE figure in this passage is conditional, not an unconditional theorem. It holds under the recursion heuristic C2 (the event "accepted in-circuit, rejected natively" does not occur; no random-oracle proof can remove it), the owed obligations K-A and K-B (round-by-round knowledge soundness) and T-1 (the transcripts' domain separation and fit to [SG26] Protocol 6.5). Under Theorem TE' (`docs/lemma-tree-extraction.md` revision 2) the classical hash level of the tree is **121.89 bits at category 1** (185.89 / 249.89 at categories 3 / 5), printed with the per-proof union (114.74 / 178.74 / 242.74) beside it as the comparison; the tree's QROM figures are derived under C2, never "proven QROM". Status of every claim: `docs/what-is-proven.md`.
- **(ii) is right as an attack estimate but is not NIST's formalisation.** NIST bounds depth,
  not sequential evaluations. Under a depth limit `D` (in oracle calls), parallel Grover over a
  bad set of density `2^-e` succeeds with probability about `P D^2 2^-e` using `P` machines
  (Zalka: no better parallelisation exists), so it needs about `2^e / D` oracle calls in total.
  AES key search over `2^e` keys needs the same `2^e / D` AES calls. Hence the correct statement
  of (ii) is **per round, `e = round bits + grinding bits >= 128`** (192 for `cat3`), which matches
  AES-128 for every MAXDEPTH, not only at `D = 2^64`. "Grinding at half its bits" is then not a
  separate rule: the round's own bits and the grinding bits are halved together because they
  multiply the same density. This needs one more assumption: a Fiat–Shamir oracle call (at least
  one Keccak-f[1600], 24 rounds of 1,600 two-input ANDs = 38,400 AND gates) costs at least one
  AES-128 evaluation (about 6,400 AND gates with the Boyar–Peralta S-box, 200 S-box calls).
  These gate counts are **from memory, not confirmed**; the ratio of about 6 means a Keccak call
  is the more expensive oracle, so the comparison is conservative.
- **(ii) also has a proven counterpart**, which the definition should state: CMS19 gives
  `eps_Q(t) <= 6 t^2 eps_rbr + 24 t^3 / 2^lambda` (Theorem 8.6, constants from its proof in
  Section 8.5.1; C-6). Requiring 64 proven QROM bits per chain (66 per layer) needs
  `e >= 2 * 66 + 1 + log2 6 = 135.6` per round and `lambda >= 199 + log2 24 = 203.6`. This is
  condition Q below. Under `cat1` it is implied by (i) (which needs `e` of about 136 to 137), so it
  costs nothing, and it turns the attack estimate into a theorem (up to F5 and `C2`).
- **(iii) holds as an attack-cost statement**: a generic Merkle or transcript collision on a
  256-bit Keccak costs 2^128 classical hash calls, which is NIST's own category-2 benchmark
  (2^146 gates), ranked above category 1. The quantum collision figure of about 2^85 (BHT with
  quantum random-access memory) and about 2^102 without it (2^(2n/5)) are **from memory**. The
  proven QROM hash term `24 t^3 / 2^256` caps QROM soundness at 83.5 bits per layer (85 before C-6),
  above the 66 needed.
- **(iv)**: with a union bound over four layers (C1 in section 2.4), the chain loses
  `log2 4 = 2` bits, so every per-layer requirement is the chain requirement plus 2.

### 8.3 The conditions the calculator checks

For one layer with `k` rounds, `e_min` the smallest effective bits over rounds (round bits plus
grinding), `lambda` the digest length:

| | Condition | `cat1` | `cat3` | Kind |
|---|---|---|---|---|
| C | proven classical IOP term `e_min - 1 - log2(1 + k)` | >= 130 | >= 194 | theorem (book Thms 25.2.1, 31.2.1) plus F4 for grinding |
| Q | proven QROM IOP term `(e_min - 1 - log2 6) / 2`, and QROM hash cap `(lambda - 1 - log2 24) / 3` | >= 66 | >= 98 | theorem (CMS19 Theorem 8.6, `C1 = 6`, `C2 = 24`, Section 8.5.1) plus F5 for grinding; for the construction CMS19 analyses (C-7) |
| G | every round `e >= ` | 128 | 192 | attack estimate (Grover under MAXDEPTH, Zalka; Keccak-f >= AES gate count, from memory) |
| H, attack rule | `lambda >=` | 256 | 384 | attack estimate (NIST's own collision benchmarks, categories 2 and 4) |
| H, proven rule | `lambda >=` | 264 | 392 | theorem (book Thm 25.2.1 hash term >= 130 / 194 bits) |
| Chain | union bound over leaf, bundle, merge 1, merge 2 | 128 classical, 64 QROM | 192, 96 | C1 (section 2.4) and the recursion heuristic C2 |

C and Q need nearly the same effective bits per round: C needs `131 + log2(1 + k)`, 135.6 to 136.4
at `k` of 22 to 40 rounds, and Q needs 135.6, so C binds for `k > 22` (every recursion layer)
and the two tie for the leaf; G (128) never binds. The tool reports C and Q of the IOP term
separately from the hash cap.

**Challenge field.** An algebraic round (sumcheck/fold, OOD, combination) has error at least
about `n / |F|` below unique decoding, `n` the codeword length (2^27 to 2^32 here). `cat1` needs
about 136 bits per round, so `|F| >= 2^(136 + 32) = 2^168`: **GF(2^192) is the smallest binary
extension that reaches `cat1` without grinding**, and `cat3` (about 200 bits per round) needs
GF(2^256). With GF(2^256) from the start, moving from `cat1` to `cat3` changes only query
counts, the fold schedule and the digest length: parameters, if both verifiers read them from a
table rather than from constants.

### 8.4 GF(2^128) at `cat1`

Not enough under proven bounds. The weakest algebraic round of a leaf has `128 - log2 n - 1`, about
100 bits (A, `n = 2^28`) or 105 (B, `n = 2^23`), against about 136 needed. Grinding can close the
gap only at 31 to 41 bits on each of 16 to 26 algebraic rounds: `2^35` to `2^46` Keccak-f per
proof, 1.2 to 2,000 hours on one M5 thread (table in `soundness/output/design-tables.txt`). The
Johnson-regime bounds are worse at this field size (they add list-size factors). The other way to
keep GF(2^128), two independent challenges per fold round, changes the protocol of both
frameworks and is not proposed; the larger field is the cheaper fix.

### 8.5 Grinding under the quantum adversary (F5) and the recommended grind

Condition C relies on classical grinding (F4, standard). Condition Q with 20-bit query grinding
relies on F5: without grinding, the queries alone give `e` of about 116 and Q fails (56 QROM bits).
With zero query grinding, the queries needed for C (about 136 bits per round) also give Q
without F5, at about 15% more proof bytes (`design-tables.txt`, grinding trade). Until E3 confirms
F5, **query grinding of 20 bits is used only for the classical condition and the parameter set
with grinding 0 is the one that meets Q unconditionally**; `design-basis.md` gives both.

### 8.5a The whole proof tree (first revision, 2026-11-19; superseded by 8.5b)

A block's tree holds about 1,700 proofs and a forger needs one false proof accepted. The union
bound over a four-layer chain (2 bits) is replaced by the tree target `wi.TreeTarget`
(`zk-wi-soundness.md` section 8.3): shared-budget model, C: `e >= 128 + 1 + log2(1 + proofs * k)`,
Q: `e >= 2 * 64 + 1 + log2 6 + log2(proofs)`; about 144 bits per round instead of 136
(`log2 1700 = 10.7`). Attempts over many blocks cost nothing in this model (a failed attempt is
oracle queries, which `t` counts); the union model with `attempts` is available for comparison.
NIST's categories are per-instance comparisons (from memory for the multi-target wording); the
tree-wide claim is the stronger one and is the one adopted. The hash term is unaffected. The
multi-instance reading of the book's Theorem 31.2.1 and the QROM factor `proofs` are our
arguments (review sheet item 16 of that document). The hiding openings (W-I for A, W-M for B) add
the rounds of `wi.rounds` / `wi.full_mask_rounds`.

### 8.5b The tree model of the shipping rows (2026-11-19, revision 2)

This is the model `design-basis.md` section 2a uses (`soundness/src/yugen_soundness/shipping.py`,
`ProofTreeTarget`); it replaces 8.5a's 1,700-proof shared-budget figure. Statement-level
notation: `S` is the tree shape (sub-bundles of at most 64 leaves, two merge levels of arity at most
16), `N = 2^14 + 2^8 + 2^4 + 1 = 16,657` the number of proofs of the largest tree of shape `S`,
`H` the random oracle (Keccak-256 for every transcript and Merkle tree, domain separated),
`lambda` its output length, `k_v` the number of rounds of proof `v` (every round of its IOP: the
opening's rounds and the zerocheck, table sumcheck, bus GKR, Keccak reduction, ring switch and
batching rounds; `k_v <= k`), `eps_rbr,v` its round-by-round soundness error (the largest error
over its rounds) and `e = -log2 eps_rbr` the effective bits of its weakest round.

**Definition (tree forgery).** An adversary `A` makes at most `t` queries to `H` (classical
queries; for the quantum statement, superposition queries) and outputs a tree `T` of shape `S`:
for each node `v`, a statement `x_v` and a proof `pi_v`, where a node's statement names its
children's statements (a sub-bundle's statement fixes its leaves' public inputs, a merge's its
children's digests). `A` wins if the native verifier accepts the root proof for the root statement
and some leaf statement is false (no witness exists). `eps_tree(t) = Pr[A wins]`. The target is

- classical: `eps_tree(t) <= t / 2^128` for every `1 <= t <= 2^128` (the book's average-case
  bits of security, section 28.3.2, at `kappa = 128`);
- quantum (proven, CMS19): `eps_tree(t) <= t / 2^64` for every `1 <= t <= 2^64` (the per-chain
  QROM target of 8.2, now for the tree);
- attack cost (G): every round of every proof has `e >= 128`;
- digests (H): `lambda >= 256` by the attack rule; `lambda >= 259` (264 at whole bytes) for the
  proven rule (below).

**Reduction to the proofs (union bound, one attempt).** A node's statement says that every child
proof is accepted by the child's verifier for the child's statement (and the node's own checks
hold). Walk down from the root towards a false leaf: the root proof is accepted; if the root's
statement is false, the root is a proof accepted for a false statement; if it is true, the child
on the path has an accepted proof, and the same alternative repeats, down to the leaf, whose proof
is accepted while its statement is false. So some node `v` on the path has `pi_v` accepted
(natively for the root, inside its parent's circuit otherwise) while `x_v` is false. Treating an in-circuit
verification as the native one (the recursion heuristic C2 of section 2.4, which no random-oracle
proof covers) and excluding a collision among all of `A`'s queries (one event for the whole tree):

*Revision note (2026-11-19, revision 10.1, finding R10-2 of `rev10-referee.md`): the walk above argues by existence
("the child on the path has an accepted proof"), but soundness bounds only proofs the adversary outputs, and the
adversary publishes the root proof alone. The reduction is replaced by an extraction lemma, `docs/lemma-tree-extraction.md`
Theorem TE (ROM; a draft until refereed): one straight-line extractor runs the root verifier and then, node by node,
[SG26]'s database algorithm and the child verifiers on one table, and fails for an accepted root with probability at
most `t eps_max + sum_v |J_V,v| eps_v + c'_max (t + K)^2 / 2^(8b)`, `K` the sum of the tree's `k_q`. It uses C2 at
exactly one point (hypothesis H-C2: a witness of the node relation lists children the child verifier accepts against
the oracle) and the round-by-round KNOWLEDGE soundness of every proof system (obligations K-A, K-B). No certified count
moves (Corollary TE-F (a)); a black-box composition node by node would raise every need by 2.3 to 3.9 bits (section 8
there). The QROM form TE-Q is argued with one step from memory. "Proven" below means proven under these assumptions.*

*Amendment (2026-11-19, calculator revision 10.2, after `docs/tree-extraction-referee.md`; not a rewrite): the note
above is corrected in three places. (1) The referee found hypothesis H-C2 **false in the ROM** (finding F-1), so
"Theorem TE (ROM)" as stated was vacuous; it is restated as **Theorem TE'** (`lemma-tree-extraction.md` revision 2,
section 6), a true theorem of the ROM with the same bound, in which C2 is the named event C2-VIOLATION ("accepted
in-circuit, rejected natively") outside the theorem. (2) C2 enters at **two** places, not one: the child's native
acceptance, and keeping the node relation oracle-free so that (K) and Lemma TE.1 apply. (3) The QROM step "from
memory" was false as worded and is replaced by Lemma QC (section 9a there; the referee's proof, unrefereed), adding a
term of about `2^-222.9`. **Unconditional in the ROM:** the root proof, and a tree whose every proof is published
(Corollary TE-X). **Conditional on C2, K-A, K-B, T-1:** every figure of the recursion tree below, classical and quantum;
the target line "quantum (proven, CMS19)" above is a target, and the tree's QROM figures that meet it are derived
under C2, not proven. "Proven" below for a tree figure means "under these conditions". Status of every claim:
`docs/what-is-proven.md`.*

```
eps_tree(t) <= 3.5 t^2 / 2^lambda + sum over the N proofs of (t + k_v) eps_rbr,v
            <= 3.5 t^2 / 2^lambda + N (t + k) 2^-e
```

(book Theorems 25.2.1 and 31.2.1 per proof, with the collision term taken out once). The target
holds when each term is at most `t / 2^129`:

- C: `N (1 + k) 2^-e <= 2^-129`, i.e. **`e >= 129 + log2 N + log2(1 + k)`**;
- hash: `3.5 t / 2^lambda <= 2^-129` at `t = 2^128`, i.e. `lambda >= 257 + log2 3.5 = 258.8`. With
  `lambda = 256` the proven classical level is `(255 - log2 3.5) / 2 = 126.6` bits
  (`design-basis.md` finding S-2); category 1 then rests on condition H's attack rule. *Revision note
  (2026-11-19, revision 10, 8.10): under [SG26] Theorem 6.6 (2)'s own hash term, per proof and summed over the
  tree, the proven classical level is 114.74 bits, not 126.6; the attack-rule basis stands.* *Amendment (2026-11-19, revision 10.2): conditional on C2, K-A, K-B, T-1; under Theorem TE' the tree's hash part is taken once, 121.89 bits (114.74 printed beside it as the comparison).*

QROM: CMS19 per proof, `eps_Q,v(t) <= 6 t^2 eps_rbr,v + C2 t^3 / 2^lambda`, summed over the `N`
proofs: **`e >= 2 * 64 + 1 + log2 6 + log2 N`** for the IOP term; the hash term
`N C2 t^3 / 2^lambda <= t / 2^65` at `t = 2^64` needs `lambda >= 193 + log2 N + log2 C2`, about 212
with `C2 = 24` (CMS19 Section 8.5.1; 207 with the `C2 = 1` assumed before C-6), met by 256. With `N = 16,657` (`log2 N = 14.02`) and
`k = 512 + ` the opening's rounds (about 530), C needs **152.1 bits a round** and Q 145.6, so C
binds; at `cat3` (192 and 96 bits) C needs 216.1. The calculator solves every opening of every
proof for C, Q and G at once (`TreeTarget._cq`, model `union`, `attempts = 1`).

`k` counts every round of the proof, not only the opening's: `shipping.OTHER_ROUNDS = 512` stands
for the rounds outside the openings (an upper figure, **E**: leanVM's bus GKR over product trees
of depth about 22 alone is about 253 sumcheck rounds). Those rounds must themselves meet `e`;
at a 256-bit field their errors are at most about `2^-220` (degree over the field size) and do, and
the bus fingerprint's Schwartz-Zippel error `n / |F|` is of the same size as a fold round's.

**What a multi-attempt attacker changes: nothing.** An attacker that tries many candidate trees
for one block before publishing one spends oracle queries on each try; all of them are in `t`.
The bound is a bound on success per unit of work, which is what grinding over candidates buys.

**What a multi-block attacker changes: nothing in the bits; the probability adds up over the
work.** Let `A` publish one tree in each of `B` blocks (all against the same oracle), win if any of
them is a forgery, and make `t_b` queries for block `b`, `T = sum t_b` in all. The union over the
blocks gives

```
eps(T) <= 3.5 T^2 / 2^lambda + sum_b N (t_b + k) 2^-e <= 3.5 T^2 / 2^lambda + sum_b t_b N (1 + k) 2^-e
       <= 3.5 T^2 / 2^lambda + T / 2^129
```

using `t_b + k <= t_b (1 + k)` for `t_b >= 1`. So the classical guarantee holds for the attacker's
total work across all blocks with the same `e`: no `log2 B` term. The same holds in the QROM
(`sum_b t_b^2 <= T^2`). What does grow with `B` is the absolute probability at a fixed budget per
block: an attacker with `2^w` queries a block for `2^20` blocks wins with probability at most
`2^(w + 20 - 128)`, exactly as a key search against `2^20` AES-128 keys does. NIST's categories are
stated per instance (one key, one tree); the tree-wide, per-block claim is the one made here, and
the lifetime claim is "total work `T`, success at most `T / 2^128`". The `attempts` parameter of
`wi.TreeTarget` (union model) charges `log2 attempts` because it gives every attempt the whole
budget `t`; under the definition above that charge is not needed and the shipping rows do not
apply it.

**G under many proofs.** A Grover search for a bad challenge in any of the `N` proofs searches a
set of density at most `N 2^-e`; with `e >= 152.1`, `e - log2 N = 138 >= 128`: G holds tree-wide
at `cat1` (and `216.1 - 14.0 = 202 >= 192` at `cat3`).

**What is a theorem, what is our argument, what is a heuristic.**

| Step | Status |
|---|---|
| Per-proof `(t + k) eps_rbr` and the hash term (book Thms 25.2.1, 31.2.1) | theorem (ROM) |
| The collision term counted once for the tree | follows from the book's proof structure (the hash term bounds one event over all queries); our reading, for review |
| Union over the `N` proofs, classical and QROM | theorem, given the per-proof bounds |
| An accepted in-circuit verification as good as a native one (C2) | heuristic; the audit feed re-verifies every leaf natively (yugen-proof-a `recursion.md` 4) |
| CMS19's constants `C1 = 6`, `C2 = 24` (Theorem 8.6, Section 8.5.1) | both read (C-6); the theorem is for CMS19's BCS variant, the built transcripts' fit is open (C-7) |
| The multi-block argument | elementary from the union bound and the linearity of the classical bound in `t`; for review |
| `OTHER_ROUNDS = 512` | estimate; the count is a task (`design-basis.md` S-1) |
| Binius64's query and fold bounds (8.5c) | terms confirmed against DP24 (ePrint 2024/504, Propositions 4.21, 4.24, equation (42)); their round-by-round form is Haböck's (ePrint 2024/1571, Theorems 1, 6) by the paper's own remark for unique decoding (C-12) |

For the external review (section 6), add: 7. check the tree definition and the reduction to the
proofs above, in particular the collision term taken out once and the multi-block step; 8. check
that the built node programs (A: `guests/bundle_node.py`; B: `bundle/`) state exactly "every child
proof is accepted for the child's statement", which the reduction uses.

### 8.5c Revision 3: the tree of specification 0.3, A's full round list, B on Binius64 (2026-11-19)

`soundness/src/yugen_soundness/current.py`, `binius64.py`; `uv run yugen-soundness --current`;
`design-basis.md` section 2a. The model of 8.5b is unchanged; three inputs change.

**The tree.** Sub-bundles of at most 16 leaves, three merge levels of arity at most 16, at most
2^14 leaves; packed full, `N = 2^14 + 2^10 + 2^6 + 2^2 + 1 = 17,477` (`log2 N = 14.09`). The
count assumes every node but the last of its level is full; a tree of single-child nodes would
hold `5 x 2^14 = 81,920` proofs (`TreeShape.proofs_any_packing`, +2.2 bits a round;
`design-basis.md` S-11).

**System A's round list** (`wi.rounds(c, "A", wi.A_WALLET_ZK)`). Each term is a new verifier
message, so each also adds one to `k`; none duplicates a round of the opening or a round counted
in `OTHER_ROUNDS`, which counts the unmasked prover. Units `1/q`:

| Rounds | Term each | Source |
|---|---|---|
| W-I: `mask_i`, `fold_i.j`, `query_i`, `bc`, `final` | 1; `n + 3`; `((1 + rho_i)/2)^Q + Q/q` at the true rate `lf_i / 2^log_domain_i`; `N + 1`; `((1 + rho)/2)^Q` | `zk-wi-soundness.md` Theorem S (5.1) |
| tail sumcheck, `n_last = ceil(log2 lf_last)` rounds | 2 | `zk-system-a-gaps.md` 12.1 (a), checklist A26 (replaces A12's direct check, which had no round) |
| S4: `rho` (A4), dummy round (A21, form A8-T) | 1; 2 (form A8: 5) | gaps 3.5; `zk-wi-soundness.md` Lemma 6 |
| A20: the slice blinder's dummy round | 1 | gaps 2.4 |
| S9: `rho` per masked sumcheck (3, E) | 1 | Lemma 6 |
| A23, per Keccak layer (2): `rho`, dummy round | 1; 2 | gaps 11 |
| A24, per bus layer (11, E): `rho`, dummy round | 1; 4 (form A5: 8) | gaps 11 |
| gadget (A7): `theta`, `c`, `z` | `m - 1` (`m` = 30 claims); 1; `l` (12, E) | `zk-wi-soundness.md` 6.3; gaps 11 |
| A18, A19, A22, A25 | none | gaps 11 (A19: completeness loss `2^mu / q` only) |

All are far below the opening's terms at `q = 2^256`; their effect is on `k` (A's leaf: 68 listed
rounds) and on nothing else. The counts marked E are upper readings of
`yugen-proof-a-zk/docs/zero-knowledge.md` 11.1, not counted from the code (`wi.AZk`).

**True rates.** `wi.layout` is the built layout (`verifier/src/wi.rs::layout`: carried slots,
`kappa` guard slots, `1 + 4 kappa` aux coefficients, four rows each at level 0, uniform
coefficients at a multiple of `2^ceil(log2(t + kappa))`, `lf = lrow + kappa`); a test reproduces
the built unit test's lane lengths 524,733 / 65,923 / 8,448 / 1,280. `row_schedule` reproduces
`derive_config_for`, domain reductions included.

**System B, Binius64** (`binius64.rounds`). One proof's listed rounds and their status:

| Round | Error | Status |
|---|---|---|
| query: `gamma` test queries at the code's rate, through every layer | `((1 + rho)/2)^gamma` | the code computes exactly this count (S: `iop/src/fri/common.rs:456-460`); **confirmed**: Diamond, Posen, ePrint 2024/504, proof of Proposition 4.24 and equation (42), `(1/2 + 1/(2 * 2^R))^gamma`, unique decoding (read 2026-11-19). The same bound is our Lemma 4 / 5 for W-I |
| `fold.j`, one per folded variable: sumcheck degree 2 and the fold's proximity | `(n_j + 2)` | **confirmed as an upper bound** of DP24's terms: `2 / |L|` a sumcheck round (proof of Theorem 4.17) and `theta |S^(i+theta)| / |L|` per committed oracle (Proposition 4.21; total at most `2^(l+R) / |L|`, Proposition 4.23); the round-by-round form: Haböck, ePrint 2024/1571, Theorem 1 (C-12) |
| `mask` (leaf only): `gamma` on `M + gamma w` after the mask claim | `n + 1` | BCIKS20 Theorem 4.1 and one root for the claim, the argument of W-M (`zk-wi-soundness.md` 9): the same two events as the proof sketch of Theorem 4.2 in Diamond, ePrint 2025/1015 (read 2026-11-19; no explicit error there); the count is ours, **unconfirmed** against the Blueprint's Protocol 7.1 |
| `wrapper.blend` (leaf only) | 1 | Lemma 6 (P) |
| `inner.skip`: the univariate-skip round | 128 | Schwartz-Zippel; and **unconfirmed** until task A-3 of `yugen-proof-b2` (the fixed GF(2^8) zerocheck coordinates need constraint values in GF(2) at every caller) |
| every other round | small degree | counted in `k` by `OTHER_ROUNDS` = 512 (as `yugen-proof-b2` parameters.md 2 does; task A-2 counts them) |

Field: every algebraic round needs `log2 q >= e + log2 n`, 176 bits for the leaf (codeword 2^23)
and 181 to 184 for nodes; GF(2^128) gives 103 to 105 bits at the fold rounds and fails at any
query count (tested); GF(2^256) is the GHASH tower's next field. Queries:
`ceil(e / -log2((1 + rho)/2))` = 367 / 225 / 184 / 167 at rates 1/2 to 1/16 (tested minimal).
Sizes: an opening model (expected distinct leaves and sibling digests per tree, cap at
`ceil(log2 q)`, terminal codeword) plus other transcript fitted to the measured proofs (E;
calibration errors in `design-basis.md` 2a).

### 8.5d Revision 4: Binius64's counted rounds, the field variants, A's built masks (2026-11-19)

`binius64.py` (second part), `current.py` (`target_bound`, `a_bound_tables`, `b_tables_r4`),
`wi.A_WALLET_ZK`; tests `tests/test_revision4.py`. Analysis: `binius-extension-challenges.md`.

**Target.** `e >= 129 + log2(sum over the tree of (1 + k_i))`, the union bound of 8.5b written as
a sum (`binius64.tree_need`); the tree bound is 20,000 proofs. System B's row is solved at a budget
of 600 challenges a proof (152.52 bits); the counted sum (leaf 182, nodes at most 663) is inside
it. System A keeps `k` = listed rounds + 512 (85 listed with the built mask counts: 152.51 bits).

**Round list of one Binius64 proof** (`rounds_counted`; errors in units of `1 / |K|`, `K` the
challenge field). It replaces the short list of 8.5c; the count equals the measured census for
six proofs (tested).

| Rounds | Error each | Status |
|---|---|---|
| BinMul: `b` zerocheck coordinates, `b` sumcheck rounds | 1; 3 | Schwartz-Zippel |
| BitAnd: `a - 3` coordinates, the skip point, one batch coefficient, `n*` rounds | 1; 127; at most 10; 3 | Schwartz-Zippel; the fixed coordinates add nothing (`parameters.md` 2a.3, lemma read) |
| Zero extension, shift (4 batch coordinates, `37 + w` rounds), public input (`kappa`, `p` rounds), ring switch (`kappa`) | 1; 1, 2; 1, 2; 1 | Schwartz-Zippel; the ring switch over `GF(2) < L < K`: Theorems 1 and 2 of `binius-extension-challenges.md` (proved there, exact tests) |
| Wrapper (leaf): `c` coordinates, blend, `c` rounds, `lambda` | 1; 1; 3; 2 | Lemma 6 for the blend; Schwartz-Zippel |
| Opening: `mu`, `gamma` (leaf), `o` index rounds, `v` fold rounds | relations - 1; `n + 1`; `n + 2`; `n_j + 2` | BCIKS20 Theorem 4.1 (read; with the domain in a subfield and challenges in the extension: its Remark 1.2, read); fold rounds: DP24 Propositions 4.21, 4.23 and Haböck Theorem 1 (C-12); the `o` rounds (lifted oracles of unequal size) are in neither paper: unconfirmed ([HMH] not available) |
| Query | `((1 + rho) / 2)^q` absolute | as 8.5c |
| Node batching transcript | `K - 1`; 2; 2 | Schwartz-Zippel |

**Field variants** (`binius64.Variant`). The alphabet of a committed oracle enters sizes only;
every error is over the challenge field. A mixed variant (alphabet `GF(2^128)`, challenges
`GF(2^256)`) has the all-`GF(2^256)` build's errors by the restriction principle (Lemma 3 there).
The wrapper's constraint count is a model (two private and `2 p` public bit transpositions),
fitted to the two measured wrappers.

**Candidate regime.** `binius64.johnson_bciks` evaluates BCIKS20 Theorem 1.2's Johnson case (P2,
confirmed as a statement) at 256 bits; it is printed as a candidate only. Haböck, ePrint 2024/1571,
Theorem 6 (read 2026-11-19) proves round-by-round soundness of row-batched FRI-Binius over binary
fields in the list-decoding regime, with query error `((1 + 1/(2m)) sqrt(rho))^s` (the candidate's
count: 107 at rate 1/8, `m = 10`) and fold error `1/|F| + eps(C_i, 1, B_i, theta)` of its Theorem 3
(169.3 bits at the first fold of 2^30 points, rate 1/8, 256-bit field: the candidate's 168.2 is the
weaker BCIKS20 form). It does not cover three parts of Binius64 as built: the eq-batched ring switch,
the zero-knowledge mask round, the lifted oracles of unequal size (finding C-11).

### 8.5e Revision 5: true rates, Theorem Q per system, salt length, B's candidate rows (2026-11-19)

`revision5.py`, `qrom.py`, `salts.py`, `johnson.py`, `whir.WhirConfig.true_rate`; `uv run
yugen-soundness --rev5 [--salt {256,384,512,576}]`; tests `tests/test_revision5.py`; every changed
number before and after in `soundness/CHANGELOG.md`; adopted rows in `design-basis.md` 2a
("Revision 5"). The tree model of 8.5b and the target of 8.5d are unchanged (20,000 proofs; 512
other rounds a proof plus the listed ones).

**The true-rate rule (finding W-1).** For system A every query term of a plain WHIR level is
evaluated at

    rho_i = (2^mu_i + kappa_i) / 2^(mu_i + r_i),    query term ((1 + rho_i) / 2)^Q_i (+ (Q_i + 1)/q before the last level),

`mu_i` the variables left after the level's `kappa_i` folds, `2^(mu_i + r_i)` the rows of its
domain. Source: Theorem S0 of `whir-additive-soundness.md` (Lemmas C0, B0; Original, the Ycash
developers, 2026), which rests on BCIKS20 Theorems 4.1 and 1.6 (Published) for proximity; the
degree growth (one coefficient a round) is read from the pinned verifier's code (the final message
of `(1 << mu) + fold_count` scalars and the per-level correction by `fold_count` high
coefficients). Chiesa, Weissenberg, Yogev, Zheng, ePrint 2026/2863, Theorem 5.2 states `d + r` for
the equal-degree combiner (5.1), a different combiner, and is cited only as consistent (corrected in
revision 6 after the referee report `qrom-zk-referee.md` 3.2).
Before revision 5 the calculator used `2^-r_i` (`whir.rounds`), which understated the error where
`mu_i` is small: row 9's last level (`mu = 3`) by 4.35 bits at rate 1/2. W-I already used the true
rates of its layout (8.5c). The superseded modules (`shipping.py`, `design.py`, `params.py`) keep
their nominal rates as records; none of their rows is built.

**Schedules.** Two per shape: the rule `q_i = ceil(153.0 / -log2((1 + rho_i)/2))` (the 153.0-bit
list's own derivation with the true rate; recommended, margin 0.68 bits or more over every shape)
and the minimal per-level counts at the shape's need (no margin; each count less by one fails,
tested). Shapes: the wallet leaf `2^22` at rates 1/4 and 1/2; nodes at stacks `2^24` to `2^30` and
rates 1/2 and 1/4, which contain every node the tree allows (sub-bundles of 1 to 16 leaves, merges
of 1 to 16 children; measured stacks `2^24` to `2^28`, a merge of 16 `2^28` children under `2^29`,
E). Costs by count: opening bytes (`whir.size_bytes`), Keccak-f of verifying the proof in its
parent (leaf hash at rate 136 plus one permutation per path node, full paths: an upper figure),
cycles (E) as Keccak-f times the measured cycles per modelled Keccak-f of a verified child.
Provenance: Original (the Ycash developers, 2026).

**Theorem Q's constants.** `qrom.py` replaces the single pair `C1 = 6`, `C2 = 24` for the tree
statement by the constants of Theorem Q (`qrom-compilation.md` 5; Adapted from CMS19 Theorem 8.6
and Section 8.5.1, Published): form X (system A) `C1 = 6`, `C2 = 6 (a + 2)`, 24 for binary trees,
or 12 and 96 with the verifier's own calls folded into `t'`; form C (system B) `C1 = 24`,
`C2 = 6 (a + 3) x 8 = 240` (Lemma X: `t' = 2t`; 5.2 (d): 4 becomes 5). Tree of `N` proofs:

    kappa_IOP = (e - 1 - log2 C1 - log2 N) / 2,     kappa_hash = (lambda - 1 - log2 C2 - log2 N) / 3,

and condition Q is `min(kappa_IOP, kappa_hash) >= 64` (category 1). A failure raises
`qrom.ConditionQFailure`; no row is printed that fails it. **Assumption (stated with every figure):
the transcripts are in the CMS form** (`qrom-compilation.md` 4); neither system's transcript as
built is covered (C-7). At `N = 20,000`, `lambda = 256`: A 67.24 / 78.71 at `e = 152.343`, 67.54 at
its weakest corrected round; B 66.24 at `e = 152.343`, 66.43 at its weakest round (184 queries,
152.73). The per-round need of system B with `C1 = 24` is unchanged (152.52; the QROM part is
147.87, condition C binds).

**Salt length.** `salts.py`, an input (256, 384, 512, 576 bits; 512 is the lead architect's
choice). Error per proof: Theorem ZQ with Lemma H of `zk-quantum.md` 3 (Adapted from Chiesa, Yogev,
"Building Cryptographic Proofs from Hash Functions", Lemma 17.3.1, Claim 3.4.2, Remark 18.6.2, and
CMS19 Lemma 7.3's argument): `zeta_IOP + N_u (2^(-(s - 256)/2) + sqrt(n_b) 2^(-s/2))` (+ `k^2 /
2^257` in form C), `N_u = 2^24`, `n_b <= 2^12`; per tree, a union over the `2^14` leaf proofs (node
proofs do not hide). 512 bits: `2^-104` a proof, `2^-90` a tree; 256 bits: no statistical
statement. Bytes: `s / 8` an opened leaf, +32 at 512 against the built 32. Provenance of the tree
and byte accounting: Original (the Ycash developers, 2026).

**System B's rows.** `johnson.py` follows `binius-johnson-row.md` 7.2 and `johnson-row/rowcalc.py`
term for term (list size `(m + 1/2)/sqrt(rho)`; DKT26 ePrint 2026/2056 Theorem 4.4 bound (39) and
Corollary 6.6; Haböck ePrint 2024/1571 Theorems 3, 4; query terms DP24 Proposition 4.24 and Haböck
Lemma 3; all Published; the lemmas L-J1 to L-J3 that apply them to Binius64 are Original, the Ycash
developers, 2026, unreviewed). The certified row stays unique decoding, 184 queries at rate 1/8;
the Johnson rows (107 on the Haböck route and on the DKT26 route at `m = 10`, 102 at `m = 153`)
are printed as **candidate, under referee review** and never as certified (tested).
`binius64.johnson_bciks` is kept as the revision-4 record.

### 8.5f Revision 6: spBCS and Sharp–Grubbs Theorem 6.6 (2026-11-19)

`revision6.py`, `spbcs.py`, `affine.py`; `uv run yugen-soundness --rev6`; tests
`tests/test_revision6.py`; changes in `soundness/CHANGELOG.md` (revision 6); documents
`qrom-compilation.md` revision 2, `zk-quantum.md` revision 2.

**Transcript form as an input.** `spbcs.FORMS`: spBCS with a SHAKE256 stream (default, both systems)
or with a counter-mode SHA-256 stream (system B's alternative). The QROM statement is Sharp, Grubbs,
ePrint 2026/2615, Theorem 6.6 (2) (Published):

    eps_ex(t) = 2 sqrt(k_q / 2^(8(b+e))) + 6 (t + k_q)^2 (eps_k + c' (t + k_q) / 2^(8b)),

with `c' = max(2, c) + n_J + 1`, `c = N_msg max(1, m)`, `k_q = 2 N_msg + n_B + q_IOP (1 + floor(log2(2
l_max)))` (their Definition I.1) computed from each system's message counts (`revision6.a_counts`,
`b_counts`: verifier messages = the listed rounds plus `OTHER_ROUNDS`, one prover message before
each, `m = 2`; estimates until the transcript modules report them). Tree of `N` proofs (8.5b): the
QROM bits are the largest `kappa` at which `N` times the IOP term (resp. the hash term) at `t =
2^kappa` is `1/2`, with `k_q` added to `t` exactly; Lemma X doubles `t` for the counter mode. Condition
Q: at least 64, a hard failure (`spbcs.require`). A 67.54, B 67.43 (counter mode 66.43); the IOP term
binds; the hash term (`6 c'` about `2^13.8`) gives 75.6.

**Condition C (finding Q-5).** The certified need keeps the book's Theorems 25.2.1 and 31.2.1, whose
construction is the hash chain; spBCS's own classical bound is the ROM part of Theorem 6.6 (2), `(t +
k_q)(eps_k + ...)`, which at `t = 1` charges `k_q` (`2^15.5`) instead of `1 + k` (`2^9.2`): 158.8 bits a
round in the "every `t`" convention, 144.3 for `t >= k_q` (`spbcs.classical_need`). Decision T-6 of
`qrom-compilation.md`. **Decided 2026-11-19 (revision 9, section 8.9): every `t`.**

**Zero knowledge.** `spbcs.eps_zk` (Theorem 6.6 (3)) and `spbcs.eps_wi_log2` (Theorem 6.6 (4)) with
leaf salts `b_l` and proof salt `b_s` (64 bytes each by default), `n_pos` per system, `eps_ov = 0`,
`eps_hvzk` never filled in (open). Leaf proofs only (D-c).

**leanVM's `eps_aff`.** `affine.eps_aff`: CWYZ26 Theorem 4.10, (4.13), hypotheses (4.1), (4.5) and
`B^2 > n (d + 1)` checked in integers; `affine.best` is leanVM's witness search. A cross-check column
of the leanVM-as-shipped configuration; no certified row is in the Johnson regime.

### 8.6 What is a theorem and what is an estimate

| Statement | Status |
|---|---|
| Per-layer proven classical bits (C), given F4 | theorem in the ROM; F4 is ethSTARK Theorems 6, 8 (read, C-17); the shipping rows use no grinding |
| Per-layer proven QROM bits (Q), given F5 | theorem in the QROM (CMS19 Theorem 8.6, constants of Section 8.5.1, read) for CMS19's BCS construction (C-7); F5 is our argument |
| QROM bits of the tree, revision 6 (8.5f) | Sharp–Grubbs Theorem 6.6 (2) (Published, read with its proof's statement chain) for the spBCS transcript (specified, not built: tasks T-1, T-2); conditional on the knowledge form of the rounds outside the openings (K-A, K-B) and on modelling assumptions MA-1, MA-2; message counts estimated; condition Q is a hard failure. Revision 5's Theorem Q is a record (form X a sketch, form C unproved) |
| Zero knowledge of leaf proofs, revision 6 (8.5f) | Sharp–Grubbs Theorem 6.6 (3), (4) (Published) with Theorem ZP (composition, ours); conditional on the IOP-level HVZK of both leaves (open) and on B's fold trees being salted |
| W-1 true rates of system A's plain levels (8.5e) | Theorem S0 (`whir-additive-soundness.md`, proven there, reviewed: holds) on BCIKS20; the degree growth from the pinned verifier's code (CWYZ26 Theorem 5.2 consistent only) |
| Chain = layers minus 2 bits | union bound; conditional on the recursion heuristic C2 (section 2.4) |
| Tree = proofs: `log2 N + log2(1 + k)` per round, `k` counting every round (8.5b) | union bound over the tree's proofs; conditional on C2; the collision term once for the tree and the multi-block step are our reading (8.5b) |
| G: per-round 128 bits is AES-128-equivalent for every MAXDEPTH | attack-cost estimate (Zalka's optimality is a theorem; the Keccak/AES gate comparison is from memory) |
| H attack rule: 256-bit digests meet category 1 | NIST's own ordering of its benchmarks (category 2 above 1) |
| Johnson-regime (DKT26) sizes | P4/P5 proved (DKT26 Theorem 4.4, read, C-14, C-15); the protocol theorems for binary additive WHIR, power batching and Binius64's ring switch, mask round and lifted oracles are not written (C-10, C-11, C-15); shown separately everywhere |
| Proof sizes, verify times, prover factors | model estimates calibrated against `bench/results/` |

### 8.7 Revision 7: the security category as an input (2026-11-19)

`soundness/src/yugen_soundness/category.py`; `uv run yugen-soundness --rev7` (categories 1, 3, 5)
or `--category N` with `--digest-bits`, `--proof-salt`, `--leaf-salt`, `--field-bits`,
`--tree-hash-a`, `--tree-hash-b`, `--privacy-category`; tests `tests/test_revision7.py`; every number
in `soundness/CHANGELOG.md` revision 7; output `soundness/output/revision7-tables.txt`.

#### 8.7.1 What the NIST text says (Published, [CFP] 4.A.5)

Each category is a requirement on every attack against "the relevant security definition": its
computational resources must be "comparable to or greater than" those of a reference attack, "with
respect to all metrics that NIST deems to be potentially relevant" (page 17):

| Category | Reference attack ([CFP] pages 16, 17) | Classical gates (page 18) | Quantum gates (page 18) |
|---|---|---|---|
| 1 | key search on a block cipher with a 128-bit key (AES128) | 2^143 | 2^170 / MAXDEPTH |
| 2 | collision search on a 256-bit hash function (SHA256/ SHA3-256) | 2^146 | not given |
| 3 | key search, 192-bit key (AES192) | 2^207 | 2^233 / MAXDEPTH |
| 4 | collision search, 384-bit hash (SHA384/ SHA3-384) | 2^210 | not given |
| 5 | key search, 256-bit key (AES 256) | 2^272 | 2^298 / MAXDEPTH |

MAXDEPTH is "2^40 ... through 2^64 ... to no more than 2^96" logical gates (page 17). Footnote 2
orders the five categories; footnote 6 cites Zalka for the cost of parallel Grover; the table also
lists SHA3-512 collisions at 2^274 classical gates. Section 4.A.6 lists resistance to multi-key
attacks as "desirable", not as part of the definition. Nothing in the text is a proven-security
definition: the categories are attack costs.

#### 8.7.2 From each figure to a calculator condition (Original, the Ycash developers, 2026; O-38)

The calculator counts hash-oracle calls and success probabilities; NIST counts gates. The
conversions are this project's conventions, stated here:

| Condition | Derivation | Where a choice is ours |
|---|---|---|
| C: `kappa_C` proven classical bits | the reference attack's evaluations: `2^k` keys for key search on a `k`-bit key, `2^(n/2)` evaluations for collision search on an `n`-bit hash: 128, 128, 192, 192, 256 for categories 1 to 5. NIST's gate figures divided by these give the gates of one reference evaluation: `2^15, 2^18, 2^15, 2^18, 2^16` | counting oracle calls equals NIST's gate figure when one oracle call costs at least one reference evaluation in gates. For a Keccak-f oracle NIST's own numbers (`2^18` for a SHA3 evaluation) make the convention conservative by 2 to 3 bits; for SHA-2 and BLAKE3 compressions the gate counts are not in the folder (assumption) |
| Q: `kappa_Q = kappa_C / 2` proven QROM bits | unlimited-depth Grover recovers a `k`-bit key in about `2^(k/2)` sequential evaluations, so a QROM bound of `k/2` bits is AES-`k` equivalent at any depth | the halving (ours, as in 8.2). **What it proves**: the tree's QROM bound reaches 1/2 at `2^kappa_Q` quantum queries. At categories 3 and 5 NIST's quantum budget (at least `2^137` and `2^202` gates at MAXDEPTH = `2^96`) allows more parallel queries than that, where the bound is vacuous; there the quantum half of the category rests on G, an attack estimate (referee report 3.3, F-3). At category 1 the bound covers the budget at large MAXDEPTH |
| G: every round `e >= kappa_C` | parallel Grover under a depth limit over a bad set of density `2^-e` costs about `2^e x (D x S) / MAXDEPTH` gates for an oracle of depth `D` and size `S`; NIST's quantum figures are `2^k x 2^42, 2^41, 2^42 / MAXDEPTH` for categories 1, 3, 5 | the premise "one oracle call's quantum circuit has depth x size at least AES's" (`2^41` to `2^42`) is an **assumption, unverified** (referee 1, correction 5); it replaces 8.2's AND-gate comparison, which compared size only |
| H: digests of `2 kappa_C` bits (256, 384, 512) | generic collision search on the digest costs `2^kappa_C` evaluations; NIST lists SHA3-384 / SHA3-512 collisions at `2^210` / `2^274` classical gates, above AES192's `2^207` / AES 256's `2^272`; [FIPS204] Table 1 sets the "collision strength of c~" to 128 / 192 / 256 at categories 2 / 3 / 5, and its Appendix D.1 records that a 384-bit SHAKE256 output left category-5 parameters at category 4 | NIST prices collisions classically only; the BHT model (`2^(n/3)` queries with free quantum memory) would need 576 bits at category 3 and is not used. The proven rule (`3.5 t^2 / 2^lambda`) is reported beside it: 264 / 392 / 520 bits |
| Tree union | `e >= kappa_C + 1 + log2 N + log2(1 + k)`, `N = 20,000` proofs, `k` = listed rounds + 512: 152.52 / 216.52 / 280.52 bits a round (A, `k = 599`; B, `k = 600`) | the union over a tree goes beyond [CFP]'s per-instance definition (multi-key is "desirable"); the per-instance reading needs 14.3 bits less a round. Kept (8.5b) |

Categories 2 and 4 give the same `kappa_C` in oracle calls as 1 and 3, so the same rows; a
collision-search category is distinct from its neighbour only in gate counts (3 bits), which the
oracle-call convention does not see. Condition Q's need (`2 kappa_Q + 1 + log2 6 + log2 N` =
145.87 / 209.87 / 273.87) is below condition C's at every category.

#### 8.7.3 Inputs, rows and refusals

Inputs (`category.Profile`): category, digest bits, proof and leaf salt bytes, challenge field bits,
each system's tree hash, and the privacy category whose `kappa_Q` is the hash-query budget `t` of the
zero-knowledge figure. Default profiles: category 1 as built (32-byte digests, 64 / 64-byte salts,
`GF(2^256)`, Keccak-256 / BLAKE3); category 3 (48, 64 / 96, `GF(2^256)`, SHAKE256-384 / SHA-384);
category 5 (64, 80 / 112, `GF(2^384)`, SHAKE256-512 / SHA-512); M-1 (category 3 with category 5
privacy: 48-byte digests, 80 / 112-byte salts, `t = 2^128`).

Rows (unique decoding, no grinding, true rates, spBCS with `C1 = 6`): system A's masked leaves
(row 6, the standalone masked row; row 8, the masked row of a tree; mode 0 at `2^22`, mode 1 from
`2^20` by the admission rule of yugen-proof-a `parameters.md` 2.4) at their minimal counts
(`wi.solve`), and node row 9 at every stack `2^24` to `2^30`, rates 1/2 and 1/4, at minimal counts
(the rule counts at the need, raised and trimmed); system B's zero-knowledge leaf (form T, route S)
and node (`2^27` words) at rates 1/8 and 1/16, `ceil(need / -log2((1 + rho)/2))`. Each count less by
one fails (tests). System B's list-decoding rows are printed as **candidate, conditional on DKT26**,
never certified.

Refusals, all hard failures: field below the algebraic rounds (`FieldTooSmall`); digest below the
attack rule (`DigestTooShort`) or below the QROM hash term of Theorem 6.6 (2)
(`ConditionQFailure`); a tree hash whose collision claim is below `kappa_C` or whose output is below
the digest (`HashNotAdmissible`: BLAKE3 and SHA-256 at categories 3 and 5, as NIST itself moves
SLH-DSA's tree functions `H` and `T_l` to SHA-512 at categories 3 and 5, [FIPS205] 11.2.2); leaf
salts not longer than the digest (`SaltNotCovered`, Theorem 6.6 (3)).

#### 8.7.4 Results (E unless marked; `output/revision7-tables.txt`)

| | Category 1 | Category 3 | Category 5 |
|---|---|---|---|
| A leaf, standalone masked, mode 0 | 226, 157, 154, 154 | 321, 222, 219, 218 | 415, 288, 283, 282 |
| A node `2^27`, 1/2 | 368, 167 x3, 168 x2, 173 | 522, 238 x4, 239, 246 | 676, 308 x4, 309, 319 |
| B, rate 1/8 / 1/16 | 184 / 168 | 261 / 238 | 338 / 308 |
| Minimum field (A and B, worst shape) | 185 | 249 | 313 (312 at rates 1/2 and 1/8) |
| QROM bits A / B | 67.25 / 67.43 | 99.29 / 99.39 (48 B) | 131.28 / 131.35 (64 B) |
| Smallest digest for the QROM hash term | 224 | 320 | 416 |
| Largest certified proof | 1,047,063 B | 1,793,209 B | 3,003,138 B (over 1,835,008) |

**Zero-knowledge target.** None was defined before (referee 3.4). The calculator now prints the salt
floors for a pool target of `2^-64`, `2^-96`, `2^-128` (`2^20` leaf proofs, excluding `Q eps_hvzk`):
leaf salts 75 / 83 / 91 B at 48-byte digests and 91 / 99 / 107 B at 64-byte digests (the leaf term
alone, independent of `t`); proof salts 54 / 62 / 70 B at `t = 2^128`. Which target is adopted is the
lead architect's decision; the profiles above keep the study's 96 B (category 3: `2^-138.0`, the
proof-salt term binds) and 112 B (category 5: `2^-151.8` / `2^-149.7`). Theorem 6.6 (3) bounds `t`
hash queries **before the last proof**; the figures use `t = 2^kappa_Q` of the privacy category. Read
with `t = 2^kappa_C` (the classical budget) the salt term gives `2^-42` at every profile: the QROM
bound's `4 Q t / 2^(4 b_s)` is quadratically loose for classical queries, so this reading is not
an attack, but no published classical bound for spBCS's zero knowledge is used here. Theorem
6.6 (4) (witness indistinguishability) has no query bound and is unaffected: `2^-150.8` (A) at
categories 3 and 5, `2^-214.8` under M-1.

**What is a theorem and what is an estimate** (adds to 8.6): the category derivation's figures are
NIST's (Published); conditions C and H as theorems under the stated conversion; Q a theorem to
`2^kappa_Q` queries; G and the quantum half of categories 3 and 5 attack estimates under the depth x
size assumption; every size an estimate.

### 8.8 Revision 8: system B's Johnson-regime terms in the calculator (2026-11-19)

`soundness/src/yugen_soundness/dkt26.py`; `uv run yugen-soundness --rev8` (with `--category N`); tests
`tests/test_revision8.py`; numbers in `soundness/CHANGELOG.md` revision 8; output
`soundness/output/revision8-tables.txt`. Condition C-3 of `johnson-row-referee-2.md`: every per-round term of
`binius-johnson-row.md` revision 2 (Lemmas U, J1, J2, F, UD), with DKT26 Theorem 4.4's exact exceptional count
(33)-(34) and its closed form (39), the parameters (36)-(37) and the list bound (38) printed per line, and Lemma 3.3 at
message dimension 1 only on request. Rows outside the theorems' hypotheses are refused (`OutsideRegime`), not
warned about. **Every Johnson-regime row is printed as resting on DKT26 (ePrint 2026/2056), a preprint**; the
unique-decoding rows (184 at 1/8; system B's node at 1/4, 225, built at 226) are certified and use no Johnson-regime
statement. The row "Johnson-regime (DKT26) sizes" of 8.6 predates `binius-johnson-row.md`: system B's protocol
lemmas are now written there (revision 2, refereed twice: pass with conditions C-1 to C-7); system A's (binary
additive WHIR, power batching) are not.

### 8.9 Revision 9: the counting convention is every `t` (2026-11-19)

Decision record: `docs/decision-qrom-counting.md` (the lead architect's ruling on condition C-2 / T-6). The
tree model of 8.5b is unchanged except its classical target's per-proof term: [SG26] (Sharp, Grubbs, ePrint
2026/2615) Theorem 6.6 (2) bounds `eps^C_ex(t) = (t + k_q)(eps_k + c' (t + k_q)/2^(8b))` for every `t` and every
`(t, 0)`-adversary (Definitions H.3, H.4, pages 128, 129, read from the rendered pages), so the target
`eps_tree(t) <= t / 2^(kappa_C + 1)` for every `1 <= t <= 2^kappa_C` binds at `t = 1` with the proof's own `k_q`:

    e_v >= kappa_C + 1 + log2 N + log2(1 + k_q,v)          (default; "every t")

in place of 8.5b's `1 + k` (the book's hash-chain theorem, which spBCS does not instantiate). `k_q,v` grows with the
proof's query count, so every row is solved to its least fixed point. At category 1 the need is 157.0 to 158.8 bits
a round (152.52 before). The book need is kept only behind `--convention t-ge-kq`, labelled "non-default convention
(t >= k_q), not certified". Rows: `soundness/CHANGELOG.md` revision 9 (system B 184 -> 192, 107 -> 111, 80 -> 82,
168 -> 174, node 1/4 225 -> 235 and 165 -> 171; system A +4 to +15 queries a level); condition Q (QROM) A 69.58,
B 70.45 against 64. Provenance: the bound and its quantifier Published [SG26]; the fixed point and the tree accounting
Original (the Ycash developers, 2026), O-13, O-68, unreviewed; Lemma M (which would restore the book counts) is a
proposal, unproved, not adopted (O-69).

### 8.10 Revision 10: the hash term of [SG26] Theorem 6.6 (2), `k_q` as an input (2026-11-19)

Amendment 1 of `docs/decision-qrom-counting.md` (section 7), after `docs/rev9-and-lean-referee.md` R9-1 to R9-5 and
`docs/lemma-d-referee.md` m-1. **A draft until refereed.** The theorem's hash term `c' (t + k_q)^2 / 2^(8b)` (ROM) and
`6 c' (t + k_q)^3 / 2^(8b)` (QROM), with `c' = max(2, c) + n_J + 1` and `b` the length of every digest the transcript
writes (32 bytes in both systems), is evaluated per row, per proof and summed over the tree, and printed on every row
(`soundness/src/yugen_soundness/hashterm.py`). Category 1: classical 121.89 (proof) / **114.74** (tree), QROM 80.40 /
75.63, for A's leaves and every B row (A's nodes 114.81). The classical claim of 8.5b therefore holds as a proven bound
for the IOP term only; the hash part rests on condition H's attack rule (the recorded basis, now printed on every
certified row; `--hash-basis proven` certifies no 256-bit row). "Certified" is computed from the row's checks, never
passed in (R9-2). `k_q` is an input with provenance; an estimated `k_q` needs a margin of 0.1375 bits (the cost of a
10 % error) for the label (R9-4), which 14 of A's 20 category-1 rows and A row 7 at 1/2 lack until task T-1 (decision
record 7.6). System B's `k_q` counts padded group slots (m-1); no count moves. Changes and figures:
`soundness/CHANGELOG.md` revision 10. Provenance: the bound Published [SG26] (pages 58, 130, 131, rendered); the
evaluation, the guard and T-1 Original (the Ycash developers, 2026), O-75 to O-77, unreviewed.

*Revision 10.1 (2026-11-19, after `docs/rev10-referee.md`): every row type is judged by one certification function on
the profile's hash basis (the Johnson-terms table included, R10-1); the tables end with what "proven" rests on (R10-2);
the tree reduction is `docs/lemma-tree-extraction.md` (Theorem TE, a draft; under it the hash part of the tree would be
taken once, 121.89 bits, while the calculator keeps 114.74 until it is refereed); the `k_q` guard is the larger of the
10 % allowance and both named errors together (A row 7 at 1/4 loses "certified", R10-7); `c'` is printed as an
estimate with a reported path (R10-6); task T-1 reports are keyed by shape, refused below the shape's floor and re-solve
the row above the estimate (R10-8); the stream term is evaluated at the shortest stream (R10-9). No query count moves.
Decision record 7.10; O-78, O-79.*


### 8.11 Revision 10.2: the tree figures after the referee's report on Lemma TE (2026-11-19)

After `docs/tree-extraction-referee.md` (F-1 to F-7). `docs/lemma-tree-extraction.md` revision 2 restates Theorem TE as
**Theorem TE'**, a theorem of the ROM in which the recursion heuristic C2 is the named event C2-VIOLATION; the bound is
unchanged (`t eps_max + sum_v |J_V,v| eps_v + c'_max (t + K)^2 / 2^(8b)`). The calculator (revision 10.2,
`soundness/CHANGELOG.md`) prints the tree's classical hash level as **121.89 bits "under C2, K-A, K-B, T-1"** with the
per-proof union 114.74 beside it (the proven-basis check keeps 114.74; no status changes), and the tree's QROM figures
as the per-proof union **69.58 / 70.45 (claimed)** beside the one-table form of Proposition TE-Q' (76.72 / 77.60, hash
part 80.40), with the term of Lemma QC, `log2` -222.91 (A) / -223.09 (B). **No query count moves** (a test pins every
row against revision 10.1). The tree figures are derived under C2, conditional on K-A, K-B (owed) and T-1 (owed); none
is an unconditional theorem. The page that lists every claim with its status is `docs/what-is-proven.md`.