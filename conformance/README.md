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
