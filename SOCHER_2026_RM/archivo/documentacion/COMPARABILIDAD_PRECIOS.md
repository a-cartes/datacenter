# Comparabilidad de precios eléctricos entre PJM y Chile

Fecha de revisión: 1 de octubre de 2026. Evaluación desde fuentes primarias; no utiliza resultados de la investigación anterior. Es una nota metodológica, no una estimación de efectos.

**Conclusión provisional:** existe una base institucional para estudiar diferencias espaciales de costos marginales y su relación con pérdidas y restricciones de transmisión. Todavía no está acreditada una serie chilena directamente equivalente al componente conjunto utilizado en el artículo. Esto exige validar la medición, pero no descarta la réplica. Tampoco permite llamar automáticamente «congestión y pérdidas» a cualquier diferencia entre barras.

## Qué significa la variable de PJM

PJM distingue precio de energía del sistema, congestión y pérdidas dentro del precio marginal local (LMP). El manual consultado es la revisión 137, vigente desde el 28 de julio de 2026; sirve para definir conceptos actuales, no para certificar todas las reglas del período histórico del artículo. [PJM, Manual 11, apartados 1 y 2.2](https://www.pjm.com/-/media/DotCom/documents/manuals/m11.pdf).

La documentación del monitor independiente de PJM de 2020 explica que la referencia es ponderada por carga y puede variar con su distribución; los componentes de congestión pueden ser positivos o negativos. Por tanto, «sin componente energético» no significa un costo físico total independiente de la convención de referencia. [Monitoring Analytics, pp. 1–4](https://www.pjm.com/-/media/DotCom/committees-groups/task-forces/afmtf/2020/20200722/20200722-item-03a-constraint-based-congestion-calculations.ashx).

Con notación propia, la identidad relevante es:

\[
P_{it}=E_t+C_{it}+L_{it},\qquad Y_{it}=C_{it}+L_{it}=P_{it}-E_t.
\]

Aquí la energía es común a los nodos del mismo sistema e instante bajo esa descomposición. No debe sustituirse por el precio total de cualquier nodo sin explicar la normalización.

## Qué establece el marco chileno

La norma de agosto de 2021 define el costo marginal por barra incorporando las limitaciones de transmisión y, cuando corresponde, racionamiento. Los factores de penalización representan pérdidas marginales relativas a una referencia. El artículo 2-23 lleva el costo de referencia a las demás barras mediante esos factores; el 2-20 exige costos diferenciados por subsistema ante desconexiones o congestiones que limiten intercambios. También contempla ponderaciones por minutos cuando un subsistema comienza o termina dentro del intervalo. Los artículos 2-24 y 2-25 distinguen factores programados y reales; el 2-26 exige registrar condiciones especiales junto con los precios. [CNE, NT de Coordinación y Operación, arts. 1-4, 2-3 y 2-20 a 2-27](https://www.cne.cl/wp-content/uploads/2021/08/NT-de-Coordinacion-y-Operacion-del-SEN.pdf).

La minuta operativa del Coordinador, versión 2 de enero de 2025, añade detalles decisivos: calcula sensibilidades de pérdidas con el estado de la red, normaliza los factores respecto de **Quillota 220 kV**, completa barras no modeladas y homologa nombres. Contempla ajustes para que el precio de la central térmica marginal coincida con su costo variable y, justificadamente, referencias locales dentro de subsistemas. Los factores diarios se publican en versiones preliminar y definitiva. Por eso, una fórmula única aplicada mecánicamente a todos los intervalos puede ser incorrecta. [Coordinador, Factores de Penalización Reales, pp. 6–10](https://www.coordinador.cl/wp-content/uploads/2025/01/Factores_de_Penalizacion_Reales_V2_20253001.pdf).

## Alcance de una diferencia respecto de Quillota

La siguiente es una deducción metodológica propia, no una descomposición publicada por el Coordinador:

\[
D_{it}=P_{it}-P_{rt}.
\]

Incluso si Chile admitiera exactamente la descomposición de PJM, esa diferencia sería:

\[
D_{it}=(C_{it}+L_{it})-(C_{rt}+L_{rt}).
\]

Es una diferencia **relativa**. No identifica por sí sola el componente del nodo tratado. Quillota tiene respaldo como referencia operacional, pero eso no prueba que su precio sea equivalente al componente energético común de PJM. Si se quisiera separar pérdidas y congestión, habría que reproducir el algoritmo efectivamente utilizado, identificar subsistemas y sus referencias, y comprobar la conciliación con los precios publicados. No se ha realizado todavía esa reconstrucción.

Hay un matiz econométrico favorable a la réplica: en una regresión lineal con efectos temporales completos, restar a todas las unidades una misma serie \(B_t\) no cambia el coeficiente del tratamiento, manteniendo iguales muestra, pesos y demás regresores, porque el ajuste queda absorbido por esos efectos. Lo mismo ocurre con diferencias contemporáneas entre tratados y controles que eliminan esa serie común. La propiedad exige igual referencia, frecuencia y transformación para todos; no se traslada automáticamente a logaritmos, porcentajes, referencias distintas por zona o agregaciones incompatibles. Por ejemplo, coberturas horarias distintas pueden hacer que la referencia anual efectiva deje de ser común. Esta invariancia permite estudiar contrastes locales sin presentar una normalización como un componente observado. Tampoco identifica un aumento común de precios de todo el sistema.

## Versiones y quiebres que debemos documentar

El catálogo actual de la CNE sigue enlazando, para costos marginales y transferencias, el texto de agosto de 2021 y la Resolución 253/2021. Eso respalda su uso como marco localizado, sin demostrar por sí solo que no existan modificaciones pertinentes. [Catálogo oficial CNE](https://www.cne.cl/normativas/electrica/normas-tecnicas/).

Existe además el Decreto 32, publicado el 17 de junio de 2026, que modifica el Decreto 125. Sus cambios relacionan el cálculo con herramientas automáticas de despacho; el primer transitorio concede 36 meses para implementarlas y mantiene el listado de prioridad mientras no operen. No debe fecharse un cambio efectivo de método solo con la publicación del decreto. [Ministerio de Energía, Decreto 32, art. primero, numerales 73 y 97, y primer transitorio](https://www.bcn.cl/leychile/navegar?idNorma=1225248).

El Coordinador sí identifica un cambio de publicación/utilización de series el **15 de julio de 2024**: separa el histórico anterior del costo marginal real nuevo. Distingue real, preliminar, en línea y programado; informa además una hora adicional por cambio horario disponible únicamente en el TSV. Estos antecedentes obligan a revisar continuidad, revisiones y calendarios antes de concatenar datos. [Coordinador, Costos Marginales](https://www.coordinador.cl/costos-marginales/).

## Decisión para la réplica base

Mantener abierta la variable final y realizar un piloto de conciliación: seleccionar barras e intervalos, reunir costo real, factores definitivos, subsistemas, unidades marginales y reglas de cálculo; contrastar identidades en períodos normales y desacoplados. El registro de cada observación debe preservar versión y metodología. Primero debe demostrarse qué variación espacial captura el precio; después se fijará su nombre y se estimará el efecto.

Si solo se puede validar un resultado relativo, corresponde describirlo como **diferencial espacial de costos marginales**, conservando la estrategia causal de la réplica y explicando la adaptación de medida. No es necesario inventar una extensión para ocultar esta diferencia institucional. Las conclusiones quedarían referidas al precio mayorista local relativo y no, automáticamente, a tarifas finales, rentas de congestión o costos totales del sistema.
