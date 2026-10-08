# Vizing domination conjecture research

A candidate research program for domination in Cartesian graph products:

\[
\gamma(G \square H) \geq \gamma(G)\gamma(H).
\]

The finite target is the reported \(n=10,\gamma(G)=4\) census and its
strict square-surplus assertion

\[
\gamma(G\square G)>16.
\]

Work currently uses the checked-in historical A, A-class and B
representatives. Their source records reproduce **16 entries → 3 exact
isomorphism classes**. The authoritative 491-entry census remains
unavailable; its reported 470 classes and 21 duplicate entries require
separate provenance and replay.

## Active roadmap

Each track has a concrete first gate. Registry labels come from
[`proof/claims.toml`](proof/claims.toml); delivered implementation milestones
and finite receipts do not automatically promote those labels.

| Track | Registry label | Current evidence | First gate |
| --- | --- | --- | --- |
| Historical corpus and identity — `VDC-CASEBASE-3` | `working` | [Source-pinned 16 → 3 identity replay](conformance/receipts/casebase_identity.json) | Recover the authoritative ordered census; reproduce 491 → 470 and establish case-base membership. |
| Row-CSP and audit architecture — `VDC-ROW-CSP`, `VDC-GOLD-AUDIT-ARCH` | `working` | [Bounded core](docs/research/row-csp-core-v1.md), [independent extension](docs/research/row-csp-bounded-extension-2026-10-08.md), explicit SAT/UNSAT/TIMEOUT receipts | Resolve the independent-checker backlog and additional historical orbits under versioned budgets; complete canonical acceptance gates. |
| Wing-pair local obstruction — `VDC-WING-PAIR` | `working` | [Proof draft](proof/wing-pair.md), [mathematical audit](docs/audits/wing-pair-review-2026-10-06.md), [candidate M1 regression](conformance/receipts/wing_pair_row_csp.json) | Record proof approval and satisfy provenance, canonical-runner and regression promotion gates. |
| Census-wide strict square surplus — `VDC-G4-SQUARE-STRICT-N10` | `working` | Historical searches at exact totals 16/16/17; all three aggregate outcomes remain TIMEOUT | Complete census ingestion, canonical checker validation and a full stratified audit with every required residue exhausted. |
| Reverse-operator negative control — `VDC-OPERATOR-NEGATIVE` | `working` | [Thread audit](docs/audits/thread-audit-2026-10-05.md); historical negative result awaits executable reproduction | Recover the operator fixtures and independently replay the depth-4 negative control before using it as research evidence. |

The [detailed roadmap](docs/research/roadmap.md) records the bootstrap,
corpus, checker, proof, stratified-audit and theory milestones.

**Unblocked execution order:** independent-checker backlog → additional
historical orbits → local-lemma reconciliation and mining. Authoritative
source recovery can proceed in parallel. Census-wide acceptance follows
source recovery, canonical checker validation and complete audit receipts.

The next bounded experiments should first revisit the **24 selected
patterns already exhausted by M1 but pending independent confirmation**:
six A, three A-class and fifteen B. Two further selected B patterns time
out in both engines; 450 other residue orbits remain unsearched. Each new
search order or budget needs a versioned profile and replayable outcomes.

## Current finite evidence

The original profile exhausts eight orbits per representative. The
extension searches 102 additional unresolved orbits and independently
exhausts 76 as UNSAT. The combined accounting is:

| Historical role | Exact target | Residue orbits | Resolved: original v1 + new independent checks | Remaining unresolved | Aggregate |
| --- | ---: | ---: | ---: | ---: | --- |
| A | 16 | 30 | 8 + 16 | 6 | TIMEOUT |
| A-class | 16 | 227 | 8 + 37 | 182 | TIMEOUT |
| B | 17 | 319 | 8 + 23 | 288 | TIMEOUT |
| Total | — | 576 | 24 + 76 | 476 | TIMEOUT |

A new extension UNSAT requires exhaustion by both the pair-capacity M1
candidate and the independent literal-product checker. A checked SAT
witness suffices; work or clock interruption remains TIMEOUT. Original v1
results retain their original evidence classification. These exact-target
samples establish neither historical product values nor census coverage.

## Working here

[`ESTATE.toml`](ESTATE.toml) and [`ARCHITECTURE.md`](ARCHITECTURE.md) define
the authority planes and acceptance boundary. Python currently has
`acceptance_authority = false`; canonical promotion requires the documented
provenance, independent-engine, receipt, failure-mode and claim-state gates.
The wing-pair proof supplies regression examples and is not an audit filter.

| Path | Role |
| --- | --- |
| [proof/claims.toml](proof/claims.toml), [proof/wing-pair.md](proof/wing-pair.md) | Claim states and proof draft |
| [kernel/](kernel/) | Candidate executable row-CSP checks |
| [oracles/](oracles/) | Independent checks and deterministic replay entry points |
| [conformance/](conformance/) | Historical fixtures, source provenance, schemas, receipts and tests |
| [experiments/](experiments/) | Non-authoritative search and lemma-mining work |
| [docs/research/](docs/research/), [docs/audits/](docs/audits/) | Milestones, experiment records and reviews |
| [paper/](paper/) | Publication artifacts after their evidence gates |

## Reproducible checks

Run from the repository root with Python 3.11 or later:

```sh
python3 -B oracles/replay_casebase.py
python3 -B oracles/replay_row_csp.py
python3 -B oracles/replay_row_csp_extension.py
python3 -B -m unittest discover -s conformance/tests -p 'test_*.py' -v
```

The current tree passes 52 conformance tests. The
[extension record](docs/research/row-csp-bounded-extension-2026-10-08.md)
documents algorithm versions, deterministic work budgets, source hashes,
regeneration commands and pinned estate validation. CI configuration remains
a bootstrap milestone; these are local validation results.

## Claim and novelty boundary

`VDC-MAIN` remains `conjectural`; all other registered claims remain
`working`. Finite search closure, proof approval, canonical acceptance and
mathematical novelty are separate gates. A novelty claim additionally needs
a dated literature search, the nearest prior art, an exact contribution
beyond it and recorded review. The full Vizing conjecture remains the
long-term mathematical target.
