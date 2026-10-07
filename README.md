# Vizing domination conjecture research

This repository organizes a research program around **Vizing's domination conjecture** for Cartesian graph products:

\[
\gamma(G \square H) \geq \gamma(G)\gamma(H).
\]

The active computational and structural focus is the diagonal \(\gamma=4\) case, especially the observed strict square-surplus phenomenon

\[
s(G) := \gamma(G \square G)-\gamma(G)^2 > 0.
\]

## Current program state

This repository starts from the October 2026 working thread and should be treated as a **candidate research repository** until the computations and proofs are reproduced from checked-in artifacts.

Established in the working record, pending repository reproduction:

- row-state CSP formulation for domination in \(G\square H\);
- three-mechanism audit architecture:
  \[
  \lambda\text{-bound} \to \text{structural lemmas} \to \text{row-CSP residue};
  \]
- verified audits for three base isomorphism classes: graph `A`, one A-class representative, and graph `B`;
- wing-pair structural lemma as the first proof-safe local obstruction;
- census correction: the 491-entry \(n=10,\gamma=4\) dataset reportedly collapses to 470 isomorphism classes;
- negative operator-reachability result for the four simple reverse operators, which are useful as lemma-mining diagnostics but not as a covering descent algebra.

Open until reproduced here:

- canonical dataset ingestion and isomorphism deduplication;
- canonical acceptance promotion and full row-CSP gold audit closure;
- proof records for structural lemmas;
- full stratified audit of the 470 isomorphism classes.

The recovered historical case-base labels replay as **16 entries -> 3 exact
isomorphism classes**, with source checksums and JSON/CSV identity receipts.
The original `aclass_target.json` now agrees with the historical log in source
order. The authoritative 491-entry census and its 21 duplicate rows remain
unavailable, so `VDC-CASEBASE-3` stays `working`. See the
[provenance recovery record](docs/audits/census-provenance-gap-2026-10-05.md).

The [wing-pair proof draft](proof/wing-pair.md) now records the local
residual-capacity lemma independently of the missing census. It includes
exact hypotheses, a proof from product domination, and applicability and
failure examples checked against direct product domination on small graphs.
`VDC-WING-PAIR` remains `working`; independent review, canonical row-CSP
regression, and promotion are pending. See the
[October 6 progress record](docs/research/status-2026-10-06-wing-pair.md) and
[October 7 restack record](docs/research/status-2026-10-07-wing-pair-restack.md).

The [bounded row-CSP candidate core](docs/research/row-csp-core-v1.md) now
replays the checked-in historical A/A-class/B representatives. Its samples
search eight residue orbits each and explicitly time out the remaining
orbits. Separate versioned receipts regress the wing-pair examples against
M1 and direct product domination. These samples do not reproduce historical
product values or census claims; all claim states and acceptance authority
remain unchanged.

## Repository layout

This repository follows the estate `authority -> domain -> language` convention.

```text
ESTATE.toml                       estate manifest
ARCHITECTURE.md                   authority and surface map
proof/claims.toml                 claim registry
proof/wing-pair.md                corpus-independent proof draft
kernel/                           canonical executable validation once promoted
oracles/                          non-authoritative exploration engines
experiments/                      disposable experiments and spikes
docs/research/                    status, roadmap, design notes
docs/audits/                      audit records and thread imports
paper/                            publication artifacts when ready
```

## Main conjectural target

The broad conjecture is Vizing's domination conjecture. The working finite target is:

> For every \(n=10\), \(\gamma(G)=4\) census isomorphism class, verify \(\gamma(G\square G)>16\) by a reproducible gold audit.

That finite target is not a proof of Vizing's conjecture, but it is the current executable route to sharpen the \(\gamma=4\) structural theory.
