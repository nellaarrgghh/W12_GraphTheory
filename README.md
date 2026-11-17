# Week 12: Network Flow

Informatics ITS Graph Theory class Group 6

| Name | NRP |
| --- | --- |
| Naila Sa'ada Cahyani | 5025251258 |
| Lina Fatima Azzahra Badr | 5025251168 |

---

## A. Dinic's Algorithm (Dinitz's Blocking Flow & Level Graph Algorithm)

### 1. Short explanation about algorithm
Dinic's Algorithm (Dinitz, 1970) finds the maximum flow from source $s$ to sink $t$ in a directed capacity network by alternating BFS level-graph construction and DFS blocking-flow phases:

The algorithm runs in four steps:
1. Build the residual network, storing forward capacity $c_r(u, v) = c(u, v) - f(u, v)$ and reverse capacity $c_r(v, u) = f(u, v)$ (skew symmetry $f(v, u) = -f(u, v)$).
2. Run BFS from $s$ ($\text{level}[s] = 0$) over edges with $c_r > 0$ to assign hop distances $\text{level}[v]$. Stop when $t$ is unreachable ($\text{level}[t] = -1$).
3. Push a blocking flow via DFS along edges with $\text{level}[v] = \text{level}[u] + 1$, advancing a current-arc index (`ptr[u]`) to skip saturated and dead-end edges until every $s \to t$ path in the level graph has a saturated edge.
4. Partition vertices reachable from $s$ in the final BFS into $P$ and $P' = V \setminus P$, where $\text{cut}(P, P')$ equals maximum flow (Max-Flow Min-Cut Theorem). Since $\text{level}[t]$ increases each phase ($\le V - 1$ phases), runtime is $O(V^2 E)$ in general and $O(E \sqrt{V})$ on unit-capacity bipartite networks.

### 2. Prerequisite to run the code, if any
- Python 3.10 or newer (standard library only: `argparse`, `collections`, `pathlib`).

### 3. Instructions to run the code
```sh
cd W12

# Run sample files (add --matrices for flow/residual matrices, --no-steps to hide phases)
python3 dinic.py samples/slide_network.txt
python3 dinic.py samples/bipartite_matching.txt --matrices
python3 dinic.py samples/logistics_grid.txt

# Run interactively (enter "<V> <E> <source> <sink>" then each "<u> <v> <capacity>" line)
python3 dinic.py
```

### 4. Result of sample run

#### Sample 1: W12 Slide Flow Network (`samples/slide_network.txt`)
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

#### Sample 2: W12 Maximum Bipartite Matching (`samples/bipartite_matching.txt`)
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

#### Summary of Sample Results:
| Input File | Case Description | $V$ | $E$ | BFS Phases | Min-Cut ($P \to P'$) | Max Flow |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `samples/slide_network.txt` | W12 Slide Flow Network ($P=\{S,A\}$) | 6 | 8 | 2 | 6 | 6 |
| `samples/bipartite_matching.txt` | W12 Bipartite Matching ($a \to d, b \to c$) | 6 | 7 | 2 | 2 | 2 |
| `samples/logistics_grid.txt` | Multi-stage Logistics Network ($P=\{S,A,B\}$) | 8 | 14 | 4 | 19 | 19 |

---

## B. Edmonds-Karp Algorithm

### 1. Short explanation about algorithm
Edmonds-Karp is a maximum flow algorithm that implements the Ford-Fulkerson method using **Breadth-First Search (BFS)** to choose the **shortest augmenting path** (fewest edges) from a source vertex `S` to a sink vertex `T` in the residual graph.

In each iteration:
1. BFS searches for a path from `S` to `T` along edges with positive residual capacity.
2. The minimum residual capacity (bottleneck) along that path is pushed as additional flow.
3. Forward residual capacities decrease by the pushed flow, while reverse residual capacities increase so later paths can reroute or undo flow if needed.
4. The process repeats until no path from `S` to `T` exists in the residual graph, running in O($VE^2$) time.

### 2. Prerequisite to run the code, if any
- Python 3.10 or newer (uses built-in type hints such as `list[int]` and `tuple[...]`).

### 3. Instructions to run the code
1. Move into the W12 root directory and run the program by doing `py edmonds_karp.py`.
2. Write input in this format:
   * Line 1: `N M S T` (`N` vertices, `M` directed edges, source `S`, sink `T`)
   * Next lines: `u v cap` (directed edge from `u` to `v` with capacity `cap`; `#` comments and blank lines are ignored)
   * (Optional) To run with an input file, do `py edmonds_karp.py [input_file_name].txt`
3. When done writing, press Enter to create a new line. On the new line, do Ctrl+Z and press Enter again to finish end `stdin` and get results.

### 4. Result of sample run
1. Bottleneck / Single-Path Limit
```text
$ py edmonds_karp.py
Enter: N M S T (vertices, edges, source, sink), followed by M lines of 'u v capacity':
4 4 0 3
0 1 100
0 2 100
1 2 5
2 3 100
^Z

=== Edmonds-Karp Results ===
Source: 0 | Sink: 3
Maximum Flow: 100

Augmenting Paths:
  1. 0 -> 2 -> 3  (flow +100)

Edge Flows (flow / capacity):
  0 -> 1: 0 / 100
  0 -> 2: 100 / 100
  1 -> 2: 0 / 5
  2 -> 3: 100 / 100
```

<br>
2. Disconnected Sink (Zero Flow)
```text
$ py edmonds_karp.py
Enter: N M S T (vertices, edges, source, sink), followed by M lines of 'u v capacity':
5 4 0 4
0 1 20
1 2 15
2 1 10
3 4 50
^Z

=== Edmonds-Karp Results ===
Source: 0 | Sink: 4
Maximum Flow: 0

Augmenting Paths:
  None (no path from source to sink)

Edge Flows (flow / capacity):
  0 -> 1: 0 / 20
  1 -> 2: 0 / 15
  2 -> 1: 0 / 10
  3 -> 4: 0 / 50
```

<br>
3. Parallel Branches
```text
$ py edmonds_karp.py
Enter: N M S T (vertices, edges, source, sink), followed by M lines of 'u v capacity':
4 5 0 3
0 1 10
0 2 10
1 3 4
2 3 8
1 2 2
^Z

=== Edmonds-Karp Results ===
Source: 0 | Sink: 3
Maximum Flow: 12

Augmenting Paths:
  1. 0 -> 1 -> 3  (flow +4)
  2. 0 -> 2 -> 3  (flow +8)

Edge Flows (flow / capacity):
  0 -> 1: 4 / 10
  0 -> 2: 8 / 10
  1 -> 2: 0 / 2
  1 -> 3: 4 / 4
  2 -> 3: 8 / 8

```

<br>
4. Multi-Stage Supply-to-Sink Network
```text
$ py edmonds_karp.py
Enter: N M S T (vertices, edges, source, sink), followed by M lines of 'u v capacity':
7 10 0 6
0 1 12
0 2 14
1 3 8
1 4 6
2 3 7
2 5 9
3 6 15
4 6 10
5 4 5
5 6 12
^Z

=== Edmonds-Karp Results ===
Source: 0 | Sink: 6
Maximum Flow: 26

Augmenting Paths:
  1. 0 -> 1 -> 3 -> 6  (flow +8)
  2. 0 -> 1 -> 4 -> 6  (flow +4)
  3. 0 -> 2 -> 3 -> 6  (flow +7)
  4. 0 -> 2 -> 5 -> 6  (flow +7)

Edge Flows (flow / capacity):
  0 -> 1: 12 / 12
  0 -> 2: 14 / 14
  1 -> 3: 8 / 8
  1 -> 4: 4 / 6
  2 -> 3: 7 / 7
  2 -> 5: 7 / 9
  3 -> 6: 15 / 15
  4 -> 6: 4 / 10
  5 -> 4: 0 / 5
  5 -> 6: 7 / 12
```

---

## AI Usage Disclosure

### AI Involved:
1. https://share.gemini.google/T3hQxkZckDb2
