"""Consulta del buscador público de cartas del Coordinador (https://cartas.coordinador.cl/).

Busca por empresa (razones sociales de centros de datos presentes en /api/empresas) y por
términos en la referencia, para 2010-2026. Conserva cada página de resultados en
fuentes/instalaciones/cartas/ y consolida datos/instalaciones/cartas_coordinador.csv.
Las cartas son declaraciones o solicitudes de los coordinados y respuestas del
Coordinador: una solicitud de entrada en operación no es la autorización ni el inicio del
consumo, y una carta no identifica por sí sola el sitio ni la barra.
"""
import html
import re
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "fuentes" / "instalaciones" / "cartas"
BASE = "https://cartas.coordinador.cl/"
PER = "01/01/2010 00:00:00 - 02/10/2026 23:59:59"
KEYS = ["DATA", "DATALUNA", "MICROSOFT", "AMAZON", "ASCENTY", "ODATA", "SCALA", "EQUINIX", "SONDA", "CIRION",
        "EDGECONNEX", "LO ESPEJO", "GOOGLE", "DIGITAL REALTY", "ALIGNED", "ELEA", "TIVIT", "CLARO CHILE", "ENTEL S.A."]
TERMS = ["data center", "datacenter", "datacenters", "edgeconnex", "microsoft", "ascenty", "odata", "dataluna", "google",
         "scala", "cirion", "equinix", "amazon", "sonda", "lo espejo data", "elea", "claro chile", "entel"]
H = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}


def parse(s):
    out = []
    for row in re.findall(r"<tr.*?</tr>", s, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(cells) < 6:
            continue
        txt = [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", c)).split()) for c in cells]
        link = re.search(r'href="(/show/[0-9a-f]+)"', row)
        ref = re.search(r"Referencias\s*</h4>.*?<div class=\"modal-body\">(.*?)</div>", row, re.S)
        emp = None  # el modal de empresas se carga dinámicamente
        clean = lambda m: " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).split()) if m else None
        out.append({"cells": txt, "url": BASE.rstrip("/") + link.group(1) if link else None,
                    "referencia": clean(ref), "empresas": clean(emp)})
    return out


def search(params, tag):
    rows, page = [], 1
    while True:
        p = {"q": "", "model_type": "todos", "periodo_reporte": PER, **params, "page": page}
        for k in range(4):
            try:
                r = requests.get(BASE + "search", params=p, headers=H, timeout=120)
                break
            except requests.RequestException:
                time.sleep(5 * (k + 1))
        f = RAW / f"{tag}_p{page}.html"
        f.write_text(r.text)
        got = parse(r.text)
        for g in got:
            g.update({"consulta": tag, **{f"param_{k}": v for k, v in params.items()}})
        rows += got
        total = re.search(r"total de\s+(\d+)", re.sub(r"<[^>]+>", " ", r.text))
        n = int(total.group(1)) if total else len(got)
        if not got or len(rows) >= n or page > 80:
            return rows
        page += 1
        time.sleep(1)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    emp = requests.get(BASE + "api/empresas", headers=H, timeout=60).json()
    (RAW / "empresas.json").write_text(pd.Series(emp).to_json(force_ascii=False))
    sel = sorted({e for e in emp if any(k in e.upper() for k in KEYS)} - {"Data Energy Chile SpA"})
    sel = [e for e in sel if not re.search(r"hidro|meteodata|agrosonda|knowledge|imelsa|power data|orbis|getdata|fr data|dimensi", e, re.I)]
    allrows = []
    for e in sel:
        allrows += search({"empresa": e}, "empresa_" + re.sub(r"\W+", "_", e)[:60])
        time.sleep(1)
    for t in TERMS:  # cartas recibidas (enviadas por coordinados) que mencionan la marca o el término
        allrows += search({"q": t, "model_type": "recibido"}, "q_recibido_" + t.replace(" ", "_"))
    recs = []
    for r in allrows:
        c = r["cells"] + [None] * 9
        recs.append({"correlativo": c[0], "tipo": c[2], "fecha": c[3], "remitente": c[5], "materia_macro": c[6],
                     "materia_micro": c[8], "referencia": r["referencia"],
                     "empresas": r["empresas"], "url": r["url"], "consulta": r["consulta"]})
    df = pd.DataFrame(recs)
    df = df.groupby("correlativo", as_index=False).agg({**{k: "first" for k in df.columns if k not in ("correlativo", "consulta")},
                                                         "consulta": lambda s: "; ".join(sorted(set(s)))})
    out = ROOT / "datos" / "instalaciones"
    df.to_csv(out / "cartas_coordinador.csv", index=False)
    print(len(sel), "empresas;", len(df), "cartas únicas")


if __name__ == "__main__":
    main()
