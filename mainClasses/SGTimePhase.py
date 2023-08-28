from mainClasses.SGModelAction import SGModelAction

# Class who define a gaming phase


class SGTimePhase():
    def __init__(self, name, activePlayers, modelActions=[]):
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

    def setModelActions(self, anAction):
        self.modelActions.append(anAction)


# Class who define a gaming phase
class SGModelPhase(SGTimePhase):
    def __init__(self, modelActions=[], feedBacks=[], feedBacksCondition=[], name=''):
        if isinstance(modelActions, SGModelAction):
            modelActions = [modelActions]
        elif isinstance(modelActions, list):
            self.modelActions = modelActions
        else:
            raise ValueError("Syntax error of actions")
        self.feedBacks = feedBacks  # a priori obsolete
        self.feedBacksCondition = feedBacksCondition  # a priori obsolete
        self.name = name
