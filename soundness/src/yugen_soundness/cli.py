"""Print the soundness and size tables used in docs/framework-selection.md and docs/soundness-method.md."""

from __future__ import annotations

import argparse
import math

from . import design, fri, whir
from .bounds import Regime
from .compose import chain_bits, evaluate
from .targets import CAT1, TARGETS
from .params import (
    QROM_TARGET,
    a_leanvm_shipped,
    a_yugen,
    b_binary_measured,
    b_koalabear_measured,
    b_koalabear_yugen_leaf,
    b_yugen,
)

LAYERS = ["leaf", "bundle", "merge1", "merge2"]
REGIMES = [Regime.UDR, Regime.JB_DKT26]


def _row(name, queries, res, size):
    return (
        f"| {name} | {queries} | {res.classical_bits:.1f} | {res.quantum_bits:.1f} | {res.weakest_round} "
        f"| {size / 1024:.0f} |"
    )


HEADER = "| Configuration | Queries | Classical bits | QROM bits | Weakest round | Size estimate (KiB) |\n|---|---|---|---|---|---|"


def cross_checks() -> list[str]:
    out = ["### Cross-checks against shipped parameters and measurements", "", HEADER]
    for regime in REGIMES:
        c = a_leanvm_shipped(regime)
        res = evaluate(c.name, whir.rounds(c), c.fs)
        out.append(_row(c.name, c.queries, res, whir.size_bytes(c)["total"]))
    for which in ["bench100", "q100"]:
        c = b_koalabear_measured(which)
        res = evaluate(c.name, fri.rounds(c), c.fs)
        out.append(_row(c.name, c.queries, res, fri.size_bytes(c)["total"]))
    c = b_binary_measured()
    res = evaluate(c.name, whir.basefold_rounds(c), c.fs)
    out.append(_row(c.name, c.queries, res, whir.basefold_size(c)["total"]))
    return out


def yugen_tables(target: float) -> list[str]:
    out = []
    for system in ["A", "B"]:
        for regime in REGIMES:
            out += ["", f"### System {system}, {regime.value}, target {target:.0f} QROM bits", "", HEADER]
            layer_q = []
            for layer in LAYERS:
                if system == "A":
                    c = whir.solve(a_yugen(layer, regime), target, quantum=True)
                    res = evaluate(c.name, whir.rounds(c), c.fs)
                    size = whir.size_bytes(c)["total"]
                else:
                    c = whir.basefold_solve(b_yugen(layer, regime), target, quantum=True)
                    res = evaluate(c.name, whir.basefold_rounds(c), c.fs)
                    size = whir.basefold_size(c)["total"]
                layer_q.append(res.quantum_bits)
                out.append(_row(c.name, c.queries, res, size))
            out.append(f"| chain leaf to merge2 | | | {chain_bits(layer_q):.1f} | union bound | |")
    out += ["", f"### System B alternative (KoalaBear FRI, narrow Keccak AIR), leaf, target {target:.0f} QROM bits", "", HEADER]
    for regime in REGIMES:
        c = fri.solve(b_koalabear_yugen_leaf(regime), target, quantum=True)
        res = evaluate(c.name, fri.rounds(c), c.fs)
        out.append(_row(c.name, c.queries, res, fri.size_bytes(c)["total"]))
    return out


def _q(c):
    return ", ".join(map(str, c.queries)) if isinstance(c.queries, list) else str(c.queries)


def _yn(checks):
    return "".join(k for k, v in checks.items() if v) + ("" if all(checks.values()) else " FAIL " + "".join(k for k, v in checks.items() if not v))


def target_table() -> list[str]:
    out = ["### Named targets", "",
           "| Target | NIST | Chain classical (proven) | Per layer | Chain QROM (proven, CMS19 C1=6) | Per layer | "
           "Attack bits per round | Digest, attack rule | Digest, proven rule | Min. challenge field |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for t in TARGETS.values():
        out.append(f"| {t.name} | {t.nist_category} | {t.classical_chain:.0f} | {t.classical_layer:.0f} | {t.quantum_chain:.0f} "
                   f"| {t.quantum_layer:.0f} | {t.attack_bits:.0f} | {t.digest_attack} | {t.digest_proven} | "
                   f"{'GF(2^192)' if t.name == 'cat1' else 'GF(2^256)'} |")
    return out


DHEAD = ("| System | Layer | Regime | Field | Rate | Queries per round | Query grind | Classical (IOP) | QROM (IOP) | Checks "
         "| Size (KiB) | Verify (ms) |\n|---|---|---|---|---|---|---|---|---|---|---|---|")


def _drow(d):
    reg = "UD (proven)" if d.regime is Regime.UDR else "Johnson DKT26 (unconfirmed)"
    return (f"| {d.system} | {d.layer} | {reg} | 2^{d.field_bits} | 1/{2 ** d.rate_log} | {_q(d.config)} | {d.grind_query} "
            f"| {d.result.classical_iop_bits:.1f} | {d.result.quantum_iop_bits:.1f} | {_yn(d.checks)} "
            f"| {d.size_bytes / 1024:.0f} | {d.verify_ms:.1f} |")


def design_tables(rate: int = 2, grind: int = 20) -> list[str]:
    out = target_table()
    for t in TARGETS.values():
        fields = [192, 256] if t.name == "cat1" else [256]
        out += ["", f"### {t.name}: every layer, rate 1/{2 ** rate}, query grind {grind}, digest {t.digest_attack} bits", "", DHEAD]
        for system in ["A", "B"]:
            for regime in REGIMES:
                for fb in fields:
                    for layer in design.LAYERS:
                        out.append(_drow(design.design_point(system, layer, t, regime, rate, fb, grind_query=grind)))
    out += ["", "### Leaf: rate trade at 256-bit challenges, query grind 20 (prover time and memory: estimate on 1 M5 thread)", "",
            "| Target | System | Rate | Queries | Size (KiB) | Verify (ms) | Prove (s) | Measured RSS at GF(2^128) (MB) |",
            "|---|---|---|---|---|---|---|---|"]
    for t in TARGETS.values():
        for system in ["A", "B"]:
            for r in range(1, 5):
                d = design.design_point(system, "leaf", t, Regime.UDR, r, 256, grind_query=20)
                out.append(f"| {t.name} | {system} | 1/{2 ** r} | {_q(d.config)} | {d.size_bytes / 1024:.0f} | {d.verify_ms:.1f} "
                           f"| {design.leaf_prove_seconds(d):.2f} | {design.RSS_MEASURED[system][r] / 1e6:.0f} |")
    out += ["", f"### Leaf: query grinding trade, cat1, 256-bit challenges, rate 1/{2 ** rate}", "",
            "| System | Query grind | Queries | Size (KiB) | Grinding (Keccak-f) | Grinding (s, M5 thread) |", "|---|---|---|---|---|---|"]
    for system in ["A", "B"]:
        for g in (0, 12, 16, 20, 24, 28):
            d = design.design_point(system, "leaf", TARGETS["cat1"], Regime.UDR, rate, 256, grind_query=g)
            out.append(f"| {system} | {g} | {_q(d.config)} | {d.size_bytes / 1024:.0f} | 2^{math.log2(max(1, d.grind_perms)):.1f} "
                       f"| {d.grind_perms / design.KECCAK_F_PER_S:.2f} |")
    out += ["", "### GF(2^128) challenges at cat1: grinding the algebraic rounds would need (unique decoding, rate 1/16)", "",
            "| System | Layer | Weakest algebraic round (bits) | Needed | Grind per algebraic round | Algebraic rounds | Work (Keccak-f) | Hours, M5 thread |",
            "|---|---|---|---|---|---|---|---|"]
    for system in ["A", "B"]:
        for layer in design.LAYERS:
            g = design.min_fold_grinding(system, layer, TARGETS["cat1"], 128)
            out.append(f"| {system} | {layer} | {g['weakest_algebraic_bits']:.1f} | {g['need']:.1f} | {g['fold_grind']} "
                       f"| {g['algebraic_rounds']} | 2^{math.log2(g['grind_perms']):.1f} | {g['grind_seconds_m5'] / 3600:.1f} |")
    out += ["", "### Digest rule: proven-bound digests (cat1 264 bits, cat3 392 bits), leaf, rate 1/4, grind 20", "", DHEAD]
    for t in TARGETS.values():
        for system in ["A", "B"]:
            out.append(_drow(design.design_point(system, "leaf", t, Regime.UDR, 2, 256, grind_query=20, digest_rule="proven")))
    return out


BASIS_RATE = {"leaf": 2, "bundle": 3, "merge1": 3, "merge2": 3}


def _shape(d):
    c = d.config
    if isinstance(c.queries, list):
        return f"WHIR folds {'/'.join(map(str, c.folds))}, final 2^{c.vars_at(len(c.folds))}"
    return f"folding PCS fold {c.fold}, final 2^{c.residual_vars}"


def basis_table() -> list[str]:
    """The design-basis table of docs/design-basis.md: every number is an estimate (E) from the
    calibrated models; the measured anchors are listed in that document."""
    out = ["| System | Layer | Target | Field | Rate | Schedule | Queries per round | Query grind | Size UD, proven (KiB, E) "
           "| Verify UD (ms, E) | Prover factor (E) | Size Johnson DKT26, unconfirmed (KiB, E) | Grind 0: queries / size (KiB, E) |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for system in ["A", "B"]:
        for t in TARGETS.values():
            for layer in design.LAYERS:
                r = BASIS_RATE[layer]
                d = design.optimise(system, layer, t, Regime.UDR, r, 256)
                j = design.optimise(system, layer, t, Regime.JB_DKT26, r, 256, shape_of=d)
                z = design.optimise(system, layer, t, Regime.UDR, r, 256, grind_query=0, shape_of=d)
                assert all(d.checks.values()) and all(j.checks.values()) and all(z.checks.values())
                out.append(f"| {system} | {layer} | {t.name} | 2^256 | 1/{2 ** r} | {_shape(d)} | {_q(d.config)} | {d.grind_query} "
                           f"| {d.size_bytes / 1024:.0f} | {d.verify_ms:.1f} | {design.prover_factor(d):.0f} | {j.size_bytes / 1024:.0f} "
                           f"| {_q(z.config)} / {z.size_bytes / 1024:.0f} |")
    return out


def wi_tables(proofs: int = 1700, attempts: float = 1.0) -> list[str]:
    """Category 1 with construction W-I (docs/zk-wi-soundness.md): per proof and for a whole tree.
    Unique decoding, rate 1/4 leaf and 1/8 bundle, the design-basis schedules, query grind 20."""
    import copy
    import math

    from . import wi

    cal = design.size_calibration()
    base = {(s_, l): design.optimise(s_, l, CAT1, Regime.UDR, BASIS_RATE[l], 256) for s_ in "AB" for l in ("leaf", "bundle")}
    targets = [("per proof (design basis: 4-layer chain)", CAT1),
               (f"tree of {proofs} proofs, union model, {attempts:g} attempt(s)", wi.tree_target(CAT1, proofs, attempts, "union")),
               (f"tree of {proofs} proofs, shared query budget", wi.tree_target(CAT1, proofs, 1.0, "shared"))]
    if attempts == 1.0:
        targets.append((f"tree of {proofs} proofs, union model, 2^20 attempts", wi.tree_target(CAT1, proofs, 2.0**20, "union")))
    out = []
    for label, t in targets:
        out += ["", f"### cat1, {label}", "",
                "| System | Layer | Opening | Queries per round | Lane lengths (coefficients) | Rates | Bits needed per round | Size (KiB, E) |",
                "|---|---|---|---|---|---|---|---|"]
        for s_ in "AB":
            d = base[(s_, "leaf")]
            scale = cal["B-whir"] if s_ == "B" else 1.0
            plain = design.optimise(s_, "leaf", t, Regime.UDR, 2, 256, shape_of=d)
            need = t.need_bits(len(whir.rounds(plain.config)), plain.config.fs)
            out.append(f"| {s_} | leaf | not hiding | {_q(plain.config)} | {', '.join('2^' + str(plain.config.vars_at(i) - k) for i, k in enumerate(plain.config.folds))} "
                       f"| {', '.join('2^-' + str(r) for r in plain.config.log_inv_rates)} | {need:.1f} | {plain.size_bytes / 1024:.0f} |")
            c = wi.solve(copy.deepcopy(d.config), s_, t)
            lv = wi.layout(c, s_)
            rs = wi.rounds(c, s_)
            need = t.need_bits(len(rs), c.fs)
            assert all(t.assess(wi.evaluate_wi(c, s_), c.fs).values())
            out.append(f"| {s_} | leaf | W-I | {_q(c)} | {', '.join(str(l.degree) for l in lv)} | {', '.join(f'{l.rate:.5f}' for l in lv)} "
                       f"| {need:.1f} | {wi.size_bytes(c, s_)['total'] * scale / 1024:.0f} |")
            if s_ == "B":
                m = copy.deepcopy(d.config)
                m = wi.full_mask_solve(m, t)
                rs = wi.full_mask_rounds(m)
                out.append(f"| B | leaf | W-M (full mask) | {_q(m)} | as not hiding, plus a mask polynomial of 2^{m.num_vars} elements of F | "
                           f"{', '.join('2^-' + str(r) for r in m.log_inv_rates)} | {t.need_bits(len(rs), m.fs):.1f} "
                           f"| {(whir.size_bytes(m)['total'] * scale + wi.full_mask_size(m)['mask_rows']) / 1024:.0f} |")
        for s_ in "AB":
            b = design.optimise(s_, "bundle", t, Regime.UDR, 3, 256, shape_of=base[(s_, "bundle")])
            assert all(b.checks.values())
            out.append(f"| {s_} | bundle | not hiding (R-9) | {_q(b.config)} | {_shape(b)} | 2^-3 at level 0 | "
                       f"{t.need_bits(len(design._rounds(b.config)), b.config.fs):.1f} | {b.size_bytes / 1024:.0f} |")
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", default=None,
                    help="cat1 or cat3 (named targets), or a number of QROM bits per layer (step 0.6 tables)")
    ap.add_argument("--design", action="store_true", help="print the design-basis tables (cat1 and cat3)")
    ap.add_argument("--rate", type=int, default=2, help="log2 inverse rate for --design (default 2: rate 1/4)")
    ap.add_argument("--basis", action="store_true", help="print the design-basis table (docs/design-basis.md)")
    ap.add_argument("--ship", action="store_true", help="the shipping rows: cat1/cat3 for a tree of 2^14 leaves, no grinding")
    ap.add_argument("--current", action="store_true",
                    help="revision 3: the rows being built (A W-I at true rates, A candidates, B on Binius64), cat1 tree")
    ap.add_argument("--wi", action="store_true", help="cat1 with the hiding opening W-I, per proof and per tree")
    ap.add_argument("--census", action="store_true",
                    help="system A's round census (finding M-3) beside the OTHER_ROUNDS estimate, category 1; changes no row")
    ap.add_argument("--proofs", type=int, default=1700, help="proofs per tree for --wi (default 1700)")
    ap.add_argument("--attempts", type=float, default=1.0, help="trees the adversary may try, union model (default 1)")
    ap.add_argument("--rev5", action="store_true",
                    help="revision 5: W-1 true rates on system A's plain rows, corrected schedules, Theorem Q's QROM bits, "
                         "salt length, system B's certified and candidate rows (20,000 proofs)")
    ap.add_argument("--rev6", action="store_true",
                    help="revision 6: the spBCS transcript form, Sharp-Grubbs Theorem 6.6 (2) for condition Q, (3) and (4) "
                         "for zero knowledge, leanVM's eps_aff (20,000 proofs)")
    ap.add_argument("--salt", type=int, default=512, choices=(256, 384, 512, 576),
                    help="salt length in bits for --rev5 (default 512, the lead architect's choice)")
    ap.add_argument("--rev7", action="store_true",
                    help="revision 7: the security category as an input; certified rows of both systems at categories "
                         "1, 3 and 5, candidate rows, field, QROM, salts, sizes (20,000 proofs)")
    ap.add_argument("--rev8", action="store_true",
                    help="revision 8: system B's rows with every Johnson-regime (DKT26-route) term, the proximity-gap "
                         "parameters, the refusals, the node at rate 1/4, condition C-2's counts (with --category N: "
                         "that category's need and field)")
    ap.add_argument("--rev9", action="store_true",
                    help="revision 9 (the default with no flag): both systems' rows under the counting convention EVERY t "
                         "(Sharp-Grubbs Theorem 6.6 (2) as stated), category 1 tables and system B's Johnson terms")
    ap.add_argument("--rev10", action="store_true",
                    help="revision 10 (the default with no flag; the same tables as --rev9 with the SG26 hash term on every "
                         "row, k_q with its provenance and guard, and the computed status)")
    ap.add_argument("--hash-basis", choices=("attack-rule", "proven"), default="attack-rule",
                    help="how the CLASSICAL hash part of SG26 Theorem 6.6 (2) is judged: attack-rule (the project's "
                         "recorded basis, condition H) or proven (the tree's proven classical level must reach kappa_C; "
                         "no 256-bit row meets it)")
    ap.add_argument("--convention", choices=("every-t", "t-ge-kq"), default="every-t",
                    help="counting convention for --rev7, --rev8, --rev9, --category: every-t (the default and the only "
                         "certified one) or t-ge-kq (the revision 1 to 8 counts; output labelled 'non-default convention "
                         "(t >= k_q), not certified')")
    ap.add_argument("--legacy", action="store_true",
                    help="RECORD: the step 0.6 per-layer tables that were the default before revision 9")
    ap.add_argument("--category", type=int, choices=(1, 2, 3, 4, 5), default=None,
                    help="revision 7 tables for one NIST category (its default profile, or the overrides below)")
    ap.add_argument("--digest-bits", type=int, default=None, help="with --category: digest length (256, 384, 512)")
    ap.add_argument("--proof-salt", type=int, default=None, help="with --category: proof salt in bytes")
    ap.add_argument("--leaf-salt", type=int, default=None, help="with --category: leaf salt in bytes")
    ap.add_argument("--field-bits", type=int, default=None, help="with --category: challenge field in bits")
    ap.add_argument("--tree-hash-a", default=None, help="with --category: system A's tree hash (category.TREE_HASHES)")
    ap.add_argument("--tree-hash-b", default=None, help="with --category: system B's tree hash (category.TREE_HASHES)")
    ap.add_argument("--privacy-category", type=int, choices=(1, 2, 3, 4, 5), default=None,
                    help="with --category: the category of the zero-knowledge figure's query budget (M-1: 5)")
    args = ap.parse_args(argv)
    conv = args.convention
    record_flags = (args.rev6, args.rev5, args.current, args.ship, args.wi, args.basis, args.design, args.legacy,
                    args.target is not None)
    if args.convention != "every-t" and any(record_flags):
        ap.error("--convention applies to the default output, --rev7, --rev8, --rev9 and --category only")
    if args.hash_basis != "attack-rule" and any(record_flags):
        ap.error("--hash-basis applies to the default output, --rev7, --rev8, --rev9, --rev10 and --category only")
    hb = args.hash_basis
    if args.census:
        from . import census

        print("\n".join(census.tables()))
        return
    if args.rev8:
        from . import category, dkt26

        print("\n".join(dkt26.tables(args.category, conv, hb) + category.PROVEN_FOOTER))
        return
    if args.category is not None:
        import dataclasses

        from . import category

        p = category.PROFILES[args.category]
        over = {k: v for k, v in (("digest_bits", args.digest_bits), ("proof_salt_bytes", args.proof_salt),
                                   ("leaf_salt_bytes", args.leaf_salt), ("field_bits", args.field_bits),
                                   ("tree_hash_a", args.tree_hash_a), ("tree_hash_b", args.tree_hash_b),
                                   ("privacy_category", args.privacy_category)) if v is not None}
        if over:
            p = dataclasses.replace(p, label=f"cat{args.category}, custom", **over)
        p = dataclasses.replace(p, convention=conv, hash_basis=hb)
        print("\n".join(category.derivation_table() + category.profile_tables(p)
                        + category.field_summary((args.category,), conv, hb) + category.PROVEN_FOOTER))
        return
    if args.rev7:
        from . import category

        print("\n".join(category.tables(convention=conv, hash_basis=hb)))
        return
    if any(record_flags):
        print(RECORD_BANNER)
    else:  # revision 9: the default output
        print("\n".join(rev9_tables(conv, hb)))
        return
    if args.rev6:
        from . import revision6

        print("\n".join(revision6.tables()))
        return
    if args.rev5:
        from . import revision5

        print("\n".join(revision5.tables(args.salt)))
        return
    if args.current:
        from . import current

        print("\n".join(current.tables()))
        return
    if args.ship:
        from . import shipping

        print("\n".join(shipping.tables()))
        return
    if args.wi:
        print("\n".join(wi_tables(args.proofs, args.attempts)))
        return
    if args.basis:
        print("\n".join(basis_table()))
        return
    if args.design:
        print("\n".join(design_tables(args.rate)))
        return
    if args.target in TARGETS:
        t = TARGETS[args.target]
        out = target_table() + ["", DHEAD]
        for system in ["A", "B"]:
            for regime in REGIMES:
                for layer in design.LAYERS:
                    out.append(_drow(design.design_point(system, layer, t, regime, args.rate, 256)))
        print("\n".join(out))
        return
    target = QROM_TARGET if args.target is None else float(args.target)
    print("\n".join(cross_checks() + yugen_tables(target)))


RECORD_BANNER = (
    "RECORD (superseded by revision 9; not the calculator's convention): the counts below use the book need "
    "(kappa_C + 1 + log2 N + log2(1 + k), or earlier per-layer targets), which for the spBCS transcript holds only under "
    "the non-default convention (t >= k_q); no row below is certified. Johnson-regime rows rest on DKT26 (Dao, "
    "Kominers, Thaler, ePrint 2026/2056), a PREPRINT; Haboeck's route is withdrawn (binius-johnson-row.md 0.1); the "
    "102- and 77-query rows are withdrawn (thin margins). The certified rows are printed by `yugen-soundness` "
    "(no flag) or `--rev9`.\n")


def rev9_tables(convention: str = "every-t", hash_basis: str = "attack-rule") -> list[str]:
    """Revisions 9 and 10: category 1's rows of both systems and system B's Johnson-regime terms, under `convention`
    (revision 10: the SG26 hash term on every row, k_q with provenance and guard, the computed status)."""
    from . import category, dkt26

    import dataclasses

    p = dataclasses.replace(category.PROFILES[1], convention=convention, hash_basis=hash_basis)
    row7 = [category.a_plain_leaf(22, r, p) for r in (2, 1)]
    return (category.tables((1,), convention, hash_basis)[:-len(category.PROVEN_FOOTER)]
            + category.rows_table(row7, "System A row 7 (plain tree leaf, wallet statement 2^22; specification A.1 names "
                                        "its counts; opening bytes only)")
            + [""] + dkt26.tables(None, convention, hash_basis) + category.PROVEN_FOOTER)


if __name__ == "__main__":
    main()
