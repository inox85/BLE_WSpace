import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMainWindow
from PyQt5.QtCore import QEventLoop
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
        self.init_real_time_plot()
        self.init_ui()
        self.manager = BluetoothManager()
        
        # Inizializziamo un timer per aggiornare il grafico

    def init_ui(self):
        layout = QVBoxLayout()

        self.button = QPushButton('Connetti ble')
        self.button.clicked.connect(self.on_connect_click)
        
        self.state_button = QPushButton('Verifica stato')
        self.state_button.clicked.connect(self.on_state_button_click)

    
        layout.addWidget(self.button)
        layout.addWidget(self.state_button)

        
        layout.addWidget(self.real_time_plot_widget)

        self.setLayout(layout)
        self.setWindowTitle('Server TCP/IP')
        self.setGeometry(100, 100, 300, 200)
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

    def on_connect_click(self):
        asyncio.ensure_future(self.async_event())

    def on_state_button_click(self):
        print(manager.bluethooth_state.is_connected)

    async def async_event(self):
        print("Avvio evento asincrono...")
        await manager.init_ble()
        self.state_label.setText(str(manager.bluethooth_state.is_connected))
        self.button.setText(f"Connesso al dispositivo {manager.bluethooth_state.device_connected_name} [{manager.bluethooth_state.device_connected_address}]")
        print("Evento asincrono completato")
        

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