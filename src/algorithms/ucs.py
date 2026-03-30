import heapq
import time
from ..state import is_goal
from ..actions import get_successors


def ucs(initial_state, env, max_nodes=500000):
    start_time = time.time()

    counter = 0
    frontier = []
    heapq.heappush(frontier, (0, counter, initial_state, []))

    explored = set()
    best_g = {initial_state: 0}
    exploration_order = []

    expanded = 0
    generated = 0
    max_frontier = 1

    while frontier:
        if expanded >= max_nodes:
            break

        g, _, state, path = heapq.heappop(frontier)

        if state in explored:
            continue

        explored.add(state)
        expanded += 1
        exploration_order.append((state, 'expanded'))

        if is_goal(state, env.all_item_ids):
            for action, s in path:
                exploration_order.append((s, 'solution'))
            return _result(path, g, expanded, generated, max_frontier,
                           time.time() - start_time, "UCS", exploration_order)

        for action, next_state, cost in get_successors(state, env):
            generated += 1
            new_g = g + cost
            if next_state not in explored:
                if next_state not in best_g or new_g < best_g[next_state]:
                    best_g[next_state] = new_g
                    counter += 1
                    heapq.heappush(frontier, (new_g, counter, next_state, path + [(action, next_state)]))
                    max_frontier = max(max_frontier, len(frontier))
                    exploration_order.append((next_state, 'frontier'))

    return _result(None, float('inf'), expanded, generated, max_frontier,
                   time.time() - start_time, "UCS", exploration_order)


def _result(solution, cost, expanded, generated, max_front, elapsed, algo, expl_order):
    return {
        "solution": solution, "cost": cost,
        "nodes_expanded": expanded, "nodes_generated": generated,
        "max_frontier_size": max_front, "time": elapsed,
        "algorithm": algo, "exploration_order": expl_order,
    }
