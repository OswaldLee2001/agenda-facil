#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from datetime import date, time


from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class Service(Base):
	__tablename__ = "services"

	id: Mapped[int] = mapped_column(
		Integer, 
		primary_key=True,
		index=True,
	)

	name: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
	)

	description: Mapped[str] = mapped_column(
		Text,
		default="",
	)

	duration_minutes: Mapped[int] = mapped_column(
		Integer,
		nullable=False,
	)

	price_cents: Mapped[int] = mapped_column(
		Integer,
		nullable=False,
	)

	available: Mapped[bool] = mapped_column(
		Boolean,
		default=True,
	)

	appointments: Mapped[list["Appointments"]] = relationship(
		back_populates="service"
	)


class Professional(Base):
	__tablename__ = "professionals"

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
		index=True,
	)

	name: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
	)

	email: Mapped[str] = mapped_column(
		String(150),
		nullable=False,
		unique=True,
	)

	phone: Mapped[str] = mapped_column(
		String(20),
		nullable=False,
	)

	available: Mapped[bool] = mapped_column(
		Boolean,
		default=True,
	)

	appointments: Mapped[list["Appointments"]] = relationship(
		back_populates="professional"
	)

	working_hours: Mapped[list["ProfessionalWorkingHour"]] = relationship(
		back_populates="professional"
	)

class Appointments(Base):
	__tablename__ = "Appointments"

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
		index=True,
	)
	
	professional_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("professionals.id"),
		nullable=False,
	)

	service_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("services.id"),
		nullable=False,
	)

	client_name: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
	)

	client_phone: Mapped[str] = mapped_column(
		String(20),
		nullable=False,
	)

	appointment_date: Mapped[date] = mapped_column(
		Date(),
		nullable=False,
	)

	appointment_time: Mapped[time] = mapped_column(
		Time(),
		nullable=False,
	)

	status: Mapped[str] = mapped_column(
		String(20),
		default="scheduled",
		nullable=False,
	)
	
	professional: Mapped["Professional"] = relationship(
		back_populates="appointments"
	)

	service: Mapped["Service"] = relationship(
		back_populates="appointments"
	)

class ProfessionalWorkingHour(Base):
	__tablename__ = "professional_working_hours"

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
		index=True,
	)


	professional_id: Mapped[int] = mapped_column(
		Integer, 
		ForeignKey("professionals.id"),
		nullable=False,
	)

	weekday: Mapped[int] = mapped_column(
		Integer,
		nullable=False,
	)

	start_time: Mapped[time] = mapped_column(
		Time(),
		nullable=False,
	)

	end_time: Mapped[time] = mapped_column(
		Time(),
		nullable=False,
	)

	professional: Mapped["Professional"] = relationship(
		back_populates="working_hours"
	)
