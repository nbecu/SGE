import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QMenu, QAction, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.animation import FuncAnimation

class SGDiagramTest(QMainWindow):
    def __init__(self, xValue, cell_data, agent_data):
        super(SGDiagramTest, self).__init__()

        self.fig, self.ax = plt.subplots()
        self.cell_data = cell_data
        self.agent_data = agent_data
        self.xValue = xValue
        self.xmin = 1
        self.xmax = 7

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QHBoxLayout(self.central_widget)
        graph_layout = QVBoxLayout(self.central_widget)
        sidebar_layout = QVBoxLayout()

        self.lines_cell, = self.ax.plot([], [], label='Cell')
        self.min_cell_line = self.ax.axhline(0, linestyle='--', color='gray', label='Min: cell')
        self.max_cell_line = self.ax.axhline(0, linestyle='dashdot', color='black', label='Max: cell')
        self.std_cell_line = self.ax.axhline(0, linestyle='dotted', color='green', label='Ecart Type: cell')
        self.lines_agent, = self.ax.plot([], [], label='Agent')
        self.min_agent_line = self.ax.axhline(0, linestyle='--', color='orange', label='Min: agent')
        self.max_agent_line = self.ax.axhline(0, linestyle='dashdot', color='red', label='Max: agent')
        self.std_agent_line = self.ax.axhline(0, linestyle='dotted', color='pink', label='Ecart Type: agent')
        # creation des actions checkbox
        self.action_checkbox_cell = QCheckBox("Données des Cells") # Number = 0
        self.action_checkbox_min_cells = QCheckBox("Données minimales des Cells")  # Number = 1
        self.action_checkbox_max_cells = QCheckBox("Données maximales des Cells")  # Number = 2
        self.action_checkbox_std_cells = QCheckBox("Données des Ecart type des Cells")  # Number = 3
        self.action_checkbox_agent = QCheckBox("Données des Agents")  # Number = 4
        self.action_checkbox_min_agent = QCheckBox("Données minimales des Agents")  # Number = 5
        self.action_checkbox_max_agent = QCheckBox("Données maximales des Agents")  # Number = 6
        self.action_checkbox_std_agent = QCheckBox("Données des Ecart type des Agents")  # Number = 7
        # connexion des actions
        self.action_checkbox_cell.stateChanged.connect(lambda isChecked=self.action_checkbox_cell.isChecked(): self.display_line(isChecked, numberBtn=0))
        self.action_checkbox_min_cells.stateChanged.connect(lambda isChecked=self.action_checkbox_min_cells.isChecked(): self.display_line(isChecked, numberBtn=1))
        self.action_checkbox_max_cells.stateChanged.connect(lambda isChecked=self.action_checkbox_max_cells.isChecked(): self.display_line(isChecked, numberBtn=2))
        self.action_checkbox_std_cells.stateChanged.connect(lambda isChecked=self.action_checkbox_std_cells.isChecked(): self.display_line(isChecked, numberBtn=3))
        self.action_checkbox_agent.stateChanged.connect(lambda isChecked=self.action_checkbox_agent.isChecked(): self.display_line(isChecked, numberBtn=4))
        self.action_checkbox_min_agent.stateChanged.connect(lambda isChecked=self.action_checkbox_min_agent.isChecked(): self.display_line(isChecked, numberBtn=5))
        self.action_checkbox_max_agent.stateChanged.connect(lambda isChecked=self.action_checkbox_max_agent.isChecked(): self.display_line(isChecked, numberBtn=6))
        self.action_checkbox_std_agent.stateChanged.connect(lambda isChecked=self.action_checkbox_std_agent.isChecked(): self.display_line(isChecked, numberBtn=7))

        sidebar_layout.addWidget(self.action_checkbox_cell)
        sidebar_layout.addWidget(self.action_checkbox_min_cells)
        sidebar_layout.addWidget(self.action_checkbox_max_cells)
        sidebar_layout.addWidget(self.action_checkbox_std_cells)
        sidebar_layout.addWidget(self.action_checkbox_agent)
        sidebar_layout.addWidget(self.action_checkbox_min_agent)
        sidebar_layout.addWidget(self.action_checkbox_max_agent)
        sidebar_layout.addWidget(self.action_checkbox_std_agent)
        sidebar_layout.setSpacing(0)

        self.canvas = FigureCanvas(self.fig)
        self.ax.set_xlabel('Phase')
        self.ax.set_ylabel('Nombre par phase')
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.legend()
        graph_layout.addWidget(self.canvas)

        layout.addLayout(sidebar_layout, stretch=1)
        layout.addLayout(graph_layout, stretch= 4)
        self.setWindowTitle("Diagramme d'évolution des données en temps réelles")



        self.set_all_checkbox_checked()

        self.ani = FuncAnimation(self.fig, self.update, frames=range(1000), interval=1000)

    def update_data(self):
        self.ani = FuncAnimation(self.fig, self.update, frames=range(1000), interval=1000)
        #plt.show()

    def set_all_checkbox_checked(self):
        checkboxes = [
            self.action_checkbox_cell,
            self.action_checkbox_min_cells,
            self.action_checkbox_max_cells,
            self.action_checkbox_std_cells,
            self.action_checkbox_agent,
            self.action_checkbox_min_agent,
            self.action_checkbox_max_agent,
            self.action_checkbox_std_agent,
        ]
        for checkbox in checkboxes:
            checkbox.setChecked(True)

        # Affichage selon le critéres choisit dans le graph
    def display_line(self, isChecked, numberBtn):
        self.hide_line(numberBtn, isChecked)

    def hide_line(self, number, isChecked):
        try:
            if number >= 0 and number < len(self.ax.lines) and self.ax.lines[number] is not None:
                if isChecked == 2:
                    self.ax.lines[number].set_visible(True)
                    print("DISPLAY numberBtn : {} , isChecked : {} , name : {}".format(number, isChecked,  self.ax.lines[number]._label))
                else:
                    self.ax.lines[number].set_visible(False)
                    print("HIDE numberBtn : {} , isChecked : {}".format(number, isChecked))
        except Exception as e:
            print(f"ERROR {e}")


    def update(self, frame):
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

            self.lines_cell.set_data(self.xValue[:frame + 1], self.cell_data[:frame + 1])
            self.lines_agent.set_data(self.xValue[:frame + 1], self.agent_data[:frame + 1])

            if (frame + 1) % 7 == 0:
                round_lab = f"Round {int((frame + 1) / 7)}"
                self.ax.axvline(self.xValue[frame], color='r', ls=':')
                self.ax.text(self.xValue[frame], 1, round_lab, color='r', ha='right', va='top', rotation=90,
                             transform=self.ax.get_xaxis_transform())
                print("x value axvline : ", self.xValue[frame])


            return (self.lines_cell, self.lines_agent, self.min_cell_line, self.max_cell_line, self.std_cell_line,
                    self.min_agent_line, self.max_agent_line, self.std_agent_line)

