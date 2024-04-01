import asyncio
import json
from bleak import BleakScanner
from bleak import BleakClient
import time
from ble_manager import BluetoothManager

async def handle_client(reader, writer):    # Dati da inviare
    print("Ricevuta richiesta...")
    #await get_ble_characteristic_value("19B10007-E8F2-537E-4F6C-D104768A1214")

    payload = await manager.get_all_characteristc_values()

    data = {'temperature': 25, 'humidity': 50}
    message = json.dumps(payload).encode()

    # Invia i dati al client
    writer.write(message)
    await writer.drain()
    # Chiudi la connessione
    writer.close()


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