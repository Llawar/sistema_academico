from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..models.models import Usuario, RegistroDiario, Materia
from ..schemas.schemas import RegistroDiarioCreate, RegistroDiarioResponse
from ..routers.auth import get_current_user

router = APIRouter(prefix="/registros", tags=["Registros de Estudio"])


@router.get("", response_model=List[RegistroDiarioResponse])
def get_registros(
    materia_id: int = None,
    fecha_inicio: datetime = None,
    fecha_fin: datetime = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(RegistroDiario).filter(RegistroDiario.usuario_id == current_user.id)
    
    if materia_id:
        query = query.filter(RegistroDiario.materia_id == materia_id)
    if fecha_inicio:
        query = query.filter(RegistroDiario.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(RegistroDiario.fecha <= fecha_fin)
    
    return query.all()


@router.post("", response_model=RegistroDiarioResponse)
def create_registro(
    registro: RegistroDiarioCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if registro.materia_id:
        materia = db.query(Materia).filter(
            Materia.id == registro.materia_id,
            Materia.usuario_id == current_user.id
        ).first()
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    db_registro = RegistroDiario(
        usuario_id=current_user.id,
        materia_id=registro.materia_id,
        hora_inicio=registro.hora_inicio,
        hora_fin=registro.hora_fin,
        tipo_actividad=registro.tipo_actividad,
        descripcion=registro.descripcion
    )
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)
    return db_registro


@router.put("/{registro_id}", response_model=RegistroDiarioResponse)
def update_registro(
    registro_id: int,
    registro: RegistroDiarioCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_registro = db.query(RegistroDiario).filter(
        RegistroDiario.id == registro_id,
        RegistroDiario.usuario_id == current_user.id
    ).first()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    db_registro.materia_id = registro.materia_id
    db_registro.hora_inicio = registro.hora_inicio
    db_registro.hora_fin = registro.hora_fin
    db_registro.tipo_actividad = registro.tipo_actividad
    db_registro.descripcion = registro.descripcion
    db.commit()
    db.refresh(db_registro)
    return db_registro


@router.delete("/{registro_id}")
def delete_registro(
    registro_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_registro = db.query(RegistroDiario).filter(
        RegistroDiario.id == registro_id,
        RegistroDiario.usuario_id == current_user.id
    ).first()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    db.delete(db_registro)
    db.commit()
    return {"message": "Registro eliminado"}
