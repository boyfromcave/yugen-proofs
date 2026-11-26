#!/bin/sh
# Design-basis measurements for system B (Plonky3 native binary @ fe5e46d7): proof-size
# engineering knobs at a leaf-sized trace (2^14 rows x 1,625 Boolean columns = 2^24.7 bits,
# 655 Keccak-f). One prover thread, nice 10. Raw output to stdout; the caller saves it under
# bench/results/. Harness security accounting (GF(2^128), its own target) holds every run at
# sec=100 so that only the knob varies.
set -eu
BIN=${BIN:-$(dirname "$0")/../../target/release/yugen-bench-b-plonky3-binary}
export RAYON_NUM_THREADS=${RAYON_NUM_THREADS:-1}
LOGH=${LOGH:-14}
run() {
  echo "## args: $*"
  nice -n 10 /usr/bin/time -l "$BIN" "$@" 2>&1 | grep -E "^system|Proof size|Prove time|Verify time|Composed|PCS:|WHIR opened|WHIR cap|Merkle leaf|maximum resident" || echo "FAILED: $*"
}
echo "# run $(date '+%Y-%m-%d %H:%M %Z')"
echo "# uptime before: $(uptime)"
sysctl -n machdep.cpu.brand_string
echo "### 1. rate sweep, folding PCS, fold 4, arity 4"
for r in 1 2 3 4; do run pcs=folding logh=$LOGH rate=$r fold=4 arity=4; done
echo "### 2. rate sweep, WHIR unique decoding, arity 2"
for r in 1 2 3 4; do run pcs=whir regime=ud logh=$LOGH rate=$r fold=4 arity=2; done
echo "### 3. fold sweep, folding PCS, rate 1/4, arity 4"
for f in 1 2 3 5 6; do run pcs=folding logh=$LOGH rate=2 fold=$f arity=4; done
echo "### 4. Merkle arity, folding PCS, rate 1/4"
run pcs=folding logh=$LOGH rate=2 fold=4 arity=2
echo "### 5. query grinding sweep, folding PCS, rate 1/4"
for p in 8 16 20 24; do run pcs=folding logh=$LOGH rate=2 fold=4 arity=4 pow=$p; done
echo "### 5b. query grinding, WHIR UD, rate 1/16"
for p in 0 16 20; do run pcs=whir regime=ud logh=$LOGH rate=4 fold=4 arity=2 pow=$p; done
echo "### 6. Merkle leaf width, folding PCS, rate 1/4"
for l in 4 64 256; do run pcs=folding logh=$LOGH rate=2 fold=4 arity=4 leaf=$l; done
echo "### 7. WHIR Johnson regime (proven Johnson radius, harness accounting)"
for r in 1 2 4; do run pcs=whir regime=jb logh=$LOGH rate=$r fold=4 arity=2; done
echo "### 8. WHIR UD with GF(2^64) values and GF(2^192) challenges"
for r in 1 2 4; do run pcs=whir-gf192 regime=ud logh=$LOGH rate=$r fold=4 arity=2; done
echo "### 9. trace-size scaling, folding PCS, rate 1/4, fold 4, arity 4"
for h in 12 13 15 16; do run pcs=folding logh=$h rate=2 fold=4 arity=4; done
echo "### 10. sumcheck grinding 8 bits per round, folding PCS, rate 1/4"
run pcs=folding logh=$LOGH rate=2 fold=4 arity=4 scpow=8
echo "# uptime after: $(uptime)"
