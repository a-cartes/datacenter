"""Construye el panel base sin inferir tratamiento, UTC ni exposición desconocidos.

Entrada: extracción horaria auditada de la versión 6. No descarga ni modifica fuentes.
Ejecutar con .venv/bin/python desde la raíz del proyecto.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import pandas as pd
import numpy as np

B = Path(__file__).resolve().parents[1]
ROOT = B.parent
OUT = B / 'tablas'
CONTROL = B / 'controles'
SRC = ROOT / 'SOCHER_2026_v6_multicentros/precios/CEN_panel_barra_hora_identificado_hasta_20240714.parquet'
REFS = {
    'q110': ('QUILLOTA______110', 'BA01T0002SE032T0002'),
    'q220': ('QUILLOTA______220', 'BA02T0002SE032T0002'),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def uid(text):
    return hashlib.sha256(text.encode()).hexdigest()[:20]

def save(name, frame):
    frame.to_parquet(OUT / f'{name}.parquet', index=False, compression='zstd')
    frame.to_csv(OUT / f'{name}.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})

def main():
    OUT.mkdir(parents=True, exist_ok=True); CONTROL.mkdir(parents=True, exist_ok=True)
    p = pd.read_parquet(SRC)
    n = len(p)
    assert not p.duplicated(['barra_cmg', 'fecha', 'hora_etiqueta']).any()
    p['barra_id'] = p.clave_barra_historica.map(lambda s: 'B_' + uid(s))
    p['fecha'] = pd.to_datetime(p.fecha)
    p['hora_etiqueta'] = p.hora_etiqueta.astype('Int16')
    p['observacion_id'] = [f'{b}_{d:%Y%m%d}_{int(h):02}' for b,d,h in zip(p.barra_id,p.fecha,p.hora_etiqueta)]
    assert p.observacion_id.nunique() == n
    p['periodo_fuente_id'] = [f'{d:%Y-%m-%d}|{int(h):02}' for d,h in zip(p.fecha,p.hora_etiqueta)]
    p['t_dia'] = ((p.fecha - pd.Timestamp('1970-01-01')).dt.days).astype('Int32')
    p['mes_calendario'] = p.fecha.dt.to_period('M').astype(str)
    p['dia_semana'] = p.fecha.dt.dayofweek.astype('Int8')
    p['timestamp_utc_validado'] = pd.Series(pd.NaT, index=p.index, dtype='datetime64[ns, UTC]')
    p['estado_reloj'] = 'etiqueta_original_sin_equivalencia_UTC_certificada'
    p['homologacion_exacta'] = p.estado_identidad.eq('homologacion_mensual_exacta')
    p['tiene_marca_revision'] = p.marcas_fuente.ne('')
    p['precio_observado'] = p.precio_usd_mwh.notna()
    p['precio_revision_estricta'] = p.homologacion_exacta & ~p.tiene_marca_revision & p.precio_observado
    p['unidad_precio'] = 'USD/MWh'
    p['regimen_valorizacion'] = 'CMg_historico_libro_definitivo_anterior_20240715'

    # La fecha y hora son etiquetas de la misma publicación; no se interpretan como reloj UTC.
    keys = ['fecha', 'hora_etiqueta', 'regimen_valorizacion']
    for tag, (bar, code) in REFS.items():
        ref = p[p.barra_cmg.eq(bar) & p.nemotecnico.eq(code)]
        assert not ref.duplicated(keys).any()
        keep = keys + ['precio_usd_mwh', 'observacion_id', 'estado_identidad', 'marcas_fuente', 'precio_revision_estricta']
        ren = {c: f'{c}_{tag}' for c in keep if c not in keys}
        p = p.merge(ref[keep].rename(columns=ren), on=keys, how='left', validate='many_to_one')
        assert len(p) == n
        p[f'diferencial_{tag}_usd_mwh'] = p.precio_usd_mwh - p[f'precio_usd_mwh_{tag}']
        p[f'es_referencia_{tag}'] = p.barra_cmg.eq(bar) & p.nemotecnico.eq(code)
        p[f'par_precio_estricto_{tag}'] = (
            p.precio_revision_estricta & p[f'precio_revision_estricta_{tag}'].fillna(False)
            & p[f'precio_usd_mwh_{tag}'].notna() & ~p[f'es_referencia_{tag}'])

    # Ausencia de validación no significa nunca tratado ni no expuesto.
    for col in ['tratado_it', 'post_evento', 'control_validado']:
        p[col] = pd.Series(pd.NA, index=p.index, dtype='boolean')
    for col in ['cohorte_g_dia', 'tiempo_evento_dias', 'tiempo_evento_horas']:
        p[col] = pd.Series(pd.NA, index=p.index, dtype='Int32')
    for col in ['exposicion_red', 'carga_asignada_mw']:
        p[col] = pd.Series(pd.NA, index=p.index, dtype='Float64')
    p['evento_id_asignado'] = pd.Series(pd.NA, index=p.index, dtype='string')
    p['fecha_tratamiento_causal'] = pd.Series(pd.NaT, index=p.index, dtype='datetime64[ns]')
    p['estado_asignacion_causal'] = 'pendiente_evento_comparacion_y_exposicion'
    p['elegible_estimacion_causal'] = False
    p['estado_enlace_carga'] = 'pendiente_vigencia_suministro_y_conciliacion_reloj'
    p = p.sort_values(['barra_id', 'fecha', 'hora_etiqueta']).reset_index(drop=True)
    save('panel_barra_hora', p)

    # Dimensión: la identidad conserva etiqueta y código histórico; no presupone continuidad entre códigos.
    dims = []
    for bar, g in p.groupby('barra_id', sort=True):
        for col in ['barra_cmg', 'nemotecnico', 'clave_barra_historica']:
            assert g[col].nunique() == 1
        dims.append({
            'barra_id': bar, 'barra_cmg': g.barra_cmg.iloc[0], 'nemotecnico': g.nemotecnico.iloc[0],
            'clave_barra_historica': g.clave_barra_historica.iloc[0],
            'entidad_busqueda': g.entidad_busqueda.iloc[0],
            'nombres_homologacion': ' | '.join(sorted(g.barra_aux.unique())),
            'tensiones_kv_homologacion': ' | '.join(str(v) for v in sorted(g.tension_kv_homologacion.dropna().unique())),
            'fecha_min_observada': g.fecha.min(), 'fecha_max_observada': g.fecha.max(),
            'n_observaciones': len(g), 'n_meses_observados': g.mes_calendario.nunique(),
            'continuidad_otros_codigos_validada': False,
            'alcance_identidad': 'Clave histórica; no equivale a un centro ni a unidad física independiente.'
        })
    d = pd.DataFrame(dims); save('barras', d)
    obscols = ['periodo_fuente_id', 'fecha', 'hora_etiqueta', 't_dia', 'mes_calendario', 'dia_semana', 'estado_reloj', 'timestamp_utc_validado']
    cal = p[obscols].drop_duplicates().sort_values(['fecha', 'hora_etiqueta'])
    assert not cal.periodo_fuente_id.duplicated().any()
    save('periodos_fuente', cal)

    # Agregaciones descriptivas diarias de etiquetas, no una valoración física por MWh consumido.
    daily = p.groupby(['barra_id', 'fecha', 't_dia'], as_index=False).agg(
        precio_medio_usd_mwh=('precio_usd_mwh', 'mean'),
        n_etiquetas=('precio_usd_mwh', 'size'),
        diferencial_q110_usd_mwh=('diferencial_q110_usd_mwh', 'mean'),
        diferencial_q220_usd_mwh=('diferencial_q220_usd_mwh', 'mean'),
        n_pares_q110=('diferencial_q110_usd_mwh', 'count'),
        n_pares_q220=('diferencial_q220_usd_mwh', 'count'),
        n_pares_estrictos_q110=('par_precio_estricto_q110', 'sum'),
        n_pares_estrictos_q220=('par_precio_estricto_q220', 'sum'),
        n_filas_marcadas=('tiene_marca_revision', 'sum'),
        n_homologacion_exacta=('homologacion_exacta', 'sum'))
    expected = cal.groupby('fecha').size().rename('n_etiquetas_calendario_fuente').reset_index()
    daily = daily.merge(expected, on='fecha', validate='many_to_one')
    daily['cobertura_completa_segun_etiquetas_fuente'] = daily.n_etiquetas.eq(daily.n_etiquetas_calendario_fuente)
    for tag in REFS:
        # Media estricta solo si TODOS los pares esperados del día cumplen la regla.
        daily[f'diferencial_estricto_{tag}_usd_mwh'] = daily[f'diferencial_{tag}_usd_mwh'].where(
            daily[f'n_pares_estrictos_{tag}'].eq(daily.n_etiquetas_calendario_fuente))
    daily['regla_agregacion'] = 'media_simple_etiquetas_publicadas;sin_ponderar_consumo'
    daily['elegible_estimacion_causal'] = False
    save('panel_barra_dia', daily)

    # Calendario por mes de búsqueda. Un hueco significa ausencia en insumos integrados, no precio cero o inexistencia.
    cov = p.groupby(['barra_id', 'mes_calendario'], as_index=False).agg(
        n_precios=('precio_usd_mwh', 'size'), n_dias=('fecha', 'nunique'),
        n_homologacion_exacta=('homologacion_exacta', 'sum'), n_filas_marcadas=('tiene_marca_revision', 'sum'))
    grid = pd.MultiIndex.from_product([d.barra_id, pd.period_range('2024-01', '2024-12', freq='M').astype(str)], names=['barra_id', 'mes_calendario']).to_frame(index=False)
    coverage = grid.merge(cov, on=['barra_id', 'mes_calendario'], how='left', validate='one_to_one')
    for col in ['n_precios', 'n_dias', 'n_homologacion_exacta', 'n_filas_marcadas']:
        coverage[col] = coverage[col].fillna(0).astype('Int32')
    coverage['estado_cobertura'] = np.where(coverage.n_precios.gt(0), 'hay_registros', 'sin_registros_en_fuentes_integradas')
    coverage['no_infiere_existencia_del_nodo'] = True
    coverage = coverage.merge(d[['barra_id','barra_cmg','nemotecnico']], on='barra_id', validate='many_to_one')
    coverage.to_csv(OUT / 'cobertura_barra_mes.csv', index=False)

    report = {
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'fuente': str(SRC.relative_to(ROOT)), 'sha256_fuente': sha(SRC),
        'script': str(Path(__file__).relative_to(ROOT)), 'sha256_script': sha(Path(__file__)),
        'python': sys.version, 'pandas': pd.__version__,
        'filas_horarias': len(p), 'filas_diarias': len(daily), 'claves_barra_historicas': len(d),
        'periodos_fuente': len(cal), 'dias_observados': cal.fecha.nunique(),
        'cohortes_validadas': 0, 'filas_elegibles_causal': 0,
        'referencias': {t:{'barra_cmg':v[0], 'nemotecnico':v[1]} for t,v in REFS.items()},
        'n_pares_estrictos': {t:int(p[f'par_precio_estricto_{t}'].sum()) for t in REFS},
        'n_faltantes_referencia': {t:int(p[f'precio_usd_mwh_{t}'].isna().sum()) for t in REFS},
        'n_filas_marcadas': int(p.tiene_marca_revision.sum()),
        'limites': ['Los ceros de conteos son ausencia de registros integrados, no valores imputados de precios.',
                   'No se convierten etiquetas a UTC ni se enlazan a mediciones sin conciliación.',
                   'No se asignan tratamientos, cohortes ni exposición a partir de solicitudes o de nombres.'],
        'salidas': {str(f.relative_to(B)): sha(f) for stem in ['panel_barra_hora','panel_barra_dia','barras','periodos_fuente'] for f in [OUT/f'{stem}.parquet', OUT/f'{stem}.csv.gz']}
    }
    (CONTROL / 'construccion_panel_precios.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: report[k] for k in ['filas_horarias','filas_diarias','claves_barra_historicas','periodos_fuente','cohortes_validadas','n_pares_estrictos']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
