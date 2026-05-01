# medibook/api/auth/password.py
"""
Servicio de hashing de contraseñas.

Principio SRP (Single Responsibility):
  Esta clase tiene UNA sola responsabilidad: hashear y verificar contraseñas.
  No sabe nada de tokens, usuarios, ni base de datos.

Principio OCP (Open/Closed):
  Si se necesita cambiar el algoritmo de hashing (ej. de bcrypt a argon2),
  se puede crear una nueva clase que implemente la misma interfaz
  sin modificar el código existente.

Principio DIP (Dependency Inversion):
  Los módulos que necesiten hashing dependen de esta abstracción,
  no de una implementación concreta de passlib.
"""

from passlib.context import CryptContext


class PasswordHasher:
    """
    Encapsula el hashing y verificación de contraseñas con bcrypt.
    """

    def __init__(self) -> None:
        self._context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain_password: str) -> str:
        """Genera un hash bcrypt de la contraseña en texto plano."""
        return self._context.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña en texto plano coincide con el hash."""
        return self._context.verify(plain_password, hashed_password)


# Instancia global (Singleton por conveniencia)
password_hasher = PasswordHasher()
