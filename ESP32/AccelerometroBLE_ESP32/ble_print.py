import asyncio
import bleak

async def notification_handler(sender, data):
    print(f"Received data from {sender}: {data}")

async def run():
    device_name = "ACC"  # Inserire il nome del dispositivo BLE
    service_uuid = "19B10000-E8F2-537E-4F6C-D104768A1214"  # Inserire l'UUID del servizio
    characteristic_uuid = "19B10001-E8F2-537E-4F6C-D104768A1214"  # Inserire l'UUID della caratteristica

    scanner = bleak.BleakScanner()
    devices = await scanner.discover()

    for device in devices:
        if device.name == device_name:
            async with bleak.BleakClient(device) as client:
                await client.connect()
                await client.start_notify(characteristic_uuid, notification_handler)
                print(f"Connected to {device_name}")
                while True:
                    await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
