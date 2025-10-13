# UNIFORMIZE_FONT_STYLES_GAMESPACES.md

## Problème identifié : Complétion du système gs_aspect dans les GameSpaces

**Date d'analyse** : Décembre 2024 (mise à jour)

### Contexte
Le système `gs_aspect` (SGAspect) existe déjà dans SGE et est partiellement implémenté dans les classes GameSpaces. Il faut compléter l'implémentation pour uniformiser l'API des modelers et remplacer les polices hardcodées par le système `gs_aspect`.

### État actuel du système gs_aspect

#### Système SGAspect existant :
- **SGAspect** : Classe avec styles prédéfinis (`title1()`, `text1()`, `success()`, `inactive()`, etc.)
- **SGGameSpace** : Système `gs_aspect` déjà implémenté avec `title1_aspect`, `text1_aspect`, etc.
- **Méthodes communes** : `setTitlesAndTextsColor()`, `setTitlesColor()`, `setTextsColor()`

#### Classes héritant de SGGameSpace :
1. **SGTextBox** - ✅ Méthode dédiée `setTextFormat()` + ✅ Paramètre `titleAlignment` + ✅ Utilise `gs_aspect`
2. **SGEndGameRule** - ✅ Méthodes modeler complètes (`setBorderColor()`, `setTextColor()`, etc.) + ✅ Utilise `gs_aspect`
3. **SGUserSelector** - ❌ Police hardcodée dans `initUI()` + ❌ Pas d'alignement de titre + ❌ Pas de méthodes modeler
4. **SGLegend** - ❌ Utilise `SGLegendItem` pour les polices + ❌ Pas d'alignement de titre + ❌ Pas de méthodes modeler
5. **SGDashBoard** - ❌ Pas de méthodes modeler + ❌ Pas d'alignement de titre + ❌ Pas d'utilisation `gs_aspect`
6. **SGControlPanel** - ❌ Pas de méthodes modeler + ❌ Pas d'alignement de titre + ❌ Pas d'utilisation `gs_aspect`
7. **SGProgressGauge** - ❌ Pas de méthodes modeler + ❌ Pas d'alignement de titre + ❌ Pas d'utilisation `gs_aspect`
8. **SGTimeLabel** - ❌ Pas de méthodes modeler + ❌ Pas d'alignement de titre + ❌ Pas d'utilisation `gs_aspect`
9. **SGGrid** - ❌ Pas de méthodes modeler + ❌ Pas d'alignement de titre + ❌ Pas d'utilisation `gs_aspect`
10. **SGVoid** - ❌ Pas de méthodes modeler + ❌ Pas d'alignement de titre + ❌ Pas d'utilisation `gs_aspect`

### Travail restant à faire

#### Système gs_aspect partiellement implémenté :
- **SGTextBox** et **SGEndGameRule** : ✅ Utilisent déjà le système `gs_aspect` avec méthodes modeler complètes
- **8 autres classes** : ❌ N'utilisent pas encore le système `gs_aspect` et ont des polices hardcodées
- **API incohérente** : Seules 2 classes sur 10 ont des méthodes modeler pour la personnalisation
- **Polices hardcodées** : La plupart des classes définissent encore les polices dans `initUI()`
- **Pas d'alignement uniforme** : Seule SGTextBox a un paramètre `titleAlignment`

#### Exemples de code actuel :

**SGTextBox (système gs_aspect)** :
```python
def setTextFormat(self, fontName='Verdana', size=12):
    font = QFont(fontName, size)
    self.textEdit.setFont(font)

# Création avec alignement de titre
textBox = model.newTextBox("Text", "Title", titleAlignment='center')
```

**SGEndGameRule (système gs_aspect)** :
```python
# Utilise le système gs_aspect
self.gs_aspect.border_color = borderColor
self.gs_aspect.background_color = backgroundColor
self.setTitlesAndTextsColor(textColor)

# Méthodes modeler disponibles
endGameRule.setBorderColor(Qt.red)
endGameRule.setTextColor(Qt.blue)
endGameRule.setBackgroundColor(Qt.white)
```

**SGUserSelector (police hardcodée - À CORRIGER)** :
```python
def initUI(self):
    title = QLabel("User Selector")
    font = QFont()
    font.setBold(True)
    title.setFont(font)  # ❌ Devrait utiliser gs_aspect
```

### Impact pour les modelers

#### Limitations actuelles :
- **API incohérente** : Seules SGTextBox et SGEndGameRule ont des méthodes modeler complètes
- **8 classes sur 10** n'ont pas de méthodes pour personnaliser les styles
- **Polices hardcodées** dans la plupart des classes GameSpaces
- **Pas d'alignement uniforme** : Seule SGTextBox a un paramètre `titleAlignment`
- **Pas de cohérence visuelle** possible entre tous les éléments d'interface

#### Exemple d'usage souhaité :
```python
# Actuellement possible pour SGTextBox et SGEndGameRule
textBox.setTextFormat("Arial", 14)
textBox = model.newTextBox("Text", "Title", titleAlignment='center')

endGameRule.setBorderColor(Qt.red)
endGameRule.setTextColor(Qt.blue)
endGameRule.setBackgroundColor(Qt.white)

# Actuellement impossible pour les autres GameSpaces
userSelector.setBorderColor(Qt.red)      # ❌ N'existe pas
userSelector = model.newUserSelector(titleAlignment='center')  # ❌ N'existe pas

legend.setBorderColor(Qt.red)           # ❌ N'existe pas
legend = model.newLegend(titleAlignment='center')              # ❌ N'existe pas

dashboard.setTextColor(Qt.blue)          # ❌ N'existe pas
dashboard = model.newDashBoard(titleAlignment='center')        # ❌ N'existe pas
```

### Solution proposée

#### Compléter le système gs_aspect existant :
```python
# Étendre les méthodes modeler existantes à toutes les classes GameSpaces
def setBorderColor(self, color):
    """Set the border color using gs_aspect system."""
    self.gs_aspect.border_color = color

def setBorderSize(self, size):
    """Set the border size using gs_aspect system."""
    self.gs_aspect.border_size = size

def setBackgroundColor(self, color):
    """Set the background color using gs_aspect system."""
    self.gs_aspect.background_color = color

def setTextColor(self, color):
    """Set the text color using gs_aspect system."""
    self.setTitlesAndTextsColor(color)

def setTitleAlignment(self, alignment='left'):
    """Set title alignment for GameSpace elements."""
    # À implémenter selon les besoins
```

#### Architecture proposée :
1. **Utiliser le système `gs_aspect` existant** au lieu d'en créer un nouveau
2. **Étendre les méthodes modeler** de SGEndGameRule à toutes les classes GameSpaces
3. **Remplacer les polices hardcodées** par l'utilisation de `gs_aspect`
4. **Maintenir la compatibilité** avec `SGTextBox.setTextFormat()` existant
5. **Ajouter `setTitleAlignment()`** si nécessaire pour l'uniformité

#### Fichiers à modifier :
- `mainClasses/SGGameSpace.py` (ajouter méthodes communes si nécessaire)
- `mainClasses/SGTextBox.py` (déjà OK, maintenir compatibilité)
- `mainClasses/SGEndGameRule.py` (déjà OK, servir de modèle)
- `mainClasses/SGUserSelector.py` (ajouter méthodes modeler + remplacer polices hardcodées)
- `mainClasses/SGLegend.py` (ajouter méthodes modeler + remplacer polices hardcodées)
- `mainClasses/SGDashBoard.py` (ajouter méthodes modeler + remplacer polices hardcodées)
- `mainClasses/SGControlPanel.py` (ajouter méthodes modeler + remplacer polices hardcodées)
- `mainClasses/SGProgressGauge.py` (ajouter méthodes modeler + remplacer polices hardcodées)
- `mainClasses/SGTimeLabel.py` (ajouter méthodes modeler + remplacer polices hardcodées)
- `mainClasses/SGGrid.py` (ajouter méthodes modeler + remplacer polices hardcodées)
- `mainClasses/SGVoid.py` (ajouter méthodes modeler + remplacer polices hardcodées)

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

#### Système `gs_aspect` existant (déjà implémenté) :
- **SGAspect** : Classe avec styles prédéfinis (`title1()`, `text1()`, `success()`, `inactive()`, etc.)
- **SGGameSpace** : Possède déjà `gs_aspect`, `title1_aspect`, `text1_aspect`, `text2_aspect`, `text3_aspect`
- **Méthodes communes** : `setTitlesAndTextsColor()`, `setTitlesColor()`, `setTextsColor()`
- **SGEndGameRule** : Utilise déjà `gs_aspect` avec `paintEvent()` et méthodes modeler complètes
- **Intégration** : Système prêt pour le système de thèmes prévu dans FUTURE_PLAN.md

#### Compatibilité :
- **Maintenir** la méthode `setTextFormat()` de `SGTextBox`
- **Maintenir** le paramètre `titleAlignment` dans `newTextBox()`
- **Éviter** les breaking changes
- **Migration progressive** : Étendre le système existant plutôt que d'en créer un nouveau

### Références
- **FUTURE_PLAN.md** : Chantier "Uniformize font style management across all GameSpaces classes"
- **SGAspect.py** : Système d'aspects existant avec styles prédéfinis
- **SGGameSpace.py** : Classe de base avec système `gs_aspect` implémenté
- **SGEndGameRule.py** : Exemple d'implémentation complète du système `gs_aspect`
- **Conventions SGE** : Respect des règles de nommage et d'organisation
