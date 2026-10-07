# Roadmap

This roadmap turns the working-thread program into repository-local milestones.

## Phase 0 — estate bootstrap

- [x] Add estate-style manifest and architecture.
- [x] Add conservative claim registry.
- [x] Add current status and roadmap.
- [x] Run official estate pinning at governance revision `5ea47dec8086eab6a1dad6fd239688d20ea89891` and verify the generated SHA-256 pin.
- [x] Pass the pinned estate audit, all 12 bootstrap conformance tests, and both historical case-base replay modes from a clean published checkout (2026-10-06).
- [ ] Add CI for the pinned estate audit and Vizing conformance checks. Prerequisite validation is complete; no workflow is configured yet.

## Phase 1 — corpus and deduplication

Goal: convert the reported 491 graph6 entries into a checked 470-isomorphism-class corpus.

Deliverables:

- `conformance/corpus/g4_n10_graph6.txt` or equivalent source file;
- provenance note for where the census came from;
- canonical isomorphism key implementation;
- duplicate report identifying the 21 collapsed entries;
- fixture asserting the case base has three isomorphism classes.

Promotion target:

- `VDC-CASEBASE-3`: `working` -> `computed`.

## Phase 2 — exact domination and product checker

Goal: reproduce \(\gamma(G)=4\) and product values for known fixtures.

Deliverables:

- exact domination-number checker;
- Cartesian product constructor;
- independent oracle check where feasible;
- fixtures for A, A-class representative, B.

Promotion targets:

- base product values to `computed` once fixtures and receipts exist.

## Phase 3 — row-CSP gold audit kernel

Goal: implement the three-mechanism audit in a replayable form.

The [v1 bounded candidate core](row-csp-core-v1.md) and historical sample
receipts are implemented. Canonical acceptance promotion and complete
historical/census audit closure remain pending; the wing-pair proof is used
only as a regression input. No claim is promoted by these samples.

Deliverables:

- row-state representation;
- residual map computation;
- scalar and lambda lower bounds;
- orbit deduplication;
- M1 row-CSP residue solver;
- JSON receipt format;
- replay command for every accepted result.

Promotion target:

- `VDC-GOLD-AUDIT-ARCH`: `working` -> `computed`.

## Phase 4 — wing-pair lemma promotion

Goal: move Patch 90 from thread artifact to repository proof.
The statement and mathematical proof can be recorded independently of
Phases 1–3; executable regression and promotion retain those dependencies.

Deliverables:

- [x] [Proof draft](../../proof/wing-pair.md) with exact hypotheses and a
  proof from product domination.
- [x] Applicability and failure examples, including shared outer capacity
  and the distinction between local survival and global feasibility.
- [x] Small non-authoritative checks against direct product domination in
  `conformance/tests/test_wing_pair_examples.py`.
- [ ] Independent review of the proof record.
- [ ] Authoritative census provenance and canonical row-CSP runner.
- [ ] Replayable regression showing agreement with M1 where both apply.

Promotion target:

- `VDC-WING-PAIR` remains `working` pending review and the executable
  regression gate. A later reviewed change may promote it to `proved`;
  executable audit results require their own code, data, and receipts.
  `computed+proved` is not a registry status.

## Phase 5 — stratified 470-class audit

Goal: audit one representative per structural bucket, then all 470 isomorphism classes.

Suggested bucket invariants:

- \(\gamma(G\square G)\);
- number of edges;
- degree sequence;
- automorphism group size;
- pendant count;
- degree-2 chain signatures;
- true/false twin counts;
- wing-pair count;
- FC/residual-kernel footprint class where available.

Deliverables:

- bucket inventory;
- representative audit receipts;
- full audit receipts;
- failure/time-out report if any.

Promotion target:

- `VDC-G4-SQUARE-STRICT-N10`: `working` -> `computed` if all receipts pass.

## Phase 6 — lemma mining and theory lift

Goal: reduce M1 residue and seek a structural \(\gamma=4\) theorem.

Candidate lemma families:

- pendant-row lemma;
- subdivision-middle lemma;
- true-twin fold lemma;
- false-twin separation lemma;
- FC mixed-lobe penalty lemma;
- generalized wing-pair / low-degree-cluster lemmas.

A side branch merges only after it creates a proof-safe filter with M1 reconciliation.
