from __future__ import annotations
from typing import List, Dict, Optional, Union

from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import os
import dpkt
import ipaddress

from packettracker.ip import IP, Location
from packettracker.kml import PacketFileKMLEncoder
from packettracker.database import DatabaseConnection




class FilePath(str):
    pass


@dataclass
class Packet:
    
    ethernet: dpkt.ethernet.Ethernet
    
    src_ip: IP = field(init=False, default=None)
    dst_ip: IP = field(init=False, default=None)
    
    def __post_init__(self) -> None:
        self.src_ip = self._bytes_to_ip(self.ethernet.data.src)
        self.dst_ip = self._bytes_to_ip(self.ethernet.data.dst)
        
    def _bytes_to_ip(self, packet_bytes: str) -> IP:
        try:
            ip = ipaddress.IPv4Address(packet_bytes)
            return IP(ip.compressed, ip.is_private)
        
        except ipaddress.AddressValueError:
            ip = ipaddress.IPv6Address(packet_bytes)
            return IP(ip.compressed, ip.is_private)
                
    def __repr__(self) -> str:
        return f'Packet(type={self.ethernet.type}, src_ip={self.src_ip}, dst_ip={self.dst_ip})'
    
    
@dataclass
class PacketFile(ABC):
    
    packets: List[Packet]
    
    @abstractmethod
    def localize_packets(self,
                         db_connection: DatabaseConnection,
                         private_to_public_dict: Dict[str, IP]) -> None:
        """ Localize source and destination IPs in the list of packets. """
        ...
    
    @classmethod
    @abstractmethod
    async def parse(cls, path_to_file: FilePath) -> PacketFile:
        """ Parse a packet file and return instance of PacketFile. """
        ...
        
    @abstractmethod
    def to_kml(self, path_to_file: FilePath) -> Optional[str]:
        """ Saves PacketFile as .kml document. Optionally returns KML string if path_to_file is None. """
        
        
        
@dataclass
class PcapFile(PacketFile):
        
    def localize_packets(self,
                         db_connection: DatabaseConnection,
                         private_to_public_dict: Dict[str, IP]) -> None:
        for packet in self.packets:
            packet.src_ip.location = self.localize_ip(packet.src_ip,
                                                      db_connection,
                                                      private_to_public_dict)
            packet.dst_ip.location = self.localize_ip(packet.dst_ip,
                                                      db_connection,
                                                      private_to_public_dict)
        
    def localize_ip(self,
                    ip: IP,
                    db_connection: DatabaseConnection,
                    private_to_public_dict: Dict[str, IP]) -> Union[Location, None]:
        if ip.is_private:
            return db_connection.get_ip_location(private_to_public_dict[ip.address])
        else:
            return db_connection.get_ip_location(ip)
    
    @classmethod
    async def parse(cls, path_to_file: FilePath) -> PcapFile:
        if not os.path.exists(path_to_file):
            raise FileNotFoundError(f'Packet file \'{path_to_file}\' was not found.')
        
        with open(path_to_file, 'rb') as f:
            pcap = dpkt.pcap.Reader(f)
            
            ethernet_packets = [dpkt.ethernet.Ethernet(packet_bytes) for ts, packet_bytes in pcap]
            ip_packets = [Packet(p) for p in ethernet_packets if p.type == dpkt.ethernet.ETH_TYPE_IP]

            return PcapFile(ip_packets)
    
    def to_kml(self, path_to_file: FilePath = None) -> Optional[str]:
        
        kml_string = PacketFileKMLEncoder.encode(self)
        
        if path_to_file is not None:
            with open(path_to_file, 'w') as f:
                f.write(kml_string)
        else:
            return kml_string
        
