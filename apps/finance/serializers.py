"""Serializery (DTO) domeny finansowej."""
from decimal import Decimal

from rest_framework import serializers

from .models import Budget, Category, Report, Transaction
from .selectors import budget_spent


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type", "color", "created_at"]
        read_only_fields = ["id", "created_at"]


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True, default=None
    )
    category_color = serializers.CharField(
        source="category.color", read_only=True, default=None
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "type",
            "amount",
            "category",
            "category_name",
            "category_color",
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

    def validate_category(self, category: Category | None) -> Category | None:
        """Kategoria musi nalezec do zalogowanego uzytkownika."""
        if category is None:
            return None
        request = self.context.get("request")
        if request and category.user_id != request.user.id:
            raise serializers.ValidationError("Nieprawidlowa kategoria.")
        return category


class BudgetSerializer(serializers.ModelSerializer):
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    usage_percent = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "month",
            "year",
            "amount",
            "spent",
            "remaining",
            "usage_percent",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_month(self, value: int) -> int:
        if not 1 <= value <= 12:
            raise serializers.ValidationError("Miesiac musi byc w zakresie 1-12.")
        return value

    def validate_category(self, category: Category | None) -> Category | None:
        if category is None:
            return None
        request = self.context.get("request")
        if request and category.user_id != request.user.id:
            raise serializers.ValidationError("Nieprawidlowa kategoria.")
        return category

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Kwota musi byc wieksza od zera.")
        return value

    def get_spent(self, obj: Budget) -> Decimal:
        return budget_spent(obj)

    def get_remaining(self, obj: Budget) -> Decimal:
        return obj.amount - budget_spent(obj)

    def get_usage_percent(self, obj: Budget) -> float:
        if obj.amount == 0:
            return 0.0
        return round(float(budget_spent(obj) / obj.amount) * 100, 1)


class ReportSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source="file", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "type",
            "status",
            "month",
            "year",
            "file_url",
            "result",
            "error",
            "created_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "file_url",
            "result",
            "error",
            "created_at",
            "completed_at",
        ]
