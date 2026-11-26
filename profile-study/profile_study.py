"""Profile study for docs/decision-security-profile.md (the Ycash developers, 2026).

Uses the calculator `soundness/` at revision 7 (commits 96dd271 to 6c8c922) as a library, unchanged: the rows, sizes,
zero-knowledge figures and salt floors come from `yugen_soundness.category`. Everything else in this file is
arithmetic on figures read from the documents named beside each constant (M measured, C counted, E estimate).
Run: cd soundness && uv run python ../profile-study/profile_study.py > ../profile-study/output/profile-tables.txt
Sections S6 to S9 are revision 2 of the record (after docs/security-profile-referee.md); S1 to S5 are unchanged.
"""
import math
from dataclasses import replace

from yugen_soundness import category as cat
from yugen_soundness import spbcs

KIB = 1024


def kib(b):
    return f"{b / KIB:,.0f}"


# ---------------------------------------------------------------------------------------------------------------
# Inputs read from the documents (each with its source)
# ---------------------------------------------------------------------------------------------------------------
W = 4_000_000                 # BLOCK_WEIGHT_MAX, specification 0.3.3 section 2
LEAF_RESERVE = 1_150_000      # specification section 2 (provisional, E1)
LEAF_BYTES_RESERVE = 17_456   # specification section 2 and 16.2
PROOF_BYTES_MAX = 1_835_008   # W1
RECORD = 200                  # bundled transfer without value balance or package, specification 7.1
E1_A, E1_B = 530 * KIB, 576 * KIB  # plan 11, E1

# Measured leaf proofs (M)
A_LEAF_STUDY = 600_340        # decision-security-category.md 3.2 (the record's and the referee's anchor)
A_LEAF_ROW8 = 692_504         # yugen-proof-a docs/parameters.md 2.3: row 8, 64-byte leaf salts, mode 0, rate 1/4
A_LEAF_ROW6 = 688_180         # same table, row 6
B_LEAF_FORMT = 583_680        # yugen-proof-b2 docs/parameters.md 8.3: cat1t, 184 queries, 256-bit salts, no route S
B_SALT_512 = 11_776           # yugen-proof-b2 parameters.md 8.4: 512-bit salts at q = 184 on the 256-bit field
B_ROUTE_S = 46 * KIB          # yugen-proof-b2 parameters.md 9.5 ("route S +46 KiB a leaf", the specification's figure)

A_NODE_ROOT_M = 875_309       # yugen-proof-a recursion.md 9.10: M of 7 S(9), 2^27, rate 1/2 (M)

# Wallet statements as built (all M or C)
A_CYCLES, A_KECCAK, A_WORDS, A_STACK = 187_746, 87, 3_463_392, 22  # yugen-proof-a statement-layout.md 3
A_FALCON_CYCLES = 78_846
A_TREE_LEVEL_CYCLES = 24      # one level of the note tree, one Keccak-f (statement-layout.md 3)
B_AND, B_WORDS, B_KECCAK = 112_710, 130_684, 78  # yugen-proof-b2 statement-layout.md (C)
B_FALCON_AND = 72_294
B_LIMIT = 131_072             # 2^17
KECCAK_AND = 600              # yugen-proof-b2 parameters.md 10.4 (C, "confirmed")

# E2 (core-seconds for N = 1,500); E2 is 7,680 for both systems (8 hosts x 16 cores x 60 s)
HOST_CS = 16 * 60
A_E2 = 4_120                  # yugen-proof-a recursion.md 9.10 (model on measured nodes)
B_E2_CAT1_BLAKE3 = (6_700, 9_500)   # yugen-proof-b2 parameters.md 9.4 (E)
B_E2_CAT1_REDUCED = (4_600, 6_200)  # parameters.md 9.4: 184 queries after D-6, K = 7 or 15 and the cap layer at 7 (E)
B_E2_CAT3_SHA384 = (25_600, 36_800)  # security-category-referee.md 4.4 (rebased, E)
A_E2_CAT3 = 5_511             # decision-security-category.md 4.3 T7 (E)
B_E2_CAT5 = (45_000, 67_000)  # decision-security-category.md 4.3 (E; the referee: rises in proportion)
A_E2_CAT5 = (9_436, 11_570)

# Privacy components; ML-KEM sizes are FROM MEMORY (FIPS 203 is not in the reference folder)
MLKEM = {768: dict(ek=1_184, ct=1_088, dk=2_400), 1024: dict(ek=1_568, ct=1_568, dk=3_168)}
PKG_SHORT, PKG_LONG = 1_178, 1_690   # specification 7.1 field sizes with ML-KEM-768
MAILBOX_PKG = 1_176                  # plan 8 (mailbox storage a package)
DPF_KEY_128 = 292                    # yugen-pir pir-selection.md: tag lookup key bytes at 128-bit seeds
DPF_BUCKET = 256
DPF_LOOKUPS_A_DAY = 17               # pir-selection.md: 17 queries x 2 servers a day


def section(t):
    print(f"\n## {t}\n")


# ---------------------------------------------------------------------------------------------------------------
section("S1. Rule W4 against the measured leaf proofs")
print("| Leaf pair | A (B) | B (B) | Proofs | + LEAF_BYTES_RESERVE | LEAF_RESERVE | Over by |")
print("|---|---|---|---|---|---|---|")
pairs = [
    ("referee R7: A 600,340 (study anchor) + B form T", A_LEAF_STUDY, B_LEAF_FORMT),
    ("A row 8 with 64-byte salts (M) + B form T (M)", A_LEAF_ROW8, B_LEAF_FORMT),
    ("A row 8 (M) + B with 512-bit salts (M + C)", A_LEAF_ROW8, B_LEAF_FORMT + B_SALT_512),
    ("A row 8 (M) + B with 512-bit salts and route S (M + C + spec figure)", A_LEAF_ROW8, B_LEAF_FORMT + B_SALT_512 + B_ROUTE_S),
]
for name, a, b in pairs:
    tot = a + b + LEAF_BYTES_RESERVE
    print(f"| {name} | {a:,} | {b:,} | {a + b:,} | {tot:,} | {LEAF_RESERVE:,} | {tot - LEAF_RESERVE:+,} |")
print(f"\nE1 size limits: A {E1_A:,} B, B {E1_B:,} B; together {E1_A + E1_B:,} B (the reserve was sized on these).")
print(f"A row 8 over E1's A limit by {A_LEAF_ROW8 - E1_A:+,} B; B form T under its limit by {B_LEAF_FORMT - E1_B:+,} B.")

# ---------------------------------------------------------------------------------------------------------------
section("S2. Calculator revision 7: category-1 rows with the salts of a zero-knowledge target")
TARGET = -128.0
c1 = cat.certify(cat.PROFILES[1])
lf_a = cat.leaf_salt_floor(c1.a_counts, 32, TARGET)
lf_b = cat.leaf_salt_floor(c1.b_counts, 32, TARGET)
ps_q = cat.proof_salt_floor(128.0, TARGET)
ps_c = cat.proof_salt_floor(256.0, TARGET)
print(f"Zero-knowledge target: pool of 2^20 leaf proofs, advantage <= 2^{TARGET:.0f} (excluding Q eps_hvzk).")
print(f"Leaf salt floor at 32-byte proof digests: A {lf_a} B, B {lf_b} B. Proof salt floor: {ps_q} B at t = 2^128 "
      f"(quantum queries before the last proof), {ps_c} B if t is read as 2^256 classical queries.")
print("Built granularity: A salts in 8-byte words (parameters.md 2.3); B salts in field elements, 32 B at GF(2^256) "
      "(yugen-proof-b2 parameters.md 8.4). Chosen: A leaf 80 B, B leaf 96 B, proof salt 80 B.")

PROFILE_Y = cat.Profile(1, 256, 80, 80, 256, "Keccak-256", "BLAKE3", privacy_category=5,
                        label="Y (soundness 1 per system, privacy 5; A leaf salt 80 B)")
PROFILE_YB = replace(PROFILE_Y, leaf_salt_bytes=96, label="Y, B's leaf salt 96 B")
cy, cyb = cat.certify(PROFILE_Y), cat.certify(PROFILE_YB)


def pick(cert, sysn, kind, lab, st, rt):
    return next(r for r in (cert.a if sysn == "A" else cert.b)
                if r.kind == kind and r.label.startswith(lab) and r.stack == st and r.rate == rt)


print("\n| Profile | System | Proof salt | Leaf salt | One proof | Pool (2^20) | WI (6.6 (4)) pool, no query bound | "
      "Salt term at t = 2^256 classical | log2(t / eps) of the salt term |")
print("|---|---|---|---|---|---|---|---|---|")
for cert in (c1, cy, cyb):
    for z in (cert.a_zk, cert.b_zk):
        salt_cl = 2 + cat.POOL_LOG2 + 256 - 4 * z.proof_salt
        print(f"| {cert.profile.name} | {z.system} | {z.proof_salt} | {z.leaf_salt} | 2^{z.one:.1f} | 2^{z.pool:.1f} | "
              f"2^{z.wi_pool:.1f} | 2^{min(0, salt_cl):.1f} | {4 * z.proof_salt - 2 - cat.POOL_LOG2:.0f} |")
print("\nThe last column is t / eps for the proof-salt term 4 Q t / 2^(4 b_s) of Theorem 6.6 (3): it does not depend "
      "on t, so an adversary's work divided by its advantage from that term is at least 2^(4 b_s - 22) whatever t is.")
print(f"Category 5 (2^256) needs 4 b_s - 22 >= 256: b_s >= {math.ceil((256 + 22) / 4)} B. Category 3: "
      f"{math.ceil((192 + 22) / 4)} B.")

print("\nCategory-1 rows (revision 7), sizes E:")
print("| Profile | A leaf row 8 mode 0 1/4 | A node 2^27 1/2 | B leaf 1/8 | B node 2^27 words 1/8 | weakest A / B | QROM A / B |")
print("|---|---|---|---|---|---|---|")
for cert in (c1, cy, cyb):
    al = pick(cert, "A", "leaf", "row 8 (masked in a tree), mode 0", 22, 2)
    an = pick(cert, "A", "node", "row 9", 27, 1)
    bl = pick(cert, "B", "leaf", "zero", 20, 3)
    bn = pick(cert, "B", "node", "node", cat.B_NODE_WORDS, 3)
    print(f"| {cert.profile.name} | {al.size:,.0f} | {an.size:,.0f} | {bl.size:,.0f} | {bn.size:,.0f} | "
          f"{cert.a_e:.2f} / {cert.b_e:.2f} | {cert.a_qrom.bits:.2f} / {cert.b_qrom.bits:.2f} |")
A_LEAF_Y = pick(cy, "A", "leaf", "row 8 (masked in a tree), mode 0", 22, 2).size
B_LEAF_Y = pick(cyb, "B", "leaf", "zero", 20, 3).size
B_NODE_Y = pick(cy, "B", "node", "node", cat.B_NODE_WORDS, 3).size
A_LEAF_1 = pick(c1, "A", "leaf", "row 8 (masked in a tree), mode 0", 22, 2).size
B_LEAF_1 = pick(c1, "B", "leaf", "zero", 20, 3).size
B_NODE_1 = pick(c1, "B", "node", "node", cat.B_NODE_WORDS, 3).size

# higher categories and M-1, from the calculator
sizes = {}
for key, p in (("cat3", cat.PROFILES[3]), ("M-1", cat.M1)):
    ce = cat.certify(p)
    sizes[key] = dict(
        a_leaf=pick(ce, "A", "leaf", "row 8 (masked in a tree), mode 0", 22, 2).size,
        b_leaf=pick(ce, "B", "leaf", "zero", 20, 3).size,
        a_node=min(pick(ce, "A", "node", "row 9", 27, r).size for r in (1, 2)),
        b_node=min(pick(ce, "B", "node", "node", cat.B_NODE_WORDS, r).size for r in (3, 4)))
c5 = cat.certify(cat.PROFILES[5])
sizes["cat5"] = dict(
    a_leaf=pick(c5, "A", "leaf", "row 8 (masked in a tree), mode 0", 22, 2).size,
    b_leaf=pick(c5, "B", "leaf", "zero", 20, 3).size,
    a_node=min(pick(c5, "A", "node", "row 9", 27, r).size for r in (1, 2)),
    b_node=min(pick(c5, "B", "node", "node", cat.B_NODE_WORDS, r).size for r in (3, 4)))

# ---------------------------------------------------------------------------------------------------------------
section("S3. The wallet statements: binding digests of 48 bytes and Falcon-1024, by count")
# 48-byte binding digests: the 4-ary note-tree node becomes 4 x 48 + 5 = 197 bytes, two Keccak-f at rate 136 (one
# today: 133 bytes); a binary tree of depth 40 at 48 bytes is 101 bytes, one Keccak-f a level, 40 a path: the same.
tree_extra = 2 * 20       # one more Keccak-f a level, 20 levels, two spends
# Falcon-1024 (yugen-falcon docs/circuit-notes.md "Witness and cost"): hash-to-point 10 -> 19, H_sig 7 -> 14 a spend
falcon_keccak_extra = (19 - 10) + 2 * (14 - 7)
A_FALCON_1024 = (165_000, 175_000)   # decision-security-category.md 3.7 (E: transforms x2.22, linear parts x2)
B_FALCON_1024 = (150_000, 155_000)   # same (E)
A_WORDS_PER_CYCLE = A_WORDS / A_CYCLES  # average committed words a cycle of the leaf (E: used only for the stack)
print("| Variant | A: cycles | A: Keccak-f | A: committed words (E) | A stack | B: AND rows | B: Keccak-f | B stack |")
print("|---|---|---|---|---|---|---|---|")
variants = []
for bind in (32, 48):
    for fal in (512, 1024):
        ac = A_CYCLES + (tree_extra * A_TREE_LEVEL_CYCLES * 2 if bind == 48 else 0)
        ak = A_KECCAK + (tree_extra if bind == 48 else 0)
        bk = B_KECCAK + (tree_extra if bind == 48 else 0)
        band = B_AND + (tree_extra * KECCAK_AND if bind == 48 else 0)
        if fal == 1024:
            ac_lo, ac_hi = ac - A_FALCON_CYCLES + A_FALCON_1024[0], ac - A_FALCON_CYCLES + A_FALCON_1024[1]
            ak += falcon_keccak_extra
            bk += falcon_keccak_extra
            b_lo = band - B_FALCON_AND + B_FALCON_1024[0] + falcon_keccak_extra * KECCAK_AND
            b_hi = band - B_FALCON_AND + B_FALCON_1024[1] + falcon_keccak_extra * KECCAK_AND
        else:
            ac_lo = ac_hi = ac
            b_lo = b_hi = band
        w_lo, w_hi = ac_lo * A_WORDS_PER_CYCLE, ac_hi * A_WORDS_PER_CYCLE
        a_stack = math.ceil(math.log2(w_hi))
        b_stack = 17 if b_hi <= B_LIMIT else math.ceil(math.log2(b_hi))
        variants.append((bind, fal, a_stack, b_stack))
        rng = (lambda lo, hi: f"{lo:,.0f}" if lo == hi else f"{lo:,.0f} to {hi:,.0f}")
        print(f"| binding {bind} B, Falcon-{fal} | {rng(ac_lo, ac_hi)} | {ak} | {rng(w_lo, w_hi)} | 2^{a_stack} | "
              f"{rng(b_lo, b_hi)} | {bk} | 2^{b_stack} |")
print("\nA's 2^22 stack holds 4,194,304 words (headroom 730,912 as built). A's words scale here by the leaf's average "
      "words a cycle (E); the KECCAK table's words a permutation are not counted (task P-2). B's limit for 2^17 is "
      "131,072 AND rows and 131,072 committed words (388 free as built).")

# ---------------------------------------------------------------------------------------------------------------
section("S4. Options: leaf pair, LEAF_RESERVE, roots, capacity at W = 4,000,000 (E unless marked)")
# Proof-size growth when a wallet stack doubles: one more Merkle level a tree. A: 32 B a query at level 0 (row 8 at
# 1/4: 227 queries; E); B: 32 B a query a round-oracle tree, two such trees at 184 queries (E).
A_LEVEL = 32 * 227
B_LEVEL = 32 * 184 * 2
pkg_extra = lambda kem: 2 * (MLKEM[kem]["ct"] - MLKEM[768]["ct"])


def option(name, a_leaf, b_leaf, a_root, b_root, record, kem, hosts, wallet):
    leaf_bytes = LEAF_BYTES_RESERVE + pkg_extra(kem)
    reserve = math.ceil((a_leaf + b_leaf + leaf_bytes) / 1_000) * 1_000
    w1 = max(a_leaf, b_leaf, a_root, b_root) <= PROOF_BYTES_MAX
    room = W - reserve - a_root - b_root
    cap = max(0, math.floor(room / record)) if w1 else 0
    w_for_6000 = reserve + a_root + b_root + 6_000 * record
    return dict(name=name, a_leaf=a_leaf, b_leaf=b_leaf, reserve=reserve, a_root=a_root, b_root=b_root, w1=w1,
                cap=cap, record=record, w6000=w_for_6000, hosts=hosts, wallet=wallet, kem=kem)


def hosts(a, b):
    lo, hi = (a[0] + b[0]) / HOST_CS, (a[1] + b[1]) / HOST_CS
    return f"{math.ceil(lo)} to {math.ceil(hi)}"


A2 = (A_E2, A_E2)
opts = [
    option("O1 category 1 as built (64/64 salts)", A_LEAF_1, B_LEAF_1, A_NODE_ROOT_M, B_NODE_1, RECORD, 768,
           hosts(A2, B_E2_CAT1_BLAKE3) + f" ({hosts(A2, B_E2_CAT1_REDUCED)} with D-6, K, cap)", "A 2^22, B 2^17"),
    option("O2 referee P6 (salts 80/96/80, ML-KEM-1024)", A_LEAF_Y, B_LEAF_Y, A_NODE_ROOT_M, B_NODE_Y, RECORD, 1024,
           hosts(A2, B_E2_CAT1_BLAKE3) + f" ({hosts(A2, B_E2_CAT1_REDUCED)})", "A 2^22, B 2^17"),
    option("O3a O2 + 48-byte binding digests", A_LEAF_Y, B_LEAF_Y + B_LEVEL, A_NODE_ROOT_M, B_NODE_Y, RECORD + 32, 1024,
           hosts(A2, B_E2_CAT1_BLAKE3) + f" ({hosts(A2, B_E2_CAT1_REDUCED)})", "A 2^22, B 2^18"),
    option("O3b O2 + Falcon-1024", A_LEAF_Y + A_LEVEL, B_LEAF_Y + B_LEVEL, A_NODE_ROOT_M, B_NODE_Y, RECORD, 1024,
           hosts(A2, B_E2_CAT1_BLAKE3) + f" ({hosts(A2, B_E2_CAT1_REDUCED)})", "A 2^23, B 2^18"),
    option("O3c O2 + both", A_LEAF_Y + A_LEVEL, B_LEAF_Y + B_LEVEL, A_NODE_ROOT_M, B_NODE_Y, RECORD + 32, 1024,
           hosts(A2, B_E2_CAT1_BLAKE3) + f" ({hosts(A2, B_E2_CAT1_REDUCED)})", "A 2^23, B 2^18"),
    option("O4 study M-1 (cat 3 rows, 48 B, Falcon-1024, ML-KEM-1024)", sizes["M-1"]["a_leaf"] + A_LEVEL,
           sizes["M-1"]["b_leaf"] + B_LEVEL, sizes["M-1"]["a_node"], sizes["M-1"]["b_node"], RECORD + 32, 1024,
           hosts((A_E2_CAT3, A_E2_CAT3), B_E2_CAT3_SHA384), "A 2^23, B 2^18"),
    option("O5 category 3 throughout (ML-KEM-768)", sizes["cat3"]["a_leaf"] + A_LEVEL, sizes["cat3"]["b_leaf"] + B_LEVEL,
           sizes["cat3"]["a_node"], sizes["cat3"]["b_node"], RECORD + 32, 768,
           hosts((A_E2_CAT3, A_E2_CAT3), B_E2_CAT3_SHA384), "A 2^23, B 2^18"),
    option("O6 category 5 throughout (GF(2^384), unique decoding)", sizes["cat5"]["a_leaf"] + A_LEVEL,
           sizes["cat5"]["b_leaf"] + B_LEVEL, sizes["cat5"]["a_node"], sizes["cat5"]["b_node"], RECORD + 64, 1024,
           hosts(A_E2_CAT5, B_E2_CAT5), "A 2^23, B 2^18"),
]
print("| Option | A leaf | B leaf | LEAF_RESERVE needed | A root | B root | W1 (every proof <= 1.75 MiB) | Record | "
      "Transfers a block at W = 4 MB | W for 6,000 a block | Hosts for E2 (N = 1,500, 60 s) | Wallet stacks |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for o in opts:
    print(f"| {o['name']} | {o['a_leaf']:,.0f} | {o['b_leaf']:,.0f} | {o['reserve']:,} | {o['a_root']:,.0f} | "
          f"{o['b_root']:,.0f} | {'yes' if o['w1'] else '**no**'} | {o['record']} | {o['cap']:,} | "
          f"{o['w6000']:,.0f} | {o['hosts']} | {o['wallet']} |")
print("\nLEAF_RESERVE needed = A leaf + B leaf + LEAF_BYTES_RESERVE (+960 B for two long ML-KEM-1024 packages), "
      "rounded up to 1,000. Capacity = (W - LEAF_RESERVE - A root - B root) / record (rule W5; tree and anchor-table "
      "bytes left out: upper figures). Roots: A's category-1 root is the measured 875,309 B; every other size is the "
      "calculator's (E). Hosts: 16 cores x 60 s = 960 core-seconds a host.")

# ---------------------------------------------------------------------------------------------------------------
section("S5. Privacy components: bytes (ML-KEM sizes from memory; FIPS 203 not in the folder)")
for kem in (768, 1024):
    m = MLKEM[kem]
    print(f"ML-KEM-{kem}: ek {m['ek']:,} B, ciphertext {m['ct']:,} B, dk {m['dk']:,} B; package short "
          f"{PKG_SHORT + m['ct'] - MLKEM[768]['ct']:,} B, long {PKG_LONG + m['ct'] - MLKEM[768]['ct']:,} B; "
          f"mailbox entry {MAILBOX_PKG + m['ct'] - MLKEM[768]['ct']:,} B")
dpf256 = 2 * DPF_KEY_128  # each correction word carries a seed of twice the length (E)
for lam, key in ((128, DPF_KEY_128), (256, dpf256)):
    day = DPF_LOOKUPS_A_DAY * 2 * (key + DPF_BUCKET)
    print(f"DPF lambda = {lam}: key about {key} B; tag lookups a day {day / 1000:.1f} KB (E5 idle limit 50 KB)")
print("Transport: the hybrid handshake carries one ek and one ciphertext a connection: +384 B and +480 B with "
      "ML-KEM-1024 (from memory).")

# ===============================================================================================================
# Revision 2 of the record (after docs/security-profile-referee.md, verdicts V1 to V8). Nothing above changes; the
# sections below restate what the referee corrected, from the same inputs plus the ones named beside each constant.
# ===============================================================================================================
Y_RECORD = RECORD + 32        # 48-byte binding: the transfer record of profile Y
A_ROOT, B_ROOT = A_NODE_ROOT_M, B_NODE_Y
ML1024_EXTRA = pkg_extra(1024)  # two long ML-KEM-1024 packages: +960 B on LEAF_BYTES_RESERVE

# ---------------------------------------------------------------------------------------------------------------
section("S6. LEAF_RESERVE from measured leaves plus counted deltas (referee V7), and capacity under Y")
A_SALT_80_DELTA = A_LEAF_Y - A_LEAF_1   # calculator delta for A's leaf salt 64 -> 80 B (E, revision 7)
B_SALT_96_DELTA = 2 * B_SALT_512        # 256 -> 768-bit salts: twice the measured 256 -> 512-bit delta (C)
a_meas = A_LEAF_ROW8 + A_SALT_80_DELTA
b_meas = B_LEAF_FORMT + B_SALT_96_DELTA + B_ROUTE_S + B_LEVEL
print("| Leaf | Calculator (E, revision 7) | Measured plus counted deltas | Difference |")
print("|---|---|---|---|")
print(f"| A, row 8, 80-byte leaf salt, 2^22 | {A_LEAF_Y:,.0f} | {a_meas:,.0f} = {A_LEAF_ROW8:,} (M) + {A_SALT_80_DELTA:,.0f} "
      f"(salt 64 -> 80 B, E) | {a_meas - A_LEAF_Y:+,.0f} |")
B_LEAF_Y48 = B_LEAF_Y + B_LEVEL
print(f"| B, form T, 96-byte leaf salt, route S, 2^18 | {B_LEAF_Y48:,.0f} | {b_meas:,} = {B_LEAF_FORMT:,} (M) + "
      f"{B_SALT_96_DELTA:,} (salt, C) + {B_ROUTE_S:,} (route S, spec figure) + {B_LEVEL:,} (one level, E) | "
      f"{b_meas - B_LEAF_Y48:+,.0f} |")
lbr = LEAF_BYTES_RESERVE + ML1024_EXTRA


def reserve_of(a, b):
    return math.ceil((a + b + lbr) / 1_000) * 1_000


def capacity(reserve, w=W, record=Y_RECORD):
    return math.floor((w - reserve - A_ROOT - B_ROOT) / record)


rows6 = [("record revision 1 (calculator on both sides)", A_LEAF_Y, B_LEAF_Y48),
         ("measured plus deltas on both sides", a_meas, b_meas),
         ("the larger of the two on each side (provisional value)", max(a_meas, A_LEAF_Y), max(b_meas, B_LEAF_Y48))]
print("\n| Reserve basis | A leaf | B leaf | LEAF_RESERVE | Transfers a block at W = 4,000,000 (record 232 B) | "
      "W for 5,150 | W for 6,000 |")
print("|---|---|---|---|---|---|---|")
for name, a, b in rows6:
    r = reserve_of(a, b)
    print(f"| {name} | {a:,.0f} | {b:,.0f} | {r:,} | {capacity(r):,} | {r + A_ROOT + B_ROOT + 5_150 * Y_RECORD:,.0f} | "
          f"{r + A_ROOT + B_ROOT + 6_000 * Y_RECORD:,.0f} |")
print(f"\nLEAF_BYTES_RESERVE with two long ML-KEM-1024 packages: {lbr:,} B. Roots: A {A_ROOT:,} (M), B {B_ROOT:,.0f} (E).")

# ---------------------------------------------------------------------------------------------------------------
section("S7. Zero-knowledge salts at the lifetime proof count (referee V6, finding on Q)")
blocks_a_day = 86_400 / 75
for cap_ in (capacity(reserve_of(a_meas, b_meas)), capacity(reserve_of(A_LEAF_Y, B_LEAF_Y48))):
    per_day = cap_ * blocks_a_day
    print(f"At {cap_:,} transfers a 75-second block: one system makes 2^{math.log2(per_day):.1f} leaf proofs a day, "
          f"2^{math.log2(per_day * 365.25 * 10):.1f} in ten years, 2^{math.log2(per_day * 365.25 * 50):.1f} in fifty (C).")


def leaf_floor_q(counts, digest_bytes, target, q_log2):
    for bl in range(digest_bytes + 1, digest_bytes + 129):
        if q_log2 + counts.n_pos_log2 + spbcs.eps_leaf_log2(digest_bytes, bl, counts.leaf_bytes) <= target:
            return bl
    return -1


def proof_floor_q(work_log2, q_log2):
    """Smallest proof salt b_s with t / eps >= 2^work for the term 4 Q t / 2^(4 b_s)."""
    return math.ceil((work_log2 + 2 + q_log2) / 4)


print("\n| | Q = 2^20 | Q = 2^35 | Q = 2^37 |")
print("|---|---|---|---|")
qs = (20, 35, 37)
print("| A leaf salt floor for 2^-128 (32-byte proof digests) | " + " | ".join(
    f"{leaf_floor_q(c1.a_counts, 32, TARGET, q)} B" for q in qs) + " |")
print("| B leaf salt floor for 2^-128 | " + " | ".join(f"{leaf_floor_q(c1.b_counts, 32, TARGET, q)} B" for q in qs) + " |")
print("| A leaf term at 80 B | " + " | ".join(
    f"2^{q + c1.a_counts.n_pos_log2 + spbcs.eps_leaf_log2(32, 80, c1.a_counts.leaf_bytes):.1f}" for q in qs) + " |")
print("| B leaf term at 96 B | " + " | ".join(
    f"2^{q + c1.b_counts.n_pos_log2 + spbcs.eps_leaf_log2(32, 96, c1.b_counts.leaf_bytes):.1f}" for q in qs) + " |")
print("| Proof salt: t / eps at 80 B | " + " | ".join(f"2^{4 * 80 - 2 - q}" for q in qs) + " |")
print("| Proof-salt floor against 2^256 / against 2^272 (AES-256's gate count, [CFP] p. 18) | " + " | ".join(
    f"{proof_floor_q(256, q)} / {proof_floor_q(272, q)} B" for q in qs) + " |")
print("\nChosen and unchanged: A leaf 80 B, B leaf 96 B, proof salt 80 B. Margins at Q = 2^37: A leaf "
      f"{80 - leaf_floor_q(c1.a_counts, 32, TARGET, 37)} B, B leaf {96 - leaf_floor_q(c1.b_counts, 32, TARGET, 37)} B, "
      f"proof salt {80 - proof_floor_q(272, 37)} B against 2^272.")

# ---------------------------------------------------------------------------------------------------------------
section("S8. B's wallet memory at 2^18 (referee V7)")
B_PEAK_2_17 = (1_095, 1_106)       # yugen-proof-b2 parameters.md 8.3: category-1 form-T leaf, whole process (M)
B_STEPS_AB = (1_270.5, 554.4)      # yugen-proof-b2 wallet-memory.md section 4: before and after steps a, b (M, dev run)
E1_MEM = 512
ratio = B_STEPS_AB[1] / B_STEPS_AB[0]
lo, hi = (2 * x * ratio for x in B_PEAK_2_17)
print(f"Steps a and b kept {ratio:.3f} of the footprint at the pin. Applied to twice the category-1 peak: "
      f"{lo:,.0f} to {hi:,.0f} MB at 2^18 (E: assumes the same proportion), about {hi / E1_MEM:.1f} x "
      f"E1's {E1_MEM} MB. The unreduced 2^18 process: {2 * B_PEAK_2_17[0]:,} to {2 * B_PEAK_2_17[1]:,} MB, "
      f"about {2 * B_PEAK_2_17[1] / E1_MEM:.1f} x (the record revision 1's 'about 4x').")

# ---------------------------------------------------------------------------------------------------------------
section("S9. Note-tree hash variants at 48-byte digests (referee V8; task F-2 counts them in circuit)")
# Per level of the note tree and per spend; a transfer has two spends. B rows: yugen-proof-b2 parameters.md 10.4 (C):
# Keccak-f 600, SHA-512 compression 920; Keccak-p[1600,12] taken as half of Keccak-f (E). Committed words: one a row
# of a permutation (E, the referee's rule), plus the sibling words a path adds over today's 1,920 bytes.
B_KECCAK12 = KECCAK_AND // 2
FRAME = 5                 # spec 3.1 node frame bytes (4 x 32 + 5 = 133 today)
FRAME16 = 16              # T1b: the frame first, padded to one 16-byte cell, so both children are whole cells in A
DIG = 48


def blocks(nbytes, rate, pad_min=1):
    return math.ceil((nbytes + pad_min) / rate)


variants9 = [
    # name, arity, depth, permutations a level, AND rows a permutation, FIPS?, A note
    ("T0 as built: SHA3-256, 4-ary, 32-byte (category 2)", 4, 20, 1, KECCAK_AND, "FIPS 202", 32,
     "24 cycles a level (M)"),
    ("T1 SHAKE256-384 (or SHA3-384), 4-ary, two blocks", 4, 20, blocks(4 * DIG + FRAME, 104), KECCAK_AND, "FIPS 202", DIG,
     "two KECCAK rows a level; aligned layout needed (a cell straddles at rate 136 or 104)"),
    ("T1b SHAKE256-384, binary, framed node (16-byte frame first), one block", 2, 40, blocks(2 * DIG + FRAME16, 136),
     KECCAK_AND, "FIPS 202", DIG, "one KECCAK row a level; 112 bytes, children at bytes 16 and 64: no straddle"),
    ("T1c SHA-384, binary, one 128-byte block", 2, 40, blocks(2 * DIG + FRAME, 128, 17), 920, "FIPS 180-4", DIG,
     "no SHA-512 precompile in A: not buildable without a VM change"),
    ("T2 TurboSHAKE256, 4-ary, two Keccak-p[1600,12]", 4, 20, blocks(4 * DIG + FRAME, 136), B_KECCAK12, "RFC 9861 (not FIPS)",
     DIG, "needs a 12-round precompile (VM change)"),
    ("T3 Keccak-f[1600] at capacity 384 (rate 152), ternary", 3, 26, blocks(3 * DIG + FRAME, 152), KECCAK_AND,
     "not FIPS (a Keccak sponge outside FIPS 202's set)", DIG, "one KECCAK row a level; no VM change; 26 levels"),
]
base_and_tree = 2 * 20 * KECCAK_AND
base_sib_bytes = 20 * 3 * 32
print("| Variant | Standard | Depth | Perm. a level | Tree AND rows a transfer (B) | B AND rows | B committed words (E) | "
      "B stack | Keccak-f-equivalents a transfer | Path bytes a spend | A |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for name, ar, depth, perm, rows, std, dig, anote in variants9:
    assert ar ** depth >= 4 ** 20, name
    tree_rows = 2 * depth * perm * rows
    d_and = tree_rows - base_and_tree
    sib = depth * (ar - 1) * dig
    d_words = d_and + (2 * (sib - base_sib_bytes)) // 8
    band, bwords = B_AND + d_and, B_WORDS + d_words
    stack = 17 if max(band, bwords) <= B_LIMIT else math.ceil(math.log2(max(band, bwords)))
    print(f"| {name} | {std} | {depth} | {perm} | {tree_rows:,} | {band:,} | {bwords:,} | 2^{stack} | "
          f"{tree_rows / KECCAK_AND:.0f} | {sib:,} | {anote} |")
print("\nB's 2^17 limit is 131,072 AND rows and 131,072 committed words (388 words free as built). The sibling words "
      "assume 8-byte words; the other 48-byte digests of the statement (cm, nkc, anchor_root as public words) are not "
      "counted here (F-2 counts them). T1c is priced for B only.")
print("Other functions of yugen-proof-b2 parameters.md 10.4 for a 48-byte binding digest: BLAKE3 (168 to 192 rows) and "
      "SHA-256 (364) give 32 bytes only and claim 128 bits (decision-b-merkle-hash.md H-1.5); Keccak-256 (600) gives "
      "32 bytes; SHA-512 (1,840 a two-block node) is a 64-byte digest. None serves 48-byte binding.")
print("\nBlock weight that restores 5,150 transfers under Y (record 232 B): S6, 4,172,711 to 4,186,711 B (about 4.18 MB).")
