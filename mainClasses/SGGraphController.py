import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QVBoxLayout, QComboBox, QWidget, QAction, QMenu, \
    QPushButton, \
    QCheckBox, QSpinBox, QLabel, QSlider, QLineEdit, QActionGroup, QInputDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
import re


class SGGraphController(NavigationToolbar):
    def __init__(self, canvas, parent, model, type_of_graph):
        super().__init__(canvas, parent)
        self.parent = parent
        self.type_of_graph = type_of_graph 

        self.is_refresh = False ## l'usage de cette variable est bizarrre. A vérifier
        self.ax = parent.ax
        self.model = model
        self.title = 'SG Graph'

        ## Data import
        # On est obligé de récupérer les data une première fois ici, car elles sont utilisés dans la méthode self.generate_and_add_indicators_menu()
        # a réfléchir si on pourrait pas appeler la méthode generate_and_add_indicators_menu() seulement après l'init du DiagramController
        self.dataEntities = self.model.dataRecorder.getStats_ofEntities()
        self.dataSimVariables = self.model.dataRecorder.getStepsData_ofSimVariables()
        self.dataPlayers = self.model.dataRecorder.getStepsData_ofPlayers()
        self.dataGameActions = self.model.dataRecorder.getStepsData_ofGameActions()


        ## Data vizualisation
        self.linestyle_items = {'mean': 'solid', 'max': 'dashed', 'min': 'dashed','stdev': 'dotted', 'sum': 'dashdot' }
        self.colors = ['gray', 'green', 'blue', 'red', 'black', 'orange', 'purple', 'pink', 'cyan', 'magenta']

        ## Menu indicators
        self.indicators = ['max', 'mean', 'min', 'stdev','sum']
        self.indicators_menu = QMenu("Indicators", self)
        self.dictMenuData = {'entities': {}, 'simVariables': {}, 'players': {}, 'gameActions': {}}
        self.checkbox_indicators_data = {}
        self.parentAttributKey = 'quantiAttributes' if self.type_of_graph in ['linear', 'hist'] else 'qualiAttributes'
        self.groupAction = QActionGroup(self)
        self.firstEntity = ""
        self.firstAttribut = ""
        self.generate_and_add_indicators_menu()

        if self.type_of_graph in ['linear',  'stackplot']:
            # Menu display option for x axis  
            self.combobox_xAxisOption_data = {'Rounds': 'per round','Rounds & Phases': 'per step','Specified phase': 'specified phase'}
            self.specified_phase = 2
            self.xAxisOption_combobox = QComboBox(parent)
            self.addWidget(self.xAxisOption_combobox)

        # self.addSeparator()
        
        # Button refresh
        button = QPushButton("refresh", self)
        button.setIcon(QIcon("./icon/actualiser.png"))
        button.clicked.connect(self.refresh_data)
        self.addWidget(button)

    ##############################################################################################
    # Accessors
    ##############################################################################################

    def allData_with_quant(self):
        return self.dataEntities + self.dataSimVariables + self.dataPlayers + self.dataGameActions

    def allData_with_quali(self):
        return self.dataEntities
    
    ##############################################################################################
    # Methods to set and update the chart
    ##############################################################################################

    def set_data(self):
        ## cette méthode est appellé par le constructreur des classes SGGraphLinear,  SGDiagramStack, SGGraphHistogram,SGGraphCircular
        self.setXValue_basedOnData(self.dataEntities)
        self.set_combobox_xAxisOption()
        self.update_chart(reloadData_before_update=False)


    def update_chart(self,reloadData_before_update=True):
        if reloadData_before_update:
            self.dataEntities = self.model.dataRecorder.getStats_ofEntities()
            self.dataSimVariables = self.model.dataRecorder.getStepsData_ofSimVariables()
            self.dataPlayers = self.model.dataRecorder.getStepsData_ofPlayers()
            self.dataGameActions = self.model.dataRecorder.getStepsData_ofGameActions()

        self.setXValue_basedOnData(self.dataEntities)

        selected_indicators = self.get_checkbox_indicators_selected()
        if self.type_of_graph == 'linear':
            self.plot_linear_typeGraph(self.allData_with_quant(), selected_indicators)
        elif self.type_of_graph == 'hist':
            self.plot_hist_typeGraph(self.dataEntities, selected_indicators)
        elif self.type_of_graph == 'pie':
            self.plot_pie_typeGraph(self.allData_with_quali(), selected_indicators)
        elif self.type_of_graph == 'stackplot':
            self.plot_stackplot_typeGraph(self.allData_with_quali(), selected_indicators)


    def setXValue_basedOnData(self, data):
        optionXScale = self.get_combobox_xAxisOption_selected()
        self.xValue = []
        self.rounds = {entry['round'] for entry in data}
        self.phases = {entry['phase'] for entry in data}
        self.nbRounds = max(self.rounds)
        self.nbPhases = self.model.timeManager.numberOfPhases()
        self.phaseOfLastRound = max({entry['phase'] for entry in data if entry['round'] == self.nbRounds})

        if optionXScale in ['per round','specified phase'] or (optionXScale == 'per step' and self.nbPhases == 1) :
            self.xValue = list(self.rounds) if self.phaseOfLastRound == self.nbPhases else list(self.rounds)[:-1]
            self.nbRoundsWithLastPhase = self.nbRounds if self.phaseOfLastRound == self.nbPhases else self.nbRounds - 1
        elif optionXScale == 'per step': 
            self.nbRoundsWithLastPhase = self.nbRounds if self.phaseOfLastRound == self.nbPhases else self.nbRounds - 1
            self.xValue = [0] + [i for i in range(1, self.nbRoundsWithLastPhase * self.nbPhases + 1)]
            if self.phaseOfLastRound != self.nbPhases:
                self.xValue += [self.xValue[-1] + i for i in range(1, self.phaseOfLastRound + 1)]
        #could add here another case for 'only last rounds' with self.nbOfLastRounds_to_display 
        

    def refresh_data(self):
        self.is_refresh = True
        self.update_chart()


    ##############################################################################################
    # Methods for Indicators menu
    ##############################################################################################

    def generate_and_add_indicators_menu(self):
        """
        Regenerates the indicators menu based on the data that have been loaded by the class.
        This menu allows the user to select different indicators for data visualization.
        Sub-menus are created for entities, players, and simulation variables, each containing specific options.
        """

        if self.type_of_graph == 'linear':
            if self.dataEntities:
                entitiesMenu = QMenu('Entités', self)
                self.indicators_menu.addMenu(entitiesMenu)

                #create menu items for entities
                ##retrieves the list of entities
                entities_list = {entry['entityName'] for entry in self.dataEntities if
                                'entityName' in entry and not isinstance(entry['entityName'], dict)}
                ###Take this opportunity to initialize the first entitiy to be selected in the menu
                if not self.firstEntity:
                    self.firstEntity = sorted(entities_list)[0]
                ##define the list of indicators for entities attributes
                attrib_data = ['mean','sum', 'min','max','stdev']

                ##create the menu items
                for entity_name in sorted(entities_list):
                    attrib_dict = {}
                    attrib_dict[f"entity-:{entity_name}-:population"] = None
                    list_entDef_attribut_key = {x for entry in self.dataEntities for x in entry.get('entDefAttributes', {}) if entry['entityName'] == entity_name}
                    for entDef_attribut_key in sorted(list_entDef_attribut_key):
                        attrib_dict[f"entity-:{entity_name}-:{entDef_attribut_key}"] = None                                              
                    list_attribut_key = {attribut for entry in self.dataEntities for attribut in entry.get(self.parentAttributKey, {}) if
                                        entry['entityName'] == entity_name}
                    if not self.firstAttribut:
                        self.firstAttribut = "population"  # sorted(list_attribut_key)[0]
                    for attribut_key in sorted(list_attribut_key):
                        attrib_dict[attribut_key] = {f"entity-:{entity_name}-:{attribut_key}-:{option_key}": None for
                                                    option_key in attrib_data}
                    self.dictMenuData['entities'][entity_name] = attrib_dict
                self.addSubMenus(entitiesMenu, self.dictMenuData['entities'], self.firstEntity, self.firstAttribut)


            #Create menu for Player Indicator
            if self.dataPlayers: #Only if its not empty
                playersMenu = QMenu('Players', self)
                self.indicators_menu.addMenu(playersMenu)
                #Create menu items for players
                ##get the list of players
                players_list = {entry['playerName'] for entry in  self.dataPlayers if 'playerName' in entry and not isinstance(entry['playerName'], dict)}
                ##create the menu for players
                for player_name in sorted(players_list):
                    attrib_dict = {}
                    list_player_attribut_key = {x for entry in self.dataPlayers for x in entry.get('dictAttributes', {}) if entry['playerName'] == player_name}
                    for player_attribut_key in sorted(list_player_attribut_key):
                        attrib_dict[f"player-:{player_name}-:{player_attribut_key}"] = None                                              
                    self.dictMenuData['players'][player_name] = attrib_dict
                self.addSubMenus(playersMenu, self.dictMenuData['players'], self.firstEntity, self.firstAttribut)


            #Create menu for SimVariables
            if self.dataSimVariables:
                simuVarsMenu = QMenu('Simulation variables', self)
                self.indicators_menu.addMenu(simuVarsMenu)
                #create menu items for simVariables
                simVariables_list = list(set(entry['simVarName'] for entry in self.dataSimVariables))
                for simVar in simVariables_list:
                    self.dictMenuData['simVariables'][f"simVariable-:{simVar}"] = None
                self.addSubMenus(simuVarsMenu, self.dictMenuData['simVariables'], self.firstEntity, self.firstAttribut)

            #Create menu for Game Actions
            if self.dataGameActions:
                gameActionsMenu = QMenu('Game actions', self)
                self.indicators_menu.addMenu(gameActionsMenu)
                #create menu items for simVariables
                # print(self.dataGameActions)
                gameActions_list = list(set((action['action_type']) 
                                          for entry in self.dataGameActions 
                                          for action in entry['actions_performed']))
                # print(self.dictMenuData)
                # Créer une liste plate des combinaisons action_type + target_entity
                for action_type in gameActions_list:
                    menu_label = f"{action_type}"
                    self.dictMenuData['gameActions'][f"gameActions-:{menu_label}"] = None
                self.addSubMenus(gameActionsMenu, self.dictMenuData['gameActions'], self.firstEntity, self.firstAttribut)


        elif self.type_of_graph in ['hist', 'pie', 'stackplot']:
            entitiesMenu = QMenu('Entités', self)
            self.indicators_menu.addMenu(entitiesMenu)

            #create menu items for entities
            ##retrieves the list of entities
            entities_list = {entry['entityName'] for entry in self.dataEntities if
                             'entityName' in entry and isinstance(entry[self.parentAttributKey], dict)
                             and entry[self.parentAttributKey].keys() and not isinstance(entry['entityName'], dict) #pourquoi cettte denière condition ?
                             }
            ##Take this opportunity to initialize the first entitiy to be selected in the menu
            if not self.firstEntity:
                self.firstEntity = sorted(entities_list)[0] if len(entities_list)>0 else ''

            for entity_name in sorted(entities_list):
                attrib_dict = {}
                list_attribut_key = {attribut for entry in self.dataEntities for attribut in entry.get(self.parentAttributKey, {}) if
                                     entry.get('entityName') == entity_name and isinstance(
                                         entry[self.parentAttributKey][attribut], dict)}

                if not self.firstAttribut:
                    self.firstAttribut = sorted(list_attribut_key)[0] if len(list_attribut_key) > 0 else ''

                ##create the menu items
                for attribut_key in list_attribut_key:
                    list_val = []
                    attrib_tmp_dict = {}
                    attrib_dict[f"entity-:{entity_name}-:{attribut_key}"] = None
                    
                self.dictMenuData['entities'][entity_name] = attrib_dict
            self.addSubMenus(entitiesMenu, self.dictMenuData['entities'], self.firstEntity, self.firstAttribut)
        self.addAction(self.indicators_menu.menuAction())


    def addSubMenus(self, parentMenu, subMenuData, firstEntity, firstAttribut):
        for key, value in subMenuData.items():
            if isinstance(value, dict):
                submenu = QMenu(key, self)
                parentMenu.addMenu(submenu)
                self.addSubMenus(submenu, value, firstEntity, firstAttribut)
            else:
                if self.type_of_graph in ['hist', 'pie', 'stackplot']:
                    action = self.create_indicatorRadioMenuItem(key, parentMenu)
                    if key == f"entity-:{firstEntity}-:{firstAttribut}":
                        action.setChecked(True)
                else:
                    action = self.create_indicatorCheckboxMenuItem(key, parentMenu)
                    if firstEntity in key.split("-:") and firstAttribut in key.split("-:"):
                        action.setChecked(True)
                self.checkbox_indicators_data[key] = action
                parentMenu.addAction(action)

    
    def create_indicatorCheckboxMenuItem(self, key, parentMenu):
        # for type_of_graph : (linear)
        # action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize(), parentMenu, checkable=True)
        action = QAction(str(key.split("-:")[-1]) if "-:" in key else str(key), parentMenu, checkable=True)
        action.setProperty("key", key)
        action.triggered.connect(self.on_indicatorCheckboxMenu_triggered)
        parentMenu.addAction(action)
        return action

    def create_indicatorRadioMenuItem(self, key, parentMenu):
        # for type_of_graph : (pie, stackplot, hist)
        # action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize())
        action = QAction(str(key.split("-:")[-1]) if "-:" in key else str(key))
        action.setCheckable(True)
        parentMenu.addAction(action)
        self.groupAction.addAction(action)
        action.triggered.connect(lambda: self.on_indicatoRadioMenuItem_triggered(action))
        return action

    def on_indicatoRadioMenuItem_triggered(self, action):
        # IndicatorRadioMenu is used only for hist, pie, stackplot
        # Deselect all other indicators except the one that has been selected in the argument action
        # Then, call the method chart
        for aAction in self.groupAction.actions():
            if aAction != action:
                aAction.setChecked(False)
        self.update_chart()
    
    def on_indicatorCheckboxMenu_triggered(self):
        # update chart after checked option
        self.update_chart()


    def get_checkbox_indicators_selected(self):
        # get indicators selected
        return [option for option, checkbox in self.checkbox_indicators_data.items() if checkbox.isChecked()]


    ##############################################################################################
    # Methods for XAxisOption menu
    ##############################################################################################

    def set_combobox_xAxisOption(self):
        if self.type_of_graph in ['linear', 'stackplot']:
            self.xAxisOption_combobox.clear()
            if self.nbRounds == 1:
                sorted_combobox_data = dict(sorted(self.combobox_xAxisOption_data.items(), key=lambda item: item[1], reverse=True))
                self.combobox_xAxisOption_data = sorted_combobox_data
            for display_text, key in self.combobox_xAxisOption_data.items():
                self.xAxisOption_combobox.addItem(display_text, key)
            self.xAxisOption_combobox.currentIndexChanged.connect(self.on_xAxisOption_combobox_triggered)
    
    def on_xAxisOption_combobox_triggered(self):    
        if self.get_combobox_xAxisOption_selected() == 'specified phase':    
            dialog = QInputDialog(self.parent)
            dialog.setWindowTitle("Select Specified Phase")
            dialog.setLabelText(f"Sélectionnez la phase (1-{self.nbPhases}):")
            dialog.setComboBoxItems([str(i) for i in range(1, self.nbPhases + 1)])
            dialog.setComboBoxEditable(False)
            if dialog.exec_() == QInputDialog.Accepted:
                self.specified_phase = int(dialog.textValue())
        self.update_chart()


    def get_combobox_xAxisOption_selected(self):
        if self.type_of_graph in ['linear', 'stackplot'] and self.xAxisOption_combobox:
            selected_text = self.xAxisOption_combobox.currentText()
            for key, value in self.combobox_xAxisOption_data.items():
                if key == selected_text:
                    return value
        return None

    ##############################################################################################
    # Methods for error message
    ##############################################################################################

    def showErrorMessage(self, titre, message):
        # message d'erreur si aucune données a affiché
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setWindowTitle(titre)
        error_dialog.setText(message)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()


    ##############################################################################################
    # Methods for plotting the different types of chart
    ##############################################################################################
 
    def plot_linear_typeGraph(self, data, selected_indicators ):
        self.ax.clear()
        optionXScale = self.get_combobox_xAxisOption_selected()
        pos = 0

        for aMenuIndicatorSpec in selected_indicators:
            aIndicatorSpec = IndicatorSpec(aMenuIndicatorSpec,isQuantitative=True)
            pos += 1
            if optionXScale == 'per round' or (optionXScale == 'per step' and self.nbPhases == 1) :
                self.process_data_per_round_for_linear_typeDiagram(data, pos, aIndicatorSpec, self.nbPhases)
                self.ax.set_xticks(self.xValue)
                self.ax.set_xlabel('Round')
            elif optionXScale == 'per step' :  
                self.process_data_per_phase_for_linear_typeDiagram(data, pos, aIndicatorSpec)
                self.ax.set_xticks(self.xValue)
                self.ax.set_xlabel('Step')
            elif optionXScale == 'specified phase' :
                self.process_data_per_round_for_linear_typeDiagram(data, pos, aIndicatorSpec,self.specified_phase)
                self.ax.set_xticks(self.xValue)
                self.ax.set_xlabel(f"Phase {self.specified_phase}")
            #could add here another case for 'only last rounds' with self.nbOfLastRounds_to_display 

        self.ax.legend()
        title_entities = ", ".join(set([option.split("-:")[1] for option in selected_indicators if 'entity' in option]))
        title = f"Evolution des populations {title_entities}"
        self.ax.set_title(title)
        self.canvas.draw()


    def plot_hist_typeGraph(self, data, selected_option_list):
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
            h_xValues_ofIntervals = list(h.values())[0][1]
            h_abcis = np.average([h_xValues_ofIntervals[1:], h_xValues_ofIntervals[:-1]], axis=0)
            h_height = list(h.values())[0][0]
            label = str(list(h.keys())[0]) if h.keys() and len(list(h.keys())) > 0 else ''
            # bins = [val - (h_abcis[1] - h_abcis[0]) / 2 for val in h_abcis] + [
            #     h_abcis[-1] + (h_abcis[1] - h_abcis[0]) / 2]
            bins = h_xValues_ofIntervals
            self.ax.hist(h_abcis, weights=h_height, bins=bins, label=label, edgecolor='black')
            self.ax.set_xticks(h_xValues_ofIntervals)

        self.ax.legend()
        self.title = "Analyse de la fréquence des {} des {}".format(attribut_value, " et ".join(entity_name_list))
        self.ax.set_title(self.title)
        self.ax.set_xlabel(attribut_value)
        self.ax.set_ylabel('Nombre d''occurences')
        self.canvas.draw()


    def plot_pie_typeGraph(self, data, selected_option_list):
        if len(selected_option_list) > 0 and "-:" in selected_option_list[0]:
            list_option = selected_option_list[0].split("-:")
            entityName = list_option[1]
            attribut_value = list_option[2]
            self.ax.clear()
            data_pie = next((entry[self.parentAttributKey][attribut_value] for entry in data
                             if entry['round'] == max(self.rounds) and
                             entry['entityName'] == entityName and attribut_value in entry[self.parentAttributKey]), None)
            if data_pie is None:
                return None 
                # raise ValueError('Did not find data for Pie Chart')  
            labels = list(data_pie.keys())
            values = list(data_pie.values())
            self.title = f"Répartition des {entityName} par {attribut_value} en (%)"
            self.ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax.axis('equal')
            self.ax.legend()
            self.ax.set_title(self.title)
            self.canvas.draw()


    def plot_stackplot_typeGraph(self, data, selected_option_list):
        list_data = []
        formatted_data = {}
        entity_name_list = []
        list_attribut_key = []
        attribut_value = ""
        self.ax.clear()

        data_y = []
        optionXScale = self.get_combobox_xAxisOption_selected()

        for option in selected_option_list:
            if "-:" in option:
                list_opt = option.split("-:")
                entityName = list_opt[1]
                entity_name_list.append(entityName)
                attribut_value = list_opt[-1]
                list_attribut_key.append(attribut_value)

                if optionXScale != 'per step' or (optionXScale == 'per step' and self.nbPhases == 1): # Case --> 'per round' or 'specified phase'
                    if self.nbRounds == 0:
                        nbRounds = self.nbRounds
                        self.xValue = [0,1]
                    else:
                        nbRounds = self.nbRoundsWithLastPhase
                    for r in range(nbRounds + 1):
                        phase_to_display = self.specified_phase if optionXScale == 'specified phase' else self.nbPhases
                        phaseIndex = phase_to_display if r != 0 else 0

                        # code initiale qui bug car parfois l'index [-1] n'existe pas car la liste est vide
                        # aEntry = [entry[self.parentAttributKey][attribut_value] for entry in data if entry['entityName'] == entityName
                        #           and attribut_value in entry[self.parentAttributKey] and
                        #           entry['round'] == r and entry['phase'] == phaseIndex][-1]
                        # list_data.append(aEntry)

                        entries = [entry[self.parentAttributKey][attribut_value] for entry in data 
                                 if entry['entityName'] == entityName
                                 and attribut_value in entry[self.parentAttributKey] 
                                 and entry['round'] == r 
                                 and entry['phase'] == phaseIndex]
                        if entries:  # vérifie si la liste n'est pas vide
                            aEntry = entries[-1]
                            list_data.append(aEntry)
                        else:
                            # list_data.append(0) #todo this issue is not resolved
                            continue  # ou gérer le cas où aucune donnée n'est trouvée

                       

                else:  # Case --> 'per step'
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
            if len(values[0]) != len(self.xValue):
                titre = "Impossible d'afficher les données"
                message = "Aucune données à afficher. veuillez continuer le jeu "
                self.showErrorMessage(titre, message)
                return None
            self.plot_stackplot_data_switch_xvalue(self.xValue, values, labels)
            self.ax.legend()
            # print("labels : ", labels)
            #title = "{} et des Simulations Variables".format(self.title)
            self.title = "Analyse comparative des composantes de la {} ".format(attribut_value.capitalize())
            self.ax.set_title(self.title)
            self.canvas.draw()
        else:
            titre = "Impossible d'afficher les données"
            message = "Aucune données à afficher. veuillez continuer le jeu "
            self.showErrorMessage(titre, message)
            #QApplication.quit()

    def plot_stackplot_data_switch_xvalue(self, xValue, data, label):
        if len(xValue) == 1:
            self.ax.stackplot(xValue * len(data), data, labels=label)
        else:
            self.ax.stackplot(xValue, data, labels=label)
            option = self.get_combobox_xAxisOption_selected()
            if self.nbPhases > 2 and option == 'per step':
                # Display red doted vertical lines to shaw the rounds
                round_lab = 1
                for x_val in xValue:
                    if (x_val -1) % self.nbPhases == 0 and x_val != 1:
                        self.ax.axvline(x_val, color='r', ls=':')
                        # self.ax.text(x_val, 1, f"Round {round_lab}", color='r', ha='center', backgroundcolor='1', va='top', rotation=90, transform=self.ax.get_xaxis_transform())                        
                        self.ax.text(x_val, 1, f"Round {round_lab}", color='r', ha='left', va='top', rotation=90, transform=self.ax.get_xaxis_transform())                        
                        round_lab += 1


    def process_data_per_round_for_linear_typeDiagram(self, data, pos, aIndicatorSpec, phase_to_display):
        data_y = []
        for r in range(self.nbRoundsWithLastPhase + 1):
            phaseIndex = phase_to_display if r != 0 else 0
            condition = {'round': r, 'phase': phaseIndex}
            data_y.extend(aIndicatorSpec.get_data([entry for entry in data if all(entry.get(k) == v for k, v in condition.items())]))
        
        if data_y:
            label = aIndicatorSpec.get_label()
            line_style = aIndicatorSpec.get_line_style()
            self.plot_data_switch_xvalue(self.xValue, data_y, label, line_style, pos)


    def process_data_per_phase_for_linear_typeDiagram(self, data, pos, aIndicatorSpec):
        currentDate = self.model.timeManager.currentRoundNumber,self.model.timeManager.currentPhaseNumber     
        data_y = []
        for r in range(self.nbRoundsWithLastPhase +2): # +2 pour prendre en compte le dernier tour ainsi que le tour en cours
            for p in range(self.nbPhases +1): # +1 pour prendre en compte le fait que quand on fait un range il exclu le dernier index
                if (r,p) == currentDate: continue # On saute la date en cours, car les dataEntities n'ont pas les data de la date en cours (seul les data des simVars et des players ont la donnée de la date en cours)
                condition = {'round': r, 'phase': p}
                data_y.extend(aIndicatorSpec.get_data([entry for entry in data if all(entry.get(k) == v for k, v in condition.items())]))
        if data_y:
            label = aIndicatorSpec.get_label()
            line_style = aIndicatorSpec.get_line_style()
            self.plot_data_switch_xvalue(self.xValue, data_y, label, line_style, pos)

    def plot_data_switch_xvalue(self, xValue, data, label, linestyle, pos): #shoudl perhaps be renamed
        color = self.colors[pos % len(self.colors)]
        if len(xValue) == 1:
            self.ax.plot(xValue * len(data), data, label=label, color=color, marker='o', linestyle='None')
        else:
            data = [0 if isinstance(item, list) and len(item) == 0 else item for item in data]
            if len(xValue) > len(data):
                data.extend([0] * (len(xValue) - len(data)))
            self.ax.plot(xValue, data, label=label, linestyle=linestyle, color=color)
            option = self.get_combobox_xAxisOption_selected()
            if self.nbPhases > 2 and option == 'per step':
                # Display red doted vertical lines to shaw the rounds
                round_lab = 1
                for x_val in xValue:
                    if (x_val -1) % self.nbPhases == 0 :
                        self.ax.axvline(x_val, color='r', ls=':')
                        # self.ax.text(x_val, 1, f"Round {round_lab}", color='r', ha='center', backgroundcolor='1',va='top', rotation=90, transform=self.ax.get_xaxis_transform())
                        self.ax.text(x_val, 1, f"Round {round_lab}", color='r', ha='left',va='top', rotation=90, transform=self.ax.get_xaxis_transform())
                        round_lab += 1


    ##############################################################################################
    # Class IndicatorSpec
    ##############################################################################################

class IndicatorSpec:
    def __init__(self, menu_indicator_spec, isQuantitative):
        self.component, self.indicatorType, self.indicator = self.parse_menu_indicator_spec(menu_indicator_spec,isQuantitative)

    def parse_menu_indicator_spec(self, menu_indicator_spec,isQuantitative):
        if "entity" in menu_indicator_spec:
            component = tuple(menu_indicator_spec.split("-:")[:2])
            if "population" in menu_indicator_spec:
                indicatorType = 'population'
                indicator = 'population'
            elif len(menu_indicator_spec.split("-:")) == 3:
                indicatorType = 'entDefAttributes'
                indicator = menu_indicator_spec.split("-:")[-1]
            else:
                indicatorType =  'quantiAttributes' if isQuantitative else 'qualiAttributes'
                indicator = tuple(menu_indicator_spec.split("-:")[-2:])
        elif "simVariable" in menu_indicator_spec:
            component = 'simVariable'
            indicatorType = None
            indicator =  menu_indicator_spec.split("-:")[-1]
        elif "player" in menu_indicator_spec:
            component = tuple(menu_indicator_spec.split("-:")[:2])
            indicatorType = 'dictAttributes'
            indicator = menu_indicator_spec.split("-:")[-1]
        elif "gameActions" in menu_indicator_spec:
            component = 'gameActions'
            indicatorType = 'actions_performed'
            indicator = menu_indicator_spec.split("-:")[-1]
        return component, indicatorType, indicator

    def get_data(self, data_at_a_given_step):
        if self.component[0] == 'entity':
            if self.indicatorType == 'population':
                return [entry['population'] for entry in data_at_a_given_step if 'entityType' in entry and entry['entityName'] == self.component[1]]
            elif self.indicatorType == 'entDefAttributes':
                return [entry[self.indicatorType][self.indicator] for entry in data_at_a_given_step if 'entityType' in entry and entry['entityName'] == self.component[1]]
            elif self.indicatorType == 'quantiAttributes':
                return [entry[self.indicatorType][self.indicator[0]][self.indicator[1]] for entry in data_at_a_given_step if 'entityType' in entry and entry['entityName'] == self.component[1]]
            elif self.indicatorType == 'qualiAttributes':
                return [entry[self.indicatorType][self.indicator[0]][self.indicator[1]] for entry in data_at_a_given_step if 'entityType' in entry and entry['entityName'] == self.component[1]]
        elif self.component == 'simVariable':
            return [entry['value'] for entry in data_at_a_given_step if 'simVarName' in entry and entry['simVarName'] == self.indicator]
        elif self.component[0] == 'player':
            return [entry[self.indicatorType][self.indicator] for entry in data_at_a_given_step if 'playerName' in entry and entry['playerName'] == self.component[1] ]
        elif self.component == 'gameActions':
            return [
                action['usage_count'] 
                for entry in data_at_a_given_step 
                for action in entry.get('actions_performed', [])
                if 'actions_performed' in entry and action['action_type'] == self.indicator
            ]
        else: 
            breakpoint()
            return []

    def get_label(self):
        if self.component[0] == 'entity':
            if self.indicatorType == 'population':
                return self.component[1] + " - " + "Population" 
            elif self.indicatorType == 'entDefAttributes':
                return self.component[1] + " - " + self.indicator
            elif self.indicatorType == 'quantiAttributes':
                return self.component[1] + " - " + self.indicator[1]   +  " of " +  self.indicator[0] 
            elif self.indicatorType == 'qualiAttributes':
                return self.component[1] + " - " + self.indicator[1] + " of " + self.indicator[0]
        elif self.component == 'simVariable':
            return self.indicator
        elif self.component[0] == 'player':
                return self.component[1] + " - " + self.indicator
        elif self.component == 'gameActions':
            return self.indicator
        
    def get_line_style(self):
        if self.indicatorType == 'quantiAttributes':
            return {'mean': 'solid', 'max': 'dashed', 'min': 'dashed','stdev': 'dotted', 'sum': 'dashdot' }[self.indicator[1]]
        else: return 'solid'

