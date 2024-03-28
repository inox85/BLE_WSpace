import asyncio
from bleak import BleakScanner
from bleak import BleakClient
import time

async def main():
    target_name = "Forometro"
    target_address = None

    SERVICE_UUID=        "19B10000-E8F2-537E-4F6C-D104768A1214"
    CHARACTERISTIC_UUID= "19B10007-E8F2-537E-4F6C-D104768A1214"

    devices = await BleakScanner.discover()
    for d in devices:
        print(d)
        if d.name == target_name :
            target_address = d.address
            print("found target {} bluetooth device with address {} ".format(target_name,target_address))
            break

    if target_address is not None:        
        async with BleakClient(target_address) as client:
            print(f"Connected: {client.is_connected}")
                
            while 1:
                #text = input()
                #if text == "quit":
                #    break

                #await client.write_gatt_char(CHARACTERISTIC_UUID, bytes(text, 'UTF-8'), response=True)
                
                try:
                    print("Leggo:", CHARACTERISTIC_UUID)
                    data = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    data = data.decode('utf-8') #convert byte to str
                    print("data: {}".format(data))
                except Exception as ex:
                    print("Errore:", ex)
                time.sleep(1)    
            
    else:
        print("could not find target bluetooth device nearby")


asyncio.run(main())