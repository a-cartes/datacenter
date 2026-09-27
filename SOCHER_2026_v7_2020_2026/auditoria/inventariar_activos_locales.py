"""Auditoría local acotada: disponibilidad de archivos y candidatos eléctricos.

No descarga, no modifica fuentes, no extrae las mediciones nacionales y no
adjudica tratamientos. Las carpetas vacías no cuentan como cobertura observada.
"""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import gzip
import hashlib
import json
import os
import re
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
AS_OF = "2026-09-27"
SOURCES = {}


def rows(rel, sep=","):
    p = ROOT / rel
    SOURCES[rel] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "rt", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=sep))


def classify(p):
    name = p.name.lower()
    full = str(p).lower()
    state = "definitivo" if "definiti" in full else "preliminar" if "preliminar" in full else "sin_version_adjudicada"
    typ = ("puntos_medida_15min" if "puntos_de_medida" in name else
           "medidas_estimadas_15min" if "estimada" in name else
           "medidas_incompletas_15min" if "incompleta" in name else
           "transferencia_regional_xlsx" if p.suffix.lower() == ".xlsx" else "otro")
    return typ, state


files, annual = [], []
for year in range(2020, 2027):
    folder = ROOT / str(year)
    current = []
    for p in sorted(folder.rglob("*")) if folder.exists() else []:
        if not p.is_file() or p.name.startswith("."):
            continue
        rel = p.relative_to(ROOT)
        month = next((int(x[:2]) for x in rel.parts[1:-1] if re.match(r"^(0[1-9]|1[0-2])_", x)), None)
        typ, state = classify(rel)
        record = {"ruta": str(rel), "anio_carpeta": year, "mes_carpeta": month,
                  "bytes": p.stat().st_size, "extension": p.suffix.lower(), "tipo_por_nombre": typ,
                  "version_por_ruta": state, "integridad_datos_validada_en_esta_auditoria": False}
        if p.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(p) as archive:
                    members = [i for i in archive.infolist() if not i.is_dir()]
                    record["zip_directorio_central_legible"] = True
                    record["miembros"] = [{"nombre": i.filename, "bytes_declarados": i.file_size,
                                           "bytes_comprimidos": i.compress_size} for i in members]
                    record["zip_crc_contenido_verificado"] = False
            except (zipfile.BadZipFile, OSError) as exc:
                record["zip_directorio_central_legible"] = False
                record["error_apertura_zip"] = type(exc).__name__
        current.append(record)
    monthly = []
    for month in range(1, 13):
        month_rows = [r for r in current if r["mes_carpeta"] == month]
        monthly.append({"mes": month, "archivos": len(month_rows),
                        "tipos": dict(Counter(r["tipo_por_nombre"] for r in month_rows)),
                        "versiones": dict(Counter(r["version_por_ruta"] for r in month_rows)),
                        "hay_medida_15min_definitiva_por_nombre": any(r["tipo_por_nombre"] == "puntos_medida_15min" and r["version_por_ruta"] == "definitivo" for r in month_rows),
                        "estado": "archivos_presentes_sin_adjudicar_cobertura_centro" if month_rows else
                                  "periodo_futuro" if year == 2026 and month > 9 else "sin_archivos_locales"})
    current_months = [r["mes"] for r in monthly if r["archivos"]]
    annual.append({"anio": year, "archivos": len(current), "bytes": sum(r["bytes"] for r in current),
                   "extensiones": dict(Counter(r["extension"] for r in current)),
                   "meses_con_archivos": current_months,
                   "meses_sin_archivos": [m for m in range(1, 13) if m not in current_months],
                   "archivos_sin_mes_de_carpeta": [r["ruta"] for r in current if r["mes_carpeta"] is None],
                   "detalle_mensual": monthly})
    files.extend(current)

# Los Parquet de la raíz son resúmenes derivados, no archivos de precios por
# definición del formato. Se registran por nombre sin homologarlos con el original.
parquets = []
for p in sorted(ROOT.glob("20*.parquet")):
    match = re.match(r"(202[0-6])_(\d{2})_", p.name)
    if match:
        parquets.append({"ruta": p.name, "anio_nombre": int(match[1]), "mes_nombre": int(match[2]),
                         "bytes": p.stat().st_size, "estado": "derivado_existente_no_revalidado"})

# Archivos mensuales de CMg y homologaciones: solo metadata, sin leer valores.
price_assets = []
excluded = {".venv", ".git", "node_modules", "__pycache__", "SOCHER_2026_repositorio", "SOCHER_2026_v7_2020_2026"}
for base, dirs, names in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in excluded and not d.startswith(".")]
    for name in names:
        low = name.lower()
        match = re.search(r"cmg[_ -]?(2[0-6])(0[1-9]|1[0-2])", low)
        match_homo = re.search(r"homologacion_(202[0-6])(0[1-9]|1[0-2])", low)
        suffix = Path(name).suffix.lower()
        if suffix not in {".xlsx", ".xlsm", ".zip"} or not (match or match_homo):
            continue
        p = Path(base) / name
        year, month = (2000 + int(match[1]), int(match[2])) if match else (int(match_homo[1]), int(match_homo[2]))
        kind = "homologacion" if "homolog" in low else "libro_cmg" if suffix == ".xlsm" else "paquete_cmg" if suffix == ".zip" else "otro_libro"
        price_assets.append({"ruta": str(p.relative_to(ROOT)), "anio_nombre": year, "mes_nombre": month,
                             "tipo": kind, "bytes": p.stat().st_size, "archivo_repetido_posible": True,
                             "limite": "La presencia no es validación de cobertura ni identidad; copias no se suman como datos nuevos"})

centers = rows("SOCHER_2026_v6_multicentros/mapeo/registro_centros_candidatos.csv")
relations = rows("SOCHER_2026_v6_multicentros/mapeo/relacion_centros_barras.csv")
homology = rows("SOCHER_2026_v6_multicentros/precios/homologacion_candidatos_mensual.csv")
entity_inventory = rows("SOCHER_2026_v6_multicentros/precios/inventario_entidades_busqueda.csv")
old_prices = rows("SOCHER_2026_v3/precios/CEN_CMg_historicos_locales_2023_20240714_deduplicado.csv", ";")
dataluna = rows("SOCHER_2026_v3/consumo/dataluna_conciliacion_mensual.csv")

by_history = defaultdict(list)
for r in homology:
    if r["nemotecnico"]:
        by_history[(r["barra_cmg"], r["nemotecnico"])].append(r)
targets = []
for i, r in enumerate(relations, 1):
    targets.append(dict(objetivo_id=f"REL_{i:02d}", **r,
                        clase_objetivo="campus_o_conexion_candidata" if r["centro_id"] != "QUILICURA_SIN_DC_ADJUDICADO" else "barra_sin_centro_adjudicado",
                        es_barra_tratada_validada=False, continuidad_historica_validada=False))

extra = [
    ("EDGE_COLINA", "CANTERAS______023", "campus_nivel_23kV_BP1", "Identidad del activo; no adjudica todas las barras BP2 ni transforma trafo en centro"),
    ("EDGE_COLINA", "CHICUREO______023", "suministro_proyectado_23kV", "Antecedente de proyecto; realización y ruta hacia campus pendientes"),
    ("QUILICURA_SIN_DC_ADJUDICADO", "QUILICURA_____013", "barra_sin_centro_adjudicado", "No adjudicar por comuna"),
    ("QUILICURA_SIN_DC_ADJUDICADO", "QUILICURA_____023", "barra_sin_centro_adjudicado", "No adjudicar por comuna"),
    (None, "QUILLOTA______110", "referencia_diferencial", "Referencia del resultado; no control no expuesto acreditado"),
    (None, "QUILLOTA______220", "referencia_diferencial_alternativa", "Referencia alternativa; nivel de tensión distinto de Quillota110"),
    (None, "C.NAVIA_______110", "red_corredor", "Extremo de corredor; la exposición temporal debe documentarse"),
    (None, "C.NAVIA_______220", "red_otro_nivel_tension", "No intercambiable con110; enlace de transformación por considerar"),
    (None, "L.VEGAS_______110", "red_corredor_BP1", "BP1 distinta de BP2; no presuponer acoplamiento"),
    (None, "L.VEGAS2______110", "red_corredor_BP2", "BP2 distinta de BP1; no presuponer acoplamiento"),
    (None, "L.VEGAS_______044", "red_otro_nivel_tension", "Nivel de tensión auxiliar; no referencia automática de110"),
    (None, "L.VEGAS_______013", "red_otro_nivel_tension", "Nivel de tensión auxiliar; no referencia automática de110"),
]
for j, (cid, label, kind, limit) in enumerate(extra, 1):
    targets.append({"objetivo_id": f"AMP_{j:02d}", "centro_id": cid, "barra_cmg": label,
                    "nemotecnico": None, "clase_objetivo": kind, "limitacion": limit,
                    "fuente": "SOCHER_2026_v4/territorio/registro_barras.csv;SOCHER_2026_v3/mapeo/Memo_mapeo_electrico_y_unidades.md",
                    "es_barra_tratada_validada": False, "continuidad_historica_validada": False})

history = []
labels_wanted = {r["barra_cmg"] for r in targets if r.get("barra_cmg")}
# La variante literal LAMPA________023 conserva su identidad por etiqueta y
# nemotécnico; no se empalma automáticamente con LAMPA_________023.
labels_wanted.add("LAMPA________023")
for (label, code), records in sorted(by_history.items()):
    if label not in labels_wanted:
        continue
    history.append({"barra_cmg": label, "nemotecnico": code,
                    "meses_con_evidencia": sorted({r["mes_fuente"] for r in records}),
                    "meses_homologacion_exacta": sorted({r["mes_fuente"] for r in records if r["estado_identidad"] == "homologacion_mensual_exacta"}),
                    "meses_provisionales": sorted({r["mes_fuente"] for r in records if r["estado_identidad"] != "homologacion_mensual_exacta"}),
                    "nombres_fisicos": sorted({r["barra_aux"] for r in records}),
                    "archivos_homologacion": sorted({r["archivo_homologacion"] for r in records}),
                    "continuidad_con_otros_codigos": "NO_ADJUDICADA"})

historical_price_summary = []
for year in range(2020, 2027):
    group = [r for r in old_prices if r["fecha"].startswith(str(year))]
    if group:
        historical_price_summary.append({"anio": year, "filas": len(group), "desde": min(r["fecha"] for r in group),
                                          "hasta": max(r["fecha"] for r in group),
                                          "codigos": sorted({r["barra_mnemotecnico"] for r in group}),
                                          "archivo": "SOCHER_2026_v3/precios/CEN_CMg_historicos_locales_2023_20240714_deduplicado.csv"})

derived_summary = {
    "precios_historicos_archivados_v3": historical_price_summary,
    "precios_2024_v6": {"archivo": "SOCHER_2026_v6_multicentros/precios/CEN_panel_barra_hora_identificado_hasta_20240714.parquet",
                        "filas_ya_verificadas": 178016, "identidades_historicas_ya_verificadas": 83,
                        "meses": ["2024-02", "2024-04", "2024-05", "2024-06", "2024-07-01/14"],
                        "limite": "83 identidades no son establecimientos; mayo tiene códigos provisionales"},
    "precios_regimen_nuevo_2024": {"archivo": "SOCHER_2026_v3/precios/CMg_nuevo_cinco_barras_horas_originales.csv.gz",
                                   "desde": "2024-07-15", "hasta": "2024-12-31", "filas_horarias_ya_verificadas": 4080,
                                   "barras": ["CANTERAS______110", "QUILLOTA______110", "QUILLOTA______220", "C.NAVIA_______110", "C.NAVIA_______220"],
                                   "limite": "Mantener régimen y reloj separados; no empalme automático con libros anteriores"},
    "dataluna_regional": {"archivo": "SOCHER_2026_v3/consumo/dataluna_horario_2020_2022.csv.gz",
                           "meses_extraidos": len(dataluna), "desde": min(r["desde"] for r in dataluna),
                           "hasta": max(r["hasta"] for r in dataluna),
                           "unidad_verificada": False, "limite": "Serie firmada de etiqueta DATALUNA; no carga incremental validada ni primera entrada"},
    "canteras_15min_2024": {"archivo": "SOCHER_2026_v3/consumo/las_canteras_transformadores_15min_2024.csv.gz",
                            "filas_ya_verificadas": 67384, "campus_grupo_id": "EDGE_COLINA",
                            "limite": "HT1/HT2 y HT3 separados; falta consumo de los otros candidatos"},
}
price_gaps = {
    "2020": "No se encontraron libros CMg mensuales ni panel nodal auditado de ese año en el alcance local.",
    "2021": "No se encontraron libros CMg mensuales ni panel nodal auditado de ese año en el alcance local.",
    "2022": "No se encontraron libros CMg mensuales ni panel nodal auditado de ese año en el alcance local.",
    "2023": "Solo exportaciones históricas de Quillota110/220 y Quilicura110; faltan precios multicentro y homologaciones mensuales.",
    "2024": "Multicentro: faltan enero/marzo, homologación exacta de mayo, y extensión desde15jul para los demás nodos. Hay cinco barras bajo nuevo régimen hasta diciembre.",
    "2025": "Mediciones nacionales disponibles; no se encontraron precios CMg ni homologación horaria multibarra de2025 en el alcance local.",
    "2026": "Mediciones disponibles enero–junio; julio–septiembre sin archivos locales y octubre–diciembre futuros al corte. No se encontraron precios CMg multibarra de2026 en el alcance local.",
}

report = {"fecha_corte": AS_OF, "ejecucion_utc": datetime.now(timezone.utc).isoformat(),
          "alcance": "Workspace actual: carpetas2020–2026, Parquet de raíz y fuentes históricas v2/v3/v4/v6; excluye checkout duplicado, entornos y descargas externas.",
          "agentes_instrucciones": "No se encontró AGENTS.md en los ancestros consultados.",
          "limites": ["Disponibilidad de archivos no prueba cobertura ni carga de cada centro.", "Lectura de directorio central ZIP no verifica CRC de su contenido.",
                      "No se consultó toda la carpeta personal ni Downloads fuera del workspace.", "No se estiman efectos ni se asignan cohortes.",
                      "No se fusionan códigos, etiquetas Lampa, niveles de tensión o fases sin documentación."],
          "resumen_anual": annual, "archivos_en_carpetas_anuales": files, "parquet_derivados_en_raiz": parquets,
          "activos_mensuales_cmg": price_assets, "huecos_precios_por_anio": price_gaps,
          "extractos_reutilizables": derived_summary, "centros_candidatos_v6": centers,
          "objetivos_barras_y_conexiones": targets, "identidades_historicas_objetivo": history,
          "otras_entidades_solo_para_busqueda": entity_inventory, "fuentes_tabulares_sha256": SOURCES,
          "scripts_reutilizables": ["SOCHER_2026_v4/scripts/extraer_cmg_mensual_cen.py", "SOCHER_2026_v6_multicentros/scripts/ampliar_panel_barra_hora.py",
                                    "SOCHER_2026_v6_multicentros/scripts/construir_registro_centros.py", "SOCHER_2026_v3/scripts/reconstruir_consumo_dataluna.py",
                                    "SOCHER_2026_dataset/scripts/construir_mediciones.py"]}
(OUT / "Inventario_local_2020_2026.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

lines = ["# Activos locales para ampliar la base 2020–2026", "", f"Corte: {AS_OF}. Auditoría local de disponibilidad; no extracción nacional nueva ni estimación causal.", "",
         "## Archivos existentes y huecos", "", "| Año | Archivos en carpeta anual | Meses con archivos | Precios y faltantes principales |", "|---|---:|---|---|"]
for a in annual:
    lines.append(f"| {a['anio']} | {a['archivos']} | {', '.join(str(m) for m in a['meses_con_archivos'])} | {price_gaps[str(a['anio'])]} |")
lines += ["", "Las carpetas de meses vacías no cuentan como observaciones. Los archivos anuales son principalmente **mediciones/transferencias, no precios CMg**. En 2020–2022 predominan libros regionales con varias versiones. En2023 conviven libros regionales y archivos de puntos de medida; desde2024 predominan los ZIP de mediciones a15min. Mantener separados real, estimado e incompleto y elegir versión con trazabilidad.", "",
          f"Hay {len(parquets)} Parquet derivados con prefijo anual en la raíz. Son productos previos y no sustituyen la inspección de encabezados/unidades/identidad de los libros originales. El inventario anterior `SOCHER_2026_v2/evidencia/inventario_parquet_verificado.csv` documenta claves y etiquetas faltantes en varios productos; no aceptarlos como panel causal por su extensión Parquet.", "",
          "## Fuentes aprovechables ahora", ""]
for key, value in derived_summary.items():
    if isinstance(value, list):
        for item in value:
            lines.append(f"- **{key}, {item['anio']}**: `{item['archivo']}`; {item['filas']} filas, {item['desde']}–{item['hasta']}, {len(item['codigos'])} códigos. No cubre todos los centros.")
    else:
        lines.append(f"- **{key}**: `{value['archivo']}`. {value.get('limite', '')}")
lines += ["", "Los libros mensuales de CMg de2024 conservados cubren febrero, abril, mayo, junio y julio. Enero y marzo tienen homologaciones recuperadas, pero no libro completo utilizable en esta capa. Mayo sigue sin homologación mensual exacta. No se encontraron ZIP mensuales CMg completos adicionales dentro de este workspace; los ZIP nacionales de las carpetas anuales son mediciones. Descargas externas al workspace quedan fuera de esta revisión.", "",
          "## Centros, conexiones y barras objetivo", "", "El registro contiene nueve filas candidatas de campus/proyecto y una fila de S/E Quilicura sin centro adjudicado. Ascenty Chile1/2 comparte un grupo por delimitar; los transformadores de EdgeConneX son fases/equipos del mismo campus. **Las83 claves históricas no son83 establecimientos.**", "",
          "| Candidato | Barras o equipos a investigar | Límite principal |", "|---|---|---|"]
for c in centers:
    connected = [r["barra_cmg"] or r["barra_fisica_o_propuesta"] for r in relations if r["centro_id"] == c["candidato_id"]]
    lines.append(f"| {c['candidato_id']} | {'; '.join(connected) or 'Sin conexión adjudicada'} | {c['pendiente']} |")
lines += ["", "Añadir Canteras23 y Chicureo23 como niveles documentados sujetos a vigencia; Quillota110/220 como referencias explícitas; Cerro Navia110/220 y Las Vegas110 BP1/BP2,44 y13 como nodos del corredor o niveles auxiliares. Una barra de referencia no se declara automáticamente control no expuesto.", "",
          "Nueva Lampa220, Santa Teresa220, ODATA110/13 y Panamericana110 requieren homologación propia. **PANAMERICANA__012 no sustituye Panamericana110.** Cirion no tiene barra adjudicada. La comuna Quilicura no autoriza asignar S/E Quilicura a Google, Ascenty o Cirion.", "",
          "## Identidad histórica: conservar separada", "", "| Etiqueta CMg | Código observado | Meses con evidencia en el inventario v6 | Exactos / provisionales |", "|---|---|---|---|"]
for r in history:
    lines.append(f"| `{r['barra_cmg']}` | `{r['nemotecnico']}` | {', '.join(r['meses_con_evidencia'])} | {', '.join(r['meses_homologacion_exacta'])} / {', '.join(r['meses_provisionales']) or '—'} |")
lines += ["", "Chacabuco, Chicureo, Quilicura y Lampa muestran códigos T0054/T0835 en las publicaciones examinadas. No se adjudica continuidad física solo por igualdad de nombre. Las etiquetas `LAMPA________023` y `LAMPA_________023` también se conservan explícitas. Los códigos de julio2024 del registro de candidatos no certifican vigencia en2020–2026.", "",
          "## Decisiones inmediatas de construcción", "", "1. Extraer mediciones reales definitivas disponibles2023–2026 para los sockets candidatos y conservar canales/signos; auditar las versiones regionales2020–2022 por separado.",
          "2. Obtener precios y homologaciones de cada año/período para las barras objetivo; aprovechar los extractos existentes como controles de solapamiento, sin duplicarlos.",
          "3. Mantener un panel único barra×etiqueta horaria y tablas separadas de centros, fases, vínculos y eventos. No multiplicar filas de precio por número de centros asociados.",
          "4. Cerrar identidad temporal y reloj antes de unir carga y precio; mantener desconocidos como nulos y cualquierfecha causal sin adjudicar.", "",
          "El JSON acompaña el inventario completo de archivos, miembros declarados de ZIP, rutas reutilizables, mapeo y hashes de los registros pequeños utilizados. No modifica fuentes ni declara integridad del contenido nacional solo por leer el directorio ZIP."]
text = "\n".join(lines) + "\n"
# Separación legible en la prosa, sin tocar nombres/rutas/códigos dentro de tablas.
for a, b in [("En2023", "En 2023"), ("desde2024", "desde 2024"), ("a15min", "a 15 min"), ("de2024", "de 2024"), ("Las83", "Las 83"), ("son83", "son 83"), ("julio2024", "julio de 2024"), ("en2020", "en 2020"), ("disponibles2023", "disponibles 2023"), ("regionales2020", "regionales 2020"), ("cualquierfecha", "cualquier fecha")]:
    text = text.replace(a, b)
(OUT / "Inventario_local_2020_2026.md").write_text(text, encoding="utf-8")
print(json.dumps({"archivos_anuales": len(files), "parquet_derivados_raiz": len(parquets),
                  "archivos_cmg_homologacion_incluyendo_copias": len(price_assets), "objetivos_documentales": len(targets),
                  "identidades_historicas_objetivo": len(history), "zip_con_error_directorio_central": sum(r.get("zip_directorio_central_legible") is False for r in files),
                  "rutas": [str(OUT / "Inventario_local_2020_2026.json"), str(OUT / "Inventario_local_2020_2026.md")]}, ensure_ascii=False, indent=2))
