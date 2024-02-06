import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QMenu, QLabel, QAction, QCheckBox, QComboBox, QPushButton
from PyQt5.QtCore import Qt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtCore import pyqtSignal, QTimer, Qt

class SGToolBar(NavigationToolbar):
    def __init__(self, canvas, parent, typeDiagram):
        super().__init__(canvas, parent)
        self.parent = parent
        self.xValue = []
        self.cell_data = []
        self.agent_data = []

        self.addSeparator()

        # typeDiagram values : plot , pie , hist , stackplot
        if typeDiagram == 'plot':
            # Menu for choosing x-axis data
            #self.x_data_label = QLabel("X - Abcisses")
            self.x_data_menu = QComboBox(self)
            self.x_data_menu.addItems(["SGEntities", "SimVariables", "SGEntityDef", "Player 1", "Player 2", "GameActions"])
            self.x_data_menu.currentIndexChanged.connect(self.update_plot)
            #self.addWidget(self.x_data_label)
            self.addWidget(self.x_data_menu)

            """# Menu for choosing y-axis data
            self.y_data_label = QLabel("Y - Ordonnées")
            self.y_data_menu = QComboBox(self)
            self.y_data_menu.addItems(["SGEntities", "SimVariables", "SGEntityDef", "Players1", "Players2", "GameActions"])
            self.y_data_menu.currentIndexChanged.connect(self.update_plot)
            self.addWidget(self.y_data_label)
            self.addWidget(self.y_data_menu)"""


        self.display_indicators_menu = QMenu("Indicators", self)

        self.options_menu = QMenu("Options", self)
        self.options_menu = QComboBox(self)
        items = {'Tous les tours' : '0', 'Dernieres Tours' : '1', 'Autres': '2'}
        for display_text, index in items.items():
            self.options_menu.addItem(display_text, index)


        #self.options_menu.addItems(["Dernieres Tours", "Tous les tours", "Autres"])
        self.options_menu.currentIndexChanged.connect(self.update_plot)
        self.addWidget(self.options_menu)
        """
        self.combo_box = QComboBox(self)
        layout.addWidget(self.combo_box)

        # Add key-value pairs to the combo box
        items = {'Option 1': 'Value 1', 'Option 2': 'Value 2', 'Option 3': 'Value 3'}
        for display_text, value in items.items():
            self.combo_box.addItem(display_text, value)

        # Connect a slot to handle item selection
        self.combo_box.currentIndexChanged.connect(self.handle_selection)

        """
        self.display_checkboxes = {}

        display_indicators = ["type", "Nombre d’individus de ce type", "quantité d’énergie", "Mean", "Min", "Max", "St Dev", "Nom de l'attribut"]

        for option in display_indicators:
            action = QAction(option, self, checkable=True)
            action.setChecked(True)
            action.triggered.connect(self.update_plot)
            self.display_indicators_menu.addAction(action)
            self.display_checkboxes[option] = action

        self.addSeparator()
        self.addAction(self.display_indicators_menu.menuAction())
        # Créez un menu supplémentaire
        """self.custom_menu = QMenu("Custom Menu", parent)

        # Ajoutez une action au menu
        custom_action = QAction("Custom Action", parent)
        custom_action.triggered.connect(self.custom_action_triggered)
        self.custom_menu.addAction(custom_action)



        # Ajoutez le menu à la barre d'outils
        self.addWidget(self.custom_menu)"""

    def custom_action_triggered(self):
        print("test")

    def onchangeValue(self):
        # Dernieres Tours
        option_menu = self.options_menu.currentText()
    def update_plot(self):
        # Retrieve selected x and y data
        x_data = self.x_data_menu.currentText()
        #y_data = self.y_data_menu.currentText()
        option_menu = self.options_menu.currentText()
        selected_indicators = [option for option, checkbox in self.display_checkboxes.items() if checkbox.isChecked()]

        #self.parent.update_plot()
        self.onchange_option_menu()
        #print("xValue : ", self.parent.xValue)
        #print("currentIndex : ", self.options_menu.currentIndex())
        #print("xValue : ", self.xValue)
        print(f"X-axis data: {x_data}")
        print(f"option_menu data: {option_menu}")
        print(f"Selected display indicators: {selected_indicators}")

    def onchange_option_menu(self):
        if self.options_menu.currentIndex() == 0:
            rounds = list(set(entry['round'] for entry in self.parent.data))
        elif self.options_menu.currentIndex() == 1:
            last_round = max(entry['round'] for entry in self.parent.data)
            rounds = [last_round]
        else:
            rounds = list(set(entry['round'] for entry in self.parent.data)) # a changer
        #print("self.options_menu.currentIndex :: ", self.options_menu.currentIndex())
        self.onchage_data(rounds)
        #print("rounds : ", rounds)

    def get_filtered_data(self, rounds):
        data = self.parent.data
        players = list(set(entry['currentPlayer'] for entry in self.parent.data if
                           self.x_data_menu.currentText() == entry['currentPlayer']))

        phases = {entry['phase'] for entry in data}
        if len(rounds) == 1:
            self.xValue = [p for _ in rounds for p in phases]
        else:
            self.xValue = [r * len(phases) + p for r in rounds for p in phases]
        if len(players) > 1 or 'player' in str(self.x_data_menu.currentText()).lower():
            filtered_data = [entry for entry in data if entry['currentPlayer'] in players]
        else:
            filtered_data = data
        return filtered_data

    def onchage_data(self, rounds, key_line_filtered):
        filtered_data = self.get_filtered_data(rounds)
        phases = {entry['phase'] for entry in filtered_data}
        cell_data = [sum(1 for entry in filtered_data if
                         entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Cell')
                     for r in rounds for p in phases]
        agent_data = [sum(1 for entry in filtered_data if
                          entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Agent')
                      for r in rounds for p in phases]
        self.parent.xValue = self.xValue
        self.onchage_plot(self.xValue, cell_data, agent_data)

    """def onchage_data(self, rounds, players):
        data = self.parent.data
        phases = set(entry['phase'] for entry in data)
        if len(rounds) == 1:
            self.xValue = [p for r in rounds for p in phases]
        else:
            self.xValue = [r * len(phases) + p for r in rounds for p in phases]
        cell_data = [ sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Cell')
            for r in rounds for p in phases]
        agent_data = [ sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Agent')
            for r in rounds for p in phases]
        if  len(players)>1 or str( self.x_data_menu.currentText()).lower().__contains__('player'):
            cell_data = [sum(1 for entry in data if entry['currentPlayer'] in players and entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Cell')
                for r in rounds for p in phases]
            agent_data = [sum(1 for entry in data if entry['currentPlayer'] in players and entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Agent')
                          for r in rounds for p in phases]
        self.parent.xValue = self.xValue
        # print("rounds : ", rounds)
        self.onchage_plot(self.xValue, cell_data, agent_data)
        print("currentIndex : ", self.options_menu.currentIndex())
        print("x_data_menu : ", self.x_data_menu.currentText())
        print("self.parent.xValue : ", self.parent.xValue)
        print("players : ", players)
        print("agent_data : ", agent_data)
        print("current phase : ", self.parent.parent.timeManager.currentPhase)"""


    def onchage_plot(self, xValue, cell_data, agent_data):
        self.parent.xValue = xValue #list(phases)
        self.parent.agent_data = agent_data
        self.parent.cell_data = cell_data
        self.parent.ax.clear()
        self.parent.ax.set_xlim(0, max(self.parent.xValue))
        self.parent.lines_cell.set_data(self.parent.xValue, self.parent.cell_data)
        self.parent.lines_agent.set_data(self.parent.xValue, self.parent.agent_data)
        # Redraw the lines
        self.parent.ax.plot(self.parent.xValue, self.parent.cell_data)
        self.parent.ax.plot(self.parent.xValue, self.parent.agent_data)
        self.parent.canvas.draw()

    def plot_lines(self, data, rounds, dict_keyfilter, xValue, linestyles, colors):
        phases = {entry['phase'] for entry in data}
        self.parent.ax.clear()
        for i, key in enumerate(dict_keyfilter):
            linestyle = linestyles[i % len(linestyles)]
            color = colors[i % len(colors)]
            line_data = [
                sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry[key] == 'Cell')
                for r in rounds for p in phases]
            self.parent.ax.plot(xValue, line_data, label= str(key).upper(), linestyle=linestyle, color=color)
            #self.parent.ax.plot(self.parent.xValue, np.sin(self.parent.xValue) + i, label=key, linestyle=linestyle, color=color)
            self.parent.ax.axhline(y=i, linestyle=linestyle, color=color, alpha=0.5)
        # Add legend
        self.parent.ax.set_xlim(0, max(xValue))
        self.parent.canvas.draw()

    """
    def getAllData(self):
        data = self.getAllHistoryData()
        phases = set(entry['phase'] for entry in data)
        rounds = set(entry['round'] for entry in data)
        self.cell_data = [
            sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Cell')
            for r in rounds for p in phases]
        self.agent_data = [
            sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Agent')
            for r in rounds for p in phases]
        self.xValue = [r * len(phases) + p for r in rounds for p in phases]
        self.data = data
    """