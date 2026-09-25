"""Construye la capa de mediciones desde extractos auditados, sin inferir tratamientos.

No descarga ni abre ZIP nacionales. Conserva las etiquetas del publicador y deja
el enlace a precios deshabilitado hasta conciliar inicio/fin y hora de publicación.
Ejecutar con .venv/bin/python (pandas, numpy y pyarrow).
"""
from pathlib import Path
import hashlib
import json
import platform
import sys

import numpy as np
import pandas as pd
import pyarrow


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
V3 = ROOT / "SOCHER_2026_v3/consumo"
TABLES = BASE / "tablas"
CHECKS = BASE / "controles"
DOCS = BASE / "documentacion"
SOCKETS = [f"LSCANTRS_110_HT{i}_EDG" for i in (1, 2, 3)]
RAW = ["archivo_original", "miembro_zip", "ID_SOC", "IDSOCKET", "SUBESTACION",
       "TENSION", "YEARX", "MONX", "DAYX", "HOURX", "DATETIME", "UTCDATETIME",
       "kWhD", "kWhR", "FLUJO", "ULTIMA_LECTURA"]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def provenance(path):
    return {"archivo": str(path.relative_to(ROOT)), "sha256": digest(path),
            "bytes": path.stat().st_size}


def write_pair(frame, name):
    paths = [TABLES / f"{name}.csv.gz", TABLES / f"{name}.parquet"]
    frame.to_csv(paths[0], index=False, compression={"method": "gzip", "mtime": 0})
    frame.to_parquet(paths[1], index=False)
    restored = pd.read_parquet(paths[1])
    pd.testing.assert_frame_equal(frame, restored)
    return paths


def write_dictionary(d, hourly):
    shared = {
        "centro_id": ("identificador", "Campus candidato EDGE_COLINA del registro multicentro; no tratamiento asignado."),
        "campus_grupo_id": ("identificador", "Agrupa fases y transformadores del mismo campus, sin contarlos como centros independientes."),
        "fecha_local": ("fecha", "Fecha de la etiqueta DATETIME del publicador."),
        "mes_local": ("mes", "Año y mes de la etiqueta DATETIME del publicador."),
        "offset_local_minutos": ("minutos", "DATETIME menos UTCDATETIME. Verificado contra America/Santiago en observaciones presentes."),
        "sentido_etiqueta_inicio_fin": ("categoría", "NO_ACREDITADO: no se confirmó si la etiqueta marca inicio o fin físico del intervalo."),
        "enlace_precio_habilitado": ("booleano", "Siempre false hasta conciliar las convenciones de medición y precios. No es indicador de tratamiento."),
    }
    detail = {
        "archivo_original": ("ruta", "ZIP nacional original registrado por la extracción v3; no se reabre en esta construcción."),
        "miembro_zip": ("nombre", "Miembro CSV dentro del ZIP original."),
        "ID_SOC": ("identificador fuente", "Código del publicador preservado literalmente."),
        "IDSOCKET": ("identificador fuente", "Socket del publicador preservado literalmente."),
        "SUBESTACION": ("texto fuente", "Nombre original de subestación."),
        "TENSION": ("kV fuente", "Etiqueta original de tensión; no modifica la energía publicada."),
        "YEARX": ("año fuente", "Año literal del registro original."),
        "MONX": ("mes fuente", "Mes literal del registro original."),
        "DAYX": ("día fuente", "Día literal del registro original."),
        "HOURX": ("hora fuente", "Hora literal del registro de medición, verificada frente a DATETIME; no es la hora 1–25 de precios."),
        "DATETIME": ("texto temporal fuente", "Etiqueta local íntegra, preservada sin desplazar."),
        "UTCDATETIME": ("texto temporal fuente", "Etiqueta UTC íntegra del publicador, preservada sin desplazar."),
        "kWhD": ("kWh fuente", "Energía delivered original como texto; decimal original preservado."),
        "kWhR": ("kWh fuente", "Energía received original como texto; decimal original preservado."),
        "FLUJO": ("código fuente", "Clasificación original, preservada; no sustituye validación histórica de polaridad."),
        "ULTIMA_LECTURA": ("texto temporal fuente", "Metadato original de última lectura. No usado como reloj de observación."),
        "fila_extracto_anual": ("fila CSV", "Número de fila del CSV anual descomprimido, cabecera en fila 1."),
        "fila_extracto_mensual": ("fila CSV", "Número de fila del extracto mensual descomprimido, cabecera en fila 1."),
        "extracto_mensual": ("ruta", "Extracto mensual que contiene la observación original."),
        "sha256_extracto_mensual": ("SHA-256", "Huella del extracto mensual verificada contra su manifiesto v3."),
        "sha256_zip_previamente_registrado": ("SHA-256", "Huella del ZIP consignada por extracción v3; no recalculada en este script."),
        "extracto_anual": ("ruta", "Tabla anual de transformadores usada como entrada."),
        "sha256_extracto_anual": ("SHA-256", "Huella recalculada del extracto anual usado."),
        "medidor_id": ("identificador", "Copia explícita de IDSOCKET para clave medidor por etiqueta UTC."),
        "pano": ("identificador", "HT1, HT2 o HT3 extraído del identificador exacto."),
        "etiqueta_utc": ("timestamp UTC", "UTCDATETIME convertido a tipo temporal con UTC; no inferencia de inicio/fin físico."),
        "etiqueta_local_original": ("texto temporal fuente", "Copia explícita de DATETIME."),
        "hora_local_fuente": ("hora 0–23", "Hora de DATETIME, sin convertirla a hora de precios."),
        "minutos_intervalo_documentados": ("minutos", "15 minutos según documentación de energía y configuración auditadas."),
        "energia_D_kwh": ("kWh", "Canal D convertido a número sin multiplicadores adicionales."),
        "energia_R_kwh": ("kWh", "Canal R convertido a número sin multiplicadores adicionales."),
        "potencia_media_D_mw": ("MW", "energia_D_kwh / 250: potencia media del intervalo de 15 minutos."),
        "potencia_media_R_mw": ("MW", "energia_R_kwh / 250: potencia media del intervalo de 15 minutos."),
        "incluido_suma_HT1_HT2": ("booleano", "True solo en HT1 y HT2, elegibles para suma de retiro validado de esos transformadores."),
        "estado_polaridad": ("categoría", "HT1/HT2 cuentan con actas históricas D=retiro. HT3 mantiene orientación pendiente."),
        "retiro_validado_kwh": ("kWh", "Canal D en HT1/HT2. Nulo en HT3; nulo nunca se interpreta como cero."),
        "naturaleza_medicion": ("categoría", "Medición eléctrica del transformador; no medición aislada de servidores ni carga IA."),
    }
    hdesc = {
        "hora_utc_etiqueta": ("timestamp UTC", "Piso horario de UTCDATETIME. Identifica agrupación de etiquetas, no una hora física certificada."),
        "n_intervalos_presentes": ("conteo", "Número de etiquetas temporales en la unión de HT1 y HT2 del bloque."),
        "n_intervalos_validos": ("conteo", "Número de etiquetas con ambos canales D válidos y simultáneos."),
        "n_intervalos_HT1": ("conteo", "Número de observaciones D no nulas de HT1 en el bloque."),
        "n_intervalos_HT2": ("conteo", "Número de observaciones D no nulas de HT2 en el bloque."),
        "energia_HT1_kwh": ("kWh", "Suma de cuatro etiquetas de HT1, disponible solo si el bloque conjunto está completo."),
        "energia_HT2_kwh": ("kWh", "Suma de cuatro etiquetas de HT2, disponible solo si el bloque conjunto está completo."),
        "energia_HT1_HT2_kwh": ("kWh", "Suma de HT1 y HT2 con ambos presentes en 00, 15, 30 y 45 minutos UTC. No incluye HT3 ni líneas."),
        "etiqueta_local_primera": ("texto temporal fuente", "Primera DATETIME entre las cuatro etiquetas del bloque."),
        "etiqueta_local_ultima": ("texto temporal fuente", "Última DATETIME entre las cuatro etiquetas del bloque."),
        "n_offsets": ("conteo", "Número de offsets locales diferentes dentro del bloque; se exige uno."),
        "cuatro_etiquetas_correctas": ("booleano", "True si existen exactamente las etiquetas UTC 00, 15, 30 y 45."),
        "n_intervalos_esperados": ("conteo", "Cuatro observaciones de 15 minutos por transformador para cada bloque de una hora."),
        "completo_por_etiquetas": ("booleano", "Ambos transformadores completos en cuatro etiquetas y offset único; no certifica reloj físico."),
        "retiro_HT1_HT2_mw_por_etiquetas": ("MW", "energia_HT1_HT2_kwh / 1000, media en 4×15 minutos. No es consumo total del campus."),
        "punto_medida_id": ("identificador", "LSCANTRS_HT1_HT2: agregado de dos transformadores identificados."),
        "agregacion": ("categoría", "Regla explícita de cuatro etiquetas UTC; inicio/fin físico pendiente."),
        "HT3_incluido": ("booleano", "Siempre false por orientación pendiente de HT3."),
        "representa_consumo_total_campus": ("booleano", "Siempre false: no se han conciliado otros suministros ni todos los componentes del campus."),
        "archivo_fuente_15min": ("ruta relativa", "Capa base de observaciones usada para reconstruir el bloque."),
        "hora_local_etiqueta": ("hora 0–23", "Hora de la primera etiqueta local del bloque; no se usa para unir precios."),
    }
    rows = []
    for name, frame, descriptions in [("carga_medidor_15min", d, detail), ("carga_campus_hora", hourly, hdesc)]:
        for col in frame.columns:
            unit, definition = {**shared, **descriptions}[col]
            rows.append(dict(tabla=name, campo=col, tipo_parquet=str(frame[col].dtype), unidad=unit,
                             tiene_nulos_observados=bool(frame[col].isna().any()), definicion=definition))
    path = DOCS / "diccionario_mediciones.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def main():
    for p in (TABLES, CHECKS, DOCS):
        p.mkdir(parents=True, exist_ok=True)
    inputs = [provenance(ROOT / "SOCHER_2026_v3/mapeo/Memo_mapeo_electrico_y_unidades.md"),
              provenance(ROOT / "SOCHER_2026_v4/eventos/Apendice_configuracion_HT1_HT2.md")]
    annual_path = V3 / "las_canteras_transformadores_15min_2024.csv.gz"
    annual = pd.read_csv(annual_path, dtype=str, keep_default_na=False)
    inputs.append(provenance(annual_path))
    assert len(annual) == 67384
    assert set(annual.IDSOCKET) == set(SOCKETS)
    annual["fila_extracto_anual"] = np.arange(2, len(annual) + 2)
    monthly_parts = []
    source_rows = []
    # Los doce extractos ya preservados permiten comprobar ausencias mensuales.
    for month in range(1, 13):
        p = V3 / f"sockets_seleccionados_2024_{month:02d}.csv.gz"
        m = p.with_name(p.name.replace(".csv.gz", "_manifest.json"))
        manifest = json.loads(m.read_text())
        actual_digest = digest(p)
        assert actual_digest == manifest["sha256_salida"], p
        original = pd.read_csv(p, dtype=str, keep_default_na=False)
        assert len(original) == manifest["registros_seleccionados"]
        original["fila_extracto_mensual"] = np.arange(2, len(original) + 2)
        selected = original[original.IDSOCKET.isin(SOCKETS)].copy()
        selected["extracto_mensual"] = str(p.relative_to(ROOT))
        selected["sha256_extracto_mensual"] = actual_digest
        selected["sha256_zip_previamente_registrado"] = manifest["sha256_zip"]
        monthly_parts.append(selected)
        inputs.extend([provenance(p), provenance(m)])
        source_rows.append({"mes": f"2024-{month:02d}", "filas_extracto_completo": len(original),
                            "filas_transformadores": len(selected), "archivo": str(p.relative_to(ROOT)),
                            "sha256_extracto_verificado": actual_digest,
                            "zip_original_no_reabierto": manifest["archivo"],
                            "sha256_zip_previamente_registrado": manifest["sha256_zip"]})
    monthly = pd.concat(monthly_parts, ignore_index=True)
    key = ["IDSOCKET", "UTCDATETIME"]
    assert not annual.duplicated(key).any()
    assert not monthly.duplicated(key).any()
    a = annual.set_index(key).sort_index()
    m = monthly.set_index(key).sort_index()
    pd.testing.assert_frame_equal(a[RAW[:3] + RAW[4:11] + RAW[12:]],
                                  m[RAW[:3] + RAW[4:11] + RAW[12:]])
    assert a.index.equals(m.index)
    d = annual[RAW + ["fila_extracto_anual"]].merge(
        monthly[key + ["fila_extracto_mensual", "extracto_mensual", "sha256_extracto_mensual",
                       "sha256_zip_previamente_registrado"]], on=key, how="left", validate="one_to_one")
    d["extracto_anual"] = str(annual_path.relative_to(ROOT))
    d["sha256_extracto_anual"] = digest(annual_path)
    d["medidor_id"] = d.IDSOCKET
    d["centro_id"] = "EDGE_COLINA"
    d["campus_grupo_id"] = "EDGE_COLINA"
    d["pano"] = d.IDSOCKET.str.extract(r"_(HT[123])_")[0]
    d["etiqueta_utc"] = pd.to_datetime(d.UTCDATETIME, utc=True, errors="raise")
    local = pd.to_datetime(d.DATETIME, errors="raise")
    d["etiqueta_local_original"] = d.DATETIME
    d["fecha_local"] = local.dt.strftime("%Y-%m-%d")
    d["mes_local"] = local.dt.strftime("%Y-%m")
    d["hora_local_fuente"] = local.dt.hour
    d["offset_local_minutos"] = ((local - d.etiqueta_utc.dt.tz_localize(None)).dt.total_seconds() / 60).astype("int64")
    d["minutos_intervalo_documentados"] = 15
    d["sentido_etiqueta_inicio_fin"] = "NO_ACREDITADO"
    d["enlace_precio_habilitado"] = False
    for channel in ("D", "R"):
        d[f"energia_{channel}_kwh"] = pd.to_numeric(d[f"kWh{channel}"].str.replace(",", ".", regex=False), errors="raise")
        d[f"potencia_media_{channel}_mw"] = d[f"energia_{channel}_kwh"] / 250
        assert d[f"energia_{channel}_kwh"].notna().all()
        assert d[f"energia_{channel}_kwh"].ge(0).all()
        np.testing.assert_allclose(d[f"energia_{channel}_kwh"], annual[f"energia_{channel}_kwh"].astype(float), rtol=1e-13, atol=1e-10)
    d["incluido_suma_HT1_HT2"] = d.pano.isin(["HT1", "HT2"])
    d["estado_polaridad"] = np.where(d.incluido_suma_HT1_HT2,
        "D_RETIRO_R_INYECCION_ACTAS_2023", "HT3_ORIENTACION_PENDIENTE")
    d["retiro_validado_kwh"] = d.energia_D_kwh.where(d.incluido_suma_HT1_HT2)
    d["naturaleza_medicion"] = "energia_electrica_transformador_no_carga_IT_individual"
    assert d.loc[d.incluido_suma_HT1_HT2, "energia_R_kwh"].eq(0).all()
    assert (local.dt.year == pd.to_numeric(d.YEARX)).all()
    assert (local.dt.month == pd.to_numeric(d.MONX)).all()
    assert (local.dt.day == pd.to_numeric(d.DAYX)).all()
    assert (local.dt.hour == pd.to_numeric(d.HOURX)).all()
    assert d.etiqueta_utc.dt.minute.isin([0, 15, 30, 45]).all()
    assert d.etiqueta_utc.dt.second.eq(0).all()
    tz_mismatches = int(local.ne(d.etiqueta_utc.dt.tz_convert("America/Santiago").dt.tz_localize(None)).sum())
    assert tz_mismatches == 0
    d = d.sort_values(["medidor_id", "etiqueta_utc"]).reset_index(drop=True)
    outputs = write_pair(d, "carga_medidor_15min")

    # Se unen únicamente registros simultáneos de los dos transformadores.
    pair = d[d.incluido_suma_HT1_HT2].copy()
    wide = pair.pivot(index="etiqueta_utc", columns="pano", values="energia_D_kwh")
    wide["retiro_par_kwh"] = wide[["HT1", "HT2"]].sum(axis=1, min_count=2)
    pair_times = pair.groupby("etiqueta_utc").agg(n_etiquetas_locales=("DATETIME", "nunique"),
        n_offsets=("offset_local_minutos", "nunique"))
    assert pair_times.n_etiquetas_locales.eq(1).all() and pair_times.n_offsets.eq(1).all()
    meta = pair.drop_duplicates("etiqueta_utc").set_index("etiqueta_utc")
    wide = wide.join(meta[["DATETIME", "fecha_local", "offset_local_minutos", "mes_local"]])
    wide["hora_utc_etiqueta"] = wide.index.floor("h")
    wide["minuto_etiqueta"] = wide.index.minute
    grouped = wide.groupby("hora_utc_etiqueta")
    hourly = grouped.agg(n_intervalos_presentes=("retiro_par_kwh", "size"),
        n_intervalos_validos=("retiro_par_kwh", "count"),
        n_intervalos_HT1=("HT1", "count"), n_intervalos_HT2=("HT2", "count"),
        energia_HT1_kwh=("HT1", lambda s: s.sum(min_count=4)),
        energia_HT2_kwh=("HT2", lambda s: s.sum(min_count=4)),
        energia_HT1_HT2_kwh=("retiro_par_kwh", lambda s: s.sum(min_count=4)),
        etiqueta_local_primera=("DATETIME", "min"), etiqueta_local_ultima=("DATETIME", "max"),
        fecha_local=("fecha_local", "first"), mes_local=("mes_local", "first"),
        offset_local_minutos=("offset_local_minutos", "first"), n_offsets=("offset_local_minutos", "nunique"))
    minute_check = grouped.minuto_etiqueta.agg(lambda s: tuple(sorted(s)) == (0, 15, 30, 45))
    hourly["cuatro_etiquetas_correctas"] = minute_check
    hourly["n_intervalos_esperados"] = 4
    complete = hourly.n_intervalos_validos.eq(4) & hourly.cuatro_etiquetas_correctas & hourly.n_offsets.eq(1)
    hourly["completo_por_etiquetas"] = complete
    for name in ["energia_HT1_kwh", "energia_HT2_kwh", "energia_HT1_HT2_kwh"]:
        hourly[name] = hourly[name].where(complete)
    hourly["retiro_HT1_HT2_mw_por_etiquetas"] = hourly.energia_HT1_HT2_kwh / 1000
    hourly["centro_id"] = "EDGE_COLINA"
    hourly["campus_grupo_id"] = "EDGE_COLINA"
    hourly["punto_medida_id"] = "LSCANTRS_HT1_HT2"
    hourly["agregacion"] = "4_ETIQUETAS_UTC_00_15_30_45_INICIO_FIN_PENDIENTE"
    hourly["sentido_etiqueta_inicio_fin"] = "NO_ACREDITADO"
    hourly["enlace_precio_habilitado"] = False
    hourly["HT3_incluido"] = False
    hourly["representa_consumo_total_campus"] = False
    hourly["archivo_fuente_15min"] = "tablas/carga_medidor_15min.parquet"
    hourly = hourly.reset_index()
    hourly["hora_local_etiqueta"] = pd.to_datetime(hourly.etiqueta_local_primera).dt.hour
    assert not hourly.duplicated(["centro_id", "punto_medida_id", "hora_utc_etiqueta"]).any()
    assert hourly.completo_por_etiquetas.all()
    assert len(hourly) == 7319
    outputs.extend(write_pair(hourly, "carga_campus_hora"))
    outputs.append(write_dictionary(d, hourly))

    # Reconciliación con los resúmenes anteriores: mismas fuentes, no prueba externa.
    daily_source = V3 / "las_canteras_transformadores_diario_2024.csv"
    monthly_source = V3 / "sockets_resumen_mensual_2024.csv"
    inputs.extend([provenance(daily_source), provenance(monthly_source)])
    daily = d.groupby(["IDSOCKET", "fecha_local"]).agg(intervalos=("etiqueta_utc", "size"),
        energia_D_kwh=("energia_D_kwh", "sum"), energia_R_kwh=("energia_R_kwh", "sum")).sort_index()
    daily_old = pd.read_csv(daily_source).set_index(["IDSOCKET", "fecha_local"]).sort_index()
    assert daily.index.equals(daily_old.index)
    np.testing.assert_array_equal(daily.intervalos, daily_old.intervalos)
    daily_errors = {}
    for c in ("D", "R"):
        col = f"energia_{c}_kwh"
        err = float(np.max(np.abs(daily[col] - daily_old[col])))
        daily_errors[c] = err
        np.testing.assert_allclose(daily[col], daily_old[col], rtol=1e-12, atol=1e-7)
    observed_months = d.groupby(["IDSOCKET", "mes_local"]).agg(registros=("etiqueta_utc", "size"),
        energia_D_kwh=("energia_D_kwh", "sum"), energia_R_kwh=("energia_R_kwh", "sum")).sort_index()
    old_months = pd.read_csv(monthly_source)
    old_months = old_months[old_months.IDSOCKET.isin(SOCKETS)].set_index(["IDSOCKET", "mes"]).sort_index()
    assert observed_months.index.tolist() == old_months.index.tolist()
    np.testing.assert_array_equal(observed_months.registros, old_months.registros)
    monthly_errors = {}
    for c in ("D", "R"):
        original = old_months[f"kWh{c}_suma"].to_numpy()
        rebuilt = observed_months[f"energia_{c}_kwh"].to_numpy()
        monthly_errors[c] = float(np.max(np.abs(original - rebuilt)))
        np.testing.assert_allclose(original, rebuilt, rtol=1e-12, atol=1e-7)
    expanded = observed_months.reindex(pd.MultiIndex.from_product(
        [SOCKETS, [f"2024-{m:02d}" for m in range(1, 13)]], names=["IDSOCKET", "mes_local"]))
    expanded["estado"] = np.where(expanded.registros.notna(), "OBSERVADO", "SIN_REGISTRO_EN_EXTRACTO_REAL_DEFINITIVO")
    expanded["registros"] = expanded.registros.fillna(0).astype("int64")
    expanded = expanded.reset_index()
    coverage_path = CHECKS / "cobertura_mediciones_mensual.csv"
    expanded.to_csv(coverage_path, index=False)
    outputs.append(coverage_path)

    # Retiros de bloques completos, contrastados con auditoría independiente de código v4.
    previous_windows_path = ROOT / "SOCHER_2026_v4/eventos/resumen_ventanas_y_persistencia.csv"
    inputs.append(provenance(previous_windows_path))
    windows = pd.read_csv(previous_windows_path)
    window_checks = []
    for _, row in windows[windows.variable.eq("retiro_HT1_HT2_mw")].iterrows():
        w = wide[(wide.fecha_local >= row.desde_local_inclusivo) & (wide.fecha_local < row.hasta_local_exclusivo)]
        values = w.retiro_par_kwh / 250
        assert int(values.notna().sum()) == int(row.n)
        np.testing.assert_allclose(values.mean(), row.media_mw, rtol=1e-12, atol=1e-12)
        window_checks.append({"periodo": row.periodo, "n": len(values), "media_mw": float(values.mean()),
                              "diferencia_media_v4_mw": float(values.mean() - row.media_mw)})
    # Compara el canal primario de junio con la reextracción original v4 conservada.
    june_path = ROOT / "SOCHER_2026_v4/eventos/junio_definitivo_1_original.csv.gz"
    inputs.append(provenance(june_path))
    june = pd.read_csv(june_path, dtype=str, keep_default_na=False)
    june = june[june.IDSOCKET.isin(SOCKETS[:2])].set_index(key).sort_index()
    actual_june = d[d.mes_local.eq("2024-06") & d.incluido_suma_HT1_HT2].set_index(key).sort_index()
    assert actual_june.index.equals(june.index)
    assert (actual_june[june.columns] == june).all().all()
    sums_hourly = hourly.energia_HT1_HT2_kwh.sum()
    sums_source = d.loc[d.incluido_suma_HT1_HT2, "energia_D_kwh"].sum()
    np.testing.assert_allclose(sums_hourly, sums_source, rtol=1e-12, atol=1e-7)

    report = {
        "fecha_ejecucion": pd.Timestamp.now(tz="UTC").isoformat(),
        "script": provenance(Path(__file__).resolve()),
        "entorno": {"python": sys.version, "plataforma": platform.platform(), "pandas": pd.__version__,
                    "numpy": np.__version__, "pyarrow": pyarrow.__version__},
        "filas_15min": len(d), "filas_horarias_por_etiqueta": len(hourly),
        "medidores": d.groupby("medidor_id").size().to_dict(),
        "etiqueta_utc_desde": d.etiqueta_utc.min().isoformat(),
        "etiqueta_utc_hasta": d.etiqueta_utc.max().isoformat(),
        "dias_con_HT1_HT2": int(hourly.fecha_local.nunique()),
        "horas_con_HT1_HT2_cero_observado": int(hourly.energia_HT1_HT2_kwh.eq(0).sum()),
        "horas_incompletas_entre_observadas": int((~hourly.completo_por_etiquetas).sum()),
        "sin_registro_HT1_HT2_meses": ["2024-01", "2024-04"],
        "duplicados_medidor_utc": int(d.duplicated(["medidor_id", "etiqueta_utc"]).sum()),
        "offsets_locales_minutos": sorted(d.offset_local_minutos.unique().tolist()),
        "diferencias_etiquetas_America_Santiago": tz_mismatches,
        "minutos_intervalo_documentados": 15,
        "inicio_fin_fisico_intervalo_acreditado": False,
        "enlace_precio_realizado": False,
        "coincide_extracto_anual_con_12_extractos_mensuales": True,
        "junio_5760_filas_HT1_HT2_coinciden_reextraccion_v4": True,
        "max_diferencia_diaria_kwh_vs_v3": daily_errors,
        "max_diferencia_mensual_kwh_vs_v3": monthly_errors,
        "energia_HT1_HT2_kwh_observada": float(sums_source),
        "diferencia_energia_horaria_menos_15min_kwh": float(sums_hourly - sums_source),
        "ventanas_replicadas_vs_v4": window_checks,
        "limite_conciliacion": "Cotejos entre derivados del mismo original; no total externo ni nueva lectura de ZIP nacionales.",
        "no_incluidos": ["H1-H4 son tránsito", "HT3 no entra en carga agregada", "DATALUNA Norte 2020-22: unidad/signo pendientes"],
        "fuentes": inputs, "extractos_mensuales": source_rows,
        "salidas": [provenance(p) for p in outputs],
    }
    report_path = CHECKS / "verificacion_mediciones.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["filas_15min", "filas_horarias_por_etiqueta", "medidores",
        "dias_con_HT1_HT2", "horas_con_HT1_HT2_cero_observado", "horas_incompletas_entre_observadas",
        "inicio_fin_fisico_intervalo_acreditado", "enlace_precio_realizado"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
