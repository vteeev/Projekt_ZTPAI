"""Warstwa logiki biznesowej (Service).

Widoki pozostaja cienkie i deleguja operacje zapisu do tych funkcji.
"""
from __future__ import annotations

import datetime
from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser

from .models import Transaction


def create_transaction(
    *,
    user: AbstractBaseUser | None,
    type: str,
    amount: Decimal,
    date: datetime.date,
    category: str = "",
    description: str = "",
) -> Transaction:
    """Tworzy transakcje przypisana do uzytkownika (jesli zalogowany)."""
    transaction = Transaction.objects.create(
        user=user if (user is not None and user.is_authenticated) else None,
        type=type,
        amount=amount,
        date=date,
        category=category,
        description=description,
    )
    return transaction


def update_transaction(*, transaction: Transaction, **data) -> Transaction:
    """Aktualizuje wybrane pola transakcji."""
    for field, value in data.items():
        setattr(transaction, field, value)
    transaction.save()
    return transaction
