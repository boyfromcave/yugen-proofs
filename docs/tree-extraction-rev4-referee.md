# Referee report: `lemma-tree-extraction.md` revision 4 (section 6b)

Part of Yugen. Independent, adversarial. 2026-11-20.
Object: `docs/lemma-tree-extraction.md` at `90abb90` (revision 4, draft), sections 0, 6b.
Code checked: `yugen-proof-b2` `wt/s045` branch `agg` @ `f231a31` (`docs/parameters.md` 21-24,
`src/node.rs` `uniform_head` and `batch_parallel`, `src/uroot.rs::check_root`, `src/fold.rs`, `src/bvirt.rs`).
Earlier reports read: `tree-extraction-referee.md`, `b-internal-node-referee.md`, `b-fold-referee.md`,
`tree-shape-referee.md`. Spec: `yugen-spec` tag `spec-0.4.7`, `spec/yugen-protocol.md` section 15.
Papers: none newly used. The lemma's [SG26] (C. Sharp, P. Grubbs, ePrint 2026/2615) and [CMS19]
(A. Chiesa, P. Manohar, N. Spooner, ePrint 2019/834) are relied on only as revision 3 used them; not re-read.

**Verdict: PASS WITH CONDITIONS** (conditions R4-1 to R4-8, section 3). Nothing in 6b may be marked proven yet.

## 1. Arithmetic

| Figure | Lemma | Check | Result |
|---|---|---|---|
| B node bound, 4/4/5 | `L + 3S + 3M` = 4,096 + 3,072 + 1,023 = 8,191 | 4^6 leaves, 4^5 sub-bundles, 4^4+..+1 = 341 merges; each sub-bundle and merge is top + 2 internal at most | correct (upper bound) |
| B stop | `N_B + 2` = 8,193 | a uniform node has two slots | correct |
| A stop, 4/4/5 | `N + 4` = 20,004 | `MAX_TREE_PROOFS` 20,000 is unreachable at 4/4/5 (<= 5,461 proofs, `tree-shape-referee.md`); valid, loose | correct |
| A stop, 16/16/3 | `N + 16` = 20,016 | spec 0.4.7 15: arity 16, depth <= 3, cap 20,000 | correct |
| per-node batching | `(m-1+2(n+2))/2^128`, `m <= 5`, `n+2 = 70`: 144, `2^-120.8` | as built (24.4): `m = 4`, `n+2 = 74` (`n_wiring` 72 at pad 24,22,25): **151**, `2^-120.76` | constants stale; figure unchanged to 0.1 bit |
| sum, 8,193 nodes | `2^-107.8` | `151 x 8,193`: `2^-107.76` | correct |
| sum, 20,016 nodes | `2^-106.5` | `2^-106.47` | arithmetic right; instance not built (R4-3) |
| built sum, 24.4 (3) | - | `151 x 1,516 = 228,916`: `2^-110.20` | arithmetic right; **wrong N for a theorem** |

**Which N is right.** The 1,516 of parameters 24.4 (3) is `N + 16` with `N = 1,500`, the critical-path
block size of 21.4, and mixes the 16/16/3 overshoot into the 4/4/5 code. A soundness bound must range
over every tree the circuits accept, not the expected block: at 4/4/5 that is B's `N_B + 2 = 8,193`
(and the stop, not 1,516, is what `E_T` enforces). The lemma's `2^-107.8` is the right figure; 24.4's
`2^-110.2` is a per-block illustration and must not be quoted as the theorem's term (R4-2).

## 2. Substance

**2.1 Extraction with deferred wiring checks: goes through, with an ordering stated.** The theorem
should run in two passes, which 6b (c) implies but does not write: (i) extract the whole tree under the
oracle-free relation "node verifier accepts" (TE' unchanged, K-B applies since the claim's truth is not
part of what the verifier checks); (ii) top-down, from the root discharge, show every reached node's
carried claim true except with the batching union. Writing the node relation as "accepts **and** claim
true" (6b (c)) and then invoking K-B on it is not right: K-B extracts for the verifier's relation, and
"claim true" is a statement about a public polynomial, not a witness property the IOP proves (R4-1).

*Is the claim bound to the child that produced it?* Yes as built: the child's `W*` claim and `fW` are
public words of the child's statement (head word 20), linked into the parent's slot and bound into
the parent's transcript before its first challenge (`batch_parallel`, `bind`), and the extracted child
witness carries the same public words. *Can claims be mixed across subtrees?* Mixing is harmless:
every claim is about one fixed polynomial `W* = sum_k eq(s,k) W_k` of the four keys the root pins, so a
claim's truth does not depend on where it came from; the only attack is a false claim batched into a
true one, which is exactly the batching term. This needs the four `W_k` fixed by the pinned keys and
the common padding rule (24.4 condition 1, built); state it (R4-1).

**2.2 The batching term is not purely statistical.** The fold's challenges are Fiat-Shamir outputs
computed by the node prover (the in-node transcript is the prover's witness, 24.2). An adversary can
re-try a node's witness (e.g. resample its own proof's salt) and re-hash: each try is a fresh chance.
The correct form is a round-by-round error charged per oracle query, i.e. at most
`(t + K) eps_batch,max` (state-restoration form), not `sum_v eps_batch,v` over reached nodes. Over
`GF(2^128)` that is `t 2^-120.8`, which caps the classical level near 119.8 bits, below `kappa_C`. Under
`cat1`/`cat1t` the challenge field is the 256-bit extension (`parameters.md` 105, 2135; `EW` = 4 words),
so `eps_batch ~ 151/2^256` and the term is negligible at any `t <= 2^128`. 6b and 24.4 (3) both use
`2^128`. Settle the field per build and restate the term in the t-linear form (R4-4). It then belongs
next to `t eps_max` in TE''s bound, **not in `k_q`** (it is still not a published verifier's query);
24.4's "not in `k_q`" is right, the "statistical" label is not.

**2.3 Head-key pinning (internal-node condition 5): built.** `src/node.rs::uniform_head`: every child
asserts `K0`, `KI0` equal to the node's for every kind, `KM`, `KI` for kinds 1, 2; kind indicators
one-hot; top accepts only kind 2, top-0 only 3, others refuse 2, 3; `fW` fixed by kind
(`1 + [f=3]` complement; `[f=1]` in `Merge`). `uroot::check_root` compares all four keys with the
`RootRule` constants. Tests named in 22, 23, 24.4 (6). 6b (b)'s "**not built**" is stale (R4-5). The
(kind, depth) order therefore holds as built, given the slot's kind subcircuit binds `f` to the
child's key (asserted in 22; not re-read here).

**2.4 Statistical terms and `k_q`.** `eps_bind` (with H_int) correctly stays outside `k_q`; the
re-certified 40,568 (+0.7786) correctly counts the fold's 152 transcript elements conservatively and
nothing else. 6b (c) still cites 40,564 (R4-6).

**2.5 16/16/3 for System A.** Valid: spec 0.4.7 is 16/16/3 (arity 16, depth <= 3, `MAX_TREE_PROOFS`
20,000); A's guests are unchanged; stop `N + 16` as revision 3.1. 4/4/5 is not in spec 0.4.7, so the
4/4/5 instantiation is for the proposed shape only (R4-7). For B at 16/16/3 there is no internal form and
no fold, so the `2^-106.5` figure at 20,016 belongs to no built or specified system (R4-3).

**2.6 C2 obligations.** The five new guests are the right list. One addition: the root discharge
(`check_root` / `fold::evaluate`) is native-only and part of the verifier, so it owes a test that it
equals `sum_k eq(s',k) W_k(r')` for the deployed keys (already in `vfinal`, not run) (R4-8).

## 3. Conditions

1. **R4-1.** Restate 6b (c) as two passes: extraction under "accepts" (TE' and K-B unchanged), then the
   top-down truth argument from the root discharge; record that claims refer to one fixed `W*` of the
   pinned keys, so mixing across subtrees is irrelevant, and that each child's claim is a public word of
   its statement bound before the parent's challenges.
2. **R4-2.** The theorem's node count at 4/4/5 for B is 8,193; amend `parameters.md` 24.4 (3) so 1,516
   (`N = 1,500`, critical path) is labelled an illustration, not the theorem's term.
3. **R4-3.** Drop or relabel the `2^-106.5` (20,016) figure: no B instance with a fold at 16/16/3.
4. **R4-4.** Restate the batching term in Fiat-Shamir (t-linear) form, `(t + K) eps_batch,max`, inside the
   theorem beside `t eps_max`; state the challenge field per build (256-bit under `cat1`/`cat1t`, where
   the term is negligible; at `GF(2^128)` it caps the level near 119.8 bits). Show from code that the
   fold's challenges are drawn in the build's challenge field.
5. **R4-5.** Mark internal-node condition 5 built (`uniform_head`, `check_root`), with the tests.
6. **R4-6.** Use the built constants: `m = 4`, `n + 2 = 74`, 151; `k_q` 40,568.
7. **R4-7.** State that 4/4/5 is a proposal not in spec 0.4.7; the theorem applies to B's built tree only
   once the spec adopts it. A at 16/16/3 stands as revision 3.1.
8. **R4-8.** Add the root discharge to the C2 / native-equivalence list (vfinal's random-point check run).
