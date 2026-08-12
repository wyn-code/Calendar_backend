# Agenda Psicóloga — Backend API

API REST para la gestión de la agenda de una psicóloga: administración de pacientes, turnos y obras sociales, con exportación del calendario mensual a Excel y de la planilla de sesiones a PDF.

Backend construido como **proyecto profesional de producción** aplicando arquitectura por capas, patrones de diseño consolidados y buenas prácticas (tipado estático, migraciones, seguridad JWT y separación de responsabilidades).

---

## Funcionalidades

- **Autenticación JWT** con registro, login y sesión persistente (`remember_me`).
- **CRUD completo** de pacientes, turnos (appointments) y obras sociales.
- **Búsqueda y paginación** de pacientes por nombre.
- **Validación de reglas de negocio** a nivel de esquema: un turno de tipo *Obra Social* exige `obra_social_id`; cada turno requiere un paciente (por `id` o por nombre, con reutilización/creación automática).
- **Exportación del calendario mensual a Excel (.xlsx)**, replicando el diseño de la UI web (colores, badges de cobertura, resaltado del día actual).
- **Exportación de la planilla mensual de sesiones a PDF**, agrupada por paciente, con logo y nombre del profesional.
- **Health check** de la API y la base de datos.

---

## Stack tecnológico

| Capa | Tecnología |
| --- | --- |
| Lenguaje | Python 3.13+ |
| Framework web | FastAPI (async-ready, OpenAPI/Swagger automático) |
| ORM | SQLAlchemy 2.0 (tipado `Mapped` / `mapped_column`) |
| Migraciones | Alembic |
| Base de datos | PostgreSQL (driver `psycopg3`) |
| Validación | Pydantic v2 (`pydantic-settings`, `EmailStr`, validadores de modelo) |
| Autenticación | PyJWT + Passlib/bcrypt (OAuth2 Bearer) |
| Exportación Excel | openpyxl (rich text, estilos y rangos) |
| Exportación PDF | ReportLab (Platypus, tablas y gráficos vectoriales) |
| Servidor | Uvicorn |
| CORS | Configurable por entorno (frontend React desplegado en Vercel) |

---

## Arquitectura por capas

El sistema sigue una **arquitectura en capas (layered architecture)** con flujo de dependencias unidireccional y descendente:

```
HTTP (FastAPI)
   │
   ▼
Router / Endpoint  ───── app/api/routes
   │                (solo maneja HTTP: parsing, status codes, respuestas)
   ▼
Service           ───── app/services
   │                (lógica de negocio: reglas, orquestación, errores 4xx)
   ▼
Repository        ───── app/repositories
   │                (acceso a datos, consultas, CRUD)
   ▼
Database (PostgreSQL)
```

Cada capa solo conoce a la inmediata inferior y nunca a la superior: los routers no tocan la base de datos, los servicios no exponen HTTP y los repositorios no contienen lógica de negocio.

### Detalle por capa

1. **Router (`app/api/routes`)** — Endpoints delgados. Reciben el payload, instancian el servicio (inyectándole la sesión de BD) y devuelven la respuesta tipada. Ej.: `app/api/routes/patients.py`.
2. **Service (`app/services`)** — Orquesta la lógica de negocio y decide qué es un error de dominio (devuelve `HTTPException` 404/409/401 con intención). Ej.: `AppointmentService` resuelve si se reutiliza o crea un paciente (`_find_or_create_patient`).
3. **Repository (`app/repositories`)** — Encapsula el acceso a datos sobre un `BaseRepository` genérico; los repositorios específicos agregan consultas de dominio (p. ej. `AppointmentRepository.get_by_month` con `joinedload` para evitar N+1).
4. **Schema (`app/schemas`)** — Contratos Pydantic `Create` / `Update` / `Response` con validación y serialización ORM (`from_attributes=True`).
5. **Model (`app/models`)** — Modelos SQLAlchemy sobre una `Base` declarativa central (`app/core/database.py`).

---

## Patrones de diseño aplicados

- **Repository Pattern** — Abstracción completa del acceso a datos. `BaseRepository[ModelType]` provee un CRUD genérico reutilizable; los repositorios de dominio lo extienden. El resto de la app depende de la abstracción, no del ORM.
- **Generic / TypeVar** — `BaseRepository` es genérico (`Generic[ModelType]`) y se especializa por entidad (`UserRepository`, `PatientRepository`, …), dando CRUD tipado sin duplicar código.
- **Service Layer** — Una capa de servicios separa la lógica de negocio del HTTP y del ORM, haciendo el dominio testeable e independiente del framework.
- **Dependency Injection** — FastAPI `Depends` inyecta la sesión de base de datos (`get_db`) y la autenticación (`get_current_user`) mediante `Annotated`, con dependencias reutilizables y componibles.
- **Singleton / Caching** — La configuración es una instancia única cacheada con `@lru_cache` (`get_settings`), evitando re-leer `.env` en cada import.
- **DTO (Data Transfer Object)** — Los schemas Pydantic `Create`/`Update`/`Response` definen los contratos de entrada/salida y desacoplan la API del modelo ORM (nunca se exponen campos sensibles como `password_hash`).
- **Data Mapper** — SQLAlchemy actúa como *data mapper*: objetos de dominio desacoplados del esquema SQL, sincronizados explícitamente por la sesión.
- **Factory** — Los repositorios se construyen a partir de una sesión y un modelo concreto; los servicios fabrican sus repositorios internos (composición).
- **Template Method (implícito)** — `BaseRepository` define el esqueleto de las operaciones; las subclases solo aportan las consultas específicas.
- **Composición sobre herencia** — Los servicios componen múltiples repositorios (ej. `AppointmentService` usa `AppointmentRepository` + `PatientRepository`).
- **Separación de infraestructura** — La generación de archivos (Excel/PDF) vive en servicios dedicados (`CalendarioExcelService`, `PlanillaPdfService`) que reciben la sesión y devuelven un `BytesIO`, desacoplados del transporte HTTP.

---

## Estructura del proyecto

```
backend/
├── alembic/                    # Migraciones (env.py inyecta DATABASE_URL y Base.metadata)
│   └── env.py
├── app/
│   ├── main.py                 # App FastAPI: CORS, routers, versión
│   ├── api/
│   │   └── routes/             # Capa HTTP
│   │       ├── health.py       # GET /health
│   │       ├── auth.py         # /auth/register, /auth/login, /auth/me
│   │       ├── patients.py     # CRUD pacientes (+ search/paginación)
│   │       ├── appointments.py # CRUD turnos
│   │       ├── obra_social.py  # CRUD obras sociales
│   │       └── export.py       # /export/calendario (xlsx), /export/planilla-sesiones (pdf)
│   ├── core/                   # Infraestructura transversal
│   │   ├── config.py           # Settings (pydantic-settings, .env)
│   │   ├── database.py         # engine, SessionLocal, Base declarativa, get_db
│   │   ├── security.py         # bcrypt + JWT (hash, verify, create/decode token)
│   │   └── dependencies.py     # get_current_user, DbSession (OAuth2 Bearer)
│   ├── models/                 # ORM: user, patient, appointment, obra_social
│   ├── schemas/                # Pydantic: auth, user, patient, appointment, obra_social
│   ├── repositories/           # base.py (CRUD genérico) + repos por entidad
│   ├── services/               # auth, patient, appointment, obra_social,
│   │                           # calendario (xlsx), planilla (pdf)
│   └── assets/                 # Recursos (logo para el PDF)
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## Modelo de datos

```
users (id, email UNIQUE, password_hash, nombre, activo, created_at)
   │ 1:N
   ├── patients (id, user_id?, nombre_completo, telefono, obra_social_id?, observaciones, timestamps)
   │       │ N:1 obra_sociales (id, nombre UNIQUE)
   │       │ 1:N
   │       └── appointments (id, user_id?, patient_id, obra_social_id?, fecha, hora_inicio,
   │                         tipo_consulta, observaciones, timestamps)
   └── appointments (relación directa del usuario)
```

- Relaciones bidireccionales con `back_populates` y borrado en cascada (`cascade="all, delete-orphan"`).
- Timestamps manejados por la base (`server_default=func.now()` / `onupdate`).
- FKs opcionales (`user_id`, `obra_social_id`) modelan cobertura particular vs. obra social.

---

## Seguridad

- **Hash de contraseñas con bcrypt** (`passlib`) — nunca se devuelve el hash en las respuestas.
- **JWT firmado (HS256)** con expiración configurable por entorno; `sub` = id de usuario.
- **Sesión extendida** opcional (`remember_me`): token de 30 días vs. 60 minutos.
- **Protección de rutas** vía `get_current_user` (OAuth2 Bearer); valida firma, existencia y estado `activo` del usuario.
- **Configuración sensible** solo en `.env` (ignorado por git); `SECRET_KEY` sin valor por defecto.
- **CORS** restringido a orígenes permitidos (frontend React en `localhost` y Vercel).

---

## Endpoints

| Método | Ruta | Descripción | Auth |
| --- | --- | --- | --- |
| GET | `/api/v1/health` | Estado de API y BD | — |
| POST | `/api/v1/auth/register` | Registro (email, contraseña ≥8, nombre) | — |
| POST | `/api/v1/auth/login` | Login → JWT (+ `remember_me`) | — |
| GET | `/api/v1/auth/me` | Usuario autenticado | ✅ |
| POST | `/api/v1/patients/` | Crear paciente | ✅ |
| GET | `/api/v1/patients/` | Listar (search, skip, limit) | ✅ |
| GET | `/api/v1/patients/{id}` | Obtener paciente | ✅ |
| PUT | `/api/v1/patients/{id}` | Actualizar paciente | ✅ |
| DELETE | `/api/v1/patients/{id}` | Eliminar paciente | ✅ |
| POST | `/api/v1/appointments/` | Crear turno | ✅ |
| GET | `/api/v1/appointments/` | Listar turnos | ✅ |
| GET | `/api/v1/appointments/{id}` | Obtener turno | ✅ |
| PUT | `/api/v1/appointments/{id}` | Actualizar turno | ✅ |
| DELETE | `/api/v1/appointments/{id}` | Eliminar turno | ✅ |
| CRUD | `/api/v1/obra-social/` | Obras sociales | ✅ |
| GET | `/api/v1/export/calendario?year=&month=` | Calendario mensual .xlsx | ✅ |
| GET | `/api/v1/export/planilla-sesiones?year=&month=` | Planilla de sesiones .pdf | ✅ |

> Swagger interactivo: `http://127.0.0.1:8000/docs` · ReDoc: `http://127.0.0.1:8000/redoc`

---

## Instalación y ejecución

### 1. Entorno virtual

```bash
# Linux / macOS
python3 -m venv .venv && source .venv/bin/activate
# Windows
py -m venv .venv && .venv\Scripts\activate
```

### 2. Dependencias

```bash
pip install -r requirements.txt
```

### 3. Variables de entorno

```bash
cp .env.example .env   # Linux/macOS — Windows: copy .env.example .env
```

Ajustar al menos:

- `DATABASE_URL` → `postgresql+psycopg://usuario:password@host:puerto/nombre_bd`
- `SECRET_KEY` → `python -c "import secrets; print(secrets.token_hex(32))"`
- `CORS_ORIGINS` → URL del frontend (por defecto `http://localhost:5173`)

### 4. Migraciones (Alembic)

```bash
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
```

`alembic/env.py` toma la URL de `settings` y descubre los modelos desde `app/models`, por lo que `alembic.ini` no repite credenciales.

### 5. Servidor

```bash
uvicorn app.main:app --reload
```

---

## Decisiones de diseño destacadas

- **`AppointmentCreate` admite `patient_id` o `nombre_completo`**: el service resuelve la FK (reutiliza por nombre o crea), simplificando el alta desde el frontend — decisión UX con lógica centralizada en el backend.
- **Anti N+1**: `get_by_month` usa `joinedload` para precargar `patient` y `obra_social`, crucial en exportaciones que recorren todo el mes.
- **Configuración cacheada con `@lru_cache`** y `extra="ignore"` para tolerar variables de más en `.env`.
- **Exportaciones desacopladas**: los servicios devuelven `BytesIO`, los routers deciden el `media_type` y el `Content-Disposition` (`StreamingResponse`).
- **PDF sin dependencia de glifos Unicode**: el check de la planilla se dibuja como polígono vectorial (ReportLab), garantizando renderizado en cualquier lector.

---

## Roadmap (en progreso)

- Middleware de **tenancy**: filtrar pacientes/turnos por `user_id` del token autenticado.
- **Testing automatizado** (pytest + base de datos de prueba).
- Endpoints de **estadísticas** y dashboard.
- **Rate limiting** e integración continua (CI/CD).
