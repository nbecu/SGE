# DEV_NOTES.md
# Suivi de développement SGE

## Objectif
Ce fichier documente l'état actuel du développement SGE, les problèmes en cours, les solutions trouvées et les prochaines étapes. Il sert de journal de bord pour maintenir la continuité entre les sessions de travail et les différents ordinateurs.

---

## État actuel du développement

### Date de dernière mise à jour : 25/08/2025
### Dernier chat utilisé : Claude Sonnet 4 (Cursor)
### Ordinateur de travail : Windows 10 (nbecu)
### Branche actuelle : main (améliorations API et tests)

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

### 25/08/2025 - Prochaine étape : Séparation Model-View (À COMMENCER)
- **Statut** : 🎯 Prêt à commencer
- **Description** : Séparer Model et View pour SGEntity, SGCell, SGAgent pour permettre déplacement fluide des agents
- **Branche cible** : refactor/model-view-separation
- **Contexte** : Suite logique du refactoring précédent

---

## Prochaines étapes

### Priorité haute - Chantier Model-View Separation
- [ ] Créer la branche `refactor/model-view-separation`
- [ ] Analyser l'architecture actuelle de SGEntity, SGCell, SGAgent
- [ ] Créer les classes View : SGEntityView, SGCellView, SGAgentView
- [ ] Adapter les classes Model pour la séparation
- [ ] Créer des tests de validation du déplacement d'agents
- [ ] Maintenir la compatibilité de l'API existante

### Priorité haute - Tests et validation
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

### 25/08/2025 - Architecture Model-View
- **Contexte** : Besoin de déplacer les agents sans perdre leur état
- **Décision prise** : Séparer Model et View pour SGEntity, SGCell, SGAgent
- **Impact** : Architecture plus propre, déplacement fluide des agents

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
- 25/08/2025 : Refactoring majeur Admin-to-super-player (15+ fichiers)
- 25/08/2025 : Séparation SGLegend/SGControlPanel
- 25/08/2025 : Ajout de screeninfo dans pyproject.toml
- 25/08/2025 : Suppression de requirements.txt
- 25/08/2025 : Création de l'exemple ex_defaultActionSelected_for_controlPanel.py
- 25/08/2025 : Amélioration API délégation (SGModel.py, SGTimeManager.py)
- 25/08/2025 : Création tests pytest (test_player_names_in_phases.py)
- 25/08/2025 : Configuration pytest.ini

### Découvertes architecturales
- 25/08/2025 : Les attributs de type `is*` permettent une séparation claire des responsabilités
- 25/08/2025 : L'API ergonomique améliore significativement l'expérience des modelers
- 25/08/2025 : La séparation Model-View est nécessaire pour le déplacement d'agents
- 25/08/2025 : L'utilisation de pyproject.toml seul est plus simple que requirements.txt + pyproject.toml
- 25/08/2025 : La conversion automatique des noms de joueurs améliore l'ergonomie de l'API
- 25/08/2025 : Les tests pytest standard facilitent la maintenance et la validation

### Questions en suspens
- Comment optimiser la performance du déplacement d'agents avec la séparation Model-View ?
- Faut-il créer d'autres exemples pour les nouvelles fonctionnalités ?
- Comment gérer la migration des modèles existants vers la nouvelle architecture ?
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
