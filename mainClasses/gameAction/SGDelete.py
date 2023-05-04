from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

#Class who manage the game mechanics of delete
class SGDelete():
    def __init__(self,anObject,number,dictAttributs):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.dictAttributs=dictAttributs
        self.name="DeleteAction "+str(anObject)
            
        
    #Function which increment the number of use
    def use(self):
        self.numberUsed= self.numberUsed+1
        
    #Function to test if the game action could be use
    def getAuthorize(self,anObject):
        returnValue=True
        #We check each condition 
        if self.numberUsed+1>self.number:
            returnValue=False
        return returnValue

    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
        
    def reset(self):
        self.numberUsed=0