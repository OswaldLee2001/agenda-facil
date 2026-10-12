#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import require_role
from app.models import Professional, ProfessionalWorkingHour, User
from app.schemas import (
    ProfessionalWorkingHourCreate,
    ProfessionalWorkingHourResponse,
)

router = APIRouter(
    prefix="/professionals/{professional_id}/working-hours",
    tags=["working-hours"],
)


def verify_professional_access(
    professional: Professional,
    current_user: User,
) -> None:
    """Permite que profissionais alterem somente os próprios horários."""
    if (
        current_user.role != "admin"
        and professional.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para realizar esta ação.",
        )


def get_professional_or_404(
    db: Session,
    professional_id: int,
) -> Professional:
    professional = (
        db.query(Professional)
        .filter(Professional.id == professional_id)
        .first()
    )

    if professional is None:
        raise HTTPException(
            status_code=404,
            detail="Profissional não encontrado.",
        )

    return professional


def validate_working_hour_interval(
    start_time,
    end_time,
) -> None:
    if start_time >= end_time:
        raise HTTPException(
            status_code=409,
            detail="O horário inicial deve ser anterior ao horário final.",
        )


def validate_no_overlap(
    db: Session,
    professional_id: int,
    weekday: int,
    start_time,
    end_time,
    exclude_working_hour_id: int | None = None,
) -> None:
    query = db.query(ProfessionalWorkingHour).filter(
        ProfessionalWorkingHour.professional_id == professional_id,
        ProfessionalWorkingHour.weekday == weekday,
    )

    if exclude_working_hour_id is not None:
        query = query.filter(
            ProfessionalWorkingHour.id != exclude_working_hour_id
        )

    existing_working_hours = query.all()

    for existing in existing_working_hours:
        if (
            start_time < existing.end_time
            and end_time > existing.start_time
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "O novo horário se sobrepõe a um horário "
                    "já cadastrado."
                ),
            )


@router.get(
    "/",
    response_model=list[ProfessionalWorkingHourResponse],
)
def list_working_hours(
    professional_id: int,
    db: Session = Depends(get_db),
):
    get_professional_or_404(db, professional_id)

    return (
        db.query(ProfessionalWorkingHour)
        .filter(
            ProfessionalWorkingHour.professional_id == professional_id
        )
        .order_by(
            ProfessionalWorkingHour.weekday,
            ProfessionalWorkingHour.start_time,
        )
        .all()
    )


@router.post(
    "/",
    response_model=ProfessionalWorkingHourResponse,
)
def create_working_hour(
    professional_id: int,
    working_hour_data: ProfessionalWorkingHourCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "professional")),
):
    professional = get_professional_or_404(db, professional_id)

    verify_professional_access(professional, current_user)

    validate_working_hour_interval(
        working_hour_data.start_time,
        working_hour_data.end_time,
    )

    validate_no_overlap(
        db=db,
        professional_id=professional_id,
        weekday=working_hour_data.weekday,
        start_time=working_hour_data.start_time,
        end_time=working_hour_data.end_time,
    )

    working_hour = ProfessionalWorkingHour(
        professional_id=professional_id,
        weekday=working_hour_data.weekday,
        start_time=working_hour_data.start_time,
        end_time=working_hour_data.end_time,
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
    current_user: User = Depends(require_role("admin", "professional")),
):
    professional = get_professional_or_404(db, professional_id)

    verify_professional_access(professional, current_user)

    working_hour = (
        db.query(ProfessionalWorkingHour)
        .filter(
            ProfessionalWorkingHour.id == working_hour_id,
            ProfessionalWorkingHour.professional_id == professional_id,
        )
        .first()
    )

    if working_hour is None:
        raise HTTPException(
            status_code=404,
            detail="Horário de trabalho não encontrado.",
        )

    validate_working_hour_interval(
        working_hour_data.start_time,
        working_hour_data.end_time,
    )

    validate_no_overlap(
        db=db,
        professional_id=professional_id,
        weekday=working_hour_data.weekday,
        start_time=working_hour_data.start_time,
        end_time=working_hour_data.end_time,
        exclude_working_hour_id=working_hour_id,
    )

    working_hour.weekday = working_hour_data.weekday
    working_hour.start_time = working_hour_data.start_time
    working_hour.end_time = working_hour_data.end_time

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
    current_user: User = Depends(require_role("admin", "professional")),
):
    professional = get_professional_or_404(db, professional_id)

    verify_professional_access(professional, current_user)

    working_hour = (
        db.query(ProfessionalWorkingHour)
        .filter(
            ProfessionalWorkingHour.id == working_hour_id,
            ProfessionalWorkingHour.professional_id == professional_id,
        )
        .first()
    )

    if working_hour is None:
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
