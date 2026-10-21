#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Appointments,
    Professional,
    ProfessionalWorkingHour,
    Service,
    User,
)
from app.core.auth import require_role
from app.schemas import (
    ProfessionalCreate,
    ProfessionalUpdate,
    ProfessionalResponse,
    MessageResponse,
)


router = APIRouter(
    prefix="/professionals",
    tags=["professionals"],
)


@router.get("/", response_model=list[ProfessionalResponse])
def list_professionals(db: Session = Depends(get_db)):
    professionals = db.query(Professional).all()
    return professionals


@router.get("/{professional_id}/available-slots/")
def get_available_slots(
    professional_id: int,
    appointment_date: date = Query(...),
    service_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    professional = (
        db.query(Professional)
        .filter(
            Professional.id == professional_id,
            Professional.available.is_(True),
        )
        .first()
    )

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado ou indisponível.",
        )

    service = (
        db.query(Service)
        .filter(
            Service.id == service_id,
            Service.available.is_(True),
        )
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado ou indisponível.",
        )

    weekday = appointment_date.weekday()

    working_hours = (
        db.query(ProfessionalWorkingHour)
        .filter(
            ProfessionalWorkingHour.professional_id == professional_id,
            ProfessionalWorkingHour.weekday == weekday,
        )
        .order_by(ProfessionalWorkingHour.start_time)
        .all()
    )

    if not working_hours:
        return []

    existing_appointments = (
        db.query(Appointments)
        .filter(
            Appointments.professional_id == professional_id,
            Appointments.appointment_date == appointment_date,
            Appointments.status != "cancelled",
        )
        .all()
    )

    # Carrega a duração dos serviços já agendados.
    service_ids = {
        appointment.service_id
        for appointment in existing_appointments
    }

    existing_services = (
        db.query(Service)
        .filter(Service.id.in_(service_ids))
        .all()
        if service_ids
        else []
    )

    service_durations = {
        existing_service.id: existing_service.duration_minutes
        for existing_service in existing_services
    }

    now = datetime.now()
    slot_interval = timedelta(minutes=30)
    service_duration = timedelta(minutes=service.duration_minutes)
    slots = []

    for working_hour in working_hours:
        slot_start = datetime.combine(
            appointment_date,
            working_hour.start_time,
        )
        working_end = datetime.combine(
            appointment_date,
            working_hour.end_time,
        )

        while slot_start + service_duration <= working_end:
            slot_end = slot_start + service_duration

            if slot_start <= now:
                slot_start += slot_interval
                continue

            has_conflict = False

            for appointment in existing_appointments:
                existing_duration = service_durations.get(
                    appointment.service_id
                )

                if existing_duration is None:
                    continue

                existing_start = datetime.combine(
                    appointment.appointment_date,
                    appointment.appointment_time,
                )
                existing_end = existing_start + timedelta(
                    minutes=existing_duration
                )

                if (
                    slot_start < existing_end
                    and slot_end > existing_start
                ):
                    has_conflict = True
                    break

            if not has_conflict:
                slots.append(slot_start.strftime("%H:%M"))

            slot_start += slot_interval

    return slots


@router.post("/", response_model=ProfessionalResponse)
def create_professional(
    professional_data: ProfessionalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    professional = Professional(
        name=professional_data.name,
        email=professional_data.email,
        phone=professional_data.phone,
    )

    db.add(professional)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="E-mail já cadastrado",
        )

    db.refresh(professional)
    return professional


@router.get("/{professional_id}", response_model=ProfessionalResponse)
def get_professional(
    professional_id: int,
    db: Session = Depends(get_db),
):
    professional = (
        db.query(Professional)
        .filter(Professional.id == professional_id)
        .first()
    )

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado",
        )

    return professional


@router.put(
    "/{professional_id}",
    response_model=ProfessionalResponse,
)
def update_professional(
    professional_id: int,
    professional_data: ProfessionalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    professional = (
        db.query(Professional)
        .filter(Professional.id == professional_id)
        .first()
    )

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado",
        )

    professional.name = professional_data.name
    professional.email = professional_data.email
    professional.phone = professional_data.phone
    professional.available = professional_data.available

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="E-mail já cadastrado",
        )

    db.refresh(professional)
    return professional


@router.delete(
    "/{professional_id}",
    response_model=MessageResponse,
)
def delete_professional(
    professional_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    professional = (
        db.query(Professional)
        .filter(Professional.id == professional_id)
        .first()
    )

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado",
        )

    try:
        db.delete(professional)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Não é possível excluir o profissional porque "
                "existem registros vinculados."
            ),
        )

    return {
        "message": "Profissional excluído com sucesso."
    }
