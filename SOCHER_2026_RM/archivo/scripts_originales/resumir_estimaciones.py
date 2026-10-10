"""Tabla resumen de todas las estimaciones (resultados/estimaciones/*.json) -> resultados/resumen_estimaciones.csv"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
rows = []
for f in sorted((ROOT / "resultados" / "estimaciones").glob("*.json")):
    d = json.loads(f.read_text())
    for y in ["D", "L", "C"]:
        if y not in d:
            continue
        r = d[y]
        sa = r.get("sun_abraham", {})
        rows.append({"alternativa": d["alternativa"], "regla_G": d["regla_G"], "resultado": y,
                     "tratadas": d["n_tratadas"], "cohortes": json.dumps(d["cohortes"]), "controles_unicos": d["controles_unicos"],
                     "TWFE": r["twfe"]["coef"], "TWFE_ee_cluster": r["twfe"]["se"],
                     "SunAbraham": sa.get("att"), "SA_ee_cluster": sa.get("se"),
                     "CallawaySantAnna": r["callaway_santanna"]["att_simple"],
                     "TWFE_sin_emparejar": r["twfe_sin_emparejar"]["coef"],
                     "p_aleatorizacion_TWFE": d["aleatorizacion_D"]["p_twfe"] if y == "D" else None,
                     "p_aleatorizacion_CS": d["aleatorizacion_D"]["p_cs"] if y == "D" else None,
                     "media_controles_2017_2018": r["media_controles_2017_2018"]})
T = pd.DataFrame(rows)
T.to_csv(ROOT / "resultados" / "resumen_estimaciones.csv", index=False)
print(T[T.resultado == "D"].round(3).to_string())
