from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Importa le librerie Python per il Bluetooth
from bluepy.btle import Scanner, DefaultDelegate

class BLEScanner(DefaultDelegate):
    def __init__(self, app):
        DefaultDelegate.__init__(self)
        self.app = app

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print(f"Trovato dispositivo: {dev.addr}")
            self.app.found_devices.append(dev)

class BLEApp(App):
    def __init__(self):
        super().__init__()
        self.found_devices = []

    def build(self):
        layout = BoxLayout(orientation='vertical')
        scan_button = Button(text='Scansiona Dispositivi BLE')
        scan_button.bind(on_press=self.scan_ble_devices)
        layout.add_widget(scan_button)
        return layout

    def scan_ble_devices(self, instance):
        scanner = Scanner().withDelegate(BLEScanner(self))
        self.found_devices = []  # Resetta la lista dei dispositivi trovati
        print("Inizio scansione dispositivi BLE...")
        devices = scanner.scan(10.0)  # Scansione per 10 secondi
        for dev in self.found_devices:
            print(f"Nome: {dev.getValueText(9)} - Indirizzo: {dev.addr}")
            # Puoi aggiungere qui la logica per mostrare i dispositivi nella GUI

if __name__ == '__main__':
    BLEApp().run()