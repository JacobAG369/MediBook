# medibook/domain/doctor.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from medibook.infra.db import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=True)
    phone = Column(String(20), nullable=True)

    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)
    active = Column(Boolean, default=True)

    # relación con Specialty
    specialty = relationship("Specialty", backref="doctors")

    # relación con citas (Appointment)
    appointments = relationship("Appointment", back_populates="doctor")

    def __repr__(self) -> str:
        return f"<Doctor(id={self.id}, name='{self.name}')>"
