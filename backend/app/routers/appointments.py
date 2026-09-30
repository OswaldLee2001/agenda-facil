#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointments, Professional, Service
from app.schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    MessageResponse,
)

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)


@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(
    db: Session = Depends(get_db),
):
    appointments = db.query(Appointments).all()
    return appointments


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
):
    professional = db.query(Professional).filter(
        Professional.id == appointment_data.professional_id
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado.",
        )

    existing_appointment = db.query(Appointments).filter(
        Appointments.professional_id == appointment_data.professional_id,
        Appointments.appointment_date == appointment_data.appointment_date.isoformat(),
        Appointments.appointment_time == appointment_data.appointment_time.strftime("%H:%M"),
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=409,
            detail="O profissional já possui um agendamento nesse horário.",
        )

    service = db.query(Service).filter(
        Service.id == appointment_data.service_id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado.",
        )

    appointment = Appointments(
        professional_id=appointment_data.professional_id,
        service_id=appointment_data.service_id,
        client_name=appointment_data.client_name,
        client_phone=appointment_data.client_phone,
        appointment_date=appointment_data.appointment_date.isoformat(),
        appointment_time=appointment_data.appointment_time.strftime("%H:%M"),
    )

    db.add(appointment)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao salvar o agendamento.",
        )

    db.refresh(appointment)

    return appointment


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = db.query(Appointments).filter(
        Appointments.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado",
        )

    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    appointment = db.query(Appointments).filter(
        Appointments.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado."
        )

    professional = db.query(Professional).filter(
        Professional.id == appointment_data.professional_id
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado.",
        )

    service = db.query(Service).filter(
        Service.id == appointment_data.service_id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado.",
        )

    existing_appointment = db.query(Appointments).filter(
        Appointments.professional_id == appointment_data.professional_id,
        Appointments.appointment_date == appointment_data.appointment_date.isoformat(),
        Appointments.appointment_time == appointment_data.appointment_time.strftime("%H:%M"),
        Appointments.id != appointment_id,
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=409,
            detail="O profissional já possui um agendamento nesse horário.",
        )

    appointment.professional_id = appointment_data.professional_id
    appointment.service_id = appointment_data.service_id
    appointment.client_name = appointment_data.client_name
    appointment.client_phone = appointment_data.client_phone
    appointment.appointment_date = appointment_data.appointment_date.isoformat()
    appointment.appointment_time = appointment_data.appointment_time.strftime("%H:%M")
    appointment.status = appointment_data.status

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar o agendamento.",
        )

    db.refresh(appointment)

    return appointment


@router.delete("/{appointment_id}", response_model=MessageResponse)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = db.query(Appointments).filter(
        Appointments.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado."
        )

    db.delete(appointment)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao excluir o agendamento.",
        )

    return {
        "message": "Agendamento excluído com sucesso."
    }

