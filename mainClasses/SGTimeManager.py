from SGTimePhase import SGTimePhase

#Class that handle the overall management of time 
class SGTimeManager():
    
    def __init__(self,parent):
        self.model=parent
        self.currentRound = 1
        self.currentPhase = 1
        self.phases=[]
        self.conditionOfEndGame=[]
        self.addGamePhase('Initialisation',0)
        
    #To increment the time of the game
    def nextPhase(self):
        if len(self.phases) != 0 and ((self.phases[self.currentPhase].activePlayer is not None and self.model.whoIAm==self.phases[self.currentPhase].activePlayer.name ) or self.model.whoIAm=="Admin") :
            end = self.checkEndGame()
            if not end :
                if self.currentPhase+2 <= len(self.phases):
                    if len(self.phases)!=1:
                        self.currentPhase = self.currentPhase +1
                        self.model.myTimeLabel.updateTimeLabel()

                else:
                    #We reset GM
                    for gm in self.model.getGM():
                        gm.reset()
                    self.currentPhase=1

                    
                thePhase= self.phases[self.currentPhase]
                #check conditions
                doThePhase=True
                if self.currentPhase == 1 and len(self.phases) > 1:
                    self.currentRound += 1
                    self.model.myTimeLabel.updateTimeLabel()
            
                #we change the active player
                self.model.currentPlayer=thePhase.activePlayer
                if doThePhase :
                    #We make the change
                    if len(thePhase.modelActions) !=0:
                        for aChange in thePhase.modelActions:
                            aChange()
                else:
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
        return self.currentRound 
    
    def getPhaseNumber(self):
        return self.currentPhase


#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #To add a new Game Phase
    def addGamePhase(self,name,activePlayer=None,modelActions=[]):
        """
        To add a Game Phase in a round.

        args:
            name (str): Name displayed on the TimeLabel
            activePlayer (?): Player concerned about the phase (default:None)
            modelActions (list): Actions the model performs at the beginning of the phase (add, delete, move...)
        """
        aPhase=SGTimePhase(name,activePlayer,modelActions)
        if activePlayer == None :
            self.model.actualPlayer=activePlayer
        self.phases.append(aPhase)
        return aPhase
    
    #To add a condition to end the game
    def addEndGameCondition(self,aCondition):
        """NOT TESTED"""
        self.conditionOfEndGame.append(aCondition)
        

    #To verify a number of round
    def verifNumberOfRound(self,aNumber):
        return self.currentRound==aNumber
    
    #To verify if the number of round is peer 
    def isPeer(self):
        return self.currentRound%2==0
    
    #To verify if the number of round is odd
    def isOdd(self):
        return self.currentRound%2==1

    
  
            
    

