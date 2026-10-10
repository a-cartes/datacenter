# Auditoría separada: no modifica datos ni resultados de la réplica.
suppressPackageStartupMessages({library(fixest); library(data.table); library(jsonlite)})
args <- commandArgs(trailingOnly = FALSE)
script <- sub("--file=", "", grep("--file=", args, value = TRUE))
root <- normalizePath(file.path(dirname(script), ".."))
out <- file.path(root, "resultados", "auditoria_20261002")
dir.create(out, recursive = TRUE, showWarnings = FALSE)

# Cargar exclusivamente las funciones, sin ejecutar el programa ni sobrescribir resultados.
for (expr in parse(file.path(root, "scripts", "estimar.R"))) {
  if (is.call(expr) && identical(expr[[1]], as.name("<-")) && is.symbol(expr[[2]]) &&
      as.character(expr[[2]]) %in% c("twfe", "sa", "cs")) eval(expr)
}
prep_audit <- function(x) {
  x[, G := fifelse(is.na(G_doc), 0, G_doc)]
  x[, post := as.integer(G > 0 & anio >= G)]
  x[, Gsa := fifelse(G == 0, 10000, G)]
  if (!"peso" %in% names(x)) x[, peso := 1]
  if (!"unidad_copia" %in% names(x)) x[, unidad_copia := as.character(unidad)]
  x
}
M <- prep_audit(fread(file.path(root, "datos/analitico/muestra_distrito.csv")))
F <- prep_audit(fread(file.path(root, "datos/analitico/muestra_distrito_sin_emparejar.csv")))
U <- unique(M, by = c("unidad", "anio"))
U[, peso := 1]

# Verificación independiente del ATT: diferencias respecto de g-1 y controles nunca tratados.
manual <- function(x) {
  rows <- list()
  for (g in sort(unique(x[G > 0, G]))) {
    ids <- unique(x[G == g, unidad]); controls <- unique(x[G == 0, unidad])
    for (yr in sort(unique(x[anio >= g, anio]))) {
      tr <- mean(x[unidad %in% ids & anio == yr, D]) - mean(x[unidad %in% ids & anio == g-1, D])
      co <- mean(x[unidad %in% controls & anio == yr, D]) - mean(x[unidad %in% controls & anio == g-1, D])
      rows[[length(rows)+1]] <- data.table(g=g, anio=yr, n=length(ids), cambio_tratados=tr, cambio_controles=co, att=tr-co)
    }
  }
  r <- rbindlist(rows)
  list(att=weighted.mean(r$att,r$n), celdas=r)
}
base <- sa(M,"D")$att
man <- manual(U)
stopifnot(abs(base-man$att)<1e-8)
fwrite(man$celdas,file.path(out,"descomposicion_att.csv"))

# Efectos conocidos bajo tendencias paralelas exactas; solo prueba de implementación.
synthetic <- copy(M)
synthetic[, efecto_unidad := as.numeric(factor(unidad))/7]
synthetic[, base_sintetica := efecto_unidad + sin(anio-2017)*8]
tests <- lapply(c(-2.4914,0,2.4914),function(tau) {
  synthetic[, Yprueba := base_sintetica + tau*post]
  got_sa <- sa(synthetic,"Yprueba")$att
  got_twfe <- twfe(synthetic,"Yprueba")$coef
  stopifnot(abs(got_sa-tau)<1e-7,abs(got_twfe-tau)<1e-7)
  list(efecto_insertado=tau,recuperado_sa=got_sa,recuperado_twfe=got_twfe)
})
injected <- copy(M)
injected[, Din := D+2.4914*post]
delta <- sa(injected,"Din")$att-base
stopifnot(abs(delta-2.4914)<1e-8)

# Separar cambio de nodos de cambio de muestra/emparejamiento.
N <- prep_audit(fread(file.path(root,"datos/analitico/muestra_distrito_nobal.csv")))
nodes <- unique(N[,.(unidad,anio,D)],by=c("unidad","anio"))
same_sample <- copy(M)
same_sample[nodes,on=.(unidad,anio),D:=i.D]

# Fechas: escenarios explícitos, no selección según significancia. 2022 es nueva evidencia
# de inauguración de ST01 (InvestChile), pendiente de verificar el primer consumo eléctrico.
date_grid <- rbindlist(lapply(c(2020,2021),function(edge) rbindlist(lapply(2021:2023,function(odata) {
  x <- copy(M)
  x[unidad=="COLINA-3",G:=edge]; x[unidad=="LAMPA-4",G:=odata]
  x[,post:=as.integer(G>0 & anio>=G)]; x[,Gsa:=fifelse(G==0,10000,G)]
  data.table(G_edge=edge,G_st01=odata,G_st02=2023,att=sa(x,"D")$att,
             nota=ifelse(odata==2021,"2021: construcción, no operación acreditada",ifelse(odata==2022,"2022: inauguración según InvestChile","2023: cota documental anterior")))
}))))
fwrite(date_grid,file.path(out,"sensibilidad_fechas_misma_muestra.csv"))

# Diagnóstico separado de señal común: no es un efecto empírico ni una prueba causal.
shared <- copy(synthetic)
shared[,Ycomun:=base_sintetica+2.4914*as.integer(anio>=2023)]
shared_est <- sa(shared,"Ycomun")$att
stopifnot(abs(shared_est)<1e-7)

result <- list(
  alcance="Auditoría de implementación; no valida identificación causal ni precisión con tres tratados",
  att_recalculado_sa=base,att_manual=man$att,
  twfe_recalculado=twfe(M,"D")$coef,
  pruebas_efectos_conocidos=tests,
  aumento_att_al_sumar_2_4914_a_tratados_post=delta,
  efecto_comun_a_todos_absorbido_por_efectos_anio=shared_est,
  nodos=list(balanceado=base,todos_nodos_misma_muestra=sa(same_sample,"D")$att,
             todos_nodos_reemparejado=sa(N,"D")$att),
  inferencia_guardada=list(sa_emparejado=base,cs_sin_emparejar=cs(F,"D")$att_simple,
     nota="El p de permutaciones guardado corresponde a CS sin emparejar, no a SA emparejado"),
  escenarios_fechas=date_grid)
write_json(result,file.path(out,"auditoria_estimacion.json"),pretty=TRUE,auto_unbox=TRUE,digits=10)
cat(toJSON(result,pretty=TRUE,auto_unbox=TRUE,digits=8),"\n")
