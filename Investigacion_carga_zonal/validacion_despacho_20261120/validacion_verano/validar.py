"""Audita los flujos programados, medidas y controles del corredor en enero de 2025."""
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
        assert hashlib.file_digest(f, "sha256").hexdigest() == "1388619ae48f9fa96855445a977d521808daa9642eb7dfe9049fe230e7aead49"
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
    assert q.index.equals(pd.date_range("2025-01-01", periods=2976, freq="15min")) and q.notna().all().all()
    return q


def minuto(hhmm):
    h, m = map(int, str(hhmm).split(":")[:2])
    return h*60+m


def leer_dia(path, dia):
    with ZipFile(path) as z:
        nombre, = [n for n in z.namelist() if Path(n).name.lower().startswith("promediosbarras") and n.lower().endswith("_r.csv")]
        p = pd.read_csv(z.open(nombre), encoding="latin1", sep=";")
        p = p[p.BARRA.isin(BARRAS)].copy()
        assert p.INTERVALO.eq(15).all() and p.FECHA.eq(20250100+dia).all()
        p["local"] = pd.Timestamp(2025, 1, dia) + pd.to_timedelta(p.HORA*60+p.MINUTO, unit="min")
        precios = p.pivot(index="local", columns="BARRA", values="CMg[USD/MWh]").reindex(columns=BARRAS)
        libro, = [n for n in z.namelist() if Path(n).name.lower().startswith("barras_subsistemas") and n.endswith(".xlsx")]
        w = openpyxl.load_workbook(z.open(libro), read_only=True, data_only=True)
        hoja = w["Desacoples_Jerarquia"]
        hoja.reset_dimensions()
        filas = iter(hoja.values)
        nombres = next(filas)
        tabla = pd.DataFrame(filas, columns=nombres)
    inverso = np.zeros(1440, dtype=bool)
    minutos = np.zeros(1440, dtype=bool)
    for r in tabla.itertuples(index=False):
        linea = str(r.LINEA).strip()
        if not all(b in linea for b in BARRAS):
            continue
        assert linea in (" -> ".join(BARRAS), " -> ".join(reversed(BARRAS))) and str(r.CAUSAL).strip() == "Ctrl. Transferencia", (dia, linea, r.CAUSAL)
        a, b = minuto(r.HORA_INICIO), minuto(r.HORA_FIN) or 1440
        assert 0 <= a < b <= 1440
        serie = minutos if linea.startswith(BARRAS[0]) else inverso
        serie[a:b] = True
    assert len(precios) == 96 and precios.notna().all().all()
    precios["min_control"] = minutos.reshape(96,15).sum(axis=1)
    precios["min_inverso"] = inverso.reshape(96,15).sum(axis=1)
    return precios


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directorio',type=Path)
    base = ap.parse_args().directorio
    # Comprueba insumos y fecha efectiva antes de calcular.
    manifiesto = pd.read_csv(base/'fuentes.csv')
    for r in manifiesto.itertuples():
        assert hashlib.sha256((base/r.archivo).read_bytes()).hexdigest() == r.sha256
    q = curvas_medidas(base/'medidas.zip')
    precios = pd.concat([leer_dia(base/'cmg'/f'{d:02}.zip',d) for d in range(1,32)])
    assert precios.index.equals(q.index)
    p = precios.join(q)
    h = p.resample('h').mean()
    for c in ('min_control','min_inverso'):
        h[c] = p[c].resample('h').sum()
    h['envio_MW'] = h.AJ_C1 + h.AJ_C2
    h['brecha_USD_MWh'] = h[BARRAS[1]]-h[BARRAS[0]]
    flujos = []
    for r in manifiesto[manifiesto.archivo.str.startswith('prg/')].sort_values('dia').itertuples():
        with ZipFile(base/r.archivo) as z:
            n, = [f for f in z.namelist() if Path(f).name.upper().startswith('PRG') and f.lower().endswith('.xlsx')]
            w = openpyxl.load_workbook(z.open(n),read_only=True,data_only=True)
            row, = [v for v in w['PROGRAMA'].values if len(v)>27 and v[2]=='LoAguirre500->AJahuel500']
            flujos.extend(-np.asarray(row[4:28],dtype=float))
    h['programado_MW']=flujos
    h['error_MW']=h.programado_MW-h.envio_MW
    h['alerta_umbral_octubre']=h.envio_MW.ge(1404.50965625).astype(int)
    assert len(h)==744 and h.notna().all().all()
    h.rename_axis('inicio_local').to_csv(base/'enero.csv',float_format='%.8f')


if __name__=='__main__':
    main()
