#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import services, professionals
from app.routers.appointments import router as appointments_router

app = FastAPI(
	debug=settings.debug,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins.split(","),

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
