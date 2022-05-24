
import gmplot

from packettracker.ip import IP
from packettracker.packet import Packet, PacketFile


class FilePath(str):
    pass


def plot_gmap(public_ip: IP, packet_file: PacketFile, output_file: FilePath) -> None:
    
    gmap = gmplot.GoogleMapPlotter(*public_ip.location, zoom=3)

    for p in packet_file.packets:
        plot_packet(gmap, p)
        
    gmap.draw(output_file)
    
    
def plot_packet(gmap: gmplot.GoogleMapPlotter, packet: Packet) -> None:
    
    if packet.src_ip.location is None or packet.dst_ip.location is None:
        # Packet source or destination IP was not found in the database.
        return
    
    lat_list = [packet.src_ip.location.lattitude, packet.dst_ip.location.lattitude]
    lng_list = [packet.src_ip.location.longitude, packet.dst_ip.location.longitude]
        
    gmap.plot(lats=lat_list,
              lngs=lng_list,
              edge_width=3,
              color='red')