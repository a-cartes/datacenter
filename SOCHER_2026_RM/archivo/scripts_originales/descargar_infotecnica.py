"""Descarga propia de Infotécnica (API pública del Coordinador, sin credenciales).

Guarda las respuestas originales (JSON) en fuentes/infotecnica/ y produce:
  datos/geo/subestaciones_infotecnica.csv : id, nombre, propietario, región, provincia, comuna,
      coordenadas UTM (Este, Norte, huso), WGS84, fecha de entrada en operación y estado de
      certificación de cada dato.
  datos/geo/barras_infotecnica.csv : id de barra (= BARRA INFO ID / ID_INFOTECNICA en precios)
      y su subestación.
Las coordenadas y fechas son las declaradas por los coordinados en Infotécnica; su estado
de certificación ('Validado', 'Rechazado', etc.) se conserva y no se corrige.

Uso: python scripts/descargar_infotecnica.py
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time

import pandas as pd
import requests
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "fuentes" / "infotecnica"
GEO = ROOT / "datos" / "geo"
API = "https://api-infotecnica.coordinador.cl/v1/"
CONC = {"Región": "region", "Provincia": "provincia", "Comuna": "comuna", "Coordenada Este": "este",
        "Coordenada Norte": "norte", "Zona o Huso [Ej: 18H-19J etc.]": "huso"}


def get(path, tries=4):
    for k in range(tries):
        try:
            r = requests.get(API + path, timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                return None
        except requests.RequestException:
            pass
        time.sleep(2 * (k + 1))
    return None


def ficha(i):
    p = RAW / "fichas_subestaciones" / f"{i}.json"
    if p.exists():
        d = json.loads(p.read_text())
    else:
        d = get(f"subestaciones/{i}/fichas-tecnicas/general/")
        p.write_text(json.dumps(d, ensure_ascii=False))
    row = {"id_subestacion": i}
    for v in (d or {}).values():
        c = v.get("nombre_concepto") or ""
        key = CONC.get(c)
        if c.startswith("5.16 Fecha de entrada"):
            key = "fecha_entrada"
        if key:
            row[key] = v.get("valor_texto")
            row[key + "_estado"] = v.get("estado_certificacion_nombre")
            row[key + "_modificado"] = v.get("fecha_modificacion")
    return row


def num(x):
    try:
        return float(str(x).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def main():
    (RAW / "fichas_subestaciones").mkdir(parents=True, exist_ok=True)
    GEO.mkdir(parents=True, exist_ok=True)
    meta = {"api": API, "fecha_consulta_utc": pd.Timestamp.utcnow().isoformat(timespec="seconds")}
    lists = {}
    for e in ["subestaciones", "barras"]:
        lists[e] = get(e + "/")
        (RAW / f"{e}.json").write_text(json.dumps(lists[e], ensure_ascii=False))
        meta[e] = len(lists[e])
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(ficha, [s["id"] for s in lists["subestaciones"]]))
    se = pd.DataFrame(lists["subestaciones"])[["id", "nombre", "nemotecnico", "propietario_nombre", "coordinado_nombre"]]
    se = se.rename(columns={"id": "id_subestacion", "nombre": "subestacion"}).merge(pd.DataFrame(rows), on="id_subestacion", how="left")
    se["este_m"] = se.este.map(num)
    se["norte_m"] = se.norte.map(num)
    se["fecha_entrada_dt"] = pd.to_datetime(se.fecha_entrada, format="%d-%m-%Y", errors="coerce")
    lon, lat = [], []
    for e, n, h in zip(se.este_m, se.norte_m, se.huso.fillna("")):
        zone = 18 if str(h).strip().upper().startswith("18") else (19 if str(h).strip().upper().startswith("19") else None)
        if e and n and zone and 1e5 < e < 9e5 and 5e6 < n < 1e7:
            t = Transformer.from_crs(f"EPSG:327{zone}", "EPSG:4326", always_xy=True)
            x, y = t.transform(e, n)
            lon.append(x); lat.append(y)
        else:
            lon.append(None); lat.append(None)
    se["lon"], se["lat"] = lon, lat
    se.to_csv(GEO / "subestaciones_infotecnica.csv", index=False)
    ba = pd.DataFrame(lists["barras"])[["id", "nombre", "id_subestacion", "subestacion_nombre", "propietario_nombre"]]
    ba.rename(columns={"id": "id_barra_info", "nombre": "barra_info_nombre"}).to_csv(GEO / "barras_infotecnica.csv", index=False)
    meta["con_coordenadas"] = int(se.lat.notna().sum())
    meta["region_metropolitana"] = int(se.region.fillna("").str.contains("Metropolitana").sum())
    (RAW / "manifiesto.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(meta)


if __name__ == "__main__":
    main()
