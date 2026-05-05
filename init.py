from pydantic import BaseModel, Field
from typing import Dict, List, Any
from collections import defaultdict
import heapq

class Properties(BaseModel):
    color: str = Field(default=1)
    zone: str = Field(default='normal')
    max_drones: int = Field(default=1, gt=0)


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
        
        # print(self.graph)
        
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
                    time = 2
                elif n[0].properties.zone == 'blocked':
                    time = 0

                self.edges.append([k, n[0].name, time])

        # print(self.edges)
        self.dijkstra(self.edges, self.start_hub.name, self.end_hub.name)

    def dijkstra(self, edeges: List[List[int]], start: str, end: str) -> None:
        graph = defaultdict(list)

        for u, v, w in edeges:
            graph[u].append([v, w])

        min_heap = [(0, [start])]
        all_path = {}

        while min_heap:
            total_cost, paths = heapq.heappop(min_heap)
            node = paths[-1]

            if node == end and len(all_path) < 3:
                if total_cost in all_path:
                    all_path[total_cost].append(paths)
                else:
                    all_path[total_cost] = [paths]
                continue

            for nei, weight in graph[node]:
                if weight == 0:
                    continue

                new_dist = weight + total_cost
                heapq.heappush(min_heap, (new_dist, paths + [nei]))

        print(all_path[min(all_path)])
            
        

if __name__ == '__main__':
    data = {'nb_drones': 30, 'hub': {'start': {'name': 'start', 'X': 0, 'Y': 0, 'properties': {'color': 'green', 'zone': 'normal', 'max_drones': 25}}, 'gate_hell1': {'name': 'gate_hell1', 'X': 1, 'Y': 0, 'properties': {'color': 'red', 'zone': 'normal', 'max_drones': 1}}, 'gate_hell2': {'name': 'gate_hell2', 'X': 2, 'Y': 0, 'properties': {'color': 'red', 'zone': 'normal', 'max_drones': 1}}, 'gate_hell3': {'name': 'gate_hell3', 'X': 3, 'Y': 0, 'properties': {'color': 'red', 'zone': 'normal', 'max_drones': 1}}, 'gate_hell4': {'name': 'gate_hell4', 'X': 4, 'Y': 0, 'properties': {'color': 'red', 'zone': 'normal', 'max_drones': 1}}, 'gate_hell5': {'name': 'gate_hell5', 'X': 5, 'Y': 0, 'properties': {'color': 'red', 'zone': 'normal', 'max_drones': 1}}, 'maze_trap_a1': {'name': 'maze_trap_a1', 'X': 1, 'Y': 1, 'properties': {'color': 'purple', 'zone': 'normal', 'max_drones': 1}}, 'maze_trap_a2': {'name': 'maze_trap_a2', 'X': 2, 'Y': 1, 'properties': {'color': 'purple', 'zone': 'normal', 'max_drones': 1}}, 'maze_trap_a3': {'name': 'maze_trap_a3', 'X': 3, 'Y': 1, 'properties': {'color': 'purple', 'zone': 'normal', 'max_drones': 1}}, 'maze_dead_a': {'name': 'maze_dead_a', 'X': 4, 'Y': 1, 'properties': {'color': 'black', 'zone': 'normal', 'max_drones': 1}}, 'maze_trap_b1': {'name': 'maze_trap_b1', 'X': 1, 'Y': -1, 'properties': {'color': 'purple', 'zone': 'normal', 'max_drones': 1}}, 'maze_trap_b2': {'name': 'maze_trap_b2', 'X': 2, 'Y': -1, 'properties': {'color': 'purple', 'zone': 'normal', 'max_drones': 1}}, 'maze_trap_b3': {'name': 'maze_trap_b3', 'X': 3, 'Y': -1, 'properties': {'color': 'purple', 'zone': 'normal', 'max_drones': 1}}, 'maze_dead_b': {'name': 'maze_dead_b', 'X': 4, 'Y': -1, 'properties': {'color': 'black', 'zone': 'normal', 'max_drones': 1}}, 'maze_loop1': {'name': 'maze_loop1', 'X': 1, 'Y': 2, 'properties': {'color': 'brown', 'zone': 'restricted', 'max_drones': 1}}, 'maze_loop2': {'name': 'maze_loop2', 'X': 2, 'Y': 2, 'properties': {'color': 'brown', 'zone': 'restricted', 'max_drones': 1}}, 'maze_loop3': {'name': 'maze_loop3', 'X': 3, 'Y': 2, 'properties': {'color': 'brown', 'zone': 'restricted', 'max_drones': 1}}, 'maze_loop4': {'name': 'maze_loop4', 'X': 4, 'Y': 2, 'properties': {'color': 'brown', 'zone': 'restricted', 'max_drones': 1}}, 'maze_loop5': {'name': 'maze_loop5', 'X': 5, 'Y': 2, 'properties': {'color': 'brown', 'zone': 'restricted', 'max_drones': 1}}, 'maze_loop6': {'name': 'maze_loop6', 'X': 5, 'Y': 1, 'properties': {'color': 'brown', 'zone': 'restricted', 'max_drones': 1}}, 'micro_gate1': {'name': 'micro_gate1', 'X': 6, 'Y': 0, 'properties': {'color': 'orange', 'zone': 'normal', 'max_drones': 1}}, 'micro_gate2': {'name': 'micro_gate2', 'X': 7, 'Y': 0, 'properties': {'color': 'orange', 'zone': 'normal', 'max_drones': 1}}, 'micro_gate3': {'name': 'micro_gate3', 'X': 8, 'Y': 0, 'properties': {'color': 'orange', 'zone': 'normal', 'max_drones': 1}}, 'overflow_hell1': {'name': 'overflow_hell1', 'X': 6, 'Y': 1, 'properties': {'color': 'maroon', 'zone': 'restricted', 'max_drones': 2}}, 'overflow_hell2': {'name': 'overflow_hell2', 'X': 7, 'Y': 1, 'properties': {'color': 'maroon', 'zone': 'restricted', 'max_drones': 2}}, 'overflow_hell3': {'name': 'overflow_hell3', 'X': 8, 'Y': 1, 'properties': {'color': 'maroon', 'zone': 'restricted', 'max_drones': 2}}, 'overflow_hell4': {'name': 'overflow_hell4', 'X': 6, 'Y': -1, 'properties': {'color': 'maroon', 'zone': 'restricted', 'max_drones': 2}}, 'overflow_hell5': {'name': 'overflow_hell5', 'X': 7, 'Y': -1, 'properties': {'color': 'maroon', 'zone': 'restricted', 'max_drones': 2}}, 'overflow_hell6': {'name': 'overflow_hell6', 'X': 8, 'Y': -1, 'properties': {'color': 'maroon', 'zone': 'restricted', 'max_drones': 2}}, 'false_hope1': {'name': 'false_hope1', 'X': 9, 'Y': 0, 'properties': {'color': 'gold', 'zone': 'priority', 'max_drones': 3}}, 'false_hope2': {'name': 'false_hope2', 'X': 10, 'Y': 0, 'properties': {'color': 'gold', 'zone': 'priority', 'max_drones': 2}}, 'false_hope3': {'name': 'false_hope3', 'X': 11, 'Y': 0, 'properties': {'color': 'gold', 'zone': 'priority', 'max_drones': 1}}, 'priority_trap1': {'name': 'priority_trap1', 'X': 9, 'Y': 1, 'properties': {'color': 'gold', 'zone': 'priority', 'max_drones': 1}}, 'priority_trap2': {'name': 'priority_trap2', 'X': 10, 'Y': 1, 'properties': {'color': 'gold', 'zone': 'priority', 'max_drones': 1}}, 'priority_dead': {'name': 'priority_dead', 'X': 11, 'Y': 1, 'properties': {'color': 'black', 'zone': 'normal', 'max_drones': 1}}, 'priority_trap3': {'name': 'priority_trap3', 'X': 9, 'Y': -1, 'properties': {'color': 'gold', 'zone': 'priority', 'max_drones': 1}}, 'priority_trap4': {'name': 'priority_trap4', 'X': 10, 'Y': -1, 'properties': {'color': 'gold', 'zone': 'priority', 'max_drones': 1}}, 'priority_dead2': {'name': 'priority_dead2', 'X': 11, 'Y': -1, 'properties': {'color': 'black', 'zone': 'normal', 'max_drones': 1}}, 'conv_restricted1': {'name': 'conv_restricted1', 'X': 12, 'Y': 2, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'conv_restricted2': {'name': 'conv_restricted2', 'X': 13, 'Y': 2, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'conv_restricted3': {'name': 'conv_restricted3', 'X': 14, 'Y': 2, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'conv_restricted4': {'name': 'conv_restricted4', 'X': 12, 'Y': 0, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'conv_restricted5': {'name': 'conv_restricted5', 'X': 13, 'Y': 0, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'conv_restricted6': {'name': 'conv_restricted6', 'X': 14, 'Y': 0, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'conv_restricted7': {'name': 'conv_restricted7', 'X': 12, 'Y': -2, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'conv_restricted8': {'name': 'conv_restricted8', 'X': 13, 'Y': -2, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'conv_restricted9': {'name': 'conv_restricted9', 'X': 14, 'Y': -2, 'properties': {'color': 'darkred', 'zone': 'restricted', 'max_drones': 1}}, 'final_merge': {'name': 'final_merge', 'X': 15, 'Y': 0, 'properties': {'color': 'violet', 'zone': 'normal', 'max_drones': 5}}, 'final_torture1': {'name': 'final_torture1', 'X': 16, 'Y': 0, 'properties': {'color': 'crimson', 'zone': 'normal', 'max_drones': 2}}, 'final_torture2': {'name': 'final_torture2', 'X': 17, 'Y': 0, 'properties': {'color': 'crimson', 'zone': 'normal', 'max_drones': 1}}, 'final_torture3': {'name': 'final_torture3', 'X': 18, 'Y': 0, 'properties': {'color': 'crimson', 'zone': 'normal', 'max_drones': 1}}, 'final_torture4': {'name': 'final_torture4', 'X': 19, 'Y': 0, 'properties': {'color': 'crimson', 'zone': 'normal', 'max_drones': 1}}, 'final_torture5': {'name': 'final_torture5', 'X': 20, 'Y': 0, 'properties': {'color': 'crimson', 'zone': 'normal', 'max_drones': 1}}, 'end': {'name': 'impossible_goal', 'X': 21, 'Y': 0, 'properties': {'color': 'rainbow', 'zone': 'normal', 'max_drones': 25}}}, 'connections': [(('start', 'gate_hell1'), {'max_link_capacity': 1}), (('gate_hell1', 'gate_hell2'), {'max_link_capacity': 1}), (('gate_hell2', 'gate_hell3'), {'max_link_capacity': 1}), (('gate_hell3', 'gate_hell4'), {'max_link_capacity': 1}), (('gate_hell4', 'gate_hell5'), {'max_link_capacity': 1}), (('gate_hell1', 'maze_trap_a1'), {'max_link_capacity': 1}), (('gate_hell2', 'maze_trap_b1'), {'max_link_capacity': 1}), (('gate_hell3', 'maze_loop1'), {'max_link_capacity': 1}), (('maze_trap_a1', 'maze_trap_a2'), {'max_link_capacity': 1}), (('maze_trap_a2', 'maze_trap_a3'), {'max_link_capacity': 1}), (('maze_trap_a3', 'maze_dead_a'), {'max_link_capacity': 1}), (('maze_trap_b1', 'maze_trap_b2'), {'max_link_capacity': 1}), (('maze_trap_b2', 'maze_trap_b3'), {'max_link_capacity': 1}), (('maze_trap_b3', 'maze_dead_b'), {'max_link_capacity': 1}), (('maze_loop1', 'maze_loop2'), {'max_link_capacity': 1}), (('maze_loop2', 'maze_loop3'), {'max_link_capacity': 1}), (('maze_loop3', 'maze_loop4'), {'max_link_capacity': 1}), (('maze_loop4', 'maze_loop5'), {'max_link_capacity': 1}), (('maze_loop5', 'maze_loop6'), {'max_link_capacity': 1}), (('maze_loop6', 'maze_loop1'), {'max_link_capacity': 1}), (('maze_trap_a2', 'micro_gate1'), {'max_link_capacity': 1}), (('maze_trap_b2', 'micro_gate1'), {'max_link_capacity': 1}), (('maze_loop3', 'micro_gate2'), {'max_link_capacity': 1}), (('gate_hell5', 'micro_gate1'), {'max_link_capacity': 1}), (('micro_gate1', 'micro_gate2'), {'max_link_capacity': 1}), (('micro_gate2', 'micro_gate3'), {'max_link_capacity': 1}), (('micro_gate1', 'overflow_hell1'), {'max_link_capacity': 1}), (('micro_gate2', 'overflow_hell2'), {'max_link_capacity': 1}), (('micro_gate3', 'overflow_hell3'), {'max_link_capacity': 1}), (('micro_gate1', 'overflow_hell4'), {'max_link_capacity': 1}), (('micro_gate2', 'overflow_hell5'), {'max_link_capacity': 1}), (('micro_gate3', 'overflow_hell6'), {'max_link_capacity': 1}), (('overflow_hell1', 'overflow_hell2'), {'max_link_capacity': 1}), (('overflow_hell2', 'overflow_hell3'), {'max_link_capacity': 1}), (('overflow_hell4', 'overflow_hell5'), {'max_link_capacity': 1}), (('overflow_hell5', 'overflow_hell6'), {'max_link_capacity': 1}), (('overflow_hell3', 'false_hope1'), {'max_link_capacity': 1}), (('overflow_hell6', 'false_hope1'), {'max_link_capacity': 1}), (('micro_gate3', 'false_hope1'), {'max_link_capacity': 1}), (('false_hope1', 'false_hope2'), {'max_link_capacity': 1}), (('false_hope2', 'false_hope3'), {'max_link_capacity': 1}), (('false_hope1', 'priority_trap1'), {'max_link_capacity': 1}), (('false_hope2', 'priority_trap2'), {'max_link_capacity': 1}), (('false_hope3', 'priority_dead'), {'max_link_capacity': 1}), (('false_hope1', 'priority_trap3'), {'max_link_capacity': 1}), (('false_hope2', 'priority_trap4'), {'max_link_capacity': 1}), (('false_hope3', 'priority_dead2'), {'max_link_capacity': 1}), (('priority_trap1', 'priority_trap2'), {'max_link_capacity': 1}), (('priority_trap3', 'priority_trap4'), {'max_link_capacity': 1}), (('false_hope3', 'conv_restricted1'), {'max_link_capacity': 1}), (('false_hope3', 'conv_restricted4'), {'max_link_capacity': 1}), (('false_hope3', 'conv_restricted7'), {'max_link_capacity': 1}), (('conv_restricted1', 'conv_restricted2'), {'max_link_capacity': 1}), (('conv_restricted2', 'conv_restricted3'), {'max_link_capacity': 1}), (('conv_restricted4', 'conv_restricted5'), {'max_link_capacity': 1}), (('conv_restricted5', 'conv_restricted6'), {'max_link_capacity': 1}), (('conv_restricted7', 'conv_restricted8'), {'max_link_capacity': 1}), (('conv_restricted8', 'conv_restricted9'), {'max_link_capacity': 1}), (('conv_restricted3', 'final_merge'), {'max_link_capacity': 1}), (('conv_restricted6', 'final_merge'), {'max_link_capacity': 1}), (('conv_restricted9', 'final_merge'), {'max_link_capacity': 1}), (('final_merge', 'final_torture1'), {'max_link_capacity': 1}), (('final_torture1', 'final_torture2'), {'max_link_capacity': 1}), (('final_torture2', 'final_torture3'), {'max_link_capacity': 1}), (('final_torture3', 'final_torture4'), {'max_link_capacity': 1}), (('final_torture4', 'final_torture5'), {'max_link_capacity': 1}), (('final_torture5', 'impossible_goal'), {'max_link_capacity': 1}), (('overflow_hell1', 'conv_restricted1'), {'max_link_capacity': 1}), (('overflow_hell4', 'conv_restricted7'), {'max_link_capacity': 1}), (('priority_trap1', 'conv_restricted4'), {'max_link_capacity': 1})]}
    map = Map(data)
  