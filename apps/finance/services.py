"""Warstwa logiki biznesowej (Service).

Widoki pozostaja cienkie i deleguja operacje zapisu do tych funkcji.
"""

from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser

from .models import Budget, Category, Transaction


def _owner(user: AbstractBaseUser | None) -> AbstractBaseUser | None:
    return user if (user is not None and user.is_authenticated) else None


def create_transaction(*, user: AbstractBaseUser | None, **data) -> Transaction:
    """Tworzy transakcje przypisana do uzytkownika (jesli zalogowany)."""
    return Transaction.objects.create(user=_owner(user), **data)


def update_transaction(*, transaction: Transaction, **data) -> Transaction:
    """Aktualizuje wybrane pola transakcji."""
    for field, value in data.items():
        setattr(transaction, field, value)
    transaction.save()
    return transaction


def create_category(*, user: AbstractBaseUser | None, **data) -> Category:
    return Category.objects.create(user=_owner(user), **data)


def create_budget(*, user: AbstractBaseUser | None, **data) -> Budget:
    return Budget.objects.create(user=_owner(user), **data)
