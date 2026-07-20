#!/usr/bin/env python3
"""Re-apply fix_dots to index/catalog JSON trees."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))
from fix_syriac_dots import process_index

ROOT = Path(__file__).resolve().parents[1]

for name in ("index.json", "psalms_index.json", "catalog.json"):
    path = ROOT / "data" / name
    if process_index(path):
        print(f"Fixed {path}")
    else:
        print(f"No changes in {path}" if path.exists() else f"Missing {path}")
