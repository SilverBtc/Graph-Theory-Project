import os
import argparse

from src.graph import list_available_graphs, process_graph, export_all_traces


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def display_banner():
    clear_screen()
    print()
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║        Floyd-Warshall Algorithm - Shortest Paths            ║")
    print("  ║            SM601I - Graph Theory - 2025/2026               ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print()


def run_cli():
    graph_dir = "graphs"
    display_banner()

    while True:
        files = list_available_graphs(graph_dir)

        print("Available graphs:")
        if files:
            for idx, filename in enumerate(files, start=1):
                print(f"    {idx}. {filename}")
        else:
            print("    (no graph files found)")

        print()
        print("  Enter a graph number to process it")
        print("  Enter T to generate execution traces for all graphs")
        print("  Enter 0 to quit.\n")

        user_input = input("  Graph selection: ").strip()

        if user_input.lower() in ("0", "q", "quit", "exit"):
            print("\n  Goodbye!\n")
            break

        if user_input.lower() in ("t", "trace", "traces"):
            try:
                generated = export_all_traces(graph_dir=graph_dir, output_dir="traces")
                print("\n  Execution traces generated:")
                for path in generated:
                    print(f"    - {path}")
            except Exception as e:
                print(f"\n  [!] Could not generate traces: {e}")
            print("\n" + "=" * 70 + "\n")
            continue

        try:
            idx = int(user_input)
            if 1 <= idx <= len(files):
                filepath = os.path.join(graph_dir, files[idx - 1])
                process_graph(filepath)
            else:
                clear_screen()
                display_banner()
                print(f"  [!] Invalid number. Choose between 1 and {len(files)}.\n")
                continue
        except ValueError:
            clear_screen()
            display_banner()
            print("  [!] Invalid input. Please enter a number, T, or 0.\n")
            continue

        print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Floyd-Warshall Shortest Path Solver")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    if args.cli:
        run_cli()
        return

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
        print("Falling back to CLI mode...")
        run_cli()


if __name__ == "__main__":
    main()