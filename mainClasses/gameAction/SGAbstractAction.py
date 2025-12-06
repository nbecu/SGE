# from mainClasses.SGAgent import SGAgent  # Commented to avoid circular import
from mainClasses.SGCell import SGCell
from mainClasses.SGTimePhase import *
from math import inf
import copy
from datetime import datetime

#Class who manage the game mechanics of Update
class SGAbstractAction():
    IDincr=0
    instances = []
    action_id_counter = 0  # Global shared counter for execution order
    context_menu_icon = "▶️ "  # Default icon for context menu (can be overridden by subclasses)
    def __init__(self, type, number, conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        """
        Initialize an abstract action
        
        Args:
            type: The target entity type or model
            number: Number of times the action can be used
            conditions: List of conditions
            feedbacks: List of feedback actions
            conditionsOfFeedback: List of conditions for feedbacks
            label: Display label for the action
            action_controler: Dict specifying interaction modes. Defaults:
                - controlPanel: True (always True by default)
                - contextMenu: False
                - button: False (only for Activate)
                - directClick: False (True by default for Flip)
        """
        self.id=self.nextId()
        self.__class__.instances.append(self)
        # print('new gameAction: '+str(self.id)) # To test
        from mainClasses.SGModel import SGModel  # Local import to avoid circular import
        if isinstance(type, SGModel):
            self.targetType='model'
            self.model=type
        else:
            self.targetType=type
            self.model=self.targetType.model 
        self.number = inf if number in ("infinite", None, inf) else number
        
        self.numberUsed=0
        self.totalNumberUsed=0
        self.conditions=copy.deepcopy(conditions) #Is is very important to use deepcopy becasue otherwise conditions are copied from one GameAction to another
                                                 # We should check that this does not ahppen as well for feedbacks and conditionsOfFeedback 
        self.feedbacks=copy.deepcopy(feedbacks)
        self.conditionsOfFeedback=copy.deepcopy(conditionsOfFeedback)
        
        # Handle action_controler
        if action_controler is None:
            action_controler = {}
        
        # Set default values for action_controler
        # Note: directClick defaults will be set by subclasses (Flip=True by default)
        self.action_controler = {
            "controlPanel": action_controler.get("controlPanel", True),  # Always True by default
            "contextMenu": action_controler.get("contextMenu", False),
            "button": action_controler.get("button", False),  # False by default
            "directClick": action_controler.get("directClick", False)  # False by default, will be overridden by subclasses if needed
        }
        
        # Set display label
        self.nameToDisplay = label
        
        #Define variables to handle the history 
        self.history={}
        self.history["performed"]=[]    

    def nextId(self):
        SGAbstractAction.IDincr +=1
        return SGAbstractAction.IDincr   
    
    def getNextActionId(self):
        """
        Generate the next action identifier for execution order
        
        Returns:
            int: Unique action identifier
        """
        SGAbstractAction.action_id_counter += 1
        return SGAbstractAction.action_id_counter
    
    #Function which increment the number of use
    def incNbUsed(self):
        self.numberUsed += 1
        self.totalNumberUsed += 1


    def perform_with(self,aTargetEntity,serverUpdate=True): #The arg aParameterHolder has been removed has it is never used and it complicates the updateServer
        # print(f"action {self.name} is performed")
        if self.checkAuthorization(aTargetEntity):
            resAction = self.executeAction(aTargetEntity)
            if self.feedbacks:
                aFeedbackTarget = self.chooseFeedbackTargetAmong([aTargetEntity,resAction]) # Previously Three choices aTargetEntity,aParameterHolder,resAction
                if self.checkFeedbackAuhorization(aFeedbackTarget):
                    resFeedback = self.executeFeedbacks(aFeedbackTarget)
            else : resFeedback = None
            self.incNbUsed()
            self.savePerformedActionInHistory(aTargetEntity, resAction, resFeedback)

            if serverUpdate: self.updateServer_gameAction_performed(aTargetEntity)

            if not self.model.timeManager.isInitialization():
                self.model.timeManager.getCurrentPhase().handleAutoForward()

            #commented because unsued -  return resAction if not self.feedbacks else [resAction,resFeedback]
        # else:
        #     return False

    #Function to test if the game action can be used

    def canBeUsed(self):
        if self.model.timeManager.numberOfPhases()==0:
            return True
        if self.model.timeManager.isInitialization():
            # During initialization, only Admin can use actions
            # Check if currentPlayer is defined before accessing it
            try:
                currentPlayer = self.model.getCurrentPlayer()
                if not currentPlayer.isAdmin:
                    # Show warning to non-admin users during initialization
                    self.model.newWarningPopUp(
                        "Action Not Available",
                        "Game actions cannot be used during the initialization phase.\n\n"
                        "Please proceed to the next turn to use actions."
                    )
                return currentPlayer.isAdmin
            except ValueError:
                # Current player not defined yet, only Admin actions should work
                # This is a temporary state during initialization
                return False
        if isinstance(self.model.timeManager.phases[self.model.phaseNumber()-1],SGModelPhase):#If this is a ModelPhase, as default players can't do actions
            # TODO add a facultative permission 
            return False
        if isinstance(self.model.timeManager.phases[self.model.phaseNumber()-1],SGPlayPhase):#If this is a PlayPhase, as default players can do actions
            player=self.model.getCurrentPlayer()
            if player in self.model.timeManager.phases[self.model.phaseNumber()-1].authorizedPlayers:
                res = True
            else:
                return False
            # TODO add a facultative restriction 
        if self.numberUsed >= self.number:
            return False
        return True
    
    def checkAuthorization(self,aTargetEntity):
        if not self.canBeUsed():
            return False
        res = True
        for aCondition in self.conditions:
            res = res and (aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(aTargetEntity))
        return res

    #Function to test if the action feedback 
    def checkFeedbackAuhorization(self,aFeedbackTarget):
        res = True 
        for aCondition in self.conditionsOfFeedback:
            res = res and aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(aFeedbackTarget)
        return res
    
    def chooseFeedbackTargetAmong(self,listOfPossibleFedbackTarget):
        return listOfPossibleFedbackTarget[0]


    def executeFeedbacks(self, feddbackTarget):
        listOfRes = []
        for aFeedback in self.feedbacks:
            res = aFeedback() if aFeedback.__code__.co_argcount == 0 else aFeedback(feddbackTarget)
            listOfRes.append(res)
        if not listOfRes: raise ValueError('why is this method called when the list of feedbaks is  empty')
        return res if len(listOfRes) == 1 else listOfRes
   
    def savePerformedActionInHistory(self,aTargetEntity, resAction, resFeedback):
        # Generate temporal and identification information
        timestamp = datetime.now().isoformat()
        id_action = self.getNextActionId()
        session_id = self.model.session_id
        
        self.history["performed"].append([self.model.timeManager.currentRoundNumber,
                                          self.model.timeManager.currentPhaseNumber,
                                          self.numberUsed,
                                          aTargetEntity,
                                          resAction,
                                          resFeedback,
                                          timestamp,
                                          id_action,
                                          session_id])


    def updateServer_gameAction_performed(self, *args):
        if self.model.mqttMajType == "Instantaneous":
            dict ={}
            dict['class_name']=self.__class__.__name__
            dict['id']=self.id
            dict['method']='perform_with'
            self.model.mqttManager.buildExeMsgAndPublishToBroker('gameAction_performed',dict, *args)
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
        
    def reset(self):
        self.numberUsed=0
    
    def addCondition(self,aCondition):
        self.conditions.append(aCondition)
    
    def addFeedback(self,aFeedback):
        self.feedbacks.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionsOfFeedback.append(aCondition)
        
    def getNbRemainingActions(self):
        return self.number-self.numberUsed
        # thePlayer.remainActions[self.name]=remainNumber
    
    def getGraphIdentifier(self):
        """Generate unique identifier for graphs, showing ID only when necessary"""
        if hasattr(self.targetType, 'name'):
            base_name = f"{self.targetType.name}_{self.nameToDisplay}"
        else:
            base_name = f"model_{self.nameToDisplay}"
        
        # Check if there are other actions with the same base name (static method to avoid recursion)
        if self._hasConflictingNames(base_name):
            return f"{base_name}_{self.id}"
        else:
            return base_name
    
    @classmethod
    def _hasConflictingNames(cls, base_name):
        """Static method to check for name conflicts without recursion"""
        count = 0
        for action in cls.instances:
            if hasattr(action, 'targetType') and hasattr(action, 'nameToDisplay'):
                if hasattr(action.targetType, 'name'):
                    action_base = f"{action.targetType.name}_{action.nameToDisplay}"
                else:
                    action_base = f"model_{action.nameToDisplay}"
                
                if action_base == base_name:
                    count += 1
                    if count > 1:  # More than one action with this name
                        return True
        return False
    
    # ============================================================================
    # EXPORT INTERFACE METHODS
    # ============================================================================
    
    def getFormattedHistory(self):
        """
        Return formatted history with explicit keys
        
        Returns:
            list: List of dictionaries with formatted history
        """
        formatted_history = []
        
        for entry in self.history["performed"]:
            # Structure: [round, phase, usage_count, target_entity, res_action, res_feedback, timestamp, id_action, session_id]
            formatted_entry = {
                "session_id": entry[8],
                "id_action": entry[7],
                "timestamp": entry[6],
                "round": entry[0],
                "phase": entry[1], 
                "usage_count": entry[2],
                "target_entity": entry[3],
                "result_action": entry[4],
                "result_feedback": entry[5]
            }
            formatted_history.append(formatted_entry)
        
        return formatted_history

    def getExportInfo(self):
        """
        Common interface for action information export
        
        Returns:
            dict: Complete action information for export (flattened structure)
        """
        # Get the detailed information
        target_entity_info = self.getTargetEntityInfo()
        action_details = self.getActionDetails()
        usage_info = self.getUsageInfo()
        
        # Flatten the structure by merging all sub-objects into the main object
        export_info = {
            "action_id": self.id,
            "action_class": self.__class__.__name__,
            "action_type": getattr(self, 'actionType', 'Unknown'),
            "action_name": getattr(self, 'nameToDisplay', f"Action_{self.id}")
        }
        
        # Add target entity info fields directly
        if target_entity_info:
            export_info.update({
                "target_entity_type": target_entity_info.get("type", "N/A"),
                "target_entity_category": target_entity_info.get("category", "N/A"),
                "target_entity_name": target_entity_info.get("name", "N/A")
            })
        
        # Add action-specific fields (attribute and value) right after target_entity_name
        # Direct access to avoid Python module caching issues
        if self.__class__.__name__ == 'SGModify':
            if hasattr(self, 'att') and hasattr(self, 'value'):
                export_info.update({
                    "attribute": str(self.att),
                    "value": str(self.value)
                })
        elif self.__class__.__name__ == 'SGCreate':
            if hasattr(self, 'dictAttributs') and self.dictAttributs:
                # Pour les actions Create, prendre le premier attribut
                first_attr = list(self.dictAttributs.keys())[0]
                export_info.update({
                    "attribute": str(first_attr),
                    "value": str(self.dictAttributs[first_attr])
                })
        
        # Add action details fields directly
        if action_details:
            export_info.update(action_details)
        
        # Add usage info fields directly
        if usage_info:
            export_info.update(usage_info)
        
        # Add history at the end (for all action types)
        export_info["history"] = self.getFormattedHistory()
        
        return export_info
    
    def getTargetEntityInfo(self):
        """
        Target entity information - generic method
        
        Returns:
            dict: Target entity information
        """
        if hasattr(self, 'targetType'):
            if self.targetType == 'model':
                return {
                    "type": "model",
                    "name": "Model",
                    "category": "Model"
                }
            elif hasattr(self.targetType, 'name'):
                return {
                    "type": self.targetType.__class__.__name__,
                    "name": self.targetType.name,
                    "category": self.targetType.category() if hasattr(self.targetType, 'category') else "Unknown"
                }
        
        return {
            "type": "Unknown",
            "name": "Unknown",
            "category": "Unknown"
        }
    
    def getActionDetails(self):
        """
        Action-specific details - to be redefined in subclasses
        
        Returns:
            dict: Action-specific details
        """
        # Default generic implementation
        return {
            "conditions_count": len(self.conditions) if hasattr(self, 'conditions') else 0,
            "feedbacks_count": len(self.feedbacks) if hasattr(self, 'feedbacks') else 0
        }
    
    def getUsageInfo(self):
        """
        Action usage information
        
        Returns:
            dict: Usage information
        """
        return {
            "max_uses": self.number if self.number != float('inf') else "infinite",
            "total_uses": self.totalNumberUsed
        }
    
    def formatActionDetailsForCSV(self):
        """
        Format action details for CSV export using Template Method pattern
        
        Returns:
            str: Formatted details for CSV
        """
        details_parts = []
        
        # Specific information (implemented by subclasses)
        specific_info = self._getSpecificActionInfo()
        if specific_info:
            details_parts.append(specific_info)
        
        # Common information (centralized)
        details_parts.extend(self._getCommonActionInfo())
        
        return " | ".join(details_parts) if details_parts else "No details"
    
    def _getSpecificActionInfo(self):
        """
        Get specific action information - to be implemented by subclasses
        
        Returns:
            str: Specific action information, or None if not applicable
        """
        return None
    
    def _getCommonActionInfo(self):
        """
        Get common action information shared by all action types
        
        Returns:
            list: List of common information strings
        """
        common_parts = []
        
        if self.action_controler.get("contextMenu", False):
            common_parts.append("(contextual menu)")
        
        if len(getattr(self, 'conditions', [])) > 0:
            common_parts.append(f"({len(self.conditions)} conditions)")
        
        if len(getattr(self, 'feedbacks', [])) > 0:
            common_parts.append(f"({len(self.feedbacks)} feedbacks)")
        
        return common_parts

