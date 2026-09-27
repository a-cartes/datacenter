#!/usr/bin/env python3
"""Congela las entradas verificadas de la entrega, sin los originales nacionales.

El ZIP resultante permite reconstruir los CSV, no sustituye a los originales ni
certifica las identidades físicas. Sus miembros llevan SHA-256 independientes.
"""
from pathlib import Path
import argparse, csv, datetime, hashlib, json, zipfile

BASE=Path(__file__).resolve().parents[1]

def require(condition,message):
 if not condition:raise ValueError(message)

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--salida',type=Path,default=BASE/'paquetes')
 args=parser.parse_args()
 manifest=json.loads((BASE/'entrega/Manifiesto_entrega.json').read_text())
 check=json.loads((BASE/'entrega/Verificacion_entrega.json').read_text())
 require(manifest['estado']=='82_fuentes_DEF_integradas','No empaquetar una entrega parcial como completa')
 require(check['estado']=='OK','La verificación de entrega no está aprobada')
 require(sha(BASE/'scripts/construir_entrega.py')==manifest['sha256_script'],'Constructor cambió después de generar la entrega; reconstruir y verificar primero')
 require(check['filas_csv']==check['filas_parquet']==manifest['filas_precios_DEF'],'Conteos de entrega y verificación distintos')
 require(check.get('filas_comparadas_todas_columnas')==manifest['filas_precios_DEF'] and check.get('columnas_comparadas')==31,'Falta verificación integral de las 31 columnas')
 for item in manifest['archivos']:
  p=BASE/'entrega'/item['archivo']
  require(p.is_file() and p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],'Entregable cambió después de verificar: '+item['archivo'])
 # El OK de ayer no acredita las particiones de hoy. Comprobar el mismo hash
 # con el que se construyeron Fuentes_precios.csv y las capas de mediciones.
 with (BASE/'entrega/Fuentes_precios.csv').open(newline='',encoding='utf-8') as f:sources=list(csv.DictReader(f))
 require(len(sources)==82 and len({s['fuente_id'] for s in sources})==82,'Fuentes DEF incompletas o repetidas')
 originals_checked=0;originals_unavailable=[]
 for source in sources:
  p=(BASE/source['archivo_derivado']).resolve()
  require(p.is_relative_to(BASE.resolve()) and p.is_file() and sha(p)==source['sha256_derivado'],'Partición cambió después de la entrega: '+source['fuente_id'])
  original=(BASE/source['archivo_original']).resolve()
  if original.is_file():
   require(sha(original)==source['sha256_original'],'Original cambió después de la entrega: '+source['fuente_id'])
   originals_checked+=1
  else:originals_unavailable.append(source['fuente_id'])
 for layer in manifest['mediciones']:
  p=BASE/layer['fuente']
  require(p.is_file() and sha(p)==layer['sha256_fuente'],'Capa de mediciones cambió después de la entrega: '+layer['fuente'])
 require(sha(BASE/'mediciones/Cobertura_mediciones_2020_2026.md')==sha(BASE/'entrega/mediciones_separadas/Cobertura_mediciones_2020_2026.md'),'Guía de mediciones cambió después de la entrega')
 files=set()
 for pattern in [
  'historico/derivados/precios_*.parquet','historico/manifiestos/precios_*.json',
  'historico/catalogo/*.json','historico/catalogo/*.csv',
  'moderno/datos/*_horario.parquet','moderno/datos/*_15min.parquet',
  'moderno/fuentes/metadatos/*.json','moderno/config/*.json','moderno/config/*.csv',
  'moderno/fuentes/ejecuciones_ci.json','moderno/fuentes/indice_tsv_moderno.json',
  'moderno/verificacion_moderno.json',
  'moderno/datos/cobertura_barras_meses_moderno.csv','moderno/datos/cobertura_diaria_etiquetas_moderno.csv.gz','moderno/datos/identidades_publicadas_por_mes.csv','moderno/datos/resumen_particiones_moderno.csv','moderno/datos/resumen_marcas_fuente.csv',
  'mediciones/tablas/*.parquet','mediciones/tablas/*.json',
  'mediciones/Cobertura_mediciones_2020_2026.md',
  'mediciones/verificacion_final_productos.json',
  'auditoria/*.json','auditoria/*.csv',
 ]:
  files.update(p for p in BASE.glob(pattern) if p.is_file())
 require(len(list(BASE.glob('historico/derivados/precios_*.parquet')))==55,'No hay 55 particiones históricas')
 require(len(list(BASE.glob('moderno/datos/*_DEF_horario.parquet')))==27,'No hay 27 particiones modernas DEF')
 records=[{'archivo':str(p.relative_to(BASE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]
 metadata={'version':'v0.2.0','alcance':'Reconstrucción de CSV y coberturas desde particiones extraídas y verificadas; no incluye los originales nacionales completos.',
  'creado_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archivos':records,
  'sha256_constructor':manifest['sha256_script'],
  'fuentes_originales_presentes_reverificadas':originals_checked,'fuentes_originales_no_presentes_no_requeridas_para_reconstruccion':originals_unavailable,
  'csv_principal_sha256':sha(BASE/'entrega/Dataset_precios_barra_hora_2020_2026.csv')}
 args.salida.mkdir(parents=True,exist_ok=True)
 package=args.salida/'Insumos_reproduccion_2020_2026.zip'
 staging=package.with_suffix('.zip.tmp')
 with zipfile.ZipFile(staging,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for p in sorted(files):z.write(p,str(p.relative_to(BASE)))
  z.writestr('MANIFIESTO_INSUMOS.json',json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
 with zipfile.ZipFile(staging) as z:
  require(z.testzip() is None,'Fallo CRC del paquete')
  for item in records:
   require(hashlib.sha256(z.read(item['archivo'])).hexdigest()==item['sha256'],'Miembro ZIP distinto del inventario: '+item['archivo'])
 staging.replace(package)
 outer={'archivo':package.name,'bytes':package.stat().st_size,'sha256':sha(package),'miembros':len(records)+1,
        'csv_principal_sha256':metadata['csv_principal_sha256']}
 (args.salida/'Insumos_reproduccion_2020_2026.sha256.json').write_text(json.dumps(outer,indent=2)+'\n')
 print(json.dumps(outer),flush=True)

if __name__=='__main__':main()
