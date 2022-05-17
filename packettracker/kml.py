from abc import ABC, abstractmethod
from typing import Any, List

from packettracker.packet import Packet




class IPLocationError(ValueError):
    pass


class KMLEncoder(ABC):
    
    @classmethod
    @abstractmethod
    def encode(cls, object: Any) -> str:
        ...


class PacketKMLEncoder(KMLEncoder):
    
    @classmethod
    def encode(cls, packet_list: List[Packet]) -> str:
        
        kml_string = cls.kml_header()
        
        for packet in packet_list:
            kml_string += cls.encode_packet(packet)
            
        return kml_string + cls.kml_footer()
    
    @classmethod
    def encode_packet(cls, packet: Packet) -> str:
        
        src_ip = packet.src_ip
        dst_ip = packet.dst_ip
        
        if src_ip.location is None or dst_ip.location is None:
            raise IPLocationError('Failed conversion to KML. Location of an IP address is None.')
        
        kml_body =  '<Placemark>\n'\
                    f'<name>{src_ip.address} --> {dst_ip.address}</name>\n'\
                    '<extrude>1</extrude>\n'\
                    '<tessellate>1</tessellate>\n'\
                    '<styleUrl>#transBluePoly</styleUrl>\n'\
                    '<LineString>\n'\
                    f'<coordinates>{dst_ip.location.lattitude},{dst_ip.location.longitude}\n'\
                    f'{src_ip.location.lattitude},{src_ip.location.longitude}</coordinates>\n'\
                    '</LineString>\n'\
                    '</Placemark>\n'
        return kml_body
        
    @classmethod
    def kml_header(cls) -> str:
        kml_header = '<?xml version="1.0" encoding="UTF-8"?> \n'\
                     '<kml xmlns="http://www.opengis.net/kml/2.2">\n'\
                     '<Document>\n'\
                     '<Style id="transBluePoly"><LineStyle><width>1.5</width><color>501400E6</color></LineStyle></Style>'
        return kml_header
                
    @classmethod
    def kml_footer(cls) -> str:
        return '</Document>\n</kml>\n'
