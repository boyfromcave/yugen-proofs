"""Reproduces the numbers of docs/binius-johnson-row.md section 7 (revision 2) from rowcalc.py, and
checks them against an independent recomputation written from the papers' formulas, not from
rowcalc.py (the referee's script, docs/johnson-row-referee.md appendix, restated here).

Formulas: DKT26 = Dao, Kominers, Thaler, ePrint 2026/2056, Theorem 4.4 bounds (38), (39), Lemma 3.3;
Haboeck = "Basefold in the List Decoding Regime", ePrint 2024/1571, Theorems 3, 4 and Lemma 3.
Original test code (the Ycash developers, 2026).
"""

import math
import unittest

import rowcalc as rc

# --- independent recomputation (no rowcalc import below this line is used) ---------------------
RHO = 1 / 8


def need(c):
    return c + 1 + math.log2(20000 * 601)


def per_query(m):
    return -math.log2((1 + 1 / (2 * m)) * math.sqrt(RHO)) if m else -math.log2((1 + RHO) / 2)


def queries(m, c):
    return math.ceil(need(c) / per_query(m))


def johnson(m):  # DKT26 (38), second term, at A = a n, D = rho n
    a = (1 + 1 / (2 * m)) * math.sqrt(RHO)
    return (a - RHO) / (a * a - RHO)


def bcf(ln, m):  # DKT26 (39)
    return 8 * 2 ** ln * (m + 0.5) ** 3 / (3 * (RHO - 2 ** -ln))


def hab(ln, B, m):  # Haboeck Theorems 3 / 4, M = 1
    return (m + 0.5) / math.sqrt(RHO) * max((m + 0.5) ** 6 / (3 * RHO) * 4 ** ln, 2 * (B * 2 ** ln + 1))


def bits(cnt):
    return 256 - math.log2(cnt)


class Rows(unittest.TestCase):
    def test_targets(self):
        self.assertAlmostEqual(rc.NEED["cat1"], 152.52, places=2)
        self.assertAlmostEqual(rc.NEED["cat3"], 216.52, places=2)
        self.assertAlmostEqual(rc.NEED["cat1"], need(128), places=9)

    def test_list_size_is_the_johnson_bound_19(self):
        """Section 2.2 F1 (revision 2): 19, not revision 1's 29.70; the bound holds at every n."""
        self.assertEqual(rc.list_bound(10, RHO), 19)
        self.assertAlmostEqual(johnson(10), 19.218, places=3)
        self.assertAlmostEqual(rc.gs_list_bound(10, RHO), 29.70, places=2)
        for ln in range(4, 32):
            n = 2 ** ln
            D = n // 8 - 1
            A = math.ceil((1 + 1 / 20) * math.sqrt(RHO) * n)
            self.assertGreater(A * A, n * D)
            self.assertLessEqual(n * (A - D) / (A * A - n * D), johnson(10))

    def test_unique_decoding_rows(self):
        r = rc.row("ud", "cat1")
        self.assertEqual(r["queries"], 184)
        self.assertEqual(queries(None, 128), 184)
        self.assertTrue(r["meets"])
        self.assertAlmostEqual(r["weakest"].bits, 226.00, places=2)
        c3 = rc.row("ud", "cat3")
        self.assertEqual((c3["queries"], queries(None, 192)), (261, 261))
        self.assertTrue(c3["meets"])

    def test_dkt_route_row_107(self):
        r = rc.row("dkt", "cat1", 10)
        self.assertEqual(r["queries"], 107)
        self.assertEqual(queries(10, 128), 107)
        self.assertAlmostEqual(r["query_bits"], 152.968, places=3)
        self.assertAlmostEqual(r["weakest"].bits, 211.41, places=2)
        self.assertAlmostEqual(r["weakest"].bits, bits(bcf(30, 10) + 2 * 19), places=6)
        leaf = {t.name: t.bits for t in r["leaf"]}
        self.assertAlmostEqual(leaf["mask fold gamma"], bits(bcf(22, 10) + 19), places=6)
        self.assertAlmostEqual(leaf["PIOP round (worst: skip, 127)"], bits(127 * 19), places=6)
        self.assertAlmostEqual(leaf["ring switch (each)"], bits(8 * 19), places=6)
        self.assertTrue(r["meets"])

    def test_algebraic_slack_and_qualitative_requirement(self):
        """Section 7.4: the row needs any exceptional count below 2^103.48 at every line length
        up to 2^30; DKT26 (39) is 59 bits below that."""
        tol = rc.tolerated_exceptional_log2("cat1", 2 * 19)
        self.assertAlmostEqual(tol, 103.48, places=2)
        self.assertGreater(tol - math.log2(bcf(30, 10)), 58.8)
        # Haboeck's n^2-type count at the node line would also fit (17 bits)
        self.assertGreater(bits(hab(30, 2, 10)), need(128) + 16.8)

    def test_haboeck_route_numbers_kept_for_reference(self):
        """Not an available route (gaps G-1, G-3, G-6); the numbers are kept for comparison."""
        r = rc.row("haboeck", "cat1", 10)
        self.assertEqual(r["queries"], 107)
        self.assertAlmostEqual(r["weakest"].bits, 169.34, places=2)
        self.assertAlmostEqual(r["weakest"].bits, bits(hab(30, 2, 10)), places=6)
        self.assertFalse(rc.row("haboeck", "cat3", 3)["meets"])

    def test_withdrawn_102_row_is_fragile(self):
        """The m = 153 row of revision 1 (102 queries) clears its target by about 0.001 bit and fails
        on Haboeck's count: withdrawn (referee R-11, section 4.1)."""
        q = queries(153, 128)
        self.assertEqual(q, 102)
        self.assertLess(q * per_query(153) - need(128), 0.002)
        self.assertLess(bits(hab(30, 2, 153)), need(128))

    def test_category_3(self):
        c3 = rc.row("dkt", "cat3", 3)
        self.assertFalse(c3["meets"])
        self.assertAlmostEqual(c3["weakest"].bits, 216.16, places=2)
        self.assertEqual(queries(3, 192), 170)

    def test_rate_one_sixteenth(self):
        r = rc.row("dkt", "cat1", 10, 1 / 16)
        self.assertEqual(r["queries"], 80)
        self.assertTrue(r["meets"])

    def test_lemma33_level(self):
        """A fold level of message dimension 1 (k = 1, codeword 1/rho = 8 points, A = 3): DKT26
        Lemma 3.3 gives at most C(8, 2)/(3 - 1) = 14 exceptional challenges."""
        self.assertEqual(rc.lemma33_count(8, math.ceil((1 + 1 / 20) * math.sqrt(RHO) * 8)), 14)

    def test_each_count_less_by_one_fails(self):
        for regime, target, m in (("ud", "cat1", None), ("dkt", "cat1", 10), ("ud", "cat3", None)):
            r = rc.row(regime, target, m)
            self.assertLess((r["queries"] - 1) * r["per_query"], r["need"])


if __name__ == "__main__":
    unittest.main()
