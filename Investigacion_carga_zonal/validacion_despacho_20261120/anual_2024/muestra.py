"""Muestra aleatoria de dos días por cuarto de mes, independiente del resultado."""
import calendar
import csv
import datetime as dt
import random

rng = random.Random(20241120)
with open('muestra.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['fecha','estrato','dias_estrato','peso'])
    segundo = random.Random(20241121)
    for mes in range(1,13):
        dias = calendar.monthrange(2024,mes)[1]
        for k in range(4):
            inicio = dias*k//4+1
            fin = dias*(k+1)//4
            elegido = rng.randint(inicio,fin)
            otro = segundo.choice([d for d in range(inicio,fin+1) if d!=elegido])
            for d in sorted((elegido,otro)):
                w.writerow([dt.date(2024,mes,d), k+1, fin-inicio+1, (fin-inicio+1)/2])
