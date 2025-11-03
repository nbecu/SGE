# GS_ASPECT_SYSTEM DEV 

## État d'avancement du système gs_aspect

**Date** : 15/10/2025  
**Dernière mise à jour** : [Date actuelle]

### 🚨 INFORMATIONS POUR LE PROCHAIN CHATBOT

**CONTEXTE** : Ce fichier documente l'état d'avancement du système `gs_aspect` (SGAspect) pour uniformiser la gestion des styles dans toutes les classes GameSpaces de SGE.

**ARCHITECTURE ACTUELLE** :
- **SGAspect** : Classe centrale pour définir les styles (couleurs, polices, bordures, etc.)
- **SGGameSpace** : Classe mère de tous les GameSpaces avec méthodes modeler communes
- **Classes GameSpaces** : SGTextBox, SGEndGameRule, SGUserSelector, SGDashBoard, SGControlPanel, SGProgressGauge, SGTimeLabel, SGVoid, SGLegend, SGGrid

**SYSTÈME FONCTIONNEL** :
- ✅ Méthodes modeler individuelles : `setBorderColor()`, `setTextColor()`, `setFontSize()`, etc.
- ✅ Méthode de style complet : `setStyle(dict)` pour appliquer plusieurs propriétés
- ✅ Système de thèmes : `applyTheme(theme_name)` avec thèmes prédéfinis
- ✅ Conversion automatique des couleurs Qt vers CSS
- ✅ 8 classes GameSpaces migrées vers le système `gs_aspect`

**PROBLÈMES IDENTIFIÉS À RÉSOUDRE** :
1. **Contournement du système** : Les paramètres de style dans les constructeurs (ex: `newTimeLabel("Title", Qt.white, Qt.black)`)
2. **Double voie** : Le modeler peut utiliser soit les paramètres du constructeur, soit les méthodes modeler
3. **Erreurs de stylesheet** : Avec les indicateurs du dashboard

**FICHIERS CLÉS À EXAMINER** :
- `mainClasses/SGAspect.py` : Classe centrale avec thèmes prédéfinis
- `mainClasses/SGGameSpace.py` : Méthodes modeler communes
- `mainClasses/SGModel.py` : Factory methods avec paramètres de style
- `notes for FUTURE_PLAN/HARDCODED_STYLES_ANALYSIS.md` : Analyse des styles hardcodés (non utilisée)
- `examples/syntax_examples/ex_game_space_style_*.py` : Exemples de test

**PRIORITÉS** :
1. Déprécier les paramètres de style dans les constructeurs
2. Faire la "chasse" aux méthodes set de styles qui contournent `gs_aspect`
3. Utiliser l'analyse HARDCODED_STYLES_ANALYSIS.md pour les styles par défaut
4. Corriger les erreurs de stylesheet des indicateurs du dashboard

---

### ✅ Travail terminé

#### Phase 1 : Extension de SGAspect
- ✅ Ajout des attributs étendus : `border_radius`, `min_width`, `min_height`, `padding`, `word_wrap`, `background_image`, `fixed_width`, `fixed_height`
- ✅ Ajout des états de survol : `hover_text_color`, `hover_background_color`, `hover_border_color`
- ✅ Ajout des états de bouton : `pressed_color`, `disabled_color`
- ✅ Création des thèmes prédéfinis : `modern()`, `minimal()`, `colorful()`, `blue()`, `green()`, `gray()`
- ✅ Ajout des méthodes étendues : `getExtendedStyle()`, `getHoverStyle()`, `getButtonStatesStyle()`

#### Phase 2 : Méthodes modeler dans SGGameSpace
- ✅ Méthodes individuelles : `setBorderColor()`, `setTextColor()`, `setFontSize()`, etc.
- ✅ Méthode de style complet : `setStyle(dict)` pour appliquer plusieurs propriétés
- ✅ Système de thèmes : `applyTheme(theme_name)` avec thèmes prédéfinis
- ✅ Mise à jour automatique : `self.update()` après chaque modification

#### Phase 3 : Migration des classes GameSpaces
- ✅ **SGUserSelector** : Migration vers `gs_aspect`, méthodes modeler ajoutées
- ✅ **SGDashBoard** : Utilise déjà `gs_aspect`, méthodes modeler ajoutées
- ✅ **SGControlPanel** : Utilise déjà `gs_aspect`, méthodes modeler existantes
- ✅ **SGProgressGauge** : Utilise déjà `gs_aspect`, méthodes modeler existantes
- ✅ **SGTimeLabel** : Utilise déjà `gs_aspect`, méthodes modeler ajoutées
- ✅ **SGVoid** : Méthodes modeler ajoutées
- ✅ **SGTextBox** : Remplacement par SGTextBoxLargeShrinkable (nouvelle implémentation robuste avec `gs_aspect`)
- ✅ **SGEndGameRule** : Utilise déjà `gs_aspect` avec méthodes modeler complètes
- ✅ **SGLabel** : Migration complète vers SGGameSpace
- ✅ **SGButton** : Migration complète vers SGGameSpace
- ✅ **SGLegend** : Migration vers `gs_aspect` (utilise `gs_aspect` pour container, SGLegendItem utilise text_aspects)
- ✅ **SGGrid** : Migration vers `gs_aspect` (utilise `gs_aspect` pour container et background image)

#### Corrections et améliorations
- ✅ Correction de `SGModel.newEndGameRule()` pour accepter les paramètres de style
- ✅ Ajout de `SGModel.newVoid()` manquante
- ✅ Correction des paramètres `newProgressGauge()` (minimum/maximum vs min_value/max_value)
- ✅ Utilisation des couleurs étendues de `SGExtensions.py` (Qt.lightgreen, Qt.lightblue, etc.)

#### Tests et exemples
- ✅ Création d'exemples de test complets
- ✅ Test des méthodes individuelles (ex_game_space_style_2.py)
- ✅ Test du système de thèmes (ex_game_space_style_4.py)
- ✅ Suppression des `moveToCoords()` (remplacés par SGEnhancedGridLayout)
- ✅ Validation du fonctionnement du système
- ⚠️ **Problème identifié** : Erreurs de stylesheet avec les indicateurs du dashboard (`Could not parse stylesheet of object QLabel`)
- ⚠️ **Note importante** : L'analyse `HARDCODED_STYLES_ANALYSIS.md` n'a pas été utilisée comme guide d'implémentation
- ⚠️ **Problème majeur** : Les paramètres de style dans les constructeurs contournent le système `gs_aspect`
- ✅ **SGTextBox** : Problèmes de hauteur/word-wrap résolus avec la nouvelle implémentation SGTextBoxLargeShrinkable
  - Exemple : `myModel.newTimeLabel("Title", Qt.white, Qt.black, Qt.black)`
  - Exemple : `myModel.newDashBoard('Title', borderColor=Qt.black, textColor=Qt.black)`
  - **Conséquence** : Double voie pour définir les styles (constructeur vs méthodes modeler)

---

### 🔄 Travail en cours

#### Réflexions sur le système de thèmes
**Question en suspens** : Application des thèmes

**Options disponibles** :
1. **Application individuelle** : `gameSpace.applyTheme('modern')`
   - ✅ Déjà implémenté et fonctionnel
   - Avantages : Flexibilité totale
   - Inconvénients : Plus de code pour application globale

2. **Application globale** : `model.applyThemeToAllGameSpaces('modern')`
   - ✅ Déjà implémenté et fonctionnel
   - Avantages : Une ligne pour changer toute l'interface
   - Inconvénients : Moins de flexibilité

3. **Approche hybride** : Les deux approches
   - Application globale + personnalisation individuelle
   - Recommandée pour maximum de flexibilité

**Questions à résoudre** :
- Voulez-vous les deux approches ou seulement une ?
- Pour l'application globale, inclure tous les GameSpaces ou exclure certains types (ex: grilles) ?
- Comment gérer les conflits entre thème global et thème individuel ?

---

### 📋 Travail restant

#### Phase 4 : Système de thèmes global
- ✅ **TERMINÉ** : `model.applyThemeToAllGameSpaces(theme_name)` implémenté
- ✅ **TERMINÉ** : Bouton "Apply to All..." ajouté dans Theme Assignment Dialog
- [ ] Définir la logique de priorité (global vs individuel) - documentation
- [ ] Gérer les exclusions (types de GameSpaces à ignorer) - optionnel
- [ ] Tests du système global

#### Phase 5 : Conversion SGLabel/SGButton en GameSpaces
- ✅ **TERMINÉ** : SGLabel migré vers SGGameSpace
- ✅ **TERMINÉ** : SGButton migré vers SGGameSpace
- ✅ **TERMINÉ** : Compatibilité maintenue avec les méthodes existantes

#### Classes GameSpaces restantes à traiter
- ✅ **SGLegend** : Migration vers `gs_aspect` terminée
- ✅ **SGGrid** : Migration vers `gs_aspect` terminée

#### Système de thèmes personnalisés ✅ **TERMINÉ**
- ✅ **Dialogue Custom Theme Editor** : Création et édition de thèmes custom en mémoire
- ✅ **Thèmes custom en mémoire** : Stockage dans `model._runtime_themes` pendant la session
- ✅ **Generate Theme Code** : Génération du code Python pour promouvoir un thème custom en prédéfini
- ✅ **Découverte dynamique des thèmes** : Les thèmes prédéfinis sont détectés automatiquement (plus de liste codée)
- ✅ **text_aspects dans thèmes prédéfinis** : Tous les thèmes prédéfinis incluent maintenant `text_aspects`
- ✅ **Persistance des thèmes custom** : Les thèmes custom sont sauvegardés dans `theme_config.json` et chargés au démarrage
- ✅ **Distinction visuelle** : Préfixe "📝 " pour les thèmes custom dans l'interface
- ✅ **Protection contre conflits** : Vérification que les noms de thèmes custom n'entrent pas en conflit avec les prédéfinis
- ✅ **Méthodes modeler** : `applyThemeConfig()` et `applyLayoutConfig()` pour charger les configurations via script (comportement retardé)

#### Améliorations possibles
- [ ] Ajouter plus de thèmes prédéfinis
- [ ] Export/import de configurations de thèmes
- ✅ **Interface graphique améliorée** : "Manage Theme Configuration" améliorée (layout compact, boutons réorganisés)
- ✅ **Support d'image en background** : Implémenté pour tous les GameSpaces via `gs_aspect.background_image`
- ✅ **Menu "Change window background color"** : Ajouté dans le menu Themes
- ✅ **Refactorisation du positionnement des dialogs** : Fonction utilitaire `position_dialog_to_right()` dans `SGExtensions.py`
- ✅ **Bouton "Apply to All"** : Ajouté dans Theme Assignment Dialog
- [ ] **Corriger les erreurs de stylesheet des indicateurs du dashboard**
- [ ] **Utiliser l'analyse HARDCODED_STYLES_ANALYSIS.md** pour définir les styles par défaut
- [ ] **Déprécier les paramètres de style dans les constructeurs** des factory methods
- [ ] **Faire la "chasse" aux méthodes set de styles** qui contournent le système `gs_aspect`

---

### 🧪 Tests à effectuer

#### Tests fonctionnels
- [ ] Tester tous les exemples créés
- [ ] Valider le comportement avec SGEnhancedGridLayout
- [ ] Tester les performances avec de nombreux GameSpaces
- [ ] Valider la compatibilité avec les fonctionnalités existantes

#### Tests de régression
- [ ] Vérifier que les exemples existants fonctionnent toujours
- [ ] Tester la compatibilité avec les jeux existants
- [ ] Valider le comportement des méthodes existantes

---

### 📝 Notes techniques

#### Architecture actuelle
- **SGAspect** : Classe centrale avec styles prédéfinis et attributs étendus
- **SGGameSpace** : Méthodes modeler communes pour tous les GameSpaces
- **Classes filles** : Méthodes modeler spécifiques + utilisation de `gs_aspect`
- **SGEnhancedGridLayout** : Gestion automatique du placement (pas de `moveToCoords()`)

#### Hiérarchie de priorité des styles
1. **Style défini par le modeler** (via méthodes modeler)
2. **Style défini dans la classe fille** (SGEndGameRule, SGDashBoard, etc.)
3. **Style par défaut de la classe mère** (SGGameSpace)

#### Syntaxe modeler validée
```python
# Méthodes individuelles
gameSpace.setBorderColor(Qt.red)
gameSpace.setTextColor(Qt.blue)
gameSpace.setFontSize(14)

# Méthode de style complet
gameSpace.setStyle({
    'border_color': Qt.red,
    'background_color': Qt.white,
    'text_color': Qt.blue,
    'font_size': 14,
    'font_weight': 'bold'
})

# Système de thèmes
gameSpace.applyTheme('modern')
```

#### Couleurs disponibles
- Utilisation des couleurs étendues de `SGExtensions.py`
- Qt.lightgreen, Qt.lightblue, Qt.lightyellow, Qt.pink, etc.
- Couleurs thématiques : Qt.darkgreen, Qt.darkblue, Qt.orange, etc.

---

### 🎯 Prochaines étapes

1. **Nettoyage et consolidation** ⚠️ **PRIORITÉ ACTUELLE**
   - Déprécier les paramètres de style dans les constructeurs des factory methods
   - Faire la "chasse" aux méthodes set de styles qui contournent `gs_aspect`
2. **Corrections de bugs**
   - Corriger les erreurs de stylesheet des indicateurs du dashboard
   - ✅ SGTextBox : problèmes de hauteur/word-wrap résolus
3. **Améliorations techniques**
   - 🔄 **EN COURS** : Réduire la duplication de code : refactoriser `onTextAspectsChanged()` dans `SGGameSpace`
     - **Plan de refactorisation** :
       - Créer `mapAlignmentStringToQtFlags()` dans `SGExtensions.py` (méthode générique)
       - Créer `applyToQFont()`, `getStyleSheetForColorAndDecoration()`, `applyToQLabel()` dans `SGAspect` (méthodes d'instance)
       - Créer `_applyAspectToLabel()` helper dans `SGGameSpace` (DEVELOPER METHODS section)
       - Refactoriser toutes les classes filles pour utiliser ces méthodes
       - Supprimer les `_map_alignment()` locaux dupliqués
       - Chaque classe gère ses propres boucles pour application multiple (Option A)
     - **Décisions** :
       - Option A pour helper dans SGGameSpace (méthode `_applyAspectToLabel()`)
       - Option A pour application multiple (chaque classe gère ses boucles)
       - Conserver l'ordre d'application actuel (ne pas changer)
       - Conserver la robustesse (try/except)
       - Supprimer directement les `_map_alignment()` locaux
   - Utiliser l'analyse `HARDCODED_STYLES_ANALYSIS.md` pour définir les styles par défaut
4. **Documentation** : Mise à jour des README et guides

---

### 📁 Fichiers modifiés

#### Classes principales
- ✅ `mainClasses/SGAspect.py` : Extension avec attributs et thèmes, ajout de `text_aspects` aux thèmes prédéfinis
- ✅ `mainClasses/SGGameSpace.py` : Méthodes modeler communes, découverte dynamique des thèmes, application des text_aspects différenciés, support background_image
- ✅ `mainClasses/SGModel.py` : Correction newEndGameRule, ajout newVoid, migration newLabel et newButton vers SGGameSpace, méthodes `applyThemeConfig()` et `applyLayoutConfig()`, menu "Change window background color"

#### Classes GameSpaces
- ✅ `mainClasses/SGUserSelector.py` : Migration vers gs_aspect
- ✅ `mainClasses/SGDashBoard.py` : Méthodes modeler ajoutées, application de l'alignement
- ✅ `mainClasses/SGTimeLabel.py` : Méthodes modeler ajoutées, application de l'alignement
- ✅ `mainClasses/SGVoid.py` : Méthodes modeler ajoutées
- ✅ `mainClasses/SGLabel.py` : Migration complète vers SGGameSpace
- ✅ `mainClasses/SGButton.py` : Migration complète vers SGGameSpace
- ✅ `mainClasses/SGProgressGauge.py` : Application de l'alignement
- ✅ `mainClasses/SGTextBox.py` : Remplacement par SGTextBoxLargeShrinkable (nouvelle implémentation robuste, problèmes de hauteur/word-wrap résolus)
- ✅ `mainClasses/SGLegend.py` : Migration vers gs_aspect (container + background image)
- ✅ `mainClasses/SGGrid.py` : Migration vers gs_aspect (container + background image)

#### Exemples de test
- `examples/syntax_examples/ex_game_space_style_2.py` : Test méthodes individuelles
- `examples/syntax_examples/ex_game_space_style_3.py` : Test style dictionary
- `examples/syntax_examples/ex_game_space_style_4.py` : Test système de thèmes
- `examples/syntax_examples/ex_game_space_style_5.py` : Test approche mixte

#### Dialogues et gestion des thèmes
- ✅ `mainClasses/theme/SGThemeCustomEditorDialog.py` : Création et édition de thèmes custom, persistance, améliorations UI
- ✅ `mainClasses/theme/SGThemeEditTableDialog.py` : Assignment de thèmes, découverte dynamique, bouton "Theme code...", "Apply to All..."
- ✅ `mainClasses/theme/SGThemeCodeGeneratorDialog.py` : Génération du code Python pour promouvoir un thème custom
- ✅ `mainClasses/theme/SGThemeConfigManager.py` : Persistance des thèmes custom dans `theme_config.json`, chargement au démarrage
- ✅ `mainClasses/theme/SGThemeConfigManagerDialog.py` : Interface améliorée (layout compact, boutons réorganisés)
- ✅ `mainClasses/SGExtensions.py` : Fonction utilitaire `position_dialog_to_right()` pour positionnement des dialogs

#### Documentation
- `notes for FUTURE_PLAN/HARDCODED_STYLES_ANALYSIS.md` : Analyse des styles hardcodés
- `notes for FUTURE_PLAN/UNIFORMIZE_FONT_STYLES_GAMESPACES.md` : Mise à jour avec gs_aspect
