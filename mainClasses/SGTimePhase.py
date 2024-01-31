from mainClasses.SGModelAction import SGModelAction

# Class who define a gaming phase


class SGTimePhase():
    def __init__(self, timeManager, name, authorizedPlayers=[], modelActions=[]):
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
                        aWatcher.simVar.setValue(aValue) #problème à getPermissionUpdate
                    else:
                        aWatcher.entity.setValue(aWatcher.attribute,aValue) #problème à getPermissionUpdate
                        aWatcher.updateText()
        #textbox update
        self.notifyNewText()

# Class who define a gaming phase
class SGModelPhase(SGTimePhase):
    def __init__(self, timeManager, modelActions=[], name='',autoForwardOn=False):
        super().__init__(timeManager, name, authorizedPlayers=[], modelActions=modelActions)
        self.autoForwardOn=autoForwardOn
