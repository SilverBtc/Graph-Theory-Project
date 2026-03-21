import os
import sys
import argparse

from src.graph import list_available_graphs, process_graph

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


def run_cli():
    GRAPH_DIR = "graphs"
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

        try:
            idx = int(user_input)
            if 1 <= idx <= len(files):
                filepath = os.path.join(GRAPH_DIR, files[idx - 1])
                process_graph(filepath)
            else:
                clear_screen()
                display_banner()
                print(f"  [!] Invalid number. Choose between 1 and {len(files)}.\n")
                continue
        except ValueError:
            clear_screen()
            display_banner()
            print("  [!] Invalid input. Please enter a number.\n")
            continue

        print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Floyd-Warshall Shortest Path Solver")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        try:
            from gui import App
            app = App()
            app.mainloop()
        except ImportError as e:
            print(f"Error loading GUI: {e}")
            print("Falling back to CLI mode...")
            run_cli()
        except Exception as e:
            print(f"An error occurred: {e}")
            run_cli()


if __name__ == "__main__":
    main()
