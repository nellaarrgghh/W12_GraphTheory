from collections import deque
import sys


class FlowNetwork:
    def __init__(self, num_vertices: int):
        # Stores vertex count, 2D capacity matrix, and adjacency lists.
        # capacity[u][v] holds remaining forward capacity (initially edge capacity)
        # and grows on capacity[v][u] as flow is pushed along u -> v. 
        self.n = num_vertices
        self.capacity = [[0] * num_vertices for _ in range(num_vertices)]
        self.adj = [[] for _ in range(num_vertices)]

    def add_edge(self, u: int, v: int, cap: int) -> None:
        if cap < 0:
            raise ValueError("Edge capacity must be non-negative.")
        # Ignore self-loops.
        if u == v:
            return
        # Register both directions in adj so BFS can traverse both forward and 
        # reverse residual edges, allowing residual graph to push flow back.
        if v not in self.adj[u]:
            self.adj[u].append(v)
        if u not in self.adj[v]:
            self.adj[v].append(u)
        # Accumulate capacity.
        self.capacity[u][v] += cap

    def _bfs_find_path(self, source: int, sink: int, parent: list[int]) -> int:
        """Find the shortest augmenting path (fewest edges) using BFS."""
        # Reset parent links: -1 means unvisited, -2 marks the source root.
        for i in range(self.n):
            parent[i] = -1
        parent[source] = -2

        # Track the maximum flow achievable from source to each reached vertex.
        flow_to = [0] * self.n
        flow_to[source] = float("inf")
        queue = deque([source])

        while queue:
            curr = queue.popleft()
            for nxt in self.adj[curr]:
                residual = self.capacity[curr][nxt]
                # Only check unvisited vertices with positive residual capacity.
                if parent[nxt] == -1 and residual > 0:
                    parent[nxt] = curr
                    bottleneck = min(flow_to[curr], residual)
                    flow_to[nxt] = bottleneck
                    # Because BFS explores level by level, reaching the sink first
                    # guarantees a path with the minimum number of edges.
                    if nxt == sink:
                        return bottleneck
                    queue.append(nxt)
        
        # No augmenting path exists from source to sink.
        return 0

    def max_flow(self, source: int, sink: int) -> tuple[int, list[tuple[list[int], int]], list[list[int]]]:
        """Compute maximum flow and return (total_flow, steps, initial_capacities)."""
        if source == sink:
            return 0, [], [row[:] for row in self.capacity]
        
        # Snapshot original capacities before mutating self.capacity into
        # final residual capacities so callers can report used / initial.
        initial_cap = [row[:] for row in self.capacity]
        parent = [-1] * self.n
        total_flow = 0
        steps: list[tuple[list[int], int]] = []

        while True:
            # Find shortest augmenting path and its bottleneck flow.
            pushed = self._bfs_find_path(source, sink, parent)
            if pushed == 0:
                break

            total_flow += pushed
            
            # Backtrack from sink to source via parent to update residual
            # capcities and reconstruct the augmenting path in forward order.
            path: list[int] = []
            curr = sink
            while curr != source:
                path.append(curr)
                prev = parent[curr]
                # Consume forward residual capacity and expose reverse capacity
                # so later augmentations can reroute or undo part of this flow.
                self.capacity[prev][curr] -= pushed
                self.capacity[curr][prev] += pushed
                curr = prev
            path.append(source)
            path.reverse()
            steps.append((path, pushed))

        return total_flow, steps, initial_cap


def read_input_from_stream(stream) -> tuple[int, int, int, list[tuple[int, int, int]]]:
    """
    Expected input format:
      Line 1: N M S T   (vertices N, directed edges M, source S, sink T; 0-indexed)
      Next M lines: u v cap
    Ignores blank lines and '#' comments.
    """
    tokens: list[str] = []
    for line in stream:
        cleaned = line.split("#", 1)[0].strip()
        if cleaned:
            tokens.extend(cleaned.split())

    if len(tokens) < 4:
        raise ValueError("Expected at least 4 integers: N M S T")

    # Read vertex count N, edge count M, source S, sink T.
    n, m, s, t = map(int, tokens[:4])
    expected_tokens = 4 + 3 * m
    if len(tokens) < expected_tokens:
        raise ValueError(f"Expected {m} edges ({expected_tokens} tokens), got {len(tokens)}.")

    # Extract each directed edge triple (u, v, cap).
    edges: list[tuple[int, int, int]] = []
    idx = 4
    for _ in range(m):
        u = int(tokens[idx])
        v = int(tokens[idx + 1])
        cap = int(tokens[idx + 2])
        idx += 3
        edges.append((u, v, cap))

    return n, m, s, t, edges


def main() -> None:
    try:
        # Read from file path if given.
        if len(sys.argv) > 1:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                n, m, s, t, edges = read_input_from_stream(f)
        else:
            print("Enter: N M S T (vertices, edges, source, sink), followed by M lines of 'u v capacity':")
            n, m, s, t, edges = read_input_from_stream(sys.stdin)

        if not (0 <= s < n and 0 <= t < n):
            raise ValueError("Source and sink must be valid vertex indices in [0, N-1].")

        net = FlowNetwork(n)
        for u, v, cap in edges:
            if not (0 <= u < n and 0 <= v < n):
                raise ValueError(f"Edge ({u}, {v}) out of vertex range [0, {n - 1}].")
            net.add_edge(u, v, cap)
        
        total_flow, steps, initial_cap = net.max_flow(s, t)

        print("\n=== Edmonds-Karp Results ===")
        print(f"Source: {s} | Sink: {t}")
        print(f"Maximum Flow: {total_flow}")

        print("\nAugmenting Paths:")
        if not steps:
            print("  None (no path from source to sink)")
        else:
            for i, (path, pushed) in enumerate(steps, start=1):
                path_str = " -> ".join(map(str, path))
                print(f"  {i}. {path_str}  (flow +{pushed})")

        print("\nEdge Flows (flow / capacity):")
        has_edge_output = False
        for u in range(n):
            for v in range(n):
                cap = initial_cap[u][v]
                if cap > 0:
                    has_edge_output = True
                    # Remaining forward capacity is net.capacity[u][v]
                    used = cap - net.capacity[u][v]
                    print(f"  {u} -> {v}: {used} / {cap}")
        if not has_edge_output:
            print("  No positive-capacity edges.")

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()