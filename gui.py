import os
import customtkinter as ctk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.graph import (
    list_available_graphs,
    load_graph,
    build_value_matrix,
    floyd_warshall,
    has_absorbing_circuit,
    reconstruct_path,
    get_all_shortest_paths,
    open_graph_html,
    format_matrix,
    INF,
)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Floyd-Warshall Shortest Path Solver")
        self.geometry("1200x800")

        self.graph_dir = "graphs"
        self.current_graph_data = None
        self.fw_results = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Graph Theory",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.graph_list_label = ctk.CTkLabel(
            self.sidebar_frame, text="Available Graphs:", anchor="w"
        )
        self.graph_list_label.grid(row=1, column=0, padx=20, pady=(10, 0))

        self.graph_listbox = ctk.CTkScrollableFrame(
            self.sidebar_frame, width=180, height=300
        )
        self.graph_listbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.refresh_button = ctk.CTkButton(
            self.sidebar_frame, text="Refresh List", command=self.load_graph_list
        )
        self.refresh_button.grid(row=3, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(
            self.main_frame,
            text="Select a graph to begin",
            font=ctk.CTkFont(size=18),
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=10)

        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.tabview.add("Information")
        self.tabview.add("Visualization")
        self.tabview.add("Matrices")
        self.tabview.add("Path Queries")

        self.setup_info_tab()
        self.setup_viz_tab()
        self.setup_matrices_tab()
        self.setup_queries_tab()

        self.load_graph_list()

    def setup_info_tab(self):
        self.info_tab = self.tabview.tab("Information")
        self.info_tab.grid_columnconfigure(0, weight=1)

        self.stats_label = ctk.CTkLabel(
            self.info_tab,
            text="No graph loaded",
            justify="left",
            font=ctk.CTkFont(size=14),
        )
        self.stats_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.external_viz_button = ctk.CTkButton(
            self.info_tab,
            text="Open Interactive View (Browser)",
            command=self.open_external_viz,
            state="disabled",
        )
        self.external_viz_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.run_fw_button = ctk.CTkButton(
            self.info_tab,
            text="Run Floyd-Warshall",
            command=self.run_floyd_warshall,
            state="disabled",
        )
        self.run_fw_button.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.status_label = ctk.CTkLabel(self.info_tab, text="", text_color="orange")
        self.status_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

    def setup_viz_tab(self):
        self.viz_tab = self.tabview.tab("Visualization")
        self.viz_tab.grid_columnconfigure(0, weight=1)
        self.viz_tab.grid_rowconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.fig.patch.set_facecolor("#2b2b2b")
        self.ax.set_facecolor("#2b2b2b")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_tab)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def setup_matrices_tab(self):
        self.matrices_tab = self.tabview.tab("Matrices")
        self.matrices_tab.grid_columnconfigure(0, weight=1)
        self.matrices_tab.grid_rowconfigure(1, weight=1)

        self.matrix_selector = ctk.CTkOptionMenu(
            self.matrices_tab,
            values=["Initial Matrix (L0)"],
            command=self.update_matrix_display,
        )
        self.matrix_selector.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.matrix_selector.set("Initial Matrix (L0)")

        self.matrix_text = ctk.CTkTextbox(
            self.matrices_tab,
            font=ctk.CTkFont(family="Courier", size=12),
        )
        self.matrix_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    def setup_queries_tab(self):
        self.queries_tab = self.tabview.tab("Path Queries")
        self.queries_tab.grid_columnconfigure(1, weight=1)
        self.queries_tab.grid_rowconfigure(3, weight=1)

        self.start_label = ctk.CTkLabel(self.queries_tab, text="Start Vertex:")
        self.start_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.start_entry = ctk.CTkEntry(self.queries_tab, placeholder_text="e.g. 0")
        self.start_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        self.end_label = ctk.CTkLabel(self.queries_tab, text="End Vertex:")
        self.end_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.end_entry = ctk.CTkEntry(self.queries_tab, placeholder_text="e.g. 5")
        self.end_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        self.query_button = ctk.CTkButton(
            self.queries_tab,
            text="Find Shortest Path",
            command=self.query_path,
            state="disabled",
        )
        self.query_button.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.all_paths_button = ctk.CTkButton(
            self.queries_tab,
            text="Show All Shortest Paths",
            command=self.show_all_paths,
            state="disabled",
        )
        self.all_paths_button.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        self.query_result_text = ctk.CTkTextbox(
            self.queries_tab,
            font=ctk.CTkFont(family="Courier", size=12),
        )
        self.query_result_text.grid(
            row=3, column=0, columnspan=2, padx=20, pady=10, sticky="nsew"
        )

    def load_graph_list(self):
        for widget in self.graph_listbox.winfo_children():
            widget.destroy()

        files = list_available_graphs(self.graph_dir)
        for filename in files:
            btn = ctk.CTkButton(
                self.graph_listbox,
                text=filename,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                command=lambda x=filename: self.select_graph(x),
            )
            btn.pack(fill="x", padx=5, pady=2)

    def select_graph(self, filename):
        filepath = os.path.join(self.graph_dir, filename)

        try:
            n, arcs = load_graph(filepath)
            L0 = build_value_matrix(n, arcs)

            self.current_graph_data = {
                "name": filename,
                "n": n,
                "arcs": arcs,
                "L0": L0,
            }
            self.fw_results = None

            self.header_label.configure(text=f"Selected Graph: {filename}")
            self.stats_label.configure(text=f"Vertices: {n}\nArcs: {len(arcs)}")
            self.external_viz_button.configure(state="normal")
            self.run_fw_button.configure(state="normal")
            self.status_label.configure(
                text="Graph loaded. Ready to run Floyd-Warshall.",
                text_color="green",
            )

            self.draw_graph_in_canvas()
            self.refresh_matrix_selector()
            self.matrix_selector.set("Initial Matrix (L0)")
            self.update_matrix_display()
            self.tabview.set("Information")

            self.query_result_text.delete("1.0", "end")
            self.query_button.configure(state="disabled")
            self.all_paths_button.configure(state="disabled")

        except Exception as e:
            self.status_label.configure(text=f"Error loading graph: {e}", text_color="red")

    def draw_graph_in_canvas(self):
        if not self.current_graph_data:
            return

        self.ax.clear()

        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = "#2b2b2b" if is_dark else "#dbdbdb"
        text_color = "white" if is_dark else "black"
        node_color = "#1f6aa5"

        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        G = nx.DiGraph()
        G.add_nodes_from(range(self.current_graph_data["n"]))
        for u, v, w in self.current_graph_data["arcs"]:
            G.add_edge(u, v, weight=w)

        pos = nx.spring_layout(G, seed=42)

        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color=node_color, node_size=600)
        nx.draw_networkx_labels(G, pos, ax=self.ax, font_color="white", font_size=10, font_weight="bold")
        nx.draw_networkx_edges(
            G,
            pos,
            ax=self.ax,
            edge_color=text_color,
            arrows=True,
            arrowsize=20,
            connectionstyle="arc3,rad=0.1",
        )

        edge_labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            ax=self.ax,
            font_color=text_color,
            font_size=8,
            bbox=dict(facecolor=bg_color, edgecolor="none", alpha=0.7),
        )

        self.ax.axis("off")
        self.canvas.draw()

    def open_external_viz(self):
        if not self.current_graph_data:
            return

        try:
            open_graph_html(self.current_graph_data["arcs"], self.current_graph_data["n"])
            self.status_label.configure(
                text="Interactive view opened in browser.",
                text_color="green",
            )
        except Exception as e:
            self.status_label.configure(text=f"Visualization error: {e}", text_color="red")

    def run_floyd_warshall(self):
        if not self.current_graph_data:
            return

        n = self.current_graph_data["n"]
        L0 = self.current_graph_data["L0"]

        L, P, steps = floyd_warshall(L0, n)
        absorbing = has_absorbing_circuit(L, n)

        self.fw_results = {
            "L": L,
            "P": P,
            "steps": steps,
            "absorbing": absorbing,
        }

        self.refresh_matrix_selector()

        if absorbing:
            self.status_label.configure(
                text="Absorbing circuit detected! Paths are not well-defined.",
                text_color="red",
            )
            self.query_button.configure(state="disabled")
            self.all_paths_button.configure(state="disabled")
        else:
            self.status_label.configure(
                text="Floyd-Warshall completed successfully.",
                text_color="green",
            )
            self.query_button.configure(state="normal")
            self.all_paths_button.configure(state="normal")

        self.matrix_selector.set("Final Distance Matrix (L)")
        self.update_matrix_display()
        self.tabview.set("Matrices")

    def refresh_matrix_selector(self):
        options = ["Initial Matrix (L0)"]

        if self.fw_results and "steps" in self.fw_results:
            for step_name, _, _ in self.fw_results["steps"]:
                options.append(f"L ({step_name})")
                options.append(f"P ({step_name})")

            options.append("Final Distance Matrix (L)")
            options.append("Predecessor Matrix (P)")

        self.matrix_selector.configure(values=options)

    def update_matrix_display(self, choice=None):
        self.matrix_text.delete("1.0", "end")

        if not self.current_graph_data:
            return

        choice = choice or self.matrix_selector.get()

        if choice == "Initial Matrix (L0)":
            text = format_matrix(self.current_graph_data["L0"], "Initial Matrix (L0)")
            self.matrix_text.insert("1.0", text)
            return

        if not self.fw_results:
            self.matrix_text.insert("1.0", "Run Floyd-Warshall to see the matrices.")
            return

        if choice == "Final Distance Matrix (L)":
            text = format_matrix(self.fw_results["L"], "Final Distance Matrix (L)")
            self.matrix_text.insert("1.0", text)
            return

        if choice == "Predecessor Matrix (P)":
            text = format_matrix(self.fw_results["P"], "Predecessor Matrix (P)")
            self.matrix_text.insert("1.0", text)
            return

        for step_name, L_step, P_step in self.fw_results["steps"]:
            if choice == f"L ({step_name})":
                self.matrix_text.insert("1.0", format_matrix(L_step, f"L ({step_name})"))
                return
            if choice == f"P ({step_name})":
                self.matrix_text.insert("1.0", format_matrix(P_step, f"P ({step_name})"))
                return

        self.matrix_text.insert("1.0", "Unknown matrix selection.")

    def query_path(self):
        if not self.fw_results or self.fw_results["absorbing"]:
            return

        try:
            start = int(self.start_entry.get())
            end = int(self.end_entry.get())
            n = self.current_graph_data["n"]

            if not (0 <= start < n and 0 <= end < n):
                self.query_result_text.delete("1.0", "end")
                self.query_result_text.insert(
                    "1.0", f"Error: Vertices must be between 0 and {n - 1}."
                )
                return

            path, cost = reconstruct_path(
                self.fw_results["P"],
                self.fw_results["L"],
                start,
                end,
                n,
            )

            self.query_result_text.delete("1.0", "end")
            if path:
                result = (
                    f"Shortest path from {start} to {end}:\n"
                    f"{' -> '.join(map(str, path))}\n"
                    f"Total cost: {cost}"
                )
                self.query_result_text.insert("1.0", result)
            else:
                self.query_result_text.insert("1.0", f"No path found from {start} to {end}.")

        except ValueError:
            self.query_result_text.delete("1.0", "end")
            self.query_result_text.insert(
                "1.0", "Error: Please enter valid integer vertex indices."
            )

    def show_all_paths(self):
        if not self.fw_results or self.fw_results["absorbing"]:
            return

        n = self.current_graph_data["n"]
        results = get_all_shortest_paths(self.fw_results["P"], self.fw_results["L"], n)

        self.query_result_text.delete("1.0", "end")
        text = "All shortest paths:\n" + "-" * 24 + "\n"

        for start, end, path, cost in results:
            if path:
                text += f"{start} -> {end}: {' -> '.join(map(str, path))} (cost: {cost})\n"
            else:
                text += f"{start} -> {end}: No path\n"

        self.query_result_text.insert("1.0", text)

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        self.draw_graph_in_canvas()


if __name__ == "__main__":
    app = App()
    app.mainloop()