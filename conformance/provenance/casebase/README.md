# Recovered historical case base

These are retained research artifacts recovered on 2026-10-05. The original
generator, command lines and source archive have not been located. The files
are preserved byte for byte; `provenance.json` pins their SHA-256 checksums.

| File | Role |
| --- | --- |
| `PATCH_43_B_star_4_falsified.md` | Literal named A/B graph6 labels and independent labeled edge lists |
| `patch91_full-1.log` | Fourteen numbered, literal A-class graph6 labels in source order |
| `STRATEGIC_SYNTHESIS_89_93-1.md` | Historical reference to a 491-graph master dataset and missing `aclass_target.json` |

The derived case-base order is A, the fourteen numbered log records, then B.
This order makes the recovered fixture explicit; it is not claimed to be the
order of the missing original case-base file or the 491-entry census.

`oracles/replay_casebase.py` verifies these checksums, extracts those literal
labels, validates `n=10` and `gamma=4`, verifies the three pinned isomorphism
classes, and compares the checked-in graph6, JSON and CSV outputs byte for byte.
Historical product values and solver verdicts in these files are not replayed
by this identity check and do not become computed or proved claims.

The source logs `patch92.log` and `patch93.log` materialized as all-NUL bytes
and were not imported as evidence. Their sizes and checksums are recorded in
the census source-search snapshot. A/B identity comes from the usable Patch 43
record instead.
