#!/usr/bin/env python3
"""Empaqueta CSV anuales y capas separadas; no modifica las tablas verificadas."""
from pathlib import Path
import hashlib,json,zipfile
BASE=Path(__file__).resolve().parents[1]

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def package(name,files,description):
 out=BASE/'paquetes';out.mkdir(exist_ok=True)
 p=out/name
 records=[{'archivo':n,'bytes':s.stat().st_size,'sha256':sha(s)} for s,n in files]
 with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for source,member in files:z.write(source,member,compress_type=zipfile.ZIP_STORED if source.suffix=='.gz' else zipfile.ZIP_DEFLATED)
  z.writestr('MANIFIESTO_ARCHIVOS.json',json.dumps({'version':'v0.2.0','alcance':description,'archivos':records},ensure_ascii=False,indent=2)+'\n')
 with zipfile.ZipFile(p) as z:
  if z.testzip() is not None:raise ValueError('Fallo CRC de '+name)
  for r in records:
   h=hashlib.sha256()
   with z.open(r['archivo']) as f:
    for b in iter(lambda:f.read(2**20),b''):h.update(b)
   if h.hexdigest()!=r['sha256']:raise ValueError('Miembro distinto: '+r['archivo'])
 return {'archivo':name,'bytes':p.stat().st_size,'sha256':sha(p),'miembros':len(records)+1}

def main():
 ent=BASE/'entrega';m=json.loads((ent/'Manifiesto_entrega.json').read_text());check=json.loads((ent/'Verificacion_entrega.json').read_text())
 if m['estado']!='82_fuentes_DEF_integradas' or check['estado']!='OK':raise ValueError('Primero cerrar y verificar la entrega completa')
 for r in m['archivos']:
  if sha(ent/r['archivo'])!=r['sha256']:raise ValueError('Entrega cambió: '+r['archivo'])
 annual=[(p,str(p.relative_to(ent))) for p in sorted((ent/'por_anio').glob('*.csv'))]
 for name in ['Diccionario_precios.csv','Cobertura_por_anio.csv','Cobertura_por_mes_regimen.csv','Cobertura_por_mes_barra.csv','Faltantes_precios_detalle.csv','Fuentes_precios.csv','LEEME_dataset.md','Manifiesto_entrega.json','Verificacion_entrega.json']:
  annual.append((ent/name,name))
 ancillary=[(p,str(p.relative_to(ent))) for folder in ['mediciones_separadas','preliminares_separados'] for p in sorted((ent/folder).glob('*')) if p.is_file()]
 for name in ['mediciones_candidatos_15min.csv.gz','cobertura_y_canales_por_mes.csv','resumen_transformadores_por_anio.csv']:
  ancillary.append((BASE/'mediciones/tablas'/name,'mediciones_15min/'+name))
 ancillary.append((BASE/'mediciones/verificacion_final_productos.json','mediciones_15min/verificacion_final_productos.json'))
 result=[package('CSV_por_anio_2020_2026.zip',annual,'Siete archivos anuales del CSV de precios y sus metadatos; 2026 hasta el corte observado.'),package('Capas_complementarias_2020_2026.zip',ancillary,'Mediciones horarias y a 15 minutos, y PRE septiembre2026; capas separadas, no unidas automáticamente al precio.')]
 (BASE/'paquetes/Verificacion_archivos_version.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
