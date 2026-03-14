import os
import math
from pyvis.network import Network
import networkx as nx


INF = math.inf


def list_available_graphs(graph_dir):
    if not os.path.isdir(graph_dir):
        print(f"  [!] Graph directory not found: {graph_dir}")
        return []
    files = sorted(f for f in os.listdir(graph_dir) if f.endswith(".txt"))
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

def floyd_warshall(L0, n):
    L = [row[:] for row in L0]

    P = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and L[i][j] != INF:
                P[i][j] = i

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

    return L, P

def has_absorbing_circuit(L, n):
    for i in range(n):
        if L[i][i] < 0:
            return True
    return False


def display_path(P, L, start, end, n):
    pass


def display_all_paths(P, L, n):
    pass


def process_graph(filepath):
    print(f"\n  Loading graph from: {os.path.basename(filepath)}")
    
    n, arcs = load_graph(filepath)

    print(f"  Number of vertices: {n}")
    print(f"  Number of arcs: {len(arcs)}")
    print(f"  Arcs: {arcs}")

    L = build_value_matrix(n, arcs)

    print("\n  Initial value matrix (L^0):")
    for row in L:
        print("  " + " ".join(f"{x if x != INF else 'INF':>5}" for x in row))


    display_matrix(arcs, n)


    L, P = floyd_warshall(L, n)

    print(L)
    print(P)


    if has_absorbing_circuit(L, n):
        print("\n  Absorbing circuit detected! Shortest paths are not well-defined.")
        absorbing_vertices = [i for i in range(n) if L[i][i] < 0]
        print(f"  Vertices on absorbing circuits: {absorbing_vertices}")
        print(f"  Diagonal values: {[L[i][i] for i in absorbing_vertices]}")
        return
    




    while True:
        print("Path query options:")
        print("  1 — Display a specific path")
        print("  2 — Display all shortest paths")
        print("  0 — Return to main menu")
        choice = input("  Your choice: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            start = int(input(f"  Starting vertex (0 to {n-1}): ").strip())
            end = int(input(f"  Ending vertex   (0 to {n-1}): ").strip())
            if 0 <= start < n and 0 <= end < n:
                display_path(P, L, start, end, n)
            else:
                print(f"  [!] Vertices must be between 0 and {n-1}.")
        elif choice == "2":
            display_all_paths(P, L, n)
        else:
            print("  [!] Invalid choice. Please enter 0, 1, or 2.")
        print()






