"""Independent feasibility, interruption and evidence-boundary regressions."""
from itertools import product
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'kernel'), str(ROOT / 'oracles')]
from row_csp import RowTable, solve_m1
from row_csp_pair import solve_m1_pair
from product_cover import solve_product_cover
from replay_row_csp import direct_product_dominates
from replay_row_csp_extension import (load_profile, replay, select_orbits,
                                      receipt_products, verified_status)
from canonical_graph6 import decode_graph6
from test_row_csp import all_graphs, graph, path


class ExtendedSolverTests(unittest.TestCase):
    def test_both_engines_against_every_literal_small_pattern(self):
        pairs = sets = patterns = 0
        for n in range(1, 4):
            for horizontal in all_graphs(n):
                for rows in (path(4), graph(3, [(0, 1), (1, 2), (0, 2)])):
                    feasible = set()
                    for states in product(range(1 << n), repeat=len(rows)):
                        if direct_product_dominates(horizontal, rows, states):
                            feasible.add(tuple(s.bit_count() for s in states))
                        sets += 1
                    table = RowTable(horizontal)
                    for sizes in product(range(n + 1), repeat=len(rows)):
                        expected = 'SAT' if sizes in feasible else 'UNSAT'
                        for outcome in (solve_m1_pair(table, rows, sizes),
                                        solve_product_cover(horizontal, rows, sizes)):
                            self.assertEqual(outcome['status'], expected)
                            if expected == 'SAT':
                                self.assertEqual(tuple(s.bit_count() for s in outcome['witness']), sizes)
                                self.assertTrue(direct_product_dominates(horizontal, rows, outcome['witness']))
                            else:
                                self.assertIsNone(outcome['witness'])
                        patterns += 1
                    pairs += 1
        self.assertEqual((pairs, sets, patterns), (22, 37528, 2800))

    def test_dense_disconnected_and_non_square_factors(self):
        horizontal = path(3)
        for rows in (graph(4, [(0, 1), (0, 2), (0, 3)]),
                     graph(4, [(u, v) for u in range(4) for v in range(u + 1, 4)]),
                     (0, 0, 0, 0)):
            feasible = {tuple(s.bit_count() for s in states)
                        for states in product(range(8), repeat=4)
                        if direct_product_dominates(horizontal, rows, states)}
            table = RowTable(horizontal)
            for sizes in product(range(4), repeat=4):
                expected = 'SAT' if sizes in feasible else 'UNSAT'
                self.assertEqual(solve_m1_pair(table, rows, sizes)['status'], expected)
                self.assertEqual(solve_product_cover(horizontal, rows, sizes)['status'], expected)

    def test_fixed_states_against_literal_enumeration(self):
        horizontal, rows = path(3), path(3)
        table = RowTable(horizontal)
        for mask in range(8):
            for sizes in product(range(4), repeat=3):
                if sizes[1] != mask.bit_count():
                    continue
                feasible = any(direct_product_dominates(horizontal, rows, states)
                               for states in product(range(8), repeat=3)
                               if states[1] == mask and tuple(s.bit_count() for s in states) == sizes)
                for outcome in (solve_m1_pair(table, rows, sizes, fixed={1: mask}),
                                solve_product_cover(horizontal, rows, sizes, fixed={1: mask})):
                    self.assertEqual(outcome['status'], 'SAT' if feasible else 'UNSAT')
                    if feasible:
                        self.assertEqual(outcome['witness'][1], mask)

    def test_budget_and_expired_clock_preserve_timeout(self):
        for solve in (lambda **kw: solve_m1_pair(RowTable(path(3)), path(3), (1, 1, 1), **kw),
                      lambda **kw: solve_product_cover(path(3), path(3), (1, 1, 1), **kw)):
            for limit in (0, 1, 2, 4):
                outcome = solve(work_limit=limit)
                self.assertEqual((outcome['status'], outcome['reason'], outcome['work_used']),
                                 ('TIMEOUT', 'work_limit', limit))
                self.assertIsNone(outcome['witness'])
            clock = iter([10.0, 11.0]).__next__
            outcome = solve(seconds=1, clock=clock)
            self.assertEqual((outcome['status'], outcome['reason'], outcome['work_used']),
                             ('TIMEOUT', 'wall_clock_limit', 0))

    def test_invalid_inputs_fail_closed(self):
        for solve in (lambda sizes, **kw: solve_m1_pair(RowTable(path(3)), path(3), sizes, **kw),
                      lambda sizes, **kw: solve_product_cover(path(3), path(3), sizes, **kw)):
            for sizes in ((1, 1), (1, -1, 1), (True, 1, 1), (4, 1, 1)):
                with self.assertRaises(ValueError):
                    solve(sizes)
            for kwargs in ({'work_limit': True}, {'work_limit': -1}, {'seconds': float('nan')},
                           {'seconds': float('inf')}, {'seconds': -1}, {'seconds': True},
                           {'fixed': {True: 1}}, {'fixed': {0: 3}}):
                with self.assertRaises(ValueError):
                    solve((1, 1, 1), **kwargs)
        for bad in ((), (1,), (2, 0), (0,) * 11, (True,)):
            with self.assertRaises(ValueError):
                solve_product_cover(bad, path(3), (1, 1, 1))

    def test_verified_stress_orbit_exhausts_where_v1_hits_cap(self):
        # Index 249 is a balanced B stress pattern, not an imported census case.
        old = json.loads((ROOT / 'conformance/receipts/row_csp_B.json').read_bytes())
        horizontal = decode_graph6(old['graph6'])
        sizes = old['orbits'][249]['sizes']
        table = RowTable(horizontal)
        baseline = solve_m1(table, horizontal, sizes, work_limit=1000000)
        primary = solve_m1_pair(table, horizontal, sizes, work_limit=1000000)
        independent = solve_product_cover(horizontal, horizontal, sizes, work_limit=2000000)
        self.assertEqual(baseline['status'], 'TIMEOUT')
        self.assertEqual((primary['status'], independent['status']), ('UNSAT', 'UNSAT'))
        self.assertEqual(verified_status(horizontal, sizes, baseline, primary, independent), 'UNSAT')


class ExtensionReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One full deterministic replay for all receipt assertions.
        cls.receipts = replay()

    def test_replay_preserves_original_files_and_partial_statuses(self):
        before = {p: p.read_bytes() for p in (ROOT / 'conformance/receipts').glob('row_csp_*.json')}
        expected = {'A': (22, 16, 6), 'A-class': (40, 37, 182), 'B': (40, 23, 288)}
        for receipt in self.receipts.values():
            selected, verified, remaining = expected[receipt['role']]
            self.assertEqual(receipt['selected_orbit_count'], selected)
            self.assertEqual(receipt['new_outcome_counts']['UNSAT'], verified)
            self.assertEqual(receipt['remaining_unresolved_orbits'], remaining)
            self.assertEqual(receipt['status'], 'TIMEOUT')
            self.assertFalse(receipt['exhaustive'])
            self.assertFalse(receipt['acceptance_authority'])
            self.assertFalse(receipt['claim_promotion'])
            self.assertEqual(receipt['structural_lemmas_applied'], [])
            self.assertEqual(len(receipt['orbits']), selected)
            self.assertEqual(sum(receipt['new_outcome_counts'].values()), selected)
            self.assertEqual(receipt['unsearched_pending_orbits'] +
                             receipt['new_outcome_counts']['TIMEOUT'], remaining)
            for orbit in receipt['orbits']:
                for engine, budget in (('baseline', 'baseline_work_per_orbit'),
                                       ('primary', 'primary_work_per_orbit'),
                                       ('independent', 'independent_work_per_orbit')):
                    self.assertLessEqual(orbit[engine]['work_used'], receipt['budgets'][budget])
                if orbit['status'] == 'UNSAT':
                    self.assertEqual((orbit['primary']['status'], orbit['independent']['status']),
                                     ('UNSAT', 'UNSAT'))
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_selection_is_deterministic_duplicate_free_and_pending_only(self):
        profile = load_profile(ROOT)
        for receipt in self.receipts.values():
            original = json.loads((ROOT / receipt['original_receipt']).read_bytes())
            selected = select_orbits(original, profile['selection'])
            indices = [i for i, _ in selected]
            self.assertEqual(len(indices), len(set(indices)))
            self.assertTrue(all(original['orbits'][i]['status'] == 'TIMEOUT' for i in indices))
            self.assertEqual(indices, [o['original_orbit_index'] for o in receipt['orbits']])
            none = select_orbits(original, {'cheap_orbits_per_role': 0, 'stress_orbits_per_role': 0})
            self.assertEqual(none, [])
            only_stress = select_orbits(original, {'cheap_orbits_per_role': 0, 'stress_orbits_per_role': 2})
            self.assertEqual(len(only_stress), 2)

    def test_one_engine_timeout_is_not_verified_unsat(self):
        unsat = {'status': 'UNSAT', 'reason': 'search_exhausted', 'work_used': 1, 'witness': None}
        timeout = {'status': 'TIMEOUT', 'reason': 'work_limit', 'work_used': 0, 'witness': None}
        for primary, independent in ((unsat, timeout), (timeout, unsat), (timeout, timeout)):
            self.assertEqual(verified_status((0,), (0,), unsat, primary, independent), 'TIMEOUT')

    def test_conflicts_and_invalid_witnesses_fail_closed(self):
        sat = {'status': 'SAT', 'reason': 'checked_witness', 'work_used': 1, 'witness': [1]}
        unsat = {'status': 'UNSAT', 'reason': 'search_exhausted', 'work_used': 1, 'witness': None}
        timeout = {'status': 'TIMEOUT', 'reason': 'work_limit', 'work_used': 0, 'witness': None}
        self.assertEqual(verified_status((0,), (1,), timeout, sat, timeout), 'SAT')
        self.assertEqual(verified_status((0,), (1,), timeout, timeout, sat), 'SAT')
        self.assertEqual(verified_status((0,), (1,), sat, timeout, timeout), 'SAT')
        with self.assertRaisesRegex(ValueError, 'engines disagree'):
            verified_status((0,), (1,), timeout, sat, unsat)
        for bad in ({**sat, 'witness': [0]}, {**sat, 'witness': [3]},
                    {**unsat, 'witness': [1]}, {**timeout, 'reason': 'search_exhausted'}):
            with self.assertRaises(ValueError):
                verified_status((0,), (1,), timeout, bad, timeout)

    def test_previously_checked_sat_cannot_become_aggregate_unsat(self):
        # Mathematical positive control for aggregation; not a historical fixture.
        control = {'kind': 'row_csp_audit', 'graph6': '@', 'horizontal_order': 1,
                   'role': 'A', 'graph_id': 'mathematical-control-only', 'target': 1,
                   'target_semantics': 'exact_total_selected_vertices', 'orbit_count': 1,
                   'enumeration_complete': True, 'outcome_counts': {'SAT': 1, 'UNSAT': 0, 'TIMEOUT': 0},
                   'orbits': [{'sizes': [1], 'status': 'SAT', 'witness': [1],
                               'reason': 'checked_witness', 'observed_multiplicity': 1}]}
        with patch('replay_row_csp_extension.replay_v1', return_value={'control.json': control}), \
             patch('replay_row_csp_extension.source_metadata', return_value={}):
            products = receipt_products()
        receipt = json.loads(next(iter(products.values())))
        self.assertEqual(receipt['selected_orbit_count'], 0)
        self.assertEqual(receipt['status'], 'SAT')

    def test_bad_scope_authority_profile_and_original_receipt_fail_before_writes(self):
        mutations = (
            ('conformance/fixtures/row_csp_extension_profile.json', 'historical_casebase_only', 'census'),
            ('conformance/fixtures/row_csp_extension_profile.json', '"schema_version": 1', '"schema_version": true'),
            ('conformance/fixtures/row_csp_extension_profile.json', '"cheap_orbits_per_role": 32', '"cheap_orbits_per_role": -1'),
            ('conformance/fixtures/row_csp_extension_profile.json', '"seconds_per_orbit": null', '"seconds_per_orbit": 1'),
            ('conformance/fixtures/row_csp_extension_profile.json', 'domain-product-extremes-v1', 'unknown'),
            ('proof/claims.toml', 'status = "working"', 'status = "computed"'),
            ('ESTATE.toml', 'acceptance_authority = false', 'acceptance_authority = true'),
            ('conformance/receipts/row_csp_A.json', '"status": "TIMEOUT"', '"status": "UNSAT"'),
        )
        for relative, old, new in mutations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for folder in ('conformance', 'kernel', 'oracles', 'proof'):
                    shutil.copytree(ROOT / folder, root / folder)
                shutil.copyfile(ROOT / 'ESTATE.toml', root / 'ESTATE.toml')
                destination = root / relative
                destination.write_text(destination.read_text().replace(old, new, 1))
                before = {p: p.read_bytes() for p in (root / 'conformance/receipts').glob('*')}
                with self.assertRaises(ValueError):
                    replay(root, write=True)
                self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_tampered_extension_rejected_without_repeating_search(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative, receipt in self.receipts.items():
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / relative).read_bytes())
            first = next(iter(self.receipts))
            destination = root / first
            destination.write_text(destination.read_text().replace('"claim_promotion": false',
                                                                  '"claim_promotion": true'))
            from replay_row_csp import receipt_bytes
            products = {p: receipt_bytes(r) for p, r in self.receipts.items()}
            with patch('replay_row_csp_extension.receipt_products', return_value=products):
                with self.assertRaisesRegex(ValueError, 'derived receipt mismatch'):
                    replay(root)


if __name__ == '__main__':
    unittest.main()
