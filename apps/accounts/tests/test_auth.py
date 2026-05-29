"""Testy autoryzacji: rejestracja i JWT."""

import pytest

pytestmark = pytest.mark.django_db


def test_register_creates_user(api_client):
    resp = api_client.post(
        "/api/auth/register/",
        {"username": "newuser", "email": "n@ex.com", "password": "SilneHaslo123"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["username"] == "newuser"


def test_register_rejects_weak_password(api_client):
    resp = api_client.post(
        "/api/auth/register/",
        {"username": "u", "password": "123"},
        format="json",
    )
    assert resp.status_code == 400


def test_login_returns_tokens(api_client, user):
    resp = api_client.post(
        "/api/auth/login/",
        {"username": "alice", "password": "SilneHaslo123"},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data


def test_transactions_require_authentication(api_client):
    resp = api_client.get("/api/transactions/")
    assert resp.status_code == 401


def test_me_returns_current_user(auth_client):
    resp = auth_client.get("/api/auth/me/")
    assert resp.status_code == 200
    assert resp.data["username"] == "alice"
