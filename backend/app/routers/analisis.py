from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.models import Usuario, Materia, RegistroDiario, DatoHabitual, Evaluacion
from ..schemas.schemas import PrediccionResponse, RecomendacionResponse
from ..routers.auth import get_current_user
from ..ml.predictor import predictor
from ..services.recomendaciones import generador

router = APIRouter(prefix="/analisis", tags=["Análisis y Predicciones"])

# Función auxiliar que obtiene todos los datos académicos de un usuario
def _obtener_datos_usuario(db: Session, user_id: int):
    return {
        "materias": db.query(Materia).filter(Materia.usuario_id == user_id).all(),
        "registros": db.query(RegistroDiario).filter(RegistroDiario.usuario_id == user_id).all(),
        "habitos": db.query(DatoHabitual).filter(DatoHabitual.usuario_id == user_id).all(),
        "evaluaciones": db.query(Evaluacion).filter(Evaluacion.usuario_id == user_id).all(),
    }


# Obtiene predicciones generales del rendimiento
@router.get("/predicciones")
def get_predicciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    datos = _obtener_datos_usuario(db, current_user.id)

    predicciones = predictor.obtener_predicciones_usuario(
        datos["materias"], datos["evaluaciones"], datos["habitos"], datos["registros"]
    )

    return predicciones

# Entrena modelo ML con todos los datos
@router.post("/entrenar-modelo-global")
def entrenar_modelo_global(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: En producción, restringir a admin o agregar rate limiting
    todas_evaluaciones = db.query(Evaluacion).all()
    todos_habitos = db.query(DatoHabitual).all()
    todos_registros = db.query(RegistroDiario).all()
    
    resultado = predictor.entrenar_modelo_global(todas_evaluaciones, todos_habitos, todos_registros)
    
    return resultado

# Obtiene predicción para una materia específica
@router.get("/predicciones/{materia_id}")
def get_prediccion_materia(
    materia_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    materia = db.query(Materia).filter(
        Materia.id == materia_id,
        Materia.usuario_id == current_user.id
    ).first()

    if not materia:
        return {"error": "Materia no encontrada"}

    evaluaciones = db.query(Evaluacion).filter(
        Evaluacion.usuario_id == current_user.id,
        Evaluacion.materia_id == materia_id
    ).all()

    registros = db.query(RegistroDiario).filter(
        RegistroDiario.usuario_id == current_user.id,
        RegistroDiario.materia_id == materia_id
    ).all()

    habitos = db.query(DatoHabitual).filter(
        DatoHabitual.usuario_id == current_user.id
    ).all()

    # Usar el singleton en vez de crear una nueva instancia
    df = predictor.preparar_datos(registros, habitos, evaluaciones)
    prediccion = predictor.predecir_nota(materia_id, df)
    prediccion['materia_nombre'] = materia.nombre

    return prediccion


# Genera recomendaciones personalizadas
@router.get("/recomendaciones")
def get_recomendaciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    datos = _obtener_datos_usuario(db, current_user.id)

    predicciones = predictor.obtener_predicciones_usuario(
        datos["materias"], datos["evaluaciones"], datos["habitos"], datos["registros"]
    )

    recomendaciones = generador.generar_recomendaciones(
        datos["materias"], datos["registros"], datos["habitos"],
        datos["evaluaciones"], predicciones
    )

    return recomendaciones

# Obtiene estadísticas detalladas del usuario
@router.get("/estadisticas")
def get_estadisticas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    datos = _obtener_datos_usuario(db, current_user.id)
    materias = datos["materias"]
    registros = datos["registros"]
    habitos = datos["habitos"]
    evaluaciones = datos["evaluaciones"]

    stats = {
        "total_materias": len(materias),
        "total_registros": len(registros),
        "total_habitos": len(habitos),
        "total_evaluaciones": len(evaluaciones),
        "tiempo_estudio_total": sum(
            (r.hora_fin - r.hora_inicio).total_seconds() / 3600
            for r in registros if r.hora_inicio and r.hora_fin
        ),
        "tiempo_distracciones": sum(
            h.duracion_minutos for h in habitos if h.tipo == "distraccion"
        ),
        "nota_promedio": (
            sum(e.nota for e in evaluaciones) / len(evaluaciones)
            if evaluaciones else 0
        ),
    }

    return stats

# ─── Endpoint de chat con IA ───

# Endpoint que recibe texto libre del estudiante y extrae datos con IA
@router.post("/chat")
def chat_registro(
    request: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from ..services.ai_service import procesar_registro_usuario

    texto = request.get("mensaje", "").strip()
    if not texto:
        return {"error": "El mensaje no puede estar vacío"}

    materias = db.query(Materia).filter(
        Materia.usuario_id == current_user.id
    ).all()

    resultado = procesar_registro_usuario(
        db=db,
        usuario_id=current_user.id,
        texto=texto,
        materias=materias,
    )

    return resultado
