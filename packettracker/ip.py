from typing import Tuple
from dataclasses import dataclass, field




@dataclass
class Location:
    lattitude: float
    longitude: float


@dataclass
class IP:
    
    address: str    
    location: Location = field(init=False, default=None)

