"""Replay literal historical case-base identity evidence without promoting claims."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from canonical_graph6 import ALGORITHM, canonical_graph6, csv_bytes, decode_graph6, deduplicate, json_bytes

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_KIND = "historical_casebase_only"


def extract_casebase(root: Path = ROOT) -> bytes:
    provenance = json.loads((root / "conformance/provenance/casebase/provenance.json").read_text())
    if (not isinstance(provenance, dict) or type(provenance.get("schema_version")) is not int
            or provenance["schema_version"] != 1
            or provenance.get("kind") != HISTORICAL_KIND):
        raise ValueError("provenance must identify schema-1 historical case-base evidence")
    sources = {}
    for source in provenance["sources"]:
        raw = (root / source["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError(f"source checksum mismatch: {source['path']}")
        if len(raw) != source["size_bytes"]:
            raise ValueError(f"source size mismatch: {source['path']}")
        if source["role"] in sources:
            raise ValueError(f"duplicate source role: {source['role']}")
        sources[source["role"]] = raw.decode("utf-8")
    labels = provenance["named_labels"]
    if not isinstance(labels, dict) or set(labels) != {"A", "B"}:
        raise ValueError("named labels must identify exactly A and B")
    headings = re.findall(r"^### `` (I[?-~]{8}) ``", sources["named_graphs"], re.MULTILINE)
    if set(headings) != {labels["A"], labels["B"]} or len(headings) != 2:
        raise ValueError("named-graph headings do not match the two source labels")
    members = re.findall(r"^\[(\d+)/14\] (I[?-~]{8})$", sources["aclass_log"], re.MULTILINE)
    if [int(i) for i, _ in members] != list(range(1, 15)):
        raise ValueError("A-class log must contain exactly the ordered 14 source records")
    records = json.loads(sources["aclass_json"])
    if (not isinstance(records, list) or len(records) != 14
            or any(not isinstance(row, dict) for row in records)):
        raise ValueError("A-class JSON must contain exactly 14 object records")
    if [row.get("graph6") for row in records] != [code for _, code in members]:
        raise ValueError("A-class JSON labels must match the numbered log in source order")
    for index, row in enumerate(records, 1):
        adj = decode_graph6(row["graph6"])
        degrees = sorted(mask.bit_count() for mask in adj)
        if row.get("edges") != sum(degrees) // 2 or row.get("deg_seq") != degrees:
            raise ValueError(f"A-class JSON structural metadata mismatch at record {index}")
    # This earlier note corroborates named labels and labeled edges only.
    # Its product values and other historical assertions are not replayed here.
    sections = re.findall(r"^## Counterexample [12]: graph6 = `` (I[?-~]{8}) ``\n"
                          r"(.*?)(?=^## |\Z)", sources["named_graphs_original"],
                          re.MULTILINE | re.DOTALL)
    if len(sections) != 2 or {code for code, _ in sections} != set(labels.values()):
        raise ValueError("original named-graph headings do not match A/B source labels")
    for code, body in sections:
        paragraph = re.search(r"\*\*Edges\*\*:\s*\$\$(.*?)\$\$", body, re.DOTALL)
        if paragraph is None:
            raise ValueError(f"original named-graph edge list missing: {code}")
        edges = [tuple(map(int, pair)) for pair in
                 re.findall(r"\((\d+),(\d+)\)", paragraph.group(1))]
        adj = decode_graph6(code)
        expected = [(u, v) for u in range(len(adj)) for v in range(u + 1, len(adj))
                    if adj[u] & (1 << v)]
        if sorted(edges) != expected:
            raise ValueError(f"original named-graph edge list mismatch: {code}")
    codes = [labels["A"], *(row["graph6"] for row in records), labels["B"]]
    return ("\n".join(codes) + "\n").encode("ascii")


def replay(root: Path = ROOT, *, write: bool = False) -> dict:
    raw = extract_casebase(root)
    report = deduplicate(raw, required_order=10, required_gamma=4)
    if (report["entry_count"], report["iso_class_count"], report["duplicate_entry_count"]) != (16, 3, 13):
        raise ValueError("recovered case base does not have the pinned 16 -> 3 shape")
    pins = json.loads((root / "conformance/fixtures/casebase_classes.json").read_text())
    if (not isinstance(pins, dict) or type(pins.get("schema_version")) is not int
            or pins["schema_version"] != 1
            or pins.get("kind") != HISTORICAL_KIND
            or pins.get("promotion_status") != "blocked_pending_authoritative_census"):
        raise ValueError("class pins must remain schema-1 historical evidence blocked pending the census")
    if pins.get("algorithm") != ALGORITHM:
        raise ValueError("case-base canonicalization version mismatch")
    codes = raw.decode("ascii").splitlines()
    representatives = {"A": codes[0], "A-class": codes[1], "B": codes[-1]}
    class_pins = pins.get("classes")
    if (not isinstance(class_pins, list) or len(class_pins) != 3
            or any(not isinstance(pin, dict) or not isinstance(pin.get("role"), str)
                   for pin in class_pins)
            or {pin["role"] for pin in class_pins} != set(representatives)):
        raise ValueError("class pins must identify A, A-class and B exactly once")
    for pin in class_pins:
        if pin.get("representative_graph6") != representatives[pin["role"]]:
            raise ValueError(f"source representative mismatch for {pin['role']}")
        canonical, _ = canonical_graph6(decode_graph6(pin["representative_graph6"]))
        if canonical != pin.get("canonical_graph6"):
            raise ValueError(f"canonical class mismatch for {pin['role']}")
        if pin.get("iso_class_id") != f"{ALGORITHM}:{canonical}":
            raise ValueError(f"versioned class ID mismatch for {pin['role']}")
        actual = [e["entry_id"] for e in report["entries"] if e["canonical_graph6"] == canonical]
        if actual != pin["entry_ids"]:
            raise ValueError(f"source membership mismatch for {pin['role']}")
    if {p["canonical_graph6"] for p in class_pins} != {c["canonical_graph6"] for c in report["classes"]}:
        raise ValueError("pins must cover all three distinct classes")
    claims_text = (root / "proof/claims.toml").read_text()
    import tomllib
    claims = tomllib.loads(claims_text)
    casebase_claims = [c for c in claims["claim"] if c["id"] == "VDC-CASEBASE-3"]
    if len(casebase_claims) != 1:
        raise ValueError("claim registry must identify VDC-CASEBASE-3 exactly once")
    claim = casebase_claims[0]
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
