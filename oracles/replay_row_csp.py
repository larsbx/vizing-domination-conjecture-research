"""Replay bounded historical row-CSP receipts and proof-input regressions.

The entry point accepts only the checked-in A/A-class/B representatives.
It does not accept census imports, promote claims, or use the wing proof as
an M1 filter. --write regenerates only four designated derived receipts.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kernel"))
from row_csp import (VERSION, RowTable, audit, integer, lambda_passes,
                     scalar_passes, solve_m1, validate_graph, validate_sizes)
from canonical_graph6 import ALGORITHM, canonical_graph6, decode_graph6
from replay_casebase import replay as replay_casebase

ROLES = ("A", "A-class", "B")


def receipt_bytes(receipt):
    """Keep each derived orbit on one line so receipt diffs remain readable."""
    lines = []
    for key, value in sorted(receipt.items()):
        if key == "orbits":
            encoded = "[\n" + ",\n".join("    " + json.dumps(orbit, sort_keys=True)
                                         for orbit in value) + "\n  ]"
        else:
            encoded = json.dumps(value, indent=2, sort_keys=True).replace("\n", "\n  ")
        lines.append("  " + json.dumps(key) + ": " + encoded)
    return ("{\n" + ",\n".join(lines) + "\n}\n").encode("utf-8")


def version_one(document):
    if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise ValueError("schema_version must be integer 1")


def source_metadata(root):
    paths = ["kernel/row_csp.py", "oracles/replay_row_csp.py", "oracles/canonical_graph6.py",
             "oracles/replay_casebase.py", "conformance/schemas/row_csp_receipt.schema.json",
             "conformance/fixtures/row_csp_profile.json",
             "conformance/fixtures/row_csp_regressions.json", "proof/wing-pair.md",
             "conformance/fixtures/casebase_graph6.txt", "conformance/fixtures/casebase_classes.json",
             "conformance/provenance/casebase/provenance.json"]
    provenance = json.loads((root / paths[-1]).read_bytes())
    paths.extend(source["path"] for source in provenance["sources"])
    return {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in sorted(set(paths))}


def historical_inputs(root):
    replay_casebase(root)
    pins = json.loads((root / "conformance/fixtures/casebase_classes.json").read_bytes())
    profile = json.loads((root / "conformance/fixtures/row_csp_profile.json").read_bytes())
    version_one(pins)
    version_one(profile)
    if (pins.get("kind") != "historical_casebase_only"
            or pins.get("promotion_status") != "blocked_pending_authoritative_census"
            or profile.get("scope") != "historical_casebase_only"
            or pins.get("algorithm") != ALGORITHM):
        raise ValueError("historical-only scope and blocked-promotion metadata required")
    roles = [pin.get("role") for pin in pins["classes"]]
    if sorted(roles) != sorted(ROLES):
        raise ValueError("exactly one A, A-class and B representative required")
    for pin in pins["classes"]:
        canonical, _ = canonical_graph6(decode_graph6(pin["representative_graph6"]))
        if pin.get("iso_class_id") != f"{ALGORITHM}:{canonical}":
            raise ValueError("versioned historical class ID mismatch")
        codes = (root / "conformance/fixtures/casebase_graph6.txt").read_text().splitlines()
        expected = {"A": codes[0], "A-class": codes[1], "B": codes[-1]}
        if pin["representative_graph6"] != expected[pin["role"]]:
            raise ValueError("historical role does not match source-order representative")
    if set(profile["targets"]) != set(ROLES):
        raise ValueError("targets must cover exactly the three historical roles")
    claims = tomllib.loads((root / "proof/claims.toml").read_text())["claim"]
    for claim_id in ("VDC-CASEBASE-3", "VDC-WING-PAIR", "VDC-G4-SQUARE-STRICT-N10",
                     "VDC-ROW-CSP", "VDC-GOLD-AUDIT-ARCH"):
        matches = [claim for claim in claims if claim["id"] == claim_id]
        if len(matches) != 1 or matches[0]["status"] != "working":
            raise ValueError(f"{claim_id} must remain uniquely working for this replay")
    estate = tomllib.loads((root / "ESTATE.toml").read_text())
    if any(language.get("acceptance_authority") is not False for language in estate["language"]):
        raise ValueError("candidate replay has no acceptance authority")
    return pins, profile


def direct_product_dominates(horizontal, rows, states):
    """Independent literal Cartesian-neighbor scan, without residuals."""
    for h in range(len(rows)):
        for g in range(len(horizontal)):
            if states[h] & (1 << g):
                continue
            if any(states[h] & (1 << u) for u in range(len(horizontal))
                   if horizontal[g] & (1 << u)):
                continue
            if any(states[k] & (1 << g) for k in range(len(rows)) if rows[h] & (1 << k)):
                continue
            return False
    return True


def wing_pairs(table, rows, sizes, wings, *, shared=False, fixed=None):
    """Non-authoritative evaluator of the proof's regression hypotheses."""
    sizes = validate_sizes(table, rows, sizes)
    w1, w2 = wings
    integer(w1, "wing row", 0, len(rows) - 1)
    integer(w2, "wing row", 0, len(rows) - 1)
    if (w1 == w2 or not rows[w1] & (1 << w2) or rows[w1].bit_count() != 2
            or rows[w2].bit_count() != 2):
        raise ValueError("adjacent distinct degree-two wings required")
    o1 = next(v for v in range(len(rows)) if rows[w1] & (1 << v) and v != w2)
    o2 = next(v for v in range(len(rows)) if rows[w2] & (1 << v) and v != w1)
    domains = (table.by_size[sizes[w1]], table.by_size[sizes[w2]])
    fixed = fixed or {}
    survivors = []
    for x, y in product(*domains):
        if (w1 in fixed and fixed[w1] != x) or (w2 in fixed and fixed[w2] != y):
            continue
        f1, f2 = table.states[x].residual & ~y, table.states[y].residual & ~x
        if f1.bit_count() > sizes[o1] or f2.bit_count() > sizes[o2]:
            continue
        if shared and o1 == o2 and (f1 | f2).bit_count() > sizes[o1]:
            continue
        survivors.append((x, y))
    return survivors


def regression_receipt(root, metadata):
    fixture = json.loads((root / "conformance/fixtures/row_csp_regressions.json").read_bytes())
    version_one(fixture)
    if fixture.get("scope") != "mathematical_examples_only":
        raise ValueError("regressions must be mathematical examples only")
    records = []
    for example in fixture["examples"]:
        table = RowTable(example["horizontal"])
        rows = validate_graph(example["rows"])
        sizes = validate_sizes(table, rows, example["sizes"])
        fixed = {int(h): mask for h, mask in example.get("fixed", {}).items()}
        outcome = solve_m1(table, rows, sizes, fixed=fixed)
        domains = [((fixed[h],) if h in fixed else table.by_size[size])
                   for h, size in enumerate(sizes)]
        direct_sat = any(direct_product_dominates(table.graph, rows, states)
                         for states in product(*domains))
        if outcome["status"] != example["expected"] or direct_sat != (outcome["status"] == "SAT"):
            raise ValueError(f"M1/direct oracle/expected disagreement: {example['id']}")
        scalar = scalar_passes(table, rows, sizes)
        lambda_ok = lambda_passes(table, rows, sizes)
        ordinary = wing_pairs(table, rows, sizes, example["wings"], fixed=fixed)
        shared = wing_pairs(table, rows, sizes, example["wings"], fixed=fixed, shared=True)
        if direct_sat and (not scalar or not lambda_ok or not ordinary or not shared):
            raise ValueError("a necessary filter rejected a direct witness")
        if outcome["witness"] is not None and not direct_product_dominates(table.graph, rows, outcome["witness"]):
            raise ValueError("SAT witness fails independent domination scan")
        records.append({"id": example["id"], "scalar_pass": scalar, "lambda_pass": lambda_ok,
                        "wing_pairs": len(ordinary), "shared_capacity_pairs": len(shared),
                        "direct_oracle_status": "SAT" if direct_sat else "UNSAT", **outcome})
    # Explicit deterministic interruption receipt, distinct from negative evidence.
    example = fixture["examples"][1]
    interrupted = solve_m1(RowTable(example["horizontal"]), example["rows"], example["sizes"], work_limit=0)
    records.append({"id": "zero-work-timeout", **interrupted})
    counts = {status: sum(record["status"] == status for record in records)
              for status in ("SAT", "UNSAT", "TIMEOUT")}
    return {"schema_version": 1, "kind": "row_csp_regression", "scope": fixture["scope"],
            "acceptance_authority": False, "claim_promotion": False, "core_version": VERSION,
            "source_sha256": metadata, "outcome_counts": counts, "examples": records}


def receipt_products(root=ROOT):
    pins, profile = historical_inputs(root)
    metadata = source_metadata(root)
    products = {}
    for pin in pins["classes"]:
        role = pin["role"]
        graph = decode_graph6(pin["representative_graph6"])
        result = audit(graph, graph, profile["targets"][role], **profile["budgets"])
        receipt = {"schema_version": 1, "kind": "row_csp_audit",
                   "scope": "historical_casebase_only", "acceptance_authority": False,
                   "claim_promotion": False, "graph_id": pin["iso_class_id"], "role": role,
                   "graph6": pin["representative_graph6"], "product": "square",
                   "horizontal_order": len(graph), "row_order": len(graph),
                   "runtime_requirement": "Python >= 3.11; standard library only",
                   "source_sha256": metadata, **result}
        products[f"conformance/receipts/row_csp_{role.replace('-', '_')}.json"] = receipt_bytes(receipt)
    products["conformance/receipts/wing_pair_row_csp.json"] = receipt_bytes(regression_receipt(root, metadata))
    return products


def replay(root=ROOT, *, write=False):
    # Complete provenance, authority and outcome checks before any output write.
    products = receipt_products(root)
    for path, expected in products.items():
        destination = root / path
        if write:
            destination.write_bytes(expected)
        elif destination.read_bytes() != expected:
            raise ValueError(f"derived receipt mismatch: {path}; inspect before --write")
    return {path: json.loads(raw) for path, raw in products.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate four derived row-CSP receipts")
    args = parser.parse_args()
    try:
        receipts = replay(write=args.write)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    for path, receipt in receipts.items():
        print(f"{path}: {receipt['outcome_counts']}")
    print("Historical fixtures / mathematical examples only. No census or claim promotion.")


if __name__ == "__main__":
    main()
