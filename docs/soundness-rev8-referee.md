# Referee report on soundness calculator revision 8 (`dkt26.py`, `--rev8`)

Part of Yugen. Subject: `soundness/src/yugen_soundness/dkt26.py` at `b6d9fb4`, its
output `--rev8`, its 292 tests, and the rows it prints: 107 queries at rate 1/8 (list 19), 80 at
rate 1/16 (list 31), the new Johnson count 165 for node proofs at rate 1/4 (list 10), beside the
unique-decoding rows 184 and 225 / 226. Referee: independent of the author; the work under review
is the Ycash developers' (2026).

Sources read for this report, with what was used:

- **[DKT26]** Q. Dao, S. D. Kominers, J. Thaler, "Reed-Solomon Codes Beyond Johnson: Efficient
  Decoding and Smaller Cryptographic Proofs", Cryptology ePrint Archive, Paper 2026/2056, copy
  dated November 2, 2026, a preprint. Read from rendered page images (pages 16, 17, 28, 29, 30):
  Section 3.1, Definitions 3.1 and 3.2, Lemma 3.3 with its proof, Section 4.2 equations (33), (34),
  Lemma 4.3 (statement), Theorem 4.4 with equations (36) to (39) and the paragraph after its proof;
  from the text layer: Lemma 6.5 with its proof, Corollary 6.6, Section 6.3 to Corollary 6.7
  (statement).
- **[SG26]** C. Sharp, P. Grubbs, "Faster and Smaller Anonymous Credentials from Standardized
  Signatures", Cryptology ePrint Archive, Paper 2026/2615: Protocol 6.5, Section 6.3, Theorem 6.6
  (all five parts as stated), Definitions H.3, H.4, I.1, Theorem I.16 (statement and the first
  paragraph of its proof). Text layer only.
- This repository: `docs/binius-johnson-row.md` (sections 0, 2.1, 2.2, 5.3, 5.4, 8),
  `docs/johnson-row-referee-2.md` (headings, 5.1, 6.3 by search), `docs/qrom-compilation.md` 6.2,
  `soundness/CHANGELOG.md` (revision 8), `dkt26.py` in full, `spbcs.classical_need`,
  `category.b_counts`.
- `yugen-proof-b2` (read-only): `docs/parameters.md` 2a.2, 2a.4, 11.3, 13.9, 14.4, 14.7;
  `tests/opening_once.rs` (BR-4 test); `bench/results/johnson-20261119-m.txt` (BR-4 lines);
  `src/params.rs` lines 110, 250, 493.

Marks: **V** verified by this referee by a run or a derivation recorded here; **R** read; **E**
this referee's estimate from figures in the documents, not measured.

## 0. Verdicts

| Subject | Verdict |
|---|---|
| (i) Rows 107 (rate 1/8) and 80 (rate 1/16) as computed by revision 8 | **PASS WITH CONDITIONS** (R8-1, R8-2, R8-6) |
| (ii) The 165-query Johnson node row at rate 1/4 | **PASS WITH CONDITIONS** as arithmetic (R8-3, R8-4); **not a refereed row**: no document proves or tests the lemma chain at rate 1/4 and the build has no such shape |
| (iii) Revision 8 as software | **PASS WITH CONDITIONS** (R8-5, R8-7 to R8-12) |

No BLOCKER. No number of the three Johnson rows or of the certified rows changed under
recomputation. Every Johnson row stays a candidate resting on a preprint; nothing here lifts that.

## 1. DKT26 equations (36), (37) and the choice of `eta_0` (author's weakest point 1)

Derived from the page image before the code was opened (V).

**What the paper prints** (Published, [DKT26] Theorem 4.4, page 29). Hypotheses: any field `F`;
distinct `alpha_1..alpha_n` in `F`; `1 <= D <= n - 2`; `rho_- = D/n`; a choice `eta_0 > 0` with
`a := sqrt(rho_-) + eta_0 <= 1`. Definitions, with the brackets as printed:

- (36) `A = ceil(a n)`; `m = max{ ceil( sqrt(rho_-) / (2 eta_0) ), 3 }`; `t = m + 1/2`. The ceiling
  encloses the quotient only; the maximum with 3 is outside it.
- (37) `B_jet = ceil(t / sqrt(rho_-)) - 1`; `B_Z = ceil(t^2 / (3 rho_-)) - 1`;
  `lambda_agr = (n - D)/(A - D)`, no rounding.
- (38) list bound `min{ B_jet, floor( n (A - D) / (A^2 - n D) ) }`, a floor on the second term.
- (39) `|E| <= B_cf := E^(1)_ord(D, A, n; B_jet, B_Z) < (8/3) n t^3 / rho_-`, strict.
- (33), page 28: `E^(l)_ord(D, A, n; B, H; L) = (2B - 1) H + ((n - L + 1)/(A - L + 1)) (l B + H Psi_D(B))
  + l (n - L) B`, `Psi_D(B) = 1 + (2D - 1)(2B - 1) + 2 (B - 2D - 1)_+`; the fraction is not rounded;
  (34): `L = D + 1`. Lemma 4.3 asks `D + 1 <= L <= A <= n`, `B_jet >= 1`, `l >= 1`.

**The text layer loses every bracket** (the extracted line reads `𝐵jet = 𝑡√𝜌− − 1`). The changelog
says the formulas were "re-read from the PDF's text layer"; that layer cannot settle the question
the author raised. The page image does, and the author's reading is the printed one. Finding R8-9.

**The choice `eta_0 = A/n - sqrt(rho_-)`.** Sound (V). The theorem lets `eta_0` be chosen; with
this choice `a = A/n` is rational, `ceil(a n) = A` exactly, `a <= 1` iff `A <= n`, and `eta_0 > 0`
iff `A^2 > n D`. It is the largest `eta_0` whose threshold is `A`, hence the smallest theorem `m`.
With our `A = ceil((1 + 1/(2m)) sqrt(k/n) n)`: `eta_0 >= sqrt(rho_-)/(2m)`, so the theorem's `m` is
at most ours (V: no counterexample in 37,698 lines, section 4).

**Hypotheses, row by row** (V, every line of every row: mask, index, each `X` fold down to the
terminal dimension):

| Hypothesis | Where it is used | Holds for the rows |
|---|---|---|
| any field, challenge uniform in the code's field | Theorem 4.4; Lemma 6.5 (`C` over `F_q`, projections in `F_q^s`) | `K = GF(2^256)` for every challenge (johnson doc 2.1, R); the code is taken over `K` |
| distinct evaluation points, no structure asked | Theorem 4.4 ("uniform over the prescribed evaluation set") | a `GF(2)`-subspace (R) |
| `1 <= D <= n - 2` | Theorem 4.4 | smallest line of any row: `n = 8, k = 2` (node 1/4 at the assumed terminal 1); built shapes stop at `k = 2^4 .. 2^6` |
| `a <= 1`, `eta_0 > 0` | Theorem 4.4 | `A/n` is 0.371 / 0.2625 / 0.525 at rates 1/8, 1/16, 1/4 |
| `A >= D + 1` (`L <= A`), `B_jet >= 1` | Lemma 4.3 | yes |
| threshold `A >= k`; scalar bound for every received line | Corollary 6.6 (width) | yes |
| message dimension 1 excluded | Theorem 4.4 ("excludes the degree-zero code") | no built shape reaches it (C-4, R); Lemma 3.3 (6) is `floor(l C(n,2)/(A-1))` for `A >= 2`, list `floor(n/A)`, as coded (V against page 16) |

Not a hypothesis of the theorem but of its use: the count is for one line `f + z g`; the fold
`(1 - z) f_0 + z f_1` is that line with `g = f_0 + f_1` (johnson doc 5.4, R; [DKT26] Section 6.3
makes the same remark for the generator `(1 - r, r)`).

## 2. The fold-line pairing and the `2^22` / `2^31` inputs (point 2)

**Pairing** (V by derivation, agrees with Lemma F of the johnson doc). The `i`-th `X` fold writes
the level-`(i-1)` word as an even and an odd part on the half domain; the word is in
`RS[n/2^(i-1), k/2^(i-1)]` iff both parts are in `RS[n/2^i, k/2^i]`, and the fold is a line in the
two parts. So the line of fold `i` lives at `(n/2^i, k/2^i)`, `D = k/2^i - 1`: what
`lines_of` computes. Mask and index rounds combine whole rows at `(n, k)`. Rate, hence `a`, is the
same at every level. Folds of arity above 1 are one line per variable ([DKT26] Corollary 6.7 is
that composition).

**The inputs are caps, not the shapes the build runs** (R, MINOR R8-6). The `johnson` build's BR-4
lines print index bits 21 at rate 1/8 for the leaf and for the level-0 node, 21 or 22 at rate 1/16
(`johnson-20261119-m.txt`), fold arities `[3,3,3,3]` with terminal 6 (18 variables). The calculator
takes the leaf at `2^22` (rate 1/8), `2^23` (1/16) and the node at `2^31`, `2^32`, `2^30`. The
caps are on the safe side: `B_cf` grows linearly in `n` at fixed rate and the list bound is
uniform in `n` (V: 10 / 19 / 31 at every `n = 2^j / rho`, `j = 1..39`). With 57.7 to 61.5 bits of
slack the rows hold for any opening up to about `2^88` points. But the docstring and the table
headings present the lengths as the rows' lines; they are bounds, and nothing in the build refuses
a node above the cap.

**The terminal dimension is a property of a shape, not of (kind, rate)** (R, MINOR R8-7). The same
log prints `log_terminal_dim` 4 for a rate-1/16 node with index bits 22 and 5 for one with index
bits 21. `TERMINAL_AS_BUILT` is keyed by (kind, rate) and is then paired with a `2^28`-element
node no build has. Effect: the number of fold rows printed and the D-term only; neither binds.

## 3. The 165-query Johnson node row at rate 1/4 (point 3; not reviewed before)

Re-derived (V): per query `-log2(1.05 x 1/2) = 0.929611` bits; need `129 + log2(20,000 x 601) =
152.518934`; `ceil(152.518934 / 0.929611) = 165`, reaching 153.3858 (164: 152.4562, fails). List:
`floor((a - rho)/(a^2 - rho)) = floor(0.275/0.025625) = 10`, and `min(B_jet = 21, 10) = 10` at
every length. First `X` fold at `(2^29, 2^27)`: `A = 281,857,229`, theorem `m = 10`, `B_jet = 21`,
`B_Z = 147`, `lambda_agr = 2.7273`, `log2 B_cf = 42.0074`; with `2 x 10` roots, 213.9926 bits.
Condition Q with the calculator's own functions at 165 queries: 67.76 QROM bits against 64 (V).
The count is right.

What the row does not have:

- **R8-3 (MAJOR for this row).** No document states Lemmas U, J1, J3, F, K at rate 1/4 and no test
  in `johnson-row/` runs there; `binius-johnson-row.md` is written at `rho = 1/8` with `B_list = 19`
  in its statements, and the second referee certified the rate-1/4 node in unique decoding only
  (225). The lemmas read as rate-generic (F1' is stated for general `a`), which is why the
  arithmetic passes, but "reads as generic" is this referee's impression of sections 2.2 and 5.4,
  not a check of every lemma. *Fix*: a revision of the johnson doc that states each lemma for
  `rho` in {1/4, 1/8, 1/16} with `B_list(rho, m)`, the list-size test extended to rate 1/4, and
  the row added to the review sheet (section 12 there). Until then the row's label should read
  "arithmetic only; lemma chain not stated at this rate" in addition to the preprint label.
- **R8-4 (MINOR).** The terminal dimension is assumed 1, "the smallest value Theorem 4.4 covers
  without Lemma 3.3". That choice sidesteps the calculator's own dimension-1 refusal for the one
  shape whose terminal is unknown. Numerically nothing depends on it (V: terminal 0 with Lemma
  3.3, and 1, 2, 5, 6, 7, 10 all give 165, weakest 213.99). *Fix*: for an unrecorded shape default
  to terminal 0 with `dimension_one="lemma33"` (the case with the most fold lines, covering both
  theorems) and print that; make the build's BR-4 test print the rate-1/4 node shape (C-4 extended).
- The `2^28`-element node "at every rate" is an assumption: a node's size depends on the count
  and rate of the proofs it verifies. Covered by the slack (section 2).
- No build exists at this row: the rate-1/4 node is built at 226 queries in unique decoding
  (`parameters.md` 14.7).

## 4. Independent recomputation (point 4)

Written from the paper, without reading `rowcalc.py` and before comparing with `dkt26.py`
(scratch, not committed). Two implementations: one in 80-digit reals, one exact (rationals and
integer square roots, own code).

| Check | Result |
|---|---|
| Need | 152.518933560260..., difference from `dkt26.need()` 1.4e-14 |
| Query bits, six rows | 152.733800 (184), 152.968342 (107), 154.368854 (80), 152.566179 (225), 153.243... (226), 153.385761 (165); each differs from the calculator by under 2e-14; each count less by one fails |
| Line parameters `A, m, B_jet, B_Z`, list, and `log2 B_cf`, all lines `n = 2^2..2^33`, every `k = 2^j < n`, `m` in {3, 4, 7, 10, 38, 153} | 3,168 lines: integers identical, `log2 B_cf` within 1e-9; exact count never above the closed form; theorem `m` never above ours |
| The same on 40,000 random `(n, k, m)`, `n <= 4000`, any `k` | 34,530 computed: `A, m, B_jet, B_Z`, list and the count as a rational **equal exactly**; 5,470 refused by both; no case computed outside the hypotheses, none refused inside them |
| Term bits of the rows | leaf index 220.13571532536, leaf fold 221.13572003417, node fold 212.13571052600 (1/8); 218.19448923023, 219.19449371646, 210.19448441938 (1/16); 213.99255459485 (1/4): equal to the calculator's to 1e-13 |

The 1e-9 claims hold against a third program. Two disagreements appeared and both were this
referee's: the real-arithmetic version rounded `ceil` wrongly where the argument is an exact
integer (`n = 49, k = 36, m = 3`: `a n = 49` exactly; `n = 1652, k = 344, m = 10`:
`t^2/(3 rho_-) = 177` exactly). The calculator's exact arithmetic is right in both. That is a
point in the module's favour and the reason the changelog's phrase "exact square-root ceilings"
matters.

## 5. The refusals and the labels (point 5)

Refused correctly (V): `k = 1` without Lemma 3.3; `k <= 0`; `m < 3` (also negative, `True`);
`D = n - 1`; `A > n` (`n = 16, k = 15`); rate 1 (`D > n - 2`); Haböck's route. Boundaries accepted
and equal to the exact recomputation: `m = 3`; `A = n` (`n = 49, k = 36`); `D = n - 2` where
`a <= 1` (`n = 3, k = 2`; `n = 16, k = 14`); `D = 1`.

No path through `dkt26` prints a Johnson row as "certified" without the label (V: `status` with
`DKT26_ACCEPTED` true still carries it; a `ud` route with an `m` passed is a true unique-decoding
row; a Johnson row below its need says so with the label).

Paths that do print Johnson rows **without the preprint label**, outside `dkt26` (V by running
every flag):

- **R8-8 (MINOR).** `--rev5` prints "Johnson, m = 10, Haboeck route | candidate, under referee
  review | 107 | ... | yes", the same for the DKT26 route and the `m = 153` row (102 queries):
  no mention of a preprint, and the Haböck route is one the johnson doc withdrew (0.1, 0.3). The
  default tables, `--design` and `--basis` print "johnson-dkt26 (UNCONFIRMED)" rows for systems A
  and B. None says "certified". The changelog calls revision 5 "a record", but the flag still
  prints it live. *Fix*: prefix those tables with one line (superseded; candidates rest on DKT26,
  a preprint; Haböck's route withdrawn) or route their status strings through `dkt26.dkt26_status`.

Defects found at the edges of the row API (V):

- **R8-10 (MINOR).** `row(.., "dkt", ..)` without `m` raises `TypeError` in `per_query_bits`; the
  intended `OutsideRegime("the Johnson regime needs m")` in `terms` is unreachable from `row`.
  A non-integer `m` raises `TypeError` in `Fraction`. *Fix*: validate `m` (an `int >= 3`) at the
  top of `row` and `line`.
- **R8-11 (MINOR).** `log_terminal_dim` is not validated. Above the message log, a unique-decoding
  node row loses every fold term and still prints "certified", weakest term the D-term; a Johnson
  node row raises `ValueError: max() iterable argument is empty` (also at the legitimate value
  equal to the message log); `-1` with Lemma 3.3 raises `ZeroDivisionError`. *Fix*: refuse
  outside `0 <= log_terminal_dim <= log_msg` with `OutsideRegime`; handle the no-fold shape.
- **R8-12 (NOTE).** `row(.., "dkt", 3, 153)` computes the withdrawn 102-query row and prints
  "meets" at +0.001 bits; `row(.., "dkt", 1, 3)` prints a "Johnson" row whose threshold (0.825) is
  above the unique-decoding threshold (0.75) at 550 queries. Both carry the candidate label.
  *Fix*: a margin floor for a printed Johnson row (the johnson doc dropped 102 and 77 for their
  margins) and a refusal when `a >= (1 + rho)/2`.

## 6. The author's listed findings (point 6)

1. **`--category` and the withdrawn rows: confirmed, MINOR R8-8b.** `--rev7` (and
   `category.b_candidates`) still searches over `m` with `johnson.best_m` and prints `m = 153`,
   102 queries, margin +0.00 and `m = 38`, 77 queries, +0.03 as "candidate ... yes", and at larger
   fields `m = 107`, 53, 92 at +0.00 / +0.01. They carry the preprint label. A search that
   minimises the count always lands on the thinnest margin, which is the reason the johnson doc
   withdrew those rows. *Fix*: replace the search by the refereed `m = 10` rows from `dkt26.rows`
   (or require a margin of at least 0.4 bits, the 107 row's), and print the list size 19 / 31, not
   revision 5's `(m + 1/2)/sqrt(rho)`.
2. **The D-term at rate 1/16: the author is right; at rate 1/8 both are, for different rows.**
   The builder's formula is `n_f (2^r - 1)` (`parameters.md` 11.3: 49 = 7 x 7 at rate 1/8 for the
   184-query build, whose terminal codeword has 1,024 symbols, `n_f = 7`). The second referee's
   5.1 carries 49 (250.39 bits) into the rate-1/16 column, where the formula gives 4 x 15 = 60
   (250.09) or 5 x 15 = 75 (249.77) at the recorded terminal dimensions: 250.39 contradicts the
   formula there. At rate 1/8 the 107-query build has `n_f = 6` (42, 250.61: the author), the
   184-query build `n_f = 7` (49, 250.39: the referee). **R8-7 (MINOR), a new defect in the same
   place**: the calculator prints 6 x 7 = 42 for the certified 184 row too, because its table is
   keyed by (kind, rate); the built 184 row has 49. *Fix*: key the terminal dimension by the row
   (kind, rate, query count) or charge the bound `log_msg x (2^r - 1)` (at worst 28 x 15 = 420,
   247.29 bits). Nothing binds: the smallest of these is 94 bits above the need.
3. **Terminal dimension 1 for the rate-1/4 node**: R8-4 above. Harmless in bits; the default
   should not be the value that avoids the refusal.
4. **The builder's list size 29.70 / 42** (`yugen-proof-b2/src/params.rs:110, 250, 493`): NOTE.
   `(m + 1/2)/sqrt(rho)` is a valid bound: it is at least `B_jet` (29 and 42; first term of (38)),
   which is at least the Johnson value 19 / 31. It is the looser of the two and unlabelled. *Fix*
   (in that repository, by its maintainers): a comment at `Row::list_size` saying "conservative: the
   Johnson bound (DKT26 (38), second term) gives 19 at rate 1/8 and 31 at 1/16", and the same
   word in `parameters.md` 8.4.

## 7. The QROM counting convention, condition C-2 (point 7)

**What the theorem says** (Published, [SG26]). Theorem 6.6 (2), ROM part: if the IOP is
round-by-round knowledge sound with errors at most `eps_k`, spBCS is adaptively knowledge sound
with extraction error at most `eps^C_ex(t) = (t + k_q)(eps_k + c'(t + k_q)/2^(8b))`. The
quantifier is in Definition H.3: "for every t and every (t, 0)-adversary A", and in Definition
H.4: "for every t in N and every (t, 0)-adversary". Section 6.3: "In Parts (1), (2), (3) and (5)
the adversary makes at most t hash queries". The paper adds, after Definition H.3, that the
definition "bounds the errors at every query bound". `k_q` is the verifier's hash-query bound
`2 N_msg + n_B + q_IOP (1 + floor(log2(2 max(1, l_max))))` (Definition I.1): almost all of it is
Merkle paths.

**Which reading the statement supports.** "Every t". The bound is stated, and holds, for every
`t >= 0`; nothing in the theorem restricts `t >= k_q`. The restriction is ours: it is a choice of
which adversaries a category-1 claim quantifies over, and it is not in [SG26]. So reading (a)
("`t >= k_q`") is a convention added to the theorem; reading (b) ("every t") is the theorem.

**What each reading loses** (V, with `category.b_counts` and the rows' own query bits).

| Row | (b) every `t`: count | Queries added | (a) kept: `eps(t) <= t / 2^129` is proved for `t >=` | below that, proved bound for the whole tree |
|---|---|---|---|---|
| 184, unique decoding, 1/8 | 192 | +8 | 56 hash queries | `2^-123.2` |
| 107, Johnson, 1/8 | 111 | +4 | 29 | `2^-124.2` |
| 80, Johnson, 1/16 | 82 | +2 | 9 | `2^-125.9` |
| 225, unique decoding, node 1/4 | 235 | +10 | 74 | `2^-122.8` |
| 165, Johnson, node 1/4 | 171 | +6 | 32 | `2^-124.0` |

- Under (a) with the rows as they stand (need 152.52, which is 8.2 bits above (a)'s own 144.29),
  the literal bound of [SG26] already gives `t / 2^129` for every adversary making at least 9 to
  74 hash queries, not merely at least `k_q` (19,000 to 46,000). What is lost is confined to
  adversaries making fewer hash queries than that: for them the proved bound is an absolute
  `2^-122.8` or better instead of `t / 2^129`, a shortfall of at most 6.2 bits at `t = 1`.
- Under (b) nothing is lost in the statement. The cost is 2.5% to 4.4% more queries on every row,
  with the proof bytes and verifier rows that follow. One consequence for the build (E, from
  `parameters.md` 14.4): the rate-1/8 Johnson merge slot fits `2^21` AND rows with 18 groups of
  six (108 query places); 111 queries need 19 groups, 2,058,958 + 64,036 = 2,122,994 rows, 1.2%
  over `2^21`. The rate-1/16 row keeps its 14 groups (84 places for 82 queries).

**Recommendation for the lead architect.** Keep the counts 107 / 80 / 184 / 225 (226 built), and
turn reading (a) from a convention into a proved statement by one lemma, before any row's label
drops the words "book convention":

> *Lemma M (to be written; Original as far as checked, the Ycash developers, 2026, this report;
> a sketch, unproved, unreviewed; sources consulted: [SG26] Section 6 and Appendix I as listed
> above, where no such statement was found).* In the random-oracle model, a proof is accepted
> only if every Merkle hash the verifier evaluates on an authentication path was queried by the
> adversary, except with probability at most `k_q / 2^(8b)`: an unqueried hash output is uniform
> and must equal a value already fixed (the root in the proof, or the input of a queried parent).
> Hence an adversary with fewer than `k_min` queries, `k_min` the least number of distinct path
> hashes of any accepted proof (at least one path per tree), succeeds with probability at most
> `k_q / 2^256`; and for `t >= k_min`, `t + k_q <= t (1 + k_q/k_min)`.

With Lemma M the classical need is `128 + log2(N) + log2(1 + k_q/k_min)` for **every** `t`. A
rough figure (E, not derived from the build): one path of 14 hashes in each of 6 trees,
`k_min = 84`, gives 150.4 (107), 151.1 (184), 151.4 (225) against the rows' 152.52: the counts as
they stand would hold for every `t`. The figure depends on tree depths, cap layers and the tree
count of each shape and must be derived per shape; if it does not come out under 152.52 for a
row, that row takes its (b) count. If the lead architect prefers no dependence on a lemma not yet
written, the answer is (b): 111 / 82 / 192 / 235 / 171, and the `2^21` merge slot at rate 1/8
needs trimming by about 26,000 rows. In neither case should a table call a row "certified" under
SG26 without naming the reading; today's tables do name it ("book convention"), which is correct.

## 8. Findings

| # | Class | Where | Finding | Fix |
|---|---|---|---|---|
| R8-1 | MAJOR (i) | rows 107, 80 | Unchanged from the second referee: both rest on [DKT26] Theorem 4.4, Corollary 6.6 (Lemma 3.3 unused by built shapes), a preprint whose proof was not checked here | conditions C-1 to C-7 of `johnson-row-referee-2.md` stand; revision 8 meets C-3 |
| R8-2 | MAJOR (i)-(iii) | `dkt26.py:90` (`need`), `:442` (`every_t_count`) | The need 152.52 is the book's convention for a transcript the build does not use; [SG26]'s own bound read as stated asks 111 / 82 / 192 / 235 / 171 | section 7: Lemma M, or the (b) counts |
| R8-3 | MAJOR (ii) | `dkt26.py:431` | The 165 row has no lemma stated, tested or refereed at rate 1/4, and no build | section 3 |
| R8-4 | MINOR | `dkt26.py:72` (`TERMINAL_ASSUMED = 1`), `:236` (`shape`) | assumption chosen to avoid the dimension-1 refusal | default terminal 0 with Lemma 3.3 for unrecorded shapes |
| R8-5 | MINOR | `dkt26.py:1-45` docstring; `CHANGELOG.md` revision 8 | "certified" for the unique-decoding rows is under the book convention only; say so where the word is defined (`CERTIFIED`, `:74`) | add "(book convention; see C-2)" to the string |
| R8-6 | MINOR | `dkt26.py:64` (`LOG_MSG`), table "proximity-gap parameters" | lengths `2^22` / `2^31` are caps above the built shapes (index bits 21 / 22), presented as the lines | name them caps in the docstring and heading; state the monotonicity argument (count linear in `n`, list uniform) next to them |
| R8-7 | MINOR | `dkt26.py:71` (`TERMINAL_AS_BUILT`), `terms` (the D-term, `:295`) | terminal dimension keyed by (kind, rate): the 184 row prints 6 x 7 where the build has 7 x 7; a rate-1/16 node has 4 or 5 by size | key by row, or charge `log_msg (2^r - 1)` |
| R8-8 | MINOR | `cli.py` `--rev5`, default, `--design`, `--basis`; `johnson.py:36`; `category.py:578-587` | Johnson rows printed without the preprint label; the Haböck route and the withdrawn 102 / 77 rows still offered | sections 5 and 6.1 |
| R8-9 | MINOR | `CHANGELOG.md` revision 8, "re-read ... from the PDF's text layer" | the text layer has no brackets; the reading it reports cannot have come from it alone | record that (36)-(38) were checked on the rendered page (this report, section 1) |
| R8-10 | MINOR | `dkt26.py:415` (`row`), `:308` (unreachable refusal), `:106` (`agreement`) | missing or non-integer `m` raises `TypeError`, not the refusal | validate `m` first |
| R8-11 | MINOR | `dkt26.py:236` (`shape`), `:268-292` (`lines_of`, `list_size`) | `log_terminal_dim` unvalidated: a "certified" row with no fold term, `ValueError`, `ZeroDivisionError` | refuse outside `0..log_msg` |
| R8-12 | NOTE | `dkt26.py:411` (`row`) | no margin floor; a "Johnson" row above the unique-decoding threshold is computed | section 5 |
| R8-13 | NOTE | `tests/test_revision8.py:224` `test_agrees_with_rowcalc_to_the_bit` | compares two programs of one authorship | add the exact recomputation of section 4 as a test with its own arithmetic and the boundary cases `(49, 36, 3)`, `(1652, 344, 10)` |
| R8-14 | NOTE | `yugen-proof-b2/src/params.rs:110, 250` | list size 29.70 / 42 valid, looser, unlabelled | section 6.4 |
| R8-15 | NOTE | `johnson-row-referee-2.md` 5.1, D-term row | 250.39 in the rate-1/16 column contradicts `n_f (2^r - 1)` | correct to 250.09 / 249.77 in a dated note |

## 9. Not checked

- The proof of [DKT26] Theorem 4.4 (Lemmas 4.1 to 4.3, A.5, Proposition B.1, Sections B.2, B.3)
  and the BCHKS dimension count; the theorem is taken as stated. Corollary 6.7's statement was
  read in part (the text layer breaks off at its display).
- Lemmas U, J1, J2, J3, K of `binius-johnson-row.md`; Lemma F was read, not re-proved. Haböck,
  ePrint 2024/1571, Lemma 3 (the per-query bound) and the weighted-measure framework were not
  opened: the per-query figure `(1 + 1/(2m)) sqrt(rho)` is taken from the johnson doc.
- The vendored Rust: no build was compiled or run. Shapes, arities, terminal dimensions and index
  bits are from `parameters.md`, one test's source and one result log.
- `johnson-row/rowcalc.py` and the `johnson-row/` tests (not read, by design, for section 4).
- [SG26] beyond the statements listed; its proofs; the QROM part of Theorem 6.6 (2) beyond one
  call of the calculator's own function at each row.
- Categories 2 to 5 (`--rev8 --category N` was run for 3 and 5 and read for labels only).
- `soundness-method.md` 8.8, `REFERENCES.md` and `CITATION-AUDIT.md` entries of revision 8.
- Lemma M is a sketch by this referee, not a proof; the figure `k_min = 84` is illustrative.

## 10. Provenance of this report

Published results used: [DKT26] and [SG26] at the places cited in each section. Original (the
Ycash developers, 2026; this report, first commit of this file; unreviewed): the row-by-row
hypothesis table of section 1; the exact recomputation of section 4 and its two boundary cases;
the per-row thresholds of section 7 (the least `t` from which the literal [SG26] bound gives
`t/2^129` at the rows' present counts); Lemma M as a proposed statement ("Original as far as
checked": only [SG26] was consulted for it).
