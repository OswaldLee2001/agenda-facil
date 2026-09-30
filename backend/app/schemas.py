#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from datetime import date, time

from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	description: str = ""
	duration_minutes: int = Field(gt=0)
	price_cents: int = Field(ge=0)

class ServiceUpdate(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	description: str = ""
	duration_minutes: int = Field(gt=0)
	price_cents: int = Field(ge=0)
	available: bool = True

class ServiceResponse(BaseModel):
	id: int
	name: str	
	description: str
	duration_minutes: int
	price_cents: int
	available: bool

class ServiceSimpleResponse(BaseModel):
	id: int
	name: str

	model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
	message: str

class ProfessionalCreate(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	email: str = Field(min_length=1, max_length=150)
	phone: str = Field(min_length=1, max_length=20)

class ProfessionalUpdate(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	email: str = Field(min_length=1, max_length=150)
	phone: str = Field(min_length=1, max_length=20)
	available: bool = True
	

class ProfessionalResponse(BaseModel):
	id: int
	name: str
	email: str
	phone: str
	available: bool

class ProfessionalSimpleResponse(BaseModel):
	id: int
	name: str	
	
	model_config = {"from_attributes": True}

class AppointmentCreate(BaseModel):
	professional_id: int
	service_id: int
	client_name: str = Field(min_length=1, max_length=100)
	client_phone: str = Field(min_length=1, max_length=20)
	appointment_date: date 
	appointment_time: time 

class AppointmentUpdate(BaseModel):
	professional_id: int
	service_id: int
	client_name: str = Field(min_length=1, max_length=100)	
	client_phone: str = Field(min_length=1, max_length=20)
	appointment_date: date 
	appointment_time: time
	status: str = "scheduled"

class AppointmentResponse(BaseModel):
	id: int
	professional_id: int
	service_id: int
	client_name: str
	client_phone: str
	appointment_date: str
	appointment_time: str
	status: str
	professional: ProfessionalSimpleResponse
	service: ServiceSimpleResponse
	

