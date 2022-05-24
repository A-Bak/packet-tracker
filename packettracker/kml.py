from __future__ import annotations
from typing import Any, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from packettracker.packet import Packet, PacketFile




class IPLocationError(ValueError):
    pass


class KMLEncoder(ABC):
    
    @classmethod
    @abstractmethod
    def encode(cls, object: Any) -> str:
        """ Returns a string with the KML representation of the object. """
        ...


class PacketFileKMLEncoder(KMLEncoder):
    
    @classmethod
    def encode(cls, packet_file: PacketFile) -> str:
        
        kml_string = cls.kml_header()
        
        for packet in packet_file.packets:
            try:
                kml_string += cls.encode_packet(packet)
            except IPLocationError:
                pass
            
        return kml_string + cls.kml_footer()
    
    @classmethod
    def encode_packet(cls, packet: Packet) -> str:
        
        src_ip = packet.src_ip
        dst_ip = packet.dst_ip
        
        if src_ip.location is None or dst_ip.location is None:
            raise IPLocationError('Failed conversion to KML. Location of an IP address is None.')
        
        kml_body =  '\t\t<Placemark>\n'\
                    f'\t\t\t<name>{src_ip.address} --> {dst_ip.address}</name>\n'\
                    '\t\t\t<extrude>1</extrude>\n'\
                    '\t\t\t<tessellate>1</tessellate>\n'\
                    '\t\t\t<styleUrl>#transBluePoly</styleUrl>\n'\
                    '\t\t\t<LineString>\n'\
                    f'\t\t\t<coordinates>{dst_ip.location.longitude},{dst_ip.location.lattitude}\n'\
                    f'\t\t\t{src_ip.location.longitude},{src_ip.location.lattitude}</coordinates>\n'\
                    '\t\t\t</LineString>\n'\
                    '\t\t</Placemark>\n'
        return kml_body
        
    @classmethod
    def kml_header(cls) -> str:
        kml_header = '<?xml version="1.0" encoding="UTF-8"?> \n'\
                     '<kml xmlns="http://www.opengis.net/kml/2.2">\n'\
                     '<Document>\n'\
                     '\t<Style id="transBluePoly">\n'\
                     '\t<LineStyle><width>1.5</width><color>501400E6</color></LineStyle>\n'\
                     '\t</Style>\n'
        return kml_header
                
    @classmethod
    def kml_footer(cls) -> str:
        return '</Document>\n</kml>\n'
