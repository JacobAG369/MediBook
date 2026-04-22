# medibook/domain/appointment.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from medibook.infra.db import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)

    start_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=30)

    status = Column(String(30), nullable=False, default="SCHEDULED")
    notes = Column(String(255), nullable=True)

    # para teleconsulta (lo usaremos luego con Decorator)
    meeting_link = Column(String(255), nullable=True)

    # relaciones
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

    def __repr__(self) -> str:
        return (
            f"<Appointment(id={self.id}, patient_id={self.patient_id}, "
            f"doctor_id={self.doctor_id}, start_time={self.start_time})>"
        )
