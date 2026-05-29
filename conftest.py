"""Wspolne fixtures dla testow pytest."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="SilneHaslo123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="bob", password="SilneHaslo123")


@pytest.fixture
def auth_client(api_client: APIClient, user) -> APIClient:
    """Klient uwierzytelniony jako 'user' (force_authenticate -> bez JWT w tescie)."""
    api_client.force_authenticate(user=user)
    return api_client
