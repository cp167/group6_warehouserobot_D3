import time
from ..state import is_goal
from ..actions import get_successors


def dls(initial_state, env, depth_limit=None, max_nodes=500000):
    if depth_limit is None:
        depth_limit = env.energy

    start_time = time.time()
    expanded = 0
    generated = 0
    max_frontier = 1
    exploration_order = []

    stack = [(initial_state, [], 0, 0)]
    visited = {initial_state: 0}

    best_solution = None
    best_cost = float('inf')

    while stack:
        if expanded >= max_nodes:
            break

        state, path, depth, g = stack.pop()
        expanded += 1
        exploration_order.append((state, 'expanded'))

        if is_goal(state, env.all_item_ids):
            if g < best_cost:
                best_cost = g
                best_solution = path
            continue

        if depth >= depth_limit:
            continue

        for action, next_state, cost in get_successors(state, env):
            generated += 1
            nd = depth + 1

            if next_state in visited and visited[next_state] <= nd:
                continue

            visited[next_state] = nd
            stack.append((next_state, path + [(action, next_state)], nd, g + cost))
            max_frontier = max(max_frontier, len(stack))
            exploration_order.append((next_state, 'frontier'))

    elapsed = time.time() - start_time

    if best_solution is not None:
        for action, s in best_solution:
            exploration_order.append((s, 'solution'))

    return {
        "solution": best_solution,
        "cost": best_cost if best_solution else float('inf'),
        "nodes_expanded": expanded, "nodes_generated": generated,
        "max_frontier_size": max_frontier, "time": elapsed,
        "algorithm": f"DLS(L={depth_limit})",
        "exploration_order": exploration_order,
    }
