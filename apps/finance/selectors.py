"""Warstwa odczytu danych (≈ Repository).

Oddziela zapytania do bazy od widokow i logiki biznesowej.
"""
from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import QuerySet

from .models import Transaction


def transaction_list(*, user: AbstractBaseUser | None = None) -> QuerySet[Transaction]:
    """Zwraca transakcje. Jesli podano uzytkownika, ogranicza do jego danych."""
    qs = Transaction.objects.all()
    if user is not None and user.is_authenticated:
        qs = qs.filter(user=user)
    return qs
