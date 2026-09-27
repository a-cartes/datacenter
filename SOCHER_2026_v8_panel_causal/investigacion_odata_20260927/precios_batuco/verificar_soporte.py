#!/usr/bin/env python3
"""Disponibilidad de etiquetas Batuco, sin examinar magnitudes de precios.

Lee OOXML archivado; no ejecuta macros ni cambia la base congelada. Registra
presencia y soporte de abril-octubre de 2022. No decide fecha ni barra causal.
"""
from pathlib import Path
import argparse, concurrent.futures, datetime as dt, hashlib, json, csv
import zipfile, xml.etree.ElementTree as ET

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
LABELS={'BATUCO________013','BATUCO________110','QUILLOTA______110','QUILLOTA______220'}

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def col(address):
    n=0
    for c in address:
        if not c.isalpha():break
        n=n*26+ord(c)-64
    return n

def process(p):
    days={}; first={}; names=[]
    with zipfile.ZipFile(p) as z:
        strings=[]
        with z.open('xl/sharedStrings.xml') as f:
            for _,e in ET.iterparse(f,events=('end',)):
                if e.tag.endswith('}si'):
                    strings.append(''.join(t.text or '' for t in e.findall('.//m:t',NS)));e.clear()
        names=sorted({s for s in strings if s in LABELS or ('QUILLOTA' in s and '->' not in s)})
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rid=next(s.attrib['{'+REL+'}id'] for s in wb.findall('.//m:sheet',NS) if s.attrib['name']=='CMG Barras')
        target=next(r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')) if r.attrib['Id']==rid)
        target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        blocks=[]
        with z.open(target) as f:
            for _,e in ET.iterparse(f,events=('end',)):
                if not e.tag.endswith('}row'):continue
                row={}
                for c in e:
                    v=c.find('m:v',NS)
                    if v is not None and v.text is not None:
                        row[col(c.attrib['r'])]=strings[int(v.text)] if c.attrib.get('t')=='s' else v.text
                if not blocks:
                    blocks=[c for c,v in row.items() if v=='Barra']
                    if blocks:assert all('mills/kWh' in row.get(c+1,'') for c in blocks)
                else:
                    for c in blocks:
                        name=row.get(c,'').strip()
                        if name not in LABELS:continue
                        ym=int(float(row[c-3]));day=int(float(row[c-2]));hour=int(float(row[c-1]))
                        date=dt.date(ym//100,ym%100,day).isoformat()
                        assert p.parent.name==str(ym) and 1<=hour<=25
                        key=(name,date)
                        rec=days.setdefault(key,{'horas':set(),'faltantes':0})
                        assert hour not in rec['horas'],(p,key,hour)
                        if c+1 not in row:rec['faltantes']+=1
                        else:rec['horas'].add(hour)
                        first.setdefault(name,{'fila':int(e.attrib['r']),'columna_etiqueta':c})
                e.clear()
    records=[{'mes':p.parent.name,'barra_cmg':name,'fecha':date,'n_etiquetas_con_valor':len(d['horas']),
              'etiquetas':'|'.join(map(str,sorted(d['horas']))),'faltantes_explicitos':d['faltantes']}
             for (name,date),d in sorted(days.items())]
    return records,{'mes':p.parent.name,'archivo':p.name,'sha256':sha(p),'etiquetas_en_diccionario':names,
                    'primeras_filas':first,'homologacion_mensual_disponible':False,
                    'magnitudes_precios_analizadas':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--datos-raiz',type=Path,required=True);a=ap.parse_args()
    here=Path(__file__).resolve().parent
    books=[a.datos_raiz/'SOCHER_2026_v7_2020_2026/historico/libros'/f'2022{m:02d}'/f'cmg22{m:02d}_def.xlsm' for m in range(4,11)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:results=list(pool.map(process,books))
    rows=[r for d,_ in results for r in d]
    with (here/'soporte_diario_etiquetas.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    g=dt.date(2022,8,2); pre=(g-dt.timedelta(days=112),g-dt.timedelta(days=8));post=(g,g+dt.timedelta(days=89))
    counts={}
    for label in sorted(LABELS):
        selected=[r for r in rows if r['barra_cmg']==label]
        counts[label]={phase:sum(lo.isoformat()<=r['fecha']<=hi.isoformat() and r['n_etiquetas_con_valor']==24 and r['faltantes_explicitos']==0 for r in selected) for phase,(lo,hi) in [('pre',pre),('post',post)]}
    report={'estado':'COBERTURA_SIN_IDENTIFICACION_CAUSAL','fecha_operacional_candidata':'2022-08-01',
            'g_convencion_condicional':g.isoformat(),'ventanas':{'pre':[x.isoformat() for x in pre],'post':[x.isoformat() for x in post]},
            'conteos_dias_24_etiquetas_por_barra_no_pares':counts,'filas_soporte':len(rows),
            'libros':[x for _,x in results],'sha256_soporte':sha(here/'soporte_diario_etiquetas.csv'),
            'sha256_script':sha(Path(__file__)),'nota':'No asigna códigos actuales a 2022 ni certifica empalme del campus. No calcula medias, diferenciales ni efectos.'}
    (here/'verificacion_soporte.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['estado','conteos_dias_24_etiquetas_por_barra_no_pares','filas_soporte']},ensure_ascii=False))

if __name__=='__main__':main()
