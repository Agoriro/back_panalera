# Guía de roles y permisos

## Roles soportados

| Rol | Lectura y reportes | Inventario | Movimientos | Catálogos | Usuarios y roles |
| --- | --- | --- | --- | --- | --- |
| `Admin` | Sí | Escritura | Escritura | Escritura | Administración |
| `Operator` | Sí | Escritura | Escritura | Solo lectura | No |
| `Consulta` | Sí | Solo lectura | Solo lectura | Solo lectura | No |

Nombres se comparan sin distinguir mayúsculas y minúsculas. Cualquier rol no
incluido en matriz carece de permisos.

## JWT

Access token contiene nombre de rol como ayuda para interfaz:

```json
{
  "sub": "11ba20c7-691f-400f-b674-29e85f39f613",
  "role": "Admin",
  "type": "access",
  "jti": "bb27b127-009d-48b1-8e2f-e872304def64",
  "iat": 1782771020,
  "exp": 1782774620
}
```

Frontend puede usar `role` para mostrar u ocultar controles, pero no debe
considerarlo autorización definitiva. Backend consulta usuario activo y rol
vigente en DB en cada petición. Un cambio de rol afecta permisos inmediatamente,
aunque token todavía muestre valor anterior.

## Respuestas esperadas

- `401 Unauthorized`: token ausente, inválido, de tipo incorrecto o usuario inactivo.
- `403 Forbidden`: usuario autenticado sin permiso requerido.
