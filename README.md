# Warehouse Robot Search Agent

**CS F407: Artificial Intelligence — Group Assignment D3**
**Group 06** 
**Team Members:**  

**Chaarvi Pruthi - 2023A7PS0555P**  

**Aditya Pannu - 2023A7PS0528P**  

**Dhruv Gupta - 2023A7PS0551P**  


## What this is

An intelligent agent that controls a warehouse robot on an NxN grid.
The robot picks up items from known locations and delivers them to a depot,
all while staying within an energy budget. We implement and compare four
search algorithms with two admissible heuristics.

Complexity level: **L3** (multiple items, energy constraints, weighted priorities).

## Algorithms

**Uninformed:**
- **UCS** — expands the cheapest node first. Optimal but memory-heavy.
- **DLS** — depth-first with a cutoff. Uses less memory, but not optimal.

**Informed:**
- **A\*** — uses f(n) = g(n) + h(n). Optimal with admissible heuristic.
- **IDA\*** — iterative deepening A*. O(bd) memory instead of O(b^d).
  NOTE: IDA* struggles on hard — this is expected and documented in our empirical analysis.

**Heuristics (from D1):**
- **h1** — nearest delivery: cost to pick up closest item and bring to depot
- **h2** — MST-based: minimum spanning tree over remaining goals. Dominates h1.

## how to run (terminal)

```bash
pip install -r requirements.txt

# interactive menu
python main.py

# specific case + algorithm
python main.py --case easy --algo astar_h2

# run all algorithms on a case
python main.py --case easy --all

# full comparison across easy/medium/hard
python main.py --compare

# with pygame visualization
python main.py --case easy --algo astar_h2 --pygame

# save matplotlib plots
python main.py --case easy --all --visualize
```

## Project structure

```
├── main.py                  # entry point (menu + CLI)
├── configs/                 # JSON test configs
│   ├── easy.json
│   ├── medium.json
│   └── hard.json
├── src/
│   ├── state.py             # S = (position, carried, delivered, energy)
│   ├── environment.py       # grid world + hardcoded test cases
│   ├── actions.py           # Move/Pick/Drop transitions
│   ├── heuristics.py        # h1 (nearest delivery), h2 (MST)
│   ├── config.py            # pygame display constants
│   ├── compare.py           # empirical comparison module
│   ├── visualizer_pygame.py # interactive pygame visualization
│   ├── visualizer_matplotlib.py  # static plots + bar charts
│   └── algorithms/
│       ├── ucs.py
│       ├── dls.py
│       ├── astar.py
│       └── ida_star.py
├── dashboard.html           # open on browser for easy visualization (game-like)
├── README.md
├── requirements.txt
├── empiricalvalidation.md   # open on browser for the D3 result comparison with the D2 predictions and more (Empirical Validation part) 
└── .gitignore
```


## Acknowledgement

This assignment was completed with the assistance of AI tools, (APIs and open source libraries and tools) for conceptual clarification and structural guidance. All final analysis, derivations, and code were understood, reviewed, and written by us to reflect our own learning.
