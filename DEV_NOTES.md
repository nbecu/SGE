# DEV_NOTES.md
# Suivi de développement SGE

## Objectif
Ce fichier documente l'état actuel du développement SGE, les problèmes en cours, les solutions trouvées et les prochaines étapes. Il sert de journal de bord pour maintenir la continuité entre les sessions de travail et les différents ordinateurs.

---

## État actuel du développement

### Date de dernière mise à jour : 26/12/2024
### Dernier chat utilisé : Claude Sonnet 4 (Cursor)
### Ordinateur de travail : Windows 10 (nbecu)
### Branche actuelle : refactor/model-view-separation (architecture Model-View terminée)

---

## Travail en cours

### 25/08/2025 - Refactoring Admin-to-super-player (TERMINÉ)
- **Statut** : ✅ Terminé et mergé sur main_candidate_release_august_2025
- **Description** : Transformation de l'Admin en "super player" utilisant le système gameAction standard, séparation complète de SGLegend et SGControlPanel
- **Fichiers concernés** : 
  - `mainClasses/SGModel.py` (ajout SGAdminPlayer, API ergonomique)
  - `mainClasses/SGAdminPlayer.py` (nouveau - super player)
  - `mainClasses/SGLegend.py` (refactoring - pure légende)
  - `mainClasses/SGControlPanel.py` (refactoring - interface contrôle)
  - `mainClasses/SGLegendItem.py` (adaptation comportement)
  - `mainClasses/gameAction/SGModify.py` (SGModifyActionWithDialog)
  - `mainClasses/SGEntityDef.py` (découverte attributs)
  - `mainClasses/SGPlayer.py` (adaptation)
  - `mainClasses/SGTimeManager.py` (gestion Admin player)
  - `README_developer.md` (documentation conventions)
- **Problèmes rencontrés** : Imports circulaires, conflits git, bugs d'initialisation
- **Solutions appliquées** : Refactoring architecture, gestion des imports, cherry-pick git

### 25/08/2025 - Amélioration API délégation et tests (TERMINÉ)
- **Statut** : ✅ Terminé
- **Description** : Amélioration des méthodes de délégation dans SGModel et ajout de tests pytest pour la conversion automatique des noms de joueurs
- **Fichiers concernés** : 
  - `mainClasses/SGModel.py` (méthodes de délégation complétées)
  - `mainClasses/SGTimeManager.py` (conversion automatique noms→instances)
  - `tests/test_player_names_in_phases.py` (nouveau - tests pytest)
  - `pytest.ini` (nouveau - configuration pytest)
- **Améliorations** : 
  - Tous les paramètres des méthodes principales sont maintenant disponibles dans les délégations
  - Conversion automatique des noms de joueurs en instances (comme pour 'Admin')
  - Tests complets avec pytest pour valider la fonctionnalité
- **Problèmes rencontrés** : Configuration Cursor pour détecter les tests pytest
- **Solutions appliquées** : Création de pytest.ini, format pytest standard

### 26/12/2024 - Architecture Model-View (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Implémentation complète de l'architecture Model-View pour SGAgent, SGCell, SGEntity avec séparation claire entre logique (Model) et UI (View)
- **Branche** : refactor/model-view-separation
- **Contexte** : Refactoring majeur pour permettre déplacement fluide des agents sans perte d'état
- **Fichiers concernés** : 
  - `mainClasses/SGAgent.py` (hérite de SGEntityModel, délègue UI)
  - `mainClasses/SGCell.py` (renommé de SGCellModel.py, hérite de SGEntityModel)
  - `mainClasses/SGAgentView.py` (gestion UI et interactions)
  - `mainClasses/SGCellView.py` (rendu et événements cellules)
  - `mainClasses/SGEntityFactory.py` (factory pour paires Model-View)
  - `mainClasses/SGModel.py` (positioning et gestion phases)
  - `mainClasses/SGEntityDef.py` (méthodes standard sans suffixe WithModelView)
  - `mainClasses/SGTimeManager.py` (gestion control panels)
  - `mainClasses/SGControlPanel.py` (activation visuelle)
  - `mainClasses/SGGameSpace.py` (drag & drop robuste)
  - `mainClasses/gameAction/SGCreate.py` (création avec Model-View)
  - `mainClasses/SGModelAction.py` (nettoyage debug prints)
  - `README_developer.md` (documentation architecture Model-View)
- **Problèmes rencontrés** : Agents dupliqués, tooltips cassés, control panels invisibles, imports circulaires
- **Solutions appliquées** : 
  - Séparation claire Model/View avec délégation UI
  - Gestion robuste du cycle de vie des vues
  - Méthodes `show()`, `update()`, `repaint()` optimisées
  - Factory pattern pour création cohérente
  - Nomenclature unifiée (SGCell au lieu de SGCellModel)

---

## Prochaines étapes

### Priorité haute - Tests et validation Model-View
- [x] Architecture Model-View implémentée et testée
- [x] Renommage SGCellModel → SGCell pour cohérence
- [x] Documentation README_developer.md mise à jour
- [x] Tests avec exStep3_1_1.py, ex_move.py, exStep8.py validés
- [ ] Tests avec modèles complexes (Solutre, CarbonPolis, etc.)
- [ ] Validation performance déplacement agents

### Priorité moyenne - Optimisations et nettoyage
- [x] Suppression méthodes temporaires et debug prints
- [x] Organisation méthodes selon convention (developer/modeler)
- [x] Nettoyage imports et références obsolètes
- [ ] Optimisation performance rendering
- [ ] Amélioration gestion mémoire vues

### Priorité basse - Documentation et exemples
- [ ] Création exemples spécifiques Model-View
- [ ] Documentation migration pour modelers existants
- [ ] Guide bonnes pratiques architecture

### Priorité moyenne - Tests et validation
- [x] Créer des tests pytest pour les nouvelles fonctionnalités
- [x] Configurer l'environnement de test (pytest.ini)
- [ ] Améliorer la détection des tests dans Cursor/IDE
- [ ] Ajouter des tests pour les autres fonctionnalités critiques

### Priorité moyenne
- [x] Documenter les nouvelles conventions découvertes
- [x] Optimiser l'API ergonomique (délégations)
- [ ] Créer des exemples pour les nouvelles fonctionnalités
- [ ] Améliorer la documentation des tests

### Priorité basse
- [ ] Nettoyer le code obsolète identifié
- [ ] Optimiser les performances

---

## Problèmes résolus

### 26/12/2024 - Architecture Model-View (MAJOR)
- **Description** : Refactoring complet pour séparer Model et View dans SGAgent, SGCell, SGEntity
- **Solution** : 
  1. Création de classes View : SGAgentView, SGCellView
  2. Refactoring SGAgent pour hériter de SGEntityModel et déléguer UI
  3. Renommage SGCellModel → SGCell pour cohérence nomenclature
  4. Factory pattern dans SGEntityFactory pour création cohérente
  5. Gestion robuste du cycle de vie des vues (show, update, repaint)
  6. Méthodes standard sans suffixe WithModelView pour API modeler
  7. Documentation complète dans README_developer.md
- **Fichiers modifiés** : 15+ fichiers principaux
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Commits** : Multiple commits avec push sur refactor/model-view-separation
- **Impact** : Architecture plus propre, déplacement fluide des agents, API transparente pour modelers

### 26/12/2024 - Agents dupliqués et mal positionnés
- **Description** : Agents affichés deux fois (position correcte + position 0,0)
- **Solution** : 
  1. Suppression création automatique de vue dans SGAgent.__init__
  2. Délégation création vue à SGEntityFactory
  3. Gestion explicite du parent des vues lors du déplacement
  4. Appel systématique de show() après positioning
- **Fichiers modifiés** : SGAgent.py, SGEntityFactory.py, SGModel.py

### 26/12/2024 - Tooltips cassés après drag & drop
- **Description** : Tooltips ne s'affichaient plus après déplacement d'agents
- **Solution** : 
  1. Ajout mouseReleaseEvent dans SGAgentView
  2. Reset robuste de self.dragging après drag.exec_()
  3. Suppression logique fallback tooltip pour restaurer comportement original
- **Fichiers modifiés** : SGAgentView.py

### 26/12/2024 - Control panels invisibles ou non activés
- **Description** : Control panels disparaissaient lors du drag ou n'étaient pas visuellement activés
- **Solution** : 
  1. Vérification robuste dans SGGameSpace.mouseMoveEvent (isVisible, parent, bounds)
  2. Ajout self.update() dans SGControlPanel.setActivation pour forcer repaint
  3. Délégation activation control panels à SGTimeManager.updateControlPanelsForCurrentPhase
- **Fichiers modifiés** : SGGameSpace.py, SGControlPanel.py, SGTimeManager.py, SGModel.py

### 26/12/2024 - Imports circulaires et références obsolètes
- **Description** : Erreurs d'imports après suppression SGCellModel.py et références à SGCell
- **Solution** : 
  1. Replace all SGCellModel → SGCell dans tous les fichiers
  2. Mise à jour tous les imports pour pointer vers mainClasses.SGCell
  3. Suppression références obsolètes et méthodes temporaires
- **Fichiers modifiés** : 13 fichiers avec imports mis à jour

### 25/08/2025 - Amélioration API délégation et conversion noms de joueurs
- **Description** : Les méthodes de délégation dans SGModel ne prenaient pas en compte tous les paramètres disponibles et la conversion automatique des noms de joueurs était limitée à 'Admin'
- **Solution** : 
  1. Complétion des méthodes de délégation `newPlayPhase` et `newModelPhase` avec tous les paramètres
  2. Extension de la conversion automatique des noms de joueurs en instances pour tous les joueurs
  3. Gestion d'erreurs robuste avec warnings pour les noms invalides
  4. Création de tests pytest complets pour valider la fonctionnalité
  5. Configuration pytest.ini pour l'environnement de test
- **Fichiers modifiés** : `mainClasses/SGModel.py`, `mainClasses/SGTimeManager.py`, `tests/test_player_names_in_phases.py` (nouveau), `pytest.ini` (nouveau)
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Impact** : API plus intuitive et robuste pour les modelers

### 25/08/2025 - Refactoring Admin-to-super-player (MAJOR)
- **Description** : Transformation complète du système Admin pour utiliser le système gameAction standard
- **Solution** : 
  1. Création de `SGAdminPlayer` héritant de `SGPlayer`
  2. Séparation complète `SGLegend` (pure légende) et `SGControlPanel` (interface)
  3. Ajout d'attributs de type (`isLegend`, `isControlPanel`, etc.)
  4. API ergonomique avec méthodes de délégation
  5. Découverte automatique des attributs d'entités
  6. Actions de modification avec dialogue utilisateur
- **Fichiers modifiés** : 15+ fichiers principaux
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Commits** : Multiple commits avec cherry-pick sur main

### 25/08/2025 - Imports circulaires et bugs d'initialisation
- **Description** : Problèmes d'imports circulaires et d'ordre d'initialisation
- **Solution** : 
  1. Commentaire des imports problématiques
  2. Réorganisation de l'ordre d'initialisation dans SGModel
  3. Gestion des cas edge dans SGAbstractAction.canBeUsed()
- **Fichiers modifiés** : SGAbstractAction.py, SGCell.py, SGModel.py

### 25/08/2025 - Conflits git et cherry-pick
- **Description** : Conflits lors du cherry-pick sur main
- **Solution** : 
  1. Résolution manuelle des conflits
  2. Adaptation du code pour la branche main
  3. Validation des fonctionnalités après merge

### 25/08/2025 - ModuleNotFoundError: No module named 'screeninfo'
- **Description** : L'import `from screeninfo import get_monitors` dans SGModel.py échouait
- **Solution** : 
  1. Ajout de `screeninfo>=0.8.1` dans `pyproject.toml`
  2. Suppression de `requirements.txt` (éviter la duplication)
  3. Installation de SGE dans l'environnement global : `pip install -e .`
  4. Configuration de l'éditeur pour utiliser le bon interpréteur Python
- **Fichiers modifiés** : `pyproject.toml`, `requirements.txt` (supprimé)
- **Chat utilisé** : Claude Sonnet 4 (Cursor)

---

## Décisions importantes

### 26/12/2024 - Architecture Model-View
- **Contexte** : Besoin de déplacer les agents sans perdre leur état et améliorer l'organisation du code
- **Décision prise** : Implémentation complète de l'architecture Model-View pour SGAgent, SGCell, SGEntity
- **Impact** : 
  - Architecture plus propre avec séparation claire logique/UI
  - Déplacement fluide des agents sans perte d'état
  - API transparente pour les modelers (pas de changement nécessaire)
  - Meilleure maintenabilité et extensibilité

### 26/12/2024 - Nomenclature cohérente
- **Contexte** : Incohérence entre SGAgent (sans suffixe) et SGCellModel (avec suffixe)
- **Décision prise** : Renommage SGCellModel → SGCell pour cohérence
- **Impact** : Nomenclature unifiée et plus intuitive pour les développeurs

### 26/12/2024 - API transparente pour modelers
- **Contexte** : Les modelers ne doivent pas être impactés par l'architecture Model-View
- **Décision prise** : 
  1. Méthodes standard sans suffixe WithModelView (newAgentAtCoords, newCell, etc.)
  2. Factory pattern pour création automatique des paires Model-View
  3. Délégation transparente entre Model et View
- **Impact** : Aucun changement nécessaire dans le code des modelers

### 26/12/2024 - Gestion robuste du cycle de vie des vues
- **Contexte** : Problèmes de positioning et d'affichage des vues
- **Décision prise** : 
  1. Utilisation systématique de show() après création/déplacement
  2. Gestion explicite du parent des vues lors du déplacement entre grilles
  3. Différenciation claire entre update() (asynchrone) et repaint() (synchrone)
- **Impact** : Affichage robuste et cohérent des éléments UI

### 25/08/2025 - Attributs de type identification
- **Contexte** : Besoin de distinguer les types d'objets sans héritage complexe
- **Décision prise** : Utiliser des attributs booléens `is*` (isLegend, isControlPanel, etc.)
- **Impact** : Séparation claire des responsabilités, API plus intuitive

### 25/08/2025 - API ergonomique et conversion automatique
- **Contexte** : Simplifier l'API pour les modelers et permettre l'utilisation de noms de joueurs
- **Décision prise** : 
  1. Créer des méthodes de délégation complètes dans les classes principales
  2. Étendre la conversion automatique des noms de joueurs en instances (pas seulement 'Admin')
- **Impact** : 
  - `model.newPlayPhase()` au lieu de `model.timeManager.newPlayPhase()`
  - `["Player 1", "Admin"]` au lieu de `[Player1, adminPlayer]`

### 25/08/2025 - Gestion des dépendances
- **Contexte** : Duplication entre requirements.txt et pyproject.toml
- **Décision prise** : Utiliser uniquement pyproject.toml pour les dépendances
- **Impact** : Simplification de la gestion des dépendances, standard moderne PEP 517/518

---

## Conventions découvertes et documentées

### 26/12/2024 - Architecture Model-View
- **Convention** : Séparation claire entre Model (logique) et View (UI) pour les entités principales
- **Exemples** : SGAgent/SGAgentView, SGCell/SGCellView
- **Avantage** : Déplacement fluide des agents, code plus maintenable, séparation des responsabilités

### 26/12/2024 - Factory Pattern pour Model-View
- **Convention** : Utiliser des méthodes factory pour créer des paires Model-View cohérentes
- **Exemples** : `entityDef.newAgentAtCoords()`, `entityDef.newCell()`
- **Avantage** : Création automatique et cohérente, API transparente pour modelers

### 26/12/2024 - Cycle de vie des vues Qt
- **Convention** : Gestion robuste du cycle de vie avec show(), update(), repaint()
- **Exemples** : `agent.view.show()` après déplacement, `self.update()` pour repaint
- **Avantage** : Affichage cohérent et performant des éléments UI

### 26/12/2024 - Nomenclature cohérente
- **Convention** : Noms de classes sans suffixe pour les modèles principaux
- **Exemples** : SGAgent, SGCell (au lieu de SGAgentModel, SGCellModel)
- **Avantage** : API plus intuitive et cohérente
### 25/08/2025 - Type Identification Attributes
- **Convention** : Utiliser des attributs booléens `is*` pour identifier le type d'objet
- **Exemples** : `isAdmin`, `isAgentDef`, `isCellDef`, `isLegend`, `isControlPanel`
- **Avantage** : Séparation des responsabilités sans héritage complexe

### 25/08/2025 - API Ergonomics and Delegation
- **Convention** : Créer des méthodes de délégation dans les classes principales
- **Exemples** : `model.newPlayPhase()`, `model.getAdminPlayer()`
- **Avantage** : API plus intuitive pour les modelers

### 25/08/2025 - Complex Instance Creation
- **Convention** : Utiliser le préfixe `new` pour créer des instances complexes
- **Exemples** : `model.newModifyActionWithDialog()`
- **Avantage** : API cohérente et prévisible

### 25/08/2025 - Player Name Conversion
- **Convention** : Permettre l'utilisation de noms de joueurs dans les listes `activePlayers`
- **Exemples** : `["Player 1", "Admin", Player2]` (mélange noms et instances)
- **Avantage** : API plus flexible et intuitive pour les modelers

---

## Chats importants

### 26/12/2024 - Architecture Model-View (MAJOR)
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Implémentation complète de l'architecture Model-View
- **Résultats** : 
  - Architecture Model-View complètement implémentée
  - Séparation claire entre SGAgent/SGAgentView et SGCell/SGCellView
  - Renommage SGCellModel → SGCell pour cohérence
  - API transparente pour modelers (pas de changement nécessaire)
  - Documentation complète dans README_developer.md
- **Fichiers modifiés** : 15+ fichiers principaux
- **Durée** : Session complète de développement
- **Commits** : Multiple commits avec push sur refactor/model-view-separation

### 25/08/2025 - Refactoring Admin-to-super-player (MAJOR)
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Transformation complète du système Admin
- **Résultats** : 
  - Admin transformé en super player
  - SGLegend et SGControlPanel séparés
  - API ergonomique améliorée
  - Conventions documentées
- **Fichiers modifiés** : 15+ fichiers principaux
- **Durée** : Session complète de développement

### 25/08/2025 - Résolution screeninfo et création exemple
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Résolution du problème d'import screeninfo et création d'un exemple pour defaultActionSelected
- **Résultats** : 
  - Problème screeninfo résolu
  - Environnement de développement simplifié
  - Nouvel exemple créé : ex_defaultActionSelected_for_controlPanel.py
- **Fichiers modifiés** : 
  - pyproject.toml
  - examples/syntax_examples/ex_defaultActionSelected_for_controlPanel.py (nouveau)

### 25/08/2025 - Amélioration API délégation et tests pytest
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Amélioration des méthodes de délégation et création de tests pour la conversion automatique des noms de joueurs
- **Résultats** : 
  - API de délégation complétée avec tous les paramètres
  - Conversion automatique des noms de joueurs en instances étendue
  - Tests pytest complets créés et validés
  - Configuration pytest.ini pour l'environnement de test
- **Fichiers modifiés** : 
  - mainClasses/SGModel.py (délégations complétées)
  - mainClasses/SGTimeManager.py (conversion noms→instances)
  - tests/test_player_names_in_phases.py (nouveau)
  - pytest.ini (nouveau)

---

## Notes techniques

### Modifications importantes
- 26/12/2024 : Architecture Model-View complètement implémentée (15+ fichiers)
- 26/12/2024 : Renommage SGCellModel → SGCell pour cohérence nomenclature
- 26/12/2024 : Documentation README_developer.md mise à jour avec section Model-View
- 26/12/2024 : Tests validés avec exStep3_1_1.py, ex_move.py, exStep8.py
- 25/08/2025 : Refactoring majeur Admin-to-super-player (15+ fichiers)
- 25/08/2025 : Séparation SGLegend/SGControlPanel
- 25/08/2025 : Ajout de screeninfo dans pyproject.toml
- 25/08/2025 : Suppression de requirements.txt
- 25/08/2025 : Création de l'exemple ex_defaultActionSelected_for_controlPanel.py
- 25/08/2025 : Amélioration API délégation (SGModel.py, SGTimeManager.py)
- 25/08/2025 : Création tests pytest (test_player_names_in_phases.py)
- 25/08/2025 : Configuration pytest.ini

### Découvertes architecturales
- 26/12/2024 : L'architecture Model-View permet un déplacement fluide des agents sans perte d'état
- 26/12/2024 : La nomenclature cohérente (SGAgent, SGCell) améliore l'intuitivité de l'API
- 26/12/2024 : Le factory pattern est essentiel pour la création cohérente des paires Model-View
- 26/12/2024 : La gestion robuste du cycle de vie des vues Qt (show, update, repaint) est cruciale
- 26/12/2024 : L'API transparente pour modelers est possible grâce à la délégation automatique
- 25/08/2025 : Les attributs de type `is*` permettent une séparation claire des responsabilités
- 25/08/2025 : L'API ergonomique améliore significativement l'expérience des modelers
- 25/08/2025 : La séparation Model-View est nécessaire pour le déplacement d'agents
- 25/08/2025 : L'utilisation de pyproject.toml seul est plus simple que requirements.txt + pyproject.toml
- 25/08/2025 : La conversion automatique des noms de joueurs améliore l'ergonomie de l'API
- 25/08/2025 : Les tests pytest standard facilitent la maintenance et la validation

### Questions en suspens
- Comment optimiser la performance du déplacement d'agents avec l'architecture Model-View ?
- Faut-il créer d'autres exemples pour les nouvelles fonctionnalités Model-View ?
- Comment gérer la migration des modèles existants vers la nouvelle architecture ?
- Faut-il étendre l'architecture Model-View à d'autres entités SGE ?
- Comment améliorer la détection des tests pytest dans Cursor/IDE ?
- Faut-il étendre la conversion automatique des noms à d'autres parties de l'API ?

---

## Instructions pour la mise à jour

### Avant de changer d'ordinateur :
1. **Commitez** vos changements sur GitHub
2. **Mettez à jour** ce fichier avec l'état actuel
3. **Notez** les problèmes non résolus
4. **Listez** les prochaines étapes

### Sur le nouvel ordinateur :
1. **Pull** les derniers changements
2. **Lisez** ce fichier pour reprendre le contexte
3. **Créez** un nouveau chat avec le contexte
4. **Continuez** le travail

---

## Template pour ajouter une entrée

### Travail en cours
```
### [Date] - [Fonctionnalité]
- **Statut** : En cours
- **Description** : [Description]
- **Fichiers concernés** : [Fichiers]
- **Problèmes** : [Problèmes]
- **Solutions testées** : [Solutions]
```

### Problème résolu
```
### [Date] - [Problème]
- **Description** : [Description]
- **Solution** : [Solution]
- **Fichiers modifiés** : [Fichiers]
- **Chat utilisé** : [Chat]
```

### Décision importante
```
### [Date] - [Décision]
- **Contexte** : [Contexte]
- **Décision prise** : [Décision]
- **Impact** : [Impact]
```
