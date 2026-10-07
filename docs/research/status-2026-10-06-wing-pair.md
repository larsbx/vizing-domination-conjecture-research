# Wing-pair progress — 2026-10-06

Scope: the corpus-independent portion of
[issue #5](https://github.com/larsbx/vizing-domination-conjecture-research/issues/5).

The authoritative ordered 491-entry `n=10, gamma=4` corpus has not been
recovered, and the user reports no additional source. Issue #2's acceptance
criteria remain unmet. This change supplies no census entries and does not
advance corpus-dependent claims or declare issue #5 complete.

## Recorded work

- [`proof/wing-pair.md`](../../proof/wing-pair.md) formalizes the Patch 90
  residual-capacity inequalities for adjacent degree-two rows in `G square H`.
- The proof starts from Cartesian adjacency and domination, establishes the
  row-residual equivalence, and derives sound rejection of an exact size
  pattern when every prescribed-size wing pair violates an inequality.
- The hypotheses identify the row factor, closed neighborhoods, and valid
  sizes. Outer vertices may coincide and have arbitrary degrees. Connectivity,
  `n=10`, and `gamma=4` are not required.
- Examples cover rejection after every scalar bound passes, a feasible
  witness, local survival without global feasibility, shared outer capacity,
  and failure when an extra neighbor is ignored.
- `conformance/tests/test_wing_pair_examples.py` checks those examples and
  compares the necessary tests with a direct product-domination oracle on
  all labeled horizontal factors through order three and two row factors.
This is an independent small check, not the canonical row-CSP runner.

Validation: all eight conformance tests pass. The exhaustive direct-product
comparison examines 37,528 selected vertex sets across 22 factor pairs.

The retained source `PATCH_90_wing_pair_lemma-1.md` supplied the intended
Lemma M statement. Its historical audit counts, runtime assertions, and
timeout conclusions have not been reproduced or promoted by this change.

## Claim and authority boundary

`VDC-WING-PAIR` remains `working`, with its proof record linked from
`proof/claims.toml`. `ESTATE.toml` lists the new proof surface and retains
`acceptance_authority = false`. Every other claim retains its status.

The filter gives a sound rejection when its pair set is empty. A surviving
pair is not a global feasibility certificate. For a shared outer row, the
union of both forced residuals must fit its capacity; the original separate
inequalities remain necessary but can be weaker.

## Remaining gate

Independent proof review, authoritative census provenance (#2), and the
replayable row-CSP runner (#4) remain pending. The later executable regression
must compare every lemma rejection with the runner where both apply and emit
versioned replay receipts. A timeout or incomplete search remains unresolved.
Only a subsequent reviewed claim update can promote `VDC-WING-PAIR`.

The proof work is based on the governed bootstrap branch in draft PR #1;
it does not require the census-recovery branch in draft PR #7. Issue #5
remains open with its executable acceptance criterion unmet.
