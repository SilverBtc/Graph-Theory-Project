import os
import osmnx as ox
import folium
import networkx as nx

def generate_villejuif_data():
    place_name = "Villejuif, France"
    print(f"Downloading road network for {place_name}...")
    
    # 1. Get the driving network graph
    G = ox.graph_from_place(place_name, network_type="drive")
    
    print("Downloading traffic signals...")
    # 2. Get traffic lights
    signals = ox.features_from_place(place_name, tags={"highway": "traffic_signals"})
    
    # 3. Initialize the number of lights (k) to 0 for all edges
    for u, v, key, data in G.edges(keys=True, data=True):
        data['num_feux'] = 0

    print("Mapping signals to nearest streets...")
    # 4. Extract GPS coordinates of traffic lights
    X = signals.geometry.x.values
    Y = signals.geometry.y.values
    
    # Find the nearest street for each traffic light
    nearest_edges = ox.distance.nearest_edges(G, X, Y)
    
    for u, v, key in nearest_edges:
        G[u][v][key]['num_feux'] += 1

    # 5. APPLY THE NEW FORMULA: Cost = 1 + 2k
    for u, v, key, data in G.edges(keys=True, data=True):
        k = data['num_feux']
        data['weight'] = 1 + (2 * k)

    # 6. Relabel nodes from 0 to N-1 (Required by the SM601I project)
    mapping = {old_id: new_id for new_id, old_id in enumerate(G.nodes())}
    G_mapped = nx.relabel_nodes(G, mapping)

    # =========================================================
    # EXPORT 1: The .txt file for your GUI and Floyd-Warshall
    # =========================================================
    os.makedirs("graphs", exist_ok=True)
    txt_path = "graphs/villejuif.txt"
    
    num_nodes = len(G_mapped.nodes)
    num_edges = len(G_mapped.edges)
    
    with open(txt_path, "w") as f:
        f.write(f"{num_nodes}\n")
        f.write(f"{num_edges}\n")
        for u, v, data in G_mapped.edges(data=True):
            f.write(f"{u} {v} {data['weight']}\n")
            
    print(f"TXT File saved: {txt_path}")

    # =========================================================
    # EXPORT 2: The Interactive HTML Map (Vertices + Edges)
    # =========================================================
    print("Generating interactive HTML map...")
    
    # Center map on the city
    center_lat = sum(data['y'] for node, data in G_mapped.nodes(data=True)) / num_nodes
    center_lon = sum(data['x'] for node, data in G_mapped.nodes(data=True)) / num_nodes
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="cartodbpositron")
    
    # Draw Edges (Streets)
    for u, v, data in G_mapped.edges(data=True):
        start_coords = (G_mapped.nodes[u]['y'], G_mapped.nodes[u]['x'])
        end_coords = (G_mapped.nodes[v]['y'], G_mapped.nodes[v]['x'])
        
        k = data['num_feux']
        weight = data['weight']
        tooltip_text = f"Cost: {weight} (Formula: 1 + 2*{k} lights)"
        
        # Color coding: Green for fast routes, Red for heavy penalties
        if k == 0:
            color = "#28a745" # Green
            line_weight = 2
        elif k == 1:
            color = "#fd7e14" # Orange
            line_weight = 4
        else:
            color = "#dc3545" # Red
            line_weight = 6
            
        folium.PolyLine(
            locations=[start_coords, end_coords],
            color=color,
            weight=line_weight,
            tooltip=tooltip_text,
            opacity=0.7
        ).add_to(m)

    # Draw Vertices (Intersections)
    for node, data in G_mapped.nodes(data=True):
        folium.CircleMarker(
            location=(data['y'], data['x']),
            radius=2, # Small radius so it doesn't hide the streets
            color="#007bff", # Blue vertices
            fill=True,
            fillColor="#007bff",
            fillOpacity=1.0,
            tooltip=f"Vertex ID: {node}" # Hover to see the exact ID for Floyd-Warshall!
        ).add_to(m)

    map_path = "villejuif_map.html"
    m.save(map_path)
    print(f"Map generated successfully: {map_path}. Open it in your browser!")

if __name__ == "__main__":
    generate_villejuif_data()