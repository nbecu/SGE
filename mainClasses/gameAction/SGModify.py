from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from PyQt5.QtWidgets import QInputDialog 

#Class who manage the game mechanics of Update
class SGModify(SGAbstractAction):
    def __init__(self,type,dictNewValues,number,conditions=[],feedbacks=[],conditionsOfFeedback=[],nameToDisplay=None,setControllerContextualMenu=False,setOnController=True, writeAttributeInLabel=False):
        super().__init__(type,number,conditions,feedbacks,conditionsOfFeedback,nameToDisplay,setControllerContextualMenu,setOnController)
        self.dictNewValues=dictNewValues
        self.entityDef=type
        self.att = list(self.dictNewValues.keys())[0]  #  Get dict key
        self.value = self.dictNewValues[self.att]  # Get associate value
        self.nameToDisplay = (
            f"{self.att}→{self.value}" if nameToDisplay is None and writeAttributeInLabel
            else f"{self.value}" if nameToDisplay is None
            else nameToDisplay
        )
        self.actionType="Modify"
        self.addCondition(lambda aTargetEntity: aTargetEntity.type == self.targetType)
        self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
        self.addCondition(lambda aTargetEntity: aTargetEntity.value(self.att) != self.value)
   

    def executeAction(self, aTargetEntity):
        aTargetEntity.setValue(self.att,self.value)
        return aTargetEntity

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            aList = []
            for aAtt, aValue in self.dictNewValues.items():
                aColor = self.targetType.getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(aAtt,aValue)
                # If it's a border color, it returns a dict, not a color.
                if isinstance(aColor,dict):
                    borderColorAndWidth = aColor
                    aColor =  self.targetType.defaultShapeColor
                    #todo Modifs pour MTZC pour que ce soit plus simple
                    aList.append(SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,aAtt,aValue,isBorderItem = True, borderColorAndWidth = borderColorAndWidth , gameAction=self))
                # If not, its a shape color
                else:
                    #todo Modifs pour MTZC pour que ce soit plus simple
                    aList.append(SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,aAtt,aValue,gameAction=self))

            return aList

# SGModifyActionWithDialog is a apecial ModifyAction that opens a dialog to ask for the value to use
class SGModifyActionWithDialog(SGModify):
    """Special ModifyAction that opens a dialog to ask for the value to use"""
    
    def __init__(self, entityDef, attribute, aNumber='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], aNameToDisplay=None, setControllerContextualMenu=False, writeAttributeInLabel=False):
        # Initialize with a placeholder value to avoid IndexError
        placeholder_dict = {attribute: "placeholder"}
        super().__init__(entityDef, placeholder_dict, aNumber, conditions, feedbacks, conditionsOfFeedback, aNameToDisplay, setControllerContextualMenu, writeAttributeInLabel)
        self.dynamicAttribute = attribute
        self.nameToDisplay = f"Modify {attribute} (ask value)"
        
    def executeAction(self, aTargetEntity):
        """Override to show dialog and get value from user"""
        # Show input dialog to get the value
        value, ok = QInputDialog.getText(None, f"Modify {self.dynamicAttribute}", 
                                        f"Enter new value for {self.dynamicAttribute}:")
        
        if ok and value:
            # Set the value directly
            aTargetEntity.setValue(self.dynamicAttribute, value)
            return aTargetEntity
        return aTargetEntity
    
    # ============================================================================
    # EXPORT INTERFACE METHODS - SGModify specific implementations
    # ============================================================================
    
    def getActionDetails(self):
        """
        Specific details for SGModify
        """
        details = super().getActionDetails()
        details["attributes_to_modify"] = self.dictNewValues
        details["primary_attribute"] = self.att if hasattr(self, 'att') else 'N/A'
        details["primary_value"] = self.value if hasattr(self, 'value') else 'N/A'
        return details
    
    def _getSpecificActionInfo(self):
        """
        Get specific modification information
        """
        if hasattr(self, 'att') and hasattr(self, 'value'):
            return f"Modify: {self.att} -> {self.value}"
        return None