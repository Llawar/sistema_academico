from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..models.models import Usuario, Evaluacion, Materia
from ..schemas.schemas import EvaluacionCreate, EvaluacionResponse
from ..routers.auth import get_current_user

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


@router.get("", response_model=List[EvaluacionResponse])
def get_evaluaciones(
    materia_id: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Evaluacion).filter(Evaluacion.usuario_id == current_user.id)
    if materia_id:
        query = query.filter(Evaluacion.materia_id == materia_id)
    return query.all()


@router.post("", response_model=EvaluacionResponse)
def create_evaluacion(
    evaluacion: EvaluacionCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    materia = db.query(Materia).filter(
        Materia.id == evaluacion.materia_id,
        Materia.usuario_id == current_user.id
    ).first()
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    db_evaluacion = Evaluacion(
        usuario_id=current_user.id,
        materia_id=evaluacion.materia_id,
        tipo=evaluacion.tipo,
        nota=evaluacion.nota,
        ponderacion=evaluacion.ponderacion
    )
    db.add(db_evaluacion)
    db.commit()
    db.refresh(db_evaluacion)
    return db_evaluacion


@router.delete("/{evaluacion_id}")
def delete_evaluacion(
    evaluacion_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_evaluacion = db.query(Evaluacion).filter(
        Evaluacion.id == evaluacion_id,
        Evaluacion.usuario_id == current_user.id
    ).first()
    if not db_evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    db.delete(db_evaluacion)
    db.commit()
    return {"message": "Evaluación eliminada"}


@router.put("/{evaluacion_id}", response_model=EvaluacionResponse)
def update_evaluacion(
    evaluacion_id: int,
    evaluacion: EvaluacionCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_evaluacion = db.query(Evaluacion).filter(
        Evaluacion.id == evaluacion_id,
        Evaluacion.usuario_id == current_user.id
    ).first()
    if not db_evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    db_evaluacion.materia_id = evaluacion.materia_id
    db_evaluacion.tipo = evaluacion.tipo
    db_evaluacion.nota = evaluacion.nota
    db_evaluacion.ponderacion = evaluacion.ponderacion
    db.commit()
    db.refresh(db_evaluacion)
    return db_evaluacion