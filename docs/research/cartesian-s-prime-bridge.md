# Cartesian S-prime bridge

Status: literature-boundary note; no VDC claim promotion.

## Why this note exists

The Vizing program previously described an "FC-kernel" side branch for lemma mining from fiber-capture / residual-footprint patterns. A bounded N6 literature audit in `larsbx/novelty-lab` subsequently identified the unrestricted fiber-capture property with the established Cartesian **S-prime** property.

That changes the research boundary:

- S-prime characterization is prior art.
- Unrestricted S-prime recognition complexity is prior art.
- The Vizing repository does not own this graph class.
- Restricted S-prime consequences may still be useful as imported structural lemmas for domination in Cartesian products.

## Upstream literature decision

The N6 audit records:

- Klavžar–Lipovec–Petkovšek (2002): the no-mixed-embedding/S-prime property and characterization via nontrivial path colorings.
- Klavžar–Peterin (2005): equivalent Hamming-embedding / edge-labeling formulations.
- Hellmuth (2013; later arXiv revision): unrestricted recognition complexity; S-composite recognition NP-complete and S-prime recognition coNP-complete.

The authoritative audit artifacts live in `larsbx/novelty-lab`:

- `docs/literature/n6-cartesian-calculus-2026-10-08.md`
- `docs/literature/n6-prior-art-2026-10-08.md`
- `docs/literature/n6-search-log-2026-10-08.md`
- `docs/literature/n6-references.bib`

This note does not duplicate those proofs or searches.

## Allowed VDC use

A Cartesian S-prime theorem may enter this repository only as an **imported structural fact** supporting a domination-specific claim.

Examples of admissible downstream questions:

1. Does S-primality rule out a row-state decomposition used by the VDC CSP?
2. Can a known S-prime certificate imply a residual-capacity obstruction for a specific VDC row pattern?
3. Does a restricted graph class in the n=10, gamma=4 census admit a cheaper exact S-prime certificate that is useful as a filter?

Any such result must be written as:

[
	ext{imported S-prime theorem} + 	ext{VDC hypotheses} Longrightarrow 	ext{new VDC consequence}.
]

## Not allowed

Do not:

- rename S-prime as a newly discovered VDC property;
- claim unrestricted S-prime characterization or recognition as open;
- use a few successful mixed-embedding tests as a proof of S-primality;
- infer domination surplus from S-primality without a separate argument;
- merge S-prime experiments into the canonical VDC acceptance boundary unless they are needed by, and replayable within, an accepted VDC theorem path.

## First useful bridge target

The most promising bounded target is not general recognition. It is:

> For a declared restricted family of row-support or residual-footprint graphs arising in the row-CSP audit, determine whether an imported S-prime certificate yields a proof-safe infeasibility filter.

Acceptance for such a bridge result requires:

- a precise restricted family;
- an external theorem locator or independently proved restricted lemma;
- an exact transformation from the S-prime certificate to the row-CSP obstruction;
- regression tests on positive and negative examples;
- no claim that the bridge extends beyond the stated family.

## Relationship to issue #10

Issue #10 remains the coordination issue for the bridge. It should close only when either:

- a concrete imported S-prime lemma is consumed by a VDC proof record, or
- the branch is explicitly retired as unhelpful for the current finite target.
