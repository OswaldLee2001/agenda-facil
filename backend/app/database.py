#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(
	settings.database_url,
	pool_pre_ping=True,
	pool_size=5,
	max_overflow=5,

)

SessionLocal = sessionmaker(
	bind=engine,
	autoflush=False,
	autocommit=False,
)



class Base(DeclarativeBase):
	pass

def get_db():
	db = SessionLocal()

	try:
		yield db
	except SQLAlchemyError:
		db.rollback()
		raise
	finally:
		db.close()
