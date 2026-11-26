"""Revision 6 of the calculator (2026-11-19): the spBCS transcript form and Sharp-Grubbs Theorem 6.6.

What changes against revision 5 (soundness/CHANGELOG.md, revision 6):
  * Condition Q is evaluated with Theorem 6.6 (2) of Sharp, Grubbs, ePrint 2026/2615 (spbcs.py; Published) for
    the spBCS transcript form of docs/qrom-compilation.md section 4 (lead decision D-a): C1 = 6 and the hash
    constant 6 c', c' = max(2, c) + n_J + 1 from each system's message counts, with the verifier's k_q queries
    added to t exactly. Default: a SHAKE256 stream in both systems (the published theorem as is); system B's
    documented alternative, a counter-mode SHA-256 stream, doubles t (Lemma X; Adapted). Theorem Q of revision 5
    (forms X and C, qrom.py) is kept as the record; form C's constants 24 / 240 are unproved (referee 1.5).
  * The zero-knowledge errors are Theorem 6.6 (3) (everlasting, QROM, Q adaptively chosen proofs) and 6.6 (4)
    (unconditional witness indistinguishability), with 64-byte leaf salts and a 64-byte proof salt (D-b),
    for leaf proofs only (D-c). eps_hvzk is open and is never filled in.
  * System A's zero-knowledge defaults are the merged code's: 11 bus layers, 52 claims (wi.A_WALLET_ZK).
  * leanVM's eps_aff as CWYZ26 Theorem 4.10, (4.13) (affine.py), as a cross-check column: no certified row
    uses it (every Yugen row is in unique decoding, Theorem S0).

Message counts (spbcs.TranscriptCounts; estimates (E) until the transcript modules report them):
  A  verifier messages = the largest round list of system A's rows (the zero-knowledge leaf: 87) plus
     OTHER_ROUNDS (512); one prover message before each; m = 2 oracle strings a message (upper figure);
     q_IOP = the largest sum of query counts over the rows; l_max = the longest oracle string in positions
     (rows of 2^k_0 elements at level 0); n_pos = every position of every tree of the zero-knowledge leaf.
  B  verifier messages = the row budget (600 challenges a proof, current.B_ROW_BUDGET); one prover message
     before each; m = 2; q_IOP = 184 queries in each of 6 trees (two round oracles, four fold trees:
     binius64.B64Proof); l_max = 2^31 positions (a node of 2^30 AND rows at rate 1/8); n_pos = the two round
     oracles (2^17 and 2^20 elements at rate 1/8) and the four fold trees, all salted (zk-quantum.md 4).

Provenance: SG26's bounds Published; Lemma X Adapted; the tree accounting and the message-count model
Original (the Ycash developers, 2026), REFERENCES.md O-13 and O-27.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import affine, binius64, current as cu, params, qrom, revision5 as r5, spbcs, whir, wi
from .bounds import Regime, pg_johnson_dkt26
from .compose import FsParams
from .shipping import OTHER_ROUNDS
from .targets import CAT1

TREE_PROOFS = r5.TREE_PROOFS
B_QUERIES = 184
B_TREES_LEAF = 6
B_LOG_L_MAX = 31
B_ROUND_ORACLES = (17, 20)  # log2 elements of the zero-knowledge leaf's two round oracles (binius64 leaf layout)
B_RATE = 3
B_ARITIES = (4, 4, 3, 3)
B_FOLD_LEAF_BYTES = 2**4 * 32  # a fold leaf of arity 4 over 32-byte K elements
T_LOG2 = 64.0  # hash queries before the last proof (zk-quantum.md 3; referee section 4 (ii))
POOL_LOG2 = 20.0  # proofs in the pool for the composition figure
WALLET_LOG2 = 16.0  # proofs one wallet makes (an illustrative upper figure)
WITNESS_BITS_LOG2 = 24.0  # L: bits of statement and both witnesses for Theorem 6.6 (4) (upper figure)


# --- message counts --------------------------------------------------------------------------------------


def _a_shapes():
    t = r5.target()
    return r5.leaf_shapes(t) + r5.node_shapes(t)


def a_counts() -> spbcs.TranscriptCounts:
    t = r5.target()
    zk = r5.wi_row("ZK", cu.ROW6, cu.A_LEAF_RATE, r5.ZK_QUERIES, t=t)
    w8 = [r5.wi_row("row 8", r5.ROW8, rate, r5.wi_solve(r5.ROW8, rate, r5.LIST_BITS), t=t) for rate in (2, 1)]
    shapes = _a_shapes()
    listed = max([zk.rounds] + [w.rounds for w in w8] + [s.rounds for s in shapes])
    q_iop = max([sum(zk.queries)] + [sum(w.queries) for w in w8] + [sum(s.rule_q) for s in shapes])
    l_max = 0
    stream = 0
    for s in shapes:
        c = cu.a_config(s.row, s.log_n, s.rate, 0, s.rule_q)
        for i, q in enumerate(c.queries):
            pos_bits = c.vars_at(i) - c.folds[i] + c.log_inv_rates[i]
            l_max = max(l_max, pos_bits)
            stream = max(stream, math.ceil(q * pos_bits / 8))
    zc = cu.a_config(cu.ROW6, cu.A_LEAF_VARS, cu.A_LEAF_RATE, 0, list(r5.ZK_QUERIES))
    n_pos = sum(2.0 ** (zc.vars_at(i) - zc.folds[i] + zc.log_inv_rates[i]) for i in range(len(zc.folds)))
    leaf_bytes = (2 ** zc.folds[0]) * zc.base_bytes
    return spbcs.TranscriptCounts("A", listed + OTHER_ROUNDS, listed + OTHER_ROUNDS, 2, q_iop, l_max,
                                  math.log2(n_pos), max(leaf_bytes, 512), max(spbcs.DIGEST_BYTES, stream),
                                  source=f"listed rounds {listed} + OTHER_ROUNDS {OTHER_ROUNDS}")


def b_counts() -> spbcs.TranscriptCounts:
    v = cu.B_ROW_BUDGET
    log_code = max(B_ROUND_ORACLES) + B_RATE
    n_pos = sum(2.0 ** (lg + B_RATE) for lg in B_ROUND_ORACLES)
    depth = log_code
    for a in B_ARITIES:
        depth -= a
        n_pos += 2.0**depth
    stream = math.ceil(B_QUERIES * B_LOG_L_MAX / 8)
    return spbcs.TranscriptCounts("B", v, v, 2, B_QUERIES * B_TREES_LEAF, B_LOG_L_MAX, math.log2(n_pos),
                                  B_FOLD_LEAF_BYTES, max(spbcs.DIGEST_BYTES, stream),
                                  source=f"row budget {v} challenges a proof")


# --- weakest rounds --------------------------------------------------------------------------------------


def b_fs() -> FsParams:
    """System B's Fiat-Shamir parameters for the need: C1 = 6 (spBCS, SHAKE256 stream, revision 6)."""
    return FsParams(digest_bits=256, qrom_c1_log2=math.log2(6.0), qrom_c2_log2=math.log2(6.0 * b_counts().c_prime))


def b_need() -> float:
    return binius64.tree_need(CAT1, [(TREE_PROOFS, cu.B_ROW_BUDGET)], b_fs())


@dataclass
class Certificate6:
    a_e: float
    b_e: float
    a: spbcs.SpbcsTree
    b: spbcs.SpbcsTree
    b_counter: spbcs.SpbcsTree


def certify() -> Certificate6:
    """Condition C on every corrected row (revision 5's certify, with the corrected zero-knowledge counts), then
    condition Q under Theorem 6.6 (2) for each system; raises spbcs.ConditionQFailure if Q fails."""
    c5 = r5.certify()
    b = r5.johnson.row("ud", b_need())
    b_e = min(b.query_bits, b.weakest.bits)
    ac, bc = a_counts(), b_counts()
    return Certificate6(
        c5.a_e, b_e,
        spbcs.require(spbcs.SpbcsTree(ac, spbcs.FORMS[0], c5.a_e, TREE_PROOFS), "system A, spBCS"),
        spbcs.require(spbcs.SpbcsTree(bc, spbcs.FORMS[0], b_e, TREE_PROOFS), "system B, spBCS"),
        spbcs.require(spbcs.SpbcsTree(bc, spbcs.FORMS[1], b_e, TREE_PROOFS), "system B, counter mode"),
    )


# --- leanVM eps_aff cross-check --------------------------------------------------------------------------


@dataclass(frozen=True)
class AffRow:
    level: int
    log_n: int
    log_d: int
    A: int
    bound: affine.AffBound | None
    dkt26_bits: float


def leanvm_eps_aff(johnson_m: float = 10.0) -> list[AffRow]:
    """leanVM as shipped (params.a_leanvm_shipped: GF(2^128), stack 2^20, rate 1/16): per level, (4.13) at the
    calculator's Johnson agreement sqrt(rho) (1 + 1/(2m)), against DKT26's line count at the same point."""
    c = params.a_leanvm_shipped(Regime.JB_DKT26)
    out = []
    for i in range(len(c.folds)):
        m, r = c.vars_at(i), c.log_inv_rates[i]
        n, d, rho = 2**(m + r), 2**m, 2.0**-r
        A = math.ceil(math.sqrt(rho) * (1 + 1 / (2 * johnson_m)) * n)
        out.append(AffRow(i, m + r, m, A, affine.best(n, d, A, c.field_bits), -pg_johnson_dkt26(m + r, m, johnson_m, c.field_bits)))
    return out


# --- tables ----------------------------------------------------------------------------------------------


def _p(x: float) -> str:
    return "1 (vacuous)" if x >= 0 else f"2^{x:.1f}"


def tables() -> list[str]:
    cert = certify()
    ac, bc = cert.a.counts, cert.b.counts
    out = [f"Revision 6. Tree of {TREE_PROOFS:,} proofs, 256-bit digests, no grinding, unique decoding. Condition Q under "
           "Sharp-Grubbs (ePrint 2026/2615) Theorem 6.6 (2) for the spBCS transcript (qrom-compilation.md 4); zero "
           "knowledge under Theorem 6.6 (3), (4) for leaf proofs (zk-quantum.md 3).", ""]
    out += ["## Message counts (SG26 Definition I.1; estimates until the transcript modules report them)", "",
            "| System | Source | N_V | N_P | m | c | c' | 6 c' | q_IOP | log2 l_max | k_q | longest stream (B) | n_pos (leaf) | L_leaf (B) |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in (ac, bc):
        out.append(f"| {k.system} | {k.source} | {k.verifier_messages} | {k.prover_messages} | {k.oracles_per_message} | {k.c:,} | "
                   f"{k.c_prime:,} | {6 * k.c_prime:,} (2^{math.log2(6 * k.c_prime):.2f}) | {k.q_iop:,} | {k.log2_l_max} | "
                   f"{k.k_q:,} (2^{math.log2(k.k_q):.2f}) | {k.stream_bytes} | 2^{k.n_pos_log2:.2f} | {k.leaf_bytes} |")
    out += ["", f"## QROM bits of the tree (Theorem 6.6 (2), N = {TREE_PROOFS:,}; condition Q: >= 64, hard failure)", "",
            "| System, transcript form | Provenance | e (bits) | C1 | C2 = 6 c' (x 8 with Lemma X) | IOP term | Hash term | Stream term (log2, any t) | QROM bits | Margin over 64 |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for lab, q, prov in (("A, spBCS, SHAKE256 stream", cert.a, "Published"),
                         ("B, spBCS, SHAKE256 stream (default)", cert.b, "Published"),
                         ("B, spBCS, counter-mode SHA-256 stream", cert.b_counter, "Adapted (Lemma X)")):
        out.append(f"| {lab} | {prov} | {q.e:.2f} | {q.c1:g} | {q.c2:,.0f} | {q.iop:.2f} | {q.hash:.2f} | {q.stream_term_log2:.1f} | "
                   f"{q.bits:.2f} | {q.margin:+.2f} |")
    out += ["", "Records (revision 5, Theorem Q; not certified): "
            + "; ".join(f"{lab} C1 = {f.c1:g}, C2 = {f.c2:g}: {qrom.tree_qrom(f, e, 256, TREE_PROOFS).bits:.2f}"
                        for lab, f, e in (("A form X", qrom.FORMS["A"], cert.a_e),
                                          ("B form C (constants unproved: no write-back)", qrom.FORMS["B"], cert.b_e)))
            + ". Needs: A "
            f"{cert.a.need_e():.2f}, B {cert.b.need_e():.2f} (SHAKE) / {cert.b_counter.need_e():.2f} (counter) bits a round for "
            f"the IOP term alone; condition C binds (B's need {b_need():.2f})."]
    # condition C under the ROM part of Theorem 6.6 (2): finding Q-5
    k_book = 87 + OTHER_ROUNDS
    out += ["", "## Condition C under the ROM part of Theorem 6.6 (2) (finding Q-5; not applied to the certified rows)", "",
            "The certified need uses the book's Theorems 25.2.1 and 31.2.1, `(t + k) eps` with k the rounds, for Construction "
            "25.1.1; for the spBCS transcript the published classical bound is SG26's `(t + k_q)(eps_k + c' (t + k_q)/2^256)`. "
            "At t = 1 that charges the verifier's k_q queries.", "",
            "| System | k_q | Need, every t >= 1 | Need, t >= k_q | Certified need (book, k rounds) | Weakest round | Margin, every t | Margin, t >= k_q |",
            "|---|---|---|---|---|---|---|---|"]
    for k, e in ((ac, cert.a_e), (bc, cert.b_e)):
        n_all, n_kq = spbcs.classical_need(k, TREE_PROOFS), spbcs.classical_need(k, TREE_PROOFS, from_k_q=True)
        book = 128.0 + 1.0 + math.log2(TREE_PROOFS) + math.log2(1 + (k_book if k.system == "A" else cu.B_ROW_BUDGET))
        out.append(f"| {k.system} | {k.k_q:,} | {n_all:.2f} | {n_kq:.2f} | {book:.2f} | {e:.2f} | {e - n_all:+.2f} | {e - n_kq:+.2f} |")
    # zero knowledge
    out += ["", "## Zero knowledge of leaf proofs (Theorem 6.6 (3), everlasting, QROM; 6.6 (4), unconditional WI)", "",
            "Every figure is the stated bound minus the IOP's term (Q eps_hvzk for (3), 2 Q eps_hvzk for (4)): eps_hvzk is open "
            "for both systems (zk-quantum.md 5). eps_ov = 0 (every challenge set a power of two). 64-byte leaf salts "
            f"(eps_leaf = {_p(spbcs.eps_leaf_log2(leaf_bytes=512))} at L_leaf = 512 B).", "",
            "| System | Proof salt b_s (B) | t | One proof | A wallet (2^16 proofs) | The pool (2^20 proofs) | Largest term at the pool | WI (6.6 (4)), pool, L = 2^24 bits |",
            "|---|---|---|---|---|---|---|---|"]
    for k in (ac, bc):
        for bs in (32, 48, 64):
            for t in (64.0, 128.0):
                one = spbcs.eps_zk(k, t, 0.0, proof_salt_bytes=bs)
                wal = spbcs.eps_zk(k, t, WALLET_LOG2, proof_salt_bytes=bs)
                pool = spbcs.eps_zk(k, t, POOL_LOG2, proof_salt_bytes=bs)
                terms = {"salt (4Qt/2^(4 b_s))": pool.salt_term, "collision": pool.collision_term, "key": pool.key_term,
                         "leaf (Q n_pos eps_leaf)": pool.leaf_term}
                big = max(terms, key=terms.get)
                wi_ = spbcs.eps_wi_log2(k, POOL_LOG2, WITNESS_BITS_LOG2, proof_salt_bytes=bs)
                out.append(f"| {k.system} | {bs}{' (D-b)' if bs == 64 else ''} | 2^{t:.0f} | {_p(one.total_log2)} | {_p(wal.total_log2)} | "
                           f"{_p(pool.total_log2)} | {big} | {_p(wi_)} |")
    out += ["", "Leaf salt length (64-byte proof salt, t = 2^64, the pool): "
            + "; ".join(f"b_l = {bl} B: A {_p(spbcs.eps_zk(ac, T_LOG2, POOL_LOG2, leaf_salt_bytes=bl).total_log2)}, "
                        f"B {_p(spbcs.eps_zk(bc, T_LOG2, POOL_LOG2, leaf_salt_bytes=bl).total_log2)}" for bl in (32, 48, 64, 72, 76))
            + ". Node proofs carry no zero-knowledge requirement (D-c)."]
    # eps_aff
    out += ["", "## leanVM's eps_aff (CWYZ26 Theorem 4.10, (4.13)) at leanVM as shipped (GF(2^128), stack 2^20, rate 1/16)", "",
            "Cross-check only: no certified Yugen row uses it (unique decoding everywhere). Agreement at the calculator's "
            "Johnson point sqrt(rho)(1 + 1/20); the witness search is leanVM's `find_witness`.", "",
            "| Level | n | d | A | m | D | M | B | eps_aff (bits) | leanVM's round (eps_aff + 2 l / q, bits) | DKT26 line count (bits) |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in leanvm_eps_aff():
        b = r.bound
        if b is None:
            out.append(f"| {r.level} | 2^{r.log_n} | 2^{r.log_d} | {r.A:,} | | | | | no witness (leanVM's search) | | {r.dkt26_bits:.2f} |")
        else:
            out.append(f"| {r.level} | 2^{r.log_n} | 2^{r.log_d} | {r.A:,} | {b.m} | {b.D} | {b.M} | {b.B:,} | {b.bits:.2f} | "
                       f"{-b.round_log2():.2f} | {r.dkt26_bits:.2f} |")
    ex = affine.eps_aff(2**20, 2**18, 576717, 128, 3, 49, 567980)
    out += ["", f"CWYZ26 Remark 5.3 reproduced: n = 2^20, d = 2^18, A = 576,717, m = 3, D = 49, B = 567,980: M = {ex.M}, "
            f"l = {ex.list_term}, delta = 2^{ex.delta_log2:.2f}, {ex.bits:.2f} bits (the paper: about 125.42)."]
    return out
