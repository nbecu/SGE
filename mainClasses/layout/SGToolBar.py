import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget, QAction, QMenu, QPushButton, \
    QCheckBox, QSpinBox, QLabel, QSlider, QLineEdit
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
import re


class SGToolBar(NavigationToolbar):
    def __init__(self, canvas, parent, model, typeDiagram):
        super().__init__(canvas, parent)

        self.typeDiagram = typeDiagram
        button = QPushButton("Actualiser", self)
        button.setIcon(QIcon("./icon/actualiser.png"))
        button.clicked.connect(self.refresh_data)
        #layout_per_round = QVBoxLayout()
        self.addWidget(button)
    

        if self.typeDiagram in ['plot']:
            self.addSeparator()
            self.start_label = QLabel('Tour Min:')
            self.start_cmb_round = QComboBox(parent)
            self.start_cmb_round.activated.connect(self.onCmbRoundActivated)
            self.addWidget(self.start_label)
            self.addWidget(self.start_cmb_round)
            self.end_label = QLabel('Tour Max:')
            self.end_cmb_round = QComboBox(parent)
            self.end_cmb_round.activated.connect(self.onCmbRoundActivated)
            self.addWidget(self.end_label)
            self.addWidget(self.end_cmb_round)
            self.combobox_per_rounds_data = {}
            self.add_button = QPushButton('Afficher')
            self.add_button.clicked.connect(self.update_plot)
            self.addWidget(self.add_button)
            self.addSeparator()
        self.start_cmb_round.setEnabled(False)
        self.end_cmb_round.setEnabled(False)
        self.add_button.setEnabled(False)


        self.roundMin = 0
        self.roundMax = 0
        self.is_refresh = False
        self.indicators = ['max','mean', 'min', 'stdev']
        self.indicators_item = {'max': 'Max', 'mean': 'Moyenne', 'min': 'Min', 'stdev': 'St Dev'}
        self.option_affichage_data = {"entityName": "Entités", "simVariable": "Simulation variables", "currentPlayer": "Players"}
        self.ax = parent.ax
        self.model = model
        self.title = 'SG Diagramme'
        self.combobox_2_data = {'Tous les tours': '0', 'Dernieres Tours': '1', 'Autres': '2'}
        if self.typeDiagram in ['pie', 'hist']:
            self.combobox_2_data = {'Dernieres Tours': '1'}

        self.data_2_combobox = QComboBox(parent)
        self.data_2_combobox.currentIndexChanged.connect(self.update_plot)
        self.addWidget(self.data_2_combobox)

        self.display_indicators_menu = QMenu("Indicators", self)
        self.checKbox_indicators_data = ["type", "Attribut", "Max", "Mean", "Min", "St Dev"]
        self.checKbox_indicators = {}

        self.rounds = []
        self.phases = []

        #self.linestyles = ['-', '--', '-.', ':', 'dashed', 'dashdot', 'dotted']
        self.linestyle_items = {'stdev':'--', 'max': 'dashed', 'min':'dashdot', 'mean':'dotted'}

        self.colors = ['gray', 'green', 'blue', 'red', 'black', 'orange', 'purple', 'pink', 'cyan', 'magenta']
        self.xValue = []
        self.display_menu = QMenu("Affichage", self)
        self.dictMenuData = {'entities': {}, 'simvariables': {}, 'players': {}}
        self.checkbox_display_menu_data = {}
        self.previous_selected_checkboxes = []

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

            ###
            players_list = {player['currentPlayer'] for player in data if
                            'currentPlayer' in player and not isinstance(player['currentPlayer'], dict)}
            for player in players_list:
                self.dictMenuData['players'][f"currentPlayer-:{player}"] = player
            """for key in simVariables_list:
                list_data = {entry['simVariable'][key] for entry in data if isinstance(entry.get('simVariable', {}), dict)}
                self.dictMenuData['simvariables'][f"simVariable-:{key}"] = list_data"""
            ###

            for entity_name in sorted(entities_list):
                attrib_dict = {}
                attrib_dict[f"entity-:{entity_name}-:population"] = None
                list_attribut_key = {attribut for entry in data for attribut in entry.get('quantiAttributes', {}) if entry['entityName']==entity_name}
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

            simVariables_list = list(set(entry['simVarName'] for entry in self.dataSimVariables))
            for simVar in simVariables_list:
                self.dictMenuData['simvariables'][f"simvariables-:{simVar}"] = None
            self.addSubMenus(simulationMenu, self.dictMenuData['simvariables'], self.firstEntity, self.firstAttribut)

            #simVariables_list = {entry['simVarName'] for entry in self.dataSimVars}


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
                        attrib_dict[attribut_key] = attrib_tmp_dict
                self.dictMenuData['entities'][entity_name] = attrib_dict
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
                action = self.set_checkbox_action(key, parentMenu, firstEntity, firstAttribut)
                self.checkbox_display_menu_data[key] = action
                parentMenu.addAction(action)

    def set_checkbox_action(self, key, parentMenu, firstEntity, firstAttribut):
        action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize(), parentMenu,
                         checkable=True)
        if firstEntity in key.split("-:") or firstAttribut in key.split("-:"):
            action.setChecked(True)
            if self.typeDiagram in ['pie', 'hist', 'stackplot']:
                self.previous_selected_checkboxes = []
                self.previous_selected_checkboxes.append(key)
        action.setProperty("key", key)
        action.triggered.connect(self.update_plot)
        parentMenu.addAction(action)
        return action


    def get_checkbox_display_menu_selected(self):
        if not self.is_refresh and self.typeDiagram in ['pie', 'hist', 'stackplot']:
            for option, checkbox in self.checkbox_display_menu_data.items():
                if option in self.previous_selected_checkboxes:
                    checkbox.setChecked(False)
                else:
                    checkbox.setChecked(True)
        selected_option = [option for option, checkbox in self.checkbox_display_menu_data.items() if
                           checkbox.isChecked()]
        return selected_option

    def onCmbRoundActivated(self):
        print("test")
        try:
            if self.start_cmb_round and self.end_cmb_round and self.start_cmb_round.currentText() and self.end_cmb_round.currentText():
                min_round_selected = int(re.search(r'\d+', self.start_cmb_round.currentText()).group())
                max_round_selected = int(re.search(r'\d+', self.end_cmb_round.currentText()).group())
                if min_round_selected < max_round_selected:
                    self.roundMax = max_round_selected
                    self.roundMin = min_round_selected
        except ValueError:
            print("Erreur de conversion")
        except Exception as e:
            print("Erreur survenue :", e)



    def update_plot(self):
        self.update_data()

        selected_option_list = self.get_checkbox_display_menu_selected()
        if self.typeDiagram == 'plot':
            self.plot_linear_typeDiagram(self.dataEntities, selected_option_list)
        elif self.typeDiagram == 'pie':
            self.plot_pie_typeDiagram(self.dataEntities, selected_option_list)
        elif self.typeDiagram == 'hist':
            self.plot_hist_typeDiagram(self.dataEntities, selected_option_list)
        elif self.typeDiagram == 'stackplot':
            self.plot_stackplot_typeDiagram(self.dataEntities, selected_option_list)
        # for pie diagram
        if not self.is_refresh:
            self.previous_selected_checkboxes = list(set(
                    option for option, checkbox in self.checkbox_display_menu_data.items() if checkbox.isChecked()))
        self.is_refresh = False

    def plot_stackplot_typeDiagram(self, data, selected_option_list):
        list_data = []
        formatted_data = {}
        entity_name_list = []
        list_attribut_key = []
        attribut_value = ""
        self.ax.clear()
        for option in selected_option_list:
            if "-:" in option:
                list_opt = option.split("-:")
                entityName = list_opt[1]
                entity_name_list.append(entityName)
                attribut_value = list_opt[-1]
                list_attribut_key.append(attribut_value)
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
        attribut_name_list = list(set(list_attribut_key))
        self.title = "Variation des {} des {}".format(", ".join(attribut_name_list), " et ".join(list(set(entity_name_list))))
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_hist_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        list_data = []
        entity_name_list = []
        attribut_value=""
        for option in selected_option_list:
            if "-:" in option:
                list_opt = option.split("-:")
                entity_name = list_opt[1]
                entity_name_list.append(entity_name)
                attribut_value = list_opt[-1]
                histo_y = {f"{entity_name}-{attribut_value}" : entry['quantiAttributes'][attribut_value]['histo']
                      for entry in data if entry['entityName']==entity_name  and 'quantiAttributes' in entry \
                           and attribut_value in entry['quantiAttributes'] and 'histo' in \
                            entry['quantiAttributes'][attribut_value] and entry['round'] == max(self.rounds)}
                #print("histo_y :: ", histo_y)
                list_data.append(histo_y)

        for h in list_data:
            h_abcis = list(h.values())[0][1][:-1]
            h_height = list(h.values())[0][0]
            label = str(list(h.keys())[0]) if h.keys() and len(list(h.keys()))>0 else ''
            #print("h_abcis : ", h_abcis)
            #print("h_height : ", h_height)
            self.ax.bar(h_abcis, h_height, width=5, label=label)
        self.ax.legend()
        #print("title", self.title)
        self.title = "Analyse de la fréquence des {} des {}".format(attribut_value, " et ".join(entity_name_list))
        self.ax.set_title(self.title)
        self.ax.set_xlabel('Valeurs')
        self.ax.set_ylabel('Fréquences')
        self.canvas.draw()

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
            self.title = f"Répartition des {entityName} par {attribut_value} en (%)"
            self.ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax.axis('equal')
            self.ax.legend()
            self.ax.set_title(self.title)
            self.canvas.draw()


    def plot_linear_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        pos = 0
        has_simvariables = any(item.startswith('simvariables-:') for item in selected_option_list)

        if len(selected_option_list)>0 and "-:" in selected_option_list[0]:
            self.plot_linear_typeDiagram_for_entities(data, selected_option_list)
        if has_simvariables:
            self.plot_linear_typeDiagram_for_simVariable(self.dataSimVariables, selected_option_list, pos)
        """
            elif variable == 'simVariable':
                self.plot_linear_typeDiagram_for_simVariable(data, selected_option_list, pos)
            elif variable == 'currentPlayer':
                self.plot_linear_typeDiagram_for_players(data, selected_option_list, pos)"""
        #pos += 1

    def plot_linear_typeDiagram_for_simVariable(self, dataSimVariables, selected_option_list, pos):
        list_simVariables = [item.split("-:")[1] for item in selected_option_list if item.startswith('simvariables-:') and item.split("-:") and len(item.split("-:"))>0]
        if list_simVariables:
            for simVarName in list_simVariables:
                y = [entry['value'] for entry in dataSimVariables if entry['simVarName'] == simVarName]
                self.plot_data_switch_xvalue(self.xValue, y, f"Simulations Variable : {simVarName}", 'solid', pos)
            self.ax.legend()
            title = "{} et des Simulations Variables".format(self.title)
            self.ax.set_title(title)
            self.canvas.draw()

    def plot_linear_typeDiagram_for_entities(self, data, selected_option_list):
        self.ax.clear()
        pos=0
        list_entity_name = []
        list_attribut_key = []
        if len(selected_option_list) > 0 and "-:" in selected_option_list[0]:
            for option in selected_option_list:
                pos += 1
                list_option = option.split("-:")
                if len(list_option)>0:
                    entityName = list_option[1]
                    list_entity_name.append(entityName)
                    label_pop = f"Populations : {entityName}"
                    key = list_option[-1] if list_option[-1] else None
                    data_populations = []; data_indicators = []; data_min=[]; data_max=[]; data_mean=[]; data_stdev=[] ; data_sum=[]
                    # for r in self.rounds:
                    #     if key == 'population':
                    #         y = [sum(entry['population'] for entry in data if entry['round'] == r
                    #                  and entry['entityName'] == entityName)]
                    #         data_populations.append(y)
                    #     else:
                    #         if key and key in self.indicators_item:
                    #             attribut_key = list_option[2]
                    #             list_attribut_key.append(attribut_key)
                                    
                    #             y_indicators = [sum(entry['quantiAttributes'][attribut_key][key] for entry in data if
                                #   ATTENTION : -->il ne faut pas faire la sum des valeurs phases

                    #                          entry['round'] == r and entry['entityName'] == entityName and
                    #                          list_option[-1] in entry['quantiAttributes'][attribut_key])]
                    #             data_indicators.append(y_indicators)

                    if self.optionRoundorSteps == 'by rounds' or (self.optionRoundorSteps == 'by steps' and self.nbPhases == 1):
                        for r in range(self.nbRoundsWithLastPhase+1):
                            phaseIndex = self.nbPhases if r !=0 else 0 
                            aEntry = [entry for entry in data if entry['entityName'] == entityName and entry['round'] == r and entry['phase'] == phaseIndex][-1]                 
                            if key == 'population':
                                y = aEntry['population']
                                data_populations.append(y)
                            else:
                                if key and key in self.indicators_item:
                                    attribut_key = list_option[2]
                                    list_attribut_key.append(attribut_key)
                                    y_indicators = aEntry['quantiAttributes'][attribut_key][key] 
                                    data_indicators.append(y_indicators)

                    else: #Case --> 'by steps'
                        #1/ get the first step (round 0, phase 0)
                        aEntry = [entry for entry in data if entry['entityName'] == entityName and entry['round'] == 0 and entry['phase'] == 0][-1]                 
                        if key == 'population':
                            y = aEntry['population']
                            data_populations.append(y)
                        else:
                            if key and key in self.indicators_item:
                                attribut_key = list_option[2]
                                list_attribut_key.append(attribut_key)
                                y_indicators = aEntry['quantiAttributes'][attribut_key][key] 
                                data_indicators.append(y_indicators)
                        #2/ get all the phases from all the rounds that have been completed
                        for aR in range(self.nbRoundsWithLastPhase):
                            for aP in range(self.nbPhases):
                                aEntry = [entry for entry in data if entry['entityName'] == entityName and entry['round'] == (aR+1) and entry['phase'] == (aP+1)][-1]                 
                                if key == 'population':
                                    y = aEntry['population']
                                    data_populations.append(y)
                                else:
                                    if key and key in self.indicators_item:
                                        attribut_key = list_option[2]
                                        list_attribut_key.append(attribut_key)
                                        y_indicators = aEntry['quantiAttributes'][attribut_key][key] 
                                        data_indicators.append(y_indicators)
                        #3/ in case the last round has not been completed, get the phases from this last round
                        if self.phaseOfLastRound != self.nbPhases:
                            for aP in range(self.phaseOfLastRound):
                                aEntry = [entry for entry in data if entry['entityName'] == entityName and entry['round'] == self.nbRounds and entry['phase'] == (aP+1)][-1]
                                if key == 'population':
                                    y = aEntry['population']
                                    data_populations.append(y)
                                else:
                                    if key and key in self.indicators_item:
                                        attribut_key = list_option[2]
                                        list_attribut_key.append(attribut_key)
                                        y_indicators = aEntry['quantiAttributes'][attribut_key][key] 
                                        data_indicators.append(y_indicators)

                    if len(data_populations)>0:
                        self.plot_data_switch_xvalue(self.xValue, data_populations, label_pop,'solid', pos)
                    if key and key in self.indicators_item:
                        label_ind = f"{self.indicators_item[key]} - {attribut_key} - {entityName}"
                        linestyle_ind = self.linestyle_items[key] if key and key in self.linestyle_items else None
                        self.plot_data_switch_xvalue(self.xValue, data_indicators, label_ind, linestyle_ind, pos)

            self.ax.legend()
            entity_name_list = list(set(list_entity_name))
            attribut_name_list = list(set(list_attribut_key))
            self.title = "Evolution des populations {} et des indicateurs des {}".format(" et ".join(entity_name_list), ", ".join(attribut_name_list) )
            self.ax.set_title(self.title)
            self.canvas.draw()

    def plot_data_switch_xvalue(self, xValue, data, label, linestyle, pos):
        color = self.colors[pos % len(self.colors)]
        if len(xValue) == 1:
            self.ax.plot(xValue * len(data), data, label=label, color=color, marker='o', linestyle='None')
        else:
            self.ax.plot(xValue, data, label=label, linestyle=linestyle, color=color)


    def plot_linear_typeDiagram_for_players(self, data, list_option, pos):
        if list_option[:1] == ['currentPlayer']:
            entities = list_option
            label = f"Player : {entities[-1].upper()}"
            y = [sum(1 for entry in data if entry['round'] == r \
                     and entry['phase'] == p and 'currentPlayer' in entry and
                     entry['currentPlayer'] == list_option[-1])
                 for r in self.rounds for p in self.phases]
            color = self.colors[pos % len(self.colors)]
            self.ax.plot(self.xValue, y, label=label, linestyle='solid', color=color)
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def set_combobox_2_items(self):
        #if self.typeDiagram not in ['pie', 'hist']:
        self.data_2_combobox.clear()
        for display_text in self.combobox_2_data:
            self.data_2_combobox.addItem(display_text)
        for index, (display_text, key) in enumerate(self.combobox_2_data.items()):
            self.data_2_combobox.setItemData(index, key)

    def load_cmb_per_rounds_data(self):
        self.start_cmb_round.setEnabled(True)
        self.end_cmb_round.setEnabled(True)
        self.add_button.setEnabled(True)
        if self.typeDiagram in ['plot']:
            self.combobox_per_rounds_data = {'Round ' + str(i): i for i in range(0, self.nbRounds + 1)}
            #selected_text = self.data_2_combobox.currentText()
            self.start_cmb_round.clear()
            self.end_cmb_round.clear()
            for display_text in self.combobox_per_rounds_data:
                self.start_cmb_round.addItem(display_text)
                self.end_cmb_round.addItem(display_text)
            for index, (display_text, key) in enumerate(self.combobox_per_rounds_data.items()):
                self.end_cmb_round.setItemData(index, key)
                self.start_cmb_round.setItemData(index, key)

    """def set_checkbox_values(self):
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
        self.addSeparator()"""

    def get_combobox2_selected_key(self):
        if self.data_2_combobox:
            selected_text = self.data_2_combobox.currentText()
            for key, value in self.combobox_2_data.items():
                if key == selected_text:
                    return value
        return None

    """def get_checkbox_indicators_selected(self):
        selected_indicators = [option for option, checkbox in self.checKbox_indicators.items() if checkbox.isChecked()]
        return selected_indicators"""

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



    def refresh_data(self):
        self.is_refresh = True
        selected_option = self.get_checkbox_display_menu_selected()
        self.update_plot()

    def update_data(self):
        # self.data = self.getAllData()
        # self.data = self.model.dataRecorder.listOfData_ofEntities
        # self.data = self.model.dataRecorder.getStepsData_ofEntities()
        self.dataEntities = self.model.dataRecorder.getStats_ofEntities()
        self.dataSimVariables = self.model.dataRecorder.getStepsData_ofSimVariables()
        self.dataPlayers = self.model.dataRecorder.getStepsData_ofPlayers()
        #self.regenerate_menu(self.dataEntities)
        # if option == '1':
        # self.phases = {entry['phase'] for entry in data if  entry['phase'] == max_round}
        self.setXValueData(self.dataEntities)



    def setXValueData(self, data):
        option = self.get_combobox2_selected_key()
        # Option d'affichage par tour ou par Steps !!!!
        # self.optionRoundorSteps = 'by steps' 
        self.optionRoundorSteps = 'by rounds' 

        rounds = {entry['round'] for entry in data}
        phases = {entry['phase'] for entry in data}
        self.nbRounds = max({entry['round'] for entry in data})
        self.nbPhases = len(self.model.timeManager.phases) -1 #be careful. should be changed wjhen merged with main branch
        self.phaseOfLastRound = max({entry['phase'] for entry in data if entry['round'] == self.nbRounds})

        if option == '2':
            self.load_cmb_per_rounds_data()
            if self.roundMax!=0:
                self.nbRounds = self.roundMax - self.roundMin
                self.nbRoundsWithLastPhase = self.roundMax - self.roundMin
                rounds = {entry['round'] for entry in data if entry['round']>= self.roundMin and entry['round']<=self.roundMax}
                aStep = self.roundMin
                self.xValue = []
                for aR in range(self.roundMin, self.roundMax):
                    for aP in range(self.nbPhases):
                        aStep += 1
                        self.xValue.append(aStep)
                if self.phaseOfLastRound != self.nbPhases:
                    for aP in range(self.phaseOfLastRound):
                        aStep += 1
                        self.xValue.append(aStep)
                self.start_cmb_round.setCurrentText(f"Round {self.roundMin}")
                self.end_cmb_round.setCurrentText(f"Round {self.roundMax}")
        if option == '1':
            max_round = max(rounds)
            self.rounds = [max_round]
            #list_data = [entry for entry in data if entry['round'] == max(rounds) and entry['phase']>3]
            #self.dataEntities = list_data
            #print("list_data : ", list_data)
            #print("################################################################")
            #print("data : ", data)
            self.phases = {entry['phase'] for entry in data if entry['round'] == max_round}
            self.xValue = self.rounds if len(self.phases) <= 2 else [phase for phase in self.phases]
            #self.xValue = [p for _ in rounds for p in phases]
            #print("self.phases :: ", self.phases)
        if self.optionRoundorSteps == 'by rounds' or (self.optionRoundorSteps == 'by steps' and self.nbPhases == 1):
            if self.phaseOfLastRound == self.nbPhases:
                self.xValue = list(rounds)
                self.nbRoundsWithLastPhase = self.nbRounds
            else:
                self.nbRoundsWithLastPhase = self.nbRounds -1
                self.xValue = list(rounds)[:-1]

        else:  # case where         self.optionRoundorSteps == 'by steps' and self.nbPhases > 1:
            self.rounds = rounds
            self.phases = phases

            if self.phaseOfLastRound == self.nbPhases:
                self.nbRoundsWithLastPhase = self.nbRounds
            else:
                self.nbRoundsWithLastPhase = self.nbRounds -1
            aStep = 0
            self.xValue =[aStep]     
            for aR in range(self.nbRoundsWithLastPhase):
                for aP in range(self.nbPhases):
                    aStep += 1
                    self.xValue.append(aStep)
            if self.phaseOfLastRound != self.nbPhases:
                for aP in range(self.phaseOfLastRound):
                    aStep += 1
                    self.xValue.append(aStep)