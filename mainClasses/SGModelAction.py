# TO BE CONTINUED
# #Class who manage a action to be executed by the model.
# It can handle more than one action, as well as a trigger condition, feedback actions and condition for feedbacks 
class SGModelAction():
    def __init__(self,actions=[],conditions=[],feedbacks=[]):
        self.actions=[]
        self.conditions=[]
        self.feedbacks=[]
        if isinstance(actions, list):
            self.actions=actions
        elif callable(actions): 
            self.actions= [actions]
        else:
            raise ValueError("Syntax error of actions")
        if isinstance(conditions, list):
            self.conditions=conditions
        elif callable(conditions): 
            self.conditions= [conditions]
        # if len(conditions) !=0:
        #     self.conditions = conditions # to be corrected
        #     breakpoint
        # self.testIfCallableAndPutInList(conditions)
        self.feedbacks=feedbacks


    def testIfCallableAndPutInList(self,anObject):
        if isinstance(anObject, list):
            aList=anObject
        elif callable(anObject): 
            aList = [anObject]
        else:
            raise ValueError("Syntax error of actions")
        return aList

    def testConditions(self):
        res = True 
        for aCondition in self.conditions:
            res = res and aCondition()
        return res
    
    def execute(self):
        if self.testConditions():
            allActionsDone = True
            for aAction in self.actions:
                if callable(aAction):
                    test = aAction()  #this command executes aAction
                    if test == False:
                        allActionsDone = False
                else:
                    raise ValueError("Syntax error of actions")
            if allActionsDone:
                for aFeedbackAction in self.feedbacks:
                    aFeedbackAction.execute()
                
 
            
            
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use


    def addModelAction(self,aAction):
        if callable(aAction):
            self.actions = self.actions + [aAction]
        else:
            raise ValueError("""Syntax error of actions. aAction should be:
                                a lambda function (syntax -> (lambda: instruction))""")
        
    def addCondition(self,aCondition):
        """Permits to add a Condition on a ModelAction
        
        Args:
            aFeedback (lambda function): condition"""
        if callable(aCondition):
            self.conditions = self.conditions + [aCondition]
        else:
            breakpoint
        return self

    def addFeedback(self,aFeedback):
        """Permits to add a Feedback on a ModelAction

        Args:
            aFeedback (lambda function): feedback action"""
        if isinstance(aFeedback,SGModelAction):
            self.feedbacks = self.feedbacks + [aFeedback]
        elif callable(aFeedback):
            self.feedbacks = self.feedbacks + [ self.model.newModelAction(aFeedback)]
        else:
            raise ValueError("""Syntax error of actions. aAction should be:
                                a lambda function (syntax -> (lambda: instruction)),
                                or an instance of SGModelAction (syntax -> aModel.newModelAction() ) """)
        
    # def addConditionOfFeedBack(self,aCondition):
    #     self.conditionOfFeedBack.append(aCondition)
        
    def setRandomEntities(self, att, value,nb):
        self.actions = self.actions + [lambda : self.model.grid.setRandomEntities(att, value,nb)]
        return self

  
            
    

class SGModelAction_OnEntities(SGModelAction):
    def __init__(self,actions=[],conditions=[],feedbacks=[], entities=None):
        super().__init__(actions,conditions,feedbacks)
                # super().__init__(parent)

        self.entitiesContainer=None
        self.setEntities(entities)

    def setEntities(self,entities):
        self.entitiesContainer = entities
        if type(self.entitiesContainer) == list:
            self.containerType = list
        elif callable(self.entitiesContainer):
            self.containerType = callable
        else:
            raise Exception("Sorry, wrong entities type")
    
    def getEntities(self):
        if self.containerType == list:
            return self.entitiesContainer
        else:
            return self.entitiesContainer()

    def execute(self):
        for aEntity in self.getEntities():
            if self.testConditions(aEntity):
                # allActionsDone = True
                for aAction in self.actions:
                    if callable(aAction):
                        test = aAction(aEntity)  #this command executes aAction
                        # if test == False:
                            # allActionsDone = False
                    # else:
                    #     raise ValueError("Syntax error of actions")
        # if allActionsDone:
        for aFeedbackAction in self.feedbacks:
            aFeedbackAction.execute()

    def testConditions(self,aEntity):
        res = True 
        for aCondition in self.conditions:
            res = res and aCondition(aEntity)
        return res
