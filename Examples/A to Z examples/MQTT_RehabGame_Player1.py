import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


myModel = SGModel(
    900, 900, x=5, windowTitle="dev project : Rehab Game - Player 1", typeOfLayout="grid")

aGrid = myModel.newGrid(7, 7, "square", size=60, gap=2,
                        name='grid1')  # ,posXY=[20,90]
Cell.setEntities("Resource", 2)
Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("Resource", 3, 7)
Cell.setRandomEntities("Resource", 1, 3)
Cell.setRandomEntities("Resource", 0, 8)
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)


Cell.newPov("Resource", "Resource", {
               3: Qt.darkGreen, 2: Qt.green, 1: Qt.yellow, 0: Qt.white})
myModel.newBorderPov("ProtectionLevel", "ProtectionLevel", {
                     "Reserve": Qt.magenta, "Free": Qt.black})

Workers = myModel.newAgentSpecies(
    "Workers", "triangleAgent1", uniqueColor=Qt.black)
Birds = myModel.newAgentSpecies(
    "Birds", "triangleAgent2", uniqueColor=Qt.yellow)

aWorker = myModel.newAgentAtCoords(aGrid,Workers,5,2)


globalLegend = myModel.newLegend("Global Legend", showAgentsWithNoAtt=True)

Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newCreateAction(Workers, 20))
    # le paramètre aDictOfAcceptedValue est mal nommé. Il faudrait l'appeler dictAttributes
Player1.addGameAction(myModel.newDeleteAction(Workers, "infinite"))
    # Pourquoi une deleteAction peut accepter aDictOfAcceptedValue ? (je crois que ce paramètre ne serta à rien)
    # "infinite" doit etre la valeur par défaut de aNumber
Player1.addGameAction(myModel.newUpdateAction('Cell', 3, {"Resource": 3}))
    # le paramètre aDictOfAcceptedValue est mal nommé. Il faudrait l'appeler dictAttributes
    #le paramètre aNumber doit être placé après dictAttributes
Player1.addGameAction(myModel.newMoveAction(Workers, 1))
    # Pourquoi une moveAction peut accepter aDictOfAcceptedValue ? (je crois que ce paramètre ne serta à rien)
    # Y'a un truc qui cloche entre feedback et feedbackAgent. Si l'actuel feeback concerne la cellule (a priori la cellule de destination), alors il faut inverser les noms des attributs : feedbackAgent doit etre feedback et et l'actuel feedback doit etre feedbackOnDestinationCell.     Si possible, il faudrait intégrer aussi un feedbackOnOriginCell
Player1ControlPanel = Player1.newControlPanel("Player 1 Actions", showAgentsWithNoAtt=True)

Player2 = myModel.newPlayer("Player 2")
Player2.addGameAction(myModel.newUpdateAction("Cell", 3, {"ProtectionLevel": "Reserve"}))
Player2.addGameAction(myModel.newUpdateAction("Cell", "infinite", {"ProtectionLevel": "Free"}))
Player2ControlPanel = Player2.newControlPanel("Actions du Joueur 2")

myModel.timeManager.newGamePhase('Phase 1', [Player1,Player2])
myModel.timeManager.newModelPhase([lambda: aGrid.setRandomCell("Resource",3),lambda: Cell.setRandomEntities("Resource",1,3)])
aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("Resource",3,2,condition=(lambda x: x.value("Resource") not in [0,1] )))
myModel.timeManager.newModelPhase(aModelAction2)
aModelAction4=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.round()==2)

GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.red)
myModel.currentPlayer = 'Player 1'

userSelector=myModel.newUserSelector()

TextBox = myModel.newTextBox(
    title='Début du jeu', textToWrite="Bonjour et bienvenue dans RehabGame !")

TextBox.addText("J'espère que vous allez bien!!!", toTheLine=True)

globalScore=myModel.newSimVariable(0,"Global Score")
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.red)
i1 = DashBoard.addIndicator("sumAtt", 'cell', attribute='Resource',color=Qt.black)
i2 = DashBoard.addIndicator("avgAtt", 'cell', attribute='Resource',color=Qt.black)
i3 = DashBoard.addIndicatorOnSimVariable(globalScore)
DashBoard.showIndicators()
aModelAction4.addFeedback(lambda: i3.setResult(i3.result + 5))
myModel.timeManager.newModelPhase(aModelAction4)


endGameRule = myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Resource equal to 90")
endGameRule.addEndGameCondition_onEntity(
    "cell1-5", 'Resource', "greater", 2, name="Cell 1-5 Resource is greater than 2",aGrid=aGrid)
endGameRule.showEndGameConditions()


myModel.launch_withMQTT("Instantaneous") # https://mosquitto.org/download/
    ## ATTENTION : il y a un problème ds le fonctionnement en mqtt
    # Premier problème : le nbUse des gameActions  n'est pas envoyé aux clients
    #        du coup, si un client passe le tour (ce qui remet les nbUSe à zéro), les autres clients eux n'ont pas  leur nbUse remis à zero
    # Deuxième problème : si plusieurs clients sont set sur le meme user, alors la maj ne se fait.
    #      C'est un soucis car ca veut dire qu'il y a une confusion entre le user et le client
    #           le client c'est l'instance du modèle qui est en train de tourner. 
    #           le user c'est le role (ou plutôt le 'personnage joueur') qui est endossé par le client, et il est autorisé de pouvoir changer de role sur un meme client
    #                              de meme il est possible que plusieurs client partagent le meme user (le meme 'personnage joueur')
    #           du coup, le test qui empeche la maj de se faire sur l'instance du modèle qui vient de lancer une maj, ne doit pas etre un tst sur 'user' mais un test sur le client (sur l'instance du modèle)

sys.exit(monApp.exec_())
