from mainClasses.SGModelAction import SGModelAction
from PyQt5.QtWidgets import QMessageBox

# Class who define a gaming phase


class SGTimePhase():
    def __init__(self, timeManager, name, authorizedPlayers=[], modelActions=[],showMessageBoxAtStart=False):
        self.timeManager = timeManager
        self.name = name
        self.authorizedPlayers = authorizedPlayers
        self.observers = {}
        self.watchers={}
        if isinstance(modelActions, SGModelAction):
            modelActions = [modelActions]
        elif isinstance(modelActions, list):
            self.modelActions = modelActions
        else:
            raise ValueError("Syntax error of actions")
        self.autoForwardOn = False
        self.showMessageBoxAtStart=showMessageBoxAtStart


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use
    def setTextBoxText(self,aTextBox, aText):
        self.observers[aTextBox]=aText
    
    def notifyNewText(self):
        for aTextBox, aText in self.observers.items():
            aTextBox.setNewText(aText)

    def authorizePlayers(self, authorizedPlayers):
        self.authorizedPlayers = authorizedPlayers

    def setNextStepAction(self, nextStepAction):
        self.nextStepAction = nextStepAction

    def addModelAction(self, aModelAction):
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

# Class who define a gaming phase
class SGModelPhase(SGTimePhase):
    def __init__(self, timeManager, modelActions=[], name='',autoForwardOn=False,messageAutoForward=True,showMessageBoxAtStart=False):
        super().__init__(timeManager, name, authorizedPlayers=[], modelActions=modelActions,showMessageBoxAtStart=showMessageBoxAtStart)
        self.autoForwardOn=autoForwardOn
        self.messageAutoForward=messageAutoForward
