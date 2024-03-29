import asyncio
import json
from bleak import BleakScanner
from bleak import BleakClient
import time


async def handle_client(reader, writer):    # Dati da inviare
    print("Ricevuta richiesta...")
    #await get_ble_characteristic_value("19B10007-E8F2-537E-4F6C-D104768A1214")

    await manager.get_characteristic_value()

    data = {'temperature': 25, 'humidity': 50}
    message = json.dumps(data).encode()

    # Invia i dati al client
    writer.write(message)
    await writer.drain()
    # Chiudi la connessione
    writer.close()

class BluetoothManager:
    def __init__(self):
        self.client = None

    async def init_ble(self):
        target_name = "Forometro"
        target_address = None

        SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
        CHARACTERISTIC_UUID = "19B10007-E8F2-537E-4F6C-D104768A1214"
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
                               
        else:
            print("could not find target bluetooth device nearby")
    
    async def get_characteristic_value(self):
        try:
            print("Leggo:", "19B10007-E8F2-537E-4F6C-D104768A1214")
            data = await self.client.read_gatt_char("19B10002-E8F2-537E-4F6C-D104768A1214")
            data = data.decode('utf-8') #convert byte to str
            print("data: {}".format(data))
        except Exception as ex:
            print("Errore:", ex)


async def init_server():
    # Indirizzo IP e porta del server
    server_address = ('127.0.0.1', 5005)

    # Creazione del server
    server = await asyncio.start_server(handle_client, *server_address)
    
    async with server:
        # Il server rimane in ascolto delle connessioni
        print("Avvio server...")
        await server.serve_forever()

    print("OK")

########################################################################

manager = BluetoothManager()

async def main():
    await manager.init_ble()    
    await init_server()
    
    
    

    

# Avvio del server
asyncio.run(main())