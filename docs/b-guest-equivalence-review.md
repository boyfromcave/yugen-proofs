# Review: system B's in-circuit verifier ("guest") against the native verifier

Part of Yugen. Maths team, 2026-11-19. Referee-queue item 3 of `what-is-proven.md` (the engineering
side of C2 for every B tree claim). **A review, not a proof; unrefereed.** Code: `yugen-proof-b2` `1f67267`, read
with `git show HEAD:<path>`; nothing was built or run. Provenance of everything below: **Original (the Ycash
developers, 2026)** as a review; no paper is used except where cited.

## 0. Verdict

| Severity | Finding |
|---|---|
| **Major** G-1 | The merge (uniform) slot's circuit (`u_record`: the kind flag `f`, its range check, the choice of `K0` / `KM` for the child's statement identifier) and the **native final verifier of a root** (keys, flags, the four leaf claims and the two carried wiring claims) exist only in `examples/recbench.rs` (`u_record`, lines 425-480; `"ufinal"`, lines 2290-2350). Neither is a library function and no file under `tests/` exercises them. The consensus verifier and the guest it is equivalent to must be library code with tests of record. |
| Minor G-2 | The native root reads a flag word as "1 or not 1" (`node::Uniform::read`, `inout[UNIFORM_F0].as_u64() == 1`), while the circuit uses the word as a field element weight. Equivalent only because every node's flags are boolean by induction (level 0 asserts them zero, `node.rs:556-560`; a merge computes them as an OR of booleans, `node.rs:575-593`, with `f` range-checked in the slot). The native verifier should refuse a flag word outside `{0, 1}` instead of reading it as 0. |
| Minor G-3 | `transcript.finalize()` (empty tape) is a native check with no in-circuit counterpart: a child proof with trailing bytes is accepted in circuit and refused natively. Not a soundness issue (the extractor reads what the circuit consumed), but by definition it is a C2-VIOLATION that the honest prover never causes. Fix: define a child proof as the prefix the verifier consumes, or have the slot replay refuse a proof with bytes left. |
| Info | The guest is the native verifier's own generic code (`IOPVerifier::verify`, the wrapper, `BaseFoldVerifierChannel`, `FRIVerifier`) run on `Binius64BuilderChannel`; equivalence reduces to the channel operations (section 1) and to the few checks made outside them (section 2). Every such check found has an in-circuit or deferred counterpart. |
| Info | `src/pbatch.rs` matches protocol P-sh of `decision-b-parallel-batching.md` and enforces the referee's conditions C-1 to C-8 where its table says (`b-round-census.md` 2.3). |

Nothing taken from unchecked advice was found on the paths read; the advice entries are listed in section 3 with
what pins each.

## 1. Channel operations: native against guest

| Native (`VerifierTranscript` channels) | Guest (`vendor/binius64/crates/recursion/src/channel.rs`) | Equal? |
|---|---|---|
| `bind_statement(id)` (statement identifier, 64-byte salt first) | `over_statement_parts`: the identifier as constant bytes with the key digest on four wires (`challenger.rs:195-250`); the merge slot sets those wires to `KM` or `K0` of the child's public words by `f` (`recbench.rs:466-474`) | yes, if the identifier template is the native one (asserted at record time: `template[at..at + 32]` zero) |
| `observe_words(inout)` | input wires absorbed (`channel.rs:515-528`); the slot asserts them equal to its public statement wires | yes |
| `recv_one` / `recv_many` (prover message, absorbed) | input element absorbed (`channel.rs:465-470`) | yes |
| `sample` | in-circuit challenger (`channel.rs:473`); tests `a_challenge_after_a_bit_sample_matches_the_native_challenger`, `..._after_a_grind_...` (`channel.rs:1062, 1123`) | yes (by test) |
| `sample_bits(index_bits)` | masked by a gate (`channel.rs:577-582`); test `a_sampled_index_is_the_native_one_and_fits_its_width` | yes |
| `assert_zero` | one zero constraint per word; a non-zero build-time constant is refused at build (`channel.rs:486-512`) | yes |
| `recv_salted_merkle_commitment` | root input absorbed (`channel.rs:643-680`) | yes |
| `recv_openings` (paths to the cap) | leaf hashed and climbed in circuit (`merkle.rs`, BLAKE3 gadgets) | yes in shape; the gadgets themselves not re-read here |
| repeated index opened once (Lemma D, VENDOR change 34) | every place verified; the replay fills a repeat | the guest is stricter; conditions D-1 to D-5 are `lemma-d-referee.md`'s |
| `recv_committed_vector` (terminal codeword) | hashed to its root in the residue | yes |
| `verify_grind` | nonce absorbed, masked draw asserted zero (`channel.rs:617-640`) | yes (zero difficulty at every row: nothing recorded) |

## 2. Checks made outside the channel, and where the guest makes them

| Native check | Where | Guest |
|---|---|---|
| Public input length (`spartan-verifier/src/lib.rs` "Check that the public input length is correct") | native `if` | fixed by the circuit's shape; tested natively by `tests/referee_conditions.rs::a_public_word_vector_of_another_length_is_refused` |
| The wiring claim, leaf (`WiringEvalClaim::check_native`, `zk_config.rs:296-305`) and node (`wiring::verify_with`) | native evaluation | **deferred**: exported as public claim words (`bind_public_elems`, "a claim leaves the circuit unchecked but pinned"), batched by the parent (`pbatch.rs`), carried to the root and evaluated there (`recbench.rs` `ufinal`: own wiring, `claims[0..4]`, and `claims[4]`, `claims[5]` under `f0`, `fM`). Correct as read; G-1 says where it lives |
| Root keys `K0`, `KM` | native compare (`recbench.rs:2338`) | each merge asserts its children state its own `K0` and, for a merge child, its `KM` (`node.rs:586-590`) |
| Flags `f0`, `fM` | native read (G-2) | computed in circuit (`node.rs:575-593`) |
| Empty tape (`finalize`) | native | none (G-3) |
| Zero blend challenge or `gamma` | prover stops (VENDOR change 5) | completeness only; nothing to check |

## 3. Advice (values the circuit takes from the prover) and what pins each

| Advice | Pinned by |
|---|---|
| Prover messages, roots, openings, terminal codeword | absorbed into the in-circuit transcript; openings hashed to the roots |
| Inverses (`hints.rs`, `InvertOrZeroHint`) | the inverse gadget's constraints (the hint's own comment says the caller owes them; the gadget was not re-read here) |
| The batching step's `observe_one` elements (`pbatch.rs` `bind`) | asserted equal to the slots' claim elements (`pbatch.rs:228-232`) |
| The batching round coefficients `c0, c2` and finals `s_o` | absorbed before the challenge (C-3, C-2); final checks asserted (C-6) |
| The merge slot's key-digest wires | asserted equal to `KM` or `K0` of the child's public words by `f` (`recbench.rs:470-473`) |
| The kind flag `f` | `f AND NOT 1 = 0` (`recbench.rs:468`) |
| Query-group shared words (cap layers, fold challenges, terminal coset) and each group's index words | the stamp's links (`groups.rs`, `stamp::Layout::with_shared`); padded places past `q` repeat the last query (`groups.rs` `default_unit` comment): a free index there only adds a check |
| `n`, `host_rec`, `k`, `lift`, cell depths and counts (node statement) | the statement-digest computation (C-4 audit territory, not reviewed here) |

## 4. Refusal tests proposed (none of these exists under `tests/`)

| | Test | Expected |
|---|---|---|
| RT-B1 | Merge slot with `f = 2` (and `f = 3`) | witness unsatisfiable at `"f is 0 or 1"` |
| RT-B2 | Merge slot fed a level-0 child under `f = 1` (identifier from `KM`) | the child's transcript fails (wrong identifier) |
| RT-B3 | Merge whose merge child states a `KM` other than the node's | unsatisfiable at `child[c].KM[i]` |
| RT-B4 | Merge with `head f0 = 0` while a child is level 0 | unsatisfiable at `uniform.f0` |
| RT-B5 | Root whose carried level-0 claim is false (child honest except one carried claim word, re-proved) | native root refuses "the level-0 wiring claim" |
| RT-B6 | Root under a valid proof of an attacker's level-0 circuit (`K0` of that circuit) | native root refuses "a key word" (the present test flips a word and is refused by the transcript, not by the key compare) |
| RT-B7 | Native root on a flag word 2 | refused (after G-2's fix) |
| RT-B8 | Child proof with one trailing byte | the slot replay refuses (after G-3's fix) |
| RT-B9 | Leaf slot whose inner ciphertext and precommit key disagree in one element | unsatisfiable (the wrapper's deferred check) |

## 5. Not checked

`recursion/src/zk.rs` (the in-circuit zero-knowledge wrapper, 1,647 lines) line by line; the Merkle and BLAKE3
gadgets (`merkle.rs`, `merkle/blake3.rs`); `stamp.rs`'s link semantics beyond its head comment; the inverse
gadget; the node statement computation (C-4); the prover; any test run.
