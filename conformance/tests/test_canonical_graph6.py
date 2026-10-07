"""Independent isomorphism cross-checks, provenance checks and fail-closed tests."""

import csv
import hashlib
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

    def test_graph6_spec_example_and_permutation_direction(self):
        # McKay's specification encodes these labeled edges as bytes 68,81,99.
        graph = adjacency(5, [(0, 2), (0, 4), (1, 3), (3, 4)])
        self.assertEqual(decode_graph6("DQc"), graph)
        self.assertEqual(encode_graph6(graph), "DQc")
        # This permutation differs from its inverse, exposing reversed maps.
        order = (2, 4, 1, 0, 3)
        expected = adjacency(5, [(0, 3), (1, 3), (1, 4), (2, 4)])
        self.assertEqual(decode_graph6(encode_graph6(graph, order)), expected)
        inverse = tuple(order.index(v) for v in range(5))
        self.assertNotEqual(decode_graph6(encode_graph6(graph, inverse)), expected)

    def test_true_and_false_twin_transpositions_at_supported_maximum(self):
        true_twins = (0, 1, 2)
        false_twins = (3, 4, 5)
        edges = [*itertools.combinations(true_twins, 2),
                 *((v, w) for v in (*true_twins, *false_twins) for w in (6, 7)),
                 (6, 7), (7, 8), (8, 9)]
        graph = adjacency(10, edges)
        key, _ = canonical_graph6(graph)
        for group in (true_twins, false_twins):
            for u, v in itertools.combinations(group, 2):
                order = list(range(10))
                order[u], order[v] = order[v], order[u]
                self.assertEqual(relabel(graph, order), graph)
        rng = random.Random(20261006)
        for _ in range(40):
            order = list(range(10))
            rng.shuffle(order)
            changed = relabel(graph, order)
            actual, witness = canonical_graph6(changed)
            self.assertEqual(actual, key)
            self.assertEqual(decode_graph6(actual), relabel(changed, witness))

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

    def test_non_newline_control_bytes_are_not_source_separators(self):
        for separator in (b"\t", b"\x0b", b"\x0c", b"\x1c", b"\x1d", b"\x1e"):
            with self.subTest(separator=separator), self.assertRaisesRegex(ValueError, "control character"):
                deduplicate(b"I?r@`aii_" + separator + b"I?r@`bgIo\n")

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

    def test_receipt_witnesses_and_source_order_independently(self):
        report = json.loads((ROOT / "conformance/receipts/casebase_identity.json").read_bytes())
        source = extract_casebase().decode("ascii").splitlines()
        with (ROOT / "conformance/receipts/casebase_identity.csv").open(newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
        self.assertEqual([entry["graph6"] for entry in report["entries"]], source)
        self.assertEqual([entry["source_line"] for entry in report["entries"]], list(range(1, 17)))
        self.assertEqual(len(csv_rows), 16)
        for entry, row in zip(report["entries"], csv_rows):
            witness = entry["canonical_permutation"]
            self.assertEqual(sorted(witness), list(range(10)))
            original = decode_graph6(entry["graph6"])
            self.assertEqual(decode_graph6(entry["canonical_graph6"]), relabel(original, witness))
            self.assertEqual(row["graph6"], entry["graph6"])
            self.assertEqual(row["iso_class_id"], entry["iso_class_id"])
            self.assertEqual(row["canonical_permutation"], " ".join(map(str, witness)))

    def test_recovered_json_requires_log_order_and_decoded_metadata(self):
        cases = [
            ("row count", lambda rows: rows.pop(), "14 object records"),
            ("source order", lambda rows: rows.reverse(), "source order"),
            ("edge count", lambda rows: rows[0].update(edges=15), "structural metadata"),
            ("degrees", lambda rows: rows[0].update(deg_seq=[3] * 10), "structural metadata"),
        ]
        for label, change, error in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                shutil.copytree(ROOT / "conformance", root / "conformance")
                shutil.copytree(ROOT / "proof", root / "proof")
                source = root / "conformance/provenance/casebase/aclass_target.json"
                rows = json.loads(source.read_bytes())
                change(rows)
                source.write_text(json.dumps(rows))
                # Repin deliberately: exercise source consistency beyond byte integrity.
                self.repin_source(root, source)
                outputs = self.derived_bytes(root)
                with self.assertRaisesRegex(ValueError, error):
                    replay(root, write=True)
                self.assertEqual(self.derived_bytes(root), outputs)

    def test_original_named_edge_list_must_match_graph6(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "conformance", root / "conformance")
            shutil.copytree(ROOT / "proof", root / "proof")
            source = root / "conformance/provenance/casebase/B_star_4_counterexamples.md"
            source.write_text(source.read_text().replace("(0,4)", "(0,3)", 1))
            self.repin_source(root, source)
            outputs = self.derived_bytes(root)
            with self.assertRaisesRegex(ValueError, "edge list mismatch"):
                replay(root, write=True)
            self.assertEqual(self.derived_bytes(root), outputs)

    @staticmethod
    def derived_bytes(root):
        return {path: (root / path).read_bytes() for path in (
            "conformance/fixtures/casebase_graph6.txt",
            "conformance/receipts/casebase_identity.json",
            "conformance/receipts/casebase_identity.csv",
        )}

    @staticmethod
    def repin_source(root, source):
        path = root / "conformance/provenance/casebase/provenance.json"
        provenance = json.loads(path.read_bytes())
        record = next(s for s in provenance["sources"] if root / s["path"] == source)
        record["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        record["size_bytes"] = source.stat().st_size
        path.write_text(json.dumps(provenance))

    def test_tampered_source_and_pin_fail_before_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "conformance", root / "conformance")
            shutil.copytree(ROOT / "proof", root / "proof")
            target = root / "conformance/fixtures/casebase_graph6.txt"
            original = target.read_bytes()
            for name in ("patch91_full-1.log", "aclass_target.json", "B_star_4_counterexamples.md"):
                source = root / "conformance/provenance/casebase" / name
                source.write_bytes(source.read_bytes() + b"tampered\n")
                with self.subTest(source=name), self.assertRaisesRegex(ValueError, "checksum"):
                    replay(root, write=True)
                self.assertEqual(target.read_bytes(), original)
                shutil.copyfile(ROOT / "conformance/provenance/casebase" / name, source)
            pin = root / "conformance/fixtures/casebase_classes.json"
            contents = json.loads(pin.read_text())
            contents["classes"][0]["canonical_graph6"] = "I????????"
            pin.write_text(json.dumps(contents))
            with self.assertRaisesRegex(ValueError, "canonical class mismatch"):
                replay(root, write=True)
            self.assertEqual(target.read_bytes(), original)

    def test_declared_pin_identity_and_scope_fail_before_writes(self):
        cases = [
            ("class ID", lambda p: p["classes"][0].update(iso_class_id="wrong-id"), "versioned class ID"),
            ("missing ID", lambda p: p["classes"][0].pop("iso_class_id"), "versioned class ID"),
            ("duplicated role", lambda p: p["classes"][0].update(role="B"), "exactly once"),
            ("extra class", lambda p: p["classes"].append(dict(p["classes"][0])), "exactly once"),
            ("source representative", lambda p: p["classes"][1].update(representative_graph6="I?r@`biI_"), "source representative"),
            ("scope", lambda p: p.update(kind="authoritative_census"), "historical evidence"),
            ("promotion", lambda p: p.update(promotion_status="computed"), "blocked pending"),
            ("schema", lambda p: p.update(schema_version=2), "schema-1"),
            ("boolean schema", lambda p: p.update(schema_version=True), "schema-1"),
            ("floating schema", lambda p: p.update(schema_version=1.0), "schema-1"),
        ]
        for label, change, error in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for folder in ("conformance", "proof"):
                    shutil.copytree(ROOT / folder, root / folder)
                path = root / "conformance/fixtures/casebase_classes.json"
                pins = json.loads(path.read_bytes())
                change(pins)
                path.write_text(json.dumps(pins))
                outputs = self.derived_bytes(root)
                with self.assertRaisesRegex(ValueError, error):
                    replay(root, write=True)
                self.assertEqual(self.derived_bytes(root), outputs)

    def test_provenance_scope_and_schema_fail_before_writes(self):
        for field, value in (("kind", "authoritative_census"), ("schema_version", 2),
                             ("schema_version", True), ("schema_version", 1.0)):
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for folder in ("conformance", "proof"):
                    shutil.copytree(ROOT / folder, root / folder)
                path = root / "conformance/provenance/casebase/provenance.json"
                provenance = json.loads(path.read_bytes())
                provenance[field] = value
                path.write_text(json.dumps(provenance))
                outputs = self.derived_bytes(root)
                with self.assertRaisesRegex(ValueError, "historical case-base evidence"):
                    replay(root, write=True)
                self.assertEqual(self.derived_bytes(root), outputs)

    def test_missing_or_duplicate_casebase_claim_fails_before_writes(self):
        for duplicate in (False, True):
            with self.subTest(duplicate=duplicate), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for folder in ("conformance", "proof"):
                    shutil.copytree(ROOT / folder, root / folder)
                path = root / "proof/claims.toml"
                text = path.read_text()
                if duplicate:
                    text += '\n[[claim]]\nid = "VDC-CASEBASE-3"\nstatus = "computed"\n'
                else:
                    text = text.replace('id = "VDC-CASEBASE-3"', 'id = "VDC-CASEBASE-ABSENT"')
                path.write_text(text)
                outputs = self.derived_bytes(root)
                with self.assertRaisesRegex(ValueError, "VDC-CASEBASE-3 exactly once"):
                    replay(root, write=True)
                self.assertEqual(self.derived_bytes(root), outputs)

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
