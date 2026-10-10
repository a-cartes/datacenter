"""Registro de fuentes citadas en datos/instalaciones/instalaciones.csv (identificador -> URL,
archivo local, fecha de consulta y SHA-256). Las fuentes SEA, cartas y SNIFA se resuelven por
patrón. Salida: datos/instalaciones/fuentes_instalaciones.csv. Señala identificadores sin respaldo.
"""
import hashlib
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "fuentes" / "instalaciones" / "web"
URLS = {
    "GOOGLE_WEB": "https://datacenters.google/intl/es-419/locations/quilicura-chile/",
    "SONDA_2013": "https://www.sonda-mco.com/novedad/sonda-inaugura-data-center-de-clase-mundial",
    "SONDA_2022": "https://www.sonda.com/detalle-noticia/2022/10/05/datacenter-kudos-de-sonda-es-premiado-en-dcd-connect-cancun-2022",
    "UPTIME_2017": "https://journal.uptimeinstitute.com/entels-tier-certification-operational-sustainability/",
    "LATERCERA_2022": "https://www.latercera.com/piensa-digital/noticia/como-funciona-un-data-center/XPTNBHTWSZHX7FTQNBN23LYI4U/",
    "TELEFONICA_2016": "https://www.telefonica.com/en/communication-room/press-room/telefonica-presents-in-chile-one-of-the-most-modern-data-centers-in-latin-america-focused-on-reinforcing-its-offer-to-companies/",
    "EDGECONNEX_2021": "https://edgeconnex.com/company/news-and-pr/edgeconnex-announces-new-edge-data-center-in-santiago-chile-and-expanded-cloud-offerings-throughout-latam-with-oracle-fastconnect",
    "EDGECONNEX_DS2024": "https://www.edgeconnex.com/wp-content/uploads/2024/09/Santiago-Data-Sheet.pdf",
    "DEVTEL_2022": "https://www.developingtelecoms.com/telecom-technology/data-centres-networks/13872-ascenty-expands-its-latin-american-presence-with-second-data-centre-in-chile.html",
    "INVESTCHILE_2019": "https://blog.investchile.gob.cl/ascenty-confirms-construction-of-data-center-in-chile-with-investment-of-us70-million",
    "INVESTCHILE_2025": "https://blog.investchile.gob.cl/aws-invests-us4-billion",
    "TELETIME_2025": "https://teletime.com.br/28/08/2025/ascenty-inaugura-chile-data-center/",
    "PORTALINNOVA_2021": "https://portalinnova.cl/odata-llega-a-chile-con-inversion-de-us-217-millones-e-inicia-construccion-en-rm/",
    "DCR_2023": "https://datacentrereview.com/2023/11/odata-unveils-new-campus-in-chile-as-part-of-expansiopn/",
    "ALIGNED_2023": "https://www.globenewswire.com/news-release/2023/11/07/2774866/0/es/ODATA-fortalece-su-presencia-en-Chile-con-nuevo-Data-Center-de-40-MW-de-capacidad-y-ampliaci%C3%B3n-de-su-primera-unidad.html",
    "MICROSOFT_2025": "https://news.microsoft.com/source/latam/company-news-es/microsoft-inaugura-su-primera-region-de-datacenters-en-chile-para-acelerar-la-innovacion-y-el-desarrollo-economico-local/",
    "ENTEL_MEM2010": "https://entel.cdn.modyo.com/uploads/883c449b-8664-4fc3-88b9-b4f469ae0cb2/original/memoria_anual_entel_2010_1719725519716.pdf",
    "ENTEL_2020": "https://informacioncorporativa.entel.cl/press-releases/entel-datacenter-is-among-six-service-providers-in-the-world-certified-tier-iv-gold-in-sustainable-operation",
    "CARTA_DE05310-24": "https://cartas.coordinador.cl/show/66e839f83563570d9edc52dc",
    "EQUINIX_2022": "https://www.sec.gov/Archives/edgar/data/1101239/000156459022011057/d330434dex991.htm",
}
LOCAL = {"INFLECT_2026": "fuentes/instalaciones/directorios/inflect/santiago.html",
         "DCATLAS_2026": "fuentes/instalaciones/directorios/dcatlas/_pais_chile.html",
         "SNIFA_2026": "fuentes/instalaciones/snifa/rca_data_center.html",
         "CARTAS_EDGECONNEX": "fuentes/instalaciones/cartas/"}
for y, ts in {"2011": "20110724045531", "2016": "20160705092459", "2022": "20220928072151",
              "2023": "20231202094652", "2024": "20240712214317"}.items():
    LOCAL[f"DCM_{y}"] = f"fuentes/instalaciones/directorios/datacentermap_wayback/santiago_{ts}.html"
    URLS[f"DCM_{y}"] = f"http://web.archive.org/web/{ts}/http://www.datacentermap.com/chile/santiago/"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ""


def main():
    reg = pd.read_csv(W / "registro.csv")
    reg = reg[reg.archivo.notna() & (reg.archivo != "")].drop_duplicates("url", keep="last")
    I = pd.read_csv(ROOT / "datos" / "instalaciones" / "instalaciones.csv", dtype=str)
    ids = sorted({x.strip() for s in I.fuentes.fillna("") for x in s.split(";") if x.strip()})
    S = pd.read_csv(ROOT / "datos" / "instalaciones" / "sea_expedientes.csv", dtype=str)
    C = pd.read_csv(ROOT / "datos" / "instalaciones" / "cartas_coordinador.csv", dtype=str)
    rows = []
    for i in ids:
        url = URLS.get(i, "")
        loc = LOCAL.get(i, "")
        if i.startswith("SEA_"):
            e = i[4:]
            r = S[S.EXPEDIENTE_ID == e]
            url = f"https://seia.sea.gob.cl/expediente/expediente.php?id_expediente={e}"
            loc = f"fuentes/instalaciones/sea/fichas/{e}_ficha.html"
        elif i.startswith("CARTA_") and i not in URLS:
            c = C[C.correlativo == i[6:]]
            url = c.url.iloc[0] if len(c) else ""
            loc = "fuentes/instalaciones/cartas/ (página de resultados)"
        http = ""
        if url and not loc:
            r = reg[reg.url == url]
            loc = f"fuentes/instalaciones/web/{r.archivo.iloc[0]}" if len(r) else ""
            http = str(r.http.iloc[0]) if len(r) else ""
        p = ROOT / loc.split(" ")[0] if loc else None
        ok = bool(p and p.exists()) and http in ("", "200", "200.0")
        rows.append({"fuente_id": i, "url": url, "archivo_local": loc, "http": http,
                     "sha256": sha(p) if p else "", "archivado": ok})
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "datos" / "instalaciones" / "fuentes_instalaciones.csv", index=False)
    print(out[~out.archivado][["fuente_id", "url"]].to_string())
    print(len(out), "fuentes;", int(out.archivado.sum()), "archivadas localmente")


if __name__ == "__main__":
    main()
