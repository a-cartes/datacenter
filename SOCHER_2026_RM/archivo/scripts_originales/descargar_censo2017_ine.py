"""Descarga capas oficiales del INE (Censo 2017) desde sus servicios ArcGIS públicos.

Servicios (listados en https://www.ine.gob.cl/herramientas/portal-de-mapas/geodatos-abiertos):
  Comuna_Densid_Superficie, Distrito_Densid_Superficie (polígonos con población y viviendas)
  Microdatos_Censo capa 1 (agregados por manzana) y capa 0 (entidades rurales)
Se descarga la Región Metropolitana (REGION=13) en GeoJSON WGS84, paginando, y se guardan
las respuestas originales en fuentes/geo/ine_censo2017/. No se modifican valores.
"""
import json
from pathlib import Path
import time

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "fuentes" / "geo" / "ine_censo2017"
BASE = "https://services5.arcgis.com/hUyD8u3TeZLKPe4T/arcgis/rest/services/{}/FeatureServer/{}/query"
CAPAS = [("Comuna_Densid_Superficie", 0, "REGION='13'"), ("Distrito_Densid_Superficie", 0, "REGION='13'"),
         ("Microdatos_Censo", 1, "CUT>=13000 AND CUT<14000"), ("Microdatos_Censo", 0, "COD_REGION='13'")]


def fetch(svc, layer, where):
    feats, off = [], 0
    while True:
        p = {"where": where, "outFields": "*", "outSR": 4326, "f": "geojson", "resultOffset": off,
             "resultRecordCount": 2000, "returnGeometry": "true"}
        for k in range(5):
            try:
                r = requests.get(BASE.format(svc, layer), params=p, timeout=180)
                d = r.json()
                break
            except Exception:
                time.sleep(5 * (k + 1))
        fs = d.get("features", [])
        if not fs and "error" in d:
            # algunos servicios guardan REGION como número
            if "'" in where:
                return fetch(svc, layer, where.replace("'", ""))
            raise RuntimeError(d)
        feats += fs
        if len(fs) < 2000 and not d.get("properties", {}).get("exceededTransferLimit"):
            break
        off += len(fs)
    return {"type": "FeatureCollection", "features": feats, "fuente": BASE.format(svc, layer), "where": where}


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    for svc, layer, where in CAPAS:
        g = fetch(svc, layer, where)
        out = RAW / f"{svc}_{layer}_RM.geojson"
        out.write_text(json.dumps(g, ensure_ascii=False))
        print(svc, layer, len(g["features"]))
