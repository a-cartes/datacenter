"""Auditoría de insumos locales. Solo escribe una ejecución nueva dentro de esta etapa."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parent

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(2**20), b''):
            h.update(part)
    return h.hexdigest()

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--proyecto', type=Path, required=True)
    ap.add_argument('--ejecucion', default='20261011_inventario')
    args = ap.parse_args()
    project = args.proyecto.resolve()
    out = STAGE/'resultados'/args.ejecucion
    if out.parent.resolve() != (STAGE/'resultados').resolve() or out.exists():
        raise SystemExit('Use un nombre de ejecución nuevo, sin subdirectorios.')
    audit = project/'Panel_datos/codex_panel_nacional/auditoria_demanda'
    pilot = project/'Panel_datos/codex_panel_nacional/piloto_panamericana'
    national = project/'Panel_datos/codex_panel_nacional'
    replica = project/'Replica_RM_desde_cero'
    et7 = REPO/'SOCHER_2026_v8_panel_causal/investigacion_e53_20260927/mediciones'
    sources = set()
    for folder in [audit, pilot, project/'Panel_datos/registro_dc', project/'Panel_datos/topologia',
                   national/'metadata', replica/'resultados/cierre_socher_20261009',
                   replica/'prospectiva_2030/extraidos/demanda_digital', et7]:
        for p in folder.iterdir():
            if p.is_file() and p.suffix in ['.csv','.json','.md','.txt','.py']:
                sources.add(p)
    for p in [national/'PLAN.md', national/'BITACORA_CODEX.md',
              national/'data/withdrawals/cliente_hora.parquet',
              pilot/'data/canales_hora.csv.gz', audit/'data/vinculos_campus.csv.gz',
              audit/'data/vinculos_historicos_puntos.csv.gz',
              audit/'data/medidas_fisicas_tres_meses.csv.gz',
              project/'Panel_datos/retiros_chacabuco/mensual_por_punto.csv',
              project/'Panel_datos/sip_api/fechado/serie_mensual.csv',
              replica/'datos/instalaciones/instalaciones.csv',
              replica/'datos/instalaciones/hitos.csv',
              replica/'datos/instalaciones/fuentes_instalaciones.csv',
              replica/'datos/panel/barra_anio.parquet', replica/'datos/panel/barra_mes.parquet',
              replica/'prospectiva_2030/extraidos/infotecnica/fichas_largas_secciones-tramos.parquet',
              replica/'prospectiva_2030/extraidos/infotecnica/fichas_largas_transformadores-2d.parquet',
              et7/'et7_15min.csv.gz',
              REPO/'SOCHER_2026_RM/evidencia/tabla_1.csv',
              REPO/'SOCHER_2026_RM/procedencia/manifest.json']:
        sources.add(p)
    missing = [str(p) for p in sources if not p.is_file()]
    if missing:
        raise SystemExit('Faltan insumos locales: '+str(missing))
    def ref(p):
        return ('repositorio:'+str(p.relative_to(REPO))) if p.is_relative_to(REPO) else ('proyecto:'+str(p.relative_to(project)))
    sources = sorted(sources, key=ref)
    before = [{'referencia':ref(p), 'bytes':p.stat().st_size, 'sha256':sha(p)} for p in sources]
    out.mkdir(parents=True)
    pd.DataFrame(before).to_csv(out/'insumos_estado_inicial.csv',index=False)
    baseline = {'fecha_local':datetime.now(ZoneInfo('America/Santiago')).isoformat(),
        'rama_nueva':git(REPO,'branch','--show-current'), 'commit_repositorio':git(REPO,'rev-parse','HEAD'),
        'version_preservada':'v0.3.0', 'commit_version_preservada':git(REPO,'rev-parse','v0.3.0^{}'),
        'commit_proyecto_local':git(project,'rev-parse','HEAD'),
        'estado_proyecto_previo':git(project,'status','--short'),
        'cifras_anteriores':pd.read_csv(REPO/'SOCHER_2026_RM/evidencia/tabla_1.csv').to_dict('records'),
        'alcance_hashes':'SHA256 recalculado para los insumos enumerados; hashes de originales masivos heredados, con existencia y tamaño comprobados de nuevo.',
        'archivos_insumo':len(before), 'bytes_insumos':sum(x['bytes'] for x in before)}
    (out/'estado_inicial.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2,default=str))
    (out/'arbol_git_anterior.txt').write_text(git(REPO,'ls-tree','-r','v0.3.0'))

    # Auditoría de existencia: no vuelve a leer 26 GB ni presenta hashes heredados como nuevos.
    originals = pd.read_csv(audit/'inventario_archivos.csv')
    originals['existe_actualmente'] = originals.archivo.map(lambda s:Path(s).is_file())
    originals['bytes_actuales'] = originals.archivo.map(lambda s:Path(s).stat().st_size if Path(s).is_file() else None)
    originals['tamano_coincide'] = originals.bytes_actuales == originals.bytes
    originals['hash_recalculado_en_esta_etapa'] = False
    originals.drop(columns=['archivo']).to_csv(out/'originales_disponibilidad.csv',index=False)
    originals.groupby('familia',dropna=False).agg(archivos=('source_id','size'),bytes=('bytes','sum'),
        disponibles=('existe_actualmente','sum'),tamano_coincidente=('tamano_coincide','sum'),
        desde=('mes_ruta','min'),hasta=('mes_ruta','max')).reset_index().to_csv(out/'familias_originales.csv',index=False)

    # Retiros: conservar ambigüedades y muestras; nunca extrapolar a total mensual.
    x = pd.read_parquet(national/'data/withdrawals/cliente_hora.parquet')
    x['valida'] = ~x.clave_ambigua & x.retiro_mwh.notna()
    daily = x.groupby(['empresa','barra','fecha'],dropna=False).agg(
        filas=('retiro_mwh','size'),horas_unicas=('hora0','nunique'),validas=('valida','sum'),
        ambiguas=('clave_ambigua','sum'),energia_observada_mwh=('retiro_mwh',lambda s:s.sum(min_count=1))).reset_index()
    daily['dia_24h_muestral'] = daily.filas.eq(24)&daily.horas_unicas.eq(24)&daily.validas.eq(24)
    daily['energia_dia_muestral_mwh'] = daily.energia_observada_mwh.where(daily.dia_24h_muestral)
    daily['nota'] = '24 etiquetas válidas no certifican huso SIP ni día físico de cambio horario; no sumar puntos solapados'
    daily.to_csv(out/'retiros_dias_revisados.csv',index=False)
    coverage = daily.groupby(['empresa','barra']).agg(desde=('fecha','min'),hasta=('fecha','max'),
        dias_muestreados=('fecha','nunique'),dias_24h_validas=('dia_24h_muestral','sum'),
        horas_validas=('validas','sum'),horas_ambiguas=('ambiguas','sum')).reset_index()
    coverage['atribucion'] = 'clasificación comercial heredada; campus y vigencia por conciliar'
    coverage.to_csv(out/'cobertura_retiros_cliente.csv',index=False)
    assert len(x)==27425 and not x.duplicated(['empresa','barra','fecha','hora0']).any()

    historical = pd.read_csv(project/'Panel_datos/retiros_chacabuco/mensual_por_punto.csv')
    historical.groupby(['punto','subestacion']).agg(desde=('mes','min'),hasta=('mes','max'),
        meses=('mes','nunique'),horas_canal_D=('horas','sum')).reset_index().to_csv(out/'cobertura_canales_historicos.csv',index=False)
    physical = pd.read_csv(audit/'medidas_fisicas_resumen.csv')
    physical[['punto','canal','rotulo','mes','medidor']].to_csv(out/'sentido_canales_auditados.csv',index=False)

    # Recalcular la señal del piloto usando la frontera heredada completa; no estimar precios.
    h = pd.read_csv(pilot/'data/canales_hora.csv.gz')
    chosen = [f'PNMRCANA_012_CT{i}_CHL' for i in range(1,5)]
    h=h[h.IDSOCKET.isin(chosen)].copy()
    if h.duplicated(['IDSOCKET','hora']).any(): raise AssertionError('Clave horaria repetida')
    valid=h.cuartos.eq(4)&h.D_n.eq(4)&h.R_n.eq(4)
    if not valid.all():raise AssertionError('Frontera piloto incompleta')
    assert ((h.D-h.R)/1000-h.MW_neto).abs().max()<1e-9
    hours=h.pivot(index='hora',columns='IDSOCKET',values='MW_neto')
    total=hours.sum(axis=1,min_count=4)
    assert len(total)==4392 and total.notna().all()
    dates=pd.to_datetime(total.index)
    pre=total[(dates>='2023-10-01')&(dates<'2023-12-01')].mean()
    post=total[(dates>='2024-02-01')&(dates<'2024-04-01')].mean()
    pilot_check={'horas_completas':len(total),'canales':chosen,'pre_MW':pre,'post_MW':post,
        'diferencia_MW':post-pre,'diferencia_pct':100*(post/pre-1),
        'alcance':'señal descriptiva de suministro seleccionado, no consumo exclusivo de ODATA ni efecto causal'}
    (out/'comprobacion_panamericana.json').write_text(json.dumps(pilot_check,ensure_ascii=False,indent=2))
    total.rename('MW_neto_frontera_provisional').to_csv(out/'panamericana_hora_frontera_provisional.csv')

    # Medición disponible a nivel de operador: asociación por nombre solo como pista.
    facilities=pd.read_csv(replica/'datos/instalaciones/instalaciones.csv')
    def family(row):
        text=' '.join(str(row.get(c,'')) for c in ['nombre','operador_actual','operadores_previos','alias']).lower()
        for tokens,label in [(['google','dataluna'],'Google/Dataluna'),(['edgeconnex'],'EdgeConneX'),
                (['odata'],'ODATA'),(['ascenty'],'Ascenty'),(['sonda'],'Sonda'),(['cirion','lumen','centurylink'],'Cirion'),
                (['scala'],'Scala'),(['amazon','aws'],'Amazon'),(['microsoft'],'Microsoft')]:
            if any(t in text for t in tokens):return label
        return 'Sin enlace en el panel SIP auditado'
    facilities['familia_busqueda']=facilities.apply(family,axis=1)
    def candidate(label):
        lookup={'Google/Dataluna':['google','dataluna'],'ODATA':['odata'],'Cirion':['cirion','lumen','centurylink']}
        terms=lookup.get(label,[label.lower()])
        return coverage[coverage.empresa.str.lower().map(lambda s:any(t in s for t in terms))]
    facilities['puntos_candidatos_operador']=facilities.familia_busqueda.map(lambda f:'; '.join(sorted(candidate(f).barra.unique())))
    facilities['estado_asignacion']='Pista por operador; NO asigna consumo del operador a este sitio o etapa'
    facilities['paso_siguiente']='Acreditar cliente, campus, punto, sentido y vigencia histórica; excluir proyectos futuros de carga observada'
    facilities[['id','campus','nombre','operador_actual','comuna','estado_2025','familia_busqueda',
        'puntos_candidatos_operador','estado_asignacion','paso_siguiente']].to_csv(out/'revision_63_registros.csv',index=False)

    # Características disponibles para construir zonas: no son una red histórica validada.
    edges=pd.read_csv(project/'Panel_datos/topologia/aristas.csv')
    trafos=pd.read_csv(project/'Panel_datos/topologia/fichas_transformadores.csv')
    technical={}
    for name in ['secciones-tramos','transformadores-2d']:
        t=pd.read_parquet(replica/f'prospectiva_2030/extraidos/infotecnica/fichas_largas_{name}.parquet')
        concepts=t[t.concepto.str.contains('resisten|reactan|corriente|capacidad|potencia|térmic',case=False,na=False)]
        concepts.groupby(['concepto','unidad','estado_certificacion'],dropna=False).agg(
            registros=('id','size'),con_valor_numerico=('valor_numerico','count')).reset_index().to_csv(out/f'parametros_{name}.csv',index=False)
        technical[name]={'registros':len(t),'elementos':t.id.nunique(),'conceptos':t.concepto.nunique()}
    # Precios ya disponibles: ambas series se mantienen separadas por procedencia.
    price_files=sorted((national/'data/hourly').glob('*.parquet'))
    summary={'fecha_corte':'2026-10-11','originales':len(originals),'GB_decimales':float(originals.bytes.sum()/1e9),
        'originales_existentes':int(originals.existe_actualmente.sum()),
        'originales_tamano_coincidente':int(originals.tamano_coincide.sum()),
        'retiros_filas':len(x),'retiros_empresas':sorted(x.empresa.unique()),'retiros_pares_empresa_barra':len(coverage),
        'retiros_dias_distintos':x.fecha.nunique(),'retiros_horas_validas':int(x.valida.sum()),
        'retiros_horas_ambiguas':int(x.clave_ambigua.sum()),
        'historia_canales_puntos':historical.punto.nunique(),'historia_canales_desde':historical.mes.min(),
        'historia_canales_hasta':historical.mes.max(),'historia_meses':historical.mes.nunique(),
        'precios_archivos_horarios':len(price_files),'topologia_aristas':len(edges),'topologia_transformadores':len(trafos),
        'parametros_tecnicos':technical,'instalaciones_registros':len(facilities),'panamericana':pilot_check}
    (out/'resumen_auditoria.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=int))
    after=[{'referencia':ref(p),'sin_cambios':sha(p)==item['sha256']} for p,item in zip(sources,before)]
    assert all(item['sin_cambios'] for item in after)
    pd.DataFrame(after).to_csv(out/'verificacion_insumos_final.csv',index=False)
    (out/'verificacion.json').write_text(json.dumps({'estado':'OK','insumos_preservados':len(after),
        'originales_masivos':'existencia y tamaño; SHA256 heredados no recalculados',
        'estimaciones_nuevas_de_precios':False,'descargas_nuevas':False,'cambios_en_bases':0},ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2,default=int))

if __name__=='__main__':
    main()
