# UNIFORMIZE_FONT_STYLES_GAMESPACES.md

## Problème identifié : Hétérogénéité des styles de police dans les GameSpaces

**Date d'analyse** : Décembre 2024

### Contexte
Les classes GameSpaces héritant de `SGGameSpace` n'ont pas une API uniforme pour paramétrer les styles de police, ce qui limite la capacité des modelers à personnaliser l'apparence de leurs interfaces.

### Analyse des classes GameSpaces

#### Classes héritant de SGGameSpace :
1. **SGTextBox** - ✅ Méthode dédiée `setTextFormat(fontName='Verdana', size=12)`
2. **SGUserSelector** - ❌ Police définie uniquement dans `initUI()` pour le titre (`font.setBold(True)`)
3. **SGEndGameRule** - ❌ Police définie uniquement dans `initUI()` pour le titre (`font.setBold(True)`)
4. **SGLegend** - ❌ Utilise `SGLegendItem` pour les polices (pas de méthode directe)
5. **SGDashBoard** - ❌ Pas de méthode de police dédiée
6. **SGControlPanel** - ❌ Pas de méthode de police dédiée
7. **SGProgressGauge** - ❌ Pas de méthode de police dédiée
8. **SGTimeLabel** - ❌ Pas de méthode de police dédiée
9. **SGGrid** - ❌ Pas de méthode de police dédiée
10. **SGVoid** - ❌ Pas de méthode de police dédiée

### Hétérogénéité constatée

#### Méthodes de police disponibles :
- **Seule SGTextBox** a une méthode dédiée `setTextFormat()` pour paramétrer la police du contenu
- **Toutes les autres classes** utilisent des polices par défaut du système ou des polices hardcodées dans `initUI()`
- **Aucune uniformité** dans l'API pour les modelers
- **Pas de méthode commune** dans `SGGameSpace` pour gérer les styles de police

#### Exemples de code actuel :

**SGTextBox (avec méthode dédiée)** :
```python
def setTextFormat(self, fontName='Verdana', size=12):
    font = QFont(fontName, size)
    self.textEdit.setFont(font)
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
- **Les autres GameSpaces** utilisent des polices par défaut non configurables
- **Pas de cohérence visuelle** possible entre les différents éléments d'interface

#### Exemple d'usage souhaité :
```python
# Actuellement impossible pour la plupart des GameSpaces
textBox.setTextFormat("Arial", 14)
userSelector.setTextFormat("Arial", 14)  # ❌ N'existe pas
endGameRule.setTextFormat("Arial", 14)   # ❌ N'existe pas
legend.setTextFormat("Arial", 14)        # ❌ N'existe pas
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
```

#### Architecture proposée :
1. **Méthode commune** dans `SGGameSpace` : `setTextFont()`
2. **Implémentation spécifique** dans chaque classe GameSpace
3. **Compatibilité** avec `SGTextBox.setTextFormat()` existant
4. **Utilisation du système `gs_aspect`** pour la cohérence

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
- Éviter les breaking changes
- Migration progressive possible

### Références
- **FUTURE_PLAN.md** : Chantier ajouté dans "User Interface & Display"
- **Code source** : Analyse effectuée sur toutes les classes GameSpaces
- **Conventions SGE** : Respect des règles de nommage et d'organisation
