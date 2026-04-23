# medibook/scripts/init_db.py
from medibook.config.logging_config import get_logger, setup_logging
from medibook.infra.db import Base, engine, SessionLocal

# Importamos explícitamente los modelos para que se registren en Base.metadata
from medibook.domain.specialty import Specialty
from medibook.domain.doctor import Doctor
from medibook.domain.patient import Patient
from medibook.domain.appointment import Appointment


logger = get_logger("scripts.init_db")


def create_tables():
    logger.info("Creando tablas en la base de datos (si no existen)...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas listas.")


def seed_minimo():
    """
    Inserta algunos datos básicos para probar rápido.
    """
    session = SessionLocal()
    try:
        # Especialidades mínimas
        base_specialties = ["General Medicine", "Cardiology", "Pediatrics"]
        existentes = {s.name for s in session.query(Specialty).all()}
        for name in base_specialties:
            if name not in existentes:
                session.add(Specialty(name=name))

        session.commit()
        logger.info("Datos mínimos insertados (specialties).")
    except Exception as e:
        session.rollback()
        logger.error("Error en seed_minimo: %s", e)
    finally:
        session.close()


if __name__ == "__main__":
    setup_logging()
    create_tables()
    seed_minimo()
    logger.info("init_db completado.")
