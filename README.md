# 🛣️ Graph Theory - Shortest Path Solver

A robust implementation of the **Floyd-Warshall algorithm** to find all-pairs shortest paths in directed graphs. This project features a modern GUI, a CLI interface, and specialized geographical visualization for real-world road networks like Villejuif, France.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Library](https://img.shields.io/badge/customtkinter-5.2.0-blue)
![Library](https://img.shields.io/badge/osmnx-1.9.0-orange)

---

## ✨ Key Features

*   **Floyd-Warshall Implementation:** Efficiently calculates the shortest path between all pairs of vertices.
*   **Absorbing Circuit Detection:** Automatically detects negative cycles (absorbing circuits) that make shortest paths undefined.
*   **Modern GUI:** Built with `CustomTkinter` for a sleek, dark-themed user experience.
*   **Interactive Visualizations:**
    *   **NetworkX/Matplotlib:** View graph topologies directly in the app.
    *   **Folium/OSMnx:** Real-world geographical path rendering for the Villejuif map.
*   **Matrix Analysis:** Inspect Initial (L₀), Distance (L), and Predecessor (P) matrices.
*   **CLI Mode:** Lightweight command-line interface for batch processing.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.12 or higher.
*   Virtual environment (recommended).

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Graph-Theory-Project.git
    cd Graph-Theory-Project
    ```

2.  **Set up the virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/MacOS
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🎮 Usage

### Launching the GUI (Default)
The GUI allows you to select graphs, run the algorithm, view matrices, and visualize paths on a map.
```bash
python main.py
```

### Launching the CLI
Useful for quick analysis without a graphical interface.
```bash
python main.py --cli
```

---

## 🌍 Villejuif Geographical Mode
This project includes a special dataset for the road network of **Villejuif, France**. 
1.  Load `villejuif.txt` in the GUI.
2.  Run the Floyd-Warshall algorithm.
3.  Go to **Path Queries**, enter start/end nodes.
4.  If the path exists, a browser window will automatically open showing the path rendered on a **real map** using Folium (violet path).

---

## 📁 Project Structure
*   `gui.py`: The main graphical interface.
*   `main.py`: Entry point supporting both CLI and GUI.
*   `src/graph.py`: Core logic for Floyd-Warshall and path reconstruction.
*   `graphs/`: Directory containing `.txt` graph files and GPS coordinate data.
*   `Villejuif.py`: Utility script used to generate real-world graph data.

---

## 🛠️ Tech Stack
*   **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
*   **Graph Logic:** [NetworkX](https://networkx.org/)
*   **Geo Data:** [OSMnx](https://osmnx.readthedocs.io/) & [Folium](https://python-visualization.github.io/folium/)
*   **Scientific Computing:** [SciPy](https://scipy.org/) & [NumPy](https://numpy.org/)

---

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

*Developed for SM601I — Graph Theory — 2025/2026*
