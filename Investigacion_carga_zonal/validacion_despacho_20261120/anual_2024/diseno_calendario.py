"""Compara dos diseños de 96 días sobre el censo finito de costos programados de 2024."""
from calendar import monthrange
from collections import defaultdict
from datetime import date
from pathlib import Path
from random import Random
from statistics import variance
import csv
import math

CARPETA = Path(__file__).resolve().parent
# Calendario 2024 publicado por el Gobierno de Chile. Los domingos ya caen
# en la tercera categoría, incluidas las elecciones que se celebraron en domingo.
FESTIVOS = set("01-01 03-29 03-30 05-01 05-21 06-20 06-29 07-16 08-15 "
               "09-18 09-19 09-20 10-12 10-31 11-01 12-08 12-25".split())


def tipo_dia(fecha):
    if fecha.weekday() == 6 or fecha.strftime("%m-%d") in FESTIVOS:
        return "domingo_festivo"
    return "sabado" if fecha.weekday() == 5 else "habil"


def main():
    calendario, cuartos = defaultdict(list), defaultdict(list)
    with (CARPETA / "censo_prg.csv").open() as archivo:
        universo = {date.fromisoformat(f["fecha"]): float(f["kUSD_dia"]) * 1000
                    for f in csv.DictReader(archivo)}
    if len(universo) != 366 or any(d.year != 2024 for d in universo):
        raise ValueError("Se requieren todos los días de 2024")
    for dia in sorted(universo):
        calendario[(dia.month, tipo_dia(dia))].append(dia)
        dias_mes = monthrange(2024, dia.month)[1]
        cuarto = (4 * dia.day - 1) // dias_mes + 1
        cuartos[(dia.month, cuarto)].append(dia)

    # La asignación y la semilla dependen solo del calendario.
    rng = Random(20261120)
    muestra = []
    for (mes, tipo), fechas in sorted(calendario.items()):
        n = 4 if tipo == "habil" else 2
        for dia in rng.sample(fechas, n):
            muestra.append((dia, mes, tipo, len(fechas), n, n / len(fechas), len(fechas) / n))
    with (CARPETA / "muestra_calendario.csv").open("w", newline="") as archivo:
        salida = csv.writer(archivo, lineterminator="\n")
        salida.writerow(["fecha", "mes", "tipo", "N", "n", "probabilidad", "peso"])
        salida.writerows(sorted(muestra))
    if len(muestra) != 96 or not math.isclose(sum(f[-1] for f in muestra), 366):
        raise ValueError("La muestra no representa los 366 días")

    total = sum(universo.values())
    print(f"Costo programado censal en USD: {total:,.2f}")
    for nombre, estratos in [("Cuartos de mes", cuartos), ("Mes y tipo de día", calendario)]:
        varianza = 0.0
        for (_, clave), fechas in estratos.items():
            n = 4 if clave == "habil" else 2
            N = len(fechas)
            varianza += N * (N - n) * variance(universo[d] for d in fechas) / n
        print(f"{nombre}: EE exacto del diseño para el total en USD = {math.sqrt(varianza):,.2f}")
    print(f"Total estimado con el nuevo sorteo en USD: {sum(universo[f[0]] * f[-1] for f in muestra):,.2f}")


if __name__ == "__main__":
    main()
