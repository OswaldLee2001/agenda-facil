#!/usr/bin/env python3
#!-*-coding:utf-8-*-

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def make_settings(**overrides):
    values = {
        "database_url": "sqlite:///./test.db",
        "secret_key": "a" * 32,
    }

    values.update(overrides)
    return Settings(**values)

def test_default_security_settings():
    settings = make_settings()

    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30

def test_rejects_short_secret_key():
    with pytest.raises(ValidationError):
        make_settings(secret_key="curta")

def test_rejects_blank_secret_key():
    with pytest.raises(ValidationError):
        make_settings(secret_key=" " * 32)

def test_rejects_unsupported_algorithm():
    with pytest.raises(ValidationError):
        make_settings(algorithm="none")

def test_rejects_zero_token_expiration():
    with pytest.raises(ValidationError):
        make_settings(access_token_expire_minutes=0)

def test_accepts_valid_custom_expiration():
    settings = make_settings(access_token_expire_minutes=60)

    assert settings.access_token_expire_minutes == 60

def test_rejects_negative_token_expiration():
    with pytest.raises(ValidationError):
        make_settings(access_token_expire_minutes=-1)
