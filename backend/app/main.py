from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import engine, Base
from .models import models  # Importar models para que se registren
from .routers import auth, materias, registros, habitos, evaluaciones, analisis

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Predicción de Rendimiento Académico",
    description="API para analizar hábitos de estudio y predecir resultados académicos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(materias.router, prefix="/api")
app.include_router(registros.router, prefix="/api")
app.include_router(habitos.router, prefix="/api")
app.include_router(evaluaciones.router, prefix="/api")
app.include_router(analisis.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "API de Predicción Académica", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
