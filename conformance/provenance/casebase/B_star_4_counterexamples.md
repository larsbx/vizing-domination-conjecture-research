# B*(4) counterexamples: structural analysis

## Statement of B*(4)

> **Conjecture B*(4) (FALSE)**: Every connected γ-edge-maximal graph with
> $\gamma(G) = 4$ admits a γ-set $\{v_1, v_2, v_3, v_4\}$ such that
> $\{v_1, v_2, v_3\}$ induces $K_3$ AND $N[v_1] \cup N[v_2] \cup N[v_3] = V(G) \setminus \{v_4\}$.

## Counterexample 1: graph6 = `` I?r@`bgIo ``

- $n = 10$, $m = 16$
- $\gamma(G) = 4$ (MILP-verified)
- γ-edge-maximal (all 29 non-edges checked)

**Edges**:
$$\{(0,4), (0,5), (0,8), (1,4), (1,5), (1,8), (2,6), (2,7), (2,8), (2,9), (3,6), (3,7), (4,8), (4,9), (6,9), (7,9)\}$$

**Degree sequence**: $(2, 2, 3, 3, 3, 3, 4, 4, 4, 4)$ where:
- vertices 0, 1: degree 3 (each adjacent to 4, 5, 8)
- vertices 3: degree 2 (adjacent to 6, 7)
- vertex 5: degree 2 (adjacent to 0, 1)
- vertices 2, 4, 6, 7: varied
- vertex 9: degree 4

**All Brešar γ-sets** (86 total). Distribution by edge count of $G[\{v_1, v_2, v_3\}]$:

| # edges | Inducing | Count |
|---|---|---|
| 0 | $3K_1$ | 24 |
| 1 | $K_2 + K_1$ | 54 |
| 2 | $P_3$ | 8 |
| **3** | **$K_3$** | **0** |

**Conclusion**: B*(4) FAILS. Maximum density is $P_3$ form.

**Why no $K_3$**: To get $\{v_1, v_2, v_3\}$ inducing $K_3$, three vertices
$\{a, b, c\}$ must be pairwise adjacent and dominate $V \setminus \{v_4\}$.
The triangles in this graph are: $\{0, 4, 8\}, \{1, 4, 8\}, \{2, 8, 4\}, \{2, 8, 9\}$
(and a few more). For each triangle $T$ and candidate $v_4 \notin T$,
$T$ must dominate $V \setminus \{v_4\}$. Direct check shows no such
$(T, v_4)$ pair satisfies the domination constraint.

## Counterexample 2: graph6 = `` I?r@`aii_ ``

- $n = 10$, $m = 16$
- $\gamma(G) = 4$ (MILP-verified)
- γ-edge-maximal (all 29 non-edges checked)

**Edges**:
$$\{(0,4), (0,5), (0,8), (0,9), (1,4), (1,5), (2,6), (2,7), (2,8), (2,9), (3,6), (3,7), (4,8), (4,9), (6,8), (6,9)\}$$

**Degree sequence**: $(2, 2, 2, 2, 4, 4, 4, 4, 4, 4)$.

The graph is **highly symmetric**: vertices 0 through 3 each have degree
2; vertices 4 through 9 form a "core" of degree-4 vertices.

**All Brešar γ-sets** (68 total):

| # edges | Inducing | Count |
|---|---|---|
| 0 | $3K_1$ | 24 |
| 1 | $K_2 + K_1$ | 44 |
| 2 | $P_3$ | **0** |
| 3 | $K_3$ | **0** |

**This is the more striking counterexample**: the maximum number of edges
in $G[\{v_1, v_2, v_3\}]$ across **all** Brešar γ-sets is **just 1**.

**Why no $P_3$ either**: For $\{v_1, v_2, v_3\}$ to induce $P_3$, the three
vertices form a path of length 2 (one with two adjacent vertices and the
others with one each). For this to be a dominating Brešar set, the constraint
$N[v_1] \cup N[v_2] \cup N[v_3] = V \setminus \{v_4\}$ must hold. Direct
verification: no path-of-length-2 in $G$ dominates $V \setminus \{v_4\}$
for any choice of $v_4$.

## Vizing-tightness of the counterexamples

Both counterexamples satisfy Vizing's conjecture, but with very small slack:

### `` I?r@`bgIo `` products

| Pair | $\gamma(P)$ | Target | Slack |
|---|---|---|---|
| × $K_2$ | 4 | 4 | **0** |
| × $C_4$ | 8 | 8 | **0** |
| × $C_5$ | 10 | 8 | +2 |
| × $C_7$ | 14 | 12 | +2 |
| × FHVf? | 13 | 12 | +1 |
| × `` I?r@`bgIo `` | 18 | 16 | +2 |

### `` I?r@`aii_ `` products

| Pair | $\gamma(P)$ | Target | Slack |
|---|---|---|---|
| × $K_2$ | 4 | 4 | **0** |
| × $C_4$ | 8 | 8 | **0** |
| × $C_5$ | 10 | 8 | +2 |
| × $C_7$ | 14 | 12 | +2 |
| × FHVf? | 13 | 12 | +1 |
| × `` I?r@`aii_ `` | **17** | **16** | **+1** |

`` I?r@`aii_ `` × `` I?r@`aii_ `` is the tightest known γ=4 × γ=4 product
(slack just 1, on 100 vertices).

For comparison, GP(6,1) × GP(6,1) had slack +8 at the same target. So
`` I?r@`aii_ `` is markedly closer to the Vizing equality boundary.

## What this tells us

1. **The structure of edge-max γ=4 graphs is more diverse than B*(4) suggests.**
   The "K_{k-1} dominating clique" picture is wrong for $k = 4$ in general.

2. **Brešar 2015's clique-dominating-V \ {v_3} structure does not extend
   verbatim to $k = 4$.** For $k = 3$ this is automatic in edge-max γ=3
   graphs (every Brešar γ-set has $\{v_1, v_2\}$ as an edge — a "$K_2$
   dominating clique"). For $k = 4$ this becomes a $K_3$ requirement that
   may not be achievable.

3. **The genuinely-open Vizing γ=4 frontier includes graphs with very
   small slack** — much smaller than I had documented. `` I?r@`aii_ `` ×
   `` I?r@`aii_ `` slack +1 is borderline tight.

4. **Any γ=4 Vizing proof attempt must handle Brešar γ-sets where
   $G[\{v_1, v_2, v_3\}]$ is $3K_1$ or $K_2 + K_1$.** This is structurally
   much harder than the $K_3$/$P_3$ cases at $k = 3$.

## Suggested next investigations

- Compute $\gamma_{\{2\}}(G \square G)$ for both counterexamples (BHK
  Question 1 test on the new tightest case).
- Test `` I?r@`aii_ `` against $H$ with $\gamma(H) \geq 4$ — does the
  slack stay near +1 or grow?
- Search at $n = 11$ for more counterexamples; the count at $n = 10$
  (2 out of 14) suggests the density of failures grows.
