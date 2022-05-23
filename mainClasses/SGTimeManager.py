from mainClasses.SGTimePhase import SGTimePhase

class SGTimeManager():
    
    def __init__(self):
        self.actualRound = 0
        self.actualPhase = 0
        self.orderGamePhases=[]
        
    #To increment the time of the game
    def nextPhase(self):
        if self.actualPhase +1 > len(self.orderGamePhases):
            self.actualPhase=0
            self.actualRound=self.actualRound+1
        else:
            if len(self.orderGamePhases)!=1:
                self.actualPhase = self.actualPhase +1
        thePhase= self.orderGamePhases[self.actualPhase]
        #Ajouter verifier les conditions
        #Ajouter les joueurs actifs qui joue 
        if len(thePhase.nextStepAction) !=0:
            for aChange in thePhase.nextStepAction:
                aChange()
        
    #To handle the victory Condition and the passment of turn    
    def next(self):
        #condition Victoire
        self.nextPhase()
        

        
    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #To add a new Game Phase
    def addGamePhase(self,name,orderNumber,activePlayers=[],nextStepAction=[],conditionOfTrigger=[True]):
        aPhase=SGTimePhase(name,orderNumber,activePlayers,nextStepAction,conditionOfTrigger)
        self.orderGamePhases.insert(orderNumber,aPhase)
    
    
  
            
    

