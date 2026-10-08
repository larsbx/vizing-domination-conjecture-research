"""Bounded pair-capacity M1 candidate; preserves the v1 core and receipts."""
from __future__ import annotations

import time
from row_csp import (Budget, BudgetExceeded, bits, integer, mask_union,
                     residual_satisfied, validate_graph, validate_sizes)

VERSION = "pair-capacity-arc-m1-v1"
ORDER_VERSION = "minimum-domain-active-degree-v1"
WORK_VERSION = "pair-state-scan-branch-v1"


def solve_m1_pair(table, rows, sizes, *, work_limit=1000000, seconds=None,
                  fixed=None, clock=time.monotonic):
    """DFS with necessary two-row capacity constraints and arc consistency.

    For adjacent h,k, |R(X_h) minus X_k| is at most the sum of the
    prescribed sizes of h's other neighbors, and conversely for k.
    Compatibility is symmetric. No structural lemma is assumed.
    Pair tests, domain-state scans and branch choices each cost one unit.
    """
    rows = validate_graph(rows)
    sizes = validate_sizes(table, rows, sizes)
    budget = Budget(work_limit, seconds=seconds, clock=clock)
    domains = [table.by_size[a] for a in sizes]
    for h, mask in (fixed or {}).items():
        integer(h, "fixed row", 0, len(rows) - 1)
        integer(mask, "fixed state", 0, table.full)
        if mask.bit_count() != sizes[h]:
            raise ValueError("fixed state has wrong size")
        domains[h] = (mask,)
    neighbors = tuple(tuple(bits(row)) for row in rows)
    capacities = tuple(sum(sizes[k] for k in adjacent) for adjacent in neighbors)
    relations = {}

    def propagate(current):
        while True:
            possible, guaranteed = [], []
            for domain in current:
                union, intersection = 0, table.full
                for state in domain:
                    budget.tick()
                    union |= state
                    intersection &= state
                possible.append(union)
                guaranteed.append(intersection)
            changed = False
            for h, domain in enumerate(current):
                support = mask_union(possible[k] for k in neighbors[h])
                supplied = mask_union(guaranteed[k] for k in neighbors[h])
                capacity = sum(sizes[k] - guaranteed[k].bit_count() for k in neighbors[h])
                kept, mandatory = [], table.full
                for state in domain:
                    budget.tick()
                    residual = table.states[state].residual
                    if residual & ~support == 0 and (residual & ~supplied).bit_count() <= capacity:
                        kept.append(state)
                        mandatory &= residual
                if not kept:
                    return None
                if len(kept) < len(domain):
                    current[h] = tuple(kept)
                    changed = True
                for k in neighbors[h]:
                    forced = mandatory & ~mask_union(possible[u] for u in neighbors[h] if u != k)
                    if forced:
                        kept_neighbor = []
                        for state in current[k]:
                            budget.tick()
                            if state & forced == forced:
                                kept_neighbor.append(state)
                        if not kept_neighbor:
                            return None
                        if len(kept_neighbor) < len(current[k]):
                            current[k] = tuple(kept_neighbor)
                            changed = True
            # Pair compatibility is static for this exact pattern. Intersect
            # its full support with the current neighbor domain at each pass.
            for h in range(len(rows)):
                for k in neighbors[h]:
                    neighbor_domain = 0
                    for state in current[k]:
                        budget.tick()
                        neighbor_domain |= 1 << state
                    kept = []
                    for x in current[h]:
                        budget.tick()
                        key = (h, k, x)
                        if key not in relations:
                            support = 0
                            for y in domains[k]:
                                budget.tick()
                                if ((table.states[x].residual & ~y).bit_count() <= capacities[h] - sizes[k]
                                        and (table.states[y].residual & ~x).bit_count() <= capacities[k] - sizes[h]):
                                    support |= 1 << y
                            relations[key] = support
                        if relations[key] & neighbor_domain:
                            kept.append(x)
                    if not kept:
                        return None
                    if len(kept) < len(current[h]):
                        current[h] = tuple(kept)
                        changed = True
            if not changed:
                return current

    def visit(current):
        current = propagate(current)
        if current is None:
            return None
        unresolved = [h for h in range(len(rows)) if len(current[h]) > 1]
        if not unresolved:
            witness = tuple(domain[0] for domain in current)
            if not residual_satisfied(table, rows, witness):
                raise AssertionError("singleton propagation failed to verify witness")
            return witness
        h = min(unresolved, key=lambda v: (len(current[v]),
                     -sum(len(current[k]) > 1 for k in neighbors[v]), v))
        for state in current[h]:
            budget.tick()
            child = list(current)
            child[h] = (state,)
            witness = visit(child)
            if witness is not None:
                return witness
        return None

    try:
        witness = visit(list(domains))
        return {"status": "SAT" if witness is not None else "UNSAT",
                "reason": "checked_witness" if witness is not None else "search_exhausted",
                "work_used": budget.used, "witness": None if witness is None else list(witness)}
    except BudgetExceeded as exc:
        return {"status": "TIMEOUT", "reason": str(exc), "work_used": budget.used, "witness": None}
