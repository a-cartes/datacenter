#!/usr/bin/env python3
"""Contrasta una descarga oficial nueva sin cambiar fuentes o datos congelados.

Preserva copia estable del ZIP, comprueba todos los CRC del contenedor exterior
y compara miembros de precios/homologación con los libros usados en la entrega.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, csv, hashlib, json, os, re, shutil, zipfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(2**20),b''):h.update(block)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mes',required=True)
    ap.add_argument('--archivo',type=Path,required=True)
    ap.add_argument('--url-observada',required=True)
    ap.add_argument('--conservar-homologaciones-adicionales',action='store_true',
                    help='Guarda sólo en esta auditoría los miembros nuevos, sin incorporarlos a datos congelados')
    a=ap.parse_args(); started=datetime.now(timezone.utc); before=a.archivo.stat()
    if not re.fullmatch(r'20\d{4}',a.mes):raise ValueError('Mes no válido')
    with (BASE/'entrega/Fuentes_precios.csv').open(newline='') as f:
        matches=[r for r in csv.DictReader(f) if r['fuente_id']==f'historico_{a.mes}_DEF']
    if len(matches)!=1:raise ValueError('Fuente histórica no única')
    source=matches[0]
    if source['url_original']!=a.url_observada:raise ValueError('URL observada distinta del catálogo congelado; investigar versión antes de contrastar')
    manifest=json.loads((BASE/source['archivo_control']).read_text())
    folder=HERE/'originales_contraste';folder.mkdir(exist_ok=True)
    temp=folder/(a.archivo.name+'.copia_en_curso')
    if temp.exists():raise ValueError('Ya existe copia en curso; no sobrescribir')
    shutil.copyfile(a.archivo,temp); after=a.archivo.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        temp.unlink();raise ValueError('La descarga cambió durante copia; no aceptada')
    digest=sha(temp)
    if sha(a.archivo)!=digest:
        temp.unlink();raise ValueError('SHA copia diferente de descarga')
    snapshot=folder/f'{a.mes}_{digest[:16]}.zip'
    if snapshot.exists():
        if sha(snapshot)!=digest:raise ValueError('Colisión de copia')
        temp.unlink()
    else:os.replace(temp,snapshot)
    errors=[];members=[];compared=[]
    with zipfile.ZipFile(snapshot) as z:
        bad=z.testzip()
        if bad:errors.append('CRC exterior incorrecto: '+bad)
        for entry in z.infolist():
            members.append({'nombre':entry.filename,'bytes':entry.file_size,'bytes_comprimidos':entry.compress_size,
                            'crc32':f'{entry.CRC:08x}','offset':entry.header_offset})
            base=Path(entry.filename).name
            kind='precios' if re.fullmatch(r'cmg_?'+a.mes[2:]+r'_def\.xls[mx]',base,re.I) else 'homologacion' if 'homolog' in base.lower() and base.lower().endswith('.xlsx') and 'prg' not in base.lower() else None
            if kind is None:continue
            h=hashlib.sha256()
            with z.open(entry) as f:
                for block in iter(lambda:f.read(2**20),b''):h.update(block)
            expected=source['sha256_original'] if kind=='precios' else (manifest.get('homologacion') or {}).get('sha256')
            current=BASE/source['archivo_original'] if kind=='precios' else Path(manifest['homologacion']['archivo']) if manifest.get('homologacion') else None
            current_sha=sha(current) if current else None
            record={'tipo':kind,'miembro':entry.filename,'bytes':entry.file_size,'crc32':f'{entry.CRC:08x}',
                    'sha256_nueva_descarga':h.hexdigest(),'sha256_usado_registrado':expected,
                    'sha256_usado_actual':current_sha,'coincide_con_usado':h.hexdigest()==expected==current_sha if expected else None,
                    'estado':'comparado_con_fuente_congelada' if expected else 'miembro_adicional_no_incorporado_en_fuente_congelada'}
            if expected and not record['coincide_con_usado']:errors.append('Miembro distinto: '+entry.filename)
            if kind=='homologacion' and not expected and a.conservar_homologaciones_adicionales:
                sidecar_dir=HERE/'miembros_nuevos'/a.mes;sidecar_dir.mkdir(parents=True,exist_ok=True)
                sidecar=sidecar_dir/base
                if sidecar.exists():
                    if sha(sidecar)!=h.hexdigest():raise ValueError('Sidecar ya existe con distinto contenido; no sobrescribir')
                else:
                    with sidecar.open('xb') as out:out.write(z.read(entry))
                if sha(sidecar)!=h.hexdigest():raise ValueError('Hash sidecar distinto')
                record['sidecar_auditoria']=str(sidecar.relative_to(BASE))
                record['incorporacion']='PENDIENTE_VERSION_FUTURA_NO_INCORPORADA_A_V0.2.0'
            compared.append(record)
    if sum(c['tipo']=='precios' for c in compared)!=1:errors.append('Libro de precios no único o ausente en nueva descarga')
    if manifest.get('homologacion') and not any(c['tipo']=='homologacion' and c['coincide_con_usado'] for c in compared):errors.append('No se encontró homologación idéntica a la utilizada')
    report={'inicio_utc':started.isoformat(),'fin_utc':datetime.now(timezone.utc).isoformat(),'mes':a.mes,
            'estado':'OK' if not errors else 'DIFERENCIAS','errores':errors,'url_oficial_observada':a.url_observada,
            'archivo_descargado':str(a.archivo),'bytes_descarga':before.st_size,'mtime_descarga_ns':before.st_mtime_ns,
            'copia_preservada':str(snapshot.relative_to(BASE)),'sha256_zip':digest,
            'directorio_central_legible':True,'crc_todos_miembros_exteriores_correcto':bad is None,
            'n_miembros_exteriores':len(members),'miembros_exteriores':members,
            'miembros_comparados_con_entrega':compared,'fuente_entrega':source,
            'datos_congelados_modificados':False,
            'alcance':'CRC de todos los miembros del ZIP exterior y comparación SHA de libros. No estima efectos ni modifica homologaciones de la versión congelada; no equivale a validación económica o causal.'}
    stamp=started.strftime('%Y%m%dT%H%M%SZ'); output=HERE/f'contraste_zip_completo_{a.mes}_{stamp}.json'
    with output.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'informe':str(output),'mes':a.mes,'estado':report['estado'],'errores':errors,
                      'crc_todos_miembros_exteriores_correcto':bad is None,'miembros_comparados':compared},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
