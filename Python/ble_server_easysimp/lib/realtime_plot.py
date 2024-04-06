from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class RealTimePlotWidget(FigureCanvas):
    data_updated = pyqtSignal()

    def __init__(self, parent=None, width=5, height=4, dpi=300):
        self.fig, self.ax = plt.subplots()
        self.x_data = []
        self.y_data = []
        super(RealTimePlotWidget, self).__init__(self.fig)
        self.setParent(parent)
        self.init_plot()
        self.data_updated.connect(self.update_plot)
        self.plot_interval = 0

    def init_plot(self):
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Real Time Plot')

    def update_plot(self):
        self.ax.clear()
        # Visualizza solo gli ultimi 10 campioni
        print(f"Intervallo impostato { self.plot_interval }")

        if self.plot_interval != 0 and len(self.x_data) > self.plot_interval:
            x_data_to_plot = self.x_data[-self.plot_interval:]
            y_data_to_plot = self.y_data[-self.plot_interval:]
        else:
            x_data_to_plot = self.x_data
            y_data_to_plot = self.y_data
        
        self.ax.plot(x_data_to_plot, y_data_to_plot)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Real Time Plot')
        self.draw()
    
    def set_plot_interval(self, interval_to_set):
        self.plot_interval = interval_to_set
    
    def get_plot_interval(self):
        return self.plot_interval
        