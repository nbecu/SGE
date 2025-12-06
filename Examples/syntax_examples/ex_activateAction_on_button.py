import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])



myModel=SGModel(340,300)
myModel.displayTimeInWindowTitle()

player_Clara = myModel.newPlayer('Clara',attributesAndValues={'foo':5})
player_Clara.setValue('score',0)
myModel.setCurrentPlayer('Clara')
PlayPhase = myModel.newPlayPhase('Play phase',[player_Clara])


dashboard = myModel.newDashBoard(title='Clara attributes')
dashboard.addIndicatorOnEntity(player_Clara,"score",title='Clara score')
dashboard.addIndicatorOnEntity(player_Clara,'foo',title='Clara foo')

textBox=myModel.newTextBox(width=240, height=130, chronologicalOrder=False)


myModel.newActivateAction( method = lambda : textBox.addText('activateAction on button\ntest text'),
                           action_controler={"button":True, "buttonPosition":(250,100)},
                           label="Test me")


activateScore=myModel.newActivateAction( method = lambda : player_Clara.incValue('score',1),
                                         action_controler={"contextMenu":True},label="Score+1")
player_Clara.addGameAction(activateScore)

activatePrint=myModel.newActivateAction( method = lambda : textBox.addText(f"activateAction on contextual menu.\nClara foo = {player_Clara.getValue('foo')}"),
                                         action_controler={"contextMenu":True},label="Write foo")
player_Clara.addGameAction(activatePrint)

def setFooValue():
    """Ask user for a new value for foo and set it"""
    value, ok = QInputDialog.getInt(None, "Set foo", "Enter new value for foo:", 
                                     player_Clara.getValue('foo'), 0, 1000, 1)
    if ok:
        player_Clara.setValue('foo', value)

setFoo=myModel.newActivateAction(   method = setFooValue,
                                    action_controler={"contextMenu":True},label="Set foo")
player_Clara.addGameAction(setFoo)

cp=player_Clara.newControlPanel("Clara actions")

myModel.applyLayoutConfig("ex_activateAction_onButton")  


myModel.launch() 
sys.exit(monApp.exec_())
