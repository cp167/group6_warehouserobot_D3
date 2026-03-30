from .state import State

DIRECTIONS = {
    "North": (-1, 0),
    "South": (1, 0),
    "West":  (0, -1),
    "East":  (0, 1),
}


def get_successors(state, env):
    successors = []
    r, c = state.p

    for direction, (dr, dc) in DIRECTIONS.items():
        nr, nc = r + dr, c + dc
        if state.E >= 1 and env.is_valid_cell(nr, nc):
            new = State(p=(nr, nc), c=state.c, D=state.D, E=state.E - 1)
            successors.append((f"Move({direction})", new, 1))

    if state.c == 0:
        for item_id, loc in env.item_locations.items():
            if loc == state.p and item_id not in state.D:
                new = State(p=state.p, c=item_id, D=state.D, E=state.E)
                successors.append((f"Pick({item_id})", new, 0))

    if state.c != 0 and state.p == env.depot:
        new = State(p=state.p, c=0, D=state.D | frozenset([state.c]), E=state.E)
        successors.append(("Drop", new, 0))

    return successors
