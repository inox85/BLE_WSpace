import asyncio
import random
import sys
import threading
import time
from datetime import datetime
import asyncqt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from lib.ble_manager import BluetoothManager
from lib.realtime_plot import RealTimePlotWidget
from lib.style import gui_style


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.export_button = None
        self.rec_button = None
        self.connect_button = None
        self.close_button = None
        self.change_graph_interval_button = None
        self.setWindowIcon(QIcon('icon.ico'))  # Imposta l'icona  
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)  # Rimuove il pulsante di chiusura
        self.real_time_plot_widget = RealTimePlotWidget(self)
        self.init_ui()
        self.manager = BluetoothManager()
        self.char_dictionary = dict()
        self.setStyleSheet(gui_style)
        self.requested_characteristics = []
        self.read_ble_thread_active = False
        self.thread_ble = threading.Thread()
        self.graph_interval = 0
        self.start_datetime = None

    def init_requested_chacteristic_dictionary(self):
        # self.requested_characteristics["GSR"] = "19B10002-E8F2-537E-4F6C-D104768A1214" 
        self.requested_characteristics = [["GSR", "19B10002-E8F2-537E-4F6C-D104768A1214", "int"],
                                          ["Battery", "19B12A19-E8F2-537E-4F6C-D104768A1214", "int"]]

    def init_ui(self):
        main_layout = QHBoxLayout()
        gui_layout = QVBoxLayout()
        buttons_row1 = QHBoxLayout()
        buttons_row2 = QHBoxLayout()

        self.connect_button = QPushButton('Connetti dispositivo')
        self.connect_button.clicked.connect(self.on_connect_click)

        self.rec_button = QPushButton('Inizia registrazione')
        self.export_button = QPushButton('Esporta CSV')
        self.close_button = QPushButton('Esci')
        self.close_button.setStyleSheet("background-color: #EB6565;")
        self.close_button.clicked.connect(self.on_close_click)
        self.close_button.setFixedWidth(100)

        self.change_graph_interval_button = QPushButton(f'Intervallo grafico: Completo')
        self.change_graph_interval_button.clicked.connect(self.on_change_interval_click)

        buttons_row1.addWidget(self.connect_button)
        buttons_row1.addWidget(self.rec_button)
        buttons_row1.addWidget(self.export_button)
        buttons_row1.addWidget(self.close_button)

        buttons_row2.addWidget(self.change_graph_interval_button)

        gui_layout.addLayout(buttons_row1)
        gui_layout.addWidget(self.real_time_plot_widget)
        gui_layout.addLayout(buttons_row2)

        main_layout.addLayout(gui_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('EasySimp')
        self.setGeometry(30, 100, 1500, 1000)

        self.show()

    # def init_real_time_plot(self):
    #     self.timer = QTimer(self)
    #     self.timer.timeout.connect(self.update_plot)
    #     self.timer.start(1000)

    def update_plot(self, x_value, y_value):
        # Aggiorniamo i dati del grafico con nuovi valori casuali
        self.real_time_plot_widget.x_data.append(x_value)
        self.real_time_plot_widget.y_data.append(y_value)
        self.real_time_plot_widget.data_updated.emit()

    def on_change_interval_click(self):
        if self.graph_interval == 0:
            self.graph_interval = 10
        elif self.graph_interval > 3600:
            self.graph_interval = 0
        else:
            self.graph_interval = self.graph_interval * 2

        self.real_time_plot_widget.set_plot_interval(self.graph_interval)
        btn_message = f"Intervallo grafico: {self.real_time_plot_widget.get_plot_interval()} secondi"
        if self.real_time_plot_widget.get_plot_interval() == 0:
            btn_message = f"Intervallo grafico: Completo"
        self.change_graph_interval_button.setText(btn_message)

    async def read_ble_and_update_data(self):
        while self.read_ble_thread_active:
            if self.manager.bluethooth_state.is_connected:
                self.connect_button.setText(
                    f"Connesso {self.manager.bluethooth_state.device_connected_name} [{self.manager.bluethooth_state.device_connected_address}]")
                print("Lettura da BLE...")
                self.char_dictionary = await self.manager.get_characteristics(self.requested_characteristics)
                print(f"Dizionario caratteristiche: {self.char_dictionary}")
                interval = datetime.now() - self.start_datetime
                self.update_plot(interval.total_seconds(), self.char_dictionary["GSR"])
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
        #self.init_real_time_plot()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    loop = asyncqt.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # server_thread = ServerThread('localhost', 8888)
    # server_thread.start()

    window = MainWindow()

    sys.exit(app.exec_())
