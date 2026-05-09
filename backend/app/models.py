from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from .database import Base


class DistritoDelito(Base):
    __tablename__ = "distritos_delitos"

    id = Column(Integer, primary_key=True, index=True)
    distrito = Column(String, index=True, nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    homicidio_2024 = Column(Integer, default=0)
    hurto_2024 = Column(Integer, default=0)
    robo_2024 = Column(Integer, default=0)
    extorsion_2024 = Column(Integer, default=0)
    estafa_2024 = Column(Integer, default=0)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(255), nullable=False)
    rol = Column(String(40), default="analista", index=True, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    ultimo_login_en = Column(DateTime, nullable=True)


class RegistroPendiente(Base):
    __tablename__ = "registros_pendientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(255), nullable=False)
    codigo_hash = Column(String(255), nullable=False)
    codigo_salt = Column(String(255), nullable=False)
    intentos = Column(Integer, default=0, nullable=False)
    consumido = Column(Boolean, default=False, nullable=False)
    expira_en = Column(DateTime, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=True, index=True)
    accion = Column(String(80), nullable=False, index=True)
    resultado = Column(String(40), nullable=False)
    ip = Column(String(80), nullable=True)
    detalle = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
