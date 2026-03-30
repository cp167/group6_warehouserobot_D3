import time
import sys
from ..state import is_goal
from ..actions import get_successors

def ida_star(initial_state, env, heuristic_fn, heuristic_name="h", max_nodes=2000000):
    start_time = time.time()
    stats = {"expanded": 0, "generated": 0, "max_depth": 0}
    exploration_order = []

    threshold = heuristic_fn(initial_state, env)
    solution = {"path": None, "cost": float('inf')}

    def dfs(state, g, threshold, path, path_set, transposition):
        if stats["expanded"] >= max_nodes:
            return float('inf')

        f = g + heuristic_fn(state, env)
        if f > threshold:
            return f

        if state in transposition and transposition[state] <= g:
            return float('inf')
        transposition[state] = g

        stats["expanded"] += 1
        if len(path) > stats["max_depth"]:
            stats["max_depth"] = len(path)
        exploration_order.append((state, 'expanded'))

        if is_goal(state, env.all_item_ids):
            solution["path"] = list(path)
            solution["cost"] = g
            return "FOUND"

        min_over_threshold = float('inf')

        for action, next_state, cost in get_successors(state, env):
            stats["generated"] += 1
            new_g = g + cost

            if next_state in path_set:
                continue
            if next_state in transposition and transposition[next_state] <= new_g:
                continue

            path.append((action, next_state))
            path_set.add(next_state)

            result = dfs(next_state, new_g, threshold, path, path_set, transposition)

            if result == "FOUND":
                return "FOUND"
            if result < min_over_threshold:
                min_over_threshold = result

            path.pop()
            path_set.discard(next_state)

        return min_over_threshold

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 10000))

    iteration = 0
    while threshold < float('inf') and stats["expanded"] < max_nodes:
        iteration += 1
        transposition = {}
        path_set = {initial_state}

        result = dfs(initial_state, 0, threshold, [], path_set, transposition)

        if result == "FOUND":
            if solution["path"]:
                for action, s in solution["path"]:
                    exploration_order.append((s, 'solution'))
            sys.setrecursionlimit(old_limit)
            return {
                "solution": solution["path"], "cost": solution["cost"],
                "nodes_expanded": stats["expanded"],
                "nodes_generated": stats["generated"],
                "max_frontier_size": stats["max_depth"],
                "time": time.time() - start_time,
                "algorithm": f"IDA*({heuristic_name})",
                "iterations": iteration,
                "exploration_order": exploration_order,
            }

        if result == float('inf'):
            break

        threshold = result

        if time.time() - start_time > 300:
            break  # 5 min timeout

    sys.setrecursionlimit(old_limit)
    return {
        "solution": None, "cost": float('inf'),
        "nodes_expanded": stats["expanded"],
        "nodes_generated": stats["generated"],
        "max_frontier_size": stats["max_depth"],
        "time": time.time() - start_time,
        "algorithm": f"IDA*({heuristic_name})",
        "iterations": iteration,
        "exploration_order": exploration_order,
    }
