#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Service
from app.schemas import ServiceCreate, ServiceUpdate, ServiceResponse, MessageResponse

router = APIRouter(
    prefix="/services",
    tags=["services"],
)


@router.get("/", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()

    return services


@router.post("/", response_model=ServiceResponse)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
):
    service = Service(
        name=service_data.name,
        description=service_data.description,
        duration_minutes=service_data.duration_minutes,
        price_cents=service_data.price_cents,
    )

    db.add(service)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao salvar o serviço.",
        )

    db.refresh(service)

    return service

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado",
        )

    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado",
        )

    service.name = service_data.name
    service.description = service_data.description
    service.duration_minutes = service_data.duration_minutes
    service.price_cents = service_data.price_cents
    service.available = service_data.available

    db.commit()
    db.refresh(service)

    return service


@router.delete("/{service_id}", response_model=MessageResponse)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado",
        )

    db.delete(service)
    db.commit()

    return {
        "message": "Serviço excluído com sucesso."
    }

