import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np



class SGLinearDiagram():
    def __init__(self, x, y1, y2, label1, label2, title):
        self.title = title
        self.fig, self.ax = plt.subplots()
        self.ax.set_title(title)
        self.x = x
        self.y1 = y1
        self.y2 = y2
        self.label1 = label1
        self.label2 = label2
        self.line1, = self.ax.plot(x, y1, label=label1)
        self.line2, = self.ax.plot(x, y2, label=label2)
        self.ax.legend()

    def update(self, frame):
        y1 = np.sin(self.x + frame * 0.1)
        y2 = np.sin(self.x + frame * 0.05)
        self.line1.set_ydata(y1)
        self.line2.set_ydata(y2)
        return self.line1, self.line2

    def display(self):
        ani = FuncAnimation(self.fig, self.update, frames=range(100), interval=500)
        plt.show()
