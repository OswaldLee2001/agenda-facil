#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from app.database import get_db
from app.models import Professional
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

@router.post("/", response_model=ProfessionalResponse)
def create_professional(
	professional_data: ProfessionalCreate,
	db: Session = Depends(get_db),
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

@router.put("/{professional_id}", response_model=ProfessionalResponse)
def update_professional(
	professional_id: int,
	professional_data: ProfessionalUpdate,
	db: Session = Depends(get_db),
):
	professional=(
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

@router.delete("/{professional_id}", response_model=MessageResponse)
def delete_professional(
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

	db.delete(professional)
	db.commit()

	return {
		"message": "Profissional excluído com sucesso."
	}


