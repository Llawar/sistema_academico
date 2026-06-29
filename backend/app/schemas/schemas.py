from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    carrera: Optional[str] = None
    semestre: int = 1
    objetivo_promedio: float = 7.0


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    carrera: Optional[str] = None
    semestre: Optional[int] = None
    objetivo_promedio: Optional[float] = None


class MateriaBase(BaseModel):
    nombre: str
    objetivo_nota: float = 7.0


class MateriaCreate(MateriaBase):
    pass


class MateriaResponse(MateriaBase):
    id: int
    usuario_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RegistroDiarioBase(BaseModel):
    materia_id: Optional[int] = None
    hora_inicio: datetime
    hora_fin: datetime
    tipo_actividad: str = "estudio"
    descripcion: Optional[str] = None


class RegistroDiarioCreate(RegistroDiarioBase):
    pass


class RegistroDiarioResponse(RegistroDiarioBase):
    id: int
    usuario_id: int
    fecha: datetime

    class Config:
        from_attributes = True


class DatoHabitualBase(BaseModel):
    tipo: str
    duracion_minutos: int
    notas: Optional[str] = None


class DatoHabitualCreate(DatoHabitualBase):
    pass


class DatoHabitualResponse(DatoHabitualBase):
    id: int
    usuario_id: int
    fecha: datetime

    class Config:
        from_attributes = True


class EvaluacionBase(BaseModel):
    materia_id: int
    tipo: str
    nota: float
    ponderacion: float = 1.0


class EvaluacionCreate(EvaluacionBase):
    pass


class EvaluacionResponse(EvaluacionBase):
    id: int
    usuario_id: int
    fecha: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class PrediccionResponse(BaseModel):
    materia_id: int
    materia_nombre: str
    prediccion_nota: float
    confianza: float
    tendencia: str
    factores: List[str]


class RecomendacionResponse(BaseModel):
    tipo: str
    titulo: str
    descripcion: str
    prioridad: str
    materia_id: Optional[int] = None
