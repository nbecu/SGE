import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget, QAction, QMenu, QPushButton, \
    QCheckBox
from PyQt5.QtCore import pyqtSignal


class SGToolBar(NavigationToolbar):
    def __init__(self, canvas, parent, model, typeDiagram):
        super().__init__(canvas, parent)
        self.typeDiagram = typeDiagram
        button = QPushButton("Actualiser", self)
        button.setIcon(QIcon("./icon/actualiser.png"))
        button.clicked.connect(self.update_plot)
        self.addWidget(button)

        self.option_affichage_data = {"entityName": "Entités", "simVariable": "Simulation variables", "currentPlayer": "Players"}

        self.data_2_combobox = QComboBox(parent)
        self.data_2_combobox.currentIndexChanged.connect(self.update_plot)
        self.addWidget(self.data_2_combobox)
        self.ax = parent.ax
        self.model = model
        self.title = 'SG Diagramme'
        self.combobox_2_data = {'Tous les tours': '0', 'Dernieres Tours': '1', 'Autres': '2'}

        self.display_indicators_menu = QMenu("Indicators", self)
        self.checKbox_indicators_data = ["type", "Attribut", "Max", "Mean", "Min", "St Dev"]
        self.checKbox_indicators = {}
        self.rounds = []
        self.phases = []
        #self.linestyles = ['-', '--', '-.', ':', 'dotted', 'dashdot']
        self.linestyles = ['-', '--', '-.', ':', 'dashed', 'dashdot', 'dotted']
        self.colors = ['gray', 'green', 'blue', 'red', 'black', 'orange', 'purple', 'pink', 'cyan', 'magenta']
        self.xValue = []
        self.display_menu = QMenu("Affichage", self)
        self.dictMenuData = {'entities': {}, 'simvariables': {}, 'players': {}}
        self.checkbox_display_menu_data = {}
        #self.checkbox_main_menu_data = {}
        #self._navigation_toolbar = self.parent().addToolBar('Navigation')

        #self.createDisplayMenu()
        self.data = self.getAllData()
        self.regenerate_menu(self.data)

    def regenerate_menu(self, data):
        entitiesMenu = QMenu('Entités', self)
        playersMenu = QMenu('Players', self)
        simulationMenu = QMenu('Simulation variables', self)
        if self.typeDiagram == 'plot':
            entities_list = {entry['entityName'] for entry in data if
                             'entityName' in entry and not isinstance(entry['entityName'], dict)}

            attrib_data = ['max', 'mean', 'min', 'stdev']
            players_list = {player['currentPlayer'] for player in data if
                            'currentPlayer' in player and not isinstance(player['currentPlayer'], dict)}
            simVariables_list = {attribut for entry in data for attribut in entry.get('simVariable', {})}
            for player in players_list:
                self.dictMenuData['players'][f"currentPlayer-:{player}"] = player

            for key in simVariables_list:
                list_data = {entry['simVariable'][key] for entry in data if isinstance(entry.get('simVariable', {}), dict)}
                self.dictMenuData['simvariables'][f"simVariable-:{key}"] = list_data
            for entity_name in sorted(entities_list):
                attrib_dict = {}
                attrib_dict[f"entity-:{entity_name}-:populations"] = None
                for attribut_key in {attribut for entry in data for attribut in entry.get('attribut', {}) if
                                     entry.get('entityName') == entity_name and isinstance(entry['attribut'][attribut], (int, float))}:
                    attrib_dict[attribut_key] = {f"entity-:{entity_name}-:{attribut_key}-:{option_key}": None for option_key in attrib_data}
                self.dictMenuData['entities'][entity_name] = attrib_dict
            self.display_menu.addMenu(entitiesMenu)
            self.display_menu.addMenu(playersMenu)
            self.display_menu.addMenu(simulationMenu)
            self.addSubMenus(entitiesMenu, self.dictMenuData['entities'])
            self.addSubMenus(simulationMenu, self.dictMenuData['simvariables'])
            self.addSubMenus(playersMenu, self.dictMenuData['players'])
        else:
            attrib_data = []
            entities_list = {entry['entityName'] for entry in data if 'entityName' in entry and isinstance(entry['attribut'], dict)
                             and entry['attribut'].keys() and not isinstance(entry['entityName'], dict)}

            for entity_name in sorted(entities_list):
                attrib_dict = {}
                #attrib_dict[f"entity-:{entity_name}-:populations"] = None
                for attribut_key in {attribut for entry in data for attribut in entry.get('attribut', {}) if
                                     entry.get('entityName') == entity_name and isinstance(entry['attribut'][attribut], str)}:
                    list_val = []
                    attrib_tmp_dict = {}
                    for sub_attribut_val in {entry['attribut'][attribut] for entry in data for attribut in entry.get('attribut', {}) if
                                         entry.get('entityName') == entity_name and isinstance(
                                             entry['attribut'][attribut], str)}:
                        list_val.append(sub_attribut_val)
                        attrib_tmp_dict[sub_attribut_val] = {f"entity-:{entity_name}-:{attribut_key}-:{sub_attribut_val}"}
                    attrib_dict[attribut_key] = attrib_tmp_dict
                self.dictMenuData['entities'][entity_name] = attrib_dict
            self.display_menu.addMenu(entitiesMenu)
            self.addSubMenus(entitiesMenu, self.dictMenuData['entities'])
        self.addAction(self.display_menu.menuAction())



    def addSubMenus(self, parentMenu, subMenuData):
        for key, value in subMenuData.items():
            if isinstance(value, dict):
                submenu = QMenu(key, self)
                parentMenu.addMenu(submenu)

                self.addSubMenus(submenu, value)

            else:
                action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize(), self, checkable=True)
                action.setChecked(True)
                action.setProperty("key", key)
                action.triggered.connect(self.update_plot)
                if key not in self.checkbox_display_menu_data:
                    self.checkbox_display_menu_data[key] = action
                """if parentMainMenu_title:
                    self.checkbox_display_menu_data[parentMainMenu_title][key] = action
                else:
                    self.checkbox_display_menu_data[key] = action"""
                parentMenu.addAction(action)


    def get_checkbox_display_menu_selected(self):
        #print("\n self.checkbox_display_menu_data.items() : ", self.checkbox_display_menu_data.keys())
        selected_option = [option for option, checkbox in self.checkbox_display_menu_data.items() if checkbox.isChecked()]
        return selected_option


    ########
    """def update_plot(self):
        self.update_plot_test()
        self.update_data()
        value_cmb_2 = self.get_combobox2_selected_key()
        value_cmb_1 = self.get_combobox1_selected_key()
        if value_cmb_1 is not None and value_cmb_2 is not None:
            index = self.data_1_combobox.currentIndex()
            if self.typeDiagram == 'plot':
                self.plot_data_typeDiagram_plot(key=value_cmb_1, index=index, option=value_cmb_2, isHidden=False)
            elif self.typeDiagram == 'pie':
                self.plot_data_typeDiagram_pie(key=value_cmb_1, index=index, option=value_cmb_2, isHidden=False)
            elif self.typeDiagram == 'hist':
                self.plot_data_typeDiagram_hist(key=value_cmb_1, index=index, option=value_cmb_2, isHidden=False)
            elif self.typeDiagram == 'stackplot':
                self.plot_data_typeDiagram_stackplot(key=value_cmb_1, index=index, option=value_cmb_2,
                                                isHidden=False)"""

    ########
    def update_plot(self):
        self.update_data()
        selected_option_list = self.get_checkbox_display_menu_selected()
        print("selected_option_list : ", selected_option_list)
        if self.typeDiagram == 'plot':
            self.plot_linear_typeDiagram(self.data, selected_option_list)
        elif self.typeDiagram == 'pie':
            self.plot_pie_typeDiagram(self.data, selected_option_list)
        elif self.typeDiagram == 'hist':
            self.plot_hist_typeDiagram(self.data, selected_option_list)
        elif self.typeDiagram == 'stackplot':
            self.plot_stackplot_typeDiagram(self.data, selected_option_list)

    def plot_stackplot_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        list_data = []
        list_labels = []
        for options in selected_option_list:
            if "-:" in options:
                list_option = options.split("-:")
                if list_option[0] == 'entity' and list_option[-1] == 'populations':
                    y = [sum(1 for entry in data if len(list_option) > 2 and entry['round'] == r \
                             and entry['phase'] == p and entry['entityName'] == list_option[1] and \
                             'attribut' in entry and list_option[2] in entry['attribut'].keys())
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(' - '.join(list_option[1:]).upper() )
                """elif list_option[0] == 'simVariable':
                    y = [sum(1 for entry in data if entry['round'] == r \
                             and entry['phase'] == p and 'simVariable' in entry and
                             entry['simVariable'] == list_option[-1])
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Simulation Variable : {str(list_option[-1]).upper()}")
                elif list_option[0] == 'currentPlayer':
                    y = [sum(1 for entry in data if entry['round'] == r \
                             and entry['phase'] == p and 'currentPlayer' in entry and
                             entry['currentPlayer'] == list_option[-1])
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Player : {str(list_option[-1]).upper()}")"""
        #self.ax.pie(list_data, labels=list_labels, autopct='%1.1f%%', startangle=90)

        self.ax.cla()
        self.ax.stackplot(range(len(list_data)), *list_data, labels=list_labels)
        #self.ax.stackplot(self.xValue, range(len(list_data)), *list_data, labels=list_labels)
        self.ax.set_title('Stack Plot')
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_hist_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        list_data = []
        list_labels = []
        for options in selected_option_list:
            if "-:" in options:
                list_option = options.split("-:")
                if list_option[0] == 'entity' and list_option[-1] == 'populations':
                    y = [sum(1 for entry in data if len(list_option) > 2 and entry['round'] == r \
                             and entry['phase'] == p and entry['entityName'] == list_option[1] and \
                             'attribut' in entry and list_option[2] in entry['attribut'].keys())
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(' - '.join(list_option[1:]).upper() )
                """elif list_option[0] == 'simVariable':
                    y = [sum(1 for entry in data if entry['round'] == r \
                             and entry['phase'] == p and 'simVariable' in entry and
                             entry['simVariable'] == list_option[-1])
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Simulation Variable : {str(list_option[-1]).upper()}")
                elif list_option[0] == 'currentPlayer':
                    y = [sum(1 for entry in data if entry['round'] == r \
                             and entry['phase'] == p and 'currentPlayer' in entry and
                             entry['currentPlayer'] == list_option[-1])
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Player : {str(list_option[-1]).upper()}")"""
        #self.ax.pie(list_data, labels=list_labels, autopct='%1.1f%%', startangle=90)

        self.ax.cla()
        for i in range(len(list_data)):
             self.ax.hist(list_data[i], bins=len(list_data), alpha=0.5, label=list_labels[i])
             print("i : {} , list_data[i] : {} ".format(i, list_data[i]))
             print("list_labels[i] : ", list_labels[i])

        #self.ax.axis('equal')

        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_pie_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        i=0
        list_data = []
        list_labels = []
        for options in selected_option_list:
            if "-:" in options:
                list_option = options.split("-:")

                """
                 for attribut_key in {attribut for entry in data for attribut in entry.get('attribut', {}) if
                                     entry.get('entityName') == entity_name and isinstance(entry['attribut'][attribut], (int, float))}:
                    attrib_dict[attribut_key] = {f"entity-:{entity_name}-:{attribut_key}-:{option_key}": None for option_key in attrib_data}
                """

                if list_option[0] == 'entity' and list_option[-1] == 'populations':
                    """y = [sum(1 for entry in data if len(list_option) > 2 and entry['round'] == r \
                             and entry['phase'] == p and entry['entityName'] == list_option[1] and \
                             'attribut' in entry and list_option[2] in entry['attribut'].keys())
                         for r in self.rounds for p in self.phases]"""

                    """for r in self.rounds:
                        for p in self.phases:
                            for entry in data:
                                #print("entry :: ", entry['attribut'])
                                i += 1
                                if i==4:
                                    break
                                if len(list_option) > 2 and entry['round'] == r \
                                                 and entry['phase'] == p and entry['entityName'] == list_option[1] and \
                                                 'attribut' in entry and list_option[2] in entry['attribut'].keys() :
                                    print("entry attr :: ", entry['attribut'][list_option[2]])"""




                    """y = [sum(1 for entry in data if len(list_option) > 2 and entry['round'] == r \
                             and entry['phase'] == p and entry['entityName'] == list_option[1] and \
                             'attribut' in entry and list_option[2] in entry['attribut'].keys())
                         for r in self.rounds for p in self.phases]"""

                    #list_data.append(sum(y))
                    list_labels.append(' - '.join(list_option[1:]).upper() )
                """elif list_option[0] == 'simVariable':
                    y = [sum(1 for entry in data if entry['round'] == r \
                             and entry['phase'] == p and 'simVariable' in entry and
                             entry['simVariable'] == list_option[-1])
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Simulation Variable : {str(list_option[-1]).upper()}")
                elif list_option[0] == 'currentPlayer':
                    y = [sum(1 for entry in data if entry['round'] == r \
                             and entry['phase'] == p and 'currentPlayer' in entry and
                             entry['currentPlayer'] == list_option[-1])
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Player : {str(list_option[-1]).upper()}")"""
        #print("list_data :: ", list_data)
        """self.ax.pie(list_data, labels=list_labels, autopct='%1.1f%%', startangle=90)
        self.ax.axis('equal')
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()"""

    def plot_linear_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        pos = 0
        for options in selected_option_list:
            if "-:" in options:
                list_option = options.split("-:")
                variable = list_option[0]
                if variable == 'entity':
                    #print("list_option : ", list_option)
                    self.plot_linear_typeDiagram_for_entities(data, list_option, pos)
                elif variable == 'simVariable':
                    self.plot_linear_typeDiagram_for_simVariable(data, list_option, pos)
                elif variable == 'currentPlayer':
                    self.plot_linear_typeDiagram_for_players(data, list_option, pos)
            pos += 1

    def plot_linear_typeDiagram_for_entities(self, data, list_option, pos):
        # entities[0] = entity; entities[1] = entityName ; entities[2] = attribut
        #print("list_option :: ", list_option)
        if list_option[:1] == ['entity']:
            entities = list_option
            label = f"{entities[-1].upper()} ({entities[1].upper()} - {entities[2].upper()})"
            y = [sum(1 for entry in data if len(entities) > 2 and entry['round'] == r \
                     and entry['phase'] == p and entry['entityName'] == entities[1] and \
                     'attribut' in entry and entities[2] in entry['attribut'].keys())
                 for r in self.rounds for p in self.phases]
            linestyle = self.linestyles[pos % len(self.linestyles)]
            color = self.colors[pos % len(self.colors)]
            if list_option[-1] == 'populations':
                self.ax.plot(self.xValue, y, label=label, linestyle='solid', color=color)
            else:
                statistics = {'max': np.max(y), 'mean': np.mean(y), 'min': np.min(y), 'stdev': np.std(y)}
                linestyle_map = {'max': 'dotted', 'mean': ':', 'min': 'dashdot', 'stdev': '--'}
                color_map = {'max': 'green', 'mean': 'blue', 'min': 'black', 'stdev': 'red'}
                line_style = linestyle_map.get(str(list_option[-1]).lower(), ':')
                line_color = color_map.get(str(list_option[-1]).lower(), 'blue')
                self.ax.axhline(statistics.get(str(list_option[-1]).lower(), np.mean(y)), linestyle=line_style,
                                color=line_color, label=label)
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()


    def plot_linear_typeDiagram_for_simVariable(self, data, list_option, pos):
        if list_option[:1] == ['simVariable']:
            entities = list_option
            label = f"Simulation Variable : {entities[-1].upper()}"
            y = [sum(1 for entry in data if entry['round'] == r \
                     and entry['phase'] == p and 'simVariable' in entry and
                     entry['simVariable'] == list_option[-1])
                 for r in self.rounds for p in self.phases]
            linestyle = self.linestyles[pos % len(self.linestyles)]
            color = self.colors[pos % len(self.colors)]
            self.ax.plot(self.xValue, y, label=label, linestyle='solid', color=color)
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_linear_typeDiagram_for_players(self, data, list_option, pos):
        if list_option[:1] == ['currentPlayer']:
            entities = list_option
            label = f"Player : {entities[-1].upper()}"
            y = [sum(1 for entry in data if entry['round'] == r \
                     and entry['phase'] == p and 'currentPlayer' in entry and
                     entry['currentPlayer'] == list_option[-1])
                 for r in self.rounds for p in self.phases]
            linestyle = self.linestyles[pos % len(self.linestyles)]
            color = self.colors[pos % len(self.colors)]
            self.ax.plot(self.xValue, y, label=label, linestyle='solid', color=color)
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()


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

    def get_combobox2_selected_key(self):
        selected_text = self.data_2_combobox.currentText()
        for key, value in self.combobox_2_data.items():
            if key == selected_text:
                return value
        return None

    def get_checkbox_indicators_selected(self):
        selected_indicators = [option for option, checkbox in self.checKbox_indicators.items() if checkbox.isChecked()]
        return selected_indicators

    def set_data(self):
        self.update_data()
        self.set_combobox_2_items()
        #self.set_checkbox_values()


    def getAllHistoryData(self):
        historyData = []
        for aEntity in self.model.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
        return historyData

    def getAllData(self):
        value_cmb_2 = self.get_combobox2_selected_key()
        return self.getAllHistoryData() if value_cmb_2 == 1 else self.model.listData

    def update_data(self):
        self.data = self.getAllData()
        self.setXValueData(self.data)

    def setXValueData(self, data):
        option = self.get_combobox2_selected_key()
        rounds = {entry['round'] for entry in data}
        phases = {entry['phase'] for entry in data}
        if option == '1':
            max_round = max(rounds)
            self.rounds = [max_round]
            self.phases = {entry['phase'] for entry in data if  entry['phase'] == max_round}
            self.xValue = self.rounds if len(self.phases) <= 2 else [phase for phase in self.phases]
        else:
            self.rounds = rounds
            self.phases = phases
            self.xValue = list(rounds) if len(phases) <= 2 else [r * len(phases) + phase for r in rounds for
                                                                 phase in phases]
