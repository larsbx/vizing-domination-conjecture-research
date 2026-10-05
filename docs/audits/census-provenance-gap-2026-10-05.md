# Census provenance recovery — 2026-10-05

**Outcome: the authoritative ordered 491-entry corpus has not been located.**
The 491 -> 470 result and the identities of its 21 duplicate entries cannot be
replayed. No `conformance/corpus/g4_n10_graph6.txt` has been created, and no
missing census entry has been generated or inferred from the reported counts.
[Issue #2](https://github.com/larsbx/vizing-domination-conjecture-research/issues/2)
remains blocked. `VDC-CASEBASE-3` remains `working`.

## GitHub recovery scope

The target repository was inspected at:

- `main`: `c6e88d9fd5068832f85fbe708f9cbab6004e5721`;
- `bootstrap/estate-research-program` / PR #1 head:
  `44990a294dfa39067d54d3915ba7735eba6422fd`;
- PR #1 synthetic merge ref:
  `f175d0a7ef846ec01154a6501b0d9e7d051404dd`.

The target has two branch heads, no tag refs, no releases and zero workflow
runs. Its 14 reachable commits (including the synthetic merge) have 13 unique
blobs: the initial README and bootstrap research shell. None is a corpus,
case-base source list, census generator or deduplication output. PR #1 and
issue #2 had no discussion comments or attachment pointers at inspection.
PR #1 remains a draft; this change is stacked on its bootstrap branch.

The history search was expanded beyond the user's earlier bounded search of
default branches. Thirteen public mathematics repositories, including this
one, were mirrored with all advertised branches, tags and pull refs. The
search covered 3,097 reachable commits and 9,264 unique blobs. It searched
exact A/B labels, Vizing/graph6/corpus pointer terms, 491/470 co-occurrences,
graph6-shaped records and likely archive paths. Seven compressed blobs were
inspected after decompression. No census source was found. Numeric matches
in unrelated data and a generated C string `ImageModL` were false positives.

Release listings for the sixteen related repositories were empty. Four
accessible private repositories could not be cloned without shell
credentials; 29 unique ref-tip trees were inspected through GitHub metadata
for corpus/archive filenames, with no matching paths. Their blob contents and
historical trees were not exhaustively searched. The repository-wide Actions
artifact-list endpoint was unavailable through the connector; the target's
supported workflow-run listing returned zero runs, so there was no run from
which to retrieve an artifact. These limitations are not evidence that an
artifact never existed in deleted history or an unavailable attachment.

The exact public ref snapshots, search patterns, hit dispositions, release
counts, archive checks and access limitations are stored in
[`census-source-search-2026-10-05.json`](../../conformance/provenance/census-source-search-2026-10-05.json).
This is a bounded recovery record, not a proof of global nonexistence.

## Retained artifact recovery

The retained artifact inventory for 2026-04-24 through 2026-04-29 contained 122
items and was fully paginated. It includes usable Patch 43, Patch 91 and
Patches 89-93 synthesis records. Searches did not locate the named archives:

- `graph_ring_vizing_research_master_bundle.tar.gz`;
- `graph_ring_complete_research_bundle_v3.tar`;
- `vizing_patches_43_to_63_bundle.tar.gz`.

The synthesis mentions a 491-graph master dataset but supplies no full list,
source checksum or generation command. It also names `aclass_target.json`,
which was not located. `g4_n10_pairs.csv` contains 21 pairwise result rows over
six sample indices, not 491 graph6 entries. `classB_g4.json` is a separate
30-graph sample across several orders. Neither can substitute for the census.

Usable original bytes, their checksums and their explicit limitations are
preserved in [`casebase/`](../../conformance/provenance/casebase/README.md).
Two later logs materialized as NUL-only bytes and were excluded from evidence.

## Supported partial result

Patch 43 supplies the literal A/B labels. The Patch 91 log supplies all fourteen
numbered A-class labels. Extracting those observations gives a **separate
16-entry historical case-base fixture**, without synthesizing graph entries.

Exact canonicalization reproduces 16 -> 3 with 13 collapsed entries in that
fixture. All sixteen recovered graphs have order 10 and exact domination
number 4. These 13 collapses are not identified as a subset of the census's
reported 21 duplicates: membership and original row positions in the missing
census have not been recovered.

| Role | Observed representative | Versioned canonical graph6 | Fixture entry IDs |
| --- | --- | --- | --- |
| A | ``I?r@`aii_`` | `IK??xXLb_` | 1 |
| A-class | ``I?r@`_iy_`` | ``IGa?x`PBw`` | 2-15 |
| B | ``I?r@`bgIo`` | `IIa?W[pKg` | 16 |

The JSON fixture pins these three classes with the `degree-ir-graph6-v1`
algorithm. JSON/CSV receipts retain each observed graph6 record, its fixture
line number, canonical class, explicit vertex-permutation witness and first
duplicate source entry. These are identity receipts only. They establish no
product domination values, strict-square-surplus result or census coverage.

## Replay and algorithm boundary

Requires Python 3.11 or newer; no packages, network access or external tools.
From the repository root:

```bash
python3 oracles/replay_casebase.py
python3 -m unittest discover -s conformance/tests -v
```

The replay checks original bytes, extracted labels, pinned classes, the
`working` claim gate and all three derived files. To regenerate those files
after inspecting a mismatch, run `python3 oracles/replay_casebase.py --write`.

The exact oracle starts with ordered degree cells, performs ordered equitable
refinement, recursively individualizes vertices and minimizes the resulting
graph6 encodings. It skips only branches equivalent under a twin transposition
that fixes every other vertex. Isomorphic inputs have corresponding search
trees and equal minima; equal minima encode identical relabeled graphs.
Keys include an algorithm version and the full canonical encoding. Degree
sequences or hashes are not used to decide isomorphism. Keys need not match
nauty's labeling. The oracle supports simple undirected graph6 inputs of order
at most ten and rejects malformed payload lengths and nonzero padding.
The encoding follows [McKay's graph6 specification](https://users.cecs.anu.edu.au/~bdm/data/formats.txt).

Cross-checks use a separate degree-preserving bijection search: all 1,100
labeled simple graphs through order five, all ordered pairs of the sixteen
case-base entries, and 400 seeded relabelings of the recovered order-ten
graphs agree. Tests also distinguish regular graphs with the same initial
refinement, validate the independently recorded A edge list, reject provenance
and pin tampering, and reject the case base when 491/470/21 are requested.
The code is a named `oracles/` implementation; acceptance authority and the
estate governance pin are unchanged.

## Precise remaining provenance gap

The missing input is the **original ordered 491 graph6 records**, with an
authoritative source locator and checksum or preserved original bytes. The
source must identify its scope: generation or selection method, graph filters,
options/seed if applicable, and any aggregation or relabeling before the 491
rows were counted. Those details cannot be recovered from `n=10`, `gamma=4`
and the remembered counts alone.

Also missing are the original case-base file, its relationship to census row
IDs, and the reported original duplicate mapping. The recovered logs close
the identity portion of the case-base gap, but do not establish census
membership. A new enumeration with the same counts would not recover the
original duplicate rows or provenance.

Once the source is recovered and recorded, this deterministic path can
generate the full mapping (the command currently fails because the source is
absent):

```bash
python3 oracles/canonical_graph6.py conformance/corpus/g4_n10_graph6.txt \
  --order 10 --gamma 4 \
  --expected-entries 491 --expected-classes 470 --expected-duplicates 21 \
  --json conformance/receipts/g4_n10_dedup.json \
  --csv conformance/receipts/g4_n10_dedup.csv
```

The count checks run before outputs are written. Count agreement alone is
insufficient: original source provenance, case-base membership, explicit
duplicate rows, independent isomorphism agreement and clean-checkout replay
must also land before promoting `VDC-CASEBASE-3` under issue #2's gate.
