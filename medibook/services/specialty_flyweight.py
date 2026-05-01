# medibook/services/specialty_flyweight.py

from typing import Dict, Optional

from medibook.infra.db import SessionLocal
from medibook.domain.specialty import Specialty


class SpecialtyFlyweightFactory:
    """
    Implementación del patrón Flyweight para Specialty.

    Mantiene un caché en memoria de objetos Specialty por nombre.
    Si se solicita una especialidad que ya existe, devuelve la misma
    instancia en lugar de crear una nueva.
    """

    _cache: Dict[str, Specialty] = {}

    @classmethod
    def get_specialty(cls, name: str, description: Optional[str] = None,) -> Specialty:
        """
        Obtiene una Specialty compartida (flyweight) por nombre.

       aqui, si ya está en la bd ya no la crea y devuelve la misma instancia
        """
        key = name.strip().lower()

        # 1) ¿Ya está en el caché?
        if key in cls._cache:
            return cls._cache[key]

        # 2) No está en el caché -> ir a la BD
        session = SessionLocal()
        try:
            specialty = (
                session.query(Specialty)
                .filter(Specialty.name.ilike(name))
                .first()
            )

            # 3) Si tampoco está en la BD, la creamos
            if not specialty:
                specialty = Specialty(name=name, description=description)
                session.add(specialty)
                session.commit()
                session.refresh(specialty)

            # 4) Guardar en caché y regresar
            cls._cache[key] = specialty
            return specialty

        finally:
            session.close()
