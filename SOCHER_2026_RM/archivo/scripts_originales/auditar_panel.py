"""Auditoría de agregaciones, muestra y una muestra cruda; no cambia la réplica."""
import json
import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resultados/auditoria_20261002"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))
from comun import canon
from extraer_precios_historicos import open_book, selected

A = pd.read_parquet(ROOT / "datos/panel/barra_anio.parquet")
M = pd.read_parquet(ROOT / "datos/panel/barra_mes.parquet")
S = pd.read_csv(ROOT / "datos/analitico/muestra_distrito.csv")
U = S.drop_duplicates(["unidad", "anio"])
B = pd.read_csv(ROOT / "datos/geo/barras_diccionario.csv").merge(
    pd.read_csv(ROOT / "datos/geo/subestaciones_unidades.csv")[["id_subestacion", "distrito_nombre"]],
    on="id_subestacion", how="left", validate="many_to_one")
assert not A.duplicated(["barra", "anio"]).any()
assert not B.barra.duplicated().any()
assert not S.duplicated(["unidad_copia", "anio"]).any()
assert np.allclose(S.groupby(["unidad", "anio"]).peso.sum(), 1)

# Reconstrucción de barra-año desde sumas mensuales, sin llamar al constructor.
ann = M.assign(anio=M.mes // 100).groupby(["barra", "anio"])[["sum_D", "horas_D"]].sum()
ann["D_reconstruido"] = ann.sum_D / ann.horas_D.replace(0, np.nan)
cmp = A.merge(ann[["D_reconstruido"]], on=["barra", "anio"], validate="one_to_one")
err_annual = float((cmp.D - cmp.D_reconstruido).abs().max())
assert err_annual < 1e-9

# Reconstrucción de distrito-año desde barras y geografía, usando el criterio declarado.
ok = A[A.cobertura_D >= .9].groupby("barra").anio.nunique()
bal = A[A.barra.isin(ok[ok == 9].index)].merge(B[["barra", "distrito_nombre"]], on="barra", validate="many_to_one")
district = bal.groupby(["distrito_nombre", "anio"]).D.mean().rename("D_reconstruido").reset_index()
c = U.merge(district, left_on=["unidad", "anio"], right_on=["distrito_nombre", "anio"], validate="one_to_one")
assert len(c) == len(U)
err_district = float((c.D-c.D_reconstruido).abs().max())
assert err_district < 1e-9

# Reconstruir directamente cinco meses desde los precios horarios extraídos.
monthly = []
for sub, month, reg in [("precios_hist",201701,"historico"),("precios_hist",202212,"historico"),
                         ("precios_hist",202407,"historico"),("precios_mod",202407,"moderno"),
                         ("precios_mod",202512,"moderno")]:
    x = pd.read_parquet(ROOT/f"datos/{sub}/{month}.parquet", columns=["barra","dia","hora","P"])
    x["barra"] = x.barra.map(canon)
    assert not x.duplicated(["barra","dia","hora"]).any()
    q = x[x.barra=="QUILLOTA______220"][["dia","hora","P"]].rename(columns={"P":"E"})
    z = x.merge(q,on=["dia","hora"],how="left",validate="many_to_one")
    z["D"] = z.P-z.E
    means = z.groupby("barra").D.mean().rename("reconstruido")
    target = M[(M.mes==month)&(M.regimen==reg)].set_index("barra")
    target["guardado"] = target.sum_D/target.horas_D.replace(0,np.nan)
    comp = target.join(means)
    err = float((comp.guardado-comp.reconstruido).abs().max())
    assert err < 1e-9
    monthly.append({"mes":month,"regimen":reg,"barras":len(comp),"error_max":err})

# Muestra cruda histórica: 24 horas del 15/01/2017, cuatro barras.
# open_book solo abre el contenedor; lectura de celdas independiente del extractor.
targets = ["QUILLOTA______220","BATUCO________110","LAMPA_________220","C.CHENA_______220"]
sel = selected()
row = next(r for r in sel if int(r["mes"])==201701)
name, data = open_book(row["archivo_proyecto"])
wb = openpyxl.load_workbook(BytesIO(data),read_only=True,data_only=True,keep_links=False)
ws = wb["CMG Barras dolares"]; ws.reset_dimensions()
recs = []; cols = {}
for n, values in enumerate(ws.iter_rows(values_only=True),start=1):
    if n==9:
        cols = {j:canon(v) for j,v in enumerate(values) if v is not None and canon(v) in targets}
    if n <= 10 or not values or values[0] is None: continue
    if values[1] == 15:
        for j, code in cols.items(): recs.append({"barra":code,"dia":15,"hora":int(values[2]),"original":values[j]})
    if isinstance(values[1], (int,float)) and values[1]>15: break
wb.close()
raw = pd.DataFrame(recs)
x = pd.read_parquet(ROOT/"datos/precios_hist/201701.parquet",columns=["barra","dia","hora","P"])
x["barra"] = x.barra.map(canon)
c = raw.merge(x,on=["barra","dia","hora"],validate="one_to_one")
assert len(c)==96
raw_err = float((c.original-c.P).abs().max())
assert raw_err < 1e-9

# Inventario efectivo de barras de los tres distritos y distancia al sitio (no prueba conexión).
I = pd.read_csv(ROOT/"datos/instalaciones/instalaciones_geo.csv")
geo = []
for ident in ["EDGE_SCL01","ODATA_ST01","ODATA_ST02"]:
    site = I[I.id==ident].iloc[0]
    b = B[(B.distrito_nombre==site.distrito_nombre)&B.barra.isin(ok[ok==9].index)].copy()
    b["dist_km"] = np.sqrt(((b.lon-site.lon)*111.32*np.cos(np.radians(site.lat)))**2+((b.lat-site.lat)*110.57)**2)
    b["instalacion"] = ident
    geo.extend(b[["instalacion","distrito_nombre","barra","subestacion","dist_km","metodo"]].to_dict("records"))
pd.DataFrame(geo).to_csv(OUT/"barras_efectivamente_tratadas.csv",index=False)

# La equivalencia P/D no es exacta en todas las variantes con distinta cobertura temporal.
equiv = []
for f in sorted((ROOT/"resultados/estimaciones").glob("*.json")):
    d=json.loads(f.read_text())
    if "P" in d and "D" in d:
        equiv.append({"archivo":f.name,"diferencia_ATT_P_menos_D":d["P"]["sun_abraham"]["att"]-d["D"]["sun_abraham"]["att"]})

result={"claves_duplicadas":0,"pesos_totales_por_unidad_anio":1,
        "error_max_barra_anio":err_annual,"error_max_distrito_anio":err_district,
        "reconstrucciones_mensuales":monthly,
        "muestra_original_201701":{"filas":len(c),"error_max":raw_err,"libro":name},
        "barras_tratadas":geo,"equivalencia_P_D_por_variante":equiv,
        "limites":"No reextrae todos los originales; no prueba geolocalización ni primer consumo eléctrico."}
(OUT/"auditoria_panel.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
