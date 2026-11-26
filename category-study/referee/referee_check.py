"""Referee recomputation for docs/security-category-referee.md (the Ycash developers, 2026).

Independent of category_study.py: closed forms for the needs, system B's unique-decoding counts, the field sizes,
the QROM digest floor and the capacity; the calculator (revision 6, unchanged) is used only to read system A's
round list and to test that each of A's counts is minimal (one less fails).
Run: cd soundness && uv run python ../category-study/referee/referee_check.py
"""
import dataclasses, math
from yugen_soundness import current as cu, wi, whir, revision5 as r5, revision6 as r6, spbcs
from yugen_soundness.compose import FsParams
from yugen_soundness.targets import CAT1, CAT3, SecurityTarget, _digest_proven

N = 20_000
KAPPA = {1: (128, 64), 3: (192, 96), 5: (256, 128)}
print("## R1 per-round need: kappa + 1 + log2 N + log2(1 + k)")
for c, (kc, kq) in KAPPA.items():
    a = kc + 1 + math.log2(N) + math.log2(600)
    b = kc + 1 + math.log2(N) + math.log2(601)
    q = 2 * kq + 1 + math.log2(6) + math.log2(N)
    # per-instance reading (one proof, no tree union)
    one = kc + 1 + math.log2(600)
    print(f"cat{c}: A {a:.3f}  B {b:.3f}  Q {q:.3f}  single-proof {one:.2f}")

print("\n## R2 system B unique decoding: ceil(e / -log2((1+rho)/2))")
for c, (kc, _) in KAPPA.items():
    e = kc + 1 + math.log2(N) + math.log2(601)
    for inv in (8, 16):
        bits = -math.log2((1 + 1 / inv) / 2)
        print(f"cat{c} rate 1/{inv}: {e / bits:.2f} -> {math.ceil(e / bits)}")

print("\n## R3 field bits: need + log2(largest n in an algebraic round); n = 2^24 (A leaf), 2^31 (2^30 nodes, both)")
for c, (kc, _) in KAPPA.items():
    e = kc + 1 + math.log2(N) + math.log2(601)
    print(f"cat{c}: leaf {e + 24:.1f}, worst node {e + 31:.1f}; at GF(2^256) margin on worst node {256 - 31 - e:+.1f}")

print("\n## R4 system A: calculator round list, counts re-solved, minimality of each count")
CAT5 = SecurityTarget(name="cat5", nist_category=5, classical_chain=256.0, quantum_chain=128.0, attack_bits=256.0,
                      digest_attack=512, digest_proven=_digest_proven(256.0))
DIG = {1: 256, 3: 384, 5: 512}
for T, fb in ((CAT1, 256), (CAT3, 256), (CAT5, 384)):
    t = cu.target(T, proofs=N)
    c = cu.a_config(cu.ROW6, cu.A_LEAF_VARS, cu.A_LEAF_RATE, 64, None)
    c.field_bits, c.ext_bytes = fb, fb // 8
    c.fs = dataclasses.replace(c.fs, digest_bits=DIG[T.nist_category])
    c = wi.solve(c, "A", t, wi.A_WALLET_ZK)
    rs = wi.rounds(c, "A", wi.A_WALLET_ZK)
    need = t.need_bits(len(rs), c.fs)
    minimal = []
    for i in range(len(c.queries)):
        c2 = copy = dataclasses.replace(c) if dataclasses.is_dataclass(c) else c
        q = list(c.queries); q[i] -= 1
        cc = cu.a_config(cu.ROW6, cu.A_LEAF_VARS, cu.A_LEAF_RATE, 64, q)
        cc.field_bits, cc.ext_bytes, cc.fs = c.field_bits, c.ext_bytes, c.fs
        w = min(r.effective_bits for r in wi.rounds(cc, "A", wi.A_WALLET_ZK))
        minimal.append(w < need)
    # per-query bits at the first round's rate 1/4 (independent check of the first count)
    first = need / -math.log2((1 + 0.25) / 2)
    print(f"{T.name} field 2^{fb}: queries {c.queries}, rounds k = {len(rs)}, need {need:.2f}, "
          f"weakest {min(r.effective_bits for r in rs):.2f}; one less fails at each level: {minimal}; "
          f"first-round closed form {first:.1f}")

print("\n## R5 QROM hash term of SG26 Thm 6.6(2) over N proofs: N 6 c' (t + k_q)^3 / 2^(8b) <= 1/2 at t = 2^kappa_Q")
k = r6.a_counts(); kb = r6.b_counts()
for name, cnt in (("A", k), ("B", kb)):
    base = math.log2(N) + math.log2(6 * cnt.c_prime) + 1
    for c, (_, kq) in KAPPA.items():
        bits = 3 * kq + base
        print(f"{name} cat{c}: c' = {cnt.c_prime}, k_q = {cnt.k_q}; digest >= {bits:.1f} bits -> {8 * math.ceil(bits / 8)}; "
              f"QROM bits of the hash term at 48 B {(384 - base) / 3:.1f}, at 64 B {(512 - base) / 3:.1f}")

print("\n## R6 leaf-salt floor (SG26 p. 58: first term of eps_leaf 2^(-4(b_l-b)-1)), pool 2^20 proofs, A's n_pos")
for target in (64, 96, 128):
    for b in (32, 48, 64):
        for bl in range(b, 160):
            lt = 20 + k.n_pos_log2 + (-4 * (bl - b) - 1)
            if lt <= -target:
                print(f"ZK pool target 2^-{target}, digest {b} B: leaf salt >= {bl} B (term 2^{lt:.1f})")
                break

print("\n## R7 capacity, specification 16.2 (weight = block bytes + proof bytes), W = 4,000,000")
W = 4_000_000
def cap(root_a, root_b, leaf_reserve, per_tx=200):
    room = W - leaf_reserve - root_a - root_b
    return max(0, room // per_tx)
print("cat1 record's figure:", cap(875_309, 735_410, 1_150_000))
print("cat1 with 210.5 B a transfer (plan's allowance):", cap(875_309, 735_410, 1_150_000, 210.5))
print("plan's own launch figure, proofs 1,787,904, leaf actually present 1,030,444:", (W - 1_787_904 - 1_030_444) // 210.5)
print("cat3 1/4 and 1/16 with LEAF_RESERVE kept at 1,150,000:", cap(1_277_031, 1_179_410, 1_150_000))
print("cat3 with LEAF_RESERVE raised to 1,972,000 (record 4.2):", cap(1_277_031, 1_179_410, 1_972_000))
print("W4 today: measured leaf proofs A 600,340 + B 583,680 =", 600_340 + 583_680, "+ 17,456 bytes =",
      600_340 + 583_680 + 17_456, "against LEAF_RESERVE 1,150,000")

print("\n## R8 system B E2 baseline: the script's formula at cat1 SHA-256 vs parameters.md 9.4")
for lo in (5.8, 8.7):
    print(f"slot {lo}: formula {1504 * lo + 435 + 416 * lo:,.0f}")
print("parameters.md 9.4: 13,000 to 18,600; ratio", round(13000 / 11571, 3), round(18600 / 17139, 3))
print("cat3 SHA-384 rescaled from parameters.md:", f"{(13000 - 435) * 2 + 435:,.0f} to {(18600 - 435) * 2 + 435:,.0f}")
