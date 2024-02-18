import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget, QAction, QMenu, QPushButton, \
    QCheckBox
from PyQt5.QtCore import pyqtSignal


class SGToolBarTest(NavigationToolbar):
    def __init__(self, canvas, parent, model, typeDiagram):
        super().__init__(canvas, parent)

        self.typeDiagram = typeDiagram
        # self.data_1_combobox = QComboBox(parent)
        # self.data_1_combobox.currentIndexChanged.connect(self.update_plot)

        # self.setIconSize(10)
        """aAction = QAction(QIcon("./icon/actualiser.png"), "&Actualiser", self)
        aAction.triggered.connect(self.update_plot)
        self.addAction(aAction)"""

        button = QPushButton("Actualiser", self)
        button.setIcon(QIcon("./icon/actualiser.png"))
        button.clicked.connect(self.update_plot)
        # button.move(50, 50)
        self.addWidget(button)

        self.option_affichage_data = {"entityName": "Entités", "simVariable": "Simulation variables",
                                      "currentPlayer": "Players"}
        self.checKbox_menu = {}
        # self.checKbox_menu_data = ["type", "Attribut", "Mean", "Min", "Max", "St Dev"]
        self.checKbox_menu_data = {'Nombres / Populations': 'nbre', 'Moyenne': 'mean', 'Minimum': 'min',
                                   'Maximum': 'max', 'St Dev': 'stdev'}

        # self.menuBar().addAction(aAction)

        # self.addWidget(self.data_1_combobox)

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
        self.list_options = []
        self.list_indicators = []
        self.combobox_1_data = {"Entités": "entityName", "Type d'entités": "entityDef", "Player": "currentPlayer"}
        self.combobox_2_data = {'Tous les tours': '0', 'Dernieres Tours': '1', 'Autres': '2'}
        self.checKbox_indicators_data = ["type", "Attribut", "Mean", "Min", "Max", "St Dev"]
        self.checKbox_indicators = {}

        self.listAttributs = []
        self.listEntities = []
        self.rounds = []
        self.phases = []
        self.axhlines = []
        self.linestyles = ['-', '--', '-.', ':']
        self.colors = ['gray', 'g', 'b']
        self.xValue = []
        # self.menu = QMenu("Affichage", self)
        self.display_menu = QMenu("Affichage", self)
        self.dictMenuData = {'entities': {}, 'simvariables': {}, 'players': {}}
        self.dictListDataToDisplay = {}
        self.checkbox_display_menu_data = {}
        self.checkbox_main_menu_data = {}
        # self._navigation_toolbar = self.parent().addToolBar('Navigation')

        self.createDisplayMenu()

    def createMenu(self, menu, items):
        for item in items:
            if isinstance(item, dict):  # If it's a dictionary, it has submenu
                for sub_key, sub_value in item.items():
                    submenu = menu.addMenu(sub_key)
                    self.createMenu(submenu, sub_value)
            else:
                action = QAction(item, self)
                menu.addAction(action)

    def createDisplayMenu(self):
        # Création des données
        data = {
            'Entities': {
                'Cells': {
                    'Types': ['Type 1', 'Type 2'],
                    'Numbers': {'Type 1': 10, 'Type 2': 15},
                    'Energy': {'mean': 20, 'min': 10, 'max': 30, 'st_dev': 5},
                    'Population': {'mean': 50, 'min': 30, 'max': 70, 'st_dev': 10}
                },
                'Sheeps': {
                    'Types': ['Type A', 'Type B'],
                    'Numbers': {'Type A': 8, 'Type B': 12},
                    'Energy': {'mean': 25, 'min': 15, 'max': 35, 'st_dev': 6},
                    'Population': {'mean': 60, 'min': 40, 'max': 80, 'st_dev': 12}
                }
            },
            'Simulation variables': {
                'Simvariable 1': 100,
                'Simvariable 2': 200
            },
            'Players': {
                'Player 1': None,
                'Player 2': None
            }
        }

        # Création du menu principal
        # menubar = self.menuBar()
        # viewMenu = self.display_menu.addMenu('Affichage')

        # Création des sous-menus
        entitiesMenu = QMenu('Entités', self)
        simulationMenu = QMenu('Simulation variables', self)
        playersMenu = QMenu('Players', self)

        # Ajout des sous-menus au menu principal
        # self.display_menu.addMenu(entitiesMenu)
        # self.display_menu.addMenu(simulationMenu)
        # self.display_menu.addMenu(playersMenu)

        # Ajout des actions pour chaque sous-menu
        # self.addSubMenus(entitiesMenu, data['Entities'])
        # self.addSubMenus(simulationMenu, data['Simulation variables'])
        # self.addSubMenus(playersMenu, data['Players'])

        """    self.display_indicators_menu.addAction(action)
            self.checKbox_indicators[option] = action"""
        # self.addAction(self.display_menu.menuAction())

        # tmp_data = self.getAllData()
        self.regenerate_menu()
        # print("tmp : ", tmp_data[0].keys())
        """
        {'id': 1, 'currentPlayer': 'Admin', 'entityDef': 'Cell', 'entityName': 'Cell', 'simVariable': {'name': 'Score', 'value': 1}, 'round': 1, 'phase': 1,
         'attribut': {'production system': 'not constant', 'energy': 0}}
        """

    def regenerate_menu(self):
        # attrib_data = {'populations': None, 'mean': None, 'min': None, 'max': None, 'stdev': None}
        attrib_data = ['populations', 'mean', 'min', 'max', 'stdev']

        # dict_keys(['id', 'currentPlayer', 'entityDef', 'entityName', 'simVariable', 'round', 'phase', 'attribut'])
        data = self.getAllData()

        players_list = list(set(player['currentPlayer'] for player in data if
                                'currentPlayer' in player and not isinstance(player['currentPlayer'], dict)))
        entities_list = list(set(entry['entityName'] for entry in data if
                                 'entityName' in entry and not isinstance(entry['entityName'], dict)))
        simVariables_list = list(set(
            attribut for entry in data for attribut in entry['simVariable'].keys()))

        for player in players_list:
            # self.dictMenuData['players'][player] = player
            self.dictMenuData['players'][f"currentPlayer-:{player}"] = player

        for key in simVariables_list:
            list_data = list(set(entry['simVariable'][key] for entry in data if isinstance(entry['simVariable'], dict)))
            self.dictMenuData['simvariables'][f"simVariable-:{key}"] = list_data
            # self.dictMenuData['simvariables'][key] = list_data

        for entity_name in entities_list:
            attrib_data_key_test = {}

            attrib_list = list(set(
                attribut for entry in data for attribut in entry['attribut'].keys() if
                entry['entityName'] == entity_name))
            # print("attrib_list : {}".format(attrib_list))
            attrib_dict = {}
            for attribut_key in attrib_list:

                # attrib_dict[attribut] = attrib_data
                # print("attrib_dict : {}".format(attrib_dict))
                for attrib_option_key in attrib_data:
                    # attrib_data = {'populations': None, 'mean': None, 'min': None, 'max': None, 'stdev': None}
                    # print("entityname : {} , attribut key : {} , attr_k value : {} ".format(entity_name, attribut_key, attrib_option_key))
                    option_key = f"entity-:{entity_name}-:{attribut_key}-:{attrib_option_key}"
                    attrib_data_key_test[option_key] = attrib_dict.get(attrib_option_key)
                attrib_dict[attribut_key] = attrib_data_key_test
                # attrib_data_test.append(option_key)
                # attrib_data_test[option_key]
                # print("entityname : {} , attribut key : {} , attrib_data value : {} ".format(attr_key, attribut, attrib_data))
                """population = list(set(
                    entry['attribut'][attribut] for entry in data for attribut in entry['attribut'].keys() if
                    entry['entityName'] == attr_key and entry['attribut'] == attribut ))"""
                # print("data 0 : ", data[0])
                # attr_val = 'production system'
                # print("data 0 : ", data[0]['attribut'][attr_val])
                # print("population : ", population)
                """players_list = list(set(player['currentPlayer'] for player in data if
                                        'currentPlayer' in player and not isinstance(player['currentPlayer'], dict)))"""

                # attrib_data = {'populations': None, 'mean': None, 'min': None, 'max': None, 'stdev': None}
                #
                # print(" attr_key : {} , attribut : {} ".format(attr_key , attribut))
            # print("=" * 10 + " Clés avec des valeurs None " + "=" * 10)
            # print({k: v for k, v in attrib_data_key_test.items() if v is None})
            self.dictMenuData['entities'][entity_name] = attrib_dict

        entitiesMenu = QMenu('Entités', self)
        simulationMenu = QMenu('Simulation variables', self)
        playersMenu = QMenu('Players', self)

        # Ajout des sous-menus au menu principal
        self.display_menu.addMenu(entitiesMenu)
        self.display_menu.addMenu(simulationMenu)
        self.display_menu.addMenu(playersMenu)

        self.addSubMenus(entitiesMenu, self.dictMenuData['entities'])
        self.addSubMenus(simulationMenu, self.dictMenuData['simvariables'])
        self.addSubMenus(playersMenu, self.dictMenuData['players'])
        self.addAction(self.display_menu.menuAction())

        # self.addSubMenus(entitiesMenu, self.dictMenuData['entities'], parentMenuTitle='entities')
        # self.addSubMenus(simulationMenu, self.dictMenuData['simvariables'], parentMenuTitle='simvariables')
        # self.addSubMenus(playersMenu, self.dictMenuData['players'], parentMenuTitle='players')
        # self.addAction(self.display_menu.menuAction())

        # name
        print("players_list : ", players_list)
        print("entities_list : ", entities_list)
        print("simVariables_list : ", simVariables_list)
        # print("dictMenuData : ", self.dictMenuData)

    """
    def addSubMenus(self, parentMenu, subMenuData, parentMenuTitle=''):
        #parentMenuTitle = parentMenu.title().title() if parentMenuTitle else None
        list_value = []
        #print("parentMenu :: ", parentMenu.title().title() )
        if not parentMenuTitle and parentMenu and parentMenu.title():
            parentMenuTitle = parentMenu.title()
            print("type parentMenu.title() : ", type(parentMenu.title()))
        else:
            parentMenuTitle = None
        for key, value in subMenuData.items():
            if isinstance(value, dict):
                submenu = QMenu(key, self)
                #submenu = parentMenu.addMenu(key)
                list_value = list(set(f"{parentMenuTitle}-{key}-{k}" for k in value.keys() if f"{parentMenuTitle}-{key}-{k}" not in list_value and parentMenuTitle and key and k))

                #self.checkbox_main_menu_data = value
                #submenu = QMenu(key, self)
                #parentMenu.addMenu(submenu)
                #self.addSubMenus(submenu, value)

                #for k in value.keys():
                #    print("k : {}, key : {}, value keys: {}, parentMenuTitle : {}".format(k, key, value.keys(), parentMenuTitle))
                #    if not isinstance(k, dict) and k is None:
                #        #print("k keys : ", k)
                #        #self.checkbox_display_menu_data[parentMainMenu_title][key] = action
                #        print("k : {} , key : {}, value : {}, parentMenuTitle : {}".format(k, key, value, parentMenuTitle))
                #print("key : {}, value : {}, parentMenuTitle : {}".format(key, value, parentMenuTitle))
                parentMenu.addMenu(submenu)
                self.addSubMenus(submenu, value, parentMenuTitle=parentMenuTitle)
            else:
                action = QAction(str(key).capitalize(), self, checkable=True)
                action.setChecked(True)
                action.triggered.connect(lambda checked, k=key, pm_title=parentMenuTitle, sm_data=subMenuData: self.on_change_and_update_plot_test(k, pm_title, sm_data))
                print("key : {}, value : {}, parentMenuTitle : {}".format(key, value, parentMenuTitle))

                if parentMenuTitle:

                    #print("parentMenuTitle : ", parentMenuTitle)
                    if parentMenuTitle not in self.checkbox_display_menu_data:
                        self.checkbox_display_menu_data[parentMenuTitle] = {}
                    self.checkbox_display_menu_data[parentMenuTitle][key] = action
                else:
                    self.checkbox_display_menu_data[key] = action
                parentMenu.addAction(action)
                #print("key : {} , value : {}".format(key, value))
        #print("list_value : {}".format(list_value))
        if list_value and len(list_value)>0:
            #self.checkbox_display_menu_data.setdefault(list_value, [])
            print("list_value :: ", list_value)"""

    def addSubMenus(self, parentMenu, subMenuData):
        parentMenu_title = parentMenu.title().title() if parentMenu.title() and parentMenu.title().title() else None
        parentMainMenu_title = ''
        for key, value in subMenuData.items():
            if isinstance(value, dict):
                # print("value : ", value)
                self.checkbox_main_menu_data = value
                submenu = QMenu(key, self)
                parentMenu.addMenu(submenu)
                self.addSubMenus(submenu, value)
            else:
                # self.checkbox_main_menu_data = subMenuData
                # parentMainMenu_title = parentMenu.parent().objectName().title()

                action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize(), self,
                                 checkable=True)

                # action = QAction(str(key).capitalize(), self, checkable=True)
                action.setChecked(True)
                action.setProperty("key", key)
                action.triggered.connect(self.on_change_and_update_plot_test)

                if parentMainMenu_title:
                    self.checkbox_display_menu_data[parentMainMenu_title][key] = action
                else:
                    self.checkbox_display_menu_data[key] = action
                parentMenu.addAction(action)

    def generate_menu(self, data, parent=None):
        for key, value in data.items():
            if isinstance(value, dict):
                submenu = QAction(key, parent)
                self.generate_menu(value, submenu)
            else:
                action = QAction(str(key).capitalize(), self, checkable=True)
                action.setChecked(True)
                # print("Action key :", key)
                # action.setProperty("value", value)
                action.triggered.connect(
                    lambda: self.on_change_and_update_plot_test(str(value), parent))

                # checkbox = QCheckBox(str(value), parent)
                # Faire quelque chose avec le checkbox, comme l'ajouter à une interface utilisateur

    def get_checkbox_display_menu_selected(self):
        # print("\n self.checkbox_display_menu_data.items() : ", self.checkbox_display_menu_data.items())
        selected_option = [option for option, checkbox in self.checkbox_display_menu_data.items() if
                           checkbox.isChecked()]
        return selected_option

    def on_change_and_update_plot_test(self):
        self.update_plot_test()
        # print("Sub Menu Data:", subMenuData)
        # print("self.get_checkbox_display_menu_selected : {} ".format(self.get_checkbox_display_menu_selected()))

    ########

    def update_plot_test(self):
        self.update_data()
        value_cmb_2 = self.get_combobox2_selected_key()
        value_cmb_1 = self.get_combobox1_selected_key()
        if value_cmb_1 is not None and value_cmb_2 is not None:
            index = self.data_1_combobox.currentIndex()
            if self.typeDiagram == 'plot':
                self.plot_linear_typeDiagram(key=value_cmb_1, index=index, option_test=value_cmb_2, isHidden=False)

    def plot_linear_typeDiagram(self, key, index, option_test, isHidden):
        self.ax.clear()
        selected_option_list = self.get_checkbox_display_menu_selected()
        # print("selected_option :: ", len(selected_option))
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        value_cmb_2 = self.get_combobox2_selected_key()
        data = self.getAllData()
        pos = 0
        # print("data 1 : ", data[1])
        for options in selected_option_list:
            print("option : ", options)
            # action = QAction(str(key.split("-:")[-1]).capitalize() if "-:" in key else str(key).capitalize(), self, checkable=True)

            if "-:" in options:
                list_option = options.split("-:")
                variable = list_option[0]
                if variable == 'entity':
                    print(list_option[1:])
                    # list_option[-1]
                    self.test_plot_data_typeDiagram_plot_test_entities(data, list_option, pos)
                elif variable == 'simVariable':
                    # print("simVariable")
                    self.test_plot_data_typeDiagram_plot_simVariables(data, list_option, pos)
                elif variable == 'currentPlayer':
                    # print("currentPlayer")
                    self.test_plot_data_typeDiagram_plot_players(data, list_option, pos)
                else:
                    print("other")
            pos += 1

    # entities[0] = entity
    # entities[1] = entityName
    # entities[2] = attribut
    def test_plot_data_typeDiagram_plot_test_entities(self, data, list_option, pos):
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
                self.ax.plot(self.xValue, y, label=label, linestyle=linestyle, color=color)
            else:
                statistics = {'mean': np.mean(y), 'max': np.max(y), 'min': np.min(y), 'stdev': np.std(y)}
                linestyle_map = {'mean': ':', 'max': 'dotted', 'min': 'dashdot', 'stdev': '--'}
                color_map = {'mean': 'blue', 'max': 'green', 'min': 'black', 'stdev': 'red'}
                line_style = linestyle_map.get(str(list_option[-1]).lower(), ':')
                line_color = color_map.get(str(list_option[-1]).lower(), 'blue')
                self.ax.axhline(statistics.get(str(list_option[-1]).lower(), np.mean(y)), linestyle=line_style,
                                color=line_color, label=label)
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def test_plot_data_typeDiagram_plot_simVariables(self, data, list_option, pos):
        if list_option[:1] == ['simVariable']:
            entities = list_option
            label = f"Simulation Variable : {entities[-1].upper()}"
            y = [sum(1 for entry in data if entry['round'] == r \
                     and entry['phase'] == p and 'simVariable' in entry and
                     entry['simVariable'] == list_option[-1])
                 for r in self.rounds for p in self.phases]
            linestyle = self.linestyles[pos % len(self.linestyles)]
            color = self.colors[pos % len(self.colors)]
            self.ax.plot(self.xValue, y, label=label, linestyle=linestyle, color=color)
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def test_plot_data_typeDiagram_plot_players(self, data, list_option, pos):
        if list_option[:1] == ['currentPlayer']:
            entities = list_option
            label = f"Player : {entities[-1].upper()}"
            y = [sum(1 for entry in data if entry['round'] == r \
                     and entry['phase'] == p and 'currentPlayer' in entry and
                     entry['currentPlayer'] == list_option[-1])
                 for r in self.rounds for p in self.phases]
            linestyle = self.linestyles[pos % len(self.linestyles)]
            color = self.colors[pos % len(self.colors)]
            self.ax.plot(self.xValue, y, label=label, linestyle=linestyle, color=color)
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def create_checkbox_menu(self, data):
        self.checkbox_menu = {}
        subMainMenu = QMenu(self)
        for entity_name in self.listEntities:
            entity_submenu = self.checkbox_menu.setdefault(entity_name, {})
            attributs_list = list(set(
                attribut for entry in data for attribut in entry['attribut'].keys() if
                entry['entityName'] == entity_name))
            entity_submenu['attribut'] = attributs_list
            # print(" checkbox_menu - : {}".format(self.checkbox_menu))

        for key, value in self.checkbox_menu.items():
            action = QAction(key, self, checkable=True)
            if isinstance(value, dict) and 'attribut' in value and isinstance(value['attribut'], list) and len(
                    value['attribut']) == 0:
                action.setChecked(True)
            action.triggered.connect(self.update_plot)
            # self.display_menu.addAction(action)
            subMainMenu.addAction(action)
            self.checkbox_menu[key] = action

            if value['attribut']:
                menu = QMenu(self)
                for attr in value['attribut']:
                    menu2 = QMenu(attr, self)
                    for option in self.checKbox_menu_data:
                        # print("option : ", option)
                        action = QAction(option, menu2, checkable=True)
                        action.setChecked(True)
                        action.triggered.connect(self.update_plot)
                        menu2.addAction(action)
                    menu.addMenu(menu2)
                self.checkbox_menu[key].setMenu(menu)
        # self.addAction(self.display_menu.menuAction())
        self.display_menu.addAction(subMainMenu.menuAction())

        tmp_menu = self.display_menu
        # self.display_menu = QMenu('Affichage', self)
        menu = QMenu("Entités", self)
        menu.addMenu(subMainMenu)
        self.display_menu.addMenu(subMainMenu)

        """for key, value in self.option_affichage_data.items():
            menu = QMenu(value, self)
            #print("key : {} , value : {}".format(key, value))
            if key == 'entityName':
                menu.setTitle(value)
                menu.addMenu(tmp_menu)
                #print(" value - : {}".format(value))
            else:
                action = QAction(value, self)
                action.triggered.connect(self.update_plot)
                menu.addAction(action)
                #print(" value - : {}".format(value))
            print(" menu title - : {}".format(menu.title()))
            self.display_menu.addMenu(menu)"""

        # list_data = set(d for entry in data for d in entry[key] if key in entry)
        # dict_data = {entry[key]: entry for entry in data if isinstance(entry[key], dict)}
        # dict_data = {entry[key]: entry for entry in data if isinstance(entry[key], (dict, str))}

        # self.display_menu.addMenu(menu)
        # print(" self.display_menu - : {}".format(self.display_menu.children()))
        return self.checkbox_menu

    def set_checkboxMenu_values(self, data):
        self.checKbox_menu = {}
        # self.create_checkbox_menu(data)
        # self.create_display_all_options()
        print("checKbox_menu :: ", self.checKbox_menu)
        """if self.typeDiagram in ['pie', 'hist', 'stackplot']:
            self.checKbox_menu_data = ["type", "Attribut"]"""
        # self.checKbox_menu_data = ["type", "Attribut", "Mean", "Min", "Max", "St Dev"]

        ['']

        # print("attribut :: ", self.listAttributs)
        # print("listEntities :: ", self.listEntities)
        # data = self.getAllHistoryData()
        """ print("#######################################")
        for entity in self.listEntities:
            print("entity : ", entity)
            attribut_ent = list(set(attribut for entry in data for attribut in entry['attribut'].keys() if entry['entityName'] == entity ))
            for attribut in attribut_ent:
                print(" - : {} attribut : {}".format(entity, attribut))
        print("#######################################")"""

        """for option in self.checKbox_menu_data:
            action = QAction(option, self, checkable=True)
            action.setChecked(True)
            action.triggered.connect(self.update_plot)
            self.display_menu.addAction(action)
            self.checKbox_menu[option] = action
        self.addAction(self.display_menu.menuAction())
        self.addSeparator()"""

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

    def set_data(self):
        self.update_data()
        data = self.getAllData()
        self.set_checkboxMenu_values(data)
        self.set_combobox_1_items()
        self.set_combobox_2_items()
        self.set_checkbox_values()

    def update_plot(self):
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
                                                     isHidden=False)

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
        source_data = self.getAllData()
        self.setXValueData()
        self.setYValueData(source_data)

    def setXValueData(self):
        option = self.get_combobox2_selected_key()
        data = self.getAllData()
        rounds = {entry['round'] for entry in data}
        phases = {entry['phase'] for entry in data}
        if option == '1':
            max_round = max(rounds)
            self.rounds = [max_round]
            self.phases = {entry['phase'] for entry in data if entry['phase'] == max_round}
            self.xValue = self.rounds if len(self.phases) <= 2 else [phase for phase in self.phases]
        else:
            self.rounds = rounds
            self.phases = phases
            self.xValue = list(rounds) if len(phases) <= 2 else [r * len(phases) + phase for r in rounds for
                                                                 phase in phases]

    def setYValueData(self, data):
        self.listAttributs = list(set(attribut for entry in data for attribut in entry['attribut'].keys()))
        selected_key = self.get_combobox1_selected_key()
        value_cmb_1 = selected_key if selected_key else 'entityName'
        self.listEntities = list(sorted(
            set(entry[value_cmb_1] for entry in data if value_cmb_1 in entry and entry[value_cmb_1] is not None)))

    def plot_data_typeDiagram_stackplot(self, key, index, option, isHidden):
        self.ax.clear()
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        value_cmb_1 = self.get_combobox1_selected_key()
        data = self.getAllData()

        list_data = []
        list_labels = []

        for pos, val in enumerate(self.listEntities):
            y = [sum(1 for entry in data if
                     entry['round'] == r and entry['phase'] == p and entry[key] == str(val).capitalize())
                 for r in self.rounds for p in self.phases]
            list_labels.append(str(val).capitalize())
            list_data.append(y)

            for ind in value_checkbox_3:
                if ind == 'type' and value_cmb_1 != 'currentPlayer':
                    typeDef = str(val).capitalize()
                    if str(val).capitalize() != 'Cell':
                        typeDef = 'Agent'
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and entry['entityDef'] == str(
                                 val).capitalize())
                         for r in self.rounds for p in self.phases]
                    list_data.append(y)
                    list_labels.append(f"Type : {str(typeDef).upper()}")
                elif ind == 'Attribut' and value_cmb_1 != 'currentPlayer':
                    for attr_key in self.listAttributs:
                        y = [sum(1 for entry in data if
                                 entry['round'] == r and entry['phase'] == p and attr_key in entry['attribut'])
                             for r in self.rounds for p in self.phases]
                        list_data.append(y)
                        list_labels.append("Attribut : {} - {}".format(attr_key, str(val).upper()))

        self.ax.cla()
        self.ax.stackplot(range(len(list_data[0])), *list_data, labels=list_labels)
        self.ax.set_title('Stack Plot')
        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_data_typeDiagram_hist(self, key, index, option, isHidden):
        self.ax.clear()
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        data = self.getAllData()
        value_cmb_1 = self.get_combobox1_selected_key()

        list_data = []
        list_labels = []
        for pos, val in enumerate(self.listEntities):
            y = [sum(1 for entry in data if
                     entry['round'] == r and entry['phase'] == p and entry[key] == str(val).capitalize())
                 for r in self.rounds for p in self.phases]
            list_labels.append(str(val).capitalize())
            list_data.append(y)

            for ind in value_checkbox_3:
                if ind == 'type' and value_cmb_1 != 'currentPlayer':
                    typeDef = str(val).capitalize()
                    if str(val).capitalize() != 'Cell':
                        typeDef = 'Agent'
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and entry['entityDef'] == str(
                                 val).capitalize())
                         for r in self.rounds for p in self.phases]
                    list_data.append(y)
                    list_labels.append(f"Type : {str(typeDef).upper()}")
                elif ind == 'Attribut' and value_cmb_1 != 'currentPlayer':
                    for attr_key in self.listAttributs:
                        y = [sum(1 for entry in data if
                                 entry['round'] == r and entry['phase'] == p and attr_key in entry['attribut'])
                             for r in self.rounds for p in self.phases]
                        list_data.append(y)
                        list_labels.append("Attribut : {} - {}".format(attr_key, str(val).upper()))

        self.ax.cla()
        for i in range(len(list_data)):
            print("data{} = {} , label = {} ".format(i, list_data[i], list_labels[i]))
            self.ax.hist(list_data[i], bins=len(list_data), alpha=0.5, label=list_labels[i])

        self.ax.set_title('Histogram')

        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_data_typeDiagram_pie(self, key, index, option, isHidden):
        self.ax.clear()
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        data = self.getAllData()
        value_cmb_1 = self.get_combobox1_selected_key()
        list_data = []
        list_labels = []
        for pos, val in enumerate(self.listEntities):
            y = [sum(1 for entry in data if
                     entry['round'] == r and entry['phase'] == p and entry[key] == str(val).capitalize())
                 for r in self.rounds for p in self.phases]
            list_labels.append(str(val).capitalize())
            list_data.append(sum(y))

            for ind in value_checkbox_3:
                if ind == 'type' and value_cmb_1 != 'currentPlayer':
                    typeDef = str(val).capitalize()
                    if str(val).capitalize() != 'Cell':
                        typeDef = 'Agent'
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and entry['entityDef'] == str(
                                 val).capitalize())
                         for r in self.rounds for p in self.phases]
                    list_data.append(sum(y))
                    list_labels.append(f"Type : {str(typeDef).upper()}")

                elif ind == 'Attribut' and value_cmb_1 != 'currentPlayer':
                    for attr_key in self.listAttributs:
                        y = [sum(1 for entry in data if
                                 entry['round'] == r and entry['phase'] == p and attr_key in entry['attribut'])
                             for r in self.rounds for p in self.phases]
                        list_data.append(sum(y))
                        list_labels.append("Attribut : {} - {}".format(attr_key, str(val).upper()))

        self.ax.pie(list_data, labels=list_labels, autopct='%1.1f%%', startangle=90)
        self.ax.axis('equal')

        self.ax.legend()
        self.ax.set_title(self.title)
        self.canvas.draw()

    def plot_data_typeDiagram_plot(self, key, index, option, isHidden):
        self.ax.clear()
        value_checkbox_3 = self.get_checkbox_indicators_selected()
        value_cmb_2 = self.get_combobox2_selected_key()
        data = self.getAllData()

        for pos, val in enumerate(self.listEntities):

            y = [sum(1 for entry in data if
                     entry['round'] == r and entry['phase'] == p and entry[key] == str(val).capitalize())
                 for r in self.rounds for p in self.phases]

            if value_cmb_2 == 1:
                self.ax.plot(self.xValue, y, marker='o', markersize=8, label=str(val).upper(),
                             linestyle=self.linestyles[pos % len(self.linestyles)],
                             color=self.colors[pos % len(self.colors)])
            else:
                self.ax.plot(self.xValue, y, label=str(val).upper(),
                             linestyle=self.linestyles[pos % len(self.linestyles)],
                             color=self.colors[pos % len(self.colors)])

            for ind in value_checkbox_3:
                if ind == 'type':
                    y = [sum(1 for entry in data if
                             entry['round'] == r and entry['phase'] == p and entry['entityDef'] == str(
                                 val).capitalize())
                         for r in self.rounds for p in self.phases]
                    self.ax.plot(y, linestyle='--', color='orange', label=f"Type : {str(val).upper()}")
                elif ind == 'Attribut':
                    for attr_key in self.listAttributs:
                        y = [sum(1 for entry in data if
                                 entry['round'] == r and entry['phase'] == p and attr_key in entry['attribut'])
                             for r in self.rounds for p in self.phases]
                        self.ax.plot(y, linestyle='--', color='black',
                                     label="Attribut : {} - {}".format(attr_key, str(val).upper()))

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