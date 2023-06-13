from SGTimePhase import SGTimePhase
from SGTimePhase import SGModelPhase
from SGEndGameCondition import SGEndGameCondition
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SGModelAction import SGModelAction

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

    def getRoundNumber(self):
        return self.currentRound

    def getPhaseNumber(self):
        return self.currentPhase


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

    # To add a new Game Phase

    def newGamePhase(self, name, activePlayers, modelActions=[]):
        """
        To add a Game Phase in a round.

        args:
            name (str): Name displayed on the TimeLabel
            activePlayers : List of plays concerned about the phase (default:all)
            modelActions (list): Actions the model performs at the beginning of the phase (add, delete, move...)
        """
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
        if isinstance(actions, SGModelAction):
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

    # To add a condition to end the game
    """def addEndGameCondition(self,aMethod,objective,concernedEntity,attribut=None,victoryNumber=None,name=None,color=Qt.black):
        aCondition=SGVictoryCondition(self.model.victoryBoard,name,aMethod,objective,attribut,victoryNumber,concernedEntity,color)
        self.conditionOfEndGame.append(aCondition)"""

    # To verify a number of round
    def verifNumberOfRound(self, aNumber):
        return self.currentRound == aNumber

    # To verify if the number of round is peer
    def isPeer(self):
        return self.currentRound % 2 == 0

    # To verify if the number of round is odd
    def isOdd(self):
        return self.currentRound % 2 == 1
