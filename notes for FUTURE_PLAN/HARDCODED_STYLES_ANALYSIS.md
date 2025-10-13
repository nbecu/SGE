# HARDCODED_STYLES_ANALYSIS.md

## Analyse des styles hardcodés dans les classes GameSpaces

**Date d'analyse** : 15/10/2025

### Objectif
Documenter tous les styles hardcodés dans les classes GameSpaces pour définir les styles par défaut lors de l'implémentation du système `gs_aspect`.

### Hiérarchie de priorité des styles
1. **Style défini par le modeler** (via méthodes modeler)
2. **Style défini dans la classe fille** (SGEndGameRule, SGDashBoard, etc.)
3. **Style par défaut de la classe mère** (SGGameSpace)

---

## Classes analysées

### 1. SGGameSpace (classe mère)
**Styles par défaut** :
- `gs_aspect = SGAspect.baseBorder()` (border: solid 1px black)
- `backgroundColor = Qt.gray` (dans constructeur)
- `title1_aspect = SGAspect.title1()` (Arial 14px bold)
- `title2_aspect = SGAspect.title2()` (Arial 12px underline)
- `title3_aspect = SGAspect.title3()` (Georgia 11px bold)
- `text1_aspect = SGAspect.text1()` (Georgia 12px black)
- `text2_aspect = SGAspect.text2()` (Arial 12px black)
- `text3_aspect = SGAspect.text3()` (Georgia 12px italic black)

### 2. SGTextBox
**Styles hardcodés** :
- `setTextFormat(fontName='Verdana', size=12)` par défaut
- `titleAlignment='left'` par défaut
- Utilise déjà le système `gs_aspect`

### 3. SGEndGameRule
**Styles hardcodés** :
- `borderColor=Qt.black` par défaut
- `backgroundColor=Qt.lightGray` par défaut
- `textColor=Qt.black` par défaut
- `font.setBold(True)` pour le titre dans `showEndGameConditions()`
- Utilise déjà le système `gs_aspect` avec méthodes modeler complètes

### 4. SGUserSelector
**Styles hardcodés** :
- `font.setBold(True)` pour le titre dans `initUI()`
- Pas d'utilisation du système `gs_aspect`

### 5. SGLegend
**Styles hardcodés** :
- Utilise `SGLegendItem` pour les polices
- Pas d'utilisation directe du système `gs_aspect`

### 6. SGDashBoard
**Styles hardcodés** :
- Pas de styles hardcodés identifiés
- Pas d'utilisation du système `gs_aspect`

### 7. SGControlPanel
**Styles hardcodés** :
- Pas de styles hardcodés identifiés
- Pas d'utilisation du système `gs_aspect`

### 8. SGProgressGauge
**Styles hardcodés** :
- Pas de styles hardcodés identifiés
- Pas d'utilisation du système `gs_aspect`

### 9. SGTimeLabel
**Styles hardcodés** :
- Pas de styles hardcodés identifiés
- Pas d'utilisation du système `gs_aspect`

### 10. SGGrid
**Styles hardcodés** :
- `frameMargin = 8` (marge de cadre)
- `gap = 3` (espacement entre cellules)
- `size = 30` (taille des cellules)
- Utilise déjà le système `gs_aspect` dans `paintEvent()`
- **ATTENTION** : Classe complexe avec fonctionnalités avancées

### 11. SGVoid
**Styles hardcodés** :
- Pas de styles hardcodés identifiés
- Pas d'utilisation du système `gs_aspect`

---

## Classes non-GameSpaces à analyser

### SGLabel
**Styles disponibles** :
- `textStyle_specs` : Style de texte complet
- `borderStyle_specs` : Style de bordure complet
- `backgroundColor_specs` : Style de fond complet
- `alignement` : Alignement du texte ("Left", "Right", "Center", etc.)
- `fixedWidth`, `fixedHeight` : Dimensions fixes

**Éléments à ajouter à SGAspect** :
- `alignment` : Déjà présent dans SGAspect
- `fixed_width`, `fixed_height` : À ajouter
- `word_wrap` : À ajouter

### SGButton
**Styles disponibles** :
- `background_color='white'` par défaut
- `border_size=1` par défaut
- `border_style='solid'` par défaut
- `border_color='lightgray'` par défaut
- `border_radius=4` par défaut
- `text_color=None` (couleur par défaut du système)
- `font_family=None` (police par défaut du système)
- `font_size=None` (taille par défaut du système)
- `font_weight=None` (poids par défaut du système)
- `min_width=None`, `min_height=None` : Dimensions minimales
- `padding=None` : Espacement interne
- `hover_text_color=None` : Couleur au survol
- `hover_background_color='#c6eff7'` : Fond au survol
- `hover_border_color='#6bd8ed'` : Bordure au survol
- `pressed_color=None` : Couleur au clic
- `disabled_color=None` : Couleur désactivé
- `word_wrap=False` : Retour à la ligne
- `fixed_width=None` : Largeur fixe

**Éléments à ajouter à SGAspect** :
- `border_radius` : À ajouter
- `min_width`, `min_height` : À ajouter
- `padding` : À ajouter
- `hover_text_color`, `hover_background_color`, `hover_border_color` : À ajouter
- `pressed_color`, `disabled_color` : À ajouter
- `word_wrap` : À ajouter
- `background_image` : À ajouter

---

## Recommandations pour l'implémentation

### 1. Extension de SGAspect
Ajouter les éléments manquants identifiés dans SGLabel et SGButton :
- `border_radius`
- `min_width`, `min_height`
- `padding`
- `hover_*` (états de survol)
- `pressed_color`, `disabled_color`
- `word_wrap`
- `background_image`
- `fixed_width`, `fixed_height`

### 2. Styles par défaut à définir
Basés sur l'analyse des styles hardcodés :

**SGEndGameRule** :
- `border_color = Qt.black`
- `background_color = Qt.lightGray`
- `text_color = Qt.black`
- `title_font_weight = 'bold'`

**SGTextBox** :
- `font_family = 'Verdana'`
- `font_size = 12`
- `title_alignment = 'left'`

**SGUserSelector** :
- `title_font_weight = 'bold'`

**SGGrid** :
- `frame_margin = 8`
- `gap = 3`
- `size = 30`

### 3. Priorité d'implémentation
1. **SGGameSpace** : Ajouter méthodes modeler communes
2. **Classes simples** : SGUserSelector, SGDashBoard, SGControlPanel, SGProgressGauge, SGTimeLabel, SGVoid
3. **Classes complexes** : SGLegend, SGGrid (avec précaution)
4. **Classes non-GameSpaces** : SGLabel, SGButton (conversion en GameSpaces)

### 4. Cas particuliers
- **SGGrid** : Classe complexe avec fonctionnalités avancées, traiter avec précaution
- **SGLabel/SGButton** : Conversion en GameSpaces si possible, sinon étendre SGAspect
- **SGLegend** : Utilise SGLegendItem, adapter l'approche

---

## Notes techniques

### Méthodes modeler à implémenter
```python
# Dans SGGameSpace (méthodes communes)
def setBorderColor(self, color):
def setBorderSize(self, size):
def setBackgroundColor(self, color):
def setTextColor(self, color):
def setTitleAlignment(self, alignment):
def setFontFamily(self, font_family):
def setFontSize(self, size):
def setFontWeight(self, weight):
def setFontStyle(self, style):
def setBorderRadius(self, radius):
def setPadding(self, padding):
def setMinWidth(self, width):
def setMinHeight(self, height):
def setWordWrap(self, wrap):
def setBackgroundImage(self, image_path):
```

### Syntaxe modeler proposée
```python
# Style simple
gameSpace.setBorderColor(Qt.red)
gameSpace.setTextColor(Qt.blue)

# Style complet
gameSpace.setStyle({
    'border_color': Qt.red,
    'background_color': Qt.white,
    'text_color': Qt.blue,
    'font_size': 14,
    'font_weight': 'bold'
})

# Style par thème
gameSpace.applyTheme('modern')
gameSpace.applyTheme('minimal')
gameSpace.applyTheme('colorful')
```

### Système de thèmes
```python
# Thèmes prédéfinis
THEMES = {
    'modern': SGAspect.modern(),
    'minimal': SGAspect.minimal(),
    'colorful': SGAspect.colorful(),
    'blue': SGAspect.blue(),
    'green': SGAspect.green(),
    'gray': SGAspect.gray()
}

# Application globale
model.applyThemeToAllGameSpaces('modern')
```
