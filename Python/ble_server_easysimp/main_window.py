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
        self.temperature_label = None
        self.hr_label = None
        self.export_button = None
        self.rec_button = None
        self.connect_button = None
        self.close_button = None
        self.change_graph_interval_button = None
        self.gsr_label = None

        self.setWindowIcon(QIcon('icon.ico'))  # Imposta l'icona  
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)  # Rimuove il pulsante di chiusura
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

    def init_requested_chacteristic_dictionary(self):
        # self.requested_characteristics["GSR"] = "19B10002-E8F2-537E-4F6C-D104768A1214" 
        self.requested_characteristics = [["Battery_level", "19B12A19-E8F2-537E-4F6C-D104768A1214", "int", 1],
                                          ["GSR", "19B10002-E8F2-537E-4F6C-D104768A1214", "int", 0.001],
                                          ["GSR_Raw", "19B10003-E8F2-537E-4F6C-D104768A1214", "int", 1],
                                          ["HR", "19B10004-E8F2-537E-4F6C-D104768A1214", "float", 0.01],
                                          ["Temperature", "19B10005-E8F2-537E-4F6C-D104768A1214", "float", 0.01]]

    def init_ui(self):
        main_layout = QHBoxLayout()
        gui_layout = QVBoxLayout()
        buttons_row1 = QHBoxLayout()
        buttons_row2 = QHBoxLayout()
        label_row1 = QHBoxLayout()

        self.connect_button = QPushButton('Connetti dispositivo')
        self.connect_button.clicked.connect(self.on_connect_click)

        self.rec_button = QPushButton('Resetta registrazione')
        self.rec_button.clicked.connect(self.on_rec_button_click)
        self.export_button = QPushButton('Esporta CSV')
        self.export_button.clicked.connect(self.on_export_button_click)
        self.close_button = QPushButton('Esci')
        self.close_button.setStyleSheet("background-color: #EB6565;")
        self.close_button.clicked.connect(self.on_close_click)
        self.close_button.setFixedWidth(150)

        self.change_graph_interval_button = QPushButton(f'Intervallo visualizzazione: Completo')
        self.change_graph_interval_button.clicked.connect(self.on_change_interval_click)

        self.gsr_label = QLabel("GSR: --- µS/cm")
        self.gsr_label.setAlignment(Qt.AlignCenter)
        self.gsr_label.setFixedHeight(50)

        self.hr_label = QLabel("HR: --- beat/min")
        self.hr_label.setAlignment(Qt.AlignCenter)
        self.hr_label.setFixedHeight(50)

        self.temperature_label = QLabel("Temperature: --- °C")
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setFixedHeight(50)

        label_row1.addWidget(self.gsr_label)
        label_row1.addWidget(self.hr_label)
        #label_row1.addWidget(self.temperature_label)

        buttons_row1.addWidget(self.connect_button)
        buttons_row1.addWidget(self.export_button)
        buttons_row1.addWidget(self.close_button)
        buttons_row2.addWidget(self.change_graph_interval_button)
        buttons_row2.addWidget(self.rec_button)

        gui_layout.addLayout(buttons_row1)
        gui_layout.addWidget(self.storage_and_plot)
        gui_layout.addLayout(label_row1)
        gui_layout.addLayout(buttons_row2)

        main_layout.addLayout(gui_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('EasySimp')
        self.setGeometry(30, 100, 1500, 1000)

        self.show()

    def update_gui_informations(self, time_value, gsr_value, hr_value, temperature_value):
        self.gsr_label.setText(f"GSR: {str(round(gsr_value, 2))} µS/cm")
        self.hr_label.setText(f"HR: {str(round(hr_value, 0))} beat/min")
        self.temperature_label.setText(f"Temperature: {str(round(temperature_value, 1))} °C")

        self.storage_and_plot.datetime_data.append(datetime.now())
        self.storage_and_plot.x_data.append(time_value)
        self.storage_and_plot.gsr_data.append(gsr_value)
        self.storage_and_plot.hr_data.append(hr_value)
        self.storage_and_plot.temperature_data.append(temperature_value)
        self.storage_and_plot.data_updated.emit()

    def get_default_file_name(self):
        # Ottieni la data e l'ora attuali
        current_datetime = datetime.now()
        # Formatta la data e l'ora nel formato desiderato (YYYY-MM-DD_HH-MM-SS)
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        # Componi il nome del file
        file_name = f"Rec_{formatted_datetime}.csv"
        return file_name

    def on_export_button_click(self):
        print("Apertura finestra salvataggio file...")
        options = QFileDialog.Options()
        try:
            default_directory = str(Path.cwd())  # Directory di esecuzione del programma
            default_file_name = self.get_default_file_name()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", default_file_name,"All Files (*);;CSV Files (*.csv)",
                                                       default_directory, options=options)

            if file_name:
                print("File salvato come:", file_name)
        except Exception as e:
            print("Errore durante l'apertura della finestra di dialogo per il salvataggio del file:", str(e))

    def on_rec_button_click(self):
        self.start_datetime = datetime.now()
        self.storage_and_plot.reset_data()

    def on_change_interval_click(self):
        if self.graph_interval == 0:
            self.graph_interval = 10
        elif self.graph_interval > 3600:
            self.graph_interval = 0
        else:
            self.graph_interval = self.graph_interval * 2

        self.storage_and_plot.set_plot_interval(self.graph_interval)
        btn_message = f"Intervallo visualizzazione: {self.storage_and_plot.get_plot_interval()} secondi"
        if self.storage_and_plot.get_plot_interval() == 0:
            btn_message = f"Intervallo visualizzazione: Completo"
        self.change_graph_interval_button.setText(btn_message)

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
