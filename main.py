# CS F407: Artificial Intelligence, Group 06
# Chaarvi Pruthi - 2023A7PS0555P
# Aditya Pannu - 2023A7PS0528P
# Dhruv Gupta - 2023A7PS0551P

import argparse
import sys
import os
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.environment import load_environment, easy_case, medium_case, hard_case, generate_warehouse
from src.state import make_initial_state, state_to_string
from src.heuristics import h1, h2
from src.algorithms import ucs, dls, astar, ida_star
from src.compare import run_comparison


ALGO_MAP = {
    'ucs':          lambda i, e: ucs(i, e),
    'dls':          lambda i, e: dls(i, e),
    'astar_h1':     lambda i, e: astar(i, e, h1, "h1"),
    'astar_h2':     lambda i, e: astar(i, e, h2, "h2"),
    'ida_star_h1':  lambda i, e: ida_star(i, e, h1, "h1"),
    'ida_star_h2':  lambda i, e: ida_star(i, e, h2, "h2"),
}

def print_result(result):
    print(f"\n{'='*50}")
    print(f"  Algorithm: {result['algorithm']}")
    print(f"{'='*50}")
    if result["solution"] is None:
        print("  No solution found!")
    else:
        print(f"  Solution cost:   {result['cost']} moves")
        print(f"  Solution length: {len(result['solution'])} steps")
    print(f"  Nodes expanded:  {result['nodes_expanded']}")
    print(f"  Nodes generated: {result['nodes_generated']}")
    print(f"  Max frontier:    {result.get('max_frontier_size', 'N/A')}")
    print(f"  Time:            {result['time']:.4f}s")
    if "iterations" in result:
        print(f"  IDA* iterations: {result['iterations']}")

    if result["solution"]:
        print(f"\n  First 15 steps:")
        for i, (action, state) in enumerate(result["solution"][:15]):
            print(f"    {i+1:3d}. {action:20s} -> {state_to_string(state)}")
        if len(result["solution"]) > 15:
            print(f"    ... ({len(result['solution']) - 15} more)")

def interactive_menu():
    print("\n" + "="*55)
    print("  Warehouse Robot — AI Search Agent")
    print("  CS F407, Group 06")
    print("="*55)

    print("\nTest case:")
    print("  1. Easy       (8x8, 2 items)")
    print("  2. Medium     (10x10, 3 items)")
    print("  3. Hard       (12x12, 5 items)")
    print("  4. Random Easy")
    print("  5. Random Medium")
    print("  6. Random Hard")
    print("  7. Open Interactive Dashboard (browser)")

    ch = input("\nChoice [1-7]: ").strip()
    if ch == '7':
        dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")
        if os.path.exists(dashboard_path):
            webbrowser.open("file://" + dashboard_path)
            print("Dashboard opened in your browser.")
        else:
            print("dashboard.html not found in the project folder.")
        return
    if ch == '1':   env = easy_case()
    elif ch == '2': env = medium_case()
    elif ch == '3': env = hard_case()
    elif ch == '4': env = generate_warehouse('easy')
    elif ch == '5': env = generate_warehouse('medium')
    elif ch == '6': env = generate_warehouse('hard')
    else:
        print("Defaulting to easy.")
        env = easy_case()

    initial = make_initial_state(env.start, env.energy)
    print(f"\n{env}")

    print("\nAlgorithm:")
    print("  1. UCS")
    print("  2. DLS")
    print("  3. A* (h1 — nearest delivery)")
    print("  4. A* (h2 — MST) [recommended]")
    print("  5. IDA* (h1)")
    print("  6. IDA* (h2)")
    print("  7. Run ALL and compare")

    ach = input("\nChoice [1-7]: ").strip()
    algo_names_map = {'1': 'ucs', '2': 'dls', '3': 'astar_h1',
                      '4': 'astar_h2', '5': 'ida_star_h1', '6': 'ida_star_h2'}
    if ach == '7':
        names = list(ALGO_MAP.keys())
    else:
        names = [algo_names_map.get(ach, 'astar_h2')]

    results = []
    for name in names:
        print(f"\nRunning {name}...")
        r = ALGO_MAP[name](initial, env)
        print_result(r)
        results.append(r)


    if len(results) > 1:
        print(f"\n{'='*60}")
        print("  COMPARISON")
        print(f"{'='*60}")
        print(f"{'Algorithm':<20} {'Cost':<8} {'Expanded':<12} {'Time':<10}")
        print("-" * 50)
        for r in results:
            c = str(r['cost']) if r['solution'] else "N/A"
            print(f"{r['algorithm']:<20} {c:<8} {r['nodes_expanded']:<12} {r['time']:<10.4f}")

    best = [r for r in results if r['solution']]
    if not best:
        return

    best_r = min(best, key=lambda r: r['cost'])

    if len(results) > 1:
        print("\nVisualize?")
        print("  1 = Matplotlib (comparison bar charts)")
        print("  n = skip")
        viz = input("Choice: ").strip()
        if viz == '1':
            from src.visualizer_matplotlib import compare_algorithms_chart
            compare_algorithms_chart(results)
    else:
        print("\nVisualize?")
        print("  1 = Pygame (interactive)")
        print("  2 = Matplotlib (solution path image)")
        print("  3 = Matplotlib (step-by-step animation)")
        print("  n = skip")
        viz = input("Choice: ").strip()
        if viz == '1':
            try:
                from src.visualizer_pygame import visualize_pygame
                visualize_pygame(env, best_r)
            except ImportError:
                print("Pygame not installed. pip install pygame")
        elif viz == '2':
            from src.visualizer_matplotlib import visualize_solution
            visualize_solution(env, best_r)
        elif viz == '3':
            from src.visualizer_matplotlib import animate_solution
            animate_solution(env, best_r)


def main():
    parser = argparse.ArgumentParser(description="Warehouse Robot — AI Search Agent")
    parser.add_argument('--config', type=str, help="JSON config file")
    parser.add_argument('--case', choices=['easy', 'medium', 'hard'])
    parser.add_argument('--algo', choices=list(ALGO_MAP.keys()))
    parser.add_argument('--all', action='store_true', help="Run all algorithms")
    parser.add_argument('--compare', action='store_true', help="Full comparison on all cases")
    parser.add_argument('--pygame', action='store_true', help="Launch pygame viz")
    parser.add_argument('--visualize', action='store_true', help="Save matplotlib plots")
    parser.add_argument('--save-dir', type=str, default='results')
    args = parser.parse_args()

    if args.compare:
        run_comparison()
        return

    if not args.config and not args.case:
        if not args.algo and not args.all:
            interactive_menu()
            return
        else:
            print("Need --config or --case")
            sys.exit(1)

    if args.config:
        env, _ = load_environment(args.config)
    else:
        env = {'easy': easy_case, 'medium': medium_case, 'hard': hard_case}[args.case]()

    initial = make_initial_state(env.start, env.energy)
    print(f"{env}")
    print(f"Start: {state_to_string(initial)}")

    names = list(ALGO_MAP.keys()) if args.all else [args.algo or 'astar_h2']

    results = []
    for name in names:
        print(f"\nRunning {name}...")
        r = ALGO_MAP[name](initial, env)
        print_result(r)
        results.append(r)

        if args.visualize:
            from src.visualizer_matplotlib import visualize_solution
            os.makedirs(args.save_dir, exist_ok=True)
            visualize_solution(env, r, save_path=os.path.join(args.save_dir, f"{name}.png"))

    if len(results) > 1:
        print(f"\n{'Algorithm':<20} {'Cost':<8} {'Expanded':<12} {'Time':<10}")
        print("-" * 50)
        for r in results:
            c = str(r['cost']) if r['solution'] else "N/A"
            print(f"{r['algorithm']:<20} {c:<8} {r['nodes_expanded']:<12} {r['time']:<10.4f}")

        if args.visualize:
            from src.visualizer_matplotlib import compare_algorithms_chart
            compare_algorithms_chart(results, os.path.join(args.save_dir, "comparison.png"))

    if args.pygame and results:
        best = min([r for r in results if r['solution']], key=lambda r: r['cost'])
        from src.visualizer_pygame import visualize_pygame
        visualize_pygame(env, best)

if __name__ == '__main__':
    main()
