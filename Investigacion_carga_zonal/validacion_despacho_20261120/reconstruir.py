"""Reproduce el diagnóstico AJLA de 05:00 a 06:00, hora local, para dos días."""
import argparse
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile

import openpyxl
import pandas as pd

HUELLAS = {
    "7.zip": "82d62c656307eef8ef6dff0cec798cf7b70ec4ead6a156d3e427eb275b64d8b5",
    "8.zip": "60ab10a749bef20d949b45cc96b808757259c847f73d38b1cc6f31896beb1df5",
    "medidas.zip": "9d1f66079917de1fa5a77e1238d0687f6eb051cffc7211fcf21b8227d5373992",
    "panel.csv.gz": "df429843dc5a3135afa209b84a1ac20ce7a63b3bbcc33bde729c6d06407dce50",
}
BARRAS = {
    "AJAHUEL_______500": "alto_jahuel", "LO_AGUIRRE____500": "lo_aguirre",
    "CANTERAS______110": "canteras", "QUILLOTA______220": "quillota",
}
# La tabla de paños del CEN figura en las fuentes del informe.
PANOS = {
    "ALJAHUEL_500_K3_TRL": "envio_c1", "AGUIRETL_500_K5-K6_TRL": "recepcion_c1",
    "ALJAHUEL_500_K4_TRL": "envio_c2", "AGUIRETL_500_K1-K2_TRL": "recepcion_c2",
}
LINEA = "AJAHUEL_______500 -> LO_AGUIRRE____500"


def flujo(datos):
    # Filtrar antes de decodificar evita cargar 2,28 GB en memoria.
    with ZipFile(datos / "medidas.zip") as z, z.open("Puntos_de_Medida_15MIN_CSV.csv") as f:
        cabecera = next(f)
        medidores = {k.encode() for k in PANOS}
        filas = [linea for linea in f if (b";2024;10;7;5;" in linea or b";2024;10;8;5;" in linea)
                 and linea.split(b";", 2)[1] in medidores]
    m = pd.read_csv(io.BytesIO(cabecera + b"".join(filas)), encoding="utf-8-sig", sep=";", decimal=",")
    assert len(m) == 32 and not m.duplicated(["DATETIME", "IDSOCKET"]).any()
    m["local"] = pd.to_datetime(m.DATETIME)
    utc = m.local.dt.tz_localize("America/Santiago").dt.tz_convert("UTC")
    assert utc.eq(pd.to_datetime(m.UTCDATETIME, utc=True)).all()
    assert m.TENSION.eq(500).all() and m[["kWhD", "kWhR"]].notna().all().all()
    m["canal"] = m.IDSOCKET.map(PANOS)
    m["MW"] = (m.kWhD - m.kWhR) / 250  # kWh netos / 0,25 horas / 1000
    m.loc[m.canal.str.startswith("recepcion"), "MW"] *= -1
    return m.pivot(index="local", columns="canal", values="MW").sort_index()


def minuto(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def precios_estado(archivo, dia):
    fecha = f"202410{dia:02d}"
    with ZipFile(archivo) as z:
        p = pd.read_csv(z.open(f"PromediosBarras{fecha}_{fecha}_R.csv"), sep=";", encoding="latin1")
        p = p[p.BARRA.isin(BARRAS) & p.HORA.eq(5)].copy()
        assert len(p) == 16 and p.FECHA.eq(int(fecha)).all()
        assert p.INTERVALO.eq(15).all() and p.REPORTE.eq("R").all()
        p["barra"] = p.BARRA.map(BARRAS)
        p["local"] = pd.to_datetime(fecha) + pd.to_timedelta(300 + p.MINUTO, unit="min")
        precios = p.pivot(index="local", columns="barra", values="CMg[USD/MWh]")
        libro = openpyxl.load_workbook(z.open(f"Barras_Subsistemas_{fecha}.xlsx"), read_only=True, data_only=True)
        hoja = libro["Desacoples_Jerarquia"]
        hoja.reset_dimensions()  # Los archivos oficiales declaran A1 como dimensión.
        it = iter(hoja.values)
        jerarquia = pd.DataFrame(it, columns=next(it))
        tramos = jerarquia[jerarquia.LINEA.eq(LINEA) & jerarquia.CAUSAL.eq("Ctrl. Transferencia")].copy()
        assert not tramos.empty and tramos.FECHA.astype(str).eq(fecha).all()
        minutos = set()
        for inicio, fin in zip(tramos.HORA_INICIO, tramos.HORA_FIN):
            a, b = minuto(inicio), minuto(fin)
            assert a < (b or 1440)
            minutos.update(range(a, b or 1440))
        conteo = len(minutos.intersection(range(300, 360)))
        assert conteo in (0, 60)
        interior = z.read(f"CMgBarrasMinuto_{fecha}_{fecha}.zip")
        with ZipFile(io.BytesIO(interior)) as cambios:
            registros = pd.read_csv(cambios.open(f"CMgxBarraMinuto_{fecha}.csv"), sep=";", encoding="latin1")
    configs = []
    for barra in list(BARRAS)[:2]:
        s = registros[registros.Barra.eq(barra) & registros.Fecha.eq(int(fecha))].copy()
        s["min"] = 60 * s.Hora + s.Minuto
        s = s.sort_values("min")
        assert not s["min"].duplicated().any()
        previo = s[s["min"].le(300)].iloc[-1]
        ventana = pd.concat([previo.to_frame().T, s[s["min"].between(301, 359)]])
        for _, r in ventana.iterrows():
            configs.append([fecha, BARRAS[barra], r.Hora, r.Minuto, r.Configuracion, r["Subsistema Designado"]])
    return precios, conteo, tramos, configs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("insumos", type=Path)
    parser.add_argument("salida", type=Path)
    args = parser.parse_args()
    for nombre, esperado in HUELLAS.items():
        with (args.insumos / nombre).open("rb") as f:
            if hashlib.file_digest(f, "sha256").hexdigest() != esperado:
                raise ValueError(f"Insumo distinto del documentado: {nombre}")
    panel = pd.read_csv(args.insumos / "panel.csv.gz")
    flujos = flujo(args.insumos)
    resumen, cuartos, intervalos, cambios = [], [], [], []
    for dia in (7, 8):
        fecha = f"2024-10-{dia:02d}"
        p, minutos, tramos, configs = precios_estado(args.insumos / f"{dia}.zip", dia)
        indice = pd.date_range(f"{fecha} 05:00", periods=4, freq="15min")
        q = p.join(flujos, validate="one_to_one").sort_index()
        assert q.index.equals(indice) and q.notna().all().all()
        for c in ("envio", "recepcion"):
            q[c + "_MW"] = q[c + "_c1"] + q[c + "_c2"]
        q["diferencia_extremos_MW"] = q.envio_MW - q.recepcion_MW
        q["brecha_corredor_USD_MWh"] = q.lo_aguirre - q.alto_jahuel
        q["brecha_local_USD_MWh"] = q.canteras - q.quillota
        row, = panel[panel.fecha.eq(fecha) & panel.hora0.eq(5)].itertuples()
        medias = q.mean()
        assert abs(medias.canteras - row.CANTERAS_110) < 0.0001
        assert abs(medias.quillota - row.QUILLOTA_220) < 0.0001
        assert int(row.ctx_AJLA) * 60 == minutos
        assert abs(row.D_HT1 + row.D_HT2 - row.MW) < 0.00001
        resumen.append({"fecha": fecha, "hora_local": 5, "retiro_HT1_HT2_MW": row.MW,
                        "minutos_control": minutos, **medias.to_dict()})
        cuartos.append(q)
        intervalos.append(tramos)
        cambios.extend(configs)
    args.salida.mkdir(parents=True, exist_ok=True)
    for nombre, frame in [
        ("horas", pd.DataFrame(resumen)),
        ("cuartos", pd.concat(cuartos).rename_axis("inicio_local").reset_index()),
        ("intervalos", pd.concat(intervalos)),
        ("configuraciones", pd.DataFrame(cambios, columns=["fecha", "barra", "hora_marca",
                                                          "minuto_marca", "configuracion", "subsistema"])),
    ]:
        frame.to_csv(args.salida / (nombre + ".csv"), index=False, float_format="%.8f")


if __name__ == "__main__":
    main()
