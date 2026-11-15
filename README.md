# Week 12: Network Flow

Informatics ITS Graph Theory class Group 6

| Name | NRP |
| --- | --- |
| Naila Sa'ada Cahyani | 5025251258 |
| Lina Fatima Azzahra Badr | 5025251168 |

---

## A. Dinic's Algorithm (Dinitz's Blocking Flow & Level Graph Algorithm)

### 1. Short explanation about algorithm
Dinic's Algorithm (introduced by Yefim Dinitz in 1970) computes the maximum flow from a source vertex $s$ to a sink vertex $t$ in a directed capacity network without relying on single-path Ford-Fulkerson iterations. Instead of searching for one augmenting path per traversal, Dinic's Algorithm alternates between constructing a shortest-distance level graph and pushing a blocking flow across each level phase:

The algorithm proceeds in four steps during each run:
1. Build the residual network. For every directed edge $(u, v)$ with capacity $c(u, v)$ and flow $f(u, v)$, the solver stores a forward residual edge with remaining capacity $c_r(u, v) = c(u, v) - f(u, v)$ and a reverse residual edge with capacity $c_r(v, u) = f(u, v)$, maintaining skew symmetry $f(v, u) = -f(u, v)$.
2. Construct the level graph with Breadth-First Search (BFS). Starting from source $s$ at level $0$, BFS assigns each reachable vertex $v$ a shortest-path distance $\text{level}[v]$ using only edges where $c_r > 0$. When sink $t$ is unreachable ($\text{level}[t] = -1$), the flow is maximum and the search stops.
3. Push a blocking flow with Depth-First Search (DFS) and dead-end pruning. DFS traverses only edges that advance by one level ($\text{level}[v] = \text{level}[u] + 1$). Each vertex keeps a current-arc index (`ptr[u]`) so saturated or dead-end edges are not revisited during the same BFS phase. The phase ends once every $s \to t$ path in the current level graph has at least one saturated edge.
4. Extract the minimum $s$-$t$ cut. After the final BFS where $t$ is unreachable, the vertices reachable from $s$ form partition $P$ and the rest form $P' = V \setminus P$. By the Max-Flow Min-Cut Theorem, the capacity sum of forward edges crossing from $P$ to $P'$ equals the maximum flow.

Each phase strictly increases $\text{level}[t]$, which caps the number of phases at $V - 1$. Current-arc pruning bounds each blocking-flow phase to $O(V E)$ work, yielding $O(V^2 E)$ total time on general networks and $O(E \sqrt{V})$ on unit-capacity bipartite matching networks.

### 2. Prerequisite to run the code, if any
- Python 3.10 or newer.
- No external libraries are needed; the script uses only Python's standard library (`argparse`, `collections`, `pathlib`).

### 3. Instructions to run the code
Ensure your terminal is inside the `W12` directory:

```sh
cd W12
```

#### Run with sample input files:
```sh
# 1. Directed network from the W12 Network Flow lecture slides (Pages 4-10, Max Flow = 6)
python3 dinic.py samples/slide_network.txt

# 2. Maximum Bipartite Matching network from the W12 lecture slides (Pages 11-15) with flow & residual matrices
python3 dinic.py samples/bipartite_matching.txt --matrices

# 3. Multi-stage 8-vertex distribution network demonstrating 4 BFS level phases
python3 dinic.py samples/logistics_grid.txt
```

#### Run interactively (custom flow network):
```sh
python3 dinic.py
```
Enter the header `<num_vertices> <num_edges> <source> <sink>` followed by each directed edge `<u> <v> <capacity>`:
```text
Dinic's Algorithm - Maximum Network Flow & Minimum Cut Solver
Press Ctrl+C to cancel.
Header (<num_vertices> <num_edges> <source> <sink>): 4 5 S T
Edge 1/5 (u v capacity): S A 4
Edge 2/5 (u v capacity): S B 2
Edge 3/5 (u v capacity): A B 3
Edge 4/5 (u v capacity): A T 2
Edge 5/5 (u v capacity): B T 4
```

### 4. Result of sample run

#### Sample 1: W12 Lecture Slide Flow Network (`samples/slide_network.txt`)
Solving the 6-vertex, 8-edge network from pages 4 to 10 of the W12 Network Flow slides (finding maximum flow of 6 and minimum cut $K_2$ with partition $P = \{S, A\}$ and $P' = \{B, C, D, T\}$):
```text
$ python3 dinic.py samples/slide_network.txt
Input: slide_network.txt
Vertices: 6 (S, A, B, C, D, T)
Edges: 8
Source: S | Sink: T

Dinic's Algorithm Phases:
  [Phase 1] BFS Level Graph (sink level = 3): {S:0, A:1, B:1, C:2, D:2, T:3}
    Augmenting path: S -> A -> C -> T (bottleneck flow = +2)
    Augmenting path: S -> B -> D -> T (bottleneck flow = +2)
    Blocking flow pushed in Phase 1: 4
  [Phase 2] BFS Level Graph (sink level = 4): {S:0, A:1, B:2, C:4, D:3, T:4}
    Augmenting path: S -> A -> B -> D -> T (bottleneck flow = +2)
    Blocking flow pushed in Phase 2: 2

Edge Flow Distribution (flow / capacity):
  S -> A : 4 / 5
  S -> B : 2 / 2 [SATURATED]
  A -> B : 2 / 2 [SATURATED]
  A -> C : 2 / 2 [SATURATED]
  B -> D : 4 / 4 [SATURATED]
  D -> C : 0 / 1
  C -> T : 2 / 3
  D -> T : 4 / 5

Max-Flow Min-Cut Verification:
  Reachable Partition P      = {S, A}
  Unreachable Partition P'   = {B, C, D, T}
  Minimum Cut Edges (P -> P'):
    (S, B) : 2 / 2
    (A, B) : 2 / 2
    (A, C) : 2 / 2
  Minimum Cut Capacity       : 6
  Maximum Network Flow       : 6
```

#### Sample 2: W12 Maximum Bipartite Matching via Network Flow (`samples/bipartite_matching.txt`)
Solving the bipartite matching problem ($V_1 = \{a, b\}$, $V_2 = \{c, d\}$) from pages 11 to 15 of the W12 slides, including the skew-symmetric flow matrix $f(u, v)$ and residual capacity matrix $c_r(u, v)$:
```text
$ python3 dinic.py samples/bipartite_matching.txt --matrices
Input: bipartite_matching.txt
Vertices: 6 (s, a, b, c, d, t)
Edges: 7
Source: s | Sink: t

Dinic's Algorithm Phases:
  [Phase 1] BFS Level Graph (sink level = 3): {s:0, a:1, b:1, c:2, d:2, t:3}
    Augmenting path: s -> a -> c -> t (bottleneck flow = +1)
    Blocking flow pushed in Phase 1: 1
  [Phase 2] BFS Level Graph (sink level = 5): {s:0, a:3, b:1, c:2, d:4, t:5}
    Augmenting path: s -> b -> c -> a -> d -> t (bottleneck flow = +1)
    Blocking flow pushed in Phase 2: 1

Edge Flow Distribution (flow / capacity):
  s -> a : 1 / 1 [SATURATED]
  s -> b : 1 / 1 [SATURATED]
  a -> c : 0 / 1
  a -> d : 1 / 1 [SATURATED]
  b -> c : 1 / 1 [SATURATED]
  c -> t : 1 / 1 [SATURATED]
  d -> t : 1 / 1 [SATURATED]

Final Flow Matrix f(u, v) [skew symmetry]:
        s    a    b    c    d    t
   s    0    1    1    0    0    0
   a   -1    0    0    0    1    0
   b   -1    0    0    1    0    0
   c    0    0   -1    0    0    1
   d    0   -1    0    0    0    1
   t    0    0    0   -1   -1    0

Final Residual Capacity Matrix cr(u, v):
      s   a   b   c   d   t
  s   0   0   0   0   0   0
  a   1   0   0   1   0   0
  b   1   0   0   0   0   0
  c   0   0   1   0   0   0
  d   0   1   0   0   0   0
  t   0   0   0   1   1   0

Max-Flow Min-Cut Verification:
  Reachable Partition P      = {s}
  Unreachable Partition P'   = {a, b, c, d, t}
  Minimum Cut Edges (P -> P'):
    (s, a) : 1 / 1
    (s, b) : 1 / 1
  Minimum Cut Capacity       : 2
  Maximum Network Flow       : 2
```

#### Sample 3: Multi-Stage Logistics Distribution Network (`samples/logistics_grid.txt`)
Demonstrating 4 consecutive BFS level phases ($\text{level}[T] = 3, 4, 5, 6$) on an 8-vertex, 14-edge network:
```text
$ python3 dinic.py samples/logistics_grid.txt
Input: logistics_grid.txt
Vertices: 8 (S, A, B, C, D, E, F, T)
Edges: 14
Source: S | Sink: T

Dinic's Algorithm Phases:
  [Phase 1] BFS Level Graph (sink level = 3): {S:0, A:1, B:1, C:1, D:2, E:2, F:2, T:3}
    Augmenting path: S -> A -> D -> T (bottleneck flow = +5)
    Augmenting path: S -> B -> D -> T (bottleneck flow = +2)
    Augmenting path: S -> B -> E -> T (bottleneck flow = +3)
    Augmenting path: S -> C -> E -> T (bottleneck flow = +4)
    Augmenting path: S -> C -> F -> T (bottleneck flow = +1)
    Blocking flow pushed in Phase 1: 15
  [Phase 2] BFS Level Graph (sink level = 4): {S:0, A:1, B:1, C:4, D:2, E:3, F:4, T:4}
    Augmenting path: S -> B -> D -> E -> T (bottleneck flow = +1)
    Blocking flow pushed in Phase 2: 1
  [Phase 3] BFS Level Graph (sink level = 5): {S:0, A:1, B:1, C:4, D:2, E:3, F:4, T:5}
    Augmenting path: S -> B -> D -> E -> F -> T (bottleneck flow = +2)
    Blocking flow pushed in Phase 3: 2
  [Phase 4] BFS Level Graph (sink level = 6): {S:0, A:1, B:2, C:5, D:3, E:4, F:5, T:6}
    Augmenting path: S -> A -> B -> D -> E -> F -> T (bottleneck flow = +1)
    Blocking flow pushed in Phase 4: 1

Edge Flow Distribution (flow / capacity):
  S -> A : 6 / 10
  S -> B : 8 / 8 [SATURATED]
  S -> C : 5 / 5 [SATURATED]
  A -> B : 1 / 4
  A -> D : 5 / 5 [SATURATED]
  B -> D : 6 / 6 [SATURATED]
  B -> E : 3 / 3 [SATURATED]
  C -> E : 4 / 4 [SATURATED]
  C -> F : 1 / 3
  D -> E : 4 / 4 [SATURATED]
  D -> T : 7 / 7 [SATURATED]
  E -> F : 3 / 3 [SATURATED]
  E -> T : 8 / 8 [SATURATED]
  F -> T : 4 / 6

Max-Flow Min-Cut Verification:
  Reachable Partition P      = {S, A, B}
  Unreachable Partition P'   = {C, D, E, F, T}
  Minimum Cut Edges (P -> P'):
    (S, C) : 5 / 5
    (A, D) : 5 / 5
    (B, D) : 6 / 6
    (B, E) : 3 / 3
  Minimum Cut Capacity       : 19
  Maximum Network Flow       : 19
```

#### Summary of Sample Results:
| Input File | Case Description | Vertices ($V$) | Edges ($E$) | BFS Phases | Minimum Cut ($P \to P'$) | Maximum Flow |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `samples/slide_network.txt` | W12 Lecture Slide Flow Network | 6 | 8 | 2 | 6 | 6 |
| `samples/bipartite_matching.txt` | W12 Bipartite Matching ($a \to d, b \to c$) | 6 | 7 | 2 | 2 | 2 |
| `samples/logistics_grid.txt` | Multi-stage Logistics Distribution Network | 8 | 14 | 4 | 19 | 19 |

---

## B. [Algorithm Name]

### 1. Short explanation about algorithm

### 2. Prerequisite to run the code, if any

### 3. Instructions to run the code

### 4. Result of sample run


---

## AI Usage Disclosure

### AI Involved:
1. [Insert AI share link here]
