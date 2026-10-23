"""Broom-family regression: disproves unit-capacity Hall, not capacitated Hall.

This is a non-authoritative finite replay for the symbolic proof record.
"""
import unittest

from oracles.broom_hall_oracle import broom, certificate, check, constructed_set


class BroomHallExamples(unittest.TestCase):
    def test_family_3_through_12(self):
        for t in range(3, 13):
            with self.subTest(t=t):
                c = check(t)
                self.assertEqual(c["D_size"], 2 * t)
                self.assertEqual(c["X"], t - 1)
                self.assertEqual(c["N_X"], 1)
                self.assertEqual(c["unit_hall_deficit"], t - 2)
                self.assertEqual(c["witness_capacity"], t - 1)

    def test_exact_single_witness_block(self):
        c = certificate(5)
        self.assertEqual(c["N_X_blocks"], [(1, 0)])
        self.assertEqual(c["occupied_block_counts"]["(1, 0)"], 4)
        self.assertTrue(all(w == [(1, 0)] for w in c["witnesses"].values()))

    def test_no_inference_against_capacity(self):
        for t in (3, 4, 7):
            c = check(t)
            self.assertGreater(c["X"], c["N_X"])
            # The same examples *satisfy* capacitated Hall exactly.
            self.assertEqual(c["X"], c["witness_capacity"])

    def test_canonical_construction_has_distinct_vertices(self):
        for t in (3, 4, 10):
            g, h = broom(t)
            d = constructed_set(t)
            self.assertEqual(len(d), 2 * t)
            self.assertEqual(len(g), 4)
            self.assertEqual(len(h), 2 * t)
            self.assertTrue(all(0 <= a < 4 and 0 <= b < 2 * t
                                for a, b in d))

    def test_domain_guard(self):
        with self.assertRaises(ValueError):
            broom(2)


if __name__ == "__main__":
    unittest.main()
