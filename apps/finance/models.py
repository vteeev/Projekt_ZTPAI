"""Modele domeny finansowej."""
from __future__ import annotations

from django.conf import settings
from django.db import models


class TransactionType(models.TextChoices):
    INCOME = "INCOME", "Przychod"
    EXPENSE = "EXPENSE", "Wydatek"


class Category(models.Model):
    """Kategoria transakcji (np. Jedzenie, Wyplata)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=7,
        choices=TransactionType.choices,
        default=TransactionType.EXPENSE,
    )
    color = models.CharField(max_length=7, default="#3b82f6")  # hex do wykresow
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "type"],
                name="unique_category_per_user",
            )
        ]
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Transaction(models.Model):
    """Pojedyncza transakcja: przychod albo wydatek."""

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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="transactions",
        null=True,
        blank=True,
    )
    description = models.CharField(max_length=255, blank=True, default="")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.get_type_display()} {self.amount} ({self.date})"


class Budget(models.Model):
    """Budzet miesieczny - limit wydatkow na dany miesiac i opcjonalnie kategorie."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
        null=True,
        blank=True,
        help_text="Puste = budzet laczny na wszystkie kategorie.",
    )
    month = models.PositiveSmallIntegerField()  # 1-12
    year = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category", "month", "year"],
                name="unique_budget_per_period",
            )
        ]

    def __str__(self) -> str:
        scope = self.category.name if self.category else "Laczny"
        return f"Budzet {scope} {self.month:02d}/{self.year}: {self.amount}"


class Report(models.Model):
    """Asynchronicznie generowany raport (CSV/PDF) lub analiza AI wydatkow."""

    class ReportType(models.TextChoices):
        CSV = "CSV", "Eksport CSV"
        PDF = "PDF", "Raport PDF"
        AI = "AI", "Analiza AI"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Oczekuje"
        PROCESSING = "PROCESSING", "W trakcie"
        DONE = "DONE", "Gotowe"
        FAILED = "FAILED", "Blad"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=3, choices=ReportType.choices)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    month = models.PositiveSmallIntegerField(null=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    file = models.FileField(upload_to="reports/", null=True, blank=True)
    result = models.TextField(blank=True, default="")  # tekst analizy AI
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_type_display()} [{self.status}] #{self.pk}"


class Notification(models.Model):
    """Powiadomienie generowane zdarzeniowo (np. przekroczenie budzetu)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.message
