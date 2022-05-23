from mainClasses.SGTimePhase import SGTimePhase

class SGTimeManager():
    
    def __init__(self):
        self.actualRound = 0
        self.actualPhase = -1
        self.orderGamePhases=[]
        
    #To increment the time of the game
    def nextPhase(self):
        if self.actualPhase+2 <= len(self.orderGamePhases):
            if len(self.orderGamePhases)!=1:
                self.actualPhase = self.actualPhase +1
        else:
            self.actualPhase=0
            
        print("------")
        print(self.actualPhase)
        print("------")
        thePhase= self.orderGamePhases[self.actualPhase]
        print(thePhase.name)
        print(self.actualRound)
        print(self.actualPhase)
        #Ajouter verifier les conditions
        doThePhase=True
        if len(thePhase.conditionOfTrigger)!=0:
            for aCondition in thePhase.conditionOfTrigger:
                doThePhase=doThePhase and aCondition()
        if self.actualPhase==len(self.orderGamePhases)-1:
            self.actualRound=self.actualRound+1
        if doThePhase :
            #Ajouter les joueurs actifs qui joue 
            if len(thePhase.nextStepAction) !=0:
                for aChange in thePhase.nextStepAction:
                    aChange()
        else:
            self.nextPhase()
        
    #To handle the victory Condition and the passment of turn    
    def next(self):
        #condition Victoire
        self.nextPhase()
        

        
    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #To add a new Game Phase
    def addGamePhase(self,name,orderNumber,activePlayers=[],nextStepAction=[],conditionOfTrigger=[]):
        aPhase=SGTimePhase(name,orderNumber,activePlayers,nextStepAction,conditionOfTrigger)
        self.orderGamePhases.insert(orderNumber,aPhase)
        
    #To verify a number of round
    def verifNumberOfRound(self,aNumber):
        return self.actualRound==aNumber
    
    
  
            
    

