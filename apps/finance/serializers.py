"""Serializery (DTO) domeny finansowej."""
from decimal import Decimal

from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "type",
            "amount",
            "category",
            "description",
            "date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Kwota musi byc wieksza od zera.")
        return value

    def validate_description(self, value: str) -> str:
        return value.strip()
