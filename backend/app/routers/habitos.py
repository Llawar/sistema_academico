from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..models.models import Usuario, DatoHabitual
from ..schemas.schemas import DatoHabitualCreate, DatoHabitualResponse
from ..routers.auth import get_current_user

router = APIRouter(prefix="/habitos", tags=["Hábitos"])


@router.get("", response_model=List[DatoHabitualResponse])
def get_habitos(
    tipo: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(DatoHabitual).filter(DatoHabitual.usuario_id == current_user.id)
    if tipo:
        query = query.filter(DatoHabitual.tipo == tipo)
    return query.all()


@router.post("", response_model=DatoHabitualResponse)
def create_habito(
    habito: DatoHabitualCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_habito = DatoHabitual(
        usuario_id=current_user.id,
        tipo=habito.tipo,
        duracion_minutos=habito.duracion_minutos,
        notas=habito.notas
    )
    db.add(db_habito)
    db.commit()
    db.refresh(db_habito)
    return db_habito


@router.delete("/{habito_id}")
def delete_habito(
    habito_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_habito = db.query(DatoHabitual).filter(
        DatoHabitual.id == habito_id,
        DatoHabitual.usuario_id == current_user.id
    ).first()
    if not db_habito:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    
    db.delete(db_habito)
    db.commit()
    return {"message": "Hábito eliminado"}
