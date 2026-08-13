# Guía de Integración Backend - Frontend (Pañalera)

Este documento contiene la información necesaria para que el equipo de Frontend pueda entender la arquitectura del Backend, los flujos principales de negocio y cómo interactuar con la API REST.

---

## 1. Información General

*   **URL Base Local**: `http://localhost:8000/api/v1`
*   **Documentación Interactiva (Swagger/OpenAPI)**: `http://localhost:8000/docs` *(Fundamental para ver en tiempo real el formato exacto de cada Request y Response)*.
*   **Colección de Postman**: Se incluye en el repositorio una colección de Postman que puedes importar para probar los endpoints y ver ejemplos reales.
*   **Formato de Comunicación**: `application/json`

---

## 2. Autenticación y Autorización (JWT)

El sistema utiliza autenticación basada en JWT (JSON Web Tokens). Existen dos tipos de token:
1.  **Access Token**: De vida corta (ej. 30 minutos). Se usa para autorizar peticiones.
2.  **Refresh Token**: De vida larga (ej. 7 días). Se usa para solicitar un nuevo Access Token cuando este expira, evitando que el usuario tenga que volver a iniciar sesión.

### Flujo de Login
1.  Realizar una petición `POST` a `/auth/login` con el body:
    ```json
    {
      "username": "admin",
      "password": "admin123"
    }
    ```
2.  La API responderá con:
    ```json
    {
      "access_token": "eyJhbGci...",
      "refresh_token": "eyJhbGci...",
      "token_type": "bearer"
    }
    ```
3.  **Frontend almacena los tokens** (se recomienda `localStorage` o en memoria para el Access Token, y un almacenamiento seguro para el Refresh Token).

### Realizar Peticiones Autenticadas
Para acceder a rutas protegidas (Inventario, Movimientos, etc.), debes incluir el Access Token en los *Headers* de tus llamadas HTTP:
```http
Authorization: Bearer <access_token>
```

### Flujo de Refresh (Expiración de Token)
Si el Access Token expira, el backend responderá con un error HTTP `401 Unauthorized`.
Tu interceptor en el Frontend (por ejemplo en Axios o Fetch) debe capturar este `401`, llamar al endpoint `/auth/refresh` enviando el `refresh_token`, y si es exitoso, reintentar la petición original con el nuevo `access_token`.

---

## 3. Arquitectura y Módulos Principales

El sistema está dividido en módulos. Todas las rutas devuelven respuestas estandarizadas basadas en modelos estrictos (garantizados por Pydantic). Revisa `/docs` para ver qué campos son obligatorios o nulos.

### A. Catálogos (Dependencias Básicas)
Antes de crear un producto de Inventario, necesitas que existan los catálogos.
Los endpoints son operaciones CRUD clásicas (`GET`, `POST`, `PUT`, `DELETE`):
*   **Proveedores**: `/catalog/suppliers` (Contiene `name_supplier`, `address`, `is_active`)
*   **Categorías**: `/catalog/categories`
*   **Colores**: `/catalog/colors`
*   **Tallas**: `/catalog/sizes`
*   **Géneros**: `/catalog/genders`

### B. Inventario (Productos)
Endpoint: `/inventory/`
*   Para crear un producto, necesitas enviar los UUIDs (IDs) de las tablas de catálogos correspondientes (`id_supplier`, `id_color`, `id_size`, `id_category`, `id_gender`), la descripción, la **utilidad** y opcionalmente el código de producto (`code_inventory`) y código de barras (`barcode_inventory`).
*   **Buscador Parcial Global**: `GET /inventory?search=texto` realiza una búsqueda en tiempo real (coincidencia parcial `ILIKE`) sobre la descripción, código de producto y código de barras.
*   **Filtros Exactos**: `GET /inventory?code_inventory=...` o `GET /inventory?barcode_inventory=...` (ideal para lectores de código de barras). Ver detalle y ejemplos de código en [GUIA_INVENTARIO_CODIGOS.md](file:///c:/Users/EdwMar/Documents/Proyectos/Panalera/Back/back_panalera/GUIA_INVENTARIO_CODIGOS.md).
*   El backend *no* calcula el precio final de venta como campo físico en la tabla de inventario, sino que la "utilidad" o los promedios se calculan dinámicamente según las compras de inventario (ver sección de Movimientos).

### C. Movimientos (Compras y Ventas)
Endpoint: `/movements/`
Este es el módulo que afecta el **Stock y los Costos**.
*   Existen dos tipos de movimiento (`type_movement`): `BUY` (Compra a proveedor) y `SELL` (Venta a cliente).
*   **`BUY` (Compra)**: Incrementa la cantidad de stock del producto (`id_inventory`). Requiere el `id_supplier`, la `quantity` (cantidad entrante) y el `value` (costo unitario de la compra).
*   **`SELL` (Venta)**: Disminuye la cantidad de stock. En este caso el `id_supplier` puede ir nulo. Debe enviarse la cantidad a restar y el valor final de venta.
*   *Nota*: El backend valida que no haya "stock negativo". Si intentas hacer un `SELL` por una cantidad mayor al stock actual, la API devolverá un error HTTP `400 Bad Request`.

### D. Usuarios y Roles
Endpoints: `/users/` y `/roles/`
Gestión interna de permisos. Los contraseñas *nunca* se devuelven en los endpoints `GET`. Cuando se actualiza un usuario, si no se envía la contraseña, se conserva la actual.

---

## 4. Respuestas de Error y Manejo (Frontend)

El backend utiliza códigos HTTP estándar:
*   `200 OK` / `201 Created`: Operación exitosa.
*   `400 Bad Request`: Error de lógica de negocio (Ej: Stock insuficiente, regla de negocio violada).
*   `401 Unauthorized`: Token inválido o ausente.
*   `403 Forbidden`: El usuario no tiene permisos suficientes para la acción.
*   `404 Not Found`: El recurso solicitado (UUID) no existe.
*   `422 Unprocessable Entity`: Error de validación de formulario/JSON (falta un campo, tipo de dato incorrecto). Muy común si no respetas el Schema exacto.
*   `429 Too Many Requests`: Por seguridad, hay límite de peticiones (Rate Limiting). Especialmente en el `/auth/login`.

El body del error generalmente tiene el formato (dependiendo si es un error de Pydantic o de negocio):
```json
{
  "detail": "Mensaje legible del error"
}
```

---

## 5. Recomendaciones para el Desarrollo Frontend

1.  **Tipado en Frontend**: Si usas TypeScript, la mejor forma de empezar es entrar a `http://localhost:8000/docs`, descargar el archivo `openapi.json` e introducirlo a un generador automático de tipos (como `openapi-typescript-codegen`) para no tener que tipar a mano las interfaces.
2.  **Interceptores Globales**: Configura Axios o Fetch para adjuntar el Header de `Authorization` globalmente, y maneja de forma centralizada la lógica de refresh si hay un `401`.
3.  **Manejo de UUIDs**: Ten en cuenta que todos los IDs del backend son `UUID` string, no enteros numéricos (ej. `a051e044-202f-43cf-a31c-be333a6e6be7`).
4.  **CORS**: El backend está configurado para aceptar CORS del Frontend local, si el Front va a correr en un puerto diferente a los habituales, deberás pedirle al encargado de Backend que agregue tu origen (Origin) en la configuración de CORS.
