# Panalera Backend API

Sistema backend de gestión de inventario y ventas construido con **Python 3.13**, **FastAPI**, **SQLAlchemy (Async)** y **PostgreSQL**. Este proyecto sigue estrictamente los principios de **Clean Architecture** para garantizar un código testeable, mantenible y escalable.

## 📋 Requisitos Previos

Asegúrate de tener instaladas las siguientes herramientas en tu sistema:

- **Docker** y **Docker Compose**
- **Git**
- **Poetry** (opcional, solo si deseas desarrollar localmente sin Docker): `pip install poetry`
- **Postman** (para probar la API)

## ⚙️ Configuración de Variables de Entorno

El sistema requiere variables de entorno para funcionar. Debes crear un archivo `.env` en la raíz del proyecto.

1. Copia el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```
2. Abre `.env` y configura los valores (para desarrollo local con Docker, los valores por defecto suelen ser suficientes):
   ```env
   # Configuración de Base de Datos
   DATABASE_URL=postgresql+asyncpg://user:password@db:5432/dbname

   # Configuración de Seguridad
   SECRET_KEY=tu_clave_secreta_super_segura_de_64_caracteres_minimo
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

   # Entorno
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```
   *(Nota: si corres la app localmente con Poetry pero la base de datos en Docker, la URL debe ser `...user:password@localhost:5432...`)*

## 🐳 Instalación y Ejecución Local con Docker

La forma más rápida de levantar el proyecto es usando Docker Compose, que levantará la base de datos y la API simultáneamente.

1. Construye y levanta los contenedores en segundo plano:
   ```bash
   docker-compose -f docker/docker-compose.yml up --build -d
   ```
2. Verifica que los contenedores estén corriendo correctamente:
   ```bash
   docker-compose -f docker/docker-compose.yml ps
   ```
3. La API estará disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🗄️ Comandos para Ejecutar Migraciones (Alembic)

La base de datos debe ser inicializada con las tablas necesarias. Si estás usando la configuración de Docker Compose, puedes correr Alembic dentro del contenedor de la API:

1. **Crear una nueva migración** (después de modificar algún modelo en `src/infrastructure/database/models`):
   ```bash
   docker exec -it panalera_api alembic revision --autogenerate -m "nombre_del_cambio"
   ```
2. **Aplicar las migraciones a la base de datos** (Actualizar a la última versión):
   ```bash
   docker exec -it panalera_api alembic upgrade head
   ```

*(Si usas un entorno virtual local con Poetry, ejecuta directamente `alembic revision --autogenerate -m "..."` y `alembic upgrade head`).*

## 🧪 Comandos para Ejecutar Tests

El proyecto incluye tests unitarios y de integración usando `pytest`. Existe un `docker-compose.test.yml` si requieres levantar una DB exclusiva para tests.

Para ejecutar las pruebas en el entorno local (asumiendo que instalaste con `poetry install`):

```bash
# Correr todos los tests
poetry run pytest

# Correr tests con reporte de cobertura
poetry run pytest --cov=src tests/

# Correr tests con salida detallada
poetry run pytest -v
```

## 🚀 Instrucciones de Despliegue en Railway

Desplegar el backend en Railway es un proceso sencillo ya que el proyecto incluye un `Dockerfile`.

1. **Crear Proyecto en Railway**: Ve a tu dashboard de Railway y selecciona "New Project" > "Deploy from GitHub repo".
2. **Seleccionar el Repositorio**: Elige el repositorio donde está alojado este código.
3. **Añadir Base de Datos (Supabase o Railway)**:
   - Si usas Supabase (como se solicitó), ve al proyecto en Supabase, copia la cadena de conexión URI (asegúrate de cambiar `postgresql://` por `postgresql+asyncpg://` y añadir el pooler de conexión si es necesario).
   - Opcionalmente, puedes añadir el servicio "PostgreSQL" nativo de Railway a tu proyecto.
4. **Configurar Variables de Entorno**: En los "Settings" de tu servicio API en Railway, ve a "Variables" y añade todas las variables listadas en tu `.env` (asegúrate de usar la `DATABASE_URL` correcta apuntando a tu base de datos de producción).
5. **Configurar Dominio**: Ve a la pestaña "Networking" y genera un dominio público (ej. `panalera-api.up.railway.app`).
6. **Ejecutar Migraciones**:
   La forma más fácil de migrar en producción es conectarte localmente a la DB de producción.
   En tu terminal local, sobrescribe la variable de entorno y corre Alembic:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:password@prod-host:5432/prod-db"
   alembic upgrade head
   ```

## 📬 Cómo importar la colección Postman

Hemos proporcionado una colección de Postman pre-configurada para testear el flujo de la API.

1. Abre **Postman**.
2. Haz clic en el botón **Import** (esquina superior izquierda).
3. Selecciona la pestaña **File** o arrastra y suelta el archivo ubicado en `postman/inventory_api.postman_collection.json`.
4. Una vez importada, en el menú lateral verás la colección "Panalera Inventory API".
5. Ve a la pestaña **Variables** dentro de la configuración de la colección (haciendo clic en el nombre de la colección).
6. Asegúrate de que `base_url` apunte a tu entorno (`http://localhost:8000` o la URL de Railway).
7. **Autenticación Automática**: 
   - Ejecuta la petición `Auth > Login`.
   - El script de Postman extraerá automáticamente el `access_token` de la respuesta y lo guardará en la variable de entorno de la colección.
   - Las peticiones subsecuentes (Inventario, Usuarios, etc.) usarán este token automáticamente.
