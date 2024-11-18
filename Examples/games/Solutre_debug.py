import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1100,550, windowTitle="Solutré", typeOfLayout ="grid", x=5,y=5)
#* --------------------------
#* Lecture des data
#* --------------------------
data_inst=pd.read_excel("./data/solutre_hex_inst.xlsx")
data_act=pd.read_excel("./data/solutre_hex_act.xlsx")

#* --------------------------
#* Construction des plateaux
#* --------------------------
def constructPlateau():
    Plateau=myModel.newCellsOnGrid(8,8,"hexagonal",size=80,gap=2,name="Plateau",backGroundImage=QPixmap("./icon/solutre/fond_solutre.jpg"))
    Plateau.deleteEntity(Plateau.getEntity(1,1))
    Plateau.deleteEntity(Plateau.getEntity(2,1))
    Plateau.deleteEntity(Plateau.getEntity(3,1))
    Plateau.deleteEntity(Plateau.getEntity(4,1))
    Plateau.deleteEntity(Plateau.getEntity(5,1))
    Plateau.deleteEntity(Plateau.getEntity(8,1))
    Plateau.deleteEntity(Plateau.getEntity(1,2))
    Plateau.deleteEntity(Plateau.getEntity(2,2))
    Plateau.deleteEntity(Plateau.getEntity(3,2))
    Plateau.deleteEntity(Plateau.getEntity(8,2))
    Plateau.deleteEntity(Plateau.getEntity(1,3))
    Plateau.deleteEntity(Plateau.getEntity(2,3))
    Plateau.deleteEntity(Plateau.getEntity(1,5))
    Plateau.deleteEntity(Plateau.getEntity(1,6))
    Plateau.deleteEntity(Plateau.getEntity(7,6))
    Plateau.deleteEntity(Plateau.getEntity(8,6))
    Plateau.deleteEntity(Plateau.getEntity(1,7))
    Plateau.deleteEntity(Plateau.getEntity(2,7))
    Plateau.deleteEntity(Plateau.getEntity(6,7))
    Plateau.deleteEntity(Plateau.getEntity(7,7))
    Plateau.deleteEntity(Plateau.getEntity(8,7))
    Plateau.deleteEntity(Plateau.getEntity(1,8))
    Plateau.deleteEntity(Plateau.getEntity(2,8))
    Plateau.deleteEntity(Plateau.getEntity(4,8))
    Plateau.deleteEntity(Plateau.getEntity(5,8))
    Plateau.deleteEntity(Plateau.getEntity(6,8))
    Plateau.deleteEntity(Plateau.getEntity(7,8))
    Plateau.deleteEntity(Plateau.getEntity(8,8))
    Plateau.getEntity(3,3).setValue("zone","Naturaliste")
    Plateau.getEntity(1,4).setValue("zone","Naturaliste")
    Plateau.getEntity(2,4).setValue("zone","Naturaliste")
    Plateau.getEntity(3,4).setValue("zone","Naturaliste")
    Plateau.getEntity(2,5).setValue("zone","Naturaliste")
    Plateau.getEntity(3,5).setValue("zone","Naturaliste")
    Plateau.getEntity(4,5).setValue("zone","Naturaliste")
    Plateau.getEntity(2,6).setValue("zone","Naturaliste")
    Plateau.getEntity(4,6).setValue("zone","Naturaliste")
    Plateau.getEntity(3,7).setValue("zone","Naturaliste")
    Plateau.getEntity(4,7).setValue("zone","Naturaliste")
    Plateau.getEntity(5,7).setValue("zone","Naturaliste")
    Plateau.getEntity(3,8).setValue("zone","Naturaliste")
    Plateau.getEntity(6,1).setValue("zone","Viticulteur")
    Plateau.getEntity(7,1).setValue("zone","Viticulteur")
    Plateau.getEntity(4,2).setValue("zone","Viticulteur")
    Plateau.getEntity(5,2).setValue("zone","Viticulteur")
    Plateau.getEntity(7,2).setValue("zone","Viticulteur")
    Plateau.getEntity(5,3).setValue("zone","Viticulteur")
    Plateau.getEntity(6,3).setValue("zone","Viticulteur")
    Plateau.getEntity(7,3).setValue("zone","Viticulteur")
    Plateau.getEntity(8,3).setValue("zone","Viticulteur")
    Plateau.getEntity(6,4).setValue("zone","Viticulteur")
    Plateau.getEntity(8,4).setValue("zone","Viticulteur")
    Plateau.getEntity(6,5).setValue("zone","Viticulteur")
    Plateau.getEntity(7,5).setValue("zone","Viticulteur")
    Plateau.getEntity(8,5).setValue("zone","Viticulteur")
    Plateau.getEntity(6,6).setValue("zone","Viticulteur")
    Plateau.getEntity(3,6).setValue("zone","Roches")
    Plateau.getEntity(6,2).setValue("zone","Roches")
    Plateau.getEntity(4,4).setValue("zone","Roches")
    Plateau.getEntity(5,4).setValue("zone","Roches")
    Plateau.getEntity(5,5).setValue("zone","Roches")
    Plateau.getEntity(4,3).setValue("zone","Village Nord")
    Plateau.getEntity(5,6).setValue("zone","Village Sud")
    Plateau.getEntity(7,4).setValue("zone","Village Est")
    Plateau.setEntities("coeurDeSite","out")
    Plateau.getEntity(5,2).setValue("coeurDeSite","in")
    Plateau.getEntity(6,2).setValue("coeurDeSite","in")
    Plateau.getEntity(5,3).setValue("coeurDeSite","in")
    Plateau.getEntity(6,3).setValue("coeurDeSite","in")
    Plateau.getEntity(7,3).setValue("coeurDeSite","in")
    Plateau.getEntity(2,4).setValue("coeurDeSite","in")
    Plateau.getEntity(3,4).setValue("coeurDeSite","in")
    Plateau.getEntity(4,4).setValue("coeurDeSite","in")
    Plateau.getEntity(5,4).setValue("coeurDeSite","in")
    Plateau.getEntity(6,4).setValue("coeurDeSite","in")
    Plateau.getEntity(3,5).setValue("coeurDeSite","in")
    Plateau.getEntity(4,5).setValue("coeurDeSite","in")
    Plateau.getEntity(5,5).setValue("coeurDeSite","in")
    Plateau.getEntity(3,6).setValue("coeurDeSite","in")
    Plateau.getEntity(4,6).setValue("coeurDeSite","in")
    return Plateau

def constructVillageNord():
    VillageNord=myModel.newCellsOnGrid(4,3,"hexagonal",size=80,gap=2,name="VillageNord",color=QColor.fromRgb(135,206,235))
    VillageNord.deleteEntity(VillageNord.getEntity(1,1))
    VillageNord.deleteEntity(VillageNord.getEntity(2,1))
    VillageNord.deleteEntity(VillageNord.getEntity(4,2))
    VillageNord.deleteEntity(VillageNord.getEntity(1,3))
    VillageNord.deleteEntity(VillageNord.getEntity(4,3))
    VillageNord.getEntity(3,1).setValue("zone","Tourisme")
    VillageNord.getEntity(4,1).setValue("zone","Elu")
    VillageNord.getEntity(3,2).setValue("zone","Elu")
    VillageNord.getEntity(3,3).setValue("zone","Elu")
    VillageNord.getEntity(1,2).setValue("zone","Habitant")
    VillageNord.getEntity(2,2).setValue("zone","Habitant")
    VillageNord.getEntity(2,3).setValue("zone","Habitant")
    return VillageNord
    
def constructVillageSud():
    VillageSud=myModel.newCellsOnGrid(4,5,"hexagonal",size=80,gap=2,name="VillageSud",color=QColor.fromRgb(176,224,230))
    VillageSud.deleteEntity(VillageSud.getEntity(1,1))
    VillageSud.deleteEntity(VillageSud.getEntity(3,1))
    VillageSud.deleteEntity(VillageSud.getEntity(4,1))
    VillageSud.deleteEntity(VillageSud.getEntity(3,2))
    VillageSud.deleteEntity(VillageSud.getEntity(4,2))
    VillageSud.deleteEntity(VillageSud.getEntity(1,3))
    VillageSud.deleteEntity(VillageSud.getEntity(4,3))
    VillageSud.deleteEntity(VillageSud.getEntity(4,4))
    VillageSud.deleteEntity(VillageSud.getEntity(1,5))
    VillageSud.deleteEntity(VillageSud.getEntity(2,5))
    VillageSud.getEntity(2,2).setValue("zone","Habitant")
    VillageSud.getEntity(2,3).setValue("zone","Habitant")
    VillageSud.getEntity(3,3).setValue("zone","Habitant")
    VillageSud.getEntity(1,4).setValue("zone","Habitant")
    VillageSud.getEntity(2,1).setValue("zone","Elu")
    VillageSud.getEntity(1,2).setValue("zone","Elu")
    VillageSud.getEntity(2,4).setValue("zone","Tourisme")
    VillageSud.getEntity(3,4).setValue("zone","Tourisme")
    VillageSud.getEntity(3,5).setValue("zone","Tourisme")
    VillageSud.getEntity(4,5).setValue("zone","Tourisme")
    return VillageSud  
    
def constructVillageEst():
    VillageEst=myModel.newCellsOnGrid(5,4,"hexagonal",size=80,gap=2,name="VillageEst",color=QColor.fromRgb(0,191,255))
    VillageEst.deleteEntity(VillageEst.getEntity(1,1))
    VillageEst.deleteEntity(VillageEst.getEntity(2,1))
    VillageEst.deleteEntity(VillageEst.getEntity(3,1))
    VillageEst.deleteEntity(VillageEst.getEntity(1,2))
    VillageEst.deleteEntity(VillageEst.getEntity(2,2))
    VillageEst.deleteEntity(VillageEst.getEntity(1,3))
    VillageEst.deleteEntity(VillageEst.getEntity(5,3))
    VillageEst.deleteEntity(VillageEst.getEntity(1,4))
    VillageEst.deleteEntity(VillageEst.getEntity(3,4))
    VillageEst.deleteEntity(VillageEst.getEntity(4,4))
    VillageEst.deleteEntity(VillageEst.getEntity(5,4))
    VillageEst.getEntity(5,1).setValue("zone","Tourisme")
    VillageEst.getEntity(4,2).setValue("zone","Tourisme")
    VillageEst.getEntity(5,2).setValue("zone","Tourisme")
    VillageEst.getEntity(4,1).setValue("zone","Elu")
    VillageEst.getEntity(3,2).setValue("zone","Habitant")
    VillageEst.getEntity(2,3).setValue("zone","Habitant")
    VillageEst.getEntity(3,3).setValue("zone","Habitant")
    VillageEst.getEntity(4,3).setValue("zone","Habitant")
    VillageEst.getEntity(2,4).setValue("zone","Habitant")
    return VillageEst
    

Plateau=constructPlateau()
VillageNord=constructVillageNord()
VillageSud=constructVillageSud()
VillageEst=constructVillageEst()

#* --------------------------
#* Classifications et POV
#* --------------------------

Plateau.newPov("Zones joueurs","zone",{"Roches":Qt.white,"Naturaliste":Qt.darkGreen,"Viticulteur":Qt.magenta,"Village Nord":QColor.fromRgb(135,206,235),"Village Sud":QColor.fromRgb(176,224,230),"Village Est":QColor.fromRgb(0,191,255)})
Plateau.newBorderPovColorAndWidth("Coeur de site","coeurDeSite", {"in": [Qt.red,6], "out": [Qt.black,1]})
VillageNord.newPov("Zones joueurs","zone",{"Elu":Qt.blue,"Habitant":QColor.fromRgb(255,165,0),"Tourisme":Qt.yellow})
VillageSud.newPov("Zones joueurs","zone",{"Elu":Qt.blue,"Habitant":QColor.fromRgb(255,165,0),"Tourisme":Qt.yellow})
VillageEst.newPov("Zones joueurs","zone",{"Elu":Qt.blue,"Habitant":QColor.fromRgb(255,165,0),"Tourisme":Qt.yellow})

#* --------------------------
#* Dashboard des indicateurs
#* -------------------------- 
DashBoardInd=myModel.newDashBoard("Suivi des indicateurs")
qualiteVie=myModel.newSimVariable("Qualité de vie",0)
environnement=myModel.newSimVariable("Environnement",0)
attractivite=myModel.newSimVariable("Attractivité",0)
indQualiteVie=DashBoardInd.addIndicatorOnSimVariable(qualiteVie)
indEnvironnement=DashBoardInd.addIndicatorOnSimVariable(environnement)
indAttractivite=DashBoardInd.addIndicatorOnSimVariable(attractivite)

#* --------------------------
#* Dashboard des services
#* --------------------------
DashBoard=myModel.newDashBoard("Suivi des services")
biodiversite=myModel.newSimVariable("Biodiversité",0)
sante=myModel.newSimVariable("Santé",0)
culture=myModel.newSimVariable("Espace culturel",0)
servicePublic=myModel.newSimVariable("Service public",0)
bar=myModel.newSimVariable("Bar",0)
restaurant=myModel.newSimVariable("Restaurant",0)
democratie=myModel.newSimVariable("Espace de démocratie",0)
loisirs=myModel.newSimVariable("Espace de loisirs",0)
emploi=myModel.newSimVariable("Emploi",0)
indSante=DashBoard.addIndicatorOnSimVariable(sante)
indCulture=DashBoard.addIndicatorOnSimVariable(culture)
indServicePublic=DashBoard.addIndicatorOnSimVariable(servicePublic)
indBar=DashBoard.addIndicatorOnSimVariable(bar)
indRestaurant=DashBoard.addIndicatorOnSimVariable(restaurant)
indDemocratie=DashBoard.addIndicatorOnSimVariable(democratie)
indLoisirs=DashBoard.addIndicatorOnSimVariable(loisirs)
indEmploi=DashBoard.addIndicatorOnSimVariable(emploi)

#* --------------------------
#* Déclaration des joueurs
#* --------------------------
Viticulteur = myModel.newPlayer("Viticulteur",attributesAndValues={"nbCubes":6,"Sous":0})

#* --------------------------
#* Déclaration des agents
#* --------------------------
Touriste=myModel.newAgentSpecies("Touriste","squareAgent",defaultSize=40,defaultImage=QPixmap("./icon/solutre/touriste.png"))
Bouteille=myModel.newAgentSpecies("Bouteille de vin conventionnel","ellipseAgent",defaultSize=20,defaultColor=Qt.magenta)
BouteilleBio=myModel.newAgentSpecies("Bouteille de vin bio","ellipseAgent",defaultSize=20,defaultColor=Qt.green)
reserve=myModel.newCellsOnGrid(1,1,"square",size=120,gap=0,name="Réserve")
Touriste.newAgentAtCoords(reserve)
Touriste.newAgentAtCoords(reserve)
Touriste.newAgentAtCoords(reserve)
Touriste.newAgentAtCoords(reserve)

def createHex(nom,species,dataInst,dataAct,dataPerm=None,model=myModel):
    variables=myModel.getSimVars()
    
    # Création des effets instantanés
    ligneHexInst = dataInst[dataInst['nom'] == nom]
    if ligneHexInst.empty:
        return f"L'entité '{nom}' n'existe pas dans le fichier Excel Inst."
    
    coutCubes=int(ligneHexInst['coutCubes'].values[0])
    colonnesJauges= dataInst.loc[:, 'Qualité de vie':'Santé'].columns
    effetInstantaneJauge = {}
    for col in colonnesJauges:
        variable=next((var for var in variables if var.name == col), None)
        if variable is not None:
            effetInstantaneJauge[variable] = int(ligneHexInst[col].values[0]) if not math.isnan(ligneHexInst[col].values[0]) else 0
    condPlacement=[]#ast.literal_eval(ligneHexInst['emplacementPose'].values[0])
    joueur=model.getPlayer(ligneHexInst["joueur"].values[0])
    
    # Création des effets activables
    ligneHexAct = dataAct[dataAct['nom'] == nom]
    if ligneHexAct.empty:
        return f"L'entité '{nom}' n'existe pas dans le fichier Excel Act."
    
    coutCubesAct=int(ligneHexAct['coutCubesAct'].values[0]) if not math.isnan(ligneHexAct['coutCubesAct'].values[0]) else 0
    coutVin=int(ligneHexAct['coutVin'].values[0]) if not math.isnan(ligneHexAct['coutVin'].values[0]) else 0
    coutVinBio=int(ligneHexAct['coutVinBio'].values[0]) if not math.isnan(ligneHexAct['coutVinBio'].values[0]) else 0
    coutSous=int(ligneHexAct['coutSous'].values[0]) if not math.isnan(ligneHexAct['coutSous'].values[0]) else 0

    vin=int(ligneHexAct['vin'].values[0]) if not math.isnan(ligneHexAct['vin'].values[0]) else 0
    vinBio=int(ligneHexAct['vinBio'].values[0]) if not math.isnan(ligneHexAct['vinBio'].values[0]) else 0
    sou=int(ligneHexAct['sou'].values[0]) if not math.isnan(ligneHexAct['sou'].values[0]) else 0
    touriste=int(ligneHexAct['touriste'].values[0]) if not math.isnan(ligneHexAct['touriste'].values[0]) else 0

    effetRessourcesAct=[vin,vinBio,sou,touriste]

    effetActivableJauge={}
    colonnesJauges= dataAct.loc[:, 'Biodiversité':'Qualité de vie'].columns
    for col in colonnesJauges:
        variable=next((var for var in variables if var.name == col), None)
        if variable is not None:
            effetActivableJauge[variable] = int(ligneHexAct[col].values[0]) if not math.isnan(ligneHexAct[col].values[0]) else 0

    # Création des effets permanents

    #TODO

    entite = hexagones.newAgentAtCoords(pioche,6,1,{'coûtCubes': coutCubes, 'joueur':joueur, 'nom':nom, 'effetInstantaneJauge': effetInstantaneJauge, "condPlacement": condPlacement , 'coutCubesAct': coutCubesAct, 'coutVin':coutVin, 'coutVinBio':coutVinBio,'coutSous':coutSous,"effetRessourcesAct":effetRessourcesAct,"effetActivableJauge":effetActivableJauge})
    return entite

hexagones=myModel.newAgentSpecies("Hexagone","hexagonAgent",{"coûtCubes":0,"joueur":None,"nom":None,"effetInstantaneJauge":None,"condPlacement":None,'coutCubesAct': None, 'coutVin':None, 'coutVinBio':None,'coutSous':None,"effetRessourcesAct":None,"effetActivableJauge":None},defaultSize=70,locationInEntity="center")#,defaultImage=QPixmap("./icon/solutre/N1.png"))
hexagones.newBorderPovColorAndWidth("Activation","Activation",{False:[Qt.black,1],True:[Qt.yellow,2]})
hexagones.setDefaultValue("Activation",False)
# hexagones.setAttributesConcernedByUpdateMenu("Activation")#,"Activation")
pioche=myModel.newCellsOnGrid(6,1,"square",size=120,gap=20,name="Pioche")
# hexagones.newAgentAtCoords(pioche,1,1,{"coûtCubes":1,"joueur":Player1,"nom":"Vigne","effetInstantaneJauge":{emploi:-1,bar:3}},popupImagePath="./icon/solutre/V5.png")
# hexVigne=hexagones.newAgentAtCoords(pioche,2,1,{"coûtCubes":1,"joueur":Viticulteur,"nom":"Vigne","effetInstantaneJauge":{emploi:-1,bar:3}})#,"Activation":True})
HexBarVin=createHex("Bar à vin",hexagones,data_inst,data_act)

#* --------------------------
#* Dashboard des ressources
#* --------------------------
DashBoardRessources=myModel.newDashBoard("Ressources")
DashBoardRessources.addIndicator(Touriste,"nb")
DashBoardRessources.addIndicator(Bouteille,"nb")
DashBoardRessources.addIndicator(BouteilleBio,"nb")


#* --------------------------
#* Dashboard du Viticulteur
#* --------------------------
DashBoardViticulteur=myModel.newDashBoard("Viticulteur")
DashBoardViticulteur.addIndicatorOnEntity(Viticulteur,"nbCubes",title="Nombre de cubes actions restant")
DashBoardViticulteur.addIndicatorOnEntity(Viticulteur,"Sous",title="Sous disponibles")


#* --------------------------
#* GameActions
#* --------------------------
MoveHexagone=myModel.newMoveAction(hexagones, 'infinite',feedback=[lambda aHex: execeffetInstantaneJauge(aHex),lambda aHex:updateCubes(aHex)])
MoveHexagone.addCondition(lambda aHex,aTargetCell: aTargetCell.value("zone")==aHex.value("joueur").name)
MoveHexagone.addCondition(lambda aHex: aHex.value("joueur").value("nbCubes")>=aHex.value("coûtCubes"))
MoveHexagone.addCondition(lambda aTargetCell : aTargetCell.value("zone") not in ["Village Nord","Village Sud","Village Est"])
Viticulteur.addGameAction(MoveHexagone)
ActivateHexagone=myModel.newActivateAction(hexagones,"execeffetActivableJauge",setControllerContextualMenu=True)
ActivateHexagone.addCondition(lambda aHex: aHex.value("joueur").value("nbCubes")>=aHex.value("coutCubesAct"))
Viticulteur.addGameAction(ActivateHexagone)
ViticulteurControlPanel = Viticulteur.newControlPanel("Actions")

def execeffetInstantaneJauge(aHex):
    for jauge, valeur in aHex.value("effetInstantaneJauge").items():
        jauge.incValue(valeur)
    # aHex.toggleHighlight

def updateCubes(aHex):
    player=aHex.value("joueur")
    print("AVANT "+str(player.value("nbCubes")))
    player.decValue("nbCubes",aHex.value("coûtCubes"))
    print("APRES "+str(player.value("nbCubes")))

def execeffetActivableJauge(aHex):
    if all(aHex.value(key) == 0 for key in ['coutCubesAct', 'coutVin', 'coutVinBio', 'coutSous']):
        myModel.newWarningPopUp("Attention!","Cet hexagone n'est pas activable!")
        return
    for jauge,valeur in aHex.value("effetActivableJauge").items():
        jauge.incValue(valeur)
        updatesCubesActivation(aHex)

def updatesCubesActivation(aHex):
    player=aHex.value("joueur")
    player.decValue("nbCubes",aHex.value("coutCubesAct"))

#* --------------------------
#* Paramètres du modèle
#* --------------------------        
GamePhase=myModel.timeManager.newGamePhase("Les joueurs peuvent jouer",[Viticulteur])

Plateau.displayBorderPov("Coeur de site")

userSelector=myModel.newUserSelector()
myModel.setCurrentPlayer("Viticulteur")
# Legend=myModel.newLegend(grid="combined")
Legend=myModel.newLegend()

print(str(sys.argv[0]))

if __name__ == '__main__':
    myModel.launch()
    # myModel.launch_withMQTT("Instantaneous")
    sys.exit(monApp.exec_())