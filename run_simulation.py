import os
import math
import sys
from src.graph import load_graph, build_value_matrix, floyd_warshall, has_absorbing_circuit, get_all_shortest_paths, INF

def format_matrix(matrix, n):
    if n > 30:
        return f"  (Matrix of size {n}x{n} is too large to display in this report.)\n"
    
    text = ""
    for row in matrix:
        text += "  " + " ".join(f"{str(x) if x is not None and x != INF else 'INF':>5}" for x in row) + "\n"
    return text

def run_simulation():
    graph_dir = "graphs"
    output_file = "simulation_results.txt"
    files = sorted(f for f in os.listdir(graph_dir) if f.endswith(".txt"))

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("Floyd-Warshall Simulation Report\n")
        out.write("=" * 60 + "\n\n")

        for f_name in files:
            filepath = os.path.join(graph_dir, f_name)
            out.write(f"--- Processing Graph: {f_name} ---\n")
            
            try:
                n, arcs = load_graph(filepath)
                out.write(f"Vertices: {n}\n")
                out.write(f"Arcs: {len(arcs)}\n\n")

                L0 = build_value_matrix(n, arcs)
                out.write("Initial Matrix (L0):\n")
                out.write(format_matrix(L0, n))
                out.write("\n")

                L, P = floyd_warshall(L0, n)
                absorbing = has_absorbing_circuit(L, n)

                if absorbing:
                    out.write("Absorbing circuit detected! Shortest paths are not well-defined.\n")
                else:
                    out.write("Final Distance Matrix (L):\n")
                    out.write(format_matrix(L, n))
                    out.write("\n")

                    out.write("Predecessor Matrix (P):\n")
                    out.write(format_matrix(P, n))
                    out.write("\n")

                    out.write("Shortest Paths:\n")
                    all_paths = get_all_shortest_paths(P, L, n)
                    
                    limit = 1000 # Limit to prevent file bloat for huge graphs like Villejuif
                    count = 0
                    for start, end, path, cost in all_paths:
                        if count >= limit:
                            out.write(f"... (Display limited to first {limit} paths to prevent file bloat. {len(all_paths)} total paths exist.)\n")
                            break
                        if path:
                            out.write(f"[{start} -> {end}] Cost: {cost} | Path: {' -> '.join(map(str, path))}\n")
                            count += 1
                        else:
                            out.write(f"[{start} -> {end}] No path found.\n")
                            count += 1
                
            except Exception as e:
                out.write(f"Error processing {f_name}: {str(e)}\n")

            out.write("\n" + "=" * 60 + "\n\n")

    print(f"Simulation completed. Results saved to {output_file}")

if __name__ == "__main__":
    run_simulation()
