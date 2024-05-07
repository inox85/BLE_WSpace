import asyncio
from datetime import datetime
import time
from bleak import BleakScanner
import ShellyPy

device = ShellyPy.Shelly("192.168.13.47")
async def scan():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    devices = await BleakScanner.discover()
    global shelly_status
    for device in devices:
        #print(f"Nome: {device.name}, Indirizzo: {device.address}, {device._rssi}")
        if device.name and ("Galaxy Watch4" in device.name):
            shelly_status = True
            print(ts, "\t", device.name, "\t", device._rssi, "\t", device.address)
        else:
            shelly_status = False
            print("Non presente")

# Avvia l'esecuzione dell'asyncio loop per eseguire la scansione
loop = asyncio.get_event_loop()
#loop.run_until_complete(scan())


while True:
    loop.run_until_complete(scan())
    global shelly_status
    #shelly_status = False
    #shelly_status = not shelly_status
    device.relay(0, turn=shelly_status)
    time.sleep = 1
