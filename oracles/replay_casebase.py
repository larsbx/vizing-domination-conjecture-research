"""Replay literal historical case-base identity evidence without promoting claims."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from canonical_graph6 import ALGORITHM, canonical_graph6, csv_bytes, decode_graph6, deduplicate, json_bytes

ROOT = Path(__file__).resolve().parents[1]


def extract_casebase(root: Path = ROOT) -> bytes:
    provenance = json.loads((root / "conformance/provenance/casebase/provenance.json").read_text())
    sources = {}
    for source in provenance["sources"]:
        raw = (root / source["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError(f"source checksum mismatch: {source['path']}")
        sources[source["role"]] = raw.decode("utf-8")
    labels = provenance["named_labels"]
    headings = re.findall(r"^### `` (I[?-~]{8}) ``", sources["named_graphs"], re.MULTILINE)
    if set(headings) != {labels["A"], labels["B"]} or len(headings) != 2:
        raise ValueError("named-graph headings do not match the two source labels")
    members = re.findall(r"^\[(\d+)/14\] (I[?-~]{8})$", sources["aclass_log"], re.MULTILINE)
    if [int(i) for i, _ in members] != list(range(1, 15)):
        raise ValueError("A-class log must contain exactly the ordered 14 source records")
    codes = [labels["A"], *(code for _, code in members), labels["B"]]
    return ("\n".join(codes) + "\n").encode("ascii")


def replay(root: Path = ROOT, *, write: bool = False) -> dict:
    raw = extract_casebase(root)
    report = deduplicate(raw, required_order=10, required_gamma=4)
    if (report["entry_count"], report["iso_class_count"], report["duplicate_entry_count"]) != (16, 3, 13):
        raise ValueError("recovered case base does not have the pinned 16 -> 3 shape")
    pins = json.loads((root / "conformance/fixtures/casebase_classes.json").read_text())
    if pins["algorithm"] != ALGORITHM:
        raise ValueError("case-base canonicalization version mismatch")
    for pin in pins["classes"]:
        canonical, _ = canonical_graph6(decode_graph6(pin["representative_graph6"]))
        if canonical != pin["canonical_graph6"]:
            raise ValueError(f"canonical class mismatch for {pin['role']}")
        actual = [e["entry_id"] for e in report["entries"] if e["canonical_graph6"] == canonical]
        if actual != pin["entry_ids"]:
            raise ValueError(f"source membership mismatch for {pin['role']}")
    if {p["canonical_graph6"] for p in pins["classes"]} != {c["canonical_graph6"] for c in report["classes"]}:
        raise ValueError("pins must cover all three distinct classes")
    claims_text = (root / "proof/claims.toml").read_text()
    import tomllib
    claims = tomllib.loads(claims_text)
    claim = next(c for c in claims["claim"] if c["id"] == "VDC-CASEBASE-3")
    if claim["status"] != "working":
        raise ValueError("case-base claim must remain working while the census is missing")
    products = {
        "conformance/fixtures/casebase_graph6.txt": raw,
        "conformance/receipts/casebase_identity.json": json_bytes(report),
        "conformance/receipts/casebase_identity.csv": csv_bytes(report),
    }
    # All parsing, provenance, class pins and claim-state checks precede writes.
    for path, expected in products.items():
        destination = root / path
        if write:
            destination.write_bytes(expected)
        elif destination.read_bytes() != expected:
            raise ValueError(f"derived artifact mismatch: {path}; inspect before regenerating")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the three derived artifacts")
    args = parser.parse_args()
    try:
        report = replay(write=args.write)
    except (ValueError, OSError, KeyError, StopIteration) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"Case base: {report['entry_count']} entries -> {report['iso_class_count']} classes; "
          "all n=10, gamma=4. Census 491 -> 470: NOT REPLAYED. VDC-CASEBASE-3: working.")


if __name__ == "__main__":
    main()
