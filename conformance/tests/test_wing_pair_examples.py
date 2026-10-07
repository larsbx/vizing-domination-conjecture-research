"""Corpus-independent checks for proof/wing-pair.md.

The domination oracle constructs closed neighborhoods of product vertices
directly. It does not use the residual characterization or a row-CSP solver.
The pair evaluator below is test-only; it has no acceptance authority.
"""

from itertools import combinations, product
import unittest


def graph(order, edges):
    adjacency = [set() for _ in range(order)]
    for u, v in edges:
        if not (0 <= u < order and 0 <= v < order) or u == v:
            raise ValueError("Expected a finite simple graph")
        adjacency[u].add(v)
        adjacency[v].add(u)
    return tuple(frozenset(neighbors) for neighbors in adjacency)


def path(order):
    return graph(order, ((i, i + 1) for i in range(order - 1)))


def subsets(order, size):
    return tuple(frozenset(s) for s in combinations(range(order), size))


def residual(horizontal, state):
    covered = set(state)
    for vertex in state:
        covered.update(horizontal[vertex])
    return frozenset(range(len(horizontal))) - covered


def outer_rows(rows, wings):
    w1, w2 = wings
    if w1 == w2 or not all(0 <= w < len(rows) for w in wings):
        raise ValueError("Expected two distinct row vertices")
    if w2 not in rows[w1] or len(rows[w1]) != 2 or len(rows[w2]) != 2:
        raise ValueError("Wings must be adjacent and have degree exactly two")
    return next(iter(rows[w1] - {w2})), next(iter(rows[w2] - {w1}))


def admissible_pairs(horizontal, rows, sizes, wings, shared_capacity=False):
    """Evaluate the finite lemma definition, not global row-CSP feasibility."""
    n = len(horizontal)
    if len(sizes) != len(rows) or any(
        not isinstance(a, int) or not 0 <= a <= n for a in sizes
    ):
        raise ValueError("Invalid exact size pattern")
    w1, w2 = wings
    o1, o2 = outer_rows(rows, wings)
    survivors = []
    for x, y in product(subsets(n, sizes[w1]), subsets(n, sizes[w2])):
        f1, f2 = residual(horizontal, x) - y, residual(horizontal, y) - x
        if len(f1) > sizes[o1] or len(f2) > sizes[o2]:
            continue
        if shared_capacity and o1 == o2 and len(f1 | f2) > sizes[o1]:
            continue
        survivors.append((x, y))
    return survivors


def product_closed_masks(horizontal, rows):
    """Use the Cartesian adjacency definition without computing row residuals."""
    n = len(horizontal)
    closed = []
    for h in range(len(rows)):
        for g in range(n):
            neighbors = {(g, h)}
            neighbors.update((other_g, h) for other_g in horizontal[g])
            neighbors.update((g, other_h) for other_h in rows[h])
            closed.append(sum(1 << (other_h * n + other_g)
                              for other_g, other_h in neighbors))
    return tuple(closed)


def selected_mask(states, horizontal_order):
    return sum(1 << (h * horizontal_order + g)
               for h, state in enumerate(states) for g in state)


def covered_mask(closed, selected):
    covered = 0
    while selected:
        bit = selected & -selected
        covered |= closed[bit.bit_length() - 1]
        selected ^= bit
    return covered


def dominates(horizontal, rows, states):
    closed = product_closed_masks(horizontal, rows)
    return covered_mask(closed, selected_mask(states, len(horizontal))) == (
        1 << len(closed)
    ) - 1


def fixed_pattern_states(horizontal_order, sizes):
    return product(*(subsets(horizontal_order, a) for a in sizes))


def direct_feasible_patterns(horizontal, rows):
    """Enumerate all selected vertex sets, including the empty and full sets."""
    n = len(horizontal)
    closed = product_closed_masks(horizontal, rows)
    full = (1 << len(closed)) - 1
    coverage = [0] * (full + 1)
    feasible = set()
    for selected in range(full + 1):
        if selected:
            bit = selected & -selected
            coverage[selected] = coverage[selected ^ bit] | closed[bit.bit_length() - 1]
        if coverage[selected] == full:
            feasible.add(tuple(((selected >> (h * n)) & ((1 << n) - 1)).bit_count()
                               for h in range(len(rows))))
    return feasible


class WingPairExamples(unittest.TestCase):
    def test_closed_neighborhood_and_empty_state_conventions(self):
        horizontal = path(4)
        self.assertEqual(residual(horizontal, set()), frozenset(range(4)))
        self.assertEqual(residual(horizontal, {1}), {3})
        self.assertEqual(residual(horizontal, {0}), {2, 3})
        self.assertEqual(residual(horizontal, {1, 2}), set())

    def test_rejection_while_all_scalar_bounds_pass(self):
        horizontal = path(4)
        rows = graph(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)])
        sizes = (0, 1, 1, 0, 4, 4)
        for h, size in enumerate(sizes):
            minimum = min(len(residual(horizontal, s)) for s in subsets(4, size))
            self.assertLessEqual(minimum, sum(sizes[k] for k in rows[h]))
        self.assertEqual(admissible_pairs(horizontal, rows, sizes, (1, 2)), [])
        pairs = list(product(subsets(4, 1), repeat=2))
        self.assertEqual(min(len(residual(horizontal, x) - y) for x, y in pairs), 0)
        self.assertEqual(min(len(residual(horizontal, y) - x) for x, y in pairs), 0)
        candidates = list(fixed_pattern_states(4, sizes))
        self.assertEqual(len(candidates), 16)
        self.assertFalse(any(dominates(horizontal, rows, states) for states in candidates))

    def test_feasible_witness_and_universal_pair_quantifier(self):
        horizontal, rows = path(4), path(4)
        sizes = (1, 1, 1, 1)
        witness = ({1}, {3}, {0}, {2})
        self.assertTrue(dominates(horizontal, rows, witness))
        survivors = admissible_pairs(horizontal, rows, sizes, (1, 2))
        self.assertIn((frozenset({3}), frozenset({0})), survivors)
        self.assertNotIn((frozenset({0}), frozenset({0})), survivors)

    def test_local_survival_is_not_global_feasibility(self):
        horizontal, rows = path(1), path(6)
        sizes = (0, 0, 1, 1, 0, 0)
        self.assertEqual(len(admissible_pairs(horizontal, rows, sizes, (2, 3))), 1)
        candidates = list(fixed_pattern_states(1, sizes))
        self.assertEqual(len(candidates), 1)
        self.assertFalse(dominates(horizontal, rows, candidates[0]))

    def test_shared_outer_row_requires_union_capacity_for_fixed_pair(self):
        horizontal = path(4)
        rows = graph(3, [(0, 1), (1, 2), (2, 0)])
        sizes, pair = (1, 1, 1), (frozenset({1}), frozenset({2}))
        self.assertEqual(outer_rows(rows, (1, 2)), (0, 0))
        self.assertIn(pair, admissible_pairs(horizontal, rows, sizes, (1, 2)))
        self.assertNotIn(pair, admissible_pairs(horizontal, rows, sizes, (1, 2), True))
        required_wings = sum(1 << (h * 4 + g) for h in (1, 2) for g in range(4))
        closed = product_closed_masks(horizontal, rows)
        for outer_state in subsets(4, 1):
            coverage = covered_mask(closed, selected_mask((outer_state, *pair), 4))
            self.assertNotEqual(coverage & required_wings, required_wings)

    def test_extra_neighbor_cannot_be_ignored(self):
        horizontal = path(1)
        rows = graph(5, [(0, 1), (1, 2), (2, 3), (1, 4), (0, 4)])
        states = (set(), set(), set(), {0}, {0})
        self.assertTrue(dominates(horizontal, rows, states))
        self.assertGreater(len(residual(horizontal, states[1]) - states[2]), len(states[0]))
        with self.assertRaises(ValueError):
            admissible_pairs(horizontal, rows, (0, 0, 0, 1, 1), (1, 2))

    def test_adjacency_is_required_but_outer_degree_is_unrestricted(self):
        horizontal = path(1)
        rows = graph(4, [(0, 1), (1, 2), (2, 3), (3, 0)])
        with self.assertRaises(ValueError):
            outer_rows(rows, (0, 2))
        self.assertEqual(outer_rows(rows, (1, 2)), (0, 3))
        self.assertEqual(len(admissible_pairs(horizontal, rows, (1, 1, 1, 1), (1, 2))), 1)

    def test_all_small_labeled_factors_against_direct_product_domination(self):
        row_factors = (path(4), graph(3, [(0, 1), (1, 2), (2, 0)]))
        factor_pairs, selected_sets = 0, 0
        for n in range(1, 4):
            possible_edges = list(combinations(range(n), 2))
            for edge_mask in range(1 << len(possible_edges)):
                horizontal = graph(n, [edge for i, edge in enumerate(possible_edges)
                                       if edge_mask & (1 << i)])
                for rows in row_factors:
                    factor_pairs += 1
                    selected_sets += 1 << (n * len(rows))
                    feasible = direct_feasible_patterns(horizontal, rows)
                    for sizes in product(range(n + 1), repeat=len(rows)):
                        for shared_capacity in (False, True):
                            if not admissible_pairs(horizontal, rows, sizes, (1, 2),
                                                    shared_capacity):
                                self.assertNotIn(sizes, feasible,
                                                 (horizontal, rows, sizes, shared_capacity))
        self.assertEqual(factor_pairs, 22)
        self.assertEqual(selected_sets, 37528)


if __name__ == "__main__":
    unittest.main()
