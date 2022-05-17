from dataclasses import dataclass, field

import dpkt
import socket

from packettracker.ip import IP




@dataclass
class Packet:
    
    ethernet: dpkt.ethernet.Ethernet
    
    src_ip: IP = field(init=False, default=None)
    dst_ip: IP = field(init=False, default=None)
    
    def __post_init__(self) -> None:
        self.src_ip = IP(socket.inet_ntoa(self.ethernet.data.src))
        self.dst_ip = IP(socket.inet_ntoa(self.ethernet.data.dst))
        

    