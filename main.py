import dpkt

import geoip2.records
import geoip2.database

from packettracker.packet import Packet
from packettracker.kml import PacketKMLEncoder
from packettracker.database import GeoLite2Database        

        


def main():
    
    packet_fp = 'example_packet_capture/tftp_rrq.pcap'
    with open(packet_fp, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        packets = [Packet(dpkt.ethernet.Ethernet(buffer)) for timestamp, buffer in pcap]

    
    city_database_fp = 'geolocation-database/GeoLite2-City/GeoLite2-City.mmdb'
    with geoip2.database.Reader(city_database_fp) as reader:
        
        db = GeoLite2Database(reader)
        
        for packet in packets:
            packet.src_ip.location = db.get_ip_location(packet.src_ip)
            packet.dst_ip.location = db.get_ip_location(packet.dst_ip)
            
    kml_string = PacketKMLEncoder.encode(packets)

    output_fp = 'out/test.kml'
    with open(output_fp, 'w') as f:
        f.write(kml_string)
    



if __name__ == '__main__':
    main()