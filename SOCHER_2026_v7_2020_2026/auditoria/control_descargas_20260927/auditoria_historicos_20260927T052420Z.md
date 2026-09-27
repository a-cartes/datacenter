# Auditoría de descargas históricas

55 meses; 2,240,276 precios. Errores técnicos detectados en libros, hashes y fuentes: 0.

Clases de procedencia:

- ZIP_con_directorio_central_y_miembros_utilizados_reverificados: 49
- miembro_completo_recuperado_v7_de_ZIP_incompleto: 2
- reutilizacion_v4_miembros_completos_verificados_de_transferencia_parcial: 1
- reutilizacion_v4_ZIP_descomprimido_por_Safari: 3

Los libros de julio y agosto de 2023 proceden de miembros completos de contenedores incompletos. Febrero de 2024 heredó el mismo tipo de recuperación desde v4. La homologación de septiembre de 2023 se recuperó primero de un parcial y luego se confirmó con el ZIP completo. Abril de 2024 tiene un antecedente de recuperación del mismo libro, pero su procedencia final v4 está registrada como carpeta descomprimida por Safari. Junio y julio de 2024 también se reutilizaron desde esas carpetas.

El archivo de captura 151935 contiene un miembro auxiliar FPen incompleto y no figura en las fuentes utilizadas. Los controles negativos, hechos sólo en memoria, comprueban que un truncamiento y una alteración de bytes son rechazados.

El detalle de tamaños, CRC, SHA, rutas y verificaciones está en `auditoria_historicos_20260927T052420Z.json`. No se alteraron fuentes ni entregables. Esta auditoría no declara íntegros todos los auxiliares de los ZIP exteriores ni acredita identificación causal.
