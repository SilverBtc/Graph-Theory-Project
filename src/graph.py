import os
import math
from time import time
from pyvis.network import Network
import networkx as nx


INF = math.inf


def _format_cell(value, empty_symbol="—"):
    if value == INF:
        return "INF"
    if value is None:
        return empty_symbol
    return str(value)


def print_matrix(matrix, title, row_label="From", col_label="To", empty_symbol="—"):
    n = len(matrix)
    if n == 0:
        print(f"\n{title}\n  (empty matrix)")
        return

    body = [[_format_cell(matrix[i][j], empty_symbol) for j in range(n)] for i in range(n)]
    row_header_width = max(len(str(row_label)), len(str(n - 1)), 2)
    col_width = max(
        3,
        max(len(cell) for row in body for cell in row),
        len(str(n - 1)),
        3,
    )

    print(f"\n{title}")
    header = " " * (row_header_width + 3) + f"{col_label:>{col_width}} "
    header += " ".join(f"{j:>{col_width}}" for j in range(n))
    print(header)
    print(" " * (row_header_width + 3) + "-" * (len(header) - (row_header_width + 3)))

    for i in range(n):
        row_values = " ".join(f"{body[i][j]:>{col_width}}" for j in range(n))
        print(f"{row_label:>{row_header_width}} {i:>2} | {row_values}")


def list_available_graphs(graph_dir):
    if not os.path.isdir(graph_dir):
        print(f"  [!] Graph directory not found: {graph_dir}")
        return []
    files = sorted(
        (f for f in os.listdir(graph_dir) if f.endswith(".txt")),
        key=lambda x: (x.split('.')[0].rstrip('0123456789'), int(''.join(filter(str.isdigit, x.split('.')[0])) or '0'))
    )
    return files


def load_graph(filepath):

    with open(filepath, "r") as f:
        lines = f.readlines()

    n = int(lines[0].strip())
    arc = int(lines[1].strip())

    arcs = []
    for line in lines[2:2 + arc]:
        parts = line.strip().split()
        u, v, w = int(parts[0]), int(parts[1]), int(parts[2])
        arcs.append((u, v, w))

    return n, arcs


def build_value_matrix(n, arcs):
    L = [[INF] * n for _ in range(n)]
    for i in range(n):
        L[i][i] = 0
    for u, v, w in arcs:
        L[u][v] = w
    return L

def display_matrix(arcs, n, title="Matrix"):
    G = nx.DiGraph() 
    G.add_nodes_from(range(n))

    for node in G.nodes():
        G.add_node(node, label=str(node))
    
    for u, v, w in arcs:
        G.add_edge(u, v, title=f"{u}", label=str(w))

    net = Network(notebook=False, directed=True, height="750px", width="100%")
    net.from_nx(G)
    net.show("graph.html", notebook=False)

def floyd_warshall(L0, n, verbose=True):
    L = [row[:] for row in L0]

    P = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and L[i][j] != INF:
                P[i][j] = i

    if verbose:
        print_matrix(L, "L^0 (Initial value matrix)")
        print_matrix(P, "P^0 (Initial predecessor matrix)", empty_symbol="∅")

    # Main loop: consider each vertex k as intermediate
    for k in range(n):
        # Create new matrices for this iteration
        L_new = [row[:] for row in L]
        P_new = [row[:] for row in P]

        for i in range(n):
            for j in range(n):
                # Can we improve path i → j by going through k?
                if L[i][k] != INF and L[k][j] != INF:
                    new_dist = L[i][k] + L[k][j]
                    if new_dist < L[i][j]:
                        L_new[i][j] = new_dist
                        P_new[i][j] = P[k][j]

        L = L_new # shortest distance
        P = P_new # predecessor matrix

        if verbose:
            print_matrix(L, f"L^{k + 1} (after allowing intermediate vertex {k})")
            print_matrix(P, f"P^{k + 1} (after allowing intermediate vertex {k})", empty_symbol="∅")

    return L, P

def has_absorbing_circuit(L, n):
    for i in range(n):
        if L[i][i] < 0:
            return True
    return False

def reconstruct_path(P, L, start, end, n):
    if L[start][end] == INF:
        return None, INF

    path = [end]
    current = end
    visited = set()

    while current != start:
        pred = P[start][current]
        if pred is None:
            return None, INF  # No path
        if pred in visited:
            return None, INF  # Cycle
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
        print(f"No path from {start} to {end}.")
    else:
        print(f"The shortest path from {start} to {end} with cost {cost}")
        print(" → ".join(map(str, path)))
        
    end_time = time()
    print(f"Path reconstruction took {end_time - start_time:.6f} seconds.")



def display_all_paths(P, L, n):
    results = get_all_shortest_paths(P, L, n)
    if not results:
        print("No paths found.")
        return
    
    for start, end, path, cost in results:
        if path:
            print(f"Shortest path from {start} to {end} with cost {cost}: {' -> '.join(map(str, path))}")
        else:
            print(f"No path from {start} to {end}.")


def get_all_shortest_paths(P, L, n):
    results = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            path, cost = reconstruct_path(P, L, i, j, n)
            results.append((i, j, path, cost))
    return results


def process_graph(filepath):
    print(f"\n  Loading graph from: {os.path.basename(filepath)}")
    
    n, arcs = load_graph(filepath)

    print(f"  Number of vertices: {n}")
    print(f"  Number of arcs: {len(arcs)}")

    L = build_value_matrix(n, arcs)

    print_matrix(L, "L^0 (Graph loaded in memory: value matrix)")

    try:
        display_matrix(arcs, n)
    except Exception as e:
        print(f"  [!] Could not display graph visually: {e}")


    print("\nRunning Floyd–Warshall and displaying intermediate L/P matrices...")
    L_final, P = floyd_warshall(L, n, verbose=True)


    if has_absorbing_circuit(L_final, n):
        print("\n  Absorbing circuit detected! Shortest paths are not well-defined.")
        absorbing_vertices = [i for i in range(n) if L_final[i][i] < 0]
        print(f"  Vertices on absorbing circuits: {absorbing_vertices}")
        print(f"  Diagonal values: {[L_final[i][i] for i in absorbing_vertices]}")
        return
    else:
        print("\n  No absorbing circuit detected.")
    




    while True:
        print("\nPath query options:")
        print("  1 — Display a specific path")
        print("  2 — Display all shortest paths")
        print("  0 — Return to main menu")
        choice = input("  Your choice: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            try:
                start = int(input(f"  Starting vertex (0 to {n-1}): ").strip())
                end = int(input(f"  Ending vertex   (0 to {n-1}): ").strip())
                print()
                if 0 <= start < n and 0 <= end < n:
                    display_path(P, L_final, start, end, n)
                else:
                    print(f"  [!] Vertices must be between 0 and {n-1}.")
            except ValueError:
                print("  [!] Invalid input. Please enter a number.")
        elif choice == "2":
            display_all_paths(P, L_final, n)
        else:
            print("  [!] Invalid choice. Please enter 0, 1, or 2.")
        print()
