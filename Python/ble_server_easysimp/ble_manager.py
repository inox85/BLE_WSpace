
import asyncio
import json
from bleak import BleakScanner
from bleak import BleakClient
import time

class BluethoothState: 
    def __init__(self):
        self.is_connected = False
        self.device_connected_name = None
        self.device_connected_address = None

class BluetoothManager:
    def __init__(self):
        self.client = None
        self.bluethooth_state = BluethoothState()

    async def init_ble(self):
        target_name = "EasySymp"
        target_address = None

        #SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
        CHARACTERISTIC_UUID = "19B10002-E8F2-537E-4F6C-D104768A1214"
        devices = await BleakScanner.discover()
        
        for d in devices:
            print(d)
            if d.name == target_name:
                target_address = d.address
                print("found target {} bluetooth device with address {} ".format(target_name, target_address))
                break

        if target_address is not None:
            print(target_address)
            self.client = BleakClient(target_address)
            await self.client.connect()
            print(f"Connected: {self.client.is_connected}")
            self.bluethooth_state.is_connected = self.client.is_connected
            self.bluethooth_state.device_connected_name = target_name
            self.bluethooth_state.device_connected_address = target_address

                               
        else:
            print("could not find target bluetooth device nearby")
    
    async def get_all_characteristc_values(self):
        char_dict = dict()
        char_dict["GSR"] = await self.get_numeric_characteristic_value("19B10002-E8F2-537E-4F6C-D104768A1214")
        char_dict["GSR"] = int.from_bytes(char_dict["GSR"], byteorder='little')
        #char_dict["custom"] = await self.get_numeric_characteristic_value("19B10005-E8F2-537E-4F6C-D104768A1214")
        #char_dict["custom"] = int.from_bytes(char_dict["custom"], byteorder='little')
        print(char_dict)
        return char_dict
    
    async def get_string_characteristic_value(self, guid):
        try:
            print("Leggo caratteristica:", guid)
            data = await self.client.read_gatt_char(guid)
            data = data.decode('utf-8') #convert byte to str
            print("data: {}".format(data))
        except Exception as ex:
            print("Errore:", ex)
        return data
    
    async def get_numeric_characteristic_value(self, guid):
        try:
            print("Leggo caratteristica:", guid)
            data = await self.client.read_gatt_char(guid)

            #data = data.decode('utf-8') #convert byte to str
            print("data: {}".format(data))
        except Exception as ex:
            print("Errore:", ex)
        return data