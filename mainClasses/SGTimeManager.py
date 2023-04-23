from SGTimePhase import SGTimePhase
from mainClasses.SGTimePhase import SGModelPhase

#Class that handle the overall management of time 
class SGTimeManager():
    
    def __init__(self,parent):
        self.model=parent
        self.currentRound = 0
        self.currentPhaseNb = 1
        self.phases=[]
        self.conditionOfEndGame=[]
        self.newGamePhase('Initialisation',0)

    # to access the phase at the currentPhaseNumber
    def currentPhase(self):
        return self.phases[self.currentPhaseNb]

    #To increment the time of the game
    def nextPhase(self):
        self.advanceTime()
        self.processPhase()
    
    def advanceTime(self):
           # if phases is empty then exit
        if not self.phases :
            return
        
        # if end of game, then exit
        if self.checkEndGame() :
            return
        
        # check if it's the last phase of the round, thne advance the phase or the round
        if self.currentPhaseNb+2 <= len(self.phases):
            self.currentPhaseNb += 1
        else:
            self.currentRound += 1
            self.currentPhaseNb=1
            
        # update the time label
        self.model.myTimeLabel.updateTimeLabel()


    def processPhase(self):
        if isinstance(self.currentPhase(),SGModelPhase) :
            self.currentPhase().execute()
       

        
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
        return self.currentPhaseNb


#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #To add a new Game Phase
    def newGamePhase(self,name,activePlayer=None,modelActions=[]):
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

 #To add a new Phase during which the model will execute some instructions
 # TO BE CONTINUED
    def newModelPhase(self,actions=[],condition=lambda: True,feedBacks=[],feedBacksCondition=lambda: True,name=''):
        """
        To add a round phase during which the model will execute some actions (add, delete, move...)
        args:
            actions (lambda function): Actions the model performs during the phase (add, delete, move...)
            condition (lambda function): Actions are performed only if the condition returns true  
            feedbacks (lambda function): Feedback actions performed only if the actions are executed
            feddbacksCondition (lambda function): Feedback actions are performed only if the feddbacksCondition returns true  
            name (str): Name displayed on the TimeLabel
        """

        if len(feedBacks) == 0:
            feedBacksCondition= lambda: False
        aPhase=SGModelPhase(actions,condition,feedBacks,feedBacksCondition,name)
        self.phases.append(aPhase)
        return aPhase
       

    def newGamePhase_adv(self,name,activePlayer=None,modelActions=[]):
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

    
  
            
    

