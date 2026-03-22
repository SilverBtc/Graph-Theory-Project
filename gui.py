import os
import math
import json # NEW import
import webbrowser # NEW import
import customtkinter as ctk
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import folium # NEW import needed here too

# Assuming your src package structure is correct
from src.graph import (
    list_available_graphs, load_graph, build_value_matrix, 
    floyd_warshall, has_absorbing_circuit, reconstruct_path, 
    get_all_shortest_paths, display_matrix, INF
)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Graph Theory - Shortest Path Solver")
        self.geometry("1200x800")
        self.graph_dir = "graphs"
        self.current_graph_data = None
        self.fw_results = None
        self.gps_coords = None # NEW state to hold Villejuif coordinates

        # UI Setup remains identical to previous response...
        # [Skipping setup code for brevity, assume same as before]
        # (Grid config, sidebar, main frame, tabview, setups...)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Graph Theory", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.graph_listbox = ctk.CTkScrollableFrame(self.sidebar_frame, width=180, height=300)
        self.graph_listbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.refresh_button = ctk.CTkButton(self.sidebar_frame, text="Refresh List", command=self.load_graph_list)
        self.refresh_button.grid(row=3, column=0, padx=20, pady=10)
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=6, column=0, padx=20, pady=10)
        self.appearance_mode_optionmenu.set("Dark")
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.header_label = ctk.CTkLabel(self.main_frame, text="Select a graph to begin", font=ctk.CTkFont(size=18))
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

    # Re-using identical setup methods from previous response...
    def setup_info_tab(self):
        self.info_tab = self.tabview.tab("Information")
        self.info_tab.grid_columnconfigure(0, weight=1)

        self.stats_label = ctk.CTkLabel(self.info_tab, text="No graph loaded", justify="left")
        self.stats_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.external_viz_button = ctk.CTkButton(self.info_tab, text="Open Interactive View (Browser)", command=self.open_external_viz, state="disabled")
        self.external_viz_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.run_fw_button = ctk.CTkButton(self.info_tab, text="Run Floyd-Warshall", command=self.run_floyd_warshall, state="disabled")
        self.run_fw_button.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.status_label = ctk.CTkLabel(self.info_tab, text="", text_color="orange")
        self.status_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

    def setup_viz_tab(self):
        self.viz_tab = self.tabview.tab("Visualization")
        self.viz_tab.grid_columnconfigure(0, weight=1)
        self.viz_tab.grid_rowconfigure(0, weight=1)
        self.fig, self.ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_tab)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))
        self.toolbar_frame = ctk.CTkFrame(self.viz_tab, height=40)
        self.toolbar_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def setup_matrices_tab(self):
        self.matrices_tab = self.tabview.tab("Matrices")
        self.matrices_tab.grid_columnconfigure(0, weight=1)
        self.matrices_tab.grid_rowconfigure(1, weight=1)
        self.matrix_selector = ctk.CTkOptionMenu(self.matrices_tab, values=["Initial Matrix (L0)", "Final Distance Matrix (L)", "Predecessor Matrix (P)"], command=self.update_matrix_display)
        self.matrix_selector.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.matrix_selector.set("Initial Matrix (L0)")
        self.matrix_text = ctk.CTkTextbox(self.matrices_tab, font=ctk.CTkFont(family="Courier", size=12))
        self.matrix_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    def setup_queries_tab(self):
        self.queries_tab = self.tabview.tab("Path Queries")
        self.queries_tab.grid_columnconfigure(1, weight=1)
        self.queries_tab.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(self.queries_tab, text="Start Vertex:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.start_entry = ctk.CTkEntry(self.queries_tab, placeholder_text="e.g. 0")
        self.start_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(self.queries_tab, text="End Vertex:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.end_entry = ctk.CTkEntry(self.queries_tab, placeholder_text="e.g. 5")
        self.end_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        self.query_button = ctk.CTkButton(self.queries_tab, text="Find Shortest Path", command=self.query_path, state="disabled")
        self.query_button.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.all_paths_button = ctk.CTkButton(self.queries_tab, text="Show All Shortest Paths", command=self.show_all_paths, state="disabled")
        self.all_paths_button.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        self.query_result_text = ctk.CTkTextbox(self.queries_tab, font=ctk.CTkFont(family="Courier", size=12))
        self.query_result_text.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    def load_graph_list(self):
        for widget in self.graph_listbox.winfo_children(): widget.destroy()
        files = list_available_graphs(self.graph_dir)
        for f in files:
            btn = ctk.CTkButton(self.graph_listbox, text=f, fg_color="transparent", text_color=("gray10", "gray90"), anchor="w", command=lambda x=f: self.select_graph(x))
            btn.pack(fill="x", padx=5, pady=2)

    def select_graph(self, filename):
        filepath = os.path.join(self.graph_dir, filename)
        try:
            n, arcs = load_graph(filepath)
            L0 = build_value_matrix(n, arcs)
            self.current_graph_data = {"name": filename, "n": n, "arcs": arcs, "L0": L0}
            self.fw_results = None
            self.gps_coords = None # Reset coordinates
            
            # --- NEW Logic to detect Villejuif and load GPS Index ---
            if filename == "villejuif.txt":
                coords_file = os.path.join(self.graph_dir, "villejuif_coords.json")
                if os.path.exists(coords_file):
                    try:
                        with open(coords_file, 'r') as f:
                            # JSON keys are strings, convert back to int keys for mapping
                            str_coords = json.load(f)
                            self.gps_coords = {int(k): v for k, v in str_coords.items()}
                        self.status_label.configure(text="Villejuif loaded with GPS mapping.", text_color="green")
                    except Exception as e:
                        self.status_label.configure(text=f"Error loading GPS index: {e}", text_color="orange")
                else:
                    self.status_label.configure(text="Villejuif loaded, but 'villejuif_coords.json' is missing. Geographical viz disabled.", text_color="orange")
            # --------------------------------------------------------

            self.header_label.configure(text=f"Selected Graph: {filename}")
            self.stats_label.configure(text=f"Vertices: {n}\nArcs: {len(arcs)}")
            self.external_viz_button.configure(state="normal")
            self.run_fw_button.configure(state="normal")

            self.status_label.configure(text="Graph loaded. Ready to run Floyd-Warshall.", text_color="green")
            
            self.draw_graph_in_canvas()
            self.matrix_selector.set("Initial Matrix (L0)")
            self.update_matrix_display()
            self.tabview.set("Information")
            self.query_result_text.delete("1.0", "end")
            self.query_button.configure(state="disabled")
            self.all_paths_button.configure(state="disabled")

        except Exception as e:
            self.status_label.configure(text=f"Error loading graph: {e}", text_color="red")
    
    def show_all_paths(self):
        if not self.fw_results or self.fw_results["absorbing"]:
            return

        n = self.current_graph_data["n"]
        results = get_all_shortest_paths(self.fw_results["P"], self.fw_results["L"], n)
        
        self.query_result_text.delete("1.0", "end")
        text = "All Shortest Paths:\n" + "-"*30 + "\n"
        
        # On limite l'affichage si le graphe est immense (comme Villejuif) pour ne pas faire crasher l'UI
        limit = 1000 
        count = 0
        
        for start, end, path, cost in results:
            if count > limit:
                text += f"\n... Display limited to first {limit} paths to prevent UI lag. Use exact query for others."
                break
            if path:
                text += f"[{start} -> {end}] Cost: {cost} | Path: {' -> '.join(map(str, path))}\n"
                count += 1
            
        self.query_result_text.insert("1.0", text)
        self.status_label.configure(text="All paths displayed.", text_color="green")

    # Identical draw logic (NetworkX style, but keeping color/zoom support)
    def draw_graph_in_canvas(self):
        if not self.current_graph_data: return
        self.ax.clear()
        n = self.current_graph_data["n"]
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = '#2b2b2b' if is_dark else '#dbdbdb'
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        G = nx.DiGraph()
        for u, v, w in self.current_graph_data["arcs"]: G.add_edge(u, v, weight=w)
        show_labels = n <= 50
        node_size = 600 if show_labels else 20
        pos = nx.spring_layout(G, seed=42)
        edges = G.edges(data=True)
        weights = [data['weight'] for u, v, data in edges]
        if weights:
            min_w, max_w = min(weights), max(weights)
            cmap = plt.cm.RdYlGn_r 
            if min_w == max_w: edge_colors = ['green' for _ in weights]; edge_widths = [1.5 for _ in weights]
            else:
                norm = mcolors.Normalize(vmin=min_w, vmax=max_w)
                edge_colors = [cmap(norm(w)) for w in weights]
                edge_widths = [1.0 + (w - min_w) / (max_w - min_w) * 2.5 for w in weights]
        else: edge_colors = ['white' if is_dark else 'black']; edge_widths = [1.5]
        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color='#1f6aa5', node_size=node_size)
        if show_labels:
            nx.draw_networkx_labels(G, pos, ax=self.ax, font_color='white', font_size=10)
        nx.draw_networkx_edges(G, pos, ax=self.ax, edge_color=edge_colors, width=edge_widths, arrows=True, connectionstyle='arc3,rad=0.1')
        self.ax.axis('off')
        self.canvas.draw()

    def open_external_viz(self):
        if self.current_graph_data:
            try:
                display_matrix(self.current_graph_data["arcs"], self.current_graph_data["n"])
                self.status_label.configure(text="Interactive view opened in browser.", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Visualization error: {e}", text_color="red")

    # Floyd-Warshall run logic remains identical...
    def run_floyd_warshall(self):
        if self.current_graph_data:
            L, P = floyd_warshall(self.current_graph_data["L0"], self.current_graph_data["n"])
            absorbing = has_absorbing_circuit(L, self.current_graph_data["n"])
            self.fw_results = {"L": L, "P": P, "absorbing": absorbing}
            if absorbing:
                self.status_label.configure(text="Absorbing circuit detected!", text_color="red")
                self.query_button.configure(state="disabled")
                self.all_paths_button.configure(state="disabled")
            else:
                self.status_label.configure(text="Floyd-Warshall completed successfully.", text_color="green")
                self.query_button.configure(state="normal")
                self.all_paths_button.configure(state="normal")
            self.matrix_selector.set("Final Distance Matrix (L)")
            self.update_matrix_display()
            self.tabview.set("Matrices")

    # Identical matrix display logic...
    def update_matrix_display(self, choice=None):
        if not self.current_graph_data: return
        choice = choice or self.matrix_selector.get()
        self.matrix_text.delete("1.0", "end")
        matrix = self.current_graph_data["L0"] if choice == "Initial Matrix (L0)" else None
        if self.fw_results and choice != "Initial Matrix (L0)":
            matrix = self.fw_results["L"] if choice == "Final Distance Matrix (L)" else self.fw_results["P"]
        if matrix:
            text = ""
            for row in matrix: text += " ".join(f"{str(x) if x is not None and x != INF else 'INF':>5}" for x in row) + "\n"
            self.matrix_text.insert("1.0", text)

    # =========================================================
    # MAJOR UPDATE: Query Path and Geographical Visualization
    # =========================================================
    def query_path(self):
        if not self.fw_results or self.fw_results["absorbing"]: return
        self.status_label.configure(text="") # Clear old status

        try:
            start = int(self.start_entry.get())
            end = int(self.end_entry.get())
            n = self.current_graph_data["n"]

            if 0 <= start < n and 0 <= end < n:
                path, cost = reconstruct_path(self.fw_results["P"], self.fw_results["L"], start, end, n)
                self.query_result_text.delete("1.0", "end")
                
                if path:
                    # 1. Update Text UI
                    res = f"Shortest path (Floyd-Warshall) from {start} to {end}:\n"
                    res += " -> ".join(map(str, path)) + "\n"
                    res += f"Total Cost: {cost}"
                    self.query_result_text.insert("1.0", res)
                    self.status_label.configure(text="Path found.", text_color="green")

                    # 2. Geographically visualize if Villejuif & Coordinates loaded
                    if self.current_graph_data["name"] == "villejuif.txt" and self.gps_coords:
                        self.status_label.configure(text="Generating geographical visualization...", text_color="orange")
                        self.update() # Force update so user sees the message
                        self.generate_geographical_path_map(path, start, end)
                    
                else:
                    self.query_result_text.insert("1.0", f"No path found from {start} to {end}.")
            else:
                self.query_result_text.delete("1.0", "end")
                self.query_result_text.insert("1.0", f"Error: Vertices must be between 0 and {n-1}.")
        except ValueError:
            self.query_result_text.delete("1.0", "end")
            self.query_result_text.insert("1.0", "Error: Valid integers required.")

    # NEW METHOD to generate the localized violet path map
    def generate_geographical_path_map(self, path_nodes, start_id, end_id):
        try:
            # 1. Gather GPS points for the path
            path_coords = []
            for node_id in path_nodes:
                if node_id in self.gps_coords:
                    point = self.gps_coords[node_id]
                    path_coords.append((point['lat'], point['lon']))
                else:
                    raise KeyError(f"Vertex ID {node_id} from Floyd-Warshall result not found in GPS Index.")

            if not path_coords: return

            # 2. Create Map centered on the path
            avg_lat = sum(p[0] for p in path_coords) / len(path_coords)
            avg_lon = sum(p[1] for p in path_coords) / len(path_coords)
            
            # Using basic tile so path stands out
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15, tiles="cartodbpositron")

            # 3. Draw background network faded
            # We add all arcs from graph as background, but make them grey
            for u, v, w in self.current_graph_data["arcs"]:
                if u in self.gps_coords and v in self.gps_coords:
                    p1, p2 = self.gps_coords[u], self.gps_coords[v]
                    folium.PolyLine(
                        locations=[(p1['lat'], p1['lon']), (p2['lat'], p2['lon'])],
                        color="grey", weight=1, opacity=0.3
                    ).add_to(m)

            # 4. Draw the actual calculated Path in VIOLET
            folium.PolyLine(
                locations=path_coords,
                color="violet", # Your request!
                weight=6,       # Thick line
                opacity=1.0,    # Fully opaque
                tooltip=f"Floyd-Warshall Path {start_id}->{end_id}"
            ).add_to(m)

            # 5. Add markers for Start and End
            folium.Marker(path_coords[0], tooltip=f"Start: Vertex {start_id}", icon=folium.Icon(color='green', icon='play')).add_to(m)
            folium.Marker(path_coords[-1], tooltip=f"End: Vertex {end_id}", icon=folium.Icon(color='red', icon='stop')).add_to(m)

            # 6. Save and open
            output_path = "villejuif_shortest_path_result.html"
            m.save(output_path)
            webbrowser.open('file://' + os.path.realpath(output_path))
            self.status_label.configure(text=f"Geographical map opened in browser.", text_color="green")

        except Exception as e:
            self.status_label.configure(text=f"Viz Error: {e}", text_color="red")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        self.draw_graph_in_canvas()

if __name__ == "__main__":
    app = App()
    app.mainloop()