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







