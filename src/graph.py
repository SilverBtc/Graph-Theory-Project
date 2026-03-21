import os
import math
from time import time
import networkx as nx

try:
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    Network = None
    PYVIS_AVAILABLE = False


INF = math.inf


def list_available_graphs(graph_dir):
    if not os.path.isdir(graph_dir):
        print(f"  [!] Graph directory not found: {graph_dir}")
        return []
    return sorted(f for f in os.listdir(graph_dir) if f.endswith(".txt"))


def load_graph(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) < 2:
        raise ValueError("Invalid graph file: missing header lines.")

    n = int(lines[0])
    arc_count = int(lines[1])

    if n < 0 or arc_count < 0:
        raise ValueError("Number of vertices and arcs must be non-negative.")

    if len(lines) != 2 + arc_count:
        raise ValueError(
            f"Invalid graph file: expected {arc_count} arc lines, found {len(lines) - 2}."
        )

    arcs = []
    seen = set()

    for line_index, line in enumerate(lines[2:], start=3):
        parts = line.split()
        if len(parts) != 3:
            raise ValueError(f"Invalid arc format on line {line_index}: '{line}'")

        u, v, w = map(int, parts)

        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(
                f"Invalid vertex on line {line_index}: vertices must be between 0 and {n - 1}."
            )

        if (u, v) in seen:
            raise ValueError(f"Duplicate arc detected: ({u}, {v})")

        seen.add((u, v))
        arcs.append((u, v, w))

    return n, arcs


def build_value_matrix(n, arcs):
    L = [[INF] * n for _ in range(n)]
    for i in range(n):
        L[i][i] = 0

    for u, v, w in arcs:
        L[u][v] = w

    return L


def open_graph_html(arcs, n, output_file="graph.html"):
    if not PYVIS_AVAILABLE:
        raise RuntimeError(
            "PyVis is not installed. Install it with: pip install pyvis"
        )

    G = nx.DiGraph()
    G.add_nodes_from(range(n))

    for node in G.nodes():
        G.nodes[node]["label"] = str(node)

    for u, v, w in arcs:
        G.add_edge(u, v, title=str(w), label=str(w))

    net = Network(notebook=False, directed=True, height="750px", width="100%")
    net.from_nx(G)
    net.show(output_file, notebook=False)


def _format_cell(value):
    if value == INF:
        return "INF"
    if value is None:
        return "-"
    return str(value)


def format_matrix(matrix, title="Matrix"):
    n = len(matrix)
    cell_width = max(
        5,
        max(len(_format_cell(value)) for row in matrix for value in row) + 1 if n > 0 else 5,
    )

    lines = [title]
    header = " " * cell_width + "".join(f"{j:>{cell_width}}" for j in range(n))
    lines.append(header)

    for i, row in enumerate(matrix):
        line = f"{i:>{cell_width}}" + "".join(
            f"{_format_cell(value):>{cell_width}}" for value in row
        )
        lines.append(line)

    return "\n".join(lines)


def print_matrix(matrix, title="Matrix", indent="  "):
    text = format_matrix(matrix, title)
    for line in text.splitlines():
        print(indent + line)


def floyd_warshall(L0, n):
    L = [row[:] for row in L0]

    P = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and L[i][j] != INF:
                P[i][j] = i

    steps = [("L0 / P0", [row[:] for row in L], [row[:] for row in P])]

    for k in range(n):
        L_new = [row[:] for row in L]
        P_new = [row[:] for row in P]

        for i in range(n):
            for j in range(n):
                if L[i][k] != INF and L[k][j] != INF:
                    new_dist = L[i][k] + L[k][j]
                    if new_dist < L[i][j]:
                        L_new[i][j] = new_dist
                        P_new[i][j] = P[k][j]

        L = L_new
        P = P_new
        steps.append((f"k = {k}", [row[:] for row in L], [row[:] for row in P]))

    return L, P, steps


def has_absorbing_circuit(L, n):
    for i in range(n):
        if L[i][i] < 0:
            return True
    return False


def reconstruct_path(P, L, start, end, n):
    if not (0 <= start < n and 0 <= end < n):
        return None, INF

    if L[start][end] == INF:
        return None, INF

    if start == end:
        return [start], 0

    path = [end]
    current = end
    visited = set()

    while current != start:
        pred = P[start][current]
        if pred is None:
            return None, INF
        if current in visited:
            return None, INF

        visited.add(current)
        path.append(pred)
        current = pred

        if len(path) > n + 1:
            return None, INF

    path.reverse()
    return path, L[start][end]


def display_path(P, L, start, end, n):
    start_time = time()
    path, cost = reconstruct_path(P, L, start, end, n)

    if path is None:
        print(f"  No path from {start} to {end}.")
    else:
        print(f"  Shortest path from {start} to {end} with cost {cost}:")
        print("  " + " -> ".join(map(str, path)))

    end_time = time()
    print(f"  Path reconstruction took {end_time - start_time:.6f} seconds.")


def get_all_shortest_paths(P, L, n):
    results = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            path, cost = reconstruct_path(P, L, i, j, n)
            results.append((i, j, path, cost))
    return results


def display_all_paths(P, L, n):
    results = get_all_shortest_paths(P, L, n)
    if not results:
        print("  No paths found.")
        return

    for start, end, path, cost in results:
        if path:
            print(f"  {start} -> {end}: {' -> '.join(map(str, path))} (cost = {cost})")
        else:
            print(f"  {start} -> {end}: No path")


def export_execution_trace(graph_filepath, output_filepath):
    n, arcs = load_graph(graph_filepath)
    L0 = build_value_matrix(n, arcs)
    L_final, P_final, steps = floyd_warshall(L0, n)

    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(f"Graph file: {os.path.basename(graph_filepath)}\n")
        f.write(f"Vertices: {n}\n")
        f.write(f"Arcs: {len(arcs)}\n\n")

        for step_name, L_step, P_step in steps:
            f.write(format_matrix(L_step, f"L matrix ({step_name})"))
            f.write("\n\n")
            f.write(format_matrix(P_step, f"P matrix ({step_name})"))
            f.write("\n\n")

        if has_absorbing_circuit(L_final, n):
            f.write("Absorbing circuit detected.\n")
            absorbing_vertices = [i for i in range(n) if L_final[i][i] < 0]
            f.write(f"Vertices on absorbing circuits: {absorbing_vertices}\n")
            f.write(f"Diagonal values: {[L_final[i][i] for i in absorbing_vertices]}\n")
        else:
            f.write("No absorbing circuit detected.\n\n")
            f.write("All shortest paths:\n")
            for start, end, path, cost in get_all_shortest_paths(P_final, L_final, n):
                if path:
                    f.write(f"{start} -> {end}: {' -> '.join(map(str, path))} (cost = {cost})\n")
                else:
                    f.write(f"{start} -> {end}: No path\n")


def export_all_traces(graph_dir="graphs", output_dir="traces"):
    os.makedirs(output_dir, exist_ok=True)
    files = list_available_graphs(graph_dir)

    generated = []
    for filename in files:
        src = os.path.join(graph_dir, filename)
        dst = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_trace.txt")
        export_execution_trace(src, dst)
        generated.append(dst)

    return generated


def process_graph(filepath):
    print(f"\n  Loading graph from: {os.path.basename(filepath)}")

    n, arcs = load_graph(filepath)

    print(f"  Number of vertices: {n}")
    print(f"  Number of arcs: {len(arcs)}")

    L0 = build_value_matrix(n, arcs)
    L_final, P_final, steps = floyd_warshall(L0, n)

    print()
    for step_name, L_step, P_step in steps:
        print_matrix(L_step, f"L matrix ({step_name})")
        print()
        print_matrix(P_step, f"P matrix ({step_name})")
        print()

    try:
        open_graph_html(arcs, n)
        print("  Interactive graph view opened in the browser.")
    except Exception as e:
        print(f"  [!] Could not display graph visually: {e}")

    if has_absorbing_circuit(L_final, n):
        print("\n  Absorbing circuit detected! Shortest paths are not well-defined.")
        absorbing_vertices = [i for i in range(n) if L_final[i][i] < 0]
        print(f"  Vertices on absorbing circuits: {absorbing_vertices}")
        print(f"  Diagonal values: {[L_final[i][i] for i in absorbing_vertices]}")
        return

    while True:
        print("\n  Path query options:")
        print("    1 - Display a specific path")
        print("    2 - Display all shortest paths")
        print("    0 - Return to main menu")
        choice = input("  Your choice: ").strip()

        if choice == "0":
            break
        if choice == "1":
            try:
                start = int(input(f"  Starting vertex (0 to {n - 1}): ").strip())
                end = int(input(f"  Ending vertex   (0 to {n - 1}): ").strip())
                print()
                display_path(P_final, L_final, start, end, n)
            except ValueError:
                print("  [!] Invalid input. Please enter integers.")
        elif choice == "2":
            display_all_paths(P_final, L_final, n)
        else:
            print("  [!] Invalid choice. Please enter 0, 1, or 2.")