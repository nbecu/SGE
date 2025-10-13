# UNIFORMIZE_FONT_STYLES_GAMESPACES.md

## Problème identifié : Hétérogénéité des styles de police et d'alignement dans les GameSpaces

**Date d'analyse** : Décembre 2024

### Contexte
Les classes GameSpaces héritant de `SGGameSpace` n'ont pas une API uniforme pour paramétrer les styles de police et l'alignement des titres, ce qui limite la capacité des modelers à personnaliser l'apparence de leurs interfaces.

### Analyse des classes GameSpaces

#### Classes héritant de SGGameSpace :
1. **SGTextBox** - ✅ Méthode dédiée `setTextFormat(fontName='Verdana', size=12)` + ✅ Paramètre `titleAlignment` dans `newTextBox()`
2. **SGUserSelector** - ❌ Police définie uniquement dans `initUI()` pour le titre (`font.setBold(True)`) + ❌ Pas d'alignement de titre
3. **SGEndGameRule** - ❌ Police définie uniquement dans `initUI()` pour le titre (`font.setBold(True)`) + ❌ Pas d'alignement de titre
4. **SGLegend** - ❌ Utilise `SGLegendItem` pour les polices (pas de méthode directe) + ❌ Pas d'alignement de titre
5. **SGDashBoard** - ❌ Pas de méthode de police dédiée + ❌ Pas d'alignement de titre
6. **SGControlPanel** - ❌ Pas de méthode de police dédiée + ❌ Pas d'alignement de titre
7. **SGProgressGauge** - ❌ Pas de méthode de police dédiée + ❌ Pas d'alignement de titre
8. **SGTimeLabel** - ❌ Pas de méthode de police dédiée + ❌ Pas d'alignement de titre
9. **SGGrid** - ❌ Pas de méthode de police dédiée + ❌ Pas d'alignement de titre
10. **SGVoid** - ❌ Pas de méthode de police dédiée + ❌ Pas d'alignement de titre

### Hétérogénéité constatée

#### Méthodes de police et d'alignement disponibles :
- **Seule SGTextBox** a une méthode dédiée `setTextFormat()` pour paramétrer la police du contenu
- **Seule SGTextBox** a un paramètre `titleAlignment` pour gérer l'alignement du titre ('left', 'center', 'right')
- **Toutes les autres classes** utilisent des polices par défaut du système ou des polices hardcodées dans `initUI()`
- **Toutes les autres classes** n'ont pas de paramètre d'alignement de titre
- **Aucune uniformité** dans l'API pour les modelers
- **Pas de méthode commune** dans `SGGameSpace` pour gérer les styles de police et l'alignement

#### Exemples de code actuel :

**SGTextBox (avec méthode dédiée)** :
```python
def setTextFormat(self, fontName='Verdana', size=12):
    font = QFont(fontName, size)
    self.textEdit.setFont(font)

# Création avec alignement de titre
textBox = model.newTextBox("Text", "Title", titleAlignment='center')
```

**SGUserSelector (police hardcodée)** :
```python
def initUI(self):
    title = QLabel("User Selector")
    font = QFont()
    font.setBold(True)
    title.setFont(font)
```

**SGEndGameRule (police hardcodée)** :
```python
def initUI(self):
    title = QtWidgets.QLabel(self.id)
    font = QFont()
    font.setBold(True)
    title.setFont(font)
```

### Impact pour les modelers

#### Limitations actuelles :
- **Impossible de paramétrer uniformément** la taille de police des GameSpaces
- **Seule la TextBox** permet de changer la police via `setTextFormat()`
- **Seule la TextBox** permet de paramétrer l'alignement du titre via `titleAlignment`
- **Les autres GameSpaces** utilisent des polices par défaut non configurables
- **Les autres GameSpaces** n'ont pas de paramètre d'alignement de titre
- **Pas de cohérence visuelle** possible entre les différents éléments d'interface

#### Exemple d'usage souhaité :
```python
# Actuellement impossible pour la plupart des GameSpaces
textBox.setTextFormat("Arial", 14)
textBox = model.newTextBox("Text", "Title", titleAlignment='center')

userSelector.setTextFormat("Arial", 14)  # ❌ N'existe pas
userSelector = model.newUserSelector(titleAlignment='center')  # ❌ N'existe pas

endGameRule.setTextFormat("Arial", 14)   # ❌ N'existe pas
endGameRule = model.newEndGameRule(titleAlignment='center')    # ❌ N'existe pas

legend.setTextFormat("Arial", 14)        # ❌ N'existe pas
legend = model.newLegend(titleAlignment='center')              # ❌ N'existe pas
```

### Solution proposée

#### API uniforme à implémenter :
```python
def setTextFont(self, fontName='Verdana', size=12, weight='normal', style='normal'):
    """
    Set text font for GameSpace elements.
    
    Args:
        fontName (str): Font family name
        size (int): Font size in pixels
        weight (str): Font weight ('normal', 'bold', etc.)
        style (str): Font style ('normal', 'italic', etc.)
    """

def setTitleAlignment(self, alignment='left'):
    """
    Set title alignment for GameSpace elements.
    
    Args:
        alignment (str): Title alignment ('left', 'center', 'right')
    """
```

#### Architecture proposée :
1. **Méthode commune** dans `SGGameSpace` : `setTextFont()` et `setTitleAlignment()`
2. **Implémentation spécifique** dans chaque classe GameSpace
3. **Compatibilité** avec `SGTextBox.setTextFormat()` et `titleAlignment` existants
4. **Utilisation du système `gs_aspect`** pour la cohérence
5. **Paramètres d'alignement** dans toutes les méthodes `new*()` de `SGModel`

#### Fichiers à modifier :
- `mainClasses/SGGameSpace.py` (méthode commune)
- `mainClasses/SGTextBox.py` (adapter `setTextFormat()`)
- `mainClasses/SGUserSelector.py`
- `mainClasses/SGEndGameRule.py`
- `mainClasses/SGLegend.py`
- `mainClasses/SGDashBoard.py`
- `mainClasses/SGControlPanel.py`
- `mainClasses/SGProgressGauge.py`
- `mainClasses/SGTimeLabel.py`
- `mainClasses/SGGrid.py`
- `mainClasses/SGVoid.py`

### Bénéfices attendus

#### Pour les modelers :
- **API uniforme** pour tous les GameSpaces
- **Personnalisation complète** des styles de police
- **Contrôle de l'alignement** des titres pour tous les GameSpaces
- **Cohérence visuelle** dans les interfaces
- **Meilleure ergonomie** de développement

#### Pour les développeurs :
- **Code plus maintenable** avec une approche commune
- **Réduction de la duplication** de code
- **Extension facilitée** pour de nouveaux GameSpaces

### Notes techniques

#### Système `gs_aspect` existant :
- `SGGameSpace` possède déjà `text1_aspect`, `text2_aspect`, `text3_aspect`
- Ces aspects peuvent être utilisés pour la cohérence des styles
- Intégration possible avec le système de thèmes prévu

#### Compatibilité :
- Maintenir la méthode `setTextFormat()` de `SGTextBox`
- Maintenir le paramètre `titleAlignment` dans `newTextBox()`
- Éviter les breaking changes
- Migration progressive possible

### Références
- **FUTURE_PLAN.md** : Chantier ajouté dans "User Interface & Display"
- **Code source** : Analyse effectuée sur toutes les classes GameSpaces
- **Conventions SGE** : Respect des règles de nommage et d'organisation
