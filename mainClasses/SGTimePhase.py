from mainClasses.SGModelAction import SGModelAction

# Class who define a gaming phase


class SGTimePhase():
    def __init__(self, name, activePlayers, modelActions=[]):
        self.name = name
        self.activePlayers = activePlayers
        self.associatedTextBoxes=[]
        if isinstance(modelActions, list):
            self.modelActions = modelActions
        else:
            self.modelActions = [modelActions]
            print(self.modelActions)


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

    def setTextBoxText(self,aTextBox, aText):
        """Ne fonctionne pas encore"""
        self.associatedTextBoxes.append(aTextBox)
        
        aTextBox.setNewText(aText)
        aTextBox.updateText()

    def setActivePlayers(self, activePlayers):
        self.activePlayers = activePlayers

    def setNextStepAction(self, nextStepAction):
        self.nextStepAction = nextStepAction

    def setModelActions(self, anAction):
        self.modelActions.append(anAction)


# Class who define a gaming phase
class SGModelPhase(SGTimePhase):
    def __init__(self, modelActions=[], feedbacks=[], feedbacksCondition=[], name=''):
        if isinstance(modelActions, SGModelAction):
            modelActions = [modelActions]
        elif isinstance(modelActions, list):
            self.modelActions = modelActions
        else:
            raise ValueError("Syntax error of actions")
        self.feedbacks = feedbacks  # a priori obsolete
        self.feedbacksCondition = feedbacksCondition  # a priori obsolete
        self.name = name
