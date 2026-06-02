# Plan de Refactorisation : Élimination de la Duplication `size` dans l'Architecture Model-View

## Date de création
2025-01-XX

## Contexte

### Problème identifié
L'architecture Model-View actuelle duplique l'attribut `size` entre Model et View :
- **Model** : `SGAgent.size`, `SGTile.size` (héritent de `SGEntity.size`)
- **View** : `SGAgentView.size`, `SGTileView.size` (copie initiale depuis Model, puis peut diverger)

Cette duplication crée des risques :
1. **Désynchronisation** : Si `model.size` change sans appeler `updateZoom()`, la View peut être désynchronisée
2. **Source de vérité ambiguë** : On ne sait pas toujours quelle source utiliser (`model.size` vs `view.size`)
3. **Duplication de `updateZoom()`** : Existe dans Model ET View, avec synchronisation manuelle
4. **Bugs potentiels** : Comme le bug de taille incorrecte en mode magnifier (résolu temporairement mais architecture fragile)

### Constatations du code
- `SGEntityView.__init__()` copie `self.size = entity_model.size` (ligne 28)
- `SGTileView` utilise parfois `self.entity_model.size` avec fallback vers `self.size` (lignes 143, 281)
- `SGGrid._updatePositionsForViewport()` modifie directement `view.size` (lignes 526, 585)
- `SGGrid.updateGridSize()` modifie directement `view.size` (lignes 722, 741, 744)
- `SGTile.moveTo()` synchronise manuellement `view.size = self.size` (lignes 407, 514)
- Plusieurs endroits utilisent le pattern `view.size if hasattr(view, 'size') else model.size`

## Objectifs de la refactorisation

1. **Source unique de vérité** : Le Model (`entity_model.size`) est la SEULE source de vérité pour `size`
2. **View en lecture seule** : La View lit toujours depuis le Model, ne maintient plus de copie
3. **Élimination de `updateZoom()` dans View** : Seul le Model a `updateZoom()`, qui met à jour automatiquement la View
4. **Cohérence** : Tous les accès à `size` passent par le Model
5. **Maintenabilité** : Architecture plus simple et moins sujette aux bugs

## Plan de refactorisation

### Phase 1 : Créer une propriété `size` dans SGEntityView (lecture depuis Model)

**Fichier** : `mainClasses/SGEntityView.py`

**Modification** :
- Supprimer `self.size = entity_model.size` dans `__init__()`
- Créer une propriété `@property def size(self)` qui retourne `self.entity_model.size`
- Cela permet de garder la compatibilité avec le code existant qui accède à `view.size`

**Code proposé** :
```python
class SGEntityView(QtWidgets.QWidget, SGEventHandlerGuide):
    def __init__(self, entity_model, parent=None):
        super().__init__(parent)
        self.entity_model = entity_model
        # ... autres initialisations ...
        # SUPPRIMER: self.size = entity_model.size
        
    @property
    def size(self):
        """Get size from model (single source of truth)"""
        return self.entity_model.size if hasattr(self.entity_model, 'size') else 0
```

**Avantages** :
- Compatibilité : Le code existant qui accède à `view.size` continue de fonctionner
- Source unique : La View lit toujours depuis le Model
- Pas de duplication : Plus besoin de synchroniser

### Phase 2 : Supprimer `updateZoom()` de SGAgentView et SGTileView

**Fichiers** : 
- `mainClasses/SGAgentView.py`
- `mainClasses/SGTileView.py`

**Modification** :
- Supprimer les méthodes `updateZoom()` des Views
- Garder uniquement `updateZoom()` dans les Models

**Code proposé** :
```python
# Dans SGAgent.updateZoom() - GARDE CETTE VERSION
def updateZoom(self, zoom_factor):
    """Update agent zoom based on zoom factor"""
    self.size = round(self.saveSize * zoom_factor)
    # La View lira automatiquement depuis self.size via la propriété
    if self.view:
        self.view.update()  # Force repaint avec nouvelle taille
        # Optionnel : mettre à jour la géométrie si position déjà définie
        if hasattr(self.view, 'xCoord') and hasattr(self.view, 'yCoord'):
            try:
                self.view.setGeometry(self.view.xCoord, self.view.yCoord, self.size, self.size)
            except RuntimeError:
                pass
```

**Avantages** :
- Logique centralisée dans le Model
- Plus de synchronisation manuelle nécessaire
- La View se met à jour automatiquement via la propriété

### Phase 3 : Mettre à jour tous les accès directs à `view.size`

**Fichiers à modifier** :

#### 3.1 `mainClasses/SGGrid.py`

**Lignes concernées** :
- Ligne 526 : `agent.view.size = round(agent.view.saveSize * self.zoom)` 
  → **Remplacer par** : `agent.updateZoom(self.zoom)` (déjà appelé ligne 708, mais vérifier cohérence)
- Ligne 530 : `agent_size = agent.view.size`
  → **Remplacer par** : `agent_size = agent.size` (depuis Model)
- Ligne 585 : `tile.view.size = round(tile.view.saveSize * self.zoom)`
  → **Remplacer par** : `tile.updateZoom(self.zoom)` (déjà appelé ligne 769, mais vérifier cohérence)
- Ligne 590 : `tile_size = tile.view.size`
  → **Remplacer par** : `tile_size = tile.size` (depuis Model)
- Lignes 722, 741, 744 : Modifications directes de `agent.view.size`
  → **Remplacer par** : Appels à `agent.updateZoom(self.zoom)`

**Code proposé** :
```python
# Dans _updatePositionsForViewport()
for agent in cell.getAgents():
    if hasattr(agent, 'view') and agent.view:
        # Size vient maintenant du Model via la propriété
        agent_size = agent.size  # Lit depuis Model via propriété view.size
        
# Dans updateGridSize()
for agent in cell.getAgents():
    agent.updateZoom(self.zoom)  # Met à jour model.size, view lit automatiquement
    if self.zoomMode == "magnifier":
        if hasattr(agent, 'view') and agent.view:
            # Plus besoin de modifier view.size directement
            # La View lit depuis agent.size via la propriété
            agent_size = agent.size
```

#### 3.2 `mainClasses/SGTile.py`

**Lignes concernées** :
- Lignes 407, 514 : `self.view.size = self.size`
  → **SUPPRIMER** : Plus nécessaire, la View lit depuis le Model
- Lignes 422, 525, 539 : `tile_size = self.view.size if hasattr(self.view, 'size') else self.size`
  → **Remplacer par** : `tile_size = self.size` (toujours depuis Model)

**Code proposé** :
```python
# Dans moveTo() - SUPPRIMER les lignes de synchronisation
# SUPPRIMER: self.view.size = self.size
# La View lit automatiquement depuis self.size via la propriété

# Utiliser directement model.size
tile_size = self.size  # Depuis Model
```

#### 3.3 `mainClasses/SGAgent.py`

**Lignes concernées** :
- Lignes 403, 440 : `agent_size = self.view.size if hasattr(self.view, 'size') else self.size`
  → **Remplacer par** : `agent_size = self.size` (toujours depuis Model)

#### 3.4 `mainClasses/SGEntityType.py`

**Lignes concernées** :
- Ligne 1508 : `agent_size = agent_view.size if hasattr(agent_view, 'size') else agent_model.size`
  → **Remplacer par** : `agent_size = agent_model.size`
- Ligne 2051 : `tile_size = tile_view.size if hasattr(tile_view, 'size') else tile_model.size`
  → **Remplacer par** : `tile_size = tile_model.size`

#### 3.5 `mainClasses/SGModel.py`

**Lignes concernées** :
- Ligne 465 : `agent_size = agent.view.size if hasattr(agent.view, 'size') else agent.size`
  → **Remplacer par** : `agent_size = agent.size`

### Phase 4 : Gérer `saveSize` de manière cohérente

**Problème** : `saveSize` est aussi dupliqué entre Model et View

**Solution** :
- Garder `saveSize` uniquement dans le Model
- La View peut avoir `saveSize` comme cache local pour performance, mais doit toujours lire depuis le Model si disponible

**Fichiers** :
- `mainClasses/SGAgentView.py` : Supprimer `self.saveSize = self.size` dans `__init__()`
- `mainClasses/SGTileView.py` : Supprimer `self.saveSize = self.size` dans `__init__()`
- `mainClasses/SGGrid.py` : Modifier les accès à `view.saveSize` pour utiliser `model.saveSize`

**Code proposé** :
```python
# Dans SGAgentView.__init__()
# SUPPRIMER: self.saveSize = self.size
# La View peut avoir un cache local, mais doit lire depuis Model si disponible

@property
def saveSize(self):
    """Get saveSize from model (single source of truth)"""
    return self.agent_model.saveSize if hasattr(self.agent_model, 'saveSize') else self.size
```

### Phase 5 : Mettre à jour les méthodes de positionnement

**Fichiers** :
- `mainClasses/SGAgentView.py` : `updatePositionInEntity()`
- `mainClasses/SGTileView.py` : `getPositionInCell()`, `paintEvent()`

**Modification** :
- Remplacer tous les accès à `self.size` par `self.entity_model.size` ou utiliser la propriété `self.size` (qui lit depuis Model)
- Supprimer les fallbacks `if hasattr(self.entity_model, 'size') else self.size`

**Code proposé** :
```python
# Dans SGAgentView.updatePositionInEntity()
# Remplacer: relX = int(self._randomX * (grid_size - self.size))
# Par: relX = int(self._randomX * (grid_size - self.size))  # self.size lit depuis Model via propriété

# Dans SGTileView.getPositionInCell()
# Remplacer: tile_size = self.entity_model.size if hasattr(self.entity_model, 'size') else self.size
# Par: tile_size = self.size  # Lit depuis Model via propriété
```

### Phase 6 : Mettre à jour `updateFromModel()` dans SGTileView

**Fichier** : `mainClasses/SGTileView.py`

**Ligne concernée** : Ligne 542 : `self.size = self.tile_model.size`

**Modification** :
- **SUPPRIMER** cette ligne : Plus nécessaire car `self.size` lit automatiquement depuis le Model via la propriété

**Code proposé** :
```python
def updateFromModel(self):
    """Update view properties from model"""
    if self.tile_model:
        # SUPPRIMER: self.size = self.tile_model.size  # Plus nécessaire
        # SUPPRIMER: self.saveSize = self.tile_model.saveSize  # Plus nécessaire si propriété
        # Garder les autres synchronisations nécessaires
        self.frontImage = self.tile_model.frontImage
        # ...
        self.update()
```

### Phase 7 : Tests et validation

**Tests à effectuer** :
1. Création d'agents/tuiles en mode magnifier (zoom ≠ 1)
2. Déplacement d'agents/tuiles en mode magnifier
3. Zoom in/out en mode magnifier
4. Zoom in/out en mode resize
5. Création via `CreateAction` en mode magnifier
6. Vérifier que toutes les tailles sont correctes dans tous les cas

**Fichiers de test** :
- `examples/syntax_examples/ex_tile_creation_magnifier.py`
- `examples/games/Sea_Zones_test_magnify.py`

## Ordre d'implémentation recommandé

1. **Phase 1** : Créer la propriété `size` dans `SGEntityView` (compatibilité maximale)
2. **Phase 2** : Supprimer `updateZoom()` des Views (test après chaque suppression)
3. **Phase 3** : Mettre à jour les accès directs (par fichier, tester après chaque fichier)
4. **Phase 4** : Gérer `saveSize` (optionnel, peut être fait en même temps que Phase 3)
5. **Phase 5** : Mettre à jour les méthodes de positionnement
6. **Phase 6** : Nettoyer `updateFromModel()`
7. **Phase 7** : Tests complets

## Risques et précautions

### Risques identifiés

1. **Performance** : Accès répétés à `entity_model.size` via propriété
   - **Mitigation** : Les propriétés Python sont rapides, impact négligeable
   - **Alternative** : Cache local avec invalidation si nécessaire

2. **Compatibilité** : Code existant qui modifie directement `view.size`
   - **Mitigation** : Phase 3 identifie et corrige tous ces cas
   - **Vérification** : Recherche exhaustive avec grep

3. **Initialisation** : `view.size` accédé avant que `entity_model` soit complètement initialisé
   - **Mitigation** : Vérifier l'ordre d'initialisation dans les factories
   - **Protection** : Gérer le cas où `entity_model` n'a pas encore `size`

### Points d'attention

1. **`SGGrid._updatePositionsForViewport()`** : Modifie directement `view.size` - doit être remplacé par `model.updateZoom()`
2. **`SGGrid.updateGridSize()`** : Modifie directement `view.size` - doit être remplacé par `model.updateZoom()`
3. **`SGTile.moveTo()`** : Synchronise manuellement - peut être supprimé
4. **Patterns de fallback** : `view.size if hasattr(view, 'size') else model.size` - remplacer par `model.size`

## Bénéfices attendus

1. **Architecture plus pure** : Model = source unique de vérité
2. **Moins de bugs** : Plus de désynchronisation possible
3. **Code plus simple** : Plus besoin de synchronisation manuelle
4. **Maintenabilité** : Plus facile à comprendre et modifier
5. **Cohérence** : Tous les accès à `size` passent par le Model

## Fichiers à modifier

### Fichiers principaux
1. `mainClasses/SGEntityView.py` - Propriété `size`
2. `mainClasses/SGAgentView.py` - Supprimer `updateZoom()`, utiliser propriété
3. `mainClasses/SGTileView.py` - Supprimer `updateZoom()`, utiliser propriété
4. `mainClasses/SGAgent.py` - Simplifier `updateZoom()`
5. `mainClasses/SGTile.py` - Simplifier `updateZoom()`, supprimer synchronisations
6. `mainClasses/SGGrid.py` - Remplacer accès directs à `view.size`
7. `mainClasses/SGEntityType.py` - Remplacer accès directs à `view.size`
8. `mainClasses/SGModel.py` - Remplacer accès directs à `view.size`

### Fichiers de test
- `examples/syntax_examples/ex_tile_creation_magnifier.py`
- `examples/games/Sea_Zones_test_magnifier.py`

## Notes d'implémentation

### Propriété Python pour `size`

```python
@property
def size(self):
    """Get size from model (single source of truth)"""
    if not hasattr(self, 'entity_model') or self.entity_model is None:
        return 0  # Fallback si model pas encore initialisé
    return getattr(self.entity_model, 'size', 0)
```

### Gestion de `saveSize`

Deux options :
1. **Option A** : Propriété aussi (lecture depuis Model)
2. **Option B** : Cache local avec synchronisation à l'initialisation uniquement

**Recommandation** : Option A pour cohérence totale

### Compatibilité avec code legacy

Si du code legacy modifie directement `view.size`, deux approches :
1. **Strict** : Lever une exception pour forcer la correction
2. **Permissif** : Définir un setter qui met à jour le Model

**Recommandation** : Approche permissive avec warning pour transition en douceur

```python
@size.setter
def size(self, value):
    """Set size on model (delegation)"""
    import warnings
    warnings.warn("Direct modification of view.size is deprecated. Use model.updateZoom() instead.", DeprecationWarning)
    if hasattr(self, 'entity_model') and self.entity_model:
        self.entity_model.size = value
```

## Validation finale

### Checklist de validation

- [ ] Tous les tests existants passent
- [ ] Création d'agents/tuiles en mode magnifier fonctionne
- [ ] Déplacement d'agents/tuiles en mode magnifier fonctionne
- [ ] Zoom in/out fonctionne en mode magnifier
- [ ] Zoom in/out fonctionne en mode resize
- [ ] Plus d'accès directs à `view.size` (vérifié avec grep)
- [ ] Plus de duplication de `updateZoom()` (vérifié avec grep)
- [ ] Documentation mise à jour si nécessaire

### Métriques de succès

1. **Réduction de duplication** : 0 duplication de `size` entre Model et View
2. **Réduction de code** : Suppression de ~50-100 lignes de synchronisation manuelle
3. **Bugs évités** : Plus de désynchronisation possible
4. **Maintenabilité** : Architecture plus claire et documentée

## Conclusion

Ce plan de refactorisation élimine la duplication dangereuse de `size` et `updateZoom()` en faisant du Model la source unique de vérité. La View lit toujours depuis le Model via une propriété, garantissant la cohérence et éliminant les risques de désynchronisation.

L'implémentation doit être progressive, avec tests après chaque phase, pour garantir la stabilité du système.
