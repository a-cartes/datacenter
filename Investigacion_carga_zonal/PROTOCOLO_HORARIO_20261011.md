# Heterogeneidad horaria de Las Canteras

Prioridad: artículo Energy Economics; SOCHER conserva su cierre. Solicitud del usuario del11-10-2026. Exploración posterior al resultado mensual: señal positiva frente a controles distantes y comparación cercana próxima a cero. Se fijan reglas antes de calcular nuevas asociaciones horarias; no es un prerregistro ajeno al conocimiento anterior.

## Panel

Agosto2024–agosto2026. Retiro HT1+HT2 horario en MWh por intervalo de una hora, numéricamente MW medios, desde frontera ya conciliada. Precios de barras originales de las25 particiones REAL, sin modificar fuentes. Unión por fecha y hora civil America/Santiago, conservando UTC físico; excluir días con23/25 horas, duplicados y días incompletos de cualquiera de las barras/carga. No escoger desfase por mejor resultado. Sensibilidad física desplazada−1/+1hora en días completos.

Zona fija: media Batuco110, Libertadores110, Cerro Navia110. Comparadores ya fijados: cercanosK5 y distantesK5/K7 de la revisión anterior, sin nueva búsqueda según coeficientes. Resultados: zona menos comparadores y Canteras menos distantesK5. Conservar también D zona−Quillota como diagnóstico de referencia. No reclasificar controles por los nuevos resultados.

## Estados y estimaciones

1. Horas fijas disjuntas: solar10–16 inclusive; tarde-noche19–23 inclusive; resto. Son bloques de reloj, no punta oficial ni congestión certificada.
2. Mayor carga física: percentil75 del retiro HT12 dentro de cada mes. Ajuste lineal continuo por tramos: MW más máximo(MW−p75mensual,0). La pendiente sobre el umbral es la suma de ambos coeficientes; reportar también su diferencia. El umbral depende solo de carga, no del resultado, y se calcula una vez. Esta es heterogeneidad observacional, no asignación exógena.
3. Precio sistémico alto: Quillota≥100USD/MWh, umbral fijado sin buscar significancia; interacción con carga y nivel del indicador. Diagnóstico endógeno de estado de precio, no variable de congestión ni instrumento. No se concluirá que la carga causa congestión con esta prueba.
4. Restricciones documentadas: revisar registros locales EAF de07-10-2024,26-10-2024 y06-11-2024; control de transferencias Alto Jahuel–Lo Aguirre500kV. Extraer inicio/fin y evidencia de estado a medianoche. Usar solo horas completas incluidas/excluidas del intervalo, omitiendo horas de transición. Los demás días tienen estado desconocido. Tres días solo admiten descripción de casos.

Dos estructuras de efectos fijos: A, mes y hora de la semana; B, día, mes×hora y hora de la semana. B se centra en variación intradiaria neta de perfiles horarios mensuales. Estimar lineal, interacciones por bloques, spline de carga y estado de precio. Reportar variación residual disponible, coeficientes, diferencias de pendientes e intervalos condicionales. No multiplicar el número de intervenciones por las horas.

Covarianza temporal principal: sumar scores por semana ISO y HAC Bartlett4 semanas, correcciónG/(G−1). Sensibilidad por bloques mensuales (25); se describe como inferencia condicional de una serie, no inferencia aleatorizada entre centros. Controlar multiplicidad de diferencias exploratorias con Holm dentro de la familia de pruebas de interacción de cada estructura FE, sobre los cuatro resultados de brecha; D de referencia separado. Usar normal asintótica; pocos bloques y dependencia residual limitan la interpretación.

## Robusteces fijadas

Repetir interacciones de bloques B para desfases físicos−1/+1hora y para submuestras agosto2024–julio2025 y agosto2025–agosto2026. Presentar todos los signos. Comparar medias mensuales por bloque y asociación con retiro del mismo bloque para evaluar qué cambia al agregar. No presentar diferencias de pendientes como prueba de dilución si desaparecen al retirar efectos comunes o dependen de alineación/subperíodo.

## Evidencia y preservación

Nueva ejecución, manifiestos SHA256 antes/después, selección previa intacta. Reporte independiente de SOCHER, bitácora y control de cambios. Fuente de estado operativo nunca se infiere de D, de precios altos o de ausencia de registro. Conservar fracasos de estimación y divergencias; no modificar originales, signos ni etiquetas históricas.
