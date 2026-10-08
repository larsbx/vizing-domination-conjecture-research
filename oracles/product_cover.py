"""Independent bounded Boolean search on literal Cartesian neighborhoods.

No row table, residual mask, scalar/lambda filter or M1 code is imported.
Each product vertex gives a positive covering clause; each row has an
exact cardinality. Exhaustive binary DFS follows cardinality/unit-clause
propagation. Interrupted trees remain TIMEOUT.
"""
from __future__ import annotations

import math
import time

VERSION = "literal-product-cover-dpll-v1"
WORK_VERSION = "cardinality-clause-scan-branch-v1"


class Interrupted(Exception):
    pass


def natural(value, name, maximum=None):
    if type(value) is not int or value < 0 or (maximum is not None and value > maximum):
        raise ValueError(f"invalid {name}")
    return value


def adjacency(graph):
    graph = tuple(graph)
    if not 1 <= len(graph) <= 10:
        raise ValueError("invalid graph order")
    for v, mask in enumerate(graph):
        natural(mask, "adjacency mask", (1 << len(graph)) - 1)
        if mask & (1 << v) or any(bool(mask & (1 << u)) != bool(graph[u] & (1 << v))
                                 for u in range(v)):
            raise ValueError("simple undirected graph required")
    return graph


def solve_product_cover(horizontal, rows, sizes, *, work_limit=1000000,
                        seconds=None, fixed=None, clock=time.monotonic):
    horizontal, rows = adjacency(horizontal), adjacency(rows)
    n, m = len(horizontal), len(rows)
    sizes = tuple(sizes)
    if len(sizes) != m:
        raise ValueError("wrong size pattern length")
    for size in sizes:
        natural(size, "row size", n)
    natural(work_limit, "work limit")
    if seconds is not None and (type(seconds) not in (int, float) or
                                not math.isfinite(seconds) or seconds < 0):
        raise ValueError("invalid wall-clock budget")
    deadline = None if seconds is None else clock() + seconds
    work = 0

    def tick():
        nonlocal work
        if deadline is not None and clock() >= deadline:
            raise Interrupted("wall_clock_limit")
        if work == work_limit:
            raise Interrupted("work_limit")
        work += 1

    row_masks = tuple(((1 << n) - 1) << (h * n) for h in range(m))
    # A clause lists exactly the product vertices that can dominate (h,g).
    clauses = []
    for h in range(m):
        for g in range(n):
            vertices = {(h, g)}
            vertices.update((h, u) for u in range(n) if horizontal[g] & (1 << u))
            vertices.update((k, g) for k in range(m) if rows[h] & (1 << k))
            clauses.append(sum(1 << (k * n + u) for k, u in vertices))
    positive, negative = 0, 0
    for h, state in (fixed or {}).items():
        natural(h, "fixed row", m - 1)
        natural(state, "fixed state", (1 << n) - 1)
        if state.bit_count() != sizes[h]:
            raise ValueError("fixed state has wrong size")
        positive |= state << (h * n)
        negative |= row_masks[h] ^ (state << (h * n))

    def visit(selected, excluded):
        while True:
            before = (selected, excluded)
            for h, row in enumerate(row_masks):
                tick()
                chosen = (selected & row).bit_count()
                unknown = row & ~(selected | excluded)
                remaining = sizes[h] - chosen
                if remaining < 0 or remaining > unknown.bit_count():
                    return None
                if remaining == 0:
                    excluded |= unknown
                elif remaining == unknown.bit_count():
                    selected |= unknown
            for clause in clauses:
                tick()
                if selected & clause:
                    continue
                choices = clause & ~excluded
                if choices == 0:
                    return None
                if choices & (choices - 1) == 0:
                    selected |= choices
            if before == (selected, excluded):
                break
        smallest = None
        uncovered = []
        for clause in clauses:
            tick()
            if selected & clause:
                continue
            choices = clause & ~excluded
            uncovered.append(choices)
            key = (choices.bit_count(), choices)
            if smallest is None or key < smallest:
                smallest = key
        if smallest is None:
            # Once every cover clause is true, pad each row to its exact size.
            for h, row in enumerate(row_masks):
                tick()
                needed = sizes[h] - (selected & row).bit_count()
                available = row & ~(selected | excluded)
                for _ in range(needed):
                    bit = available & -available
                    selected |= bit
                    available ^= bit
            return selected
        candidates = smallest[1]
        scored = []
        while candidates:
            candidate = candidates & -candidates
            candidates ^= candidate
            score = 0
            for choices in uncovered:
                tick()
                if choices & candidate:
                    score += 1
            scored.append((-score, candidate))
        bit = min(scored)[1]
        tick()
        witness = visit(selected | bit, excluded)
        if witness is not None:
            return witness
        tick()
        return visit(selected, excluded | bit)

    try:
        selected = visit(positive, negative)
        witness = None if selected is None else [
            (selected >> (h * n)) & ((1 << n) - 1) for h in range(m)]
        if witness is not None:
            if (any(state.bit_count() != sizes[h] for h, state in enumerate(witness))
                    or any(selected & clause == 0 for clause in clauses)):
                raise AssertionError("invalid direct product witness")
        return {"status": "SAT" if witness is not None else "UNSAT",
                "reason": "checked_witness" if witness is not None else "search_exhausted",
                "work_used": work, "witness": witness}
    except Interrupted as exc:
        return {"status": "TIMEOUT", "reason": str(exc), "work_used": work, "witness": None}
