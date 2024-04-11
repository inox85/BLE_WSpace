from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from bleak import BleakScanner
import asyncio

class BLEApp(App):
    def __init__(self):
        super().__init__()
        self.found_devices = []

    def build(self):
        layout = BoxLayout(orientation='vertical')
        scan_button = Button(text='Scansiona Dispositivi BLE')
        scan_button.bind(on_press=self.start_scan)
        layout.add_widget(scan_button)
        return layout

    def start_scan(self, instance):
        asyncio.ensure_future(self.scan_ble_devices())

    async def scan_ble_devices(self):
        self.found_devices = []  # Resetta la lista dei dispositivi trovati
        print("Inizio scansione dispositivi BLE...")
        devices = await BleakScanner.discover()
        for dev in devices:
            print(f"Nome: {dev.name} - Indirizzo: {dev.address}")
            # Puoi aggiungere qui la logica per mostrare i dispositivi nella GUI

if __name__ == '__main__':
    BLEApp().run()