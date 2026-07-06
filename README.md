# Sistema de Predicción de Rendimiento Académico

## Estructura del Proyecto

```
Sistema_Academico/
├── backend/                 # API con FastAPI
│   ├── app/
│   │   ├── core/           # Configuración de base de datos
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── routers/       # Endpoints de API
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── ml/            # Modelos de Machine Learning
│   │   └── services/      # Lógica de recomendaciones
│   └── requirements.txt
│
└── frontend/               # React + Vite
    └── src/
        ├── components/
        ├── pages/
        ├── services/
        └── context/
```

## Requisitos Previos

- Python 3.9+
- Node.js 18+
- npm o yarn

## Instalación y Ejecución

### 1. Backend (Python/FastAPI)

```bash
# Crear entorno virtual
cd backend
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor
uvicorn app.main:app --reload


El backend estará disponible en: `http://localhost:8000`


# Para desactivar el entorno virtual ejecuta
deactivate

# para ver que librerias de python tienes instalado en tu entorno virtual ejecuta este comando 
pip list

```

### 2. Frontend (React + Vite)

```bash
# En otra terminal
cd frontend

# Instalar dependencias
npm install

# Ejecutar el servidor de desarrollo
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register` | Registrar usuario |
| POST | `/api/auth/login` | Iniciar sesión |
| GET | `/api/auth/me` | Obtener usuario actual |
| GET/POST/PUT/DELETE | `/api/materias` | CRUD de materias |
| GET/POST/DELETE | `/api/habitos` | CRUD de hábitos |
| GET/POST/DELETE | `/api/evaluaciones` | CRUD de evaluaciones |
| GET/POST | `/api/registros` | CRUD de registros de estudio |
| GET | `/api/analisis/predicciones` | Obtener predicciones |
| GET | `/api/analisis/recomendaciones` | Obtener recomendaciones |
| GET | `/api/analisis/estadisticas` | Obtener estadísticas |

## Uso del Sistema

1. **Registrarse** en la aplicación
2. **Agregar materias** que estás cursando
3. **Registrar evaluaciones** (exámenes, tareas, proyectos)
4. **Registrar hábitos** (descansos, distracciones, sueño)
5. **Registrar tiempo de estudio** diario
6. **Ver predicciones** y recomendaciones en el dashboard

## Funcionalidades de IA

- **Predicción de notas**: Utiliza Gradient Boosting Regressor para predecir el rendimiento futuro
- **Análisis de tendencias**: Detecta si el rendimiento está mejorando o empeorando
- **Recomendaciones personalizadas**: Basadas en los patrones de estudio y hábitos del estudiante
- **Alertas académicas**: Notificaciones cuando se detecta riesgo de bajo rendimiento
