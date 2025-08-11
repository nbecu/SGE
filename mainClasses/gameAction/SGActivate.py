from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
import importlib.util
import sys

#Class who manage the game mechanics of Activation
class SGActivate(SGAbstractAction):
    def __init__(self,entDef,method,number,conditions=[],feedBack=[],conditionOfFeedBack=[],aNameToDisplay=None,setControllerContextualMenu=False,setOnController=True):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack,aNameToDisplay,setControllerContextualMenu,setOnController)
        if self.targetEntDef != "model":
            if aNameToDisplay is None :self.name="ActivateAction "+ entDef.entityName
            else: self.name=aNameToDisplay
            self.actionType="Activate"
            self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef)
            self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
        else:
            if aNameToDisplay is None :self.name="ActivateAction"
            else: self.name=aNameToDisplay
            self.actionType="Activate"
        self.method=method
    

    def executeAction(self,aTargetEntity,serverUpdate=True):
        method = self.method
        if callable(method):
            #count the number of arguments
            nbArguments = method.__code__.co_argcount
            if nbArguments == 0:
                method() #execute the method with no arguments
            elif nbArguments == 1:
                method(aTargetEntity)
            else:
                raise ValueError('the callable method as several arguments')
            return

        try:
            gameScript = self.logFromModeler(sys.argv[0])
            if hasattr(gameScript, method):
                func = getattr(gameScript, method)
                if callable(func):
                    func(aTargetEntity)
                    if serverUpdate: self.updateServer_gameAction_performed(aTargetEntity)
                else:
                    print(f"{method} n'est pas une fonction exécutable.")
            else:
                print(f"Fonction {method} introuvable dans le script.")
        except FileNotFoundError as e:
            print(e)
    
    def logFromModeler(self, fileName):
        # Import the method by name from game file
        spec=importlib.util.spec_from_file_location("GameFile",fileName)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if module is None: raise FileNotFoundError(f"File named {fileName} not found")
        return module
        
    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            aColor = self.targetEntDef.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol','activate',self.targetEntDef,aColor,gameAction=self)]