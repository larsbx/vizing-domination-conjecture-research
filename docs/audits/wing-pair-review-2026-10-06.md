# Wing-pair mathematical and conformance audit — 2026-10-06

Scope: [draft PR #8](https://github.com/larsbx/vizing-domination-conjecture-research/pull/8),
reviewing [`proof/wing-pair.md`](../../proof/wing-pair.md) separately from the
test implementation. The original proof and helper were inspected at
`350a286ab9877b82dde25789fc1fa9bdb69e7c9a`; Section 4.6 and the explicit
regression are added by this follow-up. This is an audit record, not a PR
approval or a claim-promotion decision.

## Exact-head replay

The GitHub source and local Git object agree: the original helper already
uses `shared_capacity and o1 == o2` before testing union capacity. The
original complete conformance suite passes all eight tests. The reported
unguarded condition is unsound, but it is not the condition in that head.

For horizontal edges `0-1, 0-2`, row factor `P4`, wings `(1, 2)`, and sizes
`(1, 1, 0, 2)`, the witness `({0}, {0}, empty, {1, 2})` dominates the
product by direct Cartesian-neighborhood coverage. Its forced residuals
are empty and `{1, 2}` in distinct outer rows 0 and 3. All three possible
wing pairs survive both modes of the original helper. Removing only
`o1 == o2` in an in-memory negative control rejects all three pairs.
The new explicit regression fails under that mutation and passes with the
guard retained. The exhaustive comparison additionally requires the two
modes to return identical pair sets for every distinct-row size pattern.

## Mathematical review

The argument was checked from Cartesian adjacency and set inclusions,
without using the helper's result as a premise.

| Proof component | Review finding |
| --- | --- |
| Definitions and (H) | Closed neighborhoods include selected vertices and have empty union for an empty state. The two wings are distinct, adjacent, and degree two; both outer vertices lie outside the wing pair. No outer-degree or connectivity assumption is needed. |
| Proposition 1 | A vertex not covered horizontally can only be covered from an adjacent row at the same horizontal coordinate. This proves both directions of the residual characterization. |
| Lemma 2 | After removing horizontal coverage and the partner-wing state, the sole remaining neighboring row forces each residual coordinate into its designated outer state. Cardinalities give (3). |
| Corollary 3 | Any feasible exact pattern supplies one simultaneous wing pair satisfying both inequalities. Empty pair set therefore implies infeasibility. The required quantifier is every pair, not separate minima or one failed pair. |
| Distinct outer rows | Each forced residual can be padded independently to its own prescribed outer size, since each size lies between zero and the horizontal order. This extends only the two wing constraints. |
| Shared outer row | Both forced sets must lie in one outer state, so their union must fit that state's capacity. Conversely, including the union and padding proves sufficiency for the two wing constraints of a fixed pair. |
| Examples and audit scope | Sections 4.1–4.6 agree with these deductions and direct product coverage. Local survival remains insufficient for global domination. Exact-pattern rejection does not close a target-size search or establish a census claim. |

No mathematical defect was found in the stated proposition, lemma,
corollary, or fixed-pair extension arguments. In particular, (4) cannot be
applied to distinct outer rows. Section 4.6 records the explicit witness
showing why. The timeout and exhaustive-search boundary in Section 5 is
appropriate: incomplete enumeration cannot certify pair-set emptiness.

## Validation and remaining gates

```sh
python3 -B -m unittest discover -s conformance/tests -p 'test_*.py' -v
```

The complete suite passes nine tests. The exhaustive direct-product
comparison retains 22 factor pairs and 37,528 selected vertex sets:
all labeled horizontal graphs of orders one through three, paired with
`P4` and a triangle. These counts describe only that small comparison.
They are not authoritative census coverage or canonical row-CSP receipts.

The original head has no attached pull-request workflow run, and the
branch has no workflow configuration. Validation here is local; no CI
success is claimed. Claim statuses and `acceptance_authority = false`
remain unchanged.

At inspection, #8 has no submitted PR reviews or inline review threads.
This separate mathematical audit supplies review evidence, while the
repository's independent review/approval and promotion gate remains open.
The stack base is still the open draft
[bootstrap PR #1](https://github.com/larsbx/vizing-domination-conjecture-research/pull/1).
The authoritative corpus
[#2](https://github.com/larsbx/vizing-domination-conjecture-research/issues/2),
canonical row-CSP runner
[#4](https://github.com/larsbx/vizing-domination-conjecture-research/issues/4),
and versioned lemma-to-runner regression required by
[#5](https://github.com/larsbx/vizing-domination-conjecture-research/issues/5)
remain unmet. PR #8 stays draft, `VDC-WING-PAIR` stays `working`, and
issue #5 remains open.
