# Spécification : Système de Zoom Magnifier pour les Grilles SGE

## Contexte

Actuellement, SGE propose un système de zoom qui agrandit ou réduit la taille physique de la grille et de ses éléments (cellules, agents, tiles) dans la fenêtre principale. Lors d'un zoom avant, la grille occupe plus d'espace dans la fenêtre.

Cette spécification décrit l'ajout d'un nouveau mode de zoom "magnifier" (loupe) qui permet de grossir le contenu de la grille sans modifier l'espace occupé par le gameSpace grid dans la fenêtre principale.

## Objectifs

1. **Conserver le comportement actuel** : Le zoom par défaut continue de fonctionner comme actuellement (zoom qui agrandit la grille).

2. **Ajouter un nouveau mode "magnifier"** : Un mode de zoom loupe où :
   - La grille garde une taille fixe dans la fenêtre
   - Le contenu (cellules, agents, tiles) est agrandi/réduit
   - Seule une portion de la grille est visible (effet de fenêtre)
   - Il est possible de se déplacer dans la grille pour explorer différentes zones

3. **Configurabilité** : Permettre au modeler de choisir le mode de zoom pour chaque grille individuellement.

## Comportement Actuel (Mode "resize")

### Description
- Le zoom modifie la taille physique du widget grille
- La grille grandit/rétrécit dans la fenêtre principale
- Tous les éléments sont redimensionnés proportionnellement
- La grille entière reste visible

### Déclenchement
- Molette de souris au-dessus de la grille
- Zoom avant (molette vers le haut) : agrandit la grille
- Zoom arrière (molette vers le bas) : réduit la grille

### Limites
- Zoom minimum : 0.3x
- Zoom maximum : 3.0x
- **Note** : Les mêmes limites s'appliquent au mode magnifier

## Nouveau Comportement (Mode "magnifier")

### Description
- Le zoom modifie l'échelle d'affichage du contenu sans changer la taille du widget grille
- La grille garde une taille fixe dans la fenêtre principale
- Le contenu est agrandi/réduit, créant un effet de loupe
- Seule une portion de la grille est visible à l'écran
- Il est possible de se déplacer (pan) dans la grille pour explorer différentes zones

### Déclenchement
- Molette de souris au-dessus de la grille (comme le mode actuel)
- Zoom avant (molette vers le haut) : agrandit le contenu, réduit la zone visible
- Zoom arrière (molette vers le bas) : réduit le contenu, augmente la zone visible

### Déplacement (Pan)
- **Méthode principale** : Drag & drop avec **Shift + clic gauche + glisser**
  - Maintenir Shift + clic gauche sur la grille
  - Glisser pour déplacer la zone visible
  - Relâcher pour fixer la nouvelle position
  - **Note** : L'utilisation de Shift permet d'éviter les conflits avec le drag & drop de la grille et des agents/tiles
- **Flèches clavier** : Non implémenté (à éviter)

### Point d'ancrage du zoom
- **Zoom avec molette** : Centré sur la position de la souris lors du scroll
  - Permet un zoom intuitif vers la zone d'intérêt
- **Zoom avec boutons menu** : Centré sur le centre de la grille
  - Permet un zoom centré et prévisible depuis l'interface

### Limites du pan
- Le déplacement est limité aux bords de la grille
- Impossible de dépasser les limites (pas de zones vides)
- La zone visible reste toujours à l'intérieur des limites de la grille

### Indicateurs visuels
- **Bordure/overlay** : Indicateur visuel discret pour indiquer que le mode magnifier est actif
  - Bordure colorée ou overlay subtil
  - Visible uniquement en mode magnifier
  - Permet de distinguer rapidement le mode actif
- **Mini-carte** : Non implémenté

## Configuration pour le Modeler

### Méthode 1 : Paramètre à la création
```python
# Créer une grille avec mode zoom magnifier
cellDef = myModel.newCellsOnGrid(
    columns=10, 
    rows=10, 
    zoomMode="magnifier"  # Nouveau paramètre
)

# Mode par défaut (comportement actuel)
cellDef = myModel.newCellsOnGrid(
    columns=10, 
    rows=10
    # zoomMode="resize" par défaut
)
```

### Méthode 2 : Configuration après création
```python
# Créer une grille
cellDef = myModel.newCellsOnGrid(columns=10, rows=10)

# Changer le mode de zoom
cellDef.grid.setZoomMode("magnifier")  # Mode loupe
cellDef.grid.setZoomMode("resize")    # Mode actuel (par défaut)
```

### Méthode 3 : Les deux (implémenté)
- Paramètre optionnel à la création pour configuration initiale
- Méthode `setZoomMode()` pour changer dynamiquement

### Exemples d'utilisation
```python
# Créer une grille avec mode magnifier
cellDef = myModel.newCellsOnGrid(
    columns=20, 
    rows=20, 
    zoomMode="magnifier"
)

# Changer le mode après création
cellDef.grid.setZoomMode("magnifier")  # Activer mode loupe
cellDef.grid.setZoomMode("resize")     # Revenir au mode par défaut
```

## Compatibilité

### Types de grilles
- **Grilles carrées** : Support complet
- **Grilles hexagonales** : Support complet

### Fonctionnalités existantes

#### Drag & drop de la grille (`moveable=True`)
- **En mode "resize"** : Fonctionne comme actuellement (clic gauche + glisser)
- **En mode "magnifier"** : 
  - Le pan utilise **Shift + clic gauche + glisser** pour éviter les conflits
  - Le drag & drop de la grille continue de fonctionner avec **clic gauche + glisser** (sans Shift)
  - Les deux fonctionnalités coexistent sans interférence
  - **Détection** : Si Shift est maintenu → pan, sinon → drag & drop de la grille

#### Drag & drop des agents/tiles
- Fonctionnent normalement dans les deux modes
- Utilisent clic gauche + glisser (sans Shift) comme actuellement
- Pas de conflit avec le pan (qui nécessite Shift)
- **Priorité** : Les agents/tiles ont la priorité sur le pan si le clic est sur un agent/tile

#### Clics sur les cellules
- Fonctionnent normalement dans les deux modes
- Pas d'impact du mode magnifier sur les interactions
- Les actions (Modify, Activate, etc.) fonctionnent comme actuellement

#### POV (Point of View)
- Fonctionne dans les deux modes
- Le zoom magnifier n'affecte pas le système POV

### Gestion des conflits d'interaction

**Hiérarchie de priorité des événements (mode magnifier)** :
1. **Shift + clic gauche + glisser** → Pan (déplacement de la vue)
2. **Clic gauche sur agent/tile + glisser** → Drag & drop agent/tile
3. **Clic gauche sur cellule** → Action sur cellule (si action disponible)
4. **Clic gauche + glisser (sans Shift, zone vide)** → Drag & drop de la grille (si `moveable=True`)

**Détection intelligente** :
- Si le clic est sur un agent/tile → Drag & drop agent/tile (priorité)
- Si le clic est sur une cellule avec action → Action sur cellule
- Si le clic est sur zone vide + Shift → Pan
- Si le clic est sur zone vide (sans Shift) → Drag & drop de la grille

## Cas d'usage

### Cas 1 : Grille de grande taille
- **Problème** : Grille 50x50 difficile à voir en entier
- **Solution** : Mode magnifier pour zoomer sur des zones spécifiques

### Cas 2 : Détails fins
- **Problème** : Besoin de voir les détails d'une zone précise
- **Solution** : Mode magnifier pour agrandir une zone sans perdre le contexte global

### Cas 3 : Présentation
- **Problème** : Besoin d'une grille de taille fixe pour la présentation
- **Solution** : Mode magnifier pour garder une taille constante tout en permettant le zoom

## API Programmatique pour le Modeler

En plus de la configuration du mode de zoom, des méthodes permettent de contrôler le zoom magnifier programmatiquement :

### Méthodes de contrôle du zoom magnifier

#### `setMagnifierOnArea(cellA, cellB)`
Définit la zone visible du magnifier pour afficher une zone rectangulaire entre deux cellules.

```python
# Zoomer sur une zone entre deux cellules
cellA = grid.getCell_withCoords(5, 5)
cellB = grid.getCell_withCoords(15, 15)
grid.setMagnifierOnArea(cellA, cellB)
```

**Comportement** :
- Calcule la zone rectangulaire entre les deux cellules
- Ajuste le niveau de zoom pour que cette zone soit visible
- Centre la vue sur cette zone
- Si les cellules sont dans le même sens (cellA après cellB), inverse automatiquement

#### `setMagnifierToCoverAllCellsWith(condition)`
Ajuste le zoom et la position pour afficher toutes les cellules répondant à une condition.

```python
# Zoomer pour voir toutes les cellules avec terrain="forest"
grid.setMagnifierToCoverAllCellsWith(lambda cell: cell.isValue("terrain", "forest"))

# Zoomer pour voir toutes les cellules avec des agents
grid.setMagnifierToCoverAllCellsWith(lambda cell: cell.hasAgent())
```

**Comportement** :
- Trouve toutes les cellules répondant à la condition
- Calcule la zone minimale contenant toutes ces cellules
- Ajuste le zoom pour que cette zone soit visible
- Centre la vue sur cette zone
- Si aucune cellule ne répond à la condition, ne fait rien (ou réinitialise)

#### Autres méthodes potentielles (à confirmer)
- `setMagnifierToCell(cell)` : Centrer et zoomer sur une cellule spécifique
- `setMagnifierToAgent(agent)` : Centrer et zoomer sur un agent spécifique
- `resetMagnifierView()` : Réinitialiser la vue (zoom 1.0, centré)
- `getMagnifierViewport()` : Obtenir les coordonnées de la zone visible actuelle

### Exemples d'utilisation avancée
```python
# Suivre un agent en mouvement
def followAgent(agent):
    grid.setMagnifierToAgent(agent)

# Explorer une zone spécifique après un événement
def exploreArea(x1, y1, x2, y2):
    cellA = grid.getCell_withCoords(x1, y1)
    cellB = grid.getCell_withCoords(x2, y2)
    grid.setMagnifierOnArea(cellA, cellB)

# Afficher toutes les cellules importantes
grid.setMagnifierToCoverAllCellsWith(
    lambda cell: cell.isValue("importance", "high")
)
```

## Notes techniques (non exhaustives)

### Architecture
- **Gestion de viewport** : Le mode magnifier nécessite une gestion de viewport (zone visible)
- **Transformation de coordonnées** : Conversion entre coordonnées écran (widget) et coordonnées grille (logiques)
- **Clipping** : Gestion du clipping pour n'afficher que la zone visible
- **Performance** : Optimisation du rendu pour n'afficher que les éléments visibles (culling)

### Gestion des événements
- **Priorité des événements** : 
  - Shift + clic gauche → Pan (mode magnifier uniquement)
  - Clic gauche seul → Drag & drop normal (grille, agents, tiles)
  - Molette → Zoom (les deux modes)
- **Détection de zone** : Détection de la zone cliquée (cellule, agent, tile, zone vide) pour gérer les interactions

### Compatibilité avec le système existant
- **Modification minimale** : Le mode magnifier doit s'intégrer sans casser le comportement existant
- **Mode par défaut** : Le mode "resize" reste le comportement par défaut pour compatibilité ascendante
- **Transition** : Possibilité de changer de mode dynamiquement sans perte de données

## Résumé des décisions

### Validé
- ✅ Pan avec **Shift + clic gauche + glisser** (évite les conflits)
- ✅ Zoom molette centré sur souris, zoom boutons centré sur centre grille
- ✅ Bordure/overlay pour indicateur visuel (pas de mini-carte)
- ✅ Limites de pan aux bords (pas de dépassement)
- ✅ API : Paramètre création + méthode `setZoomMode()`
- ✅ API programmatique : `setMagnifierOnArea()`, `setMagnifierToCoverAllCellsWith()`
- ✅ Compatible avec grilles carrées et hexagonales
- ✅ Compatible avec drag & drop existant (via Shift)

### À implémenter
- Mode magnifier avec viewport et transformations
- Pan avec Shift + clic gauche
- Indicateur visuel (bordure/overlay)
- API programmatique pour contrôle du zoom
- Gestion des conflits avec drag & drop

## Prochaines étapes

1. ✅ Spécification validée
2. Développer l'implémentation technique
3. Tester avec différents types de grilles et configurations
4. Tester les interactions (drag & drop, pan, zoom)
5. Documenter l'API pour les modelers
6. Créer des exemples d'utilisation
7. Ajouter tests unitaires si nécessaire

