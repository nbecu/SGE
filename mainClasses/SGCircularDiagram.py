import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
class SGCircularDiagram():
    def __init__(self, data, labels, colors):
        self.data = data
        self.colors = colors
        self.labels = labels
        self.fig, self.ax = plt.subplots()
        self.ax.axis('equal')
        self.ax.pie(data, labels=labels, autopct='%1.1f%%', colors=colors)

    # Fonction appelée à chaque itération pour mettre a jour le diagramme
    def update(self, frame):
        self.data[0] = (self.data[0] + 0.01) % 1.0
        self.data[1] = (self.data[1] + 0.005) % 1.0

        self.ax.clear()
        self.ax.axis('equal')
        self.ax.pie(self.data, labels=self.labels, autopct='%1.1f%%', colors=self.colors)

    def display(self):
        ani = FuncAnimation(self.fig, self.update, frames=range(200), interval=1000)
        plt.show()