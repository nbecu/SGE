

class SGUpdate():
    def __init__(self,anObject,number,restrictions=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.restrictions=restrictions

    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def addRestrictions(self,aRestriction):
        self.restrictions.append(aRestriction)
        
    def reset(self):
        self.numberUsed=0
        
    

  
            
    

