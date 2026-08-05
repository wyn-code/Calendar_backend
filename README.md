# Agenda Psicóloga — Backend

Backend para la agenda de una psicóloga, construido como plantilla profesional lista para escalar.

## Stack

- **Python 3.13+**
- **FastAPI**
- **SQLAlchemy 2.0** (ORM, tipado con `Mapped` / `mapped_column`)
- **Alembic** (migraciones de base de datos)
- **PostgreSQL** (driver `psycopg3`)
- **Pydantic v2** + **pydantic-settings**
- **JWT** (PyJWT) + **Passlib/bcrypt**
- **Uvicorn**

## Estructura

```
backend/
├── alembic/                 # Migraciones (env.py detecta Base.metadata)
├── app/
│   ├── api/routes/          # Routers HTTP (auth, patients, appointments, obra_social, health)
│   ├── core/                # config, database, security, dependencies
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic (Create / Update / Response)
│   ├── repositories/        # Capa de acceso a datos (CRUD genérico en base.py)
│   ├── services/            # Lógica de negocio (stubs)
│   ├── utils/               # Utilidades auxiliares
│   └── main.py              # Punto de entrada de la aplicación
├── .env.example
├── alembic.ini
└── requirements.txt
```

> Los **services** son stubs que lanzan `NotImplementedError`: la lógica de negocio y
> los endpoints completos se implementan en la siguiente etapa.

## Arquitectura por capas

```
Router (app/api/routes) → Service (app/services) → Repository (app/repositories) → Database
```

- Los **routers** solo manejan HTTP y delegan en los servicios.
- Los **services** contienen la lógica de negocio (p. ej. reglas de turnos, autenticación).
- Los **repositories** encapsulan el acceso a datos (CRUD genérico reutilizable).
- Todo el ORM se construye sobre la `Base` declarativa de `app/core/database.py`.

## Requisitos previos

- Python 3.13 o superior instalado.
- PostgreSQL en ejecución y una base de datos creada (p. ej. `calend`).

## Instalación

### 1. Crear el entorno virtual

Desde la carpeta `backend`:

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
py -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Linux / macOS
cp .env.example .env

# Windows
copy .env.example .env
```

Edita `.env` y ajusta al menos:

- `DATABASE_URL` con tus credenciales de PostgreSQL (formato `postgresql+psycopg://usuario:password@host:puerto/nombre_bd`).
- `SECRET_KEY` con una clave aleatoria segura (genera una con `python -c "import secrets; print(secrets.token_hex(32))"`).
- `CORS_ORIGINS` con la URL de tu frontend React (por defecto `http://localhost:5173`).

## Migraciones con Alembic

### Generar la primera migración

```bash
alembic revision --autogenerate -m "create initial tables"
```

Esto detecta automáticamente todos los modelos importados en `app/models` y
genera la migración de las tablas `users`, `patients`, `obras_sociales` y `appointments`.

### Aplicar las migraciones

```bash
alembic upgrade head
```

Otros comandos útiles:

```bash
alembic downgrade -1       # deshace la última migración
alembic current            # versión actual de la base
alembic history            # historial de migraciones
```

## Ejecutar el servidor

Con el entorno virtual activo, desde la carpeta `backend`:

```bash
uvicorn app.main:app --reload
```

- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs
- Documentación ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/api/v1/health

## Endpoints disponibles (stubs)

| Método | Ruta                          | Descripción               |
| ------ | ----------------------------- | ------------------------- |
| GET    | `/api/v1/health`              | Estado de la API y la BD  |
| POST   | `/api/v1/auth/register`       | Registro de usuario       |
| POST   | `/api/v1/auth/login`          | Login (OAuth2 form)       |
| GET    | `/api/v1/auth/me`             | Usuario autenticado       |
| CRUD   | `/api/v1/patients`            | Pacientes (autenticado)   |
| CRUD   | `/api/v1/appointments`        | Turnos (autenticado)      |
| CRUD   | `/api/v1/obra-social`         | Obras sociales (autent.)  |

## Notas

- El login usa el flujo **OAuth2 password** (form-data `username`/`password`); el campo
  `username` corresponde al **email** del usuario.
- Las contraseñas se hashean con **bcrypt** (`app/core/security.py`) y nunca se devuelven en las respuestas.
- Los esquemas `Response` usan `from_attributes=True` para serializar modelos ORM directamente.
- `get_current_user` (`app/core/dependencies.py`) es la dependencia de protección de las rutas autenticadas.
