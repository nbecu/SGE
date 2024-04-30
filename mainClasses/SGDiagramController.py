import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QVBoxLayout, QComboBox, QWidget, QAction, QMenu, \
    QPushButton, \
    QCheckBox, QSpinBox, QLabel, QSlider, QLineEdit, QActionGroup
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
import re


class SGDiagramController(NavigationToolbar):
    def __init__(self, canvas, parent, model, typeDiagram):
        super().__init__(canvas, parent)
        self.parent = parent
        self.typeDiagram = typeDiagram
        # layout_per_round = QVBoxLayout()


        self.roundMin = 0
        self.roundMax = 0
        self.is_refresh = False
        self.indicators = ['max', 'mean', 'min', 'stdev','sum']
        self.indicators_item = {'max': 'Max', 'mean': 'Moyenne', 'min': 'Min', 'stdev': 'St Dev', 'sum':'Sum'}
        self.option_affichage_data = {"entityName": "Entités", "simVariable": "Simulation variables",
                                      "currentPlayer": "Players"}
        self.ax = parent.ax
        self.model = model
        self.title = 'SG Diagramme'

        self.display_indicators_menu = QMenu("Indicators", self)
        self.checKbox_indicators_data = ["type", "Attribut", "Max", "Mean", "Min", "St Dev"]
        self.checKbox_indicators = {}

        self.rounds = []
        self.phases = []

        # self.linestyles = ['-', '--', '-.', ':', 'dashed', 'dashdot', 'dotted']
        self.linestyle_items = {'mean': 'solid', 'max': 'dashed', 'min': 'dashed','stdev': 'dotted', 'sum': 'dashdot' }

        self.colors = ['gray', 'green', 'blue', 'red', 'black', 'orange', 'purple', 'pink', 'cyan', 'magenta']
        self.xValue = []

        #generate menu of indicators
        self.indicators_menu = QMenu("Indicators", self)
        self.dictMenuData = {'entities': {}, 'simvariables': {}, 'players': {}}
        self.checkbox_display_menu_data = {}
        self.previous_selected_checkboxes = []
        self.parentAttributKey = 'quantiAttributes' if self.typeDiagram in ['plot', 'hist'] else 'qualiAttributes'

        self.groupAction = QActionGroup(self)
        self.firstEntity = ""
        self.firstAttribut = ""
        self.list_attribut_display = []
        self.dataEntities = self.model.dataRecorder.getStats_ofEntities()
        self.dataSimVariables = self.model.dataRecorder.getStepsData_ofSimVariables()
        self.dataPlayers = self.model.dataRecorder.getStepsData_ofPlayers()
        self.regenerate_indicators_menu(self.dataEntities)

        # Menu display option for x axis  
        self.combobox_2_data = {'Rounds': '0','Rounds & Phases': '3','Que phase 2': 'specified phase'}
        self.xAxisOption_combobox = QComboBox(parent)
        self.xAxisOption_combobox.currentIndexChanged.connect(self.update_plot)
        self.addWidget(self.xAxisOption_combobox)

        self.addSeparator()
        
        # Button refresh
        button = QPushButton("refresh", self)
        button.setIcon(QIcon("./icon/actualiser.png"))
        button.clicked.connect(self.refresh_data)
        self.addWidget(button)

        #Menu to display the data on specific interval

        # self.generateMenu_DisplaySpecificInterval(parent)


    def regenerate_indicators_menu(self, data):
        entitiesMenu = QMenu('Entités', self)
        playersMenu = QMenu('Players', self)
        simulationMenu = QMenu('Simulation variables', self)

        if self.typeDiagram == 'plot':

            #create menu items for entities
            ##retrieves the list of entities
            entities_list = {entry['entityName'] for entry in data if
                             'entityName' in entry and not isinstance(entry['entityName'], dict)}
            ###Take this opportunity to initialise the first entitiy to be selected in the menu
            if not self.firstEntity:
                self.firstEntity = sorted(entities_list)[0]
            ##define the list of indicators for entities attributes
            attrib_data = ['mean','sum', 'min','max','stdev']
            ##create the menu items
            for entity_name in sorted(entities_list):
                attrib_dict = {}
                attrib_dict[f"entity-:{entity_name}-:population"] = None
                list_entDef_attribut_key = {x for entry in data for x in entry.get('entDefAttributes', {}) if entry['entityName'] == entity_name}
                for entDef_attribut_key in sorted(list_entDef_attribut_key):
                    attrib_dict[f"entity-:{entity_name}-:{entDef_attribut_key}"] = None                                              
                list_attribut_key = {attribut for entry in data for attribut in entry.get(self.parentAttributKey, {}) if
                                     entry['entityName'] == entity_name}
                if not self.firstAttribut:
                    self.firstAttribut = "population"  # sorted(list_attribut_key)[0]
                for attribut_key in sorted(list_attribut_key):
                    attrib_dict[attribut_key] = {f"entity-:{entity_name}-:{attribut_key}-:{option_key}": None for
                                                 option_key in attrib_data}
                self.dictMenuData['entities'][entity_name] = attrib_dict
            self.indicators_menu.addMenu(entitiesMenu)
            self.indicators_menu.addMenu(playersMenu)
            self.indicators_menu.addMenu(simulationMenu)
            self.addSubMenus(entitiesMenu, self.dictMenuData['entities'], self.firstEntity, self.firstAttribut)

            #create menu items for simVariables
            simVariables_list = list(set(entry['simVarName'] for entry in self.dataSimVariables))
            for simVar in simVariables_list:
                self.dictMenuData['simvariables'][f"simvariables-:{simVar}"] = None
            self.addSubMenus(simulationMenu, self.dictMenuData['simvariables'], self.firstEntity, self.firstAttribut)

            #Create menu items for players
            ##get the list of players
            players_list = {entry['currentPlayer'] for entry in data if  #todo : c'est bizarre ce test sur 'currentPlayer'
                            'currentPlayer' in entry and not isinstance(entry['currentPlayer'], dict)}
            for player in players_list:
                self.dictMenuData['players'][f"currentPlayer-:{player}"] = player
            """for key in simVariables_list:
                list_data = {entry['simVariable'][key] for entry in data if isinstance(entry.get('simVariable', {}), dict)}
                self.dictMenuData['simvariables'][f"simVariable-:{key}"] = list_data"""
            players_list = {entry['playerName'] for entry in  self.dataPlayers if 'playerName' in entry and not isinstance(entry['playerName'], dict)}
            ##create the menu for players
            for player_name in sorted(players_list):
                attrib_dict = {}
                list_player_attribut_key = {x for entry in self.dataPlayers for x in entry.get('dictAttributes', {}) if entry['playerName'] == player_name}
                for player_attribut_key in sorted(list_player_attribut_key):
                    attrib_dict[f"player-:{player_name}-:{player_attribut_key}"] = None                                              
                self.dictMenuData['players'][player_name] = attrib_dict
            self.addSubMenus(playersMenu, self.dictMenuData['players'], self.firstEntity, self.firstAttribut)

        else:
            entities_list = {entry['entityName'] for entry in data if
                             'entityName' in entry and isinstance(entry[self.parentAttributKey], dict)
                             and entry[self.parentAttributKey].keys() and not isinstance(entry['entityName'], dict)}
            if not self.firstEntity:
                self.firstEntity = sorted(entities_list)[0] if len(entities_list)>0 else ''

            for entity_name in sorted(entities_list):
                attrib_dict = {}
                list_attribut_key = {attribut for entry in data for attribut in entry.get(self.parentAttributKey, {}) if
                                     entry.get('entityName') == entity_name and isinstance(
                                         entry[self.parentAttributKey][attribut], dict)}

                if not self.firstAttribut:
                    self.firstAttribut = sorted(list_attribut_key)[0] if len(list_attribut_key) > 0 else ""

                for attribut_key in list_attribut_key:
                    list_val = []
                    attrib_tmp_dict = {}
                    if self.typeDiagram in ['hist', 'pie', 'stackplot']:
                        attrib_dict[f"entity-:{entity_name}-:{attribut_key}"] = None
                    else:
                        for sub_attribut_val in {entry[self.parentAttributKey][attribut] for entry in data for attribut in
                                                 entry.get(self.parentAttributKey, {}) if
                                                 entry.get('entityName') == entity_name and isinstance(
                                                     entry[self.parentAttributKey][attribut], str)}:
                            list_val.append(sub_attribut_val)

                            attrib_tmp_dict[f"entity-:{entity_name}-:{attribut_key}-:{sub_attribut_val}"] = None
                        attrib_dict[attribut_key] = attrib_tmp_dict
                self.dictMenuData['entities'][entity_name] = attrib_dict
            self.indicators_menu.addMenu(entitiesMenu)
            self.addSubMenus(entitiesMenu, self.dictMenuData['entities'], self.firstEntity, self.firstAttribut)
        self.addAction(self.indicators_menu.menuAction())

    def addSubMenus(self, parentMenu, subMenuData, firstEntity, firstAttribut):
        for key, value in subMenuData.items():
            if isinstance(value, dict):
                submenu = QMenu(key, self)
                parentMenu.addMenu(submenu)
                self.addSubMenus(submenu, value, firstEntity, firstAttribut)
            else:
                if self.typeDiagram in ['pie', 'stackplot']:
                    action = self.createRadioButtonAction(key, parentMenu)
                    if key == f"entity-:{firstEntity}-:{firstAttribut}":
                        action.setChecked(True)
                else:
                    action = self.set_checkbox_action(key, parentMenu, firstEntity, firstAttribut)
                    if firstEntity in key.split("-:") and firstAttribut in key.split("-:"):
                        action.setChecked(True)
                        self.previous_selected_checkboxes.append(key)
                self.checkbox_display_menu_data[key] = action
                parentMenu.addAction(action)

    # set checkbox for diagram ( plot and hist )
    def set_checkbox_action(self, key, parentMenu, firstEntity, firstAttribut):
        self.previous_selected_checkboxes = []
        action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize(), parentMenu,
                         checkable=True)

        if key == f"entity-:{firstEntity}-:{firstAttribut}":
            action.setChecked(True)

        #else:
        #    if firstEntity in key.split("-:") and firstAttribut in key.split("-:"):
        #        action.setChecked(True)
        #        self.previous_selected_checkboxes.append(key)
        action.setProperty("key", key)
        action.triggered.connect(self.update_plot_from_checked_action)
        parentMenu.addAction(action)
        return action

    # for typediagram : (pie, stackplot, hist)
    def createRadioButtonAction(self, key, parentMenu):
        #action = QAction(key, self)
        action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize())
        action.setCheckable(True)
        parentMenu.addAction(action)
        self.groupAction.addAction(action)
        #print("key : ", key)
        #, firstEntity, firstAttribut
        action.triggered.connect(lambda: self.onActionTriggered(action))
        return action

    def onActionTriggered(self, action):
        # Désélectionner toutes les autres actions du même groupe
        for otherAction in self.groupAction.actions():
            if otherAction != action:
                otherAction.setChecked(False)
        self.update_plot()
            #print(f"otherAction : {otherAction.isChecked()} - text : {otherAction.text()}")

    def set_checkbox_action(self, key, parentMenu, firstEntity, firstAttribut):
        self.previous_selected_checkboxes = []
        action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize(), parentMenu,
                         checkable=True)

        if self.typeDiagram not in ['pie', 'hist', 'stackplot']:
            if firstEntity in key.split("-:") or firstAttribut in key.split("-:"):
                #action.setChecked(True)
                action.setCheckable(True)
        else:
            if firstEntity in key.split("-:") and firstAttribut in key.split("-:"):
                action.setChecked(True)
                self.previous_selected_checkboxes.append(key)
        action.setProperty("key", key)
        action.triggered.connect(self.update_plot_from_checked_action)
        parentMenu.addAction(action)
        return action


    # update plot after checked option
    def update_plot_from_checked_action(self, state):
        #print("state : ", state)
        if self.typeDiagram in ['pie', 'hist', 'stackplot']:
            selected_option = self.on_toggle_checked_option()
            for option, checkbox in self.checkbox_display_menu_data.items():
                checkbox.setChecked(option in selected_option)
            self.checkbox_display_menu_data.update()
        self.update_plot()

    # toggle value between previous and current option selected
    def on_toggle_checked_option(self):
        for option, checkbox in self.checkbox_display_menu_data.items():
            checkbox.setChecked(option not in self.previous_selected_checkboxes)
        self.groupAction.setExclusive(True)
        return [option for option, checkbox in self.checkbox_display_menu_data.items() if checkbox.isChecked()]

    # get checkbox selected
    def get_checkbox_display_menu_selected(self):
        return [option for option, checkbox in self.checkbox_display_menu_data.items() if checkbox.isChecked()]

    def onCmbRoundActivated(self):
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
        self.update_data() #todo   c'est déjà fait dans la méthode juste avant
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
        self.previous_selected_checkboxes = list(set(
            option for option, checkbox in self.checkbox_display_menu_data.items() if checkbox.isChecked()))


    def generateMenu_DisplaySpecificInterval(self, aParent):
        if self.typeDiagram in ['plot', 'stackplot']:
            self.addSeparator()
            self.combobox_2_data['Intervalle de tours'] = '2'
            self.start_label = QLabel('Tour Min:')
            self.start_cmb_round = QComboBox(aParent)
            self.start_cmb_round.activated.connect(self.onCmbRoundActivated)
            self.addWidget(self.start_label)
            self.addWidget(self.start_cmb_round)
            self.end_label = QLabel('Tour Max:')
            self.end_cmb_round = QComboBox(aParent)
            self.end_cmb_round.activated.connect(self.onCmbRoundActivated)
            self.addWidget(self.end_label)
            self.addWidget(self.end_cmb_round)
            self.combobox_per_rounds_data = {}
            self.add_button = QPushButton('Afficher')
            self.add_button.clicked.connect(self.update_plot)
            self.addWidget(self.add_button)
            self.start_cmb_round.setEnabled(False)
            self.end_cmb_round.setEnabled(False)
            self.add_button.setEnabled(False)

 
    ##############################################################################

    def plot_stackplot_typeDiagram(self, data, selected_option_list):
        list_data = []
        formatted_data = {}
        entity_name_list = []
        list_attribut_key = []
        attribut_value = ""
        self.ax.clear()

        data_y = []
        optionXScale = self.get_combobox2_selected_key()

        for option in selected_option_list:
            if "-:" in option:
                list_opt = option.split("-:")
                entityName = list_opt[1]
                entity_name_list.append(entityName)
                attribut_value = list_opt[-1]
                list_attribut_key.append(attribut_value)

                # data_y = [entry['value'] for entry in dataSimVariables if entry['simVarName'] == simVarName]
                if optionXScale != '3' or (optionXScale == '3' and self.nbPhases == 1):
                    if self.nbRounds == 0:
                        nbRounds = self.nbRounds
                        self.xValue = [0,1]
                    else:
                        nbRounds = self.nbRoundsWithLastPhase
                    for r in range(nbRounds + 1):
                        phaseIndex = self.nbPhases if r != 0 else 0
                        aEntry = [entry[self.parentAttributKey][attribut_value] for entry in data if entry['entityName'] == entityName
                                  and attribut_value in entry[self.parentAttributKey] and
                                  entry['round'] == r and entry['phase'] == phaseIndex][-1]
                        list_data.append(aEntry)

                else:  # Case --> 'by steps'
                    # 1/ get the first step (round 0, phase 0)
                    aEntry = [entry[self.parentAttributKey][attribut_value] for entry in data if
                              entry['entityName'] == entityName
                              and attribut_value in entry[self.parentAttributKey] and
                              entry['round'] == 0 and entry['phase'] == 0][-1]
                    list_data.append(aEntry)
                    # 2/ get all the phases from all the rounds that have been completed
                    for aR in range(self.nbRoundsWithLastPhase):
                        for aP in range(self.nbPhases):
                            aEntry = [entry[self.parentAttributKey][attribut_value] for entry in data if
                                      entry['entityName'] == entityName and attribut_value in entry[self.parentAttributKey]
                                      and entry['round'] == (aR + 1) and entry['phase'] == (aP + 1)][-1]
                            list_data.append(aEntry)

                    # 3/ in case the last round has not been completed, get the phases from this last round
                    if self.phaseOfLastRound != self.nbPhases:
                        for aP in range(self.phaseOfLastRound):
                            aEntry = [entry[self.parentAttributKey][attribut_value] for entry in data
                                      if len(data)>0 and self.parentAttributKey in entry and
                                      entry['entityName'] == entityName and attribut_value in entry[self.parentAttributKey]
                                      and entry['round'] == self.nbRounds and entry['phase'] == (aP + 1)][-1]
                            list_data.append(aEntry)

        if len(list_data)>0:
            labels = sorted(list(set(np.concatenate([list(aData.keys()) for aData in list_data]))))
            values = []
            for aLabel in labels:
                values.append([aData.get(aLabel, 0) for aData in list_data])
            self.plot_stack_plot_data_switch_xvalue(self.xValue, values, labels)
            self.ax.legend()
            print("labels : ", labels)
            #title = "{} et des Simulations Variables".format(self.title)
            self.title = "Analyse comparative des composantes de la {} ".format(attribut_value.capitalize())
            self.ax.set_title(self.title)
            self.canvas.draw()
        else:
            titre = "Impossible d'afficher les données"
            message = "Aucune données à afficher. veuillez continuer le jeu "
            self.showErrorMessage(titre, message)
            #QApplication.quit()


    # message d'erreur si aucune données a affiché
    def showErrorMessage(self, titre, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setWindowTitle(titre)
        error_dialog.setText(message)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()

    def plot_stack_plot_data_switch_xvalue(self, xValue, data, label):
        if len(xValue) == 1:
            self.ax.stackplot(xValue * len(data), data, labels=label)
        else:
            self.ax.stackplot(xValue, data, labels=label)
            option = self.get_combobox2_selected_key()
            if self.nbPhases > 2 and option == '3':
                # Display red doted vertical lines to shaw the rounds
                round_lab = 1
                for x_val in xValue:
                    if (x_val -1) % self.nbPhases == 0 and x_val != 1:
                        self.ax.axvline(x_val, color='r', ls=':')
                        self.ax.text(x_val, 1, f"Round {round_lab}", color='r', ha='right', va='top', rotation=90,
                                     transform=self.ax.get_xaxis_transform())
                        round_lab += 1

    def plot_hist_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        list_data = []
        entity_name_list = []
        attribut_value = ""

        for option in selected_option_list:
            if "-:" in option:
                list_opt = option.split("-:")
                entity_name = list_opt[1]
                entity_name_list.append(entity_name)
                attribut_value = list_opt[-1]
                histo_y = {f"{entity_name}-{attribut_value}": entry[self.parentAttributKey][attribut_value]['histo']
                           for entry in data if entry['entityName'] == entity_name and self.parentAttributKey in entry
                           and attribut_value in entry[self.parentAttributKey] and 'histo' in
                           entry[self.parentAttributKey][attribut_value] and entry['round'] == max(self.rounds)}
                list_data.append(histo_y)

        for h in list_data:
            h_abcis = np.average([list(h.values())[0][1][1:], list(h.values())[0][1][:-1]], axis=0)
            h_height = list(h.values())[0][0]
            label = str(list(h.keys())[0]) if h.keys() and len(list(h.keys())) > 0 else ''
            bins = [val - (h_abcis[1] - h_abcis[0]) / 2 for val in h_abcis] + [
                h_abcis[-1] + (h_abcis[1] - h_abcis[0]) / 2]
            self.ax.hist(h_abcis, weights=h_height, bins=bins, label=label, edgecolor='black')
            self.ax.set_xticks(list(h.values())[0][1])

        self.ax.legend()
        self.title = "Analyse de la fréquence des {} des {}".format(attribut_value, " et ".join(entity_name_list))
        self.ax.set_title(self.title)
        self.ax.set_xlabel(attribut_value)
        self.ax.set_ylabel('Nombre d''occurences')
        self.canvas.draw()

    def plot_pie_typeDiagram(self, data, selected_option_list):
        if len(selected_option_list) > 0 and "-:" in selected_option_list[0]:
            list_option = selected_option_list[0].split("-:")
            entityName = list_option[1]
            attribut_value = list_option[2]
            self.ax.clear()
            data_pie = next((entry[self.parentAttributKey][attribut_value] for entry in data
                             if entry['round'] == max(self.rounds) and
                             entry['entityName'] == entityName and attribut_value in entry[self.parentAttributKey]), None)

            labels = list(data_pie.keys())
            values = list(data_pie.values())
            self.title = f"Répartition des {entityName} par {attribut_value} en (%)"
            self.ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax.axis('equal')
            self.ax.legend()
            self.ax.set_title(self.title)
            self.canvas.draw()

    def plot_linear_typeDiagram_OLDDDDDDDD(self, data, selected_option_list):
        self.ax.clear()
        pos = 0
        if any(item.startswith('entity-:') for item in selected_option_list):
            self.plot_linear_typeDiagram_for_entities(data, selected_option_list)

        if any(item.startswith('simvariables-:') for item in selected_option_list):
            self.plot_linear_typeDiagram_for_simVariable(self.dataSimVariables, selected_option_list, pos)

        if any(item.startswith('player-:') for item in selected_option_list):
            self.plot_linear_typeDiagram_for_players(self.dataPlayers, selected_option_list, pos)


    def plot_linear_typeDiagram(self, data, selected_option_list):
        self.ax.clear()
        optionXScale = self.get_combobox2_selected_key()
        pos = 0

        for option in selected_option_list:
            pos += 1
            list_option = option.split("-:")
            entity_type = list_option[1] if len(list_option) > 1 and 'entity' in list_option else None
            key = list_option[-1] if list_option[-1] else None

            if optionXScale in ('0', '2') or (optionXScale == '3' and self.nbPhases == 1) or optionXScale == 'specified phase':
                self.process_data(data, [option],  pos, entity_type, key)
            else:  # Case --> 'by steps'
                self.process_data(data, [option],  pos, entity_type, key)

        self.ax.legend()
        title_entities = ", ".join(set([option.split("-:")[1] for option in selected_option_list if 'entity' in option]))
        title = f"Evolution des populations {title_entities}"
        self.ax.set_title(title)
        self.canvas.draw()


    def process_data(self, data, selected_option_list, pos, entity_type=None, key=None):
        data_y = []
        for option in selected_option_list:
            entity_condition = 'entity' in option.split("-:")
            if entity_type and entity_condition and entity_type not in option:
                continue

            label = f"Simulations Variable : {entity_type}" if entity_type else f"Populations : {entity_type}"

            for r in range(self.nbRoundsWithLastPhase + 1):
                phaseIndex = self.nbPhases if r != 0 else 0
                condition = {'round': r, 'phase': phaseIndex}
                if entity_type:
                    condition['entityName'] = entity_type

                if key:
                    condition['key'] = key

                entries = [entry for entry in data if all(entry.get(k) == v for k, v in condition.items())]
                ####  >>> NON , ca marche pas . cette méthoe généré par chatGPT ne donne rien
                if entries:
                    data_y.append(entries[-1]['population'] if key == 'population' else entries[-1]['value'])
                    
        if data_y:
            self.plot_data_switch_xvalue(self.xValue, data_y, label, 'solid', pos)




########""
    def plot_linear_typeDiagram_for_simVariable(self, dataSimVariables, selected_option_list, pos):
        data_y = []
        optionXScale = self.get_combobox2_selected_key()
        list_simVariables = [item.split("-:")[1] for item in selected_option_list if
                             item.startswith('simvariables-:') and item.split("-:") and len(item.split("-:")) > 0]
        if list_simVariables:
            for simVarName in list_simVariables:
                label = f"Simulations Variable : {simVarName}"
                # data_y = [entry['value'] for entry in dataSimVariables if entry['simVarName'] == simVarName]
                if optionXScale != '3' or (optionXScale == '3' and self.nbPhases == 1):
                    for r in range(self.nbRoundsWithLastPhase + 1):
                        phaseIndex = self.nbPhases if r != 0 else 0
                        aEntry = [entry['value'] for entry in dataSimVariables if 'value' in entry and
                                  entry['simVarName'] == simVarName and entry['round'] == r and entry[
                                      'phase'] == phaseIndex][-1]
                        data_y.append(aEntry)

                else:  # Case --> 'by steps'
                    # 1/ get the first step (round 0, phase 0)
                    aEntry = [entry['value'] for entry in dataSimVariables if 'value' in entry and
                              entry['simVarName'] == simVarName and entry['round'] == 0 and entry['phase'] == 0][-1]
                    data_y.append(aEntry)
                    # 2/ get all the phases from all the rounds that have been completed
                    for aR in range(self.nbRoundsWithLastPhase):
                        for aP in range(self.nbPhases):
                            aEntry = [entry['value'] for entry in dataSimVariables if 'value' in entry and
                                      entry['simVarName'] == simVarName and entry['round'] == (aR + 1) and entry[
                                          'phase'] == (aP + 1)][-1]
                            data_y.append(aEntry)

                    # 3/ in case the last round has not been completed, get the phases from this last round
                    if self.phaseOfLastRound != self.nbPhases:
                        if len(dataSimVariables) == 1:
                            self.xValue = [0,1]
                            aEntry = [entry['value'] for entry in dataSimVariables if 'value' in entry and
                                      entry['simVarName'] == simVarName and entry['round'] == 0 and entry['phase'] == 0][-1]
                            data_y.append(aEntry)
                        else:
                            for aP in range(self.phaseOfLastRound):
                                aEntry = [entry['value'] for entry in dataSimVariables
                                          if len(dataSimVariables)>0 and 'value' in entry and
                                          entry['simVarName'] == simVarName and entry['round'] == self.nbRounds and
                                          entry['phase'] == (aP + 1)] #[-1]
                                data_y.append(aEntry)
                self.plot_data_switch_xvalue(self.xValue, data_y, label, 'solid', pos)
        self.ax.legend()
        title = "{} et des Simulations Variables".format(self.title)
        self.ax.set_title(title)
        self.canvas.draw()

    def plot_linear_typeDiagram_for_entities(self, data, selected_option_list):
        # self.ax.clear()
        optionXScale = self.get_combobox2_selected_key()
        # Option d'affichage par tour ou par Steps !!!!
        phaseToDisplay = 2 if optionXScale =='specified phase' else self.nbPhases
        pos = 0
        list_entity_name = []
        list_entDef_key = []
        list_attribut_key = []
        if len(selected_option_list) > 0 and "-:" in selected_option_list[0]:
        # if any(item.startswith('entity-:') for item in selected_option_list):
            for option in selected_option_list:
                pos += 1
                list_option = option.split("-:")
                # if len(list_option) > 0 and 'simvariables' not in list_option:
                if len(list_option) > 0 and 'entity'  in list_option:
                    entityName = list_option[1]
                    list_entity_name.append(entityName)
                    label_pop = f"Populations : {entityName}"
                    key = list_option[-1] if list_option[-1] else None
                    data_populations = [];
                    entDef_indicators = [];
                    data_indicators = [];

                    if optionXScale in ('0','2') or (optionXScale == '3' and self.nbPhases == 1) or optionXScale =='specified phase':
                        for r in range(self.nbRoundsWithLastPhase + 1):
                            phaseIndex = phaseToDisplay if r != 0 else 0
                            aEntry = [entry for entry in data if
                                      entry['entityName'] == entityName
                                      and entry['round'] == r
                                      and entry['phase'] == phaseIndex][-1]
                            if key == 'population':
                                y = aEntry['population']
                                data_populations.append(y)
                            elif key in aEntry['entDefAttributes']:
                                attribut_key = list_option[2]
                                list_entDef_key.append(attribut_key)
                                y_indicators = aEntry['entDefAttributes'][attribut_key]
                                entDef_indicators.append(y_indicators)
                            else:
                                if key and key in self.indicators_item:
                                    attribut_key = list_option[2]
                                    list_attribut_key.append(attribut_key)
                                    y_indicators = aEntry[self.parentAttributKey][attribut_key][key]
                                    data_indicators.append(y_indicators)
                    else:  # Case --> 'by steps'
                        # 1/ get the first step (round 0, phase 0)
                        aEntry = [entry for entry in data if
                                  entry['entityName'] == entityName and entry['round'] == 0 and entry['phase'] == 0][-1]
                        if key == 'population':
                            y = aEntry['population']
                            data_populations.append(y)
                        else:
                            if key and key in self.indicators_item:
                                attribut_key = list_option[2]
                                list_attribut_key.append(attribut_key)
                                y_indicators = aEntry[self.parentAttributKey][attribut_key][key]
                                data_indicators.append(y_indicators)
                        # 2/ get all the phases from all the rounds that have been completed
                        for aR in range(self.nbRoundsWithLastPhase):
                            for aP in range(self.nbPhases):
                                aEntry = [entry for entry in data if
                                          entry['entityName'] == entityName and entry['round'] == (aR + 1) and entry[
                                              'phase'] == (aP + 1)][-1]
                                if key == 'population':
                                    y = aEntry['population']
                                    data_populations.append(y)
                                else:
                                    if key and key in self.indicators_item:
                                        attribut_key = list_option[2]
                                        list_attribut_key.append(attribut_key)
                                        y_indicators = aEntry[self.parentAttributKey][attribut_key][key]
                                        data_indicators.append(y_indicators)
                        # 3/ in case the last round has not been completed, get the phases from this last round
                        if self.phaseOfLastRound != self.nbPhases:
                            for aP in range(self.phaseOfLastRound):
                                aEntry = [entry for entry in data if
                                          entry['entityName'] == entityName and entry['round'] == self.nbRounds and
                                          entry['phase'] == (aP + 1)][-1]
                                if key == 'population':
                                    y = aEntry['population']
                                    data_populations.append(y)
                                else:
                                    if key and key in self.indicators_item:
                                        attribut_key = list_option[2]
                                        list_attribut_key.append(attribut_key)
                                        y_indicators = aEntry[self.parentAttributKey][attribut_key][key]
                                        data_indicators.append(y_indicators)

                    if len(data_populations) > 0:
                        self.plot_data_switch_xvalue(self.xValue, data_populations, label_pop, 'solid', pos)
                    if len(entDef_indicators) > 0:
                        self.plot_data_switch_xvalue(self.xValue, entDef_indicators, list_entDef_key, 'solid', pos)
                    if key and key in self.indicators_item and len(list_option)>2:
                        label_ind = f"{self.indicators_item[key]} - {attribut_key} - {entityName}"
                        linestyle_ind = self.linestyle_items[key] if key and key in self.linestyle_items else None
                        self.plot_data_switch_xvalue(self.xValue, data_indicators, label_ind, linestyle_ind, pos)

            self.ax.legend()
            entity_name_list = list(set(list_entity_name))
            attribut_name_list = list(set(list_attribut_key))
            self.title = "Evolution des populations {} et des indicateurs des {}".format(" et ".join(entity_name_list),
                                                                                         ", ".join(attribut_name_list))
            self.ax.set_title(self.title)
            self.canvas.draw()

    def plot_data_switch_xvalue(self, xValue, data, label, linestyle, pos):
        color = self.colors[pos % len(self.colors)]
        if len(xValue) == 1:
            self.ax.plot(xValue * len(data), data, label=label, color=color, marker='o', linestyle='None')
        else:
            data = [0 if isinstance(item, list) and len(item) == 0 else item for item in data]
            if len(xValue) > len(data):
                data.extend([0] * (len(xValue) - len(data)))
            self.ax.plot(xValue, data, label=label, linestyle=linestyle, color=color)
            option = self.get_combobox2_selected_key()
            if self.nbPhases > 2 and option == '3':
                # Display red doted vertical lines to shaw the rounds
                round_lab = 1
                for x_val in xValue:
                    if (x_val -1) % self.nbPhases == 0 :
                        self.ax.axvline(x_val, color='r', ls=':')
                        self.ax.text(x_val, 1, f"Round {round_lab}", color='r', ha='right', va='top', rotation=90,
                                     transform=self.ax.get_xaxis_transform())
                        round_lab += 1

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
        # if self.typeDiagram not in ['pie', 'hist']:
        if self.typeDiagram in ['plot', 'stackplot']:
            self.xAxisOption_combobox.clear()
            if self.nbRounds == 1:
                sorted_combobox_data = dict(sorted(self.combobox_2_data.items(), key=lambda item: item[1], reverse=True))
                self.combobox_2_data = sorted_combobox_data
            for display_text in self.combobox_2_data:
                self.xAxisOption_combobox.addItem(display_text)
            for index, (display_text, key) in enumerate(self.combobox_2_data.items()):
                self.xAxisOption_combobox.setItemData(index, key)
        """
        if self.nbRounds == 1:
            self.data_2_combobox.setCurrentText("Tous les phases")
            return '3'
        """
        """if self.typeDiagram in ['plot', 'stackplot']:
            self.data_2_combobox.clear()
            for display_text in self.combobox_2_data:
                self.data_2_combobox.addItem(display_text)
            for index, (display_text, key) in enumerate(self.combobox_2_data.items()):
                self.data_2_combobox.setItemData(index, key)"""

    def load_cmb_per_rounds_data(self):
        self.start_cmb_round.setEnabled(True)
        self.end_cmb_round.setEnabled(True)
        self.add_button.setEnabled(True)
        if self.typeDiagram in ['plot', 'stackplot']:
            self.combobox_per_rounds_data = {'Round ' + str(i): i for i in range(0, self.nbRounds + 1)}
            # selected_text = self.data_2_combobox.currentText()
            self.start_cmb_round.clear()
            self.end_cmb_round.clear()
            for display_text in self.combobox_per_rounds_data:
                self.start_cmb_round.addItem(display_text)
                self.end_cmb_round.addItem(display_text)
            for index, (display_text, key) in enumerate(self.combobox_per_rounds_data.items()):
                self.end_cmb_round.setItemData(index, key)
                self.start_cmb_round.setItemData(index, key)

    def get_combobox2_selected_key(self):
        if self.typeDiagram in ['plot', 'stackplot'] and self.xAxisOption_combobox:
            selected_text = self.xAxisOption_combobox.currentText()
            for key, value in self.combobox_2_data.items():
                if key == selected_text:
                    return value
        return None

    def set_data(self):
        self.update_data()
        self.set_combobox_2_items()
        self.update_plot()

    def getAllHistoryData(self):
        historyData = []
        for aEntity in self.model.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
        return historyData

    def refresh_data(self):
        self.is_refresh = True
        self.update_plot()

    def update_data(self):
        self.dataEntities = self.model.dataRecorder.getStats_ofEntities()
        self.dataSimVariables = self.model.dataRecorder.getStepsData_ofSimVariables()
        self.dataPlayers = self.model.dataRecorder.getStepsData_ofPlayers()
        self.setXValueData(self.dataEntities)

    def setXValueData(self, data):
        optionXScale = self.get_combobox2_selected_key()
        self.xValue = []
        self.rounds = {entry['round'] for entry in data}
        self.phases = {entry['phase'] for entry in data}
        self.nbRounds = max(self.rounds)
        self.nbPhases = len(
            self.model.timeManager.phases) #- 1  # be careful. should be changed wjhen merged with main branch
        self.phaseOfLastRound = max({entry['phase'] for entry in data if entry['round'] == self.nbRounds})

        if optionXScale == '2':
            self.load_cmb_per_rounds_data()
            if self.roundMax != 0:
                self.nbRounds = self.roundMax - self.roundMin
                self.nbRoundsWithLastPhase = self.roundMax - self.roundMin
                aStep = self.roundMin
                self.start_cmb_round.setCurrentText(f"Round {self.roundMin}")
                self.end_cmb_round.setCurrentText(f"Round {self.roundMax}")
                self.rounds = {entry['round'] for entry in data if
                               entry['round'] >= self.roundMin and entry['round'] <= self.roundMax}
                for aR in range(self.roundMin, self.roundMax):
                    self.xValue.extend(range(aStep := aR * self.nbPhases + self.roundMin, aStep + self.nbPhases))
                if self.phaseOfLastRound != self.nbPhases:
                    self.xValue.extend(range(aStep + 1, aStep + self.phaseOfLastRound + 1))

        if optionXScale == '3':
            self.nbRoundsWithLastPhase = self.nbRounds if self.phaseOfLastRound == self.nbPhases else self.nbRounds - 1
            self.xValue = [0] + [i for i in range(1, self.nbRoundsWithLastPhase * self.nbPhases + 1)]
            if self.phaseOfLastRound != self.nbPhases:
                self.xValue += [self.xValue[-1] + i for i in range(1, self.phaseOfLastRound + 1)]

        if optionXScale in ('0','2') or (optionXScale == '3' and self.nbPhases == 1) or optionXScale=='specified phase':
            self.xValue = list(self.rounds) if self.phaseOfLastRound == self.nbPhases else list(self.rounds)[:-1]
            self.nbRoundsWithLastPhase = self.nbRounds if self.phaseOfLastRound == self.nbPhases else self.nbRounds - 1

