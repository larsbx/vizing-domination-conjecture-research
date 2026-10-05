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
records and their checksums. Replay its pinned 16 -> 3 identity result with
`python3 oracles/replay_casebase.py`. The JSON/CSV identity receipts do not
certify historical product values or the reported 491 -> 470 census result.

The full source gap and bounded search scope are recorded in
[`census-provenance-gap-2026-10-05.md`](../docs/audits/census-provenance-gap-2026-10-05.md).
