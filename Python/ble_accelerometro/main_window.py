import asyncio
import sys
import threading
import time
from datetime import datetime
import asyncqt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from lib.ble_manager import BluetoothManager
from lib.realtime_plot import StorageAndPlot
from lib.style import gui_style
from pathlib import Path


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.storage_and_plot = StorageAndPlot(self)
        self.init_ui()
        self.manager = BluetoothManager()
        self.char_dictionary = dict()
        self.setStyleSheet(gui_style)
        self.requested_characteristics = []
        self.read_ble_thread_active = False
        self.thread_ble = threading.Thread()
        self.graph_interval = 0
        self.start_datetime = None

    def init_ui(self):
        main_layout = QHBoxLayout()

        main_layout.addWidget(self.storage_and_plot)

        self.setLayout(main_layout)
        self.setWindowTitle('Accelerometro')
        self.setGeometry(30, 100, 1500, 1000)

        self.show()

    def update_gui_informations(self, time_value, gsr_value, hr_value, temperature_value):
        self.gsr_label.setText(f"GSR: {str(round(gsr_value, 2))} µS/cm")
        self.hr_label.setText(f"HR: {str(round(hr_value, 0))} beat/min")
        self.temperature_label.setText(f"Temperature: {str(round(temperature_value, 1))} °C")
        self.storage_and_plot.datetime_data.append(datetime.now())
        self.storage_and_plot.x_data.append(time_value)
        self.storage_and_plot.data_updated.emit()

    async def read_ble_and_update_data(self):
        while self.read_ble_thread_active:
            if self.manager.bluethooth_state.is_connected:
                self.connect_button.setText(
                    f"Connesso {self.manager.bluethooth_state.device_connected_name} [{self.manager.bluethooth_state.device_connected_address}]")
                self.char_dictionary = await self.manager.get_characteristics(self.requested_characteristics)
                print(f"Dizionario caratteristiche: {self.char_dictionary}")
                interval = datetime.now() - self.start_datetime
                self.update_gui_informations(interval.total_seconds(), self.char_dictionary["GSR"],
                                             self.char_dictionary["HR"], self.char_dictionary["Temperature"])
                time.sleep(1)
            else:
                self.connect_button.setText("Connetti dispositivo")
                break
        print("Termino thread letture BLE")

    def on_connect_click(self):
        self.init_requested_chacteristic_dictionary()
        asyncio.ensure_future(self.async_event())

    def on_close_click(self):
        self.read_ble_thread_active = False
        if self.thread_ble.is_alive():
            self.thread_ble.join()
        exit()

    async def async_event(self):
        self.connect_button.setText("Ricerca dispositivo Easysimp in corso...")
        print("Ricerca dispositivo Easysimp in corso...")
        await self.manager.init_ble()
        print(
            f"Connesso al dispositivo {self.manager.bluethooth_state.device_connected_name} [{self.manager.bluethooth_state.device_connected_address}]")
        self.start_datetime = datetime.now()
        self.read_ble_thread()
        # self.init_real_time_plot()

    def run_async_read_ble(self):
        self.read_ble_thread_active = True
        asyncio.run(self.read_ble_and_update_data())

    def read_ble_thread(self):
        self.thread_ble = threading.Thread(target=self.run_async_read_ble)
        self.thread_ble.start()

    async def connect_ble(self):
        print("Inizio connessione BLE...")
        await self.manager.init_ble()
        print("Connessione BLE effettuata")

    def set_button_text(self, text):
        self.connect_button.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    loop = asyncqt.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()

    # server_thread = ServerThread('127.0.0.1', 5005)
    # server_thread.start()

    sys.exit(app.exec_())
