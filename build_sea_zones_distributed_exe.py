#!/usr/bin/env python3
"""
Script pour créer l'exécutable de Sea Zones Distributed (distant broker)
avec les fichiers de données inclus.
"""

from mainClasses.SGExeBuilder import SGExeBuilder
from pathlib import Path

# Créer une instance du builder
builder = SGExeBuilder()

# Ajouter les fichiers de données de sea_zones
# Format: (chemin_source, chemin_destination_dans_exe)
builder.add_custom_resources([
    ('data/import/sea_zones', 'data/import/sea_zones'),
])

# Créer l'exécutable
try:
    exe_path = builder.build_exe(
        model_path="examples/games/Sea_Zones_distributed_distant_broker.py",
        output_name="SeaZonesDistributedDistantBroker",
        clean=True
    )
    print(f"\n✓ Succès ! Exécutable créé : {exe_path}")
    print(f"  Les fichiers de data/import/sea_zones sont inclus dans l'exe.")
except Exception as e:
    print(f"\n✗ Erreur lors de la création de l'exe : {e}")
    import traceback
    traceback.print_exc()
