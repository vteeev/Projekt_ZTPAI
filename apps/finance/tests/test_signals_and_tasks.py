"""Testy zdarzen (signals) i zadan raportow."""
import pytest

from apps.finance.models import Budget, Category, Notification, Report, Transaction
from apps.finance.tasks import generate_report

pytestmark = pytest.mark.django_db


@pytest.fixture
def food(user):
    return Category.objects.create(user=user, name="Jedzenie", type="EXPENSE")


def test_signal_creates_notification_on_budget_exceed(user, food):
    Budget.objects.create(user=user, category=food, month=5, year=2026, amount="100")
    # wydatek 120 > limit 100 -> sygnal powinien utworzyc powiadomienie
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="120", category=food, date="2026-05-10"
    )
    assert Notification.objects.filter(user=user).count() == 1


def test_signal_no_notification_within_budget(user, food):
    Budget.objects.create(user=user, category=food, month=5, year=2026, amount="100")
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="50", category=food, date="2026-05-10"
    )
    assert Notification.objects.filter(user=user).count() == 0


def test_generate_csv_report(user, food):
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="10", category=food, date="2026-05-10"
    )
    report = Report.objects.create(
        user=user, type=Report.ReportType.CSV, month=5, year=2026
    )
    generate_report(report.id)
    report.refresh_from_db()
    assert report.status == Report.Status.DONE
    assert report.file.name.endswith(".csv")


def test_generate_ai_report_heuristic(user, food):
    Transaction.objects.create(
        user=user, type="INCOME", amount="1000", date="2026-05-01"
    )
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="200", category=food, date="2026-05-10"
    )
    report = Report.objects.create(
        user=user, type=Report.ReportType.AI, month=5, year=2026
    )
    generate_report(report.id)
    report.refresh_from_db()
    assert report.status == Report.Status.DONE
    assert "Analiza za" in report.result
