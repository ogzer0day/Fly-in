from pydantic import BaseModel, Field
from typing import Dict, List, Any
from collections import defaultdict
from dataclasses import dataclass
import heapq

class Properties(BaseModel):
    color: str = Field(default=1)
    zone: str = Field(default='normal')
    max_drones: int = Field(default=1, gt=0)
    turns: int = 1


class Hub(BaseModel):
    name: str
    X: int
    Y: int
    properties: Properties


class Connection(BaseModel):
    hub1_name: str
    hub2_name: str
    max_link_capacity: int = Field(default=1, gt=0)


class Map():
    def __init__(self, data: Dict[str, Any]):
        self.total_nb_drones = 0
        self.all_hubs: Dict[str, Hub] = {}
        self.all_connections: List[Connection] = []
        self.start_hub: Hub | 1 = 1
        self.end_hub: Hub | 1 = 1
        self.regular_hubs: Dict[str, Hub] = {}
        self.graph: Dict[str, List[tuple[Hub, int]]] = {}
        self.edges: List[List[int]] = []
        
        self.init_data(data)

    def init_data(self, data: Dict) -> 1:
        """Initialize and convert raw parsed data to Pydantic objects"""
        self.total_nb_drones = data['nb_drones']
        
        st_hub = data['hub']['start']
        self.start_hub = Hub(
            name=st_hub['name'],
            X=st_hub['X'],
            Y=st_hub['Y'],
            properties=Properties(**st_hub['properties'])
        )

        self.regular_hubs = {k: Hub(
            name=v['name'],
            X=v['X'],
            Y=v['Y'],
            properties=Properties(**v['properties'])
        )
        for k, v in data['hub'].items()
        if k not in ('start', 'end')}

        end_hub = data['hub']['end']
        self.end_hub = Hub(
            name=end_hub['name'],
            X=end_hub['X'],
            Y=end_hub['Y'],
            properties=Properties(**end_hub['properties'])
        )
        
        self.all_hubs = {
            self.start_hub.name: self.start_hub,
            **self.regular_hubs,
            self.end_hub.name: self.end_hub
        }
        
        self.all_connections = [
            Connection(
                hub1_name=conn[0][0],
                hub2_name=conn[0][1],
                max_link_capacity=conn[1]['max_link_capacity']
            )
            for conn in data['connections']
        ]

        tmp = data['connections']
        self.graph = {s.name: [] for s in self.all_hubs.values()}
        for zones, capacity in tmp:
                self.graph[zones[0]].append((self.all_hubs[zones[1]], capacity['max_link_capacity']))
                self.graph[zones[1]].append((self.all_hubs[zones[0]], capacity['max_link_capacity']))

        seen = set()
        for k, v in self.graph.items():
            for n in v:
                pair = tuple(sorted([k, n[0].name]))
                if pair in seen:
                    continue
                seen.add(pair)

                if n[0].properties.zone in ['normal', 'priority']:
                    time = 1
                elif n[0].properties.zone == 'restricted':
                    n[0].properties.turns = 2
                    time = 2
                elif n[0].properties.zone == 'blocked':
                    time = 0

                self.edges.append([k, n[0].name, time])

        self.dijstra(self.edges, self.start_hub.name, self.end_hub.name)
       
    def dijstra(self, eges, start, end):
        graph = defaultdict(list)
        for u, v, w in eges:
            graph[u].append((v, w))

        min_heap = [(0, [start])]
        paths = {}
        
        while min_heap and len(paths) < 2:
            min_cost, path = heapq.heappop(min_heap)
            node = path[-1]
            
            if node == end:
                if min_cost in paths:
                    paths[min_cost] += path
                else:
                    paths[min_cost] = path
                continue

            for nei, weight in graph[node]:

                if weight == 0:
                    continue

                new_cost = min_cost + weight
                heapq.heappush(min_heap, (new_cost, path + [nei]))
        
        paths = paths.values()

        drones = []
        i: int = 0

        for i in range(self.total_nb_drones):
            drones.append(Drone(i+1, [], self.start_hub.name))


        sim = Simulation(drones, list(paths), self.all_hubs)
        sim.init_path_drones()
        sim.simulation()
    
class Drone:
    def __init__(self, id, assigned_path, current_position):
        self.id = id
        self.assigned_path = assigned_path
        self.current_position = current_position
        self.position_index = 0
        self.status = 'waiting'
        self.turnes = 0

class Simulation():
    def __init__(self, drones: List[Drone], paths: List, hubs):
        self.drones = drones
        self.turns = 0
        self.paths = paths
        self.hubs = hubs
        self.is_end = {drone.id: False for drone in self.drones}
        self.zone_size = {hub: 0 for hub in hubs.keys()}
        

    def init_path_drones(self):
        i: int = 0
        len_path = len(self.paths)
        for i in range(len(self.drones)):
            self.drones[i].id = i + 1
            self.drones[i].assigned_path = self.paths[(i+1) % len_path]
            # print(self.drones[i].assigned_path)
            self.drones[i].current_position = self.drones[i].assigned_path[0]
            self.drones[i].position_index = 0
            self.drones[i].status = 'start'

    def check_move(self, hub):
        zone = self.hubs[hub]
        max_drones = zone.properties.max_drones
        if self.zone_size[hub] == max_drones:
            return 0
        return 1


    def move_drones(self, drone):
        if drone.position_index >= len(drone.assigned_path) - 1:
            if not self.is_end[drone.id]:
                self.is_end[drone.id] = True
                self.zone_size[drone.current_position] -= 1
            return

        next_pos = drone.assigned_path[drone.position_index + 1]

        if not self.check_move(next_pos):
            return

        if drone.turnes > self.turns:
            return

        self.zone_size[drone.current_position] -= 1
        self.zone_size[next_pos] += 1
        

        n_z = self.hubs[next_pos]
        drone.turnes = n_z.properties.turns + self.turns
        drone.position_index += 1
        drone.current_position = next_pos


    def simulation(self):
        for drone in self.drones:
            self.zone_size[drone.current_position] += 1

        while not all(self.is_end.values()):
            output = " ".join([f"ID{drone.id}-{drone.current_position}\n" for drone in self.drones])
            for drone in self.drones:
                self.move_drones(drone)
            
            
            print(f"Turn {self.turns}:\n {output}\n")

            self.turns += 1
           



if __name__ == '__main__':

    data = {'nb_drones': 12, 'hub': {'start': {'name': 'start', 'X': 0, 'Y': 0, 'properties': {'color': 'green', 'zone': 'normal', 'max_drones': 12}}, 'gate1': {'name': 'gate1', 'X': 1, 'Y': 0, 'properties': {'color': 'orange', 'zone': 'normal', 'max_drones': 1}}, 'gate2': {'name': 'gate2', 'X': 2, 'Y': 0, 'properties': {'color': 'orange', 'zone': 'normal', 'max_drones': 1}}, 'gate3': {'name': 'gate3', 'X': 3, 'Y': 0, 'properties': {'color': 'orange', 'zone': 'normal', 'max_drones': 1}}, 'waiting_area1': {'name': 'waiting_area1', 'X': 1, 'Y': 1, 'properties': {'color': 'blue', 'zone': 'normal', 'max_drones': 4}}, 'waiting_area2': {'name': 'waiting_area2', 'X': 2, 'Y': 1, 'properties': {'color': 'blue', 'zone': 'normal', 'max_drones': 4}}, 'waiting_area3': {'name': 'waiting_area3', 'X': 3, 'Y': 1, 'properties': {'color': 'blue', 'zone': 'normal', 'max_drones': 4}}, 'restricted_tunnel1': {'name': 'restricted_tunnel1', 'X': 4, 'Y': 0, 'properties': {'color': 'red', 'zone': 'restricted', 'max_drones': 2}}, 'restricted_tunnel2': {'name': 'restricted_tunnel2', 'X': 5, 'Y': 0, 'properties': {'color': 'red', 'zone': 'restricted', 'max_drones': 2}}, 'restricted_tunnel3': {'name': 'restricted_tunnel3', 'X': 6, 'Y': 0, 'properties': {'color': 'red', 'zone': 'restricted', 'max_drones': 2}}, 'priority_bypass1': {'name': 'priority_bypass1', 'X': 4, 'Y': 1, 'properties': {'color': 'cyan', 'zone': 'priority', 'max_drones': 3}}, 'priority_bypass2': {'name': 'priority_bypass2', 'X': 5, 'Y': 1, 'properties': {'color': 'cyan', 'zone': 'priority', 'max_drones': 3}}, 'convergence': {'name': 'convergence', 'X': 7, 'Y': 0, 'properties': {'color': 'yellow', 'zone': 'normal', 'max_drones': 6}}, 'final_bottleneck': {'name': 'final_bottleneck', 'X': 8, 'Y': 0, 'properties': {'color': 'orange', 'zone': 'normal', 'max_drones': 3}}, 'end': {'name': 'goal', 'X': 9, 'Y': 0, 'properties': {'color': 'green', 'zone': 'normal', 'max_drones': 12}}}, 'connections': [(('start', 'gate1'), {'max_link_capacity': 1}), (('gate1', 'gate2'), {'max_link_capacity': 1}), (('gate2', 'gate3'), {'max_link_capacity': 1}), (('gate1', 'waiting_area1'), {'max_link_capacity': 1}), (('gate2', 'waiting_area2'), {'max_link_capacity': 1}), (('gate3', 'waiting_area3'), {'max_link_capacity': 1}), (('waiting_area1', 'waiting_area2'), {'max_link_capacity': 1}), (('waiting_area2', 'waiting_area3'), {'max_link_capacity': 1}), (('gate3', 'restricted_tunnel1'), {'max_link_capacity': 1}), (('restricted_tunnel1', 'restricted_tunnel2'), {'max_link_capacity': 1}), (('restricted_tunnel2', 'restricted_tunnel3'), {'max_link_capacity': 1}), (('restricted_tunnel3', 'convergence'), {'max_link_capacity': 1}), (('waiting_area1', 'priority_bypass1'), {'max_link_capacity': 1}), (('priority_bypass1', 'priority_bypass2'), {'max_link_capacity': 1}), (('priority_bypass2', 'convergence'), {'max_link_capacity': 1}), (('convergence', 'final_bottleneck'), {'max_link_capacity': 1}), (('final_bottleneck', 'goal'), {'max_link_capacity': 1}), (('waiting_area3', 'convergence'), {'max_link_capacity': 1})]}




    map = Map(data)