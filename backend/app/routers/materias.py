from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.models import Usuario, Materia
from ..schemas.schemas import MateriaCreate, MateriaResponse
from ..routers.auth import get_current_user

router = APIRouter(prefix="/materias", tags=["Materias"])


@router.get("", response_model=List[MateriaResponse])
def get_materias(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Materia).filter(Materia.usuario_id == current_user.id).all()


@router.get("/{materia_id}", response_model=MateriaResponse)
def get_materia_by_id(
    materia_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_materia = db.query(Materia).filter(
        Materia.id == materia_id,
        Materia.usuario_id == current_user.id
    ).first()
    if not db_materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return db_materia


@router.post("", response_model=MateriaResponse)
def create_materia(
    materia: MateriaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_materia = Materia(
        usuario_id=current_user.id,
        nombre=materia.nombre,
        objetivo_nota=materia.objetivo_nota
    )
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia


@router.put("/{materia_id}", response_model=MateriaResponse)
def update_materia(
    materia_id: int,
    materia: MateriaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_materia = db.query(Materia).filter(
        Materia.id == materia_id,
        Materia.usuario_id == current_user.id
    ).first()
    if not db_materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    db_materia.nombre = materia.nombre
    db_materia.objetivo_nota = materia.objetivo_nota
    db.commit()
    db.refresh(db_materia)
    return db_materia


@router.delete("/{materia_id}")
def delete_materia(
    materia_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_materia = db.query(Materia).filter(
        Materia.id == materia_id,
        Materia.usuario_id == current_user.id
    ).first()
    if not db_materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    db.delete(db_materia)
    db.commit()
    return {"message": "Materia eliminada"}
