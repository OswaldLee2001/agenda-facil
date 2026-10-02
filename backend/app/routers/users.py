#!/usr/bin/env python3
#!-*-coding:utf-8-*-
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
router = APIRouter(
	prefix="/users",
	tags=["users"],
)
@router.post(
	"/",
	response_model=UserResponse,
	status_code=status.HTTP_201_CREATED,
)
def create_user(
	user: UserCreate,
	db: Session = Depends(get_db),
):
	existing_user = db.scalar(
		select(User).where(User.email == user.email)
	)
	if existing_user:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Email já cadastrado.",
		)
	new_user = User(
		name=user.name,
		email=user.email,
		hashed_password=hash_password(user.password),
	)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	return new_user
