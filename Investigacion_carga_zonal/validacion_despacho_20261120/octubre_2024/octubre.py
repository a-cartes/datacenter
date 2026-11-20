"""Agrega el corredor a horas y compara reglas simples en dos quincenas."""
import argparse
import csv
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import openpyxl
import pandas as pd

BARRAS = ["AJAHUEL_______500", "LO_AGUIRRE____500"]
PANOS = {"ALJAHUEL_500_K3_TRL": "AJ_C1", "ALJAHUEL_500_K4_TRL": "AJ_C2",
         "AGUIRETL_500_K5-K6_TRL": "LA_C1", "AGUIRETL_500_K1-K2_TRL": "LA_C2"}


def curvas_medidas(archivo):
    with archivo.open("rb") as f:
        assert hashlib.file_digest(f, "sha256").hexdigest() == "9d1f66079917de1fa5a77e1238d0687f6eb051cffc7211fcf21b8227d5373992"
    with ZipFile(archivo) as z, z.open("Puntos_de_Medida_15MIN_CSV.csv") as f:
        cabecera = next(f)
        ids = {p.encode() for p in PANOS}
        filas = [l for l in f if l.split(b";", 2)[1] in ids]
    m = pd.read_csv(io.BytesIO(cabecera+b"".join(filas)), sep=";", decimal=",", encoding="utf-8-sig")
    m["local"] = pd.to_datetime(m.DATETIME)
    assert m.local.dt.tz_localize("America/Santiago").dt.tz_convert("UTC").eq(pd.to_datetime(m.UTCDATETIME, utc=True)).all()
    signo = np.where(m.IDSOCKET.str.startswith("ALJAHUEL"), 1, -1)
    m["MW"] = signo * (m.kWhD-m.kWhR)/250
    q = m.pivot(index="local", columns="IDSOCKET", values="MW").rename(columns=PANOS)
    assert q.index.equals(pd.date_range("2024-10-01", periods=2976, freq="15min")) and q.notna().all().all()
    return q


def minuto(hhmm):
    h, m = map(int, str(hhmm).split(":")[:2])
    return h*60+m


def leer_dia(path, dia):
    with ZipFile(path) as z:
        nombre, = [n for n in z.namelist() if Path(n).name.lower().startswith("promediosbarras") and n.lower().endswith("_r.csv")]
        p = pd.read_csv(z.open(nombre), encoding="latin1", sep=";")
        p = p[p.BARRA.isin(BARRAS)].copy()
        assert p.INTERVALO.eq(15).all() and p.FECHA.eq(20241000+dia).all()
        p["local"] = pd.Timestamp(2024, 10, dia) + pd.to_timedelta(p.HORA*60+p.MINUTO, unit="min")
        precios = p.pivot(index="local", columns="BARRA", values="CMg[USD/MWh]").reindex(columns=BARRAS)
        libro, = [n for n in z.namelist() if Path(n).name.lower().startswith("barras_subsistemas") and n.endswith(".xlsx")]
        w = openpyxl.load_workbook(z.open(libro), read_only=True, data_only=True)
        hoja = w["Desacoples_Jerarquia"]
        hoja.reset_dimensions()
        filas = iter(hoja.values)
        nombres = next(filas)
        tabla = pd.DataFrame(filas, columns=nombres)
    minutos = np.zeros(1440, dtype=bool)
    for r in tabla.itertuples(index=False):
        linea = str(r.LINEA).strip()
        if not all(b in linea for b in BARRAS):
            continue
        assert linea == " -> ".join(BARRAS) and str(r.CAUSAL).strip() == "Ctrl. Transferencia", (dia, linea, r.CAUSAL)
        a, b = minuto(r.HORA_INICIO), minuto(r.HORA_FIN) or 1440
        assert 0 <= a < b <= 1440
        minutos[a:b] = True
    assert len(precios) == 96 and precios.notna().all().all()
    precios["min_control"] = minutos.reshape(96,15).sum(axis=1)
    return precios


def contrastes(h):
    # Las horas de transición se reportan aparte y no entran en la comparación.
    d = h[h.min_control.isin([0,60])].copy()
    d["activo"] = d.min_control.eq(60).astype(int)
    d["hora"] = d.index.hour
    ajuste, prueba = d[d.index.day <= 15], d[d.index.day > 15]
    # Referencia por hora y regla de flujo orientada sur-norte.
    # Umbral elegido solo en la primera quincena, con igual peso por clase.
    x = np.sort(ajuste.envio_MW.unique())
    limites = np.r_[np.nextafter(x[0], -np.inf), (x[1:] + x[:-1])/2, np.nextafter(x[-1], np.inf)]
    def balance(y, pred):
        return (pred[y==1].mean() + (1-pred[y==0]).mean())/2
    scores = [balance(ajuste.activo, ajuste.envio_MW.ge(c).astype(int)) for c in limites]
    c = limites[np.argmax(scores)]
    # Regla de calendario estimada con el mismo criterio de clases balanceadas.
    tasa = ajuste.groupby("hora").activo.mean()
    reloj = prueba.hora.map(tasa).ge(ajuste.activo.mean()).astype(int)
    filas = []
    for nombre, pred in [("hora",reloj),("flujo",prueba.envio_MW.ge(c).astype(int))]:
        y = prueba.activo
        filas.append(dict(regla=nombre, umbral_MW=c if nombre=="flujo" else None,
                          n=len(y), VP=int(((y==1)&(pred==1)).sum()), VN=int(((y==0)&(pred==0)).sum()),
                          FP=int(((y==0)&(pred==1)).sum()), FN=int(((y==1)&(pred==0)).sum()),
                          exactitud_balanceada=balance(y,pred)))
    return pd.DataFrame(filas)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for nombre in ["cache","medidas","fuentes","salida"]:
        ap.add_argument(nombre,type=Path)
    a = ap.parse_args()
    q = curvas_medidas(a.medidas)
    precios = []
    with a.fuentes.open() as f:
        fuentes = list(csv.DictReader(f))
    assert [int(r["dia"]) for r in fuentes] == list(range(1,32))
    for r in fuentes:
        dia = int(r["dia"])
        path = a.cache / f"{dia:02d}.zip"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r["sha256"]
        precios.append(leer_dia(path, dia))
    p = pd.concat(precios)
    assert p.index.equals(q.index)
    q = q.join(p)
    q["envio_MW"] = q.AJ_C1+q.AJ_C2
    q["recepcion_MW"] = q.LA_C1+q.LA_C2
    q["brecha_USD_MWh"] = q[BARRAS[1]]-q[BARRAS[0]]
    h = q.resample("h").mean()
    h["min_control"] = q.min_control.resample("h").sum()
    h["estado"] = np.select([h.min_control.eq(0),h.min_control.eq(60)],["sin_marca","control"],default="transicion")
    a.salida.mkdir(exist_ok=True,parents=True)
    h.rename_axis("inicio_local").to_csv(a.salida/"horas.csv",float_format="%.8f")
    h.groupby("estado").agg(horas=("estado","size"),dias=("estado",lambda s:s.index.normalize().nunique()),
                             envio_medio_MW=("envio_MW","mean"),brecha_media=("brecha_USD_MWh","mean"),
                             brecha_mediana=("brecha_USD_MWh","median")).to_csv(a.salida/"regimenes.csv",float_format="%.8f")
    contrastes(h).to_csv(a.salida/"prueba.csv",index=False,float_format="%.8f")


if __name__ == "__main__":
    main()
