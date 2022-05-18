from __future__ import annotations
from typing import List

from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import os
import dpkt
import ipaddress

from packettracker.ip import IP




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
            return IP(ipaddress.IPv4Address(packet_bytes).compressed)
        except ipaddress.AddressValueError:
            return IP(ipaddress.IPv6Address(packet_bytes).compressed)
        
    def __repr__(self) -> str:
        return f'Packet(type={self.ethernet.type}, src_ip={self.src_ip}, dst_ip={self.dst_ip})'
    
    
class PacketFile(ABC):
    
    @classmethod
    @abstractmethod
    async def parse(cls, path_to_file: FilePath) -> PacketFile:
        ...
        
        
@dataclass
class PcapFile(PacketFile):
    
    packets: List[Packet]
    
    @classmethod
    async def parse(cls, path_to_file: FilePath) -> PcapFile:
        
        if not os.path.exists(path_to_file):
            raise FileNotFoundError(f'Packet file \'{path_to_file}\' was not found.')
        
        with open(path_to_file, 'rb') as f:
            pcap = dpkt.pcap.Reader(f)
            
            ethernet_packets = [dpkt.ethernet.Ethernet(packet_bytes) for ts, packet_bytes in pcap]
            ip_packets = [Packet(p) for p in ethernet_packets if p.type == dpkt.ethernet.ETH_TYPE_IP]

            return PcapFile(ip_packets)
        
    
