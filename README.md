*This project has been created as part of the 42 curriculum by mzougari.*

# Fly-in 🚁

> Design an efficient drone routing system that navigates multiple drones through connected zones while minimizing simulation turns and handling movement constraints.

---

## Description

**Fly-in** is a Python simulation project that models autonomous drone fleet routing across a graph of interconnected zones. Each zone carries its own movement cost, capacity limit, and type (normal, restricted, priority, or blocked), and each connection between zones can itself be capacity-constrained.

The core challenge is to move all drones from a single start hub to a single end hub in the **fewest possible simulation turns**, while respecting every zone occupancy rule, connection limit, and movement mechanic — and doing so for a fleet of potentially dozens of drones moving in parallel.

The project is implemented in **Python 3.10+**, is fully **object-oriented**, **type-safe** (flake8 + mypy), and provides both a structured simulation log and a colored visual representation of drone movement.

---

## Instructions

### Installation

```bash
make install
```

Installs all required dependencies via pip into a virtual environment.

### Running the simulation

```bash
make run map=maps/your_map.txt
```

Or directly:

```bash
python main.py maps/your_map.txt
```

### Debug mode

```bash
make debug map=maps/your_map.txt
```

Runs the simulation under Python's built-in `pdb` debugger.

### Lint

```bash
make lint
```

Runs `flake8` and `mypy` with the mandatory flags:

```bash
flake8 .
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
        --disallow-untyped-defs --check-untyped-defs
```

Optional strict check:

```bash
make lint-strict
```

### Clean

```bash
make clean
```

Removes `__pycache__`, `.mypy_cache`, and other generated artifacts.

---

## Input Format

Map files follow this structure:

```
nb_drones: 5

start_hub: hub 0 0 [color=green]
end_hub:   goal 10 10 [color=yellow]
hub: roof1     3 4 [zone=restricted color=red]
hub: roof2     6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB   7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]

connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
connection: roof2-goal
```

Zone types and their movement costs:

| Type | Cost (turns) | Notes |
|---|---|---|
| `normal` | 1 | Default |
| `priority` | 1 | Preferred by pathfinding |
| `restricted` | 2 | Drone occupies the edge during transit |
| `blocked` | — | Impassable |

---

## Algorithm Choices & Implementation Strategy

The simulation is built around three layers: **parsing**, **pathfinding**, and **turn-based scheduling**.

### Graph Representation

The zone network is modeled as a custom adjacency-list graph (no external graph libraries). Each `Zone` object holds its type, capacity, current occupants, and connections. Each `Connection` object tracks its `max_link_capacity` and current traversal count.

---

### Pathfinding Algorithms

Three algorithms are available, selectable at runtime or automatically chosen based on map characteristics.

#### 1. Dijkstra's Algorithm (default)

The primary pathfinding algorithm. Applied to the weighted graph where edge weights reflect destination zone types:

- `normal` / `priority` → weight 1
- `restricted` → weight 2
- `blocked` → edge excluded

For each drone, Dijkstra computes the shortest weighted path from start to end. Paths are then fed to the turn scheduler, which dispatches drones across them while respecting all capacity constraints.

**Complexity:** O((V + E) log V) per query, where V = number of zones and E = number of connections.

**Path caching:** once computed, a path is cached and reused for subsequent drones routed over the same topology, avoiding redundant heap operations.

```
Priority Queue (min-heap):
  pop  → zone with lowest cumulative cost
  relax neighbors → update if shorter path found
  push → updated (cost, zone) tuples
```

#### 2. A\* (Heuristic-Guided Search)

An extension of Dijkstra that uses a **Euclidean heuristic** on zone coordinates to guide exploration toward the goal. For maps where coordinates are meaningful (which they always are in this format), A\* visits significantly fewer nodes than plain Dijkstra on large sparse graphs.

**Heuristic:** `h(n) = sqrt((x_goal - x_n)² + (y_goal - y_n)²)`

The heuristic is admissible — it never overestimates — because the minimum turn cost per hop is 1, and Euclidean distance in integer coordinate space lower-bounds the actual hop count. This guarantees A\* finds the optimal path.

**Complexity:** O((V + E) log V) worst case, but typically much faster in practice due to aggressive node pruning.

#### 3. Yen's K-Shortest Paths

Used when multiple drones must be routed simultaneously and the optimal strategy requires distributing them across **disjoint or partially-overlapping paths** to avoid congestion.

Yen's algorithm computes the K loopless shortest paths between start and end. The scheduler then assigns drones to paths greedily — filling the highest-throughput path first, then spilling overflow into the second-best path, and so on.

This is especially effective on bottleneck maps (single-capacity connections), where serializing all drones on the shortest path is suboptimal and a longer parallel route reduces total turns.

**Complexity:** O(KV(V + E)) — acceptable for the map sizes in this project (typically K ≤ 5).

---

### Turn Scheduler

After paths are assigned, the scheduler simulates turn-by-turn execution:

1. Each turn, for every drone still in transit, determine the next zone on its assigned path.
2. Check zone capacity (accounting for drones departing that same turn) and connection capacity.
3. If the move is valid → commit it; if not → the drone waits in place.
4. For restricted zones (2-turn transit), the drone is locked to the connection for one turn and must complete the move on the following turn unconditionally.
5. Output the turn line in `D<ID>-<zone>` format; omit drones that did not move.

The scheduler dispatches drones closer to the goal first within a turn, minimizing cascading blockages.

---

### Complexity Summary

| Component | Complexity |
|---|---|
| Graph construction | O(V + E) |
| Dijkstra (per drone) | O((V + E) log V) |
| A\* (per drone) | O((V + E) log V), faster in practice |
| Yen's K paths | O(KV(V + E)) |
| Turn simulation | O(T × D) — T turns, D drones |
| Path cache lookup | O(1) |

---

## Visual Representation

The simulation provides two complementary visual modes.

### Colored Terminal Output

Each turn is printed with ANSI color codes encoding zone state and drone identity:

- Zone colors are sourced from the `color=` metadata in the map file and mapped to the nearest ANSI escape code.
- Drone identifiers are highlighted to distinguish simultaneous movements on a single turn line.
- Drones mid-transit toward a restricted zone are labeled with their current connection.
- A turn summary header precedes each movement line.

This makes it straightforward to follow drone flow and identify bottlenecks or waiting patterns without a GUI.

### Graphical Interface

An optional graphical mode (pygame or matplotlib) renders the network as a 2D node-edge graph using zone coordinates:

- Zones are drawn as labeled nodes, colored by zone type.
- Active connections are highlighted during traversal.
- Drone positions are animated turn by turn, with each drone shown as a distinct icon moving between nodes.
- Capacity bars on nodes show current vs. maximum occupancy.

Run with:

```bash
python main.py maps/your_map.txt --visual gui
```

---

## Performance Benchmarks

| Map | Drones | Target | Primary Strategy |
|---|---|---|---|
| Linear path | 2 | ≤ 6 turns | Dijkstra, single path |
| Simple fork | 3 | ≤ 6 turns | Dijkstra, two paths |
| Basic capacity | 4 | ≤ 8 turns | Dijkstra + scheduler |
| Dead end trap | 5 | ≤ 15 turns | A\* with backtrack avoidance |
| Circular loop | 6 | ≤ 20 turns | Yen's K paths |
| Priority puzzle | 4 | ≤ 12 turns | A\* with priority bias |
| Maze nightmare | 8 | ≤ 45 turns | Yen's K paths |
| Capacity hell | 12 | ≤ 60 turns | Yen's K + wait scheduling |
| Ultimate challenge | 15 | ≤ 35 turns | Adaptive (all three) |
| The Impossible Dream | 25 | < 45 turns | Yen's K, full parallelism |

---

## Project Structure

```
fly-in/
├── main.py               # Entry point
├── Makefile
├── requirements.txt
├── .gitignore
├── maps/                 # Provided and custom map files
├── src/
│   ├── parser.py         # Input file parser
│   ├── graph.py          # Zone, Connection, Graph classes
│   ├── algorithms/
│   │   ├── dijkstra.py   # Dijkstra's shortest path
│   │   ├── astar.py      # A* with Euclidean heuristic
│   │   └── yen.py        # Yen's K-shortest loopless paths
│   ├── scheduler.py      # Turn-based drone dispatcher
│   ├── simulation.py     # Simulation engine and output formatter
│   └── visualizer.py     # Terminal ANSI + optional GUI renderer
└── tests/
    └── test_*.py         # Unit tests (pytest)
```

---

## Resources

- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [A\* Search Algorithm — Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Yen's K-Shortest Paths — Wikipedia](https://en.wikipedia.org/wiki/Yen%27s_k-shortest_path_algorithm)
- [Python heapq — Priority Queue (min-heap)](https://docs.python.org/3/library/heapq.html)
- [Real Python — Graphs in Python](https://realpython.com/python-graphs/)
- [mypy Documentation](https://mypy.readthedocs.io/en/stable/)
- [flake8 Documentation](https://flake8.pycqa.org/en/latest/)
- [pytest Documentation](https://docs.pytest.org/en/stable/)

**AI Usage:**
AI was used in this project as a learning and design assistant — specifically to clarify complexity trade-offs between Dijkstra, A\*, and Yen's K-shortest paths; to review type annotation patterns for complex generic structures in Python; and to proofread this README. All code was written, understood, and validated by the author.
