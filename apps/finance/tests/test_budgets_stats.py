"""Testy budzetow, statystyk i warstwy selectors."""
import pytest

from apps.finance import selectors
from apps.finance.models import Budget, Category, Transaction

pytestmark = pytest.mark.django_db


@pytest.fixture
def food(user):
    return Category.objects.create(user=user, name="Jedzenie", type="EXPENSE")


def test_budget_spent_and_usage(auth_client, user, food):
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="150", category=food, date="2026-05-10"
    )
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="80", category=food, date="2026-05-15"
    )
    budget = Budget.objects.create(
        user=user, category=food, month=5, year=2026, amount="200"
    )
    resp = auth_client.get(f"/api/budgets/{budget.id}/")
    assert resp.status_code == 200
    assert resp.data["spent"] == 230.0
    assert resp.data["remaining"] == -30.0
    assert resp.data["usage_percent"] == 115.0


def test_stats_summary(user, food):
    Transaction.objects.create(
        user=user, type="INCOME", amount="5000", date="2026-05-01"
    )
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="250", category=food, date="2026-05-10"
    )
    summary = selectors.stats_summary(user=user, month=5, year=2026)
    assert summary["income"] == 5000
    assert summary["expense"] == 250
    assert summary["balance"] == 4750


def test_stats_by_category(user, food):
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="100", category=food, date="2026-05-10"
    )
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="40", date="2026-05-11"
    )
    rows = selectors.stats_by_category(user=user, month=5, year=2026)
    assert {"category": "Jedzenie", "color": food.color, "total": 100} in [
        {"category": r["category"], "color": r["color"], "total": r["total"]}
        for r in rows
    ]
    # transakcja bez kategorii trafia do "Bez kategorii"
    assert any(r["category"] == "Bez kategorii" for r in rows)


def test_cannot_use_foreign_category(auth_client, other_user):
    foreign = Category.objects.create(
        user=other_user, name="Cudza", type="EXPENSE"
    )
    resp = auth_client.post(
        "/api/transactions/",
        {
            "type": "EXPENSE",
            "amount": "10",
            "category": foreign.id,
            "date": "2026-05-01",
        },
        format="json",
    )
    assert resp.status_code == 400
