# Ejecutar desde Replica_RM_desde_cero. Análisis suplementario: no sustituye
# los resultados por distrito ni modifica el inventario original.
suppressPackageStartupMessages({library(data.table); library(fixest); library(jsonlite)})
destino <- "resultados/comunas_20261006"
dir.create(destino, recursive=TRUE, showWarnings=FALSE)
x <- fread("datos/analitico/muestra_comuna.csv")
x[, G := fifelse(is.na(G_doc), 0, G_doc)]
# Fecha documental de inauguración corregida en AUDITORIA_REPLICA.md.
x[unidad == "LAMPA", G := 2022]
x[, Gsa := fifelse(G == 0, 10000, G)]
m <- feols(D ~ sunab(Gsa, anio, ref.p=-1) | unidad_copia + anio,
           data=x, weights=~peso, cluster=~unidad, notes=FALSE)
a <- coeftable(summary(m, agg="ATT"))
grados <- degrees_freedom(m, type="t")
intervalo <- a[1,1] + c(-1,1)*qt(.975, grados)*a[1,2]
# Validación independiente: contraste con el promedio de los 13 controles
# únicos, igualmente ponderados tras corregir las copias del matching.
u <- unique(x[, .(unidad, anio, G, D)])
controles <- u[G == 0, .(D_control=mean(D)), by=anio]
u <- merge(u, controles, by="anio")
u[, relativo := D-D_control]
contrastes <- u[G > 0, .(
  entrada=G[1], n_post=sum(anio >= G),
  contraste_ultimo_pre=mean(relativo[anio >= G])-relativo[anio == G-1],
  contraste_promedio_pre=mean(relativo[anio >= G])-mean(relativo[anio < G])
), by=unidad]
manual <- weighted.mean(contrastes$contraste_ultimo_pre, contrastes$n_post)
stopifnot(abs(manual-a[1,1]) < 1e-7)
descriptivo <- weighted.mean(contrastes$contraste_promedio_pre, contrastes$n_post)
historia <- fread("datos/unidades/historia_comuna.csv")
historia[, seleccionada_matching := unidad %in% u$unidad]
historia[, entrada_usada_este_calculo := G_doc]
historia[unidad == "LAMPA", entrada_usada_este_calculo := 2022]
fwrite(historia, file.path(destino,"clasificacion_comunas.csv"))
fwrite(contrastes, file.path(destino,"contrastes_por_comuna.csv"))
fwrite(u, file.path(destino,"series_y_comparacion.csv"))
resultado <- list(periodo="2017-2025", resultado="D = precio local - precio Quillota",
  tratados=unique(u[G>0, unidad]), controles=unique(u[G==0, unidad]),
  ATT_USD_MWh=unname(a[1,1]), SE_convencional=unname(a[1,2]),
  IC95_t_convencional=unname(intervalo), grados_libertad=grados,
  contraste_descriptivo_promedio_pre=descriptivo,
  advertencia="Solo dos comunas tratadas. El intervalo convencional no resuelve la inferencia con pocos tratamientos ni las tendencias previas. El contraste con todo el período previo es descriptivo, no un nuevo efecto causal. Ausencia de instalaciones identificadas no garantiza ausencia ni falta de exposición por la red.")
write_json(resultado, file.path(destino,"resultados.json"), pretty=TRUE, auto_unbox=TRUE, digits=12)
print(resultado)
