#!/usr/bin/env python3
"""Verifica metadatos, sin calcular ni seleccionar por precios.
Ejecutar desde la raíz de la carpeta de investigación original.
"""
from pathlib import Path
from collections import Counter
from datetime import date
import csv, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'SOCHER_2026_v7_2020_2026/entrega/por_anio/Dataset_precios_barra_hora_2025.csv'
G=date(2025,5,6)
items=Counter(); days={}; unknown=[]
with SOURCE.open() as f:
    for r in csv.DictReader(f):
        if r['barra_cmg']!='CHACABUCO_____110' or not '2025-01-14'<=r['fecha']<='2025-08-03': continue
        keys=(r['mes'],r['id_info_fuente'],r['barra_info_fuente'],r['estado_identidad'],r['fuente_id'])
        items[keys]+=1
        days.setdefault(keys,set()).add(r['fecha'])
        if r['id_info_fuente']!='703' or r['barra_info_fuente']!='BA S/E CHACABUCO 110KV BP1': unknown.append(r['fecha'])
fields=['mes','id_info_fuente','barra_info_fuente','estado_identidad','fuente_id','n_filas','n_fechas','fecha_min','fecha_max']
with (OUT/'identidad_chacabuco_2025.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(fields)
    for k,n in sorted(items.items()):w.writerow([*k,n,len(days[k]),min(days[k]),max(days[k])])
api=json.loads((OUT/'fuentes/Infotecnica_barra703_20260927.json').read_text())
assert api['id']==703 and api['nemotecnico']=='BA01T0835SE009T0835'
result={'ventana_metadata':['2025-01-14','2025-08-03'],'n_filas':sum(items.values()),'n_meses':len(items),'id_unico':'703','nombre_unico':'BA S/E CHACABUCO 110KV BP1','nemotecnico_api_20260927':api['nemotecnico'],'n_conflictos':len(unknown),'identidad_moderna_ventana':'IDENTIDAD_PUBLICADA_CONSTANTE; no certifica configuración operativa','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'g':'2025-05-06','pre':['2025-01-14','2025-04-28'],'post':['2025-05-06','2025-08-03'],'outcomes_consultados':False}
assert not unknown
(OUT/'validacion_identidad.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
