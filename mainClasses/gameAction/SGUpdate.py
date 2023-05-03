from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

#Class who manage the game mechanics of Update
class SGUpdate():
    def __init__(self,anObject,number,aDictOfAcceptedValue):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.aDictOfAcceptedValue=aDictOfAcceptedValue
        if isinstance(anObject,SGAgent):
            self.name=anObject.getId()
        elif isinstance(anObject,SGCell):
            self.name=anObject.grid

            
        
    #Function which increment the number of use
    def use(self):
        self.numberUsed= self.numberUsed+1
    
    #Function to test if the game action could be use    
    def getAuthorize(self,anObject):
        """NOT TESTED"""
        returnValue=True 
        if self.numberUsed+1>self.number:
            returnValue=False
        return returnValue

    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
        
    def reset(self):
        self.numberUsed=0
    

  
            
    

