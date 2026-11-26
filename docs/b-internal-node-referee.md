# Referee: System B internal nodes (parameters §21, P1–P4)

Object: `yugen-proof-b2` branch `agg` @ `a89652b` — `docs/parameters.md` §21.1 (4344–4420),
`src/bvirt.rs`, `tests/bvirt.rs`. Background: `design-b-aggregation.md`, `b-aggregation-referee.md`,
`lemma-tree-extraction.md`, spec 0.4.6 §15.2–15.3. Read only; `cargo test --release --features
recursion --test bvirt`: 6/6 pass (witness satisfaction via `populate_wire_witness`, no proving).

**Verdict: PASS WITH CONDITIONS.**

## 1. P1 deviation: E = H_int(0x01‖LE16(k_I)‖cells_1‖cells_2)

- Domain: `framed(0xbf, …)` = SHAKE256(`Yg 00 bf ‖ body`) (`src/sponge.rs:111`, `src/native.rs:40`).
  0xbf collides with no identifier in the code (`native.rs:20-28`, `native1.rs:14-18`,
  `bundle.rs:24-29`, all distinct); spec 0.4.6 has no 0xbf entry, so the reservation is still owed (C1).
- Framing: the body has fixed length per tag byte (0x01: 1+2+2·71 = 145 B; 0x00: 1+2+2·32 = 67 B,
  `bvirt.rs:80-103`); unused positions are 71/32 zero bytes, and `k_I` is in the body, so E for
  different `k_I` never shares a preimage; cells-E and leaves-E differ in tag byte and length. Unambiguous.
- Encoding caveat: `Stream::piece` (`sponge.rs:48-58`) does not truncate; a wire ≥ 2^(8n) XORs its high
  bits into the following bytes. depth (≤2), proofs (<2^17) and k_I are range-checked
  (`bvirt.rs:116-118`, `Count`); **`count_j` is not** (not in `internal_statement`, not in
  `merge_statement` `bundle.rs:418-429`). E and D_j alias identically (same encoder), and nothing uses
  `count` numerically, so no false statement follows, but the binding holds for the encoded bytes,
  not for the wire values. Pre-existing in BC-3; C2.
- Extraction: equality of raw words becomes collision resistance of one more framed SHAKE256 use.
  The extractor gets the cells from the top's witness and from the internal proof's witness, both
  preimages of the same E; distinct ⇒ an H_int collision. Same assumption family as H-BIND on D;
  not a weakening beyond adding H_int to the list the lemma names (C3). The trade-off is recorded
  (§21.1 4378-4384).

## 2. P2: same wires

Yes. `top_statement` (`bvirt.rs:147-164`) passes `halves[h]` to `commit_cells` and the same
`ChildCells` values (`children`, 162) to `bundle::merge_statement`; no copy. Positions agree:
merge reads the first k of [h0j0,h0j1,h1j0,h1j1]; with the canonical split those are exactly the
occupied ones in both E's. The internal node likewise hashes the wires it bounds and digests
(`bvirt.rs:113-121`); the slot-D equality is the caller's (test harness `tests/bvirt.rs:73-78`), C5.

## 3. P3: kinds and keys

`slot_kind` (`bvirt.rs:57-75`): Published ⇒ f∈{0,1}, key = K0/KM by f; Internal ⇒ f=2, key = KI. No
substitution either way given the identifier binds the key. Gaps:
- **Level-0 internal node has no key of its own.** `internal0_statement` is a different circuit from
  `internal_statement`, so a different verifying key, but the head and table (§21.1 4351-4357) carry
  one `KI`. A top0 slot under `Accept::Internal` checks `KI` and would refuse a real internal-0 proof,
  or if `KI` is reused it is ambiguous. Tag 0x00/0x01 prevents E confusion, not key confusion (C4).
- Head 14 → 18 words: `[E|K0|KM|KI|f0|fM]` = 4+4+4+4+2. K0/KM/KI are only sound if every node asserts
  its children's head keys equal its own and the final verifier pins them to constants; not in this
  code (slots not built). As written `KI` is a free word until that is shown (C5).
- auth_mode is not in E; it is a circuit constant in D_j (`bvirt.rs:119`), so one KI per mode. State it.

## 4. P4: split and counts

`split` (`bvirt.rs:127-140`): 1≤k≤4, k_L∈{1,2}, k_L+k_R=k, k_R∈{0,1,2}, k_R>0 ⇒ k_L=2. Solutions:
k=1→(1,0), 2→(2,0), 3→(2,1), 4→(2,2): unique, = `native::split`. Internal k_I∈{1,2} by `Count`
(0, 3 refused). Same `split` for the level-0 top (186). The `iadd` is mod 2^64 but k_L, k_R are
bounded small, no wrap. One published node ⇒ one B composition. Not covered: an internal node with
k_I=1 whose slot 2 holds an arbitrary proof is harmless (cells_2 zeroed in E, never read).
No published tree with two encodings found.

## 5. Node bound

Per merge 1 top + ≤2 internal; per virtual sub-bundle 1 top0 + ≤2 internal0; internal slots accept
only published kinds, top slots only internal, so no internal-over-internal chain: depth by kind is
bounded. 4/4/5: 4,096 leaves, 1,024 sub-bundles, 341 merges ⇒ 4,096 + 3·1,024 + 3·341 = 8,191. Right,
as an upper bound (k<3 drops the right internal). It is what the lemma needs (bound independent of
the `proofs` cell, well-founded order kind then depth), provided C4/C5 hold — the bound relies on
the key words, not the flag alone.

## 6. Tests

Circuit level (constraint satisfaction on the built statement parts), not native-only: P1 ×2, P2,
P4 genuinely exercise `internal_statement` / `top_statement` / `split`. Limits: P3 tests the
`slot_kind` gadget alone with keys as free witnesses (no slot verifier, no identifier); the slot-D
equality of P1 is in the test harness, not in `bvirt`; the level-0 pair has no test; no test of an
out-of-range `count` cell; no proving run.

## Conditions

1. Reserve 0xbf (B-private, internal commitment, both tag bytes 0x00/0x01) in the spec registry.
2. Range-check `count_j < 2^16` in `commit_cells`/BC-3, or state that binding is over the encoded bytes.
3. Add H_int (0xbf) to the collision-resistance assumptions the tree lemma names.
4. Give the level-0 internal node its own key (KI0, head 22 words) or merge `internal_statement` and
   `internal0_statement` into one circuit; update §21.1 table and the 8,191 argument.
5. When slots are built: the slot-D (P1) and slot-E (P2) equalities inside the node circuit, the head
   keys K0/KM/KI(/KI0) asserted equal parent-to-child and pinned at the root; a test that a proof
   under a foreign KI is refused.
6. Tests for `internal0_statement`/`top0_statement` refusals (P1–P4 analogues) before C2 sign-off.
