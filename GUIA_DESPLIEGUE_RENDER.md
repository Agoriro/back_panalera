# 🚀 Guía de Despliegue: Backend en Render + Base de Datos en Supabase

Esta arquitectura es la recomendada para evitar los límites del plan gratuito de Render (Render solo permite **1 sola base de datos gratuita por cuenta**, la cual además expira cada 30 días).

Al usar **Supabase (PostgreSQL gratuito y permanente)** para la base de datos y **Render** para el backend (**FastAPI**), obtienes la mejor combinación 100% gratuita y sin conflictos.

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
     pip install poetry && poetry config virtualenvs.create false && poetry install --only main
     ```
   - **Start Command**:
     ```bash
     alembic upgrade head && python seed_db.py && uvicorn src.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: `Free`.
4. Agrega las **Variables de Entorno** (**Environment Variables**):

| Variable | Valor | Descripción |
| :--- | :--- | :--- |
| `DATABASE_URL` | *Pega la URI de Supabase* | URL de conexión de Supabase |
| `SECRET_KEY` | *Genera un texto seguro de 32+ caracteres* | Firma para tokens JWT |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Duración del token de acceso |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duración del refresh token |
| `ALLOWED_ORIGINS` | `*` o la URL de tu frontend | CORS para el frontend |
| `ENVIRONMENT` | `production` | Modo de ejecución |
| `PYTHON_VERSION` | `3.13.0` | Versión de Python |

5. Haz clic en **Create Web Service**.

---

## 🔄 ¿Qué ocurre durante el Despliegue?

Cuando Render inicia el servicio web:
1. Se conecta a **Supabase** usando tu `DATABASE_URL`.
2. Ejecuta automáticamente `alembic upgrade head` para crear todas las tablas en Supabase.
3. Ejecuta `python seed_db.py` para crear el rol `Admin` y el usuario inicial `admin` / `admin123`.
4. Levanta FastAPI en Uvicorn.

---

## 🔍 Verificación

Una vez que el despliegue esté en verde (**Live**):

1. **Health Check**:
   ```
   https://<tu-servicio-render>.onrender.com/health
   ```
   Retorna: `{"status": "ok"}`

2. **Swagger Docs**:
   ```
   https://<tu-servicio-render>.onrender.com/docs
   ```

3. **Ver tablas en Supabase**:
   Puedes ir al panel de Supabase > **Table Editor** y verás todas las tablas (`users`, `inventory`, `movements`, `roles`, etc.) y el usuario `admin` ya creados.
