from SGTimePhase import SGTimePhase

#Class that handle the overall management of time 
class SGTimeManager():
    
    def __init__(self,parent):
        self.parent=parent
        self.model=parent
        self.actualRound = 1
        self.actualPhase = 1
        self.orderGamePhases=[]
        self.conditionOfEndGame=[]
        
    #To increment the time of the game
    def nextPhase(self):
        if len(self.orderGamePhases) != 0 and ((self.orderGamePhases[self.actualPhase].activePlayer is not None and self.parent.whoIAm==self.orderGamePhases[self.actualPhase].activePlayer.name ) or self.parent.whoIAm=="Admin") :
            end = self.checkEndGame()
            if not end :
                if self.actualPhase+2 <= len(self.orderGamePhases):
                    if len(self.orderGamePhases)!=1:
                        self.actualPhase = self.actualPhase +1
                        self.model.myTimeLabel.updateTimeLabel(self.actualRound,self.actualPhase)

                else:
                    #We reset GM
                    for gm in self.parent.getGM():
                        gm.reset()
                    self.actualPhase=1

                    
                thePhase= self.orderGamePhases[self.actualPhase]
                #check conditions
                doThePhase=True
                if len(thePhase.conditionOfTrigger)!=0:
                    for aCondition in thePhase.conditionOfTrigger:
                        doThePhase=doThePhase and aCondition()
                if self.actualPhase == 1 and len(self.orderGamePhases) > 1:
                    self.actualRound += 1
                    self.model.myTimeLabel.updateTimeLabel(self.actualRound,self.actualPhase)
            
                #we change the active player
                self.parent.actualPlayer=thePhase.activePlayer
                if doThePhase :
                    #We make the change
                    if len(thePhase.nextStepAction) !=0:
                        for aChange in thePhase.nextStepAction:
                            aChange()
                    self.model.publishEntitiesState()
                else:
                    self.model.publishEntitiesState()
                    self.nextPhase()
       

        
    #To handle the victory Condition and the passment of turn    
    def next(self):
        #condition Victoire
        self.nextPhase()
        

    def checkEndGame(self):
        endGame=False
        for aCond in self.conditionOfEndGame:
            endGame=endGame or aCond()
        if endGame :
            print("C'est fini !")
        return endGame
    
    def getRoundNumber(self):
        return self.actualRound 
    
    def getPhaseNumber(self):
        return self.actualPhase


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
        

    #To verify a number of round
    def verifNumberOfRound(self,aNumber):
        return self.actualRound==aNumber
    
    #To verify if the number of round is peer 
    def isPeer(self):
        return self.actualRound%2==0
    
    #To verify if the number of round is odd
    def isOdd(self):
        return self.actualRound%2==1
    
    
  
            
    

