#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy import create_engine

from alembic import context

from app.database import Base
from app import models
from app.core.config import settings

config = context.config

if config.config_file_name is not None:
	fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
	"""Executa migrações no modo offline"""
	
	url = config.get_main_option("sqlalchemy.url")

	context.configure(
		url=url,
		target_metadata=target_metadata,
		literal_binds=True,
		dialect_ops={"paramstyle": "named"},
	)

	with context.begin_transaction():
		context.run_migrations()

def run_migrations_online() -> None:
	"""Executa migrações no modo online"""
	
	connectable = create_engine(
		settings.database_url,
		poolclass=pool.NullPool,
	)

	with connectable.connect() as connection:
		context.configure(
			connection=connection,
			target_metadata=target_metadata,
		)

		with context.begin_transaction():
			context.run_migrations()

if context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()
