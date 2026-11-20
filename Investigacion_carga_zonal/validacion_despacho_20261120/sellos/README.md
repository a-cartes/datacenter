# Fecha verificable del protocolo de mantenimiento

DigiCert y Sectigo emitieron respuestas RFC 3161 el 20 de noviembre de 2026 a las 19:59:55 UTC (16:59:55 en Santiago). Cada respuesta contiene la huella SHA-256 del archivo exacto. La comprobación de ambas firmas con OpenSSL y el almacén público de certificados del sistema devolvió `Verification: OK`. Los sellos permiten a un tercero verificar que esa versión existía antes del 30 de noviembre. Su alcance es el archivo del protocolo. La atribución de autoría, el registro académico en OSF y el archivo del modelo ejecutable requieren constancias propias.

SHA-256 de [protocolo_mantenimiento.md](../protocolo_mantenimiento.md): `069626a960e5c78d72aa4a6180b28a5e9eda7945aa882fbb1da61b3829a20f5e`.

Desde esta carpeta en un sistema con OpenSSL y certificados de confianza, verificar tanto los bytes del archivo como el identificador aleatorio de la solicitud original.

```sh
sha256sum ../protocolo_mantenimiento.md
for recibo in digicert.tsr sectigo.tsr; do
  openssl ts -reply -in "$recibo" -text
  openssl ts -verify -data ../protocolo_mantenimiento.md -in "$recibo" -CAfile /etc/ssl/certs/ca-certificates.crt
  openssl ts -verify -queryfile protocolo.tsq -in "$recibo" -CAfile /etc/ssl/certs/ca-certificates.crt
done
```

[Servicio de DigiCert](https://knowledge.digicert.com/solution/troubleshooting-timestamping-problems) · [Estándar RFC 3161](https://www.rfc-editor.org/rfc/rfc3161)

## Copia íntegra fuera de GitHub

Internet Archive conservó el documento el 20 de noviembre de 2026 a las 20:07:49 UTC (17:07:49 en Santiago). Se recuperó la captura pública, se descomprimió la respuesta HTTP y se compararon los 10.126 bytes con el archivo firmado por las dos autoridades. El SHA-256 coincide. Esta es una copia pública fechada del protocolo. El estudio carece de un número de registro OSF. [Captura independiente del texto completo](https://web.archive.org/web/20261120200749/https://raw.githubusercontent.com/a-cartes/datacenter/f532f3181d0f4751bb4a9c988992b487fe824e09/Investigacion_carga_zonal/validacion_despacho_20261120/protocolo_mantenimiento.md)

## Etiqueta de Git

La [etiqueta anotada en formato Git bundle](protocolo-ajla-2026-11-20.bundle) apunta al commit del protocolo `f532f3181d0f4751bb4a9c988992b487fe824e09`. La huella Git de la etiqueta es `8197c34e9f4b8628c084f9b796a774c4771ba88f`. Al depositar este paquete se verificó su importación. La publicación de la referencia en `origin` quedó pendiente de una sesión Git con credenciales de escritura. Desde esta carpeta, en un clon actualizado del repositorio, se puede importar la etiqueta y publicarla sin mover ninguna rama.

```sh
git fetch origin main
git fetch ./protocolo-ajla-2026-11-20.bundle refs/tags/protocolo-ajla-2026-11-20:refs/tags/protocolo-ajla-2026-11-20
git rev-parse 'protocolo-ajla-2026-11-20^{}'
git push origin refs/tags/protocolo-ajla-2026-11-20
```
