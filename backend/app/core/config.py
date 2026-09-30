#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	database_url: str

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encondig="utf-8",
	)

settings = Settings()
