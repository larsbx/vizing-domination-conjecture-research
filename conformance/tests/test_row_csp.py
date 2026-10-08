"""Differential checks of the candidate core against literal product adjacency."""

from itertools import combinations, permutations, product
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "kernel"), str(ROOT / "oracles")]
from row_csp import (Budget, BudgetExceeded, RowTable, audit, automorphisms,
                     composition_count, lambda_passes, orbit_key,
                     residual_satisfied, scalar_passes, size_patterns, solve_m1)
from canonical_graph6 import decode_graph6
from replay_row_csp import direct_product_dominates, historical_inputs, replay


def graph(n, edges):
    masks = [0] * n
    for u, v in edges:
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return tuple(masks)


def path(n):
    return graph(n, ((i, i + 1) for i in range(n - 1)))


def all_graphs(n):
    possible = tuple(combinations(range(n), 2))
    for selected in range(1 << len(possible)):
        yield graph(n, (edge for i, edge in enumerate(possible) if selected & (1 << i)))


class RowCoreTests(unittest.TestCase):
    def test_state_residuals_against_literal_closed_neighbors(self):
        for n in range(1, 5):
            for horizontal in all_graphs(n):
                table = RowTable(horizontal)
                for selected in range(1 << n):
                    uncovered = [g for g in range(n)
                                 if not selected & (1 << g)
                                 and not any(selected & (1 << u) for u in range(n)
                                             if horizontal[g] & (1 << u))]
                    self.assertEqual(table.states[selected].residual,
                                     sum(1 << g for g in uncovered))
                self.assertEqual(table.states[0].residual, table.full)
                self.assertEqual(table.states[table.full].residual, 0)

    def test_size_enumeration_and_scalar_prefix_pruning_are_complete(self):
        for m in range(1, 5):
            for n in range(1, 4):
                for target in range(n * m + 1):
                    expected = sorted(p for p in product(range(n + 1), repeat=m)
                                      if sum(p) == target)
                    self.assertEqual(list(size_patterns(m, n, target)), expected)
                    self.assertEqual(composition_count(m, n, target), len(expected))
        from row_csp import scalar_patterns
        for horizontal in all_graphs(3):
            table, rows = RowTable(horizontal), path(4)
            for target in range(13):
                counts = {"scalar_rejected": 0, "scalar_survivors": 0}
                actual = list(scalar_patterns(table, rows, target, Budget(100000), counts))
                expected = [p for p in size_patterns(4, 3, target) if scalar_passes(table, rows, p)]
                self.assertEqual(actual, expected)
                self.assertEqual(counts["scalar_rejected"] + counts["scalar_survivors"],
                                 composition_count(4, 3, target))

    def test_every_small_pattern_against_independent_cartesian_oracle(self):
        factor_pairs, selected_sets, patterns = 0, 0, 0
        for n in range(1, 4):
            for horizontal in all_graphs(n):
                for rows in (path(4), graph(3, [(0, 1), (1, 2), (0, 2)])):
                    table = RowTable(horizontal)
                    feasible = set()
                    for states in product(range(1 << n), repeat=len(rows)):
                        direct = direct_product_dominates(horizontal, rows, states)
                        self.assertEqual(residual_satisfied(table, rows, states), direct)
                        if direct:
                            feasible.add(tuple(s.bit_count() for s in states))
                        selected_sets += 1
                    for sizes in product(range(n + 1), repeat=len(rows)):
                        outcome = solve_m1(table, rows, sizes)
                        self.assertEqual(outcome["status"], "SAT" if sizes in feasible else "UNSAT")
                        if sizes in feasible:
                            self.assertTrue(scalar_passes(table, rows, sizes))
                            self.assertTrue(lambda_passes(table, rows, sizes))
                            self.assertEqual(tuple(s.bit_count() for s in outcome["witness"]), sizes)
                            self.assertTrue(direct_product_dominates(horizontal, rows, outcome["witness"]))
                        else:
                            self.assertIsNone(outcome["witness"])
                        patterns += 1
                    factor_pairs += 1
        self.assertEqual((factor_pairs, selected_sets, patterns), (22, 37528, 2800))

    def test_complete_small_audits_and_incomplete_limits(self):
        horizontal, rows = path(3), path(3)
        for target in range(10):
            expected_sat = any(direct_product_dominates(horizontal, rows, states)
                               for states in product(range(8), repeat=3)
                               if sum(s.bit_count() for s in states) == target)
            result = audit(horizontal, rows, target, orbit_limit=1000, m1_work_limit=100000)
            self.assertTrue(result["exhaustive"])
            self.assertEqual(result["status"], "SAT" if expected_sat else "UNSAT")
            self.assertEqual(sum(result["outcome_counts"].values()), result["orbit_count"])
            self.assertEqual(sum(o["observed_multiplicity"] for o in result["orbits"]),
                             result["pattern_counts"]["scalar_survivors"] -
                             result["pattern_counts"]["lambda_rejected"])
        for kwargs in ({"enumeration_limit": 0}, {"automorphism_limit": 0},
                       {"orbit_limit": 0}, {"m1_work_limit": 0}, {"m1_seconds": 0}):
            result = audit(horizontal, rows, 4, **kwargs)
            self.assertEqual(result["status"], "TIMEOUT")
            self.assertFalse(result["exhaustive"])
        partial = audit(horizontal, rows, 4, enumeration_limit=20)
        counts = partial["pattern_counts"]
        self.assertEqual(counts["raw_patterns"], counts["scalar_rejected"] +
                         counts["scalar_survivors"] + counts["pending_enumeration"])

    def test_expired_clock_and_work_limits_never_become_unsat(self):
        table, rows, sizes = RowTable(path(3)), path(3), (1, 1, 1)
        for limit in (0, 1, 2, 4):
            outcome = solve_m1(table, rows, sizes, work_limit=limit)
            self.assertEqual(outcome["status"], "TIMEOUT")
            self.assertEqual(outcome["work_used"], limit)
            self.assertIsNone(outcome["witness"])
        clock = iter([10.0, 11.0]).__next__
        outcome = solve_m1(table, rows, sizes, seconds=1.0, clock=clock)
        self.assertEqual((outcome["status"], outcome["reason"]), ("TIMEOUT", "wall_clock_limit"))
        self.assertEqual(outcome["work_used"], 0)

    def test_automorphisms_and_orbits_against_all_small_bijections(self):
        for n in range(1, 5):
            for rows in all_graphs(n):
                expected = tuple(p for p in permutations(range(n))
                                 if all(bool(rows[u] & (1 << v)) ==
                                        bool(rows[p[u]] & (1 << p[v]))
                                        for u in range(n) for v in range(n)))
                group = automorphisms(rows)
                self.assertEqual(group, expected)
                sizes = tuple(range(n))
                key = min(tuple(sizes[p[v]] for v in range(n)) for p in expected)
                self.assertEqual(orbit_key(sizes, group), key)
        with self.assertRaises(BudgetExceeded):
            automorphisms(path(3), work_limit=0)

    def test_historical_rows_are_labeled_and_square_witnesses_are_checked(self):
        pins, _ = historical_inputs(ROOT)
        for pin, expected_aut in zip(pins["classes"], (16, 4, 16)):
            horizontal = decode_graph6(pin["representative_graph6"])
            self.assertEqual(len(automorphisms(horizontal)), expected_aut)
            table = RowTable(horizontal)
            self.assertEqual(table.gamma, 4)
            self.assertEqual(solve_m1(table, horizontal, (0,) * 10)["status"], "UNSAT")
            outcome = solve_m1(table, horizontal, (10,) * 10)
            self.assertEqual(outcome["status"], "SAT")
            self.assertTrue(direct_product_dominates(horizontal, horizontal, outcome["witness"]))

    def test_malformed_inputs_fail_instead_of_yielding_results(self):
        for horizontal in ((), (1,), (2, 0), (True,), (0,) * 11, (-1,), (2.0, 1)):
            with self.subTest(horizontal=horizontal), self.assertRaises(ValueError):
                RowTable(horizontal)
        table = RowTable(path(3))
        for sizes in ((1, 1), (-1, 1, 1), (True, 1, 1), (1.0, 1, 1), (4, 0, 0)):
            with self.assertRaises(ValueError):
                solve_m1(table, path(3), sizes)
        for kwargs in ({"work_limit": True}, {"work_limit": -1}, {"seconds": float('nan')},
                       {"seconds": float('inf')}, {"seconds": -1}, {"fixed": {0: 3}}):
            with self.assertRaises(ValueError):
                solve_m1(table, path(3), (1, 1, 1), **kwargs)


class ReceiptTests(unittest.TestCase):
    def test_checked_in_receipts_replay_and_report_partial_search(self):
        before = {p: p.read_bytes() for p in (ROOT / "conformance/receipts").glob('*')}
        receipts = replay()
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        for receipt in receipts.values():
            self.assertFalse(receipt["acceptance_authority"])
            self.assertFalse(receipt["claim_promotion"])
            if receipt["kind"] == "row_csp_audit":
                self.assertEqual(receipt["status"], "TIMEOUT")
                self.assertTrue(receipt["enumeration_complete"])
                self.assertFalse(receipt["exhaustive"])
                self.assertGreater(receipt["outcome_counts"]["TIMEOUT"], 0)
        regression = next(r for r in receipts.values() if r["kind"] == "row_csp_regression")
        self.assertEqual(regression["outcome_counts"], {"SAT": 2, "UNSAT": 3, "TIMEOUT": 1})
        examples = {e["id"]: e for e in regression["examples"]}
        self.assertTrue(examples["scalar-survival-wing-rejection"]["scalar_pass"])
        self.assertEqual(examples["scalar-survival-wing-rejection"]["wing_pairs"], 0)
        self.assertGreater(examples["local-survival-global-failure"]["wing_pairs"], 0)
        self.assertEqual(examples["shared-outer-fixed-pair"]["shared_capacity_pairs"], 0)
        self.assertGreater(examples["shared-outer-fixed-pair"]["wing_pairs"], 0)
        self.assertEqual(examples["distinct-outer-rows"]["wing_pairs"],
                         examples["distinct-outer-rows"]["shared_capacity_pairs"])

    def test_bad_scope_or_claim_state_fails_before_receipt_writes(self):
        mutations = (
            ("conformance/fixtures/row_csp_profile.json", lambda text: text.replace('historical_casebase_only', 'census')),
            ("conformance/fixtures/row_csp_profile.json", lambda text: text.replace('"schema_version": 1', '"schema_version": true')),
            ("conformance/fixtures/row_csp_profile.json", lambda text: text.replace('"schema_version": 1', '"schema_version": 1.0')),
            ("conformance/fixtures/casebase_classes.json", lambda text: text.replace('"role": "A"', '"role": "unknown"')),
            ("proof/claims.toml", lambda text: text.replace('status = "working"', 'status = "computed"', 1)),
            ("ESTATE.toml", lambda text: text.replace('acceptance_authority = false', 'acceptance_authority = true')),
        )
        for relative, mutate in mutations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for folder in ('conformance', 'proof', 'kernel', 'oracles'):
                    shutil.copytree(ROOT / folder, root / folder)
                shutil.copyfile(ROOT / 'ESTATE.toml', root / 'ESTATE.toml')
                before = {p: p.read_bytes() for p in (root / 'conformance/receipts').glob('*')}
                path_to_change = root / relative
                path_to_change.write_text(mutate(path_to_change.read_text()))
                with self.assertRaises(ValueError):
                    replay(root, write=True)
                self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_edited_receipts_fail_byte_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ('conformance', 'proof', 'kernel', 'oracles'):
                shutil.copytree(ROOT / folder, root / folder)
            shutil.copyfile(ROOT / 'ESTATE.toml', root / 'ESTATE.toml')
            receipt = root / 'conformance/receipts/row_csp_A.json'
            receipt.write_text(receipt.read_text().replace('"status": "TIMEOUT"', '"status": "UNSAT"', 1))
            with self.assertRaisesRegex(ValueError, 'derived receipt mismatch'):
                replay(root)


if __name__ == '__main__':
    unittest.main()
