# Guía de Integración de Catálogos (Frontend)

Esta guía detalla los endpoints, modelos de datos, contratos de petición/respuesta y consideraciones clave para el consumo del módulo de **Catálogos** en el frontend.

---

## 1. Reglas Generales del Módulo

1. **Catálogos Simples vs Proveedores**:
   - **Catálogos Simples** (`Categorías`, `Colores`, `Tallas`, `Géneros`):
     - **NO** tienen campo de estado (`is_active`). Todos los registros creados están siempre activos en el sistema.
     - **NO** poseen endpoint de activación/desactivación (`toggle`).
     - Para estos catálogos no debe renderizarse columna o interruptor de estado (Activo/Inactivo).
   - **Proveedores** (`Suppliers`):
     - **SÍ** maneja estado `is_active` (booleano) y dispone del endpoint `PATCH /catalog/suppliers/{id}/toggle`.

2. **Compatibilidad de Nombres de Propiedades**:
   - Para máxima compatibilidad con el frontend, todos los endpoints devuelven tanto el nombre específico de la base de datos como los alias estándar `id` y `name`:
     - Ejemplo: `id_category` y `id` tienen el mismo valor UUID.
     - Ejemplo: `name_category` y `name` tienen el mismo valor de texto.

---

## 2. Endpoints de Catálogos Simples

### A. Categorías (`/api/v1/catalog/categories`)

| Método | Endpoint | Descripción | Body Request |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/catalog/categories` | Obtener listado de categorías | Ninguno |
| `GET` | `/api/v1/catalog/categories/{id}` | Obtener una categoría por ID | Ninguno |
| `POST` | `/api/v1/catalog/categories` | Crear una nueva categoría | `{ "name": "Ropa Niña" }` |
| `PUT` | `/api/v1/catalog/categories/{id}` | Actualizar nombre de categoría | `{ "name": "Ropa Niña Modificada" }` |

> **Nota**: Tanto en `POST` como en `PUT` puedes enviar `{ "name": "..." }` o `{ "name_category": "..." }`.

**Ejemplo de Respuesta (JSON)**:
```json
{
  "id_category": "a051e044-202f-43cf-a31c-be333a6e6be7",
  "name_category": "Ropa Niña",
  "id": "a051e044-202f-43cf-a31c-be333a6e6be7",
  "name": "Ropa Niña",
  "created_at": "2026-08-15T20:49:16.352921Z",
  "updated_at": null
}
```

---

### B. Colores (`/api/v1/catalog/colors`)

| Método | Endpoint | Descripción | Body Request |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/catalog/colors` | Obtener listado de colores | Ninguno |
| `GET` | `/api/v1/catalog/colors/{id}` | Obtener un color por ID | Ninguno |
| `POST` | `/api/v1/catalog/colors` | Crear un nuevo color | `{ "name": "Azul Pastel" }` |
| `PUT` | `/api/v1/catalog/colors/{id}` | Actualizar nombre de color | `{ "name": "Azul Oscuro" }` |

**Ejemplo de Respuesta (JSON)**:
```json
{
  "id_color": "b151e044-202f-43cf-a31c-be333a6e6be8",
  "name_color": "Azul Pastel",
  "id": "b151e044-202f-43cf-a31c-be333a6e6be8",
  "name": "Azul Pastel",
  "created_at": "2026-08-15T20:50:00.000000Z",
  "updated_at": null
}
```

---

### C. Tallas (`/api/v1/catalog/sizes`)

| Método | Endpoint | Descripción | Body Request |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/catalog/sizes` | Obtener listado de tallas | Ninguno |
| `GET` | `/api/v1/catalog/sizes/{id}` | Obtener una talla por ID | Ninguno |
| `POST` | `/api/v1/catalog/sizes` | Crear una nueva talla | `{ "name": "Etapa 1" }` |
| `PUT` | `/api/v1/catalog/sizes/{id}` | Actualizar nombre de talla | `{ "name": "Etapa 2" }` |

**Ejemplo de Respuesta (JSON)**:
```json
{
  "id_size": "c251e044-202f-43cf-a31c-be333a6e6be9",
  "name_size": "Etapa 1",
  "id": "c251e044-202f-43cf-a31c-be333a6e6be9",
  "name": "Etapa 1",
  "created_at": "2026-08-15T20:50:00.000000Z",
  "updated_at": null
}
```

---

### D. Géneros (`/api/v1/catalog/genders`)

| Método | Endpoint | Descripción | Body Request |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/catalog/genders` | Obtener listado de géneros | Ninguno |
| `GET` | `/api/v1/catalog/genders/{id}` | Obtener un género por ID | Ninguno |
| `POST` | `/api/v1/catalog/genders` | Crear un nuevo género | `{ "name": "Unisex" }` |
| `PUT` | `/api/v1/catalog/genders/{id}` | Actualizar nombre de género | `{ "name": "Niño" }` |

**Ejemplo de Respuesta (JSON)**:
```json
{
  "id_gender": "d351e044-202f-43cf-a31c-be333a6e6bea",
  "name_gender": "Unisex",
  "id": "d351e044-202f-43cf-a31c-be333a6e6bea",
  "name": "Unisex",
  "created_at": "2026-08-15T20:50:00.000000Z",
  "updated_at": null
}
```

---

## 3. Endpoints de Proveedores (`/api/v1/catalog/suppliers`)

| Método | Endpoint | Descripción | Body Request |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/catalog/suppliers` | Obtener listado de proveedores | Ninguno |
| `GET` | `/api/v1/catalog/suppliers/{id}` | Obtener un proveedor por ID | Ninguno |
| `POST` | `/api/v1/catalog/suppliers` | Crear un nuevo proveedor | `{\n  "name_supplier": "Huggies Colombia",\n  "address": "Calle 100 # 15-20"\n}` |
| `PUT` | `/api/v1/catalog/suppliers/{id}` | Actualizar datos del proveedor | `{\n  "name_supplier": "Huggies SAS",\n  "address": "Carrera 45 # 26-10"\n}` |
| `PATCH` | `/api/v1/catalog/suppliers/{id}/toggle` | Activar/Desactivar proveedor | Ninguno |

**Ejemplo de Respuesta (JSON)**:
```json
{
  "id_supplier": "e451e044-202f-43cf-a31c-be333a6e6beb",
  "name_supplier": "Huggies Colombia",
  "address": "Calle 100 # 15-20",
  "is_active": true,
  "id": "e451e044-202f-43cf-a31c-be333a6e6beb",
  "name": "Huggies Colombia",
  "created_at": "2026-08-15T20:50:00.000000Z",
  "updated_at": null
}
```

---

## 4. Tipos Recomendados para TypeScript (Frontend)

```typescript
// Tipos para Catálogos Simples (Categorías, Colores, Tallas, Géneros)
export interface BasicCatalogItem {
  id: string;
  name: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface CategoryItem extends BasicCatalogItem {
  id_category: string;
  name_category: string;
}

export interface ColorItem extends BasicCatalogItem {
  id_color: string;
  name_color: string;
}

export interface SizeItem extends BasicCatalogItem {
  id_size: string;
  name_size: string;
}

export interface GenderItem extends BasicCatalogItem {
  id_gender: string;
  name_gender: string;
}

// Request DTO para Crear/Editar Catálogos Simples
export interface BasicCatalogFormData {
  name: string;
}

// Tipos para Proveedores
export interface SupplierItem {
  id: string;
  id_supplier: string;
  name: string;
  name_supplier: string;
  address?: string | null;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface SupplierFormData {
  name_supplier: string;
  address?: string | null;
}
```

---

## 5. Resumen de Cambios Necesarios en el Frontend

1. **Eliminar columna "Estado" / "Activo"** en las vistas y tablas de:
   - Categorías (`categories`)
   - Colores (`colors`)
   - Tallas (`sizes`)
   - Géneros (`genders`)
2. **Remover llamadas a `/toggle`** en categorías, colores, tallas y géneros (conservar `/toggle` únicamente en la tabla de Proveedores).
3. **Formulario de Edición**: Al editar una categoría, color, talla o género, enviar únicamente el campo `{ "name": "..." }` mediante `PUT /api/v1/catalog/{recurso}/{id}`.
