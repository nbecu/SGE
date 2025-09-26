# DEV_NOTES.md
# Suivi de développement SGE

## Objectif
Ce fichier documente l'état actuel du développement SGE, les problèmes en cours, les solutions trouvées et les prochaines étapes. Il sert de journal de bord pour maintenir la continuité entre les sessions de travail et les différents ordinateurs.

---

## État actuel du développement

### Date de dernière mise à jour : Décembre 2024
### Dernier chat utilisé : Claude Sonnet 4 (Cursor)
### Ordinateur de travail : Windows 10 (nbecu)
### Branche actuelle : renaming-classes
### Dernier chantier : Renommage SGEntityDef → SGEntityType

---

## Travail en cours

### Décembre 2024 - Renommage SGEntityDef → SGEntityType (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Renommage complet des classes et attributs pour améliorer la lisibilité et l'intuitivité du code SGE
- **Fichiers concernés** : 
  - `mainClasses/SGEntityType.py` (classes renommées : SGEntityType, SGCellType, SGAgentType)
  - `mainClasses/SGEntity.py` (attribut classDef → type)
  - `mainClasses/SGCell.py` (attribut classDef → type)
  - `mainClasses/SGAgent.py` (attribut classDef → type)
  - `mainClasses/AttributeAndValueFunctionalities.py` (classDef → type)
  - `mainClasses/SGLegendItem.py` (classDef → typeDef, entityType() → category())
  - `mainClasses/SGFormatDataHistory.py` (classDef.entityName → type.name)
  - `mainClasses/SGPlayer.py` (targetEntDef → targetType)
  - `mainClasses/SGControlPanel.py` (targetEntDef → targetType)
  - `tests/` (tous les fichiers de test mis à jour)
  - `examples/A_to_Z_examples/exStep3_2.py` (newAgentSpecies → newAgentType)
- **Problèmes rencontrés** : 
  - Chaîne de création des LegendItems dans ControlPanels cassée
  - Références incohérentes entre classes d'actions et ControlPanels
- **Solutions appliquées** : 
  - Renommage systématique de tous les attributs et méthodes
  - Correction des références dans SGPlayer.getAllGameActionsOn() et SGControlPanel.initUI_withGameActions()
  - Mise à jour de tous les imports et références dans le codebase
  - Tests complets avec exemples fonctionnels
- **Résultat** : Code plus lisible et intuitif, toutes les fonctionnalités préservées, LegendItems des ControlPanels fonctionnels

### Septembre 2025 - Système de sauvegarde/chargement des configurations Enhanced Grid Layout (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Implémentation complète d'un système de persistance des configurations Enhanced Grid Layout permettant aux modelers de sauvegarder et recharger leurs layouts entre sessions
- **Fichiers concernés** : 
  - `mainClasses/layout/SGLayoutConfigManager.py` (nouveau - gestionnaire centralisé des configurations)
  - `mainClasses/layout/SGLayoutConfigSaveDialog.py` (nouveau - dialogue de sauvegarde)
  - `mainClasses/layout/SGLayoutConfigManagerDialog.py` (nouveau - dialogue de gestion)
  - `mainClasses/layout/SGLayoutOrderTableDialog.py` (extension - gestion des types de position)
  - `mainClasses/layout/SGEnhancedGridLayout.py` (méthodes exportConfiguration/importConfiguration)
  - `mainClasses/SGGameSpace.py` (attribut _positionType, méthodes de gestion d'état)
  - `mainClasses/SGModel.py` (API modeler, intégration UI, menu Settings)
  - `README_modeler.md` (section Enhanced Grid Layout Configuration)
  - `CONTEXT_SGE_FOR_CHATBOT.md` (section 14.8 Enhanced Grid Layout)
- **Problèmes rencontrés** : Gestion des types de position (absolute/mixed/layoutOrder), persistance des états, optimisation des performances, interface utilisateur complexe
- **Solutions appliquées** : 
  - Introduction de l'attribut `_positionType` explicite dans SGGameSpace
  - Méthodes `setToAbsolute()`, `setToLayoutOrder()`, `setToMixed()` pour gestion d'état
  - Système de cache `gameSpaces_cache` pour optimisations O(1) dans SGLayoutOrderTableDialog
  - Renommage `absolute_position` → `manual_position` dans JSON pour cohérence sémantique
  - Filtrage des configurations par `model_name` pour isolation entre modèles
  - Gestion automatique du passage "layoutOrder" → "mixed" lors du drag manuel
  - Restauration intelligente des `layoutOrder` originaux pour les gameSpaces "mixed"
  - Nettoyage complet des prints debug et méthodes obsolètes
  - Documentation minimale et ciblée
- **Résultat** : Système complet de persistance des configurations Enhanced Grid Layout avec API modeler intuitive, interface utilisateur robuste, et optimisations de performance

### Septembre 2025 - Intégration Enhanced Grid Layout pour les gameSpaces (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Intégration complète du système Enhanced Grid Layout (EGL) dans SGE pour organisation flexible des gameSpaces avec colonnes décalées, système layoutOrder, et interface utilisateur de gestion
- **Fichiers concernés** : 
  - `mainClasses/layout/SGEnhancedGridLayout.py` (nouveau - classe principale EGL)
  - `mainClasses/layout/SGLayoutOrderTableDialog.py` (nouveau - interface gestion layoutOrder)
  - `mainClasses/layout/SGAbstractLayout.py` (méthode applyLayout abstraite)
  - `mainClasses/layout/SGVerticalLayout.py` (implémentation applyLayout)
  - `mainClasses/layout/SGHorizontalLayout.py` (implémentation applyLayout)
  - `mainClasses/layout/SGGridLayout.py` (implémentation applyLayout)
  - `mainClasses/SGGameSpace.py` (système layoutOrder, tooltips, positionnement manuel)
  - `mainClasses/SGModel.py` (intégration EGL, menu Enhanced Grid Layout, polymorphisme)
  - `examples/syntax_examples/ex_enhanced_grid_layout_1.py` (exemple test EGL)
  - `README_developer.md` (section Layout Management)
  - `README_modeler.md` (section Layout Options)
  - `FUTURE_PLAN.md` (chantier terminé)
  - `CONTEXT_SGE_FOR_CHATBOT.md` (section 14.8 Enhanced Grid Layout)
- **Problèmes rencontrés** : Architecture non polymorphique, conflits layoutOrder, interface utilisateur complexe, terminologie confuse (pID vs layoutOrder, EGL vs Enhanced Grid Layout)
- **Solutions appliquées** : 
  - Refactoring polymorphique avec méthode applyLayout() dans SGAbstractLayout
  - Système layoutOrder avec validation globale et réorganisation séquentielle
  - Interface utilisateur simplifiée avec tableau éditable et menu cohérent
  - Renommage systématique pID → layoutOrder, EGL → Enhanced Grid Layout
  - Support positionnement manuel avec layoutOrder="manual_position"
  - Tooltips intelligents avec priorité SGEntity
  - Nettoyage complet des méthodes inutilisées et prints debug
  - Documentation mise à jour avec approche minimale
- **Résultat** : Système Enhanced Grid Layout complet et intégré, architecture polymorphique améliorée, interface utilisateur intuitive, documentation à jour

### Septembre 2025 - Fonctionnalité de zoom pour les grilles (TERMINÉ)
- **Statut** : ✅ Terminé et validé
- **Description** : Implémentation complète de la fonctionnalité de zoom avec molette de souris pour les grilles SGE, support des grilles carrées et hexagonales avec agents
- **Fichiers concernés** : 
  - `mainClasses/SGGrid.py` (zoomIn/zoomOut, wheelEvent, updateGridSize, gestion zoom indépendant)
  - `mainClasses/SGCellView.py` (calculatePosition, correction calcul hexagonal, gestion taille dynamique)
  - `mainClasses/SGAgentView.py` (getPositionInEntity, recréation des vues, positionnement précis)
  - `mainClasses/SGAgent.py` (updateZoom, gestion taille agents)
  - `examples/syntax_examples/ex_zoom_1.py` (grille carrée simple avec agents)
  - `examples/syntax_examples/ex_zoom_2.py` (multi-grilles carrée + hexagonale)
  - `examples/syntax_examples/ex_zoom_3.py` (agents avec toutes positions possibles)
  - `FUTURE_PLAN.md` (ajout chantier terminé)
  - `README_developer.md` (section zoom functionality)
  - `CONTEXT_SGE_FOR_CHATBOT.md` (section 14.7 zoom functionality)
- **Problèmes rencontrés** : Positionnement incorrect des agents lors du zoom, calculs hexagonaux erronés, timing des mises à jour Qt
- **Solutions appliquées** : 
  - Stratégie de recréation des AgentView pour maintenir les positions
  - Correction calcul positionnement hexagonal (facteur 0.75 avec gap)
  - Gestion explicite du timing Qt avec move() forcé des cellules
  - Zoom indépendant par grille avec gestion des niveaux
  - Nettoyage complet des prints de debug
  - Exemples organisés par complexité (ex_zoom_1 à ex_zoom_3)
- **Résultat** : Fonctionnalité de zoom complète et robuste pour tous types de grilles avec agents, documentation mise à jour

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

### Fonctionnalité de zoom - TERMINÉ ✅
La fonctionnalité de zoom est **complètement terminée** et validée :
- [x] Implémentation zoom avec molette de souris sur SGGrid
- [x] Support grilles carrées et hexagonales
- [x] Zoom indépendant par grille
- [x] Positionnement correct des agents pendant le zoom
- [x] Stratégie de recréation des AgentView pour maintenir les positions
- [x] Correction calculs positionnement hexagonal
- [x] Gestion timing Qt avec move() forcé des cellules
- [x] Nettoyage complet des prints de debug
- [x] Exemples organisés par complexité (ex_zoom_1.py à ex_zoom_3.py)
- [x] Documentation mise à jour (FUTURE_PLAN.md, README_developer.md, CONTEXT_SGE_FOR_CHATBOT.md)
- [x] Tests validés avec tous types de grilles et agents

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

### Enhanced Grid Layout - TERMINÉ ✅
Le système Enhanced Grid Layout est **complètement terminé** et validé :
- [x] Intégration complète du système Enhanced Grid Layout dans SGE
- [x] Création de SGEnhancedGridLayout héritant de SGAbstractLayout
- [x] Ajout de "enhanced_grid" comme option typeOfLayout dans SGModel
- [x] Système layoutOrder pour contrôle utilisateur de l'ordre des gameSpaces
- [x] Interface utilisateur complète avec tableau éditable et menu Settings
- [x] Support du positionnement manuel avec moveToCoords() override
- [x] Tooltips intelligents avec priorité SGEntity
- [x] Refactoring polymorphique avec méthode applyLayout() dans tous les layouts
- [x] Renommage systématique pID → layoutOrder, EGL → Enhanced Grid Layout
- [x] Nettoyage complet des méthodes inutilisées et prints debug
- [x] Documentation mise à jour (README_developer.md, README_modeler.md, FUTURE_PLAN.md, CONTEXT_SGE_FOR_CHATBOT.md)
- [x] Tests validés avec ex_enhanced_grid_layout_1.py

### Système de sauvegarde/chargement des configurations Enhanced Grid Layout - TERMINÉ ✅
Le système de persistance des configurations Enhanced Grid Layout est **complètement terminé** et validé :
- [x] Création de SGLayoutConfigManager pour gestion centralisée des configurations JSON
- [x] Implémentation des dialogues SGLayoutConfigSaveDialog et SGLayoutConfigManagerDialog
- [x] Extension de SGLayoutOrderTableDialog pour gestion des types de position
- [x] Méthodes exportConfiguration/importConfiguration dans SGEnhancedGridLayout
- [x] Introduction de l'attribut _positionType explicite dans SGGameSpace
- [x] API modeler complète (saveLayoutConfig, loadLayoutConfig, getAvailableLayoutConfigs)
- [x] Gestion automatique des transitions entre types de position (layoutOrder → mixed → absolute)
- [x] Optimisations de performance avec cache gameSpaces_cache pour lookups O(1)
- [x] Filtrage des configurations par model_name pour isolation entre modèles
- [x] Renommage absolute_position → manual_position pour cohérence sémantique
- [x] Nettoyage complet des prints debug et méthodes obsolètes
- [x] Documentation mise à jour (README_modeler.md, CONTEXT_SGE_FOR_CHATBOT.md)
- [x] Tests validés avec exemples multiples et modèles complexes (CarbonPolis.py)

### Prochaines étapes générales
- [ ] Nouvelles fonctionnalités SGE (selon besoins futurs)
- [ ] Optimisations performance (si nécessaire)
- [ ] Améliorations UI/UX (selon retours utilisateurs)
- [ ] Documentation modeler (si nouveaux besoins)
- [ ] Extension SGGameSpaceSizeManager à d'autres types de widgets
- [ ] Optimisation performance du sizing adaptatif

---

## Problèmes résolus

### Septembre 2025 - Système de sauvegarde/chargement des configurations Enhanced Grid Layout (MAJOR)
- **Description** : Implémentation complète d'un système de persistance des configurations Enhanced Grid Layout avec gestion des types de position, optimisations de performance, et interface utilisateur robuste
- **Solution** : 
  1. Création de SGLayoutConfigManager pour gestion centralisée des configurations JSON
  2. Implémentation des dialogues SGLayoutConfigSaveDialog et SGLayoutConfigManagerDialog
  3. Extension de SGLayoutOrderTableDialog pour gestion des types de position (absolute/mixed/layoutOrder)
  4. Introduction de l'attribut _positionType explicite dans SGGameSpace avec méthodes de gestion d'état
  5. Méthodes exportConfiguration/importConfiguration dans SGEnhancedGridLayout
  6. API modeler complète (saveLayoutConfig, loadLayoutConfig, getAvailableLayoutConfigs)
  7. Gestion automatique des transitions entre types de position (layoutOrder → mixed lors du drag)
  8. Optimisations de performance avec cache gameSpaces_cache pour lookups O(1)
  9. Filtrage des configurations par model_name pour isolation entre modèles
  10. Renommage absolute_position → manual_position pour cohérence sémantique
  11. Nettoyage complet des prints debug et méthodes obsolètes
  12. Documentation mise à jour avec approche minimale (README_modeler.md, CONTEXT_SGE_FOR_CHATBOT.md)
- **Fichiers modifiés** : `SGLayoutConfigManager.py` (nouveau), `SGLayoutConfigSaveDialog.py` (nouveau), `SGLayoutConfigManagerDialog.py` (nouveau), `SGLayoutOrderTableDialog.py`, `SGEnhancedGridLayout.py`, `SGGameSpace.py`, `SGModel.py`, `README_modeler.md`, `CONTEXT_SGE_FOR_CHATBOT.md`
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Impact** : Système complet de persistance des configurations Enhanced Grid Layout avec API modeler intuitive, interface utilisateur robuste, et optimisations de performance

### Septembre 2025 - Intégration Enhanced Grid Layout pour les gameSpaces (MAJOR)
- **Description** : Intégration complète du système Enhanced Grid Layout dans SGE avec architecture polymorphique, système layoutOrder, et interface utilisateur
- **Solution** : 
  1. Création de SGEnhancedGridLayout héritant de SGAbstractLayout
  2. Ajout de "enhanced_grid" comme option typeOfLayout dans SGModel
  3. Implémentation du système layoutOrder avec validation globale et réorganisation séquentielle
  4. Création de SGLayoutOrderTableDialog pour interface utilisateur de gestion
  5. Refactoring polymorphique avec méthode applyLayout() dans tous les layouts
  6. Support du positionnement manuel avec layoutOrder="manual_position"
  7. Tooltips intelligents avec priorité SGEntity et affichage layoutOrder
  8. Renommage systématique pID → layoutOrder, EGL → Enhanced Grid Layout
  9. Nettoyage complet des méthodes inutilisées et prints debug
  10. Documentation mise à jour avec approche minimale (README_developer.md, README_modeler.md, FUTURE_PLAN.md, CONTEXT_SGE_FOR_CHATBOT.md)
- **Fichiers modifiés** : `SGEnhancedGridLayout.py` (nouveau), `SGLayoutOrderTableDialog.py` (nouveau), `SGAbstractLayout.py`, `SGVerticalLayout.py`, `SGHorizontalLayout.py`, `SGGridLayout.py`, `SGGameSpace.py`, `SGModel.py`, `ex_enhanced_grid_layout_1.py`, documentation complète
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Impact** : Système Enhanced Grid Layout complet et intégré, architecture polymorphique améliorée, interface utilisateur intuitive, documentation à jour

### Septembre 2025 - Fonctionnalité de zoom pour les grilles (MAJOR)
- **Description** : Implémentation complète de la fonctionnalité de zoom avec molette de souris pour les grilles SGE
- **Solution** : 
  1. Ajout wheelEvent() dans SGGrid pour détecter molette de souris
  2. Implémentation zoomIn()/zoomOut() avec gestion niveaux indépendants
  3. Stratégie de recréation des AgentView pour maintenir positions pendant zoom
  4. Correction calculs positionnement hexagonal (facteur 0.75 avec gap)
  5. Gestion explicite timing Qt avec move() forcé des cellules
  6. Méthode updateGridSize() pour synchroniser cellules et agents
  7. Support grilles carrées et hexagonales avec agents
  8. Nettoyage complet des prints de debug
  9. Création exemples organisés par complexité (ex_zoom_1.py à ex_zoom_3.py)
  10. Mise à jour documentation complète (FUTURE_PLAN.md, README_developer.md, CONTEXT_SGE_FOR_CHATBOT.md)
- **Fichiers modifiés** : `SGGrid.py`, `SGCellView.py`, `SGAgentView.py`, `SGAgent.py`, `ex_zoom_1.py`, `ex_zoom_2.py`, `ex_zoom_3.py`, `FUTURE_PLAN.md`, `README_developer.md`, `CONTEXT_SGE_FOR_CHATBOT.md`
- **Chat utilisé** : Claude Sonnet 4 (Cursor)
- **Impact** : Fonctionnalité de zoom complète et robuste pour tous types de grilles avec agents, documentation mise à jour

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

### Septembre 2025 - Système de persistance des configurations Enhanced Grid Layout
- **Contexte** : Besoin de permettre aux modelers de sauvegarder et recharger leurs configurations Enhanced Grid Layout entre sessions
- **Décision prise** : Implémenter un système complet de persistance avec JSON, gestion des types de position, et API modeler intuitive
- **Impact** : 
  - Persistance des configurations entre sessions
  - API modeler simple (saveLayoutConfig, loadLayoutConfig, getAvailableLayoutConfigs)
  - Gestion robuste des types de position (absolute/mixed/layoutOrder)
  - Optimisations de performance avec cache pour lookups O(1)
  - Isolation des configurations par modèle
  - Interface utilisateur complète avec dialogues de gestion

### Septembre 2025 - Attribut _positionType explicite dans SGGameSpace
- **Contexte** : Confusion dans la gestion des types de position avec détection dynamique complexe
- **Décision prise** : Introduire un attribut _positionType explicite avec méthodes de gestion d'état
- **Impact** : 
  - État explicite et cohérent des gameSpaces
  - Méthodes setToAbsolute(), setToLayoutOrder(), setToMixed() pour gestion d'état
  - Transitions automatiques (layoutOrder → mixed lors du drag)
  - Restauration intelligente des layoutOrder originaux
  - Élimination de la détection dynamique complexe

### Septembre 2025 - Optimisations de performance avec cache gameSpaces_cache
- **Contexte** : Recherches linéaires répétées dans SGLayoutOrderTableDialog causant des problèmes de performance
- **Décision prise** : Implémenter un cache gameSpaces_cache pour les lookups O(1)
- **Impact** : 
  - Amélioration significative des performances (lookups O(n) → O(1))
  - Réduction des itérations répétées sur self.model.gameSpaces.values()
  - Cache initialisé une seule fois dans __init__
  - Optimisation de toutes les méthodes critiques (accept, validateLayoutOrderChanges, etc.)

### Septembre 2025 - Renommage absolute_position → manual_position
- **Contexte** : Terme "absolute_position" utilisé pour les types "absolute" et "mixed", créant une confusion sémantique
- **Décision prise** : Renommer en "manual_position" pour refléter l'usage réel (positionnement manuel)
- **Impact** : 
  - Cohérence sémantique dans les fichiers JSON
  - Clarification de l'usage (positionnement manuel vs automatique)
  - Support de la rétrocompatibilité avec fallback sur "absolute_position"
  - Documentation plus claire et intuitive

### Septembre 2025 - Architecture polymorphique pour les layouts
- **Contexte** : Architecture non polymorphique avec logique conditionnelle dans SGModel.applyAutomaticLayout()
- **Décision prise** : Refactoring polymorphique avec méthode applyLayout() dans SGAbstractLayout et ses sous-classes
- **Impact** : 
  - Architecture plus propre et extensible
  - Délégation de la logique de layout aux classes spécialisées
  - Facilité d'ajout de nouveaux types de layouts
  - Code plus maintenable et testable

### Septembre 2025 - Système layoutOrder pour contrôle utilisateur
- **Contexte** : Besoin de permettre aux utilisateurs de contrôler l'ordre des gameSpaces dans Enhanced Grid Layout
- **Décision prise** : Implémenter un système layoutOrder avec validation globale et réorganisation séquentielle
- **Impact** : 
  - Contrôle utilisateur de l'ordre des gameSpaces
  - Validation robuste des conflits de layoutOrder
  - Réorganisation automatique pour éliminer les trous
  - Interface utilisateur intuitive avec tableau éditable

### Septembre 2025 - Support positionnement manuel avec layoutOrder="manual_position"
- **Contexte** : Besoin de distinguer les gameSpaces positionnés manuellement par le modeler
- **Décision prise** : Utiliser layoutOrder="manual_position" pour les gameSpaces avec moveToCoords()
- **Impact** : 
  - Séparation claire entre positionnement automatique et manuel
  - Respect des choix du modeler
  - Tooltips informatifs ("Position set manually")
  - Exclusion des gameSpaces manuels de la gestion automatique

### Septembre 2025 - Renommage systématique pID → layoutOrder
- **Contexte** : Terminologie confuse avec "pID" peu compréhensible
- **Décision prise** : Renommage systématique pID → layoutOrder dans tout le code et la documentation
- **Impact** : 
  - Terminologie plus claire et intuitive
  - Code plus lisible et maintenable
  - Documentation cohérente
  - Interface utilisateur compréhensible

### Septembre 2025 - Renommage EGL → Enhanced Grid Layout
- **Contexte** : Acronyme EGL peu compréhensible pour les développeurs
- **Décision prise** : Utiliser "Enhanced Grid Layout" pour les éléments publics et "Enhanced Grid" pour les éléments privés
- **Impact** : 
  - Documentation plus accessible
  - Code plus compréhensible
  - Interface utilisateur claire
  - Facilité de maintenance

### Septembre 2025 - Stratégie de recréation des AgentView pour le zoom
- **Contexte** : Positionnement incorrect des agents lors du zoom, problème de timing entre mises à jour des cellules et agents
- **Décision prise** : Implémenter une stratégie de recréation complète des AgentView pendant le zoom
- **Impact** : 
  - Destruction et recréation des AgentView pour garantir positionnement correct
  - Synchronisation parfaite entre positions des cellules et agents
  - Gestion explicite du timing Qt avec move() forcé des cellules
  - Maintien des positions relatives des agents (center, corners, random)

### Septembre 2025 - Correction calculs positionnement hexagonal
- **Contexte** : Erreur dans le calcul de positionnement vertical des cellules hexagonales
- **Décision prise** : Corriger le facteur 0.75 pour inclure le gap dans le calcul
- **Impact** : 
  - Calcul correct : `(grid_size + grid_gap) * 0.75` au lieu de `grid_size * 0.75`
  - Positionnement précis des cellules hexagonales
  - Agents correctement centrés dans les hexagones

### Septembre 2025 - Organisation des exemples par complexité
- **Contexte** : Besoin d'exemples pédagogiques pour la fonctionnalité de zoom
- **Décision prise** : Organiser les exemples du plus simple au plus complexe (ex_zoom_1.py à ex_zoom_3.py)
- **Impact** : 
  - ex_zoom_1.py : Grille carrée simple avec agents au centre
  - ex_zoom_2.py : Multi-grilles (carrée + hexagonale) avec agents
  - ex_zoom_3.py : Agents avec toutes les positions possibles
  - Progression pédagogique claire pour les utilisateurs

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
- **Décision prise** : Créer des méthodes utilitaires dans SGExtensions.py (execute_callable_with_entity, normalize_type_name)
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

### Septembre 2025 - Système de persistance des configurations Enhanced Grid Layout
- **Convention** : Utiliser JSON pour la persistance des configurations avec structure hiérarchique par modèle
- **Exemples** : `layout_config.json` avec clés "configurations" et filtrage par `model_name`
- **Avantage** : Persistance légère et lisible, isolation entre modèles, facilité de débogage

### Septembre 2025 - Attribut _positionType explicite pour gestion d'état
- **Convention** : Utiliser un attribut explicite _positionType avec méthodes de gestion d'état
- **Exemples** : `setToAbsolute()`, `setToLayoutOrder()`, `setToMixed()`, `getPositionType()`
- **Avantage** : État cohérent et prévisible, élimination de la détection dynamique complexe

### Septembre 2025 - Cache gameSpaces_cache pour optimisations O(1)
- **Convention** : Utiliser un cache initialisé une fois pour éviter les recherches linéaires répétées
- **Exemples** : `self.gameSpaces_cache = {gs.id: gs for gs in self.model.gameSpaces.values()}`
- **Avantage** : Amélioration significative des performances, réduction des itérations coûteuses

### Septembre 2025 - Renommage sémantique pour clarté
- **Convention** : Renommer les termes techniques pour refléter l'usage réel
- **Exemples** : `absolute_position` → `manual_position`, support rétrocompatibilité
- **Avantage** : Cohérence sémantique, documentation plus claire, interface intuitive

### Septembre 2025 - Architecture polymorphique pour les layouts
- **Convention** : Utiliser le polymorphisme pour l'application des layouts avec méthode applyLayout() dans SGAbstractLayout
- **Exemples** : `model.layoutOfModel.applyLayout(model.gameSpaces.values())`
- **Avantage** : Architecture extensible et maintenable, délégation de la logique aux classes spécialisées

### Septembre 2025 - Système layoutOrder pour contrôle utilisateur
- **Convention** : Utiliser layoutOrder pour contrôler l'ordre des gameSpaces dans Enhanced Grid Layout
- **Exemples** : `layoutOrder=1`, `layoutOrder="manual_position"`, validation globale des conflits
- **Avantage** : Contrôle utilisateur intuitif, validation robuste, réorganisation automatique

### Septembre 2025 - Support positionnement manuel avec layoutOrder="manual_position"
- **Convention** : Utiliser layoutOrder="manual_position" pour les gameSpaces positionnés manuellement
- **Exemples** : `moveToCoords()` → `layoutOrder="manual_position"`, tooltips informatifs
- **Avantage** : Séparation claire automatique/manuel, respect des choix du modeler

### Septembre 2025 - Renommage systématique pour clarté
- **Convention** : Renommer les termes techniques pour améliorer la compréhensibilité
- **Exemples** : pID → layoutOrder, EGL → Enhanced Grid Layout, "fixed_position" → "manual_position"
- **Avantage** : Code plus lisible, documentation accessible, interface utilisateur claire

### Septembre 2025 - Fonctionnalité de zoom avec molette de souris
- **Convention** : Utiliser wheelEvent() pour détecter les événements de molette de souris sur les grilles
- **Exemples** : `wheelEvent()`, `zoomIn()`, `zoomOut()`, `setZoomLevel()`, `resetZoom()`
- **Avantage** : Zoom intuitif et fluide pour les utilisateurs

### Septembre 2025 - Stratégie de recréation des AgentView
- **Convention** : Recréer complètement les AgentView lors du zoom pour garantir le positionnement correct
- **Exemples** : Destruction avec `setParent(None)` et `deleteLater()`, recréation avec `SGAgentView(agent, grid)`
- **Avantage** : Synchronisation parfaite entre cellules et agents, positionnement précis

### Septembre 2025 - Gestion timing Qt pour le zoom
- **Convention** : Forcer le déplacement des cellules avec `move()` avant de recréer les agents
- **Exemples** : `cell.view.move(cell.view.startX, cell.view.startY)` dans updateGridSize()
- **Avantage** : Évite les problèmes de timing entre mises à jour Qt

### Septembre 2025 - Calculs positionnement hexagonal
- **Convention** : Inclure le gap dans le facteur de calcul vertical hexagonal
- **Exemples** : `(grid_size + grid_gap) * 0.75` au lieu de `grid_size * 0.75`
- **Avantage** : Positionnement précis des cellules hexagonales

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
- **Exemples** : execute_callable_with_entity(), normalize_type_name()
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
- **Exemples** : `isAdmin`, `isAgentType`, `isCellType`, `isLegend`, `isControlPanel`
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

### Septembre 2025 - Système de sauvegarde/chargement des configurations Enhanced Grid Layout (MAJOR)
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Implémentation complète d'un système de persistance des configurations Enhanced Grid Layout avec gestion des types de position, optimisations de performance, et interface utilisateur robuste
- **Résultats** : 
  - Création de SGLayoutConfigManager pour gestion centralisée des configurations JSON
  - Implémentation des dialogues SGLayoutConfigSaveDialog et SGLayoutConfigManagerDialog
  - Extension de SGLayoutOrderTableDialog pour gestion des types de position (absolute/mixed/layoutOrder)
  - Introduction de l'attribut _positionType explicite dans SGGameSpace avec méthodes de gestion d'état
  - Méthodes exportConfiguration/importConfiguration dans SGEnhancedGridLayout
  - API modeler complète (saveLayoutConfig, loadLayoutConfig, getAvailableLayoutConfigs)
  - Gestion automatique des transitions entre types de position (layoutOrder → mixed lors du drag)
  - Optimisations de performance avec cache gameSpaces_cache pour lookups O(1)
  - Filtrage des configurations par model_name pour isolation entre modèles
  - Renommage absolute_position → manual_position pour cohérence sémantique
  - Nettoyage complet des prints debug et méthodes obsolètes
  - Documentation mise à jour avec approche minimale (README_modeler.md, CONTEXT_SGE_FOR_CHATBOT.md)
- **Fichiers modifiés** : `SGLayoutConfigManager.py` (nouveau), `SGLayoutConfigSaveDialog.py` (nouveau), `SGLayoutConfigManagerDialog.py` (nouveau), `SGLayoutOrderTableDialog.py`, `SGEnhancedGridLayout.py`, `SGGameSpace.py`, `SGModel.py`, `README_modeler.md`, `CONTEXT_SGE_FOR_CHATBOT.md`
- **Durée** : Session complète de développement
- **Commits** : Multiple commits avec push sur layout_export_import_for_release_sept_25

### Septembre 2025 - Intégration Enhanced Grid Layout pour les gameSpaces (MAJOR)
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Intégration complète du système Enhanced Grid Layout dans SGE avec architecture polymorphique, système layoutOrder, et interface utilisateur
- **Résultats** : 
  - Création de SGEnhancedGridLayout héritant de SGAbstractLayout
  - Ajout de "enhanced_grid" comme option typeOfLayout dans SGModel
  - Implémentation du système layoutOrder avec validation globale et réorganisation séquentielle
  - Création de SGLayoutOrderTableDialog pour interface utilisateur de gestion
  - Refactoring polymorphique avec méthode applyLayout() dans tous les layouts
  - Support du positionnement manuel avec layoutOrder="manual_position"
  - Tooltips intelligents avec priorité SGEntity et affichage layoutOrder
  - Renommage systématique pID → layoutOrder, EGL → Enhanced Grid Layout
  - Nettoyage complet des méthodes inutilisées et prints debug
  - Documentation mise à jour avec approche minimale (README_developer.md, README_modeler.md, FUTURE_PLAN.md, CONTEXT_SGE_FOR_CHATBOT.md)
- **Fichiers modifiés** : `SGEnhancedGridLayout.py` (nouveau), `SGLayoutOrderTableDialog.py` (nouveau), `SGAbstractLayout.py`, `SGVerticalLayout.py`, `SGHorizontalLayout.py`, `SGGridLayout.py`, `SGGameSpace.py`, `SGModel.py`, `ex_enhanced_grid_layout_1.py`, documentation complète
- **Durée** : Session complète de développement
- **Commits** : Multiple commits avec push sur enhanced_gameSpaces_grid_layout_for_candidate_sept_2025

### Septembre 2025 - Fonctionnalité de zoom pour les grilles (MAJOR)
- **Ordinateur** : Windows 10 (nbecu)
- **Sujet principal** : Implémentation complète de la fonctionnalité de zoom avec molette de souris pour les grilles SGE
- **Résultats** : 
  - Ajout wheelEvent() dans SGGrid pour détecter molette de souris
  - Implémentation zoomIn()/zoomOut() avec gestion niveaux indépendants
  - Stratégie de recréation des AgentView pour maintenir positions pendant zoom
  - Correction calculs positionnement hexagonal (facteur 0.75 avec gap)
  - Gestion explicite timing Qt avec move() forcé des cellules
  - Support grilles carrées et hexagonales avec agents
  - Nettoyage complet des prints de debug
  - Création exemples organisés par complexité (ex_zoom_1.py à ex_zoom_3.py)
  - Mise à jour documentation complète (FUTURE_PLAN.md, README_developer.md, CONTEXT_SGE_FOR_CHATBOT.md)
- **Fichiers modifiés** : `SGGrid.py`, `SGCellView.py`, `SGAgentView.py`, `SGAgent.py`, `ex_zoom_1.py`, `ex_zoom_2.py`, `ex_zoom_3.py`, `FUTURE_PLAN.md`, `README_developer.md`, `CONTEXT_SGE_FOR_CHATBOT.md`
- **Durée** : Session complète de développement
- **Commits** : Multiple commits avec push sur zoom_feature_for_candidate_sept_2025_v2

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
- Septembre 2025 : Système de sauvegarde/chargement des configurations Enhanced Grid Layout complet (SGLayoutConfigManager.py, SGLayoutConfigSaveDialog.py, SGLayoutConfigManagerDialog.py)
- Septembre 2025 : Attribut _positionType explicite dans SGGameSpace avec méthodes de gestion d'état (setToAbsolute, setToLayoutOrder, setToMixed)
- Septembre 2025 : Optimisations de performance avec cache gameSpaces_cache pour lookups O(1) dans SGLayoutOrderTableDialog
- Septembre 2025 : Renommage absolute_position → manual_position pour cohérence sémantique dans JSON
- Septembre 2025 : Filtrage des configurations par model_name pour isolation entre modèles
- Septembre 2025 : Gestion automatique des transitions entre types de position (layoutOrder → mixed lors du drag)
- Septembre 2025 : API modeler complète (saveLayoutConfig, loadLayoutConfig, getAvailableLayoutConfigs)
- Septembre 2025 : Extension SGLayoutOrderTableDialog pour gestion des types de position
- Septembre 2025 : Méthodes exportConfiguration/importConfiguration dans SGEnhancedGridLayout
- Septembre 2025 : Nettoyage complet des prints debug et méthodes obsolètes
- Septembre 2025 : Documentation mise à jour avec approche minimale (README_modeler.md, CONTEXT_SGE_FOR_CHATBOT.md)
- Septembre 2025 : Intégration Enhanced Grid Layout complète (SGEnhancedGridLayout.py, SGLayoutOrderTableDialog.py, polymorphisme layouts)
- Septembre 2025 : Système layoutOrder avec validation globale et réorganisation séquentielle
- Septembre 2025 : Support positionnement manuel avec layoutOrder="manual_position"
- Septembre 2025 : Renommage systématique pID → layoutOrder, EGL → Enhanced Grid Layout
- Septembre 2025 : Refactoring polymorphique avec méthode applyLayout() dans tous les layouts
- Septembre 2025 : Interface utilisateur complète avec tableau éditable et menu Settings
- Septembre 2025 : Tooltips intelligents avec priorité SGEntity et affichage layoutOrder
- Septembre 2025 : Documentation mise à jour avec approche minimale (README_developer.md, README_modeler.md, FUTURE_PLAN.md, CONTEXT_SGE_FOR_CHATBOT.md)
- Septembre 2025 : Fonctionnalité de zoom complète (SGGrid.py, SGCellView.py, SGAgentView.py, SGAgent.py, ex_zoom_1.py à ex_zoom_3.py)
- Septembre 2025 : Correction calculs positionnement hexagonal (facteur 0.75 avec gap)
- Septembre 2025 : Stratégie de recréation des AgentView pour zoom
- Septembre 2025 : Nettoyage complet des prints de debug
- Septembre 2025 : Documentation mise à jour (FUTURE_PLAN.md, README_developer.md, CONTEXT_SGE_FOR_CHATBOT.md)
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
- Septembre 2025 : Le système de persistance des configurations Enhanced Grid Layout nécessite une gestion explicite des types de position avec attribut _positionType
- Septembre 2025 : Les optimisations de performance avec cache gameSpaces_cache améliorent significativement les performances des interfaces complexes
- Septembre 2025 : Le renommage sémantique (absolute_position → manual_position) améliore la cohérence et la compréhensibilité du code
- Septembre 2025 : Le filtrage des configurations par model_name est essentiel pour l'isolation entre modèles
- Septembre 2025 : La gestion automatique des transitions entre types de position (layoutOrder → mixed) améliore l'expérience utilisateur
- Septembre 2025 : L'API modeler intuitive (saveLayoutConfig, loadLayoutConfig, getAvailableLayoutConfigs) facilite l'adoption
- Septembre 2025 : L'architecture polymorphique avec méthode applyLayout() améliore significativement la maintenabilité et l'extensibilité des layouts
- Septembre 2025 : Le système layoutOrder avec validation globale et réorganisation séquentielle offre un contrôle utilisateur robuste et intuitif
- Septembre 2025 : Le support du positionnement manuel avec layoutOrder="manual_position" permet une séparation claire entre automatique et manuel
- Septembre 2025 : Le renommage systématique des termes techniques (pID → layoutOrder, EGL → Enhanced Grid Layout) améliore la compréhensibilité du code
- Septembre 2025 : L'interface utilisateur avec tableau éditable et menu Settings offre une expérience utilisateur intuitive
- Septembre 2025 : Les tooltips intelligents avec priorité SGEntity et affichage layoutOrder améliorent l'expérience utilisateur
- Septembre 2025 : Le nettoyage complet des méthodes inutilisées et prints debug est essentiel pour la production
- Septembre 2025 : La documentation avec approche minimale est plus efficace que les ajouts détaillés
- Septembre 2025 : La stratégie de recréation des AgentView est nécessaire pour maintenir le positionnement correct pendant le zoom
- Septembre 2025 : Le timing Qt nécessite un déplacement forcé des cellules avec move() avant la recréation des agents
- Septembre 2025 : Les calculs hexagonaux nécessitent d'inclure le gap dans le facteur de calcul vertical (0.75)
- Septembre 2025 : L'organisation des exemples par complexité améliore l'expérience utilisateur
- Septembre 2025 : Le nettoyage des prints de debug est essentiel pour la production
- Septembre 2025 : La documentation doit être mise à jour simultanément avec le code
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
- Comment optimiser la performance du système de persistance pour de très grandes configurations ?
- Faut-il étendre le système de sauvegarde/chargement à d'autres types de layouts SGE ?
- Comment gérer la migration des configurations existantes vers le nouveau système ?
- Faut-il créer d'autres exemples pour les nouvelles fonctionnalités de persistance ?
- Comment optimiser la performance du cache gameSpaces_cache pour de gros volumes de gameSpaces ?
- Faut-il implémenter des raccourcis clavier pour la gestion des configurations ?
- Comment gérer les configurations avec des gameSpaces très complexes (multiples couches) ?
- Faut-il ajouter des indicateurs visuels du type de position des gameSpaces ?
- Comment optimiser la performance du zoom pour de très grandes grilles ?
- Faut-il étendre le système de zoom à d'autres types de widgets SGE ?
- Comment gérer la migration des grilles existantes vers le nouveau système de zoom ?
- Faut-il créer d'autres exemples pour les nouvelles fonctionnalités de zoom ?
- Comment optimiser la stratégie de recréation des AgentView pour de gros volumes d'agents ?
- Faut-il implémenter des raccourcis clavier pour le zoom ?
- Comment gérer le zoom avec des grilles très complexes (multiples couches) ?
- Faut-il ajouter des indicateurs visuels du niveau de zoom ?
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
