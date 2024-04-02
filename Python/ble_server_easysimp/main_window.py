import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMainWindow, QHBoxLayout
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
import datetime
import atexit

manager = BluetoothManager()

class RealTimePlotWidget(FigureCanvas):
    data_updated = pyqtSignal()

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots()
        self.x_data = []
        self.y_data = []
        super(RealTimePlotWidget, self).__init__(self.fig)
        self.setParent(parent)
        self.init_plot()
        self.data_updated.connect(self.update_plot)

    def init_plot(self):
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Real Time Plot')

    def update_plot(self):
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Real Time Plot')
        self.draw()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.real_time_plot_widget = RealTimePlotWidget(self)
        self.init_ui()
        self.manager = BluetoothManager()
        self.char_dictionary = dict()
        self.setStyleSheet(button_style)
        
        # Inizializziamo un timer per aggiornare il grafico

    def init_ui(self):
        layout = QVBoxLayout()
        buttons_row = QHBoxLayout()

        self.button = QPushButton('Connetti dispositivo')
        self.button.clicked.connect(self.on_connect_click)
        
        self.rec_button = QPushButton('Verifica stato')
        self.rec_button.clicked.connect(self.on_state_button_click)

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
    
    async def read_ble(self):
        while(1):
            print("Recupero valori da BLE...")
            self.char_dictionary = await manager.get_all_characteristc_values()
            print(self.char_dictionary)
            time.sleep(1)

    def on_connect_click(self):
        asyncio.ensure_future(self.async_event())

    def on_state_button_click(self):
        print(manager.bluethooth_state.is_connected)

    async def async_event(self):
        self.button.setText("Ricerca dispositivo Easysimp in corso...")
        print("Avvio evento asincrono...")
        await manager.init_ble()
        self.button.setText(f"Connesso al dispositivo {manager.bluethooth_state.device_connected_name} [{manager.bluethooth_state.device_connected_address}]")
        print("Evento asincrono completato")
        self.read_ble_thread()
        self.init_real_time_plot()
    
    def run_async_read_ble(self):
        # Esegui la funzione read_ble all'interno di un loop di eventi asyncio
        asyncio.run(self.read_ble())

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