#!/usr/bin/env python3
"""
Script pour créer l'exécutable de Sea_Zones_distributed2.py
"""

import subprocess
from mainClasses.SGExeBuilder import SGExeBuilder
from pathlib import Path

# Créer une instance du builder
builder = SGExeBuilder()

# Ajouter les ressources nécessaires (CSV et images)
# Le modèle utilise data/import/sea_zones/ pour les images et le CSV
builder.add_custom_resources([
    ('data/import/sea_zones', 'data/import/sea_zones'),
])

# Créer l'exécutable
try:
    print("=" * 60)
    print("Création de l'exécutable Sea_Zones_distributed2")
    print("=" * 60)
    
    exe_path = builder.build_exe(
        model_path="examples/games/Sea_Zones_distributed2.py",
        output_name="SeaZonesDistributed2"
    )
    
    print("\n" + "=" * 60)
    print(f"[OK] SUCCES ! Executable cree : {exe_path}")
    print("=" * 60)
    
except FileNotFoundError as e:
    print(f"\n[ERREUR] Fichier non trouve - {e}")
    print("Verifiez que le chemin du modele est correct.")
    
except subprocess.CalledProcessError as e:
    print(f"\n[ERREUR] Echec de PyInstaller - {e}")
    print("Verifiez que PyInstaller est installe : pip install pyinstaller")
    
except Exception as e:
    print(f"\n[ERREUR] {e}")
    import traceback
    traceback.print_exc()

