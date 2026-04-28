from pydantic import BaseModel, Field
from typing import Dict, List


class Properties(BaseModel):
    color: str = Field(default=None)
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
    max_link_capacity: int = Field(default=1, gt=0) | None


class Map():
    def __init__(self, data: Dict):
        self.total_nb_drones = 0
        self.all_hubs: Dict[str, Hub] = {}
        self.all_connections: List[Connection] = []
        self.start_hub: Hub | None = None
        self.end_hub: Hub | None = None
        self.regular_hubs: Dict[str, Hub] = {}
        
        self.init_data(data)

    def init_data(self, data: Dict) -> None:
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
            'start': self.start_hub,
            **self.regular_hubs,
            'end': self.end_hub
        }
        
        self.all_connections = [
            Connection(
                hub1_name=conn[0][0],
                hub2_name=conn[0][1],
                max_link_capacity=conn[1]['max_link_capacity']
            )
            for conn in data['connections']
        ]