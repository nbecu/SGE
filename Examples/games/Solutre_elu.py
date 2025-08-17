import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(windowTitle="Solutré", typeOfLayout ="grid", x=100,y=100)
localLink="."
#* --------------------------
#* Lecture des data
#* --------------------------
data_inst=pd.read_excel(localLink+"/data/solutre_hex_inst.xlsx")
data_act=pd.read_excel(localLink+"/data/solutre_hex_act.xlsx")
data_objectifs=pd.read_excel(localLink+"/data/data_objectifs.xlsx")
dataEvents=pd.read_excel(localLink+"/data/data_events.xlsx")

#* --------------------------
#* Construction des plateaux
#* --------------------------
def constructPlateau():
    """Permet de construire le plateau de jeu principal de Solutré"""
    Plateau=myModel.newCellsOnGrid(8,8,"hexagonal",size=80,gap=2,name="Plateau",backGroundImage=QPixmap(localLink+"/icon/solutre/fond_solutre.jpg"))
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
    """Permet de construire le village Nord de Solutré"""
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
    """Permet de construire le village Sud de Solutré"""
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
    """Permet de construire le village Est de Solutré"""
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
# Création des classifications couleur pour les plateaux : permet d'attribuer une couleur à chaque zone
Plateau.newPov("Zones joueurs","zone",{"Roches":QPixmap(localLink+"/icon/solutre/roches1_cell.png"),"Naturaliste":QPixmap(localLink+"/icon/solutre/Naturaliste_cell.png"),"Viticulteur":QPixmap(localLink+"/icon/solutre/Viticulteur_cell.png"),"Village Nord":QColor.fromRgb(135,206,235),"Village Sud":QColor.fromRgb(176,224,230),"Village Est":QColor.fromRgb(0,191,255)})
Plateau.newBorderPovColorAndWidth("Coeur de site","coeurDeSite", {"in": [Qt.red,6], "out": [Qt.black,1]})
VillageNord.newPov("Zones joueurs","zone",{"Elu":QPixmap(localLink+"/icon/solutre/Elu_cell.png"),"Habitant":QPixmap(localLink+"/icon/solutre/Habitant_cell.png"),"Tourisme":QPixmap(localLink+"/icon/solutre/Tourisme_cell.png")})
VillageSud.newPov("Zones joueurs","zone",{"Elu":QPixmap(localLink+"/icon/solutre/Elu_cell.png"),"Habitant":QPixmap(localLink+"/icon/solutre/Habitant_cell.png"),"Tourisme":QPixmap(localLink+"/icon/solutre/Tourisme_cell.png")})
VillageEst.newPov("Zones joueurs","zone",{"Elu":QPixmap(localLink+"/icon/solutre/Elu_cell.png"),"Habitant":QPixmap(localLink+"/icon/solutre/Habitant_cell.png"),"Tourisme":QPixmap(localLink+"/icon/solutre/Tourisme_cell.png")})

#* --------------------------
#* Dashboard des indicateurs
#* -------------------------- 
# Création du dashboard des indicateurs
# Chaque indicateur affiche la valeur portée par une variable de simulation
DashBoardInd=myModel.newDashBoard("Suivi des indicateurs")
qualiteVie=myModel.newSimVariable("Qualité de vie",0)
environnement=myModel.newSimVariable("Environnement",0)
attractivite=myModel.newSimVariable("Attractivité",0)
indQualiteVie=DashBoardInd.addIndicatorOnSimVariable(qualiteVie)
indAttractivite=DashBoardInd.addIndicatorOnSimVariable(attractivite)
indEnvironnement=DashBoardInd.addIndicatorOnSimVariable(environnement)

#* --------------------------
#* Jauges des indicateurs
#* -------------------------- 
# #* On affiche les valeurs des variables de simulation par des jauges : 
# celles ci sont mises à jour automatiquement lorsqu'une variable de simulation est modifiée
# les jauges peuvent avoir des valeurs seuils qui déclenchent des actions
# declaration des jauges (progressGauge)

# Construire colorRanges pour que la couleur des jauges varie en fonctions des valeurs seuils déterminées dans le jeu 
jaugeQDV_colorRanges = [
    (0, 2,QColor.fromRgb(198, 237, 195)), 
    (3, 20,"green"),
    (-3, -1, QColor.fromRgb(255, 204, 203)),
    (-10, -4, "red") ]
jaugeAtt_colorRanges = generate_color_gradient(
    "green",
    mapping={"values": [1, 3, 5, 6, 7], "value_min": 0, "value_max": 7},
    as_ranges=True)
negativeRanges = [
    (-3, -1, QColor.fromRgb(255, 204, 203)),
    (-10, -4, "red") ]
jaugeAtt_colorRanges[:0] = negativeRanges

jaugeEnv_colorRanges = generate_color_gradient(
    "green",
    mapping={"values": [6, 7, 15], "value_min": 0, "value_max": 10},
    as_ranges=True)
jaugeEnv_colorRanges[:0] = negativeRanges

# construire les jauges, en y integrant les colorRanges
jaugeQDV=myModel.newProgressGauge(qualiteVie,-10,10,"Qualité de vie",colorRanges=jaugeQDV_colorRanges)
jaugeEnv=myModel.newProgressGauge(environnement,-10,10,"Environnement",colorRanges=jaugeEnv_colorRanges)
jaugeAtt=myModel.newProgressGauge(attractivite,-10,10,"Attractivité",colorRanges=jaugeAtt_colorRanges)

# déclaration des variables de simulation qui vont contenir les bonus des jauges
bonusVin=myModel.newSimVariable("Bonus vin",0)
bonusBio=myModel.newSimVariable("Bonus vin bio",0)
bonusTouriste=myModel.newSimVariable("Bonus touriste",-1)
bonusEnvironnement=myModel.newSimVariable("Bonus environnement",0)

# On définit les valeurs seuils des jauges qui déclenchent des actions et les actions associées
jaugeEnv.setThresholdValue(6, lambda: bonusBio.incValue(2), lambda: bonusBio.decValue(2))

jaugeAtt.setThresholdValue(5, lambda: bonusVin.incValue(1), lambda: bonusVin.decValue(1))
jaugeAtt.setThresholdValue(5, lambda: bonusBio.incValue(1), lambda: bonusBio.decValue(1))
jaugeAtt.setThresholdValue(7, lambda: bonusVin.incValue(1), lambda: bonusVin.decValue(1))
jaugeAtt.setThresholdValue(7, lambda: bonusBio.incValue(1), lambda: bonusBio.decValue(1))
jaugeAtt.setThresholdValue(3, lambda: bonusTouriste.incValue(1), lambda: bonusTouriste.decValue(1))
jaugeAtt.setThresholdValue(1, lambda: bonusTouriste.incValue(1), lambda: bonusTouriste.decValue(1))
jaugeAtt.setThresholdValue(5, lambda: bonusTouriste.incValue(1), lambda: bonusTouriste.decValue(1))
jaugeAtt.setThresholdValue(6, lambda: bonusTouriste.incValue(1), lambda: bonusTouriste.decValue(1))
jaugeAtt.setThresholdValue(7, lambda: bonusTouriste.incValue(2), lambda: bonusTouriste.decValue(2))

jaugeEnv.setThresholdValue(7, lambda: bonusEnvironnement.incValue(1), lambda: None)
jaugeEnv.setThresholdValue(15, lambda: bonusEnvironnement.incValue(1), lambda: None)


#* --------------------------
#* Dashboard des services
#* --------------------------
# Création du dashboard des services (même principe que précédemment)
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
# Création des joueurs : TOUS les joueurs sont créés à chaque code de jeu Solutré
Viticulteur = myModel.newPlayer("Viticulteur",attributesAndValues={"nbCubes":6,"Sous":0})
Tourisme = myModel.newPlayer("Tourisme",attributesAndValues={"nbCubes":6,"Sous":0})
Elu=myModel.newPlayer("Elu",attributesAndValues={"nbCubes":6,"Sous":0})
Naturaliste=myModel.newPlayer("Naturaliste",attributesAndValues={"nbCubes":6,"Sous":0})
Habitant=myModel.newPlayer("Habitant",attributesAndValues={"nbCubes":6,"Sous":0})


#* --------------------------
#* Déclaration des agents
#* --------------------------
# Création des agents : représente les pions du jeu Solutré
# Ici nous créons les "espèces" d'agents, qui servent de modèle pour la création des pions individuels
Touriste=myModel.newAgentSpecies("Touriste","circleAgent",defaultSize=40,defaultImage=QPixmap(localLink+"/icon/solutre/touriste.png"))
Bouteille=myModel.newAgentSpecies("Bouteille de vin","circleAgent",defaultSize=40,defaultImage=QPixmap(localLink+"/icon/solutre/vin.png"))
BouteilleBio=myModel.newAgentSpecies("Bouteille de vin bio","circleAgent",defaultSize=40,defaultImage=QPixmap(localLink+"/icon/solutre/vinBIO.png"))
Buisson=myModel.newAgentSpecies("Buisson","circleAgent",defaultSize=40,defaultColor=Qt.darkGreen,locationInEntity="center")
reserve=myModel.newCellsOnGrid(1,1,"square",size=120,gap=0,name="Réserve")
reserve.getEntity(1,1).setValue("zone",True)
reserve.newPov("Zones joueurs","zone",{True:Qt.darkGray})

#* --------------------------
#* Dashboard des ressources
#* --------------------------
# Création du dashboard des ressources (même principe que précédemment)
DashBoardRessources=myModel.newDashBoard("Ressources")
touriste=myModel.newSimVariable("touriste",0)
vin=myModel.newSimVariable("vin",0)
vinBio=myModel.newSimVariable("vinBio",0)
indVin=DashBoardRessources.addIndicatorOnSimVariable(vin)
indVinBio=DashBoardRessources.addIndicatorOnSimVariable(vinBio)
indTouriste=DashBoardRessources.addIndicatorOnSimVariable(touriste)
DashBoardRessources.addIndicator(Touriste,"nb")


def createHex(nom,species,dataInst,dataAct,dataPerm=None,model=myModel):
    """Cette fonction permet de créer une tuile hexagone à partir du nom de celle-ci et des données issues des tableaux excel"""
    variables=myModel.getSimVars()
    
    # Création des effets instantanés
    ligneHexInst = dataInst[dataInst['nom'] == nom]
    if ligneHexInst.empty:
        return print(f"L'entité '{nom}' n'existe pas dans le fichier Excel Inst.")
        
    
    coutCubes=int(ligneHexInst['coutCubes'].values[0])
    colonnesJauges= dataInst.loc[:, 'Qualité de vie':'vinBio'].columns
    effetInstantaneJauge = {}
    for col in colonnesJauges:
        variable=next((var for var in variables if var.name == col), None)
        if variable is not None:
            effetInstantaneJauge[variable] = int(ligneHexInst[col].values[0]) if not math.isnan(ligneHexInst[col].values[0]) else 0
    joueur=model.getPlayer(ligneHexInst["joueur"].values[0]) if not "Plateau" in ligneHexInst["joueur"].values[0] else None

    conditionAdjacence=ligneHexInst["conditionAdjacence"].values[0] if isinstance(ligneHexInst["conditionAdjacence"].values[0], str) else None
    nbAdjacence=ligneHexInst["nbAdjacence"].values[0] if not math.isnan(ligneHexInst["nbAdjacence"].values[0]) else 1
    conditionFeedbackAdjacence=ligneHexInst["conditionFeedbackAdjacence"].values[0] if isinstance(ligneHexInst["conditionFeedbackAdjacence"].values[0], str) else None
    feedbackAdjacenceAttractivité=ligneHexInst["feedbackAdjacenceAttractivité"].values[0] if not math.isnan(ligneHexInst["feedbackAdjacenceAttractivité"].values[0]) else 0

    image = localLink + ligneHexInst["image recto"].values[0].lstrip(".") if isinstance(ligneHexInst["image recto"].values[0], str) else None
    
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
        if res == "sous":
            effetRessourcesAct["Sous"] = int(ligneHexAct[res].values[0]) if not math.isnan(ligneHexAct[res].values[0]) else 0

    effetActivableJauge={}
    colonnesJauges= dataAct.loc[:, 'Biodiversité':'Qualité de vie'].columns
    for col in colonnesJauges:
        variable=next((var for var in variables if var.name == col), None)
        if variable is not None:
            effetActivableJauge[variable] = int(ligneHexAct[col].values[0]) if not math.isnan(ligneHexAct[col].values[0]) else 0
    
    image_ACT = localLink + ligneHexAct["image verso"].values[0].lstrip(".") if isinstance(ligneHexAct["image verso"].values[0], str) else None

    coutTouriste=int(ligneHexAct['coutTouriste'].values[0]) if not math.isnan(ligneHexAct['coutTouriste'].values[0]) else 0
    effetActivableTouriste={
        "Sous":int(ligneHexAct['feedbackTouristeSous'].values[0]) if not math.isnan(ligneHexAct['feedbackTouristeSous'].values[0]) else 0,
        "Attractivité":int(ligneHexAct['feedbackTouristeAttractivité'].values[0]) if not math.isnan(ligneHexAct['feedbackTouristeAttractivité'].values[0]) else 0,
        "Qualité de vie": int(ligneHexAct['feedbackTouristeQDV'].values[0]) if not math.isnan(ligneHexAct['feedbackTouristeQDV'].values[0]) else 0,
    }
    

    entite = hexagones.newAgentAtCoords(pioche,6,1,{'nom': nom,'coûtCubes': coutCubes, 'joueur':joueur, 'nom':nom, 'effetInstantaneJauge': effetInstantaneJauge, 'coutCubesAct': coutCubesAct, 'coutVin':coutVin, 'coutVinBio':coutVinBio,'coutSous':coutSous,"effetRessourcesAct":effetRessourcesAct,"effetActivableJauge":effetActivableJauge,"coutTouriste":coutTouriste,"effetActivableTouriste":effetActivableTouriste,"conditionAdjacence":conditionAdjacence,"nbAdjacence":nbAdjacence,"conditionFeedbackAdjacence":conditionFeedbackAdjacence,"feedbackAdjacenceAttractivité":feedbackAdjacenceAttractivité,"placed":False},image=QPixmap(image_ACT),popupImage=image)
    return

def createAllHex(species,dataInst,dataAct,dataPerm=None,model=myModel):
    """Cette fonction permet de créer toutes les tuiles hexagones à partir des données issues des tableaux excel"""
    listOfHex=list(dataInst['nom'])
    for aHexName in listOfHex:
        createHex(aHexName,species,dataInst,dataAct,dataPerm,model)
    
def createPlayerHex(aPlayerName, species, dataInst, dataAct, dataPerm=None, model=myModel):
    """Cette fonction permet de créer les tuiles hexagones d'un joueur à partir des données issues des tableaux excel"""
    playerHex = dataInst[dataInst['joueur'] == aPlayerName]['nom'].tolist()
    random.shuffle(playerHex)
    for hexName in playerHex:
        createHex(hexName, species, dataInst, dataAct, dataPerm, model)

hexagones=myModel.newAgentSpecies("Hexagone","hexagonAgent",{"coûtCubes":0,"joueur":None,"nom":None,"effetInstantaneJauge":None,"condPlacement":None,'coutCubesAct': None, 'coutVin':None, 'coutVinBio':None,'coutSous':None,"effetRessourcesAct":None,"effetActivableJauge":None,"face":"recto","imageFace":None},defaultSize=80,locationInEntity="center")
hexagones.newBorderPovColorAndWidth("Activation","Activation",{False:[Qt.black,1],True:[Qt.yellow,2]})
hexagones.setDefaultValue("Activation",False)
pioche=myModel.newCellsOnGrid(6,1,"square",size=80,gap=20,name="Pioche")
pioche.getEntity(6,1).setValue("zone",True)
pioche.newPov("Zones joueurs","zone",{True:Qt.darkGray})

#* --------------------------
#* GameActions
#* --------------------------
GameActionsList=[]
TourismeSpecificActions=[]

def createPlayerCommuneGA():
    """Cette fonction permet de créer les actions communes à tous les joueurs"""
    # Action pour déplacer un hexagone sur les plateaux
    MoveHexagone=myModel.newMoveAction(hexagones, 'infinite')
    MoveHexagone.addCondition(lambda aHex,aTargetCell : aTargetCell.value("zone") not in ["Village Nord","Village Sud","Village Est"])
    MoveHexagone.addCondition(lambda aHex,aTargetCell : checkIfAHexIsHere(aTargetCell))
    MoveHexagone.addCondition(lambda aHex: aHex.value("placed")==False)
    GameActionsList.append(MoveHexagone)
    # Action pour valider le placement d'un hexagone
    ValiderMoveHexagone=myModel.newActivateAction(hexagones, lambda aHex : execeffetInstantaneJauge(aHex),setControllerContextualMenu=True,aNameToDisplay="Valider le placement")
    ValiderMoveHexagone.addCondition(lambda aHex: aHex.value("placed")==False)
    ValiderMoveHexagone.addCondition(lambda aHex: checkAdjacence(aHex))
    ValiderMoveHexagone.addCondition(lambda aHex: aHex.value("joueur").value("nbCubes")>=aHex.value("coûtCubes"))
    ValiderMoveHexagone.addCondition(lambda aHex: aHex.cell.grid.id!="Pioche")
    ValiderMoveHexagone.addFeedback(lambda aHex: adjacenceFeedback(aHex))
    GameActionsList.append(ValiderMoveHexagone)
    # Action pour déplacer un hexagone sur la pioche
    MovePioche=myModel.newMoveAction(hexagones, 'infinite',setOnController=False)
    MovePioche.addCondition(lambda aHex,aTargetCell: aTargetCell.grid.id=="Pioche")
    GameActionsList.append(MovePioche)
    # Action pour activer un hexagone
    ActivateHexagone=myModel.newActivateAction(hexagones,lambda aHex : execeffetActivableJauge(aHex),setControllerContextualMenu=True,aNameToDisplay="Activer l'hexagone")
    ActivateHexagone.addCondition(lambda aHex: aHex.value("joueur").value("nbCubes")>=aHex.value("coutCubesAct"))
    ActivateHexagone.addCondition(lambda aHex: checkRessources(aHex))
    ActivateHexagone.addCondition(lambda aHex: checkIfActivable(aHex))
    ActivateHexagone.addCondition(lambda aHex: aHex.value("Activation")==False)
    ActivateHexagone.addCondition(lambda aHex: aHex.value("placed")==True)
    ActivateHexagone.addFeedback(lambda aHex: decRessources(aHex))
    GameActionsList.append(ActivateHexagone)
    # Action pour supprimer un buisson
    DeleteBuisson=myModel.newDeleteAction(Buisson,conditions= [lambda : checkCubesBuisson()],feedbacks= [lambda : decCubesBuisson()],setControllerContextualMenu=True,aNameToDisplay="Supprimer le buisson")
    GameActionsList.append(DeleteBuisson)
    return GameActionsList

GameActionsList = createPlayerCommuneGA()

def createTourismeSpecificGA():
    """Cette fonction permet de créer les actions spécifiques au joueur Tourisme"""
    # Action pour placer un touriste
    PlaceTouriste=myModel.newMoveAction(Touriste,"infinite",setOnController=False)
    PlaceTouriste.addCondition(lambda: checkIsThereTouristes())
    PlaceTouriste.addCondition(lambda aTourist, aTargetCell: checkIsHebergement(aTargetCell))
    PlaceTouriste.addFeedback(lambda: decTouristes())
    PlaceTouriste.addFeedback(lambda aTourist: execeffetActivableTouriste(aTourist))
    TourismeSpecificActions.append(PlaceTouriste)
    return TourismeSpecificActions

TourismeSpecificActions = createTourismeSpecificGA()

def checkIfAHexIsHere(aTargetCell):
    """Permet de vérifier si une tuile hexagone est déjà présente sur une cellule de plateau"""
    return aTargetCell.isEmpty(specie="Hexagone")

def execeffetInstantaneJauge(aHex):
    """Détaille les actions réalisées au placement d'un hexagone"""
    for jauge, valeur in aHex.value("effetInstantaneJauge").items():
        if jauge != "Biodiversité":
            jauge.incValue(valeur)
        else:
            jauge.incValue(valeur+bonusEnvironnement.value)
    updateCubes(aHex)
    aHex.setValue("placed",True)

def updateCubes(aHex):
    """Permet de mettre à jour le nombre de cubes d'un joueur après le placement d'un hexagone"""
    player=aHex.value("joueur")
    player.decValue("nbCubes",aHex.value("coûtCubes"))

def execeffetActivableJauge(aHex):
    """Détaille les actions réalisées à l'activation d'un hexagone"""
    for jauge,valeur in aHex.value("effetActivableJauge").items():
        if jauge != "Biodiversité":
            jauge.incValue(valeur)
        else:
            jauge.incValue(valeur+bonusEnvironnement.value)
    for ressource,valeur in aHex.value("effetRessourcesAct").items():
        if ressource != "Sous":
            ressource.incValue(valeur)
        else:
            if aHex.value("coutVinBio")>0 and aHex.value("joueur") == "Viticulteur":
                aHex.value("joueur").incValue("Sous",(valeur+bonusBio.value)*aHex.value("coutVinBio"))
            elif aHex.value("coutVin")>0 and aHex.value("joueur") == "Viticulteur":
                aHex.value("joueur").incValue("Sous",(valeur+bonusVin.value)*aHex.value("coutVin"))
            elif aHex.value("coutVinBio")>0 :
                aHex.value("joueur").incValue("Sous",valeur*aHex.value("coutVinBio"))
                Viticulteur.incValue("Sous",(bonusBio.value)*aHex.value("coutVinBio"))
            elif aHex.value("coutVin")>0:
                aHex.value("joueur").incValue("Sous",valeur*aHex.value("coutVin"))
                Viticulteur.incValue("Sous",(bonusVin.value)*aHex.value("coutVin"))
            else:
                aHex.value("joueur").incValue("Sous",valeur)
    updatesCubesActivation(aHex)
    aHex.setValue("Activation",True)
    

def checkIfActivable(aHex):
    """Permet de vérifier si un hexagone est activable"""
    values= list(aHex.value("effetActivableJauge").values())+list(aHex.value("effetRessourcesAct").values())
    return any(val != 0 for val in values)


def checkRessources(aHex):
    """Permet de vérifier si les ressources nécessaires sont présentes pour activer un hexagone"""
    model=aHex.model
    simVars=model.getSimVars()
    vin = next((aSimVar for aSimVar in simVars if aSimVar.name == "vin"), None)
    vinBio = next((aSimVar for aSimVar in simVars if aSimVar.name == "vinBio"), None)
    if aHex.value("coutVin")>0 :
        if vin.value>=aHex.value("coutVin"): return True
        else: return False
    elif aHex.value("coutVinBio")>0:
        if vinBio.value>=aHex.value("coutVinBio"): return True
        else: return False
    elif aHex.value("coutSous")>0:
        if aHex.value("joueur").value("Sous")>=aHex.value("coutSous"): return True
        else: return False
    else: return True

def decRessources(aHex):
    """Permet de mettre à jour les ressources après l'activation d'un hexagone"""
    model=aHex.model
    simVars=model.getSimVars()
    vin = next((aSimVar for aSimVar in simVars if aSimVar.name == "vin"), None)
    vinBio = next((aSimVar for aSimVar in simVars if aSimVar.name == "vinBio"), None)
    vin.decValue(aHex.value("coutVin"))
    vinBio.decValue(aHex.value("coutVinBio"))
    aHex.value("joueur").decValue("Sous",aHex.value("coutSous"))


def updatesCubesActivation(aHex):
    """Permet de mettre à jour le nombre de cubes d'un joueur après l'activation d'un hexagone"""
    player=aHex.value("joueur")
    player.decValue("nbCubes",aHex.value("coutCubesAct"))

def checkCubesBuisson():
    """Permet de vérifier si un joueur a assez de cubes pour réaliser supprimer un buisson"""
    player=myModel.getPlayer(myModel.currentPlayer)
    if player.value("nbCubes")>=1: return True
    else: return False

def decCubesBuisson():
    """Permet de mettre à jour le nombre de cubes d'un joueur après la suppression d'un buisson"""
    player=myModel.getPlayer(myModel.currentPlayer)
    player.decValue("nbCubes")

def checkIsThereTouristes(): # todo cette verification est inutile a priori
    """Permet de vérifier si des touristes sont présents dans la réserve"""
    if touriste.value >= 1: return True
    else: return False

def checkIsHebergement(aTargetCell):
    """Permet de vérifier si l'emplacement permet d'acceuillir un touriste supplémentaire"""
    nbTouristesHere=aTargetCell.nbAgents(Touriste)
    aHex=aTargetCell.getFirstAgentOfSpecie(hexagones)
    if aHex is not None:
        if aHex.value("coutTouriste") > nbTouristesHere : return True
    return False

def decTouristes():
    """Permet de mettre à jour le nombre de touristes après leur placement"""
    touriste.decValue()

def execeffetActivableTouriste(aTourist):
    """Détaille les actions réalisées à l'activation d'un hexagone par le placement d'un touriste"""
    aTargetCell=aTourist.cell
    aHex=aTargetCell.getAgents(specie="Hexagone")[0]
    dictOfValues=aHex.value("effetActivableTouriste")
    attractivite.incValue(int(dictOfValues.get("Attractivité")))
    qualiteVie.incValue(int(dictOfValues.get("Qualité de vie")))
    Tourisme.incValue("Sous",int(dictOfValues.get("Sous")))
    
def checkAdjacence(aHex):
    """Permet de vérifier si un hexagone est placé à côté d'un autre hexagone en fonction des besoins"""
    if aHex.value("conditionAdjacence") is not None:
        listOfNeighbours=aHex.getNeighborCells()
        nbMatchingNeighbour = 0
        for aNeighbourCell in listOfNeighbours:
            aNeighbourHex = aNeighbourCell.getFirstAgentOfSpecie(hexagones)
            if aHex.value("conditionAdjacence") == aNeighbourCell.value("zone"): 
                if aHex.value("nbAdjacence") == 1: return True
                else:
                    nbMatchingNeighbour += 1
                    if aHex.value("nbAdjacence") == nbMatchingNeighbour:
                        return True
            elif aNeighbourHex is not None:
                if aHex.value("conditionAdjacence") in ["Service public","Espace de démocratie"]:
                    
                    for jauge, value in aNeighbourHex.value("effetActivableJauge").items():
                        if jauge.name == aHex.value("conditionAdjacence"): return True
                elif aHex.value("conditionAdjacence") in ["vinBio","vin"]:
                    for ressource, value in aNeighbourHex.value("effetRessourcesAct").items():
                        for aRessource in aHex.value("effetRessourcesAct").items():
                            if ressource == "Sous": return True
                            if aRessource[0].name == ressource.name: return True
                elif aHex.value("conditionAdjacence") == "coutTouriste" and aNeighbourHex.value("coutTouriste")>0: return True
    else: return True

def adjacenceFeedback(aHex):
    """Détaille les actions réalisées à l'activation d'un hexagone par la présence d'un autre hexagone à côté"""
    if aHex.value("conditionFeedbackAdjacence") == "coutTouriste":
        listOfNeighbours=aHex.getNeighborAgents(aSpecies=hexagones)
        for aNeighbourHex in listOfNeighbours:
            if aNeighbourHex.value("coutTouriste")>0:
                attractivite.incValue()

#* --------------------------
#* Paramètres du modèle
#* --------------------------        
usedKeys=["Au Nom des Roches"]

def execEvent():
    """Détaille les actions de début de tour"""
    randomKey=random.choice(list(dataEvents["Nom"]))
    while randomKey in usedKeys:
        randomKey=random.choice(list(dataEvents["Nom"]))
    eventLine=dataEvents[dataEvents['Nom']==randomKey]
    usedKeys.append(randomKey)
    myModel.newPopUp(eventLine['Nom'].squeeze(),eventLine["Descriptif"].squeeze()+" Nombre de touristes cette année :"+str(eventLine["nbTouristes"].squeeze()))
    Touriste.newAgentsAtCoords(int(eventLine["nbTouristes"].squeeze()+bonusTouriste.value),reserve,1,1)
    touriste.incValue(int(eventLine["nbTouristes"].squeeze()+bonusTouriste.value))
   
def execFirstEvent():
    """Détaille les actions de début de partie"""
    eventLine=dataEvents[dataEvents['Nom'] == "Au Nom des Roches"]
    myModel.newPopUp(eventLine['Nom'].squeeze(),eventLine["Descriptif"].squeeze()+" Nombre de touristes cette année :"+str(eventLine["nbTouristes"].squeeze()))
    Touriste.newAgentsAtCoords(int(eventLine["nbTouristes"].squeeze()),reserve,1,1)
    touriste.incValue(int(eventLine["nbTouristes"].squeeze()))
            
def checkTouriste():
    """Permet de vérifier si des touristes n'ont pas été placés"""
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
    """Permet de vérifier si des buissons n'ont pas été entretenus"""
    nbBuisson=Buisson.nbOfEntities()
    if nbBuisson != 0:
        for n in range(nbBuisson):
            aInd=random.choice([attractivite,qualiteVie,environnement])
            aInd.decValue()
        print(f"Attention ! Cette année, {nbBuisson} buissons n'ont pas été entretenus.")
    Buisson.deleteAllEntities()

def resetHexagones():
    """Permet de remettre les hexagones non placés dans la pioche"""
    nbHexReset=0
    for aHex in hexagones.getEntities():
        if aHex.cell.grid.id!="Pioche" and aHex.value("placed")==False:
            destinationCell=pioche.getEntity(6,1)
            aHex.moveTo(destinationCell)
            nbHexReset=+1
    print(f"{nbHexReset} hexagones ont été remis dans la pioche.")

def resetCubes():
    """Permet de remettre les cubes des joueurs à 6 en début de tour"""
    for player in myModel.getPlayers():
        player.setValue("nbCubes",6)


#PHASE 1 : Début d'années = événements + buissons
eventPopUp=myModel.newModelAction(lambda: execEvent(), lambda: myModel.timeManager.currentRoundNumber > 1)
eventPopUp2= myModel.newModelAction(lambda: execFirstEvent(), lambda: myModel.timeManager.currentRoundNumber == 1)
Embuissonnement=myModel.newModelAction([lambda: Buisson.newAgentsAtRandom(3,Plateau,condition= lambda aCell: aCell.value("zone")=="Roches")])
EventPhase=myModel.timeManager.newModelPhase([eventPopUp,eventPopUp2,Embuissonnement], name="Évènements")
EventPhase.auto_forward=True
EventPhase.message_auto_forward=False

#PHASE 2 : Aménagement du territoire = tous les joueurs peuvent jouer (placer et activer des hexagones)
PlayPhase=myModel.timeManager.newPlayPhase("Phase 1 : Aménager le territoire",[Viticulteur,Elu,Habitant,Naturaliste,Tourisme])

#PHASE 3 : Gestion des touristes = seul le joueur Pro du Tourisme peut jouer
PlayPhase2=myModel.timeManager.newPlayPhase("Phase 2 : Placement des touristes",[Tourisme])

#PHASE 4 : Résolution de l'année = 
unActivatePlateau=myModel.newModelAction([lambda: hexagones.setEntities("Activation",False)])
ModelPhase=myModel.timeManager.newModelPhase([unActivatePlateau,checkTouriste,checkBuisson,resetHexagones,resetCubes],name="Résolution de l'année en cours")
ModelPhase.auto_forward=True
ModelPhase.message_auto_forward=False

# crée l'objet qui affiche les tours de jeu
aTimeLabel = myModel.newTimeLabel()

# fixe la vue du jeu (les couleurs choisies pour les différentes zones)
Plateau.displayBorderPov("Coeur de site")


#* --------------------------
#* Joueur
#* --------------------------
def selectPlayer(aPlayerName, aObjectifCardName="random"):
    """Permet de sélectionner quel est le joueur sur cette machine"""
    myModel.setCurrentPlayer(aPlayerName)
    player=myModel.getPlayer(aPlayerName)
    if aObjectifCardName=="random":
        objectif=getRandomObjectif()
    else:
        objectif=getObjectif(aObjectifCardName)
    color=getColorByPlayer(aPlayerName)
    aDashboard=myModel.newDashBoard(f"{aPlayerName}",backgroundColor=color)
    aDashboard.addIndicatorOnEntity(player,"nbCubes",title="Nombre de cubes actions restant")
    aDashboard.addIndicatorOnEntity(player,"Sous",title="Sous")

    createPlayerHex(aPlayerName,hexagones,data_inst,data_act)

    for action in GameActionsList:
        player.addGameAction(action)
   
    for action in TourismeSpecificActions:
        Tourisme.addGameAction(action)

    return objectif, aDashboard

def getObjectif(aCardName):
    """Choisis un objectif pour le joueur choisi par un nom"""
    player = myModel.currentPlayer
    objectifs_joueur = data_objectifs[data_objectifs['Joueur'] == player]
    objectif = objectifs_joueur[objectifs_joueur['Nom'] == aCardName]
    if not objectif.empty:
        objectif_dict = objectif.to_dict(orient='records')[0]
        title = objectif_dict.pop('Nom')
        text = "\n".join([f"{key}: {value}" if "Unnamed" not in key else f"{value}" for key, value in objectif_dict.items()])
        textBoxObj = myModel.newTextBox(textToWrite=text, title=title)
        return textBoxObj
    else:
        return ValueError("Le nom d'objectif n'est pas correct ou le joueur n'a pas été spécifié.")

def getRandomObjectif():
    """Choisis un objectif aléatoire pour le joueur choisi"""
    player=myModel.currentPlayer
    objectifs_joueur = data_objectifs[data_objectifs['Joueur'] == player]
    if not objectifs_joueur.empty:
        objectif = objectifs_joueur.sample(n=1)
    if not objectif.empty:
        objectif_dict = objectif.to_dict(orient='records')[0]
        title = objectif_dict.pop('Nom')
        text = "\n".join([f"{key}: {value}" if "Unnamed" not in key else f"{value}" for key, value in objectif_dict.items()])
        textBoxObj=myModel.newTextBox(textToWrite=text, title=title)
        return textBoxObj
    else:
        return ValueError("Le joueur n'a pas été spécifié.")
    
def getColorByPlayer(aPlayerName):
    """Permet de choisir la couleur du dashboard en fonction du joueur"""
    if aPlayerName=="Viticulteur":
        return QColor.fromRgb(147,1,208)
    elif aPlayerName=="Tourisme":
        return QColor.fromRgb(254,254,1)
    elif aPlayerName=="Naturaliste":
        return QColor.fromRgb(0,128,0)
    elif aPlayerName=="Habitant":
        return QColor.fromRgb(254,140,1)
    elif aPlayerName=="Elu":
        return QColor.fromRgb(31,143,254)
    else:
        raise ValueError("Le nom du joueur n'est pas correct.")

def createInitHexagones():
    """Crée les hexagones initiaux sur le plateau"""
    if myModel.currentPlayer != "Viticulteur":
        createHex("Vigne du plateau",hexagones,data_inst,data_act)
        createHex("Caveau du plateau",hexagones,data_inst,data_act)
    createHex("Chambre d'hôtes du plateau",hexagones,data_inst,data_act)
    createHex("Chambre d'hôtes du plateau",hexagones,data_inst,data_act)

objectif, DashBoardPlayer = selectPlayer("Elu")
createInitHexagones()

def customLayout():
    """Crée le layout personnalisé du jeu"""
    Plateau.grid.moveToCoords(440,200)
    VillageNord.grid.moveToCoords(30,200)
    VillageEst.grid.moveToCoords(1180,368)
    VillageSud.grid.moveToCoords(30,450)
    pioche.grid.moveToCoords(480,750)
    reserve.grid.moveToCoords(1330,695)
    DashBoard.moveToCoords(1230,40)
    DashBoardRessources.moveToCoords(1400,40)
    DashBoardInd.moveToCoords(1580,40)
    DashBoardPlayer.moveToCoords(1485,695)
    aTimeLabel.moveToCoords(30,40)
    jaugeQDV.moveToCoords(245,40)
    jaugeEnv.moveToCoords(920,40)
    jaugeAtt.moveToCoords(575,40)
    objectif.moveToCoords(1160,695)

def placeInitHexagones():
    """Place les hexagones initiaux sur le plateau"""
    n=0
    cells=[VillageSud.getCell(3,5),VillageNord.getCell(3,1)]
    for aHex in hexagones.getEntities():
        if aHex.value("placed")==False:
            if aHex.value("nom")=="Vigne du plateau":
                aHex.setValue("placed",True)
                aHex.moveTo(Plateau.getCell(8,4))
                
            if aHex.value("nom")=="Caveau du plateau":
                aHex.setValue("placed",True)
                aHex.moveTo(Plateau.getCell(8,5))
                
            if aHex.value("nom")=="Chambre d'hôtes du plateau":
                aHex.setValue("placed",True)
                aHex.moveTo(cells[n])
                n=+1
                


customLayout()
placeInitHexagones()
myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())