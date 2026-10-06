# Recovered historical case base

These are retained research artifacts recovered on 2026-10-05, supplemented
by two original user attachments on 2026-10-06. The original generator,
command lines and master archive have not been located. The files are
preserved byte for byte; `provenance.json` pins their sizes and SHA-256 checksums.

| File | Role |
| --- | --- |
| `PATCH_43_B_star_4_falsified.md` | Literal named A/B graph6 labels and independent labeled edge lists |
| `patch91_full-1.log` | Fourteen numbered, literal A-class graph6 labels in source order |
| `STRATEGIC_SYNTHESIS_89_93-1.md` | Historical reference to a 491-graph master dataset and the subsequently recovered `aclass_target.json` |
| `aclass_target.json` | Original fourteen A-class records; literal labels and source order exactly match the Patch 91 log |
| `B_star_4_counterexamples.md` | Original A/B labels and labeled edge lists, independently checked against graph6 decoding |

The derived case-base order is A, the fourteen JSON records in source order,
then B. The numbered log independently corroborates the JSON order. The
assembled order is not claimed to be the order of an original combined
16-entry case-base file or the missing 491-entry census.

`oracles/replay_casebase.py` verifies these checksums and sizes, extracts the
literal labels, checks JSON/log agreement, validates the JSON edge counts
and degree sequences, and checks the original note's A/B labeled edge lists.
It validates `n=10` and `gamma=4`, verifies the three pinned isomorphism
classes, and compares the checked-in graph6, JSON and CSV outputs byte for byte.
The JSON `gamma_g2` values, historical product values, solver verdicts and
remaining mathematical prose are not replayed by this identity check and
do not become computed or proved claims.

The ten-file upload inspection and checksums are recorded in
[`artifact-inspection-2026-10-06.json`](../artifact-inspection-2026-10-06.json).
Only these two additional case-base sources were imported from that batch.

The source logs `patch92.log` and `patch93.log` materialized as all-NUL bytes
and were not imported as evidence. Their sizes and checksums are recorded in
the census source-search snapshot. A/B identity comes from the usable Patch 43
record instead.
