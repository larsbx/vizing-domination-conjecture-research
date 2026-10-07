# Conformance

Checked fixtures, accepted/rejected examples, malformed inputs, and replay receipts belong here.

Planned subdirectories:

```text
conformance/
  corpus/          graph6 datasets and provenance notes
  fixtures/        small known graphs and expected domination/product values
  receipts/        machine-readable audit receipts
  malformed/       parser and validation failure cases
```

A result becomes repository evidence only when its fixture or receipt is stored here and replayed by the kernel or a named oracle.

## Recovered identity evidence

`fixtures/casebase_graph6.txt` is a literal historical case-base extraction,
not the missing census. `provenance/casebase/` preserves the usable source
records and their checksums, including the original `aclass_target.json`
recovered in the 2026-10-06 upload. Replay its pinned 16 -> 3 identity result with
`python3 oracles/replay_casebase.py`. The JSON/CSV identity receipts do not
certify historical product values or the reported 491 -> 470 census result.

The full source gap and bounded search scope are recorded in
[`census-provenance-gap-2026-10-05.md`](../docs/audits/census-provenance-gap-2026-10-05.md).

The independent [identity and provenance audit](../docs/audits/casebase-identity-review-2026-10-06.md)
records the twin-pruning justification, permutation direction, original-byte
comparison and additional fail-closed identity/scope checks. Run the current
suite with `python3 -m unittest discover -s conformance/tests -v`.

## Corpus-independent wing-pair checks

`tests/test_wing_pair_examples.py` checks the examples in
[`proof/wing-pair.md`](../proof/wing-pair.md). Its independent domination
oracle builds Cartesian-product neighborhoods directly and enumerates
selected vertex sets, without using a row-CSP solver. The exhaustive small
comparison covers all labeled horizontal graphs of orders one through three
with a four-vertex path or a triangle as the row factor. It checks both the
original necessary inequalities and the shared-outer-row union condition.
For distinct outer rows, enabling `shared_capacity` must leave every pair
set unchanged. The explicit regression uses horizontal edges `0-1, 0-2`,
row factor `P4`, wings `(1, 2)`, and sizes `(1, 1, 0, 2)`. Its witness
`({0}, {0}, empty, {1, 2})` dominates the product; the second forced
residual belongs to row 3 and cannot consume row 0's capacity.

```sh
python3 -B -m unittest discover -s conformance/tests -p 'test_*.py' -v
```

These checks have no executable acceptance authority. They are not corpus
fixtures, do not reproduce historical gold audits, and do not satisfy issue
#5's pending regression against the canonical row-CSP runner. No claim is
promoted by passing them.
