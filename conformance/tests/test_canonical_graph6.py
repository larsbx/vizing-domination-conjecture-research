"""Independent isomorphism cross-checks, provenance checks and fail-closed tests."""

import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "oracles"))
from canonical_graph6 import canonical_graph6, decode_graph6, deduplicate, domination_number, encode_graph6
from replay_casebase import extract_casebase, replay


def adjacency(n, edges):
    masks = [0] * n
    for u, v in edges:
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return tuple(masks)


def relabel(adj, order):
    """Independent relabeling, without using the graph6 encoder."""
    return tuple(sum(1 << j for j, v in enumerate(order) if adj[u] & (1 << v))
                 for u in order)


def isomorphic(left, right):
    """Independent degree-preserving bijection search with adjacency checks.

    Does not call canonicalization, graph6 encoding, refinement, or twin pruning.
    """
    if len(left) != len(right):
        return False
    n = len(left)
    ld = [a.bit_count() for a in left]
    rd = [a.bit_count() for a in right]
    if sorted(ld) != sorted(rd):
        return False
    order = sorted(range(n), key=lambda v: (ld.count(ld[v]), -ld[v], v))
    assigned = {}
    used = set()

    def visit(depth):
        if depth == n:
            return True
        u = order[depth]
        for v in range(n):
            if v in used or ld[u] != rd[v]:
                continue
            if any(bool(left[u] & (1 << old)) != bool(right[v] & (1 << new))
                   for old, new in assigned.items()):
                continue
            assigned[u] = v
            used.add(v)
            if visit(depth + 1):
                return True
            used.remove(v)
            del assigned[u]
        return False

    return visit(0)


class CanonicalTests(unittest.TestCase):
    def test_all_graphs_up_to_five_vertices_against_independent_bijections(self):
        expected_counts = [1, 1, 2, 4, 11, 34]
        for n in range(6):
            edges = list(itertools.combinations(range(n), 2))
            representatives = []
            keys = []
            for bits in range(1 << len(edges)):
                graph = adjacency(n, [e for i, e in enumerate(edges) if bits & (1 << i)])
                key, permutation = canonical_graph6(graph)
                self.assertEqual(decode_graph6(key), relabel(graph, permutation))
                independent_class = next((i for i, rep in enumerate(representatives)
                                          if isomorphic(graph, rep)), None)
                if independent_class is None:
                    self.assertNotIn(key, keys)
                    representatives.append(graph)
                    keys.append(key)
                else:
                    self.assertEqual(key, keys[independent_class])
            self.assertEqual(len(representatives), expected_counts[n])

    def test_regular_graphs_that_defeat_degree_and_color_refinement(self):
        cycle = adjacency(6, [(i, (i + 1) % 6) for i in range(6)])
        triangles = adjacency(6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)])
        self.assertNotEqual(canonical_graph6(cycle)[0], canonical_graph6(triangles)[0])
        self.assertFalse(isomorphic(cycle, triangles))

    def test_casebase_pairwise_agreement_and_relabeling_invariance(self):
        graphs = [decode_graph6(code) for code in extract_casebase().decode().splitlines()]
        keys = [canonical_graph6(g)[0] for g in graphs]
        rng = random.Random(20261005)
        for i, graph in enumerate(graphs):
            for j, other in enumerate(graphs):
                self.assertEqual(keys[i] == keys[j], isomorphic(graph, other))
            for _ in range(25):
                order = list(range(len(graph)))
                rng.shuffle(order)
                self.assertEqual(canonical_graph6(relabel(graph, order))[0], keys[i])
        self.assertEqual(len(set(keys)), 3)

    def test_graph6_known_edges_and_padding(self):
        # Patch 43 explicitly lists the labeled edges independently of graph6.
        expected = [(0, 4), (0, 5), (0, 8), (0, 9), (1, 4), (1, 5), (2, 6),
                    (2, 7), (2, 8), (2, 9), (3, 6), (3, 7), (4, 8), (4, 9), (6, 8), (6, 9)]
        self.assertEqual(decode_graph6("I?r@`aii_"), adjacency(10, expected))
        for code in ["", "I?", "I?r@`aii__", "I?r@`aiia", " I?r@`aii_", ":I???????", "~???", "I?r@`aii_\x00"]:
            with self.subTest(code=code), self.assertRaises(ValueError):
                decode_graph6(code)
        self.assertEqual(decode_graph6(">>graph6<<I?r@`aii_"), adjacency(10, expected))

    def test_domination_input_checks(self):
        self.assertEqual(domination_number(()), 0)
        self.assertEqual(domination_number((0,) * 4), 4)
        self.assertEqual(domination_number(adjacency(6, [(i, (i + 1) % 6) for i in range(6)])), 2)
        with self.assertRaisesRegex(ValueError, "gamma"):
            deduplicate((encode_graph6(adjacency(10, list(itertools.combinations(range(10), 2)))) + "\n").encode(), required_gamma=4)
        with self.assertRaisesRegex(ValueError, "order"):
            deduplicate(b"?\n", required_order=10)

    def test_duplicate_ids_preserve_source_order_and_lines(self):
        raw = b">>graph6<<\r\n\r\nI?r@`_iy_\r\nI?r@`biI_\r\nI?r@`_iy_\r\n"
        result = deduplicate(raw)
        self.assertEqual(result["iso_class_count"], 1)
        self.assertEqual(result["duplicate_entry_count"], 2)
        self.assertEqual([e["source_line"] for e in result["entries"]], [3, 4, 5])
        self.assertEqual([e["duplicate_of_entry_id"] for e in result["entries"]], [None, 1, 1])

    def test_census_gate_rejects_casebase_and_writes_no_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = subprocess.run([sys.executable, str(ROOT / "oracles/canonical_graph6.py"),
                                     str(ROOT / "conformance/fixtures/casebase_graph6.txt"),
                                     "--json", str(output / "report.json"), "--csv", str(output / "report.csv"),
                                     "--order", "10", "--gamma", "4", "--expected-entries", "491",
                                     "--expected-classes", "470", "--expected-duplicates", "21"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("observed 16, expected 491", result.stderr)
            self.assertFalse((output / "report.json").exists())
            self.assertFalse((output / "report.csv").exists())


class ReplayTests(unittest.TestCase):
    def test_checked_in_bytes_replay(self):
        report = replay()
        self.assertEqual((report["entry_count"], report["iso_class_count"]), (16, 3))
        self.assertFalse((ROOT / "conformance/corpus/g4_n10_graph6.txt").exists())

    def test_tampered_source_and_pin_fail_before_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "conformance", root / "conformance")
            shutil.copytree(ROOT / "proof", root / "proof")
            target = root / "conformance/fixtures/casebase_graph6.txt"
            original = target.read_bytes()
            source = root / "conformance/provenance/casebase/patch91_full-1.log"
            source.write_bytes(source.read_bytes() + b"tampered\n")
            with self.assertRaisesRegex(ValueError, "checksum"):
                replay(root, write=True)
            self.assertEqual(target.read_bytes(), original)
            shutil.copyfile(ROOT / "conformance/provenance/casebase/patch91_full-1.log", source)
            pin = root / "conformance/fixtures/casebase_classes.json"
            contents = json.loads(pin.read_text())
            contents["classes"][0]["canonical_graph6"] = "I????????"
            pin.write_text(json.dumps(contents))
            with self.assertRaisesRegex(ValueError, "canonical class mismatch"):
                replay(root, write=True)
            self.assertEqual(target.read_bytes(), original)

    def test_claim_promotion_is_blocked_without_census(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "conformance", root / "conformance")
            shutil.copytree(ROOT / "proof", root / "proof")
            path = root / "proof/claims.toml"
            text = path.read_text()
            block = text.split('id = "VDC-CASEBASE-3"', 1)[1].split('[[claim]]', 1)[0]
            text = text.replace(block, block.replace('status = "working"', 'status = "computed"'))
            path.write_text(text)
            with self.assertRaisesRegex(ValueError, "remain working"):
                replay(root)


if __name__ == "__main__":
    unittest.main()
