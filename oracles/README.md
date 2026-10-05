# Oracles

Non-authoritative checkers and exploratory engines live here.

`canonical_graph6.py` provides an exact, versioned individualization/refinement
oracle for simple graphs of order <= 10 and emits deterministic JSON/CSV entry
mappings. `replay_casebase.py` checks the separately recovered historical case
base, source checksums and canonical pins. Both use only Python's standard
library. Their replay and independent conformance tests are documented in
[`census-provenance-gap-2026-10-05.md`](../docs/audits/census-provenance-gap-2026-10-05.md).

Examples:

- an ILP domination checker;
- a brute-force domination checker for small graphs;
- a NetworkX or nauty-backed isomorphism oracle;
- a second row-CSP implementation for differential testing.

Oracle disagreement with the kernel must fail closed. Oracles never promote claims by themselves.
