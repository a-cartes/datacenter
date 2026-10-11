# Operación de red, flujos y cargas concurrentes

Registrado el 11 de octubre de 2026, antes de las nuevas estimaciones. Punto de partida: 690987f. Prioridad Energy Economics; SOCHER y bases previas se conservan.

## Pregunta

¿La asociación diurna de Las Canteras se mantiene al observar cargas concurrentes y estados operativos? El resultado previo orienta esta exploración; este documento no es un prerregistro externo ni transforma la carga observada en variación exógena.

## Fuentes y medición

- Mantener el panel horario agosto de 2024–agosto de 2026, sus zonas, comparadores y bloques 10–16, 19–23 y resto.
- Reextraer de tablas físicas verificadas los canales H1–H4 de Las Canteras, HT1–HT3, Tap Libertadores H1/H2 y Chacabuco LBR1/LBR2/LBR4. Agregar cuatro intervalos distintos válidos por hora; kWh/1000 produce MWh horarios y MW medios. Mantener D y R separados. No sustituir flujos por capacidad nominal ni llamar congestión a un percentil de flujo.
- Conciliar otros consumos con SIP solo en horas no ambiguas y coincidentes. Los canales de tránsito de Google no son automáticamente consumo; ninguna suma se acepta sin balance y respaldo de frontera. LBR se mantienen separados; no se les asigna operador por conveniencia econométrica.
- Buscar Registro de Instrucciones de Operación (RIO) para completar un calendario continuo. Guardar archivos nuevos, fechas de consulta, cobertura, versiones y hashes en esta etapa. Ausencia de descarga o de un registro no significa ausencia de restricciones. Corroborar clasificación con los tres días EAF ya revisados.
- Separar controles de transferencia/prorratas, indisponibilidades, ampliaciones y cambios de configuración. No extrapolar un evento a otro día sin continuidad documentada. No extender la restricción de Alto Jahuel–Lo Aguirre a todas las barras de comparación sin identificar su exposición.
- Si los portales bloquean la descarga, registrar enlace y obstáculo, avanzar con mediciones locales y explicitar el alcance parcial del calendario.

## Comparaciones previstas

1. Describir perfiles horarios, reversión de flujos, balances y cobertura mensual, antes de interpretar precios.
2. Reestimar la especificación de bloques con FE de día, mes×hora y hora de semana. Comparar, sobre idéntica muestra, modelo sin y con Google/Ascenty comerciales. En una muestra física más larga, usar solo fronteras conciliadas; si no se concilian, etiquetar como sensibilidad de canales, no control de consumo.
3. Reportar controles de flujos separadamente: pueden ser mediadores de la propia carga y su inclusión no estima el efecto total. Usar los cuatro canales individuales firmados, sin escoger signos por relación con precios. No introducir todos los balances redundantes a la vez.
4. Mantener ambos signos e intervalos; errores por scores semanales con HAC de cuatro rezagos, calendario semanal completo (semanas sin muestra con score cero), alternativa agrupada mensual. Reportar rango, variación residual y correlaciones. Ajustar Holm para diferencias solar–resto y tarde–resto por familia de resultados.
5. Solo estimar carga×restricción si existe cobertura documental suficiente y variación de carga en ambos estados; en caso contrario entregar el calendario con faltantes explícitos y los contrastes descriptivos disponibles. Nunca imputar cero a horas sin revisión.

Los cambios de especificación tras observar resultados se documentarán como adendas. Toda salida usa una carpeta nueva, con control de integridad de insumos antes/después; los resultados previos no se sobrescriben.
