# SGE - Spécification de l'entité Tile

## Vue d'ensemble

Ce document définit les exigences fonctionnelles et les fonctionnalités attendues pour la nouvelle entité **Tile** dans SGE. L'entité Tile fournira un nouveau type d'élément de jeu qui diffère à la fois des Cells (structure de grille) et des Agents (entités mobiles).

## Contexte et motivation

Actuellement, SGE a deux types d'entités principaux :
- **SGCell** : Cellules de grille fixes qui forment la structure du plateau de jeu
- **SGAgent** : Entités mobiles qui se déplacent entre les cellules

Une entité **Tile** comblerait un manque en fournissant trois aspects principaux :

1. **Aspect d'empilement (Stack)** :
   - **Objets empilables** : Plusieurs tiles peuvent être placées sur la même cellule, formant un stack
   - **Éléments en couches** : Les tiles peuvent être superposées avec un système de layer/z-index
   - **TopTile** : La tile du dessus du stack (layer le plus élevé)

2. **Aspect de mouvement** :
   - **Statiques** : Ne bougent jamais (ex: caractéristiques de terrain fixes, obstacles permanents)
   - **Semi-statiques** : Peuvent être déplacées par le modeler via `tile.moveTo(cell)` ou par un joueur via une gameAction Move (`newMoveAction(tileDef, ...)`) mais n'ont pas de mouvement autonome comme les agents (ex: ressources déplaçables, bâtiments relocalisables)

3. **Aspect de double faces** :
   - **Tiles à deux faces** : Possibilité de retourner une tile pour changer la face visible (comme une carte à jouer)
   - Chaque tile a une face avant et une face arrière avec des apparences différentes

## Cas d'usage

### Scénarios d'exemple organisés par aspect

#### Aspect d'empilement (Stack)
1. **Superposition de caractéristiques** : Empiler plusieurs tiles sur une même cellule formant un stack (ex: "forêt" + "ressource or" + "bâtiment")
2. **Layers de terrain** : Créer des couches de terrain (ex: "sol" + "herbe" + "rocher")
3. **Décorations multiples** : Ajouter plusieurs éléments décoratifs sur une cellule
4. **Pile de tiles face cachée** : Empiler plusieurs tiles toutes face cachée sur une cellule formant un stack, permettant aux joueurs de piocher la tile du dessus (topTile) pour la déplacer sur une autre cellule (via gameAction Move)
5. **Déplacement de stack** : Selon la configuration, un joueur peut déplacer tout un stack d'un coup

#### Aspect de mouvement
1. **Tiles statiques** :
   - **Caractéristiques de terrain fixes** : Tiles "forêt", "montagne", "eau" qui ne bougent jamais
   - **Obstacles permanents** : Tiles "mur", "barrière" qui bloquent le mouvement de façon permanente
   - **Éléments fixes** : Tiles qui font partie du décor et restent en place
   
2. **Tiles semi-statiques** :
   - **Ressources déplaçables** : Tiles "or", "bois", "nourriture" que le modeler peut déplacer entre cellules
   - **Bâtiments relocalisables** : Tiles "maison", "usine" qui peuvent être déplacées par le modeler
   - **Éléments configurables** : Tiles dont la position peut être modifiée pendant la simulation
   - **Déplacement par joueur** : Les tiles peuvent être déplacées par un joueur via une gameAction Move (`newMoveAction(tileDef, ...)`)

#### Aspect de double faces
1. **Cartes à jouer** : Tiles avec recto/verso (ex: carte de jeu avec face cachée/révélée)
2. **États de terrain** : Tiles avec deux états (ex: "terre cultivée" / "terre en jachère")
3. **Ressources avec états** : Tiles avec deux phases (ex: "ressource disponible" / "ressource épuisée")
4. **Bâtiments en construction** : Tiles avec deux phases (ex: "en construction" / "terminé")
5. **Tiles cachées/révélées** : Tiles avec face cachée qui peuvent être révélées (ex: tuiles de découverte)
6. **Jeu de Memory** : Tiles face cachée sur certaines cellules, les joueurs peuvent retourner une tile (via gameAction Flip) pour voir l'autre face et découvrir de quel item il s'agit (comme dans le jeu Memory)

## Exigences fonctionnelles

### 1. Exigences d'architecture

#### 1.1 Architecture Model-View (OBLIGATOIRE)
- **SGTile** (Model) : Hérite de `SGEntity`
  - `SGEntity` hérite lui-même de `AttributeAndValueFunctionalities`
  - Donc `SGTile` hérite de `SGEntity` ET de `AttributeAndValueFunctionalities` (héritage en chaîne)
  - Contient les données, attributs et logique de jeu de la tile
  - Gère l'état et les propriétés de la tile
  
- **SGTileView** (View) : Hérite de `SGEntityView`
  - Gère le rendu UI et l'affichage visuel
  - Gère les événements souris et les interactions utilisateur
  
- **SGTileType** (Factory) : Hérite de `SGEntityType`
  - Classe factory pour créer des instances de Tile
  - Gère les définitions de types de tiles et les valeurs par défaut

#### 1.2 Identification de type
- Ajouter `isTileType = True` à `SGTileType`
- Ajouter `isTile = True` aux instances de `SGTile`
- Ajouter `isCell = False` et `isAgent = False` à `SGTile`

### 2. Positionnement et placement

#### 2.1 Association avec une cellule
- **OBLIGATOIRE** : Les tiles doivent être associées à une cellule
- Les tiles sont placées **sur** les cellules (ne les remplacent pas)
- Une cellule peut contenir **plusieurs tiles** (capacité d'empilement)
- Les tiles ont un **z-order/layer** pour la priorité de rendu
- **Recouvrement complet** : Une tile peut recouvrir l'ensemble de la cellule, rendant la cellule invisible (la tile prend toute la taille de la cellule)

#### 2.2 Options de position
- **Position fixe** : Tile positionnée à des coordonnées spécifiques dans une cellule
  - Options : `"center"`, `"topLeft"`, `"topRight"`, `"bottomLeft"`, `"bottomRight"`, `"full"` (recouvre complètement la cellule)
  - **Contrainte** : La position ne peut pas être `"random"` (contrairement aux agents)
  - **Contrainte** : Dans une cellule, il ne peut y avoir qu'un seul type de tuile sur une même position (ex: une seule tile de type "Forest" en position "center", mais on peut avoir une tile "Forest" en "center" et une tile "Mountain" en "topLeft")
  - **Note** : Cette contrainte s'applique aux différents types de tiles. Cependant, plusieurs tiles d'un même TileType peuvent être empilées sur une même position (voir section 3.3 sur les stacks)
  - Similaire au positionnement des agents mais les tiles ne bougent pas
- **Recouvrement complet** : Tile qui recouvre entièrement la cellule
  - Option : `"full"` ou `"cover"` - La tile prend toute la taille de la cellule et la recouvre complètement
  - Dans ce cas, la cellule n'est plus visible (cachée par la tile)
  - Utile pour remplacer visuellement une cellule tout en gardant la structure de grille

#### 2.3 Système de coordonnées
- Les tiles utilisent un **positionnement relatif** dans leur cellule
- Position calculée basée sur la position et la taille actuelles de la cellule
- Doit respecter la fonctionnalité de zoom (comme les agents)

### 3. Fonctionnalités principales

#### 3.1 Création de tiles (API Modeler)
```python
# Créer une définition de type de tile
tileDef = model.newTileType(
    name="Forest",
    shape="rectTile",  # ou "circleTile", "imageTile"
    defaultColor=Qt.green,
    defaultSize=20
)

# Créer une instance de tile sur une cellule spécifique
tile = tileDef.newTileOnCell(cell, position="center")
# OU
tile = tileDef.newTileAtCoords(x=5, y=3, position="center")
# OU - Tile qui recouvre complètement la cellule
tile = tileDef.newTileOnCell(cell, position="full")  # La cellule devient invisible
# OU - Créer une tile sur une autre tile (empilement)
tile2 = tileDef.newTileOnTile(tile)  # Crée une nouvelle tile empilée sur la tile existante
```

#### 3.2 Gestion des tiles
- **Placement** : `tile.placeOn(cell)` ou `tile.moveTo(cell)`
- **Suppression** : `tile.delete()` ou `tileDef.deleteTile(tile)`
- **Requête** : `cell.getTiles()`, `cell.nbTiles()`, `cell.hasTile(tileType)`
- **Déplacement de stack** : Selon la configuration définie par le modeler, un joueur peut déplacer tout un stack d'un coup (via gameAction Move)

#### 3.3 Support de l'empilement et notion de Stack
- Plusieurs tiles peuvent exister sur une même position dans une même cellule, formant un **stack** (pile)
- Les tiles ont une propriété **layer/z-index** pour l'ordre de rendu
- Méthodes : `tile.setLayer(layer)`, `tile.getLayer()`
- Layer par défaut : 1 (sous les agents, au-dessus du fond de cellule, cohérent avec le système de coordonnées 1-based)
- **Stack** : Ensemble de tiles empilées sur une même position dans une cellule
  - La tile du dessus (layer le plus élevé) est appelée **topTile**
  - La tile du dessous (layer le plus bas) est appelée **bottomTile**
  - Un stack peut être déplacé en entier d'un coup selon la configuration du modeler
- **Contrainte importante** : On ne peut empiler que des tiles d'un même TileType (toutes les tiles d'un stack doivent avoir le même `tileDef`)
- **Principe fondamental** : Dans un stack, les tiles sont toujours ordonnées de 1 à N où :
  - Layer 1 = tile tout en bas (première posée)
  - Layer N = tile tout en haut (dernière posée)
  - L'ordre des tiles dans le stack = leur layer
  - Les layers sont toujours continus de 1 à N (pas de gaps)
  - Le layer représente la position dans l'empilement (1 = bas, N = haut)

#### 3.4 Système de deux faces (FONCTIONNALITÉ PRINCIPALE)
- **Chaque tile a deux faces** : face avant (visible par défaut) et face arrière
- **Retournement** : Possibilité de retourner une tile pour changer la face visible
- **Cas d'usage** :
  - Cartes à jouer (recto/verso)
  - Tuiles de terrain avec deux états (ex: "terre cultivée" / "terre en jachère")
  - Ressources avec deux états (ex: "ressource disponible" / "ressource épuisée")
  - Tiles de construction avec deux phases (ex: "en construction" / "terminé")
  - Tiles cachées/révélées (ex: "face cachée" / "face révélée")

**Attributs et méthodes** :
- `face` : Attribut indiquant la face actuellement visible (`"front"` ou `"back"`)
- `frontImage` / `frontColor` : Apparence de la face avant
- `backImage` / `backColor` : Apparence de la face arrière
- `tile.flip()` : Retourner la tile (change la face visible)
- `tile.setFace("front")` / `tile.setFace("back")` : Définir explicitement la face visible
- `tile.getFace()` : Obtenir la face actuellement visible
- `tile.isFaceFront()` / `tile.isFaceBack()` : Vérifier quelle face est visible

**Configuration lors de la création** :
```python
# Créer un type de tile avec deux faces
tileDef = model.newTileType(
    name="Card",
    shape="rectTile",
    frontColor=Qt.blue,      # Face avant
    backColor=Qt.red,         # Face arrière
    frontImage="card_front.png",  # Image face avant (optionnel)
    backImage="card_back.png",     # Image face arrière (optionnel)
    positionOnCell="center"    # Position fixe sur la cellule pour toutes les tiles de ce type (obligatoire, ne peut pas être surchargée lors de la création)

)

# Créer une tile avec face spécifique
tile = tileDef.newTileOnCell(cell, face="front")  # Face avant par défaut
tile = tileDef.newTileOnCell(cell, face="back")   # Face arrière par défaut

# Note : Tous les types de tiles ont deux faces (face avant et face arrière)
```

**Rendu** :
- La vue affiche uniquement la face actuellement visible
- **Animation de retournement** : C'est configurable par le modeler (animation ou changement instantané)
- Les deux faces peuvent avoir des styles différents (couleur, image, forme)
- **Note importante** : Tous les types de tiles ont deux faces (face avant et face arrière)

### 4. Visuel et affichage

#### 4.1 Rendu
- Les tiles se rendent **au-dessus des cellules** mais **sous les agents** (par défaut)
- Support pour les formes géométriques : `"rectTile"`, `"circleTile"`, `"ellipseTile"` (rendues avec une couleur de remplissage)
- Support pour les images : `"imageTile"` - La tile est rendue uniquement avec une image (QPixmap), sans forme géométrique de base visible. L'image remplace complètement le rendu géométrique. Utile pour des cartes, des tuiles décoratives avec des images complexes, etc. L'image peut être différente pour chaque face (`frontImage`/`backImage`).
- Support pour les formes personnalisées (extension future)
- **Rendu des deux faces** : Seule la face actuellement visible est rendue (face avant ou face arrière)
- **Recouvrement complet** : Lorsqu'une tile a `position="full"`, elle recouvre entièrement la cellule et la rend invisible (la tile prend toute la taille de la cellule)
- **Rendu des stacks** : Le rendu visuel d'un stack (pile de tiles) est configurable par le modeler avec plusieurs modes :
  - `"topOnly"` : On ne voit que la topTile (la tile du dessus)
  - `"offset"` : On voit les bords des tiles en dessous qui sont toutes légèrement décalées les unes des autres
  - `"stacked"` : On voit un empilement de tiles et le nombre de tiles de la pile est affiché sur le dessus de la pile
- **Intégration avec le rendu** : À vérifier comment c'est fait pour les Agents, et utiliser la même façon de faire que pour les Agents

#### 4.2 Style
-  utiliser le système POV
- **Support du système POV** : Les tiles supportent le système POV (Point of View) comme les cellules et les agents
- Support pour :
  - Couleur de forme (`defaultShapeColor`)
  - Couleur et largeur de bordure
  - Taille (avec support du zoom)
  - Images

#### 4.3 Support du zoom
- Les tiles doivent s'adapter au zoom de la grille (comme les agents)
- Maintenir la position relative dans la cellule pendant le zoom
- Utiliser le pattern `saveSize` (comme les agents et les cellules)

### 5. Interaction et comportement

#### 5.1 Événements souris
- **Détection de clic** : Les tiles peuvent être cliquées
- **Double-clic pour retourner** : Possibilité de retourner une tile par double-clic (optionnel, configurable)
- **Menu contextuel** : Support pour les actions contextuelles (incluant option "Retourner la tile")
- **Tooltip** : Afficher les informations de la tile au survol (peut afficher la face actuelle)
- **Sélection** : Les tiles peuvent être sélectionnées/mises en surbrillance

#### 5.2 Interaction avec les agents
- **Détection de collision** : Les agents peuvent détecter les tiles sur les cellules
- **Méthodes d'interaction** : 
  - `agent.isOnTile(tileType)` - Vérifier si l'agent est sur une tile
  - `agent.getTilesHere()` - Obtenir les tiles sur la cellule actuelle
  - `tile.isOccupied()` - Vérifier si la tile est occupée par des agents

#### 5.2.1 Interaction avec les cellules
- **Méthodes sur les cellules** pour interagir avec les tiles :
  - `cell.getTilesHere()` - Obtenir toutes les tiles sur cette cellule
  - `cell.getTiles(tileType=None)` - Obtenir toutes les tiles ou filtrer par type
  - `cell.nbTiles(tileType=None)` - Compter les tiles sur la cellule (toutes ou par type)
  - `cell.hasTile(tileType)` - Vérifier si la cellule contient une tile d'un type donné
  - `cell.getRandomTile(tileType)` - Obtenir une tile au hasard d'un type donné sur la cellule
  - `cell.getStack(tileType)` - Obtenir un objet Stack (entité virtuelle) pour un type donné (la position est déterminée par le tileType)

#### 5.3 Game Actions
- **Comme pour les Cells et les Agents, les Tiles peuvent avoir des gameActions associées**
- Les tiles peuvent être des cibles pour les game actions :
  - `newCreateAction(tileDef, ...)` - Créer des tiles
  - `newDeleteAction(tileDef, ...)` - Supprimer des tiles
  - `newModifyAction(tileDef, ...)` - Modifier les attributs des tiles
  - `newActivateAction(tileDef, ...)` - Activer des tiles
  - `newMoveAction(tileDef, ...)` - Déplacer des tiles
  - `newFlipAction(tileDef, ...)` - **Retourner une tile** (changer la face visible) - GameAction principale pour les tiles
- Les gameActions permettent aux joueurs d'interagir avec les tiles pendant le jeu
- **Important** : Pour cibler les tiles, le modeler doit créer explicitement une game action avec `tileDef` comme `targetType`. Les tiles sur une cellule ne sont pas des cibles valides pour une game action créée avec un `cellDef` comme `targetType`.

### 6. Attributs et propriétés

#### 6.1 Attributs standards
- **Héritage** : `SGTile` hérite de `SGEntity`, qui hérite lui-même de `AttributeAndValueFunctionalities`
- **Attributs hérités de `SGEntity`** :
  - `id`, `privateID`, `type`, `model`
  - `size`, `shape`, `borderColor`, `isDisplay`
  - `owner`, `view`
- **Fonctionnalités héritées de `AttributeAndValueFunctionalities`** :
  - `attributes` (attributs personnalisés via `setValue`, `getValue`, `setAttributes`, `getAttributes`)
  - `history`, `watchers`
  - Toutes les méthodes de gestion d'attributs (héritage complet)

#### 6.2 Attributs spécifiques aux tiles
- `cell` : Référence à la cellule sur laquelle la tile est placée
- `layer` : Z-order pour le rendu (par défaut : 1, cohérent avec le système de coordonnées 1-based)
- `face` : Face actuellement visible (`"front"` ou `"back"`, par défaut : `"front"`)
- `frontImage` / `frontColor` : Apparence de la face avant
- `backImage` / `backColor` : Apparence de la face arrière
- `blocksStacking` : Si la tile bloque la possibilité d'empiler d'autres tiles par-dessus (par défaut : False)
- `blocksAgentPlacement` : Si la tile bloque la possibilité de placer un agent sur cette tile (par défaut : False)

### 7. Méthodes API Modeler

#### 7.1 Méthodes TileType (SGTileType)
```python
# Création
tileDef = model.newTileType(name, shape, defaultColor, defaultSize)

# Méthodes factory
tile = tileDef.newTileOnCell(cell, attributes={}) # La position est fixée par le TileType (positionOnCell), ne peut pas être surchargée
tile = tileDef.newTileAtCoords(x, y, attributes={}) # La position est fixée par le TileType (positionOnCell)

# Méthodes de requête
tiles = tileDef.getAllTiles()
tile = tileDef.getTileById(id)
tiles = tileDef.getTilesOnCell(cell)
stacks = tileDef.getAllStacks()  # Obtenir tous les stacks (groupes de tiles empilées sur une même position)


# Model actions
action = tileDef.newModelAction(actions=[lambda tile: ...])
```

#### 7.2 Méthodes Tile (SGTile)
```python
# Position
tile.placeOn(cell)
tile.moveTo(cell)  # Déplacer vers une autre cellule
cell = tile.getCell()
coords = tile.getCoords()  # Retourne les coordonnées de la cellule

# Gestion des layers
tile.setLayer(layer)
layer = tile.getLayer()

# Gestion des faces (deux faces)
tile.flip()                    # Retourner la tile
tile.setFace("front")          # Définir la face avant
tile.setFace("back")           # Définir la face arrière
face = tile.getFace()          # Obtenir la face actuelle ("front" ou "back")
is_front = tile.isFaceFront()  # Vérifier si face avant
is_back = tile.isFaceBack()    # Vérifier si face arrière

# Requête
blocks_stacking = tile.blocksStacking()        # Vérifier si empilement bloqué
blocks_agents = tile.blocksAgentPlacement()    # Vérifier si placement d'agents bloqué
agents_here = tile.getAgentsHere()

# Attributs (hérités de SGEntity)
tile.setValue("resource", "gold")
value = tile.getValue("resource")
```

#### 7.3 Méthodes Cell (Étendues)
```python
# Nouvelles méthodes sur SGCell pour interagir avec les tiles
tiles = cell.getTilesHere()           # Obtenir toutes les tiles sur cette cellule
tiles = cell.getTiles(tileType=None)  # Obtenir toutes les tiles ou filtrer par type
nb = cell.nbTiles(tileType=None)      # Compter les tiles (toutes ou par type)
has = cell.hasTile(tileType)          # Vérifier si la cellule contient une tile d'un type donné
tile = cell.getRandomTile(tileType)   # Obtenir une tile au hasard d'un type donné
stack = cell.getStack(tileType)       # Obtenir un objet Stack (entité virtuelle) pour un type donné (position déterminée par tileType.positionOnCell)
```

#### 7.4 Méthodes Stack (SGStack) - Entité virtuelle
La classe `SGStack` représente un empilement de tiles du même type à une position donnée. C'est une entité virtuelle qui permet d'interroger et de manipuler un stack de manière cohérente.

**Création** :
```python
# Obtenir un Stack pour un type de tile donné
stack = cell.getStack(tileType)  # Retourne un objet SGStack
```

**Attributs** :
- `stack.cell` : Référence à la cellule (SGCell)
- `stack.tileType` : Type de tuile (SGTileType)
- `stack.position` : Position sur la cellule (dérivée de `tileType.positionOnCell`)
- `stack.tiles` : Propriété calculée retournant la liste des tiles triée par layer (recalculée à chaque accès, sans cache)

**Méthodes GET/NB** :
```python
size = stack.size()                    # Nombre de tiles dans le stack
max_layer = stack.maxLayer()           # Layer maximum dans le stack
min_layer = stack.minLayer()           # Layer minimum dans le stack
top_tile = stack.topTile()             # Tile avec le layer le plus élevé (None si vide)
bottom_tile = stack.bottomTile()       # Tile avec le layer le plus bas (None si vide)
tile = stack.tileAtLayer(layer)        # Tile à un layer spécifique (None si inexistant)
tiles = stack.getTilesWithValue(attribute, value)  # Tiles avec un attribut/valeur spécifique
tiles = stack.getTilesWithFace(face)   # Tiles avec une face spécifique ("front" ou "back")
```

**Méthodes IS/HAS** :
```python
is_empty = stack.isEmpty()             # Vérifie si le stack est vide
contains = stack.contains(tile)        # Vérifie si une tile spécifique est dans le stack
```

**Méthodes DO** :
```python
stack.shuffle()                         # Mélange les tiles et réassigne les layers de 1 à N
```

**Notes importantes** :
- Le Stack est une vue virtuelle : les données sont recalculées à chaque accès (pas de cache)
- Les layers sont toujours continus de 1 à N (pas de gaps)
- `shuffle()` mélange l'ordre des tiles puis réassigne les layers de 1 à N dans le nouvel ordre
- Le Stack ne peut pas ajouter ou retirer des tiles par lui-même (c'est fait par des éléments extérieurs)
- `getStack()` remplace les anciennes méthodes `getStackSize()`, `getMaxLayer()`, `getTopTile()` qui sont supprimées

### 8. Intégration dans l'architecture SGE existante

Cette section décrit comment les tiles s'intègrent dans l'architecture SGE existante et quels composants doivent être modifiés ou étendus.

#### 8.1 Intégration avec la grille (SGGrid)
- **Gestion des tiles** : La grille doit gérer les tiles comme elle gère les agents
  - La grille maintient une liste de toutes les tiles (similaire à `grid.agents`)
  - La grille doit pouvoir itérer sur toutes les tiles pour le rendu
- **Rendu** : La grille doit gérer l'ordre de rendu des tiles
  - Les tiles doivent être rendues après les cellules mais avant les agents
  - L'ordre de rendu doit respecter le système de layers des tiles
- **Zoom** : La grille doit gérer le zoom des tiles (comme pour les agents)

#### 8.2 Intégration avec la factory (SGEntityFactory)
- **Extension de la factory** : `SGEntityFactory` doit être étendue pour supporter la création de tiles
  - Ajout de méthodes pour créer des instances de `SGTile` et `SGTileView`
  - Les méthodes factory suivent le même pattern que pour les agents (`newAgentAtCoords`, etc.)
- **Création Model-View** : La factory doit créer à la fois le Model (`SGTile`) et la View (`SGTileView`) comme pour les agents

#### 8.3 Intégration avec les vues (SGTileView, SGCellView, SGGrid)
- **Rendu des tiles** : `SGTileView` doit s'intégrer avec le système de rendu existant
  - Les tiles se rendent dans `SGGrid.paintEvent()` ou dans une méthode dédiée
  - `SGCellView` peut être étendue pour gérer le rendu des tiles associées à la cellule
- **Ordre de couches de rendu** : Ordre de rendu approprié
  - Fond de cellule (SGCellView) < Tiles (SGTileView) < Agents (SGAgentView)
  - Les tiles avec layer plus élevé se rendent au-dessus des tiles avec layer plus bas
- **Événements** : Les tiles doivent gérer les événements souris (clic, double-clic, etc.) comme les agents

### 9. Considérations techniques

#### 9.1 Performance
- Rendu efficace de plusieurs tiles par cellule
- Détection de collision optimisée
- Surcharge mémoire minimale

#### 9.2 Compatibilité
- Doit fonctionner avec la fonctionnalité de zoom existante
- Doit respecter les limites de la grille
- Doit s'intégrer avec le système POV existant

#### 9.3 Extensibilité
- La conception doit permettre des extensions futures :
  - Tiles animées
  - Effets de tiles
  - Interactions entre tiles
  - Comportements de tiles personnalisés

## Phases d'implémentation

### Phase 1 : Structure principale
- [x] Créer la classe `SGTile` (Model)
- [x] Créer la classe `SGTileView` (View)
- [x] Créer la classe `SGTileType` (Factory)
- [x] Placement de base sur les cellules
- [x] Rendu de base

### Phase 2 : Positionnement et affichage
- [x] Options de position (center, corners, full) - Note: pas de "random"
- [x] Support du zoom
- [x] Système de layer/z-order
- [x] Style visuel
- [x] **Système de deux faces** (FONCTIONNALITÉ PRINCIPALE)
  - [x] Attributs front/back (couleur, image)
  - [x] Méthodes flip(), setFace(), getFace()
  - [x] Rendu de la face visible
  - [x] Support dans la vue (SGTileView)

### Phase 3 : Interaction
- [x] Événements souris (mousePressEvent, mouseReleaseEvent implémentés)
- [x] Menus contextuels (hérités de SGEntityView)
- [ ] Tooltips (non implémenté spécifiquement pour les tiles)
- [~] Interaction agent-tile (partiellement fait : méthodes de base existent `getAgentsHere()`, `isOccupied()`, `doesBlockAgentPlacement()`, mais manque soit possibilité de poser agents sur tuiles, soit getters croisés entre entités - à décider)

### Phase 4 : Fonctionnalités avancées
- [~] Empilement de plusieurs tiles (méthodes de base implémentées `getStack()`, `getTopTile()`, `getStackSize()`, mais pas testé, pas d'exemple, affichage visuel des stacks dans l'interface non terminé)
- [ ] **Classe SGStack (entité virtuelle)** - À IMPLÉMENTER
  - [ ] Créer le fichier `mainClasses/SGStack.py`
  - [ ] Implémenter la classe `SGStack` avec attributs et propriété `tiles` (sans cache)
  - [ ] Implémenter méthodes GET/NB : `size()`, `maxLayer()`, `minLayer()`, `topTile()`, `bottomTile()`, `tileAtLayer()`, `getTilesWithValue()`, `getTilesWithFace()`
  - [ ] Implémenter méthodes IS/HAS : `isEmpty()`, `contains()`
  - [ ] Implémenter méthode DO : `shuffle()` (mélange et réassigne layers de 1 à N)
  - [ ] Modifier `SGCell.getStack()` pour retourner un objet `SGStack` au lieu de `list[SGTile]`
  - [ ] Supprimer les méthodes redondantes dans `SGCell` : `getStackSize()`, `getMaxLayer()`, `getTopTile()`
  - [ ] Mettre à jour la documentation et les exemples
- [x] Intégration avec les game actions (Flip, Move, Create, Delete, Modify, Activate tous implémentés)
- [ ] Model actions sur les tiles
- [ ] Intégration avec le système POV

### Phase 5 : Documentation et exemples
- [ ] Documentation API (docstrings à compléter/vérifier)
- [~] Exemples d'utilisation (partiellement fait : `ex_tiles_positioning.py`, `ex_tiles_with_images.py`, `Memory.py` existent, mais manque exemple pour empilement)
- [ ] Intégration au catalogue de méthodes

## Exemples de jeux de test pour le développement

Au cours des phases de développement, des exemples de jeux seront créés pour tester les fonctionnalités des tiles. Ces exemples serviront de validation progressive des fonctionnalités implémentées.

### Exemple 1 : Jeu de Memory ✅ IMPLÉMENTÉ

**Objectif** : Tester le système de double faces et le retournement de tiles

**Description** :
- Plateau de jeu avec plusieurs cellules
- Tiles face cachée placées sur certaines cellules
- Les joueurs peuvent retourner une tile (via gameAction Flip) pour voir l'autre face et découvrir de quel item il s'agit
- Mécanique de Memory classique : trouver les paires en retournant les tiles

**Fonctionnalités testées** :
- Création de tiles avec deux faces
- Placement de tiles face cachée sur des cellules
- GameAction Flip pour retourner les tiles
- Rendu des deux faces

**Fichier** : `Examples/games/Memory.py`
- Interaction joueur avec les tiles

### Exemple 2 : Jeu de pile de tiles avec activation

**Objectif** : Tester l'empilement, le déplacement de stack, le retournement et l'activation de tiles

**Description** :
- Plateau de jeu 4x1 (4 cellules en ligne : colonnes 1 à 4, ligne 1)
- **Cellule (1,1)** : Pile de tiles toutes face cachée (stack)
- **Cellules (2,1), (3,1), (4,1)** : Cellules vides où le joueur peut placer des tiles
- **Dashboard** : Affiche un indicateur (simVariable) qui sera modifié

**Mécanique de jeu** :
1. Le joueur peut prendre la **topTile** (tile du dessus de la pile) de la cellule (1,1)
2. Le joueur peut déplacer cette tile vers l'une des cellules (2,1), (3,1) ou (4,1) (via gameAction Move)
3. Une fois la tile placée sur une de ces cellules, le joueur peut la retourner (via gameAction Flip) pour voir sa face
4. Une fois retournée, le joueur peut activer la tile (via gameAction Activate)
5. L'activation de la tile déclenche la modification d'un indicateur affiché dans un dashboard

**Fonctionnalités testées** :
- Création d'une pile de tiles face cachée
- Récupération de la topTile d'un stack
- Déplacement de tile (gameAction Move)
- Retournement de tile (gameAction Flip)
- Activation de tile (gameAction Activate)
- Modification d'un indicateur dans un dashboard via l'activation d'une tile
- Rendu des stacks (mode "topOnly" probablement)
- Interaction complète joueur-tile-dashboard

**Structure attendue** :
```python
# Exemple de structure (à affiner lors de l'implémentation)
model = SGModel()
cellDef = model.newCellsOnGrid(columns=4, rows=1, format="square", size=50)

# Créer un type de tile avec deux faces
tileDef = model.newTileType(
    name="Card",
    shape="rectTile",
    frontColor=Qt.blue,
    backColor=Qt.red
)

# Créer une pile de tiles face cachée sur (1,1)
cell_1_1 = cellDef.getCell(x=1, y=1)
for i in range(5):  # 5 tiles dans la pile
    tile = tileDef.newTileOnCell(cell_1_1, face="back")  # Toutes face cachée

# Créer un dashboard avec un indicateur
simVar = model.newSimVariable("Score", 0)
dashboard = model.newDashBoard("Scores")
dashboard.addIndicatorOnSimVariable(simVar)

# Créer les game actions
flipAction = model.newFlipAction(tileDef, ...)
moveAction = model.newMoveAction(tileDef, ...)
activateAction = model.newActivateAction(tileDef, ...)  # Modifie simVar
```

## Questions ouvertes - Réponses

1. **Nommage** : Devrait-on utiliser "Tile" ou un autre nom (ex: "Object", "Element", "Feature") ?
   → **RÉSOLU** : Utiliser "Tile"

2. **Mouvement** : Les tiles devraient-elles être déplaçables par les modelers (comme `tile.moveTo(cell)`) ou complètement statiques ?
   → **RÉSOLU** : Support des deux (statiques par défaut, optionnellement déplaçables)

3. **Empilement** : Nombre maximum de tiles par cellule ? Ou illimité ?
   → **RÉSOLU** : C'est configurable par le modeler (voir la notion de stack précisée dans la section 3.3)

4. **Rendu** : Les tiles devraient-elles être rendues dans une couche séparée ou intégrées au rendu des cellules ?
   → **RÉSOLU** : Il faut vérifier comment c'est fait pour les Agents, et utiliser la même façon de faire que pour les Agents

5. **Système POV** : Les tiles devraient-elles supporter POV (Point of View) comme les cellules et les agents ?
   → **RÉSOLU** : Oui, les tiles supportent le système POV

6. **Game Actions - Sélection des tiles comme cibles** : 
   - **Contexte** : Dans SGE, les game actions sont créées avec un `targetType` (ex: `newModifyAction(cellDef, ...)` ou `newModifyAction(agentDef, ...)`). Quand un joueur clique sur une entité, la game action est exécutée si l'entité correspond au `targetType`.
   - **Question** : Quand un modeler crée une game action avec un `targetType` spécifique (ex: `newModifyAction(cellDef, ...)`), est-ce que les tiles sur cette cellule devraient aussi être des cibles valides pour cette action, ou seulement les cellules elles-mêmes ?
   - **Exemple concret** : 
     - Un modeler crée `modifyAction = model.newModifyAction(cellDef, ...)`
     - Un joueur clique sur une cellule → l'action s'exécute (comportement actuel)
     - **Question** : Si le joueur clique sur une tile qui est sur cette cellule, est-ce que l'action devrait aussi s'exécuter sur la tile, ou seulement sur la cellule ?
   → **RÉSOLU** : Les tiles sur une cellule ne doivent **PAS** être des cibles valides pour une game action créée avec un `targetType` spécifique (comme `cellDef`). Seules les cellules sont des cibles.
   - **Pour cibler les tiles** : Le modeler doit créer explicitement une game action avec `tileDef` comme `targetType` (ex: `newModifyAction(tileDef, ...)`)

7. **Animation de retournement** : Devrait-il y avoir une animation lors du retournement d'une tile, ou un changement instantané ?
   → **RÉSOLU** : C'est configurable par le modeler

8. **Faces différentes par type** : Tous les types de tiles doivent-ils avoir deux faces, ou seulement certains types (configurable par type) ?
   → **RÉSOLU** : Tous les types de tiles ont deux faces

## Comparaison avec les entités existantes

| Fonctionnalité | SGCell | SGAgent | SGTile (Proposé) |
|---------|--------|---------|-------------------|
| Position dans la grille | Fixe (x, y) | Se déplace entre cellules | Fixe sur une cellule |
| Multiple par cellule | Non (1 par position) | Oui | Oui (empilable) |
| Mouvement | Non | Oui (`moveTo`, `moveAgent`) | Non (ou optionnel) |
| Contient des agents | Oui | Non | Non |
| Couche | Arrière-plan | Premier plan | Milieu (configurable) |
| Objectif | Structure de grille | Entités mobiles | Éléments statiques/semi-statiques |

## Prochaines étapes

1. **Réviser et valider** cette spécification avec les parties prenantes
2. **Clarifier les questions ouvertes** avant l'implémentation
3. **Créer une conception détaillée** pour l'implémentation de la Phase 1
4. **Créer une branche de développement** : `dev_new_tile_entity`
5. **Commencer l'implémentation de la Phase 1**

---

**Statut du document** : Révisié et validé
**Dernière mise à jour** : 1/12/2025
**Auteur** : Nicolas
