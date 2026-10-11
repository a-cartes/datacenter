"""Panel horario, heterogeneidad y absorción de FE; conserva originales y resultados previos."""
from pathlib import Path
from datetime import datetime
import argparse,hashlib,json,subprocess
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests
from conciliar_canteras_odata import normal_day
S=Path(__file__).resolve().parents[1];R=S.parent
YCOL=['zona_cerca','zona_lejos5','zona_lejos7','canteras_lejos5','D_zona']

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def absorb(a,keys):
 z=np.asarray(a,dtype=float).copy();cats=[pd.factorize(k,sort=True)[0] for k in keys]
 for iteration in range(1000):
  before=z.copy()
  for g in cats:
   counts=np.bincount(g); sums=np.zeros((len(counts),z.shape[1]));np.add.at(sums,g,z);z-=sums[g]/counts[g,None]
  if np.max(np.abs(z-before))<1e-10:break
 else:raise ValueError('FE no converge')
 err=0.
 for g in cats:
  sums=np.zeros((g.max()+1,z.shape[1]));np.add.at(sums,g,z);err=max(err,float(np.max(np.abs(sums/np.bincount(g)[:,None]))))
 if err>1e-7:raise ValueError('Residuo FE no centrado')
 return z,iteration+1,err

def matrices(d,spec):
 x=d[['MW']].copy()
 if spec=='bloques':x['MW_solar']=d.MW*d.solar;x['MW_tarde']=d.MW*d.tarde
 if spec=='carga_alta':x['exceso']=np.maximum(d.MW-d.umbral75,0)
 if spec=='precio_alto':x['precio_alto']=d.altoQ;x['MW_precio_alto']=d.MW*d.altoQ
 return x

def contrasts(spec):
 if spec=='lineal':return [('pendiente',[1],False)]
 if spec=='bloques':return [('resto',[1,0,0],False),('solar',[1,1,0],False),('tarde',[1,0,1],False),('solar_menos_resto',[0,1,0],True),('tarde_menos_resto',[0,0,1],True)]
 if spec=='carga_alta':return [('carga_hasta_p75',[1,0],False),('carga_sobre_p75',[1,1],False),('alta_menos_baja',[0,1],True)]
 return [('Q_menor100',[1,0,0],False),('Q_mayor_igual100',[1,0,1],False),('Q_alto_menos_bajo',[0,0,1],True)]

def estimate(d,fe,spec,label):
 x=matrices(d,spec);keys=[d.mes,d.hora_semana] if fe=='A_mes_horasemana' else [d.fecha,d.mes+'_'+d.hora0.astype(str),d.hora_semana]
 vals=np.column_stack([x.to_numpy(),d[YCOL].to_numpy()]);z,it,err=absorb(vals,keys);X=z[:,:len(x.columns)];YY=z[:,len(x.columns):]
 if np.linalg.matrix_rank(X)<X.shape[1]:raise ValueError('Matriz singular')
 beta=np.linalg.lstsq(X,YY,rcond=None)[0];bread=np.linalg.inv(X.T@X);res=YY-X@beta
 weeks=pd.to_datetime(d.fecha).dt.to_period('W-SUN').astype(str);months=d.mes
 results=[];parameters=[]
 for j,y in enumerate(YCOL):
  scores=X*res[:,j,None];vs={}
  for mode,labels in [('semana_HAC4',weeks),('mes_cluster',months)]:
   g,unique=pd.factorize(labels,sort=True);G=len(unique);s=np.zeros((G,X.shape[1]));np.add.at(s,g,scores);meat=s.T@s
   if mode=='semana_HAC4':
    for lag in range(1,5):
     v=s[lag:].T@s[:-lag];meat+=(1-lag/5)*(v+v.T)
   vs[mode]=bread@meat@bread*(G/(G-1))
  for name,c,test in contrasts(spec):
   c=np.array(c);b=float(c@beta[:,j]);se=float(np.sqrt(max(c@vs['semana_HAC4']@c,0)));sem=float(np.sqrt(max(c@vs['mes_cluster']@c,0)))
   results.append(dict(ejecucion=label,FE=fe,modelo=spec,resultado=y,contraste=name,prueba_interaccion=test,n_horas=len(d),n_dias=d.fecha.nunique(),n_semanas=weeks.nunique(),n_meses=d.mes.nunique(),beta=b,se_semana_HAC4=se,lo95=b-1.95996398454*se,hi95=b+1.95996398454*se,se_mes_cluster=sem,p=2*norm.sf(abs(b/se)) if se>0 else np.nan,sd_MW_residual=float(X[:,0].std()),sd_MW_bruto=float(d.MW.std()),iteraciones_FE=it,error_medias_FE=err))
  for i,var in enumerate(x.columns):parameters.append(dict(ejecucion=label,FE=fe,modelo=spec,resultado=y,variable=var,beta=float(beta[i,j])))
 return results,parameters

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proyecto',type=Path,required=True);ap.add_argument('--ejecucion',default='20261011_horas_v1');a=ap.parse_args();project=a.proyecto.resolve();n=project/'Panel_datos/codex_panel_nacional';out=S/'resultados'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(S/'resultados').resolve():raise SystemExit('Carpeta nueva requerida')
 phy=S/'resultados/20261011_conciliacion_v2/fronteras_horarias.csv.gz';near=S/'resultados/20261011_controles_externos_v1/controles_seleccionados.csv';far=S/'resultados/20261011_controles_distantes_v1/controles_seleccionados.csv'
 fs=[n/f'data/hourly/REAL_{m.strftime("%Y%m")}.parquet' for m in pd.period_range('2024-08','2026-08',freq='M')]
 inputs=[phy,near,far,S/'PROTOCOLO_HORARIO_20261011.md',Path(__file__).resolve(),S/'scripts/conciliar_canteras_odata.py']+fs
 hs=[dict(referencia=('repositorio:'+str(p.relative_to(R))) if p.is_relative_to(R) else ('proyecto:'+str(p.relative_to(project))),sha256=sha(p),bytes=p.stat().st_size) for p in inputs];out.mkdir();pd.DataFrame(hs).to_csv(out/'insumos_sha256.csv',index=False)
 (out/'inicio.json').write_text(json.dumps(dict(fecha=datetime.now().isoformat(),commit_previo=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),protocolo_sha256=sha(inputs[3])),indent=2))
 nearbars=pd.read_csv(near).barra.tolist()[:5];farbars=pd.read_csv(far).barra.tolist();zone=['BATUCO_110','TLIBERTADORES_110','C.NAVIA_110'];bars=list(dict.fromkeys(zone+['CANTERAS_110','QUILLOTA_220']+nearbars+farbars));frames=[]
 for f in fs:
  q=pd.read_parquet(f,columns=['barra','fecha','hora0','cmg_usd_mwh'],filters=[('barra','in',bars)]);q['barra']=q.barra.astype(str);q['fecha']=q.fecha.astype(str);frames.append(q)
 q=pd.concat(frames);assert not q.duplicated(['barra','fecha','hora0']).any();wide=q.pivot(index=['fecha','hora0'],columns='barra',values='cmg_usd_mwh').reindex(columns=bars).dropna().reset_index()
 physical=pd.read_csv(phy);physical=physical[physical.frontera.eq('Canteras_HT12_D')].copy();physical['hora_utc']=pd.to_datetime(physical.hora_utc,utc=True);local=physical.hora_utc.dt.tz_convert('America/Santiago');physical['fecha']=local.dt.strftime('%Y-%m-%d');physical['hora0']=local.dt.hour
 physical=physical[physical.fecha.map(normal_day)].dropna(subset=['MWh']);assert not physical.duplicated(['fecha','hora0']).any()
 d=wide.merge(physical[['fecha','hora0','hora_utc','MWh']],on=['fecha','hora0'],validate='one_to_one').rename(columns={'MWh':'MW'})
 counts=d.groupby('fecha').hora0.agg(['size','nunique']);good=counts[(counts['size']==24)&counts['nunique'].eq(24)].index;d=d[d.fecha.isin(good)].sort_values(['fecha','hora0']).reset_index(drop=True)
 d['mes']=d.fecha.str[:7];d['hora_semana']=pd.to_datetime(d.fecha).dt.dayofweek*24+d.hora0;d['solar']=d.hora0.between(10,16).astype(int);d['tarde']=d.hora0.between(19,23).astype(int);d['bloque']=np.select([d.solar.eq(1),d.tarde.eq(1)],['solar_10_16','tarde_19_23'],default='resto');d['Q']=d.QUILLOTA_220;d['altoQ']=d.Q.ge(100).astype(int)
 d['zona']=d[zone].mean(axis=1);d['cerca']=d[nearbars].mean(axis=1);d['lejos5']=d[farbars[:5]].mean(axis=1);d['lejos7']=d[farbars].mean(axis=1)
 for name,v in [('zona_cerca',d.zona-d.cerca),('zona_lejos5',d.zona-d.lejos5),('zona_lejos7',d.zona-d.lejos7),('canteras_lejos5',d.CANTERAS_110-d.lejos5),('D_zona',d.zona-d.Q)]:d[name]=v
 thresholds=d.groupby('mes').MW.quantile(.75);d['umbral75']=d.mes.map(thresholds);d['carga_alta']=d.MW.gt(d.umbral75);d.to_csv(out/'panel_horario.csv.gz',index=False);thresholds.rename('umbral75_MW').to_csv(out/'umbrales_carga.csv')
 d.groupby('mes').agg(horas=('MW','size'),dias=('fecha','nunique'),MW=('MW','mean'),sd_MW=('MW','std'),horas_Qalto=('altoQ','sum'),horas_carga_alta=('carga_alta','sum')).to_csv(out/'cobertura_mensual.csv')
 summaries=d.groupby(['mes','bloque']).agg(horas=('MW','size'),MW=('MW','mean'),Q=('Q','mean'),zona_cerca=('zona_cerca','mean'),zona_lejos5=('zona_lejos5','mean'),zona_lejos7=('zona_lejos7','mean'),canteras_lejos5=('canteras_lejos5','mean'),D_zona=('D_zona','mean'));summaries.to_csv(out/'panel_mensual_bloques.csv')
 rows=[];params=[]
 for fe in ['A_mes_horasemana','B_dia_meshora_horasemana']:
  for spec in ['lineal','bloques','carga_alta','precio_alto']:
   result,p=estimate(d,fe,spec,'principal');rows+=result;params+=p
 r=pd.DataFrame(rows);r['p_Holm_interacciones']=np.nan
 for fe in r.FE.unique():
  ix=r.index[(r.FE==fe)&r.prueba_interaccion&r.resultado.ne('D_zona')];r.loc[ix,'p_Holm_interacciones']=multipletests(r.loc[ix,'p'],method='holm')[1]
 r.to_csv(out/'estimaciones_principales.csv',index=False);pd.DataFrame(params).to_csv(out/'parametros.csv',index=False)
 robust=[]
 for label,z in [('202408_202507',d[d.mes<='2025-07'].copy()),('202508_202608',d[d.mes>='2025-08'].copy())]:
  result,_=estimate(z,'B_dia_meshora_horasemana','bloques',label);robust+=result
 # Physical shifts move label, not values or selected price data; require complete days after joining.
 for delta in [-1,1]:
  ph=physical[['hora_utc','MWh']].copy();ll=(ph.hora_utc+pd.Timedelta(hours=delta)).dt.tz_convert('America/Santiago');ph['fecha']=ll.dt.strftime('%Y-%m-%d');ph['hora0']=ll.dt.hour;ph=ph[ph.fecha.map(normal_day)];ph=ph.drop_duplicates(['fecha','hora0'],keep=False)
  z=d.drop(columns='MW').merge(ph[['fecha','hora0','MWh']],on=['fecha','hora0'],validate='one_to_one').rename(columns={'MWh':'MW'});ct=z.groupby('fecha').size();z=z[z.fecha.isin(ct[ct.eq(24)].index)]
  result,_=estimate(z,'B_dia_meshora_horasemana','bloques',f'desfase_{delta:+}h');robust+=result
 pd.DataFrame(robust).to_csv(out/'robusteces_bloques.csv',index=False)
 # Public derivation that isolates aggregation: same-block monthly means, simple slopes, no causal label.
 agg=[]
 for block,m in summaries.reset_index().groupby('bloque'):
  for y in YCOL:
   x=m.MW-m.MW.mean();yy=m[y]-m[y].mean();agg.append(dict(bloque=block,resultado=y,n_meses=len(m),beta=float(x.dot(yy)/x.dot(x))))
 pd.DataFrame(agg).to_csv(out/'pendientes_mensuales_por_bloque.csv',index=False)
 check=[dict(referencia=h['referencia'],sin_cambios=sha(p)==h['sha256']) for p,h in zip(inputs,hs)];assert all(c['sin_cambios'] for c in check);pd.DataFrame(check).to_csv(out/'verificacion_insumos.csv',index=False)
 summary=dict(estado='OK',insumos_preservados=len(inputs),n_horas=len(d),n_dias=d.fecha.nunique(),n_meses=d.mes.nunique(),n_semanas=pd.to_datetime(d.fecha).dt.to_period('W-SUN').nunique(),originales_modificados=0,error_FE_max=float(r.error_medias_FE.max()))
 (out/'verificacion.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));print(r[(r.resultado=='zona_lejos5')][['FE','modelo','contraste','beta','lo95','hi95','p_Holm_interacciones','sd_MW_residual']].to_string(index=False))
if __name__=='__main__':main()
