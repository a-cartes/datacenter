# Diseño de la nueva estrategia zonal

Versión inicial, 11-10-2026. Propuesta para contrastar una hipótesis; todavía no ejecuta una nueva estimación de precios. Se conocen los resultados históricos: esta fecha no se presenta como preregistro del trabajo anterior.

## Pregunta y mecanismos

**¿Cómo cambia el costo marginal de las zonas eléctricamente expuestas cuando aumenta el retiro efectivo de centros de datos, y cómo depende esa respuesta de las restricciones y ampliaciones de la red?**

La secuencia a investigar es carga adicional → cambios de flujos, pérdidas y despacho → precios locales. Se estudiarán también cambios de punto de suministro: una transferencia puede alterar la exposición de una zona sin aumentar la demanda total del centro. Esa distinción evita interpretar una relocalización eléctrica como crecimiento neto.

## Panel y variables

La unidad básica será barra × hora, construida desde intervalos físicos. Se podrán producir agregados diarios o mensuales para el diseño estadístico, sin que más filas equivalgan a más tratamientos independientes. Se preservarán las horas observadas, cobertura y ausencia de datos.

La tabla de correspondencia tendrá: `sitio_id`, `etapa_id`, titular, empalme, `socket_id`, barra, tensión, canal/sentido, unidad, exclusividad, `vigente_desde`, `vigente_hasta`, fuente, evidencia de reloj y estado de validación. Las incertidumbres serán explícitas. Los registros futuros no se rellenan con carga solicitada.

- **Energía:** MWh retirados durante el intervalo. **Potencia media:** MWh divididos por duración en horas; kWh de un intervalo de 15 minutos divididos por 250 dan MW medios.
- **Carga directa:** suma de retiros de fronteras no superpuestas asignadas al sitio/zona, una vez acreditados sentidos y vigencia. D y R permanecen separados hasta definir retiro neto pertinente.
- **Capacidad:** MW solicitados, autorizados, energizados y TI en campos distintos. No se confunden con consumo ni se convierte MVA a MW sin factor de potencia válido. PUE se aplica solo si la magnitud de partida es TI y hay sustento.
- **Precios:** costo marginal P y diferencial D frente a Quillota 220 kV, con denominación y vigencia del nodo. Se mantiene la descomposición disponible en pérdidas y desacople, sin llamarla toda la congestión física.
- **Resultado zonal:** promedio de barras con composición/pesos fijados previamente, o regresión a nivel de barra con exposición zonal. Ponderaciones contemporáneas de consumo podrían cambiar mecánicamente al entrar el centro; se evita esa mezcla.

## Definir zonas antes de mirar sus efectos

El punto de partida es el grafo existente, contrastado con actas, circuitos, transformación y restricciones documentadas. Las zonas deben representar alimentación y cuellos de botella relevantes en cada régimen de red. Las obras y cambios de configuración generan regímenes explícitos, no agrupaciones elegidas para maximizar el coeficiente.

Para cada barra se separan exposición directa y exposición indirecta a cargas conectadas en otras barras. Una distancia geográfica grande no garantiza ausencia de exposición. Una matriz de admitancias o factores de sensibilidad calculados sobre una red validada pueden ayudar a definir pesos eléctricos; el catálogo actual no basta para afirmar independencia histórica de los controles.

La holgura se define respecto de equipos, flujos y límites operativos pertinentes, incluida seguridad N−1 cuando aplique. Se usará holgura **previa** para estudiar heterogeneidad; la congestión observada o una ampliación inducida por el centro son posibles mecanismos posteriores y no controles automáticos del efecto total.

## Secuencia de estimación

**1. Validación de carga y etapas.** Reconciliar las fuentes por fronteras y días; describir rampas y transferencias. Examinar cambios de retiros frente a patrones estacionales y horarios. Los cambios detectados estadísticamente no sustituyen evidencia documental de energización ni permiten escoger fechas según la respuesta del precio.

**2. Relación zonal de carga y precio.** Explorar P y D frente a retiro medido, exposición indirecta y régimen de red. Una especificación de diagnóstico puede ser:

`P_bt = α_b + λ_t + β L_bt + θ E_bt + γ X_bt + ε_bt`

L es carga directa; E, exposición a carga digital en otras conexiones; X, factores relevantes no inducidos por el tratamiento. Efectos temporales comparan zonas en la misma hora o período. β se reporta inicialmente como asociación condicional: carga y precio pueden responder simultáneamente a decisiones operativas o shocks comunes. Con efectos temporales, el efecto uniforme sobre todas las zonas queda absorbido; β no es el efecto nacional total.

**3. Identificación según los casos que sobrevivan la validación.** Evaluar entradas/etapas documentadas, rampas y comparación con zonas de evolución previa razonable. Una energización no es exógena automáticamente: puede coincidir con obras o responder a holguras. Explicar qué variación identifica cada estimación. Si interesa el efecto conjunto de carga y conexión, definirlo así; separarlos exige variación adicional.

Un tratamiento continuo requiere su propio estimador y supuestos sobre selección en dosis; no basta sustituir la variable binaria dentro de Sun–Abraham. Se evaluará DiD continuo, o estudios de eventos por etapas con cambios de carga medidos como validación/intensidad. No se inventará un instrumento a partir de potencia solicitada o fecha administrativa: su exclusión necesita justificación independiente.

**4. Contrastar heterogeneidad.** Explorar si la respuesta aumenta cuando la red tenía menor holgura previa, en horas de mayor presión o durante regímenes de restricción documentados. Un efecto mayor es una hipótesis; no se impone que solo estos coeficientes puedan ser significativos. Separar pruebas previstas de exploratorias.

**5. Contrafactual estructural futuro.** PET26 y PowerFactory pueden sostener escenarios con/sin carga digital bajo la misma oferta y red, después de implementar y validar el modelo. Es un ejercicio condicionado por supuestos, distinto del efecto histórico identificado. No se presenta como ejecutado ni se multiplica el ATT histórico por MW futuros para predecir precios.

## Inferencia y controles de robustez

- Número de unidades independientes definido por conexiones/eventos y exposición compartida, no por horas, sockets o copias de controles.
- Comparabilidad eléctrica y trayectoria previa evaluadas conjuntamente. Conservar alternativas de controles y mostrar cambios, sin seleccionar por signo o p favorable.
- Buscar suficiente período previo y posterior por caso; una referencia práctica inicial es al menos 12 meses previos para describir estacionalidad y, cuando exista, 24. La disponibilidad efectiva puede obligar a un estudio de caso con alcance menor.
- Comparar cada cohorte con referencia previa explícita; retener especificación histórica sin modificarla. Un test de pre con poca potencia no certifica tendencias paralelas.
- Con pocas zonas tratadas, intervalos convencionales son insuficientes. Inferencia por aleatorización requiere un mecanismo defendible de asignación/intercambiabilidad; bootstrap no crea eventos nuevos. La sensibilidad a tendencias puede aportar bajo sus condiciones y con inferencia compatible. Si esos requisitos no se cumplen, informar rangos descriptivos y límites del diseño.
- Placebos temporales y espaciales, exclusión de cada conexión, otras cargas relevantes y obras coincidentes. No sumar controles posratamiento que eliminen el mecanismo a medir.

## Entregables siguientes, en orden

1. Correspondencia documentada de Las Canteras, ST01 y ST02, con versiones de frontera y cronología.
2. Conciliación física–comercial en todas las fechas disponibles y extracción dirigida de ventanas faltantes.
3. Catálogo de zonas/regímenes y panel de carga con cobertura; cierre del reloj para precios.
4. Informe descriptivo de carga–precio y evaluación de diseños de identificación viables por caso.
5. Solo entonces, nueva estimación con tabla de comparabilidad respecto de la réplica y especificaciones registradas antes de ejecutarlas.

## Referencias metodológicas

- [Sun y Abraham, estimación de eventos con heterogeneidad del tratamiento](https://arxiv.org/abs/1804.05785).
- [Callaway, Goodman-Bacon y Sant’Anna, diferencias en diferencias con tratamiento continuo](https://www.nber.org/papers/w32117).
- [Butts, diferencias en diferencias con efectos espaciales indirectos](https://arxiv.org/abs/2105.03737).

Estas referencias orientan el diseño; no sustituyen la validación de la conexión ni justifican por sí mismas una atribución causal en esta muestra.
