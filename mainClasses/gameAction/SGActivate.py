from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
import importlib.util
import sys

#Class who manage the game mechanics of Activation
class SGActivate(SGAbstractAction):
    def __init__(self,type,method,number,conditions=[],feedbacks=[],conditionsOfFeedback=[],aNameToDisplay=None,setControllerContextualMenu=False,setOnController=True):
        super().__init__(type,number,conditions,feedbacks,conditionsOfFeedback,aNameToDisplay,setControllerContextualMenu,setOnController)
        if self.targetType != "model":
            self.nameToDisplay= aNameToDisplay or "⚡activate" #("activate "+ type.name)
            self.actionType="Activate"
            self.addCondition(lambda aTargetEntity: aTargetEntity.type == self.targetType)
            self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
        else:
            self.nameToDisplay= aNameToDisplay or "activate"
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
        if self.setControllerContextualMenu == False:
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