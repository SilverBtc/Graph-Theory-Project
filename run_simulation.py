import os
import math
import sys
from src.graph import (
    load_graph,
    build_value_matrix,
    has_absorbing_circuit,
    get_all_shortest_paths,
    list_available_graphs,
    INF,
)


def _format_cell(value, empty_symbol="—"):
    if value == INF:
        return "INF"
    if value is None:
        return empty_symbol
    return str(value)


def format_matrix(matrix, title, row_label="From", col_label="To", empty_symbol="—", max_display_size=30):
    n = len(matrix)
    if n == 0:
        return f"{title}\n  (empty matrix)\n"

    if n > max_display_size:
        return f"{title}\n  (Matrix of size {n}x{n} is too large to display in this report.)\n"

    body = [[_format_cell(matrix[i][j], empty_symbol) for j in range(n)] for i in range(n)]
    row_header_width = max(len(str(row_label)), len(str(n - 1)), 2)
    col_width = max(3, max(len(cell) for row in body for cell in row), len(str(n - 1)), 3)

    lines = []
    lines.append(f"{title}")
    header = " " * (row_header_width + 3) + f"{col_label:>{col_width}} "
    header += " ".join(f"{j:>{col_width}}" for j in range(n))
    lines.append(header)
    lines.append(" " * (row_header_width + 3) + "-" * (len(header) - (row_header_width + 3)))

    for i in range(n):
        row_values = " ".join(f"{body[i][j]:>{col_width}}" for j in range(n))
        lines.append(f"{row_label:>{row_header_width}} {i:>2} | {row_values}")

    return "\n".join(lines) + "\n"


def floyd_warshall_with_trace(L0, n):
    L = [row[:] for row in L0]

    P = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and L[i][j] != INF:
                P[i][j] = i

    steps = [(0, [row[:] for row in L], [row[:] for row in P], None)]

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
        steps.append((k + 1, [row[:] for row in L], [row[:] for row in P], k))

    return L, P, steps

def run_simulation():
    graph_dir = "graphs"
    output_file = "simulation_results.txt"
    files = list_available_graphs(graph_dir)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("Floyd-Warshall Simulation Report\n")
        out.write("=" * 60 + "\n\n")

        for index, f_name in enumerate(files, start=1):
            filepath = os.path.join(graph_dir, f_name)
            out.write(f"--- Graph #{index}: {f_name} ---\n")
            
            try:
                n, arcs = load_graph(filepath)
                out.write("Step 1: Graph selected by number.\n")
                out.write("Step 2: Graph loaded from file.\n")
                out.write("Step 3: Processing now uses in-memory structures only.\n")
                out.write(f"Vertices: {n}\n")
                out.write(f"Arcs: {len(arcs)}\n\n")

                L0 = build_value_matrix(n, arcs)
                out.write(format_matrix(L0, "Step 4: L^0 (value matrix)", row_label="From", col_label="To"))
                out.write("\n")

                out.write("Step 5: Floyd-Warshall intermediate matrices (L and P).\n\n")
                L, P, steps = floyd_warshall_with_trace(L0, n)
                for step_number, L_step, P_step, k_used in steps:
                    if step_number == 0:
                        out.write(format_matrix(L_step, "L^0 (Initial value matrix)", row_label="From", col_label="To"))
                        out.write("\n")
                        out.write(format_matrix(P_step, "P^0 (Initial predecessor matrix)", row_label="From", col_label="To", empty_symbol="∅"))
                        out.write("\n")
                    else:
                        out.write(format_matrix(
                            L_step,
                            f"L^{step_number} (after allowing intermediate vertex {k_used})",
                            row_label="From",
                            col_label="To",
                        ))
                        out.write("\n")
                        out.write(format_matrix(
                            P_step,
                            f"P^{step_number} (after allowing intermediate vertex {k_used})",
                            row_label="From",
                            col_label="To",
                            empty_symbol="∅",
                        ))
                        out.write("\n")

                absorbing = has_absorbing_circuit(L, n)

                out.write("Step 6: Absorbing circuit check.\n")
                if absorbing:
                    out.write("Absorbing circuit detected! Shortest paths are not well-defined.\n")
                else:
                    out.write("No absorbing circuit detected.\n")
                    out.write("\n")

                    out.write(format_matrix(L, "Final Distance Matrix (L)", row_label="From", col_label="To"))
                    out.write("\n")
                    out.write(format_matrix(P, "Final Predecessor Matrix (P)", row_label="From", col_label="To", empty_symbol="∅"))
                    out.write("\n")

                    out.write("Step 7: Minimum-value paths.\n")
                    out.write("Shortest Paths:\n")
                    all_paths = get_all_shortest_paths(P, L, n)
                    
                    limit = 1000
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
