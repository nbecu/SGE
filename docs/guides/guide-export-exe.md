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

### Ressources supplémentaires

Pour inclure des fichiers supplémentaires (sons, textures, config), modifiez la classe `SGExeBuilder` :

```python
# Dans SGExeBuilder._generate_spec_file()
datas=[
    ('mainClasses', 'mainClasses'),
    ('icon', 'icon'),
    ('images', 'images'),
    ('mon_jeu/sons', 'sons'),        # Sons personnalisés
    ('mon_jeu/textures', 'textures'), # Textures personnalisées
    ('mon_jeu/config', 'config'),     # Fichiers de config
]
```

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
