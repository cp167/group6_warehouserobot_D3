def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _remaining(state, env):
    return env.all_item_ids - state.D


# h1 - nearest delivery
def h1(state, env):
    remaining = _remaining(state, env)

    if len(remaining) == 0 and state.c == 0:
        return 0

    if state.c != 0:
        return manhattan(state.p, env.depot)

    best = float('inf')
    for iid in remaining:
        loc = env.item_locations[iid]
        cost = manhattan(state.p, loc) + manhattan(loc, env.depot)
        best = min(best, cost)
    return best


# h2 - MST-based
def _mst_cost(points):
    if len(points) <= 1:
        return 0

    n = len(points)
    in_tree = [False] * n
    cheapest = [float('inf')] * n
    cheapest[0] = 0
    total = 0

    for _ in range(n):
        u = -1
        for i in range(n):
            if not in_tree[i] and (u == -1 or cheapest[i] < cheapest[u]):
                u = i

        in_tree[u] = True
        total += cheapest[u]

        for v in range(n):
            if not in_tree[v]:
                d = manhattan(points[u], points[v])
                cheapest[v] = min(cheapest[v], d)

    return total


def h2(state, env):
    remaining = _remaining(state, env)

    if len(remaining) == 0 and state.c == 0:
        return 0

    pts = [env.depot]
    for iid in remaining:
        pts.append(env.item_locations[iid])

    mst = _mst_cost(pts)

    if state.c != 0:
        return manhattan(state.p, env.depot) + mst
    else:
        entry = min(manhattan(state.p, env.item_locations[iid]) for iid in remaining)
        return entry + mst


def get_heuristic(name):
    if name == "h1": return h1
    elif name == "h2": return h2
    elif name == "none": return lambda s, e: 0
    else: raise ValueError(f"Unknown heuristic: {name}")
