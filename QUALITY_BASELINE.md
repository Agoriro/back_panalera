# Línea base de calidad

Fecha: 2026-08-24

## Controles

- `poetry check --lock`: aprobado.
- `pytest`: 8 pruebas aprobadas.
- Cobertura inicial: 68 %.
- Ruff lint y formato: aprobados después de normalización automática.
- Bandit: aprobado, sin hallazgos reportados.
- mypy estricto: 209 errores heredados en 24 archivos.

## Deuda de tipos

La mayoría de errores de mypy proviene de modelos SQLAlchemy declarativos sin
`Mapped`, repositorios que heredan operaciones de modelos ORM pero exponen
entidades de dominio, y funciones de API sin anotación de retorno.

Mypy se ejecuta y muestra resultados en CI, pero queda temporalmente como
control no bloqueante. La fase final de calidad debe reducir la deuda a cero y
retirar `continue-on-error` del workflow.

## Advertencia conocida

Starlette emite `PendingDeprecationWarning` porque importa `multipart`; proviene
de una dependencia externa, no del código del proyecto.
