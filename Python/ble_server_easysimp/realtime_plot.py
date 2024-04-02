from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from style import button_style

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