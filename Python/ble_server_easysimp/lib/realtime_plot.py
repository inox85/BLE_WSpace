from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class StorageAndPlot(FigureCanvas):
    data_updated = pyqtSignal()

    def __init__(self, parent=None, width=5, height=4, dpi=300):
        self.fig, self.ax1 = plt.subplots()  # Un solo asse y
        self.ax2 = self.ax1.twinx()  # Seconda scala sull'asse y
        self.datetime_data = []
        self.x_data = []
        self.gsr_data = []
        self.hr_data = []  # Seconda grandezza
        self.temperature_data = []
        super(StorageAndPlot, self).__init__(self.fig)
        self.setParent(parent)
        self.init_plot()
        self.data_updated.connect(self.update_plot)
        self.plot_interval = 0

    def init_plot(self):
        self.ax1.set_xlabel('Tempo [s]')
        self.ax1.set_ylabel('GSR [µS/cm]')  # Label asse y per la prima grandezza
        self.ax2.set_ylabel('HR [beat/min]')  # Label asse y per la seconda grandezza

    def update_plot(self):
        self.ax1.clear()
        self.ax2.clear()
        print(f"Intervallo impostato {self.plot_interval}")
        if self.plot_interval != 0 and len(self.x_data) > self.plot_interval:
            x_data_to_plot = self.x_data[-self.plot_interval:]
            gsr_data_to_plot = self.gsr_data[-self.plot_interval:]
            hr_data_to_plot = self.hr_data[-self.plot_interval:]
        else:
            x_data_to_plot = self.x_data
            gsr_data_to_plot = self.gsr_data
            hr_data_to_plot = self.hr_data

        self.ax1.plot(x_data_to_plot, gsr_data_to_plot, label='GSR', color='tab:blue')
        self.ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Plotta la seconda grandezza sull'asse y2
        self.ax2.plot(x_data_to_plot, hr_data_to_plot, label='HR', color='tab:red')
        self.ax2.tick_params(axis='y', labelcolor='tab:red')

        self.ax1.set_xlabel('Tempo [s]')
        self.ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 1), ncol=1)  # Legenda per il primo asse
        self.ax2.legend(loc='upper left', bbox_to_anchor=(1.05, 0.95), ncol=1)  # Legenda per il secondo asse
        self.draw()

    def set_plot_interval(self, interval_to_set):
        self.plot_interval = interval_to_set

    def get_plot_interval(self):
        return self.plot_interval

    def get_last_samples(self):
        sample_dictioary = dict(Sample_number=self.datetime_data[-1], Datetime=self.x_data[-1],
                                GSR=self.gsr_data[-1],HR=self.hr_data[-1])
    def reset_data(self):
        self.x_data = []
        self.gsr_data = []
        self.hr_data = []
