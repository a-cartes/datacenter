# Alto Jahuel–Lo Aguirre a las 05:00 del 7 y 8 de octubre de 2024

**Ampliación al mes completo.** [Octubre de 2024: 744 horas de flujo medido, precio y programación oficial](octubre_2024/README.md). Incluye los 31 despachos diarios de PLEXOS, la comprobación contra las planillas PRG y la comparación con los regímenes documentados.

**Bitácora del proyecto para Energy Economics · 20 de noviembre de 2026**

Reconstruimos dos horas del corredor de 500 kV a partir de mediciones definitivas de energía en ambos extremos de los dos circuitos, precios definitivos del Coordinador y registros de control. El día 7 hubo una brecha media de **78,90 USD/MWh** entre los extremos. El día 8, con **106,30 MW más** de envío medio desde Alto Jahuel, la brecha fue de **0,81 USD/MWh**. Un umbral fijo aplicado al flujo horario observado en esas dos horas clasificaría mal el régimen si se supusiera que el mayor flujo implica mayor congestión. La instrucción operativa y la configuración marginal registrada aportan información independiente sobre qué ocurrió. El límite efectivo en MW que utilizó el operador sigue por verificar.

[Antecedentes completos del proyecto, SOCHER y pilotos anteriores](antecedentes.md) · [Tabla horaria](horas.csv) · [Ocho cuartos de hora](cuartos.csv) · [Intervalos oficiales](intervalos.csv) · [Configuraciones marginales registradas](configuraciones.csv) · [Código reproducible](reconstruir.py)

## Pregunta y selección

¿Puede el modelo reproducir precios y flujos cuando el estado operativo cambia a la misma hora del reloj y la carga de Las Canteras es similar? El par quedó seleccionado en la revisión horaria anterior por hora, carga e instrucción. Se usa para desarrollar el modelo. La variación incluye diferencias de oferta, demanda y operación entre los dos días. Medir un efecto atribuible a la carga del centro requiere un contrafactual adicional.

## Dos estados observados

El bloque corresponde a 05:00–06:00 hora continental de Chile, 08:00–09:00 UTC. Los precios y los flujos son promedios de cuatro cuartos completos. La brecha del corredor resta Alto Jahuel de Lo Aguirre. La brecha local resta Quillota de Las Canteras.

| Variable | 7 de octubre | 8 de octubre |
|---|---:|---:|
| Retiro HT1+HT2 en Las Canteras, MW | 2,0042 | 2,0221 |
| Minutos del bloque con control de transferencia documentado | 60 | 0 |
| CMg Alto Jahuel 500 kV, USD/MWh | 6,64 | 85,60 |
| CMg Lo Aguirre 500 kV, USD/MWh | 85,53 | 86,41 |
| Brecha del corredor, USD/MWh | **78,90** | **0,81** |
| Brecha Las Canteras 110 kV menos Quillota 220 kV, USD/MWh | 2,68 | 2,17 |
| Envío desde Alto Jahuel por C1 + C2, MW | 1.440,73 | 1.547,03 |
| Recepción en Lo Aguirre por C1 + C2, MW | 1.431,80 | 1.538,70 |
| Envío menos recepción, MW | 8,93 | 8,33 |
| Diferencia entre extremos como porcentaje del envío | 0,62 % | 0,54 % |

Las diferencias de potencia entre extremos son compatibles con pérdidas y diferencias de medición. Son un control de consistencia del tramo. El balance de cada barra requiere también las demás líneas, transformadores e inyecciones conectados.

## Cómo se reconstruyeron las horas

1. **Precios.** Descargamos para cada fecha el ZIP definitivo del Coordinador. Para el día 8 usamos la versión V2 enlazada en la publicación oficial. Tomamos los cuatro intervalos de 15 minutos del archivo de promedios por barra, columna en USD/MWh. Contrastamos Las Canteras y Quillota contra los precios del panel previo. Las diferencias horarias son inferiores a 0,0001 USD/MWh en cada barra y fecha. [7 de octubre](https://www.coordinador.cl/wp-content/uploads/2024/10/Antecedentes_CMG_Real_def_241007.zip) · [8 de octubre, V2](https://www.coordinador.cl/wp-content/uploads/2024/10/Antecedentes_CMG_Real_def_241008_V2.zip)
2. **Control de transferencias.** En la hoja oficial de desacoples se identifica el tramo Alto Jahuel → Lo Aguirre, la causal de control de transferencia y el intervalo de vigencia. El control iniciado a las 00:00 terminó a las 06:30 el día 7 y a las 04:03 el día 8. Este resultado coincide con el indicador del registro de instrucciones del proyecto para ambas horas. La ausencia de ese control a las 05:00 del día 8 se refiere a ese tramo y esa instrucción. [Intervalos y causal](intervalos.csv) · [EAF 499/2024, anexo operativo del día 7](https://www.coordinador.cl/wp-content/uploads/2024/10/EAF-499-2024.pdf)
3. **Configuración marginal.** El archivo de cambios por minuto registra una configuración en cada marca. Conservamos la última marca al inicio del bloque y cualquier cambio posterior dentro de la hora. El día 7, Alto Jahuel estaba en SD1 con PEHUENCHE-1 y pasó a RALCO-1_sinv a las 05:38. Lo Aguirre permaneció en SD2 con SANISIDRO-1_TG1_GN_A. El día 8, ambas barras figuraban en SD1 con ELTORO-1_vrucu_quill desde las 04:03. Esta observación permite evaluar si el modelo reproduce qué tecnología o unidad fija el precio. Atribuir toda la brecha a una única restricción requiere reconstruir el despacho y las pérdidas. [Marcas originales de configuración](configuraciones.csv)
4. **Flujo físico.** La serie histórica Qlik C1 del proyecto contenía 743 ceros en 744 observaciones de octubre en Alto Jahuel y 738 en Lo Aguirre. Recuperamos el archivo definitivo de puntos de medida, publicado por el sistema de mediciones del Coordinador. Su SHA-256 coincide con el inventario previo. Seleccionamos cuatro paños por documentación técnica y conciliamos los dos extremos por circuito. [Auditoría Qlik](../resultados/20261011_flujo500_v1/auditoria_mensual.csv) · [Tabla de paños del Coordinador](https://www.coordinador.cl/wp-content/uploads/2024/12/Requerimientos-Mejoras-Instalaciones-Transmision-2024_Informe-Preliminar.pdf) · [Mediciones definitivas de octubre](https://medidas.coordinador.cl/public/MEDIDAS%20TRANSFERENCIAS%20ECONOMICAS/2024/10_Octubre/Definitivo/1_Transferencia_Puntos_de_Medida_15MIN_CSV.zip)
5. **Dirección, unidad y cobertura.** Los medidores de Alto Jahuel marcan energía en D y los de Lo Aguirre en R en los ocho intervalos. Se expresa cada extremo en el sentido Alto Jahuel → Lo Aguirre. Convertimos kWh de cada cuarto de hora a MW medios multiplicando por 4 y dividiendo por 1.000. Se verificaron las 32 observaciones de medidor, la ausencia de duplicados, la correspondencia entre hora local y UTC y los cuatro precios en cada barra y fecha.

| Circuito | Medidor de envío en Alto Jahuel | Medidor de recepción en Lo Aguirre |
|---|---|---|
| C1 | `ALJAHUEL_500_K3_TRL` | `AGUIRETL_500_K5-K6_TRL` |
| C2 | `ALJAHUEL_500_K4_TRL` | `AGUIRETL_500_K1-K2_TRL` |

## Reproducción

Desde esta carpeta, con Python 3.11 o superior, pandas y openpyxl instalados, ejecutar lo siguiente. Los ZIP quedan fuera del repositorio. El programa comprueba las cuatro huellas SHA-256 antes de procesar y genera cuatro archivos CSV. El ZIP de mediciones contiene unos 2,28 GB descomprimidos y se lee en secuencia.

```bash
d=$(mktemp -d)
curl -fLsS 'https://www.coordinador.cl/wp-content/uploads/2024/10/Antecedentes_CMG_Real_def_241007.zip' -o "$d/7.zip"
curl -fLsS 'https://www.coordinador.cl/wp-content/uploads/2024/10/Antecedentes_CMG_Real_def_241008_V2.zip' -o "$d/8.zip"
curl -fLsS 'https://medidas.coordinador.cl/public/MEDIDAS%20TRANSFERENCIAS%20ECONOMICAS/2024/10_Octubre/Definitivo/1_Transferencia_Puntos_de_Medida_15MIN_CSV.zip' -o "$d/medidas.zip"
cp ../resultados/20261011_estimacion_rio_v3/panel_estimacion.csv.gz "$d/panel.csv.gz"
python reconstruir.py "$d" "$d/resultados"
for tabla in horas cuartos intervalos configuraciones; do
  diff -u "$tabla.csv" "$d/resultados/$tabla.csv"
done
```

La revisión de partida del repositorio es `69a68ee3ab015257b797579fd77cd1b71b2f200b`. En `horas.csv` y `cuartos.csv`, las columnas de barras son precios en USD/MWh y las de envío y recepción por circuito son MW medios. Los datos de carga proceden de HT1+HT2 y los de estado de `ctx_AJLA` del panel citado. Los dos grupos de mediciones corresponden a instalaciones diferentes.

## Qué queda para estimar el costo del desfase

- **Límite operativo y topología.** Recuperar la consigna de transferencia o inequación de seguridad aplicable por hora, el sentido y criterio de contingencia, la disponibilidad de circuitos y transformadores y las horas de maniobras. Los estudios de expansión contienen capacidades nominales en MVA y etapas de la obra NUP 1530. Esos valores sirven para reconstruir escenarios. La tasa de utilización en estas dos horas sigue indeterminada. Consultar bases históricas de programación y contrastarlas con la operación real antes de atribuir un límite al operador. [Estudio de restricciones 2024](https://www.coordinador.cl/wp-content/uploads/2024/12/Informe-Preliminar-ERST-2024.pdf) · [Modelos de programación del Coordinador](https://www.coordinador.cl/operacion/documentos/modelacion-del-sen/modelos-para-la-planificacion-y-programacion-de-la-operacion/)
- **Caso base.** Reunir disponibilidades y costos por unidad, valores del agua, demanda por barra y flujos de frontera. Cerrar balances nodales, contrastar el despacho con las configuraciones observadas y reportar error de flujo y de precio en ambos regímenes. Estos dos días son de diagnóstico. Las fechas de evaluación se fijarán antes del ajuste y deberán contener estados distintos a una misma hora. El piloto de 2021 se refiere a Polpaico–Lo Aguirre, otro corredor.
- **Resultado económico.** Una vez validado el despacho, calcular el costo incremental de la misma carga con la red original y la reforzada. Comparar luego en valor presente las fechas de inversión y operación de una obra definida. Las cifras de este informe son observaciones físicas y de precios. El efecto causal de la entrada del centro y el ahorro asociado a anticipar una obra siguen pendientes.
