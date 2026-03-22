import os
import json
import osmnx as ox
import folium
import networkx as nx

def generate_villejuif_data():
    place_name = "Villejuif, France"
    graphs_dir = "graphs"
    os.makedirs(graphs_dir, exist_ok=True)
    
    print(f"Downloading road network for {place_name}...")
    G = ox.graph_from_place(place_name, network_type="drive")
    
    print("Downloading traffic signals...")
    signals = ox.features_from_place(place_name, tags={"highway": "traffic_signals"})
    
    # Initialize light count (k)
    for u, v, key, data in G.edges(keys=True, data=True):
        data['num_feux'] = 0

    print("Mapping signals to nearest streets...")
    X = signals.geometry.x.values
    Y = signals.geometry.y.values
    nearest_edges = ox.distance.nearest_edges(G, X, Y)
    
    for u, v, key in nearest_edges:
        G[u][v][key]['num_feux'] += 1

    print(f"Number of traffic signals found: {len(signals)}")

    # Apply Formula: Cost = 1 + 2k
    for u, v, key, data in G.edges(keys=True, data=True):
        k = data['num_feux']
        data['weight'] = 1 + (2 * k)

    # Relabel nodes from 0 to N-1
    mapping = {old_id: new_id for new_id, old_id in enumerate(G.nodes())}
    G_mapped = nx.relabel_nodes(G, mapping)

    # =========================================================
    # EXPORT 1: The .txt file for your GUI (SM601I Format)
    # =========================================================
    txt_path = os.path.join(graphs_dir, "villejuif.txt")
    num_nodes = len(G_mapped.nodes)
    
    with open(txt_path, "w") as f:
        f.write(f"{num_nodes}\n")
        f.write(f"{len(G_mapped.edges)}\n")
        for u, v, data in G_mapped.edges(data=True):
            f.write(f"{u} {v} {data['weight']}\n")
    print(f"TXT File saved: {txt_path}")

    # =========================================================
    # EXPORT 2: NEW! Coordinates Index (GPS Bridge)
    # =========================================================
    coords_path = os.path.join(graphs_dir, "villejuif_coords.json")
    coord_index = {}
    for node, data in G_mapped.nodes(data=True):
        coord_index[node] = {"lat": data['y'], "lon": data['x']}
    
    with open(coords_path, "w") as f:
        json.dump(coord_index, f)
    print(f"Coordinates Index saved: {coords_path}")

    # =========================================================
    # EXPORT 3: The General Interactive HTML Map
    # =========================================================
    print("Generating general interactive HTML map...")
    center_lat = sum(data['y'] for node, data in G_mapped.nodes(data=True)) / num_nodes
    center_lon = sum(data['x'] for node, data in G_mapped.nodes(data=True)) / num_nodes
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="cartodbpositron")
    
    for u, v, data in G_mapped.edges(data=True):
        start_coords = (G_mapped.nodes[u]['y'], G_mapped.nodes[u]['x'])
        end_coords = (G_mapped.nodes[v]['y'], G_mapped.nodes[v]['x'])
        
        # Simple color coding based on formula
        k = data['num_feux']
        if k == 0: color = "#28a745" # Green
        elif k == 1: color = "#fd7e14" # Orange
        else: color = "#dc3545" # Red
            
        folium.PolyLine(
            locations=[start_coords, end_coords],
            color=color, weight=2, opacity=0.7,
            tooltip=f"Cost: {data['weight']} (1+2*{k} lights)"
        ).add_to(m)

    for node, data in G_mapped.nodes(data=True):
        folium.CircleMarker(
            location=(data['y'], data['x']), radius=1,
            color="#007bff", fill=True, fillColor="#007bff", fillOpacity=1.0,
            tooltip=f"Vertex ID: {node}"
        ).add_to(m)

    m.save("villejuif_map.html")
    print("General map generated: villejuif_map.html")

if __name__ == "__main__":
    generate_villejuif_data()