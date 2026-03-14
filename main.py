import os
import sys
import math

from src.graph import list_available_graphs, process_graph



GRAPH_DIR = "graphs"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display_banner():
    clear_screen()
    """Display the program banner."""
    print()
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║        Floyd-Warshall Algorithm — Shortest Paths             ║")
    print("  ║            SM601I — Graph Theory — 2025/2026                 ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print()


def main():
    display_banner()

    while True:

        files = list_available_graphs(GRAPH_DIR)

        print("Available graphs:")

        if files:
            for idx, f in enumerate(files, 1):
                print(f"    {idx}. {f}")
        else:
            print("    (no graph files found)")

        print()
        print("  Enter a graph number to process it,")
        print("  Enter 0 to quit.\n")

        user_input = input("  Graph selection: ").strip()

        if user_input.lower() in ("0", "q", "quit", "exit"):
            print("\n  Goodbye!\n")
            break

        filepath = None
        idx = int(user_input)
        if 1 <= idx <= len(files):
            filepath = os.path.join(GRAPH_DIR, files[idx - 1])
        else:
            clear_screen()
            display_banner()
            print(f"  [!] Invalid number. Choose between 1 and {len(files)}.\n")
            continue


        if filepath:
            process_graph(filepath)

        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
