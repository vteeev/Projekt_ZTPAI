"""Testy CRUD transakcji, walidacji i izolacji danych."""
import pytest

from apps.finance.models import Transaction

pytestmark = pytest.mark.django_db


def test_create_transaction(auth_client, user):
    resp = auth_client.post(
        "/api/transactions/",
        {"type": "EXPENSE", "amount": "49.99", "date": "2026-05-01"},
        format="json",
    )
    assert resp.status_code == 201
    t = Transaction.objects.get(pk=resp.data["id"])
    assert t.user == user
    assert str(t.amount) == "49.99"


def test_negative_amount_rejected(auth_client):
    resp = auth_client.post(
        "/api/transactions/",
        {"type": "EXPENSE", "amount": "-5", "date": "2026-05-01"},
        format="json",
    )
    assert resp.status_code == 400
    # bledy opakowane w jednolity format
    assert "error" in resp.data
    assert "amount" in resp.data["error"]["detail"]


def test_invalid_type_rejected(auth_client):
    resp = auth_client.post(
        "/api/transactions/",
        {"type": "FOO", "amount": "5", "date": "2026-05-01"},
        format="json",
    )
    assert resp.status_code == 400


def test_update_transaction(auth_client, user):
    t = Transaction.objects.create(
        user=user, type="EXPENSE", amount="10", date="2026-05-01"
    )
    resp = auth_client.patch(
        f"/api/transactions/{t.id}/", {"amount": "20"}, format="json"
    )
    assert resp.status_code == 200
    t.refresh_from_db()
    assert str(t.amount) == "20.00"


def test_delete_transaction(auth_client, user):
    t = Transaction.objects.create(
        user=user, type="EXPENSE", amount="10", date="2026-05-01"
    )
    resp = auth_client.delete(f"/api/transactions/{t.id}/")
    assert resp.status_code == 204
    assert not Transaction.objects.filter(pk=t.id).exists()


def test_user_sees_only_own_transactions(auth_client, user, other_user):
    Transaction.objects.create(
        user=user, type="EXPENSE", amount="10", date="2026-05-01"
    )
    Transaction.objects.create(
        user=other_user, type="EXPENSE", amount="99", date="2026-05-01"
    )
    resp = auth_client.get("/api/transactions/")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
