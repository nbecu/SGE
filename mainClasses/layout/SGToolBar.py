import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget, QAction, QMenu
from PyQt5.QtCore import pyqtSignal


class SGToolBar(NavigationToolbar):
    def __init__(self, canvas, parent, model, typeDiagram):
        super().__init__(canvas, parent)
        self.typeDiagram = typeDiagram
        self.data_combobox = QComboBox(parent)
        self.data_combobox.currentIndexChanged.connect(self.update_plot)

        self.data_1_combobox = QComboBox(parent)
        self.data_1_combobox.currentIndexChanged.connect(self.update_plot)
        self.addWidget(self.data_1_combobox)
        self.data_2_combobox = QComboBox(parent)
        self.data_2_combobox.currentIndexChanged.connect(self.update_plot)
        self.addWidget(self.data_2_combobox)
        self.display_indicators_menu = QMenu("Indicators", self)
        self.ax = parent.ax
        self.model = model
        self.title = 'SG Diagramme'
        self.dict_keyfilter = {}
        self.list_options = []
        self.list_indicators = []
        self.combobox_1_data = {"SGEntities": "entityName", "SGEntityDef": "entityDef", "Player": "currentPlayer"}
        self.combobox_2_data = {'Tous les tours': '0', 'Dernieres Tours': '1', 'Autres': '2'}
        self.checKbox_indicators_data = ["type", "Attribut", "Mean", "Min", "Max", "St Dev"]
        self.checKbox_indicators = {}

        self.axhlines = []
        self.linestyles = ['-', '--', '-.', ':']
        self.colors = ['gray', 'g', 'b']
        self.xValue = []


    def set_combobox_1_items(self):
        self.data_1_combobox.clear()
        for display_text in self.combobox_1_data:
            self.data_1_combobox.addItem(display_text)
        for index, (display_text, key) in enumerate(self.combobox_1_data.items()):
            self.data_1_combobox.setItemData(index, key)

    def set_combobox_2_items(self):
        self.data_2_combobox.clear()
        for display_text in self.combobox_2_data:
            self.data_2_combobox.addItem(display_text)
        for index, (display_text, key) in enumerate(self.combobox_2_data.items()):
            self.data_2_combobox.setItemData(index, key)

    def set_checkbox_values(self):
        self.checKbox_indicators = {}
        if self.typeDiagram in ['pie', 'hist', 'stackplot']:
            self.checKbox_indicators_data = ["type", "Attribut"]
        for option in self.checKbox_indicators_data:
            action = QAction(option, self, checkable=True)
            action.setChecked(True)
            action.triggered.connect(self.update_plot)
            self.display_indicators_menu.addAction(action)
            self.checKbox_indicators[option] = action
        self.addAction(self.display_indicators_menu.menuAction())
        self.addSeparator()


    def get_combobox1_selected_key(self):
        selected_text = self.data_1_combobox.currentText()
        for key, value in self.combobox_1_data.items():
            if key == selected_text:
                return value
        return None

    def get_combobox2_selected_key(self):
        selected_text = self.data_2_combobox.currentText()
        for key, value in self.combobox_2_data.items():
            if key == selected_text:
                return value
        return None

    def get_checkbox_indicators_selected(self):
        selected_indicators = [option for option, checkbox in self.checKbox_indicators.items() if checkbox.isChecked()]
        return selected_indicators

    def set_data(self, dict_keyfilter):
        self.dict_keyfilter = dict_keyfilter
        self.update_combobox()
        self.set_combobox_1_items()
        self.set_combobox_2_items()
        self.set_checkbox_values()

    def update_combobox(self):
        self.data_combobox.clear()
        self.data_combobox.addItems(list(self.dict_keyfilter))

    def update_plot(self):
        value_cmb_2 = self.get_combobox2_selected_key()
        value_cmb_1 = self.get_combobox1_selected_key()
        if value_cmb_1 is not None and value_cmb_2 is not None:
            data = self.getAllHistoryData()
            y_data = list(set(entry[value_cmb_1] for entry in data if entry[value_cmb_1] is not None))
            index = self.data_1_combobox.currentIndex()
            if self.typeDiagram == 'plot':
                self.plot_data_typeDiagram_plot(key=value_cmb_1, iist_y_data=y_data, index=index, option=value_cmb_2, isHidden=False)
            elif self.typeDiagram == 'pie':
                self.plot_data_typeDiagram_pie(key=value_cmb_1, iist_y_data=y_data, index=index, option=value_cmb_2,
                                                isHidden=False)
            elif self.typeDiagram == 'hist':
                self.plot_data_typeDiagram_hist(key=value_cmb_1, iist_y_data=y_data, index=index, option=value_cmb_2,
                                                isHidden=False)
            elif self.typeDiagram == 'stackplot':
                self.plot_data_typeDiagram_stackplot(key=value_cmb_1, iist_y_data=y_data, index=index, option=value_cmb_2,
                                                isHidden=False)


    def getAllHistoryData(self):
        historyData = []
        for aEntity in self.model.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
        return historyData

    def plot_data_typeDiagram_stackplot(self, key, iist_y_data, index, option, isHidden):
        self.ax.clear()
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        data = self.getAllHistoryData()
        rounds = set(entry['round'] for entry in data)

        if option == '1':
            rounds = [max(list(set(entry['round'] for entry in data)))]
            phases = set(entry['phase'] for entry in data if entry['round'] == rounds[0])
            self.xValue = [p for r in rounds for p in phases]
        else:
            phases = set(entry['phase'] for entry in data)
            self.xValue = [r * len(phases) + p for r in rounds for p in phases]

        list_data = []
        list_labels = []
        for pos, val in enumerate(iist_y_data):
            y = [sum(1 for entry in data if
                     entry['round'] == r and entry['phase'] == p and entry[key] == str(val).capitalize())
                 for r in rounds for p in phases]
            list_labels.append(str(val).capitalize())
            list_data.append(y)

            for ind in value_checkbox_3:
                if ind == 'type':
                    typeDef = str(val).capitalize()
                    if str(val).capitalize() != 'Cell':
                        typeDef = 'Agent'
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and entry['entityDef'] == str(
                                 val).capitalize())
                         for r in rounds for p in phases]
                    list_data.append(y)
                    list_labels.append(f"Type : {str(typeDef).upper()}")
                elif ind == 'Attribut':
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and 'health' in entry['attribut'])
                         for r in rounds for p in phases]
                    list_data.append(y)
                    list_labels.append(f"Health: {str(val).upper()}")

                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and 'landUse' in entry['attribut'] is not None)
                         for r in rounds for p in phases]
                    list_data.append(y)
                    list_labels.append(f"LandUse: {str(val).upper()}")

        self.ax.cla()
        self.ax.stackplot(range(len(list_data[0])), *list_data, labels=list_labels)
        self.ax.set_title('Stack Plot')

        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()


    def plot_data_typeDiagram_hist(self, key, iist_y_data, index, option, isHidden):
        self.ax.clear()
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        data = self.getAllHistoryData()
        rounds = set(entry['round'] for entry in data)

        if option == '1':
            rounds = [max(list(set(entry['round'] for entry in data)))]
            phases = set(entry['phase'] for entry in data if entry['round'] == rounds[0])
            self.xValue = [p for r in rounds for p in phases]
        else:
            phases = set(entry['phase'] for entry in data)
            self.xValue = [r * len(phases) + p for r in rounds for p in phases]

        list_data = []
        list_labels = []
        for pos, val in enumerate(iist_y_data):
            y = [sum(1 for entry in data if
                     entry['round'] == r and entry['phase'] == p and entry[key] == str(val).capitalize())
                 for r in rounds for p in phases]
            list_labels.append(str(val).capitalize())
            list_data.append(y)

            for ind in value_checkbox_3:
                if ind == 'type':
                    typeDef = str(val).capitalize()
                    if str(val).capitalize() != 'Cell':
                        typeDef = 'Agent'
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and entry['entityDef'] == str(
                                 val).capitalize())
                         for r in rounds for p in phases]
                    list_data.append(y)
                    list_labels.append(f"Type : {str(typeDef).upper()}")
                elif ind == 'Attribut':
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and 'health' in entry['attribut'])
                         for r in rounds for p in phases]
                    list_data.append(y)
                    list_labels.append(f"Health: {str(val).upper()}")

                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and 'landUse' in entry['attribut'] is not None)
                         for r in rounds for p in phases]
                    list_data.append(y)
                    list_labels.append(f"LandUse: {str(val).upper()}")

        self.ax.cla()
        for i in range(len(list_data)):
             print("data{} = {} , label = {} ".format(i, list_data[i], list_labels[i]))
             self.ax.hist(list_data[i], bins=len(list_data), alpha=0.5, label=list_labels[i])

        self.ax.set_title('Histogram')

        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_data_typeDiagram_pie(self, key, iist_y_data, index, option, isHidden):
        self.ax.clear()
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        data = self.getAllHistoryData()
        rounds = set(entry['round'] for entry in data)

        if option == '1':
            rounds = [max(list(set(entry['round'] for entry in data)))]
            phases = set(entry['phase'] for entry in data if entry['round'] == rounds[0])
        else:
            phases = set(entry['phase'] for entry in data)

        list_data = []
        list_labels = []
        for pos, val in enumerate(iist_y_data):
            y = [sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry[key] == str(val).capitalize())
                for r in rounds for p in phases]
            list_labels.append(str(val).capitalize())
            list_data.append(sum(y))

            for ind in value_checkbox_3:
                if ind == 'type':
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and entry['entityDef'] == str(val).capitalize())
                         for r in rounds for p in phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Type : {str(val).upper()}")
                elif ind == 'Attribut':
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and 'health' in entry['attribut'])
                             for r in rounds for p in phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Health: {str(val).upper()}")

                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and 'landUse' in entry['attribut'] is not None)
                         for r in rounds for p in phases]
                    list_data.append(sum(y))
                    list_labels.append(f"LandUse: {str(val).upper()}")

        self.ax.pie(list_data, labels=list_labels, autopct='%1.1f%%', startangle=90)
        self.ax.axis('equal')

        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()


    def plot_data_typeDiagram_plot(self, key, iist_y_data, index, option, isHidden):
        self.ax.clear()
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        data = self.getAllHistoryData()
        rounds = set(entry['round'] for entry in data)

        if option == '1':
            rounds = [max(list(set(entry['round'] for entry in data)))]
            phases = set(entry['phase'] for entry in data if entry['round'] == rounds[0])
            self.xValue = [p for r in rounds for p in phases]
        else:
            phases = set(entry['phase'] for entry in data)
            self.xValue = [r * len(phases) + p for r in rounds for p in phases]

        for pos, val in enumerate(iist_y_data):
            y = [sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry[key] == str(val).capitalize())
                for r in rounds for p in phases]
            self.ax.plot(self.xValue, y, label= str(val).upper(), linestyle=self.linestyles[pos % len(self.linestyles)],
                    color=self.colors[pos % len(self.colors)])
            for ind in value_checkbox_3:
                if ind == 'type':
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and entry['entityDef'] == str(val).capitalize())
                         for r in rounds for p in phases]
                    self.ax.plot(y, linestyle='--', color='orange', label=f"Type : {str(val).upper()}")
                elif ind == 'Attribut':
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and 'health' in entry['attribut'])
                             for r in rounds for p in phases]
                    self.ax.plot(y, linestyle='--', color='black', label=f"Attribut-health : {str(val).upper()}")
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and 'landUse' in entry['attribut'] is not None)
                         for r in rounds for p in phases]
                    self.ax.plot(y, linestyle='--', color='blue', label=f"Attribut-landUse: {str(val).upper()}")
                elif ind == 'St Dev':
                    self.ax.axhline(0, linestyle='dotted', color='pink', label=f"St Dev : {str(val).upper()}")
                elif ind == 'Max':
                    self.ax.axhline(0, linestyle='dashdot', color='green', label=f"Max : {str(val).upper()}")
                elif ind == 'Min':
                    self.ax.axhline(0, linestyle='--', color='blue', label=f"Min : {str(val).upper()}")

        for i in range(0, max(self.xValue) + 1, 7):
            round_lab = f"Round {int((i + 1) / 7)}"
            self.ax.axvline(x=i, color='r', linestyle=':')
            self.ax.text(i, 1, round_lab, color='r', ha='right', va='top', rotation=90,
                         transform=self.ax.get_xaxis_transform())

        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()