#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import services, professionals, working_hours
from app.routers.appointments import router as appointments_router
from app.routers.users import router as users_router

app = FastAPI(
	debug=settings.debug,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		origin.strip()
		for origin in settings.cors_origins.split(",")
		if origin.strip()
	],

	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],

)

@app.get("/")
def read_root():
	return {"message": "Agenda Fácil API"}


@app.get("/health")
def health_check():
	return {"status": "ok"}


app.include_router(services.router)
app.include_router(professionals.router)
app.include_router(appointments_router)
app.include_router(working_hours.router)
app.include_router(users_router)
