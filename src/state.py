from collections import namedtuple

class State(namedtuple("State", ["p", "c", "D", "E"])):
    __slots__ = ()

    def __lt__(self, other):
        return False


def make_initial_state(start_pos, energy):
    return State(
        p=tuple(start_pos),
        c=0,
        D=frozenset(),
        E=energy
    )


def is_goal(state, all_item_ids):
    return state.D == all_item_ids and state.c == 0


def state_to_string(state):
    delivered = sorted(state.D) if state.D else "none"
    carrying = state.c if state.c != 0 else "nothing"
    return f"Pos={state.p}, Carrying={carrying}, Delivered={delivered}, Energy={state.E}"
