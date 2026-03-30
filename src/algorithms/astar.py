import heapq
import time
from ..state import is_goal
from ..actions import get_successors


def astar(initial_state, env, heuristic_fn, heuristic_name="h", max_nodes=500000):
    start_time = time.time()

    counter = 0
    h0 = heuristic_fn(initial_state, env)
    frontier = []
    heapq.heappush(frontier, (h0, counter, 0, initial_state, []))

    explored = set()
    best_g = {initial_state: 0}
    exploration_order = []

    expanded = 0
    generated = 0
    max_frontier = 1

    while frontier:
        if expanded >= max_nodes:
            break

        f, _, g, state, path = heapq.heappop(frontier)

        if state in explored:
            continue

        explored.add(state)
        expanded += 1
        exploration_order.append((state, 'expanded'))

        if is_goal(state, env.all_item_ids):
            for action, s in path:
                exploration_order.append((s, 'solution'))
            return {
                "solution": path, "cost": g,
                "nodes_expanded": expanded, "nodes_generated": generated,
                "max_frontier_size": max_frontier,
                "time": time.time() - start_time,
                "algorithm": f"A*({heuristic_name})",
                "exploration_order": exploration_order,
            }

        for action, next_state, cost in get_successors(state, env):
            generated += 1
            new_g = g + cost

            if next_state not in explored:
                if next_state not in best_g or new_g < best_g[next_state]:
                    best_g[next_state] = new_g
                    h = heuristic_fn(next_state, env)
                    counter += 1
                    heapq.heappush(frontier, (new_g + h, counter, new_g, next_state, path + [(action, next_state)]))
                    max_frontier = max(max_frontier, len(frontier))
                    exploration_order.append((next_state, 'frontier'))

    return {
        "solution": None, "cost": float('inf'),
        "nodes_expanded": expanded, "nodes_generated": generated,
        "max_frontier_size": max_frontier,
        "time": time.time() - start_time,
        "algorithm": f"A*({heuristic_name})",
        "exploration_order": exploration_order,
    }
