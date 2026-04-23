# medibook/api/routes/doctors.py
"""
Endpoints CRUD para la entidad Doctor.

La creación de doctores utiliza el patrón Flyweight para las especialidades
a través del BookingService.create_doctor_with_specialty().
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from medibook.api.dependencies import get_db
from medibook.api.schemas.doctor import (
    DoctorCreate,
    DoctorResponse,
    DoctorUpdate,
)
from medibook.domain.doctor import Doctor
from medibook.domain.user import User
from medibook.api.auth.dependencies import require_admin, require_receptionist

router = APIRouter(prefix="/doctors", tags=["Doctores"])


@router.post(
    "/",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar doctor",
)
def create_doctor(
    payload: DoctorCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
):
    """
    Crea un nuevo doctor asociado a una especialidad.

    Internamente usa el patrón **Flyweight** para reutilizar
    instancias de Specialty existentes en lugar de crear duplicados.
    """
    from medibook.domain.specialty import Specialty

    try:
        # Flyweight inline: buscar o crear la especialidad
        specialty = (
            db.query(Specialty)
            .filter(Specialty.name.ilike(payload.specialty_name))
            .first()
        )
        if not specialty:
            specialty = Specialty(
                name=payload.specialty_name,
                description=payload.specialty_description,
            )
            db.add(specialty)
            db.flush()

        doctor = Doctor(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            specialty_id=specialty.id,
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        return doctor
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[DoctorResponse], summary="Listar doctores")
def list_doctors(
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """Devuelve una lista paginada de doctores. Por defecto solo los activos."""
    query = db.query(Doctor)
    if active_only:
        query = query.filter(Doctor.active == True)
    doctors = query.offset(skip).limit(limit).all()
    return doctors


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Obtener doctor por ID",
)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Devuelve los datos de un doctor específico, incluyendo su especialidad."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor con id={doctor_id} no encontrado",
        )
    return doctor


@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Actualizar doctor",
)
def update_doctor(
    doctor_id: int,
    payload: DoctorUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_receptionist),
):
    """Actualiza parcialmente los datos de un doctor."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor con id={doctor_id} no encontrado",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar doctor",
)
def deactivate_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
):
    """
    Desactiva un doctor (soft delete).
    No se elimina físicamente para preservar el historial de citas.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor con id={doctor_id} no encontrado",
        )

    doctor.active = False
    db.commit()
