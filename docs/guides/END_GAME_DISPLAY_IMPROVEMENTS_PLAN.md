# Plan de développement : Améliorations de l'affichage de fin de partie

## Date : Janvier 2026
## Statut : Planification - En attente d'implémentation

---

## 1. Contexte et problèmes identifiés

### 1.1 Problème initial
Lorsqu'une condition de fin de partie est atteinte, l'utilisateur n'est pas clairement informé que le jeu est terminé :
- Seule une coche ✓ apparaît dans le widget endGameRule
- Le terminal affiche "Game Over!" mais l'interface graphique n'est pas explicite
- En mode distribué, les messages modaux sont déconseillés

### 1.2 Problème avec delay_rounds et final_phase
Avec les paramètres `delay_rounds` et `final_phase`, le comportement actuel pose des problèmes UX :
- La coche ✓ n'apparaît qu'après le delay, alors que la condition est détectée avant
- L'utilisateur n'est pas informé du nombre de rounds/phases restants
- Pour Sea Zones : les joueurs doivent savoir qu'ils entament le dernier tour

### 1.3 Problème avec showEndGameConditions()
- Le widget peut apparaître automatiquement quand la condition est détectée
- Le nom de la méthode `showEndGameConditions()` n'est plus totalement approprié
- Besoin de clarifier le rôle de cette méthode

---

## 2. Objectifs

1. **Améliorer la visibilité de la fin de partie** : Bannière et/ou highlight du widget
2. **Informer les joueurs du temps restant** : Compteur dynamique de rounds/phases
3. **Afficher la coche dès détection** : Pas seulement après le delay
4. **Flexibilité pour les modelers** : Choix entre bannière, highlight, les deux, ou aucun
5. **Compatibilité** : Pas de breaking change pour le code existant

---

## 3. Modifications prévues

### 3.1 Renommage de méthode

**Changement** : `showEndGameConditions()` → `displayEndGameConditions()`

**Raison** :
- Plus cohérent avec les conventions SGE (préfixe `display`)
- Nom plus approprié compte tenu du nouveau comportement automatique

**Impact** :
- Mise à jour de tous les appels dans le codebase
- Amélioration de la documentation (docstring)

### 3.2 Affichage automatique du widget

**Comportement actuel** :
- Le widget n'apparaît que si `displayEndGameConditions()` est appelé
- Sinon, fenêtre vide bizarre apparaît quand condition atteinte

**Nouveau comportement** :
- Le widget s'affiche automatiquement quand la condition est détectée (même avec delay_rounds)
- `displayEndGameConditions()` reste utile pour afficher le widget avant détection
- Flag `_conditions_shown` pour suivre l'état d'affichage

**Implémentation** :
- Widget invisible par défaut (`setVisible(False)`)
- Affichage automatique dans `byCalcType()` quand `end_round` est calculé pour la première fois
- `displayEndGameConditions()` marque `_conditions_shown = True` et rend visible

### 3.3 Affichage de la coche dès détection

**Comportement actuel** :
- Coche ✓ apparaît seulement quand `checkStatus = True` (après delay)

**Nouveau comportement** :
- Coche ✓ apparaît dès que la condition est détectée (`end_round` calculé)
- Le texte est complété avec le compteur de temps restant
- Quand fin atteinte, le compteur disparaît, coche ✓ reste

**Exemple** :
- Condition détectée : `"✓ the tile "low tide" is drawn -> Last round (1 round, 2 phases remaining)"`
- Fin atteinte : `"✓ the tile "low tide" is drawn"`

### 3.4 Compteur dynamique de temps restant

**Fonctionnalité** :
- Calcul automatique des rounds/phases restants
- Affichage dans le texte de la condition
- Mise à jour automatique à chaque phase

**Format** :
- `"-> Last round (1 round, 2 phases remaining)"`
- Variations selon contexte (rounds seulement, phases seulement, les deux)

**Calcul** :
- Rounds restants : `end_round - current_round`
- Phases restantes : Calcul basé sur `end_phase`, `current_phase`, et `total_phases`

### 3.5 Système d'affichage de fin de partie (bannière + highlight)

**Nouvelle fonctionnalité** :
- Bannière en haut de la fenêtre (optionnelle)
- Highlight du widget endGameRule (optionnel)
- Animation de pulsation (optionnelle)
- Configuration flexible via API modeler

**Modes disponibles** :
- `'banner'` : Bannière uniquement
- `'highlight'` : Highlight widget uniquement (défaut)
- `'highlight + banner'` : Les deux
- `'none'` : Aucun affichage spécial (seulement coche ✓)

---

## 4. API Modeler - Nouvelles méthodes

### 4.1 Paramètres dans `newEndGameRule()`

```python
endGameRule = myModel.newEndGameRule(
    title='EndGame Rules',
    numberRequired=1,
    # ... paramètres existants ...
    
    # New optional parameters for end game display
    endGameDisplayMode='highlight',  # Default: 'highlight'
    endGameBannerText='Game over',  # Default: 'Game over'
    endGameBannerColor=Qt.red,
    endGameBannerPosition='top',  # 'top' or 'bottom'
    endGameHighlightEnabled=True,
    endGameHighlightBorderColor=Qt.green,
    endGameHighlightBorderSize=4,
    endGameHighlightBackgroundColor=Qt.lightGreen,
    endGameAnimationEnabled=False,  # Default: False (disabled)
    endGameAnimationDuration=2000
)
```

### 4.2 Méthode de configuration complète

```python
def setEndGameDisplay(self, mode='highlight', banner_text='Game over', 
                     banner_color=Qt.red, banner_position='top',
                     highlight_border_color=Qt.green, highlight_border_size=4,
                     highlight_background_color=Qt.lightGreen,
                     animation_enabled=False, animation_duration=2000):
    """
    Configure all end game display options in a single call.
    
    This is a convenience method that sets all display-related options at once.
    Individual SET methods can still be used for fine-tuning after this call.
    """
```

### 4.3 Méthodes SET individuelles

```python
# Mode d'affichage
def setEndGameDisplayMode(self, mode='highlight'):
    """Set the end game display mode: 'banner', 'highlight', 'highlight + banner', or 'none'"""

# Configuration bannière
def enableEndGameBanner(self):
    """Enable the end game banner display."""

def disableEndGameBanner(self):
    """Disable the end game banner display."""

def setEndGameBannerText(self, text):
    """Set the banner text displayed when game ends."""

def setEndGameBannerColor(self, color):
    """Set the banner background color."""

def setEndGameBannerPosition(self, position='top'):
    """Set the banner position: 'top' or 'bottom'"""

# Configuration highlight
def enableEndGameRuleHighlight(self):
    """Enable highlighting of the endGameRule widget when game ends."""

def disableEndGameRuleHighlight(self):
    """Disable highlighting of the endGameRule widget when game ends."""

def setEndGameRuleHighlightBorderColor(self, color):
    """Set the highlight border color when game ends."""

def setEndGameRuleHighlightBorderSize(self, size):
    """Set the highlight border size when game ends."""

def setEndGameRuleHighlightBackgroundColor(self, color):
    """Set the highlight background color when game ends."""

# Configuration animation
def setEndGameAnimationEnabled(self, enabled=False):
    """Enable or disable the pulse animation when game ends."""

def setEndGameAnimationDuration(self, duration_ms):
    """Set the animation duration in milliseconds."""

# Configuration compteur
def setEndGameConditionCountdownFormat(self, format_type='auto'):
    """Set the format for displaying remaining time countdown."""

def setEndGameConditionCountdownTemplate(self, template):
    """Set custom template for countdown display."""

def setEndGameConditionCountdownSeparator(self, separator=' -> '):
    """Set the separator between condition name and countdown."""
```

### 4.4 Méthodes GET

```python
def getEndGameDisplayMode(self):
    """Get the current end game display mode."""

def isEndGameBannerEnabled(self):
    """Check if banner is enabled."""

def getEndGameBannerText(self):
    """Get the banner text."""

def isEndGameRuleHighlightEnabled(self):
    """Check if widget highlight is enabled."""

def isEndGameAnimationEnabled(self):
    """Check if animation is enabled."""
```

### 4.5 Renommage de méthode

```python
def displayEndGameConditions(self):
    """
    Configure and display the EndGameRule widget with all conditions.
    
    This method:
    1. Configures the widget layout (title, conditions list, optional button)
    2. Makes the widget visible immediately
    
    Behavior:
    - If called: Widget is displayed immediately and remains visible throughout the game
    - If not called: Widget will be displayed automatically when a condition is first detected
      (useful for games with delay_rounds to inform players they're entering the last round)
    
    In both cases, when the game actually ends (checkStatus=True), the banner and highlight
    will be activated according to the endGameDisplayMode configuration.
    
    Note: This method is optional. If you want the widget to appear only when a condition
    is detected, you can omit this call. The widget will appear automatically.
    """
```

---

## 5. Modifications techniques détaillées

### 5.1 SGEndGameRule.py

**Modifications** :
1. Ajout flag `_conditions_shown` dans `__init__()`
2. Widget invisible par défaut (`setVisible(False)`)
3. Renommage `showEndGameConditions()` → `displayEndGameConditions()`
4. Ajout attributs pour configuration affichage (mode, bannière, highlight, animation)
5. Ajout méthodes SET/GET pour configuration
6. Ajout méthode `setEndGameDisplay()` pour configuration complète
7. Implémentation bannière (widget QLabel dans SGModel)
8. Implémentation highlight (styles dynamiques sur widget)
9. Implémentation animation (QPropertyAnimation pour pulsation)

### 5.2 SGEndGameCondition.py

**Modifications** :
1. Modification `updateText()` :
   - Affiche coche ✓ dès que `end_round` est calculé (condition détectée)
   - Construit texte complet : `name + separator + countdown`
   - Met à jour dynamiquement
2. Ajout méthode `getRemainingTimeText()` :
   - Calcule rounds/phases restants
   - Retourne texte formaté ou chaîne vide
3. Ajout méthodes SET pour personnalisation compteur :
   - `setEndGameConditionCountdownFormat()`
   - `setEndGameConditionCountdownTemplate()`
   - `setEndGameConditionCountdownSeparator()`
4. Modification logique `byCalcType()` :
   - Affichage automatique widget quand condition détectée
   - Calcul `end_round` et `end_phase` dès détection

### 5.3 SGTimeManager.py

**Modifications** :
1. Modification `checkEndGame()` :
   - Active bannière et highlight quand `checkStatus = True`
   - Selon configuration `endGameDisplayMode`

### 5.4 SGModel.py

**Modifications** :
1. Ajout widget bannière (QLabel ou QWidget) :
   - Position : haut ou bas selon configuration
   - Visible seulement quand `_game_ended = True`
   - Style : couleur de fond, texte centré
2. Mise à jour `newEndGameRule()` :
   - Ajout paramètres optionnels pour configuration affichage
   - Initialisation valeurs par défaut

---

## 6. Valeurs par défaut

| Paramètre | Valeur par défaut | Raison |
|-----------|-------------------|--------|
| `endGameDisplayMode` | `'highlight'` | Discret, pas intrusif |
| `endGameBannerText` | `'Game over'` | Texte simple et clair |
| `endGameBannerColor` | `Qt.red` | Couleur d'alerte standard |
| `endGameBannerPosition` | `'top'` | Position naturelle |
| `endGameHighlightBorderColor` | `Qt.green` | Indique succès/terminaison |
| `endGameHighlightBorderSize` | `4` | Visible mais pas excessif |
| `endGameHighlightBackgroundColor` | `Qt.lightGreen` | Fond discret |
| `endGameAnimationEnabled` | `False` | Désactivé par défaut (peut être activé si besoin) |
| `endGameAnimationDuration` | `2000` | Durée raisonnable (2 secondes) |
| `countdownSeparator` | `' -> '` | Séparateur clair et lisible |

---

## 7. Exemples d'utilisation

### 7.1 Exemple minimal (comportement par défaut)

```python
endGameRule = myModel.newEndGameRule()
endGameRule.addEndGameCondition_onLambda(lambda: check_victory(), name="Victory")
# Par défaut : highlight activé, pas de bannière, pas d'animation
# Widget s'affiche automatiquement quand condition détectée
```

### 7.2 Exemple Sea Zones (configuration complète)

```python
endGameRule = myModel.newEndGameRule()
endGameRule.addEndGameCondition_onLambda(
    lambda: ending_tile.isFaceFront(), 
    name='the tile "low tide" is drawn',
    delay_rounds=1,
    final_phase=(myModel.timeManager.numberOfPhases() - 2)
)

# Configuration complète en une ligne
endGameRule.setEndGameDisplay(
    mode='highlight + banner',
    banner_text='Dernier tour terminé - Partie terminée !',
    banner_color=Qt.orange,
    highlight_border_color=Qt.green,
    highlight_border_size=4,
    animation_enabled=True  # Activer animation pour Sea Zones
)

# Pas besoin de displayEndGameConditions() - s'affiche automatiquement
```

**Affichage** :
- Condition détectée : Widget apparaît avec `"✓ the tile "low tide" is drawn -> Last round (1 round, 2 phases remaining)"`
- Fin atteinte : Bannière + highlight + animation, texte devient `"✓ the tile "low tide" is drawn"`

### 7.3 Exemple avec bannière uniquement

```python
endGameRule = myModel.newEndGameRule()
endGameRule.addEndGameCondition_onLambda(lambda: gameEnded(), name="Game Ended")
endGameRule.setEndGameDisplayMode('banner')
endGameRule.setEndGameBannerText("Partie terminée !")
endGameRule.setEndGameBannerColor(Qt.red)
```

### 7.4 Exemple discret (highlight uniquement)

```python
endGameRule = myModel.newEndGameRule()
endGameRule.setEndGameDisplayMode('highlight')
endGameRule.setEndGameRuleHighlightBorderColor(Qt.green)
endGameRule.setEndGameRuleHighlightBorderSize(3)
# Pas d'animation (désactivée par défaut)
```

### 7.5 Exemple sans affichage spécial

```python
endGameRule = myModel.newEndGameRule()
endGameRule.setEndGameDisplayMode('none')
# Seulement la coche ✓, pas de bannière ni highlight
```

---

## 8. Compatibilité avec le code existant

### 8.1 Code existant continue de fonctionner

**Exemples existants** :
- `morpion_game.py` : Fonctionne sans modification (widget s'affiche automatiquement)
- `aGameExample.py` : Fonctionne avec `displayEndGameConditions()` (renommé)
- Tous les autres exemples : Compatibles après renommage méthode

### 8.2 Migration nécessaire

**Seule modification requise** :
- Renommer `showEndGameConditions()` → `displayEndGameConditions()` dans les scripts existants
- Ou laisser tel quel : l'ancien nom peut être conservé comme alias pour compatibilité

**Recommandation** :
- Conserver `showEndGameConditions()` comme alias de `displayEndGameConditions()` pour compatibilité
- Marquer comme deprecated dans la documentation
- Recommander l'utilisation de `displayEndGameConditions()`

---

## 9. Plan d'implémentation

### Phase 1 : Corrections de base
1. ✅ Widget invisible par défaut
2. ✅ Affichage automatique quand condition détectée
3. ✅ Flag `_conditions_shown` pour gestion état

### Phase 2 : Affichage coche et compteur
1. ⏳ Modifier `updateText()` pour afficher coche dès détection
2. ⏳ Ajouter méthode `getRemainingTimeText()`
3. ⏳ Compléter texte avec compteur dynamique
4. ⏳ Mise à jour automatique du compteur

### Phase 3 : Système bannière + highlight
1. ⏳ Implémenter bannière dans SGModel
2. ⏳ Implémenter highlight sur widget endGameRule
3. ⏳ Implémenter animation de pulsation
4. ⏳ Gestion activation selon `endGameDisplayMode`

### Phase 4 : API modeler
1. ⏳ Ajouter paramètres dans `newEndGameRule()`
2. ⏳ Implémenter méthode `setEndGameDisplay()`
3. ⏳ Implémenter toutes les méthodes SET/GET
4. ⏳ Renommer `showEndGameConditions()` → `displayEndGameConditions()`
5. ⏳ Ajouter alias pour compatibilité

### Phase 5 : Documentation et tests
1. ⏳ Mettre à jour docstrings
2. ⏳ Mettre à jour README_modeler.md
3. ⏳ Mettre à jour README_developer.md
4. ⏳ Mettre à jour CONTEXT_SGE_FOR_CHATBOT.md
5. ⏳ Créer exemples de démonstration
6. ⏳ Tests avec Sea Zones et autres jeux

---

## 10. Fichiers à modifier

### Fichiers principaux
- `mainClasses/SGEndGameRule.py` : Toutes les modifications API et affichage
- `mainClasses/SGEndGameCondition.py` : Logique coche, compteur, texte dynamique
- `mainClasses/SGTimeManager.py` : Activation bannière/highlight quand fin atteinte
- `mainClasses/SGModel.py` : Widget bannière, paramètres `newEndGameRule()`

### Fichiers de documentation
- `README_modeler.md` : Section sur endGameRule et affichage de fin
- `README_developer.md` : Documentation API et implémentation
- `CONTEXT_SGE_FOR_CHATBOT.md` : Mise à jour contexte
- `DEV_NOTES.md` : Ajout section travail en cours

### Fichiers d'exemples (optionnel)
- `examples/games/Sea_Zones_distributed_local_broker.py` : Exemple configuration complète
- Créer `examples/syntax_examples/ex_end_game_display.py` : Exemples tous les modes

---

## 11. Points d'attention

### 11.1 Calcul du temps restant
- Gérer correctement les cas limites (même round, même phase)
- Prendre en compte `total_phases` pour calculs précis
- Tester avec différents scénarios (delay_rounds=0, final_phase=None, etc.)

### 11.2 Bannière en mode distribué
- S'assurer que la bannière fonctionne correctement en mode distribué
- Pas de message modal (déjà évité)
- Bannière non bloquante

### 11.3 Performance
- Animation ne doit pas impacter les performances
- Mise à jour compteur à chaque phase (vérifier performance)
- Cache des calculs si nécessaire

### 11.4 Compatibilité
- Tous les exemples existants doivent continuer de fonctionner
- Alias pour `showEndGameConditions()` si nécessaire
- Valeurs par défaut raisonnables

---

## 12. Tests à effectuer

### 12.1 Tests fonctionnels
- [ ] Widget s'affiche automatiquement quand condition détectée
- [ ] Coche ✓ apparaît dès détection (pas seulement après delay)
- [ ] Compteur s'affiche et se met à jour correctement
- [ ] Bannière apparaît quand fin atteinte (si activée)
- [ ] Highlight fonctionne (si activé)
- [ ] Animation fonctionne (si activée)
- [ ] Tous les modes d'affichage fonctionnent

### 12.2 Tests avec exemples existants
- [ ] `morpion_game.py` : Fonctionne sans modification
- [ ] `aGameExample.py` : Fonctionne avec renommage méthode
- [ ] `Sea_Zones_distributed_local_broker.py` : Configuration complète fonctionne
- [ ] Tous les autres exemples : Compatibles

### 12.3 Tests edge cases
- [ ] `delay_rounds=0` : Comportement correct
- [ ] `final_phase=None` : Comportement correct
- [ ] `delay_rounds=0` et `final_phase=None` : Comportement correct
- [ ] Condition détectée puis non détectée : Gestion correcte
- [ ] Mode distribué : Bannière fonctionne correctement

---

## 13. Notes de développement

### 13.1 Ordre d'implémentation recommandé
1. D'abord : Corrections de base (Phase 1) - déjà fait
2. Ensuite : Coche et compteur (Phase 2)
3. Puis : Bannière et highlight (Phase 3)
4. Enfin : API modeler complète (Phase 4)
5. Finalement : Documentation et tests (Phase 5)

### 13.2 Points techniques importants
- Utiliser `QPropertyAnimation` pour animation
- Bannière : widget enfant de SGModel (fenêtre principale)
- Highlight : styles dynamiques via `paintEvent()` ou stylesheet
- Compteur : mise à jour dans `updateText()` appelé à chaque phase

### 13.3 Conventions SGE à respecter
- Toutes les méthodes en anglais
- Organisation selon conventions (SET, GET, etc.)
- Docstrings complètes
- Respect architecture Model-View si applicable

---

## 14. Résumé exécutif

### Problèmes résolus
1. ✅ Fenêtre vide bizarre quand `displayEndGameConditions()` non appelé
2. ✅ Coche ✓ apparaît trop tard (après delay)
3. ✅ Utilisateur non informé du temps restant
4. ✅ Fin de partie pas assez visible

### Solutions apportées
1. ✅ Affichage automatique du widget quand condition détectée
2. ✅ Coche ✓ dès détection + compteur dynamique
3. ✅ Système flexible bannière + highlight + animation
4. ✅ API modeler complète et intuitive

### Impact
- **Breaking changes** : Minimal (renommage méthode, avec alias pour compatibilité)
- **Compatibilité** : Tous les exemples existants fonctionnent
- **Flexibilité** : Modelers peuvent choisir leur affichage préféré
- **UX** : Amélioration significative de la clarté de fin de partie

---

**Document créé le** : Janvier 2025  
**Dernière mise à jour** : Janvier 2025  
**Statut** : Planification complète - Prêt pour implémentation

