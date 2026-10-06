# Thread audit import — 2026-10-05

This note imports the corrected conclusions of the working thread into the repository. It is not itself proof evidence.

## Main conjecture under study

The repository studies Vizing's domination conjecture:

\[
\gamma(G \square H) \geq \gamma(G)\gamma(H).
\]

The active finite target is the \(n=10,\gamma=4\) diagonal square census and the observed strict surplus

\[
s(G)=\gamma(G\square G)-\gamma(G)^2>0.
\]

## Corrected program state

The thread reached the following corrected state:

1. The case base is three isomorphism classes, not 16 distinct graphs.
2. The 491-entry master dataset reportedly contains 470 isomorphism classes.
3. The four simple reverse operators do not cover the census at depth <= 4.
4. The PSC-style operator-closure path should be downgraded to lemma mining.
5. The main route is a direct stratified gold audit.

## Strongest current architecture

The strongest proof architecture from the thread is:

```text
lambda-bound -> structural lemmas -> row-CSP residue
```

The wing-pair lemma is the first structural lemma that appears proof-safe.

## Caution on imported claims

Every imported claim remains `working` until reproduced from checked-in artifacts. In particular:

- The 470-class deduplication is not yet repository evidence.
- The 3-class case-base correction is not yet repository evidence.
- The row-CSP and lambda-kernel implementations are not yet checked in.
- The full finite-census strict-surplus claim is not yet repository evidence.

## Repository action implied by this audit

The immediate project is not to write a paper. It is to build the evidence chain:

1. corpus;
2. deduplication;
3. exact domination fixtures;
4. row-CSP gold audit;
5. structural lemma proof records;
6. stratified 470-class receipts.
