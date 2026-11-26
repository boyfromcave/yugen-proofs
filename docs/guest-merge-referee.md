# Referee report: the merge of seven, zk_mle, R-1, the k_q findings (yugen-proof-a b8b85af..15b9993)

Independent referee, 2026-11-19. Scope: the three commits `5ee82cb`, `877a13b`, `15b9993` of `yugen-proof-a`, read
with `git show 15b9993:<path>` and `git diff b8b85af 15b9993`. Nothing was built or run (section 7). Severities:
BLOCKER, MAJOR, MINOR, NOTE. Line numbers are at `15b9993`.

## 1. The merge program for seven children

**The identity.** `guests/e2/c_open.py:288-296` (and `vendor/leanMultisig/guests/lean_ethereum_e2.py:1788-1794`)
replace `mad2_into(acc, acc', G, 0, t0, t1, F, 0)` with `acc = G + F t0`, `acc' = F t1`. In the non-base branch the
argument order is `(c0, c1, a0, a1, b0, b1)` with `d = c + a b`, so the old call is `c = (G, 0)`, `a = (t0, t1)`,
`b = (F, 0)`. In `E2 = E[z]/(z^2 - beta)`, `(t0 + t1 z)(F + 0 z) = t0 F + t1 F z`: the `beta` term is `t1 * 0`, so the
identity is exact for every `beta`, with no reduction step involved. `F`, `G` are level-0 lanes already constrained
to K by `pack64x2` before the fold (`c_open.py:274-279`). `acc` is a `StackBuf`, so the two assignments are
write-once memory cells whose values are constrained by MUL/ADD rows. Each output cell is a polynomial identity in
the same inputs the MUL2 row constrained, so the two-row form accepts exactly the assignments the MUL2 row
accepted. No input that MUL2 refuses is accepted. **Verdict: sound.** The later rounds (`j > 0`) and the final check
`acc[2(interleave-2)] == P_final(x)` (`c_open.py:309-311`) did not change, and neither did any other query's check.

**Sharing and P-1/P-2.** The merge's shared stages run through `wi_query` / `wi_star_classes` (`guests/e2/j_wi.py`).
P-1 is now two compile-time refusals. The first is `j_wi.py:230-232`: `cut // nbits + nbits // (depth+1) +
1 // (cut+1) != 0` fails exactly when `cut >= nbits`, `nbits > depth` or `cut = 0`, which is the condition
`0 < cut < nbits <= depth` for non-negative integers. The second is `j_wi.py:294-296`: `cut != depth - cap_depth`.
Both are in the one guest source that both programs compile. P-2 (ii) is a runtime `assert!` in
`opening_placeholders` (`vendor/.../aggregation/src/placeholders.rs:1031-1040`). It is reached from `placeholders()`
(`:254`) on every compile of both programs, including `build_unchecked`. **Verdict: covered.**

- **NOTE N-1.** The P-2 assert adds `cap <= 8` and `padded` in the upper half of the cube. These are stronger than
  the guest's static checks, which is consistent. The two sources (`guests/e2/*.py` and the vendor guest) are
  edited identically, and nothing mechanical keeps them identical. Fix: a test that compares the two text
  ranges, or one generated from the other.

## 2. zk_mle at four pairs an iteration

`guests/e2/i_zk.py:438-469`. A stage has `2^(n-1-t)` pairs, which is always a power of two. When there are fewer
than 4 pairs (1 or 2), the loop is unrolled. Otherwise `quads = len/4` exactly, so no remainder ever occurs.
`zk_mle_stage` strides by 16 source cells (four pairs of two two-cell scalars) and by 8 destination cells, and
indexes `4k..4k+3` and `2k, 2k+1` for `k < 4`, the same cells as the one-pair loop. Each value is a `lerp` of
constrained source cells with `z`, and no value comes from a hint. **Verdict: no value from advice, and no check is
dropped at the boundaries. Lengths not divisible by four do not occur.**

## 3. P-1, P-2, R-1 in code

`bundle2::consensus_leaf` (`src/bundle2.rs:243-271`) is called in `Programs::build` (`:280`) and in `verify_checked`
(`:1018`). It requires the circuit's params to equal the canonical params of its mode (`pi_tag` included, and
`min_log_bytecode` free). It also requires the key's bytecode IV to equal the IV of `Key::new(circuit::build(canonical))`,
which is computed by the verifier and never read from the pair. `verify` also requires `Standing::Consensus`, which
only `build` sets. `build_unchecked` and the `*_for_tests` paths set another standing and are refused by `verify`.
**Verdict: through `verify` / `verify_tree` there is no public way to pair a non-canonical key with the consensus
verifier.** Two gaps remain, and neither is a soundness break:

- **MINOR M-1: the circuit's bytecode is unchecked, but it sets `leaf_kbc`.** `Programs::build_unchecked` takes
  `leaf_kbc` from `leaf.circuit.program` (`:322`), which `consensus_leaf` never compares (`Circuit` fields are
  `pub`, `src/circuit.rs:434-442`). *Attack:* a `Circuit` with canonical params and a program of another size makes
  consensus `Programs` whose in-circuit verifier has the wrong `LEAF_VARS`. Honest proofs then fail, so this is
  liveness at the builder, not acceptance. *Fix:* take `leaf_kbc` from `leaf.key.program()` after `consensus_leaf`,
  or have `consensus_leaf` compare the circuit's program with the canonical build.
- **MINOR M-2: the leaf passed to `verify` is not tied to the leaf passed to `build`.** `consensus_leaf` lets
  `min_log_bytecode` vary, and `verify` never compares the leaf's size with `programs.leaf_kbc`. A canonical leaf
  of another padded size reaches `verify_unchecked` and fails later, at an unclear point. *Fix:* store the canonical
  leaf (or its IV and size) in `Programs` at `build`, and refuse at `verify` any leaf that differs from it, or drop
  the parameter.

## 4. The k_q findings

All arithmetic was checked: `2*1184 + 1435*(1 + floor(log2(2*2^22))) = 2,368 + 34,440 = 36,808`; the calculator gets
`2*1086 + 34,440 = 36,612`; `log2(36,809/36,613) = 0.0077`.

**Calls or distinct inputs.** Theorem 6.6 assumes that "the verifier makes at most `k_q` hash queries". Definition
I.1 gives `k_q` as an upper bound on that number, and decision-qrom-counting 7.6 item 2 defines one query as "one
evaluation of one domain part on a whole input". So `k_q` bounds **calls by the verifier as built**, not distinct
inputs. Distinct inputs count only for a verifier that is built not to repeat a call.

- **MAJOR K-2': the wire verifier breaks the theorem's hypothesis as built.** Reading the proof from its bytes and
  then checking it makes 40,437 calls at row 9 `2^27` and 20,711 at row 8 mode 0 (parameters.md 2.2b). Both are above
  the derived `k_q` (36,808; 16,880) and above the calculator's figures. The consensus verifier reads bytes. The
  builder's argument (a repeated random-oracle query tells the caller nothing new) is plausible but unproved. The
  theorem counts calls, and in the QROM a re-query is not free to ignore without an argument. *Fix:* build the
  alternative the builder already names: check the pruned form directly, one call per distinct leaf and node, or
  memoise the decode's digests and feed them to `Transcript::merkle`. Then assert on the wire path that calls are at
  most `k_q`. Until then, either `k_q` takes the measured calls or the maths team signs off on the caching argument.
- **NOTE K-3.** One stream is made twice from one key, so there are `N_msg + 1` stream calls, which is still below
  `2 N_msg`. This is harmless to the bound. Remove the second call anyway, so that the in-circuit and native counts
  match.

**Is the message count fixed by the shape?** It is not. parameters.md 2.2b says so itself: "a proof announces its
tables' sizes and the rounds follow them, so the maximum over every accepted proof of a shape is NOT established".
`j_v` is measured at 580, 591 and 592 for different programs, and it follows the table sizes the prover announces.

- **MAJOR K-1': `N_msg`, and so `k_q`, is chosen by the prover within the shape.** The certified figure 36,808 is the
  value for one sample, not a bound. *Attack surface:* a prover that announces the largest table sizes the stack
  admits raises `N_msg`, and its proof's `k_q` goes above the figure used to certify. The `+0.0077`-bit
  argument therefore does not yet hold. *Fix:* either (a) pin each table's log size to the program in the verifier
  (refuse any other announced size), so that `N_msg` is a constant of (program, row), or (b) derive the maximum
  `N_msg` from the code path at the largest sizes each table admits under `stack_log2`, report that maximum as `k_q`,
  and have the calculator re-solve at it.
- **The builder's "no count moves; margin +0.247 covers +0.0077".** The arithmetic is right. The `+0.247` margin is
  at the built counts (383, …, 181). At the calculator's counts (382, …, 180) the margin is `+0.0979 - 0.0077 ≈
  +0.090`, which is the figure to quote. **"No count moves" holds only conditionally: K-1' and K-2' must be closed
  first**, and the merges of seven and merges of merges have to be re-reported at the maximum.

## 5. The re-recorded spBCS vector

`tests/vectors/spbcs-a-v1.txt`: only row 8's IV and statement changed. The IV is `bind_iv` =
`keccak("leanvm-params-v1" || program_iv || descriptor)` (`vendor/.../verifier/src/params.rs:445-453`). `descriptor()`
(`:396-433`) writes the id, the grinding bits, the folding factors, the reductions, the residual size, the leaf
salt, and **every query count of the table** (`ByShape`: each length and each count; `ByLevelRate`: the length and
each count), plus the challenge field and the transcript kind. **Verdict: yes, row 8's IV binds the query counts
and the row's parameters.**

- **NOTE N-2.** The descriptor does not list the zero-knowledge mask parameters field by field. They are bound
  only through `id`, which is enough while ids are never reused (`rows_are_distinct_and_bind_distinct_ivs`).

## 6. Verdicts

1. Sound. P-1 and P-2 cover the merge's sharing (N-1).
2. Sound.
3. Closed for acceptance, with M-1 and M-2 open.
4. Two MAJORs (K-1': prover-chosen `N_msg`; K-2': calls above `k_q` on the wire path). The builder's "no count
   moves" stays conditional on them.
5. Sound.

## 7. Not checked

No test, build or proof was run, and no worktree was made. I did not check `mad2_into`'s definition beyond the
argument order its call sites show, the compiler's lowering of `+` and `*` on cells to ADD/MUL rows, the
`docs/recursion.md` 10.000000 timings and table fits (F-11.1), `src/kq.rs`'s classification of permutations, the
seed re-pins, or task E. Sharp–Grubbs was read only through decision-qrom-counting §7, not from the paper.
