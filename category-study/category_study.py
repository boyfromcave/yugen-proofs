"""Category study: what NIST categories 1, 3 and 5 require of each component of a Yugen transfer.

Run from the calculator's project (it is used as a library, revision 6, unchanged):

    cd soundness && uv run python ../category-study/category_study.py > ../category-study/output/category-tables.txt

Every figure is marked: M measured (cited), C counted, E estimate (this script's model, from the calculator's
functions and the measured anchors named beside it). Provenance: the calculator's bounds are those of
docs/soundness-method.md section 8 and soundness/CHANGELOG.md revision 6 (book Theorems 25.2.1, 31.2.1; Sharp and
Grubbs, ePrint 2026/2615, Theorem 6.6); the category 5 target, the larger-field and longer-digest rows and the cost
scalings are Original (the Ycash developers, 2026), docs/decision-security-category.md.

What the calculator cannot express, computed here from its functions (stated in the decision record, section 9):
  * a category 5 target (targets.py has cat1 and cat3): built here as a SecurityTarget(256, 128, 256, 512);
  * challenge fields above 256 bits for system A's rows (current.a_config fixes 256): the config is copied and its
    field_bits / ext_bytes set;
  * digests other than 256 bits in the size models (FsParams is frozen at 256 in the row builders): replaced;
  * system B's algebraic terms at fields other than 256 bits (johnson.FIELD_BITS is a module constant): the
    counts of johnson.terms are re-read against the field here;
  * spBCS QROM bits at 48- and 64-byte digests and 96 / 128 QROM bits: spbcs.SpbcsTree takes both as fields.
"""

from __future__ import annotations

import copy
import dataclasses
import math

from yugen_soundness import binius64, current as cu, johnson, revision5 as r5, revision6 as r6, spbcs, whir, wi
from yugen_soundness.compose import FsParams
from yugen_soundness.shipping import OTHER_ROUNDS
from yugen_soundness.targets import CAT1, CAT3, SecurityTarget, _digest_proven

PROOFS = 20_000  # MAX_TREE_PROOFS, specification section 2 (SPEC-109)
CAT5 = SecurityTarget(name="cat5", nist_category=5, classical_chain=256.0, quantum_chain=128.0, attack_bits=256.0,
                      digest_attack=512, digest_proven=_digest_proven(256.0))
TARGETS = (CAT1, CAT3, CAT5)
DIGEST = {1: 256, 3: 384, 5: 512}  # attack rule H (soundness-method.md 8.3), extended to category 5 here
FIELDS = (256, 384, 512)
K_A = 87 + OTHER_ROUNDS  # system A's zero-knowledge leaf: 87 listed rounds + 512 (revision 6)
K_B = cu.B_ROW_BUDGET  # 600 challenges a proof (revision 4)

# Measured anchors (M)
A_ZK_LEAF_BYTES = 600_340  # zero-knowledge leaf at 226/157/154/154, rate 1/4 (design-basis 2a; yugen-proof-a-zk 17.4)
A_NODE_BYTES = 875_309  # M of 7 S(9) children, 2^27 stack, rate 1/2 (yugen-proof-a recursion.md 9.10)
A_E2_CORE_S = 4_120  # system A's bundle layer at N = 1,500 (recursion.md 9.10; M nodes, E model)
B_LEAF_BYTES = 583_680  # form T leaf, 184 queries, 32-byte salts (yugen-proof-b2 parameters.md 8.3, M)
B_NODE_BYTES = 538_272  # 2^23-word node circuit at 184 queries, all-256 (parameters.md 2a.5, M)
B_E2_SHA256 = (13_000, 18_600)  # 184 queries, SHA-256, spBCS + route S (parameters.md 9.4, E)
B_E2_BLAKE3 = (6_700, 9_500)  # 184 queries, BLAKE3 (parameters.md 9.4, E)
B_SLOT_SHA256_AND = 6.5e6  # the category 1 slot, SHA-256 (parameters.md 9.2 (c), C + E)
B_SLOT_CORE_S_2_23 = (5.8, 8.7)  # core-seconds a slot padded to 2^23 AND rows (parameters.md 9.4, E)
E2_CORE_S = 7_680  # eight 16-core hosts for 60 s
HOST_CORE_S = 16 * 60


def target(T):
    return cu.target(T, proofs=PROOFS)


def fs_for(T, c1=math.log2(6.0)):
    return FsParams(digest_bits=DIGEST[T.nist_category], qrom_c1_log2=c1)


def is_query(r) -> bool:
    return r.name.startswith("query") or r.name == "final"


# --- needs --------------------------------------------------------------------------------------------------


def needs() -> list[str]:
    out = ["## 1. Per-round need, tree of 20,000 proofs (union bound, soundness-method.md 8.5b), no grinding", "",
           "| Target | Classical chain | QROM chain | A: C (k = 599) | A: Q (C1 = 6) | B: C (k = 600) | G | Binding | "
           "Digest, attack rule | Digest, proven rule (whole bytes) | Proven classical cap at the attack-rule digest |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for T in TARGETS:
        t = target(T)
        ca, qa = t._cq(87, fs_for(T))  # ProofTreeTarget adds OTHER_ROUNDS
        cb, _ = t._cq(K_B - OTHER_ROUNDS, fs_for(T))
        lam = DIGEST[T.nist_category]
        cap = (lam - 1 - math.log2(3.5)) / 2
        out.append(f"| {T.name} | {T.classical_chain:.0f} | {T.quantum_chain:.0f} | {ca:.2f} | {qa:.2f} | {cb:.2f} | "
                   f"{T.attack_bits:.0f} | C | {lam} | {T.digest_proven} | {cap:.1f} (short of {T.classical_chain:.0f} by "
                   f"{T.classical_chain - cap:.1f}) |")
    return out


# --- system A -----------------------------------------------------------------------------------------------


def a_cfg(row, log_n, rate, salt, T, fb, queries=None):
    c = cu.a_config(row, log_n, rate, salt, queries)
    c.field_bits = fb
    c.ext_bytes = fb // 8
    c.fs = dataclasses.replace(c.fs, digest_bits=DIGEST[T.nist_category])
    return c


def a_leaf(T, fb, row=cu.ROW6):
    t = target(T)
    c = a_cfg(row, cu.A_LEAF_VARS, cu.A_LEAF_RATE, 64, T, fb)
    try:
        c = wi.solve(c, "A", t, wi.A_WALLET_ZK)
    except ValueError as e:
        rs = wi.rounds(c, "A", wi.A_WALLET_ZK)
        alg = min((r for r in rs if not is_query(r)), key=lambda r: r.effective_bits)
        return {"fail": str(e).split(": ", 1)[1], "alg": alg}
    rs = wi.rounds(c, "A", wi.A_WALLET_ZK)
    alg = min((r for r in rs if not is_query(r)), key=lambda r: r.effective_bits)
    need = t.need_bits(len(rs), c.fs)
    return {"q": list(c.queries), "need": need, "weakest": min(r.effective_bits for r in rs), "alg": alg,
            "model": wi.size_bytes(c, "A")["total"], "cfg": c}


def a_node(T, fb, log_n=27, rate=1, row=r5.ROW9):
    """Row 9 by shape: the rule counts at the need, raised until every round meets it, then trimmed (as
    revision5.minimal_counts, with the field and digest of the target)."""
    t = target(T)
    c = a_cfg(row, log_n, rate, 0, T, fb)
    rs = whir.rounds(c)
    need = t.need_bits(len(rs), c.fs)
    alg = min((r for r in rs if not is_query(r)), key=lambda r: r.effective_bits)
    if alg.effective_bits < need:
        return {"fail": f"round {alg.name} gives {alg.effective_bits:.1f} < {need:.1f} bits", "alg": alg}
    c.queries = r5.rule_counts(c, need)
    for _ in range(64):
        bad = [r for r in whir.rounds(c) if is_query(r) and r.effective_bits < need]
        if not bad:
            break
        for r in bad:
            c.queries[r5._level_of(r, c)] += 1
    for i in range(len(c.queries)):
        while True:
            c.queries[i] -= 1
            if min(r.effective_bits for r in whir.rounds(c)) < need:
                c.queries[i] += 1
                break
    extra = cu.a_extra_node()[0] * (fb / 256)  # non-opening bytes: field elements (E: scaled by element size)
    return {"q": list(c.queries), "need": need, "weakest": min(r.effective_bits for r in whir.rounds(c)), "alg": alg,
            "model": whir.size_bytes(c)["total"] + extra, "keccak": r5.keccak_total(c), "cfg": c}


def a_tables() -> list[str]:
    out = ["", "## 2. System A (leanVM, WHIR, unique decoding, true rates)", "",
           "Zero-knowledge wallet leaf: row 6's schedule (folds 5, 3; reductions 1, 1; residual 2^10), W-I, rate 1/4, 2^22 "
           "stack, 64-byte salts, every zero-knowledge round of `wi.A_WALLET_ZK` (the row revision 6 certifies). Node: row 9 "
           "(folds 6, 3; reductions 3, 3; residual 2^5), rate 1/2, stack 2^27 (and the worst shape over 2^24 to 2^30). "
           "Sizes: the measured anchor plus the model's difference from the category 1 row (E).", "",
           "| Target | Field | Leaf queries | Leaf need | Leaf weakest | Weakest algebraic (leaf) | Leaf KiB (E) | Node queries (2^27) | "
           "Node weakest algebraic | Node KiB (E) | Node Keccak-f to verify (E) | Worst node over 2^24..2^30 | Node at rate 1/4: queries; KiB (E) |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    base_leaf = a_leaf(CAT1, 256)["model"]
    base_node = a_node(CAT1, 256)
    for T in TARGETS:
        for fb in FIELDS:
            if T is CAT1 and fb > 256:
                continue
            lf, nd = a_leaf(T, fb), a_node(T, fb)
            if "fail" in lf:
                out.append(f"| {T.name} | 2^{fb} | **fails**: {lf['fail']} | | | {lf['alg'].name}: {lf['alg'].effective_bits:.1f} | | "
                           f"{'fails' if 'fail' in nd else nd['q']} | {nd['alg'].name}: {nd['alg'].effective_bits:.1f} | | | |")
                continue
            worst = None
            for m in range(24, 31):
                x = a_node(T, fb, m)
                if "fail" in x:
                    worst = f"fails at 2^{m}"
                    break
                if worst is None or x["alg"].effective_bits < worst[1]:
                    worst = (m, x["alg"].effective_bits)
            wtxt = worst if isinstance(worst, str) else f"2^{worst[0]}: algebraic {worst[1]:.1f}"
            leaf_b = A_ZK_LEAF_BYTES + lf["model"] - base_leaf
            node_b = A_NODE_BYTES * nd["model"] / base_node["model"]
            n4 = a_node(T, fb, 27, 2)
            n4t = f"{', '.join(map(str, n4['q']))}; {A_NODE_BYTES * n4['model'] / base_node['model'] / 1024:,.0f}"
            out.append(f"| {T.name} | 2^{fb} | {', '.join(map(str, lf['q']))} | {lf['need']:.2f} | {lf['weakest']:.2f} | "
                       f"{lf['alg'].name}: {lf['alg'].effective_bits:.1f} | {leaf_b / 1024:,.0f} | {', '.join(map(str, nd['q']))} | "
                       f"{nd['alg'].effective_bits:.1f} | {node_b / 1024:,.0f} | {nd['keccak']:,} ({nd['keccak'] / base_node['keccak']:.2f}x) | {wtxt} | {n4t} |")
    out += ["", "Smallest challenge field at each target (A): the weakest algebraic round at 2^256 is the leaf's fold0.0 "
            f"(232.0 bits; the error `2^24 / |F|`), so the field must give need + 24 bits: cat1 "
            f"{a_leaf(CAT1, 256)['need'] + 24:.1f}, cat3 {a_leaf(CAT3, 256)['need'] + 24:.1f}, cat5 {a_leaf(CAT5, 384)['need'] + 24:.1f} "
            "bits (nodes of 2^30 add 6: see the worst-node column)."]
    return out


# --- system B -----------------------------------------------------------------------------------------------


def b_need(T) -> float:
    return binius64.tree_need(T, [(PROOFS, K_B)], fs_for(T))


def b_terms_at(route, need, m, fb, rho=1 / 8):
    """johnson.row's terms (leaf at 2^22 lifted, node at 2^31) re-read at a field of fb bits."""
    shift = int(round(math.log2(8 * rho)))
    leaf = johnson.terms(route, johnson.LOG_E_LEAF - shift, m, rho)
    node = johnson.terms(route, johnson.LOG_E_NODE - shift, m, rho, mask=False, index_rounds=0)
    w = min(leaf + node, key=lambda t: fb - math.log2(t.count))
    return w.name, fb - math.log2(w.count)


def b_best_johnson(need, fb, rho=1 / 8):
    best = None
    for m in range(3, 400):
        qb = johnson.query_bits(m, rho)
        name, bits = b_terms_at("dkt", need, m, fb, rho)
        if bits >= need:
            q = math.ceil(need / qb)
            if best is None or q < best[0]:
                best = (q, m, bits)
    return best


def b_leaf_model(T, q, fb, salt=64):
    v = binius64.MIXED_T_W1
    p = binius64.leaf_proof(v, 3, q)
    p.ext_bytes = fb // 8
    p.mask_bytes = [fb // 8, fb // 8]
    p.oracle_bytes = [16, fb // 8]
    p.salt_bytes = salt
    p.fs = FsParams(digest_bits=DIGEST[T.nist_category])
    return binius64.size_model(p) + binius64.other_bytes(v, True) * fb / 256


def b_node_model(T, q, fb, log_words=27, rate=3):
    v = binius64.ALL256_W1
    p = binius64.node_proof(v, log_words, rate, q)
    p.ext_bytes = fb // 8
    p.oracle_bytes = [fb // 8]
    p.fs = FsParams(digest_bits=DIGEST[T.nist_category])
    p = binius64.best_arities(p)
    return binius64.size_model(p) + binius64.other_bytes(v, False) * fb / 256


def b_tables() -> list[str]:
    out = ["", "## 3. System B (Binius64, FRI-Binius / BaseFold, rate 1/8)", "",
           "Need from `binius64.tree_need` at 600 challenges a proof, 20,000 proofs, C1 = 6 (spBCS). Unique decoding: "
           "`ceil(need / -log2((1 + rho)/2))` (certified form). Weakest algebraic term: `johnson.terms` (unique decoding; "
           "leaf lifted to 2^22, node 2^31 at rate 1/8) read at the field. Johnson rows: DKT26 route, smallest query count "
           "over m, CANDIDATE only (binius-johnson-row.md). Sizes: measured anchor times the model's ratio to category 1 (E).", "",
           "| Target | Need | Field | UD queries (1/8) | UD queries (1/16) | Weakest algebraic, UD | Meets | Leaf KiB (E, 64-byte salts, without route S) | "
           "Node KiB, 2^27 words (E) | Node at rate 1/16: KiB (E) | Johnson DKT26 candidate: queries, m, weakest |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    b1 = b_leaf_model(CAT1, 184, 256, salt=32)
    n1 = b_node_model(CAT1, 184, 256, 23)
    for T in TARGETS:
        need = b_need(T)
        for fb in FIELDS:
            if T is CAT1 and fb > 256:
                continue
            q8, q16 = binius64.queries_for(need, 3), binius64.queries_for(need, 4)
            name, bits = b_terms_at("ud", need, None, fb)
            ok = bits >= need
            leaf = B_LEAF_BYTES * b_leaf_model(T, q8, fb) / b1
            node = B_NODE_BYTES * b_node_model(T, q8, fb) / n1
            node16 = B_NODE_BYTES * b_node_model(T, q16, fb, 27, 4) / n1
            j = b_best_johnson(need, fb)
            jt = (f"{j[0]}, m = {j[1]}, {j[2]:.1f}; leaf {B_LEAF_BYTES * b_leaf_model(T, j[0], fb) / b1 / 1024:,.0f} KiB, "
                  f"node {B_NODE_BYTES * b_node_model(T, j[0], fb) / n1 / 1024:,.0f} KiB") if j else "none meets"
            out.append(f"| {T.name} | {need:.2f} | 2^{fb} | {q8} | {q16} | {name}: {bits:.1f} | {'yes' if ok else '**no**'} | "
                       f"{leaf / 1024:,.0f} | {node / 1024:,.0f} | {node16 / 1024:,.0f} | {jt} |")
    # the field check of the code's own shapes
    out += ["", "Field check with the calculator's own shapes (`current.b_field_check`: measured leaf and a node of 2^30 AND "
            "rows; field needed in bits):", "", "| Target | Need | Leaf weakest at 2^256 | Node weakest at 2^256 | Field needed |",
            "|---|---|---|---|---|"]
    for T in TARGETS:
        need = b_need(T)
        c = cu.b_field_check(need, 256)
        out.append(f"| {T.name} | {need:.2f} | {c['leaf'][0]}: {c['leaf'][1]:.1f} | {c['node 2^30 rows'][0]}: {c['node 2^30 rows'][1]:.1f} "
                   f"| {max(c['leaf'][3], c['node 2^30 rows'][3])} |")
    return out


# --- QROM (spBCS, Sharp-Grubbs Theorem 6.6 (2)) and classical hash term ----------------------------------------------


def qrom_tables() -> list[str]:
    out = ["", "## 4. QROM bits of the tree, Sharp-Grubbs Theorem 6.6 (2), spBCS with SHAKE256 streams (calculator's "
           "`spbcs.SpbcsTree`, N = 20,000)", "",
           "e = the per-round need of section 1 (the certified rows meet it with a small margin). q_IOP scaled with the "
           "query counts (E). Condition Q: QROM bits >= the QROM chain.", "",
           "| Target | System | Digest (bytes) | e | IOP term | Hash term | QROM bits | Target | Margin | Stream term (log2) | "
           "Hash term at 32-byte digests | Classical need, SG26 ROM bound, every t (Q-5) | for t >= k_q |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for T in TARGETS:
        db = DIGEST[T.nist_category] // 8
        for sysname, counts, e in (("A", r6.a_counts(), a_leaf(T, 256 if T is not CAT5 else 384)["need"]), ("B", r6.b_counts(), b_need(T))):
            scale = e / (a_leaf(CAT1, 256)["need"] if sysname == "A" else b_need(CAT1))
            k = dataclasses.replace(counts, q_iop=int(counts.q_iop * scale), stream_bytes=max(counts.stream_bytes, db))
            q = spbcs.SpbcsTree(k, spbcs.FORMS[0], e, PROOFS, db, T.quantum_chain)
            q32 = spbcs.SpbcsTree(k, spbcs.FORMS[0], e, PROOFS, 32, T.quantum_chain)
            out.append(f"| {T.name} | {sysname} | {db} | {e:.2f} | {q.iop:.2f} | {q.hash:.2f} | {q.bits:.2f} | {T.quantum_chain:.0f} | "
                       f"{q.margin:+.2f} | {q.stream_term_log2:.1f} | {q32.hash:.2f} | "
                       f"{spbcs.classical_need(k, PROOFS, T.classical_chain):.2f} | {spbcs.classical_need(k, PROOFS, T.classical_chain, True):.2f} |")
    out += ["", "Smallest digest for the QROM hash term alone (A's counts, c' = 2,397): "
            + "; ".join(f"{T.name} {_min_digest(T)} bits" for T in TARGETS) + "."]
    return out


def _min_digest(T) -> int:
    k = r6.a_counts()
    for db in range(16, 80):
        if spbcs.SpbcsTree(k, spbcs.FORMS[0], 1e9, PROOFS, db, T.quantum_chain).hash >= T.quantum_chain:
            return 8 * db
    return -1


# --- zero knowledge: salts -----------------------------------------------------------------------------------------


def zk_tables() -> list[str]:
    out = ["", "## 5. Zero knowledge of leaf proofs, Theorem 6.6 (3) (everlasting, QROM), the pool of 2^20 proofs, proof salt 64 B",
           "", "Every figure is the bound minus Q eps_hvzk (open, zk-quantum.md 5). t = hash queries before the last proof "
           "= 2^(QROM chain).", "",
           "| Digest b (B) | Leaf salt b_l (B) | t | A: pool | B: pool | Largest term |", "|---|---|---|---|---|---|"]
    for db, tq in ((32, 64.0), (48, 96.0), (64, 128.0)):
        for bl in (64, 72, 80, 96, 112, 128):
            if bl < db:
                continue
            a = spbcs.eps_zk(r6.a_counts(), tq, 20.0, 64, bl, db)
            b = spbcs.eps_zk(r6.b_counts(), tq, 20.0, 64, bl, db)
            terms = {"salt": a.salt_term, "collision": a.collision_term, "key": a.key_term, "leaf": a.leaf_term}
            out.append(f"| {db} | {bl} | 2^{tq:.0f} | {_p(a.total_log2)} | {_p(b.total_log2)} | {max(terms, key=terms.get)} |")
    out += ["", "Proof salt b_s at t = 2^128, the pool: " + "; ".join(
        f"{bs} B: A {_p(spbcs.eps_zk(r6.a_counts(), 128.0, 20.0, bs, 128, 64).total_log2)}" for bs in (32, 48, 64, 80))]
    out += ["", "Proposed salt rows (pool of 2^20 proofs; Theorem 6.6 (3) and (4), L = 2^24 bits):", "",
            "| Target | Digest b | Proof salt b_s | Leaf salt b_l | A: ZK (3) | B: ZK (3) | A: WI (4) | B: WI (4) |", "|---|---|---|---|---|---|---|---|"]
    for name, db, tq, bs, bl in (("cat1 (D-b)", 32, 64.0, 64, 64), ("cat3", 48, 96.0, 64, 96), ("cat5", 64, 128.0, 80, 112)):
        a, b = r6.a_counts(), r6.b_counts()
        out.append(f"| {name} | {db} | {bs} | {bl} | {_p(spbcs.eps_zk(a, tq, 20.0, bs, bl, db).total_log2)} | "
                   f"{_p(spbcs.eps_zk(b, tq, 20.0, bs, bl, db).total_log2)} | {_p(spbcs.eps_wi_log2(a, 20.0, 24.0, bs, bl, db))} | "
                   f"{_p(spbcs.eps_wi_log2(b, 20.0, 24.0, bs, bl, db))} |")
    return out


def _p(x: float) -> str:
    return "1 (vacuous)" if x >= 0 else f"2^{x:.1f}"


# --- Falcon-1024 hash-to-point -------------------------------------------------------------------------------------


def falcon_tables() -> list[str]:
    from fractions import Fraction
    p = Fraction(61445, 65536)
    out = ["", "## 6. Falcon hash-to-point draws K (probability of fewer than n accepted draws; exact binomial tail)", "",
           "| n | K | Output bytes | SHAKE256 permutations (rate 136) | P(run out) |", "|---|---|---|---|---|"]
    kmin = 1024
    while True:
        t = sum(math.comb(kmin, i) * p**i * (1 - p) ** (kmin - i) for i in range(1024))
        if math.log2(t.numerator) - math.log2(t.denominator) <= -178:
            break
        kmin += 2
    for n, ks in ((512, (680,)), (1024, (1176, 1224, 1250, kmin, 1292, 1330))):
        for K in ks:
            tail = sum(math.comb(K, i) * p**i * (1 - p) ** (K - i) for i in range(n))
            lg = math.log2(tail.numerator) - math.log2(tail.denominator)
            out.append(f"| {n} | {K} | {2 * K} | {math.ceil(2 * K / 136)} | 2^{lg:.0f} |")
    return out


# --- E2 and capacity ------------------------------------------------------------------------------------------------


def cost_tables() -> list[str]:
    out = ["", "## 7. In-circuit verification and N = 1,500 (E2: 7,680 core-seconds, eight 16-core hosts, 60 s)", "",
           "Method (E). System A: the measured 4,120 core-seconds at category 1 times the per-child factor "
           "f = s x (q_x / q_1) x h + (1 - s) x a, where s is the query-proportional share of a verified child "
           "(Keccak-f x measured cycles per modelled Keccak-f, revision5.cycles_per_keccak), h the Keccak-f per opened "
           "position relative to category 1, a the field-arithmetic factor. Proving time follows committed words "
           "(recursion.md 9.10 reading 2), so the total scales by f within the step function of the padded stack. "
           "System B: the category 1 slot (6.5 M AND rows with SHA-256) times the query ratio and the hash factor of the "
           "admissible hash, padded to the next power of two, at the measured core-seconds a padded slot.", ""]
    # A
    lf1 = a_leaf(CAT1, 256)
    nd1 = a_node(CAT1, 256)
    cpk = r5.cycles_per_keccak("node")
    s = min(1.0, r5.CHILD_VERIFY[1] * cpk / r5.CHILD_VERIFY[0])
    out += [f"System A: cycles per modelled Keccak-f of a child {cpk:.1f}; query-proportional share s = {s:.2f} (E).", "",
            "| Target | Field | q ratio (node level 0) | h | a | f | A core-seconds (E) | A hosts for 60 s |", "|---|---|---|---|---|---|---|---|"]
    rows_a = {}
    for T, fb, h, a in ((CAT1, 256, 1.0, 1.0), (CAT3, 256, 1.0, 1.0), (CAT3, 384, 1.25, 2.25), (CAT5, 384, 1.25, 2.25), (CAT5, 512, 1.5, 3.0)):
        nd = a_node(T, fb)
        qr = sum(nd["q"]) / sum(nd1["q"])
        f = s * qr * h + (1 - s) * a
        cs = A_E2_CORE_S * f
        rows_a[(T.name, fb)] = cs
        out.append(f"| {T.name} | 2^{fb} | {qr:.2f} | {h} | {a} | {f:.2f} | {cs:,.0f} | {cs / HOST_CORE_S:.1f} |")
    # B
    out += ["", "System B, certified unique-decoding rows (h: in-circuit AND rows a Merkle opening against SHA-256 at "
            "category 1; SHA-384 / SHA-512 compression estimated at 455 AND rows (80 rounds of 64-bit words against "
            "SHA-256's 364 C for 64), one compression a 96- or 128-byte node in compression-function mode, leaves in "
            "128-byte blocks; SHAKE256 at 600 AND rows a Keccak-f (C by structure), one permutation a 96-byte node, two a "
            "128-byte node with a tag byte beyond 135 bytes). 'Being counted': the system B builder is counting these rows.", "",
            "| Target | Hash | Queries | Slot AND rows (E) | Padded | Core-seconds a slot (E) | B, N = 1,500 (E) | Hosts for 60 s | "
            "With D-6 (cost follows rows, E) |", "|---|---|---|---|---|---|---|---|---|"]
    path, leafh = 0.588 + 0.077, 0.249 + 0.018  # pin's split (parameters.md 9.2 (a)), Merkle 93.2 %
    def hfac(node, perbyte):
        return (path * node + leafh * perbyte + 0.067) / (path + leafh + 0.067)
    hashes = {"SHA-256": hfac(1.0, 1.0), "BLAKE3": hfac(168 / 364, 168 / 364),
              "SHA-384 (SHA-512 compression)": hfac(455 / 364, (455 / 128) / (364 / 64)),
              "SHAKE256-384": hfac(600 / 364, (600 / 136) / (364 / 64)),
              "SHA-512": hfac(455 / 364, (455 / 128) / (364 / 64)), "SHAKE256-512 (one-byte tag)": hfac(600 / 364, (600 / 136) / (364 / 64))}
    rows_b = {}
    for T, fb, hname, fieldf, qj in ((CAT1, 256, "SHA-256", 1.0, None), (CAT1, 256, "BLAKE3", 1.0, None),
                                     (CAT3, 256, "SHA-384 (SHA-512 compression)", 1.0, None), (CAT3, 256, "SHAKE256-384", 1.0, None),
                                     (CAT3, 384, "SHA-384 (SHA-512 compression)", 1.3, "J"),
                                     (CAT5, 512, "SHA-512", 1.6, None), (CAT5, 512, "SHAKE256-512 (one-byte tag)", 1.6, None),
                                     (CAT5, 384, "SHA-512", 1.3, "J")):
        q = binius64.queries_for(b_need(T), 3) if qj is None else b_best_johnson(b_need(T), fb)[0]
        rows = B_SLOT_SHA256_AND * (q / 184) * hashes[hname] * fieldf
        if qj:
            hname = f"{hname}, 2^{fb} field, Johnson CANDIDATE"
        pad = 2 ** math.ceil(math.log2(rows))
        lo, hi = (x * pad / 2**23 for x in B_SLOT_CORE_S_2_23)
        tot = (1_504 * lo + 435 + 208 * lo * 2, 1_504 * hi + 435 + 208 * hi * 2)  # levels 1, 2 + batching ~ 2 slots a child
        dlo, dhi = (x * rows / 2**23 for x in B_SLOT_CORE_S_2_23)
        dtot = (1_504 * dlo + 435 + 208 * dlo * 2, 1_504 * dhi + 435 + 208 * dhi * 2)
        if T is CAT1 and hname == "SHA-256":
            tot = B_E2_SHA256
        if T is CAT1 and hname == "BLAKE3":
            tot = B_E2_BLAKE3
        rows_b[(T.name, hname)] = tot
        out.append(f"| {T.name} | {hname} | {q} | {rows / 1e6:.1f} M | 2^{int(math.log2(pad))} | {lo:.1f} to {hi:.1f} | "
                   f"{tot[0]:,.0f} to {tot[1]:,.0f} | {tot[0] / HOST_CORE_S:.0f} to {tot[1] / HOST_CORE_S:.0f} | "
                   f"{dtot[0]:,.0f} to {dtot[1]:,.0f} |")
    out += ["", "Both systems, hosts of 16 cores for 60 s (A + B; E):", "", "| Profile | A | B | Total core-seconds | Hosts | Against E2's 8 |",
            "|---|---|---|---|---|---|"]
    for lab, ak, bk in (("cat1, BLAKE3 (as decided)", ("cat1", 256), ("cat1", "BLAKE3")),
                        ("cat1, SHA-256", ("cat1", 256), ("cat1", "SHA-256")),
                        ("cat3, 256-bit field, SHA-384", ("cat3", 256), ("cat3", "SHA-384 (SHA-512 compression)")),
                        ("cat5, A 2^384 field, B 2^512 field, SHA-512", ("cat5", 384), ("cat5", "SHA-512"))):
        a = rows_a[ak]
        b = rows_b[bk]
        out.append(f"| {lab} | {a:,.0f} | {b[0]:,.0f} to {b[1]:,.0f} | {a + b[0]:,.0f} to {a + b[1]:,.0f} | "
                   f"{math.ceil((a + b[0]) / HOST_CORE_S)} to {math.ceil((a + b[1]) / HOST_CORE_S)} | "
                   f"{(a + b[0]) / E2_CORE_S:.1f}x to {(a + b[1]) / E2_CORE_S:.1f}x |")
    return out


def capacity_tables() -> list[str]:
    per_tx = 200.0  # a transfer record without value balance or package (specification 15.1, C); the tree adds a little
    out = ["", "## 8. Transfers a block (E)", "",
           f"Per bundled transfer: {per_tx:.0f} block bytes (a transfer record without value balance or on-chain package, "
           "specification 15.1; the tree encoding of 15.2 and the anchor table are left out, so capacities are upper figures). Bundles may use W - LEAF_RESERVE = 2,850,000 weight and 1,982,544 bytes (W5); one "
           "tree, one root proof a system. Capacity = min(bytes, (2,850,000 - root proofs) / bytes a transfer, 16,384).", "",
           "| Profile | Root proof A (B) | Root proof B (B) | Both within PROOF_BYTES_MAX (W1) | Transfers by weight | By bytes | Capacity |",
           "|---|---|---|---|---|---|---|"]
    n1 = a_node(CAT1, 256)
    bn1 = b_node_model(CAT1, 184, 256, 23)
    for lab, T, fa, ra, fbb, rb in (("cat1, nodes at 1/2 and 1/8 (as built)", CAT1, 256, 1, 256, 3),
                                    ("cat3, nodes at 1/2 and 1/8", CAT3, 256, 1, 256, 3),
                                    ("cat3, nodes at 1/4 and 1/16", CAT3, 256, 2, 256, 4),
                                    ("cat5, A 2^384 node at 1/4, B 2^512 node at 1/16", CAT5, 384, 2, 512, 4)):
        pa = A_NODE_BYTES * a_node(T, fa, 27, ra)["model"] / n1["model"]
        q = binius64.queries_for(b_need(T), rb)
        pb = B_NODE_BYTES * b_node_model(T, q, fbb, 27, rb) / bn1
        w = max(0.0, (2_850_000 - pa - pb) / per_tx)
        bts = 1_982_544 / per_tx
        ok = "yes" if max(pa, pb) <= 1_835_008 else "**no**"
        out.append(f"| {lab} | {pa:,.0f} | {pb:,.0f} | {ok} | {w:,.0f} | {bts:,.0f} | {min(w, bts, 16_384):,.0f} |")
    return out


def main() -> None:
    lines = ["# Category study tables (generated by category-study/category_study.py; calculator revision 6 as a library)", ""]
    for part in (needs, a_tables, b_tables, qrom_tables, zk_tables, falcon_tables, cost_tables, capacity_tables):
        lines += part()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
