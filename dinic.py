import argparse
from collections import deque
from pathlib import Path


class _ResidualEdge:
    __slots__ = ('to', 'rev', 'cap', 'flow', 'is_original', 'orig_idx')

    def __init__(self, to, rev, cap, is_original=False, orig_idx=-1):
        self.to = to
        self.rev = rev
        self.cap = cap
        self.flow = 0
        self.is_original = is_original
        self.orig_idx = orig_idx


def _bfs_levels(adj, source_id, sink_id):
    levels = [-1] * len(adj)
    levels[source_id] = 0
    queue = deque([source_id])

    while queue:
        u = queue.popleft()
        for edge in adj[u]:
            if edge.cap - edge.flow > 0 and levels[edge.to] == -1:
                levels[edge.to] = levels[u] + 1
                queue.append(edge.to)

    return levels, levels[sink_id] != -1


def _dfs_augment(adj, levels, ptr, u, sink_id, pushed, path_nodes):
    if pushed == 0 or u == sink_id:
        return pushed

    # Advance ptr[u] in-place so saturated or dead-end edges are skipped in this phase.
    while ptr[u] < len(adj[u]):
        edge = adj[u][ptr[u]]
        residual = edge.cap - edge.flow
        if levels[edge.to] == levels[u] + 1 and residual > 0:
            path_nodes.append(edge.to)
            tr = _dfs_augment(
                adj, levels, ptr, edge.to, sink_id, min(pushed, residual), path_nodes
            )
            if tr > 0:
                edge.flow += tr
                adj[edge.to][edge.rev].flow -= tr
                return tr
            path_nodes.pop()
        ptr[u] += 1

    return 0


def solve_dinic(nodes, edges, source, sink):
    node_to_id = {name: i for i, name in enumerate(nodes)}
    n = len(nodes)
    adj = [[] for _ in range(n)]

    for idx, (u_name, v_name, cap) in enumerate(edges):
        u = node_to_id[u_name]
        v = node_to_id[v_name]
        fwd = _ResidualEdge(v, len(adj[v]), cap, is_original=True, orig_idx=idx)
        bwd = _ResidualEdge(u, len(adj[u]), 0, is_original=False, orig_idx=idx)
        adj[u].append(fwd)
        adj[v].append(bwd)

    source_id = node_to_id[source]
    sink_id = node_to_id[sink]
    max_flow = 0
    phases = []

    while True:
        levels, reachable = _bfs_levels(adj, source_id, sink_id)
        if not reachable:
            break

        ptr = [0] * n
        augmentations = []
        phase_flow = 0

        while True:
            path_ids = [source_id]
            pushed = _dfs_augment(
                adj, levels, ptr, source_id, sink_id, float('inf'), path_ids
            )
            if pushed == 0:
                break
            phase_flow += pushed
            max_flow += pushed
            augmentations.append(([nodes[i] for i in path_ids], pushed))

        level_map = {nodes[i]: levels[i] for i in range(n) if levels[i] != -1}
        phases.append({
            'levels': level_map,
            'sink_level': levels[sink_id],
            'augmentations': augmentations,
            'phase_flow': phase_flow,
        })

    final_levels, _ = _bfs_levels(adj, source_id, sink_id)
    reachable_set = {nodes[i] for i in range(n) if final_levels[i] != -1}
    p_set = [name for name in nodes if name in reachable_set]
    p_prime_set = [name for name in nodes if name not in reachable_set]

    edge_flows = [0] * len(edges)
    for u in range(n):
        for edge in adj[u]:
            if edge.is_original:
                edge_flows[edge.orig_idx] = edge.flow

    cut_edges = []
    cut_capacity = 0
    for idx, (u_name, v_name, cap) in enumerate(edges):
        if u_name in reachable_set and v_name not in reachable_set:
            cut_edges.append((u_name, v_name, edge_flows[idx], cap))
            cut_capacity += cap

    flow_matrix = [[0] * n for _ in range(n)]
    residual_matrix = [[0] * n for _ in range(n)]
    for idx, (u_name, v_name, cap) in enumerate(edges):
        u = node_to_id[u_name]
        v = node_to_id[v_name]
        f = edge_flows[idx]
        # Skew symmetry: net flow on (u, v) is +f and on (v, u) is -f.
        flow_matrix[u][v] += f
        flow_matrix[v][u] -= f
        residual_matrix[u][v] += cap - f
        residual_matrix[v][u] += f

    return {
        'nodes': nodes,
        'edges': edges,
        'source': source,
        'sink': sink,
        'max_flow': max_flow,
        'phases': phases,
        'edge_flows': edge_flows,
        'p_set': p_set,
        'p_prime_set': p_prime_set,
        'cut_edges': cut_edges,
        'cut_capacity': cut_capacity,
        'flow_matrix': flow_matrix,
        'residual_matrix': residual_matrix,
    }


def _build_node_order(edges, source, sink):
    seen = []
    for name in [source] + [x for u, v, _ in edges for x in (u, v)] + [sink]:
        if name not in seen:
            seen.append(name)
    if seen[-1] != sink and sink in seen:
        seen.remove(sink)
        seen.append(sink)
    return seen


def _parse_header(line):
    parts = line.split()
    if len(parts) != 4:
        raise ValueError(
            'Header line must contain 4 tokens: <num_vertices> <num_edges> <source> <sink>'
        )
    try:
        num_v = int(parts[0])
        num_e = int(parts[1])
    except ValueError:
        raise ValueError('Vertex and edge counts in header must be integers') from None
    if num_v < 2 or num_e < 1:
        raise ValueError('Graph must have at least 2 vertices and 1 edge')
    source, sink = parts[2], parts[3]
    if source == sink:
        raise ValueError('Source and sink must be distinct vertices')
    return num_v, num_e, source, sink


def _parse_edge(line, idx):
    parts = line.split()
    if len(parts) != 3:
        raise ValueError(f'Edge {idx} must have 3 tokens: <u> <v> <capacity>')
    u, v = parts[0], parts[1]
    try:
        cap = int(parts[2])
    except ValueError:
        raise ValueError(f'Capacity on edge {idx} ({u} -> {v}) must be an integer') from None
    if cap <= 0:
        raise ValueError(f'Capacity on edge {idx} ({u} -> {v}) must be positive')
    return u, v, cap


def read_problem(path):
    lines = []
    for raw in Path(path).read_text(encoding='utf-8-sig').splitlines():
        clean = raw.split('#', 1)[0].strip()
        if clean:
            lines.append(clean)
    if not lines:
        raise ValueError(
            'Input file is empty; expected "<V> <E> <source> <sink>" on the first line'
        )

    num_v, num_e, source, sink = _parse_header(lines[0])
    remaining = lines[1:]
    if len(remaining) != num_e:
        raise ValueError(f'Expected {num_e} edge lines after header, found {len(remaining)}')

    edges = [_parse_edge(line, i + 1) for i, line in enumerate(remaining)]
    nodes = _build_node_order(edges, source, sink)
    if len(nodes) > num_v:
        raise ValueError(
            f'Header declares {num_v} vertices, but edge list references {len(nodes)} distinct vertices'
        )
    return nodes, edges, source, sink


def read_interactive():
    print("Dinic's Algorithm - Maximum Network Flow & Minimum Cut Solver")
    print('Press Ctrl+C to cancel.')
    while True:
        try:
            num_v, num_e, source, sink = _parse_header(
                input('Header (<num_vertices> <num_edges> <source> <sink>): ')
            )
            break
        except ValueError as error:
            print(error)

    edges = []
    for i in range(num_e):
        while True:
            try:
                edge = _parse_edge(input(f'Edge {i + 1}/{num_e} (u v capacity): '), i + 1)
                edges.append(edge)
                break
            except ValueError as error:
                print(error)

    nodes = _build_node_order(edges, source, sink)
    return nodes, edges, source, sink


def _format_labeled_matrix(nodes, matrix):
    col_w = max(max(len(name) for name in nodes), max(len(str(val)) for row in matrix for val in row)) + 2
    header = f'{"":>{col_w}} ' + ' '.join(f'{name:>{col_w}}' for name in nodes)
    rows = [header]
    for r, u_name in enumerate(nodes):
        cells = ' '.join(f'{matrix[r][c]:>{col_w}}' for c in range(len(nodes)))
        rows.append(f'{u_name:>{col_w}} {cells}')
    return '\n'.join(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Compute maximum network flow and minimum s-t cut using Dinic's Algorithm"
    )
    parser.add_argument(
        'input', type=Path, nargs='?',
        help='Optional flow network file; omit to enter graph interactively'
    )
    parser.add_argument(
        '--no-steps', action='store_true',
        help='Hide intermediate BFS level graphs and blocking flow phases'
    )
    parser.add_argument(
        '--matrices', action='store_true',
        help='Display final skew-symmetric flow matrix and residual capacity matrix'
    )
    args = parser.parse_args()

    try:
        nodes, edges, source, sink = (
            read_problem(args.input) if args.input else read_interactive()
        )
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, '\nInput cancelled.\n')
    except (OSError, ValueError) as error:
        parser.error(str(error))

    result = solve_dinic(nodes, edges, source, sink)

    print(f'Input: {args.input.name if args.input else "interactive"}')
    print(f'Vertices: {len(nodes)} ({", ".join(nodes)})')
    print(f'Edges: {len(edges)}')
    print(f'Source: {source} | Sink: {sink}')

    if not args.no_steps:
        print("\nDinic's Algorithm Phases:")
        if not result['phases']:
            print('  No augmenting path exists from source to sink.')
        for idx, phase in enumerate(result['phases'], start=1):
            lvl_str = ', '.join(f'{k}:{v}' for k, v in phase['levels'].items())
            print(f'  [Phase {idx}] BFS Level Graph (sink level = {phase["sink_level"]}): {{{lvl_str}}}')
            for path_nodes, pushed in phase['augmentations']:
                route = ' -> '.join(path_nodes)
                print(f'    Augmenting path: {route} (bottleneck flow = +{pushed})')
            print(f'    Blocking flow pushed in Phase {idx}: {phase["phase_flow"]}')

    print('\nEdge Flow Distribution (flow / capacity):')
    for (u, v, cap), flow in zip(edges, result['edge_flows']):
        status = ' [SATURATED]' if flow == cap else ''
        print(f'  {u} -> {v} : {flow} / {cap}{status}')

    if args.matrices:
        print('\nFinal Flow Matrix f(u, v) [skew symmetry]:')
        print(_format_labeled_matrix(nodes, result['flow_matrix']))
        print('\nFinal Residual Capacity Matrix cr(u, v):')
        print(_format_labeled_matrix(nodes, result['residual_matrix']))

    p_str = ', '.join(result['p_set'])
    p_prime_str = ', '.join(result['p_prime_set'])
    print('\nMax-Flow Min-Cut Verification:')
    print(f'  Reachable Partition P      = {{{p_str}}}')
    print(f'  Unreachable Partition P\'   = {{{p_prime_str}}}')
    print('  Minimum Cut Edges (P -> P\'):')
    for u, v, flow, cap in result['cut_edges']:
        print(f'    ({u}, {v}) : {flow} / {cap}')
    print(f'  Minimum Cut Capacity       : {result["cut_capacity"]}')
    print(f'  Maximum Network Flow       : {result["max_flow"]}')


if __name__ == '__main__':
    main()
