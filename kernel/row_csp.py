"""Bounded candidate row-CSP core; no repository acceptance authority.

All masks use the supplied vertex labels. M1 searches exact row sizes and
checks R_G(S_h) <= union of neighboring states. No wing-pair proof is used
to prune M1. The finite pair-sum lambda bound is new, versioned below; it
does not purport to reconstruct the unavailable Patch 73 implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
import time

VERSION = "row-csp-core-v1"
SCALAR_VERSION = "residual-capacity-closed-row-v1"
LAMBDA_VERSION = "adjacent-pair-residual-sum-v1"
ORBIT_VERSION = "exact-row-automorphisms-v1"
M1_VERSION = "residual-domain-backtrack-v1"
MAX_ORDER = 10


def integer(value, name, minimum=0, maximum=None):
    if type(value) is not int or value < minimum or (
            maximum is not None and value > maximum):
        raise ValueError(f"invalid {name}")
    return value


def validate_graph(adj):
    adj = tuple(adj)
    integer(len(adj), "graph order", 1, MAX_ORDER)
    for v, mask in enumerate(adj):
        integer(mask, "adjacency mask", 0, (1 << len(adj)) - 1)
        if mask & (1 << v):
            raise ValueError("loops are unsupported")
        if any(bool(mask & (1 << u)) != bool(adj[u] & (1 << v))
               for u in range(v)):
            raise ValueError("asymmetric adjacency")
    return adj


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask_union(masks):
    result = 0
    for mask in masks:
        result |= mask
    return result


@dataclass(frozen=True)
class RowState:
    selected: int
    residual: int


class RowTable:
    """All 2^n states and their residuals, partitioned by exact size."""

    def __init__(self, horizontal):
        self.graph = validate_graph(horizontal)
        self.n = len(self.graph)
        self.full = (1 << self.n) - 1
        closed = tuple(mask | (1 << v) for v, mask in enumerate(self.graph))
        coverage = [0] * (1 << self.n)
        for selected in range(1, 1 << self.n):
            bit = selected & -selected
            coverage[selected] = coverage[selected ^ bit] | closed[bit.bit_length() - 1]
        self.states = tuple(RowState(s, self.full ^ coverage[s])
                            for s in range(1 << self.n))
        self.by_size = tuple(tuple(s.selected for s in self.states
                                   if s.selected.bit_count() == a)
                             for a in range(self.n + 1))
        self.r_min = tuple(min(self.states[s].residual.bit_count() for s in domain)
                           for domain in self.by_size)
        self.gamma = next(a for a, minimum in enumerate(self.r_min) if minimum == 0)

    @lru_cache(maxsize=None)
    def pair_lambda(self, a, b):
        r"""min |R(X)\Y| + |R(Y)\X| over |X|=a, |Y|=b.

        For adjacent rows h,k, any residuals left after their mutual support
        must fit in the other neighboring rows. Hence this minimum cannot
        exceed sum_{u~h,u!=k} a_u + sum_{v~k,v!=h} a_v. Shared external
        rows are deliberately counted twice: this only weakens the bound.
        """
        integer(a, "row size", 0, self.n)
        integer(b, "row size", 0, self.n)
        if a > b:
            return self.pair_lambda(b, a)
        minimum = 2 * self.n
        for x in self.by_size[a]:
            rx = self.states[x].residual
            for y in self.by_size[b]:
                value = (rx & ~y).bit_count() + (self.states[y].residual & ~x).bit_count()
                minimum = min(minimum, value)
                if minimum == 0:
                    return 0
        return minimum


def validate_sizes(table, rows, sizes):
    sizes = tuple(sizes)
    if len(sizes) != len(rows):
        raise ValueError("size pattern length differs from row order")
    for size in sizes:
        integer(size, "row size", 0, table.n)
    return sizes


def scalar_passes(table, rows, sizes):
    sizes = validate_sizes(table, rows, sizes)
    return all(table.r_min[sizes[h]] <= sum(sizes[k] for k in bits(rows[h]))
               and table.gamma <= sizes[h] + sum(sizes[k] for k in bits(rows[h]))
               for h in range(len(rows)))


def lambda_passes(table, rows, sizes):
    sizes = validate_sizes(table, rows, sizes)
    capacities = tuple(sum(sizes[k] for k in bits(row)) for row in rows)
    return all(table.pair_lambda(sizes[h], sizes[k]) <=
               capacities[h] - sizes[k] + capacities[k] - sizes[h]
               for h in range(len(rows)) for k in bits(rows[h]) if h < k)


@lru_cache(maxsize=None)
def composition_count(length, maximum, total):
    if total < 0 or total > length * maximum:
        return 0
    if length == 0:
        return int(total == 0)
    return sum(composition_count(length - 1, maximum, total - a)
               for a in range(min(maximum, total) + 1))


def size_patterns(length, maximum, total):
    """Enumerate every bounded composition once, in lexicographic order."""
    integer(length, "pattern length", 1, MAX_ORDER)
    integer(maximum, "maximum size", 0, MAX_ORDER)
    integer(total, "target", 0, length * maximum)

    def visit(prefix, remaining):
        if len(prefix) == length:
            if remaining == 0:
                yield prefix
            return
        left = length - len(prefix) - 1
        for a in range(max(0, remaining - left * maximum), min(maximum, remaining) + 1):
            yield from visit(prefix + (a,), remaining - a)

    yield from visit((), total)


class BudgetExceeded(Exception):
    pass


class Budget:
    def __init__(self, limit, *, seconds=None, clock=time.monotonic):
        self.limit = integer(limit, "work limit")
        if seconds is not None and (type(seconds) not in (int, float)
                                    or not math.isfinite(seconds) or seconds < 0):
            raise ValueError("invalid wall-clock budget")
        self.used = 0
        self.clock = clock
        self.deadline = None if seconds is None else clock() + seconds

    def tick(self):
        if self.deadline is not None and self.clock() >= self.deadline:
            raise BudgetExceeded("wall_clock_limit")
        if self.used >= self.limit:
            raise BudgetExceeded("work_limit")
        self.used += 1


def scalar_patterns(table, rows, target, budget, counts):
    """Prune prefixes only by necessary scalar bounds; count skipped leaves."""
    m, n = len(rows), table.n

    def visit(prefix, remaining):
        budget.tick()
        known = len(prefix)
        for h in range(m):
            neighbors = tuple(bits(rows[h]))
            capacity = sum(prefix[k] for k in neighbors if k < known)
            capacity += min(remaining, n * sum(k >= known for k in neighbors))
            if h < known and table.r_min[prefix[h]] > capacity:
                counts["scalar_rejected"] += composition_count(m - known, n, remaining)
                return
            closed = (*neighbors, h)
            closed_capacity = sum(prefix[k] for k in closed if k < known)
            closed_capacity += min(remaining, n * sum(k >= known for k in closed))
            if closed_capacity < table.gamma:
                counts["scalar_rejected"] += composition_count(m - known, n, remaining)
                return
        if known == m:
            counts["scalar_survivors"] += 1
            yield prefix
            return
        left = m - known - 1
        for a in range(max(0, remaining - left * n), min(n, remaining) + 1):
            yield from visit(prefix + (a,), remaining - a)

    yield from visit((), target)


def automorphisms(rows, *, work_limit=100000):
    """Enumerate every adjacency-preserving bijection; never use a subgroup
    as if it were the full group when this bounded search times out.
    """
    rows = validate_graph(rows)
    budget = Budget(work_limit)
    degrees = tuple(row.bit_count() for row in rows)
    order = sorted(range(len(rows)), key=lambda v: (degrees.count(degrees[v]), -degrees[v], v))
    mapping, used, result = {}, set(), []

    def visit(depth):
        budget.tick()
        if depth == len(rows):
            result.append(tuple(mapping[v] for v in range(len(rows))))
            return
        u = order[depth]
        for v in range(len(rows)):
            if v in used or degrees[u] != degrees[v]:
                continue
            if any(bool(rows[u] & (1 << old)) != bool(rows[v] & (1 << new))
                   for old, new in mapping.items()):
                continue
            mapping[u] = v
            used.add(v)
            visit(depth + 1)
            used.remove(v)
            del mapping[u]

    visit(0)
    return tuple(sorted(result))


def orbit_key(sizes, group):
    return min(tuple(sizes[p[v]] for v in range(len(sizes))) for p in group)


def residual_satisfied(table, rows, states):
    if len(states) != len(rows):
        raise ValueError("wrong number of states")
    for state in states:
        integer(state, "selected mask", 0, table.full)
    return all(table.states[states[h]].residual &
               ~mask_union(states[k] for k in bits(rows[h])) == 0
               for h in range(len(rows)))


def solve_m1(table, rows, sizes, *, work_limit=100000, seconds=None,
             fixed=None, clock=time.monotonic):
    """Complete finite DFS unless interrupted. A work unit is a domain-state
    check or branch choice, so propagation as well as branching is bounded.
    Empty domains are UNSAT. SAT includes a checked labeled witness.
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

    def propagate(current):
        while True:
            possible = []
            for domain in current:
                union = 0
                for state in domain:
                    budget.tick()
                    union |= state
                possible.append(union)
            changed = False
            for h, domain in enumerate(current):
                support = mask_union(possible[k] for k in neighbors[h])
                assigned_support = mask_union(current[k][0] for k in neighbors[h]
                                              if len(current[k]) == 1)
                remaining_capacity = sum(sizes[k] for k in neighbors[h] if len(current[k]) > 1)
                kept = []
                mandatory = table.full
                for state in domain:
                    budget.tick()
                    residual = table.states[state].residual
                    if (residual & ~support == 0 and
                            (residual & ~assigned_support).bit_count() <= remaining_capacity):
                        kept.append(state)
                        mandatory &= residual
                if not kept:
                    return None
                if len(kept) < len(domain):
                    current[h] = tuple(kept)
                    changed = True
                # A bit residual in every remaining state must be supplied by
                # a neighbor. If only one neighboring row can supply it,
                # every state in that neighbor's domain must include the bit.
                for k in neighbors[h]:
                    other_support = mask_union(possible[u] for u in neighbors[h] if u != k)
                    forced = mandatory & ~other_support
                    if not forced:
                        continue
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
            if not changed:
                return current

    def visit(current):
        current = propagate(current)
        if current is None:
            return None
        h = min(range(len(rows)), key=lambda v: (len(current[v]) == 1,
                                                len(current[v]), -len(neighbors[v]), v))
        if len(current[h]) == 1:
            witness = tuple(domain[0] for domain in current)
            if not residual_satisfied(table, rows, witness):
                raise AssertionError("singleton propagation failed to verify witness")
            return witness
        for state in current[h]:
            budget.tick()
            child = list(current)
            child[h] = (state,)
            witness = visit(child)
            if witness is not None:
                return witness
        return None

    try:
        witness = visit(domains)
        return {"status": "SAT" if witness is not None else "UNSAT",
                "reason": "checked_witness" if witness is not None else "search_exhausted",
                "work_used": budget.used,
                "witness": None if witness is None else list(witness)}
    except BudgetExceeded as exc:
        return {"status": "TIMEOUT", "reason": str(exc), "work_used": budget.used,
                "witness": None}


def audit(horizontal, rows, target, *, enumeration_limit=250000,
          automorphism_limit=100000, orbit_limit=8, m1_work_limit=10000,
          m1_seconds=None):
    """Audit one exact total. Incomplete enumeration or any unresolved orbit
    prevents UNSAT. Unsearched orbits receive explicit TIMEOUT records.
    """
    table = RowTable(horizontal)
    rows = validate_graph(rows)
    integer(target, "target", 0, table.n * len(rows))
    integer(orbit_limit, "orbit limit")
    integer(m1_work_limit, "M1 work limit")
    # Validate even when the filters leave no search work.
    Budget(m1_work_limit, seconds=m1_seconds)
    enumeration_budget = Budget(enumeration_limit)
    counts = {"raw_patterns": composition_count(len(rows), table.n, target),
              "scalar_rejected": 0, "scalar_survivors": 0, "lambda_rejected": 0}
    result = {"target": target, "target_semantics": "exact_total_selected_vertices",
              "versions": {"core": VERSION, "scalar": SCALAR_VERSION,
                           "lambda": LAMBDA_VERSION, "orbits": ORBIT_VERSION, "m1": M1_VERSION},
              "budgets": {"enumeration_work": enumeration_limit,
                          "automorphism_work": automorphism_limit, "searched_orbits": orbit_limit,
                          "m1_work_per_orbit": m1_work_limit, "m1_seconds_per_orbit": m1_seconds},
              "filters_applied": [SCALAR_VERSION, LAMBDA_VERSION],
              "structural_lemmas_applied": [], "wing_pair_use": "regression_only",
              "pattern_counts": counts, "orbits": [], "automorphism_count": None}
    try:
        group = automorphisms(rows, work_limit=automorphism_limit)
    except BudgetExceeded:
        counts["pending_enumeration"] = counts["raw_patterns"]
        result.update(status="TIMEOUT", exhaustive=False, enumeration_complete=False,
                      enumeration_work_used=0, pipeline_timeout="automorphism_work_limit",
                      outcome_counts={"SAT": 0, "UNSAT": 0, "TIMEOUT": 0}, orbit_count=0)
        return result
    result["automorphism_count"] = len(group)
    groups = {}
    complete, pipeline_timeout = True, None
    try:
        for sizes in scalar_patterns(table, rows, target, enumeration_budget, counts):
            if not lambda_passes(table, rows, sizes):
                counts["lambda_rejected"] += 1
                continue
            key = orbit_key(sizes, group)
            groups[key] = groups.get(key, 0) + 1
    except BudgetExceeded:
        complete, pipeline_timeout = False, "enumeration_work_limit"
    counts["pending_enumeration"] = (counts["raw_patterns"] - counts["scalar_rejected"]
                                     - counts["scalar_survivors"])
    outcomes = {"SAT": 0, "UNSAT": 0, "TIMEOUT": 0}
    for index, (sizes, multiplicity) in enumerate(sorted(groups.items())):
        if index >= orbit_limit:
            outcome = {"status": "TIMEOUT", "reason": "orbit_limit", "work_used": 0, "witness": None}
        else:
            outcome = solve_m1(table, rows, sizes, work_limit=m1_work_limit, seconds=m1_seconds)
        outcomes[outcome["status"]] += 1
        result["orbits"].append({"sizes": list(sizes), "observed_multiplicity": multiplicity, **outcome})
    exhaustive = complete and outcomes["TIMEOUT"] == 0
    result.update(enumeration_complete=complete, enumeration_work_used=enumeration_budget.used,
                  pipeline_timeout=pipeline_timeout, outcome_counts=outcomes, orbit_count=len(groups),
                  exhaustive=exhaustive,
                  status="SAT" if outcomes["SAT"] else "UNSAT" if exhaustive else "TIMEOUT")
    return result
