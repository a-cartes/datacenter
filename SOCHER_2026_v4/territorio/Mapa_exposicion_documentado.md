# Las Canteras: exposición eléctrica y alcance territorial documentados

Revisión del 25 de septiembre de 2026. Un solo artículo; estudio de expansión/conexión de centros de datos. Los códigos S01–S18 remiten a `fuentes_manifest.csv/json`, con URL directa, páginas PDF contadas desde 1, original local y SHA-256. `registro_barras.csv` contiene las 19 barras candidatas; `registro_conexiones.csv`, 20 relaciones eléctricas con fecha y límite de interpretación. Las fuentes originales v2/v3 permanecen intactas.

**Dictamen:** existe un caso observable de ampliación del campus y conexión eléctrica en 2024, con exposición potencial que atraviesa comunas y regiones. No se ha validado un grupo de barras no expuestas ni una fecha única de primera carga. El resultado defendible actual es un contraste descriptivo de diferenciales durante la secuencia de conexión y crecimiento del retiro. La identificación causal debe referirse al paquete de expansión y obras cuando sus componentes no puedan separarse.

## Qué conexión está documentada y de qué fecha

El [informe de 2021 alojado por CEN](https://www.coordinador.cl/wp-content/uploads/2021/07/InfDef_EdgeConneX_Sol._de_Ejecucion_de_Obra_Urgente_de_Transmision-2.pdf), S01, pp. 4–8 y 12, distingue un campus ya operativo desde 2020 y la ampliación DC02/DC03 que utilizaría una nueva seccionadora de 110/23 kV en el corredor Cerro Navia–Las Vegas. El diseño mantenía para DC01 conexiones separadas; no corresponde llamar a 2024 primera entrada del campus. El diseño incluye dos transformadores de 40 MVA, magnitud distinta de 40 MW de demanda prevista o efectivamente medida. El [CMN](https://www.monumentos.gob.cl/sites/default/files/20230809_acta_sesion_ord_env_def_f_0.pdf), S02 p. 106, acredita el cambio de nombre del proyecto: Seccionadora Colina → Las Canteras. No autoriza sustituir cualquier otra etiqueta «Colina».

El [EAF563/2024](https://www.coordinador.cl/wp-content/uploads/2024/12/EAF-563-2024.pdf), S06 p. 6, muestra al 03-dic-2024 H1 hacia Santiago Solar, H2 hacia Las Vegas, H3 hacia Cerro Navia circuito 2 y H4 hacia Cerro Navia circuito 1, además de TR1–TR3. Esta evidencia respalda la pertenencia al corredor, **no los estados de interruptores de junio**. El [EAF093/2025](https://www.coordinador.cl/wp-content/uploads/2025/03/EAF-093-2025.pdf), S07 pp.1–3, sitúa Tap Libertadores en el circuito Cerro Navia–Las Canteras; su fecha es26-feb-2025. La memoria [CTNG 2019](https://www.ctng.cl/wp-content/uploads/2020/04/Memoria-Corporativa-2019-CTNG.pdf), S14 pp.5 y12, ya describe la conexión Dataluna en Quilicura al corredor y las líneas Las Vegas–San Pedro y San Pedro–Quillota.

Quilicura y Chacabuco pertenecen a otra rama: el [EAF456/2024](https://www.coordinador.cl/wp-content/uploads/2024/09/EAF-456-2024.pdf), S12 p. 131, documenta el 29-ago-2024 la transferencia de Quilicura al circuito 2 Cerro Navia–El Salto y la pérdida de suministro en transformadores de Chacabuco tras la falla del circuito 1. Se registra el vínculo con el corredor, sin inventar una línea directa entre cada subestación y Cerro Navia ni retrotraer automáticamente esa configuración a junio.

![Esquema de conexiones documentadas](/Users/yo/Downloads/Medidas%20Transferencias%20econo%CC%81micas-selected/SOCHER_2026_v4/territorio/Esquema_conexiones_documentadas.png)

El esquema es reproducible mediante `construir_registro_y_esquema.py`; su disposición no representa distancia, orientación geográfica, impedancia o una simulación de flujos. El panel A reproduce relaciones del diseño2021; el panel B conserva las fechas de las confirmaciones posteriores. No usar el número de saltos gráficos como peso causal.

## Regla de exposición y territorio

La regla propuesta se fija por equipo/fase y conexión, sin seleccionar barras por el signo o significación de sus precios. Las clases son cualitativas y provisionales; no constituyen una matriz de transferencia de potencia. Reconstruir el estado histórico sigue siendo necesario aunque el criterio se haya fijado antes de la estimación.

| Nodo y tensión relevante | Clase y fundamento eléctrico | Territorio verificado y límite |
|---|---|---|
| Las Canteras 110/23 | Directa: instalación receptora de la conexión/expansión | Campus en Colina según S01 p. 4. **Comuna física de la subestación no resuelta:** S06 p. 2 consigna Tiltil; no se elimina esa discrepancia ni se hereda la comuna del campus. |
| Cerro Navia 110; 220 separado | Vecina del corredor 110 seccionado. 220 es otra barra | Cerro Navia, RM: [SMA/SNIFA](https://snifa.sma.gob.cl/UnidadFiscalizable/Ficha/9631), S15. |
| Las Vegas 110 BP1/BP2 | Vecina del mismo corredor; BP1 ≠ BP2 | Región de Valparaíso en antecedentes del corredor. La comuna física queda pendiente en esta revisión; un alimentador llamado Llay Llay no basta para asignarla. |
| Tap Libertadores 110 | Vecina del corredor; consumo de otro centro de datos | Quilicura, RM, conexión descrita por S14 p. 5; vínculo posterior específico S07. No es la barra Quilicura 110. |
| Quillota 110; 220 separado | **Referencia con exposición indirecta posible**, por San Pedro–Las Vegas | Quillota, Valparaíso: [EAF418/2023](https://www.coordinador.cl/wp-content/uploads/2023/10/EAF-418-2023.pdf), S13 p. 124. |
| Chacabuco 110/23 | Otra rama y abastecimiento previo del campus; sustitución de carga posible | Quilicura, RM: [EAF080/2020](https://www.coordinador.cl/wp-content/uploads/2020/03/EAF-080-2020.pdf), S09 p. 5 nota (*), distingue ubicación física y comunas servidas. |
| Chicureo 220/23 | Exposición a la fase 2024 no resuelta; antecedente de suministro previsto DC01 | Colina, RM: [CNE](https://www.cne.cl/wp-content/uploads/2021/08/ITD-Anexo-1-Ing-conceptuales.pdf), S10 p. 54. No es nodo 110 ni se ha verificado aquí la fecha del suministro previsto. |
| Quilicura 110/23/12 | Otra rama vinculada a Cerro Navia–El Salto; exposición indirecta posible | Quilicura, RM: [CEN, propuestas dic 2024](https://www.coordinador.cl/wp-content/uploads/2024/12/Apendice-I-Descripcion-de-Obras-de-Propuestas.pdf), S11 p. 50; vínculo eléctrico S12. |

**Ninguno queda acreditado como no expuesto.** Referencia, vecino y control son funciones distintas. La distancia o una frontera regional no descartan interferencia. La homologación oficial de julio 2024, S08, verifica identidades; no verifica estados operativos. Su fila 175 une `CANTERAS______110` con `BA01T0487SE001T0487`; Quillota 110/220, Cerro Navia 110/220 y las dos barras 110 de Las Vegas se conservan separadas en el CSV.

## Secuencia 2024: no reemplazar una fecha por otra

- **07 abril:** el [EAF143/2024](https://www.coordinador.cl/wp-content/uploads/2024/04/EAF-143-2024.pdf), S03 p. 105, contiene solicitudes 2024032525/2530/2531 para continuación de PES de NUP3016 y trabajos de PES de TR1/2-NUP3975. Son actividades programadas 09:00–18:00; las mismas filas indican **«Ejecución Exitosa» y fechas efectivas 08:52–21:24**. Esto corrobora ejecución de esos trabajos, no la primera energización, la primera demanda del campus ni el fin de PES completo. Se inspeccionó la página original y la alineación de columnas.
- **02 mayo y 29 mayo:** EO de NUP3016 y NUP3975, respectivamente, en [reporte CEN septiembre 2024](https://www.coordinador.cl/wp-content/uploads/2024/09/Reporte-NI-MR-Septiembre-2024.pdf), S04 p. 7. No se equiparan a primera toma de carga.
- **Noche del 24 de junio / etiqueta UTC del 25 de junio:** auditoría de medidas del equipo muestra aumento sostenido de HT1/HT2. Fecha observacional inferida de retiros, pendiente de mecanismo físico independiente. Las inversiones D/R en líneas también ocurren otras veces: no prueban una maniobra excepcional.
- **06 agosto:** PES de T3-NUP3349 desde la barra 110 kV N°2 en [EAF414/2024](https://www.coordinador.cl/wp-content/uploads/2024/08/EAF-414-2024.pdf), S05 p. 99. Es otra fase; no sumar capacidades nominales o canales HT3 sin validar orientación.

La búsqueda adicional del 24–25 de junio se acotó a EAF309/2024, S16 (240 páginas, anexo operativo del 25 de junio), y EAF291/2024, S17 (48 páginas). No se encontró una solicitud Las Canteras / NUP3975 que explicara la toma de carga. La coincidencia 3016 del primero corresponde a otra solicitud; el segundo describe una falla de 44 kV en Los Andes–Juncal. Su coincidencia horaria no demuestra relación con Canteras. Una ausencia en estos informes no prueba que no existiera maniobra ni sustituye la bitácora CDC.

## Estimando y alcance mínimo del mismo artículo

Sea (P) la secuencia de expansión y obras asociadas, y (p_{bt}(P)) el precio de la barra (b) bajo ese régimen. Si carga y red son inseparables, el objetivo causal coherente es:

\[
\tau_{b,r}=E\{[p_{bt}(P=1)-p_{rt}(P=1)]-[p_{bt}(P=0)-p_{rt}(P=0)]\mid\text{ventana posterior}\}.
\]

Es el efecto del **paquete** sobre un diferencial, con la referencia (r) sometida al mismo mundo contrafactual. Si (r) también responde, el estimando resta esa respuesta: no es el efecto total sobre (b), el costo marginal por MW de demanda ni el costo social. Un efecto relativo nulo es compatible con un cambio común a ambos precios. La definición del paquete debe indicar qué fases y obras retira el mundo(P=0); no basta llamarlo «sin centro».

Hoy el panel de efectos fijos y sus contrastes antes/después describen cambios relativos; una fecha EO no proporciona exogeneidad. Avanzar exige el siguiente cierre específico: **carga/equipo validado, secuencia operativa fechada y un contrafactual defendible frente a obras e interferencia**. No aumentar artificialmente el número de unidades tratadas contando transformadores o fases del mismo campus como sitios independientes. Tampoco incluir retiro realizado o topología posterior como controles rutinarios si son mecanismos del paquete cuyo efecto total se quiere medir. El 15 de julio y fases posteriores requieren una ventana y un tratamiento explícitos del cambio de publicación CMg; no se unen series por mera coincidencia de nombres.

Para la versión de congreso, el núcleo empírico honesto es mostrar la secuencia de retiro verificada y la evolución conjunta de diferenciales de la barra receptora y el corredor, explicar qué comparación elimina componentes comunes y reportar resultados aun si son pequeños o nulos. Una interpretación causal queda condicionada a cerrar la asignación y la interferencia, no a obtener una pre-tendencia estadísticamente nula.

**Relevancia regional.** La inversión digital se localiza en un territorio, pero se abastece mediante infraestructura que conecta otros territorios. Este caso permite estudiar dónde cambian las señales mayoristas relativas durante una expansión y si esos cambios se concentran en la conexión o aparecen en el corredor. Esa evidencia puede informar decisiones de localización y coordinación de infraestructura entre comunas y regiones. Los CMg no son tarifas finales pagadas por hogares; sus diferenciales tampoco miden por sí solos bienestar, empleo, productividad regional o costo social. Una cartografía de exposición potencial es un resultado metodológico útil incluso si no aparece un efecto detectable sobre precios.
