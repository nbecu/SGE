import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class SGHistogramDiagram():
    def __init__(self, arr_dataModel, arr_labels, title, xLabel, yLabel):
        self.arr_dataModel = arr_dataModel
        self.xLabel = xLabel
        self.yLabel = yLabel
        self.title = title
        self.arr_labels = arr_labels
        self.fig, self.ax = plt.subplots()
        self.ax.hist(arr_dataModel, bins=10, label=arr_labels)
        self.ax.legend()
        self.ax.set_title(title)
        self.ax.set_xlabel(xLabel)
        self.ax.set_ylabel(yLabel)

    # Fonction appelée à chaque itération pour mettre a jour le diagramme
    def update(self, frame):
        arr_dataModel = self.arr_dataModel
        for i in range(len(arr_dataModel)):
            arr_dataModel[i] = np.random.rand(10)
        self.ax.cla()
        self.ax.hist(arr_dataModel, bins=10, label=self.arr_labels)
        self.ax.legend()
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xLabel)
        self.ax.set_ylabel(self.yLabel)


    def display(self):
        ani = FuncAnimation(self.fig, self.update, frames=np.arange(0, 10, 0.1), interval=1000)
        plt.show()