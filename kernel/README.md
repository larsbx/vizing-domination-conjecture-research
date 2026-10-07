# Kernel

Canonical executable validation will live here once promoted.

Candidate status: no kernel code is authoritative yet.

`row_csp.py` now supplies a bounded candidate core: row/residual masks,
complete size-pattern enumeration, scalar and a versioned finite lambda
filter, exact row-factor automorphism orbits, and deterministic M1 search.
It emits explicit search exhaustion, checked witnesses and budget timeouts.
The historical replay entry point and source-pinned receipts are described
in [the v1 core record](../docs/research/row-csp-core-v1.md). The wing-pair
proof is used only in separate regressions. No acceptance or claim status
is changed by this implementation.

Candidate responsibilities:

1. exact domination-number computation;
2. Cartesian product construction;
3. row-state CSP audit replay;
4. lambda-bound computation;
5. structural-lemma filters;
6. receipt generation and verification.

Promotion rule: code in this directory becomes authoritative only after `ARCHITECTURE.md` and `ESTATE.toml` are updated to declare the acceptance boundary, and after independent oracle agreement is recorded.
