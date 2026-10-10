# Instala versiones de referencia en la biblioteca de usuario que R tenga configurada.
options(repos=c(CRAN='https://cloud.r-project.org'))
if (!requireNamespace('remotes',quietly=TRUE)) install.packages('remotes')
wanted=c(fixest='0.14.2',data.table='1.18.6.1',jsonlite='2.0.0')
for (p in names(wanted)) {
  if (!requireNamespace(p,quietly=TRUE) || as.character(packageVersion(p)) != wanted[[p]]) {
    remotes::install_version(p,version=wanted[[p]],upgrade='never',dependencies=NA)
  }
  stopifnot(as.character(packageVersion(p)) == wanted[[p]])
}
