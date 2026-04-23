# medibook/api/auth/permissions.py
"""
Sistema de permisos basado en roles (RBAC).

Principio OCP (Open/Closed):
  Para agregar un nuevo rol, basta con añadir una entrada al Enum
  y al diccionario ROLE_HIERARCHY. No se modifica el código existente.

Principio ISP (Interface Segregation):
  Cada función de permiso es una dependencia independiente de FastAPI.
  Los endpoints solo dependen del nivel de permiso que necesitan.

Principio LSP (Liskov Substitution):
  Cualquier dependencia de permiso puede sustituir a una más permisiva
  sin romper el contrato (un ADMIN satisface require_doctor, etc.).
"""

from enum import IntEnum
from typing import List

from fastapi import HTTPException, status

from medibook.domain.user import User


class Role(IntEnum):
    """
    Roles del sistema ordenados por nivel de privilegio (ascendente).
    OCP: agregar un nuevo rol solo requiere una nueva entrada aquí.
    """
    PATIENT = 1
    RECEPTIONIST = 2
    DOCTOR = 3
    ADMIN = 4


# Mapeo de strings a niveles de rol
ROLE_MAP = {role.name: role for role in Role}


def check_permission(user: User, minimum_role: Role) -> None:
    """
    Verifica que el usuario tenga al menos el nivel de rol requerido.

    Raises:
        HTTPException 403 si el usuario no tiene permiso.
    """
    user_role = ROLE_MAP.get(user.role.upper())

    if user_role is None or user_role < minimum_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso denegado. Se requiere rol: {minimum_role.name}",
        )


def check_role_in(user: User, allowed_roles: List[str]) -> None:
    """
    Verifica que el usuario tenga uno de los roles permitidos.

    Raises:
        HTTPException 403 si el usuario no tiene uno de los roles.
    """
    if user.role.upper() not in [r.upper() for r in allowed_roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso denegado. Roles permitidos: {allowed_roles}",
        )
