from mainClasses.SGTimePhase import SGTimePhase
from mainClasses.SGTimePhase import SGModelPhase
from mainClasses.SGEndGameCondition import SGEndGameCondition
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGModelAction import SGModelAction
from mainClasses.SGModelAction import SGModelAction_OnEntities

# Class that handle the overall management of time


class SGTimeManager():

    def __init__(self, parent):
        self.model = parent
        self.currentRound = 1
        self.currentPhase = 1
        self.phases = []
        self.conditionOfEndGame = []
        self.newGamePhase('Initialisation', None)

    # To increment the time of the game
    def nextPhase(self):
        if len(self.phases) != 0 and ((self.model.currentPlayer is not None and self.model.currentPlayer in self.model.users) or self.model.currentPlayer == "Admin"):
            end = self.checkEndGame()
            if not end:
                if self.currentPhase+2 <= len(self.phases):
                    if len(self.phases) != 1:
                        self.currentPhase = self.currentPhase + 1
                        if self.model.myTimeLabel is not None:
                            self.model.myTimeLabel.updateTimeLabel()

                else:
                    # We reset GM
                    for gm in self.model.getGM():
                        gm.reset()
                    self.currentPhase = 1
                
                #reset GameActions count
                for user in self.model.users:
                    if user != "Admin":
                        player=self.model.getPlayerObject(user)

                        for action in player.gameActions:
                            action.reset()

                thePhase = self.phases[self.currentPhase]
                # check conditions for the phase
                doThePhase = True
                if self.currentPhase == 1 and len(self.phases) > 1:
                    self.currentRound += 1
                    if self.model.myTimeLabel is not None:
                        self.model.myTimeLabel.updateTimeLabel()
                    if self.model.myUserSelector is not None:
                        self.model.myUserSelector.updateUI(QHBoxLayout())

                # execute the actions of the phase
                if doThePhase:
                    # We can execute the actions
                    if len(thePhase.modelActions) != 0:
                        for aAction in thePhase.modelActions:
                            if callable(aAction):
                                aAction()  # this command executes aAction
                            elif isinstance(aAction, SGModelAction):
                                aAction.execute()
                    #watchers update
                    self.checkDashBoard()
                    #mqtt update
                    if self.model.mqttMajType=="Phase" or self.model.mqttMajType=="Instantaneous":
                        self.model.publishEntitiesState()


                else:
                    self.nextPhase()

    # To handle the victory Condition and the passment of turn

    def next(self):
        # condition Victoire
        self.nextPhase()

    def checkEndGame(self):
        endGame = False
        counter = 0
        for aCond in self.conditionOfEndGame:
            aCond.verifStatus()
            if aCond.endGameRule.displayRefresh == 'instantaneous':
                aCond.updateText()
            if aCond.checkStatus:
                counter = counter+1
                if counter >= aCond.endGameRule.numberRequired:
                    endGame = True
                    break
        if endGame:
            print("C'est fini !")
        return endGame
    
    def checkDashBoard(self):
        for grid in self.model.getGrids():
            for attribut in self.model.cellCollection[grid.id]["watchers"]:
                for watcher in self.model.cellCollection[grid.id]["watchers"][attribut]:
                    updatePermit=watcher.getUpdatePermission()
                    if updatePermit:
                        watcher.updateText()
        for specie in self.model.agentSpecies.values():
            for watchers in specie["watchers"].values():
                for watcher in watchers:
                    updatePermit=watcher.getUpdatePermission()
                    if updatePermit:
                        watcher.updateText()



    def getRoundNumber(self):
        return self.currentRound

    def getPhaseNumber(self):
        return self.currentPhase
    
    #Update
    def updateEndGame(self):
        for condition in self.conditionOfEndGame:
            condition.updateText()


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

    # To add a new Game Phase

    def newGamePhase(self, name, activePlayers):
        """
        To add a Game Phase in a round.

        args:
            name (str): Name displayed on the TimeLabel
            activePlayers : List of plays concerned about the phase (default:all)
        """
        #modelActions (list): Actions the model performs at the beginning of the phase (add, delete, move...)
        modelActions=[]
        if activePlayers == None:
            activePlayers = self.model.users
        aPhase = SGTimePhase(name, activePlayers, modelActions)
        self.phases = self.phases + [aPhase]
        return aPhase

 # To add a new Phase during which the model will execute some instructions
 # TO BE CONTINUED
    def newModelPhase(self, actions=[], condition=[], name=''):
        """
        To add a round phase during which the model will execute some actions (add, delete, move...)
        args:
            actions (lambda function): Actions the model performs during the phase (add, delete, move...)
            condition (lambda function): Actions are performed only if the condition returns true  
            name (str): Name displayed on the TimeLabel
        """
        modelActions = []
        if isinstance(actions, (SGModelAction,SGModelAction_OnEntities)):
            actions.addCondition(condition)
            modelActions.append((actions))
        elif callable(actions):
            modelActions.append(self.model.newModelAction(actions, condition))
        elif isinstance(actions, list):
            for aAction in actions:
                if isinstance(aAction, SGModelAction):
                    aAction.addCondition(condition)
                    modelActions.append((aAction))
                elif callable(aAction):
                    modelActions.append(
                        self.model.newModelAction(aAction, condition))
                else:
                    raise ValueError("""Syntax error of actions. aAction should be:
                                a lambda function (syntax -> (lambda: instruction)),
                                or an instance of SGModelAction (syntax -> aModel.newModelAction() ) """)
        else:
            raise ValueError("""Syntax error of actions. aAction should be:
                                a lambda function (syntax -> (lambda: instruction)),
                                or an instance of SGModelAction (syntax -> aModel.newModelAction() ) """)

        aPhase = SGModelPhase(modelActions=modelActions, name=name)
        self.phases = self.phases + [aPhase]
        return aPhase

    def newGamePhase_adv(self, name, activePlayer=None, modelActions=[]):
        #! OBSOLETE
        """
        To add a Game Phase in a round.

        args:
            name (str): Name displayed on the TimeLabel
            activePlayer (?): Player concerned about the phase (default:None)
            modelActions (list): Actions the model performs at the beginning of the phase (add, delete, move...)
        """
        aPhase = SGTimePhase(name, activePlayer, modelActions)
        if activePlayer == None:
            self.model.actualPlayer = activePlayer
        self.phases.append(aPhase)
        return aPhase


    # To verify a number of round
    def verifNumberOfRound(self, aNumber):
        return self.currentRound == aNumber

    # To verify if the number of round is peer
    def isPeer(self):
        return self.currentRound % 2 == 0

    # To verify if the number of round is odd
    def isOdd(self):
        return self.currentRound % 2 == 1
