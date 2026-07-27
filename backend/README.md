## 1. Descripción General

El backend es una API REST construida con **FastAPI** que permite a estudiantes registrar sus datos académicos (materias, evaluaciones, hábitos y sesiones de estudio) y recibir predicciones de rendimiento generadas por Machine Learning junto con recomendaciones personalizadas.

El sistema combina dos tecnologías de inteligencia artificial:
- **GradientBoostingRegressor** (scikit-learn) para predicciones numéricas de notas
- **Google Gemini** para procesamiento de lenguaje natural y extracción de datos desde texto libre

---

## 2. Arquitectura

```
                    ┌─────────────────┐
                    │     Frontend    │
                    │   (React/Vite)  │
                    └────────┬────────┘
                             │ HTTP/JSON
                             ▼
┌────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                  │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Routers  │  │ Schemas  │  │ Services │             │
│  │ (endpoints│→ │(valida-  │→ │(lógica de│             │
│  │  HTTP)    │  │ ción)    │  │ negocio) │             │
│  └──────────┘  └──────────┘  └──────────┘              │
│       │                            │                   │
│       ▼                            ▼                   │
│  ┌──────────┐              ┌──────────────┐            │
│  │  Models   │              │  ML / IA     │           │
│  │(SQLAlchemy│              │  Predictor   │           │
│  │  ORM)     │              │  + Gemini    │           │
│  └──────────┘              └──────────────┘            │
│       │                                                │
│       ▼                                                │
│  ┌──────────┐                                          │
│  │  SQLite   │                                         │
│  │(academico │                                         │
│  │  .db)     │                                         │
│  └──────────┘                                          │
└────────────────────────────────────────────────────────┘
```

### Flujo de datos

```
Estudiante escribe en chat de texto libre
  → Router /analisis/chat recibe el texto
  → ai_service llama a Google Gemini
  → Gemini extrae hábitos y registros de estudio
  → Se guardan en la base de datos
  → Cuando el estudiante pide predicciones:
    → Router /analisis/predicciones consulta la BD
    → Predictor ML calcula nota esperada por materia
    → Se retornan predicciones + factores
  → Cuando el estudiante pide recomendaciones:
    → Se calculan predicciones primero
    → Se intenta generar recomendaciones con Gemini
    → Si Gemini falla, se usa el generador basado en reglas
```

---

## 3. Estructura de Directorios

```
backend/
├── app/
│   ├── core/
│   │   └── database.py           # Configuración BD, settings, engine
│   │   └── __init__.py
│   ├── ml/
│   │   ├── predictor.py          # Motor ML (GradientBoostingRegressor)
│   │   ├── Master_ML.joblib      # Modelo entrenado persistido
│   │   ├── Master_ML_scaler.joblib # Scaler persistido
│   │   └── __init__.py
│   ├── models/
│   │   ├── models.py             # Modelos SQLAlchemy (tablas BD)
│   │   └── __init__.py
│   ├── routers/
│   │   ├── auth.py               # Autenticación (login, register, JWT)
│   │   ├── materias.py           # CRUD de materias
│   │   ├── evaluaciones.py       # CRUD de evaluaciones
│   │   ├── habitos.py            # CRUD de hábitos
│   │   ├── registros.py          # CRUD de registros de estudio
│   │   ├── analisis.py           # Predicciones, recomendaciones, chat IA
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── schemas.py            # Modelos Pydantic (validación request/response)
│   │   └── __init__.py
│   ├── services/
│   │   ├── recomendaciones.py    # Motor de recomendaciones basado en reglas (fallback)
│   │   ├── ai_service.py         # Servicio de IA con Google Gemini
│   │   └── __init__.py
│   ├── main.py                   # Entry point de la aplicación
│   └── __init__.py
├── tests/                        # Suite de tests
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_evaluaciones.py
│   ├── test_habitos.py
│   ├── test_materias.py
│   └── test_predictor.py
├── reentrenar.py                 # Script para reentrenar el modelo ML
├── requirements.txt              # Dependencias de Python
└── .env                          # Variables de entorno (no subir a git)
```

---

## 4. Base de Datos

### Motor: SQLite

Archivo: `app/academico.db`

### Modelos (tablas)

#### `usuarios`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | Integer (PK) | Identificador único |
| email | String(255) | Email del usuario (único) |
| hashed_password | String(255) | Contraseña hasheada con bcrypt |
| nombre | String(255) | Nombre completo |
| objetivo_promedio | Float | Meta de nota promedio (default 7.0) |
| created_at | DateTime | Fecha de registro |

#### `materias`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | Integer (PK) | Identificador único |
| usuario_id | Integer (FK → usuarios) | Dueño de la materia |
| nombre | String(255) | Nombre de la materia |
| objetivo_nota | Float | Meta de nota individual (default 7.0) |
| created_at | DateTime | Fecha de creación |

#### `evaluaciones`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | Integer (PK) | Identificador único |
| usuario_id | Integer (FK → usuarios) | Dueño de la evaluación |
| materia_id | Integer (FK → materias) | Materia asociada |
| tipo | String(50) | Tipo: examen, tarea, proyecto, quiz |
| nota | Float | Nota obtenida |
| ponderacion | Float | Peso de la evaluación (default 1.0) |
| fecha | DateTime | Fecha de la evaluación |

#### `registros_diarios`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | Integer (PK) | Identificador único |
| usuario_id | Integer (FK → usuarios) | Dueño del registro |
| materia_id | Integer (FK → materias, nullable) | Materia estudiada |
| fecha | DateTime | Fecha del registro |
| hora_inicio | DateTime | Inicio de la sesión |
| hora_fin | DateTime | Fin de la sesión |
| tipo_actividad | String(50) | Tipo: estudio, practica, repaso |
| descripcion | Text (nullable) | Descripción opcional |

#### `datos_habitos`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | Integer (PK) | Identificador único |
| usuario_id | Integer (FK → usuarios) | Dueño del hábito |
| fecha | DateTime | Fecha del hábito |
| tipo | String(50) | Tipo: descanso, distraccion, ejercicio, sueno, otro |
| duracion_minutos | Integer | Duración en minutos |
| notas | Text (nullable) | Notas opcionales |

### Relaciones

```
usuarios  1───N  materias        (un usuario tiene muchas materias)
usuarios  1───N  evaluaciones    (un usuario tiene muchas evaluaciones)
usuarios  1───N  registros       (un usuario tiene muchos registros)
usuarios  1───N  datos_habitos   (un usuario tiene muchos hábitos)
materias  1───N  evaluaciones    (una materia tiene muchas evaluaciones)
materias  1───N  registros       (una materia puede tener muchos registros)
```

Todas las relaciones hijo usan `cascade="all, delete-orphan"` para eliminación en cascada.

---

## 5. Autenticación

### Método: JWT (JSON Web Tokens) + bcrypt

#### Endpoints de auth

| Método | Ruta | Descripción | Auth requerida |
|--------|------|-------------|----------------|
| POST | /api/auth/register | Registrar nuevo usuario | No |
| POST | /api/auth/login | Iniciar sesión y obtener token | No |
| GET | /api/auth/me | Ver perfil del usuario actual | Sí |
| PUT | /api/auth/me | Actualizar perfil | Sí |

#### Flujo de autenticación

```
1. Usuario envía email + password a POST /api/auth/login
2. El sistema verifica las credenciales con bcrypt.checkpw()
3. Si son correctas, genera un JWT con el user_id como subject
4. El token tiene expiración configurable (default 30 min)
5. El frontend guarda el token y lo envía en cada request:
   Authorization: Bearer <token>
6. get_current_user() decodifica el token, obtiene el user_id,
   y consulta la BD para retornar el objeto Usuario
```

#### Hashing de contraseñas

```
Registro: password → bcrypt.gensalt() → bcrypt.hashpw() → guardar en BD
Login:    password + hash_en_BD → bcrypt.checkpw() → True/False
```

---

## 6. API Endpoints

### Prefijo global: `/api`

### Autenticación (`/api/auth`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | /api/auth/register | Registrar usuario | No |
| POST | /api/auth/login | Login, retorna JWT | No |
| GET | /api/auth/me | Datos del usuario actual | Sí |
| PUT | /api/auth/me | Actualizar perfil | Sí |

### Materias (`/api/materias`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | /api/materias | Listar materias del usuario | Sí |
| GET | /api/materias/{id} | Ver materia específica | Sí |
| POST | /api/materias | Crear materia | Sí |
| PUT | /api/materias/{id} | Editar materia | Sí |
| DELETE | /api/materias/{id} | Eliminar materia | Sí |

### Evaluaciones (`/api/evaluaciones`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | /api/evaluaciones | Listar evaluaciones (filtro: materia_id) | Sí |
| POST | /api/evaluaciones | Crear evaluación | Sí |
| PUT | /api/evaluaciones/{id} | Editar evaluación | Sí |
| DELETE | /api/evaluaciones/{id} | Eliminar evaluación | Sí |

### Hábitos (`/api/habitos`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | /api/habitos | Listar hábitos (filtro: tipo) | Sí |
| POST | /api/habitos | Crear hábito | Sí |
| PUT | /api/habitos/{id} | Editar hábito | Sí |
| DELETE | /api/habitos/{id} | Eliminar hábito | Sí |

### Registros de Estudio (`/api/registros`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | /api/registros | Listar registros (filtros: materia_id, fecha_inicio, fecha_fin) | Sí |
| POST | /api/registros | Crear registro | Sí |
| PUT | /api/registros/{id} | Editar registro | Sí |
| DELETE | /api/registros/{id} | Eliminar registro | Sí |

### Análisis y Predicciones (`/api/analisis`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | /api/analisis/predicciones | Predicciones de todas las materias | Sí |
| GET | /api/analisis/predicciones/{materia_id} | Predicción de una materia | Sí |
| GET | /api/analisis/recomendaciones | Recomendaciones personalizadas | Sí |
| GET | /api/analisis/estadisticas | Estadísticas generales del usuario | Sí |
| POST | /api/analisis/chat | Enviar texto libre, extraer datos con IA | Sí |

### Seguridad de endpoints

Todos los endpoints excepto `/register` y `/login` requieren autenticación mediante JWT Bearer token. Todos los endpoints de datos verifican ownership (el usuario solo puede acceder a sus propios datos).

---

## 7. Sistema de Machine Learning

### Archivo: `app/ml/predictor.py`

### Modelo: GradientBoostingRegressor

```
Algoritmo:    GradientBoostingRegressor
Estimators:   50
Max depth:    3
Learning rate: 0.1
Scaler:       StandardScaler
```

### Archivos persistidos

| Archivo | Contenido |
|---------|-----------|
| Master_ML.joblib | Modelo entrenado (GradientBoostingRegressor) |
| Master_ML_scaler.joblib | Scaler (StandardScaler) ajustado al modelo |

### Features del modelo

```
1. semana               → Semana del año (componente temporal)
2. mes                  → Mes (componente temporal)
3. dia_semana           → Día de la semana (0=lunes, 6=domingo)
4. minutos_estudio_materia → Minutos totales de estudio en esa materia
5. n_sesiones_estudio   → Cantidad de sesiones de estudio para esa materia
6. habito_descanso_semanal → Minutos de descanso por semana
7. habito_distraccion_semanal → Minutos de distracción por semana
8. habito_ejercicio_semanal → Minutos de ejercicio por semana
9. habito_sueno_semanal → Minutos de sueño por semana
10. ratio_estudio_distraccion → Descanso / (distracción + 1)
11. habito_calidad_promedio → 1 - (distracción / total_hábitos)
```

### Predicción por materia

```
Si hay modelo entrenado Y suficientes datos (≥5):
  → Extraer features de la materia
  → Escalar con StandardScaler
  → Predecir con GradientBoostingRegressor
  → Mezclar: nota_base × 0.3 + predicción_ML × 0.7
  → Clampear entre 1.0 y 10.0
  → Confianza: 0.75

Si no hay modelo o datos insuficientes:
  → Usar promedio histórico de la materia
  → Confianza: 0.35
```

### Reentrenamiento

No se ejecuta automáticamente. Se realiza mediante el script `reentrenar.py` que:
1. Conecta directamente a la base de datos
2. Recoge TODOS los datos de TODOS los usuarios
3. Entrena un nuevo modelo desde cero
4. Guarda los nuevos archivos .joblib
5. Reporta cantidad de muestras y confianza

---

## 8. Sistema de Inteligencia Artificial

### Archivo: `app/services/ai_service.py`

### Proveedor: Google Gemini 

### Flujo del endpoint `/api/analisis/chat`

```
1. Recibe texto libre del estudiante
2. Consulta las materias del usuario en la BD
3. Construye un prompt con:
   - Lista de materias del usuario (id + nombre)
   - Texto del estudiante
   - Instrucciones de extracción
4. Envía el prompt a Google Gemini
5. Parsea la respuesta JSON de Gemini
6. Valida y guarda los datos extraídos:
   - Hábitos → tabla datos_habitos
   - Registros de estudio → tabla registros_diarios
7. Retorna la respuesta conversacional de Gemini
```

### Prompt enviado a Gemini

El prompt incluye:
- Las materias del usuario (para matchear nombres a IDs)
- El texto original del estudiante
- Instrucciones para extraer: hábitos (tipo, duración), registros (materia, horas), respuesta conversacional
- Formato JSON esperado como respuesta

### Validación de datos extraídos

```
Hábitos:
  → Tipo validado contra: descanso, distraccion, ejercicio, sueno, otro
  → Duración debe ser número positivo
  → Se ignoran hábitos con duración ≤ 0

Registros:
  → materia_id verificado contra las materias del usuario
  → Horas parseadas en formato HH:MM o HH:MM:SS
  → Si hora_fin ≤ hora_inicio, se ajusta sumando 1 día
  → tipo_actividad validado contra: estudio, practica, repaso
```

### Fallback de recomendaciones

```
Si Gemini está disponible:
  → Las recomendaciones se generan con IA (futuro)
  
Si Gemini falla:
  → Se usa GeneradorRecomendaciones (recomendaciones.py)
  → Motor basado en reglas IF/ELSE
  → Analiza hábitos, rendimiento y registros de estudio
```

---

## 9. Servicio de Recomendaciones (Fallback)

### Archivo: `app/services/recomendaciones.py`

### Método basado en reglas que analiza 3 aspectos:

#### Análisis de hábitos
| Condición | Recomendación |
|-----------|---------------|
| Distracción > 120 min | "Reduce distracciones, usa Pomodoro" |
| Distracción > 60 min | "Cuidado con distracciones" |
| Descanso < 30 min | "Toma más descansos" |
| Sueño < 420 min (7h) | "Duerme más" |
| Ejercicio < 20 min | "Haz más ejercicio" |

#### Análisis de rendimiento
| Condición | Recomendación |
|-----------|---------------|
| Sin evaluaciones | "Registra tus evaluaciones" |
| Nota materia < 5.0 | "Riesgo en [materia]" |
| Nota materia < objetivo - 0.5 | "Mejora en [materia]" |
| Nota materia ≥ objetivo | "¡Bien en [materia]!" |
| Tendencia negativa ML | "Tendencia a la baja en [materia]" |

#### Análisis de registros de estudio
| Condición | Recomendación |
|-----------|---------------|
| Sin registros | "Registra tu tiempo de estudio" |
| Sesiones < 30 min promedio | "Sesiones muy cortas" |
| < 2 sesiones | "Estudia con más frecuencia" |
| < 3 horas totales | "Aumenta tu tiempo de estudio" |
| Materias sin estudio | "Distribuye tu tiempo" |

Máximo de recomendaciones retornadas: 10

---

## 10. Scripts

### `reentrenar.py`

Ubicación: `backend/reentrenar.py`

```
Uso: python reentrenar.py
```

Qué hace:
1. Conecta a la base de datos directamente (sin autenticación de usuario)
2. Lee todas las evaluaciones, hábitos y registros
3. Entrena el modelo GradientBoostingRegressor con esos datos
4. Guarda los nuevos archivos .joblib
5. Reporta: muestras usadas y confianza del modelo

---

## 11. Configuración

### Variables de entorno (`.env`)

```env
DATABASE_URL=sqlite:///./app/academico.db
SECRET_KEY=tu_secret_key_muy_segura_aqui_cambiala
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=tu_api_key_de_google_aqui
```

### Archivo de configuración: `app/core/database.py`

Usa `pydantic-settings` para cargar variables del `.env`. Si una variable no está en el `.env`, usa el valor por defecto definido en la clase `Settings`.

---

## 12. Ejecución

### Iniciar el servidor

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Documentación interactiva

```
Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
```

### Reentrenar el modelo ML

```bash
cd backend
python reentrenar.py
```

---

## 13. Mapa completo de endpoints

```
AUTH:
  POST   /api/auth/register             → Crear cuenta
  POST   /api/auth/login                → Obtener JWT
  GET    /api/auth/me                   → Ver perfil
  PUT    /api/auth/me                   → Editar perfil

MATERIAS:
  GET    /api/materias                  → Listar materias
  GET    /api/materias/{id}             → Ver materia
  POST   /api/materias                  → Crear materia
  PUT    /api/materias/{id}             → Editar materia
  DELETE /api/materias/{id}             → Eliminar materia

EVALUACIONES:
  GET    /api/evaluaciones              → Listar evaluaciones
  POST   /api/evaluaciones              → Crear evaluación
  PUT    /api/evaluaciones/{id}         → Editar evaluación
  DELETE /api/evaluaciones/{id}         → Eliminar evaluación

HÁBITOS:
  GET    /api/habitos                   → Listar hábitos
  POST   /api/habitos                   → Crear hábito
  PUT    /api/habitos/{id}              → Editar hábito
  DELETE /api/habitos/{id}              → Eliminar hábito

REGISTROS:
  GET    /api/registros                 → Listar registros
  POST   /api/registros                 → Crear registro
  PUT    /api/registros/{id}            → Editar registro
  DELETE /api/registros/{id}            → Eliminar registro

ANÁLISIS:
  GET    /api/analisis/predicciones          → Predicciones generales
  GET    /api/analisis/predicciones/{id}     → Predicción por materia
  GET    /api/analisis/recomendaciones       → Recomendaciones
  GET    /api/analisis/estadisticas          → Estadísticas
  POST   /api/analisis/chat                  → Chat con IA (extrae datos)

TOTAL: 22 endpoints
```