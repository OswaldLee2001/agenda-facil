#!/usr/bin/env python3
#!-*-coding:utf-8-*-

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)

def test_health():
	response = client.get("/health")


	assert response.status_code == 200
	assert response.json() == {"status": "ok"}

def test_cors_allows_local_frontend():
	response = client.options(
		"/",
		headers={
			"Origin": "http://localhost:5173",
			"Access-Control-Request-Method": "GET",
		},
	)

	assert response.status_code == 200
	assert (
		response.headers.get("access-control-allow-origin")
		== "http://localhost:5173"
	)

def test_cors_rejects_unapproved_origin():
	response = client.options(
		"/",
		headers={
			"Origin": "https://example.com",
			"Access-Control-Request-Method": "GET",
		},
	)

	assert response.status_code == 400
	assert "access-control-allow-origin" not in response.headers
