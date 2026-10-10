# Resultados de la réplica adaptada (RM, 2017–2025)

Fecha: 2 de octubre de 2026. Programas: `scripts/preparar_muestra.py` y `scripts/estimar.R`. Resultados: `resultados/resumen_estimaciones.csv`, `resultados/estimaciones/*.json`, `*_eventstudy_*.csv`, `*_cs_gt_*.csv` y figuras `*.png`. Las decisiones están en REGISTRO_DECISIONES.md (D-13 a D-21).

## Advertencia de interpretación

Con 2 a 4 unidades tratadas según la definición (19 en el artículo), fechas de entrada inciertas y controles expuestos por la red, **estas estimaciones no permiten una interpretación causal defendible.** Se presentan para documentar qué produce la estrategia del artículo con los datos chilenos disponibles. No se eligieron especificaciones por su signo ni por su significancia; se informan todas las que se corrieron.

## Especificación principal (distrito censal, G documentado)

Resultado: D = P − P_Quillota (USD/MWh), promedio anual. Hay 3 distritos tratados (Colina-3 en 2021; Lampa-4 y San Bernardo-11 en 2023). Tras el emparejamiento 10‑NN quedan 16 controles únicos, con pesos 1/m.

| Estimador | D | L (2017–2023) | C (2017–2023) |
|---|---|---|---|
| TWFE (EE por conglomerado) | 0,44 (0,48) | −0,38 (0,15) | 0,36 (0,44) |
| Sun y Abraham, ATT agregado | 1,32 (0,69); IC95 [−0,02; 2,67] | 0,18 (0,12) | 0,38 (0,44) |
| Callaway y Sant'Anna, ATT simple | 1,32 | 0,18 | 0,38 |
| TWFE sin emparejar (57 controles) | 0,33 (0,35) | 0,16 | 0,23 |
| p de aleatorización (2.000 asignaciones) | TWFE 0,52; CS 0,35 | — | — |

Referencias:

- Nivel previo de D: 2,59 en los tratados antes de G y 3,13 en los controles en 2017–2018.
- Artículo (Virginia): 2,49 (EE 1,25) para congestión más pérdidas, 2,32 para congestión y 0,17 para pérdidas.
- Con el resultado P (precio total) los coeficientes son idénticos a los de D, como se espera con efectos de año.
- El TWFE con copias ponderadas 1/m es idéntico al de controles únicos sin ponderar (0,439277), lo que confirma la lectura de la regla de pesos del artículo.

**Estudio de eventos (Sun y Abraham, referencia t = −1).** Ver `resultados/estimaciones/distrito_G_doc_eventstudy_D.png`. Los coeficientes previos son positivos y decrecientes: 2,85; 2,64; 1,82; 1,67 y 0,63 en t = −6 a −2, varios con p < 0,05 por conglomerado. Es decir, antes de la entrada D venía cayendo en los tratados respecto de los controles. Los coeficientes posteriores son 0,78; 2,12; 2,13; 0,68 y −1,22 en t = 0 a 4. El supuesto de tendencias paralelas no es sostenible, y el ATT positivo coincide en buena medida con la reversión de esa tendencia. Cada coeficiente se identifica con una o dos unidades tratadas.

## Sensibilidad

D, en USD/MWh; ver `resultados/resumen_estimaciones.csv`.

| Variante | Tratadas | TWFE | Sun y Abraham | p aleat. (TWFE / CS) |
|---|---|---|---|---|
| Distrito, G documentado (principal) | 3 | 0,44 | 1,32 | 0,52 / 0,35 |
| Distrito, **G mínimo** (primer año posible) | 3 | −0,72 | −1,27 | 0,27 / 0,15 |
| Distrito, panel no balanceado | 3 | 0,41 | 1,02 | 0,51 / 0,41 |
| Distrito, controles a ≥ 5 km de cualquier centro | 1 (2 fuera de soporte) | −0,49 | −1,79 | 0,59 / 0,43 |
| Distrito, controles con correlación previa < 0,5 | 3 | −0,10 | −1,80 | 0,88 / 0,62 |
| Comuna, G documentado | 2 | 0,41 | 1,58 | 0,32 / 0,28 |
| Comuna, G mínimo | 2 | −1,01 | −1,02 | 0,15 / 0,34 |
| Nodo r = 2 km | 2 (1 fuera de soporte) | −1,14 | −4,32 | 0,97 / 0,53 |
| Nodo r = 3 km | 3 (1 fuera de soporte) | −1,42 | −4,89 | 0,68 / 0,97 |

Dejando fuera un tratado a la vez (distrito, G documentado), Sun y Abraham da 2,80 (sin Colina-3), 0,18 (sin Lampa-4) y 1,36 (sin San Bernardo-11).

## Lectura

1. **Ninguna estimación es distinguible de cero** con inferencia por aleatorización (p ≥ 0,14 en todas; mínimo 0,148). Los EE por conglomerado son menores, pero no son fiables con 1 a 3 conglomerados tratados.
2. **El signo depende de la fecha de entrada.** Con la operación documentada, el efecto es positivo. Con el primer año posible del intervalo (ODATA ST01 en 2021 y EdgeConneX en 2020), es negativo. La incertidumbre documental sobre G basta para invertir el resultado.
3. **El signo también depende de la escala y de los controles.** El distrito y la comuna dan efectos positivos con G documentado. Los entornos de nodo y los controles alejados o poco correlacionados dan efectos negativos.
4. **Tendencias previas.** Se rechaza informalmente el paralelismo en la especificación principal.
5. **Componentes.** Con años completos solo hasta 2023, L y C son pequeños e inestables: L va de −1,5 a +2,7 y C de −1,4 a +1,5 según la variante. No hay evidencia de que el resultado provenga de pérdidas o de desacoples.

**Conclusión de la réplica base.** Con la medida chilena validada y la estrategia del artículo, no se encuentra evidencia robusta de un efecto de la entrada de centros de datos sobre el componente espacial del precio en la RM. Tampoco se puede descartar un efecto de la magnitud de Virginia: el intervalo de Sun y Abraham, [−0,02; 2,67], contiene 2,49. El diseño carece de potencia y de soporte para distinguir entre ambas hipótesis. El resultado nulo es una consecuencia de las limitaciones de identificación, no una prueba de ausencia de efecto.

## Ajustes necesarios para la réplica y extensiones posibles

**Ajustes ya incorporados por necesidad:**

- Referencia Quillota en lugar de la referencia distribuida.
- D, L y C reconstruidos.
- Ventana 2017–2025.
- Distrito censal en lugar de sector censal.
- Covariables sustitutas.
- Panel de barras balanceado.
- Inferencia por aleatorización.
- Fechas como intervalos, con dos reglas de G.

**Extensiones que podrían mejorar la identificación** (todavía no estimadas; requieren una pregunta y un registro propios):

- **Tratamiento por conexión eléctrica documentada.** Usar la subestación de conexión y la fecha de puesta en servicio (cartas CEN) en lugar de la colocalización. Hay evidencia para Ascenty y Microsoft (S/E Chacabuco), Cirion y Scala (S/E Quilicura), EdgeConneX (S/E Las Canteras) y Google (S/E Los Libertadores).
- **Intensidad.** Usar la potencia conectada o la demanda medida, en lugar de una variable binaria. Esto permitiría usar las expansiones en unidades ya expuestas, que hoy se descartan.
- **Frecuencia horaria o mensual de los desacoples.** Medir episodios del subsistema SD4 a partir de los registros de desacople, para estudiar el mecanismo de congestión. Requiere los antecedentes diarios.
- **Diseño de exposición por red.** Usar distancias eléctricas o topología, no geográficas, para tratar explícitamente la interferencia.
