# Generación y maniobras: protocolo de la etapa

Registro previo a descargar las series y estimar los nuevos modelos. Punto de partida: 9fdf14e. Se conocen las asociaciones horarias anteriores; esta investigación es exploratoria, no una prueba confirmatoria independiente.

1. Conservar panel, frontera HT1+HT2, cinco resultados, comparadores, bloques 10–16 y 19–23, efectos fijos día, mes×hora y hora de semana. No modificar originales ni cierre SOCHER.
2. Obtener generación efectiva de PFV Santiago Solar y PFV Don Humberto del CEN, separada de instrucciones de despacho, potencia disponible y almacenamiento. Verificar identificador, nombre, unidad, hora, duplicados y cobertura. No imputar generación cero a faltantes. Archivar respuestas y hashes sin credenciales.
3. Comparar sobre exactamente las mismas horas: modelo con proxy Google; agregar ambas generaciones separadas; agregar sus cuadrados como sensibilidad a no linealidad. La generación contemporánea puede responder al despacho y a la propia restricción: estos ajustes identifican asociaciones condicionales, no efectos causales por sí solos.
4. Mantener días completos; presentar ambos subperíodos anuales (agosto 2024–julio 2025 y agosto 2025–agosto 2026), desfases de generación ±1 hora como sensibilidad de alineación y exclusión de las fechas con maniobras locales documentadas. No escoger el modelo por significación ni por signo. Si falta soporte o rango, declararlo.
5. Inferencia con scores semanales HAC4 sobre calendario completo; alternativa agrupada por mes. Ajustar Holm las diferencias solar−resto/tarde−resto entre especificaciones principales para cuatro diferenciales de comparación. Los intervalos son aproximados, no remedian endogeneidad.
6. Examinar el episodio 22-01-2025 y las menciones 06-03-2025 y 11-02-2026; distinguir horario programado, maniobra efectivamente ejecutada e intervalo de restricción. Ceros físicos no certifican desconexión. Las fechas se excluyen solo como sensibilidad, no para fabricar un grupo sin restricciones.
7. Presentar perfiles generación/carga/flujos y diagnósticos de soporte. Los flujos H1–H4 se usan para el mecanismo, no como controles causales preferidos, dada su dependencia casi algebraica del consumo local.
8. Documentar verificaciones, resultados completos y limitaciones; código y derivados separados, con registro de cambios. Toda modificación adicional se declara como adenda posterior.

## Adenda previa a las regresiones

La consulta documental identifica BESS Don Humberto separado de la central fotovoltaica, con identificador de central nulo en la API. Se conserva una consulta diaria de sus retiros e inyección para verificar esa separación; las series fotovoltaicas no representan inyección neta del conjunto PV+BESS. La búsqueda identifica además dos fallas de los circuitos Cerro Navia–Las Canteras el 26-02-2025 (EAF092/093). Se agrega esa fecha a una sensibilidad separada, conservando la exclusión de las tres fechas originales. Estas adiciones anteceden a conocer los coeficientes de generación.

La consulta larga entrega solo la medianoche del último día: se excluirá ese día incompleto conservando la misma muestra para los modelos comparados. Se retirarán duplicados exactos únicamente en derivados y las fechas de transición horaria ya excluidas por el panel anterior. No se completarán series con ceros.

La primera ejecución se detuvo antes de regresiones: la API fecha la hora25 del cambio de otoño como 06-04-2025 00:00, junto a la hora1 regular. Esa fila especial se conserva en auditoría y se excluye del enlace; no se elimina la hora1 regular ni se traslada la hora25 por suposición. V1 y su código se archivan; V2 aplica este criterio a las dos centrales. Los 46 duplicados exactos del 31-12-2025 se conservan en una tabla de auditoría.
