"""Extrae la solución oficial del primer día de cada horizonte, en el sentido AJ→LA."""
import argparse
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

LINEA = "LoAguirre500->AJahuel500"
COLUMNAS = {"Flow":"flujo_PCP_MW", "Import Limit":"limite_AJ_LA_PCP_MW",
            "Export Limit":"limite_LA_AJ_PCP_MW","Hours Congested":"congestion_PCP"}


def abrir_interno(z, sufijo):
    nombre, = [n for n in z.namelist() if n.endswith(sufijo)]
    return ZipFile(io.BytesIO(z.read(nombre)))


def series(archivo, dia):
    fecha = f"202410{dia:02}"
    with ZipFile(archivo) as z, abrir_interno(z, "RES"+fecha+".zip") as resultados:
        with abrir_interno(resultados,"Solution.zip") as solucion:
            xml, = [n for n in solucion.namelist() if n.endswith("Solution.xml")]
            raiz = ET.fromstring(solucion.read(xml))
            binario = solucion.read("t_data_0.BIN")

    def filas(tabla):
        return [{campo.tag.split("}")[-1]:campo.text for campo in fila}
                for fila in raiz.findall("{*}t_"+tabla)]

    def indice(tabla, columna):
        return {f[columna]:f for f in filas(tabla)}

    objetos = indice("object","object_id")
    propiedades = indice("property","property_id")
    unidades = indice("unit","unit_id")
    miembros = indice("membership","membership_id")
    claves = indice("key_index","key_id")
    calendario = indice("period_0","interval_id")
    fase = sorted(filas("phase_3"),key=lambda f:int(f["period_id"]))
    horas = pd.to_datetime([calendario[f["interval_id"]]["datetime"] for f in fase[:24]],dayfirst=True)
    assert horas.equals(pd.date_range(pd.Timestamp(2024,10,dia),periods=24,freq="h"))
    tabla = pd.DataFrame(index=horas)
    for k in filas("key"):
        m = miembros[k["membership_id"]]
        if objetos[m["child_object_id"]]["name"] != LINEA or objetos[m["parent_object_id"]]["name"]!="SEN":
            continue
        prop = propiedades[k["property_id"]]
        nombre = prop["name"]
        if nombre not in COLUMNAS or k["phase_id"]!="3" or k["period_type_id"]!="0":
            continue
        ix = claves[k["key_id"]]
        assert int(ix["period_offset"])==0 and int(ix["length"])>=24
        assert COLUMNAS[nombre] not in tabla
        if nombre != "Hours Congested":
            assert unidades[prop["unit_id"]]["value"]=="MW"
        v = np.frombuffer(binario, dtype="<f8", count=24, offset=int(ix["position"]))
        tabla[COLUMNAS[nombre]] = -v if nombre in ("Flow","Import Limit") else v
    assert set(tabla)==set(COLUMNAS.values()) and tabla.congestion_PCP.isin([0,1]).all()
    return tabla


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("cache",type=Path)
    a.add_argument("fuentes",type=Path)
    a.add_argument("directorio_resultados",type=Path)
    args = a.parse_args()
    fuentes = pd.read_csv(args.fuentes)
    assert fuentes.dia.tolist()==list(range(1,32))
    dias = []
    for r in fuentes.itertuples():
        ruta = args.cache/f"{r.dia:02}.zip"
        assert hashlib.sha256(ruta.read_bytes()).hexdigest()==r.sha256
        dias.append(series(ruta,r.dia))
    simulacion = pd.concat(dias)
    real = pd.read_csv(args.directorio_resultados/"horas.csv",index_col="inicio_local",parse_dates=True)
    assert simulacion.index.equals(real.index)
    obs = real.join(simulacion,validate="one_to_one")
    # Convención de comparación principal: envío medido en Alto Jahuel.
    obs["error_flujo_MW"] = obs.flujo_PCP_MW-obs.envio_MW
    obs[simulacion.columns.tolist()+["error_flujo_MW"]].to_csv(
        args.directorio_resultados/"programado.csv",index_label="inicio_local",float_format="%.8f")
    resumen = []
    for periodo, bloque in [("mes",obs),("16-31",obs[obs.index.day>15])]:
        enteras = bloque[bloque.min_control.isin([0,60])]
        y = enteras.min_control.eq(60)
        pred = enteras.congestion_PCP.eq(1)
        resumen.append(dict(periodo=periodo,horas_flujo=len(bloque),mae_MW=bloque.error_flujo_MW.abs().mean(),
                            sesgo_MW=bloque.error_flujo_MW.mean(),horas_estado=len(enteras),
                            VP=(pred&y).sum(),FP=(pred&~y).sum(),VN=(~pred&~y).sum(),FN=(~pred&y).sum()))
    pd.DataFrame(resumen).to_csv(args.directorio_resultados/"desempeno_PCP.csv",index=False,float_format="%.8f")


if __name__ == "__main__":
    main()
