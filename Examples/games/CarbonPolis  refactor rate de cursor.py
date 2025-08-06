import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QPoint
import random

class CarbonPolisGame:
    def __init__(self):
        self.monApp = QtWidgets.QApplication([])
        self.myModel = SGModel(1700, 1020, name="CarbonPolis", typeOfLayout="grid", x=7, y=7)
        self.initialize_game()

    def initialize_game(self):
        #********************************************************************
        self.nbJoueurs = 5  # Entre 5 et 8

        # Initialisation des variables manquantes
        self.casesAction1 = []
        self.surfaceCorrespondantAuPotentielAccueilInitial = {}
        self.dictSymbology = {
            "action1": Qt.black,
            "action2": Qt.black,
            "vide": Qt.transparent
        }
        self.pZH = {}  # Initialisation du dictionnaire pZH

        # Def des joueurs
        self.joueurs_potentiels = {
            'J1': Qt.blue,
            'J2': Qt.red,
            'J3': Qt.yellow,
            'J4': Qt.green,
            'J5': Qt.white,
            'J6': Qt.black,    
            'J7': Qt.magenta,  
            'J8': Qt.gray      
        }

        # Créer le dictionnaire joueurs_actifs avec les N (N= nbJoueurs) premiers éléments de joueurs_poentiels
        self.joueurs_actifs = {key: self.joueurs_potentiels[key] for key in list(self.joueurs_potentiels.keys())[:self.nbJoueurs]}
        
        # Définir le coût du bonus aménagé en fonction du nombre de joueurs
        self.coutBonusAmenage = {
            5: 70,
            6: 84,
            7: 98,
            8: 112
        }[self.nbJoueurs]

        # Initialisation des zones et du plateau
        self.initialize_zones()
        
        # Vérification détaillée de self.ZHs
        if not hasattr(self, 'ZHs'):
            raise ValueError("self.ZHs n'a pas été initialisé")
        if not isinstance(self.ZHs, dict):
            raise ValueError("self.ZHs n'est pas un dictionnaire")
        if len(self.ZHs) == 0:
            raise ValueError("self.ZHs est vide")
        
        self.initialize_plateau()
        self.initialize_variables()
        
        # Construction des zones humides
        for typeZH in self.ZHs.keys():
            if typeZH not in ['demi-herbier', 'mer', 'vide', 'pres sales Diop', 'demi-herbier Diop']:
                self.construct_zh(typeZH)
                
        self.initialize_actions()
        self.initialize_dashboards()
        self.initialize_phases()
        self.initialize_buttons()

    def initialize_zones(self):
        # Initialisation de self.ZHs
        self.ZHs = {}
        
        # Définition de l'ordre des zones humides
        self.ordreZHs = ['champs agricoles','marais doux agricole', 'marais doux', 'marais saumatre', 'marais saumatre d''Huyez', 'marais salee', 'oestricole', 'marais salant', 'pres sales', 'vasiere nue', 'herbier', "demi-herbier", 'plage', 'port plaisance', 'port industriel', 'foret', 'vasiere nue Diop', "mer", "vide"]

        # Ajout des zones humides une par une
        self.ZHs['champs agricoles'] = {
            "sequestration": 0,
            "couleur": QColor(255, 0, 0, 120),
            "potentiel accueil actions1": None,
            "cases actions2": [
                {"type_action2": "agri intensive", "effet economie": 3, "effet sequestration": -1},
                {"type_action2": "agri intensive", "effet economie": 3, "effet sequestration": -1},
                {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
                {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
                {"type_action2": "fauchage", "effet economie": 0, "effet sequestration": 0},
                {"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1},
                {"type_action2": "ovin", "effet economie": 2, "effet sequestration": -1},
                {"type_action2": "apiculture", "effet economie": 1, "effet sequestration": 0},
                {"type_action2": "fauchage", "effet economie": 0, "effet sequestration": 0},
                *([{"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1} if self.nbJoueurs >= 6 else None]),
                *([{"type_action2": "ovin", "effet economie": 2, "effet sequestration": -1} if self.nbJoueurs >= 7 else None]),
                *([{"type_action2": "apiculture", "effet economie": 1, "effet sequestration": 0} if self.nbJoueurs >= 8 else None])
            ],
            "cases actions2 en plus": [
                {"type_action2": "agri intensive", "effet economie": 3, "effet sequestration": -1},
                {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
                {"type_action2": "fauchage", "effet economie": 2, "effet sequestration": -1},
                {"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1},
                {"type_action2": "ovin", "effet economie": 2, "effet sequestration": -1}
            ],
            "seuil variation actions2": 14
        }
        
        # Vérification que self.ZHs est correctement initialisé
        if not isinstance(self.ZHs, dict):
            raise ValueError("self.ZHs n'a pas été correctement initialisé")

    def initialize_plateau(self):
        # construction du plateau
        self.cases=self.myModel.newCellsOnGrid(21,21,"square",size=40,gap=0,backGroundImage=QPixmap("./icon/MTZC/plateau-jeu.jpg"))
        # surface  des petites cases sPC ett des grandes cases SGC
        sPC = 2
        sGC = 4
        # codification des occupation du sol
        t0 = "vide"
        tD = "marais doux"
        tDA = "marais doux agricole"
        tSAU = "marais saumatre"
        tSAL = "marais salee"
        tO = "oestricole"
        tPS = "pres sales"
        tV = "vasiere nue"
        tH2 = "demi-herbier"
        tH = "herbier"
        tA = "champs agricoles"
        tM = "mer"
        tP = "plage"
        tPP = 'port plaisance'
        tPI = 'port industriel'
        tF = 'foret'
        # Liste des coordonnées spécifiques à préserver avec leur valeur de surface
        self.cases_preservees = {
            (10,2): [sPC, tH2], (11,2): [sGC, tPS], (13,2): [sGC, tA],
            (9,3): [sPC, tH2], (10,3): [sGC, tV], (11,3): [sPC, tPS], (13,3): [sGC, tA], (14,3): [sGC, tA], (18,3): [sPC, tA],
            (9,4): [sPC, tPS], (10,4): [sPC, tPS], (18,4): [sGC, tA], (19,4): [sGC, tA],
            (8,5): [sPC, tO], (10,5): [sGC, tSAU], (12,5): [sPC, tSAU], (13,5): [sGC, tSAU], (14,5): [sPC, tSAU], (21,5): [sPC, tA],
            (7,6): [sPC, tP], (8,6): [sGC, tO], (10,6): [sPC, tSAU], (12,7): [sPC, tDA], (13,7): [sPC, tDA], (18,6): [sGC, tA], (19,6): [sPC, tA], (20,6): [sGC, tA], (21,6): [sPC, tA],        
            (7,7): [sPC, tP], (10,7): [sPC, tSAU], (11,8): [sPC, tDA], (12,8): [sPC, tDA], 
            (3,8): [sPC, tV], (4,8): [sPC, tV], (5,8): [sPC, tV], (8,8): [sPC, tDA],
            (2,9): [sPC, tV], (4,9): [sPC, t0], (5,9): [sPC, t0], (6,9): [sPC, t0], (7,9): [sPC, tDA], (8,9): [sPC, tDA], (9,9): [sGC, tDA], (10,9): [sGC, tDA], (11,9): [sGC, tDA], (19,9): [sPC, t0], (20,9): [sPC, t0],  
            (2,10): [sPC, tV], (7,10): [sPC, tDA], (8,10): [sPC, tDA], (9,10): [sGC, tDA], (10,10): [sGC, tDA], (11,10): [sGC, tDA], (18,10): [sPC, tA], (19,10): [sPC, tA], (20,10): [sGC, t0],  
            (4,11): [sPC, t0], (5,11): [sGC, t0], (8,11): [sPC, tDA], (9,11): [sGC, tDA], (10,11): [sGC, tDA], (11,11): [sGC, tDA], (12,11): [sGC, tDA], (13,11): [sGC, tDA], (16,11): [sPC, tA], (17,11): [sGC, tA], (18,11): [sGC, tA], (19,11): [sGC, tA], (20,11): [sGC, tA],  
            (2,12): [sPC, tPI], (3,12): [sPC, tPI], (10,12): [sPC, tDA], (11,12): [sPC, tDA], (12,12): [sPC, tDA], (16,12): [sPC, tA], (17,12): [sPC, tA], (18,12): [sGC, tA], (19,12): [sGC, tA], (20,12): [sGC, tA],  
            (3,13): [sPC, tPP], (19,13): [sGC, tA], 
            (3,14): [sPC, tPP], (4,14): [sPC, tPP],
            (4,15): [sPC, tO], (5,15): [sPC, tO], (20,15): [sPC, tF], (21,15): [sGC, tF], 
            (19,16): [sGC, tF], (20,16): [sGC, tF], (21,16): [sGC, tF], 
            (3,18): [sPC, tP], 
            (3,19): [sGC, tP],                                                                                    
            (4,20): [sPC, tSAU], (5,20): [sGC, tSAU], (9,20): [sGC, t0], (12,20): [sPC, tD], (13,20): [sPC, tD], (16,20): [sPC, tD], (17,20): [sPC, tD],
            (3,21): [sGC, tSAU], (4,21): [sGC, tSAU], (5,21): [sGC, tSAU], (6,21): [sGC, tSAU], (17,21): [sPC, tD], (18,21): [sGC, tD], (19,21): [sGC, tD]
        }

        # Balayage de toutes les cases
        for aCase in self.cases.getEntities():
            if (aCase.xPos, aCase.yPos) in self.cases_preservees:
                aCase.setValue("surface", self.cases_preservees[(aCase.xPos, aCase.yPos)][0])  # Définir la valeur de surface
                aCase.setValue("typeZH", self.cases_preservees[(aCase.xPos, aCase.yPos)][1])  # Définir la valeur de TYPEzh
            else:
                try:
                    self.cases.deleteEntity(aCase)
                except:
                    pass
        # self.cases.setEntities("typeZH","vide")

    def initialize_variables(self):
        # Variables de simulation
        self.sequestrationZH = self.myModel.newSimVariable("Sequestration ZH", 0)
        self.ptCB = self.myModel.newSimVariable("CB", 0)
        self.valeurPtCB = 0.75  # Taux de conversion entre le point CB et la valeur de sequestration (en T/ha/an)
        self.ptDE = self.myModel.newSimVariable("DE", 0)
        self.cumulDE = self.myModel.newSimVariable("réserve DE", 0)
        self.perc_ptCB_sequestrationZH = self.myModel.newSimVariable("part CB / sequest ZH", 0.00)
        self.sequestrationTot = self.myModel.newSimVariable("Bilan Sequestration", 0)
        self.nbBonusAmenage = self.myModel.newSimVariable(' Bonus déjà utilisés   ', 0)

    def initialize_actions(self):
        # Definition des actions de jeu
        self.Player = self.myModel.newPlayer("Player")

        for aZH in self.ZHs.keys():
            self.Player.addGameAction(self.myModel.newModifyAction(self.cases, {"typeZH": aZH}, feedbacks=[lambda: self.update_actions3()]))

        # Actions de type 1
        self.nbPionActions1_parJoueur = 'infinite'  # 20
        self.pionAction1 = self.myModel.newAgentSpecies("Action1", "circleAgent", defaultSize=5)
        self.pionAction1.newPov("joueur", "joueur", self.joueurs_potentiels)

        for jX in list(self.joueurs_actifs.keys()):
            nomJ = "" + jX
            self.Player.addGameAction(self.myModel.newCreateAction(
                self.pionAction1, 
                {"joueur": nomJ}, 
                self.nbPionActions1_parJoueur,
                conditions=[
                    lambda aCell: aCell.classDef != self.cases and aCell.value('type') == 'action1',
                ],
                create_several_at_each_click=True
            ))
        self.Player.addGameAction(self.myModel.newDeleteAction(self.pionAction1))

        # Actions de type 2
        self.nbPionActions2_parJoueur = 'infinite'  # 6
        self.pionAction2 = self.myModel.newAgentSpecies("Action2", "squareAgent", defaultSize=20, locationInEntity='center')
        self.pionAction2.newPov("joueur", "joueur", self.joueurs_actifs)

        for jX in list(self.joueurs_actifs.keys()):
            nomJ = "" + jX
            self.Player.addGameAction(self.myModel.newCreateAction(
                self.pionAction2, 
                {"joueur": nomJ}, 
                self.nbPionActions2_parJoueur,
                conditions=[
                    lambda aCell: aCell.classDef != self.cases and aCell.value('type') == 'action2',
                    lambda aCell: aCell.isEmpty(),
                ],
                feedbacks=[lambda: self.update_actions2()]
            ))
        self.Player.addGameAction(self.myModel.newDeleteAction(self.pionAction2, feedbacks=[lambda: self.update_actions2()]))

    def initialize_dashboards(self):
        # Dashboard des scores obtenus
        self.DashBoardInd = self.myModel.newDashBoard("Suivi des indicateurs")
        self.DashBoardInd.addIndicatorOnSimVariable(self.sequestrationZH)
        self.DashBoardInd.addSeparator()                                  
        self.DashBoardInd.addIndicatorOnSimVariable(self.ptCB)
        self.DashBoardInd.addIndicatorOnSimVariable(self.perc_ptCB_sequestrationZH)
        self.DashBoardInd.addSeparator()
        self.DashBoardInd.addIndicatorOnSimVariable(self.sequestrationTot)
        self.DashBoardInd.addSeparator()
        self.DashBoardInd.addIndicatorOnSimVariable(self.ptDE)
        self.DashBoardInd.addIndicatorOnSimVariable(self.cumulDE)
        self.DashBoardInd.moveToCoords(1510, 725)

        # Dashboard des surfaces des ZH
        self.DashBoardSurfaces = self.myModel.newDashBoard("Surfaces")
        for typeZH in self.ZHs.keys():
            if typeZH in ['demi-herbier', 'demi-herbier Diop', 'mer', 'vide']: continue
            if typeZH in ['pres sales Diop']:
                aMetricIndicator = self.DashBoardSurfaces.addIndicator_Sum(
                    self.cases, 
                    "surface", 
                    typeZH, 
                    conditionsOnEntities=[(lambda case, typeZH=typeZH: case.value("typeZH") == typeZH)]
                )
            else:
                aMetricIndicator = self.DashBoardSurfaces.addIndicatorOnEntity(
                    self.pZH[typeZH],
                    'surface actuelle',
                    title=typeZH
                )
        self.DashBoardSurfaces.moveToCoords(1510, 30)

    def initialize_phases(self):
        self.PlayerControlPanel = self.Player.newControlPanel("Actions")
        self.PlayerControlPanel.moveToCoords(1320, 30)
        self.myModel.setCurrentPlayer("Player")
        self.myModel.displayTimeInWindowTitle()
        
        self.modelPhase1 = self.myModel.timeManager.newModelPhase(
            [lambda: self.init_debut_tour()],
            auto_forward=True,
            message_auto_forward=False
        )
        self.gamePhase2 = self.myModel.timeManager.newGamePhase(
            "Jouer",
            [self.Player],
            show_message_box_at_start=False
        )
        self.modelPhase3 = self.myModel.timeManager.newModelPhase(
            [
                lambda: self.update_actions1(),
                lambda: self.update_actions3(),
                lambda: self.calc_sequestration_tot(),
                lambda: self.calc_cumul_de()
            ],
            name='Bilan du tour'
        )

    def initialize_buttons(self):
        # Button pour les cartes de changement de land use
        self.dashBonus = self.myModel.newDashBoard(backgroundColor='#afe3d7', borderColor='transparent')
        self.dashBonus.addIndicatorOnSimVariable(self.nbBonusAmenage)
        self.dashBonus.moveToCoords(1070, 852)
        
        self.myModel.newButton(
            (lambda: self.bonus_amenagement()),
            f"Bonus 10ha \nd'aménagement ({self.coutBonusAmenage} DE)",
            (1070, 800),
            padding=10,
            background_color='#afe3d7'
        )
        
        self.myModel.newButton(
            (lambda: self.ajout_de()),
            f"Ajouter/Retrancher des points DE)",
            (1070, 882),
            padding=8,
            background_color='#afe3d7'
        )

    def update_surface_zh(self, typeZH):
        """
        Met à jour la surface actuelle d'un type de ZH.
        
        Args:
            typeZH (str): Le type de zone humide à mettre à jour
        """
        # Calcul de la surface de base
        surface_base = self.cases.metricOnEntitiesWithValue('typeZH', typeZH, 'sumAtt', 'surface')
        self.pZH[typeZH].setValue("surface actuelle", surface_base)
        
        # Ajout de la moitié de la surface des demi-herbiers si applicable
        if typeZH in ['herbier', 'vasiere nue']:
            surface_demi_herbier = self.cases.metricOnEntitiesWithValue('typeZH', 'demi-herbier', 'sumAtt', 'surface')
            self.pZH[typeZH].incValue("surface actuelle", int(surface_demi_herbier / 2))      
        
        # Ajout de la moitié de la surface des demi-herbiers Diop si applicable
        if typeZH in ['herbier', 'vasiere nue Diop']:
            surface_demi_herbier_diop = self.cases.metricOnEntitiesWithValue('typeZH', 'demi-herbier Diop', 'sumAtt', 'surface')
            self.pZH[typeZH].incValue("surface actuelle", int(surface_demi_herbier_diop / 2))    

    def update_surface_all_zh(self):
        """
        Met à jour la surface de tous les types de ZH, en excluant certains types spécifiques.
        """
        for typeZH in self.ZHs.keys():
            if typeZH in ['demi-herbier', 'mer', 'vide', 'pres sales Diop', 'demi-herbier Diop']: 
                continue
            self.update_surface_zh(typeZH)

    def construct_zh(self, typeZH, coords=None):
        """
        Construit un plateau pour une zone humide.
        
        Args:
            typeZH (str): Le type de zone humide
            coords (tuple, optional): Coordonnées du plateau
        """
        nbCases = (0 if self.ZHs[typeZH]["potentiel accueil actions1"] is None else 4) + len(self.ZHs[typeZH]["cases actions2"]) + len(self.ZHs[typeZH].get("cases actions2 en plus", []))
        nbCols = 4
        nbLines = -(-nbCases // nbCols)  # Arrondir au nombre entier supérieur
        self.pZH[typeZH]=self.myModel.newCellsOnGrid(nbCols,nbLines,"square",size=30,gap=2,name=typeZH,color=self.ZHs[typeZH]["couleur"])
        self.pZH[typeZH].setEntities('potentiel accueil',0)
        self.pZH[typeZH].setEntities('frequentation',0) 
        self.pZH[typeZH].setEntities('surfrequentation',0) #0 si la cpacité d'accueil n'est passé  / 1 si la cpacité d'accueil est dépassé
        self.pZH[typeZH].setEntities('type',"vide")
        self.pZH[typeZH].setEntities('vue normale',"vide")
        self.pZH[typeZH].setEntities('effet sequestration',0)
        self.pZH[typeZH].setEntities('effet economie',0)
        self.update_surface_zh(typeZH) #permet de calculer la surface actuelle en prenant en compte le cas des demi-herbier et autre cas particuliers
        if typeZH in self.surfaceCorrespondantAuPotentielAccueilInitial:  
            surfaceInitialeDeReferencePourPotentielAccueil = self.surfaceCorrespondantAuPotentielAccueilInitial[typeZH]
        else:
            surfaceInitialeDeReferencePourPotentielAccueil = self.pZH[typeZH].value('surface actuelle')
        self.pZH[typeZH].setValue('surfaceInitialeDeReferencePourPotentielAccueil', surfaceInitialeDeReferencePourPotentielAccueil)
        self.pZH[typeZH].setValue('surfaceDuSeuilPrécédent_action2',self.pZH[typeZH].value('surface actuelle'))
        


        if self.ZHs[typeZH]["potentiel accueil actions1"] is None:
            startCasesActions2 = 1
        else:
            startCasesActions2 = nbCols +1
            case1= self.pZH[typeZH].getEntity(1,1)
            self.casesAction1.append(case1)
            case1.setValue('type','action1')
            case1.setValue('vue normale',"action1")
            case1.setValue('potentiel accueil',self.ZHs[typeZH]["potentiel accueil actions1"])
            

            #supprimer les cases de la première ligne sauf la première
            for aCaseInutile in self.pZH[typeZH].getEntities_withRow(1)[1:]:
                self.pZH[typeZH].deleteEntity(aCaseInutile)

        #Ajout des actions2 de base
        for i, paramCaseAction2 in enumerate(self.ZHs[typeZH]["cases actions2"], start=startCasesActions2):
            caseX = self.pZH[typeZH].getEntity(i)
            if caseX is not None and isinstance(paramCaseAction2, dict):
                caseX.setValue("type", "action2")
                caseX.setValue("vue normale", "action2")
                for aParam, aValue in paramCaseAction2.items():
                    caseX.setValue(aParam, aValue)
                    if aParam == "type_action2":
                        caseX.setValue("vue normale", aValue)
        # print(f"{typeZH}: {i if 'i' in locals() else 0}, startCasesActions2: {startCasesActions2}")
        
        #Ajout des actions2 en plus
        self.ZHs[typeZH]['Actions2 en plus']=[]
        if self.ZHs[typeZH].get("cases actions2 en plus") is not None:
            for j, paramCaseAction2 in enumerate(self.ZHs[typeZH]["cases actions2 en plus"], start=(i if 'i' in locals() else (startCasesActions2 -1))+1):
                caseX = self.pZH[typeZH].getEntity(j)
                caseX.setValue("type", "action2")
                caseX.setValue("vue normale", "action2")
                for aParam, aValue in paramCaseAction2.items():
                    caseX.setValue(aParam, aValue)
                    if aParam == "type_action2":
                        caseX.setValue("vue normale", aValue)
                self.ZHs[typeZH]['Actions2 en plus'].append(caseX)
                self.pZH[typeZH].deleteEntity(caseX)


        self.pZH[typeZH].newPov("vue normale", "vue normale", self.dictSymbology)  
        self.pZH[typeZH].newBorderPovColorAndWidth("bords", "type", {"action1": [Qt.black,1], "action2": [Qt.black,1], "vide": [Qt.transparent,0]})
        self.pZH[typeZH].displayBorderPov("bords")
      

        if coords != None : self.pZH[typeZH].grid.moveToCoords(coords)

        return self.pZH[typeZH]

    def update_actions1(self):
        """Mise à jour des actions de type 1"""
        for aCell in self.cases.getEntities():
            if aCell.value('type') == 'action1':
                aCell.setValue('nbPions', len(aCell.agentsInCell(self.pionAction1)))

    def update_actions2(self):
        """Mise à jour des actions de type 2"""
        for aCell in self.cases.getEntities():
            if aCell.value('type') == 'action2':
                aCell.setValue('nbPions', len(aCell.agentsInCell(self.pionAction2)))

    def update_actions3(self):
        """Mise à jour des actions de type 3 (changement de type de ZH)"""
        for aCell in self.cases.getEntities():
            if aCell.value('type') == 'action3':
                aCell.setValue('typeZH', aCell.value('typeZH'))

    def calc_sequestration_tot(self):
        """Calcul de la séquestration totale"""
        self.sequestrationTot.setValue(self.sequestrationZH.value() + self.ptCB.value() * self.valeurPtCB)

    def calc_cumul_de(self):
        """Calcul du cumul des points DE"""
        self.cumulDE.setValue(self.cumulDE.value() + self.ptDE.value())

    def init_debut_tour(self):
        """Initialisation au début de chaque tour"""
        self.ptDE.setValue(0)
        self.ptCB.setValue(0)
        self.sequestrationZH.setValue(0)
        self.sequestrationTot.setValue(0)

    def bonus_amenagement(self):
        """Gestion du bonus d'aménagement"""
        if self.cumulDE.value() >= self.coutBonusAmenage:
            self.cumulDE.setValue(self.cumulDE.value() - self.coutBonusAmenage)
            self.nbBonusAmenage.setValue(self.nbBonusAmenage.value() + 1)
            self.ptCB.setValue(self.ptCB.value() + 10)
            self.calc_sequestration_tot()

    def ajout_de(self):
        """Ajout ou retrait de points DE"""
        value, ok = QInputDialog.getInt(None, "Points DE", "Entrez le nombre de points DE à ajouter/retrancher:", 0, -100, 100, 1)
        if ok:
            self.ptDE.setValue(value)
            self.calc_cumul_de()

    def run(self):
        # First calc
        self.update_actions3()
        self.calc_sequestration_tot()
        self.myModel.launch()
        sys.exit(self.monApp.exec_())

if __name__ == "__main__":
    game = CarbonPolisGame()
    game.run()