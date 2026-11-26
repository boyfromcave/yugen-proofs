#!/usr/bin/env python3
"""The count root of the memory argument with one free leaf (docs/zk-system-a-gaps.md, section 1).

System A's bus publishes two scalars: R, the one root of the push and the pull tree, and R_c, the
product of every leaf of the count tree, checked only to be nonzero. A count leaf is the count
column's cell of an executed row, g^t for the t-th read of an address (g the generator of K*), and
1 on padding. So R_c = g^(sum of the exponents), an element of K*, a function of the witness.

Construction G-1: one leaf of the count tree, at a fixed public padding position, holds a committed
uniform nonzero mask e. The published value is R_c * e.

Part A (zero knowledge, exact, all values of e). K = GF(4) inside F = GF(16).
  - e uniform on F* (an element of the mask column): R_c e is uniform on F* for every R_c in F*.
  - e uniform on K* (one K word): R_c e is uniform on K* for every R_c in K*.
  - controls: no leaf; an additive mask; e uniform on K* with a root outside K*; e also published.
Part B (soundness, exhaustive). The memory argument of leanVM's lookup protocol over K = GF(4)
(g of order 3; the theorem needs fewer than 3 reads), two cells, two reads:
    push: seeds (g^i, 1, lut[i]) and (a_j, g c_j, v_j);  pull: (a_j, c_j, v_j) and (g^i, fin_i, lut[i])
    accept iff the two multisets are equal and the published count value is nonzero.
  Enumerated over every (a, c, v) of both reads and every final count: with the leaf, for every
  e != 0, the accepted set is the accepted set without the leaf, and every accepted assignment has
  only correct reads; e = 0 accepts nothing. Controls: without the nonzero check a forged read is
  accepted; an additive mask R_c + e accepts forged reads; three reads (the bound violated) forge.

Run: python3 test_count_root.py
"""
import itertools
import sys
from collections import Counter

from gf import GF
from gaps_common import emitter, tv

F = GF(4)                                    # GF(16)
KSTAR = [x for x in range(1, 16) if F.pow(x, 3) == 1]      # the subfield GF(4) without 0: {1, 6, 7}
G = KSTAR[1]                                 # a generator of K*
FSTAR = list(range(1, 16))


def root(counts):
    r = 1
    for t in counts:
        r = F.mul(r, F.pow(G, t))
    return r


def part_a(emit):
    ok = True
    # every multiset of read exponents for up to 4 reads: the honest roots
    roots = sorted({root(c) for n in range(5) for c in itertools.product(range(3), repeat=n)})
    emit(f"honest count roots (products of powers of g): {roots} = K* = {sorted(KSTAR)}")
    ok &= roots == sorted(KSTAR)
    laws_F = [Counter(F.mul(r, e) for e in FSTAR) for r in roots]
    laws_K = [Counter(F.mul(r, e) for e in KSTAR) for r in roots]
    uni_F, uni_K = Counter(FSTAR), Counter(KSTAR)
    a = all(l == uni_F for l in laws_F)
    b = all(l == uni_K for l in laws_K)
    emit(f"leaf uniform on F*: R_c e uniform on F* for all {len(roots)} roots: {a}")
    emit(f"leaf uniform on K*: R_c e uniform on K* for all {len(roots)} roots: {b}")
    ok &= a and b
    # every root of F* under an F* leaf (a prover whose counts leave K changes nothing for hiding)
    c = all(Counter(F.mul(r, e) for e in FSTAR) == uni_F for r in FSTAR)
    emit(f"leaf uniform on F*, any nonzero root in F: uniform on F*: {c}")
    ok &= c
    # controls
    d0 = max(tv(Counter([r]), Counter([s])) for r in roots for s in roots)
    emit(f"control, no leaf: distance between two witnesses with different roots: {d0}")
    add = [Counter(r ^ e for e in FSTAR) for r in roots]
    d1 = max(tv(x, y) for x in add for y in add)
    emit(f"control, additive mask R_c + e, e uniform nonzero: largest distance {d1}")
    out = [x for x in FSTAR if x not in KSTAR][0]
    d2 = tv(Counter(F.mul(out, e) for e in KSTAR), uni_K)
    emit(f"control, K-word leaf with a root outside K*: distance from uniform on K*: {d2} (a coset of K*)")
    pub = [Counter((F.mul(r, e), e) for e in FSTAR) for r in roots]
    d3 = max(tv(x, y) for x in pub for y in pub)
    emit(f"control, the leaf also published in clear: largest distance {d3}")
    # the leaf's own contribution to the leaf claim is linear and goes into a later head (no value is sent)
    ok &= d0 == 1 and d1 > 0 and d2 == 1 and d3 == 1
    return ok


K4 = GF(2)                                   # the memory argument's field K = GF(4), g = 2 of order 3
g = 2
LUT = [1, 3]                                 # lut[i], addresses g^0 = 1, g^1 = 2
ADDR = [1, 2]


def balanced(reads, fin):
    push = Counter((ADDR[i], 1, LUT[i]) for i in range(2))
    pull = Counter((ADDR[i], fin[i], LUT[i]) for i in range(2))
    for a, c, v in reads:
        push[(a, K4.mul(g, c), v)] += 1
        pull[(a, c, v)] += 1
    return push == pull


def correct(read):
    a, c, v = read
    return any(a == ADDR[i] and v == LUT[i] for i in range(2))


def count_root(reads):
    r = 1
    for _, c, _ in reads:
        r = K4.mul(r, c)
    return r


def part_b(emit):
    ok = True
    cells = list(itertools.product(range(4), repeat=3))
    acc_plain, acc_leaf = set(), {e: set() for e in range(4)}
    forged_plain = forged_leaf = no_check_forged = additive_forged = 0
    total = 0
    for reads in itertools.product(cells, repeat=2):
        rc = count_root(reads)
        bad = not all(correct(rd) for rd in reads)
        for fin in itertools.product(range(4), repeat=2):
            total += 1
            if not balanced(reads, fin):
                continue
            no_check_forged += bad
            if rc != 0:
                acc_plain.add((reads, fin))
                forged_plain += bad
            for e in range(4):
                if K4.mul(rc, e) != 0:
                    acc_leaf[e].add((reads, fin))
                    forged_leaf += bad
                if e and (rc ^ e) != 0:
                    additive_forged += bad
    same = all(acc_leaf[e] == acc_plain for e in (1, 2, 3))
    emit(f"memory argument, K = GF(4), 2 cells, 2 reads: {total} assignments, {len(acc_plain)} accepted without the leaf")
    emit(f"with the leaf: accepted set equal to the plain one for each of the 3 nonzero e: {same}; "
         f"accepted with e = 0: {len(acc_leaf[0])}")
    emit(f"forged reads accepted: plain {forged_plain}, with the leaf (all e) {forged_leaf}")
    emit(f"control, no nonzero check: {no_check_forged} balanced assignments contain a forged read")
    emit(f"control, additive mask (accept iff R_c + e != 0): {additive_forged} forged acceptances over the nonzero e")
    ok &= same and len(acc_leaf[0]) == 0 and forged_plain == 0 and forged_leaf == 0
    ok &= no_check_forged > 0 and additive_forged > 0
    # control: three reads at an address/value that is no entry, counts 1, g, g^2: the read bound is violated
    reads = [(3, c, 0) for c in (1, 2, 3)]
    push = Counter((ADDR[i], 1, LUT[i]) for i in range(2))
    pull = Counter((ADDR[i], 1, LUT[i]) for i in range(2))
    for a, c, v in reads:
        push[(a, K4.mul(g, c), v)] += 1
        pull[(a, c, v)] += 1
    cyc = push == pull and count_root(reads) != 0
    emit(f"control, 3 = |K*| reads forming a cycle of counts at a non-entry: accepted: {cyc} "
         f"(the read bound, not the leaf, excludes it; unchanged by the leaf)")
    ok &= cyc
    return ok


def main():
    emit, lines = emitter()
    emit("# count root with one free leaf: part A, zero knowledge (K = GF(4) in F = GF(16))")
    ok = part_a(emit)
    emit("# part B, soundness of the memory argument with the leaf (exhaustive)")
    ok &= part_b(emit)
    emit("RESULT: " + ("PASS" if ok else "FAIL"))
    with open("results/count_root.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
