#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from datetime import date, time
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, field_serializer


class ServiceCreate(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	description: str = ""
	duration_minutes: int = Field(gt=0)
	price_cents: int = Field(ge=0)

	@field_validator("name")
	@classmethod
	def validate_name(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O nome do serviço não pode ficar vazio.")

		return value

	@field_validator("description")
	@classmethod
	def normalize_description(cls, value: str) -> str:
		return value.strip()


class ServiceUpdate(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	description: str = ""
	duration_minutes: int = Field(gt=0)
	price_cents: int = Field(ge=0)
	available: bool = True

	@field_validator("name")
	@classmethod
	def validate_name(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O nome do serviço não pode ficar vazio.")

		return value

	@field_validator("description")
	@classmethod
	def normalize_description(cls, value: str) -> str:
		return value.strip()


class ServiceResponse(BaseModel):
	id: int
	name: str
	description: str
	duration_minutes: int
	price_cents: int
	available: bool

	model_config = {"from_attributes": True}


class ServiceSimpleResponse(BaseModel):
	id: int
	name: str

	model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
	message: str


class ProfessionalCreate(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	email: EmailStr
	phone: str = Field(min_length=1, max_length=20)

	@field_validator("name")
	@classmethod
	def validate_name(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O nome do profissional não pode ficar vazio.")

		return value

	@field_validator("phone")
	@classmethod
	def validate_phone(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O telefone não pode ficar vazio.")

		return value


class ProfessionalUpdate(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	email: EmailStr
	phone: str = Field(min_length=1, max_length=20)
	available: bool = True

	@field_validator("name")
	@classmethod
	def validate_name(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O nome do profissional não pode ficar vazio.")

		return value

	@field_validator("phone")
	@classmethod
	def validate_phone(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O telefone não pode ficar vazio.")

		return value


class ProfessionalResponse(BaseModel):
	id: int
	name: str
	email: str
	phone: str
	available: bool

	model_config = {"from_attributes": True}


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

	@field_validator("client_name")
	@classmethod
	def validate_client_name(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O nome do cliente não pode ficar vazio.")

		return value

	@field_validator("client_phone")
	@classmethod
	def validate_client_phone(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O telefone do cliente não pode ficar vazio.")

		return value


class AppointmentUpdate(BaseModel):
	professional_id: int
	service_id: int
	client_name: str = Field(min_length=1, max_length=100)
	client_phone: str = Field(min_length=1, max_length=20)
	appointment_date: date
	appointment_time: time
	status: Literal[
		"scheduled",
		"confirmed",
		"completed",
		"cancelled",
	] = "scheduled"

	@field_validator("client_name")
	@classmethod
	def validate_client_name(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O nome do cliente não pode ficar vazio.")

		return value

	@field_validator("client_phone")
	@classmethod
	def validate_client_phone(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("O telefone do cliente não pode ficar vazio.")

		return value


class AppointmentResponse(BaseModel):
	id: int
	professional_id: int
	service_id: int
	client_name: str
	client_phone: str
	appointment_date: date
	appointment_time: time
	status: str
	professional: ProfessionalSimpleResponse
	service: ServiceSimpleResponse

	model_config = {"from_attributes": True}


class ProfessionalWorkingHourCreate(BaseModel):
	weekday: int = Field(ge=0, le=6)
	start_time: time
	end_time: time


class ProfessionalWorkingHourResponse(BaseModel):
	id: int
	professional_id: int
	weekday: int
	start_time: time
	end_time: time

	@field_serializer("start_time", "end_time")
	def serialize_time(self, value: time) -> str:
		return value.strftime("%H:%M")

	model_config = {"from_attributes": True}
