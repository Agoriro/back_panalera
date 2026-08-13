# Guía de Integración Frontend: Campos `code_inventory`, `barcode_inventory` y Buscador Parcial (`search`)

Esta guía describe los cambios realizados en el módulo de **Inventario** para soportar el **código interno de producto** (`code_inventory`), el **código de barras** (`barcode_inventory`), y el **buscador parcial multi-campo** (`search`).

---

## 1. Campos Añadidos en la Entidad

| Campo | Tipo | Requerido | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- | :--- |
| `code_inventory` | `string` (opcional / `null`) | No | Código único o SKU interno asignado al producto. | `"PAN-BABY-001"` |
| `barcode_inventory` | `string` (opcional / `null`) | No | Código de barras numérico o alfanumérico leído por un escáner. | `"7701234567890"` |

---

## 2. Peticiones HTTP (Endpoints)

### A. Crear Producto (`POST /api/v1/inventory`)

Al registrar un producto nuevo, puedes enviar opcionalmente los campos `code_inventory` y `barcode_inventory`.

**Ejemplo de Body (JSON)**:
```json
{
  "description_inventory": "Pañales Etapa 1 x 30 unidades",
  "code_inventory": "PAN-ET1-30",
  "barcode_inventory": "7701234567890",
  "utility": 0.35,
  "id_supplier": "a051e044-202f-43cf-a31c-be333a6e6be7",
  "id_color": "b151e044-202f-43cf-a31c-be333a6e6be8",
  "id_size": "c251e044-202f-43cf-a31c-be333a6e6be9",
  "id_category": "d351e044-202f-43cf-a31c-be333a6e6bea",
  "id_gender": "e451e044-202f-43cf-a31c-be333a6e6beb"
}
```

---

### B. Actualizar Producto (`PUT /api/v1/inventory/{id}`)

Puedes actualizar solo el código o el código de barras enviando los valores correspondientes en el cuerpo de la petición.

**Ejemplo de Body (JSON)**:
```json
{
  "code_inventory": "PAN-ET1-30-V2",
  "barcode_inventory": "7709999888877"
}
```

---

### C. Búsqueda y Filtrado (`GET /api/v1/inventory`)

El endpoint admite filtros exactos y un **buscador parcial global**:

#### 1. Buscador Parcial Multi-campo (`search`) 🔍
Permite buscar mediante un texto libre. El backend evaluará el término buscando coincidencias parciales (insensibles a mayúsculas/minúsculas) de forma simultánea en:
- `description_inventory`
- `code_inventory`
- `barcode_inventory`

**Ejemplo URL**:
- Buscar por fragmento de texto o código:
  `GET /api/v1/inventory?search=pañal`
  `GET /api/v1/inventory?search=ET1`
  `GET /api/v1/inventory?search=770`

#### 2. Filtros Exactos
- `barcode_inventory`: Coincidencia exacta con el código de barras (Ideal para lector láser de código de barras).
  `GET /api/v1/inventory?barcode_inventory=7701234567890`
- `code_inventory`: Coincidencia exacta con el SKU/código interno.
  `GET /api/v1/inventory?code_inventory=PAN-ET1-30`

---

## 3. Ejemplo de Implementación en el Frontend (React / TypeScript / Axios)

```typescript
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export interface InventoryItem {
  id_inventory: string;
  description_inventory: string;
  code_inventory: string | null;
  barcode_inventory: string | null;
  utility: number;
  id_supplier: string;
  id_color: string;
  id_size: string;
  id_category: string;
  id_gender: string;
  is_active: boolean;
}

// Búsqueda parcial (Buscador universal en la UI / Punto de Venta)
export const searchInventory = async (query: string, token: string): Promise<InventoryItem[]> => {
  const response = await axios.get<InventoryItem[]>(`${API_URL}/inventory`, {
    headers: { Authorization: `Bearer ${token}` },
    params: { search: query }
  });
  return response.data;
};

// Búsqueda exacta por código de barras (Escáner POS)
export const findByBarcode = async (barcode: string, token: string): Promise<InventoryItem | null> => {
  const response = await axios.get<InventoryItem[]>(`${API_URL}/inventory`, {
    headers: { Authorization: `Bearer ${token}` },
    params: { barcode_inventory: barcode }
  });
  return response.data.length > 0 ? response.data[0] : null;
};
```

---

## 4. Respuesta Estandarizada (`InventoryResponse`)

```json
{
  "id_inventory": "f551e044-202f-43cf-a31c-be333a6e6bec",
  "description_inventory": "Pañales Etapa 1 x 30 unidades",
  "code_inventory": "PAN-ET1-30",
  "barcode_inventory": "7701234567890",
  "utility": 0.35,
  "id_supplier": "a051e044-202f-43cf-a31c-be333a6e6be7",
  "id_color": "b151e044-202f-43cf-a31c-be333a6e6be8",
  "id_size": "c251e044-202f-43cf-a31c-be333a6e6be9",
  "id_category": "d351e044-202f-43cf-a31c-be333a6e6bea",
  "id_gender": "e451e044-202f-43cf-a31c-be333a6e6beb",
  "is_active": true,
  "created_at": "2026-08-02T17:00:00Z",
  "updated_at": null,
  "photos": []
}
```
