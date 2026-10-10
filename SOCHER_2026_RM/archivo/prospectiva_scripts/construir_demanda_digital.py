"""Identifica la carga digital ya incluida en la previsión oficial de demanda de la CNE (feb. 2026).

La previsión de clientes libres (Anexo 2) no tiene una categoría 'centro de datos': el sector económico de
estas filas es 'Industrial' o 'CPR'. La identificación se hace aquí por razón social (decisión propia,
documentada en la columna 'criterio'), en dos clases que NO deben mezclarse:
  operador_centro_datos : la razón social es un operador de centros de datos; toda la fila es carga digital.
  ti_telecom_mixto      : empresa de telecomunicaciones/TI que opera centros de datos según el inventario del
                          proyecto, pero cuyo retiro en ese punto puede incluir redes y oficinas. No es
                          atribuible por completo a centros de datos.
Salidas (extraidos/demanda_digital/):
  clientes_digitales_cne_anual.csv    una fila por cliente-punto de conexión y año: MWh y MW medio
  clientes_digitales_cne_mensual.csv  lo mismo por mes (permite ver la rampa dentro del año)
  resumen_digital_cne.csv             totales por clase, región metropolitana sí/no y año
MW medio = MWh / horas del período (energía convertida a potencia media; NO es potencia contratada,
potencia informática ni demanda máxima).
"""
import calendar
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "extraidos" / "cne_prevision_demanda_2025_2045" / "clientes_libres_mensual.parquet"
OUT = ROOT / "extraidos" / "demanda_digital"

OPERADOR = [("ASCENTY", "Ascenty"), ("EDGECONNEX", "EdgeConneX"), ("DATALUNA", "Google (Dataluna)"),
            ("LO ESPEJO DATA CENTER", "Lo Espejo Data Center (GTD)"), ("MICROSOFT DATACENTER", "Microsoft"),
            ("ODATA", "ODATA (Aligned)"), ("SCALA", "Scala")]
MIXTO = [("CIRION", "Cirion"), (r"CLARO (CHILE|COMUNICACIONES)", "Claro"), (r"^SONDA", "SONDA"),
         (r"^GTD ", "GTD"), (r"^IBM DE CHILE", "IBM/Kyndryl"), ("EMPRESA NACIONAL DE TELECOMUNICACIONES", "Entel"),
         (r"^TELEFONICA (CHILE|EMPRESAS|MOVILES)", "Telefónica/NextStream"), (r"^TIVIT", "TIVIT"),
         ("NETGLOBALIS", "Netglobalis"), (r"^VTR ", "VTR"), (r"^WOM ", "WOM")]


def clasificar(nombre):
    n = nombre.upper()
    for pat, op in OPERADOR:
        if re.search(pat, n):
            return "operador_centro_datos", op, f"razón social coincide con '{pat}'"
    for pat, op in MIXTO:
        if re.search(pat, n):
            return "ti_telecom_mixto", op, f"razón social coincide con '{pat}'"
    return None, None, None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_parquet(SRC)
    cl = d.cliente.drop_duplicates().to_frame()
    cl[["clase", "operador", "criterio"]] = cl.cliente.apply(lambda s: pd.Series(clasificar(s)))
    d = d.merge(cl.dropna(subset=["clase"]), on="cliente")
    d["rm"] = d.region.str.contains("metropolitana", case=False)
    d["horas"] = [calendar.monthrange(a, m)[1] * 24 for a, m in zip(d.anio, d.mes)]
    d["mw_medio"] = d.mwh / d.horas
    ids = ["fila_excel", "clase", "operador", "cliente", "rut", "region", "rm", "sector", "punto_conexion", "tension", "criterio"]
    d[ids + ["anio", "mes", "mwh", "mwh_ee", "mw_medio"]].sort_values(["clase", "operador", "fila_excel", "anio", "mes"]) \
        .round(3).to_csv(OUT / "clientes_digitales_cne_mensual.csv", index=False)
    an = d.groupby(ids + ["anio"], as_index=False).agg(mwh=("mwh", "sum"), mwh_ee=("mwh_ee", "sum"), horas=("horas", "sum"),
                                                        mw_medio_dic=("mw_medio", "last"))
    an["mw_medio_anual"] = an.mwh / an.horas
    an.drop(columns="horas").round(3).to_csv(OUT / "clientes_digitales_cne_anual.csv", index=False)
    res = an.groupby(["clase", "rm", "anio"], as_index=False).agg(filas=("fila_excel", "nunique"), gwh=("mwh", lambda s: s.sum() / 1e3),
                                                                 mw_medio_anual=("mw_medio_anual", "sum"),
                                                                 mw_medio_dic=("mw_medio_dic", "sum"))
    res.round(1).to_csv(OUT / "resumen_digital_cne.csv", index=False)
    pd.set_option("display.width", 200)
    print(res[res.anio.isin([2025, 2026, 2027, 2028, 2029, 2030, 2032]) & res.rm].round(1).to_string(index=False))
    op = an[(an.clase == "operador_centro_datos") & an.anio.isin([2025, 2028, 2030])] \
        .pivot_table(index=["operador", "punto_conexion"], columns="anio", values="mw_medio_anual").round(1)
    print(op.to_string())


if __name__ == "__main__":
    main()
