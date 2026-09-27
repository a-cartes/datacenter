#!/usr/bin/env python3
"""Copia trazable de la etapa canónica al repositorio; no hace commit ni push."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import shutil

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--repository',type=Path,required=True);p.add_argument('--xlsx',type=Path,required=True);a=p.parse_args()
    stage=a.root.resolve()/'SOCHER_2026_v8_panel_causal';target=a.repository.resolve()/stage.name
    assert target!=stage,'No copiar sobre la carpeta canónica'
    assert (a.repository.resolve()/'.git').exists(),'Destino debe ser el repositorio ya existente'
    book=stage/'revision/Revision_panel_causal_v8.xlsx';shutil.copy2(a.xlsx,book)
    src=stage/'panel/panel_diario.csv';gz=src.with_suffix('.csv.gz')
    with src.open('rb') as r,gz.open('wb') as w,gzip.GzipFile(filename='',mode='wb',fileobj=w,mtime=0) as z:shutil.copyfileobj(r,z)
    with gzip.open(gz,'rb') as f:recovered=hashlib.file_digest(f,'sha256').hexdigest()
    assert recovered==digest(src)
    copy_records=[];omitted=[]
    for item in sorted(stage.rglob('*')):
        rel=item.relative_to(stage)
        if not item.is_file():continue
        if 'node_modules' in rel.parts or '__pycache__' in rel.parts or item.name=='.DS_Store':continue
        if str(rel)=='panel/panel_diario.csv' or str(rel)=='revision/contenido_excel.json' or (str(rel).startswith('revision/qa/') and item.suffix=='.png'):
            omitted.append(str(rel));continue
        if str(rel)=='validacion/copia_repositorio.json':continue
        dest=target/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(item,dest)
        h=digest(item);assert digest(dest)==h
        copy_records.append({'ruta':str(rel),'bytes':item.stat().st_size,'sha256':h})
    report={'estado':'OK','carpeta_canonica':stage.name,'copias_verificadas':len(copy_records),'csv_diario_recuperado_sha256':recovered,'omitidos_regenerables':omitted,'archivos':copy_records}
    data=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    (stage/'validacion/copia_repositorio.json').write_text(data);(target/'validacion/copia_repositorio.json').write_text(data)
    print(json.dumps({'archivos_copiados_verificados':len(copy_records),'bytes':sum(r['bytes'] for r in copy_records),'gzip_diario_bytes':gz.stat().st_size},ensure_ascii=False))

if __name__=='__main__':main()
