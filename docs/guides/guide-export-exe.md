# Guide d'export d'exécutables SGE

Ce guide explique comment exporter un modèle SGE sous forme d'exécutable Windows (.exe) autonome.

## Vue d'ensemble

L'export d'exécutable permet de distribuer un modèle SGE sans nécessiter l'installation de Python ou des dépendances sur la machine cible. L'exécutable inclut toutes les dépendances nécessaires.

## Prérequis

- Python 3.x installé
- PyInstaller installé : `pip install pyinstaller`
- Modèle SGE fonctionnel
- Toutes les dépendances SGE installées

## Utilisation rapide

### Méthode 1 : Classe SGExeBuilder (recommandée)

```python
from mainClasses.SGExeBuilder import SGExeBuilder

# Créer une instance du builder
builder = SGExeBuilder()

# Exporter un modèle
builder.build_exe("examples/games/morpion_game.py")

# Avec options personnalisées
builder.build_exe(
    model_path="examples/games/mon_jeu.py",
    output_name="MonJeu",
    icon="mon_jeu/icone.ico"
)
```

### Méthode 2 : Script en ligne de commande

```bash
# Depuis la racine du projet SGE
python -c "from mainClasses.SGExeBuilder import SGExeBuilder; SGExeBuilder().build_exe('examples/games/morpion_game.py')"
```

## Options de personnalisation

### Nom d'exécutable personnalisé

```python
builder.build_exe("mon_jeu.py", output_name="MonSuperJeu")
# Résultat : MonSuperJeu.exe
```

### Icône personnalisée

```python
builder.build_exe("mon_jeu.py", icon="mon_jeu/icone.ico")
```

### Intégrer des fichiers de données dans l'exe

Si votre modèle utilise des fichiers externes (CSV, images, sons, config, etc.), vous devez les inclure dans l'exe et adapter votre code pour qu'il fonctionne à la fois en mode développement et en mode exe.

**Avant de créer l'exe** : vérifiez si votre modèle dépend de fichiers d'import (CSV, images, fichiers de paramètres, etc.). Si oui, ajoutez-les explicitement via `add_custom_resources()` (voir ci-dessous).

#### Étape 1 : Ajouter les fichiers avec `add_custom_resources()`

Utilisez la méthode `add_custom_resources()` pour inclure vos fichiers :

```python
from mainClasses.SGExeBuilder import SGExeBuilder

builder = SGExeBuilder()

# Ajouter des fichiers/dossiers à inclure dans l'exe
# Format: (chemin_source, chemin_destination_dans_exe)
builder.add_custom_resources([
    ('data/import/mon_jeu', 'data/import/mon_jeu'),  # Dossier complet
    ('config/settings.json', 'config'),              # Fichier dans un dossier
    ('sons', 'sons'),                                # Dossier sons
])

# Créer l'exe
builder.build_exe("examples/games/mon_jeu.py", output_name="MonJeu")
```

#### Étape 2 : Adapter les chemins dans votre code

Dans votre script Python, vous devez gérer les chemins différemment selon que vous êtes en mode développement ou en mode exe :

```python
from mainClasses.SGSGE import *

# Utiliser getResourcePath pour gérer dev + exe automatiquement
csv_path = getResourcePath("data/import/mon_jeu/donnees.csv")
images_dir = getResourcePath("data/import/mon_jeu")
config_file = getResourcePath("config/settings.json")
```

**Note** : `getResourcePath()` gère automatiquement le mode exe (`sys._MEIPASS`) et le mode script.


#### Notes importantes

- **Chemins relatifs** : Utilisez toujours des chemins relatifs depuis la racine du projet SGE
- **Structure préservée** : La structure des dossiers est préservée dans l'exe (même hiérarchie)
- **Test** : Testez toujours l'exe pour vérifier que les fichiers sont accessibles
- **Taille** : L'inclusion de fichiers augmente la taille de l'exe

## Structure des fichiers générés

```
SGE/
├── dist/
│   └── MonJeu.exe              # Exécutable final
├── build/                      # Fichiers temporaires
├── MonJeu.spec                 # Fichier de configuration PyInstaller
└── guide-export-exe.md         # Ce guide
```

## Dépendances SGE incluses

L'exécutable inclut automatiquement toutes les dépendances SGE :

- **PyQt5** : Interface graphique
- **matplotlib** : Graphiques et visualisations
- **numpy** : Calculs numériques
- **pandas** : Manipulation de données
- **SQLAlchemy** : Base de données
- **paho-mqtt** : Communication MQTT
- **screeninfo** : Détection d'écrans
- **pyrsistent** : Structures de données
- **openpyxl** : Fichiers Excel
- **pyparsing** : Analyse de texte
- **tzdata** : Fuseaux horaires

## Dépannage

### Erreur "Module not found"

Si vous obtenez une erreur `ModuleNotFoundError`, ajoutez le module manquant dans `SGExeBuilder._get_sge_dependencies()` :

```python
def _get_sge_dependencies(self):
    return [
        # ... dépendances existantes ...
        'nouveau_module',  # Ajouter ici
    ]
```

### Erreur "File not found"

Vérifiez que le chemin du modèle est correct et que tous les fichiers de ressources existent.

### Exécutable trop volumineux

L'exécutable peut faire 100-150 MB. C'est normal car il inclut toutes les dépendances Python et SGE.

## Bonnes pratiques

1. **Testez d'abord** : Vérifiez que votre modèle fonctionne avec Python avant l'export
2. **Nommage** : Utilisez des noms d'exécutable sans espaces ni caractères spéciaux
3. **Ressources** : Organisez vos fichiers de ressources dans des dossiers dédiés
4. **Version** : Testez l'exécutable sur une machine propre (sans Python installé)

## Exemples d'utilisation

### Export basique

```python
from mainClasses.SGExeBuilder import SGExeBuilder

builder = SGExeBuilder()
builder.build_exe("examples/games/morpion_game.py")
# Génère : dist/MorpionGame.exe
```

### Export avec personnalisation

```python
from mainClasses.SGExeBuilder import SGExeBuilder

builder = SGExeBuilder()
builder.build_exe(
    model_path="examples/games/CarbonPolis.py",
    output_name="CarbonPolis",
    icon="icon/carbon_polis.ico"
)
# Génère : dist/CarbonPolis.exe
```

### Export avec fichiers de données

```python
from mainClasses.SGExeBuilder import SGExeBuilder

builder = SGExeBuilder()

# Ajouter les fichiers de données à inclure
builder.add_custom_resources([
    ('data/import/mon_jeu', 'data/import/mon_jeu'),
])

# Créer l'exe
builder.build_exe(
    model_path="examples/games/mon_jeu.py",
    output_name="MonJeu"
)
# Génère : dist/MonJeu.exe avec les fichiers de données inclus
```

### Export en lot

```python
from mainClasses.SGExeBuilder import SGExeBuilder

builder = SGExeBuilder()

# Exporter plusieurs modèles
models = [
    "examples/games/morpion_game.py",
    "examples/games/CarbonPolis.py",
    "examples/games/Solutre_elu.py"
]

for model in models:
    print(f"Export de {model}...")
    builder.build_exe(model)
    print(f"✓ Export terminé")
```

## Support

Pour toute question ou problème :

1. Consultez ce guide
2. Vérifiez les logs de compilation
3. Testez avec un modèle simple (morpion_game.py)
4. Contactez l'équipe de développement SGE

---

*Guide créé le 19 décembre 2024 - Version 1.0*
