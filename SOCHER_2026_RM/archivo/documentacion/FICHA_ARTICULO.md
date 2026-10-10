# Ficha del artículo original sobre centros de datos y precios eléctricos

Esta ficha resume el ejemplar aportado por el usuario de Mamkhezri, Sun y Yang, *The Hidden Cost of the Cloud: Data Centers and Transmission-Induced Electricity Prices*, fechado en marzo de 2026, SSRN 5736562. Todas las páginas citadas corresponden a ese PDF de 57 páginas. Los resultados aquí descritos pertenecen a Virginia.

Fuente local consultada: `<HOME>/Desktop/ssrn-5736562.pdf`. La ficha se elaboró el 1 de octubre de 2026 mediante lectura del texto y revisión visual de las páginas metodológicas y de las tablas 1, 2 y A.7.

## Pregunta y variable de resultado

La pregunta central es el efecto causal de demanda concentrada, representada por la entrada de centros de datos, sobre el componente espacial del precio mayorista atribuible a transmisión. El resultado principal suma congestión y pérdidas marginales de los precios nodales de PJM, expresadas en USD/MWh. El componente de energía es común entre nodos en cada instante (pp. 3 y 8 a 9).

La variable principal no es una tarifa residencial. El artículo reconoce que precios mayoristas y minoristas no se trasladan uno a uno (p. 17, nota 10).

## Datos y muestra

| Elemento | Especificación informada | Referencia |
|---|---|---|
| Precios | Precios nodales horarios en tiempo real y componentes de PJM Data Miner 2 | p. 9 |
| Período | 2015 a 2024 | p. 9 |
| Unidad principal | Sector censal por año | pp. 7 y 9 |
| Agregación | Promedios de precios nodales dentro del sector y promedios anuales; incorpora nodos nuevos | pp. 7 y 9 |
| Centros de datos | Ubicación y año operativo de Data Center Map, complementados con búsquedas de fechas | p. 9, nota 2 |
| Tratamiento | Primera operación en el sector; primeras entradas elegibles desde 2017 | pp. 9 y 12 |
| Exclusiones | Sectores con operación anterior a 2017 | p. 9 |
| Comparadores | Sectores sin entrada durante la ventana | p. 10 |
| Generación | Capacidad y localización de plantas de EIA Form 860 | p. 9 |
| Otras cargas | Instalaciones manufactureras del inventario TRI de EPA | p. 9 |
| Demografía | American Community Survey | p. 9 |

La tabla 1, p. 33, informa 20 sectores tratados y 449 controles antes del emparejamiento. Después quedan 19 tratados y 115 controles únicos. Con repetición por emparejamiento, los controles ocupan 190 posiciones. La tabla 2 informa 2.090 observaciones de sector por año. Las repeticiones no representan territorios independientes adicionales.

La mención narrativa de 19 tratados en p. 10 debe leerse junto con esos conteos: para distinguir antes y después del emparejamiento se utilizan los valores explícitos de la tabla 1.

## Emparejamiento y ponderación

El artículo estima un probit de la probabilidad de primera entrada durante 2017 a 2024. Utiliza población, porcentaje de residentes blancos, porcentaje con educación secundaria, ingreso mediano del hogar y viviendas, medidos en 2015 y 2016. Aplica diez vecinos más cercanos con reemplazo y excluye un tratado fuera del soporte común (pp. 10 a 11).

La regresión pondera cada copia de un sector por el inverso del número de veces que aparece en el conjunto emparejado. La nota de la tabla 2 precisa la frecuencia de duplicación de controles (pp. 11 y 34). No debe sustituirse esa regla por una ponderación proporcional a la frecuencia sin declarar el cambio.

Interpretación de la regla: si existen m copias idénticas y cada una pesa 1/m, el peso total de ese sector suma uno. Esto es coherente con que los coeficientes principales de la tabla A.7, panel D, coincidan con los de la tabla 2 al eliminar duplicados; los errores estándar sí difieren. La implementación y correcciones de inferencia requieren documentación propia.

## Estrategia de estimación

La especificación de referencia incluye efectos fijos de sector y año y un indicador que permanece activo desde la primera entrada. El estimador preferido es Sun y Abraham (2021). Presenta también efectos fijos de dos vías y Callaway y Sant’Anna (2021). El estudio de eventos utiliza el año anterior a la entrada como referencia. Agrupa los errores estándar por sector censal (pp. 11 a 12).

La figura 5 muestra los horizontes de cuatro años anteriores a cinco posteriores; agrupa los períodos más extremos y no los muestra (p. 29). Los horizontes utilizables en Chile dependerán del soporte de cada cohorte.

Los supuestos centrales son tendencias paralelas, ausencia de anticipación y ausencia de efectos sobre las unidades de comparación. El artículo reconoce que la interconexión eléctrica puede comprometer este último supuesto (pp. 12 a 13 y 18).

## Resultados de referencia

La tabla 2, p. 34, reporta efectos posteriores agregados de 2,4914 USD/MWh para congestión más pérdidas, 2,3173 para congestión y 0,1741 para pérdidas. Los errores estándar son, respectivamente, 1,2460; 1,2047; y 0,0531.

El texto describe el efecto conjunto como aproximadamente 70% del nivel previo (p. 13). Ese porcentaje se refiere al componente estudiado, no al precio mayorista total. La fórmula y población exactas de ese denominador deben verificarse si se pretende reproducir el porcentaje.

El efecto agregado no implica que todos los coeficientes del estudio de eventos sean significativos: el propio texto señala que los coeficientes posteriores individuales del resultado conjunto no lo son al 5% (p. 13).

## Robustez y análisis adicionales

Las pruebas de robustez incorporan capacidad de generación y número de instalaciones manufactureras; utilizan comparadores con baja correlación previa de precios; y cambian emparejamiento, ponderación y duplicación de controles (pp. 18 a 19; tablas A.6 y A.7).

Para exposición indirecta, el texto utiliza un umbral de correlación de 0,5 y reconoce su carácter arbitrario. Una baja correlación histórica no constituye por sí sola prueba de independencia eléctrica.

El original ya analiza distancia y tecnología de generación, horarios, estaciones, número de centros y características demográficas (pp. 14 a 17). Repetir esas dimensiones corresponde a reproducir análisis existentes; una extensión debe explicar qué añade.

## Detalles que requieren resolución antes de programar

1. Cómo combina las covariables de 2015 y 2016 en el probit, y qué reglas usa para empates y soporte común.
2. Reglas exactas de cobertura horaria, tratamiento de datos faltantes y orden de agregación de nodos y tiempo.
3. Implementación de la agrupación de extremos del estudio de eventos y ponderación de efectos agregados por cohorte y período.
4. Implementación de los pesos por duplicación y de las correcciones de los errores estándar.
5. Variable exacta usada para calcular correlaciones de comparadores: p. 18 menciona el componente conjunto, mientras la nota de A.7 menciona congestión; también debe resolverse cómo se aplica el umbral respecto de múltiples tratados.
6. Universo operativo de centros y tratamiento de cierres, reaperturas y fechas inciertas.

Estas cuestiones deberán buscarse en materiales de replicación, documentación adicional o aclaraciones de los autores. Mientras permanezcan abiertas, las decisiones propias se registrarán como tales. Esta ficha no acredita acceso al código o a los microdatos originales.
