# Método y decisiones

[Inicio](../README.md) · [Datos](datos.md) · [Reproducción](reproducir.md)

## Pregunta de investigación

¿Cómo cambia el diferencial de costo marginal de una barra cuando entra o se amplía un centro de datos vinculado a ella, y cómo se distribuye ese cambio en otros nodos de la red?

El panel organiza las observaciones. El ATT es un efecto de interés. DiD escalonado, estudios de eventos y análisis de spillovers requieren definiciones y supuestos específicos. El tamaño de la base por sí solo no identifica esos efectos.

## Secuencia analítica

1. Acreditar la identidad del establecimiento y sus fases.
2. Distinguir entrada, ampliación, energización y traslado de suministro.
3. Validar la fecha y la vigencia del vínculo eléctrico con la barra de precios.
4. Conciliar reloj, unidades y polaridad de las mediciones.
5. Definir resultado, comparación, anticipación, ventanas y exposición a otras entradas.
6. Estimar efectos compatibles con ese diseño y documentar la incertidumbre.

Los hitos registrados son evidencia para los primeros pasos. No se convierten automáticamente en fechas de tratamiento. Las fases de un campus o los establecimientos que comparten nodo requieren considerar su dependencia.

## Registro de decisiones

Cada decisión tendrá un identificador, fuente y localizador, fecha o intervalo acreditado, vigencia, criterio, incertidumbre, responsable y referencia a la versión que modifica. La plantilla de incidencia «Validar centro, evento o barra» ayuda a reunir estos antecedentes; resolver una incidencia no modifica automáticamente el dataset.

Las reglas se fijarán antes de inspeccionar los efectos estimados. Un ajuste posterior conservará el motivo y la versión anterior. La comparación principal y las alternativas se distinguirán de los análisis exploratorios.

## Documentación completa

El [contrato para estimación](../SOCHER_2026_dataset/documentacion/Contrato_para_estimacion.md) contiene los requisitos del resultado, las cohortes, los comparadores y la exposición. El [registro del proceso original](../SOCHER_2026_dataset/documentacion/Reproducibilidad_y_plan_GitHub.md) documenta la construcción previa al empaquetado del repositorio; las instrucciones vigentes del paquete están en la [guía de reproducción](reproducir.md).
