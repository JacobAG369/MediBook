# medibook/domain/user.py
"""
Modelo de dominio para los usuarios del sistema.

Cada usuario tiene un rol que determina sus permisos (RBAC).
Principio SRP: este modelo solo se encarga de la representación
del usuario en la base de datos.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from medibook.infra.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Rol para RBAC: ADMIN, DOCTOR, RECEPTIONIST, PATIENT
    role = Column(String(30), nullable=False, default="PATIENT")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
