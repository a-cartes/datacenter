"""Cotejo independiente del CSV final con extractos y de agregaciones publicadas."""
from pathlib import Path
import hashlib,json
import pandas as pd

OUT=Path(__file__).resolve().parents[1]
raw=['archivo_original','miembro_zip','fila_csv_original','ID_SOC','IDSOCKET','SUBESTACION','TENSION','YEARX','MONX','DAYX','HOURX','DATETIME','UTCDATETIME','kWhD','kWhR','FLUJO','ULTIMA_LECTURA']
parts=[]
for mfile in sorted((OUT/'extractos').glob('*_manifest.json')):
    m=json.loads(mfile.read_text());p=OUT/m['extracto']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256_extracto']
    parts.append(pd.read_csv(p,dtype=str,keep_default_na=False))
a=pd.concat(parts,ignore_index=True).sort_values('UTCDATETIME').reset_index(drop=True)
d=pd.read_csv(OUT/'et7_15min.csv.gz',dtype=str,keep_default_na=False).sort_values('UTCDATETIME').reset_index(drop=True)
assert a[raw].equals(d[raw])
assert len(d)==90532
assert not d.duplicated(['IDSOCKET','UTCDATETIME']).any()
daily=pd.read_csv(OUT/'et7_cobertura_diaria.csv')
monthly=pd.read_csv(OUT/'et7_cobertura_mensual.csv')
assert daily.registros.sum()==monthly.registros.sum()==len(d)
assert daily.ausente.sum()==31
assert daily.loc[daily.ausente,'fecha_etiqueta_local'].str.startswith('2025-03').all()
assert daily.loc[daily.ausente,['energia_D_kwh','energia_R_kwh','media_D_mw','media_R_mw']].isna().all().all()
assert (daily.dia_completo|daily.ausente).all()
for c in ['D','R']:
    raw_energy=pd.to_numeric(a[f'kWh{c}'].str.replace(',','.',regex=False))
    assert (raw_energy-pd.to_numeric(d[f'energia_{c}_kwh'])).abs().max()<1e-9
    assert abs(raw_energy.sum()-daily[f'energia_{c}_kwh'].sum())<1e-4
    assert abs(raw_energy.sum()-monthly[f'energia_{c}_kwh'].sum())<1e-4
report={'filas_verificadas':len(d),'extractos_verificados':len(parts),'campos_literales_identicos':True,
        'dias_completos':int(daily.dia_completo.sum()),'dias_ausentes':int(daily.ausente.sum()),
        'meses_completos':int(monthly.cobertura.eq(1).sum()),'ausencias_sin_imputacion':True,
        'totales_diarios_y_mensuales_conciliados':True,'tolerancia_energia_kwh':0.0001,
        'sha256_tabla':hashlib.sha256((OUT/'et7_15min.csv.gz').read_bytes()).hexdigest(),
        'coincide_sha_primera_ejecucion':hashlib.sha256((OUT/'et7_15min.csv.gz').read_bytes()).hexdigest()=='95ccaed47257e314edaa86705abc93ded4c689c517eb20240fa916be5a4ca3c3'}
(OUT/'verificacion_tabular.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
