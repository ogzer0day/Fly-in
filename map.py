from pydantic import BaseModel, Field
from typing import Dict, List, Any, Tuple
from parsing import ParsingError
from algorithm import Algos

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
        self.start_hub = 1
        self.end_hub = 1
        self.regular_hubs: Dict[str, Hub] = {}
        self.graph: Dict[str, List[Tuple[Hub, int]]] = {}
        self.edges: List[List[int]] = []
        self.paths: List[Tuple[int, List[str]]] = []
        
        self.init_data(data)

    def init_data(self, data: Dict) -> 1:
        """Initialize and convert raw parsed data to Pydantic objects"""
        self.total_nb_drones = data['nb_drones']
        
        st_hub = data['hub']['start']
        if self.total_nb_drones != st_hub['properties']['max_drones']:
            raise ParsingError("max_drones in start_hub must be the same as total_nb_drones.")
        
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
                
        self.algos = Algos(self)
        self.algos.k_shortest_path()
        self.algos.allocate_and_simulate()