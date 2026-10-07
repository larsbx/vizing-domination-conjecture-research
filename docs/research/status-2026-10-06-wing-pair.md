# Wing-pair progress — 2026-10-06

Scope: the corpus-independent portion of
[issue #5](https://github.com/larsbx/vizing-domination-conjecture-research/issues/5).

This page records the October 6 snapshot. The
[October 7 follow-up](status-2026-10-07-wing-pair-restack.md) records the
merged bootstrap and restack onto `main`.

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
  failure when an extra neighbor is ignored, and a feasible distinct-outer
  witness that would be rejected by an unguarded union-capacity check.
- `conformance/tests/test_wing_pair_examples.py` checks those examples and
  compares the necessary tests with a direct product-domination oracle on
  all labeled horizontal factors through order three and two row factors.
  This is an independent small check, not the canonical row-CSP runner.

Validation: the complete conformance suite passes all nine tests. The
explicit regression uses horizontal edges `0-1, 0-2`, row factor `P4`,
wings `(1, 2)`, and sizes `(1, 1, 0, 2)`. Its dominating witness
`({0}, {0}, empty, {1, 2})` survives both helper modes. The exhaustive
comparison also checks equality of both pair sets for distinct outer rows.
The exhaustive direct-product comparison examines 37,528 selected vertex
sets across 22 factor pairs.

A separate [mathematical audit](../audits/wing-pair-review-2026-10-06.md)
found no defect in the stated proof. Exact-head inspection at `350a286`
also confirmed that `o1 == o2` was already present in the helper and that
the original eight tests passed. An in-memory negative control removing
that guard rejects the feasible regression, confirming the need for the
guard. The audit supplies evidence but does not grant independent PR
approval or satisfy the outstanding promotion gate. No CI result is claimed.

Replay the complete local suite with:

```sh
python3 -B -m unittest discover -s conformance/tests -p 'test_*.py' -v
```

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
