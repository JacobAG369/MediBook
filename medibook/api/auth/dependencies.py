# medibook/api/auth/dependencies.py
"""
Dependencias de autenticación para inyección en FastAPI.

Principio ISP (Interface Segregation):
  Se proveen dependencias separadas según el nivel de acceso requerido:
    - get_current_user: cualquier usuario autenticado
    - require_admin: solo administradores
    - require_doctor: doctores o superiores
    - require_receptionist: recepcionistas o superiores

  Cada endpoint depende SOLO de la interfaz que necesita.

Principio DIP (Dependency Inversion):
  Las dependencias usan TokenService y no implementan lógica de JWT
  directamente. Si cambia el proveedor de tokens, solo se modifica
  token.py, no las dependencias.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from medibook.api.dependencies import get_db
from medibook.api.auth.token import token_service
from medibook.api.auth.permissions import Role, check_permission
from medibook.domain.user import User

# Esquema OAuth2 — FastAPI genera el form de login en /docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependencia base: extrae y valida el usuario del token JWT.

    Raises:
        HTTPException 401 si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = token_service.decode_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia: requiere rol ADMIN."""
    check_permission(current_user, Role.ADMIN)
    return current_user


def require_doctor(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia: requiere rol DOCTOR o superior."""
    check_permission(current_user, Role.DOCTOR)
    return current_user


def require_receptionist(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia: requiere rol RECEPTIONIST o superior."""
    check_permission(current_user, Role.RECEPTIONIST)
    return current_user
