# Analyse de l'Architecture SGE - Classes de Zoom

## Hiérarchie des Classes

### 1. SGGrid (Widget Qt)
```
SGGrid extends SGGameSpace extends QtWidgets.QWidget
```

**Propriétés clés :**
- `self.zoom = 1` (facteur de zoom)
- `self.saveSize` et `self.saveGap` (valeurs de référence)
- `self.size` et `self.gap` (valeurs actuelles zoomées)
- `self.frameMargin = 8` (marge du cadre)
- `self.cellShape` ("square" ou "hexagonal")

**Responsabilités :**
- Gestion du zoom via `wheelEvent()`
- Calcul de la taille minimale du widget
- Dessin du cadre de la grille
- Coordination avec les cellules

### 2. SGCell (Modèle)
```
SGCell extends SGEntity extends AttributeAndValueFunctionalities
```

**Propriétés clés :**
- `self.grid` (référence vers SGGrid)
- `self.xCoord`, `self.yCoord` (coordonnées 1-based)
- `self.size`, `self.gap` (copiés depuis la grille)
- `self.saveSize`, `self.saveGap` (valeurs de référence)
- `self.view` (référence vers SGCellView)

**Responsabilités :**
- Logique métier de la cellule
- Gestion des agents dans la cellule
- Méthodes de zoom (`updateZoom()`)

### 3. SGCellView (Vue Qt)
```
SGCellView extends SGEntityView extends QtWidgets.QWidget
```

**Propriétés clés :**
- `self.cell_model` (référence vers SGCell)
- `self.grid` (référence vers SGGrid)
- `self.xCoord`, `self.yCoord` (copiés depuis le modèle)
- `self.size`, `self.gap` (copiés depuis le modèle)

**Responsabilités :**
- Rendu visuel de la cellule
- Gestion des événements souris
- Calcul du positionnement (`calculatePosition()`)
- Dessin de la forme (carré/hexagone)

## Problèmes Identifiés dans Notre Implémentation

### 1. Duplication de Propriétés
**Problème :** Les propriétés `size`, `gap`, `xCoord`, `yCoord` sont dupliquées entre :
- SGCell (modèle)
- SGCellView (vue)
- SGGrid (conteneur)

**Impact :** Synchronisation complexe et source d'erreurs

### 2. Calcul de Position Incorrect
**Problème :** Dans `SGCellView.calculatePosition()`, nous utilisons :
```python
self.startX = int(self.startXBase + (self.xCoord - 1) * (self.size + self.gap) + self.gap)
```

**Mais :** `self.size` et `self.gap` dans SGCellView ne sont pas mis à jour lors du zoom !

### 3. Références Circulaires
**Problème :** 
- SGCell → SGCellView → SGGrid
- SGCellView → SGCell → SGGrid
- SGGrid → SGCell → SGCellView

**Impact :** Risque de références obsolètes

### 4. Synchronisation Zoom
**Problème :** Quand SGGrid change `self.size` et `self.gap`, les cellules ne sont pas automatiquement mises à jour.

## Solution Proposée

### 1. Centraliser les Valeurs de Zoom
- SGGrid garde les valeurs de référence (`saveSize`, `saveGap`)
- SGGrid calcule les valeurs zoomées (`size`, `gap`)
- Les cellules utilisent les valeurs de SGGrid

### 2. Simplifier le Calcul de Position
- Utiliser directement les valeurs de SGGrid
- Éliminer la duplication dans SGCellView

### 3. Améliorer la Synchronisation
- SGCellView doit toujours lire les valeurs depuis SGGrid
- Éviter de stocker des copies dans SGCellView

## Corrections Nécessaires

1. **SGCellView.calculatePosition()** : Utiliser `self.grid.size` et `self.grid.gap`
2. **SGCell.updateZoom()** : Supprimer, utiliser directement SGGrid
3. **SGCellView.__init__()** : Ne pas copier `size` et `gap`
4. **SGGrid.updateGridSize()** : Forcer la mise à jour des vues
