# Wing-pair residual-capacity lemma

Claim: `VDC-WING-PAIR`. Status: **working — repository proof draft**.

This record supplies the corpus-independent statement, proof, and examples
requested by [issue #5](https://github.com/larsbx/vizing-domination-conjecture-research/issues/5).
Claim promotion and agreement with the canonical row-CSP gold audit remain
pending. The authoritative census and that runner are unavailable. The small
examples below are mathematical examples, not recovered census entries.

## 1. Standing definitions and hypotheses

Let $G$ and $H$ be finite simple undirected graphs, and write
$U=V(G)$, $n=|U|\geq 1$. The Cartesian product has vertex set
$U\times V(H)$; two vertices are adjacent exactly when one coordinate
agrees and the other coordinates are adjacent in the corresponding factor.
A set $D$ dominates the product if every product vertex belongs to $D$
or is adjacent to a member of $D$.

For $S\subseteq U$, define its closed neighborhood and residual by

$$
N_G[S]=\bigcup_{g\in S}\bigl(\{g\}\cup N_G(g)\bigr),
\qquad R_G(S)=U\setminus N_G[S].
$$

In particular, $N_G[\varnothing]=\varnothing$ and
$R_G(\varnothing)=U$. For each row $h\in V(H)$, put

$$
S_h=\{g\in U:(g,h)\in D\}.
$$

A **size pattern** is a prescribed vector
$\mathbf a=(a_h)_{h\in V(H)}$ with integer entries
$0\leq a_h\leq n$. It is feasible if some dominating set has
$|S_h|=a_h$ in every row. Its total size is exactly $\sum_h a_h$.

Fix distinct vertices $w_1,w_2\in V(H)$ such that

$$
N_H(w_1)=\{w_2,o_1\},\qquad
N_H(w_2)=\{w_1,o_2\},\qquad
o_i\notin\{w_1,w_2\}. \tag{H}
$$

Thus the wings are adjacent and each has degree exactly two. The outer
vertices $o_1,o_2$ may coincide; no degree condition is imposed on them.
Neither graph needs to be connected. The wings belong to the **row factor
$H$**. Specializing to $H=G$ gives the square-product setting, but
neither $n=10$ nor $\gamma(G)=4$ is a hypothesis.

## 2. Product-domination characterization

**Proposition 1.** A row family $(S_h)_{h\in V(H)}$ defines a
dominating set in $G\square H$ if and only if

$$
R_G(S_h)\subseteq\bigcup_{k\in N_H(h)}S_k
\quad\text{for every }h\in V(H). \tag{1}
$$

**Proof.** Fix $(g,h)$. It is covered by a selected vertex in its
own row exactly when $g\in N_G[S_h]$: this includes selection of
$(g,h)$ itself. Otherwise $g\in R_G(S_h)$, and a selected vertex
outside that row can cover it only at $(g,k)$, with $k\in N_H(h)$.
Such a vertex exists exactly when $g$ belongs to the union on the
right of (1). Checking every vertex proves both directions. $\square$

This is a set-theoretic characterization of domination; its proof uses
no solver, row-state representation, search budget, or receipt.

## 3. Wing-pair lemma and rejection criterion

For prospective wing states $X,Y\subseteq U$, put

$$
F_1(X,Y)=R_G(X)\setminus Y,\qquad
F_2(X,Y)=R_G(Y)\setminus X.
$$

**Lemma 2 (wing-pair residual capacity).** Under (H), every dominating
set with size pattern $\mathbf a$, wing states
$X=S_{w_1}$, $Y=S_{w_2}$, satisfies

$$
F_1(X,Y)\subseteq S_{o_1},\qquad
F_2(X,Y)\subseteq S_{o_2}, \tag{2}
$$

and hence

$$
|F_1(X,Y)|\leq a_{o_1},\qquad
|F_2(X,Y)|\leq a_{o_2}. \tag{3}
$$

**Proof.** If $g\in F_1(X,Y)$, then $(g,w_1)$ is not
covered within its row, since $g\notin N_G[X]$, and is not covered
from the partner wing, since $g\notin Y$. By (H), the only remaining
neighboring row is $o_1$. Domination therefore forces
$(g,o_1)\in D$, or $g\in S_{o_1}$. This proves the first
inclusion. Interchanging the two wings proves the second. Taking
cardinalities and using the prescribed outer-row sizes gives (3).
$\square$

Define the simultaneous admissible-pair set

$$
\mathcal P(\mathbf a)=
\left\{(X,Y):
\begin{array}{l}
X,Y\subseteq U,\quad |X|=a_{w_1},\quad |Y|=a_{w_2},\\
|F_1(X,Y)|\leq a_{o_1},\quad |F_2(X,Y)|\leq a_{o_2}
\end{array}\right\}.
$$

**Corollary 3 (sound pattern rejection).** If
$\mathcal P(\mathbf a)=\varnothing$, then $\mathbf a$ is
infeasible in $G\square H$.

**Proof.** A dominating set with this pattern would supply its actual
wing states $(S_{w_1},S_{w_2})$. Lemma 2 puts that pair in
$\mathcal P(\mathbf a)$, contradicting emptiness. $\square$

Equivalently, rejection requires that **every** pair of the prescribed
wing sizes violate **at least one** inequality. One failed pair is
insufficient. Minimizing the two residual sizes separately is also
insufficient: the same pair must satisfy both inequalities.

For distinct outer rows, (3) is sufficient to extend a **fixed pair** to
states of the prescribed sizes satisfying just the two wing-row
constraints. Indeed, choose $S_{o_i}$ containing $F_i(X,Y)$
and pad it to size $a_{o_i}$, which is possible since
$|F_i|\leq a_{o_i}\leq n$. This says nothing about domination
of the outer rows or any other rows. Consequently,
$\mathcal P(\mathbf a)\ne\varnothing$ is a survivor verdict,
not a feasibility certificate.

### Shared outer row

If $o_1=o_2=o$, (2) forces the stronger necessary inequality

$$
|F_1(X,Y)\cup F_2(X,Y)|\leq a_o. \tag{4}
$$

For a fixed pair, (4) is necessary and sufficient to choose a single
outer-row state of size $a_o$ satisfying the two wing constraints:
include the union and pad. The original inequalities (3) remain sound
when the outer row is shared, but they may miss this competition for
capacity. Neither version certifies a global solution on survival.
Equation (4) follows from (2); executable integration and regression
remain pending.

### Relation to an audit target

Rejecting one exact pattern excludes only sets with that pattern. To
deduce absence of all dominating sets of size at most $T$, every
pattern with $\sum_h a_h\leq T$ must be excluded by sound arguments.
A wing-pair rejection alone makes no numerical strict-surplus claim
for a graph or a census.

## 4. Applicability and failure examples

### 4.1 Rejection after the scalar bounds pass

Let the horizontal factor be the path $x_0-x_1-x_2-x_3$, and let
the row factor be the six-cycle
$o_1-w_1-w_2-o_2-r_2-r_1-o_1$. In that row order, prescribe sizes

$$
(a_{o_1},a_{w_1},a_{w_2},a_{o_2},a_{r_2},a_{r_1})=(0,1,1,0,4,4).
$$

The minimum residual sizes of horizontal states of sizes zero, one,
and four are respectively four, one, and zero. Thus the scalar bound
$\min_{|S|=a_h}|R_G(S)|\leq\sum_{k\in N_H(h)}a_k$
passes in every row: the two wings give $1\leq 1$, the empty
outer rows give $4\leq 5$, and the full rows give $0\leq 4$.
Nevertheless,
$\mathcal P(\mathbf a)$ is empty:

- An endpoint singleton has residual size two, which cannot fit in the
  partner singleton when the outer capacity is zero.
- If $X=\{x_1\}$, its residual is $\{x_3\}$, so
  $Y=\{x_3\}$ is forced. Then
  $R_G(Y)\setminus X=\{x_0\}$, violating the second zero capacity.
- If $X=\{x_2\}$, $Y=\{x_0\}$ is forced, and
  $R_G(Y)\setminus X=\{x_3\}$, again violating it.

These cases exhaust all possible $X$; Corollary 3 rejects the pattern.
Each inequality separately can be satisfied: take
$X=\{x_1\},Y=\{x_3\}$ for the first, and swap these states
for the second. Thus separate minima do not replace the simultaneous test.

### 4.2 A feasible pattern and why one failed pair is insufficient

Let the horizontal factor again be the four-vertex path and let the row
factor be the path $o_1-w_1-w_2-o_2$. Prescribe size one in every
row. The row states

$$
S_{o_1}=\{x_1\},\quad S_{w_1}=\{x_3\},\quad
S_{w_2}=\{x_0\},\quad S_{o_2}=\{x_2\}
$$

give residuals, in row order,
$\{x_3\},\{x_0,x_1\},\{x_2,x_3\},\{x_0\}$.
Each is covered by its neighboring row states, so Proposition 1 proves
domination. Both wing capacities are attained with equality.

The alternative pair $X=Y=\{x_0\}$ fails (3), since
$|R_G(X)\setminus Y|=2>1$. Rejecting the pattern because of
that single pair would discard the explicit dominating set above.

### 4.3 Survival need not imply global feasibility

Let $G$ have one vertex $x$, and let $H$ be the path
$h_0-h_1-h_2-h_3-h_4-h_5$. Take wings $h_2,h_3$, each
with state $\{x\}$, and prescribe zero size in every other row.
Both wing residuals are empty, so (3) passes. But the unique set with
this size pattern leaves $(x,h_0)$ and $(x,h_5)$ undominated.
The pattern is infeasible despite surviving the local filter.

### 4.4 Shared outer capacity

Let $G$ be the path $x_0-x_1-x_2-x_3$, and let
$H$ be the triangle on $w_1,w_2,o$. Fix
$X=\{x_1\}$, $Y=\{x_2\}$, and $a_o=1$.
Then $F_1=\{x_3\}$, $F_2=\{x_0\}$.
Both inequalities in (3) pass, but their union has size two.
No one-vertex outer state can extend **this pair** to cover both wings.
This is a failure of local sufficiency for (3), not a refutation of
its necessary inequalities or a rejection of all pairs with these sizes.

### 4.5 An extra neighbor invalidates the degree-two specialization

Let $G$ again have one vertex. Let $H$ have vertices
$o_1,w_1,w_2,o_2,r$ and edges

$$
o_1w_1,\quad w_1w_2,\quad w_2o_2,\quad w_1r,\quad o_1r.
$$

The selected rows $r,o_2$ dominate this product, which is isomorphic
to $H$. Yet ignoring $r$ would give
$|R_G(S_{w_1})\setminus S_{w_2}|=1>a_{o_1}=0$.
Here $\deg_H(w_1)=3$, so (H) fails. Proposition 1 instead gives
the valid bound

$$
|R_G(S_{w_1})\setminus S_{w_2}|\leq a_{o_1}+a_r.
$$

Degree two without adjacency is also insufficient: opposite vertices
of a four-cycle cannot be used as the stipulated wing pair. Conversely,
adjacent vertices of a four-cycle do satisfy (H), even though their
outer neighbors also have degree two. The phrase "non-wing neighbor"
in the historical note must not be read as an additional degree assumption.

### 4.6 Distinct outer rows have separate capacities

Let $G$ have vertices $x_0,x_1,x_2$ and edges $x_0x_1,x_0x_2$.
Let $H$ be the path $o_1-w_1-w_2-o_2$, with size pattern
$(1,1,0,2)$. The states

$$
S_{o_1}=\{x_0\},\quad X=S_{w_1}=\{x_0\},\quad
Y=S_{w_2}=\varnothing,\quad S_{o_2}=\{x_1,x_2\}
$$

dominate the product. The first two row residuals are empty; the third
residual $U$ is covered by $X\cup S_{o_2}=U$; and the last
residual is empty. Here $F_1=\varnothing$ and
$F_2=\{x_1,x_2\}$, so (3) passes with capacities one and two.
Comparing $|F_1\cup F_2|=2$ with $a_{o_1}=1$ would falsely
reject the pattern. Equation (4) applies only when $o_1=o_2$;
this example has distinct outer rows.

## 5. Evidence, provenance, and pending promotion

The intended two inequalities and universal rejection criterion were
recovered from the retained historical note
`PATCH_90_wing_pair_lemma-1.md` (uploaded 2026-04-28), where they appear
as Lemma M. This record derives them independently from the definition
of product domination. It makes the factor orientation, closed
neighborhood, size bounds, shared outer row, and survivor semantics
explicit. Historical graph-specific audit counts, runtime claims,
timeout conclusions, and performance assertions are not promoted here.

The finite check has
$\binom{n}{a_{w_1}}\binom{n}{a_{w_2}}$ candidate pairs before
any justified reduction; it is not a constant-time decision procedure
as graph order varies. The mathematical proof does not depend on
enumerating them. A future implementation may reject by this criterion
only after an exhaustive check or another complete certificate of
emptiness. A timeout or partial enumeration must remain unresolved.

`conformance/tests/test_wing_pair_examples.py` checks the examples and
compares rejection with direct Cartesian-product domination on all
labeled horizontal graphs of orders one through three, using a path
and a triangle as the row factors. These are non-authoritative sanity
checks. They neither implement the canonical row-CSP runner nor replace
the missing census regression.
The distinct-row witness in Section 4.6 is an explicit regression, and
the exhaustive comparison also checks that enabling the shared-row
condition leaves every distinct-row pair set unchanged. A separate
[mathematical audit](../docs/audits/wing-pair-review-2026-10-06.md)
records the proof checks without promoting the claim or granting approval.

Run them with:

```sh
python3 -B -m unittest discover -s conformance/tests -p 'test_*.py' -v
```

The following remain pending for issue #5 and `VDC-WING-PAIR` promotion:

- independent review of this proof record;
- recovery and provenance acceptance of the authoritative census (issue #2);
- a replayable canonical row-CSP gold-audit runner (issue #4);
- regression showing that every lemma rejection is UNSAT in that runner
  wherever both apply, with surviving patterns left to the runner;
- explicit coverage of distinct and shared outer rows, infeasible patterns,
  feasible witnesses, and invalid topology, plus versioned replay receipts.

`VDC-WING-PAIR` remains `working`; issue #5 is only partially delivered.
No executable acceptance authority, census membership, strict-surplus
value, or historical audit closure is asserted by this record.
