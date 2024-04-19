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
        super(StorageAndPlot, self).__init__(self.fig)
        self.setParent(parent)
        self.init_plot()
        self.data_updated.connect(self.update_plot)
        self.plot_interval = 0

    def init_plot(self):
        self.ax1.set_xlabel('Tempo [s]')
        self.ax1.set_ylabel('Acc. X')  # Label asse y per la prima grandezza

    def update_plot(self):
        self.ax1.clear()
        self.ax2.clear()
        print(f"Intervallo impostato {self.plot_interval}")
        if self.plot_interval != 0 and len(self.x_data) > self.plot_interval:
            x_data_to_plot = self.x_data[-self.plot_interval:]
        else:
            x_data_to_plot = self.x_data
        self.ax1.plot(x_data_to_plot, label='GSR', color='tab:blue')
        self.ax1.tick_params(axis='y', labelcolor='tab:blue')
        self.draw()

    def set_plot_interval(self, interval_to_set):
        self.plot_interval = interval_to_set

    def get_plot_interval(self):
        return self.plot_interval

    def get_last_samples(self):
        sample_dictioary = dict(Sample_number=self.datetime_data[-1], Datetime=self.x_data[-1],
                                GSR=self.gsr_data[-1], HR=self.hr_data[-1])

    def reset_data(self):
        self.x_data = []
        self.gsr_data = []
        self.hr_data = []
