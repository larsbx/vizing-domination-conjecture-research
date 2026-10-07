# Wing-pair restack — 2026-10-07

Scope: repair the stack of
[PR #8](https://github.com/larsbx/vizing-domination-conjecture-research/pull/8)
after bootstrap #1 merged. `VDC-WING-PAIR` remains `working`, and #8 remains
draft. Issue #5's executable regression gate is still unmet.

## Base and conflict reconciliation

Bootstrap #1 merged into `main` at
`fa07fbfadb7aa344f83617e297e22207dc2d5719`. The two wing-pair commits from
the previously validated head `8487670b05fb24506ae8c2b981792e6a2928cb12`
were rebased onto that main commit. Their patches retain the proof and
regression work; this follow-up adds the dated status record.

Only `README.md` and `conformance/README.md` conflicted. Both now retain
main's recovered-case-base provenance and identity-replay notes alongside
the wing-pair proof and small-factor checks. The merged official estate
pin, completed bootstrap milestones, and conservative case-base status
are retained.

`proof/wing-pair.md`, `conformance/tests/test_wing_pair_examples.py`, and
the October 6 mathematical audit are byte-identical to `8487670`.
Every claim keeps its main-branch status, the repository stays `candidate`,
and Python retains `acceptance_authority = false`.

## Restacked validation

- Complete local conformance: **21 tests pass**, comprising the nine
  wing-pair checks and 12 inherited bootstrap checks.
- The checked-in exhaustive wing-pair comparison covers **22 factor pairs
  and 37,528 selected vertex sets**: every labeled horizontal graph of
  orders one through three with row factor `P4` or `K3`.
- A separate one-off Cartesian-neighbor scan checks the same 37,528 sets,
  finds 17,154 dominating sets, and agrees with the row-residual
  characterization throughout. Across 2,800 size patterns, neither helper
  mode rejects a feasible pattern, every actual dominating wing pair
  survives, and the distinct-outer-row pair sets are unchanged.
- Removing only `o1 == o2` in memory makes the existing distinct-outer-row
  witness regression fail. The checked-in guard and implementation are
  unchanged.
- Official estate pin `--check`, the audit at the declared governance
  revision `5ea47dec8086eab6a1dad6fd239688d20ea89891`, and historical
  case-base replay pass. The replay establishes 16 historical entries
  mapping to three classes, all `n=10, gamma=4`; it does not establish the
  reported 491-entry census.
- Python syntax, TOML parsing, and diff checks pass.

Replay the checked-in conformance suite with:

```sh
python3 -B -m unittest discover -s conformance/tests -p 'test_*.py' -v
python3 -B oracles/replay_casebase.py
```

These are local, non-authoritative validation results. The one-off scan is
additional audit evidence, not a canonical row-CSP implementation or a
versioned lemma-to-runner receipt. No CI success is asserted.

## Review and remaining gate

The exact published head, its clean-checkout verification, and the fresh
review outcome are recorded on PR #8. A code-review result supplies review
evidence; independent proof approval remains a separate requirement.

The canonical row-CSP runner (#4), versioned regression receipts, and
authoritative census provenance (#2) remain outstanding. A surviving local
pair still does not certify global feasibility. The proof statements,
timeout boundary, numerical claim boundary, and issue #5 status are
unchanged. Only a later reviewed claim update can promote `VDC-WING-PAIR`.
