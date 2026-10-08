# Bounded historical row-CSP core v1

Scope: the checked-in historical A, A-class representative and B, plus
separately labeled mathematical regression examples. This is a candidate
implementation for issue #4. Python retains `acceptance_authority = false`;
every claim retains its existing state. `VDC-WING-PAIR`, the census and
strict-surplus claims remain `working`.

## Representation and filters

`kernel/row_csp.py` represents a row state by integer masks `selected` and
`residual`, with bit `g` referring to supplied vertex label `g`. It enumerates
all subsets of the horizontal factor, orders masks numerically, partitions
them by exact size, and computes `R_G(S) = V(G) minus N_G[S]`. Empty states
have full residuals. Finite simple undirected graphs of orders 1–10 are
supported; malformed masks, loops, asymmetric inputs and non-integer sizes
are rejected. The historical entry point accepts only the three pinned
representatives, with source roles and class IDs checked before writes.

Each target is an **exact total selected size**. Bounded compositions
enumerate all size patterns with that total. The scalar stage requires,
for each row `h`, both:

- `r_min[a_h] <= sum_{k adjacent to h} a_k`;
- `gamma(G) <= a_h + sum_{k adjacent to h} a_k`.

Here `r_min[a]` is the exact minimum residual size over size-`a` states.
The second condition follows because the union of selected horizontal
vertices in the closed row neighborhood dominates G. Prefix pruning uses
only upper bounds on still-available capacity. A bounded-composition count
records exactly how many complete patterns each pruned prefix represents.

The new lambda filter `adjacent-pair-residual-sum-v1` is defined by

\[
\lambda_G(a,b)=\min_{|X|=a,\,|Y|=b}
\bigl(|R_G(X)\setminus Y|+|R_G(Y)\setminus X|\bigr).
\]

For adjacent rows `h,k`, reject only when this exceeds
`sum_{u adjacent to h, u != k} a_u + sum_{v adjacent to k, v != h} a_v`.
Every actual pair's two residual sets must fit in those external rows,
so this is a necessary bound. A shared external row is counted twice,
which weakens the bound without introducing false rejection.

This definition is versioned independently of the historical isolated-wing
Patch 73 lambda implementation, whose source is absent. Similar scalar
totals do not establish historical algorithm equivalence. No old lambda,
orbit or gold-audit counts are asserted as replayed.

After these filters, the core enumerates the complete adjacency-preserving
automorphism group of the row factor and selects lexicographically minimal
size vectors. Horizontal state subsets are not individually quotiented:
independent row-by-row relabeling could lose inter-row incidence. Each
orbit records its observed multiplicity. Partial enumeration can give
partial multiplicities, and the receipt identifies that condition.

## M1 and timeout semantics

M1 searches domains of exact-size states and checks the residual constraints
directly. Propagation removes states without possible neighboring support,
checks remaining size capacity, and propagates mandatory residual bits to
their unique possible supporting row. These rules are necessary consequences
of the row constraints. Deterministic depth-first branching covers every
remaining state. A singleton solution is checked against all residual
constraints before being returned.

The solver returns `SAT` only with a labeled mask witness, and `UNSAT` only
after complete search exhaustion. A search work unit is a domain-state scan
or branch choice; it bounds propagation as well as branching. Optional wall
time uses a monotonic clock. Work or wall interruption returns `TIMEOUT`
with no witness. Zero work and zero seconds interrupt before search.

Enumeration and automorphism construction have separate deterministic
prefix/search-node limits. Row tables are bounded by 2^10 states; exact
lambda precomputation by at most 2^20 state pairs. The orbit cap limits M1
calls. Every unsearched orbit is recorded as `TIMEOUT` with `orbit_limit`;
incomplete enumeration instead records a pipeline timeout and a pending
pattern count. A pipeline timeout is not misreported as an M1 orbit outcome.

An aggregate `UNSAT` requires complete enumeration and all residue orbits
resolved. `SAT` can be reported with unresolved other orbits because its
witness suffices. Otherwise the aggregate is `TIMEOUT`. `exhaustive` is true
only when enumeration and all residue searches complete. No timeout supports
a negative conclusion. These finite outcomes do not promote registry claims.

## Replays and receipt boundaries

Run from the repository root:

```sh
python3 -B oracles/replay_row_csp.py
python3 -B -m unittest discover -s conformance/tests -p 'test_*.py' -v
```

To deliberately regenerate only the four derived row-CSP receipts:

```sh
python3 -B oracles/replay_row_csp.py --write
```

The fixed profile in `conformance/fixtures/row_csp_profile.json` uses targets
16, 16, 17; 250,000 enumeration nodes; 100,000 automorphism nodes; eight M1
orbits per representative; and one million work units per searched orbit.
Wall time is disabled for these byte-replayable samples. Budgets may be
changed in that explicit profile and reviewed with regenerated receipts.
The core API also accepts separately bounded finite-factor audits.

Receipts include graph6 and full versioned class IDs, exact target semantics,
filter versions, budgets, pattern counts, automorphism/orbit counts,
SAT/TIMEOUT/UNSAT counts, per-orbit results, and source SHA-256 metadata.
The JSON Schema is `conformance/schemas/row_csp_receipt.schema.json`.
Replaying recomputes outcomes and requires byte agreement. Runtime timing
and timestamps are excluded to keep deterministic replays portable.

The [wing-pair draft](../../proof/wing-pair.md) is a **regression input**,
hash-pinned alongside the fixtures and code. The audit applies no wing-pair
structural filter. The separate regression receipt checks its examples
against M1 and an independent Cartesian-neighbor oracle, including the
shared/distinct outer-row condition and local survival without global
feasibility. It contains two SAT, three UNSAT and one explicit TIMEOUT
example. It grants no proof authority or claim promotion.

## October 7 validation and remaining evidence

The implementation is based on `main` at
`375b63d86c92bfda695293d04a4a42c7b78cae5f`, including the merged
wing-pair draft (#8) and historical identity/provenance repair (#9).

The bounded samples completely enumerate the scalar stage and search eight
residue orbits per representative:

| Historical role | Target | Scalar survivors | Lambda survivors | Residue orbits | M1 UNSAT | M1 TIMEOUT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 16 | 164 | 164 | 30 | 8 | 22 |
| A-class | 16 | 1,311 | 531 | 227 | 8 | 219 |
| B | 17 | 2,232 | 2,232 | 319 | 8 | 311 |

All three aggregate outcomes are **TIMEOUT**. The 24 searched orbits exhaust
without a witness. The 552 unsearched orbits are explicitly unresolved;
this does not reproduce any historical product lower bound or exact value.

Differential tests compare M1 with literal Cartesian domination on every
size pattern of 22 small factor pairs: 37,528 selected sets and 2,800 patterns.
They check the residual equivalence, no false scalar/lambda rejections, SAT
witnesses and exhausted UNSAT searches. Other tests cover exact orbit
groups against small bijections, size enumeration, budget interruption,
fixed wing states, malformed inputs, receipt tampering and fail-before-write
scope/authority checks. All 39 conformance tests pass. The pinned estate
audit and pin check pass, as do both historical identity replay modes and
row-CSP receipt replay. A separate check of the JSON Schema assertions used
by these receipts accepts all four files and rejects five mutated controls
(authority, status, checksum format, witness type and false exhaustion).

The original provenance, case-base fixture/identity receipts, claim registry,
wing-pair proof and estate manifest are unchanged. The authoritative 491-entry
census, independent historical product evidence, canonical acceptance
promotion and independent proof approval remain separate open gates. No
Actions CI success or independent review is asserted by this local record.
