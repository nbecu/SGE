# CONTEXT_SGE_FOR_CHATBOT.md
# Guide de contexte pour les assistants IA

## Objectif
Ce fichier contient les informations essentielles pour que les chatbots comprennent rapidement le contexte du projet SGE et suivent les bonnes pratiques de développement.

## Contexte général du projet SGE

SGE (Simulation Game Editor) est une solution Python basée sur PyQt5 qui permet de créer des jeux de simulation basés sur une grille avec une approche agent-based. 

**Caractéristiques uniques de SGE** :
- **Distributed asymmetric simulations** : Chaque joueur peut interagir selon ses compétences et sa compréhension
- **Viewpoints, players, game actions et game phases** intégrés directement dans la structure
- **Interface utilisateur spécifique** pour chaque terminal d'ordinateur
- **Approche modulaire** : Définir les éléments structurels et configurer les variables

**Architecture** :
- **Examples/** : Exemples de jeux
- **mainClasses/** : Classes principales du framework
- **Game/** : Jeux créés par les utilisateurs

## RÈGLE CRITIQUE - Langue de codage
**TOUT le code, commentaires et docstrings DOIVENT être en anglais.**
- Code : anglais
- Commentaires : anglais  
- Docstrings : anglais
- Documentation : anglais
- **Seule la discussion dans le chat peut être en français**

## 1. Rôles et terminologie

SGE distingue trois types d'utilisateurs :
- **Player** : Personne qui interagit avec un jeu/simulation SGE
- **Modeler** : Personne qui développe un jeu/simulation avec SGE
- **Developer** : Personne qui développe de nouvelles fonctionnalités pour SGE

**Utilisez toujours ces termes exacts** dans la documentation et les commentaires.

## 2. Conventions de nommage

- **Fonctions et variables** : `snake_case` (ex: `auto_forward`, `player_score`)
- **Méthodes et fonctions** : `camelCase` (ex: `newModelPhase`, `getEntityByName`)

## 3. Keywords réservés pour les noms de méthodes

Utilisez ces préfixes pour les méthodes destinées aux modelers :

- **new** : Créer un nouveau type d'entité ou instance (ex: `newCellsOnGrid`, `newAgentAtCoords()`)
- **get** : Accéder ou récupérer un élément (ex: `getPlayer`, `getScore`)
- **delete** : Supprimer un élément (ex: `deleteEntity`, `deleteAllAgents()`)
- **set** : Modifier une valeur ou propriété (ex: `setParameter`, `setName`)
- **add** : Ajouter un élément ou fonctionnalité (ex: `addAction`, `addIndicator`)
- **nb** : Obtenir le nombre d'entités/objets
- **is** : Effectuer un test (retourne True/False) (ex: `isDeleted()`)
- **do_** : Effectuer une action sur une entité
- **display** : Afficher un élément sur l'interface SGE

## 4. Attributs d'identification de type

Utilisez des attributs booléens avec le préfixe `is` :

- **`isAdmin`** : Pour les joueurs admin
- **`isAgentDef`** : Pour les définitions d'agents
- **`isCellDef`** : Pour les définitions de cellules
- **`isLegend`** : Pour les composants UI de légende
- **`isControlPanel`** : Pour les interfaces de contrôle

## 5. Ergonomie API et délégation

### Méthodes de délégation
Préférez créer des méthodes de délégation dans les classes principales :

```python
# Au lieu de: model.timeManager.newPlayPhase(...)
# Utilisez: model.newPlayPhase(...)
```

### Getters d'instances
Utilisez des méthodes getter avec le préfixe `get` :

```python
# Au lieu de: model.adminPlayer
# Utilisez: model.getAdminPlayer()

def getAdminPlayer(self):
    return self.players.get("Admin")
```

### Création d'instances complexes
Utilisez des méthodes avec le préfixe `new` :

```python
def newModifyActionWithDialog(self, entityDef, attribute):
    # Creates a modify action that prompts user for value
```

## 6. Architecture Model-View (CRITIQUE - OBLIGATOIRE)

**RÈGLE ABSOLUE** : SGE utilise une architecture Model-View. Chaque entité a un Model (logique) + View (UI).

**Classes principales** :
- `SGAgent` = Model (logique agent)
- `SGAgentView` = View (UI agent)  
- `SGCell` = Model (logique cellule)
- `SGCellView` = View (UI cellule)

**INTERDICTION STRICTE** : Ne jamais créer `SGAgent(x,y)` directement. Utiliser TOUJOURS les méthodes factory.

**Hiérarchie des méthodes factory dans SGE** :

SGE utilise plusieurs niveaux de méthodes factory selon le type d'élément à créer :

### 1. Méthodes factory pour les définitions d'entités (EntityDef)
```python
# Créer une définition de cellules + grille (gameSpace)
cellDef = model.newCellsOnGrid(columns=10, rows=10, format="square", size=30)
# Particularité : crée à la fois les entités ET une grille (gameSpace)

# Créer une définition d'agents (espèce)
agentDef = model.newAgentSpecies("Sheeps", "circleAgent", defaultColor=Qt.gray)
```

### 2. Méthodes factory pour les instances d'entités (Model-View)
```python
# Créer des instances d'agents (Model + View automatiquement)
agent = agentDef.newAgentAtCoords(x, y)  # Crée Model + View automatiquement
agent = agentDef.newAgentOnCell(cell)    # Alternative avec cellule

# Créer des instances de cellules (Model + View automatiquement)  
cell = cellDef.newCell(x, y)            # Crée Model + View automatiquement
```

### 3. Méthodes factory pour les gameSpaces (widgets d'interface)
```python
# Créer une légende (widget d'affichage)
legend = model.newLegend("Global Legend", alwaysDisplayDefaultAgentSymbology=True)

# Créer un sélecteur d'utilisateur (widget de contrôle)
userSelector = model.newUserSelector()

# Créer un tableau de bord (widget de scores et indicateurs)
dashBoard = model.newDashBoard(title="Scores", borderColor=Qt.black, textColor=Qt.black)

# Créer une jauge de progression (widget de monitoring)
progressGauge = model.newProgressGauge(simVar, minimum=0, maximum=100, title="Progress")

# Créer un affichage de temps (widget temporel)
timeLabel = model.newTimeLabel("Game Time", backgroundColor=Qt.white, textColor=Qt.black)

# Créer des règles de fin de jeu (widget de conditions)
endGameRule = model.newEndGameRule(title="EndGame Rules", numberRequired=1)

# Créer une boîte de texte (widget d'affichage de texte)
textBox = model.newTextBox("Welcome to the game!", title="Instructions")

# Créer un label simple (widget de texte basique)
label = model.newLabel("Score: 100", position=(100, 50), textStyle_specs="font-size: 14px; color: blue")

# Créer un label stylisé (widget de texte avancé)
label_stylised = model.newLabel_stylised("Title", position=(200, 100), font="Arial", size=16, color="red", font_weight="bold")

# Créer un panneau de contrôle (widget d'actions de jeu - appelé par un joueur)
controlPanel = player.newControlPanel("Player Actions", defaultActionSelected=gameAction)
```

### 4. Méthodes factory pour les joueurs et leurs gameActions
```python
# Le joueur Admin est créé automatiquement
adminPlayer = model.getAdminPlayer()

# Créer un joueur
player = model.newPlayer("Player 1")

# Ajouter des gameActions à un joueur
player.addGameAction(gameAction)        # Ajouter une action
player.addGameActions([action1, action2])  # Ajouter plusieurs actions

# Méthodes factory pour créer des gameActions
createAction = model.newCreateAction(agentDef, dictAttributes={"health": "good"}, aNumber=5)
modifyAction = model.newModifyAction(cellDef, dictAttributes={"landUse": "forest"}, aNumber='infinite')
modifyActionWithDialog = model.newModifyActionWithDialog(cellDef, "landUse", aNumber='infinite')
deleteAction = model.newDeleteAction(agentDef, aNumber=3)
moveAction = model.newMoveAction(agentDef, aNumber=10)
activateAction = model.newActivateAction(model, aMethod="nextTurn", aNumber='infinite')
```

### 5. Méthodes factory pour les variables de simulation
```python
# Créer une variable de simulation (pour scores, compteurs, etc.)
simVar = model.newSimVariable(name="Score", initValue=0, color=Qt.black, isDisplay=True)

# Utilisation typique avec dashboard
score = model.newSimVariable("Player Score", 100)
dashboard = model.newDashBoard("Scores")
dashboard.addIndicatorOnSimVariable(score)

# Utilisation avec progress gauge
progress = model.newProgressGauge(simVar, minimum=0, maximum=100, title="Progress")

# Méthodes disponibles sur les variables de simulation
simVar.setValue(50)                    # Définir une valeur
simVar.incValue(10)                    # Incrémenter de 10
simVar.decValue(5)                     # Décrémenter de 5
simVar.calcValue(lambda x: x * 1.2)   # Appliquer un calcul
```

### 6. Méthodes factory pour les phases de simulation
```python
# Créer une phase de jeu (phase interactive avec joueurs)
playPhase = model.newPlayPhase(
    phaseName="Player Turn", 
    activePlayers=["Player 1", "Admin"], 
    modelActions=[lambda: print("Phase started")],
    autoForwardWhenAllActionsUsed=True
)

# Créer une phase de modèle (phase automatique sans interaction joueur)
modelPhase = model.newModelPhase(
    actions=[lambda: agent.moveAgent(method="random")],
    condition=lambda: model.roundNumber() > 5,
    name="Automatic Movement",
    auto_forward=True
)

# Ajouter des actions supplémentaires à une phase existante
modelPhase.addAction(lambda: cell.setValue("type", "forest"))
modelPhase.addAction(model.newModelAction_onCells(actions=[lambda cell: cell.doSomething()]))
```

### 7. Méthodes factory pour les modelActions (actions spécifiques aux modelPhase)
```python
# Créer une action générale
modelAction = model.newModelAction(actions=[lambda: doSomething()])

# Créer une action sur toutes les cellules
cellAction = model.newModelAction_onCells(actions=[lambda cell: cell.doSomething()])

# Créer une action sur une espèce d'agents
agentAction = model.newModelAction_onAgents("Sheeps", actions=[lambda agent: agent.moveAgent()])

# Créer une action depuis une EntityDef
entityAction = cellDef.newModelAction(actions=[lambda entity: entity.doSomething()])
```


**Cycle de vie Qt OBLIGATOIRE** :
- `show()` = Rend visible + positioning correct (TOUJOURS appeler après création/déplacement)
- `update()` = Repaint asynchrone (préféré)
- `repaint()` = Repaint synchrone (éviter sauf cas spéciaux)

**RÈGLE CRITIQUE** : Après chaque `moveTo()` ou création d'agent, appeler `agent.view.show()`

## 7. Organisation des méthodes (OBLIGATOIRE)

**Structure de classe OBLIGATOIRE** :
```python
class SGAgent(SGEntity):
    def __init__(self, ...):
        # Developer code
    
    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================
    # Méthodes internes, UI delegation, Model-View
    
    # ============================================================================
    # MODELER METHODS  
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    # Création et modification
    
    # ============================================================================
    # DELETE METHODS
    # ============================================================================
    # Suppression
    
    # ============================================================================
    # GET/NB METHODS
    # ============================================================================
    # Récupération et comptage
    
    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================
    # Tests booléens
    
    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================
    # Actions et affichage
```

**RÈGLE** : Respecter cette structure exacte dans toutes les classes SGE.

## 8. Règles critiques pour chatbots

**OBLIGATOIRE** :
- Code, commentaires, docstrings = ANGLAIS UNIQUEMENT
- Utiliser méthodes factory pour Model-View
- Appeler `show()` après création/déplacement d'agents
- Respecter structure organisation méthodes
- Utiliser nomenclature cohérente (SGAgent, SGCell)
- Distinguer moveTo() (placement initial) de moveAgent() (mouvement avec patterns)
- Utiliser les méthodes utilitaires de SGExtensions.py pour éviter la duplication

**INTERDIT** :
- Créer `SGAgent(x,y)` directement
- Oublier `show()` après `moveTo()`
- Écrire en français dans le code
- Ignorer l'architecture Model-View

## 9. Message de démarrage pour chaque chat

"**CRITIQUE** : Lire ce fichier avant tout travail sur SGE. 
**RÈGLES ABSOLUES** :
1. Code/commentaires/docstrings = ANGLAIS UNIQUEMENT
2. Architecture Model-View OBLIGATOIRE
3. Utiliser méthodes factory (newAgentAtCoords, newCell)
4. Appeler show() après création/déplacement d'agents
5. Respecter structure organisation méthodes

Attacher README_developer.md et README_modeler.md pour contexte complet."

## 10. Fichiers à toujours attacher

1. **README_developer.md** (contexte complet et détaillé)
2. **README_modeler.md** (contexte utilisateur et architecture)
3. **[Fichier principal sur lequel travailler]**
4. **[Autres fichiers pertinents au contexte]**

## 11. Dépendances et environnement

**Requirements** :
- Python 3.8+
- PyQt5 5.15.9
- numpy 1.24.2
- matplotlib
- SQLAlchemy 2.0.3
- paho-mqtt 1.6.1
- pyrsistent
- pywin32

**Contexte académique** :
- Développé sous la supervision du laboratoire LIENSs (Université de La Rochelle)
- Répond à un besoin académique pour les serious games
- Version présentée à ISAGA 2023

## 12. Exemples critiques pour chatbots

### ✅ CORRECT - Architecture Model-View
```python
def createAgent(self, x, y):
    """Creates agent with proper Model-View architecture"""
    # Use factory method - creates both Model and View
    agent = self.entityDef.newAgentAtCoords(x, y)
    agent.view.show()  # CRITICAL: Always call show()
    return agent

def moveAgent(self, agent, newCell):
    """Moves agent with proper view handling"""
    agent.moveTo(newCell)  # Handles Model-View coordination
    agent.view.show()      # CRITICAL: Ensure proper positioning
```

### ❌ INCORRECT - Violation Model-View
```python
def createAgent(self, x, y):
    """Creates agent - WRONG WAY"""
    agent = SGAgent(x, y)  # ERROR: Missing View creation!
    return agent

def moveAgent(self, agent, newCell):
    """Moves agent - WRONG WAY"""
    agent.moveTo(newCell)  # ERROR: Missing show() call!
```

### ❌ INCORRECT - Français dans le code
```python
def createAgent(self, x, y):
    """Crée un agent - INTERDIT"""
    agent = SGAgent(x, y)
    return agent
```

## 14. API récentes et améliorations (DÉCEMBRE 2024)

### 14.1 API moveAgent unifiée
**Nouvelle signature** : `moveAgent(method='random', target=None, numberOfMovement=1, condition=None)`

**Types de target supportés** :
- `int` : ID numérique de la cellule (ex: `target=5`)
- `tuple` : Coordonnées (ex: `target=(2, 3)`)
- `str` : Direction (ex: `target="up"`, `target="down"`, `target="left"`, `target="right"`)

**Auto-détection** : Si `method='random'` et `target` fourni, la méthode est automatiquement détectée :
- `target=int` → `method='cell'`
- `target=tuple` → `method='cell'` 
- `target=str` → `method='direction'`

**Exemples** :
```python
# Movement by ID
agent.moveAgent(target=5)

# Movement by coordinates  
agent.moveAgent(target=(2, 3))

# Movement by direction
agent.moveAgent(target="up")

# Auto-detection
agent.moveAgent(method='random', target=5)  # Automatically becomes method='cell'
```

### 14.2 Système d'IDs standardisé
**RÈGLE** : Tous les IDs sont maintenant numériques pour cohérence.

**Méthodes concernées** :
- `SGCell.getId()` : Retourne `x + (grid.columns * (y - 1))`
- `SGEntityDef.cellIdFromCoords(x, y)` : Retourne le même ID numérique

**Avantage** : Élimination des incohérences entre string et numeric IDs.

### 14.3 Tooltips optionnels
**Nouvelle méthode** : `displayTooltip(type=None)` dans `SGEntityDef`

**Types supportés** :
- `None` ou `'none'` : Aucun tooltip (par défaut)
- `'coords'` : Affiche `(x, y)`
- `'id'` : Affiche `ID: {id}`
- `'custom'` : Pour extensions futures

**Exemple** :
```python
# No tooltip (default)
cellDef.displayTooltip()

# Show coordinates
cellDef.displayTooltip('coords')

# Show ID
cellDef.displayTooltip('id')
```

### 14.4 Protection race conditions Qt
**Problème** : `RuntimeError: wrapped C/C++ object deleted` lors de clics rapides sur nextTurn.

**Solution** : Protection `try/except RuntimeError` dans les opérations sur vues Qt.

**Pattern recommandé** :
```python
try:
    self.move(self.xCoord, self.yCoord)
except RuntimeError:
    # Agent view has been deleted, ignore the error
    pass
```

### 14.5 Tests de voisinage
**Tests disponibles** :
- `test_neighborhood_hexagonal.py` : Tests voisinage hexagonal (ouvert/fermé)
- `test_neighborhood_square.py` : Tests voisinage carré (Moore/Neumann, ouvert/fermé)

**Validation** : Patterns de voisinage corrects pour géométries complexes.

### 14.6 Patterns géométriques hexagonaux
**Type** : "Pointy-top hex grid with even-r offset"

**Caractéristiques** :
- Voisinage : 6 voisins pour `boundaries='open'` (toroidal)
- Patterns : Correction des `valid_neighbors` pour géométrie correcte
- Tests : Validation complète des patterns de voisinage

## 15. Lancement des applications SGE (CRITIQUE pour chatbots)

### 15.1 Problèmes courants avec PowerShell
**ATTENTION** : PowerShell Windows ne supporte pas la syntaxe `&&` comme bash.

❌ **INCORRECT** :
```powershell
cd examples/A_to_Z_examples && python exStep1.py
# Erreur: "Le jeton « && » n'est pas un séparateur d'instruction valide"
```

✅ **CORRECT** :
```powershell
cd examples/A_to_Z_examples
python exStep1.py
```

### 15.2 Commandes de lancement recommandées
```powershell
# 1. Naviguer vers le répertoire des exemples
cd examples/A_to_Z_examples

# 2. Lancer l'exemple souhaité
python exStep1.py
python exStep3_2.py
python exStep8.py
```

### 15.3 Gestion des applications Qt
- **Applications SGE** : Applications Qt avec interface graphique
- **Lancement** : Toujours en mode **foreground** (pas background)
- **Fermeture** : L'utilisateur ferme manuellement la fenêtre
- **Environnement** : S'assurer que l'environnement virtuel est activé

### 15.4 Structure des exemples
- **exStep1.py** : Exemple minimal (fenêtre vide)
- **exStep3_2.py** : Grille + agents avec attributs + POV
- **exStep8.py** : Exemple le plus avancé
- **CarbonPolis.py** : Jeu complet dans `examples/games/`

### 15.5 Messages d'erreur courants
- **"No such file or directory"** : Vérifier le répertoire de travail
- **"Le jeton « && » n'est pas un séparateur"** : Utiliser syntaxe PowerShell
- **Application ne s'ouvre pas** : Lancer en foreground, pas background

### 15.6 Syntaxe PowerShell vs Bash (CRITIQUE)
**ATTENTION** : PowerShell Windows utilise une syntaxe différente de bash/Linux.

❌ **INCORRECT - Syntaxe Bash** :
```bash
cd examples/A_to_Z_examples && python exStep1.py
git add . && git commit -m "message" && git push
```

✅ **CORRECT - Syntaxe PowerShell** :
```powershell
cd examples/A_to_Z_examples
python exStep1.py

git add .
git commit -m "message"
git push
```

**Règle** : En PowerShell, séparer les commandes par des retours à la ligne, pas par `&&`.

## 16. Méthodes de déplacement d'agents (CRITIQUE)

### 16.1 Distinction moveTo() vs moveAgent()
**RÈGLE** : Distinguer clairement les deux méthodes de déplacement.

**moveTo(destinationCell)** :
- **Usage** : Placement initial ET déplacement général
- **Avantage** : Fonctionne même si l'agent n'est pas encore placé
- **Exemple** : `agent.moveTo(targetCell)`

**moveAgent(method, target, numberOfMovement, condition)** :
- **Usage** : Mouvement avec patterns prédéfinis
- **PRÉREQUIS** : Agent doit être déjà placé sur une cellule
- **Exemple** : `agent.moveAgent(method="random")`

### 16.2 Paramètre numberOfMovement
**Fonctionnalité** : Répète le mouvement plusieurs fois en une action.
```python
agent.moveAgent(method="random", numberOfMovement=3)  # 3 mouvements
```

### 16.3 Paramètre condition
**Fonctionnalité** : Mouvement conditionnel basé sur les propriétés de la cellule.
```python
agent.moveAgent(condition=lambda cell: cell.isNotValue("terrain", "metal"))
```

### 16.4 Erreurs courantes
- **Oublier show()** après moveTo() → Agent invisible
- **Utiliser moveAgent()** sur agent non placé → Erreur
- **Confondre les deux méthodes** → Comportement inattendu

## 17. Méthodes utilitaires SGExtensions.py

### 17.1 Centralisation des utilitaires
**RÈGLE** : Les méthodes utilitaires communes sont dans `SGExtensions.py`.

**Méthodes disponibles** :
- `execute_callable_with_entity(callable_func, entity=None)` : Gestion dynamique des arguments
- `normalize_species_name(species)` : Normalisation des noms d'espèces

### 17.2 Usage recommandé
```python
from mainClasses.SGExtensions import execute_callable_with_entity

# Pour les lambdas avec 0 ou 1 argument
execute_callable_with_entity(lambda: doSomething(), agent)
execute_callable_with_entity(lambda a: doSomething(a), agent)
```

## 18. Gestion des chantiers avec FUTURE_PLAN.md (CRITIQUE pour chatbots)

### 18.1 Rôle du FUTURE_PLAN.md
**FUTURE_PLAN.md** est le **système centralisé de référencement des chantiers** pour SGE. Ce fichier doit être **TOUJOURS** consulté et mis à jour par les chatbots.

### 18.2 Obligations pour les chatbots

**AVANT tout travail de développement** :
- ✅ **Consulter FUTURE_PLAN.md** pour comprendre les priorités
- ✅ **Identifier les chantiers liés** au travail demandé
- ✅ **Proposer des améliorations** basées sur les items du plan

**PENDANT le développement** :
- ✅ **Référencer les items** du FUTURE_PLAN.md dans les discussions
- ✅ **Identifier les dépendances** entre chantiers
- ✅ **Suggérer des optimisations** basées sur le plan

**APRÈS le développement** :
- ✅ **Mettre à jour FUTURE_PLAN.md** avec les avancées
- ✅ **Marquer les items terminés** dans "Completed Items"
- ✅ **Ajouter les nouvelles idées** qui émergent

### 18.3 Structure du FUTURE_PLAN.md

**Sections principales** :
- **Current Development Items** : Chantiers organisés par catégories
- **Completed Items** : Chantiers terminés (à mettre à jour)
- **Notes** : Informations contextuelles

**Catégories de chantiers** :
- **Core Architecture & Framework** : Refactoring, conventions
- **User Interface & Display** : Améliorations UI/UX
- **POV System & Visual Elements** : Système de points de vue
- **Graphs & Analytics Interface** : Interface des graphiques
- **Simulation Management & Data** : Gestion des simulations
- **Multiplayer & Configuration** : Fonctionnalités multijoueurs
- **New Entities & Features** : Nouvelles entités
- **Documentation & Tools** : Outils de documentation

### 18.4 Workflow recommandé pour chatbots

**1. Analyse initiale** :
```markdown
# Consulter FUTURE_PLAN.md
# Identifier les chantiers liés au travail demandé
# Proposer une approche basée sur les priorités du plan
```

**2. Développement guidé** :
```markdown
# Référencer les items du plan dans les discussions
# Expliquer comment le travail s'inscrit dans la roadmap
# Suggérer des améliorations connexes
```

**3. Mise à jour post-développement** :
```markdown
# Déplacer les items terminés vers "Completed Items"
# Ajouter les nouvelles idées qui émergent
# Mettre à jour les descriptions si nécessaire
```

### 18.5 Exemples d'utilisation

**Exemple 1 - Développement guidé** :
```
User: "Je veux améliorer le système de zoom"
Chatbot: "D'après FUTURE_PLAN.md, le zoom est dans 'User Interface & Display'. 
         Je vois aussi 'Correct the zoom' dans les items. 
         Cela s'inscrit dans l'amélioration générale de l'interface utilisateur."
```

**Exemple 2 - Mise à jour post-développement** :
```
# Après avoir terminé un chantier
# Déplacer l'item de "Current Development Items" vers "Completed Items"
# Ajouter la date et les détails de l'implémentation
```

### 18.6 Règles critiques

**OBLIGATOIRE** :
- ✅ Toujours consulter FUTURE_PLAN.md avant de commencer
- ✅ Référencer les items du plan dans les discussions
- ✅ Mettre à jour le plan après chaque développement
- ✅ Respecter l'organisation par catégories

**INTERDIT** :
- ❌ Ignorer le FUTURE_PLAN.md
- ❌ Travailler sans référence au plan
- ❌ Oublier de mettre à jour les avancées
- ❌ Créer des chantiers sans les référencer

### 18.7 Message de démarrage pour chaque chat

"**CRITIQUE** : Consulter FUTURE_PLAN.md avant tout travail sur SGE.
**OBLIGATIONS** :
1. Analyser les chantiers liés au travail demandé
2. Guider le développement selon les priorités du plan
3. Mettre à jour FUTURE_PLAN.md après chaque avancée
4. Référencer les items du plan dans les discussions

FUTURE_PLAN.md est le système centralisé de référencement des chantiers SGE."