from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of mooving
class SGMove(SGAbstractAction):
    def __init__(self,anObject,number,dictAttributs,restrictions=[],feedBack=[],conditionOfFeedBack=[],feedbackAgent=[],conditionOfFeedBackAgent=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.dictAttributs=dictAttributs
        self.restrictions=restrictions
        self.name="Move "+str(anObject.name)
        self.feedback=feedBack
        self.conditionOfFeedBack=conditionOfFeedBack
        self.feedbackAgent=feedbackAgent
        self.conditionOfFeedBackAgent=conditionOfFeedBackAgent
            
        