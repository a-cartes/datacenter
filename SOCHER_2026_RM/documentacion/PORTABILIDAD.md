# Reproducción entre Mac y Linux

La primera ejecución pública en Linux detectó una diferencia respecto de las muestras históricas: el ordenamiento por distancia del puntaje probit no especificaba un desempate. Dos nodos ubicados en el mismo distrito tienen las mismas covariables censales; sus puntajes y distancias son iguales matemáticamente, aunque el cálculo matricial puede introducir diferencias en los últimos decimales. El orden de `quicksort` para empates puede depender de la arquitectura.

## Corrección y alcance

El programa activo ordena por distancia absoluta redondeada a doce decimales y, en caso de empate, por identificador alfanumérico ascendente. El redondeo se aplica al ordenamiento, no a precios, covariables, coeficientes ni puntajes guardados. Evita que diferencias de precisión matricial entre plataformas decidan entre covariables idénticas. Este criterio utiliza identificadores, no precios ni resultados posteriores. Se aplica a todas las variantes. El informe de cada emparejamiento registra ahora los pares y los candidatos empatados en el décimo puesto.

- En el radio de 2 km, los nodos 675 y 715, ambos de Renca-5, empatan en el corte. La regla explícita selecciona 675; la muestra histórica seleccionaba 715. Se mantienen diez controles únicos y dos tratados dentro del soporte. Cambia la composición eléctrica de esta alternativa: no se afirma equivalencia de sus resultados.
- En el radio de 3 km se reordenan copias de controles empatados; permanecen las mismas unidades y sus pesos.
- Las muestras distritales y comunales no cambian. Las seis especificaciones y las exclusiones que se reestiman para SOCHER usan muestras distritales. Sus resultados, la Tabla 1 y la Figura 1 siguen coincidiendo con las referencias anteriores.

Las muestras históricas se conservan intactas en `datos/analitico/`. Las dos muestras de radios con desempate explícito están en `referencia/emparejamiento_portable/`, con hashes propios. El verificador utiliza estas referencias para los radios y las originales para todas las demás variantes. La ejecución reconstruye las muestras en una carpeta separada; no reemplaza el archivo histórico.

También se corrigió una etiqueta del mecanismo de respaldo: `Probit.fit_regularized` aplica penalización L1, aunque el comentario antiguo decía L2. Se retiró el argumento inoperante `L1_wt`. Todas las variantes publicadas convergen por el probit ordinario; ese respaldo no se activa ni cambia estas estimaciones. Los programas archivados conservan la redacción original.

Esta revisión resuelve la reproducibilidad informática del emparejamiento. No modifica las limitaciones estadísticas, ni convierte el emparejamiento demográfico en una medición de comparabilidad eléctrica.
