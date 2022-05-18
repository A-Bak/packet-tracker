from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import requests




@dataclass
class Location:
    lattitude: float
    longitude: float


@dataclass
class IP:
    
    address: str    
    location: Location = field(init=False, default=None)
    

class StatusCodeError(ConnectionError):
    """ Unexpected status code exception. """
    
    
class PublicIPAddressAPI(ABC):
    
    @classmethod
    @abstractmethod
    async def get_public_ip(cls) -> IP:
        ...
        

class IPInfoAPI(PublicIPAddressAPI):
    
    @classmethod
    async def get_public_ip(cls) -> IP:
        
        response = requests.get('https://ipinfo.io/json', verify=True)

        if response.status_code != 200:
            raise StatusCodeError('Failed to retrieve public ip information.')
        
        return IP(response.json()['ip'])

   