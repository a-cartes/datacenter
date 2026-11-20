"""Reconstruye el primer día de los 366 PRG públicos, con su versión y SHA-256."""
import argparse
import csv
import hashlib
import io
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import openpyxl


def extraer(dia, cache):
    # Versiones publicadas que contienen el PRG de la fecha.
    sufijo = "-1" if dia.isoformat() in {"2024-02-24", "2024-06-12", "2024-08-29"} else ""
    nombre = f"PROGRAMA{dia:%Y%m%d}{sufijo}.zip"
    url = f"https://www.coordinador.cl/wp-content/uploads/{dia-timedelta(days=1):%Y/%m}/{nombre}"
    archivo = cache / nombre
    if archivo.exists():
        contenido = archivo.read_bytes()
    else:
        with urlopen(url, timeout=60) as respuesta:
            contenido = respuesta.read()
    with ZipFile(io.BytesIO(contenido)) as paquete:
        esperado = f"PRG{dia:%y%m%d}.XLSX"
        candidatos = [n for n in paquete.namelist() if Path(n).name.upper() == esperado]
        if len(candidatos) != 1:
            raise ValueError(f"{dia}: PRG de la fecha ambiguo o ausente: {candidatos}")
        miembro = candidatos[0]
        libro = openpyxl.load_workbook(io.BytesIO(paquete.read(miembro)), read_only=True, data_only=True)
    try:
        periodos = None
        for fila in libro["PROGRAMA"].values:
            if isinstance(fila[2], datetime):
                if fila[2].date() != dia:
                    raise ValueError(f"{dia}: fecha interna {fila[2]}")
                ancho = 25 if dia == date(2024, 4, 6) else 24
                periodos = list(fila[4:4 + ancho])
                if periodos != list(range(1, ancho + 1)):
                    raise ValueError(f"{dia}: periodos inesperados {periodos}")
            if fila[2] == "Costos Totales [kUSD]" and periodos:
                valores = list(fila[4:4 + len(periodos)])
                if dia == date(2024, 9, 8):
                    if valores.pop(0) is not None:
                        raise ValueError(f"{dia}: primer periodo distinto de vacío")
                costo = sum(valores)
                declarado = float(fila[4 + len(periodos)])
                if abs(costo - declarado) >= 0.05:
                    raise ValueError(f"{dia}: suma incompatible con el total diario")
                break
        else:
            raise ValueError(f"{dia}: faltan fecha o costos totales")
    finally:
        libro.close()
    if not archivo.exists():
        archivo.write_bytes(contenido)
    return dia, len(valores), costo, url, hashlib.sha256(contenido).hexdigest(), miembro


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache", type=Path)
    parser.add_argument("--salida", type=Path, default=Path("censo_prg.csv"))
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    fechas = [date(2024, 1, 1) + timedelta(days=i) for i in range(366)]
    with ThreadPoolExecutor(5) as pool:
        filas = list(pool.map(lambda dia: extraer(dia, args.cache), fechas))
    if sum(f[1] for f in filas) != 8784:
        raise ValueError("Cobertura horaria inesperada")
    with args.salida.open("w", newline="") as archivo:
        salida = csv.writer(archivo, lineterminator="\n")
        salida.writerow(["fecha", "horas", "kUSD_dia", "url", "sha256", "planilla"])
        salida.writerows(filas)


if __name__ == "__main__":
    main()
