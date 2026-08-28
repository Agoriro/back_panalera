# Cambios del backend que debe implementar el frontend

Este documento consolida los cambios aplicados entre las fases 0 y 6. Está dirigido al equipo frontend y describe únicamente contratos, comportamientos y tareas de integración relevantes.

## 1. Autenticación

- El login continúa en `POST /api/v1/auth/login` y devuelve `access_token`, `refresh_token` y `token_type`.
- El access token se envía como `Authorization: Bearer <token>`.
- `POST /api/v1/auth/refresh` solo acepta refresh tokens. Cada refresh token es de un solo uso: al renovarlo, debe reemplazarse inmediatamente por el nuevo.
- Reutilizar un refresh token, usar un access token para renovar, presentar un token expirado o pertenecer a un usuario desactivado devuelve `401`.
- Ante `401`, el frontend debe limpiar la sesión si no puede completar una única renovación controlada. Debe evitar bucles de refresh.

## 2. Roles y permisos

Los permisos se consultan con el rol vigente en la base de datos; no dependen de un rol antiguo incluido en el token.

- `Admin`: acceso completo, incluidos usuarios, roles y catálogos.
- `Operator`: lectura general, escritura de inventario y registro de movimientos.
- `Consulta`: solo lectura.

Comportamiento esperado:

- Sin autenticación: `401 Unauthorized`.
- Autenticado sin permiso: `403 Forbidden` con `detail` indicando el permiso requerido.
- El frontend debe ocultar o desactivar acciones incompatibles con el rol, pero el backend sigue siendo la autoridad final.

## 3. Respuestas paginadas

Los siguientes listados ya no devuelven un array en la raíz:

- `GET /api/v1/inventory`
- `GET /api/v1/movements`
- `GET /api/v1/users`
- `GET /api/v1/reports/sales`

Parámetros:

- `page`: entero desde `1`; valor predeterminado `1`.
- `page_size`: entero entre `1` y `100`; valor predeterminado `50`.

Estructura general:

```json
{
  "items": [],
  "total": 125,
  "page": 1,
  "page_size": 50,
  "pages": 3
}
```

`/reports/sales` agrega `total_revenue` y `total_profit` al mismo nivel. Estos totales corresponden a todo el filtro, no solo a la página visible.

## 4. Inventario

- `code_inventory` (SKU) y `barcode_inventory` son opcionales, únicos y admiten máximo 100 caracteres.
- Espacios al principio/final se eliminan. Una cadena vacía se guarda y devuelve como `null`.
- SKU o código de barras duplicado devuelve `409 Conflict`.
- `description_inventory` admite entre 1 y 255 caracteres después de eliminar espacios externos.
- Las relaciones `id_supplier`, `id_color`, `id_size`, `id_category` e `id_gender` se validan tanto al crear como al actualizar. Un UUID inexistente devuelve `404`.
- Los filtros `search`, `code_inventory`, `barcode_inventory`, categoría, género, color, talla y estado siguen disponibles junto con paginación.

## 5. Fotos de inventario

Endpoint de alta: `POST /api/v1/inventory/{id}/photos`.

```json
{
  "url_photos": [
    "https://cdn.example.com/products/photo-1.webp"
  ]
}
```

Reglas:

- Solo URLs `http` o `https`.
- Máximo 2048 caracteres por URL.
- No se aceptan URLs duplicadas dentro de una petición.
- Máximo 10 fotos acumuladas por artículo.
- Una foto solo puede eliminarse mediante el ID del inventario al que pertenece. Una combinación inventario/foto incorrecta devuelve `404` y no borra nada.

## 6. Compras, ventas y stock

- Compras: `POST /api/v1/movements/purchase`.
- Ventas: `POST /api/v1/movements/sale`.
- `quantity` y valores monetarios deben ser positivos.
- El backend calcula el precio de venta; el frontend no debe enviarlo en una venta.
- No se permite vender más unidades que el stock disponible. Devuelve:

```json
{
  "detail": "Stock insuficiente: disponible 3, solicitado 4"
}
```

con estado `422 Unprocessable Entity`.

Cada movimiento incluye ahora:

```json
{
  "value": "135.000000",
  "unit_cost": "100.000000"
}
```

En una venta, `unit_cost` es el coste histórico usado para calcular su ganancia. Compras posteriores no modifican ese valor ni la ganancia histórica.

## 7. Fechas y reportes

- Las fechas de movimientos se entregan en UTC, normalmente con sufijo `Z`.
- Todos los filtros deben incluir zona horaria: `Z` o un offset como `-05:00`.
- Una fecha sin zona horaria devuelve `422`.
- Los rangos usan semántica `[date_from, date_to)`: inicio inclusivo, fin exclusivo.
- `date_from` debe ser anterior a `date_to`.
- `GET /api/v1/reports/inventory` incluye artículos sin movimientos con compras, ventas y stock en cero.
- La ganancia de ventas usa el coste histórico inmutable.

Ejemplo:

```http
GET /api/v1/reports/sales?date_from=2026-08-01T00:00:00Z&date_to=2026-09-01T00:00:00Z&page=1&page_size=50
```

## 8. Manejo de errores

El formato habitual es:

```json
{
  "detail": "Descripción del error"
}
```

- `400`: petición inválida no clasificada en otra categoría.
- `401`: sesión ausente, inválida, expirada, revocada o usuario inactivo.
- `403`: usuario autenticado sin permiso.
- `404`: recurso o relación inexistente.
- `409`: conflicto de unicidad, por ejemplo SKU o barcode duplicado.
- `422`: esquema inválido o regla de negocio, por ejemplo stock insuficiente, URL inválida o fecha sin zona horaria.
- `429`: límite de intentos en login/refresh.

Los mensajes `detail` sirven para diagnóstico. La interfaz debe mapear estados a mensajes propios cuando necesite textos estables o localizados.

## 9. Health checks

- `GET /health/live`: confirma que el proceso HTTP está vivo.
- `GET /health/ready`: confirma también conexión a PostgreSQL; puede devolver `503`.
- `GET /health`: se conserva por compatibilidad como liveness simple.

Estos endpoints no forman parte del flujo normal del usuario, pero pueden usarse en monitoreo o pantalla de estado operativo.

## 10. Checklist frontend

- Adaptar inventario, movimientos y usuarios desde arrays a `Page<T>`.
- Adaptar reporte de ventas a paginación más totales globales.
- Añadir controles `page` y `page_size` y manejar páginas vacías.
- Tratar campos Decimal como cadenas decimales; evitar cálculos monetarios con `number` cuando requieran precisión.
- Enviar fechas ISO 8601 con zona horaria y respetar fin exclusivo.
- Mostrar conflicto específico para `409` de SKU/barcode.
- Mostrar stock disponible/solicitado en errores `422` de venta.
- Limitar selector de fotos a 10 acumuladas y validar URL antes de enviar.
- Renovar y reemplazar refresh token una sola vez; limpiar sesión ante fallo.
- Aplicar visibilidad de acciones según `Admin`, `Operator` o `Consulta`.
