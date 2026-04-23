# medibook/api/routes/patients.py
"""
Endpoints CRUD para la entidad Patient.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from medibook.api.dependencies import get_db
from medibook.api.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)
from medibook.domain.patient import Patient
from medibook.domain.user import User
from medibook.api.auth.dependencies import require_admin, require_receptionist

router = APIRouter(prefix="/patients", tags=["Pacientes"])


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar paciente",
)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_receptionist),
):
    """Crea un nuevo registro de paciente en el sistema."""
    patient = Patient(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        date_of_birth=payload.date_of_birth,
        notes=payload.notes,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/", response_model=List[PatientResponse], summary="Listar pacientes")
def list_patients(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Devuelve una lista paginada de pacientes."""
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Obtener paciente por ID",
)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Devuelve los datos de un paciente específico."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con id={patient_id} no encontrado",
        )
    return patient


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Actualizar paciente",
)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_receptionist),
):
    """Actualiza parcialmente los datos de un paciente."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con id={patient_id} no encontrado",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar paciente",
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
):
    """Elimina un paciente del sistema."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con id={patient_id} no encontrado",
        )

    db.delete(patient)
    db.commit()
