"""Warstwa odczytu danych (≈ Repository).

Oddziela zapytania do bazy od widokow i logiki biznesowej.
"""
from __future__ import annotations

import datetime
from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import QuerySet, Sum

from .models import Budget, Category, Transaction, TransactionType


def transaction_list(*, user: AbstractBaseUser | None = None) -> QuerySet[Transaction]:
    """Zwraca transakcje. Jesli podano uzytkownika, ogranicza do jego danych."""
    qs = Transaction.objects.select_related("category").all()
    if user is not None and user.is_authenticated:
        qs = qs.filter(user=user)
    return qs


def category_list(*, user: AbstractBaseUser | None = None) -> QuerySet[Category]:
    qs = Category.objects.all()
    if user is not None and user.is_authenticated:
        qs = qs.filter(user=user)
    return qs


def budget_list(*, user: AbstractBaseUser | None = None) -> QuerySet[Budget]:
    qs = Budget.objects.select_related("category").all()
    if user is not None and user.is_authenticated:
        qs = qs.filter(user=user)
    return qs


def budget_spent(budget: Budget) -> Decimal:
    """Suma wydatkow objetych danym budzetem (miesiac/rok, opcjonalnie kategoria)."""
    qs = Transaction.objects.filter(
        user=budget.user,
        type=TransactionType.EXPENSE,
        date__month=budget.month,
        date__year=budget.year,
    )
    if budget.category_id:
        qs = qs.filter(category_id=budget.category_id)
    return qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")


def stats_summary(*, user: AbstractBaseUser, month: int, year: int) -> dict:
    """Przychody, wydatki i bilans dla danego miesiaca."""
    qs = Transaction.objects.filter(user=user, date__month=month, date__year=year)
    income = qs.filter(type=TransactionType.INCOME).aggregate(
        t=Sum("amount")
    )["t"] or Decimal("0")
    expense = qs.filter(type=TransactionType.EXPENSE).aggregate(
        t=Sum("amount")
    )["t"] or Decimal("0")
    return {
        "month": month,
        "year": year,
        "income": income,
        "expense": expense,
        "balance": income - expense,
    }


def stats_by_category(*, user: AbstractBaseUser, month: int, year: int) -> list[dict]:
    """Suma wydatkow per kategoria (dane pod wykres kolowy)."""
    qs = (
        Transaction.objects.filter(
            user=user,
            type=TransactionType.EXPENSE,
            date__month=month,
            date__year=year,
        )
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    return [
        {
            "category": row["category__name"] or "Bez kategorii",
            "color": row["category__color"] or "#9ca3af",
            "total": row["total"],
        }
        for row in qs
    ]


def stats_monthly(*, user: AbstractBaseUser, year: int) -> list[dict]:
    """Przychody i wydatki w rozbiciu na miesiace danego roku (trend)."""
    result = []
    for month in range(1, 13):
        summary = stats_summary(user=user, month=month, year=year)
        result.append(
            {
                "month": month,
                "income": summary["income"],
                "expense": summary["expense"],
            }
        )
    return result


def current_month_year() -> tuple[int, int]:
    today = datetime.date.today()
    return today.month, today.year
