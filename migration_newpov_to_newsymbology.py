#!/usr/bin/env python3
"""
Migration helper: Convert newPov() calls to newSymbology()

This script helps identify and document the migration needed from the legacy
POV system to the new symbology system.

Pattern:
OLD:  entity_type.newPov("POV Name", "attribute", dict_colors)
NEW:  entity_type.newSymbology("attribute", dict_colors, name="POV Name")

Usage:
  python migration_newpov_to_newsymbology.py <gamefile>

The script will print out the necessary changes.
"""

import re
import sys

def migrate_file(filepath):
    """Identify POV-to-symbology migrations needed in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern: newPov(...)
    pov_pattern = r'\.newPov\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*(\w+)\s*\)'
    newborderpov_pattern = r'\.newBorderPov\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*(\w+)(?:\s*,\s*([\d.]+))?\s*\)'

    pov_matches = re.finditer(pov_pattern, content)
    border_matches = re.finditer(newborderpov_pattern, content)

    print(f"\n{'=' * 70}")
    print(f"Migration Guide for {filepath}")
    print(f"{'=' * 70}\n")

    migrations = []
    for match in pov_matches:
        pov_name = match.group(1)
        attribute = match.group(2)
        dict_var = match.group(3)
        old_call = match.group(0)
        new_call = f'.newSymbology("{attribute}", {dict_var}, name="{pov_name}")'
        migrations.append((old_call, new_call))
        print(f"[COLOR] {pov_name}")
        print(f"  OLD: {old_call}")
        print(f"  NEW: {new_call}\n")

    for match in border_matches:
        pov_name = match.group(1)
        attribute = match.group(2)
        dict_var = match.group(3)
        border_width = match.group(4) if match.group(4) else "3"
        old_call = match.group(0)
        new_call = f'.newSymbologyWithBorder("{attribute}", {dict_var}, border_width={border_width}, name="{pov_name}")'
        migrations.append((old_call, new_call))
        print(f"[BORDER] {pov_name}")
        print(f"  OLD: {old_call}")
        print(f"  NEW: {new_call}\n")

    return migrations

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migration_newpov_to_newsymbology.py <gamefile>")
        sys.exit(1)

    gamefile = sys.argv[1]
    migrations = migrate_file(gamefile)
    print(f"\nTotal migrations needed: {len(migrations)}")
