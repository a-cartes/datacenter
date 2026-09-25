"""Verificación cruzada y catálogo del dataset; no estima efectos."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import pandas as pd
import numpy as np

B = Path(__file__).resolve().parents[1]
ROOT = B.parent
T = B / 'tablas'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p = pd.read_parquet(T/'panel_barra_hora.parquet')
    old = pd.read_parquet(ROOT/'SOCHER_2026_v6_multicentros/precios/CEN_panel_barra_hora_identificado_hasta_20240714.parquet')
    old['fecha'] = pd.to_datetime(old.fecha)
    keys = ['barra_cmg','nemotecnico','fecha','hora_etiqueta']
    checked = old[keys+['precio_usd_mwh']].merge(p[keys+['precio_usd_mwh']], on=keys, validate='one_to_one', how='outer', indicator=True, suffixes=('_fuente','_panel'))
    assert len(checked) == len(old) == len(p) and checked._merge.eq('both').all()
    error_precio = float((checked.precio_usd_mwh_fuente-checked.precio_usd_mwh_panel).abs().max())
    assert error_precio == 0
    assert not p.observacion_id.duplicated().any()
    dif_errors = {}
    for tag,code in [('q110','BA01T0002SE032T0002'),('q220','BA02T0002SE032T0002')]:
        source_ref = old.loc[old.nemotecnico.eq(code)].set_index(['fecha','hora_etiqueta']).precio_usd_mwh
        mapped = [source_ref.loc[(d,int(h))] for d,h in zip(p.fecha,p.hora_etiqueta)]
        error = float(np.max(np.abs(p[f'diferencial_{tag}_usd_mwh'].to_numpy() - (p.precio_usd_mwh.to_numpy()-np.asarray(mapped)))))
        assert error < 1e-10
        dif_errors[tag] = error
        mask=p[f'par_precio_estricto_{tag}']
        assert p.loc[mask,'marcas_fuente'].eq('').all()
        assert p.loc[mask,'estado_identidad'].eq('homologacion_mensual_exacta').all()
        assert not p.loc[mask,f'es_referencia_{tag}'].any()
    for col in ['tratado_it','post_evento','control_validado','cohorte_g_dia','tiempo_evento_dias','tiempo_evento_horas','exposicion_red','carga_asignada_mw','evento_id_asignado','fecha_tratamiento_causal','timestamp_utc_validado']:
        assert p[col].isna().all(), col
    assert not p.elegible_estimacion_causal.any()
    b = pd.read_parquet(T/'barras.parquet')
    c = pd.read_parquet(T/'centros.parquet')
    e = pd.read_parquet(T/'eventos_documentados.parquet')
    r = pd.read_parquet(T/'relaciones_centros_barras.parquet')
    red = pd.read_parquet(T/'conexiones_red_documentadas.parquet')
    assert set(p.barra_id) == set(b.barra_id)
    assert set(e.centro_id).issubset(set(c.centro_id))
    assert set(r.centro_id).issubset(set(c.centro_id))
    assert not e.evento_id.duplicated().any()
    assert e.cohorte_g.isna().all() and e.fecha_tratamiento_causal.isna().all()
    assert not e.elegible_causal.any() and not red.utilizable_W_causal.any()
    assert red.peso_exposicion.isna().all()

    # Puente informativo entre relaciones documentales y precios, sin atribuir vigencia histórica.
    bridge = r.merge(b[['barra_id','barra_cmg','nemotecnico','n_observaciones','fecha_min_observada','fecha_max_observada']], on=['barra_cmg','nemotecnico'], how='left', validate='many_to_one')
    bridge['coincide_codigo_con_precios'] = bridge.barra_id.notna()
    bridge['habilita_asignacion_causal'] = False
    bridge.to_parquet(T/'relaciones_con_cobertura.parquet', index=False, compression='zstd')
    bridge.to_csv(T/'relaciones_con_cobertura.csv',index=False)
    assert len(bridge) == len(r)

    daily = pd.read_parquet(T/'panel_barra_dia.parquet')
    previous = pd.read_csv(ROOT/'SOCHER_2026_v4/resultados/panel_diferenciales_comparadores.csv')
    previous = previous[previous.comparador.eq('QUILLOTA______110')].copy()
    previous['fecha'] = pd.to_datetime(previous.fecha)
    bid = b.loc[b.barra_cmg.eq('CANTERAS______110') & b.nemotecnico.eq('BA01T0487SE001T0487'),'barra_id'].item()
    matched = daily[daily.barra_id.eq(bid)].merge(previous[['fecha','spread_usd_mwh']], on='fecha',validate='one_to_one')
    assert len(matched) > 0
    err_daily = float((matched.diferencial_q110_usd_mwh-matched.spread_usd_mwh).abs().max())
    assert err_daily < 1e-9
    for tag in ['q110','q220']:
        m = daily[f'n_pares_estrictos_{tag}'].eq(daily.n_etiquetas_calendario_fuente)
        assert daily.loc[~m,f'diferencial_estricto_{tag}_usd_mwh'].isna().all()
        assert daily.loc[m,f'diferencial_estricto_{tag}_usd_mwh'].equals(daily.loc[m,f'diferencial_{tag}_usd_mwh'])
    load = pd.read_parquet(T/'carga_medidor_15min.parquet')
    hourly = pd.read_parquet(T/'carga_campus_hora.parquet')
    assert set(load.centro_id).issubset(set(c.centro_id))
    assert set(hourly.centro_id).issubset(set(c.centro_id))
    assert not hourly.enlace_precio_habilitado.any() and not hourly.HT3_incluido.any()
    assert not load.enlace_precio_habilitado.any()
    assert not load.duplicated(['medidor_id','etiqueta_utc']).any()
    assert not hourly.duplicated(['punto_medida_id','hora_utc_etiqueta']).any()
    assert hourly.n_intervalos_validos.eq(4).all()
    energy=load[load.incluido_suma_HT1_HT2].retiro_validado_kwh.sum()
    err_energy=float(abs(energy-hourly.energia_HT1_HT2_kwh.sum()))
    assert err_energy<1e-7

    # Exportación tabular leíble: no altera nulos de tratamiento ni crea registros.
    csv = pd.read_csv(T/'panel_barra_hora.csv.gz',dtype={'observacion_id':str},low_memory=False)
    assert len(csv)==len(p) and csv.observacion_id.equals(p.observacion_id.astype(str))
    assert csv.cohorte_g_dia.isna().all() and csv.tratado_it.isna().all()
    err_csv=float(np.max(np.abs(csv.precio_usd_mwh-p.precio_usd_mwh)))
    assert err_csv<1e-10

    catalogue=[];schema=[]
    for file in sorted(T.glob('*.parquet')):
        frame=pd.read_parquet(file)
        catalogue.append({'tabla':file.stem,'filas':len(frame),'columnas':len(frame.columns),'archivo':str(file.relative_to(B)),'sha256':sha(file)})
        for col in frame:
            schema.append({'tabla':file.stem,'variable':col,'tipo_parquet_leido':str(frame[col].dtype),'n_nulos':int(frame[col].isna().sum()),'n_observados':int(frame[col].notna().sum())})
    pd.DataFrame(catalogue).to_csv(B/'documentacion/catalogo_tablas.csv',index=False)
    pd.DataFrame(schema).to_csv(B/'documentacion/esquema_y_faltantes.csv',index=False)
    report={
        'fecha_utc':datetime.now(timezone.utc).isoformat(),
        'filas_horarias':len(p),'filas_diarias':len(daily),'claves_barra_historicas':len(b),
        'candidatos':len(c),'hitos_documentados':len(e),'relaciones_documentales':len(r),
        'conexiones_red_documentadas':len(red),'filas_medidor_15min':len(load),'horas_carga_HT1_HT2':len(hourly),
        'relaciones_con_codigo_de_precio':int(bridge.coincide_codigo_con_precios.sum()),
        'error_precio_vs_v6':error_precio,'errores_diferencial_vs_fuente':dif_errors,
        'dias_Canteras_Quillota_comparados_v4':len(matched),'error_diario_vs_v4':err_daily,
        'error_energia_total_kwh':err_energy,'error_precio_csv_parquet':err_csv,
        'llaves_foraneas_verificadas':True,'tratamiento_desconocido_conservado_nulo':True,
        'filas_elegibles_estimacion_causal':0,
        'estado':'BASE_OBSERVADA_INTEGRADA_ASIGNACION_CAUSAL_PENDIENTE',
        'tablas':catalogue,'script_sha256':sha(Path(__file__))}
    (B/'controles/verificacion_integral.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='tablas'},ensure_ascii=False))

if __name__=='__main__':main()
