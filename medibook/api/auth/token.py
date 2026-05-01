# medibook/api/auth/token.py
"""
Servicio de tokens JWT.

Principio SRP (Single Responsibility):
  Esta clase tiene UNA sola responsabilidad: crear y decodificar tokens JWT.
  No sabe nada de contraseñas, usuarios, ni base de datos.

Principio DIP (Dependency Inversion):
  Los módulos de nivel superior dependen de esta abstracción para tokens,
  no de la implementación concreta de python-jose.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# Configuración desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class TokenService:
    """
    Crea y decodifica tokens JWT.
    """

    def __init__(
        self,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM,
        expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Genera un JWT firmado con los datos proporcionados.

        Args:
            data: Payload del token (ej. {"sub": "username", "role": "ADMIN"}).
            expires_delta: Duración personalizada. Si es None, usa el valor por defecto.

        Returns:
            Token JWT como string.
        """
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self._expire_minutes)
        )
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decodifica y valida un JWT.

        Returns:
            Payload decodificado o None si el token es inválido/expirado.
        """
        try:
            payload = jwt.decode(
                token, self._secret_key, algorithms=[self._algorithm]
            )
            return payload
        except JWTError:
            return None


# Instancia global
token_service = TokenService()
