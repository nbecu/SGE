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

        self.indicators = ['max','mean', 'min', 'stdev']

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
        # self.data = self.getAllData()
        self.firstEntity=""
        self.firstAttribut=""
        self.list_attribut_display = []
        self.dataEntities = self.model.dataRecorder.getStats_ofEntities() #ATTENTION --> lire les commentaires en dessous
                #ATTENTION : getStats_ofEntities() recupère les données des entitées avec toutes les Stats déjà calculé
                #ATTENTION : Il n'y a pas besoin de  recalculer les Stats !!!
                #ATTENTION : Les Stats déjà calculé sont population, mean, min, max, std, (voir suite des stats calculés ci-dessous)
                #ATTENTION(suite des Stats déjà calculés) : sum (nouvelle stat pour les DiagramLinear), histogram (pour l'affichage des DiagramHistogram)
                #ATTENTION(suite des Stats déjà calculés) : + les 'counter' des attributs de type str (qualiAttributes), (pour l'affichage des DiagramCircular et DiagramStackPlot)
                #ATTENTION(explication des 'counter'): un 'counter' donne le nombre d'occurences de chaque catégorie, pour l'affichage des DiagramCircular et DiagramStackPlot
                
        self.dataSimVariables = self.model.dataRecorder.getStepsData_ofSimVariables()
        self.dataPlayers = self.model.dataRecorder.getStepsData_ofPlayers()
        self.regenerate_menu(self.dataEntities)

    def regenerate_menu(self, data):
        entitiesMenu = QMenu('Entités', self)
        playersMenu = QMenu('Players', self)
        simulationMenu = QMenu('Simulation variables', self)
        if self.typeDiagram == 'plot':
            entities_list = {entry['entityName'] for entry in data if
                             'entityName' in entry and not isinstance(entry['entityName'], dict)}
            if not self.firstEntity:
                self.firstEntity = sorted(entities_list)[0]
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
                attrib_dict[f"entity-:{entity_name}-:population"] = None
                list_attribut_key = {attribut for entry in data for attribut in entry.get('quantiAttributes', {})}
                        #  if entry.get('entityName') == entity_name and isinstance(entry['quantiAttributes'][attribut], (int, float))}
                        # ---> Pas besoin, car j'ai séparé les attributes dans deux keys -> quantiAttributes  pour les (int, float) et qualiAttributes  pour les str
                if not self.firstAttribut:
                    self.firstAttribut = "" #sorted(list_attribut_key)[0]
                for attribut_key in sorted(list_attribut_key):
                    attrib_dict[attribut_key] = {f"entity-:{entity_name}-:{attribut_key}-:{option_key}": None for option_key in attrib_data}
                self.dictMenuData['entities'][entity_name] = attrib_dict
            self.display_menu.addMenu(entitiesMenu)
            self.display_menu.addMenu(playersMenu)
            self.display_menu.addMenu(simulationMenu)
            self.addSubMenus(entitiesMenu, self.dictMenuData['entities'], self.firstEntity, self.firstAttribut)
            #self.addSubMenus(simulationMenu, self.dictMenuData['simvariables'])
            #self.addSubMenus(playersMenu, self.dictMenuData['players'])
        else:
            attrib_data = []
            entities_list = {entry['entityName'] for entry in data if 'entityName' in entry and isinstance(entry['quantiAttributes'], dict)
                             and entry['quantiAttributes'].keys() and not isinstance(entry['entityName'], dict)}
            if not self.firstEntity:
                self.firstEntity = sorted(entities_list)[0]

            for entity_name in sorted(entities_list):
                attrib_dict = {}
                #attrib_dict[f"entity-:{entity_name}-:population"] = None
                parentAttributKey = 'quantiAttributes' if self.typeDiagram in ['plot', 'hist'] else 'qualiAttributes'
                list_attribut_key = {attribut for entry in data for attribut in entry.get(parentAttributKey, {}) if
                                     entry.get('entityName') == entity_name and isinstance(entry[parentAttributKey][attribut], dict)}

                if not self.firstAttribut:
                    self.firstAttribut = sorted(list_attribut_key)[0] if len(list_attribut_key)>0 else ""
                for attribut_key in list_attribut_key:
                    list_val = []
                    attrib_tmp_dict = {}
                    if self.typeDiagram in ['hist', 'pie', 'stackplot']:
                        attrib_dict[f"entity-:{entity_name}-:{attribut_key}"] = None
                    else:
                        for sub_attribut_val in {entry['quantiAttributes'][attribut] for entry in data for attribut in entry.get('quantiAttributes', {}) if
                                             entry.get('entityName') == entity_name and isinstance(
                                                 entry['quantiAttributes'][attribut], str)}:
                            list_val.append(sub_attribut_val)

                            attrib_tmp_dict[f"entity-:{entity_name}-:{attribut_key}-:{sub_attribut_val}"] = None

                        #attrib_tmp_dict[sub_attribut_val] = {f"entity-:{entity_name}-:{attribut_key}-:{sub_attribut_val}" : None}
                        attrib_dict[attribut_key] = attrib_tmp_dict
                    #print("attrib_dict :: ", attrib_dict)

                self.dictMenuData['entities'][entity_name] = attrib_dict

            #        firstEntity=""
            #   firstAttribut=""
            self.display_menu.addMenu(entitiesMenu)
            self.addSubMenus(entitiesMenu, self.dictMenuData['entities'], self.firstEntity, self.firstAttribut)
        self.addAction(self.display_menu.menuAction())



    def addSubMenus(self, parentMenu, subMenuData, firstEntity, firstAttribut):
        for key, value in subMenuData.items():
            if isinstance(value, dict):
                submenu = QMenu(key, self)
                parentMenu.addMenu(submenu)
                self.addSubMenus(submenu, value, firstEntity, firstAttribut)
            else:
                action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize(), self, checkable=True)
                if firstEntity in key.split("-:") or firstAttribut in key.split("-:"):
                    action.setChecked(True)
                action.setProperty("key", key)
                action.triggered.connect(self.update_plot)
                if key not in self.checkbox_display_menu_data:
                    self.checkbox_display_menu_data[key] = action
                parentMenu.addAction(action)


    def get_checkbox_display_menu_selected(self):
        print("\n self.checkbox_display_menu_data.items() : ", self.checkbox_display_menu_data.keys())
        selected_option = [option for option, checkbox in self.checkbox_display_menu_data.items() if checkbox.isChecked()]
        return selected_option


    def update_plot(self):
        self.update_data()
        selected_option_list = self.get_checkbox_display_menu_selected()
        #print("dataEntities : ", self.dataEntities)
        if self.typeDiagram == 'plot':
            self.plot_linear_typeDiagram(self.dataEntities, selected_option_list)
        elif self.typeDiagram == 'pie':
            self.plot_pie_typeDiagram(self.dataEntities, selected_option_list)
        elif self.typeDiagram == 'hist':
            self.plot_hist_typeDiagram(self.dataEntities, selected_option_list)
        elif self.typeDiagram == 'stackplot':
            self.plot_stackplot_typeDiagram(self.dataEntities, selected_option_list)

    def plot_stackplot_typeDiagram(self, data, selected_option_list):
        print("selected_option_list : ", selected_option_list)
        list_data = []
        formatted_data = {}
        self.ax.clear()
        for option in selected_option_list:
            if "-:" in option:
                list_opt = option.split("-:")
                entityName = list_opt[1]
                attribut_value = list_opt[-1]
                for r in self.rounds:
                    data_stackplot = next((entry['qualiAttributes'][attribut_value] for entry in data
                                           if entry['round'] == r and
                                           entry['entityName'] == entityName and attribut_value in entry[
                                               'qualiAttributes']), None)
                    list_data.append(data_stackplot)

        #ordonner par attribut
        list_data_sorted = sorted(list_data, key=lambda x: sorted(x.keys()))
        for i, counts in enumerate(list_data_sorted):
            for key, value in counts.items():
                if key not in formatted_data:
                    formatted_data[key] = []
                formatted_data[key].append(value)

        lengths = {key: len(value) for key, value in formatted_data.items()}
        max_length = max(lengths.values())
        for key, length in lengths.items():
            if length < max_length:
                difference = max_length - length
                formatted_data[key] = [0] * difference + formatted_data[key]
        self.ax.stackplot(self.xValue, list(formatted_data.values()), labels=list(formatted_data.keys()))
        self.ax.legend()
        self.ax.set_xlabel("Rounds")
        self.ax.set_ylabel("Valeurs")
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_hist_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        list_data = []
        for option in selected_option_list:
            if "-:" in option:
                list_opt = option.split("-:")
                entity_name = list_opt[1]
                attribut_value = list_opt[-1]
                histo_y = {f"{entity_name}-{attribut_value}" : entry['quantiAttributes'][attribut_value]['histo']
                      for entry in data if entry['entityName']==entity_name  and 'quantiAttributes' in entry \
                           and attribut_value in entry['quantiAttributes'] and 'histo' in \
                            entry['quantiAttributes'][attribut_value] and entry['round'] == max(self.rounds)}
                list_data.append(histo_y)

        for h in list_data:
            h_abcis = list(h.values())[0][1][:-1]
            h_height = list(h.values())[0][0]
            label = str(list(h.keys())[0]) if h.keys() and len(list(h.keys()))>0 else ''
            self.ax.bar(h_abcis, h_height, width=5, label=label)

        self.ax.legend()
        self.ax.set_title(self.title)
        self.ax.set_xlabel('Valeurs')
        self.ax.set_ylabel('Fréauences')

    def plot_pie_typeDiagram(self, data, selected_option_list):
        if len(selected_option_list)>0 and "-:" in selected_option_list[0]:
            list_option = selected_option_list[0].split("-:")
            entityName = list_option[1]
            attribut_value = list_option[2]
            self.ax.clear()
            data_pie = next((entry['qualiAttributes'][attribut_value] for entry in data
                             if entry['round'] == max(self.rounds) and
                             entry['entityName'] == entityName and attribut_value in entry['qualiAttributes']), None)

            labels = list(data_pie.keys())
            values = list(data_pie.values())
            self.ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax.axis('equal')
            self.ax.legend()
            self.ax.set_title(self.title)
            self.canvas.draw()


    def plot_linear_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        pos = 0
        if len(selected_option_list)>0 and "-:" in selected_option_list[0]:
            self.plot_linear_typeDiagram_for_entities(data, selected_option_list, pos)
            """elif variable == 'simVariable':
                self.plot_linear_typeDiagram_for_simVariable(data, list_option, pos)
            elif variable == 'currentPlayer':
                self.plot_linear_typeDiagram_for_players(data, list_option, pos)"""
        #pos += 1

    def plot_linear_typeDiagram_for_entities(self, data, selected_option_list, pos):
        self.ax.clear()
        if len(selected_option_list) > 0 and "-:" in selected_option_list[0]:
            for option in selected_option_list:
                list_option = option.split("-:")
                if len(list_option)>0:
                    entityName = list_option[1]
                    label_pop = f"Populations : {entityName}"
                    data_populations = []; data_min=[]; data_max=[]; data_mean=[]; data_stdev=[] ; data_sum=[]
                    for r in self.rounds:
                        if list_option[-1] == 'population':
                            y = [sum(entry['population'] for entry in data if entry['round'] == r
                                     and entry['entityName'] == entityName)]
                            data_populations.append(y)
                        else:
                            if list_option[-1] in self.indicators:
                                attribut_key = list_option[2]
                                if list_option[-1] == 'min':
                                    min_y = [sum(entry['quantiAttributes'][attribut_key]['min'] for entry in data if entry['round'] == r
                                             and entry['entityName'] == entityName)]
                                    data_min.append(min_y)
                                elif list_option[-1] == 'mean':
                                    mean_y = [sum(entry['quantiAttributes'][attribut_key]['mean'] for entry in data if entry['round'] == r
                                             and entry['entityName'] == entityName)]
                                    data_mean.append(mean_y)
                                elif list_option[-1] == 'max':
                                    max_y = [sum(entry['quantiAttributes'][attribut_key]['max'] for entry in data if entry['round'] == r
                                             and entry['entityName'] == entityName)]
                                    data_max.append(max_y)
                                elif list_option[-1] == 'stdev':
                                    stdev_y = [sum(entry['quantiAttributes'][attribut_key]['stdev'] for entry in data if entry['round'] == r
                                                 and entry['entityName'] == entityName)]
                                    data_stdev.append(stdev_y)
                    if len(data_populations)>0:
                        self.ax.plot(self.xValue, data_populations, label=label_pop, linestyle='solid', color='green')

                    if list_option[-1] in self.indicators:
                        if len(data_mean)>0:
                            self.ax.plot(self.xValue, data_mean, label=f"Moyenne - {attribut_key} - {entityName}", linestyle='dashdot', color='red')
                        if len(data_min) > 0:
                            self.ax.plot(self.xValue, data_min, label=f"Min - {attribut_key} - {entityName}", linestyle='dotted', color='blue')
                        if len(data_max) > 0:
                            self.ax.plot(self.xValue, data_max, label=f"Max - {attribut_key} - {entityName}", linestyle=':', color='black')
                        if len(data_stdev) > 0:
                            self.ax.plot(self.xValue, data_stdev, label=f"St Dev - {attribut_key} - {entityName}", linestyle='--', color='orange')
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
    
    #  format de entity.getHistoryDataJSON()) de entity 
    #  {
    #         'id': self.id,
    #         'currentPlayer': self.model.currentPlayer,
    #         'entityDef': self.classDef.entityName if self.classDef.entityName == 'Cell' else 'Agent',
    #         'entityName': self.classDef.entityName,
    #         'simVariable': simvariable_dict,
    #         'round': self.model.timeManager.currentRound,
    #         'phase': self.model.timeManager.currentPhase,
    #         'quantiAttributes': self.dictAttributes
    #     }

    # def getAllData(self):
    #     value_cmb_2 = self.get_combobox2_selected_key()
    #     return self.getAllHistoryData() if value_cmb_2 == 1 else self.model.listData



    def update_data(self):
        # self.data = self.getAllData()
        # self.data = self.model.dataRecorder.listOfData_ofEntities
        # self.data = self.model.dataRecorder.getStepsData_ofEntities()
        self.dataEntities = self.model.dataRecorder.getStats_ofEntities()
        self.dataSimVars = self.model.dataRecorder.getStepsData_ofSimVariables()
        self.dataPlayers = self.model.dataRecorder.getStepsData_ofPlayers()
        #self.regenerate_menu(self.dataEntities)

        self.setXValueData(self.dataEntities)

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
