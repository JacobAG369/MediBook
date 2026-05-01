# medibook/config/logging_config.py
"""
Configuración de logging estructurado para MediBook.

Reemplaza los print() por un sistema de logging profesional
con formato JSON para producción y formato legible para desarrollo.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Configura el logging global de la aplicación.

    Args:
        level: Nivel mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Formato para desarrollo (legible en consola)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Configurar el logger raíz de la aplicación
    app_logger = logging.getLogger("medibook")
    app_logger.setLevel(log_level)
    app_logger.addHandler(console_handler)

    # Evitar propagación al logger raíz de Python
    app_logger.propagate = False

    # Reducir el ruido de SQLAlchemy en desarrollo
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    app_logger.info("Sistema de logging inicializado (nivel=%s)", level)


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger hijo del logger principal de MediBook.

    Args:
        name: Nombre del módulo (ej. 'services.booking').

    Returns:
        Logger configurado.
    """
    return logging.getLogger(f"medibook.{name}")
