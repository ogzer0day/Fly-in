from pydantic import BaseModel, Field


class Properties(BaseModel):
    color: str
    zone: str
    max_drones: int = Field(gt=0)


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
    pass
