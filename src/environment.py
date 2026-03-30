import json
import random

class Environment:
    def __init__(self, grid_size, obstacles, items, depot, energy, start=None):
        self.N = grid_size
        self.obstacles = set(map(tuple, obstacles))
        self.depot = tuple(depot)
        self.energy = energy
        self.start = tuple(start) if start else self.depot

        self.items_info = {}
        if isinstance(items, dict):
            for item_id, info in items.items():
                iid = int(item_id)
                self.items_info[iid] = {
                    "location": tuple(info["location"]),
                    "priority": info["priority"]
                }
        elif isinstance(items, list):
            for item_id, row, col, priority in items:
                self.items_info[item_id] = {
                    "location": (row, col),
                    "priority": priority
                }

        self.all_item_ids = frozenset(self.items_info.keys())
        self.item_locations = {iid: info["location"] for iid, info in self.items_info.items()}
        self.item_priorities = {iid: info["priority"] for iid, info in self.items_info.items()}

    def is_valid_cell(self, r, c):
        return 0 <= r < self.N and 0 <= c < self.N and (r, c) not in self.obstacles

    def __repr__(self):
        return (f"Environment(N={self.N}, items={len(self.items_info)}, "
                f"obstacles={len(self.obstacles)}, depot={self.depot}, energy={self.energy})")


def load_environment(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    robot_start = tuple(config["robot_start"])
    env = Environment(
        grid_size=config["grid_size"],
        obstacles=config["obstacles"],
        items=config["items"],
        depot=config["depot"],
        energy=config["energy"],
        start=robot_start
    )
    return env, robot_start

def easy_case():
    return Environment(
        grid_size=8,
        obstacles=[(1,2), (2,2), (3,4), (4,1), (5,5)],
        items=[(1, 2, 5, 1.0), (2, 6, 3, 2.0)],
        depot=(0,0), energy=50, start=(0,0)
    )

def medium_case():
    return Environment(
        grid_size=10,
        obstacles=[(1,3), (2,3), (3,3), (4,6), (5,1), (5,2),
                   (6,6), (7,4), (8,2), (3,7), (1,8), (6,1)],
        items=[(1, 2, 7, 1.0), (2, 5, 5, 3.0), (3, 8, 8, 2.0)],
        depot=(0,0), energy=100, start=(0,0)
    )

def hard_case():
    return Environment(
        grid_size=12,
        obstacles=[(1,2), (1,5), (2,2), (2,8), (3,4), (3,9),
                   (4,1), (4,6), (5,3), (5,7), (5,10), (6,1),
                   (6,5), (7,3), (7,8), (8,6), (9,2), (9,9),
                   (10,4), (10,7)],
        items=[(1, 2, 6, 1.0), (2, 4, 10, 3.0), (3, 7, 1, 2.0),
               (4, 9, 7, 1.0), (5, 11, 11, 2.0)],
        depot=(0,0), energy=200, start=(0,0)
    )

def generate_warehouse(difficulty='easy'):
    cfgs = {
        'easy':   {'size': 8,  'items': 2, 'obs': 5,  'e_mult': 4},
        'medium': {'size': 10, 'items': 3, 'obs': 12, 'e_mult': 3},
        'hard':   {'size': 12, 'items': 5, 'obs': 20, 'e_mult': 3},
    }
    cfg = cfgs[difficulty]
    N = cfg['size']
    depot = (0, 0)
    occupied = {depot}

    obstacles = []
    for _ in range(cfg['obs']):
        for _ in range(100):
            pos = (random.randint(0, N-1), random.randint(0, N-1))
            if pos not in occupied:
                obstacles.append(pos)
                occupied.add(pos)
                break

    items = []
    for i in range(1, cfg['items'] + 1):
        for _ in range(100):
            pos = (random.randint(0, N-1), random.randint(0, N-1))
            if pos not in occupied:
                pri = random.choice([1.0, 2.0, 3.0])
                items.append((i, pos[0], pos[1], pri))
                occupied.add(pos)
                break

    total_dist = sum(abs(r) + abs(c) for _, r, c, _ in items)
    energy = max(int(total_dist * cfg['e_mult']), N * cfg['items'] * 2)

    return Environment(N, obstacles, items, depot, energy, depot)
