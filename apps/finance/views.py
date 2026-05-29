"""Widoki (warstwa Controller) domeny finansowej.

Widoki sa cienkie: walidacje robi serializer (DTO), a operacje zapisu
deleguja do warstwy services. Odczyt korzysta z warstwy selectors.
"""
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import selectors, services
from .serializers import (
    BudgetSerializer,
    CategorySerializer,
    TransactionSerializer,
)


class TransactionViewSet(viewsets.ModelViewSet):
    """Pelny CRUD dla transakcji. Chroniony JWT, izolacja per uzytkownik."""

    serializer_class = TransactionSerializer

    def get_queryset(self):
        return selectors.transaction_list(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.instance = services.create_transaction(
            user=self.request.user, **serializer.validated_data
        )

    def perform_update(self, serializer) -> None:
        serializer.instance = services.update_transaction(
            transaction=serializer.instance, **serializer.validated_data
        )


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD kategorii (per uzytkownik)."""

    serializer_class = CategorySerializer

    def get_queryset(self):
        return selectors.category_list(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.instance = services.create_category(
            user=self.request.user, **serializer.validated_data
        )


class BudgetViewSet(viewsets.ModelViewSet):
    """CRUD budzetow miesiecznych (per uzytkownik)."""

    serializer_class = BudgetSerializer

    def get_queryset(self):
        return selectors.budget_list(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.instance = services.create_budget(
            user=self.request.user, **serializer.validated_data
        )


def _resolve_period(request: Request) -> tuple[int, int]:
    """Pobiera month/year z query params lub uzywa biezacego miesiaca."""
    month, year = selectors.current_month_year()
    month = int(request.query_params.get("month", month))
    year = int(request.query_params.get("year", year))
    return month, year


class SummaryStatsView(APIView):
    def get(self, request: Request) -> Response:
        month, year = _resolve_period(request)
        return Response(
            selectors.stats_summary(user=request.user, month=month, year=year)
        )


class ByCategoryStatsView(APIView):
    def get(self, request: Request) -> Response:
        month, year = _resolve_period(request)
        return Response(
            selectors.stats_by_category(user=request.user, month=month, year=year)
        )


class MonthlyStatsView(APIView):
    def get(self, request: Request) -> Response:
        _, year = _resolve_period(request)
        return Response(selectors.stats_monthly(user=request.user, year=year))
