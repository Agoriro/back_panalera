# 🚀 Guía de Despliegue: Backend en Render + Base de Datos en Supabase

Esta arquitectura usa un servicio web `starter` para disponer de pre-deploy seguro. El plan gratuito sirve para pruebas, pero no incluye pre-deploy y Render no lo recomienda para producción.

Supabase aloja PostgreSQL y Render ejecuta FastAPI. Confirma límites y retención del plan de base de datos elegido antes del despliegue.

---

## 📋 Arquitectura

```
┌────────────────────────────────────────────────────────┐
│                        SUPABASE                        │
│                                                        │
│                  ┌──────────────────┐                  │
│                  │  PostgreSQL DB   │                  │
│                  │  (Gratuito/24/7) │                  │
│                  └────────▲─────────┘                  │
└───────────────────────────┼────────────────────────────┘
                            │
               DATABASE_URL │ (Conexión segura IPv4/SSL)
                            │
┌───────────────────────────┼────────────────────────────┐
│                        RENDER                          │
│                                                        │
│                  ┌────────┴─────────┐                  │
│                  │   Web Service    │                  │
│                  │ (FastAPI/Python) │                  │
│                  └────────┬─────────┘                  │
└───────────────────────────┼────────────────────────────┘
                            │ Public HTTPS URL (/api/v1)
                            ▼
                [ Frontend / Vercel / App ]
```

---

## 🗄️ Paso 1: Configurar la Base de Datos en Supabase (2 minutos)

1. Ingresa a **[supabase.com](https://supabase.com/)** e inicia sesión (o crea cuenta gratis con GitHub).
2. Haz clic en **New Project**.
3. Configura el proyecto:
   - **Name**: `panalera-db`
   - **Database Password**: Elige una contraseña segura (¡guárdala!).
   - **Region**: Selecciona la más cercana (ej. *East US* o *West US*).
   - **Pricing Plan**: `Free`.
4. Haz clic en **Create new project** y espera ~1 minuto a que se aprovisione.
5. **Obtener la URL de conexión**:
   - En el menú lateral izquierdo, ve a ⚙️ **Project Settings** > **Database**.
   - Desplázate hacia abajo hasta la sección **Connection parameters** o **Connection string** > pestaña **URI**.
   - Si usas el nuevo panel de Supabase:
     - Selecciona **Nodejs** o **URI** / **Connection Pooling** (Modo **Session**, puerto `5432`).
   - La URL tendrá una estructura como esta:
     ```text
     postgresql://postgres.[PROJECT-REF]:[TU-CONTRASEÑA]@aws-0-[REGION].pooler.supabase.com:5432/postgres
     ```
     *(o la URL directa `postgresql://postgres:[TU-CONTRASEÑA]@db.[PROJECT-REF].supabase.co:5432/postgres`)*.

---

## ⚙️ Paso 2: Desplegar el Backend en Render

### Opción A: Con Render Blueprint (`render.yaml`) - Recomendado

1. Sube los cambios más recientes a tu repositorio:
   ```bash
   git add .
   git commit -m "Configurar Render con Supabase"
   git push origin main
   ```
2. Ve a [dashboard.render.com](https://dashboard.render.com/) > **New +** > **Blueprint**.
3. Selecciona tu repositorio `back_panalera`.
4. Render detectará el servicio `panalera-backend` y te solicitará ingresar el valor de:
   - **DATABASE_URL**: Pega la URI de Supabase obtenida en el Paso 1.
5. Haz clic en **Apply**.

---

### Opción B: Creando el Web Service Manualmente en Render

1. En Render Dashboard, haz clic en **New +** > **Web Service**.
2. Conecta tu repositorio `back_panalera`.
3. Configura los campos:
   - **Name**: `panalera-backend`
   - **Language / Runtime**: `Python 3`
   - **Region**: La más cercana a tu base de datos de Supabase.
   - **Branch**: `main`.
   - **Build Command**:
     ```bash
     pip install poetry==1.8.3 && poetry config virtualenvs.create false && poetry install --only main --sync
     ```
   - **Pre-Deploy Command**:
     ```bash
     alembic upgrade head
     ```
   - **Start Command**:
     ```bash
     uvicorn src.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips=*
     ```
   - **Plan**: `Starter` o superior; pre-deploy no está disponible en `Free`.
4. Agrega las **Variables de Entorno** (**Environment Variables**):

| Variable | Valor | Descripción |
| :--- | :--- | :--- |
| `DATABASE_URL` | *Pega la URI de Supabase* | URL de conexión de Supabase |
| `SECRET_KEY` | *Genera un texto seguro de 32+ caracteres* | Firma para tokens JWT |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Duración del token de acceso |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duración del refresh token |
| `ALLOWED_ORIGINS` | `https://tu-frontend.example` | Lista CORS explícita, separada por comas; nunca `*` |
| `ENVIRONMENT` | `production` | Modo de ejecución |
| `PYTHON_VERSION` | `3.13.7` | Versión de Python fijada |
| `DB_POOL_SIZE` | `5` | Conexiones persistentes por proceso |
| `DB_MAX_OVERFLOW` | `10` | Conexiones temporales máximas |
| `DB_POOL_TIMEOUT_SECONDS` | `10` | Espera máxima por conexión |
| `DB_POOL_RECYCLE_SECONDS` | `1800` | Reciclaje preventivo de conexiones |
| `DB_COMMAND_TIMEOUT_SECONDS` | `30` | Timeout de comandos PostgreSQL |
| `DB_HEALTH_TIMEOUT_SECONDS` | `3` | Timeout del readiness check |

5. Haz clic en **Create Web Service**.

---

## 🔄 ¿Qué ocurre durante el Despliegue?

Cuando Render inicia el servicio web:
1. Se conecta a **Supabase** usando tu `DATABASE_URL`.
2. En pre-deploy ejecuta únicamente `alembic upgrade head`. El administrador existente no se modifica.
3. Levanta Uvicorn con soporte de proxy. Render es el límite de confianza que entrega el IP real; no uses `--forwarded-allow-ips=*` fuera de una plataforma con proxy controlado.

---

## 🔍 Verificación

Una vez que el despliegue esté en verde (**Live**):

1. **Health Check**:
   ```
   https://<tu-servicio-render>.onrender.com/health/live
   ```
   Retorna: `{"status": "ok"}`

   Readiness con DB:
   ```text
   https://<tu-servicio-render>.onrender.com/health/ready
   ```
   Devuelve `503` cuando PostgreSQL no está disponible.

2. **Swagger Docs**:
   ```
   https://<tu-servicio-render>.onrender.com/docs
   ```

3. **Ver tablas en Supabase**:
   Puedes ir al panel de Supabase > **Table Editor** y verás todas las tablas (`users`, `inventory`, `movements`, `roles`, etc.) y el usuario `admin` ya creados.

---

## Migración y rollback

Antes de desplegar:

1. Crea un backup o snapshot de PostgreSQL.
2. Revisa la revisión activa con `poetry run alembic current`.
3. Revisa destino con `poetry run alembic heads`.
4. Aplica en staging: `poetry run alembic upgrade head`.
5. Ejecuta pruebas de humo sobre `/health/ready`, login y consultas principales.

Rollback de una revisión:

```bash
poetry run alembic downgrade -1
```

Después despliega el commit de aplicación compatible con esa revisión. Si una migración transformó o eliminó datos, restaura el backup; `downgrade` no garantiza recuperar datos perdidos. No ejecutes migraciones manuales concurrentes con el pre-deploy de Render.

`src.seed_db` es implementación canónica. `seed_db.py` en raíz solo conserva compatibilidad y delega en ella; no contiene lógica duplicada.
