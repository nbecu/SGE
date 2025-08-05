from mainClasses.SGModelAction import SGModelAction
from PyQt5.QtWidgets import QMessageBox

# Class who define a gaming phase


class SGTimePhase():
    def __init__(self, timeManager, name, modelActions=[], showMessageBoxAtStart=False, messageAutoForward=True):
        self.timeManager = timeManager
        self.name = name
        self.observers = {}
        self.watchers={}
        if isinstance(modelActions, SGModelAction):
            modelActions = [modelActions]
        elif isinstance(modelActions, list):
            self.modelActions = modelActions
        else:
            raise ValueError("Syntax error of actions")
        self._autoForwardOn = False
        self.showMessageBoxAtStart = showMessageBoxAtStart
        self.messageAutoForward = messageAutoForward


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use
    def setTextBoxText(self,aTextBox, aText):
        self.observers[aTextBox]=aText
    
    def notifyNewText(self):
        for aTextBox, aText in self.observers.items():
            aTextBox.setNewText(aText)

    def setNextStepAction(self, nextStepAction):
        self.nextStepAction = nextStepAction

    def addAction(self, aModelAction):
        if isinstance(aModelAction,SGModelAction):
            self.modelActions.append(aModelAction)
        else :
            self.modelActions.append( self.timeManager.model.newModelAction(aModelAction) )

    def execPhase(self):
        #proceed with optional message box at the start of the phase
        if self.showMessageBoxAtStart:
            if isinstance(self.showMessageBoxAtStart,str):
                aText = self.showMessageBoxAtStart
            else:
                aText = "The phase '"+self.name+"' starts"
            msg_box = QMessageBox(self.timeManager.model)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("SGE Time Manager Message")
            msg_box.setText(aText)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.exec_()
        
        # We can execute the actions           
        if len(self.modelActions) != 0:
            for aAction in self.modelActions:
                if callable(aAction):
                    aAction()  # this command executes aAction
                elif isinstance(aAction, SGModelAction):
                    aAction.execute()
        if self.watchers is not None:
            for aWatcher,aValue in self.watchers.items():
                if aValue == None:
                    aWatcher.updateText()
                else:
                    if aWatcher.method=="simVar":
                        aWatcher.simVar.setValue(aValue)
                    else:
                        aWatcher.entity.setValue(aWatcher.attribute,aValue)
                        aWatcher.updateText()
        #textbox update
        self.notifyNewText()

    def showEndPhaseMessage(self):
        """Affiche le message de fin de phase si messageAutoForward est activé"""
        if self.messageAutoForward:
            msg_box = QMessageBox(self.timeManager.model)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("SGE Time Manager Message")
            
            if isinstance(self.messageAutoForward, str):
                aText = self.messageAutoForward
            else:
                is_last = self.timeManager.isItTheLastPhase()
                if is_last:
                    aText = f"The phase '{self.name}' has been completed. The simulation now moves on to the next round"
                else:
                    next_phase = self.timeManager.getNextPhase()
                    aText = f"The phase '{self.name}' has been completed. The simulation now moves on to the next phase: '{next_phase.name}'"
            
            msg_box.setText(aText)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.exec_()

    def shouldForwardAutomatically(self):
        """Détermine si la phase doit passer automatiquement à la suivante"""
        return self._autoForwardOn

    def setAutoForward(self, value):
        """Active ou désactive le passage automatique à la phase suivante"""
        self._autoForwardOn = value

    def finalizePhase(self):
        """Exécute les actions nécessaires à la fin d'une phase"""
        if self.messageAutoForward:
            self.showEndPhaseMessage()
        
        # Les sous-classes peuvent surcharger cette méthode pour ajouter
        # des comportements spécifiques à la fin de leur phase

    def handleAutoForward(self):
        """Gère le passage automatique à la phase suivante si les conditions sont remplies"""
        if self.shouldForwardAutomatically():
            self.finalizePhase()
            self.timeManager.nextPhase()

# Class who define a gaming phase
class SGModelPhase(SGTimePhase):
    def __init__(self, timeManager, modelActions=[], name='', autoForwardOn=False, messageAutoForward=True, showMessageBoxAtStart=False):
        super().__init__(timeManager, name, modelActions=modelActions, showMessageBoxAtStart=showMessageBoxAtStart, messageAutoForward=messageAutoForward)
        self.setAutoForward(autoForwardOn)
    
    def getAuthorizedPlayers(self):
        return []


class SGGamePhase(SGTimePhase):
    def __init__(self, timeManager, modelActions=[], name='', authorizedPlayers=[], autoForwardWhenAllActionsUsed=False, messageAutoForward=True, showMessageBoxAtStart=False):
        super().__init__(timeManager, name, modelActions=modelActions, showMessageBoxAtStart=showMessageBoxAtStart, messageAutoForward=messageAutoForward)
        self._authorizedPlayers = authorizedPlayers if authorizedPlayers else []
        self.authorizedPlayers = self._authorizedPlayers
        self.autoForwardWhenAllActionsUsed = autoForwardWhenAllActionsUsed

    def addAuthorizedPlayer(self, player):
        """Ajoute un joueur à la liste des joueurs autorisés"""
        if player not in self._authorizedPlayers:
            self._authorizedPlayers.append(player)
            self.authorizedPlayers = self._authorizedPlayers

    def removeAuthorizedPlayer(self, player):
        """Retire un joueur de la liste des joueurs autorisés"""
        if player in self._authorizedPlayers:
            self._authorizedPlayers.remove(player)
            self.authorizedPlayers = self._authorizedPlayers

    def clearAuthorizedPlayers(self):
        """Vide la liste des joueurs autorisés"""
        self._authorizedPlayers = []
        self.authorizedPlayers = []

    def isPlayerAuthorized(self, player):
        """Vérifie si un joueur est autorisé dans cette phase"""
        return player in self._authorizedPlayers

    def getAuthorizedPlayers(self):
        """Retourne la liste des joueurs autorisés"""
        return self._authorizedPlayers.copy()

    def setAuthorizedPlayers(self, players):
        """Définit la liste complète des joueurs autorisés"""
        self._authorizedPlayers = players.copy()
        self.authorizedPlayers = self._authorizedPlayers

    def hasAllPlayersUsedAllActions(self):
        """Vérifie si tous les joueurs autorisés ont utilisé toutes leurs actions de jeu possibles"""
        for player in self._authorizedPlayers:
            if player.hasActionsToUse():
                return False
        return True

    def shouldForwardAutomatically(self):
        """Détermine si la phase doit passer automatiquement à la suivante"""
        if self._autoForwardOn:
            return True
        if self.autoForwardWhenAllActionsUsed:
            return self.hasAllPlayersUsedAllActions()
        return False

