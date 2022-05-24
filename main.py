import os
import asyncio
from collections import defaultdict

import geoip2.records
import geoip2.database

import packettracker.gmap
from packettracker.ip import IPInfoAPI
from packettracker.packet import PcapFile
from packettracker.database import GeoLite2Database        

        


async def main():
    
    packet_traffic_file = 'example/http.pcap'
    city_database_file = 'geolocation-database/GeoLite2-City/GeoLite2-City.mmdb'
    
    public_ip, pcap_file = await asyncio.gather(
        IPInfoAPI.get_public_ip(),
        PcapFile.parse(packet_traffic_file)
    )
    
    private_to_public_dict = defaultdict(lambda: public_ip)

    with geoip2.database.Reader(city_database_file) as reader:
        
        db = GeoLite2Database(reader)
        
        public_ip.location = db.get_ip_location(public_ip)
        pcap_file.localize_packets(db, private_to_public_dict)
    

    kml_file = os.path.splitext(packet_traffic_file)[0] + '_map.kml'
    pcap_file.to_kml(path_to_file=kml_file)
    
    html_file = os.path.splitext(packet_traffic_file)[0] + '_map.html'
    packettracker.gmap.plot_gmap(public_ip, pcap_file, html_file)


if __name__ == '__main__':
    asyncio.run(main())