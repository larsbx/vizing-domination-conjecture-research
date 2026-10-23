# Broom family: unbounded unit-capacity Hall deficit with minimum product dominating sets

**Status:** self-contained analytic argument; non-authoritative regression in
`oracles/broom_hall_oracle.py`; claim registry remains `working` pending
repository proof review. This is a falsification of an **intermediate**
block-matching statement, not of Vizing's conjecture.

## Definitions and convention

For dominating sets `A` in `G` and `B` in `H`, fix a vertex partition
`V(G)=disjoint_union P_i`, `V(H)=disjoint_union Q_j`, with each block
assigned to a selected dominator (a fixed lowest-index tie break suffices).
Write `C_ij=P_i x Q_j`. A block is occupied if it meets `D`.
An **any-cell witness** of empty block `C` is an occupied block containing a
vertex of `D` adjacent in `G square H` to at least one cell of `C`.
The witness graph is bipartite between empty and occupied blocks.

The *unit-capacity Hall* assertion would require
`|N(X)| >= |X|` for every set `X` of empty blocks. The *capacitated*
assertion instead asks `|X| <= sum_{Y in N(X)} |D intersect Y|`.

## Proposition (explicit infinite obstruction)

For every integer `t >= 3`, let `G=P_4` on `{0,1,2,3}` with
edges `01,12,23`. Let `H_t` have vertices `0,1,...,2t-1`, with
edges `0i` for `1 <= i <= t`, and `i(t+i)` for `1 <= i < t`.

Set
`A=(1,2)` and `B_t=(0,t+1,...,2t-1)` in the indicated ordering.
The resulting partitions are

- `P_0={0,1,2}`, `P_1={3}`;
- `Q_0={0,1,...,t}`, `Q_i={t+i}` for `1 <= i < t`.

Define the **explicit** product set

```
D_t = {(0,0),(2,t)}
    union {(1,t+i): 1 <= i < t}
    union {(3,i):   1 <= i < t}.
```

Then:

1. `gamma(H_t)=t` and `gamma(G)=2`.
2. `gamma(P_4 square H_t)=|D_t|=2t`; therefore `D_t` is a **minimum**
   dominating set and the pair is Vizing-tight.
3. The empty blocks are exactly `X_t={(1,i): 1 <= i < t}`. Each has
   the sole witness block `(1,0)`. Thus `|X_t|=t-1`,
   `|N(X_t)|=1`, and the unit Hall deficit is `t-2`, unbounded.
4. The occupied witness block has `|D_t intersect C_(1,0)|=t-1`,
   so the **capacitated** inequality for `X_t` holds with equality.
   This family does *not* disprove capacitated Hall.

### Proof of the factor domination numbers

The vertex `t+i` is a pendant adjacent only to `i`, for each
`1<=i<t`. The `t` closed neighborhoods

```
N_H[t+i] = {t+i,i}   (1<=i<t),     N_H[t] = {t,0}
```

are pairwise disjoint. Every dominating set of `H_t` therefore
contains at least one vertex in each, hence has size at least `t`.
The displayed `B_t` has `t` vertices and dominates `H_t`.
Thus `gamma(H_t)=t`.

The path `P_4` has domination number two, witnessed by `A`.

### Proof that D_t dominates the product

For each second-coordinate vertex, the four first-coordinate cells are
covered as follows (horizontal means an edge in `H_t`; vertical means
an edge in `P_4`).

- Second coordinate `0`: `(0,0)` belongs to `D_t`;
  `(1,0)` is vertically adjacent to `(0,0)`;
  `(2,0)` is horizontally adjacent to `(2,t)`;
  `(3,0)` is horizontally adjacent to any `(3,i)`, `1<=i<t`.
- Second coordinate `i` (`1<=i<t`):
  `(0,i)` is covered horizontally by `(0,0)`;
  `(1,i)` horizontally by `(1,t+i)`;
  `(2,i)` vertically by `(3,i)`;
  and `(3,i)` itself is selected.
- Second coordinate `t`: `(0,t)` is covered by `(0,0)`;
  `(1,t)` vertically by `(2,t)`; `(2,t)` itself is selected;
  and `(3,t)` vertically by `(2,t)`.
- Second coordinate `t+i` (`1<=i<t`):
  `(0,t+i)` and `(2,t+i)` are vertically covered by `(1,t+i)`;
  `(1,t+i)` itself is selected; and `(3,t+i)` is horizontally
  covered by `(3,i)`.

Every product vertex is dominated, and `|D_t|=2t`.

### Analytic minimality: endpoint-strip lemma

For **every** dominating set `D` of `P_4 square H`, consider its
restriction to the first two `P_4` rows, and project onto `H`:

```
S_0={h: (0,h) in D or (1,h) in D}.
```

Every cell `(0,h)` must be dominated either horizontally from row 0,
or vertically by `(1,h)`. Hence `S_0` dominates `H`,
so `|D intersect ({0,1} x V(H))| >= |S_0| >= gamma(H)`.

Similarly, dominance of the endpoint row 3 forces at least `gamma(H)`
selected vertices in the disjoint strip `{2,3} x V(H)`.
Therefore

```
gamma(P_4 square H) >= 2 gamma(H)
```

for every finite simple `H`. Taking `H=H_t` and using the explicit
`D_t` proves `gamma(P_4 square H_t)=2t`. No MILP extrapolation is
needed for this infinite family.

### Witness obstruction and the capacity distinction

The product block `(1,i)`, `1<=i<t`, is the singleton cell
`(3,t+i)`, absent from `D_t`. Its only `H_t` neighbor is `i`,
and `(3,i) in D_t`. Its only `P_4` neighbor is row 2, but
`(2,t+i) notin D_t`. Hence the **unique selected dominator** is
`(3,i)`, in block `(1,0)`.

The blocks `(0,i)` are occupied via `(1,t+i)`; `(0,0)`
is occupied via `(0,0),(2,t)`; and `(1,0)` via all the
`(3,i)`. Thus `X_t` is the entire empty-block set and
`N(X_t)={(1,0)}`. As `t` grows, no universal constant `alpha>0`
can satisfy `|N(X)| >= alpha |X|` for **this unit-capacity witness
graph**. On the other hand, `(1,0)` contains exactly `t-1`
selected vertices: it has capacity `t-1=|X_t|`.

## Consequences and non-consequences

- Retire unrestricted empty-block unit matching, even for minimum `D`.
- Retire every fixed positive-ratio *block-count* variant.
- Do **not** infer that capacitated Hall is false; this example satisfies it.
- Do **not** infer that every possible averaging or charging argument is false.
  Sampled distributional claims for `t=3,4,5` are not a uniform theorem
  about all partitions and all minimum product dominating sets.
- Do **not** infer any counterexample to Vizing: this construction is tight.
- The endpoint-strip lower bound is a direct elementary argument, and novelty
  of the bound or the broader `gamma=2` case is **not** asserted here.

## Reproduction

From the repository root:

```sh
python3 -B oracles/broom_hall_oracle.py 12
python3 -B -m unittest conformance.tests.test_broom_hall_examples -v
```

The oracle checks the closed neighborhoods and any-cell witnesses from
the graph definitions, without `networkx`, an ILP solver, or a row-CSP
shortcut. It supplies finite regression evidence; the proof above
supplies the all-`t` argument.
