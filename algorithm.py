import heapq
from collections import defaultdict
from typing import List, Dict, Tuple, Any


class Algos:
    """Pathfinding and drone allocation algorithms."""

    def __init__(self, map_instance: Any) -> None:
        """Initialize Algos with Map instance to access its attributes."""
        self.edges = map_instance.edges
        self.start_hub = map_instance.start_hub
        self.end_hub = map_instance.end_hub
        self.all_hubs = map_instance.all_hubs
        self.total_nb_drones = map_instance.total_nb_drones
        self.paths: List[Tuple[int, List[str]]] = []

    def k_shortest_path(self) -> None:
        """Find up to 6 shortest paths from start to end hub."""
        graph: Dict[str, List[Tuple[str, int]]] = defaultdict(list)

        for u, v, w in self.edges:
            graph[u].append((v, w))
        min_heap: List[Tuple[int, List[str]]] = [
            (0, [self.start_hub.name])
        ]
        visited_paths: set[Tuple[str, ...]] = set()
        self.paths = []

        while min_heap and len(self.paths) < 6:
            min_cost, path = heapq.heappop(min_heap)
            node = path[-1]

            t_path = tuple(path)
            if t_path in visited_paths:
                continue

            visited_paths.add(t_path)

            if node == self.end_hub.name:
                self.paths.append((min_cost, path))
                continue
            for nei, weight in graph[node]:
                if nei not in path:
                    new_cost = min_cost + weight
                    heapq.heappush(
                        min_heap, (new_cost, path + [nei])
                    )

    def allocate_drones_to_paths(self) -> Dict[int, List[int]]:
        """Distribute drones evenly across available paths."""
        drone_assignments: Dict[int, List[int]] = {
            i: [] for i in range(len(self.paths))
        }

        path_idx = 0
        for drone_id in range(1, self.total_nb_drones + 1):
            drone_assignments[path_idx].append(drone_id)
            path_idx = (path_idx + 1) % len(self.paths)

        return drone_assignments

    def allocate_dornes_to_list(self) -> List['Drone']:
        """Allocate drones to paths and return list."""
        drone_allocation = self.allocate_drones_to_paths()
        drones_list: List['Drone'] = []

        for drone_id in range(1, self.total_nb_drones + 1):
            for path_idx, drones in drone_allocation.items():
                if drone_id in drones:
                    cost, path = self.paths[path_idx]
                    drones_list.append(
                        Drone(
                            drone_id, path, self.start_hub.name
                        )
                    )
                    break

        return drones_list


class Drone:
    """Represents a single drone with position and path information."""

    def __init__(
        self, id: int, assigned_path: List[str], current_position: str
    ) -> None:
        """Initialize drone with ID, assigned path, and starting position."""
        self.id = id
        self.assigned_path = assigned_path
        self.current_position = current_position
        self.position_index = 0
        self.arrival_turn: Any = None
        self.turns_in_hub = 0


class Simulation:
    """Manages drone movement simulation with constraints and timing."""

    def __init__(
        self, drones: List[Drone], paths: List[Any], hubs: Dict[str, Any]
    ) -> None:
        """Initialize simulation with drones, paths, and hub network."""
        self.active_drones: List[Drone] = []
        self.waiting_drones: List[Drone] = list(drones)
        self.paths = paths
        self.hubs = hubs
        self.turns = 0
        self.is_end: Dict[int, bool] = {}
        self.hub_occupancy: Dict[str, int] = {
            hub: 0 for hub in hubs.keys()
        }
        self.start_hub_name = 'start'

    def check_hub_capacity(self, hub_name: str) -> bool:
        """Check if hub has space for another drone."""
        return bool(self.hub_occupancy[hub_name] <
                    self.hubs[hub_name].properties.max_drones)

    def launch_drones(self) -> None:
        """Launch waiting drones if there's capacity in start hub."""
        hub_name = self.start_hub_name
        start_capacity = self.hubs[hub_name].properties.max_drones

        while (self.waiting_drones and
               self.hub_occupancy[self.start_hub_name] < start_capacity):
            drone = self.waiting_drones.pop(0)
            self.active_drones.append(drone)
            self.is_end[drone.id] = False
            self.hub_occupancy[self.start_hub_name] += 1

    def move_drones(self) -> None:
        """Move each drone based on path respecting constraints."""
        for drone in self.active_drones:
            if self.is_end[drone.id]:
                continue

            if drone.position_index >= len(drone.assigned_path) - 1:
                self.is_end[drone.id] = True
                self.hub_occupancy[drone.current_position] -= 1
                if drone.arrival_turn is None:
                    drone.arrival_turn = self.turns
                continue

            current_hub = self.hubs[drone.current_position]
            zone = current_hub.properties.zone

            required_turns = 2 if zone == 'restricted' else 1

            drone.turns_in_hub += 1

            if drone.turns_in_hub < required_turns:
                continue

            next_hub = drone.assigned_path[drone.position_index + 1]

            if not self.check_hub_capacity(next_hub):
                continue

            self.hub_occupancy[drone.current_position] -= 1
            self.hub_occupancy[next_hub] += 1
            drone.current_position = next_hub
            drone.position_index += 1
            drone.turns_in_hub = 0

    def move_one_drone(self) -> bool:
        """Move only one drone (for manual stepping)."""
        self.launch_drones()
        for drone in self.active_drones:
            if self.is_end[drone.id]:
                continue

            if drone.position_index >= len(drone.assigned_path) - 1:
                self.is_end[drone.id] = True
                self.hub_occupancy[drone.current_position] -= 1
                if drone.arrival_turn is None:
                    drone.arrival_turn = self.turns
                return True

            current_hub = self.hubs[drone.current_position]
            zone = current_hub.properties.zone
            required_turns = 2 if zone == 'restricted' else 1
            drone.turns_in_hub += 1

            if drone.turns_in_hub < required_turns:
                return True

            next_hub = drone.assigned_path[drone.position_index + 1]
            if not self.check_hub_capacity(next_hub):
                return True

            self.hub_occupancy[drone.current_position] -= 1
            self.hub_occupancy[next_hub] += 1
            drone.current_position = next_hub
            drone.position_index += 1
            drone.turns_in_hub = 0
            return True
        return False

    def step(self) -> bool:
        """Execute one simulation step."""
        if self.waiting_drones or not all(self.is_end.values()):
            self.launch_drones()
            self.move_drones()
            self.turns += 1
            return True
        return False

    def manual_step(self) -> None:
        """Execute one drone movement for manual mode and increment turn."""
        self.move_one_drone()
        self.turns += 1

    def simulation(self) -> None:
        """Run full simulation until all drones reach destination."""
        print("============ SIMULATION START ============")

        while self.waiting_drones or not all(self.is_end.values()):
            self.launch_drones()

            output = "".join(
                [f"ID{drone.id}-{drone.current_position}\n"
                 for drone in self.active_drones]
            )

            print(f"Turn {self.turns}:\n {output}")
            if self.waiting_drones:
                print(f"(Waiting: {len(self.waiting_drones)} drones)\n")
            else:
                print()

            self.move_drones()
            self.turns += 1

        print(f"Total turns: {self.turns - 1} turns")
        print("============ SIMULATION ENDS ============")
