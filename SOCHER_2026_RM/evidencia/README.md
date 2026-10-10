# Evidencia de reproducción

La entrega `v0.3.0` conserva las comprobaciones locales y externas. La [ejecución completa en Linux](https://github.com/a-cartes/datacenter/actions/runs/38015858759) pasó los 35 controles científicos; la [revisión de integridad y enlaces](https://github.com/a-cartes/datacenter/actions/runs/38015858728) también terminó correctamente.

- [Informe Linux](verificacion_linux.json): entorno limpio de GitHub, Python 3.13.16 y R 4.6.1.
- [Informe local con desempate portable](verificacion_portable_local.json): Python 3.13.9 y R 4.6.1.
- [Procedencia de la ejecución externa](ejecucion_github.json): commit ejecutado, enlaces y hashes.
- [Tabla 1](tabla_1.csv), [Figura 1](figura_1.png) y [sensibilidad 2030](sensibilidad_2030.csv): resultados consultables.

`verificacion_local.json` y `verificacion_entorno_limpio.json` conservan las primeras comprobaciones en Mac, anteriores al desempate explícito. La [nota de portabilidad](../documentacion/PORTABILIDAD.md) documenta la diferencia y las referencias históricas conservadas. Las cifras distritales del manuscrito no cambiaron.

Los informes son evidencia computacional, no una validación de identificación causal. La reproducción comienza en datos derivados; no ejecuta una simulación PET26 ni vuelve a descargar todas las fuentes primarias.
