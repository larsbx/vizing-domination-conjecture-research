# Independent case-base identity and provenance audit — 2026-10-06

## Result and integration state

The canonical-isomorphism path at PR #7 head
`980938f22fe4c847e42ad245e4310f5bc10e5615` reproduces the separately recovered
historical fixture: **16 entries, three classes, 13 collapsed entries**, all
of order ten and exact domination number four. Both identity receipts replay
byte for byte. The authoritative 491-entry census remains absent; the
491/470/21 result, original duplicate rows and census membership have not
been replayed. `VDC-CASEBASE-3` remains `working`.

At this audit's initial state check, PR #7 had already merged into
`bootstrap/estate-research-program` as
`6a23cd226059f3791f8cd74ec8c6989d657071cf`. That merge has the same tree as the
audited head. Bootstrap PR #1 remains a draft targeting `main`. PR #7 is
closed, so there is no open #7 to restack. This follow-up targets the bootstrap
branch and does not advance or merge #1.

GitHub records a completed independent Codex code review at `980938f` on
2026-10-06 at 10:08:18 UTC and the review bot's positive PR reaction at
10:08:22 UTC. No inline review findings were recorded. The completion is in
the [review summary](https://github.com/larsbx/vizing-domination-conjecture-research/pull/7#issuecomment-6013993498),
rather than a submitted approval review. That review predates the fixes below;
the follow-up needs its own review.

## Canonicalization and permutation convention

The ordered degree partition is preserved by every graph isomorphism.
Neighbor-count signatures into ordered cells are preserved as well, so
equitable refinement and selection of the first nonsingleton cell commute
with relabeling. Individualization explores all vertices except the branches
justified by the twin test. Isomorphic inputs consequently have the same set
of leaf encodings; equal leaf encodings explicitly witness isomorphic inputs.

For the twin test, distinct vertices `u` and `v` have equal neighborhoods
outside `{u,v}`. Their transposition preserves all other edges, preserves
the unordered edge `{u,v}` and fixes all remaining vertices. This holds both
when the twins are adjacent and when they are nonadjacent. Both are in the
selected cell, so the swap also fixes earlier individualized singletons and
stabilizes every ordered cell. Refinement and descendant individualization
therefore pair the two branches with identical leaf encodings. Keeping one
representative is sound. The witness remains deterministic; it is not claimed
to be the smallest permutation among all automorphisms.

The graph6 bit order and big-endian six-bit packing agree with
[McKay's specification](https://users.cecs.anu.edu.au/~bdm/data/formats.txt).
The specification's five-vertex example is independently pinned as `DQc`.
For `canonical_permutation = p`, **`p[new_vertex] = original_vertex`**:
canonical edge `(i,j)` is original edge `(p[i],p[j])`. The inverse map sends
original labels to canonical labels. A regression uses a permutation that
differs from its inverse. These versioned keys are not claimed to equal
nauty keys or the minimum over all vertex permutations.

## Original bytes, source order and receipt scope

The two original user attachments were independently compared with the
retained repository copies, with exact byte equality:

| Original attachment | Bytes | SHA-256 |
| --- | ---: | --- |
| `aclass_target.json` | 2592 | `f3b48949e2b02411d9fc926da7a157e21ce7c8538802ce9d921e3d819a5b7d59` |
| `B_star_4_counterexamples.md` | 4948 | `995fa433c0ae727bc0cfa9a1b144e8cb85257850cfbba630d93340613aa94c06` |

The numbered log agrees with all fourteen JSON labels in their original order.
The assembled fixture order is A, those fourteen records, then B. Its entry
IDs and `source_line` values refer to this assembled fixture, not original
JSON line numbers, log line numbers or census positions. Class rows may be
sorted by canonical key; their entry memberships retain source order and
duplicates refer to the first observed member.

All sixteen JSON receipt permutations were checked as bijections, and their
edge mappings were checked independently of the encoder. CSV graph labels,
class IDs and witness permutations agree with the JSON rows. The receipts
remain identity evidence only: no historical `gamma_g2`, product domination,
surplus, coverage or census-membership assertion is certified.

## Findings and repairs

1. Replay checked canonical encodings and membership but ignored the declared
   `iso_class_id`, role uniqueness and source representative associated with
   each role. It accepted a wrong ID or duplicate role. Replay now requires
   exactly one A, A-class and B pin, their observed representatives and their
   complete versioned IDs.
2. Replay ignored the declared historical kind, schema and blocked-promotion
   metadata. It accepted a pin marked as an authoritative census or as
   computed evidence. It now validates historical scope and the existing
   blocked status, and requires exactly one `VDC-CASEBASE-3` registry record
   before enforcing its `working` state.
3. The generic importer's `splitlines()` silently recognized vertical tabs,
   form feeds and ASCII record separators as line endings. It now rejects
   control bytes other than CR/LF before splitting, preventing those invalid
   bytes from being discarded during entry and source-line assignment.

Every added rejection precedes derived-file writes. The fixes leave all
canonical keys, source files, class pins, graph6 fixture, JSON/CSV receipts
and claim states unchanged.

## Validation

An isolated GitHub clone was checked out at the exact PR #7 head. All original
12 conformance tests passed under Python 3.12.14; replay and `--write` left
the checkout unchanged. The bootstrap merge's tree was compared with that
head and was identical.

The revised suite has 19 tests. It retains the independent bijection oracle
over all 1,100 labeled graphs through order five, all ordered case-base
pairs and 400 seeded case-base relabelings. Added checks cover true and false
twins at order ten, 40 relabelings of that fixture, the specification example,
permutation direction, receipt witnesses, invalid record separators, and
identity/scope/registry tampering before writes. The existing full-census
count gate still rejects the historical fixture without writing reports.

```bash
python3 -m unittest discover -s conformance/tests -v
python3 oracles/replay_casebase.py
python3 oracles/replay_casebase.py --write
git diff --exit-code
```

This audit adds oracle conformance evidence. It does not promote acceptance
authority, resolve the estate pin or close issue #2's corpus-provenance gate.

## Restack and review follow-up — 2026-10-07 UTC

Bootstrap #1 merged on 2026-10-06 at 23:56:15 UTC as
`fa07fbfadb7aa344f83617e297e22207dc2d5719`. The follow-up was rebased onto
that main commit with a guarded update. The bootstrap's corrected estate pin
and roadmap were preserved. Every tracked provenance, fixture and receipt
file, together with the claim registry, remained byte-identical to the
original follow-up head `4f8e8a5c526a73ffdc0c21ddecadf17815a1aeff`.

The independent review of restacked head `3fc230dbf39355958b2ce1c3235139076288cf18`
identified a P2: Python equality accepted JSON `true` as schema version `1`.
Both provenance and class-pin checks now require an actual integer type as
well as the value one. Boolean and floating-point versions are rejected in
both documents, with all three derived artifacts unchanged even when write
mode is requested. The suite retains 19 tests with these additional rejection
cases. Published-head replay and fresh review evidence are attached to PR #9.

## Current-main reconciliation — 2026-10-07

Main advanced through the wing-pair PR #8 merge to
`5aaa62745b181dfcba0abd7c6cfbe4cf9eada39f`. PR #9 was rebased from
`c2da0e965c730d198679a362afd2e32fa4ef2f04` onto that commit. The only
conflict was in `conformance/README.md`; it now retains both this identity
audit's replay note and main's corpus-independent wing-pair checks.

The two oracle files and the 19 identity/provenance tests are byte-identical
to the previously reviewed `c2da0e9` head. Current main's wing-pair proof,
nine wing-pair tests, estate manifest, roadmap and complete claim registry
are preserved byte for byte. All 13 tracked provenance, fixture and receipt
files are byte-identical to current main, `c2da0e9` and the original audited
head `4f8e8a5c526a73ffdc0c21ddecadf17815a1aeff`.

The combined local suite passes **28 tests**. Both receipt replay modes pass;
regeneration leaves the checkout unchanged. The official estate pin check
and layout audit pass at the declared governance revision
`5ea47dec8086eab6a1dad6fd239688d20ea89891`. Python syntax, TOML parsing and
diff checks pass. The live review check still shows only the resolved schema
P2 thread; the existing completed code review covers the unchanged oracle
code and identity tests. Published-head checks are recorded on PR #9.

The supported identity result remains the historical **16 -> 3**, with 13
collapsed entries and all entries of order ten and domination number four.
`VDC-CASEBASE-3` and all other working claims retain their current-main
statuses. The authoritative census, 491/470/21 mapping, census membership
and product claims remain unreplayed. The repository stays `candidate`
with `acceptance_authority = false`. No Actions CI run is claimed.
