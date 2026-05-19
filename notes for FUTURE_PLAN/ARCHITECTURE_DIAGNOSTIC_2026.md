# Diagnostic architectural SGE — Mai 2026

**Date :** 20 mai 2026  
**Branche :** main  
**Méthode :** lecture directe du code source (SGSGE.py, SGModel.py, SGEntity.py, SGEntityType.py, SGGameSpace.py, SGAgent.py, SGTimeManager.py, SGExtensions.py, SGAspect.py, AttributeAndValueFunctionalities.py)

---

## Ce que le diagnostic précédent (nov. 2025) a bien identifié

Les points suivants sont confirmés et toujours valides :

- Séparation Model-View (`SGAgent`/`SGAgentView` etc.) bien respectée
- Pattern Factory via `SGEntityFactory` et les méthodes `newAgentAtCoords` etc.
- Polymorphisme des layouts via `applyLayout()`
- Organisation DEVELOPER/MODELER methods cohérente
- `SGTimeManager` offre une bonne séparation du flux temporel
- `SGMethodsCatalog` et la documentation sont de vrais atouts

---

## Observations nouvelles — issues identifiées dans le code réel

### Problème 1 — Star imports en cascade dans SGModel.py [PRIORITE HAUTE]

Dans SGModel.py, lignes 28-70, presque toutes les classes sont importées avec `*` :

```python
from mainClasses.SGAgent import *
from mainClasses.SGCell import *
from mainClasses.SGControlPanel import *
# ... ~30 star imports
```

**Conséquence concrète :** le namespace de SGModel reçoit des centaines de noms non déclarés. Un conflit de noms entre deux modules se règle silencieusement par l'ordre d'import, créant des bugs impossibles à tracer. La refactorisation devient dangereuse car supprimer un import ne cause pas d'erreur visible.

**Recommandation :** Remplacer par des imports explicites. `SGMQTTManager` et `SGEnhancedGridLayout` montrent déjà la bonne pratique (`from mainClasses.X import SGX`).

---

### Problème 2 — Incohérence self.TextBoxes / self.gameSpaces [PRIORITE HAUTE]

Ligne 136 de SGModel.py — commenté par le développeur lui-même :

```python
self.gameSpaces = {}
self.TextBoxes = []   # Why textBoxes are not in gameSpaces ?
```

`TextBoxes` vit en dehors du registre central `gameSpaces`. Toute méthode qui itère sur `self.gameSpaces` (layout, thème, export) ignore silencieusement les TextBoxes.

**Impact réel :** `applyThemeToAllGameSpaces` itère `self.gameSpaces.values()` — les TextBoxes n'en bénéficient pas. Idem pour les layouts.

**Recommandation :** Fusionner `TextBoxes` dans `gameSpaces`, ou créer une méthode `getAllGameSpaces()` qui agrège les deux.

---

### Problème 3 — Couplage implicite du mixin AttributeAndValueFunctionalities [PRIORITE HAUTE]

Dans `AttributeAndValueFunctionalities.saveValueInHistory()` :

```python
self.history["value"][aAttribute].append([
    self.model.timeManager.currentRoundNumber,
    self.model.timeManager.currentPhaseNumber,
    aValue
])
```

Ce mixin présuppose que tout objet qui l'hérite possède `self.model` pointant vers un SGModel avec un `timeManager`. Tester un SGEntity en isolation est impossible sans instancier un SGModel complet.

De plus, dans `setValue()` :

```python
if hasattr(self, 'type'):  # This is to prevent the EntDef from executing the following line
    self.type.updateWatchersOnAttribute(...)
```

Anti-pattern : le mixin utilise `hasattr` pour distinguer Entity vs EntityType au lieu d'une surcharge polymorphique.

**Recommandation long terme :** Injecter le round/phase au moment du save (paramètre ou callback) plutôt que via `self.model`.

---

### Problème 4 — SGTimeManager.nextPhase() est une méthode god [PRIORITE MOYENNE]

Ce seul appel fait : calcul de stats, vérification fin de partie, avancement round/phase, reset des actions, reset des action points, mise à jour TimeLabel, mise à jour window title, mise à jour UserSelector, mise à jour ControlPanels.

**Recommandation :** Décomposer en méthodes privées nommées (`_recordStepStats()`, `_advanceTime()`, `_resetActions()`, `_notifyObservers()`) et considérer un système d'événements interne pour découpler les notifications UI du moteur temporel.

---

### Problème 5 — Imports morts ou non conditionnels dans SGModel [PRIORITE MOYENNE]

Ligne 24 de SGModel.py :
```python
from paho.mqtt import client as mqtt_client
```
Importé inconditionnellement même pour un jeu simple sans mode distribué. Impose la dépendance `paho-mqtt` à tous les modelers.

Ligne 25 :
```python
from pyrsistent import s
```
`s` n'est pas utilisé dans SGModel. Import mort qui impose une dépendance inutile.

**Recommandation :** Rendre l'import paho-mqtt conditionnel (lazy import dans `enableDistributedGame()`), supprimer l'import pyrsistent.

---

### Problème 6 — SGModel.positionAllAgents() franchit la frontière Model-View [PRIORITE MOYENNE]

```python
def positionAllAgents(self):
    for agent_type in self.getAgentTypes():
        for agent in agent_type.entities:
            if hasattr(agent, 'view') and agent.view:
                agent.view.show()
                agent.view.raise_()
                agent.view.updatePositionInEntity()
```

SGModel (couche Model) orchestre directement les Views. Cela contredit le principe Model-View qui guide toute l'architecture.

**Recommandation :** Déléguer à une méthode sur la View elle-même, ou passer par un événement/signal Qt.

---

### Problème 7 — Monkey-patching du namespace Qt global dans SGExtensions [PRIORITE MOYENNE]

```python
Qt.pink = QColor.fromRgb(255, 192, 203)
Qt.orange = QColor.fromRgb(255, 165, 0)
QPainter.drawTextAutoSized = drawTextAutoSized
```

Ces effets de bord s'exécutent à l'import, ne sont pas documentés dans la complétion IDE, et créent des conflits potentiels si PyQt ajoute ces noms dans une future version.

**Recommandation :** Centraliser dans un objet `SGColors.pink`, `SGColors.orange` etc. plutôt que de polluer l'espace de noms Qt.

---

### Problème 8 — Croissance non bornée de l'historique [PRIORITE BASSE]

Dans `AttributeAndValueFunctionalities`, `history["value"]` est un `defaultdict(list)` qui s'allonge à chaque `setValue()` sans jamais être purgé. Pour des simulations longues avec beaucoup d'entités et d'attributs, la mémoire croît linéairement sans limite.

**Recommandation :** Ajouter une politique de rétention (max N rounds, purge à la demande via `clearHistory(beforeRound=N)`).

---

### Problème 9 — Dead code et commentaires orphelins dans SGModel [PRIORITE BASSE]

- `# self.users = ["Admin"]  # Moved above` — commentaire de refactoring laissé en place
- La branche `else: raise ValueError('This case is not handled')` dans `SGAgent.__init__` après `if cell is not None` — `cell=None` ne peut jamais arriver en pratique, la signature est trompeuse

---

### Problème 10 — SGGameSpaceSizeManager instancié par objet sans état propre [PRIORITE BASSE]

```python
self.size_manager = SGGameSpaceSizeManager()
```

Chaque GameSpace crée sa propre instance. Si `SGGameSpaceSizeManager` n'a pas d'état per-instance, c'est du gaspillage. Une instance partagée ou des méthodes statiques suffiraient.

---

## Ce que le code fait vraiment bien

### Le mixin AttributeAndValueFunctionalities est une abstraction puissante
Fournir setValue/getValue/isValue avec historique et watchers à TOUT objet via héritage est élégant. Le système `doWhenAttributeChanges` permet une réactivité propre sans event bus externe.

### SGSGE.py est une façade propre avec __all__ explicite
Le modeler écrit `from mainClasses.SGSGE import *` et obtient exactement ce dont il a besoin.

### L'ID système par classe de GameSpace est astucieux
```python
@classmethod
def nextId(cls):
    if not hasattr(cls, '_nextId'):
        cls._nextId = 0
    cls._nextId += 1
    return f"{cls.__name__}#{cls._nextId}"
```
Chaque sous-classe obtient son propre compteur sans registre central.

### SGExtensions regroupe intelligemment les utilitaires cross-cutting
`mapAlignmentStringToQtFlags`, `execute_callable_with_entity`, `getResourcePath` — centralisation bien faite.

### Le tag @CATEGORY: pour le catalogue de méthodes est pratique et bas-coût

---

## Tableau de synthèse

| # | Problème | Sévérité | Effort de correction |
|---|----------|----------|----------------------|
| 1 | Star imports en cascade dans SGModel | Haute | Moyen |
| 2 | TextBoxes hors de gameSpaces | Haute | Faible |
| 3 | Mixin couplé a model.timeManager | Haute | Eleve |
| 4 | nextPhase() methode god | Moyenne | Moyen |
| 5 | Imports morts/non-conditionnels | Moyenne | Faible |
| 6 | positionAllAgents() franchit M-V | Moyenne | Moyen |
| 7 | Monkey-patching namespace Qt | Moyenne | Faible |
| 8 | Historique non borne | Basse | Faible |
| 9 | Dead code / commentaires orphelins | Basse | Faible |
| 10 | SizeManager instancie inutilement | Basse | Faible |

---

## Recommandations priorisees

**Court terme (faible effort, impact immediat) :**
- Creer `getAllGameSpaces()` qui fusionne `gameSpaces` et `TextBoxes` (probleme 2)
- Supprimer `from pyrsistent import s` et rendre l'import `paho-mqtt` conditionnel (probleme 5)
- Nettoyer les commentaires orphelins et le dead code (probleme 9)

**Moyen terme :**
- Remplacer les star imports de SGModel par des imports nommes (probleme 1)
- Decomposer `nextPhase()` en methodes privees (probleme 4)
- Remplacer `Qt.orange` etc. par un objet `SGColors` (probleme 7)

**Long terme / architectural :**
- Decouplage du mixin de `model.timeManager` (probleme 3)
- Deplacer `positionAllAgents()` vers une couche de coordination View (probleme 6)
