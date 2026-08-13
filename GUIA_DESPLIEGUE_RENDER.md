# 🚀 Guía de Despliegue en Render (Backend + Base de Datos PostgreSQL)

Esta guía explica paso a paso cómo publicar el backend (**FastAPI**) y la base de datos (**PostgreSQL**) en **[Render](https://render.com/)**.

---

## 📋 Arquitectura del Despliegue

```
┌────────────────────────────────────────────────────────┐
│                        RENDER                          │
│                                                        │
│  ┌──────────────────────┐    Internal Connection       │
│  │     Web Service      │ ──────────────────────────┐  │
│  │   (FastAPI/Python)   │                           │  │
│  │   panalera-backend   │                           ▼  │
│  └──────────┬───────────┘                ┌──────────────────┐
│             │                            │   PostgreSQL DB  │
│             │ Public HTTPS URL           │   panalera-db    │
│             ▼                            └──────────────────┘
│     [ Frontend / Web / App ]                           │
└────────────────────────────────────────────────────────┘
```

El proyecto ya incluye la configuración de Infraestructura como Código (**Render Blueprint** en `render.yaml`), lo que permite desplegar la base de datos y el backend con **un solo clic**.

---

## 🌟 Método 1: Despliegue Automático con Blueprint (Recomendado)

Render leerá el archivo `render.yaml` y creará automáticamente tanto la base de datos como el servicio web, vinculando las credenciales y ejecutando las migraciones.

### Pasos:

1. **Subir los cambios a tu repositorio Git** (GitHub o GitLab):
   ```bash
   git add .
   git commit -m "Configuracion de despliegue en Render para backend y base de datos"
   git push origin main
   ```

2. **Ingresar a Render**:
   - Ve a [dashboard.render.com](https://dashboard.render.com/) e inicia sesión.

3. **Crear un nuevo Blueprint**:
   - Haz clic en el botón superior **New +** y selecciona **Blueprint**.
   - Conecta tu cuenta de GitHub/GitLab si aún no lo has hecho y selecciona el repositorio de `back_panalera`.

4. **Revisar y Aplicar**:
   - Render detectará el archivo `render.yaml` y te mostrará los dos recursos a crear:
     - 🗄️ **panalera-db** (PostgreSQL Database - Plan Free)
     - ⚙️ **panalera-backend** (Web Service - Plan Free)
   - Asigna un nombre al Blueprint Instance (por ejemplo: `panalera-production`).
   - Haz clic en **Apply**.

5. **Proceso Automático de Render**:
   - Render creará la base de datos PostgreSQL.
   - Instalará las dependencias (`poetry install`).
   - Ejecutará el comando pre-deploy: `alembic upgrade head && python seed_db.py` (aplica todas las migraciones y crea el usuario `admin`).
   - Iniciará la API con `uvicorn`.

---

## 🛠️ Método 2: Despliegue Manual (Paso a Paso)

Si prefieres crear los recursos manualmente desde el dashboard de Render:

### Paso 1: Crear la Base de Datos PostgreSQL

1. En Render Dashboard, clic en **New +** > **PostgreSQL**.
2. Completa los campos:
   - **Name**: `panalera-db`
   - **Database**: `panalera_db`
   - **User**: `panalera_user`
   - **Region**: Selecciona la más cercana (ej. *Oregon (US West)* o *Ohio (US East)*).
   - **Plan**: `Free`.
3. Clic en **Create Database**.
4. Una vez creada, ve a la sección **Connections** y copia la **Internal Database URL** (empieza con `postgres://...`).

---

### Paso 2: Crear el Web Service para el Backend

1. En Render Dashboard, clic en **New +** > **Web Service**.
2. Conecta tu repositorio Git (`back_panalera`).
3. Configura los siguientes parámetros:
   - **Name**: `panalera-backend`
   - **Language / Runtime**: `Python 3`
   - **Region**: La misma región donde creaste la base de datos.
   - **Branch**: `main` (o tu rama principal).
   - **Build Command**:
     ```bash
     pip install poetry && poetry config virtualenvs.create false && poetry install --only main
     ```
   - **Start Command**:
     ```bash
     alembic upgrade head && python seed_db.py && uvicorn src.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: `Free`.

> **Nota para Plan Free**: Render no permite `pre-deploy commands` en el plan gratuito, por lo que las migraciones y la creación del usuario inicial se ejecutan automáticamente al inicio de `Start Command`.

5. Agrega las **Variables de Entorno** (**Environment Variables**):

| Clave (Key) | Valor (Value) | Descripción |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.13.0` | Versión de Python en el contenedor |
| `ENVIRONMENT` | `production` | Modo de ejecución |
| `LOG_LEVEL` | `INFO` | Nivel de logs |
| `DATABASE_URL` | *Pega la Internal Database URL copiada en el Paso 1* | Conexión a la base de datos |
| `SECRET_KEY` | *Genera una clave segura de 32+ caracteres* | Clave para firmar JWT |
| `ALGORITHM` | `HS256` | Algoritmo de JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Duración del token de acceso (minutos) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duración del token de refresco (días) |
| `ALLOWED_ORIGINS` | `*` o la URL de tu frontend (ej. `https://tu-frontend.vercel.app`) | Orígenes permitidos por CORS |

6. Haz clic en **Create Web Service**.

---

## 🔍 Verificación y Pruebas

Una vez finalizado el despliegue (estado **Live**):

1. **Health Check**:
   Abre en el navegador:
   ```
   https://<tu-servicio-render>.onrender.com/health
   ```
   Respuesta esperada:
   ```json
   {"status": "ok"}
   ```

2. **Documentación Interactiva (Swagger UI)**:
   Abre:
   ```
   https://<tu-servicio-render>.onrender.com/docs
   ```
   Podrás explorar y probar todos los endpoints de la API.

3. **Credenciales Iniciales de Administrador**:
   El comando pre-deploy crea automáticamente las credenciales iniciales:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`
   - **Rol**: `Admin`

   *Nota de seguridad*: Se recomienda cambiar la contraseña del usuario administrador una vez desplegado en producción.

---

## 🔗 Conectar el Frontend con el Backend en Render

En tu proyecto Frontend (`front_panalera`), configura tu archivo `.env.production` o la variable de entorno en tu plataforma de despliegue (Vercel, Netlify o Render):

```env
VITE_API_BASE_URL=https://panalera-backend.onrender.com/api/v1
```

> **Importante sobre CORS**: En la configuración del Web Service en Render, actualiza la variable `ALLOWED_ORIGINS` con la URL pública de tu frontend (por ejemplo: `https://mi-tienda-panalera.vercel.app,http://localhost:3000,http://localhost:5173`).

---

## 💡 Notas sobre el Plan Gratuito de Render

- **Inactividad (Spin-down)**: Los Web Services gratuitos en Render se suspenden tras 15 minutos sin recibir peticiones. La primera petición tras la inactividad puede tardar unos ~30-50 segundos en despertar el servidor.
- **Base de Datos Free**: Las bases de datos PostgreSQL gratuitas de Render están activas 24/7 de forma continua durante 30 días o el ciclo del plan gratuito.
- **Logs**: Puedes consultar los logs en tiempo real directamente en la pestaña **Logs** del servicio en Render.
