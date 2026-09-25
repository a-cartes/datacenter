"""Comprueba enlaces locales de las guías nuevas y la portada del repositorio."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
files = [ROOT / name for name in ['README.md', 'ROADMAP.md', 'CHANGELOG.md', 'REUSE.md']]
files.extend(sorted((ROOT / 'docs').glob('*.md')))
errors, count = [], 0
for path in files:
    text = path.read_text(encoding='utf-8')
    targets = re.findall(r'\]\(([^)]+)\)', text) + re.findall(r'src="([^"]+)"', text)
    for target in targets:
        if target.startswith(('https://', 'http://', '#', 'mailto:')):
            continue
        target = target.split('#')[0]
        if not (path.parent / target).is_file():
            errors.append({'archivo': str(path.relative_to(ROOT)), 'enlace_ausente': target})
        count += 1
svg = ET.parse(ROOT / 'docs/assets/portada.svg').getroot()
if svg.tag != '{http://www.w3.org/2000/svg}svg':
    errors.append({'portada': 'raiz SVG inválida'})
print(json.dumps({'estado': 'OK' if not errors else 'FALLO', 'guias': len(files), 'enlaces_locales': count, 'errores': errors}, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 0)
