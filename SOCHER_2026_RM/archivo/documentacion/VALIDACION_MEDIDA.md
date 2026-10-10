# Validación de la medida eléctrica

Fecha: 2 de octubre de 2026. Programas: `scripts/piloto_conciliacion.py` y `scripts/continuidad_precios.py`. Resultados: `resultados/piloto_conciliacion.json` y `resultados/continuidad_precios.json`.

## Resultado

En las dos muestras oficiales, el costo marginal publicado cumple, dentro de cada subsistema, **P_it = λ_s(i),t · FP_it**. Quillota 220 kV tiene FP = 1 en todos los intervalos y pertenece siempre al subsistema principal. Con esa normalización se reconstruye una descomposición contable exacta:

| Componente | Definición propia | Interpretación admisible |
|---|---|---|
| E_t | P de Quillota 220 kV | Precio de referencia del subsistema principal. No es la referencia distribuida por carga de PJM |
| L_it | E_t (FP_it − 1) | Pérdidas marginales relativas a Quillota, valoradas al precio de referencia |
| C_it | P_it − E_t · FP_it | Diferencia de precio por pertenecer a otro subsistema (desacople). Es nula, salvo redondeo, cuando la barra comparte subsistema con Quillota |
| D_it | P_it − E_t = L_it + C_it | Componente espacial relativo a Quillota |

Equivalencia física y equivalencia econométrica son afirmaciones distintas:

- **Física.** D es una identidad contable bajo la convención chilena de factores y subsistemas. C no mide toda la congestión de red: el método chileno representa la congestión mediante separación de subsistemas, no mediante un componente nodal por restricción como el LMP de PJM. Además, L y C dependen de la referencia elegida.
- **Econométrica.** Con efectos de año completos, misma muestra y mismos pesos, restar E_t no cambia el coeficiente. Se verificó numéricamente: en todas las especificaciones, el coeficiente sobre P es idéntico al coeficiente sobre D (por ejemplo, 0,439277 en el TWFE del distrito). Esta igualdad no prueba que D sea una descomposición física observada.

## Piloto del 15 de julio de 2024 (régimen nuevo)

| Comprobación | Resultado |
|---|---|
| Archivo comparativo (R) frente a promedios R | Idénticos en las 144.000 barra-intervalos. 170 filas marcadas MODIFICADO |
| Preliminar frente a real | Iguales salvo casos aislados (máximo 54,0 USD/MWh) |
| En línea frente a real | Diferencia absoluta mediana de 0,77 y p99 de 23,2 USD/MWh. Solo la versión real se usa |
| Factores | 1.535 barras × 96 intervalos. 10.318 filas «ESTIMADO» y 137.042 «LEÍDO». Todas las barras con precio tienen factor; 35 factores no tienen precio (barras de prueba o auxiliares) |
| Identidad P = λ·FP (intervalos sin cambio de subsistema) | Desviación relativa mediana 3,2e-8, p99 1,9e-7, máximo 0,9% |
| Archivo por minuto | Usa factores distintos de los reales de 15 minutos: solo coincide donde FP = 1. Es un antecedente; no reemplaza el precio definitivo |
| D = L + C | Error máximo 2,8e-14 |
| Intervalos con más de un subsistema | 44 de 96 |

**Desacople en la RM.** Entre 12:27 y 16:30 se registraron dos desacoples por «control de transferencia» en el transformador C.NAVIA 220→110 kV. Formaron el subsistema SD4 con 59 barras: Quilicura, Chacabuco, Lo Boza, Pudahuel, Lo Aguirre, Batuco, Renca, San Cristóbal, Recoleta y otras de la red de 110 kV del sector norponiente. En los 14 intervalos desacoplados, C promedió 24,9 USD/MWh (λ_SD4 = 85,05 frente a 62,76 en SD1). En el día completo, D de esas barras fue 6,6 USD/MWh: C = 3,8 y L = 2,8. Es evidencia directa de congestión en la red de distribución troncal donde se concentran los centros de datos. Una barra sin centro local puede compartir el subsistema con barras tratadas, de modo que la ausencia de centros no garantiza ausencia de exposición.

## Piloto de diciembre de 2017 (régimen histórico)

| Comprobación | Resultado |
|---|---|
| Precios | 1.235 barras × 744 horas, un decimal. 1.512 vacíos (2 barras sin precio) que se conservan como faltantes |
| Asignación de tramos de factores | Búsqueda empírica: horas 1–8, 9–18 y 19–24 (99,9% de barra-horas dentro de 0,5%). El mismo mapeo resultó óptimo en los 91 meses extraídos |
| Identidad P = λ·FP | Desviación log mediana 0,05%, 99,97% < 0,5%; compatible con el redondeo |
| Quillota 220 kV | FP = 1 y siempre en SD1. 38 horas con precio cero (vertimiento hidro) |
| C en el subsistema de Quillota | p99 = 0,07 USD/MWh (redondeo). En otros subsistemas, mediana 5,4 |

## Continuidad entre regímenes

El Coordinador separa el histórico (hasta el 14/07/2024) del costo marginal real nuevo (desde el 15/07/2024). Antes de combinarlos se comprobó:

1. **Definición horaria.** En abril de 2024, el precio horario del libro es el promedio de los cuatro cuartos del CSV oficial con la misma etiqueta: 99,9% de diferencias < 0,01 y máximo 0,017 por redondeo. Con una hora de desplazamiento solo coincide el 31%. Se usa hora = HRA + 1 en el régimen nuevo.
2. **Mismo dato.** El TSV mensual REAL-DEF reproduce exactamente el precio R de la muestra diaria oficial del 15/07/2024 en las 144.000 filas.
3. **Universo de barras.** Hay 1.500 barras a ambos lados del corte, con el mismo conjunto de códigos.
4. **Nivel.** En barras RM, D bajó 0,56 USD/MWh entre la primera y la segunda mitad de julio de 2024 (EE aproximado 0,87). Particiones placebo: +0,71 en 2023 y −1,91 en 2025. No hay salto distinguible de la variación habitual.

**Limitación.** Desde el 15/07/2024 no se dispone de factores públicos en esta base (los paquetes diarios de antecedentes están detrás de Cloudflare), así que L y C solo existen hasta 2023 como años completos. D está disponible en todo 2017–2025.

## Cambios de nombre y homologación

- Desde junio de 2023, 20 códigos con «Ñ» se publican con «N» (p. ej., PIÑATAS_______066 → PINATAS_______066). Se unifican.
- En mayo de 2024, LAMPA 23 kV cambió el relleno con guiones bajos. Se unifica mediante una tabla de alias (`datos/geo/alias_codigos.csv`).
- No se fusionan códigos con meses superpuestos ni nombres parecidos.
- Diccionario de barras (`datos/geo/barras_diccionario.csv`): 1.613 códigos. 1.378 se vinculan a una subestación de Infotécnica con coordenadas; 214 están en la RM. Los vínculos provienen del ID Infotécnica del TSV, la homologación oficial, nombres exactos o un prefijo idéntico de otra tensión. Las derivaciones (TAP) quedan sin localizar.

## Pendiente

- Factores reales posteriores al 15/07/2024 (requieren descarga manual de los paquetes diarios o del portal).
- Reliquidaciones posteriores a la versión DEF de cada mes (no inventariadas).
- Verificación de factores «ESTIMADO» frente a «LEÍDO» en todo el período.
