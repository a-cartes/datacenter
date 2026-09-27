#!/usr/bin/env python3
"""Reproduce contrastes con CSV anual horario congelado, sin leer panel diario.
No calcula inferencia ni cambia ventana o fecha. El archivo analisis se lee al final
solo para comparar las salidas independientes con las ya calculadas.
"""
from pathlib import Path
from datetime import date
from statistics import mean
import csv, json, math, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'SOCHER_2026_v7_2020_2026/entrega/por_anio/Dataset_precios_barra_hora_2025.csv'
EXPECTED=OUT.parent/'analisis/resultados/contrastes_descriptivos.csv'
BAR=['CHACABUCO_____110','QUILLOTA______110','QUILLOTA______220']
IDS=dict(zip(BAR,['703','1242','519']))
G=date(2025,5,6); records={}; conflicts=[]
with SOURCE.open() as f:
 for r in csv.DictReader(f):
  if r['barra_cmg'] not in BAR or not '2025-01-14'<=r['fecha']<='2025-08-03':continue
  assert r['version_fuente']=='REAL-DEF'
  assert r['regimen_precio']=='CMg_Real_nuevo_desde_2024-07-15'
  assert r['id_info_fuente']==IDS[r['barra_cmg']]
  key=(r['fecha'],r['barra_cmg']);h=r['hora_fuente_moderna']
  day=records.setdefault(key,{})
  assert h not in day,(key,h)
  day[h]=float(r['precio_usd_mwh'])
daily={};excluded=[]
for d in sorted({d for d,b in records}):
 vals=[records.get((d,b),{}) for b in BAR]; signatures=[set(v) for v in vals]
 if not all(len(v)==24 and all(math.isfinite(x) for x in v.values()) for v in vals) or not signatures[0]==signatures[1]==signatures[2]:
  excluded.append({'fecha':d,'n_chac':len(vals[0]),'n_q110':len(vals[1]),'n_q220':len(vals[2])});continue
 hs=sorted(signatures[0],key=int)
 # El precio de cada referencia se lee desde su propia fila original; no se usa
 # el diferencial ni las columnas de precio de referencia guardadas en Chacabuco.
 daily[d]={'precio_mean_usd_mwh':mean(vals[0][h] for h in hs),'precio_q110':mean(vals[1][h] for h in hs),'precio_q220':mean(vals[2][h] for h in hs),'dif_q110_mean_usd_mwh':mean(vals[0][h]-vals[1][h] for h in hs),'dif_q220_mean_usd_mwh':mean(vals[0][h]-vals[2][h] for h in hs)}
scenarios=[('principal',-112,-8,0,89,[]),('post28',-112,-8,0,27,[]),('anticipacion0',-112,-1,0,89,[]),('anticipacion14',-112,-15,0,89,[]),('sin_apagon_25_26feb',-112,-8,0,89,['2025-02-25','2025-02-26'])]
rows=[]
for name,a,b,c,e,skip in scenarios:
 pre=[v for d,v in daily.items() if a<=(date.fromisoformat(d)-G).days<=b and d not in skip]
 post=[v for d,v in daily.items() if c<=(date.fromisoformat(d)-G).days<=e and d not in skip]
 for series in ['dif_q110_mean_usd_mwh','dif_q220_mean_usd_mwh','precio_mean_usd_mwh','precio_q110','precio_q220']:
  p=mean(x[series] for x in pre);q=mean(x[series] for x in post)
  rows.append({'escenario':name,'serie':series,'n_pre':len(pre),'n_post':len(post),'media_pre_usd_mwh':p,'media_post_usd_mwh':q,'cambio_descriptivo_usd_mwh':q-p,'es_estimacion_causal':False})
with (OUT/'contrastes_independientes.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
expected={ (r['escenario'],r['serie']):r for r in csv.DictReader(EXPECTED.open()) }
maxerr=0
for r in rows:
 e=expected[(r['escenario'],r['serie'])]
 assert r['n_pre']==int(e['n_pre']) and r['n_post']==int(e['n_post'])
 for k in ['media_pre_usd_mwh','media_post_usd_mwh','cambio_descriptivo_usd_mwh']:
  err=abs(r[k]-float(e[k]));maxerr=max(err,maxerr);assert err<1e-8,(r['escenario'],r['serie'],k,err)
result={'estado':'PASS','fuente_exclusiva_calculo':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'no_usa_panel_diario':True,'no_usa_diferenciales_precalculados':True,'n_contrastes_verificados':len(rows),'tolerancia_absoluta':1e-8,'max_discrepancia_por_redondeo':maxerr,'dias_sin_soporte24':excluded,'n_asignaciones_independientes':1,'inferencias_causales':False,'observacion':'25 contrastes son resúmenes descriptivos del mismo episodio, no pruebas independientes.'}
(OUT/'verificacion_contrastes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
