from typing import Any, Union

from dataclasses import dataclass
from abc import ABC, abstractmethod

import geoip2.database
from geoip2.errors import AddressNotFoundError

from packettracker.ip import IP, Location




@dataclass
class DatabaseConnection(ABC):
    
    database: Any
    
    @abstractmethod
    def get_ip_location(self, ip: IP) -> Union[Location, None]:
        """ Returns lattitude and longitude for a given IP adress. """
        ...
    
        
class GeoLite2Database(DatabaseConnection):
    
    database: geoip2.database.Reader
    
    def get_ip_location(self, ip: IP) -> Union[Location, None]:
        try: 
            db_record = self.database.city(ip.address)
            return Location(db_record.location.latitude, db_record.location.longitude)
        
        except AddressNotFoundError:
            print(f'Address {ip.address} not found in the GeoLite2 City database.')
            return Location(None, None)

        
    
    
        
    
        
        