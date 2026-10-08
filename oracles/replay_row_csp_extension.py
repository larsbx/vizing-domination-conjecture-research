"""Replay additional historical residue orbits with two bounded engines.

The frozen v1 receipts are replayed first. New derived files contain only
previously unresolved orbits. An independently checked UNSAT requires both
new engines to exhaust; any interruption stays TIMEOUT. No claim promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "kernel"), str(ROOT / "oracles")]
from row_csp import M1_VERSION, RowTable, integer, solve_m1
from row_csp_pair import (VERSION as PRIMARY_VERSION, ORDER_VERSION,
                          WORK_VERSION as PRIMARY_WORK_VERSION, solve_m1_pair)
from product_cover import (VERSION as INDEPENDENT_VERSION,
                           WORK_VERSION as INDEPENDENT_WORK_VERSION, solve_product_cover)
from canonical_graph6 import decode_graph6
from replay_row_csp import (direct_product_dominates, receipt_bytes,
                            replay as replay_v1, version_one)

VERSION = "historical-row-csp-extension-v1"
SELECTION_VERSION = "domain-product-extremes-v1"
AGGREGATION_VERSION = "dual-exhaustion-or-checked-witness-v1"
PROFILE_PATH = "conformance/fixtures/row_csp_extension_profile.json"
SCHEMA_PATH = "conformance/schemas/row_csp_extension.schema.json"


def load_profile(root):
    profile = json.loads((root / PROFILE_PATH).read_bytes())
    version_one(profile)
    if (set(profile) != {"schema_version", "profile_version", "scope", "selection", "budgets"}
            or profile["scope"] != "historical_casebase_only"
            or not isinstance(profile["profile_version"], str)
            or not profile["profile_version"].endswith("-v1")):
        raise ValueError("versioned historical-only extension profile required")
    selection = profile["selection"]
    if (set(selection) != {"version", "cheap_orbits_per_role", "stress_orbits_per_role"}
            or selection["version"] != SELECTION_VERSION):
        raise ValueError("unsupported orbit selection version")
    for key in ("cheap_orbits_per_role", "stress_orbits_per_role"):
        integer(selection[key], key)
    budgets = profile["budgets"]
    if (set(budgets) != {"baseline_work_per_orbit", "primary_work_per_orbit",
                        "independent_work_per_orbit", "seconds_per_orbit"}
            or budgets["seconds_per_orbit"] is not None):
        raise ValueError("deterministic work budgets with wall clock disabled required")
    for key in ("baseline_work_per_orbit", "primary_work_per_orbit", "independent_work_per_orbit"):
        integer(budgets[key], key)
    return profile


def select_orbits(receipt, selection):
    pending = [(index, orbit) for index, orbit in enumerate(receipt["orbits"])
               if orbit["status"] == "TIMEOUT"]
    def rank(item):
        sizes = tuple(item[1]["sizes"])
        return math.prod(math.comb(receipt["horizontal_order"], a) for a in sizes), sizes
    ordered = sorted(pending, key=rank)
    cheap = ordered[:selection["cheap_orbits_per_role"]]
    stress = ordered[-selection["stress_orbits_per_role"]:] if selection["stress_orbits_per_role"] else []
    selected = cheap + [item for item in stress if item not in cheap]
    return selected


def check_outcome(graph, sizes, outcome):
    status, witness = outcome["status"], outcome["witness"]
    if status == "SAT":
        if (outcome["reason"] != "checked_witness" or witness is None
                or len(witness) != len(graph)
                or any(type(state) is not int or state < 0 or state >= (1 << len(graph))
                       or state.bit_count() != sizes[h] for h, state in enumerate(witness))
                or not direct_product_dominates(graph, graph, witness)):
            raise ValueError("SAT witness fails independent exact-size/product check")
    elif (status not in ("UNSAT", "TIMEOUT") or witness is not None
          or (status == "UNSAT" and outcome["reason"] != "search_exhausted")
          or (status == "TIMEOUT" and outcome["reason"] not in ("work_limit", "wall_clock_limit"))):
        raise ValueError("invalid search outcome semantics")


def verified_status(graph, sizes, baseline, primary, independent):
    for outcome in (baseline, primary, independent):
        check_outcome(graph, sizes, outcome)
    resolved = {o["status"] for o in (baseline, primary, independent) if o["status"] != "TIMEOUT"}
    if len(resolved) > 1:
        raise ValueError("engines disagree; refuse derived evidence")
    # A witness can be checked without independent search exhaustion.
    if primary["status"] == "SAT":
        return "SAT"
    if primary["status"] == independent["status"] == "UNSAT":
        return "UNSAT"
    return "TIMEOUT"


def source_metadata(root):
    paths = ["kernel/row_csp_pair.py", "oracles/product_cover.py", "oracles/replay_row_csp_extension.py",
             "kernel/row_csp.py", "oracles/replay_row_csp.py", "oracles/canonical_graph6.py",
             "oracles/replay_casebase.py", PROFILE_PATH, SCHEMA_PATH,
             "conformance/fixtures/casebase_classes.json", "proof/claims.toml", "ESTATE.toml"]
    paths.extend(f"conformance/receipts/row_csp_{role}.json" for role in ("A", "A_class", "B"))
    return {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in sorted(paths)}


def receipt_products(root=ROOT):
    profile = load_profile(root)
    # Recomputes source provenance, complete orbit directories and original
    # outcomes. All old claim-state and acceptance-authority gates run here.
    original = replay_v1(root)
    metadata = source_metadata(root)
    products = {}
    for path, receipt in original.items():
        if receipt["kind"] != "row_csp_audit":
            continue
        graph = decode_graph6(receipt["graph6"])
        table = RowTable(graph)
        records = []
        for index, orbit in select_orbits(receipt, profile["selection"]):
            sizes = tuple(orbit["sizes"])
            budget = profile["budgets"]
            baseline = solve_m1(table, graph, sizes, work_limit=budget["baseline_work_per_orbit"])
            primary = solve_m1_pair(table, graph, sizes, work_limit=budget["primary_work_per_orbit"])
            independent = solve_product_cover(graph, graph, sizes, work_limit=budget["independent_work_per_orbit"])
            status = verified_status(graph, sizes, baseline, primary, independent)
            records.append({"original_orbit_index": index, "sizes": list(sizes),
                            "observed_multiplicity": orbit["observed_multiplicity"],
                            "original_reason": orbit["reason"], "baseline": baseline,
                            "primary": primary, "independent": independent, "status": status})
        counts = {status: sum(o["status"] == status for o in records)
                  for status in ("SAT", "UNSAT", "TIMEOUT")}
        pending = receipt["outcome_counts"]["TIMEOUT"]
        unsearched = pending - len(records)
        remaining = unsearched + counts["TIMEOUT"]
        exhaustive = receipt["enumeration_complete"] and remaining == 0
        output = {"schema_version": 1, "kind": "row_csp_extension",
                  "scope": "historical_casebase_only", "acceptance_authority": False,
                  "claim_promotion": False, "role": receipt["role"], "graph6": receipt["graph6"],
                  "graph_id": receipt["graph_id"], "target": receipt["target"],
                  "target_semantics": receipt["target_semantics"], "product": "square",
                  "runtime_requirement": "Python >= 3.11; standard library only",
                  "source_sha256": metadata, "original_receipt": path,
                  "original_orbit_count": receipt["orbit_count"],
                  "original_outcome_counts": receipt["outcome_counts"],
                  "profile_version": profile["profile_version"], "selection": profile["selection"],
                  "budgets": profile["budgets"],
                  "versions": {"extension": VERSION, "baseline": M1_VERSION,
                               "primary": PRIMARY_VERSION, "primary_order": ORDER_VERSION,
                               "primary_work": PRIMARY_WORK_VERSION, "independent": INDEPENDENT_VERSION,
                               "independent_work": INDEPENDENT_WORK_VERSION, "aggregation": AGGREGATION_VERSION},
                  "structural_lemmas_applied": [], "wing_pair_use": "regression_only",
                  "orbits": records, "selected_orbit_count": len(records),
                  "new_outcome_counts": counts, "unsearched_pending_orbits": unsearched,
                  "remaining_unresolved_orbits": remaining, "exhaustive": exhaustive,
                  "status": "SAT" if counts["SAT"] else "UNSAT" if exhaustive else "TIMEOUT"}
        products[f"conformance/receipts/row_csp_extension_{receipt['role'].replace('-', '_')}.json"] = receipt_bytes(output)
    return products


def replay(root=ROOT, *, write=False):
    # Compute all outputs and cross-check every witness before writing any.
    products = receipt_products(root)
    for relative, expected in products.items():
        destination = root / relative
        if write:
            destination.write_bytes(expected)
        elif destination.read_bytes() != expected:
            raise ValueError(f"derived receipt mismatch: {relative}; inspect before --write")
    return {path: json.loads(raw) for path, raw in products.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate only three extension receipts")
    args = parser.parse_args()
    try:
        receipts = replay(write=args.write)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    for path, receipt in receipts.items():
        print(f"{path}: new={receipt['new_outcome_counts']}; "
              f"remaining={receipt['remaining_unresolved_orbits']}; {receipt['status']}")
    print("Historical representatives only. No census, acceptance or claim promotion.")


if __name__ == "__main__":
    main()
