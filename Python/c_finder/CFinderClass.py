import asyncio
from datetime import datetime
import time
from bleak import BleakScanner
import ShellyPy
import csv

# Galaxy Watch4 (WFTK) 	 -84 	 74:E5:36:50:6B:0B
class CFinderClass:
    def __init__(self,  device_threat_name="Galaxy Watch4", device_threath_address="7C:E2:3F:50:0B:8F",
                 shelly_ip="192.168.13.47", ):

        self.device_to_find = device_threat_name
        self.latest_sighting = datetime.now()
        self.device_name = ""
        self.device_power = ""
        self.device_address = ""

        self.response_dictionary = dict()

    async def find_threat(self):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        devices = await BleakScanner.discover()
        devices_dict = dict()
        for device in devices:
            infos = [device.name, device._rssi]
            devices_dict[device.address] = infos

        print(devices_dict)

        self.response_dictionary = dict()
        for values in devices_dict.values():
            if self.device_to_find in str(values[0]):
                self.latest_sighting = datetime.now()
                self.response_dictionary["Device_name"] = values[0]
                self.response_dictionary["Device_power"] = values[1]

    def calculate_last_sighting_time(self):
        return (datetime.now() - self.latest_sighting).total_seconds()

    def get_informations(self):
        return self.response_dictionary
    async def start_to_find_threat(self):
        while (True):
            await self.find_threat()
            sighting_time_interval = self.calculate_last_sighting_time()
            print("Ultimo avvistamento:", self.calculate_last_sighting_time(), "secondi", "[", self.latest_sighting,
                  "]")
            #if self.calculate_last_sighting_time()> 60:

            #else:


            time.sleep(1)
