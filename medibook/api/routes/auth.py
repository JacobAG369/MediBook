# medibook/api/routes/auth.py
"""
Endpoints de autenticación (registro e inicio de sesión).

Principio SRP:
  Esta ruta solo se encarga del flujo HTTP de autenticación.
  Delega el hashing a PasswordHasher y los tokens a TokenService.

Principio DIP:
  Depende de abstracciones (PasswordHasher, TokenService),
  no de implementaciones concretas de bcrypt o jose.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from medibook.api.dependencies import get_db
from medibook.api.auth.password import password_hasher
from medibook.api.auth.token import token_service
from medibook.api.auth.dependencies import get_current_user
from medibook.api.schemas.auth import (
    UserRegister,
    TokenResponse,
    UserResponse,
)
from medibook.domain.user import User
from medibook.config.logging_config import get_logger

logger = get_logger("api.auth")

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.

    La contraseña se almacena como hash bcrypt (nunca en texto plano).
    """
    # Verificar que el username no exista
    existing = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario o email ya está registrado",
        )

    # Crear usuario con contraseña hasheada (SRP → PasswordHasher)
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=password_hasher.hash(payload.password),
        role=payload.role.upper(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("Usuario registrado: %s (rol=%s)", user.username, user.role)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Autentica un usuario y devuelve un token JWT.

    Compatible con OAuth2PasswordRequestForm para que Swagger UI
    muestre el botón 'Authorize' con formulario de login.
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not password_hasher.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada",
        )

    # Generar token JWT (SRP → TokenService)
    access_token = token_service.create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    logger.info("Login exitoso: %s", user.username)
    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Devuelve la información del usuario autenticado.
    Requiere un token JWT válido en el header Authorization.
    """
    return current_user
