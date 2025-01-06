import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(windowTitle="Solutré", typeOfLayout ="grid", x=5,y=5)
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

Plateau.newPov("Zones joueurs","zone",{"Roches":QPixmap("./icon/solutre/roches1_cell.png"),"Naturaliste":QPixmap("./icon/solutre/Naturaliste_cell.png"),"Viticulteur":QPixmap("./icon/solutre/Viticulteur_cell.png"),"Village Nord":QColor.fromRgb(135,206,235),"Village Sud":QColor.fromRgb(176,224,230),"Village Est":QColor.fromRgb(0,191,255)})
Plateau.newBorderPovColorAndWidth("Coeur de site","coeurDeSite", {"in": [Qt.red,6], "out": [Qt.black,1]})
VillageNord.newPov("Zones joueurs","zone",{"Elu":QPixmap("./icon/solutre/Elu_cell.png"),"Habitant":QPixmap("./icon/solutre/Habitant_cell.png"),"Tourisme":QPixmap("./icon/solutre/Tourisme_cell.png")})
VillageSud.newPov("Zones joueurs","zone",{"Elu":QPixmap("./icon/solutre/Elu_cell.png"),"Habitant":QPixmap("./icon/solutre/Habitant_cell.png"),"Tourisme":QPixmap("./icon/solutre/Tourisme_cell.png")})
VillageEst.newPov("Zones joueurs","zone",{"Elu":QPixmap("./icon/solutre/Elu_cell.png"),"Habitant":QPixmap("./icon/solutre/Habitant_cell.png"),"Tourisme":QPixmap("./icon/solutre/Tourisme_cell.png")})

#* --------------------------
#* Dashboard des indicateurs
#* -------------------------- 
DashBoardInd=myModel.newDashBoard("Suivi des indicateurs")
qualiteVie=myModel.newSimVariable("Qualité de vie",0)
environnement=myModel.newSimVariable("Environnement",0)
attractivite=myModel.newSimVariable("Attractivité",0)
indQualiteVie=DashBoardInd.addIndicatorOnSimVariable(qualiteVie)
indAttractivite=DashBoardInd.addIndicatorOnSimVariable(attractivite)
indEnvironnement=DashBoardInd.addIndicatorOnSimVariable(environnement)

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
indBiodiv=DashBoard.addIndicatorOnSimVariable(biodiversite)
indSante=DashBoard.addIndicatorOnSimVariable(sante)
indCulture=DashBoard.addIndicatorOnSimVariable(culture)
indServicePublic=DashBoard.addIndicatorOnSimVariable(servicePublic)
indBar=DashBoard.addIndicatorOnSimVariable(bar)
indRestaurant=DashBoard.addIndicatorOnSimVariable(restaurant)
indLoisirs=DashBoard.addIndicatorOnSimVariable(loisirs)
indEmploi=DashBoard.addIndicatorOnSimVariable(emploi)
indDemocratie=DashBoard.addIndicatorOnSimVariable(democratie)

#* --------------------------
#* Déclaration des joueurs
#* --------------------------
Viticulteur = myModel.newPlayer("Viticulteur",attributesAndValues={"nbCubes":30,"Sous":0})
Tourisme = myModel.newPlayer("Tourisme",attributesAndValues={"nbCubes":30,"Sous":0})


#* --------------------------
#* Déclaration des agents
#* --------------------------
Touriste=myModel.newAgentSpecies("Touriste","circleAgent",defaultSize=40,defaultImage=QPixmap("./icon/solutre/touriste.png"))
Bouteille=myModel.newAgentSpecies("Bouteille de vin","circleAgent",defaultSize=40,defaultImage=QPixmap("./icon/solutre/vin.png"))
BouteilleBio=myModel.newAgentSpecies("Bouteille de vin bio","circleAgent",defaultSize=40,defaultImage=QPixmap("./icon/solutre/vinBIO.png"))
Buisson=myModel.newAgentSpecies("Buisson","circleAgent",defaultSize=40,defaultColor=Qt.darkGreen,locationInEntity="center")
reserve=myModel.newCellsOnGrid(2,1,"square",size=120,gap=0,name="Réserve")
reserve.getEntity(1,1).setValue("zone",True)
reserve.getEntity(2,1).setValue("zone",True)
reserve.newPov("Zones joueurs","zone",{True:Qt.darkGray})

#* --------------------------
#* Dashboard des ressources
#* --------------------------
DashBoardRessources=myModel.newDashBoard("Ressources")
touriste=myModel.newSimVariable("touriste",0)
vin=myModel.newSimVariable("vin",0)
vinBio=myModel.newSimVariable("vinBio",0)
indVin=DashBoardRessources.addIndicatorOnSimVariable(vin)
indVinBio=DashBoardRessources.addIndicatorOnSimVariable(vinBio)
indTouriste=DashBoardRessources.addIndicatorOnSimVariable(touriste)
DashBoardRessources.addIndicator(Touriste,"nb")


def createHex(nom,species,dataInst,dataAct,dataPerm=None,model=myModel):
    variables=myModel.getSimVars()
    
    # Création des effets instantanés
    ligneHexInst = dataInst[dataInst['nom'] == nom]
    if ligneHexInst.empty:
        return print(f"L'entité '{nom}' n'existe pas dans le fichier Excel Inst.")
        
    
    coutCubes=int(ligneHexInst['coutCubes'].values[0])
    colonnesJauges= dataInst.loc[:, 'Qualité de vie':'Santé'].columns
    effetInstantaneJauge = {}
    for col in colonnesJauges:
        variable=next((var for var in variables if var.name == col), None)
        if variable is not None:
            effetInstantaneJauge[variable] = int(ligneHexInst[col].values[0]) if not math.isnan(ligneHexInst[col].values[0]) else 0
    joueur=model.getPlayer(ligneHexInst["joueur"].values[0]) if not "Plateau" in ligneHexInst["joueur"].values[0] else None

    conditionAdjacence=ligneHexInst["conditionAdjacence"].values[0] if isinstance(ligneHexInst["conditionAdjacence"].values[0], str) else None
    nbAdjacence=ligneHexInst["nbAdjacence"].values[0] if not math.isnan(ligneHexInst["nbAdjacence"].values[0]) else 1
    conditionFeedbackAdjacence=ligneHexInst["conditionFeedbackAdjacence"].values[0] if isinstance(ligneHexInst["conditionFeedbackAdjacence"].values[0], str) else None
    feedbackAdjacenceAttractivité=ligneHexInst["feedbackAdjacenceAttractivité"].values[0] if not math.isnan(ligneHexInst["nbAdjacence"].values[0]) else 0


    image=ligneHexInst["image recto"].values[0] if isinstance(ligneHexInst["image recto"].values[0], str) else None
    
    # Création des effets activables
    ligneHexAct = dataAct[dataAct['nom'] == nom]
    if ligneHexAct.empty:
        return print(f"L'entité '{nom}' n'existe pas dans le fichier Excel Act.")
    
    coutCubesAct=int(ligneHexAct['coutCubesAct'].values[0]) if not math.isnan(ligneHexAct['coutCubesAct'].values[0]) else 0
    coutVin=int(ligneHexAct['coutVin'].values[0]) if not math.isnan(ligneHexAct['coutVin'].values[0]) else 0
    coutVinBio=int(ligneHexAct['coutVinBio'].values[0]) if not math.isnan(ligneHexAct['coutVinBio'].values[0]) else 0
    coutSous=int(ligneHexAct['coutSous'].values[0]) if not math.isnan(ligneHexAct['coutSous'].values[0]) else 0

    effetRessourcesAct={}
    ressources= dataAct.loc[:, 'vin':'touriste'].columns
    for res in ressources:
        variable=next((var for var in variables if var.name == res), None)
        if variable is not None:
            effetRessourcesAct[variable] = int(ligneHexAct[res].values[0]) if not math.isnan(ligneHexAct[res].values[0]) else 0

    effetActivableJauge={}
    colonnesJauges= dataAct.loc[:, 'Biodiversité':'Qualité de vie'].columns
    for col in colonnesJauges:
        variable=next((var for var in variables if var.name == col), None)
        if variable is not None:
            effetActivableJauge[variable] = int(ligneHexAct[col].values[0]) if not math.isnan(ligneHexAct[col].values[0]) else 0
    
    image_ACT=ligneHexAct["image verso"].values[0] if isinstance(ligneHexAct["image verso"].values[0], str) else None

    coutTouriste=int(ligneHexAct['coutTouriste'].values[0]) if not math.isnan(ligneHexAct['coutTouriste'].values[0]) else 0
    effetActivableTouriste={
        "Sous":int(ligneHexAct['feedbackTouristeSous'].values[0]) if not math.isnan(ligneHexAct['feedbackTouristeSous'].values[0]) else 0,
        "Attractivité":int(ligneHexAct['feedbackTouristeAttractivité'].values[0]) if not math.isnan(ligneHexAct['feedbackTouristeAttractivité'].values[0]) else 0,
        "Qualité de vie": int(ligneHexAct['feedbackTouristeQDV'].values[0]) if not math.isnan(ligneHexAct['feedbackTouristeQDV'].values[0]) else 0,
    }
    

    entite = hexagones.newAgentAtCoords(pioche,6,1,{'nom': nom,'coûtCubes': coutCubes, 'joueur':joueur, 'nom':nom, 'effetInstantaneJauge': effetInstantaneJauge, 'coutCubesAct': coutCubesAct, 'coutVin':coutVin, 'coutVinBio':coutVinBio,'coutSous':coutSous,"effetRessourcesAct":effetRessourcesAct,"effetActivableJauge":effetActivableJauge,"coutTouriste":coutTouriste,"effetActivableTouriste":effetActivableTouriste,"conditionAdjacence":conditionAdjacence,"nbAdjacence":nbAdjacence,"conditionFeedbackAdjacence":conditionFeedbackAdjacence,"feedbackAdjacenceAttractivité":feedbackAdjacenceAttractivité,"placed":False},image=QPixmap(image_ACT),popupImage=image)#QPixmap(image))
    return

def createAllHex(species,dataInst,dataAct,dataPerm=None,model=myModel):
    listOfHex=list(dataInst['nom'])
    for aHexName in listOfHex:
        createHex(aHexName,species,dataInst,dataAct,dataPerm,model)

def setImageFaceHexagone():
    for aHex in hexagones.getEntities():
        return

hexagones=myModel.newAgentSpecies("Hexagone","hexagonAgent",{"coûtCubes":0,"joueur":None,"nom":None,"effetInstantaneJauge":None,"condPlacement":None,'coutCubesAct': None, 'coutVin':None, 'coutVinBio':None,'coutSous':None,"effetRessourcesAct":None,"effetActivableJauge":None,"face":"recto","imageFace":None},defaultSize=70,locationInEntity="center")#,defaultImage=QPixmap("./icon/solutre/N1.png"))
hexagones.newBorderPovColorAndWidth("Activation","Activation",{False:[Qt.black,1],True:[Qt.yellow,2]})
hexagones.setDefaultValue("Activation",False)
pioche=myModel.newCellsOnGrid(6,1,"square",size=80,gap=20,name="Pioche")
pioche.getEntity(6,1).setValue("zone",True)
pioche.newPov("Zones joueurs","zone",{True:Qt.darkGray})

# Création des hexagones

createHex("Bar à vin",hexagones,data_inst,data_act)
createHex("Dégustation au caveau",hexagones,data_inst,data_act)
createHex("Vigne Bio",hexagones,data_inst,data_act)
createHex("Export vin BIO",hexagones,data_inst,data_act)
createHex("Parcours gastronomique",hexagones,data_inst,data_act)
createHex("Labellisation bio",hexagones,data_inst,data_act)
createHex("Vigne",hexagones,data_inst,data_act)
createHex("Bar",hexagones,data_inst,data_act)

createHex("Chambre d'hôtes du plateau",hexagones,data_inst,data_act)
createHex("Chambre d'hôtes du plateau",hexagones,data_inst,data_act)
createHex("Vigne du plateau",hexagones,data_inst,data_act)
createHex("Caveau du plateau",hexagones,data_inst,data_act)


#* --------------------------
#* Dashboard du Viticulteur
#* --------------------------
DashBoardViticulteur=myModel.newDashBoard("Viticulteur")
DashBoardViticulteur.addIndicatorOnEntity(Viticulteur,"nbCubes",title="Nombre de cubes actions restant")
DashBoardViticulteur.addIndicatorOnEntity(Viticulteur,"Sous",title="Sous")


#* --------------------------
#* GameActions
#* --------------------------
MoveHexagone=myModel.newMoveAction(hexagones, 'infinite')#,feedbacks=[lambda aHex: execeffetInstantaneJauge(aHex),lambda aHex:updateCubes(aHex)],setOnController=False)
MoveHexagone.addCondition(lambda aHex,aTargetCell : aTargetCell.value("zone") not in ["Village Nord","Village Sud","Village Est"])
MoveHexagone.addCondition(lambda aHex,aTargetCell : checkIfAHexIsHere(aTargetCell))
MoveHexagone.addCondition(lambda aHex: aHex.value("placed")==False)
Viticulteur.addGameAction(MoveHexagone)
ValiderMoveHexagone=myModel.newActivateAction(hexagones, 'execeffetInstantaneJauge',setControllerContextualMenu=True,aNameToDisplay="Valider le placement")#,feedbacks=[lambda aHex: execeffetInstantaneJauge(aHex),lambda aHex:updateCubes(aHex)],setOnController=False)
ValiderMoveHexagone.addCondition(lambda aHex: aHex.value("placed")==False)
ValiderMoveHexagone.addCondition(lambda aHex: checkAdjacence(aHex))
ValiderMoveHexagone.addCondition(lambda aHex: aHex.value("joueur").value("nbCubes")>=aHex.value("coûtCubes"))
ValiderMoveHexagone.addCondition(lambda aHex: aHex.cell.grid.id!="Pioche")
ValiderMoveHexagone.addFeedback(lambda aHex: adjacenceFeedback(aHex))
Viticulteur.addGameAction(ValiderMoveHexagone)
MovePioche=myModel.newMoveAction(hexagones, 'infinite',setOnController=False)
MovePioche.addCondition(lambda aHex,aTargetCell: aTargetCell.grid.id=="Pioche")
Viticulteur.addGameAction(MovePioche)
ActivateHexagone=myModel.newActivateAction(hexagones,"execeffetActivableJauge",setControllerContextualMenu=True,aNameToDisplay="Activer l'hexagone")
ActivateHexagone.addCondition(lambda aHex: aHex.value("joueur").value("nbCubes")>=aHex.value("coutCubesAct"))
ActivateHexagone.addCondition(lambda aHex: checkIfActivable(aHex))
ActivateHexagone.addCondition(lambda aHex: aHex.value("Activation")==False)
ActivateHexagone.addCondition(lambda aHex: aHex.value("placed")==True)
Viticulteur.addGameAction(ActivateHexagone)
DeleteBuisson=myModel.newDeleteAction(Buisson,conditions= [lambda : checkCubes()],feedbacks= [lambda : decCubes()])
Viticulteur.addGameAction(DeleteBuisson)
ViticulteurControlPanel = Viticulteur.newControlPanel("Actions")



PlaceTouriste=myModel.newMoveAction(Touriste,"infinite",setOnController=False)
PlaceTouriste.addCondition(lambda: checkIsThereTouristes())
PlaceTouriste.addCondition(lambda aTourist, aTargetCell: checkIsHébergement(aTargetCell))
PlaceTouriste.addFeedback(lambda: decTouristes())
PlaceTouriste.addFeedback(lambda aTourist: execeffetActivableTouriste(aTourist))
Tourisme.addGameAction(PlaceTouriste)

def checkIfAHexIsHere(aTargetCell):
    hexa=aTargetCell.getAgents(specie="Hexagone")
    if len(hexa) != 0: return False
    else: return True

def execeffetInstantaneJauge(aHex):
    print(aHex.value("placed"))
    for jauge, valeur in aHex.value("effetInstantaneJauge").items():
        jauge.incValue(valeur)
    updateCubes(aHex)
    aHex.setValue("placed",True)

def updateCubes(aHex):
    player=aHex.value("joueur")
    player.decValue("nbCubes",aHex.value("coûtCubes"))

def execeffetActivableJauge(aHex):
    for jauge,valeur in aHex.value("effetActivableJauge").items():
        jauge.incValue(valeur)
    for ressource,valeur in aHex.value("effetRessourcesAct").items():
        ressource.incValue(valeur)
    updatesCubesActivation(aHex)
    aHex.setValue("Activation",True)

def checkIfActivable(aHex):
    values= list(aHex.value("effetActivableJauge").values())+list(aHex.value("effetRessourcesAct").values())
    return any(val != 0 for val in values)

def updatesCubesActivation(aHex):
    player=aHex.value("joueur")
    player.decValue("nbCubes",aHex.value("coutCubesAct"))

def checkCubes():
    player=myModel.getPlayer(myModel.currentPlayer)
    if player.value("nbCubes")>1: return True
    else: return False

def decCubes():
    player=myModel.getPlayer(myModel.currentPlayer)
    player.decValue("nbCubes")

def checkIsThereTouristes():
    if touriste.value >= 1: return True
    else: return False

def checkIsHébergement(aTargetCell):
    hexa=aTargetCell.getAgents(specie="Hexagone")
    for aHex in hexa:
        if aHex.value("coutTouriste") !=0: return True
        else: return False

def decTouristes():
    touriste.decValue()

def execeffetActivableTouriste(aTourist):
    aTargetCell=aTourist.cell
    aHex=aTargetCell.getAgents(specie="Hexagone")[0]
    dictOfValues=aHex.value("effetActivableTouriste")
    attractivite.incValue(int(dictOfValues.get("Attractivité")))
    qualiteVie.incValue(int(dictOfValues.get("Qualité de vie")))
    Tourisme.incValue("Sous",int(dictOfValues.get("Sous")))
    
def checkAdjacence(aHex):
    if aHex.value("conditionAdjacence") is not None:
        listOfNeighbours=aHex.getNeighborAgents(aSpecies=hexagones)
        nbNeighbour=0
        for aNeighbourHex in listOfNeighbours:
            if aHex.value("conditionAdjacence") == aNeighbourHex.value("player").name: 
                if aHex.value("nbAdjacence") == 1: return True
                else:
                    nbNeighbour=+1
                    if aHex.value("nbAdjacence") == nbNeighbour:
                        return True
            elif aHex.value("conditionAdjacence") in ["Service public","Espace de démocratie"]:
                for jauge, value in aNeighbourHex.value("effetActivableJauge").items():
                    if jauge.name == aHex.value("conditionAdjacence"): return True
            elif aHex.value("conditionAdjacence") in ["vinBio","vin"]:
                for ressource, value in aNeighbourHex.value("effetRessourcesAct").items():
                    if ressource.name == aHex.value("effetRessourcesAct"): return True
            elif aHex.value("conditionAdjacence") == "coutTouriste" and aNeighbourHex.value("coutTouriste")>0: return True
    else: return True

def adjacenceFeedback(aHex):
    if aHex.value("conditionFeedbackAdjacence") == "coutTouriste":
        listOfNeighbours=aHex.getNeighborAgents(aSpecies=hexagones)
        for aNeighbourHex in listOfNeighbours:
            if aNeighbourHex.value("coutTouriste")>0:
                attractivite.incValue()

#* --------------------------
#* Paramètres du modèle
#* --------------------------        
dataEvents=pd.read_excel("./data/data_events.xlsx")
usedKeys=["Au Nom des Roches"]

def execEvent():
    randomKey=random.choice(list(dataEvents["Nom"]))
    while randomKey in usedKeys:
        randomKey=random.choice(list(dataEvents["Nom"]))
    eventLine=dataEvents[dataEvents['Nom']==randomKey]
    usedKeys.append(randomKey)
    myModel.newPopUp(eventLine['Nom'].squeeze(),eventLine["Descriptif"].squeeze()+" Nombre de touristes cette année :"+str(eventLine["nbTouristes"].squeeze()))
    Touriste.newAgentsAtCoords(int(eventLine["nbTouristes"].squeeze()),reserve,1,1)
    touriste.incValue(int(eventLine["nbTouristes"].squeeze()))
   
def execFirstEvent():
    eventLine=dataEvents[dataEvents['Nom'] == "Au Nom des Roches"]
    myModel.newPopUp(eventLine['Nom'].squeeze(),eventLine["Descriptif"].squeeze()+" Nombre de touristes cette année :"+str(eventLine["nbTouristes"].squeeze()))
    Touriste.newAgentsAtCoords(int(eventLine["nbTouristes"].squeeze()),reserve,1,1)
    touriste.incValue(int(eventLine["nbTouristes"].squeeze()))
            
def checkTouriste():
    cell=reserve.getCell(1,1)
    nbTouriste=cell.nbAgents()
    if nbTouriste != 0:
        for n in range(nbTouriste):
            aInd=random.choice([attractivite,qualiteVie,environnement])
            aInd.decValue()
        print(f"Attention ! Cette année, {nbTouriste} touristes n'ont pas été placés.")
    Touriste.deleteAllEntities()
    touriste.setValue(0)

def checkBuisson():
    nbBuisson=Buisson.nbOfEntities()
    if nbBuisson != 0:
        for n in range(nbBuisson):
            aInd=random.choice([attractivite,qualiteVie,environnement])
            aInd.decValue()
        print(f"Attention ! Cette année, {nbBuisson} buissons n'ont pas été entretenus.")
    Buisson.deleteAllEntities()

def resetHexagones():
    nbHexReset=0
    for aHex in hexagones.getEntities():
        if aHex.cell.grid.id!="Pioche" and aHex.value("placed")==False:
            aHex.moveToCell(pioche,6,1)
            nbHexReset=+1
    print(f"{nbHexReset} hexagones ont été remis dans la pioche.")


#PHASE 1 : Début d'années = événements + buissons
eventPopUp=myModel.newModelAction(lambda: execEvent(), lambda: myModel.timeManager.currentRoundNumber > 1)
eventPopUp2= myModel.newModelAction(lambda: execFirstEvent(), lambda: myModel.timeManager.currentRoundNumber == 1)
Embuissonnement=myModel.newModelAction([lambda: Buisson.newAgentsAtRandom(3,Plateau,condition= lambda aCell: aCell.value("zone")=="Roches")])
EventPhase=myModel.timeManager.newModelPhase([eventPopUp,eventPopUp2,Embuissonnement], name="Évènements")
EventPhase.autoForwardOn=True
EventPhase.messageAutoForward=False

#PHASE 2 : Aménagement du territoire = tous les joueurs peuvent jouer (placer et activer des hexagones)
GamePhase=myModel.timeManager.newGamePhase("Phase 1 : Aménager le territoire",[Viticulteur])

#PHASE 3 : Gestion des touristes = seul le joueur Pro du Tourisme peut jouer
GamePhase2=myModel.timeManager.newGamePhase("Phase 2 : Placement des touristes",[Tourisme])

#PHASE 4 : Résolution de l'année = 
unActivatePlateau=myModel.newModelAction([lambda: hexagones.setEntities("Activation",False)])
ModelPhase=myModel.timeManager.newModelPhase([unActivatePlateau,checkTouriste,checkBuisson,resetHexagones],name="Résolution de l'année en cours")
ModelPhase.autoForwardOn=True
ModelPhase.messageAutoForward=False

aTimeLabel = myModel.newTimeLabel()

Plateau.displayBorderPov("Coeur de site")

userSelector=myModel.newUserSelector()
myModel.setCurrentPlayer("Viticulteur")

def customLayout():
    Plateau.grid.moveToCoords(440,130)
    VillageNord.grid.moveToCoords(30,130)
    VillageEst.grid.moveToCoords(1180,400)
    VillageSud.grid.moveToCoords(30,380)
    pioche.grid.moveToCoords(400,730)
    reserve.grid.moveToCoords(135,765)
    DashBoardInd.moveToCoords(1180,130)
    DashBoard.moveToCoords(1390,130)
    DashBoardRessources.moveToCoords(1640,130)
    DashBoardViticulteur.moveToCoords(1500,730)
    ViticulteurControlPanel.moveToCoords(1330,730)
    aTimeLabel.moveToCoords(30,40)

def placeInitHexagones():
    n=0
    cells=[VillageSud.getCell(3,5),VillageNord.getCell(3,1)]
    for aHex in hexagones.getEntities():
        if aHex.value("placed")==False:
            if aHex.value("nom")=="Vigne du plateau":
                aHex.setValue("placed",True)
                aHex.moveTo(Plateau.getCell(8,4))
                
                print(f"Vigne du plateau placé: {aHex.value('placed')}")
            if aHex.value("nom")=="Caveau du plateau":
                aHex.setValue("placed",True)
                aHex.moveTo(Plateau.getCell(8,5))
                
            if aHex.value("nom")=="Chambre d'hôtes du plateau":
                aHex.setValue("placed",True)
                aHex.moveTo(cells[n])
                n=+1
                

if __name__ == '__main__':
    customLayout()
    placeInitHexagones()
    myModel.launch()
    # myModel.launch_withMQTT("Instantaneous")
    sys.exit(monApp.exec_())