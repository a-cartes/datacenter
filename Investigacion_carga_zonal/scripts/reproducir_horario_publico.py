"""Repite las 40 regresiones horarias principales desde el panel público, sin originales."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from estimar_heterogeneidad_horaria import estimate
S=Path(__file__).resolve().parents[1];root=S/'resultados/20261011_horas_v1'
d=pd.read_csv(root/'panel_horario.csv.gz');old=pd.read_csv(root/'estimaciones_principales.csv');rows=[]
for fe in ['A_mes_horasemana','B_dia_meshora_horasemana']:
 for spec in ['lineal','bloques','carga_alta','precio_alto']:
  r,_=estimate(d,fe,spec,'principal');rows.extend(r)
new=pd.DataFrame(rows);keys=['FE','modelo','resultado','contraste'];joined=old.merge(new,on=keys,suffixes=('_anterior','_nuevo'),validate='one_to_one');assert len(joined)==len(old)==120
errors={k:float(np.max(np.abs(joined[k+'_anterior']-joined[k+'_nuevo']))) for k in ['beta','se_semana_HAC4','se_mes_cluster']}
assert max(errors.values())<1e-7
print(json.dumps(dict(estado='OK',regresiones=40,contrastes=120,errores_maximos=errors,originales_necesarios=False),indent=2,ensure_ascii=False))
