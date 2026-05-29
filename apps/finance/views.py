"""Widoki (warstwa Controller) domeny finansowej.

Widoki sa cienkie: walidacje robi serializer (DTO), a operacje zapisu
deleguja do warstwy services. Odczyt korzysta z warstwy selectors.
"""

from django.http import FileResponse, Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import selectors, services
from .models import Notification, Report
from .serializers import (
    BudgetSerializer,
    CategorySerializer,
    NotificationSerializer,
    ReportSerializer,
    TransactionSerializer,
)
from .tasks import generate_report


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


class ReportViewSet(viewsets.ModelViewSet):
    """Zlecanie i pobieranie raportow (CSV/PDF/AI) generowanych asynchronicznie."""

    serializer_class = ReportSerializer
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        report = serializer.save(user=self.request.user)
        # Wrzucenie zadania do kolejki Redis -> przetwarza je worker Celery
        generate_report.delay(report.id)

    @action(detail=True, methods=["get"])
    def download(self, request: Request, pk: str | None = None) -> FileResponse:
        report = self.get_object()
        if not report.file:
            raise Http404("Plik nie jest jeszcze gotowy.")
        return FileResponse(report.file.open("rb"), as_attachment=True)


class NotificationViewSet(viewsets.ModelViewSet):
    """Powiadomienia uzytkownika (np. przekroczenie budzetu).

    Tworzone zdarzeniowo przez sygnaly - tu tylko odczyt i oznaczanie."""

    serializer_class = NotificationSerializer
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


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
