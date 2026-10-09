# Bounded historical row-CSP extension — 2026-10-08

This extends the candidate core merged in [PR #11](https://github.com/larsbx/vizing-domination-conjecture-research/pull/11)
at `c7a4ef8f5ac5d5cc19f394e00ff8dd21cc4d20d5`. The original v1 core,
profile and four receipts are preserved byte for byte. The new experiment
searches **102 additional unresolved orbits** and independently exhausts
**76 as UNSAT**. All three aggregate evidence outcomes remain **TIMEOUT**.
These are the three checked-in historical representatives, with exact
selected totals 16, 16 and 17. The corpus and every claim state retain their
existing boundaries; Python retains `acceptance_authority = false`.

## Search improvements and their justification

The baseline is `residual-domain-backtrack-v1`. The additional candidate
in [`kernel/row_csp_pair.py`](../../kernel/row_csp_pair.py) is
`pair-capacity-arc-m1-v1`. It retains every labeled horizontal state and
adds two necessary propagation rules to complete depth-first search.

For adjacent rows h,k, any solution with states X,Y satisfies

\[
|R_G(X)\setminus Y| \leq \sum_{u\sim h,\,u\ne k} a_u,
\qquad
|R_G(Y)\setminus X| \leq \sum_{v\sim k,\,v\ne h} a_v.
\]

Each residual set must be covered by the indicated remaining rows; their
union has size at most the sum of their prescribed sizes. A shared outer
row does not invalidate these separate necessary inequalities. The code
caches this pair relation within one search call. Arc consistency removes
a state only if no current state in a neighboring row satisfies both
inequalities. A genuine solution supplies a compatible pair on every
edge, so it survives each removal. This is a consequence of M1 itself,
without applying the wing-pair draft or any structural lemma.

For each current domain D_k, let I_k be the intersection of its selected
masks. Every state in that row already selects I_k. Residual coordinates
outside the union of neighboring I_k must therefore fit within
`sum_k (a_k - |I_k|)` additional selections. This strengthens the old
singleton-only capacity check. The original possible-support and unique
supporter rules are retained. Using unions from the beginning of a pass
can weaken propagation after a later removal, but cannot remove a feasible
state: those unions remain supersets of all current choices.

Branching selects the smallest non-singleton domain, then the row with the
most still-unresolved neighbors, then the supplied row label. States remain
numerically ordered. Every surviving state is explored unless the budget
interrupts the search. Pair relations never cross search calls or patterns.

The new work unit counts a pair-compatibility test, a domain-state scan
(including neighbor-domain bitsets), or a branch choice. Relation cache
misses consume the full pair-test work. Table construction and validation
retain the core's finite order-10 bounds. These units differ from the v1
units; raw count ratios are not wall-time speedup measurements. Pair
precomputation adds overhead on some easy patterns, so v1 remains available
and its outcomes are recorded alongside the new candidate.

## Independent checker

[`oracles/product_cover.py`](../../oracles/product_cover.py), version
`literal-product-cover-dpll-v1`, imports no row table, residuals, scalar or
lambda filters, or M1 code. It constructs literal Cartesian closed
neighborhoods. Each product vertex contributes a positive covering clause,
and each row has an exact cardinality constraint.

It propagates row cardinalities and single-choice clauses to a fixed point.
It then chooses a smallest uncovered clause and a variable appearing in
the most uncovered clauses, breaking ties numerically. Both truth values
are searched. Once all cover clauses hold, remaining row quotas can be
filled from available vertices without invalidating any clause. A returned
witness is checked for exact row sizes and neighborhood coverage. A work
unit is a row-cardinality scan, clause scan (including branch scoring), or
branch choice. Exhaustion and interruptions have separate outcomes.

The replay entry point additionally checks every SAT witness with the
existing literal Cartesian-neighbor scan. Engine disagreements reject all
output generation. An additional orbit is recorded as UNSAT only when both
the pair candidate and independent checker exhaust. A SAT witness from any
engine is checked directly even if another search times out. An existing
SAT in the replayed v1 directory also remains SAT in the aggregate. In this
profile there are no historical-target SAT witnesses; the small-factor
conformance tests exercise independently checked positive cases.

## Versioned profile and results

The profile is
[`row_csp_extension_profile.json`](../../conformance/fixtures/row_csp_extension_profile.json),
`historical-unresolved-32-cheap-8-stress-v1`. It selects only TIMEOUT orbits
from the freshly replayed v1 directory. Rank is the exact domain-product
estimate `product_h binomial(10, a_h)`, then the size vector. Per role, take
the 32 smallest estimates followed by the eight largest, removing overlap.
A has only 22 unresolved orbits, so every one is selected. The eight stress
slots prevent the experiment from covering only the easiest patterns.

Each selected orbit has independent caps of 1,000,000 v1 work units,
1,000,000 pair-candidate work units and 2,000,000 direct-checker work units.
Wall time is disabled for deterministic receipts. There are 102 baseline,
102 primary and 102 independent calls: at most 408,000,000 search work
units under their respective definitions. Original fixture/provenance,
size enumeration and automorphism checks run first under their unchanged
v1 limits. Algorithm, selection, aggregation and work definitions have
separate versions; any future budget/profile change must bump the profile
version and regenerate the source-pinned receipts.

| Historical role | Original pending | Additional searched | Primary UNSAT | Independently checked UNSAT | Selected pending | Unsearched pending | Remaining pending | Aggregate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 22 | 22 | 22 | 16 | 6 | 0 | 6 | TIMEOUT |
| A-class | 219 | 40 | 40 | 37 | 3 | 179 | 182 | TIMEOUT |
| B | 311 | 40 | 38 | 23 | 17 | 271 | 288 | TIMEOUT |
| Total | 552 | 102 | 100 | 76 | 26 | 450 | 476 | TIMEOUT |

The old 24 exhausted orbits are preserved as previously replayed evidence,
not relabeled as new independent checks. Together with 76 new checked
results, 100 of the 576 original residue orbits are resolved in this
conservative evidence accounting. The remaining 476 include 450 unsearched
orbits and 26 selected orbits lacking a conclusive dual-engine result.

For A, the pair candidate exhausts all 22 formerly pending patterns. Six
still hit the independent checker's cap, so the extension's evidence
aggregate stays TIMEOUT. The two pair-candidate TIMEOUTs occur in B, at
original orbit indices 291 and 310. A checker timeout never becomes a
verified negative merely because another engine completed.

Three newly checked B orbits demonstrate useful improvement over the
one-million-unit v1 cap. Indices refer to the preserved, zero-based v1
orbit directory:

| Original B index | Exact size vector | v1 outcome/work | Pair outcome/work | Direct outcome/work |
| ---: | --- | --- | --- | --- |
| 56 | `[1,1,0,1,2,2,3,5,2,0]` | TIMEOUT / 1,000,000 | UNSAT / 53,158 | UNSAT / 1,119,541 |
| 64 | `[1,1,0,2,0,3,1,1,3,5]` | TIMEOUT / 1,000,000 | UNSAT / 196,094 | UNSAT / 378,857 |
| 249 | `[1,1,2,2,2,2,1,2,2,2]` | TIMEOUT / 1,000,000 | UNSAT / 58,025 | UNSAT / 244,389 |

## Replay and validation

Run from the repository root:

```sh
python3 -B oracles/replay_row_csp.py
python3 -B oracles/replay_row_csp_extension.py
python3 -B -m unittest discover -s conformance/tests -p 'test_*.py' -v
```

To regenerate only the three additional derived receipts:

```sh
python3 -B oracles/replay_row_csp_extension.py --write
```

The extension first replays all original receipts, so an edited baseline,
provenance drift, changed claim state or promoted acceptance authority fails
before writes. It computes every result and checks witnesses/disagreement
before writing any extension output. Sources and the frozen baseline
receipts are SHA-256 pinned. No timestamps, elapsed times or machine-specific
paths enter the receipts. The schema is
[`row_csp_extension.schema.json`](../../conformance/schemas/row_csp_extension.schema.json).

Both new engines are compared with exhaustive literal product enumeration
on all 2,800 size patterns and 37,528 selected sets across the existing 22
small factor pairs. Additional checks cover dense, disconnected and
non-square factors, every fixed-middle-state example for P3 square, exact
witness sizes, work/clock interruptions, malformed input, selection without
duplicates, disagreement rejection, and fail-before-write scope/authority
controls. The balanced B index-249 regression requires independent UNSAT
exhaustion and the baseline TIMEOUT at the same recorded budget.

All **52 conformance tests pass**. Both identity replay modes, original v1
byte replay and extension byte replay pass. The estate pin check and audit
pass at the manifest's pinned governance revision
`5ea47dec8086eab6a1dad6fd239688d20ea89891`. An independent local structural
validator checks every JSON Schema assertion used by all three extension
receipts and rejects nine mutated controls (scope, authority, promotion,
schema type, checksum, witness, false aggregate exhaustion and false
dual-engine exhaustion). Python syntax, JSON/TOML parsing, all 33 relative
Markdown links and whitespace checks pass.

Validation is local. The authoritative 491-entry census remains unavailable.
The historical source bytes, identity artifacts, proof records, claim
registry, estate manifest and original row-CSP artifacts are unchanged.
Independent search agreement here does not promote acceptance authority or
reproduce any unreplayed census or historical product-value assertion.
