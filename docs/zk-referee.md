# Referee report: salting of the leaf proof's trees (systems A and B), HVZK documents

Date 2026-11-19. Independent referee. Builder repositories read, not modified; no test was run by
this referee (every "test" below is cited from code, not re-run).

## 1. Priority 1: system B's fold trees

**Answer: the audit finding is stale. B's fold trees are salted as built**, since commit
`7de8da0` of `yugen-proof-b2` (2026-11-19 11:59, VENDOR.md change 35, "route S"), an ancestor of
the head. The audit (`qc-and-status-referee.md`, committed 18:35) quoted `zk-quantum.md` section 5
and `yugen-proof-b2/docs/parameters.md` line 1942 ("Not built: salts on the four fold trees"),
both written before change 35 and not updated; section 11.2 of the same `parameters.md` records
the change as built.

Trees of a B leaf (payment) proof, as built (`vendor/binius64/crates`):

| Tree | Salted | Where |
|---|---|---|
| Round oracle 1 (precommit and inner trace = witness) | yes, row salt length (512 bits at category 1, `CAT1_SALT_BITS`) | `iop-prover/src/basefold/channel.rs` 211-230 |
| Round oracle 2 (wrapper private and mask) | yes, same | same |
| Every fold-round tree | yes, fold salt = round salt length when any round oracle is hiding | `iop/src/basefold/compiler.rs` 95-102; `iop-prover/src/fri/fold.rs` 298-316; verifier `iop/src/fri/fold.rs` 169, 235 |
| Terminal codeword | no tree salt; it is sent in full | `iop/src/fri/fold.rs` 182 |

Salt coins: `F::random` from a `StdRng` seeded from the channel's generator, which the leaf prover
takes from `rand::rng()` (OS-seeded) at `src/prove.rs` 188. Node proofs: transparent, unsalted.

Consequences. With every opened-or-hidden tree salted at 512 bits and fresh per leaf, the sibling
digests of unopened leaves are within the [SG26] / Lemma H statistical bound regardless of leaf
content, so no guessing test (classical or quantum) against sibling digests applies; verdict (c)
"must salt" is already met; cost is in the build (`parameters.md` 11.3 table: route S, longer
salts and the cap add 0.2 M AND rows; +116 x 32 bytes per salted fold tree in
`spartan-verifier/tests/proof_size_test.rs` at the pin's field). The terminal codeword is a prover
message, not an oracle: it is not a salting matter but part of `eps_hvzk^B` (it reveals `2^n_f`
linear functionals of the folded masked polynomial; B's mask is the full-length `omega` of
Diamond Construction 4.1, so the budget `Q * 2^K + 2^n_f` is far below the mask dimension).

For the record (route F, not needed): without salts an unopened fold leaf is a coset of a
deterministic linear image of `(M, omega)` given the challenges (`zk-hiding-commitment.md` 1.4);
its min-entropy given the transcript is positive only while revealed functionals stay below the
folded dimension, which is small in the last fold rounds, and an unbounded-query distinguisher can
test candidate cosets against siblings. No statistical statement holds; salting was the right fix.

Node proofs need no zero knowledge: their witnesses are leaf proofs (published to the audit feed),
child node proofs and public data (`zk-quantum.md` section 4, hypothesis N table); leaf proofs are
public, so nothing secret enters a node. Confirmed against both builders' docs; not re-derived
from node circuits.

### System A

All trees of the masked leaf (rows 6, 8) are salted with 8 words (64 bytes): the level-0 commit
(`pcs/src/whir.rs` 190), every later WHIR level (`whir.rs` 400, tree index `level + 1`), and every
oracle of the hiding opening W-I (`pcs/src/wi.rs` 273, 287, unconditional `Some(salts)`). Salts and
masks come from the caller's `zk_seed` through SHAKE256 (finding S-1 of A's `parameters.md`,
computational).

## 2. Findings

| # | Class | Location | Finding | Fix |
|---|---|---|---|---|
| R-1 | MAJOR (record) | `what-is-proven.md` Z-2..Z-4; `qc-and-status-referee.md` 5.1 item; `zk-quantum.md` section 2 table row and section 5 | state B's fold trees as unsalted; the build salts them since `7de8da0` | rewrite section 5 as "route S built (change 35)"; drop "route S not built" from Z-2's conditions; cite `7de8da0` |
| R-2 | MINOR | `yugen-proof-b2/docs/parameters.md` 1941-1943 | "Not built: salts on the four fold trees" contradicts 11.2 | builder strikes the line |
| R-3 | MINOR | B tests | no test asserts fold-tree digests equal the salted hash (the round-oracle test at `iop-prover/src/basefold/channel.rs` 1836-1900 does this for round oracles only); evidence is round trips and proof size | extend that test to every fold-round commitment and to the terminal (unsalted) |
| R-4 | MINOR | A: `ProveOptions::zk_seed` | the library takes the seed from the caller; bench and `src/bin/wasi.rs` 33 use the fixed `[0x42; 64]`. Not a leak in a wallet that calls `prg.rs` 85 (`getrandom`), but a wallet copying the bench would publish witness-dependent, reproducible masks | wallet entry point draws the seed itself; fixed seeds behind a test-only constructor |
| R-5 | NOTE | both | de-duplicated positions and first/duplicate flags are functions of the public Fiat-Shamir query indices: no leakage | none |
| R-6 | MINOR | `zk-hiding-commitment.md` 129-130, 710-736 | worked examples use queries 171/119/117/116 and describe B as WHIR `n = 19`, folds 5/4; tonight's rows are A 234/166/169/186 and B 184-192 at rate 1/8 on BaseFold | restate the examples; A's code sizes `t = Q` per level from the row (`verifier/src/wi.rs` 64-85), so coverage holds at the raised counts by construction |

## 3. Verdicts

- **B's privacy as built:** salting is complete on every tree (finding of the audit withdrawn);
  zero knowledge still rests on `eps_hvzk^B`, owed (Z-B), as the documents say.
- **A's privacy as built:** every tree salted at 64 bytes; mask budget `t = Q` tracks the row;
  conditional on S-1 (generator) and `eps_hvzk^A` (Z-A).
- **HVZK documents:** read only for coverage (R-5, R-6); simulators per system not re-checked.
- **zk-quantum revision 2 (Theorem 6.6 (3), (4); Theorem ZP):** not reached, beyond R-1.
