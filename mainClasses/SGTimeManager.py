from mainClasses.SGTimePhase import *
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGModelAction import SGModelAction
from mainClasses.SGModelAction import SGModelAction_OnEntities

# Class that handle the overall management of time


class SGTimeManager():
  
    def __init__(self, parent):
        self.model = parent
        self.currentRoundNumber = 0
        self.currentPhaseNumber = 0
        self.phases = []
        self.conditionOfEndGame = []
        
    # To increment the time of the game
    def nextPhase(self):
        if self.numberOfPhases() == 0:
            # TODO: should we handle differently the case when there is no phases defined ?
            return
        
        # Record the data of the step in dataRecorded
        self.model.dataRecorder.calculateStepStats()

        # Process the conditions of game ending
        isEndGame = self.checkEndGame()
        if isEndGame : return

        # set the values of currentRoundNumber and currentPhaseNumber
        ## This case is to quit the Initialization phase at the begining of the game
        if self.currentRoundNumber ==0:     
            self.currentRoundNumber = 1
            self.currentPhaseNumber = 1
        ## This case is when  there is no nextphase after the current one. Therefor it is a next round
        elif self.isItTheLastPhase():    
            self.currentRoundNumber += 1
            self.currentPhaseNumber = 1
            #reset GameActions count
            for action in self.model.getAllGameActions():
                action.reset()
        ## This case is to advance to the next phase wthin the same round
        else :
            self.currentPhaseNumber += 1
        
        # Process the timeLabel widgets for this next phase/round
        if self.model.myTimeLabel is not None:
            self.model.myTimeLabel.updateTimeLabel()
        self.model.updateWindowTitle()

        # Get current phase before processing
        currentPhase = self.getCurrentPhase()
        
        # Process the useSelector widgets for this next phase/round
        if self.model.userSelector is not None:
            self.model.userSelector.updateOnNewPhase()
        else:
            # If userSelector doesn't exist, update currentPlayer manually based on authorized players
            if isinstance(currentPhase, SGPlayPhase) and currentPhase.authorizedPlayers:
                # Set currentPlayer to the first authorized player
                first_authorized_player = currentPhase.authorizedPlayers[0]
                if isinstance(first_authorized_player, str):
                    self.model.setCurrentPlayer(first_authorized_player)
                else:
                    self.model.setCurrentPlayer(first_authorized_player.name if hasattr(first_authorized_player, 'name') else str(first_authorized_player))

        # Update control panels based on current phase type
        self.updateControlPanelsForCurrentPhase()

        # execute the actions of the phase
        self.getCurrentPhase().execPhase()
        #watchers update
        self.model.checkAndUpdateWatchers()
        #opened graph windows update
        for aGraph in self.model.openedGraphs:
            aGraph.toolbar.refresh_data()

        # The phase handles its own automatic forwarding
        self.getCurrentPhase().handleAutoForward()

    def updateControlPanelsForCurrentPhase(self):
        """Update control panels activation based on current phase type"""
        currentPhase = self.getCurrentPhase()
        
        # Check if we're in a model phase (no authorized players)
        if hasattr(currentPhase, '__class__') and currentPhase.__class__.__name__ == 'SGModelPhase':
            # In model phase, all control panels should be inactive
            for controlPanel in self.model.getControlPanels():
                controlPanel.setActivation(False)
        else:
            # In play phase, only the current player's control panel should be active
            for controlPanel in self.model.getControlPanels():
                is_active = controlPanel.playerName == self.model.currentPlayerName
                controlPanel.setActivation(is_active)

    def isItTheLastPhase(self):
        return (self.currentPhaseNumber + 1) > self.numberOfPhases() 

    def getCurrentPhase(self):
        return self.phases[self.currentPhaseNumber-1]
    
    def numberOfPhases(self):
        return len(self.phases)
                            
    def getNextPhase(self):
        return self.phases[self.currentPhaseNumber]

    def next(self):
        # Victory condition
        self.nextPhase()

    def checkEndGame(self):
        endGame = False
        counter = 0
        for aCond in self.conditionOfEndGame:
            aCond.verifStatus()
            if aCond.endGameRule.displayRefresh == 'instantaneous':
                aCond.updateText()
            if aCond.checkStatus:
                counter = counter+1
                if counter >= aCond.endGameRule.numberRequired:
                    endGame = True
                    break
        if endGame:
            print("Game Over!")
        return endGame
    
    #Update
    def updateEndGame(self):
        for condition in self.conditionOfEndGame:
            condition.updateText()


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

    # To add a new Game Phase

    def newPlayPhase(self, name, activePlayers=None, modelActions=[], authorizedActions=None, autoForwardWhenAllActionsUsed=False, message_auto_forward=True, show_message_box_at_start=False):
        """
        To add a Game Phase in a round.

        args:
            name (str): Name displayed on the TimeLabel
            activePlayers (list): List of players concerned about the phase. Can contain:
                - Player instances (SGPlayer objects)
                - Player names (str) - will be automatically converted to instances
                - 'Admin' (str) - will be converted to the Admin player instance
                - None (default:all users)
            modelActions (list): Actions the model performs at the beginning of the phase (add, delete, move...)
            authorizedActions (list, optional): List of game actions authorized in this phase. Can contain:
                - None (default): all actions are allowed
                - []: no actions are allowed
                - [action1, action2, ...]: only these actions are allowed
            autoForwardWhenAllActionsUsed (bool): Whether to automatically forward to next phase when all players have used their actions
            message_auto_forward (bool): Whether to show a message when automatically forwarding to the next phase
            show_message_box_at_start (bool): Whether to show a message box at the start of the phase
        """
        if activePlayers == None:
            activePlayers = self.model.users
        
        # Convert player names to player instances
        processedPlayers = []
        for player in activePlayers:
            if isinstance(player, str):
                if player == 'Admin':
                    # Handle Admin player
                    adminPlayer = self.model.getAdminPlayer()
                    if adminPlayer:
                        processedPlayers.append(adminPlayer)
                    else:
                        # If no adminPlayer exists, skip it
                        continue
                else:
                    # Handle regular players by name
                    try:
                        playerInstance = self.model.getPlayer(player)
                        processedPlayers.append(playerInstance)
                    except ValueError:
                        # If player not found, skip it
                        print(f"Warning: Player '{player}' not found, skipping from active players")
                        continue
            else:
                # Already an instance, keep as is
                processedPlayers.append(player)
        
        activePlayers = processedPlayers

        aPhase = SGPlayPhase(self, modelActions=modelActions, name=name, authorizedPlayers=activePlayers,
                           authorizedActions=authorizedActions,
                           autoForwardWhenAllActionsUsed=autoForwardWhenAllActionsUsed,
                           message_auto_forward=message_auto_forward,
                           show_message_box_at_start=show_message_box_at_start)
        self.phases = self.phases + [aPhase]
        return aPhase

 # To add a new Phase during which the model will execute some instructions
    def newModelPhase(self,actions=None,condition=None, name='', auto_forward=False, message_auto_forward=True, show_message_box_at_start=False):
        """
        Add a phase during which the model will automatically execute actions.

        Args:
            actions (SGModelAction, lambda function, or list of SGModelAction/lambda function, optional):
                The action(s) to be executed during the phase. Can be a single SGModelAction, a lambda function,
                or a list of either.
            condition (lambda function, optional):
                A function returning a boolean. Actions are performed only if this function returns True.
            name (str, optional):
                Name displayed on the TimeLabel.
            auto_forward (bool, optional):
                If True, this phase will be executed automatically. Default is False.
            message_auto_forward (bool, optional):
                If True, a message will be displayed when auto-forwarding. Default is True.
            show_message_box_at_start (bool, optional):
                If True, a message box will be shown at the start of the phase. Default is False.
        """
        if actions is None:
            actions = []
        modelActions = []
        if isinstance(actions, (SGModelAction,SGModelAction_OnEntities)):
            actions.addCondition(condition)
            modelActions.append((actions))
        elif callable(actions):
            modelActions.append(self.model.newModelAction(actions, condition))
        elif isinstance(actions, list):
            for aAction in actions:
                if isinstance(aAction, SGModelAction):
                    aAction.addCondition(condition)
                    modelActions.append((aAction))
                elif callable(aAction):
                    modelActions.append(
                        self.model.newModelAction(aAction, condition))
                else:
                    raise ValueError("""Syntax error of actions. aAction should be:
                                a lambda function (syntax -> (lambda: instruction)),
                                or an instance of SGModelAction (syntax -> aModel.newModelAction() ) """)
        else:
            raise ValueError("""Syntax error of actions. aAction should be:
                                a lambda function (syntax -> (lambda: instruction)),
                                or an instance of SGModelAction (syntax -> aModel.newModelAction() ) """)

        aPhase = SGModelPhase(self,modelActions=modelActions, name=name,auto_forward=auto_forward,message_auto_forward=message_auto_forward,show_message_box_at_start=show_message_box_at_start)
        self.phases = self.phases + [aPhase]
        return aPhase

    # To verify a number of round
    def verifNumberOfRound(self, aNumber):
        return self.currentRoundNumber == aNumber

    # To verify if the number of round is peer
    def isPeer(self):
        return  (self.currentRoundNumber != 0) and (self.currentRoundNumber % 2 == 0)

    # To verify if the number of round is odd
    def isOdd(self):
        return self.currentRoundNumber % 2 == 1

    # To verify if its the initialization period (round 0)
    def isInitialization(self):
        return self.currentRoundNumber  == 0
    
    def getPlayPhasesForPlayers(self):
        """
        Returns a dictionary that associates each player with their play phases.
        
        Returns:
            dict: Dictionary {player: [list of phases]}
        """
        player_phases = {}
        for phase in self.phases:
            if isinstance(phase, SGPlayPhase) and phase.authorizedPlayers:
                for player in phase.authorizedPlayers:
                    if player not in player_phases:
                        player_phases[player] = []
                    player_phases[player].append(phase)
        return player_phases