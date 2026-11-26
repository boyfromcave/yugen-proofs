# Yugen step 0.3: choice of proof frameworks A and B

Status: **decided** (SQ-23, 2026-11-18): the lead architect accepted system A = leanVM and system
B = Plonky3's binary stack; the prime-field (KoalaBear) configuration of Plonky3 stays the
documented fallback for B. The security target is now NIST category 1 with a parameter path to
category 3 (`docs/soundness-method.md` section 8); the parameter sets, sizes and verify times the
plan cites are in `docs/design-basis.md`, which supersedes section 7 below. Written 2026-11-18 in
`yugen-proofs`, which stays local (no remote). Plan references are to the Yugen plan, revision 6.

## 1. Decision

| | System A | System B |
|---|---|---|
| Framework | **leanVM** (`leanEthereum/leanMultisig`) | **Plonky3** with **Plonky3-recursion** (`Plonky3/Plonky3`, `Plonky3/Plonky3-recursion`) |
| Pin | commit `84780fb42667bc288c0e567c125b7e10479fb568` (2026-11-18) | Plonky3 commit `fe5e46d755b8a7d9069778361e21b33e5978b377` (crates `p3-*` `0.9.0-rc.2`, 2026-10-16); Plonky3-recursion commit `3a69ba61f713c8400b14eb3d8f0e52caa13512c7` (2026-10-17), which depends on `p3-*` `0.9.0-rc.2` |
| Configuration | GF(2^128) as a degree-2 extension of GF(2^64); WHIR over binary additive codes in the Johnson regime; VM arithmetization (six instructions, write-once memory); Keccak-f proven by GKR; Keccak-256 Merkle trees and transcript | Plonky3's native binary stack: GF(2^64) values (`Poly64`), multilinear AIR prover (`p3-multi-stark`, SuperSpartan-style), product buses, `KeccakBinaryAir`; leaf proofs with the hiding WHIR commitment, recursion layers with the folding (BaseFold-style) commitment; Keccak-256 Merkle trees and transcript |
| Licence | MIT or Apache-2.0 | MIT or Apache-2.0 (both repositories) |
| Runner-up | **Binius64** (`IrreducibleOSS/binius64`, `32ede490e8b6`, 2026-11-18) | **Plonky3 in its KoalaBear configuration** (31-bit prime field, octic extension, univariate STARK, FRI, `HidingFriPcs`) if the lead architect ranks field diversity above E2; as an independent codebase, **Stwo** (`starkware-libs/stwo` v2.3.0, development moved to `starkware-libs/proving`) |

The two pins share no proof-system code: leanVM's `Cargo.lock` contains no `p3-*` crate (checked
at the pin), and Plonky3 contains no leanVM crate. They differ in arithmetization (a VM against
AIR tables), in the Keccak argument (GKR against a Boolean AIR), in the commitment used by the
recursion layers (WHIR against folding), and in the representation of the binary field (leanVM's
own GF(2^64)/GF(2^128) code against Plonky3's `Poly64`/tower code). They share the field
characteristic (2), and both leaves rely on hiding WHIR for zero knowledge (section 8, risk R-4).

**The plan asks for a different field in B (§4: "for example FRI over a 31-bit field
extension").** This proposal departs from that for one reason: Keccak-only recursion over a
prime field is about 30 times slower per Keccak-f permutation than over a binary field on the
measurements in section 5, which puts E2 out of reach for a prime-field B (section 6). The
KoalaBear configuration of Plonky3 is kept as B's runner-up configuration, measured and
parameterized, so the lead architect can take the other side of that trade.

## 2. What Yugen needs from each system

Acceptance criteria for a framework, from plan §4, §9 and §11:

| # | Requirement | Test |
|---|---|---|
| R1 | Keccak/SHAKE is the only hash in the configuration used, including transcripts, Merkle trees and recursion | Configuration review; no algebraic hash type reachable from the verifier |
| R2 | NIST category 1 for the whole suite (`cat1`: 128 proven classical bits and 64 proven QROM bits for the four-layer chain, every Fiat–Shamir round at least 128 effective bits, 256-bit digests), with a category 3 parameter set (`cat3`), proven bounds only (no proximity-gap conjecture). Replaces "100 QROM bits" | `soundness/` (`--basis`) reports conditions C, Q, G and H met for every layer from bounds marked confirmed, or the gap is listed |
| R3 | Zero knowledge proven for the exact construction, or a clear route to it | A cited proof that covers the construction, plus a simulator test |
| R4 | Recursion: verify own proofs in-circuit with Keccak; leaf, bundle, two merge levels, about 1,500 leaves | A recursion layer that verifies a Keccak-committed proof exists at the pin |
| R5 | Proving on a phone and in WebAssembly | Builds for `aarch64` and `wasm32`; memory under 512 MB for the leaf |
| R6 | Permissive licence | MIT, Apache-2.0 or BSD |
| R7 | Active maintenance | Commits in the last month |
| R8 | Audit history | Published audits of the code at or near the pin |

## 3. Candidates surveyed

Read at the commits shown (shallow clones of each default branch on 2026-11-18, and primary web
pages); URLs in section 11.

| Candidate | Pin read | Licence | Field and commitment | Hash options | ZK at the pin | Recursion with Keccak at the pin | Soundness regime at the pin | Maintenance |
|---|---|---|---|---|---|---|---|---|
| leanVM / leanMultisig | `84780fb4` | MIT/Apache | GF(2^128) over GF(2^64); WHIR ("aka Ligerito") with affine combiners | Keccak-256 only | **None** (signature aggregation needs none) | **Yes**: 2-to-1 recursion is its core use; Keccak by GKR | Johnson regime, "no proximity gap conjecture", 125-bit round-by-round target, README states 62-bit QROM | Commits daily; README: "not (yet) production ready"; Lean formal statements in progress |
| Plonky3 (binary stack) | `fe5e46d7` / main `0d803737` | MIT/Apache | Binary tower GF(2^128), or `Poly64` with `Poly192` challenges; folding PCS or additive WHIR; multilinear AIR prover | Keccak-256, BLAKE3 | Reference-scale only ("binary reference ZK": trace log 1..8, width 1..16); HVZK-WHIR accounting module present | **Yes**: native Tower128 and Poly64 recursion with native Keccak tables (Plonky3-recursion `binary_fields.md`); non-hiding | `p3-security` crate: unique decoding, Johnson (proven), capacity (conjectured, opt-in) | Very active |
| Plonky3 (prime stack) | same | MIT/Apache | KoalaBear/BabyBear/Mersenne31/Goldilocks; FRI, STIR, WHIR; univariate STARK | Keccak-256, SHA-256, BLAKE3, Poseidon2 | **Yes**: `HidingFriPcs` + salted Merkle (`MerkleTreeHidingMmcs`), Lagrange-quotient masking bound of Haböck and Al Kindi, "A note on adding zero-knowledge to STARK", ePrint 2024/1037, Section 4.2, inequalities (16), (17) and Lemma 5 (verified against the paper 2026-11-19) | In-circuit Keccak-f and Keccak MMCS openings exist; **every built-in FRI recursion suite is Poseidon1/Poseidon2** (`SuiteIdV1`); a Keccak suite is not built | Same crate | Very active; Least Authority audit report in `audits/`; Fiat–Shamir advisory GHSA-vj64-rjf3-w3v7 (plan §16) |
| Binius64 | `32ede490` | MIT/Apache | GHASH GF(2^128); BaseFold/FRI-Binius; 64-bit word constraints (AND, MUL) | SHA-256, BLAKE3 (`HashSuite`); Keccak and SHA3 exist only as circuit gadgets | **Yes** via the Iron Spartan wrapper ("IronSpartan proofs are always zero-knowledge"); no paper found for the exact construction | Yes (`binius-recursion`, end-to-end test), **SHA-256 Merkle gadgets only** | Unique decoding: per-query error (1+rho)/2 (DP24 §5.2); `SECURITY_BITS = 96` | Commits daily |
| WHIR (`WizardOfMenlo/whir`) | `fe86de76` | MIT/Apache | PCS library only | generic | no | no (a PCS, not a prover) | per paper | Active |
| Stwo / StarkWare `proving` | v2.3.0; `proving` `c87ea10d` | Apache-2.0 | Mersenne31, circle FRI | Blake2s, Poseidon252, Keccak channel and Merkle | Blinding in the Cairo circuit stack (`zk_blinding_test.rs`) | Recursion through the Cairo verifier with Blake2s/Poseidon; no Keccak recursion | ethSTARK-style | Repository migrated to `starkware-libs/proving` (July 2026); production at StarkWare |
| RISC Zero | `5e1be36a` | Apache-2.0 | BabyBear FRI | SHA-256, Blake2b, Poseidon2 (recursion) | zkVM-level | Recursion uses Poseidon2 | ethSTARK-style | Active |
| SP1 (Hypercube) | `0cd151a8` | MIT/Apache | KoalaBear, multilinear, jagged PCS | Poseidon2 in recursion (`Poseidon2SP1FieldHasherVariable`) | zkVM-level | Recursion uses Poseidon2 | own analysis | Active; several audits in `audits/` |
| Jolt | `9def6087` | MIT/Apache | Dory, HyperKZG, Akita adapters | Keccak transcript | `jolt-zk` crate | elliptic-curve or lattice commitments | — | Active |
| TzEL (Stwo) | `a2302e21` | see repo | Stwo | — | — | — | README: "should not be assumed secure" (plan §16) | — |

Excluded at the first criterion: RISC Zero and SP1 (algebraic hash in recursion, R1), Jolt (no
hash-based commitment at the pin, R1/R2), the WHIR library (not a prover), TzEL (a deployment of
Stwo, not a framework).

## 4. Criteria matrix

Y = meets at the pin; W = work closes it in our tree or upstream; N = blocks. The work for each W
is in section 8.

| Criterion | leanVM (A) | Plonky3 binary (B) | Plonky3 KoalaBear (B-alt) | Binius64 (A runner-up) | Stwo (B runner-up) |
|---|---|---|---|---|---|
| R1 Keccak only | Y | Y | Y (leaf); W (recursion suite) | W (Keccak `HashSuite` and recursion Merkle gadget) | Y (leaf); N (recursion) |
| R2 `cat1` (and `cat3`), proven bounds | W (256-bit challenge field, query table as parameters) | W (`Poly192` reaches `cat1`; 256-bit challenges for the `cat3` path) | W (octic extension exists; 384-bit digests work at the pin, measured) | W (raise `SECURITY_BITS`, 192/256-bit challenges) | W |
| R3 ZK | **W, largest item** (none today) | W (reference only; HVZK-WHIR in progress upstream) | Y (`HidingFriPcs`) | Y in code; proof not found | W |
| R4 Keccak recursion | Y | Y (non-hiding, which recursion layers do not need) | W, and E2 is out of reach (section 6) | W | N |
| R5 phone and WebAssembly | W (no `wasm32` build seen; `no_std`-style verifier) | W (Keccak `wasm32_simd128` backend exists) | Leaf memory 1.7 GB measured with the wide Keccak AIR: N until a narrow AIR | W | W |
| R6 licence | Y | Y | Y | Y | Y |
| R7 maintenance | Y | Y | Y | Y | Y (moved repository) |
| R8 audit | N (none; formal verification under way) | Partial (Least Authority audit of earlier Plonky3; Plonky3-recursion "hasn't been audited yet") | Partial | Unknown; a 2026 report on unbound Fiat–Shamir claims named Binius64 (osec.io) | Production use at StarkWare |
| Arithmetic fit for Falcon (mod 12289) | Poor: native MUL is GF(2^128); mod-q products need table lookups | Poor: bit-level multipliers in a Boolean AIR | Good: q^2 < p, one field product per modular product | Good: native 64-bit MUL constraints | Good |
| Keccak cost | Best (GKR) | Good (Boolean AIR, 1,625 columns) | Poor (2,633 columns; per-query openings carry the full row) | Good (64-bit lanes) | Medium |

## 5. Measurements on this machine

Apple M5 (10 cores, 24 GB). Each run is the smallest Keccak-hashing proof the framework offers,
proved and then verified by the framework's own verifier. Raw output, with `uptime` before and
after, is in `bench/results/`. Load averages during the runs: 3.0 to 5.6 (beta4 builds in
parallel); below the briefing's limit of 8. Times are wall-clock means.

| System | Statement | Parameters | Proof size | Prove | Verify | Peak RSS |
|---|---|---|---|---|---|---|
| A leanVM | 128 chained Keccak-256 compressions, digest public | rate 1/2, 1 thread | 167,480 B | 0.060 s | 2.5 ms | not measured |
| A leanVM | same | rate 1/4, 1 thread | 119,824 B | 0.083 s | 1.9 ms | |
| A leanVM | same | rate 1/8, 1 thread | 101,828 B | 0.071 s | 1.8 ms | |
| A leanVM | same | rate 1/16, 1 thread | 91,608 B | 0.051 s | 1.6 ms | |
| A leanVM | same | rate 1/16, 4 threads | 91,608 B | 0.021 s | 1.6 ms | |
| B Plonky3 binary | 163 Keccak-f (4,096 rows x 1,625 bit columns) | folding PCS, rate 1/2, 100-bit target (reported 101.3), 1 thread | 434,434 B | 0.031 s | 4 ms | 24 MB |
| B Plonky3 binary | same | folding PCS, rate 1/4 | 314,427 B | 0.033 s | 3 ms | 26 MB |
| B Plonky3 binary | same | WHIR unique decoding, rate 1/2 (462 queries) | 283,161 B | 0.037 s | 3 ms | 24 MB |
| B Plonky3 binary | same | WHIR unique decoding, rate 1/8 (331 queries) | 247,324 B | 0.047 s | 3 ms | 36 MB |
| B Plonky3 binary | same | WHIR UD, GF(2^64) values, GF(2^192) challenges, rate 1/8 | 305,231 B | 0.187 s | 4 ms | 125 MB |
| B-alt KoalaBear | 128 Keccak-f (`KeccakAir`, 2,633 columns), ZK on | quartic ext., 256-bit digests, rate 1/2, 100 queries, 16-bit grind | 1,428,394 B | 0.694 s | 4.7 ms | 1.67 GB |
| B-alt KoalaBear | same, ZK on | octic ext., 384-bit digests, rate 1/16, arity 8, 110 queries, grinds 24/16/16 | 1,809,036 B | 4.25 s | 5.8 ms | 3.66 GB |
| B-alt KoalaBear | same, ZK on | as above with 199 queries (100 QROM bits under confirmed bounds, `soundness/`) | 3,080,009 B | 3.42 s (1 run) | 8.5 ms | 1.63 GB |
| A leanVM, leaf-sized | 128 compressions + 2^15 squarings, 589,976 cycles (stacked 2^24 by the size-model fit) | leanVM's parameters, rate 1/2 / 1/4 / 1/8 / 1/16, 1 thread | 290,584 / 202,664 / 170,628 / 153,688 B | 0.95 / 1.37 / 2.31 / 4.28 s | 3.0 / 2.3 / 2.2 / 2.0 ms | 0.89 / 1.30 / 2.12 / 3.63 GB |
| B Plonky3 binary, leaf-sized | 655 Keccak-f (2^14 rows x 1,625 bits = 2^24.67 bits) | WHIR UD, GF(2^128), 100-bit harness target, rate 1/2 / 1/4 / 1/8 / 1/16, 1 thread | 314,540 / 279,443 / 269,911 / 272,859 B | 0.15 / 0.16 / 0.20 / 0.27 s | 3 ms | 71 / 90 / 131 / 199 MB |
| B Plonky3 binary, leaf-sized | same | WHIR UD, GF(2^64) values, GF(2^192) challenges, rate 1/2 / 1/4 / 1/16 | 425,515 / 404,439 / 408,108 B | 0.73 / 0.73 / 0.92 s | 4 ms | 383 / 428 / 598 MB |

The leaf-sized rows (added for the design basis; `system-a-leafsize-20261118.txt`,
`system-b-binary-engineering-20261118.txt`) are proxies of the leaf's committed size, not the
Yugen statement. They show A's prover memory at 0.9 to 3.6 GB, over E1's 512 MB (R-14).

What the numbers say:

- leanVM's proofs have a floor of about 90 KB even for a tiny program at 125-bit classical
  parameters. Plonky3's binary stack is about 250 to 430 KB at 100 classical bits.
- The KoalaBear configuration is dominated by the width of `KeccakAir`: every FRI query opens a
  full 2,633-column row. A Yugen leaf in that configuration needs a narrow Keccak AIR (section 8,
  R-7) and still estimates at 0.7 to 1.3 MB at 100 QROM bits (section 7).
- Keccak throughput per core: Plonky3 binary 163 permutations in 31 ms (about 5,300/s);
  Plonky3 KoalaBear 128 in 694 ms (about 185/s, 29 times slower); leanVM's own README reports
  about 833,000/s on 12 M4 Max cores (about 70,000/s per core; read, not measured here).
- None of these runs used the Yugen statement. They establish that each pinned framework builds
  and proves Keccak with Keccak-only commitments on this machine, and they calibrate the size
  model in `soundness/` (within 15% for FRI, a 30% under-estimate for the binary folding PCS).

## 6. Statement size and recursion cost (estimates)

The statement is the 2-in/2-out wallet proof of plan §4. The constraint list in
`yugen-spec/spec/yugen-protocol.md` did not exist yet when this was written, so these counts are
derived from plan §4 and are replaced by counts from the specification in step 0.4.

**Keccak-f permutations** (Keccak-256 rate 136 bytes; personalization strings assumed 8 to 16
bytes):

| Use | Input bytes | Permutations |
|---|---|---|
| Two depth-20 4-ary Merkle paths | 4 x 32 + personalization and level, 144 | 2 x 20 x 2 = 80 |
| Note commitments (2 spent, 2 outputs) | about 140 | 4 x 2 = 8 |
| `nkc_d`, nullifier PRF, `rho_j` | under 136 | 6 |
| `auth_d` (Falcon-512 public key is 897 bytes) and `H("rk" ...)` | about 1,000 | 2 x 8 + 2 = 18 |
| Falcon hash-to-point, SHAKE256, fixed bound of 12 squeezes per signature | salt, transfer hash; 1,632 bytes out | 2 x 13 = 26 |
| **Total** | | **about 138** |

A finding for the specification: a 4-ary node with a personalization of 7 bytes or fewer fits
one Keccak-256 block (4 x 32 + 7 < 136), which halves the dominant term (80 to 40
permutations).

**Falcon-512 verification** (two signatures, one per spend, for one transfer shape): check
`s1 = c - s2*h mod (q, x^512 + 1)` and the norm bound. With in-circuit NTTs: three transforms of
2,304 butterflies plus 512 pointwise products, about 7,400 products mod q and about 15,000
14-bit range checks per signature, plus 1,024 squares for the norm. Committing `h` in NTT form
inside `auth_d` would remove one transform; that is a specification choice.

**Trace size per candidate** (leaf):

| System | Keccak part | Falcon part | Total committed |
|---|---|---|---|
| A leanVM | 138 `KECCAK` instructions (GKR; negligible) | modular products through table lookups in write-once memory, about 20 cycles per butterfly: about 2^18.2 cycles | about 2^19 cycles; leanVM commits about 2^4 elements per cycle, so 2^23 to 2^24 elements (`m0 = 24` used) |
| B Plonky3 binary | 138 x 25 rows x 1,625 bits = 2^22.4 bits | bit-level 14 x 14 multiply and reduce, about 1,000 bit cells per product: 2^24 bits | about 2^24.6 bits, 2^18.6 GF(2^64) elements (`m0 = 19` used) |
| B-alt KoalaBear | narrow lane-serial Keccak AIR, about 600 rows x 150 columns per permutation: 2^16.3 rows | one butterfly per row, 12 columns: 2^14 rows | height 2^17, about 200 main + 160 aux + 80 quotient base columns |

**Recursion** (bundle of 16 leaves, merge of 16 bundles, final merge of 6: 1,536 leaves):

- A: leanVM measures 2^18.7 cycles to verify two proofs. At Yugen parameters (twice the
  queries, 256-bit challenges emulated over GF(2^128) at about three products each) one
  verification is about 2^19.5 cycles; a bundle about 2^23.5 cycles, committing about 2^28
  elements.
- B: one verification hashes about 4 layers x 13 compressions x 94 to 199 queries, about 5,000
  to 10,000 Keccak-f, about 2^28 bits of `KeccakBinaryAir` trace; a bundle about 2^32 bits,
  2^26 to 2^28 elements.
- E2 throughput, from the per-core Keccak rates in section 5: B binary about 3,000 core-seconds
  for all layers, about 24 s on 8 machines of 16 cores; A about 1,800 core-seconds, about 14 s.
  B-alt KoalaBear: about 29 times B binary's Keccak cost, about 700 s, which fails E2's 60 s.
  These are estimates of the Keccak share only; step 0.5 measures them.

## 7. What 100 QROM bits costs (superseded)

**Superseded by the category 1 target**: `docs/design-basis.md` gives the parameter sets at
`cat1` and `cat3`. In short, at `cat1` under proven bounds the leaf is about 443 KiB (A) and 325
KiB (B), bundle proofs 589 KiB (A) and 850 KiB (B); GF(2^192) is the smallest challenge field
that reaches `cat1` and GF(2^256) the smallest for `cat3`; 256-bit digests suffice for `cat1` by
the attack rule (264 bits by the proven rule). The rest of this section is the step 0.3 record
at the old target.

Full derivation in `docs/soundness-method.md`; the tables are produced by `soundness/`
(`uv run yugen-soundness --target 100`).

The quantum Fiat–Shamir bound (Chiesa–Manohar–Spooner, ePrint 2019/834) is
`O(t^2 eps_rbr + t^3 / 2^lambda)` for `t` quantum queries. Three consequences, none of which the
plan's size targets account for:

1. **Every round needs about 201 bits of classical round-by-round soundness** (grinding
   included) for 100 QROM bits: Grover search for a bad challenge halves both. A challenge field
   of 2^128 cannot get there (an algebraic round's error is at least about 2/|F|), and neither
   can 2^192 at the unique-decoding radius (the fold error is n/|F|, about 2^-169). **Both systems
   need 256-bit challenges**: leanVM has only GF(2^128) and Plonky3's binary stack stops at
   `Poly192`; KoalaBear's octic extension (248 bits) exists at the pin.
2. **256-bit digests cap proof soundness at about 85 QROM bits** (`t^3 / 2^256`; 83.5 with the
   constant `24 t^3 / 2^lambda` read in ePrint 2019/834, Section 8.5.1, in the citation audit of
   2026-11-19, finding C-6). That is the same 85-bit figure plan §9 gives for hash collisions with
   quantum random-access memory. With **384-bit Keccak digests inside the proofs** the cap is 127
   (126.1 with the constant 24). This changes only proof-internal
   Merkle trees, not on-chain commitments.
3. **Proof sizes at 100 QROM bits are several times the plan's 55 KB.** Per-layer estimates,
   rate 1/16, 384-bit digests, 256-bit challenges:

| Layer | A, confirmed bounds only (UDR) | A, Johnson (DKT26, unconfirmed) | B, confirmed (UDR) | B, Johnson (unconfirmed) |
|---|---|---|---|---|
| Leaf | 1,075 KiB (queries 199, 184, 182 ...) | 333 KiB (94, 53, 37, 29, 23) | 576 KiB (199) | 300 KiB (94) |
| Bundle | 1,466 KiB | 423 KiB | 1,163 KiB | 590 KiB |
| Merge 1 | 1,466 KiB | 423 KiB | 1,163 KiB | 590 KiB |
| Merge 2 | 1,167 KiB | 370 KiB | 1,112 KiB | 563 KiB |
| Chain, QROM bits | 98.3 | 98.2 | 98.3 | 98.2 |

The B column uses the folding-PCS model, which under-estimated the measured binary proof by
about 30% (section 5); a WHIR leaf for B would sit near A's numbers. B-alt KoalaBear leaf: 1,325
KiB (confirmed) and 674 KiB (Johnson). At the plan's other reading (128 classical bits, 64 QROM
bits) the Johnson-regime leaf is about 220 KiB for A and 200 KiB for B.

A four-layer chain loses 2 bits to the union bound; to keep 100 bits end to end, each layer
targets 102.

**E1's 60 KB threshold cannot be met at 100 QROM bits by any candidate surveyed; E2's 1.5 MiB
per bundle proof can, in the Johnson regime.** That is a plan correction (section 10).

## 8. Risks and the work that closes each

| # | Risk | Work that closes it | Step |
|---|---|---|---|
| R-1 | leanVM has no zero knowledge | Add hiding to leanVM's leaf: salted Merkle leaves (32-byte salts) in every WHIR tree, masking polynomials for the WHIR commitment following Chiesa, Fenzi, Weissenberg, "Zero-Knowledge IOPPs for Constrained Interleaved Codes", ePrint 2026/391 (read 2026-11-19 in its revision of 2026-11-16: Section 11; what was built is W-I, `zk-hiding-commitment.md` 3.4 and 6), a masked sumcheck for the zerocheck and Keccak GKR, and masked bus columns; then a simulator test and the external cryptographer's review (E3). Done in a Yugen fork crate (`a-leanvm-zk`), proposed upstream only by the lead architect | 0.4, 0.6 |
| R-2 | A's challenge field GF(2^128) cannot reach `cat1` under proven bounds (algebraic rounds give about 100 bits against 136 needed; grinding the gap costs 2^35 to 2^46 Keccak-f per proof); B's `Poly192` reaches `cat1` but not `cat3` | A: GF(2^256) as a degree-2 extension of leanVM's GF(2^128) for every verifier challenge, with the VM's recursion verifier emulating it. B: a degree-4 extension of `Poly64` (or a 256-bit tower level) as the challenge field, so that `cat3` is a parameter change; until then B runs `cat1` on `Poly192`. Acceptance: `soundness/ --basis` passes C, Q, G, H for every layer with the shipped tables | 0.4 |
| R-3 | Digest length per target: 256 bits for `cat1` (attack rule; proven rule 264), 384 for `cat3` (proven 392) | Both systems take the digest length as a parameter: 256-bit Keccak for `cat1`, Keccak[c=768] with 48-byte output for `cat3`; Plonky3's `PaddingFreeSponge<KeccakF, 25, 17, 6>` already works (measured, section 5); leanVM's `keccak256` crate gains a 384-bit variant behind the same interface | 0.4 |
| R-4 | Both leaves would take ZK from the same construction (HVZK-WHIR) | Acceptable for soundness diversity (ZK protects privacy, not supply), recorded as a decision for the lead architect; alternatively B's leaf uses the folding PCS with its own masking | 0.4 |
| R-5 | leanVM's 125-bit claim rests on the affine-combiner bound (CWYZ26, ePrint 2026/2863, read 2026-11-19); under BCIKS20 alone its shipped queries give 31 classical bits, under DKT26 (Theorem 4.4, read) 86 | leanVM's Definition `epsaff` was checked against CWYZ26 Theorem 4.10, eq. (4.13), and the packing step of Theorem 5.2 (`CITATION-AUDIT.md` C-19); remaining: the external cryptographer checks leanVM appendix B's own RBR theorem (`doc/leanvm/body/b-polynomial-commitment-scheme.tex`), and `soundness/` implements `eps_aff` with a test against CWYZ26's worked example (Remark 5.3: about 125.42 bits at `n = 2^20`, `q = 2^128`) | 0.6 (E3) |
| R-6 | Falcon arithmetic is a poor fit for both binary systems | A: mod-q products by quarter-square tables in write-once memory, range checks by lookup; B: a dedicated 14-bit multiply-reduce AIR with product-bus range checks. Both checked against `yugen-falcon` known-answer vectors, both receiving the same witness | 0.4 |
| R-7 | B-alt KoalaBear proofs are dominated by `KeccakAir`'s 2,633 columns | Only if B-alt is chosen: a lane-serial Keccak AIR with byte lookups, under 200 columns | 0.4 |
| R-8 | No pinned candidate is audited at the pin; Plonky3-recursion "hasn't been audited yet"; leanVM "not production ready" | Assurance A1 (plan §9): two circuit audits, constraint-mutation testing, differential fuzzing between A and B; pins move only by a reviewed bump with the soundness tables regenerated | 1.14 |
| R-9 | Plonky3's binary recursion is non-hiding; leaf audit-feed proofs are published anyway | Recursion layers need no ZK (they only carry proofs that are public on the audit feed); the leaf is hiding (R-1, R-4). Recorded in the specification | 0.4 |
| R-10 | Fiat–Shamir binding bugs of the class of GHSA-vj64-rjf3-w3v7 | Both statements absorb the verification key, the circuit identifier and every public input before the first challenge; a transcript test per system that flips each public byte and expects rejection | 0.4 |
| R-11 | WebAssembly and phone builds not shown for either system | Build both provers for `wasm32-unknown-unknown` and `aarch64-linux-android`; measure the leaf in E1 | 0.4 |
| R-12 | Upstream churn at both pins (both commit daily) | Pins by commit hash in `Cargo.toml` and `Cargo.lock`; a bump is a reviewed change that reruns E1, E2 and the soundness tables | ongoing |
| R-13 | E1's 60 KB size threshold is unreachable at any target with proven bounds (`cat1` leaf about 325 to 443 KiB) | Restate E1 from `docs/design-basis.md` (leaf at most 512 KiB at `cat1` per system) and replace the estimate with the E1 measurement | SQ-23, E1 |
| R-14 | leanVM's prover memory: 0.9 GB (rate 1/2) to 3.6 GB (rate 1/16) for a leaf-sized trace, measured; E1 allows 512 MB | A memory-bounded leaf prover in `a-leanvm`: commit the stacked polynomial in streamed chunks (Merkle leaves hashed as produced), drop the trace once encoded, rate 1/4; acceptance: peak RSS under 512 MB on the leaf in E1, measured with `/usr/bin/time -l` and on a phone | 0.4, E1 |
| R-15 | leanVM's WHIR schedule, grinding bits and query table are compile-time constants (`crates/verifier/src/whir.rs`), so a `cat1` to `cat3` move would be a code change | `a-leanvm` reads (fold schedule, rates, queries, grinding, digest length) from one parameter table per target, versioned and absorbed into the transcript; both systems verify against the table the release names; acceptance: switching the table from `cat1` to `cat3` changes no code and `soundness/ --basis` regenerates it | 0.4 |

## 9. Layout for step 0.4

```
yugen-proofs/
  statement/              crate yugen-statement: the single constraint list, parsed from
                          yugen-spec (constraint IDs, hash personalizations, input lengths),
                          and the one witness generator (uses yugen-ref and yugen-falcon)
  falcon-gadget-spec/     the Falcon verification as integer operations with bounds: NTT
                          schedule, quotient bounds, norm accumulation; consumed by both systems
  a-leanvm/               system A: zkDSL sources (statement.py, falcon.py, merkle.py),
                          the host crate that fills hints from the witness generator, recursion
                          programs (bundle.py, merge.py); depends on leanVM at the pin
  a-leanvm-zk/            the hiding additions to leanVM (R-1), kept as a fork crate
  b-plonky3/              system B: AIR tables (falcon_ntt, mod_q_mul, range, merkle4, note),
                          Keccak through KeccakBinaryAir, buses binding them; recursion layers
                          on Plonky3-recursion's native binary owners
  verifier/               (P1a step 1.1) the no_std verifier crate for both leaf verifiers
  conformance/            constraint-coverage, mutation and differential tests across A and B
  soundness/              step 0.6 calculator (this commit)
  bench/                  step 0.3 benchmarks (this commit)
```

**How the single constraint list maps into each system.**

- The specification gives each constraint an identifier and a class: hash (with personalization
  and fixed input length), Merkle step, linear relation, range check (bits), modular product mod
  q, NTT butterfly, norm accumulation, equality to a public input, branch selector (Falcon or
  recovery key). `yugen-statement` loads that list and exposes it as data.
- Each system implements one emitter per class, not per constraint: `a-leanvm` emits zkDSL
  functions, `b-plonky3` emits rows in the matching AIR table and the bus messages that bind them.
  Each emitted gadget records the constraint IDs it enforces.
- `conformance/` fails the build if any ID in the list is enforced by no gadget in either
  system, or by a gadget the list does not name.
- One witness generator produces every value both systems use, including the NTT intermediate
  values, quotients and range-check limbs. Each system's prover only lays the witness out.
- Mutation testing (plan §9, A1) runs on IDs: for each ID, drop its gadget in one system and
  require a test witness that the mutated circuit accepts and the specification rejects.
- Every valid and invalid test vector from `yugen-spec/vectors` must get the same answer from
  both verifiers (plan §9 "the two circuits drift apart").

**Where the Falcon gadget goes.** The bounds (coefficient ranges, quotient ranges, the
hash-to-point iteration bound, the norm bound 34,034,726 for Falcon-512, from memory and to be
checked against the Falcon specification and `yugen-falcon`) live once in `falcon-gadget-spec`.
The gadget is the NTT form: the witness supplies NTT(s2), NTT(h) and the quotients; every
butterfly is checked as `a + w*b = a' + q*k` with `k` range-checked, which never wraps either
field. The challenge drawn after the witness is committed (plan §4) is used for the bus and
lookup arguments; the Falcon arithmetic itself is checked exactly, not by evaluation at a point,
because in characteristic 2 an integer identity cannot be checked by evaluation.

**Tasks with acceptance criteria for 0.4:**

| Task | Done when |
|---|---|
| `yugen-statement` loads the specification's constraint list and generates witnesses | Reproduces `yugen-spec` test vectors byte for byte |
| Falcon gadget in A and B | Accepts every valid `yugen-falcon` known-answer signature, rejects every mutated one, in both systems |
| Full wallet statement in A and B | E1 measured; conformance coverage at 100% of constraint IDs |
| R-1, R-2, R-3 for the leaf | `soundness/` shows at least 102 QROM bits for the leaf with the shipped configuration; the simulator test passes |

## 10. Findings for the lead architect (plan corrections)

1. **§9 and §11 E1:** "about 55 KB per wallet proof" and "60 KB or less" are not reachable at
   100 QROM bits counted with the query loss of ePrint 2019/834 (section 7). Leaf estimates are
   300 to 1,100 KiB per system depending on which proximity bounds the external review accepts;
   even at 128 classical bits (64 QROM) about 200 KiB. §5 and §8 sizes follow from E1 and need
   restating once it runs.
2. **§9:** "Proof soundness 100 bits" needs a definition. Under the CMS19 bound it means about
   200 bits of classical round-by-round soundness per round; with 256-bit digests it is capped at
   85 bits (83.5 with CMS19's constant 24, C-6), the same as the hash-collision row. Proposed: 384-bit digests inside proofs and
   256-bit challenge fields (decision with SQ-22).
3. **§4 "System B ... a different field":** proposed binary for B as well (section 1), because a
   prime-field Keccak-only recursion misses E2 by about an order of magnitude. Decision for the
   lead architect (SQ-23).
4. **§4 Merkle tree:** a 4-ary node with a personalization of at most 7 bytes costs one
   Keccak-f instead of two; a note for `yugen-spec`.
5. **§16:** the leanMultisig entry says "128-bit ROM (64-bit QROM)"; at the pin the README says
   125-bit ROM and 62-bit QROM, and the system is called leanVM.
6. **Category 1 target (2026-11-18), plan line 41 and SQ-8/SQ-22:** the definition needs two
   corrections (`docs/soundness-method.md` 8.2): the 2^64-Grover condition is, in NIST's
   depth-limited model, "every Fiat–Shamir round has at least 128 effective bits" (and it is
   implied by the 128 proven classical bits); and 256-bit digests give 126.6 proven classical
   bits per layer, so "128 classical bits from proven bounds" holds for the IOP term, while the
   hash term meets category 1 by NIST's own collision benchmark (264-bit digests if it must be
   proven). Plan §9's risk table (line 716) still says "100 bits, as the target".
   *Revision note (2026-11-19, calculator revision 10):* under the spBCS theorem's own hash term
   (Sharp, Grubbs, ePrint 2026/2615, Theorem 6.6 (2)) summed over a 20,000-proof tree the proven
   classical level is 114.74 bits, not 126.6, and a proven 128 needs 288-bit digests, not 264
   (`decision-qrom-counting.md` 7).
   *Amendment (2026-11-19, calculator revision 10.2, after `docs/tree-extraction-referee.md`; not a rewrite):* every TREE figure in this passage is conditional, not an unconditional theorem. It holds under the recursion heuristic C2 (the event "accepted in-circuit, rejected natively" does not occur; no random-oracle proof can remove it), the owed obligations K-A and K-B (round-by-round knowledge soundness) and T-1 (the transcripts' domain separation and fit to [SG26] Protocol 6.5). Under Theorem TE' (`docs/lemma-tree-extraction.md` revision 2) the classical hash level of the tree is **121.89 bits at category 1** (185.89 / 249.89 at categories 3 / 5), printed with the per-proof union (114.74 / 178.74 / 242.74) beside it as the comparison; the tree's QROM figures are derived under C2, never "proven QROM". Status of every claim: `docs/what-is-proven.md`.
7. **§9 / §11 E1:** leaf size at `cat1` is about 325 KiB (B) to 443 KiB (A) under proven bounds,
   and leanVM's prover needs 0.9 GB or more for a leaf-sized trace (R-14).
8. **§11 E2:** bundle proofs at `cat1` are 589 KiB (A) and 850 KiB (B), within 1.5 MiB; at
   `cat3` B's folding-PCS bundle is 1,507 KiB with grinding and 1,640 KiB without, at or over the
   limit (WHIR in B's recursion would give 1,388 / 1,521 KiB).

## 11. Sources

Repositories (read at the pins named in section 3):

- leanVM: https://github.com/leanEthereum/leanMultisig (README; `crates/verifier/src/whir.rs`,
  `transcript.rs`; `doc/leanvm/body/b-polynomial-commitment-scheme.tex`)
- Plonky3: https://github.com/Plonky3/Plonky3 (README; `security/`; `docs/caller-obligations.md`;
  `fri/src/hiding_pcs.rs`; `examples/examples/prove_hash_binary.rs`)
- Plonky3-recursion: https://github.com/Plonky3/Plonky3-recursion (README;
  `book/src/advanced_topics/binary_fields.md`; `recursion/src/builtin_config/registry.rs`)
- Binius64: https://github.com/IrreducibleOSS/binius64 (ARCHITECTURE.md; `crates/verifier/src/verify.rs`;
  `crates/iop/src/fri/common.rs`; `crates/recursion/src/merkle.rs`); https://www.binius.xyz/blueprint
- Stwo: https://github.com/starkware-libs/stwo and https://github.com/starkware-libs/proving
- RISC Zero: https://github.com/risc0/risc0; SP1: https://github.com/succinctlabs/sp1;
  Jolt: https://github.com/a16z/jolt; WHIR: https://github.com/WizardOfMenlo/whir;
  TzEL: https://github.com/trilitech/tzel
- crates.io API for `p3-uni-stark` and `p3-recursion` versions

Papers: see `docs/soundness-method.md`, "Sources", for status of each.

- Unfaithful Fiat–Shamir claims across zkVMs, including Binius64 (secondary, search result
  only): https://osec.io/blog/zkvms-unfaithful-claims/

## 12. Claims not confirmed from a primary source

- leanVM's Keccak throughput (833,000 permutations/s) and recursion timings: read from its
  README, not measured here.
- The statement-size estimates in section 6 (cycles per butterfly, bit cells per product,
  rows per narrow Keccak permutation, committed elements per cycle, recursion verification
  costs) are engineering estimates, to be replaced by E1 and E2.
- Binius64's ZK construction: at the time of writing no paper or blueprint page was found. Since then: the Blueprint of 2026-11-16 (sections 6, 7) and Diamond, "Zero-Knowledge Polynomial Commitment in Binary Fields", ePrint 2025/1015 (read 2026-11-19), which gives the full-mask zero-knowledge BaseFold opening (Construction 4.1) that the Blueprint's opening builds on.
- The Falcon-512 norm bound 34,034,726 and the hash-to-point sampling rule (16-bit samples,
  accept below 5q): from memory of the Falcon specification.
- WebAssembly and phone suitability of either system: not tested.
- The sources marked unconfirmed in `docs/soundness-method.md` (WHIR Theorem 5.2 terms,
  DKT26, CWYZ26, CMS19 constants, the grinding arguments). Since read (2026-11-19): WHIR, CMS19,
  DKT26, CWYZ26 and ethSTARK (F4); what remains is listed in `CITATION-AUDIT.md` section 4.
