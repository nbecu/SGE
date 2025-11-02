# RÉCAPITULATIF DU CHANTIER GS_ASPECT_SYSTEM

**Date du récapitulatif** : Après 2 semaines de pause  
**Date de référence du fichier NEXT_STEPS** : 15/10/2025

---

## 📊 ÉTAT GLOBAL

### Système `gs_aspect` : Architecture de base ✅
- **SGAspect** : Classe centrale pour définir les styles (couleurs, polices, bordures, etc.)
- **SGGameSpace** : Classe mère de tous les GameSpaces avec méthodes modeler communes
- Tous les GameSpaces héritent maintenant de `SGGameSpace`
- Système de thèmes prédéfinis et personnalisés fonctionnel

---

## ✅ TRAVAIL TERMINÉ (dans les dernières sessions)

### 1. Migration SGLabel vers SGGameSpace ✅
**Fichier** : `mainClasses/SGLabel.py`

- ✅ `SGLabel` hérite maintenant de `SGGameSpace`
- ✅ Intégration au système `gs_aspect` pour le container (borders, background)
- ✅ Intégration au système `text1_aspect` pour le style du texte
- ✅ Méthode `onTextAspectsChanged()` implémentée pour appliquer les styles texte
- ✅ Méthode `paintEvent()` implémentée pour dessiner borders et background
- ✅ Support de l'alignement via `text1_aspect.alignment`
- ✅ Parsing rétrocompatible des anciennes spécifications CSS (`textStyle_specs`, `borderStyle_specs`, `backgroundColor_specs`)
- ✅ Getters robustes `getSizeXGlobal()` et `getSizeYGlobal()` avec fallback pour éviter les erreurs `NoneType`
- ✅ Intégration dans `SGModel.newLabel()` : ajout à `gameSpaces` et `layoutOfModel`
- ✅ Exemples testés : `ex_label_1.py`, `ex_label_2.py`, etc.

**Points clés** :
- L'alignement initial du modeler (via paramètre `alignement`) est préservé dans `text1_aspect.alignment`
- L'alignement via Custom Theme Editor fonctionne correctement (Preview + application)

---

### 2. Migration SGButton vers SGGameSpace ✅
**Fichier** : `mainClasses/SGButton.py`

- ✅ `SGButton` hérite maintenant de `SGGameSpace`
- ✅ Intégration au système `gs_aspect` pour container (borders, background, hover states)
- ✅ Intégration au système `text1_aspect` pour le style du texte
- ✅ Méthode `onTextAspectsChanged()` implémentée pour appliquer les styles texte
- ✅ Méthode `paintEvent()` implémentée pour dessiner le container avec états hover
- ✅ Support du word wrap via `QLabel` interne pour textes longs
- ✅ Support des états hover (background, border, text color)
- ✅ Support de `text_decoration` (underline, overline, line-through)
- ✅ Correction de la hauteur dynamique pour les boutons avec word wrap
- ✅ Intégration dans `SGModel.newButton()` : ajout à `gameSpaces` et `layoutOfModel`
- ✅ Exemples testés : `ex_button_1.py`, `ex_button_2.py`, `ex_button_4.py`, `ex_button_5.py`

**Points clés** :
- Le hover s'applique sur toute la superficie du container visible
- Le `QPushButton` interne est transparent pour éviter la cascade QSS
- Les styles sont appliqués via `paintEvent` (container) et `onTextAspectsChanged` (texte)

---

### 3. Application de l'alignement via gs_aspect ✅

**GameSpaces traités** :
- ✅ **SGLabel** : `text1_aspect.alignment` appliqué au `QLabel` interne
- ✅ **SGButton** : `text1_aspect.alignment` appliqué au `QPushButton`/`QLabel` interne
- ✅ **SGProgressGauge** : `title1_aspect.alignment` pour title, `text1_aspect.alignment` pour value_label (par défaut 'center')
- ✅ **SGDashBoard** : `title1_aspect.alignment` pour `labelTitle`, `text1_aspect.alignment` pour les labels des indicateurs
- ✅ **SGTimeLabel** : `title1_aspect.alignment` pour `labelTitle`, `text1_aspect.alignment` pour les autres labels
- ✅ **SGLegendItem** : Respect de l'alignement via `title1/title2/text1_aspect` dans `paintEvent`
- ✅ **SGControlPanel** : Déjà intégré, alignement respecté dans les `SGLegendItem`

**Points clés** :
- Chaque GameSpace a une méthode `onTextAspectsChanged()` qui applique l'alignement
- Le Custom Theme Editor peut modifier l'alignement et l'appliquer en Preview
- L'alignement est sauvegardé dans les thèmes personnalisés

---

### 4. Corrections de SGControlPanel ✅
**Fichier** : `mainClasses/SGControlPanel.py`

- ✅ Ajout de paddings explicites : `topPadding = 8`, `leftPadding = 10`, `rightMargin = 8`, `bottomPadding = 3`
- ✅ Ajustement du calcul de largeur via `getSizeX_fromAllWidgets()` utilisant `minimumSize().width()` des `SGLegendItem`
- ✅ Inclusion du `Title1` dans `legendItems` pour que sa largeur soit prise en compte
- ✅ Ajustement du `paintEvent` pour utiliser les paddings explicites
- ✅ Ajustement du positionnement dans `SGLegendItem.paintEvent` pour utiliser `self.legend.leftPadding` et `self.legend.topPadding`

**Points clés** :
- Les marges sont maintenant cohérentes visuellement
- La marge de droite prend en compte tous les widgets (y compris Title1 et Title2)

---

### 5. Correction de la fuite de bordures dans Custom Theme Editor ✅
**Fichier** : `mainClasses/theme/SGThemeCustomEditorDialog.py`

- ✅ Correction de `_restore_original()` : nettoyage du QSS résiduel avec `setStyleSheet("")` avant de réappliquer les styles
- ✅ Utilisation de `applyContainerAspectStyle()` au lieu de `_applyContainerStyle()` pour respecter les GameSpaces qui ne l'utilisent pas
- ✅ Réapplication propre des styles container et texte via les hooks `applyContainerAspectStyle()` et `onTextAspectsChanged()`

**Problème résolu** :
- Avant : Lors du Cancel, des bordures s'affichaient sur les widgets enfants (non désiré)
- Après : Les styles sont restaurés proprement sans fuite vers les widgets enfants

---

### 6. Positionnement du Theme Assignment Dialog ✅
**Fichier** : `mainClasses/theme/SGThemeEditTableDialog.py`

- ✅ Implémentation de `showEvent()` pour positionner la fenêtre à droite de la fenêtre principale
- ✅ Gestion des limites d'écran pour éviter que la fenêtre sorte de la zone visible
- ✅ Calcul dynamique de la position en fonction de la taille de la fenêtre principale

---

## 🔄 TRAVAIL EN ATTENTE / PROBLÈMES IDENTIFIÉS

### 1. SGTextBox : hauteur et word-wrap ⚠️
**Fichier** : `mainClasses/SGTextBox.py`  
**Exemple de test** : `ex_textbox_font_style.py`

**Problèmes identifiés** :
- ❌ Les textBox 7, 8, 9 (avec texte long et `QTextEdit`) : le texte déborde par le bas du cadre
- ❌ Le word-wrap ne semble pas toujours s'appliquer correctement pour les `QTextEdit`
- ❌ La hauteur calculée automatiquement ne prend pas toujours en compte tout le texte wrappé

**Tentatives précédentes** :
- Configuration explicite de `setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)` et `setWordWrapMode(QTextOption.WordWrap)`
- Recalcul de la hauteur via `QTextDocument.setTextWidth()` et `doc.size().height()`
- Ajout de padding pour prendre en compte les marges du layout et du frame

**Statut** : ⏸️ Laissé en attente par décision utilisateur. À corriger plus tard.

---

### 2. Sauvegarde/chargement des custom themes ⚠️
**Problème identifié** :
- ❌ Lors de la sauvegarde d'un thème via Custom Theme Editor puis chargement dans un autre GameSpace, certains paramètres ne s'appliquent pas (ex: `text_color` ne s'applique pas, mais `bgcolor` fonctionne)

**Fichiers concernés** :
- `mainClasses/theme/SGThemeCustomEditorDialog.py` : Méthode `_onSave()` et `_apply_spec_to_gs()`
- `mainClasses/theme/SGThemeConfigManager.py` : Système de gestion des thèmes

**Action requise** : Investigation et correction de la logique de sauvegarde/chargement pour garantir que tous les paramètres du `gs_aspect` sont correctement sérialisés et désérialisés.

---

### 3. Système de sauvegarde des custom themes et Manage Theme Configuration ⚠️
**Problème identifié** :
- ❌ Le système actuel de sauvegarde/chargement des thèmes personnalisés n'est pas optimal
- ❌ La fenêtre "Manage Theme Configuration" nécessite un repensage

**Action requise** : Repenser l'architecture de sauvegarde des thèmes pour garantir :
- Persistance entre sessions
- Export/import de configurations
- Gestion des conflits de noms

---

## 📋 TRAVAIL RESTANT (de NEXT_STEPS.md + nouvelles tâches)

### Tâches identifiées dans NEXT_STEPS.md

#### Phase 4 : Système de thèmes global (si souhaité)
- [ ] Implémenter `model.applyThemeToAllGameSpaces(theme_name)`
- [ ] Définir la logique de priorité (global vs individuel)
- [ ] Gérer les exclusions (types de GameSpaces à ignorer)
- [ ] Tests du système global

#### Phase 5 : Conversion SGLabel/SGButton en GameSpaces
- ✅ **TERMINÉ** : SGLabel migré vers SGGameSpace
- ✅ **TERMINÉ** : SGButton migré vers SGGameSpace
- ✅ **TERMINÉ** : Compatibilité maintenue avec les méthodes existantes

#### Classes GameSpaces restantes à traiter
- [ ] **SGLegend** : Utilise SGLegendItem, adapter l'approche
- [ ] **SGGrid** : Classe complexe avec fonctionnalités avancées, traiter avec précaution

#### Améliorations possibles
- [ ] Ajouter plus de thèmes prédéfinis
- [ ] Système de thèmes personnalisés par le modeler (partiellement fait, à améliorer)
- [ ] Export/import de configurations de thèmes
- [ ] Interface graphique pour la gestion des thèmes (améliorer "Manage Theme Configuration")
- [ ] **Corriger les erreurs de stylesheet des indicateurs du dashboard** (`Could not parse stylesheet of object QLabel`)
- [ ] **Utiliser l'analyse HARDCODED_STYLES_ANALYSIS.md** pour définir les styles par défaut
- [ ] **Déprécier les paramètres de style dans les constructeurs** des factory methods
- [ ] **Faire la "chasse" aux méthodes set de styles** qui contournent le système `gs_aspect`

---

### Nouvelles tâches ajoutées (d'après la TODO actuelle)

#### 1. Support d'image en background ⏸️
- [ ] Ajouter la prise en charge d'image en background à la place d'une couleur
- **Priorité** : Ajoutée en 3ème position dans la TODO
- **Fichiers concernés** : `SGAspect.py`, `SGGameSpace.py`, GameSpaces qui utilisent `background_image`

#### 2. Réduction de duplication de code 📝
- [ ] Réduire duplication de logique texte entre GameSpaces via héritage/refactor
- **Constat** : Plusieurs GameSpaces ont des implémentations similaires de `onTextAspectsChanged()`
- **Opportunité** : Factoriser dans `SGGameSpace` ou créer une classe utilitaire

#### 3. Nettoyage des méthodes modeler 📝
- [ ] Nettoyer les méthodes modeler de création des GameSpaces (retirer anciens styles)
- **Fichiers concernés** : `SGModel.py` (factory methods)
- **Objectif** : Déprécier les paramètres de style dans les constructeurs pour forcer l'utilisation de `gs_aspect`

#### 4. Documentation 📝
- [ ] Documenter le chantier (design, décisions, guide modeler)
- **Fichiers à créer/mettre à jour** :
  - Guide pour les modelers sur l'utilisation de `gs_aspect`
  - Documentation technique de l'architecture
  - Mise à jour des README existants

---

## 🎯 PRIORITÉS RECOMMANDÉES

### Court terme (prochaines sessions)
1. **Corriger SGTextBox** (word-wrap et hauteur) ⚠️
2. **Corriger la sauvegarde/chargement des custom themes** ⚠️
3. **Repenser Manage Theme Configuration** ⚠️

### Moyen terme
4. **Réduire la duplication de code** (refactor `onTextAspectsChanged`)
5. **Ajouter support d'image en background**
6. **Nettoyer les méthodes modeler** (déprécier paramètres de style dans constructeurs)

### Long terme
7. **Finaliser SGLegend et SGGrid**
8. **Système de thèmes global** (si souhaité)
9. **Documentation complète**

---

## 📁 FICHIERS MODIFIÉS (récents)

### Classes principales
- `mainClasses/SGAspect.py` : Classe centrale (inchangée récemment)
- `mainClasses/SGGameSpace.py` : Méthodes modeler communes (inchangée récemment)
- `mainClasses/SGModel.py` : Factory methods `newLabel()` et `newButton()` modifiées

### Classes GameSpaces migrées récemment
- ✅ `mainClasses/SGLabel.py` : Migration complète vers SGGameSpace
- ✅ `mainClasses/SGButton.py` : Migration complète vers SGGameSpace
- ✅ `mainClasses/SGControlPanel.py` : Ajustement des marges
- ✅ `mainClasses/SGProgressGauge.py` : Application de l'alignement
- ✅ `mainClasses/SGDashBoard.py` : Application de l'alignement
- ✅ `mainClasses/SGTimeLabel.py` : Application de l'alignement
- ✅ `mainClasses/SGLegendItem.py` : Respect de l'alignement

### Dialogues et thèmes
- ✅ `mainClasses/theme/SGThemeCustomEditorDialog.py` : Correction fuite de bordures, prise en charge de l'alignement
- ✅ `mainClasses/theme/SGThemeEditTableDialog.py` : Positionnement de la fenêtre
- `mainClasses/theme/SGThemeConfigManager.py` : À investiguer pour la sauvegarde/chargement

### Classes en attente
- ⚠️ `mainClasses/SGTextBox.py` : Problèmes de hauteur/word-wrap à corriger
- [ ] `mainClasses/SGLegend.py` : À traiter
- [ ] `mainClasses/SGGrid.py` : À traiter

---

## 📊 STATISTIQUES

### Classes GameSpaces
- **Total** : 12 classes GameSpaces identifiées
- **Migrées vers gs_aspect** : 10 ✅
  - SGUserSelector ✅
  - SGDashBoard ✅
  - SGControlPanel ✅
  - SGProgressGauge ✅
  - SGTimeLabel ✅
  - SGVoid ✅
  - SGTextBox ✅ (partiellement, problèmes de hauteur/word-wrap)
  - SGEndGameRule ✅
  - SGLabel ✅ (récemment)
  - SGButton ✅ (récemment)
- **En attente** : 2
  - SGLegend
  - SGGrid

### Fonctionnalités
- ✅ Alignement via `gs_aspect` : 8/12 GameSpaces
- ✅ PaintEvent avec `gs_aspect` : 10/12 GameSpaces
- ✅ Custom Theme Editor fonctionnel : Oui (avec bugs mineurs à corriger)
- ✅ Theme Assignment Dialog : Fonctionnel avec positionnement

---

## 🔍 POINTS D'ATTENTION POUR LA SUITE

1. **Compatibilité rétroactive** : Les anciennes syntaxes CSS (`textStyle_specs`, etc.) sont encore supportées via parsing dans `SGLabel`. À déprécier progressivement.

2. **Double voie de style** : Certaines factory methods (`newTimeLabel`, `newDashBoard`) acceptent encore des paramètres de style qui contournent `gs_aspect`. À nettoyer.

3. **Tests de régression** : Après chaque modification, tester les exemples existants pour garantir la compatibilité.

4. **Architecture QSS vs paintEvent** : Certains GameSpaces utilisent `paintEvent` pour éviter les problèmes de cascade QSS. Cette approche est correcte et doit être maintenue.

---

## 📝 NOTES TECHNIQUES

### Hiérarchie de priorité des styles
1. **Style défini par le modeler** (via méthodes modeler comme `setBorderColor()`, `setTextColor()`, etc.)
2. **Thème appliqué** (via `applyTheme()`)
3. **Style défini dans la classe fille** (défauts spécifiques à la classe)
4. **Style par défaut de la classe mère** (SGGameSpace)

### Méthodes clés de `SGGameSpace`
- `applyContainerAspectStyle()` : Applique les styles du container (background, border) - certains GameSpaces la surchargent en `pass` pour utiliser `paintEvent`
- `onTextAspectsChanged()` : Hook pour appliquer les styles texte (`text1_aspect`, `title1_aspect`, etc.) - doit être implémentée par chaque GameSpace
- `updateSizeFromLayout()` : Calcule la taille à partir d'un layout
- `updateSizeFromLabels()` : Calcule la taille à partir de labels

### Architecture des aspects
- `gs_aspect` : Styles du container (background, border, padding, etc.)
- `text1_aspect`, `text2_aspect`, `text3_aspect` : Styles pour les textes de contenu
- `title1_aspect`, `title2_aspect`, `title3_aspect` : Styles pour les titres

---

**Fin du récapitulatif**

