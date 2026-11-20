"""Contrasta el flujo publicado en PRG y resume la comparación a la misma hora local."""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import openpyxl
import pandas as pd


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directorio",type=Path)
    p.add_argument("prg",type=Path)
    a = p.parse_args()
    h = pd.read_csv(a.directorio/"horas.csv",index_col="inicio_local",parse_dates=True)
    plan = pd.read_csv(a.directorio/"programado.csv",index_col="inicio_local",parse_dates=True)
    tabla = h.join(plan,validate="one_to_one")
    fuentes = pd.read_csv(a.directorio/"fuentes_prg.csv")
    assert fuentes.dia.tolist()==list(range(1,32))
    for fila in fuentes.itertuples():
        ruta = a.prg/f"{fila.dia:02}.zip"
        assert hashlib.sha256(ruta.read_bytes()).hexdigest()==fila.sha256
        with ZipFile(ruta) as z:
            nombre, = [n for n in z.namelist() if Path(n).name.upper().startswith("PRG") and n.lower().endswith(".xlsx")]
            libro = openpyxl.load_workbook(z.open(nombre),read_only=True,data_only=True)
            linea, = [r for r in libro["PROGRAMA"].values if len(r)>27 and r[2]=="LoAguirre500->AJahuel500"]
        esperado = -np.array(linea[4:28],dtype=float)
        valores = tabla.loc[tabla.index.day==fila.dia,"flujo_PCP_MW"]
        np.testing.assert_allclose(valores,esperado,atol=0.00001,rtol=0)
    completas = tabla[tabla.estado.ne("transicion")]
    por_hora = completas.groupby([completas.index.hour,"estado"]).brecha_USD_MWh.agg(["mean","size"]).unstack()
    por_hora.columns = ["_".join(k) for k in por_hora.columns]
    por_hora["contraste_USD_MWh"] = por_hora.mean_control-por_hora.mean_sin_marca
    por_hora.rename_axis("hora_local").to_csv(a.directorio/"misma_hora.csv",float_format="%.8f")


if __name__=="__main__":
    main()
