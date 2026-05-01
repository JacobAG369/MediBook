# medibook/api/schemas/auth.py
"""
Schemas Pydantic para autenticación y gestión de usuarios.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Request Schemas ----------

class UserRegister(BaseModel):
    """Datos para registrar un nuevo usuario."""
    username: str = Field(
        ..., min_length=3, max_length=80, examples=["dr.mendoza"]
    )
    email: EmailStr = Field(..., examples=["carlos@medibook.com"])
    password: str = Field(
        ..., min_length=8, max_length=128,
        description="Mínimo 8 caracteres.",
        examples=["SecureP@ss123"],
    )
    role: str = Field(
        default="PATIENT",
        pattern=r"^(ADMIN|DOCTOR|RECEPTIONIST|PATIENT)$",
        description="Rol del usuario en el sistema.",
        examples=["DOCTOR"],
    )


class UserLogin(BaseModel):
    """Datos para iniciar sesión."""
    username: str = Field(..., examples=["dr.mendoza"])
    password: str = Field(..., examples=["SecureP@ss123"])


# ---------- Response Schemas ----------

class TokenResponse(BaseModel):
    """Respuesta con el token JWT."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Representación pública del usuario (sin contraseña)."""
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
