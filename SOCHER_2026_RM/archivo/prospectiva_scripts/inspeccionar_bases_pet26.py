"""Lee PET26 sin ejecutar PLP/PF y extrae insumos y resultados base de 2030.

Los precios son resultados oficiales del escenario original; NO son efectos de
centros de datos. Las carpetas E01/E02/E03 conservan su nombre, sin asignarles
etiquetas de demanda baja/media/alta que no se hayan verificado.
"""
from pathlib import Path
import csv
import io
import json
import re
import tarfile
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'fuentes/originales/pet26/CEN_PET26_BD_PLP'
INPUT = BASE / 'IPLP-PET26/IPLP-PET26'
OUT = ROOT / 'extraidos/pet26'
OUT.mkdir(parents=True, exist_ok=True)


def dat(path):
    with path.open(encoding='latin1') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                yield line


def write_csv(name, rows):
    if not rows:
        return
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    inspection = []
    calendar = {}
    demand = {}
    buses_all, blocks_all, demand_all = [], [], []
    for p in sorted(INPUT.iterdir()):
        if not p.is_dir():
            continue
        scenario = p.name
        counts, months = Counter(), defaultdict(set)
        with (p / 'indhor.csv').open(encoding='latin1') as f:
            rows = csv.reader(f)
            next(rows)
            for year, month, day, hour, block in rows:
                b = int(block)
                counts[b] += 1
                months[b].add((int(year), int(month)))
        assert all(len(v) == 1 for v in months.values())
        cal = {}
        lines = iter(dat(p / 'plpblo.dat'))
        n_blocks = int(next(lines))
        for line in lines:
            parts = line.split()
            block, stage, hours = map(int, parts[:3])
            year, month = next(iter(months[block]))
            assert counts[block] == hours, (scenario, block, hours, counts[block])
            cal[block] = (year, month, hours)
            blocks_all.append(dict(escenario=scenario, bloque=block, etapa=stage,
                                   anio=year, mes=month, horas=hours))
        assert len(cal) == n_blocks
        assert sum(h for y, m, h in cal.values() if y == 2030) == 8760
        calendar[scenario] = cal
        lines = iter(dat(p / 'plpbar.dat'))
        n_buses = int(next(lines))
        buses = {}
        for line in lines:
            m = re.fullmatch(r"(\d+)\s+'([^']+)'", line)
            assert m, line
            buses[int(m[1])] = m[2]
            buses_all.append(dict(escenario=scenario, numero=int(m[1]), barra=m[2]))
        assert len(buses) == n_buses
        lines = iter(dat(p / 'plpdem.dat'))
        n_demand = int(next(lines))
        dem = {}
        names = []
        for _ in range(n_demand):
            name = next(lines).strip("'")
            names.append(name)
            assert name in buses.values(), name
            n = int(next(lines))
            seen = set()
            for _ in range(n):
                month_model, block, val = next(lines).split()
                block, val = int(block), float(val)
                assert block not in seen
                seen.add(block)
                year, month, hours = cal[block]
                if year == 2030:
                    dem[(name, block)] = val
                    demand_all.append(dict(escenario=scenario, barra=name, bloque=block,
                                           anio=year, mes=month, horas=hours,
                                           demanda_MW=val, energia_MWh=val*hours))
            assert len(seen) == n_blocks
        assert next(lines, None) is None
        demand[scenario] = dem
        central_counts = list(map(int, next(dat(p / 'plpcnfce.dat')).split()))
        lines_count = int(next(dat(p / 'plpcnfli.dat')).split()[0])
        hydro_counts = list(map(int, next(dat(p / 'plpaflce.dat')).split()))
        terms = ['chacabuco', 'puntaverde', 'huechuraba', 'enea', 'ascenty',
                 'microsoft', 'google', 'scala', 'odata', 'edgeconnex']
        inspection.append(dict(escenario=scenario, barras=n_buses, barras_con_demanda=n_demand,
                               registros_configuracion_central=central_counts[0],
                               embalses=central_counts[1], baterias=central_counts[5],
                               lineas=lines_count, series_afluentes=hydro_counts[0],
                               hidrologias_declaradas=hydro_counts[1], bloques=n_blocks,
                               inicio=min(v[:2] for v in cal.values()), fin=max(v[:2] for v in cal.values()),
                               bloques_2030=sum(y == 2030 for y, m, h in cal.values()),
                               demanda_total_2030_TWh=sum(v*cal[b][2] for (name,b),v in dem.items())/1e6,
                               coincidencias_nombres_digitales={t:[n for n in buses.values() if t in n.lower()] for t in terms}))
    write_csv('barras_PLP.csv', buses_all)
    write_csv('calendario_bloques_PLP.csv', blocks_all)
    write_csv('demanda_2030_PLP.csv', demand_all)

    # Leer el TAR en secuencia: exportar solo 2030 sin expandir 10,6 GB de salidas.
    inventories, official = [], []
    errors = defaultdict(float)
    checked = Counter()
    metadata = {'costosop.csv', 'etapas.csv', 'lineas.csv', 'series.csv',
                'centrales.csv', 'barras.csv', 'presuf.csv', 'simuls.csv', 'embalses.csv'}
    with tarfile.open(BASE / 'OPLP-PET26.tar.gz', 'r|gz') as archive:
        for member in archive:
            if not member.isfile():
                continue
            path = Path(member.name)
            scenario = path.parts[0]
            selected = path.name in metadata or path.name == 'plpbar_media.csv'
            inventories.append(dict(ruta=member.name, bytes=member.size,
                                    tratamiento='extraido' if path.name in metadata else
                                    'filtrado_2030' if selected else 'conservado_en_tar'))
            if path.name in metadata:
                dest = OUT / 'resultados_oficiales' / path
                assert dest.resolve().is_relative_to(OUT.resolve())
                dest.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as f:
                    dest.write_bytes(f.read())
            elif path.name == 'plpbar_media.csv':
                with archive.extractfile(member) as f:
                    for r in csv.DictReader(line.decode('latin1') for line in f):
                        block = int(r['Bloque'])
                        year, month, hours = calendar[scenario][block]
                        if year != 2030:
                            continue
                        name = r['BarNom'].strip()
                        mw = float(r['DemBarP'])
                        err = abs(mw - demand[scenario].get((name, block), 0))
                        errors[scenario] = max(errors[scenario], err)
                        checked[scenario] += 1
                        official.append(dict(escenario=scenario, barra=name,
                                             bloque=block, anio=year, mes=month, horas=hours,
                                             CMgBar=float(r['CMgBar']), DemBarP=mw,
                                             DemBarE=float(r['DemBarE']),
                                             tipo='resultado_oficial_original_no_contrafactual'))
    write_csv('inventario_resultados_PLP.csv', inventories)
    write_csv('precios_demanda_oficiales_2030_PLP.csv', official)
    comparison = {s:dict(filas_2030=checked[s], max_diferencia_demanda_MW=errors[s]) for s in calendar}
    # No imponer conciliación exacta: si hay diferencias, se conservan y reportan.
    report = dict(estado='ZIP importados; entradas PLP y resultados base de 2030 leídos',
                  escenarios=inspection, conciliacion_entrada_salida=comparison,
                  alcance='Demanda por barra agregada; no identifica por sí sola consumo de cada centro de datos.',
                  resolucion='Diez bloques representativos por mes, con correspondencia de horas a bloques. No equivale a un despacho cronológico horario.',
                  powerfactory='Seis proyectos PFD binarios; no se ejecutaron ni se convirtieron.',
                  ejecutables='No se encontraron ejecutables PLP ni manuales en los inventarios ZIP.',
                  resultado_economico='Los costos marginales extraídos son del escenario oficial original; todavía no se simuló el cambio de demanda digital.',
                  siguiente='Determinar escenarios, agregación de nodos y carga digital incluida; implementar o disponer de motor de despacho y contrastarlo con las salidas oficiales antes del contrafactual.')
    (OUT / 'estado_ingesta.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
