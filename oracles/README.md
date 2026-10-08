# Oracles

Non-authoritative checkers and exploratory engines live here.

`canonical_graph6.py` provides an exact, versioned individualization/refinement
oracle for simple graphs of order <= 10 and emits deterministic JSON/CSV entry
mappings. `replay_casebase.py` checks the separately recovered historical case
base, source checksums, agreement between the recovered JSON and log,
recorded structural metadata, A/B edge lists and canonical pins. Both use only
Python's standard library. Their replay and independent conformance tests are documented in
[`census-provenance-gap-2026-10-05.md`](../docs/audits/census-provenance-gap-2026-10-05.md).

Examples:

- an ILP domination checker;
- a brute-force domination checker for small graphs;
- a NetworkX or nauty-backed isomorphism oracle;
- a second row-CSP implementation for differential testing.

Oracle disagreement with the kernel must fail closed. Oracles never promote claims by themselves.

`product_cover.py` supplies an independent Boolean search using literal
Cartesian-neighborhood clauses and exact row cardinalities. It imports no
M1 code or residual/filter machinery. `replay_row_csp_extension.py` first
replays v1, then checks additional unresolved historical orbits with both
engines. A new UNSAT record requires both to exhaust. Search and checker
interruptions remain TIMEOUT.

```sh
python3 -B oracles/replay_row_csp_extension.py
```

The [October 8 extension record](../docs/research/row-csp-bounded-extension-2026-10-08.md)
documents the versioned profile, budgets, new receipts and independent
validation. All claim states and acceptance boundaries remain unchanged.
