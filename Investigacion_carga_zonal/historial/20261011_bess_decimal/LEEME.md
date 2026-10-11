# Historial de correcciones de procesamiento

- extraer_medidores_v1.py omitía declarar coma decimal en el resumen por canal. canales_v1_no_valido.csv.gz contiene concatenaciones de texto y no tiene uso analítico. El archivo de filas originales extraídas no se alteró; el resumen se regeneró con lectura numérica explícita antes de estimar.
- conciliar_bess_v1.py exigía90días sin componentes ausentes; se detuvo por tres horas incompletas. La versión vigente conserva todas las horas para conciliación y aplica días completos al soporte API.

Estas correcciones afectan derivados nuevos; no modifican archivos originales del Coordinador ni resultados anteriores.
