import tracemalloc
from .environment import easy_case, medium_case, hard_case
from .state import make_initial_state
from .heuristics import h1, h2
from .algorithms import ucs, dls, astar, ida_star


def _track_memory(func, *args, **kwargs):
    tracemalloc.start()
    result = func(*args, **kwargs)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result["peak_memory_mb"] = peak / (1024 * 1024)
    return result


def run_comparison():
    cases = [("Easy", easy_case()), ("Medium", medium_case()), ("Hard", hard_case())]
    all_results = []

    for name, env in cases:
        print(f"\n{'='*80}")
        print(f"  {name}: {env.N}x{env.N} grid, {len(env.items_info)} items, "
              f"{len(env.obstacles)} obstacles, energy={env.energy}")
        print(f"{'='*80}")

        initial = make_initial_state(env.start, env.energy)
        algos = [
            ("UCS",      lambda i, e: ucs(i, e)),
            (f"DLS(L={env.energy})", lambda i, e: dls(i, e)),
            ("A*(h1)",   lambda i, e: astar(i, e, h1, "h1")),
            ("A*(h2)",   lambda i, e: astar(i, e, h2, "h2")),
            ("IDA*(h1)", lambda i, e: ida_star(i, e, h1, "h1")),
            ("IDA*(h2)", lambda i, e: ida_star(i, e, h2, "h2")),
        ]

        case_results = []
        for aname, fn in algos:
            print(f"  Running {aname}...", end=" ", flush=True)
            try:
                r = _track_memory(fn, initial, env)
                case_results.append((aname, r))
                found = "FOUND" if r.get("solution") else "NOT FOUND"
                print(f"{found} | cost={r['cost']} | expanded={r['nodes_expanded']} | "
                      f"mem={r.get('peak_memory_mb',0):.2f}MB | time={r['time']:.4f}s")
            except Exception as e:
                print(f"ERROR: {e}")
                case_results.append((aname, None))

        all_results.append((name, case_results))

    print(f"\n{'='*120}")
    print("  SUMMARY")
    print(f"{'='*120}")
    print(f"{'Case':<8} {'Algorithm':<18} {'Found':<6} {'Cost':<6} "
          f"{'Expanded':>10} {'Generated':>10} {'Memory(MB)':>10} {'Time(s)':>10}")
    print("-" * 120)
    for case_name, results in all_results:
        for aname, r in results:
            if r is None:
                print(f"{case_name:<8} {aname:<18} ERR")
                continue
            found = 'Yes' if r.get("solution") else 'No'
            cost = str(r['cost']) if r.get("solution") else 'N/A'
            print(f"{case_name:<8} {aname:<18} {found:<6} {cost:<6} "
                  f"{r['nodes_expanded']:>10} {r['nodes_generated']:>10} "
                  f"{r.get('peak_memory_mb',0):>10.2f} {r['time']:>10.4f}")
        print("-" * 120)

    print(f"\n  Key observations:")
    for case_name, results in all_results:
        rd = {n: r for n, r in results if r is not None}
        ucs_r = rd.get("UCS")
        ah2_r = rd.get("A*(h2)")
        ah1_r = rd.get("A*(h1)")

        if ucs_r and ah2_r and ucs_r.get("solution") and ah2_r.get("solution"):
            if ucs_r["cost"] == ah2_r["cost"]:
                print(f"  [{case_name}] UCS and A*(h2) agree on optimal cost: {ucs_r['cost']}")
        if ah1_r and ah2_r and ah1_r.get("solution") and ah2_r.get("solution"):
            print(f"  [{case_name}] A*(h1) expanded {ah1_r['nodes_expanded']}, "
                  f"A*(h2) expanded {ah2_r['nodes_expanded']} — "
                  f"h2 {'dominates' if ah2_r['nodes_expanded'] <= ah1_r['nodes_expanded'] else 'does not dominate'} h1")

    return all_results
