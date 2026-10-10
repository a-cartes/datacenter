# Reproducción del cierre SOCHER 2026

Este paquete reproduce el análisis histórico del resumen **¿Dónde se conecta la inteligencia artificial? Centros de datos y costos marginales eléctricos en la Región Metropolitana ante el horizonte 2030**. Parte de paneles derivados congelados y vuelve a construir las muestras y el emparejamiento, estima los modelos y regenera la Tabla 1, la Figura 1, las tendencias previas y la sensibilidad energética.

El cierre corresponde al 9 de octubre de 2026. La estimación principal es **1,05263 USD/MWh**, cae a **0,03273** al excluir Lampa y el contraste contra el promedio previo completo es **−0,08663**. La sensibilidad a controles, fechas y trayectoria previa impide una atribución causal robusta. Los escenarios contrafactuales PET26 siguen pendientes; la cuenta hacia 2030 es una sensibilidad aritmética.

## Ejecutar

Requiere Python 3.13 y R con `fixest`, `data.table` y `jsonlite`. Desde la raíz del repositorio:

```bash
python3 -m venv .venv-socher
source .venv-socher/bin/activate
python -m pip install -r SOCHER_2026_RM/requirements-lock.txt
Rscript SOCHER_2026_RM/scripts/instalar_R.R
python SOCHER_2026_RM/scripts/reproducir.py
```

En Windows, active el entorno con `.venv-socher\Scripts\activate`. El programa usa `Rscript` del PATH; puede definir `RSCRIPT` con su ubicación. La instalación de dependencias necesita internet; la ejecución analítica no descarga fuentes.

Las salidas quedan en `SOCHER_2026_RM/salidas/reproduccion/`:

- `tabla_1.csv`: cuatro filas, coeficientes e intervalos convencionales.
- `figura_1.png`: Lampa y sus mismos controles, y diferencia entre ambos.
- `sensibilidad_2030.csv`: equivalencias de potencia, energía y valoración hipotética.
- `verificacion.json`: controles, cifras, versiones y resultado de cada etapa.
- `trabajo/resultados/`: modelos completos, estudios de eventos y diagnósticos.
- Seis registros de ejecución que permiten localizar cualquier fallo.

La ejecución no sobrescribe una salida existente. Para repetir, use `--salida /ruta/a/otra/carpeta`. Para comprobar solo hashes sin instalar dependencias estadísticas:

```bash
python SOCHER_2026_RM/scripts/reproducir.py --solo-integridad
```

## Qué puede comprobarse

| Alcance | Estado del paquete |
|---|---|
| Integridad de los insumos publicados | SHA-256 y tamaños en `procedencia/manifest.json` |
| Emparejamiento y muestras | Se reconstruyen desde paneles, covariables e historias; se comparan con las muestras congeladas |
| Tabla 1, figura y pretendencias | Se reestiman con R y Python, con comprobaciones independientes de agregación |
| Inventario y conexiones | 63 registros, 138 hitos y 65 fuentes; matrices y procedencia consultables |
| 96 precios de agosto de 2021 | Se contrastan valores archivados contra el extracto horario; el programa público no relee el XLSM original |
| Descarga y extracción de todos los originales | Código, manifiestos y orden histórico conservados; requiere obtener fuentes externas, algunas manualmente |
| Simulación con y sin expansión digital en 2030 | Pendiente; no se presenta como resultado reproducido |

## Leer la evidencia

- [Cómo se llegó al análisis actual](documentacion/TRAZABILIDAD.md).
- [Mapa de afirmaciones, insumos y resultados](documentacion/MAPA_RESULTADOS.md).
- [Definiciones y ponderaciones](documentacion/METODO.md).
- [Reconstrucción desde originales y sus límites](documentacion/FUENTES_Y_RECONSTRUCCION.md).
- [Registro original de decisiones](archivo/documentacion/REGISTRO_DECISIONES.md).
- [Auditoría de la réplica anterior](archivo/documentacion/AUDITORIA_REPLICA.md).
- [Informe del cierre de Lampa y controles](referencia/cierre_socher_20261009/INFORME_CIERRE.txt).
- [Conexiones y potencia por etapa](referencia/cierre_socher_20261009/matriz_conexiones_potencias.csv).
- [Correspondencia con Virginia](referencia/cierre_socher_20261009/correspondencia_virginia.csv).
- [Manuscrito revisado por los autores](manuscrito/Resumen_extendido_Alan_Cartes.docx) y [PDF de consulta](manuscrito/Resumen_extendido_Alan_Cartes.pdf).

`referencia/` contiene los resultados congelados contra los que se contrasta cada ejecución. `salidas/` contiene lo recién calculado. `archivo/` conserva documentación y programas históricos, con rutas personales sustituidas por marcadores: no es el punto de entrada ejecutable del paquete actual. Los datos fuente y el trabajo de versiones anteriores del repositorio no se mezclan automáticamente con esta muestra 2017–2025.

Autoría del manuscrito aportado: **Alan Cartes, Ricardo Troncoso y Rodrigo Romo**, Universidad del Bío-Bío. Correspondencia: alancartes@outlook.com. La inclusión del documento no acredita envío, aceptación ni publicación. Consulte las [condiciones de reutilización](../REUSE.md).
