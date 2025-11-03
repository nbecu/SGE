# Factory Methods - Paramètres de Style

**Date** : [Date actuelle]  
**Status** : Toutes les factory methods passent maintenant par `gs_aspect` via les setters

---

## Liste des Factory Methods avec Paramètres de Style

### 1. `newTimeLabel()`
**GameSpace** : `SGTimeLabel`

**Paramètres de style disponibles** :
- `backgroundColor` (Qt.Color, default: `Qt.white`) : Couleur de fond
- `borderColor` (Qt.Color, default: `Qt.black`) : Couleur de la bordure
- `textColor` (Qt.Color, default: `Qt.black`) : Couleur du texte

**Exemple** :
```python
# Option A : Paramètres dans constructeur
timeLabel = myModel.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.cyan, borderColor=Qt.blue)

# Option B : Méthodes modeler
timeLabel = myModel.newTimeLabel("Game Time")
timeLabel.setBackgroundColor(Qt.cyan)
timeLabel.setTextColor(Qt.cyan)
timeLabel.setBorderColor(Qt.blue)
```

---

### 2. `newDashBoard()`
**GameSpace** : `SGDashBoard`

**Paramètres de style disponibles** :
- `borderColor` (Qt.Color, default: `Qt.black`) : Couleur de la bordure
- `borderSize` (int, default: `1`) : Taille de la bordure en pixels
- `backgroundColor` (QColor, default: `QColor(230, 230, 230)`) : Couleur de fond
- `textColor` (Qt.Color, default: `Qt.black`) : Couleur du texte
- `layout` (str, default: `'vertical'`) : Orientation du layout ('vertical' ou 'horizontal')

**Exemple** :
```python
# Option A : Paramètres dans constructeur
dashboard = myModel.newDashBoard("Dashboard", borderColor=Qt.red, borderSize=2, backgroundColor=Qt.yellow, textColor=Qt.black)

# Option B : Méthodes modeler
dashboard = myModel.newDashBoard("Dashboard")
dashboard.setBorderColor(Qt.red)
dashboard.setBorderSize(2)
dashboard.setBackgroundColor(Qt.yellow)
dashboard.setTextColor(Qt.black)
```

---

### 3. `newEndGameRule()`
**GameSpace** : `SGEndGameRule`

**Paramètres de style disponibles** :
- `borderColor` (QColor, default: `Qt.black`) : Couleur de la bordure
- `backgroundColor` (QColor, default: `Qt.lightGray`) : Couleur de fond
- `textColor` (QColor, default: `Qt.black`) : Couleur du texte
- `layout` (str, default: `"vertical"`) : Orientation du layout ('vertical' ou 'horizontal')

**Autres paramètres** (non-style) :
- `title` (str, default: `'EndGame Rules'`) : Titre affiché
- `numberRequired` (int, default: `1`) : Nombre de conditions requises
- `displayRefresh` (str, default: `'instantaneous'`) : Mode de rafraîchissement
- `isDisplay` (bool, default: `True`) : Affichage ou non

**Exemple** :
```python
# Option A : Paramètres dans constructeur
endGameRule = myModel.newEndGameRule("Rules", 1, borderColor=Qt.green, backgroundColor=Qt.white, textColor=Qt.green)

# Option B : Méthodes modeler
endGameRule = myModel.newEndGameRule("Rules", 1)
endGameRule.setBorderColor(Qt.green)
endGameRule.setBackgroundColor(Qt.white)
endGameRule.setTextColor(Qt.green)
```

---

### 4. `newProgressGauge()`
**GameSpace** : `SGProgressGauge`

**Paramètres de style disponibles** :
- `borderColor` (QColor ou Qt.GlobalColor, default: `Qt.black`) : Couleur de la bordure
- `backgroundColor` (QColor ou Qt.GlobalColor, default: `Qt.white`) : Couleur de fond

**Autres paramètres** (non-style) :
- `simVar` (object) : Variable de simulation à surveiller
- `minimum` (float/int, default: `0`) : Valeur minimale
- `maximum` (float/int, default: `100`) : Valeur maximale
- `title` (str, optional) : Titre affiché
- `orientation` (str, default: `"horizontal"`) : 'horizontal' ou 'vertical'
- `colorRanges` (list of tuple, optional) : Règles de couleur dynamiques
- `unit` (str, default: `""`) : Unité affichée
- `bar_width` (int/float/str, default: `25`) : Largeur de la barre
- `bar_length` (int, optional) : Longueur de la barre
- `title_position` (str, default: `'above'`) : 'above' ou 'below'
- `display_value_on_top` (bool, default: `True`) : Afficher la valeur au-dessus

**Exemple** :
```python
# Option A : Paramètres dans constructeur
gauge = myModel.newProgressGauge(simVar, 0, 100, "Progress", borderColor=Qt.red, backgroundColor=Qt.lightGray)

# Option B : Méthodes modeler
gauge = myModel.newProgressGauge(simVar, 0, 100, "Progress")
gauge.setBorderColor(Qt.red)
gauge.setBackgroundColor(Qt.lightGray)
```

---

### 5. `newTextBox()`
**GameSpace** : `SGTextBox`

**Paramètres de style disponibles** :
- `borderColor` (QColor, default: `Qt.black`) : Couleur de la bordure
- `backgroundColor` (QColor, default: `Qt.lightGray`) : Couleur de fond
- `titleAlignment` (str, default: `'left'`) : Alignement du titre ('left', 'center', 'right')

**Autres paramètres** (non-style) :
- `textToWrite` (str, default: `'Welcome in the game !'`) : Texte à afficher
- `title` (str, default: `'Text Box'`) : Titre affiché
- `width` (int, optional) : Largeur en pixels
- `height` (int, optional) : Hauteur en pixels
- `shrinked` (bool, default: `True`) : Ajustement automatique de la taille

**Exemple** :
```python
# Option A : Paramètres dans constructeur
textBox = myModel.newTextBox("Texte", "Title", 200, 150, borderColor=Qt.green, backgroundColor=Qt.lightGreen, titleAlignment='center')

# Option B : Méthodes modeler
textBox = myModel.newTextBox("Texte", "Title", 200, 150)
textBox.setBorderColor(Qt.green)
textBox.setBackgroundColor(Qt.lightGreen)
textBox.setTitleAlignment('center')
```

---

### 6. `newLabel()`
**GameSpace** : `SGLabel`

**Paramètres de style disponibles** :
- `textStyle_specs` (str, default: `""`) : Spécifications CSS pour le style du texte (font, size, color, etc.)
- `borderStyle_specs` (str, default: `""`) : Spécifications CSS pour le style de la bordure
- `backgroundColor_specs` (str, default: `""`) : Spécifications CSS pour la couleur de fond
- `alignement` (str, default: `"Left"`) : Alignement du texte

**Autres paramètres** :
- `text` (str) : Texte à afficher
- `position` (tuple, optional) : Coordonnées (x, y)
- `fixedWidth` (float, optional) : Largeur fixe en pixels
- `fixedHeight` (float, optional) : Hauteur fixe en pixels

**Note** : Cette méthode utilise des spécifications CSS (legacy). Pour une approche moderne via `gs_aspect`, utilisez les méthodes modeler après création.

**Exemple** :
```python
# Legacy (CSS specs)
label = myModel.newLabel("Text", position=(10, 10), 
                         textStyle_specs="color: red; font-size: 14px;",
                         borderStyle_specs="border: 1px solid black;",
                         backgroundColor_specs="background-color: yellow;")

# Moderne (Option B via méthodes modeler)
label = myModel.newLabel("Text", position=(10, 10))
label.setTextColor(Qt.red)
label.setFontSize(14)
label.setBorderColor(Qt.black)
label.setBorderSize(1)
label.setBackgroundColor(Qt.yellow)
```

---

### 7. `newLabel_stylised()`
**GameSpace** : `SGLabel`

**Paramètres de style disponibles** :
- `font` (str, optional) : Famille de police
- `size` (int, optional) : Taille de police en pixels
- `color` (str, optional) : Couleur du texte (nom, hex, RGB, RGBA)
- `text_decoration` (str, default: `"none"`) : Décoration du texte ('none', 'underline', 'overline', 'line-through', 'blink')
- `font_weight` (str, default: `"normal"`) : Poids de la police
- `font_style` (str, default: `"normal"`) : Style de la police ('normal', 'italic', 'oblique')
- `alignement` (str, default: `"Left"`) : Alignement du texte
- `border_style` (str, default: `"solid"`) : Style de la bordure
- `border_size` (int, default: `0`) : Taille de la bordure en pixels
- `border_color` (str, optional) : Couleur de la bordure
- `background_color` (str, optional) : Couleur de fond

**Autres paramètres** :
- `text` (str) : Texte à afficher
- `position` (tuple) : Coordonnées (x, y)
- `fixedWidth` (float, optional) : Largeur fixe
- `fixedHeight` (float, optional) : Hauteur fixe

**Note** : Cette méthode est marquée comme potentiellement obsolète (`#todo: could be obsolete`). Utilisez `newLabel()` + méthodes modeler pour une approche moderne.

---

### 8. `newButton()`
**GameSpace** : `SGButton`

**Paramètres de style disponibles** :
- `background_color` (str, default: `'white'`) : Couleur de fond (nom, hex, RGB, RGBA)
- `background_image` (str, optional) : Chemin vers l'image de fond
- `border_size` (int, default: `1`) : Taille de la bordure en pixels
- `border_color` (str, default: `'lightgray'`) : Couleur de la bordure
- `border_style` (str, default: `'solid'`) : Style de la bordure
- `border_radius` (int, default: `5`) : Rayon des coins arrondis en pixels
- `text_color` (str, optional) : Couleur du texte
- `font_family` (str, optional) : Famille de police
- `font_size` (int, optional) : Taille de police en pixels
- `font_weight` (str, optional) : Poids de la police ('normal', 'bold', '100'-'900')
- `min_width` (int, optional) : Largeur minimale en pixels
- `min_height` (int, optional) : Hauteur minimale en pixels
- `padding` (int, default: `2`) : Padding interne en pixels
- `hover_text_color` (str, optional) : Couleur du texte au survol
- `hover_background_color` (str, default: `'#c6eff7'`) : Couleur de fond au survol
- `hover_border_color` (str, default: `'#6bd8ed'`) : Couleur de bordure au survol
- `pressed_color` (str, optional) : Couleur quand pressé
- `disabled_color` (str, optional) : Couleur quand désactivé
- `word_wrap` (bool, default: `False`) : Retour à la ligne automatique
- `fixed_width` (int, optional) : Largeur fixe

**Autres paramètres** :
- `method` (lambda function | SGAbstractAction) : Méthode à exécuter au clic
- `text` (str) : Texte du bouton
- `position` (tuple, optional) : Coordonnées (x, y)

**Exemple** :
```python
# Option A : Paramètres dans constructeur
button = myModel.newButton(lambda: print("Click"), "Click me", 
                           background_color='blue', border_color='darkblue', 
                           text_color='white', border_radius=10)

# Option B : Méthodes modeler
button = myModel.newButton(lambda: print("Click"), "Click me")
button.setBackgroundColor('blue')
button.setBorderColor('darkblue')
button.setTextColor('white')
button.setBorderRadius(10)
```

---

### 9. `newVoid()`
**GameSpace** : `SGVoid`

**Paramètres de style disponibles** :
- ❌ **Aucun paramètre de style dans le constructeur**

**Autres paramètres** :
- `name` (str) : Nom du widget void
- `sizeX` (int, default: `200`) : Largeur en pixels
- `sizeY` (int, default: `200`) : Hauteur en pixels

**Note** : Les styles peuvent être appliqués via les méthodes modeler après création.

**Exemple** :
```python
void = myModel.newVoid("Void1", 200, 200)
void.setBackgroundColor(Qt.gray)
void.setBorderColor(Qt.black)
void.setBorderSize(1)
```

---

### 10. `newLegend()`
**GameSpace** : `SGLegend`

**Paramètres de style disponibles** :
- ❌ **Aucun paramètre de style dans le constructeur**

**Autres paramètres** :
- `name` (str, default: `'Legend'`) : Nom de la légende
- `alwaysDisplayDefaultAgentSymbology` (bool, default: `False`) : Afficher la symbologie par défaut des agents

**Note** : Les styles peuvent être appliqués via les méthodes modeler après création.

**Exemple** :
```python
legend = myModel.newLegend("My Legend")
legend.setBackgroundColor(Qt.white)
legend.setBorderColor(Qt.black)
legend.setBorderSize(1)
```

---

### 11. `newUserSelector()`
**GameSpace** : `SGUserSelector`

**Paramètres de style disponibles** :
- ❌ **Aucun paramètre de style dans le constructeur**

**Autres paramètres** :
- `customListOfUsers` (list, optional) : Liste personnalisée d'utilisateurs
- `orientation` (str, default: `'horizontal'`) : Orientation du layout ('horizontal' ou 'vertical')

**Note** : Les styles peuvent être appliqués via les méthodes modeler après création.

**Exemple** :
```python
userSelector = myModel.newUserSelector(orientation='vertical')
userSelector.setBackgroundColor(Qt.lightGray)
userSelector.setBorderColor(Qt.black)
```

---

### 12. `newCellsOnGrid()` / Grid
**GameSpace** : `SGGrid`

**Paramètres de style disponibles** :
- `color` (Qt.Color, default: `Qt.gray`) : Couleur de fond de la grille
- `backGroundImage` (str, optional) : Chemin vers l'image de fond

**Autres paramètres** :
- `columns` (int, default: `10`) : Nombre de colonnes
- `rows` (int, default: `10`) : Nombre de lignes
- `format` / `cellShape` (str, default: `"square"`) : Forme des cellules
- `size` (int, default: `30`) : Taille des cellules
- `gap` (int, default: `0`) : Espacement entre cellules
- `moveable` (bool, default: `True`) : Peut être déplacé
- `name` (str, optional) : Nom de la grille
- `defaultCellImage` (str, optional) : Image par défaut des cellules
- `neighborhood` (str, default: `'moore'`) : Type de voisinage
- `boundaries` (str, default: `'open'`) : Conditions aux limites

**Note** : Pour les styles de bordure, utilisez les méthodes modeler après création.

**Exemple** :
```python
grid = myModel.newCellsOnGrid(8, 8, "square", size=40, gap=2, color=Qt.green, backGroundImage="path/to/image.png")
grid.setBorderColor(Qt.black)
grid.setBorderSize(2)
```

---

### 13. `newControlPanel()` (via Player)
**GameSpace** : `SGControlPanel`

**Note** : Cette méthode est appelée via `Player.newControlPanel()`, pas directement via `SGModel`.

**Paramètres de style disponibles** :
- ❌ **Aucun paramètre de style dans le constructeur**

**Autres paramètres** :
- `title` (str) : Titre du panneau de contrôle

**Note** : Les styles peuvent être appliqués via les méthodes modeler après création.

**Exemple** :
```python
player = myModel.newPlayer("Player 1", {})
controlPanel = player.newControlPanel("Actions")
controlPanel.setBackgroundColor(Qt.lightBlue)
controlPanel.setBorderColor(Qt.darkBlue)
```

---

## Résumé des Paramètres de Style par Catégorie

### Paramètres de Container (background, border)
- `backgroundColor` / `background_color` : Couleur de fond
- `background_image` / `backGroundImage` : Image de fond
- `borderColor` / `border_color` : Couleur de bordure
- `borderSize` / `border_size` : Taille de bordure
- `border_style` : Style de bordure ('solid', 'dotted', 'dashed', etc.)
- `border_radius` : Rayon des coins arrondis

### Paramètres de Texte
- `textColor` / `text_color` : Couleur du texte
- `font` / `font_family` : Famille de police
- `font_size` / `size` : Taille de police
- `font_weight` : Poids de police
- `font_style` : Style de police
- `text_decoration` : Décoration du texte

### Paramètres de Layout/Dimensions
- `min_width` : Largeur minimale
- `min_height` : Hauteur minimale
- `padding` : Padding interne
- `width` : Largeur fixe
- `height` : Hauteur fixe
- `fixed_width` : Largeur fixe
- `fixedHeight` : Hauteur fixe

### Paramètres Hover/États (Button uniquement)
- `hover_text_color` : Couleur texte au survol
- `hover_background_color` : Couleur fond au survol
- `hover_border_color` : Couleur bordure au survol
- `pressed_color` : Couleur quand pressé
- `disabled_color` : Couleur quand désactivé

---

## Notes Importantes

1. **Double syntaxe** : Toutes les factory methods supportent maintenant les deux syntaxes (Option A et Option B)
2. **Passage par `gs_aspect`** : Tous les paramètres de style passent maintenant par les setters qui utilisent `gs_aspect`
3. **Méthodes modeler disponibles** : Après création, vous pouvez utiliser toutes les méthodes modeler de `SGGameSpace` :
   - `setBackgroundColor()`, `setBorderColor()`, `setBorderSize()`, `setTextColor()`, etc.
   - `applyTheme()`, `setStyle()`, etc.
4. **GameSpaces sans paramètres de style** : `newVoid()`, `newLegend()`, `newUserSelector()` n'ont pas de paramètres de style dans le constructeur, mais supportent les méthodes modeler
5. **Legacy methods** : `newLabel()` et `newLabel_stylised()` utilisent encore des spécifications CSS (legacy), mais peuvent être stylisés via les méthodes modeler après création

---

## Prochaines Étapes

- [ ] Harmoniser `newLabel()` et `newLabel_stylised()` pour utiliser les paramètres de style standardisés
- [ ] Ajouter des paramètres de style à `newVoid()`, `newLegend()`, `newUserSelector()` si nécessaire
- [ ] Documenter les méthodes modeler disponibles pour chaque GameSpace

