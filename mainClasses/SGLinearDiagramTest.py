import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class SGLinearDiagramTest:
    def __init__(self, xValue, cell_data, agent_data):
        self.cell_data = cell_data
        self.agent_data = agent_data
        self.shrub_data = []
        self.xValue= xValue


    def plot_diagram(self):
        plt.plot(self.xValue, self.cell_data, label='cell')
        #plt.plot(self.xValue, self.agent_data, label='agent')

        plt.axhline(np.min(self.cell_data), linestyle='--', color='gray', label='Min: cell')
        plt.axhline(np.max(self.cell_data), linestyle='dashdot', color='black', label='Max: cell')
        plt.axhline(np.std(self.cell_data), linestyle='dotted', color='green', label='Ecart Type: cell')

        plt.axhline(np.min(self.agent_data), linestyle='--', color='orange', label='Min: agent')
        plt.axhline(np.max(self.agent_data), linestyle='dashdot', color='red', label='Max: agent')
        plt.axhline(np.std(self.agent_data), linestyle='dotted', color='pink', label='Ecart Type: agent')

        plt.xlabel('Phase')
        plt.ylabel('Nombre par phase')
        plt.legend()

        #ani = FuncAnimation(plt.subplots(), self.update, frames=range(1000), interval=500)

        # ani.resume()
        plt.show()
