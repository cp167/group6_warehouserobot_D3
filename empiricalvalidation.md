# Empirical Validation

## Setup

We ran all six algorithm variants (UCS, DLS, A* with h1 and h2, IDA* with h1 and h2) on our three test cases and recorded nodes expanded, nodes generated, max frontier size, peak memory, and wall-clock time. We then compared these against what we predicted in D2.

Quick recap of the problem parameters:

| Config | Grid | Items (m) | Energy | Optimal cost | State space bound |
|--------|------|-----------|--------|--------------|-------------------|
| Easy   | 8×8  | 2         | 50     | 32           | ~39k              |
| Medium | 10×10| 3         | 100    | 70           | ~323k             |
| Hard   | 12×12| 5         | 200    | 136          | ~5.5M             |

The state space bound comes from our D1 formula: N² × (m+1) × 2^m × (Emax+1). The jump from Easy to Hard is roughly 140x, mostly because of the 2^m term — going from 2 items to 5 items means way more possible delivery-subset combinations.


## Results

| Algorithm | Cost | Expanded | Generated | Max Frontier | Memory | Time   |
|-----------|------|----------|-----------|--------------|--------|--------|
| UCS       | 32   | 2,897    | 9,196     | 212          | 1.2 MB | 0.016s |
| DLS       | 32   | 6,264    | 19,209    | 77           | 1.8 MB | 0.024s |
| A*(h1)    | 32   | 1,380    | 4,394     | 289          | 0.7 MB | 0.008s |
| A*(h2)    | 32   | 1,255    | 3,999     | 306          | 0.7 MB | 0.011s |
| IDA*(h1)  | 32   | 5,663    | 18,011    | 36           | 1.0 MB | 0.029s |
| IDA*(h2)  | 32   | 7,984    | 25,443    | 36           | 1.5 MB | 0.067s |

### Medium (10×10, 3 items)

| Algorithm | Cost | Expanded | Generated | Max Frontier | Memory  |  Time  |
|-----------|------|----------|-----------|--------------|---------|--------|
| UCS       | 70   | 25,830   | 80,405    | 857          | 10.9 MB | 0.133s |
| DLS       | 70   | 48,551   | 148,295   | 107          | 14.7 MB | 0.239s |
| A*(h1)    | 70   | 17,168   | 53,476    | 1,385        | 7.1 MB  | 0.099s |
| A*(h2)    | 70   | 14,737   | 45,949    | 1,415        | 6.3 MB  | 0.135s |
| IDA*(h1)  | 70   | 156,464  | 487,694   | 76           | 30.4 MB | 1.127s |
| IDA*(h2)  | 70   | 223,888  | 699,540   | 76           | 43.3 MB | 4.841s |

### Hard (12×12, 5 items)

| Algorithm | Cost | Expanded | Generated   | Max Frontier | Memory   | Time  |
|-----------|------|----------|-------------|--------------|----------|-------|
| UCS       | 136  | 418,309  | 1,253,758   | 6,939        | 156.6 MB | 4.104s |
| DLS       | 180  | 500,000  | 1,477,575   | 303          | 146.4 MB | 4.294s |
| A*(h1)    | 136  | 337,493  | 1,010,543   | 12,830       | 156.3 MB | 5.233s |
| A*(h2)    | 136  | 251,864  | 754,370     | 13,000       | 104.7 MB | 6.055s |
| IDA*(h1)  | —    | timeout  | —           | —            | —        | —     |
| IDA*(h2)  | —    | timeout  | —           | —            | —        | —     |


## What we found

### Optimality

This one was straightforward to verify. We just checked if the costs match across algorithms that should be optimal.

UCS, A*(h1), and A*(h2) all returned cost 32 on Easy, 70 on Medium, and 136 on Hard. Exactly the same in every case, which is what we expected since all three guarantee optimality (A* because our heuristics are admissible, UCS by definition).

DLS got lucky on Easy and Medium — it happened to find the optimal cost both times. But on Hard it returned 180, while the actual optimal is 136. This makes sense because DLS just does depth-first expansion and returns whatever solution it hits first. It doesn't always find the cheapest one. So the D2 prediction that DLS is not optimal checks out.

### h2 dominates h1

In D1 we proved that h2 ≥ h1 for all states, so A* with h2 should expand fewer nodes. Here's what actually happened:

| Config | A*(h1) expanded | A*(h2) expanded | Reduction |
|--------|-----------------|-----------------|-----------|
| Easy   | 1,380           | 1,255           | ~9%       |
| Medium | 17,168          | 14,737          | ~14%      |
| Hard   | 337,493         | 251,864         | ~25%      |

So, h2 is consistently better. What's interesting is the gap gets bigger as the problem gets harder. On Easy with just 2 items, the MST doesn't add much over the nearest-item estimate. But with 5 items on Hard, the MST captures the cost of connecting all of them, which h1 completely ignores. A 25% reduction in node expansions is pretty significant when we're talking about hundreds of thousands of nodes.

### Space usage — A* vs IDA*

In D2 we said A* stores O(b^d) nodes (the whole frontier and explored set) while IDA* only stores O(b·d) (just the current path). The max frontier numbers tell the story:

On Easy: A*(h2) had max frontier 306, IDA*(h2) had just 36.
On Medium: A*(h2) had 1,415, IDA*(h2) had 76.
On Hard: A*(h2) had 13,000 (and IDA* didn't finish, but its frontier would still be lesser).

IDA*'s frontier stays tiny and grows linearly with depth, while A*'s grows exponentially. This matches the O(b·d) vs O(b^d) prediction.

### DLS space

DLS's max frontier was 77 on Easy, 107 on Medium, 303 on Hard. These are way smaller than UCS or A* because DLS only keeps the current path and its unexplored siblings — it doesn't maintain a priority queue of the entire frontier. This matches our D2 prediction of O(b·L) space.

### IDA* failing on Hard case

IDA* solved Easy and Medium just fine but couldn't finish Hard within our node budget. We spent some time figuring out why, and it comes down to two things working against it:

First, IDA* needs to go through a lot of iterations. It starts at threshold h2 = 44 and needs to climb all the way to the optimal cost 136. Since our move costs are all 1, the threshold goes up by 1 or 2 each iteration. That's roughly 90 iterations, and each one starts the DFS over from scratch.

Second, our problem is a graph, not a tree. The robot can reach the same grid cell through many different paths. IDA* was really designed for tree-shaped search spaces like the 15-puzzle, where there aren't many ways to reach the same state. On a grid, even with the transposition table, a lot of work gets redone across iterations.

For reference, A*(h2) solved Hard with 251,864 total expansions. IDA* would need millions to get through all ~90 iterations with growing work per iteration.

### How node counts scale

From Easy to Hard, UCS expansions went from 2,897 to 418,309 — about 144x. The state space bound went from 39k to 5.5M — about 142x. So the actual growth roughly tracks the state space growth, which makes sense. Both are driven by the 2^m factor.

A*(h2) went from 1,255 to 251,864 — about 200x. It grows a bit faster than UCS in ratio terms, which surprised us at first. But it makes sense: the heuristic is a bigger help on smaller problems where it can rule out more of the search space proportionally. On Hard with lots of obstacles, the Manhattan-based heuristic is a looser bound because the actual paths have to detour around walls.


## Summary table

|      D2 Prediction      | Confirmed? |                   Evidence                  |
|-------------------------|------------|---------------------------------------------|
| UCS is optimal          |    Yes     | Same cost as A* on all configs              |
| DLS is not optimal      |    Yes     | Cost 180 vs optimal 136 on Hard             |
| A* is optimal           |    Yes     | Matches UCS on all configs                  |
| h2 dominates h1         |    Yes     | 9-25% fewer expansions with h2              |
| A*/UCS space is O(b^d)  |    Yes     | Frontier grows to thousands                 |
| IDA* space is O(b·d)    |    Yes     | Frontier stays under 100                    |
| DLS space is O(b·L)     |    Yes     | Frontier stays under 303                    |
| DLS complete when L ≥ d |    Yes     | L = Emax ≥ d* held in all cases             |
| IDA* complete           | In theory  | Timed out on Hard due to iteration overhead |