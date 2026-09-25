"""Consolida hitos, candidatos y relaciones documentales, sin asignar tratamientos.

Ejecución desde cualquier directorio con pandas y pyarrow. Los insumos v2–v6 se
leen sin modificación; no se descargan fuentes ni se estiman efectos causales.
Las fechas de previsiones y documentos no son fechas de carga realizada.
"""
from pathlib import Path, PurePosixPath
import calendar
import csv
import hashlib
import json
import pandas as pd

B = Path(__file__).resolve().parents[1]
ROOT = B.parent
OUT = B / "tablas"
DOC = B / "documentacion"
OUT.mkdir(parents=True, exist_ok=True)
DOC.mkdir(parents=True, exist_ok=True)
INPUTS = {}


def ruta_origen_relativa(value):
    """Normaliza raíces archivadas sin exigir la ruta personal del investigador.

    Las fuentes se preservan intactas. Solo se reconoce el sufijo iniciado por
    una carpeta de versión conocida; no se adivina identidad por nombre de PDF.
    """
    parts = PurePosixPath(str(value).replace("\\", "/")).parts
    if ".." in parts:
        raise ValueError(f"Ruta heredada con ascenso no permitido: {value}")
    roots = {"SOCHER_2026_v2", "SOCHER_2026_v3", "SOCHER_2026_v4", "SOCHER_2026_v6_multicentros"}
    for pos, part in enumerate(parts):
        if part in roots:
            return PurePosixPath(*parts[pos:]).as_posix()
    raise ValueError(f"Raíz de fuente no reconocida: {value}")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(relative):
    path = ROOT / relative
    INPUTS[relative] = sha(path)
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(relative):
    path = ROOT / relative
    INPUTS[relative] = sha(path)
    return json.loads(path.read_text(encoding="utf-8"))


OUTPUTS = {}
SCHEMAS = {}


def write(name, rows):
    df = pd.DataFrame(rows)
    for col in df.columns:
        if col.startswith("es_") or col in {"elegible_causal", "vigencia_operativa_validada", "utilizable_W_causal"}:
            df[col] = df[col].astype("boolean")
        elif col.endswith("_fila"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        else:
            df[col] = df[col].replace("", pd.NA).astype("string")
    df.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")
    df.to_parquet(OUT / f"{name}.parquet", index=False)
    restored = pd.read_parquet(OUT / f"{name}.parquet")
    pd.testing.assert_frame_equal(df, restored)
    OUTPUTS[name] = {"filas": len(df), "csv_sha256": sha(OUT / f"{name}.csv"), "parquet_sha256": sha(OUT / f"{name}.parquet")}
    SCHEMAS[name] = {k: str(v) for k, v in df.dtypes.items()}
    return df


CENTER_INPUT = "SOCHER_2026_v6_multicentros/mapeo/registro_centros_candidatos.csv"
REL_INPUT = "SOCHER_2026_v6_multicentros/mapeo/relacion_centros_barras.csv"
V3_EVENTS = "SOCHER_2026_v3/eventos/registro_eventos_2020_2021.csv"
V4_EVENTS = "SOCHER_2026_v4/eventos/registro_fechas_observadas_y_documentales.csv"
NETWORK_INPUT = "SOCHER_2026_v4/territorio/registro_conexiones.csv"

raw_centers = read_csv(CENTER_INPUT)
centers = []
for i, r in enumerate(raw_centers, 2):
    r = dict(r)
    cid = r.pop("candidato_id")
    r.pop("elegible_evento_causal")
    centers.append(dict(centro_id=cid, **r,
                        es_candidato_campus=cid != "QUILICURA_SIN_DC_ADJUDICADO",
                        es_establecimiento_independiente_validado=False,
                        elegible_causal=False, fecha_tratamiento_causal=None,
                        cohorte_g=None, estado_tratamiento="PENDIENTE_ADJUDICACION",
                        motivo_no_elegible=r["pendiente"],
                        tabla_origen=CENTER_INPUT, tabla_origen_fila=i))
center_map = {r["centro_id"]: r for r in centers}
assert len(center_map) == len(centers) == 10
centers_df = write("centros", centers)

# La homologación de julio de 2024 identifica códigos en esa versión; no
# transforma toda relación de proyecto/catálogo en suministro histórico activo.
relations = []
for i, r in enumerate(read_csv(REL_INPUT), 2):
    cid = r["centro_id"]
    relations.append(dict(relacion_id=f"CB_{i-1:03d}",
                          campus_grupo_id=center_map[cid]["campus_grupo_id"], **r,
                          vigencia_operativa_desde=None, vigencia_operativa_hasta=None,
                          vigencia_operativa_validada=False, es_asignacion_causal=False,
                          tabla_origen=REL_INPUT, tabla_origen_fila=i))
assert all(r["centro_id"] in center_map for r in relations)
relations_df = write("relaciones_centros_barras", relations)

# Catálogo de referencias: conserva la diferencia entre PDF archivado y ficha
# cuyo contenido se había verificado por web, sin fabricar copias originales.
sources = []
for s in read_json("SOCHER_2026_v3/eventos/fuentes_manifest.json"):
    local = f"SOCHER_2026_v3/eventos/{s['file']}" if s.get("file") else None
    sources.append(dict(fuente_id="V3_" + s["source_id"], titulo=s["source_id"],
                        url=s["url"], archivo_original_local=local,
                        paginas=s["pages"], estado_archivo=s["status"],
                        sha256_original_declarado=s.get("sha256"),
                        fecha_revision_declarada=s["accessed"]))
for s in read_csv("SOCHER_2026_v4/territorio/fuentes_manifest.csv"):
    local = s["archivo_local"]
    if local:
        local = ruta_origen_relativa(local)
    sources.append(dict(fuente_id="V4_" + s["id"], titulo=s["titulo"], url=s["url"],
                        archivo_original_local=local, paginas=s["paginas_pdf_1based"],
                        estado_archivo="archivo local declarado" if local else "consulta web previa sin archivo original local",
                        sha256_original_declarado=s["sha256"], fecha_revision_declarada=s["consultado"]))
for s in read_json("SOCHER_2026_v2/fuentes_publicas/manifest_fuentes_nuevas.json"):
    sources.append(dict(fuente_id="V2_" + s["id"], titulo=s["type"], url=s["url"],
                        archivo_original_local="SOCHER_2026_v2/fuentes_publicas/" + s["file"],
                        paginas=s["pages_reviewed"], estado_archivo="archivo local declarado",
                        sha256_original_declarado=s["sha256"], fecha_revision_declarada=s["retrieved"]))


def extra_source(sid, title, url, local=None, state="Referencia heredada del registro v6; original no archivado en esta consolidación"):
    sources.append(dict(fuente_id=sid, titulo=title, url=url,
                        archivo_original_local=local, paginas=None, estado_archivo=state,
                        sha256_original_declarado=None, fecha_revision_declarada="2026-09-25"))


extra_source("V6_GOOGLE2018", "Google: expansión Quilicura", "https://latam.googleblog.com/2018/09/expansion-quilicura.html")
extra_source("V6_ASCENTY2", "Minuta solicitud nuevo transformador Data Center Chile", "https://www.coordinador.cl/wp-content/uploads/2025/01/Minuta_Solicitud_Nuevo_Transformador_para_Data_Center_Chile.pdf")
extra_source("V6_ODATA_ST02", "Carta promotor ODATA ST02", "https://cartas.coordinador.cl/download_saved_file/6925c4f93563570b31306392")
extra_source("V6_SANTA_TERESA", "Presentación ampliación Santa Teresa", "https://cartas.coordinador.cl/show/68a378dd3563570a01a644dd")
extra_source("V6_CIRION_DIA", "DIA Cirion", "https://infofirma.sea.gob.cl/DocumentosSEA/MostrarDocumento?docId=2023%2F05%2F24%2Fcecb-c2f6-40e9-a2fd-cb30bcdbafb1")
for month, title in [("06_Junio", "Junio"), ("07_Julio", "Julio")]:
    local = f"2024/{month}/Definitivo/1_Transferencia_Puntos_de_Medida_15MIN_CSV.zip"
    extra_source("MED_2024_" + month[:2], f"Transferencias 15 minutos, {title} de 2024", None, local,
                 "Original local referido por auditoría v4; ver manifiestos v4 para extracción y versiones")
    sources[-1]["paginas"] = "V4 diagnóstico y registro; canales HT1/HT2; etiquetas UTC y local"

source_map = {s["fuente_id"]: s for s in sources}
assert len(source_map) == len(sources)

events = []


def add(eid, cid, kind, description, start, end, precision, evidence, source_ids,
        origin, row, note, *, time_start=None, time_end=None, utc_start=None,
        utc_end=None, is_forecast=False, phase=None, realized=None):
    for sid in source_ids.split(";"):
        assert sid in source_map, sid
    c = center_map[cid]
    urls = [source_map[s]["url"] for s in source_ids.split(";") if source_map[s]["url"]]
    local = [source_map[s]["archivo_original_local"] for s in source_ids.split(";") if source_map[s]["archivo_original_local"]]
    events.append(dict(evento_id=eid, centro_id=cid, campus_grupo_id=c["campus_grupo_id"],
                       tipo_evento=kind, descripcion=description, fase_o_equipos=phase,
                       fecha_desde=start, fecha_hasta=end, precision_fecha=precision,
                       etiqueta_local_desde=time_start, etiqueta_local_hasta=time_end,
                       etiqueta_utc_desde=utc_start, etiqueta_utc_hasta=utc_end,
                       zona_horaria_etiquetas="America/Santiago" if time_start else None,
                       convencion_inicio_fin_intervalo="NO_ACREDITADA" if time_start else None,
                       nivel_evidencia_fecha=evidence, es_fecha_prevista=is_forecast,
                       estado_realizacion=realized or "DOCUMENTO_NO_PRUEBA_CARGA_NUEVA",
                       naturaleza_tratamiento_pendiente=c["pendiente"],
                       elegible_causal=False, motivo_no_elegible=note,
                       fecha_tratamiento_causal=None, cohorte_g=None,
                       fuente_ids=source_ids, fuentes_url=";".join(dict.fromkeys(urls)),
                       fuentes_originales_locales=";".join(dict.fromkeys(local)),
                       tabla_origen=origin, tabla_origen_fila=row))


mapping = {
    "DATALUNA_LIBERTADORES_2020_RAMP": ("DATALUNA_QUILICURA", "PRUEBAS_CONEXION", "MES_FINES_SIN_DIA"),
    "DATALUNA_LIBERTADORES_2020_EO": ("DATALUNA_QUILICURA", "EO_FORMAL_RED", "DIA"),
    "ASCENTY_CHACABUCO_2020_PES": ("ASCENTY_CHILE1", "PES_ALIMENTADOR", "DIA"),
    "EDGECONNEX_DC01_2020": ("EDGE_COLINA", "OPERACION_CAMPUS_DOCUMENTADA", "ANIO"),
    "EDGECONNEX_DC01_ETAPA2_PLAN2021": ("EDGE_COLINA", "AMPLIACION_PREVISTA", "FECHA_REALIZADA_NO_VERIFICADA"),
}
for i, r in enumerate(read_csv(V3_EVENTS), 2):
    cid, kind, precision = mapping[r["event_id"]]
    start, end = r["date_start"] or None, r["date_end"] or None
    if start and len(start) == 7:
        year, month = map(int, start.split("-"))
        start = f"{year:04d}-{month:02d}-01"
        end = f"{year:04d}-{month:02d}-{calendar.monthrange(year, month)[1]}"
    add(r["event_id"], cid, kind, r["event_type"], start, end, precision,
        "HITO_DOCUMENTAL_HEREDADO_V3", ";".join("V3_" + s for s in r["source_ids"].split(";")),
        V3_EVENTS, i, r["critical_note"] + "; " + r["status"],
        is_forecast=kind == "AMPLIACION_PREVISTA", phase=r["facility"])

v4_specs = [
    ("EDGE_PES_3016_3975_20240407", "PES_RED_CONTINUACION", "V4_S03", "2024-04-07", "2024-04-07"),
    ("EDGE_EO_3016_20240502", "EO_FORMAL_RED", "V4_S04", "2024-05-02", "2024-05-02"),
    ("EDGE_EO_3975_20240529", "EO_FORMAL_AMPLIACION", "V4_S04", "2024-05-29", "2024-05-29"),
    ("EDGE_HT2_AUMENTO_20240624_2130", "CAMBIO_RETIRO_OBSERVADO", "MED_2024_06", "2024-06-24", "2024-06-24"),
    ("EDGE_HT2_AUMENTO_20240624_2145", "CAMBIO_RETIRO_OBSERVADO", "MED_2024_06", "2024-06-24", "2024-06-24"),
    ("EDGE_HT1_AUMENTO_20240624_2300", "CAMBIO_RETIRO_OBSERVADO", "MED_2024_06", "2024-06-24", "2024-06-24"),
    ("EDGE_PRIMER_DIA_POST_TRANSICION_20240625", "REGLA_AGREGACION_DIARIA", "MED_2024_06", "2024-06-25", "2024-06-25"),
    ("EDGE_RETIRO_BAJO_20240708", "CAMBIO_RETIRO_OBSERVADO", "MED_2024_07", "2024-07-08", "2024-07-08"),
    ("EDGE_PES_3349_20240806", "PES_ENERGIZACION_TRANSFORMADOR", "V4_S05", "2024-08-06", "2024-08-06"),
    ("EDGE_EO_3349_20240819", "EO_FORMAL_AMPLIACION", "V2_CEN_NUP3349", "2024-08-19", "2024-08-19"),
]
v4_rows = read_csv(V4_EVENTS)
assert len(v4_rows) == len(v4_specs)
for i, (r, spec) in enumerate(zip(v4_rows, v4_specs), 2):
    eid, kind, sources_id, start, end = spec
    assert r["fecha_local"].startswith(start), (r, spec)
    measurement = kind == "CAMBIO_RETIRO_OBSERVADO"
    ts = te = us = ue = None
    if measurement:
        if start == "2024-07-08":
            ts, te = "2024-07-08T09:00:00-04:00", "2024-07-08T20:30:00-04:00"
            us, ue = "2024-07-08T13:00:00Z", "2024-07-09T00:30:00Z"
        else:
            ts = te = r["fecha_local"].replace(" ", "T") + "-04:00"
            us = ue = r["etiqueta_utc"].replace(" ", "T")
    add(eid, "EDGE_COLINA", kind, r["hito"], start, end,
        "ETIQUETAS_15_MINUTOS" if measurement else "DIA", r["tipo"].upper(), sources_id,
        V4_EVENTS, i, r["alcance"] + "; no fecha causal adjudicada",
        time_start=ts, time_end=te, utc_start=us, utc_end=ue, phase=r["equipos"],
        realized="RETIRO_MEDIDO_NO_MECANISMO" if measurement else None)

# Hitos adicionales ya consignados en v6: una fila por hecho y su naturaleza.
extras = [
    ("DATALUNA_CAMPUS_201501", "DATALUNA_QUILICURA", "OPERACION_CAMPUS_REFERIDA", "Campus desde enero de 2015 según Google", "2015-01-01", "2015-01-31", "MES", "V6_GOOGLE2018", False, "No asignar apertura a la conexión Libertadores de 2020 ni a primera etiqueta de medidor"),
    ("ASCENTY_CHILE1_INAUGURACION_20201117", "ASCENTY_CHILE1", "INAUGURACION_CORPORATIVA", "Inauguración corporativa Chile 1", "2020-11-17", "2020-11-17", "DIA", "V3_ASCENTY2020", False, "Inauguración posterior al PES; no certifica primera energización ni carga incremental"),
    ("SONDA_ALIMENTADOR_PES_20200909", "SONDA_CHACABUCO", "PES_ALIMENTADOR", "PES del nuevo alimentador Sonda", "2020-09-09", "2020-09-09", "DIA", "V3_ENEL2020", False, "Campus y medidor pendientes; posición inicialmente compartida con Ascenty"),
    ("ASCENTY_CHILE2_SAC_20231122", "ASCENTY_CHILE2", "SOLICITUD_CONEXION", "Solicitud de acceso/conexión referida en minuta", "2023-11-22", "2023-11-22", "DIA", "V6_ASCENTY2", False, "Solicitud no demuestra ejecución ni operación"),
    ("ASCENTY_CHILE2_PES_PREVISTA_202608", "ASCENTY_CHILE2", "PES_PREVISTA", "PES proyectada para agosto de 2026 en minuta de 2025", "2026-08-01", "2026-08-31", "MES_PREVISTO", "V6_ASCENTY2", True, "No convertir la fecha prevista en realizada aunque el mes ya haya transcurrido"),
    ("ODATA_ST02_CARTA_20251124", "ODATA_SAN_BERNARDO", "CARTA_ESTADO_PROYECTO", "Carta refiere ST02 y subestación en PES", "2025-11-24", "2025-11-24", "DIA_DOCUMENTO", "V6_ODATA_ST02", False, "Fecha de carta, no de entrada del campus ni de inicio exacto del PES"),
    ("ODATA_ST02_EO_ESTIMADA_202511", "ODATA_SAN_BERNARDO", "EO_PREVISTA", "EO estimada para noviembre de 2025", "2025-11-01", "2025-11-30", "MES_PREVISTO", "V6_ODATA_ST02", True, "Realización no acreditada; evitar simultaneidad falsa con fecha de carta"),
    ("SANTA_TERESA_PRESENTACION_20250818", "SANTA_TERESA_LAMPA", "PRESENTACION_AMPLIACION", "Presentación de ampliación Santa Teresa", "2025-08-18", "2025-08-18", "DIA_DOCUMENTO", "V6_SANTA_TERESA", False, "NUP/fases por conciliar; presentación no equivale a obra realizada"),
    ("CIRION_DIA_20230522", "CIRION_QUILICURA", "INGRESO_DIA", "Ingreso de declaración de impacto ambiental", "2023-05-22", "2023-05-22", "DIA_DOCUMENTO", "V6_CIRION_DIA", False, "Falta adjudicar equivalencia DIA/SAN2, medidor, conexión y energización"),
]
for eid, cid, kind, description, start, end, precision, sid, forecast, note in extras:
    row = next(i for i, r in enumerate(raw_centers, 2) if r["candidato_id"] == cid)
    add(eid, cid, kind, description, start, end, precision, "HITO_HEREDADO_REGISTRO_V6", sid,
        CENTER_INPUT, row, note, is_forecast=forecast)

assert len(events) == 24 and len({r["evento_id"] for r in events}) == len(events)
assert all(r["fecha_tratamiento_causal"] is None and r["cohorte_g"] is None and r["elegible_causal"] is False for r in events)
assert all(r["fecha_desde"] is None or r["fecha_desde"] <= r["fecha_hasta"] for r in events)
events_df = write("eventos_documentados", events)
for endpoint in ("desde", "hasta"):
    labeled = events_df[events_df[f"etiqueta_local_{endpoint}"].notna()]
    local_utc = pd.to_datetime(labeled[f"etiqueta_local_{endpoint}"], utc=True)
    original_utc = pd.to_datetime(labeled[f"etiqueta_utc_{endpoint}"], utc=True)
    assert (local_utc == original_utc).all(), f"Etiquetas UTC/local incompatibles: {endpoint}"

# El registro no es una matriz de adyacencia contemporánea. Desde/hacia son
# etiquetas del documento y no sentidos de flujo; no completar pares faltantes.
net = []
for i, r in enumerate(read_csv(NETWORK_INPUT), 2):
    ids = ["V4_" + s for s in r["fuente"].split(";")]
    assert all(s in source_map for s in ids)
    description = r["fecha_o_estado_evidencia"]
    typ = ("PROYECCION" if "proyecto" in description else
           "DISENO_O_ANTECEDENTE" if "diseño" in description or "antecedente" in description else
           "INSTANTANEA_O_EVENTO_POSTERIOR" if "instantanea" in description or "evento" in description else
           "HITO_OPERACIONAL_DOCUMENTADO")
    net.append(dict(conexion_id=f"RED_{i-1:03d}", nodo_desde_documental=r["desde"], nodo_hasta_documental=r["hacia"],
                    tension_documental=r["tension_kV"], circuito_o_pano=r["circuito_o_pano"],
                    fecha_o_estado_evidencia=description, tipo_evidencia=typ,
                    fuente_ids=";".join(ids), fuentes_url=";".join(source_map[s]["url"] for s in ids),
                    paginas_pdf_1based=r["paginas_pdf_1based"], limite=r["limite"],
                    vigencia_operativa_desde=None, vigencia_operativa_hasta=None,
                    vigencia_operativa_validada=False, utilizable_W_causal=False,
                    peso_exposicion=None, estado_interruptor=None, flujo_horario=None,
                    interpretacion_par_no_registrado="DESCONOCIDO_NO_CERO",
                    tabla_origen=NETWORK_INPUT, tabla_origen_fila=i))
net_df = write("conexiones_red_documentadas", net)

# Verificar todas las copias originales con hash declarado que siguen presentes.
source_checks = []
for s in sources:
    path = ROOT / s["archivo_original_local"] if s["archivo_original_local"] else None
    observed = sha(path) if path and path.is_file() and s["sha256_original_declarado"] else None
    if observed:
        assert observed == s["sha256_original_declarado"], s["fuente_id"]
    source_checks.append(dict(fuente_id=s["fuente_id"], archivo_local_existe=bool(path and path.is_file()),
                              hash_original_verificado=bool(observed)))
sources_df = write("fuentes_eventos_red", sources)

report = dict(version="2026-09-25", entradas_sha256=INPUTS, salidas=OUTPUTS,
              esquemas=SCHEMAS, comprobacion_fuentes=source_checks,
              n_eventos=len(events), n_centros_candidatos=9, n_barras_sin_centro=1,
              n_establecimientos_independientes_cerrados=0, n_cohortes_causales_cerradas=0,
              verificaciones=["claves únicas", "integridad referencial centro_id y fuentes", "orden de fechas",
                              "todos los g y fechas causales nulos", "ninguna fecha prevista usada como realizada",
                              "etiquetas horarias UTC y locales consistentes",
                              "lectura Parquet idéntica al DataFrame", "hashes originales disponibles coinciden"],
              advertencia="24 hitos no equivalen a 24 entradas; 9 candidatos no equivalen a 9 centros independientes. No estima ATT, DiD ni spillovers.")
(DOC / "verificacion_eventos_relaciones.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v["filas"] for k, v in OUTPUTS.items()}, ensure_ascii=False, indent=2))
