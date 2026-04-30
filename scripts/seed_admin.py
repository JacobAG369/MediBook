# medibook/scripts/seed_admin.py
"""
Script de inicialización: crea el primer usuario administrador en la BD.

Uso:
    python -m medibook.scripts.seed_admin

    o con credenciales personalizadas:
    python -m medibook.scripts.seed_admin --username admin --password miClave123
"""

import argparse
import sys

from sqlalchemy.orm import Session

from medibook.infra.db import engine, Base
from medibook.domain.user import User
from medibook.api.auth.password import password_hasher
from medibook.config.logging_config import get_logger

logger = get_logger("scripts.seed_admin")


def crear_admin(username: str, email: str, password: str) -> None:
    # Asegurar que las tablas existen
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        existente = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existente:
            print(f"[AVISO] El usuario '{existente.username}' ya existe en la base de datos.")
            print(f"        Email: {existente.email} | Rol: {existente.role}")
            return

        usuario = User(
            username=username,
            email=email,
            hashed_password=password_hasher.hash(password),
            role="ADMIN",
            is_active=True,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        print("=" * 50)
        print("  Usuario administrador creado exitosamente")
        print("=" * 50)
        print(f"  Usuario   : {usuario.username}")
        print(f"  Email     : {usuario.email}")
        print(f"  Rol       : {usuario.role}")
        print(f"  Contraseña: {password}")
        print("=" * 50)
        print("  Accede en: http://localhost:8000/web/login")
        print("=" * 50)

        logger.info("Admin creado: %s (id=%s)", usuario.username, usuario.id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Crea el primer usuario administrador de MediBook.")
    parser.add_argument("--username", default="admin",       help="Nombre de usuario (default: admin)")
    parser.add_argument("--email",    default="admin@medibook.app", help="Email del admin")
    parser.add_argument("--password", default="Admin123!",   help="Contraseña (default: Admin123!)")
    args = parser.parse_args()

    try:
        crear_admin(args.username, args.email, args.password)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
