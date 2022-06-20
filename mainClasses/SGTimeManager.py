from SGTimePhase import SGTimePhase

class SGTimeManager():
    
    def __init__(self,parent):
        self.parent=parent
        self.actualRound = 0
        self.actualPhase = -1
        self.orderGamePhases=[]
        self.conditionOfEndGame=[]
        
    #To increment the time of the game
    def nextPhase(self):
        end = self.checkEndGame()
        if not end :
            if self.actualPhase+2 <= len(self.orderGamePhases):
                if len(self.orderGamePhases)!=1:
                    self.actualPhase = self.actualPhase +1
            else:
                self.actualPhase=0

                
            thePhase= self.orderGamePhases[self.actualPhase]
            #Add conditions
            doThePhase=True
            if len(thePhase.conditionOfTrigger)!=0:
                for aCondition in thePhase.conditionOfTrigger:
                    doThePhase=doThePhase and aCondition()
            if self.actualPhase==len(self.orderGamePhases)-1:
                self.actualRound=self.actualRound+1
            #we change the active player
            self.parent.actualPlayer=thePhase.activePlayer
            if doThePhase :
                #Add Action of players 
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
    def addGamePhase(self,name,orderNumber,activePlayer=None,nextStepAction=[],conditionOfTrigger=[]):
        aPhase=SGTimePhase(name,orderNumber,activePlayer,nextStepAction,conditionOfTrigger)
        if orderNumber == 0 :
            self.parent.actualPlayer=activePlayer
        self.orderGamePhases.insert(orderNumber,aPhase)
        return aPhase
    
    #To add a condition to end the game
    def addEndGameCondition(self,aCondition):
        self.conditionOfEndGame.append(aCondition)
        
    def checkEndGame(self):
        endGame=False
        for aCond in self.conditionOfEndGame:
            endGame=endGame or aCond()
        if endGame :
            print("C'est finit !")
        return endGame
        
    #To verify a number of round
    def verifNumberOfRound(self,aNumber):
        return self.actualRound==aNumber
    
    #To verify if the number of round is peer 
    def isPeer(self):
        return self.actualRound%2==0
    
    #To verify if the number of round is odd
    def isOdd(self):
        return self.actualRound%2==1
    
    
  
            
    

