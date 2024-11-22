from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
import importlib.util
import sys

#Class who manage the game mechanics of Activation
class SGActivate(SGAbstractAction):
    def __init__(self,entDef,method,number,conditions=[],feedBack=[],conditionOfFeedBack=[],setControllerContextualMenu=False):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack,setControllerContextualMenu)
        if entDef != "model":
            self.name="ActivateAction "+ entDef.entityName
            self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef)
            self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
        self.method=method
    

    def executeAction(self,aTargetEntity,serverUpdate=True):
        method = self.method
        try:
            gameScript = self.logFromModeleur(sys.argv[0])
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
    
    def logFromModeleur(self, fileName):
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