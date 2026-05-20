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

        self.model.dataRecorder.calculateStepStats()

        if self.checkEndGame():
            return

        self._advanceCounters()

        if self.model.myTimeLabel is not None:
            self.model.myTimeLabel.updateTimeLabel()
        self.model.updateWindowTitle()

        currentPhase = self.getCurrentPhase()
        self._updateCurrentPlayer(currentPhase)
        self.updateControlPanelsForCurrentPhase()
        self._resetActionPointsForPhase(currentPhase)
        self._executeAndRefresh()

    def _advanceCounters(self):
        """Advance round/phase counters and reset round-level state when a new round starts."""
        if self.currentRoundNumber == 0:
            self.currentRoundNumber = 1
            self.currentPhaseNumber = 1
        elif self.isItTheLastPhase():
            self.currentRoundNumber += 1
            self.currentPhaseNumber = 1
            for action in self.model.getAllGameActions():
                action.reset()
            self._resetActionPointsForAllPlayers("round")
            # Ensures countdown displays are updated correctly when entering the final round
            for aCond in self.conditionOfEndGame:
                if aCond.endGameRule.displayRefresh == 'instantaneous':
                    aCond.updateText()
        else:
            self.currentPhaseNumber += 1

    def _updateCurrentPlayer(self, currentPhase):
        """Sync the active player for the new phase via userSelector or direct assignment."""
        if self.model.userSelector is not None:
            self.model.userSelector.updateOnNewPhase()
        elif isinstance(currentPhase, SGPlayPhase) and currentPhase.authorizedPlayers:
            first_player = currentPhase.authorizedPlayers[0]
            name = first_player if isinstance(first_player, str) else getattr(first_player, 'name', str(first_player))
            self.model.setCurrentPlayer(name)

    def _executeAndRefresh(self):
        """Execute the current phase then refresh watchers, graphs, and auto-forward logic."""
        self.getCurrentPhase().execPhase()
        self.model.checkAndUpdateWatchers()
        for aGraph in self.model.openedGraphs:
            aGraph.toolbar.refresh_data()
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

    def _resetActionPointsForAllPlayers(self, mode):
        try:
            for player in self.model.players.values():
                if hasattr(player, "resetActionPoints"):
                    player.resetActionPoints(mode)
        except Exception:
            pass

    def _resetActionPointsForPhase(self, phase):
        try:
            if isinstance(phase, SGPlayPhase):
                for player in phase.authorizedPlayers:
                    if hasattr(player, "resetActionPoints"):
                        player.resetActionPoints("phase")
        except Exception:
            pass

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
        endGameRule = None
        for aCond in self.conditionOfEndGame:
            aCond.verifStatus()
            # Note: Auto-show is now handled in byCalcType() when condition is first detected
            # This ensures the widget appears immediately when condition is met, even with delay_rounds
            if aCond.endGameRule.displayRefresh == 'instantaneous':
                aCond.updateText()
            if aCond.checkStatus:
                counter = counter+1
                if counter >= aCond.endGameRule.numberRequired:
                    endGame = True
                    endGameRule = aCond.endGameRule
                    break
        if endGame:
            print("Game Over!")
            # Activate end game display (banner and/or highlight)
            endGameRule.activateEndGameDisplay()
        return endGame
    
    #Update
    def updateEndGame(self):
        for condition in self.conditionOfEndGame:
            condition.updateText()


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

    # To add a new Game Phase

    def newPlayPhase(self, name, activePlayers=None, modelActions=[], authorizedActions=None, autoForwardWhenAllActionsUsed=False, autoForwardWhenNoMoreActionPoints=False, message_auto_forward=True, show_message_box_at_start=False):
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
            autoForwardWhenNoMoreActionPoints (bool): Whether to automatically forward when all players have no action points
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

        aPhase = SGPlayPhase(
            self,
            modelActions=modelActions,
            name=name,
            authorizedPlayers=activePlayers,
            authorizedActions=authorizedActions,
            autoForwardWhenAllActionsUsed=autoForwardWhenAllActionsUsed,
            autoForwardWhenNoMoreActionPoints=autoForwardWhenNoMoreActionPoints,
            message_auto_forward=message_auto_forward,
            show_message_box_at_start=show_message_box_at_start
        )
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