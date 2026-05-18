# Fly-in: Drone Flow Simulation System

## Description

**Fly-in** is a Python-based simulation system that models multi-drone pathfinding and scheduling through complex networks. The project visualizes how multiple drones navigate from a start hub to an end hub while respecting hub capacity constraints, edge weights, and turn-based movement mechanics.

This system demonstrates advanced pathfinding algorithms, discrete event simulation, and interactive visualization. It's designed to explore solutions for drone fleet management in constrained network environments—applicable to warehouse automation, delivery services, and multi-agent logistics systems.

### Key Features
- **K-Shortest Paths Algorithm**: Finds multiple alternative paths from start to end hub
- **Intelligent Drone Allocation**: Distributes drones evenly across available paths to minimize congestion
- **Hub Capacity Management**: Enforces maximum concurrent drone occupancy at each hub
- **Turn-Based Simulation**: Realistic discrete-time movement and scheduling
- **Interactive Visualization**: Real-time pygame-based rendering with manual step and auto-play modes

---

## Instructions

### Prerequisites
- Python 3.12+
- pip package manager

### Installation

1. Clone or extract the project:
   ```bash
   cd Fly-in
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   make install
   # Or manually: pip install -r requirements.txt
   ```

### Running the Simulation

Execute the simulation with a map file:
```bash
python3 main.py maps/easy/01_linear_path.txt
```

Or use the makefile target (defaults to medium difficulty):
```bash
make run
```

### Available Map Files

The `maps/` directory contains test scenarios of varying difficulty:

**Easy Level:**
- `maps/easy/01_linear_path.txt` - Single straight path
- `maps/easy/02_simple_fork.txt` - Two alternative paths
- `maps/easy/03_basic_capacity.txt` - Hub capacity constraints

**Medium Level:**
- `maps/medium/01_dead_end_trap.txt` - Backtracking challenge
- `maps/medium/02_circular_loop.txt` - Multi-cycle network
- `maps/medium/03_priority_puzzle.txt` - Complex path prioritization

**Hard Level:**
- `maps/hard/01_maze_nightmare.txt` - Large complex network
- `maps/hard/02_capacity_hell.txt` - Strict capacity constraints
- `maps/hard/03_ultimate_challenge.txt` - Combined complexity

**Challenger Level:**
- `maps/challenger/01_the_impossible_dream.txt` - Maximum difficulty

### Interactive Controls

Once the visualization window opens:

| Key | Action |
|-----|--------|
| **SPACE** | Step one simulation turn (manual mode) or pause/resume (auto-play) |
| **M** | Toggle between manual stepping and continuous auto-play |
| **Close Window** | Exit the simulation |

The status bar displays current turn count and simulation state.

### Code Quality

Run linting and type checking:
```bash
make lint 
make lint-strict
make clean      
```

---

## Algorithm Explanation

### K-Shortest Paths Pathfinding

The `Algos.k_shortest_path()` method implements a modified **Dijkstra-based K-shortest paths algorithm** to find up to 6 alternative routes from start to end hub.

**Algorithm Overview:**
1. Build an adjacency graph from map edges with weights
2. Initialize a min-heap with the start hub (cost=0, path=[start_hub])
3. Extract minimum-cost paths from heap, adding unvisited neighbors
4. Track visited complete paths to avoid duplicates
5. Stop when 6 distinct paths are discovered or heap exhausted

**Design Decisions:**
- **Heap-based**: $O(k \cdot E \log V)$ complexity where $k=6$ (bounded paths)
- **K=6 limit**: Balances path diversity vs. computation time
- **Non-simple paths prevented**: `if nei not in path` ensures no cycles
- **Visited tracking**: Tuple-based set prevents exploring identical paths multiple times

### Drone Allocation Strategy

The `Algos.allocate_drones_to_paths()` method uses **round-robin distribution** to spread drones evenly:
- Assign drone 1 to path 0, drone 2 to path 1, ..., drone N to path (N-1) % num_paths
- **Benefit**: Balances network load and reduces congestion
- **Alternative approaches considered**: Random allocation (unpredictable), greedy-by-path-length (computationally expensive)

### Turn-Based Simulation Engine

The `Simulation` class implements discrete-time movement:

**Simulation Loop:**
1. **launch_drones()**: Check start hub capacity; move waiting drones into network
2. **move_drones()**: Advance each active drone one step along its path
3. **hub occupancy tracking**: Decrement `hub_occupancy[hub]` when drones leave
4. **arrival detection**: Mark drones as arrived when reaching end hub
5. **Increment turn counter**: Move to next discrete time unit

**Hub Capacity Constraint:**
- Each hub has `max_drones`: maximum concurrent occupancy
- Drones cannot enter a hub if occupancy is at max
- Drones in queue wait until space becomes available

**Data Structures:**
- `active_drones: List[Drone]` - Drones currently moving in network
- `waiting_drones: List[Drone]` - Drones queued at start hub
- `hub_occupancy: Dict[str, int]` - Current drone count per hub
- `hubs: Dict[str, Hub]` - Hub metadata (capacity, color, position)

### Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| K-shortest paths | $O(6 \cdot E \log V)$ | $O(V + E)$ |
| Drone allocation | $O(n)$ where $n=$ total drones | $O(n)$ |
| One simulation step | $O(n + h)$ where $h=$ hubs | $O(n + h)$ |
| Full simulation | $O(T \cdot (n + h))$ where $T=$ total turns | $O(n + h)$ |

---

## Visualization Features

### Interactive pygame Renderer

The `Visualizer` class renders the drone simulation in real-time with:

**Visual Elements:**
- **Hubs**: Colored circles at network positions (green=start, red=end, blue=waypoints)
- **Connections**: Gray edges connecting hubs, labeled with edge weights
- **Drones**: Small colored circles (cycling through 10 distinct colors) positioned on edges/hubs
- **Status Bar**: Turn count and mode indicator (manual/auto-play)

**User Experience Enhancements:**

1. **Manual Stepping (default mode)**
   - User presses SPACE to advance one turn
   - Full control for debugging and analysis
   - Ideal for understanding bottlenecks and capacity issues

2. **Auto-Play Mode**
   - Press M to toggle to continuous simulation
   - Simulation advances automatically
   - Press SPACE to pause/resume
   - Visual feedback of complete drone flows in motion

3. **Color Coding**
   - Each drone gets unique color for tracking
   - Hub colors indicate function (green start, red end)
   - Easy identification of bottlenecks and congestion

4. **Dynamic Scaling**
   - Automatically scales network layout (60 pixels per unit)
   - Padding prevents cutoff at edges
   - Window size: 1500×700 pixels

**Benefits:**
- Intuitive understanding of drone behavior
- Identify bottlenecks before production deployment
- Validate pathfinding and allocation strategies
- Educational tool for algorithm visualization

---

## Example Input and Output

### Example Input: `maps/easy/02_simple_fork.txt`

```
# Easy Level 2: Two alternative paths
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: mid1 1 1 [color=blue]
hub: mid2 1 -1 [color=blue]
end_hub: goal 2 0 [color=red]

connection: start-mid1 weight=2
connection: start-mid2 weight=2
connection: mid1-goal weight=1
connection: mid2-goal weight=1
```

### Expected Output: Simulation Flow

**Initial State (Turn 0):**
- 4 drones queued at start hub
- Pathfinding discovers 2 paths:
  - Path 1: start → mid1 → goal (cost: 3)
  - Path 2: start → mid2 → goal (cost: 3)
- Drones allocated: Drone 1,3 → Path 1 | Drone 2,4 → Path 2

**Turns 1-2:** Launch Phase
```
Turn 1: Drones 1,2 move into network (start hub capacity allows 2)
Turn 2: Drones 3,4 launch; Drone 1 reaches mid1; Drone 2 reaches mid2
```

**Turns 3-5:** Routing Phase
```
Turn 3: Drones move along paths
Turn 4: Drones 1,2 reach goal hub
Turn 5: Drones 3,4 reach goal hub
```

**Final State (Turn 5):**
- All drones arrived at end hub
- Simulation time: 5 turns
- Total distance traveled: 24 units (4 drones × 6 units each)
- Network utilization: Balanced across 2 paths

### Visualization Output

The pygame window displays:
1. Network topology with colored hubs and weighted edges
2. Drones represented as moving colored circles following their paths
3. Status bar showing: "Turn: 5 | Mode: Manual"
4. Hub colors indicating function and occupancy state

### Performance Metrics (From Simulation)

```
Drones launched successfully: 4
Average turn to completion: 5
Path distribution: 50% / 50% (balanced)
Hub congestion: None (all drones moved smoothly)
```

---

## Development

### Project Structure

```
Fly-in/
├── algorithm.py          # Core pathfinding and simulation engine
├── parsing.py            # Map file parser
├── map.py                # Network topology structures
├── main.py               # Entry point orchestrator
├── visualisation.py      # pygame visualization
├── makefile              # Build and linting targets
├── requirements.txt      # Python dependencies
└── maps/                 # Test scenarios by difficulty
    ├── easy/
    ├── medium/
    ├── hard/
    └── challenger/
```

### Architecture

1. **Parsing Layer** (`parsing.py`): Reads `.txt` map files into structured dictionaries
2. **Data Layer** (`map.py`): Pydantic models for hubs, connections, and network topology
3. **Algorithm Layer** (`algorithm.py`): Pathfinding, allocation, and simulation logic
4. **Visualization Layer** (`visualisation.py`): pygame-based rendering engine
5. **Orchestration** (`main.py`): Coordinates all layers

### Dependencies

- **pygame** (2.6.1): Interactive visualization
- **pydantic** (2.7+): Data validation and models
- **mypy**: Type checking (development)
- **flake8**: Style linting (development)

---

## Future Enhancements

- [ ] Real-time performance metrics dashboard
- [ ] Multiple start/end hubs for hub-to-hub routing
- [ ] Drone failure and recovery scenarios
- [ ] Dynamic weight adjustment based on congestion
- [ ] Export simulation data to CSV for analysis
- [ ] Network topology import from standard formats (GeoJSON, GraphML)
- [ ] Machine learning for optimal allocation strategies

---

## License

This project is provided as-is for educational and research purposes.

## Author

Development Team | Fly-in Simulation Project
