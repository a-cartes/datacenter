"""Tabla de candidatos a instalaciones desde directorios secundarios (DC Atlas e Inflect).

Los directorios se usan solo como universo de búsqueda, análogo al uso de Data Center Map
en el artículo original (Data Center Map bloqueó el acceso automatizado el 2026-10-02).
Sus comunas, coordenadas, estados y capacidades NO se aceptan como verificados: varias
geolocalizaciones son evidentemente erróneas. Salida: datos/instalaciones/candidatos_directorios.csv
"""
import html, json, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fuentes" / "instalaciones" / "directorios"
rows = []
for f in sorted((SRC / "dcatlas").glob("*.html")):
    if f.name.startswith("_"):
        continue
    s = f.read_text()
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            d = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if d.get("@type") == "Place" and "operator" in d:
            props = {p["name"]: p.get("value") for p in d.get("additionalProperty", [])}
            st = re.search(r"Back to Facilities.*?Santiago\s*</a>.*?>(Operational|Under construction|Planned|Decommissioned)<", s, re.S)
            prec = re.search(r"Location precision\s*</[^>]+>\s*<[^>]+>\s*([A-Za-z ]+)<", s)
            rows.append({"directorio": "DC Atlas", "archivo": f"fuentes/instalaciones/directorios/dcatlas/{f.name}",
                         "nombre_directorio": d["name"], "descripcion": d.get("description"),
                         "operador_directorio": d["operator"]["name"], "localidad_directorio": d["address"].get("addressLocality"),
                         "direccion_directorio": None, "lat_directorio": d.get("geo", {}).get("latitude"),
                         "lon_directorio": d.get("geo", {}).get("longitude"), "tipo_directorio": d.get("additionalType"),
                         "mw_directorio": props.get("Live capacity"),
                         "estado_directorio": "Operational" if "Operational" in (d.get("description") or "") else None,
                         "precision_ubicacion": prec.group(1).strip() if prec else None, "mercado": d.get("containedInPlace", {}).get("name")})
s = (SRC / "inflect" / "santiago.html").read_text()
t = re.sub(r"<script.*?</script>|<style.*?</style>|<svg.*?</svg>", "", s, flags=re.S)
L = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", t)).split("\n") if l.strip()]
i0 = L.index("found")
i1 = next(i for i, l in enumerate(L) if l.startswith("Need Bare Metal"))
seq = L[i0 + 1:i1]
for k in range(0, len(seq) - 2, 3):
    nm, addr = seq[k + 1], seq[k + 2]
    rows.append({"directorio": "Inflect", "archivo": "fuentes/instalaciones/directorios/inflect/santiago.html",
                 "nombre_directorio": nm, "direccion_directorio": addr.split(", ")[0],
                 "localidad_directorio": addr.split(", ")[-1], "mercado": "Santiago"})
df = pd.DataFrame(rows)
out = ROOT / "datos" / "instalaciones"
out.mkdir(parents=True, exist_ok=True)
df.to_csv(out / "candidatos_directorios.csv", index=False)
print(df.groupby("directorio").size())
print(df[["directorio", "nombre_directorio", "operador_directorio", "localidad_directorio", "direccion_directorio", "mw_directorio"]].to_string())
