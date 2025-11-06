#!/usr/bin/env python3
"""
Script Python pour convertir Mermaid en images
Utilise requests + mermaid.live API
"""

import requests
import base64
import json
import os
import sys
import re

def mermaid_to_image_python(mermaid_code, output_path, format='png'):
    """
    Convertit du code Mermaid en image via l'API mermaid.live
    """
    try:
        # Encoder le code Mermaid en base64
        encoded_code = base64.b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        
        # URL de l'API mermaid.live
        api_url = f"https://mermaid.ink/img/{encoded_code}"
        
        if format == 'svg':
            api_url = f"https://mermaid.ink/svg/{encoded_code}"
        
        # Télécharger l'image
        response = requests.get(api_url)
        response.raise_for_status()
        
        # Sauvegarder l'image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Diagramme sauvegardé : {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

def extract_mermaid_from_md(md_file):
    """
    Extrait le code Mermaid d'un fichier Markdown
    """
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Trouver les blocs mermaid
        pattern = r'```mermaid\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        return matches
    except Exception as e:
        print(f"❌ Erreur lecture fichier : {e}")
        return []

def convert_md_to_images(md_file, output_dir="images"):
    """
    Convertit tous les diagrammes Mermaid d'un fichier MD en images
    """
    # Créer le dossier de sortie
    os.makedirs(output_dir, exist_ok=True)
    
    # Extraire les codes Mermaid
    mermaid_codes = extract_mermaid_from_md(md_file)
    
    if not mermaid_codes:
        print("❌ Aucun diagramme Mermaid trouvé")
        return
    
    print(f"📊 {len(mermaid_codes)} diagramme(s) trouvé(s)")
    
    # Convertir chaque diagramme
    for i, mermaid_code in enumerate(mermaid_codes, 1):
        # Noms de fichiers
        base_name = os.path.splitext(os.path.basename(md_file))[0]
        png_file = os.path.join(output_dir, f"{base_name}_diagram_{i}.png")
        svg_file = os.path.join(output_dir, f"{base_name}_diagram_{i}.svg")
        
        print(f"🔄 Conversion diagramme {i}...")
        
        # Convertir en PNG
        if mermaid_to_image_python(mermaid_code, png_file, 'png'):
            print(f"   📄 PNG : {png_file}")
        
        # Convertir en SVG
        if mermaid_to_image_python(mermaid_code, svg_file, 'svg'):
            print(f"   🎨 SVG : {svg_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mermaid_converter.py <input.md> [output_dir]")
        print("Exemple: python mermaid_converter.py docs/architecture/sge_classes_overview.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "images"
    
    if not os.path.exists(input_file):
        print(f"❌ Fichier non trouvé : {input_file}")
        sys.exit(1)
    
    print(f"📁 Fichier : {input_file}")
    print(f"📁 Sortie : {output_dir}")
    
    convert_md_to_images(input_file, output_dir)
