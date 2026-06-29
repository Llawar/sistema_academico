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


@router.get("/predicciones")
def get_predicciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    materias = db.query(Materia).filter(Materia.usuario_id == current_user.id).all()
    registros = db.query(RegistroDiario).filter(RegistroDiario.usuario_id == current_user.id).all()
    habitos = db.query(DatoHabitual).filter(DatoHabitual.usuario_id == current_user.id).all()
    evaluaciones = db.query(Evaluacion).filter(Evaluacion.usuario_id == current_user.id).all()
    
    predicciones = predictor.obtener_predicciones_usuario(materias, evaluaciones, habitos, registros)
    
    return predicciones


@router.post("/entrenar-modelo-global")
def entrenar_modelo_global(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todas_evaluaciones = db.query(Evaluacion).all()
    todos_habitos = db.query(DatoHabitual).all()
    todos_registros = db.query(RegistroDiario).all()
    
    resultado = predictor.entrenar_modelo_global(todas_evaluaciones, todos_habitos, todos_registros)
    
    return resultado


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
    
    habitos = db.query(DatoHabitual).filter(DatoHabitual.usuario_id == current_user.id).all()
    
    from ..ml.predictor import PredictorAcademico
    predictor_temp = PredictorAcademico()
    df = predictor_temp.preparar_datos(registros, habitos, evaluaciones)
    
    prediccion = predictor_temp.predecir_nota(materia_id, df)
    prediccion['materia_nombre'] = materia.nombre
    
    return prediccion


@router.get("/recomendaciones")
def get_recomendaciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    materias = db.query(Materia).filter(Materia.usuario_id == current_user.id).all()
    registros = db.query(RegistroDiario).filter(RegistroDiario.usuario_id == current_user.id).all()
    habitos = db.query(DatoHabitual).filter(DatoHabitual.usuario_id == current_user.id).all()
    evaluaciones = db.query(Evaluacion).filter(Evaluacion.usuario_id == current_user.id).all()
    
    predicciones = predictor.obtener_predicciones_usuario(materias, evaluaciones, habitos, registros)
    
    recomendaciones = generador.generar_recomendaciones(materias, registros, habitos, evaluaciones, predicciones)
    
    return recomendaciones


@router.get("/estadisticas")
def get_estadisticas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    materias = db.query(Materia).filter(Materia.usuario_id == current_user.id).all()
    registros = db.query(RegistroDiario).filter(RegistroDiario.usuario_id == current_user.id).all()
    habitos = db.query(DatoHabitual).filter(DatoHabitual.usuario_id == current_user.id).all()
    evaluaciones = db.query(Evaluacion).filter(Evaluacion.usuario_id == current_user.id).all()
    
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
        "nota_promedio": sum(e.nota for e in evaluaciones) / len(evaluaciones) if evaluaciones else 0
    }
    
    return stats
