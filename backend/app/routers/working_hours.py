#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Professional, ProfessionalWorkingHour
from app.schemas import (
    ProfessionalWorkingHourCreate,
    ProfessionalWorkingHourResponse,
)

router = APIRouter(
    prefix="/professionals/{professional_id}/working-hours",
    tags=["working-hours"],
)


@router.get("/", response_model=list[ProfessionalWorkingHourResponse])
def list_working_hours(
    professional_id: int,
    db: Session = Depends(get_db),
):
    professional = db.query(Professional).filter(
        Professional.id == professional_id
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado.",
        )

    working_hours = db.query(ProfessionalWorkingHour).filter(
        ProfessionalWorkingHour.professional_id == professional_id
    ).order_by(
        ProfessionalWorkingHour.weekday,
        ProfessionalWorkingHour.start_time,
    ).all()

    return working_hours


@router.post("/", response_model=ProfessionalWorkingHourResponse)
def create_working_hour(
    professional_id: int,
    working_hour_data: ProfessionalWorkingHourCreate,
    db: Session = Depends(get_db),
):
    professional = db.query(Professional).filter(
        Professional.id == professional_id
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado.",
        )

    if working_hour_data.start_time >= working_hour_data.end_time:
        raise HTTPException(
            status_code=409,
            detail="O horário inicial deve ser anterior ao horário final.",
        )

    existing_working_hours = db.query(
        ProfessionalWorkingHour
    ).filter(
        ProfessionalWorkingHour.professional_id == professional_id,
        ProfessionalWorkingHour.weekday == working_hour_data.weekday,
    ).all()

    for existing in existing_working_hours:
        existing_start = datetime.strptime(
            existing.start_time,
            "%H:%M",
        ).time()

        existing_end = datetime.strptime(
            existing.end_time,
            "%H:%M",
        ).time()

        if (
            working_hour_data.start_time < existing_end
            and working_hour_data.end_time > existing_start
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "O novo horário se sobrepõe a um horário "
                    "já cadastrado."
                ),
            )

    working_hour = ProfessionalWorkingHour(
        professional_id=professional_id,
        weekday=working_hour_data.weekday,
        start_time=working_hour_data.start_time.strftime("%H:%M"),
        end_time=working_hour_data.end_time.strftime("%H:%M"),
    )

    db.add(working_hour)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao salvar o horário de trabalho.",
        )

    db.refresh(working_hour)

    return working_hour


@router.put(
    "/{working_hour_id}",
    response_model=ProfessionalWorkingHourResponse,
)
def update_working_hour(
    professional_id: int,
    working_hour_id: int,
    working_hour_data: ProfessionalWorkingHourCreate,
    db: Session = Depends(get_db),
):
    working_hour = db.query(
        ProfessionalWorkingHour
    ).filter(
        ProfessionalWorkingHour.id == working_hour_id,
        ProfessionalWorkingHour.professional_id == professional_id,
    ).first()

    if not working_hour:
        raise HTTPException(
            status_code=404,
            detail="Horário de trabalho não encontrado.",
        )

    if working_hour_data.start_time >= working_hour_data.end_time:
        raise HTTPException(
            status_code=409,
            detail="O horário inicial deve ser anterior ao horário final.",
        )

    existing_working_hours = db.query(
        ProfessionalWorkingHour
    ).filter(
        ProfessionalWorkingHour.professional_id == professional_id,
        ProfessionalWorkingHour.weekday == working_hour_data.weekday,
        ProfessionalWorkingHour.id != working_hour_id,
    ).all()

    for existing in existing_working_hours:
        existing_start = datetime.strptime(
            existing.start_time,
            "%H:%M",
        ).time()

        existing_end = datetime.strptime(
            existing.end_time,
            "%H:%M",
        ).time()

        if (
            working_hour_data.start_time < existing_end
            and working_hour_data.end_time > existing_start
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "O novo horário se sobrepõe a um horário "
                    "já cadastrado."
                ),
            )

    working_hour.weekday = working_hour_data.weekday
    working_hour.start_time = working_hour_data.start_time.strftime("%H:%M")
    working_hour.end_time = working_hour_data.end_time.strftime("%H:%M")

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar o horário de trabalho.",
        )

    db.refresh(working_hour)

    return working_hour


@router.delete(
    "/{working_hour_id}",
    response_model=dict,
)
def delete_working_hour(
    professional_id: int,
    working_hour_id: int,
    db: Session = Depends(get_db),
):
    working_hour = db.query(
        ProfessionalWorkingHour
    ).filter(
        ProfessionalWorkingHour.id == working_hour_id,
        ProfessionalWorkingHour.professional_id == professional_id,
    ).first()

    if not working_hour:
        raise HTTPException(
            status_code=404,
            detail="Horário de trabalho não encontrado.",
        )

    db.delete(working_hour)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao excluir o horário de trabalho.",
        )

    return {
        "message": "Horário de trabalho excluído com sucesso."
    }
