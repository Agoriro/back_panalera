# Guía de Integración para el Frontend: Nombre del Rol en JWT

Para facilitar la validación de accesos e inicio de sesión de forma rápida en el frontend, se ha realizado una modificación en la estructura del token JWT.

---

## 🔹 Estructura del Token JWT de Acceso (`access_token`)

El payload del JWT generado al iniciar sesión (`POST /api/v1/auth/login`) o al refrescar el token (`POST /api/v1/auth/refresh`) ahora incluye la propiedad `"role"` en texto plano (nombre legible del rol) en lugar del UUID interno de la base de datos.

### Estructura del Payload decodificado:

```json
{
  "sub": "11ba20c7-691f-400f-b674-29e85f39f613",
  "role": "Admin", // <- Ahora es el nombre legible del rol ("Admin", "Vendedor", etc.)
  "exp": 1782774620
}
```

## 🔹 Consumo en el Frontend

El frontend puede decodificar la parte del payload del JWT en el cliente (usando librerías como `jwt-decode` en Javascript/Typescript) para conocer el rol de manera inmediata y mostrar/ocultar elementos de la interfaz, sin necesidad de consultar endpoints adicionales de perfil.

Ejemplo:
```typescript
import { jwtDecode } from "jwt-decode";

interface TokenPayload {
  sub: string;
  role: string; // "Admin" | "Vendedor"
  exp: number;
}

const token = localStorage.getItem("access_token");
if (token) {
  const decoded = jwtDecode<TokenPayload>(token);
  console.log("Rol del usuario:", decoded.role); // "Admin"
}
```
