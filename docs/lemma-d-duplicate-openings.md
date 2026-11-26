# Lemma D: a position opened more than once (duplicate openings under spBCS)

Part of Yugen. `yugen-proofs`. **Revision 1 (2026-11-19).** Written by the maths team.
**A draft until refereed**: nothing here is reviewed, and no builder should cite it as settled before
the referee's report.

**Revision note (2026-11-19, after the referee's report `docs/lemma-d-referee.md`, commit `10277f9`:
PASS WITH CONDITIONS; not a rewrite).** Conditions m-1 to m-4 are applied: D-4 now counts every
record checked, padded group slots included (m-1; the calculator counts them since revision 10,
`category.b_counts`, and no query count moved); D-2 states system A's lazy cap linkage and section 3
gives the cap argument (m-2); "position" is the Merkle leaf index of each tree, after that tree's
shift (m-3, section 1 and D-3); the source note and B's audit line below are replaced (m-4). Edits by
the calculator's author at the lead's instruction. It replaces the sketch "Lemma D" of `qrom-compilation.md` 2.8 B-3
(`REFERENCES.md` O-66), whose part (ii) rested on a collision bound quoted from memory.

How the sources were read. [SG26], [CMS19] and [BCS16] were first read for this draft from the text
layer of the PDFs in the lead architect's folder. Every formula quoted below has since been compared
with the rendered pages by the referee (`docs/lemma-d-referee.md` section 1: [SG26] pages 13, 57, 58,
130, 131, 137 to 143; [CMS19] pages 20, 22, 33), with no discrepancy found. Page numbers are the
papers' printed page numbers.

- [SG26] C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized
  Signatures*, Cryptology ePrint Archive, Paper 2026/2615 (no venue stated in the copy).
- [CMS19] A. Chiesa, P. Manohar, N. Spooner, *Succinct Arguments in the Quantum Random Oracle
  Model*, Cryptology ePrint Archive, Paper 2019/834.
- [BCS16] E. Ben-Sasson, A. Chiesa, N. Spooner, *Interactive Oracle Proofs*, Cryptology ePrint
  Archive, Paper 2016/116.

## 0. Result

1. **The lemma needed is true, and the extra term is zero.** A verifier that accepts several
   openings of one position, each checked against the same root and never compared with each
   other, has the knowledge-soundness and soundness bounds of [SG26] Theorem 6.6 (2) **with the
   same formula and the same constants**, in the QROM and in the ROM, provided the verifier's
   hash-query count `k_q` counts one Merkle path per opening it checks (Theorem D, section 4). It
   does already: `q_IOP` in `qrom-compilation.md` section 4 and in the calculator is the number of
   **drawn** queries, repetitions included.
2. **Why no term is added.** The event "two different openings of one position both verify" is
   not a new event to pay for. The bad set `B` of [SG26] Lemma I.12 already contains every
   database with a digest collision anywhere, and its instability already charges for it: it is
   the `+ 1` in `c' = max(2, c) + n_J + 1` ("T bounds collisions", [SG26] page 140, after
   [CMS19] Lemma 6.11). Outside `B`, [SG26] Lemma I.14 shows that every opened leaf equals the
   one leaf the extractor reconstructs at that position; that sentence is about each opening
   separately and does not use that there is only one. So the theorem's own extraction argument
   covers the case (section 4).
3. **The sketch's part (ii), as it was written, is the wrong shape.** `eps' <= eps_ex(t) +
   Pr[collision]` is a black-box reduction to the de-duplicating verifier. It is provable from the
   papers in the folder, without Zhandry's bound from memory (Corollary D-bb, section 5), but it
   omitted two things (the reduction's own hash queries and the lifting term), and it charges for
   collisions twice. It is kept only as a cross-check: even in that form the cost is 0.0002 bits
   of the hash term, which does not bind.
4. **What each system must do: nothing new in the verifiers.** System A's flag walk under W-1 to
   W-7, system A's unmasked opening (`open_stacked`, one path a drawn query), and system B's
   in-circuit verifier (one opening a query, the filler repeating the first occurrence) all meet
   the conditions D-1 to D-5 of section 3 as described in their documents; the two native
   verifiers and wire formats carry one leaf a distinct position and meet [SG26]'s hypothesis
   literally. The write-once position table (option b') is **not needed**; section 7 states the
   invariant it would have to enforce if a referee rules otherwise.
5. **The calculator adds nothing.** One condition on it, already met: `q_iop` stays the count of
   drawn queries (section 8).

## 1. Setting and notation

[SG26] Protocol 6.5 (page 57) compiles a series–parallel IOP whose query list `qry(theta)` is "a
list ... without repetitions" (Definition 2.18, page 13), and its verifier "requires exactly one
salted leaf per position of `qry(theta)`" (Section I.1, "Prover and verifier", page 131). Call this
verifier `V`.

The IOPs of both systems draw `n` query positions per oracle from a challenge, with repetition:
`p_0, .., p_(n-1)`. The IOP verifier's decision is computed query by query (a fold of the opened
row at the query's point, summed with weights over the drawn order in system A; the FRI/BaseFold
consistency check of each query in system B). As a series–parallel IOP in [SG26]'s sense its query
list is the list of distinct positions, and the decision reads the symbol at `p_k` for each `k`.

**Position** (referee m-3). Throughout, a position is the **Merkle leaf index of one tree**: in a
tree whose leaf holds a coset, the drawn index after that tree's shift. So two records share a
position of a tree either because two draws repeat or because two distinct drawn indices fall in
one leaf of that tree (in system B this happens routinely in the later fold trees). Every statement
and proof below is per record and per tree, and covers both cases; `p_j = p_k` below means equal
leaf indices in the tree concerned.

**The multi-opening verifier `V'`.** A proof (or, in circuit, the advice) is the spBCS proof with
the openings replaced by a list of **opening records** per oracle; a record is (a drawn-query
index `k`, a salted leaf `(r, v)`, an authentication path). `V'` is any deterministic verifier with
the properties below. Both native verifiers are the special case "one record per distinct
position"; A's flag walk is "a record at each query flagged first"; A's `open_stacked` and B's
in-circuit verifier are "a record at every drawn query".

## 2. What must hold (the precise statement)

For soundness, two facts are needed, and together they are sufficient:

- **(S1) Equal copies change nothing.** If all records of `V'` at one position hold the same leaf
  input `(r, v)` and `V'` accepts, then `V` accepts the proof that keeps one record per distinct
  position; and an honest de-duplicated proof expands to one `V'` accepts (Proposition D.1).
- **(S2) Unequal copies are inside the theorem's failure event.** If `V'` accepts with two records
  at one position whose leaf inputs differ, then the set of hash queries `V'` made contains a
  digest collision (Proposition D.2); and the proof of Theorem 6.6 (2) already bounds every
  execution whose database contains a digest collision (Theorem D).

For zero knowledge, one fact: the multi-opening format is a deterministic function of the
de-duplicated proof and of challenges the adversary can recompute (Proposition D.Z, section 6).

## 3. Conditions on a multi-opening verifier

| # | Condition | Why it is needed |
|---|---|---|
| D-1 | Challenges, keys, streams and samplers are those of Protocol 6.5 step 2, recomputed from the items; the drawn positions `p_k` are read from the stream. | The base game and the database extractor are unchanged. |
| D-2 | Every record at query `k` is **authenticated at `p_k`**: its leaf input is hashed in the leaf part with its salt, and the path is walked with the left/right order given by the bits of the drawn position `p_k` (the verifier's own decoding of the stream, not advice) up to the root item of that oracle, the same root item that the challenge inputs absorb. With a cap, the walk ends at the cap entry the position's top bits select, and **every cap entry a walk lands on is linked to that root by node hashes the verifier itself evaluates** (a cap hashed lazily must hash the path from each reached entry to the root; m-2). | Proposition D.2. |
| D-3 | **Coverage.** The symbol used for drawn query `k` is the decoded leaf of a record authenticated at a position (the leaf index in that tree, after the tree's shift) equal to `p_k`'s: its own record, or the record of a query `j` with the same leaf index in that tree (whole indices compared) that has a record of its own. | Otherwise a drawn position goes unopened (`guest-masked-referee.md` 4.2). |
| D-4 | **Count** (restated after m-1). `k'_q` counts **every record the verifier checks**, padded slots included: a grouped verifier that repeats the last index in a group's unused places checks those records too, so `q_IOP` is the number of checked records (system B: the query count rounded up to the group unit, in each tree). | `k_q` of [SG26] Definition I.1 at that `q_IOP` bounds the verifier's hash queries; the calculator takes it so (revision 10). |
| D-5 | **Decision.** The decision is the IOP verifier's, evaluated on the non-oracle messages, the challenges and, for each drawn query, the symbol of D-3. Nothing else of a record enters the decision except through values that are functions of (the decoded leaf, the position, the challenges). | Proposition D.1. |

**System A, flag walk.** W-2 gives D-2 for a first-flagged query (own windows, cap to the level's
root, the root the transcript's). **The cap (m-2).** A's cap is hashed lazily: `verify_merkle_cap`
hashes only flagged nodes, so an unflagged node's hinted digest is unconstrained by itself. D-2 still
holds as built: `walk_path` writes flag 1 at the parent of the cap entry it reaches, an unflagged
node pins its children's flags to 0 (so every ancestor of a reached entry is flagged and hashed), the
root is always hashed, and all records of a level use the one hinted cap. Hence every cap entry a
walk lands on is joined to the level's root by node hashes the verifier evaluates, and Proposition
D.2's "the cap's own hashes to the root are common to both walks" applies (code as read by the
referee at `b467aa8`, `docs/lemma-d-referee.md` finding m-2). W-3 and W-4 give D-3 for a query flagged "as before" (`j < k`,
record `j` marked first, `positions[j] == positions[k]`). W-1 gives D-4 (a query is first or as
before, never both). W-5 and the record's content give D-5: the record holds the fold `(d0, d1)`,
which `wi_query` computes from the row, `positions[k]`, the query's windows and level-wide values
only (`yugen-proof-a/guests/e2/j_wi.py`, `wi_queries`, read at `b467aa8`); the windows are the
same drawn query's as the position (`guest-masked-referee.md` 4.1). W-6 is the well-definedness of
the reads; W-7 is the tests.

**System A, `open_stacked`; system B in circuit.** One record at every drawn query, each walked
to the root: D-3 and D-4 hold trivially. D-1, D-2 and D-5 are the correctness of those verifiers
as verifiers, which their own acceptance tests and referees cover; this document adds no
condition to them. B's D-2 (each slot's path walked by the slot's own drawn index into the one
absorbed root) was **audited by the referee at `yugen-proof-b2` `0f84f74`** (`docs/lemma-d-referee.md`
section 5). B's builder still records the one line in `yugen-proof-b2/docs/parameters.md`, with the
padded slots of m-1 (the grouped slot repeats the last index; D-4 as restated counts those records).

**Native verifiers.** One leaf a distinct position on the wire (A: `parameters.md` 2.5; B: VENDOR
change 34, an old-format tape refused): [SG26]'s `V` literally. Nothing to prove.

## 4. Statements and proofs

### Proposition D.1 (equal copies)

*Provenance: Original (the Ycash developers, 2026), elementary; it is part (i) of the sketch
(`qrom-compilation.md` 2.8, O-66), now with its conditions. Sources consulted for a prior
statement: [SG26] Sections 6.2, 6.3, I.1; [CMS19] Section 8; [BCS16] Section 6. None states it;
[BCS16] simply sends "an authentication path for each query" (Section 6, page 25).*

Let `V'` satisfy D-1 to D-5 and let `pf'` be a proof for it in which, at every oracle, all records
authenticated at equal positions hold the same leaf input. Let `pf` keep, at each oracle, one
record per distinct position (any one). Then: (a) if `V'` accepts `(x, pf')`, `V` accepts
`(x, pf)`; (b) if `V` accepts `(x, pf)`, `V'` accepts every expansion of `pf` that repeats kept
records (or flags queries "as before") in a way D-3 allows.

*Proof.* By D-1 both verifiers compute the same challenges and positions from the same items. By
D-2 a record is checked by `V'` exactly as `V` checks it. (a) If `V'` accepts, every record
passes, so the kept ones do; by D-3 and the hypothesis the symbol of drawn query `k` is the
decoded leaf of the kept record at `p_k`; by D-5 the decision of `V'` is the IOP verifier's on
those symbols, which is `V`'s decision. (Copies with equal leaf inputs may carry different
sibling digests; `V` sees only the copy kept, so this does not matter. Outside the bad set they
agree, by Proposition D.2's argument one level up.) (b) Each record of the expansion is a record
`V` accepted, and the symbols are the same. ∎

Only (a) is used for soundness; (b) is completeness of the in-circuit forms. The equivalence
"`V'` accepts if and only if `V` accepts" is **false** in general and is not claimed: `V'` also
rejects when a redundant copy has a bad path.

### Proposition D.2 (unequal copies give a digest collision)

*Provenance: Original (the Ycash developers, 2026) as a stated proposition; the argument is the
unique-preimage step inside the proof of [SG26] Lemma I.14 (page 141) and the standard Merkle
binding argument ([BCS16] Lemma 3.2, pages 14 to 15, classical).*

Let two records be authenticated (D-2) at the same position `q` of the same oracle against the
same root digest `rt`, with leaf inputs `u_0 = leaf(r, v)` and `u'_0 = leaf(r', v')`. Let
`u_0, u_1, .., u_h` and `u'_0, .., u'_h` be the oracle inputs the verifier evaluates along the two
walks (`u_(j+1)` is the node input made of the digest of `H(u_j)` and the path's sibling, ordered
by bit `j` of `q`; `dg(H(u_h)) = dg(H(u'_h)) = rt`; with a cap, the cap's own hashes to the root
are common to both walks). If `(r, v) != (r', v')`, there are two **distinct** inputs among these
with the same digest.

*Proof.* The leaf encoding is injective ([SG26] Section I.1, "The oracle's domain"; for our byte
layouts `qrom-compilation.md` 2.2, 2.8: fixed-length rows and salts), so `u_0 != u'_0`. Take the
largest `j` with `u_j != u'_j`. If `j = h`, the two inputs have digest `rt`: a collision. If
`j < h`, then `u_(j+1) = u'_(j+1)`; the node encoding is injective and both walks put their running
digest on the same side (the same bit of the same `q`), so `dg(H(u_j)) = dg(H(u'_j))` with
`u_j != u'_j`: a collision. The two walks have the same length because the tree's shape is a
function of the oracle's length (D-2), so no leaf input is compared with a node input at different
heights; and if it were, the parts are disjoint and it would still be two distinct inputs. ∎

The proposition is deterministic and holds for salts of any length, including 0 (node proofs),
and for both builds of system B (under MA-2 or MA-2' the leaf and node parts are disjoint parts of
one oracle, which is all the proof uses). Two openings with the same row and different salts are
distinct leaf inputs and are covered.

### Theorem D (knowledge soundness of the multi-opening verifier)

*Provenance: **Adapted** from [SG26] Theorem I.16 (page 142) and its proof through Lemmas I.12,
I.14 and I.15 (pages 140 to 142). Change: the verifier of Protocol 6.5 step 2 ("exactly one salted
leaf per position") is replaced by a verifier satisfying D-1 to D-5; the base game's second
condition and the count `k` of appended queries follow the new verifier; the database algorithm,
the bad set and every bound are [SG26]'s unchanged. The adaptation and the check that each step
survives are the Ycash developers' (2026), unreviewed. [SG26] reports a machine-checked proof of
its own statements (its table mapping Lemma I.14 to `SPBCS.cover_simExtGame`); the adapted
statement is **not** machine-checked.*

Let IOP, `eps_k`, `E`, `b`, `e`, `c`, `n_J` be as in [SG26] Theorem I.16, and let `V'` satisfy D-1
to D-5. Let `k'_q` bound the hash queries of `V'`. Then with `V'` in place of `V`, the argument is
adaptively knowledge sound ([SG26] Definition H.3) with the database extractor of Protocol I.9,
oracle simulation error 0 and extraction error at most

    eps'_ex(t) = 2 sqrt( k'_q / 2^(8(b+e)) ) + 6 (t + k'_q)^2 ( eps_k + c' (t + k'_q) / 2^(8b) )   (QROM)
    eps'^C_ex(t) = (t + k'_q) ( eps_k + c' (t + k'_q) / 2^(8b) )                                   (ROM)

with `c' = max(2, c) + n_J + 1`, for every `t`, and has adaptive soundness error at most the same
([SG26] Definition H.4, Lemma H.5). By D-4, `k'_q <= k_q = 2 N_msg + n_B + q_IOP (1 +
floor(log2(2 max(1, l_max))))` with `q_IOP` the number of records checked (drawn queries plus
padded slots; m-1), so `eps'_ex <= eps_ex` at that `k_q`.

*Proof.* We go through the proof of [SG26] Theorem I.16 (1) and say what each step uses.

1. *The extractor* (Protocol I.9) runs the adversary against the compressed oracle, appends the
   verifier's queries for the output `(x, pf')`, measures the database `db`, and runs the database
   algorithm, which reconstructs transcripts from recorded challenge inputs and recovers leaves
   "from its roots by following each digest through its unique recorded preimage". None of this
   refers to the proof's openings. Unchanged, with `V'`'s queries appended (`k = k'_q`).
2. *The bad set `B`* ([SG26] Lemma I.12): databases with a digest collision ("two distinct
   recorded inputs whose answers have the same digest") or a knowledge failure. Its definition and
   its instability bound `I(B, T) <= eps_k + (max(2, c) + n_J + 1) T / 2^(8b)` are statements
   about databases and the database algorithm only. Unchanged.
3. *The base game* ([SG26] Definition I.13) with `V'` in its second condition: tuples (statement,
   proof, appended inputs with answers) such that `V'` accepts with all its queries among the
   appended ones, answered as recorded. It has `k'_q` oracle inputs.
4. *Lifting* ([SG26] Lemma I.15, from [CMS19] Lemma 4.9, page 20, and Lemmas 5.7, 5.9, 5.10,
   page 22): holds for every base game with `k` oracle inputs and every set of databases not
   containing the empty one. Unchanged, with `k = k'_q`.
5. *Extraction outside the bad set* ([SG26] Lemma I.14). **This is the only step that reads the
   openings**, and it is re-proved here for `V'`. Let `db` not in `B` agree with a tuple of the
   game of step 3, with proof `pf'`. As in [SG26], every answer `V'` reads is recorded in `db`,
   and at every verifier message the challenge input and stream point are recorded, the stream's
   digest is the written-back digest, and the sampler succeeds.
   Take any record of `pf'`, at drawn query `k`, oracle `O`, position `q = p_k`, with walk inputs
   `u_0, .., u_h` (D-2). All of them are recorded in `db` with the answers `V'` read, and
   `dg(H(u_h))` is the root item `rt` of `O`. `db` has no digest collision, so `rt` has exactly
   one recorded preimage, which is therefore `u_h`; the database algorithm descending from `rt`
   towards position `q` takes the child digest on the side of `q`'s bit, which is `dg(H(u_(h-1)))`,
   whose one recorded preimage is `u_(h-1)`; and so on down to `u_0`, a leaf preimage, which
   "gives a leaf's salt and bytes". So **the leaf the extractor reconstructs at `q` is this
   record's leaf, for every record**. In particular two records at one position hold the same leaf
   input (this is Proposition D.2 read in `db`), and by D-3 the symbol `V'` uses for each drawn
   query is the reconstructed symbol at its position.
   Define `tr` as [SG26] does: the non-oracle messages and challenges of `pf'` and of the
   verifier's execution, and at each oracle position the reconstructed leaf, or the default.
   `tr` restricted to each past is the past the database algorithm reconstructs at the verifier's
   challenge input (same argument as [SG26]: each item comes from `pf'` or from a unique
   preimage). By D-5 the decision of `V'` is the IOP verifier's on values that agree with `tr`, so
   the IOP verifier accepts `tr`. The rest is verbatim: either `E(x, tr|past(i))` is a witness for
   some `i`, and the extractor outputs one, or by condition (a) of [SG26] Definition 2.20 there is
   a knowledge failure at a recorded challenge input, so `db` is in `B`, a contradiction.
6. *Conclusion*, as in [SG26]: `Pr[v = 1 and no witness] <= (Pr[G : oracle] - Pr[G : simulated])
   + Pr[db in B] <= 2 sqrt(k'_q / 2^(8(b+e))) + 6 T^2 I(B, T)` with `T = t + k'_q`.

The ROM part is [SG26] Theorem I.16 (2) with the same step 5: the table of the classical
execution is the database, and the union bound gives `T` times the instability. The oracle
simulation error is 0 as in [SG26] (Lemmas I.10, I.11 do not refer to the verifier's form). ∎

**Corollary (the term in bits).** The extra term for duplicate openings is **0 bits** in both
models, at every `t`: `eps'_ex` is `eps_ex` evaluated at the same `k_q` the project already uses.
Every figure of `qrom-compilation.md` section 5 and of calculator revision 9 stands (condition Q:
A 69.58, B 70.45 against 64; the classical needs at each row's own `k_q` under "every t",
`decision-qrom-counting.md`). *(Amendment 2026-11-19, revision 10.2: the tree's QROM figures 69.58 / 70.45 are derived under the recursion heuristic C2 and conditional on K-A, K-B and T-1, not proven QROM figures; `docs/what-is-proven.md`.)* The parameters enter only through quantities already in the tables:
`b = 32` for both systems (Keccak-256 keys and digests in A, whose 16-byte part tags do not
shorten the digest; SHA-256 keys in B), `c'` = 2,397 (A) and 2,401 (B), `N = 20,000`.

Weak online simulation extractability ([SG26] Theorem I.17) uses the same Lemma I.14; the same
change of step 5 applies. It is not used by the project's present claims and is not re-proved
line by line here.

## 5. The black-box form (cross-check only): Corollary D-bb

*Provenance: **Adapted**. The reduction is the sketch's part (ii) (Original, O-66), corrected; the
collision bound is [CMS19] Lemma 5.7 (page 22) with Lemma 6.11 (page 33) and Lemma 4.9 (page 20),
in the form [SG26] Lemma I.15 states them; [CMS19] Section 2.3 (page 11) states the consequence
"`O(t^3 / 2^n)`" for the collision game. This replaces the sketch's citation of Zhandry from
memory: no source outside the folder is needed.*

Treat Theorem 6.6 (2) for `V` as a black box. From an adversary `A'` against `V'` build `A`
against `V`: run `A'`, recompute the challenges of its output (`2 N_msg` further hash queries),
keep the first record at each distinct position. If `V'` accepts and `V` does not accept the
shortened proof, then by Proposition D.1 two records at one position differ, and by Proposition
D.2 the queries of `V'` on `A'`'s output contain a digest collision. The probability that a
`t`-query algorithm outputs inputs whose appended evaluation (at most `k'_q` queries) contains a
digest collision is at most `2 sqrt(k'_q / 2^(8(b+e))) + 6 T^2 * T / 2^(8b)`, `T = t + k'_q`
(Lemma I.15 with the collision set, whose instability is below `T / 2^(8b)` by the argument of
[CMS19] Lemma 6.11). So

    eps'(t) <= eps_ex(t + 2 N_msg) + 2 sqrt( k'_q / 2^(8(b+e)) ) + 6 (t + k'_q)^3 / 2^(8b).

Against the sketch: `t + 2 N_msg` in place of `t`, and a second lifting term (below `2^-2800` at
our stream lengths). In bits, tree of `N = 20,000`, `b = 32`:

| Quantity | System A | System B |
|---|---|---|
| Collision term alone: `kappa` with `N 6 T^3 / 2^256 = 1/2` | 79.38 | 79.38 |
| The same term at `T = 2^64` | `2^-47.1` | `2^-47.1` |
| Hash term of the theorem (`6 c'`), section 5 of `qrom-compilation.md` | 75.6334 | 75.6326 |
| Hash term with the collision term added (`6 (c' + 1)`) | 75.6332 | 75.6324 |
| Loss | 0.0002 bits, in a term that does not bind (the IOP term binds at 69.58 / 70.45) | the same |
| Classical, `t = 1`: `N (1 + k_q)^2 / 2^256` at the section-4 `k_q` | `2^-210.7` | `2^-211.2` |

(Computed in this pass with a few lines of Python from the formulas above; not part of the
calculator.) So if the referee rejects Theorem D's white-box route, the black-box route still
holds every figure to the second decimal. It is not the claim made.

## 6. Zero knowledge, salts, leaf framing

*Provenance: Original (the Ycash developers, 2026), a data-processing remark on [SG26] Theorem 6.6
(3), (4) (page 59; Definition 6.2, page 54).*

**Proposition D.Z.** Let `F` be a deterministic polynomial-time oracle procedure that maps a
de-duplicated proof `(x, pf)` to a multi-opening form by recomputing the challenges (queries at the
proof's own challenge inputs and stream points only, at most `2 N_msg` of them) and then repeating
or flagging records. If spBCS is everlasting zero knowledge with error `eps_zk(t, Q)`, the scheme
whose prover outputs `F(pf)` is so with error `eps_zk(t + 2 N_msg (Q - 1), Q)` and simulator
`F` applied to the simulator's proof; witness indistinguishability (Theorem 6.6 (4)) is unchanged.

*Proof.* A distinguisher for the `F`-forms yields one for the de-duplicated forms that applies `F`
to each proof it receives, with its own oracle access (in the simulated world, the reprogrammed
oracle, under which the simulated proof's challenges are the simulator's). The `2 N_msg` queries
after each of the first `Q - 1` proofs count towards `t`; those after the last proof do not
(Definition 6.2). Witness indistinguishability is a statistical distance of `(H, proofs)`, which a
function of `(H, proofs)` cannot increase. ∎

As built this proposition is not even invoked: **both wire formats are de-duplicated**, so the
published proofs are [SG26]'s; the multi-opening form exists only as advice of an in-circuit
verifier, where an honest host's advice is such an `F(pf)`. A repeated record repeats the same
salt and the same leaf bytes, so it reveals nothing the single record does not; no fresh salt is
drawn for a copy and none is needed. The leaf term `n_pos eps_leaf` counts salted leaves of the
tree, not openings. Salts and leaf framing interact with this lemma in one place only:
Proposition D.2 needs the leaf encoding `(r, v) -> bytes` injective, which holds for both systems'
framings at fixed salt length (`qrom-compilation.md` 2.2, 2.8 A-1, B-4). A cheating prover's
flags are a soundness matter, not a zero-knowledge one.

## 7. The opposite direction, and the fallback

**A query flagged "as before"** (system A only; the other verifiers have no such flag). What is
checked: W-3 (`j < k` against the loop's own `k`, and record `j` marked first), W-4
(`positions[j] == positions[k]`, whole position, same level; the records array is allocated per
level inside `wi_queries`, so `j` cannot name another level's record). What is copied: the fold
`(d0, d1)`. What is not re-checked for query `k`: the row hash, the path, and at the last level the
check `P*(x) = column + c fold`. Each of these is a function of the row, the position and
level-wide values, and was checked for record `j` at the same position; so query `k`'s values are
exactly those a first-flagged opening of the same leaf would give. The weight `lambda^(k+1)` is
applied to query `k` itself (W-5), not copied. A query flagged "as before" when no earlier
first-flagged query shares its position is refused by W-4 or the mark. **Nothing is left
unchecked**, in agreement with the referee's 4.3; in the terms of section 3 it is D-3.

One point for the referee to confirm at the code (not a finding): the fold must not depend on
anything per-query beyond the position and the windows decoded from the same stream field. Read at
`b467aa8`, `wi_query` receives `positions[xi]` and `query_win_ptrs[xi]` and level-wide arguments
only.

**The fallback, option b' (not needed under Theorem D).** If the lead architect or a referee
rules that the in-circuit verifier must meet [SG26] H7 as stated, the write-once position table
must enforce exactly: *per oracle, the map from first-flagged queries to their positions is
injective.* Concretely: (1) one table per oracle (or the level in the cell index), indexed by the
**whole** position, with the same encoding W-4 compares; (2) a first-flagged query `k` writes a
value that is **different for different `k`** (its index or `g^k`) to cell `p_k`: write-once
memory accepts a second write of an equal value, so writing a constant enforces nothing; (3) with
W-3 and W-4 unchanged, every drawn position then has exactly one record, which is `V` itself.
The same table would serve `open_stacked` only together with a flag walk there (today it opens a
row at every query, so a table alone would refuse every honest proof with a repeated position).
For system B's circuit the equivalent is a comparison of leaf and salt wires between slots at
equal indices, which a fixed-shape circuit can do only for all pairs or after sorting.

## 8. The calculator

No term is added and no formula changes (`soundness/src/yugen_soundness/spbcs.py`, `category.py`).
One condition, stated for the calculator's author and already met: `TranscriptCounts.q_iop` (and
each row's own `k_q` under "every t") counts **drawn** queries, one Merkle path each, and must not
be lowered to the number or expected number of distinct positions while any in-circuit verifier
checks one record per drawn query (D-4). The field's comment "largest number of opened positions"
should say "drawn queries". Not edited here.

## 9. What a referee should attack first

1. **Step 5 of Theorem D against the paper's Lemma I.14**, sentence by sentence: is there any
   other place in [SG26] Sections I.3, I.4 (Protocol I.9, Definition I.13, Lemmas I.10 to I.15)
   that uses "exactly one leaf per position"? We found none: the database algorithm never reads
   the proof's openings, and Lemma I.12 never reads the proof at all.
2. **D-2 for each in-circuit verifier**: that every record is walked by the drawn position's own
   bits into the root item the transcript absorbed. For B's circuit this is taken from its
   documents, not audited (section 3). A walk whose direction bits were advice would break
   Proposition D.2's "same side" step.
3. **D-5 for system A's fold record**: that `(d0, d1)` is a function of (row, position,
   level-wide values) only (section 7).
4. **The count D-4 / `k'_q`** with caps: the cap's hashes and the per-opening walks are within
   `q_IOP (1 + floor(log2(2 l_max)))` as `qrom-compilation.md` section 4 counts them.
5. **The formulas**, against the typeset pages of [SG26] pages 140 to 143 and [CMS19] pages 20,
   22, 33 (read here from the text layer).
6. **Recursion in the QROM** is outside this lemma: Theorem D bounds an adversary that outputs
   advice the guest's computation accepts; how an outer proof's extraction delivers that advice is
   the tree accounting's (`soundness-method.md` 8.5b, O-13) and is unchanged by this document.
7. **Obligations K-A, K-B, the modelling assumptions MA-1, MA-2, MA-2'** stand as before; Theorem D
   inherits them.

## 10. Provenance table

| Result | Label | Source / relation | Where |
|---|---|---|---|
| spBCS, Theorem 6.6 (2), Theorem I.16, Lemmas I.12, I.14, I.15, Protocol I.9, Definitions 2.18, I.1, I.13, H.3, H.4 | **Published** [SG26] (pages 13, 57 to 59, 130 to 131, 137 to 143) | used as stated | sections 1, 4 |
| Lifting lemma, collision instability, oracle vs simulated game | **Published** [CMS19] Lemma 5.7 (page 22), Lemma 6.11 (page 33), Lemma 4.9 (page 20), Section 2.3 (page 11) | through [SG26] Lemma I.15; directly in section 5 | sections 4, 5 |
| Classical Merkle extraction with a path per query | **Published** [BCS16] Section 6 (page 25), Lemma 3.2 (pages 14 to 15) | context only: the classical analysis never needed distinct positions | section 4 |
| Conditions D-1 to D-5 | **Original (the Ycash developers, 2026)**; D-3 restates the referee's W-3, W-4 (`guest-masked-referee.md` 4.3) | this document | section 3 |
| Proposition D.1 | **Original (the Ycash developers, 2026)**; first as the sketch's part (i), `qrom-compilation.md` 2.8 (`e41de26`) | sources consulted: [SG26], [CMS19] Section 8, [BCS16] Section 6 | section 4 |
| Proposition D.2 | **Original as a stated proposition**; the argument is the unique-preimage step of [SG26] Lemma I.14 and standard Merkle binding | | section 4 |
| Theorem D | **Adapted** from [SG26] Theorem I.16 (change: the verifier's opening rule; step 5 re-proved) | not machine-checked, unlike [SG26]'s own statements | section 4 |
| Corollary D-bb | **Adapted** (the sketch's part (ii), corrected, with [CMS19]'s bounds in place of a citation from memory) | cross-check only | section 5 |
| Proposition D.Z | **Original (the Ycash developers, 2026)** | data processing on [SG26] Theorem 6.6 (3), (4) | section 6 |
| The b' table invariant (distinct written values) | **Original (the Ycash developers, 2026)**; option b' itself is system A's (`yugen-proof-a/docs/recursion.md` 10.0000) | not needed under Theorem D | section 7 |
| The flag walk and W-1 to W-7 | system A's builder and the referee (Original, the Ycash developers, 2026) | read, not changed | sections 3, 7 |
