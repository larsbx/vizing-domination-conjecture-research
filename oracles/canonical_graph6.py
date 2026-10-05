"""Exact, deterministic graph6 isomorphism keys for simple graphs of order <= 10.

This is a named oracle, not a promoted acceptance kernel. No third-party
dependencies, hashes-as-isomorphism-tests, or heuristic collision decisions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
from pathlib import Path

ALGORITHM = "degree-ir-graph6-v1"
MAX_ORDER = 10
HEADER = ">>graph6<<"


def decode_graph6(code: str) -> tuple[int, ...]:
    """Decode the short graph6 form, rejecting malformed or unsupported input.

    Specification: https://users.cecs.anu.edu.au/~bdm/data/formats.txt
    Whitespace, extra bytes, and nonzero padding are rejected, not normalized.
    """
    if code.startswith(HEADER):
        code = code[len(HEADER):]
    if not code or any(not 63 <= ord(c) <= 126 for c in code):
        raise ValueError("invalid graph6 characters or empty graph")
    n = ord(code[0]) - 63
    if n > MAX_ORDER:
        raise ValueError(f"graph6 order {n} unsupported; maximum is {MAX_ORDER}")
    bit_count = n * (n - 1) // 2
    if len(code) != 1 + (bit_count + 5) // 6:
        raise ValueError("wrong graph6 payload length")
    bits = [((ord(c) - 63) >> k) & 1 for c in code[1:] for k in range(5, -1, -1)]
    if any(bits[bit_count:]):
        raise ValueError("nonzero graph6 padding")
    adj = [0] * n
    pos = 0
    for j in range(1, n):
        for i in range(j):
            if bits[pos]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            pos += 1
    return tuple(adj)


def encode_graph6(adj: tuple[int, ...], order: tuple[int, ...] | None = None) -> str:
    n = len(adj)
    if n > MAX_ORDER:
        raise ValueError("unsupported graph order")
    if any(a < 0 or a >> n or a & (1 << i) for i, a in enumerate(adj)):
        raise ValueError("invalid adjacency mask or loop")
    if any(((adj[i] >> j) & 1) != ((adj[j] >> i) & 1)
           for i in range(n) for j in range(i)):
        raise ValueError("asymmetric adjacency")
    if order is None:
        order = tuple(range(n))
    if sorted(order) != list(range(n)):
        raise ValueError("order must be a vertex permutation")
    bits = [(adj[order[i]] >> order[j]) & 1 for j in range(1, n) for i in range(j)]
    bits += [0] * (-len(bits) % 6)
    chars = [chr(n + 63)]
    for start in range(0, len(bits), 6):
        value = 0
        for bit in bits[start:start + 6]:
            value = value * 2 + bit
        chars.append(chr(value + 63))
    return "".join(chars)


def canonical_graph6(adj: tuple[int, ...]) -> tuple[str, tuple[int, ...]]:
    """Return an exact canonical encoding and an original-vertex permutation.

    Start with degree cells in ascending order, repeatedly refine each cell by
    neighbor counts into the ordered cells, then individualize a vertex in the
    first nonsingleton cell. Visit every inequivalent branch and minimize the
    resulting graph6 strings. A twin transposition fixes all other vertices,
    so only one branch per twin group is necessary. No other pruning is used.

    Isomorphic inputs have corresponding search trees and the same minimum.
    Conversely, equal output strings encode identical relabeled graphs, so
    they cannot merge nonisomorphic inputs. The key is versioned: it is not
    promised to equal nauty's canonical labeling or the minimum over ALL n!
    labelings. The returned permutation witnesses each relabeling directly.
    """
    encode_graph6(adj)  # Validate adjacency before searching.
    degree_cells: dict[int, list[int]] = {}
    for v, neighbors in enumerate(adj):
        degree_cells.setdefault(neighbors.bit_count(), []).append(v)
    initial = tuple(tuple(degree_cells[d]) for d in sorted(degree_cells))

    def refine(cells: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
        while True:
            masks = tuple(sum(1 << v for v in cell) for cell in cells)
            refined = []
            for cell in cells:
                groups: dict[tuple[int, ...], list[int]] = {}
                for v in cell:
                    signature = tuple((adj[v] & mask).bit_count() for mask in masks)
                    groups.setdefault(signature, []).append(v)
                refined.extend(tuple(groups[s]) for s in sorted(groups))
            result = tuple(refined)
            if len(result) == len(cells):
                return result
            cells = result

    def search(cells: tuple[tuple[int, ...], ...]) -> tuple[str, tuple[int, ...]]:
        cells = refine(cells)
        index = next((i for i, cell in enumerate(cells) if len(cell) > 1), None)
        if index is None:
            order = tuple(v for cell in cells for v in cell)
            return encode_graph6(adj, order), order
        cell = cells[index]
        representatives = []
        results = []
        for v in cell:
            if any((adj[v] & ~((1 << v) | (1 << u))) ==
                   (adj[u] & ~((1 << v) | (1 << u))) for u in representatives):
                continue
            representatives.append(v)
            rest = tuple(u for u in cell if u != v)
            results.append(search(cells[:index] + ((v,), rest) + cells[index + 1:]))
        return min(results)

    return search(initial)


def domination_number(adj: tuple[int, ...]) -> int:
    """Exhaustive closed-neighborhood coverage; used only as an input check."""
    target = (1 << len(adj)) - 1
    closed = tuple(a | (1 << v) for v, a in enumerate(adj))
    for size in range(len(adj) + 1):
        for chosen in itertools.combinations(range(len(adj)), size):
            covered = 0
            for v in chosen:
                covered |= closed[v]
            if covered == target:
                return size
    raise AssertionError("all vertices must dominate a finite simple graph")


def deduplicate(raw: bytes, *, required_order: int | None = None,
                required_gamma: int | None = None) -> dict:
    text = raw.decode("ascii")
    entries = []
    classes: dict[str, list[int]] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line or line == HEADER:
            continue
        code = line.removeprefix(HEADER)
        try:
            adj = decode_graph6(code)
            gamma = domination_number(adj)
            if required_order is not None and len(adj) != required_order:
                raise ValueError(f"order {len(adj)} != required {required_order}")
            if required_gamma is not None and gamma != required_gamma:
                raise ValueError(f"gamma {gamma} != required {required_gamma}")
            canonical, order = canonical_graph6(adj)
        except ValueError as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
        entry_id = len(entries) + 1
        class_id = f"{ALGORITHM}:{canonical}"
        members = classes.setdefault(class_id, [])
        entries.append({"entry_id": entry_id, "source_line": line_number,
                        "graph6": code, "order": len(adj), "gamma": gamma,
                        "iso_class_id": class_id, "canonical_graph6": canonical,
                        "canonical_permutation": list(order),
                        "duplicate_of_entry_id": members[0] if members else None})
        members.append(entry_id)
    if not entries:
        raise ValueError("no graph6 entries")
    class_rows = [{"iso_class_id": key,
                   "canonical_graph6": entries[members[0] - 1]["canonical_graph6"],
                   "representative_entry_id": members[0], "entry_ids": members,
                   "duplicate_entry_ids": members[1:]}
                  for key, members in sorted(classes.items())]
    return {"schema_version": 1, "algorithm": ALGORITHM,
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "entry_count": len(entries), "iso_class_count": len(classes),
            "duplicate_entry_count": len(entries) - len(classes),
            "entries": entries, "classes": class_rows,
            "duplicate_classes": [row for row in class_rows if len(row["entry_ids"]) > 1]}


def json_bytes(report: dict) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")


def csv_bytes(report: dict) -> bytes:
    output = io.StringIO(newline="")
    fields = ["entry_id", "source_line", "graph6", "iso_class_id", "canonical_graph6",
              "canonical_permutation", "duplicate_of_entry_id", "order", "gamma"]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for entry in report["entries"]:
        row = dict(entry)
        row["canonical_permutation"] = " ".join(map(str, row["canonical_permutation"]))
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--order", type=int)
    parser.add_argument("--gamma", type=int)
    parser.add_argument("--expected-entries", type=int)
    parser.add_argument("--expected-classes", type=int)
    parser.add_argument("--expected-duplicates", type=int)
    args = parser.parse_args()
    try:
        report = deduplicate(args.input.read_bytes(), required_order=args.order,
                             required_gamma=args.gamma)
        for field, expected in (("entry_count", args.expected_entries),
                                ("iso_class_count", args.expected_classes),
                                ("duplicate_entry_count", args.expected_duplicates)):
            if expected is not None and report[field] != expected:
                raise ValueError(f"{field}: observed {report[field]}, expected {expected}")
        paths = [args.input.resolve(), args.json.resolve(), args.csv.resolve()]
        if len(set(paths)) != 3:
            raise ValueError("input, JSON and CSV paths must be distinct")
        args.json.write_bytes(json_bytes(report))
        args.csv.write_bytes(csv_bytes(report))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"{report['entry_count']} entries -> {report['iso_class_count']} classes; "
          f"{report['duplicate_entry_count']} duplicate entries")


if __name__ == "__main__":
    main()
