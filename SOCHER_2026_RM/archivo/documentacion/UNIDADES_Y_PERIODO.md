# Unidad geográfica, período y universo de comparación

Fecha: 2 de octubre de 2026. Programa: `scripts/diagnostico_unidades.py`. Resultados: `resultados/diagnostico_unidades.json` y `datos/unidades/historia_*.csv`.

## Período

| Criterio | Evidencia | Decisión |
|---|---|---|
| Cobertura de precios con referencia | Originales DEF desde enero de 2017; 2015–2016 no disponibles sin descarga manual | Ventana 2017–2025: 9 años completos y 108 meses |
| Homogeneidad | Los regímenes se concilian (VALIDACION_MEDIDA.md). El SIC y el SING se interconectaron en nov 2017; la RM siempre estuvo en el SIC | Sin quiebre en las barras RM |
| Años previos | El artículo exige primeras entradas desde 2017 en 2015–2024 (al menos 2 años previos) | Entradas elegibles 2019–2025. Se excluyen unidades con operación anterior a 2019 |
| L y C | Factores públicos solo hasta jul 2024 | L y C con años completos 2017–2023 |

## Comparación de unidades candidatas

Las barras se asignan a unidades mediante las coordenadas de su subestación en Infotécnica: 145 subestaciones dentro de la RM, con 98,6% de coincidencia entre la comuna declarada y el polígono INE. El panel usa 194 barras RM con cobertura ≥ 0,9 en los 9 años (94 subestaciones).

| Alternativa | Unidades con barras balanceadas | Presencia previa (< 2019) | Historia incierta | Tratadas 2019–2025 | Cohortes (G documentado) | Controles |
|---|---|---|---|---|---|---|
| Comuna (52 en la RM) | 38 | 6 | 5 | **2** (Lampa, San Bernardo) | 2023: 2 | 25 |
| Distrito censal 2017 (451) | 76 | 4 | 12 (10 por instalaciones sin coordenadas en la comuna) | **3** (Colina-3, Lampa-4, San Bernardo-11) | 2021: 1; 2023: 2 | 57 |
| Entorno de nodo, r = 2 km | 94 subestaciones | 7 | 8 | 3 (+ Las Canteras, sin años previos) | 2020: 1 (Chacabuco); 2023: 2 (Chena y Panamericana, un mismo centro) | 76 |
| Entorno de nodo, r = 3 km | 94 | 11 | 9 | 4 (todos por ODATA ST02) | 2023: 4 | 70 |
| Entorno de nodo, r = 5 km | 94 | 23 | 10 | 9 (7 por ODATA ST02) | 2021–2023 | 52 |

Las columnas cuentan solo unidades con al menos una barra de panel balanceado; el conteo completo por estado está en `resultados/diagnostico_unidades.json`.

**Tratamientos independientes.** En todas las escalas, las primeras entradas se reducen a tres o cuatro instalaciones: EdgeConneX Colina (2020–21), ODATA ST01 Lampa (2021–23), ODATA ST02 San Bernardo (2023) y, solo con nodo r = 2 km, Ascenty en S/E Chacabuco (2020). Al ampliar el radio aumentan los nodos tratados, pero no los eventos independientes. En el artículo hay 19 sectores tratados.

## Elección

**Unidad principal: distrito censal 2017.**

- Es la escala oficial más cercana al sector censal de Virginia.
- Separa EdgeConneX (Colina-3) de Claro Liray (Colina-1), cosa que la comuna no permite.
- Tiene covariables censales comparables (población y viviendas) y polígonos oficiales.
- Reproduce la regla del artículo: precio = promedio de los nodos dentro de la unidad.

Alternativas reportadas: comuna (más gruesa), entorno de nodo de 2 y 3 km (más cercano a la exposición eléctrica, pero sin covariables propias y con nodos dependientes entre sí), y distrito con panel no balanceado (incluye nodos nuevos, como el artículo).

**Territorio.** Las entradas estudiadas y los controles son de la RM. No se incorporaron unidades de otras regiones: la RM tiene suficientes controles con precio (57 distritos), y unidades externas añadirían diferencias de red y de oferta sin aumentar los tratados.

## Exposición indirecta por la red

- **Evidencia de acoplamiento.** El 15/07/2024, el desacople en C.NAVIA 220/110 kV separó en un mismo subsistema 59 barras del norponiente: Quilicura, Chacabuco, Lo Boza, Pudahuel, Batuco, Renca, Recoleta, Lo Aguirre y otras. Controles como Batuco o Lo Boza comparten ese subsistema con nodos tratados o expuestos.
- **Vecindad.** Varios distritos de control están a menos de 5 km de algún centro. Excluirlos deja 33 controles, y solo 1 tratado dentro del soporte común.
- **Correlación previa.** Con el umbral de 0,5 del artículo, aplicado al D mensual de 2017–2018 frente al promedio de tratados, quedan 13 controles. Una baja correlación histórica no prueba independencia eléctrica.

La ausencia de centros locales no garantiza ausencia de efectos. Con estos datos, el supuesto de no interferencia (SUTVA) es menos plausible que en Virginia: las entradas ocurren en la misma red de 110 kV donde están muchos controles.
