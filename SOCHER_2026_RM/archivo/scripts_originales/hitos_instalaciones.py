"""Tabla de hitos por instalación con fechas separadas (anuncio, ingreso SEA, RCA, inicio de
construcción, puesta en servicio eléctrica, operación, inauguración, expansión, cambio de titular).
Combina: instalaciones.csv (intervalo de operación), sea_expedientes.csv (ingreso y RCA) e hitos
curados con fuente. Una fecha conocida solo por intervalo conserva fecha_min y fecha_max.
Salida: datos/instalaciones/hitos.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CUR = [  # id, hito, fecha_min, fecha_max, precision, fuente, pasaje
    ("ENT_CDLV", "inauguracion", "2010-05-01", "2010-05-31", "mes", "ENTEL_MEM2010", "Memoria 2010, p. impresa 77: inauguración de la primera etapa en mayo de 2010"),
    ("ENT_CDLV", "operacion_documentada", "2010-02-27", "2010-02-27", "dia", "ENTEL_2020", "Mantuvo operaciones durante el terremoto de 2010"),
    ("ENT_CDLV", "cambio_titular", "2022-05-03", "2022-05-03", "dia", "DCATLAS_2026", "Adquisición por Equinix (no es entrada)"),
    ("SONDA_Q1", "inauguracion", "2013-04-04", "2013-04-04", "dia", "SONDA_2013", "Inauguró su nuevo Data Center... comuna de Quilicura"),
    ("SONDA_KUDOS", "inauguracion", "2020-12-01", "2020-12-31", "mes", "SONDA_2022", "Datacenter Kudos, inaugurado en diciembre de 2020"),
    ("GOOG_QUIL", "puesta_en_marcha", "2015-01-01", "2015-01-31", "mes", "GOOGLE_WEB", "Desde su puesta en marcha en enero de 2015"),
    ("GOOG_SE_LIB", "entrada_operacion_electrica", "2020-07-10", "2020-07-10", "dia_carta", "CARTA_DE03485-20", "Entrada en Operación del Proyecto SE Los Libertadores (NUP 341)"),
    ("CLARO_LIRAY", "puesta_en_marcha", "2013-01-01", "2013-12-31", "anio", "LATERCERA_2022", "Comenzó en 2011 con el diseño... para 2013 lo echaron a andar"),
    ("CLARO_LIRAY", "expansion", "2023-05-01", "2023-05-31", "mes", "DCATLAS_2026", "Tercera fase inaugurada en 2023 (prensa)"),
    ("TEF_PAINE", "presentacion_operador", "2016-05-27", "2016-05-27", "dia", "TELEFONICA_2016", "Telefónica presenta en Chile... Data Center (Paine)"),
    ("ASC_SCL1", "anuncio", "2019-06-04", "2019-06-04", "dia", "INVESTCHILE_2019", "Confirmó la construcción; se esperaba operar en 2020"),
    ("ASC_SCL1", "apertura", "2020-11-01", "2020-11-30", "mes", "DEVTEL_2022", "When Ascenty opened Chile 1 (noviembre de 2020)"),
    ("ASC_SCL2", "apertura", "2022-07-01", "2022-08-15", "intervalo", "DEVTEL_2022", "Second structure Chile 2 (15/08/2022)"),
    ("ASC_SCL3", "inauguracion", "2025-08-28", "2025-08-28", "dia", "TELETIME_2025", "Inaugurou o terceiro data center... nesta quinta-feira, 28"),
    ("EDGE_SCL01", "anuncio_disponibilidad", "2021-01-19", "2021-01-19", "dia", "EDGECONNEX_2021", "SCL01 facility provides... 7MWs"),
    ("EDGE_SCL0203", "solicitud_entrada_operacion", "2024-05-30", "2024-05-30", "dia_carta", "CARTA_DE03409-24", "Ampliación Data Center Tercera Etapa 40 MW (NUP 3975)"),
    ("EDGE_SCL0203", "puesta_en_servicio_electrica", "2024-08-06", "2024-08-06", "dia_declarado", "CARTA_DE05310-24", "Ampliación Data Center Cuarta Etapa en 40 MVA (NUP 3349): puesta en servicio 6/08/2024"),
    ("ODATA_ST01", "inicio_construccion", "2021-05-15", "2021-05-15", "cota_superior", "PORTALINNOVA_2021", "Ya está construyéndose en la comuna de Lampa"),
    ("ODATA_ST01", "operacion_documentada", "2023-11-07", "2023-11-07", "cota_superior", "DCR_2023", "Fully licensed and operational"),
    ("ODATA_ST01", "autorizacion_conexion_definitiva", "2023-07-03", "2023-07-03", "dia_carta", "CARTA_DE02932-23", "Informe de Autorización de Conexión Definitivo, proyecto Odata Datacenter ST01"),
    ("ODATA_ST02", "apertura_anunciada", "2023-11-07", "2023-11-07", "dia", "DCR_2023", "Apertura del segundo sitio (ST02, hasta 40,6 MW TI)"),
    ("ODATA_ST02", "solicitud_entrada_operacion", "2026-09-28", "2026-09-28", "dia_carta", "CARTA_OP02215-26", "Solicitud de Entrada en Operación del proyecto NUP 3129 Odata San Bernardo ST02"),
    ("MSFT_SCL03", "region_operativa", "2025-06-19", "2025-06-19", "dia", "MICROSOFT_2025", "Chile Central comprende tres ubicaciones físicas independientes (sin individualizar)"),
    ("AWS_PH", "anuncio_region", "2025-05-12", "2025-05-12", "dia", "INVESTCHILE_2025", "Operación esperada a fines de 2026"),
]


def main():
    I = pd.read_csv(ROOT / "datos" / "instalaciones" / "instalaciones.csv", dtype=str)
    S = pd.read_csv(ROOT / "datos" / "instalaciones" / "sea_expedientes.csv", dtype=str)
    rows = []
    for _, r in I.iterrows():
        rows.append({"id": r.id, "hito": "operacion_primera_intervalo", "fecha_min": r.op_min, "fecha_max": r.op_max,
                     "precision": r.op_precision, "fuente": r.fuentes, "pasaje": r.op_base})
        for f in str(r.fuentes).split(";"):
            f = f.strip()
            if f.startswith("SEA_"):
                e = S[S.EXPEDIENTE_ID == f[4:]]
                if len(e):
                    e = e.iloc[0]
                    rows.append({"id": r.id, "hito": "ingreso_SEA", "fecha_min": e.FECHA_PRESENTACION_FORMAT,
                                 "fecha_max": e.FECHA_PRESENTACION_FORMAT, "precision": "dia", "fuente": f,
                                 "pasaje": f"{e.EXPEDIENTE_NOMBRE} ({e.WORKFLOW_DESCRIPCION}); estado {e.ESTADO_PROYECTO}"})
                    if isinstance(e.rca_fecha, str):
                        rows.append({"id": r.id, "hito": "RCA", "fecha_min": e.rca_fecha, "fecha_max": e.rca_fecha,
                                     "precision": "dia", "fuente": f, "pasaje": f"RCA {e.rca_numero}"})
    for c in CUR:
        rows.append(dict(zip(["id", "hito", "fecha_min", "fecha_max", "precision", "fuente", "pasaje"], c)))
    H = pd.DataFrame(rows)
    for c in ["fecha_min", "fecha_max"]:
        H[c] = pd.to_datetime(H[c], dayfirst=True, errors="coerce", format="mixed").dt.date
    H = H.sort_values(["id", "fecha_max"])
    H.to_csv(ROOT / "datos" / "instalaciones" / "hitos.csv", index=False)
    print(len(H), "hitos;", H.hito.value_counts().to_dict())


if __name__ == "__main__":
    main()
