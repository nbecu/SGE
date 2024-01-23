from mainClasses.SGTimePhase import SGTimePhase
from mainClasses.SGTimePhase import SGModelPhase
from mainClasses.SGEndGameCondition import SGEndGameCondition
from mainClasses.SGDashBoard import SGDashBoard
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGModelAction import SGModelAction
from mainClasses.SGModelAction import SGModelAction_OnEntities

# Class that handle the overall management of time


class SGTimeManager():

    def __init__(self, parent):
        self.model = parent
        self.currentRoundNumber = 0
        self.currentPhaseNumber = 0
        self.phases = []
        self.conditionOfEndGame = []
        # self.newGamePhase('Initialisation', None)

    # # To increment the time of the game
    # def nextPhase(self):
    #     if len(self.phases) != 0:
    #         end = self.checkEndGame()
    #         if not end:
    #             if self.currentPhaseNumber+2 <= len(self.phases):
    #                 if len(self.phases) != 1:
    #                     self.currentPhaseNumber = self.currentPhaseNumber + 1
    #                     if self.model.myTimeLabel is not None:
    #                         self.model.myTimeLabel.updateTimeLabel()

    #             else:
    #                 #reset GameActions count
    #                 for action in self.model.getAllGameActions():
    #                     action.reset()
    #                 self.currentPhaseNumber = 1
                

    #             thePhase = self.phases[self.currentPhaseNumber]
    #             # check conditions for the phase
    #             doThePhase = True
    #             if self.currentPhaseNumber == 1 and len(self.phases) > 1:
    #                 self.currentRoundNumber += 1
    #                 if self.model.myTimeLabel is not None:
    #                     self.model.myTimeLabel.updateTimeLabel()
    #                 if self.model.userSelector is not None:
    #                     self.model.userSelector.updateUI(QHBoxLayout())

    #             # execute the actions of the phase
    #             if doThePhase:
    #                 thePhase.execPhase()
    #                 #watchers update
    #                 self.model.checkAndUpdateWatchers()
    #                 #mqtt update
    #     #The instructions below have been commented temporarily to test a new process for broker msg  
    #                 # if self.model.mqttMajType=="Phase" or self.model.mqttMajType=="Instantaneous":
    #                 #     self.model.publishEntitiesState()

    #                 if isinstance(thePhase,SGModelPhase) and self.phases[self.currentPhaseNumber].autoForwardOn==True:
    #                     pass

    #             else:
    #                 self.nextPhase()

    # # To handle the victory Condition and the passment of turn


# trying to refactor the nextPhase() method !
    # To increment the time of the game
    def nextPhase(self):
        if len(self.phases) == 0:
            print('warning : should we handle the case when there is no phases defined ?')
            return
        end = self.checkEndGame()
        if end :
            return

        self.model.recordAllData()

        if self.currentRoundNumber ==0: #This case is to quit the Initialization phase at the begining of the game
            self.currentRoundNumber = 1
            self.currentPhaseNumber = 1

        elif (self.currentPhaseNumber + 1) > len(self.phases)   : #This case is when  there is no nextphase after the current one. Therefor it is a next round
            self.currentRoundNumber += 1
            self.currentPhaseNumber = 1
            #reset GameActions count
            for action in self.model.getAllGameActions():
                action.reset()

        else : #This case is to advance to the next phase wthin the same round
            self.currentPhaseNumber += 1

        # if self.currentPhaseNumber+2 <= len(self.phases):
        #     if len(self.phases) != 1:
        #         self.currentPhaseNumber = self.currentPhaseNumber + 1
        #         if self.model.myTimeLabel is not None:
        #             self.model.myTimeLabel.updateTimeLabel()

        # else:
        #     #reset GameActions count
        #     for action in self.model.getAllGameActions():
        #         action.reset()
        #     self.currentPhaseNumber = 1
        
        # Process the widgets for this next phase/round
        if self.model.myTimeLabel is not None:
            self.model.myTimeLabel.updateTimeLabel()
        if self.model.userSelector is not None:
            self.model.userSelector.updateUI(QHBoxLayout())

        # thePhase = self.phases[self.currentPhaseNumber]
        # # check conditions for the phase
        # doThePhase = True
        # if self.currentPhaseNumber == 1 and len(self.phases) > 1:
        #     self.currentRoundNumber += 1
        #     if self.model.myTimeLabel is not None:
        #         self.model.myTimeLabel.updateTimeLabel()
        #     if self.model.userSelector is not None:
        #         self.model.userSelector.updateUI(QHBoxLayout())

        # execute the actions of the phase
        self.getCurrentPhase().execPhase()
        #watchers update
        self.model.checkAndUpdateWatchers()
            #mqtt update
#The instructions below have been commented temporarily to test a new process for broker msg  
            # if self.model.mqttMajType=="Phase" or self.model.mqttMajType=="Instantaneous":
            #     self.model.publishEntitiesState()

        if self.getCurrentPhase().autoForwardOn :
            self.nextPhase()

            

    def getCurrentPhase(self):
        return self.phases[self.currentPhaseNumber-1]
                            

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
        aPhase = SGTimePhase(self, name, activePlayers, modelActions)
        self.phases = self.phases + [aPhase]
        return aPhase

 # To add a new Phase during which the model will execute some instructions
    def newModelPhase(self, actions=[], condition=[], name='',autoForwardOn=False):
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

        aPhase = SGModelPhase(self,modelActions=modelActions, name=name,autoForwardOn=autoForwardOn)
        self.phases = self.phases + [aPhase]
        return aPhase

    # To verify a number of round
    def verifNumberOfRound(self, aNumber):
        return self.currentRoundNumber == aNumber

    # To verify if the number of round is peer
    def isPeer(self):
        return  (self.currentRoundNumber != 0) and (self.currentRoundNumber % 2 == 0)

    # To verify if the number of round is odd
    def isOdd(self):
        return self.currentRoundNumber % 2 == 1

    # To verify if its the initialization period (round 0)
    def isInitialization(self):
        return self.currentRoundNumber  == 0