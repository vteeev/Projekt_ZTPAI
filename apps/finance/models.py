"""Modele domeny finansowej."""
from __future__ import annotations

from django.conf import settings
from django.db import models


class TransactionType(models.TextChoices):
    INCOME = "INCOME", "Przychod"
    EXPENSE = "EXPENSE", "Wydatek"


class Transaction(models.Model):
    """Pojedyncza transakcja: przychod albo wydatek."""

    # user jest na razie opcjonalny; izolacja per-user dochodzi w Etapie 4 (JWT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=7,
        choices=TransactionType.choices,
        default=TransactionType.EXPENSE,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # category bedzie ForeignKey do modelu Category w Etapie 5
    category = models.CharField(max_length=100, blank=True, default="")
    description = models.CharField(max_length=255, blank=True, default="")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.get_type_display()} {self.amount} ({self.date})"
