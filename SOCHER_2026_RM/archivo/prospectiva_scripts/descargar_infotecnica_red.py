"""Red y parque EXISTENTES según Infotécnica (API pública del Coordinador, sin credenciales).

Complementa a las bases de planificación: entrega parámetros eléctricos y límites térmicos declarados
de las instalaciones en servicio (no incluye obras futuras ni restricciones operativas del PLP).

Descarga listados y fichas técnicas 'general' de: secciones de tramos de línea, transformadores de
2 devanados y unidades generadoras. Conserva cada respuesta en fuentes/originales/infotecnica/ y produce:
  extraidos/infotecnica/secciones_lineas.csv   una fila por sección: línea, tramo, circuito, kV, km, R, X, B,
                                               límites térmicos [kA] y capacidad térmica derivada [MVA]
  extraidos/infotecnica/tramos_extremos.csv    tramo y descripción de sus dos extremos (paño/subestación)
  extraidos/infotecnica/fichas_largas_<clase>.parquet  todos los conceptos (valor, unidad, estado de certificación)
Los datos son los declarados por los coordinados; el estado de certificación ('Validado', 'Rechazado', ...)
se conserva y no se corrige.  MVA = sqrt(3) * kV * kA (derivado, no declarado).

Uso: python scripts/descargar_infotecnica_red.py
"""
from concurrent.futures import ThreadPoolExecutor
import json
import math
import re
from pathlib import Path
import time

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "fuentes" / "originales" / "infotecnica"
OUT = ROOT / "extraidos" / "infotecnica"
API = "https://api-infotecnica.coordinador.cl/v1/"
CLASES = ["secciones-tramos", "transformadores-2d", "unidades-generadoras"]
LISTAS = CLASES + ["lineas", "tramos", "centrales", "subestaciones", "barras", "panos"]


def get(path, tries=4):
    for k in range(tries):
        try:
            r = requests.get(API + path, timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                return None
        except (requests.RequestException, ValueError):
            pass
        time.sleep(2 * (k + 1))
    return "ERROR"


def ficha(args):
    clase, i = args
    p = RAW / f"fichas_{clase}" / f"{i}.json"
    if p.exists():
        return
    d = get(f"{clase}/{i}/fichas-tecnicas/general/")
    if d != "ERROR":
        p.write_text(json.dumps(d, ensure_ascii=False))


def num(s):
    if isinstance(s, (int, float)):
        return float(s)
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(s or ""))
    return float(m.group(0).replace(",", ".")) if m else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    listas = {}
    for e in LISTAS:
        p = RAW / f"{e}.json"
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(get(f"{e}/"), ensure_ascii=False))
        listas[e] = json.loads(p.read_text())
    for c in CLASES:
        (RAW / f"fichas_{c}").mkdir(exist_ok=True)
    tareas = [(c, x["id"]) for c in CLASES for x in listas[c]]
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(ficha, tareas))
    for c in CLASES:
        rec = []
        for x in listas[c]:
            p = RAW / f"fichas_{c}" / f"{x['id']}.json"
            d = json.loads(p.read_text()) if p.exists() else None
            for v in (d or {}).values():
                if v.get("nombre_concepto"):
                    rec.append((x["id"], x["nombre"], v["nombre_concepto"], v["unidad_nemo"], v["valor_numerico"],
                                v["valor_texto"], v["estado_certificacion_nombre"], v["fecha_modificacion"]))
        df = pd.DataFrame(rec, columns=["id", "nombre", "concepto", "unidad", "valor_numerico", "valor_texto",
                                        "estado_certificacion", "fecha_modificacion"])
        for col in ("nombre", "concepto", "unidad", "valor_texto", "estado_certificacion", "fecha_modificacion"):
            df[col] = df[col].astype(str)
        df["valor_numerico"] = pd.to_numeric(df.valor_numerico, errors="coerce")
        df.to_parquet(OUT / f"fichas_largas_{c}.parquet", index=False)
        print(c, len(listas[c]), "elementos;", df.id.nunique(), "con ficha")
    # tabla de secciones de línea
    f = pd.read_parquet(OUT / "fichas_largas_secciones-tramos.parquet")
    conc = {"1.1 Tensión nominal": "kv", "1.2 Longitud conductor": "km",
            "1.3 Resistencia de secuencia positiva": "r_ohm_km", "1.4 Reactancia de Secuencia positiva": "x_ohm_km",
            "1.5 Susceptancia de secuencia positiva": "b_uS_km",
            "1.9 Límite térmico permanente en verano": "lim_perm_verano_ka",
            "1.9 Límite térmico permanente en invierno": "lim_perm_invierno_ka",
            "1.22 Fecha de entrada en operación": "fecha_entrada"}
    filas = {}
    for r in f.itertuples():
        for k, col in conc.items():
            if r.concepto.startswith(k):
                d = filas.setdefault(r.id, {})
                d[col] = r.valor_texto if col == "fecha_entrada" else (r.valor_numerico if r.valor_numerico is not None
                                                                       and not pd.isna(r.valor_numerico) else num(r.valor_texto))
                d[col + "_estado"] = r.estado_certificacion
    base = pd.DataFrame(listas["secciones-tramos"])[["id", "nombre", "nemotecnico", "id_linea", "linea_nombre", "id_tramo",
                                                      "tramo_nombre", "circuito_nombre", "propietario_nombre"]]
    t = base.merge(pd.DataFrame.from_dict(filas, orient="index").rename_axis("id").reset_index(), on="id", how="left")
    for est in ("verano", "invierno"):
        t[f"mva_{est}_derivado"] = (math.sqrt(3) * t.kv * t[f"lim_perm_{est}_ka"]).round(1)
    t.to_csv(OUT / "secciones_lineas.csv", index=False)
    pd.DataFrame(listas["tramos"])[["id", "nombre", "nemotecnico", "circuito_nombre", "extremo1_descripcion",
                                    "extremo2_descripcion"]].to_csv(OUT / "tramos_extremos.csv", index=False)
    print("secciones con kV y límite de verano:", int((t.kv.notna() & t.lim_perm_verano_ka.notna()).sum()), "de", len(t))


if __name__ == "__main__":
    main()
