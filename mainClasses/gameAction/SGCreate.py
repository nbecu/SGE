

class SGCreate():
    def __init__(self,anObject,number,aDictOfAcceptedValue,restrictions=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.aDictOfAcceptedValue=aDictOfAcceptedValue
        self.restrictions=restrictions
        
    #Function which increment the number of use
    def use(self):
        self.numberUsed= self.numberUsed+1
        
    def getAuthorize(self):
        if self.numberUsed+1>self.number:
            return False
        else:
            return True

    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def addRestrictions(self,aRestriction):
        self.restrictions.append(aRestriction)
        
    def reset(self):
        self.numberUsed=0
        
    

  
            
    

