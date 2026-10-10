# Cómo se construyó el análisis

La contribución empírica combina adquisición de precios, identificación eléctrica, reconstrucción documental de instalaciones y evaluación de un diseño econométrico. Esta secuencia permite revisar tanto lo que produjo resultados como lo que obligó a limitar su interpretación.

## De los originales al panel

1. Se recuperaron libros originales del Coordinador y se verificaron por SHA-256 o ETag. La réplica desde cero reutilizó originales, no las bases procesadas de investigaciones anteriores.
2. Se extrajeron precios horarios, factores y subsistemas. El cambio de publicación del 15 de julio de 2024 se trató explícitamente y se comprobó continuidad de horas, barras y niveles.
3. Se conciliaron identidades y tensiones, incluido Ñ/N y el alias de Lampa. Se georreferenciaron subestaciones y se relacionaron sus barras con distritos censales.
4. Se construyó el inventario de instalaciones y etapas a partir de SEA, Coordinador, operadores y otras fuentes. Los hitos separan apertura, energización, conexión, solicitud y ampliación.
5. Se generaron paneles y covariables censales; se compararon distrito, comuna y radios alrededor de nodos. Aumentar nodos expuestos no crea entradas independientes.
6. Se estimó la adaptación histórica, se revisaron sus supuestos y se conservaron las especificaciones anteriores.

## Cambios que importan para interpretar el resultado

El resultado inicial cercano a 1,32 correspondía a otro conjunto de decisiones sobre fecha, barras y controles. El cierre de SOCHER utiliza Lampa 2022 y barras incorporadas con cobertura anual suficiente. Por eso se reproduce una comparación con Lampa 2023 manteniendo constante la muestra, en lugar de atribuir toda diferencia entre iteraciones al cambio de fecha.

La auditoría anterior detectó una atribución incorrecta de un p de permutaciones. El cierre actual no reutiliza ese p. El registro conserva qué decisiones antecedieron a la estimación y cuáles fueron revisiones posteriores. La variante de controles lejanos o con correlación baja no se escoge por conseguir significación.

La revisión del año de referencia mostró que el diferencial relativo de Lampa era bajo porque los controles habían subido más. Se contrastó composición de barras, descomposición contable y precios horarios archivados. Eso sustenta un diagnóstico de fragilidad de identificación; no acredita una causa operativa específica del episodio.

Las conexiones de ST01, EdgeConneX y ST02 documentan diferencias entre hitos comerciales y eléctricos. No se asigna retroactivamente la potencia futura de conexión a toda la vida del edificio. Las solicitudes, los MVA de transformación y los MW informáticos no sustituyen retiros eléctricos medidos.

## Versiones y antecedentes

- `archivo/documentacion/`: ficha del artículo original, protocolo, decisiones, inventario, validación, auditoría y resultados anteriores.
- `archivo/scripts_originales/`: programas conservados del trabajo local; algunas rutas y dependencias requieren adaptación antes de ejecutarlos.
- `referencia/cierre_socher_20261009/`: diagnóstico final, correspondencia con Virginia y matrices de conexión/potencia.
- `archivo/prospectiva_documentacion/`: estado de las bases PET26, conciliaciones y requisitos de la simulación pendiente.
- Carpetas históricas v1–v8 en la raíz: investigación previa conservada. No son insumos procesados del cierre RM ni versiones intercambiables del manuscrito.

Los documentos históricos mantienen sus fechas y pueden contener cifras superadas. El punto de entrada vigente es `SOCHER_2026_RM/README.md`. No se presenta como un prerregistro retrospectivo ni se borran resultados desfavorables.
