# medibook/domain/patient.py
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship

from medibook.infra.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(120), nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    notes = Column(String(255), nullable=True)

    # relación con citas
    appointments = relationship("Appointment", back_populates="patient")

    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, full_name='{self.full_name}')>"

