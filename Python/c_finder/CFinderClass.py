import asyncio
from datetime import datetime
import time
from bleak import BleakScanner
import ShellyPy

# Galaxy Watch4 (WFTK) 	 -84 	 7C:E2:3F:50:0B:8F
class CFinderClass:
    def __init__(self, device_threat_name="Galaxy Watch4", device_threath_address="7C:E2:3F:50:0B:8F", shelly_ip="192.168.13.47"):

        self.shelly_device = ShellyPy.Shelly(shelly_ip)
        self.device_to_find = device_threat_name
        self.latest_sighting = datetime.now()
    def set_shelly_status(self, status):
        self.shelly_device.relay(0, turn=status)

    async def find_threat(self):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        devices = await BleakScanner.discover()
        global shelly_status
        for device in devices:
            # print(f"Nome: {device.name}, Indirizzo: {device.address}, {device._rssi}")
            if device.name and (self.device_to_find in device.name):
                #self.set_shelly_status(True)
                self.latest_sighting = datetime.now()
                print(ts, "\t", device.name, "\t", device._rssi, "\t", device.address)
            #else:
                #self.set_shelly_status(True)
    def calculate_last_sighting_time(self):
        return (datetime.now() - self.latest_sighting).total_seconds()

    async def start_to_find_threat(self):
        while(True):
            await self.find_threat()
            sighting_time_interval = self.calculate_last_sighting_time()
            print("Ultimo avvistamento:", self.calculate_last_sighting_time(),"secondi", "[", self.latest_sighting,"]")
            if(sighting_time_interval < 60):
                self.set_shelly_status(True)
            else:
                self.set_shelly_status(False)

            time.sleep(1)
