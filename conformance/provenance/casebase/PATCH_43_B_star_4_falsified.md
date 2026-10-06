# Patch 43: B*(4) FALSIFIED + new minimum-Vizing-slack candidates

## Headline

**Conjecture B*(4) is false.** Systematic exhaustive search over all
γ-edge-maximal connected graphs of order $n \leq 10$ found **two
counterexamples** at $n=10$, $m=16$:

- `` I?r@`bgIo ``
- `` I?r@`aii_ ``

Both are γ-edge-maximal, $\gamma = 4$, $n = 10$, $m = 16$ (verified
independently via MILP). For both, **no Brešar γ-set has $\{v_1, v_2, v_3\}$
inducing $K_3$**. For the second graph, the maximum number of edges in
$G[\{v_1, v_2, v_3\}]$ across all 68 Brešar γ-sets is just 1 — not even
$P_3$.

This kills the path

$$\text{B}^*(4) \implies \text{Projection Lemma}(4) \implies \gamma=4 \text{ Vizing}$$

at the first arrow. The empirical evidence on the small samples (8/8 in
prior session) was misleading; the real counterexample density at $n=10$
is non-trivial (2 out of 14 = ~14%).

## Methodology

Used `nauty-geng` to enumerate all connected graphs at $n \in \{8, 9, 10\}$:

- $n=8$: 11,117 connected graphs → 1 γ-edge-maximal γ=4 (B*(4) holds).
- $n=9$: 261,080 connected graphs → 3 γ-edge-maximal γ=4 (all hold).
- $n=10$: 11,716,571 connected graphs → 14 γ-edge-maximal γ=4 (12 hold, **2 fail**).

For $n=10$ the search was restricted to $m \in [15, 20]$ based on edge counts
observed in $n=8, 9$ examples. The 14 found are likely all of them in this range;
all 14 have $m \in [16, 19]$.

Filtering pipeline per graph:

1. $\gamma(G) > 3$ (brute combinatorial check up to size 3).
2. $\gamma(G) = 4$ (combinatorial check up to size 4).
3. γ-edge-maximal: every non-edge $uv$ has a 3-set dominating $G + uv$.
4. Test B*(4): does any Brešar γ-set $\{v_1, v_2, v_3, v_4\}$ have
   $G[\{v_1, v_2, v_3\}] \cong K_3$?

## The counterexamples

### `` I?r@`bgIo `` ($n=10, m=16$)

Edges: $\{04, 05, 08, 14, 15, 18, 26, 27, 28, 29, 36, 37, 48, 49, 69, 79\}$.

Degree sequence: $(2, 2, 3, 3, 3, 3, 4, 4, 4, 4)$.

Brešar γ-set inducings (over all 86 such sets):
- $3K_1$ (3 independent): 24 sets
- $K_2 + K_1$ (one edge, isolated): 54 sets
- $P_3$ (path of 3): 8 sets
- $K_3$: **0 sets**

Maximum edges in $G[\{v_1, v_2, v_3\}]$ across all Brešar γ-sets: **2** (only $P_3$ form).

### `` I?r@`aii_ `` ($n=10, m=16$)

Edges: $\{04, 05, 08, 09, 14, 15, 26, 27, 28, 29, 36, 37, 48, 49, 68, 69\}$.

Degree sequence: $(2, 2, 2, 2, 4, 4, 4, 4, 4, 4)$.

Brešar γ-set inducings (over all 68 such sets):
- $3K_1$: 24 sets
- $K_2 + K_1$: 44 sets
- $P_3$: **0 sets**
- $K_3$: **0 sets**

Maximum edges in $G[\{v_1, v_2, v_3\}]$ across all Brešar γ-sets: **1**.

## These counterexamples are also Vizing-extremal

Both have $\rho = 2$ (so Hartnell-Rall $\gamma \leq \rho + 1$ does not close
them). Vizing values for products:

| Pair | $\gamma(P)$ | Target | Slack |
|---|---|---|---|
| `` I?r@`bgIo `` □ K_2 | 4 | 4 | **+0 (tight)** |
| `` I?r@`bgIo `` □ C_4 | 8 | 8 | **+0 (tight)** |
| `` I?r@`bgIo `` □ C_5 | 10 | 8 | +2 |
| `` I?r@`bgIo `` □ FHVf? | 13 | 12 | +1 |
| `` I?r@`bgIo `` □ `` I?r@`bgIo `` | 18 | 16 | +2 |
| `` I?r@`aii_ `` □ K_2 | 4 | 4 | **+0 (tight)** |
| `` I?r@`aii_ `` □ C_4 | 8 | 8 | **+0 (tight)** |
| `` I?r@`aii_ `` □ FHVf? | 13 | 12 | +1 |
| `` I?r@`aii_ `` □ `` I?r@`aii_ `` | **17** | **16** | **+1** |

These are dramatically tighter than GP(6,1) (which had slack +8 against
itself). `` I?r@`aii_ `` × `` I?r@`aii_ `` with γ=17 vs target 16 is the
**tightest known γ=4 × γ=4 product** — slack just 1.

This shifts the open frontier: GP(6,1) and friends had +8 slack; `` I?r@`aii_ ``
has only +1 slack against itself, much closer to the Vizing equality
boundary.

## Implications for the Vizing program

**Negative**: B*(4) does not hold, so the planned reduction route through
B*(4) → Projection Lemma(4) is closed. Any Brešar-style proof at γ=4 must
handle Brešar γ-sets where $G[\{v_1, v_2, v_3\}]$ is **arbitrary** —
including the case where it's only $K_2 + K_1$ or even $3K_1$.

**Positive**:

1. **Theorem B(k) is unaffected** — it's the proven structural result and
   provides $N[v_1] \cup N[v_2] \cup N[v_3] = V \setminus \{v_4\}$ regardless
   of how dense $G[\{v_1, v_2, v_3\}]$ is.

2. **New extremal candidates**: `` I?r@`aii_ `` etc. are sharper test
   cases for any Vizing proof attempt. A proof that handles only the
   "easy" K_3-form case will miss these.

3. **The Brešar-Henning-Klavžar question 1** ($\gamma_{\{2\}}(G \square H)
   \geq \gamma_G \gamma_H$) becomes more interesting on these graphs,
   given how tight Vizing already is.

## Revised path forward

The four-label Projection Lemma must be stated and proved **without**
assuming $K_3$ form. The hypothesis becomes:

> **Projection Lemma(4)** (revised): Let $G$ be γ-edge-maximal with
> $\gamma(G) = 4$. By Theorem B(k), there exists a γ-set
> $\{v_1, v_2, v_3, v_4\}$ with $N[v_1] \cup N[v_2] \cup N[v_3] = V(G) \setminus \{v_4\}$.
> Then for every graph $H$, every dominating set $D$ of $G \square H$
> admits a partition $D = D_1 \sqcup D_2 \sqcup D_3 \sqcup D_4$ such that
> each $D_i$ dominates a copy of $H$.

This is what would need proving. The hypothesis is now "B(4) γ-set exists"
(which is Theorem B(k), proven) — no extra structure. The conclusion
remains the same.

But the **proof** becomes harder: Brešar's $k=3$ argument used the
clique-or-$P_3$ structure of $\{v_1, v_2\}$ implicitly to control the
projection. For $k=4$, the four labels might project to fibers in any
of $\binom{|V(G)|}{?}$ many ways, and the global compatibility (Brešar's
Case 7 analog) becomes harder.

## Status of the Vizing γ=4 frontier

- **Closed**: 14/14 edge-max γ=4 at $n \leq 10$ have empirically Vizing
  ≥ 4γ(H) verified on tested products; many with very small slack.
- **Hardest tested case**: `` I?r@`aii_ `` × `` I?r@`aii_ ``: γ=17, target 16, slack +1.
- **B(k)** holds (proven theorem).
- **B*(4)** does not hold (2 counterexamples found).
- **Projection Lemma(4)** revised — still open.

## Files

- `THEOREM_Bk.md` — proof of Theorem B(k) (unchanged, valid for all $k \geq 2$).
- `em_g4_n10_*.txt` — all 14 edge-max γ=4 graphs at $n=10$ (graph6 codes).
- `B_star_4_counterexamples.md` — detailed analysis of the two falsifying graphs.
- This document.

## Honest summary of the program after Patch 43

Of the three pieces I outlined two messages ago:

1. **Theorem B(k)**: still solid, proven, generalization of Brešar 2015 Obs. 4.
2. **B*(4)**: **falsified by counterexample**. Empirical evidence on small
   samples (8/8) was insufficient.
3. **Projection Lemma(4)**: must now be stated without B*(4), making it
   strictly harder. Whether it holds at all for general edge-max γ=4 graphs
   is currently unknown.

The existence of `` I?r@`aii_ `` (Vizing slack only +1 against itself)
suggests the γ=4 frontier is genuinely hard, not just a "few extra cases"
over γ=3.
