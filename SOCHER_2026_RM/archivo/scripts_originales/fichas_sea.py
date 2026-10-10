"""Descarga y lee las fichas SEA de expedientes de centros de datos (y obras asociadas).

Entrada: datos/instalaciones/sea_resultados_brutos.csv (de consultar_sea.py), filtrado por
nombre/titular pertinente y revisado manualmente (EXCLUIR lista falsos positivos).
Guarda HTML original de ficha y mapa en fuentes/instalaciones/sea/fichas/ y produce
datos/instalaciones/sea_expedientes.csv con: id, nombre, titular, comuna, forma, estado,
inversión, fecha de admisibilidad, RCA (número y fecha), punto representativo (WGS84)
y un extracto de la descripción. Las fechas del SEA son de tramitación, no de operación.
"""
import re
import html
from pathlib import Path
import time

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "fuentes" / "instalaciones" / "sea" / "fichas"
FICHA = "https://seia.sea.gob.cl/expediente/ficha/fichaPrincipal.php?modo=ficha&id_expediente={}"
MAPA = "https://seia.sea.gob.cl/mapa/visualizacion/PuntoRepresentativo/index.php?idExpediente={}"
PAT_NOMBRE = r"data|datos|scl0|scl1|scl99|st5|c[oó]mputo"
PAT_TIT = r"data ?center|datacenter|edgeconnex|odata|ascenty|scala|equinix|microsoft|amazon|cirion|google|dataluna|elea|digital holdings"
# Falsos positivos revisados (ácido sulfúrico, aceite dieléctrico, hidroeléctrica, recursos del mar)
EXCLUIR = {"2588", "5108", "2204776", "7113361", "7243160", "7280836", "2131141874", "2131168800",
           "2131261066", "2131327699", "2131795389"}


def text(s):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    return [l.strip() for l in t.split("\n") if l.strip()]


def after(L, key, n=1):
    for i, l in enumerate(L):
        if l == key and i + n < len(L):
            return L[i + n]
    return None


def parse(eid):
    fp, mp = RAW / f"{eid}_ficha.html", RAW / f"{eid}_mapa.html"
    for url, p in [(FICHA.format(eid), fp), (MAPA.format(eid), mp)]:
        if not p.exists():
            r = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
            p.write_bytes(r.content)
            time.sleep(1)
    L = text(fp.read_bytes().decode("latin-1"))
    m = mp.read_bytes().decode("latin-1")
    x = re.search(r"var x = (-?[\d.]+);", m)
    y = re.search(r"var y = (-?[\d.]+);", m)
    rec = {"EXPEDIENTE_ID": eid, "lon_sea": float(x.group(1)) if x else None, "lat_sea": float(y.group(1)) if y else None,
           "tipo_proyecto": after(L, "Tipo de Proyecto"), "inversion_mmusd": after(L, "Monto de Inversión")}
    # registro de estados: secuencias Estado | Documento | Número | Fecha | Autor
    joined = " | ".join(L)
    adm = re.search(r"Resolución de Admisibilidad \| ([^|]*) \| (\d{2}/\d{2}/\d{4})", joined)
    rca = re.search(r"Resolución de Calificación Ambiental \(RCA\) \| ([^|]*) \| (\d{2}/\d{2}/\d{4})", joined)
    des = re.search(r"Resolución que tiene por desistid[ao][^|]* \| ([^|]*) \| (\d{2}/\d{2}/\d{4})", joined)
    rec.update({"admisibilidad_fecha": adm.group(2) if adm else None,
                "rca_numero": rca.group(1).strip() if rca else None, "rca_fecha": rca.group(2) if rca else None,
                "desistimiento_fecha": des.group(2) if des else None})
    i0 = joined.find("Descripción del Proyecto")
    i1 = joined.find("Información de Contacto")
    rec["descripcion"] = joined[i0 + 27:i1].replace(" | ", " ")[:3000] if i0 > 0 else None
    return rec


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(ROOT / "datos" / "instalaciones" / "sea_resultados_brutos.csv", dtype=str)
    k = d[d.EXPEDIENTE_NOMBRE.str.lower().str.contains(PAT_NOMBRE, regex=True)
          | d.TITULAR.str.lower().str.contains(PAT_TIT, regex=True)]
    k = k[~k.EXPEDIENTE_ID.isin(EXCLUIR)]
    recs = [parse(e) for e in k.EXPEDIENTE_ID]
    out = k[["EXPEDIENTE_ID", "EXPEDIENTE_NOMBRE", "WORKFLOW_DESCRIPCION", "REGION_NOMBRE", "COMUNA_NOMBRE", "TITULAR",
             "FECHA_PRESENTACION_FORMAT", "ESTADO_PROYECTO", "EXPEDIENTE_URL_PPAL", "termino"]].merge(pd.DataFrame(recs), on="EXPEDIENTE_ID")
    out.to_csv(ROOT / "datos" / "instalaciones" / "sea_expedientes.csv", index=False)
    print(out.drop(columns=["descripcion", "EXPEDIENTE_URL_PPAL", "termino", "tipo_proyecto"]).to_string())


if __name__ == "__main__":
    main()
