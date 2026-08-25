# Línea base de calidad

Fecha de actualización: 2026-08-24

## Controles

- `poetry check --lock`: aprobado.
- Ruff lint y formato: bloqueantes en CI.
- Bandit: bloqueante, sin hallazgos.
- Mypy: bloqueante, sin errores en 64 archivos.
- Pytest exige cobertura mínima de 75 % en CI.

## Política de tipos

Mypy comprueba cuerpos no anotados y avisos útiles. Se desactivan códigos que
SQLAlchemy declarativo clásico y la adaptación modelo-entidad producen de forma
sistemática (`override`, `assignment`, `arg-type`, entre otros). El control ya
es bloqueante: nuevos errores fuera de esas incompatibilidades conocidas rompen
el pipeline. Migrar modelos a `Mapped` permitiría endurecer esos códigos después.

## Advertencia conocida

La advertencia `PendingDeprecationWarning` de `starlette.formparsers` se filtra
por módulo y mensaje exactos; proviene de dependencia fijada, no del proyecto.
