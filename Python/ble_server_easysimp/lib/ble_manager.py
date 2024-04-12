from bleak import BleakScanner
from bleak import BleakClient
from PyQt5.QtWidgets import QPushButton
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
        self.characteristc_values = dict()

    #async def notification_handler(self, sender, data):
    #    hr = int.from_bytes(data, byteorder='little')
    #    print(hr)

    async def init_ble(self):
        target_name = "EasySimp"
        target_address = None

        devices = await BleakScanner.discover()

        for d in devices:
            print(d)
            if d.name == target_name:
                target_address = d.address
                print("Dispositivo {} trovato  con indirizzo {} ".format(target_name, target_address))
                break

        if target_address is not None:
            print(target_address)
            self.client = BleakClient(target_address)
            await self.client.connect()
            print(f"Connesso: {self.client.is_connected}")
            self.bluethooth_state.is_connected = self.client.is_connected
            self.bluethooth_state.device_connected_name = target_name
            self.bluethooth_state.device_connected_address = target_address
            #await self.client.start_notify("19B10004-E8F2-537E-4F6C-D104768A1214", self.notification_handler)

        else:
            print("could not find target bluetooth device nearby")
        time.sleep(1)



    def disconnect_from_device(self):
        self.client.disconnect()

    async def get_characteristics(self, chacteristics):
        try:
            for row_char in chacteristics:
                id = row_char[0]
                guid = row_char[1]
                type = row_char[2]
                coeff = row_char[3]
                print(f"Lettura caratteristica -> ID: {id} GUID: {guid} tipo: {type}")
                data = await self.get_characteristc_raw_value(guid)
                if type == "int":
                    self.characteristc_values[id] = int.from_bytes(data, byteorder='little') * coeff
                if type == "float":
                    value = float(int.from_bytes(data, byteorder='little')) * coeff
                    self.characteristc_values[id] = round(value,2)

            return self.characteristc_values
        except Exception as ex:
            print(f"Errore: {ex}")
            self.bluethooth_state.is_connected = False

    async def get_characteristc_raw_value(self, guid):
        try:
            data = await self.client.read_gatt_char(guid)
        except Exception as ex:
            print("Errore:", ex)
        return data

    def convert_bytearray_to_int(self, bytearray):
        converted = None
        try:
            converted = int.from_bytes(bytearray, byteorder='little')
            print(f"Valore convertito: {converted}")
        except Exception as ex:
            print("Errore:", ex)
        return converted

    # async def get_all_characteristc_values(self):
    #     char_dict = dict()
    #     char_dict["GSR"] = await self.get_numeric_characteristic_value("19B10002-E8F2-537E-4F6C-D104768A1214")
    #     char_dict["GSR"] = int.from_bytes(char_dict["GSR"], byteorder='little')
    #     #char_dict["custom"] = await self.get_numeric_characteristic_value("19B10005-E8F2-537E-4F6C-D104768A1214")
    #     #char_dict["custom"] = int.from_bytes(char_dict["custom"], byteorder='little')
    #     print(char_dict)
    #     return char_dict

    # async def get_string_characteristic_value(self, guid):
    #     try:
    #         print("Leggo caratteristica:", guid)
    #         data = await self.client.read_gatt_char(guid)
    #         data = data.decode('utf-8') #convert byte to str
    #         print("data: {}".format(data))
    #     except Exception as ex:
    #         print("Errore:", ex)
    #     return data

    # async def get_numeric_characteristic_value(self, guid):
    #     try:
    #         print("Leggo caratteristica:", guid)
    #         data = await self.client.read_gatt_char(guid)

    #         #data = data.decode('utf-8') #convert byte to str
    #         print("data: {}".format(data))
    #     except Exception as ex:
    #         print("Errore:", ex)
    #     return data
