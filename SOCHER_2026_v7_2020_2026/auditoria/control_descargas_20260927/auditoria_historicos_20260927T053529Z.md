# Auditoría de descargas históricas

55 meses; 2,240,276 precios. Errores técnicos detectados en libros, hashes y fuentes: 0.

Clases de procedencia:

- ZIP_con_directorio_central_y_miembros_utilizados_reverificados: 49
- miembro_completo_recuperado_v7_de_ZIP_incompleto: 2
- reutilizacion_v4_miembros_completos_verificados_de_transferencia_parcial: 1
- reutilizacion_v4_ZIP_descomprimido_por_Safari: 3

La procedencia describe la construcción congelada: julio y agosto de 2023 usaron miembros completos de contenedores incompletos; febrero de 2024 heredó ese tipo de recuperación desde v4. Los contrastes posteriores con descargas completas se registran por separado. Abril, junio y julio de 2024 remiten a carpetas descomprimidas por Safari.

La búsqueda explícita del nombre, ruta y SHA del archivo 151935 no encontró coincidencias en los 114 documentos de procedencia examinados. El alcance queda limitado a esa cadena registrada.

Los errores globales incluyen ahora los controles obligatorios de recuperación, los controles negativos y la unión explícita por SHA entre el miembro del ZIP y el libro utilizado. No se volvieron a comparar todos los valores fuente–partición.

El detalle está en `auditoria_historicos_20260927T053529Z.json`; incluye la huella SHA256 del script. No se alteraron fuentes ni entregables. Esta auditoría no declara íntegros todos los auxiliares de los ZIP exteriores ni acredita identificación causal.
