from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    objetivo_promedio = Column(Float, default=7.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    materias = relationship("Materia", back_populates="usuario", cascade="all, delete-orphan")
    registros = relationship("RegistroDiario", back_populates="usuario", cascade="all, delete-orphan")
    datos_habitos = relationship("DatoHabitual", back_populates="usuario", cascade="all, delete-orphan")
    evaluaciones = relationship("Evaluacion", back_populates="usuario", cascade="all, delete-orphan")


class Materia(Base):
    __tablename__ = "materias"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre = Column(String(255), nullable=False)
    objetivo_nota = Column(Float, default=7.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("Usuario", back_populates="materias")
    registros = relationship("RegistroDiario", back_populates="materia")
    evaluaciones = relationship("Evaluacion", back_populates="materia")


class RegistroDiario(Base):
    __tablename__ = "registros_diarios"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    hora_inicio = Column(DateTime, nullable=False)
    hora_fin = Column(DateTime, nullable=False)
    tipo_actividad = Column(String(50), default="estudio")  # estudio, practica, repaso
    descripcion = Column(Text, nullable=True)
    
    usuario = relationship("Usuario", back_populates="registros")
    materia = relationship("Materia", back_populates="registros")


class DatoHabitual(Base):
    __tablename__ = "datos_habitos"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String(50), nullable=False)  # descanso, distraccion, ejercicio, sueno
    duracion_minutos = Column(Integer, nullable=False)
    notas = Column(Text, nullable=True)
    
    usuario = relationship("Usuario", back_populates="datos_habitos")


class Evaluacion(Base):
    __tablename__ = "evaluaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)
    tipo = Column(String(50), nullable=False)  # examen, tarea, proyecto, quiz
    nota = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    ponderacion = Column(Float, default=1.0)
    
    usuario = relationship("Usuario", back_populates="evaluaciones")
    materia = relationship("Materia", back_populates="evaluaciones")
