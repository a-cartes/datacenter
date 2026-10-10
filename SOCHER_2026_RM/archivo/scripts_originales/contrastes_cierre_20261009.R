suppressPackageStartupMessages({library(data.table);library(fixest);library(jsonlite)})
scr=sub('--file=','',grep('--file=',commandArgs(FALSE),value=TRUE));r=normalizePath(file.path(dirname(scr),'..'));o=file.path(r,'resultados/cierre_socher_20261009')
x=fread(file.path(r,'resultados/socher_20261005/muestra_principal.csv'))
fit=function(z){z[,Gsa:=fifelse(G==0,10000,G)];feols(D~sunab(Gsa,anio,ref.p=-1)|unidad_copia+anio,data=z,weights=~peso,cluster=~unidad,notes=FALSE)}
m=fit(copy(x));a=coeftable(summary(m,agg='ATT'));w=wald(m,keep='anio::-[2-6]',print=FALSE)
# Joint test uses unaggregated cohort x relative-year leads, check covariance rank.
ind=grep('anio::-[2-6]',names(m$coefficients));V=m$cov.scaled[ind,ind,drop=FALSE]
print(list(wald=w,n_restricciones=length(ind),rango=qr(V)$rank))
orig=copy(x);orig[unidad=='LAMPA-4',G:=2023];mo=fit(orig);ao=coeftable(summary(mo,agg='ATT'));df=degrees_freedom(mo,type='t');ci=ao[1,1]+c(-1,1)*qt(.975,df)*ao[1,2]
# Separate joint test of aggregated lead coefficients: estimate covariance via agg sunab.
# El test conjunto completo se reporta no calculable si la covarianza es singular.
res=list(ATT=unname(a[1,1]),fecha_original_misma_muestra=list(ATT=unname(ao[1,1]),IC95=ci),test_previo_convencional=w,restricciones=length(ind),rango_covarianza=qr(V)$rank,advertencia='Test convencional, solo tres tratados; no constituye inferencia válida de pocos tratamientos por sí mismo. No interpretar no rechazo como prueba de paralelismo.')
write_json(res,file.path(o,'contrastes_estadisticos.json'),pretty=TRUE,auto_unbox=TRUE,digits=12);print(res)
# Ventana previa común a las tres cohortes, horizontes -4,-3,-2.
# Evita extremos con cambio de composición; test convencional exploratorio.
nm=names(m$coefficients);ev=sapply(nm,function(n) as.integer(sub('anio::(-?[0-9]+):.*','\\1',n)))
H=matrix(0,3,length(nm));for(i in 1:3){v=which(ev==c(-4,-3,-2)[i]);H[i,v]=1/length(v)}
bb=H%*%m$coefficients;VV=H%*%m$cov.scaled%*%t(H);rank=qr(VV)$rank
res$test_previo_ventana_comun=list(horizontes=c(-4,-3,-2),coeficientes=as.numeric(bb),rango=rank,restricciones=3)
if(rank==3){F=as.numeric(t(bb)%*%solve(VV,bb)/3);res$test_previo_ventana_comun$F=F;res$test_previo_ventana_comun$p_convencional=pf(F,3,20,lower.tail=FALSE);res$test_previo_ventana_comun$gl=c(3,20)}
write_json(res,file.path(o,'contrastes_estadisticos.json'),pretty=TRUE,auto_unbox=TRUE,digits=12);print(res$test_previo_ventana_comun)
