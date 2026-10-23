# Thread audit and corrective disposition — 2026-10-23

**Scope:** the exploratory Vizing support/Hall → broom → coverage progression
through Patches 33–36, with a pointer to the separate graph-product-ring repo.
**Authority:** historical thread evaluation and the analytic broom proof
in `proof/broom-hall-obstruction.md`; *not* new canonical census acceptance.

## Repository selection and current source correction

This repository owns Vizing-domination research. The cross-cutting Cartesian
cycle-symbol algebra belongs to `larsbx/graph-product-ring-research`.
An earlier thread audit flagged a negative C14 symbol coefficient in a
historical Paper III draft; **do not import that issue here as unresolved**.
Graph-ring PR #24, merged into main on 2026-10-23, already drafted corrected
Paper III v5 with positive C14 and full-ring NB/primitive-symbol results:
https://github.com/larsbx/graph-product-ring-research/pull/24 .
Claim-state/acceptance review remains controlled by that repository.

## Mathematical state and repairs

**Established independently by argument:**
- For every graph H, the two disjoint endpoint strips of P4 square H each
  contain at least gamma(H) members of any product dominating set. Hence
  gamma(P4 square H) >= 2 gamma(H).
- The explicit broom H_t (center, t leaves and t-1 pendant extensions)
  has gamma(H_t)=t, and the displayed 2t-point set D_t dominates P4 square
  H_t. Thus gamma(P4 square H_t)=2t for **every t>=3**, not just t<=7.
- For the designated minimum-factor block partition, t-1 empty blocks have
  exactly one occupied *block* witness, of occupancy t-1. The ratio
  |X|/|N(X)|=t-1 is unbounded, even with minimum D.
- This disproves unrestricted unit-capacity block Hall and every fixed
  positive-factor *unit-block-count* Hall bound.

**Not established by that counterexample:**
- Failure of the capacitated inequality
  |X| <= sum_(Y in N(X)) |D intersect Y|.
  The broom family meets this inequality **with equality**.
- Failure of all possible averaging schemes, private-neighborhood charges,
  or Clark--Suen reconstructions.
- Failure of Vizing; this family is Vizing-tight.

**Patches 33–35:** the closed-neighborhood counting inequality
gamma(G square H) >= ceil(|V(G)||V(H)|/(Delta(G)+Delta(H)+1))
is valid. The gamma(G)=gamma(H)=2 argument deduced from it is valid but
the product-domination case is covered by substantially older literature;
do not claim a novel resolution. Exhaustive three-vertex coverage for
C4 square C4 is a finite regression, not a new general competition theorem.

**Patch 36:** the reported n<=7 Class-B, gamma=3 census
(14 factors, 105 unordered pairs, 97 residuals) is thread-supplied
computational evidence, **not imported/replayed as canonical data here**.
The stated next-step implication is incorrect: excluding dominating
8-sets only proves gamma >=9, not gamma >=10.
A >=10 surplus certificate must also exclude all dominating 9-sets.
MILP 'optimal' logs alone do not provide independently checkable
infeasibility certificates. Respect `ESTATE.toml` non-authoritative Python
setting until provenance, replay and proof acceptance requirements pass.

## Next proof gates

1. Retain broom as the permanent unit-Hall counterexample regression.
2. Test capacitated Hall as a **separate undecided conjecture**; an actual
   failure requires an example with |X| > sum witness occupancies, not merely
   |X|>|N(X)|.
3. Reproduce the gamma=3 n<=7 factor list, solver statuses, and independence
   of nine-set infeasibility checks before any `computed` or `proved`
   promotion. Search for a structural explanation of the surplus, not a
   circular rephrasing of Vizing.
4. Keep the historical n=10, gamma=4 census provenance and row-CSP gates
   in the repository README as the canonical main track; this patch does
   not change them.

## Scope limitation

This is a focused correction to the Vizing research branch, not a claim
that every archived script, TeX file, or checksum in the former sandbox
bundles is valid. Previous NUL-filled archived sources and ambiguous
download paths are provenance issues, not grounds to promote mathematical
claims.
