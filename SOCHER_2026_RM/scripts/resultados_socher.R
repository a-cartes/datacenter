# Cierre de resultados históricos para SOCHER, 5 de octubre de 2026.
# Conserva las bases previas. La fecha ST01=2022 y los nodos incorporados
# responden a la evidencia y regla del original descritas en AUDITORIA_REPLICA.md.
suppressPackageStartupMessages({library(fixest); library(data.table); library(jsonlite)})
script <- sub("--file=", "", grep("--file=", commandArgs(FALSE), value=TRUE))
root <- normalizePath(file.path(dirname(script), ".."))
out <- file.path(root, "resultados", "socher_20261005")
dir.create(out, recursive=TRUE, showWarnings=FALSE)

read_sample <- function(alt, dates="corregidas") {
  x <- fread(file.path(root, "datos/analitico", paste0("muestra_", alt, ".csv")))
  x[, G := fifelse(is.na(G_doc), 0, G_doc)]
  if (dates != "anteriores") x[unidad == "LAMPA-4" & G > 0, G := 2022]
  if (dates == "siguiente_calendario") x[G > 0, G := G + 1]
  x[, Gsa := fifelse(G == 0, 10000, G)]
  x[, post := as.integer(G > 0 & anio >= G)]
  x
}

manual_att <- function(x) {
  u <- unique(x, by=c("unidad", "anio"))
  cells <- rbindlist(lapply(sort(unique(u[G>0, G])), function(g) {
    rbindlist(lapply(sort(unique(u[anio>=g, anio])), function(t) {
      a <- u[G==g & anio==t, mean(D)] - u[G==g & anio==g-1, mean(D)]
      b <- u[G==0 & anio==t, mean(D)] - u[G==0 & anio==g-1, mean(D)]
      data.table(cohorte=g, anio=t, n=uniqueN(u[G==g, unidad]), att=a-b)
    }))
  }))
  list(att=weighted.mean(cells$att, cells$n), cells=cells)
}

estimate <- function(x, name) {
  m <- feols(D ~ sunab(Gsa, anio, ref.p=-1) | unidad_copia + anio,
             data=x, weights=~peso, cluster=~unidad, notes=FALSE)
  a <- summary(m, agg="ATT")
  ct <- coeftable(a)
  df <- degrees_freedom(m, type="t")
  tcrit <- qt(.975, df)
  att <- unname(ct["ATT", 1]); serr <- unname(ct["ATT", 2]); p <- unname(ct["ATT", 4])
  stopifnot(abs(p - 2*pt(-abs(att/serr),df)) < 1e-8)
  manual <- manual_att(x)
  stopifnot(abs(manual$att-att)<1e-8)
  row <- data.table(especificacion=name, att=att, se=serr,
     ic95_inf=att-tcrit*serr, ic95_sup=att+tcrit*serr, p_convencional=p, gl=df,
     tratadas=uniqueN(x[G>0, unidad]), controles=uniqueN(x[G==0, unidad]),
     filas_copias=nrow(x), unidades_anio=uniqueN(x,by=c("unidad","anio")))
  es <- as.data.table(coeftable(m), keep.rownames="termino")
  es[, rel := as.integer(sub("anio::", "", termino))]
  es[, `:=`(ic95_inf=Estimate-tcrit*`Std. Error`, ic95_sup=Estimate+tcrit*`Std. Error`)]
  fwrite(es,file.path(out,paste0(name,"_eventos.csv")))
  fwrite(manual$cells,file.path(out,paste0(name,"_cohortes.csv")))
  row
}

# Orden fijado por correspondencia metodológica, no por resultados.
specs <- list(
  principal_nodos_incorporados=read_sample("distrito_nobal"),
  sensibilidad_barras_fijas=read_sample("distrito"),
  sensibilidad_calendario_siguiente=read_sample("distrito_nobal","siguiente_calendario"),
  sensibilidad_controles_lejos=read_sample("distrito_ctrl_lejos5km"),
  sensibilidad_controles_baja_correlacion=read_sample("distrito_ctrl_corr_menor05"),
  referencia_anterior=read_sample("distrito","anteriores")
)
rows <- rbindlist(lapply(names(specs),function(n) estimate(specs[[n]],n)))
main <- specs[[1]]
loo <- rbindlist(lapply(unique(main[G>0,unidad]), function(u) {
  x <- main[unidad != u]
  z <- estimate(x,paste0("sin_",gsub("-","_",u)))
  z[,excluida:=u]; z
}))
fwrite(rows,file.path(out,"estimaciones.csv"))
fwrite(loo,file.path(out,"sensibilidad_exclusion.csv"))
fwrite(main,file.path(out,"muestra_principal.csv"))
write_json(list(fecha="2026-10-05", principal=rows[1], variantes=rows,
  exclusion=loo, fechas=unique(main[G>0,.(unidad,G)]),
  inferencia="Intervalos y p convencionales con errores agrupados por distrito y distribución t de fixest; no garantizan cobertura con tres distritos tratados. No se utiliza el p de otra especificación.",
  seleccion="Principal incorpora barras con cobertura anual >=90%, matching previamente calculado para ese universo, ST01=2022 según evidencia de inauguración. Cambios posteriores al protocolo original declarados.",
  versiones=list(R=R.version.string,fixest=as.character(packageVersion("fixest")))),
  file.path(out,"resultados.json"),pretty=TRUE,auto_unbox=TRUE,digits=10)
print(rows)
print(loo[,.(excluida,att,ic95_inf,ic95_sup)])

# Figura con soporte de cohortes visible, sin presentar intervalos convencionales
# como solución a los pocos tratados o a las diferencias previas.
ev <- fread(file.path(out,"principal_nodos_incorporados_eventos.csv"))
ev <- rbind(ev[,.(rel,Estimate,ic95_inf,ic95_sup)],
            data.table(rel=-1,Estimate=0,ic95_inf=0,ic95_sup=0))[order(rel)]
gs <- unique(main[G>0,.(unidad,G)])
ev[,n_cohortes:=sapply(rel,function(e) sum(gs$G+e>=2017 & gs$G+e<=2025))]
fwrite(ev,file.path(out,"figura_eventos_datos.csv"))
png(file.path(out,"figura_eventos.png"),width=1800,height=730,res=240)
par(mar=c(4.1,4.2,0.5,0.7),mgp=c(2.4,0.6,0),family="sans",cex=.86)
plot(ev$rel,ev$Estimate,type="n",xaxt="n",xlab="Años desde la primera entrada",
     ylab="D respecto de t = -1 (USD/MWh)",ylim=c(-2.7,3.4),bty="l")
abline(h=0,col="grey65",lty=2);abline(v=-.5,col="grey75",lty=3)
shown <- ev[rel != -1]
arrows(shown$rel,shown$ic95_inf,shown$rel,shown$ic95_sup,angle=90,code=3,length=.035,col="#424242")
points(ev$rel,ev$Estimate,pch=19,col=ifelse(ev$rel<0,"#575757","#16466B"),cex=.85)
axis(1,at=ev$rel,labels=ev$rel)
dev.off()

# Cálculo contextual sobre una tabla oficial. No se atribuye a los centros de datos.
cen <- data.table(escenario=c("Bajo","Medio","Alto"),
                  sen_2025_TWh=c(83.4,84,84.8),sen_2030_TWh=c(97.4,102.6,114.6))
cen[,`:=`(incremento_TWh=sen_2030_TWh-sen_2025_TWh,
          crecimiento_porcentaje=100*(sen_2030_TWh/sen_2025_TWh-1),
          tasa_anual_porcentaje=100*((sen_2030_TWh/sen_2025_TWh)^(1/5)-1))]
cen[,fuente:="CEN 2511-C13-INF-DPR-01-V1, noviembre 2025, tabla 1-1, p. 5"]
fwrite(cen,file.path(out,"contexto_SEN_2030.csv"))
