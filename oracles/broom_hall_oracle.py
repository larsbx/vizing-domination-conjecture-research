"""Deterministic, dependency-free checks for the broom obstruction.

Research oracle only: NOT the repository's canonical acceptance authority.
The analytic minimality proof is in proof/broom-hall-obstruction.md.
"""
from collections import defaultdict
import json


def broom(t):
    if t < 3:
        raise ValueError("The Hall-failure family is indexed by t >= 3")
    g = [set() for _ in range(4)]
    for u, v in ((0, 1), (1, 2), (2, 3)):
        g[u].add(v)
        g[v].add(u)
    h = [set() for _ in range(2 * t)]
    for i in range(1, t + 1):
        h[0].add(i)
        h[i].add(0)
    for i in range(1, t):
        h[i].add(t + i)
        h[t + i].add(i)
    return tuple(map(frozenset, g)), tuple(map(frozenset, h))


def constructed_set(t):
    return (frozenset((3, i) for i in range(1, t))
            | frozenset((1, t + i) for i in range(1, t))
            | frozenset({(0, 0), (2, t)}))


def adjacent_or_equal(g, h, x, y):
    a, b = x
    c, d = y
    return x == y or (a == c and d in h[b]) or (b == d and c in g[a])


def dominates_factor(h, selected):
    return all(v in selected or any(u in h[v] for u in selected)
               for v in range(len(h)))


def dominates_product(g, h, selected):
    return all(any(adjacent_or_equal(g, h, v, d) for d in selected)
               for v in ((a, b) for a in range(len(g)) for b in range(len(h))))


def block(t, cell):
    a, b = cell
    return (0 if a < 3 else 1, 0 if b <= t else b - t)


def certificate(t):
    g, h = broom(t)
    d = constructed_set(t)
    b = {0} | {t + i for i in range(1, t)}
    # A packing certificate in H: these t closed neighborhoods are disjoint,
    # so every dominating set of H contains at least t vertices.
    targets = [t + i for i in range(1, t)] + [t]
    closed = [{v} | set(h[v]) for v in targets]
    pairwise_disjoint = all(closed[i].isdisjoint(closed[j])
                            for i in range(t) for j in range(i + 1, t))
    # The row-0 and row-3 product fibers force domination in H via disjoint
    # strips {0,1} and {2,3}, hence a product lower bound of 2*t.
    strip01 = {hh for gg, hh in d if gg in (0, 1)}
    strip23 = {hh for gg, hh in d if gg in (2, 3)}
    x = {(1, i) for i in range(1, t)}
    witnesses = {}
    counts = defaultdict(int)
    for u in d:
        counts[block(t, u)] += 1
    for empty in x:
        cell = (3, t + empty[1])
        witnesses[empty] = {block(t, u) for u in d
                            if adjacent_or_equal(g, h, cell, u)}
    neighbors = set().union(*witnesses.values())
    return {
        "t": t,
        "gamma_h_lower_certificate": pairwise_disjoint,
        "B_dominates_H": dominates_factor(h, b),
        "D_dominates_product": dominates_product(g, h, d),
        "D_size": len(d),
        "strip01_dominates_H": dominates_factor(h, strip01),
        "strip23_dominates_H": dominates_factor(h, strip23),
        "strip01_size": len(strip01),
        "strip23_size": len(strip23),
        "X": len(x),
        "N_X": len(neighbors),
        "witnesses": {str(k): sorted(v) for k, v in sorted(witnesses.items())},
        "N_X_blocks": sorted(neighbors),
        "unit_hall_deficit": len(x) - len(neighbors),
        "witness_capacity": sum(counts[z] for z in neighbors),
        "occupied_block_counts": {str(k): val for k, val in sorted(counts.items())},
    }


def check(t):
    c = certificate(t)
    assert c["gamma_h_lower_certificate"] and c["B_dominates_H"]
    assert c["D_dominates_product"] and c["D_size"] == 2 * t
    assert c["strip01_dominates_H"] and c["strip23_dominates_H"]
    assert c["strip01_size"] >= t and c["strip23_size"] >= t
    assert c["X"] == t - 1 and c["N_X"] == 1
    assert c["N_X_blocks"] == [(1, 0)]
    assert c["unit_hall_deficit"] == t - 2
    assert c["witness_capacity"] == t - 1
    return c


if __name__ == "__main__":
    import sys
    maximum = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    print(json.dumps([check(t) for t in range(3, maximum + 1)], indent=2))
