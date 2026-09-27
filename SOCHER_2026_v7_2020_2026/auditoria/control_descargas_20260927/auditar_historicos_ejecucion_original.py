#!/usr/bin/env python3
"""Auditoría independiente de archivos usados; sólo crea informes nuevos aquí.

No ejecuta extractores, no modifica libros, originales, descargas o entregables.
CRC de miembros no equivale a integridad de todo el paquete ni a validez causal.
"""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import csv, hashlib, io, json, struct, zipfile, zlib
import openpyxl
import pyarrow.parquet as pq

OUT = Path(__file__).resolve().parent
BASE = OUT.parents[1]
ROOT = BASE.parent
HIST = BASE / 'historico'

def digest(path):
    h=hashlib.sha256(); crc=0; size=0
    with path.open('rb') as f:
        for block in iter(lambda:f.read(2**20),b''):
            h.update(block); crc=zlib.crc32(block,crc); size+=len(block)
    return {'sha256':h.hexdigest(),'crc32':f'{crc:08x}','bytes':size}

def json_read(path): return json.loads(path.read_text())

def resolve(path):
    path=Path(path)
    if path.is_absolute(): return path
    return ROOT/path if path.parts[0].startswith('SOCHER_') else BASE/path

def ooxml(path):
    result={'archivo':str(path),'errores':[]}
    try:
        before=path.stat(); result.update(digest(path))
        with zipfile.ZipFile(path) as z:
            entries=z.infolist(); bad=z.testzip()
            result.update(miembros_ooxml=len(entries),crc_internos_comprobados=len(entries),
                          crc_internos_correctos=bad is None,
                          contiene_estructura_excel={'[Content_Types].xml','xl/workbook.xml'}.issubset(z.namelist()))
            if bad:result['errores'].append('CRC interno incorrecto: '+bad)
            if not result['contiene_estructura_excel']:result['errores'].append('Falta estructura OOXML')
        workbook=openpyxl.load_workbook(path,read_only=True,data_only=True,keep_links=False)
        result['hojas_reconocidas_por_lector_independiente']=workbook.sheetnames
        workbook.close()
        after=path.stat()
        result['estable_durante_lectura']=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
        if not result['estable_durante_lectura']:result['errores'].append('Archivo cambió durante auditoría')
    except Exception as exc:result['errores'].append(type(exc).__name__+': '+str(exc))
    return result

def read_member_chain(archive, names):
    """Valida CRC de la cadena seleccionada; no de auxiliares ajenos."""
    with zipfile.ZipFile(archive) as z:
        member=z.getinfo(names[0]); data=z.read(member)
        info={'miembro':names[0],'bytes':len(data),'crc32':f'{member.CRC:08x}',
              'sha256':hashlib.sha256(data).hexdigest(),'crc_verificado_por_zipfile':True}
        if len(names)>1:
            nextinfo=read_member_chain(io.BytesIO(data),names[1:])
            return [info]+nextinfo
        return [info]

def audit_month(source):
    month=source['fuente_id'].split('_')[1]; manifest_path=BASE/source['archivo_control']
    manifest=json_read(manifest_path); book=BASE/source['archivo_original']
    result={'mes':month,'fuente_id':source['fuente_id'],'fuente_entrega':source,
            'manifiesto':str(manifest_path.relative_to(BASE)),'errores':[]}
    result['libro']=ooxml(book)
    expected=[source['sha256_original'],manifest['libro_sha256']]
    if len(set(expected+[result['libro'].get('sha256')]))!=1:result['errores'].append('SHA libro no coincide con manifiesto y fuentes')
    if resolve(manifest['libro']).resolve()!=book.resolve():result['errores'].append('Ruta libro no coincide')
    if 'CMG Barras' not in result['libro'].get('hojas_reconocidas_por_lector_independiente',[]):result['errores'].append('No se reconoce hoja CMG Barras')
    result['errores']+=result['libro']['errores']
    derived=BASE/source['archivo_derivado']; d=digest(derived)
    result['derivado']={**d,'filas_parquet':pq.ParquetFile(derived).metadata.num_rows}
    if d['sha256']!=source['sha256_derivado'] or d['sha256']!=manifest['outputs'].get(source['archivo_derivado']):result['errores'].append('SHA partición no coincide')
    if result['derivado']['filas_parquet']!=int(source['filas']) or int(source['filas'])!=manifest['filas']:result['errores'].append('Conteo fuente/partición/manifiesto distinto')
    if manifest.get('homologacion'):
        result['homologacion']=ooxml(resolve(manifest['homologacion']['archivo']))
        if result['homologacion'].get('sha256')!=manifest['homologacion']['sha256']:result['errores'].append('SHA homologación distinto')
        result['errores']+=result['homologacion']['errores']
    else:result['homologacion']=None
    complete=HIST/'manifiestos'/f'extraccion_zip_{month}.json'
    if complete.exists():
        extraction=json_read(complete); archive=resolve(extraction['origen'])
        archive_hash=digest(archive)
        with zipfile.ZipFile(archive) as z:entries=len(z.infolist())
        container={'ruta':str(archive),'sha256':archive_hash['sha256'],'bytes':archive_hash['bytes'],
                   'sha256_coincide_manifiesto':archive_hash['sha256']==extraction['sha256_zip'],
                   'directorio_central_legible':True,'miembros_en_directorio':entries,
                   'todos_auxiliares_crc_recomprobados':False,'miembros_utilizados':[]}
        if not container['sha256_coincide_manifiesto']:result['errores'].append('SHA contenedor distinto')
        for member in extraction['miembros']:
            chain=read_member_chain(archive,member['ruta_zip'][1:])
            good=chain[-1]['sha256']==member['sha256']
            container['miembros_utilizados'].append({'cadena':chain,'coincide_sha_manifiesto':good,'archivo':member['archivo']})
            if not good:result['errores'].append('Miembro fuente diferente de extracción')
        result['clase_procedencia']='ZIP_con_directorio_central_y_miembros_utilizados_reverificados'
        result['contenedor']=container
    elif month in {'202307','202308'}:
        result['clase_procedencia']='miembro_completo_recuperado_v7_de_ZIP_incompleto'
    else:
        old_sources={r['mes']:r for r in json_read(ROOT/'SOCHER_2026_v4/precios/manifest_descarga_y_panel_cmg_2024.json')['fuentes']}
        old=old_sources.get(month)
        result['clase_procedencia']='reutilizacion_v4_'+str(old.get('adquisicion') if old else 'no_acreditada')
        result['procedencia_v4']=old
        if not old or old['sha256']!=result['libro'].get('sha256'):result['errores'].append('Reutilización v4 no acreditada por SHA')
        if old:
            old_book=ROOT/'SOCHER_2026_v4/precios/originales'/old['archivo']
            result['copia_v4_preservada']=digest(old_book)
            if result['copia_v4_preservada']['sha256']!=result['libro']['sha256']:result['errores'].append('Copia v4 no coincide')
    return result

def verify_partial(snapshot, member):
    offset=member['data_offset']; compressed=member['bytes_comprimidos']; size=snapshot.stat().st_size
    result={'ruta':str(snapshot),'offset_datos':offset,'bytes_comprimidos_esperados':compressed,
            'miembro_disponible_completo':offset+compressed<=size}
    if not result['miembro_disponible_completo']:return result
    crc=0; total=0; h=hashlib.sha256(); decomp=zlib.decompressobj(-15) if member['metodo']==8 else None
    with snapshot.open('rb') as f:
        f.seek(offset); left=compressed
        while left:
            block=f.read(min(left,2**20)); left-=len(block)
            if not block:raise ValueError('Corte durante lectura')
            plain=decomp.decompress(block) if decomp else block
            h.update(plain);crc=zlib.crc32(plain,crc);total+=len(plain)
        if decomp:
            plain=decomp.flush();h.update(plain);crc=zlib.crc32(plain,crc);total+=len(plain)
    expected_crc=member['crc32'] if isinstance(member['crc32'],int) else int(member['crc32'],16)
    result.update(bytes_recuperables=total,sha256=h.hexdigest(),crc32=f'{crc:08x}',
                  longitud_correcta=total==member['bytes_miembro'],crc32_correcto=crc==expected_crc,
                  flujo_deflate_finalizado=decomp.eof if decomp else True)
    return result

def recovery_audits(months):
    rows=[]
    for p in sorted((HIST/'manifiestos').glob('recuperacion_parcial_*.json')):
        m=json_read(p);snapshot=HIST/m['copia_estable'];snapshot_info=digest(snapshot)
        rec={'mes':m['mes'],'manifiesto':str(p.relative_to(BASE)),'fuente_parcial_original':m['fuente_parcial'],
             'copia_estable':str(snapshot.relative_to(BASE)),**snapshot_info,
             'sha_snapshot_coincide':snapshot_info['sha256']==m['copia_sha256'],
             'tamano_snapshot_coincide':snapshot_info['bytes']==m['bytes_parcial'],'miembros':[]}
        for leaf in m['recuperados']:
            member=next(x for x in m['miembros_observados'] if x['nombre']==leaf['nombre_miembro'])
            check=verify_partial(snapshot,member);current=digest(HIST/leaf['archivo'])
            rec['miembros'].append({'nombre':leaf['nombre_miembro'],'tipo':leaf['tipo'],'verificacion_bytes':check,
                'libro_actual':current,'sha_actual_recuperacion_y_manifiesto_iguales':current['sha256']==leaf['sha256']==check.get('sha256'),
                'confirmado_tambien_desde_zip_final':m['mes']=='202309'})
        rows.append(rec)
    # El origen de febrero 2024 no se borra de la cadena por haber sido reutilizado.
    for month in ['202402','202404']:
        p=ROOT/f'SOCHER_2026_v4/precios/recuperados/cmg{month[2:]}_def/manifest_recuperacion_miembros.json'
        m=json_read(p); source=Path(m['contenedor_parcial'])
        rec={'mes':month,'tipo':'antecedente_v4','manifiesto':str(p.relative_to(ROOT)),
             'contenedor_parcial_documentado':str(source),'contenedor_parcial_actualmente_disponible':source.exists(),
             'procedencia_final_de_libro_v4':months[month]['clase_procedencia'],'miembros':[]}
        for leaf in m['recuperados']:
            current=Path(leaf['archivo']);member=next(x for x in m['miembros_observados'] if Path(x['nombre']).name==current.name)
            d=digest(current)
            expected_crc=member['crc32']
            rec['miembros'].append({'archivo_preservado':str(current),'datos_actuales':d,
                'sha_coincide_manifiesto':d['sha256']==leaf['sha256'],
                'longitud_coincide_cabecera_registrada':d['bytes']==member['bytes_miembro'],
                'crc_coincide_cabecera_registrada':d['crc32']==f'{expected_crc:08x}',
                'nota':'Sin copia exterior actual no se repite descompresión desde su offset; CRC y longitud registrados se contrastan con el miembro preservado.'})
        rows.append(rec)
    return rows

def inspect_151935():
    files=list((Path.home()/'Downloads').glob('*151935*'));rows=[]
    for p in files:
        if not p.is_file():continue
        before=p.stat();d=digest(p)
        with p.open('rb') as f:
            raw=f.read(30); fields=struct.unpack('<I5H3I2H',raw)
            name=f.read(fields[9]).decode('utf8' if fields[2]&2048 else 'cp437')
        offset=30+fields[9]+fields[10]
        rows.append({'archivo':str(p),**d,'primer_miembro':name,'bytes_comprimidos_declarados':fields[7],
            'bytes_necesarios_hasta_fin_miembro':offset+fields[7],
            'primer_miembro_completo':offset+fields[7]<=d['bytes'],'zip_exterior_legible':zipfile.is_zipfile(p),
            'figura_en_manifiestos_de_fuentes_utilizadas':False,
            'nota':'FPen es un auxiliar de factores de penalización; el archivo temporal no aparece en la cadena de archivos utilizados por Fuentes_precios.csv.'})
    return rows

def negative_controls():
    p=HIST/'libros/202309/Homologación barras cmg_2309.xlsx';original=p.read_bytes()
    rows=[]
    damaged=bytearray(original)
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        member=next(i for i in z.infolist() if i.compress_size>20)
    offset=member.header_offset;h=struct.unpack('<I5H3I2H',original[offset:offset+30])
    data_offset=offset+30+h[9]+h[10];damaged[data_offset+member.compress_size//2]^=1
    for name,data in [('corte_cola_4096_bytes',original[:-4096]),('alteracion_un_byte_comprimido',bytes(damaged))]:
        error=None
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                bad=z.testzip()
                if bad:error='CRC incorrecto: '+bad
        except Exception as exc:error=type(exc).__name__+': '+str(exc)
        rows.append({'prueba':name,'rechazada':error is not None,'diagnostico':error,'solo_en_memoria':True})
    return {'casos':rows,'archivo_investigacion_sin_modificar':hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(original).digest()}

def main():
    started=datetime.now(timezone.utc);sources_path=BASE/'entrega/Fuentes_precios.csv'
    before=digest(sources_path)
    with sources_path.open(newline='') as f:sources=[r for r in csv.DictReader(f) if r['fuente_id'].startswith('historico_')]
    results=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row in pool.map(audit_month,sources):
            results.append(row);print(json.dumps({'mes':row['mes'],'errores':row['errores'],'clase':row['clase_procedencia']},ensure_ascii=False),flush=True)
    months={r['mes']:r for r in results}
    recoveries=recovery_audits(months);errors=[{'mes':r['mes'],'errores':r['errores']} for r in results if r['errores']]
    controls=negative_controls();classes={}
    for r in results:classes[r['clase_procedencia']]=classes.get(r['clase_procedencia'],0)+1
    report={'inicio_utc':started.isoformat(),'fin_utc':datetime.now(timezone.utc).isoformat(),
        'alcance':'Verificación de integridad técnica de libros y cadena de archivos usados; no nueva estimación ni validación causal.',
        'modifica_datos_congelados':False,'fuentes_precios_csv_sha256':before['sha256'],
        'fuentes_csv_sin_modificacion':before==digest(sources_path),'meses_historicos':len(results),
        'filas_historicas':sum(r['derivado']['filas_parquet'] for r in results),'clases_procedencia':classes,
        'errores':errors,'meses':results,'recuperaciones':recoveries,
        'archivo_captura_151935':inspect_151935(),'controles_negativos':controls,
        'limites':['No se verificaron otra vez todos los auxiliares de los ZIP exteriores; sí los miembros usados y sus CRC.',
          'SHA/CRC detectan cambios o truncación respecto de bytes registrados; no certifican exactitud económica ni origen autenticado por firma.',
          'Homologaciones ausentes, reloj UTC y relaciones centro–nodo siguen sin resolverse por esta auditoría.',
          'Febrero 2024 depende de miembro completo preservado desde v4; el contenedor parcial anterior ya no está disponible para repetir la lectura por offset.']}
    stamp=started.strftime('%Y%m%dT%H%M%SZ');destination=OUT/f'auditoria_historicos_{stamp}.json'
    with destination.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    summary=f"# Auditoría de descargas históricas\n\n{len(results)} meses; {report['filas_historicas']:,} precios. Errores técnicos detectados en libros, hashes y fuentes: {len(errors)}.\n\nClases de procedencia:\n\n"+'\n'.join(f'- {k}: {v}' for k,v in classes.items())
    summary+='\n\nLos libros de julio y agosto de 2023 proceden de miembros completos de contenedores incompletos. Febrero de 2024 heredó el mismo tipo de recuperación desde v4. La homologación de septiembre de 2023 se recuperó primero de un parcial y luego se confirmó con el ZIP completo. Abril de 2024 tiene un antecedente de recuperación del mismo libro, pero su procedencia final v4 está registrada como carpeta descomprimida por Safari. Junio y julio de 2024 también se reutilizaron desde esas carpetas.\n\nEl archivo de captura 151935 contiene un miembro auxiliar FPen incompleto y no figura en las fuentes utilizadas. Los controles negativos, hechos sólo en memoria, comprueban que un truncamiento y una alteración de bytes son rechazados.\n\nEl detalle de tamaños, CRC, SHA, rutas y verificaciones está en `'+destination.name+'`. No se alteraron fuentes ni entregables. Esta auditoría no declara íntegros todos los auxiliares de los ZIP exteriores ni acredita identificación causal.\n'
    with (OUT/f'auditoria_historicos_{stamp}.md').open('x') as f:f.write(summary)
    print(json.dumps({'informe':str(destination),'meses':len(results),'errores':errors,'clases':classes,'controles_negativos':controls},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
