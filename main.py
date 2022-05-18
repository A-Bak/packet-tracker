import asyncio
from collections import defaultdict

import geoip2.records
import geoip2.database

from packettracker.ip import IPInfoAPI
from packettracker.packet import PcapFile
from packettracker.kml import PacketFileKMLEncoder
from packettracker.database import GeoLite2Database        

        


async def main():
    
    packet_traffic_file = 'example_packet_capture/small_sample.pcap'
    
    public_ip, pcap_file = await asyncio.gather(
        IPInfoAPI.get_public_ip(),
        PcapFile.parse(packet_traffic_file)
    )
    
    private_to_public_dict = defaultdict(lambda: public_ip)

    city_database_file = 'geolocation-database/GeoLite2-City/GeoLite2-City.mmdb'
    with geoip2.database.Reader(city_database_file) as reader:
        
        db = GeoLite2Database(reader)
        pcap_file.localize_packets(db, private_to_public_dict)
    
    kml_string = PacketFileKMLEncoder.encode(pcap_file)

    output_fp = 'out/test.kml'
    with open(output_fp, 'w') as f:
        f.write(kml_string)
    



if __name__ == '__main__':
    asyncio.run(main())