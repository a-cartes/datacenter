"""Extrae ET7 literalmente de ZIP definitivos locales auditados; no mide Ascenty.

No descarga fuentes, modifica v7, imputa ausencia, atribuye consumo ni une precios.
Usa hashes originales conservados en v7, coteja tamaño y recorrido CSV; no repite
la auditoría íntegra de adquisición. Los hashes nuevos corresponden a extractos.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, csv, gzip, hashlib, json, zipfile, os, tempfile
import pandas as pd
import openpyxl

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[2]
V7 = ROOT / 'SOCHER_2026_v7_2020_2026/mediciones'
SOCKET = 'CHCABUCO_023_ET7_CHL'
RAW = ['ID_SOC','IDSOCKET','SUBESTACION','TENSION','YEARX','MONX','DAYX','HOURX',
       'DATETIME','UTCDATETIME','kWhD','kWhR','FLUJO','ULTIMA_LECTURA']

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()

def catalog():
    p=ROOT/'SOCHER_2026_v3/mapeo/CEN_SOCKET_HABILITADO_20260925.xlsx'
    w=openpyxl.load_workbook(p,read_only=True,data_only=True)
    s=w.worksheets[0]; rows=list(s.values); cols=list(rows[0]); matches=[]
    for n,row in enumerate(rows[1:],2):
        r=dict(zip(cols,row))
        if str(r.get('Subestación','')).upper()=='CHACABUCO' or any('ASCENT' in str(v).upper() for v in row):
            matches.append({'fila_excel':n,'hoja':s.title,**r})
    pd.DataFrame(matches).to_csv(OUT/'catalogo_chacabuco.csv',index=False)
    meta={'archivo':str(p.relative_to(ROOT)),'sha256':sha(p),'filas_catalogo':len(rows)-1,
          'filas_chacabuco_o_ascenty':len(matches),'coincidencias_ascenty':sum(any('ASCENT' in str(v).upper() for v in r) for r in rows[1:]),
          'coincidencias_e53_chacabuco':sum(r['Paño']=='E53' for r in matches),
          'vigencia_historica_certificada':False,'fecha_nombre_hoja':s.title}
    (OUT/'control_catalogo.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))

def extract(meta_path):
    prior=json.loads(meta_path.read_text()); year,month=prior['anio'],prior['mes']
    source=ROOT/prior['archivo_original']
    assert source.stat().st_size==prior['bytes_original']
    target=OUT/'extractos'/f'et7_{year}_{month:02d}.csv.gz'
    mp=target.with_name(target.name.replace('.csv.gz','_manifest.json'))
    if target.exists() and mp.exists():
        m=json.loads(mp.read_text())
        if m['sha256_extracto']==sha(target): return m
    count=0; lines=1; consumed=0; seen={}
    with gzip.open(target,'wt',encoding='utf-8',newline='') as o:
        writer=csv.writer(o); writer.writerow(['archivo_original','miembro_zip','fila_csv_original']+RAW)
        with zipfile.ZipFile(source) as z:
            members=[m for m in z.infolist() if m.filename.lower().endswith('.csv')]
            assert len(members)==1
            member=members[0]
            with z.open(member) as f:
                hb=f.readline(); consumed+=len(hb)
                header=next(csv.reader([hb.decode('utf-8-sig').strip()],delimiter=';'))
                index=header.index('IDSOCKET'); tail=b''
                while True:
                    block=f.read(8*1024*1024)
                    if not block: break
                    consumed+=len(block); block=tail+block
                    stop=block.rfind(b'\n')
                    if stop<0: tail=block; continue
                    complete,tail=block[:stop],block[stop+1:]
                    if b'CHCABUCO' in complete or b'ASCENT' in complete.upper():
                        for position,line in enumerate(complete.split(b'\n'),1):
                            if b'CHCABUCO' not in line and b'ASCENT' not in line.upper(): continue
                            row=next(csv.reader([line.decode('utf-8-sig').rstrip('\r')],delimiter=';'))
                            assert len(row)==len(header)
                            seen[row[index]]=seen.get(row[index],0)+1
                            if row[index]!=SOCKET: continue
                            record=dict(zip(header,row))
                            writer.writerow([prior['archivo_original'],member.filename,lines+position]+[record.get(c,'') for c in RAW]); count+=1
                    lines+=complete.count(b'\n')+1
                if tail.strip():
                    lines+=1; row=next(csv.reader([tail.decode('utf-8-sig').rstrip('\r')],delimiter=';'))
                    if 'CHCABUCO' in row[index] or 'ASCENT' in row[index].upper(): seen[row[index]]=seen.get(row[index],0)+1
                    if row[index]==SOCKET:
                        record=dict(zip(header,row));writer.writerow([prior['archivo_original'],member.filename,lines]+[record.get(c,'') for c in RAW]);count+=1
            assert consumed==member.file_size==prior['bytes_csv_original']
            assert lines==prior['lineas_csv_con_cabecera']
    m={'anio':year,'mes':month,'archivo_original':prior['archivo_original'],'bytes_original':prior['bytes_original'],
       'sha256_original_auditoria_v7':prior['sha256_original'],'manifiesto_original_v7':str(meta_path.relative_to(ROOT)),
       'sha256_original_recalculado':False,'bytes_csv_leidos':consumed,'lineas_csv_con_cabecera':lines,
       'miembro_zip':member.filename,'csv_crc_zip_validado_al_leer':True,'extracto':str(target.relative_to(OUT)),
       'sha256_extracto':sha(target),'filas_et7':count,'sockets_chacabuco_o_ascenty_observados':seen}
    mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)); print(f'{year}-{month:02d}: ET7 {count}',flush=True)
    return m

def consolidate(manifests):
    parts=[]
    socket_rows=[]
    for m in manifests:
        p=OUT/m['extracto']; assert sha(p)==m['sha256_extracto']
        d=pd.read_csv(p,dtype=str,keep_default_na=False)
        d['sha256_original_auditoria_v7']=m['sha256_original_auditoria_v7']
        d['archivo_extracto']=m['extracto'];d['mes_archivo']=f"{m['anio']}-{m['mes']:02d}"
        parts.append(d)
        socket_rows.extend({'mes_archivo':f"{m['anio']}-{m['mes']:02d}",'socket':s,'registros':n} for s,n in m['sockets_chacabuco_o_ascenty_observados'].items())
    pd.DataFrame(socket_rows).to_csv(OUT/'sockets_chacabuco_observados_por_mes.csv',index=False)
    d=pd.concat(parts,ignore_index=True)
    d['etiqueta_utc']=pd.to_datetime(d.UTCDATETIME,utc=True)
    local=pd.to_datetime(d.DATETIME);d['fecha_etiqueta_local']=local.dt.strftime('%Y-%m-%d')
    assert not d.duplicated(['IDSOCKET','etiqueta_utc']).any()
    assert local.dt.strftime('%Y-%m').eq(d.mes_archivo).all()
    d['offset_local_min']=((local-d.etiqueta_utc.dt.tz_localize(None)).dt.total_seconds()/60).astype(int)
    d['america_santiago_coincide']=local.eq(d.etiqueta_utc.dt.tz_convert('America/Santiago').dt.tz_localize(None))
    for c in ('D','R'):
        d[f'energia_{c}_kwh']=pd.to_numeric(d[f'kWh{c}'].str.replace(',','.',regex=False),errors='raise')
        d[f'potencia_media_{c}_mw']=d[f'energia_{c}_kwh']/250
    d['duracion_intervalo_minutos']=15;d['inicio_fin_fisico_acreditado']=False
    d['representa_demanda_ascenty']=False;d['enlace_precio_habilitado']=False
    d=d.sort_values('etiqueta_utc');d.to_csv(OUT/'et7_15min.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    group=d.groupby('mes_archivo').agg(registros=('IDSOCKET','size'),desde=('DATETIME','min'),hasta=('DATETIME','max'),
        energia_D_kwh=('energia_D_kwh','sum'),energia_R_kwh=('energia_R_kwh','sum'),
        media_D_mw=('potencia_media_D_mw','mean'),media_R_mw=('potencia_media_R_mw','mean'),
        max_D_mw=('potencia_media_D_mw','max'),max_R_mw=('potencia_media_R_mw','max'),
        negativos_D=('energia_D_kwh',lambda s:int(s.lt(0).sum())),negativos_R=('energia_R_kwh',lambda s:int(s.lt(0).sum())))
    months=[f"{m['anio']}-{m['mes']:02d}" for m in manifests];group=group.reindex(months)
    group['registros']=group.registros.fillna(0).astype(int)
    group['intervalos_civiles_esperados']=[len(pd.date_range(pd.Timestamp(s).tz_localize('America/Santiago'),(pd.Timestamp(s)+pd.offsets.MonthBegin()).tz_localize('America/Santiago'),freq='15min',inclusive='left')) for s in group.index]
    group['cobertura']=group.registros/group.intervalos_civiles_esperados
    group['estado_presencia']=group.registros.map(lambda n:'OBSERVADO' if n else 'AUSENTE_EN_ARCHIVO_EXAMINADO_NO_CERO')
    group.to_csv(OUT/'et7_cobertura_mensual.csv')
    day=d.groupby('fecha_etiqueta_local').agg(registros=('IDSOCKET','size'),energia_D_kwh=('energia_D_kwh','sum'),energia_R_kwh=('energia_R_kwh','sum'),media_D_mw=('potencia_media_D_mw','mean'),media_R_mw=('potencia_media_R_mw','mean'))
    day.to_csv(OUT/'et7_descriptivo_diario.csv')
    expected=pd.Series(pd.date_range('2024-01-01','2026-09-01',tz='America/Santiago',freq='15min',inclusive='left')).dt.strftime('%Y-%m-%d').value_counts().sort_index()
    daily_support=day.reindex(expected.index)
    daily_support['registros']=daily_support.registros.fillna(0).astype(int)
    daily_support['intervalos_civiles_esperados']=expected
    daily_support['dia_completo']=daily_support.registros.eq(expected)
    daily_support['ausente']=daily_support.registros.eq(0)
    daily_support.index.name='fecha_etiqueta_local'
    daily_support.to_csv(OUT/'et7_cobertura_diaria.csv')
    assert abs(day.energia_D_kwh.sum()-d.energia_D_kwh.sum())<0.0001
    assert abs(group.energia_D_kwh.sum()-d.energia_D_kwh.sum())<0.0001
    g=pd.Timestamp('2025-05-06')
    windows=[('exploratorio_30_fechas_pre','2025-04-05','2025-05-04','exploratorio_posterior_a_inspeccion'),('exploratorio_30_fechas_post','2025-05-06','2025-06-04','exploratorio_posterior_a_inspeccion'),('dia_energizacion','2025-05-05','2025-05-05','contexto_no_estimacion'),
             ('protocolo_pre_m112_m8',(g-pd.Timedelta(days=112)).strftime('%Y-%m-%d'),(g-pd.Timedelta(days=8)).strftime('%Y-%m-%d'),'ventana_protocolo'),
             ('protocolo_excluida_m7_m1',(g-pd.Timedelta(days=7)).strftime('%Y-%m-%d'),(g-pd.Timedelta(days=1)).strftime('%Y-%m-%d'),'excluida_de_comparacion'),
             ('protocolo_post_0_89',g.strftime('%Y-%m-%d'),(g+pd.Timedelta(days=89)).strftime('%Y-%m-%d'),'ventana_protocolo'),
             ('protocolo_post_0_27',g.strftime('%Y-%m-%d'),(g+pd.Timedelta(days=27)).strftime('%Y-%m-%d'),'subventana_28_dias')]
    rows=[]
    for name,start,end,kind in windows:
        q=d[d.fecha_etiqueta_local.between(start,end)]
        ds=daily_support.loc[start:end]
        rows.append({'ventana':name,'tipo':kind,'desde_local':start,'hasta_local':end,'registros':len(q),'intervalos_esperados':int(ds.intervalos_civiles_esperados.sum()),'dias_esperados':len(ds),'dias_observados':q.fecha_etiqueta_local.nunique(),'dias_completos':int(ds.dia_completo.sum()),'dias_ausentes':int(ds.ausente.sum()),'media_D_mw':q.potencia_media_D_mw.mean(),'media_R_mw':q.potencia_media_R_mw.mean(),'energia_D_kwh':q.energia_D_kwh.sum(min_count=1),'energia_R_kwh':q.energia_R_kwh.sum(min_count=1),'efecto_causal':False})
    pd.DataFrame(rows).to_csv(OUT/'et7_ventanas_descriptivas.csv',index=False)
    os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'socher_et7_matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    q=day.copy();q.index=pd.to_datetime(q.index)
    q=q.reindex(pd.date_range(q.index.min(),q.index.max(),freq='D'))
    fig,ax=plt.subplots(figsize=(10,4.8))
    ax.plot(q.index,q.media_D_mw,color='#20566c',lw=1.0)
    ax.axvline(pd.Timestamp('2025-05-05'),color='#aa6130',lw=1.5,ls='--',label='Energización E53: 5 mayo 2025')
    ax.set(title='Canal D de ET7 de Chacabuco: promedio por fecha de etiqueta',ylabel='MW medios del canal D',xlabel='Fecha de etiqueta local')
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2)
    ax.legend(frameon=False,loc='lower left')
    fig.text(.09,.015,'ET7 es un punto de medida compartido; no representa demanda Ascenty. Marzo de 2025 está ausente.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(OUT/'et7_diario.png',dpi=180);fig.savefig(OUT/'et7_diario.svg');plt.close(fig)
    descriptions={
      'archivo_original':'Ruta del ZIP definitivo local que contenía la fila.',
      'miembro_zip':'CSV dentro del ZIP original.',
      'fila_csv_original':'Número de fila original contando la cabecera como fila 1.',
      'sha256_original_auditoria_v7':'Hash del ZIP conservado en auditoría v7; no recalculado en esta extracción.',
      'archivo_extracto':'Extracto mensual relativo a esta carpeta.',
      'mes_archivo':'Año y mes del archivo; coincide con DATETIME.',
      'etiqueta_utc':'Parseo de UTCDATETIME explícito del publicador, sin inferir UTC de DATETIME.',
      'fecha_etiqueta_local':'Fecha de DATETIME; no certifica fecha física de integración.',
      'offset_local_min':'DATETIME menos UTCDATETIME en minutos.',
      'america_santiago_coincide':'Concordancia empírica entre etiquetas y zona America/Santiago.',
      'energia_D_kwh':'kWhD convertido a numérico conservando significado de canal D.',
      'energia_R_kwh':'kWhR convertido a numérico conservando significado de canal R.',
      'potencia_media_D_mw':'energia_D_kwh / 250 para intervalos de 15 minutos.',
      'potencia_media_R_mw':'energia_R_kwh / 250 para intervalos de 15 minutos.',
      'duracion_intervalo_minutos':'15 según formato publicado.',
      'inicio_fin_fisico_acreditado':'False: no acreditada convención inicio/fin de etiqueta CSV.',
      'representa_demanda_ascenty':'False: no es medición dedicada acreditada del cliente.',
      'enlace_precio_habilitado':'False: no se une el reloj de medidas a precios.'}
    pd.DataFrame([{'variable':c,'descripcion':descriptions.get(c,'Campo literal del CSV original; no se modifica.'),'origen':'literal' if c in RAW else 'procedencia_o_derivada'} for c in d.columns]).to_csv(OUT/'diccionario_et7.csv',index=False)
    audit={'filas':len(d),'desde':d.DATETIME.min(),'hasta':d.DATETIME.max(),'duplicados_socket_utc':int(d.duplicated(['IDSOCKET','etiqueta_utc']).sum()),'reloj_civil_discrepancias':int((~d.america_santiago_coincide).sum()),'offsets_observados':sorted(d.offset_local_min.unique().tolist()),'meses_examinados':len(manifests),'descargas':0,'representa_demanda_ascenty':False,'tratamiento_habilitado':False,'precio_unido':False,'hash_tabla_15min':sha(OUT/'et7_15min.csv.gz')}
    (OUT/'verificacion_et7.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)); print(json.dumps(audit,ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solo-consolidar',action='store_true',help='Reconstruye tablas y figura desde extractos locales, sin requerir los ZIP nacionales.')
    parser.add_argument('--datos-raiz',type=Path,help='Raíz externa con v3 y v7/originales, cuando se ejecuta desde la copia de repositorio.')
    args=parser.parse_args()
    if args.datos_raiz: ROOT=args.datos_raiz.resolve();V7=ROOT/'SOCHER_2026_v7_2020_2026/mediciones'
    catalog()
    if args.solo_consolidar:
        manifests=[json.loads(p.read_text()) for p in sorted((OUT/'extractos').glob('*_manifest.json'))]
        assert len(manifests)==32
    else:
        source=sorted(p for p in (V7/'extractos').glob('*_manifest.json') if 2024<=json.loads(p.read_text())['anio']<=2026)
        assert len(source)==32
        with ThreadPoolExecutor(max_workers=2) as pool: manifests=list(pool.map(extract,source))
    consolidate(manifests)
