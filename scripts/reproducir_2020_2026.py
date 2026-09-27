#!/usr/bin/env python3
"""Verifica el paquete de insumos y reconstruye la ampliación 2020–2026.

El paquete es una instantánea de las particiones extraídas. Las descargas
nacionales originales corresponden a una etapa separada y documentada.
"""
import argparse, datetime, hashlib, json, re, subprocess, sys, zipfile
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'SOCHER_2026_v7_2020_2026'

def require(condition,message):
 if not condition:raise ValueError(message)

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--insumos',type=Path,required=True,help='ZIP de insumos publicado con v0.2.0')
 args=ap.parse_args()
 contract=json.loads((ROOT/'contracts/insumos_2020_2026.json').read_text())
 archive=args.insumos.resolve()
 require(sha(archive)==contract['sha256'],'SHA del paquete distinto al publicado')
 if 'bytes' in contract:require(archive.stat().st_size==contract['bytes'],'Tamaño del paquete distinto al contrato')
 with zipfile.ZipFile(archive) as z:
  names=z.namelist()
  require(len(names)==len(set(names)),'Miembros ZIP duplicados')
  manifest=json.loads(z.read('MANIFIESTO_INSUMOS.json'))
  records=manifest['archivos']
  require(len(records)==len({r['archivo'] for r in records}),'Entradas duplicadas en manifiesto')
  allowed={r['archivo'] for r in manifest['archivos']}|{'MANIFIESTO_INSUMOS.json'}
  require(set(names)==allowed,'Miembros no declarados o ausentes')
  require(sha(BASE/'scripts/construir_entrega.py')==manifest['sha256_constructor'],'Constructor distinto del usado para la versión; usar el código del tag publicado')
  # Validar todo antes de escribir evita una extracción parcial cuando hay un
  # archivo diferente en el checkout. Las guardas siguen activas con python -O.
  for row in manifest['archivos']:
   member=PurePosixPath(row['archivo'])
   require(not member.is_absolute() and '..' not in member.parts and '\\' not in row['archivo'],'Ruta ZIP no portable o externa')
   require(bool(re.fullmatch('[0-9a-f]{64}',row['sha256'])) and isinstance(row['bytes'],int) and row['bytes']>=0,'Metadatos de miembro inválidos')
   target=(BASE/row['archivo']).resolve()
   require(target.is_relative_to(BASE.resolve()),'Ruta externa en archivo')
   data=z.read(row['archivo'])
   require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'Hash o tamaño incorrecto: '+row['archivo'])
   if target.exists():
    require(target.is_file() and sha(target)==row['sha256'],'Se conserva archivo diferente; usar un checkout limpio: '+str(target))
  for row in manifest['archivos']:
   target=(BASE/row['archivo']).resolve()
   if not target.exists():
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(row['archivo']))
 subprocess.run([sys.executable,str(BASE/'scripts/construir_entrega.py')],cwd=ROOT,check=True)
 csv=BASE/'entrega/Dataset_precios_barra_hora_2020_2026.csv'
 actual=sha(csv)
 require(actual==contract['csv_principal_sha256']==manifest['csv_principal_sha256'],'CSV reconstruido distinto de la entrega')
 result={'estado':'OK','paquete_sha256':contract['sha256'],'insumos_verificados':len(manifest['archivos']),
  'csv_reconstruido_sha256':actual,'csv_identico_version_publicada':True,
  'alcance':'Reconstrucción desde particiones archivadas; no prueba nueva adquisición de originales ni identificación causal.',
  'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 out=ROOT/'artifacts';out.mkdir(exist_ok=True)
 (out/'reproduccion_2020_2026.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
