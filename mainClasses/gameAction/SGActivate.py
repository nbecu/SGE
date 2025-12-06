from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from PyQt5.QtCore import Qt
import importlib.util
import sys

#Class who manage the game mechanics of Activation
class SGActivate(SGAbstractAction):
    context_menu_icon = "⚡"  # Icon for context menu
    def __init__(self, type, method, uses_per_round, conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        super().__init__(type, uses_per_round, conditions, feedbacks, conditionsOfFeedback, label=label, action_controler=action_controler)
        if self.targetType != "model":
            if self.nameToDisplay is None:
                self.nameToDisplay = "activate" #("activate "+ type.name)
            self.actionType="Activate"
            self.addCondition(lambda aTargetEntity: aTargetEntity.type == self.targetType)
            self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
        else:
            if self.nameToDisplay is None:
                self.nameToDisplay = "activate"
            self.actionType="Activate"
        self.method=method
    

    def executeAction(self,aTargetEntity,serverUpdate=True):
        method = self.method
        if callable(method):
            from mainClasses.SGExtensions import execute_callable_with_entity
            execute_callable_with_entity(method, aTargetEntity)
            return

    
    def logFromModeler(self, fileName):
        # Import the method by name from game file
        spec=importlib.util.spec_from_file_location("GameFile",fileName)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if module is None: raise FileNotFoundError(f"File named {fileName} not found")
        return module
        
    def generateLegendItems(self,aControlPanel):
        # Use action_controler["controlPanel"] to determine if action should appear in ControlPanel
        if self.action_controler.get("controlPanel", True):
            # Handle model actions (targetType == 'model')
            if self.targetType == 'model':
                # Use Activate icon for model actions
                icon = self.context_menu_icon
                displayText = f"{icon} {self.nameToDisplay}"
                # Use a default color (gray) for model actions
                return [SGLegendItem(aControlPanel,'symbol',displayText,None,Qt.gray,gameAction=self)]
            else:
                # Regular entity actions
                aColor = self.targetType.defaultShapeColor
                return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,gameAction=self)]
    
    # ============================================================================
    # EXPORT INTERFACE METHODS - SGActivate specific implementations
    # ============================================================================
    
    def getActionDetails(self):
        """
        Specific details for SGActivate
        """
        details = super().getActionDetails()
        details["method_name"] = getattr(self.method, '__name__', str(self.method)) if callable(self.method) else str(self.method)
        return details
    
    def _getSpecificActionInfo(self):
        """
        Get specific activation information
        """
        method_name = getattr(self.method, '__name__', str(self.method)) if callable(self.method) else str(self.method)
        return f"Activate: {method_name}"