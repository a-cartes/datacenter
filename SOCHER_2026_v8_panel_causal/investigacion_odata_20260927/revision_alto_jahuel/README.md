# Alto Jahuel: una solicitud no es una entrada de demanda

Revisión documental: 27 de septiembre de 2026.

El inventario exploratorio `data/tratamiento_acceso_abierto.csv` marca Alto Jahuel como «TRATADA», con año 2024 y empresa Ensolution. Esa fila no contiene una fecha operacional realizada ni identifica NUP; no debe alimentar la variable de tratamiento causal.

El expediente primario localizado de la misma empresa y subestación corresponde a **Solution 2, NUP5260**. El [informe de autorización definitiva del 4 de julio de 2025](https://cartas.coordinador.cl/download_anexos/68684eee3563571479b32843/0), p.4, describe un centro de consumo de 450 MW, conexión futura al paño K7 de Alto Jahuel 500 kV y operación prevista para diciembre de 2028. La [carta DE04070-25](https://cartas.coordinador.cl/download_saved_file/68684eee3563571479b32843), p.1, remite a la solicitud presentada el 15 de octubre de 2024. La sigla DC del cronograma significa declaración en construcción, no data center.

**Decisión:** el año 2024 de esa fila no acredita entrada de carga. El pronóstico 2028 tampoco constituye una entrada realizada. La coincidencia de empresa, subestación y año de solicitud dirige la revisión, pero no prueba que el registro antiguo corresponda inequívocamente a ese NUP. Estos documentos no identifican por sí solos el consumo como centro de datos ni descartan otros proyectos en Alto Jahuel.

La corrección se conserva como capa posterior: no se reescribe el inventario original ni la entrega congelada v0.2.0. No se habilita un evento causal de Alto Jahuel. Los PDF originales y sus huellas están en `fuentes/` y `manifest_fuentes.json`; se inspeccionó visualmente la página 4 del informe.
