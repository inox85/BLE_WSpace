import asyncio
from bleak import BleakClient, BleakScanner

CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"  # Esempio di UUID di una caratteristica
DEVICE_NAME = "Accelerometro"  # Nome del dispositivo da cercare


async def handle_notification(sender, data):
    value = int.from_bytes(data, byteorder="little")  # Converti i dati ricevuti in un intero
    print("Valore ricevuto:", value)


async def main():
    scanner = BleakScanner()
    devices = await scanner.discover()
    device_address = None
    for device in devices:
        if device.name == DEVICE_NAME:
            device_address = device
            break

    if device_address is None:
        print(f"Dispositivo '{DEVICE_NAME}' non trovato.")
        return

    async with BleakClient(device_address) as client:
        await client.start_notify(CHARACTERISTIC_UUID, handle_notification)
        #await asyncio.sleep(30)  # Durata in secondi per cui si desidera ricevere le notifiche
        #await client.stop_notify(CHARACTERISTIC_UUID)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())