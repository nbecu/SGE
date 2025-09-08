# DEV_NOTES.md
# Suivi de développement SGE

## Objectif
Ce fichier documente l'état actuel du développement SGE, les problèmes en cours, les solutions trouvées et les prochaines étapes. Il sert de journal de bord pour maintenir la continuité entre les sessions de travail et les différents ordinateurs.

---

## État actuel du développement

### Date de dernière mise à jour : 26/12/2024
### Dernier chat utilisé : Claude Sonnet 4 (Cursor)
### Ordinateur de travail : Windows 10 (nbecu)
### Branche actuelle : refactor/model-view-separation (drag & drop des gameSpaces terminé)
### Dernier chantier : Refactoring drag & drop des gameSpaces + corrections SGControlPanel + SGGrid

---

## Travail en cours

### 26/12/2024 - Système de tooltips avancé (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Implémentation d'un système de tooltips complet avec menu dynamique, tooltips personnalisés et méthode setTooltip() pour les modelers
- **Fichiers concernés** : 
  - `mainClasses/SGModel.py` (menu dynamique des tooltips, initBeforeShowing())
  - `mainClasses/SGEntityDef.py` (méthode setTooltip(), displayTooltip() améliorée)
  - `mainClasses/AttributeAndValueFunctionalities.py` (méthode hasAttribute())
  - `examples/syntax_examples/ex_tooltip_2.py` (exemple mis à jour)
  - `examples/syntax_examples/ex_tooltip_3.py` (nouveau exemple)
  - `FUTURE_PLAN.md` (mise à jour chantier terminé)
- **Problèmes rencontrés** : Menu incohérent avec doublons, tooltips statiques affichant None, timing d'initialisation
- **Solutions appliquées** : 
  - Refactoring menu dynamique avec sous-menus individuels par EntityDef
  - Méthode setTooltip() pour tooltips personnalisés (attributs, texte statique, lambdas)
  - Méthode hasAttribute() pour vérification robuste d'existence d'attributs
  - Initialisation dans initBeforeShowing() pour timing correct
  - Suppression option "Custom" obsolète
  - Correction affichage tooltips statiques
- **Résultat** : Système de tooltips complet et flexible pour les modelers, menu dynamique cohérent, exemples complets

### 26/12/2024 - Refactoring drag & drop des gameSpaces + corrections SGControlPanel + SGGrid (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Refactoring complet du système de drag & drop des gameSpaces, passage de QDrag à mouvement direct de la souris, corrections SGControlPanel et SGGrid pour compatibilité
- **Fichiers concernés** : 
  - `mainClasses/SGGameSpace.py` (refactoring drag & drop, passage QDrag → mouvement direct)
  - `mainClasses/SGControlPanel.py` (refactoring constructeur __init__, corrections mousePressEvent)
  - `mainClasses/SGPlayer.py` (mise à jour utilisation SGControlPanel)
  - `mainClasses/SGGrid.py` (corrections mouseMoveEvent pour compatibilité drag & drop)
  - `mainClasses/SGUserSelector.py` (ajout orientation verticale/horizontale)
  - `mainClasses/SGModel.py` (ajout paramètre orientation dans newUserSelector)
  - `examples/syntax_examples/ex_userSelector_orientation.py` (nouveau - exemple orientation)
  - `FUTURE_PLAN.md` (mise à jour chantier drag & drop terminé)
- **Problèmes rencontrés** : Drag & drop non intuitif avec QDrag, SGControlPanel non draggable, SGGrid incompatible avec nouveau système, hauteur excessive SGUserSelector
- **Solutions appliquées** : 
  - Abandon complet du système QDrag au profit d'un mouvement direct basé sur global mouse position
  - Implémentation du comportement hotspot intuitif (point cliqué reste sous curseur)
  - Refactoring SGControlPanel pour utiliser constructeur __init__ standard
  - Correction SGControlPanel.mousePressEvent pour appeler super().mousePressEvent()
  - Mise à jour SGPlayer pour utiliser nouveau constructeur SGControlPanel
  - Correction SGGrid.mouseMoveEvent pour déléguer à super() quand isDraggable
  - Ajout orientation verticale/horizontale dans SGUserSelector
  - Réduction hauteur SGUserSelector (padding réduit, min_height 25px)
  - Création exemple syntax_examples pour démonstration orientation
- **Résultat** : Système de drag & drop fluide et intuitif pour tous les gameSpaces, comportement hotspot cohérent, SGControlPanel et SGGrid compatibles

### 26/12/2024 - Gestion de taille des gameSpaces + SGGameSpaceSizeManager (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Implémentation d'un système de gestion de taille adaptative pour les gameSpaces, création de SGGameSpaceSizeManager, et corrections des problèmes de sizing dans SGTextBox, SGEndGameRule, SGEndGameCondition, et SGUserSelector
- **Fichiers concernés** : 
  - `mainClasses/SGGameSpaceSizeManager.py` (nouveau - classe utilitaire pour gestion de taille)
  - `mainClasses/SGGameSpace.py` (intégration SGGameSpaceSizeManager, méthodes utilitaires)
  - `mainClasses/SGTextBox.py` (sizing dynamique, correction débordement widgets internes)
  - `mainClasses/SGEndGameRule.py` (sizing dynamique basé sur layout)
  - `mainClasses/SGEndGameCondition.py` (remplacement QTextEdit par QLabel, sizing adaptatif)
  - `mainClasses/SGUserSelector.py` (sizing dynamique, réduction hauteur excessive)
  - `mainClasses/SGModel.py` (amélioration factory method newTextBox)
  - `FUTURE_PLAN.md` (mise à jour chantiers terminés)
- **Problèmes rencontrés** : Hauteur excessive SGUserSelector, débordement widgets internes SGTextBox, taille disproportionnée SGEndGameCondition, sizing fixe non adaptatif
- **Solutions appliquées** : 
  - Création de SGGameSpaceSizeManager pour centraliser la logique de sizing
  - Intégration dans SGGameSpace avec méthodes utilitaires (adjustSizeToContent, calculateContentWidth/Height)
  - Refactoring SGTextBox pour sizing dynamique basé sur layout.sizeHint()
  - Refactoring SGEndGameRule pour sizing adaptatif des conditions
  - Remplacement QTextEdit par QLabel dans SGEndGameCondition avec word wrapping dynamique
  - Réduction hauteur SGUserSelector (50px → 25px + padding réduit)
  - Amélioration factory method newTextBox avec paramètres complets
  - Respect des tailles manuelles (sizeX/sizeY) avec priorité sur sizing automatique
- **Résultat** : Système de sizing adaptatif et cohérent pour tous les gameSpaces, élimination des tailles disproportionnées et débordements

### 26/12/2024 - Refactoring Model-View + corrections finales + documentation (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Refactoring complet de l'architecture Model-View, corrections des méthodes dans SGEntityDef, résolution des bugs UI, et mise à jour de la documentation
- **Fichiers concernés** : 
  - `mainClasses/SGEntity.py` (renommé de SGEntityModel.py, classe de base)
  - `mainClasses/SGAgent.py` (hérite de SGEntity, délègue UI à SGAgentView)
  - `mainClasses/SGCell.py` (renommé de SGCellModel.py, hérite de SGEntity)
  - `mainClasses/SGAgentView.py` (gestion UI et interactions agents)
  - `mainClasses/SGCellView.py` (rendu et événements cellules)
  - `mainClasses/SGEntityView.py` (classe de base pour les vues)
  - `mainClasses/SGEntityFactory.py` (renommé de SGEntityDefFactory.py, factory Model-View)
  - `mainClasses/SGEntityDef.py` (corrections méthodes newAgentAtCoords, newCell, deleteEntity)
  - `mainClasses/SGModel.py` (imports mis à jour, gestion phases)
  - `mainClasses/SGTimeManager.py` (gestion control panels)
  - `mainClasses/SGControlPanel.py` (activation visuelle avec update())
  - `mainClasses/SGGameSpace.py` (drag & drop robuste)
  - `mainClasses/gameAction/SGCreate.py` (création avec Model-View)
  - `mainClasses/SGModelAction.py` (nettoyage debug prints)
  - `examples/A_to_Z_examples/exStep3_1_1.py` (correction assignation agent)
  - `examples/A_to_Z_examples/exStep8.py` (correction assignation agent)
  - `examples/syntax_examples/ex_move.py` (correction assignation agent)
  - `examples/games/CarbonPolis.py` (test validation final)
  - `README_developer.md` (section architecture Model-View complète)
  - `DEV_NOTES.md` (mise à jour état actuel)
  - `CONTEXT_SGE_FOR_CHATBOT.md` (règles critiques Model-View)
  - `tests/test_model_view_architecture.py` (imports mis à jour)
  - `tests/test_model_view_separation.py` (imports mis à jour)
  - `tests/test_entity_factory.py` (renommé de test_entity_def_factory.py)
  - `tests/test_sgagent_model_view_adaptation.py` (imports mis à jour)
- **Problèmes rencontrés** : Agents dupliqués, tooltips cassés, control panels invisibles, imports circulaires, méthodes retournant tuples au lieu de modèles, RuntimeError lors de suppression vues
- **Solutions appliquées** : 
  - Séparation claire Model/View avec délégation UI
  - Gestion robuste du cycle de vie des vues (show, update, repaint)
  - Factory pattern pour création cohérente des paires Model-View
  - Nomenclature unifiée (SGCell au lieu de SGCellModel, SGEntity au lieu de SGEntityModel)
  - Renommage SGEntityDefFactory → SGEntityFactory pour clarté
  - Correction méthodes SGEntityDef pour retourner seulement les modèles
  - Suppression méthodes dupliquées et obsolètes
  - Protection RuntimeError avec try-except dans deleteEntity()
  - Correction drag & drop avec vérifications robustes
  - Activation visuelle control panels avec update()

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

### 26/12/2024 - Renommage SGEntityModel → SGEntity (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Renommage de SGEntityModel en SGEntity pour harmoniser la nomenclature
- **Contexte** : Après suppression de l'ancienne classe SGEntity, renommage de SGEntityModel pour avoir une nomenclature cohérente
- **Fichiers concernés** :
  - `mainClasses/SGEntityModel.py` → `mainClasses/SGEntity.py` (renommé)
  - `mainClasses/SGAgent.py` (héritage mis à jour)
  - `mainClasses/SGCell.py` (héritage mis à jour)
  - `mainClasses/SGEntityFactory.py` (imports mis à jour)
  - `mainClasses/SGDashBoard.py` (références de type mises à jour)
  - `mainClasses/SGDataRecorder.py` (imports mis à jour)
  - `mainClasses/SGTestGetData.py` (imports mis à jour)
  - `mainClasses/SGModel.py` (imports mis à jour)
  - `mainClasses/SGCellView.py` (imports mis à jour)
  - `mainClasses/SGFormatDataHistory.py` (imports mis à jour)
  - `tests/test_sgagent_model_view_adaptation.py` (imports mis à jour)
  - Documentation mise à jour (README_developer.md, DEV_NOTES.md, CONTEXT_SGE_FOR_CHATBOT.md)
- **Résultat** : Architecture parfaitement cohérente avec SGEntity comme classe de base pour SGAgent et SGCell

### 26/12/2024 - Architecture Model-View (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Implémentation complète de l'architecture Model-View pour SGAgent, SGCell, SGEntity avec séparation claire entre logique (Model) et UI (View)
- **Branche** : refactor/model-view-separation
- **Contexte** : Refactoring majeur pour permettre déplacement fluide des agents sans perte d'état
- **Fichiers concernés** : 
  - `mainClasses/SGAgent.py` (hérite de SGEntity, délègue UI)
  - `mainClasses/SGCell.py` (renommé de SGCellModel.py, hérite de SGEntity)
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

### Gestion de taille des gameSpaces - TERMINÉ ✅
Le système de gestion de taille adaptative est **complètement terminé** et validé :
- [x] Création de SGGameSpaceSizeManager pour centraliser la logique de sizing
- [x] Intégration dans SGGameSpace avec méthodes utilitaires
- [x] Refactoring SGTextBox pour sizing dynamique basé sur layout.sizeHint()
- [x] Refactoring SGEndGameRule pour sizing adaptatif des conditions
- [x] Remplacement QTextEdit par QLabel dans SGEndGameCondition avec word wrapping dynamique
- [x] Réduction hauteur SGUserSelector (50px → 25px + padding réduit)
- [x] Amélioration factory method newTextBox avec paramètres complets
- [x] Respect des tailles manuelles (sizeX/sizeY) avec priorité sur sizing automatique
- [x] Correction débordement widgets internes dans SGTextBox
- [x] Élimination des tailles disproportionnées dans SGEndGameCondition
- [x] Tests avec exStep8.py, aGameExample.py, Delmoges_v3.py validés
- [x] Mise à jour FUTURE_PLAN.md avec les avancées

### Architecture Model-View - TERMINÉ ✅
L'architecture Model-View est **complètement terminée** et validée :
- [x] Architecture Model-View implémentée et testée
- [x] Renommage SGCellModel → SGCell pour cohérence
- [x] Suppression SGEntity et renommage SGEntityModel → SGEntity
- [x] Renommage SGEntityDefFactory → SGEntityFactory
- [x] Documentation README_developer.md mise à jour
- [x] Tests avec exStep3_1_1.py, exStep8.py, CarbonPolis.py validés
- [x] Correction bugs UI (control panels, tooltips, drag & drop)
- [x] Protection RuntimeError dans deleteEntity()
- [x] API transparente pour modelers (pas de changement nécessaire)
- [x] Nettoyage méthodes dupliquées et obsolètes
- [x] Documentation CONTEXT_SGE_FOR_CHATBOT.md mise à jour

### Refactoring drag & drop des gameSpaces - TERMINÉ ✅
Le système de drag & drop des gameSpaces est **complètement terminé** et validé :
- [x] Refactoring complet du système QDrag vers mouvement direct de la souris
- [x] Implémentation du comportement hotspot intuitif (point cliqué reste sous curseur)
- [x] Correction SGControlPanel pour utiliser constructeur __init__ standard
- [x] Correction SGControlPanel.mousePressEvent pour compatibilité drag & drop
- [x] Mise à jour SGPlayer pour utiliser nouveau constructeur SGControlPanel
- [x] Correction SGGrid.mouseMoveEvent pour déléguer à super() quand isDraggable
- [x] Ajout orientation verticale/horizontale dans SGUserSelector
- [x] Réduction hauteur SGUserSelector (padding réduit, min_height 25px)
- [x] Création exemple syntax_examples pour démonstration orientation
- [x] Tests avec exStep8.py et ex_userSelector_orientation.py validés
- [x] Mise à jour FUTURE_PLAN.md avec le chantier terminé

### Prochaines étapes générales
- [ ] Nouvelles fonctionnalités SGE (selon besoins futurs)
- [ ] Optimisations performance (si nécessaire)
- [ ] Améliorations UI/UX (selon retours utilisateurs)
- [ ] Documentation modeler (si nouveaux besoins)
- [ ] Extension SGGameSpaceSizeManager à d'autres types de widgets
- [ ] Optimisation performance du sizing adaptatif

---

## Problèmes résolus

### 26/12/2024 - Refactoring drag & drop des gameSpaces (MAJOR)
- **Description** : Système de drag & drop non intuitif avec QDrag, SGControlPanel non draggable, SGGrid incompatible avec nouveau système, hauteur excessive SGUserSelector
- **Solution** : 
  1. Abandon complet du système QDrag au profit d'un mouvement direct basé sur global mouse position
  2. Implémentation du comportement hotspot intuitif (point cliqué reste sous curseur)
  3. Refactoring SGControlPanel pour utiliser constructeur __init__ standard
  4. Correction SGControlPanel.mousePressEvent pour appeler super().mousePressEvent()
  5. Mise à jour SGPlayer pour utiliser nouveau constructeur SGControlPanel
  6. Correction SGGrid.mouseMoveEvent pour déléguer à super() quand isDraggable
  7. Ajout orientation verticale/horizontale dans SGUserSelector
  8. Réduction hauteur SGUserSelector (padding réduit, min_height 25px)
  9. Création exemple syntax_examples pour démonstration orientation
  10. Tests de validation avec exStep8.py et ex_userSelector_orientation.py
- **Fichiers modifiés** : `SGGameSpace.py`, `SGControlPanel.py`, `SGPlayer.py`, `SGGrid.py`, `SGUserSelector.py`, `SGModel.py`, `ex_userSelector_orientation.py` (nouveau), `FUTURE_PLAN.md`
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Impact** : Système de drag & drop fluide et intuitif pour tous les gameSpaces, comportement hotspot cohérent, SGControlPanel et SGGrid compatibles

### 26/12/2024 - Gestion de taille des gameSpaces (MAJOR)
- **Description** : Problèmes de sizing dans les gameSpaces : hauteur excessive, débordement widgets internes, tailles disproportionnées, sizing fixe non adaptatif
- **Solution** : 
  1. Création de `SGGameSpaceSizeManager` pour centraliser la logique de sizing
  2. Intégration dans `SGGameSpace` avec méthodes utilitaires (`adjustSizeToContent`, `calculateContentWidth/Height`)
  3. Refactoring `SGTextBox` pour sizing dynamique basé sur `layout.sizeHint()`
  4. Refactoring `SGEndGameRule` pour sizing adaptatif des conditions
  5. Remplacement `QTextEdit` par `QLabel` dans `SGEndGameCondition` avec word wrapping dynamique
  6. Réduction hauteur `SGUserSelector` (50px → 25px + padding réduit)
  7. Amélioration factory method `newTextBox` avec paramètres complets
  8. Respect des tailles manuelles (`sizeX`/`sizeY`) avec priorité sur sizing automatique
  9. Correction débordement widgets internes dans `SGTextBox`
  10. Élimination des tailles disproportionnées dans `SGEndGameCondition`
- **Fichiers modifiés** : `SGGameSpaceSizeManager.py` (nouveau), `SGGameSpace.py`, `SGTextBox.py`, `SGEndGameRule.py`, `SGEndGameCondition.py`, `SGUserSelector.py`, `SGModel.py`, `FUTURE_PLAN.md`
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Impact** : Système de sizing adaptatif et cohérent pour tous les gameSpaces, élimination des problèmes de taille

### 26/12/2024 - Architecture Model-View complète (MAJOR)
- **Description** : Refactoring complet de l'architecture Model-View avec toutes les corrections finales
- **Solution** : 
  1. Implémentation complète de l'architecture Model-View pour SGAgent, SGCell, SGEntity
  2. Renommage SGCellModel → SGCell et SGEntityModel → SGEntity pour cohérence
  3. Renommage SGEntityDefFactory → SGEntityFactory pour clarté
  4. Correction des méthodes SGEntityDef pour retourner seulement les modèles
  5. Suppression des méthodes dupliquées et obsolètes
  6. Protection RuntimeError avec try-except dans deleteEntity()
  7. Correction des bugs UI (control panels, tooltips, drag & drop)
  8. Gestion robuste du cycle de vie des vues Qt
  9. Factory pattern pour création cohérente des paires Model-View
  10. API transparente pour modelers (pas de changement nécessaire)
  11. Documentation complète dans README_developer.md et CONTEXT_SGE_FOR_CHATBOT.md
- **Fichiers modifiés** : 25+ fichiers principaux
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Commits** : Multiple commits avec push sur main
- **Impact** : Architecture Model-View complètement fonctionnelle, déplacement fluide des agents, API transparente

### 26/12/2024 - Corrections finales Model-View (MAJOR)
- **Description** : Corrections des méthodes SGEntityDef et résolution des bugs UI finaux
- **Solution** : 
  1. Correction newAgentAtCoords() pour retourner seulement le modèle (pas le tuple)
  2. Correction newCell() pour retourner seulement le modèle (pas le tuple)
  3. Correction newAgentOnCell() pour ajouter seulement le modèle à self.entities
  4. Suppression des méthodes dupliquées dans SGEntityDef
  5. Protection RuntimeError avec try-except dans deleteEntity() pour vues déjà supprimées
  6. Correction drag & drop avec vérifications robustes dans SGGameSpace
  7. Activation visuelle control panels avec update() dans SGControlPanel
  8. Tests de validation avec CarbonPolis.py sans erreur
- **Fichiers modifiés** : SGEntityDef.py, SGGameSpace.py, SGControlPanel.py, examples/
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Impact** : API cohérente pour modelers, bugs UI résolus, architecture Model-View stable

### 26/12/2024 - Architecture Model-View (MAJOR)
- **Description** : Refactoring complet pour séparer Model et View dans SGAgent, SGCell, SGEntity
- **Solution** : 
  1. Création de classes View : SGAgentView, SGCellView
  2. Refactoring SGAgent pour hériter de SGEntity et déléguer UI
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

### 26/12/2024 - SGGameSpaceSizeManager pour centraliser la gestion de taille
- **Contexte** : Problèmes de sizing dans les gameSpaces : hauteur excessive, débordement widgets internes, tailles disproportionnées, sizing fixe non adaptatif
- **Décision prise** : Créer une classe dédiée `SGGameSpaceSizeManager` pour centraliser la logique de sizing, similaire à `SGAspect` pour les styles
- **Impact** : 
  - Centralisation de la logique de sizing dans une classe réutilisable
  - Séparation des responsabilités (sizing vs styles)
  - API cohérente pour tous les gameSpaces
  - Facilité de maintenance et d'extension

### 26/12/2024 - Sizing dynamique basé sur layout.sizeHint()
- **Contexte** : Sizing fixe non adaptatif dans SGTextBox et SGEndGameRule
- **Décision prise** : Utiliser `layout.sizeHint()` comme source principale de sizing, avec fallback sur calcul manuel
- **Impact** : 
  - Sizing adaptatif au contenu réel
  - Respect des contraintes Qt
  - Élimination des tailles disproportionnées
  - Meilleure intégration avec le système Qt

### 26/12/2024 - Remplacement QTextEdit par QLabel dans SGEndGameCondition
- **Contexte** : Taille disproportionnée des SGEndGameCondition par rapport au texte
- **Décision prise** : Remplacer `QTextEdit` par `QLabel` avec word wrapping dynamique basé sur la longueur du texte
- **Impact** : 
  - Taille adaptée au contenu texte
  - Word wrapping intelligent (seuil à 50 caractères)
  - Interface plus légère et performante
  - Sizing cohérent avec les autres widgets

### 26/12/2024 - Priorité des tailles manuelles sur sizing automatique
- **Contexte** : Besoin de respecter les tailles manuelles (sizeX/sizeY) tout en gardant le sizing automatique
- **Décision prise** : Prioriser les tailles manuelles dans `getSizeXGlobal()` et `getSizeYGlobal()` avec fallback sur sizing automatique
- **Impact** : 
  - Flexibilité pour les modelers (override possible)
  - Sizing automatique par défaut
  - API intuitive et prévisible
  - Respect des contraintes spécifiques

### 26/12/2024 - Centralisation méthodes legacy UI
- **Contexte** : Duplication des méthodes UI dans SGAgent et SGCell après architecture Model-View
- **Décision prise** : Centraliser toutes les méthodes legacy UI dans SGEntity pour éviter la duplication
- **Impact** : Code plus maintenable, héritage cohérent, suppression de la duplication

### 26/12/2024 - Méthodes utilitaires SGExtensions
- **Contexte** : Besoin de méthodes utilitaires communes pour éviter la duplication de code
- **Décision prise** : Créer des méthodes utilitaires dans SGExtensions.py (execute_callable_with_entity, normalize_species_name)
- **Impact** : Code plus réutilisable, gestion dynamique des arguments lambda, normalisation des noms d'espèces

### 26/12/2024 - Documentation PowerShell vs Bash
- **Contexte** : Problèmes récurrents avec la syntaxe PowerShell (&& non supporté)
- **Décision prise** : Documenter explicitement les différences PowerShell vs Bash dans CONTEXT_SGE_FOR_CHATBOT.md
- **Impact** : Évite les erreurs courantes pour les futurs chatbots

### 26/12/2024 - Exemples pédagogiques de déplacement
- **Contexte** : Besoin d'exemples clairs pour les différentes méthodes de déplacement
- **Décision prise** : Créer ex_move_1.py (moveTo), ex_move_2.py (moveAgent), ex_move_3.py (numberOfMovement)
- **Impact** : Documentation pratique pour les modelers, exemples complets et testés

### 26/12/2024 - API moveAgent unifiée et auto-détection
- **Contexte** : Besoin d'unifier l'API moveAgent avec un paramètre `target` flexible
- **Décision prise** : 
  1. Remplacer `cellID` par `target` (plus générique)
  2. `target` accepte int (ID), tuple (coords), str (direction)
  3. Auto-détection de la méthode basée sur le type de `target`
  4. `method='cardinal'` → `method='direction'` (plus clair)
- **Impact** : API plus intuitive et flexible pour les modelers

### 26/12/2024 - Protection race conditions Qt
- **Contexte** : Race conditions lors de clics rapides sur nextTurn causant RuntimeError
- **Décision prise** : Ajouter `try/except RuntimeError` dans SGAgentView.getPositionInEntity()
- **Impact** : Protection contre les crashes lors d'opérations concurrentes

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

### 26/12/2024 - SGGameSpaceSizeManager pour centraliser la gestion de taille
- **Convention** : Utiliser `SGGameSpaceSizeManager` pour centraliser la logique de sizing des gameSpaces
- **Exemples** : `calculate_content_width()`, `calculate_content_height()`, `adjust_game_space_to_content()`
- **Avantage** : Centralisation de la logique, réutilisabilité, séparation des responsabilités

### 26/12/2024 - Sizing dynamique basé sur layout.sizeHint()
- **Convention** : Prioriser `layout.sizeHint()` pour le sizing automatique avec fallback sur calcul manuel
- **Exemples** : `getSizeXGlobal()` et `getSizeYGlobal()` utilisent `sizeHint()` en premier
- **Avantage** : Sizing adaptatif au contenu réel, respect des contraintes Qt

### 26/12/2024 - Priorité des tailles manuelles sur sizing automatique
- **Convention** : Respecter les tailles manuelles (`sizeX`/`sizeY`) avec priorité sur sizing automatique
- **Exemples** : `if self.sizeX: return self.sizeX` avant `return self.calculateContentWidth()`
- **Avantage** : Flexibilité pour les modelers, sizing automatique par défaut

### 26/12/2024 - Word wrapping dynamique basé sur longueur de texte
- **Convention** : Utiliser des seuils de longueur pour activer/désactiver le word wrapping
- **Exemples** : `setWordWrap(len(text) > 50)` dans SGEndGameCondition
- **Avantage** : Interface adaptée au contenu, sizing optimal

### 26/12/2024 - Centralisation méthodes legacy UI
- **Convention** : Centraliser toutes les méthodes legacy UI dans SGEntity pour éviter la duplication
- **Exemples** : show(), hide(), update(), move(), setGeometry(), resize(), etc. dans SGEntity
- **Avantage** : Code plus maintenable, héritage cohérent, suppression de la duplication

### 26/12/2024 - Méthodes utilitaires SGExtensions
- **Convention** : Utiliser SGExtensions.py pour les méthodes utilitaires communes
- **Exemples** : execute_callable_with_entity(), normalize_species_name()
- **Avantage** : Code réutilisable, gestion dynamique des arguments, normalisation des noms

### 26/12/2024 - Documentation PowerShell vs Bash
- **Convention** : Documenter explicitement les différences PowerShell vs Bash pour les chatbots
- **Exemples** : PowerShell ne supporte pas &&, utiliser des commandes séparées
- **Avantage** : Évite les erreurs courantes pour les futurs chatbots

### 26/12/2024 - Exemples pédagogiques
- **Convention** : Créer des exemples complets et testés pour chaque fonctionnalité
- **Exemples** : ex_move_1.py (moveTo), ex_move_2.py (moveAgent), ex_move_3.py (numberOfMovement)
- **Avantage** : Documentation pratique pour les modelers, exemples fiables

### 26/12/2024 - Standardisation IDs numériques
- **Convention** : Utiliser des IDs numériques partout pour cohérence
- **Exemples** : `SGCell.getId()` retourne `x + (grid.columns * (y - 1))`
- **Avantage** : Cohérence entre `getId()` et `cellIdFromCoords()`, élimination des incohérences

### 26/12/2024 - API moveAgent unifiée
- **Convention** : Utiliser `target` pour tous les types de mouvement (ID/coords/direction)
- **Exemples** : `moveAgent(target=5)`, `moveAgent(target=(2,3))`, `moveAgent(target="up")`
- **Avantage** : API plus intuitive et flexible

### 26/12/2024 - Protection race conditions Qt
- **Convention** : Utiliser `try/except RuntimeError` pour les opérations sur vues Qt supprimées
- **Exemples** : `try: self.move(x,y) except RuntimeError: pass`
- **Avantage** : Protection contre les crashes lors d'opérations concurrentes

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

### 26/12/2024 - Refactoring drag & drop des gameSpaces (MAJOR)
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Refactoring complet du système de drag & drop des gameSpaces, passage de QDrag à mouvement direct de la souris, corrections SGControlPanel et SGGrid
- **Résultats** : 
  - Abandon complet du système QDrag au profit d'un mouvement direct basé sur global mouse position
  - Implémentation du comportement hotspot intuitif (point cliqué reste sous curseur)
  - Refactoring SGControlPanel pour utiliser constructeur __init__ standard
  - Correction SGControlPanel.mousePressEvent pour appeler super().mousePressEvent()
  - Mise à jour SGPlayer pour utiliser nouveau constructeur SGControlPanel
  - Correction SGGrid.mouseMoveEvent pour déléguer à super() quand isDraggable
  - Ajout orientation verticale/horizontale dans SGUserSelector
  - Réduction hauteur SGUserSelector (padding réduit, min_height 25px)
  - Création exemple syntax_examples pour démonstration orientation
- **Fichiers modifiés** : `SGGameSpace.py`, `SGControlPanel.py`, `SGPlayer.py`, `SGGrid.py`, `SGUserSelector.py`, `SGModel.py`, `ex_userSelector_orientation.py` (nouveau), `FUTURE_PLAN.md`
- **Durée** : Session complète de développement
- **Commits** : Multiple commits avec push sur refactor/model-view-separation

### 26/12/2024 - Gestion de taille des gameSpaces + SGGameSpaceSizeManager (MAJOR)
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Implémentation d'un système de gestion de taille adaptative pour les gameSpaces, création de SGGameSpaceSizeManager, et corrections des problèmes de sizing
- **Résultats** : 
  - Création de `SGGameSpaceSizeManager` pour centraliser la logique de sizing
  - Intégration dans `SGGameSpace` avec méthodes utilitaires
  - Refactoring `SGTextBox` pour sizing dynamique basé sur `layout.sizeHint()`
  - Refactoring `SGEndGameRule` pour sizing adaptatif des conditions
  - Remplacement `QTextEdit` par `QLabel` dans `SGEndGameCondition` avec word wrapping dynamique
  - Réduction hauteur `SGUserSelector` (50px → 25px + padding réduit)
  - Amélioration factory method `newTextBox` avec paramètres complets
  - Respect des tailles manuelles (`sizeX`/`sizeY`) avec priorité sur sizing automatique
  - Correction débordement widgets internes dans `SGTextBox`
  - Élimination des tailles disproportionnées dans `SGEndGameCondition`
- **Fichiers modifiés** : `SGGameSpaceSizeManager.py` (nouveau), `SGGameSpace.py`, `SGTextBox.py`, `SGEndGameRule.py`, `SGEndGameCondition.py`, `SGUserSelector.py`, `SGModel.py`, `FUTURE_PLAN.md`
- **Durée** : Session complète de développement
- **Commits** : Multiple commits avec push sur refactor/model-view-separation

### 26/12/2024 - Refactoring Model-View + améliorations méthodes de déplacement (MAJOR)
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Refactoring complet de l'architecture Model-View, amélioration des méthodes de déplacement, création d'exemples, et mise à jour de la documentation
- **Résultats** : 
  - Architecture Model-View refactorisée avec centralisation des méthodes legacy UI
  - Méthodes de déplacement améliorées (moveTo vs moveAgent, numberOfMovement)
  - Correction des patterns hexagonal selon référence Even-r offset
  - Création d'exemples complets : ex_move_1.py, ex_move_2.py, ex_move_3.py
  - Ajout de méthodes utilitaires dans SGExtensions.py
  - Documentation PowerShell vs Bash dans CONTEXT_SGE_FOR_CHATBOT.md
  - Mise à jour complète de la documentation (README_developer.md, README_modeler.md)
- **Fichiers modifiés** : SGEntity.py, SGAgent.py, SGCell.py, SGExtensions.py, SGModelAction.py, SGActivate.py, SGEntityDef.py, examples/, tests/, documentation/
- **Durée** : Session complète de développement
- **Commits** : Multiple commits avec push sur refactor/model-view-separation

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
- 26/12/2024 : Refactoring drag & drop des gameSpaces (SGGameSpace.py, SGControlPanel.py, SGPlayer.py, SGGrid.py, SGUserSelector.py, SGModel.py, ex_userSelector_orientation.py)
- 26/12/2024 : Gestion de taille des gameSpaces + SGGameSpaceSizeManager (SGGameSpaceSizeManager.py nouveau, SGGameSpace.py, SGTextBox.py, SGEndGameRule.py, SGEndGameCondition.py, SGUserSelector.py, SGModel.py)
- 26/12/2024 : Correction bugs hexagonal + améliorations API (SGCell.py, SGAgent.py, SGEntityDef.py, tests/)
- 26/12/2024 : Protection race conditions Qt (SGAgentView.py)
- 26/12/2024 : Tests voisinage hexagonal et carré complets (tests/)
- 26/12/2024 : Documentation README_modeler.md mise à jour
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
- 26/12/2024 : Le système QDrag est inadapté pour le drag & drop intuitif des gameSpaces, le mouvement direct basé sur global mouse position est plus efficace
- 26/12/2024 : Le comportement hotspot intuitif (point cliqué reste sous curseur) nécessite un calcul précis avec drag_start_position
- 26/12/2024 : SGControlPanel nécessite un refactoring vers constructeur __init__ standard pour compatibilité drag & drop
- 26/12/2024 : SGGrid.mouseMoveEvent doit déléguer à super() quand isDraggable pour utiliser le nouveau système
- 26/12/2024 : SGUserSelector bénéficie d'une orientation verticale/horizontale avec sizing adaptatif
- 26/12/2024 : Le système de sizing adaptatif nécessite une classe dédiée `SGGameSpaceSizeManager` pour centraliser la logique
- 26/12/2024 : L'utilisation de `layout.sizeHint()` est plus fiable que le calcul manuel pour le sizing automatique
- 26/12/2024 : Le remplacement de `QTextEdit` par `QLabel` améliore significativement les performances et le sizing
- 26/12/2024 : La priorité des tailles manuelles sur sizing automatique offre la flexibilité nécessaire aux modelers
- 26/12/2024 : Le word wrapping dynamique basé sur la longueur du texte optimise l'affichage
- 26/12/2024 : Les patterns de voisinage hexagonal "Pointy-top hex grid with even-r offset" nécessitent des corrections spécifiques
- 26/12/2024 : La standardisation des IDs numériques élimine les incohérences entre méthodes
- 26/12/2024 : L'API moveAgent unifiée avec `target` améliore significativement l'ergonomie
- 26/12/2024 : L'auto-détection de méthode basée sur le type de `target` simplifie l'API
- 26/12/2024 : La protection `try/except RuntimeError` est essentielle pour les opérations Qt concurrentes
- 26/12/2024 : Les tests de voisinage hexagonal/carré révèlent des patterns géométriques complexes
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
- Comment optimiser la performance du drag & drop direct pour de gros volumes de gameSpaces ?
- Faut-il étendre le système de drag & drop à d'autres types de widgets SGE ?
- Comment gérer la migration des gameSpaces existants vers le nouveau système de drag & drop ?
- Faut-il créer d'autres exemples pour les nouvelles fonctionnalités de drag & drop ?
- Comment optimiser la performance du sizing adaptatif avec SGGameSpaceSizeManager ?
- Faut-il étendre SGGameSpaceSizeManager à d'autres types de widgets ?
- Comment gérer la migration des gameSpaces existants vers le nouveau système de sizing ?
- Faut-il créer d'autres exemples pour les nouvelles fonctionnalités de sizing ?
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
