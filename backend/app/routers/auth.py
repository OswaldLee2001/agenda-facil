#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.jwt import create_access_token
from app.core.security import verify_password
from app.database import get_db
from app.models import User
from app.schemas import UserLogin


router = APIRouter(
	prefix="/auth",
	tags=["auth"],
)

@router.post("/login")
def login(
	user: UserLogin,
	db: Session = Depends(get_db),
):

	existing_user = db.scalar(
		select(User).where(User.email == user.email)
	)

	if not existing_user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Email ou senha inválidos.",
	)

	if not verify_password(
		user.password,
		existing_user.hashed_password,
	):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Email ou senha inválidos.",
	)

	access_token = create_access_token(
		{
			"sub": str(existing_user.id),
			"email": existing_user.email,
		}
	)

	return {
		"access_token": access_token,
		"token_type": "bearer",
	}







