"""Zdarzenia domenowe (Django signals).

Po zapisaniu wydatku sprawdzamy, czy nie przekroczono budzetu na dany
miesiac/kategorie i - jesli tak - tworzymy powiadomienie dla uzytkownika.
"""
from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Budget, Notification, Transaction, TransactionType
from .selectors import budget_spent


@receiver(post_save, sender=Transaction)
def check_budget_on_transaction(sender, instance: Transaction, created, **kwargs):
    """Reaguje na nowy/zmieniony wydatek i ostrzega o przekroczeniu budzetu."""
    if instance.type != TransactionType.EXPENSE or instance.user_id is None:
        return

    budgets = Budget.objects.filter(
        user_id=instance.user_id,
        month=instance.date.month,
        year=instance.date.year,
    )
    for budget in budgets:
        # budzet kategorii musi pasowac do kategorii transakcji;
        # budzet laczny (bez kategorii) obejmuje wszystkie wydatki
        if budget.category_id and budget.category_id != instance.category_id:
            continue
        if budget_spent(budget) > budget.amount:
            scope = budget.category.name if budget.category else "laczny"
            message = (
                f"Przekroczono budzet {scope} na {budget.month:02d}/{budget.year} "
                f"(limit {budget.amount} PLN)."
            )
            # unikamy duplikatu tego samego ostrzezenia
            Notification.objects.get_or_create(
                user_id=instance.user_id,
                message=message,
                is_read=False,
            )
