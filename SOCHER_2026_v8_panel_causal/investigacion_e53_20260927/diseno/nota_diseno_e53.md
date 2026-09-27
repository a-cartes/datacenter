# E53: identidad, exposición, concurrencias y alcance del contraste

Fecha: 27 de septiembre de 2026. Revisión documental iniciada antes de recibir los contrastes E53; la sección de reproducción se añadió después de conocerlos. No es un prerregistro. No modifica el protocolo v8, la matriz publicada ni la entrega v0.2.0. Las recomendaciones sobre nuevos estimandos requieren una adenda explícita.

## Decisión de diseño

La energización del alimentador E53 es un objeto de intervención específico que puede analizarse como **conexión eléctrica**, aunque todavía no se haya demostrado que incorpora demanda neta nueva. La fecha de realización del 5 de mayo de 2025 está respaldada por la carta de término STM (S003 v8). El día completo convencional continúa siendo **g = 6 de mayo de 2025**. Esto no convierte la fecha en inicio de operación del centro de datos ni acredita cuánto consumo empezó ese día.

Conviene conservar ahora el contraste descriptivo de **Chacabuco 110 kV frente a Quillota 110 kV**, con Quillota 220 y los niveles como complementos; ventana previa 14 de enero–28 de abril de 2025, anticipación 29 de abril–5 de mayo, y posterior 6 de mayo–3 de agosto. La base dinámica g−8 es el 28 de abril; el resumen descriptivo de la adenda compara medias de ventanas, por lo que no debe confundirse con el ATT(g,t) anclado a esa base. Ninguna comparación habilita hoy la palabra causal.

## Qué identidad queda cerrada

La revisión del archivo horario anual 2025 congelado identifica **4.849 filas de metadatos** para Chacabuco entre el 14 de enero y el 3 de agosto. Las ocho particiones mensuales publican el mismo ID_INFO **703** y el mismo nombre **BA S/E CHACABUCO 110KV BP1**; no hay conflicto. La consulta pública Infotécnica de 27 de septiembre de 2026 devuelve para 703 el nemotécnico **BA01T0835SE009T0835**. La correspondencia de la barra moderna en esta ventana está documentada y no necesita cruzar el cambio de régimen de julio de 2024. Véanse `identidad_chacabuco_2025.csv`, `validacion_identidad.json` y [API de la barra](https://api-infotecnica.coordinador.cl/v1/barras/703/).

Esto certifica identidad publicada del resultado y enlace actual de identificadores, **no la configuración operativa de todos los interruptores durante ocho meses**. El plano DUF NUP5417 existente muestra E53→BP7 23 kV→T7→BP1 110 kV, y distingue T1 en BP1 de T4 en BP2. Su condición nominal debe conservarse. No hay fundamento para tratar Chacabuco 12/23/110 kV como tres asignaciones independientes.

## Exposición y comparadores

El DUF NUP5417 rotula aguas arriba los circuitos Cerro Navia–San Cristóbal. La minuta CEN de Punta Verde, fechada 25 de julio de 2025, presenta el corredor Cerro Navia–El Salto y un esquema que contiene Lo Boza, Quilicura, Chacabuco, Recoleta y San Cristóbal. La figura 4-2 es un escenario de **2027**, con obras propuestas diferenciadas; sirve para corroborar pertenencia nominal al corredor, no como estado operativo observado en mayo de 2025. No se convierte esa figura en una matriz numérica de sensibilidad eléctrica. [Minuta CEN, pp. 4, 6, 12–14](https://www.coordinador.cl/wp-content/uploads/2025/07/Minuta_Solicitud_Nueva_Subestacion_Seccionadora_Punta_Verde_110_kV-V2.pdf).

Por tanto, Cerro Navia 110, Quilicura 110, Recoleta 110 y El Salto 110 pueden describir un **perfil de respuestas dentro del corredor**. No deben nombrarse controles no expuestos. La pertenencia al corredor no prueba igual exposición, ni intensidad o signo de spillovers. Tampoco se deduce que Quillota esté libre de efectos. El archivo `exposicion_nominal.csv` conserva el alcance documental y los desconocidos.

Para una intervención concreta E53, haber abastecido previamente otro centro de datos **no excluye automáticamente** una barra comparadora. Importan la estabilidad de su trayectoria y los cambios simultáneos relevantes para ese estimando. La exclusión de unidades ya tratadas es adecuada para primera adopción absorbente; trasladarla sin más a una conexión específica sería una restricción distinta e innecesaria. Del mismo modo, ausencia de un centro en un catálogo no demuestra ausencia de cambios durante la ventana.

## Un efecto relativo no exige exposición cero en todo el SEN

Sea A la activación de la intervención E53 y P_b,t(A) el precio nodal que resultaría bajo esa decisión, dejando que el resto del sistema responda. Defínase τ_b,t = E[P_b,t(1)−P_b,t(0)]. Para una referencia r, el efecto relativo de la intervención es θ_b,r,t = τ_b,t−τ_r,t. Este parámetro incluye la respuesta de ambos nodos a la misma intervención; no es el efecto directo de tratamiento propio manteniendo fija la exposición de todos los demás.

La diferencia observada del diferencial entre t y una base previa identifica θ_b,r,t solo si, además de consistencia y anticipación acotada, el **cambio contrafactual del diferencial sin E53 es cero en esperanza** (o se modela justificadamente), no existen intervenciones diferenciales omitidas confundidas con E53 y la trayectoria de la intervención está bien definida. Para comparar medias de ventanas, la condición debe formularse sobre esos promedios y la selección de días. La exposición de r puede ser distinta de cero: forma parte de θ. Para reinterpretar el mismo contraste como τ_b,t habría que añadir τ_r,t = 0, restricción que hoy no está acreditada.

No es necesario demostrar W=0 para toda la red para definir θ; sí debe evitarse que la etiqueta de causalidad o de efecto total encubra un supuesto sin defender. El efecto relativo no entrega impacto agregado del SEN, bienestar, efecto por MW ni separación entre consumo informático y obra de conexión. La discusión metodológica de spillovers advierte precisamente que resultados afectados del grupo comparador alteran la interpretación del DiD convencional. [Butts, versión 5 de diciembre de 2024, §§2–3](https://www.kylebutts.com/files/Spillover.pdf).

Con una sola asignación E53, las muchas horas, barras y semanas no multiplican eventos independientes. El análisis actual no habilita p-valores por agrupar horas ni permutaciones de barras sin un mecanismo de asignación. Los diagnósticos de tendencia previa pueden informar compatibilidad, pero no certificar tendencias contrafactuales.

## Concurrencias documentadas y cómo tratarlas

La búsqueda no es un censo completo de maniobras enero–agosto. Los registros que siguen son evidencia positiva; la falta de otros hallazgos no acredita una ventana libre de intervenciones.

| Fecha | Registro | Alcance | Decisión actual |
|---|---|---|---|
| 25–26 febrero | Acta extraordinaria CEN 3/2025, p. 2 | Apagón sistémico; recuperación completa declarada el 26 a las 09:31 | Conservar principal; sensibilidad documental conjunta de ambos días |
| 19 abril | EAF178/2025, pp. 1, 8–9, 16 | Falla en Lautaro y protección de respaldo CT1; 17,28 MW desconectados en Chacabuco 12 kV BP1 | Marcar en cronología; no eliminar según precios |
| 20 abril | EAF178/2025, p. 9 | Pruebas y reinicio de protección del alimentador Lautaro | Marcar; no atribuir a E53 |
| 26 abril | EAF190/2025, pp. 1, 6, 9 | Falla en San Ignacio; 28,59 MW de consumo desconectados; barra 12 kV BP1 | Marcar; la falla de 12 kV no demuestra corte en BP1 110 kV |
| 4 mayo | EAF190/2025, p. 9 | Pruebas y mantenimiento del mecanismo de San Ignacio | Ya cae en anticipación excluida; no cambiar g |
| 26 julio | Informe Diario anexo al EAF337/2025, portada p. 94 y observaciones p. 116 | 18:55 interrupción de 23 MW por error operacional; 18:57 recuperación; 23:00 CT1 indisponible y consumos transferidos a T4 | Concurrencia post t=81; marcar, no excluir ad hoc; falta cierre de duración de transferencia |

[Acta CEN 26 de febrero](https://www.coordinador.cl/wp-content/uploads/2025/02/Sesion-Extraordinaria-N%C2%B03-2025-26-febrero-2025.pdf), [EAF178](https://www.coordinador.cl/wp-content/uploads/2025/05/EAF-178-2025.pdf), [EAF190](https://www.coordinador.cl/wp-content/uploads/2025/05/EAF-190-2025.pdf), [EAF337, anexo diario](https://www.coordinador.cl/wp-content/uploads/2025/08/EAF-337-2025.pdf).

El EAF337 tiene como asunto principal una falla Itahue–Talca: el hecho Chacabuco proviene de su **anexo diario**, no de la carátula de ese EAF. La transferencia de T1 a T4 merece seguimiento porque el DUF nominal sitúa esos transformadores en distintas barras de 110 kV. No se ha probado que modificara el diferencial ni por cuánto tiempo permaneció. Punta Verde/SCL4 es una propuesta para 2027–2028 y no se registra como entrada realizada de 2025.

## Reproducción independiente y lectura de resultados

`verificar_contrastes_independiente.py` recalcula los 25 resúmenes de la adenda desde el **CSV horario anual 2025 congelado**, usando las filas originales de Chacabuco y de cada Quillota. No lee el panel diario ni los diferenciales precalculados. Exige 24 etiquetas únicas, precios finitos y conjuntos horarios idénticos para las tres barras. Compara con la salida principal solo después del cálculo independiente.

Resultado: **PASS**, discrepancia máxima 4,88×10⁻¹¹ por redondeo. La muestra principal comprende 104 días previos y 90 posteriores. El 5 de abril contiene 25 etiquetas en las tres barras y queda documentado fuera de la muestra principal.

| Resultado | Cambio media post90 menos media pre | Sensibilidad post28 |
|---|---:|---:|
| Precio Chacabuco 110 | +16,573171 USD/MWh | −7,227934 USD/MWh |
| Diferencial con Quillota 110 | +0,993893 USD/MWh | +0,236594 USD/MWh |
| Diferencial con Quillota 220 | +0,716359 USD/MWh | +0,017238 USD/MWh |

El aumento de nivel de 90 días coincide principalmente con un movimiento de las referencias: Quillota 110 sube 15,579278 USD/MWh. Ello impide presentar los 16,57 como efecto local de E53. El contraste a 28 días es considerablemente menor y el nivel cae: no procede ocultarlo ni describir un salto persistente demostrado desde la conexión. Las dos referencias son resultados relacionados; no son dos réplicas independientes. Estos son resultados cuantitativos verificables y potencialmente útiles para orientar mecanismos, pero **no son estimaciones de impacto causal, ni evidencia de significación estadística**.

## Trabajo siguiente que cambia la identificación

1. Cerrar campus/fase y trayectoria efectiva de la conexión para distinguir capacidad habilitada, toma de carga y suministro previo. La definición de conexión evita exigir aumento neto, pero no elimina la necesidad de definir qué se activó y qué otros cambios formaron parte del episodio.
2. Recoger maniobras y vigencia de Chacabuco BP1/BP2, en particular normalización de IF2025004841, y revisar cambios contemporáneos de los comparadores propuestos sin mirar qué selección produce mayor efecto.
3. Justificar una tendencia contrafactual del diferencial mediante historia previa dentro del régimen moderno y condiciones de oferta predeterminadas. Si no puede sostenerse, conservar el estudio del episodio como descriptivo y fortalecer otros eventos.
4. Registrar cualquier diseño relativo causal como objeto distinto del ATT de primera entrada. No reetiquetar retrospectivamente la tabla descriptiva como causal por su signo o tamaño.

Archivos de trazabilidad: `fuentes_diseno.csv`, `concurrencias_2025.csv`, `exposicion_nominal.csv`, los dos scripts, sus CSV/JSON y el manifiesto SHA-256 de las fuentes descargadas. Los textos e imágenes de `validacion/` son auxiliares de lectura; los PDF originales están en `fuentes/`.
