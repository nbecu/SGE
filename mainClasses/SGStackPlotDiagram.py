
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

class SGStackPlotDiagram():
    def __init__(self, data, labels, xlabel, ylabel, nb_data, ymax, title):
        self.nb_data = nb_data
        self.ymax = ymax
        self.data = data
        self.labels = labels
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        # Mise en place du diagramme Stackplot
        self.fig, self.ax = plt.subplots()
        self.ax.stackplot(range(10), self.data, labels=self.labels)

        # Configurations du graphique
        self.ax.set_title(self.title)
        self.ax.legend(loc='upper left')
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        plt.show(block=False)

    # Fonction de mise à jour des données
    def update(self, frame):
        for i in range(100):
            new_data = [np.random.rand() for _ in range(self.nb_data)]
            for j in range(self.nb_data):
                self.data[j] = np.append(self.data[j][1:], new_data[j])
            self.ax.clear()
            self.ax.stackplot(range(10), self.data, labels=self.labels)

            self.ax.set_title(self.title)
            self.ax.legend(loc='upper left')
            self.ax.set_xlabel(self.xlabel)
            self.ax.set_ylabel(self.ylabel)
            plt.pause(0.1)

    def display(self):
        ani = FuncAnimation(self.fig, self.update, frames=np.arange(0, 10, 0.1), interval=1000)
        plt.show()