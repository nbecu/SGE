# Refactoring des méthodes de récupération d'objets par nom dans SGModel

## Problème identifié

Dans `SGModel.py`, il existe de nombreuses méthodes qui permettent de récupérer des objets à partir de leur nom, mais ces méthodes présentent des incohérences importantes :

### Incohérences observées

1. **Nommage incohérent** :
   - `getAgentType(aTypeName)` vs `getEntityType(name)`
   - `getPlayer(aUserName)` vs `getUsersName()`
   - `getGameSpaceByName(name)` vs `getSubmenuSymbology(submenuName)`

2. **Paramètres variés** :
   - `name`, `aTypeName`, `aUserName`, `submenuName`, `aGridID`, `aId`
   - Pas de convention claire sur le nommage des paramètres

3. **Logique dupliquée** :
   - Recherche par nom répétée dans plusieurs méthodes
   - Gestion d'erreurs similaire (`ValueError` avec liste des éléments existants)

4. **Manque de méthodes inverses** :
   - Beaucoup de méthodes nom → objet
   - Peu de méthodes objet → nom
   - Pas de système cohérent pour les conversions bidirectionnelles

## Méthodes concernées

### Méthodes Nom → Objet
- `getEntityType(name)` - Retourne SGEntityType
- `getAgentType(aTypeName)` - Retourne SGAgentType  
- `getPlayer(aUserName)` - Retourne SGPlayer
- `getGameSpaceByName(name)` - Retourne SGGameSpace
- `getSubmenuSymbology(submenuName)` - Retourne symbologie
- `getSymbologiesOfSubmenu(submenuName)` - Retourne symbologies
- `getCheckedSymbologyOfEntity(name)` - Retourne symbologie cochée
- `getCellType(aGrid)` - Retourne SGCellType
- `getCell(aGrid, aId)` - Retourne cellule
- `getGrid_withID(aGridID)` - Retourne grille
- `getSGEntity_withIdentfier(aIdentificationDict)` - Retourne entité
- `getSGObject_withIdentifier(aIdentificationDict)` - Retourne objet SGE
- `getGameAction_withClassAndId(aClassName, aId)` - Retourne action
- `getUserControlPanelOrLegend(aUserName)` - Retourne panneau/légende

### Méthodes Objet → Nom/Liste
- `getUsersName()` - Retourne liste des noms d'utilisateurs
- `getUsers_withControlPanel()` - Retourne noms avec panneau
- `getUsers_withGameActions()` - Retourne noms avec actions

### Méthodes de récupération multiple
- `getEntityTypes()` - Tous les types d'entités
- `getAgentTypes()` - Tous les types d'agents
- `getAllEntities()` - Toutes les entités
- `getAllCells()` - Toutes les cellules
- `getAllAgents()` - Tous les agents
- `getAgentsOfType(aTypeName)` - Agents d'un type

## Refactoring proposé

### 1. Standardisation du nommage
- **Convention de paramètres** : Utiliser `name` pour tous les paramètres de nom
- **Convention de méthodes** : 
  - `get{ObjectType}ByName(name)` pour nom → objet
  - `get{ObjectType}Name(object)` pour objet → nom
  - `getAll{ObjectType}Names()` pour liste de noms

### 2. Création d'une classe utilitaire
Créer une classe `SGObjectRegistry` qui centralise :
- La logique de recherche par nom
- La gestion d'erreurs standardisée
- Le cache des objets pour améliorer les performances
- Les méthodes de conversion bidirectionnelles

### 3. Interface commune
Définir une interface `SGIdentifiable` que tous les objets SGE doivent implémenter :
```python
class SGIdentifiable:
    def getName(self) -> str
    def getIdentifier(self) -> str
    def getType(self) -> str
```

### 4. Méthodes génériques
Remplacer les méthodes spécifiques par des méthodes génériques :
```python
def getObjectByName(self, object_type: str, name: str) -> SGIdentifiable
def getObjectName(self, obj: SGIdentifiable) -> str
def getAllObjectNames(self, object_type: str) -> List[str]
```

### 5. Gestion d'erreurs standardisée
```python
class SGObjectNotFoundError(ValueError):
    def __init__(self, object_type: str, name: str, available_names: List[str]):
        super().__init__(f"No {object_type} found with name '{name}'. Available: {', '.join(available_names)}")
```

## Bénéfices attendus

1. **Cohérence** : Nommage uniforme et logique prévisible
2. **Maintenabilité** : Code centralisé et réutilisable
3. **Performance** : Cache et recherche optimisée
4. **Extensibilité** : Facile d'ajouter de nouveaux types d'objets
5. **Robustesse** : Gestion d'erreurs standardisée
6. **Documentation** : Interface claire et documentée

## Impact

- **Fichiers concernés** : `SGModel.py` (principalement)
- **Méthodes à refactorer** : ~20 méthodes
- **Compatibilité** : Nécessite une période de transition avec méthodes dépréciées
- **Tests** : Tous les tests utilisant ces méthodes devront être mis à jour

## Priorité

**Moyenne** - Améliore la qualité du code mais n'est pas critique pour la fonctionnalité existante.
