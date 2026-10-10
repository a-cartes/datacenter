# Estimación de la réplica adaptada: TWFE, Sun y Abraham (2021), Callaway y Sant'Anna (2021)
# e inferencia por aleatorización. Uso: Rscript scripts/estimar.R <alternativa> [G_doc|G_min]
# Entradas: datos/analitico/muestra_<alt>.csv (copias con peso 1/m) y _sin_emparejar.csv
# Salidas: resultados/estimaciones/<alt>_<G>.json, event study en CSV y PNG.
suppressPackageStartupMessages({library(fixest); library(data.table); library(jsonlite)})
args <- commandArgs(trailingOnly = TRUE)
alt <- ifelse(length(args) >= 1, args[1], "distrito")
gcol <- ifelse(length(args) >= 2, args[2], "G_doc")
root <- normalizePath(file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE))), ".."))
out <- file.path(root, "resultados", "estimaciones"); dir.create(out, showWarnings = FALSE, recursive = TRUE)
set.seed(20261002)

M <- fread(file.path(root, "datos", "analitico", paste0("muestra_", alt, ".csv")))
F <- fread(file.path(root, "datos", "analitico", paste0("muestra_", alt, "_sin_emparejar.csv")))
prep <- function(X) {
  X[, G := get(gcol)]
  X[is.na(G), G := 0]
  X[, post := as.integer(G > 0 & anio >= G)]
  X[, Gsa := ifelse(G == 0, 10000, G)]
  X
}
M <- prep(M); F <- prep(F)
if (!"unidad_copia" %in% names(F)) F[, unidad_copia := as.character(unidad)]
if (!"peso" %in% names(F)) F[, peso := 1]

res <- list(alternativa = alt, regla_G = gcol,
            n_tratadas = uniqueN(M[G > 0, unidad]), cohortes = as.list(table(unique(M[G > 0, .(unidad, G)])$G)),
            controles_unicos = uniqueN(M[G == 0, unidad]), posiciones_control = uniqueN(M[G == 0, unidad_copia]),
            filas = nrow(M), anios = sort(unique(M$anio)))

ci <- function(est, se) c(est - 1.96 * se, est + 1.96 * se)

twfe <- function(X, y, w = TRUE) {
  f <- as.formula(paste(y, "~ post | unidad_copia + anio"))
  m <- feols(f, X[!is.na(get(y))], weights = if (w) ~peso else NULL, cluster = ~unidad)
  list(coef = unname(coef(m)["post"]), se = unname(se(m)["post"]), n = nobs(m), p = unname(pvalue(m)["post"]))
}

sa <- function(X, y, w = TRUE) {
  X2 <- X[!is.na(get(y))]
  f <- as.formula(paste(y, "~ sunab(Gsa, anio, ref.p = -1) | unidad_copia + anio"))
  m <- feols(f, X2, weights = if (w) ~peso else NULL, cluster = ~unidad)
  a <- summary(m, agg = "ATT")
  ct <- coeftable(a)
  es <- as.data.table(coeftable(m), keep.rownames = "termino")
  es[, rel := as.integer(sub("anio::", "", termino))]
  list(att = unname(ct["ATT", 1]), se = unname(ct["ATT", 2]), p = unname(ct["ATT", 4]), es = es, n = nobs(m))
}

# Callaway y Sant'Anna con controles nunca tratados, base 'varying' (g-1), sin covariables
cs <- function(X, y) {
  X2 <- X[!is.na(get(y))]
  gs <- sort(unique(X2[G > 0, G])); yrs <- sort(unique(X2$anio))
  rows <- list()
  for (g in gs) {
    tr <- X2[G == g]; co <- X2[G == 0]
    for (t in yrs) {
      b <- if (t >= g) g - 1 else t - 1
      if (!(b %in% yrs) || t == b) next
      dt <- tr[anio == t, weighted.mean(get(y), peso)] - tr[anio == b, weighted.mean(get(y), peso)]
      dc <- co[anio == t, weighted.mean(get(y), peso)] - co[anio == b, weighted.mean(get(y), peso)]
      rows[[length(rows) + 1]] <- data.table(g = g, t = t, e = t - g, att = dt - dc, ng = uniqueN(tr$unidad))
    }
  }
  A <- rbindlist(rows)
  post <- A[e >= 0]
  list(att_simple = post[, weighted.mean(att, ng)], gt = A)
}

ys <- c("D", "L", "C", "P")
for (y in ys) {
  if (!y %in% names(M) || all(is.na(M[[y]]))) next
  r <- list()
  r$twfe <- twfe(M, y)
  r$twfe_sin_pesos_unicos <- twfe(unique(M, by = c("unidad", "anio")), y, w = FALSE)
  s <- tryCatch(sa(M, y), error = function(e) NULL)
  if (!is.null(s)) {
    r$sun_abraham <- list(att = s$att, se = s$se, p = s$p, ic95 = ci(s$att, s$se), n = s$n)
    fwrite(s$es, file.path(out, paste0(alt, "_", gcol, "_eventstudy_", y, ".csv")))
  }
  c_ <- cs(M, y)
  r$callaway_santanna <- list(att_simple = c_$att_simple)
  fwrite(c_$gt, file.path(out, paste0(alt, "_", gcol, "_cs_gt_", y, ".csv")))
  r$twfe_sin_emparejar <- twfe(F, y, w = FALSE)
  pre <- M[G == 0 & anio < 2019, mean(get(y), na.rm = TRUE)]
  r$media_controles_2017_2018 <- pre
  r$media_tratadas_antes_de_G <- M[G > 0 & anio < G, mean(get(y), na.rm = TRUE)]
  res[[y]] <- r
}

# Inferencia por aleatorización (Fisher): se asignan al azar los G observados a unidades del
# conjunto completo sin emparejar (tratadas + controles) y se recalcula el TWFE y el CS simple.
ri <- function(X, y, B = 2000) {
  X2 <- X[!is.na(get(y))]
  units <- unique(X2$unidad); Gobs <- unique(X2[G > 0, .(unidad, G)])$G
  obs_t <- twfe(X2, y, w = FALSE)$coef
  obs_c <- cs(X2[, peso := 1], y)$att_simple
  sims <- replicate(B, {
    pick <- sample(units, length(Gobs))
    Z <- copy(X2)[, G := 0]
    for (i in seq_along(pick)) Z[unidad == pick[i], G := Gobs[i]]
    Z[, post := as.integer(G > 0 & anio >= G)]
    c(tryCatch(coef(feols(as.formula(paste(y, "~ post | unidad + anio")), Z, notes = FALSE))["post"], error = function(e) NA),
      cs(Z, y)$att_simple)
  })
  list(obs_twfe = obs_t, p_twfe = mean(abs(sims[1, ]) >= abs(obs_t), na.rm = TRUE),
       obs_cs = obs_c, p_cs = mean(abs(sims[2, ]) >= abs(obs_c), na.rm = TRUE),
       B = B, pool_unidades = length(units), tratadas = length(Gobs),
       cuantiles_twfe = quantile(sims[1, ], c(.025, .5, .975), na.rm = TRUE))
}
res$aleatorizacion_D <- ri(F, "D")

# Dejar fuera una unidad tratada a la vez (Sun y Abraham y TWFE sobre D)
loo <- list()
for (u in unique(M[G > 0, unidad])) {
  X <- M[unidad != u]
  if (uniqueN(X[G > 0, unidad]) == 0) next
  s <- tryCatch(sa(X, "D"), error = function(e) NULL)
  loo[[as.character(u)]] <- list(twfe = twfe(X, "D")$coef, sa = if (is.null(s)) NA else s$att)
}
res$deja_uno_fuera_D <- loo

# Figura del estudio de eventos (D)
esf <- file.path(out, paste0(alt, "_", gcol, "_eventstudy_D.csv"))
if (file.exists(esf)) {
  es <- fread(esf)
  png(file.path(out, paste0(alt, "_", gcol, "_eventstudy_D.png")), width = 900, height = 560)
  es <- rbind(es[, .(rel, Estimate, se = `Std. Error`)], data.table(rel = -1, Estimate = 0, se = 0))[order(rel)]
  plot(es$rel, es$Estimate, pch = 19, ylim = range(c(es$Estimate - 1.96 * es$se, es$Estimate + 1.96 * es$se)),
       xlab = "Años desde la primera entrada", ylab = "D (USD/MWh), relativo a t = -1",
       main = paste0("Sun y Abraham: ", alt, " (", gcol, ")"))
  arrows(es$rel, es$Estimate - 1.96 * es$se, es$rel, es$Estimate + 1.96 * es$se, angle = 90, code = 3, length = 0.04)
  abline(h = 0, lty = 2); abline(v = -0.5, lty = 3)
  dev.off()
}
write_json(res, file.path(out, paste0(alt, "_", gcol, ".json")), auto_unbox = TRUE, pretty = TRUE, digits = 6)
cat(toJSON(res[c("alternativa", "regla_G", "n_tratadas", "cohortes", "controles_unicos")], auto_unbox = TRUE), "\n")
for (y in ys) if (!is.null(res[[y]])) cat(y, "TWFE", round(res[[y]]$twfe$coef, 3), "(", round(res[[y]]$twfe$se, 3), ")",
                                          " SA", round(res[[y]]$sun_abraham$att, 3), "(", round(res[[y]]$sun_abraham$se, 3), ")",
                                          " CS", round(res[[y]]$callaway_santanna$att_simple, 3), "\n")
cat("RI p TWFE", res$aleatorizacion_D$p_twfe, " RI p CS", res$aleatorizacion_D$p_cs, "\n")
