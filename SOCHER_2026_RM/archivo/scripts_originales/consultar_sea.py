"""Consulta sistemática del buscador público del SEA (e-SEIA) para proyectos de centros de datos.

Usa el mismo servicio que la página https://seia.sea.gob.cl/busqueda/buscarProyecto.php
(endpoint /busqueda/buscarProyectoResumenAction.php). Busca por nombre de proyecto y por
titular, en todas las regiones, y conserva cada respuesta original en
fuentes/instalaciones/sea/consultas/. Consolida expedientes únicos en
datos/instalaciones/sea_expedientes.csv con el término que los encontró.
La aparición en el SEA no acredita construcción ni operación: un proyecto puede no
ingresar, desistir, ser rechazado o no construirse. Un centro puede no requerir SEA.

Uso: python scripts/consultar_sea.py
"""
import json
from pathlib import Path
import time

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "fuentes" / "instalaciones" / "sea" / "consultas"
URL = "https://seia.sea.gob.cl/busqueda/buscarProyectoResumenAction.php"
NOMBRES = ["data center", "datacenter", "data centre", "centro de datos", "centro datos", "centros de datos",
           "datos", "nube", "cloud", "hyperscale", "colocation", "SCL0", "SCL1", "servidores", "TI campus",
           "campus tecnológico", "edificio tecnológico", "procesamiento de datos"]
TITULARES = ["Google", "Microsoft", "Amazon", "AWS", "Equinix", "Entel", "Sonda", "Ascenty", "Digital Realty",
             "EdgeConneX", "Edgeconnex", "ODATA", "Aligned", "Scala", "Cirion", "Level 3", "Lumen", "Claro",
             "Telefónica", "Movistar", "GTD", "Telmex", "TIVIT", "Huawei", "Oracle", "IBM", "Kyndryl",
             "Hewlett", "Param", "NextStream", "Nabiax", "Actis", "EdgeUno", "Ufinet", "Elea", "Patria",
             "CloudHQ", "Cloud HQ", "Rackspace", "Mercado Libre", "Falabella", "Cencosud", "Banco",
             "Data Center", "Datacenter", "Data Centers", "Centro de Datos", "TECfusions", "Novva", "Templus",
             "Tikal", "Megadatos", "Imperial Data", "Pacific", "Gramercy", "Prime Data", "Kio"]
BASE = {k: "" for k in ["nombre", "titular", "folio", "selectRegion", "selectComuna", "tipoPresentacion",
                        "projectStatus", "PresentacionMin", "PresentacionMax", "CalificaMin", "CalificaMax",
                        "sectores_economicos", "razoningreso", "id_tipoexpediente"]}


def query(field, term):
    out, offset = [], 1
    while True:
        data = {**BASE, field: term, "offset": offset, "limit": 100}
        for k in range(4):
            try:
                r = requests.post(URL, data=data, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
                break
            except requests.RequestException:
                time.sleep(3 * (k + 1))
        txt = r.content.decode("latin-1")
        safe = f"{field}_{term}".replace(" ", "_").replace("/", "_")
        (RAW / f"{safe}_p{offset}.json").write_text(txt, encoding="utf-8")
        d = json.loads(txt)
        rows = d.get("data") or []
        out += rows
        total = int(d.get("recordsFiltered") or 0)
        if offset * 100 >= total or not rows:
            return out, total
        offset += 1
        time.sleep(1)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    recs, log = [], []
    for field, terms in [("nombre", NOMBRES), ("titular", TITULARES)]:
        for t in terms:
            rows, total = query(field, t)
            log.append({"campo": field, "termino": t, "resultados": total})
            for r in rows:
                r = {k: v for k, v in r.items() if k not in ("ACCIONES", "LINK_MAPA")}
                r.update({"campo_busqueda": field, "termino": t})
                recs.append(r)
            time.sleep(1)
    df = pd.DataFrame(recs)
    agg = (df.groupby("EXPEDIENTE_ID")
             .agg({**{c: "first" for c in df.columns if c not in ("EXPEDIENTE_ID", "campo_busqueda", "termino")},
                   "termino": lambda s: "; ".join(sorted(set(s)))})
             .reset_index())
    out = ROOT / "datos" / "instalaciones"
    out.mkdir(parents=True, exist_ok=True)
    agg.to_csv(out / "sea_resultados_brutos.csv", index=False)
    pd.DataFrame(log).to_csv(RAW.parent / "registro_consultas.csv", index=False)
    print(pd.DataFrame(log).to_string())
    print(len(agg), "expedientes únicos")


if __name__ == "__main__":
    main()
