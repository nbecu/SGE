from email import feedparser
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction


#Class who manage the game mechanics of creation
class SGCreate(SGAbstractAction):
    def __init__(self,anObject,number,dictAttributs,restrictions=[],feedBack=[],conditionOfFeedBack=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.dictAttributs=dictAttributs
        self.name="CreateAction "+str(anObject.name)
        self.restrictions=restrictions
        self.feedback=feedBack
        self.conditionOfFeedBack=conditionOfFeedBack

    

