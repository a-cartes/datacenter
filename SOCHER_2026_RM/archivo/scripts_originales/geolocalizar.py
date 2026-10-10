"""Coordenadas y unidades territoriales de instalaciones y subestaciones.

1. Geocodifica con Nominatim (OpenStreetMap) las instalaciones marcadas 'geocodificar'
   (respuesta guardada en fuentes/instalaciones/geocodificacion/; 1 consulta/s).
2. Asigna comuna y distrito censal 2017 (polígonos INE) por punto en polígono a
   instalaciones (datos/instalaciones/instalaciones_geo.csv) y subestaciones
   (datos/geo/subestaciones_unidades.csv). Registra si la comuna declarada coincide.
Coordenadas aproximadas o ausentes se conservan como tales; no se imputan.
"""
import json
from pathlib import Path
import time
import unicodedata

import pandas as pd
import requests
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]
GC = ROOT / "fuentes" / "instalaciones" / "geocodificacion"
INE = ROOT / "fuentes" / "geo" / "ine_censo2017"
UA = {"User-Agent": "replica-rm-centros-datos/1.0 (investigacion academica)"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().strip()
    return " ".join(s.split())


def geocode(q):
    GC.mkdir(parents=True, exist_ok=True)
    f = GC / (norm(q).replace(" ", "_").replace("/", "-")[:120] + ".json")
    if f.exists():
        return json.loads(f.read_text())
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params={"q": q, "format": "json", "limit": 1, "addressdetails": 1, "countrycodes": "cl"},
                     headers=UA, timeout=60)
    d = r.json()
    f.write_text(json.dumps({"consulta": q, "fecha": pd.Timestamp.utcnow().isoformat(), "respuesta": d}, ensure_ascii=False))
    time.sleep(1.1)
    return json.loads(f.read_text())


def polygons(name, key):
    g = json.loads((INE / name).read_text())
    geoms = [shape(f["geometry"]) for f in g["features"]]
    props = [f["properties"] for f in g["features"]]
    return STRtree(geoms), geoms, props


def locate(tree, geoms, props, lon, lat):
    if pd.isna(lon) or pd.isna(lat):
        return None
    p = Point(lon, lat)
    for i in tree.query(p):
        if geoms[i].contains(p):
            return props[i]
    return None


def main():
    I = pd.read_csv(ROOT / "datos" / "instalaciones" / "instalaciones.csv", dtype=str)
    I["lat"] = pd.to_numeric(I.lat, errors="coerce")
    I["lon"] = pd.to_numeric(I.lon, errors="coerce")
    I["geocodigo_display"] = None
    for i, r in I[I.fuente_coordenadas == "geocodificar"].iterrows():
        q = f"{r.direccion}, {r.comuna}, Región Metropolitana, Chile"
        d = geocode(q)["respuesta"]
        if d:
            I.loc[i, ["lat", "lon"]] = float(d[0]["lat"]), float(d[0]["lon"])
            I.loc[i, "fuente_coordenadas"] = f"nominatim_{d[0].get('addresstype') or d[0].get('type')}"
            I.loc[i, "geocodigo_display"] = d[0]["display_name"]
        else:
            I.loc[i, "fuente_coordenadas"] = "nominatim_sin_resultado"
    ct, cg, cp = polygons("Comuna_Densid_Superficie_0_RM.geojson", "COMUNA")
    dt, dg, dp = polygons("Distrito_Densid_Superficie_0_RM.geojson", "COD_DISTRI")
    for i, r in I.iterrows():
        c = locate(ct, cg, cp, r.lon, r.lat)
        d = locate(dt, dg, dp, r.lon, r.lat)
        I.loc[i, "comuna_ine"] = c["NOM_COMUNA"] if c else None
        I.loc[i, "cut_comuna"] = c["COMUNA"] if c else None
        I.loc[i, "distrito_ine"] = d["CODIGO_C17"] if d else None
        I.loc[i, "distrito_nombre"] = f'{d["NOM_COMUNA"]}-{d["COD_DISTRI"]}' if d else None
    I["comuna_coincide"] = [norm(a).split(" (")[0] == norm(b) if isinstance(b, str) else None for a, b in zip(I.comuna, I.comuna_ine)]
    I.to_csv(ROOT / "datos" / "instalaciones" / "instalaciones_geo.csv", index=False)
    print(I[["id", "comuna", "comuna_ine", "distrito_nombre", "fuente_coordenadas", "comuna_coincide"]].to_string())

    S = pd.read_csv(ROOT / "datos" / "geo" / "subestaciones_infotecnica.csv")
    out = []
    for _, r in S.iterrows():
        c = locate(ct, cg, cp, r.lon, r.lat)
        d = locate(dt, dg, dp, r.lon, r.lat)
        out.append({"id_subestacion": r.id_subestacion, "comuna_ine": c["NOM_COMUNA"] if c else None,
                    "cut_comuna": c["COMUNA"] if c else None, "distrito_ine": d["CODIGO_C17"] if d else None,
                    "distrito_nombre": f'{d["NOM_COMUNA"]}-{d["COD_DISTRI"]}' if d else None})
    S = S.merge(pd.DataFrame(out), on="id_subestacion")
    S["comuna_coincide"] = [norm(a) == norm(b) if isinstance(a, str) and isinstance(b, str) else None for a, b in zip(S.comuna, S.comuna_ine)]
    S.to_csv(ROOT / "datos" / "geo" / "subestaciones_unidades.csv", index=False)
    rm = S[S.comuna_ine.notna()]
    print("subestaciones dentro de RM (polígonos):", len(rm), "coincide comuna declarada:", rm.comuna_coincide.mean())


if __name__ == "__main__":
    main()
