# Lemma TE: extraction down the proof tree (the reduction of `soundness-method.md` 8.5b)

Part of Yugen. `yugen-proofs`. **Revision 3 (2026-11-19)**, applying the second referee's report
`docs/qc-and-status-referee.md` (findings T-1 to T-5, Q-1 to Q-4) to revision 2 (commit `44b751d`). Revision 2 applied
the first referee's report `docs/tree-extraction-referee.md` (findings F-1 to F-7, conditions C-1 to C-7) to revision 1
(commit `f414811`). Revision 1 was written by the calculator's author after `docs/rev10-referee.md` finding R10-2.
Status: revision 1 was refereed (**pass with conditions**); revision 2 was refereed in `qc-and-status-referee.md`
(Theorem TE' with TE-X, TE.1 and TE-Q': **pass with conditions** T-1 to T-4; Lemma QC: **pass**); **revision 3 is the
restatement those conditions ask for and has not itself been refereed**. No figure moves from revision 2.
**Revision 3.1 (2026-11-19, `zkq-te3-r8-referee.md` M-3, N-3):** the shape check moves to after the child's witness is
extracted (step 3, Lemma TE.3 (a)); H-BIND lists A's `merge_statement` and `Hvar_bundle-kids`; the node stop is
`N + 16`; part (b) covers the root's header count; row 0 of A recorded (N-3, after Lemma TE.3). Provenance:
**Original (the Ycash developers, 2026)**, adapting [SG26]'s knowledge-soundness proof (section 11 says exactly what is
taken and what is changed).
**Revision 4 (2026-11-19), draft, unrefereed.** Collects the obligations owed to this lemma by the proposed tree shape
and System B's new aggregation: `tree-shape-referee.md` condition 5 (shape 4/4/5, overshoot `N + 4`, depth enters
termination only), `b-aggregation-referee.md` condition 2 and `b-internal-node-referee.md` conditions 3 to 5 (B's
internal arity-2 nodes, kinds K0, KM, KI, KI0; the node bound by shape and kind; H_int added to H-BIND; cells bound
through `E`), and `b-fold-referee.md` condition 4 (the carried-claim fold of `yugen-proof-b2` `wt/s045` branch `agg`,
`docs/parameters.md` section 24: node relation = "accepts and the carried `W*` claim is true", extraction conditioned
on the root discharge, a deferred-claim union term and a per-node batching error). The statement is made parametric in
the shape `(a_s, a_m, d)` (sub-bundle size, merge arity, depth); revision 3.1's 16/16/3 is one instantiation and
4/4/5 the other. New text is section 6b and the marked edits in sections 1 to 3 and 10; **no earlier figure moves**
except as section 6b states.

**Revision 5 (2026-11-20), draft, unrefereed.** Applies `tree-extraction-rev4-referee.md` (`f32848e`, pass with
conditions) R4-1 to R4-8 to section 6b: two-pass argument for the fold (extraction under "accepts", then truth of the
carried claims from the root discharge; one fixed `W*` of the four pinned keys); B's node count 8,193 at 4/4/5 as the
theorem's term; the `2^-106.5` figure dropped; the batching term restated per query, `(t + K) eps_batch,max`, beside
`t eps_max` and outside `k_q`, with the challenge field read per build (`GF(2^128)` default, `GF(2^256)` under
`cat1`/`cat1t`); internal-node condition 5 marked built; built constants `m = 4`, `n + 2 = 74`, `k_q` 40,568; 4/4/5
marked a proposal (spec 0.4.7 section 15 is 16/16/3); the root discharge added to the C2 list. **Figure moved:** at
the default build B's tree caps at 120.76 classical / about 60.4 quantum bits; under the 256-bit challenge build no
stated figure moves.
**Revision 5.1 (2026-11-20), draft.** Applies `tree-extraction-rev5-referee.md` (`cabb19c`, pass with conditions
R5-1 to R5-4) to section 6b. R5-1: the fold is refused without `challenge256` (`yugen-proof-b2` branch `agg`, commit
`0613c6c`), so the default-build row is a build that cannot be constructed. R5-2: the quantum column is labelled order
only. R5-4: `vfinal`'s random-point check of the root discharge was run (log cited in 6b (d)). No figure moves. Status
stays **draft** until a referee report names a PASS on revision 5.1.
**Revision 5.2 (2026-11-20), draft.** Applies `tree-extraction-rev51-referee.md` (`d31ce64`, pass with editorial
conditions R51-1 to R51-3): the versioned `bench/results` records of the root-discharge check are cited (R51-1); both
root evaluators (`fold::evaluate`, and `phased::Stacked` since `cc6a794`) are named in 6b (c) and the C2 list (R51-2);
line citations in 6b are pinned to commit `13e0e9d`, with `check_root`'s refusal at line 170 at `8d1517f` (R51-3). No
figure moves. Status stays **draft** until a referee report names a PASS on revision 5.2.
**Revision 5.3 (2026-11-20), draft.** Applies `te3-referee.md` (`1056ea6`, SHAPE-VIOLATION, Lemma TE.3 and H-BIND:
pass with conditions TE3-1 to TE3-5): `eps_bind` is defined over the primitives on any two distinct inputs (TE3-1);
stated numerically, no H-BIND link is 48 bytes, and it lowers no printed level (TE3-2); H-DS is named beside C-4 in
TE.3, the non-collision exits listed and the `Stream::piece` caveat carried into TE.3 (a) (TE3-3); H-BIND as the
explicit-reduction form (TE3-4); section 11 and `what-is-proven.md` record the report (TE3-5). Also the System A note
on `merge_statement`. No figure moves. Status stays **draft**.

**What changed from revision 2** (each item names the second referee's finding):

| Finding | Revision 2 | Revision 3 |
|---|---|---|
| T-1 (MAJOR) | "the tree's shape bounds the reached nodes by `N` (the node circuits check the shape)"; H-BIND "only for Corollary TE-S", "modelled as a further random-oracle part" | the node count and termination rest on the depth and proof count being bound through the **concrete statement digest** computed inside the fixed relation. **H-BIND is restated as collision resistance of the concrete statement-digest functions** (a standard-model assumption, not an oracle property; section 2), and `E_T` has a fourth outcome, **SHAPE-VIOLATION** (section 3), with `Pr[SHAPE-VIOLATION] <= eps_bind` (Lemma TE.3, section 6). `K <= N k_q,max` holds for every run, since `E_T` stops before an `(N + 1)`-th node. The figure `T^2 / 2^(8b + 1)` is dropped |
| T-2 (MINOR) | "conditional on C2" | stated as a **joint probability**, with what a reader may and may not conclude; equivalence tests do **not** discharge C2 (section 6, "How to read 'conditional on C2'") |
| T-3 (MINOR) | quantum version of Corollary TE-X asserted in one sentence | written out as Corollary TE-X-Q (section 9), labelled **sketched**; TE-X's content stated as knowledge soundness of a **batch** of published proofs on one table |
| T-4 (MINOR) | H-DS: "each statement carries its system's verifying-key or circuit digest" | within one system, H-DS rests on `pre(x)`: row and bound IV for A, `StatementId` for B, and on the binding of those digests to the program (section 2) |
| Q-2 (MINOR) | Proposition TE-Q' bounded FAIL | bounds **FAIL or DEVIATION**; the right side is unchanged (section 9) |
| Q-3 (MINOR) | the capacity remark gave half the argument | one sentence on the padding embedding ([CMS19] Lemmas 5.9, 5.10, page 22) (section 9) |
| Q-1, T-5 (NOTE) | - | the constant 10 of Lemma QC is not tight (section 9a); B's node-rule switches: the consensus constraint-system digest is the all-on rule set's (section 3, audit owed) |

**What changed from revision 1 to revision 2** (each item names the first referee's finding):

| Finding | Revision 1 | Revision 2 |
|---|---|---|
| F-1 (MAJOR), C-1 | Theorem TE "under H-C2", a hypothesis on witnesses that is **false in the ROM** (section 1.1 of the report), called "proved here, with a full proof" | **Theorem TE'** (section 6), a theorem of the ROM with the same bound: the extractor stops with the outcome **C2-VIOLATION** when a child verifier rejects, and the bound is on the event "accepted, and neither a compliant tree nor a C2-VIOLATION". The recursion heuristic C2 is the named event "accepted in-circuit, rejected natively", outside the theorem; it enters at **two** places (section 2) |
| F-2 (MINOR), C-2 | "`B*` is monotone" | two-sided instability, as [SG26] Lemma I.12 states it; "the final table is in `B*`" replaced by "the table is in `B*` at some step". **The bound is unchanged** |
| F-3, C-3 | (K) owed, stated | every tree figure is marked conditional on K-A, K-B (section 7) |
| F-4, C-5 | `E_T` step 3 did not test the child verifier's verdict | it does, and stops with C2-VIOLATION |
| F-7 (MAJOR), C-6 | QROM step (ii) "from memory" | **Lemma QC** (section 9a, the referee's proof from [CMS19] Lemma 3.2, unrefereed) and the corrected `E_T^Q` (section 9); one added term `10 (K - k_q,r) / 2^(8(b+e))`, about `2^-222.9` (A) and `2^-223.1` (B) at category 1 |
| C-7 | "proven QROM figure for the tree" | "derived under the recursion heuristic C2", never "proven QROM" |

How the sources were read. Every statement of [SG26] used below was read from page images rendered with pypdfium2
(scale 2.0 for revision 1; pages 140 and 142 again at scale 1.7 for revision 2) from the lead architect's copy: pages 53
(Definition 6.1), 58 (Section 6.3, Theorem 6.6), 59 (the remark on stream lengths; "Parts (1) and (2) follow known
arguments"), 128 and 129 (Definitions H.3, H.4, Lemma H.5), 137 and 138 (Section I.3, Protocol I.9), 140 and 141
(Lemma I.12 with its proof, Definition I.13, Lemma I.14 with its proof), 142 to 144 (Theorem I.16 with its proof,
Theorem I.17). [CMS19] Lemma 3.2 (printed page 17) was read for revision 2 from the rendered page (pypdfium2, scale
1.8). For revision 3, [CMS19] page 22 (Definition 5.6, Lemmas 5.9, 5.10, footnote 6) is used as the second referee
read and quoted it (`qc-and-status-referee.md`, sources); it was not re-read for this revision. Page numbers are the
papers' printed numbers.

- [SG26] C. Sharp, P. Grubbs, *Faster and Smaller Anonymous Credentials from Standardized Signatures*, Cryptology
  ePrint Archive, Paper 2026/2615 (a preprint; no venue stated in the copy).
- [CMS19] A. Chiesa, P. Manohar, N. Spooner, *Succinct Arguments in the Quantum Random Oracle Model*, Cryptology ePrint
  Archive, Paper 2019/834 (copy dated 2020-01-14). Lemma 3.2 there is attributed to Zhandry and proved in its
  Appendix A, which was **not** read.

## 0. Result

1. **What was missing.** `soundness-method.md` 8.5b walks down the tree using "a true statement has an accepted child
   proof". That is existence. Soundness ([SG26] Definition H.4) bounds only proofs the adversary **outputs**, and the
   adversary publishes the root proof alone. So the tree claim needs a statement that the child proofs inside an
   accepted root can be **extracted**, and a bound on the probability that this extraction fails anywhere in the tree.
2. **Theorem TE' (section 6), in one sentence.** In the random-oracle model, under H-DS and the round-by-round
   knowledge soundness of every proof system of the tree (obligations K-A, K-B), one straight-line extractor that
   answers the adversary's queries by lazy sampling, runs the root verifier and then, node by node, [SG26]'s database
   algorithm and the child verifiers on the same table, ends, for every accepted root, with a compliant tree of
   witnesses or with the named event **C2-VIOLATION** (a child proof the in-circuit verifier accepted and the native
   verifier rejects) or the named event **SHAPE-VIOLATION** (an extracted child's depth, child count or proof count
   contradicts its parent's, or more than `N` nodes are reached), except with probability at most
   `t eps_max + sum_v |J_V,v| eps_v + c'_max (t + K)^2 / 2^(8b)`, where `K` is the sum of the verifiers' hash-query
   bounds `k_q,v` over the tree; and SHAPE-VIOLATION has probability at most `eps_bind`, the advantage of a
   collision finder against the concrete statement-digest functions (H-BIND, Lemma TE.3). **This is a theorem of
   the ROM plus one standard-model collision-resistance assumption, with a full proof here; revisions 1 and 2 were
   refereed (pass with conditions) and the revision-3 restatement is unrefereed.**
3. **What is unconditional and what is not.** Unconditional in the ROM (given (K), H-DS, H-BIND and [SG26]): the **root**
   proof (that is [SG26] Theorem 6.6 (2) itself), and **a tree whose every proof is published and verified natively**
   (Corollary TE-X: no child is reached through a witness, so C2-VIOLATION cannot occur; same table, same bound, `t`
   shared). **Conditional on C2** (that C2-VIOLATION does not occur): every statement about a recursion tree whose
   inner proofs are witnesses, which is the tree the chain accepts. C2 is used at **two** places (section 2): for the
   child's native acceptance, and for keeping the node relation oracle-free so that (K) and Lemma TE.1 apply. No proof
   in the ROM can remove it (`tree-extraction-referee.md` 1.1). "Conditional on C2" is a **joint** probability, never
   a conditional one (section 6, "How to read 'conditional on C2'"), and in-circuit / native equivalence tests do
   **not** discharge C2.
4. **What the figures become (section 7).** No query count moves: every row the calculator certifies already makes the
   IOP part at most `t / 2^(kappa_C + 1)` for every `t` (Corollary TE-F (a)). The hash part is taken **once for the
   tree**: the classical level of the tree's hash part is **121.89 bits** (A 121.886, B 121.885) **under C2, K-A, K-B
   and T-1**, in place of the per-proof sum's **114.74**, which the calculator (revision 10.2) prints beside it as the
   comparison. Still 6.1 bits short of 128 at 256-bit digests: category 1's classical hash part stays on condition H's
   attack rule.
5. **The black-box form moves figures** (section 8). Composing [SG26] Theorem 6.6 (2) as a black box, node by node,
   raises the IOP need at `t = 1` by about 14.3 bits in the form `sum_v eps_ex,v(t + N k_q)`, and by **2.3 bits (B)
   to 3.9 bits (A)** a round when only the ancestors' queries are charged. Theorem TE' does not need it.
6. **The QROM (sections 9, 9a).** The same one-table argument, with the corrected extractor `E_T^Q` and Lemma QC,
   gives Proposition TE-Q': under C2, (K), H-DS, H-BIND, T-1, [SG26] Theorem I.16 (1) and Lemma QC, the tree's QROM level is
   that of one proof plus negligible terms (A 76.72, B 77.60 bits for the IOP part, hash part 80.40, against 64).
   These are **derived under the recursion heuristic C2, not proven QROM figures**; no unconditional QROM figure exists
   for a tree whose inner proofs are witnesses. The project **claims the lower figures, 69.58 / 70.45** (the per-proof
   union of the calculator), and prints 76.72 / 77.60 beside them.
7. **What a referee should attack first: section 10.**

## 1. Setting and notation

**The tree.** A tree shape `S = (a_s, a_m, d)` (revision 4: sub-bundles of at most `a_s` leaves, merges of arity at
most `a_m`, depth at most `d`; instantiation **16/16/3**, the specification of revision 3.1: at most `2^14` leaves, three
merge levels; instantiation **4/4/5**, `docs/decision-tree-shape.md` as proposed: 4,096 leaves, 1,024 sub-bundles, 341
merges, at most 5,461 published proofs; `MAX_TREE_PROOFS = N = 20,000` bounds the published nodes in both and is
unreachable at 4/4/5, `tree-shape-referee.md` condition 8) and a set `Sigma` of proof systems: the
leaf systems (A's masked leaves, rows 6 and 8, and row 7; B's form-T leaf) and the node systems (A's row 9, B's node).
Every node `v` of a tree of shape `S` has a system `sigma(v)`, a statement `x_v`, and, if it is an internal node, a
list of children. Each system `sigma` is an spBCS argument `(Prv_sigma, Vrf_sigma)` ([SG26] Protocol 6.5) for a
**fixed** relation `R_sigma`:

- a leaf system's relation is its statement circuit (the wallet statement);
- a node system's relation is its node circuit `C_sigma(x, w) = 1`, which evaluates the **concrete** hash functions of
  the transcript (Keccak-256, SHA-256, BLAKE3, SHAKE256) inside the circuit; a witness `w` lists the children
  `ch_sigma(x, w) = ((x_c1, pf_c1), (x_c2, pf_c2), ...)` and the node circuit checks that each child's proof is
  accepted by the in-circuit verifier for that child's statement, that the statements bind (`x` names its children's
  statements or their digests), and the shape.

`R_sigma` does not depend on the random oracle. `[SG26]` Definitions H.3 and H.4 and Theorem 6.6 are for such fixed
relations.

**The oracle.** One random oracle `H` with the four disjoint domain parts of [SG26] Section I.1 (challenge input, leaf,
node, stream), every digest the first `8b` bits of an answer, `b = 32` in both systems (`decision-qrom-counting.md`
7.1). Per system, `k_q,sigma`, `c_sigma`, `n_J,sigma` and `|J_V,sigma|` (verifier messages) are those of [SG26]
Definition I.1, and `c'_sigma = max(2, c_sigma) + n_J,sigma + 1`. Write `c'_max = max_sigma c'_sigma`.

**The adversary.** A `(t, 0)`-adversary `A` of the ROM ([SG26] Definition 6.1, page 53; classical in the ROM): at most
`t` hash queries on every execution path, no proof queries. It outputs a root statement `x_r` and a root proof `pf_r`.

**Compliance.** A **tree of witnesses** for `(x_r, pf_r)` assigns to every node `v` reached from the root through
`ch` a witness `w_v`. It is **compliant** when `(x_v, w_v) in R_sigma(v)` at every node. A compliant tree has, at
every internal node, every listed child accepted by the **in-circuit** verifier (the node relation checks it); that the
**native** verifier against `H` accepts it too is the event C2 of section 2, not a property of compliance.

## 2. Hypotheses

- **(K) Round-by-round knowledge soundness of every system** ([SG26] Definition 2.20): each IOP of `Sigma` is
  round-by-round knowledge sound with an extractor `E_sigma` and errors at most `eps_sigma`; write `eps_max = max_sigma
  eps_sigma`. For the openings this is Theorem S0 (`whir-additive-soundness.md`) and Theorem S (`zk-wi-soundness.md`);
  for every round outside the openings its knowledge form is **owed**: obligations K-A (system A) and K-B (system B),
  `qrom-compilation.md` H3 and T-5. The calculator's `e` of a row is its weakest round's soundness error; this lemma
  needs it as a knowledge error.
- **(H-DS) One oracle, injective encodings across systems.** Every system of `Sigma` compiles with [SG26] Protocol 6.5
  against the one oracle `H` and the same four parts, and the encodings of all systems' oracle inputs together are
  injective; a statement determines its system (each statement carries its system's verifying-key or circuit digest,
  so statements of different systems differ). Then a recorded challenge input decodes, as in [SG26] Protocol I.9 step
  6 (page 138), to `(s, x, i, l_i)` and so to exactly one system `sigma(x)`. [SG26] Section I.1 (page 131) gives this
  within one system: the challenge input is `ch(label || salt(s) || pre(x) || items(i, l_i))` "for a fixed protocol
  label", the statement encoding is prefix-free, and "a challenge input determines (s, x, i, l_i)"; across systems it
  needs distinct protocol labels, or statement encodings that are jointly prefix-free and carry the circuit identifier
  (which [SG26] places in `x`). **To be checked in the transcripts** (an
  addition to task T-1, item 7.6 (g)).

  *What separates systems, as built (revision 3, `qc-and-status-referee.md` T-4; read by the referee by search and
  excerpt, not audited).* **Between A and B**: a different part-tag byte (`0x10..0x13` against `0x20..0x23`), a
  different 16-byte protocol label and different functions (`qrom-compilation.md` 2.2); sufficient. **Within one
  system** the protocol label is the same for every proof system of the tree (A's rows 6 to 9; B's leaf and node), so
  the system `sigma(x)` is determined only by `pre(x)`: for A by the row number and `bind_iv(IV(program))`
  (`qrom-compilation.md` 2.8 A-3; `yugen-proof-a/docs/parameters.md` 2.5), for B by the `StatementId` (circuit name,
  constraint-system digest, mode, row; `qrom-compilation.md` B-1). That suffices **provided the bound IV and the
  constraint-system digest determine the program**, a binding of a concrete digest of the same kind as H-BIND below,
  and it is assumed as part of H-BIND. Nothing in the transcript separates levels or proofs of one system except the
  statement and the salt; [SG26] needs no more, and this lemma uses the level only for termination (section 3).
  Owed in task T-1 item 10: that A's unframed Keccak-256 statement wrappers (rule BC-5) and every other in-relation use
  of Keccak-256 / SHAKE256 cannot produce an oracle input that begins with a part tag.
- **C2, the recursion heuristic, as a named event (revision 2; replaces revision 1's hypothesis H-C2).** Revision 1
  assumed, as hypothesis H-C2, that for every `(x, w) in R_sigma` every child `(x_c, pf_c)` in `ch_sigma(x, w)` is
  accepted by the native verifier **against `H`**. In the ROM that hypothesis is false with probability essentially 1
  (`tree-extraction-referee.md` 1.1: an honest tree whose inner proofs are made with the concrete hash `h` has
  children that the oracle verifier rejects), so a theorem under it is vacuous. Revision 2 states no hypothesis on
  witnesses. Instead:

  > **C2-VIOLATION at `c`.** A child `(x_c, pf_c)` of a node `v` with `(x_v, w_v) in R_sigma(v)` is accepted by the
  > in-circuit verifier (the node relation checks it; for system B the multi-opening verifier `V'` of
  > `lemma-d-duplicate-openings.md` Theorem D) and **rejected** by the native verifier `Vrf_sigma(c)` run against
  > `H` on the extractor's table.

  Theorem TE' bounds the probability that the extraction fails **without** this event; the event itself is outside
  the theorem. C2, "C2-VIOLATION does not occur", is `soundness-method.md` 2.4's recursion heuristic in the one form
  the proof uses. In the deployed system the in-circuit and native verifiers compute the same function, so the event
  is excluded by **in-circuit / native verifier equivalence**, a testable engineering property of the guests; what
  remains heuristic is the usual step, that a bound proved for a random `H` describes the concrete hash, here applied to
  a statement that itself contains the hash. **C2 enters at two places:**
  1. **Child acceptance** (section 6 step (1)): a child is reached only if its native verifier accepted it; without C2
     the extraction may end at C2-VIOLATION, and the theorem then says nothing about that child's subtree.
  2. **Keeping the relation oracle-free** (hypothesis (K) and Lemma TE.1): `R_sigma` is the fixed relation that
     evaluates `h`; it does not read `H`, so the challenge an entry fixes is independent of the relation (Lemma TE.1),
     and an IOP for `R_sigma` with round-by-round knowledge soundness can exist (K). Making the relation read the oracle
     (`R^H`, hash gates as oracle gates) would make the native acceptance hold by definition but would remove both:
     no IOP for `R^H` exists for a random `H`, and the independence in TE.1 fails. So the choice "fixed relation, C2
     as an event" is the only one under which (K) and TE.1 are available, and it is the choice that leaves C2 as a
     heuristic.

  No proof in the ROM can remove C2 (the referee's report, section 1.1, citing the known impossibility and heuristic
  status of recursion in the random-oracle model **from memory only**; none of those papers is in the folder).
- **(H-BIND) Collision resistance of the concrete statement-digest functions** (revision 3, `qc-and-status-referee.md`
  T-1; replaces revision 2's "statement binding, modelled as a further random-oracle part"). The statement digests
  are computed **inside the fixed relation** by the concrete hash: the node statement digest
  `H_bundle-node(depth | mode | LE16(count) | content | attr | LE32(proofs))` of both systems (A:
  `yugen-proof-a/guests/bundle_merge_e2.py`, rules BC-3 to BC-5 of `yugen-proof-a/docs/recursion.md`; B:
  `yugen-proof-b2/src/bundle.rs`), A's bound IV and B's constraint-system digest (H-DS above), and the digests through
  which the chain checks the root statement against the published leaf statements. Section 2's second place of C2
  says the relation does not read the oracle, so these digests **cannot** be a part of `H`; H-BIND is a
  **standard-model** assumption on the concrete functions (SHAKE256 / Keccak-256 at 256-bit output in A, the
  corresponding functions of B), not an oracle property. Define `eps_bind` as the largest probability with which an
  algorithm running `A` together with `E_T` (or `E_T^Q`; Lemma TE.3) outputs two distinct inputs of one of these
  functions with equal outputs. *Revision 5.3 (`te3-referee.md` TE3-1):* **`eps_bind` is defined over the
  primitives**: the largest probability with which such an algorithm outputs **any two distinct inputs** with equal
  output of **Keccak-256**, of **SHAKE256 at 32 bytes on framed inputs** (`SHAKE256("Yg" 00 id || body)[0..32]`), or
  of **SHA-256** (B's `cs_digest`). A collision between inputs that belong to different digest functions over one
  primitive (e.g. a sub statement and a merge statement under Keccak) is therefore counted, and the hash-chain
  argument of Lemma TE.3 does not depend on the layers of the two chains lining up. Keccak-256 (pad 0x01) and
  SHAKE256 (pad 0x1F) are different functions, and no edge compares across them.
  *Revision 5.3 (TE3-4):* H-BIND is collision resistance in its **explicit-reduction** ("human-ignorance") form
  (Rogaway, "Formalizing human ignorance: collision-resistant hashing without the keys", VIETCRYPT 2006; ePrint
  2006/281; **cited from memory, not checked against the paper**): `eps_bind` is the advantage of the specific
  collision finder `B` built from `A` and `E_T`, not an asymptotic property of an unkeyed function.
  *Revision 5.3 (TE3-2), numerically.* Every link of the H-BIND chain is a **32-byte** digest (`H_bundle-node`,
  `Hvar_*`, H_int, `merge_statement`, `cs_digest`); **no H-BIND link is 48 bytes** (the 48-byte note-tree, `rho`
  and `cm` outputs are leaf-statement contents hashed into 32-byte `Hvar` digests). With `q` the hash evaluations
  of `B`, generically (random-function heuristic for the concrete primitive): classically
  `eps_bind <= q(q-1)/2^257`, cost about `2^128`; quantumly `eps_bind = O(q^3/2^256)`, about `2^85.3` queries
  (Brassard, Høyer, Tapp, "Quantum cryptanalysis of hash and claw-free functions", LATIN 1998), tight for random
  functions (Zhandry, "A note on the quantum collision and set equality problems", Quantum Information and
  Computation 15, 2015); without free quantum memory the best known is about `2^(2n/5)` = `2^102` (Chailloux,
  Naya-Plasencia, Schrottenloher, "An efficient quantum collision search algorithm and implications on symmetric
  cryptography", ASIACRYPT 2017). **All three cited from memory, not checked against the papers** (not in the
  folder). NIST prices collisions in classical gates ([CFP] §4.A.5, `call-for-proposals-final-dec-2016.pdf`
  pp. 16-18, in the folder). **`eps_bind` lowers no printed level**: classically `2^128` exceeds 121.89 / 114.74
  (T-e); quantumly the conservative BHT `2^85` exceeds 69.58 / 70.45 (T-g) and 76.72 / 77.60 (T-h).
  *System A note (revision 5.3, `te3-referee.md` section 2):* A's `merge_statement` is **unframed** Keccak-256 of a
  fixed cell count. TE.3 does not need its separation (the primitive definition above counts any collision), but its
  separation from the oracle's part tags is an **open T-1 item** (`what-is-proven.md` queue), not settled here.
  *Revision 3.1 (M-3):* the functions H-BIND covers include, besides `H_bundle-node`,
  **A's `merge_statement`** (`keccak_cells(seeds || D || three deferred claims)`, `yugen-proof-a/guests/
  bundle_merge_e2.py`; a node's public input is this hash, with `D` two layers below it) and **`Hvar_bundle-kids`**
  (the children-digest list hashed into `D`, both systems; B: `framed(id::BUNDLE_NODE, ..)` natively and
  `node_digest` in circuit, `yugen-proof-b2/src/bundle.rs` 96, 298), and the header digest through which
  `Tree::check` reads the root's proof count. The generic attack costs `2^128` evaluations classically at 256 bits; the quantum
  generic cost is of order `2^85` (**from memory**, as the referee marks it; no source in the folder). Revision 2's
  figure `T^2 / 2^(8b + 1)` is **dropped**: it is an oracle bound, and the digests are not oracle outputs. [SG26]
  Section I.1 (page 131, rendered): "Statement digests, such as circuit identifiers, are part of the statement x, and
  the verifier reads them from pre(x) without recomputing them", so they are outside Theorem 6.6 and this term is
  separate (`rev10-referee.md` section 2, note (i)). H-BIND is used twice: to exclude SHAPE-VIOLATION (Lemma TE.3),
  which every tree figure needs, and for the leaf statements' binding to the root (Corollary TE-S).
  *Revision 4 (`b-internal-node-referee.md` condition 3):* for System B's internal nodes, H-BIND also covers
  **`H_int`**, `framed(0xbf, ..)` = SHAKE256(`Yg 00 bf || body`), the commitment
  `E = H_int(tag || LE16(k_I) || cells_1 || cells_2)` (`yugen-proof-b2` `src/bvirt.rs` 80-103) through which a top
  node binds the cells its internal children carry (section 6b); identifier 0xbf is not yet reserved in the spec
  (`b-internal-node-referee.md` C1).

## 3. The tree extractor `E_T` (ROM)

1. Run `A`, answering every hash query by lazy sampling (a fresh uniform answer for a new input, the recorded answer
   for a repeated one). Record the table `db` of inputs and answers.
2. On `A`'s output `(x_r, pf_r)`, run `Vrf_sigma(r)` on it, its queries answered and recorded the same way. If it
   rejects, stop: nothing is claimed.
3. Process the reached nodes in breadth-first order from the root. At node `v`, with the current table `db_v`, run
   the database algorithm of [SG26] Protocol I.9 step 6 for `sigma(v)` (built from `E_sigma(v)`) on the statement
   `x_v` and `db_v`, giving `w_v` or `⊥`. If `w_v = ⊥` or `(x_v, w_v)` is not in `R_sigma(v)`, record **FAIL at `v`**
   and stop. If `v` is internal, for each child `(x_c, pf_c)` in `ch_sigma(v)(x_v, w_v)` run the child's native
   verifier on it (queries answered and recorded); **if it rejects, record C2-VIOLATION at `c` and stop** (revision 2,
   finding F-4); **if queuing `c` would make more than `N + a_m` reached nodes (revision 4; `N + 16` at 16/16/3, `N + 4` at 4/4/5;
for B's internal tree the bound of section 6b replaces it), record SHAPE-VIOLATION at `c` and
   stop**; otherwise queue `c` together with the shape cells (depth, child count, proof count) `w_v` claims for it.
   **Shape check at the child (revision 3.1, `zkq-te3-r8-referee.md` M-3):** when `c` is processed, after `w_c` is
   extracted and `(x_c, w_c) in R_sigma(c)`, compare the cells that `w_c` hashes into `c`'s own statement with those
   its parent claimed; if they differ (depth not lower than the parent's, or child count or proof count different),
   record SHAPE-VIOLATION at `c` and stop. (Revision 3 compared at the parent, which assumed `x_c` exposes its cells;
   it does not: A's public input is the `merge_statement` hash, and B's node words carry `D_c`, not its preimage.)
4. Output the tree of witnesses.

`E_T` ends in exactly one of four outcomes: a compliant tree of witnesses, FAIL at some `v`, C2-VIOLATION at some
`c`, or SHAPE-VIOLATION at some `c`. The extracted child proofs come from the witness the database algorithm extracts
for the parent ([SG26] Protocol I.9 step 6), a deterministic function of the table; the native run of a child's
verifier is a run against the lazily sampled oracle, recorded in the same table.

**Node count and termination (revision 3; stop at `N + 16` since revision 3.1).** Because `E_T` stops before an
`(N + 17)`-th node, it always terminates and always reaches at most `N + 16` nodes (a node is queued before its cells
are checked, and a node queues at most 16 children), so `K = sum_v k_q,sigma(v) <= (N + 16) k_q,max` holds for
**every** run, not only for compliant ones. Against `N = 20,000` this raises `log2 N` by `log2(20,016 / 20,000) =
0.0012` bits; the referee states that it moves no figure, and the rounding of the printed two-decimal figures
against this shift was **not recomputed** here (calculator not run). What the builds provide (`qc-and-status-referee.md` T-1, read by the referee by search and excerpt,
not audited): both systems put the depth, the child count and the proof count in the statement digest
`H_bundle-node(depth | mode | LE16(count) | content | attr | LE32(proofs))`; a merge has depth `1 + max` of its
children's and refuses a child of depth 3 (A: `bundle_merge_e2.py`, rules BC-3, BC-4; B: `src/bundle.rs`,
`depth_bound`, `depth_max`); `proofs = 1 + sum proofs_c`; the bound `MAX_TREE_PROOFS = N` is checked natively on the
root's count (`Tree::check`; rule BC-5), in no circuit. A child's depth and counts are advice in the parent's
circuit, **bound only through the recomputed digest `D_c`**. So the node relation ties an extracted child's cells to
those its parent claimed only through the concrete digest: if the cells agree along every edge, depths strictly
decrease (termination) and the proof counts add up to the root's, which is at most `N` (node count); if they disagree
on an edge, the run ends in SHAPE-VIOLATION, which Lemma TE.3 bounds by a collision of that digest (H-BIND).
*Revision 4:* the stop is at `N + a_m` (a node queues at most `a_m` children): `N + 16` at 16/16/3, **`N + 4`** at
4/4/5, `log2(20,004 / 20,000) = 0.0003` bits. **Depth enters termination only** (`tree-shape-referee.md` condition 5):
it orders the descent; no term of the bound depends on `d`, and a deeper tree adds no C2 application beyond its extra
nodes, each already counted in `K`. Shape
alone (depth 3, arity 16) would allow 69,905 nodes, which is why the proof-count cell matters. This is condition C-4
of the first referee's report: **met by design, by search, not audited** (an audit owed: both node circuits, the
native `Tree::check`, and, for B, that the consensus constraint-system digest is that of the all-on rule set, since
`depth_bound` and `depth_max` have "off" switches for negative tests (`qc-and-status-referee.md` T-5), pinned in a
test; task T-1, item 7.6 (g) of `decision-qrom-counting.md`).

`E_T` is straight-line (no rewinding), never reprograms the oracle, and changes nothing `A` sees: its answers to `A`
are lazy sampling, so `A`'s view, output and auxiliary output are distributed exactly as against a uniform `H` (oracle
simulation error 0, as [SG26] Theorem I.16 (2), page 143: "Lazy sampling gives the distribution of a uniform
oracle"). In the ROM the database algorithm of step 3 is exactly the extractor of [SG26] Theorem I.16 (2): "The
extractor answers the queries of the adversary and the verifier by lazy sampling and applies the database algorithm of
Protocol I.9, built from E, to the table of these queries and answers" (page 142). Since `E_T` reaches at most `N`
nodes on every run (above), the table has at most `T = t + K` entries, `K = sum_v k_q,sigma(v)` over the reached
nodes, at most `N k_q,max`.

## 4. Lemma TE.1 (the joint bad set and its instability)

*Provenance: **Adapted** from [SG26] Lemma I.12 (page 140). Changes: (i) several proof systems share the oracle and
the table; the knowledge-failure clause ranges over all of them, each with its own state function, extractor and
relation; (ii) the instability is bounded per added entry by the error of the one system whose challenge that entry
fixes, not by one common `eps^k`. The proof is [SG26]'s with these two changes.*

**Definition.** `B*` is the set of tables `db` with a **digest collision** (two distinct recorded inputs whose answers
have the same digest) or a **knowledge failure**: some recorded challenge input, decoding to `(s, x, i, l_i)` with
`sigma = sigma(x)`, encodes a past whose transcript `tr` the database algorithm of `sigma` reconstructs from `db`, and
`State_sigma(x, i, tr) = 0`, `State_sigma(x, i, tr || theta_i) = 1` for the recorded challenge `theta_i`, and
`(x, E_sigma(x, tr))` is not in `R_sigma` ([SG26] Definition 2.20 for `sigma`).

**Lemma TE.1 (two-sided instability; revision 2, finding F-2).** The empty table is not in `B*`, and for every table
`db` with fewer than `T` entries and every input `u` not in `db`, the probability over a uniform answer `y` that adding
the entry `(u, y)` **changes whether the table is in `B*`** is at most

    c'_max T / 2^(8b) + eps(u, db),

where `eps(u, db) = eps_sigma(x)` if `u` is a stream point `stream(v, s)` whose key `v` is the digest of the answer to a
recorded challenge input of statement `x`, and `eps(u, db) = 0` otherwise.

This is the form [SG26] Lemma I.12 (page 140) states: "the probability over a uniform answer y that adding the entry
changes whether the database is in B", that is, the instability `I(B, T)` of [CMS19] Definitions 5.4 and 5.6.
Revision 1 claimed in addition that `B*` is **monotone**; that is **false as written** (referee F-2): [SG26] Protocol
I.9 step 6 (page 138) leaves a missing or ambiguous preimage undefined and decodes it to the default, so a later entry
that supplies a **missing first** preimage of a digest carried by a recorded input changes a reconstructed transcript
with no collision, and a knowledge failure may disappear. Such an entry lies in the event `F` below, which is all the
two-sided form needs.

*Proof.* The empty table has no collision and no recorded challenge input. Fix `db` and `u`.

Let `F` be the event that `dg(y)` equals the digest of a recorded answer of `db`, a digest of an item a recorded input
carries, or a final digest a recorded input carries for a merged branch. A recorded input of system `sigma` carries at
most `max(2, c_sigma)` digests of items (counting a stream point's key and a node's two child digests) and at most
`n_J,sigma` final digests ([SG26]'s count, per system), so at most `c'_max - 1` digests, and `db` has fewer than `T`
recorded answers: `Pr[F] <= c'_max T / 2^(8b)`.

Outside `F` the new entry creates no digest collision and no recorded input contains `dg(y)`, so it changes no
transcript, leaf or challenge that the database algorithm of any system already reconstructs from `db` ([SG26]'s
argument verbatim: the entries such a reconstruction uses are in `db` and `u` is not, and outside `F` the entry gives no
first or second preimage of a digest a recorded input carries). It remains to bound, outside `F`, the probability that
`db` and `db + {(u, y)}` differ in membership. **If `db` is in `B*`**, so is the extension outside `F`: a digest
collision of `db` is one of the extension, and a knowledge failure of `db` is one of the extension, since outside `F`
the entry changes no reconstructed transcript or challenge. **If `db` is not in `B*`**, then outside `F` the extension
is in `B*` only through a new knowledge failure at a transcript the entry extends at its end. If `u` is a challenge input, a leaf or a node, it extends no
reconstructed transcript, and a new challenge input completes no round since no stream point at its key is recorded.
Let `u = stream(v, s)`. Since `db` has no digest collision, the key `v` is the digest of at most one recorded answer;
if it is the answer to a challenge input, that input decodes (H-DS) to one `(s, x, i, l_i)`, one statement `x` of one
system `sigma(x)`, and the entry fixes the challenge `theta_i = sample_i(y)` at one reconstructed past `tr`. By the
write-back no recorded input contains `dg(y)`, so the entry completes no later round. Hence the extension is in `B*`
only if `State_sigma(x, i, tr) = 0`, `State_sigma(x, i, tr || theta_i) = 1` and `(x, E_sigma(x, tr))` is not in
`R_sigma`; conditional on sampler success `theta_i` is uniform on `C_i` and independent of `tr`, `x` and `R_sigma`
(which is fixed), so by Definition 2.20 for `sigma` this has probability at most `eps_sigma(x)`; a sampler failure
fixes no challenge. If the key is the digest of no recorded challenge-input answer, the entry fixes no challenge and
`eps(u, db) = 0`. In both cases membership changes with probability at most `Pr[F] + eps(u, db)`. ∎

The place where "`R_sigma` is fixed" is used is the independence of `theta_i` from the relation; this is the second
place C2 enters (section 2): the relation is kept oracle-free, and the native / in-circuit gap is left to the event
C2-VIOLATION, rather than making the relation depend on `H`.

## 5. Lemma TE.2 (extraction at one node)

*Provenance: **Published**, [SG26] Lemma I.14 (page 141), applied per node with `B*` in place of `B`; for system B's
in-circuit verifier `V'`, step 5 of Theorem D of `lemma-d-duplicate-openings.md` (Adapted, refereed: pass with
conditions) in its place.*

Let `v` be a node and `db` a table that contains the queries of a run of `Vrf_sigma(v)` on `(x_v, pf_v)` that accepts,
with the answers that run read. Then the database algorithm of `sigma(v)` outputs a witness for `x_v` from `db`, or
`db` is in `B*`.

*Proof.* [SG26]'s proof of Lemma I.14 with `Q = 0` (no proof queries, so no assigned points and "x is fresh" holds):
since `db` has no digest collision, every leaf the proof opens is the reconstructed leaf, the reconstructions of each
past agree, the IOP verifier of `sigma(v)` accepts the reconstructed transcript `tr`, and either `E_sigma(v)(x_v,
tr|past(i))` is a witness for some `i`, or by condition (a) of Definition 2.20 some `i` in `J_V` has `State(x_v, i,
tr|past(i)) = 0` and `State(x_v, i, tr|past(i) ∪ {i}) = 1`, a knowledge failure of `db` at the verifier's challenge
input for `i`, so `db` is in `B*`. The proof reads only the entries of `db` that the verifier's run and the
reconstruction use; entries for other statements, other systems or other nodes do not enter it, except through a
digest collision, which puts `db` in `B*`. The base-game condition "the verifier accepts with all its queries among
the appended ones, answered as recorded" ([SG26] Definition I.13) holds because the run was answered from `db`. ∎

## 6. Theorem TE' (knowledge soundness of the tree up to the event C2-VIOLATION, ROM)

*Provenance: **Original (the Ycash developers, 2026)**, adapting the proof of [SG26] Theorem I.16 (2) (pages 142, 143)
from one proof to a tree of proofs on one table. Related: [SG26] Theorem I.17 (page 144), whose ROM extractor also
"uses the table of the execution's hash queries" with further appended queries counted in `T`. The statement in this
form is the referee's (`tree-extraction-referee.md` 1.1, condition C-1); revision 1's Theorem TE "under H-C2" is
withdrawn (section 2).*

**Theorem TE'.** Under (K) and H-DS, for every `t` and every `(t, 0)`-adversary `A` of the ROM, with `E_T` as in
section 3 (including the stops at C2-VIOLATION and SHAPE-VIOLATION),

    Pr[ Vrf_r accepts (x_r, pf_r)  and  E_T ends with neither a compliant tree of witnesses, nor a C2-VIOLATION,
                                        nor a SHAPE-VIOLATION ]
        =  Pr[ Vrf_r accepts (x_r, pf_r)  and  E_T records FAIL ]
        <=  t eps_max  +  sum_v |J_V,sigma(v)| eps_sigma(v)  +  c'_max (t + K)^2 / 2^(8b),

the sum over the nodes `E_T` reaches (at most `N + 16` on every run since revision 3.1, section 3), `K = sum_v k_q,sigma(v) <= (N + 16) k_q,max` (the `N k_q,max` figures below shift by 0.0012 bits in `log2`).
`E_T` has oracle simulation error 0. No hypothesis on witnesses is made; C2 is not used; H-BIND is not used (it
enters through Lemma TE.3).

**Lemma TE.3 (SHAPE-VIOLATION is a digest collision; revision 3, `qc-and-status-referee.md` T-1).** Assume the node
relations check the shape as section 3 describes (condition C-4; met by design, by search, not audited), and
**H-DS** holds in the form the tree uses: **the parent fixes the child's program and key** (the verifier, seed and
statement function the child is verified under; for B also `auth_mode` and the kind, circuit constants bound by the
pinned key; revision 5.3, `te3-referee.md` TE3-3). Then

    Pr[ Vrf_r accepts (x_r, pf_r)  and  E_T records SHAPE-VIOLATION ]  <=  eps_bind,

with `eps_bind` the collision-finding advantage of H-BIND against the concrete statement-digest functions, for the
collision finder `B` that runs `A` and `E_T`, answering every oracle query itself by lazy sampling (no oracle access
is needed: `B` simulates `H` exactly), and evaluates the concrete digest functions directly. *Proof.* Suppose `E_T`
records SHAPE-VIOLATION at `c`, child of `v`. (a) *(Revision 3.1, M-3.)* If the cells `w_c` hashes into `c`'s
statement differ from those `w_v` claimed, then `(x_v, w_v) in R_sigma(v)` and `(x_c, w_c) in R_sigma(c)` (no FAIL
at either). The parent's relation recomputes the child's statement from the claimed cells (`D_c = H_bundle-node(..)`,
then for A `merge_statement`; and the parent's own `Hvar_bundle-kids` over the children's digests); the child's
relation computes its public input from the cells in `w_c` by the same chain. Both chains end in the public input
`x_c` names, and their first inputs differ, so at the first layer at which the inputs differ the outputs are equal:
a collision of `H_bundle-node`, of `merge_statement`'s Keccak (A) or of `Hvar_bundle-kids`, all computed by `B`
(hash-chain argument; H-BIND as listed in section 2). No new assumption. *Caveat (revision 5.3, TE3-3):* "the cells
`w_c` hashes" are the relation's encoded bytes; where B's `Stream::piece` hashes encoded bytes without
range-checking the cell values (section 6b), (a) holds for the encoded cells, and a gap between encoding and value
is a C-4 failure, not a collision. (b) If queuing `c` would reach an `(N + 1)`-th node with the cells
agreeing on every edge so far, then every reached node's proof count is `1 + sum` of its children's (the node
relation, C-4) and the root's is at most `N` (checked natively, `Tree::check`), so at most `N` nodes are reachable
along agreeing edges, and with the at most 16 queued but unchecked children at most `N + 16`; hence (b) does not
occur without (a) on some edge. *(Revision 3.1.)* The root's count is read by `Tree::check` from the header the chain
holds, a third preimage of the root's digest; if it differs from the count the root's witness hashes, that is the
same kind of collision. ∎

*Exits that are not collisions (revision 5.3, TE3-3).* A disagreement between the extracted tree and the published
statement that is not a collision counted in `eps_bind` is one of: **FAIL** (extraction fails, Theorem TE');
**C2-VIOLATION** (an inner proof rejected natively); a **C-4 failure** (a relation does not recompute or
range-check a cell; unaudited, cf. A's `count_le` mutation, `yugen-proof-a/docs/recursion.md` 691, and the
`Stream::piece` caveat); an **H-DS failure** (a child verified under a foreign program or key). TE.3 bounds only
the collision case, under C-4 and H-DS.

*Note N-3 (revision 3.1, `zkq-te3-r8-referee.md` N-3).* In A, `bind_iv` (`vendor/leanMultisig/crates/verifier/src/
params.rs` 460) is `Keccak("leanvm-params-v1" || program IV || descriptor())`, but row 0's descriptor returns the
program IV unbound, so H-DS for a node under row 0 would rest on the program IV alone (the row's parameters not
bound). **It does not matter as built**: the tree's programs run on rows 6 to 9, whose descriptors bind every field
(including `leaf_salt_words` and the query table); no tree node uses row 0. **Fix (buildable):** make row 0's
descriptor bind its fields like every other row (or refuse row 0 in any program the tree accepts), with a test that
for every row a change of any parameter field changes `bind_iv`. The same `B` serves in the QROM (with
`E_T^Q` and the compressed oracle simulated by `B`; section 9), with `eps_bind` then the quantum collision-finding
advantage.

**How to read "conditional on C2"** (revision 3, `qc-and-status-referee.md` T-2). Theorem TE' and Lemma TE.3 are
true statements about **joint** probabilities: together,

    Pr[ accepted, and no compliant tree ]
        <=  (the bound of Theorem TE')  +  eps_bind  +  Pr[ accepted and C2-VIOLATION ].

The last term is bounded by nothing, and in the model it is **not** small: for the **honest** tree (inner proofs made
with the concrete hash `h`, the root checked against `H`) it is essentially 1. So "conditional on C2" is never a
conditional probability (the conditioning event can have probability near 0); every tree statement is displayed as
`Pr[bad outcome and no C2-VIOLATION] <= ...`. A reader **may** conclude: the root proof alone is knowledge sound;
every way of cheating that does not pass through a child the native verifier rejects is bounded; the tree is sound to
the stated level if the event C2-VIOLATION is empty, which in the deployed system (`H` is the concrete hash) is
in-circuit / native verifier equivalence. A reader **may not** conclude: that a random-oracle proof of the recursion
tree exists with a small gap; that `Pr[C2-VIOLATION]` is small in the model; or that passing in-circuit / native
equivalence tests **discharges** C2 (the tests make the event empty in the deployed system, where there is no
theorem, not in the model, where the theorem is).

*Proof.* **(1) A FAIL lies in `B*` at the step it is recorded.** Suppose `E_T` records FAIL at node `v` with table
`db_v`. Then `Vrf_sigma(v)` accepted `(x_v, pf_v)` with its queries recorded in `db_v`: for the root by step 2; for any
other node, its parent was processed without FAIL and `E_T` ran the child's native verifier in step 3 on the lazily
sampled oracle, whose answers are the oracle's, and recorded them; the verifier accepted, since otherwise `E_T` would
have stopped with C2-VIOLATION before queuing `v`. By Lemma TE.2 the database algorithm outputs a witness for `x_v` from
`db_v`, or `db_v` is in `B*`. Step 3 records FAIL only when no witness is output, so `db_v` is in `B*`. (Revision 1
concluded "so is the final table" by monotonicity; that step is withdrawn, F-2. Nothing below needs it.)

**(2) The table is in `B*` at some step with probability at most the bound.** The table is built one entry at a time,
`db_0` empty, `db_j = db_(j-1) + {(u_j, y_j)}`; each new input `u_j` is chosen (by `A` or by `E_T`) as a function of
the answers before it, and its answer `y_j` is uniform and independent of them. Since the empty table is not in `B*`,
the table is in `B*` at some step only if some entry moves it from outside `B*` into it, so

    Pr[ exists j: db_j in B* ]  <=  sum_j Pr[ db_(j-1) not in B*,  db_j in B* ]
                                <=  sum_j E[ c'_max T / 2^(8b) + eps(u_j, db_(j-1)) ],    T = t + K,

each term by Lemma TE.1 (the two-sided bound covers the one direction used) and taken on the event that
`db_(j-1)` is not in `B*`. The first parts sum to at most `T c'_max T / 2^(8b)`. For the second: at most `t` entries
are `A`'s, each with `eps(u_j, db_(j-1)) <= eps_max`. The others are verifier queries of the reached nodes. A query of
`Vrf_sigma(v)` on a stream point has as key the digest of the answer to `v`'s own challenge input (the verifier computes
it from that answer), and since `db_(j-1)` is not in `B*` that key is the digest of no other recorded answer, so
`eps(u_j, db_(j-1)) = eps_sigma(v)`; non-stream queries contribute 0; and `Vrf_sigma(v)` makes at most `|J_V,sigma(v)|`
stream queries (one a verifier message, [SG26] Definition I.1; the count of stream queries was **not re-read** for
revision 2, referee 1.2). Summing gives the bound. Two points of the union bound carried over from [SG26] (page 143):
it holds for each choice of the adversary's coins, which are independent of `H`, and stopping an execution before its
`j`-th query is handled as there ([CMS19] footnote 6, page 22, as [SG26] cites it). That `E_T`'s own inputs depend
adaptively on the table (through the extracted witnesses) changes nothing: the bound of Lemma TE.1 holds for every
table and every new input.

**(3) Conclusion.** By (1), a FAIL implies `db_j in B*` for the step `j` at which it is recorded; (2) bounds the
probability of that. A run that ends with C2-VIOLATION or SHAPE-VIOLATION is not counted (Lemma TE.3 bounds the
second). The oracle simulation error is 0 (section 3). ∎

**Corollary TE-X (the explicit tree; no C2).** If every proof of the tree is published with its
statement and verified natively, run `E_T` with step 3 taking each child from the published record instead of from
the witness; every child's native verifier is then part of the verification, so C2-VIOLATION cannot occur. Under (K)
and H-DS, with the same table and the same `t`, `Pr[every published proof accepted and E_T records FAIL]` is at most
the bound of Theorem TE', and SHAPE-VIOLATION is bounded by `eps_bind` (Lemma TE.3). *Proof:* Theorem TE' with step 3
changed as stated; step (1) uses the published acceptance in place of the native run. ∎ This is the rigorous core
(referee 1.1, "What is unconditional"). It does not describe the chain, which publishes the root proof only.
**What it says** (`qc-and-status-referee.md` T-3 (a)): its content is knowledge soundness of a **batch** of published
proofs extracted from one table; the children an extracted node witness lists are concrete-hash proofs, are not the
published ones and are not used, so "tree" adds only the statement binding, which is H-BIND again. Its quantum form is
Corollary TE-X-Q (section 9).

**What is unconditional, and what is conditional.**

| Statement | Status |
|---|---|
| The root proof alone ([SG26] Theorem 6.6 (2), Theorem I.16 (2)) | proven in the ROM, given (K) for the root's system, H-DS, MA-1 / MA-2' (the hashes modelled as the oracle) and [SG26] (a preprint) |
| A tree whose every proof is published and verified natively (Corollary TE-X) | proven in the ROM under the same conditions plus H-BIND (Lemma TE.3) and C-4 as built; no C2 |
| A recursion tree whose inner proofs are witnesses (the chain's tree): its leaf statements are true, and every tree figure of section 7 | **conditional on C2**, read as the joint probability `Pr[bad and no C2-VIOLATION]`, in addition to the above; Theorem TE' and Lemma TE.3 bound everything else |

Until K-A and K-B are discharged, every row of this table is **conditional** in the sense of `what-is-proven.md`: the
implication is proven, its hypothesis (K) is owed for every round outside the openings.

## 6b. Revision 4/5: shape 4/4/5, System B's internal nodes and the carried-claim fold (revision 5: draft, unrefereed)

*Provenance: **Original (the Ycash developers, 2026)**. The node bound and the (kind, depth) order are
`b-internal-node-referee.md` section 5's; the fold construction is `yugen-proof-b2` `docs/parameters.md` section 24
(stacked wiring polynomial; batching sumcheck as that repository's `src/batch.rs` cites it; stacking called folklore
there, no paper read). The batching error is the Schwartz-Zippel bound for a batched sumcheck over the build's
challenge field, taken from that construction, not re-derived from a paper here. Revision 5 applies
`tree-extraction-rev4-referee.md` (`f32848e`) conditions R4-1 to R4-8. Code read for revision 5: `yugen-proof-b2`
`wt/s045` branch `agg` @ `f231a31`. Papers: the quantum form in (c) uses the quadratic query loss of round-by-round
soundness in the QROM from [CMS19] (A. Chiesa, P. Manohar, N. Spooner, "Succinct arguments in the quantum random oracle
model", ePrint 2019/834), as this lemma already cites it; the exact theorem and its constant were **not re-read** for
revision 5.*

**(a) Shape.** Parametric: `E_T` stops at `N + a_m`, so every bound of section 6 holds with
`K <= (N + a_m) k_q,max`. 16/16/3: `N + 16 = 20,016`; 4/4/5: `N + 4 = 20,004` (A's published nodes). Depth `d`
bounds the descent only. **Which shape is specified (R4-7).** Specification 0.4.7 section 15 is **16/16/3** (arity 16,
depth at most 3, `MAX_TREE_PROOFS` 20,000). **4/4/5 is a proposal** (`docs/decision-tree-shape.md`), not in the
specification: everything below that is stated at 4/4/5, and all of (b) and (c) (B's internal form and fold exist
only at 4/4/5), applies to B's built tree only once the specification adopts 4/4/5. System A at 16/16/3 stands as
revision 3.1 states it.

**(b) System B's internal nodes** (`design-b-aggregation.md`; `b-aggregation-referee.md` condition 2). B proves each
published merge (arity at most 4) as one **top** node over at most two **internal** arity-2 nodes, and each virtual
sub-bundle as one **top-0** over at most two **internal-0** nodes. Kinds and keys: K0 (published, level 0), KM
(published merge), KI (internal), KI0 (internal-0; `b-internal-node-referee.md` condition 4). Internal slots accept
only published kinds, top slots only internal kinds: no internal-over-internal chain.
- *Node bound*, by shape and kind (not by the `proofs` cell, which does not count internal nodes):
  `N_B <= L + 3 S + 3 M` for `L` leaves, `S` sub-bundles, `M` merges; at 4/4/5, `4,096 + 3 x 1,024 + 3 x 341 =`
  **8,191** (an upper bound; `k < 3` drops the right internal node). B's stop is at `N_B + 2` (a B node queues at
  most 2 children): **8,193** at 4/4/5, and `K <= (N_B + 2) k_q,max^B`. **The theorem's node count for B at 4/4/5 is
  8,193 (R4-2)**: a soundness bound ranges over every tree the circuits accept, and the stop is what `E_T` enforces.
  `yugen-proof-b2` `docs/parameters.md` 24.4 (3)'s 1,516 (`N + 16` with `N = 1,500`, the critical-path block of 21.4)
  is a **per-block illustration**, not this theorem's term (the amendment of 24.4 (3) is owed in that repository). At
  16/16/3 the internal form is neither specified nor built and B's stop stays `N + 16`.
- *Line citations in this section are to `yugen-proof-b2` branch `agg` at commit `13e0e9d` unless another commit is named (revision 5.2, R51-3).*
- *Termination*: well-founded on **(published depth, kind)** with, at one published depth, top above internal above
  published-of-lower-depth, i.e. the order (kind, depth) of `b-internal-node-referee.md`. It needs the kind fixed
  by the key words. **Built (R4-5; internal-node condition 5):**
  - `src/node.rs::uniform_head` (lines 967 to 1009): for every child, the kind word `f` gives four indicators that are
    asserted one-hot; a top node accepts only kind 2, a top-0 only kind 3, every other node refuses 2 and 3; `K0` and
    `KI0` of the child are asserted equal to the node's for every kind, `KM` and `KI` for kinds 1 and 2; the
    exported flag `fW` is fixed by the kind (`1 + [f = 3]` complement; `[f = 1]` in `Merge`).
  - **The slot's kind subcircuit binds `f` to the key the child is verified under** (checked for revision 5):
    `src/uroot.rs::record_for` (lines 70 to 110) puts the four words of the child's statement-identifier key digest
    on wires (`StatementPart::Le64(digest[i])`, the identifier the recorded verifier hashes) and calls
    `kind_choice_for` (lines 39 to 47), which calls `src/bvirt.rs::slot_kind` (lines 60 to 84): `Published` asserts
    `f` in {0, 1} and the identifier's key equal to the child's `KM` (`f = 1`) or `K0` (`f = 0`); `Internal` asserts
    `f = 2` and the key equal to `KI`; `Internal0` asserts `f = 3` and the key equal to `KI0`. With `uniform_head`'s
    equalities, the key a child proof verifies under is the node's own `K0`/`KM`/`KI`/`KI0` selected by `f`.
  - `src/uroot.rs::check_root` (lines 165 to 191) compares all four keys `K0`, `KM`, `KI`, `KI0` with the `RootRule`
    constants. Tests: `yugen-proof-b2` `docs/parameters.md` sections 22, 23, 24.4 (6) (the foreign-`KI` refusal and
    the kind refusals); not re-run for this revision.
  So the kind is fixed by the pinned keys and the bound holds as built (at 4/4/5).
- *Cells through `E`.* A top node binds its internal children's cells only through `E = H_int(..)`. The extractor
  gets the cells from the top's witness and from the internal proof's witness, both preimages of the same `E`;
  distinct cells give an **H_int collision**. Lemma TE.3 (a) extends by one layer of the hash chain: SHAPE-VIOLATION
  on an internal edge is a collision of H_int, `H_bundle-node` or `Hvar_bundle-kids`. Bound unchanged: `eps_bind`,
  with H_int listed (section 2). Caveat (`b-internal-node-referee.md` section 1): `Stream::piece` binds encoded
  bytes, not wire values; harmless while the range checks stand.

**(c) The carried-claim fold** (`b-fold-referee.md` condition 4; restated in revision 5 per R4-1, R4-4). A B node no
longer discharges its children's wiring claims: it batches them with its own into one claim `W*(r', s') = v'` that it
carries; the final verifier discharges that one claim at the root as `sum_k eq(s', k) W_k(r')`
(`uroot::check_root`, `fold::evaluate`). Since commit `cc6a794` `check_root` has two evaluator paths (`src/uroot.rs`
lines 191 to 194 at `8d1517f`): with `RootRule::folded_wiring` set, the folded claim is evaluated by
`phased::Stacked` (each distinct term table read once, a single weight required); otherwise by `fold::holds` /
`fold::evaluate` as before. Both compute `sum_k eq(s', k) W_k(r')`; the statements below hold for either (R51-2).

*The node relation is unchanged.* Revision 4 amended it to "accepts **and** the carried claim is true"; that is
withdrawn (R4-1): K-B extracts for the verifier's relation, and "claim true" is a statement about a public polynomial,
not a witness property the IOP proves. The theorem for B runs in **two passes**:

- **Pass 1 (extraction).** `E_T` runs exactly as in section 3 under the oracle-free relation "the node verifier
  accepts", so Theorem TE' and K-B apply **unchanged**: except with the bound of Theorem TE' (and the batching term
  of pass 2 below, which sits beside it), `E_T` ends with a compliant tree of witnesses, C2-VIOLATION or
  SHAPE-VIOLATION. A false child claim does not stop extraction: the in-circuit step never refuses one (a cheating
  prover sets `s_o` to the running claim; `b-fold-referee.md` section 4).
- **Pass 2 (truth of the carried claims, top-down).** On the event "`Vrf_r` accepts, the root discharge holds and
  pass 1 ended compliant", every reached node's carried claim is true except with the batching term below. From the
  root down: the root's carried claim is true (the discharge); a node's carried claim is the batch of its own claim and
  its children's carried claims; if some input to that batch is false and the output is true, the batching step has
  mapped a false claim to a true one. Induction over the extracted tree.
- **What a claim is about.** Every carried claim is about **one fixed polynomial** `W* = sum_k eq(s, k) W_k` of the
  four wiring polynomials the **four keys pinned at the root** determine (`check_root`), under the common padding rule
  (parameters 24.4 condition 1, built). So a claim's truth does not depend on which subtree it came from; mixing claims
  across subtrees is harmless, and the only attack is a false claim batched into a true one, which is the term below.
- **Binding of a child's claim.** Each child's `W*` claim and `fW` are public words of the child's statement (head
  word 20), linked into the parent's slot and bound into the parent's transcript before its first challenge
  (`src/node.rs::batch_parallel`, line 455: `bind` of every slot element; `src/pbatch.rs::run`: `bind` precedes the
  first `sample`, line 269), and the extracted child witness carries the same public words.

*The batching term, in Fiat-Shamir form (R4-4).* The fold's challenges are Fiat-Shamir outputs computed by the node
prover (the in-node transcript is the prover's witness, parameters 24.2), so an adversary may retry a node's witness
and rehash; each oracle query is a fresh chance. The term is therefore **per query**, not a sum over reached nodes:

    Theorem TE' for B:  t eps_max  +  (t + K) eps_batch,max  +  (the remaining terms of Theorem TE')

`eps_batch,max = (m - 1 + 2 (n + 2)) / |F_c|` with the **built constants (R4-6)** `m = 4` claims a batch and
`n + 2 = 74` stacked variables (`n_wiring` 72 at pad 24,22,25, parameters 24.4): **151 / |F_c|**. The term sits
**beside `t eps_max`, outside `k_q`**: it is not a query of a published verifier. B's re-certified `k_q` is
**40,568** (margin +0.7786; it counts the fold's 152 transcript elements conservatively and nothing else).
Revision 4's "statistical" label is withdrawn; its `sum_v eps_batch,v` (about `2^-107.8` over 8,193 nodes at
`GF(2^128)`) is replaced by the per-query form. **Revision 4's `2^-106.5` at 20,016 nodes is dropped (R4-3)**: no
B instance with a fold exists at 16/16/3, built or specified.

*The challenge field, per build (read from code).* The fold's challenges are drawn by `pbatch::run` through
`IPVerifierChannel<B128>` (`src/node.rs` line 455; `src/pbatch.rs` lines 227, 269). `B128` is
`binius_verifier::config::B128 = ChallengeField` (`vendor/binius64/crates/verifier/src/config.rs` line 14), and
`ChallengeField` is `GhashSq256b` under the feature `challenge256`, `Ghash128b` otherwise
(`vendor/binius64/crates/field/src/arch/arch_optimal.rs` lines 34 to 38; `CHALLENGE_WORDS` 4 or 2, line 88). The crate
feature `cat1` turns `challenge256` on and `cat1t` implies `cat1` (`Cargo.toml` lines 58, 61; `default =
["recursion"]`, line 46). So the fold is drawn in the build's challenge field:

| Build | Challenge field | `eps_batch,max` | Classical cap (per query, `t + K ~ t`) | Quantum cap: **order only (classical cap halved; constant not stated)**, `(t + K)^2 eps_batch` form |
|---|---|---|---|---|
| default (`recursion`; the pin's row, 96-bit rows): **not constructible, the fold is refused (R5-1)** | `GF(2^128)` (`Ghash128b`) | `151 / 2^128 = 2^-120.76` | 120.76 bits (the reason for the refusal) | about 60.4 bits (the reason for the refusal) |
| `cat1t,blake3` (category 1, form T) | `GF(2^256)` (`GhashSq256b`, `ghash128[Y]/(Y^2+X*Y+X)`) | `151 / 2^256 = 2^-248.76` | 248.76 bits | 124.38 bits |

(`K <= 8,193 x 40,568 = 2^28.31`, negligible beside any `t` at these levels.) *Quantum column (revision 5.1,
R5-2):* order only, the classical cap halved; the constant of the grinding bound is not stated and [CMS19] was not
re-read for it. The `cat1t` conclusion does not depend on the constant (124 bits against a 64-bit target).

*Against the stated bounds* (`what-is-proven.md`: classical 114.74 bits a 20,000-proof tree, 121.89 under TE';
quantum 69.58 (A) / 70.45 (B) against 64). The fold is B's only; A's figures are untouched.
- **`cat1t,blake3`: no stated bound drops.** The term is below `2^-248` a query.
- **Default build: not constructible (revision 5.1, R5-1).** `yugen-proof-b2` branch `agg`, commit `0613c6c`, adds
  `src/fold.rs::require_challenge256`, which fails unless the crate feature `challenge256` is on; it is enforced in
  `build_uniform` (`src/node.rs` line 578, a uniform node is not built) and in `uroot::check_root` (`src/uroot.rs`
  line 166 at `13e0e9d`, line 170 at `8d1517f`; the root check refuses), with `tests/fold_field.rs`. So no B tree with a fold exists in a
  `GF(2^128)`-challenge build, and no bound of that build is stated. The figures it would have had (classical cap
  120.76 bits, 120.22 under TE' against 121.89; quantum cap about 60.4 bits, below the 64 target) are kept only as
  the reason for the refusal.

*Selector.* Boolean and one-hot, flag fixed by the kind rules (0 only for an internal-0 child; `b-fold-referee.md`
conditions 2, 6; `uniform_head`, above): a non-Boolean selector would let a claim enter under a mixture of kinds,
outside this analysis.

**(d) New C2 equivalence obligations.** C2-VIOLATION (section 2) now ranges over B's new in-circuit verifiers, each
owing in-circuit / native equivalence: the **internal** node, the **top** node, the **internal-0** node, the
**top-0** node, and the fold's **in-circuit batching verifier** (the `pbatch` step with the stacked `W*` group and
the selector from kind indicators). **Added in revision 5 (R4-8):** the **root discharge** (`uroot::check_root`, by either evaluator: `fold::evaluate` or, since `cc6a794`,
`phased::Stacked` through `RootRule::folded_wiring`; both owe the test, R51-2) is native-only and part of the verifier, so it owes a test that it equals
`sum_k eq(s', k) W_k(r')` for the deployed keys; that random-point check exists in `vfinal` (`examples/recbench.rs` lines 2459 to 2470, `assert_eq!` of the stacked
shape against `fold::evaluate`). **Revision 5.1 (R5-4): run.** System B worktree `yugen-proof-b2/wt/s045` (`agg`,
`13e0e9d`), `bench/v-tree-20261120-s.sh`, chain data `target/v4` (keys `slot`, pad 23,22,24, `n = k = 2`): log
`target/logs/v-tree-pad23-chain4.log` (2026-11-20 01:25, sha256 `5f030d66...65528`) line 104, `VFINAL W* = sum_k
eq(s, k) W_k at a random point; 81052349 terms in four shapes`, followed by the root verified (line 105) and the
refusals (line 106); the same check also passed in `v-tree-pad23-chain.log` and `-chain3.log`. Caveats: the log sits
under `target/` and is not versioned; the point is drawn from a fixed seed (`StdRng` seed 24), one point, so this is a
test of the identity, not a proof; `yugen-proof-b2` `parameters.md` section 25 is the record that cites it. **Versioned records (revision 5.2, R51-1):**
`bench/results/v-tree-pad23-chain4-vfinal.txt` (commit `99f646a`; the lines above, the log's sha256 and the run
parameters) and `bench/results/v-tree-vfinal-20261120T0947Z.txt` (commit `8d1517f`, run at `cc6a794`; it also shows
the stacked evaluator equal to the discharge at the same point).
A's guests are unchanged.

**Summary of the change.** Stop `N + a_m` (`N + 4` at 4/4/5, a proposal; 16/16/3 is the specification); B's sums over
at most `N_B + 2 = 8,193` nodes at 4/4/5; for B, two passes (extraction under "accepts", then truth of the carried
claims from the root discharge down) and the per-query term `(t + K) eps_batch,max` with `eps_batch,max = 151 / |F_c|`,
negligible at the 256-bit challenge field; the `GF(2^128)` build refuses the fold (revision 5.1);
H-BIND adds H_int; internal-node condition 5 built; six C2 obligations (five guests and the root discharge). Section
7's figures are not recomputed.

## 7. Corollaries: soundness of the tree and the figures

**Corollary TE-S (soundness of the tree).** Let the chain accept a root proof for `x_r` and publish the leaf
statements `x_1, .., x_L` that `x_r` binds (H-BIND). An adversary wins if some published leaf statement is false (no
witness exists). Then

    Pr[ some published leaf statement is false  and  no C2-VIOLATION ]
        <=  t eps_max + sum_v |J_V,v| eps_v + c'_max (t + K)^2 / 2^(8b) + eps_bind.

**Conditional on C2** in exactly this joint sense (section 6, "How to read 'conditional on C2'"; never as a
conditional probability), and on (K), H-DS, H-BIND and C-4 as built. `eps_bind` covers both uses of H-BIND: the
SHAPE-VIOLATION of Lemma TE.3 and the leaf statements' binding to the root.

*Proof.* Outside FAIL, C2-VIOLATION and SHAPE-VIOLATION, `E_T` outputs a compliant tree; its leaf statements are bound
to `x_r` by the node circuits through the concrete statement digests, so outside a collision of those digests among
the values `E_T` computes (H-BIND, the same collision finder `B` as Lemma TE.3) they are the published ones, and each
has the witness `E_T` extracted, so none is false. ∎ (H-BIND was not examined by the first referee, F-6; the second
referee asked for its restatement as collision resistance, T-1, which this revision makes.)

**Corollary TE-F (the figures, category 1, `N = 20,000`, `b = 32`).**

(a) **IOP part: no query count moves.** Every row the calculator certifies has `e_v >= kappa_C + 1 + log2 N +
log2(1 + k_q,v)`, so `eps_v <= 2^-(kappa_C + 1) / (N (1 + k_q,v))`. With `|J_V,v| <= k_q,v` and at most `N` nodes,

    t eps_max + sum_v |J_V,v| eps_v  <=  2^-(kappa_C + 1) ( t / (N (1 + k_min)) + 1 - 1 / (1 + k_max) )
                                     <=  t / 2^(kappa_C + 1)     for every t >= 1,

because `N (1 + k_min) >= 1 + k_max` (`20,000 x 13,457` against `74,941`). So the certified needs already give
the IOP part of Theorem TE' at every `t`, with the knowledge errors of (K) in place of the rows' soundness errors (the
referee reproduced this, F-5).

(b) **Hash part: once for the tree.** The largest `kappa` with `c'_max (t + K)^2 / 2^256 <= t / 2^(kappa + 1)` for
every `1 <= t <= 2^kappa`, with `K <= N k_q,max` (A: `2^29.77`, `k_q` up to 45,658; B: `2^29.59` over the certified
unique-decoding rows, `k_q` up to 40,416, and `2^30.48` with the largest `k_q` the calculator prints for B, 74,940), is
**121.886 (A, `c'_max = 2,397`) and 121.885 (B, `c'_max = 2,401`)** (`hashterm.tree_extraction_level`; `K` is
negligible against `2^121`, so the level is the same at either `K`), against the per-proof sum 114.74. **These are
classical levels under C2, K-A, K-B and T-1**, and H-BIND (Lemma TE.3; revision 3), not unconditional ones. A classical 128 for the hash part on this basis
would need `8b >= 2 x 128 + 1 + log2 c'_max = 268.2`, so **272 bits (34 bytes)**: option (c) of
`decision-qrom-counting.md` 7.4.

(c) **What the calculator prints (revision 10.2).** The tree's classical hash level is printed as **121.89, "under
C2, K-A, K-B, T-1"** (Theorem TE'), with the per-proof union form **114.74** beside it as the comparison (114.74 has no
better foundation: the per-proof sum also needs an extraction argument for inner proofs; it is only more
conservative, referee section 4). The **proven-basis certification check keeps the lower figure** (114.74): at every
profile's digest both figures are below `kappa_C`, so no row's status depends on the choice (tested). The QROM figures
of section 9 are printed beside the claimed 69.58 / 70.45 with the same label. The footer of every table lists the
conditions.

(d) **Every tree figure is conditional on K-A and K-B** (referee C-3, F-3): extraction needs round-by-round
**knowledge** soundness of every round of both systems; soundness errors do not suffice for a tree whose inner proofs
are witnesses. Until those obligations are discharged, every figure of this section carries them.

## 8. The black-box form, and why it moves figures (Corollary TE-bb)

*Provenance: **Original (the Ycash developers, 2026)**; uses only the statement of [SG26] Theorem I.16 (2) and the
form of its extractor stated there (page 142).*

**Corollary TE-bb.** Under (K) and H-DS, for every `(t, 0)`-adversary of the ROM, with `E_T` stopping at
C2-VIOLATION as in section 3,
`Pr[accepted and FAIL] <= sum_v eps^C_ex,sigma(v)(t + K_v)`, where `K_v` is the sum of `k_q,u` over the strict
ancestors `u` of `v` and `eps^C_ex,sigma(t) = (t + k_q,sigma)(eps_sigma + c'_sigma (t + k_q,sigma) / 2^(8b))`.

*Proof.* Define `E_T` as in section 3 but extract each node from the table of `A`'s queries and the verifier queries
**on its own path** only (database algorithm applied to `db_A ∪ db_path(v)`). For each node position `v`, let `B_v` be
the ROM adversary that runs `A`, forwarding every query to its own oracle and recording query and answer, then runs the
verifiers and database algorithms of `v`'s ancestors in order on its recorded table (forwarding their queries), and
outputs `(x_v, pf_v)` (or a fixed rejected pair if it does not reach `v`). `B_v` makes at most `t + K_v` queries. Run
`B_v` against the extractor of Theorem I.16 (2) for `sigma(v)`: that extractor answers by lazy sampling and applies the
database algorithm to the table of `B_v`'s and the verifier's queries, which is `db_A ∪ db_path(v) ∪ db_Vrf_v`, the
same table and the same answers `E_T` uses at `v` (both are functions of one uniform `H`). So "FAIL first at `v`" in
`E_T` implies "the verifier accepts and the extractor's output is not a witness" in that experiment (the acceptance by
the stop at C2-VIOLATION, as in section 6), whose probability is at most `eps^C_ex,sigma(v)(t + K_v)` by Theorem I.16 (2). Union over the
nodes. ∎

**Its cost.** The IOP part binds at `t = 1`: `sum_v (1 + k_q,v + K_v) eps_v <= 2^-(kappa_C + 1)` needs
`e_v >= kappa_C + 1 + log2 N + log2(1 + k_q,v + K_v)`, a rise of `log2((1 + k_q,v + K_v) / (1 + k_q,v))`. A leaf has
four ancestors in the specification's shape (sub-bundle, two merge levels, root). With the ancestors charged at the
largest node `k_q` of the system: B leaves +2.32 bits (rate 1/8) and +2.40 (1/16); A leaves +3.29 to +3.87 bits.
Charging every proof `t + N k_q`, the referee's form `sum_v eps_ex,v(t + N k_q)`, the rise is `log2(1 + N k_q / (1 +
k_q))` = **+14.29 bits** at every row. Either would move every certified count. **So the referee's "no figure moves
(`N k_q = 2^29.7`)" is right for the hash term (negligible against `2^114`) and wrong for the IOP term**, which binds at
`t = 1`, where `N k_q` is not negligible against `1 + k_q`. Theorem TE' avoids the cost because one table is shared:
each verifier query is charged once, to the one system whose challenge it fixes.

## 9. The QROM: Proposition TE-Q' (revision 2: the corrected extractor; derived under C2)

*Provenance: **Original (the Ycash developers, 2026)**, adapting [SG26] Theorem I.16 (1) (page 142) and Lemma I.15
(pages 141, 142). The corrected extractor and the added term are the referee's (`tree-extraction-referee.md` 3.2,
condition C-6). Revision 1's step (ii), quoted from memory, was **false as worded** ("one inside returns the recorded
answer", "is recorded": true only up to `O(2^-n)` per query) and is replaced by Lemma QC (section 9a).*

**What the QROM version needs** (referee 3.1): (a) the pre-measurement part exactly as [SG26] Theorem I.16 (1) for `A`
followed by the root verifier (compressed oracle, Lemmas I.10, I.11, one database measurement, Lemma I.15 with `B*`);
(b) the two-sided instability of `B*` (Lemma TE.1); (c) how the compressed oracle answers the extractor's **classical**
queries after the database has been measured (Lemma QC); (d) the classical per-entry argument for those queries
(section 6 step (2)); (e) C2 as in Theorem TE'. No joint measurement and no commutation argument is needed: after the
one measurement everything `E_T^Q` does is classical, and its queries act on the query and database registers only, so
`A`'s output and its register `Z` are untouched ([SG26] Lemma I.11).

**The corrected `E_T^Q`.** Use Zhandry's compressed phase oracle as [CMS19] Section 3.6 and [SG26] Protocol I.9 do,
with database capacity `T = t + K`.

1. Run `A` and the root verifier against it as the extractor `E_SL` of [SG26] Protocol I.9 does (steps 1, 2, 4), and
   measure the database once, obtaining `db_0` (at most `T_0 = t + k_q,r` entries).
2. Continue as `E_T` steps 3 and 4 (section 3, with the stop at C2-VIOLATION), making each of the child verifiers'
   classical queries `x` to the compressed oracle (phase register prepared as `H^n |0>`, one application of the
   oracle, `H^n`, measure the answer `y`) and **measuring the database after each query**. Stop with the outcome
   **DEVIATION** if the measured database is not `D + [x -> y]` for a fresh `x` (`D(x) = ⊥`), or if a recorded `x`
   (`D(x) = y_0`) does not return `y_0` with the database unchanged.

The capacity `t + K` in place of [SG26]'s `T_0` changes nothing before the measurement: as [SG26] notes in the proof of
Theorem I.16 (1) (page 142), when the database has fewer entries than slots at every query the compressed oracle
"never acts in its full case [CMS19, Lem. 3.2, p. 17]", and [CMS19] Lemma 3.2 depends on the capacity only through that
full case. That is half the argument (`qc-and-status-referee.md` Q-3): [CMS19] Lemmas 5.9 and 5.10 (page 22) are
stated with one `t` for the query count and the database bound, so used as black boxes at capacity `t + K` they would
give `6 T^2 I(B*, T)`, not `6 T_0^2 I(B*, T_0)`. **The other half (revision 3):** the database state of [CMS19] page 16,
`|D_t> = |x_1, y_1, ..> ⊗ |⊥, 0^n>^(t - |D|)`, embeds capacity `T_0` in capacity `T` by padding; with at most `T_0`
queries neither oracle is ever applied to a full database, and off the full case the two act identically (Lemma 3.2,
cases 2 and 3 do not mention the capacity), so the state before the measurement is the padded image of the
capacity-`T_0` state and the measured database has the same distribution; so [SG26] Lemma I.15 (2) is applied at
capacity `T_0`. After the measurement the database never fills: before each of the `K - k_q,r` continuation queries it
has fewer than `t + K` entries.

**Proposition TE-Q'.** Under (K), H-DS, [SG26] Theorem I.16 (1) and Lemma QC (C-4 as built for the node count), for every quantum adversary `A` with at
most `t` quantum queries, with `n = 8(b + e)` the oracle's output bits, `T_0 = t + k_q,r` and `T = t + K`,

    Pr[ Vrf_r accepts  and  E_T^Q ends with FAIL or DEVIATION ]
        <=  2 sqrt(k_q,r / 2^n)  +  6 T_0^2 ( eps_max + c'_max T_0 / 2^(8b) )
          +  sum_(v != r) |J_V,v| eps_v  +  (K - k_q,r) c'_max T / 2^(8b)  +  10 (K - k_q,r) / 2^n,

cubic in `t` with constant 6; `N` does not multiply `t^2`. The left side names both outcomes that are neither a
compliant tree nor a named violation (revision 3, `qc-and-status-referee.md` Q-2: DEVIATION is a fourth outcome of
`E_T^Q`); the right side is unchanged, since by the coupling of (ii) `Pr_Q[FAIL or DEVIATION] <= Pr_L[FAIL] +
Pr[DEVIATION]`. Runs ending in C2-VIOLATION or SHAPE-VIOLATION are not counted; SHAPE-VIOLATION has probability at
most `eps_bind` against quantum collision finders (Lemma TE.3, H-BIND), and every statement about the recursion tree
drawn from it is **conditional on C2** in the joint sense of section 6.

*Proof.* (i) *Before the measurement*, exactly as [SG26]'s proof of Theorem I.16 (1): the oracle simulation error is 0
for `(x_r, pf_r, Z, v)` (Lemmas I.10, I.11); the root is accepted and its extraction fails only outside the simulated
game (at most `2 sqrt(k_q,r / 2^n)`, Lemma I.15 (1)) or with `db_0` in `B*` (Lemma TE.2 at `db_0`), and `db_0` lies in
`B*` with probability at most `6 T_0^2 I(B*, T_0)` (Lemma I.15 (2), which needs a set without the empty database and
the instability of [CMS19] Definition 5.6, the two-sided quantity Lemma TE.1 bounds by `eps_max + c'_max T_0 / 2^(8b)`).
This part is [SG26]'s, read and not re-derived (referee 3.3).

(ii) *After the measurement.* The database register is in the basis state `|db_0>`, in product with every other
register. By Lemma QC, at each continuation query, conditioned on everything before it and on no DEVIATION so far: a
fresh input returns an answer that is exactly uniform and independent of every other register, and the measured
database is `D + [x -> y]` with probability `(1 - 2^-n)^2`, the same for every `y`, so conditioned on no DEVIATION at
this step the answer is still uniform and recorded; a recorded input returns its recorded answer with the database
unchanged except with probability at most `10 / 2^n`. A fresh input deviates with probability `1 - (1 - 2^-n)^2 <= 2 /
2^n`. So the continuation can be coupled with the classical continuation `L` of section 3 from `db_0` (lazy sampling
extending `db_0`) so that the two agree until the first DEVIATION, and `Pr[DEVIATION] <= 10 (K - k_q,r) / 2^n` by a
union bound over the `K - k_q,r` queries of the child verifiers (the database algorithm makes no oracle query).

(iii) *The classical continuation.* In `L` started from `db_0` not in `B*`, a FAIL at a child is a table in `B*` at
the step it is recorded (section 6 step (1), which needs only that the child's native verifier accepted, as `E_T^Q`
checks), and section 6 step (2) applied to the `K - k_q,r` continuation entries gives at most `sum_(v != r) |J_V,v|
eps_v + (K - k_q,r) c'_max T / 2^(8b)`.

Adding (i), the deviation of (ii) and (iii) gives the bound on FAIL or DEVIATION. ∎

**Corollary TE-X-Q (the explicit tree in the QROM; SKETCHED, revision 3, `qc-and-status-referee.md` T-3 (b)).** If
every proof of the tree is published with its statement and verified natively, then under (K), H-DS, H-BIND, C-4 as
built and [SG26] Theorem I.16 (1), for every quantum adversary with at most `t` quantum queries, with `n = 8(b + e)`
and `T = t + K`,

    Pr[ every published proof accepted  and  the extraction fails ]
        <=  2 sqrt(K / 2^n)  +  6 (t + K)^2 ( eps_max  +  c'_max (t + K) / 2^(8b) ),

and SHAPE-VIOLATION is bounded separately by `eps_bind`. *Sketch:* the proof of [SG26] Theorem I.16 (1) re-run with
one verifier that runs every published proof's verifier, `K` queries in all, before the single database measurement,
and the joint bad set `B*` (Lemmas TE.1, TE.2 in place of [SG26] Lemmas I.12, I.14); no continuation after the
measurement, so no Lemma QC term and no C2. This is the proof of I.16 (1) re-run with a joint bad set, **not** the
theorem used as a black box; it is labelled **sketched** until written out in full. Revision 2 asserted it in one
sentence; the second referee found it right as far as checked.

**Figures** (`e_min` the weakest round of the system's rows, every term evaluated at `t = 2^kappa`, category 1, `b =
32`, `e = 0`, the shortest stream, as the calculator does since R10-9; `n = 8(b + e) >= 256`):

| Term | A | B | Note |
|---|---|---|---|
| IOP part, `6 t^2 eps_max = 1/2` at `kappa = (e_min - 1 - log2 6) / 2` | **76.72** (`e_min` 157.03) | **77.60** (158.78) | the one-table form |
| Hash part, `6 c'_max t^3 / 2^256 = 1/2` | 80.40 | 80.40 | the per-proof figure |
| Stream term `2 sqrt(k_q,r / 2^n)`, `log2` | about -119 | about -119 | one proof |
| Lemma QC term `10 (K - k_q,r) / 2^n`, `log2`, `K <= N k_q,max` | **-222.91** (`k_q,max` 45,658) | **-223.09** (40,416); -222.20 at 74,940 | negligible |
| Calculator's per-proof union (the figure the project **claims**) | **69.58** | **70.45** | `soundness/` revision 10.2 |

All of these are **derived under the recursion heuristic C2**, and conditional on K-A, K-B (owed), H-DS and the
transcripts' fit to [SG26] Protocol 6.5 (T-1, owed from the builders), [SG26] Theorem I.16 (1) (a preprint; read, not
re-derived), Lemma QC (refereed: pass), H-BIND (Lemma TE.3) and [CMS19] Lemmas 5.9, 5.10 as black boxes (through [SG26] Lemma I.15). They are
**not** unconditional QROM theorems, and no unconditional QROM figure exists for a tree whose inner proofs are
witnesses. Proven, given [SG26] Theorem I.16 (1), (K) and T-1: the per-proof QROM figures; sketched: a tree whose
every proof is published (Corollary TE-X-Q: one verifier with `K` queries before the measurement; no continuation, no
C2). Revision 1's sentence
"without (ii) there is no proven QROM figure for the tree" is superseded: (ii) is closed in the corrected form by Lemma
QC, and what remains is C2, which was always there. The project claims the lower figures (69.58 / 70.45); 76.72 /
77.60 are printed beside them as the one-table comparison.

## 9a. Lemma QC: a classical query after a database measurement

*Provenance: **Original (the Ycash developers, 2026)**, found in referee review (`tree-extraction-referee.md` section
3.2, where it is stated and proved); derived from [CMS19] Lemma 3.2 (printed page 17; Published there, attributed to
Zhandry and proved in [CMS19] Appendix A, which was not read). Original as far as checked (sources consulted: [CMS19]
Sections 3.5, 3.6, 4 by the referee, page 17 for this revision; [SG26] Appendix I). The proof below is the first
referee's, written out in full; **refereed by a second referee, `qc-and-status-referee.md` section 1: PASS** (both
cases re-derived, the coupling checked, a numerical check for `n = 1` to 5).*

**Setting.** [CMS19] Lemma 3.2 (page 17, read from the rendered page) states the action of the compressed phase oracle
`O` with `m` input bits, `n` output bits and database query bound `t` on a basis state `|x, u, z, D>`, `|D| <= t`:

- if `|D| = t` or `u = 0^n`: `O |x, u, z, D> = (-1)^(u . D(x)) |x, u, z, D>`, with `u . ⊥ := 0`;
- if `D(x) = ⊥`, `|D| < t` and `u != 0^n`: `O |x, u, z, D> = |x, u, z> ⊗ 2^(-n/2) sum_y (-1)^(u . y) |D + [x -> y]>`;
- if `D(x) != ⊥`, `|D| < t` and `u != 0^n`: `O |x, u, z, D> = |x, u, z> ⊗ |phi_u>`, where
  `|phi_u> = (-1)^(u . D(x)) |D> + (-1)^(u . D(x)) 2^(-n/2) |D - x> + 2^-n sum_y (1 - (-1)^(u . y) - (-1)^(u . D(x)))
  |D - x + [x -> y]>`.

A **classical query on `x`** is: prepare the phase register `u` as `H^n |0^n> = 2^(-n/2) sum_u |u>`, apply `O`, apply
`H^n` to the phase register and measure it; the outcome is the answer `y`.

**Lemma QC (continuation after a database measurement).** Let the database register be in a basis state `|D>` with
`|D|` below the capacity, in product with every other register. A classical query on `x` satisfies:

1. if `D(x) = ⊥`: the answer `y` is **exactly** uniform on `{0,1}^n` and independent of every other register; measuring
   the database afterwards gives `D + [x -> y]` with probability `(1 - 2^-n)^2`, for every `y`;
2. if `D(x) = y_0`: measuring the answer and then the database gives `(y_0, D)` with probability at least `1 - 10 /
   2^n`.

The constant 10 is not tight (`qc-and-status-referee.md` Q-1): case (2) gives 6 analytically (`2 / 2^n` or `6 / 2^n`
by the sign of `(-1)^(u . y_0)`), and the referee's numerical check gave about `3.8 / 2^n` at `n = 5`. It is kept at 10.

*Proof.* Write `|D'_y>` for `|D + [x -> y]>`. The registers `x` and `z` are untouched and omitted.

(1) Before the oracle the state is `2^(-n/2) sum_u |u> |D>`. By the first case (`u = 0`) and the second (`u != 0`),
after `O` it is

    2^(-n/2) |0> |D>  +  2^(-n/2) sum_(u != 0) |u> 2^(-n/2) sum_y (-1)^(u . y) |D'_y>.

Write the second sum as the sum over every `u` minus the term `u = 0`. Apply `H^n |u> = 2^(-n/2) sum_(y') (-1)^(u . y')
|y'>` to the phase register. The full sum gives `2^(-n/2) 2^(-n/2) 2^(-n/2) sum_y sum_(y') (sum_u (-1)^(u . (y + y')))
|y'> |D'_y> = 2^(-n/2) sum_y |y> |D'_y>`, since the inner sum is `2^n` if `y' = y` and 0 otherwise; the term `u = 0`
of the first part gives `2^-n sum_(y') |y'> |D>`; the subtracted term gives `-2^(-3n/2) sum_(y') |y'> sum_y |D'_y>`. So
the state is

    sum_(y') |y'>  ⊗  ( 2^(-n/2) |D'_(y')>  +  2^-n |D>  -  2^(-3n/2) sum_y |D'_y> ).

The vectors `|D>` and `|D'_y>` (one per `y`) are orthonormal. In the bracket the coefficient of `|D'_(y')>` is
`2^(-n/2) - 2^(-3n/2) = 2^(-n/2) (1 - 2^-n)`, that of `|D>` is `2^-n`, and that of each `|D'_y>`, `y != y'`, is
`-2^(-3n/2)`. Its squared norm is

    2^-n (1 - 2^-n)^2  +  2^-2n  +  (2^n - 1) 2^-3n   =   2^-n ( (1 - 2^-n)^2 + 2^-n + 2^-n - 2^-2n )   =   2^-n,

the same for every `y'`, so the answer is exactly uniform. Every other register is in product with `|D>` and is not
acted on, so the answer is independent of it. Given the answer `y'`, the database is in the normalized bracket, and
measuring it gives `D + [x -> y']` with probability `2^-n (1 - 2^-n)^2 / 2^-n = (1 - 2^-n)^2`.

(2) By the first case (`u = 0`) and the third (`u != 0`), after `O` the state is `|Psi> = |Psi_0> + |Delta>`, where
`|Psi_0> = 2^(-n/2) sum_u (-1)^(u . y_0) |u> |D>` and `|Delta> = 2^(-n/2) sum_(u != 0) |u> |delta_u>` with

    |delta_u>  =  (-1)^(u . y_0) 2^(-n/2) |D - x>  +  2^-n sum_y c_(u,y) |D - x + [x -> y]>,     c_(u,y) = 1 - (-1)^(u . y) - (-1)^(u . y_0).

The vectors `|D - x>` and `|D - x + [x -> y]>` are orthonormal, and `|c_(u,y)| <= 3`, so `|| delta_u ||^2 <= 2^-n +
2^-2n 2^n 9 = 10 / 2^n`, and `|| Delta ||^2 = 2^-n sum_(u != 0) || delta_u ||^2 <= 10 / 2^n`. After `H^n` on the
phase register, `|Psi_0>` becomes `|y_0> |D>` exactly. Let `Pi` project onto `|y_0> |D>` and `Pi^⊥ = 1 - Pi`. The
probability that the measurements do not give `(y_0, D)` is `|| Pi^⊥ (H^n ⊗ 1) |Psi> ||^2 = || Pi^⊥ (H^n ⊗ 1) |Delta>
||^2 <= || Delta ||^2 <= 10 / 2^n`, since `Pi^⊥` annihilates the image of `|Psi_0>` and `H^n` is unitary. ∎

The referee checked (1) and (2) numerically for `n = 1` to 5 on one cell (the transcribed map unitary, uniformity
exact, `(1 - 2^-n)^2` exact, (2) with room); the second referee ran an independent check of the same kind
(`qc-and-status-referee.md` section 1: worst failure probability of case (2) about `3.8 / 2^n` at `n = 5`).

**At our parameters.** `n = 8(b + e) >= 256`; the continuation makes at most `K - k_q,r < N k_q,max` queries, so
`Pr[DEVIATION] <= 10 (K - k_q,r) / 2^n`: `log2` **-222.91** for system A (`N k_q,max = 2^29.77`), **-223.09** for B
over its certified rows (`2^29.59`), **-222.20** for B at the largest `k_q` the calculator prints (74,940); at category
3 about -350.4 and at category 5 about -478.1 (`hashterm.lemma_qc_log2`, printed by the calculator revision 10.2). The
term is negligible: at `t = 2^64` the smallest other term of Proposition TE-Q' is the continuation's hash term
`(K - k_q,r) c'_max T / 2^256`, about `2^-151.0` (A), and the Lemma QC term is more than 70 bits below it.

## 10. What a referee should attack first

Revision 1's list put "H-C2 as stated" first; the first referee found that hypothesis false in the ROM (F-1). The
second referee passed Lemma QC and passed revision 2 with conditions T-1 to T-4 (`qc-and-status-referee.md`). For
revision 3:

1. **Lemma TE.3 and SHAPE-VIOLATION (sections 3, 6).** That every way the extracted tree can exceed `N` nodes or fail
   to descend passes through a cell mismatch on an edge, and that a cell mismatch with an accepted child is a
   collision of the concrete statement digest that the collision finder `B` outputs; that `B` needs no oracle (it
   simulates `H` by lazy sampling, and the compressed oracle in the QROM).
2. **H-BIND as restated (section 2)**: collision resistance of the concrete digest functions, with no oracle bound;
   that the bound IV (A) and the constraint-system digest (B) determining the program is the same kind of assumption
   (H-DS within one system).
3. **The joint-probability reading of C2 (section 6)** and the three "may not" sentences.
4. **Corollary TE-X-Q (section 9)**, sketched: the proof of [SG26] Theorem I.16 (1) re-run with a joint bad set.
5. **The capacity remark (section 9)**: the padding embedding of capacity `T_0` in `T`.
6. **The audit owed (C-4)**: termination and level binding in both node circuits (`yugen-proof-a`
   `guests/bundle_merge_e2.py`, `bundle_sub_e2.py`; `yugen-proof-b2` `src/bundle.rs`), the native `Tree::check`,
   B's all-on rule set pinned in the consensus constraint-system digest; and that the circuits state "every child proof
   is accepted for the child's statement" (`soundness-method.md` 8.5b item 8). Met by design, by search; not audited.
7. **The count `|J_V,v|`** of stream queries ([SG26] Definition I.1, not re-read) and for system B's `V'` (padded slots
   add Merkle queries, not stream queries).
8. *(Revision 4, 5.)* **Section 6b**: B's node bound by shape and kind and the (kind, depth) order; `E` and H_int;
   the two-pass fold argument (pass 2's induction, the fixed `W*`), the per-query batching term and its quantum form
   (the [CMS19] constant not re-read), the per-build field reading.
9. Task T-1 item 10: A's unframed Keccak-256 statement wrappers (BC-5) against the part tags (not checked).

## 11. Provenance

| Item | Label | Source / what changed |
|---|---|---|
| Spbcs knowledge soundness, its extractor's form (lazy sampling + database algorithm), Lemma I.12, I.14, I.15, Theorem I.16 | Published | [SG26] pages 140 to 143, rendered; used as stated |
| Lemma TE.1 (joint bad set, two-sided per-entry instability) | Adapted | from [SG26] Lemma I.12: several systems on one table; per-entry error of the system the entry fixes. Revision 2: stated two-sided as I.12 is (referee F-2); revision 1's monotonicity claim withdrawn |
| Lemma TE.2 | Published (per node) | [SG26] Lemma I.14 with `B*`; Theorem D step 5 for B's `V'` |
| The tree extractor `E_T` with the stops at C2-VIOLATION and SHAPE-VIOLATION, Theorem TE', Corollaries TE-X, TE-S, TE-F, TE-bb | Original (the Ycash developers, 2026) | this document. Revision 1 (`f414811`) refereed in `tree-extraction-referee.md` (pass with conditions); revision 2 (`44b751d`: the restatement as TE', the explicit-tree corollary, the stop of F-4) refereed in `qc-and-status-referee.md` (pass with conditions T-1 to T-4); revision 3 (SHAPE-VIOLATION, H-BIND as collision resistance, the joint-probability reading) follows those conditions and is **unrefereed**. Sources consulted for prior statements of a tree / recursion extraction lemma in the folder: [SG26] (Theorem I.17's extended table is the closest), [CMS19] as cited by [SG26]; recursive-proof extraction in the literature (e.g. proof-carrying data) is known **from memory only** and was not consulted, so the label is "Original as far as checked" |
| C2 as the named event C2-VIOLATION, entering at two places | Original (the Ycash developers, 2026), found in referee review | `tree-extraction-referee.md` 1.1; replaces revision 1's hypothesis H-C2 (withdrawn: false in the ROM) |
| Lemma TE.3 (SHAPE-VIOLATION is a digest collision) and H-BIND as collision resistance | Original (the Ycash developers, 2026), found in referee review | `qc-and-status-referee.md` T-1; written out here in revision 3; revision 3.1 + 6b and H-BIND **refereed in `te3-referee.md` (`1056ea6`), pass with conditions TE3-1 to TE3-5**, applied in revision 5.3, not re-refereed. Collision bounds: Brassard–Høyer–Tapp (LATIN 1998), Zhandry (QIC 2015), Chailloux–Naya-Plasencia–Schrottenloher (ASIACRYPT 2017), Rogaway (VIETCRYPT 2006): Published, **cited from memory, not checked against the papers**; [CFP] §4.A.5 in the folder |
| Proposition TE-Q' and the corrected `E_T^Q` | Original (the Ycash developers, 2026); the extractor's correction found in referee review | from [SG26] Theorem I.16 (1), Lemma I.15; the continuation by Lemma QC; revision 2 form refereed in `qc-and-status-referee.md` (pass with conditions); revision 3 (FAIL or DEVIATION, Q-2; the padding sentence, Q-3, from [CMS19] page 16 and Lemmas 5.9, 5.10) **unrefereed** |
| Corollary TE-X-Q | Original (the Ycash developers, 2026), found in referee review | `qc-and-status-referee.md` T-3 (b); the proof of [SG26] Theorem I.16 (1) re-run with the joint bad set; **sketched**, unrefereed as written |
| Revision 4, section 6b (shape parameters, B's node bound and order, `E`, the fold's conditioning and terms) | Original (the Ycash developers, 2026) | `b-internal-node-referee.md` 5, `b-fold-referee.md`, `yugen-proof-b2` parameters section 24; revision 4 refereed in `tree-extraction-rev4-referee.md` (pass with conditions R4-1 to R4-8); revision 5 applies them, **draft, unrefereed** |
| Lemma QC | Original (the Ycash developers, 2026), found in referee review | from [CMS19] Lemma 3.2 (page 17, rendered; Published there, attributed to Zhandry; Appendix A not read); stated and proved in `tree-extraction-referee.md` 3.2, written out in section 9a; **refereed: `qc-and-status-referee.md` section 1, PASS** (both cases re-derived, numerical check `n = 1..5`) |
| The black-box cost and the reading of R10-2 | Original (the Ycash developers, 2026) | figures computed with the calculator's functions (`hashterm`, `category`) at revision 10.1; arithmetic confirmed by the referee (section 2 there; 2.40 and 3.29 to 3.87 not recomputed row by row) |
