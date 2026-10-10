# Definiciones y agregación

## Resultado y unidad

El resultado es `D = P − P_Quillota220`, en USD/MWh, agregado por año y distrito censal 2017. El umbral de cobertura por barra y año es 90%; la principal incorpora las barras que cumplen en cada año y la alternativa balanceada conserva las barras con cobertura en los nueve años. Las subestaciones se asignan por coordenadas y las barras mediante el diccionario técnico, conservando tensiones e identidades.

En las muestras con factores de penalización, `L = P_Quillota220 × (fp − 1)` y `C = P − P_Quillota220 × fp`. Por construcción, `D = L + C`. C captura separación de subsistemas bajo esta representación, no toda la congestión física. No se interpreta D como tarifa residencial, precio de contrato ni carga de IA medida. Los factores posteriores a julio de 2024 no forman una serie completa disponible para esta descomposición.

## Emparejamiento y tratamiento

El probit usa log población, log viviendas, proporción de inmigrantes, proporción de pueblos originarios y materialidad aceptable. Se seleccionan diez vecinos con reemplazo y se aplica soporte común. Las muestras y los diagnósticos de todas las variantes quedan incluidos. Los empates exactos se resuelven por identificador alfanumérico ascendente; la [nota de portabilidad](PORTABILIDAD.md) documenta su diferencia con dos muestras históricas de radios. El emparejamiento demográfico no garantiza comparabilidad eléctrica ni tendencias paralelas.

La muestra principal contiene 3 distritos tratados, 18 controles y 9 años: 189 observaciones únicas, representadas por 297 filas con copias. Colina-3 entra en 2021, Lampa-4 en 2022 y San Bernardo-11 en 2023. La corrección de Lampa desde 2023 y el cambio de universo de barras son posteriores al protocolo inicial; se conserva la fila con Lampa 2023 sobre la misma muestra. Las decisiones anteriores no se presentan como prerregistro de todos los análisis posteriores.

## Dos niveles de ponderación

1. **Copias del emparejamiento:** cada copia de un control repetido m veces recibe peso 1/m. La suma por distrito-año es uno. Se incluyen efectos fijos de unidad-copia y año, y errores agrupados por distrito.
2. **Agregación de efectos:** la principal promedia las celdas cohorte-año posterior. Hay un distrito en cada cohorte y cinco, cuatro y tres años posteriores observados, de modo que los pesos por cohorte son 5/12, 4/12 y 3/12. Un cálculo manual de cambios respecto de t = −1, netos del cambio medio de los 18 controles, coincide con el ATT de Sun y Abraham.

El contraste descriptivo de −0,08663 usa las mismas unidades y esos pesos por cohorte, sustituyendo el año de referencia por el promedio previo propio. Se calcula sobre distritos únicos (equivalente a neutralizar las copias); no vuelve a aplicar 1/m sobre datos ya deduplicados. No es un ATT causal corregido.

Los pesos anteriores no se extienden a toda la Tabla 1: cambiar Lampa a 2023 altera el número de años posteriores; excluir Lampa altera las cohortes disponibles.

## Inferencia y diagnóstico previo

Los intervalos son los convencionales de `fixest`, con agrupación por distrito y distribución t. Tres tratados no garantizan su cobertura nominal. La covarianza de los doce términos previos por cohorte tiene rango cinco; el test conjunto completo no es calculable. El p convencional de 6,2023 × 10⁻¹⁵ corresponde a tres promedios de horizontes comunes (−4, −3 y −2), con F(3,20) = 193,23035. La significación convencional no soluciona el problema de pocos tratamientos.

Los p de aleatorización de iteraciones antiguas no se trasladan al coeficiente actual. La evidencia de Lampa muestra un aumento previo mayor en controles; no demuestra selección por holgura ni reversión a la media como mecanismo causal.

## Comparación y horizonte 2030

El 2,49 de Virginia es una cifra publicada, no una reestimación con sus microdatos. Las variables eléctricas, mercados y covariables no son idénticos. Se documenta una adaptación de diseño y una comparación de mecanismos, no una réplica exacta de resultados.

Los 1.038 MW de la RM provienen de una nota de Systep que atribuye la proyección al Coordinador. La definición precisa de potencia no se recuperó. Las fracciones 60%, 80% y 100% son supuestos de sensibilidad; si la cifra representa potencia media, solo aplica 100%. No se extrapola el ATT por MW ni se deduce un incremento de tarifa o costo social. Las bases PET26 están inventariadas y extraídas; falta el contrafactual de despacho.
