# Referencias metodológicas primarias

[Inicio](../README.md) · [Método](metodologia.md)

Fuentes consultadas el **25 de septiembre de 2026** mediante páginas de autores, sus manuscritos y documentación oficial. Fundamentan el diseño propuesto; no acreditan que sus supuestos se cumplan en este dataset.

| Referencia | Fuente primaria | Uso en el proyecto |
|---|---|---|
| Callaway, B., y Sant’Anna, P. H. C. (2021). *Difference-in-Differences with Multiple Time Periods*. Journal of Econometrics, 225(2), 200–230. | [Manuscrito de los autores](https://arxiv.org/abs/1803.09015); [DOI](https://doi.org/10.1016/j.jeconom.2020.12.001) | ATT por cohorte y período, adopción escalonada, covariables, agregación e inferencia. |
| Sun, L., y Abraham, S. (2021). *Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects*. | [Manuscrito de las autoras](https://arxiv.org/abs/1804.05785) | Evitar interpretar automáticamente anticipos y rezagos de una regresión convencional con efectos fijos como efectos dinámicos cuando existe heterogeneidad. |
| Butts, K. (2023, revisión del manuscrito iniciado en 2021). *Difference-in-Differences Estimation with Spatial Spillovers*. Documento de trabajo, versión 3. | [Manuscrito del autor](https://arxiv.org/abs/2105.03737v3); [página del autor](https://www.kylebutts.com/papers/spatial-spillovers/) | Distinguir efectos propios y exposición a otras intervenciones; detectar contaminación del grupo de comparación. |
| Cameron, A. C., y Miller, D. L. (2015). *A Practitioner’s Guide to Cluster-Robust Inference*. | [PDF de los autores en UC Davis](https://www.econ.ucdavis.edu/faculty/cameron/research/Cameron_Miller_JHR_2015_February.pdf) | Dependencia intragrupo, pocos grupos y límites de errores estándar convencionales en paneles. |
| Callaway, B., y Sant’Anna, P. H. C. *Group-Time Average Treatment Effects — att_gt*. Documentación del paquete `did`; página consultada muestra versión 2.5.1. | [Documentación mantenida por los autores](https://bcallaway11.github.io/did/reference/att_gt.html) | Formato largo, primera fecha de tratamiento, grupos nunca/todavía no tratados, anticipación y consecuencias de balancear automáticamente el panel. |

Las páginas de arXiv de los dos artículos publicados se consultaron como versiones accesibles de los autores; los años de los manuscritos y de publicación pueden diferir. La referencia de Butts se mantiene explícitamente como documento de trabajo en la versión consultada. Esta lista no sustituye una revisión completa de la literatura energética ni una evaluación de novedad para una revista.

## Evidencia empírica local

Las fuentes de identidad, operación, precios y mediciones se rastrean en sus propios catálogos, separados de la bibliografía econométrica:

- [Registro de centros, eventos y relaciones eléctricas](../SOCHER_2026_dataset/documentacion/Eventos_relaciones_y_red.md).
- [Mediciones, unidades y reloj](../SOCHER_2026_dataset/documentacion/Mediciones_y_reloj.md).
- [Diccionario de precios y variables del panel](../SOCHER_2026_dataset/documentacion/diccionario_panel.csv).

Una URL bibliográfica no valida la fecha de entrada de un centro. La evidencia de esa fecha debe identificarse en el expediente del establecimiento y contrastarse con su vínculo eléctrico vigente.
