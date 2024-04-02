import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
import socket
import threading
from server import ServerThread
from ble_manager import BluetoothManager
import asyncio
import asyncqt
from PyQt5.QtCore import QTimer, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import random
import time
from style import button_style
from realtime_plot import RealTimePlotWidget

manager = BluetoothManager()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.real_time_plot_widget = RealTimePlotWidget(self)
        self.init_ui()
        self.manager = BluetoothManager()
        self.char_dictionary = dict()
        self.setStyleSheet(button_style)
        self.requested_characteristics = dict()
        

    def init_requested_chacteristic_dictionary(self):
        self.requested_characteristics["GSR"] = "19B10002-E8F2-537E-4F6C-D104768A1214" 

    def init_ui(self):
        layout = QVBoxLayout()
        buttons_row = QHBoxLayout()

        self.button = QPushButton('Connetti dispositivo')
        self.button.clicked.connect(self.on_connect_click)
        
        self.rec_button = QPushButton('Verifica stato')

        self.rec_button = QPushButton('Inizia registrazione')
        self.export_button = QPushButton('Esporta CSV')
        
        buttons_row.addWidget(self.button)
        buttons_row.addWidget(self.rec_button)
        buttons_row.addWidget(self.export_button)

        layout.addLayout(buttons_row)
        #layout.addWidget(self.state_button)
        #layout.addWidget(self.state_button1)
        
        layout.addWidget(self.real_time_plot_widget)

        self.setLayout(layout)
        self.setWindowTitle('EasySimp')
        self.setGeometry(30, 100, 1000, 1000)
        self.show()

    def init_real_time_plot(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)
    
    def update_plot(self):
        # Aggiorniamo i dati del grafico con nuovi valori casuali
        self.real_time_plot_widget.x_data.append(len(self.real_time_plot_widget.x_data))
        self.real_time_plot_widget.y_data.append(random.randint(0, 100))
        self.real_time_plot_widget.data_updated.emit()
    
    async def read_ble_and_update_data(self):
        while(1):
            print("Recupero valori da BLE...")
            self.char_dictionary = await manager.get_characteristics(self.requested_characteristics)
            print(self.char_dictionary)
            time.sleep(1)

    def on_connect_click(self):
        self.init_requested_chacteristic_dictionary()
        asyncio.ensure_future(self.async_event())

    async def async_event(self):
        self.button.setText("Ricerca dispositivo Easysimp in corso...")
        print("Ricerca dispositivo Easysimp in corso...")
        await manager.init_ble()
        self.button.setText(f"Connesso {manager.bluethooth_state.device_connected_name} [{manager.bluethooth_state.device_connected_address}]")
        print(f"Connesso al dispositivo {manager.bluethooth_state.device_connected_name} [{manager.bluethooth_state.device_connected_address}]")
        self.read_ble_thread()
        self.init_real_time_plot()
    
    def run_async_read_ble(self):
        # Esegui la funzione read_ble all'interno di un loop di eventi asyncio
        asyncio.run(self.read_ble_and_update_data())

    def read_ble_thread(self):
        thread = threading.Thread(target=self.run_async_read_ble)
        thread.start()  

    async def connect_ble():
        # Simula un'operazione asincrona
        print("Inizio connessione BLE...")
        await manager.init_ble()
        print("Connessione BLE effettuata")



if __name__ == '__main__':
    app = QApplication(sys.argv)

    loop = asyncqt.QEventLoop(app)
    asyncio.set_event_loop(loop)

    #server_thread = ServerThread('localhost', 8888)
    #server_thread.start()

    window = MainWindow()

    sys.exit(app.exec_())