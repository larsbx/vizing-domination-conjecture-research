# Architecture

Status: bootstrap architecture for a candidate research repository.

This repository follows the estate-governance v2 convention: authority first, domain second, language third. The repository is not yet claiming theorem authority. It is a research repository whose current job is to separate conjecture, computation, proof records, and exploratory code.

## Domain

Primary domain: domination in Cartesian graph products.

Main conjecture:

\[
\gamma(G \square H) \geq \gamma(G)\gamma(H).
\]

Working finite target:

\[
\gamma(G)=4,\ |V(G)|=10 \quad\Longrightarrow\quad \gamma(G\square G)>16
\]

for every isomorphism class in the checked census.

## Authority surfaces

### Proof plane: `proof/`

The proof plane records claim states. A claim may be:

- `conjectural`: plausible but not established;
- `working`: supported by thread computation or draft argument, not yet reproduced here;
- `computed`: reproduced by checked-in code and data;
- `proved`: has a repository proof record independent of exploratory scripts;
- `retracted`: kept for provenance but no longer asserted.

### Kernel plane: `kernel/`

The kernel plane contains the bounded candidate row-CSP core described in
[the v1 implementation record](docs/research/row-csp-core-v1.md). The
repository declares no acceptance authority. No kernel code is yet
authoritative; this implementation and its historical samples do not
satisfy the promotion conditions below.

Candidate future kernel responsibilities:

1. parse graph6 / adjacency inputs;
2. compute domination numbers by exact methods;
3. run row-state CSP audits;
4. perform isomorphism deduplication;
5. emit machine-checkable audit receipts.

### Oracles plane: `oracles/`

The oracle plane is for non-authoritative cross-checks: ILP solvers, brute force scripts, nauty/networkx comparisons, and independently written CSP engines.

### Experiments plane: `experiments/`

Experiments are disposable. They may motivate proof lemmas but do not certify claims.

### Docs plane: `docs/`

Docs preserve research status, design notes, audit imports, roadmaps, and handoffs.

## Acceptance boundary

Current state: **no repository-local acceptance boundary**.

The `ESTATE.toml` canonical language entry therefore sets `acceptance_authority = false`. A future PR may promote a canonical kernel to acceptance authority only after:

1. dataset provenance is checked in;
2. at least two independent engines agree on gold vectors;
3. row-CSP certificates are replayable;
4. failure modes and timeout semantics are documented;
5. proof claims in `proof/claims.toml` are updated.

## Research branch map

- Main branch: stratified gold audit of the \(n=10,\gamma=4\) census.
- FC-kernel branch: lemma mining from fiber-capture / residual-footprint patterns.
- Operator branch: surplus-monotonicity diagnostics and operator-induced local lemmas.
- Paper branch: only after claim states are promoted from `working` to `computed` or `proved`.

## Non-goals at bootstrap

- Do not claim a proof of Vizing's conjecture.
- Do not claim a proof of the full \(\gamma=4\) case.
- Do not treat deterministic computation as a theorem without replayable evidence.
- Do not treat side-branch operator reachability as established after the negative depth-4 test.
