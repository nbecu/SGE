# Design: Aspect System pour remplacer POV

**Date:** 2026-06-14  
**Priorité:** Amélioration architecturale avant prochaine release  
**Effort estimé:** 2.5-3 jours  
**Impact:** 278 usages de newPov/newBorderPov à travers 163 fichiers

---

## 1. Problèmes avec le POV system actuel

### 1.1 Limitations structurelles

**Problème 1: Pas de hiérarchie**
- Les POV sont définis seulement au niveau EntityType
- Pas de résolution Entity → EntityType → Default
- Impossible de surcharger un POV pour une instance spécifique

**Problème 2: Symbologies rigides**
- Les couleurs sont la seule propriété visuelle (+ bordure)
- Impossible de combiner plusieurs attributs visuels (couleur + transparence + motif)
- Pas de support pour les "vues composées" (groupes de symbologies)

**Problème 3: Pas de gestion de groupes**
- Chaque POV est indépendant
- Impossible de basculer un groupe de symbologies ensemble
- Complexe quand on veut implémenter "voir les joueurs ET leurs ressources"

**Problème 4: Structure de données peu claire**
```python
# Code actuel - difficile à maintenir
povShapeColor = {
    "Health": {"health": {100: Qt.green, 80: Qt.yellow, 50: Qt.red}},
    "Owner": {"owner": {"Player1": Qt.blue, "Player2": Qt.red}}
}
```

---

## 2. Architecture proposée

### 2.1 Concepts clés

**SGVisualAspect:** Classe pour représenter une propriété visuelle unique
```python
SGVisualAspect:
  - symbol_type: str ('color', 'border', 'icon', 'pattern', 'transparency')
  - symbol_property: dict (ex: {value: color} ou {value: {color, width}})
  - attribute: str (ex: 'health', 'owner')
```

**SGSymbology:** Collection de SGVisualAspect (multi-dimensions)
```python
SGSymbology:
  - name: str ('Health', 'Owner')
  - aspects: List[SGVisualAspect]  # Peut combiner couleur + icône + transparence
  - condition: callable (optional, pour la résolution hiérarchique)
```

**SGAspectView:** Groupe de symbologies
```python
SGAspectView:
  - name: str ('DefaultView', 'PlayerView', 'ResourceView')
  - symbologies: List[SGSymbology]
  - is_active: bool
```

**SGAspectResolver:** Résolution hiérarchique
```python
SGAspectResolver.resolve(entity, attribute, symbol_type):
  1. Cherche dans Entity.aspects
  2. Si non trouvé, cherche dans EntityType.aspects
  3. Sinon retourne default
```

---

### 2.2 Hiérarchie de résolution

```
┌─────────────────────────────────────────┐
│ Entity.aspects (instance override)      │ ← Priorité 1 (si défini)
├─────────────────────────────────────────┤
│ EntityType.aspects (type definition)    │ ← Priorité 2 (défaut)
├─────────────────────────────────────────┤
│ Global.default_aspect (fallback)        │ ← Priorité 3
└─────────────────────────────────────────┘
```

**Exemple d'utilisation:**
```python
# EntityType définit un aspect
Cell.newSymbology("Health", "health", {100: Qt.green, 50: Qt.red})

# Instance peut surcharger
cell_instance.setSymbology("Health", "health", {100: Qt.blue})

# Résolution: utilise cell_instance.aspects d'abord
color = resolver.resolve(cell_instance, "health", "color")
# → Qt.blue (instance override)
```

---

## 3. API proposée (modeler-facing)

### 3.1 API de définition (dans SGEntityType)

```python
# Remplace newPov()
def newSymbology(self, name, attribute, value_to_symbol_dict, symbol_type='color'):
    """
    Args:
        name: str ('Health', 'Owner')
        attribute: str ('health', 'owner')
        value_to_symbol_dict: dict ({value: color} ou {value: {color, width}})
        symbol_type: str ('color', 'border', 'icon', 'pattern') [défault: 'color']
    """

# Pour les symbologies multi-dimensions
def newSymbologyWithBorder(self, name, attribute, value_to_dict):
    """Convenience method pour couleur + bordure"""

# Groupe plusieurs symbologies
def newAspectView(self, view_name, symbologies_list):
    """
    Args:
        view_name: str ('DefaultView', 'PlayerView')
        symbologies_list: [('Health', 'color'), ('Owner', 'border')]
    """

# Contrôle des vues
def setActiveAspectView(self, view_name):
def getActiveAspectView(self) -> SGAspectView
```

### 3.2 API d'instance (dans SGEntity)

```python
# Surcharger l'aspect pour une instance
def setInstanceSymbology(self, name, attribute, value_to_symbol_dict):
    """Override le symbology pour cette instance spécifique"""

# Lever les surcharges
def clearInstanceSymbology(self, name):
```

---

## 4. Stratégie de migration

### 4.1 Backward compatibility

**Option A (recommandée): Wrapper transparent**
```python
def newPov(self, name, attribute, value_to_color_dict):
    # Appel interne à newSymbology
    self.newSymbology(name, attribute, value_to_color_dict, symbol_type='color')
    
def newBorderPov(self, name, attribute, value_to_color_dict, borderWidth=3):
    # Convertir en format multi-dimension
    value_to_dict = {v: {color: c, width: borderWidth} for v, c in ...}
    self.newSymbology(name, attribute, value_to_dict, symbol_type='border')
```

**Avantages:**
- Les exemples existants (278 usages) continuent de fonctionner
- Pas de refactor immédiat requis
- Graduel: on peut migrer peu à peu

**Inconvénients:**
- La couche de compatibilité reste dans le code
- Peut masquer des bugs

### 4.2 Plan de migration graduel

**Phase 1: Infrastructure (1 jour)**
- Créer SGVisualAspect, SGSymbology, SGAspectView, SGAspectResolver
- Implémenter dans SGEntityType
- Wrapper newPov() → newSymbology()
- Tests: exemples existants continuent de passer

**Phase 2: Refactor crit core (1 jour)**
- Remplacer newPov() par newSymbology() dans les 3 jeux avancés:
  - CarbonPolis (déclarative)
  - Sea_Zones (CSV + images)
  - Solutre (Excel + hex)
- Tester chaque jeu
- Vérifier que la hiérarchie fonctionne

**Phase 3: Migration des exemples (0.5-1 jour)**
- Migrer progressivement les 163 fichiers
- Commencer par les A_to_Z (séquentiels)
- Puis syntax_examples
- Puis advanced_games (déjà fait en phase 2)
- Tool: script Python pour convertir les appels automatiquement (~80% des cas)

**Phase 4: Tests & cleanup (0.5 jour)**
- Smoke tests sur tous les exemples
- Retirer le wrapper newPov() si plus utilisé
- Documentation

---

## 5. Implémentation détaillée

### 5.1 Fichiers à créer

**`mainClasses/SGAspectSystem.py`** (~300 lignes)
```python
class SGVisualAspect:
    def __init__(self, symbol_type, attribute, mapping):
        self.symbol_type = symbol_type  # 'color', 'border', 'icon', ...
        self.attribute = attribute       # 'health', 'owner', ...
        self.mapping = mapping           # {value: symbol}

class SGSymbology:
    def __init__(self, name):
        self.name = name
        self.aspects = []  # List[SGVisualAspect]

class SGAspectView:
    def __init__(self, name, symbologies):
        self.name = name
        self.symbologies = symbologies  # List[SGSymbology]
        self.is_active = True

class SGAspectResolver:
    @staticmethod
    def resolve(entity, attribute, symbol_type, default=None):
        # Hiérarchie: Entity → EntityType → default
        ...
```

### 5.2 Modifications à SGEntityType

**Avant:**
```python
self.povShapeColor = {}
self.povBorderColorAndWidth = {}
```

**Après:**
```python
self.symbologies = {}  # {name: SGSymbology}
self.aspect_views = {}  # {name: SGAspectView}
self.active_aspect_view = None
```

**Nouvelles méthodes:**
```python
def newSymbology(self, name, attribute, mapping, symbol_type='color'):
    aspect = SGVisualAspect(symbol_type, attribute, mapping)
    if name not in self.symbologies:
        self.symbologies[name] = SGSymbology(name)
    self.symbologies[name].aspects.append(aspect)

def newAspectView(self, view_name, symbologies_list):
    view = SGAspectView(view_name, [self.symbologies[s] for s in symbologies_list])
    self.aspect_views[view_name] = view
```

### 5.3 Modifications à SGEntity

**Ajouter:**
```python
self.instance_symbologies = {}  # Surcharges par instance

def setInstanceSymbology(self, name, attribute, mapping):
    aspect = SGVisualAspect('color', attribute, mapping)
    if name not in self.instance_symbologies:
        self.instance_symbologies[name] = SGSymbology(name)
    self.instance_symbologies[name].aspects.append(aspect)
```

**Modifier readColorFromPovDef():**
```python
def readColorFromPovDef(self, aPovDef, aDefaultColor):
    # Cherche d'abord dans instance_symbologies
    color = SGAspectResolver.resolve(self, aPovDef, 'color')
    return color if color is not None else aDefaultColor
```

---

## 6. Cas d'usage validés

### 6.1 Hiérarchie simple (backward compatible)
```python
# EntityType definition
Sheep.newSymbology("Health", "health", {100: Qt.green, 50: Qt.red})

# Utilisation
sheep.readColorFromPovDef(...)  # ← Utilise EntityType
```

### 6.2 Instance override
```python
# Surcharge pour une instance
special_sheep.setInstanceSymbology("Health", "health", {100: Qt.blue, 50: Qt.orange})
special_sheep.readColorFromPovDef(...)  # ← Utilise instance override
```

### 6.3 Aspect views (groupes)
```python
# Définir plusieurs vues
Cell.newSymbology("Health", "health", {...})
Cell.newSymbology("Owner", "owner", {...})
Cell.newSymbology("Resources", "resource_count", {...})

Cell.newAspectView("HealthView", ["Health"])
Cell.newAspectView("PlayerView", ["Health", "Owner", "Resources"])

# Basculer
grid.setActiveAspectView("PlayerView")
```

### 6.4 Symbologies composées
```python
# Couleur + bordure + transparence
Cell.newSymbology("Complex", "health", mapping, symbol_type='color')
Cell.newSymbology("Complex", "health", mapping, symbol_type='border')
Cell.newSymbology("Complex", "health", mapping, symbol_type='transparency')
```

---

## 7. Considérations techniques

### 7.1 Performance
- La résolution hiérarchique est O(1) si bien codée (dict lookup)
- Cache optionnel: `entity._aspect_cache` pour ne pas recalculer à chaque frame

### 7.2 Sérialisation
- Les symbologies doivent être sérialisables (pour save/load de parties)
- Format JSON: utiliser des indices de couleur plutôt que Qt.Color

### 7.3 Gestion d'erreurs
- Validation: symbology_name existe-t-il?
- Message d'erreur clair si attribute n'existe pas

---

## 8. Validation requise avant de coder

**Avant de commencer Phase 1, valider:**

- [ ] La hiérarchie (Entity → EntityType → default) répond aux besoins?
- [ ] L'API newSymbology() est claire pour les modelers?
- [ ] La backward-compatibility via newPov() wrapper est acceptable?
- [ ] Les jeux avancés (Sea_Zones, Solutre) peuvent être portés sans impact?
- [ ] La structure SGVisualAspect est suffisante pour les futures extensions (images, patterns)?

---

## 9. Risques & mitigations

| Risque | Impact | Mitigation |
|--------|--------|-----------|
| 278 usages à migrer | Élevé | Script de conversion auto + backward compat |
| Refactor de SGEntity | Moyen | Tests exhaustifs sur exemples |
| Bug dans résolution hiérarchique | Moyen | Unit tests spécifiques |
| Compatibilité jeux existants | Moyen | Tests smoke sur CarbonPolis, Sea_Zones, Solutre |

---

## Notes supplémentaires

- **Naming:** "Symbology" = ensemble de propriétés visuelles, "Aspect" = système global
- **Alternative considérée:** Utiliser le système SGAspect existant (pour styles) — rejeté car c'est du styling UI, pas de la représentation d'entités
- **Future:** Ce système peut supporter des "plugins" de symbotypes (ex: particle system, custom shaders)

