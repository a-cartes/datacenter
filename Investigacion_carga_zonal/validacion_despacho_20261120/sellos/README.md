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
