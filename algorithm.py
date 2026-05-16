
import heapq
from collections import defaultdict
from typing import List

class Algos():
    def __init__(self, map_instance):
        """Initialize Algos with Map instance to access its attributes"""
        self.edges = map_instance.edges
        self.start_hub = map_instance.start_hub
        self.end_hub = map_instance.end_hub
        self.all_hubs = map_instance.all_hubs
        self.total_nb_drones = map_instance.total_nb_drones
        self.paths = []
    
    def k_shortest_path(self):
            graph = defaultdict(list)
            for u, v, w in self.edges:
                graph[u].append((v, w))

            min_heap = [(0, [self.start_hub.name])]
            visited_paths = set()
            self.paths = []
            
            while min_heap and len(self.paths) < 5:
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
                        heapq.heappush(min_heap, (new_cost, path + [nei]))
                
    
    def allocate_drones_to_paths(self):
        drone_assignments = {i: [] for i in range(len(self.paths))}
        
        path_idx = 0
        for drone_id in range(1, self.total_nb_drones + 1):
            drone_assignments[path_idx].append(drone_id)
            path_idx = (path_idx + 1) % len(self.paths)
                    
        return drone_assignments
        
    def allocate_and_simulate(self):
        drone_allocation = self.allocate_drones_to_paths()
        drone_list = []
        
        for drone_id in range(1, self.total_nb_drones + 1):
            for path_idx, drones in drone_allocation.items():
                if drone_id in drones:
                    cost, path = self.paths[path_idx]
                    drone_list.append(Drone(drone_id, path, self.start_hub.name))
                    break
                
        sim = Simulation(drone_list, self.paths, self.all_hubs)
        sim.simulation()
        
class Drone():
    def __init__(self, id, assigned_path, current_position):
        self.id = id
        self.assigned_path = assigned_path
        self.current_position = current_position   
        self.position_index = 0
        self.arrival_turn = None
        self.turns_in_hub = 0
        
class Simulation():
    def __init__(self, drones: List[Drone], paths: List, hubs):
        self.all_drones = drones
        self.active_drones = []
        self.waiting_drones = list(drones)
        self.paths = paths
        self.hubs = hubs
        self.turns = 0
        self.is_end = {}
        self.hub_occupancy = {hub: 0 for hub in hubs.keys()}
        self.start_hub_name = 'start'
    
    def check_hub_capacity(self, hub_name):
        """Check if hub has space for another drone"""
        return self.hub_occupancy[hub_name] < self.hubs[hub_name].properties.max_drones

    def launch_drones(self):
        """Launch waiting drones if there's capacity in start hub"""
        hub_name = self.start_hub_name
        start_capacity = self.hubs[hub_name].properties.max_drones
        
        while self.waiting_drones and self.hub_occupancy[self.start_hub_name] < start_capacity:
            drone = self.waiting_drones.pop(0)
            self.active_drones.append(drone)
            self.is_end[drone.id] = False
            self.hub_occupancy[self.start_hub_name] += 1

    def move_drones(self):
        """Move each drone based on their path, respecting constraints and zone delays"""
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
            
            drone.turns_in_hub += required_turns
            
            next_hub = drone.assigned_path[drone.position_index + 1]

            if not self.check_hub_capacity(next_hub):
                continue
            
            self.hub_occupancy[drone.current_position] -= 1
            self.hub_occupancy[next_hub] += 1
            drone.current_position = next_hub
            drone.position_index += 1
            drone.turns_in_hub = 0

    def simulation(self):
        print("============ SIMULATION START ============")
        
        while self.waiting_drones or not all(self.is_end.values()):
            self.launch_drones()
            
            output = "".join([f"ID{drone.id}-{drone.current_position}\n" for drone in self.active_drones])
            
            print(f"Turn {self.turns}:\n {output}")
            if self.waiting_drones:
                print(f"(Waiting: {len(self.waiting_drones)} drones)\n")
            else:
                print()
            
            self.move_drones()
            self.turns += 1
    
        print(f"Total turns: {self.turns} turns")
        print("============ SIMULATION ENDS ============")