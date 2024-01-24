import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class SGLinearDiagramTest:
    def __init__(self, xValue, cell_data, agent_data):
        self.cell_data = cell_data
        self.agent_data = agent_data
        self.xValue = xValue
        self.xmin=1
        self.xmax=7

        self.fig, self.ax = plt.subplots()
        self.lines_cell, = plt.plot([], [], label='Cell')
        self.lines_agent, = plt.plot([], [], label='Agent')
        self.min_line = self.ax.axhline(0, linestyle='--', color='gray', label='Min: cell')
        self.max_line = self.ax.axhline(0, linestyle='dashdot', color='black', label='Max: cell')
        self.std_line = self.ax.axhline(0, linestyle='dotted', color='green', label='Ecart Type: cell')

        self.ax.axhline(0, linestyle='--', color='orange', label='Min: agent')
        self.ax.axhline(0, linestyle='dashdot', color='red', label='Max: agent')
        self.ax.axhline(0, linestyle='dotted', color='pink', label='Ecart Type: agent')

        self.ax.set_xlabel('Phase')
        self.ax.set_ylabel('Nombre par phase')
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.legend()

        self.ani = FuncAnimation(self.fig, self.update, frames=range(1000), interval=1000)
        plt.show()


    def update(self, frame):
        # Mettez à jour les données ici
        # Exemple: self.cell_data.append(nouvelle_valeur)
        #          self.agent_data.append(nouvelle_valeur_agent)
        # Mettez à jour les séparations de round après chaque 7 éléments
        if frame < len(self.xValue):
            if (frame + 1) % 7 == 0:
                self.xmin = self.xValue[frame] - 7
            else:
                if self.xValue[frame] > 7:
                    self.xmin = self.xValue[frame] - 7
            if self.xmax < self.xValue[frame]:
                self.xmax = self.xValue[frame]

            self.ax.set_xlim(1, self.xmax)

            maxY = np.max(self.agent_data)
            if np.max(self.cell_data) > maxY:
                maxY = np.max(self.cell_data)
            self.ax.set_ylim(0, maxY)
            print(" frame : {} , min {} et max {} ".format(frame, self.xmin, int(self.xValue[frame])))

            # Mise à jour des données sur le graphique
            self.lines_cell.set_data(self.xValue[:frame+1], self.cell_data[:frame+1])
            self.lines_agent.set_data(self.xValue[:frame + 1], self.agent_data[:frame + 1])

            # Mise à jour des lignes de référence
            #self.min_line.set_ydata(np.min(self.cell_data))
            #self.max_line.set_ydata(np.max(self.cell_data))
            #self.std_line.set_ydata(np.std(self.cell_data))

            # Mettez à jour les séparations de round après chaque 7 éléments
            if (frame + 1) % 7 == 0:
                #self.ax.axvline(self.xValue[frame], linestyle='-', color='gray', linewidth=2)
                round_lab = f"Round {int((frame + 1) / 7)}"
                #self.ax.vlines(x=self.xValue[frame], ymin=0, ymax=100, colors='0.75', linestyle='-', label=round_lab)
                #self.ax.legend()

                self.ax.axvline(self.xValue[frame], color='r', ls=':')
                self.ax.text(self.xValue[frame], 1, round_lab, color='r', ha='right', va='top', rotation=90,
                        transform=self.ax.get_xaxis_transform())

                print("x value axvline : ", self.xValue[frame])
            #self.ax.set_xlim(self.xmin, self.xValue[frame])

            return self.lines_cell, self.lines_agent, self.min_line, self.max_line, self.std_line