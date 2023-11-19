from mainClasses.SGModelAction import SGModelAction

# Class who define a gaming phase


class SGTimePhase():
    def __init__(self, timeManager, name, activePlayers, modelActions=[]):
        self.timeManager = timeManager
        self.name = name
        self.activePlayers = activePlayers
        if isinstance(modelActions, list):
            self.modelActions = modelActions
        else:
            self.modelActions = [modelActions]
            print(self.modelActions)


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use


    def setActivePlayers(self, activePlayers):
        self.activePlayers = activePlayers

    def setNextStepAction(self, nextStepAction):
        self.nextStepAction = nextStepAction

    def addModelAction(self, aModelAction):
        if isinstance(aModelAction,SGModelAction):
            self.modelActions.append(aModelAction)
        else :
            self.modelActions.append( self.timeManager.model.newModelAction(aModelAction) )


# Class who define a gaming phase
class SGModelPhase(SGTimePhase):
    def __init__(self, timeManager, modelActions=[], feedbacks=[], feedbacksCondition=[], name=''):
        self.timeManager = timeManager
        if isinstance(modelActions, SGModelAction):
            modelActions = [modelActions]
        elif isinstance(modelActions, list):
            self.modelActions = modelActions
        else:
            raise ValueError("Syntax error of actions")
        self.feedbacks = feedbacks  # a priori obsolete
        self.feedbacksCondition = feedbacksCondition  # a priori obsolete
        self.name = name
