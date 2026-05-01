# tests/unit/test_specialty_flyweight.py
"""
Tests unitarios para el patrón Flyweight.
Verifica el caché y reutilización de especialidades.
"""

from medibook.domain.specialty import Specialty
from medibook.services.specialty_flyweight import SpecialtyFlyweightFactory


class TestSpecialtyFlyweightFactory:
    """Pruebas para SpecialtyFlyweightFactory."""

    def setup_method(self):
        """Limpia el caché antes de cada test."""
        SpecialtyFlyweightFactory._cache.clear()

    def test_cache_stores_specialty(self, db_session):
        """La Flyweight debe almacenar la especialidad en caché."""
        specialty = SpecialtyFlyweightFactory.get_specialty(
            name="Neurología", description="Sistema nervioso"
        )

        assert isinstance(specialty, Specialty)
        assert specialty.name == "Neurología"
        assert "neurología" in SpecialtyFlyweightFactory._cache

    def test_cache_returns_same_instance(self, db_session):
        """Solicitar la misma especialidad dos veces debe retornar la misma instancia."""
        first = SpecialtyFlyweightFactory.get_specialty(name="Dermatología")
        second = SpecialtyFlyweightFactory.get_specialty(name="Dermatología")

        assert first is second

    def test_cache_is_case_insensitive(self, db_session):
        """La key del caché debe ser case-insensitive."""
        first = SpecialtyFlyweightFactory.get_specialty(name="Pediatría")
        second = SpecialtyFlyweightFactory.get_specialty(name="PEDIATRÍA")

        assert first is second

    def test_different_specialties_are_different(self, db_session):
        """Especialidades diferentes deben ser instancias distintas."""
        cardio = SpecialtyFlyweightFactory.get_specialty(name="Cardiología Test")
        neuro = SpecialtyFlyweightFactory.get_specialty(name="Neurología Test")

        assert cardio is not neuro
        assert cardio.name != neuro.name
